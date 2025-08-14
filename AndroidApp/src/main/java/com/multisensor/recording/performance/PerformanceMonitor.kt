package com.multisensor.recording.performance

import android.content.Context
import android.os.Debug
import android.os.Process
import android.util.Log
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import java.io.RandomAccessFile
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.max

/**
 * NFR1: Performance (Real-Time Data Handling) - Monitors system performance
 * 
 * Implements:
 * - Real-time data throughput monitoring (128 Hz sensor + 30 FPS video)
 * - Memory usage tracking
 * - CPU utilization monitoring
 * - Frame drop detection
 * - Data buffering analysis
 * - Performance alerting
 * 
 * Requirements from 3.tex section NFR1:
 * - Support 128 Hz sensor sampling + 30 FPS video without data loss
 * - Multi-threading and asynchronous processing for performance
 * - Video ~5 Mbps + audio 128 kbps real-time storage
 * - Multiple devices (3+ cameras + GSR) without bottlenecks
 * - No dropped frames or samples due to performance issues
 */
class PerformanceMonitor(private val context: Context) {
    
    companion object {
        private const val TAG = "PerformanceMonitor"
        
        // Performance targets from NFR1
        private const val TARGET_GSR_SAMPLE_RATE_HZ = 128.0
        private const val TARGET_VIDEO_FPS = 30.0
        private const val TARGET_VIDEO_BITRATE_MBPS = 5.0
        private const val TARGET_AUDIO_BITRATE_KBPS = 128.0
        
        // Performance thresholds
        private const val MAX_ACCEPTABLE_FRAME_DROP_RATE = 0.05 // 5%
        private const val MAX_ACCEPTABLE_SAMPLE_DROP_RATE = 0.01 // 1%
        private const val MAX_MEMORY_USAGE_PERCENT = 80.0
        private const val MAX_CPU_USAGE_PERCENT = 85.0
        
        // Monitoring intervals
        private const val MONITORING_INTERVAL_MS = 1000L
        private const val PERFORMANCE_HISTORY_SIZE = 300 // 5 minutes at 1s intervals
    }

    private val isMonitoring = AtomicBoolean(false)
    private val monitoringScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var monitoringJob: Job? = null
    
    // Performance counters
    private val totalFramesExpected = AtomicLong(0)
    private val totalFramesProcessed = AtomicLong(0)
    private val totalSamplesExpected = AtomicLong(0)
    private val totalSamplesProcessed = AtomicLong(0)
    private val totalBytesWritten = AtomicLong(0)
    
    // Real-time metrics
    private val currentFPS = AtomicLong(0)
    private val currentSampleRate = AtomicLong(0)
    private val currentMemoryUsage = AtomicLong(0)
    private val currentCpuUsage = AtomicLong(0)
    
    // Performance history
    private val performanceHistory = mutableListOf<PerformanceSnapshot>()
    private val streamMetrics = ConcurrentHashMap<String, StreamMetrics>()
    
    // Alert callbacks
    private var performanceAlertCallback: ((PerformanceAlert) -> Unit)? = null

    /**
     * Start performance monitoring
     * NFR1: Real-time performance tracking
     */
    fun startMonitoring() {
        if (isMonitoring.get()) {
            Logger.w(TAG, "Performance monitoring already running")
            return
        }
        
        Logger.i(TAG, "Starting performance monitoring...")
        isMonitoring.set(true)
        resetCounters()
        
        monitoringJob = monitoringScope.launch {
            while (isMonitoring.get()) {
                try {
                    val snapshot = capturePerformanceSnapshot()
                    updatePerformanceHistory(snapshot)
                    checkPerformanceThresholds(snapshot)
                    
                    delay(MONITORING_INTERVAL_MS)
                } catch (e: Exception) {
                    Logger.e(TAG, "Error in performance monitoring", e)
                }
            }
        }
    }

    /**
     * Stop performance monitoring
     */
    fun stopMonitoring() {
        if (!isMonitoring.get()) {
            return
        }
        
        Logger.i(TAG, "Stopping performance monitoring...")
        isMonitoring.set(false)
        monitoringJob?.cancel()
        
        // Generate final performance report
        val finalReport = generatePerformanceReport()
        Logger.i(TAG, "Final performance report: $finalReport")
    }

