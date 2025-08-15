package com.multisensor.recording.network

import android.content.Context
import android.util.Log
import com.multisensor.recording.session.SessionInfo
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.*
import java.net.*
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * FR10: Data Transfer and Aggregation - Automatic file transfer to PC
 * Handles uploading recorded session files to PC server after recording
 */
class DataTransferManager(private val context: Context) {
    
    companion object {
        private const val TAG = "DataTransferManager"
        private const val DEFAULT_TRANSFER_PORT = 8081
        private const val CHUNK_SIZE = 1024 * 1024 // 1MB chunks
        private const val CONNECTION_TIMEOUT_MS = 30000
        private const val TRANSFER_TIMEOUT_MS = 300000 // 5 minutes per file
        private const val MAX_RETRY_ATTEMPTS = 3
        private const val RETRY_DELAY_MS = 2000L
    }

    // Transfer state
    private val isTransferActive = AtomicBoolean(false)
    private val totalBytesTransferred = AtomicLong(0L)
    private val currentTransferProgress = AtomicLong(0L)
    
    // Coroutine scope for transfer operations
    private val transferScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    
    // Callbacks
    private var transferProgressCallback: ((String, Long, Long, Double) -> Unit)? = null
    private var transferCompleteCallback: ((Boolean, String?, List<TransferResult>) -> Unit)? = null
    private var fileTransferCallback: ((String, Boolean, String?) -> Unit)? = null

    /**
     * Upload session data to PC server
     */
    fun uploadSessionData(sessionInfo: SessionInfo, pcAddress: String, port: Int = DEFAULT_TRANSFER_PORT): Boolean {
        if (isTransferActive.get()) {
            Logger.w(TAG, "Transfer already in progress")
            return false
        }

        Logger.i(TAG, "Starting session data upload to $pcAddress:$port")
        
        transferScope.launch {
            performSessionUpload(sessionInfo, pcAddress, port)
        }
        
        return true
    }

    /**
     * Upload individual file to PC
     */
    fun uploadFile(filePath: String, fileName: String, pcAddress: String, port: Int = DEFAULT_TRANSFER_PORT): Boolean {
        if (isTransferActive.get()) {
            Logger.w(TAG, "Transfer already in progress")
            return false
        }

        transferScope.launch {
            val result = performFileUpload(filePath, fileName, pcAddress, port)
            fileTransferCallback?.invoke(fileName, result.success, result.errorMessage)
        }
        
        return true
    }

    /**
     * Perform complete session upload
     */
    private suspend fun performSessionUpload(sessionInfo: SessionInfo, pcAddress: String, port: Int) {
        isTransferActive.set(true)
        totalBytesTransferred.set(0L)
        val transferResults = mutableListOf<TransferResult>()
        
        try {
            Logger.i(TAG, "Uploading session: ${sessionInfo.sessionId}")
            
            // Calculate total size of all files
            val totalSize = calculateTotalSize(sessionInfo)
            Logger.d(TAG, "Total upload size: ${totalSize / (1024 * 1024)}MB")
            
            // Upload session metadata first
            val metadataFile = File(sessionInfo.sessionDirectory, "session_metadata.json")
            if (metadataFile.exists()) {
                val metadataResult = performFileUpload(
                    metadataFile.absolutePath, 
                    "session_metadata.json", 
                    pcAddress, 
                    port
                )
                transferResults.add(metadataResult)
            }
            
            // Upload recorded files
            sessionInfo.recordedFiles.forEach { recordedFile ->
                val file = File(recordedFile.path)
                if (file.exists()) {
                    val result = performFileUpload(
                        file.absolutePath,
                        file.name,
                        pcAddress,
                        port,
                        sessionInfo.sessionId
                    )
                    transferResults.add(result)
                    
                    if (result.success) {
                        totalBytesTransferred.addAndGet(result.bytesTransferred)
                    }
                } else {
                    Logger.w(TAG, "File not found: ${recordedFile.path}")
                    transferResults.add(TransferResult(
                        fileName = file.name,
                        success = false,
                        errorMessage = "File not found",
                        bytesTransferred = 0L
                    ))
                }
            }
            
            // Upload any additional files in session directory
            sessionInfo.sessionDirectory.listFiles()?.forEach { file ->
                if (file.isFile() && !isFileAlreadyUploaded(file.name, transferResults)) {
                    val result = performFileUpload(
                        file.absolutePath,
                        file.name,
                        pcAddress,
                        port,
                        sessionInfo.sessionId
                    )
                    transferResults.add(result)
                    
                    if (result.success) {
                        totalBytesTransferred.addAndGet(result.bytesTransferred)
                    }
                }
            }
            
            // Send transfer completion notification
            sendTransferCompletionNotification(sessionInfo.sessionId, pcAddress, port, transferResults)
            
            val successCount = transferResults.count { it.success }
            val totalCount = transferResults.size
            
            Logger.i(TAG, "Session upload completed: $successCount/$totalCount files successful")
            transferCompleteCallback?.invoke(
                successCount == totalCount,
                if (successCount == totalCount) null else "Some files failed to transfer",
                transferResults
            )
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error during session upload", e)
            transferCompleteCallback?.invoke(false, e.message, transferResults)
            
        } finally {
            isTransferActive.set(false)
        }
    }

