package com.multisensor.recording.recording

/**
 * Enumeration representing the connection status of devices in the multi-sensor system
 */
enum class DeviceStatus {
    CONNECTED,
    DISCONNECTED,
    CONNECTING,
    ERROR;
    
    /**
     * Check if device is in a working state
     */
    val isWorking: Boolean get() = this == CONNECTED
    
    /**
     * Check if device is in a transitional state
     */
    val isTransitional: Boolean get() = this == CONNECTING
    
    /**
     * Check if device has an issue
     */
    val hasIssue: Boolean get() = this == DISCONNECTED || this == ERROR
    
    /**
     * Get user-friendly display text
     */
    val displayText: String get() = when (this) {
        CONNECTED -> "Connected"
        DISCONNECTED -> "Disconnected"
        CONNECTING -> "Connecting..."
        ERROR -> "Error"
    }
}