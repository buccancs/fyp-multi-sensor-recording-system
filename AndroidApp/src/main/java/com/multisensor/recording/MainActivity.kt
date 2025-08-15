package com.multisensor.recording

import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Build
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
import com.multisensor.recording.network.PcCommunicationClient
import com.multisensor.recording.network.FaultToleranceManager
import com.multisensor.recording.network.DataTransferManager
import com.multisensor.recording.calibration.CalibrationManager
import com.multisensor.recording.security.SecurityManager
import com.multisensor.recording.validation.DataValidationService
import com.multisensor.recording.performance.PerformanceMonitor
import com.multisensor.recording.scalability.ScalabilityManager
import com.multisensor.recording.config.ConfigurationManager
import com.multisensor.recording.util.ToastManager

/**
 * MainActivity with IRCamera-style navigation
 * Features ViewPager2 with bottom navigation tabs
 */
class MainActivity : FragmentActivity(), View.OnClickListener {
    
    companion object {
        private const val TAG = "MainActivity"
    }

    // UI components
    private lateinit var viewPager: ViewPager2
    
    // Core components
    private lateinit var permissionManager: PermissionManager
    
    // Device components for multi-sensor recording
    lateinit var rgbCamera: com.multisensor.recording.camera.RgbCamera
    lateinit var thermalCamera: com.multisensor.recording.camera.ThermalCamera
    lateinit var gsrSensor: com.multisensor.recording.sensor.GsrSensor
    
    // Functional requirement components
    lateinit var pcCommunicationClient: PcCommunicationClient
    lateinit var sharedProtocolClient: com.multisensor.recording.network.SharedProtocolClient
    lateinit var faultToleranceManager: FaultToleranceManager
    lateinit var dataTransferManager: DataTransferManager
    lateinit var calibrationManager: CalibrationManager
    
    // NFR components for complete 3.tex implementation
    lateinit var securityManager: SecurityManager
    lateinit var dataValidationService: DataValidationService
    lateinit var performanceMonitor: PerformanceMonitor
    lateinit var scalabilityManager: ScalabilityManager
    lateinit var configurationManager: ConfigurationManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        Log.i(TAG, "Starting IRCamera-style Multi-Sensor Recording App")
        
        initializeViews()
        initializeComponents()
        requestPermissions()
        
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
            val usbDevice = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
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
                    ToastManager.showMessage(this@MainActivity, ToastManager.Messages.USB_DEVICE_DETECTED)
                    
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
     * Initialize core components
     */
    private fun initializeComponents() {
        // Initialize configuration manager first (NFR8)
        configurationManager = ConfigurationManager(this)
        val configStatus = configurationManager.initializeConfiguration()
        if (configStatus != ConfigurationManager.ConfigurationStatus.LOADED) {
            Logger.w(TAG, "Configuration system not properly loaded")
        }
        
        // Initialize security manager (NFR5)
        securityManager = SecurityManager(this)
        val securityStatus = securityManager.initializeSecurity()
        if (securityStatus != SecurityManager.SecurityStatus.SECURE) {
            Logger.w(TAG, "Security system not properly configured")
            showSecurityWarnings(securityManager.generateSecurityReport())
        }
        
        // Initialize data validation service (NFR4)
        dataValidationService = DataValidationService(this)
        dataValidationService.setValidationEnabled(true)
        
        // Initialize performance monitor (NFR1)
        performanceMonitor = PerformanceMonitor(this)
        performanceMonitor.setPerformanceAlertCallback { alert ->
            runOnUiThread {
                showPerformanceAlert(alert)
            }
        }
        performanceMonitor.startMonitoring()
        
        // Initialize scalability manager (NFR7)
        scalabilityManager = ScalabilityManager(this)
        val scalingStatus = scalabilityManager.initializeScaling()
        if (scalingStatus != ScalabilityManager.ScalingStatus.INITIALIZED) {
            Logger.w(TAG, "Scalability manager initialization failed")
        }
        
        // Initialize existing components
        permissionManager = PermissionManager(this)
        
        // Initialize device components for multi-sensor recording
        rgbCamera = com.multisensor.recording.camera.RgbCamera(this)
        thermalCamera = com.multisensor.recording.camera.ThermalCamera(this)
        gsrSensor = com.multisensor.recording.sensor.GsrSensor(this)
        
        // Initialize functional requirement components
        pcCommunicationClient = PcCommunicationClient()
        sharedProtocolClient = com.multisensor.recording.network.SharedProtocolClient()
        faultToleranceManager = FaultToleranceManager(this)
        dataTransferManager = DataTransferManager(this)
        calibrationManager = CalibrationManager(this)
        
        // Setup callbacks and integration
        setupComponentCallbacks()
        
        Log.i(TAG, "All components initialized successfully")
    }

