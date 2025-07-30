package com.multisensor.recording.network

import android.util.Base64
import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.io.File
import java.io.FileInputStream

/**
 * Unit tests for FileTransferHandler - Milestone 3.6
 *
 * Tests the file transfer functionality including:
 * - File validation and error handling
 * - Chunked file reading and Base64 encoding
 * - Message sending and progress tracking
 * - Expected file path generation
 */
@ExperimentalCoroutinesApi
class FileTransferHandlerTest {
    private lateinit var fileTransferHandler: FileTransferHandler
    private lateinit var mockLogger: Logger
    private lateinit var mockJsonSocketClient: JsonSocketClient
    private lateinit var testFile: File

    @Before
    fun setUp() {
        // Mock dependencies
        mockLogger = mockk(relaxed = true)
        mockJsonSocketClient = mockk(relaxed = true)

        // Create FileTransferHandler instance
        fileTransferHandler = FileTransferHandler(mockLogger)
        fileTransferHandler.initialize(mockJsonSocketClient)

        // Create test file
        testFile = File.createTempFile("test_file", ".txt")
        testFile.writeText("This is a test file for file transfer validation. ".repeat(100))

        // Mock Base64 encoding (since Android Base64 is not available in unit tests)
        mockkStatic(Base64::class)
        every { Base64.encodeToString(any(), Base64.NO_WRAP) } answers {
            java.util.Base64
                .getEncoder()
                .encodeToString(firstArg<ByteArray>())
        }
    }

    @After
    fun tearDown() {
        // Clean up test file
        if (testFile.exists()) {
            testFile.delete()
        }

        // Clear mocks
        clearAllMocks()
        unmockkAll()
    }

    @Test
    fun `test handleSendFileCommand with valid file`() =
        runTest {
            // Arrange
            val command =
                SendFileCommand(
                    filepath = testFile.absolutePath,
                    filetype = "text",
                )

            // Act
            fileTransferHandler.handleSendFileCommand(command)

            // Allow coroutine to complete
            kotlinx.coroutines.delay(100)

            // Assert
            verify { mockLogger.info("Received file transfer request for: ${testFile.absolutePath}") }
            verify { mockJsonSocketClient.sendMessage(any<FileInfoMessage>()) }
            verify(atLeast = 1) { mockJsonSocketClient.sendMessage(any<FileChunkMessage>()) }
            verify { mockJsonSocketClient.sendMessage(any<FileEndMessage>()) }
        }

    @Test
    fun `test handleSendFileCommand with non-existent file`() =
        runTest {
            // Arrange
            val nonExistentPath = "/path/to/non/existent/file.txt"
            val command =
                SendFileCommand(
                    filepath = nonExistentPath,
                    filetype = "text",
                )

            // Act
            fileTransferHandler.handleSendFileCommand(command)

            // Allow coroutine to complete
            kotlinx.coroutines.delay(100)

            // Assert
            verify { mockLogger.error("File not found: $nonExistentPath") }
            verify { mockJsonSocketClient.sendMessage(any<AckMessage>()) }
            verify(exactly = 0) { mockJsonSocketClient.sendMessage(any<FileInfoMessage>()) }
        }

    @Test
    fun `test file chunking with small file`() =
        runTest {
            // Arrange
            val smallFile = File.createTempFile("small_test", ".txt")
            smallFile.writeText("Small test content")

            val command =
                SendFileCommand(
                    filepath = smallFile.absolutePath,
                    filetype = "text",
                )

            try {
                // Act
                fileTransferHandler.handleSendFileCommand(command)

                // Allow coroutine to complete
                kotlinx.coroutines.delay(100)

                // Assert
                verify { mockJsonSocketClient.sendMessage(any<FileInfoMessage>()) }
                verify(exactly = 1) { mockJsonSocketClient.sendMessage(any<FileChunkMessage>()) }
                verify { mockJsonSocketClient.sendMessage(any<FileEndMessage>()) }
            } finally {
                smallFile.delete()
            }
        }

    @Test
    fun `test file chunking with large file`() =
        runTest {
            // Arrange - Create a file larger than chunk size (64KB)
            val largeFile = File.createTempFile("large_test", ".txt")
            val chunkSize = 65536 // 64KB
            val content = "A".repeat(chunkSize * 2 + 1000) // Create file > 2 chunks
            largeFile.writeText(content)

            val command =
                SendFileCommand(
                    filepath = largeFile.absolutePath,
                    filetype = "text",
                )

            try {
                // Act
                fileTransferHandler.handleSendFileCommand(command)

                // Allow coroutine to complete
                kotlinx.coroutines.delay(200)

                // Assert
                verify { mockJsonSocketClient.sendMessage(any<FileInfoMessage>()) }
                verify(atLeast = 3) { mockJsonSocketClient.sendMessage(any<FileChunkMessage>()) }
                verify { mockJsonSocketClient.sendMessage(any<FileEndMessage>()) }
            } finally {
                largeFile.delete()
            }
        }

