package com.multisensor.recording.network

import com.multisensor.recording.util.Logger
import dagger.hilt.android.scopes.ServiceScoped
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.Socket
import javax.inject.Inject

/**
 * Manages socket connection between the Android phone and PC controller.
 * Acts as a client connecting to the PC server to receive commands and send status updates.
 * 
 * Design: PC acts as server, phone connects as client for remote control functionality.
 */
@ServiceScoped
class SocketController @Inject constructor(
    private val logger: Logger
) {
    
    private var socket: Socket? = null
    private var reader: BufferedReader? = null
    private var writer: PrintWriter? = null
    private var connectionScope: CoroutineScope? = null
    private var isConnected = false
    private var shouldReconnect = true
    
    // Callback for service commands
    private var serviceCallback: ((String) -> Unit)? = null
    
    // Connection configuration
    private var serverIp: String = "192.168.1.100" // TODO: Make configurable
    private var serverPort: Int = 8080
    
    companion object {
        private const val RECONNECT_DELAY_MS = 5000L
        private const val CONNECTION_TIMEOUT_MS = 10000
    }
    
    /**
     * Set the callback function for service commands
     */
    fun setServiceCallback(callback: (String) -> Unit) {
        serviceCallback = callback
    }
    
    /**
     * Configure server connection details
     */
    fun configure(ip: String, port: Int) {
        serverIp = ip
        serverPort = port
        logger.info("SocketController configured for $ip:$port")
    }
    
    /**
     * Start listening for commands from PC
     */
    fun startListening() {
        if (isConnected) {
            logger.warning("SocketController already connected")
            return
        }
        
        shouldReconnect = true
        connectionScope = CoroutineScope(Dispatchers.IO + Job())
        
        connectionScope?.launch {
            connectWithRetry()
        }
        
        logger.info("SocketController started listening")
    }
    
    /**
     * Stop the socket connection
     */
    fun stop() {
        logger.info("Stopping SocketController...")
        shouldReconnect = false
        
        try {
            // Close socket resources
            writer?.close()
            reader?.close()
            socket?.close()
            
            // Cancel coroutines
            connectionScope?.cancel()
            
            isConnected = false
            socket = null
            reader = null
            writer = null
            connectionScope = null
            
            logger.info("SocketController stopped successfully")
            
        } catch (e: Exception) {
            logger.error("Error stopping SocketController", e)
        }
    }
    
    /**
     * Send a message to the PC
     */
    fun sendMessage(message: String) {
        if (!isConnected || writer == null) {
            logger.warning("Cannot send message - not connected to PC")
            return
        }
        
        try {
            writer?.println(message)
            writer?.flush()
            logger.debug("Sent message to PC: $message")
        } catch (e: Exception) {
            logger.error("Failed to send message to PC", e)
            handleConnectionError()
        }
    }
    
    /**
     * Send binary data to PC (for preview frames)
     */
    fun sendBytes(data: ByteArray) {
        if (!isConnected || socket == null) {
            logger.warning("Cannot send bytes - not connected to PC")
            return
        }
        
        try {
            val outputStream = socket?.getOutputStream()
            outputStream?.write(data.size) // Send length first
            outputStream?.write(data)
            outputStream?.flush()
            logger.debug("Sent ${data.size} bytes to PC")
        } catch (e: Exception) {
            logger.error("Failed to send bytes to PC", e)
            handleConnectionError()
        }
    }
    
    /**
     * Connect to PC with retry logic
     */
    private suspend fun connectWithRetry() {
        while (shouldReconnect && !isConnected) {
            try {
                logger.info("Attempting to connect to PC at $serverIp:$serverPort")
                
                socket = Socket().apply {
                    soTimeout = CONNECTION_TIMEOUT_MS
                    connect(java.net.InetSocketAddress(serverIp, serverPort), CONNECTION_TIMEOUT_MS)
                }
                
                reader = BufferedReader(InputStreamReader(socket?.getInputStream()))
                writer = PrintWriter(socket?.getOutputStream(), true)
                
                isConnected = true
                logger.info("Successfully connected to PC")
                
                // Send initial hello message
                sendMessage("HELLO ANDROID_CLIENT")
                
                // Start listening for commands
                startCommandListener()
                
            } catch (e: Exception) {
                logger.error("Failed to connect to PC: ${e.message}")
                handleConnectionError()
                
                if (shouldReconnect) {
                    logger.info("Retrying connection in ${RECONNECT_DELAY_MS}ms...")
                    delay(RECONNECT_DELAY_MS)
                }
            }
        }
    }
    
    /**
     * Listen for incoming commands from PC
     */
    private suspend fun startCommandListener() {
        try {
            var line: String?
            while (isConnected && shouldReconnect && reader?.readLine().also { line = it } != null) {
                line?.let { command ->
                    processCommand(command.trim())
                }
            }
        } catch (e: Exception) {
            logger.error("Error in command listener", e)
            handleConnectionError()
        }
    }
    
    /**
     * Process incoming commands from PC
     */
    private fun processCommand(command: String) {
        logger.info("Received command from PC: $command")
        
        when (command.uppercase()) {
            "START_RECORD" -> {
                serviceCallback?.invoke("START")
                sendMessage("ACK RECORDING_STARTED")
                logger.info("Executed START_RECORD command")
            }
            
            "STOP_RECORD" -> {
                serviceCallback?.invoke("STOP")
                sendMessage("ACK RECORDING_STOPPED")
                logger.info("Executed STOP_RECORD command")
            }
            
            "PING" -> {
                sendMessage("PONG")
                logger.debug("Responded to PING")
            }
            
            "GET_STATUS" -> {
                // TODO: Get actual status from service
                sendMessage("STATUS READY")
                logger.debug("Sent status response")
            }
            
            "CALIBRATE" -> {
                serviceCallback?.invoke("CALIBRATE")
                sendMessage("ACK CALIBRATION_STARTED")
                logger.info("Executed CALIBRATE command")
            }
            
            else -> {
                logger.warning("Unknown command received: $command")
                sendMessage("ERROR UNKNOWN_COMMAND")
            }
        }
    }
    
    /**
     * Handle connection errors and attempt reconnection
     */
    private fun handleConnectionError() {
        if (isConnected) {
            logger.warning("Connection to PC lost")
            isConnected = false
            
            try {
                socket?.close()
                reader?.close()
                writer?.close()
            } catch (e: Exception) {
                logger.error("Error closing connection resources", e)
            }
            
            socket = null
            reader = null
            writer = null
            
            // Attempt reconnection if still should reconnect
            if (shouldReconnect) {
                connectionScope?.launch {
                    delay(RECONNECT_DELAY_MS)
                    connectWithRetry()
                }
            }
        }
    }
    
    /**
     * Get current connection status
     */
    fun isConnected(): Boolean = isConnected
    
    /**
     * Get connection info
     */
    fun getConnectionInfo(): String {
        return if (isConnected) {
            "Connected to $serverIp:$serverPort"
        } else {
            "Disconnected"
        }
    }
}