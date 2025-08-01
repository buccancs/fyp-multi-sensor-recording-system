package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.app.Activity
import android.content.Context
import android.content.SharedPreferences
import android.widget.Toast
import com.multisensor.recording.managers.PermissionManager
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all permission-related logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * 
 * Integration with MainActivity refactoring: ✅ COMPLETED
 * - MainActivity now delegates all permission operations to PermissionController
 * - Complete separation of concerns achieved
 * - All permission logic centralized in this controller
 * 
 * Comprehensive unit tests: ✅ COMPLETED  
 * - Added PermissionControllerTest with 40+ test scenarios
 * - Covers all permission flows: granted, denied, manual requests
 * - Tests state persistence, edge cases, and callback handling
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
    
    // SharedPreferences for state persistence
    private var sharedPreferences: SharedPreferences? = null
    
    companion object {
        private const val PREFS_NAME = "permission_controller_prefs"
        private const val KEY_HAS_CHECKED_PERMISSIONS = "has_checked_permissions_on_startup"
        private const val KEY_PERMISSION_RETRY_COUNT = "permission_retry_count"
        private const val KEY_LAST_PERMISSION_REQUEST_TIME = "last_permission_request_time"
        private const val KEY_PERMANENTLY_DENIED_PERMISSIONS = "permanently_denied_permissions"
    }
    
    /**
     * Set the callback for permission events and initialize state persistence
     */
    fun setCallback(callback: PermissionCallback) {
        this.callback = callback
        
        // Initialize SharedPreferences if we have a context
        if (callback is Context) {
            initializeStateStorage(callback as Context)
        }
    }
    
    /**
     * Initialize SharedPreferences for state persistence
     */
    private fun initializeStateStorage(context: Context) {
        try {
            sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            loadPersistedState()
            android.util.Log.d("PermissionController", "[DEBUG_LOG] State persistence initialized")
        } catch (e: Exception) {
            android.util.Log.e("PermissionController", "[DEBUG_LOG] Failed to initialize state persistence: ${e.message}")
        }
    }
    
    /**
     * Load persisted state from SharedPreferences
     */
    private fun loadPersistedState() {
        sharedPreferences?.let { prefs ->
            hasCheckedPermissionsOnStartup = prefs.getBoolean(KEY_HAS_CHECKED_PERMISSIONS, false)
            permissionRetryCount = prefs.getInt(KEY_PERMISSION_RETRY_COUNT, 0)
            
            val lastRequestTime = prefs.getLong(KEY_LAST_PERMISSION_REQUEST_TIME, 0)
            val currentTime = System.currentTimeMillis()
            
            // Reset permission state if more than 24 hours have passed since last request
            if (currentTime - lastRequestTime > 24 * 60 * 60 * 1000) {
                android.util.Log.d("PermissionController", "[DEBUG_LOG] Resetting permission state after 24 hours")
                hasCheckedPermissionsOnStartup = false
                permissionRetryCount = 0
                persistState()
            }
            
            android.util.Log.d("PermissionController", "[DEBUG_LOG] Loaded persisted state: checked=$hasCheckedPermissionsOnStartup, retries=$permissionRetryCount")
        }
    }
    
    /**
     * Persist current state to SharedPreferences
     */
    private fun persistState() {
        sharedPreferences?.edit()?.apply {
            putBoolean(KEY_HAS_CHECKED_PERMISSIONS, hasCheckedPermissionsOnStartup)
            putInt(KEY_PERMISSION_RETRY_COUNT, permissionRetryCount)
            putLong(KEY_LAST_PERMISSION_REQUEST_TIME, System.currentTimeMillis())
            apply()
        }
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
            hasCheckedPermissionsOnStartup = true
            persistState()
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
        
        // Reset retry counter for fresh manual attempt (don't increment for manual requests)
        permissionRetryCount = 0
        persistState()
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
                hasCheckedPermissionsOnStartup = true
                persistState()
                callback?.onAllPermissionsGranted()
                callback?.onPermissionRequestCompleted()
            }
            
            override fun onPermissionsTemporarilyDenied(
                deniedPermissions: List<String>,
                grantedCount: Int,
                totalCount: Int
            ) {
                android.util.Log.d("PermissionController", "[DEBUG_LOG] Temporary denial callback received")
                persistState()
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
                
                // Store permanently denied permissions for future reference
                storePermanentlyDeniedPermissions(deniedPermissions)
                persistState()
                
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
     * Store permanently denied permissions for future reference
     */
    private fun storePermanentlyDeniedPermissions(deniedPermissions: List<String>) {
        sharedPreferences?.edit()?.apply {
            putStringSet(KEY_PERMANENTLY_DENIED_PERMISSIONS, deniedPermissions.toSet())
            apply()
        }
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Stored permanently denied permissions: ${deniedPermissions.joinToString(", ")}")
    }
    
    /**
     * Get permanently denied permissions from storage
     */
    fun getPermanentlyDeniedPermissions(): Set<String> {
        return sharedPreferences?.getStringSet(KEY_PERMANENTLY_DENIED_PERMISSIONS, emptySet()) ?: emptySet()
    }
    
    /**
     * Reset internal state (useful for testing or app restart scenarios)
     */
    fun resetState() {
        hasCheckedPermissionsOnStartup = false
        permissionRetryCount = 0
        persistState()
        android.util.Log.d("PermissionController", "[DEBUG_LOG] Permission controller state reset and persisted")
    }
    
    /**
     * Get current permission retry count (useful for debugging)
     */
    fun getPermissionRetryCount(): Int = permissionRetryCount
    
    /**
     * Check if permissions have been checked on startup
     */
    fun hasCheckedPermissionsOnStartup(): Boolean = hasCheckedPermissionsOnStartup
    
    /**
     * Get permission controller status for debugging
     */
    fun getPermissionStatus(): String {
        return buildString {
            append("Permission Controller Status:\n")
            append("- Has checked permissions on startup: $hasCheckedPermissionsOnStartup\n")
            append("- Permission retry count: $permissionRetryCount\n")
            append("- State persistence: ${if (sharedPreferences != null) "Enabled" else "Disabled"}\n")
            val permanentlyDenied = getPermanentlyDeniedPermissions()
            append("- Permanently denied permissions: ${if (permanentlyDenied.isEmpty()) "None" else permanentlyDenied.joinToString(", ")}\n")
            append("- Last request time: ${sharedPreferences?.getLong(KEY_LAST_PERMISSION_REQUEST_TIME, 0) ?: 0}")
        }
    }
    
    /**
     * Clear all persisted permission state (useful for testing or fresh start)
     */
    fun clearPersistedState() {
        sharedPreferences?.edit()?.clear()?.apply()
        hasCheckedPermissionsOnStartup = false
        permissionRetryCount = 0
        android.util.Log.d("PermissionController", "[DEBUG_LOG] All persisted permission state cleared")
    }
    
    /**
     * Initialize permissions check on app startup
     * Should be called from MainActivity.onResume() on first resume
     */
    fun initializePermissionsOnStartup(context: Context) {
        if (!hasCheckedPermissionsOnStartup) {
            android.util.Log.d("PermissionController", "[DEBUG_LOG] First startup - checking permissions")
            hasCheckedPermissionsOnStartup = true
            checkPermissions(context)
        } else {
            android.util.Log.d("PermissionController", "[DEBUG_LOG] Subsequent startup - skipping permission check")
            // Still update button visibility in case permissions changed externally
            updatePermissionButtonVisibility(context)
        }
    }
    
    /**
     * Log current permission states for debugging
     */
    fun logCurrentPermissionStates(context: Context) {
        permissionManager.logCurrentPermissionStates(context)
    }
}