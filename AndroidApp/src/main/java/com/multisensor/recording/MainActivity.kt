package com.multisensor.recording

import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.multisensor.recording.databinding.ActivityMainFragmentsBinding
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.OnboardingActivity
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainFragmentsBinding
    private lateinit var viewModel: MainViewModel
    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var sharedPreferences: SharedPreferences

    @Inject
    lateinit var logger: Logger

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        sharedPreferences = getSharedPreferences("app_prefs", MODE_PRIVATE)
        
        // Check if onboarding should be shown
        if (OnboardingActivity.shouldShowOnboarding(sharedPreferences)) {
            startActivity(Intent(this, OnboardingActivity::class.java))
            finish()
            return
        }
        
        enableEdgeToEdge()

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
        try {

            val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
            val navController = navHostFragment.navController

            appBarConfiguration = AppBarConfiguration(
                setOf(
                    R.id.nav_recording, R.id.nav_devices,
                    R.id.nav_calibration, R.id.nav_files
                ),
                binding.drawerLayout
            )

            setupActionBarWithNavController(navController, appBarConfiguration)

            binding.navView.setupWithNavController(navController)

            binding.bottomNavigation.setupWithNavController(navController)

            binding.navView.setNavigationItemSelectedListener { menuItem ->
                when (menuItem.itemId) {
                    R.id.nav_settings -> {
                        startActivity(Intent(this, SettingsActivity::class.java))
                        binding.drawerLayout.closeDrawers()
                        true
                    }
                    // Hide "Coming Soon" items by not handling them or disable them
                    R.id.nav_network_config, 
                    R.id.nav_shimmer_config, 
                    R.id.nav_diagnostics, 
                    R.id.nav_about -> {
                        // These are disabled - do nothing
                        binding.drawerLayout.closeDrawers()
                        false
                    }
                    else -> {
                        val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
                        val navController = navHostFragment.navController
                        navController.navigate(menuItem.itemId)
                        binding.drawerLayout.closeDrawers()
                        true
                    }
                }
            }

            logger.info("Navigation setup completed successfully")
            
        } catch (e: Exception) {
            logger.error("Error during navigation setup", e)
            showErrorDialog("Navigation Error", "Failed to setup navigation: ${e.message}")
        }
    }

    private fun setupUI() {
        // Disable "Coming Soon" menu items to avoid user confusion
        val menu = binding.navView.menu
        menu.findItem(R.id.nav_network_config)?.isEnabled = false
        menu.findItem(R.id.nav_shimmer_config)?.isEnabled = false
        menu.findItem(R.id.nav_diagnostics)?.isEnabled = false
        menu.findItem(R.id.nav_about)?.isEnabled = false
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
        binding.toolbar.title = when {
            state.isRecording -> "Recording - ${state.sessionDuration}"
            state.isCalibrating -> "Calibrating..."
            else -> "Multi-Sensor Recording"
        }

        // Lock orientation during recording to prevent camera disruption
        requestedOrientation = if (state.isRecording) {
            ActivityInfo.SCREEN_ORIENTATION_LOCKED
        } else {
            ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
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