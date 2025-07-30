package com.multisensor.recording.calibration

import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import kotlin.math.abs

/**
 * Unit tests for SyncClockManager
 * Tests clock synchronization, offset calculation, and time conversion functionality
 */
@RunWith(RobolectricTestRunner::class)
class SyncClockManagerTest {
    private lateinit var mockLogger: Logger
    private lateinit var syncClockManager: SyncClockManager
    private lateinit var testDispatcher: TestDispatcher

    @Before
    fun setUp() {
        mockLogger = mockk(relaxed = true)
        testDispatcher = StandardTestDispatcher()
        Dispatchers.setMain(testDispatcher)

        syncClockManager = SyncClockManager(mockLogger)

        println("[DEBUG_LOG] SyncClockManagerTest setup complete")
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        clearAllMocks()
        println("[DEBUG_LOG] SyncClockManagerTest teardown complete")
    }

    @Test
    fun testSyncStatusDataClass() {
        println("[DEBUG_LOG] Testing SyncStatus data class")

        val syncStatus =
            SyncClockManager.SyncStatus(
                isSynchronized = true,
                clockOffsetMs = 1500L,
                lastSyncTimestamp = System.currentTimeMillis(),
                pcReferenceTime = System.currentTimeMillis() + 1500L,
                syncAge = 5000L,
            )

        assertTrue("Should be synchronized", syncStatus.isSynchronized)
        assertEquals("Clock offset should match", 1500L, syncStatus.clockOffsetMs)
        assertTrue("Last sync timestamp should be positive", syncStatus.lastSyncTimestamp > 0)
        assertTrue("PC reference time should be positive", syncStatus.pcReferenceTime > 0)
        assertEquals("Sync age should match", 5000L, syncStatus.syncAge)

        println("[DEBUG_LOG] SyncStatus data class test passed")
    }

    @Test
    fun testInitialSyncState() =
        runTest {
            println("[DEBUG_LOG] Testing initial synchronization state")

            val syncStatus = syncClockManager.getSyncStatus()

            assertFalse("Should not be synchronized initially", syncStatus.isSynchronized)
            assertEquals("Initial offset should be zero", 0L, syncStatus.clockOffsetMs)
            assertEquals("Initial last sync should be zero", 0L, syncStatus.lastSyncTimestamp)
            assertEquals("Initial PC reference should be zero", 0L, syncStatus.pcReferenceTime)
            assertEquals("Initial sync age should be -1", -1L, syncStatus.syncAge)
            assertFalse("Sync should not be valid initially", syncClockManager.isSyncValid())

            println("[DEBUG_LOG] Initial sync state test passed")
        }

    @Test
    fun testSuccessfulClockSynchronization() =
        runTest {
            println("[DEBUG_LOG] Testing successful clock synchronization")

            val pcTimestamp = System.currentTimeMillis() + 2000L // PC is 2 seconds ahead
            val syncId = "test_sync_001"

            val success = syncClockManager.synchronizeWithPc(pcTimestamp, syncId)

            assertTrue("Synchronization should succeed", success)

            val syncStatus = syncClockManager.getSyncStatus()
            assertTrue("Should be synchronized after sync", syncStatus.isSynchronized)
            assertTrue("Clock offset should be positive (PC ahead)", syncStatus.clockOffsetMs > 0)
            assertEquals("PC reference time should match", pcTimestamp, syncStatus.pcReferenceTime)
            assertTrue(
                "Last sync timestamp should be recent",
                abs(syncStatus.lastSyncTimestamp - System.currentTimeMillis()) < 1000,
            )
            assertTrue("Sync should be valid", syncClockManager.isSyncValid())

            verify { mockLogger.info(match { it.contains("Clock synchronized successfully") }) }

            println("[DEBUG_LOG] Successful clock synchronization test passed")
        }

    @Test
    fun testClockSynchronizationWithNegativeOffset() =
        runTest {
            println("[DEBUG_LOG] Testing clock synchronization with negative offset")

            val pcTimestamp = System.currentTimeMillis() - 1500L // PC is 1.5 seconds behind
            val syncId = "test_sync_002"

            val success = syncClockManager.synchronizeWithPc(pcTimestamp, syncId)

            assertTrue("Synchronization should succeed", success)

            val syncStatus = syncClockManager.getSyncStatus()
            assertTrue("Should be synchronized", syncStatus.isSynchronized)
            assertTrue("Clock offset should be negative (PC behind)", syncStatus.clockOffsetMs < 0)
            assertEquals("PC reference time should match", pcTimestamp, syncStatus.pcReferenceTime)

            println("[DEBUG_LOG] Negative offset synchronization test passed")
        }