    /**
     * Record frame processing for video streams
     * NFR1: Frame drop detection
     */
    fun recordFrameProcessed(streamId: String, expectedFrameTime: Long, actualFrameTime: Long) {
        totalFramesProcessed.incrementAndGet()
        
        val metrics = streamMetrics.getOrPut(streamId) { StreamMetrics(streamId, StreamType.VIDEO) }
        metrics.recordFrame(expectedFrameTime, actualFrameTime)
        
        // Update current FPS estimate
        val recentFrameCount = metrics.getRecentFrameCount(1000) // Frames in last second
        currentFPS.set(recentFrameCount.toLong())
    }

    /**
     * Record expected frame for drop rate calculation
     */
    fun recordExpectedFrame(streamId: String) {
        totalFramesExpected.incrementAndGet()
        
        val metrics = streamMetrics.getOrPut(streamId) { StreamMetrics(streamId, StreamType.VIDEO) }
        metrics.recordExpectedFrame()
    }

    /**
     * Record sensor sample processing
     * NFR1: Sample drop detection for 128 Hz sensor data
     */
    fun recordSampleProcessed(streamId: String, expectedSampleTime: Long, actualSampleTime: Long) {
        totalSamplesProcessed.incrementAndGet()
        
        val metrics = streamMetrics.getOrPut(streamId) { StreamMetrics(streamId, StreamType.SENSOR) }
        metrics.recordSample(expectedSampleTime, actualSampleTime)
        
        // Update current sample rate estimate
        val recentSampleCount = metrics.getRecentSampleCount(1000) // Samples in last second
        currentSampleRate.set(recentSampleCount.toLong())
    }

    /**
     * Record expected sensor sample
     */
    fun recordExpectedSample(streamId: String) {
        totalSamplesExpected.incrementAndGet()
        
        val metrics = streamMetrics.getOrPut(streamId) { StreamMetrics(streamId, StreamType.SENSOR) }
        metrics.recordExpectedSample()
    }

    /**
     * Record data throughput
     * NFR1: Monitor ~5 Mbps video + 128 kbps audio throughput
     */
    fun recordDataThroughput(streamId: String, bytesWritten: Long) {
        totalBytesWritten.addAndGet(bytesWritten)
        
        val metrics = streamMetrics.getOrPut(streamId) { StreamMetrics(streamId, StreamType.DATA) }
        metrics.recordDataThroughput(bytesWritten)
    }

    /**
     * Capture current performance snapshot
     */
    private fun capturePerformanceSnapshot(): PerformanceSnapshot {
        val timestamp = System.currentTimeMillis()
        
        // Memory usage
        val memoryInfo = Debug.MemoryInfo()
        Debug.getMemoryInfo(memoryInfo)
        val totalMemoryKB = memoryInfo.totalPss
        val memoryUsagePercent = calculateMemoryUsagePercent(totalMemoryKB)
        currentMemoryUsage.set(memoryUsagePercent.toLong())
        
        // CPU usage
        val cpuUsagePercent = calculateCpuUsage()
        currentCpuUsage.set(cpuUsagePercent.toLong())
        
        // Calculate rates
        val frameDropRate = calculateFrameDropRate()
        val sampleDropRate = calculateSampleDropRate()
        val totalThroughputMbps = calculateTotalThroughputMbps()
        
        return PerformanceSnapshot(
            timestamp = timestamp,
            memoryUsagePercent = memoryUsagePercent,
            cpuUsagePercent = cpuUsagePercent,
            currentFPS = currentFPS.get().toDouble(),
            currentSampleRateHz = currentSampleRate.get().toDouble(),
            frameDropRate = frameDropRate,
            sampleDropRate = sampleDropRate,
            totalThroughputMbps = totalThroughputMbps,
            activeStreamCount = streamMetrics.size
        )
    }

    /**
     * Calculate memory usage percentage
     */
    private fun calculateMemoryUsagePercent(usedMemoryKB: Int): Double {
        return try {
            val runtime = Runtime.getRuntime()
            val maxMemoryKB = runtime.maxMemory() / 1024
            (usedMemoryKB.toDouble() / maxMemoryKB.toDouble()) * 100.0
        } catch (e: Exception) {
            Logger.w(TAG, "Could not calculate memory usage", e)
            0.0
        }
    }

