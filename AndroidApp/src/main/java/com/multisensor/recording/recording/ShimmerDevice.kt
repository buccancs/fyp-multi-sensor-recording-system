package com.multisensor.recording.recording

import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * Represents a connected Shimmer3 GSR+ device with its state and configuration.
 * 
 * This data class encapsulates all information needed to manage a single Shimmer device
 * including connection state, device metadata, and runtime statistics.
 */
data class ShimmerDevice(
    val macAddress: String,
    val deviceName: String,
    val deviceId: String = macAddress.takeLast(4), // Last 4 chars of MAC for display
    var connectionState: ConnectionState = ConnectionState.DISCONNECTED,
    var batteryLevel: Int = 0,
    var firmwareVersion: String = "",
    var hardwareVersion: String = "",
    val sampleCount: AtomicLong = AtomicLong(0),
    val isStreaming: AtomicBoolean = AtomicBoolean(false),
    var lastSampleTime: Long = 0L,
    var reconnectionAttempts: Int = 0,
    var configuration: DeviceConfiguration? = null
) {
    
    /**
     * Connection states for Shimmer devices
     */
    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        STREAMING,
        RECONNECTING,
        ERROR
    }
    
    /**
     * Get a display-friendly device identifier
     */
    fun getDisplayName(): String {
        return if (deviceName.isNotBlank() && deviceName != "Shimmer") {
            "$deviceName ($deviceId)"
        } else {
            "Shimmer $deviceId"
        }
    }
    
    /**
     * Check if device is in a connected state
     */
    fun isConnected(): Boolean {
        return connectionState in listOf(
            ConnectionState.CONNECTED,
            ConnectionState.STREAMING
        )
    }
    
    /**
     * Check if device is actively streaming data
     */
    fun isActivelyStreaming(): Boolean {
        return connectionState == ConnectionState.STREAMING && isStreaming.get()
    }
    
    /**
     * Update connection state with logging
     */
    fun updateConnectionState(newState: ConnectionState, logger: com.multisensor.recording.util.Logger? = null) {
        val oldState = connectionState
        connectionState = newState
        
        logger?.debug("Device ${getDisplayName()} state changed: $oldState -> $newState")
        
        // Reset streaming flag if disconnected
        if (newState == ConnectionState.DISCONNECTED) {
            isStreaming.set(false)
            reconnectionAttempts = 0
        }
    }
    
    /**
     * Increment sample count and update last sample time
     */
    fun recordSample() {
        sampleCount.incrementAndGet()
        lastSampleTime = System.currentTimeMillis()
    }
    
    /**
     * Get samples per second based on recent activity
     */
    fun getSamplesPerSecond(): Double {
        val timeSinceLastSample = System.currentTimeMillis() - lastSampleTime
        return if (timeSinceLastSample < 5000 && sampleCount.get() > 0) {
            // Estimate based on recent activity (rough calculation)
            sampleCount.get().toDouble() / ((System.currentTimeMillis() - (lastSampleTime - timeSinceLastSample)) / 1000.0)
        } else {
            0.0
        }
    }
    
    /**
     * Reset device statistics
     */
    fun resetStatistics() {
        sampleCount.set(0)
        lastSampleTime = 0L
        reconnectionAttempts = 0
    }
    
    override fun toString(): String {
        return "ShimmerDevice(${getDisplayName()}, state=$connectionState, samples=${sampleCount.get()}, battery=$batteryLevel%)"
    }
}