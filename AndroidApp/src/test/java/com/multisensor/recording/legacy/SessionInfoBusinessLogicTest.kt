package com.multisensor.recording.recording

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Non-Android unit tests for SessionInfo data class
 * Tests all properties, methods, and business logic without requiring Robolectric
 */
class SessionInfoBusinessLogicTest {
    private lateinit var sessionInfo: SessionInfo
    private val testSessionId = "test_session_123"

    @Before
    fun setup() {
        sessionInfo = SessionInfo(sessionId = testSessionId)
    }

    @Test
    fun `SessionInfo should initialize with correct default values`() {
        // Then
        assertEquals(testSessionId, sessionInfo.sessionId)
        assertFalse(sessionInfo.videoEnabled)
        assertFalse(sessionInfo.rawEnabled)
        assertFalse(sessionInfo.thermalEnabled)
        assertEquals(0L, sessionInfo.startTime)
        assertEquals(0L, sessionInfo.endTime)
        assertNull(sessionInfo.videoFilePath)
        assertTrue(sessionInfo.rawFilePaths.isEmpty())
        assertNull(sessionInfo.thermalFilePath)
        assertNull(sessionInfo.cameraId)
        assertNull(sessionInfo.videoResolution)
        assertNull(sessionInfo.rawResolution)
        assertNull(sessionInfo.thermalResolution)
        assertEquals(0L, sessionInfo.thermalFrameCount)
        assertFalse(sessionInfo.errorOccurred)
        assertNull(sessionInfo.errorMessage)
    }

    @Test
    fun `SessionInfo should allow setting all properties`() {
        // Given
        val startTime = System.currentTimeMillis()
        val endTime = startTime + 60000 // 1 minute later

        // When
        sessionInfo.videoEnabled = true
        sessionInfo.rawEnabled = true
        sessionInfo.thermalEnabled = true
        sessionInfo.startTime = startTime
        sessionInfo.endTime = endTime
        sessionInfo.videoFilePath = "/path/to/video.mp4"
        sessionInfo.thermalFilePath = "/path/to/thermal.bin"
        sessionInfo.cameraId = "camera_0"
        sessionInfo.videoResolution = "1920x1080"
        sessionInfo.rawResolution = "4032x3024"
        sessionInfo.thermalResolution = "256x192"
        sessionInfo.thermalFrameCount = 1800L // 30fps * 60s

        // Then
        assertTrue(sessionInfo.videoEnabled)
        assertTrue(sessionInfo.rawEnabled)
        assertTrue(sessionInfo.thermalEnabled)
        assertEquals(startTime, sessionInfo.startTime)
        assertEquals(endTime, sessionInfo.endTime)
        assertEquals("/path/to/video.mp4", sessionInfo.videoFilePath)
        assertEquals("/path/to/thermal.bin", sessionInfo.thermalFilePath)
        assertEquals("camera_0", sessionInfo.cameraId)
        assertEquals("1920x1080", sessionInfo.videoResolution)
        assertEquals("4032x3024", sessionInfo.rawResolution)
        assertEquals("256x192", sessionInfo.thermalResolution)
        assertEquals(1800L, sessionInfo.thermalFrameCount)
    }

    @Test
    fun `getDurationMs should return correct duration`() {
        // Given
        val startTime = 1000L
        val endTime = 5000L
        sessionInfo.startTime = startTime
        sessionInfo.endTime = endTime

        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertEquals(4000L, duration)
    }

    @Test
    fun `getDurationMs should return 0 when endTime is before startTime`() {
        // Given
        sessionInfo.startTime = 5000L
        sessionInfo.endTime = 1000L

        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertEquals(0L, duration)
    }

    @Test
    fun `getDurationMs should return 0 when times are equal`() {
        // Given
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = 1000L

        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertEquals(0L, duration)
    }