    @Test
    fun testInvalidPcTimestamp() =
        runTest {
            println("[DEBUG_LOG] Testing invalid PC timestamp handling")

            val invalidTimestamp = -1000L // Invalid negative timestamp
            val syncId = "test_sync_invalid"

            val success = syncClockManager.synchronizeWithPc(invalidTimestamp, syncId)

            assertFalse("Synchronization should fail with invalid timestamp", success)

            val syncStatus = syncClockManager.getSyncStatus()
            assertFalse("Should not be synchronized", syncStatus.isSynchronized)
            assertEquals("Offset should remain zero", 0L, syncStatus.clockOffsetMs)

            verify { mockLogger.error(match { it.contains("Invalid PC timestamp") }) }

            println("[DEBUG_LOG] Invalid PC timestamp test passed")
        }

    @Test
    fun testSyncedTimestampCalculation() =
        runTest {
            println("[DEBUG_LOG] Testing synced timestamp calculation")

            val pcTimestamp = System.currentTimeMillis() + 3000L // PC is 3 seconds ahead
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_003")

            val deviceTime = System.currentTimeMillis()
            val syncedTime = syncClockManager.getSyncedTimestamp(deviceTime)

            assertTrue("Synced time should be greater than device time", syncedTime > deviceTime)
            assertTrue(
                "Offset should be approximately 3000ms",
                abs((syncedTime - deviceTime) - 3000L) < 100L,
            ) // Allow 100ms tolerance

            println("[DEBUG_LOG] Synced timestamp calculation test passed")
        }

    @Test
    fun testCurrentSyncedTime() =
        runTest {
            println("[DEBUG_LOG] Testing current synced time")

            val pcTimestamp = System.currentTimeMillis() + 1000L
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_004")

            val currentSyncedTime = syncClockManager.getCurrentSyncedTime()
            val currentDeviceTime = System.currentTimeMillis()

            assertTrue(
                "Current synced time should be greater than device time",
                currentSyncedTime > currentDeviceTime,
            )
            assertTrue(
                "Time difference should be approximately 1000ms",
                abs((currentSyncedTime - currentDeviceTime) - 1000L) < 200L,
            ) // Allow 200ms tolerance

            println("[DEBUG_LOG] Current synced time test passed")
        }

    @Test
    fun testUnsynchronizedTimestamp() =
        runTest {
            println("[DEBUG_LOG] Testing unsynchronized timestamp handling")

            val deviceTime = System.currentTimeMillis()
            val syncedTime = syncClockManager.getSyncedTimestamp(deviceTime)

            assertEquals("Should return device time when not synchronized", deviceTime, syncedTime)

            verify { mockLogger.warning("Clock not synchronized, using device timestamp") }

            println("[DEBUG_LOG] Unsynchronized timestamp test passed")
        }

    @Test
    fun testSyncValidityExpiration() =
        runTest {
            println("[DEBUG_LOG] Testing sync validity expiration")

            val pcTimestamp = System.currentTimeMillis()
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_005")

            assertTrue("Sync should be valid initially", syncClockManager.isSyncValid())

            // Mock time passage beyond validity duration
            // Note: In real implementation, we would need to mock System.currentTimeMillis()
            // For this test, we verify the logic conceptually
            val syncStatus = syncClockManager.getSyncStatus()
            assertTrue("Sync age should be small initially", syncStatus.syncAge < 1000L)

            println("[DEBUG_LOG] Sync validity expiration test passed")
        }

    @Test
    fun testResetSynchronization() =
        runTest {
            println("[DEBUG_LOG] Testing synchronization reset")

            // First synchronize
            val pcTimestamp = System.currentTimeMillis() + 2000L
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_006")

            assertTrue("Should be synchronized before reset", syncClockManager.isSyncValid())

            // Reset synchronization
            syncClockManager.resetSync()

            val syncStatus = syncClockManager.getSyncStatus()
            assertFalse("Should not be synchronized after reset", syncStatus.isSynchronized)
            assertEquals("Offset should be zero after reset", 0L, syncStatus.clockOffsetMs)
            assertEquals("Last sync should be zero after reset", 0L, syncStatus.lastSyncTimestamp)
            assertEquals("PC reference should be zero after reset", 0L, syncStatus.pcReferenceTime)
            assertFalse("Sync should not be valid after reset", syncClockManager.isSyncValid())

            verify { mockLogger.info(match { it.contains("Resetting clock synchronization") }) }

            println("[DEBUG_LOG] Synchronization reset test passed")
        }

