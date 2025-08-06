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

/**
 * Refactored MainViewModel following clean MVVM architecture.
 * 
 * This ViewModel now focuses solely on UI state management and coordination,
 * delegating business logic to specialized controllers and managers:
 * - RecordingSessionController: Handles all recording operations
 * - DeviceConnectionManager: Manages device connections
 * - FileTransferManager: Handles file operations
 * - CalibrationManager: Manages calibration processes
 * 
 * By following the single responsibility principle, this ViewModel is now
 * much more maintainable and testable.
 */
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
        
        // Combine states from all controllers
        viewModelScope.launch {
            combine(
                recordingController.recordingState,
                deviceManager.connectionState,
                fileManager.operationState,
                calibrationManager.calibrationState
            ) { recordingState, connectionState, fileState, calibrationState ->
                
                // Update main UI state based on controller states
                _uiState.value.copy(
                    // Recording related
                    isRecording = recordingState.isRecording,
                    isPaused = recordingState.isPaused,
                    recordingSessionId = recordingState.sessionId,
                    isLoadingRecording = false, // Controllers handle their own loading states
                    
                    // Device connection states
                    isCameraConnected = connectionState.cameraConnected,
                    isThermalConnected = connectionState.thermalConnected,
                    isShimmerConnected = connectionState.shimmerConnected,
                    isPcConnected = connectionState.pcConnected,
                    isInitialized = connectionState.cameraConnected || connectionState.thermalConnected,
                    isConnecting = connectionState.isInitializing,
                    isScanning = connectionState.isScanning,
                    
                    // Calibration states
                    isCalibrating = calibrationState.isCalibrating,
                    isCalibrationRunning = calibrationState.isCalibrating,
                    isValidating = calibrationState.isValidating,
                    isCalibratingCamera = calibrationState.calibrationType == CalibrationManager.CalibrationType.CAMERA,
                    isCalibratingThermal = calibrationState.calibrationType == CalibrationManager.CalibrationType.THERMAL,
                    isCalibratingShimmer = calibrationState.calibrationType == CalibrationManager.CalibrationType.SHIMMER,
                    isCameraCalibrated = calibrationState.completedCalibrations.contains(CalibrationManager.CalibrationType.CAMERA),
                    isThermalCalibrated = calibrationState.completedCalibrations.contains(CalibrationManager.CalibrationType.THERMAL),
                    isShimmerCalibrated = calibrationState.completedCalibrations.contains(CalibrationManager.CalibrationType.SHIMMER),
                    
                    // File operation states
                    isTransferring = fileState.isTransferring,
                    
                    // Status and error messages
                    statusText = determineStatusText(recordingState, connectionState, fileState, calibrationState),
                    errorMessage = recordingState.recordingError 
                        ?: connectionState.connectionError 
                        ?: fileState.transferError 
                        ?: calibrationState.calibrationError,
                    
                    // UI control states
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
        
        // Initialize with basic state
        updateUiState { currentState ->
            currentState.copy(
                statusText = "Initializing application...",
                showManualControls = true,
                showPermissionsButton = false
            )
        }
    }

    //region System Initialization
    
    /**
     * Initializes the system with provided views for camera preview
     */
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

    /**
     * Initializes system with fallback mode
     */
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

    //endregion

    //region Recording Operations
    
    /**
     * Starts a new recording session
     */
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

    /**
     * Stops the current recording session
     */
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

    /**
     * Captures a RAW image during recording
     */
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

    /**
     * Pauses the current recording
     */
    fun pauseRecording() {
        viewModelScope.launch {
            recordingController.pauseRecording()
        }
    }

    //endregion

    //region Device Management
    
    /**
     * Connects to the PC server
     */
    fun connectToPC() {
        viewModelScope.launch {
            deviceManager.connectToPC()
        }
    }

    /**
     * Disconnects from the PC server
     */
    fun disconnectFromPC() {
        viewModelScope.launch {
            deviceManager.disconnectFromPC()
        }
    }

    /**
     * Scans for available devices
     */
    fun scanForDevices() {
        viewModelScope.launch {
            deviceManager.scanForDevices()
        }
    }

    /**
     * Connects to all available devices
     */
    fun connectAllDevices() {
        viewModelScope.launch {
            // This would initiate device connections
            deviceManager.refreshDeviceStatus()
        }
    }

    /**
     * Refreshes the status of all devices
     */
    fun refreshSystemStatus() {
        viewModelScope.launch {
            deviceManager.refreshDeviceStatus()
        }
    }

    /**
     * Checks device capabilities
     */
    fun checkRawStage3Availability(): Boolean {
        // This should be handled through device manager's capabilities check
        viewModelScope.launch {
            deviceManager.checkDeviceCapabilities()
        }
        return false // Placeholder - real implementation would return actual value
    }

    /**
     * Checks thermal camera availability
     */
    fun checkThermalCameraAvailability(): Boolean {
        viewModelScope.launch {
            deviceManager.checkDeviceCapabilities()
        }
        return false // Placeholder - real implementation would return actual value
    }

    //endregion

    //region Calibration Operations
    
    /**
     * Runs the calibration process
     */
    fun runCalibration() {
        viewModelScope.launch {
            calibrationManager.runCalibration()
        }
    }

    /**
     * Starts camera calibration
     */
    fun startCameraCalibration() {
        viewModelScope.launch {
            calibrationManager.runCameraCalibration()
        }
    }

    /**
     * Starts thermal calibration
     */
    fun startThermalCalibration() {
        viewModelScope.launch {
            calibrationManager.runThermalCalibration()
        }
    }

    /**
     * Starts Shimmer calibration
     */
    fun startShimmerCalibration() {
        viewModelScope.launch {
            calibrationManager.runShimmerCalibration()
        }
    }

    /**
     * Validates the system calibration
     */
    fun validateSystem() {
        viewModelScope.launch {
            calibrationManager.validateSystemCalibration()
        }
    }

    //endregion

    //region File Operations
    
    /**
     * Transfers files to PC
     */
    fun transferFilesToPC() {
        viewModelScope.launch {
            fileManager.transferAllFilesToPC()
        }
    }

    /**
     * Exports all data
     */
    fun exportData() {
        viewModelScope.launch {
            fileManager.exportAllData()
        }
    }

    /**
     * Deletes the current session
     */
    fun deleteCurrentSession() {
        viewModelScope.launch {
            fileManager.deleteCurrentSession()
        }
    }

    /**
     * Deletes all recorded data
     */
    fun deleteAllFiles() {
        viewModelScope.launch {
            fileManager.deleteAllData()
        }
    }

    /**
     * Opens the data folder
     */
    fun browseFiles() {
        viewModelScope.launch {
            fileManager.openDataFolder()
        }
    }

    /**
     * Refreshes storage information
     */
    fun refreshStorageInfo() {
        viewModelScope.launch {
            fileManager.refreshStorageInfo()
        }
    }

    //endregion

    //region Error Handling
    
    /**
     * Clears any error messages
     */
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

    //endregion

    //region UI State Helpers
    
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

    //endregion

    //region Lifecycle
    
    override fun onCleared() {
        super.onCleared()
        logger.info("MainViewModel cleared")

        // Emergency stop any ongoing operations
        viewModelScope.launch {
            if (recordingController.isRecording()) {
                recordingController.emergencyStop()
            }
        }
    }

    //endregion

    //region Legacy Methods (deprecated - will be removed)
    
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

    //endregion
}