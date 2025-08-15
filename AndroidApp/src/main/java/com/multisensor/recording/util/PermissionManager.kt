package com.multisensor.recording.util

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner

/**
 * Lifecycle-aware permission manager for essential app permissions
 * Fixes permission flow fragility by initializing launchers in onCreate
 * and providing API level gating
 */
class PermissionManager(private val context: Context) : DefaultLifecycleObserver {

    companion object {
        // API level gated permissions - only request what's available for current API
        private val BASE_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
        
        private val BLUETOOTH_LEGACY_PERMISSIONS = arrayOf(
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
        
        // API 31+ permissions
        private val BLUETOOTH_NEW_PERMISSIONS = arrayOf(
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    }
    
    private var permissionLauncher: ActivityResultLauncher<Array<String>>? = null
    private var permissionCallback: ((Boolean) -> Unit)? = null
    private var isInitialized = false

    /**
     * Get required permissions based on API level
     */
    fun getRequiredPermissions(): Array<String> {
        val permissions = mutableListOf<String>()
        permissions.addAll(BASE_PERMISSIONS)
        
        // API level gating for Bluetooth permissions
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissions.addAll(BLUETOOTH_NEW_PERMISSIONS)
        } else {
            permissions.addAll(BLUETOOTH_LEGACY_PERMISSIONS)
        }
        
        return permissions.toTypedArray()
    }

    /**
     * Initialize permission launcher - must be called during onCreate
     */
    fun initializePermissionLauncher(activity: ComponentActivity) {
        if (isInitialized) {
            return
        }
        
        permissionLauncher = activity.registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            val allGranted = permissions.all { it.value }
            permissionCallback?.invoke(allGranted)
            permissionCallback = null
        }
        
        // Observe lifecycle to clean up
        activity.lifecycle.addObserver(this)
        isInitialized = true
    }

    fun hasAllPermissions(): Boolean {
        return getRequiredPermissions().all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
    }

    /**
     * Request permissions with lifecycle safety
     */
    fun requestAllPermissions(callback: (Boolean) -> Unit) {
        if (!isInitialized) {
            throw IllegalStateException("PermissionManager not initialized. Call initializePermissionLauncher() first.")
        }
        
        if (hasAllPermissions()) {
            callback(true)
            return
        }

        permissionCallback = callback
        permissionLauncher?.launch(getRequiredPermissions())
    }

    fun hasCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == 
               PackageManager.PERMISSION_GRANTED
    }

    fun hasStoragePermission(): Boolean {
        return ContextCompat.checkSelfPermission(context, Manifest.permission.WRITE_EXTERNAL_STORAGE) == 
               PackageManager.PERMISSION_GRANTED
    }

    fun hasBluetoothPermissions(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == 
                   PackageManager.PERMISSION_GRANTED &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == 
                   PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH) == 
                   PackageManager.PERMISSION_GRANTED &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_ADMIN) == 
                   PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Provide user guidance for denied permissions
     */
    fun getPermissionGuidanceMessage(): String {
        val deniedPermissions = getRequiredPermissions().filter { permission ->
            ContextCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED
        }
        
        if (deniedPermissions.isEmpty()) {
            return "All permissions granted"
        }
        
        return buildString {
            append("The following permissions are required for full functionality:\n\n")
            deniedPermissions.forEach { permission ->
                val friendlyName = when (permission) {
                    Manifest.permission.CAMERA -> "Camera access"
                    Manifest.permission.RECORD_AUDIO -> "Microphone access"
                    Manifest.permission.WRITE_EXTERNAL_STORAGE -> "Storage access"
                    Manifest.permission.BLUETOOTH_CONNECT -> "Bluetooth connection"
                    Manifest.permission.BLUETOOTH_SCAN -> "Bluetooth scanning"
                    Manifest.permission.ACCESS_FINE_LOCATION -> "Location access (for Bluetooth)"
                    else -> permission.removePrefix("android.permission.")
                }
                append("• $friendlyName\n")
            }
            append("\nPlease grant these permissions in Settings or retry the permission request.")
        }
    }
    
    override fun onDestroy(owner: LifecycleOwner) {
        permissionLauncher = null
        permissionCallback = null
        isInitialized = false
    }
}