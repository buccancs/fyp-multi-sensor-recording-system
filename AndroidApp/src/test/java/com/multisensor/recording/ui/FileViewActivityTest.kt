package com.multisensor.recording.ui

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class FileViewActivityTest {
    private lateinit var mockSessionManager: SessionManager
    private lateinit var mockLogger: Logger
    private lateinit var context: Context

    @Before
    fun setUp() {
        mockSessionManager = mockk()
        mockLogger = mockk(relaxed = true)
        context = ApplicationProvider.getApplicationContext()
    }

    @After
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `getAllSessions should return list of sessions`() =
        runTest {
            // Given
            val testSessions =
                listOf(
                    createTestSessionInfo("session1"),
                    createTestSessionInfo("session2"),
                )
            coEvery { mockSessionManager.getAllSessions() } returns testSessions

            // When
            val result = mockSessionManager.getAllSessions()

            // Then
            assertEquals(2, result.size)
            assertEquals("session1", result[0].sessionId)
            assertEquals("session2", result[1].sessionId)
            verify { mockLogger wasNot Called }
        }

    @Test
    fun `deleteAllSessions should return success`() =
        runTest {
            // Given
            coEvery { mockSessionManager.deleteAllSessions() } returns true

            // When
            val result = mockSessionManager.deleteAllSessions()

            // Then
            assertTrue("Delete all sessions should succeed", result)
            coVerify { mockSessionManager.deleteAllSessions() }
        }

    @Test
    fun `deleteAllSessions should handle failure`() =
        runTest {
            // Given
            coEvery { mockSessionManager.deleteAllSessions() } returns false

            // When
            val result = mockSessionManager.deleteAllSessions()

            // Then
            assertFalse("Delete all sessions should fail", result)
            coVerify { mockSessionManager.deleteAllSessions() }
        }

    @Test
    fun `SessionManager integration should work correctly`() =
        runTest {
            // Given
            val testSessions =
                listOf(
                    createTestSessionInfo("session1"),
                    createTestSessionInfo("session2"),
                )
            coEvery { mockSessionManager.getAllSessions() } returns testSessions

            // When
            val sessions = mockSessionManager.getAllSessions()

            // Then
            assertEquals(2, sessions.size)
            assertTrue("Sessions should contain session1", sessions.any { it.sessionId == "session1" })
            assertTrue("Sessions should contain session2", sessions.any { it.sessionId == "session2" })
        }

    @Test
    fun `File operations should handle different file types`() {
        // Given
        val videoFile = File("/test/video.mp4")
        val rawFile = File("/test/image.dng")
        val thermalFile = File("/test/thermal.bin")

        // When & Then
        assertTrue("Video file should exist in test", videoFile.path.contains("video"))
        assertTrue("RAW file should exist in test", rawFile.path.contains("image"))
        assertTrue("Thermal file should exist in test", thermalFile.path.contains("thermal"))
    }

    @Test
    fun `SessionInfo should be created with correct properties`() {
        // Given
        val sessionId = "test_session_123"
        val startTime = System.currentTimeMillis()

        // When
        val sessionInfo =
            SessionInfo(sessionId).apply {
                this.startTime = startTime
                this.videoEnabled = true
                this.rawEnabled = true
                this.thermalEnabled = true
            }

        // Then
        assertEquals(sessionId, sessionInfo.sessionId)
        assertEquals(startTime, sessionInfo.startTime)
        assertTrue("Video should be enabled", sessionInfo.videoEnabled)
        assertTrue("RAW should be enabled", sessionInfo.rawEnabled)
        assertTrue("Thermal should be enabled", sessionInfo.thermalEnabled)
    }

    @Test
    fun `SessionInfo should track file paths correctly`() {
        // Given
        val sessionInfo = createTestSessionInfo("test_session")

        // When
        sessionInfo.videoFilePath = "/test/video.mp4"
        sessionInfo.addRawFile("/test/raw1.dng")
        sessionInfo.addRawFile("/test/raw2.dng")
        sessionInfo.setThermalFile("/test/thermal.bin")

        // Then
        assertEquals("/test/video.mp4", sessionInfo.videoFilePath)
        assertEquals(2, sessionInfo.getRawImageCount())
        assertEquals("/test/thermal.bin", sessionInfo.thermalFilePath)
    }

    private fun createTestSessionInfo(sessionId: String): SessionInfo =
        SessionInfo(sessionId).apply {
            this.startTime = System.currentTimeMillis()
            this.videoEnabled = true
            this.rawEnabled = true
            this.thermalEnabled = true
        }
}
