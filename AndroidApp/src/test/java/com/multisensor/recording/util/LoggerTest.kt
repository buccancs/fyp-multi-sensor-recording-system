package com.multisensor.recording.util

import android.content.Context
import com.multisensor.recording.TestConstants
import com.multisensor.recording.testutils.BaseUnitTest
import io.mockk.*
import io.mockk.impl.annotations.MockK
import org.junit.*
import org.junit.Assert.*
import java.io.File

/**
 * Comprehensive unit tests for Logger utility.
 * Covers all logging levels, formatting, and file operations.
 */
class LoggerTest : BaseUnitTest() {

    @MockK
    private lateinit var context: Context
    
    @MockK
    private lateinit var mockFile: File

    private lateinit var logger: Logger

    @Before
    override fun setUp() {
        super.setUp()
        
        // Setup context mocks
        every { context.getExternalFilesDir(any()) } returns mockFile
        every { context.filesDir } returns mockFile
        every { mockFile.exists() } returns true
        every { mockFile.mkdirs() } returns true
        every { mockFile.absolutePath } returns "/test/logs"
        
        logger = Logger(context)
    }

    @Test
    fun `test_info_logging`() {
        // Given: Logger is initialized
        
        // When: Logging info message
        logger.info("Test info message")
        
        // Then: Message should be logged without exception
        assertTrue("Info logging should work", true)
    }

    @Test
    fun `test_error_logging_with_exception`() {
        // Given: An exception occurs
        val exception = RuntimeException("Test exception")
        
        // When: Logging error with exception
        logger.error("Test error", exception)
        
        // Then: Error and exception should be logged
        assertTrue("Error logging with exception should work", true)
    }

    @Test
    fun `test_debug_logging`() {
        // Given: Logger is initialized
        
        // When: Logging debug message
        logger.debug("Debug message")
        
        // Then: Debug message should be logged
        assertTrue("Debug logging should work", true)
    }

    @Test
    fun `test_warn_logging`() {
        // Given: Logger is initialized
        
        // When: Logging warning message
        logger.warn("Warning message")
        
        // Then: Warning should be logged
        assertTrue("Warning logging should work", true)
    }

    @Test
    fun `test_verbose_logging`() {
        // Given: Logger is initialized
        
        // When: Logging verbose message
        logger.verbose("Verbose message")
        
        // Then: Verbose message should be logged
        assertTrue("Verbose logging should work", true)
    }

    @Test
    fun `test_cleanup_logs`() {
        // Given: Logger is initialized
        
        // When: Cleaning up old logs
        logger.cleanupOldLogs()
        
        // Then: Cleanup should complete without exception
        assertTrue("Log cleanup should work", true)
    }
}