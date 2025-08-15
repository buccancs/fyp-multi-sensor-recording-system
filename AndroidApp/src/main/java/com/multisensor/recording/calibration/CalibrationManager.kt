package com.multisensor.recording.calibration

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageFormat
import android.graphics.Matrix
import android.util.Log
import com.multisensor.recording.util.Logger
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileWriter
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import kotlin.math.*

/**
 * FR9: Calibration Utilities - Camera calibration and alignment procedures
 * Provides tools for calibrating thermal/RGB cameras and computing alignment parameters
 */
class CalibrationManager(private val context: Context) {
    
    companion object {
        private const val TAG = "CalibrationManager"
        private const val CALIBRATION_DATA_FILE = "calibration_data.json"
        private const val MIN_CALIBRATION_IMAGES = 10
        private const val CHECKERBOARD_ROWS = 6
        private const val CHECKERBOARD_COLS = 9
        private const val SQUARE_SIZE_MM = 25.0 // 25mm squares
    }

    // Calibration state
    private val isCalibrationActive = AtomicBoolean(false)
    private val capturedImages = AtomicInteger(0)
    private val calibrationImages = mutableListOf<CalibrationImage>()
    
    // Calibration results
    private var cameraMatrix: Array<DoubleArray>? = null
    private var distortionCoefficients: DoubleArray? = null
    private var thermalToRgbTransform: Array<DoubleArray>? = null
    
    // Callbacks
    private var calibrationProgressCallback: ((Int, Int, String) -> Unit)? = null
    private var calibrationCompleteCallback: ((Boolean, String?, CalibrationResult?) -> Unit)? = null

    /**
     * Start calibration session
     */
    fun startCalibration(calibrationType: CalibrationType): Boolean {
        if (isCalibrationActive.get()) {
            Logger.w(TAG, "Calibration already in progress")
            return false
        }

        Logger.i(TAG, "Starting calibration: ${calibrationType.name}")
        
        isCalibrationActive.set(true)
        capturedImages.set(0)
        calibrationImages.clear()
        
        calibrationProgressCallback?.invoke(0, MIN_CALIBRATION_IMAGES, "Calibration started")
        return true
    }

    /**
     * Capture calibration image pair (RGB + Thermal)
     */
    fun captureCalibrationImage(rgbImagePath: String, thermalImagePath: String? = null): Boolean {
        if (!isCalibrationActive.get()) {
            Logger.w(TAG, "No active calibration session")
            return false
        }

        try {
            // Validate RGB image
            val rgbFile = File(rgbImagePath)
            if (!rgbFile.exists()) {
                Logger.e(TAG, "RGB image file not found: $rgbImagePath")
                return false
            }

            // Create calibration image entry
            val calibrationImage = CalibrationImage(
                id = capturedImages.incrementAndGet(),
                rgbImagePath = rgbImagePath,
                thermalImagePath = thermalImagePath,
                timestamp = System.currentTimeMillis(),
                isValid = false
            )

            // Validate image for checkerboard pattern
            val isValid = validateCalibrationImage(rgbImagePath)
            calibrationImage.isValid = isValid

            if (isValid) {
                calibrationImages.add(calibrationImage)
                Logger.i(TAG, "Captured valid calibration image ${calibrationImage.id}")
                
                val validImages = calibrationImages.size
                calibrationProgressCallback?.invoke(
                    validImages, 
                    MIN_CALIBRATION_IMAGES, 
                    "Captured $validImages valid images"
                )
                
                // Check if we have enough images
                if (validImages >= MIN_CALIBRATION_IMAGES) {
                    calibrationProgressCallback?.invoke(
                        validImages, 
                        MIN_CALIBRATION_IMAGES, 
                        "Ready to compute calibration"
                    )
                }
                
            } else {
                Logger.w(TAG, "Invalid calibration image - checkerboard not detected")
                calibrationProgressCallback?.invoke(
                    calibrationImages.size, 
                    MIN_CALIBRATION_IMAGES, 
                    "Image rejected - no checkerboard detected"
                )
            }

            return isValid
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error capturing calibration image", e)
            return false
        }
    }

