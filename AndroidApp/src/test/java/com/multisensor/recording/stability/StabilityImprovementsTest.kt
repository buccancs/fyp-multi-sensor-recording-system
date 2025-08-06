package com.multisensor.recording.stability

import com.multisensor.recording.recording.RecordingState
import com.multisensor.recording.recording.RecordingStateManager
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/**
 * Tests for stability and reliability improvements.
 * Validates thread-safety, error handling, and resource management.
 */
@OptIn(ExperimentalCoroutinesApi::class)
class StabilityImprovementsTest {

    @Mock
    private lateinit var logger: Logger

    private lateinit var recordingStateManager: RecordingStateManager
    private lateinit var stabilityCoordinator: SimpleStabilityCoordinator
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        Dispatchers.setMain(testDispatcher)
        recordingStateManager = RecordingStateManager(logger)
        stabilityCoordinator = SimpleStabilityCoordinator(recordingStateManager, logger)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `test recording state manager prevents overlapping operations`() = runTest {
        // First operation should succeed
        val operation1 = async {
            recordingStateManager.transitionToState(RecordingState.STARTING) {
                delay(100) // Simulate some work
                Result.success(Unit)
            }
        }

        // Second operation should fail due to overlap
        val operation2 = async {
            delay(50) // Start after operation1 but before it completes
            recordingStateManager.transitionToState(RecordingState.RECORDING) {
                Result.success(Unit)
            }
        }

        val result1 = operation1.await()
        val result2 = operation2.await()

        assertTrue(result1.isSuccess, "First operation should succeed")
        assertTrue(result2.isFailure, "Second operation should fail due to overlap")
        
        // Verify error logging
        verify(logger, atLeastOnce()).error(any(), any<String>())
    }

    @Test
    fun `test resource registration and cleanup`() = runTest {
        val resourceId = "test_camera"
        
        // Register resource
        recordingStateManager.registerResource(resourceId)
        
        val activeResources = recordingStateManager.getActiveResources()
        assertTrue(activeResources.contains(resourceId), "Resource should be registered")
        
        // Unregister resource
        recordingStateManager.unregisterResource(resourceId)
        
        val activeResourcesAfter = recordingStateManager.getActiveResources()
        assertFalse(activeResourcesAfter.contains(resourceId), "Resource should be unregistered")
    }

    @Test
    fun `test force cleanup functionality`() = runTest {
        val resourceId1 = "camera_device"
        val resourceId2 = "media_recorder"
        
        // Register multiple resources
        recordingStateManager.registerResource(resourceId1)
        recordingStateManager.registerResource(resourceId2)
        
        // Start a mock operation
        recordingStateManager.transitionToState(RecordingState.RECORDING) {
            Result.success(Unit)
        }
        
        // Force cleanup
        recordingStateManager.forceCleanup()
        
        // Verify all resources are cleared
        val activeResources = recordingStateManager.getActiveResources()
        assertTrue(activeResources.isEmpty(), "All resources should be cleared after force cleanup")
        
        // Verify state is reset to idle
        assertEquals(RecordingState.IDLE, recordingStateManager.recordingState.value)
    }

    @Test
    fun `test operation timeout handling`() = runTest {
        val result = recordingStateManager.transitionToState(RecordingState.STARTING) {
            delay(35000) // Exceed the 30-second timeout
            Result.success(Unit)
        }

        assertTrue(result.isFailure, "Operation should fail due to timeout")
        
        // Verify timeout error is logged
        verify(logger, atLeastOnce()).error(contains("timeout"), any<String>())
    }

    @Test
    fun `test invalid state transitions are blocked`() = runTest {
        // Try to transition from IDLE to STOPPING (invalid)
        val result = recordingStateManager.transitionToState(RecordingState.STOPPING) {
            Result.success(Unit)
        }

        assertTrue(result.isFailure, "Invalid state transition should fail")
        
        // Verify error is logged
        verify(logger, atLeastOnce()).error(contains("Invalid state transition"), any<String>())
    }

    @Test
    fun `test valid state transition sequence`() = runTest {
        // Valid sequence: IDLE -> STARTING -> RECORDING -> STOPPING -> IDLE
        
        val result1 = recordingStateManager.transitionToState(RecordingState.STARTING) {
            Result.success(Unit)
        }
        assertTrue(result1.isSuccess, "IDLE to STARTING should succeed")
        
        val result2 = recordingStateManager.transitionToState(RecordingState.RECORDING) {
            Result.success(Unit)
        }
        assertTrue(result2.isSuccess, "STARTING to RECORDING should succeed")
        
        val result3 = recordingStateManager.transitionToState(RecordingState.STOPPING) {
            Result.success(Unit)
        }
        assertTrue(result3.isSuccess, "RECORDING to STOPPING should succeed")
        
        val result4 = recordingStateManager.transitionToState(RecordingState.IDLE) {
            Result.success(Unit)
        }
        assertTrue(result4.isSuccess, "STOPPING to IDLE should succeed")
    }

    @Test
    fun `test system stability when operation fails`() = runTest {
        val result = recordingStateManager.transitionToState(RecordingState.STARTING) {
            Result.failure(Exception("Simulated failure"))
        }

        assertTrue(result.isFailure, "Failed operation should return failure")
        
        // State should revert to safe state
        val currentState = recordingStateManager.recordingState.value
        assertTrue(currentState == RecordingState.IDLE || currentState == RecordingState.ERROR, 
            "State should revert to safe state after failure")
    }

    @Test
    fun `test system stability assessment`() = runTest {
        // This test would verify that the system correctly assesses stability
        // based on various factors. For now, it's a placeholder for future implementation.
        assertTrue(recordingStateManager.isSystemStable(), "System should start in stable state")
    }

    @Test
    fun `test error state management`() = runTest {
        // Trigger an error state
        recordingStateManager.transitionToState(RecordingState.STARTING) {
            Result.failure(Exception("Test error"))
        }

        // Check that error is recorded
        val lastError = recordingStateManager.lastError.value
        assertTrue(lastError != null, "Error should be recorded")

        // Clear error
        recordingStateManager.clearError()
        
        val clearedError = recordingStateManager.lastError.value
        assertTrue(clearedError == null, "Error should be cleared")
    }

    @Test
    fun `test stability coordinator system ready check`() = runTest {
        // System should start as ready
        assertTrue(stabilityCoordinator.isSystemReady(), "System should start ready")
        
        // Status should be READY
        assertEquals("READY", stabilityCoordinator.getSystemStatus())
    }

    @Test
    fun `test stability coordinator cleanup`() = runTest {
        // Register some resources
        recordingStateManager.registerResource("test_resource_1")
        recordingStateManager.registerResource("test_resource_2")
        
        // Perform cleanup
        stabilityCoordinator.performCleanup()
        
        // Resources should be cleared
        val activeResources = recordingStateManager.getActiveResources()
        assertTrue(activeResources.isEmpty(), "Resources should be cleared after cleanup")
    }
}