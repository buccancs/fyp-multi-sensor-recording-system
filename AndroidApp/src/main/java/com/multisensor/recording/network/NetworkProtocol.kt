package com.multisensor.recording.network

/**
 * Network protocol definitions for communication between Android app and PC controller.
 * Defines standard commands, responses, and message formats.
 */
object NetworkProtocol {
    
    // Command constants
    object Commands {
        const val START_RECORD = "START_RECORD"
        const val STOP_RECORD = "STOP_RECORD"
        const val PING = "PING"
        const val GET_STATUS = "GET_STATUS"
        const val CALIBRATE = "CALIBRATE"
        const val CONFIGURE = "CONFIGURE"
        const val GET_PREVIEW = "GET_PREVIEW"
        const val HELLO = "HELLO"
    }
    
    // Response constants
    object Responses {
        const val ACK = "ACK"
        const val ERROR = "ERROR"
        const val STATUS = "STATUS"
        const val PONG = "PONG"
        const val HELLO = "HELLO"
        const val PREVIEW_RGB = "PREVIEW_RGB"
        const val PREVIEW_THERMAL = "PREVIEW_THERMAL"
    }
    
    // Status constants
    object Status {
        const val READY = "READY"
        const val RECORDING = "RECORDING"
        const val CALIBRATING = "CALIBRATING"
        const val ERROR = "ERROR"
        const val INITIALIZING = "INITIALIZING"
        const val DISCONNECTED = "DISCONNECTED"
    }
    
    // Error codes
    object ErrorCodes {
        const val UNKNOWN_COMMAND = "UNKNOWN_COMMAND"
        const val INVALID_PARAMETER = "INVALID_PARAMETER"
        const val RECORDING_FAILED = "RECORDING_FAILED"
        const val CAMERA_ERROR = "CAMERA_ERROR"
        const val STORAGE_ERROR = "STORAGE_ERROR"
        const val PERMISSION_DENIED = "PERMISSION_DENIED"
        const val ALREADY_RECORDING = "ALREADY_RECORDING"
        const val NOT_RECORDING = "NOT_RECORDING"
    }
    
    // Message formats
    object MessageFormat {
        const val COMMAND_SEPARATOR = " "
        const val PARAMETER_SEPARATOR = ":"
        const val MESSAGE_TERMINATOR = "\n"
        
        /**
         * Create a command message
         */
        fun createCommand(command: String, parameters: Map<String, String> = emptyMap()): String {
            return if (parameters.isEmpty()) {
                command
            } else {
                val paramString = parameters.entries.joinToString(COMMAND_SEPARATOR) { "${it.key}${PARAMETER_SEPARATOR}${it.value}" }
                "$command$COMMAND_SEPARATOR$paramString"
            }
        }
        
        /**
         * Create a response message
         */
        fun createResponse(response: String, data: String = ""): String {
            return if (data.isEmpty()) {
                response
            } else {
                "$response$COMMAND_SEPARATOR$data"
            }
        }
        
        /**
         * Create an acknowledgment message
         */
        fun createAck(operation: String): String {
            return createResponse(Responses.ACK, operation)
        }
        
        /**
         * Create an error message
         */
        fun createError(errorCode: String, details: String = ""): String {
            return if (details.isEmpty()) {
                createResponse(Responses.ERROR, errorCode)
            } else {
                createResponse(Responses.ERROR, "$errorCode$PARAMETER_SEPARATOR$details")
            }
        }
        
        /**
         * Create a status message
         */
        fun createStatus(status: String, details: String = ""): String {
            return if (details.isEmpty()) {
                createResponse(Responses.STATUS, status)
            } else {
                createResponse(Responses.STATUS, "$status$PARAMETER_SEPARATOR$details")
            }
        }
        
        /**
         * Parse a command message
         */
        fun parseCommand(message: String): ParsedCommand {
            val parts = message.trim().split(COMMAND_SEPARATOR)
            val command = parts.firstOrNull()?.uppercase() ?: ""
            
            val parameters = mutableMapOf<String, String>()
            for (i in 1 until parts.size) {
                val paramParts = parts[i].split(PARAMETER_SEPARATOR, limit = 2)
                if (paramParts.size == 2) {
                    parameters[paramParts[0]] = paramParts[1]
                }
            }
            
            return ParsedCommand(command, parameters)
        }
        
        /**
         * Parse a response message
         */
        fun parseResponse(message: String): ParsedResponse {
            val parts = message.trim().split(COMMAND_SEPARATOR, limit = 2)
            val response = parts.firstOrNull()?.uppercase() ?: ""
            val data = if (parts.size > 1) parts[1] else ""
            
            return ParsedResponse(response, data)
        }
    }
    
    // Data classes for parsed messages
    data class ParsedCommand(
        val command: String,
        val parameters: Map<String, String>
    )
    
    data class ParsedResponse(
        val response: String,
        val data: String
    )
    
    // Configuration parameters
    object ConfigParams {
        const val SERVER_IP = "server_ip"
        const val SERVER_PORT = "server_port"
        const val PREVIEW_FPS = "preview_fps"
        const val PREVIEW_QUALITY = "preview_quality"
        const val PREVIEW_WIDTH = "preview_width"
        const val PREVIEW_HEIGHT = "preview_height"
        const val SESSION_ID = "session_id"
        const val DEVICE_ID = "device_id"
    }
    
    // Default configuration values
    object Defaults {
        const val SERVER_IP = "192.168.1.100"
        const val SERVER_PORT = 8080
        const val PREVIEW_FPS = 2
        const val PREVIEW_QUALITY = 70
        const val PREVIEW_WIDTH = 640
        const val PREVIEW_HEIGHT = 480
        const val CONNECTION_TIMEOUT_MS = 10000
        const val RECONNECT_DELAY_MS = 5000L
    }
    
    // Message validation
    object Validation {
        private val VALID_COMMANDS = setOf(
            Commands.START_RECORD,
            Commands.STOP_RECORD,
            Commands.PING,
            Commands.GET_STATUS,
            Commands.CALIBRATE,
            Commands.CONFIGURE,
            Commands.GET_PREVIEW,
            Commands.HELLO
        )
        
        private val VALID_RESPONSES = setOf(
            Responses.ACK,
            Responses.ERROR,
            Responses.STATUS,
            Responses.PONG,
            Responses.HELLO,
            Responses.PREVIEW_RGB,
            Responses.PREVIEW_THERMAL
        )
        
        /**
         * Validate if a command is supported
         */
        fun isValidCommand(command: String): Boolean {
            return VALID_COMMANDS.contains(command.uppercase())
        }
        
        /**
         * Validate if a response is supported
         */
        fun isValidResponse(response: String): Boolean {
            return VALID_RESPONSES.contains(response.uppercase())
        }
        
        /**
         * Validate message format
         */
        fun isValidMessage(message: String): Boolean {
            return message.isNotBlank() && message.length <= 8192 // Max message size
        }
    }
    
    // Protocol version
    const val PROTOCOL_VERSION = "1.0"
    
    // Client identification
    object ClientInfo {
        const val CLIENT_TYPE = "ANDROID_CLIENT"
        const val CLIENT_VERSION = "1.0.0"
        
        fun createHelloMessage(deviceId: String = "unknown"): String {
            return MessageFormat.createCommand(
                Commands.HELLO,
                mapOf(
                    "client_type" to CLIENT_TYPE,
                    "client_version" to CLIENT_VERSION,
                    "protocol_version" to PROTOCOL_VERSION,
                    "device_id" to deviceId
                )
            )
        }
    }
}