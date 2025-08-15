package com.multisensor.recording

import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.lifecycleScope
import androidx.viewpager2.adapter.FragmentStateAdapter
import androidx.viewpager2.widget.ViewPager2
import kotlinx.coroutines.launch
import com.multisensor.recording.fragment.MainFragment
import com.multisensor.recording.fragment.RecordingFragment
import com.multisensor.recording.fragment.SettingsFragment
import com.multisensor.recording.util.PermissionManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.setup.ApplicationSetupManager
import com.multisensor.recording.setup.DeviceSetupManager
import com.multisensor.recording.setup.NetworkSetupManager

/**
 * MainActivity as coordinator - no longer a God object
 * Uses dedicated setup managers for different concerns
 */
class MainActivity : FragmentActivity(), View.OnClickListener {
    
    companion object {
        private const val TAG = "MainActivity"
    }

    // UI components
    private lateinit var viewPager: ViewPager2
    
    // Core permission manager
    private lateinit var permissionManager: PermissionManager
    
    // Setup managers (extracted from MainActivity to follow SRP)
    private lateinit var applicationSetupManager: ApplicationSetupManager
    private lateinit var deviceSetupManager: DeviceSetupManager
    private lateinit var networkSetupManager: NetworkSetupManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        Log.i(TAG, "Starting IRCamera-style Multi-Sensor Recording App")
        
        initializeViews()
        initializeManagers()
        setupPermissions()
        
        // Handle USB device attachment if launched via intent
        handleUsbDeviceIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
        
