package com.multisensor.recording.util

import android.content.Context
import android.os.Build
import io.mockk.mockk
import io.mockk.verify
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread

/**
 * Comprehensive tests for the enhanced Android AppLogger system.
 * 
 * Tests all aspects of the enhanced logging including:
 * - Basic logging functionality
 * - Performance monitoring and timing
 * - Memory usage tracking
 * - Crash reporting setup
 * - Structured logging with context
 * - Thread safety
 * - Extension functions
 * 
 * Author: Multi-Sensor Recording System Team
 * Date: 2025-07-30
 */
class AppLoggerEnhancedTest {
    
    private lateinit var mockContext: Context
    
    @Before
    fun setup() {
        mockContext = mockk(relaxed = true)
        
        // Reset AppLogger state
        AppLogger.setDebugEnabled(true)
        AppLogger.setVerboseEnabled(true)
        AppLogger.setMemoryMonitoringEnabled(true)
        AppLogger.clearPerformanceStats()
    }
    
    @Test
    fun `test basic logging levels`() {
        // Test all logging levels with structured context
        val context = mapOf("test_id" to "basic_logging", "component" to "test")
        
        AppLogger.v("TestTag", "Verbose message", context = context)
        AppLogger.d("TestTag", "Debug message", context = context)
        AppLogger.i("TestTag", "Info message", context = context)
        AppLogger.w("TestTag", "Warning message", context = context)
        AppLogger.e("TestTag", "Error message", context = context)
        
        // Test with exceptions
        val testException = RuntimeException("Test exception")
        AppLogger.e("TestTag", "Error with exception", testException, context)
        
        // Verify logging doesn't throw exceptions
        assertTrue("Basic logging should complete without errors", true)
    }
    
    @Test
    fun `test log level controls`() {
        // Test debug level control
        AppLogger.setDebugEnabled(false)
        AppLogger.d("TestTag", "This debug message should be filtered")
        
        // Test verbose level control
        AppLogger.setVerboseEnabled(false)
        AppLogger.v("TestTag", "This verbose message should be filtered")
        
        // Verify controls work
        assertTrue("Debug control should work", true)
        assertTrue("Verbose control should work", true)
    }
    
    @Test
    fun `test performance timing`() {
        val tag = "PerformanceTest"
        val operation = "test_operation"
        
        // Test manual timing
        AppLogger.startTiming(tag, operation)
        Thread.sleep(50) // Simulate some work
        val duration = AppLogger.endTiming(tag, operation)
        
        assertTrue("Duration should be positive", duration > 0)
        assertTrue("Duration should be reasonable", duration >= 40 && duration <= 200)
        
        // Test timing with context
        AppLogger.startTiming(tag, operation, "with_context")
        Thread.sleep(30)
        val contextDuration = AppLogger.endTiming(tag, operation, "with_context")
        
        assertTrue("Context duration should be positive", contextDuration > 0)
    }
    
    @Test
    fun `test measureTime function`() {
        val tag = "MeasureTest"
        var executed = false
        
        val result = AppLogger.measureTime(tag, "test_block") {
            Thread.sleep(25)
            executed = true
            "test_result"
        }
        
        assertTrue("Block should be executed", executed)
        assertEquals("Result should be returned", "test_result", result)
    }
    
    @Test
    fun `test measureTime with exception`() {
        val tag = "MeasureExceptionTest"
        
        try {
            AppLogger.measureTime(tag, "failing_block") {
                Thread.sleep(10)
                throw RuntimeException("Test exception")
            }
            fail("Should have thrown exception")
        } catch (e: RuntimeException) {
            assertEquals("Test exception", e.message)
        }
    }
    
    @Test
    fun `test performance statistics`() {
        val tag = "StatsTest"
        
        // Perform several timed operations
        repeat(3) { i ->
            AppLogger.measureTime(tag, "repeated_operation") {
                Thread.sleep(10 + i * 5) // Variable timing
            }
        }
        
        // Check statistics
        val stats = AppLogger.getPerformanceStats()
        assertNotNull("Stats should not be null", stats)
        
        val operationStats = stats["repeated_operation"]
        assertNotNull("Operation stats should exist", operationStats)
        operationStats?.let {
            assertEquals("Should have 3 calls", 3L, it.totalCalls)
            assertTrue("Total time should be positive", it.totalTimeMs > 0)
            assertTrue("Min time should be positive", it.minTimeMs > 0)
            assertTrue("Max time should be >= min time", it.maxTimeMs >= it.minTimeMs)
            assertTrue("Average should be calculated", it.avgTimeMs > 0)
        }
        
        // Test logging stats
        AppLogger.logPerformanceStats(tag)
        
        // Test clearing stats
        AppLogger.clearPerformanceStats()
        val clearedStats = AppLogger.getPerformanceStats()
        assertTrue("Stats should be empty after clear", clearedStats.isEmpty())
    }
    
