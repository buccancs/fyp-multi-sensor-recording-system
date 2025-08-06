package com.multisensor.recording

import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.widget.Toast
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
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
import com.multisensor.recording.ui.MainViewModelRefactored
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.ui.compose.navigation.MainComposeNavigation
import com.multisensor.recording.ui.theme.MultiSensorTheme
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainFragmentsBinding
    private lateinit var viewModel: MainViewModelRefactored
    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var sharedPreferences: SharedPreferences

    @Inject
    lateinit var logger: Logger

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sharedPreferences = getSharedPreferences("app_prefs", MODE_PRIVATE)

        // TODO: Re-enable onboarding after Compose migration
        // if (OnboardingActivity.shouldShowOnboarding(sharedPreferences)) {
        //     startActivity(Intent(this, OnboardingActivity::class.java))
        //     finish()
        //     return
        // }

        enableEdgeToEdge()

        // Check if user wants to use the new Compose UI
        val useComposeUI = sharedPreferences.getBoolean("use_compose_ui", true) // Default to true for testing

        if (useComposeUI) {
            initializeComposeUI()
        } else {
            initializeFragmentUI()
        }
    }

    private fun initializeComposeUI() {
        try {
            viewModel = ViewModelProvider(this)[MainViewModelRefactored::class.java]
            
            setContent {
                MultiSensorTheme {
                    Surface(
                        modifier = Modifier.fillMaxSize(),
                        color = MaterialTheme.colorScheme.background
                    ) {
                        MainComposeNavigation()
                    }
                }
            }

            logger.info("MainActivity initialized with Compose UI")

        } catch (e: SecurityException) {
            logger.error("Permission error during MainActivity Compose initialization: ${e.message}", e)
            showErrorDialog("Permission Error", "Application requires additional permissions: ${e.message}")
        } catch (e: IllegalStateException) {
            logger.error("Invalid state during MainActivity Compose initialization: ${e.message}", e)
            showErrorDialog("State Error", "Failed to initialize application state: ${e.message}")
        } catch (e: RuntimeException) {
            logger.error("Runtime error during MainActivity Compose initialization: ${e.message}", e)
            showErrorDialog("Initialization Error", "Failed to initialize the application: ${e.message}")
        }
    }

    private fun initializeFragmentUI() {
        binding = ActivityMainFragmentsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        try {
            viewModel = ViewModelProvider(this)[MainViewModelRefactored::class.java]

            setupNavigation()
            setupUI()
            observeViewModel()

            logger.info("MainActivity initialized with fragment architecture")

        } catch (e: SecurityException) {
            logger.error("Permission error during MainActivity initialization: ${e.message}", e)
            showErrorDialog("Permission Error", "Application requires additional permissions: ${e.message}")
        } catch (e: IllegalStateException) {
            logger.error("Invalid state during MainActivity initialization: ${e.message}", e)
            showErrorDialog("State Error", "Failed to initialize application state: ${e.message}")
        } catch (e: RuntimeException) {
            logger.error("Runtime error during MainActivity initialization: ${e.message}", e)
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

                    R.id.nav_network_config, 
                    R.id.nav_shimmer_config, 
                    R.id.nav_diagnostics, 
                    R.id.nav_about -> {

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

        } catch (e: SecurityException) {
            logger.error("Permission error during navigation setup: ${e.message}", e)
            showErrorDialog("Permission Error", "Failed to setup navigation permissions: ${e.message}")
        } catch (e: IllegalStateException) {
            logger.error("Invalid state during navigation setup: ${e.message}", e)
            showErrorDialog("Navigation State Error", "Failed to setup navigation state: ${e.message}")
        } catch (e: RuntimeException) {
            logger.error("Runtime error during navigation setup: ${e.message}", e)
            showErrorDialog("Navigation Error", "Failed to setup navigation: ${e.message}")
        }
    }

    private fun setupUI() {

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

        requestedOrientation = if (state.isRecording) {
            ActivityInfo.SCREEN_ORIENTATION_LOCKED
        } else {
            ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        // Only handle fragment navigation if using fragment UI
        val useComposeUI = sharedPreferences.getBoolean("use_compose_ui", true)
        return if (!useComposeUI) {
            val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
            val navController = navHostFragment.navController
            navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
        } else {
            super.onSupportNavigateUp()
        }
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