package com.multisensor.recording.network

import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import java.net.InetSocketAddress
import java.net.Socket
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.max
import kotlin.math.min

/**
 * NetworkQualityMonitor provides real-time network quality assessment for adaptive frame rate control.
 * 
 * This class monitors network latency and bandwidth to provide a quality score (1-5) that can be used
 * to dynamically adjust preview streaming frame rates for optimal performance.
 * 
 * Quality Scoring:
 * - 5 (Perfect): <50ms latency, >2Mbps bandwidth
 * - 4 (Excellent): <100ms latency, >1Mbps bandwidth  
 * - 3 (Good): <200ms latency, >500Kbps bandwidth
 * - 2 (Fair): <500ms latency, >100Kbps bandwidth
 * - 1 (Poor): >500ms latency or <100Kbps bandwidth
 */
@Singleton
class NetworkQualityMonitor @Inject constructor(
    private val logger: Logger
) {
    companion object {
        private const val MONITORING_INTERVAL_MS = 5000L // 5 seconds
        private const val LATENCY_SAMPLES = 3
        private const val BANDWIDTH_WINDOW_SIZE = 5
        private const val SOCKET_TIMEOUT_MS = 3000
        
        // Quality thresholds
        private const val PERFECT_LATENCY_MS = 50
        private const val EXCELLENT_LATENCY_MS = 100
        private const val GOOD_LATENCY_MS = 200
        private const val FAIR_LATENCY_MS = 500
        
        private const val PERFECT_BANDWIDTH_KBPS = 2000
        private const val EXCELLENT_BANDWIDTH_KBPS = 1000
        private const val GOOD_BANDWIDTH_KBPS = 500
        private const val FAIR_BANDWIDTH_KBPS = 100
    }
    
    data class NetworkQuality(
        val score: Int, // 1-5 quality score
        val latencyMs: Long,
        val bandwidthKbps: Double,
        val timestamp: Long = System.currentTimeMillis()
    )
    
    interface NetworkQualityListener {
        fun onNetworkQualityChanged(quality: NetworkQuality)
    }
    
    private var monitoringJob: Job? = null
    private var isMonitoring = false
    private val listeners = mutableSetOf<NetworkQualityListener>()
    
    // Network metrics tracking
    private val latencyHistory = mutableListOf<Long>()
    private val bandwidthHistory = mutableListOf<Double>()
    private var lastFrameTransmissionTime = 0L
    private var lastFrameSize = 0L
    
    // Current network state
    private var currentQuality = NetworkQuality(3, 100, 1000.0) // Default to "Good"
    private var serverHost = "192.168.1.100" // Default, will be updated
    private var serverPort = 8080
    
    /**
     * Starts network quality monitoring with periodic assessments
     */
    fun startMonitoring(host: String, port: Int) {
        if (isMonitoring) {
            logger.info("[DEBUG_LOG] NetworkQualityMonitor already monitoring")
            return
        }
        
        serverHost = host
        serverPort = port
        isMonitoring = true
        
        logger.info("[DEBUG_LOG] Starting network quality monitoring for $host:$port")
        
        monitoringJob = CoroutineScope(Dispatchers.IO).launch {
            while (isMonitoring) {
                try {
                    val quality = assessNetworkQuality()
                    updateNetworkQuality(quality)
                    delay(MONITORING_INTERVAL_MS)
                } catch (e: Exception) {
                    logger.error("Error during network quality assessment", e)
                    // Continue monitoring despite errors
                    delay(MONITORING_INTERVAL_MS)
                }
            }
        }
    }
    
    /**
     * Stops network quality monitoring
     */
    fun stopMonitoring() {
        logger.info("[DEBUG_LOG] Stopping network quality monitoring")
        isMonitoring = false
        monitoringJob?.cancel()
        monitoringJob = null
    }
    
    /**
     * Adds a listener for network quality changes
     */
    fun addListener(listener: NetworkQualityListener) {
        listeners.add(listener)
        // Immediately notify with current quality
        listener.onNetworkQualityChanged(currentQuality)
    }
    
    /**
     * Removes a network quality listener
     */
    fun removeListener(listener: NetworkQualityListener) {
        listeners.remove(listener)
    }
    
    /**
     * Records frame transmission metrics for bandwidth estimation
     */
    fun recordFrameTransmission(frameSizeBytes: Long) {
        val currentTime = System.currentTimeMillis()
        
        if (lastFrameTransmissionTime > 0) {
            val timeDeltaMs = currentTime - lastFrameTransmissionTime
            if (timeDeltaMs > 0) {
                // Calculate bandwidth in Kbps
                val bandwidth = (frameSizeBytes * 8.0) / (timeDeltaMs / 1000.0) / 1000.0
                addBandwidthSample(bandwidth)
            }
        }
        
        lastFrameTransmissionTime = currentTime
        lastFrameSize = frameSizeBytes
    }
    
    /**
     * Gets the current network quality assessment
     */
    fun getCurrentQuality(): NetworkQuality = currentQuality
    
    /**
     * Performs comprehensive network quality assessment
     */
    private suspend fun assessNetworkQuality(): NetworkQuality {
        val latency = measureLatency()
        val bandwidth = calculateAverageBandwidth()
        val score = calculateQualityScore(latency, bandwidth)
        
        logger.debug("[DEBUG_LOG] Network assessment - Latency: ${latency}ms, Bandwidth: ${bandwidth}Kbps, Score: $score")
        
        return NetworkQuality(score, latency, bandwidth)
    }
    
    /**
     * Measures network latency using socket connection time
     */
    private suspend fun measureLatency(): Long = withContext(Dispatchers.IO) {
        val latencies = mutableListOf<Long>()
        
        repeat(LATENCY_SAMPLES) {
            try {
                val startTime = System.currentTimeMillis()
                Socket().use { socket ->
                    socket.connect(InetSocketAddress(serverHost, serverPort), SOCKET_TIMEOUT_MS)
                }
                val latency = System.currentTimeMillis() - startTime
                latencies.add(latency)
            } catch (e: Exception) {
                logger.debug("Latency measurement failed: ${e.message}")
                latencies.add(SOCKET_TIMEOUT_MS.toLong()) // Use timeout as worst-case latency
            }
            
            if (it < LATENCY_SAMPLES - 1) {
                delay(100) // Small delay between samples
            }
        }
        
        val averageLatency = latencies.average().toLong()
        addLatencySample(averageLatency)
        return@withContext averageLatency
    }
    
    /**
     * Calculates average bandwidth from recent samples
     */
    private fun calculateAverageBandwidth(): Double {
        return if (bandwidthHistory.isNotEmpty()) {
            bandwidthHistory.average()
        } else {
            1000.0 // Default bandwidth estimate
        }
    }
    
    /**
     * Calculates quality score based on latency and bandwidth
     */
    private fun calculateQualityScore(latencyMs: Long, bandwidthKbps: Double): Int {
        val latencyScore = when {
            latencyMs <= PERFECT_LATENCY_MS -> 5
            latencyMs <= EXCELLENT_LATENCY_MS -> 4
            latencyMs <= GOOD_LATENCY_MS -> 3
            latencyMs <= FAIR_LATENCY_MS -> 2
            else -> 1
        }
        
        val bandwidthScore = when {
            bandwidthKbps >= PERFECT_BANDWIDTH_KBPS -> 5
            bandwidthKbps >= EXCELLENT_BANDWIDTH_KBPS -> 4
            bandwidthKbps >= GOOD_BANDWIDTH_KBPS -> 3
            bandwidthKbps >= FAIR_BANDWIDTH_KBPS -> 2
            else -> 1
        }
        
        // Use the minimum of latency and bandwidth scores for conservative assessment
        return min(latencyScore, bandwidthScore)
    }
    
    /**
     * Adds a latency sample to the history with size limiting
     */
    private fun addLatencySample(latency: Long) {
        latencyHistory.add(latency)
        if (latencyHistory.size > BANDWIDTH_WINDOW_SIZE) {
            latencyHistory.removeAt(0)
        }
    }
    
    /**
     * Adds a bandwidth sample to the history with size limiting
     */
    private fun addBandwidthSample(bandwidth: Double) {
        bandwidthHistory.add(bandwidth)
        if (bandwidthHistory.size > BANDWIDTH_WINDOW_SIZE) {
            bandwidthHistory.removeAt(0)
        }
    }
    
    /**
     * Updates current quality and notifies listeners if changed
     */
    private fun updateNetworkQuality(newQuality: NetworkQuality) {
        val qualityChanged = newQuality.score != currentQuality.score
        currentQuality = newQuality
        
        if (qualityChanged) {
            logger.info("[DEBUG_LOG] Network quality changed to score ${newQuality.score} (${getQualityDescription(newQuality.score)})")
            listeners.forEach { listener ->
                try {
                    listener.onNetworkQualityChanged(newQuality)
                } catch (e: Exception) {
                    logger.error("Error notifying network quality listener", e)
                }
            }
        }
    }
    
    /**
     * Gets human-readable description of quality score
     */
    private fun getQualityDescription(score: Int): String = when (score) {
        5 -> "Perfect"
        4 -> "Excellent"
        3 -> "Good"
        2 -> "Fair"
        1 -> "Poor"
        else -> "Unknown"
    }
    
    /**
     * Gets detailed network statistics for debugging
     */
    fun getNetworkStatistics(): String {
        return buildString {
            appendLine("Network Quality Statistics:")
            appendLine("  Current Score: ${currentQuality.score} (${getQualityDescription(currentQuality.score)})")
            appendLine("  Latency: ${currentQuality.latencyMs}ms")
            appendLine("  Bandwidth: ${String.format("%.1f", currentQuality.bandwidthKbps)}Kbps")
            appendLine("  Server: $serverHost:$serverPort")
            appendLine("  Monitoring: $isMonitoring")
            appendLine("  Latency History: ${latencyHistory.size} samples")
            appendLine("  Bandwidth History: ${bandwidthHistory.size} samples")
        }
    }
}
