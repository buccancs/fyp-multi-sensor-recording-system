package com.multisensor.recording.recording

import android.content.Context
import android.graphics.*
import android.hardware.camera2.*
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.SessionConfiguration
import android.media.ImageReader
import android.media.MediaRecorder
import android.os.Handler
import android.os.HandlerThread
import android.util.Size
import android.view.Surface
import android.view.TextureView
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.File
import java.io.FileOutputStream
import javax.inject.Inject
import com.multisensor.recording.util.SimpleFileUtils
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CameraRecorder
@Inject
constructor(
    @ApplicationContext private val context: Context,
    private val sessionManager: SessionManager,
    private val logger: Logger,
) {
    private var cameraDevice: CameraDevice? = null
    private var captureSession: CameraCaptureSession? = null
    private var textureView: TextureView? = null
    private var previewSurface: Surface? = null
    private var mediaRecorder: MediaRecorder? = null
    
    private var backgroundThread: HandlerThread? = null
    private var backgroundHandler: Handler? = null
    
    private var currentSessionInfo: SessionInfo? = null
    private var cameraId: String? = null
    private var videoSize: Size = Size(1920, 1080)
    private var previewSize: Size = Size(1280, 720)
    
    private var isInitialized = false
    private var isSessionActive = false

    val isConnected: Boolean get() = cameraDevice != null

    suspend fun initialize(textureView: TextureView): Boolean {
        return try {
            logger.info("Initializing camera...")
            
            if (isInitialized) {
                return true
            }
            
            this.textureView = textureView
            startBackgroundThread()
            
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            cameraId = findBackCamera(cameraManager)
            
            if (cameraId == null) {
                logger.error("No back camera found")
                return false
            }
            
            setupTextureView()
            isInitialized = true
            logger.info("Camera initialized successfully")
            true
        } catch (e: Exception) {
            logger.error("Camera initialization failed", e)
            false
        }
    }

    suspend fun startSession(recordVideo: Boolean, captureRaw: Boolean): SessionInfo? {
        return try {
            if (!isInitialized) {
                logger.error("Camera not initialized")
                return null
            }

            if (isSessionActive) {
                return currentSessionInfo
            }

            val sessionId = "Session_${System.currentTimeMillis()}"
            val sessionInfo = SessionInfo(
                sessionId = sessionId,
                videoEnabled = recordVideo,
                rawEnabled = captureRaw,
                startTime = System.currentTimeMillis(),
                cameraId = cameraId,
                videoResolution = if (recordVideo) "${videoSize.width}x${videoSize.height}" else null,
                rawResolution = null
            )

            openCamera()
            setupCapture(sessionInfo)

            currentSessionInfo = sessionInfo
            isSessionActive = true
            
            logger.info("Camera session started")
            sessionInfo
        } catch (e: Exception) {
            logger.error("Failed to start camera session", e)
            null
        }
    }

    suspend fun stopSession(): SessionInfo? {
        return try {
            if (!isSessionActive) {
                return null
            }

            val sessionInfo = currentSessionInfo
            logger.info("Stopping camera session")

            mediaRecorder?.stop()
            mediaRecorder?.release()
            mediaRecorder = null

            captureSession?.close()
            captureSession = null
            
            cameraDevice?.close()
            cameraDevice = null

            isSessionActive = false
            currentSessionInfo = null
            
            logger.info("Camera session stopped")
            sessionInfo
        } catch (e: Exception) {
            logger.error("Error stopping camera session", e)
            currentSessionInfo
        }
    }

    fun cleanup() {
        try {
            stopSession()
            stopBackgroundThread()
            isInitialized = false
        } catch (e: Exception) {
            logger.error("Error during cleanup", e)
        }
    }

    suspend fun captureRawImage(): Boolean {
        logger.info("RAW capture not implemented in simplified version")
        return false
    }

    fun setPreviewStreamer(streamer: Any) {
        // Preview streaming not implemented in simplified version
    }

    private fun findBackCamera(cameraManager: CameraManager): String? {
        try {
            for (cameraId in cameraManager.cameraIdList) {
                val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
                
                if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                    logger.info("Found back camera: $cameraId")
                    return cameraId
                }
            }
        } catch (e: Exception) {
            logger.error("Error finding camera", e)
        }
        return null
    }

    private fun setupTextureView() {
        textureView?.surfaceTextureListener = object : TextureView.SurfaceTextureListener {
            override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
                setupPreviewSurface(surface)
            }
            override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {}
            override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean = true
            override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
        }
        
        textureView?.surfaceTexture?.let { setupPreviewSurface(it) }
    }

    private fun setupPreviewSurface(surfaceTexture: SurfaceTexture) {
        try {
            surfaceTexture.setDefaultBufferSize(previewSize.width, previewSize.height)
            previewSurface = Surface(surfaceTexture)
        } catch (e: Exception) {
            logger.error("Error setting up preview surface", e)
        }
    }

    private fun openCamera() {
        try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            cameraManager.openCamera(cameraId!!, object : CameraDevice.StateCallback() {
                override fun onOpened(camera: CameraDevice) {
                    cameraDevice = camera
                }
                override fun onDisconnected(camera: CameraDevice) {
                    camera.close()
                    cameraDevice = null
                }
                override fun onError(camera: CameraDevice, error: Int) {
                    camera.close()
                    cameraDevice = null
                }
            }, backgroundHandler)
        } catch (e: Exception) {
            logger.error("Failed to open camera", e)
        }
    }

    private fun setupCapture(sessionInfo: SessionInfo) {
        try {
            val surfaces = mutableListOf<Surface>()
            previewSurface?.let { surfaces.add(it) }
            
            if (sessionInfo.videoEnabled) {
                setupMediaRecorder(sessionInfo)
                mediaRecorder?.surface?.let { surfaces.add(it) }
            }
            
            createCaptureSession(surfaces)
        } catch (e: Exception) {
            logger.error("Error setting up capture", e)
        }
    }

    private fun setupMediaRecorder(sessionInfo: SessionInfo) {
        try {
            mediaRecorder = MediaRecorder().apply {
                setVideoSource(MediaRecorder.VideoSource.SURFACE)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setVideoEncoder(MediaRecorder.VideoEncoder.H264)
                setVideoSize(videoSize.width, videoSize.height)
                setVideoFrameRate(30)
                setVideoEncodingBitRate(8000000)
                
                val videoFile = SimpleFileUtils.createVideoFile(context, sessionInfo.sessionId)
                setOutputFile(videoFile.absolutePath)
                sessionInfo.videoFilePath = videoFile.absolutePath
                
                prepare()
            }
        } catch (e: Exception) {
            logger.error("Error setting up media recorder", e)
        }
    }

    private fun createCaptureSession(surfaces: List<Surface>) {
        try {
            val outputConfigurations = surfaces.map { OutputConfiguration(it) }
            val sessionConfiguration = SessionConfiguration(
                SessionConfiguration.SESSION_REGULAR,
                outputConfigurations,
                { it.run() },
                object : CameraCaptureSession.StateCallback() {
                    override fun onConfigured(session: CameraCaptureSession) {
                        captureSession = session
                        startPreview()
                    }
                    override fun onConfigureFailed(session: CameraCaptureSession) {
                        logger.error("Failed to configure capture session")
                    }
                }
            )
            cameraDevice?.createCaptureSession(sessionConfiguration)
        } catch (e: Exception) {
            logger.error("Error creating capture session", e)
        }
    }

    private fun startPreview() {
        try {
            val previewRequest = cameraDevice?.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW)?.apply {
                previewSurface?.let { addTarget(it) }
                set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
            }?.build()

            previewRequest?.let {
                captureSession?.setRepeatingRequest(it, null, backgroundHandler)
            }
        } catch (e: Exception) {
            logger.error("Error starting preview", e)
        }
    }

    private fun startBackgroundThread() {
        backgroundThread = HandlerThread("CameraBackground").also { it.start() }
        backgroundHandler = Handler(backgroundThread!!.looper)
    }

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
}