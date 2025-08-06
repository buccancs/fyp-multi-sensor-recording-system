package com.multisensor.recording.ui

import android.content.Context
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import com.multisensor.recording.controllers.RecordingSessionController
import com.multisensor.recording.managers.DeviceConnectionManager
import com.multisensor.recording.managers.FileTransferManager
import com.multisensor.recording.managers.CalibrationManager
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.flow.MutableStateFlow

/**
 * Unit tests for MainViewModelRefactored
 * 
 * Tests demonstrate the clean architecture implementation:
 * - ViewModel focuses only on UI state coordination
 * - Business logic is delegated to specialized controllers
 * - Reactive state management using StateFlow
 * - Proper separation of concerns
 */
class MainViewModelRefactoredTest {

    @Mock
    private lateinit var context: Context

    @Mock
    private lateinit var recordingController: RecordingSessionController

    @Mock
    private lateinit var deviceManager: DeviceConnectionManager

    @Mock
    private lateinit var fileManager: FileTransferManager

    @Mock
    private lateinit var calibrationManager: CalibrationManager

    @Mock
    private lateinit var logger: Logger

    private lateinit var viewModel: MainViewModelRefactored

    // Mock state flows from controllers
    private val recordingStateFlow = MutableStateFlow(RecordingSessionController.RecordingState())
    private val connectionStateFlow = MutableStateFlow(DeviceConnectionManager.DeviceConnectionState())
    private val fileStateFlow = MutableStateFlow(FileTransferManager.FileOperationState())
    private val calibrationStateFlow = MutableStateFlow(CalibrationManager.CalibrationState())

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)

        // Setup mock controller state flows
        `when`(recordingController.recordingState).thenReturn(recordingStateFlow)
        `when`(deviceManager.connectionState).thenReturn(connectionStateFlow)
        `when`(fileManager.operationState).thenReturn(fileStateFlow)
        `when`(calibrationManager.calibrationState).thenReturn(calibrationStateFlow)

        viewModel = MainViewModelRefactored(
            context,
            recordingController,
            deviceManager,
            fileManager,
            calibrationManager,
            logger
        )
    }

    @Test
    fun `viewModel should initialize with clean architecture delegation`() {
        // Assert that ViewModel properly injects all required controllers
        assertNotNull("Recording controller should be injected", recordingController)
        assertNotNull("Device manager should be injected", deviceManager)
        assertNotNull("File manager should be injected", fileManager)
        assertNotNull("Calibration manager should be injected", calibrationManager)
        
        // Verify initialization logging
        verify(logger).info("MainViewModel initialized with clean architecture")
    }

    @Test
    fun `startRecording should delegate to RecordingSessionController`() = runTest {
        // Act
        viewModel.startRecording()

        // Assert - verify delegation to controller
        verify(recordingController).startRecording()
        verify(logger).info("Starting recording session...")
    }

    @Test
    fun `stopRecording should delegate to RecordingSessionController`() = runTest {
        // Act
        viewModel.stopRecording()

        // Assert - verify delegation to controller
        verify(recordingController).stopRecording()
        verify(logger).info("Stopping recording session...")
    }

    @Test
    fun `captureRawImage should delegate to RecordingSessionController`() = runTest {
        // Act
        viewModel.captureRawImage()

        // Assert - verify delegation to controller
        verify(recordingController).captureRawImage()
        verify(logger).info("Capturing RAW image...")
    }

    @Test
    fun `connectToPC should delegate to DeviceConnectionManager`() = runTest {
        // Act
        viewModel.connectToPC()

        // Assert - verify delegation to manager
        verify(deviceManager).connectToPC()
    }

    @Test
    fun `disconnectFromPC should delegate to DeviceConnectionManager`() = runTest {
        // Act
        viewModel.disconnectFromPC()

        // Assert - verify delegation to manager
        verify(deviceManager).disconnectFromPC()
    }

    @Test
    fun `scanForDevices should delegate to DeviceConnectionManager`() = runTest {
        // Act
        viewModel.scanForDevices()

        // Assert - verify delegation to manager
        verify(deviceManager).scanForDevices()
    }

    @Test
    fun `transferFilesToPC should delegate to FileTransferManager`() = runTest {
        // Act
        viewModel.transferFilesToPC()

        // Assert - verify delegation to manager
        verify(fileManager).transferAllFilesToPC()
    }

    @Test
    fun `exportData should delegate to FileTransferManager`() = runTest {
        // Act
        viewModel.exportData()

        // Assert - verify delegation to manager
        verify(fileManager).exportAllData()
    }

    @Test
    fun `deleteCurrentSession should delegate to FileTransferManager`() = runTest {
        // Act
        viewModel.deleteCurrentSession()

        // Assert - verify delegation to manager
        verify(fileManager).deleteCurrentSession()
    }

    @Test
    fun `runCalibration should delegate to CalibrationManager`() = runTest {
        // Act
        viewModel.runCalibration()

        // Assert - verify delegation to manager
        verify(calibrationManager).runCalibration()
    }

    @Test
    fun `startCameraCalibration should delegate to CalibrationManager`() = runTest {
        // Act
        viewModel.startCameraCalibration()

        // Assert - verify delegation to manager
        verify(calibrationManager).runCameraCalibration()
    }

    @Test
    fun `clearError should delegate to all controllers`() {
        // Act
        viewModel.clearError()

        // Assert - verify all controllers are notified to clear errors
        verify(recordingController).clearError()
        verify(deviceManager).clearError()
        verify(fileManager).clearError()
        verify(calibrationManager).clearError()
    }

    @Test
    fun `UI state should react to recording state changes`() = runTest {
        // Arrange - simulate recording state change
        val recordingState = RecordingSessionController.RecordingState(
            isRecording = true,
            sessionId = "test_session_123",
            sessionInfo = "Test Recording Session"
        )

        // Act - update recording state
        recordingStateFlow.value = recordingState

        // Allow state combination to process
        kotlinx.coroutines.delay(100)

        // Assert - UI state should reflect recording state
        val uiState = viewModel.uiState.value
        assertTrue("UI should show recording", uiState.isRecording)
        assertEquals("Session ID should match", "test_session_123", uiState.recordingSessionId)
    }

    @Test
    fun `UI state should react to device connection changes`() = runTest {
        // Arrange - simulate device connection changes
        val connectionState = DeviceConnectionManager.DeviceConnectionState(
            cameraConnected = true,
            thermalConnected = true,
            shimmerConnected = false,
            pcConnected = true
        )

        // Act - update connection state
        connectionStateFlow.value = connectionState

        // Allow state combination to process
        kotlinx.coroutines.delay(100)

        // Assert - UI state should reflect connection state
        val uiState = viewModel.uiState.value
        assertTrue("Camera should be connected", uiState.isCameraConnected)
        assertTrue("Thermal should be connected", uiState.isThermalConnected)
        assertFalse("Shimmer should not be connected", uiState.isShimmerConnected)
        assertTrue("PC should be connected", uiState.isPcConnected)
        assertTrue("System should be initialized", uiState.isInitialized)
    }

    @Test
    fun `UI state should react to calibration state changes`() = runTest {
        // Arrange - simulate calibration in progress
        val calibrationState = CalibrationManager.CalibrationState(
            isCalibrating = true,
            calibrationType = CalibrationManager.CalibrationType.CAMERA,
            completedCalibrations = setOf(CalibrationManager.CalibrationType.THERMAL)
        )

        // Act - update calibration state
        calibrationStateFlow.value = calibrationState

        // Allow state combination to process
        kotlinx.coroutines.delay(100)

        // Assert - UI state should reflect calibration state
        val uiState = viewModel.uiState.value
        assertTrue("Should be calibrating", uiState.isCalibrating)
        assertTrue("Should be calibrating camera", uiState.isCalibratingCamera)
        assertTrue("Thermal should be calibrated", uiState.isThermalCalibrated)
        assertFalse("Camera should not be calibrated yet", uiState.isCameraCalibrated)
    }

    @Test
    fun `UI state should react to file operation changes`() = runTest {
        // Arrange - simulate file transfer in progress
        val fileState = FileTransferManager.FileOperationState(
            isTransferring = true,
            lastOperation = "Transferring files to PC..."
        )

        // Act - update file state
        fileStateFlow.value = fileState

        // Allow state combination to process
        kotlinx.coroutines.delay(100)

        // Assert - UI state should reflect file state
        val uiState = viewModel.uiState.value
        assertTrue("Should be transferring", uiState.isTransferring)
    }

    @Test
    fun `deprecated methods should show appropriate warnings`() = runTest {
        // Act - call deprecated method
        viewModel.switchCamera()

        // Assert - should log warning about deprecation
        verify(logger).warning("switchCamera() is deprecated - functionality moved to DeviceConnectionManager")
    }

    @Test
    fun `onCleared should perform emergency stop if recording`() = runTest {
        // Arrange - simulate recording in progress
        recordingStateFlow.value = RecordingSessionController.RecordingState(isRecording = true)
        `when`(recordingController.isRecording()).thenReturn(true)

        // Act - simulate ViewModel being cleared
        viewModel.onCleared()

        // Allow coroutine to complete
        kotlinx.coroutines.delay(100)

        // Assert - emergency stop should be called
        verify(recordingController).emergencyStop()
        verify(logger).info("MainViewModel cleared")
    }
}