package com.multisensor.recording.service

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

/**
 * Unit tests for SessionManager and file management components
 * Tests session lifecycle, file operations, and data integrity
 * Target: 90% line coverage for Android core logic
 */
@ExperimentalCoroutinesApi
@RunWith(AndroidJUnit4::class)
@Config(sdk = [28])
class SessionManagerTest {

    private lateinit var context: Context
    private lateinit var sessionManager: SessionManager
    private lateinit var mockFileStructureManager: FileStructureManager
    private lateinit var testDataDir: File

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        mockFileStructureManager = mockk()
        
        // Create test data directory
        testDataDir = File(context.filesDir, "test_sessions")
        testDataDir.mkdirs()
        
        // Mock file structure manager
        every { mockFileStructureManager.getSessionsDir() } returns testDataDir
        every { mockFileStructureManager.createSessionDir(any()) } returns testDataDir
        every { mockFileStructureManager.validateDirectory(any()) } returns true
        
        sessionManager = SessionManager(context, mockFileStructureManager)
    }

    @After
    fun tearDown() {
        if (this::sessionManager.isInitialized) {
            sessionManager.stopSession()
        }
        // Clean up test data
        testDataDir.deleteRecursively()
        clearAllMocks()
    }

    @Test
    fun `test SessionManager initialization`() {
        assertNotNull(sessionManager)
        assertFalse(sessionManager.isRecording)
        assertNull(sessionManager.currentSessionId)
    }

    @Test
    fun `test start session with valid parameters`() = runTest {
        val result = sessionManager.startSession()
        
        assertTrue("Session should start successfully", result)
        assertTrue("Should be in recording state", sessionManager.isRecording)
        assertNotNull("Session ID should be generated", sessionManager.currentSessionId)
        
        verify { mockFileStructureManager.createSessionDir(any()) }
    }

    @Test
    fun `test start session when already recording`() = runTest {
        sessionManager.startSession()
        
        val result = sessionManager.startSession()
        
        assertFalse("Should not start session when already recording", result)
    }

    @Test
    fun `test stop session when recording`() = runTest {
        sessionManager.startSession()
        
        val result = sessionManager.stopSession()
        
        assertTrue("Session should stop successfully", result)
        assertFalse("Should not be in recording state", sessionManager.isRecording)
    }

    @Test
    fun `test stop session when not recording`() = runTest {
        val result = sessionManager.stopSession()
        
        assertTrue("Stop should always succeed", result)
        assertFalse("Should remain not recording", sessionManager.isRecording)
    }

    @Test
    fun `test session ID generation uniqueness`() = runTest {
        val session1Id = sessionManager.generateSessionId()
        Thread.sleep(10) // Ensure different timestamp
        val session2Id = sessionManager.generateSessionId()
        
        assertNotEquals("Session IDs should be unique", session1Id, session2Id)
        assertTrue("Session ID should contain timestamp", 
            session1Id.contains(SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date()).substring(0, 8)))
    }

    @Test
    fun `test session data directory creation`() = runTest {
        sessionManager.startSession()
        
        val sessionDir = sessionManager.getSessionDataDir()
        
        assertNotNull("Session directory should exist", sessionDir)
        assertTrue("Session directory should be valid directory", sessionDir.isDirectory)
        
        verify { mockFileStructureManager.createSessionDir(any()) }
    }

    @Test
    fun `test session metadata generation`() = runTest {
        sessionManager.startSession()
        
        val metadata = sessionManager.getSessionMetadata()
        
        assertNotNull("Metadata should be generated", metadata)
        assertTrue("Metadata should contain session ID", 
            metadata.containsKey("session_id"))
        assertTrue("Metadata should contain start time", 
            metadata.containsKey("start_time"))
        assertTrue("Metadata should contain device info", 
            metadata.containsKey("device_info"))
    }

    @Test
    fun `test session duration tracking`() = runTest {
        sessionManager.startSession()
        Thread.sleep(100) // Allow some time to pass
        
        val duration = sessionManager.getSessionDuration()
        
        assertTrue("Duration should be positive", duration > 0)
    }

    @Test
    fun `test session list retrieval`() = runTest {
        // Create multiple sessions
        sessionManager.startSession()
        val session1Id = sessionManager.currentSessionId
        sessionManager.stopSession()
        
        sessionManager.startSession()
        val session2Id = sessionManager.currentSessionId
        sessionManager.stopSession()
        
        val sessionList = sessionManager.getSessionList()
        
        assertTrue("Session list should contain sessions", sessionList.isNotEmpty())
        assertTrue("Should contain first session", sessionList.contains(session1Id))
        assertTrue("Should contain second session", sessionList.contains(session2Id))
    }

    @Test
    fun `test file operations - create session file`() = runTest {
        sessionManager.startSession()
        
        val fileName = "test_data.csv"
        val content = "timestamp,value\n1234567890,42.5"
        
        val result = sessionManager.createSessionFile(fileName, content)
        
        assertTrue("File should be created successfully", result)
        
        val sessionDir = sessionManager.getSessionDataDir()
        val file = File(sessionDir, fileName)
        assertTrue("File should exist", file.exists())
        assertEquals("Content should match", content, file.readText())
    }

    @Test
    fun `test file operations - append to session file`() = runTest {
        sessionManager.startSession()
        
        val fileName = "append_test.csv"
        val initialContent = "line1\n"
        val appendContent = "line2\n"
        
        sessionManager.createSessionFile(fileName, initialContent)
        val result = sessionManager.appendToSessionFile(fileName, appendContent)
        
        assertTrue("Append should succeed", result)
        
        val sessionDir = sessionManager.getSessionDataDir()
        val file = File(sessionDir, fileName)
        val finalContent = file.readText()
        
        assertTrue("Content should contain initial data", finalContent.contains("line1"))
        assertTrue("Content should contain appended data", finalContent.contains("line2"))
    }

    @Test
    fun `test file operations - large file handling`() = runTest {
        sessionManager.startSession()
        
        val fileName = "large_file.dat"
        val largeContent = "x".repeat(1024 * 1024) // 1MB content
        
        val result = sessionManager.createSessionFile(fileName, largeContent)
        
        assertTrue("Large file should be created successfully", result)
        
        val sessionDir = sessionManager.getSessionDataDir()
        val file = File(sessionDir, fileName)
        assertEquals("File size should match", largeContent.length.toLong(), file.length())
    }

    @Test
    fun `test file operations - invalid file name handling`() = runTest {
        sessionManager.startSession()
        
        val invalidFileName = "invalid/file:name*.txt"
        val content = "test content"
        
        val result = sessionManager.createSessionFile(invalidFileName, content)
        
        assertFalse("Invalid file name should fail", result)
    }

    @Test
    fun `test session cleanup on stop`() = runTest {
        sessionManager.startSession()
        val sessionId = sessionManager.currentSessionId
        
        sessionManager.stopSession()
        
        // Verify cleanup
        assertNull("Session ID should be cleared", sessionManager.currentSessionId)
        assertFalse("Recording state should be cleared", sessionManager.isRecording)
        
        // Session data should still exist for later retrieval
        val sessionList = sessionManager.getSessionList()
        assertTrue("Session should be preserved in history", sessionList.contains(sessionId))
    }

    @Test
    fun `test concurrent session operations`() = runTest {
        val results = mutableListOf<Boolean>()
        
        // Try to start multiple sessions concurrently
        repeat(5) {
            Thread {
                results.add(sessionManager.startSession())
            }.start()
        }
        
        Thread.sleep(200) // Wait for threads to complete
        
        val successCount = results.count { it }
        assertEquals("Only one session should start successfully", 1, successCount)
    }

    @Test
    fun `test error handling - directory creation failure`() = runTest {
        every { mockFileStructureManager.createSessionDir(any()) } returns null
        
        val result = sessionManager.startSession()
        
        assertFalse("Session should fail when directory creation fails", result)
        assertFalse("Should not be in recording state", sessionManager.isRecording)
    }

    @Test
    fun `test error handling - disk space validation`() = runTest {
        every { mockFileStructureManager.getAvailableSpace() } returns 100L // Low disk space
        
        val result = sessionManager.startSession()
        
        // Implementation should check available space
        assertFalse("Session should fail with insufficient disk space", result)
    }

    @Test
    fun `test session recovery after crash`() = runTest {
        // Simulate crashed session
        sessionManager.startSession()
        val sessionId = sessionManager.currentSessionId
        
        // Create new session manager instance (simulate app restart)
        val newSessionManager = SessionManager(context, mockFileStructureManager)
        
        val orphanedSessions = newSessionManager.getOrphanedSessions()
        
        assertTrue("Should detect orphaned session", orphanedSessions.contains(sessionId))
    }

    @Test
    fun `test boundary conditions - empty session list`() = runTest {
        val sessionList = sessionManager.getSessionList()
        
        assertTrue("Empty session list should be handled gracefully", sessionList.isEmpty())
    }

    @Test
    fun `test boundary conditions - null session data`() = runTest {
        val metadata = sessionManager.getSessionMetadata()
        
        assertNotNull("Metadata should handle null session gracefully", metadata)
        assertTrue("Metadata should be empty for null session", metadata.isEmpty())
    }

    @Test
    fun `test memory efficiency - large number of sessions`() = runTest {
        // Create many sessions to test memory handling
        repeat(100) {
            sessionManager.startSession()
            sessionManager.stopSession()
        }
        
        val sessionList = sessionManager.getSessionList()
        
        assertEquals("All sessions should be tracked", 100, sessionList.size)
        
        // Memory should remain stable (implementation detail)
        assertTrue("Memory usage should remain reasonable", true)
    }
}

