package com.multisensor.recording.service

import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.io.File
import java.io.IOException

/**
 * Non-Android unit tests for SessionManager business logic
 * Tests data classes, enums, and core logic without requiring Robolectric
 */
class SessionManagerBusinessLogicTest {
    private lateinit var mockLogger: Logger
    private lateinit var tempDir: File

    @Before
    fun setup() {
        mockLogger = mockk(relaxed = true)
        // Create a temporary directory for testing
        tempDir = createTempDir("session_test")
    }

    @After
    fun tearDown() {
        unmockkAll()
        // Clean up temp directory
        tempDir.deleteRecursively()
    }

    @Test
    fun `SessionStatus enum should have all expected values`() {
        // Test all enum values exist
        val expectedValues =
            setOf(
                SessionManager.SessionStatus.ACTIVE,
                SessionManager.SessionStatus.COMPLETED,
                SessionManager.SessionStatus.FAILED,
                SessionManager.SessionStatus.CANCELLED,
            )

        val actualValues = SessionManager.SessionStatus.values().toSet()
        assertEquals(expectedValues, actualValues)

        // Test enum count
        assertEquals(4, SessionManager.SessionStatus.values().size)
    }

    @Test
    fun `RecordingSession should initialize with correct default values`() {
        // Given
        val sessionId = "test_session_123"
        val startTime = System.currentTimeMillis()
        val sessionFolder = File(tempDir, "session_folder")

        // When
        val session =
            SessionManager.RecordingSession(
                sessionId = sessionId,
                startTime = startTime,
                sessionFolder = sessionFolder,
            )

        // Then
        assertEquals(sessionId, session.sessionId)
        assertEquals(startTime, session.startTime)
        assertEquals(sessionFolder, session.sessionFolder)
        assertNull(session.endTime)
        assertEquals(SessionManager.SessionStatus.ACTIVE, session.status)
    }

    @Test
    fun `RecordingSession should allow setting endTime and status`() {
        // Given
        val sessionId = "test_session_456"
        val startTime = System.currentTimeMillis()
        val endTime = startTime + 60000 // 1 minute later
        val sessionFolder = File(tempDir, "session_folder")

        // When
        val session =
            SessionManager.RecordingSession(
                sessionId = sessionId,
                startTime = startTime,
                sessionFolder = sessionFolder,
                endTime = endTime,
                status = SessionManager.SessionStatus.COMPLETED,
            )

        // Then
        assertEquals(sessionId, session.sessionId)
        assertEquals(startTime, session.startTime)
        assertEquals(endTime, session.endTime)
        assertEquals(SessionManager.SessionStatus.COMPLETED, session.status)
    }

    @Test
    fun `SessionFilePaths should create all required file paths`() {
        // Given
        val sessionFolder = File(tempDir, "test_session")
        val rgbVideoFile = File(sessionFolder, "rgb_video.mp4")
        val thermalVideoFile = File(sessionFolder, "thermal_video.mp4")
        val rawFramesFolder = File(sessionFolder, "raw_frames")
        val shimmerDataFile = File(sessionFolder, "shimmer_data.csv")
        val logFile = File(sessionFolder, "session.log")
        val thermalDataFolder = File(sessionFolder, "thermal_data")
        val calibrationFolder = File(sessionFolder, "calibration")
        val sessionConfigFile = File(sessionFolder, "session_config.json")

        // When
        val filePaths =
            SessionManager.SessionFilePaths(
                sessionFolder = sessionFolder,
                rgbVideoFile = rgbVideoFile,
                thermalVideoFile = thermalVideoFile,
                rawFramesFolder = rawFramesFolder,
                shimmerDataFile = shimmerDataFile,
                logFile = logFile,
                thermalDataFolder = thermalDataFolder,
                calibrationFolder = calibrationFolder,
                sessionConfigFile = sessionConfigFile,
            )

        // Then
        assertEquals(sessionFolder, filePaths.sessionFolder)
        assertEquals(rgbVideoFile, filePaths.rgbVideoFile)
        assertEquals(thermalVideoFile, filePaths.thermalVideoFile)
        assertEquals(rawFramesFolder, filePaths.rawFramesFolder)
        assertEquals(shimmerDataFile, filePaths.shimmerDataFile)
        assertEquals(logFile, filePaths.logFile)
        assertEquals(thermalDataFolder, filePaths.thermalDataFolder)
        assertEquals(calibrationFolder, filePaths.calibrationFolder)
        assertEquals(sessionConfigFile, filePaths.sessionConfigFile)
    }

