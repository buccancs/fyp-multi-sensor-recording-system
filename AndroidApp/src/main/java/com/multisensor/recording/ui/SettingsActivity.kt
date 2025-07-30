package com.multisensor.recording.ui

import android.os.Bundle
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import androidx.preference.PreferenceFragmentCompat
import com.multisensor.recording.R
import dagger.hilt.android.AndroidEntryPoint

/**
 * Settings and Configuration Activity - Milestone 2.7 UI Enhancement
 *
 * Provides comprehensive settings interface for:
 * - Shimmer MAC address configuration
 * - Recording parameters (video resolution, frame rate)
 * - Network configuration
 * - System preferences
 */
@AndroidEntryPoint
class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        // Setup action bar with back button
        supportActionBar?.apply {
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
            title = "Settings"
        }

        // Load settings fragment
        if (savedInstanceState == null) {
            supportFragmentManager
                .beginTransaction()
                .replace(R.id.settings_container, SettingsFragment())
                .commit()
        }
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean =
        when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }

    /**
     * Settings Fragment with comprehensive configuration options
     */
    class SettingsFragment : PreferenceFragmentCompat() {
        override fun onCreatePreferences(
            savedInstanceState: Bundle?,
            rootKey: String?,
        ) {
            setPreferencesFromResource(R.xml.preferences, rootKey)

            // Setup preference listeners and validation
            setupPreferenceListeners()
        }

        /**
         * Setup preference change listeners and validation
         */
        private fun setupPreferenceListeners() {
            // Shimmer MAC Address validation
            findPreference<androidx.preference.EditTextPreference>("shimmer_mac_address")?.apply {
                setOnPreferenceChangeListener { _, newValue ->
                    val macAddress = newValue as String
                    if (isValidMacAddress(macAddress)) {
                        summary = "MAC Address: $macAddress"
                        true
                    } else {
                        // Show error message
                        android.widget.Toast
                            .makeText(
                                context,
                                "Invalid MAC address format. Use format: XX:XX:XX:XX:XX:XX",
                                android.widget.Toast.LENGTH_LONG,
                            ).show()
                        false
                    }
                }

                // Set initial summary
                text?.let { summary = "MAC Address: $it" }
            }

            // Video resolution validation
            findPreference<androidx.preference.ListPreference>("video_resolution")?.apply {
                setOnPreferenceChangeListener { _, newValue ->
                    val resolution = newValue as String
                    summary = "Resolution: $resolution"
                    true
                }

                // Set initial summary
                value?.let { summary = "Resolution: $it" }
            }

            // Frame rate validation
            findPreference<androidx.preference.ListPreference>("frame_rate")?.apply {
                setOnPreferenceChangeListener { _, newValue ->
                    val frameRate = newValue as String
                    summary = "Frame Rate: ${frameRate}fps"
                    true
                }

                // Set initial summary
                value?.let { summary = "Frame Rate: ${it}fps" }
            }

            // Server IP validation
            findPreference<androidx.preference.EditTextPreference>("server_ip")?.apply {
                setOnPreferenceChangeListener { _, newValue ->
                    val ipAddress = newValue as String
                    if (isValidIpAddress(ipAddress)) {
                        summary = "Server IP: $ipAddress"
                        true
                    } else {
                        android.widget.Toast
                            .makeText(
                                context,
                                "Invalid IP address format",
                                android.widget.Toast.LENGTH_LONG,
                            ).show()
                        false
                    }
                }

                // Set initial summary
                text?.let { summary = "Server IP: $it" }
            }

            // Server port validation
            findPreference<androidx.preference.EditTextPreference>("server_port")?.apply {
                setOnPreferenceChangeListener { _, newValue ->
                    val portStr = newValue as String
                    try {
                        val port = portStr.toInt()
                        if (port in 1024..65535) {
                            summary = "Server Port: $port"
                            true
                        } else {
                            android.widget.Toast
                                .makeText(
                                    context,
                                    "Port must be between 1024 and 65535",
                                    android.widget.Toast.LENGTH_LONG,
                                ).show()
                            false
                        }
                    } catch (e: NumberFormatException) {
                        android.widget.Toast
                            .makeText(
                                context,
                                "Invalid port number",
                                android.widget.Toast.LENGTH_LONG,
                            ).show()
                        false
                    }
                }

                // Set initial summary
                text?.let { summary = "Server Port: $it" }
            }
        }

        /**
         * Validates MAC address format (XX:XX:XX:XX:XX:XX)
         */
        private fun isValidMacAddress(macAddress: String): Boolean {
            val macPattern = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
            return macAddress.matches(macPattern.toRegex())
        }

        /**
         * Validates IP address format
         */
        private fun isValidIpAddress(ipAddress: String): Boolean {
            val parts = ipAddress.split(".")
            if (parts.size != 4) return false

            return parts.all { part ->
                try {
                    val num = part.toInt()
                    num in 0..255
                } catch (e: NumberFormatException) {
                    false
                }
            }
        }
    }
}
