package com.multisensor.recording

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.SystemHealthStatus
import com.multisensor.recording.ui.SettingsActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Streamlined Material Design 3 Dashboard
 * 
 * Minimalist research data collection interface:
 * - Single-screen dashboard with organized sections
 * - Live video preview and recording controls at top
 * - System status and quick actions below
 * - Optimized for one-handed field operation
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // Initialize binding and ViewModel
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        } catch (e: Exception) {
            showError("Failed to initialize app: ${e.message}")
            return
        }

        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        binding.toolbar.title = "Multi-Sensor Recording"
        
        // Setup recording controls
        setupRecordingControls()
        
        // Setup quick actions
        setupQuickActions()
        
        // Setup FAB for settings
        setupFloatingActionButton()
        
        // Setup toolbar menu
        setupToolbarMenu()
    }

    private fun setupRecordingControls() {
        binding.recordButton.setOnClickListener {
            try {
                if (viewModel.uiState.value.isRecording) {
                    viewModel.stopRecording()
                } else {
                    viewModel.startRecording()
                }
            } catch (e: Exception) {
                showError("Recording control failed: ${e.message}")
            }
        }
    }

    private fun setupQuickActions() {
        // Calibration
        binding.calibrateButton.setOnClickListener {
            try {
                val intent = Intent(this, com.multisensor.recording.ui.CalibrationActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open calibration: ${e.message}")
            }
        }
        
        // Files management
        binding.filesButton.setOnClickListener {
            try {
                val intent = Intent(this, com.multisensor.recording.ui.FileViewActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open files: ${e.message}")
            }
        }
        
        // Device settings
        binding.devicesButton.setOnClickListener {
            try {
                val intent = Intent(this, com.multisensor.recording.ui.DevicesActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open device management: ${e.message}")
            }
        }
    }

    private fun setupFloatingActionButton() {
        binding.fabSettings.setOnClickListener {
            try {
                val intent = Intent(this, SettingsActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open settings: ${e.message}")
            }
        }
    }

    private fun setupToolbarMenu() {
        binding.toolbar.setOnMenuItemClickListener { menuItem ->
            when (menuItem.itemId) {
                R.id.action_settings -> {
                    navigateToActivity(SettingsActivity::class.java)
                    true
                }
                R.id.action_diagnostics -> {
                    navigateToActivity(com.multisensor.recording.ui.DiagnosticsActivity::class.java)
                    true
                }
                R.id.action_about -> {
                    navigateToActivity(com.multisensor.recording.ui.AboutActivity::class.java)
                    true
                }
                else -> false
            }
        }
        
        binding.toolbar.inflateMenu(R.menu.main_toolbar_menu)
    }

    private fun observeViewModel() {
        try {
            // Observe UI state changes using StateFlow
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

    private fun updateUI(uiState: MainUiState) {
        // Update recording controls
        updateRecordingControls(uiState)
        
        // Update device status indicators
        updateDeviceStatusIndicators(uiState)
        
        // Update storage info
        updateStorageInfo(uiState)
        
        // Update toolbar subtitle
        updateToolbarSubtitle(uiState)
    }

    private fun updateRecordingControls(uiState: MainUiState) {
        // Record button
        binding.recordButton.isEnabled = uiState.canStartRecording || uiState.canStopRecording
        binding.recordButton.text = if (uiState.isRecording) "Stop Recording" else "Start Recording"
        
        // Recording status
        binding.recordingStatusText.text = when {
            uiState.isRecording -> "Recording in progress..."
            uiState.canStartRecording -> "Ready to record"
            else -> "Cannot record - check connections"
        }
    }

    private fun updateDeviceStatusIndicators(uiState: MainUiState) {
        // Update device status indicators with color-coded dots
        updateStatusIndicator(binding.pcStatusText, uiState.isPcConnected)
        updateStatusIndicator(binding.shimmerStatusText, uiState.isShimmerConnected)
        updateStatusIndicator(binding.thermalStatusText, uiState.isThermalConnected)
        updateStatusIndicator(binding.networkStatusText, uiState.isNetworkConnected)
    }

    private fun updateStatusIndicator(textView: com.google.android.material.textview.MaterialTextView, isConnected: Boolean) {
        textView.text = "●"
        textView.setTextColor(
            if (isConnected) {
                resources.getColor(R.color.status_connected, theme)
            } else {
                resources.getColor(R.color.status_disconnected, theme)
            }
        )
    }

    private fun updateStorageInfo(uiState: MainUiState) {
        val usedPercentage = uiState.storageUsagePercentage
        binding.storageProgressBar.progress = usedPercentage
        binding.storageText.text = "${formatBytes(uiState.storageAvailable)} available"
    }

    private fun updateToolbarSubtitle(uiState: MainUiState) {
        val connectedDevices = listOfNotNull(
            if (uiState.isPcConnected) "PC" else null,
            if (uiState.isShimmerConnected) "Shimmer" else null,
            if (uiState.isThermalConnected) "Thermal" else null,
            if (uiState.isGsrConnected) "GSR" else null
        )
        
        binding.toolbar.subtitle = when {
            uiState.isRecording -> "● Recording..."
            connectedDevices.isNotEmpty() -> "${connectedDevices.size} devices connected"
            else -> "No devices connected"
        }
    }

    private fun formatDuration(durationMs: Long): String {
        val seconds = durationMs / 1000
        val minutes = seconds / 60
        val hours = minutes / 60
        return when {
            hours > 0 -> String.format("%d:%02d:%02d", hours, minutes % 60, seconds % 60)
            else -> String.format("%d:%02d", minutes, seconds % 60)
        }
    }

    private fun navigateToActivity(activityClass: Class<*>) {
        try {
            startActivity(Intent(this, activityClass))
        } catch (e: Exception) {
            showError("Navigation failed: ${e.message}")
        }
    }

    private fun runDiagnostics() {
        try {
            val currentState = viewModel.uiState.value
            val diagnosticInfo = buildString {
                appendLine("=== SYSTEM DIAGNOSTICS ===")
                appendLine("App Version: ${BuildConfig.VERSION_NAME}")
                appendLine("PC Connected: ${currentState.isPcConnected}")
                appendLine("Shimmer Connected: ${currentState.isShimmerConnected}")
                appendLine("Thermal Connected: ${currentState.isThermalConnected}")
                appendLine("GSR Connected: ${currentState.isGsrConnected}")
                appendLine("Network Connected: ${currentState.isNetworkConnected}")
                appendLine("Recording Active: ${currentState.isRecording}")
                appendLine("System Status: ${currentState.systemHealthStatus}")
                appendLine("Permissions OK: ${checkPermissions()}")
                appendLine("Storage Available: ${formatBytes(currentState.storageAvailable)}")
                appendLine("========================")
            }
            
            showMessage("Diagnostics completed - check logs for details")
            android.util.Log.i("DiagnosticsMD3", diagnosticInfo)
            
        } catch (e: Exception) {
            showError("Diagnostics failed: ${e.message}")
        }
    }

    private fun formatBytes(bytes: Long): String {
        return when {
            bytes >= 1024 * 1024 * 1024 -> String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0))
            bytes >= 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
            bytes >= 1024 -> String.format("%.1f KB", bytes / 1024.0)
            else -> "$bytes B"
        }
    }

    private fun checkPermissions(): Boolean {
        // Simple permission check - can be expanded
        return checkSelfPermission(android.Manifest.permission.CAMERA) == 
               android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(error: String) {
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        android.util.Log.e("MainActivityMD3", error)
    }
}