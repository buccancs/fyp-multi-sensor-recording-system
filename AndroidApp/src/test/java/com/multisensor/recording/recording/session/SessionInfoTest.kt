package com.multisensor.recording.recording.session

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import com.multisensor.recording.testfixtures.SessionInfoTestFactory
import org.junit.Test

/**
 * Comprehensive unit tests for SessionInfo data class
 * 
 * Test Categories:
 * - Basic initialization and properties
 * - State transitions and business logic
 * - Duration calculations
 * - File management operations
 * - Error handling
 * - Thermal data operations
 */
class SessionInfoTest : BaseUnitTest() {

    @Test
    fun `SessionInfo should initialize with correct default values`() {
        // Given
        val sessionId = "test-session-123"
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(sessionId = sessionId)

        // Then
        assertThat(sessionInfo.sessionId).isEqualTo(sessionId)
        assertThat(sessionInfo.videoEnabled).isFalse()
        assertThat(sessionInfo.rawEnabled).isFalse()
        assertThat(sessionInfo.thermalEnabled).isFalse()
        assertThat(sessionInfo.startTime).isEqualTo(0L)
        assertThat(sessionInfo.endTime).isEqualTo(0L)
        assertThat(sessionInfo.videoFilePath).isNull()
        assertThat(sessionInfo.rawFilePaths).isEmpty()
        assertThat(sessionInfo.thermalFilePath).isNull()
        assertThat(sessionInfo.cameraId).isNull()
        assertThat(sessionInfo.videoResolution).isNull()
        assertThat(sessionInfo.rawResolution).isNull()
        assertThat(sessionInfo.thermalResolution).isNull()
        assertThat(sessionInfo.thermalFrameCount).isEqualTo(0L)
        assertThat(sessionInfo.errorOccurred).isFalse()
        assertThat(sessionInfo.errorMessage).isNull()
    }

    @Test
    fun `getDurationMs should calculate correct duration for completed session`() {
        // Given
        val startTime = 1000L
        val endTime = 5000L
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(
            startTime = startTime,
            endTime = endTime
        )

        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertThat(duration).isEqualTo(4000L)
    }

