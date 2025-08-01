package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.content.Context
import android.graphics.Color
import android.media.MediaActionSound
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Toast
import androidx.lifecycle.LifecycleCoroutineScope
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.calibration.SyncClockManager
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all calibration system logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * Manages calibration capture, feedback mechanisms, sync testing, and clock synchronization.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for calibration scenarios
 * TODO: Implement calibration state persistence across app restarts
 * TODO: Add support for different calibration patterns and configurations
 * TODO: Implement calibration quality validation and metrics
 */
@Singleton
class CalibrationController @Inject constructor(
    private val calibrationCaptureManager: CalibrationCaptureManager,
    private val syncClockManager: SyncClockManager
) {
    
    /**
     * Interface for calibration-related callbacks to the UI layer
     */
    interface CalibrationCallback {
        fun onCalibrationStarted()
        fun onCalibrationCompleted(calibrationId: String)
        fun onCalibrationFailed(errorMessage: String)
        fun onSyncTestCompleted(success: Boolean, message: String)
        fun updateStatusText(text: String)
        fun showToast(message: String, duration: Int = Toast.LENGTH_SHORT)
        fun runOnUiThread(action: () -> Unit)
        fun getContentView(): View
    }
    
    private var callback: CalibrationCallback? = null
    private var mediaActionSound: MediaActionSound? = null
    
    /**
     * Set the callback for calibration events
     */
    fun setCallback(callback: CalibrationCallback) {
        this.callback = callback
    }
    
    /**
     * Initialize calibration controller
     */
    fun initialize() {
        try {
            mediaActionSound = MediaActionSound()
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration controller initialized")
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to initialize MediaActionSound: ${e.message}")
        }
    }
    
    /**
     * Run calibration capture process
     * Extracted from MainActivity.runCalibration()
     */
    fun runCalibration(lifecycleScope: LifecycleCoroutineScope) {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Starting enhanced calibration capture with CalibrationCaptureManager")
        
        // Show initial calibration start message
        callback?.showToast("Starting calibration capture...")
        callback?.onCalibrationStarted()
        
        // Use actual CalibrationCaptureManager for 
        lifecycleScope.launch {
            try {
                val result = calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = null, // Auto-generate ID
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = true
                )
                
                if (result.success) {
                    android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration capture successful: ${result.calibrationId}")
                    
                    // Trigger enhanced feedback for successful capture
                    callback?.runOnUiThread {
                        triggerCalibrationCaptureSuccess(result.calibrationId)
                    }
                    
                    callback?.onCalibrationCompleted(result.calibrationId)
                } else {
                    android.util.Log.e("CalibrationController", "[DEBUG_LOG] Calibration capture failed: ${result.errorMessage}")
                    callback?.runOnUiThread {
                        callback?.showToast("Calibration capture failed: ${result.errorMessage}", Toast.LENGTH_LONG)
                    }
                    
                    callback?.onCalibrationFailed(result.errorMessage ?: "Unknown error")
                }
            } catch (e: Exception) {
                android.util.Log.e("CalibrationController", "[DEBUG_LOG] Error during calibration capture", e)
                callback?.runOnUiThread {
                    callback?.showToast("Calibration error: ${e.message}", Toast.LENGTH_LONG)
                }
                
                callback?.onCalibrationFailed("Calibration error: ${e.message}")
            }
        }
    }
    
    /**
     * Triggers comprehensive calibration capture feedback - Enhanced for 
     */
    private fun triggerCalibrationCaptureSuccess(calibrationId: String = "unknown") {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration photo captured - triggering feedback for ID: $calibrationId")
        
        // 1. Toast notification
        showCalibrationCaptureToast()
        
        // 2. Screen flash visual feedback
        triggerScreenFlash()
        
        // 3. Audio feedback (camera shutter sound)
        triggerCalibrationAudioFeedback()
        
        // 4. Visual cue for multi-angle calibration
        showCalibrationGuidance()
    }
    
    /**
     * Shows toast message for calibration photo capture
     */
    private fun showCalibrationCaptureToast() {
        callback?.showToast("📸 Calibration photo captured!")
    }
    
    /**
     * Triggers screen flash visual feedback
     */
    private fun triggerScreenFlash() {
        callback?.getContentView()?.let { contentView ->
            // Create a white overlay view for screen flash effect
            val flashOverlay = View(contentView.context).apply {
                setBackgroundColor(Color.WHITE)
                alpha = 0.8f
            }
            
            // Add overlay to the root view
            if (contentView is android.view.ViewGroup) {
                contentView.addView(
                    flashOverlay,
                    android.view.ViewGroup.LayoutParams(
                        android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                        android.view.ViewGroup.LayoutParams.MATCH_PARENT
                    )
                )
                
                // Remove overlay after brief flash
                Handler(Looper.getMainLooper()).postDelayed({
                    try {
                        contentView.removeView(flashOverlay)
                        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Screen flash effect completed")
                    } catch (e: Exception) {
                        android.util.Log.w("CalibrationController", "[DEBUG_LOG] Error removing flash overlay: ${e.message}")
                    }
                }, 150) // 150ms flash duration
            }
        }
    }
    
    /**
     * Triggers calibration audio feedback
     */
    private fun triggerCalibrationAudioFeedback() {
        try {
            mediaActionSound?.play(MediaActionSound.SHUTTER_CLICK)
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Camera shutter sound played for calibration feedback")
        } catch (e: Exception) {
            android.util.Log.w("CalibrationController", "[DEBUG_LOG] Failed to play shutter sound: ${e.message}")
        }
    }
    
    /**
     * Shows calibration guidance for multi-angle capture
     */
    private fun showCalibrationGuidance() {
        // Show additional toast with guidance
        Handler(Looper.getMainLooper()).postDelayed({
            callback?.showToast("📐 Position device at different angle and capture again", Toast.LENGTH_LONG)
        }, 1000) // 1 second delay after initial feedback
        
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Multi-angle calibration guidance displayed")
    }
    
    /**
     * Test flash sync signal - 
     */
    fun testFlashSync(lifecycleScope: LifecycleCoroutineScope) {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Testing flash sync signal")
        
        lifecycleScope.launch {
            try {
                // Trigger screen flash for sync testing
                callback?.runOnUiThread {
                    triggerScreenFlash()
                    callback?.showToast("🔆 Flash sync signal triggered!")
                }
                
                android.util.Log.d("CalibrationController", "[DEBUG_LOG] Flash sync test completed successfully")
                callback?.onSyncTestCompleted(true, "Flash sync signal triggered successfully")
            } catch (e: Exception) {
                android.util.Log.e("CalibrationController", "[DEBUG_LOG] Error during flash sync test", e)
                callback?.runOnUiThread {
                    callback?.showToast("Flash sync test failed: ${e.message}", Toast.LENGTH_LONG)
                }
                callback?.onSyncTestCompleted(false, "Flash sync test failed: ${e.message}")
            }
        }
    }
    
    /**
     * Test beep sync signal - 
     */
    fun testBeepSync() {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Testing beep sync signal")
        
        try {
            // Trigger audio beep for sync testing
            triggerCalibrationAudioFeedback()
            callback?.showToast("🔊 Beep sync signal triggered!")
            
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Beep sync test completed successfully")
            callback?.onSyncTestCompleted(true, "Beep sync signal triggered successfully")
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Error during beep sync test", e)
            callback?.showToast("Beep sync test failed: ${e.message}", Toast.LENGTH_LONG)
            callback?.onSyncTestCompleted(false, "Beep sync test failed: ${e.message}")
        }
    }
    
    /**
     * Test clock synchronization - 
     */
    fun testClockSync(lifecycleScope: LifecycleCoroutineScope) {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Testing clock synchronization")
        
        lifecycleScope.launch {
            try {
                // Simulate PC timestamp for testing
                val simulatedPcTimestamp = System.currentTimeMillis() + 1000 // 1 second ahead
                val syncId = "test_sync_${System.currentTimeMillis()}"
                
                val success = syncClockManager.synchronizeWithPc(simulatedPcTimestamp, syncId)
                
                callback?.runOnUiThread {
                    if (success) {
                        val syncStatus = syncClockManager.getSyncStatus()
                        val statusMessage = "✅ Clock sync successful!\nOffset: ${syncStatus.clockOffsetMs}ms\nSync ID: $syncId"
                        callback?.showToast(statusMessage, Toast.LENGTH_LONG)
                        
                        // Update status text with sync info
                        callback?.updateStatusText("Clock synchronized - Offset: ${syncStatus.clockOffsetMs}ms")
                        
                        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Clock sync test successful: offset=${syncStatus.clockOffsetMs}ms")
                        callback?.onSyncTestCompleted(true, "Clock synchronized with offset: ${syncStatus.clockOffsetMs}ms")
                    } else {
                        callback?.showToast("❌ Clock sync test failed", Toast.LENGTH_LONG)
                        android.util.Log.e("CalibrationController", "[DEBUG_LOG] Clock sync test failed")
                        callback?.onSyncTestCompleted(false, "Clock synchronization failed")
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e("CalibrationController", "[DEBUG_LOG] Error during clock sync test", e)
                callback?.runOnUiThread {
                    callback?.showToast("Clock sync test error: ${e.message}", Toast.LENGTH_LONG)
                }
                callback?.onSyncTestCompleted(false, "Clock sync test error: ${e.message}")
            }
        }
    }
    
    /**
     * Display current sync status - 
     */
    fun showSyncStatus() {
        val syncStatus = syncClockManager.getSyncStatus()
        val statistics = syncClockManager.getSyncStatistics()
        
        val statusMessage = buildString {
            appendLine("🕐 Clock Synchronization Status")
            appendLine("Synchronized: ${if (syncStatus.isSynchronized) "✅ Yes" else "❌ No"}")
            appendLine("Offset: ${syncStatus.clockOffsetMs}ms")
            appendLine("Last Sync: ${if (syncStatus.syncAge >= 0) "${syncStatus.syncAge}ms ago" else "Never"}")
            appendLine("Valid: ${if (syncClockManager.isSyncValid()) "✅ Yes" else "❌ No"}")
        }
        
        callback?.showToast(statusMessage, Toast.LENGTH_LONG)
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Sync status displayed: $statistics")
    }
    
    /**
     * Get calibration system status
     */
    fun getCalibrationStatus(): String {
        val syncStatus = syncClockManager.getSyncStatus()
        
        return buildString {
            append("Calibration System Status:\n")
            append("- Clock Synchronized: ${syncStatus.isSynchronized}\n")
            append("- Clock Offset: ${syncStatus.clockOffsetMs}ms\n")
            append("- Sync Valid: ${syncClockManager.isSyncValid()}\n")
            // TODO: Add calibration capture status
            append("- Last Calibration: TODO - implement calibration history tracking")
        }
    }
    
    /**
     * Reset calibration controller state
     */
    fun resetState() {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration controller state reset")
        // TODO: Reset calibration-specific state
    }
    
    /**
     * Cleanup resources
     */
    fun cleanup() {
        try {
            mediaActionSound?.release()
            mediaActionSound = null
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration controller resources cleaned up")
        } catch (e: Exception) {
            android.util.Log.w("CalibrationController", "[DEBUG_LOG] Error during cleanup: ${e.message}")
        }
    }
    
    /**
     * Check if sync is valid for calibration
     */
    fun isSyncValidForCalibration(): Boolean {
        return syncClockManager.isSyncValid()
    }
    
    /**
     * Get sync statistics for debugging
     */
    fun getSyncStatistics(): String {
        return syncClockManager.getSyncStatistics().toString()
    }
}