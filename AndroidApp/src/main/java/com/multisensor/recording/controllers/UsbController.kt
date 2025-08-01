package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.widget.Toast
import com.multisensor.recording.managers.UsbDeviceManager
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling USB device management and integration.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * Works in coordination with UsbDeviceManager for comprehensive USB device handling.
 * 
 * ✅ Complete integration with MainActivity refactoring
 * ✅ Add comprehensive unit tests for USB device scenarios
 * ✅ Implement USB device state persistence across app restarts
 * ✅ Add support for multiple simultaneous USB devices
 * 
 * TODO: Add device prioritization for recording when multiple devices are connected
 * TODO: Implement hot-swap detection for device replacement scenarios
 * TODO: Add configuration profiles for per-device settings persistence
 * TODO: Integrate usage analytics and performance metrics
 * TODO: Add network-based device status reporting for remote monitoring
 * TODO: Implement device-specific calibration state persistence
 * TODO: Add advanced connection quality monitoring and reporting
 * TODO: Support for custom device filtering and selection criteria
 */
@Singleton
class UsbController @Inject constructor(
    private val usbDeviceManager: UsbDeviceManager
) {
    
    companion object {
        private const val USB_PREFS_NAME = "usb_device_prefs"
        private const val PREF_LAST_CONNECTED_DEVICE = "last_connected_device"
        private const val PREF_LAST_CONNECTION_TIME = "last_connection_time"
        private const val PREF_CONNECTION_COUNT = "connection_count"
        private const val PREF_DEVICE_VENDOR_ID = "device_vendor_id"
        private const val PREF_DEVICE_PRODUCT_ID = "device_product_id"
        private const val SCANNING_INTERVAL_MS = 5000L // 5 seconds
    }
    
    /**
     * Interface for USB device-related callbacks to the UI layer
     */
    interface UsbCallback {
        fun onSupportedDeviceAttached(device: UsbDevice)
        fun onUnsupportedDeviceAttached(device: UsbDevice)
        fun onDeviceDetached(device: UsbDevice)
        fun onUsbError(message: String)
        fun updateStatusText(text: String)
        fun initializeRecordingSystem()
        fun areAllPermissionsGranted(): Boolean
    }

    private var callback: UsbCallback? = null
    
    // Multiple device management state
    private val connectedSupportedDevices = mutableMapOf<String, UsbDevice>()
    private val deviceConnectionTimes = mutableMapOf<String, Long>()
    private val deviceConnectionCounts = mutableMapOf<String, Int>()
    
    // Periodic scanning state
    private var isScanning = false
    private var lastKnownDevices = mutableSetOf<String>()
    private val scanningHandler = android.os.Handler(android.os.Looper.getMainLooper())
    
    /**
     * Set the callback for USB device events
     */
    fun setCallback(callback: UsbCallback) {
        this.callback = callback
    }
    
    /**
     * Handle USB device intent from system - extracted from MainActivity
     */
    fun handleUsbDeviceIntent(context: Context, intent: Intent) {
        android.util.Log.d("UsbController", "[DEBUG_LOG] Handling USB device intent: ${intent.action}")
        
        when (intent.action) {
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                handleUsbDeviceAttached(context, intent)
            }
            UsbManager.ACTION_USB_DEVICE_DETACHED -> {
                handleUsbDeviceDetached(context, intent)
            }
            else -> {
                android.util.Log.d("UsbController", "[DEBUG_LOG] Intent action: ${intent.action} (not USB device related)")
            }
        }
    }
    
    /**
     * Handle USB device attachment event
     */
    private fun handleUsbDeviceAttached(context: Context, intent: Intent) {
        val device: UsbDevice? = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
        }
        
        device?.let { usbDevice ->
            android.util.Log.d("UsbController", "[DEBUG_LOG] USB device attached:")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Device name: ${usbDevice.deviceName}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", usbDevice.vendorId)}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", usbDevice.productId)}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Device class: ${usbDevice.deviceClass}")
            
            // Use UsbDeviceManager to check if device is supported
            if (usbDeviceManager.isSupportedTopdonDevice(usbDevice)) {
                handleSupportedDeviceAttached(context, usbDevice)
            } else {
                handleUnsupportedDeviceAttached(context, usbDevice)
            }
        } ?: run {
            android.util.Log.w("UsbController", "[DEBUG_LOG] USB device attachment intent received but no device found")
            callback?.onUsbError("USB device attachment detected but no device information available")
        }
    }
    
    /**
     * Handle USB device detachment event
     */
    private fun handleUsbDeviceDetached(context: Context, intent: Intent) {
        val device: UsbDevice? = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
        }
        
        device?.let { usbDevice ->
            val deviceKey = getDeviceKey(usbDevice)
            android.util.Log.d("UsbController", "[DEBUG_LOG] USB device detached:")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Device name: ${usbDevice.deviceName}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Device key: $deviceKey")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", usbDevice.vendorId)}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", usbDevice.productId)}")
            
            callback?.onDeviceDetached(usbDevice)
            
            // Update status if it was a supported device
            if (usbDeviceManager.isSupportedTopdonDevice(usbDevice)) {
                // Remove from our tracking
                connectedSupportedDevices.remove(deviceKey)
                
                val remainingDevices = connectedSupportedDevices.size
                val message = if (remainingDevices == 0) {
                    "Topdon Thermal Camera Disconnected"
                } else {
                    "Topdon Camera Disconnected\nRemaining devices: $remainingDevices"
                }
                
                callback?.updateStatusText(getMultiDeviceStatusText())
                Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
                
                // Update multi-device state
                saveMultiDeviceState(context)
            }
        } ?: run {
            android.util.Log.w("UsbController", "[DEBUG_LOG] USB device detachment intent received but no device found")
        }
    }
    
    /**
     * Handle supported TOPDON device attachment
     */
    private fun handleSupportedDeviceAttached(context: Context, usbDevice: UsbDevice) {
        val deviceKey = getDeviceKey(usbDevice)
        android.util.Log.d("UsbController", "[DEBUG_LOG] ✓ Supported Topdon thermal camera detected!")
        android.util.Log.d("UsbController", "[DEBUG_LOG] Device key: $deviceKey")
        
        // Track this device in our multiple device management
        connectedSupportedDevices[deviceKey] = usbDevice
        deviceConnectionTimes[deviceKey] = System.currentTimeMillis()
        deviceConnectionCounts[deviceKey] = (deviceConnectionCounts[deviceKey] ?: 0) + 1
        
        // Show user notification
        val deviceCount = connectedSupportedDevices.size
        val message = if (deviceCount == 1) {
            "Topdon Thermal Camera Connected!\nDevice: ${usbDevice.deviceName}"
        } else {
            "Topdon Camera #$deviceCount Connected!\nDevice: ${usbDevice.deviceName}\nTotal devices: $deviceCount"
        }
        
        Toast.makeText(context, message, Toast.LENGTH_LONG).show()
        
        // Update status
        callback?.updateStatusText(getMultiDeviceStatusText())
        
        // Save device state persistence
        saveDeviceConnectionState(context, usbDevice)
        saveMultiDeviceState(context)
        
        // Initialize thermal recorder if permissions are available
        if (callback?.areAllPermissionsGranted() == true) {
            android.util.Log.d("UsbController", "[DEBUG_LOG] Permissions available, initializing thermal recorder")
            callback?.initializeRecordingSystem()
        } else {
            android.util.Log.d("UsbController", "[DEBUG_LOG] Permissions not available, requesting permissions first")
            callback?.updateStatusText("Thermal camera detected - Please grant permissions to continue")
        }
        
        // Notify callback
        callback?.onSupportedDeviceAttached(usbDevice)
    }
    
    /**
     * Handle unsupported USB device attachment
     */
    private fun handleUnsupportedDeviceAttached(context: Context, usbDevice: UsbDevice) {
        android.util.Log.d("UsbController", "[DEBUG_LOG] ⚠ USB device is not a supported Topdon thermal camera")
        android.util.Log.d("UsbController", "[DEBUG_LOG] Supported devices: VID=0x0BDA, PID=0x3901/0x5840/0x5830/0x5838")
        
        // Notify callback
        callback?.onUnsupportedDeviceAttached(usbDevice)
        
        // Optional: Show user notification for unsupported devices
        // This can be configured based on user preferences
        android.util.Log.i("UsbController", "Unsupported USB device connected: ${usbDevice.deviceName}")
    }
    
    /**
     * Get list of currently connected USB devices
     */
    fun getConnectedUsbDevices(context: Context): List<UsbDevice> {
        return usbDeviceManager.getConnectedUsbDevices(context)
    }
    
    /**
     * Get list of connected supported TOPDON devices
     */
    fun getConnectedSupportedDevices(context: Context): List<UsbDevice> {
        return usbDeviceManager.getConnectedSupportedDevices(context)
    }
    
    /**
     * Check if any supported TOPDON devices are currently connected
     */
    fun hasSupportedDeviceConnected(context: Context): Boolean {
        return usbDeviceManager.hasSupportedDeviceConnected(context)
    }
    
    /**
     * Check if the USB device is a supported TOPDON device
     * Delegates to UsbDeviceManager for consistency
     */
    fun isSupportedTopdonDevice(device: UsbDevice): Boolean {
        return usbDeviceManager.isSupportedTopdonDevice(device)
    }
    
    /**
     * Get device information string for display
     */
    fun getDeviceInfoString(device: UsbDevice): String {
        return usbDeviceManager.getDeviceInfoString(device)
    }
    
    /**
     * Initialize USB monitoring for already connected devices
     * Implements periodic scanning for device state changes
     */
    fun initializeUsbMonitoring(context: Context) {
        android.util.Log.d("UsbController", "[DEBUG_LOG] Initializing USB monitoring...")
        
        // Restore previous multi-device state
        restoreMultiDeviceState(context)
        
        // Initial device scan
        scanForDevices(context)
        
        // Start periodic scanning
        startPeriodicScanning(context)
    }
    
    /**
     * Start periodic USB device scanning
     */
    private fun startPeriodicScanning(context: Context) {
        if (isScanning) {
            android.util.Log.d("UsbController", "[DEBUG_LOG] USB scanning already active")
            return
        }
        
        isScanning = true
        android.util.Log.d("UsbController", "[DEBUG_LOG] Starting periodic USB device scanning (${SCANNING_INTERVAL_MS}ms interval)")
        
        val scanningRunnable = object : Runnable {
            override fun run() {
                if (isScanning) {
                    scanForDevices(context)
                    scanningHandler.postDelayed(this, SCANNING_INTERVAL_MS)
                }
            }
        }
        
        scanningHandler.postDelayed(scanningRunnable, SCANNING_INTERVAL_MS)
    }
    
    /**
     * Stop periodic USB device scanning
     */
    fun stopPeriodicScanning() {
        if (isScanning) {
            isScanning = false
            scanningHandler.removeCallbacksAndMessages(null)
            android.util.Log.d("UsbController", "[DEBUG_LOG] USB periodic scanning stopped")
        }
    }
    
    /**
     * Scan for USB devices and detect changes
     */
    private fun scanForDevices(context: Context) {
        try {
            val connectedDevices = getConnectedUsbDevices(context)
            val currentDeviceNames = connectedDevices.map { it.deviceName }.toSet()
            
            // Detect newly connected devices
            val newDevices = currentDeviceNames - lastKnownDevices
            val removedDevices = lastKnownDevices - currentDeviceNames
            
            // Handle newly connected devices
            newDevices.forEach { deviceName ->
                val device = connectedDevices.find { it.deviceName == deviceName }
                device?.let {
                    android.util.Log.d("UsbController", "[DEBUG_LOG] Detected new USB device: $deviceName")
                    if (usbDeviceManager.isSupportedTopdonDevice(it)) {
                        handleSupportedDeviceAttached(context, it)
                    }
                }
            }
            
            // Handle removed devices - update our tracking
            removedDevices.forEach { deviceName ->
                android.util.Log.d("UsbController", "[DEBUG_LOG] USB device disconnected: $deviceName")
                
                // Find and remove from our tracking by device name
                val keysToRemove = connectedSupportedDevices.filter { (_, device) -> 
                    device.deviceName == deviceName 
                }.keys
                
                keysToRemove.forEach { key ->
                    connectedSupportedDevices.remove(key)
                }
                
                // Update status and save state if we removed supported devices
                if (keysToRemove.isNotEmpty()) {
                    callback?.updateStatusText(getMultiDeviceStatusText())
                    saveMultiDeviceState(context)
                }
            }
            
            // Update known devices
            lastKnownDevices = currentDeviceNames.toMutableSet()
            
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Error during USB device scanning: ${e.message}")
        }
    }
    
    /**
     * Get USB device status summary for debugging - enhanced for multiple devices
     */
    fun getUsbStatusSummary(context: Context): String {
        val connectedDevices = getConnectedUsbDevices(context)
        val supportedDevices = getConnectedSupportedDevices(context)
        val trackedSupportedDevices = connectedSupportedDevices.size
        val lastDeviceInfo = getLastConnectedDeviceInfo(context)
        
        return buildString {
            append("Enhanced USB Status Summary:\n")
            append("- Total connected devices: ${connectedDevices.size}\n")
            append("- Supported TOPDON devices (system): ${supportedDevices.size}\n")
            append("- Tracked supported devices (controller): $trackedSupportedDevices\n")
            append("- Last connected device: $lastDeviceInfo\n")
            append("- Total connections: ${getConnectionCount(context)}\n")
            
            if (connectedSupportedDevices.isNotEmpty()) {
                append("- Tracked supported devices:\n")
                connectedSupportedDevices.forEach { (key, device) ->
                    val connectionTime = deviceConnectionTimes[key]
                    val connectionCount = deviceConnectionCounts[key] ?: 0
                    val timeStr = if (connectionTime != null) {
                        val format = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
                        format.format(java.util.Date(connectionTime))
                    } else "Unknown"
                    
                    append("  • ${device.deviceName} (Key: $key)\n")
                    append("    VID: 0x${String.format("%04X", device.vendorId)}, PID: 0x${String.format("%04X", device.productId)}\n")
                    append("    Connected: $timeStr, Count: $connectionCount\n")
                }
            }
            
            if (supportedDevices.isNotEmpty() && supportedDevices.size != trackedSupportedDevices) {
                append("- System-detected but not tracked:\n")
                supportedDevices.forEach { device ->
                    val key = getDeviceKey(device)
                    if (!connectedSupportedDevices.containsKey(key)) {
                        append("  • ${device.deviceName} (VID: 0x${String.format("%04X", device.vendorId)}, PID: 0x${String.format("%04X", device.productId)})\n")
                    }
                }
            }
        }
    }
    
    /**
     * Save device connection state for persistence across app restarts
     */
    private fun saveDeviceConnectionState(context: Context, device: UsbDevice) {
        try {
            val prefs = context.getSharedPreferences(USB_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().apply {
                putString(PREF_LAST_CONNECTED_DEVICE, device.deviceName)
                putLong(PREF_LAST_CONNECTION_TIME, System.currentTimeMillis())
                putInt(PREF_DEVICE_VENDOR_ID, device.vendorId)
                putInt(PREF_DEVICE_PRODUCT_ID, device.productId)
                putInt(PREF_CONNECTION_COUNT, getConnectionCount(context) + 1)
                apply()
            }
            
            android.util.Log.d("UsbController", "[DEBUG_LOG] Device state saved: ${device.deviceName}")
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Failed to save device state: ${e.message}")
        }
    }
    
    /**
     * Get information about the last connected device
     */
    private fun getLastConnectedDeviceInfo(context: Context): String {
        return try {
            val prefs = context.getSharedPreferences(USB_PREFS_NAME, Context.MODE_PRIVATE)
            val deviceName = prefs.getString(PREF_LAST_CONNECTED_DEVICE, null)
            val lastConnectionTime = prefs.getLong(PREF_LAST_CONNECTION_TIME, 0L)
            
            if (deviceName != null && lastConnectionTime > 0) {
                val timeFormat = java.text.SimpleDateFormat("MMM dd, HH:mm", java.util.Locale.getDefault())
                "$deviceName (${timeFormat.format(java.util.Date(lastConnectionTime))})"
            } else {
                "None"
            }
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Failed to get last device info: ${e.message}")
            "Error retrieving info"
        }
    }
    
    /**
     * Get total connection count
     */
    private fun getConnectionCount(context: Context): Int {
        return try {
            val prefs = context.getSharedPreferences(USB_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.getInt(PREF_CONNECTION_COUNT, 0)
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Failed to get connection count: ${e.message}")
            0
        }
    }
    
    /**
     * Check if a previously connected device is available
     */
    fun hasPreviouslyConnectedDevice(context: Context): Boolean {
        return try {
            val prefs = context.getSharedPreferences(USB_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.getString(PREF_LAST_CONNECTED_DEVICE, null) != null
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Failed to check previous device: ${e.message}")
            false
        }
    }
    
    // ========== Multiple Device Support Methods ==========
    
    /**
     * Generate a unique key for a USB device based on vendor ID, product ID, and device name
     */
    private fun getDeviceKey(device: UsbDevice): String {
        return "${device.vendorId}_${device.productId}_${device.deviceName}"
    }
    
    /**
     * Get all currently connected and tracked supported devices
     */
    fun getConnectedSupportedDevicesList(): List<UsbDevice> {
        return connectedSupportedDevices.values.toList()
    }
    
    /**
     * Get count of currently connected supported devices
     */
    fun getConnectedSupportedDeviceCount(): Int {
        return connectedSupportedDevices.size
    }
    
    /**
     * Get device information for a specific device by key
     */
    fun getDeviceInfoByKey(deviceKey: String): UsbDevice? {
        return connectedSupportedDevices[deviceKey]
    }
    
    /**
     * Check if a specific device (by key) is currently connected
     */
    fun isDeviceConnected(deviceKey: String): Boolean {
        return connectedSupportedDevices.containsKey(deviceKey)
    }
    
    /**
     * Get connection time for a specific device
     */
    fun getDeviceConnectionTime(deviceKey: String): Long? {
        return deviceConnectionTimes[deviceKey]
    }
    
    /**
     * Get connection count for a specific device
     */
    fun getDeviceConnectionCount(deviceKey: String): Int {
        return deviceConnectionCounts[deviceKey] ?: 0
    }
    
    /**
     * Generate status text for multiple device scenario
     */
    private fun getMultiDeviceStatusText(): String {
        val deviceCount = connectedSupportedDevices.size
        return when (deviceCount) {
            0 -> "No thermal cameras connected"
            1 -> "1 Topdon thermal camera connected - Ready for recording"
            else -> "$deviceCount Topdon thermal cameras connected - Ready for multi-device recording"
        }
    }
    
    /**
     * Save state for multiple devices
     */
    private fun saveMultiDeviceState(context: Context) {
        try {
            val prefs = context.getSharedPreferences(USB_PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().apply {
                putInt("connected_device_count", connectedSupportedDevices.size)
                putStringSet("connected_device_keys", connectedSupportedDevices.keys)
                
                // Save individual device info
                connectedSupportedDevices.forEach { (key, device) ->
                    putString("device_${key}_name", device.deviceName)
                    putInt("device_${key}_vendor", device.vendorId)
                    putInt("device_${key}_product", device.productId)
                    putLong("device_${key}_connected_time", deviceConnectionTimes[key] ?: 0L)
                    putInt("device_${key}_connection_count", deviceConnectionCounts[key] ?: 0)
                }
                
                apply()
            }
            
            android.util.Log.d("UsbController", "[DEBUG_LOG] Multi-device state saved: ${connectedSupportedDevices.size} devices")
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Failed to save multi-device state: ${e.message}")
        }
    }
    
    /**
     * Restore multi-device state from preferences
     */
    fun restoreMultiDeviceState(context: Context) {
        try {
            val prefs = context.getSharedPreferences(USB_PREFS_NAME, Context.MODE_PRIVATE)
            val deviceKeys = prefs.getStringSet("connected_device_keys", emptySet()) ?: emptySet()
            
            android.util.Log.d("UsbController", "[DEBUG_LOG] Restoring multi-device state for ${deviceKeys.size} devices")
            
            // Clear current tracking (will be rebuilt from current scan)
            connectedSupportedDevices.clear()
            deviceConnectionTimes.clear()
            
            // Restore connection counts and times for tracking
            deviceKeys.forEach { key ->
                val connectionCount = prefs.getInt("device_${key}_connection_count", 0)
                val lastConnectionTime = prefs.getLong("device_${key}_connected_time", 0L)
                
                if (connectionCount > 0) {
                    deviceConnectionCounts[key] = connectionCount
                }
                if (lastConnectionTime > 0L) {
                    deviceConnectionTimes[key] = lastConnectionTime
                }
            }
            
        } catch (e: Exception) {
            android.util.Log.e("UsbController", "[DEBUG_LOG] Failed to restore multi-device state: ${e.message}")
        }
    }
    
    /**
     * Get summary of all tracked devices (connected and historical)
     */
    fun getMultiDeviceStatusSummary(context: Context): String {
        val currentDevices = connectedSupportedDevices.size
        val lastDeviceInfo = getLastConnectedDeviceInfo(context)
        val totalConnections = getConnectionCount(context)
        
        return buildString {
            append("Multi-Device USB Status Summary:\n")
            append("- Currently connected TOPDON devices: $currentDevices\n")
            append("- Last connected device: $lastDeviceInfo\n")
            append("- Total historical connections: $totalConnections\n")
            
            if (connectedSupportedDevices.isNotEmpty()) {
                append("- Currently connected devices:\n")
                connectedSupportedDevices.forEach { (key, device) ->
                    val connectionTime = deviceConnectionTimes[key]
                    val connectionCount = deviceConnectionCounts[key] ?: 0
                    val timeStr = if (connectionTime != null) {
                        val format = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
                        format.format(java.util.Date(connectionTime))
                    } else "Unknown"
                    
                    append("  • ${device.deviceName} (Key: $key)\n")
                    append("    VID: 0x${String.format("%04X", device.vendorId)}, PID: 0x${String.format("%04X", device.productId)}\n")
                    append("    Connected at: $timeStr, Total connections: $connectionCount\n")
                }
            }
            
            if (deviceConnectionCounts.isNotEmpty()) {
                append("- Historical device connections:\n")
                deviceConnectionCounts.forEach { (key, count) ->
                    if (!connectedSupportedDevices.containsKey(key)) {
                        append("  • Device $key: $count connections\n")
                    }
                }
            }
        }
    }
}