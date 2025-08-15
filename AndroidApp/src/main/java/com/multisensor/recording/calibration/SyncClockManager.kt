package com.multisensor.recording.calibration

import com.multisensor.recording.util.Logger
import kotlinx.coroutines.delay
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.ConcurrentLinkedQueue
import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

/**
 * Time synchronization manager implementing NTP-like clock sync with PC
 * Implements FR3: Time Synchronisation Service
 */
class SyncClockManager {
    companion object {
        private const val TARGET_ACCURACY_MS = 10L
        private const val MAX_OFFSET_DRIFT_MS = 50L
        private const val SYNC_VALIDITY_DURATION_MS = 180000L

        private const val MIN_SYNC_SAMPLES = 3
        private const val MAX_SYNC_SAMPLES = 8
        private const val OUTLIER_THRESHOLD_FACTOR = 2.0
        private const val DRIFT_CORRECTION_INTERVAL_MS = 30000L

        private const val MAX_ACCEPTABLE_RTT_MS = 200L
        private const val LATENCY_MEASUREMENT_SAMPLES = 5
    }

    data class SyncMeasurement(
        val t1: Long,
        val t2: Long,
        val t3: Long,
        val t4: Long,
        val roundTripDelay: Long = (t4 - t1) - (t3 - t2),
        val clockOffset: Long = ((t2 - t1) + (t3 - t4)) / 2,
        val timestamp: Long = System.currentTimeMillis(),
    )

    data class SyncQualityMetrics(
        val accuracy: Float,
        val stability: Float,
        val latency: Long,
        val jitter: Float,
        val driftRate: Double,
        val sampleCount: Int,
        val lastUpdateTime: Long = System.currentTimeMillis(),
    )

    data class SyncResult(
        val success: Boolean,
        val measurement: SyncMeasurement,
        val error: String? = null,
    )

    data class SyncStatus(
        val isSynchronized: Boolean,
        val clockOffsetMs: Long,
        val lastSyncTimestamp: Long,
        val pcReferenceTime: Long,
        val syncAge: Long,
    )

    private val logger = Logger()
    private val mutex = Mutex()
    private var clockOffsetMs: Long = 0L
    private var lastSyncTimestamp: Long = 0L
    private var pcReferenceTime: Long = 0L
    private var isSynchronized: Boolean = false

    private val syncMeasurements = ConcurrentLinkedQueue<SyncMeasurement>()
    private val latencyMeasurements = ConcurrentLinkedQueue<Long>()
    private var driftRate: Double = 0.0
    private var lastDriftCorrectionTime: Long = 0L
    private var syncQualityScore: Float = 0.0f

    /**
     * Synchronize with PC using NTP-style protocol
     * @param pcTimestamp Timestamp from PC
     * @param syncId Optional sync identifier for logging
     * @return True if synchronization successful
     */
    suspend fun synchronizeWithPc(
        pcTimestamp: Long,
        syncId: String? = null,
    ): Boolean =
        mutex.withLock {
            return try {
                logger.info("[DEBUG_LOG] Enhanced NTP-style synchronisation requested")
                syncId?.let { logger.info("[DEBUG_LOG] Sync ID: $it") }

                val syncResult = performNTPStyleSync(pcTimestamp)

                if (syncResult.success) {
                    syncMeasurements.offer(syncResult.measurement)

                    while (syncMeasurements.size > MAX_SYNC_SAMPLES) {
                        syncMeasurements.poll()
                    }

                    val enhancedOffset = calculateEnhancedOffset()

                    updateDriftRate(enhancedOffset)

                    val correctedOffset = applyDriftCorrection(enhancedOffset)

                    clockOffsetMs = correctedOffset
                    lastSyncTimestamp = System.currentTimeMillis()
                    pcReferenceTime = pcTimestamp
                    isSynchronized = true

                    updateSyncQualityMetrics()

                    logger.info("[DEBUG_LOG] Enhanced sync complete - Offset: ${clockOffsetMs}ms, Quality: $syncQualityScore")
                    true
                } else {
                    logger.error("NTP-style synchronisation failed: ${syncResult.error}")
                    false
                }
            } catch (e: Exception) {
                logger.error("Error during enhanced clock synchronisation", e)
                false
            }
        }

    /**
     * Get synchronized timestamp for given device timestamp
     * @param deviceTimestamp Device timestamp (default: current time)
     * @return Synchronized timestamp
     */
    fun getSyncedTimestamp(deviceTimestamp: Long = System.currentTimeMillis()): Long =
        if (isSynchronized) {
            deviceTimestamp + clockOffsetMs
        } else {
            logger.warning("Clock not synchronized, using device timestamp")
            deviceTimestamp
        }

    /**
     * Get current synchronized time
     * @return Current synchronized timestamp
     */
    fun getCurrentSyncedTime(): Long = getSyncedTimestamp()

    /**
     * Check if sync is still valid (not expired)
     * @return True if sync is valid
     */
    fun isSyncValid(): Boolean {
        if (!isSynchronized) return false

        val syncAge = System.currentTimeMillis() - lastSyncTimestamp
        return syncAge < SYNC_VALIDITY_DURATION_MS
    }

