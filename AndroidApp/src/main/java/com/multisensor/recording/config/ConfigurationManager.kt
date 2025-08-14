package com.multisensor.recording.config

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.multisensor.recording.util.Logger
import org.json.JSONException
import org.json.JSONObject
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.IOException
import java.util.concurrent.atomic.AtomicBoolean

/**
 * NFR8: Maintainability and Modularity - External configuration management
 * 
 * Implements:
 * - External configuration through config.json
 * - Runtime configuration updates
 * - Modular component configuration
 * - Settings validation and defaults
 * - Configuration versioning and migration
 * 
 * Requirements from 3.tex section NFR8:
 * - Modular design with clear interfaces
 * - Configuration externalized (config.json and settings)
 * - Changes in requirements accommodated by editing configuration
 * - No need to modify code for configuration changes
 * - Extensible configuration for new sensor types and sampling rates
 */
class ConfigurationManager(private val context: Context) {
    
    companion object {
        private const val TAG = "ConfigurationManager"
        private const val CONFIG_FILE_NAME = "config.json"
        private const val SHARED_PREFS_NAME = "multisensor_config"
        private const val CONFIG_VERSION_KEY = "config_version"
        private const val CURRENT_CONFIG_VERSION = 1
    }

    private val sharedPrefs: SharedPreferences = context.getSharedPreferences(SHARED_PREFS_NAME, Context.MODE_PRIVATE)
    private val isConfigLoaded = AtomicBoolean(false)
    private var currentConfig: SystemConfiguration? = null
    private val configFile: File by lazy {
        File(context.getExternalFilesDir(null), CONFIG_FILE_NAME)
    }

    /**
     * Initialize configuration system
     * NFR8: External configuration loading
     */
    fun initializeConfiguration(): ConfigurationStatus {
        Logger.i(TAG, "Initializing configuration system...")
        
        try {
            // Check for configuration file
            val config = if (configFile.exists()) {
                loadConfigurationFromFile()
            } else {
                Logger.i(TAG, "No config file found, creating default configuration")
                createDefaultConfiguration()
            }
            
            // Validate configuration
            val validationResult = validateConfiguration(config)
            if (!validationResult.isValid) {
                Logger.e(TAG, "Configuration validation failed: ${validationResult.errors}")
                return ConfigurationStatus.INVALID
            }
            
            // Apply configuration
            currentConfig = config
            isConfigLoaded.set(true)
            
            // Save current configuration to file if it was default
            if (!configFile.exists()) {
                saveConfigurationToFile(config)
            }
            
            Logger.i(TAG, "Configuration system initialized successfully")
            return ConfigurationStatus.LOADED
            
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to initialize configuration", e)
            return ConfigurationStatus.ERROR
        }
    }

    /**
     * Load configuration from external config.json file
     * NFR8: Configuration externalized through config.json
     */
    private fun loadConfigurationFromFile(): SystemConfiguration {
        Logger.d(TAG, "Loading configuration from ${configFile.absolutePath}")
        
        return try {
            val jsonString = configFile.readText()
            val jsonConfig = JSONObject(jsonString)
            
            // Check version and migrate if necessary
            val configVersion = jsonConfig.optInt("version", 0)
            val migratedConfig = if (configVersion < CURRENT_CONFIG_VERSION) {
                migrateConfiguration(jsonConfig, configVersion)
            } else {
                jsonConfig
            }
            
            parseConfigurationFromJson(migratedConfig)
            
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to load configuration from file, using defaults", e)
            createDefaultConfiguration()
        }
    }

