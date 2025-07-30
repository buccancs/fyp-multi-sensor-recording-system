package com.multisensor.recording.controllers

import android.content.Context
import android.content.Intent
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
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for USB device scenarios
 * TODO: Implement USB device state persistence across app restarts
 * TODO: Add support for multiple simultaneous USB devices
 */
@Singleton
class UsbController @Inject constructor(
    private val usbDeviceManager: UsbDeviceManager
) {
    
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
            android.util.Log.d("UsbController", "[DEBUG_LOG] USB device detached:")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Device name: ${usbDevice.deviceName}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", usbDevice.vendorId)}")
            android.util.Log.d("UsbController", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", usbDevice.productId)}")
            
            callback?.onDeviceDetached(usbDevice)
            
            // Update status if it was a supported device
            if (usbDeviceManager.isSupportedTopdonDevice(usbDevice)) {
                callback?.updateStatusText("Topdon thermal camera disconnected")
                Toast.makeText(
                    context,
                    "Topdon Thermal Camera Disconnected",
                    Toast.LENGTH_SHORT
                ).show()
            }
        } ?: run {
            android.util.Log.w("UsbController", "[DEBUG_LOG] USB device detachment intent received but no device found")
        }
    }
    
    /**
     * Handle supported TOPDON device attachment
     */
    private fun handleSupportedDeviceAttached(context: Context, usbDevice: UsbDevice) {
        android.util.Log.d("UsbController", "[DEBUG_LOG] ✓ Supported Topdon thermal camera detected!")
        
        // Show user notification
        Toast.makeText(
            context,
            "Topdon Thermal Camera Connected!\nDevice: ${usbDevice.deviceName}",
            Toast.LENGTH_LONG
        ).show()
        
        // Update status
        callback?.updateStatusText("Topdon thermal camera connected - Ready for recording")
        
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
     * TODO: Implement periodic scanning for device state changes
     */
    fun initializeUsbMonitoring(context: Context) {
        android.util.Log.d("UsbController", "[DEBUG_LOG] Initializing USB monitoring...")
        
        val connectedDevices = getConnectedUsbDevices(context)
        android.util.Log.d("UsbController", "[DEBUG_LOG] Found ${connectedDevices.size} connected USB devices")
        
        val supportedDevices = getConnectedSupportedDevices(context)
        if (supportedDevices.isNotEmpty()) {
            android.util.Log.d("UsbController", "[DEBUG_LOG] Found ${supportedDevices.size} supported TOPDON devices")
            supportedDevices.forEach { device ->
                handleSupportedDeviceAttached(context, device)
            }
        } else {
            android.util.Log.d("UsbController", "[DEBUG_LOG] No supported TOPDON devices currently connected")
        }
    }
    
    /**
     * Get USB device status summary for debugging
     */
    fun getUsbStatusSummary(context: Context): String {
        val connectedDevices = getConnectedUsbDevices(context)
        val supportedDevices = getConnectedSupportedDevices(context)
        
        return buildString {
            append("USB Status Summary:\n")
            append("- Total connected devices: ${connectedDevices.size}\n")
            append("- Supported TOPDON devices: ${supportedDevices.size}\n")
            if (supportedDevices.isNotEmpty()) {
                append("- Supported devices:\n")
                supportedDevices.forEach { device ->
                    append("  • ${device.deviceName} (VID: 0x${String.format("%04X", device.vendorId)}, PID: 0x${String.format("%04X", device.productId)})\n")
                }
            }
        }
    }
}