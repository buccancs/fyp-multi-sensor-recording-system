package com.multisensor.recording.ui

/**
 * System Health Status for Multi-Sensor Recording App
 * 
 * Tracks the health and connection status of all system components
 */
data class SystemHealthStatus(
    val pcConnection: HealthStatus = HealthStatus.DISCONNECTED,
    val shimmerConnection: HealthStatus = HealthStatus.DISCONNECTED,
    val thermalCamera: HealthStatus = HealthStatus.DISCONNECTED,
    val networkConnection: HealthStatus = HealthStatus.DISCONNECTED,
    val rgbCamera: HealthStatus = HealthStatus.DISCONNECTED,
    val storage: HealthStatus = HealthStatus.DISCONNECTED,
    val batteryLevel: Int = -1,
    val lastUpdateTime: Long = System.currentTimeMillis()
) {
    
    enum class HealthStatus {
        CONNECTED,
        DISCONNECTED,
        ERROR,
        CONNECTING,
        UNKNOWN
    }
    
    /**
     * Overall system health based on individual component status
     */
    val overallHealth: HealthStatus
        get() = when {
            listOf(pcConnection, shimmerConnection, thermalCamera, networkConnection, rgbCamera)
                .any { it == HealthStatus.ERROR } -> HealthStatus.ERROR
            listOf(pcConnection, rgbCamera).all { it == HealthStatus.CONNECTED } -> HealthStatus.CONNECTED
            listOf(pcConnection, shimmerConnection, thermalCamera, networkConnection, rgbCamera)
                .any { it == HealthStatus.CONNECTING } -> HealthStatus.CONNECTING
            else -> HealthStatus.DISCONNECTED
        }
    
    /**
     * Count of connected devices
     */
    val connectedDeviceCount: Int
        get() = listOf(pcConnection, shimmerConnection, thermalCamera, networkConnection, rgbCamera)
            .count { it == HealthStatus.CONNECTED }
    
    /**
     * Whether the system is ready for recording
     */
    val isReadyForRecording: Boolean
        get() = pcConnection == HealthStatus.CONNECTED && 
                rgbCamera == HealthStatus.CONNECTED &&
                (shimmerConnection == HealthStatus.CONNECTED || thermalCamera == HealthStatus.CONNECTED)
}