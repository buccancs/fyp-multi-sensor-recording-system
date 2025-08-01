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
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.Lifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.SessionDisplayInfo
import com.multisensor.recording.ui.components.StatusIndicatorView
import com.multisensor.recording.ui.components.ActionButtonPair
import com.multisensor.recording.util.AllAndroidPermissions
import com.multisensor.recording.util.PermissionTool
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.calibration.SyncClockManager
import com.multisensor.recording.managers.PermissionManager
import com.multisensor.recording.controllers.PermissionController
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.managers.UsbDeviceManager
import com.multisensor.recording.controllers.ShimmerController
import com.multisensor.recording.controllers.MainActivityCoordinator
import com.multisensor.recording.controllers.UIController
import com.multisensor.recording.controllers.UsbController
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
import com.multisensor.recording.ui.components.HandSegmentationControlView

/**
 * main activity for multi-sensor recording system
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity(),
    PermissionManager.PermissionCallback,
    ShimmerController.ShimmerCallback,
    UsbDeviceManager.UsbDeviceCallback,

    HandSegmentationManager.HandSegmentationListener,
    HandSegmentationControlView.HandSegmentationControlListener {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel

    @Inject
    lateinit var calibrationCaptureManager: CalibrationCaptureManager

    @Inject
    lateinit var syncClockManager: SyncClockManager

    @Inject
    lateinit var permissionManager: PermissionManager

    @Inject
    lateinit var permissionController: PermissionController

    @Inject
    lateinit var shimmerManager: ShimmerManager

    @Inject
    lateinit var shimmerController: ShimmerController

    @Inject
    lateinit var usbDeviceManager: UsbDeviceManager

    @Inject
    lateinit var calibrationController: CalibrationController

    @Inject
    lateinit var usbController: UsbController


    @Inject
    lateinit var handSegmentationManager: HandSegmentationManager

    @Inject
    lateinit var mainActivityCoordinator: MainActivityCoordinator

    @Inject
    lateinit var uiController: UIController

    private var selectedShimmerAddress: String? = null
    private var selectedShimmerName: String? = null
    private var preferredBtType: ShimmerBluetoothManagerAndroid.BT_TYPE = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC

    // Modern Activity Result API for Shimmer device selection
    private val shimmerDeviceSelectionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        AppLogger.logMethodEntry("MainActivity", "shimmerDeviceSelectionLauncher", "resultCode=${result.resultCode}")
        
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            // Get selected device information from dialog
            val address = result.data?.getStringExtra(ShimmerBluetoothDialog.EXTRA_DEVICE_ADDRESS)
            val name = result.data?.getStringExtra(ShimmerBluetoothDialog.EXTRA_DEVICE_NAME)

            logI("Shimmer device selected: Address=$address, Name=$name")

            // Use ShimmerController to handle device selection
            shimmerController.handleDeviceSelectionResult(address, name)
        } else {
            logI("Shimmer device selection cancelled")
            shimmerController.handleDeviceSelectionResult(null, null)
        }
    }
    private var looper: Looper? = null


    override fun onCreate(savedInstanceState: Bundle?) {
        AppLogger.logMethodEntry("MainActivity", "onCreate", "Initializing main activity")
        AppLogger.logMemoryUsage("MainActivity", "onCreate - start")
        super.onCreate(savedInstanceState)
        
        AppLogger.logLifecycle("MainActivity", "onCreate")
        logI("=== Multi-Sensor Recording Application Starting ===")
        AppLogger.logMemoryUsage("MainActivity", "Application Startup")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onCreate() starting")

        // Initialize view binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        android.util.Log.d("MainActivity", "[DEBUG_LOG] View binding initialized and content view set")

        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ViewModel initialized")

        // Initialize ShimmerController with callback
        shimmerController.setCallback(this)
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ShimmerController initialized and callback set")

        // Setup UI
        setupUI()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] UI setup completed")

        // Setup managers and callbacks (TODO: Add proper callback setup methods to managers)
        // shimmerManager.setCallback(this)
        // permissionManager.setCallback(this)
        // handSegmentationManager.setListener(this)
        usbController.setCallback(this)

        // Initialize USB monitoring for already connected devices
        usbController.initializeUsbMonitoring(this)

        // Note: Permission checking moved to onResume() for better timing
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Permission checking will be done in onResume() for better timing")

        // Observe ViewModel state
        observeViewModel()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] ViewModel observers set up")

        android.util.Log.d("MainActivity", "[DEBUG_LOG] ===== APP STARTUP: onCreate() completed =====")

        // Handle USB device attachment if launched by USB intent
        usbController.handleUsbDeviceIntent(this, intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        android.util.Log.d("MainActivity", "[DEBUG_LOG] onNewIntent() called")

        // Handle USB device attachment
        usbController.handleUsbDeviceIntent(this, intent)

    private fun handleUsbDeviceIntent(intent: Intent) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Handling USB device intent: ${intent.action}")

        when (intent.action) {
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                val device: UsbDevice? = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                }
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
                        Toast
                            .makeText(
                                this,
                                "Topdon Thermal Camera Connected!\nDevice: ${usbDevice.deviceName}",
                                Toast.LENGTH_LONG,
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
        android.util.Log.d(
            "MainActivity",
            "[DEBUG_LOG] - Expected PIDs: ${supportedProductIds.joinToString { "0x${String.format("%04X", it)}" }}",
        )
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Actual PID: 0x${String.format("%04X", productId)}")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Is supported: $isSupported")

        return isSupported
    }

    /**
     * Check if all required permissions are granted
     */
    private fun areAllPermissionsGranted(): Boolean =
        permissionController.areAllPermissionsGranted(this)

    override fun onStart() {
        super.onStart()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onStart() called")
    }

    // Status Display System - UI Enhancements
    private var currentBatteryLevel = -1
    private var isPcConnected = false
    private var isShimmerConnected = false
    private var isThermalConnected = false
    private lateinit var statusUpdateHandler: Handler
    private lateinit var mediaActionSound: MediaActionSound
    
    // UI Components for consolidation
    private lateinit var pcStatusIndicator: StatusIndicatorView
    private lateinit var shimmerStatusIndicator: StatusIndicatorView
    private lateinit var thermalStatusIndicator: StatusIndicatorView
    private lateinit var recordingButtonPair: ActionButtonPair

    // Battery monitoring receiver
    private val batteryReceiver =
        object : BroadcastReceiver() {
            override fun onReceive(
                context: Context?,
                intent: Intent?,
            ) {
                if (intent?.action == Intent.ACTION_BATTERY_CHANGED) {
                    val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                    val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)

                    if (level != -1 && scale != -1) {
                        currentBatteryLevel = (level * 100) / scale
                        updateBatteryDisplay()
                    }
                }
            }
        }

    override fun onResume() {
        AppLogger.logMethodEntry("MainActivity", "onResume", "Activity resuming")
        super.onResume()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onResume() called")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity is now fully visible and interactive")

        // Log current permission states for debugging
        permissionController.logCurrentPermissionStates(this)

        // Check and request permissions on first resume (app startup)
        permissionController.initializePermissionsOnStartup(this)
    }

    override fun onPause() {
        AppLogger.logMethodEntry("MainActivity", "onPause", "Activity pausing")
        super.onPause()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onPause() called")
    }

    override fun onStop() {
        super.onStop()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Activity lifecycle: onStop() called")
    }

    private fun logCurrentPermissionStates() {
        permissionController.logCurrentPermissionStates(this)
    }

    // Status Display System Methods - UI Enhancements

    /**
     * Updates the battery level display with current percentage
     */
    private fun updateBatteryDisplay() {
        runOnUiThread {
            if (currentBatteryLevel >= 0) {
                binding.batteryLevelText.text = "Battery: $currentBatteryLevel%"

                // Change text color based on battery level
                val textColor =
                    when {
                        currentBatteryLevel > 50 -> Color.GREEN
                        currentBatteryLevel > 20 -> Color.YELLOW
                        else -> Color.RED
                    }
                binding.batteryLevelText.setTextColor(textColor)
            } else {
                binding.batteryLevelText.text = "Battery: ---%"
                binding.batteryLevelText.setTextColor(Color.WHITE)
            }
        }
    }

    /**
     * Updates PC connection status display
     */
    private fun updatePcConnectionStatus(connected: Boolean) {
        isPcConnected = connected
        runOnUiThread {
            if (connected) {
                binding.pcConnectionStatus.text = "PC: Connected"
                binding.pcConnectionIndicator.setBackgroundColor(Color.GREEN)
            } else {
                binding.pcConnectionStatus.text = "PC: Waiting for PC..."
                binding.pcConnectionIndicator.setBackgroundColor(Color.RED)
            }
        }
    }

    /**
     * Updates sensor connectivity status displays
     */
    private fun updateSensorConnectionStatus(
        shimmerConnected: Boolean,
        thermalConnected: Boolean,
    ) {
        isShimmerConnected = shimmerConnected
        isThermalConnected = thermalConnected

        runOnUiThread {
            // Update Shimmer status
            if (shimmerConnected) {
                binding.shimmerConnectionStatus.text = "Shimmer: Connected"
                binding.shimmerConnectionIndicator.setBackgroundColor(Color.GREEN)
            } else {
                binding.shimmerConnectionStatus.text = "Shimmer: Disconnected"
                binding.shimmerConnectionIndicator.setBackgroundColor(Color.RED)
            }

            // Update Thermal status
            if (thermalConnected) {
                binding.thermalConnectionStatus.text = "Thermal: Connected"
                binding.thermalConnectionIndicator.setBackgroundColor(Color.GREEN)
            } else {
                binding.thermalConnectionStatus.text = "Thermal: Disconnected"
                binding.thermalConnectionIndicator.setBackgroundColor(Color.RED)
            }
        }
    }



    /**
     * Initializes status monitoring system
     */
    private fun initializeStatusMonitoring() {
        // Initialize status update handler
        statusUpdateHandler = Handler(Looper.getMainLooper())

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
                updateBatteryDisplay()
            }
        }

        // Initialize status displays
        updatePcConnectionStatus(false) // Start with PC disconnected
        updateSensorConnectionStatus(false, false) // Start with sensors disconnected

        // Start periodic status updates
        startPeriodicStatusUpdates()
    }

    /**
     * Starts periodic status updates every 5 seconds
     */
    private fun startPeriodicStatusUpdates() {
        val updateRunnable =
            object : Runnable {
                override fun run() {
                    // Update sensor connection status based on current state
                    // Note: Connection status will be updated by other components when they change
                    // This periodic update mainly ensures UI consistency

                    // Schedule next update
                    statusUpdateHandler.postDelayed(this, 5000) // 5 seconds
                }
            }
        statusUpdateHandler.post(updateRunnable)
    }

    /**
     * Updates sensor connection status from external components
     */
    fun updateShimmerConnectionStatus(connected: Boolean) {
        isShimmerConnected = connected
        updateSensorConnectionStatus(isShimmerConnected, isThermalConnected)
    }

    /**
     * Updates thermal connection status from external components
     */
    fun updateThermalConnectionStatus(connected: Boolean) {
        isThermalConnected = connected
        updateSensorConnectionStatus(isShimmerConnected, isThermalConnected)
    }

    private fun setupUI() {
        // Initialize coordinator with callback implementation
        initializeCoordinator()
        
        // Initialize UIController through coordinator
        initializeUIControllerIntegration()
        
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
            permissionController.requestPermissionsManually(this)
        }

        binding.navigationModeButton.setOnClickListener {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Navigation mode button clicked")
            launchNavigationMode()
        }

        // Initially disable stop buttons
        binding.stopRecordingButton.isEnabled = false

        // Setup hand segmentation controls
        setupHandSegmentation()

        // Initialize status monitoring system
        initializeStatusMonitoring()
    }
    
    /**
     * Initialize the main activity coordinator with callback implementation
     */
    private fun initializeCoordinator() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Initializing MainActivityCoordinator")
        
        val coordinatorCallback = object : MainActivityCoordinator.CoordinatorCallback {
            override fun updateStatusText(text: String) {
                runOnUiThread {
                    binding.statusText.text = text
                }
            }
            
            override fun showToast(message: String, duration: Int) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, message, duration).show()
                }
            }
            
            override fun runOnUiThread(action: () -> Unit) {
                this@MainActivity.runOnUiThread(action)
            }
            
            override fun getContentView(): View = binding.root
            override fun getStreamingIndicator(): View? = binding.streamingIndicator
            override fun getStreamingLabel(): View? = binding.streamingLabel
            override fun getStreamingDebugOverlay(): TextView? = binding.streamingDebugOverlay
            
            override fun showPermissionButton(show: Boolean) {
                runOnUiThread {
                    binding.requestPermissionsButton.visibility = if (show) View.VISIBLE else View.GONE
                }
            }
            
            // UI Controller callback methods implementation
            override fun getContext(): Context = this@MainActivity
            override fun getStatusText(): TextView? = binding.statusText
            override fun getStartRecordingButton(): View? = binding.startRecordingButton
            override fun getStopRecordingButton(): View? = binding.stopRecordingButton
            override fun getCalibrationButton(): View? = binding.calibrationButton
            override fun getPcConnectionIndicator(): View? = binding.pcConnectionIndicator
            override fun getShimmerConnectionIndicator(): View? = binding.shimmerConnectionIndicator
            override fun getThermalConnectionIndicator(): View? = binding.thermalConnectionIndicator
            override fun getPcConnectionStatus(): TextView? = binding.pcConnectionStatus
            override fun getShimmerConnectionStatus(): TextView? = binding.shimmerConnectionStatus
            override fun getThermalConnectionStatus(): TextView? = binding.thermalConnectionStatus
            override fun getBatteryLevelText(): TextView? = binding.batteryLevelText
            override fun getRecordingIndicator(): View? = binding.recordingIndicator
            override fun getRequestPermissionsButton(): View? = binding.requestPermissionsButton
            override fun getShimmerStatusText(): TextView? = binding.shimmerStatusText
        }
        
        mainActivityCoordinator.initialize(coordinatorCallback)
        android.util.Log.d("MainActivity", "[DEBUG_LOG] MainActivityCoordinator initialized successfully")
    }
    
    /**
     * Initialize UIController integration with validation and error handling
     */
    private fun initializeUIControllerIntegration() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Initializing UIController integration")
        
        try {
            // Initialize UI components through UIController
            uiController.initializeUIComponents()
            
            // Validate UI components
            val validationResult = uiController.validateUIComponents()
            if (!validationResult.isValid) {
                android.util.Log.w("MainActivity", "[DEBUG_LOG] UI validation failed: ${validationResult.errors}")
                // Attempt recovery
                val recoveryResult = uiController.recoverFromUIErrors()
                if (recoveryResult.success) {
                    android.util.Log.d("MainActivity", "[DEBUG_LOG] UI recovery successful: ${recoveryResult.recoveryActions}")
                } else {
                    android.util.Log.e("MainActivity", "[DEBUG_LOG] UI recovery failed: ${recoveryResult.recoveryActions}")
                }
            } else {
                android.util.Log.d("MainActivity", "[DEBUG_LOG] UI validation passed: ${validationResult.componentCount} components available")
            }
            
            // Apply saved theme preferences
            uiController.applyThemeFromPreferences()
            
            // Enable accessibility features if needed
            val savedState = uiController.getSavedUIState()
            if (savedState.accessibilityMode) {
                uiController.enableAccessibilityFeatures()
            }
            
            android.util.Log.d("MainActivity", "[DEBUG_LOG] UIController integration completed successfully")
            
        } catch (e: Exception) {
            android.util.Log.e("MainActivity", "[DEBUG_LOG] Failed to initialize UIController integration: ${e.message}")
            Toast.makeText(this, "UI initialization error: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
    
    /**
     * Initialize consolidated UI components (legacy method - now delegated to UIController)
     */
    private fun initializeUIComponents() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Delegating UI component initialization to UIController")
        
        try {
            // Get consolidated components from UIController
            val consolidatedComponents = uiController.getConsolidatedComponents()
            
            // Initialize local references for backward compatibility
            consolidatedComponents.pcStatusIndicator?.let { pcStatusIndicator = it }
            consolidatedComponents.shimmerStatusIndicator?.let { shimmerStatusIndicator = it }
            consolidatedComponents.thermalStatusIndicator?.let { thermalStatusIndicator = it }
            consolidatedComponents.recordingButtonPair?.let { recordingButtonPair = it }
            
            android.util.Log.d("MainActivity", "[DEBUG_LOG] UI components delegated to UIController successfully")
            
        } catch (e: Exception) {
            android.util.Log.e("MainActivity", "[DEBUG_LOG] Failed to delegate UI components: ${e.message}")
            // Fallback to legacy initialization
            initializeLegacyUIComponents()
        }
    }
    
    /**
     * Fallback legacy UI component initialization
     */
    private fun initializeLegacyUIComponents() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Falling back to legacy UI component initialization")
        
        // Initialize StatusIndicatorView components
        pcStatusIndicator = StatusIndicatorView(this).apply {
            setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "PC: Waiting for PC...")
            setTextColor(android.R.color.white)
        }
        
        shimmerStatusIndicator = StatusIndicatorView(this).apply {
            setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Shimmer: Disconnected")
            setTextColor(android.R.color.white)
        }
        
        thermalStatusIndicator = StatusIndicatorView(this).apply {
            setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Thermal: Disconnected")
            setTextColor(android.R.color.white)
        }
        
        // Initialize ActionButtonPair for recording controls
        recordingButtonPair = ActionButtonPair(this).apply {
            setButtons("Start Recording", "Stop Recording")
            setOnClickListeners(
                { startRecording() },
                { stopRecording() }
            )
            setButtonsEnabled(true, false) // Initially only start is enabled
        }
        
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Legacy UI components initialized successfully")
    }

    /**
     * Observe ViewModel UiState using modern StateFlow pattern
     * This replaces multiple individual LiveData observers with a single centralized state observer
     * Following modern Android architecture guidelines for reactive UI
     */
    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUIFromState(state)
                }
            }
        }
    }

    /**
     * Update all UI elements from the centralized UiState
     * This method demonstrates the modern reactive UI pattern where the Activity
     * becomes much simpler and only needs to observe one state object
     */
    private fun updateUIFromState(state: com.multisensor.recording.ui.MainUiState) {
        // Update status text
        binding.statusText.text = state.statusText

        // Update consolidated recording controls
        recordingButtonPair.setButtonsEnabled(state.canStartRecording, state.canStopRecording)
        
        // Update legacy recording controls for backward compatibility
        binding.startRecordingButton.isEnabled = state.canStartRecording
        binding.stopRecordingButton.isEnabled = state.canStopRecording

        // Update calibration button
        binding.calibrationButton.isEnabled = state.canRunCalibration

        // Update consolidated status indicator components
        pcStatusIndicator.setStatus(
            if (state.isPcConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
            "PC: ${if (state.isPcConnected) "Connected" else "Waiting for PC..."}"
        )
        
        shimmerStatusIndicator.setStatus(
            if (state.isShimmerConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
            "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
        )
        
        thermalStatusIndicator.setStatus(
            if (state.isThermalConnected) StatusIndicatorView.StatusType.CONNECTED else StatusIndicatorView.StatusType.DISCONNECTED,
            "Thermal: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"
        )

        // Update legacy connection indicators for backward compatibility
        updateConnectionIndicator(binding.pcConnectionIndicator, state.isPcConnected)
        updateConnectionIndicator(binding.shimmerConnectionIndicator, state.isShimmerConnected)
        updateConnectionIndicator(binding.thermalConnectionIndicator, state.isThermalConnected)

        // Update legacy connection status texts for backward compatibility
        binding.pcConnectionStatus.text = "PC: ${if (state.isPcConnected) "Connected" else "Waiting for PC..."}"
        binding.shimmerConnectionStatus.text = "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Disconnected"}"
        binding.thermalConnectionStatus.text = "Thermal: ${if (state.isThermalConnected) "Connected" else "Disconnected"}"

        // Update battery level
        val batteryText = if (state.batteryLevel >= 0) {
            "Battery: ${state.batteryLevel}%"
        } else {
            "Battery: ---%"
        }
        binding.batteryLevelText.text = batteryText

        // Update recording indicator
        updateRecordingIndicator(state.isRecording)

        // Update streaming indicator and debug overlay
        updateStreamingIndicator(state.isStreaming, state.streamingFrameRate, state.streamingDataSize)

        // Update permissions button visibility
        binding.requestPermissionsButton.visibility = if (state.showPermissionsButton) View.VISIBLE else View.GONE

        // Handle error messages
        state.errorMessage?.let { errorMsg ->
            if (state.showErrorDialog) {
                Toast.makeText(this, errorMsg, Toast.LENGTH_LONG).show()
                // Clear error in ViewModel after showing
                viewModel.clearError()
            }
        }

        // Update session information if available
        state.currentSessionInfo?.let { sessionInfo ->
            updateSessionInfoDisplay(sessionInfo)
        }

        // Update hand segmentation for session changes
        state.recordingSessionId?.let { sessionId ->
            updateHandSegmentationForSession(sessionId)
        }

        // Update Shimmer status text
        val shimmerStatusText = when {
            state.shimmerDeviceInfo != null -> {
                "Shimmer GSR: ${state.shimmerDeviceInfo.deviceName} - Connected"
            }
            state.isShimmerConnected -> "Shimmer GSR: Connected"
            else -> "Shimmer GSR: Disconnected"
        }
        binding.shimmerStatusText.text = shimmerStatusText
        binding.shimmerStatusText.setTextColor(
            if (state.isShimmerConnected) Color.GREEN else Color.RED
        )
    }

    /**
     * Helper method to update connection indicators
     */
    private fun updateConnectionIndicator(indicator: View, isConnected: Boolean) {
        indicator.setBackgroundColor(if (isConnected) Color.GREEN else Color.RED)
    }

    /**
     * Helper method to update recording indicator
     */
    private fun updateRecordingIndicator(isRecording: Boolean) {
        binding.recordingIndicator.setBackgroundColor(
            if (isRecording) Color.RED else Color.GRAY
        )
    }

    /**
     * Helper method to update streaming indicator and debug overlay
     */
    private fun updateStreamingIndicator(isStreaming: Boolean, frameRate: Int, dataSize: String) {
        binding.streamingIndicator.setBackgroundColor(
            if (isStreaming) Color.GREEN else Color.GRAY
        )
        
        if (isStreaming && frameRate > 0) {
            binding.streamingDebugOverlay.text = "Streaming: ${frameRate}fps ($dataSize)"
            binding.streamingDebugOverlay.visibility = View.VISIBLE
            binding.streamingLabel.visibility = View.VISIBLE
        } else {
            binding.streamingDebugOverlay.visibility = View.GONE
            binding.streamingLabel.visibility = View.GONE
        }
    }

    private fun checkPermissions() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Starting permission check via PermissionManager...")

        if (permissionManager.areAllPermissionsGranted(this)) {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] All permissions already granted, initializing system")
            initializeRecordingSystemInternal()
        } else {
            android.util.Log.d("MainActivity", "[DEBUG_LOG] Requesting permissions via PermissionManager...")
            binding.statusText.text = "Requesting permissions..."

            // Use PermissionManager for permission requests
            permissionManager.requestPermissions(this, this)
        }

        // Update permission button visibility based on current permission status
        updatePermissionButtonVisibility()
    }

    private fun showTemporaryDenialMessage(
        temporarilyDenied: List<String>,
        grantedCount: Int,
        totalCount: Int,
    ) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Showing temporary denial message for ${temporarilyDenied.size} permissions")

        val message =
            "Some permissions were denied but can be requested again.\n\n" +
                "Denied permissions:\n" +
                temporarilyDenied.joinToString("\n") { "• ${getPermissionDisplayName(it)}" } +
                "\n\nYou can grant these permissions using the 'Request Permissions' button."

        Toast.makeText(this, message, Toast.LENGTH_LONG).show()

        binding.statusText.text = "Permissions: $grantedCount/$totalCount granted - Some permissions denied"

        android.util.Log.i("MainActivity", "Temporary permission denial: ${temporarilyDenied.joinToString(", ")}")
    }

    // Removed - now handled by PermissionController
    // private fun requestPermissionsManually() - moved to PermissionController.requestPermissionsManually()
    // private fun logCurrentPermissionStates() - moved to PermissionController.logCurrentPermissionStates()
    // private var hasCheckedPermissionsOnStartup - moved to PermissionController
    // private var permissionRetryCount - moved to PermissionController

    private fun getPermissionDisplayName(permission: String): String {
        return permissionController.getPermissionDisplayName(permission)
    }

    // Removed - now handled by PermissionController
    // private fun requestPermissionsManually() - moved to PermissionController.requestPermissionsManually()
    // private fun logCurrentPermissionStates() - moved to PermissionController.logCurrentPermissionStates()
    // private var hasCheckedPermissionsOnStartup - moved to PermissionController
    // private var permissionRetryCount - moved to PermissionController

    private fun launchNavigationMode() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Launching navigation mode")
        
        // Launch the MainNavigationActivity
        val intent = Intent(this, MainNavigationActivity::class.java)
        startActivity(intent)
        
        // Optionally finish this activity if you want to replace it
        // finish()
    }

    private fun updatePermissionButtonVisibility() {
        permissionController.updatePermissionButtonVisibility(this)
    }

    private fun initializeRecordingSystemInternal() {
        // Get TextureView from layout for camera preview
        val textureView = binding.texturePreview

        // Initialize system with TextureView for enhanced CameraRecorder integration
        viewModel.initializeSystem(textureView)
        binding.statusText.text = "System initialized - Ready to record"
    }

    private fun startRecording() {
        val intent =
            Intent(this, RecordingService::class.java).apply {
                action = RecordingService.ACTION_START_RECORDING
            }
        ContextCompat.startForegroundService(this, intent)
        viewModel.startRecording()
    }

    private fun stopRecording() {
        val intent =
            Intent(this, RecordingService::class.java).apply {
                action = RecordingService.ACTION_STOP_RECORDING
            }
        startService(intent)
        viewModel.stopRecording()
    }

    private fun runCalibration() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Starting calibration via CalibrationController")
        
        // Use CalibrationController for all calibration functionality
        calibrationController.runCalibration(lifecycleScope)
    }
    
    /**
     * Initialize CalibrationController with MainActivity callback
     */
    private fun initializeCalibrationController() {
        calibrationController.setCallback(object : CalibrationController.CalibrationCallback {
            override fun onCalibrationStarted() {
                updateStatusText("Calibration started...")
            }
            
            override fun onCalibrationCompleted(calibrationId: String) {
                updateStatusText("Calibration completed: $calibrationId")
                Toast.makeText(this@MainActivity, "✅ Calibration completed: $calibrationId", Toast.LENGTH_LONG).show()
            }
            
            override fun onCalibrationFailed(errorMessage: String) {
                updateStatusText("Calibration failed: $errorMessage")
                Toast.makeText(this@MainActivity, "❌ Calibration failed: $errorMessage", Toast.LENGTH_LONG).show()
            }
            
            override fun onSyncTestCompleted(success: Boolean, message: String) {
                val emoji = if (success) "✅" else "❌"
                Toast.makeText(this@MainActivity, "$emoji $message", Toast.LENGTH_LONG).show()
            }
            
            override fun updateStatusText(text: String) {
                runOnUiThread {
                    if (::binding.isInitialized) {
                        binding.statusText.text = text
                    }
                }
            }
            
            override fun showToast(message: String, duration: Int) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, message, duration).show()
                }
            }
            
            override fun runOnUiThread(action: () -> Unit) {
                this@MainActivity.runOnUiThread(action)
            }
            
            override fun getContentView(): View {
                return binding.root
            }
            
            override fun getContext(): Context {
                return this@MainActivity
            }
        })
        
        calibrationController.initialize()
    }

    /**
     * Triggers comprehensive calibration capture feedback - Enhanced for 
     */
    private fun triggerCalibrationCaptureSuccess(calibrationId: String = "unknown") {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Calibration photo captured - triggering feedback for ID: $calibrationId")

        // 1. Toast notification
        showCalibrationCaptureToast()

        // 2. Screen flash visual feedback
        triggerScreenFlash()

        // 3. Audio feedback (camera shutter sound)
        triggerCalibrationAudioFeedback()

        // 4. Visual cue for multi-angle calibration
        showCalibrationGuidance()
    }

    /**
     * Shows toast message for calibration photo capture
     */
    private fun showCalibrationCaptureToast() {
        Toast.makeText(this, "📸 Calibration photo captured!", Toast.LENGTH_SHORT).show()
    }

    /**
     * Triggers screen flash visual feedback
     */
    private fun triggerScreenFlash() {
        // Create a white overlay view for screen flash effect
        val flashOverlay =
            View(this).apply {
                setBackgroundColor(Color.WHITE)
                alpha = 0.8f
            }

        // Add overlay to the root view
        val rootView = findViewById<android.view.ViewGroup>(android.R.id.content)
        rootView.addView(
            flashOverlay,
            android.view.ViewGroup.LayoutParams(
                android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                android.view.ViewGroup.LayoutParams.MATCH_PARENT,
            ),
        )

        // Animate flash effect
        flashOverlay
            .animate()
            .alpha(0f)
            .setDuration(200) // 200ms flash duration
            .withEndAction {
                // Remove overlay after animation
                rootView.removeView(flashOverlay)
            }.start()

        android.util.Log.d("MainActivity", "[DEBUG_LOG] Screen flash visual feedback triggered")
    }

    /**
     * Triggers audio feedback using MediaActionSound
     */
    private fun triggerCalibrationAudioFeedback() {
        try {
            if (::mediaActionSound.isInitialized) {
                mediaActionSound.play(MediaActionSound.SHUTTER_CLICK)
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Camera shutter sound played for calibration")
            } else {
                android.util.Log.w("MainActivity", "[DEBUG_LOG] MediaActionSound not initialized, skipping audio feedback")
            }
        } catch (e: Exception) {
            android.util.Log.e("MainActivity", "[DEBUG_LOG] Error playing calibration audio feedback", e)
        }
    }

    /**
     * Shows visual cues for multi-angle calibration guidance
     */
    private fun showCalibrationGuidance() {
        // Show guidance message for multi-angle calibration
        val guidanceMessage = "✅ Photo captured! Move to next position for multi-angle calibration."

        // Update status text with guidance
        binding.statusText.text = guidanceMessage

        // Show additional toast with guidance
        Handler(Looper.getMainLooper()).postDelayed({
            Toast.makeText(this, "📐 Position device at different angle and capture again", Toast.LENGTH_LONG).show()
        }, 1000) // 1 second delay after initial feedback

        android.util.Log.d("MainActivity", "[DEBUG_LOG] Multi-angle calibration guidance displayed")
    }

    // ========== Sync Signal Testing Methods ==========

    /**
     * Test flash sync signal - 
     */
    private fun testFlashSync() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Testing flash sync signal")

        lifecycleScope.launch {
            try {
                // Trigger screen flash for sync testing
                runOnUiThread {
                    triggerScreenFlash()
                    Toast.makeText(this@MainActivity, "🔆 Flash sync signal triggered!", Toast.LENGTH_SHORT).show()
                }

                android.util.Log.d("MainActivity", "[DEBUG_LOG] Flash sync test completed successfully")
            } catch (e: Exception) {
                android.util.Log.e("MainActivity", "[DEBUG_LOG] Error during flash sync test", e)
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Flash sync test failed: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    /**
     * Test beep sync signal - 
     */
    private fun testBeepSync() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Testing beep sync signal")

        try {
            // Trigger audio beep for sync testing
            triggerCalibrationAudioFeedback()
            Toast.makeText(this, "🔊 Beep sync signal triggered!", Toast.LENGTH_SHORT).show()

            android.util.Log.d("MainActivity", "[DEBUG_LOG] Beep sync test completed successfully")
        } catch (e: Exception) {
            android.util.Log.e("MainActivity", "[DEBUG_LOG] Error during beep sync test", e)
            Toast.makeText(this, "Beep sync test failed: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    /**
     * Test clock synchronization - 
     */
    private fun testClockSync() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Testing clock synchronization")

        lifecycleScope.launch {
            try {
                // Simulate PC timestamp for testing
                val simulatedPcTimestamp = System.currentTimeMillis() + 1000 // 1 second ahead
                val syncId = "test_sync_${System.currentTimeMillis()}"

                val success = syncClockManager.synchronizeWithPc(simulatedPcTimestamp, syncId)

                runOnUiThread {
                    if (success) {
                        val syncStatus = syncClockManager.getSyncStatus()
                        val statusMessage = "✅ Clock sync successful!\nOffset: ${syncStatus.clockOffsetMs}ms\nSync ID: $syncId"
                        Toast.makeText(this@MainActivity, statusMessage, Toast.LENGTH_LONG).show()

                        // Update status text with sync info
                        binding.statusText.text = "Clock synchronized - Offset: ${syncStatus.clockOffsetMs}ms"

                        android.util.Log.d("MainActivity", "[DEBUG_LOG] Clock sync test successful: offset=${syncStatus.clockOffsetMs}ms")
                    } else {
                        Toast.makeText(this@MainActivity, "❌ Clock sync test failed", Toast.LENGTH_LONG).show()
                        android.util.Log.e("MainActivity", "[DEBUG_LOG] Clock sync test failed")
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e("MainActivity", "[DEBUG_LOG] Error during clock sync test", e)
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Clock sync test error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    /**
     * Display current sync status - 
     */
    private fun showSyncStatus() {
        val syncStatus = syncClockManager.getSyncStatus()
        val statistics = syncClockManager.getSyncStatistics()

        val statusMessage =
            buildString {
                appendLine("🕐 Clock Synchronization Status")
                appendLine("Synchronized: ${if (syncStatus.isSynchronized) "✅ Yes" else "❌ No"}")
                appendLine("Offset: ${syncStatus.clockOffsetMs}ms")
                appendLine("Last Sync: ${if (syncStatus.syncAge >= 0) "${syncStatus.syncAge}ms ago" else "Never"}")
                appendLine("Valid: ${if (syncClockManager.isSyncValid()) "✅ Yes" else "❌ No"}")
            }

        Toast.makeText(this, statusMessage, Toast.LENGTH_LONG).show()
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Sync status displayed: $statistics")
    }

    private fun updateRecordingUI(isRecording: Boolean) {
        binding.startRecordingButton.isEnabled = !isRecording
        binding.stopRecordingButton.isEnabled = isRecording
        binding.calibrationButton.isEnabled = !isRecording

        if (isRecording) {
            binding.recordingIndicator.setBackgroundColor(
                ContextCompat.getColor(this, android.R.color.holo_red_light),
            )
            binding.statusText.text = "Recording in progress..."
        } else {
            binding.recordingIndicator.setBackgroundColor(
                ContextCompat.getColor(this, android.R.color.darker_gray),
            )
            if (binding.statusText.text.contains("Recording")) {
                binding.statusText.text = "Recording stopped - Ready"
            }
        }

        // Update streaming UI indicators
        updateStreamingUI(isRecording)
    }

    /**
     * Update UI with SessionDisplayInfo data from UI state
     */
    private fun updateSessionInfoDisplay(sessionInfo: SessionDisplayInfo?) {
        if (sessionInfo != null) {
            // Update status text with session summary
            val sessionSummary = "Session ${sessionInfo.sessionId} - ${sessionInfo.status}"

            // Enhanced SessionInfo display with more details
            val displayText = when (sessionInfo.status) {
                "Active" -> {
                    "🔴 Recording: $sessionSummary"
                }
                "Completed" -> {
                    "✅ Completed: $sessionSummary"
                }
                else -> "📋 $sessionSummary"
            }
            
            binding.statusText.text = displayText

            // Log detailed session information
            android.util.Log.d("MainActivity", "SessionInfo updated: $sessionSummary")
        } else {
            // No active session
            val currentState = viewModel.uiState.value
            if (!currentState.isRecording) {
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
            ContextCompat.getColor(this, android.R.color.holo_green_light),
        )
        binding.streamingLabel.visibility = android.view.View.VISIBLE
    }

    /**
     * Hide streaming status indicator when preview streaming is stopped
     */
    private fun hideStreamingIndicator() {
        binding.streamingIndicator.setBackgroundColor(
            ContextCompat.getColor(this, android.R.color.darker_gray),
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
     * Launch ShimmerBluetoothDialog for device selection using modern Activity Result API
     */
    fun launchShimmerDeviceDialog() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Launching Shimmer device selection dialog via ShimmerController")
        shimmerController.launchShimmerDeviceDialog(this, shimmerDeviceSelectionLauncher)
    }

    /**
     * Show Shimmer sensor configuration dialog
     * Requires a connected Shimmer device
     */
    fun showShimmerSensorConfiguration() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Delegating Shimmer sensor configuration to ShimmerController")
        shimmerController.showShimmerSensorConfiguration(this, viewModel)
    }

    /**
     * Show Shimmer general configuration dialog
     * Requires a connected Shimmer device
     */
    fun showShimmerGeneralConfiguration() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Delegating Shimmer general configuration to ShimmerController")
        shimmerController.showShimmerGeneralConfiguration(this, viewModel)
    }

    /**
     * Start SD logging on connected Shimmer device
     */
    fun startShimmerSDLogging() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Delegating Shimmer SD logging start to ShimmerController")
        shimmerController.startShimmerSDLogging(viewModel)
    }

    /**
     * Stop SD logging on connected Shimmer device
     */
    fun stopShimmerSDLogging() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Delegating Shimmer SD logging stop to ShimmerController")
        shimmerController.stopShimmerSDLogging(viewModel)
    }

    // Menu Handling - UI Enhancement

    /**
     * Creates the options menu for MainActivity
     */
    override fun onCreateOptionsMenu(menu: android.view.Menu?): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    /**
     * Handles options menu item selections
     */
    override fun onOptionsItemSelected(item: android.view.MenuItem): Boolean =
        when (item.itemId) {
            R.id.action_settings -> {
                // Launch Settings Activity
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Opening Settings")
                val intent = Intent(this, com.multisensor.recording.ui.SettingsActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_network_config -> {
                // Launch Network Configuration Activity
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Opening Network Configuration")
                val intent = Intent(this, com.multisensor.recording.ui.NetworkConfigActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_file_browser -> {
                // Launch File Browser Activity
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Opening File Browser")
                val intent = Intent(this, com.multisensor.recording.ui.FileViewActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_shimmer_config -> {
                // Launch Shimmer Configuration Activity
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Opening Shimmer Configuration")
                val intent = Intent(this, com.multisensor.recording.ui.ShimmerConfigActivity::class.java)
                startActivity(intent)
                true
            }
            R.id.action_test_flash_sync -> {
                // Test Flash Sync Signal - 
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Testing Flash Sync")
                testFlashSync()
                true
            }
            R.id.action_test_beep_sync -> {
                // Test Beep Sync Signal - 
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Testing Beep Sync")
                testBeepSync()
                true
            }
            R.id.action_test_clock_sync -> {
                // Test Clock Synchronization - 
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Testing Clock Sync")
                testClockSync()
                true
            }
            R.id.action_sync_status -> {
                // Show Sync Status - 
                android.util.Log.d("MainActivity", "[DEBUG_LOG] Showing Sync Status")
                showSyncStatus()
                true
            }
            R.id.action_about -> {
                // Show About Dialog
                showAboutDialog()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }

    /**
     * Shows About dialog with app information
     */
    private fun showAboutDialog() {
        val aboutMessage =
            """
            Multi-Sensor Recording System
            
            Version: 1.0.0
            Build: Complete
            
            Features:
            • Real-time status monitoring
            • Manual recording controls
            • Calibration capture feedback
            • Comprehensive settings interface
            • Adaptive frame rate control
            
            Developed with ❤️ for multi-sensor data collection
            """.trimIndent()

        AlertDialog
            .Builder(this)
            .setTitle("About Multi-Sensor Recording")
            .setMessage(aboutMessage)
            .setIcon(R.drawable.ic_multisensor_idle)
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .show()

        android.util.Log.d("MainActivity", "[DEBUG_LOG] About dialog displayed")
    }

    // ===== Hand Segmentation Integration =====
    
    /**
     * Setup hand segmentation controls and integration
     */
    private fun setupHandSegmentation() {
        val handSegmentationControl = findViewById<HandSegmentationControlView>(R.id.handSegmentationControl)
        handSegmentationControl.setListener(this)
        
        // Initialize hand segmentation for current session if one exists
        viewModel.uiState.value.recordingSessionId?.let { sessionId ->
            handSegmentationManager.initializeForSession(sessionId, this)
        }
        
        logI("Hand segmentation controls initialized")
    }
    
    /**
     * Update hand segmentation controls when session changes
     */
    private fun updateHandSegmentationForSession(sessionId: String?) {
        sessionId?.let {
            handSegmentationManager.initializeForSession(it, this)
            val handSegmentationControl = findViewById<HandSegmentationControlView>(R.id.handSegmentationControl)
            handSegmentationControl.updateStatus(handSegmentationManager.getStatus())
            logI("Hand segmentation updated for session: $it")
        }
    }
    
    // ===== HandSegmentationManager.HandSegmentationListener Implementation =====
    
    override fun onHandDetectionStatusChanged(isEnabled: Boolean, handsDetected: Int) {
        runOnUiThread {
            val handSegmentationControl = findViewById<HandSegmentationControlView>(R.id.handSegmentationControl)
            handSegmentationControl.updateHandDetectionStatus(isEnabled, handsDetected)
        }
    }
    
    override fun onDatasetProgress(totalSamples: Int, leftHands: Int, rightHands: Int) {
        runOnUiThread {
            val handSegmentationControl = findViewById<HandSegmentationControlView>(R.id.handSegmentationControl)
            handSegmentationControl.updateDatasetProgress(totalSamples, leftHands, rightHands)
        }
    }
    
    override fun onDatasetSaved(datasetPath: String, totalSamples: Int) {
        runOnUiThread {
            val handSegmentationControl = findViewById<HandSegmentationControlView>(R.id.handSegmentationControl)
            handSegmentationControl.showDatasetSaved(datasetPath, totalSamples)
            Toast.makeText(this, "Dataset saved: $totalSamples samples", Toast.LENGTH_LONG).show()
        }
    }
    
    override fun onError(error: String) {
        runOnUiThread {
            val handSegmentationControl = findViewById<HandSegmentationControlView>(R.id.handSegmentationControl)
            handSegmentationControl.showError(error)
            android.util.Log.e("MainActivity", "Error: $error")
            binding.statusText.text = "Error: $error"
            Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        }
    }
    
    // ===== HandSegmentationControlView.HandSegmentationControlListener Implementation =====
    
    override fun onHandSegmentationToggled(enabled: Boolean) {
        handSegmentationManager.setEnabled(enabled)
        logI("Hand segmentation ${if (enabled) "enabled" else "disabled"}")
    }
    
    override fun onRealTimeProcessingToggled(enabled: Boolean) {
        handSegmentationManager.setRealTimeProcessing(enabled)
        logI("Real-time hand processing ${if (enabled) "enabled" else "disabled"}")
    }
    
    override fun onCroppedDatasetToggled(enabled: Boolean) {
        handSegmentationManager.setCroppedDatasetEnabled(enabled)
        logI("Cropped dataset creation ${if (enabled) "enabled" else "disabled"}")
    }
    
    override fun onSaveDatasetClicked() {
        handSegmentationManager.saveCroppedDataset { success, datasetPath, totalSamples ->
            runOnUiThread {
                if (success && datasetPath != null) {
                    logI("Hand dataset saved successfully: $datasetPath")
                } else {
                    Toast.makeText(this, "Failed to save dataset", Toast.LENGTH_SHORT).show()
                    logE("Failed to save hand dataset")
                }
            }
        }
    }
    
    override fun onClearDatasetClicked() {
        AlertDialog.Builder(this)
            .setTitle("Clear Dataset")
            .setMessage("Are you sure you want to clear the current hand dataset? This action cannot be undone.")
            .setPositiveButton("Clear") { _, _ ->
                handSegmentationManager.clearCurrentDataset()
                Toast.makeText(this, "Dataset cleared", Toast.LENGTH_SHORT).show()
                logI("Hand dataset cleared")
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroy() {
        super.onDestroy()

        // Stop USB monitoring
        usbController.stopPeriodicScanning()

        // Ensure recording service is stopped when activity is destroyed
        if (viewModel.uiState.value.isRecording) {
            stopRecording()
        }

        // Cleanup Status Display System - UI Enhancements
        try {
            // Unregister battery receiver
            unregisterReceiver(batteryReceiver)
        } catch (e: Exception) {
            android.util.Log.w("MainActivity", "[DEBUG_LOG] Battery receiver was not registered or already unregistered")
        }

        // Cleanup MediaActionSound
        if (::mediaActionSound.isInitialized) {
            mediaActionSound.release()
        }

        // Remove all Handler callbacks to prevent memory leaks
        if (::statusUpdateHandler.isInitialized) {
            statusUpdateHandler.removeCallbacksAndMessages(null)
        }

        // Cleanup hand segmentation
        handSegmentationManager.cleanup()

        // Cleanup CalibrationController
        if (::calibrationController.isInitialized) {
            calibrationController.cleanup()
        }

        android.util.Log.d("MainActivity", "[DEBUG_LOG] Status monitoring system cleaned up")
    }

    // ========== PermissionController.PermissionCallback Implementation ==========
    
    override fun onAllPermissionsGranted() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] All permissions granted via PermissionManager")
        initializeRecordingSystemInternal()
        binding.statusText.text = "All permissions granted - System ready"
    }

    override fun onPermissionsTemporarilyDenied(deniedPermissions: List<String>, grantedCount: Int, totalCount: Int) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Permissions temporarily denied: ${deniedPermissions.size}")
        binding.statusText.text = "Permissions: $grantedCount/$totalCount granted - Some permissions denied"
    }

    override fun onPermissionsPermanentlyDenied(deniedPermissions: List<String>) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Permissions permanently denied: ${deniedPermissions.size}")
        binding.statusText.text = "Permissions required - Please enable in Settings"
    }
    
    override fun onPermissionCheckStarted() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Permission check started")
        binding.statusText.text = "Checking permissions..."
    }
    
    override fun onPermissionRequestCompleted() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Permission request completed")
        // Final status will be set by other callbacks
    }
    
    override fun updateStatusText(text: String) {
        binding.statusText.text = text
    }
    
    override fun showPermissionButton(show: Boolean) {
        binding.requestPermissionsButton.visibility = if (show) android.view.View.VISIBLE else android.view.View.GONE
    }

    // ========== ShimmerController.ShimmerCallback Implementation ==========
    
    override fun onDeviceSelected(address: String, name: String) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Shimmer device selected via ShimmerController:")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Address: $address")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Name: $name")
        
        selectedShimmerAddress = address
        selectedShimmerName = name
        
        // Show BLE/Classic connection type selection dialog
        shimmerController.showBtTypeConnectionOption(this)
    }

    override fun onDeviceSelectionCancelled() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Shimmer device selection cancelled")
        showToast("Device selection cancelled")
    }

    override fun onConnectionStatusChanged(connected: Boolean) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Shimmer connection status changed: $connected")
        updateShimmerConnectionStatus(connected)
        
        val statusMessage = if (connected) "Shimmer device connected" else "Shimmer device disconnected"
        updateStatusText(statusMessage)
        showToast(statusMessage)
    }

    override fun onConfigurationComplete() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Shimmer configuration completed")
        updateStatusText("Shimmer configuration completed")
        showToast("Shimmer configuration completed")
    }

    override fun onShimmerError(message: String) {
        android.util.Log.e("MainActivity", "[DEBUG_LOG] Shimmer Controller error: $message")
        updateStatusText("Shimmer Error: $message")
        showToast("Shimmer Error: $message", Toast.LENGTH_LONG)
    }

    override fun updateStatusText(text: String) {
        runOnUiThread {
            binding.statusText.text = text
        }
    }

    override fun showToast(message: String, duration: Int) {
        runOnUiThread {
            Toast.makeText(this, message, duration).show()
        }
    }

    override fun runOnUiThread(action: () -> Unit) {
        runOnUiThread(action)
    }

    // ========== UsbController.UsbCallback Implementation ==========
    
    override fun onSupportedDeviceAttached(device: UsbDevice) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Supported USB device attached via UsbController")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Device: ${device.deviceName}")
        
        // Update thermal connection status
        updateThermalConnectionStatus(true)
        
        Toast.makeText(this, "TOPDON thermal camera connected: ${device.deviceName}", Toast.LENGTH_SHORT).show()
    }

    override fun onUnsupportedDeviceAttached(device: UsbDevice) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Unsupported USB device attached")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Device: ${device.deviceName}")
        
        Toast.makeText(this, "Unsupported USB device: ${device.deviceName}", Toast.LENGTH_SHORT).show()
    }

    override fun onDeviceDetached(device: UsbDevice) {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] USB device detached")
        android.util.Log.d("MainActivity", "[DEBUG_LOG] - Device: ${device.deviceName}")
        
        // Update thermal connection status
        updateThermalConnectionStatus(false)
        
        Toast.makeText(this, "USB device disconnected: ${device.deviceName}", Toast.LENGTH_SHORT).show()
    }

    override fun onUsbError(message: String) {
        android.util.Log.e("MainActivity", "[DEBUG_LOG] USB Controller error: $message")
        binding.statusText.text = "USB Error: $message"
        Toast.makeText(this, "USB Error: $message", Toast.LENGTH_LONG).show()
    }

    override fun updateStatusText(text: String) {
        binding.statusText.text = text
    }

    override fun initializeRecordingSystem() {
        android.util.Log.d("MainActivity", "[DEBUG_LOG] Initializing recording system from USB controller")
        // Call the private initializeRecordingSystem method
        this.initializeRecordingSystemInternal()
    }

    override fun areAllPermissionsGranted(): Boolean {
        return AllAndroidPermissions.getDangerousPermissions().all { permission ->
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
        }
    }
}
