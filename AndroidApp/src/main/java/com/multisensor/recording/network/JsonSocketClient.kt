package com.multisensor.recording.network

import com.multisensor.recording.util.Logger
import dagger.hilt.android.scopes.ServiceScoped
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.IOException
import java.net.Socket
import java.nio.ByteBuffer
import java.nio.ByteOrder
import javax.inject.Inject

/**
 * JSON Socket Client for Milestone 2.6 Network Communication.
 * Implements length-prefixed JSON message protocol for bidirectional communication with PC server.
 * 
 * Based on 2_6_milestone.md specifications:
 * - TCP connection to PC server on port 9000
 * - Length-prefixed framing (4-byte length header + JSON payload)
 * - Auto-reconnection with retry logic
 * - Command processing and acknowledgment system
 */
@ServiceScoped
class JsonSocketClient @Inject constructor(
    private val logger: Logger
) {
    
    private var socket: Socket? = null
    private var inputStream: BufferedInputStream? = null
    private var outputStream: BufferedOutputStream? = null
    private var connectionScope: CoroutineScope? = null
    private var isConnected = false
    private var shouldReconnect = true
    
    // Connection configuration
    private var serverIp: String = "192.168.1.100" // Default IP, configurable
    private var serverPort: Int = 9000 // Milestone 2.6 specifies port 9000
    
    // Callback for incoming commands
    private var commandCallback: ((JsonMessage) -> Unit)? = null
    
    companion object {
        private const val RECONNECT_DELAY_MS = 5000L
        private const val CONNECTION_TIMEOUT_MS = 10000
        private const val LENGTH_HEADER_SIZE = 4 // 4-byte length prefix
    }
    
    /**
     * Configure server connection details
     */
    fun configure(ip: String, port: Int = 9000) {
        serverIp = ip
        serverPort = port
        logger.info("JsonSocketClient configured for $ip:$port")
    }
    
    /**
     * Set callback for incoming command messages
     */
    fun setCommandCallback(callback: (JsonMessage) -> Unit) {
        commandCallback = callback
    }
    
    /**
     * Start connection to PC server with auto-reconnect
     */
    fun connect() {
        if (isConnected) {
            logger.warning("JsonSocketClient already connected")
            return
        }
        
        shouldReconnect = true
        connectionScope = CoroutineScope(Dispatchers.IO + Job())
        
        connectionScope?.launch {
            connectWithRetry()
        }
        
        logger.info("JsonSocketClient connection started")
    }
    
    /**
     * Disconnect from server and stop reconnection attempts
     */
    fun disconnect() {
        logger.info("Disconnecting JsonSocketClient...")
        shouldReconnect = false
        
        try {
            // Close socket resources
            outputStream?.close()
            inputStream?.close()
            socket?.close()
            
            // Cancel coroutines
            connectionScope?.cancel()
            
            isConnected = false
            socket = null
            inputStream = null
            outputStream = null
            connectionScope = null
            
            logger.info("JsonSocketClient disconnected successfully")
            
        } catch (e: Exception) {
            logger.error("Error disconnecting JsonSocketClient", e)
        }
    }
    
    /**
     * Send JSON message to PC server using length-prefixed framing
     */
    fun sendMessage(message: JsonMessage) {
        if (!isConnected) {
            logger.warning("Cannot send message - not connected to server")
            return
        }
        
        connectionScope?.launch {
            try {
                val jsonString = JsonMessage.toJson(message)
                val jsonBytes = jsonString.toByteArray(Charsets.UTF_8)
                
                // Create length-prefixed message
                val lengthHeader = ByteBuffer.allocate(LENGTH_HEADER_SIZE)
                    .order(ByteOrder.BIG_ENDIAN)
                    .putInt(jsonBytes.size)
                    .array()
                
                // Send length header followed by JSON payload
                outputStream?.write(lengthHeader)
                outputStream?.write(jsonBytes)
                outputStream?.flush()
                
                logger.debug("Sent message: ${message.type} (${jsonBytes.size} bytes)")
                
            } catch (e: IOException) {
                logger.error("Error sending message", e)
                handleConnectionError()
            }
        }
    }
    
    /**
     * Send device introduction message on connection
     */
    fun sendHelloMessage(deviceId: String, capabilities: List<String>) {
        val helloMessage = HelloMessage(
            device_id = deviceId,
            capabilities = capabilities
        )
        sendMessage(helloMessage)
    }
    
    /**
     * Send acknowledgment message for received command
     */
    fun sendAck(commandType: String, success: Boolean, errorMessage: String? = null) {
        val ackMessage = AckMessage(
            cmd = commandType,
            status = if (success) "ok" else "error",
            message = errorMessage
        )
        sendMessage(ackMessage)
    }
    
    /**
     * Send device status update
     */
    fun sendStatusUpdate(battery: Int?, storage: String?, temperature: Double?, recording: Boolean) {
        val statusMessage = StatusMessage(
            battery = battery,
            storage = storage,
            temperature = temperature,
            recording = recording,
            connected = true
        )
        sendMessage(statusMessage)
    }
    
    /**
     * Connection with retry logic
     */
    private suspend fun connectWithRetry() {
        while (shouldReconnect && !isConnected) {
            try {
                logger.info("Attempting to connect to $serverIp:$serverPort...")
                
                socket = Socket().apply {
                    soTimeout = CONNECTION_TIMEOUT_MS
                    connect(java.net.InetSocketAddress(serverIp, serverPort), CONNECTION_TIMEOUT_MS)
                }
                
                inputStream = BufferedInputStream(socket?.getInputStream())
                outputStream = BufferedOutputStream(socket?.getOutputStream())
                isConnected = true
                
                logger.info("Connected to PC server at $serverIp:$serverPort")
                
                // Send hello message to introduce this device
                sendHelloMessage(
                    deviceId = android.os.Build.MODEL + "_" + android.os.Build.SERIAL.takeLast(4),
                    capabilities = listOf("rgb_video", "thermal", "shimmer")
                )
                
                // Start listening for incoming messages
                startMessageListener()
                
            } catch (e: Exception) {
                logger.error("Connection failed: ${e.message}")
                handleConnectionError()
                
                if (shouldReconnect) {
                    logger.info("Retrying connection in ${RECONNECT_DELAY_MS}ms...")
                    delay(RECONNECT_DELAY_MS)
                }
            }
        }
    }
    
    /**
     * Listen for incoming messages with length-prefixed framing
     */
    private suspend fun startMessageListener() {
        try {
            while (isConnected && shouldReconnect) {
                // Read 4-byte length header
                val lengthHeader = ByteArray(LENGTH_HEADER_SIZE)
                var bytesRead = 0
                
                while (bytesRead < LENGTH_HEADER_SIZE) {
                    val read = inputStream?.read(lengthHeader, bytesRead, LENGTH_HEADER_SIZE - bytesRead) ?: -1
                    if (read == -1) {
                        throw IOException("Connection closed while reading length header")
                    }
                    bytesRead += read
                }
                
                // Parse message length
                val messageLength = ByteBuffer.wrap(lengthHeader)
                    .order(ByteOrder.BIG_ENDIAN)
                    .int
                
                if (messageLength <= 0 || messageLength > 1024 * 1024) { // Max 1MB message
                    throw IOException("Invalid message length: $messageLength")
                }
                
                // Read JSON payload
                val messageBytes = ByteArray(messageLength)
                bytesRead = 0
                
                while (bytesRead < messageLength) {
                    val read = inputStream?.read(messageBytes, bytesRead, messageLength - bytesRead) ?: -1
                    if (read == -1) {
                        throw IOException("Connection closed while reading message payload")
                    }
                    bytesRead += read
                }
                
                // Parse and process JSON message
                val jsonString = String(messageBytes, Charsets.UTF_8)
                val message = JsonMessage.fromJson(jsonString)
                
                if (message != null) {
                    logger.debug("Received message: ${message.type}")
                    commandCallback?.invoke(message)
                } else {
                    logger.warning("Failed to parse JSON message: $jsonString")
                }
            }
        } catch (e: IOException) {
            logger.error("Error in message listener", e)
            handleConnectionError()
        }
    }
    
    /**
     * Handle connection errors and initiate reconnection
     */
    private suspend fun handleConnectionError() {
        if (!isConnected) return
        
        logger.warning("Connection error detected, attempting to reconnect...")
        
        try {
            outputStream?.close()
            inputStream?.close()
            socket?.close()
        } catch (e: Exception) {
            logger.debug("Error closing connection resources", e)
        }
        
        isConnected = false
        socket = null
        inputStream = null
        outputStream = null
        
        // Attempt reconnection if enabled
        if (shouldReconnect) {
            delay(RECONNECT_DELAY_MS)
            connectWithRetry()
        }
    }
    
    /**
     * Check if currently connected to server
     */
    fun isConnected(): Boolean = isConnected
    
    /**
     * Get current connection information
     */
    fun getConnectionInfo(): String {
        return if (isConnected) {
            "Connected to $serverIp:$serverPort"
        } else {
            "Disconnected"
        }
    }
}
