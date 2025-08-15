package com.multisensor.recording.fragment

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.multisensor.recording.R
import com.multisensor.recording.MainActivity
import com.multisensor.recording.performance.PerformanceMonitor
import com.multisensor.recording.security.SecurityManager
import com.multisensor.recording.config.ConfigurationManager
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.launch

/**
 * Settings Fragment - System configuration and status display
 * Shows performance, security, and configuration information with interactive controls
 */
class SettingsFragment : Fragment(), View.OnClickListener {

    private lateinit var performanceStatus: TextView
    private lateinit var memoryUsage: TextView
    private lateinit var cpuUsage: TextView
    private lateinit var securityStatus: TextView
    private lateinit var encryptionStatus: TextView
    private lateinit var pcAddress: TextView
    private lateinit var samplingRate: TextView
    private lateinit var reloadConfigButton: Button
    private lateinit var testConnectionButton: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_settings, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        initializeViews(view)
        updateSettings()
    }

    private fun initializeViews(view: View) {
        performanceStatus = view.findViewById(R.id.performance_status)
        memoryUsage = view.findViewById(R.id.memory_usage)
        cpuUsage = view.findViewById(R.id.cpu_usage)
        securityStatus = view.findViewById(R.id.security_status)
        encryptionStatus = view.findViewById(R.id.encryption_status)
        pcAddress = view.findViewById(R.id.pc_address)
        samplingRate = view.findViewById(R.id.sampling_rate)
        
        // Initialize action buttons
        reloadConfigButton = view.findViewById(R.id.btn_reload_config)
        testConnectionButton = view.findViewById(R.id.btn_test_connection)
        
        // Set click listeners
        reloadConfigButton.setOnClickListener(this)
        testConnectionButton.setOnClickListener(this)
    }

    private fun updateSettings() {
        // Update performance information with better error handling
        try {
            val performanceMonitor = PerformanceMonitor(requireContext())
            val metrics = performanceMonitor.getCurrentMetrics()
            
            if (metrics != null) {
                performanceStatus.text = "System performing well"
                memoryUsage.text = "Memory Usage: ${metrics.memoryUsagePercent.toInt()}%"
                cpuUsage.text = "CPU Usage: ${metrics.cpuUsagePercent.toInt()}%"
                
                // Set color based on performance with proper resource handling
                val memoryPercent = metrics.memoryUsagePercent
                val memoryColor = when {
                    memoryPercent > 80.0 -> R.color.red
                    memoryPercent > 60.0 -> R.color.orange
                    else -> R.color.green
                }
                memoryUsage.setTextColor(requireContext().getColor(memoryColor))
                
                val cpuPercent = metrics.cpuUsagePercent
                val cpuColor = when {
                    cpuPercent > 80.0 -> R.color.red
                    cpuPercent > 60.0 -> R.color.orange
                    else -> R.color.green
                }
                cpuUsage.setTextColor(requireContext().getColor(cpuColor))
            } else {
                performanceStatus.text = "Performance data unavailable"
                memoryUsage.text = "Memory Usage: N/A"
                cpuUsage.text = "CPU Usage: N/A"
                performanceStatus.setTextColor(requireContext().getColor(R.color.orange))
            }
            
        } catch (e: Exception) {
            Logger.e("SettingsFragment", "Performance monitoring error: ${e.message}")
            performanceStatus.text = "Performance monitoring unavailable"
            performanceStatus.setTextColor(requireContext().getColor(R.color.red))
            memoryUsage.text = "Memory Usage: Error"
            cpuUsage.text = "CPU Usage: Error"
        }

        // Update security information with better validation
        try {
            val activity = activity as? MainActivity
            if (activity != null) {
                try {
                    val securityReport = activity.securityManager.generateSecurityReport()
                    
                    if (securityReport.hasWarnings()) {
                        val warningCount = securityReport.getWarningMessages().size
                        securityStatus.text = "Security warnings: $warningCount issues"
                        securityStatus.setTextColor(requireContext().getColor(R.color.orange))
                        encryptionStatus.text = "TLS Encryption: Check required"
                        encryptionStatus.setTextColor(requireContext().getColor(R.color.orange))
                    } else {
                        securityStatus.text = "Security: All checks passed"
                        securityStatus.setTextColor(requireContext().getColor(R.color.green))
                        encryptionStatus.text = "TLS Encryption: Enabled"
                        encryptionStatus.setTextColor(requireContext().getColor(R.color.green))
                    }
                } catch (e: Exception) {
                    securityStatus.text = "Security: Not available"
                    securityStatus.setTextColor(requireContext().getColor(R.color.red))
                    encryptionStatus.text = "TLS Encryption: Unknown"
                    encryptionStatus.setTextColor(requireContext().getColor(R.color.red))
                }
            } else {
                securityStatus.text = "Security: Not initialized"
                securityStatus.setTextColor(requireContext().getColor(R.color.red))
                encryptionStatus.text = "TLS Encryption: Unknown"
                encryptionStatus.setTextColor(requireContext().getColor(R.color.red))
            }
            
        } catch (e: Exception) {
            Logger.e("SettingsFragment", "Security status error: ${e.message}")
            securityStatus.text = "Security status: Error"
            securityStatus.setTextColor(requireContext().getColor(R.color.red))
            encryptionStatus.text = "TLS Encryption: Error"
            encryptionStatus.setTextColor(requireContext().getColor(R.color.red))
        }

        // Update configuration information with better error handling
        try {
            val activity = activity as? MainActivity
            if (activity != null) {
                try {
                    val config = activity.configurationManager.getConfiguration()
                    
                    if (config != null) {
                        pcAddress.text = "localhost:${config.network.pcServerPort}"
                        samplingRate.text = "${config.sensor.gsr.samplingRateHz} Hz"
                        pcAddress.setTextColor(requireContext().getColor(R.color.white))
                        samplingRate.setTextColor(requireContext().getColor(R.color.white))
                    } else {
                        pcAddress.text = "Configuration not loaded"
                        samplingRate.text = "Configuration not loaded"
                        pcAddress.setTextColor(requireContext().getColor(R.color.orange))
                        samplingRate.setTextColor(requireContext().getColor(R.color.orange))
                    }
                } catch (e: Exception) {
                    // Fallback values with indication they're defaults
                    pcAddress.text = "192.168.1.100 (default)"
                    samplingRate.text = "128 Hz (default)"
                    pcAddress.setTextColor(requireContext().getColor(R.color.tab_text))
                    samplingRate.setTextColor(requireContext().getColor(R.color.tab_text))
                }
            } else {
                // Fallback values with indication they're defaults
                pcAddress.text = "192.168.1.100 (default)"
                samplingRate.text = "128 Hz (default)"
                pcAddress.setTextColor(requireContext().getColor(R.color.tab_text))
                samplingRate.setTextColor(requireContext().getColor(R.color.tab_text))
            }
            
        } catch (e: Exception) {
            Logger.e("SettingsFragment", "Configuration error: ${e.message}")
            pcAddress.text = "Configuration error"
            samplingRate.text = "Configuration error"
            pcAddress.setTextColor(requireContext().getColor(R.color.red))
            samplingRate.setTextColor(requireContext().getColor(R.color.red))
        }
    }

    override fun onResume() {
        super.onResume()
        updateSettings()
    }
    
    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.btn_reload_config -> {
                handleReloadConfigClick()
            }
            R.id.btn_test_connection -> {
                handleTestConnectionClick()
            }
        }
    }
    
    /**
     * Handle reload configuration button click
     */
    private fun handleReloadConfigClick() {
        lifecycleScope.launch {
            try {
                reloadConfigButton.isEnabled = false
                reloadConfigButton.text = "Reloading..."
                
                val activity = activity as? MainActivity
                if (activity != null) {
                    try {
                        val status = activity.configurationManager.initializeConfiguration()
                        if (status == ConfigurationManager.ConfigurationStatus.LOADED) {
                            Toast.makeText(requireContext(), "✅ Configuration reloaded successfully", Toast.LENGTH_SHORT).show()
                            updateSettings() // Refresh display
                        } else {
                            Toast.makeText(requireContext(), "⚠️ Configuration reload failed", Toast.LENGTH_SHORT).show()
                        }
                    } catch (e: Exception) {
                        Toast.makeText(requireContext(), "❌ Configuration manager error", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(requireContext(), "❌ Configuration manager not available", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Logger.e("SettingsFragment", "Config reload error: ${e.message}")
                Toast.makeText(requireContext(), "❌ Error reloading configuration", Toast.LENGTH_SHORT).show()
            } finally {
                reloadConfigButton.isEnabled = true
                reloadConfigButton.text = "Reload Config"
            }
        }
    }
    
    /**
     * Handle test PC connection button click
     */
    private fun handleTestConnectionClick() {
        lifecycleScope.launch {
            try {
                testConnectionButton.isEnabled = false
                testConnectionButton.text = "Testing..."
                
                val activity = activity as? MainActivity
                if (activity != null) {
                    try {
                        // Test PC connection
                        val connected = activity.pcCommunicationClient.isConnected()
                        if (connected) {
                            Toast.makeText(requireContext(), "✅ PC connection successful", Toast.LENGTH_SHORT).show()
                        } else {
                            Toast.makeText(requireContext(), "⚠️ PC connection failed - check server", Toast.LENGTH_SHORT).show()
                        }
                    } catch (e: Exception) {
                        Toast.makeText(requireContext(), "❌ PC communication error", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(requireContext(), "❌ PC communication client not available", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Logger.e("SettingsFragment", "Connection test error: ${e.message}")
                Toast.makeText(requireContext(), "❌ Error testing connection", Toast.LENGTH_SHORT).show()
            } finally {
                testConnectionButton.isEnabled = true
                testConnectionButton.text = "Test PC Connection"
            }
        }
    }
}