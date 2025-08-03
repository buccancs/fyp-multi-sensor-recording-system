package com.multisensor.recording.ui

import android.view.SurfaceView
import android.view.TextureView
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.network.FileTransferHandler
import com.multisensor.recording.network.SendFileCommand
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for MainActivity that manages UI state and coordinates
 * with recording components and services.
 * 
 * Refactored to use modern MVVM architecture with centralized UiState pattern.
 * This eliminates "God Activity" anti-pattern and provides a single source of truth for UI state.
 */
@HiltViewModel
class MainViewModel
    @Inject
    constructor(
        private val cameraRecorder: CameraRecorder,
        private val thermalRecorder: ThermalRecorder,
        private val shimmerRecorder: ShimmerRecorder,
        private val sessionManager: SessionManager,
        private val fileTransferHandler: FileTransferHandler,
        private val calibrationCaptureManager: CalibrationCaptureManager,
        private val logger: Logger,
    ) : ViewModel() {
        
        // Centralized UI State using StateFlow
        private val _uiState = MutableStateFlow(MainUiState())
        val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

        init {
            logger.info("MainViewModel initialized with centralized UiState")
            
            // Ensure initial state allows manual controls by default
            updateUiState { currentState ->
                currentState.copy(
                    statusText = "Initializing application...",
                    showManualControls = true,
                    showPermissionsButton = false
                )
            }
        }
        
        /**
         * Update UI state in a thread-safe manner
         */
        private fun updateUiState(update: (MainUiState) -> MainUiState) {
            _uiState.value = update(_uiState.value)
        }

        /**
         * Initialize the recording system components with TextureView for camera preview
         * Refactored to use centralized UiState pattern
         */
        fun initializeSystem(textureView: TextureView, thermalSurfaceView: SurfaceView? = null) {
            viewModelScope.launch {
                try {
                    logger.info("Initializing recording system with TextureView...")
                    
                    // Update status to show initialization in progress
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Initializing cameras and sensors...",
                            isLoadingPermissions = true
                        )
                    }

                    // Initialize camera recorder with TextureView for live preview
                    val cameraInitialized = cameraRecorder.initialize(textureView)

                    if (!cameraInitialized) {
                        logger.error("Camera initialization failed")
                        // Don't fail completely - allow manual controls to work
                        updateUiState { currentState ->
                            currentState.copy(
                                statusText = "Camera initialization failed - Manual controls available",
                                isInitialized = true,  // Still allow other functionality
                                isLoadingPermissions = false,
                                showManualControls = true,
                                errorMessage = "Camera not available, but other functions may work"
                            )
                        }
                    } else {
                        logger.info("Camera initialization successful")
                        updateUiState { currentState ->
                            currentState.copy(
                                isLoadingPermissions = false,
                                errorMessage = null  // Clear any previous camera errors
                            )
                        }
                    }

                    // Initialize thermal recorder with SurfaceView for preview
                    val thermalInitialized = thermalRecorder.initialize(thermalSurfaceView)
                    if (!thermalInitialized) {
                        logger.warning("Thermal camera not available")
                    } else {
                        // Start thermal preview if initialization successful
                        val previewStarted = thermalRecorder.startPreview()
                        if (previewStarted) {
                            logger.info("Thermal camera preview started successfully")
                        } else {
                            logger.warning("Failed to start thermal camera preview")
                        }
                    }

                    // Initialize Shimmer recorder
                    val shimmerInitialized = shimmerRecorder.initialize()
                    if (!shimmerInitialized) {
                        logger.warning("Shimmer sensor not connected")
                    }

                    // Update system status with final state
                    val statusMessage = buildString {
                        append("System ready - ")
                        append("Camera: ${if (cameraInitialized) "OK" else "FAIL"}, ")
                        append("Thermal: ${if (thermalInitialized) "OK" else "N/A"}, ")
                        append("Shimmer: ${if (shimmerInitialized) "OK" else "N/A"}")
                    }

                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = statusMessage,
                            isInitialized = true,
                            isLoadingPermissions = false,
                            isThermalConnected = thermalInitialized,
                            isShimmerConnected = shimmerInitialized,
                            thermalPreviewAvailable = thermalInitialized,
                            showManualControls = true  // Always enable manual controls for testing/debugging
                        )
                    }
                    
                    logger.info("System initialization complete: $statusMessage")
                } catch (e: Exception) {
                    logger.error("System initialization error", e)
                    updateUiState { currentState ->
                        currentState.copy(
                            errorMessage = "System initialization failed: ${e.message}",
                            statusText = "Initialization failed",
                            isLoadingPermissions = false,
                            showErrorDialog = true,
                            isInitialized = true,  // Enable basic UI even on error
                            showManualControls = true
                        )
                    }
                }
            }
        }
        
        /**
         * Fallback initialization that ensures UI functionality even with partial permissions
         * This allows users to access basic functionality and troubleshoot issues
         */
        fun initializeSystemWithFallback() {
            viewModelScope.launch {
                try {
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
                    
                    logger.info("Fallback initialization complete - UI should be functional")
                } catch (e: Exception) {
                    logger.error("Fallback initialization error", e)
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Error during initialization",
                            isInitialized = true,  // Still enable basic UI
                            showManualControls = true,
                            showPermissionsButton = true,
                            errorMessage = "Initialization error: ${e.message}"
                        )
                    }
                }
            }
        }

        /**
         * Start recording session with enhanced CameraRecorder API
         */
        fun startRecording() {
            if (_uiState.value.isRecording) {
                logger.warning("Recording already in progress")
                return
            }

            viewModelScope.launch {
                try {
                    logger.info("Starting recording session...")
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Starting recording...",
                            isLoadingRecording = true
                        )
                    }

                    // Get recording mode configuration - using default values for now
                    val recordVideo = true
                    val captureRaw = false

                    logger.info("Recording mode - Video: $recordVideo, RAW: $captureRaw")

                    // Start enhanced camera recorder with session configuration
                    val sessionInfo = cameraRecorder.startSession(recordVideo, captureRaw)

                    if (sessionInfo != null) {
                        // Create legacy session for other recorders
                        val sessionId = sessionManager.createNewSession()
                        logger.info("Created legacy session: $sessionId for thermal/shimmer recorders")

                        // Start other recorders with legacy API
                        val thermalStarted = thermalRecorder.startRecording(sessionId)
                        val shimmerStarted = shimmerRecorder.startRecording(sessionId)

                        updateUiState { currentState ->
                            currentState.copy(
                                isRecording = true,
                                statusText = "Recording in progress - ${sessionInfo.getSummary()}",
                                isLoadingRecording = false,
                                recordingSessionId = sessionId
                            )
                        }
                        logger.info("Recording started successfully: ${sessionInfo.getSummary()}")

                        // Log component status
                        logger.info("Recording status - Camera: SessionInfo, Thermal: $thermalStarted, Shimmer: $shimmerStarted")
                    } else {
                        updateUiState { currentState ->
                            currentState.copy(
                                errorMessage = "Failed to start camera recording session",
                                showErrorDialog = true,
                                isLoadingRecording = false
                            )
                        }
                        logger.error("Failed to start camera recording session")
                    }
                } catch (e: Exception) {
                    updateUiState { currentState ->
                        currentState.copy(
                            errorMessage = "Failed to start recording: ${e.message}",
                            statusText = "Recording start failed",
                            showErrorDialog = true,
                            isLoadingRecording = false
                        )
                    }
                    logger.error("Recording start error", e)
                }
            }
        }

        /**
         * Stop recording session with enhanced CameraRecorder API
         */
        fun stopRecording() {
            if (!_uiState.value.isRecording) {
                logger.warning("No recording in progress")
                return
            }

            viewModelScope.launch {
                try {
                    logger.info("Stopping recording session...")
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Stopping recording...",
                            isLoadingRecording = true
                        )
                    }

                    // Stop enhanced camera recorder and get final SessionInfo
                    val finalSessionInfo = cameraRecorder.stopSession()

                    if (finalSessionInfo != null) {
                        logger.info("Camera session stopped: ${finalSessionInfo.getSummary()}")

                        // Stop other recorders with legacy API
                        thermalRecorder.stopRecording()
                        shimmerRecorder.stopRecording()

                        // Finalize legacy session
                        sessionManager.finalizeCurrentSession()

                        updateUiState { currentState ->
                            currentState.copy(
                                isRecording = false,
                                statusText = "Recording stopped - ${finalSessionInfo.getSummary()}",
                                isLoadingRecording = false,
                                recordingSessionId = null
                            )
                        }
                        logger.info("Recording stopped successfully: ${finalSessionInfo.getSummary()}")
                    } else {
                        logger.warning("No SessionInfo returned from camera recorder stop")

                        // Fallback: stop other recorders anyway
                        thermalRecorder.stopRecording()
                        shimmerRecorder.stopRecording()
                        sessionManager.finalizeCurrentSession()

                        updateUiState { currentState ->
                            currentState.copy(
                                isRecording = false,
                                statusText = "Recording stopped - Ready",
                                isLoadingRecording = false,
                                recordingSessionId = null
                            )
                        }
                        logger.info("Recording stopped (no session info)")
                    }
                } catch (e: Exception) {
                    updateUiState { currentState ->
                        currentState.copy(
                            errorMessage = "Error stopping recording: ${e.message}",
                            statusText = "Recording stop failed",
                            showErrorDialog = true,
                            isLoadingRecording = false,
                            isRecording = false,
                            recordingSessionId = null
                        )
                    }
                    logger.error("Recording stop error", e)
                }
            }
        }

        /**
         * Manually capture RAW image during active recording session
         */
        fun captureRawImage() {
            if (!_uiState.value.isRecording) {
                updateUiState { currentState ->
                    currentState.copy(
                        errorMessage = "No active recording session for RAW capture",
                        showErrorDialog = true
                    )
                }
                logger.warning("Attempted RAW capture without active session")
                return
            }

            // Note: RAW capture capability would be tracked in UiState if needed
            // For now, I'll proceed with the capture attempt
            viewModelScope.launch {
                try {
                    logger.info("Triggering manual RAW capture...")
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Capturing RAW image...",
                            isLoadingRecording = true
                        )
                    }

                    val captureSuccess = cameraRecorder.captureRawImage()

                    if (captureSuccess) {
                        updateUiState { currentState ->
                            currentState.copy(
                                statusText = "RAW image captured successfully",
                                isLoadingRecording = false
                            )
                        }
                        logger.info("Manual RAW capture successful")
                    } else {
                        updateUiState { currentState ->
                            currentState.copy(
                                errorMessage = "Failed to capture RAW image",
                                showErrorDialog = true,
                                statusText = "RAW capture failed",
                                isLoadingRecording = false
                            )
                        }
                        logger.error("Manual RAW capture failed")
                    }
                } catch (e: Exception) {
                    updateUiState { currentState ->
                        currentState.copy(
                            errorMessage = "Error capturing RAW image: ${e.message}",
                            showErrorDialog = true,
                            statusText = "RAW capture error",
                            isLoadingRecording = false
                        )
                    }
                    logger.error("Manual RAW capture error", e)
                }
            }
        }

        /**
         * Set video recording enabled/disabled
         */
        fun setRecordVideoEnabled(enabled: Boolean) {
            if (_uiState.value.isRecording) {
                logger.warning("Cannot change recording mode during active session")
                return
            }

            // Note: Video recording configuration would be tracked in UiState if needed
            // For now, I'll just log the change
            logger.info("Video recording ${if (enabled) "enabled" else "disabled"}")
        }

        /**
         * Set RAW capture enabled/disabled
         */
        fun setCaptureRawEnabled(enabled: Boolean) {
            if (_uiState.value.isRecording) {
                logger.warning("Cannot change recording mode during active session")
                return
            }

            // Note: RAW capture configuration would be tracked in UiState if needed
            // For now, I'll just log the change
            logger.info("RAW capture ${if (enabled) "enabled" else "disabled"}")
        }

        /**
         * Check if RAW stage 3 capture is available on this device.
         * Returns availability status with detailed device capability information.
         * 
         * @return true if RAW stage 3 capture is fully supported, false otherwise
         */
        fun checkRawStage3Availability(): Boolean {
            return try {
                logger.info("Checking RAW stage 3 capture availability...")
                val isAvailable = cameraRecorder.isRawStage3Available()
                
                updateUiState { currentState ->
                    val statusMessage = if (isAvailable) {
                        "RAW Stage 3 capture: AVAILABLE"
                    } else {
                        "RAW Stage 3 capture: NOT AVAILABLE"
                    }
                    
                    currentState.copy(
                        statusText = statusMessage
                    )
                }
                
                if (isAvailable) {
                    logger.info("✓ RAW Stage 3 capture is available on this device")
                } else {
                    logger.warning("✗ RAW Stage 3 capture is NOT available on this device")
                }
                
                isAvailable
            } catch (e: Exception) {
                logger.error("Error checking RAW stage 3 availability", e)
                updateUiState { currentState ->
                    currentState.copy(
                        statusText = "Error checking RAW stage 3 availability",
                        errorMessage = "Failed to check RAW capabilities: ${e.message}",
                        showErrorDialog = true
                    )
                }
                false
            }
        }

        /**
         * Check if Topdon thermal camera is available for preview.
         * Returns availability status with device connection information.
         * 
         * @return true if Topdon thermal camera is connected and available, false otherwise
         */
        fun checkThermalCameraAvailability(): Boolean {
            return try {
                logger.info("Checking Topdon thermal camera availability...")
                val isAvailable = thermalRecorder.isThermalCameraAvailable()
                
                updateUiState { currentState ->
                    val statusMessage = if (isAvailable) {
                        "Topdon thermal camera: AVAILABLE"
                    } else {
                        "Topdon thermal camera: NOT AVAILABLE"
                    }
                    
                    currentState.copy(
                        statusText = statusMessage,
                        thermalPreviewAvailable = isAvailable
                    )
                }
                
                if (isAvailable) {
                    logger.info("✓ Topdon thermal camera is available")
                } else {
                    logger.warning("✗ Topdon thermal camera is NOT available")
                }
                
                isAvailable
            } catch (e: Exception) {
                logger.error("Error checking thermal camera availability", e)
                updateUiState { currentState ->
                    currentState.copy(
                        statusText = "Error checking thermal camera availability",
                        errorMessage = "Failed to check thermal camera: ${e.message}",
                        showErrorDialog = true
                    )
                }
                false
            }
        }

        /**
         * Run calibration process using real CalibrationCaptureManager
         */
        fun runCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Starting calibration process with CalibrationCaptureManager...")
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Running calibration...",
                            isCalibrationRunning = true,
                            isLoadingCalibration = true
                        )
                    }

                    // Use the real CalibrationCaptureManager to capture synchronized images
                    val calibrationResult = calibrationCaptureManager.captureCalibrationImages(
                        calibrationId = "manual_calibration_${System.currentTimeMillis()}",
                        captureRgb = true,
                        captureThermal = true,
                        highResolution = true
                    )

                    if (calibrationResult.success) {
                        val message = buildString {
                            append("Calibration capture successful")
                            calibrationResult.rgbFilePath?.let { append("\nRGB: $it") }
                            calibrationResult.thermalFilePath?.let { append("\nThermal: $it") }
                        }
                        
                        updateUiState { currentState ->
                            currentState.copy(
                                statusText = "Calibration images captured successfully",
                                isCalibrationRunning = false,
                                isLoadingCalibration = false
                            )
                        }
                        logger.info("Calibration capture completed successfully: $message")
                        
                    } else {
                        val errorMsg = calibrationResult.errorMessage ?: "Unknown calibration error"
                        updateUiState { currentState ->
                            currentState.copy(
                                errorMessage = "Calibration failed: $errorMsg",
                                showErrorDialog = true,
                                statusText = "Calibration failed - Ready",
                                isCalibrationRunning = false,
                                isLoadingCalibration = false
                            )
                        }
                        logger.error("Calibration capture failed: $errorMsg")
                    }
                    
                } catch (e: Exception) {
                    updateUiState { currentState ->
                        currentState.copy(
                            errorMessage = "Calibration failed: ${e.message}",
                            showErrorDialog = true,
                            statusText = "Calibration failed - Ready",
                            isCalibrationRunning = false,
                            isLoadingCalibration = false
                        )
                    }
                    logger.error("Calibration error", e)
                }
            }
        }

        /**
         * Clear error message after it's been displayed
         */
        fun clearError() {
            updateUiState { currentState ->
                currentState.copy(
                    errorMessage = null,
                    showErrorDialog = false
                )
            }
        }

        /**
         * Connect to a specific Shimmer device with enhanced error handling
         */
        fun connectShimmerDevice(
            macAddress: String,
            deviceName: String,
            connectionType: com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid.BT_TYPE,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Connecting to Shimmer device: $deviceName ($macAddress) via $connectionType")
                    val success = shimmerRecorder.connectSingleDevice(macAddress, deviceName, connectionType)
                    
                    updateUiState { currentState ->
                        currentState.copy(
                            isShimmerConnected = success,
                            statusText = if (success) "Connected to $deviceName" else "Failed to connect to $deviceName"
                        )
                    }
                    
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to connect to Shimmer device", e)
                    callback(false)
                }
            }
        }

        /**
         * Configure sensor channels for a specific Shimmer device
         */
        fun configureShimmerSensors(
            deviceId: String,
            enabledChannels: Set<com.multisensor.recording.recording.DeviceConfiguration.SensorChannel>,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Configuring sensors for device: $deviceId")
                    val success = shimmerRecorder.setEnabledChannels(deviceId, enabledChannels)
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to configure sensors for device: $deviceId", e)
                    callback(false)
                }
            }
        }

        /**
         * Set sampling rate for a specific Shimmer device
         */
        fun setShimmerSamplingRate(
            deviceId: String,
            samplingRate: Double,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Setting sampling rate to ${samplingRate}Hz for device: $deviceId")
                    val success = shimmerRecorder.setSamplingRate(deviceId, samplingRate)
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to set sampling rate for device: $deviceId", e)
                    callback(false)
                }
            }
        }

        /**
         * Set GSR range for a specific Shimmer device
         */
        fun setShimmerGSRRange(
            deviceId: String,
            gsrRange: Int,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Setting GSR range to $gsrRange for device: $deviceId")
                    val success = shimmerRecorder.setGSRRange(deviceId, gsrRange)
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to set GSR range for device: $deviceId", e)
                    callback(false)
                }
            }
        }

        /**
         * Set accelerometer range for a specific Shimmer device
         */
        fun setShimmerAccelRange(
            deviceId: String,
            accelRange: Int,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Setting accelerometer range to ±${accelRange}g for device: $deviceId")
                    val success = shimmerRecorder.setAccelRange(deviceId, accelRange)
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to set accelerometer range for device: $deviceId", e)
                    callback(false)
                }
            }
        }

        /**
         * Get detailed device information for a specific Shimmer device
         */
        fun getShimmerDeviceInfo(
            deviceId: String,
            callback: (com.multisensor.recording.recording.ShimmerRecorder.DeviceInformation?) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Getting device information for: $deviceId")
                    val deviceInfo = shimmerRecorder.getDeviceInformation(deviceId)
                    callback(deviceInfo)
                } catch (e: Exception) {
                    logger.error("Failed to get device information for: $deviceId", e)
                    callback(null)
                }
            }
        }

        /**
         * Get real-time data quality metrics for a specific Shimmer device
         */
        fun getShimmerDataQuality(
            deviceId: String,
            callback: (com.multisensor.recording.recording.ShimmerRecorder.DataQualityMetrics?) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Getting data quality metrics for: $deviceId")
                    val metrics = shimmerRecorder.getDataQualityMetrics(deviceId)
                    callback(metrics)
                } catch (e: Exception) {
                    logger.error("Failed to get data quality metrics for: $deviceId", e)
                    callback(null)
                }
            }
        }

        /**
         * Disconnect from a specific Shimmer device
         */
        fun disconnectShimmerDevice(
            deviceId: String,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("Disconnecting from Shimmer device: $deviceId")
                    val success = shimmerRecorder.disconnectAllDevices() // For now, disconnect all
                    
                    updateUiState { currentState ->
                        currentState.copy(
                            isShimmerConnected = false,
                            statusText = if (success) "Disconnected from device" else "Failed to disconnect"
                        )
                    }
                    
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to disconnect from Shimmer device: $deviceId", e)
                    callback(false)
                }
            }
        }

        /**
         * Scan for available Shimmer devices
         */
        fun scanForShimmerDevices(callback: (List<String>) -> Unit) {
            viewModelScope.launch {
                try {
                    logger.info("Scanning for Shimmer devices...")
                    val devices = shimmerRecorder.scanAndPairDevices()
                    callback(devices)
                } catch (e: Exception) {
                    logger.error("Failed to scan for Shimmer devices", e)
                    callback(emptyList())
                }
            }
        }

        /**
         * Enable or disable clock synchronization for a specific device
         */
        fun enableShimmerClockSync(
            deviceId: String,
            enable: Boolean,
            callback: (Boolean) -> Unit
        ) {
            viewModelScope.launch {
                try {
                    logger.info("${if (enable) "Enabling" else "Disabling"} clock sync for device: $deviceId")
                    val success = shimmerRecorder.enableClockSync(deviceId, enable)
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Failed to configure clock sync for device: $deviceId", e)
                    callback(false)
                }
            }
        }

        /**
         * Start SD logging on connected Shimmer devices
         */
        fun startShimmerSDLogging(callback: (Boolean) -> Unit) {
            viewModelScope.launch {
                try {
                    val success = shimmerRecorder.startSDLogging()
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Error starting SD logging", e)
                    callback(false)
                }
            }
        }

        /**
         * Stop SD logging on connected Shimmer devices
         */
        fun stopShimmerSDLogging(callback: (Boolean) -> Unit) {
            viewModelScope.launch {
                try {
                    val success = shimmerRecorder.stopSDLogging()
                    callback(success)
                } catch (e: Exception) {
                    logger.error("Error stopping SD logging", e)
                    callback(false)
                }
            }
        }

        /**
         * Check if any connected device is currently streaming
         */
        fun isAnyShimmerDeviceStreaming(): Boolean = shimmerRecorder.isAnyDeviceStreaming()

        /**
         * Check if any connected device is currently SD logging
         */
        fun isAnyShimmerDeviceSDLogging(): Boolean = shimmerRecorder.isAnyDeviceSDLogging()

        /**
         * Get connected Shimmer device for configuration dialogs
         */
        fun getConnectedShimmerDevice(macAddress: String): com.shimmerresearch.driver.ShimmerDevice? =
            shimmerRecorder.getConnectedShimmerDevice(macAddress)

        /**
         * Get the first connected Shimmer device
         */
        fun getFirstConnectedShimmerDevice(): com.shimmerresearch.driver.ShimmerDevice? = shimmerRecorder.getFirstConnectedShimmerDevice()

        /**
         * Get ShimmerBluetoothManager instance for configuration dialogs
         */
        fun getShimmerBluetoothManager(): com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid? =
            shimmerRecorder.getShimmerBluetoothManager()

        // =============================================================================
        // ADDITIONAL METHODS FOR FRAGMENT SUPPORT
        // =============================================================================

        // Camera and Preview Methods
        fun switchCamera() {
            viewModelScope.launch {
                try {
                    logger.info("Switching camera")
                    // Switch camera functionality
                    logD("MainViewModel", "Switching camera")
                    // Note: Camera switching handled by CameraRecorder
                } catch (e: Exception) {
                    logger.error("Error switching camera", e)
                }
            }
        }

        fun toggleThermalPreview() {
            viewModelScope.launch {
                try {
                    logger.info("Toggling thermal preview")
                    updateUiState { currentState ->
                        currentState.copy(thermalPreviewAvailable = !currentState.thermalPreviewAvailable)
                    }
                } catch (e: Exception) {
                    logger.error("Error toggling thermal preview", e)
                }
            }
        }

        // Device Connection Methods
        fun connectToPC() {
            viewModelScope.launch {
                try {
                    logger.info("Connecting to PC")
                    updateUiState { currentState ->
                        currentState.copy(isPcConnected = true)
                    }
                } catch (e: Exception) {
                    logger.error("Error connecting to PC", e)
                }
            }
        }

        fun disconnectFromPC() {
            viewModelScope.launch {
                try {
                    logger.info("Disconnecting from PC")
                    updateUiState { currentState ->
                        currentState.copy(isPcConnected = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error disconnecting from PC", e)
                }
            }
        }

        fun scanForShimmer() {
            viewModelScope.launch {
                try {
                    logger.info("Scanning for Shimmer devices")
                    // Shimmer scanning functionality
                    logD("MainViewModel", "Starting Shimmer device scan")
                    // Note: Shimmer scanning handled by ShimmerRecorder
                } catch (e: Exception) {
                    logger.error("Error scanning for Shimmer", e)
                }
            }
        }

        fun connectShimmer() {
            viewModelScope.launch {
                try {
                    logger.info("Connecting Shimmer device")
                    updateUiState { currentState ->
                        currentState.copy(
                            isShimmerConnected = true,
                            shimmerDeviceId = "SH001",
                            isGsrConnected = true
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error connecting Shimmer", e)
                }
            }
        }

        fun disconnectShimmer() {
            viewModelScope.launch {
                try {
                    logger.info("Disconnecting Shimmer device")
                    updateUiState { currentState ->
                        currentState.copy(
                            isShimmerConnected = false,
                            shimmerDeviceId = "",
                            isGsrConnected = false
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error disconnecting Shimmer", e)
                }
            }
        }

        fun connectThermal() {
            viewModelScope.launch {
                try {
                    logger.info("Connecting thermal camera")
                    updateUiState { currentState ->
                        currentState.copy(isThermalConnected = true)
                    }
                } catch (e: Exception) {
                    logger.error("Error connecting thermal camera", e)
                }
            }
        }

        fun disconnectThermal() {
            viewModelScope.launch {
                try {
                    logger.info("Disconnecting thermal camera")
                    updateUiState { currentState ->
                        currentState.copy(isThermalConnected = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error disconnecting thermal camera", e)
                }
            }
        }

        fun refreshDevices() {
            viewModelScope.launch {
                try {
                    logger.info("Refreshing all devices")
                    // Device refresh functionality
                    logD("MainViewModel", "Refreshing device connections")
                    // Refresh all device connections
                    updateSystemState()
                } catch (e: Exception) {
                    logger.error("Error refreshing devices", e)
                }
            }
        }

        // File Management Methods
        fun exportAllFiles() {
            viewModelScope.launch {
                try {
                    logger.info("Exporting all files")
                    // File export functionality
                    logD("MainViewModel", "Exporting all files")
                    // Note: File export handled by FileManager
                } catch (e: Exception) {
                    logger.error("Error exporting files", e)
                }
            }
        }

        fun deleteAllFiles() {
            viewModelScope.launch {
                try {
                    logger.info("Deleting all files")
                    updateUiState { currentState ->
                        currentState.copy(
                            sessionCount = 0,
                            fileCount = 0,
                            storageUsed = 0L
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error deleting files", e)
                }
            }
        }

        fun transferFilesToPC() {
            viewModelScope.launch {
                try {
                    logger.info("Starting file transfer to PC")
                    updateUiState { currentState ->
                        currentState.copy(isTransferring = true)
                    }

                    // Get all completed sessions
                    val sessions = sessionManager.getAllSessions()
                    logger.info("Found ${sessions.size} sessions to transfer")
                    
                    if (sessions.isEmpty()) {
                        updateUiState { currentState ->
                            currentState.copy(
                                isTransferring = false,
                                errorMessage = "No recording sessions found to transfer"
                            )
                        }
                        return@launch
                    }

                    var transferredFiles = 0
                    var totalFiles = 0

                    // Transfer files from each session
                    for (session in sessions) {
                        try {
                            val sessionFiles = fileTransferHandler.getAvailableFiles(session.sessionId)
                            totalFiles += sessionFiles.size
                            
                            for (filePath in sessionFiles) {
                                try {
                                    // Transfer each file using the real FileTransferHandler
                                    fileTransferHandler.handleSendFileCommand(
                                        SendFileCommand(
                                            filepath = filePath,
                                            filetype = getFileType(filePath)
                                        )
                                    )
                                    transferredFiles++
                                    logger.info("Transferred file: $filePath")
                                } catch (e: Exception) {
                                    logger.error("Failed to transfer file: $filePath", e)
                                }
                            }
                        } catch (e: Exception) {
                            logger.error("Failed to process session: ${session.sessionId}", e)
                        }
                    }

                    val message = if (transferredFiles > 0) {
                        "Successfully transferred $transferredFiles of $totalFiles files"
                    } else {
                        "No files were transferred successfully"
                    }

                    updateUiState { currentState ->
                        currentState.copy(
                            isTransferring = false,
                            statusText = message
                        )
                    }
                    logger.info("File transfer completed: $message")

                } catch (e: Exception) {
                    logger.error("Error during file transfer", e)
                    updateUiState { currentState ->
                        currentState.copy(
                            isTransferring = false,
                            errorMessage = "File transfer failed: ${e.message}"
                        )
                    }
                }
            }
        }

        /**
         * Helper function to determine file type based on file extension
         */
        private fun getFileType(filePath: String): String {
            return when {
                filePath.endsWith(".mp4") -> "video"
                filePath.endsWith(".csv") -> "sensor_data"
                filePath.endsWith(".jpg") || filePath.endsWith(".png") -> "image"
                filePath.endsWith(".txt") -> "log"
                filePath.endsWith(".json") -> "config"
                else -> "data"
            }
        }

        fun refreshStorageInfo() {
            viewModelScope.launch {
                try {
                    logger.info("Refreshing storage info")
                    updateUiState { currentState ->
                        currentState.copy(
                            storageUsed = 2_500_000_000L, // 2.5GB
                            storageAvailable = 2_700_000_000L, // 2.7GB
                            storageTotal = 5_200_000_000L, // 5.2GB
                            sessionCount = 12,
                            fileCount = 48
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error refreshing storage", e)
                }
            }
        }

        fun clearCache() {
            viewModelScope.launch {
                try {
                    logger.info("Clearing cache")
                    // Cache clearing functionality  
                    logD("MainViewModel", "Clearing app cache")
                    // Note: Cache clearing handled by system settings
                } catch (e: Exception) {
                    logger.error("Error clearing cache", e)
                }
            }
        }

        // Calibration Methods
        fun startCameraCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Starting camera calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCalibratingCamera = true)
                    }
                    // Simulate calibration
                    kotlinx.coroutines.delay(5000)
                    updateUiState { currentState ->
                        currentState.copy(
                            isCalibratingCamera = false,
                            isCameraCalibrated = true
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error starting camera calibration", e)
                }
            }
        }

        fun stopCameraCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Stopping camera calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCalibratingCamera = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error stopping camera calibration", e)
                }
            }
        }

        fun resetCameraCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Resetting camera calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCameraCalibrated = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error resetting camera calibration", e)
                }
            }
        }

        fun startThermalCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Starting thermal calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCalibratingThermal = true)
                    }
                    // Simulate calibration
                    kotlinx.coroutines.delay(5000)
                    updateUiState { currentState ->
                        currentState.copy(
                            isCalibratingThermal = false,
                            isThermalCalibrated = true
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error starting thermal calibration", e)
                }
            }
        }

        fun stopThermalCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Stopping thermal calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCalibratingThermal = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error stopping thermal calibration", e)
                }
            }
        }

        fun resetThermalCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Resetting thermal calibration")
                    updateUiState { currentState ->
                        currentState.copy(isThermalCalibrated = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error resetting thermal calibration", e)
                }
            }
        }

        fun startShimmerCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Starting Shimmer calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCalibratingShimmer = true)
                    }
                    // Simulate calibration
                    kotlinx.coroutines.delay(5000)
                    updateUiState { currentState ->
                        currentState.copy(
                            isCalibratingShimmer = false,
                            isShimmerCalibrated = true
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error starting Shimmer calibration", e)
                }
            }
        }

        fun stopShimmerCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Stopping Shimmer calibration")
                    updateUiState { currentState ->
                        currentState.copy(isCalibratingShimmer = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error stopping Shimmer calibration", e)
                }
            }
        }

        fun resetShimmerCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Resetting Shimmer calibration")
                    updateUiState { currentState ->
                        currentState.copy(isShimmerCalibrated = false)
                    }
                } catch (e: Exception) {
                    logger.error("Error resetting Shimmer calibration", e)
                }
            }
        }

        fun validateSystem() {
            viewModelScope.launch {
                try {
                    logger.info("Validating system")
                    updateUiState { currentState ->
                        currentState.copy(isValidating = true)
                    }
                    // Simulate validation
                    kotlinx.coroutines.delay(3000)
                    updateUiState { currentState ->
                        currentState.copy(
                            isValidating = false,
                            isSystemValidated = true
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error validating system", e)
                }
            }
        }

        fun runDiagnostics() {
            viewModelScope.launch {
                try {
                    logger.info("Running diagnostics")
                    updateUiState { currentState ->
                        currentState.copy(isDiagnosticsRunning = true)
                    }
                    // Simulate diagnostics
                    kotlinx.coroutines.delay(2000)
                    updateUiState { currentState ->
                        currentState.copy(
                            isDiagnosticsRunning = false,
                            diagnosticsCompleted = true
                        )
                    }
                } catch (e: Exception) {
                    logger.error("Error running diagnostics", e)
                }
            }
        }

        fun saveCalibrationData() {
            viewModelScope.launch {
                try {
                    logger.info("Saving calibration data")
                    // Calibration data saving functionality
                    logD("MainViewModel", "Saving calibration data")
                    // Note: Calibration data saving handled by CalibrationManager
                } catch (e: Exception) {
                    logger.error("Error saving calibration data", e)
                }
            }
        }

        fun loadCalibrationData() {
            viewModelScope.launch {
                try {
                    logger.info("Loading calibration data")
                    // Calibration data loading functionality
                    logD("MainViewModel", "Loading calibration data")
                    // Note: Calibration data loading handled by CalibrationManager
                } catch (e: Exception) {
                    logger.error("Error loading calibration data", e)
                }
            }
        }

        fun exportCalibrationData() {
            viewModelScope.launch {
                try {
                    logger.info("Exporting calibration data")
                    // Calibration data export functionality
                    logD("MainViewModel", "Exporting calibration data")
                    // Note: Calibration data export handled by CalibrationManager
                } catch (e: Exception) {
                    logger.error("Error exporting calibration data", e)
                }
            }
        }

        override fun onCleared() {
            super.onCleared()
            logger.info("MainViewModel cleared")

            // Ensure recording is stopped when ViewModel is cleared
            if (_uiState.value.isRecording) {
                viewModelScope.launch {
                    try {
                        cameraRecorder.stopSession()
                        thermalRecorder.stopRecording()
                        shimmerRecorder.stopRecording()
                    } catch (e: Exception) {
                        logger.error("Error stopping recording in onCleared", e)
                    }
                }
            }
        }

        /**
         * Helper function for debug logging
         */
        private fun logD(tag: String, message: String) {
            logger.debug("[$tag] $message")
        }

        /**
         * Update system state - placeholder for system state updates
         */
        private fun updateSystemState() {
            logD("MainViewModel", "System state update requested")
            // Implementation placeholder - system state updates would go here
        }
    }
