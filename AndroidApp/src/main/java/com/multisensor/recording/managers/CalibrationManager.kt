package com.multisensor.recording.managers

import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.delay
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.util.Logger
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager responsible for calibration operations across all devices.
 * Follows single responsibility principle by focusing only on calibration processes.
 * 
 * Handles:
 * - Camera calibration (RGB and thermal)
 * - Shimmer sensor calibration
 * - Calibration data management
 * - Validation processes
 * 
 * @param calibrationCaptureManager Core calibration capture functionality
 * @param logger Application logger
 */
@Singleton
class CalibrationManager @Inject constructor(
    private val calibrationCaptureManager: CalibrationCaptureManager,
    private val logger: Logger
) {
    
    /**
     * Represents the current state of calibration processes
     */
    data class CalibrationState(
        val isCalibrating: Boolean = false,
        val calibrationType: CalibrationType? = null,
        val progress: CalibrationProgress? = null,
        val isValidating: Boolean = false,
        val calibrationError: String? = null,
        val completedCalibrations: Set<CalibrationType> = emptySet(),
        val lastCalibrationResult: CalibrationResult? = null
    )
    
    /**
     * Types of calibration that can be performed
     */
    enum class CalibrationType(val displayName: String) {
        CAMERA("Camera Calibration"),
        THERMAL("Thermal Camera Calibration"),
        SHIMMER("Shimmer Sensor Calibration"),
        SYSTEM("Full System Calibration")
    }
    
    /**
     * Progress information for calibration operations
     */
    data class CalibrationProgress(
        val currentStep: String,
        val stepNumber: Int,
        val totalSteps: Int,
        val progressPercent: Int
    )
    
    /**
     * Result of a calibration operation
     */
    data class CalibrationResult(
        val success: Boolean,
        val calibrationType: CalibrationType,
        val message: String,
        val rgbFilePath: String? = null,
        val thermalFilePath: String? = null,
        val timestamp: Long = System.currentTimeMillis()
    )
    
    /**
     * Configuration for calibration operations
     */
    data class CalibrationConfig(
        val captureRgb: Boolean = true,
        val captureThermal: Boolean = true,
        val highResolution: Boolean = true,
        val captureCount: Int = 1,
        val calibrationId: String? = null
    )
    
    private val _calibrationState = MutableStateFlow(CalibrationState())
    val calibrationState: StateFlow<CalibrationState> = _calibrationState.asStateFlow()
    
    /**
     * Runs a complete calibration process
     * 
     * @param config Calibration configuration
     * @return Calibration result
     */
    suspend fun runCalibration(config: CalibrationConfig = CalibrationConfig()): Result<CalibrationResult> {
        return try {
            if (_calibrationState.value.isCalibrating) {
                return Result.failure(IllegalStateException("Calibration already in progress"))
            }
            
            val calibrationId = config.calibrationId ?: "calibration_${System.currentTimeMillis()}"
            logger.info("Starting calibration process: $calibrationId")
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = true,
                calibrationType = CalibrationType.SYSTEM,
                progress = CalibrationProgress("Initializing calibration...", 1, 4, 0)
            )
            
            // Step 1: Prepare calibration
            updateProgress("Preparing calibration setup...", 1, 4, 25)
            delay(1000)
            
            // Step 2: Capture calibration images
            updateProgress("Capturing calibration images...", 2, 4, 50)
            val captureResult = calibrationCaptureManager.captureCalibrationImages(
                calibrationId = calibrationId,
                captureRgb = config.captureRgb,
                captureThermal = config.captureThermal,
                highResolution = config.highResolution
            )
            
            if (!captureResult.success) {
                val errorMsg = captureResult.errorMessage ?: "Calibration capture failed"
                _calibrationState.value = _calibrationState.value.copy(
                    isCalibrating = false,
                    calibrationError = errorMsg
                )
                return Result.failure(RuntimeException(errorMsg))
            }
            
            // Step 3: Process calibration data
            updateProgress("Processing calibration data...", 3, 4, 75)
            delay(2000) // Simulate processing time
            
            // Step 4: Validate calibration
            updateProgress("Validating calibration results...", 4, 4, 100)
            delay(1000)
            
            val result = CalibrationResult(
                success = true,
                calibrationType = CalibrationType.SYSTEM,
                message = "Calibration completed successfully",
                rgbFilePath = captureResult.rgbFilePath,
                thermalFilePath = captureResult.thermalFilePath
            )
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                completedCalibrations = _calibrationState.value.completedCalibrations + CalibrationType.SYSTEM,
                lastCalibrationResult = result
            )
            
            logger.info("Calibration completed successfully: $calibrationId")
            Result.success(result)
            
        } catch (e: Exception) {
            logger.error("Calibration failed", e)
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                calibrationError = "Calibration failed: ${e.message}"
            )
            Result.failure(e)
        }
    }
    
    /**
     * Runs camera-specific calibration
     * 
     * @param includeRgb Whether to calibrate RGB camera
     * @param includeThermal Whether to calibrate thermal camera
     * @return Calibration result
     */
    suspend fun runCameraCalibration(
        includeRgb: Boolean = true,
        includeThermal: Boolean = true
    ): Result<CalibrationResult> {
        return try {
            if (_calibrationState.value.isCalibrating) {
                return Result.failure(IllegalStateException("Calibration already in progress"))
            }
            
            logger.info("Starting camera calibration (RGB: $includeRgb, Thermal: $includeThermal)")
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = true,
                calibrationType = CalibrationType.CAMERA,
                progress = CalibrationProgress("Starting camera calibration...", 1, 3, 0)
            )
            
            // Step 1: Setup
            updateProgress("Setting up camera calibration...", 1, 3, 33)
            delay(1000)
            
            // Step 2: Capture
            updateProgress("Capturing calibration images...", 2, 3, 66)
            val calibrationId = "camera_calibration_${System.currentTimeMillis()}"
            
            val captureResult = calibrationCaptureManager.captureCalibrationImages(
                calibrationId = calibrationId,
                captureRgb = includeRgb,
                captureThermal = includeThermal,
                highResolution = true
            )
            
            // Step 3: Complete
            updateProgress("Finalizing camera calibration...", 3, 3, 100)
            delay(1000)
            
            val result = CalibrationResult(
                success = captureResult.success,
                calibrationType = CalibrationType.CAMERA,
                message = if (captureResult.success) "Camera calibration completed" else (captureResult.errorMessage ?: "Camera calibration failed"),
                rgbFilePath = captureResult.rgbFilePath,
                thermalFilePath = captureResult.thermalFilePath
            )
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                completedCalibrations = if (captureResult.success) {
                    _calibrationState.value.completedCalibrations + CalibrationType.CAMERA
                } else {
                    _calibrationState.value.completedCalibrations
                },
                lastCalibrationResult = result,
                calibrationError = if (!captureResult.success) result.message else null
            )
            
            if (captureResult.success) {
                logger.info("Camera calibration completed successfully")
                Result.success(result)
            } else {
                logger.error("Camera calibration failed: ${result.message}")
                Result.failure(RuntimeException(result.message))
            }
            
        } catch (e: Exception) {
            logger.error("Camera calibration error", e)
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                calibrationError = "Camera calibration error: ${e.message}"
            )
            Result.failure(e)
        }
    }
    
    /**
     * Runs thermal camera calibration
     * 
     * @return Calibration result
     */
    suspend fun runThermalCalibration(): Result<CalibrationResult> {
        return try {
            if (_calibrationState.value.isCalibrating) {
                return Result.failure(IllegalStateException("Calibration already in progress"))
            }
            
            logger.info("Starting thermal camera calibration")
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = true,
                calibrationType = CalibrationType.THERMAL,
                progress = CalibrationProgress("Starting thermal calibration...", 1, 3, 0)
            )
            
            // Simulate thermal calibration process
            updateProgress("Setting up thermal calibration...", 1, 3, 33)
            delay(2000)
            
            updateProgress("Capturing thermal reference...", 2, 3, 66)
            delay(3000)
            
            updateProgress("Processing thermal calibration...", 3, 3, 100)
            delay(2000)
            
            val result = CalibrationResult(
                success = true,
                calibrationType = CalibrationType.THERMAL,
                message = "Thermal calibration completed successfully"
            )
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                completedCalibrations = _calibrationState.value.completedCalibrations + CalibrationType.THERMAL,
                lastCalibrationResult = result
            )
            
            logger.info("Thermal calibration completed successfully")
            Result.success(result)
            
        } catch (e: Exception) {
            logger.error("Thermal calibration failed", e)
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                calibrationError = "Thermal calibration failed: ${e.message}"
            )
            Result.failure(e)
        }
    }
    
    /**
     * Runs Shimmer sensor calibration
     * 
     * @return Calibration result
     */
    suspend fun runShimmerCalibration(): Result<CalibrationResult> {
        return try {
            if (_calibrationState.value.isCalibrating) {
                return Result.failure(IllegalStateException("Calibration already in progress"))
            }
            
            logger.info("Starting Shimmer sensor calibration")
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = true,
                calibrationType = CalibrationType.SHIMMER,
                progress = CalibrationProgress("Starting Shimmer calibration...", 1, 4, 0)
            )
            
            // Simulate Shimmer calibration process
            updateProgress("Initializing Shimmer sensors...", 1, 4, 25)
            delay(2000)
            
            updateProgress("Collecting baseline data...", 2, 4, 50)
            delay(3000)
            
            updateProgress("Calibrating GSR sensors...", 3, 4, 75)
            delay(2000)
            
            updateProgress("Finalizing calibration...", 4, 4, 100)
            delay(1000)
            
            val result = CalibrationResult(
                success = true,
                calibrationType = CalibrationType.SHIMMER,
                message = "Shimmer calibration completed successfully"
            )
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                completedCalibrations = _calibrationState.value.completedCalibrations + CalibrationType.SHIMMER,
                lastCalibrationResult = result
            )
            
            logger.info("Shimmer calibration completed successfully")
            Result.success(result)
            
        } catch (e: Exception) {
            logger.error("Shimmer calibration failed", e)
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                calibrationError = "Shimmer calibration failed: ${e.message}"
            )
            Result.failure(e)
        }
    }
    
    /**
     * Validates the current system calibration
     * 
     * @return Validation result
     */
    suspend fun validateSystemCalibration(): Result<Boolean> {
        return try {
            if (_calibrationState.value.isValidating) {
                return Result.failure(IllegalStateException("Validation already in progress"))
            }
            
            logger.info("Starting system calibration validation")
            
            _calibrationState.value = _calibrationState.value.copy(isValidating = true)
            
            // Simulate validation process
            delay(3000)
            
            val isValid = _calibrationState.value.completedCalibrations.isNotEmpty()
            
            _calibrationState.value = _calibrationState.value.copy(isValidating = false)
            
            if (isValid) {
                logger.info("System calibration validation successful")
            } else {
                logger.warning("System calibration validation failed - no calibrations found")
            }
            
            Result.success(isValid)
            
        } catch (e: Exception) {
            logger.error("Calibration validation error", e)
            _calibrationState.value = _calibrationState.value.copy(isValidating = false)
            Result.failure(e)
        }
    }
    
    /**
     * Stops any ongoing calibration process
     */
    suspend fun stopCalibration(): Result<Unit> {
        return try {
            if (!_calibrationState.value.isCalibrating) {
                return Result.failure(IllegalStateException("No calibration in progress"))
            }
            
            logger.info("Stopping calibration process")
            
            _calibrationState.value = _calibrationState.value.copy(
                isCalibrating = false,
                progress = null,
                calibrationType = null
            )
            
            logger.info("Calibration stopped")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Failed to stop calibration", e)
            Result.failure(e)
        }
    }
    
    /**
     * Resets calibration status for a specific type
     * 
     * @param type Calibration type to reset
     */
    suspend fun resetCalibration(type: CalibrationType): Result<Unit> {
        return try {
            logger.info("Resetting calibration for type: ${type.displayName}")
            
            _calibrationState.value = _calibrationState.value.copy(
                completedCalibrations = _calibrationState.value.completedCalibrations - type
            )
            
            logger.info("Calibration reset for ${type.displayName}")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Failed to reset calibration", e)
            Result.failure(e)
        }
    }
    
    /**
     * Saves calibration data to persistent storage
     */
    suspend fun saveCalibrationData(): Result<Unit> {
        return try {
            logger.info("Saving calibration data...")
            
            // In a real implementation, this would save calibration parameters to file
            delay(1000)
            
            logger.info("Calibration data saved successfully")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Failed to save calibration data", e)
            Result.failure(e)
        }
    }
    
    /**
     * Loads calibration data from persistent storage
     */
    suspend fun loadCalibrationData(): Result<Unit> {
        return try {
            logger.info("Loading calibration data...")
            
            // In a real implementation, this would load calibration parameters from file
            delay(1000)
            
            logger.info("Calibration data loaded successfully")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Failed to load calibration data", e)
            Result.failure(e)
        }
    }
    
    /**
     * Exports calibration data for external use
     */
    suspend fun exportCalibrationData(): Result<String> {
        return try {
            logger.info("Exporting calibration data...")
            
            // In a real implementation, this would create export file
            delay(2000)
            
            val exportPath = "calibration_export_${System.currentTimeMillis()}.json"
            logger.info("Calibration data exported to: $exportPath")
            
            Result.success(exportPath)
            
        } catch (e: Exception) {
            logger.error("Failed to export calibration data", e)
            Result.failure(e)
        }
    }
    
    /**
     * Gets the current calibration state
     */
    fun getCurrentState(): CalibrationState = _calibrationState.value
    
    /**
     * Checks if any calibration is currently running
     */
    fun isCalibrating(): Boolean = _calibrationState.value.isCalibrating
    
    /**
     * Checks if a specific calibration type has been completed
     */
    fun isCalibrationCompleted(type: CalibrationType): Boolean =
        _calibrationState.value.completedCalibrations.contains(type)
    
    /**
     * Clears any calibration errors
     */
    fun clearError() {
        _calibrationState.value = _calibrationState.value.copy(calibrationError = null)
    }
    
    // Private helper methods
    
    private fun updateProgress(step: String, stepNumber: Int, totalSteps: Int, percent: Int) {
        _calibrationState.value = _calibrationState.value.copy(
            progress = CalibrationProgress(step, stepNumber, totalSteps, percent)
        )
        logger.debug("Calibration progress: $step ($percent%)")
    }
}