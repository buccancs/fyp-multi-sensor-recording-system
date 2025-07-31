package com.multisensor.recording.util

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import android.os.Debug
import android.os.Process
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.PrintWriter
import java.io.StringWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlin.system.measureTimeMillis

/**
 * Centralized Logging Utility for Multi-Sensor Recording System
 *
 * Enhanced comprehensive logging system providing:
 * - Standardized log tags and formatting
 * - Structured logging levels with performance monitoring
 * - Crash reporting and error tracking
 * - Memory and performance profiling
 * - Thread-safe operations with coroutine support
 * - Detailed system information logging
 * - File and network operation tracking
 *
 * Author: Multi-Sensor Recording System Team
 * Date: 2025-07-30
 */
object AppLogger {
    
    // Global log tag prefix
    private const val TAG_PREFIX = "MSR"
    
    // Log level control
    private var isDebugEnabled = true
    private var isVerboseEnabled = false
    
    // Performance tracking with thread-safe collections
    private val startTimes = ConcurrentHashMap<String, Long>()
    private val performanceStats = ConcurrentHashMap<String, PerformanceStats>()
    
    // Memory monitoring
    private var memoryMonitoringEnabled = true
    private var lastMemoryCheck = System.currentTimeMillis()
    private val memorySnapshots = mutableListOf<MemorySnapshot>()
    
    // Crash reporting
    private var crashHandler: Thread.UncaughtExceptionHandler? = null
    private var originalHandler: Thread.UncaughtExceptionHandler? = null
    
    // System information
    private var appContext: Context? = null
    private val logCounter = AtomicLong(0)
    
