package com.multisensor.recording.streaming

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import android.media.Image
import com.multisensor.recording.network.SocketController
import com.multisensor.recording.util.Logger
import dagger.hilt.android.scopes.ServiceScoped
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import javax.inject.Inject

/**
 * Handles live preview frame streaming to PC and local UI updates.
 * Converts camera frames to JPEG format and sends them via SocketController.
 * 
 * Supports both RGB and thermal camera preview streaming with configurable frame rates.
 */
@ServiceScoped
class PreviewStreamer @Inject constructor(
    private val socketController: SocketController,
    private val logger: Logger
) {
    
    private var streamingScope: CoroutineScope? = null
    private var isStreaming = false
    private var frameCount = 0L
    
    // Streaming configuration
    private var targetFps = 2 // Low FPS to avoid bandwidth issues
    private var jpegQuality = 70 // Compression quality (0-100)
    private var maxFrameWidth = 640 // Max width for preview frames
    private var maxFrameHeight = 480 // Max height for preview frames
    
    // Frame rate control
    private var lastFrameTime = 0L
    private var frameIntervalMs = 1000L / targetFps
    
    companion object {
        private const val PREVIEW_RGB_TAG = "PREVIEW_RGB"
        private const val PREVIEW_THERMAL_TAG = "PREVIEW_THERMAL"
    }
    
    /**
     * Configure streaming parameters
     */
    fun configure(fps: Int = 2, quality: Int = 70, maxWidth: Int = 640, maxHeight: Int = 480) {
        targetFps = fps
        jpegQuality = quality
        maxFrameWidth = maxWidth
        maxFrameHeight = maxHeight
        updateFrameInterval()
        
        logger.info("PreviewStreamer configured: ${fps}fps, quality=$quality, size=${maxWidth}x${maxHeight}")
    }
    
    /**
     * Update frame rate dynamically during streaming (for adaptive frame rate control)
     */
    fun updateFrameRate(newFps: Float) {
        if (newFps <= 0) {
            logger.warning("Invalid frame rate: $newFps, ignoring update")
            return
        }
        
        val previousFps = targetFps
        targetFps = newFps.toInt()
        updateFrameInterval()
        
        logger.info("[DEBUG_LOG] PreviewStreamer frame rate updated from ${previousFps}fps to ${targetFps}fps")
    }
    
    /**
     * Get current frame rate
     */
    fun getCurrentFrameRate(): Float = targetFps.toFloat()
    
    /**
     * Update frame interval based on current target FPS
     */
    private fun updateFrameInterval() {
        frameIntervalMs = if (targetFps > 0) {
            (1000L / targetFps).coerceAtLeast(1L) // Minimum 1ms interval
        } else {
            1000L // Default to 1fps if invalid
        }
    }
    
    /**
     * Start preview streaming
     */
    fun startStreaming() {
        if (isStreaming) {
            logger.warning("PreviewStreamer already streaming")
            return
        }
        
        isStreaming = true
        frameCount = 0
        lastFrameTime = 0
        streamingScope = CoroutineScope(Dispatchers.IO + Job())
        
        logger.info("PreviewStreamer started")
    }
    
    /**
     * Stop preview streaming
     */
    fun stopStreaming() {
        if (!isStreaming) {
            logger.info("PreviewStreamer not currently streaming")
            return
        }
        
        logger.info("Stopping PreviewStreamer...")
        isStreaming = false
        
        try {
            streamingScope?.cancel()
            streamingScope = null
            
            logger.info("PreviewStreamer stopped successfully. Total frames: $frameCount")
            
        } catch (e: Exception) {
            logger.error("Error stopping PreviewStreamer", e)
        }
    }
    
    /**
     * Process RGB camera frame for streaming
     */
    fun onRgbFrameAvailable(image: Image) {
        if (!isStreaming || !shouldProcessFrame()) {
            image.close()
            return
        }
        
        streamingScope?.launch {
            try {
                val jpegBytes = convertImageToJpeg(image)
                if (jpegBytes != null) {
                    sendPreviewFrame(PREVIEW_RGB_TAG, jpegBytes)
                    frameCount++
                }
            } catch (e: Exception) {
                logger.error("Error processing RGB frame", e)
            } finally {
                image.close()
            }
        }
    }
    
    /**
     * Process thermal camera frame for streaming
     */
    fun onThermalFrameAvailable(thermalData: ByteArray, width: Int, height: Int) {
        if (!isStreaming || !shouldProcessFrame()) {
            return
        }
        
        streamingScope?.launch {
            try {
                // Convert thermal data to visual representation
                val jpegBytes = convertThermalToJpeg(thermalData, width, height)
                if (jpegBytes != null) {
                    sendPreviewFrame(PREVIEW_THERMAL_TAG, jpegBytes)
                    frameCount++
                }
            } catch (e: Exception) {
                logger.error("Error processing thermal frame", e)
            }
        }
    }
    
    /**
     * Check if frame should be processed based on target FPS
     */
    private fun shouldProcessFrame(): Boolean {
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastFrameTime >= frameIntervalMs) {
            lastFrameTime = currentTime
            return true
        }
        return false
    }
    
    /**
     * Convert Camera2 Image to JPEG bytes
     */
    private fun convertImageToJpeg(image: Image): ByteArray? {
        return try {
            when (image.format) {
                ImageFormat.JPEG -> {
                    // Image is already JPEG, extract bytes directly
                    val buffer = image.planes[0].buffer
                    val bytes = ByteArray(buffer.remaining())
                    buffer.get(bytes)
                    
                    // Resize if needed
                    resizeJpegIfNeeded(bytes)
                }
                
                ImageFormat.YUV_420_888 -> {
                    // Convert YUV to JPEG
                    convertYuvToJpeg(image)
                }
                
                else -> {
                    logger.warning("Unsupported image format: ${image.format}")
                    null
                }
            }
        } catch (e: Exception) {
            logger.error("Failed to convert image to JPEG", e)
            null
        }
    }
    
    /**
     * Convert YUV_420_888 image to JPEG
     */
    private fun convertYuvToJpeg(image: Image): ByteArray? {
        return try {
            val yBuffer = image.planes[0].buffer
            val uBuffer = image.planes[1].buffer
            val vBuffer = image.planes[2].buffer
            
            val ySize = yBuffer.remaining()
            val uSize = uBuffer.remaining()
            val vSize = vBuffer.remaining()
            
            val nv21 = ByteArray(ySize + uSize + vSize)
            
            // Copy Y plane
            yBuffer.get(nv21, 0, ySize)
            
            // Interleave U and V planes for NV21 format
            val uvPixelStride = image.planes[1].pixelStride
            if (uvPixelStride == 1) {
                uBuffer.get(nv21, ySize, uSize)
                vBuffer.get(nv21, ySize + uSize, vSize)
            } else {
                // Handle pixel stride > 1
                val uvBuffer = ByteArray(uSize + vSize)
                uBuffer.get(uvBuffer, 0, uSize)
                vBuffer.get(uvBuffer, uSize, vSize)
                
                var uvIndex = ySize
                for (i in 0 until uSize step uvPixelStride) {
                    nv21[uvIndex++] = uvBuffer[i + uSize] // V
                    nv21[uvIndex++] = uvBuffer[i] // U
                }
            }
            
            // Convert NV21 to JPEG
            val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
            val outputStream = ByteArrayOutputStream()
            
            yuvImage.compressToJpeg(
                Rect(0, 0, image.width, image.height),
                jpegQuality,
                outputStream
            )
            
            val jpegBytes = outputStream.toByteArray()
            outputStream.close()
            
            // Resize if needed
            resizeJpegIfNeeded(jpegBytes)
            
        } catch (e: Exception) {
            logger.error("Failed to convert YUV to JPEG", e)
            null
        }
    }
    
    /**
     * Resize JPEG if it exceeds maximum dimensions
     */
    private fun resizeJpegIfNeeded(jpegBytes: ByteArray): ByteArray {
        return try {
            val bitmap = BitmapFactory.decodeByteArray(jpegBytes, 0, jpegBytes.size)
            
            if (bitmap.width <= maxFrameWidth && bitmap.height <= maxFrameHeight) {
                // No resizing needed
                return jpegBytes
            }
            
            // Calculate new dimensions maintaining aspect ratio
            val aspectRatio = bitmap.width.toFloat() / bitmap.height.toFloat()
            val (newWidth, newHeight) = if (aspectRatio > 1) {
                // Landscape
                Pair(maxFrameWidth, (maxFrameWidth / aspectRatio).toInt())
            } else {
                // Portrait
                Pair((maxFrameHeight * aspectRatio).toInt(), maxFrameHeight)
            }
            
            val resizedBitmap = Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
            bitmap.recycle()
            
            val outputStream = ByteArrayOutputStream()
            resizedBitmap.compress(Bitmap.CompressFormat.JPEG, jpegQuality, outputStream)
            resizedBitmap.recycle()
            
            val resizedBytes = outputStream.toByteArray()
            outputStream.close()
            
            logger.debug("Resized frame from ${bitmap.width}x${bitmap.height} to ${newWidth}x${newHeight}")
            resizedBytes
            
        } catch (e: Exception) {
            logger.error("Failed to resize JPEG", e)
            jpegBytes // Return original if resize fails
        }
    }
    
    /**
     * Convert thermal data to JPEG with proper thermal colorization
     * Enhanced implementation with iron color palette for better thermal visualization
     */
    private fun convertThermalToJpeg(thermalData: ByteArray, width: Int, height: Int): ByteArray? {
        return try {
            val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            val pixels = IntArray(width * height)
            
            // Find min and max temperature values for normalization
            var minTemp = Int.MAX_VALUE
            var maxTemp = Int.MIN_VALUE
            
            val tempValues = IntArray(width * height)
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
            
            bitmap.setPixels(pixels, 0, width, 0, 0, width, height)
            
            // Convert to JPEG
            val outputStream = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, jpegQuality, outputStream)
            bitmap.recycle()
            
            val jpegBytes = outputStream.toByteArray()
            outputStream.close()
            
            jpegBytes
            
        } catch (e: Exception) {
            logger.error("Failed to convert thermal data to JPEG", e)
            null
        }
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
     * Send preview frame to PC via SocketController
     */
    private fun sendPreviewFrame(tag: String, jpegBytes: ByteArray) {
        try {
            // Create message with tag and base64 encoded image
            val base64Image = android.util.Base64.encodeToString(jpegBytes, android.util.Base64.NO_WRAP)
            val message = "$tag:$base64Image"
            
            socketController.sendMessage(message)
            
            logger.debug("Sent $tag frame (${jpegBytes.size} bytes)")
            
        } catch (e: Exception) {
            logger.error("Failed to send preview frame", e)
        }
    }
    
    /**
     * Get streaming statistics
     */
    fun getStreamingStats(): StreamingStats {
        return StreamingStats(
            isStreaming = isStreaming,
            frameCount = frameCount,
            targetFps = targetFps,
            jpegQuality = jpegQuality,
            maxFrameSize = "${maxFrameWidth}x${maxFrameHeight}"
        )
    }
    
    /**
     * Data class for streaming statistics
     */
    data class StreamingStats(
        val isStreaming: Boolean,
        val frameCount: Long,
        val targetFps: Int,
        val jpegQuality: Int,
        val maxFrameSize: String
    )
}