    @Test
    fun `getRawImageCount should return correct count`() {
        // Given
        sessionInfo.addRawFile("/path/to/raw1.dng")
        sessionInfo.addRawFile("/path/to/raw2.dng")
        sessionInfo.addRawFile("/path/to/raw3.dng")

        // When
        val count = sessionInfo.getRawImageCount()

        // Then
        assertEquals(3, count)
    }

    @Test
    fun `getRawImageCount should return 0 for empty list`() {
        // When
        val count = sessionInfo.getRawImageCount()

        // Then
        assertEquals(0, count)
    }

    @Test
    fun `isActive should return true when session is active`() {
        // Given
        sessionInfo.startTime = System.currentTimeMillis()
        sessionInfo.endTime = 0L

        // When
        val isActive = sessionInfo.isActive()

        // Then
        assertTrue(isActive)
    }

    @Test
    fun `isActive should return false when session is not started`() {
        // Given
        sessionInfo.startTime = 0L
        sessionInfo.endTime = 0L

        // When
        val isActive = sessionInfo.isActive()

        // Then
        assertFalse(isActive)
    }

    @Test
    fun `isActive should return false when session is completed`() {
        // Given
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = 2000L

        // When
        val isActive = sessionInfo.isActive()

        // Then
        assertFalse(isActive)
    }

    @Test
    fun `markCompleted should set endTime when not already set`() {
        // Given
        sessionInfo.startTime = System.currentTimeMillis()
        sessionInfo.endTime = 0L
        val timeBefore = System.currentTimeMillis()

        // When
        sessionInfo.markCompleted()

        // Then
        assertTrue("End time should be set", sessionInfo.endTime > 0L)
        assertTrue("End time should be recent", sessionInfo.endTime >= timeBefore)
        assertFalse("Session should no longer be active", sessionInfo.isActive())
    }

    @Test
    fun `markCompleted should not change endTime when already set`() {
        // Given
        val originalEndTime = 5000L
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = originalEndTime

        // When
        sessionInfo.markCompleted()

        // Then
        assertEquals("End time should remain unchanged", originalEndTime, sessionInfo.endTime)
    }

    @Test
    fun `addRawFile should add file to list`() {
        // Given
        val filePath1 = "/path/to/raw1.dng"
        val filePath2 = "/path/to/raw2.dng"

        // When
        sessionInfo.addRawFile(filePath1)
        sessionInfo.addRawFile(filePath2)

        // Then
        assertEquals(2, sessionInfo.rawFilePaths.size)
        assertTrue(sessionInfo.rawFilePaths.contains(filePath1))
        assertTrue(sessionInfo.rawFilePaths.contains(filePath2))
    }

    @Test
    fun `setThermalFile should set thermal file path`() {
        // Given
        val thermalPath = "/path/to/thermal.bin"

        // When
        sessionInfo.setThermalFile(thermalPath)

        // Then
        assertEquals(thermalPath, sessionInfo.thermalFilePath)
    }

    @Test
    fun `updateThermalFrameCount should update frame count`() {
        // Given
        val frameCount = 1800L

        // When
        sessionInfo.updateThermalFrameCount(frameCount)

        // Then
        assertEquals(frameCount, sessionInfo.thermalFrameCount)
    }

    @Test
    fun `isThermalActive should return true when thermal is enabled and file is set`() {
        // Given
        sessionInfo.thermalEnabled = true
        sessionInfo.setThermalFile("/path/to/thermal.bin")

        // When
        val isActive = sessionInfo.isThermalActive()

        // Then
        assertTrue(isActive)
    }

    @Test
    fun `isThermalActive should return false when thermal is disabled`() {
        // Given
        sessionInfo.thermalEnabled = false
        sessionInfo.setThermalFile("/path/to/thermal.bin")

        // When
        val isActive = sessionInfo.isThermalActive()

        // Then
        assertFalse(isActive)
    }

    @Test
    fun `isThermalActive should return false when thermal file is not set`() {
        // Given
        sessionInfo.thermalEnabled = true
        sessionInfo.thermalFilePath = null

        // When
        val isActive = sessionInfo.isThermalActive()

        // Then
        assertFalse(isActive)
    }

