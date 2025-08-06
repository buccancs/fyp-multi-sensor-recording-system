package com.multisensor.recording.util

import android.content.Context
import android.os.Debug
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ProcessLifecycleOwner
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.lang.ref.WeakReference
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PerformanceMonitor @Inject constructor(
    private val context: Context,
    private val logger: Logger
) : DefaultLifecycleObserver {

    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val handler = Handler(Looper.getMainLooper())

    private val _performanceMetrics = MutableStateFlow(PerformanceMetrics())
    val performanceMetrics: StateFlow<PerformanceMetrics> = _performanceMetrics.asStateFlow()

    private val activityReferences = ConcurrentHashMap<String, WeakReference<Any>>()
    private val viewReferences = ConcurrentHashMap<String, WeakReference<Any>>()
    
    // Stability action tracking
    private var lastMemoryStabilityAction = 0L
    private var lastPerformanceStabilityAction = 0L
    private var consecutiveHighUtilizationCount = 0
    private var stabilityActionsListener: StabilityActionsListener? = null
    
    // Thresholds for stability actions
    private val memoryStabilityActionCooldown = 30_000L // 30 seconds
    private val performanceStabilityActionCooldown = 15_000L // 15 seconds
    private val sustainedHighUtilizationThreshold = 3 // 3 consecutive measurements

    private var frameRateMonitoring = false
    private var lastFrameTime = 0L
    private var frameCount = 0
    private var currentFps = 0.0

    private var memoryMonitoringJob: Job? = null
    private var performanceMonitoringJob: Job? = null

    init {
        ProcessLifecycleOwner.get().lifecycle.addObserver(this)
        startPerformanceMonitoring()
    }

    override fun onStart(owner: LifecycleOwner) {
        super.onStart(owner)
        logger.info("App entered foreground - starting performance monitoring")
        startMemoryMonitoring()
    }

    override fun onStop(owner: LifecycleOwner) {
        super.onStop(owner)
        logger.info("App entered background - pausing performance monitoring")
        stopMemoryMonitoring()
    }

    private fun startPerformanceMonitoring() {
        performanceMonitoringJob = scope.launch {
            while (isActive) {
                try {
                    val metrics = collectPerformanceMetrics()
                    _performanceMetrics.value = metrics

                    analyzePerformance(metrics)

                    delay(5000)
                } catch (e: Exception) {
                    logger.error("Performance monitoring error", e)
                }
            }
        }
    }

    private fun startMemoryMonitoring() {
        memoryMonitoringJob = scope.launch {
            while (isActive) {
                try {
                    checkForMemoryLeaks()
                    monitorMemoryUsage()
                    delay(10000)
                } catch (e: Exception) {
                    logger.error("Memory monitoring error", e)
                }
            }
        }
    }

    private fun stopMemoryMonitoring() {
        memoryMonitoringJob?.cancel()
        memoryMonitoringJob = null
    }

    private fun collectPerformanceMetrics(): PerformanceMetrics {
        val runtime = Runtime.getRuntime()
        val memoryInfo = Debug.MemoryInfo()
        Debug.getMemoryInfo(memoryInfo)

        val totalMemory = runtime.totalMemory()
        val freeMemory = runtime.freeMemory()
        val usedMemory = totalMemory - freeMemory
        val maxMemory = runtime.maxMemory()

        return PerformanceMetrics(
            heapUsedMB = (usedMemory / 1024 / 1024).toDouble(),
            heapMaxMB = (maxMemory / 1024 / 1024).toDouble(),
            heapUtilization = (usedMemory.toDouble() / maxMemory.toDouble()) * 100,
            nativeHeapUsedMB = (memoryInfo.nativePss / 1024.0),
            currentFps = currentFps,
            activeActivityCount = activityReferences.size,
            activeViewCount = viewReferences.size,
            timestamp = System.currentTimeMillis()
        )
    }

    private fun analyzePerformance(metrics: PerformanceMetrics) {
        // Critical memory threshold - proactive action required
        if (metrics.heapUtilization > 85) {
            logger.error("CRITICAL: Memory usage at ${metrics.heapUtilization.toInt()}% - triggering stability actions")
            triggerMemoryStabilityActions(metrics)
        } else if (metrics.heapUtilization > 80) {
            logger.warning("High memory usage detected: ${metrics.heapUtilization.toInt()}%")
            triggerGarbageCollection()
        }

        // Frame rate monitoring with adaptive response
        if (metrics.currentFps > 0) {
            if (metrics.currentFps < 30) {
                logger.error("CRITICAL: Very low frame rate: ${metrics.currentFps} FPS - triggering performance actions")
                triggerPerformanceStabilityActions(metrics)
            } else if (metrics.currentFps < 45) {
                logger.warning("Low frame rate detected: ${metrics.currentFps} FPS")
                // Trigger lighter optimizations
                triggerLightPerformanceOptimizations()
            }
        }

        // Potential memory leak detection
        if (metrics.activeActivityCount > 5) {
            logger.warning("POTENTIAL LEAK: High activity reference count: ${metrics.activeActivityCount}")
            triggerLeakDetectionActions()
        }

        if (metrics.activeViewCount > 100) {
            logger.warning("POTENTIAL LEAK: High view reference count: ${metrics.activeViewCount}")
            triggerLeakDetectionActions()
        }

        // Check for sustained high utilization
        checkForSustainedHighUtilization(metrics)
    }

    private fun checkForMemoryLeaks() {
        val deadActivityRefs = mutableListOf<String>()
        activityReferences.forEach { (key, reference) ->
            if (reference.get() == null) {
                deadActivityRefs.add(key)
            }
        }
        deadActivityRefs.forEach { activityReferences.remove(it) }

        val deadViewRefs = mutableListOf<String>()
        viewReferences.forEach { (key, reference) ->
            if (reference.get() == null) {
                deadViewRefs.add(key)
            }
        }
        deadViewRefs.forEach { viewReferences.remove(it) }

        if (activityReferences.size > 3) {
            logger.warning("Potential activity leak: ${activityReferences.size} active references")
        }

        if (viewReferences.size > 50) {
            logger.warning("Potential view leak: ${viewReferences.size} active references")
        }
    }

    private fun monitorMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val totalMemory = runtime.totalMemory()
        val freeMemory = runtime.freeMemory()
        val usedMemory = totalMemory - freeMemory
        val maxMemory = runtime.maxMemory()

        val utilizationPercent = (usedMemory.toDouble() / maxMemory.toDouble()) * 100

        logger.debug("Memory usage: ${usedMemory / 1024 / 1024}MB / ${maxMemory / 1024 / 1024}MB (${utilizationPercent.toInt()}%)")

        if (utilizationPercent > 85) {
            triggerGarbageCollection()
        }
    }

    fun registerActivity(activity: Any, name: String) {
        activityReferences[name] = WeakReference(activity)
        logger.debug("Registered activity: $name")
    }

    fun unregisterActivity(name: String) {
        activityReferences.remove(name)
        logger.debug("Unregistered activity: $name")
    }

    fun registerView(view: Any, name: String) {
        viewReferences[name] = WeakReference(view)
        logger.debug("Registered view: $name")
    }

    fun unregisterView(name: String) {
        viewReferences.remove(name)
        logger.debug("Unregistered view: $name")
    }

    fun startFrameRateMonitoring() {
        if (frameRateMonitoring) return

        frameRateMonitoring = true
        lastFrameTime = System.nanoTime()
        frameCount = 0

        val frameCallback = object : android.view.Choreographer.FrameCallback {
            override fun doFrame(frameTimeNanos: Long) {
                if (!frameRateMonitoring) return

                frameCount++
                val currentTime = System.nanoTime()
                val deltaTime = currentTime - lastFrameTime

                if (deltaTime >= 1_000_000_000) {
                    currentFps = frameCount * 1_000_000_000.0 / deltaTime
                    frameCount = 0
                    lastFrameTime = currentTime
                }

                android.view.Choreographer.getInstance().postFrameCallback(this)
            }
        }

        android.view.Choreographer.getInstance().postFrameCallback(frameCallback)
        logger.info("Frame rate monitoring started")
    }

    fun stopFrameRateMonitoring() {
        frameRateMonitoring = false
        currentFps = 0.0
        logger.info("Frame rate monitoring stopped")
    }

    fun triggerGarbageCollection() {
        logger.info("Triggering garbage collection")
        System.gc()
    }

    fun getPerformanceRecommendations(): List<PerformanceRecommendation> {
        val metrics = _performanceMetrics.value
        val recommendations = mutableListOf<PerformanceRecommendation>()

        if (metrics.heapUtilization > 80) {
            recommendations.add(
                PerformanceRecommendation(
                    type = RecommendationType.MEMORY,
                    priority = Priority.HIGH,
                    title = "High Memory Usage",
                    description = "Memory usage is at ${metrics.heapUtilization.toInt()}%. Consider closing other apps or reducing recording quality.",
                    action = "Reduce video quality or close background apps"
                )
            )
        }

        if (metrics.currentFps > 0 && metrics.currentFps < 45) {
            recommendations.add(
                PerformanceRecommendation(
                    type = RecommendationType.PERFORMANCE,
                    priority = Priority.MEDIUM,
                    title = "Low Frame Rate",
                    description = "Frame rate is ${metrics.currentFps.toInt()} FPS. This may affect recording quality.",
                    action = "Close other apps or reduce camera resolution"
                )
            )
        }

        if (metrics.activeActivityCount > 5) {
            recommendations.add(
                PerformanceRecommendation(
                    type = RecommendationType.MEMORY_LEAK,
                    priority = Priority.HIGH,
                    title = "Potential Memory Leak",
                    description = "High number of active activities detected.",
                    action = "Restart the app if performance degrades"
                )
            )
        }

        return recommendations
    }

    fun logPerformanceSummary() {
        val metrics = _performanceMetrics.value
        logger.info("Performance Summary:")
        logger.info("  Heap Usage: ${metrics.heapUsedMB.toInt()}MB / ${metrics.heapMaxMB.toInt()}MB (${metrics.heapUtilization.toInt()}%)")
        logger.info("  Native Heap: ${metrics.nativeHeapUsedMB.toInt()}MB")
        logger.info("  Frame Rate: ${metrics.currentFps.toInt()} FPS")
        logger.info("  Active References: ${metrics.activeActivityCount} activities, ${metrics.activeViewCount} views")
    }

    fun cleanup() {
        stopMemoryMonitoring()
        performanceMonitoringJob?.cancel()
        stopFrameRateMonitoring()
        activityReferences.clear()
        viewReferences.clear()
        stabilityActionsListener = null
        scope.cancel()
        logger.info("Performance monitor cleaned up")
    }
    
    /**
     * Interface for receiving stability action notifications.
     */
    interface StabilityActionsListener {
        fun onMemoryPressureDetected(utilizationPercent: Double)
        fun onPerformanceDegradation(fps: Double)
        fun onSustainedHighUtilization()
        fun onPotentialLeakDetected(activityCount: Int, viewCount: Int)
        fun onStabilityActionRequired(actionType: StabilityActionType)
    }
    
    /**
     * Sets a listener for stability action notifications.
     */
    fun setStabilityActionsListener(listener: StabilityActionsListener) {
        this.stabilityActionsListener = listener
        logger.info("$TAG: Stability actions listener set")
    }
    
    /**
     * Triggers memory stability actions when critical thresholds are exceeded.
     */
    private fun triggerMemoryStabilityActions(metrics: PerformanceMetrics) {
        val currentTime = System.currentTimeMillis()
        
        // Prevent too frequent stability actions
        if (currentTime - lastMemoryStabilityAction < memoryStabilityActionCooldown) {
            logger.debug("$TAG: Memory stability action skipped - cooldown period")
            return
        }
        
        lastMemoryStabilityAction = currentTime
        logger.warning("$TAG: Triggering memory stability actions - utilization: ${metrics.heapUtilization.toInt()}%")
        
        // Immediate actions
        triggerGarbageCollection()
        
        // Notify listener for additional actions
        stabilityActionsListener?.let { listener ->
            scope.launch(Dispatchers.Main) {
                try {
                    listener.onMemoryPressureDetected(metrics.heapUtilization)
                    listener.onStabilityActionRequired(StabilityActionType.MEMORY_PRESSURE)
                } catch (e: Exception) {
                    logger.error("$TAG: Error notifying stability actions listener", e)
                }
            }
        }
    }
    
    /**
     * Triggers performance stability actions when frame rate drops critically.
     */
    private fun triggerPerformanceStabilityActions(metrics: PerformanceMetrics) {
        val currentTime = System.currentTimeMillis()
        
        if (currentTime - lastPerformanceStabilityAction < performanceStabilityActionCooldown) {
            logger.debug("$TAG: Performance stability action skipped - cooldown period")
            return
        }
        
        lastPerformanceStabilityAction = currentTime
        logger.warning("$TAG: Triggering performance stability actions - FPS: ${metrics.currentFps}")
        
        // Notify listener for performance-related actions
        stabilityActionsListener?.let { listener ->
            scope.launch(Dispatchers.Main) {
                try {
                    listener.onPerformanceDegradation(metrics.currentFps)
                    listener.onStabilityActionRequired(StabilityActionType.PERFORMANCE_DEGRADATION)
                } catch (e: Exception) {
                    logger.error("$TAG: Error notifying stability actions listener", e)
                }
            }
        }
    }
    
    /**
     * Triggers lighter performance optimizations for moderate issues.
     */
    private fun triggerLightPerformanceOptimizations() {
        logger.info("$TAG: Triggering light performance optimizations")
        
        // Request garbage collection
        triggerGarbageCollection()
        
        // Notify for light optimizations
        stabilityActionsListener?.let { listener ->
            scope.launch(Dispatchers.Main) {
                try {
                    listener.onStabilityActionRequired(StabilityActionType.LIGHT_OPTIMIZATION)
                } catch (e: Exception) {
                    logger.error("$TAG: Error notifying stability actions listener", e)
                }
            }
        }
    }
    
    /**
     * Triggers actions when potential memory leaks are detected.
     */
    private fun triggerLeakDetectionActions() {
        logger.warning("$TAG: Triggering leak detection actions")
        
        val activityCount = activityReferences.size
        val viewCount = viewReferences.size
        
        // Force cleanup of dead references
        checkForMemoryLeaks()
        
        // Notify listener
        stabilityActionsListener?.let { listener ->
            scope.launch(Dispatchers.Main) {
                try {
                    listener.onPotentialLeakDetected(activityCount, viewCount)
                    listener.onStabilityActionRequired(StabilityActionType.LEAK_DETECTION)
                } catch (e: Exception) {
                    logger.error("$TAG: Error notifying stability actions listener", e)
                }
            }
        }
    }
    
    /**
     * Checks for sustained high utilization and triggers appropriate actions.
     */
    private fun checkForSustainedHighUtilization(metrics: PerformanceMetrics) {
        if (metrics.heapUtilization > 75 || (metrics.currentFps > 0 && metrics.currentFps < 40)) {
            consecutiveHighUtilizationCount++
            
            if (consecutiveHighUtilizationCount >= sustainedHighUtilizationThreshold) {
                logger.error("$TAG: Sustained high utilization detected for $consecutiveHighUtilizationCount measurements")
                
                stabilityActionsListener?.let { listener ->
                    scope.launch(Dispatchers.Main) {
                        try {
                            listener.onSustainedHighUtilization()
                            listener.onStabilityActionRequired(StabilityActionType.SUSTAINED_HIGH_UTILIZATION)
                        } catch (e: Exception) {
                            logger.error("$TAG: Error notifying stability actions listener", e)
                        }
                    }
                }
                
                // Reset counter after triggering action
                consecutiveHighUtilizationCount = 0
            }
        } else {
            // Reset counter if metrics are good
            consecutiveHighUtilizationCount = 0
        }
    }
}