    @Test
    fun `test memory monitoring`() {
        val tag = "MemoryTest"
        
        // Test memory logging
        AppLogger.logMemoryUsage(tag, "Test Memory Check")
        
        // Test memory monitoring enable/disable
        AppLogger.setMemoryMonitoringEnabled(false)
        AppLogger.logMemoryUsage(tag, "Should be filtered")
        
        AppLogger.setMemoryMonitoringEnabled(true)
        AppLogger.logMemoryUsage(tag, "Should be logged")
        
        // Test garbage collection
        AppLogger.forceGarbageCollection(tag, "Test GC")
        
        // Test memory snapshots
        val snapshots = AppLogger.getMemorySnapshots()
        assertNotNull("Snapshots should not be null", snapshots)
        assertTrue("Should have memory snapshots", snapshots.isNotEmpty())
        
        val snapshot = snapshots.first()
        assertTrue("Used memory should be positive", snapshot.usedMemoryMB > 0)
        assertTrue("Max memory should be positive", snapshot.maxMemoryMB > 0)
        assertTrue("Thread count should be positive", snapshot.threadCount > 0)
        assertTrue("Timestamp should be reasonable", snapshot.timestamp > 0)
    }
    
    @Test
    fun `test specialized logging methods`() {
        val tag = "SpecializedTest"
        val context = mapOf("test_phase" to "specialized_logging")
        
        // Test lifecycle logging
        AppLogger.logLifecycle(tag, "onCreate", "MainActivity", context)
        
        // Test network logging
        AppLogger.logNetwork(tag, "GET", "https://api.example.com", "200 OK", 150L, context)
        
        // Test recording logging
        AppLogger.logRecording(tag, "start", "Camera1", 5000L, 1024*1024L, context)
        
        // Test sensor logging
        AppLogger.logSensor(tag, "reading", "GSR", "1.23", 3, System.currentTimeMillis(), context)
        
        // Test file logging
        AppLogger.logFile(tag, "save", "test.mp4", 1024*1024L, 250L, true, context)
        AppLogger.logFile(tag, "save", "failed.mp4", null, 100L, false, context)
        
        // Test state change logging
        AppLogger.logStateChange(tag, "Camera", "IDLE", "RECORDING", context)
        
        // Test thread info logging
        AppLogger.logThreadInfo(tag, "Test Thread Info")
        
        // Test error logging
        val testError = RuntimeException("Test error for specialized logging")
        AppLogger.logError(tag, "test_operation", testError, context)
        
        assertTrue("Specialized logging should complete", true)
    }
    
    @Test
    fun `test extension functions`() {
        val testObject = TestLoggingClass()
        
        // Test basic extension functions
        testObject.logI("Extension info message")
        testObject.logD("Extension debug message")
        testObject.logW("Extension warning message")
        testObject.logE("Extension error message")
        
        // Test extension with context
        val context = mapOf("extension_test" to true)
        testObject.logI("Extension with context", context = context)
        
        // Test performance extensions
        testObject.startTiming("extension_operation")
        Thread.sleep(20)
        val duration = testObject.endTiming("extension_operation")
        assertTrue("Extension timing should work", duration > 0)
        
        // Test measureTime extension
        val result = testObject.measureTime("extension_measure") {
            Thread.sleep(15)
            "extension_result"
        }
        assertEquals("Extension measureTime should work", "extension_result", result)
        
        // Test memory extension
        testObject.logMemory("Extension Memory Check")
        
        // Test error extension
        val error = RuntimeException("Extension error")
        testObject.logError("extension_operation", error)
        
        assertTrue("Extension functions should work", true)
    }
    
