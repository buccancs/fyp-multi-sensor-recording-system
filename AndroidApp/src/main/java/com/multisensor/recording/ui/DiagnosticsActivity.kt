package com.multisensor.recording.ui

import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.ActivityDiagnosticsBinding
import com.multisensor.recording.ui.DiagnosticsHealthStatus
import dagger.hilt.android.AndroidEntryPoint

/**
 * Diagnostics Activity - System Health Dashboard
 * 
 * Provides comprehensive system diagnostics including:
 * - System health dashboard with real-time metrics
 * - Performance monitoring and metrics display
 * - Error logs viewer with filtering and search
 * - Network connectivity tests and results
 * - Device communication tests
 * - Diagnostics report generation and export
 */
@AndroidEntryPoint
class DiagnosticsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDiagnosticsBinding
    private lateinit var viewModel: DiagnosticsViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        binding = ActivityDiagnosticsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[DiagnosticsViewModel::class.java]
        } catch (e: Exception) {
            showError("Failed to initialize diagnostics: ${e.message}")
            return
        }

        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.apply {
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
            title = "System Diagnostics"
            subtitle = "Monitor system health and performance"
        }
        
        setupDiagnosticActions()
        setupReportActions()
    }

    private fun setupDiagnosticActions() {
        // Run diagnostics (using existing button)
        binding.runDiagnosticsButton.setOnClickListener {
            try {
                viewModel.runFullSystemDiagnostic()
                showMessage("Running system diagnostics...")
            } catch (e: Exception) {
                showError("Diagnostic failed: ${e.message}")
            }
        }
        
        // Test network connectivity (using existing button)
        binding.testNetworkButton.setOnClickListener {
            try {
                viewModel.testNetworkConnectivity()
                showMessage("Testing network connectivity...")
            } catch (e: Exception) {
                showError("Network test failed: ${e.message}")
            }
        }
    }

    private fun setupReportActions() {
        // Export diagnostic data (using existing button)
        binding.exportLogsButton.setOnClickListener {
            try {
                viewModel.exportDiagnosticData()
                showMessage("Exporting diagnostic data...")
            } catch (e: Exception) {
                showError("Export failed: ${e.message}")
            }
        }
    }

    private fun observeViewModel() {
        try {
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.uiState.collect { uiState ->
                        updateUI(uiState)
                    }
                }
            }
        } catch (e: Exception) {
            showError("Failed to setup monitoring: ${e.message}")
        }
    }

    private fun updateUI(uiState: DiagnosticsUiState) {
        updateSystemHealth(uiState)
        updateButtons(uiState)
    }

    private fun updateSystemHealth(uiState: DiagnosticsUiState) {
        // Update status chips based on system health
        updateStatusChips(uiState)
        
        // Update performance details
        binding.performanceDetails.text = buildString {
            append("• Frame Rate: ${uiState.currentFrameRate} FPS\n")
            append("• CPU Usage: ${uiState.cpuUsagePercent}%\n")
            append("• Memory Usage: ${uiState.memoryUsagePercent}%\n")
            append("• Network: ↓${uiState.networkDownload} ↑${uiState.networkUpload}")
        }
        
        // Update network details
        binding.networkDetails.text = buildString {
            append("• Connection Status: Connected\n")
            append("• Network Tests: ${uiState.networkTestResults.size} completed\n")
            append("• Device Tests: ${uiState.deviceTestResults.size} completed")
        }
        
        // Update device info details
        binding.deviceInfoDetails.text = buildString {
            append("• Connected Devices: ${uiState.connectedDevicesCount}\n")
            append("• Active Processes: ${uiState.activeProcessesCount}\n")
            append("• System Health: ${uiState.systemHealthStatus}\n")
            append("• Errors: ${uiState.errorCount}, Warnings: ${uiState.warningCount}")
        }
    }

    private fun updateStatusChips(uiState: DiagnosticsUiState) {
        // Update CPU status chip
        binding.cpuStatusChip.text = "CPU: ${uiState.cpuUsagePercent}%"
        binding.cpuStatusChip.isSelected = uiState.cpuUsagePercent < 80
        
        // Update memory status chip
        binding.memoryStatusChip.text = "Memory: ${uiState.memoryUsagePercent}%"
        binding.memoryStatusChip.isSelected = uiState.memoryUsagePercent < 90
        
        // Update storage status chip
        binding.storageStatusChip.text = "Storage: ${uiState.storageUsagePercent}%"
        binding.storageStatusChip.isSelected = uiState.storageUsagePercent < 85
    }

    private fun updateButtons(uiState: DiagnosticsUiState) {
        // Disable buttons during tests
        binding.runDiagnosticsButton.isEnabled = !uiState.isRunningDiagnostic
        binding.testNetworkButton.isEnabled = !uiState.isTestingNetwork
        binding.exportLogsButton.isEnabled = !uiState.isExportingData
        
        // Update button text for active operations
        binding.runDiagnosticsButton.text = if (uiState.isRunningDiagnostic) "Running Tests..." else "Run Tests"
        binding.exportLogsButton.text = if (uiState.isExportingData) "Exporting..." else "Export Logs"
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean =
        when (item.itemId) {
            android.R.id.home -> {
                onBackPressedDispatcher.onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(error: String) {
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        android.util.Log.e("DiagnosticsActivity", error)
    }
}