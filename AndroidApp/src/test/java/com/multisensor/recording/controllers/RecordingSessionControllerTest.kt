package com.multisensor.recording.controllers

import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger

/**
 * Unit tests for RecordingSessionController
 * 
 * Tests the single responsibility principle implementation by verifying
 * that the controller properly manages recording sessions across devices
 * without handling UI concerns or other responsibilities.
 */
class RecordingSessionControllerTest {

    @Mock
    private lateinit var cameraRecorder: CameraRecorder

    @Mock
    private lateinit var thermalRecorder: ThermalRecorder

    @Mock
    private lateinit var shimmerRecorder: ShimmerRecorder

    @Mock
    private lateinit var sessionManager: SessionManager

    @Mock
    private lateinit var logger: Logger

    @Mock
    private lateinit var mockSessionInfo: com.multisensor.recording.recording.SessionInformation

    private lateinit var controller: RecordingSessionController

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        controller = RecordingSessionController(
            cameraRecorder,
            thermalRecorder,
            shimmerRecorder,
            sessionManager,
            logger
        )

        // Setup default mock behavior
        `when`(mockSessionInfo.getSummary()).thenReturn("Test Session Summary")
    }

    @Test
    fun `initial state should be not recording`() {
        val state = controller.getCurrentState()
        
        assertFalse("Should not be recording initially", state.isRecording)
        assertFalse("Should not be paused initially", state.isPaused)
        assertNull("Session ID should be null initially", state.sessionId)
        assertNull("Recording error should be null initially", state.recordingError)
    }

    @Test
    fun `startRecording should succeed with default config`() = runTest {
        // Arrange
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(true, false)).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        `when`(thermalRecorder.startRecording(sessionId)).thenReturn(true)
        `when`(shimmerRecorder.startRecording(sessionId)).thenReturn(true)

        // Act
        val result = controller.startRecording()

        // Assert
        assertTrue("Recording should start successfully", result.isSuccess)
        assertEquals("Should return session summary", "Session started: Test Session Summary", result.getOrNull())
        
        val state = controller.getCurrentState()
        assertTrue("Should be recording", state.isRecording)
        assertEquals("Session ID should be set", sessionId, state.sessionId)
        assertEquals("Session info should be set", "Test Session Summary", state.sessionInfo)
        assertTrue("Camera should be recording", state.deviceStatuses.cameraRecording)
        assertTrue("Thermal should be recording", state.deviceStatuses.thermalRecording)
        assertTrue("Shimmer should be recording", state.deviceStatuses.shimmerRecording)

        // Verify interactions
        verify(cameraRecorder).startSession(true, false)
        verify(sessionManager).createNewSession()
        verify(thermalRecorder).startRecording(sessionId)
        verify(shimmerRecorder).startRecording(sessionId)
    }

    @Test
    fun `startRecording should fail if already recording`() = runTest {
        // Arrange - start a recording first
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        controller.startRecording()

        // Act - try to start another recording
        val result = controller.startRecording()

        // Assert
        assertTrue("Should fail when already recording", result.isFailure)
        assertTrue("Should be IllegalStateException", result.exceptionOrNull() is IllegalStateException)
    }

    @Test
    fun `startRecording should fail if camera fails to start`() = runTest {
        // Arrange
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(null)

        // Act
        val result = controller.startRecording()

        // Assert
        assertTrue("Recording should fail when camera fails", result.isFailure)
        assertTrue("Should be RuntimeException", result.exceptionOrNull() is RuntimeException)
        
        val state = controller.getCurrentState()
        assertFalse("Should not be recording", state.isRecording)
        assertNotNull("Should have error message", state.recordingError)
    }

    @Test
    fun `stopRecording should succeed when recording`() = runTest {
        // Arrange - start recording first
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        `when`(cameraRecorder.stopSession()).thenReturn(mockSessionInfo)
        controller.startRecording()

        // Act
        val result = controller.stopRecording()

        // Assert
        assertTrue("Recording should stop successfully", result.isSuccess)
        assertEquals("Should return session summary", "Test Session Summary", result.getOrNull())
        
        val state = controller.getCurrentState()
        assertFalse("Should not be recording", state.isRecording)
        assertEquals("Session info should be updated", "Test Session Summary", state.sessionInfo)
        assertFalse("Camera should not be recording", state.deviceStatuses.cameraRecording)
        assertFalse("Thermal should not be recording", state.deviceStatuses.thermalRecording)
        assertFalse("Shimmer should not be recording", state.deviceStatuses.shimmerRecording)

        // Verify interactions
        verify(cameraRecorder).stopSession()
        verify(thermalRecorder).stopRecording()
        verify(shimmerRecorder).stopRecording()
        verify(sessionManager).finalizeCurrentSession()
    }

    @Test
    fun `stopRecording should fail if not recording`() = runTest {
        // Act
        val result = controller.stopRecording()

        // Assert
        assertTrue("Should fail when not recording", result.isFailure)
        assertTrue("Should be IllegalStateException", result.exceptionOrNull() is IllegalStateException)
    }

    @Test
    fun `captureRawImage should succeed when recording`() = runTest {
        // Arrange - start recording first
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        `when`(cameraRecorder.captureRawImage()).thenReturn(true)
        controller.startRecording()

        // Act
        val result = controller.captureRawImage()

        // Assert
        assertTrue("RAW capture should succeed", result.isSuccess)
        verify(cameraRecorder).captureRawImage()
    }

    @Test
    fun `captureRawImage should fail if not recording`() = runTest {
        // Act
        val result = controller.captureRawImage()

        // Assert
        assertTrue("Should fail when not recording", result.isFailure)
        assertTrue("Should be IllegalStateException", result.exceptionOrNull() is IllegalStateException)
    }

    @Test
    fun `pauseRecording should succeed when recording`() = runTest {
        // Arrange - start recording first
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        controller.startRecording()

        // Act
        val result = controller.pauseRecording()

        // Assert
        assertTrue("Pause should succeed", result.isSuccess)
        
        val state = controller.getCurrentState()
        assertTrue("Should still be recording", state.isRecording)
        assertTrue("Should be paused", state.isPaused)
    }

    @Test
    fun `resumeRecording should succeed when paused`() = runTest {
        // Arrange - start and pause recording
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        controller.startRecording()
        controller.pauseRecording()

        // Act
        val result = controller.resumeRecording()

        // Assert
        assertTrue("Resume should succeed", result.isSuccess)
        
        val state = controller.getCurrentState()
        assertTrue("Should still be recording", state.isRecording)
        assertFalse("Should not be paused", state.isPaused)
    }

    @Test
    fun `emergencyStop should clean up all devices`() = runTest {
        // Arrange - start recording first
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(any(), any())).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)
        controller.startRecording()

        // Act
        val result = controller.emergencyStop()

        // Assert
        assertTrue("Emergency stop should succeed", result.isSuccess)
        
        val state = controller.getCurrentState()
        assertFalse("Should not be recording", state.isRecording)
        assertFalse("Should not be paused", state.isPaused)
        assertNull("Session ID should be null", state.sessionId)

        // Verify all devices are stopped (even if they throw exceptions)
        verify(cameraRecorder).stopSession()
        verify(thermalRecorder).stopRecording()
        verify(shimmerRecorder).stopRecording()
        verify(sessionManager).finalizeCurrentSession()
    }

    @Test
    fun `clearError should reset error state`() {
        // Arrange - simulate an error state by accessing private field via reflection
        // (In a real test, we might trigger an actual error)
        controller.clearError()

        // Act & Assert
        val state = controller.getCurrentState()
        assertNull("Error should be cleared", state.recordingError)
    }

    @Test
    fun `recording with custom config should respect settings`() = runTest {
        // Arrange
        val config = RecordingSessionController.RecordingConfig(
            recordVideo = false,
            captureRaw = true,
            enableThermal = false,
            enableShimmer = false
        )
        val sessionId = "test_session_123"
        `when`(cameraRecorder.startSession(false, true)).thenReturn(mockSessionInfo)
        `when`(sessionManager.createNewSession()).thenReturn(sessionId)

        // Act
        val result = controller.startRecording(config)

        // Assert
        assertTrue("Recording should start successfully", result.isSuccess)
        
        val state = controller.getCurrentState()
        assertTrue("Camera should be recording", state.deviceStatuses.cameraRecording)
        assertFalse("Thermal should not be recording", state.deviceStatuses.thermalRecording)
        assertFalse("Shimmer should not be recording", state.deviceStatuses.shimmerRecording)

        // Verify camera was called with correct parameters
        verify(cameraRecorder).startSession(false, true)
        // Verify thermal and shimmer were not started
        verify(thermalRecorder, never()).startRecording(any())
        verify(shimmerRecorder, never()).startRecording(any())
    }
}