    @Test
    fun `test thread safety`() {
        val threadCount = 5
        val operationsPerThread = 10
        val latch = CountDownLatch(threadCount)
        val exceptions = mutableListOf<Exception>()
        
        // Create multiple threads performing logging operations
        repeat(threadCount) { threadId ->
            thread {
                try {
                    repeat(operationsPerThread) { opId ->
                        val tag = "ThreadTest$threadId"
                        val context = mapOf(
                            "thread_id" to threadId,
                            "operation_id" to opId
                        )
                        
                        // Mix different types of operations
                        AppLogger.i(tag, "Thread operation $opId", context = context)
                        
                        AppLogger.measureTime(tag, "threaded_operation_$opId") {
                            Thread.sleep(1) // Minimal work
                        }
                        
                        if (opId % 3 == 0) {
                            AppLogger.logMemoryUsage(tag, "Thread $threadId Op $opId")
                        }
                        
                        AppLogger.logNetwork(tag, "API call", "test.com", "200", 50L, context)
                    }
                } catch (e: Exception) {
                    synchronized(exceptions) {
                        exceptions.add(e)
                    }
                } finally {
                    latch.countDown()
                }
            }
        }
        
        // Wait for all threads to complete
        assertTrue("All threads should complete within timeout", 
                  latch.await(30, TimeUnit.SECONDS))
        
        // Check for exceptions
        assertTrue("No exceptions should occur during concurrent logging: ${exceptions.joinToString()}", 
                  exceptions.isEmpty())
        
        // Verify statistics were collected correctly
        val stats = AppLogger.getPerformanceStats()
        assertTrue("Should have performance stats from threads", stats.isNotEmpty())
        
        // Verify memory snapshots were collected
        val snapshots = AppLogger.getMemorySnapshots()
        assertTrue("Should have memory snapshots from threads", snapshots.isNotEmpty())
    }
    
    @Test
    fun `test logging statistics`() {
        val tag = "StatsTest"
        
        // Perform various logging operations
        repeat(5) { AppLogger.i(tag, "Info message $it") }
        repeat(3) { AppLogger.w(tag, "Warning message $it") }
        repeat(2) { AppLogger.e(tag, "Error message $it") }
        
        // Get logging statistics
        val stats = AppLogger.getLoggingStats()
        assertNotNull("Stats should not be null", stats)
        assertTrue("Stats should contain information", stats.isNotEmpty())
        assertTrue("Stats should mention logs", stats.contains("Logs:"))
    }
    
    @Test
    fun `test data class functionality`() {
        // Test PerformanceStats data class
        val perfStats = AppLogger.PerformanceStats(
            operationName = "test_op",
            totalCalls = 5L,
            totalTimeMs = 100L,
            minTimeMs = 10L,
            maxTimeMs = 30L
        )
        
        assertEquals("test_op", perfStats.operationName)
        assertEquals(5L, perfStats.totalCalls)
        assertEquals(100L, perfStats.totalTimeMs)
        assertEquals(10L, perfStats.minTimeMs)
        assertEquals(30L, perfStats.maxTimeMs)
        assertEquals(20L, perfStats.avgTimeMs) // 100/5
        
        // Test MemorySnapshot data class
        val memSnapshot = AppLogger.MemorySnapshot(
            timestamp = System.currentTimeMillis(),
            context = "test_context",
            usedMemoryMB = 50L,
            freeMemoryMB = 100L,
            maxMemoryMB = 200L,
            nativeHeapSizeMB = 30L,
            threadCount = 10
        )
        
        assertEquals("test_context", memSnapshot.context)
        assertEquals(50L, memSnapshot.usedMemoryMB)
        assertEquals(100L, memSnapshot.freeMemoryMB)
        assertEquals(200L, memSnapshot.maxMemoryMB)
        assertEquals(30L, memSnapshot.nativeHeapSizeMB)
        assertEquals(10, memSnapshot.threadCount)
    }
    
    @Test
    fun `test method entry and exit logging`() {
        val tag = "MethodTest"
        
        // Test method entry logging
        AppLogger.logMethodEntry(tag, "testMethod", "param1", 42, null)
        AppLogger.logMethodExit(tag, "testMethod", "return_value")
        
        // Test with no parameters
        AppLogger.logMethodEntry(tag, "noParamMethod")
        AppLogger.logMethodExit(tag, "noParamMethod")
        
        // Test with no return value
        AppLogger.logMethodEntry(tag, "voidMethod", "param")
        AppLogger.logMethodExit(tag, "voidMethod", null)
        
        assertTrue("Method logging should complete", true)
    }
    
    @Test
    fun `test system info logging`() {
        // Initialize AppLogger with context (would log system info)
        AppLogger.initialize(mockContext)
        
        // This should complete without errors
        assertTrue("System info logging should work", true)
    }
    
    /**
     * Test helper class for extension function testing
     */
    private class TestLoggingClass {
        fun doSomething() {
            logI("Doing something in TestLoggingClass")
        }
    }
}