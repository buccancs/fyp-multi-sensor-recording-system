package com.multisensor.recording

import android.os.Bundle
import android.view.MenuItem
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.navigation.NavigationView
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.multisensor.recording.databinding.ActivityMainSimplifiedBinding
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.ui.util.NavigationUtils
import dagger.hilt.android.AndroidEntryPoint

/**
 * Simplified MainActivity with clean navigation architecture
 * 
 * This replaces the complex 1600+ line MainActivity with a clean,
 * navigation-based architecture focusing on simplicity and usability.
 */
@AndroidEntryPoint
class SimplifiedMainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

    private lateinit var binding: ActivityMainSimplifiedBinding
    private lateinit var appBarConfiguration: AppBarConfiguration

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        binding = ActivityMainSimplifiedBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupNavigation()
    }

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.title = "Multi-Sensor Recording"
    }

    private fun setupNavigation() {
        val navController = findNavController(R.id.nav_host_fragment)
        
        // Setup app bar configuration with drawer layout
        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.nav_recording,
                R.id.nav_devices,
                R.id.nav_calibration,
                R.id.nav_files
            ),
            binding.drawerLayout
        )
        
        // Setup action bar with navigation controller
        setupActionBarWithNavController(navController, appBarConfiguration)
        
        // Setup navigation drawer
        binding.navView.setupWithNavController(navController)
        binding.navView.setNavigationItemSelectedListener(this)
        
        // Setup bottom navigation
        binding.bottomNavigation.setupWithNavController(navController)
        
        // Setup drawer toggle
        val toggle = ActionBarDrawerToggle(
            this,
            binding.drawerLayout,
            binding.toolbar,
            R.string.nav_header_desc,
            R.string.nav_header_desc
        )
        binding.drawerLayout.addDrawerListener(toggle)
        toggle.syncState()
    }

    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        
        // Use NavigationUtils for main navigation items
        val handled = NavigationUtils.handleDrawerNavigation(navController, item.itemId)
        
        if (!handled) {
            // Handle non-navigation items (settings, tools, etc.)
            when (item.itemId) {
                R.id.nav_settings -> {
                    NavigationUtils.launchActivity(this, SettingsActivity::class.java)
                }
                R.id.nav_network -> {
                    showNetworkConfiguration()
                }
                R.id.nav_shimmer -> {
                    showShimmerConfiguration()
                }
                R.id.nav_sync_test -> {
                    showSyncTests()
                }
                R.id.nav_about -> {
                    showAbout()
                }
            }
        }
        
        binding.drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    private fun showNetworkConfiguration() {
        android.app.AlertDialog.Builder(this)
            .setTitle("Network Configuration")
            .setMessage(
                "Network Settings:\n\n" +
                "• PC Connection: Socket-based communication\n" +
                "• Default Port: 8080 (command channel)\n" +
                "• Preview Streams: 8081-8082\n" +
                "• Auto-discovery: Enabled\n\n" +
                "Advanced network configuration will be available in future updates."
            )
            .setPositiveButton("OK", null)
            .show()
    }

    private fun showShimmerConfiguration() {
        android.app.AlertDialog.Builder(this)
            .setTitle("Shimmer Configuration")
            .setMessage(
                "Shimmer GSR+ Settings:\n\n" +
                "• Bluetooth Connection: Auto-detect\n" +
                "• Sampling Rate: 51.2 Hz (default)\n" +
                "• Sensors: GSR, PPG, Accelerometer\n" +
                "• Data Format: CSV with timestamps\n\n" +
                "Device-specific configuration available after connection."
            )
            .setPositiveButton("OK", null)
            .show()
    }

    private fun showSyncTests() {
        android.app.AlertDialog.Builder(this)
            .setTitle("Synchronization Tests")
            .setMessage(
                "Sync Testing Features:\n\n" +
                "• Clock synchronization between devices\n" +
                "• Latency measurement and compensation\n" +
                "• Timestamp alignment validation\n" +
                "• Multi-device coordination tests\n\n" +
                "Comprehensive sync testing tools coming soon."
            )
            .setPositiveButton("OK", null)
            .show()
    }

    private fun showAbout() {
        android.app.AlertDialog.Builder(this)
            .setTitle("About Multi-Sensor Recording System")
            .setMessage(
                "Multi-Sensor Recording System\n" +
                "Navigation Architecture v2.0\n\n" +
                "Features:\n" +
                "• Clean fragment-based navigation\n" +
                "• Simplified user interface design\n" +
                "• Enhanced maintainability\n" +
                "• Modern Android architecture\n\n" +
                "Focus: Simplicity, cleanliness, and maintainability\n" +
                "Built with Kotlin, Navigation Component, and Material Design"
            )
            .setPositiveButton("OK", null)
            .show()
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }

    @Deprecated("Use onBackPressedDispatcher instead")
    override fun onBackPressed() {
        if (binding.drawerLayout.isDrawerOpen(GravityCompat.START)) {
            binding.drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            onBackPressedDispatcher.onBackPressed()
        }
    }
}