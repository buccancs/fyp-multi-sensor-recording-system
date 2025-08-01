package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDevice
import android.view.TextureView
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.ActivityResultLauncher
import androidx.lifecycle.LifecycleCoroutineScope
import com.multisensor.recording.ui.MainViewModel
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Main coordinator that orchestrates interactions between all feature controllers.
 * This class serves as the central coordination point for MainActivity, managing
 * communication and dependencies between different feature controllers.
 * 
 * Follows the Coordinator pattern to reduce MainActivity complexity and improve
 * separation of concerns while maintaining feature integration.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for coordinator scenarios
 * TODO: Implement coordinator state persistence across app restarts
 * TODO: Add coordinator-level error handling and recovery
 * TODO: Implement feature dependency validation and management
 */
@Singleton
class MainActivityCoordinator @Inject constructor(
    private val permissionController: PermissionController,
    private val usbController: UsbController,
    private val shimmerController: ShimmerController,
    private val recordingController: RecordingController,
    private val calibrationController: CalibrationController,
    private val networkController: NetworkController,
    private val statusDisplayController: StatusDisplayController,
    private val uiController: UIController,
    private val menuController: MenuController
) {
    
    /**
     * Interface for coordinator callbacks to MainActivity
     */
    interface CoordinatorCallback {
        fun updateStatusText(text: String)
        fun showToast(message: String, duration: Int = Toast.LENGTH_SHORT)
        fun runOnUiThread(action: () -> Unit)
        fun getContentView(): View
        fun getStreamingIndicator(): View?
        fun getStreamingLabel(): View?
        fun getStreamingDebugOverlay(): TextView?
        fun showPermissionButton(show: Boolean)
        
        // UI Controller callback methods
        fun getContext(): android.content.Context
        fun getStatusText(): TextView?
        fun getStartRecordingButton(): View?
        fun getStopRecordingButton(): View?
        fun getCalibrationButton(): View?
        fun getPcConnectionIndicator(): View?
        fun getShimmerConnectionIndicator(): View?
        fun getThermalConnectionIndicator(): View?
        fun getPcConnectionStatus(): TextView?
        fun getShimmerConnectionStatus(): TextView?
        fun getThermalConnectionStatus(): TextView?
        fun getBatteryLevelText(): TextView?
        fun getRecordingIndicator(): View?
        fun getRequestPermissionsButton(): View?
        fun getShimmerStatusText(): TextView?
    }
    
    private var callback: CoordinatorCallback? = null
    private var isInitialized = false
    
    /**
     * Initialize the coordinator and all feature controllers
     */
    fun initialize(callback: CoordinatorCallback) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Initializing coordinator with all feature controllers")
        
        this.callback = callback
        
        // Initialize all controllers with their respective callbacks
        setupPermissionController()
        setupUsbController()
        setupShimmerController()
        setupRecordingController()
        setupCalibrationController()
        setupNetworkController()
        setupStatusDisplayController()
        setupUIController()
        setupMenuController()
        
        isInitialized = true
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinator initialization complete")
    }
    
    /**
     * Setup PermissionController with callback
     */
    private fun setupPermissionController() {
        permissionController.setCallback(object : PermissionController.PermissionCallback {
            override fun onAllPermissionsGranted() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] All permissions granted - initializing recording system")
                // Coordinate with recording controller to initialize system
                // This will be implemented when MainActivity integration is complete
            }
            
            override fun onPermissionsTemporarilyDenied(deniedPermissions: List<String>, grantedCount: Int, totalCount: Int) {
                callback?.updateStatusText("Permissions: $grantedCount/$totalCount granted - Some permissions denied")
            }
            
            override fun onPermissionsPermanentlyDenied(deniedPermissions: List<String>) {
                callback?.updateStatusText("Permissions required - Please enable in Settings")
            }
            
            override fun onPermissionCheckStarted() {
                callback?.updateStatusText("Checking permissions...")
            }
            
            override fun onPermissionRequestCompleted() {
                // Permission request completed - update UI accordingly
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showPermissionButton(show: Boolean) {
                callback?.showPermissionButton(show)
            }
        })
    }
    
    /**
     * Setup UsbController with callback
     */
    private fun setupUsbController() {
        usbController.setCallback(object : UsbController.UsbCallback {
            override fun onSupportedDeviceAttached(device: UsbDevice) {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Supported USB device attached - coordinating with other controllers")
                callback?.updateStatusText("Topdon thermal camera connected - Ready for recording")
            }
            
            override fun onUnsupportedDeviceAttached(device: UsbDevice) {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Unsupported USB device attached")
            }
            
            override fun onDeviceDetached(device: UsbDevice) {
                callback?.updateStatusText("USB device disconnected")
            }
            
            override fun onUsbError(message: String) {
                callback?.showToast("USB Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun initializeRecordingSystem() {
                // Coordinate with recording controller
                // This will be implemented when MainActivity integration is complete
            }
            
            override fun areAllPermissionsGranted(): Boolean {
                // Coordinate with permission controller
                return callback?.getContext()?.let { context ->
                    permissionController.areAllPermissionsGranted(context)
                } ?: false
            }
        })
    }
    
    /**
     * Setup ShimmerController with callback
     */
    private fun setupShimmerController() {
        shimmerController.setCallback(object : ShimmerController.ShimmerCallback {
            override fun onDeviceSelected(address: String, name: String) {
                callback?.updateStatusText("Shimmer device selected: $name")
            }
            
            override fun onDeviceSelectionCancelled() {
                callback?.updateStatusText("Shimmer device selection cancelled")
            }
            
            override fun onConnectionStatusChanged(connected: Boolean) {
                val status = if (connected) "connected" else "disconnected"
                callback?.updateStatusText("Shimmer device $status")
            }
            
            override fun onConfigurationComplete() {
                callback?.showToast("Shimmer configuration completed")
            }
            
            override fun onShimmerError(message: String) {
                callback?.showToast("Shimmer Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showToast(message: String, duration: Int) {
                callback?.showToast(message, duration)
            }
            
            override fun runOnUiThread(action: () -> Unit) {
                callback?.runOnUiThread(action)
            }
        })
    }
    
    /**
     * Setup RecordingController with callback
     */
    private fun setupRecordingController() {
        recordingController.setCallback(object : RecordingController.RecordingCallback {
            override fun onRecordingInitialized() {
                callback?.updateStatusText("Recording system initialized - Ready to record")
            }
            
            override fun onRecordingStarted() {
                callback?.updateStatusText("Recording in progress...")
                // Coordinate with network controller to update streaming UI
                callback?.getContext()?.let { context ->
                    networkController.updateStreamingUI(context, true)
                }
            }
            
            override fun onRecordingStopped() {
                callback?.updateStatusText("Recording stopped - Processing data...")
                // Coordinate with network controller to update streaming UI
                callback?.getContext()?.let { context ->
                    networkController.updateStreamingUI(context, false)
                }
            }
            
            override fun onRecordingError(message: String) {
                callback?.showToast("Recording Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showToast(message: String, duration: Int) {
                callback?.showToast(message, duration)
            }
        })
    }
    
    /**
     * Setup CalibrationController with callback
     */
    private fun setupCalibrationController() {
        calibrationController.setCallback(object : CalibrationController.CalibrationCallback {
            override fun onCalibrationStarted() {
                callback?.updateStatusText("Calibration in progress...")
            }
            
            override fun onCalibrationCompleted(calibrationId: String) {
                callback?.updateStatusText("Calibration completed - ID: $calibrationId")
            }
            
            override fun onCalibrationFailed(errorMessage: String) {
                callback?.showToast("Calibration failed: $errorMessage", Toast.LENGTH_LONG)
            }
            
            override fun onSyncTestCompleted(success: Boolean, message: String) {
                val status = if (success) "✅" else "❌"
                callback?.showToast("$status $message")
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showToast(message: String, duration: Int) {
                callback?.showToast(message, duration)
            }
            
            override fun runOnUiThread(action: () -> Unit) {
                callback?.runOnUiThread(action)
            }
            
            override fun getContentView(): View {
                return callback?.getContentView() ?: throw IllegalStateException("Content view not available")
            }
            
            override fun getContext(): Context {
                return callback?.getContext() ?: throw IllegalStateException("Context not available")
            }
        })
    }
    
    /**
     * Setup NetworkController with callback
     */
    private fun setupNetworkController() {
        networkController.setCallback(object : NetworkController.NetworkCallback {
            override fun onStreamingStarted() {
                callback?.updateStatusText("Streaming started")
            }
            
            override fun onStreamingStopped() {
                callback?.updateStatusText("Streaming stopped")
            }
            
            override fun onNetworkStatusChanged(connected: Boolean) {
                val status = if (connected) "connected" else "disconnected"
                callback?.updateStatusText("Network $status")
            }
            
            override fun onStreamingError(message: String) {
                callback?.showToast("Streaming Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showToast(message: String, duration: Int) {
                callback?.showToast(message, duration)
            }
            
            override fun getStreamingIndicator(): View? {
                return callback?.getStreamingIndicator()
            }
            
            override fun getStreamingLabel(): View? {
                return callback?.getStreamingLabel()
            }
            
            override fun getStreamingDebugOverlay(): TextView? {
                return callback?.getStreamingDebugOverlay()
            }
        })
    }
    
    /**
     * Setup StatusDisplayController with callback
     */
    private fun setupStatusDisplayController() {
        statusDisplayController.setCallback(object : StatusDisplayController.StatusDisplayCallback {
            override fun onBatteryLevelChanged(level: Int, color: Int) {
                // Battery level updates handled by controller
            }
            
            override fun onConnectionStatusChanged(type: StatusDisplayController.ConnectionType, connected: Boolean) {
                val statusText = when (type) {
                    StatusDisplayController.ConnectionType.PC -> if (connected) "PC connected" else "PC disconnected"
                    StatusDisplayController.ConnectionType.SHIMMER -> if (connected) "Shimmer connected" else "Shimmer disconnected"
                    StatusDisplayController.ConnectionType.THERMAL -> if (connected) "Thermal connected" else "Thermal disconnected"
                }
                callback?.updateStatusText(statusText)
            }
            
            override fun onStatusMonitoringInitialized() {
                callback?.updateStatusText("Status monitoring initialized")
            }
            
            override fun onStatusMonitoringError(message: String) {
                callback?.showToast("Status Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun runOnUiThread(action: () -> Unit) {
                callback?.runOnUiThread(action)
            }
            
            override fun registerBroadcastReceiver(receiver: android.content.BroadcastReceiver, filter: android.content.IntentFilter): android.content.Intent? {
                // Simple delegation to callback - remove complex error handling
                return try {
                    callback?.getContext()?.registerReceiver(receiver, filter)
                } catch (e: Exception) {
                    android.util.Log.e("MainActivityCoordinator", "Failed to register broadcast receiver", e)
                    null
                }
            }
            
            override fun unregisterBroadcastReceiver(receiver: android.content.BroadcastReceiver) {
                try {
                    callback?.getContext()?.unregisterReceiver(receiver)
                } catch (e: Exception) {
                    android.util.Log.e("MainActivityCoordinator", "Failed to unregister broadcast receiver", e)
                }
            }
            
            override fun getBatteryLevelText(): TextView? {
                return callback?.getBatteryLevelText()
            }
            
            override fun getPcConnectionStatus(): TextView? {
                return callback?.getPcConnectionStatus()
            }
            
            override fun getPcConnectionIndicator(): View? {
                return callback?.getPcConnectionIndicator()
            }
            
            override fun getShimmerConnectionStatus(): TextView? {
                // Get Shimmer connection status text view access via coordinator callback
                return callback?.getShimmerConnectionStatus()
            }
            
            override fun getShimmerConnectionIndicator(): View? {
                // Get Shimmer connection indicator view access via coordinator callback
                return callback?.getShimmerConnectionIndicator()
            }
            
            override fun getThermalConnectionStatus(): TextView? {
                return callback?.getThermalConnectionStatus()
            }
            
            override fun getThermalConnectionIndicator(): View? {
                return callback?.getThermalConnectionIndicator()
            }
        })
    }
    
    /**
     * Setup UIController with callback
     */
    private fun setupUIController() {
        uiController.setCallback(object : UIController.UICallback {
            override fun onUIComponentsInitialized() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] UI components initialized")
            }
            
            override fun onUIStateUpdated(state: com.multisensor.recording.ui.MainUiState) {
                // UI state updated - handled by controller
            }
            
            override fun onUIError(message: String) {
                callback?.showToast("UI Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showToast(message: String, duration: Int) {
                callback?.showToast(message, duration)
            }
            
            override fun runOnUiThread(action: () -> Unit) {
                callback?.runOnUiThread(action)
            }
            
            override fun getContext(): android.content.Context {
                return callback?.getContext() ?: throw IllegalStateException("Context not available")
            }
            
            override fun getStatusText(): TextView? {
                return callback?.getStatusText()
            }
            
            override fun getStartRecordingButton(): View? {
                return callback?.getStartRecordingButton()
            }
            
            override fun getStopRecordingButton(): View? {
                return callback?.getStopRecordingButton()
            }
            
            override fun getCalibrationButton(): View? {
                return callback?.getCalibrationButton()
            }
            
            override fun getPcConnectionIndicator(): View? {
                return callback?.getPcConnectionIndicator()
            }
            
            override fun getShimmerConnectionIndicator(): View? {
                return callback?.getShimmerConnectionIndicator()
            }
            
            override fun getThermalConnectionIndicator(): View? {
                return callback?.getThermalConnectionIndicator()
            }
            
            override fun getPcConnectionStatus(): TextView? {
                return callback?.getPcConnectionStatus()
            }
            
            override fun getShimmerConnectionStatus(): TextView? {
                return callback?.getShimmerConnectionStatus()
            }
            
            override fun getThermalConnectionStatus(): TextView? {
                return callback?.getThermalConnectionStatus()
            }
            
            override fun getBatteryLevelText(): TextView? {
                return callback?.getBatteryLevelText()
            }
            
            override fun getRecordingIndicator(): View? {
                return callback?.getRecordingIndicator()
            }
            
            override fun getStreamingIndicator(): View? {
                return callback?.getStreamingIndicator()
            }
            
            override fun getStreamingLabel(): View? {
                return callback?.getStreamingLabel()
            }
            
            override fun getStreamingDebugOverlay(): TextView? {
                return callback?.getStreamingDebugOverlay()
            }
            
            override fun getRequestPermissionsButton(): View? {
                return callback?.getRequestPermissionsButton()
            }
            
            override fun getShimmerStatusText(): TextView? {
                return callback?.getShimmerStatusText()
            }
        })
    }
    
    /**
     * Setup MenuController with callback
     */
    private fun setupMenuController() {
        menuController.setCallback(object : MenuController.MenuCallback {
            override fun onMenuItemSelected(itemId: Int): Boolean {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Menu item selected: $itemId")
                return true
            }
            
            override fun onAboutDialogRequested() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] About dialog requested")
            }
            
            override fun onSettingsRequested() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Settings requested")
            }
            
            override fun onNetworkConfigRequested() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Network config requested")
            }
            
            override fun onFileBrowserRequested() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] File browser requested")
            }
            
            override fun onShimmerConfigRequested() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Shimmer config requested")
            }
            
            override fun onSyncTestRequested(testType: MenuController.SyncTestType) {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Sync test requested: $testType")
                // Coordinate with CalibrationController for sync tests
                when (testType) {
                    MenuController.SyncTestType.FLASH_SYNC -> {
                        callback?.showToast("Flash sync test requires lifecycleScope from MainActivity", Toast.LENGTH_SHORT)
                        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Flash sync test requested - requires MainActivity to call testFlashSync() directly")
                    }
                    MenuController.SyncTestType.BEEP_SYNC -> {
                        calibrationController.testBeepSync()
                    }
                    MenuController.SyncTestType.CLOCK_SYNC -> {
                        callback?.showToast("Clock sync test requires lifecycleScope from MainActivity", Toast.LENGTH_SHORT)
                        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Clock sync test requested - requires MainActivity to call testClockSync() directly")
                    }
                }
            }
            
            override fun onSyncStatusRequested() {
                android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Sync status requested")
                calibrationController.showSyncStatus()
            }
            
            override fun onMenuError(message: String) {
                callback?.showToast("Menu Error: $message", Toast.LENGTH_LONG)
            }
            
            override fun updateStatusText(text: String) {
                callback?.updateStatusText(text)
            }
            
            override fun showToast(message: String, duration: Int) {
                callback?.showToast(message, duration)
            }
            
            override fun getContext(): android.content.Context {
                return callback?.getContext() ?: throw IllegalStateException("Context not available")
            }
        })
    }
    
    // ========== Coordinated Feature Operations ==========
    
    /**
     * Check permissions through coordinator
     */
    fun checkPermissions(context: Context) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating permission check")
        permissionController.checkPermissions(context)
    }
    
    /**
     * Handle USB device intent through coordinator
     */
    fun handleUsbDeviceIntent(context: Context, intent: Intent) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating USB device intent handling")
        usbController.handleUsbDeviceIntent(context, intent)
    }
    
    /**
     * Initialize recording system through coordinator
     */
    fun initializeRecordingSystem(context: Context, textureView: TextureView, viewModel: MainViewModel) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating recording system initialization")
        
        // Initialize state persistence first
        recordingController.initializeStatePersistence(context)
        
        // Then initialize the recording system
        recordingController.initializeRecordingSystem(context, textureView, viewModel)
    }
    
    /**
     * Start recording through coordinator with quality validation
     */
    fun startRecording(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating recording start")
        
        // Validate prerequisites before starting
        if (!recordingController.validateRecordingPrerequisites(context)) {
            android.util.Log.w("MainActivityCoordinator", "[DEBUG_LOG] Recording prerequisites not met")
            return
        }
        
        // Check if current quality is suitable for available resources
        val currentQuality = recordingController.getCurrentQuality()
        if (!recordingController.validateQualityForResources(context, currentQuality)) {
            val recommendedQuality = recordingController.getRecommendedQuality(context)
            android.util.Log.w("MainActivityCoordinator", "[DEBUG_LOG] Current quality $currentQuality not suitable, switching to $recommendedQuality")
            recordingController.setRecordingQuality(recommendedQuality)
        }
        
        recordingController.startRecording(context, viewModel)
        networkController.updateStreamingUI(context, true)
    }
    
    /**
     * Stop recording through coordinator
     */
    fun stopRecording(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating recording stop")
        recordingController.stopRecording(context, viewModel)
        networkController.updateStreamingUI(context, false)
    }
    
    /**
     * Emergency stop recording through coordinator
     */
    fun emergencyStopRecording(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating emergency recording stop")
        recordingController.emergencyStopRecording(context, viewModel)
        networkController.updateStreamingUI(context, false)
    }
    
    /**
     * Set recording quality through coordinator
     */
    fun setRecordingQuality(context: Context, quality: RecordingController.RecordingQuality) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating recording quality change to $quality")
        
        if (recordingController.validateQualityForResources(context, quality)) {
            recordingController.setRecordingQuality(quality)
        } else {
            android.util.Log.w("MainActivityCoordinator", "[DEBUG_LOG] Quality $quality not suitable for current resources")
            callback?.showToast("Quality $quality not suitable for current storage/resources", android.widget.Toast.LENGTH_LONG)
        }
    }
    
    /**
     * Get recording status through coordinator
     */
    fun getRecordingStatus(): String {
        return recordingController.getRecordingStatus()
    }
    
    /**
     * Get current recording quality through coordinator
     */
    fun getCurrentRecordingQuality(): RecordingController.RecordingQuality {
        return recordingController.getCurrentQuality()
    }
    
    /**
     * Get available recording qualities through coordinator
     */
    fun getAvailableRecordingQualities(): Array<RecordingController.RecordingQuality> {
        return recordingController.getAvailableQualities()
    }
    
    /**
     * Run calibration through coordinator
     */
    fun runCalibration(lifecycleScope: LifecycleCoroutineScope) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating calibration run")
        calibrationController.runCalibration(lifecycleScope)
    }
    
    /**
     * Test flash sync signal through coordinator
     */
    fun testFlashSync(lifecycleScope: LifecycleCoroutineScope) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating flash sync test")
        calibrationController.testFlashSync(lifecycleScope)
    }
    
    /**
     * Test clock sync through coordinator
     */
    fun testClockSync(lifecycleScope: LifecycleCoroutineScope) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating clock sync test")
        calibrationController.testClockSync(lifecycleScope)
    }
    
    /**
     * Launch Shimmer device dialog through coordinator
     */
    fun launchShimmerDeviceDialog(activity: Activity, launcher: ActivityResultLauncher<Intent>) {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating Shimmer device dialog launch")
        shimmerController.launchShimmerDeviceDialog(activity, launcher)
    }
    
    /**
     * Create options menu through coordinator
     */
    fun createOptionsMenu(menu: android.view.Menu, activity: Activity): Boolean {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating options menu creation")
        return menuController.createOptionsMenu(menu, activity)
    }
    
    /**
     * Handle options menu item selection through coordinator
     */
    fun handleOptionsItemSelected(item: android.view.MenuItem): Boolean {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Coordinating menu item selection")
        return menuController.handleOptionsItemSelected(item)
    }
    
    /**
     * Get system status summary from all controllers
     */
    fun getSystemStatusSummary(context: Context): String {
        return buildString {
            append("=== System Status Summary ===\n")
            append("Coordinator Initialized: $isInitialized\n\n")
            append(permissionController.getPermissionRetryCount().let { "Permission Retries: $it\n" })
            append(usbController.getUsbStatusSummary(context))
            append("\n")
            append(shimmerController.getConnectionStatus())
            append("\n")
            append(recordingController.getRecordingStatus())
            append("\n")
            append(calibrationController.getCalibrationStatus())
            append("\n")
            append(networkController.getStreamingStatus())
            append("\n")
            
            // Add enhanced recording status
            append("=== Recording Controller Enhanced Status ===\n")
            val currentState = recordingController.getCurrentState()
            append("Current Quality: ${recordingController.getCurrentQuality().displayName}\n")
            append("Service Health: ${if (recordingController.isServiceHealthy()) "✓ Healthy" else "✗ Unhealthy"}\n")
            append("State Persistence: ${if (currentState.isInitialized) "✓ Active" else "✗ Inactive"}\n")
            append("Session Count: ${currentState.sessionCount}\n")
            append("Total Recording Time: ${formatDuration(currentState.totalRecordingTime)}\n")
            
            // Add service connection status
            val serviceState = recordingController.serviceConnectionState.value
            append("Service Connected: ${if (serviceState.isConnected) "✓ Yes" else "✗ No"}\n")
            if (serviceState.lastHeartbeat != null) {
                val timeSinceHeartbeat = System.currentTimeMillis() - serviceState.lastHeartbeat
                append("Last Heartbeat: ${timeSinceHeartbeat}ms ago\n")
            }
        }
    }
    
    /**
     * Format duration helper method
     */
    private fun formatDuration(millis: Long): String {
        val seconds = millis / 1000
        val hours = seconds / 3600
        val minutes = (seconds % 3600) / 60
        val remainingSeconds = seconds % 60
        
        return when {
            hours > 0 -> "${hours}h ${minutes}m ${remainingSeconds}s"
            minutes > 0 -> "${minutes}m ${remainingSeconds}s" 
            else -> "${remainingSeconds}s"
        }
    }
    
    /**
     * Reset all controller states
     */
    fun resetAllStates() {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Resetting all controller states")
        
        permissionController.resetState()
        shimmerController.resetState()
        recordingController.resetState()
        calibrationController.resetState()
        networkController.resetState()
        
        isInitialized = false
    }
    
    /**
     * Cleanup all controllers
     */
    fun cleanup() {
        android.util.Log.d("MainActivityCoordinator", "[DEBUG_LOG] Cleaning up all controllers")
        
        calibrationController.cleanup()
        // TODO: Add cleanup for other controllers as needed
        
        callback = null
        isInitialized = false
    }
}