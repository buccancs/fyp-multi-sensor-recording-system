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
                    "flash_sync" -> FlashSyncCommand.fromJson(jsonObject)
                    "beep_sync" -> BeepSyncCommand.fromJson(jsonObject)
                    "sync_time" -> SyncTimeCommand.fromJson(jsonObject)
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
 * Command to capture calibration images - Enhanced for Milestone 2.8
 */
data class CaptureCalibrationCommand(
    override val type: String = "capture_calibration",
    val calibration_id: String? = null,
    val capture_rgb: Boolean = true,
    val capture_thermal: Boolean = true,
    val high_resolution: Boolean = true
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            calibration_id?.let { put("calibration_id", it) }
            put("capture_rgb", capture_rgb)
            put("capture_thermal", capture_thermal)
            put("high_resolution", high_resolution)
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): CaptureCalibrationCommand {
            return CaptureCalibrationCommand(
                calibration_id = if (json.has("calibration_id")) json.getString("calibration_id") else null,
                capture_rgb = json.optBoolean("capture_rgb", true),
                capture_thermal = json.optBoolean("capture_thermal", true),
                high_resolution = json.optBoolean("high_resolution", true)
            )
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

/**
 * Command to trigger LED flash sync signal - Milestone 2.8
 */
data class FlashSyncCommand(
    override val type: String = "flash_sync",
    val duration_ms: Long = 200,
    val sync_id: String? = null
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("duration_ms", duration_ms)
            sync_id?.let { put("sync_id", it) }
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): FlashSyncCommand {
            return FlashSyncCommand(
                duration_ms = json.optLong("duration_ms", 200),
                sync_id = if (json.has("sync_id")) json.getString("sync_id") else null
            )
        }
    }
}

/**
 * Command to trigger audio beep sync signal - Milestone 2.8
 */
data class BeepSyncCommand(
    override val type: String = "beep_sync",
    val frequency_hz: Int = 1000,
    val duration_ms: Long = 200,
    val volume: Float = 0.8f,
    val sync_id: String? = null
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("frequency_hz", frequency_hz)
            put("duration_ms", duration_ms)
            put("volume", volume.toDouble())
            sync_id?.let { put("sync_id", it) }
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): BeepSyncCommand {
            return BeepSyncCommand(
                frequency_hz = json.optInt("frequency_hz", 1000),
                duration_ms = json.optLong("duration_ms", 200),
                volume = json.optDouble("volume", 0.8).toFloat(),
                sync_id = if (json.has("sync_id")) json.getString("sync_id") else null
            )
        }
    }
}

/**
 * Command to synchronize device clock with PC reference time - Milestone 2.8
 */
data class SyncTimeCommand(
    override val type: String = "sync_time",
    val pc_timestamp: Long,
    val sync_id: String? = null
) : JsonMessage() {
    
    override fun toJsonObject(): JSONObject {
        return JSONObject().apply {
            put("type", type)
            put("pc_timestamp", pc_timestamp)
            sync_id?.let { put("sync_id", it) }
        }
    }
    
    companion object {
        fun fromJson(json: JSONObject): SyncTimeCommand {
            return SyncTimeCommand(
                pc_timestamp = json.getLong("pc_timestamp"),
                sync_id = if (json.has("sync_id")) json.getString("sync_id") else null
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
