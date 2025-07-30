package com.multisensor.recording.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

/**
 * ViewModel for FileViewActivity that manages UI state and coordinates
 * file browsing, session management, and file operations.
 * 
 * Follows MVVM pattern with centralized StateFlow-based UI state management.
 */
@HiltViewModel
class FileViewViewModel @Inject constructor(
    private val sessionManager: SessionManager,
    private val logger: Logger
) : ViewModel() {

    private val _uiState = MutableStateFlow(FileViewUiState())
    val uiState: StateFlow<FileViewUiState> = _uiState.asStateFlow()

    init {
        logger.info("FileViewViewModel initialized")
        loadInitialData()
    }

    /**
     * Load initial data when ViewModel is created
     */
    fun loadInitialData() {
        loadSessions()
    }

    /**
     * Load all recording sessions
     */
    fun loadSessions() {
        viewModelScope.launch {
            try {
                updateUiState { currentState ->
                    currentState.copy(isLoadingSessions = true, errorMessage = null)
                }

                val sessionInfos = sessionManager.getAllSessions()
                val sessionItems = sessionInfos.map { sessionInfo ->
                    convertToSessionItem(sessionInfo)
                }
                
                logger.info("Loaded ${sessionItems.size} sessions")

                updateUiState { currentState ->
                    currentState.copy(
                        isLoadingSessions = false,
                        sessions = sessionItems,
                        filteredSessions = sessionItems,
                        showEmptyState = sessionItems.isEmpty()
                    )
                }
            } catch (e: Exception) {
                logger.error("Failed to load sessions", e)
                updateUiState { currentState ->
                    currentState.copy(
                        isLoadingSessions = false,
                        errorMessage = "Failed to load sessions: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Convert SessionInfo to SessionItem
     */
    private fun convertToSessionItem(sessionInfo: SessionInfo): SessionItem {
        val deviceTypes = mutableListOf<String>()
        if (sessionInfo.videoEnabled) deviceTypes.add("camera")
        if (sessionInfo.thermalEnabled) deviceTypes.add("thermal")
        if (sessionInfo.rawEnabled) deviceTypes.add("raw")

        val status = when {
            sessionInfo.errorOccurred -> SessionStatus.CORRUPTED
            sessionInfo.isActive() -> SessionStatus.PROCESSING
            else -> SessionStatus.COMPLETED
        }

        val fileCount = (if (sessionInfo.videoFilePath != null) 1 else 0) +
                       sessionInfo.rawFilePaths.size +
                       (if (sessionInfo.thermalFilePath != null) 1 else 0)

        return SessionItem(
            sessionId = sessionInfo.sessionId,
            name = sessionInfo.sessionId, // Use sessionId as name for now
            startTime = sessionInfo.startTime,
            endTime = sessionInfo.endTime,
            duration = sessionInfo.getDurationMs(),
            fileCount = fileCount,
            totalSize = calculateSessionSize(sessionInfo),
            deviceTypes = deviceTypes,
            status = status
        )
    }

    /**
     * Calculate total size of session files
     */
    private fun calculateSessionSize(sessionInfo: SessionInfo): Long {
        var totalSize = 0L
        
        sessionInfo.videoFilePath?.let { path ->
            val file = File(path)
            if (file.exists()) totalSize += file.length()
        }
        
        sessionInfo.thermalFilePath?.let { path ->
            val file = File(path)
            if (file.exists()) totalSize += file.length()
        }
        
        sessionInfo.rawFilePaths.forEach { path ->
            val file = File(path)
            if (file.exists()) totalSize += file.length()
        }
        
        return totalSize
    }

    /**
     * Refresh sessions list
     */
    fun refreshSessions() {
        loadSessions()
    }

    /**
     * Select a session by index and load its files
     */
    fun selectSession(sessionItem: SessionItem) {
        val sessionIndex = _uiState.value.sessions.indexOf(sessionItem)
        if (sessionIndex >= 0) {
            updateUiState { currentState ->
                currentState.copy(selectedSessionIndex = sessionIndex)
            }
            loadSessionFiles(sessionItem)
        }
    }

    /**
     * Load files for the selected session
     */
    private fun loadSessionFiles(sessionItem: SessionItem) {
        viewModelScope.launch {
            try {
                updateUiState { currentState ->
                    currentState.copy(isLoadingFiles = true)
                }

                // Find the original SessionInfo to get file paths
                val sessionInfos = sessionManager.getAllSessions()
                val sessionInfo = sessionInfos.find { it.sessionId == sessionItem.sessionId }
                
                if (sessionInfo == null) {
                    updateUiState { currentState ->
                        currentState.copy(
                            isLoadingFiles = false,
                            errorMessage = "Session not found"
                        )
                    }
                    return@launch
                }

                val files = mutableListOf<FileItem>()
                
                // Add video file if exists
                sessionInfo.videoFilePath?.let { videoPath ->
                    val videoFile = File(videoPath)
                    if (videoFile.exists()) {
                        files.add(
                            FileItem(
                                file = videoFile,
                                type = FileType.VIDEO,
                                sessionId = sessionInfo.sessionId,
                                metadata = "Video recording"
                            )
                        )
                    }
                }
                
                // Add thermal file if exists
                sessionInfo.thermalFilePath?.let { thermalPath ->
                    val thermalFile = File(thermalPath)
                    if (thermalFile.exists()) {
                        files.add(
                            FileItem(
                                file = thermalFile,
                                type = FileType.THERMAL_DATA,
                                sessionId = sessionInfo.sessionId,
                                metadata = "Thermal data"
                            )
                        )
                    }
                }
                
                // Add RAW files
                sessionInfo.rawFilePaths.forEach { rawPath ->
                    val rawFile = File(rawPath)
                    if (rawFile.exists()) {
                        files.add(
                            FileItem(
                                file = rawFile,
                                type = FileType.RAW_IMAGE,
                                sessionId = sessionInfo.sessionId,
                                metadata = "RAW image"
                            )
                        )
                    }
                }

                files.sortByDescending { it.file.lastModified() }

                updateUiState { currentState ->
                    currentState.copy(
                        isLoadingFiles = false,
                        sessionFiles = files
                    )
                }

                logger.info("Loaded ${files.size} files for session ${sessionInfo.sessionId}")
            } catch (e: Exception) {
                logger.error("Failed to load session files", e)
                updateUiState { currentState ->
                    currentState.copy(
                        isLoadingFiles = false,
                        errorMessage = "Failed to load files: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Filter sessions based on search query
     */
    fun onSearchQueryChanged(query: String) {
        val currentState = _uiState.value
        val filteredSessions = if (query.isBlank()) {
            currentState.sessions
        } else {
            currentState.sessions.filter { session ->
                session.sessionId.contains(query, ignoreCase = true) ||
                session.name.contains(query, ignoreCase = true) ||
                session.deviceTypes.any { it.contains(query, ignoreCase = true) }
            }
        }

        updateUiState { currentState ->
            currentState.copy(
                searchQuery = query,
                filteredSessions = filteredSessions,
                showEmptyState = filteredSessions.isEmpty()
            )
        }
    }

    /**
     * Apply filter to sessions
     */
    fun applyFilter(filterIndex: Int) {
        val currentState = _uiState.value
        val filteredSessions = when (filterIndex) {
            0 -> currentState.sessions // All sessions
            1 -> currentState.sessions.filter { it.duration > 0 } // Sessions with recordings
            2 -> currentState.sessions.sortedByDescending { it.startTime } // Recent first
            else -> currentState.sessions
        }

        updateUiState { currentState ->
            currentState.copy(
                filteredSessions = filteredSessions,
                showEmptyState = filteredSessions.isEmpty()
            )
        }
    }

    /**
     * Delete a specific file
     */
    fun deleteFile(fileItem: FileItem) {
        viewModelScope.launch {
            try {
                if (fileItem.file.exists() && fileItem.file.delete()) {
                    logger.info("Deleted file: ${fileItem.file.name}")
                    
                    // Refresh the current session's files
                    _uiState.value.selectedSession?.let { session ->
                        loadSessionFiles(session)
                    }
                    
                    updateUiState { currentState ->
                        currentState.copy(successMessage = "File deleted successfully")
                    }
                } else {
                    updateUiState { currentState ->
                        currentState.copy(errorMessage = "Failed to delete file")
                    }
                }
            } catch (e: Exception) {
                logger.error("Error deleting file", e)
                updateUiState { currentState ->
                    currentState.copy(errorMessage = "Error deleting file: ${e.message}")
                }
            }
        }
    }

    /**
     * Delete all sessions
     */
    fun deleteAllSessions() {
        viewModelScope.launch {
            try {
                updateUiState { currentState ->
                    currentState.copy(isLoadingSessions = true)
                }

                sessionManager.deleteAllSessions()
                logger.info("All sessions deleted")

                updateUiState { currentState ->
                    currentState.copy(
                        isLoadingSessions = false,
                        sessions = emptyList(),
                        filteredSessions = emptyList(),
                        sessionFiles = emptyList(),
                        selectedSessionIndex = -1,
                        showEmptyState = true,
                        successMessage = "All sessions deleted successfully"
                    )
                }
            } catch (e: Exception) {
                logger.error("Failed to delete all sessions", e)
                updateUiState { currentState ->
                    currentState.copy(
                        isLoadingSessions = false,
                        errorMessage = "Failed to delete sessions: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Clear error message
     */
    fun clearError() {
        updateUiState { currentState ->
            currentState.copy(errorMessage = null)
        }
    }

    /**
     * Clear success message
     */
    fun clearSuccess() {
        updateUiState { currentState ->
            currentState.copy(successMessage = null)
        }
    }

    /**
     * Thread-safe state update helper
     */
    private fun updateUiState(update: (FileViewUiState) -> FileViewUiState) {
        _uiState.value = update(_uiState.value)
    }

    override fun onCleared() {
        super.onCleared()
        logger.info("FileViewViewModel cleared")
    }
}