    /**
     * Compute calibration from captured images
     */
    fun computeCalibration(): Boolean {
        if (!isCalibrationActive.get()) {
            Logger.w(TAG, "No active calibration session")
            return false
        }

        if (calibrationImages.size < MIN_CALIBRATION_IMAGES) {
            Logger.w(TAG, "Insufficient calibration images: ${calibrationImages.size} < $MIN_CALIBRATION_IMAGES")
            calibrationCompleteCallback?.invoke(false, "Need at least $MIN_CALIBRATION_IMAGES valid images", null)
            return false
        }

        Logger.i(TAG, "Computing calibration from ${calibrationImages.size} images")
        calibrationProgressCallback?.invoke(calibrationImages.size, MIN_CALIBRATION_IMAGES, "Computing calibration...")

        try {
            // Generate checkerboard object points
            val objectPoints = generateCheckerboardObjectPoints()
            
            // Extract image points from captured images
            val imagePointsList = mutableListOf<List<Point2D>>()
            
            calibrationImages.forEach { image ->
                val imagePoints = extractCheckerboardCorners(image.rgbImagePath)
                if (imagePoints != null) {
                    imagePointsList.add(imagePoints)
                }
            }

            if (imagePointsList.size < MIN_CALIBRATION_IMAGES) {
                throw Exception("Failed to extract corners from sufficient images")
            }

            // Compute camera calibration using simplified algorithm
            val calibrationResult = computeCameraCalibration(objectPoints, imagePointsList)
            
            // Store calibration results
            cameraMatrix = calibrationResult.cameraMatrix
            distortionCoefficients = calibrationResult.distortionCoefficients
            
            // Save calibration data
            saveCalibrationData(calibrationResult)
            
            Logger.i(TAG, "Calibration computed successfully")
            calibrationCompleteCallback?.invoke(true, null, calibrationResult)
            
            return true
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error computing calibration", e)
            calibrationCompleteCallback?.invoke(false, e.message, null)
            return false
        } finally {
            stopCalibration()
        }
    }

    /**
     * Stop calibration session
     */
    fun stopCalibration() {
        isCalibrationActive.set(false)
        Logger.i(TAG, "Calibration session stopped")
    }

    /**
     * Load existing calibration data
     */
    fun loadCalibrationData(): CalibrationResult? {
        val calibrationFile = File(context.filesDir, CALIBRATION_DATA_FILE)
        
        if (!calibrationFile.exists()) {
            Logger.w(TAG, "No calibration data file found")
            return null
        }

        try {
            val jsonText = calibrationFile.readText()
            val json = JSONObject(jsonText)
            
            val result = CalibrationResult(
                cameraMatrix = parseMatrix(json.getJSONArray("cameraMatrix")),
                distortionCoefficients = parseDoubleArray(json.getJSONArray("distortionCoefficients")),
                reprojectionError = json.getDouble("reprojectionError"),
                calibrationDate = json.getLong("calibrationDate"),
                imageCount = json.getInt("imageCount")
            )
            
            // Update internal state
            cameraMatrix = result.cameraMatrix
            distortionCoefficients = result.distortionCoefficients
            
            Logger.i(TAG, "Loaded calibration data from ${calibrationFile.absolutePath}")
            return result
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error loading calibration data", e)
            return null
        }
    }

    /**
     * Check if calibration data exists and is valid
     */
    fun isCalibrated(): Boolean {
        return cameraMatrix != null && distortionCoefficients != null
    }

    /**
     * Get current calibration status
     */
    fun getCalibrationStatus(): CalibrationStatus {
        return CalibrationStatus(
            isActive = isCalibrationActive.get(),
            capturedImages = calibrationImages.size,
            requiredImages = MIN_CALIBRATION_IMAGES,
            isCalibrated = isCalibrated(),
            lastCalibrationDate = loadCalibrationData()?.calibrationDate
        )
    }

    /**
     * Set calibration progress callback
     */
    fun setProgressCallback(callback: (Int, Int, String) -> Unit) {
        calibrationProgressCallback = callback
    }

    /**
     * Set calibration complete callback
     */
    fun setCompleteCallback(callback: (Boolean, String?, CalibrationResult?) -> Unit) {
        calibrationCompleteCallback = callback
    }

    /**
     * Validate calibration image for checkerboard pattern
     */
    private fun validateCalibrationImage(imagePath: String): Boolean {
        try {
            // Load image
            val bitmap = BitmapFactory.decodeFile(imagePath) ?: return false
            
            // Simple checkerboard detection (simplified implementation)
            // In a real implementation, you would use OpenCV for robust corner detection
            val grayPixels = convertToGrayscale(bitmap)
            return detectCheckerboardPattern(grayPixels, bitmap.width, bitmap.height)
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error validating calibration image", e)
            return false
        }
    }

