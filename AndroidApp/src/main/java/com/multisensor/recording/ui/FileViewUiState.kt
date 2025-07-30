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
    
    // Search and Filter State
    val searchQuery: String = "",
    val selectedFilter: FileFilter = FileFilter.ALL,
    val filteredSessions: List<SessionItem> = emptyList(),
    
    // UI Display State
    val showEmptyState: Boolean = false,
    val showSessionInfo: Boolean = false,
    val showFilesList: Boolean = false,
    
    // Loading States
    val isLoadingSessions: Boolean = false,
    val isLoadingFiles: Boolean = false,
    val isRefreshing: Boolean = false,
    
    // Selection and Actions
    val selectedFileIndices: Set<Int> = emptySet(),
    val showFileActions: Boolean = false,
    val showDeleteConfirmation: Boolean = false,
    
    // Error Handling
    val errorMessage: String? = null,
    val showErrorDialog: Boolean = false,
    
    // Storage Information
    val totalStorageUsed: Long = 0L,
    val availableStorage: Long = 0L,
    val storageWarningThreshold: Float = 0.8f,
    
    // Sort Options
    val sortBy: SortOption = SortOption.DATE_DESC,
    val showSortMenu: Boolean = false
) {
    
    /**
     * Computed property for the currently selected session
     */
    val selectedSession: SessionItem?
        get() = if (selectedSessionIndex >= 0 && selectedSessionIndex < sessions.size) {
            sessions[selectedSessionIndex]
        } else null
    
    /**
     * Computed property to determine if files can be deleted
     */
    val canDeleteFiles: Boolean
        get() = selectedFileIndices.isNotEmpty() && !isLoadingFiles
    
    /**
     * Computed property to determine if session can be deleted
     */
    val canDeleteSession: Boolean
        get() = selectedSession != null && !isLoadingSessions
    
    /**
     * Computed property to determine if files can be shared
     */
    val canShareFiles: Boolean
        get() = selectedFileIndices.isNotEmpty() && !isLoadingFiles
    
    /**
     * Computed property for storage usage percentage
     */
    val storageUsagePercentage: Float
        get() = if (totalStorageUsed + availableStorage > 0) {
            totalStorageUsed.toFloat() / (totalStorageUsed + availableStorage)
        } else 0f
    
    /**
     * Computed property to determine if storage warning should be shown
     */
    val showStorageWarning: Boolean
        get() = storageUsagePercentage > storageWarningThreshold
    
    /**
     * Computed property for total file count across all sessions
     */
    val totalFileCount: Int
        get() = sessions.sumOf { it.fileCount }
    
    /**
     * Computed property for selected files count
     */
    val selectedFilesCount: Int
        get() = selectedFileIndices.size
    
    /**
     * Get selected files from the current session
     */
    val selectedFiles: List<FileItem>
        get() = selectedFileIndices.mapNotNull { index ->
            if (index < sessionFiles.size) sessionFiles[index] else null
        }
    
    /**
     * Computed property for search results count
     */
    val searchResultsCount: Int
        get() = if (searchQuery.isNotEmpty()) filteredSessions.size else sessions.size
}

/**
 * Represents a recording session
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
    val status: SessionStatus,
    val thumbnailPath: String? = null
) {
    /**
     * Computed property for human-readable duration
     */
    val formattedDuration: String
        get() {
            val hours = duration / 3600000
            val minutes = (duration % 3600000) / 60000
            val seconds = (duration % 60000) / 1000
            return when {
                hours > 0 -> "${hours}h ${minutes}m ${seconds}s"
                minutes > 0 -> "${minutes}m ${seconds}s"
                else -> "${seconds}s"
            }
        }
    
    /**
     * Computed property for human-readable file size
     */
    val formattedSize: String
        get() = formatFileSize(totalSize)
}

/**
 * Data class representing a file item in the browser.
 * This is the single source of truth, moved from FileViewActivity.
 */
data class FileItem(
    val file: File,
    val type: FileType,
    val sessionId: String,
    val metadata: String = "",
)

/**
 * Session status enumeration
 */
enum class SessionStatus {
    COMPLETED,
    INTERRUPTED,
    CORRUPTED,
    PROCESSING
}

/**
 * Enum representing different file types.
 * This is the single source of truth, moved from FileViewActivity.
 */
enum class FileType(
    val displayName: String,
) {
    VIDEO("Video"),
    RAW_IMAGE("RAW Image"),
    THERMAL_DATA("Thermal Data"),
}

/**
 * File filter options
 */
enum class FileFilter(val displayName: String) {
    ALL("All Files"),
    VIDEO("Video Files"),
    AUDIO("Audio Files"),
    SENSOR_DATA("Sensor Data"),
    THERMAL("Thermal Data"),
    RECENT("Recent"),
    LARGE_FILES("Large Files")
}

/**
 * Sort options for sessions and files
 */
enum class SortOption(val displayName: String) {
    DATE_DESC("Newest First"),
    DATE_ASC("Oldest First"),
    NAME_ASC("Name A-Z"),
    NAME_DESC("Name Z-A"),
    SIZE_DESC("Largest First"),
    SIZE_ASC("Smallest First"),
    DURATION_DESC("Longest First"),
    DURATION_ASC("Shortest First")
}

/**
 * Helper function to format file sizes
 */
private fun formatFileSize(bytes: Long): String {
    val units = arrayOf("B", "KB", "MB", "GB", "TB")
    var size = bytes.toDouble()
    var unitIndex = 0
    
    while (size >= 1024 && unitIndex < units.size - 1) {
        size /= 1024
        unitIndex++
    }
    
    return "%.1f %s".format(size, units[unitIndex])
}