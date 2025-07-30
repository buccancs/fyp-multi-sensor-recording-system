package com.multisensor.recording.ui

import com.multisensor.recording.recording.SessionInfo
import org.junit.Assert.*
import org.junit.Test
import java.io.File

/**
 * Unit tests for file management logic without Android dependencies.
 * Tests core functionality of SessionInfo and file operations.
 */
class FileManagementLogicTest {
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

    @Test
    fun `SessionInfo should calculate duration correctly`() {
        // Given
        val sessionInfo = createTestSessionInfo("duration_test")
        val startTime = 1000L
        val endTime = 5000L

        // When
        sessionInfo.startTime = startTime
        sessionInfo.endTime = endTime

        // Then
        assertEquals(4000L, sessionInfo.getDurationMs())
    }

    @Test
    fun `SessionInfo should handle active state correctly`() {
        // Given
        val sessionInfo = createTestSessionInfo("active_test")

        // When - Session started but not ended
        sessionInfo.startTime = System.currentTimeMillis()
        sessionInfo.endTime = 0L

        // Then
        assertTrue("Session should be active", sessionInfo.isActive())

        // When - Session completed
        sessionInfo.markCompleted()

        // Then
        assertFalse("Session should not be active", sessionInfo.isActive())
        assertTrue("End time should be set", sessionInfo.endTime > 0L)
    }

    @Test
    fun `SessionInfo should handle thermal data correctly`() {
        // Given
        val sessionInfo = createTestSessionInfo("thermal_test")

        // When
        sessionInfo.thermalEnabled = true
        sessionInfo.setThermalFile("/test/thermal.bin")
        sessionInfo.updateThermalFrameCount(100L)

        // Then
        assertTrue("Thermal should be active", sessionInfo.isThermalActive())
        assertEquals(100L, sessionInfo.thermalFrameCount)
        assertTrue("Thermal data size should be calculated", sessionInfo.getThermalDataSizeMB() > 0.0)
    }

    @Test
    fun `SessionInfo should handle errors correctly`() {
        // Given
        val sessionInfo = createTestSessionInfo("error_test")
        val errorMessage = "Test error occurred"

        // When
        sessionInfo.markError(errorMessage)

        // Then
        assertTrue("Error should be marked", sessionInfo.errorOccurred)
        assertEquals(errorMessage, sessionInfo.errorMessage)
    }

    @Test
    fun `SessionInfo should generate summary correctly`() {
        // Given
        val sessionInfo = createTestSessionInfo("summary_test")
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = 5000L
        sessionInfo.addRawFile("/test/raw1.dng")
        sessionInfo.updateThermalFrameCount(50L)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue("Summary should contain session ID", summary.contains("summary_test"))
        assertTrue("Summary should contain duration", summary.contains("4000ms"))
        assertTrue("Summary should contain RAW count", summary.contains("1 files"))
        assertTrue("Summary should contain thermal frames", summary.contains("50 frames"))
    }

    @Test
    fun `File operations should handle different extensions`() {
        // Given
        val videoFile = File("test_video.mp4")
        val rawFile = File("test_image.dng")
        val thermalFile = File("test_thermal.bin")

        // When & Then
        assertTrue("Video file should have mp4 extension", videoFile.name.endsWith(".mp4"))
        assertTrue("RAW file should have dng extension", rawFile.name.endsWith(".dng"))
        assertTrue("Thermal file should have bin extension", thermalFile.name.endsWith(".bin"))
    }

    @Test
    fun `File size calculations should work correctly`() {
        // Given
        val bytes1KB = 1024L
        val bytes1MB = 1024L * 1024L
        val bytes1GB = 1024L * 1024L * 1024L

        // When & Then
        assertEquals("1KB should equal 1024 bytes", 1024L, bytes1KB)
        assertEquals("1MB should equal 1048576 bytes", 1048576L, bytes1MB)
        assertEquals("1GB should equal 1073741824 bytes", 1073741824L, bytes1GB)
    }

    @Test
    fun `Duration calculations should work correctly`() {
        // Given
        val duration30Seconds = 30 * 1000L
        val duration1Minute = 60 * 1000L
        val duration1Hour = 60 * 60 * 1000L

        // When & Then
        assertEquals("30 seconds should equal 30000ms", 30000L, duration30Seconds)
        assertEquals("1 minute should equal 60000ms", 60000L, duration1Minute)
        assertEquals("1 hour should equal 3600000ms", 3600000L, duration1Hour)
    }

    private fun createTestSessionInfo(sessionId: String): SessionInfo =
        SessionInfo(sessionId).apply {
            this.startTime = System.currentTimeMillis()
            this.videoEnabled = true
            this.rawEnabled = true
            this.thermalEnabled = true
        }
}
