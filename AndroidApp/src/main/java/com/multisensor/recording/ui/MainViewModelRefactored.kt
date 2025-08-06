package com.multisensor.recording.ui

import android.content.Context
import android.view.SurfaceView
import android.view.TextureView
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import com.multisensor.recording.controllers.RecordingSessionController
import com.multisensor.recording.managers.DeviceConnectionManager
import com.multisensor.recording.managers.FileTransferManager
import com.multisensor.recording.managers.CalibrationManager
import com.multisensor.recording.util.Logger
import javax.inject.Inject

@HiltViewModel
class MainViewModelRefactored @Inject constructor(
    @ApplicationContext private val context: Context,
    private val recordingController: RecordingSessionController,
    private val deviceManager: DeviceConnectionManager,
    private val fileManager: FileTransferManager,
    private val calibrationManager: CalibrationManager,
    private val logger: Logger
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    init {
        logger.info("MainViewModel initialized with clean architecture")

        viewModelScope.launch {
            combine(
                recordingController.recordingState,
                deviceManager.connectionState,
                fileManager.operationState,
                calibrationManager.calibrationState
            ) { recordingState, connectionState, fileState, calibrationState ->

                _uiState.value.copy(
                    isRecording = recordingState.isRecording,
                    isPaused = recordingState.isPaused,
                    recordingSessionId = recordingState.sessionId,
                    isLoadingRecording = false,

                    isCameraConnected = connectionState.cameraConnected,
                    isThermalConnected = connectionState.thermalConnected,
                    isShimmerConnected = connectionState.shimmerConnected,
                    isPcConnected = connectionState.pcConnected,
                    isInitialized = connectionState.cameraConnected || connectionState.thermalConnected,
                    isConnecting = connectionState.isInitializing,
                    isScanning = connectionState.isScanning,

                    isCalibrating = calibrationState.isCalibrating,
                    isCalibrationRunning = calibrationState.isCalibrating,
                    isValidating = calibrationState.isValidating,
                    isCalibratingCamera = calibrationState.calibrationType == CalibrationManager.CalibrationType.CAMERA,
                    isCalibratingThermal = calibrationState.calibrationType == CalibrationManager.CalibrationType.THERMAL,
                    isCalibratingShimmer = calibrationState.calibrationType == CalibrationManager.CalibrationType.SHIMMER,
                    isCameraCalibrated = calibrationState.completedCalibrations.contains(CalibrationManager.CalibrationType.CAMERA),
                    isThermalCalibrated = calibrationState.completedCalibrations.contains(CalibrationManager.CalibrationType.THERMAL),
                    isShimmerCalibrated = calibrationState.completedCalibrations.contains(CalibrationManager.CalibrationType.SHIMMER),

                    isTransferring = fileState.isTransferring,

                    statusText = determineStatusText(recordingState, connectionState, fileState, calibrationState),
                    errorMessage = recordingState.recordingError
                        ?: connectionState.connectionError
                        ?: fileState.transferError
                        ?: calibrationState.calibrationError,

                    showManualControls = true,
                    isLoadingPermissions = connectionState.isInitializing,
                    showErrorDialog = (recordingState.recordingError != null
                        || connectionState.connectionError != null
                        || fileState.transferError != null
                        || calibrationState.calibrationError != null)
                )
            }.collect { newState ->
                _uiState.value = newState
            }
        }

        updateUiState { currentState ->
            currentState.copy(
                statusText = "Initializing application...",
                showManualControls = true,
                showPermissionsButton = false
            )
        }
    }

    fun initializeSystem(textureView: TextureView, thermalSurfaceView: SurfaceView? = null) {
        viewModelScope.launch {
            try {
                logger.info("Initializing recording system...")

                val result = deviceManager.initializeAllDevices(textureView, thermalSurfaceView)

                if (result.isFailure) {
                    logger.error("System initialization failed: ${result.exceptionOrNull()?.message}")
                    updateUiState { currentState ->
                        currentState.copy(
                            errorMessage = "System initialization failed: ${result.exceptionOrNull()?.message}",
                            showErrorDialog = true,
                            isInitialized = true,
                            showManualControls = true
                        )
                    }
                } else {
                    logger.info("System initialization completed successfully")
                }

            } catch (e: Exception) {
                logger.error("System initialization error", e)
                updateUiState { currentState ->
                    currentState.copy(
                        errorMessage = "System initialization failed: ${e.message}",
                        showErrorDialog = true,
                        isInitialized = true,
                        showManualControls = true
                    )
                }
            }
        }
    }

    fun initializeSystemWithFallback() {
        viewModelScope.launch {
            logger.info("Initializing system with fallback mode...")
            updateUiState { currentState ->
                currentState.copy(
                    statusText = "Basic initialization - Some features may be limited",
                    isInitialized = true,
                    isLoadingPermissions = false,
                    showManualControls = true,
                    showPermissionsButton = true
                )
            }
        }
    }

    fun startRecording() {
        viewModelScope.launch {
            try {
                logger.info("Starting recording session...")
                val result = recordingController.startRecording()

                if (result.isFailure) {
                    logger.error("Failed to start recording: ${result.exceptionOrNull()?.message}")
                }
            } catch (e: Exception) {
                logger.error("Recording start error", e)
            }
        }
    }

    fun stopRecording() {
        viewModelScope.launch {
            try {
                logger.info("Stopping recording session...")
                val result = recordingController.stopRecording()

                if (result.isFailure) {
                    logger.error("Failed to stop recording: ${result.exceptionOrNull()?.message}")
                }
            } catch (e: Exception) {
                logger.error("Recording stop error", e)
            }
        }
    }

    fun captureRawImage() {
        viewModelScope.launch {
            try {
                logger.info("Capturing RAW image...")
                val result = recordingController.captureRawImage()

                if (result.isFailure) {
                    logger.error("Failed to capture RAW image: ${result.exceptionOrNull()?.message}")
                }
            } catch (e: Exception) {
                logger.error("RAW capture error", e)
            }
        }
    }

    fun pauseRecording() {
        viewModelScope.launch {
            recordingController.pauseRecording()
        }
    }

    fun connectToPC() {
        viewModelScope.launch {
            deviceManager.connectToPC()
        }
    }

    fun disconnectFromPC() {
        viewModelScope.launch {
            deviceManager.disconnectFromPC()
        }
    }

    fun scanForDevices() {
        viewModelScope.launch {
            deviceManager.scanForDevices()
        }
    }

    fun connectAllDevices() {
        viewModelScope.launch {
            deviceManager.refreshDeviceStatus()
        }
    }

    fun refreshSystemStatus() {
        viewModelScope.launch {
            deviceManager.refreshDeviceStatus()
        }
    }

    fun checkRawStage3Availability(): Boolean {
        viewModelScope.launch {
            deviceManager.checkDeviceCapabilities()
        }
        return false
    }

    fun checkThermalCameraAvailability(): Boolean {
        viewModelScope.launch {
            deviceManager.checkDeviceCapabilities()
        }
        return false
    }

    fun runCalibration() {
        viewModelScope.launch {
            calibrationManager.runCalibration()
        }
    }

    fun startCameraCalibration() {
        viewModelScope.launch {
            calibrationManager.runCameraCalibration()
        }
    }

    fun startThermalCalibration() {
        viewModelScope.launch {
            calibrationManager.runThermalCalibration()
        }
    }

    fun startShimmerCalibration() {
        viewModelScope.launch {
            calibrationManager.runShimmerCalibration()
        }
    }

    fun validateSystem() {
        viewModelScope.launch {
            calibrationManager.validateSystemCalibration()
        }
    }

    fun transferFilesToPC() {
        viewModelScope.launch {
            fileManager.transferAllFilesToPC()
        }
    }

    fun exportData() {
        viewModelScope.launch {
            fileManager.exportAllData()
        }
    }

    fun deleteCurrentSession() {
        viewModelScope.launch {
            fileManager.deleteCurrentSession()
        }
    }

    fun deleteAllFiles() {
        viewModelScope.launch {
            fileManager.deleteAllData()
        }
    }

    fun browseFiles() {
        viewModelScope.launch {
            fileManager.openDataFolder()
        }
    }

    fun refreshStorageInfo() {
        viewModelScope.launch {
            fileManager.refreshStorageInfo()
        }
    }

    fun clearError() {
        recordingController.clearError()
        deviceManager.clearError()
        fileManager.clearError()
        calibrationManager.clearError()

        updateUiState { currentState ->
            currentState.copy(
                errorMessage = null,
                showErrorDialog = false
            )
        }
    }

    private fun updateUiState(update: (MainUiState) -> MainUiState) {
        _uiState.value = update(_uiState.value)
    }

    private fun determineStatusText(
        recordingState: RecordingSessionController.RecordingState,
        connectionState: DeviceConnectionManager.DeviceConnectionState,
        fileState: FileTransferManager.FileOperationState,
        calibrationState: CalibrationManager.CalibrationState
    ): String {
        return when {
            recordingState.isRecording -> recordingState.sessionInfo ?: "Recording in progress..."
            calibrationState.isCalibrating -> calibrationState.progress?.currentStep ?: "Calibrating..."
            fileState.isTransferring -> "Transferring files..."
            connectionState.isInitializing -> "Initializing devices..."
            connectionState.isScanning -> "Scanning for devices..."
            else -> fileState.lastOperation ?: "Ready"
        }
    }

    override fun onCleared() {
        super.onCleared()
        logger.info("MainViewModel cleared")

        viewModelScope.launch {
            if (recordingController.isRecording()) {
                recordingController.emergencyStop()
            }
        }
    }

    @Deprecated("Use specific controller methods instead")
    fun switchCamera() {
        logger.warning("switchCamera() is deprecated - functionality moved to DeviceConnectionManager")
    }

    @Deprecated("Use CalibrationManager instead")
    fun stopCameraCalibration() {
        viewModelScope.launch {
            calibrationManager.stopCalibration()
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun resetCameraCalibration() {
        viewModelScope.launch {
            calibrationManager.resetCalibration(CalibrationManager.CalibrationType.CAMERA)
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun stopThermalCalibration() {
        viewModelScope.launch {
            calibrationManager.stopCalibration()
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun resetThermalCalibration() {
        viewModelScope.launch {
            calibrationManager.resetCalibration(CalibrationManager.CalibrationType.THERMAL)
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun stopShimmerCalibration() {
        viewModelScope.launch {
            calibrationManager.stopCalibration()
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun resetShimmerCalibration() {
        viewModelScope.launch {
            calibrationManager.resetCalibration(CalibrationManager.CalibrationType.SHIMMER)
        }
    }

    fun openDataFolder() {
        viewModelScope.launch {
            fileManager.openDataFolder()
        }
    }

    fun saveCalibration() {
        viewModelScope.launch {
            calibrationManager.saveCalibrationData()
        }
    }

    fun startCalibration() {
        viewModelScope.launch {
            calibrationManager.runCalibration()
        }
    }

    fun stopCalibration() {
        viewModelScope.launch {
            calibrationManager.stopCalibration()
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun saveCalibrationData() {
        viewModelScope.launch {
            calibrationManager.saveCalibrationData()
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun loadCalibrationData() {
        viewModelScope.launch {
            calibrationManager.loadCalibrationData()
        }
    }

    @Deprecated("Use CalibrationManager instead")
    fun exportCalibrationData() {
        viewModelScope.launch {
            calibrationManager.exportCalibrationData()
        }
    }

    @Deprecated("Use specific methods instead")
    fun runDiagnostics() {
        logger.warning("runDiagnostics() is deprecated - use specific device status checks")
    }

}
