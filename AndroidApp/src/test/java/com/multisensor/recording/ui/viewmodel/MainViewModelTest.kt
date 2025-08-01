package com.multisensor.recording.ui.viewmodel

import androidx.lifecycle.Observer
import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import com.multisensor.recording.testfixtures.UiStateTestFactory
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.MainViewModel
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test

/**
 * Comprehensive tests for MainViewModel using modern test architecture
 */
class MainViewModelTest : BaseUnitTest() {

    private lateinit var viewModel: MainViewModel
    private val uiStateObserver: Observer<MainUiState> = mockk(relaxed = true)

    @Before
    override fun setUp() {
        super.setUp()
        viewModel = MainViewModel()
        viewModel.uiState.observeForever(uiStateObserver)
    }

    @Test
    fun `should initialize with default state`() = runTest {
        // When
        val initialState = viewModel.uiState.value

        // Then
        assertThat(initialState).isNotNull()
        assertThat(initialState?.isInitialized).isTrue()
        assertThat(initialState?.isRecording).isFalse()
        assertThat(initialState?.statusText).isEqualTo("Ready")
    }

    @Test
    fun `should start recording and update state correctly`() = runTest {
        // Given
        val sessionId = "test-session-123"
        
        // When
        viewModel.startRecording(sessionId)
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.isRecording).isTrue()
        assertThat(currentState?.recordingSessionId).isEqualTo(sessionId)
        assertThat(currentState?.statusText).contains("Recording")
    }

    @Test
    fun `should stop recording and reset state`() = runTest {
        // Given
        viewModel.startRecording("test-session")
        
        // When
        viewModel.stopRecording()
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.isRecording).isFalse()
        assertThat(currentState?.recordingSessionId).isNull()
        assertThat(currentState?.recordingDuration).isEqualTo(0L)
    }

    @Test
    fun `should update device connection status`() = runTest {
        // When
        viewModel.updateDeviceStatus(
            pcConnected = true,
            shimmerConnected = true,
            thermalConnected = false
        )
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.isPcConnected).isTrue()
        assertThat(currentState?.isShimmerConnected).isTrue()
        assertThat(currentState?.isThermalConnected).isFalse()
    }

    @Test
    fun `should handle error state correctly`() = runTest {
        // Given
        val errorMessage = "Connection failed"
        
        // When
        viewModel.showError(errorMessage)
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.errorMessage).isEqualTo(errorMessage)
        assertThat(currentState?.showErrorDialog).isTrue()
    }

    @Test
    fun `should clear error state`() = runTest {
        // Given
        viewModel.showError("Test error")
        
        // When
        viewModel.clearError()
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.errorMessage).isNull()
        assertThat(currentState?.showErrorDialog).isFalse()
    }

    @Test
    fun `should update battery status`() = runTest {
        // Given
        val batteryLevel = 75
        
        // When
        viewModel.updateBatteryStatus(batteryLevel)
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.batteryLevel).isEqualTo(batteryLevel)
    }

    @Test
    fun `should handle streaming state updates`() = runTest {
        // Given
        val frameRate = 30
        val dataSize = "2.5 MB/s"
        
        // When
        viewModel.updateStreamingStatus(true, frameRate, dataSize)
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.isStreaming).isTrue()
        assertThat(currentState?.streamingFrameRate).isEqualTo(frameRate)
        assertThat(currentState?.streamingDataSize).isEqualTo(dataSize)
    }

    @Test
    fun `should update recording duration during active recording`() = runTest {
        // Given
        viewModel.startRecording("test-session")
        val duration = 15000L
        
        // When
        viewModel.updateRecordingDuration(duration)
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.recordingDuration).isEqualTo(duration)
    }

    @Test
    fun `should toggle manual controls visibility`() = runTest {
        // Given
        val initialState = viewModel.uiState.value
        val initialVisibility = initialState?.showManualControls ?: false
        
        // When
        viewModel.toggleManualControls()
        
        // Then
        val currentState = viewModel.uiState.value
        assertThat(currentState?.showManualControls).isEqualTo(!initialVisibility)
    }

    @Test
    fun `should notify observer when state changes`() = runTest {
        // When
        viewModel.startRecording("test-session")
        
        // Then
        verify(atLeast = 2) { uiStateObserver.onChanged(any()) }
    }
}