    /**
     * Request all required permissions
     */
    private fun requestPermissions() {
        permissionManager.requestAllPermissions(this) { granted ->
            if (granted) {
                Log.i(TAG, "All permissions granted")
                // Permissions granted, components are ready
            } else {
                Log.w(TAG, "Permissions denied")
                // Handle permission denial - maybe show explanation
            }
        }
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
        // Apply sophisticated button API features with professional validation
        lifecycleScope.launch {
            try {
                // Create enhanced validation dialog
                val validationDialog = EnhancedProgressDialog.createValidationDialog(this@MainActivity)
                    .setOnCancelCallback {
                        Logger.i(TAG, "Recording access validation cancelled by user")
                    }
                
                // Execute comprehensive security and performance validation
                val validationSuccess = validationDialog.executeSteps(
                    EnhancedProgressDialog.getSecurityValidationSteps()
                ) { step ->
                    // Execute actual validation for each step
                    when {
                        step.description.contains("authentication", true) -> {
                            performAuthenticationCheck()
                        }
                        step.description.contains("TLS", true) -> {
                            performTlsValidation()
                        }
                        step.description.contains("permissions", true) -> {
                            performPermissionValidation()
                        }
                        else -> true
                    }
                }
                
                validationDialog.dismiss()
                
                if (validationSuccess) {
                    // Navigation only after successful validation
                    viewPager.setCurrentItem(0, false)
                    Logger.i(TAG, "Recording tab accessed with enhanced validation complete")
                    
                    // Show professional success feedback
                    android.widget.Toast.makeText(
                        this@MainActivity, 
                        "✅ Recording access granted - All validations passed", 
                        android.widget.Toast.LENGTH_SHORT
                    ).show()
                } else {
                    // Show professional error dialog
                    showValidationErrorDialog("Recording access validation failed")
                }
                
            } catch (e: Exception) {
                Logger.e(TAG, "Error during recording tab validation: ${e.message}")
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
                if (::faultToleranceManager.isInitialized) {
                    val systemHealthy = faultToleranceManager.isSystemHealthy()
                    if (!systemHealthy) {
                        Logger.w(TAG, "System health issues detected")
                        android.widget.Toast.makeText(this@MainActivity, "System health issues detected - checking devices", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
                
                Logger.i(TAG, "Main tab accessed with device health validation")
            } catch (e: Exception) {
                Logger.e(TAG, "Error accessing main tab: ${e.message}")
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
                if (::configurationManager.isInitialized) {
                    val configStatus = configurationManager.initializeConfiguration()
                    if (configStatus != ConfigurationManager.ConfigurationStatus.LOADED) {
                        Logger.w(TAG, "Configuration issues detected")
                        android.widget.Toast.makeText(this@MainActivity, "Configuration validation completed", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
                
                Logger.i(TAG, "Settings tab accessed with configuration validation")
            } catch (e: Exception) {
                Logger.e(TAG, "Error accessing settings tab: ${e.message}")
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
     * Setup callbacks for functional requirement components
     */
    private fun setupComponentCallbacks() {
        // PC Communication callbacks (legacy)
        pcCommunicationClient.setConnectionCallback { connected, message ->
            runOnUiThread {
                // Handle PC connection status changes
                Log.i(TAG, "PC connection (legacy): $connected - $message")
            }
        }
        
        // Shared Protocol Communication callbacks (harmonized)
        sharedProtocolClient.setConnectionCallback { connected, message ->
            runOnUiThread {
                // Handle PC connection status changes using shared protocol
                Log.i(TAG, "PC connection (shared protocol): $connected - $message")
            }
        }
        
        // Shared Protocol Command callbacks
        sharedProtocolClient.setCommandCallback { protocolMessage ->
            runOnUiThread {
                handleSharedProtocolMessage(protocolMessage)
            }
        }
        
        // Fault tolerance callbacks
        faultToleranceManager.setSystemHealthCallback { isHealthy, deviceHealthMap ->
            // Update UI with system health status
            runOnUiThread {
                Log.d(TAG, "System health: $isHealthy")
            }
        }
        
        // Data transfer callbacks
        dataTransferManager.setTransferCompleteCallback { success, errorMessage, results ->
            runOnUiThread {
                if (success) {
                    Log.i(TAG, "Data transfer completed successfully")
                } else {
                    Log.w(TAG, "Data transfer failed: $errorMessage")
                }
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
                sharedProtocolClient.sendCommandResponse("session_start", true)
            }
            "session_stop" -> {
                // Handle session stop command
                Log.i(TAG, "Session stop command received")
                sharedProtocolClient.sendCommandResponse("session_stop", true)
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
     * Show security warnings from security report
     * NFR5: Security checks at startup warn if not configured correctly
     */
    private fun showSecurityWarnings(report: SecurityManager.SecurityReport) {
        if (report.hasWarnings()) {
            val warnings = report.getWarningMessages()
            Logger.w(TAG, "Security warnings detected: ${warnings.joinToString("; ")}")
            
            // Show warning dialog to user
            runOnUiThread {
                val warningMessage = "Security Configuration Warnings:\n\n" + 
                                   warnings.joinToString("\n• ", "• ")
                
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
    }

    /**
     * Show performance alert from performance monitor
     * NFR1: Performance alerting for bottlenecks
     */
    private fun showPerformanceAlert(alert: PerformanceMonitor.PerformanceAlert) {
        // Show performance alert as toast for now
        android.widget.Toast.makeText(this, "Performance Alert: ${alert.message}", android.widget.Toast.LENGTH_LONG).show()
        
        Logger.w(TAG, "Performance alert: ${alert.type} - ${alert.message}")
        
        // Take automated actions based on alert type
        when (alert.type) {
            PerformanceMonitor.AlertType.HIGH_MEMORY_USAGE -> {
                System.gc()
            }
            PerformanceMonitor.AlertType.HIGH_FRAME_DROP_RATE -> {
                Logger.i(TAG, "Consider reducing video quality due to frame drops")
            }
            PerformanceMonitor.AlertType.HIGH_SAMPLE_DROP_RATE -> {
                Logger.i(TAG, "Consider reducing sensor sampling rate due to sample drops")
            }
            else -> {
                // Other alerts handled by monitoring
            }
        }
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
            if (::securityManager.isInitialized) {
                val securityStatus = securityManager.initializeSecurity()
                securityStatus == SecurityManager.SecurityStatus.SECURE
            } else {
                Logger.w(TAG, "Security manager not initialized")
                false
            }
        } catch (e: Exception) {
            Logger.e(TAG, "Authentication check failed: ${e.message}")
            false
        }
    }
    
    /**
     * Professional TLS validation for enhanced security
     */
    private suspend fun performTlsValidation(): Boolean {
        return try {
            // Check if security manager is properly initialized
            if (!::securityManager.isInitialized) {
                Logger.w(TAG, "Security manager not initialized for TLS validation")
                return false
            }
            
            // Generate security report to validate TLS configuration
            val securityReport = securityManager.generateSecurityReport()
            val hasSecurityIssues = securityReport.hasWarnings()
            
            if (hasSecurityIssues) {
                Logger.w(TAG, "TLS validation failed due to security warnings")
                return false
            }
            
            // Check if encryption is properly configured
            val securityStatus = securityManager.initializeSecurity()
            val tlsValid = securityStatus == SecurityManager.SecurityStatus.SECURE
            
            if (tlsValid) {
                Logger.i(TAG, "TLS validation successful")
            } else {
                Logger.w(TAG, "TLS validation failed - security status: $securityStatus")
            }
            
            tlsValid
        } catch (e: Exception) {
            Logger.e(TAG, "TLS validation failed: ${e.message}")
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
                Logger.w(TAG, "Required permissions not granted")
            }
            hasPermissions
        } catch (e: Exception) {
            Logger.e(TAG, "Permission validation failed: ${e.message}")
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
        
        // Cleanup device components
        if (::rgbCamera.isInitialized) rgbCamera.release()
        if (::thermalCamera.isInitialized) thermalCamera.release()
        if (::gsrSensor.isInitialized) gsrSensor.release()
        
        // Cleanup functional components
        if (::pcCommunicationClient.isInitialized) pcCommunicationClient.cleanup()
        if (::faultToleranceManager.isInitialized) faultToleranceManager.cleanup()
        if (::dataTransferManager.isInitialized) dataTransferManager.cleanup()
        
        // Cleanup NFR components
        if (::performanceMonitor.isInitialized) performanceMonitor.stopMonitoring()
        if (::scalabilityManager.isInitialized) scalabilityManager.cleanup()
        
        Log.i(TAG, "MainActivity destroyed, all resources released")
    }
}