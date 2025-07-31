package com.multisensor.recording.recording

import com.multisensor.recording.util.Logger
import com.shimmerresearch.driver.ObjectCluster
import com.shimmerresearch.driver.Configuration
import kotlinx.coroutines.*

/**
 * Comprehensive data schema validator for Shimmer3 GSR+ devices.
 * 
 * This class ensures rock-solid preparation for Shimmer device data schemas by:
 * - Validating incoming ObjectCluster data structures
 * - Ensuring data type compatibility
 * - Checking sensor data ranges and validity
 * - Providing schema documentation and mapping
 * - Handling version compatibility
 * - Real-time data validation
 */
class DataSchemaValidator(
    private val logger: Logger
) {
    
    /**
     * Schema definition for a sensor channel
     */
    data class SensorChannelSchema(
        val name: String,
        val displayName: String,
        val dataType: DataType,
        val unit: String,
        val validRange: DoubleRange,
        val precision: Int,
        val isRequired: Boolean = false,
        val calibrationRequired: Boolean = false
    )
    
    /**
     * Data types supported by Shimmer devices
     */
    enum class DataType {
        DOUBLE,
        FLOAT,
        LONG,
        INT,
        BOOLEAN,
        STRING,
        BYTE_ARRAY
    }
    
    /**
     * Schema validation result
     */
    data class ValidationResult(
        val isValid: Boolean,
        val errors: List<String> = emptyList(),
        val warnings: List<String> = emptyList(),
        val validatedChannels: Set<String> = emptySet(),
        val missingChannels: Set<String> = emptySet(),
        val extraChannels: Set<String> = emptySet()
    )
    
    /**
     * Device schema configuration
     */
    data class DeviceSchema(
        val deviceType: String,
        val firmwareVersion: String,
        val supportedChannels: Map<String, SensorChannelSchema>,
        val requiredChannels: Set<String>,
        val samplingRateRange: DoubleRange,
        val maxChannelsSimultaneous: Int,
        val dataFormat: String
    ) {
        companion object {
            /**
             * Create comprehensive schema for Shimmer3 GSR+
             */
            fun createShimmer3GSRPlusSchema(): DeviceSchema = DeviceSchema(
                deviceType = "Shimmer3-GSR+",
                firmwareVersion = "3.2.3",
                supportedChannels = mapOf(
                    // GSR Sensor
                    "GSR_CONDUCTANCE" to SensorChannelSchema(
                        name = "GSR_CONDUCTANCE",
                        displayName = "GSR Conductance",
                        dataType = DataType.DOUBLE,
                        unit = "µS",
                        validRange = 0.0..100.0,
                        precision = 3,
                        isRequired = true,
                        calibrationRequired = true
                    ),
                    
                    // PPG Sensor
                    "PPG_A13" to SensorChannelSchema(
                        name = "INT_EXP_ADC_A13",
                        displayName = "PPG (A13)",
                        dataType = DataType.DOUBLE,
                        unit = "mV",
                        validRange = 0.0..3300.0,
                        precision = 2,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    
                    // 3-Axis Accelerometer
                    "ACCEL_X" to SensorChannelSchema(
                        name = "ACCEL_LN_X",
                        displayName = "Accelerometer X",
                        dataType = DataType.DOUBLE,
                        unit = "g",
                        validRange = -16.0..16.0,
                        precision = 4,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "ACCEL_Y" to SensorChannelSchema(
                        name = "ACCEL_LN_Y",
                        displayName = "Accelerometer Y",
                        dataType = DataType.DOUBLE,
                        unit = "g",
                        validRange = -16.0..16.0,
                        precision = 4,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "ACCEL_Z" to SensorChannelSchema(
                        name = "ACCEL_LN_Z",
                        displayName = "Accelerometer Z",
                        dataType = DataType.DOUBLE,
                        unit = "g",
                        validRange = -16.0..16.0,
                        precision = 4,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    
                    // 3-Axis Gyroscope
                    "GYRO_X" to SensorChannelSchema(
                        name = "GYRO_X",
                        displayName = "Gyroscope X",
                        dataType = DataType.DOUBLE,
                        unit = "°/s",
                        validRange = -2000.0..2000.0,
                        precision = 3,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "GYRO_Y" to SensorChannelSchema(
                        name = "GYRO_Y",
                        displayName = "Gyroscope Y",
                        dataType = DataType.DOUBLE,
                        unit = "°/s",
                        validRange = -2000.0..2000.0,
                        precision = 3,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "GYRO_Z" to SensorChannelSchema(
                        name = "GYRO_Z",
                        displayName = "Gyroscope Z",
                        dataType = DataType.DOUBLE,
                        unit = "°/s",
                        validRange = -2000.0..2000.0,
                        precision = 3,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    
                    // 3-Axis Magnetometer
                    "MAG_X" to SensorChannelSchema(
                        name = "MAG_X",
                        displayName = "Magnetometer X",
                        dataType = DataType.DOUBLE,
                        unit = "gauss",
                        validRange = -8.0..8.0,
                        precision = 4,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "MAG_Y" to SensorChannelSchema(
                        name = "MAG_Y",
                        displayName = "Magnetometer Y",
                        dataType = DataType.DOUBLE,
                        unit = "gauss",
                        validRange = -8.0..8.0,
                        precision = 4,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "MAG_Z" to SensorChannelSchema(
                        name = "MAG_Z",
                        displayName = "Magnetometer Z",
                        dataType = DataType.DOUBLE,
                        unit = "gauss",
                        validRange = -8.0..8.0,
                        precision = 4,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    
                    // EXG Sensors (ECG/EMG)
                    "ECG_LL_RA" to SensorChannelSchema(
                        name = "ECG_LL_RA",
                        displayName = "ECG (LL-RA)",
                        dataType = DataType.DOUBLE,
                        unit = "mV",
                        validRange = -1650.0..1650.0,
                        precision = 3,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    "EMG" to SensorChannelSchema(
                        name = "EMG",
                        displayName = "EMG",
                        dataType = DataType.DOUBLE,
                        unit = "mV",
                        validRange = -1650.0..1650.0,
                        precision = 3,
                        isRequired = false,
                        calibrationRequired = true
                    ),
                    
                    // System channels
                    "TIMESTAMP" to SensorChannelSchema(
                        name = "TIMESTAMP",
                        displayName = "Timestamp",
                        dataType = DataType.LONG,
                        unit = "ms",
                        validRange = 0.0..Double.MAX_VALUE,
                        precision = 0,
                        isRequired = true,
                        calibrationRequired = false
                    ),
                    "BATTERY" to SensorChannelSchema(
                        name = "BATTERY",
                        displayName = "Battery Voltage",
                        dataType = DataType.DOUBLE,
                        unit = "V",
                        validRange = 2.5..4.2,
                        precision = 3,
                        isRequired = false,
                        calibrationRequired = true
                    )
                ),
                requiredChannels = setOf("GSR_CONDUCTANCE", "TIMESTAMP"),
                samplingRateRange = 1.0..1000.0,
                maxChannelsSimultaneous = 15,
                dataFormat = "ObjectCluster"
            )
        }
    }
    
    // Schema registry
    private val deviceSchemas = mutableMapOf<String, DeviceSchema>()
    private val validationCache = mutableMapOf<String, ValidationResult>()
    
    init {
        // Register default schemas
        registerDeviceSchema(DeviceSchema.createShimmer3GSRPlusSchema())
    }
    
    /**
     * Register a device schema
     */
    fun registerDeviceSchema(schema: DeviceSchema) {
        deviceSchemas[schema.deviceType] = schema
        logger.info("Registered schema for device type: ${schema.deviceType}")
    }
    
    /**
     * Validate ObjectCluster data against device schema
     */
    suspend fun validateObjectCluster(
        objectCluster: ObjectCluster,
        deviceType: String = "Shimmer3-GSR+"
    ): ValidationResult = withContext(Dispatchers.Default) {
        
        val schema = deviceSchemas[deviceType]
        if (schema == null) {
            return@withContext ValidationResult(
                isValid = false,
                errors = listOf("No schema found for device type: $deviceType")
            )
        }
        
        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()
        val validatedChannels = mutableSetOf<String>()
        val missingChannels = mutableSetOf<String>()
        val extraChannels = mutableSetOf<String>()
        
        try {
            // Check for required channels
            schema.requiredChannels.forEach { requiredChannel ->
                val channelSchema = schema.supportedChannels[requiredChannel]
                if (channelSchema != null) {
                    try {
                        val formats = objectCluster.getCollectionOfFormatClusters(channelSchema.name)
                        if (formats == null || formats.isEmpty()) {
                            missingChannels.add(requiredChannel)
                            errors.add("Required channel missing: $requiredChannel (${channelSchema.name})")
                        } else {
                            validatedChannels.add(requiredChannel)
                        }
                    } catch (e: Exception) {
                        errors.add("Error accessing required channel $requiredChannel: ${e.message}")
                    }
                }
            }
            
            // Validate present channels
            schema.supportedChannels.forEach { (channelKey, channelSchema) ->
                try {
                    val formats = objectCluster.getCollectionOfFormatClusters(channelSchema.name)
                    if (formats != null && formats.isNotEmpty()) {
                        val formatCluster = com.shimmerresearch.driver.ObjectCluster.returnFormatCluster(formats, "CAL")
                        if (formatCluster != null) {
                            val value = formatCluster.mData
                            
                            // Validate data type
                            if (!isValidDataType(value, channelSchema.dataType)) {
                                errors.add("Invalid data type for ${channelSchema.displayName}: expected ${channelSchema.dataType}")
                            }
                            
                            // Validate range
                            if (!isValueInRange(value, channelSchema.validRange)) {
                                warnings.add("Value out of range for ${channelSchema.displayName}: $value (expected ${channelSchema.validRange})")
                            }
                            
                            validatedChannels.add(channelKey)
                        }
                    }
                } catch (e: Exception) {
                    warnings.add("Error validating channel ${channelSchema.displayName}: ${e.message}")
                }
            }
            
            // Check for extra/unknown channels
            try {
                // This would require iterating through all ObjectCluster data
                // Implementation depends on Shimmer SDK capabilities
                logger.debug("Channel validation completed for ${validatedChannels.size} channels")
            } catch (e: Exception) {
                warnings.add("Could not check for extra channels: ${e.message}")
            }
            
        } catch (e: Exception) {
            errors.add("Schema validation failed: ${e.message}")
        }
        
        val isValid = errors.isEmpty() && missingChannels.isEmpty()
        
        val result = ValidationResult(
            isValid = isValid,
            errors = errors,
            warnings = warnings,
            validatedChannels = validatedChannels,
            missingChannels = missingChannels,
            extraChannels = extraChannels
        )
        
        logger.debug("Schema validation result for $deviceType: valid=$isValid, errors=${errors.size}, warnings=${warnings.size}")
        
        result
    }
    
    /**
     * Validate sensor sample data
     */
    fun validateSensorSample(
        sensorSample: SensorSample,
        deviceType: String = "Shimmer3-GSR+"
    ): ValidationResult {
        val schema = deviceSchemas[deviceType]
        if (schema == null) {
            return ValidationResult(
                isValid = false,
                errors = listOf("No schema found for device type: $deviceType")
            )
        }
        
        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()
        val validatedChannels = mutableSetOf<String>()
        val missingChannels = mutableSetOf<String>()
        
        // Check for required channels in sensor values
        schema.requiredChannels.forEach { requiredChannel ->
            val channelSchema = schema.supportedChannels[requiredChannel]
            if (channelSchema != null) {
                // Map schema channel names to SensorChannel enum
                val sensorChannel = mapSchemaChannelToSensorChannel(requiredChannel)
                if (sensorChannel != null) {
                    val value = sensorSample.sensorValues[sensorChannel]
                    if (value == null) {
                        missingChannels.add(requiredChannel)
                        errors.add("Required sensor value missing: $requiredChannel")
                    } else {
                        // Validate range
                        if (!isValueInRange(value, channelSchema.validRange)) {
                            warnings.add("Sensor value out of range for ${channelSchema.displayName}: $value")
                        }
                        validatedChannels.add(requiredChannel)
                    }
                }
            }
        }
        
        // Validate timestamp
        if (sensorSample.systemTimestamp <= 0) {
            errors.add("Invalid system timestamp: ${sensorSample.systemTimestamp}")
        }
        
        if (sensorSample.deviceTimestamp <= 0) {
            warnings.add("Invalid device timestamp: ${sensorSample.deviceTimestamp}")
        }
        
        // Validate battery level
        if (sensorSample.batteryLevel < 0 || sensorSample.batteryLevel > 100) {
            warnings.add("Battery level out of range: ${sensorSample.batteryLevel}%")
        }
        
        val isValid = errors.isEmpty()
        
        return ValidationResult(
            isValid = isValid,
            errors = errors,
            warnings = warnings,
            validatedChannels = validatedChannels,
            missingChannels = missingChannels
        )
    }
    
    /**
     * Get schema documentation for a device type
     */
    fun getSchemaDocumentation(deviceType: String): String? {
        val schema = deviceSchemas[deviceType] ?: return null
        
        return buildString {
            appendLine("Schema Documentation for ${schema.deviceType}")
            appendLine("Firmware Version: ${schema.firmwareVersion}")
            appendLine("Data Format: ${schema.dataFormat}")
            appendLine("Sampling Rate Range: ${schema.samplingRateRange}")
            appendLine("Max Simultaneous Channels: ${schema.maxChannelsSimultaneous}")
            appendLine()
            appendLine("Supported Sensor Channels:")
            
            schema.supportedChannels.values.sortedBy { it.name }.forEach { channel ->
                appendLine("  ${channel.displayName} (${channel.name})")
                appendLine("    Type: ${channel.dataType}")
                appendLine("    Unit: ${channel.unit}")
                appendLine("    Range: ${channel.validRange}")
                appendLine("    Precision: ${channel.precision} decimal places")
                appendLine("    Required: ${if (channel.isRequired) "Yes" else "No"}")
                appendLine("    Calibration Required: ${if (channel.calibrationRequired) "Yes" else "No"}")
                appendLine()
            }
            
            appendLine("Required Channels:")
            schema.requiredChannels.forEach { channel ->
                appendLine("  - $channel")
            }
        }
    }
    
    /**
     * Check if device supports specific channels
     */
    fun supportsChannels(deviceType: String, channelNames: List<String>): Map<String, Boolean> {
        val schema = deviceSchemas[deviceType] ?: return channelNames.associateWith { false }
        
        return channelNames.associateWith { channelName ->
            schema.supportedChannels.containsKey(channelName) || 
            schema.supportedChannels.values.any { it.name == channelName }
        }
    }
    
    /**
     * Get optimal sampling rate for given channels
     */
    fun getOptimalSamplingRate(deviceType: String, enabledChannels: Set<String>): Double? {
        val schema = deviceSchemas[deviceType] ?: return null
        
        // Basic implementation - could be enhanced with more sophisticated logic
        return when {
            enabledChannels.size <= 3 -> schema.samplingRateRange.endInclusive // Max rate for few channels
            enabledChannels.size <= 6 -> (schema.samplingRateRange.endInclusive * 0.7) // Moderate rate
            else -> (schema.samplingRateRange.endInclusive * 0.5) // Conservative rate for many channels
        }
    }
    
    /**
     * Validate device configuration against schema
     */
    fun validateDeviceConfiguration(
        deviceType: String,
        configuration: DeviceConfiguration
    ): ValidationResult {
        val schema = deviceSchemas[deviceType]
        if (schema == null) {
            return ValidationResult(
                isValid = false,
                errors = listOf("No schema found for device type: $deviceType")
            )
        }
        
        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()
        
        // Validate sampling rate
        if (!schema.samplingRateRange.contains(configuration.samplingRate)) {
            errors.add("Sampling rate ${configuration.samplingRate}Hz is outside valid range: ${schema.samplingRateRange}")
        }
        
        // Validate channel count
        if (configuration.enabledSensors.size > schema.maxChannelsSimultaneous) {
            errors.add("Too many channels enabled: ${configuration.enabledSensors.size} (max: ${schema.maxChannelsSimultaneous})")
        }
        
        // Check if all enabled sensors are supported
        configuration.enabledSensors.forEach { sensorChannel ->
            val channelKey = sensorChannel.name
            if (!schema.supportedChannels.containsKey(channelKey)) {
                warnings.add("Sensor channel may not be supported: ${sensorChannel.displayName}")
            }
        }
        
        return ValidationResult(
            isValid = errors.isEmpty(),
            errors = errors,
            warnings = warnings
        )
    }
    
    // Helper methods
    private fun isValidDataType(value: Double, expectedType: DataType): Boolean {
        return when (expectedType) {
            DataType.DOUBLE, DataType.FLOAT -> true // Double can represent both
            DataType.LONG -> value % 1.0 == 0.0 && value >= Long.MIN_VALUE && value <= Long.MAX_VALUE
            DataType.INT -> value % 1.0 == 0.0 && value >= Int.MIN_VALUE && value <= Int.MAX_VALUE
            DataType.BOOLEAN -> value == 0.0 || value == 1.0
            else -> false
        }
    }
    
    private fun isValueInRange(value: Double, range: DoubleRange): Boolean {
        return value >= range.start && value <= range.endInclusive
    }
    
    private fun mapSchemaChannelToSensorChannel(schemaChannel: String): DeviceConfiguration.SensorChannel? {
        return when (schemaChannel) {
            "GSR_CONDUCTANCE" -> DeviceConfiguration.SensorChannel.GSR
            "PPG_A13" -> DeviceConfiguration.SensorChannel.PPG
            "ACCEL_X" -> DeviceConfiguration.SensorChannel.ACCEL_X
            "ACCEL_Y" -> DeviceConfiguration.SensorChannel.ACCEL_Y
            "ACCEL_Z" -> DeviceConfiguration.SensorChannel.ACCEL_Z
            "GYRO_X" -> DeviceConfiguration.SensorChannel.GYRO_X
            "GYRO_Y" -> DeviceConfiguration.SensorChannel.GYRO_Y
            "GYRO_Z" -> DeviceConfiguration.SensorChannel.GYRO_Z
            "MAG_X" -> DeviceConfiguration.SensorChannel.MAG_X
            "MAG_Y" -> DeviceConfiguration.SensorChannel.MAG_Y
            "MAG_Z" -> DeviceConfiguration.SensorChannel.MAG_Z
            "ECG_LL_RA" -> DeviceConfiguration.SensorChannel.ECG
            "EMG" -> DeviceConfiguration.SensorChannel.EMG
            else -> null
        }
    }
    
    /**
     * Get list of supported device types
     */
    fun getSupportedDeviceTypes(): List<String> = deviceSchemas.keys.toList()
    
    /**
     * Get schema for device type
     */
    fun getDeviceSchema(deviceType: String): DeviceSchema? = deviceSchemas[deviceType]
    
    /**
     * Clear validation cache
     */
    fun clearValidationCache() {
        validationCache.clear()
        logger.debug("Validation cache cleared")
    }
    
    /**
     * Get validation statistics
     */
    fun getValidationStatistics(): Map<String, Any> = mapOf(
        "registeredSchemas" to deviceSchemas.size,
        "supportedDeviceTypes" to deviceSchemas.keys.toList(),
        "cacheSize" to validationCache.size
    )
    
    /**
     * Cleanup resources
     */
    fun cleanup() {
        validationCache.clear()
        logger.info("DataSchemaValidator cleanup completed")
    }
}