    // Date formatters
    private val dateFormatter = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault())
    private val fullDateFormatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault())
    
    /**
     * Data class for tracking performance statistics
     */
    data class PerformanceStats(
        val operationName: String,
        val totalCalls: Long,
        val totalTimeMs: Long,
        val minTimeMs: Long,
        val maxTimeMs: Long,
        val avgTimeMs: Long = if (totalCalls > 0) totalTimeMs / totalCalls else 0L
    )
    
    /**
     * Data class for memory snapshots
     */
    data class MemorySnapshot(
        val timestamp: Long,
        val context: String,
        val usedMemoryMB: Long,
        val freeMemoryMB: Long,
        val maxMemoryMB: Long,
        val nativeHeapSizeMB: Long,
        val threadCount: Int
    )
    
    /**
     * Initialize the enhanced logging system with application context
     */
    fun initialize(context: Context) {
        appContext = context
        setupCrashReporting()
        logSystemInfo()
        i("AppLogger", "Enhanced logging system initialized")
    }
    
    /**
     * Setup crash reporting to capture uncaught exceptions
     */
    private fun setupCrashReporting() {
        originalHandler = Thread.getDefaultUncaughtExceptionHandler()
        crashHandler = Thread.UncaughtExceptionHandler { thread, throwable ->
            logCrash(thread, throwable)
            originalHandler?.uncaughtException(thread, throwable)
        }
        Thread.setDefaultUncaughtExceptionHandler(crashHandler)
    }
    
    /**
     * Log system information on startup
     */
    private fun logSystemInfo() {
        i("SystemInfo", "=== SYSTEM INFORMATION ===")
        i("SystemInfo", "Device: ${Build.MANUFACTURER} ${Build.MODEL}")
        i("SystemInfo", "Android Version: ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
        i("SystemInfo", "App Process ID: ${Process.myPid()}")
        i("SystemInfo", "Available Processors: ${Runtime.getRuntime().availableProcessors()}")
        
        appContext?.let { context ->
            val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val memoryInfo = ActivityManager.MemoryInfo()
            activityManager.getMemoryInfo(memoryInfo)
            
            i("SystemInfo", "Total RAM: ${memoryInfo.totalMem / (1024 * 1024)} MB")
            i("SystemInfo", "Available RAM: ${memoryInfo.availMem / (1024 * 1024)} MB")
            i("SystemInfo", "Low Memory Threshold: ${memoryInfo.threshold / (1024 * 1024)} MB")
            i("SystemInfo", "Low Memory: ${memoryInfo.lowMemory}")
        }
        i("SystemInfo", "=== END SYSTEM INFORMATION ===")
    }
    
    /**
     * Enable or disable debug logging
     */
    fun setDebugEnabled(enabled: Boolean) {
        isDebugEnabled = enabled
        i("AppLogger", "Debug logging ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Enable or disable verbose logging
     */
    fun setVerboseEnabled(enabled: Boolean) {
        isVerboseEnabled = enabled
        i("AppLogger", "Verbose logging ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Enable or disable memory monitoring
     */
    fun setMemoryMonitoringEnabled(enabled: Boolean) {
        memoryMonitoringEnabled = enabled
        i("AppLogger", "Memory monitoring ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Get current logging statistics
     */
    fun getLoggingStats(): String {
        val totalLogs = logCounter.get()
        val performanceOps = performanceStats.size
        val memorySnapshots = memorySnapshots.size
        
        return "Logs: $totalLogs, Performance Ops: $performanceOps, Memory Snapshots: $memorySnapshots"
    }
    
    /**
     * Enhanced verbose logging with structured information
     */
    fun v(tag: String, message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) {
        if (isVerboseEnabled) {
            val structuredMessage = formatMessage(message, context)
            logToAndroid(Log.VERBOSE, tag, structuredMessage, throwable)
        }
    }
    
    /**
     * Enhanced debug logging with structured information
     */
    fun d(tag: String, message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) {
        if (isDebugEnabled) {
            val structuredMessage = formatMessage(message, context)
            logToAndroid(Log.DEBUG, tag, structuredMessage, throwable)
        }
    }
    
    /**
     * Enhanced info logging with structured information
     */
    fun i(tag: String, message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) {
        val structuredMessage = formatMessage(message, context)
        logToAndroid(Log.INFO, tag, structuredMessage, throwable)
    }
    
    /**
     * Enhanced warning logging with structured information
     */
    fun w(tag: String, message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) {
        val structuredMessage = formatMessage(message, context)
        logToAndroid(Log.WARN, tag, structuredMessage, throwable)
    }
    
    /**
     * Enhanced error logging with structured information
     */
    fun e(tag: String, message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) {
        val structuredMessage = formatMessage(message, context)
        logToAndroid(Log.ERROR, tag, structuredMessage, throwable)
    }
    
    /**
     * Internal method to format and log to Android logcat
     */
    private fun logToAndroid(priority: Int, tag: String, message: String, throwable: Throwable?) {
        val fullTag = "${TAG_PREFIX}_$tag"
        val timestamp = dateFormatter.format(Date())
        val threadName = Thread.currentThread().name
        val logId = logCounter.incrementAndGet()
        
        val fullMessage = "[$timestamp][#$logId][$threadName] $message"
        
        // Check memory usage periodically
        if (memoryMonitoringEnabled && priority >= Log.WARN) {
            checkMemoryUsage("Log Entry")
        }
        
        if (throwable != null) {
            Log.println(priority, fullTag, "$fullMessage\n${getStackTraceString(throwable)}")
        } else {
            Log.println(priority, fullTag, fullMessage)
        }
    }
    
    /**
     * Format message with optional context information
     */
    private fun formatMessage(message: String, context: Map<String, Any>?): String {
        return if (context.isNullOrEmpty()) {
            message
        } else {
            val contextStr = context.entries.joinToString(", ") { "${it.key}=${it.value}" }
            "$message [$contextStr]"
        }
    }
    
    /**
     * Get formatted stack trace string
     */
    private fun getStackTraceString(throwable: Throwable): String {
        val stringWriter = StringWriter()
        val printWriter = PrintWriter(stringWriter)
        throwable.printStackTrace(printWriter)
        return stringWriter.toString()
    }
    
    /**
     * Log method entry with optional parameters
     */
    fun logMethodEntry(tag: String, methodName: String, vararg params: Any?) {
        if (isDebugEnabled) {
            val paramString = if (params.isNotEmpty()) {
                " with params: ${params.joinToString(", ") { it?.toString() ?: "null" }}"
            } else {
                ""
            }
            d(tag, "→ Entering $methodName$paramString")
        }
    }
    
    /**
     * Log method exit with optional return value
     */
    fun logMethodExit(tag: String, methodName: String, returnValue: Any? = null) {
        if (isDebugEnabled) {
            val returnString = returnValue?.let { " returning: $it" } ?: ""
            d(tag, "← Exiting $methodName$returnString")
        }
    }
    
    /**
     * Log lifecycle events (onCreate, onStart, onResume, etc.)
     */
    fun logLifecycle(tag: String, lifecycleEvent: String, componentName: String? = null) {
        val component = componentName ?: tag
        i(tag, "🔄 Lifecycle: $component.$lifecycleEvent")
    }
    
    /**
     * Log network operations
     */
    fun logNetwork(tag: String, operation: String, endpoint: String? = null, status: String? = null) {
        val endpointInfo = endpoint?.let { " to $it" } ?: ""
        val statusInfo = status?.let { " - $it" } ?: ""
        i(tag, "🌐 Network: $operation$endpointInfo$statusInfo")
    }
    
    /**
     * Log recording operations
     */
    fun logRecording(tag: String, operation: String, deviceInfo: String? = null) {
        val deviceString = deviceInfo?.let { " ($it)" } ?: ""
        i(tag, "📹 Recording: $operation$deviceString")
    }
    
    /**
     * Log sensor operations
     */
    fun logSensor(tag: String, operation: String, sensorType: String? = null, value: String? = null) {
        val sensorInfo = sensorType?.let { " $it" } ?: ""
        val valueInfo = value?.let { " = $it" } ?: ""
        i(tag, "📊 Sensor$sensorInfo: $operation$valueInfo")
    }
    
    /**
     * Log file operations
     */
    fun logFile(tag: String, operation: String, fileName: String? = null, size: Long? = null) {
        val fileInfo = fileName?.let { " $it" } ?: ""
        val sizeInfo = size?.let { " (${formatFileSize(it)})" } ?: ""
        i(tag, "📁 File: $operation$fileInfo$sizeInfo")
    }
    
    /**
     * Enhanced start performance timing with automatic context detection
     */
    fun startTiming(tag: String, operationName: String, context: String? = null) {
        val key = "${tag}_$operationName"
        val fullKey = context?.let { "${key}_$it" } ?: key
        startTimes[fullKey] = System.nanoTime()
        d(tag, "⏱️ Started timing: $operationName${context?.let { " ($it)" } ?: ""}")
    }
    
    /**
     * Enhanced end performance timing with statistics tracking
     */
    fun endTiming(tag: String, operationName: String, context: String? = null): Long {
        val key = "${tag}_$operationName"
        val fullKey = context?.let { "${key}_$it" } ?: key
        val startTime = startTimes.remove(fullKey)
        
        return if (startTime != null) {
            val durationNanos = System.nanoTime() - startTime
            val durationMs = durationNanos / 1_000_000
            
            // Update performance statistics
            updatePerformanceStats(operationName, durationMs)
            
            val contextStr = context?.let { " ($it)" } ?: ""
            i(tag, "⏱️ Completed $operationName$contextStr in ${durationMs}ms", 
              context = mapOf("duration_ms" to durationMs, "operation" to operationName))
            
            durationMs
        } else {
            w(tag, "⏱️ No start time found for operation: $operationName${context?.let { " ($it)" } ?: ""}")
            -1L
        }
    }
    
    /**
     * Measure execution time of a code block
     */
    inline fun <T> measureTime(tag: String, operationName: String, block: () -> T): T {
        val startTime = System.nanoTime()
        return try {
            val result = block()
            val durationMs = (System.nanoTime() - startTime) / 1_000_000
            updatePerformanceStats(operationName, durationMs)
            
            i(tag, "⏱️ Measured $operationName in ${durationMs}ms",
              context = mapOf("duration_ms" to durationMs, "operation" to operationName))
            result
        } catch (e: Exception) {
            val durationMs = (System.nanoTime() - startTime) / 1_000_000
            e(tag, "⏱️ Failed $operationName after ${durationMs}ms", e,
              context = mapOf("duration_ms" to durationMs, "operation" to operationName))
            throw e
        }
    }
    
    /**
     * Update performance statistics for an operation
     */
    fun updatePerformanceStats(operationName: String, durationMs: Long) {
        performanceStats.compute(operationName) { _, existing ->
            if (existing == null) {
                PerformanceStats(
                    operationName = operationName,
                    totalCalls = 1,
                    totalTimeMs = durationMs,
                    minTimeMs = durationMs,
                    maxTimeMs = durationMs
                )
            } else {
                existing.copy(
                    totalCalls = existing.totalCalls + 1,
                    totalTimeMs = existing.totalTimeMs + durationMs,
                    minTimeMs = minOf(existing.minTimeMs, durationMs),
                    maxTimeMs = maxOf(existing.maxTimeMs, durationMs)
                )
            }
        }
    }
    
    /**
     * Get performance statistics for all operations
     */
    fun getPerformanceStats(): Map<String, PerformanceStats> = performanceStats.toMap()
    
    /**
     * Log current performance statistics
     */
    fun logPerformanceStats(tag: String) {
        if (performanceStats.isEmpty()) {
            i(tag, "📊 No performance statistics available")
            return
        }
        
        i(tag, "📊 Performance Statistics:")
        performanceStats.forEach { (operation, stats) ->
            i(tag, "  $operation: ${stats.totalCalls} calls, avg=${stats.avgTimeMs}ms, " +
                    "min=${stats.minTimeMs}ms, max=${stats.maxTimeMs}ms, total=${stats.totalTimeMs}ms")
        }
    }
    
    /**
     * Clear performance statistics
     */
    fun clearPerformanceStats() {
        performanceStats.clear()
        i("AppLogger", "📊 Performance statistics cleared")
    }
    
    /**
     * Enhanced memory usage logging with detailed information
     */
    fun logMemoryUsage(tag: String, context: String = "Memory Check") {
        if (!memoryMonitoringEnabled) return
        
        val runtime = Runtime.getRuntime()
        val maxMemory = runtime.maxMemory()
        val totalMemory = runtime.totalMemory()
        val freeMemory = runtime.freeMemory()
        val usedMemory = totalMemory - freeMemory
        
        // Native heap information
        val nativeHeapSize = Debug.getNativeHeapSize()
        val nativeHeapFree = Debug.getNativeHeapFreeSize()
        val nativeHeapUsed = nativeHeapSize - nativeHeapFree
        
        // Thread count
        val threadCount = Thread.activeCount()
        
        // Create memory snapshot
        val snapshot = MemorySnapshot(
            timestamp = System.currentTimeMillis(),
            context = context,
            usedMemoryMB = usedMemory / (1024 * 1024),
            freeMemoryMB = freeMemory / (1024 * 1024),
            maxMemoryMB = maxMemory / (1024 * 1024),
            nativeHeapSizeMB = nativeHeapSize / (1024 * 1024),
            threadCount = threadCount
        )
        
        // Store snapshot (keep only last 50)
        synchronized(memorySnapshots) {
            memorySnapshots.add(snapshot)
            if (memorySnapshots.size > 50) {
                memorySnapshots.removeAt(0)
            }
        }
        
        // Log memory information
        val memoryInfo = mapOf(
            "used_mb" to snapshot.usedMemoryMB,
            "free_mb" to snapshot.freeMemoryMB,
            "max_mb" to snapshot.maxMemoryMB,
            "native_heap_mb" to snapshot.nativeHeapSizeMB,
            "thread_count" to threadCount,
            "usage_percent" to ((usedMemory * 100) / maxMemory)
        )
        
        val level = when {
            (usedMemory * 100 / maxMemory) > 85 -> Log.WARN
            (usedMemory * 100 / maxMemory) > 70 -> Log.INFO
            else -> Log.DEBUG
        }
        
        val priority = if (level == Log.WARN) "WARNING" else "INFO"
        val logMessage = "💾 $context - Used: ${formatFileSize(usedMemory)}, " +
                "Free: ${formatFileSize(freeMemory)}, " +
                "Max: ${formatFileSize(maxMemory)}, " +
                "Native: ${formatFileSize(nativeHeapUsed)}, " +
                "Threads: $threadCount"
        
        when (level) {
            Log.WARN -> w(tag, logMessage, context = memoryInfo)
            Log.INFO -> i(tag, logMessage, context = memoryInfo)
            else -> d(tag, logMessage, context = memoryInfo)
        }
        
        lastMemoryCheck = System.currentTimeMillis()
    }
    
    /**
     * Check memory usage and log if threshold exceeded
     */
    private fun checkMemoryUsage(context: String) {
        val now = System.currentTimeMillis()
        if (now - lastMemoryCheck > 30000) { // Check every 30 seconds max
            logMemoryUsage("MemoryMonitor", context)
        }
    }
    
    /**
     * Get memory usage history
     */
    fun getMemorySnapshots(): List<MemorySnapshot> = synchronized(memorySnapshots) {
        memorySnapshots.toList()
    }
    
    /**
     * Force garbage collection and log memory impact
     */
    fun forceGarbageCollection(tag: String, context: String = "Manual GC") {
        val beforeMemory = Runtime.getRuntime().let { it.totalMemory() - it.freeMemory() }
        
        measureTime(tag, "garbage_collection") {
            System.gc()
            System.runFinalization()
            System.gc()
        }
        
        val afterMemory = Runtime.getRuntime().let { it.totalMemory() - it.freeMemory() }
        val freed = beforeMemory - afterMemory
        
        i(tag, "🗑️ $context - Freed ${formatFileSize(freed)} (${formatFileSize(beforeMemory)} → ${formatFileSize(afterMemory)})",
          context = mapOf(
              "freed_bytes" to freed,
              "before_bytes" to beforeMemory,
              "after_bytes" to afterMemory
          ))
    }
    
    /**
     * Log thread information
     */
    fun logThreadInfo(tag: String, context: String = "Thread Info") {
        val thread = Thread.currentThread()
        d(tag, "🧵 $context - Thread: ${thread.name}, ID: ${thread.id}, " +
                "State: ${thread.state}")
    }
    
    /**
     * Create a formatted error log with stack trace information
     */
    fun logError(tag: String, operation: String, error: Throwable) {
        e(tag, "❌ Failed $operation: ${error.message}", error)
    }
    
    /**
     * Log application state changes
     */
    fun logStateChange(tag: String, component: String, fromState: String, toState: String) {
        i(tag, "🔄 State Change: $component from '$fromState' to '$toState'")
    }
    
    /**
     * Format file size in human-readable format
     */
    private fun formatFileSize(bytes: Long): String {
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> "${bytes / 1024} KB"
            bytes < 1024 * 1024 * 1024 -> "${bytes / (1024 * 1024)} MB"
            else -> "${bytes / (1024 * 1024 * 1024)} GB"
        }
    }
    
    /**
     * Log crash information when uncaught exception occurs
     */
    private fun logCrash(thread: Thread, throwable: Throwable) {
        try {
            e("CrashReport", "=== UNCAUGHT EXCEPTION ===")
            e("CrashReport", "Thread: ${thread.name} (ID: ${thread.id})")
            e("CrashReport", "Exception: ${throwable::class.java.simpleName}")
            e("CrashReport", "Message: ${throwable.message}")
            e("CrashReport", "Stack trace:", throwable)
            
            // Log system state at crash time
            logSystemStateAtCrash()
            
            e("CrashReport", "=== END CRASH REPORT ===")
        } catch (e: Exception) {
            // Fallback logging in case of issues
            Log.e("${TAG_PREFIX}_CrashReport", "Failed to log crash details", e)
        }
    }
    
    /**
     * Log system state information during a crash
     */
    private fun logSystemStateAtCrash() {
        try {
            // Memory state
            val runtime = Runtime.getRuntime()
            e("CrashReport", "Memory - Used: ${formatFileSize(runtime.totalMemory() - runtime.freeMemory())}, " +
                    "Max: ${formatFileSize(runtime.maxMemory())}")
            
            // Thread information
            e("CrashReport", "Active Threads: ${Thread.activeCount()}")
            
            // Current performance operations
            if (startTimes.isNotEmpty()) {
                e("CrashReport", "Active Performance Timers: ${startTimes.keys.joinToString(", ")}")
            }
            
            // Recent memory snapshots
            synchronized(memorySnapshots) {
                if (memorySnapshots.isNotEmpty()) {
                    val recent = memorySnapshots.takeLast(3)
                    e("CrashReport", "Recent Memory Snapshots:")
                    recent.forEach { snapshot ->
                        e("CrashReport", "  ${snapshot.context}: ${snapshot.usedMemoryMB}MB used, ${snapshot.threadCount} threads")
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("${TAG_PREFIX}_CrashReport", "Failed to log system state", e)
        }
    }
    
    /**
     * Enhanced error logging with automatic stack trace and context
     */
    fun logError(tag: String, operation: String, error: Throwable, context: Map<String, Any>? = null) {
        val errorContext = mutableMapOf<String, Any>(
            "operation" to operation,
            "exception_type" to error::class.java.simpleName,
            "exception_message" to (error.message ?: "No message")
        )
        context?.let { errorContext.putAll(it) }
        
        e(tag, "❌ Failed $operation: ${error.message}", error, errorContext)
        
        // Log memory state on errors
        if (memoryMonitoringEnabled) {
            logMemoryUsage(tag, "Error Context: $operation")
        }
    }
    
    /**
     * Enhanced state change logging with transition timing
     */
    fun logStateChange(tag: String, component: String, fromState: String, toState: String, context: Map<String, Any>? = null) {
        val stateContext = mutableMapOf<String, Any>(
            "component" to component,
            "from_state" to fromState,
            "to_state" to toState,
            "transition_time" to System.currentTimeMillis()
        )
        context?.let { stateContext.putAll(it) }
        
        i(tag, "🔄 State Change: $component from '$fromState' to '$toState'", context = stateContext)
    }
    
    /**
     * Enhanced lifecycle logging with automatic timing
     */
    fun logLifecycle(tag: String, lifecycleEvent: String, componentName: String? = null, context: Map<String, Any>? = null) {
        val component = componentName ?: tag
        val lifecycleContext = mutableMapOf<String, Any>(
            "component" to component,
            "lifecycle_event" to lifecycleEvent,
            "timestamp" to System.currentTimeMillis()
        )
        context?.let { lifecycleContext.putAll(it) }
        
        i(tag, "🔄 Lifecycle: $component.$lifecycleEvent", context = lifecycleContext)
    }
    
    /**
     * Enhanced network operation logging
     */
    fun logNetwork(tag: String, operation: String, endpoint: String? = null, status: String? = null, 
                   responseTime: Long? = null, context: Map<String, Any>? = null) {
        val endpointInfo = endpoint?.let { " to $it" } ?: ""
        val statusInfo = status?.let { " - $it" } ?: ""
        val timeInfo = responseTime?.let { " (${it}ms)" } ?: ""
        
        val networkContext = mutableMapOf<String, Any>(
            "operation" to operation
        )
        endpoint?.let { networkContext["endpoint"] = it }
        status?.let { networkContext["status"] = it }
        responseTime?.let { networkContext["response_time_ms"] = it }
        context?.let { networkContext.putAll(it) }
        
        i(tag, "🌐 Network: $operation$endpointInfo$statusInfo$timeInfo", context = networkContext)
    }
    
    /**
     * Enhanced recording operation logging
     */
    fun logRecording(tag: String, operation: String, deviceInfo: String? = null, duration: Long? = null, 
                     fileSize: Long? = null, context: Map<String, Any>? = null) {
        val deviceString = deviceInfo?.let { " ($it)" } ?: ""
        val durationString = duration?.let { " ${it}ms" } ?: ""
        val sizeString = fileSize?.let { " ${formatFileSize(it)}" } ?: ""
        
        val recordingContext = mutableMapOf<String, Any>(
            "operation" to operation
        )
        deviceInfo?.let { recordingContext["device"] = it }
        duration?.let { recordingContext["duration_ms"] = it }
        fileSize?.let { recordingContext["file_size_bytes"] = it }
        context?.let { recordingContext.putAll(it) }
        
        i(tag, "📹 Recording: $operation$deviceString$durationString$sizeString", context = recordingContext)
    }
    
    /**
     * Enhanced sensor operation logging
     */
    fun logSensor(tag: String, operation: String, sensorType: String? = null, value: String? = null, 
                  accuracy: Int? = null, timestamp: Long? = null, context: Map<String, Any>? = null) {
        val sensorInfo = sensorType?.let { " $it" } ?: ""
        val valueInfo = value?.let { " = $it" } ?: ""
        val accuracyInfo = accuracy?.let { " (accuracy: $it)" } ?: ""
        
        val sensorContext = mutableMapOf<String, Any>(
            "operation" to operation
        )
        sensorType?.let { sensorContext["sensor_type"] = it }
        value?.let { sensorContext["value"] = it }
        accuracy?.let { sensorContext["accuracy"] = it }
        timestamp?.let { sensorContext["sensor_timestamp"] = it }
        context?.let { sensorContext.putAll(it) }
        
        i(tag, "📊 Sensor$sensorInfo: $operation$valueInfo$accuracyInfo", context = sensorContext)
    }
    
    /**
     * Enhanced file operation logging
     */
    fun logFile(tag: String, operation: String, fileName: String? = null, size: Long? = null, 
                duration: Long? = null, success: Boolean = true, context: Map<String, Any>? = null) {
        val fileInfo = fileName?.let { " $it" } ?: ""
        val sizeInfo = size?.let { " (${formatFileSize(it)})" } ?: ""
        val durationInfo = duration?.let { " in ${it}ms" } ?: ""
        val statusIcon = if (success) "📁" else "❌"
        
        val fileContext = mutableMapOf<String, Any>(
            "operation" to operation,
            "success" to success
        )
        fileName?.let { fileContext["file_name"] = it }
        size?.let { fileContext["file_size_bytes"] = it }
        duration?.let { fileContext["duration_ms"] = it }
        context?.let { fileContext.putAll(it) }
        
        val logLevel = if (success) Log.INFO else Log.WARN
        val message = "$statusIcon File: $operation$fileInfo$sizeInfo$durationInfo"
        
        when (logLevel) {
            Log.WARN -> w(tag, message, context = fileContext)
            else -> i(tag, message, context = fileContext)
        }
    }
    
}

/**
 * Extension functions for easy logging from any class
 */

/**
 * Get a simple class name for logging tag
 */
fun Any.getLogTag(): String = this::class.java.simpleName

/**
 * Quick access to verbose logging with context support
 */
fun Any.logV(message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) = 
    AppLogger.v(getLogTag(), message, throwable, context)

/**
 * Quick access to debug logging with context support
 */
fun Any.logD(message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) = 
    AppLogger.d(getLogTag(), message, throwable, context)

/**
 * Quick access to info logging with context support
 */
fun Any.logI(message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) = 
    AppLogger.i(getLogTag(), message, throwable, context)

/**
 * Quick access to warning logging with context support
 */
fun Any.logW(message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) = 
    AppLogger.w(getLogTag(), message, throwable, context)

/**
 * Quick access to error logging with context support
 */
fun Any.logE(message: String, throwable: Throwable? = null, context: Map<String, Any>? = null) = 
    AppLogger.e(getLogTag(), message, throwable, context)

/**
 * Quick access to performance timing
 */
fun Any.startTiming(operationName: String, context: String? = null) = 
    AppLogger.startTiming(getLogTag(), operationName, context)

/**
 * Quick access to end performance timing
 */
fun Any.endTiming(operationName: String, context: String? = null) = 
    AppLogger.endTiming(getLogTag(), operationName, context)

/**
 * Quick access to measure execution time
 */
inline fun <T> Any.measureTime(operationName: String, block: () -> T): T = 
    AppLogger.measureTime(getLogTag(), operationName, block)

/**
 * Quick access to memory usage logging
 */
fun Any.logMemory(context: String = "Memory Check") = 
    AppLogger.logMemoryUsage(getLogTag(), context)

/**
 * Quick access to error logging with operation context
 */
fun Any.logError(operation: String, error: Throwable, context: Map<String, Any>? = null) =
    AppLogger.logError(getLogTag(), operation, error, context)