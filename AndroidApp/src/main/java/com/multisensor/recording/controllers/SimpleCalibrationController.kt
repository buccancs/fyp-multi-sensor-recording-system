package com.multisensor.recording.controllers

import android.content.Context
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SimpleCalibrationController @Inject constructor(
    private val calibrationCaptureManager: CalibrationCaptureManager,
    private val logger: Logger
) {

    enum class CalibrationPattern(val displayName: String, val pointCount: Int) {
        SINGLE_POINT("Single Point Calibration", 1),
        MULTI_POINT("Multi-Point Calibration", 4),
        GRID_BASED("Grid-Based Calibration", 9)
    }

    suspend fun startCalibration(pattern: CalibrationPattern): Boolean {
        return try {
            logger.info("Starting calibration with pattern: ${pattern.displayName}")
            calibrationCaptureManager.startCalibration()
            true
        } catch (e: Exception) {
            logger.error("Failed to start calibration", e)
            false
        }
    }

    suspend fun stopCalibration(): Boolean {
        return try {
            calibrationCaptureManager.stopCalibration()
            logger.info("Calibration stopped")
            true
        } catch (e: Exception) {
            logger.error("Failed to stop calibration", e)
            false
        }
    }

    suspend fun captureCalibrationPoint(): Boolean {
        return try {
            calibrationCaptureManager.captureCalibrationFrame()
            logger.info("Calibration point captured")
            true
        } catch (e: Exception) {
            logger.error("Failed to capture calibration point", e)
            false
        }
    }

    fun isCalibrating(): Boolean {
        return calibrationCaptureManager.isCalibrating()
    }
}