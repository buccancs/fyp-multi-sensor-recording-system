package com.multisensor.recording.recording

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import com.multisensor.recording.testfixtures.SessionInfoTestFactory
import io.mockk.mockk
import io.mockk.verify
import io.mockk.every
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test

/**
 * Comprehensive tests for RecordingManager using modern test architecture
 */
class RecordingManagerTest : BaseUnitTest() {

    private lateinit var recordingManager: RecordingManager
    private val mockListener: RecordingManager.RecordingListener = mockk(relaxed = true)

    @Before
    override fun setUp() {
        super.setUp()
        recordingManager = RecordingManager()
        recordingManager.setListener(mockListener)
    }

    @Test
    fun `should initialize with default state`() {
        // When & Then
        assertThat(recordingManager.isRecording()).isFalse()
        assertThat(recordingManager.getCurrentSession()).isNull()
        assertThat(recordingManager.getRecordingDuration()).isEqualTo(0L)
    }

    @Test
    fun `should start recording with valid session`() = runTest {
        // Given
        val sessionId = "test-session-123"
        
        // When
        val result = recordingManager.startRecording(sessionId)
        
        // Then
        assertThat(result).isTrue()
        assertThat(recordingManager.isRecording()).isTrue()
        assertThat(recordingManager.getCurrentSession()?.sessionId).isEqualTo(sessionId)
        verify { mockListener.onRecordingStarted(sessionId) }
    }

    @Test
    fun `should not start recording if already recording`() = runTest {
        // Given
        recordingManager.startRecording("existing-session")
        
        // When
        val result = recordingManager.startRecording("new-session")
        
        // Then
        assertThat(result).isFalse()
        assertThat(recordingManager.getCurrentSession()?.sessionId).isEqualTo("existing-session")
    }

    @Test
    fun `should stop recording successfully`() = runTest {
        // Given
        val sessionId = "test-session"
        recordingManager.startRecording(sessionId)
        
        // When
        val result = recordingManager.stopRecording()
        
        // Then
        assertThat(result).isTrue()
        assertThat(recordingManager.isRecording()).isFalse()
        verify { mockListener.onRecordingStopped(sessionId) }
    }

    @Test
    fun `should not stop recording if not recording`() = runTest {
        // When
        val result = recordingManager.stopRecording()
        
        // Then
        assertThat(result).isFalse()
    }

    @Test
    fun `should pause and resume recording`() = runTest {
        // Given
        recordingManager.startRecording("test-session")
        
        // When
        val pauseResult = recordingManager.pauseRecording()
        val resumeResult = recordingManager.resumeRecording()
        
        // Then
        assertThat(pauseResult).isTrue()
        assertThat(resumeResult).isTrue()
        verify { mockListener.onRecordingPaused() }
        verify { mockListener.onRecordingResumed() }
    }

    @Test
    fun `should handle recording errors`() = runTest {
        // Given
        val sessionId = "test-session"
        val errorMessage = "Storage full"
        recordingManager.startRecording(sessionId)
        
        // When
        recordingManager.handleRecordingError(errorMessage)
        
        // Then
        assertThat(recordingManager.isRecording()).isFalse()
        assertThat(recordingManager.getCurrentSession()?.errorOccurred).isTrue()
        verify { mockListener.onRecordingError(errorMessage) }
    }

    @Test
    fun `should update recording duration`() = runTest {
        // Given
        recordingManager.startRecording("test-session")
        val duration = 15000L
        
        // When
        recordingManager.updateDuration(duration)
        
        // Then
        assertThat(recordingManager.getRecordingDuration()).isEqualTo(duration)
    }

    @Test
    fun `should enable and configure recording types`() = runTest {
        // Given
        recordingManager.startRecording("test-session")
        
        // When
        recordingManager.enableVideo(true)
        recordingManager.enableRaw(true)
        recordingManager.enableThermal(true)
        
        // Then
        val session = recordingManager.getCurrentSession()
        assertThat(session?.videoEnabled).isTrue()
        assertThat(session?.rawEnabled).isTrue()
        assertThat(session?.thermalEnabled).isTrue()
    }

    @Test
    fun `should add recorded files to session`() = runTest {
        // Given
        recordingManager.startRecording("test-session")
        val videoPath = "/storage/video.mp4"
        val rawPath = "/storage/raw.csv"
        val thermalPath = "/storage/thermal.bin"
        
        // When
        recordingManager.addVideoFile(videoPath)
        recordingManager.addRawFile(rawPath)
        recordingManager.addThermalFile(thermalPath)
        
        // Then
        val session = recordingManager.getCurrentSession()
        assertThat(session?.videoFilePath).isEqualTo(videoPath)
        assertThat(session?.rawFilePaths).contains(rawPath)
        assertThat(session?.thermalFilePath).isEqualTo(thermalPath)
    }

    @Test
    fun `should calculate total recorded data size`() = runTest {
        // Given
        val session = SessionInfoTestFactory.createCompletedSession()
        recordingManager.setCurrentSession(session)
        
        // When
        val totalSize = recordingManager.calculateTotalDataSize()
        
        // Then
        assertThat(totalSize).isGreaterThan(0.0)
    }

    @Test
    fun `should get recording statistics`() = runTest {
        // Given
        recordingManager.startRecording("test-session")
        recordingManager.updateDuration(30000L)
        recordingManager.enableVideo(true)
        recordingManager.enableThermal(true)
        
        // When
        val stats = recordingManager.getRecordingStatistics()
        
        // Then
        assertThat(stats.duration).isEqualTo(30000L)
        assertThat(stats.videoEnabled).isTrue()
        assertThat(stats.thermalEnabled).isTrue()
        assertThat(stats.sessionId).isNotEmpty()
    }

    @Test
    fun `should validate recording configuration`() = runTest {
        // When
        val isValidEmpty = recordingManager.isValidConfiguration()
        
        recordingManager.enableVideo(true)
        val isValidWithVideo = recordingManager.isValidConfiguration()
        
        // Then
        assertThat(isValidEmpty).isFalse()
        assertThat(isValidWithVideo).isTrue()
    }
}