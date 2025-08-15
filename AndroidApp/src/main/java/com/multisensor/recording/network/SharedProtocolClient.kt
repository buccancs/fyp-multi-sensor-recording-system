package com.multisensor.recording.network

import android.util.Log
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.*
import java.net.*
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

/**
 * Enhanced PC communication client using shared protocols
 * Implements standardized message format for Python-Android communication
 */
class SharedProtocolClient {
    
    companion object {
        private const val TAG = "SharedProtocolClient"
        private const val DEFAULT_PC_SERVER_PORT = 8080
        private const val HEARTBEAT_INTERVAL_MS = 5000L
        private const val CONNECTION_TIMEOUT_MS = 10000
        private const val RECONNECT_DELAY_MS = 3000L
    }

    // Connection state
    private val isConnected = AtomicBoolean(false)
    private val isReconnecting = AtomicBoolean(false)
    private val currentPcAddress = AtomicReference<String?>(null)
    private val currentPort = AtomicReference<Int>(DEFAULT_PC_SERVER_PORT)
    
    // Network components
    private var clientSocket: Socket? = null
    private var outputStream: PrintWriter? = null
    private var inputStream: BufferedReader? = null
    
    // Coroutine scope for async operations
    private val clientScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var heartbeatJob: Job? = null
    private var messageListenerJob: Job? = null
    
    // Callback for received commands
    private var commandCallback: ((SharedProtocolMessage) -> Unit)? = null
    private var connectionCallback: ((Boolean, String?) -> Unit)? = null
    
    // Device information
    private var deviceId: String = "android_${System.currentTimeMillis()}"
    private var protocolVersion: String = "1.0"

    /**
     * Connect to PC server using shared protocol
     */
    fun connectToPc(pcAddress: String, port: Int = DEFAULT_PC_SERVER_PORT): Boolean {
        if (isConnected.get()) {
            Logger.w(TAG, "Already connected to PC")
            return true
        }

        Logger.i(TAG, "Connecting to PC at $pcAddress:$port")
        currentPcAddress.set(pcAddress)
        currentPort.set(port)

        return try {
            // Create socket connection
            clientSocket = Socket()
            clientSocket?.connect(InetSocketAddress(pcAddress, port), CONNECTION_TIMEOUT_MS)
            
            // Setup streams
            outputStream = PrintWriter(OutputStreamWriter(clientSocket?.getOutputStream()), true)
            inputStream = BufferedReader(InputStreamReader(clientSocket?.getInputStream()))
            
            isConnected.set(true)
            connectionCallback?.invoke(true, "Connected to PC server")
            
            // Send HELLO message
            sendHelloMessage()
            
            // Start message listener and heartbeat
            startMessageListener()
            startHeartbeat()
            
            Logger.i(TAG, "Successfully connected to PC")
            true
            
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to connect to PC", e)
            disconnectFromPc()
            false
        }
    }

    /**
     * Disconnect from PC server
     */
    fun disconnectFromPc() {
        if (!isConnected.get()) return
        
        Logger.i(TAG, "Disconnecting from PC")
        isConnected.set(false)
        
        // Send GOODBYE message if possible
        try {
            sendGoodbyeMessage()
        } catch (e: Exception) {
            Logger.w(TAG, "Could not send goodbye message", e)
        }
        
        // Cancel coroutines
        heartbeatJob?.cancel()
        messageListenerJob?.cancel()
        
        // Close network connections
        try {
            outputStream?.close()
            inputStream?.close()
            clientSocket?.close()
        } catch (e: Exception) {
            Logger.w(TAG, "Error closing connections", e)
        }
        
        outputStream = null
        inputStream = null
        clientSocket = null
        
        connectionCallback?.invoke(false, "Disconnected")
        Logger.i(TAG, "Disconnected from PC")
    }

    /**
     * Send HELLO message using shared protocol
     */
    private fun sendHelloMessage() {
        val deviceInfo = JSONObject().apply {
            put("device_id", deviceId)
            put("device_type", "android")
            put("model", android.os.Build.MODEL)
            put("os_version", android.os.Build.VERSION.RELEASE)
            put("capabilities", JSONArray().apply {
                put("recording")
                put("thermal")
                put("rgb")
                put("gsr")
            })
        }

        val message = JSONObject().apply {
            put("message_type", "hello")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
            put("device_info", deviceInfo)
            put("capabilities", JSONArray().apply {
                put("recording")
                put("thermal") 
                put("rgb")
                put("gsr")
            })
            put("protocol_version", protocolVersion)
        }

        sendMessage(message.toString())
    }

    /**
     * Send GOODBYE message using shared protocol
     */
    private fun sendGoodbyeMessage() {
        val message = JSONObject().apply {
            put("message_type", "goodbye")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
        }

        sendMessage(message.toString())
    }

    /**
     * Send heartbeat message using shared protocol
     */
    private fun sendHeartbeat() {
        if (!isConnected.get()) return

        val message = JSONObject().apply {
            put("message_type", "heartbeat")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
        }

        sendMessage(message.toString())
    }

    /**
     * Send device status update using shared protocol
     */
    fun sendDeviceStatus(deviceState: String, batteryLevel: Float? = null, errorMessage: String? = null) {
        if (!isConnected.get()) return

        val message = JSONObject().apply {
            put("message_type", "device_status")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
            put("device_state", deviceState)
            if (batteryLevel != null) put("battery_level", batteryLevel)
            if (errorMessage != null) put("error_message", errorMessage)
            put("additional_info", JSONObject())
        }

        sendMessage(message.toString())
    }

