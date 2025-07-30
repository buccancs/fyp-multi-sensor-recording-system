package com.multisensor.recording.ui

import org.junit.Test
import org.junit.Assert.*

/**
 * Unit tests for MainUiState computed properties and behavior
 * 
 * These tests ensure that the centralized UI state management works correctly
 * and that computed properties return expected values based on state combinations.
 */
class MainUiStateTest {

    @Test
    fun `canStartRecording returns true when system is ready and not recording`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            isLoadingRecording = false,
            isPcConnected = true
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to start recording when system is ready", state.canStartRecording)
    }

    @Test
    fun `canStartRecording returns false when not initialized`() {
        // Given
        val state = MainUiState(
            isInitialized = false,
            isRecording = false,
            isLoadingRecording = false,
            isPcConnected = true
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to start recording when not initialized", state.canStartRecording)
    }

    @Test
    fun `canStartRecording returns false when already recording`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = true,
            isLoadingRecording = false,
            isPcConnected = true
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to start recording when already recording", state.canStartRecording)
    }

    @Test
    fun `canStartRecording returns false when loading`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            isLoadingRecording = true,
            isPcConnected = true
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to start recording when loading", state.canStartRecording)
    }

    @Test
    fun `canStartRecording returns true with manual controls when PC not connected`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            isLoadingRecording = false,
            isPcConnected = false,
            showManualControls = true
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to start recording with manual controls", state.canStartRecording)
    }

    @Test
    fun `canStopRecording returns true when recording and not loading`() {
        // Given
        val state = MainUiState(
            isRecording = true,
            isLoadingRecording = false
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to stop recording when recording", state.canStopRecording)
    }

    @Test
    fun `canStopRecording returns false when not recording`() {
        // Given
        val state = MainUiState(
            isRecording = false,
            isLoadingRecording = false
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to stop recording when not recording", state.canStopRecording)
    }

    @Test
    fun `canStopRecording returns false when loading`() {
        // Given
        val state = MainUiState(
            isRecording = true,
            isLoadingRecording = true
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to stop recording when loading", state.canStopRecording)
    }

    @Test
    fun `canRunCalibration returns true when system ready and not busy`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            isCalibrationRunning = false,
            isLoadingCalibration = false
        )

        // When & Then
        assertTrue("[DEBUG_LOG] Should be able to run calibration when system is ready", state.canRunCalibration)
    }

    @Test
    fun `canRunCalibration returns false when recording`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = true,
            isCalibrationRunning = false,
            isLoadingCalibration = false
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to run calibration when recording", state.canRunCalibration)
    }

    @Test
    fun `canRunCalibration returns false when calibration already running`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            isCalibrationRunning = true,
            isLoadingCalibration = false
        )

        // When & Then
        assertFalse("[DEBUG_LOG] Should not be able to run calibration when already running", state.canRunCalibration)
    }

    @Test
    fun `systemHealthStatus returns INITIALIZING when not initialized`() {
        // Given
        val state = MainUiState(isInitialized = false)

        // When & Then
        assertEquals("[DEBUG_LOG] System health should be INITIALIZING", 
            SystemHealthStatus.INITIALIZING, state.systemHealthStatus)
    }

    @Test
    fun `systemHealthStatus returns ERROR when error message present`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            errorMessage = "Test error"
        )

        // When & Then
        assertEquals("[DEBUG_LOG] System health should be ERROR when error present", 
            SystemHealthStatus.ERROR, state.systemHealthStatus)
    }

    @Test
    fun `systemHealthStatus returns RECORDING when recording`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = true,
            errorMessage = null
        )

        // When & Then
        assertEquals("[DEBUG_LOG] System health should be RECORDING when recording", 
            SystemHealthStatus.RECORDING, state.systemHealthStatus)
    }

    @Test
    fun `systemHealthStatus returns READY when PC and sensors connected`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            errorMessage = null,
            isPcConnected = true,
            isShimmerConnected = true
        )

        // When & Then
        assertEquals("[DEBUG_LOG] System health should be READY when all connected", 
            SystemHealthStatus.READY, state.systemHealthStatus)
    }

    @Test
    fun `systemHealthStatus returns PARTIAL_CONNECTION when only PC connected`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            errorMessage = null,
            isPcConnected = true,
            isShimmerConnected = false,
            isThermalConnected = false
        )

        // When & Then
        assertEquals("[DEBUG_LOG] System health should be PARTIAL_CONNECTION", 
            SystemHealthStatus.PARTIAL_CONNECTION, state.systemHealthStatus)
    }

    @Test
    fun `systemHealthStatus returns DISCONNECTED when nothing connected`() {
        // Given
        val state = MainUiState(
            isInitialized = true,
            isRecording = false,
            errorMessage = null,
            isPcConnected = false,
            isShimmerConnected = false,
            isThermalConnected = false
        )

        // When & Then
        assertEquals("[DEBUG_LOG] System health should be DISCONNECTED", 
            SystemHealthStatus.DISCONNECTED, state.systemHealthStatus)
    }

    @Test
    fun `battery status enum values are correct`() {
        // Test all battery status values
        val statuses = BatteryStatus.values()
        
        assertTrue("[DEBUG_LOG] Should contain UNKNOWN status", statuses.contains(BatteryStatus.UNKNOWN))
        assertTrue("[DEBUG_LOG] Should contain CHARGING status", statuses.contains(BatteryStatus.CHARGING))
        assertTrue("[DEBUG_LOG] Should contain DISCHARGING status", statuses.contains(BatteryStatus.DISCHARGING))
        assertTrue("[DEBUG_LOG] Should contain NOT_CHARGING status", statuses.contains(BatteryStatus.NOT_CHARGING))
        assertTrue("[DEBUG_LOG] Should contain FULL status", statuses.contains(BatteryStatus.FULL))
    }

    @Test
    fun `shimmer device info data class works correctly`() {
        // Given
        val deviceInfo = ShimmerDeviceInfo(
            deviceName = "Shimmer3-ABC123",
            macAddress = "00:11:22:33:44:55",
            isConnected = true,
            signalStrength = -65,
            firmwareVersion = "1.2.3"
        )

        // When & Then
        assertEquals("[DEBUG_LOG] Device name should match", "Shimmer3-ABC123", deviceInfo.deviceName)
        assertEquals("[DEBUG_LOG] MAC address should match", "00:11:22:33:44:55", deviceInfo.macAddress)
        assertTrue("[DEBUG_LOG] Should be connected", deviceInfo.isConnected)
        assertEquals("[DEBUG_LOG] Signal strength should match", -65, deviceInfo.signalStrength)
        assertEquals("[DEBUG_LOG] Firmware version should match", "1.2.3", deviceInfo.firmwareVersion)
    }

    @Test
    fun `session display info data class works correctly`() {
        // Given
        val sessionInfo = SessionDisplayInfo(
            sessionId = "session_123",
            startTime = 1640995200000L, // 2022-01-01 00:00:00
            duration = 3661000L, // 1h 1m 1s
            deviceCount = 3,
            recordingMode = "multi_sensor",
            status = "completed"
        )

        // When & Then
        assertEquals("[DEBUG_LOG] Session ID should match", "session_123", sessionInfo.sessionId)
        assertEquals("[DEBUG_LOG] Start time should match", 1640995200000L, sessionInfo.startTime)
        assertEquals("[DEBUG_LOG] Duration should match", 3661000L, sessionInfo.duration)
        assertEquals("[DEBUG_LOG] Device count should match", 3, sessionInfo.deviceCount)
        assertEquals("[DEBUG_LOG] Recording mode should match", "multi_sensor", sessionInfo.recordingMode)
        assertEquals("[DEBUG_LOG] Status should match", "completed", sessionInfo.status)
    }
}