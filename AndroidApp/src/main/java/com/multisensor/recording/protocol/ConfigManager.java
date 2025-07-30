package com.multisensor.recording.protocol;

import android.content.Context;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;

/**
 * ConfigManager for Android - manages the shared configuration for the recording system.
 * 
 * This class provides utilities for loading and managing the shared configuration
 * file. It implements the shared configuration approach described in Milestone 4
 * for ensuring consistent parameters between Python and Android platforms.
 */
public class ConfigManager {
    private static final String TAG = "ConfigManager";
    private static final String CONFIG_FILE = "config.json";
    
    private static ConfigManager instance;
    private JSONObject config;
    private Context context;
    
    private ConfigManager(Context context) {
        this.context = context.getApplicationContext();
        loadConfig();
    }
    
    /**
     * Get the singleton instance of ConfigManager.
     * 
     * @param context Android context for asset access
     * @return ConfigManager instance
     */
    public static synchronized ConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new ConfigManager(context);
        }
        return instance;
    }
    
    /**
     * Load the configuration from assets.
     */
    private void loadConfig() {
        try {
            InputStream is = context.getAssets().open(CONFIG_FILE);
            int size = is.available();
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();
            
            String configJson = new String(buffer, "UTF-8");
            config = new JSONObject(configJson);
            
            Log.i(TAG, "Successfully loaded configuration");
            
        } catch (IOException e) {
            Log.e(TAG, "Failed to load config file: " + e.getMessage());
            config = null;
        } catch (JSONException e) {
            Log.e(TAG, "Invalid JSON in config file: " + e.getMessage());
            config = null;
        }
    }
    
    /**
     * Get a configuration value by key path.
     * 
     * @param keyPath Dot-separated key path (e.g., "network.port")
     * @param defaultValue Default value if key not found
     * @return Configuration value or default
     */
    public Object get(String keyPath, Object defaultValue) {
        if (config == null) {
            return defaultValue;
        }
        
        String[] keys = keyPath.split("\\.");
        JSONObject current = config;
        
        try {
            // Navigate through nested objects
            for (int i = 0; i < keys.length - 1; i++) {
                if (!current.has(keys[i])) {
                    return defaultValue;
                }
                current = current.getJSONObject(keys[i]);
            }
            
            // Get the final value
            String finalKey = keys[keys.length - 1];
            if (!current.has(finalKey)) {
                return defaultValue;
            }
            
            return current.get(finalKey);
            
        } catch (JSONException e) {
            Log.e(TAG, "Error getting config value for " + keyPath + ": " + e.getMessage());
            return defaultValue;
        }
    }
    
    /**
     * Get a string configuration value.
     * 
     * @param keyPath Dot-separated key path
     * @param defaultValue Default value if key not found
     * @return String value or default
     */
    public String getString(String keyPath, String defaultValue) {
        Object value = get(keyPath, defaultValue);
        return value instanceof String ? (String) value : defaultValue;
    }
    
    /**
     * Get an integer configuration value.
     * 
     * @param keyPath Dot-separated key path
     * @param defaultValue Default value if key not found
     * @return Integer value or default
     */
    public int getInt(String keyPath, int defaultValue) {
        Object value = get(keyPath, defaultValue);
        if (value instanceof Integer) {
            return (Integer) value;
        } else if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        return defaultValue;
    }
    
    /**
     * Get a double configuration value.
     * 
     * @param keyPath Dot-separated key path
     * @param defaultValue Default value if key not found
     * @return Double value or default
     */
    public double getDouble(String keyPath, double defaultValue) {
        Object value = get(keyPath, defaultValue);
        if (value instanceof Double) {
            return (Double) value;
        } else if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        return defaultValue;
    }
    
    /**
     * Get a boolean configuration value.
     * 
     * @param keyPath Dot-separated key path
     * @param defaultValue Default value if key not found
     * @return Boolean value or default
     */
    public boolean getBoolean(String keyPath, boolean defaultValue) {
        Object value = get(keyPath, defaultValue);
        return value instanceof Boolean ? (Boolean) value : defaultValue;
    }
    
    /**
     * Get an entire configuration section.
     * 
     * @param section Section name (e.g., "network", "devices")
     * @return JSONObject containing the section data, or empty object if not found
     */
    public JSONObject getSection(String section) {
        if (config == null) {
            return new JSONObject();
        }
        
        try {
            return config.has(section) ? config.getJSONObject(section) : new JSONObject();
        } catch (JSONException e) {
            Log.e(TAG, "Error getting section " + section + ": " + e.getMessage());
            return new JSONObject();
        }
    }
    
    // Convenience methods for commonly used configuration sections
    
    /**
     * Get network configuration section.
     * 
     * @return JSONObject containing network configuration
     */
    public JSONObject getNetworkConfig() {
        return getSection("network");
    }
    
    /**
     * Get devices configuration section.
     * 
     * @return JSONObject containing devices configuration
     */
    public JSONObject getDevicesConfig() {
        return getSection("devices");
    }
    
    /**
     * Get UI configuration section.
     * 
     * @return JSONObject containing UI configuration
     */
    public JSONObject getUIConfig() {
        return getSection("UI");
    }
    
    /**
     * Get calibration configuration section.
     * 
     * @return JSONObject containing calibration configuration
     */
    public JSONObject getCalibrationConfig() {
        return getSection("calibration");
    }
    
    /**
     * Get session configuration section.
     * 
     * @return JSONObject containing session configuration
     */
    public JSONObject getSessionConfig() {
        return getSection("session");
    }
    
    /**
     * Get logging configuration section.
     * 
     * @return JSONObject containing logging configuration
     */
    public JSONObject getLoggingConfig() {
        return getSection("logging");
    }
    
    /**
     * Get testing configuration section.
     * 
     * @return JSONObject containing testing configuration
     */
    public JSONObject getTestingConfig() {
        return getSection("testing");
    }
    
    /**
     * Get performance configuration section.
     * 
     * @return JSONObject containing performance configuration
     */
    public JSONObject getPerformanceConfig() {
        return getSection("performance");
    }
    
    /**
     * Get security configuration section.
     * 
     * @return JSONObject containing security configuration
     */
    public JSONObject getSecurityConfig() {
        return getSection("security");
    }
    
    // Convenience methods for commonly used values
    
    /**
     * Get network host.
     * 
     * @return String host address
     */
    public String getHost() {
        return getString("network.host", "192.168.0.100");
    }
    
    /**
     * Get network port.
     * 
     * @return Integer port number
     */
    public int getPort() {
        return getInt("network.port", 9000);
    }
    
    /**
     * Get network timeout in seconds.
     * 
     * @return Integer timeout in seconds
     */
    public int getTimeout() {
        return getInt("network.timeout_seconds", 30);
    }
    
    /**
     * Get camera frame rate.
     * 
     * @return Integer frame rate
     */
    public int getFrameRate() {
        return getInt("devices.frame_rate", 30);
    }
    
    /**
     * Get camera resolution width.
     * 
     * @return Integer width in pixels
     */
    public int getResolutionWidth() {
        return getInt("devices.resolution.width", 1920);
    }
    
    /**
     * Get camera resolution height.
     * 
     * @return Integer height in pixels
     */
    public int getResolutionHeight() {
        return getInt("devices.resolution.height", 1080);
    }
    
    /**
     * Get preview resolution width.
     * 
     * @return Integer width in pixels
     */
    public int getPreviewResolutionWidth() {
        return getInt("devices.preview_resolution.width", 640);
    }
    
    /**
     * Get preview resolution height.
     * 
     * @return Integer height in pixels
     */
    public int getPreviewResolutionHeight() {
        return getInt("devices.preview_resolution.height", 480);
    }
    
    /**
     * Get UI preview scale factor.
     * 
     * @return Double scale factor
     */
    public double getPreviewScale() {
        return getDouble("UI.preview_scale", 0.5);
    }
    
    /**
     * Get calibration pattern rows.
     * 
     * @return Integer number of rows
     */
    public int getCalibrationPatternRows() {
        return getInt("calibration.pattern_rows", 7);
    }
    
    /**
     * Get calibration pattern columns.
     * 
     * @return Integer number of columns
     */
    public int getCalibrationPatternCols() {
        return getInt("calibration.pattern_cols", 6);
    }
    
    /**
     * Get calibration square size in meters.
     * 
     * @return Double square size in meters
     */
    public double getCalibrationSquareSize() {
        return getDouble("calibration.square_size_m", 0.0245);
    }
    
    /**
     * Get calibration error threshold in pixels.
     * 
     * @return Double error threshold
     */
    public double getCalibrationErrorThreshold() {
        return getDouble("calibration.error_threshold", 1.0);
    }
    
    /**
     * Get session directory path.
     * 
     * @return String directory path
     */
    public String getSessionDirectory() {
        return getString("session.session_directory", "recordings");
    }
    
    /**
     * Get log level.
     * 
     * @return String log level
     */
    public String getLogLevel() {
        return getString("logging.level", "INFO");
    }
    
    /**
     * Check if fake device mode is enabled for testing.
     * 
     * @return Boolean true if enabled
     */
    public boolean isFakeDeviceEnabled() {
        return getBoolean("testing.fake_device_enabled", false);
    }
    
    /**
     * Validate the configuration structure and values.
     * 
     * @return true if configuration is valid, false otherwise
     */
    public boolean validateConfig() {
        if (config == null) {
            Log.e(TAG, "Configuration not loaded");
            return false;
        }
        
        // Check required sections
        String[] requiredSections = {"network", "devices", "UI", "calibration"};
        
        for (String section : requiredSections) {
            if (!config.has(section)) {
                Log.e(TAG, "Missing required configuration section: " + section);
                return false;
            }
        }
        
        // Validate network section
        JSONObject network = getNetworkConfig();
        if (!network.has("host") || !network.has("port")) {
            Log.e(TAG, "Network configuration missing host or port");
            return false;
        }
        
        // Validate devices section
        JSONObject devices = getDevicesConfig();
        if (getFrameRate() <= 0) {
            Log.e(TAG, "Invalid frame rate in devices configuration");
            return false;
        }
        
        // Validate calibration section
        JSONObject calibration = getCalibrationConfig();
        if (getCalibrationPatternRows() <= 0 || getCalibrationPatternCols() <= 0) {
            Log.e(TAG, "Invalid calibration pattern size");
            return false;
        }
        
        Log.i(TAG, "Configuration validation passed");
        return true;
    }
    
    /**
     * Reload the configuration from assets (useful for development).
     */
    public void reloadConfig() {
        loadConfig();
    }
    
    /**
     * Check if configuration is loaded.
     * 
     * @return true if configuration is loaded, false otherwise
     */
    public boolean isConfigLoaded() {
        return config != null;
    }
}
