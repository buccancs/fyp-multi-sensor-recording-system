package com.multisensor.recording.network

import android.util.Log
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.*
import java.net.*
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

/**
 * FR7: Device Synchronisation and Signals - PC communication client
 * Handles commands from PC server for coordinated recording sessions
 */
class PcCommunicationClient {
    
    companion object {
        private const val TAG = "PcCommunicationClient"
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
    private var commandCallback: ((PcCommand) -> Unit)? = null
    private var connectionCallback: ((Boolean, String?) -> Unit)? = null

    /**
     * Connect to PC server
     */
    fun connectToPc(pcAddress: String, port: Int = DEFAULT_PC_SERVER_PORT): Boolean {
        if (isConnected.get()) {
            Logger.w(TAG, "Already connected to PC")
            return true
        }

        Logger.i(TAG, "Connecting to PC at $pcAddress:$port")
        
        return try {
            // Create socket connection
            val socket = Socket()
            socket.connect(InetSocketAddress(pcAddress, port), CONNECTION_TIMEOUT_MS)
            
            clientSocket = socket
            outputStream = PrintWriter(socket.getOutputStream(), true)
            inputStream = BufferedReader(InputStreamReader(socket.getInputStream()))
            
            currentPcAddress.set(pcAddress)
            currentPort.set(port)
            isConnected.set(true)
            
            // Start message listener and heartbeat
            startMessageListener()
            startHeartbeat()
            
            // Send initial connection message
            sendDeviceInfo()
            
            connectionCallback?.invoke(true, null)
            Logger.i(TAG, "Successfully connected to PC at $pcAddress:$port")
            true
            
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to connect to PC", e)
            connectionCallback?.invoke(false, e.message)
            false
        }
    }

    /**
     * Disconnect from PC server
     */
    fun disconnect() {
        Logger.i(TAG, "Disconnecting from PC")
        
        isConnected.set(false)
        isReconnecting.set(false)
        
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
     * Set callback for received PC commands
     */
    fun setCommandCallback(callback: (PcCommand) -> Unit) {
        commandCallback = callback
    }

    /**
     * Set callback for connection status changes
     */
    fun setConnectionCallback(callback: (Boolean, String?) -> Unit) {
        connectionCallback = callback
    }

    /**
     * Send response to PC
     */
    fun sendResponse(command: String, success: Boolean, message: String? = null, data: Any? = null) {
        if (!isConnected.get()) {
            Logger.w(TAG, "Cannot send response - not connected")
            return
        }

        val response = JSONObject().apply {
            put("type", "response")
            put("command", command)
            put("success", success)
            put("message", message)
            put("timestamp", System.currentTimeMillis())
            if (data != null) {
                put("data", data)
            }
        }

        sendMessage(response.toString())
    }

    /**
     * Send status update to PC
     */
    fun sendStatusUpdate(status: String, data: JSONObject? = null) {
        if (!isConnected.get()) return

        val message = JSONObject().apply {
            put("type", "status")
            put("status", status)
            put("timestamp", System.currentTimeMillis())
            if (data != null) {
                put("data", data)
            }
        }

        sendMessage(message.toString())
    }

    /**
     * Check if connected to PC
     */
    fun isConnected(): Boolean = isConnected.get()

    /**
     * Start automatic message listener
     */
    private fun startMessageListener() {
        messageListenerJob = clientScope.launch {
            try {
                while (isConnected.get() && !currentCoroutineContext().isActive.not()) {
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
     * Start heartbeat mechanism
     */
    private fun startHeartbeat() {
        heartbeatJob = clientScope.launch {
            while (isConnected.get()) {
                delay(HEARTBEAT_INTERVAL_MS)
                
                if (isConnected.get()) {
                    val heartbeat = JSONObject().apply {
                        put("type", "heartbeat")
                        put("timestamp", System.currentTimeMillis())
                    }
                    
                    if (!sendMessage(heartbeat.toString())) {
                        Logger.w(TAG, "Heartbeat failed")
                        break
                    }
                }
            }
        }
    }

    /**
     * Process received message from PC
     */
    private fun processReceivedMessage(message: String) {
        try {
            val json = JSONObject(message)
            val type = json.getString("type")
            
            when (type) {
                "command" -> {
                    val command = PcCommand.fromJson(json)
                    Logger.d(TAG, "Received command: ${command.action}")
                    commandCallback?.invoke(command)
                }
                "heartbeat_response" -> {
                    // Heartbeat acknowledged
                    Logger.d(TAG, "Heartbeat acknowledged")
                }
                "sync_signal" -> {
                    // Synchronization signal (flash, beep, etc.)
                    val signalType = json.optString("signalType", "flash")
                    val command = PcCommand("sync_signal", mutableMapOf<String, Any>(), json.optLong("timestamp"))
                    command.parameters["signalType"] = signalType
                    commandCallback?.invoke(command)
                }
                else -> {
                    Logger.w(TAG, "Unknown message type: $type")
                }
            }
            
        } catch (e: Exception) {
            Logger.e(TAG, "Error processing message: $message", e)
        }
    }

    /**
     * Send message to PC
     */
    private fun sendMessage(message: String): Boolean {
        return try {
            outputStream?.println(message)
            outputStream?.flush()
            true
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to send message", e)
            handleConnectionError(e)
            false
        }
    }

    /**
     * Send device information to PC
     */
    private fun sendDeviceInfo() {
        val deviceInfo = JSONObject().apply {
            put("type", "device_info")
            put("deviceId", android.os.Build.MODEL)
            put("deviceName", android.os.Build.DEVICE)
            put("androidVersion", android.os.Build.VERSION.RELEASE)
            put("appVersion", "1.0")
            put("capabilities", org.json.JSONArray().apply {
                put("rgb_camera")
                put("thermal_camera")
                put("gsr_sensor")
                put("time_sync")
            })
            put("timestamp", System.currentTimeMillis())
        }

        sendMessage(deviceInfo.toString())
    }

    /**
     * Handle connection errors and attempt reconnection
     */
    private fun handleConnectionError(error: Exception) {
        Logger.w(TAG, "Connection error: ${error.message}")
        
        if (isConnected.get() && !isReconnecting.get()) {
            isReconnecting.set(true)
            
            clientScope.launch {
                disconnect()
                delay(RECONNECT_DELAY_MS)
                
                val pcAddress = currentPcAddress.get()
                val port = currentPort.get()
                
                if (pcAddress != null && isReconnecting.get()) {
                    Logger.i(TAG, "Attempting to reconnect to PC...")
                    val reconnected = connectToPc(pcAddress, port)
                    
                    if (reconnected) {
                        Logger.i(TAG, "Successfully reconnected to PC")
                    } else {
                        Logger.w(TAG, "Failed to reconnect to PC")
                    }
                }
                
                isReconnecting.set(false)
            }
        }
    }

    /**
     * Cleanup resources
     */
    fun cleanup() {
        disconnect()
        clientScope.cancel()
    }
}

/**
 * PC command data class
 */
data class PcCommand(
    val action: String,
    val parameters: MutableMap<String, Any> = mutableMapOf(),
    val timestamp: Long = System.currentTimeMillis()
) {
    companion object {
        fun fromJson(json: JSONObject): PcCommand {
            val action = json.getString("action")
            val timestamp = json.optLong("timestamp", System.currentTimeMillis())
            val parameters = mutableMapOf<String, Any>()
            
            val params = json.optJSONObject("parameters")
            params?.keys()?.forEach { key ->
                parameters[key] = params.get(key)
            }
            
            return PcCommand(action, parameters, timestamp)
        }
    }
}