package com.multisensor.recording.network

import org.json.JSONException
import org.json.JSONObject

/**
 * JSON message protocol for Milestone 2.6 Network Communication Client.
 * Defines message types and structures for bidirectional communication between Android and PC.
 * 
 * Based on 2_6_milestone.md specifications for JSON socket communication.
 */

/**
 * Base class for all JSON messages with common type field
 */
abstract class JsonMessage {
    abstract val type: String
    
    companion object {
        /**
         * Parse incoming JSON message and return appropriate message object
         */
        fun fromJson(jsonString: String): JsonMessage? {
            return try {
                val jsonObject = JSONObject(jsonString)
                val messageType = jsonObject.getString("type")
                
                // Parse to specific message type based on type field
                when (messageType) {
                    "start_record" -> StartRecordCommand.fromJson(jsonObject)
                    "stop_record" -> StopRecordCommand.fromJson(jsonObject)
                    "capture_calibration" -> CaptureCalibrationCommand.fromJson(jsonObject)
                    "set_stimulus_time" -> SetStimulusTimeCommand.fromJson(jsonObject)
                    "hello" -> HelloMessage.fromJson(jsonObject)
                    "preview_frame" -> PreviewFrameMessage.fromJson(jsonObject)
                    "sensor_data" -> SensorDataMessage.fromJson(jsonObject)
                    "status" -> StatusMessage.fromJson(jsonObject)
                    "ack" -> AckMessage.fromJson(jsonObject)
                    else -> null // Unknown message type
                }
            } catch (e: JSONException) {
                null // Invalid JSON
            }
        }
        
        /**
         * Convert message object to JSON string
         */
        fun toJson(message: JsonMessage): String {
            return message.toJsonObject().toString()
        }
    }
    
    /**
     * Convert message to JSONObject - to be implemented by subclasses
     */
    abstract fun toJsonObject(): JSONObject
}

// ========== PC-to-Phone Command Messages ==========

/**
 * Command to start recording session
 */
data class StartRecordCommand(
    override val type: String = "start_record",
    val session_id: String,
    val record_video: Boolean = true,
    val record_thermal: Boolean = true,
    val record_shimmer: Boolean = false
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("session_id", session_id)
            put("record_video", record_video)
            put("record_thermal", record_thermal)
            put("record_shimmer", record_shimmer)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): StartRecordCommand {
            return StartRecordCommand(
                session_id = json.getString("session_id"),
                record_video = json.optBoolean("record_video", true),
                record_thermal = json.optBoolean("record_thermal", true),
                record_shimmer = json.optBoolean("record_shimmer", false)
            )
        }
    }
}

/**
 * Command to stop current recording session
 */
data class StopRecordCommand(
    override val type: String = "stop_record"
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): StopRecordCommand {
            return StopRecordCommand()
        }
    }
}

/**
 * Command to capture calibration images
 */
data class CaptureCalibrationCommand(
    override val type: String = "capture_calibration"
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): CaptureCalibrationCommand {
            return CaptureCalibrationCommand()
        }
    }
}

/**
 * Command to set stimulus time for synchronization
 */
data class SetStimulusTimeCommand(
    override val type: String = "set_stimulus_time",
    val time: Long
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("time", time)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): SetStimulusTimeCommand {
            return SetStimulusTimeCommand(
                time = json.getLong("time")
            )
        }
    }
}

// ========== Phone-to-PC Messages ==========

/**
 * Device introduction message sent on connection
 */
data class HelloMessage(
    override val type: String = "hello",
    val device_id: String,
    val capabilities: List<String>
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("device_id", device_id)
            put("capabilities", org.json.JSONArray(capabilities))
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): HelloMessage {
            val capabilitiesArray = json.getJSONArray("capabilities")
            val capabilities = mutableListOf<String>()
            for (i in 0 until capabilitiesArray.length()) {
                capabilities.add(capabilitiesArray.getString(i))
            }
            return HelloMessage(
                device_id = json.getString("device_id"),
                capabilities = capabilities
            )
        }
    }
}

/**
 * Live preview frame message
 */
data class PreviewFrameMessage(
    override val type: String = "preview_frame",
    val cam: String, // "rgb" or "thermal"
    val timestamp: Long,
    val image: String // base64 encoded image data
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("cam", cam)
            put("timestamp", timestamp)
            put("image", image)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): PreviewFrameMessage {
            return PreviewFrameMessage(
                cam = json.getString("cam"),
                timestamp = json.getLong("timestamp"),
                image = json.getString("image")
            )
        }
    }
}

/**
 * Sensor data update message
 */
data class SensorDataMessage(
    override val type: String = "sensor_data",
    val timestamp: Long,
    val values: Map<String, Double>
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("timestamp", timestamp)
            val valuesJson = JSONObject()
            values.forEach { (key, value) ->
                valuesJson.put(key, value)
            }
            put("values", valuesJson)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): SensorDataMessage {
            val valuesJson = json.getJSONObject("values")
            val values = mutableMapOf<String, Double>()
            val keys = valuesJson.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                values[key] = valuesJson.getDouble(key)
            }
            return SensorDataMessage(
                timestamp = json.getLong("timestamp"),
                values = values
            )
        }
    }
}

/**
 * Device status update message
 */
data class StatusMessage(
    override val type: String = "status",
    val battery: Int? = null,
    val storage: String? = null,
    val temperature: Double? = null,
    val recording: Boolean = false,
    val connected: Boolean = true
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            battery?.let { put("battery", it) }
            storage?.let { put("storage", it) }
            temperature?.let { put("temperature", it) }
            put("recording", recording)
            put("connected", connected)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): StatusMessage {
            return StatusMessage(
                battery = if (json.has("battery")) json.getInt("battery") else null,
                storage = if (json.has("storage")) json.getString("storage") else null,
                temperature = if (json.has("temperature")) json.getDouble("temperature") else null,
                recording = json.optBoolean("recording", false),
                connected = json.optBoolean("connected", true)
            )
        }
    }
}

/**
 * Acknowledgment/response message
 */
data class AckMessage(
    override val type: String = "ack",
    val cmd: String,
    val status: String, // "ok" or "error"
    val message: String? = null
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("cmd", cmd)
            put("status", status)
            message?.let { put("message", it) }
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): AckMessage {
            return AckMessage(
                cmd = json.getString("cmd"),
                status = json.getString("status"),
                message = if (json.has("message")) json.getString("message") else null
            )
        }
    }
}
