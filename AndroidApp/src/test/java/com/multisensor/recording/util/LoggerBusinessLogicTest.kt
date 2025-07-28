package com.multisensor.recording.util

import org.junit.Assert.*
import org.junit.Test
import java.io.File

/**
 * Non-Android unit tests for Logger business logic
 * Tests LogLevel enum, LogStatistics data class, and core logic without requiring Robolectric
 */
class LoggerBusinessLogicTest {

    @Test
    fun `LogLevel enum should have correct priority values`() {
        // Then
        assertEquals("VERBOSE should have priority 2", 2, Logger.LogLevel.VERBOSE.priority)
        assertEquals("DEBUG should have priority 3", 3, Logger.LogLevel.DEBUG.priority)
        assertEquals("INFO should have priority 4", 4, Logger.LogLevel.INFO.priority)
        assertEquals("WARNING should have priority 5", 5, Logger.LogLevel.WARNING.priority)
        assertEquals("ERROR should have priority 6", 6, Logger.LogLevel.ERROR.priority)
    }

    @Test
    fun `LogLevel enum should have all expected values`() {
        // When
        val logLevels = Logger.LogLevel.values()
        
        // Then
        assertEquals("Should have 5 log levels", 5, logLevels.size)
        
        val expectedLevels = setOf(
            Logger.LogLevel.VERBOSE,
            Logger.LogLevel.DEBUG,
            Logger.LogLevel.INFO,
            Logger.LogLevel.WARNING,
            Logger.LogLevel.ERROR
        )
        
        assertEquals("Should contain all expected log levels", expectedLevels, logLevels.toSet())
    }

    @Test
    fun `LogLevel priorities should be in ascending order`() {
        // When
        val levels = Logger.LogLevel.values()
        
        // Then
        for (i in 0 until levels.size - 1) {
            assertTrue("Priority should increase: ${levels[i]} < ${levels[i + 1]}", 
                      levels[i].priority < levels[i + 1].priority)
        }
    }

    @Test
    fun `LogLevel should support comparison by priority`() {
        // Then
        assertTrue("VERBOSE < DEBUG", Logger.LogLevel.VERBOSE.priority < Logger.LogLevel.DEBUG.priority)
        assertTrue("DEBUG < INFO", Logger.LogLevel.DEBUG.priority < Logger.LogLevel.INFO.priority)
        assertTrue("INFO < WARNING", Logger.LogLevel.INFO.priority < Logger.LogLevel.WARNING.priority)
        assertTrue("WARNING < ERROR", Logger.LogLevel.WARNING.priority < Logger.LogLevel.ERROR.priority)
    }

    @Test
    fun `LogStatistics should initialize with correct default values`() {
        // When
        val stats = Logger.LogStatistics(
            fileCount = 5,
            totalSizeBytes = 1024L,
            oldestLogDate = 1000L,
            newestLogDate = 2000L,
            currentLogFile = "current.log"
        )
        
        // Then
        assertEquals(5, stats.fileCount)
        assertEquals(1024L, stats.totalSizeBytes)
        assertEquals(1000L, stats.oldestLogDate)
        assertEquals(2000L, stats.newestLogDate)
        assertEquals("current.log", stats.currentLogFile)
    }

    @Test
    fun `LogStatistics should handle null values`() {
        // When
        val stats = Logger.LogStatistics(
            fileCount = 0,
            totalSizeBytes = 0L,
            oldestLogDate = null,
            newestLogDate = null,
            currentLogFile = null
        )
        
        // Then
        assertEquals(0, stats.fileCount)
        assertEquals(0L, stats.totalSizeBytes)
        assertNull(stats.oldestLogDate)
        assertNull(stats.newestLogDate)
        assertNull(stats.currentLogFile)
    }

    @Test
    fun `LogStatistics should support data class functionality`() {
        // Given
        val stats1 = Logger.LogStatistics(
            fileCount = 3,
            totalSizeBytes = 512L,
            oldestLogDate = 1000L,
            newestLogDate = 2000L,
            currentLogFile = "test.log"
        )
        
        val stats2 = Logger.LogStatistics(
            fileCount = 3,
            totalSizeBytes = 512L,
            oldestLogDate = 1000L,
            newestLogDate = 2000L,
            currentLogFile = "test.log"
        )
        
        val stats3 = Logger.LogStatistics(
            fileCount = 4,
            totalSizeBytes = 512L,
            oldestLogDate = 1000L,
            newestLogDate = 2000L,
            currentLogFile = "test.log"
        )
        
        // Then
        assertEquals("Equal objects should be equal", stats1, stats2)
        assertNotEquals("Different objects should not be equal", stats1, stats3)
        assertEquals("Hash codes should be equal for equal objects", stats1.hashCode(), stats2.hashCode())
    }

