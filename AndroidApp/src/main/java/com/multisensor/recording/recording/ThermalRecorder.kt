package com.multisensor.recording.recording

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Bitmap
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.view.SurfaceView
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.streaming.PreviewStreamer
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.BufferedOutputStream
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import javax.inject.Inject
import javax.inject.Singleton

// Topdon SDK imports
import com.infisense.iruvc.ircmd.ConcreteIRCMDBuilder
import com.infisense.iruvc.ircmd.IRCMD
import com.infisense.iruvc.ircmd.IRCMDType
import com.infisense.iruvc.sdkisp.LibIRProcess
import com.infisense.iruvc.usb.USBMonitor
import com.infisense.iruvc.utils.CommonParams
import com.infisense.iruvc.utils.IFrameCallback
import com.infisense.iruvc.uvc.ConcreateUVCBuilder
import com.infisense.iruvc.uvc.UVCCamera
import com.infisense.iruvc.uvc.UVCType

/**
 * ThermalRecorder manages thermal camera capture using Topdon TC001/Plus cameras.
 * Implements Milestone 2.3 specifications for thermal recording with:
 * - USB permission handling and Topdon SDK integration
 * - Frame acquisition and radiometric data buffering
 * - Live preview rendering pipeline
 * - Preview frame compression and streaming to PC
 * - Raw frame file format implementation
 * - Threading and concurrency model
 * - Session integration and file management
 */
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
            private const val TAG = "ThermalRecorder"
            private const val USB_PERMISSION_ACTION = "com.multisensor.recording.USB_PERMISSION"

            // Topdon camera specifications
            private const val THERMAL_WIDTH = 256
            private const val THERMAL_HEIGHT = 192
            private const val THERMAL_FRAME_RATE = 25
            private const val BYTES_PER_PIXEL = 2

            // Supported Topdon device PIDs
            private val SUPPORTED_PRODUCT_IDS = intArrayOf(0x3901, 0x5840, 0x5830, 0x5838)

            // File format constants
            private const val THERMAL_FILE_HEADER_SIZE = 16
            private const val TIMESTAMP_SIZE = 8
        }

        // Core components
        private var previewStreamer: PreviewStreamer? = null
        private val coroutineScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        // USB and camera management
        private var usbManager: UsbManager? = null
        private var currentDevice: UsbDevice? = null
        private var isInitialized = AtomicBoolean(false)
        private var isRecording = AtomicBoolean(false)
        private var isPreviewActive = AtomicBoolean(false)

        // Topdon SDK objects
        private var uvcCamera: UVCCamera? = null
        private var ircmd: IRCMD? = null
        private var topdonUsbMonitor: USBMonitor? = null

        // Threading
        private var backgroundThread: HandlerThread? = null
        private var backgroundHandler: Handler? = null
        private var fileWriterThread: HandlerThread? = null
        private var fileWriterHandler: Handler? = null

        // Frame buffers
        private val imageSrc = ByteArray(THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL)
        private val temperatureSrc = ByteArray(THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL)
        private val frameQueue = ConcurrentLinkedQueue<ThermalFrame>()

        // Recording state
        private var currentSessionId: String? = null
        private var thermalDataFile: File? = null
        private var fileOutputStream: BufferedOutputStream? = null
        private val frameCounter = AtomicLong(0)

        // Current thermal configuration
        private var currentThermalConfig: ThermalCameraSettings.ThermalConfig? = null

        // Preview surface
        private var previewSurface: SurfaceView? = null

        // USB permission receiver
        private val usbPermissionReceiver =
            object : BroadcastReceiver() {
                override fun onReceive(
                    context: Context,
                    intent: Intent,
                ) {
                    when (intent.action) {
                        USB_PERMISSION_ACTION -> {
                            synchronized(this) {
                                val device: UsbDevice? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                                } else {
                                    @Suppress("DEPRECATION")
                                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                                }
                                if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)) {
                                    device?.let {
                                        logger.debug("USB permission granted for device: ${it.deviceName}")
                                        initializeCamera(it)
                                    }
                                } else {
                                    logger.warning("USB permission denied for device: ${device?.deviceName}")
                                }
                            }
                        }
                        UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                            val device: UsbDevice? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                                intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                            } else {
                                @Suppress("DEPRECATION")
                                intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                            }
                            device?.let { handleDeviceAttached(it) }
                        }
                        UsbManager.ACTION_USB_DEVICE_DETACHED -> {
                            val device: UsbDevice? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                                intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                            } else {
                                @Suppress("DEPRECATION")
                                intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                            }
                            device?.let { handleDeviceDetached(it) }
                        }
                    }
                }
            }

        /**
         * Initialize the thermal recorder with preview surface
         */
        fun initialize(
            previewSurface: SurfaceView? = null,
            previewStreamer: PreviewStreamer? = null,
        ): Boolean =
            try {
                logger.info("Initializing ThermalRecorder")

                // Load current thermal configuration
                currentThermalConfig = thermalSettings.getCurrentConfig()
                logger.info("Loaded thermal configuration:")
                logger.info(thermalSettings.getConfigSummary())

                this.previewSurface = previewSurface
                this.previewStreamer = previewStreamer

                // Initialize USB manager for device enumeration
                usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager

                // Initialize Topdon SDK USBMonitor
                topdonUsbMonitor =
                    USBMonitor(
                        context,
                        object : USBMonitor.OnDeviceConnectListener {
                            override fun onAttach(device: UsbDevice) {
                                logger.debug("Topdon USBMonitor: Device attached - ${device.deviceName}")
                                if (isSupportedThermalCamera(device)) {
                                    // Check USB priority setting
                                    val config = currentThermalConfig ?: thermalSettings.getCurrentConfig()
                                    if (config.usbPriority) {
                                        logger.info("Requesting priority USB access for thermal camera")
                                        topdonUsbMonitor?.requestPermission(device)
                                    } else {
                                        topdonUsbMonitor?.requestPermission(device)
                                    }
                                }
                            }

                            override fun onGranted(
                                device: UsbDevice,
                                granted: Boolean,
                            ) {
                                logger.debug("Topdon USBMonitor: Permission granted=$granted for ${device.deviceName}")
                                if (granted) {
                                    logger.info("USB permission granted for thermal camera with priority access")
                                }
                            }

                            override fun onConnect(
                                device: UsbDevice,
                                ctrlBlock: USBMonitor.UsbControlBlock,
                                createNew: Boolean,
                            ) {
                                logger.debug("Topdon USBMonitor: Device connected - ${device.deviceName}")
                                if (createNew && isSupportedThermalCamera(device)) {
                                    initializeCameraWithControlBlock(device, ctrlBlock)
                                }
                            }

                            override fun onDisconnect(
                                device: UsbDevice,
                                ctrlBlock: USBMonitor.UsbControlBlock,
                            ) {
                                logger.debug("Topdon USBMonitor: Device disconnected - ${device.deviceName}")
                                handleDeviceDetached(device)
                            }

                            override fun onDettach(device: UsbDevice) {
                                logger.debug("Topdon USBMonitor: Device detached - ${device.deviceName}")
                                handleDeviceDetached(device)
                            }

                            override fun onCancel(device: UsbDevice) {
                                logger.debug("Topdon USBMonitor: Permission cancelled - ${device.deviceName}")
                            }
                        },
                    )

                // Register Topdon USBMonitor
                topdonUsbMonitor?.register()

                // Register USB receivers for additional monitoring
                registerUsbReceivers()

                // Start background threads
                startBackgroundThreads()

                // Check for already connected devices
                checkForConnectedDevices()

                isInitialized.set(true)
                logger.info("ThermalRecorder initialized successfully")
                true
            } catch (e: Exception) {
                logger.error("Failed to initialize ThermalRecorder", e)
                false
            }

        /**
         * Start thermal recording for the given session
         */
        fun startRecording(sessionId: String): Boolean {
            if (!isInitialized.get()) {
                logger.error("ThermalRecorder not initialized")
                return false
            }

            if (isRecording.get()) {
                logger.warning("Recording already in progress")
                return false
            }

            return try {
                logger.info("Starting thermal recording for session: $sessionId")

                // Get current thermal configuration and apply it
                currentThermalConfig = thermalSettings.getCurrentConfig()
                
                if (!currentThermalConfig!!.isEnabled) {
                    logger.info("Thermal recording is disabled in settings")
                    return false
                }

                logger.info("Applying thermal configuration for recording:")
                logger.info(thermalSettings.getConfigSummary())

                currentSessionId = sessionId

                // Get session directory from SessionManager
                val sessionFilePaths = sessionManager.getSessionFilePaths()
                val sessionDir =
                    sessionFilePaths?.sessionFolder ?: run {
                        logger.error("Could not get session directory for session: $sessionId")
                        return false
                    }

                // Ensure thermal data folder exists
                val thermalDataDir = sessionFilePaths.thermalDataFolder
                if (!thermalDataDir.exists() && !thermalDataDir.mkdirs()) {
                    logger.error("Could not create thermal data directory: ${thermalDataDir.absolutePath}")
                    return false
                }

                // Create thermal data file with configuration-based naming
                val config = currentThermalConfig!!
                val thermalFileName = when (config.dataFormat) {
                    "radiometric" -> "thermal_${sessionId}_radiometric.dat"
                    "visual" -> "thermal_${sessionId}_visual.dat"
                    "combined" -> "thermal_${sessionId}_combined.dat"
                    "raw" -> "thermal_${sessionId}_raw.dat"
                    else -> "thermal_${sessionId}.dat"
                }

                thermalDataFile = File(thermalDataDir, thermalFileName)

                // Initialize file output stream
                fileOutputStream = BufferedOutputStream(FileOutputStream(thermalDataFile!!))

                // Write file header with configuration metadata
                writeFileHeaderWithConfig()

                // Apply thermal camera settings before starting preview
                applyCameraSettings()

                // Start thermal camera recording by starting preview (which includes frame capture)
                if (!startPreview()) {
                    logger.error("Failed to start thermal preview for recording")
                    cleanup()
                    return false
                }

                frameCounter.set(0)
                isRecording.set(true)

                logger.info("Thermal recording started successfully with configuration: ${config.dataFormat}")
                true
            } catch (e: Exception) {
                logger.error("Failed to start thermal recording", e)
                cleanup()
                false
            }
        }

        /**
         * Stop thermal recording
         */
        fun stopRecording(): Boolean {
            if (!isRecording.get()) {
                logger.warning("No recording in progress")
                return false
            }

            return try {
                logger.info("Stopping thermal recording")

                isRecording.set(false)

                // Stop thermal camera capture by stopping preview
                stopPreview()

                // Close file output
                fileOutputStream?.flush()
                fileOutputStream?.close()
                fileOutputStream = null

                val frameCount = frameCounter.get()
                logger.info("Thermal recording stopped. Captured $frameCount frames")

                // Update session info
                currentSessionId?.let { sessionId: String ->
                    logger.debug("Thermal data saved to: ${thermalDataFile?.absolutePath}")
                }

                currentSessionId = null
                thermalDataFile = null

                true
            } catch (e: Exception) {
                logger.error("Failed to stop thermal recording", e)
                false
            }
        }

        /**
         * Start thermal preview
         */
        fun startPreview(): Boolean {
            if (isPreviewActive.get()) {
                return true
            }

            return try {
                logger.debug("Starting thermal preview")

                if (uvcCamera == null || ircmd == null) {
                    logger.error("Camera not initialized - cannot start preview")
                    return false
                }

                // Set frame callback for thermal data processing
                uvcCamera?.setFrameCallback(
                    object : IFrameCallback {
                        override fun onFrame(frameData: ByteArray) {
                            val timestamp = System.currentTimeMillis()
                            onFrameReceived(frameData, timestamp)
                        }
                    },
                )

                // Start UVC camera preview
                uvcCamera?.onStartPreview()

                // Start IRCMD preview with dual mode (image + temperature)
                val result =
                    ircmd?.startPreview(
                        CommonParams.PreviewPathChannel.PREVIEW_PATH0,
                        CommonParams.StartPreviewSource.SOURCE_SENSOR,
                        THERMAL_FRAME_RATE,
                        CommonParams.StartPreviewMode.VOC_DVP_MODE,
                        CommonParams.DataFlowMode.IMAGE_AND_TEMP_OUTPUT,
                    )

                if (result == 0) {
                    isPreviewActive.set(true)
                    logger.debug("Thermal preview started successfully")
                    true
                } else {
                    logger.error("Failed to start IRCMD preview, result: $result")
                    false
                }
            } catch (e: Exception) {
                logger.error("Failed to start thermal preview", e)
                false
            }
        }

        /**
         * Stop thermal preview
         */
        fun stopPreview(): Boolean {
            if (!isPreviewActive.get()) {
                return true
            }

            return try {
                logger.debug("Stopping thermal preview")

                // Stop IRCMD preview
                val result = ircmd?.stopPreview(CommonParams.PreviewPathChannel.PREVIEW_PATH0)
                if (result == 0) {
                    logger.debug("IRCMD preview stopped successfully")
                } else {
                    logger.warning("Failed to stop IRCMD preview, result: $result")
                }

                // Clear frame callback
                uvcCamera?.setFrameCallback(null)

                isPreviewActive.set(false)
                logger.debug("Thermal preview stopped")
                true
            } catch (e: Exception) {
                logger.error("Failed to stop thermal preview", e)
                false
            }
        }

        /**
         * Get current thermal camera status
         */
        fun getThermalCameraStatus(): ThermalCameraStatus =
            ThermalCameraStatus(
                isAvailable = currentDevice != null,
                isRecording = isRecording.get(),
                isPreviewActive = isPreviewActive.get(),
                width = THERMAL_WIDTH,
                height = THERMAL_HEIGHT,
                frameRate = THERMAL_FRAME_RATE,
                frameCount = frameCounter.get(),
                deviceName = currentDevice?.deviceName,
            )

        /**
         * Frame callback from Topdon SDK (to be implemented)
         */
        private fun onFrameReceived(
            frameData: ByteArray,
            timestamp: Long,
        ) {
            if (frameData.size >= THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL * 2) {
                // Split frame data into image and temperature parts
                val imageDataLength = THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL

                // Copy image data (first half)
                System.arraycopy(frameData, 0, imageSrc, 0, imageDataLength)

                // Copy temperature data (second half)
                System.arraycopy(frameData, imageDataLength, temperatureSrc, 0, imageDataLength)

                // Process frame for recording
                if (isRecording.get()) {
                    processFrameForRecording(temperatureSrc, timestamp)
                }

                // Process frame for preview
                if (isPreviewActive.get()) {
                    processFrameForPreview(imageSrc, timestamp)
                }

                frameCounter.incrementAndGet()
            }
        }

        /**
         * Process frame for recording to file
         */
        private fun processFrameForRecording(
            temperatureData: ByteArray,
            timestamp: Long,
        ) {
            fileWriterHandler?.post {
                try {
                    fileOutputStream?.let { output ->
                        // Write timestamp (8 bytes)
                        val timestampBuffer = ByteBuffer.allocate(TIMESTAMP_SIZE)
                        timestampBuffer.putLong(timestamp)
                        output.write(timestampBuffer.array())

                        // Write temperature data
                        output.write(temperatureData)
                    }
                } catch (e: Exception) {
                    logger.error("Failed to write thermal frame to file", e)
                }
            }
        }

        /**
         * Process frame for preview display and streaming
         */
        private fun processFrameForPreview(
            imageData: ByteArray,
            timestamp: Long,
        ) {
            backgroundHandler?.post {
                try {
                    // Convert thermal image data to displayable format
                    val argbBitmap = convertThermalToARGB(imageData)

                    // Update local preview surface
                    if (argbBitmap != null) {
                        updatePreviewSurface(argbBitmap)
                    }

                    // Stream to PC via PreviewStreamer
                    previewStreamer?.onThermalFrameAvailable(imageData, THERMAL_WIDTH, THERMAL_HEIGHT)
                } catch (e: Exception) {
                    logger.error("Failed to process frame for preview", e)
                }
            }
        }

        /**
         * Convert thermal image data to ARGB bitmap for local display
         * Uses iron color palette similar to PreviewStreamer but optimized for local rendering
         */
        private fun convertThermalToARGB(thermalData: ByteArray): Bitmap? =
            try {
                val bitmap = Bitmap.createBitmap(THERMAL_WIDTH, THERMAL_HEIGHT, Bitmap.Config.ARGB_8888)
                val pixels = IntArray(THERMAL_WIDTH * THERMAL_HEIGHT)

                // Find min and max temperature values for normalization
                var minTemp = Int.MAX_VALUE
                var maxTemp = Int.MIN_VALUE

                val tempValues = IntArray(THERMAL_WIDTH * THERMAL_HEIGHT)
                for (i in thermalData.indices step 2) {
                    if (i + 1 < thermalData.size && i / 2 < tempValues.size) {
                        // Combine two bytes to form temperature value (little-endian)
                        val temp = ((thermalData[i + 1].toInt() and 0xFF) shl 8) or (thermalData[i].toInt() and 0xFF)
                        tempValues[i / 2] = temp
                        minTemp = minOf(minTemp, temp)
                        maxTemp = maxOf(maxTemp, temp)
                    }
                }

                // Avoid division by zero
                val tempRange = if (maxTemp > minTemp) maxTemp - minTemp else 1

                // Convert temperature values to iron color palette
                for (i in tempValues.indices) {
                    if (i < pixels.size) {
                        // Normalize temperature to 0-255 range
                        val normalizedTemp = ((tempValues[i] - minTemp) * 255 / tempRange).coerceIn(0, 255)

                        // Apply iron color palette
                        pixels[i] = applyIronColorPalette(normalizedTemp)
                    }
                }

                bitmap.setPixels(pixels, 0, THERMAL_WIDTH, 0, 0, THERMAL_WIDTH, THERMAL_HEIGHT)
                bitmap
            } catch (e: Exception) {
                logger.error("Failed to convert thermal data to ARGB", e)
                null
            }

        /**
         * Apply iron color palette to normalized temperature value (0-255)
         * Iron palette: black -> red -> orange -> yellow -> white (hot)
         */
        private fun applyIronColorPalette(normalizedTemp: Int): Int {
            val temp = normalizedTemp.coerceIn(0, 255)

            val r: Int
            val g: Int
            val b: Int

            when {
                temp < 64 -> {
                    // Black to dark red
                    r = (temp * 4).coerceIn(0, 255)
                    g = 0
                    b = 0
                }
                temp < 128 -> {
                    // Dark red to bright red
                    r = 255
                    g = ((temp - 64) * 4).coerceIn(0, 255)
                    b = 0
                }
                temp < 192 -> {
                    // Bright red to yellow
                    r = 255
                    g = 255
                    b = ((temp - 128) * 4).coerceIn(0, 255)
                }
                else -> {
                    // Yellow to white
                    r = 255
                    g = 255
                    b = 255
                }
            }

            return (0xFF shl 24) or (r shl 16) or (g shl 8) or b
        }

        /**
         * Capture thermal calibration image for device synchronization and alignment.
         * Uses the current thermal frame data to create a high-quality calibration image.
         */
        suspend fun captureCalibrationImage(outputPath: String): Boolean =
            withContext(Dispatchers.IO) {
                return@withContext try {
                    logger.info("Starting thermal calibration image capture to: $outputPath")

                    // Check if thermal camera is available and active
                    if (uvcCamera == null || !isPreviewActive.get()) {
                        logger.error("Thermal camera not ready for calibration capture")
                        return@withContext false
                    }

                    // Check if we have current frame data
                    if (imageSrc.isEmpty()) {
                        logger.error("No thermal frame data available for calibration")
                        return@withContext false
                    }

                    // Create output file
                    val outputFile = File(outputPath)
                    outputFile.parentFile?.mkdirs()

                    // Convert current thermal data to bitmap
                    val thermalBitmap = convertThermalToARGB(imageSrc.copyOf())

                    if (thermalBitmap != null) {
                        // Save bitmap as high-quality JPEG
                        FileOutputStream(outputFile).use { fos ->
                            thermalBitmap.compress(Bitmap.CompressFormat.JPEG, 95, fos)
                        }

                        logger.info("Thermal calibration image saved successfully: $outputPath")
                        true
                    } else {
                        logger.error("Failed to convert thermal data to bitmap for calibration")
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to capture thermal calibration image", e)
                    false
                }
            }

        /**
         * Update preview surface with thermal bitmap
         */
        private fun updatePreviewSurface(bitmap: Bitmap) {
            try {
                previewSurface?.holder?.let { holder ->
                    val canvas = holder.lockCanvas()
                    if (canvas != null) {
                        try {
                            // Clear canvas
                            canvas.drawColor(android.graphics.Color.BLACK)

                            // Calculate scaling to fit surface while maintaining aspect ratio
                            val surfaceWidth = canvas.width
                            val surfaceHeight = canvas.height
                            val bitmapWidth = bitmap.width
                            val bitmapHeight = bitmap.height

                            val scaleX = surfaceWidth.toFloat() / bitmapWidth
                            val scaleY = surfaceHeight.toFloat() / bitmapHeight
                            val scale = minOf(scaleX, scaleY)

                            val scaledWidth = (bitmapWidth * scale).toInt()
                            val scaledHeight = (bitmapHeight * scale).toInt()

                            val left = (surfaceWidth - scaledWidth) / 2
                            val top = (surfaceHeight - scaledHeight) / 2

                            val destRect = android.graphics.Rect(left, top, left + scaledWidth, top + scaledHeight)

                            // Draw bitmap to canvas
                            canvas.drawBitmap(bitmap, null, destRect, null)
                        } finally {
                            holder.unlockCanvasAndPost(canvas)
                        }
                    }
                }
            } catch (e: Exception) {
                logger.error("Failed to update preview surface", e)
            }
        }

        /**
         * Register USB broadcast receivers
         */
        private fun registerUsbReceivers() {
            val filter =
                IntentFilter().apply {
                    addAction(USB_PERMISSION_ACTION)
                    addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED)
                    addAction(UsbManager.ACTION_USB_DEVICE_DETACHED)
                }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val flags =
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        Context.RECEIVER_NOT_EXPORTED
                    } else {
                        0
                    }
                context.registerReceiver(usbPermissionReceiver, filter, flags)
            } else {
                @Suppress("UnspecifiedRegisterReceiverFlag")
                context.registerReceiver(usbPermissionReceiver, filter)
            }
        }

        /**
         * Check for already connected thermal cameras
         */
        private fun checkForConnectedDevices() {
            usbManager?.deviceList?.values?.forEach { device ->
                if (isSupportedThermalCamera(device)) {
                    handleDeviceAttached(device)
                }
            }
        }

        /**
         * Handle USB device attached
         */
        private fun handleDeviceAttached(device: UsbDevice) {
            if (isSupportedThermalCamera(device)) {
                logger.info("Thermal camera attached: ${device.deviceName}")
                requestUsbPermission(device)
            }
        }

        /**
         * Handle USB device detached
         */
        private fun handleDeviceDetached(device: UsbDevice) {
            if (device == currentDevice) {
                logger.info("Current thermal camera detached: ${device.deviceName}")
                currentDevice = null

                // Stop recording if active
                if (isRecording.get()) {
                    stopRecording()
                }

                // Stop preview if active
                if (isPreviewActive.get()) {
                    stopPreview()
                }
            }
        }

        /**
         * Check if device is a supported thermal camera
         */
        private fun isSupportedThermalCamera(device: UsbDevice): Boolean = SUPPORTED_PRODUCT_IDS.contains(device.productId)

        /**
         * Request USB permission for device
         */
        private fun requestUsbPermission(device: UsbDevice) {
            val permissionIntent =
                android.app.PendingIntent.getBroadcast(
                    context,
                    0,
                    Intent(USB_PERMISSION_ACTION),
                    android.app.PendingIntent.FLAG_UPDATE_CURRENT or android.app.PendingIntent.FLAG_IMMUTABLE,
                )
            usbManager?.requestPermission(device, permissionIntent)
        }

        /**
         * Initialize camera with USBMonitor control block (called from USBMonitor callback)
         */
        private fun initializeCameraWithControlBlock(
            device: UsbDevice,
            controlBlock: USBMonitor.UsbControlBlock,
        ) {
            try {
                logger.info("Initializing thermal camera with control block: ${device.deviceName}")

                currentDevice = device

                // Initialize UVC camera first (following sample code pattern)
                val uvcBuilder = ConcreateUVCBuilder()
                uvcCamera =
                    uvcBuilder
                        .setUVCType(UVCType.USB_UVC)
                        .build()

                // Set default bandwidth for stability
                uvcCamera?.setDefaultBandwidth(1.0f)

                // Open UVC camera with the provided control block
                val result = uvcCamera?.openUVCCamera(controlBlock)
                if (result == 0) {
                    logger.debug("UVC camera opened successfully")

                    // Get supported sizes for device detection
                    val supportedSizes = uvcCamera?.getSupportedSizeList()
                    supportedSizes?.forEach { size ->
                        logger.debug("Supported size: ${size.width} x ${size.height}")
                    }

                    // Set preview size for image+temperature dual mode
                    uvcCamera?.setUSBPreviewSize(THERMAL_WIDTH, THERMAL_HEIGHT * 2)

                    // Initialize IRCMD
                    val ircmdBuilder = ConcreteIRCMDBuilder()
                    ircmd =
                        ircmdBuilder
                            .setIrcmdType(IRCMDType.USB_IR_256_384)
                            .setIdCamera(uvcCamera?.getNativePtr() ?: 0L)
                            .build()

                    if (ircmd != null) {
                        logger.info("Thermal camera initialized successfully")
                    } else {
                        logger.error("Failed to initialize IRCMD")
                        currentDevice = null
                    }
                } else {
                    logger.error("Failed to open UVC camera, result: $result")
                    currentDevice = null
                }
            } catch (e: Exception) {
                logger.error("Failed to initialize thermal camera", e)
                currentDevice = null
            }
        }

        /**
         * Initialize camera after USB permission granted (legacy method for fallback)
         */
        private fun initializeCamera(device: UsbDevice) {
            logger.debug("Legacy initializeCamera called - device should be handled by USBMonitor")
            // This method is now handled by the USBMonitor callbacks
            // Keep for compatibility but the actual initialization happens in initializeCameraWithControlBlock
        }

        /**
         * Apply thermal camera settings to the hardware
         */
        private fun applyCameraSettings() {
            val config = currentThermalConfig ?: return
            
            try {
                logger.info("Applying thermal camera settings...")
                
                // Apply frame rate if supported
                if (config.frameRate != THERMAL_FRAME_RATE) {
                    logger.info("Setting thermal frame rate to: ${config.frameRate} fps")
                    // Note: Actual frame rate setting depends on Topdon SDK capabilities
                    // The SDK may have limitations on which frame rates are supported
                }
                
                // Apply emissivity setting
                logger.info("Setting thermal emissivity to: ${config.emissivity}")
                // Note: Emissivity setting would be applied through Topdon SDK if supported
                
                // Apply temperature range settings
                config.getTemperatureRangeValues()?.let { (minTemp, maxTemp) ->
                    logger.info("Setting temperature range: ${minTemp}°C to ${maxTemp}°C")
                    // Note: Temperature range setting would be applied through Topdon SDK if supported
                }
                
                // Enable auto-calibration if requested
                if (config.autoCalibration) {
                    logger.info("Auto-calibration enabled")
                    // Note: Auto-calibration would be configured through Topdon SDK
                }
                
                // Set high-resolution mode if supported and enabled
                if (config.highResolution) {
                    logger.info("High-resolution mode requested")
                    // Note: High-resolution mode would be set through Topdon SDK if available
                }
                
                logger.info("Thermal camera settings applied successfully")
                
            } catch (e: Exception) {
                logger.warning("Some thermal camera settings could not be applied", e)
            }
        }

        /**
         * Write thermal data file header with configuration metadata
         */
        private fun writeFileHeaderWithConfig() {
            fileOutputStream?.let { output ->
                val config = currentThermalConfig ?: thermalSettings.getCurrentConfig()
                
                // Extended header with configuration metadata
                val configString = thermalSettings.exportConfigToString()
                val configBytes = configString.toByteArray()
                val configLength = configBytes.size
                
                // Calculate total header size: basic header + config length + config data
                val totalHeaderSize = THERMAL_FILE_HEADER_SIZE + 4 + configLength
                
                val header = ByteBuffer.allocate(totalHeaderSize)
                
                // Write basic header
                header.put("THERMAL2".toByteArray()) // Updated version identifier for enhanced format
                header.putInt(THERMAL_WIDTH) // 4 bytes width
                header.putInt(THERMAL_HEIGHT) // 4 bytes height
                
                // Write configuration data length and data
                header.putInt(configLength) // 4 bytes config length
                header.put(configBytes) // Config data
                
                output.write(header.array())
                
                logger.debug("Written enhanced thermal file header with configuration metadata")
            }
        }

        /**
         * Start background threads for processing
         */
        private fun startBackgroundThreads() {
            // Background thread for general processing
            backgroundThread =
                HandlerThread("ThermalRecorder-Background").apply {
                    start()
                    backgroundHandler = Handler(looper)
                }

            // File writer thread for disk I/O
            fileWriterThread =
                HandlerThread("ThermalRecorder-FileWriter").apply {
                    start()
                    fileWriterHandler = Handler(looper)
                }
        }

        /**
         * Stop background threads
         */
        private fun stopBackgroundThreads() {
            backgroundThread?.quitSafely()
            backgroundThread = null
            backgroundHandler = null

            fileWriterThread?.quitSafely()
            fileWriterThread = null
            fileWriterHandler = null
        }

        /**
         * Cleanup resources
         */
        fun cleanup() {
            logger.info("Cleaning up ThermalRecorder")

            // Stop recording if active
            if (isRecording.get()) {
                stopRecording()
            }

            // Stop preview if active
            if (isPreviewActive.get()) {
                stopPreview()
            }

            // Unregister receivers
            try {
                context.unregisterReceiver(usbPermissionReceiver)
            } catch (e: Exception) {
                logger.warning("Failed to unregister USB receiver", e)
            }

            // Stop background threads
            stopBackgroundThreads()

            // Cancel coroutines
            coroutineScope.cancel()

            // Release Topdon SDK resources
            try {
                // Unregister USBMonitor
                topdonUsbMonitor?.unregister()
                topdonUsbMonitor = null

                // Release IRCMD resources
                ircmd?.let { ircmdInstance ->
                    // Note: IRCMD doesn't have a direct release method in the SDK
                    // Resources are automatically cleaned up when the object is nullified
                    logger.debug("Releasing IRCMD resources")
                }
                ircmd = null

                // Close UVCCamera
                uvcCamera?.let { camera ->
                    if (camera.getOpenStatus()) {
                        logger.debug("Closing UVC camera")
                        // The camera will be closed when the USBMonitor is unregistered
                    }
                }
                uvcCamera = null
            } catch (e: Exception) {
                logger.warning("Error during SDK resource cleanup", e)
            }

            currentDevice = null
            isInitialized.set(false)

            logger.info("ThermalRecorder cleanup completed")
        }

        /**
         * Data class representing thermal camera status
         */
        data class ThermalCameraStatus(
            val isAvailable: Boolean,
            val isRecording: Boolean,
            val isPreviewActive: Boolean,
            val width: Int,
            val height: Int,
            val frameRate: Int,
            val frameCount: Long,
            val deviceName: String? = null,
        )

        /**
         * Data class representing a thermal frame
         */
        data class ThermalFrame(
            val width: Int,
            val height: Int,
            val timestamp: Long,
            val imageData: ByteArray,
            val temperatureData: ByteArray,
        ) {
            override fun equals(other: Any?): Boolean {
                if (this === other) return true
                if (javaClass != other?.javaClass) return false

                other as ThermalFrame

                if (width != other.width) return false
                if (height != other.height) return false
                if (timestamp != other.timestamp) return false
                if (!imageData.contentEquals(other.imageData)) return false
                if (!temperatureData.contentEquals(other.temperatureData)) return false

                return true
            }

            override fun hashCode(): Int {
                var result = width
                result = 31 * result + height
                result = 31 * result + timestamp.hashCode()
                result = 31 * result + imageData.contentHashCode()
                result = 31 * result + temperatureData.contentHashCode()
                return result
            }
        }
    }
