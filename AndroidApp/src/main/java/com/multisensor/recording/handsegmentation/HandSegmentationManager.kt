package com.multisensor.recording.handsegmentation

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import androidx.lifecycle.lifecycleScope
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Hand Segmentation Manager
 * 
 * Manages hand segmentation functionality within the multi-sensor recording system.
 * Integrates with existing camera recording and provides real-time hand detection.
 */
@Singleton
class HandSegmentationManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    companion object {
        private const val TAG = "HandSegmentationManager"
    }
    
    interface HandSegmentationListener {
        fun onHandDetectionStatusChanged(isEnabled: Boolean, handsDetected: Int)
        fun onDatasetProgress(totalSamples: Int, leftHands: Int, rightHands: Int)
        fun onDatasetSaved(datasetPath: String, totalSamples: Int)
        fun onError(error: String)
    }
    
    private val handSegmentationEngine = HandSegmentationEngine(context)
    private var isEnabled = false
    private var listener: HandSegmentationListener? = null
    private var processingJob: Job? = null
    private var currentSessionId: String? = null
    
    // Configuration
    var isRealTimeProcessingEnabled = false
        private set
    var isCroppedDatasetEnabled = false
        private set
    
    /**
     * Initialize hand segmentation for a recording session
     */
    fun initializeForSession(sessionId: String, listener: HandSegmentationListener? = null): Boolean {
        this.currentSessionId = sessionId
        this.listener = listener
        
        return try {
            val outputDir = File(context.getExternalFilesDir(null), "sessions/$sessionId/hand_segmentation")
            
            val success = handSegmentationEngine.initialize(
                outputDir = outputDir,
                callback = object : HandSegmentationEngine.HandSegmentationCallback {
                    override fun onHandDetected(handRegions: List<HandSegmentationEngine.HandRegion>) {
                        listener?.onHandDetectionStatusChanged(isEnabled, handRegions.size)
                        
                        if (isCroppedDatasetEnabled) {
                            val stats = handSegmentationEngine.getDatasetStats()
                            listener?.onDatasetProgress(
                                totalSamples = stats["total_samples"] as Int,
                                leftHands = stats["left_hands"] as Int,
                                rightHands = stats["right_hands"] as Int
                            )
                        }
                    }
                    
                    override fun onSegmentationResult(result: HandSegmentationEngine.SegmentationResult) {
                        // Handle segmentation result if needed
                        logD("Processed frame in ${result.processingTimeMs}ms, found ${result.detectedHands.size} hands")
                    }
                    
                    override fun onError(error: String) {
                        logE("Hand segmentation error: $error")
                        listener?.onError(error)
                    }
                }
            )
            
            if (success) {
                logI("Hand segmentation initialized for session: $sessionId")
            }
            
            success
        } catch (e: Exception) {
            logE("Failed to initialize hand segmentation", e)
            false
        }
    }
    
    /**
     * Enable or disable hand segmentation
     */
    fun setEnabled(enabled: Boolean) {
        if (isEnabled == enabled) return
        
        isEnabled = enabled
        
        if (enabled) {
            logI("Hand segmentation enabled")
        } else {
            logI("Hand segmentation disabled")
            stopProcessing()
        }
        
        listener?.onHandDetectionStatusChanged(isEnabled, 0)
    }
    
    /**
     * Configure real-time processing
     */
    fun setRealTimeProcessing(enabled: Boolean) {
        isRealTimeProcessingEnabled = enabled
        logI("Real-time hand segmentation processing: ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Configure cropped dataset creation
     */
    fun setCroppedDatasetEnabled(enabled: Boolean) {
        isCroppedDatasetEnabled = enabled
        if (!enabled) {
            handSegmentationEngine.clearCroppedDataset()
        }
        logI("Cropped dataset creation: ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Process a camera frame for hand detection
     * This method is called from the camera recorder during recording
     */
    fun processFrame(bitmap: Bitmap, timestamp: Long = System.currentTimeMillis()) {
        if (!isEnabled || !isRealTimeProcessingEnabled) return
        
        // Process frame asynchronously to avoid blocking camera
        processingJob?.cancel()
        processingJob = CoroutineScope(Dispatchers.Default).launch {
            try {
                handSegmentationEngine.processFrame(bitmap, timestamp)
            } catch (e: Exception) {
                logE("Error processing frame", e)
            }
        }
    }
    
    /**
     * Process recorded video files post-recording
     */
    fun processRecordedVideo(videoPath: String, callback: (success: Boolean, outputPath: String?) -> Unit) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                logI("Starting post-processing of recorded video: $videoPath")
                
                // This would integrate with video processing logic
                // For now, I'll create a placeholder that would work with MediaMetadataRetriever
                val outputDir = File(videoPath).parent?.let { "$it/hand_segmentation" } ?: "/tmp/hand_segmentation"
                File(outputDir).mkdirs()
                
                // Implement actual video frame extraction and processing
                val mediaRetriever = android.media.MediaMetadataRetriever()
                try {
                    mediaRetriever.setDataSource(videoPath)
                    
                    // Get video duration and frame rate
                    val durationMs = mediaRetriever.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull() ?: 0L
                    val frameRate = 10 // Extract every 100ms for hand segmentation
                    
                    var frameCount = 0
                    var currentTimeMs = 0L
                    
                    logI("Extracting frames from video for hand segmentation: duration=${durationMs}ms")
                    
                    // Extract frames at regular intervals
                    while (currentTimeMs < durationMs && frameCount < 100) { // Limit to prevent excessive processing
                        try {
                            val bitmap = mediaRetriever.getFrameAtTime(currentTimeMs * 1000, android.media.MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
                            
                            if (bitmap != null) {
                                // Save frame for hand segmentation processing
                                val frameFile = File(outputDir, "frame_${String.format("%04d", frameCount)}.jpg")
                                val out = java.io.FileOutputStream(frameFile)
                                bitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, 90, out)
                                out.close()
                                bitmap.recycle()
                                
                                frameCount++
                                logD("Extracted frame $frameCount at ${currentTimeMs}ms")
                            }
                            
                            currentTimeMs += (1000 / frameRate) // Next frame interval
                            
                        } catch (e: Exception) {
                            logW("Failed to extract frame at ${currentTimeMs}ms: ${e.message}")
                            currentTimeMs += (1000 / frameRate)
                        }
                    }
                    
                    logI("Hand segmentation frame extraction complete: $frameCount frames extracted")
                    
                } finally {
                    try {
                        mediaRetriever.release()
                    } catch (e: Exception) {
                        logW("Error releasing MediaMetadataRetriever: ${e.message}")
                    }
                }
                
                withContext(Dispatchers.Main) {
                    callback(true, outputDir)
                }
                
            } catch (e: Exception) {
                logE("Error processing recorded video", e)
                withContext(Dispatchers.Main) {
                    callback(false, null)
                }
            }
        }
    }
    
    /**
     * Save the current cropped dataset
     */
    fun saveCroppedDataset(callback: (success: Boolean, datasetPath: String?, totalSamples: Int) -> Unit) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val stats = handSegmentationEngine.getDatasetStats()
                val totalSamples = stats["total_samples"] as Int
                
                if (totalSamples == 0) {
                    withContext(Dispatchers.Main) {
                        callback(false, null, 0)
                        listener?.onError("No hand data to save")
                    }
                    return@launch
                }
                
                val datasetDir = handSegmentationEngine.saveCroppedDataset(currentSessionId)
                
                withContext(Dispatchers.Main) {
                    if (datasetDir != null) {
                        logI("Saved cropped dataset: ${datasetDir.absolutePath}")
                        callback(true, datasetDir.absolutePath, totalSamples)
                        listener?.onDatasetSaved(datasetDir.absolutePath, totalSamples)
                    } else {
                        callback(false, null, totalSamples)
                        listener?.onError("Failed to save cropped dataset")
                    }
                }
                
            } catch (e: Exception) {
                logE("Error saving cropped dataset", e)
                withContext(Dispatchers.Main) {
                    callback(false, null, 0)
                    listener?.onError("Error saving dataset: ${e.message}")
                }
            }
        }
    }
    
    /**
     * Get current dataset statistics
     */
    fun getCurrentDatasetStats(): Map<String, Any> {
        return handSegmentationEngine.getDatasetStats()
    }
    
    /**
     * Clear the current cropped dataset
     */
    fun clearCurrentDataset() {
        handSegmentationEngine.clearCroppedDataset()
        logI("Cleared current hand dataset")
        
        val stats = getCurrentDatasetStats()
        listener?.onDatasetProgress(
            totalSamples = stats["total_samples"] as Int,
            leftHands = stats["left_hands"] as Int,
            rightHands = stats["right_hands"] as Int
        )
    }
    
    /**
     * Stop any ongoing processing
     */
    private fun stopProcessing() {
        processingJob?.cancel()
        processingJob = null
    }
    
    /**
     * Cleanup resources when session ends
     */
    fun cleanup() {
        stopProcessing()
        handSegmentationEngine.cleanup()
        currentSessionId = null
        listener = null
        logI("Hand segmentation manager cleaned up")
    }
    
    /**
     * Get integration status for other components
     */
    fun getStatus(): HandSegmentationStatus {
        val stats = getCurrentDatasetStats()
        return HandSegmentationStatus(
            isEnabled = isEnabled,
            isRealTimeProcessing = isRealTimeProcessingEnabled,
            isCroppedDatasetEnabled = isCroppedDatasetEnabled,
            currentSessionId = currentSessionId,
            totalSamples = stats["total_samples"] as Int,
            leftHands = stats["left_hands"] as Int,
            rightHands = stats["right_hands"] as Int,
            averageConfidence = stats["average_confidence"] as Double
        )
    }
    
    data class HandSegmentationStatus(
        val isEnabled: Boolean,
        val isRealTimeProcessing: Boolean,
        val isCroppedDatasetEnabled: Boolean,
        val currentSessionId: String?,
        val totalSamples: Int,
        val leftHands: Int,
        val rightHands: Int,
        val averageConfidence: Double
    )
}