    /**
     * Calculate CPU usage percentage
     */
    private fun calculateCpuUsage(): Double {
        return try {
            val statFile = RandomAccessFile("/proc/stat", "r")
            val cpuLine = statFile.readLine()
            statFile.close()
            
            val cpuTimes = cpuLine.split("\\s+".toRegex()).drop(1).map { it.toLong() }
            if (cpuTimes.size >= 4) {
                val idle = cpuTimes[3]
                val total = cpuTimes.sum()
                val usage = ((total - idle).toDouble() / total.toDouble()) * 100.0
                max(0.0, usage)
            } else {
                0.0
            }
        } catch (e: Exception) {
            Logger.w(TAG, "Could not calculate CPU usage", e)
            0.0
        }
    }

    /**
     * Calculate frame drop rate across all video streams
     */
    private fun calculateFrameDropRate(): Double {
        val expected = totalFramesExpected.get()
        val processed = totalFramesProcessed.get()
        
        return if (expected > 0) {
            max(0.0, (expected - processed).toDouble() / expected.toDouble())
        } else {
            0.0
        }
    }

    /**
     * Calculate sample drop rate across all sensor streams
     */
    private fun calculateSampleDropRate(): Double {
        val expected = totalSamplesExpected.get()
        val processed = totalSamplesProcessed.get()
        
        return if (expected > 0) {
            max(0.0, (expected - processed).toDouble() / expected.toDouble())
        } else {
            0.0
        }
    }

    /**
     * Calculate total data throughput in Mbps
     */
    private fun calculateTotalThroughputMbps(): Double {
        val recentBytes = streamMetrics.values.sumOf { it.getRecentThroughput(1000) }
        return (recentBytes * 8.0) / (1024.0 * 1024.0) // Convert to Mbps
    }

    /**
     * Update performance history with snapshot
     */
    private fun updatePerformanceHistory(snapshot: PerformanceSnapshot) {
        synchronized(performanceHistory) {
            performanceHistory.add(snapshot)
            
            // Keep only recent history
            if (performanceHistory.size > PERFORMANCE_HISTORY_SIZE) {
                performanceHistory.removeAt(0)
            }
        }
    }

    /**
     * Check performance thresholds and trigger alerts
     * NFR1: Performance alerting for bottlenecks
     */
    private fun checkPerformanceThresholds(snapshot: PerformanceSnapshot) {
        val alerts = mutableListOf<PerformanceAlert>()
        
        // Memory usage alert
        if (snapshot.memoryUsagePercent > MAX_MEMORY_USAGE_PERCENT) {
            alerts.add(PerformanceAlert(
                type = AlertType.HIGH_MEMORY_USAGE,
                message = "High memory usage: ${String.format("%.1f", snapshot.memoryUsagePercent)}%",
                severity = AlertSeverity.WARNING,
                value = snapshot.memoryUsagePercent
            ))
        }
        
        // CPU usage alert
        if (snapshot.cpuUsagePercent > MAX_CPU_USAGE_PERCENT) {
            alerts.add(PerformanceAlert(
                type = AlertType.HIGH_CPU_USAGE,
                message = "High CPU usage: ${String.format("%.1f", snapshot.cpuUsagePercent)}%",
                severity = AlertSeverity.WARNING,
                value = snapshot.cpuUsagePercent
            ))
        }
        
        // Frame drop rate alert
        if (snapshot.frameDropRate > MAX_ACCEPTABLE_FRAME_DROP_RATE) {
            alerts.add(PerformanceAlert(
                type = AlertType.HIGH_FRAME_DROP_RATE,
                message = "High frame drop rate: ${String.format("%.2f", snapshot.frameDropRate * 100)}%",
                severity = AlertSeverity.ERROR,
                value = snapshot.frameDropRate * 100
            ))
        }
        
        // Sample drop rate alert
        if (snapshot.sampleDropRate > MAX_ACCEPTABLE_SAMPLE_DROP_RATE) {
            alerts.add(PerformanceAlert(
                type = AlertType.HIGH_SAMPLE_DROP_RATE,
                message = "High sample drop rate: ${String.format("%.2f", snapshot.sampleDropRate * 100)}%",
                severity = AlertSeverity.ERROR,
                value = snapshot.sampleDropRate * 100
            ))
        }
        
        // Low performance alerts
        if (snapshot.currentFPS < TARGET_VIDEO_FPS * 0.9) { // 10% tolerance
            alerts.add(PerformanceAlert(
                type = AlertType.LOW_FRAME_RATE,
                message = "Low frame rate: ${String.format("%.1f", snapshot.currentFPS)} FPS (target: $TARGET_VIDEO_FPS)",
                severity = AlertSeverity.WARNING,
                value = snapshot.currentFPS
            ))
        }
        
        if (snapshot.currentSampleRateHz < TARGET_GSR_SAMPLE_RATE_HZ * 0.95) { // 5% tolerance
            alerts.add(PerformanceAlert(
                type = AlertType.LOW_SAMPLE_RATE,
                message = "Low sample rate: ${String.format("%.1f", snapshot.currentSampleRateHz)} Hz (target: $TARGET_GSR_SAMPLE_RATE_HZ)",
                severity = AlertSeverity.WARNING,
                value = snapshot.currentSampleRateHz
            ))
        }
        
        // Trigger alerts
        alerts.forEach { alert ->
            Logger.w(TAG, "Performance alert: ${alert.message}")
            performanceAlertCallback?.invoke(alert)
        }
    }

