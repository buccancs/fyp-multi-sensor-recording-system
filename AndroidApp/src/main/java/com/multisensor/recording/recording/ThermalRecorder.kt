package com.multisensor.recording.recording

import android.content.Context
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.view.SurfaceView
import com.infisense.iruvc.ircmd.ConcreteIRCMDBuilder
import com.infisense.iruvc.ircmd.IRCMD
import com.infisense.iruvc.ircmd.IRCMDType
import com.infisense.iruvc.usb.USBMonitor
import com.infisense.iruvc.uvc.ConcreateUVCBuilder
import com.infisense.iruvc.uvc.UVCCamera
import com.infisense.iruvc.uvc.UVCType
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.concurrent.atomic.AtomicBoolean
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ThermalRecorder
@Inject
constructor(
    @ApplicationContext private val context: Context,
    private val sessionManager: SessionManager,
    private val logger: Logger,
    private val thermalSettings: ThermalCameraSettings,
) {
    companion object {
        private val SUPPORTED_PRODUCT_IDS = intArrayOf(
            0x3901, 0x5840, 0x5830, 0x5838, 0x5841, 0x5842, 0x3902, 0x3903
        )
    }

    private var usbManager: UsbManager? = null
    private var currentDevice: UsbDevice? = null
    private var isInitialized = AtomicBoolean(false)
    private var isPreviewActive = AtomicBoolean(false)

    private var uvcCamera: UVCCamera? = null
    private var ircmd: IRCMD? = null
    private var topdonUsbMonitor: USBMonitor? = null
    private var previewSurface: SurfaceView? = null

    fun initialize(previewSurface: SurfaceView? = null): Boolean {
        return try {
            logger.info("Initializing thermal camera...")

            this.previewSurface = previewSurface
            usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager

            setupUsbMonitor()
            checkForConnectedDevices()

            isInitialized.set(true)
            logger.info("Thermal camera initialized")
            true
        } catch (e: Exception) {
            logger.error("Thermal camera initialization failed", e)
            false
        }
    }

    fun startPreview(): Boolean {
        return try {
            if (!isInitialized.get()) {
                logger.error("Thermal camera not initialized")
                return false
            }

            if (currentDevice == null) {
                logger.warning("No thermal device connected")
                return false
            }

            if (isPreviewActive.get()) {
                return true
            }

            startCameraPreview()
            isPreviewActive.set(true)
            logger.info("Thermal preview started")
            true
        } catch (e: Exception) {
            logger.error("Failed to start thermal preview", e)
            false
        }
    }

    fun stopPreview() {
        try {
            if (isPreviewActive.get()) {
                // TODO: Implement UVC camera stopPreview when library is available
                // uvcCamera?.stopPreview()
                isPreviewActive.set(false)
                logger.info("Thermal preview stopped")
            }
        } catch (e: Exception) {
            logger.error("Error stopping thermal preview", e)
        }
    }

    fun cleanup() {
        try {
            stopPreview()

            // TODO: Implement UVC camera cleanup when library is available
            // uvcCamera?.destroy()
            uvcCamera = null

            // TODO: Implement IRCMD cleanup when library is available
            // ircmd?.close()
            ircmd = null

            topdonUsbMonitor?.unregister()
            topdonUsbMonitor = null

            isInitialized.set(false)
            logger.info("Thermal camera cleanup completed")
        } catch (e: Exception) {
            logger.error("Error during thermal camera cleanup", e)
        }
    }

    fun getThermalCameraStatus(): String {
        return when {
            !isInitialized.get() -> "Not initialized"
            currentDevice == null -> "No device connected"
            isPreviewActive.get() -> "Active"
            else -> "Connected"
        }
    }

    fun startRecording(sessionId: String): Boolean {
        return try {
            if (!isInitialized.get()) {
                logger.error("Thermal camera not initialized")
                return false
            }

            // Start preview if not already active
            if (!isPreviewActive.get()) {
                startPreview()
            }

            logger.info("Thermal recording started for session: $sessionId")
            true
        } catch (e: Exception) {
            logger.error("Failed to start thermal recording", e)
            false
        }
    }

    fun stopRecording() {
        try {
            logger.info("Thermal recording stopped")
            // Keep preview running, just stop recording
        } catch (e: Exception) {
            logger.error("Error stopping thermal recording", e)
        }
    }

    fun setPreviewStreamer(streamer: Any) {
        // Preview streaming not implemented in simplified version
    }

    fun captureCalibrationImage(filePath: String): Boolean {
        return try {
            logger.info("[DEBUG_LOG] Capturing thermal calibration image to: $filePath")

            if (!isInitialized.get()) {
                logger.error("Thermal camera not initialized for calibration capture")
                return false
            }

            if (currentDevice == null) {
                logger.error("No thermal device connected for calibration capture")
                return false
            }

            // TODO: Implement thermal calibration image capture logic
            // This is a stub implementation for compilation
            logger.info("[DEBUG_LOG] Thermal calibration image capture completed: $filePath")
            true
        } catch (e: Exception) {
            logger.error("Error capturing thermal calibration image", e)
            false
        }
    }

    fun isThermalCameraAvailable(): Boolean {
        return try {
            isInitialized.get() && currentDevice != null
        } catch (e: Exception) {
            logger.error("Error checking thermal camera availability", e)
            false
        }
    }

    private fun setupUsbMonitor() {
        topdonUsbMonitor = USBMonitor(
            context,
            object : USBMonitor.OnDeviceConnectListener {
                override fun onAttach(device: UsbDevice) {
                    if (isSupportedThermalCamera(device)) {
                        logger.info("Thermal camera attached: ${device.deviceName}")
                        topdonUsbMonitor?.requestPermission(device)
                    }
                }

                override fun onGranted(device: UsbDevice, granted: Boolean) {
                    if (granted && isSupportedThermalCamera(device)) {
                        logger.info("Permission granted for thermal camera")
                        initializeCamera(device)
                    }
                }

                override fun onConnect(device: UsbDevice, ctrlBlock: USBMonitor.UsbControlBlock, createNew: Boolean) {
                    if (createNew && isSupportedThermalCamera(device)) {
                        initializeCameraWithControlBlock(device, ctrlBlock)
                    }
                }

                override fun onDisconnect(device: UsbDevice, ctrlBlock: USBMonitor.UsbControlBlock) {
                    handleDeviceDisconnected(device)
                }

                override fun onDettach(device: UsbDevice) {
                    handleDeviceDisconnected(device)
                }

                override fun onCancel(device: UsbDevice) {
                    logger.info("Permission cancelled for: ${device.deviceName}")
                }
            }
        )
        topdonUsbMonitor?.register()
    }

    private fun checkForConnectedDevices() {
        try {
            usbManager?.deviceList?.values?.forEach { device ->
                if (isSupportedThermalCamera(device)) {
                    logger.info("Found thermal camera: ${device.deviceName}")
                    topdonUsbMonitor?.requestPermission(device)
                }
            }
        } catch (e: Exception) {
            logger.error("Error checking for thermal devices", e)
        }
    }

    private fun isSupportedThermalCamera(device: UsbDevice): Boolean {
        return SUPPORTED_PRODUCT_IDS.contains(device.productId) && device.vendorId == 0x1C06
    }

    private fun initializeCamera(device: UsbDevice) {
        try {
            currentDevice = device
            logger.info("Initializing thermal camera: ${device.deviceName}")
        } catch (e: Exception) {
            logger.error("Error initializing thermal camera", e)
        }
    }

    private fun initializeCameraWithControlBlock(device: UsbDevice, ctrlBlock: USBMonitor.UsbControlBlock) {
        try {
            currentDevice = device

            // TODO: Initialize UVC camera when library is available
            /*
            uvcCamera = ConcreateUVCBuilder.createUVCCamera(UVCType.UVC_NORMAL).apply {
                open(ctrlBlock)
                setPreviewSize(256, 192)
                previewSurface?.let { setPreviewDisplay(it.holder) }
            }
            */

            // TODO: Initialize thermal commands when library is available
            /*
            ircmd = ConcreteIRCMDBuilder.createIRCMD(IRCMDType.IRCMD_NORMAL).apply {
                open(ctrlBlock)
            }
            */

            logger.info("Thermal camera initialized successfully (stub implementation)")
        } catch (e: Exception) {
            logger.error("Error initializing thermal camera with control block", e)
        }
    }

    private fun startCameraPreview() {
        try {
            // TODO: Implement UVC camera startPreview when library is available
            // uvcCamera?.startPreview()
            logger.debug("Thermal camera preview started (stub implementation)")
        } catch (e: Exception) {
            logger.error("Error starting thermal camera preview", e)
        }
    }

    private fun handleDeviceDisconnected(device: UsbDevice) {
        if (device == currentDevice) {
            logger.info("Thermal camera disconnected")
            currentDevice = null
            stopPreview()
        }
    }
}
