package com.multisensor.recording.protocol

import android.content.Context
import android.util.Log
import com.multisensor.recording.config.CommonConstants
import org.json.JSONObject
import java.io.OutputStream
import java.net.Socket

/**
 * HandshakeManager for Android - handles initial handshake with version checking.
 * 
 * This class implements the handshake protocol described in Milestone 6 to ensure
 * compatibility between Android and Python applications by exchanging protocol
 * version information at connection start.
 */
class HandshakeManager(private val context: Context) {
    
    companion object {
        private const val TAG = "HandshakeManager"
        private const val HANDSHAKE_TIMEOUT_MS = 10000L // 10 seconds
    }
    
    private val schemaManager = SchemaManager.getInstance(context)
    
    /**
     * Send handshake message to the server.
     * 
     * @param socket Connected socket to send handshake through
     * @return true if handshake was sent successfully, false otherwise
     */
    fun sendHandshake(socket: Socket): Boolean {
        return try {
            val handshakeMessage = createHandshakeMessage()
            val messageJson = handshakeMessage.toString()
            
            Log.i(TAG, "Sending handshake: $messageJson")
            
            val outputStream = socket.getOutputStream()
            outputStream.write(messageJson.toByteArray())
            outputStream.write('\n'.code) // Add newline delimiter
            outputStream.flush()
            
            Log.i(TAG, "Handshake sent successfully")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send handshake: ${e.message}", e)
            false
        }
    }
    
    /**
     * Process received handshake acknowledgment.
     * 
     * @param ackMessage JSON object containing handshake acknowledgment
     * @return true if handshake is compatible, false otherwise
     */
    fun processHandshakeAck(ackMessage: JSONObject): Boolean {
        return try {
            // Validate the message against schema
            if (!schemaManager.validateMessage(ackMessage)) {
                Log.e(TAG, "Invalid handshake acknowledgment format")
                return false
            }
            
            val serverProtocolVersion = ackMessage.getInt("protocol_version")
            val serverName = ackMessage.getString("server_name")
            val serverVersion = ackMessage.getString("server_version")
            val compatible = ackMessage.getBoolean("compatible")
            val message = ackMessage.optString("message", "")
            
            Log.i(TAG, "Received handshake ack from $serverName v$serverVersion")
            Log.i(TAG, "Server protocol version: $serverProtocolVersion")
            Log.i(TAG, "Client protocol version: ${CommonConstants.PROTOCOL_VERSION}")
            
            if (!compatible) {
                Log.w(TAG, "Protocol version mismatch detected!")
                Log.w(TAG, "Server message: $message")
                
                // Log detailed version information for debugging
                if (serverProtocolVersion != CommonConstants.PROTOCOL_VERSION) {
                    Log.w(TAG, "Version mismatch: Android v${CommonConstants.PROTOCOL_VERSION}, Server v$serverProtocolVersion")
                    Log.w(TAG, "Consider updating both applications to the same version")
                }
                
                return false
            }
            
            Log.i(TAG, "Handshake successful - protocol versions compatible")
            if (message.isNotEmpty()) {
                Log.i(TAG, "Server message: $message")
            }
            
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Error processing handshake acknowledgment: ${e.message}", e)
            false
        }
    }
    
    /**
     * Create handshake message with device information.
     * 
     * @return JSONObject containing handshake message
     */
    private fun createHandshakeMessage(): JSONObject {
        return schemaManager.createMessage("handshake").apply {
            put("protocol_version", CommonConstants.PROTOCOL_VERSION)
            put("device_name", getDeviceName())
            put("app_version", CommonConstants.APP_VERSION)
            put("device_type", "android")
        }
    }
    
    /**
     * Get a human-readable device name.
     * 
     * @return Device name string
     */
    private fun getDeviceName(): String {
        return try {
            val manufacturer = android.os.Build.MANUFACTURER
            val model = android.os.Build.MODEL
            "$manufacturer $model"
        } catch (e: Exception) {
            "Android Device"
        }
    }
    
    /**
     * Check if two protocol versions are compatible.
     * 
     * Currently implements exact version matching, but could be extended
     * to support backward compatibility rules in the future.
     * 
     * @param clientVersion Client protocol version
     * @param serverVersion Server protocol version
     * @return true if versions are compatible
     */
    fun areVersionsCompatible(clientVersion: Int, serverVersion: Int): Boolean {
        // For now, require exact version match
        // In the future, this could implement more sophisticated compatibility rules
        return clientVersion == serverVersion
    }
    
    /**
     * Create a handshake acknowledgment message.
     * 
     * This is used when the Android device acts as a server receiving handshakes.
     * 
     * @param clientProtocolVersion Protocol version from client handshake
     * @param compatible Whether the versions are compatible
     * @param message Optional message about compatibility status
     * @return JSONObject containing handshake acknowledgment
     */
    fun createHandshakeAck(clientProtocolVersion: Int, compatible: Boolean, message: String = ""): JSONObject {
        return schemaManager.createMessage("handshake_ack").apply {
            put("protocol_version", CommonConstants.PROTOCOL_VERSION)
            put("server_name", "Android Recording Device")
            put("server_version", CommonConstants.APP_VERSION)
            put("compatible", compatible)
            if (message.isNotEmpty()) {
                put("message", message)
            }
        }
    }
}