    @Test
    fun `getDurationMs should return zero for session not started`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()

        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertThat(duration).isEqualTo(0L)
    }

    @Test
    fun `getDurationMs should return zero for active session with endTime before startTime`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(
            startTime = 5000L,
            endTime = 1000L
        )

        // When
        val duration = sessionInfo.getDurationMs()

        // Then
        assertThat(duration).isEqualTo(0L)
    }

    @Test
    fun `isActive should return true when session is started but not completed`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(
            startTime = System.currentTimeMillis(),
            endTime = 0L
        )

        // When & Then
        assertThat(sessionInfo.isActive()).isTrue()
    }

    @Test
    fun `isActive should return false when session is not started`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()

        // When & Then
        assertThat(sessionInfo.isActive()).isFalse()
    }

    @Test
    fun `isActive should return false when session is completed`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createCompletedSession()

        // When & Then
        assertThat(sessionInfo.isActive()).isFalse()
    }

    @Test
    fun `markCompleted should set endTime when session is active`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createActiveSession()
        val originalEndTime = sessionInfo.endTime

        // When
        sessionInfo.markCompleted()

        // Then
        assertThat(sessionInfo.endTime).isNotEqualTo(originalEndTime)
        assertThat(sessionInfo.endTime).isGreaterThan(sessionInfo.startTime)
        assertThat(sessionInfo.isActive()).isFalse()
    }

    @Test
    fun `markCompleted should not change endTime when already set`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createCompletedSession()
        val originalEndTime = sessionInfo.endTime

        // When
        sessionInfo.markCompleted()

        // Then
        assertThat(sessionInfo.endTime).isEqualTo(originalEndTime)
    }

    @Test
    fun `addRawFile should add file path to rawFilePaths list`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()
        val filePath = "/path/to/raw/file.csv"

        // When
        sessionInfo.addRawFile(filePath)

        // Then
        assertThat(sessionInfo.rawFilePaths).containsExactly(filePath)
        assertThat(sessionInfo.getRawImageCount()).isEqualTo(1)
    }

    @Test
    fun `addRawFile should handle multiple files`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()
        val filePaths = listOf("/path/1.csv", "/path/2.csv", "/path/3.csv")

        // When
        filePaths.forEach { sessionInfo.addRawFile(it) }

        // Then
        assertThat(sessionInfo.rawFilePaths).containsExactlyElementsIn(filePaths)
        assertThat(sessionInfo.getRawImageCount()).isEqualTo(3)
    }

    @Test
    fun `setThermalFile should update thermalFilePath`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()
        val thermalPath = "/path/to/thermal.bin"

        // When
        sessionInfo.setThermalFile(thermalPath)

        // Then
        assertThat(sessionInfo.thermalFilePath).isEqualTo(thermalPath)
    }

    @Test
    fun `updateThermalFrameCount should update count`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()
        val frameCount = 1500L

        // When
        sessionInfo.updateThermalFrameCount(frameCount)

        // Then
        assertThat(sessionInfo.thermalFrameCount).isEqualTo(frameCount)
    }

    @Test
    fun `isThermalActive should return true when thermal enabled and file path set`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(
            thermalEnabled = true,
            thermalFilePath = "/path/to/thermal.bin"
        )

        // When & Then
        assertThat(sessionInfo.isThermalActive()).isTrue()
    }

    @Test
    fun `isThermalActive should return false when thermal disabled`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(
            thermalEnabled = false,
            thermalFilePath = "/path/to/thermal.bin"
        )

        // When & Then
        assertThat(sessionInfo.isThermalActive()).isFalse()
    }

    @Test
    fun `isThermalActive should return false when thermal enabled but no file path`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(
            thermalEnabled = true,
            thermalFilePath = null
        )

        // When & Then
        assertThat(sessionInfo.isThermalActive()).isFalse()
    }

    @Test
    fun `getThermalDataSizeMB should calculate correct size for given frame count`() {
        // Given
        val frameCount = 1000L
        val sessionInfo = SessionInfoTestFactory.createSessionInfo(thermalFrameCount = frameCount)

        // When
        val sizeMB = sessionInfo.getThermalDataSizeMB()

        // Then
        // Each frame: 256 * 192 * 2 + 8 = 98312 bytes
        // 1000 frames = 98,312,000 bytes = ~93.77 MB
        assertThat(sizeMB).isWithin(0.1).of(93.77)
    }

    @Test
    fun `getThermalDataSizeMB should return zero for zero frames`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()

        // When
        val sizeGB = sessionInfo.getThermalDataSizeMB()

        // Then
        assertThat(sizeGB).isEqualTo(0.0)
    }

    @Test
    fun `markError should set error state and message`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createSessionInfo()
        val errorMessage = "Test error occurred"

        // When
        sessionInfo.markError(errorMessage)

        // Then
        assertThat(sessionInfo.errorOccurred).isTrue()
        assertThat(sessionInfo.errorMessage).isEqualTo(errorMessage)
    }

    @Test
    fun `getSummary should return comprehensive session information`() {
        // Given
        val sessionInfo = SessionInfoTestFactory.createCompletedSession()

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertThat(summary).contains("SessionInfo[")
        assertThat(summary).contains("id=${sessionInfo.sessionId}")
        assertThat(summary).contains("duration=${sessionInfo.getDurationMs()}ms")
        assertThat(summary).contains("video=enabled")
        assertThat(summary).contains("raw=enabled")
        assertThat(summary).contains("thermal=enabled")
        assertThat(summary).contains("active=${sessionInfo.isActive()}")
    }

    @Test
    fun `getSummary should include error information when error occurred`() {
        // Given
        val errorMessage = "Test error"
        val sessionInfo = SessionInfoTestFactory.createErrorSession(errorMessage = errorMessage)

        // When
        val summary = sessionInfo.getSummary()

        // Then
        assertThat(summary).contains("ERROR: $errorMessage")
    }
}