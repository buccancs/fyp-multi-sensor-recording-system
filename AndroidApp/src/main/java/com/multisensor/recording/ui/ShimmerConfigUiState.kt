package com.multisensor.recording.ui

/**
 * UI State data class for ShimmerConfigActivity
 * 
 * Enhanced to support multiple simultaneous Shimmer devices
 * as required by the ShimmerController enhancements.
 * 
 * This class represents everything the Shimmer configuration UI needs to know 
 * to draw itself at any given moment. Following modern Android architecture 
 * guidelines for centralized state management.
 */
data class ShimmerConfigUiState(
    // Multiple Device Support
    val connectedDevices: List<ShimmerDeviceItem> = emptyList(),
    val selectedDeviceIndex: Int = -1, // Index in connectedDevices list
    val maxSimultaneousDevices: Int = 4, // Configurable limit
    
    // Device Connection State (for currently selected device)
    val isDeviceConnected: Boolean = false,
    val deviceName: String = "",
    val deviceMacAddress: String = "",
    val connectionStatus: String = "Disconnected",
    
    // Device Information (for currently selected device)
    val batteryLevel: Int = -1,
    val signalStrength: Int = -1,
    val firmwareVersion: String = "",
    
    // Scanning State
    val isScanning: Boolean = false,
    val availableDevices: List<ShimmerDeviceItem> = emptyList(),
    val selectedScanDeviceIndex: Int = -1, // Index in availableDevices for new connections
    
    // Configuration State (for currently selected device)
    val samplingRate: Int = 512,
    val enabledSensors: Set<String> = emptySet(),
    val isConfiguring: Boolean = false,
    
    // Recording State (affects all connected devices)
    val isRecording: Boolean = false,
    val recordingDuration: Long = 0L,
    val dataPacketsReceived: Int = 0,
    val devicesRecording: Set<String> = emptySet(), // Device addresses currently recording
    
    // UI Control States
    val showDeviceList: Boolean = true,
    val showConfigurationPanel: Boolean = false,
    val showRecordingControls: Boolean = false,
    val showMultiDevicePanel: Boolean = false, // New panel for managing multiple devices
    
    // Loading States
    val isLoadingConnection: Boolean = false,
    val isLoadingConfiguration: Boolean = false,
    val isLoadingDeviceInfo: Boolean = false,
    val devicesConnecting: Set<String> = emptySet(), // Device addresses currently connecting
    
    // Error Handling
    val errorMessage: String? = null,
    val showErrorDialog: Boolean = false,
    val deviceErrors: Map<String, String> = emptyMap(), // Per-device error messages
    
    // Bluetooth State
    val isBluetoothEnabled: Boolean = false,
    val hasBluetoothPermission: Boolean = false,
    
    // Auto-reconnection State
    val autoReconnectEnabled: Boolean = true,
    val devicesForAutoReconnect: List<String> = emptyList(), // Device addresses
    val autoReconnectInProgress: Boolean = false
) {
    
    /**
     * Computed property to determine if scanning can be started
     */
    val canStartScan: Boolean
        get() = isBluetoothEnabled && 
                hasBluetoothPermission && 
                !isScanning && 
                !isLoadingConnection &&
                connectedDevices.size < maxSimultaneousDevices
    
    /**
     * Computed property to determine if device connection can be attempted
     */
    val canConnectToDevice: Boolean
        get() = selectedScanDeviceIndex >= 0 && 
                selectedScanDeviceIndex < availableDevices.size &&
                !isLoadingConnection &&
                connectedDevices.size < maxSimultaneousDevices &&
                !isDeviceAlreadyConnected(availableDevices.getOrNull(selectedScanDeviceIndex)?.macAddress)
    
    /**
     * Computed property to determine if device can be disconnected
     */
    val canDisconnectDevice: Boolean
        get() = selectedDeviceIndex >= 0 &&
                selectedDeviceIndex < connectedDevices.size &&
                !isLoadingConnection
    
    /**
     * Computed property to determine if all devices can be disconnected
     */
    val canDisconnectAllDevices: Boolean
        get() = connectedDevices.isNotEmpty() && !isLoadingConnection
    
    /**
     * Computed property to determine if configuration can be applied
     */
    val canApplyConfiguration: Boolean
        get() = selectedDeviceIndex >= 0 &&
                selectedDeviceIndex < connectedDevices.size &&
                !isConfiguring && 
                !isRecording &&
                enabledSensors.isNotEmpty()
    
    /**
     * Computed property to determine if recording can be started
     */
    val canStartRecording: Boolean
        get() = connectedDevices.isNotEmpty() && 
                !isRecording && 
                !isConfiguring &&
                connectedDevices.any { it.isConnectable } // At least one device is properly configured
    
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
            connectedDevices.isEmpty() -> ConnectionHealthStatus.DISCONNECTED
            connectedDevices.all { it.rssi > -70 } -> ConnectionHealthStatus.EXCELLENT
            connectedDevices.all { it.rssi > -80 } -> ConnectionHealthStatus.GOOD
            else -> ConnectionHealthStatus.POOR
        }
    
    /**
     * Get the currently selected device if any
     */
    val selectedDevice: ShimmerDeviceItem?
        get() = if (selectedDeviceIndex >= 0 && selectedDeviceIndex < connectedDevices.size) {
            connectedDevices[selectedDeviceIndex]
        } else null
    
    /**
     * Get the currently selected scan device if any
     */
    val selectedScanDevice: ShimmerDeviceItem?
        get() = if (selectedScanDeviceIndex >= 0 && selectedScanDeviceIndex < availableDevices.size) {
            availableDevices[selectedScanDeviceIndex]
        } else null
    
    /**
     * Check if a device is already connected
     */
    private fun isDeviceAlreadyConnected(macAddress: String?): Boolean {
        return macAddress != null && connectedDevices.any { it.macAddress == macAddress }
    }
    
    /**
     * Get connection summary for display
     */
    val connectionSummary: String
        get() = when (connectedDevices.size) {
            0 -> "No devices connected"
            1 -> "1 device connected"
            else -> "${connectedDevices.size} devices connected"
        }
    
    /**
     * Get devices with errors
     */
    val devicesWithErrors: List<String>
        get() = deviceErrors.keys.toList()
    
    /**
     * Check if multi-device operations are available
     */
    val hasMultipleDevices: Boolean
        get() = connectedDevices.size > 1
    
    /**
     * Check if more devices can be connected
     */
    val canConnectMoreDevices: Boolean
        get() = connectedDevices.size < maxSimultaneousDevices
    
    /**
     * Get auto-reconnect status
     */
    val autoReconnectStatus: String
        get() = when {
            autoReconnectInProgress -> "Auto-reconnecting..."
            devicesForAutoReconnect.isEmpty() -> "No devices for auto-reconnect"
            else -> "${devicesForAutoReconnect.size} device(s) available for auto-reconnect"
        }
}

/**
 * Represents a discovered or connected Shimmer device
 * Enhanced to support multiple device management
 */
data class ShimmerDeviceItem(
    val name: String,
    val macAddress: String,
    val rssi: Int,
    val isConnectable: Boolean = true,
    val deviceType: String = "Shimmer3",
    val isConnected: Boolean = false,
    val connectionStatus: String = "Disconnected",
    val batteryLevel: Int = -1,
    val connectionPriority: Int = 0,
    val autoReconnectEnabled: Boolean = true,
    val lastConnectedTimestamp: Long = 0L,
    val errorMessage: String? = null
) {
    /**
     * Get display name with connection status
     */
    val displayName: String
        get() = if (isConnected) "$name (Connected)" else name
    
    /**
     * Get connection status with battery if available
     */
    val statusWithBattery: String
        get() = if (isConnected && batteryLevel >= 0) {
            "$connectionStatus (Battery: $batteryLevel%)"
        } else {
            connectionStatus
        }
    
    /**
     * Get signal strength description
     */
    val signalStrengthDescription: String
        get() = when {
            rssi > -50 -> "Excellent"
            rssi > -70 -> "Good"
            rssi > -80 -> "Fair"
            else -> "Poor"
        }
}

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