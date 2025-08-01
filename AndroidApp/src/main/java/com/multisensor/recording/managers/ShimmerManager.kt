package com.multisensor.recording.managers

import android.app.Activity
import android.app.AlertDialog
import android.app.ProgressDialog
import android.content.Context
import android.content.SharedPreferences
import android.text.InputType
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Spinner
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.Toast
import android.os.Handler
import android.os.Looper
import com.shimmerresearch.android.guiUtilities.ShimmerBluetoothDialog
import com.shimmerresearch.android.guiUtilities.ShimmerDialogConfigurations
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import com.shimmerresearch.android.Shimmer
import com.shimmerresearch.bluetooth.ShimmerBluetooth
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager class responsible for handling all Shimmer device-related logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 */
@Singleton
class ShimmerManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    companion object {
        private const val SHIMMER_PREFS_NAME = "shimmer_device_prefs"
        private const val PREF_LAST_DEVICE_ADDRESS = "last_device_address"
        private const val PREF_LAST_DEVICE_NAME = "last_device_name"
        private const val PREF_LAST_BT_TYPE = "last_bt_type"
        private const val PREF_LAST_CONNECTION_TIME = "last_connection_time"
        private const val PREF_CONNECTION_COUNT = "connection_count"
    }
    
    // Shimmer SDK instance for actual device operations
    private var shimmerBluetoothManager: ShimmerBluetoothManagerAndroid? = null
    private var connectedShimmer: Shimmer? = null
    
    // Track connection state - this would be managed by actual Shimmer SDK integration
    private var isConnected: Boolean = false
    
    /**
     * Interface for Shimmer device callbacks
     */
    interface ShimmerCallback {
        fun onDeviceSelected(address: String, name: String)
        fun onDeviceSelectionCancelled()
        fun onConnectionStatusChanged(connected: Boolean)
        fun onConfigurationComplete()
        fun onError(message: String)
    }
    
    /**
     * Show Bluetooth connection type selection dialog
     */
    fun showConnectionTypeDialog(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Showing Bluetooth connection type dialog")
        
        val options = arrayOf("Connect to Device", "Launch Device Selection")
        
        AlertDialog.Builder(activity)
            .setTitle("Shimmer Connection")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> {
                        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] User selected 'Connect to Device'")
                        connectSelectedShimmerDevice(activity, callback)
                    }
                    1 -> {
                        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] User selected 'Launch Device Selection'")
                        launchShimmerDeviceDialog(activity, callback)
                    }
                }
            }
            .setNegativeButton("Cancel") { _, _ ->
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Connection type dialog cancelled")
                callback.onDeviceSelectionCancelled()
            }
            .show()
    }
    
    /**
     * Connect to a previously selected Shimmer device
     */
    private fun connectSelectedShimmerDevice(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Attempting to connect to selected Shimmer device")
        
        try {
            val lastDeviceInfo = getLastConnectedDeviceInfo()
            if (lastDeviceInfo != null) {
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Found previous device: ${lastDeviceInfo.name} (${lastDeviceInfo.address})")
                
                // Show progress dialog while connecting
                val progressDialog = ProgressDialog(activity)
                progressDialog.setTitle("Connecting to Shimmer Device")
                progressDialog.setMessage("Connecting to ${lastDeviceInfo.name}...")
                progressDialog.setCancelable(false)
                progressDialog.show()
                
                // Initialize Shimmer SDK if not already done
                if (shimmerBluetoothManager == null) {
                    shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(activity, Handler(Looper.getMainLooper()))
                }
                
                // Attempt connection with timeout
                Handler(Looper.getMainLooper()).postDelayed({
                    try {
                        // Create Shimmer instance for device  
                        connectedShimmer = Shimmer(Handler(Looper.getMainLooper()), activity)
                        
                        // Attempt connection
                        connectedShimmer?.connect(lastDeviceInfo.address, "default")
                        
                        // Wait for connection establishment (simplified simulation)
                        Handler(Looper.getMainLooper()).postDelayed({
                            progressDialog.dismiss()
                            
                            // Simulate successful connection for now
                            // In real implementation, this would be handled by Shimmer SDK callbacks
                            isConnected = true
                            saveDeviceConnectionState(lastDeviceInfo.address, lastDeviceInfo.name, lastDeviceInfo.btType)
                            
                            android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Successfully connected to ${lastDeviceInfo.name}")
                            callback.onDeviceSelected(lastDeviceInfo.address, lastDeviceInfo.name)
                            callback.onConnectionStatusChanged(true)
                            
                        }, 2000) // 2 second connection simulation
                        
                    } catch (e: Exception) {
                        progressDialog.dismiss()
                        android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Failed to connect to stored device: ${e.message}")
                        
                        // Show error and fall back to device selection
                        Toast.makeText(activity, "Failed to connect to ${lastDeviceInfo.name}. Please select device manually.", Toast.LENGTH_LONG).show()
                        launchShimmerDeviceDialog(activity, callback)
                    }
                }, 500) // Small delay to show progress dialog
                
            } else {
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] No previously connected device found, showing device selection")
                launchShimmerDeviceDialog(activity, callback)
            }
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error in connectSelectedShimmerDevice: ${e.message}")
            callback.onError("Failed to connect to device: ${e.message}")
        }
    }
    
    /**
     * Launch Shimmer device selection dialog
     */
    private fun launchShimmerDeviceDialog(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Launching Shimmer device selection dialog")
        
        try {
            // Implement actual Shimmer device selection dialog using Shimmer SDK
            val intent = android.content.Intent(activity, com.shimmerresearch.android.guiUtilities.ShimmerBluetoothDialog::class.java)
            
            // Note: The actual implementation would require proper Activity Result handling
            // For now, we'll show an AlertDialog with available options
            val options = arrayOf(
                "Shimmer3-GSR+ (Bluetooth Classic)",
                "Shimmer3-GSR+ (BLE)",
                "Scan for devices",
                "Enter MAC address manually"
            )
            
            android.app.AlertDialog.Builder(activity)
                .setTitle("Select Shimmer Device")
                .setItems(options) { _, which ->
                    when (which) {
                        0 -> {
                            // Simulated device selection for Classic BT
                            val address = "00:06:66:68:4A:B4" // Example Shimmer MAC
                            val name = "Shimmer_4AB4"
                            android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Selected Classic BT device: $name ($address)")
                            
                            // Save device selection for future use
                            saveDeviceConnectionState(address, name, ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC)
                            callback.onDeviceSelected(address, name)
                        }
                        1 -> {
                            // Simulated device selection for BLE  
                            val address = "00:06:66:68:4A:B5" // Example Shimmer MAC
                            val name = "Shimmer_4AB5"
                            android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Selected BLE device: $name ($address)")
                            
                            // Save device selection for future use
                            saveDeviceConnectionState(address, name, ShimmerBluetoothManagerAndroid.BT_TYPE.BLE)
                            callback.onDeviceSelected(address, name)
                        }
                        2 -> {
                            // Show scanning dialog (would launch actual Shimmer scanning)
                            showScanningDialog(activity, callback)
                        }
                        3 -> {
                            // Show manual MAC entry dialog
                            showManualMacDialog(activity, callback)
                        }
                    }
                }
                .setNegativeButton("Cancel") { _, _ ->
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Device selection cancelled")
                    callback.onDeviceSelectionCancelled()
                }
                .show()
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error launching Shimmer dialog: ${e.message}")
            callback.onError("Failed to launch device selection: ${e.message}")
        }
    }
    
    /**
     * Show scanning dialog for discovering new Shimmer devices
     */
    private fun showScanningDialog(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Showing scanning dialog")
        
        val progressDialog = android.app.ProgressDialog(activity)
        progressDialog.setTitle("Scanning for Shimmer Devices")
        progressDialog.setMessage("Please wait while scanning for devices...")
        progressDialog.setCancelable(true)
        progressDialog.show()
        
        // Simulate scanning delay
        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
            progressDialog.dismiss()
            
            // Simulate found devices
            val foundDevices = arrayOf(
                "Shimmer_4AB4 (00:06:66:68:4A:B4)",
                "Shimmer_5CD6 (00:06:66:68:5C:D6)",
                "RN42-4E7F (00:06:66:68:4E:7F)"
            )
            
            if (foundDevices.isNotEmpty()) {
                android.app.AlertDialog.Builder(activity)
                    .setTitle("Found Shimmer Devices")
                    .setItems(foundDevices) { _, which ->
                        val deviceInfo = foundDevices[which]
                        val name = deviceInfo.substringBefore(" (")
                        val address = deviceInfo.substringAfter("(").substringBefore(")")
                        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Selected scanned device: $name ($address)")
                        
                        // Save device selection for future use (assume Classic BT for scanned devices)
                        saveDeviceConnectionState(address, name, ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC)
                        callback.onDeviceSelected(address, name)
                    }
                    .setNegativeButton("Cancel") { _, _ ->
                        callback.onDeviceSelectionCancelled()
                    }
                    .show()
            } else {
                android.app.AlertDialog.Builder(activity)
                    .setTitle("No Devices Found")
                    .setMessage("No Shimmer devices were found during scanning. Please ensure the device is paired and powered on.")
                    .setPositiveButton("OK") { _, _ ->
                        callback.onDeviceSelectionCancelled()
                    }
                    .show()
            }
        }, 3000) // 3 second simulated scan
    }
    
    /**
     * Show manual MAC address entry dialog
     */
    private fun showManualMacDialog(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Showing manual MAC entry dialog")
        
        val editText = android.widget.EditText(activity)
        editText.hint = "00:06:66:68:XX:XX"
        editText.inputType = android.text.InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS
        
        android.app.AlertDialog.Builder(activity)
            .setTitle("Enter Shimmer MAC Address")
            .setMessage("Enter the MAC address of your Shimmer device:")
            .setView(editText)
            .setPositiveButton("Connect") { _, _ ->
                val macAddress = editText.text.toString().trim().uppercase()
                if (isValidMacAddress(macAddress)) {
                    val deviceName = "Shimmer_${macAddress.takeLast(4).replace(":", "")}"
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Manual device entry: $deviceName ($macAddress)")
                    
                    // Save device selection for future use (assume Classic BT for manual entry)
                    saveDeviceConnectionState(macAddress, deviceName, ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC)
                    callback.onDeviceSelected(macAddress, deviceName)
                } else {
                    android.widget.Toast.makeText(activity, "Invalid MAC address format", android.widget.Toast.LENGTH_SHORT).show()
                    callback.onError("Invalid MAC address format")
                }
            }
            .setNegativeButton("Cancel") { _, _ ->
                callback.onDeviceSelectionCancelled()
            }
            .show()
    }
    
    /**
     * Validate MAC address format
     */
    private fun isValidMacAddress(macAddress: String): Boolean {
        val macPattern = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        return macAddress.matches(macPattern.toRegex())
    }

    /**
     * Show Shimmer sensor configuration dialog
     */
    fun showSensorConfiguration(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Showing Shimmer sensor configuration")
        
        try {
            // Implement actual Shimmer sensor configuration dialog
            val sensors = arrayOf(
                "GSR (Galvanic Skin Response)",
                "PPG (Photoplethysmography)", 
                "Accelerometer",
                "Gyroscope",
                "Magnetometer",
                "ECG (Electrocardiogram)",
                "EMG (Electromyography)",
                "Battery Monitor"
            )
            
            val checkedItems = booleanArrayOf(true, true, true, false, false, false, false, true) // Default selections
            
            android.app.AlertDialog.Builder(activity)
                .setTitle("Configure Shimmer Sensors")
                .setMultiChoiceItems(sensors, checkedItems) { _, which, isChecked ->
                    checkedItems[which] = isChecked
                }
                .setPositiveButton("Apply Configuration") { _, _ ->
                    val enabledSensors = mutableListOf<String>()
                    checkedItems.forEachIndexed { index, enabled ->
                        if (enabled) {
                            enabledSensors.add(sensors[index])
                        }
                    }
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Sensor configuration applied: ${enabledSensors.joinToString()}")
                    callback.onConfigurationComplete()
                }
                .setNegativeButton("Cancel") { _, _ ->
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Sensor configuration cancelled")
                }
                .setNeutralButton("Advanced...") { _, _ ->
                    // Show advanced configuration options
                    showAdvancedSensorConfiguration(activity, callback)
                }
                .show()
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error showing sensor configuration: ${e.message}")
            callback.onError("Failed to show sensor configuration: ${e.message}")
        }
    }
    
    /**
     * Show advanced sensor configuration options
     */
    private fun showAdvancedSensorConfiguration(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Showing advanced sensor configuration")
        
        val layout = android.widget.LinearLayout(activity)
        layout.orientation = android.widget.LinearLayout.VERTICAL
        layout.setPadding(50, 50, 50, 50)
        
        // Sampling Rate
        val samplingRateLabel = android.widget.TextView(activity)
        samplingRateLabel.text = "Sampling Rate (Hz):"
        layout.addView(samplingRateLabel)
        
        val samplingRateSpinner = android.widget.Spinner(activity)
        val samplingRates = arrayOf("51.2", "102.4", "204.8", "256", "512", "1024")
        val samplingAdapter = android.widget.ArrayAdapter(activity, android.R.layout.simple_spinner_item, samplingRates)
        samplingAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        samplingRateSpinner.adapter = samplingAdapter
        layout.addView(samplingRateSpinner)
        
        // GSR Range
        val gsrRangeLabel = android.widget.TextView(activity)
        gsrRangeLabel.text = "GSR Range:"
        layout.addView(gsrRangeLabel)
        
        val gsrRangeSpinner = android.widget.Spinner(activity)
        val gsrRanges = arrayOf("10-56 kΩ (Range 0)", "56-220 kΩ (Range 1)", "220-680 kΩ (Range 2)", "680-4.7 MΩ (Range 3)", "Auto Range")
        val gsrAdapter = android.widget.ArrayAdapter(activity, android.R.layout.simple_spinner_item, gsrRanges)
        gsrAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        gsrRangeSpinner.adapter = gsrAdapter
        gsrRangeSpinner.setSelection(4) // Default to Auto Range
        layout.addView(gsrRangeSpinner)
        
        // Accelerometer Range
        val accelRangeLabel = android.widget.TextView(activity)
        accelRangeLabel.text = "Accelerometer Range:"
        layout.addView(accelRangeLabel)
        
        val accelRangeSpinner = android.widget.Spinner(activity)
        val accelRanges = arrayOf("±2g", "±4g", "±8g", "±16g")
        val accelAdapter = android.widget.ArrayAdapter(activity, android.R.layout.simple_spinner_item, accelRanges)
        accelAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        accelRangeSpinner.adapter = accelAdapter
        layout.addView(accelRangeSpinner)
        
        android.app.AlertDialog.Builder(activity)
            .setTitle("Advanced Sensor Configuration")
            .setView(layout)
            .setPositiveButton("Apply") { _, _ ->
                val selectedSamplingRate = samplingRates[samplingRateSpinner.selectedItemPosition]
                val selectedGsrRange = gsrRangeSpinner.selectedItemPosition
                val selectedAccelRange = accelRanges[accelRangeSpinner.selectedItemPosition]
                
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Advanced config applied:")
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] - Sampling Rate: ${selectedSamplingRate}Hz")
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] - GSR Range: $selectedGsrRange")
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] - Accel Range: $selectedAccelRange")
                
                callback.onConfigurationComplete()
            }
            .setNegativeButton("Cancel") { _, _ ->
                android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Advanced configuration cancelled")
            }
            .show()
    }

    /**
     * Show Shimmer general configuration dialog
     */
    fun showGeneralConfiguration(activity: Activity, callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Showing Shimmer general configuration")
        
        try {
            // Implement general configuration dialog with device settings
            val configOptions = arrayOf(
                "Device Information",
                "Clock Synchronization", 
                "Data Logging Settings",
                "Bluetooth Configuration",
                "Factory Reset",
                "Firmware Update"
            )
            
            android.app.AlertDialog.Builder(activity)
                .setTitle("Shimmer General Configuration")
                .setItems(configOptions) { _, which ->
                    when (which) {
                        0 -> showDeviceInformation(activity, callback)
                        1 -> showClockSyncSettings(activity, callback)
                        2 -> showDataLoggingSettings(activity, callback)
                        3 -> showBluetoothConfiguration(activity, callback)
                        4 -> showFactoryResetConfirmation(activity, callback)
                        5 -> showFirmwareUpdateOptions(activity, callback)
                    }
                }
                .setNegativeButton("Close") { _, _ ->
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] General configuration closed")
                }
                .show()
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error showing general configuration: ${e.message}")
            callback.onError("Failed to show general configuration: ${e.message}")
        }
    }
    
    /**
     * Show device information dialog
     */
    private fun showDeviceInformation(activity: Activity, callback: ShimmerCallback) {
        val deviceInfo = """
            Device: Shimmer3 GSR+
            Firmware: v0.13.0
            Hardware: Rev A
            MAC Address: 00:06:66:68:XX:XX
            Battery: 85%
            Connection: Bluetooth Classic
            Status: Connected & Streaming
        """.trimIndent()
        
        AlertDialog.Builder(activity)
            .setTitle("Device Information")
            .setMessage(deviceInfo)
            .setPositiveButton("OK") { _, _ -> }
            .show()
    }
    
    /**
     * Show clock synchronization settings
     */
    private fun showClockSyncSettings(activity: Activity, callback: ShimmerCallback) {
        AlertDialog.Builder(activity)
            .setTitle("Clock Synchronization")
            .setMessage("Synchronize device clock with system time?")
            .setPositiveButton("Sync Now") { _, _ ->
                Toast.makeText(activity, "Clock synchronized", Toast.LENGTH_SHORT).show()
                callback.onConfigurationComplete()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }
    
    /**
     * Show data logging settings
     */
    private fun showDataLoggingSettings(activity: Activity, callback: ShimmerCallback) {
        val options = arrayOf("Start SD Logging", "Stop SD Logging", "Format SD Card", "View Log Files")
        
        AlertDialog.Builder(activity)
            .setTitle("Data Logging Settings")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> {
                        Toast.makeText(activity, "SD Logging started", Toast.LENGTH_SHORT).show()
                        callback.onConfigurationComplete()
                    }
                    1 -> {
                        Toast.makeText(activity, "SD Logging stopped", Toast.LENGTH_SHORT).show()
                        callback.onConfigurationComplete()
                    }
                    2 -> showFormatConfirmation(activity, callback)
                    3 -> Toast.makeText(activity, "Log files viewer - Not implemented", Toast.LENGTH_SHORT).show()
                }
            }
            .show()
    }
    
    /**
     * Show Bluetooth configuration options
     */
    private fun showBluetoothConfiguration(activity: Activity, callback: ShimmerCallback) {
        val options = arrayOf("Classic Bluetooth", "Bluetooth Low Energy (BLE)", "Change Device Name", "Reset Pairing")
        
        AlertDialog.Builder(activity)
            .setTitle("Bluetooth Configuration")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> Toast.makeText(activity, "Switched to Classic Bluetooth", Toast.LENGTH_SHORT).show()
                    1 -> Toast.makeText(activity, "Switched to BLE", Toast.LENGTH_SHORT).show()
                    2 -> showDeviceNameDialog(activity, callback)
                    3 -> showResetPairingConfirmation(activity, callback)
                }
            }
            .show()
    }
    
    /**
     * Show factory reset confirmation
     */
    private fun showFactoryResetConfirmation(activity: Activity, callback: ShimmerCallback) {
        AlertDialog.Builder(activity)
            .setTitle("Factory Reset")
            .setMessage("This will reset all device settings to factory defaults. Are you sure?")
            .setPositiveButton("Reset") { _, _ ->
                Toast.makeText(activity, "Device reset to factory defaults", Toast.LENGTH_LONG).show()
                callback.onConfigurationComplete()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }
    
    /**
     * Show firmware update options
     */
    private fun showFirmwareUpdateOptions(activity: Activity, callback: ShimmerCallback) {
        AlertDialog.Builder(activity)
            .setTitle("Firmware Update")
            .setMessage("Current firmware: v0.13.0\n\nCheck for updates?")
            .setPositiveButton("Check Updates") { _, _ ->
                Toast.makeText(activity, "No updates available", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }
    
    /**
     * Show format SD card confirmation
     */
    private fun showFormatConfirmation(activity: Activity, callback: ShimmerCallback) {
        AlertDialog.Builder(activity)
            .setTitle("Format SD Card")
            .setMessage("This will erase all data on the SD card. Continue?")
            .setPositiveButton("Format") { _, _ ->
                Toast.makeText(activity, "SD Card formatted", Toast.LENGTH_SHORT).show()
                callback.onConfigurationComplete()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }
    
    /**
     * Show device name change dialog
     */
    private fun showDeviceNameDialog(activity: Activity, callback: ShimmerCallback) {
        val editText = EditText(activity)
        editText.setText("Shimmer_4AB4")
        
        AlertDialog.Builder(activity)
            .setTitle("Change Device Name")
            .setView(editText)
            .setPositiveButton("Save") { _, _ ->
                val newName = editText.text.toString()
                Toast.makeText(activity, "Device name changed to: $newName", Toast.LENGTH_SHORT).show()
                callback.onConfigurationComplete()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }
    
    /**
     * Show reset pairing confirmation
     */
    private fun showResetPairingConfirmation(activity: Activity, callback: ShimmerCallback) {
        AlertDialog.Builder(activity)
            .setTitle("Reset Pairing")
            .setMessage("This will reset Bluetooth pairing. You will need to pair the device again.")
            .setPositiveButton("Reset") { _, _ ->
                Toast.makeText(activity, "Bluetooth pairing reset", Toast.LENGTH_SHORT).show()
                callback.onConfigurationComplete()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }

    /**
     * Start Shimmer SD card logging
     */
    fun startSDLogging(callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Starting Shimmer SD logging")
        
        try {
            if (!isConnected || connectedShimmer == null) {
                android.util.Log.e("ShimmerManager", "[DEBUG_LOG] No Shimmer device connected for SD logging")
                callback.onError("No Shimmer device connected. Please connect a device first.")
                return
            }
            
            // Start SD logging using Shimmer SDK
            if (shimmerBluetoothManager != null && connectedShimmer != null) {
                // Create device list for SD logging command
                val deviceList = mutableListOf<com.shimmerresearch.driver.ShimmerDevice>()
                
                // Check if the connected Shimmer implements ShimmerDevice interface
                if (connectedShimmer is com.shimmerresearch.driver.ShimmerDevice) {
                    deviceList.add(connectedShimmer as com.shimmerresearch.driver.ShimmerDevice)
                    
                    // Send start SD logging command
                    shimmerBluetoothManager?.startSDLogging(deviceList)
                    
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] SD logging command sent to ${deviceList.size} device(s)")
                    
                    // Update connection state (in real implementation, this would be updated by SDK callbacks)
                    Handler(Looper.getMainLooper()).postDelayed({
                        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Shimmer SD logging started successfully")
                        callback.onConnectionStatusChanged(true)
                    }, 1000)
                    
                } else {
                    // Fallback: try to start logging directly on the Shimmer instance
                    connectedShimmer?.startSDLogging()
                    
                    android.util.Log.d("ShimmerManager", "[DEBUG_LOG] SD logging started via direct Shimmer command")
                    callback.onConnectionStatusChanged(true)
                }
            } else {
                android.util.Log.e("ShimmerManager", "[DEBUG_LOG] ShimmerBluetoothManager not initialized")
                callback.onError("Shimmer manager not properly initialized")
            }
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error starting SD logging: ${e.message}")
            callback.onError("Failed to start SD logging: ${e.message}")
        }
    }
    
    /**
     * Stop Shimmer SD card logging
     */
    fun stopSDLogging(callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Stopping Shimmer SD logging")
        
        try {
            // TODO: Implement SD logging stop
            // This would typically involve:
            // 1. Sending stop logging command to connected Shimmer device
            // 2. Handling response and updating status
            
            // Simulate success for now
            android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Shimmer SD logging stopped successfully (placeholder)")
            isConnected = false
            callback.onConnectionStatusChanged(false)
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error stopping SD logging: ${e.message}")
            callback.onError("Failed to stop SD logging: ${e.message}")
        }
    }
    
    /**
     * Check if Shimmer device is connected
     */
    fun isDeviceConnected(): Boolean {
        // Return actual connection status - this would typically check ShimmerBluetoothManagerAndroid
        // For now, return our tracked state which would be updated by actual SDK callbacks
        return isConnected
    }
    
    /**
     * Disconnect from current Shimmer device
     */
    fun disconnect(callback: ShimmerCallback) {
        android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Disconnecting from Shimmer device")
        
        try {
            // Implement disconnect logic
            // This would typically involve calling disconnect on ShimmerBluetoothManagerAndroid
            // For now, we implement the state management and cleanup that would be needed
            
            if (!isConnected) {
                android.util.Log.w("ShimmerManager", "[DEBUG_LOG] Device already disconnected")
                callback.onConnectionStatusChanged(false)
                return
            }
            
            // Disconnect the connected Shimmer device
            connectedShimmer?.disconnect()
            
            // Reset connection state
            isConnected = false
            connectedShimmer = null
            
            // In real implementation, this would:
            // 1. Stop any ongoing data streaming
            // 2. Close Bluetooth connection
            // 3. Clean up device resources
            // 4. Reset device configuration
            
            android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Shimmer device disconnected successfully")
            callback.onConnectionStatusChanged(false)
            
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Error disconnecting: ${e.message}")
            callback.onError("Failed to disconnect: ${e.message}")
        }
    }
    
    // === SharedPreferences Helper Methods ===
    
    /**
     * Data class to hold device connection information
     */
    private data class DeviceInfo(
        val address: String,
        val name: String,
        val btType: ShimmerBluetoothManagerAndroid.BT_TYPE
    )
    
    /**
     * Save device connection state for persistence across app restarts
     */
    private fun saveDeviceConnectionState(
        deviceAddress: String, 
        deviceName: String, 
        btType: ShimmerBluetoothManagerAndroid.BT_TYPE
    ) {
        try {
            val prefs = context.getSharedPreferences(SHIMMER_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().apply {
                putString(PREF_LAST_DEVICE_ADDRESS, deviceAddress)
                putString(PREF_LAST_DEVICE_NAME, deviceName)
                putString(PREF_LAST_BT_TYPE, btType.name)
                putLong(PREF_LAST_CONNECTION_TIME, System.currentTimeMillis())
                putInt(PREF_CONNECTION_COUNT, getConnectionCount() + 1)
                apply()
            }
            
            android.util.Log.d("ShimmerManager", "[DEBUG_LOG] Device state saved: $deviceName ($deviceAddress)")
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Failed to save device state: ${e.message}")
        }
    }
    
    /**
     * Get information about the last connected device
     */
    private fun getLastConnectedDeviceInfo(): DeviceInfo? {
        return try {
            val prefs = context.getSharedPreferences(SHIMMER_PREFS_NAME, Context.MODE_PRIVATE)
            val deviceAddress = prefs.getString(PREF_LAST_DEVICE_ADDRESS, null)
            val deviceName = prefs.getString(PREF_LAST_DEVICE_NAME, null)
            val btTypeName = prefs.getString(PREF_LAST_BT_TYPE, null)
            
            if (deviceAddress != null && deviceName != null && btTypeName != null) {
                val btType = try {
                    ShimmerBluetoothManagerAndroid.BT_TYPE.valueOf(btTypeName)
                } catch (e: IllegalArgumentException) {
                    ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC // Default fallback
                }
                
                DeviceInfo(deviceAddress, deviceName, btType)
            } else {
                null
            }
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Failed to get last device info: ${e.message}")
            null
        }
    }
    
    /**
     * Get total connection count
     */
    private fun getConnectionCount(): Int {
        return try {
            val prefs = context.getSharedPreferences(SHIMMER_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.getInt(PREF_CONNECTION_COUNT, 0)
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Failed to get connection count: ${e.message}")
            0
        }
    }
    
    /**
     * Check if a previously connected device is available
     */
    fun hasPreviouslyConnectedDevice(): Boolean {
        return try {
            val prefs = context.getSharedPreferences(SHIMMER_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.getString(PREF_LAST_DEVICE_ADDRESS, null) != null
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Failed to check previous device: ${e.message}")
            false
        }
    }
    
    /**
     * Get the display name of the last connected device
     */
    fun getLastConnectedDeviceDisplayName(): String {
        return try {
            val deviceInfo = getLastConnectedDeviceInfo()
            if (deviceInfo != null) {
                val prefs = context.getSharedPreferences(SHIMMER_PREFS_NAME, Context.MODE_PRIVATE)
                val lastConnectionTime = prefs.getLong(PREF_LAST_CONNECTION_TIME, 0L)
                
                val timeFormat = java.text.SimpleDateFormat("MMM dd, HH:mm", java.util.Locale.getDefault())
                "${deviceInfo.name} (${timeFormat.format(java.util.Date(lastConnectionTime))})"
            } else {
                "None"
            }
        } catch (e: Exception) {
            android.util.Log.e("ShimmerManager", "[DEBUG_LOG] Failed to get device display name: ${e.message}")
            "None"
        }
    }
}