    /**
     * Perform individual file upload with retry logic
     */
    private suspend fun performFileUpload(
        filePath: String, 
        fileName: String, 
        pcAddress: String, 
        port: Int,
        sessionId: String? = null
    ): TransferResult {
        var lastError: Exception? = null
        
        repeat(MAX_RETRY_ATTEMPTS) { attempt ->
            try {
                Logger.d(TAG, "Uploading file: $fileName (attempt ${attempt + 1})")
                
                val file = File(filePath)
                if (!file.exists()) {
                    return TransferResult(fileName, false, "File not found", 0L)
                }
                
                val result = uploadFileToServer(file, fileName, pcAddress, port, sessionId)
                
                if (result.success) {
                    Logger.i(TAG, "Successfully uploaded: $fileName (${result.bytesTransferred} bytes)")
                    return result
                } else {
                    Logger.w(TAG, "Upload failed for $fileName: ${result.errorMessage}")
                    lastError = Exception(result.errorMessage)
                }
                
            } catch (e: Exception) {
                Logger.w(TAG, "Upload attempt ${attempt + 1} failed for $fileName", e)
                lastError = e
                
                if (attempt < MAX_RETRY_ATTEMPTS - 1) {
                    delay(RETRY_DELAY_MS)
                }
            }
        }
        
        return TransferResult(
            fileName = fileName,
            success = false,
            errorMessage = lastError?.message ?: "Upload failed after $MAX_RETRY_ATTEMPTS attempts",
            bytesTransferred = 0L
        )
    }

    /**
     * Upload file to server using HTTP POST
     */
    private suspend fun uploadFileToServer(
        file: File,
        fileName: String,
        pcAddress: String,
        port: Int,
        sessionId: String?
    ): TransferResult = withContext(Dispatchers.IO) {
        
        var socket: Socket? = null
        var outputStream: OutputStream? = null
        var inputStream: InputStream? = null
        
        try {
            // Connect to server
            socket = Socket()
            socket.connect(InetSocketAddress(pcAddress, port), CONNECTION_TIMEOUT_MS)
            socket.soTimeout = TRANSFER_TIMEOUT_MS
            
            outputStream = socket.getOutputStream()
            inputStream = socket.getInputStream()
            
            // Send file upload request header
            val header = createUploadHeader(file, fileName, sessionId)
            outputStream.write(header.toByteArray())
            outputStream.flush()
            
            // Send file data in chunks
            val fileInputStream = FileInputStream(file)
            val buffer = ByteArray(CHUNK_SIZE)
            var bytesTransferred = 0L
            var bytesRead: Int
            
            currentTransferProgress.set(0L)
            
            while (fileInputStream.read(buffer).also { bytesRead = it } != -1) {
                outputStream.write(buffer, 0, bytesRead)
                bytesTransferred += bytesRead
                currentTransferProgress.set(bytesTransferred)
                
                // Update progress callback
                val progress = (bytesTransferred.toDouble() / file.length()) * 100.0
                transferProgressCallback?.invoke(fileName, bytesTransferred, file.length(), progress)
            }
            
            outputStream.flush()
            fileInputStream.close()
            
            // Read response from server
            val response = readServerResponse(inputStream)
            
            if (response.success) {
                // Verify file integrity if checksum provided
                val localChecksum = calculateFileChecksum(file)
                if (response.checksum != null && response.checksum != localChecksum) {
                    return@withContext TransferResult(
                        fileName = fileName,
                        success = false,
                        errorMessage = "Checksum mismatch",
                        bytesTransferred = bytesTransferred
                    )
                }
                
                return@withContext TransferResult(
                    fileName = fileName,
                    success = true,
                    errorMessage = null,
                    bytesTransferred = bytesTransferred
                )
            } else {
                return@withContext TransferResult(
                    fileName = fileName,
                    success = false,
                    errorMessage = response.errorMessage ?: "Server rejected upload",
                    bytesTransferred = bytesTransferred
                )
            }
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error uploading file: $fileName", e)
            return@withContext TransferResult(
                fileName = fileName,
                success = false,
                errorMessage = e.message ?: "Unknown error",
                bytesTransferred = 0L
            )
            
        } finally {
            try {
                outputStream?.close()
                inputStream?.close()
                socket?.close()
            } catch (e: Exception) {
                Logger.w(TAG, "Error closing upload connection", e)
            }
        }
    }

