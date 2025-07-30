package com.multisensor.recording.ui

import java.io.File
import org.junit.Test
import org.junit.Assert.*

/**
 * Unit tests for FileViewUiState computed properties and behavior
 * 
 * These tests ensure that the file browser UI state management works correctly
 * and that computed properties return expected values for file operations and storage management.
 */
class FileViewUiStateTest {

    @Test
    fun `selectedSession returns correct session when valid index`() {
        // Given
        val sessions = listOf(
            createTestSession("session_1", "Test Session 1"),
            createTestSession("session_2", "Test Session 2")
        )
        val state = FileViewUiState(
            sessions = sessions,
            selectedSessionIndex = 1
        )

        // When & Then
        val selectedSession = state.selectedSession
        assertNotNull("[DEBUG_LOG] Selected session should not be null", selectedSession)
        assertEquals("[DEBUG_LOG] Should return second session", "session_2", selectedSession?.sessionId)
        assertEquals("[DEBUG_LOG] Session name should match", "Test Session 2", selectedSession?.name)
    }

    @Test
    fun `selectedSession returns null when invalid index`() {
        // Given
        val sessions = listOf(createTestSession("session_1", "Test Session 1"))
        val state = FileViewUiState(
            sessions = sessions,
            selectedSessionIndex = 5
        )

        // When & Then
        assertNull("[DEBUG_LOG] Selected session should be null for invalid index", state.selectedSession)
    }

    @Test
    fun `selectedSession returns null when no sessions available`() {
        // Given
        val state = FileViewUiState(
            sessions = emptyList(),
            selectedSessionIndex = 0
        )

        // When & Then
        assertNull("[DEBUG_LOG] Selected session should be null when no sessions", state.selectedSession)
    }

