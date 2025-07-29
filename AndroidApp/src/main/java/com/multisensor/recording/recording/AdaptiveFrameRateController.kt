package com.multisensor.recording.recording

import com.multisensor.recording.network.NetworkQualityMonitor
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.abs

/**
 * AdaptiveFrameRateController intelligently adjusts preview streaming frame rates based on network conditions.
 * 
 * This controller uses NetworkQualityMonitor feedback to optimize frame rates for the best possible
 * preview quality while preventing network congestion and ensuring smooth streaming performance.
 * 
 * Frame Rate Mapping:
 * - Quality 5 (Perfect): 5.0 fps - Maximum quality for excellent networks
 * - Quality 4 (Excellent): 3.0 fps - High quality for good networks
 * - Quality 3 (Good): 2.0 fps - Standard quality for average networks
 * - Quality 2 (Fair): 1.0 fps - Reduced quality for poor networks
 * - Quality 1 (Poor): 0.5 fps - Minimum quality for very poor networks
 * 
 * Features:
 * - Hysteresis to prevent rapid frame rate oscillations
 * - Manual override capability for fixed frame rates
 * - Smooth transitions with configurable adaptation delays
 * - Comprehensive logging and statistics
 */
@Singleton
class AdaptiveFrameRateController @Inject constructor(
    private val networkQualityMonitor: NetworkQualityMonitor,
    private val logger: Logger
) : NetworkQualityMonitor.NetworkQualityListener {
    
    companion object {
        // Frame rate mappings for each quality level
        private const val PERFECT_FRAME_RATE = 5.0f
        private const val EXCELLENT_FRAME_RATE = 3.0f
        private const val GOOD_FRAME_RATE = 2.0f
        private const val FAIR_FRAME_RATE = 1.0f
        private const val POOR_FRAME_RATE = 0.5f
        
        // Hysteresis settings to prevent oscillation
        private const val HYSTERESIS_THRESHOLD = 1 // Quality must change by this amount to trigger adaptation
        private const val ADAPTATION_DELAY_MS = 3000L // Minimum time between frame rate changes
        private const val STABILITY_WINDOW_SIZE = 3 // Number of consistent quality readings required
        
        // Default settings
        private const val DEFAULT_FRAME_RATE = GOOD_FRAME_RATE
        private const val MIN_FRAME_RATE = 0.1f
        private const val MAX_FRAME_RATE = 10.0f
    }
    
    data class FrameRateSettings(
        val currentFrameRate: Float,
        val targetFrameRate: Float,
        val networkQuality: Int,
        val isAdaptive: Boolean,
        val lastAdaptationTime: Long,
        val adaptationCount: Long
    )
    
    interface FrameRateChangeListener {
        fun onFrameRateChanged(newFrameRate: Float, reason: String)
        fun onAdaptationModeChanged(isAdaptive: Boolean)
    }
    
    // Current state
    private var currentFrameRate = DEFAULT_FRAME_RATE
    private var targetFrameRate = DEFAULT_FRAME_RATE
    private var isAdaptiveMode = true
    private var manualFrameRate = DEFAULT_FRAME_RATE
    
    // Adaptation control
    private var lastAdaptationTime = 0L
    private var lastQualityScore = 3 // Start with "Good" quality
    private var adaptationCount = 0L
    private val qualityHistory = mutableListOf<Int>()
    
    // Listeners
    private val listeners = mutableSetOf<FrameRateChangeListener>()
    
    // Coroutine management
    private var adaptationJob: Job? = null
    private var isActive = false
    
    /**
     * Starts the adaptive frame rate controller
     */
    fun start() {
        if (isActive) {
            logger.info("[DEBUG_LOG] AdaptiveFrameRateController already active")
            return
        }
        
        isActive = true
        logger.info("[DEBUG_LOG] Starting AdaptiveFrameRateController - Initial frame rate: ${currentFrameRate}fps")
        
        // Register for network quality updates
        networkQualityMonitor.addListener(this)
        
        // Start adaptation monitoring
        adaptationJob = CoroutineScope(Dispatchers.Main).launch {
            monitorAdaptation()
        }
    }
    
    /**
     * Stops the adaptive frame rate controller
     */
    fun stop() {
        logger.info("[DEBUG_LOG] Stopping AdaptiveFrameRateController")
        isActive = false
        
        // Unregister from network quality updates
        networkQualityMonitor.removeListener(this)
        
        // Cancel adaptation monitoring
        adaptationJob?.cancel()
        adaptationJob = null
    }
    
    /**
     * Adds a listener for frame rate changes
     */
    fun addListener(listener: FrameRateChangeListener) {
        listeners.add(listener)
        // Immediately notify with current state
        listener.onFrameRateChanged(currentFrameRate, "Initial state")
        listener.onAdaptationModeChanged(isAdaptiveMode)
    }
    
    /**
     * Removes a frame rate change listener
     */
    fun removeListener(listener: FrameRateChangeListener) {
        listeners.remove(listener)
    }
    
    /**
     * Sets manual frame rate and disables adaptive mode
     */
    fun setManualFrameRate(frameRate: Float) {
        val clampedFrameRate = frameRate.coerceIn(MIN_FRAME_RATE, MAX_FRAME_RATE)
        manualFrameRate = clampedFrameRate
        
        if (isAdaptiveMode) {
            isAdaptiveMode = false
            notifyAdaptationModeChanged()
        }
        
        updateFrameRate(clampedFrameRate, "Manual override to ${clampedFrameRate}fps")
        logger.info("[DEBUG_LOG] Manual frame rate set to ${clampedFrameRate}fps")
    }
    
    /**
     * Enables adaptive mode using network quality feedback
     */
    fun enableAdaptiveMode() {
        if (!isAdaptiveMode) {
            isAdaptiveMode = true
            notifyAdaptationModeChanged()
            
            // Immediately adapt to current network quality
            val currentQuality = networkQualityMonitor.getCurrentQuality()
            onNetworkQualityChanged(currentQuality)
            
            logger.info("[DEBUG_LOG] Adaptive mode enabled - Current quality: ${currentQuality.score}")
        }
    }
    
    /**
     * Gets current frame rate settings
     */
    fun getCurrentSettings(): FrameRateSettings {
        return FrameRateSettings(
            currentFrameRate = currentFrameRate,
            targetFrameRate = targetFrameRate,
            networkQuality = lastQualityScore,
            isAdaptive = isAdaptiveMode,
            lastAdaptationTime = lastAdaptationTime,
            adaptationCount = adaptationCount
        )
    }
    
    /**
     * Gets current frame rate
     */
    fun getCurrentFrameRate(): Float = currentFrameRate
    
    /**
     * Checks if adaptive mode is enabled
     */
    fun isAdaptiveModeEnabled(): Boolean = isAdaptiveMode
    
    /**
     * NetworkQualityMonitor.NetworkQualityListener implementation
     */
    override fun onNetworkQualityChanged(quality: NetworkQualityMonitor.NetworkQuality) {
        if (!isAdaptiveMode || !isActive) {
            return
        }
        
        addQualityToHistory(quality.score)
        
        // Check if we should adapt based on hysteresis and timing
        if (shouldAdaptFrameRate(quality.score)) {
            val newFrameRate = calculateOptimalFrameRate(quality.score)
            val reason = "Network quality ${quality.score} (${getQualityDescription(quality.score)})"
            
            updateFrameRate(newFrameRate, reason)
            lastAdaptationTime = System.currentTimeMillis()
            adaptationCount++
            
            logger.info("[DEBUG_LOG] Frame rate adapted to ${newFrameRate}fps due to $reason")
        }
        
        lastQualityScore = quality.score
    }
    
    /**
     * Determines if frame rate should be adapted based on current conditions
     */
    private fun shouldAdaptFrameRate(newQualityScore: Int): Boolean {
        val currentTime = System.currentTimeMillis()
        
        // Check adaptation delay
        if (currentTime - lastAdaptationTime < ADAPTATION_DELAY_MS) {
            return false
        }
        
        // Check hysteresis threshold
        val qualityDifference = abs(newQualityScore - lastQualityScore)
        if (qualityDifference < HYSTERESIS_THRESHOLD) {
            return false
        }
        
        // Check stability (require consistent quality readings)
        if (qualityHistory.size >= STABILITY_WINDOW_SIZE) {
            val recentQualities = qualityHistory.takeLast(STABILITY_WINDOW_SIZE)
            val isStable = recentQualities.all { abs(it - newQualityScore) <= 1 }
            if (!isStable) {
                return false
            }
        }
        
        return true
    }
    
    /**
     * Calculates optimal frame rate for given network quality
     */
    private fun calculateOptimalFrameRate(qualityScore: Int): Float {
        return when (qualityScore) {
            5 -> PERFECT_FRAME_RATE
            4 -> EXCELLENT_FRAME_RATE
            3 -> GOOD_FRAME_RATE
            2 -> FAIR_FRAME_RATE
            1 -> POOR_FRAME_RATE
            else -> DEFAULT_FRAME_RATE
        }
    }
    
    /**
     * Updates the current frame rate and notifies listeners
     */
    private fun updateFrameRate(newFrameRate: Float, reason: String) {
        if (newFrameRate != currentFrameRate) {
            val previousFrameRate = currentFrameRate
            currentFrameRate = newFrameRate
            targetFrameRate = newFrameRate
            
            logger.info("[DEBUG_LOG] Frame rate changed from ${previousFrameRate}fps to ${newFrameRate}fps - $reason")
            
            // Notify all listeners
            listeners.forEach { listener ->
                try {
                    listener.onFrameRateChanged(newFrameRate, reason)
                } catch (e: Exception) {
                    logger.error("Error notifying frame rate change listener", e)
                }
            }
        }
    }
    
    /**
     * Notifies listeners about adaptation mode changes
     */
    private fun notifyAdaptationModeChanged() {
        listeners.forEach { listener ->
            try {
                listener.onAdaptationModeChanged(isAdaptiveMode)
            } catch (e: Exception) {
                logger.error("Error notifying adaptation mode change listener", e)
            }
        }
    }
    
    /**
     * Adds quality score to history with size limiting
     */
    private fun addQualityToHistory(qualityScore: Int) {
        qualityHistory.add(qualityScore)
        if (qualityHistory.size > STABILITY_WINDOW_SIZE * 2) {
            qualityHistory.removeAt(0)
        }
    }
    
    /**
     * Monitors adaptation performance and logs statistics
     */
    private suspend fun monitorAdaptation() {
        while (isActive) {
            try {
                delay(30000) // Log statistics every 30 seconds
                
                if (isAdaptiveMode) {
                    logger.debug("[DEBUG_LOG] Adaptation statistics: ${getAdaptationStatistics()}")
                }
            } catch (e: Exception) {
                logger.error("Error in adaptation monitoring", e)
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
     * Gets detailed adaptation statistics for debugging
     */
    fun getAdaptationStatistics(): String {
        return buildString {
            appendLine("Adaptive Frame Rate Statistics:")
            appendLine("  Current Frame Rate: ${currentFrameRate}fps")
            appendLine("  Target Frame Rate: ${targetFrameRate}fps")
            appendLine("  Adaptive Mode: $isAdaptiveMode")
            appendLine("  Manual Frame Rate: ${manualFrameRate}fps")
            appendLine("  Network Quality: $lastQualityScore (${getQualityDescription(lastQualityScore)})")
            appendLine("  Total Adaptations: $adaptationCount")
            appendLine("  Last Adaptation: ${if (lastAdaptationTime > 0) "${System.currentTimeMillis() - lastAdaptationTime}ms ago" else "Never"}")
            appendLine("  Quality History: ${qualityHistory.takeLast(5)}")
            appendLine("  Active Listeners: ${listeners.size}")
        }
    }
    
    /**
     * Resets adaptation statistics and history
     */
    fun resetStatistics() {
        adaptationCount = 0
        lastAdaptationTime = 0
        qualityHistory.clear()
        logger.info("[DEBUG_LOG] Adaptation statistics reset")
    }
}
