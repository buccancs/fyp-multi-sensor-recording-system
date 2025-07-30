package com.multisensor.recording.recording

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Comprehensive unit tests for SessionInfo data class
 * Tests all methods, validation logic, and data integrity
 */
class SessionInfoTest {
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
    fun `getDurationMs should return zero when times are not set`() {
        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertEquals(0L, duration)
    }

    @Test
    fun `getDurationMs should calculate correct duration`() {
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
    fun `getDurationMs should return zero when endTime is before startTime`() {
        // Given
        sessionInfo.startTime = 5000L
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
    fun `getRawImageCount should return zero for empty list`() {
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
        sessionInfo.startTime = 1000L
        sessionInfo.endTime = 0L
        val beforeTime = System.currentTimeMillis()

        // When
        sessionInfo.markCompleted()
        val afterTime = System.currentTimeMillis()

        // Then
        assertTrue(sessionInfo.endTime >= beforeTime)
        assertTrue(sessionInfo.endTime <= afterTime)
        assertFalse(sessionInfo.isActive())
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
        assertEquals(originalEndTime, sessionInfo.endTime)
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
        val thermalPath = "/path/to/thermal.dat"

        // When
        sessionInfo.setThermalFile(thermalPath)

        // Then
        assertEquals(thermalPath, sessionInfo.thermalFilePath)
    }

    @Test
    fun `updateThermalFrameCount should update frame count`() {
        // Given
        val frameCount = 1500L

        // When
        sessionInfo.updateThermalFrameCount(frameCount)

        // Then
        assertEquals(frameCount, sessionInfo.thermalFrameCount)
    }

    @Test
    fun `isThermalActive should return true when thermal is enabled and file path is set`() {
        // Given
        sessionInfo.thermalEnabled = true
        sessionInfo.setThermalFile("/path/to/thermal.dat")

        // When
        val isActive = sessionInfo.isThermalActive()

        // Then
        assertTrue(isActive)
    }

    @Test
    fun `isThermalActive should return false when thermal is not enabled`() {
        // Given
        sessionInfo.thermalEnabled = false
        sessionInfo.setThermalFile("/path/to/thermal.dat")

        // When
        val isActive = sessionInfo.isThermalActive()

        // Then
        assertFalse(isActive)
    }

    @Test
    fun `isThermalActive should return false when file path is not set`() {
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
        val frameCount = 1000L
        sessionInfo.updateThermalFrameCount(frameCount)

        // When
        val sizeMB = sessionInfo.getThermalDataSizeMB()

        // Then
        // Each frame is 256*192*2 + 8 = 98312 bytes
        // 1000 frames = 98,312,000 bytes = ~93.8 MB
        val expectedSize = (frameCount * (256 * 192 * 2 + 8)) / (1024.0 * 1024.0)
        assertEquals(expectedSize, sizeMB, 0.01)
    }

    @Test
    fun `getThermalDataSizeMB should return zero for no frames`() {
        // Given
        sessionInfo.updateThermalFrameCount(0L)

        // When
        val sizeMB = sessionInfo.getThermalDataSizeMB()

        // Then
        assertEquals(0.0, sizeMB, 0.01)
    }

    @Test
    fun `markError should set error state`() {
        // Given
        val errorMessage = "Test error occurred"

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
        sessionInfo.endTime = 6000L
        sessionInfo.addRawFile("/path/to/raw1.dng")
        sessionInfo.addRawFile("/path/to/raw2.dng")
        sessionInfo.updateThermalFrameCount(500L)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue(summary.contains("id=$testSessionId"))
        assertTrue(summary.contains("duration=5000ms"))
        assertTrue(summary.contains("video=enabled"))
        assertTrue(summary.contains("raw=enabled (2 files)"))
        assertTrue(summary.contains("thermal=enabled (500 frames"))
        assertTrue(summary.contains("active=false"))
    }

    @Test
    fun `getSummary should show disabled states correctly`() {
        // Given - all features disabled (default state)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue(summary.contains("video=disabled"))
        assertTrue(summary.contains("raw=disabled"))
        assertTrue(summary.contains("thermal=disabled"))
    }

    @Test
    fun `getSummary should include error information when error occurred`() {
        // Given
        val errorMessage = "Test error"
        sessionInfo.markError(errorMessage)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue(summary.contains("ERROR: $errorMessage"))
    }

    @Test
    fun `getSummary should show active state correctly`() {
        // Given
        sessionInfo.startTime = System.currentTimeMillis()
        sessionInfo.endTime = 0L

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertTrue(summary.contains("active=true"))
    }

    @Test
    fun `SessionInfo should be mutable for all properties`() {
        // Given
        val newVideoPath = "/new/video.mp4"
        val newCameraId = "camera_1"
        val newVideoResolution = "1920x1080"
        val newRawResolution = "4000x3000"
        val newThermalResolution = "256x192"

        // When
        sessionInfo.videoEnabled = true
        sessionInfo.rawEnabled = true
        sessionInfo.thermalEnabled = true
        sessionInfo.videoFilePath = newVideoPath
        sessionInfo.cameraId = newCameraId
        sessionInfo.videoResolution = newVideoResolution
        sessionInfo.rawResolution = newRawResolution
        sessionInfo.thermalResolution = newThermalResolution

        // Then
        assertTrue(sessionInfo.videoEnabled)
        assertTrue(sessionInfo.rawEnabled)
        assertTrue(sessionInfo.thermalEnabled)
        assertEquals(newVideoPath, sessionInfo.videoFilePath)
        assertEquals(newCameraId, sessionInfo.cameraId)
        assertEquals(newVideoResolution, sessionInfo.videoResolution)
        assertEquals(newRawResolution, sessionInfo.rawResolution)
        assertEquals(newThermalResolution, sessionInfo.thermalResolution)
    }

    @Test
    fun `rawFilePaths should be mutable list`() {
        // Given
        val filePath1 = "/path/to/raw1.dng"
        val filePath2 = "/path/to/raw2.dng"

        // When
        sessionInfo.rawFilePaths.add(filePath1)
        sessionInfo.rawFilePaths.add(filePath2)

        // Then
        assertEquals(2, sessionInfo.rawFilePaths.size)
        assertTrue(sessionInfo.rawFilePaths.contains(filePath1))
        assertTrue(sessionInfo.rawFilePaths.contains(filePath2))

        // When - remove file
        sessionInfo.rawFilePaths.remove(filePath1)

        // Then
        assertEquals(1, sessionInfo.rawFilePaths.size)
        assertFalse(sessionInfo.rawFilePaths.contains(filePath1))
        assertTrue(sessionInfo.rawFilePaths.contains(filePath2))
    }

    @Test
    fun `thermal data size calculation should handle large frame counts`() {
        // Given
        val largeFrameCount = 100000L // 100k frames
        sessionInfo.updateThermalFrameCount(largeFrameCount)

        // When
        val sizeMB = sessionInfo.getThermalDataSizeMB()

        // Then
        assertTrue(sizeMB > 0)
        // Should be approximately 9.38 GB for 100k frames
        assertTrue(sizeMB > 9000) // More than 9 GB
    }
}
