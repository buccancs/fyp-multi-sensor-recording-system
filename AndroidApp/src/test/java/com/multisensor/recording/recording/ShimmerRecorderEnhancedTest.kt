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
 * Enhanced unit tests for ShimmerRecorder with new features
 * Tests all new functionality including enhanced sensor configuration,
 * data quality metrics, connection management, and real-time parameter updates
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class ShimmerRecorderEnhancedTest {
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
            println("[DEBUG_LOG] Testing enhanced ShimmerRecorder initialization")
            
            // When
            val result = shimmerRecorder.initialize()
            
            // Then
            assertTrue("ShimmerRecorder should initialize successfully", result)
            verify(exactly = 1) { mockLogger.info("Initializing ShimmerRecorder (stub implementation)...") }
        }

    @Test
    fun `scanAndPairDevices should return device list when successful`() =
        runTest {
            println("[DEBUG_LOG] Testing Shimmer device scanning functionality")
            
            // Given
            shimmerRecorder.initialize()
            
            // When
            val devices = shimmerRecorder.scanAndPairDevices()
            
            // Then
            assertNotNull("Device list should not be null", devices)
            assertTrue("Device list should be empty for mock environment", devices.isEmpty())
            verify { mockLogger.info("=== SHIMMER DEVICE DISCOVERY DIAGNOSTIC ===") }
        }

    @Test
    fun `connectDevices should handle empty device list gracefully`() =
        runTest {
            println("[DEBUG_LOG] Testing connection with empty device list")
            
            // Given
            shimmerRecorder.initialize()
            val emptyDeviceList = emptyList<String>()
            
            // When
            val result = shimmerRecorder.connectDevices(emptyDeviceList)
            
            // Then
            assertFalse("Connection should return false for empty device list", result)
        }

    @Test
    fun `setEnabledChannels should validate device existence`() =
        runTest {
            println("[DEBUG_LOG] Testing sensor channel configuration")
            
            // Given
            val deviceId = "test_device"
            val channels = setOf(SensorChannel.GSR, SensorChannel.PPG)
            
            // When
            val result = shimmerRecorder.setEnabledChannels(deviceId, channels)
            
            // Then
            assertFalse("Should return false for non-existent device", result)
            verify { mockLogger.error("Device not found: $deviceId") }
        }

    @Test
    fun `setSamplingRate should validate parameters`() =
        runTest {
            println("[DEBUG_LOG] Testing sampling rate configuration")
            
            // Given
            val deviceId = "test_device"
            val samplingRate = 51.2
            
            // When
            val result = shimmerRecorder.setSamplingRate(deviceId, samplingRate)
            
            // Then
            assertFalse("Should return false for non-existent device", result)
            verify { mockLogger.error("Device not found: $deviceId") }
        }

    @Test
    fun `setGSRRange should validate range parameters`() =
        runTest {
            println("[DEBUG_LOG] Testing GSR range configuration")
            
            // Given
            val deviceId = "test_device"
            val validGsrRange = 2
            val invalidGsrRange = 10
            
            // When - valid range
            val result1 = shimmerRecorder.setGSRRange(deviceId, validGsrRange)
            
            // When - invalid range
            val result2 = shimmerRecorder.setGSRRange(deviceId, invalidGsrRange)
            
            // Then
            assertFalse("Should return false for non-existent device", result1)
            assertFalse("Should return false for invalid GSR range", result2)
            verify { mockLogger.error("Device not found: $deviceId") }
        }

    @Test
    fun `setAccelRange should validate range parameters`() =
        runTest {
            println("[DEBUG_LOG] Testing accelerometer range configuration")
            
            // Given
            val deviceId = "test_device"
            val validAccelRange = 4
            val invalidAccelRange = 3
            
            // When - valid range
            val result1 = shimmerRecorder.setAccelRange(deviceId, validAccelRange)
            
            // When - invalid range
            val result2 = shimmerRecorder.setAccelRange(deviceId, invalidAccelRange)
            
            // Then
            assertFalse("Should return false for non-existent device", result1)
            assertFalse("Should return false for invalid accelerometer range", result2)
        }

    @Test
    fun `getDeviceInformation should return null for non-existent device`() =
        runTest {
            println("[DEBUG_LOG] Testing device information retrieval")
            
            // Given
            val deviceId = "non_existent_device"
            
            // When
            val deviceInfo = shimmerRecorder.getDeviceInformation(deviceId)
            
            // Then
            assertNull("Should return null for non-existent device", deviceInfo)
        }

    @Test
    fun `getDataQualityMetrics should return null for non-existent device`() =
        runTest {
            println("[DEBUG_LOG] Testing data quality metrics")
            
            // Given
            val deviceId = "non_existent_device"
            
            // When
            val metrics = shimmerRecorder.getDataQualityMetrics(deviceId)
            
            // Then
            assertNull("Should return null for non-existent device", metrics)
        }

    @Test
    fun `enableClockSync should handle non-existent device gracefully`() =
        runTest {
            println("[DEBUG_LOG] Testing clock synchronization")
            
            // Given
            val deviceId = "non_existent_device"
            
            // When
            val result = shimmerRecorder.enableClockSync(deviceId, true)
            
            // Then
            assertFalse("Should return false for non-existent device", result)
            verify { mockLogger.error("Device or Shimmer instance not found: $deviceId") }
        }

    @Test
    fun `setEXGConfiguration should handle non-existent device gracefully`() =
        runTest {
            println("[DEBUG_LOG] Testing EXG configuration")
            
            // Given
            val deviceId = "non_existent_device"
            
            // When
            val result = shimmerRecorder.setEXGConfiguration(deviceId, true, false)
            
            // Then
            assertFalse("Should return false for non-existent device", result)
            verify { mockLogger.error("Device or Shimmer instance not found: $deviceId") }
        }

    @Test
    fun `startSDLogging should handle no connected devices`() =
        runTest {
            println("[DEBUG_LOG] Testing SD logging start with no devices")
            
            // When
            val result = shimmerRecorder.startSDLogging()
            
            // Then
            assertFalse("Should return false when no devices connected", result)
            verify { mockLogger.info("No connected Shimmer devices found for SD logging") }
        }

    @Test
    fun `stopSDLogging should handle no connected devices`() =
        runTest {
            println("[DEBUG_LOG] Testing SD logging stop with no devices")
            
            // When
            val result = shimmerRecorder.stopSDLogging()
            
            // Then
            assertFalse("Should return false when no devices connected", result)
            verify { mockLogger.info("No connected Shimmer devices found for stopping SD logging") }
        }

    @Test
    fun `disconnectAllDevices should succeed even with no devices`() =
        runTest {
            println("[DEBUG_LOG] Testing disconnect all devices")
            
            // When
            val result = shimmerRecorder.disconnectAllDevices()
            
            // Then
            assertTrue("Should return true even with no devices to disconnect", result)
            verify { mockLogger.info("Disconnecting from 0 devices...") }
        }

    @Test
    fun `isAnyDeviceStreaming should return false when no devices connected`() {
        println("[DEBUG_LOG] Testing device streaming status check")
        
        // When
        val result = shimmerRecorder.isAnyDeviceStreaming()
        
        // Then
        assertFalse("Should return false when no devices connected", result)
    }

    @Test
    fun `isAnyDeviceSDLogging should return false when no devices connected`() {
        println("[DEBUG_LOG] Testing device SD logging status check")
        
        // When
        val result = shimmerRecorder.isAnyDeviceSDLogging()
        
        // Then
        assertFalse("Should return false when no devices connected", result)
    }

    @Test
    fun `getConnectedShimmerDevice should return null for non-existent device`() {
        println("[DEBUG_LOG] Testing connected device retrieval")
        
        // Given
        val macAddress = "00:11:22:33:44:55"
        
        // When
        val device = shimmerRecorder.getConnectedShimmerDevice(macAddress)
        
        // Then
        assertNull("Should return null for non-existent device", device)
    }

    @Test
    fun `getFirstConnectedShimmerDevice should return null when no devices connected`() {
        println("[DEBUG_LOG] Testing first connected device retrieval")
        
        // When
        val device = shimmerRecorder.getFirstConnectedShimmerDevice()
        
        // Then
        assertNull("Should return null when no devices connected", device)
    }

    @Test
    fun `getShimmerBluetoothManager should return null initially`() {
        println("[DEBUG_LOG] Testing Shimmer Bluetooth manager retrieval")
        
        // When
        val manager = shimmerRecorder.getShimmerBluetoothManager()
        
        // Then
        assertNull("Should return null when not initialized", manager)
    }

    @Test
    fun `DeviceInformation getDisplaySummary should format correctly`() {
        println("[DEBUG_LOG] Testing DeviceInformation display formatting")
        
        // Given
        val deviceInfo = ShimmerRecorder.DeviceInformation(
            deviceId = "test_device",
            macAddress = "00:11:22:33:44:55",
            deviceName = "Shimmer3-GSR+",
            firmwareVersion = "1.0.0",
            hardwareVersion = "3.0",
            batteryLevel = 85,
            connectionState = ShimmerDevice.ConnectionState.CONNECTED,
            isStreaming = false,
            configuration = null,
            samplesRecorded = 1000L,
            lastSampleTime = System.currentTimeMillis(),
            bluetoothType = "Classic",
            signalStrength = 80,
            totalConnectedTime = 60000L
        )
        
        // When
        val summary = deviceInfo.getDisplaySummary()
        
        // Then
        assertTrue("Summary should contain device name", summary.contains("Shimmer3-GSR+"))
        assertTrue("Summary should contain connection state", summary.contains("CONNECTED"))
        assertTrue("Summary should contain battery level", summary.contains("85%"))
        assertTrue("Summary should contain sample count", summary.contains("1000"))
    }

    @Test
    fun `DataQualityMetrics getDisplaySummary should format correctly`() {
        println("[DEBUG_LOG] Testing DataQualityMetrics display formatting")
        
        // Given
        val metrics = ShimmerRecorder.DataQualityMetrics(
            deviceId = "test_device",
            samplesAnalyzed = 100,
            averageSamplingRate = 51.2,
            signalQuality = "Good",
            batteryLevel = 85,
            connectionStability = "Stable",
            dataLossPercentage = 0.5
        )
        
        // When
        val summary = metrics.getDisplaySummary()
        
        // Then
        assertTrue("Summary should contain device ID", summary.contains("test_device"))
        assertTrue("Summary should contain sampling rate", summary.contains("51.2 Hz"))
        assertTrue("Summary should contain signal quality", summary.contains("Good"))
        assertTrue("Summary should contain battery level", summary.contains("85%"))
        assertTrue("Summary should contain connection stability", summary.contains("Stable"))
    }
}