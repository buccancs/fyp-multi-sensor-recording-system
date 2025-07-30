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

/**
 * Performance monitoring and optimization utility for the multi-sensor recording app.
 * Provides memory leak detection, performance metrics, and optimization recommendations.
 */
@Singleton
class PerformanceMonitor @Inject constructor(
    private val context: Context,
    private val logger: Logger
) : DefaultLifecycleObserver {

    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val handler = Handler(Looper.getMainLooper())
    
    // Performance metrics
    private val _performanceMetrics = MutableStateFlow(PerformanceMetrics())
    val performanceMetrics: StateFlow<PerformanceMetrics> = _performanceMetrics.asStateFlow()
    
    // Memory leak detection
    private val activityReferences = ConcurrentHashMap<String, WeakReference<Any>>()
    private val viewReferences = ConcurrentHashMap<String, WeakReference<Any>>()
    
    // Frame rate monitoring
    private var frameRateMonitoring = false
    private var lastFrameTime = 0L
    private var frameCount = 0
    private var currentFps = 0.0
    
    // Memory monitoring
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

    /**
     * Start comprehensive performance monitoring
     */
    private fun startPerformanceMonitoring() {
        performanceMonitoringJob = scope.launch {
            while (isActive) {
                try {
                    val metrics = collectPerformanceMetrics()
                    _performanceMetrics.value = metrics
                    
                    // Check for performance issues
                    analyzePerformance(metrics)
                    
                    delay(5000) // Update every 5 seconds
                } catch (e: Exception) {
                    logger.error("Performance monitoring error", e)
                }
            }
        }
    }

    /**
     * Start memory monitoring for leak detection
     */
    private fun startMemoryMonitoring() {
        memoryMonitoringJob = scope.launch {
            while (isActive) {
                try {
                    checkForMemoryLeaks()
                    monitorMemoryUsage()
                    delay(10000) // Check every 10 seconds
                } catch (e: Exception) {
                    logger.error("Memory monitoring error", e)
                }
            }
        }
    }

    /**
     * Stop memory monitoring
     */
    private fun stopMemoryMonitoring() {
        memoryMonitoringJob?.cancel()
        memoryMonitoringJob = null
    }

    /**
     * Collect current performance metrics
     */
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

    /**
     * Analyze performance metrics for issues
     */
    private fun analyzePerformance(metrics: PerformanceMetrics) {
        // High memory usage warning
        if (metrics.heapUtilization > 80) {
            logger.warning("High memory usage detected: ${metrics.heapUtilization.toInt()}%")
            triggerGarbageCollection()
        }
        
        // Low frame rate warning
        if (metrics.currentFps > 0 && metrics.currentFps < 45) {
            logger.warning("Low frame rate detected: ${metrics.currentFps} FPS")
        }
        
        // Too many active references
        if (metrics.activeActivityCount > 5) {
            logger.warning("High activity reference count: ${metrics.activeActivityCount}")
        }
        
        if (metrics.activeViewCount > 100) {
            logger.warning("High view reference count: ${metrics.activeViewCount}")
        }
    }

    /**
     * Check for potential memory leaks
     */
    private fun checkForMemoryLeaks() {
        // Check activity references
        val deadActivityRefs = mutableListOf<String>()
        activityReferences.forEach { (key, reference) ->
            if (reference.get() == null) {
                deadActivityRefs.add(key)
            }
        }
        deadActivityRefs.forEach { activityReferences.remove(it) }
        
        // Check view references
        val deadViewRefs = mutableListOf<String>()
        viewReferences.forEach { (key, reference) ->
            if (reference.get() == null) {
                deadViewRefs.add(key)
            }
        }
        deadViewRefs.forEach { viewReferences.remove(it) }
        
        // Log potential leaks
        if (activityReferences.size > 3) {
            logger.warning("Potential activity leak: ${activityReferences.size} active references")
        }
        
        if (viewReferences.size > 50) {
            logger.warning("Potential view leak: ${viewReferences.size} active references")
        }
    }

    /**
     * Monitor memory usage patterns
     */
    private fun monitorMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val totalMemory = runtime.totalMemory()
        val freeMemory = runtime.freeMemory()
        val usedMemory = totalMemory - freeMemory
        val maxMemory = runtime.maxMemory()
        
        val utilizationPercent = (usedMemory.toDouble() / maxMemory.toDouble()) * 100
        
        logger.debug("Memory usage: ${usedMemory / 1024 / 1024}MB / ${maxMemory / 1024 / 1024}MB (${utilizationPercent.toInt()}%)")
        
        // Trigger GC if memory usage is high
        if (utilizationPercent > 85) {
            triggerGarbageCollection()
        }
    }

    /**
     * Register activity for leak detection
     */
    fun registerActivity(activity: Any, name: String) {
        activityReferences[name] = WeakReference(activity)
        logger.debug("Registered activity: $name")
    }

    /**
     * Unregister activity
     */
    fun unregisterActivity(name: String) {
        activityReferences.remove(name)
        logger.debug("Unregistered activity: $name")
    }

    /**
     * Register view for leak detection
     */
    fun registerView(view: Any, name: String) {
        viewReferences[name] = WeakReference(view)
        logger.debug("Registered view: $name")
    }

    /**
     * Unregister view
     */
    fun unregisterView(name: String) {
        viewReferences.remove(name)
        logger.debug("Unregistered view: $name")
    }

    /**
     * Start frame rate monitoring
     */
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
                
                if (deltaTime >= 1_000_000_000) { // 1 second
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

    /**
     * Stop frame rate monitoring
     */
    fun stopFrameRateMonitoring() {
        frameRateMonitoring = false
        currentFps = 0.0
        logger.info("Frame rate monitoring stopped")
    }

    /**
     * Trigger garbage collection
     */
    fun triggerGarbageCollection() {
        logger.info("Triggering garbage collection")
        System.gc()
    }

    /**
     * Get performance recommendations based on current metrics
     */
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

    /**
     * Log performance summary
     */
    fun logPerformanceSummary() {
        val metrics = _performanceMetrics.value
        logger.info("Performance Summary:")
        logger.info("  Heap Usage: ${metrics.heapUsedMB.toInt()}MB / ${metrics.heapMaxMB.toInt()}MB (${metrics.heapUtilization.toInt()}%)")
        logger.info("  Native Heap: ${metrics.nativeHeapUsedMB.toInt()}MB")
        logger.info("  Frame Rate: ${metrics.currentFps.toInt()} FPS")
        logger.info("  Active References: ${metrics.activeActivityCount} activities, ${metrics.activeViewCount} views")
    }

    /**
     * Clean up resources
     */
    fun cleanup() {
        stopMemoryMonitoring()
        performanceMonitoringJob?.cancel()
        stopFrameRateMonitoring()
        activityReferences.clear()
        viewReferences.clear()
        scope.cancel()
        logger.info("Performance monitor cleaned up")
    }
}

/**
 * Performance metrics data class
 */
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

/**
 * Performance recommendation data class
 */
data class PerformanceRecommendation(
    val type: RecommendationType,
    val priority: Priority,
    val title: String,
    val description: String,
    val action: String
)

/**
 * Recommendation types
 */
enum class RecommendationType {
    MEMORY,
    PERFORMANCE,
    MEMORY_LEAK,
    BATTERY,
    NETWORK,
    STORAGE
}

/**
 * Priority levels
 */
enum class Priority {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

/**
 * Extension functions for performance monitoring
 */
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