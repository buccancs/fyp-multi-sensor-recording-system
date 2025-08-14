package com.multisensor.recording.camera

import android.content.Context
import android.util.Log
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Streamlined RGB camera implementation using Camera2 API
 * Simplified from the complex ModularCameraRecorder
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
    private var preview: Preview? = null
    private var videoCapture: VideoCapture<Recorder>? = null
    private var recording: Recording? = null
    private var previewView: PreviewView? = null

    /**
     * Initialize RGB camera
     */
    fun initialize(previewView: PreviewView, lifecycleOwner: LifecycleOwner): Boolean {
        return try {
            Log.i(TAG, "Initializing RGB camera")
            
            this.previewView = previewView
            
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
     * Setup camera with preview and recording
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

            // Create video capture use case
            val recorder = Recorder.Builder()
                .setQualitySelector(QualitySelector.from(Quality.HD))
                .build()
            videoCapture = VideoCapture.withOutput(recorder)

            try {
                // Unbind any existing use cases
                cameraProvider.unbindAll()

                // Bind use cases to camera
                camera = cameraProvider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    preview,
                    videoCapture
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
     * Start video recording
     */
    fun startRecording(outputFile: java.io.File): Boolean {
        val videoCapture = this.videoCapture ?: return false

        return try {
            val outputOptions = FileOutputOptions.Builder(outputFile).build()
            
            recording = videoCapture.output
                .prepareRecording(context, outputOptions)
                .start(ContextCompat.getMainExecutor(context)) { recordEvent ->
                    when (recordEvent) {
                        is VideoRecordEvent.Start -> {
                            Log.i(TAG, "Recording started")
                        }
                        is VideoRecordEvent.Finalize -> {
                            if (!recordEvent.hasError()) {
                                Log.i(TAG, "Recording saved to: ${outputFile.absolutePath}")
                            } else {
                                Log.e(TAG, "Recording error: ${recordEvent.error}")
                            }
                        }
                    }
                }
            
            isRecording.set(true)
            Log.i(TAG, "RGB recording started")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start recording", e)
            false
        }
    }

    /**
     * Stop video recording
     */
    fun stopRecording(): Boolean {
        return try {
            recording?.stop()
            recording = null
            isRecording.set(false)
            Log.i(TAG, "RGB recording stopped")
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
        return camera?.cameraInfo?.let { info ->
            "RGB Camera: ${info.cameraSelector}"
        } ?: "No Camera"
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
            videoCapture = null
            recording = null
            
            isInitialized.set(false)
            isPreviewActive.set(false)
            isRecording.set(false)
            
            Log.i(TAG, "RGB camera resources released")
        } catch (e: Exception) {
            Log.e(TAG, "Error releasing camera resources", e)
        }
    }
}