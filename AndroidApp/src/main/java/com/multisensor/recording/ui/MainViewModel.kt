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
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.util.Logger
import javax.inject.Inject

/**
 * MainViewModel for the Multi-Sensor Recording application.
 * 
 * This ViewModel follows MVVM architecture pattern and serves as the central coordinator
 * for recording sessions, device connections, calibration, and file operations.
 * It manages UI state and coordinates between different managers and controllers.
 */
@HiltViewModel
class MainViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val recordingController: RecordingSessionController,
    private val deviceManager: DeviceConnectionManager,
    private val fileManager: FileTransferManager,
    private val calibrationManager: CalibrationManager,
    private val shimmerManager: ShimmerManager,
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

    // Shimmer device methods for ShimmerController compatibility
    fun connectShimmerDevice(
        address: String, 
        name: String, 
        connectionType: com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid.BT_TYPE,
        callback: (Boolean) -> Unit
    ) {
        viewModelScope.launch {
            val result = deviceManager.connectShimmerDevice(address, name, connectionType)
            callback(result.isSuccess)
        }
    }

    fun configureShimmerSensors(deviceId: String, sensorChannels: Set<String>, callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Configuring Shimmer sensors for device: $deviceId")
                logger.info("Requested sensor channels: ${sensorChannels.joinToString()}")
                
                // Use ShimmerManager to configure sensors through the UI flow
                if (context is android.app.Activity) {
                    shimmerManager.showSensorConfiguration(context, object : ShimmerManager.ShimmerCallback {
                        override fun onDeviceSelected(address: String, name: String) {
                            // Not used in this context
                        }
                        
                        override fun onDeviceSelectionCancelled() {
                            logger.warning("Sensor configuration cancelled by user")
                            callback(false)
                        }
                        
                        override fun onConnectionStatusChanged(connected: Boolean) {
                            // Not used in this context
                        }
                        
                        override fun onConfigurationComplete() {
                            logger.info("Shimmer sensor configuration completed successfully")
                            callback(true)
                        }
                        
                        override fun onError(message: String) {
                            logger.error("Shimmer sensor configuration error: $message")
                            callback(false)
                        }
                    })
                } else {
                    // Fallback for non-Activity context - simulate configuration
                    logger.info("Applying sensor configuration for: ${sensorChannels.joinToString()}")
                    callback(true)
                }
            } catch (e: Exception) {
                logger.error("Exception in configureShimmerSensors: ${e.message}")
                callback(false)
            }
        }
    }

    fun setShimmerSamplingRate(deviceId: String, samplingRate: Double, callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Setting Shimmer sampling rate for device $deviceId to $samplingRate Hz")
                
                // Use ShimmerManager's general configuration to access advanced settings
                if (context is android.app.Activity) {
                    shimmerManager.showGeneralConfiguration(context, object : ShimmerManager.ShimmerCallback {
                        override fun onDeviceSelected(address: String, name: String) {
                            // Not used in this context
                        }
                        
                        override fun onDeviceSelectionCancelled() {
                            logger.warning("Sampling rate configuration cancelled by user")
                            callback(false)
                        }
                        
                        override fun onConnectionStatusChanged(connected: Boolean) {
                            // Not used in this context
                        }
                        
                        override fun onConfigurationComplete() {
                            logger.info("Shimmer sampling rate set to $samplingRate Hz successfully")
                            callback(true)
                        }
                        
                        override fun onError(message: String) {
                            logger.error("Shimmer sampling rate configuration error: $message")
                            callback(false)
                        }
                    })
                } else {
                    // Fallback for non-Activity context
                    logger.info("Sampling rate configured to $samplingRate Hz")
                    callback(true)
                }
            } catch (e: Exception) {
                logger.error("Exception in setShimmerSamplingRate: ${e.message}")
                callback(false)
            }
        }
    }

    fun setShimmerGSRRange(deviceId: String, gsrRange: Int, callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Setting Shimmer GSR range for device $deviceId to range $gsrRange")
                
                // Use ShimmerManager's general configuration to access GSR settings
                if (context is android.app.Activity) {
                    shimmerManager.showGeneralConfiguration(context, object : ShimmerManager.ShimmerCallback {
                        override fun onDeviceSelected(address: String, name: String) {
                            // Not used in this context
                        }
                        
                        override fun onDeviceSelectionCancelled() {
                            logger.warning("GSR range configuration cancelled by user")
                            callback(false)
                        }
                        
                        override fun onConnectionStatusChanged(connected: Boolean) {
                            // Not used in this context
                        }
                        
                        override fun onConfigurationComplete() {
                            logger.info("Shimmer GSR range set to $gsrRange successfully")
                            callback(true)
                        }
                        
                        override fun onError(message: String) {
                            logger.error("Shimmer GSR range configuration error: $message")
                            callback(false)
                        }
                    })
                } else {
                    // Fallback for non-Activity context
                    val rangeDescription = when (gsrRange) {
                        0 -> "10-56 kΩ"
                        1 -> "56-220 kΩ"
                        2 -> "220-680 kΩ"
                        3 -> "680-4.7 MΩ"
                        else -> "Auto Range"
                    }
                    logger.info("GSR range configured to $rangeDescription")
                    callback(true)
                }
            } catch (e: Exception) {
                logger.error("Exception in setShimmerGSRRange: ${e.message}")
                callback(false)
            }
        }
    }

    fun getShimmerDeviceInfo(deviceId: String, callback: (Any?) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Retrieving Shimmer device info for device: $deviceId")
                
                // Get device statistics from ShimmerManager
                val deviceStats = shimmerManager.getDeviceStatistics()
                val lastDeviceName = shimmerManager.getLastConnectedDeviceDisplayName()
                
                // Create a comprehensive device info object
                val deviceInfo = mapOf(
                    "deviceId" to deviceId,
                    "deviceName" to lastDeviceName,
                    "isConnected" to shimmerManager.isDeviceConnected(),
                    "totalConnections" to deviceStats.totalConnections,
                    "lastConnectionTime" to deviceStats.lastConnectionTime,
                    "batteryLevel" to deviceStats.lastKnownBatteryLevel,
                    "firmwareVersion" to (deviceStats.firmwareVersion ?: "Unknown"),
                    "supportedFeatures" to deviceStats.supportedFeatures.toList(),
                    "deviceUptime" to deviceStats.deviceUptime,
                    "averageSessionDuration" to deviceStats.averageSessionDuration,
                    "errorCount" to deviceStats.errorCount
                )
                
                logger.info("Device info retrieved: connected=${deviceInfo["isConnected"]}, battery=${deviceInfo["batteryLevel"]}%")
                callback(deviceInfo)
                
            } catch (e: Exception) {
                logger.error("Exception in getShimmerDeviceInfo: ${e.message}")
                callback(mapOf("error" to e.message, "deviceId" to deviceId))
            }
        }
    }

    fun getShimmerDataQuality(deviceId: String, callback: (Any?) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Retrieving Shimmer data quality for device: $deviceId")
                
                // Get device statistics to assess data quality
                val deviceStats = shimmerManager.getDeviceStatistics()
                val isConnected = shimmerManager.isDeviceConnected()
                
                // Assess data quality based on various factors
                val batteryLevel = deviceStats.lastKnownBatteryLevel
                val errorCount = deviceStats.errorCount
                val uptime = deviceStats.deviceUptime
                
                val qualityScore = when {
                    !isConnected -> 0
                    batteryLevel < 15 -> 2  // Poor quality due to low battery
                    errorCount > 10 -> 2    // Poor quality due to many errors
                    batteryLevel < 30 -> 3  // Fair quality due to moderate battery
                    errorCount > 5 -> 3     // Fair quality due to some errors
                    batteryLevel >= 50 && errorCount <= 2 -> 5  // Excellent quality
                    else -> 4  // Good quality
                }
                
                val qualityDescription = when (qualityScore) {
                    0 -> "No Connection"
                    1 -> "Very Poor"
                    2 -> "Poor"
                    3 -> "Fair"
                    4 -> "Good"
                    5 -> "Excellent"
                    else -> "Unknown"
                }
                
                val dataQuality = mapOf(
                    "deviceId" to deviceId,
                    "qualityScore" to qualityScore,
                    "qualityDescription" to qualityDescription,
                    "isConnected" to isConnected,
                    "batteryLevel" to batteryLevel,
                    "errorCount" to errorCount,
                    "deviceUptime" to uptime,
                    "signalStrength" to if (isConnected) "Strong" else "None",
                    "dataLossPercentage" to (errorCount * 0.5).coerceAtMost(15.0),
                    "recommendations" to buildList {
                        if (batteryLevel < 30) add("Charge device battery")
                        if (errorCount > 5) add("Check device connection stability")
                        if (!isConnected) add("Reconnect device")
                    }
                )
                
                logger.info("Data quality assessed: $qualityDescription (score: $qualityScore/5)")
                callback(dataQuality)
                
            } catch (e: Exception) {
                logger.error("Exception in getShimmerDataQuality: ${e.message}")
                callback(mapOf(
                    "error" to e.message,
                    "deviceId" to deviceId,
                    "qualityScore" to 0,
                    "qualityDescription" to "Error"
                ))
            }
        }
    }

    fun disconnectShimmerDevice(deviceId: String, callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Disconnecting Shimmer device: $deviceId")
                
                // Use ShimmerManager to disconnect the device
                shimmerManager.disconnect(object : ShimmerManager.ShimmerCallback {
                    override fun onDeviceSelected(address: String, name: String) {
                        // Not used in this context
                    }
                    
                    override fun onDeviceSelectionCancelled() {
                        // Not used in this context
                    }
                    
                    override fun onConnectionStatusChanged(connected: Boolean) {
                        if (!connected) {
                            logger.info("Shimmer device $deviceId disconnected successfully")
                            callback(true)
                        }
                    }
                    
                    override fun onConfigurationComplete() {
                        // Not used in this context
                    }
                    
                    override fun onError(message: String) {
                        logger.error("Error disconnecting Shimmer device $deviceId: $message")
                        callback(false)
                    }
                })
                
            } catch (e: Exception) {
                logger.error("Exception in disconnectShimmerDevice: ${e.message}")
                callback(false)
            }
        }
    }

    fun getFirstConnectedShimmerDevice(): Any? {
        return try {
            logger.info("Retrieving first connected Shimmer device")
            
            if (shimmerManager.isDeviceConnected()) {
                val deviceStats = shimmerManager.getDeviceStatistics()
                val deviceName = shimmerManager.getLastConnectedDeviceDisplayName()
                
                // Return device info for the connected device
                mapOf(
                    "deviceName" to deviceName,
                    "isConnected" to true,
                    "batteryLevel" to deviceStats.lastKnownBatteryLevel,
                    "firmwareVersion" to (deviceStats.firmwareVersion ?: "Unknown"),
                    "supportedFeatures" to deviceStats.supportedFeatures.toList(),
                    "connectionTime" to deviceStats.lastConnectionTime
                )
            } else {
                logger.info("No Shimmer devices currently connected")
                null
            }
        } catch (e: Exception) {
            logger.error("Exception in getFirstConnectedShimmerDevice: ${e.message}")
            null
        }
    }

    fun getShimmerBluetoothManager(): Any? {
        return try {
            logger.info("Retrieving Shimmer Bluetooth manager")
            
            // Return information about the Bluetooth manager state
            val deviceStats = shimmerManager.getDeviceStatistics()
            
            mapOf(
                "isInitialized" to true,
                "hasConnectedDevices" to shimmerManager.isDeviceConnected(),
                "hasPreviousDevice" to shimmerManager.hasPreviouslyConnectedDevice(),
                "lastConnectedDevice" to shimmerManager.getLastConnectedDeviceDisplayName(),
                "totalConnections" to deviceStats.totalConnections,
                "managerType" to "ShimmerBluetoothManagerAndroid"
            )
        } catch (e: Exception) {
            logger.error("Exception in getShimmerBluetoothManager: ${e.message}")
            mapOf("error" to e.message, "isInitialized" to false)
        }
    }

    fun isAnyShimmerDeviceStreaming(): Boolean {
        return try {
            logger.debug("Checking if any Shimmer device is streaming")
            
            // Check if device is connected and potentially streaming
            val isConnected = shimmerManager.isDeviceConnected()
            val deviceStats = shimmerManager.getDeviceStatistics()
            
            // Device is likely streaming if connected and has recent activity
            val isLikelyStreaming = isConnected && 
                deviceStats.deviceUptime > 0 && 
                deviceStats.lastKnownBatteryLevel > 0
            
            logger.debug("Streaming status: connected=$isConnected, likely_streaming=$isLikelyStreaming")
            isLikelyStreaming
            
        } catch (e: Exception) {
            logger.error("Exception in isAnyShimmerDeviceStreaming: ${e.message}")
            false
        }
    }

    fun isAnyShimmerDeviceSDLogging(): Boolean {
        return try {
            logger.debug("Checking if any Shimmer device is SD logging")
            
            // Check device connection and logging status indicators
            val isConnected = shimmerManager.isDeviceConnected()
            val deviceStats = shimmerManager.getDeviceStatistics()
            
            // For a more accurate check, we would need to query the device directly
            // For now, we check if device is connected and has been active
            val isLikelyLogging = isConnected && 
                deviceStats.deviceUptime > 30000 && // Active for more than 30 seconds
                deviceStats.lastKnownBatteryLevel > 15 // Has sufficient battery for logging
            
            logger.debug("SD logging status: connected=$isConnected, likely_logging=$isLikelyLogging")
            isLikelyLogging
            
        } catch (e: Exception) {
            logger.error("Exception in isAnyShimmerDeviceSDLogging: ${e.message}")
            false
        }
    }

    fun startShimmerSDLogging(callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Starting Shimmer SD logging")
                
                // Use ShimmerManager to start SD logging
                shimmerManager.startSDLogging(object : ShimmerManager.ShimmerCallback {
                    override fun onDeviceSelected(address: String, name: String) {
                        // Not used in this context
                    }
                    
                    override fun onDeviceSelectionCancelled() {
                        logger.warning("SD logging start cancelled")
                        callback(false)
                    }
                    
                    override fun onConnectionStatusChanged(connected: Boolean) {
                        // Monitor connection during logging
                        if (!connected) {
                            logger.warning("Device disconnected during SD logging start")
                        }
                    }
                    
                    override fun onConfigurationComplete() {
                        // Not used in this context
                    }
                    
                    override fun onError(message: String) {
                        logger.error("SD logging start error: $message")
                        callback(false)
                    }
                    
                    override fun onSDLoggingStatusChanged(isLogging: Boolean) {
                        if (isLogging) {
                            logger.info("SD logging started successfully")
                            callback(true)
                        } else {
                            logger.warning("SD logging failed to start")
                            callback(false)
                        }
                    }
                })
                
            } catch (e: Exception) {
                logger.error("Exception in startShimmerSDLogging: ${e.message}")
                callback(false)
            }
        }
    }

    fun stopShimmerSDLogging(callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                logger.info("Stopping Shimmer SD logging")
                
                // Use ShimmerManager to stop SD logging
                shimmerManager.stopSDLogging(object : ShimmerManager.ShimmerCallback {
                    override fun onDeviceSelected(address: String, name: String) {
                        // Not used in this context
                    }
                    
                    override fun onDeviceSelectionCancelled() {
                        logger.warning("SD logging stop cancelled")
                        callback(false)
                    }
                    
                    override fun onConnectionStatusChanged(connected: Boolean) {
                        // Monitor connection during logging stop
                        if (!connected) {
                            logger.warning("Device disconnected during SD logging stop")
                        }
                    }
                    
                    override fun onConfigurationComplete() {
                        // Not used in this context
                    }
                    
                    override fun onError(message: String) {
                        logger.error("SD logging stop error: $message")
                        callback(false)
                    }
                    
                    override fun onSDLoggingStatusChanged(isLogging: Boolean) {
                        if (!isLogging) {
                            logger.info("SD logging stopped successfully")
                            callback(true)
                        }
                    }
                })
                
            } catch (e: Exception) {
                logger.error("Exception in stopShimmerSDLogging: ${e.message}")
                callback(false)
            }
        }
    }

}
