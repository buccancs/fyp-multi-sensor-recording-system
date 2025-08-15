package com.multisensor.recording.session

import android.content.Context
import android.os.Environment
import android.util.Log
import com.multisensor.recording.util.Logger
import org.json.JSONObject
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

/**
 * FR4: Session Management - Organizes recordings into sessions with unique IDs
 * Handles session metadata, directory creation, and session lifecycle
 */
class SessionManager(private val context: Context) {
    
    companion object {
        private const val TAG = "SessionManager"
        private const val SESSION_METADATA_FILE = "session_metadata.json"
        private const val SESSIONS_BASE_DIR = "multi_sensor_sessions"
        private val DATE_FORMAT = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault())
    }

    // Session state
    private val isSessionActive = AtomicBoolean(false)
    private val currentSession = AtomicReference<SessionInfo?>(null)
    private val sessionsBaseDir: File
    
    init {
        // Initialize sessions directory
        sessionsBaseDir = File(context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), SESSIONS_BASE_DIR)
        if (!sessionsBaseDir.exists()) {
            sessionsBaseDir.mkdirs()
            Logger.d(TAG, "Created sessions base directory: ${sessionsBaseDir.absolutePath}")
        }
    }

    /**
     * Create a new recording session with unique ID
     * @param participantId Optional participant identifier
     * @return SessionInfo if successful, null if session already active
     */
    fun createSession(participantId: String? = null): SessionInfo? {
        if (isSessionActive.get()) {
            Logger.w(TAG, "Cannot create session - session already active")
            return null
        }

        val timestamp = System.currentTimeMillis()
        val sessionId = generateSessionId(timestamp)
        val sessionDir = File(sessionsBaseDir, sessionId)
        
        if (!sessionDir.exists()) {
            sessionDir.mkdirs()
        }

        val sessionInfo = SessionInfo(
            sessionId = sessionId,
            participantId = participantId,
            startTime = timestamp,
            sessionDirectory = sessionDir,
            status = SessionStatus.CREATED
        )

        // Save initial metadata
        saveSessionMetadata(sessionInfo)
        
        currentSession.set(sessionInfo)
        Logger.i(TAG, "Created session: $sessionId in ${sessionDir.absolutePath}")
        
        return sessionInfo
    }

    /**
     * Start the current session (begin recording)
     */
    fun startSession(): Boolean {
        val session = currentSession.get() ?: run {
            Logger.w(TAG, "No session to start")
            return false
        }

        if (isSessionActive.get()) {
            Logger.w(TAG, "Session already active")
            return false
        }

        session.status = SessionStatus.RECORDING
        session.recordingStartTime = System.currentTimeMillis()
        isSessionActive.set(true)
        
        // Update metadata
        saveSessionMetadata(session)
        
        Logger.i(TAG, "Started session: ${session.sessionId}")
        return true
    }

    /**
     * Stop the current session
     */
    fun stopSession(): Boolean {
        val session = currentSession.get() ?: run {
            Logger.w(TAG, "No session to stop")
            return false
        }

        if (!isSessionActive.get()) {
            Logger.w(TAG, "No active session to stop")
            return false
        }

        session.status = SessionStatus.COMPLETED
        session.endTime = System.currentTimeMillis()
        session.duration = session.endTime!! - (session.recordingStartTime ?: session.startTime)
        isSessionActive.set(false)
        
        // Final metadata save
        saveSessionMetadata(session)
        
        Logger.i(TAG, "Stopped session: ${session.sessionId}, duration: ${session.duration}ms")
        return true
    }

    /**
     * Terminate session with error
     */
    fun terminateSession(errorMessage: String? = null): Boolean {
        val session = currentSession.get() ?: return false
        
        session.status = SessionStatus.ERROR
        session.endTime = System.currentTimeMillis()
        session.duration = session.endTime!! - (session.recordingStartTime ?: session.startTime)
        session.errorMessage = errorMessage
        isSessionActive.set(false)
        
        saveSessionMetadata(session)
        
        Logger.e(TAG, "Terminated session: ${session.sessionId}, error: $errorMessage")
        return true
    }

    /**
     * Add recorded file to current session
     */
    fun addRecordedFile(fileType: String, filePath: String, fileSize: Long = 0L): Boolean {
        val session = currentSession.get() ?: return false
        
        val fileInfo = RecordedFile(
            type = fileType,
            path = filePath,
            size = fileSize,
            timestamp = System.currentTimeMillis()
        )
        
        session.recordedFiles.add(fileInfo)
        saveSessionMetadata(session)
        
        Logger.d(TAG, "Added file to session ${session.sessionId}: $fileType -> $filePath")
        return true
    }

    /**
     * Get current session info
     */
    fun getCurrentSession(): SessionInfo? = currentSession.get()

    /**
     * Check if session is currently active
     */
    fun isActive(): Boolean = isSessionActive.get()

    /**
     * Get session directory for file storage
     */
    fun getSessionDirectory(): File? = currentSession.get()?.sessionDirectory

    /**
     * Generate unique session ID based on timestamp
     */
    private fun generateSessionId(timestamp: Long): String {
        return "session_${DATE_FORMAT.format(Date(timestamp))}"
    }

    /**
     * Save session metadata to JSON file
     */
    private fun saveSessionMetadata(session: SessionInfo) {
        val metadataFile = File(session.sessionDirectory, SESSION_METADATA_FILE)
        
        try {
            val json = JSONObject().apply {
                put("sessionId", session.sessionId)
                put("participantId", session.participantId)
                put("startTime", session.startTime)
                put("recordingStartTime", session.recordingStartTime)
                put("endTime", session.endTime)
                put("duration", session.duration)
                put("status", session.status.name)
                put("errorMessage", session.errorMessage)
                put("deviceInfo", JSONObject().apply {
                    put("deviceId", android.os.Build.MODEL)
                    put("androidVersion", android.os.Build.VERSION.RELEASE)
                    put("appVersion", "1.0")
                })
                
                // Recorded files
                val filesArray = org.json.JSONArray()
                session.recordedFiles.forEach { file ->
                    filesArray.put(JSONObject().apply {
                        put("type", file.type)
                        put("path", file.path)
                        put("size", file.size)
                        put("timestamp", file.timestamp)
                    })
                }
                put("recordedFiles", filesArray)
            }
            
            FileWriter(metadataFile).use { writer ->
                writer.write(json.toString(2))
            }
            
            Logger.d(TAG, "Saved session metadata: ${metadataFile.absolutePath}")
            
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to save session metadata", e)
        }
    }

    /**
     * List all previous sessions
     */
    fun listSessions(): List<String> {
        return sessionsBaseDir.listFiles()?.filter { it.isDirectory }?.map { it.name } ?: emptyList()
    }
}

/**
 * Session information data class
 */
data class SessionInfo(
    val sessionId: String,
    val participantId: String?,
    val startTime: Long,
    val sessionDirectory: File,
    var status: SessionStatus,
    var recordingStartTime: Long? = null,
    var endTime: Long? = null,
    var duration: Long = 0L,
    var errorMessage: String? = null,
    val recordedFiles: MutableList<RecordedFile> = mutableListOf()
)

/**
 * Recorded file information
 */
data class RecordedFile(
    val type: String,
    val path: String,
    val size: Long,
    val timestamp: Long
)

/**
 * Session status enumeration
 */
enum class SessionStatus {
    CREATED,
    RECORDING,
    COMPLETED,
    ERROR
}