package com.multisensor.recording.service

import android.content.Context
import android.os.Environment
import com.multisensor.recording.persistence.CrashRecoveryManager
import com.multisensor.recording.persistence.DeviceState
import com.multisensor.recording.persistence.RecordingState
import com.multisensor.recording.persistence.SessionState
import com.multisensor.recording.persistence.SessionStateDao
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manages recording sessions, including file organization, session lifecycle,
 * and data storage coordination.
 */
@Singleton
class SessionManager
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
        private val logger: Logger,
        private val thermalSettings: ThermalCameraSettings,
        private val sessionStateDao: SessionStateDao, // Phase 3: State Persistence
        private val crashRecoveryManager: CrashRecoveryManager, // Phase 3: Crash Recovery
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

        /**
         * Data class representing a recording session
         */
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

        /**
         * Creates a new recording session with organized folder structure
         */
        suspend fun createNewSession(): String =
            withContext(Dispatchers.IO) {
                try {
                    val timestamp = dateFormat.format(Date())
                    val sessionId = "session_$timestamp"

                    logger.info("Creating new session: $sessionId")

                    // Create session folder
                    val baseFolder = getBaseRecordingFolder()
                    val sessionFolder = File(baseFolder, sessionId)

                    if (!sessionFolder.exists() && !sessionFolder.mkdirs()) {
                        throw Exception("Failed to create session folder: ${sessionFolder.absolutePath}")
                    }

                    // Create subfolders
                    createSessionSubfolders(sessionFolder)

                    // Create session object
                    val session =
                        RecordingSession(
                            sessionId = sessionId,
                            startTime = System.currentTimeMillis(),
                            sessionFolder = sessionFolder,
                        )

                    currentSession = session

                    // Phase 3: Persist session state to database
                    val sessionState = SessionState(
                        sessionId = sessionId,
                        recordingState = RecordingState.STARTING,
                        deviceStates = emptyList(), // Will be updated by recording service
                        timestamp = System.currentTimeMillis(),
                        startTime = session.startTime
                    )
                    sessionStateDao.insertSessionState(sessionState)

                    // Write session info file
                    writeSessionInfo(session)

                    // Write session configuration file with thermal settings
                    writeSessionConfig(session)

                    logger.info("Session created successfully: $sessionId at ${sessionFolder.absolutePath}")

                    sessionId
                } catch (e: Exception) {
                    logger.error("Failed to create new session", e)
                    throw e
                }
            }

        /**
         * Gets the current active session
         */
        fun getCurrentSession(): RecordingSession? = currentSession

        /**
         * Finalizes the current session
         */
        suspend fun finalizeCurrentSession() =
            withContext(Dispatchers.IO) {
                currentSession?.let { session ->
                    try {
                        logger.info("Finalizing session: ${session.sessionId}")

                        session.endTime = System.currentTimeMillis()
                        session.status = SessionStatus.COMPLETED

                        // Phase 3: Update session state in database
                        val existingState = sessionStateDao.getSessionState(session.sessionId)
                        if (existingState != null) {
                            val updatedState = existingState.copy(
                                recordingState = RecordingState.COMPLETED,
                                endTime = session.endTime!!,
                                timestamp = System.currentTimeMillis()
                            )
                            sessionStateDao.updateSessionState(updatedState)
                        }

                        // Update session info file
                        writeSessionInfo(session)

                        // Log session summary
                        logSessionSummary(session)

                        logger.info("Session finalized: ${session.sessionId}")
                    } catch (e: Exception) {
                        logger.error("Failed to finalize session: ${session.sessionId}", e)
                        session.status = SessionStatus.FAILED
                        writeSessionInfo(session)
                    } finally {
                        currentSession = null
                    }
                }
            }

        /**
         * Phase 3: Initialize crash recovery on app startup
         */
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
                
                // Clean up old sessions periodically
                crashRecoveryManager.cleanupOldSessions(30) // Keep 30 days
            } catch (e: Exception) {
                logger.error("SessionManager: Error during crash recovery initialization", e)
            }
        }

        /**
         * Phase 3: Update session state with device information
         */
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

        /**
         * Phase 3: Update session recording state
         */
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

        /**
         * Gets file paths for different data types in the current session
         */
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

        /**
         * Data class containing file paths for a session
         */
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

        /**
         * Gets the base recording folder, creating it if necessary
         */
        private fun getBaseRecordingFolder(): File {
            // Use external storage if available, otherwise use internal storage
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

        /**
         * Creates necessary subfolders for a session
         */
        private fun createSessionSubfolders(sessionFolder: File) {
            // Create raw frames folder
            val rawFramesFolder = File(sessionFolder, RAW_FRAMES_FOLDER)
            if (!rawFramesFolder.exists() && !rawFramesFolder.mkdirs()) {
                logger.warning("Failed to create raw frames folder: ${rawFramesFolder.absolutePath}")
            }
            
            // Create thermal data folder
            val thermalDataFolder = File(sessionFolder, THERMAL_DATA_FOLDER)
            if (!thermalDataFolder.exists() && !thermalDataFolder.mkdirs()) {
                logger.warning("Failed to create thermal data folder: ${thermalDataFolder.absolutePath}")
            }
            
            // Create calibration folder
            val calibrationFolder = File(sessionFolder, CALIBRATION_FOLDER)
            if (!calibrationFolder.exists() && !calibrationFolder.mkdirs()) {
                logger.warning("Failed to create calibration folder: ${calibrationFolder.absolutePath}")
            }
        }

        /**
         * Writes session information to a file
         */
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

        /**
         * Writes session configuration including thermal settings
         */
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

        /**
         * Logs a summary of the completed session
         */
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

        /**
         * Gets available storage space in bytes
         */
        fun getAvailableStorageSpace(): Long =
            try {
                val baseFolder = getBaseRecordingFolder()
                baseFolder.freeSpace
            } catch (e: Exception) {
                logger.error("Failed to get available storage space", e)
                0L
            }

        /**
         * Checks if there's sufficient storage space for recording
         */
        fun hasSufficientStorage(requiredSpaceBytes: Long = 1024 * 1024 * 1024): Boolean { // Default 1GB
            return getAvailableStorageSpace() > requiredSpaceBytes
        }

        /**
         * Get all recorded sessions by scanning the recording directory
         * Returns a list of SessionInfo objects reconstructed from session folders
         */
        suspend fun getAllSessions(): List<com.multisensor.recording.recording.SessionInfo> =
            withContext(Dispatchers.IO) {
                return@withContext try {
                    val baseFolder = getBaseRecordingFolder()
                    val sessions = mutableListOf<com.multisensor.recording.recording.SessionInfo>()

                    if (!baseFolder.exists()) {
                        logger.info("Base recording folder does not exist")
                        return@withContext emptyList()
                    }

                    // Scan all subdirectories for session folders
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

                    // Sort sessions by start time (newest first)
                    sessions.sortedByDescending { it.startTime }
                } catch (e: Exception) {
                    logger.error("Failed to get all sessions", e)
                    emptyList()
                }
            }

        /**
         * Reconstruct SessionInfo from a session folder
         */
        private fun reconstructSessionInfo(sessionFolder: File): com.multisensor.recording.recording.SessionInfo? =
            try {
                val sessionId = sessionFolder.name

                // Try to read session info file first
                val infoFile = File(sessionFolder, SESSION_INFO_FILE)
                var startTime = sessionFolder.lastModified() // Fallback to folder creation time
                var endTime = 0L
                var errorOccurred = false
                var errorMessage: String? = null

                if (infoFile.exists()) {
                    try {
                        val infoContent = infoFile.readText()
                        // Parse session info file for more accurate data
                        infoContent.lines().forEach { line ->
                            when {
                                line.startsWith("Start Time:") -> {
                                    // Extract timestamp from date string if possible
                                    // For now, use folder modification time as fallback
                                }
                                line.startsWith("End Time:") -> {
                                    // Extract end time if available
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

                // Check for file existence and determine what was recorded
                val rgbVideoFile = File(sessionFolder, RGB_VIDEO_FILE)
                val thermalVideoFile = File(sessionFolder, THERMAL_VIDEO_FILE)
                val rawFramesFolder = File(sessionFolder, RAW_FRAMES_FOLDER)
                val shimmerDataFile = File(sessionFolder, SHIMMER_DATA_FILE)

                val videoEnabled = rgbVideoFile.exists() && rgbVideoFile.length() > 0
                val thermalEnabled = thermalVideoFile.exists() && thermalVideoFile.length() > 0
                val rawEnabled = rawFramesFolder.exists() && (rawFramesFolder.listFiles()?.isNotEmpty() == true)

                // Create SessionInfo object
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

                // Add RAW file paths if they exist
                if (rawEnabled) {
                    rawFramesFolder.listFiles()?.forEach { rawFile ->
                        if (rawFile.isFile && rawFile.name.endsWith(".dng")) {
                            sessionInfo.addRawFile(rawFile.absolutePath)
                        }
                    }
                }

                // Estimate thermal frame count if thermal file exists
                if (thermalEnabled) {
                    val thermalFileSize = thermalVideoFile.length()
                    val estimatedFrameCount = thermalFileSize / (256 * 192 * 2 + 8) // Rough estimate
                    sessionInfo.updateThermalFrameCount(estimatedFrameCount)
                }

                // Mark as completed if I have an end time
                if (endTime > 0) {
                    sessionInfo.markCompleted()
                }

                logger.debug("Reconstructed session: ${sessionInfo.getSummary()}")
                sessionInfo
            } catch (e: Exception) {
                logger.error("Failed to reconstruct session info from folder: ${sessionFolder.name}", e)
                null
            }

        /**
         * Delete all recorded sessions and their data
         * WARNING: This permanently removes all recording data
         */
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

                    // Delete all session folders
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

                    // Return true if I deleted at least some sessions and had no failures
                    deletedCount > 0 && failedCount == 0
                } catch (e: Exception) {
                    logger.error("Failed to delete all sessions", e)
                    false
                }
            }

        /**
         * Recursively delete a session folder and all its contents
         */
        private fun deleteSessionFolder(folder: File): Boolean =
            try {
                if (folder.isDirectory) {
                    // Delete all files and subdirectories first
                    folder.listFiles()?.forEach { file ->
                        if (file.isDirectory) {
                            deleteSessionFolder(file)
                        } else {
                            file.delete()
                        }
                    }
                }
                // Delete the folder itself
                folder.delete()
            } catch (e: Exception) {
                logger.error("Failed to delete folder: ${folder.absolutePath}", e)
                false
            }
    }