    /**
     * Reset performance counters
     */
    private fun resetCounters() {
        totalFramesExpected.set(0)
        totalFramesProcessed.set(0)
        totalSamplesExpected.set(0)
        totalSamplesProcessed.set(0)
        totalBytesWritten.set(0)
        currentFPS.set(0)
        currentSampleRate.set(0)
        currentMemoryUsage.set(0)
        currentCpuUsage.set(0)
        
        streamMetrics.clear()
        synchronized(performanceHistory) {
            performanceHistory.clear()
        }
    }

    /**
     * Set performance alert callback
     */
    fun setPerformanceAlertCallback(callback: (PerformanceAlert) -> Unit) {
        performanceAlertCallback = callback
    }

    /**
     * Get current performance metrics
     */
    fun getCurrentMetrics(): CurrentPerformanceMetrics {
        return CurrentPerformanceMetrics(
            isMonitoring = isMonitoring.get(),
            currentFPS = currentFPS.get().toDouble(),
            currentSampleRateHz = currentSampleRate.get().toDouble(),
            memoryUsagePercent = currentMemoryUsage.get().toDouble(),
            cpuUsagePercent = currentCpuUsage.get().toDouble(),
            frameDropRate = calculateFrameDropRate(),
            sampleDropRate = calculateSampleDropRate(),
            totalThroughputMbps = calculateTotalThroughputMbps(),
            activeStreams = streamMetrics.keys.toList()
        )
    }

    /**
     * Generate comprehensive performance report
     */
    fun generatePerformanceReport(): PerformanceReport {
        val history = synchronized(performanceHistory) { performanceHistory.toList() }
        
        val avgMemoryUsage = history.map { it.memoryUsagePercent }.average()
        val avgCpuUsage = history.map { it.cpuUsagePercent }.average()
        val avgFPS = history.map { it.currentFPS }.average()
        val avgSampleRate = history.map { it.currentSampleRateHz }.average()
        val avgThroughput = history.map { it.totalThroughputMbps }.average()
        
        val maxFrameDropRate = history.maxOfOrNull { it.frameDropRate } ?: 0.0
        val maxSampleDropRate = history.maxOfOrNull { it.sampleDropRate } ?: 0.0
        
        return PerformanceReport(
            totalFramesExpected = totalFramesExpected.get(),
            totalFramesProcessed = totalFramesProcessed.get(),
            totalSamplesExpected = totalSamplesExpected.get(),
            totalSamplesProcessed = totalSamplesProcessed.get(),
            totalBytesWritten = totalBytesWritten.get(),
            averageMemoryUsagePercent = avgMemoryUsage,
            averageCpuUsagePercent = avgCpuUsage,
            averageFPS = avgFPS,
            averageSampleRateHz = avgSampleRate,
            averageThroughputMbps = avgThroughput,
            maxFrameDropRate = maxFrameDropRate,
            maxSampleDropRate = maxSampleDropRate,
            meetsPerformanceTargets = meetsPerformanceTargets(avgFPS, avgSampleRate, maxFrameDropRate, maxSampleDropRate)
        )
    }

    /**
     * Check if performance meets NFR1 targets
     */
    private fun meetsPerformanceTargets(avgFPS: Double, avgSampleRate: Double, maxFrameDropRate: Double, maxSampleDropRate: Double): Boolean {
        return avgFPS >= TARGET_VIDEO_FPS * 0.9 &&
               avgSampleRate >= TARGET_GSR_SAMPLE_RATE_HZ * 0.95 &&
               maxFrameDropRate <= MAX_ACCEPTABLE_FRAME_DROP_RATE &&
               maxSampleDropRate <= MAX_ACCEPTABLE_SAMPLE_DROP_RATE
    }

