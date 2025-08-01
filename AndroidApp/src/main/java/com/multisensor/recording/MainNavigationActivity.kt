package com.multisensor.recording

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.app.Dialog
import android.content.BroadcastReceiver
import android.content.Context
import android.content.DialogInterface
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.graphics.Color
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.media.MediaActionSound
import android.os.BatteryManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.Lifecycle
import androidx.viewpager2.widget.ViewPager2
import kotlinx.coroutines.launch
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.multisensor.recording.databinding.ActivityMainNavigationBinding
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.SessionDisplayInfo
import com.multisensor.recording.ui.adapters.MainNavigationAdapter
import com.multisensor.recording.util.AllAndroidPermissions
import com.multisensor.recording.util.PermissionTool
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.calibration.SyncClockManager
import com.multisensor.recording.managers.PermissionManager
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.managers.UsbDeviceManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

// shimmer ui components imports
import com.shimmerresearch.android.guiUtilities.ShimmerBluetoothDialog
import com.shimmerresearch.android.guiUtilities.ShimmerDialogConfigurations
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid

// centralized logging
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW

// hand segmentation
import com.multisensor.recording.handsegmentation.HandSegmentationManager

/**
 * Navigation-enabled main activity for multi-sensor recording system
 * 
 * This version of MainActivity uses a fragment-based navigation architecture
 * with TabLayout and ViewPager2 for organized UI management.
 */