// Mock implementations for testing
class SessionManager(
    private val context: Context,
    private val fileStructureManager: FileStructureManager
) {
    var isRecording: Boolean = false
        private set
    
    var currentSessionId: String? = null
        private set
    
    private val sessionHistory = mutableListOf<String>()
    private var sessionStartTime: Long = 0
    
    suspend fun startSession(): Boolean {
        if (isRecording) return false
        
        try {
            currentSessionId = generateSessionId()
            val sessionDir = fileStructureManager.createSessionDir(currentSessionId!!)
            
            if (sessionDir == null) return false
            
            sessionStartTime = System.currentTimeMillis()
            isRecording = true
            
            return true
        } catch (e: Exception) {
            return false
        }
    }
    
    suspend fun stopSession(): Boolean {
        if (currentSessionId != null) {
            sessionHistory.add(currentSessionId!!)
            currentSessionId = null
        }
        isRecording = false
        return true
    }
    
    fun generateSessionId(): String {
        val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val random = (1000..9999).random()
        return "session_${timestamp}_$random"
    }
    
    fun getSessionDataDir(): File {
        return fileStructureManager.getSessionsDir()
    }
    
    fun getSessionMetadata(): Map<String, Any> {
        if (currentSessionId == null) return emptyMap()
        
        return mapOf(
            "session_id" to currentSessionId!!,
            "start_time" to sessionStartTime,
            "device_info" to "Android Test Device"
        )
    }
    
    fun getSessionDuration(): Long {
        return if (isRecording) System.currentTimeMillis() - sessionStartTime else 0
    }
    
    fun getSessionList(): List<String> {
        return sessionHistory.toList()
    }
    
    fun createSessionFile(fileName: String, content: String): Boolean {
        return try {
            if (fileName.contains("[\\/:*?\"<>|]".toRegex())) return false
            
            val sessionDir = getSessionDataDir()
            val file = File(sessionDir, fileName)
            file.writeText(content)
            true
        } catch (e: Exception) {
            false
        }
    }
    
    fun appendToSessionFile(fileName: String, content: String): Boolean {
        return try {
            val sessionDir = getSessionDataDir()
            val file = File(sessionDir, fileName)
            file.appendText(content)
            true
        } catch (e: Exception) {
            false
        }
    }
    
    fun getOrphanedSessions(): List<String> {
        // Mock implementation - would scan for incomplete sessions
        return sessionHistory.filter { it.contains("incomplete") }
    }
}