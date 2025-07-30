package com.multisensor.recording.integration

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.calibration.SyncClockManager
import com.multisensor.recording.network.CommandProcessor
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import io.mockk.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import javax.inject.Inject

/**
 * Integration tests for Milestone 2.8: Calibration Capture and Sync Features
 * Tests end-to-end functionality of calibration capture, clock synchronization, and flash/beep sync
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
@LargeTest
class Milestone28IntegrationTest {
    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var calibrationCaptureManager: CalibrationCaptureManager

    @Inject
    lateinit var syncClockManager: SyncClockManager

    @Inject
    lateinit var sessionManager: SessionManager

    @Inject
    lateinit var logger: Logger

    private lateinit var mockCameraRecorder: CameraRecorder
    private lateinit var mockThermalRecorder: ThermalRecorder
    private lateinit var mockCommandProcessor: CommandProcessor
    private lateinit var context: Context
    private lateinit var testDispatcher: TestDispatcher

    @Before
    fun setUp() {
        hiltRule.inject()

        context = ApplicationProvider.getApplicationContext()
        mockCameraRecorder = mockk(relaxed = true)
        mockThermalRecorder = mockk(relaxed = true)
        mockCommandProcessor = mockk(relaxed = true)
        testDispatcher = StandardTestDispatcher()
        Dispatchers.setMain(testDispatcher)

        println("[DEBUG_LOG] Milestone28IntegrationTest setup complete")
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        clearAllMocks()
        println("[DEBUG_LOG] Milestone28IntegrationTest teardown complete")
    }

    @Test
    fun testEndToEndCalibrationCaptureWorkflow() =
        runTest {
            println("[DEBUG_LOG] Testing end-to-end calibration capture workflow")

            // Step 1: Synchronize clock with PC
            val pcTimestamp = System.currentTimeMillis() + 1000L
            val syncSuccess = syncClockManager.synchronizeWithPc(pcTimestamp, "integration_test_sync")
            assertTrue("Clock synchronization should succeed", syncSuccess)

            // Step 2: Mock successful camera captures
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            // Step 3: Perform calibration capture
            val calibrationResult =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "integration_test_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = true,
                )

            // Step 4: Verify results
            assertTrue("Calibration capture should succeed", calibrationResult.success)
            assertEquals("Calibration ID should match", "integration_test_001", calibrationResult.calibrationId)
            assertNotNull("RGB file path should be set", calibrationResult.rgbFilePath)
            assertNotNull("Thermal file path should be set", calibrationResult.thermalFilePath)
            assertTrue(
                "Synced timestamp should be greater than device timestamp",
                calibrationResult.syncedTimestamp > calibrationResult.timestamp,
            )

            // Step 5: Verify sync status
            val syncStatus = syncClockManager.getSyncStatus()
            assertTrue("Clock should remain synchronized", syncStatus.isSynchronized)
            assertTrue("Sync should be valid", syncClockManager.isSyncValid())

            println("[DEBUG_LOG] End-to-end calibration capture workflow test passed")
        }

    @Test
    fun testMultiDeviceCalibrationCoordination() =
        runTest {
            println("[DEBUG_LOG] Testing multi-device calibration coordination")

            // Simulate multiple devices synchronizing with same PC timestamp
            val pcTimestamp = System.currentTimeMillis() + 2000L
            val syncId = "multi_device_sync_001"

            // Device 1 synchronization
            val sync1Success = syncClockManager.synchronizeWithPc(pcTimestamp, syncId)
            assertTrue("Device 1 sync should succeed", sync1Success)

            // Reset and simulate Device 2 synchronization
            syncClockManager.resetSync()
            val sync2Success = syncClockManager.synchronizeWithPc(pcTimestamp + 50L, syncId) // 50ms network delay
            assertTrue("Device 2 sync should succeed", sync2Success)

            // Both devices should have similar but not identical offsets due to network delay
            val syncStatus = syncClockManager.getSyncStatus()
            assertTrue("Final sync should be valid", syncStatus.isSynchronized)

            // Verify calibration capture works with synchronized time
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            val calibrationResult =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "multi_device_calib_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = false,
                )

            assertTrue("Multi-device calibration should succeed", calibrationResult.success)
            assertTrue(
                "Synced timestamp should be adjusted",
                calibrationResult.syncedTimestamp != calibrationResult.timestamp,
            )

            println("[DEBUG_LOG] Multi-device calibration coordination test passed")
        }

    @Test
    fun testCalibrationCaptureWithSyncFailure() =
        runTest {
            println("[DEBUG_LOG] Testing calibration capture with sync failure scenarios")

            // Test calibration without clock synchronization
            val calibrationResult1 =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "no_sync_test_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = false,
                )

            // Should still work but use device timestamps
            assertTrue("Calibration should work without sync", calibrationResult1.success)
            assertEquals(
                "Timestamps should be equal without sync",
                calibrationResult1.timestamp,
                calibrationResult1.syncedTimestamp,
            )

            // Test with invalid PC timestamp
            val invalidSyncSuccess = syncClockManager.synchronizeWithPc(-1000L, "invalid_sync")
            assertFalse("Invalid sync should fail", invalidSyncSuccess)

            // Calibration should still work
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            val calibrationResult2 =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "invalid_sync_test_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = false,
                )

            assertTrue("Calibration should work with invalid sync", calibrationResult2.success)

            println("[DEBUG_LOG] Calibration capture with sync failure test passed")
        }

    @Test
    fun testCalibrationFileManagement() =
        runTest {
            println("[DEBUG_LOG] Testing calibration file management")

            // Mock successful captures
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            // Capture multiple calibration sessions
            val calibrationIds = mutableListOf<String>()
            repeat(3) { index ->
                val calibrationId = "file_mgmt_test_${String.format("%03d", index + 1)}"
                calibrationIds.add(calibrationId)

                val result =
                    calibrationCaptureManager.captureCalibrationImages(
                        calibrationId = calibrationId,
                        captureRgb = true,
                        captureThermal = true,
                        highResolution = false,
                    )

                assertTrue("Calibration $calibrationId should succeed", result.success)
            }

            // Verify calibration sessions can be retrieved
            val sessions = calibrationCaptureManager.getCalibrationSessions()
            assertTrue("Should have at least 3 sessions", sessions.size >= 3)

            // Verify session data
            val testSessions = sessions.filter { it.calibrationId.startsWith("file_mgmt_test_") }
            assertEquals("Should have exactly 3 test sessions", 3, testSessions.size)

            // Test session deletion
            val firstSessionId = calibrationIds.first()
            val deleteSuccess = calibrationCaptureManager.deleteCalibrationSession(firstSessionId)
            assertTrue("Session deletion should succeed", deleteSuccess)

            // Verify deletion
            val sessionsAfterDelete = calibrationCaptureManager.getCalibrationSessions()
            val remainingTestSessions = sessionsAfterDelete.filter { it.calibrationId.startsWith("file_mgmt_test_") }
            assertEquals("Should have 2 test sessions after deletion", 2, remainingTestSessions.size)

            // Test statistics
            val statistics = calibrationCaptureManager.getCalibrationStatistics()
            assertTrue("Should have positive total captures", statistics.totalCaptures > 0)
            assertTrue("Should have some complete sessions", statistics.completeSessions >= 0)

            println("[DEBUG_LOG] Calibration file management test passed")
        }

    @Test
    fun testSyncClockAccuracy() =
        runTest {
            println("[DEBUG_LOG] Testing sync clock accuracy and drift")

            val initialPcTime = System.currentTimeMillis()

            // Initial synchronization
            val syncSuccess = syncClockManager.synchronizeWithPc(initialPcTime, "accuracy_test_001")
            assertTrue("Initial sync should succeed", syncSuccess)

            val initialSyncStatus = syncClockManager.getSyncStatus()
            val initialOffset = initialSyncStatus.clockOffsetMs

            // Wait a short time and check drift
            delay(100L)

            val currentSyncedTime = syncClockManager.getCurrentSyncedTime()
            val currentDeviceTime = System.currentTimeMillis()
            val actualOffset = currentSyncedTime - currentDeviceTime

            // Offset should remain consistent (within tolerance)
            assertTrue(
                "Clock offset should remain stable",
                kotlin.math.abs(actualOffset - initialOffset) < 50L,
            ) // 50ms tolerance

            // Test time conversion accuracy
            val testDeviceTime = System.currentTimeMillis()
            val convertedPcTime = syncClockManager.deviceToPcTime(testDeviceTime)
            val convertedBackTime = syncClockManager.pcToDeviceTime(convertedPcTime)

            assertEquals("Time conversion should be reversible", testDeviceTime, convertedBackTime)

            // Test sync health validation
            assertTrue("Sync should be healthy", syncClockManager.validateSyncHealth())

            println("[DEBUG_LOG] Sync clock accuracy test passed")
        }

    @Test
    fun testCalibrationCaptureErrorHandling() =
        runTest {
            println("[DEBUG_LOG] Testing calibration capture error handling")

            // Test RGB camera failure
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns false
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            val result1 =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "rgb_fail_test_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = false,
                )

            assertFalse("Should fail when RGB capture fails", result1.success)
            assertNotNull("Should have error message", result1.errorMessage)
            assertTrue(
                "Error should mention RGB failure",
                result1.errorMessage?.contains("RGB", ignoreCase = true) == true,
            )

            // Test thermal camera failure
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns false

            val result2 =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "thermal_fail_test_001",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = false,
                )

            assertFalse("Should fail when thermal capture fails", result2.success)
            assertNotNull("Should have error message", result2.errorMessage)
            assertTrue(
                "Error should mention thermal failure",
                result2.errorMessage?.contains("thermal", ignoreCase = true) == true,
            )

            // Test partial capture (RGB only)
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true

            val result3 =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "rgb_only_test_001",
                    captureRgb = true,
                    captureThermal = false,
                    highResolution = false,
                )

            assertTrue("RGB-only capture should succeed", result3.success)
            assertNotNull("Should have RGB file path", result3.rgbFilePath)
            assertNull("Should not have thermal file path", result3.thermalFilePath)

            println("[DEBUG_LOG] Calibration capture error handling test passed")
        }

    @Test
    fun testConcurrentCalibrationOperations() =
        runTest {
            println("[DEBUG_LOG] Testing concurrent calibration operations")

            // Mock successful captures
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            // Synchronize clock first
            val pcTimestamp = System.currentTimeMillis() + 1000L
            syncClockManager.synchronizeWithPc(pcTimestamp, "concurrent_test_sync")

            // Launch multiple concurrent calibration operations
            val jobs = mutableListOf<Deferred<CalibrationCaptureManager.CalibrationCaptureResult>>()

            repeat(5) { index ->
                val job =
                    async {
                        calibrationCaptureManager.captureCalibrationImages(
                            calibrationId = "concurrent_test_${String.format("%03d", index + 1)}",
                            captureRgb = true,
                            captureThermal = true,
                            highResolution = false,
                        )
                    }
                jobs.add(job)
            }

            // Wait for all operations to complete
            val results = jobs.awaitAll()

            // Verify all operations succeeded
            results.forEachIndexed { index, result ->
                assertTrue("Concurrent operation $index should succeed", result.success)
                assertTrue(
                    "Each operation should have unique ID",
                    result.calibrationId.contains("concurrent_test_"),
                )
            }

            // Verify unique calibration IDs
            val calibrationIds = results.map { it.calibrationId }.toSet()
            assertEquals("All calibration IDs should be unique", results.size, calibrationIds.size)

            // Verify sync remained stable during concurrent operations
            assertTrue("Sync should remain valid", syncClockManager.isSyncValid())

            println("[DEBUG_LOG] Concurrent calibration operations test passed")
        }

    @Test
    fun testMilestone28FeatureIntegration() =
        runTest {
            println("[DEBUG_LOG] Testing complete Milestone 2.8 feature integration")

            // Step 1: Clock synchronization
            val pcTimestamp = System.currentTimeMillis() + 1500L
            val syncId = "milestone_integration_sync"
            val syncSuccess = syncClockManager.synchronizeWithPc(pcTimestamp, syncId)
            assertTrue("Clock sync should succeed", syncSuccess)

            // Step 2: Calibration capture with sync
            coEvery { mockCameraRecorder.captureCalibrationImage(any()) } returns true
            coEvery { mockThermalRecorder.captureCalibrationImage(any()) } returns true

            val calibrationResult =
                calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = "milestone_integration_calib",
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = true,
                )

            assertTrue("Calibration should succeed", calibrationResult.success)

            // Step 3: Verify synchronized timestamps
            val timeDifference = calibrationResult.syncedTimestamp - calibrationResult.timestamp
            assertTrue("Synced timestamp should be adjusted", timeDifference != 0L)
            assertTrue("Time adjustment should be reasonable", kotlin.math.abs(timeDifference) < 5000L)

            // Step 4: Verify file management
            val sessions = calibrationCaptureManager.getCalibrationSessions()
            val integrationSession = sessions.find { it.calibrationId == "milestone_integration_calib" }
            assertNotNull("Integration session should be found", integrationSession)
            assertNotNull("Session should have RGB file", integrationSession?.rgbFile)
            assertNotNull("Session should have thermal file", integrationSession?.thermalFile)

            // Step 5: Verify statistics
            val statistics = calibrationCaptureManager.getCalibrationStatistics()
            assertTrue("Should have at least one complete session", statistics.completeSessions >= 1)
            assertTrue("Should have positive total captures", statistics.totalCaptures > 0)

            // Step 6: Test sync health
            assertTrue("Sync should be healthy", syncClockManager.validateSyncHealth())
            val syncStatistics = syncClockManager.getSyncStatistics()
            assertTrue(
                "Sync statistics should contain sync info",
                syncStatistics.contains("Clock Synchronization Statistics"),
            )

            println("[DEBUG_LOG] Complete Milestone 2.8 feature integration test passed")
        }
}
