package com.multisensor.recording.util

import android.content.Context
import android.widget.Toast

/**
 * Centralized toast message manager with ASCII-only messages.
 * Provides consistent user feedback across the application.
 */
object ToastManager {

    /**
     * Show a short informational message.
     */
    fun showMessage(context: Context, message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    /**
     * Show a long error message.
     */
    fun showError(context: Context, message: String) {
        Toast.makeText(context, message, Toast.LENGTH_LONG).show()
    }

    /**
     * Show a short success message.
     */
    fun showSuccess(context: Context, message: String) {
        Toast.makeText(context, "[SUCCESS] $message", Toast.LENGTH_SHORT).show()
    }

    /**
     * Show a warning message.
     */
    fun showWarning(context: Context, message: String) {
        Toast.makeText(context, "[WARNING] $message", Toast.LENGTH_LONG).show()
    }

    // Predefined ASCII-only messages for common scenarios
    object Messages {
        // Connection messages
        const val USB_DEVICE_DETECTED = "[USB] Device detected - Connecting automatically..."
        const val DEVICE_CONNECTION_SUCCESS = "All devices connected successfully!"
        const val DEVICE_CONNECTION_ERROR = "Connection Error"
        const val DEVICE_TROUBLESHOOTING = "[TROUBLESHOOTING] Check device connections and permissions"
        
        // Configuration messages
        const val CONFIG_RELOAD_SUCCESS = "Configuration reloaded successfully"
        const val CONFIG_RELOAD_FAILED = "Configuration reload failed"
        const val CONFIG_MANAGER_ERROR = "Configuration manager error"
        const val CONFIG_MANAGER_UNAVAILABLE = "Configuration manager not available"
        const val CONFIG_ERROR_RELOADING = "Error reloading configuration"
        
        // PC connection messages
        const val PC_CONNECTION_SUCCESS = "PC connection successful"
        const val PC_CONNECTION_FAILED = "PC connection failed - check server"
        
        // Permission messages
        const val PERMISSIONS_GRANTED = "All permissions granted"
        const val PERMISSIONS_DENIED = "Permissions denied"
        
        // General messages
        const val FEATURE_COMING_SOON = "Feature coming soon"
        const val OPERATION_SUCCESSFUL = "Operation completed successfully"
        const val OPERATION_FAILED = "Operation failed"
        const val EXPORT_FUNCTIONALITY_COMING_SOON = "Export functionality coming soon"
    }
}