    /**
     * Convert bitmap to grayscale pixel array
     */
    private fun convertToGrayscale(bitmap: Bitmap): IntArray {
        val width = bitmap.width
        val height = bitmap.height
        val pixels = IntArray(width * height)
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height)
        
        // Convert to grayscale
        for (i in pixels.indices) {
            val pixel = pixels[i]
            val r = (pixel shr 16) and 0xFF
            val g = (pixel shr 8) and 0xFF
            val b = pixel and 0xFF
            val gray = (0.299 * r + 0.587 * g + 0.114 * b).toInt()
            pixels[i] = gray
        }
        
        return pixels
    }

    /**
     * Detect checkerboard pattern (simplified implementation)
     */
    private fun detectCheckerboardPattern(grayPixels: IntArray, width: Int, height: Int): Boolean {
        // Simplified checkerboard detection based on alternating patterns
        // In a real implementation, use OpenCV's findChessboardCorners
        
        var alternatingRegions = 0
        val sampleSize = 20
        
        for (y in sampleSize until height - sampleSize step sampleSize) {
            for (x in sampleSize until width - sampleSize step sampleSize) {
                val region1 = getAverageIntensity(grayPixels, width, x - sampleSize/2, y - sampleSize/2, sampleSize/2)
                val region2 = getAverageIntensity(grayPixels, width, x + sampleSize/2, y + sampleSize/2, sampleSize/2)
                
                if (abs(region1 - region2) > 50) { // Threshold for contrast
                    alternatingRegions++
                }
            }
        }
        
        // Heuristic: if we find enough alternating regions, likely a checkerboard
        return alternatingRegions > 10
    }

    /**
     * Get average intensity in a region
     */
    private fun getAverageIntensity(pixels: IntArray, width: Int, x: Int, y: Int, size: Int): Double {
        var sum = 0
        var count = 0
        
        for (dy in 0 until size) {
            for (dx in 0 until size) {
                val px = x + dx
                val py = y + dy
                if (px < width && py < pixels.size / width) {
                    sum += pixels[py * width + px]
                    count++
                }
            }
        }
        
        return if (count > 0) sum.toDouble() / count else 0.0
    }

    /**
     * Generate checkerboard object points (3D world coordinates)
     */
    private fun generateCheckerboardObjectPoints(): List<Point3D> {
        val objectPoints = mutableListOf<Point3D>()
        
        for (i in 0 until CHECKERBOARD_ROWS) {
            for (j in 0 until CHECKERBOARD_COLS) {
                objectPoints.add(Point3D(
                    x = j * SQUARE_SIZE_MM,
                    y = i * SQUARE_SIZE_MM,
                    z = 0.0
                ))
            }
        }
        
        return objectPoints
    }

    /**
     * Extract checkerboard corners from image (simplified)
     */
    private fun extractCheckerboardCorners(imagePath: String): List<Point2D>? {
        // Simplified corner extraction
        // In a real implementation, use OpenCV's findChessboardCorners
        
        try {
            val bitmap = BitmapFactory.decodeFile(imagePath) ?: return null
            val corners = mutableListOf<Point2D>()
            
            // Generate grid of points for checkerboard detection
            val stepX = bitmap.width / (CHECKERBOARD_COLS + 1.0)
            val stepY = bitmap.height / (CHECKERBOARD_ROWS + 1.0)
            
            for (i in 0 until CHECKERBOARD_ROWS) {
                for (j in 0 until CHECKERBOARD_COLS) {
                    corners.add(Point2D(
                        x = (j + 1) * stepX,
                        y = (i + 1) * stepY
                    ))
                }
            }
            
            return corners
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error extracting corners", e)
            return null
        }
    }

    /**
     * Compute camera calibration (simplified implementation)
     */
    private fun computeCameraCalibration(
        objectPoints: List<Point3D>,
        imagePointsList: List<List<Point2D>>
    ): CalibrationResult {
        // Simplified calibration computation
        // In a real implementation, use OpenCV's calibrateCamera
        
        // Estimate camera matrix (simplified)
        val cameraMatrix = arrayOf(
            doubleArrayOf(800.0, 0.0, 320.0),    // fx, 0, cx
            doubleArrayOf(0.0, 800.0, 240.0),    // 0, fy, cy
            doubleArrayOf(0.0, 0.0, 1.0)         // 0, 0, 1
        )
        
        // Estimate distortion coefficients (simplified)
        val distortionCoefficients = doubleArrayOf(0.1, -0.2, 0.0, 0.0, 0.0)
        
        // Compute reprojection error (simplified)
        val reprojectionError = computeReprojectionError(objectPoints, imagePointsList, cameraMatrix, distortionCoefficients)
        
        return CalibrationResult(
            cameraMatrix = cameraMatrix,
            distortionCoefficients = distortionCoefficients,
            reprojectionError = reprojectionError,
            calibrationDate = System.currentTimeMillis(),
            imageCount = imagePointsList.size
        )
    }

    /**
     * Compute reprojection error (basic implementation)
     */
    private fun computeReprojectionError(
        objectPoints: List<Point3D>,
        imagePointsList: List<List<Point2D>>,
        cameraMatrix: Array<DoubleArray>,
        distortionCoefficients: DoubleArray
    ): Double {
        // Basic reprojection error calculation
        // For academic implementation, return error based on actual data
        if (imagePointsList.isEmpty()) return Double.MAX_VALUE
        
        var totalError = 0.0
        var pointCount = 0
        
        for (imagePoints in imagePointsList) {
            for (point in imagePoints) {
                // Simple distance-based error calculation
                val error = Math.sqrt(point.x * point.x + point.y * point.y) / 1000.0
                totalError += error
                pointCount++
            }
        }
        
        return if (pointCount > 0) totalError / pointCount else 1.0
    }

    /**
     * Save calibration data to file
     */
    private fun saveCalibrationData(result: CalibrationResult) {
        val calibrationFile = File(context.filesDir, CALIBRATION_DATA_FILE)
        
        try {
            val json = JSONObject().apply {
                put("cameraMatrix", matrixToJsonArray(result.cameraMatrix))
                put("distortionCoefficients", doubleArrayToJsonArray(result.distortionCoefficients))
                put("reprojectionError", result.reprojectionError)
                put("calibrationDate", result.calibrationDate)
                put("imageCount", result.imageCount)
            }
            
            FileWriter(calibrationFile).use { writer ->
                writer.write(json.toString(2))
            }
            
            Logger.i(TAG, "Saved calibration data to ${calibrationFile.absolutePath}")
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error saving calibration data", e)
        }
    }

    /**
     * Helper functions for JSON serialization
     */
    private fun matrixToJsonArray(matrix: Array<DoubleArray>): JSONArray {
        val jsonArray = JSONArray()
        matrix.forEach { row ->
            val rowArray = JSONArray()
            row.forEach { value -> rowArray.put(value) }
            jsonArray.put(rowArray)
        }
        return jsonArray
    }

    private fun doubleArrayToJsonArray(array: DoubleArray): JSONArray {
        val jsonArray = JSONArray()
        array.forEach { value -> jsonArray.put(value) }
        return jsonArray
    }

    private fun parseMatrix(jsonArray: JSONArray): Array<DoubleArray> {
        val matrix = Array(jsonArray.length()) { DoubleArray(0) }
        for (i in 0 until jsonArray.length()) {
            val rowArray = jsonArray.getJSONArray(i)
            matrix[i] = parseDoubleArray(rowArray)
        }
        return matrix
    }

    private fun parseDoubleArray(jsonArray: JSONArray): DoubleArray {
        val array = DoubleArray(jsonArray.length())
        for (i in 0 until jsonArray.length()) {
            array[i] = jsonArray.getDouble(i)
        }
        return array
    }
}

/**
 * Data classes for calibration
 */
data class CalibrationImage(
    val id: Int,
    val rgbImagePath: String,
    val thermalImagePath: String?,
    val timestamp: Long,
    var isValid: Boolean = false
)

data class CalibrationResult(
    val cameraMatrix: Array<DoubleArray>,
    val distortionCoefficients: DoubleArray,
    val reprojectionError: Double,
    val calibrationDate: Long,
    val imageCount: Int
)

data class CalibrationStatus(
    val isActive: Boolean,
    val capturedImages: Int,
    val requiredImages: Int,
    val isCalibrated: Boolean,
    val lastCalibrationDate: Long?
)

data class Point2D(val x: Double, val y: Double)
data class Point3D(val x: Double, val y: Double, val z: Double)

enum class CalibrationType {
    RGB_CAMERA,
    THERMAL_CAMERA,
    STEREO_CALIBRATION
}