package com.multisensor.recording.ui

import java.io.File

/**
 * UI State data class for FileViewActivity
 * 
 * This class represents everything the file browser UI needs to know 
 * to draw itself at any given moment. Following modern Android architecture 
 * guidelines for centralized state management.
 */
data class FileViewUiState(
    // Session Data
    val sessions: List<SessionItem> = emptyList(),
    val selectedSessionIndex: Int = -1,
    val sessionFiles: List<FileItem> = emptyList(),
    val selectedFileIndices: Set<Int> = emptySet(),
    
    // Search and Filter State
    val searchQuery: String = "",
    val filteredSessions: List<SessionItem> = emptyList(),
    
    // Storage Management
    val totalStorageUsed: Long = 0L,
    val availableStorage: Long = 0L,
    val storageWarningThreshold: Float = 0.8f,
    
    // UI Display State
    val showEmptyState: Boolean = false,
    
    // Loading States
    val isLoadingSessions: Boolean = false,
    val isLoadingFiles: Boolean = false,
    
    // Error Handling
    val errorMessage: String? = null,
    val successMessage: String? = null
) {
    /**
     * Get the currently selected session, or null if none selected
     */
    val selectedSession: SessionItem?
        get() = if (selectedSessionIndex >= 0 && selectedSessionIndex < sessions.size) {
            sessions[selectedSessionIndex]
        } else null

    /**
     * Check if files can be deleted (files selected and not loading)
     */
    val canDeleteFiles: Boolean
        get() = selectedFileIndices.isNotEmpty() && !isLoadingFiles

    /**
     * Check if session can be deleted (session selected and not loading)
     */
    val canDeleteSession: Boolean
        get() = selectedSession != null && !isLoadingSessions

    /**
     * Check if files can be shared (files selected and not loading)
     */
    val canShareFiles: Boolean
        get() = selectedFileIndices.isNotEmpty() && !isLoadingFiles

    /**
     * Calculate storage usage percentage
     */
    val storageUsagePercentage: Float
        get() {
            val totalStorage = totalStorageUsed + availableStorage
            return if (totalStorage > 0) {
                totalStorageUsed.toFloat() / totalStorage.toFloat()
            } else 0f
        }

    /**
     * Check if storage warning should be shown
     */
    val showStorageWarning: Boolean
        get() = storageUsagePercentage > storageWarningThreshold

    /**
     * Get total file count across all sessions
     */
    val totalFileCount: Int
        get() = sessions.sumOf { it.fileCount }

    /**
     * Get count of selected files
     */
    val selectedFilesCount: Int
        get() = selectedFileIndices.size

    /**
     * Get list of selected files
     */
    val selectedFiles: List<FileItem>
        get() = selectedFileIndices.mapNotNull { index ->
            if (index >= 0 && index < sessionFiles.size) {
                sessionFiles[index]
            } else null
        }

    /**
     * Get search results count
     */
    val searchResultsCount: Int
        get() = if (searchQuery.isBlank()) {
            sessions.size
        } else {
            filteredSessions.size
        }
}

/**
 * Data class representing a session item in the browser.
 */
data class SessionItem(
    val sessionId: String,
    val name: String,
    val startTime: Long,
    val endTime: Long,
    val duration: Long,
    val fileCount: Int,
    val totalSize: Long,
    val deviceTypes: List<String>,
    val status: SessionStatus
) {
    /**
     * Get formatted duration string
     */
    val formattedDuration: String
        get() {
            val seconds = duration / 1000
            val minutes = seconds / 60
            val hours = minutes / 60

            return when {
                hours > 0 -> "${hours}h ${minutes % 60}m ${seconds % 60}s"
                minutes > 0 -> "${minutes}m ${seconds % 60}s"
                else -> "${seconds}s"
            }
        }
}

/**
 * Enum representing session status.
 */
enum class SessionStatus {
    COMPLETED,
    INTERRUPTED,
    CORRUPTED,
    PROCESSING
}

/**
 * Data class representing a file item in the browser.
 */
data class FileItem(
    val file: File,
    val type: FileType,
    val sessionId: String,
    val metadata: String = ""
)

/**
 * Enum representing different file types.
 */
enum class FileType(
    val displayName: String
) {
    VIDEO("Video"),
    RAW_IMAGE("RAW Image"),
    THERMAL_DATA("Thermal Data")
}

/**
 * Extension property for File to get file extension
 */
val File.extension: String
    get() {
        val name = this.name
        val lastDot = name.lastIndexOf('.')
        return if (lastDot >= 0 && lastDot < name.length - 1) {
            name.substring(lastDot + 1)
        } else ""
    }