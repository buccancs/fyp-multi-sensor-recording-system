package com.multisensor.recording.validation

import android.content.Context
import android.util.Log
import com.multisensor.recording.util.Logger
import org.json.JSONObject
import java.io.File
import java.io.FileInputStream
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.abs

/**
 * NFR4: Data Integrity and Validation - Ensures data accuracy and corruption-free recording
 * 
 * Implements:
 * - Sensor data range validation (e.g., GSR 0.0-100.0 uS)
 * - File transfer integrity verification
 * - Session metadata validation
 * - Data completeness checks
 * - SHA-256 checksums for file integrity
 * 
 * Requirements from 3.tex section NFR4:
 * - All recorded data accurate and corruption-free
 * - Data validation mode for sensor inputs with range checking
 * - File transfer verification for completeness
 * - Session metadata as manifest for missing/inconsistent files
 * - No overwriting of existing session data
 */
class DataValidationService(private val context: Context) {
    
    companion object {
        private const val TAG = "DataValidationService"
        
        // GSR validation ranges (from 3.tex: GSR readings 0.0 to 100.0 uS)
        private const val GSR_MIN_VALUE = 0.0
        private const val GSR_MAX_VALUE = 100.0
        private const val GSR_REASONABLE_CHANGE_RATE = 10.0 // uS per second
        
        // Video validation
        private const val MIN_VIDEO_FPS = 15
        private const val MAX_VIDEO_FPS = 60
        private const val MIN_VIDEO_RESOLUTION_WIDTH = 640
        private const val MIN_VIDEO_RESOLUTION_HEIGHT = 480
        
        // File validation
        private const val MIN_FILE_SIZE_BYTES = 100 // Minimum reasonable file size
        private const val MAX_SINGLE_FILE_SIZE_GB = 2.0 // Maximum single file size
        
        // Thermal validation
        private const val THERMAL_MIN_TEMP_CELSIUS = -10.0
        private const val THERMAL_MAX_TEMP_CELSIUS = 60.0
    }

    private val isValidationEnabled = AtomicBoolean(true)
    private val validationErrorCount = AtomicLong(0)
    private val validationWarningCount = AtomicLong(0)
    
    // Validation statistics
    private var lastGsrValue: Double? = null
    private var lastGsrTimestamp: Long = 0L
    private val fileChecksums = mutableMapOf<String, String>()

    /**
     * Enable or disable data validation
     * NFR4: Data validation mode configurable
     */
    fun setValidationEnabled(enabled: Boolean) {
        isValidationEnabled.set(enabled)
        Logger.i(TAG, "Data validation ${if (enabled) "enabled" else "disabled"}")
    }

    /**
     * Validate GSR sensor reading
     * NFR4: Range checking for GSR readings (0.0-100.0 uS)
     */
    fun validateGsrReading(value: Double, timestamp: Long): ValidationResult {
        if (!isValidationEnabled.get()) {
            return ValidationResult.valid()
        }

        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()

        // Range validation
        if (value < GSR_MIN_VALUE || value > GSR_MAX_VALUE) {
            errors.add("GSR value $value uS outside valid range [$GSR_MIN_VALUE, $GSR_MAX_VALUE]")
        }

        // Rate of change validation
        lastGsrValue?.let { lastValue ->
            val timeDiffSeconds = (timestamp - lastGsrTimestamp) / 1000.0
            if (timeDiffSeconds > 0) {
                val changeRate = abs(value - lastValue) / timeDiffSeconds
                if (changeRate > GSR_REASONABLE_CHANGE_RATE) {
                    warnings.add("High GSR change rate: ${String.format("%.2f", changeRate)} uS/s")
                }
            }
        }

        // Physiological plausibility
        if (value > 50.0) {
            warnings.add("Unusually high GSR reading: $value uS (possible sensor saturation)")
        }

        // Update tracking
        lastGsrValue = value
        lastGsrTimestamp = timestamp

        return createValidationResult(errors, warnings, "GSR")
    }

    /**
     * Validate thermal sensor reading
     * NFR4: Thermal data validation
     */
    fun validateThermalReading(temperatureCelsius: Double, timestamp: Long): ValidationResult {
        if (!isValidationEnabled.get()) {
            return ValidationResult.valid()
        }

        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()

        // Temperature range validation
        if (temperatureCelsius < THERMAL_MIN_TEMP_CELSIUS || temperatureCelsius > THERMAL_MAX_TEMP_CELSIUS) {
            errors.add("Thermal reading ${temperatureCelsius}C outside reasonable range [$THERMAL_MIN_TEMP_CELSIUS, $THERMAL_MAX_TEMP_CELSIUS]")
        }

        // Physiological range for human skin temperature
        if (temperatureCelsius < 25.0 || temperatureCelsius > 40.0) {
            warnings.add("Thermal reading ${temperatureCelsius}C outside typical human skin temperature range")
        }

        return createValidationResult(errors, warnings, "Thermal")
    }

