package com.multisensor.recording.recording

/**
 * Data models for Shimmer sensor recording functionality.
 * Extracted from ShimmerRecorder.kt for better code organization.
 */

/**
 * Data class representing real-time data quality metrics
 */
data class DataQualityMetrics(
    val deviceId: String,
    val samplesAnalyzed: Int,
    val averageSamplingRate: Double,
    val signalQuality: String,
    val batteryLevel: Int,
    val dataLossPercentage: Double,
    val lastSampleTimestamp: Long,
    val connectionStability: String,
    val signalStrength: Int, // Signal strength in dBm
    val errorCount: Int
)

/**
 * Data class representing Shimmer sensor status
 */
data class ShimmerStatus(
    val isAvailable: Boolean,
    val isConnected: Boolean,
    val isRecording: Boolean,
    val samplingRate: Int,
    val batteryLevel: Int? = null, // Battery percentage
    val deviceId: String,
    val connectionTime: Long? = null,
    val lastDataReceived: Long? = null
)

/**
 * Data class representing a Shimmer sensor sample
 */
data class ShimmerSample(
    val timestamp: Long,
    val systemTime: String,
    val gsrConductance: Double,
    val ppgA13: Double,
    val accelX: Double,
    val accelY: Double,
    val accelZ: Double,
    val gyroX: Double,
    val gyroY: Double,
    val gyroZ: Double,
    val magX: Double,
    val magY: Double,
    val magZ: Double,
    val ecg: Double,
    val emg: Double,
    val batteryVoltage: Double,
    val deviceId: String,
    val sequenceNumber: Long
)

/**
 * Data class representing comprehensive device information
 */
data class DeviceInformation(
    val deviceId: String,
    val macAddress: String,
    val deviceName: String,
    val firmwareVersion: String,
    val hardwareVersion: String,
    val serialNumber: String,
    val batteryLevel: Int,
    val connectionTime: Long,
    val lastSeenTime: Long,
    val deviceType: String,
    val supportedSensors: List<String>,
    val currentConfiguration: Map<String, Any>,
    val capabilities: List<String>
)

/**
 * Data class representing sensor configuration
 */
data class SensorConfiguration(
    val gsrRange: Int,
    val accelerometerRange: Int,
    val gyroscopeRange: Int,
    val magnetometerRange: Int,
    val samplingRate: Double,
    val enabledSensors: List<String>,
    val calibrationData: Map<String, Double>
)

/**
 * Enum representing connection states
 */
enum class ShimmerConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    STREAMING,
    LOST_CONNECTION,
    RECONNECTING,
    ERROR
}

/**
 * Enum representing data quality levels
 */
enum class DataQuality {
    EXCELLENT,
    GOOD,
    FAIR,
    POOR,
    CRITICAL
}