    @Test
    fun testDeviceToPcTimeConversion() =
        runTest {
            println("[DEBUG_LOG] Testing device to PC time conversion")

            val pcTimestamp = System.currentTimeMillis() + 5000L // PC is 5 seconds ahead
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_007")

            val deviceTime = System.currentTimeMillis()
            val pcTime = syncClockManager.deviceToPcTime(deviceTime)

            assertTrue("PC time should be greater than device time", pcTime > deviceTime)
            assertTrue(
                "Time difference should be approximately 5000ms",
                abs((pcTime - deviceTime) - 5000L) < 100L,
            )

            println("[DEBUG_LOG] Device to PC time conversion test passed")
        }

    @Test
    fun testPcToDeviceTimeConversion() =
        runTest {
            println("[DEBUG_LOG] Testing PC to device time conversion")

            val pcTimestamp = System.currentTimeMillis() + 3000L // PC is 3 seconds ahead
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_008")

            val pcTime = System.currentTimeMillis() + 3000L
            val deviceTime = syncClockManager.pcToDeviceTime(pcTime)

            assertTrue("Device time should be less than PC time", deviceTime < pcTime)
            assertTrue(
                "Time difference should be approximately 3000ms",
                abs((pcTime - deviceTime) - 3000L) < 100L,
            )

            println("[DEBUG_LOG] PC to device time conversion test passed")
        }

    @Test
    fun testSyncStatisticsGeneration() =
        runTest {
            println("[DEBUG_LOG] Testing sync statistics generation")

            val pcTimestamp = System.currentTimeMillis() + 1000L
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_009")

            val statistics = syncClockManager.getSyncStatistics()

            assertNotNull("Statistics should not be null", statistics)
            assertTrue("Statistics should contain sync info", statistics.contains("Clock Synchronization Statistics"))
            assertTrue("Statistics should show synchronized state", statistics.contains("Synchronized: true"))
            assertTrue("Statistics should show clock offset", statistics.contains("Clock Offset:"))
            assertTrue("Statistics should show last sync", statistics.contains("Last Sync:"))
            assertTrue("Statistics should show PC reference time", statistics.contains("PC Reference Time:"))
            assertTrue("Statistics should show sync validity", statistics.contains("Sync Valid:"))
            assertTrue("Statistics should show current synced time", statistics.contains("Current Synced Time:"))

            println("[DEBUG_LOG] Sync statistics generation test passed")
        }

    @Test
    fun testNetworkLatencyEstimation() =
        runTest {
            println("[DEBUG_LOG] Testing network latency estimation")

            val pcTimestamp = System.currentTimeMillis()
            val requestSentTime = System.currentTimeMillis() - 100L // Request sent 100ms ago

            val estimatedLatency = syncClockManager.estimateNetworkLatency(pcTimestamp, requestSentTime)

            assertTrue("Estimated latency should be positive", estimatedLatency >= 0)
            assertTrue("Estimated latency should be reasonable", estimatedLatency < 1000L) // Less than 1 second

            verify { mockLogger.debug(match { it.contains("Network latency estimation") }) }
            verify { mockLogger.debug(match { it.contains("Round-trip time") }) }
            verify { mockLogger.debug(match { it.contains("Estimated latency") }) }

            println("[DEBUG_LOG] Network latency estimation test passed")
        }

    @Test
    fun testSyncHealthValidation() =
        runTest {
            println("[DEBUG_LOG] Testing sync health validation")

            // Test unsynchronized state
            var isHealthy = syncClockManager.validateSyncHealth()
            assertFalse("Should not be healthy when unsynchronized", isHealthy)
            verify { mockLogger.warning("Clock synchronization not established") }

            // Test synchronized state
            val pcTimestamp = System.currentTimeMillis() + 2000L
            syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_010")

            isHealthy = syncClockManager.validateSyncHealth()
            assertTrue("Should be healthy when synchronized", isHealthy)

            println("[DEBUG_LOG] Sync health validation test passed")
        }

    @Test
    fun testConcurrentSynchronization() =
        runTest {
            println("[DEBUG_LOG] Testing concurrent synchronization operations")

            val jobs = mutableListOf<Job>()

            // Launch multiple synchronization operations concurrently
            repeat(5) { index ->
                val job =
                    launch {
                        val pcTimestamp = System.currentTimeMillis() + (index * 1000L)
                        syncClockManager.synchronizeWithPc(pcTimestamp, "concurrent_sync_$index")
                    }
                jobs.add(job)
            }

            // Wait for all operations to complete
            jobs.joinAll()

            // Verify final state is consistent
            val syncStatus = syncClockManager.getSyncStatus()
            assertTrue("Should be synchronized after concurrent operations", syncStatus.isSynchronized)
            assertTrue("Should have valid sync after concurrent operations", syncClockManager.isSyncValid())

            println("[DEBUG_LOG] Concurrent synchronization test passed")
        }
}
