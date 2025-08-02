package com.multisensor.recording

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.ui.fragments.PreviewRecordFragment
import com.multisensor.recording.ui.fragments.DevicesFragment
import com.multisensor.recording.ui.fragments.FilesFragment
import com.multisensor.recording.ui.fragments.CalibrationFragment
import dagger.hilt.android.AndroidEntryPoint

/**
 * Material Design 3 Main Activity with Bottom Navigation
 * 
 * Research data collection app optimized for field use:
 * - Bottom navigation for primary sections (Preview/Record, Devices, Files, Calibration)
 * - Live video preview and recording controls
 * - Mobile-friendly layout for one-handed operation
 * - Clean Material Design aesthetics
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
        
        // Load default fragment (Preview/Record)
        if (savedInstanceState == null) {
            loadFragment(PreviewRecordFragment())
            binding.bottomNavigation.selectedItemId = R.id.nav_preview_record
        }
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        
        // Setup bottom navigation
        setupBottomNavigation()
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_preview_record -> {
                    loadFragment(PreviewRecordFragment())
                    binding.toolbar.title = "Preview & Record"
                    true
                }
                R.id.nav_devices -> {
                    loadFragment(DevicesFragment())
                    binding.toolbar.title = "Device Management"
                    true
                }
                R.id.nav_files -> {
                    loadFragment(FilesFragment())
                    binding.toolbar.title = "File Management"
                    true
                }
                R.id.nav_calibration -> {
                    loadFragment(CalibrationFragment())
                    binding.toolbar.title = "Calibration"
                    true
                }
                else -> false
            }
        }
        
        // Setup toolbar menu for settings
        binding.toolbar.setOnMenuItemClickListener { menuItem ->
            when (menuItem.itemId) {
                R.id.action_settings -> {
                    navigateToActivity(SettingsActivity::class.java)
                    true
                }
                R.id.action_diagnostics -> {
                    runDiagnostics()
                    true
                }
                else -> false
            }
        }
        
        binding.toolbar.inflateMenu(R.menu.main_toolbar_menu)
    }

    private fun loadFragment(fragment: Fragment) {
        try {
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragment_container, fragment)
                .commit()
        } catch (e: Exception) {
            showError("Failed to load fragment: ${e.message}")
        }
    }

    private fun observeViewModel() {
        try {
            // Observe UI state changes using StateFlow
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.uiState.collect { uiState ->
                        // Update toolbar subtitle based on system status
                        updateToolbarSubtitle(uiState)
                    }
                }
            }
            
        } catch (e: Exception) {
            showError("Failed to setup monitoring: ${e.message}")
        }
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