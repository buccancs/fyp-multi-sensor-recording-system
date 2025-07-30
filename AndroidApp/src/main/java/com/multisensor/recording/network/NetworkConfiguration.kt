package com.multisensor.recording.network

import android.content.Context
import android.content.SharedPreferences
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Network Configuration Manager for Milestone 2.6 Implementation Gap Resolution.
 * Manages dynamic server IP configuration to replace hardcoded values.
 *
 * Provides configurable network settings with persistent storage and default values.
 */
@Singleton
class NetworkConfiguration
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) {
        companion object {
            private const val PREFS_NAME = "network_config"
            private const val KEY_SERVER_IP = "server_ip"
            private const val KEY_LEGACY_PORT = "legacy_port"
            private const val KEY_JSON_PORT = "json_port"

            // Default configuration values
            private const val DEFAULT_SERVER_IP = "192.168.1.100"
            private const val DEFAULT_LEGACY_PORT = 8080
            private const val DEFAULT_JSON_PORT = 9000
        }

        private val sharedPreferences: SharedPreferences by lazy {
            context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        }

        /**
         * Get configured server IP address
         */
        fun getServerIp(): String = sharedPreferences.getString(KEY_SERVER_IP, DEFAULT_SERVER_IP) ?: DEFAULT_SERVER_IP

        /**
         * Set server IP address
         */
        fun setServerIp(ip: String) {
            sharedPreferences.edit().apply {
                putString(KEY_SERVER_IP, ip)
                apply()
            }
        }

        /**
         * Get legacy socket port (Milestone 2.5 compatibility)
         */
        fun getLegacyPort(): Int = sharedPreferences.getInt(KEY_LEGACY_PORT, DEFAULT_LEGACY_PORT)

        /**
         * Set legacy socket port
         */
        fun setLegacyPort(port: Int) {
            sharedPreferences.edit().apply {
                putInt(KEY_LEGACY_PORT, port)
                apply()
            }
        }

        /**
         * Get JSON socket port (Milestone 2.6)
         */
        fun getJsonPort(): Int = sharedPreferences.getInt(KEY_JSON_PORT, DEFAULT_JSON_PORT)

        /**
         * Set JSON socket port
         */
        fun setJsonPort(port: Int) {
            sharedPreferences.edit().apply {
                putInt(KEY_JSON_PORT, port)
                apply()
            }
        }

        /**
         * Get complete server configuration
         */
        fun getServerConfiguration(): ServerConfiguration =
            ServerConfiguration(
                serverIp = getServerIp(),
                legacyPort = getLegacyPort(),
                jsonPort = getJsonPort(),
            )

        /**
         * Update complete server configuration
         */
        fun updateServerConfiguration(config: ServerConfiguration) {
            sharedPreferences.edit().apply {
                putString(KEY_SERVER_IP, config.serverIp)
                putInt(KEY_LEGACY_PORT, config.legacyPort)
                putInt(KEY_JSON_PORT, config.jsonPort)
                apply()
            }
        }

        /**
         * Reset to default configuration
         */
        fun resetToDefaults() {
            sharedPreferences.edit().apply {
                putString(KEY_SERVER_IP, DEFAULT_SERVER_IP)
                putInt(KEY_LEGACY_PORT, DEFAULT_LEGACY_PORT)
                putInt(KEY_JSON_PORT, DEFAULT_JSON_PORT)
                apply()
            }
        }

        /**
         * Check if configuration has been customized
         */
        fun isCustomConfiguration(): Boolean =
            getServerIp() != DEFAULT_SERVER_IP ||
                getLegacyPort() != DEFAULT_LEGACY_PORT ||
                getJsonPort() != DEFAULT_JSON_PORT

        /**
         * Validate IP address format
         */
        fun isValidIpAddress(ip: String): Boolean {
            return try {
                val parts = ip.split(".")
                if (parts.size != 4) return false

                parts.all { part ->
                    val num = part.toIntOrNull()
                    num != null && num in 0..255
                }
            } catch (e: Exception) {
                false
            }
        }

        /**
         * Validate port number
         */
        fun isValidPort(port: Int): Boolean = port in 1024..65535

        /**
         * Get configuration summary for logging
         */
        fun getConfigurationSummary(): String {
            val config = getServerConfiguration()
            return "NetworkConfig[IP=${config.serverIp}, Legacy=${config.legacyPort}, JSON=${config.jsonPort}]"
        }
    }

/**
 * Data class representing complete server configuration
 */
data class ServerConfiguration(
    val serverIp: String,
    val legacyPort: Int,
    val jsonPort: Int,
) {
    /**
     * Get legacy socket address
     */
    fun getLegacyAddress(): String = "$serverIp:$legacyPort"

    /**
     * Get JSON socket address
     */
    fun getJsonAddress(): String = "$serverIp:$jsonPort"

    /**
     * Validate configuration
     */
    fun isValid(): Boolean {
        val networkConfig = NetworkConfiguration::class.java.newInstance()
        return networkConfig.isValidIpAddress(serverIp) &&
            networkConfig.isValidPort(legacyPort) &&
            networkConfig.isValidPort(jsonPort)
    }
}