    /**
     * Validate video parameters
     * NFR4: Video data validation
     */
    fun validateVideoParameters(width: Int, height: Int, fps: Double): ValidationResult {
        if (!isValidationEnabled.get()) {
            return ValidationResult.valid()
        }

        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()

        // Resolution validation
        if (width < MIN_VIDEO_RESOLUTION_WIDTH || height < MIN_VIDEO_RESOLUTION_HEIGHT) {
            errors.add("Video resolution ${width}x${height} below minimum ${MIN_VIDEO_RESOLUTION_WIDTH}x${MIN_VIDEO_RESOLUTION_HEIGHT}")
        }

        // Frame rate validation
        if (fps < MIN_VIDEO_FPS || fps > MAX_VIDEO_FPS) {
            warnings.add("Video FPS $fps outside recommended range [$MIN_VIDEO_FPS, $MAX_VIDEO_FPS]")
        }

        // Aspect ratio check
        val aspectRatio = width.toDouble() / height
        if (aspectRatio < 1.0 || aspectRatio > 2.5) {
            warnings.add("Unusual aspect ratio: ${String.format("%.2f", aspectRatio)}")
        }

        return createValidationResult(errors, warnings, "Video")
    }

    /**
     * Validate file integrity using SHA-256 checksum
     * NFR4: File transfer verification for completeness
     */
    fun validateFileIntegrity(file: File, expectedChecksum: String? = null): ValidationResult {
        if (!isValidationEnabled.get()) {
            return ValidationResult.valid()
        }

        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()

        try {
            // Check file existence and readability
            if (!file.exists()) {
                errors.add("File does not exist: ${file.name}")
                return createValidationResult(errors, warnings, "File")
            }

            if (!file.canRead()) {
                errors.add("Cannot read file: ${file.name}")
                return createValidationResult(errors, warnings, "File")
            }

            // File size validation
            val fileSizeGB = file.length() / (1024.0 * 1024.0 * 1024.0)
            if (file.length() < MIN_FILE_SIZE_BYTES) {
                warnings.add("File suspiciously small: ${file.length()} bytes")
            }
            if (fileSizeGB > MAX_SINGLE_FILE_SIZE_GB) {
                warnings.add("Large file: ${String.format("%.2f", fileSizeGB)} GB")
            }

            // Calculate SHA-256 checksum
            val calculatedChecksum = calculateSHA256(file)
            fileChecksums[file.name] = calculatedChecksum

            // Compare with expected checksum if provided
            expectedChecksum?.let { expected ->
                if (calculatedChecksum != expected) {
                    errors.add("Checksum mismatch for ${file.name}: expected $expected, got $calculatedChecksum")
                }
            }

            Logger.d(TAG, "File validation complete: ${file.name} (${file.length()} bytes, SHA256: ${calculatedChecksum.take(8)}...)")

        } catch (e: Exception) {
            errors.add("File validation failed: ${e.message}")
            Logger.e(TAG, "File validation error for ${file.name}", e)
        }

        return createValidationResult(errors, warnings, "File")
    }

