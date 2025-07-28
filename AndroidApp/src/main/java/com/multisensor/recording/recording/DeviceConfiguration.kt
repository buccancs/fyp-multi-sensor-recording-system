package com.multisensor.recording.recording

/**
 * Configuration settings for a Shimmer3 GSR+ device.
 * 
 * This data class encapsulates all configurable parameters for a Shimmer device
 * including sensor channels, sampling rates, and hardware-specific settings.
 */
data class DeviceConfiguration(
    val samplingRate: Double = DEFAULT_SAMPLING_RATE,
    val enabledSensors: Set<SensorChannel> = setOf(SensorChannel.GSR, SensorChannel.PPG),
    val gsrRange: Int = DEFAULT_GSR_RANGE,
    val accelRange: Int = DEFAULT_ACCEL_RANGE,
    val gyroRange: Int = DEFAULT_GYRO_RANGE,
    val magRange: Int = DEFAULT_MAG_RANGE,
    val enableLowPowerMode: Boolean = false,
    val enableAutoCalibration: Boolean = true,
    val bufferSize: Int = DEFAULT_BUFFER_SIZE
) {
    
    companion object {
        // Default configuration values matching Shimmer3 GSR+ specifications
        const val DEFAULT_SAMPLING_RATE = 51.2 // Hz
        const val DEFAULT_GSR_RANGE = 4 // GSR range setting (4.7kΩ)
        const val DEFAULT_ACCEL_RANGE = 2 // ±2g
        const val DEFAULT_GYRO_RANGE = 250 // ±250°/s
        const val DEFAULT_MAG_RANGE = 1 // ±1.3 Gauss
        const val DEFAULT_BUFFER_SIZE = 100 // Number of samples to buffer
        
        // Shimmer sensor bitmask constants (matching Shimmer SDK)
        const val SENSOR_GSR = 0x04
        const val SENSOR_PPG = 0x4000
        const val SENSOR_ACCEL = 0x80
        const val SENSOR_GYRO = 0x40
        const val SENSOR_MAG = 0x20
        const val SENSOR_ECG = 0x10
        const val SENSOR_EMG = 0x08
        
        /**
         * Create a default configuration for Shimmer3 GSR+
         */
        fun createDefault(): DeviceConfiguration {
            return DeviceConfiguration(
                samplingRate = DEFAULT_SAMPLING_RATE,
                enabledSensors = setOf(SensorChannel.GSR, SensorChannel.PPG, SensorChannel.ACCEL),
                gsrRange = DEFAULT_GSR_RANGE,
                accelRange = DEFAULT_ACCEL_RANGE
            )
        }
        
        /**
         * Create a high-performance configuration with all sensors enabled
         */
        fun createHighPerformance(): DeviceConfiguration {
            return DeviceConfiguration(
                samplingRate = 128.0,
                enabledSensors = SensorChannel.values().toSet(),
                gsrRange = DEFAULT_GSR_RANGE,
                accelRange = DEFAULT_ACCEL_RANGE,
                enableAutoCalibration = true,
                bufferSize = 200
            )
        }
        
        /**
         * Create a low-power configuration with minimal sensors
         */
        fun createLowPower(): DeviceConfiguration {
            return DeviceConfiguration(
                samplingRate = 25.6,
                enabledSensors = setOf(SensorChannel.GSR),
                enableLowPowerMode = true,
                bufferSize = 50
            )
        }
    }
    
    /**
     * Available sensor channels on Shimmer3 GSR+
     */
    enum class SensorChannel(val displayName: String, val bitmask: Int) {
        GSR("GSR (Skin Conductance)", SENSOR_GSR),
        PPG("PPG (Heart Rate)", SENSOR_PPG),
        ACCEL("Accelerometer", SENSOR_ACCEL),
        GYRO("Gyroscope", SENSOR_GYRO),
        MAG("Magnetometer", SENSOR_MAG),
        ECG("ECG", SENSOR_ECG),
        EMG("EMG", SENSOR_EMG);
        
        companion object {
            /**
             * Get sensor channels that are typically available on Shimmer3 GSR+
             */
            fun getGSRPlusChannels(): Set<SensorChannel> {
                return setOf(GSR, PPG, ACCEL, GYRO, MAG)
            }
        }
    }
    
    /**
     * Calculate the sensor bitmask for enabled sensors
     */
    fun getSensorBitmask(): Int {
        return enabledSensors.fold(0) { acc, sensor -> acc or sensor.bitmask }
    }
    
    /**
     * Get the number of enabled sensor channels
     */
    fun getEnabledChannelCount(): Int {
        return enabledSensors.size
    }
    
    /**
     * Check if a specific sensor is enabled
     */
    fun isSensorEnabled(sensor: SensorChannel): Boolean {
        return sensor in enabledSensors
    }
    
    /**
     * Get estimated data rate in samples per second
     */
    fun getEstimatedDataRate(): Double {
        return samplingRate * getEnabledChannelCount()
    }
    
    /**
     * Get estimated bandwidth in bytes per second (rough calculation)
     */
    fun getEstimatedBandwidth(): Int {
        // Each sample is roughly 8 bytes (timestamp + value), plus overhead
        return (getEstimatedDataRate() * 10).toInt()
    }
    
    /**
     * Validate configuration parameters
     */
    fun validate(): List<String> {
        val errors = mutableListOf<String>()
        
        if (samplingRate <= 0 || samplingRate > 1000) {
            errors.add("Sampling rate must be between 0 and 1000 Hz")
        }
        
        if (enabledSensors.isEmpty()) {
            errors.add("At least one sensor must be enabled")
        }
        
        if (gsrRange !in 1..8) {
            errors.add("GSR range must be between 1 and 8")
        }
        
        if (accelRange !in listOf(2, 4, 8, 16)) {
            errors.add("Accelerometer range must be 2, 4, 8, or 16g")
        }
        
        if (bufferSize <= 0 || bufferSize > 1000) {
            errors.add("Buffer size must be between 1 and 1000")
        }
        
        return errors
    }
    
    /**
     * Create a copy with modified sensor channels
     */
    fun withSensors(sensors: Set<SensorChannel>): DeviceConfiguration {
        return copy(enabledSensors = sensors)
    }
    
    /**
     * Create a copy with modified sampling rate
     */
    fun withSamplingRate(rate: Double): DeviceConfiguration {
        return copy(samplingRate = rate)
    }
    
    override fun toString(): String {
        return "DeviceConfiguration(rate=${samplingRate}Hz, sensors=${enabledSensors.size}, " +
                "channels=[${enabledSensors.joinToString { it.displayName }}])"
    }
}