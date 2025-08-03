package com.multisensor.recording

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AlertDialog
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import androidx.drawerlayout.widget.DrawerLayout
import com.google.android.material.navigation.NavigationView
import com.google.android.material.bottomnavigation.BottomNavigationView
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import com.multisensor.recording.databinding.ActivityMainFragmentsBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.SystemHealthStatus
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Fragment-Based Material Design 3 MainActivity
 * 
 * Proper fragment-based architecture with Navigation Component:
 * - Navigation drawer for main sections
 * - Bottom navigation for quick access
 * - Fragment container for different screens
 * - Shared ViewModel across fragments
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainFragmentsBinding
    private lateinit var viewModel: MainViewModel
    private lateinit var appBarConfiguration: AppBarConfiguration
    
    @Inject
    lateinit var logger: Logger

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // Initialize binding and ViewModel
        binding = ActivityMainFragmentsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[MainViewModel::class.java]
            
            setupNavigation()
            setupUI()
            observeViewModel()
            
            logger.info("MainActivity initialized with fragment architecture")
            
        } catch (e: Exception) {
            logger.error("Error during MainActivity initialization", e)
            showErrorDialog("Initialization Error", "Failed to initialize the application: ${e.message}")
        }
    }

    private fun setupNavigation() {
        setSupportActionBar(binding.toolbar)
        
        val navController = findNavController(R.id.nav_host_fragment)
        
        // Setup app bar configuration
        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.nav_recording, R.id.nav_devices, 
                R.id.nav_calibration, R.id.nav_files
            ),
            binding.drawerLayout
        )
        
        setupActionBarWithNavController(navController, appBarConfiguration)
        
        // Setup navigation drawer
        binding.navView.setupWithNavController(navController)
        
        // Setup bottom navigation
        binding.bottomNavigation.setupWithNavController(navController)
        
        // Handle navigation menu item clicks
        binding.navView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_settings -> {
                    startActivity(Intent(this, SettingsActivity::class.java))
                    true
                }
                R.id.nav_network_config -> {
                    // Start NetworkConfigActivity when it exists
                    showToast("Network Config - Coming Soon")
                    true
                }
                R.id.nav_shimmer_config -> {
                    // Start ShimmerConfigActivity when it exists
                    showToast("Shimmer Config - Coming Soon")
                    true
                }
                R.id.nav_diagnostics -> {
                    // Start DiagnosticsActivity when it exists
                    showToast("Diagnostics - Coming Soon")
                    true
                }
                R.id.nav_about -> {
                    // Start AboutActivity when it exists
                    showToast("About - Coming Soon")
                    true
                }
                else -> {
                    // Handle fragment navigation
                    val navController = findNavController(R.id.nav_host_fragment)
                    navController.navigate(menuItem.itemId)
                    binding.drawerLayout.closeDrawers()
                    true
                }
            }
        }
    }

    private fun setupUI() {
        // Setup drawer toggle
        binding.toolbar.setNavigationOnClickListener {
            if (binding.drawerLayout.isDrawerOpen(binding.navView)) {
                binding.drawerLayout.closeDrawer(binding.navView)
            } else {
                binding.drawerLayout.openDrawer(binding.navView)
            }
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }

    private fun updateUI(state: MainUiState) {
        // Update toolbar title based on current state
        binding.toolbar.title = when {
            state.isRecording -> "Recording - ${state.sessionDuration}"
            state.isCalibrating -> "Calibrating..."
            else -> "Multi-Sensor Recording"
        }
        
        // Update system status in drawer header if needed
        // This could be implemented when nav_header_md3 is enhanced
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }

    private fun showErrorDialog(title: String, message: String) {
        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .show()
    }

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}