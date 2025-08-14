package com.multisensor.recording.camera

import android.content.Context
import android.util.Log
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.*
import androidx.camera.video.VideoCapture
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean

/**
 * RGB camera implementation with real video recording
 * Built around CameraX API with full video recording functionality
 */
class RgbCamera(private val context: Context) {
    
    companion object {
        private const val TAG = "RgbCamera"
    }

    // Camera state
    private val isInitialized = AtomicBoolean(false)
    private val isPreviewActive = AtomicBoolean(false)
    private val isRecording = AtomicBoolean(false)

    // Camera components
    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var videoCapture: VideoCapture<Recorder>? = null
    private var currentRecording: Recording? = null
    private var preview: Preview? = null
    private var previewView: PreviewView? = null
    private var lifecycleOwner: LifecycleOwner? = null

    /**
     * Initialize RGB camera
     */
    fun initialize(previewView: PreviewView, lifecycleOwner: LifecycleOwner): Boolean {
        return try {
            Log.i(TAG, "Initializing RGB camera")
            
            this.previewView = previewView
            this.lifecycleOwner = lifecycleOwner
            
            val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
            cameraProviderFuture.addListener({
                try {
                    cameraProvider = cameraProviderFuture.get()
                    setupCamera(lifecycleOwner)
                    isInitialized.set(true)
                    Log.i(TAG, "RGB camera initialized successfully")
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to get camera provider", e)
                }
            }, ContextCompat.getMainExecutor(context))
            
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize RGB camera", e)
            false
        }
    }

    /**
     * Setup camera with preview only
     */
    private fun setupCamera(lifecycleOwner: LifecycleOwner) {
        try {
            val cameraProvider = this.cameraProvider ?: return
            
            // Select back camera
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            // Create preview use case
            preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(previewView?.surfaceProvider)
                }

            try {
                // Unbind any existing use cases
                cameraProvider.unbindAll()

                // Bind use cases to camera
                camera = cameraProvider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    preview
                )

                isPreviewActive.set(true)
                Log.i(TAG, "Camera setup completed")

            } catch (e: Exception) {
                Log.e(TAG, "Failed to bind use cases", e)
            }

        } catch (e: Exception) {
            Log.e(TAG, "Failed to setup camera", e)
        }
    }

    /**
     * Start camera preview (already started in setup)
     */
    fun startPreview(): Boolean {
        return if (isInitialized.get() && isPreviewActive.get()) {
            Log.i(TAG, "RGB camera preview is running")
            true
        } else {
            Log.w(TAG, "RGB camera not properly initialized")
            false
        }
    }

    /**
     * Stop camera preview
     */
    fun stopPreview(): Boolean {
        return try {
            cameraProvider?.unbindAll()
            isPreviewActive.set(false)
            Log.i(TAG, "RGB camera preview stopped")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop preview", e)
            false
        }
    }

    /**
     * Start video recording - real implementation  
     */
    fun startRecording(outputFile: File): Boolean {
        return try {
            if (!isInitialized.get()) {
                Log.e(TAG, "RGB camera not initialized")
                return false
            }
            
            if (isRecording.get()) {
                Log.w(TAG, "RGB recording already in progress")
                return false
            }
            
            Log.i(TAG, "Starting RGB video recording to: ${outputFile.absolutePath}")
            
            // Create FileOutputOptions for the recording
            val outputOptions = FileOutputOptions.Builder(outputFile).build()
            
            // Configure VideoCapture use case
            val recorder = Recorder.Builder()
                .setQualitySelector(QualitySelector.from(Quality.HD))
                .build()
            
            videoCapture = VideoCapture.withOutput(recorder)
            
            // Rebind with video capture
            cameraProvider?.let { provider ->
                try {
                    // Unbind all use cases
                    provider.unbindAll()
                    
                    // Create preview again
                    val preview = Preview.Builder()
                        .setTargetAspectRatio(AspectRatio.RATIO_16_9)
                        .build()
                    
                    previewView?.let { view ->
                        preview.setSurfaceProvider(view.surfaceProvider)
                    }
                    
                    // Bind preview and video capture
                    camera = lifecycleOwner?.let { owner ->
                        provider.bindToLifecycle(
                            owner,
                            CameraSelector.DEFAULT_BACK_CAMERA,
                            preview,
                            videoCapture
                        )
                    }
                    
                    // Start the actual recording
                    currentRecording = recorder
                        .prepareRecording(context, outputOptions)
                        .start(ContextCompat.getMainExecutor(context)) { recordEvent ->
                            when (recordEvent) {
                                is VideoRecordEvent.Start -> {
                                    isRecording.set(true)
                                    Log.i(TAG, "RGB video recording started successfully")
                                }
                                is VideoRecordEvent.Finalize -> {
                                    isRecording.set(false)
                                    if (recordEvent.hasError()) {
                                        Log.e(TAG, "RGB video recording error: ${recordEvent.error}")
                                    } else {
                                        Log.i(TAG, "RGB video recording completed: ${outputFile.absolutePath}")
                                    }
                                }
                                is VideoRecordEvent.Status -> {
                                    Log.d(TAG, "RGB recording status: ${recordEvent.recordingStats.recordedDurationNanos}")
                                }
                            }
                        }
                    
                    Log.i(TAG, "RGB recording started")
                    true
                    
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to bind camera with video capture", e)
                    false
                }
            } ?: run {
                Log.e(TAG, "Camera provider not available")
                false
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start RGB recording", e)
            false
        }
    }

    /**
     * Stop video recording - real implementation
     */
    fun stopRecording(): Boolean {
        return try {
            currentRecording?.stop()
            currentRecording = null
            
            isRecording.set(false)
            Log.i(TAG, "RGB recording stopped")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop RGB recording", e)
            false
        }
    }

    /**
     * Check if camera is connected and ready
     */
    fun isConnected(): Boolean {
        return isInitialized.get() && camera != null
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
     * Get camera info
     */
    fun getCameraInfo(): String {
        return camera?.cameraInfo?.let { "RGB Camera Ready" } ?: "No Camera"
    }

    /**
     * Release camera resources
     */
    fun release() {
        try {
            stopRecording()
            stopPreview()
            
            cameraProvider?.unbindAll()
            cameraProvider = null
            camera = null
            preview = null
            
            isInitialized.set(false)
            isPreviewActive.set(false)
            isRecording.set(false)
            
            Log.i(TAG, "RGB camera resources released")
        } catch (e: Exception) {
            Log.e(TAG, "Error releasing camera resources", e)
        }
    }
}