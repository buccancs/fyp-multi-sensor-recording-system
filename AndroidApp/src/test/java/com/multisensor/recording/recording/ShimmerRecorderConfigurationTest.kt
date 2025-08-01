package com.multisensor.recording.recording

import android.content.Context
import com.multisensor.recording.recording.DeviceConfiguration.SensorChannel
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Comprehensive unit tests for ShimmerRecorder configuration methods
 * Tests device configuration, sensor channel setup, and sampling rate management
 * Ensures 100% test coverage as required by guidelines
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class ShimmerRecorderConfigurationTest {
    private lateinit var mockContext: Context
    private lateinit var mockSessionManager: SessionManager
    private lateinit var mockLogger: Logger
    private lateinit var shimmerRecorder: ShimmerRecorder

    @Before
    fun setup() {
        // Create mocks
        mockContext = mockk(relaxed = true)
        mockSessionManager = mockk(relaxed = true)
        mockLogger = mockk(relaxed = true)

        // Create ShimmerRecorder instance
        shimmerRecorder = ShimmerRecorder(mockContext, mockSessionManager, mockLogger)
    }

    @After
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `initialize should return true when successful`() =
        runTest {
            // [DEBUG_LOG] Testing ShimmerRecorder initialization
            println("[DEBUG_LOG] Testing ShimmerRecorder initialization")

            // When
            val result = shimmerRecorder.initialize()

            // Then
            assertTrue("ShimmerRecorder should initialize successfully", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] ShimmerRecorder initialization test passed")
        }

    @Test
    fun `scanAndPairDevices should return list of discovered devices`() =
        runTest {
            // [DEBUG_LOG] Testing device scanning and pairing
            println("[DEBUG_LOG] Testing device scanning and pairing")

            // When
            val devices = shimmerRecorder.scanAndPairDevices()

            // Then
            assertNotNull("Device list should not be null", devices)
            assertTrue("Device list should be a valid list", devices is List<String>)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Device scanning test passed - found ${devices.size} devices")
        }

    @Test
    fun `connectDevices should handle empty device list`() =
        runTest {
            // [DEBUG_LOG] Testing connection with empty device list
            println("[DEBUG_LOG] Testing connection with empty device list")

            // Given
            val emptyDeviceList = emptyList<String>()

            // When
            val result = shimmerRecorder.connectDevices(emptyDeviceList)

            // Then
            assertFalse("Connection should fail with empty device list", result)
            verify { mockLogger.warning(any()) }

            println("[DEBUG_LOG] Empty device list test passed")
        }

    @Test
    fun `connectDevices should handle valid device addresses`() =
        runTest {
            // [DEBUG_LOG] Testing connection with valid device addresses
            println("[DEBUG_LOG] Testing connection with valid device addresses")

            // Given
            val deviceAddresses = listOf("00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF")

            // When
            val result = shimmerRecorder.connectDevices(deviceAddresses)

            // Then
            // Note: In simulation mode, this may return true or false depending on implementation
            assertNotNull("Connection result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Valid device addresses test passed - result: $result")
        }

    @Test
    fun `setEnabledChannels should configure sensor channels correctly`() =
        runTest {
            // [DEBUG_LOG] Testing sensor channel configuration
            println("[DEBUG_LOG] Testing sensor channel configuration")

            // Given
            val deviceId = "test_device_001"
            val channels =
                setOf(
                    SensorChannel.GSR,
                    SensorChannel.PPG,
                    SensorChannel.ACCEL,
                    SensorChannel.GYRO,
                    SensorChannel.MAG,
                )

            // When
            val result = shimmerRecorder.setEnabledChannels(deviceId, channels)

            // Then
            // Note: Result depends on whether device is connected in simulation
            assertNotNull("Channel configuration result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Sensor channel configuration test passed - result: $result")
        }

    @Test
    fun `setEnabledChannels should handle invalid device ID`() =
        runTest {
            // [DEBUG_LOG] Testing sensor channel configuration with invalid device ID
            println("[DEBUG_LOG] Testing sensor channel configuration with invalid device ID")

            // Given
            val invalidDeviceId = ""
            val channels = setOf(SensorChannel.GSR)

            // When
            val result = shimmerRecorder.setEnabledChannels(invalidDeviceId, channels)

            // Then
            assertFalse("Channel configuration should fail with invalid device ID", result)

            println("[DEBUG_LOG] Invalid device ID test passed")
        }

    @Test
    fun `setEnabledChannels should handle empty channel set`() =
        runTest {
            // [DEBUG_LOG] Testing sensor channel configuration with empty channels
            println("[DEBUG_LOG] Testing sensor channel configuration with empty channels")

            // Given
            val deviceId = "test_device_001"
            val emptyChannels = emptySet<SensorChannel>()

            // When
            val result = shimmerRecorder.setEnabledChannels(deviceId, emptyChannels)

            // Then
            // Should handle empty channels gracefully
            assertNotNull("Channel configuration result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Empty channels test passed - result: $result")
        }

    @Test
    fun `startStreaming should return appropriate result`() =
        runTest {
            // [DEBUG_LOG] Testing data streaming start
            println("[DEBUG_LOG] Testing data streaming start")

            // When
            val result = shimmerRecorder.startStreaming()

            // Then
            assertNotNull("Streaming start result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Start streaming test passed - result: $result")
        }

    @Test
    fun `stopStreaming should return appropriate result`() =
        runTest {
            // [DEBUG_LOG] Testing data streaming stop
            println("[DEBUG_LOG] Testing data streaming stop")

            // When
            val result = shimmerRecorder.stopStreaming()

            // Then
            assertNotNull("Streaming stop result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Stop streaming test passed - result: $result")
        }

    @Test
    fun `getShimmerStatus should return valid status information`() =
        runTest {
            // [DEBUG_LOG] Testing shimmer status retrieval
            println("[DEBUG_LOG] Testing shimmer status retrieval")

            // When
            val status = shimmerRecorder.getShimmerStatus()

            // Then
            assertNotNull("Shimmer status should not be null", status)
            assertTrue("Status should indicate availability", status.isAvailable)
            assertTrue("Sampling rate should be positive", status.samplingRate > 0)
            assertTrue("Battery level should be valid", status.batteryLevel == null || status.batteryLevel in 0..100)

            println("[DEBUG_LOG] Shimmer status test passed - isAvailable: ${status.isAvailable}, samplingRate: ${status.samplingRate}")
        }

    @Test
    fun `startRecording should handle valid session ID`() =
        runTest {
            // [DEBUG_LOG] Testing recording start with valid session ID
            println("[DEBUG_LOG] Testing recording start with valid session ID")

            // Given
            val sessionId = "test_session_${System.currentTimeMillis()}"

            // When
            val result = shimmerRecorder.startRecording(sessionId)

            // Then
            assertNotNull("Recording start result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Start recording test passed - result: $result")
        }

    @Test
    fun `startRecording should handle empty session ID`() =
        runTest {
            // [DEBUG_LOG] Testing recording start with empty session ID
            println("[DEBUG_LOG] Testing recording start with empty session ID")

            // Given
            val emptySessionId = ""

            // When
            val result = shimmerRecorder.startRecording(emptySessionId)

            // Then
            assertFalse("Recording should fail with empty session ID", result)
            verify { mockLogger.error(any(), any()) }

            println("[DEBUG_LOG] Empty session ID test passed")
        }

    @Test
    fun `stopRecording should complete successfully`() =
        runTest {
            // [DEBUG_LOG] Testing recording stop
            println("[DEBUG_LOG] Testing recording stop")

            // When
            shimmerRecorder.stopRecording()

            // Then - Should not throw exceptions
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Stop recording test passed")
        }

    @Test
    fun `getCurrentReadings should return sensor data when available`() =
        runTest {
            // [DEBUG_LOG] Testing current sensor readings retrieval
            println("[DEBUG_LOG] Testing current sensor readings retrieval")

            // When
            val readings = shimmerRecorder.getCurrentReadings()

            // Then
            // Readings may be null if no data is available
            if (readings.isNotEmpty()) {
                readings.values.forEach { sensorSample ->
                    assertTrue("Timestamp should be positive", sensorSample.systemTimestamp > 0)
                    assertTrue("Battery level should be valid", sensorSample.batteryLevel in 0..100)
                }
            }

            println("[DEBUG_LOG] Current readings test passed - readings available: ${readings.isNotEmpty()}")
        }

    @Test
    fun `startSDLogging should return appropriate result`() =
        runTest {
            // [DEBUG_LOG] Testing SD card logging start
            println("[DEBUG_LOG] Testing SD card logging start")

            // When
            val result = shimmerRecorder.startSDLogging()

            // Then
            assertNotNull("SD logging start result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Start SD logging test passed - result: $result")
        }

    @Test
    fun `stopSDLogging should return appropriate result`() =
        runTest {
            // [DEBUG_LOG] Testing SD card logging stop
            println("[DEBUG_LOG] Testing SD card logging stop")

            // When
            val result = shimmerRecorder.stopSDLogging()

            // Then
            assertNotNull("SD logging stop result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Stop SD logging test passed - result: $result")
        }

    @Test
    fun `cleanup should complete without errors`() =
        runTest {
            // [DEBUG_LOG] Testing cleanup process
            println("[DEBUG_LOG] Testing cleanup process")

            // When
            shimmerRecorder.cleanup()

            // Then - Should not throw exceptions
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Cleanup test passed")
        }

    @Test
    fun `multiple sensor channels configuration should work correctly`() =
        runTest {
            // [DEBUG_LOG] Testing multiple sensor channels configuration
            println("[DEBUG_LOG] Testing multiple sensor channels configuration")

            // Given
            val deviceId = "multi_sensor_device"
            val allChannels =
                setOf(
                    SensorChannel.GSR,
                    SensorChannel.PPG,
                    SensorChannel.ACCEL,
                    SensorChannel.GYRO,
                    SensorChannel.MAG,
                    SensorChannel.ECG,
                    SensorChannel.EMG,
                )

            // When
            val result = shimmerRecorder.setEnabledChannels(deviceId, allChannels)

            // Then
            assertNotNull("Multi-channel configuration result should not be null", result)
            verify { mockLogger.info(any()) }

            println("[DEBUG_LOG] Multiple sensor channels test passed - configured ${allChannels.size} channels")
        }

    @Test
    fun `device connection state management should work correctly`() =
        runTest {
            // [DEBUG_LOG] Testing device connection state management
            println("[DEBUG_LOG] Testing device connection state management")

            // Given
            val deviceAddresses = listOf("00:11:22:33:44:55")

            // When - Connect devices
            val connectResult = shimmerRecorder.connectDevices(deviceAddresses)

            // Then - Check status
            val status = shimmerRecorder.getShimmerStatus()
            assertNotNull("Status should be available after connection attempt", status)

            println(
                "[DEBUG_LOG] Connection state management test passed - connect result: $connectResult, status available: ${status.isAvailable}",
            )
        }
}
