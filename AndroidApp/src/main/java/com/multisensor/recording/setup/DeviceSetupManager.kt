package com.multisensor.recording.setup

import android.content.Context
import android.util.Log
import com.multisensor.recording.camera.RgbCamera
import com.multisensor.recording.camera.ThermalCamera
import com.multisensor.recording.sensor.GsrSensor

/**
 * Manager for device setup (rgbCamera, thermalCamera, gsrSensor)
 * Extracted from MainActivity to follow Single Responsibility Principle
 */
class DeviceSetupManager(private val context: Context) {
    
    companion object {
        private const val TAG = "DeviceSetupManager"
    }
    
    // Device components for multi-sensor recording
    lateinit var rgbCamera: RgbCamera
    lateinit var thermalCamera: ThermalCamera
    lateinit var gsrSensor: GsrSensor
    
    private var isInitialized = false
    
    /**
     * Initialize all device components
     */
    fun initializeDevices(): Boolean {
        return try {
            Log.i(TAG, "Initializing device components")
            
            // Initialize device components for multi-sensor recording
            rgbCamera = RgbCamera(context)
            thermalCamera = ThermalCamera(context)
            gsrSensor = GsrSensor(context)
            
            isInitialized = true
            Log.i(TAG, "Device components initialized successfully")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize device components", e)
            false
        }
    }
    
    /**
     * Check if devices are initialized
     */
    fun areDevicesReady(): Boolean {
        return isInitialized
    }
    
    /**
     * Get thermal camera status for diagnostics
     */
    fun getThermalCameraStatus(): String {
        return if (::thermalCamera.isInitialized) {
            thermalCamera.getCameraStatus()
        } else "ThermalCamera not initialized"
    }
    
    /**
     * Check if all devices are connected and ready
     */
    fun areAllDevicesReady(): Boolean {
        return isInitialized &&
               ::rgbCamera.isInitialized &&
               ::thermalCamera.isInitialized && thermalCamera.isFullyReady() &&
               ::gsrSensor.isInitialized
    }
    
    /**
     * Cleanup device resources
     */
    fun cleanup() {
        try {
            if (::rgbCamera.isInitialized) rgbCamera.release()
            if (::thermalCamera.isInitialized) thermalCamera.release()
            if (::gsrSensor.isInitialized) gsrSensor.release()
            
            isInitialized = false
            Log.i(TAG, "Device components cleaned up")
        } catch (e: Exception) {
            Log.e(TAG, "Error during device cleanup", e)
        }
    }
}