package com.multisensor.recording

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.app.Dialog
import android.content.DialogInterface
import android.content.Intent
import android.content.pm.PackageManager
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Bundle
import android.os.Looper
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.util.AllAndroidPermissions
import com.multisensor.recording.util.PermissionTool
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

// Shimmer UI Components imports
import com.shimmerresearch.android.guiUtilities.ShimmerBluetoothDialog
import com.shimmerresearch.android.guiUtilities.ShimmerDialogConfigurations
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid

/**
 * Main activity for the Multi-Sensor Recording System.
 * Provides the primary user interface for controlling recording sessions,
 * viewing camera previews, and monitoring system status.
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    
    
    // Shimmer UI state management
    private var selectedShimmerAddress: String? = null
    private var selectedShimmerName: String? = null
    private var preferredBtType: ShimmerBluetoothManagerAndroid.BT_TYPE = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
    private var looper: Looper? = null
    
    // Enhanced permission handling using XXPermissions library
    private val permissionCallback = object : PermissionTool.PermissionCallback {
        override fun onAllGranted() {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] All permissions granted via XXPermissions")
            permissionRetryCount = 0 // Reset retry counter on success
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Reset permission retry counter to 0")
            initializeRecordingSystem()
            binding.statusText.text = "All permissions granted - System ready"
            updatePermissionButtonVisibility()
        }

        override fun onTemporarilyDenied(deniedPermissions: List<String>) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Permissions temporarily denied: ${deniedPermissions.size}")
            
            // Automatically retry temporarily denied permissions - keep showing dialogs until accepted
            if (deniedPermissions.isNotEmpty()) {
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Automatically retrying ${deniedPermissions.size} temporarily denied permissions")
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Current retry count: $permissionRetryCount / $maxPermissionRetries")
                
                if (permissionRetryCount < maxPermissionRetries) {
                    permissionRetryCount++
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] Incrementing retry count to: $permissionRetryCount")
                    
                    // Add a small delay to prevent immediate re-popup (better UX)
                    binding.root.postDelayed({
                        android.util.Log.d("MainActivity", "[DEBUG_LOG] Launching persistent retry #$permissionRetryCount for temporarily denied permissions")
                        binding.statusText.text = "Requesting remaining permissions... (Attempt $permissionRetryCount/$maxPermissionRetries)"
                        
                        // Retry with XXPermissions
                        PermissionTool.requestAllDangerousPermissions(this@MainActivity, this)
                    }, 1500) // 1.5 second delay for better user experience
                } else {
                    android.util.Log.w("MainActivity", "[DEBUG_LOG] Maximum retry attempts ($maxPermissionRetries) reached, falling back to manual request")
                    binding.statusText.text = "Maximum retry attempts reached - Please use the button to grant permissions"
                    showTemporaryDenialMessage(deniedPermissions, 0, deniedPermissions.size)
                }
            }
            updatePermissionButtonVisibility()
        }

        override fun onPermanentlyDeniedWithSettingsOpened(deniedPermissions: List<String>) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Permanently denied permissions, Settings opened: ${deniedPermissions.size}")
            binding.statusText.text = "Please enable permissions in Settings and return to the app"
            updatePermissionButtonVisibility()
        }

        override fun onPermanentlyDeniedWithoutSettings(deniedPermissions: List<String>) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Permanently denied permissions, Settings not opened: ${deniedPermissions.size}")
            binding.statusText.text = "Permissions required - Please enable in Settings or use the button to try again"
            updatePermissionButtonVisibility()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ===== APP STARTUP: onCreate() called =====")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onCreate() starting")
        
        // Initialize view binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        android.util.Log.d("MainActivity", "[DEBUG_LOG] View binding initialized and content view set")
        
        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ViewModel initialized")
        
        // Setup UI
        setupUI()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] UI setup completed")
        
        // Note: Permission checking moved to onResume() for better timing
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Permission checking will be done in onResume() for better timing")
        
        // Observe ViewModel state
        observeViewModel()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ViewModel observers set up")
        
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ===== APP STARTUP: onCreate() completed =====")
        
        // Handle USB device attachment if launched by USB intent
        handleUsbDeviceIntent(intent)
    }
    
    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        android.util.Log.d("MainActivity", "[DEBUG_LOG] onNewIntent() called")
        
        // Handle USB device attachment
        intent?.let { handleUsbDeviceIntent(it) }
    }
    
    /**
     * Handle USB device attachment intent
     * This method is called when the app is launched due to a Topdon device being connected
     */
    private fun handleUsbDeviceIntent(intent: Intent) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Handling USB device intent: ${intent.action}")
        
        when (intent.action) {
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                val device: UsbDevice? = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                device?.let { usbDevice ->
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] USB device attached:")
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] - Device name: ${usbDevice.deviceName}")
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] - Vendor ID: 0x${String.format("%04X", usbDevice.vendorId)}")
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] - Product ID: 0x${String.format("%04X", usbDevice.productId)}")
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] - Device class: ${usbDevice.deviceClass}")
                    
                    // Check if this is a supported Topdon thermal camera
                    if (isSupportedTopdonDevice(usbDevice)) {
                        android.util.Log.d("MainActivity", "[DEBUG_LOG] ✓ Supported Topdon thermal camera detected!")
                        
                        // Show user notification
                        Toast.makeText(
                            this,
                            "Topdon Thermal Camera Connected!\nDevice: ${usbDevice.deviceName}",
                            Toast.LENGTH_LONG
                        ).show()
                        
                        // Update status
                        binding.statusText.text = "Topdon thermal camera connected - Ready for recording"
                        
                        // Initialize thermal recorder if permissions are available
                        if (areAllPermissionsGranted()) {
                            android.util.Log.d("MainActivity", "[DEBUG_LOG] Permissions available, initializing thermal recorder")
                            initializeRecordingSystem()
                        } else {
                            android.util.Log.d("MainActivity", "[DEBUG_LOG] Permissions not available, requesting permissions first")
                            binding.statusText.text = "Thermal camera detected - Please grant permissions to continue"
                        }
                    } else {
                        android.util.Log.d("MainActivity", "[DEBUG_LOG] ⚠ USB device is not a supported Topdon thermal camera")
                        android.util.Log.d("MainActivity", "[DEBUG_LOG] Supported devices: VID=0x0BDA, PID=0x3901/0x5840/0x5830/0x5838")
                    }
                } ?: run {
                    android.util.Log.w("MainActivity", "[DEBUG_LOG] USB device attachment intent received but no device found")
                }
            }
            else -> {
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Intent action: ${intent.action} (not USB device attachment)")
            }
        }
    }
    
    /**
     * Check if the USB device is a supported Topdon thermal camera
     * Based on vendor ID and product ID matching ThermalRecorder configuration
     */
    private fun isSupportedTopdonDevice(device: UsbDevice): Boolean {
        val vendorId = device.vendorId
        val productId = device.productId
        
        // Topdon vendor ID (matches device_filter.xml and IRCamera library)
        val topdonVendorId = 0x0BDA
        
        // Supported product IDs (matches ThermalRecorder.kt)
        val supportedProductIds = intArrayOf(0x3901, 0x5840, 0x5830, 0x5838)
        
        val isSupported = vendorId == topdonVendorId && supportedProductIds.contains(productId)
        
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Device support check:")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Expected VID: 0x${String.format("%04X", topdonVendorId)}")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Actual VID: 0x${String.format("%04X", vendorId)}")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Expected PIDs: ${supportedProductIds.joinToString { "0x${String.format("%04X", it)}" }}")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Actual PID: 0x${String.format("%04X", productId)}")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Is supported: $isSupported")
        
        return isSupported
    }
    
    /**
     * Check if all required permissions are granted
     */
    private fun areAllPermissionsGranted(): Boolean {
        return AllAndroidPermissions.getDangerousPermissions().all { permission ->
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    override fun onStart() {
        super.onStart()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onStart() called")
    }
    
    private var hasCheckedPermissionsOnStartup = false
    private var permissionRetryCount = 0
    private val maxPermissionRetries = 5 // Prevent infinite loops while being persistent
    
    override fun onResume() {
        super.onResume()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onResume() called")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity is now fully visible and interactive")
        
        // Log current permission states for debugging
        logCurrentPermissionStates()
        
        // Check and request permissions on first resume (app startup)
        if (!hasCheckedPermissionsOnStartup) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] First onResume() - checking permissions for app startup")
            hasCheckedPermissionsOnStartup = true
            
            // Small delay to ensure activity is fully ready
            binding.root.post {
                android.util.Log.d("MainActivity", "[DEBUG_LOG] About to call checkPermissions() in onResume()")
                checkPermissions()
                android.util.Log.d("MainActivity", "[DEBUG_LOG] checkPermissions() call completed in onResume()")
            }
        } else {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Subsequent onResume() - skipping permission check")
        }
    }
    
    override fun onPause() {
        super.onPause()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onPause() called")
    }
    
    override fun onStop() {
        super.onStop()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onStop() called")
    }
    
    private fun logCurrentPermissionStates() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] === Current Permission States (XXPermissions) ===")
        
        val missingPermissions = PermissionTool.getMissingDangerousPermissions(this)
        val allPermissionsGranted = PermissionTool.areAllDangerousPermissionsGranted(this)
        
        android.util.Log.d("MainActivity", "[DEBUG_LOG] All permissions granted: $allPermissionsGranted")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Missing permissions count: ${missingPermissions.size}")
        
        if (missingPermissions.isNotEmpty()) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Missing permissions:")
            missingPermissions.forEach { permission ->
                val displayName = getPermissionDisplayName(permission)
                android.util.Log.d("MainActivity", "[DEBUG_LOG]   - $displayName ($permission)")
            }
            android.util.Log.d("MainActivity", "[DEBUG_LOG] ⚠ MISSING PERMISSIONS - Dialog should appear")
        } else {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] ✓ ALL PERMISSIONS GRANTED - No dialog needed")
        }
        
        android.util.Log.d("MainActivity", "[DEBUG_LOG] === End Permission States ===")
    }
    
    private fun setupUI() {
        // Setup recording control buttons
        binding.startRecordingButton.setOnClickListener {
            startRecording()
        }
        
        binding.stopRecordingButton.setOnClickListener {
            stopRecording()
        }
        
        binding.calibrationButton.setOnClickListener {
            runCalibration()
        }
        
        binding.requestPermissionsButton.setOnClickListener {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Manual permission request button clicked")
            requestPermissionsManually()
        }
        
        // Initially disable stop button
        binding.stopRecordingButton.isEnabled = false
    }
    
    private fun observeViewModel() {
        // Observe recording state
        viewModel.isRecording.observe(this) { isRecording ->
            updateRecordingUI(isRecording)
        }
        
        // Observe system status
        viewModel.systemStatus.observe(this) { status ->
            binding.statusText.text = status
        }
        
        // Observe error messages
        viewModel.errorMessage.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_LONG).show()
                viewModel.clearError()
            }
        }
        
        // Observe SessionInfo for enhanced CameraRecorder integration
        viewModel.currentSessionInfo.observe(this) { sessionInfo ->
            updateSessionInfoDisplay(sessionInfo)
        }
        
        // Observe recording mode configuration
        viewModel.recordVideoEnabled.observe(this) { enabled ->
            // TODO: Update video recording checkbox when UI is added
        }
        
        viewModel.captureRawEnabled.observe(this) { enabled ->
            // TODO: Update RAW capture checkbox when UI is added
        }
    }
    
    private fun checkPermissions() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Starting enhanced permission check with XXPermissions...")
        
        if (PermissionTool.areAllDangerousPermissionsGranted(this)) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] All permissions already granted, initializing system")
            initializeRecordingSystem()
        } else {
            val missingPermissions = PermissionTool.getMissingDangerousPermissions(this)
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Missing permissions count: ${missingPermissions.size}")
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Missing permissions: $missingPermissions")
            
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Requesting permissions via XXPermissions...")
            binding.statusText.text = "Requesting permissions..."
            
            // Use enhanced permission system
            PermissionTool.requestAllDangerousPermissions(this, permissionCallback)
        }
        
        // Update permission button visibility based on current permission status
        updatePermissionButtonVisibility()
    }
    
    
    private fun showTemporaryDenialMessage(temporarilyDenied: List<String>, grantedCount: Int, totalCount: Int) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Showing temporary denial message for ${temporarilyDenied.size} permissions")
        
        val message = "Some permissions were denied but can be requested again.\n\n" +
                "Denied permissions:\n" +
                temporarilyDenied.joinToString("\n") { "• ${getPermissionDisplayName(it)}" } +
                "\n\nYou can grant these permissions using the 'Request Permissions' button."
        
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        
        binding.statusText.text = "Permissions: $grantedCount/$totalCount granted - Some permissions denied"
        
        android.util.Log.i("MainActivity", "Temporary permission denial: ${temporarilyDenied.joinToString(", ")}")
    }
    
    
    private fun showPermanentlyDeniedMessage(permanentlyDenied: List<String>) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Showing permanently denied permissions message")
        
        val message = "Some permissions have been permanently denied. " +
                "Please enable them manually in Settings > Apps > Multi-Sensor Recording > Permissions.\n\n" +
                "Permanently denied permissions:\n" +
                permanentlyDenied.joinToString("\n") { "• ${getPermissionDisplayName(it)}" }
        
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        
        binding.statusText.text = "Permissions required - Please enable in Settings"
        
        // Log the permanently denied permissions
        android.util.Log.w("MainActivity", "Permanently denied permissions: ${permanentlyDenied.joinToString(", ")}")
    }
    
    private fun getPermissionDisplayName(permission: String): String {
        return when (permission) {
            Manifest.permission.CAMERA -> "Camera"
            Manifest.permission.RECORD_AUDIO -> "Microphone"
            Manifest.permission.ACCESS_FINE_LOCATION -> "Fine Location"
            Manifest.permission.ACCESS_COARSE_LOCATION -> "Coarse Location"
            Manifest.permission.READ_EXTERNAL_STORAGE -> "Read Storage"
            Manifest.permission.WRITE_EXTERNAL_STORAGE -> "Write Storage"
            Manifest.permission.READ_PHONE_STATE -> "Phone State"
            Manifest.permission.READ_CONTACTS -> "Contacts"
            Manifest.permission.SEND_SMS -> "Send SMS"
            else -> permission.substringAfterLast(".")
        }
    }
    
    private fun requestPermissionsManually() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Manual permission request initiated by user")
        
        // Reset the startup flag to allow permission checking again
        hasCheckedPermissionsOnStartup = false
        
        // Reset retry counter for fresh manual attempt
        permissionRetryCount = 0
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Reset permission retry counter to 0 for manual request")
        
        // Hide the button while processing
        binding.requestPermissionsButton.visibility = android.view.View.GONE
        binding.statusText.text = "Requesting permissions..."
        
        // Call the same permission checking logic
        checkPermissions()
    }
    
    private fun updatePermissionButtonVisibility() {
        val missingPermissions = PermissionTool.getMissingDangerousPermissions(this)
        
        if (missingPermissions.isNotEmpty()) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Showing permission request button - ${missingPermissions.size} permissions missing")
            binding.requestPermissionsButton.visibility = android.view.View.VISIBLE
        } else {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Hiding permission request button - all permissions granted")
            binding.requestPermissionsButton.visibility = android.view.View.GONE
        }
    }
    
    private fun initializeRecordingSystem() {
        // Get TextureView from layout for camera preview
        val textureView = binding.texturePreview
        
        // Initialize system with TextureView for enhanced CameraRecorder integration
        viewModel.initializeSystem(textureView)
        binding.statusText.text = "System initialized - Ready to record"
    }
    
    private fun startRecording() {
        val intent = Intent(this, RecordingService::class.java).apply {
            action = RecordingService.ACTION_START_RECORDING
        }
        ContextCompat.startForegroundService(this, intent)
        viewModel.startRecording()
    }
    
    private fun stopRecording() {
        val intent = Intent(this, RecordingService::class.java).apply {
            action = RecordingService.ACTION_STOP_RECORDING
        }
        startService(intent)
        viewModel.stopRecording()
    }
    
    private fun runCalibration() {
        viewModel.runCalibration()
        Toast.makeText(this, "Starting calibration process...", Toast.LENGTH_SHORT).show()
    }
    
    private fun updateRecordingUI(isRecording: Boolean) {
        binding.startRecordingButton.isEnabled = !isRecording
        binding.stopRecordingButton.isEnabled = isRecording
        binding.calibrationButton.isEnabled = !isRecording
        
        if (isRecording) {
            binding.recordingIndicator.setBackgroundColor(
                ContextCompat.getColor(this, android.R.color.holo_red_light)
            )
            binding.statusText.text = "Recording in progress..."
        } else {
            binding.recordingIndicator.setBackgroundColor(
                ContextCompat.getColor(this, android.R.color.darker_gray)
            )
            if (binding.statusText.text.contains("Recording")) {
                binding.statusText.text = "Recording stopped - Ready"
            }
        }
        
        // Update streaming UI indicators
        updateStreamingUI(isRecording)
    }
    
    /**
     * Update UI with SessionInfo data from enhanced CameraRecorder
     */
    private fun updateSessionInfoDisplay(sessionInfo: SessionInfo?) {
        if (sessionInfo != null) {
            // Update status text with session summary
            val sessionSummary = sessionInfo.getSummary()
            
            // For now, display session info in the existing status text
            // TODO: Add dedicated SessionInfo display components to layout
            if (sessionInfo.isActive()) {
                binding.statusText.text = "Active: $sessionSummary"
            } else {
                binding.statusText.text = "Completed: $sessionSummary"
            }
            
            // Log detailed session information
            android.util.Log.d("MainActivity", "SessionInfo updated: $sessionSummary")
            
            if (sessionInfo.errorOccurred) {
                Toast.makeText(this, "Session error: ${sessionInfo.errorMessage}", Toast.LENGTH_LONG).show()
            }
            
        } else {
            // No active session
            if (!viewModel.isRecording.value!!) {
                binding.statusText.text = "Ready to record"
            }
        }
    }
    
    // ========== Preview Streaming UI Methods ==========
    
    /**
     * Show streaming status indicator when preview streaming is active
     */
    private fun showStreamingIndicator() {
        binding.streamingIndicator.setBackgroundColor(
            ContextCompat.getColor(this, android.R.color.holo_green_light)
        )
        binding.streamingLabel.visibility = android.view.View.VISIBLE
    }
    
    /**
     * Hide streaming status indicator when preview streaming is stopped
     */
    private fun hideStreamingIndicator() {
        binding.streamingIndicator.setBackgroundColor(
            ContextCompat.getColor(this, android.R.color.darker_gray)
        )
        binding.streamingLabel.visibility = android.view.View.GONE
    }
    
    /**
     * Update debug overlay with streaming information
     */
    private fun updateStreamingDebugOverlay() {
        // Display static streaming information (dynamic stats handled by RecordingService)
        val debugText = "Streaming: 2fps (640x480) - Live Preview Active"
        binding.streamingDebugOverlay.text = debugText
        binding.streamingDebugOverlay.visibility = android.view.View.VISIBLE
    }
    
    /**
     * Update streaming UI based on recording state
     */
    private fun updateStreamingUI(isRecording: Boolean) {
        if (isRecording) {
            showStreamingIndicator()
            updateStreamingDebugOverlay()
        } else {
            hideStreamingIndicator()
            binding.streamingDebugOverlay.visibility = android.view.View.GONE
        }
    }
    
    // ========== Shimmer UI Enhancement Methods ==========
    
    /**
     * Handle results from ShimmerBluetoothDialog and other activities
     */
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        when (requestCode) {
            ShimmerBluetoothDialog.REQUEST_CONNECT_SHIMMER -> {
                if (resultCode == Activity.RESULT_OK && data != null) {
                    // Get selected device information from dialog
                    selectedShimmerAddress = data.getStringExtra(ShimmerBluetoothDialog.EXTRA_DEVICE_ADDRESS)
                    selectedShimmerName = data.getStringExtra(ShimmerBluetoothDialog.EXTRA_DEVICE_NAME)
                    
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] Shimmer device selected:")
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] - Address: $selectedShimmerAddress")
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] - Name: $selectedShimmerName")
                    
                    // Show BLE/Classic connection type selection dialog
                    showBtTypeConnectionOption()
                    
                } else {
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] Shimmer device selection cancelled")
                    Toast.makeText(this, "Device selection cancelled", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    /**
     * Show Bluetooth connection type selection dialog (BLE vs Classic)
     * Following the official bluetoothManagerExample pattern
     */
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
    
    /**
     * Connect to the selected Shimmer device using the chosen connection type
     */
    private fun connectSelectedShimmerDevice() {
        selectedShimmerAddress?.let { address ->
            selectedShimmerName?.let { name ->
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Connecting to Shimmer device:")
                android.util.Log.d("MainActivity", "[DEBUG_LOG] - Address: $address")
                android.util.Log.d("MainActivity", "[DEBUG_LOG] - Name: $name")
                android.util.Log.d("MainActivity", "[DEBUG_LOG] - Connection Type: $preferredBtType")
                
                // Update UI to show connection attempt
                binding.statusText.text = "Connecting to $name ($preferredBtType)..."
                
                // TODO: Connect via ViewModel/ShimmerRecorder - implement connectShimmerDevice method
                // viewModel.connectShimmerDevice(address, name, preferredBtType)
                
                Toast.makeText(this, "Connecting to $name via $preferredBtType", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    /**
     * Launch ShimmerBluetoothDialog for device selection
     */
    fun launchShimmerDeviceDialog() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Launching Shimmer device selection dialog")
        val intent = Intent(this, ShimmerBluetoothDialog::class.java)
        startActivityForResult(intent, ShimmerBluetoothDialog.REQUEST_CONNECT_SHIMMER)
    }
    
    /**
     * Show Shimmer sensor configuration dialog
     * Requires a connected Shimmer device
     */
    fun showShimmerSensorConfiguration() {
        // TODO: Get connected shimmer device from ViewModel
        // val shimmerDevice = viewModel.getConnectedShimmerDevice()
        // val btManager = viewModel.getShimmerBluetoothManager()
        
        // if (shimmerDevice != null && btManager != null) {
        //     if (!shimmerDevice.isStreaming() && !shimmerDevice.isSDLogging()) {
        //         ShimmerDialogConfigurations.buildShimmerSensorEnableDetails(shimmerDevice, this, btManager)
        //     } else {
        //         Toast.makeText(this, "Cannot configure - device is streaming or logging", Toast.LENGTH_SHORT).show()
        //     }
        // } else {
        //     Toast.makeText(this, "No Shimmer device connected", Toast.LENGTH_SHORT).show()
        // }
        
        Toast.makeText(this, "Shimmer sensor configuration - Coming soon", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * Show Shimmer general configuration dialog
     * Requires a connected Shimmer device
     */
    fun showShimmerGeneralConfiguration() {
        // TODO: Get connected shimmer device from ViewModel
        // val shimmerDevice = viewModel.getConnectedShimmerDevice()
        // val btManager = viewModel.getShimmerBluetoothManager()
        
        // if (shimmerDevice != null && btManager != null) {
        //     if (!shimmerDevice.isStreaming() && !shimmerDevice.isSDLogging()) {
        //         ShimmerDialogConfigurations.buildShimmerConfigOptions(shimmerDevice, this, btManager)
        //     } else {
        //         Toast.makeText(this, "Cannot configure - device is streaming or logging", Toast.LENGTH_SHORT).show()
        //     }
        // } else {
        //     Toast.makeText(this, "No Shimmer device connected", Toast.LENGTH_SHORT).show()
        // }
        
        Toast.makeText(this, "Shimmer general configuration - Coming soon", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * Start SD logging on connected Shimmer device
     */
    fun startShimmerSDLogging() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Starting Shimmer SD logging")
        
        // Check if any device is currently streaming or logging
        if (viewModel.isAnyShimmerDeviceStreaming()) {
            Toast.makeText(this, "Cannot start SD logging - device is streaming", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (viewModel.isAnyShimmerDeviceSDLogging()) {
            Toast.makeText(this, "SD logging is already active", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Start SD logging via ViewModel wrapper method
        viewModel.startShimmerSDLogging { success ->
            runOnUiThread {
                if (success) {
                    Toast.makeText(this@MainActivity, "SD logging started", Toast.LENGTH_SHORT).show()
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] SD logging started successfully")
                } else {
                    Toast.makeText(this@MainActivity, "Failed to start SD logging", Toast.LENGTH_SHORT).show()
                    android.util.Log.e("MainActivity", "[DEBUG_LOG] Failed to start SD logging")
                }
            }
        }
    }
    
    /**
     * Stop SD logging on connected Shimmer device
     */
    fun stopShimmerSDLogging() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Stopping Shimmer SD logging")
        
        // Check if any device is currently SD logging
        if (!viewModel.isAnyShimmerDeviceSDLogging()) {
            Toast.makeText(this, "No SD logging is currently active", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Stop SD logging via ViewModel wrapper method
        viewModel.stopShimmerSDLogging { success ->
            runOnUiThread {
                if (success) {
                    Toast.makeText(this@MainActivity, "SD logging stopped", Toast.LENGTH_SHORT).show()
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] SD logging stopped successfully")
                } else {
                    Toast.makeText(this@MainActivity, "Failed to stop SD logging", Toast.LENGTH_SHORT).show()
                    android.util.Log.e("MainActivity", "[DEBUG_LOG] Failed to stop SD logging")
                }
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Ensure recording service is stopped when activity is destroyed
        if (viewModel.isRecording.value == true) {
            stopRecording()
        }
    }
}