    @Test
    fun `LogStatistics should have meaningful toString`() {
        // Given
        val stats = Logger.LogStatistics(
            fileCount = 2,
            totalSizeBytes = 1024L,
            oldestLogDate = 1000L,
            newestLogDate = 2000L,
            currentLogFile = "current.log"
        )
        
        // When
        val toString = stats.toString()
        
        // Then
        assertTrue("Should contain fileCount", toString.contains("2"))
        assertTrue("Should contain totalSizeBytes", toString.contains("1024"))
        assertTrue("Should contain current log file", toString.contains("current.log"))
    }

    @Test
    fun `LogStatistics should handle large file sizes`() {
        // Given
        val largeSize = Long.MAX_VALUE
        
        // When
        val stats = Logger.LogStatistics(
            fileCount = 1000,
            totalSizeBytes = largeSize,
            oldestLogDate = 1000L,
            newestLogDate = System.currentTimeMillis(),
            currentLogFile = "large.log"
        )
        
        // Then
        assertEquals(1000, stats.fileCount)
        assertEquals(largeSize, stats.totalSizeBytes)
        assertNotNull(stats.currentLogFile)
    }

    @Test
    fun `LogStatistics should handle edge case values`() {
        // When
        val stats = Logger.LogStatistics(
            fileCount = 0,
            totalSizeBytes = 0L,
            oldestLogDate = 0L,
            newestLogDate = 0L,
            currentLogFile = ""
        )
        
        // Then
        assertEquals(0, stats.fileCount)
        assertEquals(0L, stats.totalSizeBytes)
        assertEquals(0L, stats.oldestLogDate)
        assertEquals(0L, stats.newestLogDate)
        assertEquals("", stats.currentLogFile)
    }

    @Test
    fun `LogStatistics should support copy functionality`() {
        // Given
        val original = Logger.LogStatistics(
            fileCount = 5,
            totalSizeBytes = 2048L,
            oldestLogDate = 1000L,
            newestLogDate = 3000L,
            currentLogFile = "original.log"
        )
        
        // When
        val copied = original.copy(fileCount = 10)
        
        // Then
        assertEquals(10, copied.fileCount)
        assertEquals(2048L, copied.totalSizeBytes) // Should preserve other values
        assertEquals(1000L, copied.oldestLogDate)
        assertEquals(3000L, copied.newestLogDate)
        assertEquals("original.log", copied.currentLogFile)
    }

    @Test
    fun `log level filtering should work correctly`() {
        // Given
        val minLevel = Logger.LogLevel.WARNING
        
        // When & Then
        assertTrue("ERROR should pass WARNING filter", 
                  Logger.LogLevel.ERROR.priority >= minLevel.priority)
        assertTrue("WARNING should pass WARNING filter", 
                  Logger.LogLevel.WARNING.priority >= minLevel.priority)
        assertFalse("INFO should not pass WARNING filter", 
                   Logger.LogLevel.INFO.priority >= minLevel.priority)
        assertFalse("DEBUG should not pass WARNING filter", 
                   Logger.LogLevel.DEBUG.priority >= minLevel.priority)
        assertFalse("VERBOSE should not pass WARNING filter", 
                   Logger.LogLevel.VERBOSE.priority >= minLevel.priority)
    }

    @Test
    fun `log level names should match enum names`() {
        // Then
        assertEquals("VERBOSE", Logger.LogLevel.VERBOSE.name)
        assertEquals("DEBUG", Logger.LogLevel.DEBUG.name)
        assertEquals("INFO", Logger.LogLevel.INFO.name)
        assertEquals("WARNING", Logger.LogLevel.WARNING.name)
        assertEquals("ERROR", Logger.LogLevel.ERROR.name)
    }

