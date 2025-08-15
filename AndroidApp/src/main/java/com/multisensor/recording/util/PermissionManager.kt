package com.multisensor.recording.util

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat

/**
 * Streamlined permission manager for essential app permissions
 */
class PermissionManager(private val context: Context) {

    companion object {
        /**
         * Get the appropriate permissions based on API level.
         * Handles deprecated storage permissions and API-specific Bluetooth permissions.
         */
        fun getRequiredPermissions(): Array<String> {
            val permissions = mutableListOf<String>()
            
            // Core permissions - always required
            permissions.add(Manifest.permission.CAMERA)
            permissions.add(Manifest.permission.RECORD_AUDIO)
            
            // Storage permissions - deprecated in API 30+ for scoped storage
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
            }
            
            // Bluetooth permissions - different for API 31+
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                permissions.add(Manifest.permission.BLUETOOTH_CONNECT)
                permissions.add(Manifest.permission.BLUETOOTH_SCAN)
            } else {
                permissions.add(Manifest.permission.BLUETOOTH)
                permissions.add(Manifest.permission.BLUETOOTH_ADMIN)
            }
            
            // Location permissions - needed for Bluetooth scanning
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                // For API 31+, fine location may not be needed if we don't derive location
                permissions.add(Manifest.permission.ACCESS_COARSE_LOCATION)
            } else {
                // For older APIs, both needed for Bluetooth
                permissions.add(Manifest.permission.ACCESS_COARSE_LOCATION)
                permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
            }
            
            return permissions.toTypedArray()
        }
        
        @Deprecated("Use getRequiredPermissions() for API-level aware permissions")
        val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    }

    fun hasAllPermissions(): Boolean {
        return getRequiredPermissions().all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
    }

    fun requestAllPermissions(activity: ComponentActivity, callback: (Boolean) -> Unit) {
        if (hasAllPermissions()) {
            callback(true)
            return
        }

        val requestPermissionLauncher = activity.registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            val allGranted = permissions.all { it.value }
            callback(allGranted)
        }

        requestPermissionLauncher.launch(getRequiredPermissions())
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
        return ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == 
               PackageManager.PERMISSION_GRANTED &&
               ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == 
               PackageManager.PERMISSION_GRANTED
    }
}