    /**
     * Create default system configuration
     * NFR8: Sensible defaults for maintainability
     */
    private fun createDefaultConfiguration(): SystemConfiguration {
        Logger.d(TAG, "Creating default configuration")
        
        return SystemConfiguration(
            version = CURRENT_CONFIG_VERSION,
            
            // Camera configuration
            camera = CameraConfiguration(
                rgbCamera = RgbCameraConfig(
                    resolution = Resolution(1920, 1080),
                    frameRate = 30,
                    bitrateMbps = 5.0,
                    enableStabilization = true
                ),
                thermalCamera = ThermalCameraConfig(
                    enabled = true,
                    resolution = Resolution(640, 480),
                    frameRate = 15,
                    temperatureRange = TemperatureRange(-10.0, 60.0)
                )
            ),
            
            // Sensor configuration
            sensor = SensorConfiguration(
                gsr = GsrSensorConfig(
                    enabled = true,
                    samplingRateHz = 128,
                    dataRange = DataRange(0.0, 100.0),
                    filterEnabled = true
                ),
                accelerometer = AccelerometerConfig(
                    enabled = false,
                    samplingRateHz = 50
                )
            ),
            
            // Network configuration
            network = NetworkConfiguration(
                pcServerPort = 8080,
                timeServerPort = 8889,
                connectionTimeoutMs = 10000,
                heartbeatIntervalMs = 5000,
                enableTLS = true,
                enableDiscovery = true,
                maxConnections = 10
            ),
            
            // Session configuration
            session = SessionConfiguration(
                maxDurationMinutes = 120,
                enableAutoStop = true,
                enableFileChunking = true,
                chunkSizeGB = 1.0,
                enableCompression = false
            ),
            
            // Performance configuration
            performance = PerformanceConfiguration(
                enableMonitoring = true,
                maxMemoryUsagePercent = 80.0,
                maxCpuUsagePercent = 85.0,
                enableAdaptiveQuality = true,
                maxConcurrentDevices = 8
            ),
            
            // Security configuration
            security = SecurityConfiguration(
                enableEncryption = true,
                minAuthTokenLength = 32,
                enableRuntimeChecks = true,
                enableFileValidation = true
            ),
            
            // UI configuration
            ui = UIConfiguration(
                theme = "dark",
                enableStatusIndicators = true,
                updateIntervalMs = 1000,
                enablePreviewStreams = true,
                showPerformanceMetrics = false
            )
        )
    }

    /**
     * Parse configuration from JSON object
     */
    private fun parseConfigurationFromJson(json: JSONObject): SystemConfiguration {
        return SystemConfiguration(
            version = json.optInt("version", CURRENT_CONFIG_VERSION),
            
            camera = parseCameraConfiguration(json.optJSONObject("camera")),
            sensor = parseSensorConfiguration(json.optJSONObject("sensor")),
            network = parseNetworkConfiguration(json.optJSONObject("network")),
            session = parseSessionConfiguration(json.optJSONObject("session")),
            performance = parsePerformanceConfiguration(json.optJSONObject("performance")),
            security = parseSecurityConfiguration(json.optJSONObject("security")),
            ui = parseUIConfiguration(json.optJSONObject("ui"))
        )
    }

    /**
     * Parse camera configuration section
     */
    private fun parseCameraConfiguration(json: JSONObject?): CameraConfiguration {
        val defaults = createDefaultConfiguration().camera
        if (json == null) return defaults
        
        return CameraConfiguration(
            rgbCamera = RgbCameraConfig(
                resolution = parseResolution(json.optJSONObject("rgbCamera")?.optJSONObject("resolution")) ?: defaults.rgbCamera.resolution,
                frameRate = json.optJSONObject("rgbCamera")?.optInt("frameRate") ?: defaults.rgbCamera.frameRate,
                bitrateMbps = json.optJSONObject("rgbCamera")?.optDouble("bitrateMbps") ?: defaults.rgbCamera.bitrateMbps,
                enableStabilization = json.optJSONObject("rgbCamera")?.optBoolean("enableStabilization") ?: defaults.rgbCamera.enableStabilization
            ),
            thermalCamera = ThermalCameraConfig(
                enabled = json.optJSONObject("thermalCamera")?.optBoolean("enabled") ?: defaults.thermalCamera.enabled,
                resolution = parseResolution(json.optJSONObject("thermalCamera")?.optJSONObject("resolution")) ?: defaults.thermalCamera.resolution,
                frameRate = json.optJSONObject("thermalCamera")?.optInt("frameRate") ?: defaults.thermalCamera.frameRate,
                temperatureRange = parseTemperatureRange(json.optJSONObject("thermalCamera")?.optJSONObject("temperatureRange")) ?: defaults.thermalCamera.temperatureRange
            )
        )
    }