    /**
     * Get current synchronization status
     * @return SyncStatus object with sync information
     */
    fun getSyncStatus(): SyncStatus {
        val currentTime = System.currentTimeMillis()
        val syncAge = if (isSynchronized) currentTime - lastSyncTimestamp else -1L

        return SyncStatus(
            isSynchronized = isSynchronized,
            clockOffsetMs = clockOffsetMs,
            lastSyncTimestamp = lastSyncTimestamp,
            pcReferenceTime = pcReferenceTime,
            syncAge = syncAge,
        )
    }

    /**
     * Reset synchronization state
     */
    suspend fun resetSync(): Unit =
        mutex.withLock {
            logger.info("Resetting clock synchronisation")
            isSynchronized = false
            clockOffsetMs = 0L
            lastSyncTimestamp = 0L
            pcReferenceTime = 0L
            syncMeasurements.clear()
            latencyMeasurements.clear()
            driftRate = 0.0
            lastDriftCorrectionTime = 0L
            syncQualityScore = 0.0f
        }

    private suspend fun performNTPStyleSync(pcTimestamp: Long): SyncResult {
        return try {
            val t1 = System.currentTimeMillis()
            val t2 = pcTimestamp
            val t3 = pcTimestamp
            val t4 = System.currentTimeMillis()

            val roundTripTime = t4 - t1
            if (roundTripTime > MAX_ACCEPTABLE_RTT_MS) {
                return SyncResult(
                    false,
                    SyncMeasurement(t1, t2, t3, t4),
                    "Round-trip time too high: ${roundTripTime}ms"
                )
            }

            val measurement = SyncMeasurement(t1, t2, t3, t4)

            logger.debug("[DEBUG_LOG] NTP measurement - RTT: ${measurement.roundTripDelay}ms, Offset: ${measurement.clockOffset}ms")

            SyncResult(true, measurement)
        } catch (e: Exception) {
            SyncResult(false, SyncMeasurement(0, 0, 0, 0), "NTP sync failed: ${e.message}")
        }
    }

    private fun calculateEnhancedOffset(): Long {
        if (syncMeasurements.size < MIN_SYNC_SAMPLES) {
            return syncMeasurements.lastOrNull()?.clockOffset ?: 0L
        }

        val offsets = syncMeasurements.map { it.clockOffset }

        val mean = offsets.average()
        val variance = offsets.map { (it - mean).pow(2) }.average()
        val stdDev = sqrt(variance)

        val filteredOffsets =
            offsets.filter {
                abs(it - mean) <= OUTLIER_THRESHOLD_FACTOR * stdDev
            }

        val weights =
            filteredOffsets.indices.map { index ->
                1.0 + (index.toDouble() / filteredOffsets.size)
            }

        val weightedSum = filteredOffsets.zip(weights).sumOf { (offset, weight) -> offset * weight }
        val weightSum = weights.sum()

        return (weightedSum / weightSum).toLong()
    }

    private fun updateDriftRate(currentOffset: Long) {
        if (syncMeasurements.size < 2) return

        val measurements = syncMeasurements.toList().sortedBy { it.timestamp }
        if (measurements.size < 2) return

        val timeSpan = measurements.last().timestamp - measurements.first().timestamp
        if (timeSpan < DRIFT_CORRECTION_INTERVAL_MS) return

        val offsetChange = measurements.last().clockOffset - measurements.first().clockOffset
        driftRate = offsetChange.toDouble() / timeSpan.toDouble()

        logger.debug("[DEBUG_LOG] Drift rate updated: ${driftRate} ms/ms")
    }

    private fun applyDriftCorrection(offset: Long): Long {
        if (driftRate == 0.0 || lastDriftCorrectionTime == 0L) {
            lastDriftCorrectionTime = System.currentTimeMillis()
            return offset
        }

        val timeSinceLastCorrection = System.currentTimeMillis() - lastDriftCorrectionTime
        val driftCorrection = (driftRate * timeSinceLastCorrection).toLong()

        val correctedOffset = offset - driftCorrection

        logger.debug("[DEBUG_LOG] Drift correction applied: ${driftCorrection}ms, Corrected offset: ${correctedOffset}ms")

        lastDriftCorrectionTime = System.currentTimeMillis()
        return correctedOffset
    }

    private fun updateSyncQualityMetrics() {
        if (syncMeasurements.isEmpty()) {
            syncQualityScore = 0.0f
            return
        }

        val offsets = syncMeasurements.map { it.clockOffset }
        val rtts = syncMeasurements.map { it.roundTripDelay }

        val offsetMean = offsets.average()
        val offsetStdDev = if (offsets.size > 1) {
            sqrt(offsets.map { (it - offsetMean).pow(2) }.average())
        } else {
            0.0
        }

        val rttMean = rtts.average()
        val accuracy = (TARGET_ACCURACY_MS / (abs(offsetMean) + 1.0)).toFloat()
        val stability = (1.0 / (offsetStdDev + 1.0)).toFloat()

        syncQualityScore = (accuracy * 0.6f + stability * 0.4f).coerceIn(0.0f, 1.0f)

        logger.debug("[DEBUG_LOG] Quality metrics - Accuracy: $accuracy, Stability: $stability, Score: $syncQualityScore")
    }
}