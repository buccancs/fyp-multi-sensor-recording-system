package com.multisensor.recording.stability

import com.multisensor.recording.recording.RecordingStateManager
import com.multisensor.recording.util.Logger
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Simple stability coordinator for basic system health monitoring.
 */
@Singleton
class SimpleStabilityCoordinator @Inject constructor(
    private val recordingStateManager: RecordingStateManager,
    private val logger: Logger
) {
    
    companion object {
        private const val TAG = "SimpleStabilityCoordinator"
    }
    
    /**
     * Checks if the system is ready for recording operations.
     */
    fun isSystemReady(): Boolean {
        return recordingStateManager.isSystemStable()
    }
    
    /**
     * Performs basic cleanup operations.
     */
    suspend fun performCleanup() {
        logger.info("$TAG: Performing system cleanup")
        recordingStateManager.forceCleanup()
    }
    
    /**
     * Gets basic system status.
     */
    fun getSystemStatus(): String {
        return if (isSystemReady()) "READY" else "NOT_READY"
    }
}