    /**
     * Parse sensor configuration section
     */
    private fun parseSensorConfiguration(json: JSONObject?): SensorConfiguration {
        val defaults = createDefaultConfiguration().sensor
        if (json == null) return defaults
        
        return SensorConfiguration(
            gsr = GsrSensorConfig(
                enabled = json.optJSONObject("gsr")?.optBoolean("enabled") ?: defaults.gsr.enabled,
                samplingRateHz = json.optJSONObject("gsr")?.optInt("samplingRateHz") ?: defaults.gsr.samplingRateHz,
                dataRange = parseDataRange(json.optJSONObject("gsr")?.optJSONObject("dataRange")) ?: defaults.gsr.dataRange,
                filterEnabled = json.optJSONObject("gsr")?.optBoolean("filterEnabled") ?: defaults.gsr.filterEnabled
            ),
            accelerometer = AccelerometerConfig(
                enabled = json.optJSONObject("accelerometer")?.optBoolean("enabled") ?: defaults.accelerometer.enabled,
                samplingRateHz = json.optJSONObject("accelerometer")?.optInt("samplingRateHz") ?: defaults.accelerometer.samplingRateHz
            )
        )
    }

    /**
     * Parse network configuration section
     */
    private fun parseNetworkConfiguration(json: JSONObject?): NetworkConfiguration {
        val defaults = createDefaultConfiguration().network
        if (json == null) return defaults
        
        return NetworkConfiguration(
            pcServerPort = json.optInt("pcServerPort", defaults.pcServerPort),
            timeServerPort = json.optInt("timeServerPort", defaults.timeServerPort),
            connectionTimeoutMs = json.optInt("connectionTimeoutMs", defaults.connectionTimeoutMs),
            heartbeatIntervalMs = json.optInt("heartbeatIntervalMs", defaults.heartbeatIntervalMs),
            enableTLS = json.optBoolean("enableTLS", defaults.enableTLS),
            enableDiscovery = json.optBoolean("enableDiscovery", defaults.enableDiscovery),
            maxConnections = json.optInt("maxConnections", defaults.maxConnections)
        )
    }

    /**
     * Parse session configuration section
     */
    private fun parseSessionConfiguration(json: JSONObject?): SessionConfiguration {
        val defaults = createDefaultConfiguration().session
        if (json == null) return defaults
        
        return SessionConfiguration(
            maxDurationMinutes = json.optInt("maxDurationMinutes", defaults.maxDurationMinutes),
            enableAutoStop = json.optBoolean("enableAutoStop", defaults.enableAutoStop),
            enableFileChunking = json.optBoolean("enableFileChunking", defaults.enableFileChunking),
            chunkSizeGB = json.optDouble("chunkSizeGB", defaults.chunkSizeGB),
            enableCompression = json.optBoolean("enableCompression", defaults.enableCompression)
        )
    }

    /**
     * Parse performance configuration section
     */
    private fun parsePerformanceConfiguration(json: JSONObject?): PerformanceConfiguration {
        val defaults = createDefaultConfiguration().performance
        if (json == null) return defaults
        
        return PerformanceConfiguration(
            enableMonitoring = json.optBoolean("enableMonitoring", defaults.enableMonitoring),
            maxMemoryUsagePercent = json.optDouble("maxMemoryUsagePercent", defaults.maxMemoryUsagePercent),
            maxCpuUsagePercent = json.optDouble("maxCpuUsagePercent", defaults.maxCpuUsagePercent),
            enableAdaptiveQuality = json.optBoolean("enableAdaptiveQuality", defaults.enableAdaptiveQuality),
            maxConcurrentDevices = json.optInt("maxConcurrentDevices", defaults.maxConcurrentDevices)
        )
    }

    /**
     * Parse security configuration section
     */
    private fun parseSecurityConfiguration(json: JSONObject?): SecurityConfiguration {
        val defaults = createDefaultConfiguration().security
        if (json == null) return defaults
        
        return SecurityConfiguration(
            enableEncryption = json.optBoolean("enableEncryption", defaults.enableEncryption),
            minAuthTokenLength = json.optInt("minAuthTokenLength", defaults.minAuthTokenLength),
            enableRuntimeChecks = json.optBoolean("enableRuntimeChecks", defaults.enableRuntimeChecks),
            enableFileValidation = json.optBoolean("enableFileValidation", defaults.enableFileValidation)
        )
    }

    /**
     * Parse UI configuration section
     */
    private fun parseUIConfiguration(json: JSONObject?): UIConfiguration {
        val defaults = createDefaultConfiguration().ui
        if (json == null) return defaults
        
        return UIConfiguration(
            theme = json.optString("theme", defaults.theme),
            enableStatusIndicators = json.optBoolean("enableStatusIndicators", defaults.enableStatusIndicators),
            updateIntervalMs = json.optInt("updateIntervalMs", defaults.updateIntervalMs),
            enablePreviewStreams = json.optBoolean("enablePreviewStreams", defaults.enablePreviewStreams),
            showPerformanceMetrics = json.optBoolean("showPerformanceMetrics", defaults.showPerformanceMetrics)
        )
    }

