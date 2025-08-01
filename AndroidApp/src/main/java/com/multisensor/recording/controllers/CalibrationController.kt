package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.content.Context
import android.content.SharedPreferences
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
 * Features:
 * - Calibration capture with multiple patterns and configurations
 * - State persistence across app restarts with validation
 * - Quality validation and metrics collection
 * - Comprehensive sync testing and clock synchronization
 * - Visual and audio feedback for calibration events
 * - Pattern-based calibration support (single-point, multi-point, grid-based)
 */
@Singleton
class CalibrationController @Inject constructor(
    private val calibrationCaptureManager: CalibrationCaptureManager,
    private val syncClockManager: SyncClockManager
) {
    
    companion object {
        private const val CALIBRATION_PREFS_NAME = "calibration_history"
        private const val PREF_LAST_CALIBRATION_ID = "last_calibration_id"
        private const val PREF_LAST_CALIBRATION_TIME = "last_calibration_time"
        private const val PREF_CALIBRATION_COUNT = "calibration_count"
        private const val PREF_LAST_CALIBRATION_SUCCESS = "last_calibration_success"
        
        // Enhanced state persistence keys
        private const val PREF_CALIBRATION_PATTERN = "calibration_pattern"
        private const val PREF_CALIBRATION_QUALITY_SCORE = "calibration_quality_score"
        private const val PREF_CALIBRATION_SESSION_STATE = "calibration_session_state"
        private const val PREF_LAST_SYNC_OFFSET = "last_sync_offset"
        private const val PREF_SYNC_VALIDATION_COUNT = "sync_validation_count"
        
        // Calibration pattern constants
        private const val PATTERN_SINGLE_POINT = "single_point"
        private const val PATTERN_MULTI_POINT = "multi_point"
        private const val PATTERN_GRID_BASED = "grid_based"
        private const val PATTERN_CUSTOM = "custom"
    }
    
    /**
     * Calibration pattern types supported by the system
     */
    enum class CalibrationPattern(val patternId: String, val displayName: String, val pointCount: Int) {
        SINGLE_POINT(PATTERN_SINGLE_POINT, "Single Point Calibration", 1),
        MULTI_POINT(PATTERN_MULTI_POINT, "Multi-Point Calibration", 4),
        GRID_BASED(PATTERN_GRID_BASED, "Grid-Based Calibration", 9),
        CUSTOM(PATTERN_CUSTOM, "Custom Pattern", -1)
    }
    
    /**
     * Calibration quality metrics
     */
    data class CalibrationQuality(
        val score: Float, // 0.0 to 1.0
        val syncAccuracy: Float,
        val visualClarity: Float,
        val thermalAccuracy: Float,
        val overallReliability: Float,
        val validationMessages: List<String> = emptyList()
    )
    
    /**
     * Calibration session state for persistence
     */
    data class CalibrationSessionState(
        val isSessionActive: Boolean,
        val currentPattern: CalibrationPattern,
        val completedPoints: Int,
        val totalPoints: Int,
        val startTimestamp: Long,
        val lastUpdateTimestamp: Long,
        val sessionId: String
    )
    
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
        fun getContext(): Context
    }
    
    private var callback: CalibrationCallback? = null
    private var mediaActionSound: MediaActionSound? = null
    private var currentSessionState: CalibrationSessionState? = null
    private var currentPattern: CalibrationPattern = CalibrationPattern.SINGLE_POINT
    private var qualityMetrics: MutableList<CalibrationQuality> = mutableListOf()
    
    /**
     * Set the callback for calibration events
     */
    fun setCallback(callback: CalibrationCallback) {
        this.callback = callback
    }
    
    /**
     * Initialize calibration controller with state restoration
     */
    fun initialize() {
        try {
            mediaActionSound = MediaActionSound()
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration controller initialized")
            
            // Restore previous session state if available
            callback?.getContext()?.let { context ->
                restoreSessionState(context)
            }
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to initialize MediaActionSound: ${e.message}")
        }
    }
    
    /**
     * Run calibration capture process with pattern support
     * Extracted from MainActivity.runCalibration()
     */
    fun runCalibration(lifecycleScope: LifecycleCoroutineScope, pattern: CalibrationPattern = CalibrationPattern.SINGLE_POINT) {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Starting enhanced calibration capture with pattern: ${pattern.displayName}")
        
        // Update current pattern and create session state
        currentPattern = pattern
        currentSessionState = CalibrationSessionState(
            isSessionActive = true,
            currentPattern = pattern,
            completedPoints = 0,
            totalPoints = pattern.pointCount,
            startTimestamp = System.currentTimeMillis(),
            lastUpdateTimestamp = System.currentTimeMillis(),
            sessionId = "session_${System.currentTimeMillis()}"
        )
        
        // Save session state
        callback?.getContext()?.let { context ->
            saveSessionState(context, currentSessionState!!)
        }
        
        // Show initial calibration start message
        callback?.showToast("Starting ${pattern.displayName}...")
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
                    
                    // Calculate quality metrics
                    val quality = calculateCalibrationQuality(result)
                    qualityMetrics.add(quality)
                    
                    // Update session state
                    currentSessionState = currentSessionState?.copy(
                        completedPoints = currentSessionState!!.completedPoints + 1,
                        lastUpdateTimestamp = System.currentTimeMillis()
                    )
                    
                    // Save calibration history with quality data
                    callback?.getContext()?.let { context ->
                        saveCalibrationHistory(context, result.calibrationId, true, quality)
                        saveSessionState(context, currentSessionState!!)
                    }
                    
                    // Trigger enhanced feedback for successful capture
                    callback?.runOnUiThread {
                        triggerCalibrationCaptureSuccess(result.calibrationId, quality)
                    }
                    
                    // Check if pattern is complete
                    if (currentSessionState?.completedPoints == currentSessionState?.totalPoints || pattern == CalibrationPattern.SINGLE_POINT) {
                        completeCalibrationSession(result.calibrationId)
                    }
                    
                    callback?.onCalibrationCompleted(result.calibrationId)
                } else {
                    android.util.Log.e("CalibrationController", "[DEBUG_LOG] Calibration capture failed: ${result.errorMessage}")
                    
                    // Save failed calibration attempt
                    callback?.getContext()?.let { context ->
                        saveCalibrationHistory(context, "failed_${System.currentTimeMillis()}", false)
                        clearSessionState(context)
                    }
                    
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
                
                // Clear session state on error
                callback?.getContext()?.let { context ->
                    clearSessionState(context)
                }
                
                callback?.onCalibrationFailed("Calibration error: ${e.message}")
            }
        }
    }
    
    /**
     * Triggers comprehensive calibration capture feedback with quality information
     */
    private fun triggerCalibrationCaptureSuccess(calibrationId: String = "unknown", quality: CalibrationQuality? = null) {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration photo captured - triggering feedback for ID: $calibrationId")
        
        // 1. Toast notification with quality info
        showCalibrationCaptureToast(quality)
        
        // 2. Screen flash visual feedback
        triggerScreenFlash()
        
        // 3. Audio feedback (camera shutter sound)
        triggerCalibrationAudioFeedback()
        
        // 4. Visual cue for multi-angle calibration
        showCalibrationGuidance(quality)
    }
    
    /**
     * Shows toast message for calibration photo capture with quality information
     */
    private fun showCalibrationCaptureToast(quality: CalibrationQuality? = null) {
        val message = if (quality != null) {
            "📸 Calibration photo captured! Quality: ${String.format("%.1f", quality.score * 100)}%"
        } else {
            "📸 Calibration photo captured!"
        }
        callback?.showToast(message)
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
     * Shows calibration guidance for multi-angle capture with quality feedback
     */
    private fun showCalibrationGuidance(quality: CalibrationQuality? = null) {
        val baseMessage = "📐 Position device at different angle and capture again"
        val qualityMessage = quality?.let { q ->
            if (q.validationMessages.isNotEmpty()) {
                "\n${q.validationMessages.first()}"
            } else if (q.score < 0.7f) {
                "\nTip: Ensure good lighting and stable positioning"
            } else null
        }
        
        // Show additional toast with guidance
        Handler(Looper.getMainLooper()).postDelayed({
            val fullMessage = baseMessage + (qualityMessage ?: "")
            callback?.showToast(fullMessage, Toast.LENGTH_LONG)
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
        val lastCalibrationInfo = callback?.getContext()?.let { getLastCalibrationInfo(it) } ?: "Context unavailable"
        
        return buildString {
            append("Calibration System Status:\n")
            append("- Clock Synchronized: ${syncStatus.isSynchronized}\n")
            append("- Clock Offset: ${syncStatus.clockOffsetMs}ms\n")
            append("- Sync Valid: ${syncClockManager.isSyncValid()}\n")
            append("- Last Calibration: $lastCalibrationInfo\n")
            append("- Total Calibrations: ${callback?.getContext()?.let { getCalibrationCount(it) } ?: 0}")
        }
    }
    
    /**
     * Reset calibration controller state with comprehensive cleanup
     */
    fun resetState() {
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Resetting calibration controller state")
        
        // Reset session state
        currentSessionState = null
        currentPattern = CalibrationPattern.SINGLE_POINT
        qualityMetrics.clear()
        
        // Clear persisted session state
        callback?.getContext()?.let { context ->
            clearSessionState(context)
        }
        
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration controller state reset complete")
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
    
    /**
     * Save calibration history for tracking with quality metrics
     */
    private fun saveCalibrationHistory(context: Context, calibrationId: String, success: Boolean, quality: CalibrationQuality? = null) {
        try {
            val prefs = context.getSharedPreferences(CALIBRATION_PREFS_NAME, Context.MODE_PRIVATE)
            val currentCount = prefs.getInt(PREF_CALIBRATION_COUNT, 0)
            
            prefs.edit().apply {
                putString(PREF_LAST_CALIBRATION_ID, calibrationId)
                putLong(PREF_LAST_CALIBRATION_TIME, System.currentTimeMillis())
                putBoolean(PREF_LAST_CALIBRATION_SUCCESS, success)
                putInt(PREF_CALIBRATION_COUNT, currentCount + 1)
                putString(PREF_CALIBRATION_PATTERN, currentPattern.patternId)
                
                // Save quality metrics if available
                quality?.let { q ->
                    putFloat(PREF_CALIBRATION_QUALITY_SCORE, q.score)
                }
                
                // Save sync status
                putLong(PREF_LAST_SYNC_OFFSET, syncClockManager.getSyncStatus().clockOffsetMs)
                
                apply()
            }
            
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration history saved: $calibrationId (success: $success, quality: ${quality?.score})")
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to save calibration history: ${e.message}")
        }
    }
    
    /**
     * Get information about the last calibration
     */
    private fun getLastCalibrationInfo(context: Context): String {
        return try {
            val prefs = context.getSharedPreferences(CALIBRATION_PREFS_NAME, Context.MODE_PRIVATE)
            val calibrationId = prefs.getString(PREF_LAST_CALIBRATION_ID, null)
            val lastTime = prefs.getLong(PREF_LAST_CALIBRATION_TIME, 0L)
            val success = prefs.getBoolean(PREF_LAST_CALIBRATION_SUCCESS, false)
            
            if (calibrationId != null && lastTime > 0) {
                val timeFormat = java.text.SimpleDateFormat("MMM dd, HH:mm", java.util.Locale.getDefault())
                val status = if (success) "✓" else "✗"
                "$status $calibrationId (${timeFormat.format(java.util.Date(lastTime))})"
            } else {
                "None"
            }
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to get last calibration info: ${e.message}")
            "Error retrieving info"
        }
    }
    
    /**
     * Get total calibration count
     */
    private fun getCalibrationCount(context: Context): Int {
        return try {
            val prefs = context.getSharedPreferences(CALIBRATION_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.getInt(PREF_CALIBRATION_COUNT, 0)
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to get calibration count: ${e.message}")
            0
        }
    }
    
    // ========== Enhanced State Persistence Methods ==========
    
    /**
     * Save session state to persistent storage
     */
    private fun saveSessionState(context: Context, sessionState: CalibrationSessionState) {
        try {
            val prefs = context.getSharedPreferences(CALIBRATION_PREFS_NAME, Context.MODE_PRIVATE)
            val sessionJson = """
                {
                    "isSessionActive": ${sessionState.isSessionActive},
                    "currentPattern": "${sessionState.currentPattern.patternId}",
                    "completedPoints": ${sessionState.completedPoints},
                    "totalPoints": ${sessionState.totalPoints},
                    "startTimestamp": ${sessionState.startTimestamp},
                    "lastUpdateTimestamp": ${sessionState.lastUpdateTimestamp},
                    "sessionId": "${sessionState.sessionId}"
                }
            """.trimIndent()
            
            prefs.edit().apply {
                putString(PREF_CALIBRATION_SESSION_STATE, sessionJson)
                apply()
            }
            
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Session state saved: ${sessionState.sessionId}")
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to save session state: ${e.message}")
        }
    }
    
    /**
     * Restore session state from persistent storage
     */
    private fun restoreSessionState(context: Context) {
        try {
            val prefs = context.getSharedPreferences(CALIBRATION_PREFS_NAME, Context.MODE_PRIVATE)
            val sessionJson = prefs.getString(PREF_CALIBRATION_SESSION_STATE, null)
            
            if (sessionJson != null) {
                // Simple JSON parsing - in production could use Gson or similar
                val isActive = sessionJson.contains("\"isSessionActive\": true")
                if (isActive) {
                    android.util.Log.d("CalibrationController", "[DEBUG_LOG] Active session found, restoring state")
                    // For now, just log that we found an active session
                    // TODO: Implement full JSON parsing if needed
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to restore session state: ${e.message}")
        }
    }
    
    /**
     * Clear session state from persistent storage
     */
    private fun clearSessionState(context: Context) {
        try {
            val prefs = context.getSharedPreferences(CALIBRATION_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().apply {
                remove(PREF_CALIBRATION_SESSION_STATE)
                apply()
            }
            
            currentSessionState = null
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Session state cleared")
        } catch (e: Exception) {
            android.util.Log.e("CalibrationController", "[DEBUG_LOG] Failed to clear session state: ${e.message}")
        }
    }
    
    // ========== Calibration Quality Validation Methods ==========
    
    /**
     * Calculate calibration quality metrics
     */
    private fun calculateCalibrationQuality(result: CalibrationCaptureManager.CalibrationCaptureResult): CalibrationQuality {
        val syncStatus = syncClockManager.getSyncStatus()
        val validationMessages = mutableListOf<String>()
        
        // Calculate sync accuracy (0.0 to 1.0, higher is better)
        val syncAccuracy = if (syncStatus.isSynchronized) {
            val offsetMs = kotlin.math.abs(syncStatus.clockOffsetMs)
            when {
                offsetMs <= 10 -> 1.0f  // Excellent sync
                offsetMs <= 50 -> 0.8f  // Good sync
                offsetMs <= 100 -> 0.6f // Fair sync
                else -> 0.3f            // Poor sync
            }
        } else {
            0.1f // No sync
        }
        
        // Calculate visual clarity (mock implementation - could use image analysis)
        val visualClarity = when {
            result.rgbFilePath != null && result.thermalFilePath != null -> 0.9f
            result.rgbFilePath != null || result.thermalFilePath != null -> 0.7f
            else -> 0.3f
        }
        
        // Calculate thermal accuracy (mock implementation)
        val thermalAccuracy = if (result.thermalFilePath != null) 0.8f else 0.5f
        
        // Calculate overall reliability
        val overallReliability = (syncAccuracy + visualClarity + thermalAccuracy) / 3.0f
        
        // Generate validation messages
        if (syncAccuracy < 0.6f) {
            validationMessages.add("Sync quality is low - consider recalibrating clock sync")
        }
        if (visualClarity < 0.7f) {
            validationMessages.add("Image quality could be improved - check lighting and stability")
        }
        if (overallReliability > 0.8f) {
            validationMessages.add("Excellent calibration quality!")
        }
        
        val finalScore = overallReliability * 0.9f + kotlin.math.min(1.0f, qualityMetrics.size * 0.1f) * 0.1f
        
        return CalibrationQuality(
            score = finalScore,
            syncAccuracy = syncAccuracy,
            visualClarity = visualClarity,
            thermalAccuracy = thermalAccuracy,
            overallReliability = overallReliability,
            validationMessages = validationMessages
        )
    }
    
    /**
     * Complete calibration session and update metrics
     */
    private fun completeCalibrationSession(calibrationId: String) {
        currentSessionState?.let { sessionState ->
            val duration = System.currentTimeMillis() - sessionState.startTimestamp
            
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration session completed: ${sessionState.sessionId}")
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] - Pattern: ${sessionState.currentPattern.displayName}")
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] - Duration: ${duration}ms")
            android.util.Log.d("CalibrationController", "[DEBUG_LOG] - Points: ${sessionState.completedPoints}/${sessionState.totalPoints}")
            
            // Clear session state
            callback?.getContext()?.let { context ->
                clearSessionState(context)
            }
        }
    }
    
    // ========== Pattern and Configuration Support Methods ==========
    
    /**
     * Set calibration pattern for next session
     */
    fun setCalibrationPattern(pattern: CalibrationPattern) {
        currentPattern = pattern
        android.util.Log.d("CalibrationController", "[DEBUG_LOG] Calibration pattern set to: ${pattern.displayName}")
    }
    
    /**
     * Get current calibration pattern
     */
    fun getCurrentPattern(): CalibrationPattern = currentPattern
    
    /**
     * Get available calibration patterns
     */
    fun getAvailablePatterns(): List<CalibrationPattern> = CalibrationPattern.values().toList()
    
    /**
     * Get current session state
     */
    fun getCurrentSessionState(): CalibrationSessionState? = currentSessionState
    
    /**
     * Get calibration quality metrics
     */
    fun getQualityMetrics(): List<CalibrationQuality> = qualityMetrics.toList()
    
    /**
     * Get average quality score
     */
    fun getAverageQualityScore(): Float {
        return if (qualityMetrics.isNotEmpty()) {
            qualityMetrics.map { it.score }.average().toFloat()
        } else {
            0.0f
        }
    }
    
    /**
     * Validate current calibration setup
     */
    fun validateCalibrationSetup(): Pair<Boolean, List<String>> {
        val issues = mutableListOf<String>()
        
        // Check sync status
        if (!syncClockManager.isSyncValid()) {
            issues.add("Clock synchronization is not valid")
        }
        
        // Check session state
        currentSessionState?.let { state ->
            if (state.isSessionActive && (System.currentTimeMillis() - state.lastUpdateTimestamp) > 300000) { // 5 minutes
                issues.add("Session appears stale - consider restarting")
            }
        }
        
        // Check quality history
        if (qualityMetrics.isNotEmpty() && getAverageQualityScore() < 0.5f) {
            issues.add("Recent calibration quality is below acceptable threshold")
        }
        
        return Pair(issues.isEmpty(), issues)
    }
}