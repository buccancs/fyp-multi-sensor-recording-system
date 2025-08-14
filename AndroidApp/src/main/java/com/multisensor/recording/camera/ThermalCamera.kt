package com.multisensor.recording.camera

import android.content.Context
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.view.SurfaceView
import android.util.Log
import com.infisense.iruvc.ircmd.ConcreteIRCMDBuilder
import com.infisense.iruvc.ircmd.IRCMD
import com.infisense.iruvc.ircmd.IRCMDType
import com.infisense.iruvc.usb.USBMonitor
import com.infisense.iruvc.uvc.ConcreateUVCBuilder
import com.infisense.iruvc.uvc.UVCCamera
import com.infisense.iruvc.uvc.UVCType
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Streamlined thermal camera implementation based on IRCamera
 * Simplified from the complex ThermalRecorder in the original app
 */
class ThermalCamera(private val context: Context) {
    
    companion object {
        private const val TAG = "ThermalCamera"
        private val SUPPORTED_PRODUCT_IDS = intArrayOf(
            0x3901, 0x5840, 0x5830, 0x5838, 0x5841, 0x5842, 0x3902, 0x3903
        )
    }

    // Camera state
    private val isInitialized = AtomicBoolean(false)
    private val isPreviewActive = AtomicBoolean(false)
    private val isRecording = AtomicBoolean(false)

    // Hardware components
    private var uvcCamera: UVCCamera? = null
    private var ircmd: IRCMD? = null
    private var usbMonitor: USBMonitor? = null
    private var currentDevice: UsbDevice? = null
    private var previewSurface: SurfaceView? = null

    // USB manager
    private var usbManager: UsbManager? = null

    /**
     * Initialize thermal camera - simplified initialization
     */
    fun initialize(surface: SurfaceView? = null): Boolean {
        return try {
            Log.i(TAG, "Initializing thermal camera")
            
            previewSurface = surface
            usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager
            
            setupUsbMonitor()
            checkForDevices()
            
            isInitialized.set(true)
            Log.i(TAG, "Thermal camera initialized successfully")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize thermal camera", e)
            false
        }
    }

    /**
     * Setup USB monitor for device detection
     */
    private fun setupUsbMonitor() {
        try {
            usbMonitor = USBMonitor(context) { device ->
                Log.i(TAG, "USB device connected: ${device.deviceName}")
                if (isSupportedDevice(device)) {
                    currentDevice = device
                    initializeCamera(device)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to setup USB monitor", e)
        }
    }

    /**
     * Check if device is supported thermal camera
     */
    private fun isSupportedDevice(device: UsbDevice): Boolean {
        return SUPPORTED_PRODUCT_IDS.contains(device.productId)
    }

    /**
     * Check for already connected devices
     */
    private fun checkForDevices() {
        try {
            usbManager?.deviceList?.values?.forEach { device ->
                if (isSupportedDevice(device)) {
                    Log.i(TAG, "Found supported thermal camera: ${device.deviceName}")
                    currentDevice = device
                    initializeCamera(device)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error checking for devices", e)
        }
    }

    /**
     * Initialize camera with detected device
     */
    private fun initializeCamera(device: UsbDevice) {
        try {
            Log.i(TAG, "Initializing camera for device: ${device.deviceName}")
            
            // Create UVC camera
            uvcCamera = ConcreateUVCBuilder().apply {
                setType(UVCType.USB_IR_256_384)
                setCallBack { /* Frame callback if needed */ }
            }.build()

            // Initialize thermal commands
            ircmd = ConcreteIRCMDBuilder().apply {
                setIrcmdType(IRCMDType.USB_IR_256_384)
                setIdCamera(0L) // Default camera ID
            }.build()

            Log.i(TAG, "Thermal camera components initialized")
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize camera components", e)
        }
    }

    /**
     * Start camera preview
     */
    fun startPreview(): Boolean {
        if (!isInitialized.get()) {
            Log.w(TAG, "Camera not initialized")
            return false
        }

        if (isPreviewActive.get()) {
            Log.i(TAG, "Preview already active")
            return true
        }

        return try {
            previewSurface?.let { surface ->
                // Start preview using UVC camera
                uvcCamera?.let { camera ->
                    val startPreviewMethod = camera.javaClass.getMethod(
                        "startPreview", 
                        android.view.Surface::class.java
                    )
                    startPreviewMethod.invoke(camera, surface.holder.surface)
                    isPreviewActive.set(true)
                    Log.i(TAG, "Thermal preview started")
                    true
                } ?: false
            } ?: false
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start preview", e)
            false
        }
    }

    /**
     * Stop camera preview
     */
    fun stopPreview(): Boolean {
        return try {
            if (isPreviewActive.get()) {
                uvcCamera?.let { camera ->
                    val stopPreviewMethod = camera.javaClass.getMethod("stopPreview")
                    stopPreviewMethod.invoke(camera)
                    isPreviewActive.set(false)
                    Log.i(TAG, "Thermal preview stopped")
                }
            }
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop preview", e)
            false
        }
    }

    /**
     * Start recording
     */
    fun startRecording(): Boolean {
        if (!isPreviewActive.get()) {
            Log.w(TAG, "Preview not active, cannot start recording")
            return false
        }

        return try {
            // Implementation would depend on specific recording requirements
            isRecording.set(true)
            Log.i(TAG, "Thermal recording started")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start recording", e)
            false
        }
    }

    /**
     * Stop recording
     */
    fun stopRecording(): Boolean {
        return try {
            if (isRecording.get()) {
                // Stop recording logic
                isRecording.set(false)
                Log.i(TAG, "Thermal recording stopped")
            }
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop recording", e)
            false
        }
    }

    /**
     * Check if camera is connected and ready
     */
    fun isConnected(): Boolean {
        return isInitialized.get() && currentDevice != null
    }

    /**
     * Check if preview is running
     */
    fun isPreviewRunning(): Boolean {
        return isPreviewActive.get()
    }

    /**
     * Check if recording is active
     */
    fun isRecordingActive(): Boolean {
        return isRecording.get()
    }

    /**
     * Get device name if connected
     */
    fun getDeviceName(): String {
        return currentDevice?.deviceName ?: "No Device"
    }

    /**
     * Release camera resources
     */
    fun release() {
        try {
            stopRecording()
            stopPreview()
            
            uvcCamera?.let { camera ->
                val destroyMethod = camera.javaClass.getMethod("destroy")
                destroyMethod.invoke(camera)
            }
            
            ircmd?.let { cmd ->
                val closeMethod = cmd.javaClass.getMethod("close")
                closeMethod.invoke(cmd)
            }
            
            usbMonitor = null
            uvcCamera = null
            ircmd = null
            currentDevice = null
            
            isInitialized.set(false)
            isPreviewActive.set(false)
            isRecording.set(false)
            
            Log.i(TAG, "Thermal camera resources released")
        } catch (e: Exception) {
            Log.e(TAG, "Error releasing camera resources", e)
        }
    }
}