    @Test
    fun `canDeleteFiles returns true when files selected and not loading`() {
        // Given
        val state = FileViewUiState(
            selectedFileIndices = setOf(0, 1, 2),
            isLoadingFiles = false
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to delete files when selected", state.canDeleteFiles)
    }

    @Test
    fun `canDeleteFiles returns false when no files selected`() {
        // Given
        val state = FileViewUiState(
            selectedFileIndices = emptySet(),
            isLoadingFiles = false
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to delete files when none selected", state.canDeleteFiles)
    }

    @Test
    fun `canDeleteFiles returns false when loading files`() {
        // Given
        val state = FileViewUiState(
            selectedFileIndices = setOf(0, 1),
            isLoadingFiles = true
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to delete files when loading", state.canDeleteFiles)
    }

    @Test
    fun `canDeleteSession returns true when session selected and not loading`() {
        // Given
        val sessions = listOf(createTestSession("session_1", "Test Session"))
        val state = FileViewUiState(
            sessions = sessions,
            selectedSessionIndex = 0,
            isLoadingSessions = false
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to delete session when selected", state.canDeleteSession)
    }

    @Test
    fun `canDeleteSession returns false when no session selected`() {
        // Given
        val state = FileViewUiState(
            sessions = emptyList(),
            selectedSessionIndex = -1,
            isLoadingSessions = false
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to delete session when none selected", state.canDeleteSession)
    }

    @Test
    fun `canShareFiles returns true when files selected and not loading`() {
        // Given
        val state = FileViewUiState(
            selectedFileIndices = setOf(0, 2),
            isLoadingFiles = false
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to share files when selected", state.canShareFiles)
    }

    @Test
    fun `canShareFiles returns false when no files selected`() {
        // Given
        val state = FileViewUiState(
            selectedFileIndices = emptySet(),
            isLoadingFiles = false
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to share files when none selected", state.canShareFiles)
    }

    @Test
    fun `storageUsagePercentage calculates correctly`() {
        // Given
        val state = FileViewUiState(
            totalStorageUsed = 750L * 1024 * 1024, // 750 MB
            availableStorage = 250L * 1024 * 1024  // 250 MB
        )

        // When & Then
        val expectedPercentage = 0.75f // 750 / (750 + 250)
        assertEquals("[DEBUG_LOG] Storage usage percentage should be correct", 
            expectedPercentage, state.storageUsagePercentage, 0.01f)
    }

    @Test
    fun `storageUsagePercentage returns zero when no storage data`() {
        // Given
        val state = FileViewUiState(
            totalStorageUsed = 0L,
            availableStorage = 0L
        )

        // When & Then
        assertEquals("[DEBUG_LOG] Storage usage percentage should be zero", 
            0f, state.storageUsagePercentage, 0.01f)
    }

    @Test
    fun `showStorageWarning returns true when usage exceeds threshold`() {
        // Given
        val state = FileViewUiState(
            totalStorageUsed = 900L * 1024 * 1024, // 900 MB
            availableStorage = 100L * 1024 * 1024, // 100 MB
            storageWarningThreshold = 0.8f // 80%
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should show storage warning when usage exceeds threshold", 
            state.showStorageWarning)
    }

    @Test
    fun `showStorageWarning returns false when usage below threshold`() {
        // Given
        val state = FileViewUiState(
            totalStorageUsed = 500L * 1024 * 1024, // 500 MB
            availableStorage = 500L * 1024 * 1024, // 500 MB
            storageWarningThreshold = 0.8f // 80%
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not show storage warning when usage below threshold", 
            state.showStorageWarning)
    }

    @Test
    fun `totalFileCount sums files across all sessions`() {
        // Given
        val sessions = listOf(
            createTestSession("session_1", "Session 1", fileCount = 5),
            createTestSession("session_2", "Session 2", fileCount = 3),
            createTestSession("session_3", "Session 3", fileCount = 7)
        )
        val state = FileViewUiState(sessions = sessions)

        // When & Then
        assertEquals("[DEBUG_LOG] Total file count should sum all session files", 
            15, state.totalFileCount)
    }

    @Test
    fun `totalFileCount returns zero when no sessions`() {
        // Given
        val state = FileViewUiState(sessions = emptyList())

        // When & Then
        assertEquals("[DEBUG_LOG] Total file count should be zero when no sessions", 
            0, state.totalFileCount)
    }

    @Test
    fun `selectedFilesCount returns correct count`() {
        // Given
        val state = FileViewUiState(selectedFileIndices = setOf(0, 2, 4, 7))

        // When & Then
        assertEquals("[DEBUG_LOG] Selected files count should match indices size", 
            4, state.selectedFilesCount)
    }

    @Test
    fun `selectedFiles returns correct files when valid indices`() {
        // Given
        val files =
            listOf(
                createTestFile("file1.mp4", FileType.VIDEO),
                createTestFile("file2.dng", FileType.RAW_IMAGE),
                createTestFile("file3.dat", FileType.THERMAL_DATA),
            )
        val state = FileViewUiState(
            sessionFiles = files,
            selectedFileIndices = setOf(0, 2)
        )

        // When & Then
        val selectedFiles = state.selectedFiles
        assertEquals("[DEBUG_LOG] Should return 2 selected files", 2, selectedFiles.size)
        assertEquals("[DEBUG_LOG] First selected file should be correct", "file1.mp4", selectedFiles[0].file.name)
        assertEquals("[DEBUG_LOG] Second selected file should be correct", "file3.dat", selectedFiles[1].file.name)
    }

    @Test
    fun `selectedFiles handles invalid indices gracefully`() {
        // Given
        val files = listOf(createTestFile("file1.mp4", FileType.VIDEO))
        val state = FileViewUiState(
            sessionFiles = files,
            selectedFileIndices = setOf(0, 5, 10) // indices 5 and 10 are invalid
        )

        // When & Then
        val selectedFiles = state.selectedFiles
        assertEquals("[DEBUG_LOG] Should return only valid files", 1, selectedFiles.size)
        assertEquals("[DEBUG_LOG] Valid file should be returned", "file1.mp4", selectedFiles[0].file.name)
    }

    @Test
    fun `searchResultsCount returns filtered count when searching`() {
        // Given
        val sessions = listOf(
            createTestSession("session_1", "Test Session 1"),
            createTestSession("session_2", "Test Session 2")
        )
        val filteredSessions = listOf(sessions[0]) // Only first session matches search
        val state = FileViewUiState(
            sessions = sessions,
            filteredSessions = filteredSessions,
            searchQuery = "Test Session 1"
        )

        // When & Then
        assertEquals("[DEBUG_LOG] Search results count should return filtered count", 
            1, state.searchResultsCount)
    }

    @Test
    fun `searchResultsCount returns total count when not searching`() {
        // Given
        val sessions = listOf(
            createTestSession("session_1", "Test Session 1"),
            createTestSession("session_2", "Test Session 2")
        )
        val state = FileViewUiState(
            sessions = sessions,
            searchQuery = ""
        )

        // When & Then
        assertEquals("[DEBUG_LOG] Search results count should return total count when not searching", 
            2, state.searchResultsCount)
    }

    @Test
    fun `session item formatted duration works correctly`() {
        // Given
        val session = SessionItem(
            sessionId = "test",
            name = "Test Session",
            startTime = 0L,
            endTime = 0L,
            duration = 3661000L, // 1h 1m 1s
            fileCount = 5,
            totalSize = 1024L,
            deviceTypes = listOf("camera", "shimmer"),
            status = SessionStatus.COMPLETED
        )

        // When & Then
        assertEquals("[DEBUG_LOG] Formatted duration should be correct", "1h 1m 1s", session.formattedDuration)
    }

    @Test
    fun `session item formatted duration handles minutes only`() {
        // Given
        val session = createTestSession("test", "Test", duration = 125000L) // 2m 5s

        // When & Then
        assertEquals("[DEBUG_LOG] Formatted duration should show minutes and seconds", "2m 5s", session.formattedDuration)
    }

    @Test
    fun `session item formatted duration handles seconds only`() {
        // Given
        val session = createTestSession("test", "Test", duration = 45000L) // 45s

        // When & Then
        assertEquals("[DEBUG_LOG] Formatted duration should show seconds only", "45s", session.formattedDuration)
    }

    @Test
    fun `file item extension extraction works correctly`() {
        // Given
        val fileItem = createTestFile("recording_session_001.mp4", FileType.VIDEO)

        // When & Then
        assertEquals("[DEBUG_LOG] File extension should be extracted correctly", "mp4", fileItem.file.extension)
    }

    @Test
    fun `file item extension handles files without extension`() {
        // Given
        val fileItem = createTestFile("logfile", FileType.THERMAL_DATA)

        // When & Then
        assertEquals("[DEBUG_LOG] File without extension should return empty string", "", fileItem.file.extension)
    }

    @Test
    fun `file type enum contains all expected types`() {
        // Test all file type values
        val types = FileType.values()
        
        assertTrue("[DEBUG_LOG] Should contain VIDEO type", types.contains(FileType.VIDEO))
        assertTrue("[DEBUG_LOG] Should contain RAW_IMAGE type", types.contains(FileType.RAW_IMAGE))
        assertTrue("[DEBUG_LOG] Should contain THERMAL_DATA type", types.contains(FileType.THERMAL_DATA))
        
        // Verify we have exactly 3 types
        assertEquals("[DEBUG_LOG] Should have exactly 3 file types", 3, types.size)
    }

    @Test
    fun `session status enum contains all expected statuses`() {
        // Test all session status values
        val statuses = SessionStatus.values()
        
        assertTrue("[DEBUG_LOG] Should contain COMPLETED status", statuses.contains(SessionStatus.COMPLETED))
        assertTrue("[DEBUG_LOG] Should contain INTERRUPTED status", statuses.contains(SessionStatus.INTERRUPTED))
        assertTrue("[DEBUG_LOG] Should contain CORRUPTED status", statuses.contains(SessionStatus.CORRUPTED))
        assertTrue("[DEBUG_LOG] Should contain PROCESSING status", statuses.contains(SessionStatus.PROCESSING))
    }

    // Helper methods for creating test data
    private fun createTestSession(
        sessionId: String,
        name: String,
        fileCount: Int = 3,
        duration: Long = 60000L
    ): SessionItem {
        return SessionItem(
            sessionId = sessionId,
            name = name,
            startTime = System.currentTimeMillis(),
            endTime = System.currentTimeMillis() + duration,
            duration = duration,
            fileCount = fileCount,
            totalSize = 1024L * 1024L, // 1 MB
            deviceTypes = listOf("camera", "shimmer"),
            status = SessionStatus.COMPLETED
        )
    }

    private fun createTestFile(fileName: String, fileType: FileType): FileItem {
        val mockFile = File(fileName)
        return FileItem(file = mockFile, type = fileType, sessionId = "test_session")
    }
}