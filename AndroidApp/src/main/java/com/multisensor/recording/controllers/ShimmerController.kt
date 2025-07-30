package com.multisensor.recording.controllers

import android.app.Activity
import android.app.AlertDialog
import android.app.Dialog
import android.content.Context
import android.content.Intent
import android.widget.Toast
import androidx.activity.result.ActivityResultLauncher
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.ui.MainViewModel
import com.shimmerresearch.android.guiUtilities.ShimmerBluetoothDialog
import com.shimmerresearch.android.guiUtilities.ShimmerDialogConfigurations
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all Shimmer device integration logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * Works in coordination with ShimmerManager for comprehensive Shimmer device handling.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for Shimmer device scenarios
 * TODO: Implement Shimmer device state persistence across app restarts
 * TODO: Add support for multiple simultaneous Shimmer devices
 * TODO: Implement proper error handling for Shimmer connection failures
 */
@Singleton
class ShimmerController @Inject constructor(
    private val shimmerManager: ShimmerManager
) {
    
    /**
     * Interface for Shimmer device-related callbacks to the UI layer
     */
    interface ShimmerCallback {
        fun onDeviceSelected(address: String, name: String)
        fun onDeviceSelectionCancelled()
        fun onConnectionStatusChanged(connected: Boolean)
        fun onConfigurationComplete()
        fun onShimmerError(message: String)
        fun updateStatusText(text: String)
        fun showToast(message: String, duration: Int = Toast.LENGTH_SHORT)
        fun runOnUiThread(action: () -> Unit)
    }
    
    private var callback: ShimmerCallback? = null
    private var selectedShimmerAddress: String? = null
    private var selectedShimmerName: String? = null
    private var preferredBtType: ShimmerBluetoothManagerAndroid.BT_TYPE = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
    
    /**
     * Set the callback for Shimmer device events
     */
    fun setCallback(callback: ShimmerCallback) {
        this.callback = callback
    }
    
    /**
     * Show Bluetooth connection type selection dialog (BLE vs Classic)
     * Following the official bluetoothManagerExample pattern
     */
    fun showBtTypeConnectionOption(context: Context) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Showing Bluetooth type selection dialog")
        
        val alertDialog = AlertDialog.Builder(context).create()
        alertDialog.setCancelable(false)
        alertDialog.setMessage("Choose preferred Bluetooth type")
        
        alertDialog.setButton(Dialog.BUTTON_POSITIVE, "BT CLASSIC") { _, _ ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] User selected BT CLASSIC")
            preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
            connectSelectedShimmerDevice()
        }
        
        alertDialog.setButton(Dialog.BUTTON_NEGATIVE, "BLE") { _, _ ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] User selected BLE")
            preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BLE
            connectSelectedShimmerDevice()
        }
        
        alertDialog.show()
    }
    
    /**
     * Connect to the selected Shimmer device using the chosen connection type
     */
    private fun connectSelectedShimmerDevice() {
        selectedShimmerAddress?.let { address ->
            selectedShimmerName?.let { name ->
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] Connecting to Shimmer device:")
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] - Address: $address")
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] - Name: $name")
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] - Connection Type: $preferredBtType")
                
                // Update UI to show connection attempt
                callback?.updateStatusText("Connecting to $name ($preferredBtType)...")
                
                // TODO: Connect via ViewModel/ShimmerRecorder - implement connectShimmerDevice method
                // This should be implemented when integrating with the ViewModel
                callback?.showToast("Connecting to $name via $preferredBtType")
                
                // Notify callback of connection attempt
                callback?.onDeviceSelected(address, name)
            }
        } ?: run {
            android.util.Log.w("ShimmerController", "[DEBUG_LOG] Cannot connect - no device selected")
            callback?.onShimmerError("No Shimmer device selected for connection")
        }
    }
    
    /**
     * Launch ShimmerBluetoothDialog for device selection using Activity Result API
     */
    fun launchShimmerDeviceDialog(activity: Activity, launcher: ActivityResultLauncher<Intent>) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Launching Shimmer device selection dialog")
        
        try {
            val intent = Intent(activity, ShimmerBluetoothDialog::class.java)
            launcher.launch(intent)
        } catch (e: Exception) {
            android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to launch Shimmer device dialog: ${e.message}")
            callback?.onShimmerError("Failed to launch device selection dialog: ${e.message}")
        }
    }
    
    /**
     * Handle device selection result from ShimmerBluetoothDialog
     */
    fun handleDeviceSelectionResult(address: String?, name: String?) {
        if (address != null && name != null) {
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Device selected: $name ($address)")
            selectedShimmerAddress = address
            selectedShimmerName = name
            
            // Show connection type selection dialog
            // Note: Context will be provided by the callback implementation
            callback?.onDeviceSelected(address, name)
        } else {
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Device selection cancelled")
            callback?.onDeviceSelectionCancelled()
        }
    }
    
    /**
     * Show Shimmer sensor configuration dialog
     * Requires a connected Shimmer device
     */
    fun showShimmerSensorConfiguration(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Showing Shimmer sensor configuration")
        
        // TODO: Get connected shimmer device from ViewModel
        // This is a placeholder implementation that should be completed during integration
        /*
        val shimmerDevice = viewModel.getConnectedShimmerDevice()
        val btManager = viewModel.getShimmerBluetoothManager()
        
        if (shimmerDevice != null && btManager != null) {
            if (!shimmerDevice.isStreaming() && !shimmerDevice.isSDLogging()) {
                ShimmerDialogConfigurations.buildShimmerSensorEnableDetails(shimmerDevice, context as Activity, btManager)
                callback?.onConfigurationComplete()
            } else {
                callback?.showToast("Cannot configure - device is streaming or logging")
            }
        } else {
            callback?.showToast("No Shimmer device connected")
        }
        */
        
        // Temporary implementation until ViewModel integration is complete
        callback?.showToast("Shimmer sensor configuration - Coming soon")
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Sensor configuration - placeholder implementation")
    }
    
    /**
     * Show Shimmer general configuration dialog
     * Requires a connected Shimmer device
     */
    fun showShimmerGeneralConfiguration(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Showing Shimmer general configuration")
        
        // TODO: Get connected shimmer device from ViewModel
        // This is a placeholder implementation that should be completed during integration
        /*
        val shimmerDevice = viewModel.getConnectedShimmerDevice()
        val btManager = viewModel.getShimmerBluetoothManager()
        
        if (shimmerDevice != null && btManager != null) {
            if (!shimmerDevice.isStreaming() && !shimmerDevice.isSDLogging()) {
                ShimmerDialogConfigurations.buildShimmerConfigOptions(shimmerDevice, context as Activity, btManager)
                callback?.onConfigurationComplete()
            } else {
                callback?.showToast("Cannot configure - device is streaming or logging")
            }
        } else {
            callback?.showToast("No Shimmer device connected")
        }
        */
        
        // Temporary implementation until ViewModel integration is complete
        callback?.showToast("Shimmer general configuration - Coming soon")
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] General configuration - placeholder implementation")
    }
    
    /**
     * Start SD logging on connected Shimmer device
     */
    fun startShimmerSDLogging(viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Starting Shimmer SD logging")
        
        // Check if any device is currently streaming or logging
        if (viewModel.isAnyShimmerDeviceStreaming()) {
            callback?.showToast("Cannot start SD logging - device is streaming")
            return
        }
        
        if (viewModel.isAnyShimmerDeviceSDLogging()) {
            callback?.showToast("SD logging is already active")
            return
        }
        
        // Start SD logging via ViewModel wrapper method
        viewModel.startShimmerSDLogging { success ->
            callback?.runOnUiThread {
                if (success) {
                    callback?.showToast("SD logging started")
                    android.util.Log.d("ShimmerController", "[DEBUG_LOG] SD logging started successfully")
                } else {
                    callback?.showToast("Failed to start SD logging")
                    android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to start SD logging")
                    callback?.onShimmerError("Failed to start SD logging")
                }
            }
        }
    }
    
    /**
     * Stop SD logging on connected Shimmer device
     */
    fun stopShimmerSDLogging(viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Stopping Shimmer SD logging")
        
        // Check if any device is currently SD logging
        if (!viewModel.isAnyShimmerDeviceSDLogging()) {
            callback?.showToast("No SD logging is currently active")
            return
        }
        
        // Stop SD logging via ViewModel wrapper method
        viewModel.stopShimmerSDLogging { success ->
            callback?.runOnUiThread {
                if (success) {
                    callback?.showToast("SD logging stopped")
                    android.util.Log.d("ShimmerController", "[DEBUG_LOG] SD logging stopped successfully")
                } else {
                    callback?.showToast("Failed to stop SD logging")
                    android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to stop SD logging")
                    callback?.onShimmerError("Failed to stop SD logging")
                }
            }
        }
    }
    
    /**
     * Handle Shimmer configuration menu action
     */
    fun handleShimmerConfigMenuAction(context: Context) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Opening Shimmer Configuration")
        
        try {
            val intent = Intent(context, com.multisensor.recording.ui.ShimmerConfigActivity::class.java)
            context.startActivity(intent)
        } catch (e: Exception) {
            android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to open Shimmer Configuration: ${e.message}")
            callback?.onShimmerError("Failed to open Shimmer Configuration: ${e.message}")
        }
    }
    
    /**
     * Get current Shimmer connection status
     */
    fun getConnectionStatus(): String {
        return buildString {
            append("Shimmer Status:\n")
            append("- Selected Device: ${selectedShimmerName ?: "None"}\n")
            append("- Selected Address: ${selectedShimmerAddress ?: "None"}\n")
            append("- Preferred BT Type: $preferredBtType\n")
            // TODO: Add actual connection status from ViewModel
            append("- Connection Status: TODO - implement with ViewModel integration")
        }
    }
    
    /**
     * Reset Shimmer controller state
     */
    fun resetState() {
        selectedShimmerAddress = null
        selectedShimmerName = null
        preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Shimmer controller state reset")
    }
    
    /**
     * Get selected device information
     */
    fun getSelectedDeviceInfo(): Pair<String?, String?> {
        return Pair(selectedShimmerAddress, selectedShimmerName)
    }
    
    /**
     * Get preferred Bluetooth type
     */
    fun getPreferredBtType(): ShimmerBluetoothManagerAndroid.BT_TYPE {
        return preferredBtType
    }
    
    /**
     * Set preferred Bluetooth type
     */
    fun setPreferredBtType(btType: ShimmerBluetoothManagerAndroid.BT_TYPE) {
        preferredBtType = btType
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Preferred BT type set to: $btType")
    }
}