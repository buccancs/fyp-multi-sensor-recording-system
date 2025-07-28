package com.multisensor.recording.service

import android.content.Context
import android.os.Environment
import com.multisensor.recording.util.Logger
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
class SessionManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {
    
    private var currentSession: RecordingSession? = null
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.getDefault())
    
    companion object {
        private const val BASE_FOLDER_NAME = "MultiSensorRecording"
        private const val SESSION_INFO_FILE = "session_info.txt"
        private const val RGB_VIDEO_FILE = "rgb_video.mp4"
        private const val THERMAL_VIDEO_FILE = "thermal_video.mp4"
        private const val RAW_FRAMES_FOLDER = "raw_frames"
        private const val SHIMMER_DATA_FILE = "shimmer_data.csv"
        private const val LOG_FILE = "session_log.txt"
    }
    
    /**
     * Data class representing a recording session
     */
    data class RecordingSession(
        val sessionId: String,
        val startTime: Long,
        val sessionFolder: File,
        var endTime: Long? = null,
        var status: SessionStatus = SessionStatus.ACTIVE
    )
    
    enum class SessionStatus {
        ACTIVE,
        COMPLETED,
        FAILED,
        CANCELLED
    }
    
    /**
     * Creates a new recording session with organized folder structure
     */
    suspend fun createNewSession(): String = withContext(Dispatchers.IO) {
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
            val session = RecordingSession(
                sessionId = sessionId,
                startTime = System.currentTimeMillis(),
                sessionFolder = sessionFolder
            )
            
            currentSession = session
            
            // Write session info file
            writeSessionInfo(session)
            
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
    suspend fun finalizeCurrentSession() = withContext(Dispatchers.IO) {
        currentSession?.let { session ->
            try {
                logger.info("Finalizing session: ${session.sessionId}")
                
                session.endTime = System.currentTimeMillis()
                session.status = SessionStatus.COMPLETED
                
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
     * Gets file paths for different data types in the current session
     */
    fun getSessionFilePaths(): SessionFilePaths? {
        return currentSession?.let { session ->
            SessionFilePaths(
                sessionFolder = session.sessionFolder,
                rgbVideoFile = File(session.sessionFolder, RGB_VIDEO_FILE),
                thermalVideoFile = File(session.sessionFolder, THERMAL_VIDEO_FILE),
                rawFramesFolder = File(session.sessionFolder, RAW_FRAMES_FOLDER),
                shimmerDataFile = File(session.sessionFolder, SHIMMER_DATA_FILE),
                logFile = File(session.sessionFolder, LOG_FILE)
            )
        }
    }
    
    /**
     * Data class containing file paths for a session
     */
    data class SessionFilePaths(
        val sessionFolder: File,
        val rgbVideoFile: File,
        val thermalVideoFile: File,
        val rawFramesFolder: File,
        val shimmerDataFile: File,
        val logFile: File
    )
    
    /**
     * Gets the base recording folder, creating it if necessary
     */
    private fun getBaseRecordingFolder(): File {
        // Use external storage if available, otherwise use internal storage
        val baseDir = if (Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED) {
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
        val rawFramesFolder = File(sessionFolder, RAW_FRAMES_FOLDER)
        if (!rawFramesFolder.exists() && !rawFramesFolder.mkdirs()) {
            logger.warning("Failed to create raw frames folder: ${rawFramesFolder.absolutePath}")
        }
    }
    
    /**
     * Writes session information to a file
     */
    private fun writeSessionInfo(session: RecordingSession) {
        try {
            val infoFile = File(session.sessionFolder, SESSION_INFO_FILE)
            val duration = session.endTime?.let { it - session.startTime } ?: 0
            
            val info = buildString {
                appendLine("Session ID: ${session.sessionId}")
                appendLine("Start Time: ${Date(session.startTime)}")
                session.endTime?.let { 
                    appendLine("End Time: ${Date(it)}")
                    appendLine("Duration: ${duration / 1000} seconds")
                }
                appendLine("Status: ${session.status}")
                appendLine("Session Folder: ${session.sessionFolder.absolutePath}")
                appendLine("Created: ${Date()}")
            }
            
            infoFile.writeText(info)
            
        } catch (e: Exception) {
            logger.error("Failed to write session info", e)
        }
    }
    
    /**
     * Logs a summary of the completed session
     */
    private fun logSessionSummary(session: RecordingSession) {
        try {
            val duration = session.endTime?.let { it - session.startTime } ?: 0
            val filePaths = SessionFilePaths(
                sessionFolder = session.sessionFolder,
                rgbVideoFile = File(session.sessionFolder, RGB_VIDEO_FILE),
                thermalVideoFile = File(session.sessionFolder, THERMAL_VIDEO_FILE),
                rawFramesFolder = File(session.sessionFolder, RAW_FRAMES_FOLDER),
                shimmerDataFile = File(session.sessionFolder, SHIMMER_DATA_FILE),
                logFile = File(session.sessionFolder, LOG_FILE)
            )
            
            logger.info("Session Summary:")
            logger.info("  Session ID: ${session.sessionId}")
            logger.info("  Duration: ${duration / 1000} seconds")
            logger.info("  RGB Video: ${if (filePaths.rgbVideoFile.exists()) "✓" else "✗"} (${filePaths.rgbVideoFile.length()} bytes)")
            logger.info("  Thermal Video: ${if (filePaths.thermalVideoFile.exists()) "✓" else "✗"} (${filePaths.thermalVideoFile.length()} bytes)")
            logger.info("  Raw Frames: ${filePaths.rawFramesFolder.listFiles()?.size ?: 0} files")
            logger.info("  Shimmer Data: ${if (filePaths.shimmerDataFile.exists()) "✓" else "✗"} (${filePaths.shimmerDataFile.length()} bytes)")
            logger.info("  Session Folder: ${session.sessionFolder.absolutePath}")
            
        } catch (e: Exception) {
            logger.error("Failed to log session summary", e)
        }
    }
    
    /**
     * Gets available storage space in bytes
     */
    fun getAvailableStorageSpace(): Long {
        return try {
            val baseFolder = getBaseRecordingFolder()
            baseFolder.freeSpace
        } catch (e: Exception) {
            logger.error("Failed to get available storage space", e)
            0L
        }
    }
    
    /**
     * Checks if there's sufficient storage space for recording
     */
    fun hasSufficientStorage(requiredSpaceBytes: Long = 1024 * 1024 * 1024): Boolean { // Default 1GB
        return getAvailableStorageSpace() > requiredSpaceBytes
    }
}