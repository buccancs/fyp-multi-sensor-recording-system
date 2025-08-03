package com.multisensor.recording.recording

import android.content.Context
import android.graphics.ImageFormat
import android.graphics.SurfaceTexture
import android.hardware.camera2.*
import android.hardware.camera2.params.SessionConfiguration
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.StreamConfigurationMap
import android.media.Image
import android.media.ImageReader
import android.media.MediaRecorder
// DngCreator import - conditionally import based on API availability
import androidx.annotation.RequiresApi
import android.os.Build
// DngCreator only available from API 21+
// import android.media.DngCreator
import android.os.Environment
import android.os.Handler
import android.os.HandlerThread
import android.util.Size
import android.view.Surface
import android.view.TextureView
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.streaming.PreviewStreamer
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import com.multisensor.recording.handsegmentation.HandSegmentationManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.graphics.Rect
import android.graphics.YuvImage
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Semaphore
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * enhanced camera recorder with camera2 api
 * supports preview + 4k video + raw capture
 */
@Singleton
class CameraRecorder
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
        private val sessionManager: SessionManager,
        private val logger: Logger,
        private val handSegmentationManager: HandSegmentationManager,
    ) {
        private var cameraDevice: CameraDevice? = null
        private var captureSession: CameraCaptureSession? = null

        private var previewStreamer: PreviewStreamer? = null

        /**
         * set preview streamer for live streaming
         */
        fun setPreviewStreamer(streamer: PreviewStreamer) {
            previewStreamer = streamer
            logger.info("PreviewStreamer injected into CameraRecorder")
        }

        private var cameraCharacteristics: CameraCharacteristics? = null

        private var mediaRecorder: MediaRecorder? = null
        private var rawImageReader: ImageReader? = null
        private var previewImageReader: ImageReader? = null
        private var textureView: TextureView? = null
        private var previewSurface: Surface? = null

        private var backgroundThread: HandlerThread? = null
        private var backgroundHandler: Handler? = null
        private val cameraLock = Semaphore(1)
        private val cameraDispatcher = Dispatchers.IO.limitedParallelism(1)

        // Session management
        private var currentSessionInfo: SessionInfo? = null
        private var lastRawCaptureResult: TotalCaptureResult? = null
        private var rawCaptureCount = 0

        // Camera configuration
        private var cameraId: String? = null
        private var videoSize: Size = Size(3840, 2160) // 4K UHD
        private var previewSize: Size? = null
        private var rawSize: Size? = null

        // State flags
        private var isInitialized = false
        private var isSessionActive = false

        companion object {
            private const val THREAD_NAME = "CameraRecorder"
            private const val VIDEO_FRAME_RATE = 30
            private const val VIDEO_BIT_RATE = 10_000_000 // 10 Mbps for 4K
            private const val CAMERA_LOCK_TIMEOUT_MS = 2500L

            // Orientation mapping for video recording
            private val ORIENTATIONS =
                mapOf(
                    android.view.Surface.ROTATION_0 to 90,
                    android.view.Surface.ROTATION_90 to 0,
                    android.view.Surface.ROTATION_180 to 270,
                    android.view.Surface.ROTATION_270 to 180,
                )
        }

        /**
         * Initialize the camera recorder with TextureView for live preview.
         * Prepares the camera (selecting appropriate camera and outputs) and binds TextureView.
         *
         * @param textureView TextureView for live preview display
         * @return true if initialization successful, false otherwise
         */
        suspend fun initialize(textureView: TextureView): Boolean =
            withContext(cameraDispatcher) {
                try {
                    if (!cameraLock.tryAcquire(CAMERA_LOCK_TIMEOUT_MS, TimeUnit.MILLISECONDS)) {
                        logger.error("Camera lock timeout during initialization")
                        return@withContext false
                    }

                    try {
                        logger.info("Initializing CameraRecorder with TextureView...")

                        if (isInitialized) {
                            logger.info("CameraRecorder already initialized")
                            return@withContext true
                        }

                        // Store TextureView reference
                        this@CameraRecorder.textureView = textureView

                        // Start background thread
                        startBackgroundThread()

                        // Setup camera
                        val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                        cameraId = selectBestCamera(cameraManager)

                        if (cameraId == null) {
                            logger.error("No suitable camera found with RAW capability")
                            return@withContext false
                        }

                        // Get camera characteristics and configure sizes
                        cameraCharacteristics = cameraManager.getCameraCharacteristics(cameraId!!)
                        configureCameraSizes(cameraCharacteristics!!)

                        // Setup TextureView surface
                        setupTextureViewSurface()

                        isInitialized = true
                        logger.info("CameraRecorder initialized successfully with camera: $cameraId")
                        logger.info("Video size: ${videoSize.width}x${videoSize.height}")
                        logger.info("Preview size: ${previewSize?.width}x${previewSize?.height}")
                        logger.info("RAW size: ${rawSize?.width}x${rawSize?.height}")

                        true
                    } finally {
                        cameraLock.release()
                    }
                } catch (e: Exception) {
                    logger.error("Failed to initialize CameraRecorder", e)
                    cleanup()
                    false
                }
            }

        /**
         * Start a capture session based on flags to record 4K video, capture RAW images, or both.
         * Configures outputs (MediaRecorder, ImageReader) accordingly and begins camera preview.
         *
         * @param recordVideo Enable 4K video recording
         * @param captureRaw Enable RAW image capture
         * @return SessionInfo object with session details, or null if failed
         */
        suspend fun startSession(
            recordVideo: Boolean,
            captureRaw: Boolean,
        ): SessionInfo? =
            withContext(cameraDispatcher) {
                try {
                    if (!cameraLock.tryAcquire(CAMERA_LOCK_TIMEOUT_MS, TimeUnit.MILLISECONDS)) {
                        logger.error("Camera lock timeout during session start")
                        return@withContext null
                    }

                    try {
                        if (!isInitialized) {
                            logger.error("CameraRecorder not initialized")
                            return@withContext null
                        }

                        if (isSessionActive) {
                            logger.warning("Camera session already active")
                            return@withContext currentSessionInfo
                        }

                        // Generate session ID and create SessionInfo
                        val sessionId = "Session_${System.currentTimeMillis()}"
                        val sessionInfo =
                            SessionInfo(
                                sessionId = sessionId,
                                videoEnabled = recordVideo,
                                rawEnabled = captureRaw,
                                startTime = System.currentTimeMillis(),
                                cameraId = cameraId,
                                videoResolution = if (recordVideo) "${videoSize.width}x${videoSize.height}" else null,
                                rawResolution = if (captureRaw) "${rawSize?.width}x${rawSize?.height}" else null,
                            )

                        logger.info("Starting camera session: ${sessionInfo.getSummary()}")

                        // Open camera
                        if (!openCamera()) {
                            sessionInfo.markError("Failed to open camera")
                            logger.error("Failed to open camera")
                            return@withContext null
                        }

                        // Setup outputs based on flags
                        val surfaces = mutableListOf<Surface>()

                        // Always include preview surface
                        previewSurface?.let { surfaces.add(it) }

                        // Setup MediaRecorder if video recording enabled
                        if (recordVideo) {
                            setupMediaRecorder(sessionInfo)
                            mediaRecorder?.surface?.let { surfaces.add(it) }
                        }

                        // Setup Preview ImageReader for streaming (always enabled)
                        setupPreviewImageReader()
                        previewImageReader?.surface?.let { surfaces.add(it) }

                        // Setup RAW ImageReader if RAW capture enabled
                        if (captureRaw) {
                            setupRawImageReader(sessionInfo)
                            rawImageReader?.surface?.let { surfaces.add(it) }
                        }

                        // Create capture session with configured surfaces
                        if (!createCaptureSession(surfaces)) {
                            sessionInfo.markError("Failed to create capture session")
                            logger.error("Failed to create capture session")
                            return@withContext null
                        }

                        // Start video recording if enabled
                        if (recordVideo) {
                            try {
                                mediaRecorder?.start()
                                logger.info("Video recording started")
                            } catch (e: Exception) {
                                sessionInfo.markError("Failed to start video recording: ${e.message}")
                                logger.error("Failed to start video recording", e)
                                return@withContext null
                            }
                        }

                        // Store session info and mark as active
                        currentSessionInfo = sessionInfo
                        isSessionActive = true
                        rawCaptureCount = 0

                        logger.info("Camera session started successfully: ${sessionInfo.getSummary()}")
                        sessionInfo
                    } finally {
                        cameraLock.release()
                    }
                } catch (e: Exception) {
                    logger.error("Failed to start camera session", e)
                    // Cleanup on failure
                    stopSession()
                    null
                }
            }

        /**
         * Stop any ongoing recording, flush pending captures, and release camera resources.
         * Ensures video is finalized and RAW images (if any) are saved.
         *
         * @return SessionInfo of the stopped session, or null if no active session
         */
        suspend fun stopSession(): SessionInfo? =
            withContext(cameraDispatcher) {
                try {
                    if (!cameraLock.tryAcquire(CAMERA_LOCK_TIMEOUT_MS, TimeUnit.MILLISECONDS)) {
                        logger.error("Camera lock timeout during session stop")
                        return@withContext currentSessionInfo
                    }

                    try {
                        if (!isSessionActive) {
                            logger.info("No active camera session to stop")
                            return@withContext null
                        }

                        val sessionInfo = currentSessionInfo
                        logger.info("Stopping camera session: ${sessionInfo?.getSummary()}")

                        // Stop MediaRecorder if video was recording
                        if (sessionInfo?.videoEnabled == true) {
                            try {
                                mediaRecorder?.stop()
                                logger.info("Video recording stopped and finalized")
                            } catch (e: Exception) {
                                sessionInfo?.markError("Error stopping video recording: ${e.message}")
                                logger.warning("Error stopping MediaRecorder", e)
                            }

                            try {
                                mediaRecorder?.reset()
                                mediaRecorder?.release()
                                mediaRecorder = null
                            } catch (e: Exception) {
                                logger.warning("Error releasing MediaRecorder", e)
                            }
                        }

                        // Flush pending RAW captures
                        if (sessionInfo?.rawEnabled == true) {
                            try {
                                // Allow time for any pending RAW captures to complete
                                kotlinx.coroutines.delay(100)
                                logger.info("RAW capture completed. Total images: ${sessionInfo.getRawImageCount()}")
                            } catch (e: Exception) {
                                sessionInfo?.markError("Error finalizing RAW captures: ${e.message}")
                                logger.warning("Error finalizing RAW captures", e)
                            }
                        }

                        // Close capture session
                        try {
                            captureSession?.close()
                            captureSession = null
                            logger.debug("Capture session closed")
                        } catch (e: Exception) {
                            logger.warning("Error closing capture session", e)
                        }

                        // Close camera device
                        try {
                            cameraDevice?.close()
                            cameraDevice = null
                            logger.debug("Camera device closed")
                        } catch (e: Exception) {
                            logger.warning("Error closing camera device", e)
                        }

                        // Close image readers
                        try {
                            rawImageReader?.close()
                            rawImageReader = null
                            logger.debug("RAW ImageReader closed")
                        } catch (e: Exception) {
                            logger.warning("Error closing RAW ImageReader", e)
                        }

                        try {
                            previewImageReader?.close()
                            previewImageReader = null
                            logger.debug("Preview ImageReader closed")
                        } catch (e: Exception) {
                            logger.warning("Error closing Preview ImageReader", e)
                        }

                        // Release preview surface
                        try {
                            previewSurface?.release()
                            previewSurface = null
                            logger.debug("Preview surface released")
                        } catch (e: Exception) {
                            logger.warning("Error releasing preview surface", e)
                        }

                        // Mark session as completed
                        sessionInfo?.markCompleted()

                        // Reset state
                        isSessionActive = false
                        currentSessionInfo = null
                        lastRawCaptureResult = null
                        rawCaptureCount = 0

                        logger.info("Camera session stopped successfully: ${sessionInfo?.getSummary()}")
                        sessionInfo
                    } finally {
                        cameraLock.release()
                    }
                } catch (e: Exception) {
                    logger.error("Error stopping camera session", e)
                    currentSessionInfo?.markError("Error during session stop: ${e.message}")
                    currentSessionInfo
                }
            }

        /**
         * Manually trigger a RAW capture during an active session (only if RAW is enabled).
         * Allows capturing a RAW_SENSOR frame on-demand while video is recording.
         *
         * @return true if RAW capture was triggered successfully, false otherwise
         */
        suspend fun captureRawImage(): Boolean =
            withContext(cameraDispatcher) {
                try {
                    if (!isSessionActive) {
                        logger.error("No active session for RAW capture")
                        return@withContext false
                    }

                    val sessionInfo = currentSessionInfo
                    if (sessionInfo?.rawEnabled != true) {
                        logger.error("RAW capture not enabled for current session")
                        return@withContext false
                    }

                    if (captureSession == null || rawImageReader == null) {
                        logger.error("Capture session or RAW ImageReader not available")
                        return@withContext false
                    }

                    logger.info("Triggering manual RAW capture...")

                    // Create RAW capture request using STILL_CAPTURE template for high quality
                    val rawCaptureRequest =
                        cameraDevice
                            ?.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE)
                            ?.apply {
                                addTarget(rawImageReader!!.surface)

                                // Set capture controls for optimal RAW quality
                                set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
                                set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
                                set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)

                                // Optional: Add preview surface to keep preview synchronized
                                previewSurface?.let { addTarget(it) }
                            }?.build()

                    if (rawCaptureRequest == null) {
                        logger.error("Failed to create RAW capture request")
                        return@withContext false
                    }

                    // Submit RAW capture request with callback to handle metadata
                    val captureCallback =
                        object : CameraCaptureSession.CaptureCallback() {
                            override fun onCaptureCompleted(
                                session: CameraCaptureSession,
                                request: CaptureRequest,
                                result: TotalCaptureResult,
                            ) {
                                // Store capture result for DNG metadata
                                lastRawCaptureResult = result
                                logger.debug("RAW capture metadata received")
                            }

                            override fun onCaptureFailed(
                                session: CameraCaptureSession,
                                request: CaptureRequest,
                                failure: CaptureFailure,
                            ) {
                                logger.error("RAW capture failed: ${failure.reason}")
                                sessionInfo.markError("RAW capture failed: ${failure.reason}")
                            }
                        }

                    captureSession!!.capture(rawCaptureRequest, captureCallback, backgroundHandler)

                    logger.info("RAW capture request submitted successfully")
                    true
                } catch (e: Exception) {
                    logger.error("Failed to capture RAW image", e)
                    currentSessionInfo?.markError("RAW capture error: ${e.message}")
                    false
                }
            }

        /**
         * Capture calibration image for device synchronization and alignment.
         * Creates a high-quality JPEG image suitable for calibration purposes.
         */
        suspend fun captureCalibrationImage(outputPath: String): Boolean =
            withContext(Dispatchers.IO) {
                return@withContext try {
                    logger.info("Starting calibration image capture to: $outputPath")

                    // Verify camera is ready
                    val camera = cameraDevice
                    val session = captureSession
                    if (camera == null || session == null) {
                        logger.error("Camera not ready for calibration capture")
                        return@withContext false
                    }

                    // Create ImageReader for calibration capture (high quality JPEG)
                    val calibrationImageReader =
                        ImageReader.newInstance(
                            videoSize.width,
                            videoSize.height,
                            ImageFormat.JPEG,
                            1,
                        )

                    var captureSuccess = false
                    val captureSemaphore = Semaphore(0)

                    calibrationImageReader.setOnImageAvailableListener({ reader ->
                        try {
                            val image = reader.acquireLatestImage()
                            if (image != null) {
                                val buffer = image.planes[0].buffer
                                val bytes = ByteArray(buffer.remaining())
                                buffer.get(bytes)

                                // Save to file
                                val outputFile = File(outputPath)
                                outputFile.parentFile?.mkdirs()
                                FileOutputStream(outputFile).use { it.write(bytes) }

                                logger.info("Calibration image saved successfully: $outputPath")
                                captureSuccess = true
                                image.close()
                            }
                        } catch (e: Exception) {
                            logger.error("Error saving calibration image", e)
                        } finally {
                            captureSemaphore.release()
                        }
                    }, backgroundHandler)

                    // Create capture request for calibration
                    val calibrationRequest =
                        camera.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE).apply {
                            addTarget(calibrationImageReader.surface)

                            // Set high quality capture parameters
                            set(CaptureRequest.JPEG_QUALITY, 95.toByte())
                            set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO)
                            set(CaptureRequest.CONTROL_AF_MODE, CameraMetadata.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
                            set(CaptureRequest.CONTROL_AE_MODE, CameraMetadata.CONTROL_AE_MODE_ON)
                        }

                    // Capture the calibration image
                    session.capture(
                        calibrationRequest.build(),
                        object : CameraCaptureSession.CaptureCallback() {
                            override fun onCaptureCompleted(
                                session: CameraCaptureSession,
                                request: CaptureRequest,
                                result: TotalCaptureResult,
                            ) {
                                logger.debug("Calibration capture completed")
                            }

                            override fun onCaptureFailed(
                                session: CameraCaptureSession,
                                request: CaptureRequest,
                                failure: CaptureFailure,
                            ) {
                                logger.error("Calibration capture failed: ${failure.reason}")
                                captureSemaphore.release()
                            }
                        },
                        backgroundHandler,
                    )

                    // Wait for capture completion (timeout after 5 seconds)
                    val acquired = captureSemaphore.tryAcquire(5, TimeUnit.SECONDS)
                    calibrationImageReader.close()

                    if (!acquired) {
                        logger.error("Calibration capture timeout")
                        return@withContext false
                    }

                    captureSuccess
                } catch (e: Exception) {
                    logger.error("Failed to capture calibration image", e)
                    false
                }
            }

        /**
         * Setup TextureView surface for live preview with proper lifecycle management.
         * Handles SurfaceTextureListener callbacks and configures preview surface.
         */
        private suspend fun setupTextureViewSurface() =
            withContext(Dispatchers.Main) {
                try {
                    val textureView = this@CameraRecorder.textureView
                    if (textureView == null) {
                        logger.error("TextureView not available for surface setup")
                        return@withContext
                    }

                    logger.info("Setting up TextureView surface...")

                    // Check if SurfaceTexture is already available
                    if (textureView.isAvailable) {
                        logger.debug("SurfaceTexture already available")
                        textureView.surfaceTexture?.let { configureSurfaceTexture(it) }
                    } else {
                        logger.debug("Waiting for SurfaceTexture to become available")

                        // Set up SurfaceTextureListener to wait for surface availability
                        textureView.surfaceTextureListener =
                            object : TextureView.SurfaceTextureListener {
                                override fun onSurfaceTextureAvailable(
                                    surface: SurfaceTexture,
                                    width: Int,
                                    height: Int,
                                ) {
                                    logger.debug("SurfaceTexture became available: ${width}x$height")
                                    configureSurfaceTexture(surface)
                                }

                                override fun onSurfaceTextureSizeChanged(
                                    surface: SurfaceTexture,
                                    width: Int,
                                    height: Int,
                                ) {
                                    logger.debug("SurfaceTexture size changed: ${width}x$height")
                                    // Handle orientation changes or view resizing
                                    configureTransform(width, height)
                                }

                                override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
                                    logger.debug("SurfaceTexture destroyed")
                                    previewSurface?.release()
                                    previewSurface = null
                                    return true // Let TextureView release the SurfaceTexture
                                }

                                override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {
                                    // Called for each frame - not needed for my implementation
                                }
                            }
                    }
                } catch (e: Exception) {
                    logger.error("Failed to setup TextureView surface", e)
                }
            }

        /**
         * Configure SurfaceTexture with proper buffer size and create preview Surface.
         */
        private fun configureSurfaceTexture(surfaceTexture: SurfaceTexture) {
            try {
                val previewSize = this.previewSize
                if (previewSize == null) {
                    logger.error("Preview size not configured")
                    return
                }

                // Set buffer size to match preview resolution
                surfaceTexture.setDefaultBufferSize(previewSize.width, previewSize.height)

                // Create Surface for camera preview
                previewSurface = Surface(surfaceTexture)

                logger.info("Preview surface configured: ${previewSize.width}x${previewSize.height}")

                // Configure transform matrix for proper orientation
                textureView?.let { configureTransform(it.width, it.height) }
            } catch (e: Exception) {
                logger.error("Failed to configure SurfaceTexture", e)
            }
        }

        /**
         * Configure transform matrix for TextureView to handle orientation and aspect ratio.
         * Based on Google Camera2 sample implementation.
         */
        private fun configureTransform(
            viewWidth: Int,
            viewHeight: Int,
        ) {
            try {
                val textureView = this.textureView ?: return
                val previewSize = this.previewSize ?: return

                // Get device rotation
                val rotation = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    (context as? android.app.Activity)?.display?.rotation
                        ?: android.view.Surface.ROTATION_0
                } else {
                    @Suppress("DEPRECATION")
                    (context as? android.app.Activity)?.windowManager?.defaultDisplay?.rotation
                        ?: android.view.Surface.ROTATION_0
                }

                val matrix = android.graphics.Matrix()
                val viewRect = android.graphics.RectF(0f, 0f, viewWidth.toFloat(), viewHeight.toFloat())
                val bufferRect = android.graphics.RectF(0f, 0f, previewSize.height.toFloat(), previewSize.width.toFloat())

                val centerX = viewRect.centerX()
                val centerY = viewRect.centerY()

                if (android.view.Surface.ROTATION_90 == rotation || android.view.Surface.ROTATION_270 == rotation) {
                    bufferRect.offset(centerX - bufferRect.centerX(), centerY - bufferRect.centerY())
                    matrix.setRectToRect(viewRect, bufferRect, android.graphics.Matrix.ScaleToFit.FILL)
                    val scale =
                        Math.max(
                            viewHeight.toFloat() / previewSize.height,
                            viewWidth.toFloat() / previewSize.width,
                        )
                    matrix.postScale(scale, scale, centerX, centerY)
                    matrix.postRotate((90 * (rotation - 2)).toFloat(), centerX, centerY)
                } else if (android.view.Surface.ROTATION_180 == rotation) {
                    matrix.postRotate(180f, centerX, centerY)
                }

                textureView.setTransform(matrix)
                logger.debug("Transform matrix configured for rotation: $rotation")
            } catch (e: Exception) {
                logger.error("Failed to configure transform matrix", e)
            }
        }

        /**
         * Select the best camera for recording with Samsung S21/S22 optimization and stage 3 RAW capability.
         * Prioritizes LEVEL_3 hardware with enhanced RAW sensor capabilities for Samsung devices.
         */
        private fun selectBestCamera(cameraManager: CameraManager): String? {
            try {
                logger.info("Selecting best camera with Samsung S21/S22 RAW capability and LEVEL_3 support...")
                
                // Samsung S21/S22 device detection for specialized handling
                val deviceModel = android.os.Build.MODEL.uppercase()
                val isSamsungS21S22 = deviceModel.contains("SM-G99") || deviceModel.contains("SM-G99") ||
                        deviceModel.contains("S21") || deviceModel.contains("S22")
                
                if (isSamsungS21S22) {
                    logger.info("Samsung S21/S22 device detected: $deviceModel - Applying optimizations")
                }

                for (cameraId in cameraManager.cameraIdList) {
                    val characteristics = cameraManager.getCameraCharacteristics(cameraId)

                    // Prefer back camera for main recording
                    val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
                    if (facing != CameraCharacteristics.LENS_FACING_BACK) {
                        continue
                    }

                    // Check hardware level - CRITICAL for Samsung S21/S22 LEVEL_3 capabilities
                    val hardwareLevel = characteristics.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL)
                    val isLevel3 = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3
                    val isFullOrBetter = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL || isLevel3

                    // For Samsung S21/S22, strongly prefer LEVEL_3 for stage 3 RAW extraction
                    if (isSamsungS21S22 && !isLevel3) {
                        logger.debug("Camera $cameraId: Not LEVEL_3 - may not support optimal Samsung RAW features")
                    }

                    if (!isFullOrBetter) {
                        logger.debug("Camera $cameraId: Hardware level insufficient (level: $hardwareLevel)")
                        continue
                    }

                    // Check for RAW capability - ESSENTIAL for stage 3 RAW extraction
                    val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                    val hasRawCapability = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW) == true
                    val hasBackwardCompatibility =
                        capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_BACKWARD_COMPATIBLE) == true
                    
                    // Samsung S21/S22 specific capability validation
                    val hasManualSensor = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_SENSOR) == true
                    val hasManualPostProcessing = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_POST_PROCESSING) == true

                    if (!hasRawCapability) {
                        logger.debug("Camera $cameraId: No RAW capability - REQUIRED for stage 3 extraction")
                        continue
                    }

                    if (!hasBackwardCompatibility) {
                        logger.debug("Camera $cameraId: No backward compatibility")
                        continue
                    }

                    // Samsung S21/S22 enhanced validation for stage 3 RAW
                    if (isSamsungS21S22) {
                        if (!hasManualSensor) {
                            logger.warning("Camera $cameraId: No manual sensor control - stage 3 RAW may be limited")
                        }
                        if (!hasManualPostProcessing) {
                            logger.warning("Camera $cameraId: No manual post-processing - advanced RAW features limited")
                        }
                    }

                    // Verify 4K video support
                    val streamConfigMap = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                    val videoSizes = streamConfigMap?.getOutputSizes(MediaRecorder::class.java)
                    val supports4K = videoSizes?.any { it.width >= 3840 && it.height >= 2160 } == true

                    if (!supports4K) {
                        logger.debug("Camera $cameraId: No 4K video support")
                        continue
                    }

                    // Enhanced RAW sensor validation for Samsung S21/S22 stage 3 extraction
                    val rawSizes = streamConfigMap?.getOutputSizes(ImageFormat.RAW_SENSOR)
                    val hasRawSizes = rawSizes?.isNotEmpty() == true

                    if (!hasRawSizes) {
                        logger.debug("Camera $cameraId: No RAW sensor sizes available - stage 3 extraction not possible")
                        continue
                    }

                    // Samsung S21/S22 specific RAW capabilities validation
                    if (isSamsungS21S22 && rawSizes != null) {
                        val maxRawSize = rawSizes.maxByOrNull { it.width * it.height }
                        val megapixels = maxRawSize?.let { (it.width * it.height) / 1_000_000 } ?: 0
                        
                        logger.info("Samsung device RAW sensor: ${maxRawSize?.width}x${maxRawSize?.height} (${megapixels}MP)")
                        
                        // Samsung S21/S22 typically have 12MP+ main sensors for optimal stage 3 RAW
                        if (megapixels < 12) {
                            logger.warning("Camera $cameraId: RAW sensor below expected Samsung S21/S22 resolution")
                        }
                    }

                    // Validate Samsung specific color filter array for proper RAW processing
                    val colorFilterArrangement = characteristics.get(CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT)
                    if (isSamsungS21S22 && colorFilterArrangement != null) {
                        val cfaName = when (colorFilterArrangement) {
                            CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_RGGB -> "RGGB"
                            CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_GRBG -> "GRBG"
                            CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_GBRG -> "GBRG"
                            CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_BGGR -> "BGGR"
                            else -> "UNKNOWN"
                        }
                        logger.info("Samsung device CFA pattern: $cfaName (required for proper RAW demosaicing)")
                    }

                    // This camera meets all requirements including Samsung S21/S22 stage 3 RAW
                    val levelName =
                        when (hardwareLevel) {
                            CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3 -> "LEVEL_3"
                            CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL -> "FULL"
                            else -> "OTHER($hardwareLevel)"
                        }

                    val samsungOptimized = if (isSamsungS21S22 && isLevel3) " [SAMSUNG_OPTIMIZED]" else ""
                    logger.info("Selected camera: $cameraId (back camera, $levelName, RAW capable, 4K support)$samsungOptimized")
                    logger.info("RAW sizes available: ${rawSizes?.size}")
                    logger.info("Video sizes available: ${videoSizes?.size}")
                    
                    if (isSamsungS21S22) {
                        logger.info("Stage 3 RAW extraction capabilities: Manual sensor=$hasManualSensor, Manual post-processing=$hasManualPostProcessing")
                    }

                    return cameraId
                }

                // If no camera meets all requirements, try with relaxed constraints
                logger.warning("No camera found with all requirements, trying with relaxed constraints...")

                for (cameraId in cameraManager.cameraIdList) {
                    val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                    val facing = characteristics.get(CameraCharacteristics.LENS_FACING)

                    if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                        val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                        val hasBackwardCompatibility =
                            capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_BACKWARD_COMPATIBLE) == true

                        if (hasBackwardCompatibility) {
                            logger.warning("Selected fallback camera: $cameraId (may not support all features)")
                            return cameraId
                        }
                    }
                }

                logger.error("No suitable camera found")
            } catch (e: Exception) {
                logger.error("Error selecting camera", e)
            }

            return null
        }

        /**
         * Configure camera sizes for video, preview, and RAW capture.
         * Ensures optimal sizes for 4K video, efficient preview, and maximum quality RAW.
         */
        private fun configureCameraSizes(characteristics: CameraCharacteristics) {
            val map = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
            if (map == null) {
                logger.error("Stream configuration map not available")
                return
            }

            logger.info("Configuring camera sizes for multi-stream capture...")

            // Configure 4K video size (3840x2160) - primary requirement
            val videoSizes = map.getOutputSizes(MediaRecorder::class.java)
            videoSize = videoSizes?.find { it.width == 3840 && it.height == 2160 }
                ?: videoSizes?.find { it.width >= 3840 && it.height >= 2160 } // Accept higher if available
                ?: videoSizes?.maxByOrNull { it.width * it.height } // Fallback to highest available
                ?: Size(1920, 1080) // Final fallback to 1080p

            logger.info("Video recording size: ${videoSize.width}x${videoSize.height}")

            // Configure preview size - should match video aspect ratio but be smaller for efficiency
            val previewSizes = map.getOutputSizes(SurfaceTexture::class.java)
            val videoAspectRatio = videoSize.width.toFloat() / videoSize.height.toFloat()

            previewSize = previewSizes
                ?.filter { size ->
                    val aspectRatio = size.width.toFloat() / size.height.toFloat()
                    Math.abs(aspectRatio - videoAspectRatio) < 0.1f // Allow small aspect ratio difference
                }?.filter { size ->
                    size.width <= 1920 && size.height <= 1080 // Limit preview size for performance
                }?.maxByOrNull { it.width * it.height } // Choose largest matching size
                ?: previewSizes?.find { it.width == 1920 && it.height == 1080 } // 1080p fallback
                ?: previewSizes?.find { it.width == 1280 && it.height == 720 } // 720p fallback
                ?: Size(1280, 720) // Final fallback

            logger.info("Preview size: ${previewSize?.width}x${previewSize?.height}")

            // Configure RAW size - use maximum sensor resolution for best quality
            val rawSizes = map.getOutputSizes(ImageFormat.RAW_SENSOR)
            rawSize = rawSizes?.maxByOrNull { it.width * it.height } // Maximum available RAW resolution

            if (rawSize != null) {
                logger.info(
                    "RAW capture size: ${rawSize!!.width}x${rawSize!!.height} (${rawSize!!.width * rawSize!!.height / 1_000_000}MP)",
                )
            } else {
                logger.warning("No RAW sizes available - RAW capture will be disabled")
            }

            // Verify stream combination compatibility
            verifyStreamCombination(map)

            logger.info("Camera sizes configured successfully")
            logger.info("  Video: ${videoSize.width}x${videoSize.height}")
            logger.info("  Preview: ${previewSize?.width}x${previewSize?.height}")
            logger.info("  RAW: ${rawSize?.width ?: 0}x${rawSize?.height ?: 0}")
        }

        /**
         * Verify that the configured stream combination is supported by the camera.
         * Based on Camera2 API stream combination guarantees.
         */
        private fun verifyStreamCombination(map: StreamConfigurationMap) {
            try {
                // Check if simultaneous video + preview + RAW is supported
                val videoSizes = map.getOutputSizes(MediaRecorder::class.java)
                val previewSizes = map.getOutputSizes(SurfaceTexture::class.java)
                val rawSizes = map.getOutputSizes(ImageFormat.RAW_SENSOR)

                val hasVideoSize = videoSizes?.contains(videoSize) == true
                val hasPreviewSize = previewSizes?.contains(previewSize) == true
                val hasRawSize = rawSizes?.contains(rawSize) == true

                logger.debug("Stream combination verification:")
                logger.debug("  Video size supported: $hasVideoSize")
                logger.debug("  Preview size supported: $hasPreviewSize")
                logger.debug("  RAW size supported: $hasRawSize")

                if (!hasVideoSize) {
                    logger.warning("Selected video size may not be supported")
                }
                if (!hasPreviewSize) {
                    logger.warning("Selected preview size may not be supported")
                }
                if (rawSize != null && !hasRawSize) {
                    logger.warning("Selected RAW size may not be supported")
                }

                // For LEVEL_3 devices, simultaneous RAW + video + preview should be guaranteed
                // For FULL devices, it may work but not guaranteed
                logger.info("Stream combination should be supported on LEVEL_3 hardware")
            } catch (e: Exception) {
                logger.warning("Could not verify stream combination", e)
            }
        }

        /**
         * Open the camera device
         */
        private suspend fun openCamera(): Boolean =
            suspendCancellableCoroutine { continuation ->
                try {
                    val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager

                    val stateCallback =
                        object : CameraDevice.StateCallback() {
                            override fun onOpened(camera: CameraDevice) {
                                cameraDevice = camera
                                logger.info("Camera opened successfully")
                                continuation.resume(true)
                            }

                            override fun onDisconnected(camera: CameraDevice) {
                                camera.close()
                                cameraDevice = null
                                logger.warning("Camera disconnected")
                                if (continuation.isActive) {
                                    continuation.resume(false)
                                }
                            }

                            override fun onError(
                                camera: CameraDevice,
                                error: Int,
                            ) {
                                camera.close()
                                cameraDevice = null
                                logger.error("Camera error: $error")
                                if (continuation.isActive) {
                                    continuation.resumeWithException(Exception("Camera error: $error"))
                                }
                            }
                        }

                    cameraManager.openCamera(cameraId!!, stateCallback, backgroundHandler)
                } catch (e: Exception) {
                    logger.error("Failed to open camera", e)
                    continuation.resumeWithException(e)
                }
            }

        /**
         * Setup MediaRecorder for 4K video recording with H.264 encoding (no audio).
         * Generates file path based on SessionInfo and configures orientation.
         */
        private fun setupMediaRecorder(sessionInfo: SessionInfo) {
            try {
                // Generate video file path
                val videoFile = generateVideoFilePath(sessionInfo.sessionId)
                sessionInfo.videoFilePath = videoFile.absolutePath

                logger.info("Setting up MediaRecorder for 4K video recording...")
                logger.info("Output file: ${videoFile.absolutePath}")

                mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    MediaRecorder(context)
                } else {
                    @Suppress("DEPRECATION")
                    MediaRecorder()
                }.apply {
                        // Video source from camera surface
                        setVideoSource(MediaRecorder.VideoSource.SURFACE)

                        // No audio source - video only as specified

                        // Output format and file
                        setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                        setOutputFile(videoFile.absolutePath)

                        // Video encoder settings
                        setVideoEncoder(MediaRecorder.VideoEncoder.H264)
                        setVideoSize(videoSize.width, videoSize.height)
                        setVideoFrameRate(VIDEO_FRAME_RATE)
                        setVideoEncodingBitRate(VIDEO_BIT_RATE)

                        // Orientation hint for proper playback
                        val orientationHint = getOrientationHint()
                        setOrientationHint(orientationHint)
                        logger.debug("Orientation hint set to: $orientationHint degrees")

                        // Prepare MediaRecorder - this makes getSurface() available
                        prepare()
                    }

                logger.info("MediaRecorder configured successfully:")
                logger.info("  Resolution: ${videoSize.width}x${videoSize.height}")
                logger.info("  Frame rate: ${VIDEO_FRAME_RATE}fps")
                logger.info("  Bitrate: ${VIDEO_BIT_RATE / 1_000_000}Mbps")
                logger.info("  Codec: H.264")
                logger.info("  Audio: None")
            } catch (e: Exception) {
                logger.error("Failed to setup MediaRecorder", e)
                sessionInfo.markError("MediaRecorder setup failed: ${e.message}")
                throw e
            }
        }

        /**
         * Generate video file path based on session ID.
         * Uses app-specific storage to avoid permission requirements.
         */
        private fun generateVideoFilePath(sessionId: String): File {
            val moviesDir =
                context.getExternalFilesDir(Environment.DIRECTORY_MOVIES)
                    ?: context.filesDir // Fallback to internal storage

            // Ensure directory exists
            if (!moviesDir.exists()) {
                moviesDir.mkdirs()
            }

            return File(moviesDir, "$sessionId.mp4")
        }

        /**
         * Get orientation hint for video recording based on device rotation.
         * Ensures recorded video has correct orientation metadata.
         */
        private fun getOrientationHint(): Int =
            try {
                val activity = context as? android.app.Activity
                val rotation = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    activity?.display?.rotation ?: android.view.Surface.ROTATION_0
                } else {
                    @Suppress("DEPRECATION")
                    activity?.windowManager?.defaultDisplay?.rotation ?: android.view.Surface.ROTATION_0
                }

                ORIENTATIONS[rotation] ?: 90 // Default to 90 degrees for portrait
            } catch (e: Exception) {
                logger.warning("Could not determine device rotation, using default orientation", e)
                90 // Default orientation hint
            }

        /**
         * Setup Preview ImageReader for live streaming to PC.
         * Uses JPEG format with lower resolution for network efficiency.
         */
        private fun setupPreviewImageReader() {
            try {
                logger.info("Setting up Preview ImageReader for streaming...")

                // Use smaller resolution for streaming (640x480 default from PreviewStreamer)
                val streamWidth = 640
                val streamHeight = 480

                logger.info("Preview streaming resolution: ${streamWidth}x$streamHeight")

                // Create ImageReader for JPEG format with capacity for 2 images
                previewImageReader =
                    ImageReader
                        .newInstance(
                            streamWidth,
                            streamHeight,
                            ImageFormat.JPEG,
                            2,
                        ).apply {
                            setOnImageAvailableListener({ reader ->
                                handlePreviewImageAvailable(reader)
                            }, backgroundHandler)
                        }

                logger.info("Preview ImageReader configured successfully")
            } catch (e: Exception) {
                logger.error("Failed to setup Preview ImageReader", e)
                throw e
            }
        }

        /**
         * Handle Preview image available callback for streaming.
         * Passes RGB frames to PreviewStreamer for network transmission.
         */
        private fun handlePreviewImageAvailable(reader: ImageReader) {
            var image: Image? = null
            try {
                image = reader.acquireLatestImage() // Use latest to avoid backlog
                if (image == null) {
                    logger.debug("No preview image available")
                    return
                }

                // Pass image to PreviewStreamer for processing and transmission (if available)
                previewStreamer?.onRgbFrameAvailable(image)
                
                // Process frame for hand segmentation if enabled
                processFrameForHandSegmentation(image)
                
            } catch (e: Exception) {
                logger.error("Error handling preview image", e)
                image?.close()
            }
            // Note: PreviewStreamer is responsible for closing the image
        }
        
        /**
         * Process camera frame for hand segmentation
         */
        private fun processFrameForHandSegmentation(image: Image) {
            try {
                // Check if hand segmentation is active
                val status = handSegmentationManager.getStatus()
                if (!status.isEnabled || !status.isRealTimeProcessing) {
                    return
                }
                
                // Convert Image to Bitmap for hand segmentation processing
                val bitmap = convertImageToBitmap(image)
                if (bitmap != null) {
                    // Process frame asynchronously to avoid blocking camera pipeline
                    handSegmentationManager.processFrame(bitmap, System.currentTimeMillis())
                }
                
            } catch (e: Exception) {
                logger.warning("Error processing frame for hand segmentation", e)
            }
        }
        
        /**
         * Convert Camera2 Image to Bitmap for hand segmentation processing
         */
        private fun convertImageToBitmap(image: Image): Bitmap? {
            return try {
                when (image.format) {
                    ImageFormat.JPEG -> {
                        // JPEG format - direct conversion
                        val buffer = image.planes[0].buffer
                        val bytes = ByteArray(buffer.remaining())
                        buffer.get(bytes)
                        BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                    }
                    ImageFormat.YUV_420_888 -> {
                        // YUV format - convert to RGB
                        convertYuv420ToBitmap(image)
                    }
                    else -> {
                        logger.warning("Unsupported image format for hand segmentation: ${image.format}")
                        null
                    }
                }
            } catch (e: Exception) {
                logger.warning("Error converting image to bitmap", e)
                null
            }
        }
        
        /**
         * Convert YUV_420_888 Image to RGB Bitmap
         */
        private fun convertYuv420ToBitmap(image: Image): Bitmap? {
            return try {
                val yBuffer = image.planes[0].buffer
                val uBuffer = image.planes[1].buffer
                val vBuffer = image.planes[2].buffer
                
                val ySize = yBuffer.remaining()
                val uSize = uBuffer.remaining()
                val vSize = vBuffer.remaining()
                
                val nv21 = ByteArray(ySize + uSize + vSize)
                
                yBuffer.get(nv21, 0, ySize)
                vBuffer.get(nv21, ySize, vSize)
                uBuffer.get(nv21, ySize + vSize, uSize)
                
                val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
                val out = ByteArrayOutputStream()
                yuvImage.compressToJpeg(Rect(0, 0, image.width, image.height), 80, out)
                val imageBytes = out.toByteArray()
                
                BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
            } catch (e: Exception) {
                logger.warning("Error converting YUV to bitmap", e)
                null
            }
        }

        /**
         * Setup RAW ImageReader with DngCreator for professional RAW processing.
         * Handles RAW_SENSOR format with full metadata embedding.
         */
        private fun setupRawImageReader(sessionInfo: SessionInfo) {
            try {
                val rawSize = this.rawSize
                if (rawSize == null) {
                    logger.error("RAW size not configured")
                    sessionInfo.markError("RAW size not available")
                    return
                }

                logger.info("Setting up RAW ImageReader for DNG processing...")
                logger.info("RAW resolution: ${rawSize.width}x${rawSize.height}")

                // Create ImageReader for RAW_SENSOR format with capacity for 2 images
                rawImageReader =
                    ImageReader
                        .newInstance(
                            rawSize.width,
                            rawSize.height,
                            ImageFormat.RAW_SENSOR,
                            2,
                        ).apply {
                            setOnImageAvailableListener({ reader ->
                                handleRawImageAvailable(reader, sessionInfo)
                            }, backgroundHandler)
                        }

                logger.info("RAW ImageReader configured successfully")
            } catch (e: Exception) {
                logger.error("Failed to setup RAW ImageReader", e)
                sessionInfo.markError("RAW ImageReader setup failed: ${e.message}")
                throw e
            }
        }

        /**
         * Handle RAW image available callback with DNG processing.
         * Uses DngCreator to save professional RAW images with full metadata.
         */
        private fun handleRawImageAvailable(
            reader: ImageReader,
            sessionInfo: SessionInfo,
        ) {
            var image: Image? = null
            try {
                image = reader.acquireNextImage()
                if (image == null) {
                    logger.warning("No RAW image available")
                    return
                }

                // Get capture result metadata for DNG creation
                val captureResult = lastRawCaptureResult
                if (captureResult == null) {
                    logger.warning("No capture result available for RAW image")
                    image.close()
                    return
                }

                val cameraCharacteristics = this.cameraCharacteristics
                if (cameraCharacteristics == null) {
                    logger.error("Camera characteristics not available for DNG creation")
                    image.close()
                    return
                }

                // Process RAW image on IO dispatcher to avoid blocking camera thread
                CoroutineScope(Dispatchers.IO).launch {
                    processRawImageToDng(image, captureResult, cameraCharacteristics, sessionInfo)
                }
            } catch (e: Exception) {
                logger.error("Error handling RAW image", e)
                sessionInfo.markError("RAW image processing error: ${e.message}")
                image?.close()
            }
        }

        /**
         * Process Samsung S21/S22 optimized RAW image to DNG file with enhanced stage 3 metadata.
         * Enhanced for Samsung camera characteristics and proper RAW sensor data extraction.
         * Runs on IO dispatcher for optimal performance.
         */
        private suspend fun processRawImageToDng(
            image: Image,
            captureResult: TotalCaptureResult,
            characteristics: CameraCharacteristics,
            sessionInfo: SessionInfo,
        ) = withContext(Dispatchers.IO) {
            var outputStream: FileOutputStream? = null

            try {
                // Generate DNG file path
                rawCaptureCount++
                val dngFile = generateRawFilePath(sessionInfo.sessionId, rawCaptureCount)

                logger.info("Processing Samsung-optimized RAW image to DNG: ${dngFile.name}")
                
                // Samsung S21/S22 device detection for enhanced processing
                val deviceModel = android.os.Build.MODEL.uppercase()
                val isSamsungS21S22 = deviceModel.contains("SM-G99") || deviceModel.contains("S21") || deviceModel.contains("S22")

                // Log Samsung specific RAW characteristics for stage 3 validation
                if (isSamsungS21S22) {
                    logSamsungRawCharacteristics(image, captureResult, characteristics)
                }

                // Check if DngCreator is available (API 21+) and handle via reflection for compatibility
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    try {
                        // Use reflection to avoid compile-time dependency on DngCreator
                        val dngCreatorClass = Class.forName("android.media.DngCreator")
                        val constructor = dngCreatorClass.getConstructor(
                            CameraCharacteristics::class.java,
                            TotalCaptureResult::class.java
                        )
                        val dngCreator = constructor.newInstance(characteristics, captureResult)

                        // Enhanced Samsung S21/S22 specific DNG metadata configuration
                        configureSamsungDngMetadata(dngCreator, dngCreatorClass, characteristics, captureResult, isSamsungS21S22)

                        // Create output stream and write DNG with enhanced metadata
                        outputStream = FileOutputStream(dngFile)
                        val writeImageMethod = dngCreatorClass.getMethod("writeImage", 
                            java.io.OutputStream::class.java, Image::class.java)
                        writeImageMethod.invoke(dngCreator, outputStream, image)

                        // Close DngCreator
                        val closeMethod = dngCreatorClass.getMethod("close")
                        closeMethod.invoke(dngCreator)

                        // Update session info with successful Samsung-optimized processing
                        sessionInfo.addRawFile(dngFile.absolutePath)
                        logger.info("Samsung-optimized DNG file created successfully: ${dngFile.absolutePath}")
                        logger.debug("Total RAW images in session: ${sessionInfo.getRawImageCount()}")
                        
                        // Log Samsung stage 3 RAW validation
                        if (isSamsungS21S22) {
                            validateSamsungStage3Raw(dngFile, image, captureResult)
                        }
                        
                    } catch (e: ClassNotFoundException) {
                        logger.warning("DngCreator class not found - likely a build environment issue")
                        sessionInfo.markError("DNG processing: DngCreator class not available")
                    } catch (e: ReflectiveOperationException) {
                        logger.warning("DngCreator reflection error: ${e.message}")
                        sessionInfo.markError("DNG processing: Reflection error")
                    }
                } else {
                    logger.warning("DngCreator not available on API level ${Build.VERSION.SDK_INT} (requires API 21+)")
                    sessionInfo.markError("DNG processing requires API 21+")
                }
            } catch (e: Exception) {
                logger.error("Failed to process Samsung RAW image to DNG", e)
                sessionInfo.markError("Samsung DNG processing failed: ${e.message}")
            } finally {
                // Clean up resources
                try {
                    outputStream?.close()
                    // DngCreator is closed in the reflection block above
                    image.close()
                } catch (e: Exception) {
                    logger.warning("Error closing Samsung DNG resources", e)
                }
            }
        }

        /**
         * Configure Samsung S21/S22 specific DNG metadata for optimal stage 3 RAW processing.
         * Enhances DNG metadata with Samsung camera characteristics and capture parameters.
         */
        private fun configureSamsungDngMetadata(
            dngCreator: Any,
            dngCreatorClass: Class<*>,
            characteristics: CameraCharacteristics,
            captureResult: TotalCaptureResult,
            isSamsungDevice: Boolean
        ) {
            try {
                // Set orientation if available
                val sensorOrientation = characteristics.get(CameraCharacteristics.SENSOR_ORIENTATION)
                if (sensorOrientation != null) {
                    val setOrientationMethod = dngCreatorClass.getMethod("setOrientation", Int::class.java)
                    setOrientationMethod.invoke(dngCreator, sensorOrientation)
                    logger.debug("DNG orientation set to: $sensorOrientation degrees")
                }

                // Samsung specific DNG enhancements
                if (isSamsungDevice) {
                    // Set GPS location if available (Samsung cameras often have GPS integration)
                    val gpsLocation = captureResult.get(CaptureResult.JPEG_GPS_LOCATION)
                    if (gpsLocation != null) {
                        try {
                            val setLocationMethod = dngCreatorClass.getMethod("setLocation", android.location.Location::class.java)
                            setLocationMethod.invoke(dngCreator, gpsLocation)
                            logger.debug("Samsung DNG GPS location metadata applied")
                        } catch (e: Exception) {
                            logger.debug("GPS location not available for DNG metadata")
                        }
                    }

                    // Enhanced thumbnail for Samsung DNG files (if supported)
                    try {
                        val thumbnail = captureResult.get(CaptureResult.JPEG_THUMBNAIL_QUALITY)
                        if (thumbnail != null && thumbnail > 0) {
                            logger.debug("Samsung DNG thumbnail quality: $thumbnail")
                        }
                    } catch (e: Exception) {
                        logger.debug("Thumbnail metadata not available")
                    }
                }

                logger.info("Samsung-optimized DNG metadata configuration completed")
            } catch (e: Exception) {
                logger.warning("Error configuring Samsung DNG metadata", e)
            }
        }

        /**
         * Log Samsung S21/S22 specific RAW characteristics for stage 3 validation.
         * Provides detailed logging of Samsung camera sensor properties.
         */
        private fun logSamsungRawCharacteristics(
            image: Image,
            captureResult: TotalCaptureResult,
            characteristics: CameraCharacteristics
        ) {
            try {
                logger.info("=== Samsung S21/S22 Stage 3 RAW Characteristics ===")
                
                // Image properties
                logger.info("RAW Image: ${image.width}x${image.height}, Format: ${image.format}")
                logger.info("Planes: ${image.planes.size}")
                
                // Samsung sensor characteristics
                val activeArraySize = characteristics.get(CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE)
                val pixelArraySize = characteristics.get(CameraCharacteristics.SENSOR_INFO_PIXEL_ARRAY_SIZE)
                val physicalSize = characteristics.get(CameraCharacteristics.SENSOR_INFO_PHYSICAL_SIZE)
                
                logger.info("Active Array: ${activeArraySize?.width()}x${activeArraySize?.height()}")
                logger.info("Pixel Array: ${pixelArraySize?.width}x${pixelArraySize?.height}")
                logger.info("Physical Size: ${physicalSize?.width}mm x ${physicalSize?.height}mm")
                
                // Color Filter Array - critical for Samsung RAW demosaicing
                val colorFilterArrangement = characteristics.get(CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT)
                val cfaPattern = when (colorFilterArrangement) {
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_RGGB -> "RGGB (Samsung Standard)"
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_GRBG -> "GRBG"
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_GBRG -> "GBRG"
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_BGGR -> "BGGR"
                    else -> "Unknown/Mono"
                }
                logger.info("CFA Pattern: $cfaPattern")
                
                // Capture parameters for stage 3 validation
                val sensitivity = captureResult.get(CaptureResult.SENSOR_SENSITIVITY)
                val exposureTime = captureResult.get(CaptureResult.SENSOR_EXPOSURE_TIME)
                val frameDuration = captureResult.get(CaptureResult.SENSOR_FRAME_DURATION)
                
                logger.info("Capture - ISO: $sensitivity, Exposure: ${exposureTime?.let { it / 1000000 }}ms")
                logger.info("Frame Duration: ${frameDuration?.let { it / 1000000 }}ms")
                
                // Samsung specific noise model (critical for stage 3 RAW)
                val noiseProfile = captureResult.get(CaptureResult.SENSOR_NOISE_PROFILE)
                if (noiseProfile != null) {
                    logger.info("Samsung Noise Profile: ${noiseProfile.size} coefficients available")
                }
                
                logger.info("===============================================")
            } catch (e: Exception) {
                logger.warning("Error logging Samsung RAW characteristics", e)
            }
        }

        /**
         * Validate Samsung S21/S22 stage 3 RAW extraction success.
         * Ensures proper RAW data integrity and Samsung compliance.
         */
        private fun validateSamsungStage3Raw(
            dngFile: File,
            image: Image,
            captureResult: TotalCaptureResult
        ) {
            try {
                logger.info("=== Samsung S21/S22 Stage 3 RAW Validation ===")
                
                // File validation
                val fileSize = dngFile.length()
                val expectedMinSize = (image.width * image.height * 2) // 16-bit RAW minimum
                logger.info("DNG File: ${dngFile.name}, Size: ${fileSize / 1024}KB")
                
                if (fileSize < expectedMinSize) {
                    logger.warning("DNG file size appears small - possible data loss")
                } else {
                    logger.info("DNG file size validation: PASSED")
                }
                
                // RAW data plane validation
                image.planes.forEachIndexed { index, plane ->
                    val pixelStride = plane.pixelStride
                    val rowStride = plane.rowStride
                    val bufferSize = plane.buffer.remaining()
                    
                    logger.info("Plane $index: PixelStride=$pixelStride, RowStride=$rowStride, BufferSize=${bufferSize / 1024}KB")
                }
                
                // Samsung stage 3 specific validation
                val timestamp = image.timestamp
                val captureTimestamp = captureResult.get(CaptureResult.SENSOR_TIMESTAMP)
                
                logger.info("Image Timestamp: $timestamp")
                logger.info("Capture Timestamp: $captureTimestamp")
                
                if (timestamp > 0 && captureTimestamp != null) {
                    logger.info("Samsung stage 3 RAW timestamp validation: PASSED")
                } else {
                    logger.warning("Samsung stage 3 RAW timestamp validation: FAILED")
                }
                
                logger.info("Samsung Stage 3 RAW Extraction: COMPLETED")
                logger.info("============================================")
                
            } catch (e: Exception) {
                logger.warning("Error during Samsung stage 3 RAW validation", e)
            }
        }

        /**
         * Generate RAW file path based on session ID and capture index.
         * Uses app-specific storage for DNG files.
         */
        private fun generateRawFilePath(
            sessionId: String,
            index: Int,
        ): File {
            val picturesDir =
                context.getExternalFilesDir(Environment.DIRECTORY_PICTURES)
                    ?: context.filesDir // Fallback to internal storage

            // Ensure directory exists
            if (!picturesDir.exists()) {
                picturesDir.mkdirs()
            }

            return File(picturesDir, "${sessionId}_RAW_$index.dng")
        }

        /**
         * Create camera capture session with specified surfaces for multi-stream configuration.
         * Supports simultaneous Preview + Video + RAW capture based on enabled features.
         */
        private suspend fun createCaptureSession(surfaces: List<Surface>): Boolean =
            suspendCancellableCoroutine { continuation ->
                try {
                    if (surfaces.isEmpty()) {
                        logger.error("No surfaces provided for capture session")
                        continuation.resume(false)
                        return@suspendCancellableCoroutine
                    }

                    logger.info("Creating capture session with ${surfaces.size} surfaces")

                    val stateCallback =
                        object : CameraCaptureSession.StateCallback() {
                            override fun onConfigured(session: CameraCaptureSession) {
                                captureSession = session
                                logger.info("Capture session configured successfully")

                                // Start repeating request for preview and video
                                startRepeatingRequest(surfaces)

                                continuation.resume(true)
                            }

                            override fun onConfigureFailed(session: CameraCaptureSession) {
                                logger.error("Failed to configure capture session")
                                currentSessionInfo?.markError("Capture session configuration failed")
                                continuation.resume(false)
                            }
                        }

                    // Create session with provided surfaces
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                        val outputConfigurations = surfaces.map { OutputConfiguration(it) }
                        val sessionConfig = SessionConfiguration(
                            SessionConfiguration.SESSION_REGULAR,
                            outputConfigurations,
                            { backgroundHandler!!.post(it) },
                            stateCallback
                        )
                        cameraDevice!!.createCaptureSession(sessionConfig)
                    } else {
                        @Suppress("DEPRECATION")
                        cameraDevice!!.createCaptureSession(surfaces, stateCallback, backgroundHandler)
                    }
                } catch (e: Exception) {
                    logger.error("Failed to create capture session", e)
                    currentSessionInfo?.markError("Capture session creation error: ${e.message}")
                    continuation.resumeWithException(e)
                }
            }

        /**
         * Start repeating capture request for preview and video recording.
         * Uses appropriate template based on session configuration.
         */
        private fun startRepeatingRequest(surfaces: List<Surface>) {
            try {
                val sessionInfo = currentSessionInfo
                if (sessionInfo == null) {
                    logger.error("No active session for repeating request")
                    return
                }

                // Choose template based on session configuration
                val template =
                    if (sessionInfo.videoEnabled) {
                        CameraDevice.TEMPLATE_RECORD // Optimized for video recording with steady frame rate
                    } else {
                        CameraDevice.TEMPLATE_PREVIEW // Optimized for low latency preview
                    }

                logger.debug("Creating repeating request with template: ${if (sessionInfo.videoEnabled) "RECORD" else "PREVIEW"}")

                val requestBuilder =
                    cameraDevice!!.createCaptureRequest(template).apply {
                        // Add surfaces based on what's available and enabled
                        surfaces.forEach { surface ->
                            when {
                                surface == previewSurface -> {
                                    addTarget(surface)
                                    logger.debug("Added preview surface to repeating request")
                                }
                                surface == previewImageReader?.surface -> {
                                    addTarget(surface)
                                    logger.debug("Added preview streaming surface to repeating request")
                                }
                                surface == mediaRecorder?.surface && sessionInfo.videoEnabled -> {
                                    addTarget(surface)
                                    logger.debug("Added video recording surface to repeating request")
                                }
                                // Note: RAW surface is NOT added to repeating request
                                // RAW captures are done on-demand via captureRawImage()
                            }
                        }

                        // Set capture controls for optimal quality
                        set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)

                        if (sessionInfo.videoEnabled) {
                            // Video recording settings - prioritize steady frame rate
                            set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_VIDEO)
                            set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                        } else {
                            // Preview-only settings - prioritize low latency
                            set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
                            set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                        }
                    }

                // Start repeating request
                captureSession!!.setRepeatingRequest(requestBuilder.build(), null, backgroundHandler)

                logger.info("Repeating request started successfully")
            } catch (e: Exception) {
                logger.error("Failed to start repeating request", e)
                currentSessionInfo?.markError("Failed to start repeating request: ${e.message}")
            }
        }

        /**
         * Start background thread for camera operations
         */
        private fun startBackgroundThread() {
            backgroundThread = HandlerThread(THREAD_NAME).also { it.start() }
            backgroundHandler = Handler(backgroundThread!!.looper)
        }

        /**
         * Stop background thread
         */
        private fun stopBackgroundThread() {
            backgroundThread?.quitSafely()
            try {
                backgroundThread?.join()
                backgroundThread = null
                backgroundHandler = null
            } catch (e: InterruptedException) {
                logger.error("Error stopping background thread", e)
            }
        }

        /**
         * Trigger LED flash sync signal
         * Uses camera flashlight for multi-device synchronization
         */
        suspend fun triggerFlashSync(durationMs: Long = 200): Boolean =
            withContext(Dispatchers.IO) {
                return@withContext try {
                    logger.info("[DEBUG_LOG] Triggering LED flash sync signal (${durationMs}ms)")

                    // Check if camera and session are available
                    val camera = cameraDevice
                    val session = captureSession
                    if (camera == null || session == null) {
                        logger.error("Camera not ready for flash sync")
                        return@withContext false
                    }

                    // Check if flash is available
                    val currentCameraId = cameraId
                    if (currentCameraId == null) {
                        logger.error("Camera ID not available for flash sync")
                        return@withContext false
                    }

                    val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                    val characteristics = cameraManager.getCameraCharacteristics(currentCameraId)
                    val flashAvailable = characteristics.get(CameraCharacteristics.FLASH_INFO_AVAILABLE) ?: false
                    if (!flashAvailable) {
                        logger.warning("Flash not available on this device")
                        return@withContext false
                    }

                    // Turn on flash
                    val flashOnSuccess = setFlashMode(true)
                    if (!flashOnSuccess) {
                        logger.error("Failed to turn on flash")
                        return@withContext false
                    }

                    // Keep flash on for specified duration
                    delay(durationMs)

                    // Turn off flash
                    val flashOffSuccess = setFlashMode(false)
                    if (!flashOffSuccess) {
                        logger.warning("Failed to turn off flash - may remain on")
                    }

                    logger.info("[DEBUG_LOG] LED flash sync completed successfully")
                    true
                } catch (e: Exception) {
                    logger.error("Failed to trigger flash sync", e)
                    // Ensure flash is turned off in case of error
                    try {
                        setFlashMode(false)
                    } catch (cleanupException: Exception) {
                        logger.debug("Error during flash cleanup", cleanupException)
                    }
                    false
                }
            }

        /**
         * Set camera flash mode on/off
         */
        private suspend fun setFlashMode(flashOn: Boolean): Boolean =
            withContext(Dispatchers.IO) {
                return@withContext try {
                    val camera = cameraDevice
                    val session = captureSession
                    if (camera == null || session == null) {
                        return@withContext false
                    }

                    // Create capture request with flash mode
                    val requestBuilder =
                        camera.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW).apply {
                            // Add preview surface if available
                            previewSurface?.let { addTarget(it) }

                            // Set flash mode
                            if (flashOn) {
                                set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                                set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_TORCH)
                            } else {
                                set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                                set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_OFF)
                            }
                        }

                    // Apply flash setting
                    session.setRepeatingRequest(requestBuilder.build(), null, backgroundHandler)

                    logger.debug("Flash mode set to: ${if (flashOn) "ON" else "OFF"}")
                    true
                } catch (e: Exception) {
                    logger.error("Failed to set flash mode", e)
                    false
                }
            }

        /**
         * Check if camera flash is available
         */
        fun isFlashAvailable(): Boolean {
            return try {
                val currentCameraId = cameraId
                if (currentCameraId == null) {
                    return false
                }

                val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                val characteristics = cameraManager.getCameraCharacteristics(currentCameraId)
                characteristics.get(CameraCharacteristics.FLASH_INFO_AVAILABLE) ?: false
            } catch (e: Exception) {
                logger.debug("Error checking flash availability", e)
                false
            }
        }

        /**
         * Check if RAW stage 3 capture is available on this device.
         * Validates Samsung S21/S22 optimized RAW sensor capabilities including:
         * - LEVEL_3 or FULL camera hardware support
         * - RAW_SENSOR capability and format support  
         * - Samsung-specific manual sensor controls (for optimal stage 3 extraction)
         * - Adequate sensor resolution for professional RAW processing
         * 
         * @return true if RAW stage 3 capture is fully supported, false otherwise
         */
        fun isRawStage3Available(): Boolean {
            return try {
                val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                
                logger.info("Checking RAW stage 3 capture availability...")
                
                // Samsung S21/S22 device detection for enhanced validation
                val deviceModel = android.os.Build.MODEL.uppercase()
                val isSamsungS21S22 = deviceModel.contains("SM-G99") || deviceModel.contains("S21") || deviceModel.contains("S22")
                
                if (isSamsungS21S22) {
                    logger.info("Samsung S21/S22 device detected: $deviceModel - Enhanced RAW validation")
                }

                for (cameraId in cameraManager.cameraIdList) {
                    val characteristics = cameraManager.getCameraCharacteristics(cameraId)

                    // Check if this is a back camera (primary camera for RAW capture)
                    val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
                    if (facing != CameraCharacteristics.LENS_FACING_BACK) {
                        continue
                    }

                    // Check hardware level - CRITICAL for stage 3 RAW extraction
                    val hardwareLevel = characteristics.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL)
                    val isLevel3 = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3
                    val isFullOrBetter = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL || isLevel3

                    if (!isFullOrBetter) {
                        logger.debug("Camera $cameraId: Hardware level insufficient for stage 3 RAW")
                        continue
                    }

                    // Check for RAW capability - ESSENTIAL for stage 3 RAW extraction
                    val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                    val hasRawCapability = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW) == true
                    val hasBackwardCompatibility = 
                        capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_BACKWARD_COMPATIBLE) == true

                    if (!hasRawCapability) {
                        logger.debug("Camera $cameraId: No RAW capability - stage 3 extraction not supported")
                        continue
                    }

                    if (!hasBackwardCompatibility) {
                        logger.debug("Camera $cameraId: No backward compatibility")
                        continue
                    }

                    // Verify RAW sensor sizes are available
                    val streamConfigMap = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                    val rawSizes = streamConfigMap?.getOutputSizes(ImageFormat.RAW_SENSOR)
                    val hasRawSizes = rawSizes?.isNotEmpty() == true

                    if (!hasRawSizes) {
                        logger.debug("Camera $cameraId: No RAW sensor sizes available - stage 3 extraction not possible")
                        continue
                    }

                    // Samsung S21/S22 enhanced validation for optimal stage 3 RAW
                    var samsungOptimal = true
                    if (isSamsungS21S22) {
                        val hasManualSensor = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_SENSOR) == true
                        val hasManualPostProcessing = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_POST_PROCESSING) == true
                        
                        if (!hasManualSensor) {
                            logger.warning("Camera $cameraId: No manual sensor control - stage 3 RAW may be limited on Samsung")
                            samsungOptimal = false
                        }
                        if (!hasManualPostProcessing) {
                            logger.warning("Camera $cameraId: No manual post-processing - advanced RAW features limited on Samsung")
                            samsungOptimal = false
                        }

                        // Check sensor resolution for Samsung devices
                        val maxRawSize = rawSizes?.maxByOrNull { it.width * it.height }
                        val megapixels = maxRawSize?.let { (it.width * it.height) / 1_000_000 } ?: 0
                        
                        if (megapixels < 12) {
                            logger.warning("Camera $cameraId: RAW sensor below expected Samsung S21/S22 resolution (${megapixels}MP)")
                            samsungOptimal = false
                        }
                    }

                    // This camera supports RAW stage 3 capture
                    val levelName = when (hardwareLevel) {
                        CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3 -> "LEVEL_3"
                        CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL -> "FULL"
                        else -> "OTHER($hardwareLevel)"
                    }

                    val samsungStatus = if (isSamsungS21S22) {
                        if (samsungOptimal) " [SAMSUNG_OPTIMAL]" else " [SAMSUNG_BASIC]"
                    } else ""

                    logger.info("RAW stage 3 capture AVAILABLE: Camera $cameraId ($levelName)$samsungStatus")
                    logger.info("RAW sensor sizes: ${rawSizes?.size}, Max resolution: ${rawSizes?.maxByOrNull { it.width * it.height }?.let { "${it.width}x${it.height}" }}")

                    return true
                }

                // No suitable camera found
                logger.warning("RAW stage 3 capture NOT AVAILABLE: No camera with required capabilities found")
                logger.info("Requirements: Back camera + LEVEL_3/FULL hardware + RAW capability + RAW sensor sizes")
                
                false
            } catch (e: Exception) {
                logger.error("Error checking RAW stage 3 availability", e)
                false
            }
        }

        /**
         * Cleanup resources
         */
        private fun cleanup() {
            stopBackgroundThread()
            isInitialized = false
        }
    }
