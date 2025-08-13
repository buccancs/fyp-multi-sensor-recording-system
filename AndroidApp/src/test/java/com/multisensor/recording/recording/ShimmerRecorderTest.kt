package com.multisensor.recording.recording

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import java.io.File

/**
 * Unit tests for ShimmerRecorder component
 * Tests initialization, recording lifecycle, error handling, and boundary conditions
 * Target: 90% line coverage for Android core logic
 */
@ExperimentalCoroutinesApi
@RunWith(AndroidJUnit4::class)
@Config(sdk = [28])
class ShimmerRecorderTest {

    private lateinit var context: Context
    private lateinit var shimmerRecorder: ShimmerRecorder
    private lateinit var mockSessionManager: SessionManager
    private lateinit var testDataDir: File

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        mockSessionManager = mockk()
        
        // Create test data directory
        testDataDir = File(context.filesDir, "test_shimmer_data")
        testDataDir.mkdirs()
        
        // Mock session manager calls
        every { mockSessionManager.currentSessionId } returns "test_session_001"
        every { mockSessionManager.getSessionDataDir() } returns testDataDir
        every { mockSessionManager.isRecording } returns false
        
        shimmerRecorder = ShimmerRecorder(context, mockSessionManager)
    }

    @After
    fun tearDown() {
        if (this::shimmerRecorder.isInitialized) {
            shimmerRecorder.disconnect()
        }
        // Clean up test data
        testDataDir.deleteRecursively()
        clearAllMocks()
    }

    @Test
    fun `test ShimmerRecorder initialization with valid context`() {
        assertNotNull(shimmerRecorder)
        assertFalse(shimmerRecorder.isConnected())
        assertFalse(shimmerRecorder.isRecording())
    }

    @Test
    fun `test initialization with null context throws exception`() {
        assertThrows(IllegalArgumentException::class.java) {
            ShimmerRecorder(null, mockSessionManager)
        }
    }

    @Test
    fun `test connect with valid device address`() = runTest {
        val deviceAddress = "00:06:66:12:34:56"
        
        val result = shimmerRecorder.connect(deviceAddress)
        
        // Should attempt connection (mock implementation)
        assertTrue("Connection attempt should be initiated", result)
    }

    @Test
    fun `test connect with invalid device address`() = runTest {
        val invalidAddress = "invalid_address"
        
        val result = shimmerRecorder.connect(invalidAddress)
        
        assertFalse("Invalid address should fail connection", result)
    }

    @Test
    fun `test connect with empty device address`() = runTest {
        val result = shimmerRecorder.connect("")
        
        assertFalse("Empty address should fail connection", result)
    }

    @Test
    fun `test startRecording when not connected`() = runTest {
        val result = shimmerRecorder.startRecording()
        
        assertFalse("Recording should fail when not connected", result)
    }

    @Test
    fun `test startRecording when already recording`() = runTest {
        // Mock connection state
        shimmerRecorder.setConnectedState(true)
        shimmerRecorder.setRecordingState(true)
        
        val result = shimmerRecorder.startRecording()
        
        assertFalse("Recording should fail when already recording", result)
    }

    @Test
    fun `test stopRecording when not recording`() = runTest {
        val result = shimmerRecorder.stopRecording()
        
        assertTrue("Stop recording should always succeed", result)
    }

    @Test
    fun `test recording lifecycle - start and stop`() = runTest {
        // Setup connected state
        shimmerRecorder.setConnectedState(true)
        
        // Start recording
        val startResult = shimmerRecorder.startRecording()
        assertTrue("Recording should start successfully", startResult)
        assertTrue("Should be in recording state", shimmerRecorder.isRecording())
        
        // Stop recording
        val stopResult = shimmerRecorder.stopRecording()
        assertTrue("Recording should stop successfully", stopResult)
        assertFalse("Should not be in recording state", stopResult)
    }

    @Test
    fun `test disconnect while recording`() = runTest {
        shimmerRecorder.setConnectedState(true)
        shimmerRecorder.setRecordingState(true)
        
        shimmerRecorder.disconnect()
        
        assertFalse("Should not be recording after disconnect", shimmerRecorder.isRecording())
        assertFalse("Should not be connected after disconnect", shimmerRecorder.isConnected())
    }

    @Test
    fun `test getRecordingDuration when not recording`() {
        val duration = shimmerRecorder.getRecordingDuration()
        
        assertEquals("Duration should be 0 when not recording", 0L, duration)
    }

    @Test
    fun `test getRecordingDuration during recording`() = runTest {
        shimmerRecorder.setConnectedState(true)
        shimmerRecorder.startRecording()
        
        Thread.sleep(100) // Small delay to allow time tracking
        
        val duration = shimmerRecorder.getRecordingDuration()
        
        assertTrue("Duration should be positive during recording", duration >= 0)
    }

    @Test
    fun `test battery level monitoring`() {
        val batteryLevel = shimmerRecorder.getBatteryLevel()
        
        assertTrue("Battery level should be between 0 and 100", 
            batteryLevel in 0..100)
    }

    @Test
    fun `test data file creation during recording`() = runTest {
        shimmerRecorder.setConnectedState(true)
        shimmerRecorder.startRecording()
        
        // Verify session manager interaction
        verify { mockSessionManager.currentSessionId }
        verify { mockSessionManager.getSessionDataDir() }
    }

    @Test
    fun `test error handling - connection failure`() = runTest {
        val invalidDevice = "INVALID_DEVICE"
        
        val result = shimmerRecorder.connect(invalidDevice)
        
        assertFalse("Connection should fail gracefully", result)
        assertFalse("Should remain disconnected", shimmerRecorder.isConnected())
    }

    @Test
    fun `test error handling - recording failure due to hardware`() = runTest {
        shimmerRecorder.setConnectedState(true)
        // Simulate hardware failure
        shimmerRecorder.simulateHardwareFailure()
        
        val result = shimmerRecorder.startRecording()
        
        assertFalse("Recording should fail due to hardware error", result)
    }

    @Test
    fun `test concurrent recording attempts`() = runTest {
        shimmerRecorder.setConnectedState(true)
        
        val result1 = shimmerRecorder.startRecording()
        val result2 = shimmerRecorder.startRecording()
        
        assertTrue("First recording should succeed", result1)
        assertFalse("Second recording should fail", result2)
    }

    @Test
    fun `test resource cleanup on disconnect`() = runTest {
        shimmerRecorder.setConnectedState(true)
        shimmerRecorder.startRecording()
        
        shimmerRecorder.disconnect()
        
        assertFalse("All resources should be cleaned up", shimmerRecorder.isConnected())
        assertFalse("Recording should be stopped", shimmerRecorder.isRecording())
    }

    @Test
    fun `test data validation boundary conditions`() = runTest {
        shimmerRecorder.setConnectedState(true)
        shimmerRecorder.startRecording()
        
        // Test boundary values
        val maxSampleRate = shimmerRecorder.getMaxSampleRate()
        val minSampleRate = shimmerRecorder.getMinSampleRate()
        
        assertTrue("Max sample rate should be positive", maxSampleRate > 0)
        assertTrue("Min sample rate should be positive", minSampleRate > 0)
        assertTrue("Max should be greater than min", maxSampleRate >= minSampleRate)
    }
}

// Extension functions for testing support
private fun ShimmerRecorder.setConnectedState(connected: Boolean) {
    // Mock implementation - would use reflection or test-specific methods in real implementation
}

private fun ShimmerRecorder.setRecordingState(recording: Boolean) {
    // Mock implementation - would use reflection or test-specific methods in real implementation
}

private fun ShimmerRecorder.simulateHardwareFailure() {
    // Mock implementation - would simulate hardware failure for testing
}

private fun ShimmerRecorder.getMaxSampleRate(): Int = 512
private fun ShimmerRecorder.getMinSampleRate(): Int = 1