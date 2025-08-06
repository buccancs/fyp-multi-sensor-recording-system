package com.multisensor.recording.service

import android.content.Context
import android.os.Environment
import com.multisensor.recording.persistence.*
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SessionManager
@Inject
constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger,
    private val thermalSettings: ThermalCameraSettings,
    private val sessionStateDao: SessionStateDao,
    private val crashRecoveryManager: CrashRecoveryManager,
) {
    private var currentSession: RecordingSession? = null
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.getDefault())

    companion object {
        private const val BASE_FOLDER_NAME = "MultiSensorRecording"
        private const val SESSION_INFO_FILE = "session_info.txt"
        private const val SESSION_CONFIG_FILE = "session_config.json"
        private const val RGB_VIDEO_FILE = "rgb_video.mp4"
        private const val THERMAL_VIDEO_FILE = "thermal_video.mp4"
        private const val THERMAL_DATA_FOLDER = "thermal_data"
        private const val RAW_FRAMES_FOLDER = "raw_frames"
        private const val SHIMMER_DATA_FILE = "shimmer_data.csv"
        private const val LOG_FILE = "session_log.txt"
        private const val CALIBRATION_FOLDER = "calibration"
    }

    data class RecordingSession(
        val sessionId: String,
        val startTime: Long,
        val sessionFolder: File,
        var endTime: Long? = null,
        var status: SessionStatus = SessionStatus.ACTIVE,
    )

    enum class SessionStatus {
        ACTIVE,
        COMPLETED,
        FAILED,
        CANCELLED,
    }

    suspend fun createNewSession(): String =
        withContext(Dispatchers.IO) {
            try {
                val timestamp = dateFormat.format(Date())
                val sessionId = "session_$timestamp"

                logger.info("Creating new session: $sessionId")

                val baseFolder = getBaseRecordingFolder()
                val sessionFolder = File(baseFolder, sessionId)

                if (!sessionFolder.exists() && !sessionFolder.mkdirs()) {
                    throw Exception("Failed to create session folder: ${sessionFolder.absolutePath}")
                }

                createSessionSubfolders(sessionFolder)

                val session =
                    RecordingSession(
                        sessionId = sessionId,
                        startTime = System.currentTimeMillis(),
                        sessionFolder = sessionFolder,
                    )

                currentSession = session

                val sessionState = SessionState(
                    sessionId = sessionId,
                    recordingState = RecordingState.STARTING,
                    deviceStates = emptyList(),
                    timestamp = System.currentTimeMillis(),
                    startTime = session.startTime
                )
                sessionStateDao.insertSessionState(sessionState)

                writeSessionInfo(session)

                writeSessionConfig(session)

                logger.info("Session created successfully: $sessionId at ${sessionFolder.absolutePath}")

                sessionId
            } catch (e: CancellationException) {
                throw e
            } catch (e: SecurityException) {
                logger.error("Permission error creating session: ${e.message}", e)
                throw e
            } catch (e: java.io.IOException) {
                logger.error("IO error creating session: ${e.message}", e)
                throw e
            } catch (e: IllegalStateException) {
                logger.error("Invalid state creating session: ${e.message}", e)
                throw e
            } catch (e: RuntimeException) {
                logger.error("Runtime error creating session: ${e.message}", e)
                throw e
            }
        }

    fun getCurrentSession(): RecordingSession? = currentSession

    fun getSessionOutputDir(): File? {
        return currentSession?.sessionFolder
    }

    fun addStimulusEvent(timestamp: Long, eventType: String) {
        currentSession?.let { session ->
            try {
                logger.info("Adding stimulus event to session ${session.sessionId}: type=$eventType, timestamp=$timestamp")

                val stimulusFile = File(session.sessionFolder, "stimulus_events.csv")
                val isNewFile = !stimulusFile.exists()

                stimulusFile.appendText(
                    if (isNewFile) {
                        "timestamp_ms,event_type,session_time_ms\n$timestamp,$eventType,${timestamp - session.startTime}\n"
                    } else {
                        "$timestamp,$eventType,${timestamp - session.startTime}\n"
                    }
                )

                logger.info("Stimulus event recorded in: ${stimulusFile.absolutePath}")
            } catch (e: CancellationException) {
                throw e
            } catch (e: SecurityException) {
                logger.error("Permission error adding stimulus event: ${e.message}", e)
            } catch (e: java.io.IOException) {
                logger.error("IO error adding stimulus event: ${e.message}", e)
            } catch (e: IllegalStateException) {
                logger.error("Invalid state adding stimulus event: ${e.message}", e)
            } catch (e: RuntimeException) {
                logger.error("Runtime error adding stimulus event: ${e.message}", e)
            }
        }
    }

    suspend fun finalizeCurrentSession() =
        withContext(Dispatchers.IO) {
            currentSession?.let { session ->
                try {
                    logger.info("Finalizing session: ${session.sessionId}")

                    session.endTime = System.currentTimeMillis()
                    session.status = SessionStatus.COMPLETED

                    val existingState = sessionStateDao.getSessionState(session.sessionId)
                    if (existingState != null) {
                        val updatedState = existingState.copy(
                            recordingState = RecordingState.COMPLETED,
                            endTime = session.endTime!!,
                            timestamp = System.currentTimeMillis()
                        )
                        sessionStateDao.updateSessionState(updatedState)
                    }

                    writeSessionInfo(session)

                    logSessionSummary(session)

                    logger.info("Session finalized: ${session.sessionId}")
                } catch (e: CancellationException) {
                    throw e
                } catch (e: SecurityException) {
                    logger.error("Permission error finalizing session ${session.sessionId}: ${e.message}", e)
                    session.status = SessionStatus.FAILED
                    writeSessionInfo(session)
                } catch (e: java.io.IOException) {
                    logger.error("IO error finalizing session ${session.sessionId}: ${e.message}", e)
                    session.status = SessionStatus.FAILED
                    writeSessionInfo(session)
                } catch (e: IllegalStateException) {
                    logger.error("Invalid state finalizing session ${session.sessionId}: ${e.message}", e)
                    session.status = SessionStatus.FAILED
                    writeSessionInfo(session)
                } catch (e: RuntimeException) {
                    logger.error("Runtime error finalizing session ${session.sessionId}: ${e.message}", e)
                    session.status = SessionStatus.FAILED
                    writeSessionInfo(session)
                } finally {
                    currentSession = null
                }
            }
        }

    suspend fun initializeCrashRecovery() {
        try {
            logger.info("SessionManager: Initializing crash recovery")

            val needsRecovery = crashRecoveryManager.detectCrashRecovery()
            if (needsRecovery) {
                logger.info("SessionManager: Crash recovery needed - starting recovery process")
                crashRecoveryManager.recoverAllActiveSessions()
            } else {
                logger.info("SessionManager: No crash recovery needed")
            }

            crashRecoveryManager.cleanupOldSessions(30)
        } catch (e: Exception) {
            logger.error("SessionManager: Error during crash recovery initialization", e)
        }
    }

    suspend fun updateSessionDeviceStates(deviceStates: List<DeviceState>) {
        currentSession?.let { session ->
            try {
                val existingState = sessionStateDao.getSessionState(session.sessionId)
                if (existingState != null) {
                    val updatedState = existingState.copy(
                        deviceStates = deviceStates,
                        timestamp = System.currentTimeMillis()
                    )
                    sessionStateDao.updateSessionState(updatedState)
                }
            } catch (e: Exception) {
                logger.error("SessionManager: Error updating session device states", e)
            }
        }
    }

    suspend fun updateSessionRecordingState(recordingState: RecordingState) {
        currentSession?.let { session ->
            try {
                val existingState = sessionStateDao.getSessionState(session.sessionId)
                if (existingState != null) {
                    val updatedState = existingState.copy(
                        recordingState = recordingState,
                        timestamp = System.currentTimeMillis()
                    )
                    sessionStateDao.updateSessionState(updatedState)
                }
            } catch (e: Exception) {
                logger.error("SessionManager: Error updating session recording state", e)
            }
        }
    }

    fun getSessionFilePaths(): SessionFilePaths? =
        currentSession?.let { session ->
            SessionFilePaths(
                sessionFolder = session.sessionFolder,
                rgbVideoFile = File(session.sessionFolder, RGB_VIDEO_FILE),
                thermalVideoFile = File(session.sessionFolder, THERMAL_VIDEO_FILE),
                thermalDataFolder = File(session.sessionFolder, THERMAL_DATA_FOLDER),
                rawFramesFolder = File(session.sessionFolder, RAW_FRAMES_FOLDER),
                shimmerDataFile = File(session.sessionFolder, SHIMMER_DATA_FILE),
                logFile = File(session.sessionFolder, LOG_FILE),
                calibrationFolder = File(session.sessionFolder, CALIBRATION_FOLDER),
                sessionConfigFile = File(session.sessionFolder, SESSION_CONFIG_FILE),
            )
        }

    data class SessionFilePaths(
        val sessionFolder: File,
        val rgbVideoFile: File,
        val thermalVideoFile: File,
        val thermalDataFolder: File,
        val rawFramesFolder: File,
        val shimmerDataFile: File,
        val logFile: File,
        val calibrationFolder: File,
        val sessionConfigFile: File,
    )

    private fun getBaseRecordingFolder(): File {
        val baseDir =
            if (Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED) {
                File(Environment.getExternalStorageDirectory(), BASE_FOLDER_NAME)
            } else {
                File(context.filesDir, BASE_FOLDER_NAME)
            }

        if (!baseDir.exists() && !baseDir.mkdirs()) {
            logger.warning("Failed to create base recording folder, using app internal storage")
            return File(context.filesDir, BASE_FOLDER_NAME).apply {
                mkdirs()
            }
        }

        return baseDir
    }

    private fun createSessionSubfolders(sessionFolder: File) {
        val rawFramesFolder = File(sessionFolder, RAW_FRAMES_FOLDER)
        if (!rawFramesFolder.exists() && !rawFramesFolder.mkdirs()) {
            logger.warning("Failed to create raw frames folder: ${rawFramesFolder.absolutePath}")
        }

        val thermalDataFolder = File(sessionFolder, THERMAL_DATA_FOLDER)
        if (!thermalDataFolder.exists() && !thermalDataFolder.mkdirs()) {
            logger.warning("Failed to create thermal data folder: ${thermalDataFolder.absolutePath}")
        }

        val calibrationFolder = File(sessionFolder, CALIBRATION_FOLDER)
        if (!calibrationFolder.exists() && !calibrationFolder.mkdirs()) {
            logger.warning("Failed to create calibration folder: ${calibrationFolder.absolutePath}")
        }
    }

    private fun writeSessionInfo(session: RecordingSession) {
        try {
            val infoFile = File(session.sessionFolder, SESSION_INFO_FILE)
            val duration = session.endTime?.let { it - session.startTime } ?: 0

            val info =
                buildString {
                    appendLine("Session ID: ${session.sessionId}")
                    appendLine("Start Time: ${Date(session.startTime)}")
                    session.endTime?.let {
                        appendLine("End Time: ${Date(it)}")
                        appendLine("Duration: ${duration / 1000} seconds")
                    }
                    appendLine("Status: ${session.status}")
                    appendLine("Session Folder: ${session.sessionFolder.absolutePath}")
                    appendLine("Created: ${Date()}")
                    appendLine("")
                    appendLine("=== Folder Structure ===")
                    appendLine("RGB Video: $RGB_VIDEO_FILE")
                    appendLine("Thermal Video: $THERMAL_VIDEO_FILE")
                    appendLine("Thermal Data: $THERMAL_DATA_FOLDER/")
                    appendLine("Raw Frames: $RAW_FRAMES_FOLDER/")
                    appendLine("Shimmer Data: $SHIMMER_DATA_FILE")
                    appendLine("Calibration: $CALIBRATION_FOLDER/")
                    appendLine("Session Config: $SESSION_CONFIG_FILE")
                    appendLine("Log File: $LOG_FILE")
                }

            infoFile.writeText(info)
        } catch (e: Exception) {
            logger.error("Failed to write session info", e)
        }
    }

    private fun writeSessionConfig(session: RecordingSession) {
        try {
            val configFile = File(session.sessionFolder, SESSION_CONFIG_FILE)
            val thermalConfig = thermalSettings.getCurrentConfig()

            val configJson = buildString {
                appendLine("{")
                appendLine("  \"session_id\": \"${session.sessionId}\",")
                appendLine("  \"start_time\": ${session.startTime},")
                appendLine("  \"timestamp\": \"${Date(session.startTime)}\",")
                appendLine("  \"thermal_camera\": {")
                appendLine("    \"enabled\": ${thermalConfig.isEnabled},")
                appendLine("    \"frame_rate\": ${thermalConfig.frameRate},")
                appendLine("    \"color_palette\": \"${thermalConfig.colorPalette}\",")
                appendLine("    \"temperature_range\": \"${thermalConfig.temperatureRange}\",")
                appendLine("    \"emissivity\": ${thermalConfig.emissivity},")
                appendLine("    \"auto_calibration\": ${thermalConfig.autoCalibration},")
                appendLine("    \"high_resolution\": ${thermalConfig.highResolution},")
                appendLine("    \"temperature_units\": \"${thermalConfig.temperatureUnits}\",")
                appendLine("    \"usb_priority\": ${thermalConfig.usbPriority},")
                appendLine("    \"data_format\": \"${thermalConfig.dataFormat}\"")
                appendLine("  },")
                appendLine("  \"folder_structure\": {")
                appendLine("    \"rgb_video\": \"$RGB_VIDEO_FILE\",")
                appendLine("    \"thermal_video\": \"$THERMAL_VIDEO_FILE\",")
                appendLine("    \"thermal_data_folder\": \"$THERMAL_DATA_FOLDER\",")
                appendLine("    \"raw_frames_folder\": \"$RAW_FRAMES_FOLDER\",")
                appendLine("    \"shimmer_data\": \"$SHIMMER_DATA_FILE\",")
                appendLine("    \"calibration_folder\": \"$CALIBRATION_FOLDER\",")
                appendLine("    \"log_file\": \"$LOG_FILE\"")
                appendLine("  }")
                appendLine("}")
            }

            configFile.writeText(configJson)
            logger.debug("Session configuration written to: ${configFile.absolutePath}")
        } catch (e: Exception) {
            logger.error("Failed to write session config", e)
        }
    }

    private fun logSessionSummary(session: RecordingSession) {
        try {
            val duration = session.endTime?.let { it - session.startTime } ?: 0
            val filePaths =
                SessionFilePaths(
                    sessionFolder = session.sessionFolder,
                    rgbVideoFile = File(session.sessionFolder, RGB_VIDEO_FILE),
                    thermalVideoFile = File(session.sessionFolder, THERMAL_VIDEO_FILE),
                    thermalDataFolder = File(session.sessionFolder, THERMAL_DATA_FOLDER),
                    rawFramesFolder = File(session.sessionFolder, RAW_FRAMES_FOLDER),
                    shimmerDataFile = File(session.sessionFolder, SHIMMER_DATA_FILE),
                    logFile = File(session.sessionFolder, LOG_FILE),
                    calibrationFolder = File(session.sessionFolder, CALIBRATION_FOLDER),
                    sessionConfigFile = File(session.sessionFolder, SESSION_CONFIG_FILE),
                )

            logger.info("Session Summary:")
            logger.info("  Session ID: ${session.sessionId}")
            logger.info("  Duration: ${duration / 1000} seconds")
            logger.info("  RGB Video: ${if (filePaths.rgbVideoFile.exists()) "✓" else "✗"} (${filePaths.rgbVideoFile.length()} bytes)")
            logger.info(
                "  Thermal Video: ${if (filePaths.thermalVideoFile.exists()) "✓" else "✗"} (${filePaths.thermalVideoFile.length()} bytes)",
            )
            logger.info("  Raw Frames: ${filePaths.rawFramesFolder.listFiles()?.size ?: 0} files")
            logger.info(
                "  Shimmer Data: ${if (filePaths.shimmerDataFile.exists()) "✓" else "✗"} (${filePaths.shimmerDataFile.length()} bytes)",
            )
            logger.info("  Session Folder: ${session.sessionFolder.absolutePath}")
        } catch (e: Exception) {
            logger.error("Failed to log session summary", e)
        }
    }

    fun getAvailableStorageSpace(): Long =
        try {
            val baseFolder = getBaseRecordingFolder()
            baseFolder.freeSpace
        } catch (e: Exception) {
            logger.error("Failed to get available storage space", e)
            0L
        }

    fun hasSufficientStorage(requiredSpaceBytes: Long = 1024 * 1024 * 1024): Boolean {
        return getAvailableStorageSpace() > requiredSpaceBytes
    }

    suspend fun getAllSessions(): List<com.multisensor.recording.recording.SessionInfo> =
        withContext(Dispatchers.IO) {
            return@withContext try {
                val baseFolder = getBaseRecordingFolder()
                val sessions = mutableListOf<com.multisensor.recording.recording.SessionInfo>()

                if (!baseFolder.exists()) {
                    logger.info("Base recording folder does not exist")
                    return@withContext emptyList()
                }

                baseFolder.listFiles()?.forEach { sessionFolder ->
                    if (sessionFolder.isDirectory && sessionFolder.name.startsWith("session_")) {
                        try {
                            val sessionInfo = reconstructSessionInfo(sessionFolder)
                            if (sessionInfo != null) {
                                sessions.add(sessionInfo)
                            }
                        } catch (e: Exception) {
                            logger.error("Failed to reconstruct session from folder: ${sessionFolder.name}", e)
                        }
                    }
                }

                sessions.sortedByDescending { it.startTime }
            } catch (e: Exception) {
                logger.error("Failed to get all sessions", e)
                emptyList()
            }
        }

    private fun reconstructSessionInfo(sessionFolder: File): com.multisensor.recording.recording.SessionInfo? =
        try {
            val sessionId = sessionFolder.name

            val infoFile = File(sessionFolder, SESSION_INFO_FILE)
            var startTime = sessionFolder.lastModified()
            var endTime = 0L
            var errorOccurred = false
            var errorMessage: String? = null

            if (infoFile.exists()) {
                try {
                    val infoContent = infoFile.readText()
                    infoContent.lines().forEach { line ->
                        when {
                            line.startsWith("Start Time:") -> {
                            }

                            line.startsWith("End Time:") -> {
                            }

                            line.startsWith("Status: FAILED") -> {
                                errorOccurred = true
                                errorMessage = "Session failed"
                            }
                        }
                    }
                } catch (e: Exception) {
                    logger.debug("Could not parse session info file for $sessionId", e)
                }
            }

            val rgbVideoFile = File(sessionFolder, RGB_VIDEO_FILE)
            val thermalVideoFile = File(sessionFolder, THERMAL_VIDEO_FILE)
            val rawFramesFolder = File(sessionFolder, RAW_FRAMES_FOLDER)
            val shimmerDataFile = File(sessionFolder, SHIMMER_DATA_FILE)

            val videoEnabled = rgbVideoFile.exists() && rgbVideoFile.length() > 0
            val thermalEnabled = thermalVideoFile.exists() && thermalVideoFile.length() > 0
            val rawEnabled = rawFramesFolder.exists() && (rawFramesFolder.listFiles()?.isNotEmpty() == true)

            val sessionInfo =
                com.multisensor.recording.recording.SessionInfo(
                    sessionId = sessionId,
                    videoEnabled = videoEnabled,
                    rawEnabled = rawEnabled,
                    thermalEnabled = thermalEnabled,
                    startTime = startTime,
                    endTime = if (endTime > 0) endTime else System.currentTimeMillis(),
                    videoFilePath = if (videoEnabled) rgbVideoFile.absolutePath else null,
                    thermalFilePath = if (thermalEnabled) thermalVideoFile.absolutePath else null,
                    errorOccurred = errorOccurred,
                    errorMessage = errorMessage,
                )

            if (rawEnabled) {
                rawFramesFolder.listFiles()?.forEach { rawFile ->
                    if (rawFile.isFile && rawFile.name.endsWith(".dng")) {
                        sessionInfo.addRawFile(rawFile.absolutePath)
                    }
                }
            }

            if (thermalEnabled) {
                val thermalFileSize = thermalVideoFile.length()
                val estimatedFrameCount = thermalFileSize / (256 * 192 * 2 + 8)
                sessionInfo.updateThermalFrameCount(estimatedFrameCount)
            }

            if (endTime > 0) {
                sessionInfo.markCompleted()
            }

            logger.debug("Reconstructed session: ${sessionInfo.getSummary()}")
            sessionInfo
        } catch (e: Exception) {
            logger.error("Failed to reconstruct session info from folder: ${sessionFolder.name}", e)
            null
        }

    suspend fun deleteAllSessions(): Boolean =
        withContext(Dispatchers.IO) {
            return@withContext try {
                val baseFolder = getBaseRecordingFolder()

                if (!baseFolder.exists()) {
                    logger.info("Base recording folder does not exist, nothing to delete")
                    return@withContext true
                }

                var deletedCount = 0
                var failedCount = 0

                baseFolder.listFiles()?.forEach { sessionFolder ->
                    if (sessionFolder.isDirectory && sessionFolder.name.startsWith("session_")) {
                        try {
                            if (deleteSessionFolder(sessionFolder)) {
                                deletedCount++
                                logger.info("Deleted session folder: ${sessionFolder.name}")
                            } else {
                                failedCount++
                                logger.warning("Failed to delete session folder: ${sessionFolder.name}")
                            }
                        } catch (e: Exception) {
                            failedCount++
                            logger.error("Error deleting session folder: ${sessionFolder.name}", e)
                        }
                    }
                }

                logger.info("Session deletion complete - Deleted: $deletedCount, Failed: $failedCount")

                deletedCount > 0 && failedCount == 0
            } catch (e: Exception) {
                logger.error("Failed to delete all sessions", e)
                false
            }
        }

    private fun deleteSessionFolder(folder: File): Boolean =
        try {
            if (folder.isDirectory) {
                folder.listFiles()?.forEach { file ->
                    if (file.isDirectory) {
                        deleteSessionFolder(file)
                    } else {
                        file.delete()
                    }
                }
            }
            folder.delete()
        } catch (e: Exception) {
            logger.error("Failed to delete folder: ${folder.absolutePath}", e)
            false
        }
}

