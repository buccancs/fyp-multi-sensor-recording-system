package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.app.Activity
import android.content.Context
import android.widget.Toast
import com.multisensor.recording.managers.PermissionManager
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all permission-related logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for all permission scenarios
 * TODO: Implement permission state persistence across app restarts
 */
@Singleton
class PermissionController @Inject constructor(
    private val permissionManager: PermissionManager
) {
    
    /**
     * Interface for permission-related callbacks to the UI layer
     */
    interface PermissionCallback {
        fun onAllPermissionsGranted()
        fun onPermissionsTemporarilyDenied(deniedPermissions: List<String>, grantedCount: Int, totalCount: Int)
        fun onPermissionsPermanentlyDenied(deniedPermissions: List<String>)
        fun onPermissionCheckStarted()
        fun onPermissionRequestCompleted()
        fun updateStatusText(text: String)
        fun showPermissionButton(show: Boolean)
    }
    
    private var callback: PermissionCallback? = null
    private var hasCheckedPermissionsOnStartup = false
    private var permissionRetryCount = 0
    
    /**
     * Set the callback for permission events
     */
    fun setCallback(callback: PermissionCallback) {
        this.callback = callback
    }
    
    /**
     * Check if all required permissions are granted
     */
    fun areAllPermissionsGranted(context: Context): Boolean {
        return permissionManager.areAllPermissionsGranted(context)
    }
    
    /**
     * Main permission checking logic extracted from MainActivity
     */
    fun checkPermissions(context: Context) {
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Starting permission check via PermissionManager...")
        
        callback?.onPermissionCheckStarted()
        
        if (permissionManager.areAllPermissionsGranted(context)) {
            android.util.Log.d("PermissionController", "[DEBUG_LOG] All permissions already granted")
            callback?.onAllPermissionsGranted()
        } else {
            android.util.Log.d("PermissionController", "[DEBUG_LOG] Requesting permissions via PermissionManager...")
            callback?.updateStatusText("Requesting permissions...")
            
            // Use PermissionManager for permission requests
            if (context is Activity) {
                permissionManager.requestPermissions(context, createPermissionManagerCallback())
            }
        }
        
        // Update permission button visibility based on current permission status
        updatePermissionButtonVisibility(context)
    }
    
    /**
     * Handle manual permission request initiated by user
     */
    fun requestPermissionsManually(context: Context) {
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Manual permission request initiated by user")
        
        // Reset the startup flag to allow permission checking again
        hasCheckedPermissionsOnStartup = false
        
        // Reset retry counter for fresh manual attempt
        permissionRetryCount = 0
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Reset permission retry counter to 0 for manual request")
        
        // Hide the button while processing
        callback?.showPermissionButton(false)
        callback?.updateStatusText("Requesting permissions...")
        
        // Call the same permission checking logic
        checkPermissions(context)
    }
    
    /**
     * Update permission button visibility based on current permission status
     */
    fun updatePermissionButtonVisibility(context: Context) {
        val allPermissionsGranted = permissionManager.areAllPermissionsGranted(context)
        
        if (!allPermissionsGranted) {
            android.util.Log.d("PermissionController", "[DEBUG_LOG] Showing permission request button - permissions missing")
            callback?.showPermissionButton(true)
        } else {
            android.util.Log.d("PermissionController", "[DEBUG_LOG] Hiding permission request button - all permissions granted")
            callback?.showPermissionButton(false)
        }
    }
    
    /**
     * Show message for temporarily denied permissions
     */
    private fun showTemporaryDenialMessage(
        context: Context,
        temporarilyDenied: List<String>,
        grantedCount: Int,
        totalCount: Int
    ) {
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Showing temporary denial message for ${temporarilyDenied.size} permissions")
        
        val message = buildString {
            append("Some permissions were denied but can be requested again.\n\n")
            append("Denied permissions:\n")
            append(temporarilyDenied.joinToString("\n") { "• ${getPermissionDisplayName(it)}" })
            append("\n\nYou can grant these permissions using the 'Request Permissions' button.")
        }
        
        Toast.makeText(context, message, Toast.LENGTH_LONG).show()
        
        callback?.updateStatusText("Permissions: $grantedCount/$totalCount granted - Some permissions denied")
        
        android.util.Log.i("PermissionController", "Temporary permission denial: ${temporarilyDenied.joinToString(", ")}")
    }
    
    /**
     * Show message for permanently denied permissions
     */
    private fun showPermanentlyDeniedMessage(context: Context, permanentlyDenied: List<String>) {
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Showing permanently denied permissions message")
        
        val message = buildString {
            append("Some permissions have been permanently denied. ")
            append("Please enable them manually in Settings > Apps > Multi-Sensor Recording > Permissions.\n\n")
            append("Permanently denied permissions:\n")
            append(permanentlyDenied.joinToString("\n") { "• ${getPermissionDisplayName(it)}" })
        }
        
        Toast.makeText(context, message, Toast.LENGTH_LONG).show()
        
        callback?.updateStatusText("Permissions required - Please enable in Settings")
        
        // Log the permanently denied permissions
        android.util.Log.w("PermissionController", "Permanently denied permissions: ${permanentlyDenied.joinToString(", ")}")
    }
    
    /**
     * Get display name for permission
     */
    private fun getPermissionDisplayName(permission: String): String {
        return permissionManager.getPermissionDisplayName(permission)
    }
    
    /**
     * Create callback for PermissionManager
     */
    private fun createPermissionManagerCallback(): PermissionManager.PermissionCallback {
        return object : PermissionManager.PermissionCallback {
            override fun onAllPermissionsGranted() {
                android.util.Log.d("PermissionController", "[DEBUG_LOG] All permissions granted callback received")
                callback?.onAllPermissionsGranted()
                callback?.onPermissionRequestCompleted()
            }
            
            override fun onPermissionsTemporarilyDenied(
                deniedPermissions: List<String>,
                grantedCount: Int,
                totalCount: Int
            ) {
                android.util.Log.d("PermissionController", "[DEBUG_LOG] Temporary denial callback received")
                // Show message to user about temporarily denied permissions
                callback?.let { cb ->
                    if (cb is Context) {
                        showTemporaryDenialMessage(cb as Context, deniedPermissions, grantedCount, totalCount)
                    }
                }
                callback?.onPermissionsTemporarilyDenied(deniedPermissions, grantedCount, totalCount)
                callback?.onPermissionRequestCompleted()
            }
            
            override fun onPermissionsPermanentlyDenied(deniedPermissions: List<String>) {
                android.util.Log.d("PermissionController", "[DEBUG_LOG] Permanent denial callback received")
                // Show message to user about permanently denied permissions
                callback?.let { cb ->
                    if (cb is Context) {
                        showPermanentlyDeniedMessage(cb as Context, deniedPermissions)
                    }
                }
                callback?.onPermissionsPermanentlyDenied(deniedPermissions)
                callback?.onPermissionRequestCompleted()
            }
        }
    }
    
    /**
     * Reset internal state (useful for testing or app restart scenarios)
     * TODO: Implement state persistence to survive app restarts
     */
    fun resetState() {
        hasCheckedPermissionsOnStartup = false
        permissionRetryCount = 0
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Permission controller state reset")
    }
    
    /**
     * Get current permission retry count (useful for debugging)
     */
    fun getPermissionRetryCount(): Int = permissionRetryCount
    
    /**
     * Check if permissions have been checked on startup
     */
    fun hasCheckedPermissionsOnStartup(): Boolean = hasCheckedPermissionsOnStartup
}