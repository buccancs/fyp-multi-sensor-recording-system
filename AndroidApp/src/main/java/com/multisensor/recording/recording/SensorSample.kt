package com.multisensor.recording.recording

import com.multisensor.recording.recording.DeviceConfiguration.SensorChannel
import java.text.SimpleDateFormat
import java.util.*

/**
 * Represents a single sensor sample from a Shimmer3 GSR+ device.
 *
 * This data class encapsulates all sensor readings from a single timestamp,
 * including device timing information and calibrated sensor values.
 */
data class SensorSample(
    val deviceId: String,
    val deviceTimestamp: Long, // Device's internal timestamp (ms)
    val systemTimestamp: Long = System.currentTimeMillis(), // Android system timestamp (ms)
    val sessionTimestamp: Long = 0L, // Session-relative timestamp (ms)
    val sensorValues: Map<SensorChannel, Double> = emptyMap(),
    val batteryLevel: Int = 0,
    val sequenceNumber: Long = 0L,
) {
    companion object {
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault())

        /**
         * Create a sample with GSR, PPG, and Accelerometer data (typical Shimmer3 GSR+ configuration)
         */
        fun createGSRPlusSample(
            deviceId: String,
            deviceTimestamp: Long,
            gsrConductance: Double,
            ppgValue: Double,
            accelX: Double,
            accelY: Double,
            accelZ: Double,
            batteryLevel: Int = 0,
            sequenceNumber: Long = 0L,
        ): SensorSample {
            val sensorValues =
                mapOf(
                    SensorChannel.GSR to gsrConductance,
                    SensorChannel.PPG to ppgValue,
                    SensorChannel.ACCEL to accelX, // Note: This simplifies 3-axis accel to single value
                    // In real implementation, I might need separate channels for X, Y, Z
                )

            return SensorSample(
                deviceId = deviceId,
                deviceTimestamp = deviceTimestamp,
                sensorValues = sensorValues,
                batteryLevel = batteryLevel,
                sequenceNumber = sequenceNumber,
            )
        }

        /**
         * Create a sample with all available sensor channels
         */
        fun createFullSample(
            deviceId: String,
            deviceTimestamp: Long,
            gsrConductance: Double,
            ppgValue: Double,
            accelX: Double,
            accelY: Double,
            accelZ: Double,
            gyroX: Double,
            gyroY: Double,
            gyroZ: Double,
            magX: Double,
            magY: Double,
            magZ: Double,
            batteryLevel: Int = 0,
            sequenceNumber: Long = 0L,
        ): SensorSample {
            val sensorValues =
                mapOf(
                    SensorChannel.GSR to gsrConductance,
                    SensorChannel.PPG to ppgValue,
                    SensorChannel.ACCEL to accelX, // Simplified - in real implementation might need separate channels
                    SensorChannel.GYRO to gyroX, // Simplified - in real implementation might need separate channels
                    SensorChannel.MAG to magX, // Simplified - in real implementation might need separate channels
                )

            return SensorSample(
                deviceId = deviceId,
                deviceTimestamp = deviceTimestamp,
                sensorValues = sensorValues,
                batteryLevel = batteryLevel,
                sequenceNumber = sequenceNumber,
            )
        }

        /**
         * Create a simulated sample for testing purposes
         */
        fun createSimulatedSample(
            deviceId: String,
            sequenceNumber: Long,
            enabledSensors: Set<SensorChannel> = setOf(SensorChannel.GSR, SensorChannel.PPG, SensorChannel.ACCEL),
        ): SensorSample {
            val currentTime = System.currentTimeMillis()
            val sensorValues = mutableMapOf<SensorChannel, Double>()

            // Generate realistic simulated values
            enabledSensors.forEach { sensor ->
                val value =
                    when (sensor) {
                        SensorChannel.GSR -> 2.0 + Math.sin(sequenceNumber * 0.1) * 0.5 // 1.5-2.5 µS
                        SensorChannel.PPG -> 512.0 + Math.sin(sequenceNumber * 0.2) * 100.0 // Heart rate simulation
                        SensorChannel.ACCEL -> if (sequenceNumber % 3 == 0L) 9.8 else 0.1 // Gravity + small movements
                        SensorChannel.GYRO -> Math.sin(sequenceNumber * 0.05) * 10.0 // Small rotations
                        SensorChannel.MAG -> 25.0 + Math.sin(sequenceNumber * 0.03) * 5.0 // Magnetic field
                        SensorChannel.ECG -> Math.sin(sequenceNumber * 0.3) * 0.5 // ECG simulation
                        SensorChannel.EMG -> Math.random() * 0.1 // EMG noise
                        else -> 0.0 // Default value for other sensors
                    }
                sensorValues[sensor] = value
            }

            return SensorSample(
                deviceId = deviceId,
                deviceTimestamp = currentTime,
                sensorValues = sensorValues,
                batteryLevel = (80 + (sequenceNumber % 20)).toInt(), // Simulate battery 80-99%
                sequenceNumber = sequenceNumber,
            )
        }
    }

    /**
     * Get sensor value for a specific channel
     */
    fun getSensorValue(channel: SensorChannel): Double? = sensorValues[channel]

    /**
     * Check if a sensor channel has data in this sample
     */
    fun hasSensorData(channel: SensorChannel): Boolean = channel in sensorValues

    /**
     * Get all available sensor channels in this sample
     */
    fun getAvailableChannels(): Set<SensorChannel> = sensorValues.keys

    /**
     * Get the number of sensor channels with data
     */
    fun getChannelCount(): Int = sensorValues.size

    /**
     * Convert to CSV format string with enhanced sensor support
     */
    fun toCsvString(includeHeader: Boolean = false): String {
        val header =
            if (includeHeader) {
                "Timestamp_ms,DeviceTime_ms,SystemTime_ms,SessionTime_ms,DeviceId,SequenceNumber," +
                    "GSR_Conductance_uS,PPG_A13," +
                    "Accel_X_g,Accel_Y_g,Accel_Z_g," +
                    "Gyro_X_dps,Gyro_Y_dps,Gyro_Z_dps," +
                    "Mag_X_gauss,Mag_Y_gauss,Mag_Z_gauss," +
                    "ECG_mV,EMG_mV,Battery_Percentage\n"
            } else {
                ""
            }

        val values =
            listOf(
                systemTimestamp,
                deviceTimestamp,
                systemTimestamp,
                sessionTimestamp,
                deviceId,
                sequenceNumber,
                getSensorValue(SensorChannel.GSR) ?: 0.0,
                getSensorValue(SensorChannel.PPG) ?: 0.0,
                getSensorValue(SensorChannel.ACCEL_X) ?: getSensorValue(SensorChannel.ACCEL) ?: 0.0,
                getSensorValue(SensorChannel.ACCEL_Y) ?: 0.0,
                getSensorValue(SensorChannel.ACCEL_Z) ?: 0.0,
                getSensorValue(SensorChannel.GYRO_X) ?: getSensorValue(SensorChannel.GYRO) ?: 0.0,
                getSensorValue(SensorChannel.GYRO_Y) ?: 0.0,
                getSensorValue(SensorChannel.GYRO_Z) ?: 0.0,
                getSensorValue(SensorChannel.MAG_X) ?: getSensorValue(SensorChannel.MAG) ?: 0.0,
                getSensorValue(SensorChannel.MAG_Y) ?: 0.0,
                getSensorValue(SensorChannel.MAG_Z) ?: 0.0,
                getSensorValue(SensorChannel.ECG) ?: 0.0,
                getSensorValue(SensorChannel.EMG) ?: 0.0,
                batteryLevel,
            ).joinToString(",")

        return header + values
    }

    /**
     * Convert to JSON format string for network streaming
     */
    fun toJsonString(): String {
        val sensorData =
            sensorValues.entries.joinToString(",") { (channel, value) ->
                "\"${channel.name}\":$value"
            }

        return """{
            "deviceId":"$deviceId",
            "deviceTimestamp":$deviceTimestamp,
            "systemTimestamp":$systemTimestamp,
            "sessionTimestamp":$sessionTimestamp,
            "sequenceNumber":$sequenceNumber,
            "batteryLevel":$batteryLevel,
            "sensorData":{$sensorData}
        }""".replace("\n", "").replace("  ", "")
    }

    /**
     * Get a human-readable timestamp
     */
    fun getFormattedTimestamp(): String = dateFormat.format(Date(systemTimestamp))

    /**
     * Calculate time difference from another sample (in milliseconds)
     */
    fun getTimeDifference(other: SensorSample): Long = Math.abs(this.systemTimestamp - other.systemTimestamp)

    /**
     * Check if this sample is within a time window of another sample
     */
    fun isWithinTimeWindow(
        other: SensorSample,
        windowMs: Long,
    ): Boolean = getTimeDifference(other) <= windowMs

    /**
     * Create a copy with updated session timestamp
     */
    fun withSessionTimestamp(sessionStart: Long): SensorSample = copy(sessionTimestamp = systemTimestamp - sessionStart)

    /**
     * Validate sample data
     */
    fun validate(): List<String> {
        val errors = mutableListOf<String>()

        if (deviceId.isBlank()) {
            errors.add("Device ID cannot be blank")
        }

        if (deviceTimestamp <= 0) {
            errors.add("Device timestamp must be positive")
        }

        if (systemTimestamp <= 0) {
            errors.add("System timestamp must be positive")
        }

        if (sensorValues.isEmpty()) {
            errors.add("Sample must contain at least one sensor value")
        }

        if (batteryLevel < 0 || batteryLevel > 100) {
            errors.add("Battery level must be between 0 and 100")
        }

        // Validate sensor value ranges
        sensorValues.forEach { (channel, value) ->
            when (channel) {
                SensorChannel.GSR -> {
                    if (value < 0 || value > 100) {
                        errors.add("GSR value out of range: $value µS")
                    }
                }
                SensorChannel.PPG -> {
                    if (value < 0 || value > 4096) {
                        errors.add("PPG value out of range: $value")
                    }
                }
                SensorChannel.ACCEL -> {
                    if (Math.abs(value) > 50) {
                        errors.add("Accelerometer value out of range: $value g")
                    }
                }
                else -> {
                    // Other sensors - basic range check
                    if (!value.isFinite()) {
                        errors.add("${channel.name} value is not finite: $value")
                    }
                }
            }
        }

        return errors
    }

    override fun toString(): String {
        val sensorSummary =
            sensorValues.entries.take(3).joinToString(", ") { (channel, value) ->
                "${channel.name}=%.2f".format(value)
            }
        return "SensorSample($deviceId, seq=$sequenceNumber, ${getFormattedTimestamp()}, [$sensorSummary], bat=$batteryLevel%)"
    }
}
