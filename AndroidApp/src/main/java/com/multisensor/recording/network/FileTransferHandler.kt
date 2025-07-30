package com.multisensor.recording.network

import android.util.Base64
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileInputStream
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

/**
 * File Transfer Handler for Milestone 3.6 - File Transfer and Data Aggregation
 *
 * Handles file transfer requests from PC server by reading files in chunks
 * and sending them via Base64-encoded JSON messages over the existing socket connection.
 *
 * Based on 3_6_milestone.md specifications:
 * - Reads files in 64KB chunks
 * - Base64 encodes chunks for JSON transmission
 * - Sends file_info, file_chunk sequence, and file_end messages
 * - Handles file access errors gracefully
 */
@Singleton
class FileTransferHandler
    @Inject
    constructor(
        private val logger: Logger,
    ) {
        companion object {
            private const val CHUNK_SIZE = 65536 // 64KB chunks as specified in milestone
            private const val MAX_FILE_SIZE = 2L * 1024 * 1024 * 1024 // 2GB max file size
        }

        private var jsonSocketClient: JsonSocketClient? = null

        /**
         * Initialize with JsonSocketClient for sending messages
         */
        fun initialize(client: JsonSocketClient) {
            jsonSocketClient = client
            logger.info("FileTransferHandler initialized")
        }

        /**
         * Handle send_file command from PC server
         *
         * @param command The SendFileCommand containing filepath and optional filetype
         */
        fun handleSendFileCommand(command: SendFileCommand) {
            logger.info("Received file transfer request for: ${command.filepath}")

            CoroutineScope(Dispatchers.IO).launch {
                try {
                    sendFile(command.filepath, command.filetype)
                } catch (e: Exception) {
                    logger.error("Error handling file transfer request", e)
                    sendErrorResponse("Failed to transfer file: ${e.message}")
                }
            }
        }

        /**
         * Send file to PC server in chunks
         *
         * @param filepath Path to the file to send
         * @param filetype Optional file type descriptor
         */
        private suspend fun sendFile(
            filepath: String,
            filetype: String?,
        ) {
            val file = File(filepath)

            // Validate file exists and is readable
            if (!file.exists()) {
                logger.error("File not found: $filepath")
                sendErrorResponse("File not found: $filepath")
                return
            }

            if (!file.canRead()) {
                logger.error("Cannot read file: $filepath")
                sendErrorResponse("Cannot read file: $filepath")
                return
            }

            if (file.length() > MAX_FILE_SIZE) {
                logger.error("File too large: ${file.length()} bytes")
                sendErrorResponse("File too large: ${file.length()} bytes")
                return
            }

            logger.info("Starting file transfer: ${file.name} (${file.length()} bytes)")

            try {
                // Send file info message
                val fileInfoMessage =
                    FileInfoMessage(
                        name = file.name,
                        size = file.length(),
                    )
                jsonSocketClient?.sendMessage(fileInfoMessage)
                logger.debug("Sent file info for ${file.name}")

                // Send file in chunks
                FileInputStream(file).use { inputStream ->
                    val buffer = ByteArray(CHUNK_SIZE)
                    var sequenceNumber = 1
                    var totalBytesSent = 0L

                    while (true) {
                        val bytesRead = inputStream.read(buffer)
                        if (bytesRead == -1) break // End of file

                        // Create chunk with actual bytes read (may be less than CHUNK_SIZE for last chunk)
                        val chunkData =
                            if (bytesRead == CHUNK_SIZE) {
                                buffer
                            } else {
                                buffer.copyOf(bytesRead)
                            }

                        // Base64 encode the chunk
                        val base64Data = Base64.encodeToString(chunkData, Base64.NO_WRAP)

                        // Send chunk message
                        val chunkMessage =
                            FileChunkMessage(
                                seq = sequenceNumber,
                                data = base64Data,
                            )
                        jsonSocketClient?.sendMessage(chunkMessage)

                        totalBytesSent += bytesRead
                        sequenceNumber++

                        // Log progress periodically
                        if (sequenceNumber % 100 == 0) {
                            val progress = (totalBytesSent * 100.0 / file.length()).toInt()
                            logger.debug("File transfer progress: $progress% ($totalBytesSent/${file.length()} bytes)")
                        }
                    }

                    // Send file end message
                    val fileEndMessage = FileEndMessage(name = file.name)
                    jsonSocketClient?.sendMessage(fileEndMessage)

                    logger.info("File transfer completed: ${file.name} ($totalBytesSent bytes, ${sequenceNumber - 1} chunks)")
                }
            } catch (e: IOException) {
                logger.error("IO error during file transfer", e)
                sendErrorResponse("IO error during file transfer: ${e.message}")
            } catch (e: Exception) {
                logger.error("Unexpected error during file transfer", e)
                sendErrorResponse("Unexpected error during file transfer: ${e.message}")
            }
        }

        /**
         * Send error response to PC server
         *
         * @param errorMessage Error message to send
         */
        private fun sendErrorResponse(errorMessage: String) {
            val errorAck =
                AckMessage(
                    cmd = "send_file",
                    status = "error",
                    message = errorMessage,
                )
            jsonSocketClient?.sendMessage(errorAck)
            logger.debug("Sent error response: $errorMessage")
        }

        /**
         * Get list of available files for transfer
         * This method can be used to determine what files are available for transfer
         *
         * @param sessionId Session ID to look for files
         * @return List of file paths available for transfer
         */
        fun getAvailableFiles(sessionId: String): List<String> {
            val availableFiles = mutableListOf<String>()

            try {
                // TODO: Implement based on actual file storage structure
                // This is a placeholder implementation
                val sessionDir = File("/storage/emulated/0/MultiSensorRecording/sessions/$sessionId")

                if (sessionDir.exists() && sessionDir.isDirectory) {
                    sessionDir.listFiles()?.forEach { file ->
                        if (file.isFile) {
                            availableFiles.add(file.absolutePath)
                            logger.debug("Available file: ${file.absolutePath}")
                        }
                    }
                }
            } catch (e: Exception) {
                logger.error("Error getting available files", e)
            }

            return availableFiles
        }

        /**
         * Construct expected file paths based on session ID and device capabilities
         *
         * @param sessionId Session ID
         * @param deviceId Device ID
         * @param capabilities Device capabilities
         * @return List of expected file paths
         */
        fun getExpectedFilePaths(
            sessionId: String,
            deviceId: String,
            capabilities: List<String>,
        ): List<String> {
            val expectedFiles = mutableListOf<String>()
            val baseDir = "/storage/emulated/0/MultiSensorRecording/sessions/$sessionId"

            // Add expected files based on device capabilities
            if (capabilities.contains("rgb_video")) {
                expectedFiles.add("$baseDir/${sessionId}_${deviceId}_rgb.mp4")
            }

            if (capabilities.contains("thermal")) {
                expectedFiles.add("$baseDir/${sessionId}_${deviceId}_thermal.mp4")
            }

            if (capabilities.contains("shimmer")) {
                expectedFiles.add("$baseDir/${sessionId}_${deviceId}_sensors.csv")
            }

            logger.debug("Expected files for $deviceId: $expectedFiles")
            return expectedFiles
        }
    }
