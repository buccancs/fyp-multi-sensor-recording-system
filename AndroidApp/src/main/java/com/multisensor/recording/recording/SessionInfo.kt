package com.multisensor.recording.recording

/**
 * Comprehensive session information tracking for CameraRecorder sessions.
 * Tracks file outputs, timestamps, configuration flags, and session metadata.
 * 
 * Based on Milestone 2.2 specification for enhanced session management.
 */
data class SessionInfo(
    val sessionId: String,
    var videoEnabled: Boolean = false,
    var rawEnabled: Boolean = false,
    var startTime: Long = 0L,
    var endTime: Long = 0L,
    var videoFilePath: String? = null,
    val rawFilePaths: MutableList<String> = mutableListOf(),
    var cameraId: String? = null,
    var videoResolution: String? = null,
    var rawResolution: String? = null,
    var errorOccurred: Boolean = false,
    var errorMessage: String? = null
) {
    
    /**
     * Get session duration in milliseconds
     */
    fun getDurationMs(): Long {
        return if (endTime > startTime) endTime - startTime else 0L
    }
    
    /**
     * Get number of RAW images captured
     */
    fun getRawImageCount(): Int = rawFilePaths.size
    
    /**
     * Check if session is currently active
     */
    fun isActive(): Boolean = startTime > 0L && endTime == 0L
    
    /**
     * Mark session as completed
     */
    fun markCompleted() {
        if (endTime == 0L) {
            endTime = System.currentTimeMillis()
        }
    }
    
    /**
     * Add a RAW file path to the session
     */
    fun addRawFile(filePath: String) {
        rawFilePaths.add(filePath)
    }
    
    /**
     * Mark session as having an error
     */
    fun markError(message: String) {
        errorOccurred = true
        errorMessage = message
    }
    
    /**
     * Get summary string for logging
     */
    fun getSummary(): String {
        return buildString {
            append("SessionInfo[")
            append("id=$sessionId, ")
            append("duration=${getDurationMs()}ms, ")
            append("video=${if (videoEnabled) "enabled" else "disabled"}, ")
            append("raw=${if (rawEnabled) "enabled (${getRawImageCount()} files)" else "disabled"}, ")
            if (errorOccurred) append("ERROR: $errorMessage, ")
            append("active=${isActive()}")
            append("]")
        }
    }
}