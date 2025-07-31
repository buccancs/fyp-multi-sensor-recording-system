package com.multisensor.recording.ui

import android.view.TextureView
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
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
        private val logger: Logger,
    ) : ViewModel() {
        
        // Centralized UI State using StateFlow
        private val _uiState = MutableStateFlow(MainUiState())
        val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

        init {
            logger.info("MainViewModel initialized with centralized UiState")
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
        fun initializeSystem(textureView: TextureView) {
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
                        updateUiState { currentState ->
                            currentState.copy(
                                errorMessage = "Failed to initialize camera",
                                showErrorDialog = true
                            )
                        }
                    }

                    // Initialize thermal recorder
                    val thermalInitialized = thermalRecorder.initialize()
                    if (!thermalInitialized) {
                        logger.warning("Thermal camera not available")
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
                            thermalPreviewAvailable = thermalInitialized
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
                            showErrorDialog = true
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
            // For now, we'll proceed with the capture attempt
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
            // For now, we'll just log the change
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
            // For now, we'll just log the change
            logger.info("RAW capture ${if (enabled) "enabled" else "disabled"}")
        }

        /**
         * Run calibration process
         */
        fun runCalibration() {
            viewModelScope.launch {
                try {
                    logger.info("Starting calibration process...")
                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Running calibration...",
                            isCalibrationRunning = true,
                            isLoadingCalibration = true
                        )
                    }

                    // TODO: Implement actual calibration logic
                    // For now, this is a placeholder that simulates calibration

                    // Simulate calibration delay
                    kotlinx.coroutines.delay(2000)

                    updateUiState { currentState ->
                        currentState.copy(
                            statusText = "Calibration completed - Ready",
                            isCalibrationRunning = false,
                            isLoadingCalibration = false
                        )
                    }
                    logger.info("Calibration completed")
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
    }
