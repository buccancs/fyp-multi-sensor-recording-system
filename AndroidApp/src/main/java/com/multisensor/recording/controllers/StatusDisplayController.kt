package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Color
import android.media.MediaActionSound
import android.os.BatteryManager
import android.os.Handler
import android.os.Looper
import android.widget.TextView
import android.view.View
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all status display and monitoring logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * Manages battery monitoring, connection status displays, and periodic status updates.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for status display scenarios
 * TODO: Implement status display state persistence across app restarts
 * TODO: Add support for additional status indicators and metrics
 * TODO: Implement status display customization and themes
 */
@Singleton
class StatusDisplayController @Inject constructor() {
    
    /**
     * Interface for status display-related callbacks to the UI layer
     */
    interface StatusDisplayCallback {
        fun onBatteryLevelChanged(level: Int, color: Int)
        fun onConnectionStatusChanged(type: ConnectionType, connected: Boolean)
        fun onStatusMonitoringInitialized()
        fun onStatusMonitoringError(message: String)
        fun updateStatusText(text: String)
        fun runOnUiThread(action: () -> Unit)
        fun registerBroadcastReceiver(receiver: BroadcastReceiver, filter: IntentFilter): Intent?
        fun unregisterBroadcastReceiver(receiver: BroadcastReceiver)
        fun getBatteryLevelText(): TextView?
        fun getPcConnectionStatus(): TextView?
        fun getPcConnectionIndicator(): View?
        fun getShimmerConnectionStatus(): TextView?
        fun getShimmerConnectionIndicator(): View?
        fun getThermalConnectionStatus(): TextView?
        fun getThermalConnectionIndicator(): View?
    }
    
    /**
     * Connection types for status display
     */
    enum class ConnectionType {
        PC, SHIMMER, THERMAL
    }
    
    private var callback: StatusDisplayCallback? = null
    private var currentBatteryLevel = -1
    private var isPcConnected = false
    private var isShimmerConnected = false
    private var isThermalConnected = false
    private lateinit var statusUpdateHandler: Handler
    private lateinit var mediaActionSound: MediaActionSound
    
