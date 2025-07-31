package com.multisensor.recording.recording

/**
 * session info for multi-sensor recording
 */
data class SessionInfo(
    val sessionId: String,
    var videoEnabled: Boolean = false,
    var rawEnabled: Boolean = false,
    var thermalEnabled: Boolean = false,
    var startTime: Long = 0L,
    var endTime: Long = 0L,
    var videoFilePath: String? = null,
    val rawFilePaths: MutableList<String> = mutableListOf(),
    var thermalFilePath: String? = null,
    var cameraId: String? = null,
    var videoResolution: String? = null,
    var rawResolution: String? = null,
    var thermalResolution: String? = null,
    var thermalFrameCount: Long = 0L,
    var errorOccurred: Boolean = false,
    var errorMessage: String? = null,
) {
    /**
     * get session duration in milliseconds
     */
    fun getDurationMs(): Long = if (endTime > startTime) endTime - startTime else 0L

    /**
     * get number of raw images captured
     */
    fun getRawImageCount(): Int = rawFilePaths.size

    /**
     * check if session is currently active
     */
    fun isActive(): Boolean = startTime > 0L && endTime == 0L

    /**
     * mark session as completed
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
     * Set thermal file path for the session
     */
    fun setThermalFile(filePath: String) {
        thermalFilePath = filePath
    }

    /**
     * Update thermal frame count
     */
    fun updateThermalFrameCount(count: Long) {
        thermalFrameCount = count
    }

    /**
     * Check if thermal recording is active
     */
    fun isThermalActive(): Boolean = thermalEnabled && thermalFilePath != null

    /**
     * Get thermal data size estimate in MB (based on frame count)
     */
    fun getThermalDataSizeMB(): Double {
        // Each frame is approximately 98KB (256x192x2 bytes)
        val bytesPerFrame = 256 * 192 * 2 + 8 // +8 for timestamp
        return (thermalFrameCount * bytesPerFrame) / (1024.0 * 1024.0)
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
    fun getSummary(): String =
        buildString {
            append("SessionInfo[")
            append("id=$sessionId, ")
            append("duration=${getDurationMs()}ms, ")
            append("video=${if (videoEnabled) "enabled" else "disabled"}, ")
            append("raw=${if (rawEnabled) "enabled (${getRawImageCount()} files)" else "disabled"}, ")
            append(
                "thermal=${if (thermalEnabled) {
                    "enabled ($thermalFrameCount frames, ${String.format(
                        "%.1f",
                        getThermalDataSizeMB(),
                    )}MB)"
                } else {
                    "disabled"
                }}, ",
            )
            if (errorOccurred) append("ERROR: $errorMessage, ")
            append("active=${isActive()}")
            append("]")
        }
}
