package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.content.Context
import android.content.SharedPreferences
import android.graphics.Color
import android.view.View
import android.widget.TextView
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.SessionDisplayInfo
import com.multisensor.recording.ui.components.StatusIndicatorView
import com.multisensor.recording.ui.components.ActionButtonPair
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all UI management and component logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * Manages UI component initialization, state updates, and visual indicators.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for UI management scenarios
 * TODO: Add support for dynamic theming and accessibility features
 * TODO: Implement UI component validation and error handling
 */
@Singleton
class UIController @Inject constructor() {
    
    /**
     * Interface for UI-related callbacks to the UI layer
     */
    interface UICallback {
        fun onUIComponentsInitialized()
        fun onUIStateUpdated(state: MainUiState)
        fun onUIError(message: String)
        fun updateStatusText(text: String)
        fun showToast(message: String, duration: Int = android.widget.Toast.LENGTH_SHORT)
        fun runOnUiThread(action: () -> Unit)
        fun getContext(): Context
        fun getStatusText(): TextView?
        fun getStartRecordingButton(): View?
        fun getStopRecordingButton(): View?
        fun getCalibrationButton(): View?
        fun getPcConnectionIndicator(): View?
        fun getShimmerConnectionIndicator(): View?
        fun getThermalConnectionIndicator(): View?
        fun getPcConnectionStatus(): TextView?
        fun getShimmerConnectionStatus(): TextView?
        fun getThermalConnectionStatus(): TextView?
        fun getBatteryLevelText(): TextView?
        fun getRecordingIndicator(): View?
        fun getStreamingIndicator(): View?
        fun getStreamingLabel(): View?
        fun getStreamingDebugOverlay(): TextView?
        fun getRequestPermissionsButton(): View?
        fun getShimmerStatusText(): TextView?
    }
    
    private var callback: UICallback? = null
    
    // UI Components for consolidation
    private lateinit var pcStatusIndicator: StatusIndicatorView
    private lateinit var shimmerStatusIndicator: StatusIndicatorView
    private lateinit var thermalStatusIndicator: StatusIndicatorView
    private lateinit var recordingButtonPair: ActionButtonPair
    
    // SharedPreferences for UI state persistence
    private var sharedPreferences: SharedPreferences? = null
    
    companion object {
        private const val PREFS_NAME = "ui_controller_prefs"
        private const val KEY_LAST_BATTERY_LEVEL = "last_battery_level"
        private const val KEY_PC_CONNECTION_STATUS = "pc_connection_status"
        private const val KEY_SHIMMER_CONNECTION_STATUS = "shimmer_connection_status"
        private const val KEY_THERMAL_CONNECTION_STATUS = "thermal_connection_status"
        private const val KEY_RECORDING_STATE = "recording_state"
        private const val KEY_STREAMING_STATE = "streaming_state"
        private const val KEY_UI_THEME_MODE = "ui_theme_mode"
        private const val KEY_ACCESSIBILITY_MODE = "accessibility_mode"
        private const val KEY_HIGH_CONTRAST_MODE = "high_contrast_mode"
    }
    
    /**
     * Set the callback for UI events and initialize state persistence
     */
    fun setCallback(callback: UICallback) {
        this.callback = callback
        
        // Initialize SharedPreferences for UI state persistence
        val context = callback.getContext()
        initializeUIStatePersistence(context)
    }
    
    /**
     * Initialize SharedPreferences for UI state persistence
     */
    private fun initializeUIStatePersistence(context: Context) {
        try {
            sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            android.util.Log.d("UIController", "[DEBUG_LOG] UI state persistence initialized")
        } catch (e: Exception) {
            android.util.Log.e("UIController", "[DEBUG_LOG] Failed to initialize UI state persistence: ${e.message}")
        }
    }
    
    /**
     * Save UI state to SharedPreferences
     */
    private fun saveUIState(state: MainUiState) {
        sharedPreferences?.edit()?.apply {
            putInt(KEY_LAST_BATTERY_LEVEL, state.batteryLevel)
            putBoolean(KEY_PC_CONNECTION_STATUS, state.isPcConnected)
            putBoolean(KEY_SHIMMER_CONNECTION_STATUS, state.isShimmerConnected)
            putBoolean(KEY_THERMAL_CONNECTION_STATUS, state.isThermalConnected)
            putBoolean(KEY_RECORDING_STATE, state.isRecording)
            putBoolean(KEY_STREAMING_STATE, state.isStreaming)
            apply()
        }
    }
    
