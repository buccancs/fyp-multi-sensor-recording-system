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
        
        when (item.itemId) {
            R.id.nav_recording -> navController.navigate(R.id.nav_recording)
            R.id.nav_devices -> navController.navigate(R.id.nav_devices)
            R.id.nav_calibration -> navController.navigate(R.id.nav_calibration)
            R.id.nav_files -> navController.navigate(R.id.nav_files)
            R.id.nav_settings -> {
                // Launch settings activity
                // startActivity(Intent(this, SettingsActivity::class.java))
            }
            R.id.nav_network -> {
                // Launch network config activity
                // startActivity(Intent(this, NetworkConfigActivity::class.java))
            }
            R.id.nav_shimmer -> {
                // Launch shimmer config activity
                // startActivity(Intent(this, ShimmerConfigActivity::class.java))
            }
            R.id.nav_sync_test -> {
                // Show sync tests
                showSyncTests()
            }
            R.id.nav_about -> {
                showAbout()
            }
        }
        
        binding.drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    private fun showSyncTests() {
        // Placeholder for sync tests
        android.app.AlertDialog.Builder(this)
            .setTitle("Sync Tests")
            .setMessage("Sync testing functionality coming soon")
            .setPositiveButton("OK", null)
            .show()
    }

    private fun showAbout() {
        android.app.AlertDialog.Builder(this)
            .setTitle("About")
            .setMessage(
                "Multi-Sensor Recording System\n" +
                "Simplified Navigation Architecture\n" +
                "Version 1.0.0\n\n" +
                "Focus: Simplicity and Cleanliness"
            )
            .setPositiveButton("OK", null)
            .show()
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }

    override fun onBackPressed() {
        if (binding.drawerLayout.isDrawerOpen(GravityCompat.START)) {
            binding.drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}