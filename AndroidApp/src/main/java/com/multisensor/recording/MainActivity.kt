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
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.SystemHealthStatus
import com.multisensor.recording.ui.SettingsActivity
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

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
    
    @Inject
    lateinit var logger: Logger

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
        initializeCamera()
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
        
        // Setup swipe-to-refresh
        setupSwipeToRefresh()
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
        
        // Setup preview layout switcher
        setupPreviewLayoutSwitcher()
    }

    private fun setupPreviewLayoutSwitcher() {
        var currentPreviewMode = PreviewMode.DUAL
        
        binding.previewLayoutToggle.setOnClickListener {
            try {
                currentPreviewMode = when (currentPreviewMode) {
                    PreviewMode.DUAL -> PreviewMode.RGB_ONLY
                    PreviewMode.RGB_ONLY -> PreviewMode.THERMAL_ONLY
                    PreviewMode.THERMAL_ONLY -> PreviewMode.DUAL
                }
                
                switchPreviewLayout(currentPreviewMode)
                
            } catch (e: Exception) {
                showError("Failed to switch preview layout: ${e.message}")
            }
        }
    }
    
    private fun switchPreviewLayout(mode: PreviewMode) {
        try {
            logger.info("Switching to preview mode: $mode")
            
            // Hide all layouts first
            binding.dualPreviewLayout.visibility = android.view.View.GONE
            binding.singleRgbLayout.visibility = android.view.View.GONE
            binding.singleThermalLayout.visibility = android.view.View.GONE
            
            when (mode) {
                PreviewMode.DUAL -> {
                    binding.dualPreviewLayout.visibility = android.view.View.VISIBLE
                    binding.previewLayoutToggle.text = "Dual View"
                    binding.previewLayoutToggle.setIconResource(R.drawable.ic_view_module)
                    
                    // Reinitialize camera surfaces if needed
                    val cameraTextureView = binding.cameraPreview
                    val thermalSurfaceView = binding.thermalPreview
                    viewModel.switchPreviewSurfaces(cameraTextureView, thermalSurfaceView)
                }
                
                PreviewMode.RGB_ONLY -> {
                    binding.singleRgbLayout.visibility = android.view.View.VISIBLE
                    binding.previewLayoutToggle.text = "RGB Only"
                    binding.previewLayoutToggle.setIconResource(R.drawable.ic_videocam)
                    
                    // Use fullscreen texture view for RGB
                    val cameraTextureView = binding.cameraPreviewFullscreen
                    viewModel.switchPreviewSurfaces(cameraTextureView, null)
                }
                
                PreviewMode.THERMAL_ONLY -> {
                    binding.singleThermalLayout.visibility = android.view.View.VISIBLE
                    binding.previewLayoutToggle.text = "Thermal Only"
                    binding.previewLayoutToggle.setIconResource(R.drawable.ic_thermostat)
                    
                    // Use fullscreen surface view for thermal
                    val thermalSurfaceView = binding.thermalPreviewFullscreen
                    viewModel.switchPreviewSurfaces(null, thermalSurfaceView)
                }
            }
            
            logger.info("Preview layout switched to: $mode")
            
        } catch (e: Exception) {
            logger.error("Failed to switch preview layout", e)
            showError("Failed to switch preview layout: ${e.message}")
        }
    }
    
    enum class PreviewMode {
        DUAL, RGB_ONLY, THERMAL_ONLY
    }

    private fun setupQuickActions() {
        // Calibration
        binding.calibrationButton.setOnClickListener {
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
                showDeviceConnectionDialog()
            } catch (e: Exception) {
                showError("Failed to open device management: ${e.message}")
            }
        }
        
        // Transfer files to PC
        binding.transferButton.setOnClickListener {
            try {
                viewModel.transferFilesToPC()
                showMessage("File transfer started")
            } catch (e: Exception) {
                showError("Failed to start file transfer: ${e.message}")
            }
        }
    }

    private fun setupFloatingActionButton() {
        binding.settingsFab.setOnClickListener {
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

    private fun initializeCamera() {
        try {
            // Initialize camera system with TextureView
            val cameraTextureView = binding.cameraPreview
            val thermalSurfaceView = binding.thermalPreview
            
            viewModel.initializeSystem(cameraTextureView, thermalSurfaceView)
            
            // Update status overlays
            binding.cameraStatusOverlay.text = "Initializing camera..."
            binding.thermalStatusOverlay.text = "Initializing thermal camera..."
            
            // Check RAW stage 3 availability after initialization
            checkRawStage3Availability()
            
            // Check thermal camera availability and update UI
            checkThermalCameraAvailability()
            
        } catch (e: Exception) {
            showError("Failed to initialize camera: ${e.message}")
            binding.cameraStatusOverlay.text = "Camera Error"
            binding.thermalStatusOverlay.text = "Thermal Error"
        }
    }

    /**
     * Check and display RAW stage 3 capture availability
     */
    private fun checkRawStage3Availability() {
        lifecycleScope.launch {
            try {
                val isAvailable = viewModel.checkRawStage3Availability()
                
                val message = if (isAvailable) {
                    "✓ RAW Stage 3 Capture: AVAILABLE"
                } else {
                    "✗ RAW Stage 3 Capture: NOT AVAILABLE"
                }
                
                // Show status in a toast for immediate user feedback
                Toast.makeText(this@MainActivity, message, Toast.LENGTH_LONG).show()
                
                logger.info("RAW Stage 3 availability check completed: $isAvailable")
                
            } catch (e: Exception) {
                logger.error("Error during RAW stage 3 availability check", e)
                Toast.makeText(this@MainActivity, "Error checking RAW capabilities", Toast.LENGTH_SHORT).show()
            }
        }
    }

    /**
     * Check thermal camera availability and notify user
     */
    private fun checkThermalCameraAvailability() {
        lifecycleScope.launch {
            try {
                val isAvailable = viewModel.checkThermalCameraAvailability()
                
                val message = if (isAvailable) {
                    "✓ Topdon Thermal Camera: AVAILABLE"
                } else {
                    "✗ Topdon Thermal Camera: NOT AVAILABLE"
                }
                
                // Show status in a toast for immediate user feedback
                Toast.makeText(this@MainActivity, message, Toast.LENGTH_LONG).show()
                
                logger.info("Thermal camera availability check completed: $isAvailable")
                
            } catch (e: Exception) {
                logger.error("Error during thermal camera availability check", e)
                Toast.makeText(this@MainActivity, "Error checking thermal camera", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun updateUI(uiState: MainUiState) {
        // Update recording controls
        updateRecordingControls(uiState)
        
        // Update device status indicators
        updateDeviceStatusIndicators(uiState)
        
        // Update camera status overlay
        updateCameraStatusOverlay(uiState)
        
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
        binding.recordingStatus.text = when {
            uiState.isRecording -> "Recording in progress..."
            uiState.canStartRecording -> "Ready to record"
            else -> "Cannot record - check connections"
        }
    }

    private fun updateDeviceStatusIndicators(uiState: MainUiState) {
        // Update device status chips with connection status
        updateStatusChip(binding.pcStatusChip, "PC", uiState.isPcConnected)
        updateStatusChip(binding.shimmerStatusChip, "Shimmer", uiState.isShimmerConnected)
        updateStatusChip(binding.thermalStatusChip, "Thermal", uiState.isThermalConnected)
        updateStatusChip(binding.networkStatusChip, "Network", uiState.isNetworkConnected)
    }

    private fun updateCameraStatusOverlay(uiState: MainUiState) {
        // Update RGB camera status overlay for both dual and single view
        val rgbStatusText = when {
            uiState.isCameraConnected -> {
                if (uiState.isRecording) "Recording..." else "Ready"
            }
            uiState.isLoadingPermissions -> "Initializing..."
            else -> "Camera Error"
        }
        
        binding.cameraStatusOverlay.text = rgbStatusText
        binding.cameraStatusOverlay.visibility = if (uiState.isCameraConnected) android.view.View.GONE else android.view.View.VISIBLE
        
        // Update fullscreen RGB status overlay
        try {
            binding.cameraStatusOverlayFullscreen.text = rgbStatusText
            binding.cameraStatusOverlayFullscreen.visibility = if (uiState.isCameraConnected) android.view.View.GONE else android.view.View.VISIBLE
        } catch (e: Exception) {
            // Ignore if fullscreen view not inflated yet
        }
        
        // Update thermal camera status overlay for both dual and single view
        val thermalStatusText = when {
            uiState.isThermalConnected -> {
                if (uiState.isRecording) "Recording..." else "Ready"
            }
            uiState.isLoadingPermissions -> "Initializing..."
            else -> "Thermal Camera Error"
        }
        
        binding.thermalStatusOverlay.text = thermalStatusText
        binding.thermalStatusOverlay.visibility = if (uiState.isThermalConnected) android.view.View.GONE else android.view.View.VISIBLE
        
        // Update fullscreen thermal status overlay
        try {
            binding.thermalStatusOverlayFullscreen.text = thermalStatusText
            binding.thermalStatusOverlayFullscreen.visibility = if (uiState.isThermalConnected) android.view.View.GONE else android.view.View.VISIBLE
        } catch (e: Exception) {
            // Ignore if fullscreen view not inflated yet
        }
    }
    
    private fun updateStatusChip(chip: com.google.android.material.chip.Chip, deviceName: String, isConnected: Boolean) {
        chip.text = "$deviceName: ${if (isConnected) "Connected" else "Disconnected"}"
        chip.isChecked = isConnected
    }

    private fun updateStorageInfo(uiState: MainUiState) {
        val usedPercentage = uiState.storageUsagePercentage
        binding.storageProgress.progress = usedPercentage
        binding.storageLabel.text = "${formatBytes(uiState.storageAvailable)} available (${uiState.sessionCount} sessions)"
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

    /**
     * Setup swipe-to-refresh functionality for system status updates
     */
    private fun setupSwipeToRefresh() {
        // Add a SwipeRefreshLayout to the status card programmatically
        binding.statusCard.setOnClickListener {
            refreshSystemStatus()
        }
        
        // Set up long-press listener for manual refresh trigger
        binding.statusCard.setOnLongClickListener {
            refreshSystemStatus()
            Toast.makeText(this, "Refreshing system status...", Toast.LENGTH_SHORT).show()
            true
        }
    }
    
    /**
     * Refresh system status by re-checking all device connections
     */
    private fun refreshSystemStatus() {
        lifecycleScope.launch {
            try {
                // Update UI to show refresh in progress
                binding.loadingProgressBar.visibility = android.view.View.VISIBLE
                
                // Trigger system status refresh in ViewModel
                viewModel.refreshSystemStatus()
                
                // Brief delay to show user that refresh happened
                delay(500)
                
                // Hide loading indicator
                binding.loadingProgressBar.visibility = android.view.View.GONE
                
                logger.info("System status refresh completed")
                
            } catch (e: Exception) {
                logger.error("Error during system status refresh", e)
                showError("Failed to refresh system status: ${e.message}")
                binding.loadingProgressBar.visibility = android.view.View.GONE
            }
        }
    }
    
    /**
     * Show device connection dialog for Bluetooth devices (primarily Shimmer)
     */
    private fun showDeviceConnectionDialog() {
        val options = arrayOf(
            "Connect Shimmer Device (Bluetooth)",
            "Disconnect Shimmer Device", 
            "Check USB Devices",
            "Refresh System Status"
        )
        
        AlertDialog.Builder(this)
            .setTitle("Device Management")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> showShimmerConnectionDialog()
                    1 -> disconnectShimmerDevice()
                    2 -> checkUsbDevices()
                    3 -> refreshSystemStatus()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    /**
     * Show Shimmer device connection dialog with Bluetooth options
     */
    private fun showShimmerConnectionDialog() {
        val connectionOptions = arrayOf(
            "Scan for Shimmer Devices",
            "Connect to Known Device", 
            "Enter MAC Address Manually",
            "Pair New Device"
        )
        
        AlertDialog.Builder(this)
            .setTitle("Shimmer Bluetooth Connection")
            .setItems(connectionOptions) { _, which ->
                when (which) {
                    0 -> scanForShimmerDevices()
                    1 -> showKnownShimmerDevices()
                    2 -> showManualMacEntryDialog()
                    3 -> showBluetoothPairingDialog()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    /**
     * Scan for available Shimmer devices via Bluetooth
     */
    private fun scanForShimmerDevices() {
        lifecycleScope.launch {
            try {
                showMessage("Scanning for Shimmer devices...")
                binding.loadingProgressBar.visibility = android.view.View.VISIBLE
                
                // Use ViewModel to perform Bluetooth scan
                viewModel.scanForShimmerDevicesEnhanced { devices ->
                    binding.loadingProgressBar.visibility = android.view.View.GONE
                    
                    if (devices.isEmpty()) {
                        showMessage("No Shimmer devices found. Make sure device is in pairing mode.")
                    } else {
                        showShimmerDeviceList(devices)
                    }
                }
                
            } catch (e: Exception) {
                logger.error("Error during Shimmer scan", e)
                showError("Failed to scan for devices: ${e.message}")
                binding.loadingProgressBar.visibility = android.view.View.GONE
            }
        }
    }
    
    /**
     * Show list of discovered Shimmer devices for selection
     */
    private fun showShimmerDeviceList(devices: List<Pair<String, String>>) {
        val deviceNames = devices.map { "${it.second} (${it.first})" }.toTypedArray()
        
        AlertDialog.Builder(this)
            .setTitle("Select Shimmer Device")
            .setItems(deviceNames) { _, which ->
                val (macAddress, deviceName) = devices[which]
                connectShimmerDevice(macAddress, deviceName)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    /**
     * Show list of previously connected Shimmer devices
     */
    private fun showKnownShimmerDevices() {
        lifecycleScope.launch {
            try {
                val knownDevices = viewModel.getKnownShimmerDevices()
                
                if (knownDevices.isEmpty()) {
                    showMessage("No previously connected devices found.")
                    return@launch
                }
                
                showShimmerDeviceList(knownDevices)
                
            } catch (e: Exception) {
                logger.error("Error getting known devices", e)
                showError("Failed to get known devices: ${e.message}")
            }
        }
    }
    
    /**
     * Show dialog for manual MAC address entry
     */
    private fun showManualMacEntryDialog() {
        val input = android.widget.EditText(this)
        input.hint = "00:06:66:68:XX:XX"
        input.inputType = android.text.InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS
        
        AlertDialog.Builder(this)
            .setTitle("Enter Shimmer MAC Address")
            .setView(input)
            .setPositiveButton("Connect") { _, _ ->
                val macAddress = input.text.toString().trim()
                if (isValidMacAddress(macAddress)) {
                    connectShimmerDevice(macAddress, "Shimmer_Manual")
                } else {
                    showError("Invalid MAC address format")
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    /**
     * Show Bluetooth pairing instructions dialog
     */
    private fun showBluetoothPairingDialog() {
        AlertDialog.Builder(this)
            .setTitle("Pair New Shimmer Device")
            .setMessage("""
                To pair a new Shimmer device:
                
                1. Turn on the Shimmer device
                2. Press and hold the power button until LED flashes blue
                3. Go to Android Settings > Bluetooth
                4. Scan for devices and pair with "Shimmer_XXXX"
                5. Return to this app and scan for devices
                
                Make sure Bluetooth is enabled on this device.
            """.trimIndent())
            .setPositiveButton("Open Bluetooth Settings") { _, _ ->
                val intent = Intent(android.provider.Settings.ACTION_BLUETOOTH_SETTINGS)
                startActivity(intent)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    /**
     * Connect to specific Shimmer device
     */
    private fun connectShimmerDevice(macAddress: String, deviceName: String) {
        lifecycleScope.launch {
            try {
                showMessage("Connecting to $deviceName...")
                binding.loadingProgressBar.visibility = android.view.View.VISIBLE
                
                viewModel.connectShimmerDevice(macAddress, deviceName, com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC) { success ->
                    binding.loadingProgressBar.visibility = android.view.View.GONE
                    
                    val message = if (success) {
                        "Successfully connected to $deviceName"
                    } else {
                        "Failed to connect to $deviceName. Check device is powered on and paired."
                    }
                    
                    showMessage(message)
                }
                
            } catch (e: Exception) {
                logger.error("Error connecting to Shimmer device", e)
                showError("Connection failed: ${e.message}")
                binding.loadingProgressBar.visibility = android.view.View.GONE
            }
        }
    }
    
    /**
     * Disconnect from Shimmer device
     */
    private fun disconnectShimmerDevice() {
        lifecycleScope.launch {
            try {
                viewModel.disconnectShimmerDevice("shimmer_device_id") { success ->
                    val message = if (success) {
                        "Shimmer device disconnected"
                    } else {
                        "Failed to disconnect device"
                    }
                    showMessage(message)
                }
                
            } catch (e: Exception) {
                logger.error("Error disconnecting Shimmer device", e)
                showError("Disconnect failed: ${e.message}")
            }
        }
    }
    
    /**
     * Check USB devices and show status
     */
    private fun checkUsbDevices() {
        lifecycleScope.launch {
            try {
                val thermalAvailable = viewModel.checkThermalCameraAvailability()
                
                val message = if (thermalAvailable) {
                    "✓ Topdon Thermal Camera: Connected"
                } else {
                    "✗ Topdon Thermal Camera: Not detected"
                }
                
                showMessage(message)
                
            } catch (e: Exception) {
                logger.error("Error checking USB devices", e)
                showError("USB check failed: ${e.message}")
            }
        }
    }
    
    /**
     * Validate MAC address format
     */
    private fun isValidMacAddress(mac: String): Boolean {
        val macPattern = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$".toRegex()
        return macPattern.matches(mac)
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(error: String) {
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        android.util.Log.e("MainActivityMD3", error)
    }
}