    /**
     * Send session control message using shared protocol
     */
    fun sendSessionControl(action: String, sessionConfig: JSONObject? = null) {
        if (!isConnected.get()) return

        val message = JSONObject().apply {
            put("message_type", if (action == "start") "session_start" else "session_stop")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
            put("action", action)
            if (sessionConfig != null) put("session_config", sessionConfig)
        }

        sendMessage(message.toString())
    }

    /**
     * Send command response using shared protocol
     */
    fun sendCommandResponse(originalCommand: String, success: Boolean, result: JSONObject? = null, errorMessage: String? = null) {
        if (!isConnected.get()) return

        val message = JSONObject().apply {
            put("message_type", "response")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
            put("original_command", originalCommand)
            put("success", success)
            if (result != null) put("result", result)
            if (errorMessage != null) put("error_message", errorMessage)
        }

        sendMessage(message.toString())
    }

    /**
     * Send error message using shared protocol
     */
    fun sendError(errorCode: String, errorMessage: String, context: JSONObject? = null) {
        if (!isConnected.get()) return

        val message = JSONObject().apply {
            put("message_type", "error")
            put("timestamp", System.currentTimeMillis() / 1000.0)
            put("device_id", deviceId)
            put("error_code", errorCode)
            put("error_message", errorMessage)
            if (context != null) put("context", context)
        }

        sendMessage(message.toString())
    }

    /**
     * Set callback for received messages
     */
    fun setCommandCallback(callback: (SharedProtocolMessage) -> Unit) {
        commandCallback = callback
    }

    /**
     * Set callback for connection status changes
     */
    fun setConnectionCallback(callback: (Boolean, String?) -> Unit) {
        connectionCallback = callback
    }

    /**
     * Check if connected to PC
     */
    fun isConnected(): Boolean = isConnected.get()

    /**
     * Get device ID
     */
    fun getDeviceId(): String = deviceId

    /**
     * Set device ID
     */
    fun setDeviceId(newDeviceId: String) {
        deviceId = newDeviceId
    }

    /**
     * Send raw message to PC
     */
    private fun sendMessage(message: String) {
        try {
            outputStream?.println(message)
            Logger.d(TAG, "Sent message: ${message.take(100)}...")
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to send message", e)
            handleConnectionError(e)
        }
    }

    /**
     * Start automatic heartbeat
     */
    private fun startHeartbeat() {
        heartbeatJob = clientScope.launch {
            while (isConnected.get() && currentCoroutineContext().isActive) {
                try {
                    sendHeartbeat()
                    delay(HEARTBEAT_INTERVAL_MS)
                } catch (e: Exception) {
                    if (isConnected.get()) {
                        Logger.e(TAG, "Heartbeat error", e)
                        handleConnectionError(e)
                    }
                    break
                }
            }
        }
    }

    /**
     * Start automatic message listener
     */
    private fun startMessageListener() {
        messageListenerJob = clientScope.launch {
            try {
                while (isConnected.get() && currentCoroutineContext().isActive) {
                    val message = inputStream?.readLine()
                    if (message == null) {
                        Logger.w(TAG, "Received null message, connection may be closed")
                        break
                    }
                    
                    processReceivedMessage(message)
                }
            } catch (e: Exception) {
                if (isConnected.get()) {
                    Logger.e(TAG, "Message listener error", e)
                    handleConnectionError(e)
                }
            }
        }
    }

    /**
     * Process received message using shared protocol
     */
    private fun processReceivedMessage(message: String) {
        try {
            val jsonMessage = JSONObject(message)
            val messageType = jsonMessage.optString("message_type", "")
            
            Logger.d(TAG, "Received message type: $messageType")
            
            val protocolMessage = SharedProtocolMessage(
                messageType = messageType,
                timestamp = jsonMessage.optDouble("timestamp", 0.0),
                sessionId = jsonMessage.optString("session_id", null),
                deviceId = jsonMessage.optString("device_id", null),
                data = jsonMessage
            )
            
            commandCallback?.invoke(protocolMessage)
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error processing received message", e)
        }
    }

    /**
     * Handle connection errors
     */
    private fun handleConnectionError(error: Exception) {
        if (isReconnecting.get()) return
        
        Logger.w(TAG, "Connection error occurred", error)
        disconnectFromPc()
        
        // Attempt reconnection if we have connection details
        val pcAddress = currentPcAddress.get()
        val port = currentPort.get()
        
        if (pcAddress != null) {
            isReconnecting.set(true)
            clientScope.launch {
                delay(RECONNECT_DELAY_MS)
                Logger.i(TAG, "Attempting to reconnect...")
                
                try {
                    if (connectToPc(pcAddress, port)) {
                        Logger.i(TAG, "Reconnection successful")
                    } else {
                        Logger.w(TAG, "Reconnection failed")
                    }
                } finally {
                    isReconnecting.set(false)
                }
            }
        }
    }
}

/**
 * Data class for shared protocol messages
 */
data class SharedProtocolMessage(
    val messageType: String,
    val timestamp: Double,
    val sessionId: String?,
    val deviceId: String?,
    val data: JSONObject
)