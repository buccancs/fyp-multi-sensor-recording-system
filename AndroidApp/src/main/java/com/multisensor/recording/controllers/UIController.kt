package com.multisensor.recording.controllers

import android.content.Context
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
 * TODO: Implement UI state persistence across configuration changes
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
    
    /**
     * Set the callback for UI events
     */
    fun setCallback(callback: UICallback) {
        this.callback = callback
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
                
                // Update consolidated status indicator components
                if (::pcStatusIndicator.isInitialized) {
                    pcStatusIndicator.setStatus(
                        if (state.isPcConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
                        "PC: ${if (state.isPcConnected) "Connected" else "Waiting for PC..."}"
                    )
                }
                
                if (::shimmerStatusIndicator.isInitialized) {
                    shimmerStatusIndicator.setStatus(
                        if (state.isShimmerConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
                        "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
                    )
                }
                
                if (::thermalStatusIndicator.isInitialized) {
                    thermalStatusIndicator.setStatus(
                        if (state.isThermalConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
                        "Thermal: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"
                    )
                }
                
                // Update legacy connection indicators for backward compatibility
                updateConnectionIndicator(callback?.getPcConnectionIndicator(), state.isPcConnected)
                updateConnectionIndicator(callback?.getShimmerConnectionIndicator(), state.isShimmerConnected)
                updateConnectionIndicator(callback?.getThermalConnectionIndicator(), state.isThermalConnected)
                
                // Update legacy connection status texts for backward compatibility
                callback?.getPcConnectionStatus()?.text = "PC: ${if (state.isPcConnected) "Connected" else "Waiting for PC..."}"
                callback?.getShimmerConnectionStatus()?.text = "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
                callback?.getThermalConnectionStatus()?.text = "Thermal: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"
                
                // Update battery level
                val batteryText = if (state.batteryLevel >= 0) {
                    "Battery: ${state.batteryLevel}%"
                } else {
                    "Battery: ---%"
                }
                callback?.getBatteryLevelText()?.text = batteryText
                
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
                
                // Update Shimmer status text
                val shimmerStatusText = when {
                    state.shimmerDeviceInfo != null -> {
                        "Shimmer GSR: ${state.shimmerDeviceInfo.deviceName} - Connected"
                    }
                    state.isShimmerConnected -> "Shimmer GSR: Connected"
                    else -> "Shimmer GSR: Disconnected"
                }
                callback?.getShimmerStatusText()?.let { textView ->
                    textView.text = shimmerStatusText
                    textView.setTextColor(
                        if (state.isShimmerConnected) Color.GREEN else Color.RED
                    )
                }
                
                callback?.onUIStateUpdated(state)
            } catch (e: Exception) {
                android.util.Log.e("UIController", "[DEBUG_LOG] Error updating UI from state: ${e.message}")
                callback?.onUIError("Failed to update UI: ${e.message}")
            }
        }
    }
    
    /**
     * Helper method to update connection indicators
     * Extracted from MainActivity.updateConnectionIndicator()
     */
    private fun updateConnectionIndicator(indicator: View?, isConnected: Boolean) {
        indicator?.setBackgroundColor(if (isConnected) Color.GREEN else Color.RED)
    }
    
    /**
     * Helper method to update recording indicator
     * Extracted from MainActivity.updateRecordingIndicator()
     */
    private fun updateRecordingIndicator(isRecording: Boolean) {
        callback?.getRecordingIndicator()?.setBackgroundColor(
            if (isRecording) Color.RED else Color.GRAY
        )
    }
    
    /**
     * Helper method to update streaming indicator and debug overlay
     * Extracted from MainActivity.updateStreamingIndicator()
     */
    private fun updateStreamingIndicator(isStreaming: Boolean, frameRate: Int, dataSize: String) {
        callback?.getStreamingIndicator()?.setBackgroundColor(
            if (isStreaming) Color.GREEN else Color.GRAY
        )
        
        if (isStreaming && frameRate > 0) {
            callback?.getStreamingDebugOverlay()?.let { overlay ->
                overlay.text = "Streaming: ${frameRate}fps ($dataSize)"
                overlay.visibility = View.VISIBLE
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
     * Data class for consolidated UI components
     */
    data class ConsolidatedUIComponents(
        val pcStatusIndicator: StatusIndicatorView?,
        val shimmerStatusIndicator: StatusIndicatorView?,
        val thermalStatusIndicator: StatusIndicatorView?,
        val recordingButtonPair: ActionButtonPair?
    )
    
    /**
     * Get UI controller status for debugging
     */
    fun getUIStatus(): String {
        return buildString {
            append("UI Controller Status:\n")
            append("- PC Status Indicator: ${if (::pcStatusIndicator.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- Shimmer Status Indicator: ${if (::shimmerStatusIndicator.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- Thermal Status Indicator: ${if (::thermalStatusIndicator.isInitialized) "Initialized" else "Not initialized"}\n")
            append("- Recording Button Pair: ${if (::recordingButtonPair.isInitialized) "Initialized" else "Not initialized"}\n")
            // TODO: Add more UI status information
            append("- Callback Set: ${callback != null}")
        }
    }
    
    /**
     * Reset UI controller state
     */
    fun resetState() {
        android.util.Log.d("UIController", "[DEBUG_LOG] UI controller state reset")
        // TODO: Reset UI-specific state if needed
    }
    
    /**
     * Cleanup UI resources
     */
    fun cleanup() {
        try {
            // TODO: Cleanup UI resources if needed
            callback = null
            android.util.Log.d("UIController", "[DEBUG_LOG] UI controller resources cleaned up")
        } catch (e: Exception) {
            android.util.Log.w("UIController", "[DEBUG_LOG] Error during UI cleanup: ${e.message}")
        }
    }
    
    /**
     * Set click listeners for recording button pair
     * TODO: This should be called by the coordinator during initialization
     */
    fun setRecordingButtonListeners(startAction: (View) -> Unit, stopAction: (View) -> Unit) {
        if (::recordingButtonPair.isInitialized) {
            recordingButtonPair.setOnClickListeners(startAction, stopAction)
            android.util.Log.d("UIController", "[DEBUG_LOG] Recording button listeners set")
        } else {
            android.util.Log.w("UIController", "[DEBUG_LOG] Cannot set listeners - recording button pair not initialized")
        }
    }
}