@AndroidEntryPoint
class MainNavigationActivity : AppCompatActivity(),
    PermissionManager.PermissionCallback,
    ShimmerManager.ShimmerCallback,
    UsbDeviceManager.UsbDeviceCallback,
    HandSegmentationManager.HandSegmentationListener {
    
    private lateinit var binding: ActivityMainNavigationBinding
    private lateinit var viewModel: MainViewModel
    private lateinit var navigationAdapter: MainNavigationAdapter

    @Inject
    lateinit var calibrationCaptureManager: CalibrationCaptureManager

    @Inject
    lateinit var syncClockManager: SyncClockManager

    @Inject
    lateinit var permissionManager: PermissionManager

    @Inject
    lateinit var shimmerManager: ShimmerManager

    @Inject
    lateinit var usbDeviceManager: UsbDeviceManager

    @Inject
    lateinit var handSegmentationManager: HandSegmentationManager

    private var selectedShimmerAddress: String? = null
    private var selectedShimmerName: String? = null
    private var preferredBtType: ShimmerBluetoothManagerAndroid.BT_TYPE = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC

    // Modern Activity Result API for Shimmer device selection
    private val shimmerDeviceSelectionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        AppLogger.logMethodEntry("MainNavigationActivity", "shimmerDeviceSelectionLauncher", "resultCode=${result.resultCode}")
        
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            selectedShimmerAddress = result.data?.getStringExtra(ShimmerBluetoothDialog.EXTRA_DEVICE_ADDRESS)
            selectedShimmerName = result.data?.getStringExtra(ShimmerBluetoothDialog.EXTRA_DEVICE_NAME)
            logI("Shimmer device selected: Address=$selectedShimmerAddress, Name=$selectedShimmerName")
            showBtTypeConnectionOption()
        } else {
            logI("Shimmer device selection cancelled")
            Toast.makeText(this, "Device selection cancelled", Toast.LENGTH_SHORT).show()
        }
    }

    private var hasCheckedPermissionsOnStartup = false
    private var permissionRetryCount = 0
    private val maxPermissionRetries = 5

    // Status Display System
    private var currentBatteryLevel = -1
    private lateinit var mediaActionSound: MediaActionSound

    // Battery monitoring receiver
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == Intent.ACTION_BATTERY_CHANGED) {
                val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                if (level != -1 && scale != -1) {
                    currentBatteryLevel = (level * 100) / scale
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        AppLogger.logMethodEntry("MainNavigationActivity", "onCreate", "Initializing navigation activity")
        AppLogger.logMemoryUsage("MainNavigationActivity", "onCreate - start")
        super.onCreate(savedInstanceState)
        
        AppLogger.logLifecycle("MainNavigationActivity", "onCreate")
        logI("=== Multi-Sensor Recording Application Starting (Navigation Mode) ===")

        // Initialize view binding
        binding = ActivityMainNavigationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]

        // Setup navigation UI
        setupNavigationUI()

        // Setup status monitoring
        setupStatusMonitoring()

        // Observe ViewModel state
        observeViewModel()

        // Handle USB device attachment if launched by USB intent
        handleUsbDeviceIntent(intent)

        logI("Navigation activity initialization completed")
    }

    private fun setupNavigationUI() {
        // Initialize ViewPager2 adapter
        navigationAdapter = MainNavigationAdapter(this)
        binding.viewPager.adapter = navigationAdapter

        // Connect TabLayout with ViewPager2
        TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
            tab.text = navigationAdapter.getTabTitle(position)
            // Tab icons are set in the layout
        }.attach()

        // Set default tab
        binding.viewPager.currentItem = MainNavigationAdapter.TAB_RECORDING

        logI("Navigation UI setup completed")
    }

    private fun setupStatusMonitoring() {
        // Initialize MediaActionSound for calibration feedback
        mediaActionSound = MediaActionSound()
        mediaActionSound.load(MediaActionSound.SHUTTER_CLICK)

        // Register battery receiver
        val batteryFilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        registerReceiver(batteryReceiver, batteryFilter)

        // Get initial battery level
        val batteryIntent = registerReceiver(null, batteryFilter)
        batteryIntent?.let { intent ->
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            if (level != -1 && scale != -1) {
                currentBatteryLevel = (level * 100) / scale
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleUsbDeviceIntent(intent)
    }

    private fun handleUsbDeviceIntent(intent: Intent) {
        when (intent.action) {
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                val device: UsbDevice? = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                }
                device?.let { usbDevice ->
                    if (isSupportedTopdonDevice(usbDevice)) {
                        Toast.makeText(this, "Topdon Thermal Camera Connected!", Toast.LENGTH_LONG).show()
                        binding.statusText.text = "Topdon thermal camera connected - Ready for recording"
                        
                        if (areAllPermissionsGranted()) {
                            initializeRecordingSystem()
                        }
                    }
                }
            }
        }
    }

    private fun isSupportedTopdonDevice(device: UsbDevice): Boolean {
        val vendorId = device.vendorId
        val productId = device.productId
        val topdonVendorId = 0x0BDA
        val supportedProductIds = intArrayOf(0x3901, 0x5840, 0x5830, 0x5838)
        return vendorId == topdonVendorId && supportedProductIds.contains(productId)
    }

    private fun areAllPermissionsGranted(): Boolean =
        AllAndroidPermissions.getDangerousPermissions().all { permission ->
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
        }

    override fun onResume() {
        AppLogger.logMethodEntry("MainNavigationActivity", "onResume", "Activity resuming")
        super.onResume()

        if (!hasCheckedPermissionsOnStartup) {
            hasCheckedPermissionsOnStartup = true
            binding.root.post {
                checkPermissions()
            }
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateGlobalStatusFromState(state)
                }
            }
        }
    }

    private fun updateGlobalStatusFromState(state: com.multisensor.recording.ui.MainUiState) {
        // Update global status text in navigation activity
        binding.statusText.text = state.statusText

        // Handle error messages
        state.errorMessage?.let { errorMsg ->
            if (state.showErrorDialog) {
                Toast.makeText(this, errorMsg, Toast.LENGTH_LONG).show()
                viewModel.clearError()
            }
        }
    }

    private fun checkPermissions() {
        if (permissionManager.areAllPermissionsGranted(this)) {
            initializeRecordingSystem()
        } else {
            binding.statusText.text = "Requesting permissions..."
            permissionManager.requestPermissions(this, this)
        }
    }

    private fun initializeRecordingSystem() {
        // Initialize the recording system for use across fragments
        // For navigation mode, initialization is handled by the RecordingFragment
        // which has access to the TextureView
        try {
            binding.statusText.text = "System ready - Navigate to Recording tab to initialize cameras"
        } catch (e: Exception) {
            binding.statusText.text = "Initialization error: ${e.message}"
            logE("Recording system initialization failed", e)
        }
    }

    // Show BT type selection dialog
    private fun showBtTypeConnectionOption() {
        val alertDialog = AlertDialog.Builder(this).create()
        alertDialog.setCancelable(false)
        alertDialog.setMessage("Choose preferred Bluetooth type")

        alertDialog.setButton(Dialog.BUTTON_POSITIVE, "BT CLASSIC") { _, _ ->
            preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
            connectSelectedShimmerDevice()
        }

        alertDialog.setButton(Dialog.BUTTON_NEGATIVE, "BLE") { _, _ ->
            preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BLE
            connectSelectedShimmerDevice()
        }

        alertDialog.show()
    }

    private fun connectSelectedShimmerDevice() {
        selectedShimmerAddress?.let { address ->
            selectedShimmerName?.let { name ->
                binding.statusText.text = "Connecting to $name ($preferredBtType)..."
                Toast.makeText(this, "Connecting to $name via $preferredBtType", Toast.LENGTH_SHORT).show()
            }
        }
    }

    // ========== Menu Handling ==========

    override fun onCreateOptionsMenu(menu: android.view.Menu?): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: android.view.MenuItem): Boolean =
        when (item.itemId) {
            R.id.action_settings -> {
                val intent = Intent(this, com.multisensor.recording.ui.SettingsActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_network_config -> {
                val intent = Intent(this, com.multisensor.recording.ui.NetworkConfigActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_file_browser -> {
                val intent = Intent(this, com.multisensor.recording.ui.FileViewActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_shimmer_config -> {
                val intent = Intent(this, com.multisensor.recording.ui.ShimmerConfigActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_about -> {
                showAboutDialog()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }

    private fun showAboutDialog() {
        val aboutMessage = """
            Multi-Sensor Recording System (Navigation Mode)
            
            Version: 1.0.0
            Build: Navigation Architecture
            
            Features:
            • Fragment-based navigation
            • Organized UI sections
            • Shared state management
            • Comprehensive device support
            
            Developed with ❤️ for multi-sensor data collection
        """.trimIndent()

        AlertDialog.Builder(this)
            .setTitle("About Multi-Sensor Recording")
            .setMessage(aboutMessage)
            .setIcon(R.drawable.ic_multisensor_idle)
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .show()
    }

    override fun onDestroy() {
        super.onDestroy()

        // Cleanup resources
        try {
            unregisterReceiver(batteryReceiver)
        } catch (e: Exception) {
            logW("Battery receiver cleanup error: ${e.message}")
        }

        if (::mediaActionSound.isInitialized) {
            mediaActionSound.release()
        }

        handSegmentationManager.cleanup()
    }

    // ========== Interface Implementations ==========

    override fun onAllPermissionsGranted() {
        initializeRecordingSystem()
        binding.statusText.text = "All permissions granted - System ready"
    }

    override fun onPermissionsTemporarilyDenied(deniedPermissions: List<String>, grantedCount: Int, totalCount: Int) {
        binding.statusText.text = "Permissions: $grantedCount/$totalCount granted"
        Toast.makeText(this, "Some permissions denied. Check Devices tab for details.", Toast.LENGTH_LONG).show()
    }

    override fun onPermissionsPermanentlyDenied(deniedPermissions: List<String>) {
        binding.statusText.text = "Permissions required - Check Settings"
        Toast.makeText(this, "Please enable permissions in Settings", Toast.LENGTH_LONG).show()
    }

    override fun onDeviceSelected(address: String, name: String) {
        selectedShimmerAddress = address
        selectedShimmerName = name
        binding.statusText.text = "Shimmer device selected: $name"
    }

    override fun onDeviceSelectionCancelled() {
        Toast.makeText(this, "Device selection cancelled", Toast.LENGTH_SHORT).show()
    }

    override fun onConnectionStatusChanged(connected: Boolean) {
        val statusMessage = if (connected) "Shimmer device connected" else "Shimmer device disconnected"
        binding.statusText.text = statusMessage
        Toast.makeText(this, statusMessage, Toast.LENGTH_SHORT).show()
    }

    override fun onConfigurationComplete() {
        binding.statusText.text = "Shimmer configuration completed"
        Toast.makeText(this, "Shimmer configuration completed", Toast.LENGTH_SHORT).show()
    }

    override fun onSupportedDeviceAttached(device: UsbDevice) {
        binding.statusText.text = "Supported TOPDON device connected"
        Toast.makeText(this, "TOPDON device connected: ${device.deviceName}", Toast.LENGTH_SHORT).show()
    }

    override fun onUnsupportedDeviceAttached(device: UsbDevice) {
        Toast.makeText(this, "Unsupported USB device: ${device.deviceName}", Toast.LENGTH_SHORT).show()
    }

    override fun onDeviceDetached(device: UsbDevice) {
        binding.statusText.text = "USB device disconnected"
        Toast.makeText(this, "USB device disconnected: ${device.deviceName}", Toast.LENGTH_SHORT).show()
    }

    override fun onHandDetectionStatusChanged(isEnabled: Boolean, handsDetected: Int) {
        // Hand segmentation status updates can be handled by individual fragments if needed
    }

    override fun onDatasetProgress(totalSamples: Int, leftHands: Int, rightHands: Int) {
        // Dataset progress updates can be handled by individual fragments if needed
    }

    override fun onDatasetSaved(datasetPath: String, totalSamples: Int) {
        Toast.makeText(this, "Dataset saved: $totalSamples samples", Toast.LENGTH_LONG).show()
    }

    override fun onError(error: String) {
        binding.statusText.text = "Error: $error"
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
    }
}