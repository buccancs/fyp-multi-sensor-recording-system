package com.multisensor.recording.calibration

import android.content.Context
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import io.mockk.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File

/**
 * Unit tests for CalibrationCaptureManager
 * Tests calibration capture coordination, file management, and sync integration
 */
@RunWith(RobolectricTestRunner::class)
class CalibrationCaptureManagerTest {
    private lateinit var mockContext: Context
    private lateinit var mockCameraRecorder: CameraRecorder
    private lateinit var mockThermalRecorder: ThermalRecorder
    private lateinit var mockSyncClockManager: SyncClockManager
    private lateinit var mockThermalCameraSettings: ThermalCameraSettings
    private lateinit var mockLogger: Logger
    private lateinit var calibrationCaptureManager: CalibrationCaptureManager
    private lateinit var testDispatcher: TestDispatcher

    @Before
    fun setUp() {
        mockContext = mockk(relaxed = true)
        mockCameraRecorder = mockk(relaxed = true)
        mockThermalRecorder = mockk(relaxed = true)
        mockSyncClockManager = mockk(relaxed = true)
        mockThermalCameraSettings = mockk(relaxed = true)
        mockLogger = mockk(relaxed = true)
        testDispatcher = StandardTestDispatcher()
        Dispatchers.setMain(testDispatcher)

        // Mock external files directory
        val mockExternalDir = mockk<File>(relaxed = true)
        every { mockContext.getExternalFilesDir(any()) } returns mockExternalDir
        every { mockExternalDir.exists() } returns true
        every { mockExternalDir.absolutePath } returns "/test/external"

        calibrationCaptureManager =
            CalibrationCaptureManager(
                mockContext,
                mockCameraRecorder,
                mockThermalRecorder,
                mockSyncClockManager,
                mockThermalCameraSettings,
                mockLogger,
            )

        println("[DEBUG_LOG] CalibrationCaptureManagerTest setup complete")
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        clearAllMocks()
        println("[DEBUG_LOG] CalibrationCaptureManagerTest teardown complete")
    }

    @Test
    fun testCalibrationCaptureResultDataClass() {
        println("[DEBUG_LOG] Testing CalibrationCaptureResult data class")

        val result =
            CalibrationCaptureManager.CalibrationCaptureResult(
                success = true,
                calibrationId = "test_calib_001",
                rgbFilePath = "/test/rgb.jpg",
                thermalFilePath = "/test/thermal.png",
                timestamp = System.currentTimeMillis(),
                syncedTimestamp = System.currentTimeMillis() + 100,
            )

        assertTrue("Result should be successful", result.success)
        assertEquals("Calibration ID should match", "test_calib_001", result.calibrationId)
        assertNotNull("RGB file path should not be null", result.rgbFilePath)
        assertNotNull("Thermal file path should not be null", result.thermalFilePath)
        assertTrue("Timestamp should be positive", result.timestamp > 0)
        assertTrue("Synced timestamp should be positive", result.syncedTimestamp > 0)

        println("[DEBUG_LOG] CalibrationCaptureResult data class test passed")
    }

    @Test
    fun testSuccessfulDualCameraCapture() =
        runTest {
            println("[DEBUG_LOG] Testing successful dual camera capture")

            // Mock successful camera captures
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute calibration capture
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_dual_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = true,
                )

            // Verify results
            assertTrue("Capture should be successful", result.success)
            assertEquals("Calibration ID should match", "test_dual_001", result.calibrationId)
            assertNotNull("RGB file path should be set", result.rgbFilePath)
            assertNotNull("Thermal file path should be set", result.thermalFilePath)
            assertNull("Error message should be null", result.errorMessage)

            // Verify camera recorder calls
            coVerify { mockCameraRecorder.captureCalibrationImage(any()) }
            coVerify { mockThermalRecorder.captureCalibrationImage(any()) }
            verify { mockSyncClockManager.getSyncedTimestamp(any()) }

