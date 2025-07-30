package com.multisensor.recording.calibration

import android.content.Context
import android.os.Environment
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.atomic.AtomicInteger
import javax.inject.Inject
import javax.inject.Singleton

/**
 * CalibrationCaptureManager coordinates synchronized capture from RGB and thermal cameras
 * for Milestone 2.8 calibration and sync features.
 *
 * This manager ensures both cameras capture images in quick succession with matching
 * identifiers for later calibration processing.
 */
@Singleton
class CalibrationCaptureManager
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
        private val cameraRecorder: CameraRecorder,
        private val thermalRecorder: ThermalRecorder,
        private val syncClockManager: SyncClockManager,
        private val logger: Logger,
    ) {
        companion object {
            private const val CALIBRATION_DIR = "calibration"
            private const val RGB_SUFFIX = "_rgb.jpg"
            private const val THERMAL_SUFFIX = "_thermal.png"
            private const val MAX_CAPTURE_DELAY_MS = 100L // Maximum delay between RGB and thermal capture
        }

        private val captureCounter = AtomicInteger(0)
        private val dateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US)

        data class CalibrationCaptureResult(
            val success: Boolean,
            val calibrationId: String,
            val rgbFilePath: String?,
            val thermalFilePath: String?,
            val timestamp: Long,
            val syncedTimestamp: Long,
            val errorMessage: String? = null,
        )

        /**
         * Captures synchronized calibration images from both RGB and thermal cameras
         */
        suspend fun captureCalibrationImages(
            calibrationId: String? = null,
            captureRgb: Boolean = true,
            captureThermal: Boolean = true,
            highResolution: Boolean = true,
        ): CalibrationCaptureResult =
            withContext(Dispatchers.IO) {
                val actualCalibrationId = calibrationId ?: generateCalibrationId()
                val captureTimestamp = System.currentTimeMillis()
                val syncedTimestamp = syncClockManager.getSyncedTimestamp(captureTimestamp)

                logger.info("[DEBUG_LOG] Starting calibration capture: $actualCalibrationId")
                logger.info("[DEBUG_LOG] Capture settings - RGB: $captureRgb, Thermal: $captureThermal, HighRes: $highResolution")

                try {
                    // Ensure calibration directory exists
                    val calibrationDir = getCalibrationDirectory()
                    if (!calibrationDir.exists()) {
                        calibrationDir.mkdirs()
                    }

                    var rgbFilePath: String? = null
                    var thermalFilePath: String? = null
                    val captureJobs = mutableListOf<Deferred<String?>>()

                    // Start RGB capture if requested
                    if (captureRgb) {
                        val rgbJob =
                            async {
                                captureRgbImage(actualCalibrationId, highResolution, syncedTimestamp)
                            }
                        captureJobs.add(rgbJob)
                    }

                    // Start thermal capture if requested (with minimal delay for synchronization)
                    if (captureThermal) {
                        val thermalJob =
                            async {
                                delay(10) // Small delay to ensure thermal capture happens after RGB setup
                                captureThermalImage(actualCalibrationId, syncedTimestamp)
                            }
                        captureJobs.add(thermalJob)
                    }

                    // Wait for all captures to complete
                    val results = captureJobs.awaitAll()

                    // Process results
                    if (captureRgb && captureThermal) {
                        rgbFilePath = results[0]
                        thermalFilePath = results[1]
                    } else if (captureRgb) {
                        rgbFilePath = results[0]
                    } else if (captureThermal) {
                        thermalFilePath = results[0]
                    }

                    val success =
                        (captureRgb && rgbFilePath != null || !captureRgb) &&
                            (captureThermal && thermalFilePath != null || !captureThermal)

                    if (success) {
                        logger.info("[DEBUG_LOG] Calibration capture successful: $actualCalibrationId")
                        logger.info("[DEBUG_LOG] RGB file: $rgbFilePath")
                        logger.info("[DEBUG_LOG] Thermal file: $thermalFilePath")
                    } else {
                        logger.error("Calibration capture failed for: $actualCalibrationId")
                    }

                    CalibrationCaptureResult(
                        success = success,
                        calibrationId = actualCalibrationId,
                        rgbFilePath = rgbFilePath,
                        thermalFilePath = thermalFilePath,
                        timestamp = captureTimestamp,
                        syncedTimestamp = syncedTimestamp,
                    )
                } catch (e: Exception) {
                    logger.error("Error during calibration capture: $actualCalibrationId", e)
                    CalibrationCaptureResult(
                        success = false,
                        calibrationId = actualCalibrationId,
                        rgbFilePath = null,
                        thermalFilePath = null,
                        timestamp = captureTimestamp,
                        syncedTimestamp = syncedTimestamp,
                        errorMessage = e.message,
                    )
                }
            }

        /**
         * Captures RGB calibration image
         */
        private suspend fun captureRgbImage(
            calibrationId: String,
            highResolution: Boolean,
            syncedTimestamp: Long,
        ): String? =
            withContext(Dispatchers.IO) {
                try {
                    val fileName = "${calibrationId}${RGB_SUFFIX}"
                    val filePath = File(getCalibrationDirectory(), fileName).absolutePath

                    logger.info("[DEBUG_LOG] Capturing RGB calibration image: $fileName (highRes: $highResolution, syncTime: $syncedTimestamp)")

                    // Use CameraRecorder's calibration capture method
                    val success = cameraRecorder.captureCalibrationImage(filePath)

                    if (success) {
                        logger.info("[DEBUG_LOG] RGB calibration image captured successfully: $filePath at timestamp $syncedTimestamp")
                        filePath
                    } else {
                        logger.error("Failed to capture RGB calibration image: $fileName")
                        null
                    }
                } catch (e: Exception) {
                    logger.error("Error capturing RGB calibration image", e)
                    null
                }
            }

        /**
         * Captures thermal calibration image
         */
        private suspend fun captureThermalImage(
            calibrationId: String,
            syncedTimestamp: Long,
        ): String? =
            withContext(Dispatchers.IO) {
                try {
                    val fileName = "${calibrationId}${THERMAL_SUFFIX}"
                    val filePath = File(getCalibrationDirectory(), fileName).absolutePath

                    logger.info("[DEBUG_LOG] Capturing thermal calibration image: $fileName (syncTime: $syncedTimestamp)")

                    // Use ThermalRecorder's calibration capture method
                    val success = thermalRecorder.captureCalibrationImage(filePath)

                    if (success) {
                        logger.info("[DEBUG_LOG] Thermal calibration image captured successfully: $filePath at timestamp $syncedTimestamp")
                        filePath
                    } else {
                        logger.error("Failed to capture thermal calibration image: $fileName")
                        null
                    }
                } catch (e: Exception) {
                    logger.error("Error capturing thermal calibration image", e)
                    null
                }
            }

        /**
         * Generates a unique calibration ID
         */
        private fun generateCalibrationId(): String {
            val timestamp = dateFormat.format(Date())
            val counter = captureCounter.incrementAndGet()
            return "calib_${timestamp}_${String.format("%03d", counter)}"
        }

        /**
         * Gets the calibration directory, creating it if necessary
         */
        private fun getCalibrationDirectory(): File {
            val externalDir =
                context.getExternalFilesDir(Environment.DIRECTORY_PICTURES)
                    ?: context.filesDir // Fallback to internal storage

            return File(externalDir, CALIBRATION_DIR)
        }

        /**
         * Lists all calibration capture sessions
         */
        fun getCalibrationSessions(): List<CalibrationSession> {
            val calibrationDir = getCalibrationDirectory()
            if (!calibrationDir.exists()) {
                return emptyList()
            }

            val sessions = mutableMapOf<String, CalibrationSession>()

            calibrationDir.listFiles()?.forEach { file ->
                if (file.isFile) {
                    val fileName = file.nameWithoutExtension
                    val calibrationId =
                        when {
                            fileName.endsWith("_rgb") -> fileName.removeSuffix("_rgb")
                            fileName.endsWith("_thermal") -> fileName.removeSuffix("_thermal")
                            else -> fileName
                        }

                    val session =
                        sessions.getOrPut(calibrationId) {
                            CalibrationSession(calibrationId, null, null, file.lastModified())
                        }

                    when {
                        file.name.endsWith(RGB_SUFFIX) -> sessions[calibrationId] = session.copy(rgbFile = file)
                        file.name.endsWith(THERMAL_SUFFIX) -> sessions[calibrationId] = session.copy(thermalFile = file)
                    }
                }
            }

            return sessions.values.sortedByDescending { it.timestamp }
        }

        /**
         * Deletes a calibration session and its associated files
         */
        fun deleteCalibrationSession(calibrationId: String): Boolean =
            try {
                val calibrationDir = getCalibrationDirectory()
                val rgbFile = File(calibrationDir, "${calibrationId}${RGB_SUFFIX}")
                val thermalFile = File(calibrationDir, "${calibrationId}${THERMAL_SUFFIX}")

                var deleted = true
                if (rgbFile.exists()) {
                    deleted = deleted && rgbFile.delete()
                }
                if (thermalFile.exists()) {
                    deleted = deleted && thermalFile.delete()
                }

                logger.info("[DEBUG_LOG] Calibration session deleted: $calibrationId, success: $deleted")
                deleted
            } catch (e: Exception) {
                logger.error("Error deleting calibration session: $calibrationId", e)
                false
            }

        /**
         * Gets calibration statistics
         */
        fun getCalibrationStatistics(): CalibrationStatistics {
            val sessions = getCalibrationSessions()
            val totalSessions = sessions.size
            val completeSessions = sessions.count { it.rgbFile != null && it.thermalFile != null }
            val rgbOnlySessions = sessions.count { it.rgbFile != null && it.thermalFile == null }
            val thermalOnlySessions = sessions.count { it.rgbFile == null && it.thermalFile != null }

            return CalibrationStatistics(
                totalSessions = totalSessions,
                completeSessions = completeSessions,
                rgbOnlySessions = rgbOnlySessions,
                thermalOnlySessions = thermalOnlySessions,
                totalCaptures = captureCounter.get(),
            )
        }

        data class CalibrationSession(
            val calibrationId: String,
            val rgbFile: File?,
            val thermalFile: File?,
            val timestamp: Long,
        )

        data class CalibrationStatistics(
            val totalSessions: Int,
            val completeSessions: Int,
            val rgbOnlySessions: Int,
            val thermalOnlySessions: Int,
            val totalCaptures: Int,
        )
    }
