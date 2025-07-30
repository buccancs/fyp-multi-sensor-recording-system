package com.multisensor.recording.ui

/**
 * UI State data class for ShimmerConfigActivity
 * 
 * This class represents everything the Shimmer configuration UI needs to know 
 * to draw itself at any given moment. Following modern Android architecture 
 * guidelines for centralized state management.
 */
data class ShimmerConfigUiState(
    // Device Connection State
    val isDeviceConnected: Boolean = false,
    val deviceName: String = "",
    val deviceMacAddress: String = "",
    val connectionStatus: String = "Disconnected",
    
    // Device Information
    val batteryLevel: Int = -1,
    val signalStrength: Int = -1,
    val firmwareVersion: String = "",
    
    // Scanning State
    val isScanning: Boolean = false,
    val availableDevices: List<ShimmerDeviceItem> = emptyList(),
    val selectedDeviceIndex: Int = -1,
    
    // Configuration State
    val samplingRate: Int = 512,
    val enabledSensors: Set<String> = emptySet(),
    val isConfiguring: Boolean = false,
    
    // Recording State
    val isRecording: Boolean = false,
    val recordingDuration: Long = 0L,
    val dataPacketsReceived: Int = 0,
    
    // UI Control States
    val showDeviceList: Boolean = true,
    val showConfigurationPanel: Boolean = false,
    val showRecordingControls: Boolean = false,
    
    // Loading States
    val isLoadingConnection: Boolean = false,
    val isLoadingConfiguration: Boolean = false,
    val isLoadingDeviceInfo: Boolean = false,
    
    // Error Handling
    val errorMessage: String? = null,
    val showErrorDialog: Boolean = false,
    
    // Bluetooth State
    val isBluetoothEnabled: Boolean = false,
    val hasBluetoothPermission: Boolean = false
) {
    
    /**
     * Computed property to determine if scanning can be started
     */
    val canStartScan: Boolean
        get() = isBluetoothEnabled && 
                hasBluetoothPermission && 
                !isScanning && 
                !isLoadingConnection
    
    /**
     * Computed property to determine if device connection can be attempted
     */
    val canConnectToDevice: Boolean
        get() = !isDeviceConnected && 
                selectedDeviceIndex >= 0 && 
                selectedDeviceIndex < availableDevices.size &&
                !isLoadingConnection
    
    /**
     * Computed property to determine if device can be disconnected
     */
    val canDisconnectDevice: Boolean
        get() = isDeviceConnected && !isLoadingConnection
    
    /**
     * Computed property to determine if configuration can be applied
     */
    val canApplyConfiguration: Boolean
        get() = isDeviceConnected && 
                !isConfiguring && 
                !isRecording &&
                enabledSensors.isNotEmpty()
    
    /**
     * Computed property to determine if recording can be started
     */
    val canStartRecording: Boolean
        get() = isDeviceConnected && 
                !isRecording && 
                !isConfiguring &&
                enabledSensors.isNotEmpty()
    
    /**
     * Computed property to determine if recording can be stopped
     */
    val canStopRecording: Boolean
        get() = isRecording
    
    /**
     * Computed property for overall connection health status
     */
    val connectionHealthStatus: ConnectionHealthStatus
        get() = when {
            !isBluetoothEnabled -> ConnectionHealthStatus.BLUETOOTH_DISABLED
            !hasBluetoothPermission -> ConnectionHealthStatus.NO_PERMISSION
            isLoadingConnection -> ConnectionHealthStatus.CONNECTING
            isDeviceConnected && signalStrength > -70 -> ConnectionHealthStatus.EXCELLENT
            isDeviceConnected && signalStrength > -80 -> ConnectionHealthStatus.GOOD
            isDeviceConnected -> ConnectionHealthStatus.POOR
            else -> ConnectionHealthStatus.DISCONNECTED
        }
    
    /**
     * Get the currently selected device if any
     */
    val selectedDevice: ShimmerDeviceItem?
        get() = if (selectedDeviceIndex >= 0 && selectedDeviceIndex < availableDevices.size) {
            availableDevices[selectedDeviceIndex]
        } else null
}

/**
 * Represents a discovered Shimmer device
 */
data class ShimmerDeviceItem(
    val name: String,
    val macAddress: String,
    val rssi: Int,
    val isConnectable: Boolean = true,
    val deviceType: String = "Shimmer3"
)

/**
 * Connection health status enumeration
 */
enum class ConnectionHealthStatus {
    BLUETOOTH_DISABLED,
    NO_PERMISSION,
    DISCONNECTED,
    CONNECTING,
    POOR,
    GOOD,
    EXCELLENT
}

/**
 * Available Shimmer sensors enumeration
 */
enum class ShimmerSensor(val displayName: String, val key: String) {
    ACCELEROMETER("Accelerometer", "accel"),
    GYROSCOPE("Gyroscope", "gyro"),
    MAGNETOMETER("Magnetometer", "mag"),
    GSR("Galvanic Skin Response", "gsr"),
    PPG("Photoplethysmography", "ppg"),
    ECG("Electrocardiogram", "ecg"),
    EMG("Electromyography", "emg"),
    PRESSURE("Pressure", "pressure"),
    TEMPERATURE("Temperature", "temp")
}