            println("[DEBUG_LOG] Successful dual camera capture test passed")
        }

    @Test
    fun testRgbOnlyCapture() =
        runTest {
            println("[DEBUG_LOG] Testing RGB-only capture")

            // Mock successful RGB capture
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute RGB-only calibration capture
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_rgb_001",
                    captureRgb = true,
                    captureThermal = false,
                    highResolution = true,
                )

            // Verify results
            assertTrue("Capture should be successful", result.success)
            assertEquals("Calibration ID should match", "test_rgb_001", result.calibrationId)
            assertNotNull("RGB file path should be set", result.rgbFilePath)
            assertNull("Thermal file path should be null", result.thermalFilePath)

            // Verify only RGB camera was called
            coVerify { mockCameraRecorder.captureCalibrationImage(any()) }
            coVerify(exactly = 0) { mockThermalRecorder.captureCalibrationImage(any()) }

            println("[DEBUG_LOG] RGB-only capture test passed")
        }

    @Test
    fun testThermalOnlyCapture() =
        runTest {
            println("[DEBUG_LOG] Testing thermal-only capture")

            // Mock successful thermal capture
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute thermal-only calibration capture
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_thermal_001",
                    captureRgb = false,
                    captureThermal = true,
                    highResolution = false,
                )

            // Verify results
            assertTrue("Capture should be successful", result.success)
            assertEquals("Calibration ID should match", "test_thermal_001", result.calibrationId)
            assertNull("RGB file path should be null", result.rgbFilePath)
            assertNotNull("Thermal file path should be set", result.thermalFilePath)

            // Verify only thermal camera was called
            coVerify(exactly = 0) { mockCameraRecorder.captureCalibrationImage(any()) }
            coVerify { mockThermalRecorder.captureCalibrationImage(any()) }

            println("[DEBUG_LOG] Thermal-only capture test passed")
        }

    @Test
    fun testCameraFailureHandling() =
        runTest {
            println("[DEBUG_LOG] Testing camera failure handling")

            // Mock camera failure
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns false
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute calibration capture with camera failure
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_failure_001",
                    captureRgb = true,
                    captureThermal = true,
                )

            // Verify failure is handled correctly
            assertFalse("Capture should fail when RGB camera fails", result.success)
            assertEquals("Calibration ID should still be set", "test_failure_001", result.calibrationId)

            println("[DEBUG_LOG] Camera failure handling test passed")
        }

    @Test
    fun testExceptionHandling() =
        runTest {
            println("[DEBUG_LOG] Testing exception handling")

            // Mock exception during capture
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } throws RuntimeException("Camera error")
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute calibration capture with exception
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_exception_001",
                    captureRgb = true,
                    captureThermal = false,
                )

            // Verify exception is handled gracefully
            assertFalse("Capture should fail when exception occurs", result.success)
            assertNotNull("Error message should be set", result.errorMessage)
            assertTrue("Error message should contain exception info", result.errorMessage!!.contains("Camera error"))

            println("[DEBUG_LOG] Exception handling test passed")
        }

    @Test
    fun testAutoGeneratedCalibrationId() =
        runTest {
            println("[DEBUG_LOG] Testing auto-generated calibration ID")

            // Mock successful capture
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute capture without providing calibration ID
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = null,
                    captureRgb = true,
                    captureThermal = false,
                )

            // Verify auto-generated ID
            assertTrue("Capture should be successful", result.success)
            assertNotNull("Calibration ID should be auto-generated", result.calibrationId)
            assertTrue("ID should start with 'calib_'", result.calibrationId.startsWith("calib_"))
            assertTrue("ID should contain timestamp", result.calibrationId.contains("_"))

            println("[DEBUG_LOG] Auto-generated calibration ID test passed")
        }

    @Test
    fun testSyncTimestampIntegration() =
        runTest {
            println("[DEBUG_LOG] Testing sync timestamp integration")

            val testTimestamp = 1234567890L
            val syncedTimestamp = 1234567990L

            // Mock sync clock manager
            every { mockSyncClockManager.getSyncedTimestamp(testTimestamp) } returns syncedTimestamp
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true

            // Execute capture
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_sync_001",
                    captureRgb = true,
                    captureThermal = false,
                )

            // Verify sync integration
            assertTrue("Capture should be successful", result.success)
            assertEquals("Synced timestamp should be used", syncedTimestamp, result.syncedTimestamp)

            // Verify sync clock manager was called
            verify { mockSyncClockManager.getSyncedTimestamp(any()) }

            println("[DEBUG_LOG] Sync timestamp integration test passed")
        }

    @Test
    fun testCalibrationStatistics() {
        println("[DEBUG_LOG] Testing calibration statistics")

        // Get initial statistics
        val stats = calibrationCaptureManager.getCalibrationStatistics()

        // Verify statistics structure
        assertNotNull("Statistics should not be null", stats)
        assertTrue("Total sessions should be non-negative", stats.totalSessions >= 0)
        assertTrue("Complete sessions should be non-negative", stats.completeSessions >= 0)
        assertTrue("RGB-only sessions should be non-negative", stats.rgbOnlySessions >= 0)
        assertTrue("Thermal-only sessions should be non-negative", stats.thermalOnlySessions >= 0)
        assertTrue("Total captures should be non-negative", stats.totalCaptures >= 0)

        println("[DEBUG_LOG] Statistics: $stats")
        println("[DEBUG_LOG] Calibration statistics test passed")
    }

    @Test
    fun testCalibrationSessionDataClass() {
        println("[DEBUG_LOG] Testing CalibrationSession data class")

        val mockRgbFile = mockk<File>(relaxed = true)
        val mockThermalFile = mockk<File>(relaxed = true)
        val timestamp = System.currentTimeMillis()

        val session =
            CalibrationCaptureManager.CalibrationSession(
                calibrationId = "test_session_001",
                rgbFile = mockRgbFile,
                thermalFile = mockThermalFile,
                timestamp = timestamp,
            )

        assertEquals("Calibration ID should match", "test_session_001", session.calibrationId)
        assertEquals("RGB file should match", mockRgbFile, session.rgbFile)
        assertEquals("Thermal file should match", mockThermalFile, session.thermalFile)
        assertEquals("Timestamp should match", timestamp, session.timestamp)

        println("[DEBUG_LOG] CalibrationSession data class test passed")
    }

    @Test
    fun testConcurrentCaptureOperations() =
        runTest {
            println("[DEBUG_LOG] Testing concurrent capture operations")

            // Mock successful captures with delays
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } coAnswers {
                delay(50)
                true
            }
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } coAnswers {
                delay(30)
                true
            }
            every { mockSyncClockManager.getSyncedTimestamp(any()) } returns System.currentTimeMillis()

            // Execute concurrent captures
            val startTime = System.currentTimeMillis()
            val result =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "test_concurrent_001",
                    captureRgb = true,
                    captureThermal = true,
                )
            val endTime = System.currentTimeMillis()

            // Verify concurrent execution (should be faster than sequential)
            assertTrue("Capture should be successful", result.success)
            val totalTime = endTime - startTime
            assertTrue("Concurrent execution should be faster than 80ms (50+30)", totalTime < 80)

            println("[DEBUG_LOG] Concurrent capture operations test passed")
        }
}
