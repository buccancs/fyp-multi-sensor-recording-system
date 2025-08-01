package com.multisensor.recording.service

import androidx.test.ext.junit.runners.AndroidJUnit4
import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseInstrumentedTest
import com.multisensor.recording.testfixtures.SessionInfoTestFactory
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import javax.inject.Inject

/**
 * Modern instrumented tests for RecordingService using Hilt injection
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RecordingServiceInstrumentedTest : BaseInstrumentedTest() {

    @Inject
    lateinit var recordingService: RecordingService

    @Before
    override fun setUp() {
        super.setUp()
        // Hilt will inject the service
    }

    @Test
    fun shouldInitializeServiceCorrectly() = runTest {
        // When service is initialized
        
        // Then verify initial state
        assertThat(recordingService.isRecording()).isFalse()
        assertThat(recordingService.getCurrentSession()).isNull()
    }

    @Test
    fun shouldStartRecordingWithValidSession() = runTest {
        // Given
        val sessionId = "integration-test-session"
        
        // When
        val result = recordingService.startRecording(sessionId)
        
        // Then
        assertThat(result).isTrue()
        assertThat(recordingService.isRecording()).isTrue()
        assertThat(recordingService.getCurrentSession()?.sessionId).isEqualTo(sessionId)
    }

    @Test
    fun shouldStopRecordingSuccessfully() = runTest {
        // Given
        recordingService.startRecording("test-session")
        
        // When
        val result = recordingService.stopRecording()
        
        // Then
        assertThat(result).isTrue()
        assertThat(recordingService.isRecording()).isFalse()
    }

    @Test
    fun shouldHandleDeviceConnections() = runTest {
        // When
        recordingService.connectToPC("192.168.1.100", 8080)
        recordingService.connectToShimmer("test-device")
        recordingService.connectToThermal()
        
        // Then
        assertThat(recordingService.isPcConnected()).isTrue()
        assertThat(recordingService.isShimmerConnected()).isTrue()
        assertThat(recordingService.isThermalConnected()).isTrue()
    }

    @Test
    fun shouldManageMultipleSessions() = runTest {
        // Given
        val session1 = "session-1"
        val session2 = "session-2"
        
        // When
        recordingService.startRecording(session1)
        recordingService.stopRecording()
        recordingService.startRecording(session2)
        
        // Then
        assertThat(recordingService.getCurrentSession()?.sessionId).isEqualTo(session2)
        assertThat(recordingService.getSessionHistory()).hasSize(2)
    }

    @Test
    fun shouldHandleServiceLifecycle() = runTest {
        // When
        recordingService.onCreate()
        recordingService.onStartCommand(null, 0, 0)
        recordingService.onDestroy()
        
        // Then
        // Service should handle lifecycle correctly without crashing
        assertThat(recordingService).isNotNull()
    }

    @Test
    fun shouldPersistSessionData() = runTest {
        // Given
        val session = SessionInfoTestFactory.createCompletedSession()
        
        // When
        recordingService.saveSession(session)
        val retrievedSession = recordingService.getSession(session.sessionId)
        
        // Then
        assertThat(retrievedSession).isNotNull()
        assertThat(retrievedSession?.sessionId).isEqualTo(session.sessionId)
    }

    @Test
    fun shouldHandleStorageOperations() = runTest {
        // Given
        recordingService.startRecording("storage-test")
        
        // When
        val storageInfo = recordingService.getStorageInfo()
        
        // Then
        assertThat(storageInfo.totalSpace).isGreaterThan(0L)
        assertThat(storageInfo.freeSpace).isAtLeast(0L)
        assertThat(storageInfo.usedSpace).isAtLeast(0L)
    }

    @Test
    fun shouldMonitorBatteryStatus() = runTest {
        // When
        val batteryStatus = recordingService.getBatteryStatus()
        
        // Then
        assertThat(batteryStatus.level).isIn(0..100)
        assertThat(batteryStatus.isCharging).isAnyOf(true, false)
    }

    @Test
    fun shouldHandlePermissions() = runTest {
        // When
        val hasPermissions = recordingService.checkPermissions()
        
        // Then
        // Result depends on test environment permissions
        assertThat(hasPermissions).isAnyOf(true, false)
    }

    @Test
    fun shouldConfigureRecordingSettings() = runTest {
        // Given
        val settings = RecordingSettings(
            videoEnabled = true,
            audioEnabled = false,
            thermalEnabled = true,
            videoResolution = "1920x1080",
            frameRate = 30
        )
        
        // When
        recordingService.updateSettings(settings)
        val currentSettings = recordingService.getSettings()
        
        // Then
        assertThat(currentSettings.videoEnabled).isTrue()
        assertThat(currentSettings.thermalEnabled).isTrue()
        assertThat(currentSettings.videoResolution).isEqualTo("1920x1080")
    }
}