    @Test
    fun `test getExpectedFilePaths with all capabilities`() {
        // Arrange
        val sessionId = "test_session_123"
        val deviceId = "test_device_456"
        val capabilities = listOf("rgb_video", "thermal", "shimmer")

        // Act
        val expectedFiles = fileTransferHandler.getExpectedFilePaths(sessionId, deviceId, capabilities)

        // Assert
        assertEquals(3, expectedFiles.size)
        assertTrue(expectedFiles.any { it.contains("rgb.mp4") })
        assertTrue(expectedFiles.any { it.contains("thermal.mp4") })
        assertTrue(expectedFiles.any { it.contains("sensors.csv") })

        // Verify all files contain session and device IDs
        expectedFiles.forEach { filepath ->
            assertTrue("File path should contain session ID", filepath.contains(sessionId))
            assertTrue("File path should contain device ID", filepath.contains(deviceId))
        }
    }

    @Test
    fun `test getExpectedFilePaths with partial capabilities`() {
        // Arrange
        val sessionId = "test_session_789"
        val deviceId = "test_device_012"
        val capabilities = listOf("rgb_video") // Only RGB video capability

        // Act
        val expectedFiles = fileTransferHandler.getExpectedFilePaths(sessionId, deviceId, capabilities)

        // Assert
        assertEquals(1, expectedFiles.size)
        assertTrue(expectedFiles[0].contains("rgb.mp4"))
        assertFalse(expectedFiles.any { it.contains("thermal.mp4") })
        assertFalse(expectedFiles.any { it.contains("sensors.csv") })
    }

    @Test
    fun `test getExpectedFilePaths with no capabilities`() {
        // Arrange
        val sessionId = "test_session_empty"
        val deviceId = "test_device_empty"
        val capabilities = emptyList<String>()

        // Act
        val expectedFiles = fileTransferHandler.getExpectedFilePaths(sessionId, deviceId, capabilities)

        // Assert
        assertEquals(0, expectedFiles.size)
    }

    @Test
    fun `test getAvailableFiles with existing directory`() {
        // Arrange
        val sessionId = "test_session_available"

        // Mock file system behavior
        mockkStatic(File::class)
        val mockSessionDir = mockk<File>()
        val mockFile1 = mockk<File>()
        val mockFile2 = mockk<File>()

        every { File(any<String>()) } returns mockSessionDir
        every { mockSessionDir.exists() } returns true
        every { mockSessionDir.isDirectory } returns true
        every { mockSessionDir.listFiles() } returns arrayOf(mockFile1, mockFile2)
        every { mockFile1.isFile } returns true
        every { mockFile1.absolutePath } returns "/path/to/file1.mp4"
        every { mockFile2.isFile } returns true
        every { mockFile2.absolutePath } returns "/path/to/file2.csv"

        // Act
        val availableFiles = fileTransferHandler.getAvailableFiles(sessionId)

        // Assert
        assertEquals(2, availableFiles.size)
        assertTrue(availableFiles.contains("/path/to/file1.mp4"))
        assertTrue(availableFiles.contains("/path/to/file2.csv"))
    }

    @Test
    fun `test file size validation - file too large`() =
        runTest {
            // Arrange
            val mockFile = mockk<File>()
            every { mockFile.exists() } returns true
            every { mockFile.canRead() } returns true
            every { mockFile.length() } returns 3L * 1024 * 1024 * 1024 // 3GB - exceeds 2GB limit
            every { mockFile.absolutePath } returns "/path/to/large/file.mp4"

            mockkConstructor(File::class)
            every { anyConstructed<File>().exists() } returns true
            every { anyConstructed<File>().canRead() } returns true
            every { anyConstructed<File>().length() } returns 3L * 1024 * 1024 * 1024

            val command =
                SendFileCommand(
                    filepath = "/path/to/large/file.mp4",
                    filetype = "video",
                )

            // Act
            fileTransferHandler.handleSendFileCommand(command)

            // Allow coroutine to complete
            kotlinx.coroutines.delay(100)

            // Assert
            verify { mockLogger.error(match { it.contains("File too large") }) }
            verify { mockJsonSocketClient.sendMessage(any<AckMessage>()) }
            verify(exactly = 0) { mockJsonSocketClient.sendMessage(any<FileInfoMessage>()) }
        }

    @Test
    fun `test Base64 encoding in file chunks`() =
        runTest {
            // Arrange
            val testContent = "Test content for Base64 encoding validation"
            val testFile = File.createTempFile("base64_test", ".txt")
            testFile.writeText(testContent)

            val command =
                SendFileCommand(
                    filepath = testFile.absolutePath,
                    filetype = "text",
                )

            try {
                // Act
                fileTransferHandler.handleSendFileCommand(command)

                // Allow coroutine to complete
                kotlinx.coroutines.delay(100)

                // Assert - Verify Base64.encodeToString was called
                verify { Base64.encodeToString(any(), Base64.NO_WRAP) }

                // Verify chunk message was sent with encoded data
                verify {
                    mockJsonSocketClient.sendMessage(
                        match<FileChunkMessage> {
                            it.data.isNotEmpty() && it.seq == 1
                        },
                    )
                }
            } finally {
                testFile.delete()
            }
        }
}