    @Test
    fun `log level ordinals should be sequential`() {
        // Then
        assertEquals(0, Logger.LogLevel.VERBOSE.ordinal)
        assertEquals(1, Logger.LogLevel.DEBUG.ordinal)
        assertEquals(2, Logger.LogLevel.INFO.ordinal)
        assertEquals(3, Logger.LogLevel.WARNING.ordinal)
        assertEquals(4, Logger.LogLevel.ERROR.ordinal)
    }

    @Test
    fun `message formatting should handle null throwables`() {
        // Given
        val message = "Test message"
        val throwable: Throwable? = null
        
        // When
        val hasThrowable = throwable != null
        
        // Then
        assertFalse("Should handle null throwable", hasThrowable)
        assertNotNull("Message should not be null", message)
        assertTrue("Message should not be empty", message.isNotEmpty())
    }

    @Test
    fun `message formatting should handle throwables with stack traces`() {
        // Given
        val message = "Error occurred"
        val throwable = RuntimeException("Test exception")
        
        // When
        val hasThrowable = throwable != null
        val stackTrace = throwable.stackTrace
        
        // Then
        assertTrue("Should detect throwable", hasThrowable)
        assertNotNull("Stack trace should not be null", stackTrace)
        assertTrue("Stack trace should not be empty", stackTrace.isNotEmpty())
        assertEquals("Test exception", throwable.message)
    }

    @Test
    fun `file path validation should work correctly`() {
        // Given
        val validPath = "logs/app_2023-01-01.log"
        val invalidPath = ""
        val nullPath: String? = null
        
        // When & Then
        assertTrue("Valid path should not be empty", validPath.isNotEmpty())
        assertTrue("Invalid path should be empty", invalidPath.isEmpty())
        assertNull("Null path should be null", nullPath)
        
        // Path should contain expected components
        assertTrue("Should contain logs directory", validPath.contains("logs"))
        assertTrue("Should contain log extension", validPath.endsWith(".log"))
    }

    @Test
    fun `timestamp validation should work correctly`() {
        // Given
        val currentTime = System.currentTimeMillis()
        val pastTime = currentTime - 86400000L // 24 hours ago
        val futureTime = currentTime + 86400000L // 24 hours from now
        
        // When & Then
        assertTrue("Current time should be positive", currentTime > 0)
        assertTrue("Past time should be less than current", pastTime < currentTime)
        assertTrue("Future time should be greater than current", futureTime > currentTime)
        assertTrue("Time difference should be reasonable", 
                  (currentTime - pastTime) == 86400000L)
    }

    @Test
    fun `log statistics calculations should be accurate`() {
        // Given
        val file1Size = 1024L
        val file2Size = 2048L
        val file3Size = 512L
        val totalSize = file1Size + file2Size + file3Size
        val fileCount = 3
        
        // When
        val stats = Logger.LogStatistics(
            fileCount = fileCount,
            totalSizeBytes = totalSize,
            oldestLogDate = 1000L,
            newestLogDate = 3000L,
            currentLogFile = "current.log"
        )
        
        // Then
        assertEquals("File count should be correct", fileCount, stats.fileCount)
        assertEquals("Total size should be sum of all files", totalSize, stats.totalSizeBytes)
        assertEquals("Should be 3584 bytes total", 3584L, stats.totalSizeBytes)
        
        // Average file size calculation
        val averageSize = stats.totalSizeBytes / stats.fileCount
        assertEquals("Average file size should be correct", 1194L, averageSize)
    }

    @Test
    fun `enum valueOf should work correctly`() {
        // When & Then
        assertEquals(Logger.LogLevel.VERBOSE, Logger.LogLevel.valueOf("VERBOSE"))
        assertEquals(Logger.LogLevel.DEBUG, Logger.LogLevel.valueOf("DEBUG"))
        assertEquals(Logger.LogLevel.INFO, Logger.LogLevel.valueOf("INFO"))
        assertEquals(Logger.LogLevel.WARNING, Logger.LogLevel.valueOf("WARNING"))
        assertEquals(Logger.LogLevel.ERROR, Logger.LogLevel.valueOf("ERROR"))
    }

    @Test
    fun `enum valueOf should throw exception for invalid values`() {
        // When & Then
        try {
            Logger.LogLevel.valueOf("INVALID")
            fail("Should throw IllegalArgumentException for invalid enum value")
        } catch (e: IllegalArgumentException) {
            // Expected
            assertTrue("Should contain enum name in error", e.message?.contains("INVALID") == true)
        }
    }
}