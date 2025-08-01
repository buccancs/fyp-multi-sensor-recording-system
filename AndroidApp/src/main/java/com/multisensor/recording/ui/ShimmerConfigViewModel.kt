package com.multisensor.recording.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.DeviceConfiguration
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.util.Logger
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import javax.inject.Inject

@HiltViewModel
class ShimmerConfigViewModel @Inject constructor(
    private val shimmerRecorder: ShimmerRecorder,
    private val logger: Logger,
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ShimmerConfigUiState())
    val uiState: StateFlow<ShimmerConfigUiState> = _uiState.asStateFlow()

    companion object {
        private const val STATUS_UPDATE_INTERVAL_MS = 2000L
    }

    init {
        initialize()
        startPeriodicStatusUpdates()
    }

    private fun initialize() {
        viewModelScope.launch {
            try {
                shimmerRecorder.initialize()
                logger.info("ShimmerRecorder initialized successfully")
            } catch (e: Exception) {
                logger.error("Error initializing ShimmerRecorder", e)
                _uiState.update { 
                    it.copy(
                        errorMessage = "Error initializing shimmer: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    private fun startPeriodicStatusUpdates() {
        viewModelScope.launch {
            flow {
                while (true) {
                    emit(Unit)
                    delay(STATUS_UPDATE_INTERVAL_MS)
                }
            }.collect {
                if (_uiState.value.isDeviceConnected) {
                    updateRealTimeData()
                }
            }
        }
    }

    fun scanForDevices() {
        viewModelScope.launch {
            _uiState.update { 
                it.copy(
                    isScanning = true, 
                    connectionStatus = "Scanning...",
                    errorMessage = null
                ) 
            }
            try {
                val devices = shimmerRecorder.scanAndPairDevices()
                val deviceItems = devices.map { address ->
                    ShimmerDeviceItem(
                        name = "Shimmer Device",
                        macAddress = address,
                        rssi = -50, // Default RSSI since I don't have actual scan data
                        isConnectable = true
                    )
                }
                _uiState.update {
                    it.copy(
                        availableDevices = deviceItems,
                        isScanning = false,
                        connectionStatus = if (deviceItems.isNotEmpty()) "Found ${deviceItems.size} devices" else "No devices found",
                        errorMessage = if (deviceItems.isEmpty()) "No Shimmer devices found. Make sure devices are paired in Bluetooth settings." else null
                    )
                }
            } catch (e: Exception) {
                logger.error("Error scanning for devices", e)
                _uiState.update { 
                    it.copy(
                        isScanning = false,
                        connectionStatus = "Scan failed",
                        errorMessage = "Error scanning: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    fun connectToDevice() {
        val selectedDevice = _uiState.value.selectedDevice ?: return
        viewModelScope.launch {
            _uiState.update { 
                it.copy(
                    isLoadingConnection = true,
                    connectionStatus = "Connecting...",
                    errorMessage = null
                ) 
            }
            try {
                val connected = shimmerRecorder.connectDevices(listOf(selectedDevice.macAddress))
                if (connected) {
                    _uiState.update { 
                        it.copy(
                            isDeviceConnected = true,
                            isLoadingConnection = false,
                            connectionStatus = "Connected",
                            deviceName = selectedDevice.name,
                            deviceMacAddress = selectedDevice.macAddress,
                            showConfigurationPanel = true,
                            showRecordingControls = true
                        ) 
                    }
                } else {
                    _uiState.update { 
                        it.copy(
                            isLoadingConnection = false,
                            connectionStatus = "Connection failed",
                            errorMessage = "Failed to connect to ${selectedDevice.name}",
                            showErrorDialog = true
                        ) 
                    }
                }
            } catch (e: Exception) {
                logger.error("Error connecting", e)
                _uiState.update { 
                    it.copy(
                        isLoadingConnection = false,
                        connectionStatus = "Connection error",
                        errorMessage = "Connection error: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    fun disconnectFromDevice() {
        viewModelScope.launch {
            try {
                if (_uiState.value.isRecording) {
                    shimmerRecorder.stopStreaming()
                }
                shimmerRecorder.cleanup()
                _uiState.update {
                    it.copy(
                        isDeviceConnected = false,
                        isRecording = false,
                        connectionStatus = "Disconnected",
                        deviceName = "",
                        deviceMacAddress = "",
                        batteryLevel = -1,
                        signalStrength = -1,
                        firmwareVersion = "",
                        showConfigurationPanel = false,
                        showRecordingControls = false,
                        recordingDuration = 0L,
                        dataPacketsReceived = 0,
                        errorMessage = null
                    )
                }
            } catch (e: Exception) {
                logger.error("Error disconnecting from device", e)
                _uiState.update { 
                    it.copy(
                        errorMessage = "Disconnect error: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    fun startStreaming() {
        viewModelScope.launch {
            try {
                val started = shimmerRecorder.startStreaming()
                if (started) {
                    _uiState.update { 
                        it.copy(
                            isRecording = true,
                            connectionStatus = "Recording",
                            errorMessage = null
                        ) 
                    }
                } else {
                    _uiState.update { 
                        it.copy(
                            errorMessage = "Failed to start streaming",
                            showErrorDialog = true
                        ) 
                    }
                }
            } catch (e: Exception) {
                logger.error("Error starting streaming", e)
                _uiState.update { 
                    it.copy(
                        errorMessage = "Streaming error: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    fun stopStreaming() {
        viewModelScope.launch {
            try {
                val stopped = shimmerRecorder.stopStreaming()
                if (stopped) {
                    _uiState.update { 
                        it.copy(
                            isRecording = false,
                            connectionStatus = "Connected",
                            errorMessage = null
                        ) 
                    }
                } else {
                    _uiState.update { 
                        it.copy(
                            errorMessage = "Failed to stop streaming",
                            showErrorDialog = true
                        ) 
                    }
                }
            } catch (e: Exception) {
                logger.error("Error stopping streaming", e)
                _uiState.update { 
                    it.copy(
                        errorMessage = "Stop streaming error: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    private fun updateRealTimeData() {
        viewModelScope.launch {
            try {
                val status = shimmerRecorder.getShimmerStatus()
                val readings = shimmerRecorder.getCurrentReadings()
                
                _uiState.update {
                    it.copy(
                        batteryLevel = status.batteryLevel ?: -1,
                        signalStrength = if (status.isConnected) -50 else -100, // Simulated signal strength
                        dataPacketsReceived = it.dataPacketsReceived + if (readings != null) 1 else 0,
                        recordingDuration = if (it.isRecording) it.recordingDuration + STATUS_UPDATE_INTERVAL_MS else 0L
                    )
                }
            } catch (e: Exception) {
                logger.error("Error updating real-time data", e)
            }
        }
    }

    fun onDeviceSelected(index: Int) {
        _uiState.update { it.copy(selectedDeviceIndex = index) }
    }

    fun updateSensorConfiguration(enabledSensors: Set<String>) {
        _uiState.update { 
            it.copy(
                enabledSensors = enabledSensors,
                isConfiguring = true
            ) 
        }
        
        viewModelScope.launch {
            try {
                // Apply sensor configuration to device if connected
                if (_uiState.value.isDeviceConnected) {
                    // Implement actual sensor configuration update
                    val sensorChannels = enabledSensors.mapNotNull { sensorName ->
                        // Convert string sensor names to SensorChannel enum values
                        try {
                            com.multisensor.recording.recording.DeviceConfiguration.SensorChannel.valueOf(sensorName.uppercase())
                        } catch (e: IllegalArgumentException) {
                            logger.warning("Unknown sensor channel: $sensorName")
                            null
                        }
                    }.toSet()
                    
                    val result = _uiState.value.selectedDevice?.let { device ->
                        shimmerRecorder.setEnabledChannels(device.macAddress, sensorChannels)
                    } ?: false
                    
                    if (!result) {
                        logger.warning("Failed to update sensor configuration")
                    } else {
                        logger.info("Sensor configuration updated successfully")
                    }
                    
                    delay(500) // Allow time for configuration to apply
                }
                _uiState.update { it.copy(isConfiguring = false) }
            } catch (e: Exception) {
                logger.error("Error updating sensor configuration", e)
                _uiState.update { 
                    it.copy(
                        isConfiguring = false,
                        errorMessage = "Configuration error: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    fun updateSamplingRate(samplingRate: Int) {
        _uiState.update { it.copy(samplingRate = samplingRate) }
        
        viewModelScope.launch {
            try {
                // Apply sampling rate to device if connected
                if (_uiState.value.isDeviceConnected) {
                    // Implement actual sampling rate update
                    val result = _uiState.value.selectedDevice?.let { device ->
                        shimmerRecorder.setSamplingRate(device.macAddress, samplingRate.toDouble())
                    } ?: false
                    
                    if (!result) {
                        logger.warning("Failed to update sampling rate")
                    } else {
                        logger.info("Sampling rate updated to ${samplingRate}Hz")
                    }
                    
                    delay(200) // Allow time for configuration to apply
                }
            } catch (e: Exception) {
                logger.error("Error updating sampling rate", e)
                _uiState.update { 
                    it.copy(
                        errorMessage = "Sampling rate error: ${e.message}",
                        showErrorDialog = true
                    ) 
                }
            }
        }
    }

    fun updateBluetoothState(isEnabled: Boolean, hasPermission: Boolean) {
        _uiState.update { 
            it.copy(
                isBluetoothEnabled = isEnabled,
                hasBluetoothPermission = hasPermission
            ) 
        }
    }

    fun onErrorMessageShown() {
        _uiState.update { 
            it.copy(
                errorMessage = null,
                showErrorDialog = false
            ) 
        }
    }
}