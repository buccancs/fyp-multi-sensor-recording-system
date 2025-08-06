package com.multisensor.recording.ui

import android.Manifest
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.tabs.TabLayoutMediator
import com.multisensor.recording.MainActivity
import com.multisensor.recording.databinding.ActivityOnboardingBinding
import com.multisensor.recording.ui.components.OnboardingAdapter
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class OnboardingActivity : AppCompatActivity() {

    private lateinit var binding: ActivityOnboardingBinding
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var onboardingAdapter: OnboardingAdapter

    private val requiredPermissions = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.BLUETOOTH_SCAN,
        Manifest.permission.BLUETOOTH_CONNECT
    )

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        updatePermissionStatus()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOnboardingBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sharedPreferences = getSharedPreferences("app_prefs", MODE_PRIVATE)

        setupViewPager()
        setupButtons()
        updatePermissionStatus()
    }

    private fun setupViewPager() {
        onboardingAdapter = OnboardingAdapter(this)
        binding.viewPager.adapter = onboardingAdapter

        TabLayoutMediator(binding.tabLayout, binding.viewPager) { _, _ ->

        }.attach()

        binding.viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                super.onPageSelected(position)
                updateButtonsForPage(position)
            }
        })
    }

    private fun setupButtons() {
        binding.btnSkip.setOnClickListener {
            finishOnboarding()
        }

        binding.btnNext.setOnClickListener {
            val currentItem = binding.viewPager.currentItem
            if (currentItem < onboardingAdapter.itemCount - 1) {
                binding.viewPager.currentItem = currentItem + 1
            } else {
                handleGetStarted()
            }
        }

        binding.btnRequestPermissions.setOnClickListener {
            requestPermissions()
        }

        binding.btnOpenSettings.setOnClickListener {
            openAppSettings()
        }
    }

    private fun updateButtonsForPage(position: Int) {
        when (position) {
            0, 1 -> {
                binding.btnNext.text = "Next"
                binding.btnRequestPermissions.visibility = android.view.View.GONE
                binding.btnOpenSettings.visibility = android.view.View.GONE
            }
            2 -> {
                binding.btnNext.text = "Get Started"
                updatePermissionStatus()
            }
        }
    }

    private fun updatePermissionStatus() {
        val allPermissionsGranted = requiredPermissions.all { permission ->
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
        }

        if (binding.viewPager.currentItem == 2) {
            binding.btnRequestPermissions.visibility = 
                if (allPermissionsGranted) android.view.View.GONE else android.view.View.VISIBLE
            binding.btnOpenSettings.visibility = android.view.View.VISIBLE
        }
    }

    private fun requestPermissions() {
        permissionLauncher.launch(requiredPermissions)
    }

    private fun openAppSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", packageName, null)
        }
        startActivity(intent)
    }

    private fun handleGetStarted() {
        val allPermissionsGranted = requiredPermissions.all { permission ->
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
        }

        if (allPermissionsGranted) {
            finishOnboarding()
        } else {

            androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Permissions Required")
                .setMessage("Some permissions are still missing. The app may not function properly without them. You can grant them later in Settings.")
                .setPositiveButton("Continue Anyway") { _, _ -> 
                    finishOnboarding() 
                }
                .setNegativeButton("Grant Permissions") { _, _ -> 
                    requestPermissions() 
                }
                .show()
        }
    }

    private fun finishOnboarding() {
        sharedPreferences.edit()
            .putBoolean("onboarding_completed", true)
            .apply()

        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    companion object {
        fun shouldShowOnboarding(sharedPreferences: SharedPreferences): Boolean {
            return !sharedPreferences.getBoolean("onboarding_completed", false)
        }
    }
}