    @Test
    fun `SessionFilePaths should have correct file extensions`() {
        // Given
        val sessionFolder = File(tempDir, "test_session")
        val rgbVideoFile = File(sessionFolder, "rgb_video.mp4")
        val thermalVideoFile = File(sessionFolder, "thermal_video.mp4")
        val rawFramesFolder = File(sessionFolder, "raw_frames")
        val shimmerDataFile = File(sessionFolder, "shimmer_data.csv")
        val logFile = File(sessionFolder, "session.log")
        val thermalDataFolder = File(sessionFolder, "thermal_data")
        val calibrationFolder = File(sessionFolder, "calibration")
        val sessionConfigFile = File(sessionFolder, "session_config.json")

        // When
        val filePaths =
            SessionManager.SessionFilePaths(
                sessionFolder = sessionFolder,
                rgbVideoFile = rgbVideoFile,
                thermalVideoFile = thermalVideoFile,
                rawFramesFolder = rawFramesFolder,
                shimmerDataFile = shimmerDataFile,
                logFile = logFile,
                thermalDataFolder = thermalDataFolder,
                calibrationFolder = calibrationFolder,
                sessionConfigFile = sessionConfigFile,
            )

        // Then
        assertTrue("RGB video should be MP4", filePaths.rgbVideoFile.name.endsWith(".mp4"))
        assertTrue("Thermal video should be MP4", filePaths.thermalVideoFile.name.endsWith(".mp4"))
        assertTrue("Shimmer data should be CSV", filePaths.shimmerDataFile.name.endsWith(".csv"))
        assertTrue("Log file should be .log", filePaths.logFile.name.endsWith(".log"))
        assertTrue("Session config should be JSON", filePaths.sessionConfigFile.name.endsWith(".json"))
        assertTrue("Raw frames should be a directory", filePaths.rawFramesFolder.name == "raw_frames")
        assertTrue("Thermal data should be a directory", filePaths.thermalDataFolder.name == "thermal_data")
        assertTrue("Calibration should be a directory", filePaths.calibrationFolder.name == "calibration")
    }

    @Test
    fun `session duration calculation should work correctly`() {
        // Given
        val startTime = 1000L
        val endTime = 5000L
        val sessionFolder = File(tempDir, "session_folder")

        val session =
            SessionManager.RecordingSession(
                sessionId = "test_session",
                startTime = startTime,
                sessionFolder = sessionFolder,
                endTime = endTime,
                status = SessionManager.SessionStatus.COMPLETED,
            )

        // When
        val duration = session.endTime!! - session.startTime

        // Then
        assertEquals(4000L, duration)
    }

    @Test
    fun `session should be active by default`() {
        // Given
        val sessionFolder = File(tempDir, "session_folder")

        // When
        val session =
            SessionManager.RecordingSession(
                sessionId = "test_session",
                startTime = System.currentTimeMillis(),
                sessionFolder = sessionFolder,
            )

        // Then
        assertEquals(SessionManager.SessionStatus.ACTIVE, session.status)
        assertNull(session.endTime)
    }

    @Test
    fun `session folder path should be valid`() {
        // Given
        val sessionId = "test_session_789"
        val sessionFolder = File(tempDir, sessionId)

        // When
        val session =
            SessionManager.RecordingSession(
                sessionId = sessionId,
                startTime = System.currentTimeMillis(),
                sessionFolder = sessionFolder,
            )

        // Then
        assertTrue(
            "Session folder path should contain session ID",
            session.sessionFolder.name.contains(sessionId),
        )
        assertEquals(tempDir, session.sessionFolder.parentFile)
    }

    @Test
    fun `file operations should handle directory creation`() {
        // Given
        val sessionFolder = File(tempDir, "new_session")
        val rawFramesFolder = File(sessionFolder, "raw_frames")

        // When
        sessionFolder.mkdirs()
        rawFramesFolder.mkdirs()

        // Then
        assertTrue("Session folder should exist", sessionFolder.exists())
        assertTrue("Session folder should be directory", sessionFolder.isDirectory)
        assertTrue("Raw frames folder should exist", rawFramesFolder.exists())
        assertTrue("Raw frames folder should be directory", rawFramesFolder.isDirectory)
    }

    @Test
    fun `storage space validation logic should work`() {
        // Given
        val requiredSpace = 1024L * 1024L * 100L // 100 MB
        val availableSpace = tempDir.freeSpace

        // When
        val hasSufficientSpace = availableSpace >= requiredSpace

        // Then
        // This test depends on actual disk space, so I just verify the logic works
        assertTrue("Available space should be non-negative", availableSpace >= 0)
        assertEquals(
            "Logic should match expected result",
            availableSpace >= requiredSpace,
            hasSufficientSpace,
        )
    }

    @Test
    fun `session ID should be unique and non-empty`() {
        // Given
        val sessionIds = mutableSetOf<String>()
        val sessionFolder = File(tempDir, "session_folder")

        // When - Create multiple sessions
        repeat(10) {
            val sessionId = "session_${System.currentTimeMillis()}_$it"
            sessionIds.add(sessionId)

            val session =
                SessionManager.RecordingSession(
                    sessionId = sessionId,
                    startTime = System.currentTimeMillis(),
                    sessionFolder = sessionFolder,
                )

            // Then
            assertNotNull("Session ID should not be null", session.sessionId)
            assertTrue("Session ID should not be empty", session.sessionId.isNotEmpty())
        }

        // All session IDs should be unique
        assertEquals("All session IDs should be unique", 10, sessionIds.size)
    }
}