    /**
     * Helper parsers for nested objects
     */
    private fun parseResolution(json: JSONObject?): Resolution? {
        return if (json != null) {
            Resolution(json.optInt("width", 1920), json.optInt("height", 1080))
        } else null
    }

    private fun parseTemperatureRange(json: JSONObject?): TemperatureRange? {
        return if (json != null) {
            TemperatureRange(json.optDouble("min", -10.0), json.optDouble("max", 60.0))
        } else null
    }

    private fun parseDataRange(json: JSONObject?): DataRange? {
        return if (json != null) {
            DataRange(json.optDouble("min", 0.0), json.optDouble("max", 100.0))
        } else null
    }

    /**
     * Migrate configuration from older version
     * NFR8: Configuration versioning and migration
     */
    private fun migrateConfiguration(config: JSONObject, fromVersion: Int): JSONObject {
        Logger.i(TAG, "Migrating configuration from version $fromVersion to $CURRENT_CONFIG_VERSION")
        
        // Add migration logic here for future versions
        config.put("version", CURRENT_CONFIG_VERSION)
        
        return config
    }

    /**
     * Validate configuration
     * NFR8: Configuration validation
     */
    private fun validateConfiguration(config: SystemConfiguration): ValidationResult {
        val errors = mutableListOf<String>()
        
        // Validate camera settings
        if (config.camera.rgbCamera.frameRate <= 0 || config.camera.rgbCamera.frameRate > 120) {
            errors.add("Invalid RGB camera frame rate: ${config.camera.rgbCamera.frameRate}")
        }
        
        if (config.camera.rgbCamera.bitrateMbps <= 0 || config.camera.rgbCamera.bitrateMbps > 50) {
            errors.add("Invalid RGB camera bitrate: ${config.camera.rgbCamera.bitrateMbps}")
        }
        
        // Validate sensor settings
        if (config.sensor.gsr.samplingRateHz <= 0 || config.sensor.gsr.samplingRateHz > 1000) {
            errors.add("Invalid GSR sampling rate: ${config.sensor.gsr.samplingRateHz}")
        }
        
        // Validate network settings
        if (config.network.pcServerPort <= 1024 || config.network.pcServerPort > 65535) {
            errors.add("Invalid PC server port: ${config.network.pcServerPort}")
        }
        
        // Validate session settings
        if (config.session.maxDurationMinutes <= 0 || config.session.maxDurationMinutes > 720) {
            errors.add("Invalid max session duration: ${config.session.maxDurationMinutes}")
        }
        
        // Validate security settings
        if (config.security.minAuthTokenLength < 16) {
            errors.add("Auth token length too short: ${config.security.minAuthTokenLength} (minimum 16)")
        }
        
        return ValidationResult(errors.isEmpty(), errors)
    }

    /**
     * Save configuration to file
     * NFR8: Persistent configuration storage
     */
    private fun saveConfigurationToFile(config: SystemConfiguration) {
        try {
            val jsonConfig = convertConfigurationToJson(config)
            configFile.writeText(jsonConfig.toString(2))
            Logger.d(TAG, "Configuration saved to ${configFile.absolutePath}")
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to save configuration to file", e)
        }
    }

    /**
     * Convert configuration to JSON
     */
    private fun convertConfigurationToJson(config: SystemConfiguration): JSONObject {
        return JSONObject().apply {
            put("version", config.version)
            put("camera", JSONObject().apply {
                put("rgbCamera", JSONObject().apply {
                    put("resolution", JSONObject().apply {
                        put("width", config.camera.rgbCamera.resolution.width)
                        put("height", config.camera.rgbCamera.resolution.height)
                    })
                    put("frameRate", config.camera.rgbCamera.frameRate)
                    put("bitrateMbps", config.camera.rgbCamera.bitrateMbps)
                    put("enableStabilization", config.camera.rgbCamera.enableStabilization)
                })
                put("thermalCamera", JSONObject().apply {
                    put("enabled", config.camera.thermalCamera.enabled)
                    put("resolution", JSONObject().apply {
                        put("width", config.camera.thermalCamera.resolution.width)
                        put("height", config.camera.thermalCamera.resolution.height)
                    })
                    put("frameRate", config.camera.thermalCamera.frameRate)
                    put("temperatureRange", JSONObject().apply {
                        put("min", config.camera.thermalCamera.temperatureRange.min)
                        put("max", config.camera.thermalCamera.temperatureRange.max)
                    })
                })
            })
            // Add other sections similarly...
        }
    }

