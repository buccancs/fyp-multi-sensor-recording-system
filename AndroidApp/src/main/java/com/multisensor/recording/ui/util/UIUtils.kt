package com.multisensor.recording.ui.util

import android.content.Context
import android.view.View
import android.widget.Toast
import androidx.core.content.ContextCompat
import com.multisensor.recording.R

/**
 * UI utility class that provides common UI operations and state management
 * functionality used across multiple fragments and activities. This centralizes
 * UI-related code to reduce duplication and ensure consistent behavior throughout
 * the application's navigation architecture.
 */
object UIUtils {

    /**
     * Update connection indicator with consistent styling and color scheme
     * across all fragments. This provides a standardized way to show device
     * connection status throughout the application.
     */
    fun updateConnectionIndicator(context: Context, indicator: View, isConnected: Boolean) {
        val colorRes = if (isConnected) {
            R.color.statusIndicatorConnected
        } else {
            R.color.statusIndicatorDisconnected
        }
        indicator.setBackgroundColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Update recording status indicator with consistent visual feedback
     * for recording state changes. This ensures uniform recording status
     * presentation across different interface components.
     */
    fun updateRecordingIndicator(context: Context, indicator: View, isRecording: Boolean) {
        val colorRes = if (isRecording) {
            R.color.recordingActive
        } else {
            R.color.recordingInactive
        }
        indicator.setBackgroundColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Show standardized status messages with consistent duration and formatting.
     * This provides a unified way to display user feedback across all fragments
     * and activities in the navigation system.
     */
    fun showStatusMessage(context: Context, message: String, isLongDuration: Boolean = false) {
        val duration = if (isLongDuration) Toast.LENGTH_LONG else Toast.LENGTH_SHORT
        Toast.makeText(context, message, duration).show()
    }

    /**
     * Get standardized connection status text based on device state.
     * This ensures consistent status messaging across all interface components.
     */
    fun getConnectionStatusText(deviceName: String, isConnected: Boolean): String {
        return "$deviceName: ${if (isConnected) "Connected" else getDisconnectedText(deviceName)}"
    }

    /**
     * Get device-specific disconnected status text that provides appropriate
     * context for different types of devices and their connection states.
     */
    private fun getDisconnectedText(deviceName: String): String {
        return when (deviceName.lowercase()) {
            "pc" -> "Waiting..."
            "shimmer" -> "Off"
            "thermal" -> "Off"
            else -> "Disconnected"
        }
    }

    /**
     * Format battery level text with consistent presentation across the interface.
     * This provides standardized battery level display formatting for all components.
     */
    fun formatBatteryText(batteryLevel: Int): String {
        return if (batteryLevel >= 0) {
            "Battery: $batteryLevel%"
        } else {
            "Battery: ---%"
        }
    }

    /**
     * Format streaming information text with consistent presentation.
     * This standardizes the display of streaming status and performance metrics.
     */
    fun formatStreamingText(isStreaming: Boolean, frameRate: Int, dataSize: String): String {
        return if (isStreaming && frameRate > 0) {
            "Streaming: ${frameRate}fps ($dataSize)"
        } else {
            "Ready to stream"
        }
    }

    /**
     * Get standardized recording status text based on current state.
     * This ensures consistent recording status messaging across all fragments.
     */
    fun getRecordingStatusText(isRecording: Boolean): String {
        return if (isRecording) "Recording in progress..." else "Ready to record"
    }

    /**
     * Apply consistent styling to buttons based on their role and state.
     * This provides standardized button appearance throughout the navigation system.
     */
    fun styleButton(context: Context, button: View, buttonType: ButtonType, isEnabled: Boolean = true) {
        val colorRes = when (buttonType) {
            ButtonType.PRIMARY -> R.color.colorSecondary  // Orange/blue for primary
            ButtonType.SUCCESS -> R.color.colorPrimary    // Green for success  
            ButtonType.DANGER -> R.color.recordingActive  // Red for danger
            ButtonType.SECONDARY -> R.color.textColorSecondary // Gray for secondary
        }
        
        button.setBackgroundColor(ContextCompat.getColor(context, colorRes))
        button.isEnabled = isEnabled
        button.alpha = if (isEnabled) 1.0f else 0.6f
    }

    /**
     * Enum defining standard button types for consistent styling across the application.
     */
    enum class ButtonType {
        PRIMARY,
        SUCCESS,
        DANGER,
        SECONDARY
    }

    /**
     * Set view visibility with fade animation for smooth UI transitions.
     * This provides consistent animation behavior across all interface components.
     */
    fun setViewVisibilityWithAnimation(view: View, isVisible: Boolean, duration: Long = 300) {
        if (isVisible) {
            view.visibility = View.VISIBLE
            view.animate()
                .alpha(1.0f)
                .setDuration(duration)
                .start()
        } else {
            view.animate()
                .alpha(0.0f)
                .setDuration(duration)
                .withEndAction {
                    view.visibility = View.GONE
                }
                .start()
        }
    }

    /**
     * Calculate appropriate timeout duration based on operation type.
     * This provides consistent timeout handling across different interface operations.
     */
    fun getOperationTimeout(operationType: OperationType): Long {
        return when (operationType) {
            OperationType.CONNECTION -> 10000L // 10 seconds
            OperationType.RECORDING_START -> 5000L // 5 seconds
            OperationType.RECORDING_STOP -> 3000L // 3 seconds
            OperationType.CALIBRATION -> 30000L // 30 seconds
            OperationType.FILE_OPERATION -> 15000L // 15 seconds
        }
    }

    /**
     * Enum defining operation types for timeout calculations.
     */
    enum class OperationType {
        CONNECTION,
        RECORDING_START,
        RECORDING_STOP,
        CALIBRATION,
        FILE_OPERATION
    }
}