    /**
     * Calculate SHA-256 hash of file
     */
    private fun calculateSHA256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        FileInputStream(file).use { fis ->
            val buffer = ByteArray(8192)
            var bytesRead: Int
            while (fis.read(buffer).also { bytesRead = it } != -1) {
                digest.update(buffer, 0, bytesRead)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    /**
     * Validate session metadata completeness
     * NFR4: Session metadata as manifest for missing/inconsistent files
     */
    fun validateSessionMetadata(sessionMetadata: JSONObject, sessionDirectory: File): ValidationResult {
        if (!isValidationEnabled.get()) {
            return ValidationResult.valid()
        }

        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()

        try {
            // Check required metadata fields
            val requiredFields = listOf("sessionId", "startTime", "endTime", "duration", "deviceId")
            for (field in requiredFields) {
                if (!sessionMetadata.has(field)) {
                    errors.add("Missing required metadata field: $field")
                }
            }

            // Validate session timing
            if (sessionMetadata.has("startTime") && sessionMetadata.has("endTime")) {
                val startTime = sessionMetadata.getLong("startTime")
                val endTime = sessionMetadata.getLong("endTime")
                
                if (endTime <= startTime) {
                    errors.add("Invalid session timing: end time <= start time")
                }
                
                val actualDuration = endTime - startTime
                if (sessionMetadata.has("duration")) {
                    val reportedDuration = sessionMetadata.getLong("duration")
                    val durationDiff = abs(actualDuration - reportedDuration)
                    if (durationDiff > 1000) { // Allow 1 second tolerance
                        warnings.add("Duration mismatch: reported ${reportedDuration}ms, calculated ${actualDuration}ms")
                    }
                }
            }

            // Validate file manifest
            if (sessionMetadata.has("files")) {
                val filesArray = sessionMetadata.getJSONArray("files")
                val declaredFiles = mutableSetOf<String>()
                
                for (i in 0 until filesArray.length()) {
                    val fileInfo = filesArray.getJSONObject(i)
                    if (fileInfo.has("filename")) {
                        val filename = fileInfo.getString("filename")
                        declaredFiles.add(filename)
                        
                        // Check if declared file exists
                        val file = File(sessionDirectory, filename)
                        if (!file.exists()) {
                            errors.add("Declared file missing: $filename")
                        } else {
                            // Validate file size if specified
                            if (fileInfo.has("size")) {
                                val declaredSize = fileInfo.getLong("size")
                                val actualSize = file.length()
                                if (declaredSize != actualSize) {
                                    warnings.add("File size mismatch for $filename: declared $declaredSize, actual $actualSize")
                                }
                            }
                        }
                    }
                }

                // Check for undeclared files in session directory
                sessionDirectory.listFiles()?.forEach { file ->
                    if (file.isFile && !declaredFiles.contains(file.name) && !file.name.endsWith(".tmp")) {
                        warnings.add("Undeclared file in session directory: ${file.name}")
                    }
                }
            }

        } catch (e: Exception) {
            errors.add("Metadata validation failed: ${e.message}")
            Logger.e(TAG, "Session metadata validation error", e)
        }

        return createValidationResult(errors, warnings, "Session Metadata")
    }

    /**
     * Validate that session directory is unique (no overwriting existing data)
     * NFR4: No overwriting of existing session data
     */
    fun validateSessionUniqueness(sessionDirectory: File): ValidationResult {
        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()

        if (sessionDirectory.exists() && sessionDirectory.list()?.isNotEmpty() == true) {
            errors.add("Session directory already exists and contains data: ${sessionDirectory.name}")
            Logger.w(TAG, "Attempting to use non-empty session directory: ${sessionDirectory.absolutePath}")
        }

        return createValidationResult(errors, warnings, "Session Uniqueness")
    }

    /**
     * Get file checksum for integrity verification
     */
    fun getFileChecksum(filename: String): String? {
        return fileChecksums[filename]
    }

    /**
     * Create validation result and update statistics
     */
    private fun createValidationResult(errors: List<String>, warnings: List<String>, category: String): ValidationResult {
        if (errors.isNotEmpty()) {
            validationErrorCount.incrementAndGet()
            Logger.e(TAG, "Validation errors in $category: ${errors.joinToString("; ")}")
        }
        
        if (warnings.isNotEmpty()) {
            validationWarningCount.incrementAndGet()
            Logger.w(TAG, "Validation warnings in $category: ${warnings.joinToString("; ")}")
        }

        return ValidationResult(
            isValid = errors.isEmpty(),
            errors = errors,
            warnings = warnings,
            category = category
        )
    }

    /**
     * Get validation statistics
     */
    fun getValidationStatistics(): ValidationStatistics {
        return ValidationStatistics(
            isEnabled = isValidationEnabled.get(),
            errorCount = validationErrorCount.get(),
            warningCount = validationWarningCount.get(),
            totalFilesValidated = fileChecksums.size
        )
    }

    /**
     * Reset validation statistics
     */
    fun resetStatistics() {
        validationErrorCount.set(0)
        validationWarningCount.set(0)
        fileChecksums.clear()
        lastGsrValue = null
        lastGsrTimestamp = 0L
        Logger.d(TAG, "Validation statistics reset")
    }

    /**
     * Validation result data class
     */
    data class ValidationResult(
        val isValid: Boolean,
        val errors: List<String> = emptyList(),
        val warnings: List<String> = emptyList(),
        val category: String = ""
    ) {
        companion object {
            fun valid() = ValidationResult(true)
        }
        
        fun hasWarnings() = warnings.isNotEmpty()
        fun hasErrors() = errors.isNotEmpty()
    }

    /**
     * Validation statistics data class
     */
    data class ValidationStatistics(
        val isEnabled: Boolean,
        val errorCount: Long,
        val warningCount: Long,
        val totalFilesValidated: Int
    )
}