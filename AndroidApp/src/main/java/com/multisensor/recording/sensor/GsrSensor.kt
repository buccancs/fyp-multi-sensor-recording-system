package com.multisensor.recording.sensor

import android.content.Context
import android.util.Log
import com.shimmerresearch.android.Shimmer
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Streamlined GSR sensor implementation using Shimmer
 * Simplified from the complex GSR integration in the original app
 */
class GsrSensor(private val context: Context) {
    
    companion object {
        private const val TAG = "GsrSensor"
    }

    // Sensor state
    private val isInitialized = AtomicBoolean(false)
    private val isConnected = AtomicBoolean(false)
    private val isStreaming = AtomicBoolean(false)

    // Shimmer components
    private var shimmerManager: ShimmerBluetoothManagerAndroid? = null
    private var shimmerDevice: Shimmer? = null
    private var deviceAddress: String? = null

    /**
     * Initialize GSR sensor
     */
    fun initialize(): Boolean {
        return try {
            Log.i(TAG, "Initializing GSR sensor")
            
            shimmerManager = ShimmerBluetoothManagerAndroid(context)
            
            isInitialized.set(true)
            Log.i(TAG, "GSR sensor initialized successfully")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize GSR sensor", e)
            false
        }
    }

    /**
     * Scan for available Shimmer devices
     */
    fun scanForDevices(callback: (List<String>) -> Unit) {
        try {
            shimmerManager?.let { manager ->
                // Scan for Bluetooth devices
                val pairedDevices = manager.getShimmerBluetoothRadio()?.bondedDevices
                val shimmerDevices = pairedDevices?.filter { device ->
                    device.name?.contains("Shimmer", ignoreCase = true) ?: false
                }?.map { device ->
                    "${device.name} (${device.address})"
                } ?: emptyList()
                
                callback(shimmerDevices)
                Log.i(TAG, "Found ${shimmerDevices.size} Shimmer devices")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error scanning for devices", e)
            callback(emptyList())
        }
    }

    /**
     * Connect to a specific Shimmer device
     */
    fun connect(deviceAddress: String): Boolean {
        return try {
            Log.i(TAG, "Connecting to GSR sensor: $deviceAddress")
            
            this.deviceAddress = deviceAddress
            
            shimmerManager?.let { manager ->
                shimmerDevice = manager.getShimmerBluetoothRadio()?.getShimmer(deviceAddress)
                shimmerDevice?.connect()
                
                // Simple connection check (in real implementation, use callbacks)
                Thread.sleep(2000) // Give time for connection
                
                val connected = shimmerDevice?.isConnected ?: false
                isConnected.set(connected)
                
                if (connected) {
                    Log.i(TAG, "GSR sensor connected successfully")
                } else {
                    Log.w(TAG, "GSR sensor connection failed")
                }
                
                connected
            } ?: false
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to connect to GSR sensor", e)
            false
        }
    }

    /**
     * Start GSR data streaming
     */
    fun startStreaming(): Boolean {
        if (!isConnected.get()) {
            Log.w(TAG, "GSR sensor not connected")
            return false
        }

        return try {
            shimmerDevice?.let { device ->
                // Configure for GSR sensing
                device.enableGSRSensor()
                device.startStreaming()
                
                isStreaming.set(true)
                Log.i(TAG, "GSR streaming started")
                true
            } ?: false
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start GSR streaming", e)
            false
        }
    }

    /**
     * Stop GSR data streaming
     */
    fun stopStreaming(): Boolean {
        return try {
            if (isStreaming.get()) {
                shimmerDevice?.stopStreaming()
                isStreaming.set(false)
                Log.i(TAG, "GSR streaming stopped")
            }
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop GSR streaming", e)
            false
        }
    }

    /**
     * Disconnect from GSR sensor
     */
    fun disconnect(): Boolean {
        return try {
            stopStreaming()
            
            shimmerDevice?.disconnect()
            shimmerDevice = null
            deviceAddress = null
            
            isConnected.set(false)
            Log.i(TAG, "GSR sensor disconnected")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to disconnect GSR sensor", e)
            false
        }
    }

    /**
     * Check if sensor is connected
     */
    fun isConnected(): Boolean {
        return isConnected.get()
    }

    /**
     * Check if streaming is active
     */
    fun isStreamingActive(): Boolean {
        return isStreaming.get()
    }

    /**
     * Get connected device info
     */
    fun getDeviceInfo(): String {
        return shimmerDevice?.let { device ->
            "Shimmer GSR: ${device.deviceName}"
        } ?: deviceAddress ?: "No Device"
    }

    /**
     * Release sensor resources
     */
    fun release() {
        try {
            disconnect()
            shimmerManager = null
            
            isInitialized.set(false)
            isConnected.set(false)
            isStreaming.set(false)
            
            Log.i(TAG, "GSR sensor resources released")
        } catch (e: Exception) {
            Log.e(TAG, "Error releasing GSR sensor resources", e)
        }
    }
}