package com.multisensor.recording.calibration

import com.multisensor.recording.util.Logger
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import kotlin.math.abs

/**
 * Unit tests for SyncClockManager - FR3 Time Synchronisation Service
 */
class SyncClockManagerTest {
    private lateinit var syncClockManager: SyncClockManager

    @Before
    fun setUp() {
        // Enable test mode to disable Android Log calls
        Logger.isTestMode = true
        syncClockManager = SyncClockManager()
    }

    @Test
    fun testInitialSyncState() = runTest {
        val syncStatus = syncClockManager.getSyncStatus()

        assertFalse("Should not be synchronised initially", syncStatus.isSynchronized)
        assertEquals("Initial offset should be zero", 0L, syncStatus.clockOffsetMs)
        assertEquals("Initial last sync should be zero", 0L, syncStatus.lastSyncTimestamp)
        assertEquals("Initial PC reference should be zero", 0L, syncStatus.pcReferenceTime)
        assertEquals("Initial sync age should be -1", -1L, syncStatus.syncAge)
        assertFalse("Sync should not be valid initially", syncClockManager.isSyncValid())
    }

    @Test
    fun testSuccessfulClockSynchronization() = runTest {
        val pcTimestamp = System.currentTimeMillis() + 2000L
        val syncId = "test_sync_001"

        val syncResult = syncClockManager.synchronizeWithPc(pcTimestamp, syncId)
        assertTrue("Synchronization should succeed", syncResult)

        val syncStatus = syncClockManager.getSyncStatus()
        assertTrue("Should be synchronized after sync", syncStatus.isSynchronized)
        assertTrue("Sync should be valid after sync", syncClockManager.isSyncValid())
        assertNotEquals("Clock offset should not be zero", 0L, syncStatus.clockOffsetMs)
        assertEquals("PC reference time should match", pcTimestamp, syncStatus.pcReferenceTime)
    }

    @Test
    fun testSyncedTimestamp() = runTest {
        val pcTimestamp = System.currentTimeMillis() + 1000L
        syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_002")

        val deviceTime = System.currentTimeMillis()
        val syncedTime = syncClockManager.getSyncedTimestamp(deviceTime)

        assertTrue("Synced time should be greater than device time", syncedTime > deviceTime)
        // Allow for some variance due to timing
        assertTrue("Time difference should be approximately 1000ms", 
                   abs((syncedTime - deviceTime) - 1000L) < 200L)
    }

    @Test
    fun testCurrentSyncedTime() = runTest {
        val pcTimestamp = System.currentTimeMillis() + 1000L
        syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_003")

        val currentSyncedTime = syncClockManager.getCurrentSyncedTime()
        val currentDeviceTime = System.currentTimeMillis()

        assertTrue("Current synced time should be greater than device time", 
                   currentSyncedTime > currentDeviceTime)
        assertTrue("Time difference should be approximately 1000ms",
                   abs((currentSyncedTime - currentDeviceTime) - 1000L) < 200L)
    }

    @Test
    fun testUnsynchronizedTimestamp() = runTest {
        val deviceTime = System.currentTimeMillis()
        val syncedTime = syncClockManager.getSyncedTimestamp(deviceTime)

        assertEquals("Should return device time when not synchronised", deviceTime, syncedTime)
    }

    @Test
    fun testResetSynchronization() = runTest {
        val pcTimestamp = System.currentTimeMillis() + 2000L
        syncClockManager.synchronizeWithPc(pcTimestamp, "test_sync_004")

        assertTrue("Should be synchronized before reset", syncClockManager.isSyncValid())

        syncClockManager.resetSync()

        val syncStatus = syncClockManager.getSyncStatus()
        assertFalse("Should not be synchronized after reset", syncStatus.isSynchronized)
        assertEquals("Offset should be zero after reset", 0L, syncStatus.clockOffsetMs)
        assertFalse("Sync should not be valid after reset", syncClockManager.isSyncValid())
    }

    @Test
    fun testSyncDataClasses() {
        // Test SyncMeasurement
        val measurement = SyncClockManager.SyncMeasurement(
            t1 = 1000L, t2 = 1010L, t3 = 1020L, t4 = 1030L
        )
        assertEquals("Round trip delay calculation", 20L, measurement.roundTripDelay)
        assertEquals("Clock offset calculation", 0L, measurement.clockOffset)

        // Test SyncStatus
        val status = SyncClockManager.SyncStatus(
            isSynchronized = true,
            clockOffsetMs = 100L,
            lastSyncTimestamp = 1000L,
            pcReferenceTime = 2000L,
            syncAge = 500L
        )
        assertTrue("Status should show synchronized", status.isSynchronized)
        assertEquals("Clock offset should match", 100L, status.clockOffsetMs)
    }
}