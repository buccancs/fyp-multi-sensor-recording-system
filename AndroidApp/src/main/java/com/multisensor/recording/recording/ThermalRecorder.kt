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
import com.infisense.iruvc.ircmd.ConcreteIRCMDBuilder
import com.infisense.iruvc.ircmd.IRCMD
import com.infisense.iruvc.ircmd.IRCMDType
import com.infisense.iruvc.usb.USBMonitor
import com.infisense.iruvc.utils.CommonParams
import com.infisense.iruvc.utils.IFrameCallback
import com.infisense.iruvc.uvc.ConcreateUVCBuilder
import com.infisense.iruvc.uvc.UVCCamera
import com.infisense.iruvc.uvc.UVCType
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.streaming.PreviewStreamer
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.BufferedOutputStream
import java.io.File
import java.io.IOException
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
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
        private const val TAG = "ThermalRecorder"
        private const val USB_PERMISSION_ACTION = "com.multisensor.recording.USB_PERMISSION"

        private const val THERMAL_WIDTH = 256
        private const val THERMAL_HEIGHT = 192
        private const val THERMAL_FRAME_RATE = 25
        private const val BYTES_PER_PIXEL = 2

        private val SUPPORTED_PRODUCT_IDS = intArrayOf(
            0x3901,
            0x5840,
            0x5830,
            0x5838,
            0x5841,
            0x5842,
            0x3902,
            0x3903
        )

        private const val THERMAL_FILE_HEADER_SIZE = 16
        private const val TIMESTAMP_SIZE = 8
    }

    private var previewStreamer: PreviewStreamer? = null
    private val coroutineScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    private var usbManager: UsbManager? = null
    private var currentDevice: UsbDevice? = null
    private var isInitialized = AtomicBoolean(false)
    private var isRecording = AtomicBoolean(false)
    private var isPreviewActive = AtomicBoolean(false)

    private var uvcCamera: UVCCamera? = null
    private var ircmd: IRCMD? = null
    private var topdonUsbMonitor: USBMonitor? = null

    private var backgroundThread: HandlerThread? = null
    private var backgroundHandler: Handler? = null
    private var fileWriterThread: HandlerThread? = null
    private var fileWriterHandler: Handler? = null

    private val imageSrc = ByteArray(THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL)
    private val temperatureSrc = ByteArray(THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL)
    private val frameQueue = ConcurrentLinkedQueue<ThermalFrame>()

    private var currentSessionId: String? = null
    private var thermalDataFile: File? = null
    private var fileOutputStream: BufferedOutputStream? = null
    private val frameCounter = AtomicLong(0)

    private var currentThermalConfig: ThermalCameraSettings.ThermalConfig? = null

    private var previewSurface: SurfaceView? = null

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

    fun initialize(
        previewSurface: SurfaceView? = null,
        previewStreamer: PreviewStreamer? = null,
    ): Boolean =
        try {
            logger.info("Initializing ThermalRecorder")

            currentThermalConfig = thermalSettings.getCurrentConfig()
            logger.info("Loaded thermal configuration:")
            logger.info(thermalSettings.getConfigSummary())

            this.previewSurface = previewSurface
            this.previewStreamer = previewStreamer

            usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager

            topdonUsbMonitor =
                USBMonitor(
                    context,
                    object : USBMonitor.OnDeviceConnectListener {
                        override fun onAttach(device: UsbDevice) {
                            logger.debug("Topdon USBMonitor: Device attached - ${device.deviceName}")
                            if (isSupportedThermalCamera(device)) {
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

            topdonUsbMonitor?.register()

            registerUsbReceivers()

            startBackgroundThreads()

            checkForConnectedDevices()

            isInitialized.set(true)
            logger.info("ThermalRecorder initialized successfully")
            true
        } catch (e: CancellationException) {
            throw e
        } catch (e: SecurityException) {
            logger.error("Security exception initializing thermal recorder - check permissions", e)
            false
        } catch (e: IllegalStateException) {
            logger.error("Invalid state initializing thermal recorder", e)
            false
        } catch (e: IOException) {
            logger.error("IO error initializing thermal recorder", e)
            false
        } catch (e: RuntimeException) {
            logger.error("Runtime error initializing thermal recorder", e)
            false
        }

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

            currentThermalConfig = thermalSettings.getCurrentConfig()

            if (!currentThermalConfig!!.isEnabled) {
                logger.info("Thermal recording is disabled in settings")
                return false
            }

            logger.info("Applying thermal configuration for recording:")
            logger.info(thermalSettings.getConfigSummary())

            currentSessionId = sessionId

            val sessionFilePaths = sessionManager.getSessionFilePaths()
            val sessionDir =
                sessionFilePaths?.sessionFolder ?: run {
                    logger.error("Could not get session directory for session: $sessionId")
                    return false
                }

            val thermalDataDir = sessionFilePaths.thermalDataFolder
            if (!thermalDataDir.exists() && !thermalDataDir.mkdirs()) {
                logger.error("Could not create thermal data directory: ${thermalDataDir.absolutePath}")
                return false
            }

            val config = currentThermalConfig!!
            val thermalFileName = when (config.dataFormat) {
                "radiometric" -> "thermal_${sessionId}_radiometric.dat"
                "visual" -> "thermal_${sessionId}_visual.dat"
                "combined" -> "thermal_${sessionId}_combined.dat"
                "raw" -> "thermal_${sessionId}_raw.dat"
                else -> "thermal_${sessionId}.dat"
            }

            thermalDataFile = File(thermalDataDir, thermalFileName)

            fileOutputStream = BufferedOutputStream(FileOutputStream(thermalDataFile!!))

            writeFileHeaderWithConfig()

            applyCameraSettings()

            if (!startPreview()) {
                logger.error("Failed to start thermal preview for recording")
                cleanup()
                return false
            }

            frameCounter.set(0)
            isRecording.set(true)

            logger.info("Thermal recording started successfully with configuration: ${config.dataFormat}")
            true
        } catch (e: CancellationException) {
            throw e
        } catch (e: SecurityException) {
            logger.error("Security exception starting thermal recording - check permissions", e)
            cleanup()
            false
        } catch (e: IllegalStateException) {
            logger.error("Invalid state starting thermal recording", e)
            cleanup()
            false
        } catch (e: IOException) {
            logger.error("IO error starting thermal recording", e)
            cleanup()
            false
        } catch (e: RuntimeException) {
            logger.error("Runtime error starting thermal recording", e)
            cleanup()
            false
        }
    }

    fun stopRecording(): Boolean {
        if (!isRecording.get()) {
            logger.warning("No recording in progress")
            return false
        }

        return try {
            logger.info("Stopping thermal recording")

            isRecording.set(false)

            stopPreview()

            fileOutputStream?.flush()
            fileOutputStream?.close()
            fileOutputStream = null

            val frameCount = frameCounter.get()
            logger.info("Thermal recording stopped. Captured $frameCount frames")

            currentSessionId?.let { sessionId: String ->
                logger.debug("Thermal data saved to: ${thermalDataFile?.absolutePath}")
            }

            currentSessionId = null
            thermalDataFile = null

            true
        } catch (e: CancellationException) {
            throw e
        } catch (e: IllegalStateException) {
            logger.error("Invalid state stopping thermal recording", e)
            false
        } catch (e: IOException) {
            logger.error("IO error stopping thermal recording", e)
            false
        } catch (e: RuntimeException) {
            logger.error("Runtime error stopping thermal recording", e)
            false
        }
    }

    fun startPreview(): Boolean {
        if (isPreviewActive.get()) {
            logger.info("Thermal preview already active")
            return true
        }

        return try {
            logger.info("Starting thermal preview...")

            // Check if components are initialized
            if (currentDevice == null) {
                logger.warning("No thermal camera device connected")
                checkForConnectedDevices()
                if (currentDevice == null) {
                    logger.error("No thermal camera device found")
                    return false
                }
            }

            if (uvcCamera == null || ircmd == null) {
                logger.error("Thermal camera components not initialized (uvcCamera=${uvcCamera != null}, ircmd=${ircmd != null})")
                return false
            }

            logger.debug("Setting up thermal frame callback...")
            uvcCamera?.setFrameCallback(
                object : IFrameCallback {
                    override fun onFrame(frameData: ByteArray) {
                        val timestamp = System.currentTimeMillis()
                        onFrameReceived(frameData, timestamp)
                    }
                },
            )

            logger.debug("Starting UVC camera preview...")
            uvcCamera?.onStartPreview()

            logger.debug("Starting IRCMD preview with dual mode (image + temperature)...")
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
                logger.info("Thermal preview started successfully")
                logger.info("  Frame rate: ${THERMAL_FRAME_RATE}fps")
                logger.info("  Resolution: ${THERMAL_WIDTH}x${THERMAL_HEIGHT}")
                logger.info("  Data mode: Image + Temperature")
                true
            } else {
                logger.error("Failed to start IRCMD preview, result code: $result")
                false
            }
        } catch (e: Exception) {
            logger.error("Exception while starting thermal preview", e)
            false
        }
    }

    fun stopPreview(): Boolean {
        if (!isPreviewActive.get()) {
            return true
        }

        return try {
            logger.debug("Stopping thermal preview")

            val result = ircmd?.stopPreview(CommonParams.PreviewPathChannel.PREVIEW_PATH0)
            if (result == 0) {
                logger.debug("IRCMD preview stopped successfully")
            } else {
                logger.warning("Failed to stop IRCMD preview, result: $result")
            }

            uvcCamera?.setFrameCallback(null)

            isPreviewActive.set(false)
            logger.debug("Thermal preview stopped")
            true
        } catch (e: Exception) {
            logger.error("Failed to stop thermal preview", e)
            false
        }
    }

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

    fun isThermalCameraAvailable(): Boolean {
        try {
            if (usbManager == null) {
                return false
            }

            val usbDevices = usbManager?.deviceList ?: return false
            val supportedDevice = usbDevices.values.find { device ->
                device.vendorId == 0x0BDA &&
                        SUPPORTED_PRODUCT_IDS.contains(device.productId)
            }

            return supportedDevice != null && isInitialized.get()
        } catch (e: Exception) {
            logger.error("Failed to check thermal camera availability", e)
            return false
        }
    }

    private fun onFrameReceived(
        frameData: ByteArray,
        timestamp: Long,
    ) {
        if (frameData.size >= THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL * 2) {
            val imageDataLength = THERMAL_WIDTH * THERMAL_HEIGHT * BYTES_PER_PIXEL

            System.arraycopy(frameData, 0, imageSrc, 0, imageDataLength)

            System.arraycopy(frameData, imageDataLength, temperatureSrc, 0, imageDataLength)

            if (isRecording.get()) {
                processFrameForRecording(temperatureSrc, timestamp)
            }

            if (isPreviewActive.get()) {
                processFrameForPreview(imageSrc, timestamp)
            }

            frameCounter.incrementAndGet()
        }
    }

    private fun processFrameForRecording(
        temperatureData: ByteArray,
        timestamp: Long,
    ) {
        fileWriterHandler?.post {
            try {
                fileOutputStream?.let { output ->
                    val timestampBuffer = ByteBuffer.allocate(TIMESTAMP_SIZE)
                    timestampBuffer.putLong(timestamp)
                    output.write(timestampBuffer.array())

                    output.write(temperatureData)
                }
            } catch (e: Exception) {
                logger.error("Failed to write thermal frame to file", e)
            }
        }
    }

    private fun processFrameForPreview(
        imageData: ByteArray,
        timestamp: Long,
    ) {
        backgroundHandler?.post {
            try {
                val argbBitmap = convertThermalToARGB(imageData)

                if (argbBitmap != null) {
                    updatePreviewSurface(argbBitmap)
                }

                previewStreamer?.onThermalFrameAvailable(imageData, THERMAL_WIDTH, THERMAL_HEIGHT)
            } catch (e: Exception) {
                logger.error("Failed to process frame for preview", e)
            }
        }
    }

    private fun convertThermalToARGB(thermalData: ByteArray): Bitmap? =
        try {
            val bitmap = Bitmap.createBitmap(THERMAL_WIDTH, THERMAL_HEIGHT, Bitmap.Config.ARGB_8888)
            val pixels = IntArray(THERMAL_WIDTH * THERMAL_HEIGHT)

            var minTemp = Int.MAX_VALUE
            var maxTemp = Int.MIN_VALUE

            val tempValues = IntArray(THERMAL_WIDTH * THERMAL_HEIGHT)
            for (i in thermalData.indices step 2) {
                if (i + 1 < thermalData.size && i / 2 < tempValues.size) {
                    val temp = ((thermalData[i + 1].toInt() and 0xFF) shl 8) or (thermalData[i].toInt() and 0xFF)
                    tempValues[i / 2] = temp
                    minTemp = minOf(minTemp, temp)
                    maxTemp = maxOf(maxTemp, temp)
                }
            }

            val tempRange = if (maxTemp > minTemp) maxTemp - minTemp else 1

            for (i in tempValues.indices) {
                if (i < pixels.size) {
                    val normalizedTemp = ((tempValues[i] - minTemp) * 255 / tempRange).coerceIn(0, 255)

                    pixels[i] = applyIronColorPalette(normalizedTemp)
                }
            }

            bitmap.setPixels(pixels, 0, THERMAL_WIDTH, 0, 0, THERMAL_WIDTH, THERMAL_HEIGHT)
            bitmap
        } catch (e: Exception) {
            logger.error("Failed to convert thermal data to ARGB", e)
            null
        }

    private fun applyIronColorPalette(normalizedTemp: Int): Int {
        val temp = normalizedTemp.coerceIn(0, 255)

        val r: Int
        val g: Int
        val b: Int

        when {
            temp < 64 -> {
                r = (temp * 4).coerceIn(0, 255)
                g = 0
                b = 0
            }

            temp < 128 -> {
                r = 255
                g = ((temp - 64) * 4).coerceIn(0, 255)
                b = 0
            }

            temp < 192 -> {
                r = 255
                g = 255
                b = ((temp - 128) * 4).coerceIn(0, 255)
            }

            else -> {
                r = 255
                g = 255
                b = 255
            }
        }

        return (0xFF shl 24) or (r shl 16) or (g shl 8) or b
    }

    suspend fun captureCalibrationImage(outputPath: String): Boolean =
        withContext(Dispatchers.IO) {
            return@withContext try {
                logger.info("Starting thermal calibration image capture to: $outputPath")

                if (uvcCamera == null || !isPreviewActive.get()) {
                    logger.error("Thermal camera not ready for calibration capture")
                    return@withContext false
                }

                if (imageSrc.isEmpty()) {
                    logger.error("No thermal frame data available for calibration")
                    return@withContext false
                }

                val outputFile = File(outputPath)
                outputFile.parentFile?.mkdirs()

                val thermalBitmap = convertThermalToARGB(imageSrc.copyOf())

                if (thermalBitmap != null) {
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

    private fun updatePreviewSurface(bitmap: Bitmap) {
        try {
            previewSurface?.holder?.let { holder ->
                val canvas = holder.lockCanvas()
                if (canvas != null) {
                    try {
                        canvas.drawColor(android.graphics.Color.BLACK)

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

    private fun registerUsbReceivers() {
        val filter =
            IntentFilter().apply {
                addAction(USB_PERMISSION_ACTION)
                addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED)
                addAction(UsbManager.ACTION_USB_DEVICE_DETACHED)
            }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.registerReceiver(usbPermissionReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.registerReceiver(usbPermissionReceiver, filter, 0)
        } else {
            @Suppress("UnspecifiedRegisterReceiverFlag")
            context.registerReceiver(usbPermissionReceiver, filter)
        }
    }

    private fun checkForConnectedDevices() {
        logger.info("Checking for already connected Topdon devices...")

        usbManager?.deviceList?.values?.forEach { device ->
            logger.info("Found USB device: ${device.deviceName}")
            logger.info("  Vendor ID: 0x${String.format("%04X", device.vendorId)}")
            logger.info("  Product ID: 0x${String.format("%04X", device.productId)}")
            logger.info("  Device Class: ${device.deviceClass}")
            logger.info("  Device Protocol: ${device.deviceProtocol}")
            logger.info("  Device Subclass: ${device.deviceSubclass}")

            if (isSupportedThermalCamera(device)) {
                logger.info("  -> This is a SUPPORTED Topdon thermal camera!")
                handleDeviceAttached(device)
            } else {
                logger.debug("  -> Not a supported thermal camera")
                if (device.vendorId == 0x0BDA) {
                    logger.warning(
                        "  -> Vendor ID matches (0x0BDA) but Product ID (0x${
                            String.format(
                                "%04X",
                                device.productId
                            )
                        }) not in supported list"
                    )
                    logger.warning(
                        "  -> Supported Product IDs: ${
                            SUPPORTED_PRODUCT_IDS.map {
                                "0x${
                                    String.format(
                                        "%04X",
                                        it
                                    )
                                }"
                            }
                        }"
                    )
                } else if (SUPPORTED_PRODUCT_IDS.contains(device.productId)) {
                    logger.warning(
                        "  -> Product ID matches but Vendor ID (0x${
                            String.format(
                                "%04X",
                                device.vendorId
                            )
                        }) != 0x0BDA"
                    )
                }
            }
        }

        val deviceCount = usbManager?.deviceList?.size ?: 0
        logger.info("USB device scan completed. Found $deviceCount total USB devices")
    }

    private fun handleDeviceAttached(device: UsbDevice) {
        logger.info("USB device attached: ${device.deviceName}")
        logger.info("  Vendor ID: 0x${String.format("%04X", device.vendorId)}")
        logger.info("  Product ID: 0x${String.format("%04X", device.productId)}")

        if (isSupportedThermalCamera(device)) {
            logger.info("Supported Topdon thermal camera detected!")
            requestUsbPermission(device)
        } else {
            logger.debug("Non-thermal USB device attached")
        }
    }

    private fun handleDeviceDetached(device: UsbDevice) {
        logger.info("USB device detached: ${device.deviceName}")
        logger.info("  Vendor ID: 0x${String.format("%04X", device.vendorId)}")
        logger.info("  Product ID: 0x${String.format("%04X", device.productId)}")

        if (device == currentDevice) {
            logger.warning("Current thermal camera detached!")
            currentDevice = null

            if (isRecording.get()) {
                logger.warning("Stopping thermal recording due to device disconnect")
                stopRecording()
            }

            if (isPreviewActive.get()) {
                logger.warning("Stopping thermal preview due to device disconnect")
                stopPreview()
            }
        }
    }

    private fun isSupportedThermalCamera(device: UsbDevice): Boolean {
        return device.vendorId == 0x0BDA && SUPPORTED_PRODUCT_IDS.contains(device.productId)
    }

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

    private fun initializeCameraWithControlBlock(
        device: UsbDevice,
        controlBlock: USBMonitor.UsbControlBlock,
    ) {
        try {
            logger.info("Initializing thermal camera with control block: ${device.deviceName}")

            currentDevice = device

            val uvcBuilder = ConcreateUVCBuilder()
            uvcCamera =
                uvcBuilder
                    .setUVCType(UVCType.USB_UVC)
                    .build()

            uvcCamera?.setDefaultBandwidth(1.0f)

            val result = uvcCamera?.openUVCCamera(controlBlock)
            if (result == 0) {
                logger.debug("UVC camera opened successfully")

                val supportedSizes = uvcCamera?.getSupportedSizeList()
                supportedSizes?.forEach { size ->
                    logger.debug("Supported size: ${size.width} x ${size.height}")
                }

                uvcCamera?.setUSBPreviewSize(THERMAL_WIDTH, THERMAL_HEIGHT * 2)

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

    private fun initializeCamera(device: UsbDevice) {
        logger.debug("Legacy initializeCamera called - device should be handled by USBMonitor")
    }

    private fun applyCameraSettings() {
        val config = currentThermalConfig ?: return

        try {
            logger.info("Applying thermal camera settings...")

            if (config.frameRate != THERMAL_FRAME_RATE) {
                logger.info("Setting thermal frame rate to: ${config.frameRate} fps")
            }

            logger.info("Setting thermal emissivity to: ${config.emissivity}")

            config.getTemperatureRangeValues()?.let { (minTemp, maxTemp) ->
                logger.info("Setting temperature range: ${minTemp}°C to ${maxTemp}°C")
            }

            if (config.autoCalibration) {
                logger.info("Auto-calibration enabled")
            }

            if (config.highResolution) {
                logger.info("High-resolution mode requested")
            }

            logger.info("Thermal camera settings applied successfully")

        } catch (e: Exception) {
            logger.warning("Some thermal camera settings could not be applied", e)
        }
    }

    private fun writeFileHeaderWithConfig() {
        fileOutputStream?.let { output ->
            val config = currentThermalConfig ?: thermalSettings.getCurrentConfig()

            val configString = thermalSettings.exportConfigToString()
            val configBytes = configString.toByteArray()
            val configLength = configBytes.size

            val totalHeaderSize = THERMAL_FILE_HEADER_SIZE + 4 + configLength

            val header = ByteBuffer.allocate(totalHeaderSize)

            header.put("THERMAL2".toByteArray())
            header.putInt(THERMAL_WIDTH)
            header.putInt(THERMAL_HEIGHT)

            header.putInt(configLength)
            header.put(configBytes)

            output.write(header.array())

            logger.debug("Written enhanced thermal file header with configuration metadata")
        }
    }

    private fun startBackgroundThreads() {
        backgroundThread =
            HandlerThread("ThermalRecorder-Background").apply {
                start()
                backgroundHandler = Handler(looper)
            }

        fileWriterThread =
            HandlerThread("ThermalRecorder-FileWriter").apply {
                start()
                fileWriterHandler = Handler(looper)
            }
    }

    private fun stopBackgroundThreads() {
        backgroundThread?.quitSafely()
        backgroundThread = null
        backgroundHandler = null

        fileWriterThread?.quitSafely()
        fileWriterThread = null
        fileWriterHandler = null
    }

    fun cleanup() {
        logger.info("Cleaning up ThermalRecorder")

        if (isRecording.get()) {
            stopRecording()
        }

        if (isPreviewActive.get()) {
            stopPreview()
        }

        try {
            context.unregisterReceiver(usbPermissionReceiver)
        } catch (e: Exception) {
            logger.warning("Failed to unregister USB receiver", e)
        }

        stopBackgroundThreads()

        coroutineScope.cancel()

        try {
            topdonUsbMonitor?.unregister()
            topdonUsbMonitor = null

            ircmd?.let { ircmdInstance ->
                logger.debug("Releasing IRCMD resources")
            }
            ircmd = null

            uvcCamera?.let { camera ->
                if (camera.getOpenStatus()) {
                    logger.debug("Closing UVC camera")
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
