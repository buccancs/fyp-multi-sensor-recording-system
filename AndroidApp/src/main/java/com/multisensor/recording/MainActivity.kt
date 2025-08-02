package com.multisensor.recording

import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.google.android.material.navigation.NavigationView
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.FileViewActivity
import com.multisensor.recording.ui.NetworkConfigActivity
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.ui.ShimmerConfigActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Material Design 3 Main Activity
 * 
 * Clean, minimalist interface focused on essential functionality:
 * - System status monitoring
 * - Recording controls  
 * - Quick access to key features
 * - Simplified navigation
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    private lateinit var toggle: ActionBarDrawerToggle

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
        
        // Setup navigation drawer
        toggle = ActionBarDrawerToggle(
            this, binding.drawerLayout, binding.toolbar,
            R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        binding.drawerLayout.addDrawerListener(toggle)
        toggle.syncState()
        
        binding.navView.setNavigationItemSelectedListener(this)
        
        // Setup button listeners with error protection
        setupButtonListeners()
    }

    private fun setupButtonListeners() {
        // Recording controls
        binding.startRecordingButton.setOnClickListener {
            try {
                viewModel.startRecording()
                showMessage("Recording started")
            } catch (e: Exception) {
                showError("Failed to start recording: ${e.message}")
            }
        }
        
        binding.stopRecordingButton.setOnClickListener {
            try {
                viewModel.stopRecording()
                showMessage("Recording stopped")
            } catch (e: Exception) {
                showError("Failed to stop recording: ${e.message}")
            }
        }
        
        // Quick action buttons
        binding.calibrationButton.setOnClickListener {
            navigateToFragment("calibration")
        }
        
        binding.settingsButton.setOnClickListener {
            navigateToActivity(SettingsActivity::class.java)
        }
        
        binding.devicesButton.setOnClickListener {
            navigateToFragment("devices")
        }
        
        binding.filesButton.setOnClickListener {
            navigateToActivity(FileViewActivity::class.java)
        }
        
        // Diagnostics FAB
        binding.diagnosticsFab.setOnClickListener {
            runDiagnostics()
        }
    }

    private fun observeViewModel() {
        try {
            // Observe UI state changes using StateFlow
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.uiState.collect { uiState ->
                        updateConnectionStatus(binding.pcConnectionIndicator, 
                                             binding.pcConnectionStatus,
                                             uiState.isPcConnected, "PC Connection")
                        
                        updateConnectionStatus(binding.shimmerConnectionIndicator,
                                             binding.shimmerConnectionStatus,
                                             uiState.isShimmerConnected, "Shimmer")
                        
                        updateConnectionStatus(binding.thermalConnectionIndicator,
                                             binding.thermalConnectionStatus,
                                             uiState.isThermalConnected, "Thermal Camera")
                        
                        // Update recording state
                        binding.startRecordingButton.isEnabled = uiState.canStartRecording
                        binding.stopRecordingButton.isEnabled = uiState.canStopRecording
                    }
                }
            }
            
        } catch (e: Exception) {
            showError("Failed to setup monitoring: ${e.message}")
        }
    }

    private fun updateConnectionStatus(indicator: android.view.View, 
                                     textView: com.google.android.material.textview.MaterialTextView,
                                     connected: Boolean, deviceName: String) {
        val color = if (connected) {
            getColor(R.color.status_connected)
        } else {
            getColor(R.color.status_disconnected)
        }
        
        indicator.setBackgroundColor(color)
        textView.text = "$deviceName: ${if (connected) "Connected" else "Disconnected"}"
    }

    private fun navigateToActivity(activityClass: Class<*>) {
        try {
            startActivity(Intent(this, activityClass))
        } catch (e: Exception) {
            showError("Navigation failed: ${e.message}")
        }
    }

    private fun navigateToFragment(fragmentType: String) {
        // For now, show a message - fragments can be implemented later if needed
        showMessage("$fragmentType feature coming soon")
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
                appendLine("Recording Active: ${currentState.isRecording}")
                appendLine("System Status: ${currentState.systemHealthStatus}")
                appendLine("Permissions OK: ${checkPermissions()}")
                appendLine("========================")
            }
            
            showMessage("Diagnostics completed - check logs for details")
            android.util.Log.i("DiagnosticsMD3", diagnosticInfo)
            
        } catch (e: Exception) {
            showError("Diagnostics failed: ${e.message}")
        }
    }

    private fun checkPermissions(): Boolean {
        // Simple permission check - can be expanded
        return checkSelfPermission(android.Manifest.permission.CAMERA) == 
               android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.nav_recording -> {
                // Already on main screen
            }
            R.id.nav_devices -> navigateToFragment("devices")
            R.id.nav_calibration -> navigateToFragment("calibration")
            R.id.nav_files -> navigateToActivity(FileViewActivity::class.java)
            R.id.nav_settings -> navigateToActivity(SettingsActivity::class.java)
            R.id.nav_network_config -> navigateToActivity(NetworkConfigActivity::class.java)
            R.id.nav_shimmer_config -> navigateToActivity(ShimmerConfigActivity::class.java)
            R.id.nav_diagnostics -> runDiagnostics()
            R.id.nav_about -> showAbout()
        }
        
        binding.drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    private fun showAbout() {
        showMessage("Multi-Sensor Recording System v${BuildConfig.VERSION_NAME}")
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(error: String) {
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        android.util.Log.e("MainActivityMD3", error)
    }

    override fun onBackPressed() {
        if (binding.drawerLayout.isDrawerOpen(GravityCompat.START)) {
            binding.drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}