    // Data classes and enums

    data class PerformanceSnapshot(
        val timestamp: Long,
        val memoryUsagePercent: Double,
        val cpuUsagePercent: Double,
        val currentFPS: Double,
        val currentSampleRateHz: Double,
        val frameDropRate: Double,
        val sampleDropRate: Double,
        val totalThroughputMbps: Double,
        val activeStreamCount: Int
    )

    data class CurrentPerformanceMetrics(
        val isMonitoring: Boolean,
        val currentFPS: Double,
        val currentSampleRateHz: Double,
        val memoryUsagePercent: Double,
        val cpuUsagePercent: Double,
        val frameDropRate: Double,
        val sampleDropRate: Double,
        val totalThroughputMbps: Double,
        val activeStreams: List<String>
    )

    data class PerformanceReport(
        val totalFramesExpected: Long,
        val totalFramesProcessed: Long,
        val totalSamplesExpected: Long,
        val totalSamplesProcessed: Long,
        val totalBytesWritten: Long,
        val averageMemoryUsagePercent: Double,
        val averageCpuUsagePercent: Double,
        val averageFPS: Double,
        val averageSampleRateHz: Double,
        val averageThroughputMbps: Double,
        val maxFrameDropRate: Double,
        val maxSampleDropRate: Double,
        val meetsPerformanceTargets: Boolean
    )

    data class PerformanceAlert(
        val type: AlertType,
        val message: String,
        val severity: AlertSeverity,
        val value: Double,
        val timestamp: Long = System.currentTimeMillis()
    )

    enum class AlertType {
        HIGH_MEMORY_USAGE,
        HIGH_CPU_USAGE,
        HIGH_FRAME_DROP_RATE,
        HIGH_SAMPLE_DROP_RATE,
        LOW_FRAME_RATE,
        LOW_SAMPLE_RATE
    }

    enum class AlertSeverity {
        INFO,
        WARNING,
        ERROR
    }

    enum class StreamType {
        VIDEO,
        SENSOR,
        DATA
    }

    /**
     * Stream-specific metrics tracking
     */
    private class StreamMetrics(val streamId: String, val type: StreamType) {
        private val frameTimestamps = mutableListOf<Long>()
        private val sampleTimestamps = mutableListOf<Long>()
        private val throughputData = mutableListOf<Pair<Long, Long>>() // timestamp, bytes
        private val expectedFrames = AtomicLong(0)
        private val expectedSamples = AtomicLong(0)

        fun recordFrame(expectedTime: Long, actualTime: Long) {
            synchronized(frameTimestamps) {
                frameTimestamps.add(actualTime)
                cleanOldData(frameTimestamps, 60000) // Keep 1 minute of data
            }
        }

        fun recordExpectedFrame() {
            expectedFrames.incrementAndGet()
        }

        fun recordSample(expectedTime: Long, actualTime: Long) {
            synchronized(sampleTimestamps) {
                sampleTimestamps.add(actualTime)
                cleanOldData(sampleTimestamps, 60000) // Keep 1 minute of data
            }
        }

        fun recordExpectedSample() {
            expectedSamples.incrementAndGet()
        }

        fun recordDataThroughput(bytes: Long) {
            val timestamp = System.currentTimeMillis()
            synchronized(throughputData) {
                throughputData.add(Pair(timestamp, bytes))
                // Clean old data (keep 1 minute)
                val cutoff = timestamp - 60000
                throughputData.removeAll { it.first < cutoff }
            }
        }

        fun getRecentFrameCount(periodMs: Long): Int {
            val cutoff = System.currentTimeMillis() - periodMs
            return synchronized(frameTimestamps) {
                frameTimestamps.count { it >= cutoff }
            }
        }

        fun getRecentSampleCount(periodMs: Long): Int {
            val cutoff = System.currentTimeMillis() - periodMs
            return synchronized(sampleTimestamps) {
                sampleTimestamps.count { it >= cutoff }
            }
        }

        fun getRecentThroughput(periodMs: Long): Long {
            val cutoff = System.currentTimeMillis() - periodMs
            return synchronized(throughputData) {
                throughputData.filter { it.first >= cutoff }.sumOf { it.second }
            }
        }

        private fun cleanOldData(list: MutableList<Long>, maxAgeMs: Long) {
            val cutoff = System.currentTimeMillis() - maxAgeMs
            list.removeAll { it < cutoff }
        }
    }
}