package com.multisensor.recording.calibration

import com.multisensor.recording.util.Logger
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.abs

/**
 * SyncClockManager handles clock synchronization with PC reference time for Milestone 2.8.
 * 
 * This manager maintains a clock offset between the phone and PC to ensure all recorded data
 * uses a consistent timeline across devices.
 */
@Singleton
class SyncClockManager @Inject constructor(
    private val logger: Logger
) {
    
    companion object {
        private const val MAX_OFFSET_DRIFT_MS = 1000L // Maximum allowed drift before re-sync
        private const val SYNC_VALIDITY_DURATION_MS = 300000L // 5 minutes
    }
    
    private val mutex = Mutex()
    private var clockOffsetMs: Long = 0L
    private var lastSyncTimestamp: Long = 0L
    private var pcReferenceTime: Long = 0L
    private var isSynchronized: Boolean = false
    
    data class SyncStatus(
        val isSynchronized: Boolean,
        val clockOffsetMs: Long,
        val lastSyncTimestamp: Long,
        val pcReferenceTime: Long,
        val syncAge: Long
    )
    
    /**
     * Synchronizes device clock with PC reference time
     */
    suspend fun synchronizeWithPc(pcTimestamp: Long, syncId: String? = null): Boolean = mutex.withLock {
        try {
            val deviceTimestamp = System.currentTimeMillis()
            val newOffset = pcTimestamp - deviceTimestamp
            
            logger.info("[DEBUG_LOG] Clock synchronization requested")
            logger.info("[DEBUG_LOG] PC timestamp: $pcTimestamp")
            logger.info("[DEBUG_LOG] Device timestamp: $deviceTimestamp")
            logger.info("[DEBUG_LOG] Calculated offset: ${newOffset}ms")
            syncId?.let { logger.info("[DEBUG_LOG] Sync ID: $it") }
            
            // Check if this is a significant change from previous sync
            if (isSynchronized) {
                val offsetDrift = abs(newOffset - clockOffsetMs)
                if (offsetDrift > MAX_OFFSET_DRIFT_MS) {
                    logger.warning("Large clock drift detected: ${offsetDrift}ms")
                }
            }
            
            // Update synchronization state
            clockOffsetMs = newOffset
            lastSyncTimestamp = deviceTimestamp
            pcReferenceTime = pcTimestamp
            isSynchronized = true
            
            logger.info("[DEBUG_LOG] Clock synchronization complete - Offset: ${clockOffsetMs}ms")
            true
            
        } catch (e: Exception) {
            logger.error("Error during clock synchronization", e)
            false
        }
    }
    
    /**
     * Gets synchronized timestamp based on current device time and PC offset
     */
    fun getSyncedTimestamp(deviceTimestamp: Long = System.currentTimeMillis()): Long {
        return if (isSynchronized) {
            deviceTimestamp + clockOffsetMs
        } else {
            logger.warning("Clock not synchronized, using device timestamp")
            deviceTimestamp
        }
    }
    
    /**
     * Gets current PC-synchronized time
     */
    fun getCurrentSyncedTime(): Long {
        return getSyncedTimestamp()
    }
    
    /**
     * Checks if clock synchronization is still valid
     */
    fun isSyncValid(): Boolean {
        if (!isSynchronized) return false
        
        val syncAge = System.currentTimeMillis() - lastSyncTimestamp
        return syncAge < SYNC_VALIDITY_DURATION_MS
    }
    
    /**
     * Gets current synchronization status
     */
    fun getSyncStatus(): SyncStatus {
        val currentTime = System.currentTimeMillis()
        val syncAge = if (isSynchronized) currentTime - lastSyncTimestamp else -1L
        
        return SyncStatus(
            isSynchronized = isSynchronized,
            clockOffsetMs = clockOffsetMs,
            lastSyncTimestamp = lastSyncTimestamp,
            pcReferenceTime = pcReferenceTime,
            syncAge = syncAge
        )
    }
    
    /**
     * Resets synchronization state
     */
    suspend fun resetSync(): Unit = mutex.withLock {
        logger.info("[DEBUG_LOG] Resetting clock synchronization")
        clockOffsetMs = 0L
        lastSyncTimestamp = 0L
        pcReferenceTime = 0L
        isSynchronized = false
    }
    
    /**
     * Converts device timestamp to PC-synchronized timestamp
     */
    fun deviceToPcTime(deviceTimestamp: Long): Long {
        return deviceTimestamp + clockOffsetMs
    }
    
    /**
     * Converts PC timestamp to device timestamp
     */
    fun pcToDeviceTime(pcTimestamp: Long): Long {
        return pcTimestamp - clockOffsetMs
    }
    
    /**
     * Gets detailed synchronization statistics for debugging
     */
    fun getSyncStatistics(): String {
        val status = getSyncStatus()
        return buildString {
            appendLine("Clock Synchronization Statistics:")
            appendLine("  Synchronized: ${status.isSynchronized}")
            appendLine("  Clock Offset: ${status.clockOffsetMs}ms")
            appendLine("  Last Sync: ${if (status.lastSyncTimestamp > 0) "${status.syncAge}ms ago" else "Never"}")
            appendLine("  PC Reference Time: ${status.pcReferenceTime}")
            appendLine("  Sync Valid: ${isSyncValid()}")
            appendLine("  Current Synced Time: ${getCurrentSyncedTime()}")
        }
    }
    
    /**
     * Estimates network latency based on sync round-trip
     */
    fun estimateNetworkLatency(pcTimestamp: Long, requestSentTime: Long): Long {
        val responseReceivedTime = System.currentTimeMillis()
        val roundTripTime = responseReceivedTime - requestSentTime
        
        // Estimate one-way latency as half of round-trip time
        val estimatedLatency = roundTripTime / 2
        
        logger.debug("[DEBUG_LOG] Network latency estimation:")
        logger.debug("[DEBUG_LOG] Round-trip time: ${roundTripTime}ms")
        logger.debug("[DEBUG_LOG] Estimated latency: ${estimatedLatency}ms")
        
        return estimatedLatency
    }
    
    /**
     * Performs periodic sync validation and warns about drift
     */
    fun validateSyncHealth(): Boolean {
        if (!isSynchronized) {
            logger.warning("Clock synchronization not established")
            return false
        }
        
        if (!isSyncValid()) {
            logger.warning("Clock synchronization expired - re-sync recommended")
            return false
        }
        
        val syncAge = System.currentTimeMillis() - lastSyncTimestamp
        if (syncAge > SYNC_VALIDITY_DURATION_MS / 2) {
            logger.info("Clock synchronization aging - consider re-sync soon")
        }
        
        return true
    }
}