    @Test
    fun `getThermalDataSizeMB should calculate correct size`() {
        // Given
        sessionInfo.updateThermalFrameCount(1000L)

        // When
        val sizeMB = sessionInfo.getThermalDataSizeMB()

        // Then
        // Each frame: 256 * 192 * 2 + 8 = 98,312 bytes
        // 1000 frames = 98,312,000 bytes = ~93.75 MB
        assertTrue("Size should be approximately 93.75 MB", sizeMB > 93.0 && sizeMB < 95.0)
    }

    @Test
    fun `getThermalDataSizeMB should return 0 for no frames`() {
        // Given
        sessionInfo.updateThermalFrameCount(0L)

        // When
        val sizeMB = sessionInfo.getThermalDataSizeMB()

        // Then
        assertEquals(0.0, sizeMB, 0.001)
    }

    @Test
    fun `markError should set error state`() {
        // Given
        val errorMessage = "Camera initialization failed"

        // When
        sessionInfo.markError(errorMessage)

        // Then
        assertTrue(sessionInfo.errorOccurred)
        assertEquals(errorMessage, sessionInfo.errorMessage)
    }

    @Test
    fun `getSummary should include all relevant information`() {
        // Given
        sessionInfo.videoEnabled = true
        sessionInfo.rawEnabled = true
        sessionInfo.thermalEnabled = true
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = 5000L
        sessionInfo.addRawFile("/path/to/raw1.dng")
        sessionInfo.addRawFile("/path/to/raw2.dng")
        sessionInfo.updateThermalFrameCount(100L)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue("Should contain session ID", summary.contains(testSessionId))
        assertTrue("Should contain duration", summary.contains("4000ms"))
        assertTrue("Should contain video enabled", summary.contains("video=enabled"))
        assertTrue("Should contain raw enabled with count", summary.contains("raw=enabled (2 files)"))
        assertTrue("Should contain thermal enabled with frames", summary.contains("thermal=enabled (100 frames"))
        assertTrue("Should contain thermal size", summary.contains("MB)"))
        assertTrue("Should contain active status", summary.contains("active=false"))
    }

    @Test
    fun `getSummary should show disabled features correctly`() {
        // Given - all features disabled (default state)
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = 2000L

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue("Should show video disabled", summary.contains("video=disabled"))
        assertTrue("Should show raw disabled", summary.contains("raw=disabled"))
        assertTrue("Should show thermal disabled", summary.contains("thermal=disabled"))
        assertTrue("Should show not active", summary.contains("active=false"))
    }

    @Test
    fun `getSummary should show error information when error occurred`() {
        // Given
        val errorMessage = "Test error occurred"
        sessionInfo.markError(errorMessage)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue("Should contain error message", summary.contains("ERROR: $errorMessage"))
    }

    @Test
    fun `getSummary should show active session correctly`() {
        // Given
        sessionInfo.startTime = System.currentTimeMillis()
        sessionInfo.endTime = 0L

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue("Should show active=true", summary.contains("active=true"))
    }

    @Test
    fun `data class should support copy functionality`() {
        // Given
        sessionInfo.videoEnabled = true
        sessionInfo.startTime = 1000L

        // When
        val copiedSession = sessionInfo.copy(sessionId = "new_session_id")

        // Then
        assertEquals("new_session_id", copiedSession.sessionId)
        assertTrue("Should preserve other properties", copiedSession.videoEnabled)
        assertEquals(1000L, copiedSession.startTime)
    }

    @Test
    fun `data class should support equality comparison`() {
        // Given
        val session1 = SessionInfo(sessionId = "test_id")
        val session2 = SessionInfo(sessionId = "test_id")
        val session3 = SessionInfo(sessionId = "different_id")

        // Then
        assertEquals("Sessions with same data should be equal", session1, session2)
        assertNotEquals("Sessions with different data should not be equal", session1, session3)
    }
}