    /**
     * Get saved UI state from SharedPreferences
     */
    fun getSavedUIState(): SavedUIState {
        return sharedPreferences?.let { prefs ->
            SavedUIState(
                lastBatteryLevel = prefs.getInt(KEY_LAST_BATTERY_LEVEL, -1),
                isPcConnected = prefs.getBoolean(KEY_PC_CONNECTION_STATUS, false),
                isShimmerConnected = prefs.getBoolean(KEY_SHIMMER_CONNECTION_STATUS, false),
                isThermalConnected = prefs.getBoolean(KEY_THERMAL_CONNECTION_STATUS, false),
                wasRecording = prefs.getBoolean(KEY_RECORDING_STATE, false),
                wasStreaming = prefs.getBoolean(KEY_STREAMING_STATE, false),
                themeMode = prefs.getString(KEY_UI_THEME_MODE, "default") ?: "default",
                accessibilityMode = prefs.getBoolean(KEY_ACCESSIBILITY_MODE, false),
                highContrastMode = prefs.getBoolean(KEY_HIGH_CONTRAST_MODE, false)
            )
        } ?: SavedUIState()
    }
    
    /**
     * Initialize consolidated UI components
     * Extracted from MainActivity.initializeUIComponents()
     */
    fun initializeUIComponents() {
        android.util.Log.d("UIController", "[DEBUG_LOG] Initializing consolidated UI components")
        
        try {
            val context = callback?.getContext() ?: throw IllegalStateException("Context not available")
            
            // Initialize StatusIndicatorView components
            pcStatusIndicator = StatusIndicatorView(context).apply {
                setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "PC: Waiting for PC...")
                setTextColor(android.R.color.white)
            }
            
            shimmerStatusIndicator = StatusIndicatorView(context).apply {
                setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Shimmer: Disconnected")
                setTextColor(android.R.color.white)
            }
            
            thermalStatusIndicator = StatusIndicatorView(context).apply {
                setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Thermal: Disconnected")
                setTextColor(android.R.color.white)
            }
            
            // Initialize ActionButtonPair for recording controls
            recordingButtonPair = ActionButtonPair(context).apply {
                setButtons("Start Recording", "Stop Recording")
                // Note: Click listeners will be set by the coordinator
                setButtonsEnabled(true, false) // Initially only start is enabled
            }
            
            callback?.onUIComponentsInitialized()
            android.util.Log.d("UIController", "[DEBUG_LOG] Consolidated UI components initialized successfully")
        } catch (e: Exception) {
            android.util.Log.e("UIController", "[DEBUG_LOG] Failed to initialize UI components: ${e.message}")
            callback?.onUIError("Failed to initialize UI components: ${e.message}")
        }
    }
    
    /**
     * Update all UI elements from the centralized UiState
     * Extracted from MainActivity.updateUIFromState()
     */
    fun updateUIFromState(state: MainUiState) {
        android.util.Log.d("UIController", "[DEBUG_LOG] Updating UI from centralized state")
        
        callback?.runOnUiThread {
            try {
                // Save state for persistence across configuration changes
                saveUIState(state)
                
                // Update status text
                callback?.getStatusText()?.text = state.statusText
                
                // Update consolidated recording controls
                if (::recordingButtonPair.isInitialized) {
                    recordingButtonPair.setButtonsEnabled(state.canStartRecording, state.canStopRecording)
                }
                
                // Update legacy recording controls for backward compatibility
                callback?.getStartRecordingButton()?.isEnabled = state.canStartRecording
                callback?.getStopRecordingButton()?.isEnabled = state.canStopRecording
                
                // Update calibration button
                callback?.getCalibrationButton()?.isEnabled = state.canRunCalibration
                
                // Update consolidated status indicator components with accessibility
                updateStatusIndicatorsWithAccessibility(state)
                
                // Update legacy connection indicators for backward compatibility
                updateConnectionIndicator(callback?.getPcConnectionIndicator(), state.isPcConnected)
                updateConnectionIndicator(callback?.getShimmerConnectionIndicator(), state.isShimmerConnected)
                updateConnectionIndicator(callback?.getThermalConnectionIndicator(), state.isThermalConnected)
                
                // Update legacy connection status texts for backward compatibility
                callback?.getPcConnectionStatus()?.text = "PC: ${if (state.isPcConnected) "Connected" else "Waiting for PC..."}"
                callback?.getShimmerConnectionStatus()?.text = "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
                callback?.getThermalConnectionStatus()?.text = "Thermal: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"
                
                // Update battery level with color coding
                updateBatteryLevelDisplay(state.batteryLevel)
                
                // Update recording indicator
                updateRecordingIndicator(state.isRecording)
                
                // Update streaming indicator and debug overlay
                updateStreamingIndicator(state.isStreaming, state.streamingFrameRate, state.streamingDataSize)
                
                // Update permissions button visibility
                callback?.getRequestPermissionsButton()?.visibility = if (state.showPermissionsButton) View.VISIBLE else View.GONE
                
                // Handle error messages
                state.errorMessage?.let { errorMsg ->
                    if (state.showErrorDialog) {
                        callback?.showToast(errorMsg, android.widget.Toast.LENGTH_LONG)
                        // TODO: Clear error in ViewModel after showing
                    }
                }
                
                // Update session information if available
                state.currentSessionInfo?.let { sessionInfo ->
                    updateSessionInfoDisplay(sessionInfo)
                }
                
                // Update Shimmer status text with accessibility
                updateShimmerStatusWithAccessibility(state)
                
                callback?.onUIStateUpdated(state)
            } catch (e: Exception) {
                android.util.Log.e("UIController", "[DEBUG_LOG] Error updating UI from state: ${e.message}")
                callback?.onUIError("Failed to update UI: ${e.message}")
            }
        }
    }
    
    /**
     * Update status indicators with accessibility features
     */
    private fun updateStatusIndicatorsWithAccessibility(state: MainUiState) {
        val savedState = getSavedUIState()
        val isHighContrast = savedState.highContrastMode
        val isAccessibilityMode = savedState.accessibilityMode
        
        if (::pcStatusIndicator.isInitialized) {
            pcStatusIndicator.setStatus(
                if (state.isPcConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
                "PC: ${if (state.isPcConnected) "Connected" else "Waiting for PC..."}"
            )
            
            // Apply accessibility enhancements
            if (isAccessibilityMode) {
                pcStatusIndicator.contentDescription = "PC connection status: ${if (state.isPcConnected) "Connected" else "Disconnected"}"
            }
        }
        
        if (::shimmerStatusIndicator.isInitialized) {
            shimmerStatusIndicator.setStatus(
                if (state.isShimmerConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
                "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
            )
            
            if (isAccessibilityMode) {
                shimmerStatusIndicator.contentDescription = "Shimmer sensor status: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
            }
        }
        
        if (::thermalStatusIndicator.isInitialized) {
            thermalStatusIndicator.setStatus(
                if (state.isThermalConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
                "Thermal: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"
            )
            
            if (isAccessibilityMode) {
                thermalStatusIndicator.contentDescription = "Thermal camera status: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"
            }
        }
    }
    
    /**
     * Update battery level display with color coding and accessibility
     */
    private fun updateBatteryLevelDisplay(batteryLevel: Int) {
        val savedState = getSavedUIState()
        val isHighContrast = savedState.highContrastMode
        
        val batteryText = if (batteryLevel >= 0) {
            "Battery: $batteryLevel%"
        } else {
            "Battery: ---%"
        }
        
        // Determine color based on battery level and accessibility mode
        val textColor = when {
            batteryLevel < 0 -> Color.WHITE
            isHighContrast -> {
                when {
                    batteryLevel > 50 -> Color.GREEN
                    batteryLevel > 20 -> Color.YELLOW
                    else -> Color.RED
                }
            }
            else -> {
                when {
                    batteryLevel > 50 -> Color.parseColor("#4CAF50") // Softer green
                    batteryLevel > 20 -> Color.parseColor("#FF9800") // Orange
                    else -> Color.parseColor("#F44336") // Red
                }
            }
        }
        
        callback?.getBatteryLevelText()?.let { textView ->
            textView.text = batteryText
            textView.setTextColor(textColor)
            
            if (savedState.accessibilityMode) {
                textView.contentDescription = "Battery level: $batteryLevel percent"
            }
        }
    }
    
    /**
     * Update Shimmer status with accessibility features
     */
    private fun updateShimmerStatusWithAccessibility(state: MainUiState) {
        val savedState = getSavedUIState()
        val isHighContrast = savedState.highContrastMode
        
        val shimmerStatusText = when {
            state.shimmerDeviceInfo != null -> {
                "Shimmer GSR: ${state.shimmerDeviceInfo.deviceName} - Connected"
            }
            state.isShimmerConnected -> "Shimmer GSR: Connected"
            else -> "Shimmer GSR: Disconnected"
        }
        
        val textColor = if (isHighContrast) {
            if (state.isShimmerConnected) Color.GREEN else Color.RED
        } else {
            if (state.isShimmerConnected) Color.parseColor("#4CAF50") else Color.parseColor("#F44336")
        }
        
        callback?.getShimmerStatusText()?.let { textView ->
            textView.text = shimmerStatusText
            textView.setTextColor(textColor)
            
            if (savedState.accessibilityMode) {
                textView.contentDescription = "Shimmer GSR sensor: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
            }
        }
    }
    
    /**
     * Helper method to update connection indicators
     * Extracted from MainActivity.updateConnectionIndicator()
     */
    private fun updateConnectionIndicator(indicator: View?, isConnected: Boolean) {
        val savedState = getSavedUIState()
        val isHighContrast = savedState.highContrastMode
        
        val color = if (isHighContrast) {
            if (isConnected) Color.GREEN else Color.RED
        } else {
            if (isConnected) Color.parseColor("#4CAF50") else Color.parseColor("#F44336")
        }
        
        indicator?.setBackgroundColor(color)
    }
    
    /**
     * Helper method to update recording indicator
     * Extracted from MainActivity.updateRecordingIndicator()
     */
    private fun updateRecordingIndicator(isRecording: Boolean) {
        val savedState = getSavedUIState()
        val isHighContrast = savedState.highContrastMode
        
        val color = if (isHighContrast) {
            if (isRecording) Color.RED else Color.GRAY
        } else {
            if (isRecording) Color.parseColor("#F44336") else Color.parseColor("#9E9E9E")
        }
        
        callback?.getRecordingIndicator()?.setBackgroundColor(color)
    }
    
    /**
     * Helper method to update streaming indicator and debug overlay
     * Extracted from MainActivity.updateStreamingIndicator()
     */
    private fun updateStreamingIndicator(isStreaming: Boolean, frameRate: Int, dataSize: String) {
        val savedState = getSavedUIState()
        val isHighContrast = savedState.highContrastMode
        
        val color = if (isHighContrast) {
            if (isStreaming) Color.GREEN else Color.GRAY
        } else {
            if (isStreaming) Color.parseColor("#4CAF50") else Color.parseColor("#9E9E9E")
        }
        
        callback?.getStreamingIndicator()?.setBackgroundColor(color)
        
        if (isStreaming && frameRate > 0) {
            callback?.getStreamingDebugOverlay()?.let { overlay ->
                overlay.text = "Streaming: ${frameRate}fps ($dataSize)"
                overlay.visibility = View.VISIBLE
                
                if (savedState.accessibilityMode) {
                    overlay.contentDescription = "Currently streaming at $frameRate frames per second, data size $dataSize"
                }
            }
            callback?.getStreamingLabel()?.visibility = View.VISIBLE
        } else {
            callback?.getStreamingDebugOverlay()?.visibility = View.GONE
            callback?.getStreamingLabel()?.visibility = View.GONE
        }
    }
    
    /**
     * Update UI with SessionDisplayInfo data from UI state
     * Extracted from MainActivity.updateSessionInfoDisplay()
     */
    private fun updateSessionInfoDisplay(sessionInfo: SessionDisplayInfo?) {
        if (sessionInfo != null) {
            // Update status text with session summary
            val sessionSummary = "Session ${sessionInfo.sessionId} - ${sessionInfo.status}"
            
            // For now, display session info in the existing status text
            // TODO: Add dedicated SessionInfo display components to layout
            if (sessionInfo.status == "Active") {
                callback?.updateStatusText("Active: $sessionSummary")
            } else {
                callback?.updateStatusText("Completed: $sessionSummary")
            }
            
            // Log detailed session information
            android.util.Log.d("UIController", "SessionInfo updated: $sessionSummary")
        } else {
            // No active session - handled by state management
            android.util.Log.d("UIController", "No active session info to display")
        }
    }
    
    /**
     * Get consolidated UI components for external access
     */
    fun getConsolidatedComponents(): ConsolidatedUIComponents {
        return ConsolidatedUIComponents(
            pcStatusIndicator = if (::pcStatusIndicator.isInitialized) pcStatusIndicator else null,
            shimmerStatusIndicator = if (::shimmerStatusIndicator.isInitialized) shimmerStatusIndicator else null,
            thermalStatusIndicator = if (::thermalStatusIndicator.isInitialized) thermalStatusIndicator else null,
            recordingButtonPair = if (::recordingButtonPair.isInitialized) recordingButtonPair else null
        )
    }
    
    /**
     * Set UI theme mode (light, dark, auto)
     */
    fun setThemeMode(themeMode: String) {
        sharedPreferences?.edit()?.apply {
            putString(KEY_UI_THEME_MODE, themeMode)
            apply()
        }
        android.util.Log.d("UIController", "[DEBUG_LOG] UI theme mode set to: $themeMode")
    }
    
    /**
     * Set accessibility mode
     */
    fun setAccessibilityMode(enabled: Boolean) {
        sharedPreferences?.edit()?.apply {
            putBoolean(KEY_ACCESSIBILITY_MODE, enabled)
            apply()
        }
        android.util.Log.d("UIController", "[DEBUG_LOG] Accessibility mode set to: $enabled")
    }
    
    /**
     * Set high contrast mode
     */
    fun setHighContrastMode(enabled: Boolean) {
        sharedPreferences?.edit()?.apply {
            putBoolean(KEY_HIGH_CONTRAST_MODE, enabled)
            apply()
        }
        android.util.Log.d("UIController", "[DEBUG_LOG] High contrast mode set to: $enabled")
    }
    
    /**
     * Data class for consolidated UI components
     */
    data class ConsolidatedUIComponents(
        val pcStatusIndicator: StatusIndicatorView?,
        val shimmerStatusIndicator: StatusIndicatorView?,
        val thermalStatusIndicator: StatusIndicatorView?,
        val recordingButtonPair: ActionButtonPair?
    )
    
    /**
     * Data class for saved UI state
     */
    data class SavedUIState(
        val lastBatteryLevel: Int = -1,
        val isPcConnected: Boolean = false,
        val isShimmerConnected: Boolean = false,
        val isThermalConnected: Boolean = false,
        val wasRecording: Boolean = false,
        val wasStreaming: Boolean = false,
        val themeMode: String = "default",
        val accessibilityMode: Boolean = false,
        val highContrastMode: Boolean = false
    )
    
    /**
     * Get UI controller status for debugging
     */
    fun getUIStatus(): String {
        val savedState = getSavedUIState()
        return buildString {
            append("UI Controller Status:\n")
            append("- PC Status Indicator: ${if (::pcStatusIndicator.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- Shimmer Status Indicator: ${if (::shimmerStatusIndicator.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- Thermal Status Indicator: ${if (::thermalStatusIndicator.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- Recording Button Pair: ${if (::recordingButtonPair.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- State Persistence: ${if (sharedPreferences != null) "Enabled" else "Disabled"}\n")
            append("- Theme Mode: ${savedState.themeMode}\n")
            append("- Accessibility Mode: ${savedState.accessibilityMode}\n")
            append("- High Contrast Mode: ${savedState.highContrastMode}\n")
            append("- Last Battery Level: ${savedState.lastBatteryLevel}%\n")
            append("- Callback Set: ${callback != null}")
        }
    }
    
    /**
     * Reset UI controller state
     */
    fun resetState() {
        // Clear persisted UI state
        sharedPreferences?.edit()?.clear()?.apply()
        android.util.Log.d("UIController", "[DEBUG_LOG] UI controller state reset and persisted state cleared")
    }
    
    /**
     * Cleanup UI resources
     */
    fun cleanup() {
        try {
            // Cleanup UI resources and clear callback
            callback = null
            sharedPreferences = null
            android.util.Log.d("UIController", "[DEBUG_LOG] UI controller resources cleaned up")
        } catch (e: Exception) {
            android.util.Log.w("UIController", "[DEBUG_LOG] Error during UI cleanup: ${e.message}")
        }
    }
    
    /**
     * Set click listeners for recording button pair
     */
    fun setRecordingButtonListeners(startAction: (View) -> Unit, stopAction: (View) -> Unit) {
        if (::recordingButtonPair.isInitialized) {
            recordingButtonPair.setOnClickListeners(startAction, stopAction)
            android.util.Log.d("UIController", "[DEBUG_LOG] Recording button listeners set")
        } else {
            android.util.Log.w("UIController", "[DEBUG_LOG] Cannot set listeners - recording button pair not initialized")
        }
    }
    
    /**
     * Apply UI theme based on saved preferences
     */
    fun applyThemeFromPreferences() {
        val savedState = getSavedUIState()
        android.util.Log.d("UIController", "[DEBUG_LOG] Applying UI theme: ${savedState.themeMode}, accessibility: ${savedState.accessibilityMode}, high contrast: ${savedState.highContrastMode}")
        
        // Theme application would be handled by the activity/fragment
        callback?.let { cb ->
            if (cb is Context) {
                // Future implementation: apply theme via context
                android.util.Log.d("UIController", "[DEBUG_LOG] Theme preferences ready for application")
            }
        }
    }
}