    // Battery monitoring receiver
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == Intent.ACTION_BATTERY_CHANGED) {
                val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)

                if (level != -1 && scale != -1) {
                    currentBatteryLevel = (level * 100) / scale
                    updateBatteryDisplay()
                }
            }
        }
    }
    
    /**
     * Set the callback for status display events
     */
    fun setCallback(callback: StatusDisplayCallback) {
        this.callback = callback
    }
    
    /**
     * Initialize status monitoring system
     * Extracted from MainActivity.initializeStatusMonitoring()
     */
    fun initializeStatusMonitoring() {
        android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Initializing status monitoring system")
        
        try {
            // Initialize status update handler
            statusUpdateHandler = Handler(Looper.getMainLooper())

            // Initialize MediaActionSound for calibration feedback
            mediaActionSound = MediaActionSound()
            mediaActionSound.load(MediaActionSound.SHUTTER_CLICK)

            // Register battery receiver
            val batteryFilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
            val batteryIntent = callback?.registerBroadcastReceiver(batteryReceiver, batteryFilter)
            
            // Get initial battery level
            batteryIntent?.let { intent ->
                val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                if (level != -1 && scale != -1) {
                    currentBatteryLevel = (level * 100) / scale
                    updateBatteryDisplay()
                }
            }

            // Initialize status displays
            updatePcConnectionStatus(false) // Start with PC disconnected
            updateSensorConnectionStatus(false, false) // Start with sensors disconnected

            // Start periodic status updates
            startPeriodicStatusUpdates()
            
            callback?.onStatusMonitoringInitialized()
            android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Status monitoring system initialized successfully")
        } catch (e: Exception) {
            android.util.Log.e("StatusDisplayController", "[DEBUG_LOG] Failed to initialize status monitoring: ${e.message}")
            callback?.onStatusMonitoringError("Failed to initialize status monitoring: ${e.message}")
        }
    }
    
    /**
     * Updates the battery level display with current percentage
     * Extracted from MainActivity.updateBatteryDisplay()
     */
    private fun updateBatteryDisplay() {
        callback?.runOnUiThread {
            if (currentBatteryLevel >= 0) {
                val batteryText = "Battery: $currentBatteryLevel%"
                
                // Change text color based on battery level
                val textColor = when {
                    currentBatteryLevel > 50 -> Color.GREEN
                    currentBatteryLevel > 20 -> Color.YELLOW
                    else -> Color.RED
                }
                
                callback?.getBatteryLevelText()?.let { textView ->
                    textView.text = batteryText
                    textView.setTextColor(textColor)
                }
                
                callback?.onBatteryLevelChanged(currentBatteryLevel, textColor)
            } else {
                callback?.getBatteryLevelText()?.let { textView ->
                    textView.text = "Battery: ---%"
                    textView.setTextColor(Color.WHITE)
                }
                
                callback?.onBatteryLevelChanged(-1, Color.WHITE)
            }
        }
    }
    
    /**
     * Updates PC connection status display
     * Extracted from MainActivity.updatePcConnectionStatus()
     */
    fun updatePcConnectionStatus(connected: Boolean) {
        android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Updating PC connection status: $connected")
        
        isPcConnected = connected
        callback?.runOnUiThread {
            val statusText = if (connected) "PC: Connected" else "PC: Waiting for PC..."
            val indicatorColor = if (connected) Color.GREEN else Color.RED
            
            callback?.getPcConnectionStatus()?.text = statusText
            callback?.getPcConnectionIndicator()?.setBackgroundColor(indicatorColor)
            
            callback?.onConnectionStatusChanged(ConnectionType.PC, connected)
        }
    }
    
    /**
     * Updates sensor connectivity status displays
     * Extracted from MainActivity.updateSensorConnectionStatus()
     */
    fun updateSensorConnectionStatus(shimmerConnected: Boolean, thermalConnected: Boolean) {
        android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Updating sensor connection status: Shimmer=$shimmerConnected, Thermal=$thermalConnected")
        
        isShimmerConnected = shimmerConnected
        isThermalConnected = thermalConnected

        callback?.runOnUiThread {
            // Update Shimmer status
            val shimmerStatusText = if (shimmerConnected) "Shimmer: Connected" else "Shimmer: Disconnected"
            val shimmerIndicatorColor = if (shimmerConnected) Color.GREEN else Color.RED
            
            callback?.getShimmerConnectionStatus()?.text = shimmerStatusText
            callback?.getShimmerConnectionIndicator()?.setBackgroundColor(shimmerIndicatorColor)
            
            // Update Thermal status
            val thermalStatusText = if (thermalConnected) "Thermal: Connected" else "Thermal: Disconnected"
            val thermalIndicatorColor = if (thermalConnected) Color.GREEN else Color.RED
            
            callback?.getThermalConnectionStatus()?.text = thermalStatusText
            callback?.getThermalConnectionIndicator()?.setBackgroundColor(thermalIndicatorColor)
            
            callback?.onConnectionStatusChanged(ConnectionType.SHIMMER, shimmerConnected)
            callback?.onConnectionStatusChanged(ConnectionType.THERMAL, thermalConnected)
        }
    }
    
    /**
     * Starts periodic status updates every 5 seconds
     * Extracted from MainActivity.startPeriodicStatusUpdates()
     */
    private fun startPeriodicStatusUpdates() {
        val updateRunnable = object : Runnable {
            override fun run() {
                // Update sensor connection status based on current state
                // Note: Connection status will be updated by other components when they change
                // This periodic update mainly ensures UI consistency

                // Schedule next update
                statusUpdateHandler.postDelayed(this, 5000) // 5 seconds
            }
        }
        statusUpdateHandler.post(updateRunnable)
        
        android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Periodic status updates started")
    }
    
    /**
     * Updates shimmer connection status from external components
     * Extracted from MainActivity.updateShimmerConnectionStatus()
     */
    fun updateShimmerConnectionStatus(connected: Boolean) {
        isShimmerConnected = connected
        updateSensorConnectionStatus(isShimmerConnected, isThermalConnected)
    }
    
    /**
     * Updates thermal connection status from external components
     * Extracted from MainActivity.updateThermalConnectionStatus()
     */
    fun updateThermalConnectionStatus(connected: Boolean) {
        isThermalConnected = connected
        updateSensorConnectionStatus(isShimmerConnected, isThermalConnected)
    }
    
    /**
     * Get current status summary for debugging
     */
    fun getStatusSummary(): String {
        return buildString {
            append("Status Display System Summary:\n")
            append("- Battery Level: ${if (currentBatteryLevel >= 0) "$currentBatteryLevel%" else "Unknown"}\n")
            append("- PC Connected: $isPcConnected\n")
            append("- Shimmer Connected: $isShimmerConnected\n")
            append("- Thermal Connected: $isThermalConnected\n")
            append("- Status Monitoring: ${if (::statusUpdateHandler.isInitialized) "Active" else "Inactive"}")
        }
    }
    
    /**
     * Reset status display controller state
     */
    fun resetState() {
        currentBatteryLevel = -1
        isPcConnected = false
        isShimmerConnected = false
        isThermalConnected = false
        android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Status display controller state reset")
    }
    
    /**
     * Cleanup resources
     */
    fun cleanup() {
        try {
            // Unregister battery receiver
            callback?.unregisterBroadcastReceiver(batteryReceiver)
            
            // Cleanup MediaActionSound
            if (::mediaActionSound.isInitialized) {
                mediaActionSound.release()
            }

            // Remove all Handler callbacks to prevent memory leaks
            if (::statusUpdateHandler.isInitialized) {
                statusUpdateHandler.removeCallbacksAndMessages(null)
            }
            
            android.util.Log.d("StatusDisplayController", "[DEBUG_LOG] Status display controller resources cleaned up")
        } catch (e: Exception) {
            android.util.Log.w("StatusDisplayController", "[DEBUG_LOG] Error during cleanup: ${e.message}")
        }
    }
    
    /**
     * Get current battery level
     */
    fun getCurrentBatteryLevel(): Int = currentBatteryLevel
    
    /**
     * Get connection status for specific type
     */
    fun getConnectionStatus(type: ConnectionType): Boolean {
        return when (type) {
            ConnectionType.PC -> isPcConnected
            ConnectionType.SHIMMER -> isShimmerConnected
            ConnectionType.THERMAL -> isThermalConnected
        }
    }
    
    /**
     * Get MediaActionSound instance for calibration feedback
     * TODO: Consider moving this to CalibrationController
     */
    fun getMediaActionSound(): MediaActionSound? {
        return if (::mediaActionSound.isInitialized) mediaActionSound else null
    }
}