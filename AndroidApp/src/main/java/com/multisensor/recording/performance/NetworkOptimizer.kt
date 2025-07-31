package com.multisensor.recording.performance

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Phase 3: Performance Optimization - Network Performance Tuning
 * 
 * Implements the Phase 3 requirement for network performance optimization
 * including message batching, compression, and bandwidth adaptation.
 */
@Singleton
class NetworkOptimizer @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {
    
    private val scope = CoroutineScope(Dispatchers.IO)
    private var monitoringJob: Job? = null
    private var listeners = mutableListOf<NetworkPerformanceListener>()
    
    private var currentBandwidth: Long = 0L
    private var currentLatency: Long = 0L
    private var compressionEnabled: Boolean = false
    private var batchingEnabled: Boolean = false
    private var adaptiveQualityEnabled: Boolean = true
    
    interface NetworkPerformanceListener {
        fun onBandwidthChanged(bandwidth: Long)
        fun onLatencyChanged(latency: Long)
        fun onCompressionStateChanged(enabled: Boolean)
        fun onBatchingStateChanged(enabled: Boolean)
    }
    
    /**
     * Start network optimization monitoring
     */
    fun startOptimization() {
        logger.info("NetworkOptimizer: Starting network optimization")
        
        monitoringJob = scope.launch {
            while (isActive) {
                try {
                    // Monitor network conditions
                    measureNetworkPerformance()
                    
                    // Apply optimizations based on current conditions
                    optimizeNetworkSettings()
                    
                    // Wait before next measurement
                    delay(5000) // 5 second intervals
                } catch (e: Exception) {
                    logger.error("NetworkOptimizer: Error during monitoring cycle", e)
                    delay(10000) // Longer delay on error
                }
            }
        }
    }
    
    /**
     * Stop network optimization monitoring
     */
    fun stopOptimization() {
        logger.info("NetworkOptimizer: Stopping network optimization")
        monitoringJob?.cancel()
        monitoringJob = null
    }
    
    /**
     * Add network performance listener
     */
    fun addListener(listener: NetworkPerformanceListener) {
        listeners.add(listener)
    }
    
    /**
     * Remove network performance listener
     */
    fun removeListener(listener: NetworkPerformanceListener) {
        listeners.remove(listener)
    }
    
    /**
     * Measure current network performance
     */
    private suspend fun measureNetworkPerformance() {
        try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = connectivityManager.activeNetwork
            val networkCapabilities = connectivityManager.getNetworkCapabilities(network)
            
            if (networkCapabilities != null) {
                // Estimate bandwidth based on network type
                val estimatedBandwidth = estimateBandwidth(networkCapabilities)
                
                // Measure latency (simplified - could ping a server)
                val estimatedLatency = estimateLatency(networkCapabilities)
                
                if (currentBandwidth != estimatedBandwidth) {
                    currentBandwidth = estimatedBandwidth
                    notifyBandwidthChange()
                }
                
                if (currentLatency != estimatedLatency) {
                    currentLatency = estimatedLatency
                    notifyLatencyChange()
                }
                
                logger.debug("NetworkOptimizer: Bandwidth: ${currentBandwidth}bps, Latency: ${currentLatency}ms")
            }
        } catch (e: Exception) {
            logger.error("NetworkOptimizer: Error measuring network performance", e)
        }
    }
    
    /**
     * Estimate bandwidth based on network capabilities
     */
    private fun estimateBandwidth(capabilities: NetworkCapabilities): Long {
        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> {
                if (capabilities.linkDownstreamBandwidthKbps > 0) {
                    capabilities.linkDownstreamBandwidthKbps * 1000L
                } else {
                    50_000_000L // 50 Mbps default for WiFi
                }
            }
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> {
                when {
                    capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED) -> 20_000_000L // 20 Mbps
                    else -> 5_000_000L // 5 Mbps for metered cellular
                }
            }
            else -> 1_000_000L // 1 Mbps default
        }
    }
    
    /**
     * Estimate latency based on network type
     */
    private fun estimateLatency(capabilities: NetworkCapabilities): Long {
        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> 20L // 20ms
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> 100L // 100ms
            else -> 200L // 200ms default
        }
    }
    
    /**
     * Optimize network settings based on current performance
     */
    private fun optimizeNetworkSettings() {
        // Enable compression for low bandwidth
        val shouldCompress = currentBandwidth < 5_000_000L // Less than 5 Mbps
        if (compressionEnabled != shouldCompress) {
            compressionEnabled = shouldCompress
            notifyCompressionStateChange()
            logger.info("NetworkOptimizer: Compression ${if (compressionEnabled) "enabled" else "disabled"}")
        }
        
        // Enable batching for high latency
        val shouldBatch = currentLatency > 100L // More than 100ms latency
        if (batchingEnabled != shouldBatch) {
            batchingEnabled = shouldBatch
            notifyBatchingStateChange()
            logger.info("NetworkOptimizer: Message batching ${if (batchingEnabled) "enabled" else "disabled"}")
        }
    }
    
    /**
     * Get current optimization settings
     */
    fun getOptimizationSettings(): NetworkOptimizationSettings {
        return NetworkOptimizationSettings(
            bandwidth = currentBandwidth,
            latency = currentLatency,
            compressionEnabled = compressionEnabled,
            batchingEnabled = batchingEnabled,
            adaptiveQualityEnabled = adaptiveQualityEnabled
        )
    }
    
    /**
     * Enable or disable adaptive quality
     */
    fun setAdaptiveQualityEnabled(enabled: Boolean) {
        adaptiveQualityEnabled = enabled
        logger.info("NetworkOptimizer: Adaptive quality ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Get recommended frame rate based on current network conditions
     */
    fun getRecommendedFrameRate(): Float {
        return when {
            currentBandwidth > 20_000_000L -> 5.0f // High bandwidth - 5 fps
            currentBandwidth > 10_000_000L -> 3.0f // Medium bandwidth - 3 fps
            currentBandwidth > 5_000_000L -> 2.0f // Low bandwidth - 2 fps
            else -> 1.0f // Very low bandwidth - 1 fps
        }
    }
    
    /**
     * Get recommended compression quality
     */
    fun getRecommendedCompressionQuality(): Int {
        return when {
            currentBandwidth > 20_000_000L -> 85 // High quality
            currentBandwidth > 10_000_000L -> 70 // Medium quality
            currentBandwidth > 5_000_000L -> 55 // Low quality
            else -> 40 // Very low quality
        }
    }
    
    private fun notifyBandwidthChange() {
        listeners.forEach { it.onBandwidthChanged(currentBandwidth) }
    }
    
    private fun notifyLatencyChange() {
        listeners.forEach { it.onLatencyChanged(currentLatency) }
    }
    
    private fun notifyCompressionStateChange() {
        listeners.forEach { it.onCompressionStateChanged(compressionEnabled) }
    }
    
    private fun notifyBatchingStateChange() {
        listeners.forEach { it.onBatchingStateChanged(batchingEnabled) }
    }
}

/**
 * Data class for network optimization settings
 */
data class NetworkOptimizationSettings(
    val bandwidth: Long,
    val latency: Long,
    val compressionEnabled: Boolean,
    val batchingEnabled: Boolean,
    val adaptiveQualityEnabled: Boolean
)