    /**
     * Get current configuration
     * NFR8: Runtime configuration access
     */
    fun getConfiguration(): SystemConfiguration? {
        return if (isConfigLoaded.get()) currentConfig else null
    }

    /**
     * Update configuration at runtime
     * NFR8: Runtime configuration updates
     */
    fun updateConfiguration(config: SystemConfiguration): Boolean {
        val validationResult = validateConfiguration(config)
        if (!validationResult.isValid) {
            Logger.e(TAG, "Configuration update failed validation: ${validationResult.errors}")
            return false
        }
        
        currentConfig = config
        saveConfigurationToFile(config)
        Logger.i(TAG, "Configuration updated successfully")
        return true
    }

    /**
     * Update specific configuration section
     */
    fun updateCameraConfiguration(cameraConfig: CameraConfiguration): Boolean {
        val current = currentConfig ?: return false
        return updateConfiguration(current.copy(camera = cameraConfig))
    }

    fun updateSensorConfiguration(sensorConfig: SensorConfiguration): Boolean {
        val current = currentConfig ?: return false
        return updateConfiguration(current.copy(sensor = sensorConfig))
    }

    fun updateNetworkConfiguration(networkConfig: NetworkConfiguration): Boolean {
        val current = currentConfig ?: return false
        return updateConfiguration(current.copy(network = networkConfig))
    }

    // Configuration data classes

    data class SystemConfiguration(
        val version: Int,
        val camera: CameraConfiguration,
        val sensor: SensorConfiguration,
        val network: NetworkConfiguration,
        val session: SessionConfiguration,
        val performance: PerformanceConfiguration,
        val security: SecurityConfiguration,
        val ui: UIConfiguration
    )

    data class CameraConfiguration(
        val rgbCamera: RgbCameraConfig,
        val thermalCamera: ThermalCameraConfig
    )

    data class RgbCameraConfig(
        val resolution: Resolution,
        val frameRate: Int,
        val bitrateMbps: Double,
        val enableStabilization: Boolean
    )

    data class ThermalCameraConfig(
        val enabled: Boolean,
        val resolution: Resolution,
        val frameRate: Int,
        val temperatureRange: TemperatureRange
    )

    data class SensorConfiguration(
        val gsr: GsrSensorConfig,
        val accelerometer: AccelerometerConfig
    )

    data class GsrSensorConfig(
        val enabled: Boolean,
        val samplingRateHz: Int,
        val dataRange: DataRange,
        val filterEnabled: Boolean
    )

    data class AccelerometerConfig(
        val enabled: Boolean,
        val samplingRateHz: Int
    )

    data class NetworkConfiguration(
        val pcServerPort: Int,
        val timeServerPort: Int,
        val connectionTimeoutMs: Int,
        val heartbeatIntervalMs: Int,
        val enableTLS: Boolean,
        val enableDiscovery: Boolean,
        val maxConnections: Int
    )

    data class SessionConfiguration(
        val maxDurationMinutes: Int,
        val enableAutoStop: Boolean,
        val enableFileChunking: Boolean,
        val chunkSizeGB: Double,
        val enableCompression: Boolean
    )

    data class PerformanceConfiguration(
        val enableMonitoring: Boolean,
        val maxMemoryUsagePercent: Double,
        val maxCpuUsagePercent: Double,
        val enableAdaptiveQuality: Boolean,
        val maxConcurrentDevices: Int
    )

    data class SecurityConfiguration(
        val enableEncryption: Boolean,
        val minAuthTokenLength: Int,
        val enableRuntimeChecks: Boolean,
        val enableFileValidation: Boolean
    )

    data class UIConfiguration(
        val theme: String,
        val enableStatusIndicators: Boolean,
        val updateIntervalMs: Int,
        val enablePreviewStreams: Boolean,
        val showPerformanceMetrics: Boolean
    )

    data class Resolution(val width: Int, val height: Int)
    data class TemperatureRange(val min: Double, val max: Double)
    data class DataRange(val min: Double, val max: Double)

    data class ValidationResult(
        val isValid: Boolean,
        val errors: List<String>
    )

    enum class ConfigurationStatus {
        LOADED,
        INVALID,
        ERROR
    }
}