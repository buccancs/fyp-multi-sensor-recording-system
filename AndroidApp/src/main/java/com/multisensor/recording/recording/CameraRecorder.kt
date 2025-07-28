package com.multisensor.recording.recording

import android.content.Context
import android.graphics.ImageFormat
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureRequest
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.SessionConfiguration
import android.media.ImageReader
import android.media.MediaRecorder
import android.os.Handler
import android.os.HandlerThread
import android.util.Size
import android.view.Surface
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import java.io.File
import java.util.concurrent.Executor
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * Handles 4K RGB camera recording with RAW image capture support using Camera2 API.
 * Supports simultaneous video recording and periodic RAW frame capture.
 */
@Singleton
class CameraRecorder @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sessionManager: SessionManager,
    private val logger: Logger
) {
    
    private var cameraDevice: CameraDevice? = null
    private var captureSession: CameraCaptureSession? = null
    private var mediaRecorder: MediaRecorder? = null
    private var imageReader: ImageReader? = null
    private var rawImageReader: ImageReader? = null
    
    private var backgroundThread: HandlerThread? = null
    private var backgroundHandler: Handler? = null
    
    private var isRecording = false
    private var isInitialized = false
    private var currentSessionId: String? = null
    
    // Camera configuration
    private var cameraId: String? = null
    private var videoSize: Size? = null
    private var previewSize: Size? = null
    
    companion object {
        private const val THREAD_NAME = "CameraRecorder"
        private const val VIDEO_FRAME_RATE = 30
        private const val VIDEO_BIT_RATE = 10_000_000 // 10 Mbps for 4K
        private const val RAW_CAPTURE_INTERVAL_MS = 5000L // Capture RAW every 5 seconds
    }
    
    /**
     * Initialize the camera recorder
     */
    suspend fun initialize(): Boolean = withContext(Dispatchers.Main) {
        try {
            logger.info("Initializing CameraRecorder...")
            
            if (isInitialized) {
                logger.info("CameraRecorder already initialized")
                return@withContext true
            }
            
            // Start background thread
            startBackgroundThread()
            
            // Setup camera
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            cameraId = selectBestCamera(cameraManager)
            
            if (cameraId == null) {
                logger.error("No suitable camera found")
                return@withContext false
            }
            
            // Get camera characteristics and configure sizes
            val characteristics = cameraManager.getCameraCharacteristics(cameraId!!)
            configureCameraSizes(characteristics)
            
            isInitialized = true
            logger.info("CameraRecorder initialized successfully with camera: $cameraId")
            
            true
            
        } catch (e: Exception) {
            logger.error("Failed to initialize CameraRecorder", e)
            cleanup()
            false
        }
    }
    
    /**
     * Start recording with the specified session ID
     */
    suspend fun startRecording(sessionId: String): Boolean = withContext(Dispatchers.Main) {
        try {
            if (!isInitialized) {
                logger.error("CameraRecorder not initialized")
                return@withContext false
            }
            
            if (isRecording) {
                logger.warning("Camera recording already in progress")
                return@withContext true
            }
            
            logger.info("Starting camera recording for session: $sessionId")
            currentSessionId = sessionId
            
            // Get session file paths
            val filePaths = sessionManager.getSessionFilePaths()
            if (filePaths == null) {
                logger.error("No active session found")
                return@withContext false
            }
            
            // Open camera
            if (!openCamera()) {
                logger.error("Failed to open camera")
                return@withContext false
            }
            
            // Setup MediaRecorder
            setupMediaRecorder(filePaths.rgbVideoFile)
            
            // Setup ImageReaders
            setupImageReaders(filePaths.rawFramesFolder)
            
            // Create capture session
            if (!createCaptureSession()) {
                logger.error("Failed to create capture session")
                return@withContext false
            }
            
            // Start recording
            mediaRecorder?.start()
            isRecording = true
            
            // Start periodic RAW capture
            startPeriodicRawCapture()
            
            logger.info("Camera recording started successfully")
            true
            
        } catch (e: Exception) {
            logger.error("Failed to start camera recording", e)
            stopRecording()
            false
        }
    }
    
    /**
     * Stop recording
     */
    suspend fun stopRecording() = withContext(Dispatchers.Main) {
        try {
            if (!isRecording) {
                logger.info("Camera recording not in progress")
                return@withContext
            }
            
            logger.info("Stopping camera recording...")
            
            // Stop MediaRecorder
            try {
                mediaRecorder?.stop()
                mediaRecorder?.reset()
            } catch (e: Exception) {
                logger.warning("Error stopping MediaRecorder", e)
            }
            
            // Close capture session
            captureSession?.close()
            captureSession = null
            
            // Close camera
            cameraDevice?.close()
            cameraDevice = null
            
            // Close image readers
            imageReader?.close()
            imageReader = null
            rawImageReader?.close()
            rawImageReader = null
            
            isRecording = false
            currentSessionId = null
            
            logger.info("Camera recording stopped successfully")
            
        } catch (e: Exception) {
            logger.error("Error stopping camera recording", e)
        }
    }
    
    /**
     * Select the best camera for recording (prefer back camera with highest resolution)
     */
    private fun selectBestCamera(cameraManager: CameraManager): String? {
        try {
            for (cameraId in cameraManager.cameraIdList) {
                val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                
                // Prefer back camera
                val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
                if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                    
                    // Check if camera supports required features
                    val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                    val hasRequiredCapabilities = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_BACKWARD_COMPATIBLE) == true
                    
                    if (hasRequiredCapabilities) {
                        logger.info("Selected camera: $cameraId (back camera)")
                        return cameraId
                    }
                }
            }
            
            // Fallback to first available camera
            if (cameraManager.cameraIdList.isNotEmpty()) {
                val fallbackId = cameraManager.cameraIdList[0]
                logger.info("Selected fallback camera: $fallbackId")
                return fallbackId
            }
            
        } catch (e: Exception) {
            logger.error("Error selecting camera", e)
        }
        
        return null
    }
    
    /**
     * Configure camera sizes for video and preview
     */
    private fun configureCameraSizes(characteristics: CameraCharacteristics) {
        val map = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
        
        // Find 4K video size (3840x2160) or closest available
        val videoSizes = map?.getOutputSizes(MediaRecorder::class.java)
        videoSize = videoSizes?.find { it.width == 3840 && it.height == 2160 }
            ?: videoSizes?.maxByOrNull { it.width * it.height }
            ?: Size(1920, 1080) // Fallback to 1080p
        
        // Find suitable preview size (smaller than video size)
        val previewSizes = map?.getOutputSizes(SurfaceTexture::class.java)
        previewSize = previewSizes?.find { it.width <= 1920 && it.height <= 1080 }
            ?: previewSizes?.minByOrNull { it.width * it.height }
            ?: Size(1280, 720) // Fallback to 720p
        
        logger.info("Configured sizes - Video: ${videoSize}, Preview: ${previewSize}")
    }
    
    /**
     * Open the camera device
     */
    private suspend fun openCamera(): Boolean = suspendCancellableCoroutine { continuation ->
        try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            
            val stateCallback = object : CameraDevice.StateCallback() {
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
                
                override fun onError(camera: CameraDevice, error: Int) {
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
     * Setup MediaRecorder for video recording
     */
    private fun setupMediaRecorder(outputFile: File) {
        mediaRecorder = MediaRecorder().apply {
            setVideoSource(MediaRecorder.VideoSource.SURFACE)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setOutputFile(outputFile.absolutePath)
            setVideoEncoder(MediaRecorder.VideoEncoder.H264)
            setVideoSize(videoSize!!.width, videoSize!!.height)
            setVideoFrameRate(VIDEO_FRAME_RATE)
            setVideoEncodingBitRate(VIDEO_BIT_RATE)
            prepare()
        }
        
        logger.info("MediaRecorder configured for ${videoSize!!.width}x${videoSize!!.height} at ${VIDEO_FRAME_RATE}fps")
    }
    
    /**
     * Setup ImageReaders for preview and RAW capture
     */
    private fun setupImageReaders(rawFramesFolder: File) {
        // Preview ImageReader (for streaming to PC)
        imageReader = ImageReader.newInstance(
            previewSize!!.width, previewSize!!.height,
            ImageFormat.JPEG, 2
        )
        
        // RAW ImageReader (for periodic RAW capture)
        rawImageReader = ImageReader.newInstance(
            videoSize!!.width, videoSize!!.height,
            ImageFormat.RAW_SENSOR, 2
        ).apply {
            setOnImageAvailableListener({ reader ->
                // TODO: Save RAW image to file
                val image = reader.acquireLatestImage()
                image?.close()
            }, backgroundHandler)
        }
        
        logger.info("ImageReaders configured")
    }
    
    /**
     * Create camera capture session
     */
    private suspend fun createCaptureSession(): Boolean = suspendCancellableCoroutine { continuation ->
        try {
            val surfaces = mutableListOf<Surface>().apply {
                add(mediaRecorder!!.surface)
                add(imageReader!!.surface)
                add(rawImageReader!!.surface)
            }
            
            val stateCallback = object : CameraCaptureSession.StateCallback() {
                override fun onConfigured(session: CameraCaptureSession) {
                    captureSession = session
                    startRepeatingRequest()
                    logger.info("Capture session configured")
                    continuation.resume(true)
                }
                
                override fun onConfigureFailed(session: CameraCaptureSession) {
                    logger.error("Failed to configure capture session")
                    continuation.resume(false)
                }
            }
            
            cameraDevice!!.createCaptureSession(surfaces, stateCallback, backgroundHandler)
            
        } catch (e: Exception) {
            logger.error("Failed to create capture session", e)
            continuation.resumeWithException(e)
        }
    }
    
    /**
     * Start repeating capture request
     */
    private fun startRepeatingRequest() {
        try {
            val requestBuilder = cameraDevice!!.createCaptureRequest(CameraDevice.TEMPLATE_RECORD).apply {
                addTarget(mediaRecorder!!.surface)
                addTarget(imageReader!!.surface)
            }
            
            captureSession!!.setRepeatingRequest(requestBuilder.build(), null, backgroundHandler)
            
        } catch (e: Exception) {
            logger.error("Failed to start repeating request", e)
        }
    }
    
    /**
     * Start periodic RAW capture
     */
    private fun startPeriodicRawCapture() {
        // TODO: Implement periodic RAW capture logic
        // This would capture RAW frames at specified intervals
        logger.info("Periodic RAW capture started (placeholder)")
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
     * Cleanup resources
     */
    private fun cleanup() {
        stopBackgroundThread()
        isInitialized = false
        isRecording = false
        currentSessionId = null
    }
}