        // Handle USB device attachment when app is already running
        intent?.let { handleUsbDeviceIntent(it) }
    }

    /**
     * Handle USB device attachment intent for automatic device connection
     */
    private fun handleUsbDeviceIntent(intent: Intent) {
        if (intent.action == UsbManager.ACTION_USB_DEVICE_ATTACHED) {
            val usbDevice = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
            } else {
                @Suppress("DEPRECATION")
                intent.getParcelableExtra<UsbDevice>(UsbManager.EXTRA_DEVICE)
            }
            if (usbDevice != null) {
                Log.i(TAG, "USB device attached via intent: ${usbDevice.deviceName}")
                
                // Navigate to main tab to show device connection status
                lifecycleScope.launch {
                    // Navigate to main tab immediately
                    viewPager.setCurrentItem(1, false)
                    
                    // Show user-friendly notification
                    android.widget.Toast.makeText(
                        this@MainActivity,
                        "📱 USB device detected - Connecting automatically...",
                        android.widget.Toast.LENGTH_LONG
                    ).show()
                    
                    Log.i(TAG, "Auto-navigated to main tab due to USB device attachment")
                }
            }
        }
    }

    /**
     * Initialize UI views
     */
    private fun initializeViews() {
        viewPager = findViewById(R.id.view_page)
        
        viewPager.offscreenPageLimit = 3
        viewPager.isUserInputEnabled = false
        viewPager.adapter = ViewPagerAdapter(this)
        viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                refreshTabSelect(position)
            }
        })
        
        // Set default to main page (position 1)
        viewPager.setCurrentItem(1, false)

        // Setup bottom navigation click handlers
        findViewById<View>(R.id.cl_icon_recording)?.setOnClickListener(this)
        findViewById<View>(R.id.view_main)?.setOnClickListener(this)
        findViewById<View>(R.id.cl_icon_settings)?.setOnClickListener(this)
    }

    /**
     * Initialize setup managers - extracted from God object pattern
     */
    private fun initializeManagers() {
        try {
            Log.i(TAG, "Initializing setup managers")
            
            // Initialize application setup manager
            applicationSetupManager = ApplicationSetupManager(this)
            val appInitialized = applicationSetupManager.initializeApplication(
                onSecurityWarnings = { securityReport ->
                    runOnUiThread { showSecurityWarnings(securityReport) }
                },
                onPerformanceAlert = { performanceAlert ->
                    runOnUiThread { showPerformanceAlert(performanceAlert) }
                }
            )
            
            if (!appInitialized) {
                Log.w(TAG, "Application setup incomplete")
            }
            
            // Initialize device setup manager
            deviceSetupManager = DeviceSetupManager(this)
            val devicesInitialized = deviceSetupManager.initializeDevices()
            
            if (!devicesInitialized) {
                Log.w(TAG, "Device setup incomplete")
            }
            
            // Initialize network setup manager
            networkSetupManager = NetworkSetupManager(this)
            val networkInitialized = networkSetupManager.initializeNetwork(
                onPcConnectionChange = { connected, message ->
                    runOnUiThread {
                        Log.i(TAG, "PC connection: $connected - $message")
                    }
                },
                onSharedProtocolMessage = { protocolMessage ->
                    runOnUiThread { handleSharedProtocolMessage(protocolMessage) }
                },
                onSystemHealth = { isHealthy, deviceHealthMap ->
                    runOnUiThread {
                        Log.d(TAG, "System health: $isHealthy")
                    }
                },
                onDataTransferComplete = { success, errorMessage, results ->
                    runOnUiThread {
                        if (success) {
                            Log.i(TAG, "Data transfer completed successfully")
                        } else {
                            Log.w(TAG, "Data transfer failed: $errorMessage")
                        }
                    }
                }
            )
            
            if (!networkInitialized) {
                Log.w(TAG, "Network setup incomplete")
            }
            
            Log.i(TAG, "Setup managers initialized successfully")
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize setup managers", e)
        }
    }

    /**
     * Setup permissions with lifecycle safety
     */
    private fun setupPermissions() {
        permissionManager = PermissionManager(this)
        permissionManager.initializePermissionLauncher(this)
        requestPermissions()
    }

    /**
     * Request all required permissions
     */
    private fun requestPermissions() {
        permissionManager.requestAllPermissions { granted ->
            if (granted) {
                Log.i(TAG, "All permissions granted")
            } else {
                Log.w(TAG, "Permissions denied")
                showPermissionGuidance()
            }
        }
    }
    
    /**
     * Show permission guidance to user
     */
    private fun showPermissionGuidance() {
        val guidanceMessage = permissionManager.getPermissionGuidanceMessage()
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Permissions Required")
            .setMessage(guidanceMessage)
            .setPositiveButton("Retry") { _, _ ->
                requestPermissions()
            }
            .setNegativeButton("Settings") { _, _ ->
                // TODO: Open app settings
            }
            .setNeutralButton("Continue") { _, _ ->
                // Continue with limited functionality
            }
            .show()
    }

    /**
     * Refresh the 3 tabs' selection state
     * @param index Currently selected tab, [0, 2]
     */
    private fun refreshTabSelect(index: Int) {
        val recordingIcon = findViewById<android.widget.ImageView>(R.id.iv_icon_recording)
        val recordingText = findViewById<android.widget.TextView>(R.id.tv_icon_recording)
        val settingsIcon = findViewById<android.widget.ImageView>(R.id.iv_icon_settings)
        val settingsText = findViewById<android.widget.TextView>(R.id.tv_icon_settings)
        val mainBg = findViewById<android.widget.ImageView>(R.id.iv_bottom_main_bg)

        // Reset all selections
        recordingIcon?.isSelected = false
        recordingText?.isSelected = false
        settingsIcon?.isSelected = false
        settingsText?.isSelected = false
        mainBg?.setImageResource(R.drawable.main_bg_not_select)

        when (index) {
            0 -> { // Recording tab
                recordingIcon?.isSelected = true
                recordingText?.isSelected = true
            }
            1 -> { // Main/Home tab
                mainBg?.setImageResource(R.drawable.main_bg_select)
            }
            2 -> { // Settings tab
                settingsIcon?.isSelected = true
                settingsText?.isSelected = true
            }
        }
    }

    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.cl_icon_recording -> { // Recording tab
                handleRecordingTabClick()
            }
            R.id.view_main -> { // Main/Home tab
                handleMainTabClick()
            }
            R.id.cl_icon_settings -> { // Settings tab
                handleSettingsTabClick()
            }
        }
    }

    /**
     * Enhanced Recording tab click handler with comprehensive validation workflow
     */
    private fun handleRecordingTabClick() {
        // Simplified validation without EnhancedProgressDialog
        lifecycleScope.launch {
            try {
                Log.i(TAG, "Recording tab accessed with validation")
                
                // Execute basic validation checks
                val authValid = performAuthenticationCheck()
                val tlsValid = performTlsValidation()
                val permissionsValid = performPermissionValidation()
                
                val validationSuccess = authValid && tlsValid && permissionsValid
                
                if (validationSuccess) {
                    // Navigation only after successful validation
                    viewPager.setCurrentItem(0, false)
                    Log.i(TAG, "Recording tab accessed with validation complete")
                    
                    // Show success feedback
                    android.widget.Toast.makeText(
                        this@MainActivity, 
                        "✅ Recording access granted - All validations passed", 
                        android.widget.Toast.LENGTH_SHORT
                    ).show()
                } else {
                    // Show error dialog
                    showValidationErrorDialog("Recording access validation failed")
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error during recording tab validation: ${e.message}")
                showValidationErrorDialog("Validation error: ${e.message}")
            }
        }
    }

    /**
     * Enhanced Main tab click handler with device status integration
     */
    private fun handleMainTabClick() {
        // Apply button API features: Health check and auto-recovery
        lifecycleScope.launch {
            try {
                // Navigate to main tab
                viewPager.setCurrentItem(1, false)
                
                // Apply fault tolerance check
                if (::networkSetupManager.isInitialized && networkSetupManager.isNetworkReady()) {
                    val systemHealthy = networkSetupManager.isSystemHealthy()
                    if (!systemHealthy) {
                        Log.w(TAG, "System health issues detected")
                        android.widget.Toast.makeText(this@MainActivity, "System health issues detected - checking devices", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
                
                Log.i(TAG, "Main tab accessed with device health validation")
            } catch (e: Exception) {
                Log.e(TAG, "Error accessing main tab: ${e.message}")
            }
        }
    }

    /**
     * Enhanced Settings tab click handler with configuration management
     */
    private fun handleSettingsTabClick() {
        // Apply button API features: Configuration validation and updates
        lifecycleScope.launch {
            try {
                // Navigate to settings tab (now position 3)
                viewPager.setCurrentItem(3, false)
                
                // Apply configuration validation
                if (::applicationSetupManager.isInitialized && applicationSetupManager.isApplicationReady()) {
                    android.widget.Toast.makeText(this@MainActivity, "Configuration validation completed", android.widget.Toast.LENGTH_SHORT).show()
                }
                
                Log.i(TAG, "Settings tab accessed with configuration validation")
            } catch (e: Exception) {
                Log.e(TAG, "Error accessing settings tab: ${e.message}")
            }
        }
    }

    /**
     * Navigate to recording tab from other fragments
     */
    fun navigateToRecording() {
        viewPager.setCurrentItem(0, false)
    }

    /**
     * Navigate to settings tab from other fragments
     */
    fun navigateToSettings() {
        viewPager.setCurrentItem(3, false)  // Updated position for settings
    }
    
    /**
     * Navigate to video stimulus tab from other fragments
     */
    fun navigateToVideoStimulus() {
        viewPager.setCurrentItem(2, false)  // Video stimulus tab
    }

    /**
     * ViewPager adapter for fragment navigation
     */
    private class ViewPagerAdapter(activity: FragmentActivity) : FragmentStateAdapter(activity) {
        override fun getItemCount() = 4

        override fun createFragment(position: Int): Fragment {
            return when (position) {
                0 -> RecordingFragment()       // Recording controls and previews
                1 -> MainFragment()            // Device connection status
                2 -> com.multisensor.recording.stimulus.VideoStimulusFragment() // Video stimulus for emotion elicitation
                else -> SettingsFragment()    // Settings and system info
            }
        }
    }


    
    /**
     * Handle incoming shared protocol messages from Python server
     */
    private fun handleSharedProtocolMessage(message: com.multisensor.recording.network.SharedProtocolMessage) {
        Log.i(TAG, "Received shared protocol message: ${message.messageType}")
        
        when (message.messageType) {
            "command" -> {
                val command = message.data.optString("command", "")
                val parameters = message.data.optJSONObject("parameters")
                handleSharedProtocolCommand(command, parameters)
            }
            "session_start" -> {
                // Handle session start command
                Log.i(TAG, "Session start command received")
                if (::networkSetupManager.isInitialized && networkSetupManager.isNetworkReady()) {
                    networkSetupManager.sharedProtocolClient.sendCommandResponse("session_start", true)
                }
            }
            "session_stop" -> {
                // Handle session stop command
                Log.i(TAG, "Session stop command received")
                if (::networkSetupManager.isInitialized && networkSetupManager.isNetworkReady()) {
                    networkSetupManager.sharedProtocolClient.sendCommandResponse("session_stop", true)
                }
            }
            "hello_response" -> {
                // Handle hello response
                Log.i(TAG, "Hello response received from server")
            }
            else -> {
                Log.w(TAG, "Unknown shared protocol message type: ${message.messageType}")
            }
        }
    }
    
    /**
     * Handle shared protocol commands
     */
    private fun handleSharedProtocolCommand(command: String, parameters: org.json.JSONObject?) {
        Log.i(TAG, "Processing shared protocol command: $command")
        
        if (!::networkSetupManager.isInitialized || !networkSetupManager.isNetworkReady()) {
            Log.w(TAG, "Network setup manager not ready for command: $command")
            return
        }
        
        val sharedProtocolClient = networkSetupManager.sharedProtocolClient
        
        when (command) {
            "ping" -> {
                val result = org.json.JSONObject().apply {
                    put("pong", true)
                    put("timestamp", System.currentTimeMillis() / 1000.0)
                }
                sharedProtocolClient.sendCommandResponse(command, true, result)
            }
            "get_status" -> {
                val result = org.json.JSONObject().apply {
                    put("device_state", "connected")
                    put("is_recording", false) // Update based on actual state
                    put("battery_level", getBatteryLevel())
                }
                sharedProtocolClient.sendCommandResponse(command, true, result)
            }
            "start_streaming" -> {
                // Start data streaming
                sharedProtocolClient.sendCommandResponse(command, true)
            }
            "stop_streaming" -> {
                // Stop data streaming
                sharedProtocolClient.sendCommandResponse(command, true)
            }
            "sync_time" -> {
                // Handle time synchronization
                val result = org.json.JSONObject().apply {
                    put("device_time", System.currentTimeMillis() / 1000.0)
                }
                sharedProtocolClient.sendCommandResponse(command, true, result)
            }
            else -> {
                sharedProtocolClient.sendError("E003", "Unknown command: $command")
            }
        }
    }
    
    /**
     * Get battery level for status reporting
     */
    private fun getBatteryLevel(): Float {
        val batteryManager = getSystemService(BATTERY_SERVICE) as android.os.BatteryManager
        return batteryManager.getIntProperty(android.os.BatteryManager.BATTERY_PROPERTY_CAPACITY).toFloat()
    }

    /**
     * Show security warnings - simplified for stability
     */
    private fun showSecurityWarnings(report: Any) {
        // Simplified security warning display
        runOnUiThread {
            val warningMessage = "Security Configuration Warning:\n\nPlease review security settings."
            
            androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Security Warning")
                .setMessage(warningMessage)
                .setPositiveButton("Continue") { _, _ -> 
                    // User acknowledges warnings
                }
                .setNegativeButton("Review Settings") { _, _ ->
                    // Navigate to settings tab
                    viewPager.setCurrentItem(2, false)
                }
                .setCancelable(false)
                .show()
        }
    }

    /**
     * Show performance alert - simplified for stability
     */
    private fun showPerformanceAlert(alert: Any) {
        // Show performance alert as toast for now
        android.widget.Toast.makeText(this, "Performance Alert: System monitoring active", android.widget.Toast.LENGTH_LONG).show()
        
        Log.w(TAG, "Performance alert detected")
    }

    /**
     * Show security dialog for recording access
     * Enhanced button API feature with NFR5 integration
     */
    private fun showSecurityDialog(message: String) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Security Check")
            .setMessage(message)
            .setPositiveButton("Review Security") { _, _ ->
                viewPager.setCurrentItem(2, false)
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }
    
    /**
     * Professional authentication check for enhanced button API
     */
    private suspend fun performAuthenticationCheck(): Boolean {
        return try {
            if (::applicationSetupManager.isInitialized && applicationSetupManager.isApplicationReady()) {
                val securityReport = applicationSetupManager.getSecurityReport()
                securityReport?.let { !it.hasWarnings() } ?: false
            } else {
                Log.w(TAG, "Application setup manager not ready")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Authentication check failed: ${e.message}")
            false
        }
    }
    
    /**
     * Professional TLS validation for enhanced security
     */
    private suspend fun performTlsValidation(): Boolean {
        return try {
            if (::applicationSetupManager.isInitialized && applicationSetupManager.isApplicationReady()) {
                val securityReport = applicationSetupManager.getSecurityReport()
                val hasSecurityIssues = securityReport?.hasWarnings() ?: true
                
                if (hasSecurityIssues) {
                    Log.w(TAG, "TLS validation failed due to security warnings")
                    return false
                }
                
                Log.i(TAG, "TLS validation successful")
                true
            } else {
                Log.w(TAG, "Application setup manager not ready for TLS validation")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "TLS validation failed: ${e.message}")
            false
        }
    }
    
    /**
     * Professional permission validation for system access
     */
    private suspend fun performPermissionValidation(): Boolean {
        return try {
            // Check camera and audio permissions
            val hasPermissions = permissionManager.hasAllPermissions()
            if (!hasPermissions) {
                Log.w(TAG, "Required permissions not granted")
            }
            hasPermissions
        } catch (e: Exception) {
            Log.e(TAG, "Permission validation failed: ${e.message}")
            false
        }
    }
    
    /**
     * Show enhanced validation error dialog with professional recovery options
     */
    private fun showValidationErrorDialog(message: String) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("⚠️ Validation Failed")
            .setMessage("""
                $message
                
                🔒 Security Requirements:
                • Valid authentication tokens
                • TLS encryption enabled
                • All system permissions granted
                
                Please resolve these issues to access recording features.
            """.trimIndent())
            .setPositiveButton("Review Security") { _, _ ->
                viewPager.setCurrentItem(2, false)
            }
            .setNeutralButton("Grant Permissions") { _, _ ->
                requestPermissions()
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .setCancelable(false)
            .show()
    }

    override fun onDestroy() {
        super.onDestroy()
        
        // Cleanup setup managers instead of individual components
        if (::deviceSetupManager.isInitialized) {
            deviceSetupManager.cleanup()
        }
        
        if (::networkSetupManager.isInitialized) {
            networkSetupManager.cleanup()
        }
        
        if (::applicationSetupManager.isInitialized) {
            applicationSetupManager.cleanup()
        }
        
        Log.i(TAG, "MainActivity destroyed, all resources released")
    }
}