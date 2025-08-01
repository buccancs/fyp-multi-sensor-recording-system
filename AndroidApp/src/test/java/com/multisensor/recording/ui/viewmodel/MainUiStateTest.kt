package com.multisensor.recording.ui.viewmodel

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import com.multisensor.recording.testfixtures.UiStateTestFactory
import com.multisensor.recording.ui.BatteryStatus
import org.junit.Test

/**
 * Comprehensive unit tests for MainUiState data class
 * 
 * Test Categories:
 * - Default state initialization
 * - State transitions and immutability
 * - Business logic validation
 * - Edge cases and error scenarios
 */
class MainUiStateTest : BaseUnitTest() {

    @Test
    fun `MainUiState should initialize with correct default values`() {
        // Given & When
        val state = UiStateTestFactory.createMainUiState()

        // Then
        assertThat(state.statusText).isEqualTo("Ready")
        assertThat(state.isInitialized).isTrue()
        assertThat(state.isRecording).isFalse()
        assertThat(state.recordingDuration).isEqualTo(0L)
        assertThat(state.recordingSessionId).isNull()
        assertThat(state.isPcConnected).isFalse()
        assertThat(state.isShimmerConnected).isFalse()
        assertThat(state.isThermalConnected).isFalse()
        assertThat(state.batteryLevel).isEqualTo(85)
        assertThat(state.batteryStatus).isEqualTo(BatteryStatus.DISCHARGING)
        assertThat(state.showManualControls).isTrue()
        assertThat(state.showPermissionsButton).isFalse()
        assertThat(state.isCalibrationRunning).isFalse()
        assertThat(state.isStreaming).isFalse()
        assertThat(state.streamingFrameRate).isEqualTo(0)
        assertThat(state.streamingDataSize).isEmpty()
        assertThat(state.errorMessage).isNull()
        assertThat(state.showErrorDialog).isFalse()
        assertThat(state.isLoadingRecording).isFalse()
    }

    @Test
    fun `recording state should have correct values`() {
        // Given
        val sessionId = "test-session-123"
        val duration = 15000L

        // When
        val state = UiStateTestFactory.createRecordingState(sessionId, duration)

        // Then
        assertThat(state.statusText).isEqualTo("Recording...")
        assertThat(state.isRecording).isTrue()
        assertThat(state.recordingDuration).isEqualTo(duration)
        assertThat(state.recordingSessionId).isEqualTo(sessionId)
        assertThat(state.isPcConnected).isTrue()
        assertThat(state.isShimmerConnected).isTrue()
        assertThat(state.isThermalConnected).isTrue()
    }

    @Test
    fun `connected state should show all devices connected`() {
        // Given & When
        val state = UiStateTestFactory.createConnectedState()

        // Then
        assertThat(state.statusText).isEqualTo("All devices connected")
        assertThat(state.isPcConnected).isTrue()
        assertThat(state.isShimmerConnected).isTrue()
        assertThat(state.isThermalConnected).isTrue()
    }

    @Test
    fun `disconnected state should show no devices connected`() {
        // Given & When
        val state = UiStateTestFactory.createDisconnectedState()

        // Then
        assertThat(state.statusText).isEqualTo("Devices disconnected")
        assertThat(state.isPcConnected).isFalse()
        assertThat(state.isShimmerConnected).isFalse()
        assertThat(state.isThermalConnected).isFalse()
    }

    @Test
    fun `error state should display error information`() {
        // Given
        val errorMessage = "Connection failed"

        // When
        val state = UiStateTestFactory.createErrorState(errorMessage)

        // Then
        assertThat(state.statusText).isEqualTo("Error occurred")
        assertThat(state.errorMessage).isEqualTo(errorMessage)
        assertThat(state.showErrorDialog).isTrue()
    }

    @Test
    fun `streaming state should show streaming information`() {
        // Given
        val frameRate = 30
        val dataSize = "2.5 MB/s"

        // When
        val state = UiStateTestFactory.createStreamingState(frameRate, dataSize)

        // Then
        assertThat(state.statusText).isEqualTo("Streaming active")
        assertThat(state.isStreaming).isTrue()
        assertThat(state.streamingFrameRate).isEqualTo(frameRate)
        assertThat(state.streamingDataSize).isEqualTo(dataSize)
    }

    @Test
    fun `loading state should show loading indicators`() {
        // Given & When
        val state = UiStateTestFactory.createLoadingState()

        // Then
        assertThat(state.statusText).isEqualTo("Loading...")
        assertThat(state.isLoadingRecording).isTrue()
    }

    @Test
    fun `state should be immutable and support copy operations`() {
        // Given
        val originalState = UiStateTestFactory.createMainUiState()

        // When
        val modifiedState = originalState.copy(
            statusText = "Updated status",
            isRecording = true,
            recordingDuration = 5000L
        )

        // Then
        assertThat(originalState.statusText).isEqualTo("Ready")
        assertThat(originalState.isRecording).isFalse()
        assertThat(originalState.recordingDuration).isEqualTo(0L)

        assertThat(modifiedState.statusText).isEqualTo("Updated status")
        assertThat(modifiedState.isRecording).isTrue()
        assertThat(modifiedState.recordingDuration).isEqualTo(5000L)
    }

    @Test
    fun `battery status enum should handle all values`() {
        // Given
        val allBatteryStatuses = BatteryStatus.values()

        // When & Then
        allBatteryStatuses.forEach { status ->
            val state = UiStateTestFactory.createMainUiState(batteryStatus = status)
            assertThat(state.batteryStatus).isEqualTo(status)
        }
    }

    @Test
    fun `should handle edge case battery levels`() {
        // Given & When
        val lowBatteryState = UiStateTestFactory.createMainUiState(batteryLevel = 0)
        val fullBatteryState = UiStateTestFactory.createMainUiState(batteryLevel = 100)
        val invalidBatteryState = UiStateTestFactory.createMainUiState(batteryLevel = -1)

        // Then
        assertThat(lowBatteryState.batteryLevel).isEqualTo(0)
        assertThat(fullBatteryState.batteryLevel).isEqualTo(100)
        assertThat(invalidBatteryState.batteryLevel).isEqualTo(-1)
    }

    @Test
    fun `should handle long recording durations`() {
        // Given
        val longDuration = Long.MAX_VALUE / 2

        // When
        val state = UiStateTestFactory.createRecordingState(duration = longDuration)

        // Then
        assertThat(state.recordingDuration).isEqualTo(longDuration)
    }

    @Test
    fun `equals and hashCode should work correctly for data class`() {
        // Given
        val state1 = UiStateTestFactory.createMainUiState(statusText = "Test")
        val state2 = UiStateTestFactory.createMainUiState(statusText = "Test")
        val state3 = UiStateTestFactory.createMainUiState(statusText = "Different")

        // When & Then
        assertThat(state1).isEqualTo(state2)
        assertThat(state1.hashCode()).isEqualTo(state2.hashCode())
        assertThat(state1).isNotEqualTo(state3)
        assertThat(state1.hashCode()).isNotEqualTo(state3.hashCode())
    }
}