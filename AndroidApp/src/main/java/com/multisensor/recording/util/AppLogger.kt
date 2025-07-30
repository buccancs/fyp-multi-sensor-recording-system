package com.multisensor.recording.util

import android.util.Log
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Centralized Logging Utility for Multi-Sensor Recording System
 *
 * Provides consistent logging across all Android components with:
 * - Standardized log tags and formatting
 * - Structured logging levels
 * - Optional detailed logging for debugging
 * - Performance tracking utilities
 * - Thread-safe operations
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
    
    // Performance tracking
    private val startTimes = mutableMapOf<String, Long>()
    
    // Date formatter for timestamps
    private val dateFormatter = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault())
    
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
     * Verbose logging - most detailed level
     */
    fun v(tag: String, message: String, throwable: Throwable? = null) {
        if (isVerboseEnabled) {
            val fullTag = "${TAG_PREFIX}_$tag"
            val timestamp = dateFormatter.format(Date())
            val threadName = Thread.currentThread().name
            val fullMessage = "[$timestamp][$threadName] $message"
            
            if (throwable != null) {
                Log.v(fullTag, fullMessage, throwable)
            } else {
                Log.v(fullTag, fullMessage)
            }
        }
    }
    
    /**
     * Debug logging - detailed information for troubleshooting
     */
    fun d(tag: String, message: String, throwable: Throwable? = null) {
        if (isDebugEnabled) {
            val fullTag = "${TAG_PREFIX}_$tag"
            val timestamp = dateFormatter.format(Date())
            val threadName = Thread.currentThread().name
            val fullMessage = "[$timestamp][$threadName] $message"
            
            if (throwable != null) {
                Log.d(fullTag, fullMessage, throwable)
            } else {
                Log.d(fullTag, fullMessage)
            }
        }
    }
    
    /**
     * Info logging - general information about app operations
     */
    fun i(tag: String, message: String, throwable: Throwable? = null) {
        val fullTag = "${TAG_PREFIX}_$tag"
        val timestamp = dateFormatter.format(Date())
        val fullMessage = "[$timestamp] $message"
        
        if (throwable != null) {
            Log.i(fullTag, fullMessage, throwable)
        } else {
            Log.i(fullTag, fullMessage)
        }
    }
    
    /**
     * Warning logging - potential issues that don't stop execution
     */
    fun w(tag: String, message: String, throwable: Throwable? = null) {
        val fullTag = "${TAG_PREFIX}_$tag"
        val timestamp = dateFormatter.format(Date())
        val fullMessage = "[$timestamp] WARNING: $message"
        
        if (throwable != null) {
            Log.w(fullTag, fullMessage, throwable)
        } else {
            Log.w(fullTag, fullMessage)
        }
    }
    
    /**
     * Error logging - errors that affect functionality
     */
    fun e(tag: String, message: String, throwable: Throwable? = null) {
        val fullTag = "${TAG_PREFIX}_$tag"
        val timestamp = dateFormatter.format(Date())
        val fullMessage = "[$timestamp] ERROR: $message"
        
        if (throwable != null) {
            Log.e(fullTag, fullMessage, throwable)
        } else {
            Log.e(fullTag, fullMessage)
        }
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
     * Start performance timing
     */
    fun startTiming(tag: String, operationName: String) {
        val key = "${tag}_$operationName"
        startTimes[key] = System.currentTimeMillis()
        d(tag, "⏱️ Started timing: $operationName")
    }
    
    /**
     * End performance timing and log duration
     */
    fun endTiming(tag: String, operationName: String) {
        val key = "${tag}_$operationName"
        val startTime = startTimes.remove(key)
        if (startTime != null) {
            val duration = System.currentTimeMillis() - startTime
            i(tag, "⏱️ Completed $operationName in ${duration}ms")
        } else {
            w(tag, "⏱️ No start time found for operation: $operationName")
        }
    }
    
    /**
     * Log memory usage information
     */
    fun logMemoryUsage(tag: String, context: String = "Memory Check") {
        val runtime = Runtime.getRuntime()
        val maxMemory = runtime.maxMemory()
        val totalMemory = runtime.totalMemory()
        val freeMemory = runtime.freeMemory()
        val usedMemory = totalMemory - freeMemory
        
        d(tag, "💾 $context - Used: ${formatFileSize(usedMemory)}, " +
                "Free: ${formatFileSize(freeMemory)}, " +
                "Max: ${formatFileSize(maxMemory)}")
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
}

/**
 * Extension functions for easy logging from any class
 */

/**
 * Get a simple class name for logging tag
 */
fun Any.getLogTag(): String = this::class.java.simpleName

/**
 * Quick access to verbose logging
 */
fun Any.logV(message: String, throwable: Throwable? = null) = 
    AppLogger.v(getLogTag(), message, throwable)

/**
 * Quick access to debug logging
 */
fun Any.logD(message: String, throwable: Throwable? = null) = 
    AppLogger.d(getLogTag(), message, throwable)

/**
 * Quick access to info logging
 */
fun Any.logI(message: String, throwable: Throwable? = null) = 
    AppLogger.i(getLogTag(), message, throwable)

/**
 * Quick access to warning logging
 */
fun Any.logW(message: String, throwable: Throwable? = null) = 
    AppLogger.w(getLogTag(), message, throwable)

/**
 * Quick access to error logging
 */
fun Any.logE(message: String, throwable: Throwable? = null) = 
    AppLogger.e(getLogTag(), message, throwable)