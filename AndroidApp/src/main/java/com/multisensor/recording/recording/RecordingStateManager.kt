package com.multisensor.recording.recording

import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.atomic.AtomicReference
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Centralized recording state management to prevent race conditions and overlapping operations.
 * Ensures thread-safety across all recording operations and provides coordinated state transitions.
 */
@Singleton
class RecordingStateManager @Inject constructor(
    private val logger: Logger
) {
    private val stateMutex = Mutex()
    private val operationTimeout = 30_000L // 30 seconds timeout for operations
    
    private val _recordingState = MutableStateFlow(RecordingState.IDLE)
    val recordingState: StateFlow<RecordingState> = _recordingState.asStateFlow()
    
    private val _lastError = MutableStateFlow<RecordingError?>(null)
    val lastError: StateFlow<RecordingError?> = _lastError.asStateFlow()
    
    private val currentOperation = AtomicReference<Job?>(null)
    private val activeResources = mutableSetOf<String>()
    
    companion object {
        private const val TAG = "RecordingStateManager"
    }
    
    /**
     * Attempts to transition to a new recording state with thread-safety guarantees.
     * Returns true if transition was successful, false if another operation is in progress.
     */
    suspend fun transitionToState(
        targetState: RecordingState,
        operation: suspend () -> Result<Unit>
    ): Result<Unit> = withContext(Dispatchers.IO) {
        stateMutex.withLock {
            val currentState = _recordingState.value
            
            // Check if transition is allowed
            if (!isTransitionAllowed(currentState, targetState)) {
                val error = RecordingError(
                    type = ErrorType.INVALID_STATE_TRANSITION,
                    message = "Cannot transition from $currentState to $targetState",
                    timestamp = System.currentTimeMillis()
                )
                _lastError.value = error
                logger.error("$TAG: Invalid state transition from $currentState to $targetState")
                return@withContext Result.failure(IllegalStateException(error.message))
            }
            
            // Check if another operation is in progress
            val existingOperation = currentOperation.get()
            if (existingOperation?.isActive == true) {
                val error = RecordingError(
                    type = ErrorType.OPERATION_IN_PROGRESS,
                    message = "Another recording operation is already in progress",
                    timestamp = System.currentTimeMillis()
                )
                _lastError.value = error
                logger.warning("$TAG: Operation blocked - another operation in progress")
                return@withContext Result.failure(IllegalStateException(error.message))
            }
            
            // Update state and execute operation with timeout
            _recordingState.value = targetState
            logger.info("$TAG: State transition: $currentState -> $targetState")
            
            try {
                val operationJob = async {
                    operation()
                }
                currentOperation.set(operationJob)
                
                val result = withTimeout(operationTimeout) {
                    operationJob.await()
                }
                
                result.onFailure { error ->
                    val recordingError = RecordingError(
                        type = ErrorType.OPERATION_FAILED,
                        message = "Operation failed: ${error.message}",
                        cause = error,
                        timestamp = System.currentTimeMillis()
                    )
                    _lastError.value = recordingError
                    logger.error("$TAG: Operation failed in state $targetState", error)
                    
                    // Revert to safe state on failure
                    _recordingState.value = getSafeStateForFailure(targetState)
                }
                
                result
                
            } catch (e: TimeoutCancellationException) {
                val error = RecordingError(
                    type = ErrorType.OPERATION_TIMEOUT,
                    message = "Operation timed out after ${operationTimeout}ms",
                    cause = e,
                    timestamp = System.currentTimeMillis()
                )
                _lastError.value = error
                logger.error("$TAG: Operation timeout in state $targetState")
                
                // Cancel the operation and revert state
                currentOperation.get()?.cancel()
                _recordingState.value = getSafeStateForFailure(targetState)
                
                Result.failure(e)
            } finally {
                currentOperation.set(null)
            }
        }
    }
    
    /**
     * Registers a resource as active to track for cleanup.
     */
    suspend fun registerResource(resourceId: String) {
        stateMutex.withLock {
            activeResources.add(resourceId)
            logger.debug("$TAG: Registered resource: $resourceId")
        }
    }
    
    /**
     * Unregisters a resource, indicating it has been properly cleaned up.
     */
    suspend fun unregisterResource(resourceId: String) {
        stateMutex.withLock {
            activeResources.remove(resourceId)
            logger.debug("$TAG: Unregistered resource: $resourceId")
        }
    }
    
    /**
     * Gets list of active resources that may need cleanup.
     */
    suspend fun getActiveResources(): Set<String> {
        return stateMutex.withLock {
            activeResources.toSet()
        }
    }
    
    /**
     * Forces cleanup of all active resources and resets to idle state.
     * Should be used in emergency shutdown scenarios.
     */
    suspend fun forceCleanup() {
        stateMutex.withLock {
            logger.warning("$TAG: Force cleanup initiated. Active resources: ${activeResources.size}")
            
            // Cancel any ongoing operation
            currentOperation.get()?.cancel()
            currentOperation.set(null)
            
            // Clear resources (actual cleanup should be handled by resource owners)
            val resourcesCleared = activeResources.size
            activeResources.clear()
            
            // Reset to idle state
            _recordingState.value = RecordingState.IDLE
            
            logger.info("$TAG: Force cleanup completed. Cleared $resourcesCleared resources.")
        }
    }
    
    /**
     * Checks if the system is in a stable state for new operations.
     */
    fun isSystemStable(): Boolean {
        return _recordingState.value != RecordingState.ERROR && 
               currentOperation.get()?.isActive != true
    }
    
    /**
     * Clears the last error state.
     */
    fun clearError() {
        _lastError.value = null
        logger.debug("$TAG: Error state cleared")
    }
    
    private fun isTransitionAllowed(from: RecordingState, to: RecordingState): Boolean {
        return when (from) {
            RecordingState.IDLE -> to != RecordingState.STOPPING
            RecordingState.STARTING -> to == RecordingState.RECORDING || to == RecordingState.ERROR || to == RecordingState.IDLE
            RecordingState.RECORDING -> to == RecordingState.STOPPING || to == RecordingState.ERROR
            RecordingState.STOPPING -> to == RecordingState.IDLE || to == RecordingState.ERROR
            RecordingState.ERROR -> to == RecordingState.IDLE || to == RecordingState.STOPPING
        }
    }
    
    private fun getSafeStateForFailure(fromState: RecordingState): RecordingState {
        return when (fromState) {
            RecordingState.STARTING -> RecordingState.IDLE
            RecordingState.RECORDING -> RecordingState.ERROR
            RecordingState.STOPPING -> RecordingState.IDLE
            else -> RecordingState.ERROR
        }
    }
}

/**
 * Represents the current state of the recording system.
 */
enum class RecordingState {
    IDLE,       // No recording in progress, ready to start
    STARTING,   // Recording is being initialized
    RECORDING,  // Recording is active
    STOPPING,   // Recording is being stopped and cleaned up
    ERROR       // System is in error state and needs recovery
}

/**
 * Represents an error that occurred during recording operations.
 */
data class RecordingError(
    val type: ErrorType,
    val message: String,
    val cause: Throwable? = null,
    val timestamp: Long
)

/**
 * Types of errors that can occur during recording operations.
 */
enum class ErrorType {
    INVALID_STATE_TRANSITION,   // Attempted invalid state change
    OPERATION_IN_PROGRESS,      // Another operation is already running
    OPERATION_FAILED,           // The operation failed to complete
    OPERATION_TIMEOUT,          // Operation exceeded timeout
    RESOURCE_UNAVAILABLE,       // Required resource is not available
    INSUFFICIENT_STORAGE,       // Not enough storage space
    INSUFFICIENT_MEMORY,        // Not enough memory available
    SENSOR_DISCONNECTED,        // Sensor became unavailable
    NETWORK_FAILED              // Network operation failed
}