data class PerformanceMetrics(
    val heapUsedMB: Double = 0.0,
    val heapMaxMB: Double = 0.0,
    val heapUtilization: Double = 0.0,
    val nativeHeapUsedMB: Double = 0.0,
    val currentFps: Double = 0.0,
    val activeActivityCount: Int = 0,
    val activeViewCount: Int = 0,
    val timestamp: Long = 0L
)

data class PerformanceRecommendation(
    val type: RecommendationType,
    val priority: Priority,
    val title: String,
    val description: String,
    val action: String
)

enum class RecommendationType {
    MEMORY,
    PERFORMANCE,
    MEMORY_LEAK,
    BATTERY,
    NETWORK,
    STORAGE
}

enum class Priority {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

/**
 * Types of stability actions that can be triggered by the performance monitor.
 */
enum class StabilityActionType {
    MEMORY_PRESSURE,                // Critical memory usage detected
    PERFORMANCE_DEGRADATION,        // Significant frame rate drop
    LIGHT_OPTIMIZATION,            // Minor optimizations needed
    LEAK_DETECTION,                // Potential memory leak detected
    SUSTAINED_HIGH_UTILIZATION     // Extended period of high resource usage
}

fun PerformanceMonitor.monitorCoroutine(
    name: String,
    block: suspend CoroutineScope.() -> Unit
): Job {
    return CoroutineScope(Dispatchers.Default).launch {
        val startTime = System.currentTimeMillis()
        try {
            block()
        } finally {
            val duration = System.currentTimeMillis() - startTime
            Log.d("PerformanceMonitor", "Coroutine '$name' completed in ${duration}ms")
        }
    }
}

fun PerformanceMonitor.measureExecutionTime(
    name: String,
    block: () -> Unit
): Long {
    val startTime = System.currentTimeMillis()
    block()
    val duration = System.currentTimeMillis() - startTime
    Log.d("PerformanceMonitor", "Operation '$name' completed in ${duration}ms")
    return duration
}