    /**
     * Create HTTP upload header
     */
    private fun createUploadHeader(file: File, fileName: String, sessionId: String?): String {
        val boundary = "----MultiSensorUpload${System.currentTimeMillis()}"
        val checksum = calculateFileChecksum(file)
        
        return buildString {
            append("POST /upload HTTP/1.1\r\n")
            append("Host: android-device\r\n")
            append("Content-Type: multipart/form-data; boundary=$boundary\r\n")
            append("Content-Length: ${file.length() + 500}\r\n") // Approximate with headers
            append("X-Session-ID: ${sessionId ?: "unknown"}\r\n")
            append("X-File-Checksum: $checksum\r\n")
            append("\r\n")
            append("--$boundary\r\n")
            append("Content-Disposition: form-data; name=\"file\"; filename=\"$fileName\"\r\n")
            append("Content-Type: application/octet-stream\r\n")
            append("\r\n")
        }
    }

    /**
     * Calculate file checksum (MD5)
     */
    private fun calculateFileChecksum(file: File): String {
        return try {
            val md = MessageDigest.getInstance("MD5")
            val inputStream = FileInputStream(file)
            val buffer = ByteArray(8192)
            var bytesRead: Int
            
            while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                md.update(buffer, 0, bytesRead)
            }
            
            inputStream.close()
            
            val digest = md.digest()
            digest.joinToString("") { "%02x".format(it) }
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error calculating checksum", e)
            "unknown"
        }
    }

    /**
     * Read server response
     */
    private fun readServerResponse(inputStream: InputStream): ServerResponse {
        return try {
            val reader = BufferedReader(InputStreamReader(inputStream))
            val responseLine = reader.readLine()
            
            if (responseLine?.contains("200 OK") == true) {
                // Read JSON response body
                val jsonLine = reader.readLine()
                val json = JSONObject(jsonLine ?: "{}")
                
                ServerResponse(
                    success = json.optBoolean("success", true),
                    errorMessage = json.optString("error"),
                    checksum = json.optString("checksum")
                )
            } else {
                ServerResponse(false, "HTTP error: $responseLine", null)
            }
        } catch (e: Exception) {
            Logger.e(TAG, "Error reading server response", e)
            ServerResponse(false, e.message, null)
        }
    }

    /**
     * Send transfer completion notification
     */
    private suspend fun sendTransferCompletionNotification(
        sessionId: String,
        pcAddress: String,
        port: Int,
        results: List<TransferResult>
    ) {
        try {
            val notification = JSONObject().apply {
                put("type", "transfer_complete")
                put("sessionId", sessionId)
                put("timestamp", System.currentTimeMillis())
                put("totalFiles", results.size)
                put("successfulFiles", results.count { it.success })
                put("totalBytes", results.sumOf { it.bytesTransferred })
            }
            
            // Send notification (simplified - could use existing PC communication)
            Logger.i(TAG, "Transfer completed for session: $sessionId")
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error sending completion notification", e)
        }
    }

    /**
     * Calculate total size of session files
     */
    private fun calculateTotalSize(sessionInfo: SessionInfo): Long {
        var totalSize = 0L
        
        sessionInfo.recordedFiles.forEach { recordedFile ->
            val file = File(recordedFile.path)
            if (file.exists()) {
                totalSize += file.length()
            }
        }
        
        // Add other files in session directory
        sessionInfo.sessionDirectory.listFiles()?.forEach { file ->
            if (file.isFile()) {
                totalSize += file.length()
            }
        }
        
        return totalSize
    }

    /**
     * Check if file was already uploaded
     */
    private fun isFileAlreadyUploaded(fileName: String, results: List<TransferResult>): Boolean {
        return results.any { it.fileName == fileName }
    }

    /**
     * Set transfer progress callback
     */
    fun setTransferProgressCallback(callback: (String, Long, Long, Double) -> Unit) {
        transferProgressCallback = callback
    }

    /**
     * Set transfer complete callback
     */
    fun setTransferCompleteCallback(callback: (Boolean, String?, List<TransferResult>) -> Unit) {
        transferCompleteCallback = callback
    }

    /**
     * Set file transfer callback
     */
    fun setFileTransferCallback(callback: (String, Boolean, String?) -> Unit) {
        fileTransferCallback = callback
    }

    /**
     * Check if transfer is currently active
     */
    fun isTransferActive(): Boolean = isTransferActive.get()

    /**
     * Get current transfer progress
     */
    fun getTransferProgress(): TransferProgress {
        return TransferProgress(
            isActive = isTransferActive.get(),
            totalBytesTransferred = totalBytesTransferred.get(),
            currentFileProgress = currentTransferProgress.get()
        )
    }

    /**
     * Cleanup resources
     */
    fun cleanup() {
        transferScope.cancel()
    }
}

/**
 * Data classes for transfer operations
 */
data class TransferResult(
    val fileName: String,
    val success: Boolean,
    val errorMessage: String?,
    val bytesTransferred: Long
)

data class ServerResponse(
    val success: Boolean,
    val errorMessage: String?,
    val checksum: String?
)

data class TransferProgress(
    val isActive: Boolean,
    val totalBytesTransferred: Long,
    val currentFileProgress: Long
)