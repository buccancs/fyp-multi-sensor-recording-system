package com.multisensor.recording.managers

import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Build
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager class responsible for handling all USB device-related logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 */
@Singleton
class UsbDeviceManager @Inject constructor() {
    
    /**
     * Interface for USB device callbacks
     */
    interface UsbDeviceCallback {
        fun onSupportedDeviceAttached(device: UsbDevice)
        fun onUnsupportedDeviceAttached(device: UsbDevice)
        fun onDeviceDetached(device: UsbDevice)
        fun onError(message: String)
    }
    
    // Supported TOPDON device vendor/product IDs
    // Based on device_filter.xml and actual TOPDON TC001 series cameras
    private val supportedDevices = listOf(
        Pair(0x0BDA, 0x3901), // TOPDON TC001 series cameras
        Pair(0x0BDA, 0x5840), // TOPDON TC001 Plus
        Pair(0x0BDA, 0x5830), // TOPDON TC001 variant
        Pair(0x0BDA, 0x5838), // TOPDON TC001 variant
    )
    
    /**
     * Handle USB device intent from system
     */
    fun handleUsbDeviceIntent(intent: Intent, callback: UsbDeviceCallback) {
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Handling USB device intent: ${intent.action}")
        
        try {
            when (intent.action) {
                UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                    val usbDevice = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra<UsbDevice>(UsbManager.EXTRA_DEVICE)
                    }
                    if (usbDevice != null) {
                        handleDeviceAttached(usbDevice, callback)
                    } else {
                        android.util.Log.w("UsbDeviceManager", "[DEBUG_LOG] USB device attached but no device in intent")
                        callback.onError("USB device attached but no device information available")
                    }
                }
                
                UsbManager.ACTION_USB_DEVICE_DETACHED -> {
                    val usbDevice = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra<UsbDevice>(UsbManager.EXTRA_DEVICE)
                    }
                    if (usbDevice != null) {
                        handleDeviceDetached(usbDevice, callback)
                    } else {
                        android.util.Log.w("UsbDeviceManager", "[DEBUG_LOG] USB device detached but no device in intent")
                    }
                }
                
                else -> {
                    android.util.Log.w("UsbDeviceManager", "[DEBUG_LOG] Unhandled USB intent action: ${intent.action}")
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("UsbDeviceManager", "[DEBUG_LOG] Error handling USB device intent: ${e.message}")
            callback.onError("Failed to handle USB device intent: ${e.message}")
        }
    }
    
    /**
     * Handle USB device attached event
     */
    private fun handleDeviceAttached(usbDevice: UsbDevice, callback: UsbDeviceCallback) {
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] USB device attached:")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Device name: ${usbDevice.deviceName}")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", usbDevice.vendorId)}")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", usbDevice.productId)}")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Device class: ${usbDevice.deviceClass}")
        
        if (isSupportedTopdonDevice(usbDevice)) {
            android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Supported TOPDON device detected")
            callback.onSupportedDeviceAttached(usbDevice)
        } else {
            android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Unsupported device detected")
            callback.onUnsupportedDeviceAttached(usbDevice)
        }
    }
    
    /**
     * Handle USB device detached event
     */
    private fun handleDeviceDetached(usbDevice: UsbDevice, callback: UsbDeviceCallback) {
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] USB device detached:")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Device name: ${usbDevice.deviceName}")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", usbDevice.vendorId)}")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", usbDevice.productId)}")
        
        callback.onDeviceDetached(usbDevice)
    }
    
    /**
     * Check if the USB device is a supported TOPDON device
     */
    fun isSupportedTopdonDevice(device: UsbDevice): Boolean {
        val vendorId = device.vendorId
        val productId = device.productId
        
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Checking device support:")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", vendorId)}")
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", productId)}")
        
        val isSupported = supportedDevices.any { (supportedVendorId, supportedProductId) ->
            vendorId == supportedVendorId && productId == supportedProductId
        }
        
        android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Device support result: $isSupported")
        return isSupported
    }
    
    /**
     * Get list of currently connected USB devices
     */
    fun getConnectedUsbDevices(context: Context): List<UsbDevice> {
        return try {
            val usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager
            val deviceList = usbManager.deviceList
            
            android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Found ${deviceList.size} connected USB devices")
            
            deviceList.values.toList().also { devices ->
                devices.forEach { device ->
                    android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] - ${device.deviceName}: VID=0x${String.format("%04X", device.vendorId)}, PID=0x${String.format("%04X", device.productId)}")
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("UsbDeviceManager", "[DEBUG_LOG] Error getting connected USB devices: ${e.message}")
            emptyList()
        }
    }
    
    /**
     * Get list of connected supported TOPDON devices
     */
    fun getConnectedSupportedDevices(context: Context): List<UsbDevice> {
        return getConnectedUsbDevices(context).filter { device ->
            isSupportedTopdonDevice(device)
        }.also { supportedDevices ->
            android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Found ${supportedDevices.size} supported TOPDON devices")
        }
    }
    
    /**
     * Check if any supported TOPDON devices are currently connected
     */
    fun hasSupportedDeviceConnected(context: Context): Boolean {
        return getConnectedSupportedDevices(context).isNotEmpty().also { hasSupported ->
            android.util.Log.d("UsbDeviceManager", "[DEBUG_LOG] Has supported device connected: $hasSupported")
        }
    }
    
    /**
     * Get device information string for display
     */
    fun getDeviceInfoString(device: UsbDevice): String {
        return buildString {
            append("${device.deviceName}\n")
            append("Vendor ID: 0x${String.format("%04X", device.vendorId)}\n")
            append("Product ID: 0x${String.format("%04X", device.productId)}\n")
            append("Device Class: ${device.deviceClass}")
        }
    }
    
}