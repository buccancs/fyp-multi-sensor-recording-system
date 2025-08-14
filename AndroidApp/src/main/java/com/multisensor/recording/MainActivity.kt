package com.multisensor.recording

import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.SurfaceView
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.multisensor.recording.camera.RgbCamera
import com.multisensor.recording.camera.ThermalCamera
import com.multisensor.recording.calibration.SyncClockManager
import com.multisensor.recording.calibration.CalibrationManager
import com.multisensor.recording.sensor.GsrSensor
import com.multisensor.recording.util.PermissionManager
import com.multisensor.recording.session.SessionManager
import com.multisensor.recording.network.PcCommunicationClient
import com.multisensor.recording.network.FaultToleranceManager
import com.multisensor.recording.network.DataTransferManager
import com.multisensor.recording.network.DeviceType
import com.multisensor.recording.network.DeviceStatus
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Streamlined MainActivity - simplified from the complex original
 * Focuses on core IRCamera functionality with minimal dependencies
 */
class MainActivity : ComponentActivity() {
    
    companion object {
        private const val TAG = "MainActivity"
    }

    // UI components
    private lateinit var cameraPreview: PreviewView
    private lateinit var thermalPreview: SurfaceView
    private lateinit var recordButton: Button
    private lateinit var recordingTimer: TextView
    private lateinit var cameraStatus: TextView
    private lateinit var thermalStatus: TextView
    private lateinit var gsrStatus: TextView
    private lateinit var cameraConnectionStatus: TextView
    private lateinit var thermalConnectionStatus: TextView
    private lateinit var gsrConnectionStatus: TextView
    private lateinit var syncStatus: TextView

    // Core components
    private lateinit var permissionManager: PermissionManager
    private lateinit var rgbCamera: RgbCamera
    private lateinit var thermalCamera: ThermalCamera
    private lateinit var gsrSensor: GsrSensor
    private lateinit var syncClockManager: SyncClockManager
    
    // New functional requirement components
    private lateinit var sessionManager: SessionManager
    private lateinit var pcCommunicationClient: PcCommunicationClient
    private lateinit var faultToleranceManager: FaultToleranceManager
    private lateinit var dataTransferManager: DataTransferManager
    private lateinit var calibrationManager: CalibrationManager

    // Recording state
    private val isRecording = AtomicBoolean(false)
    private var recordingStartTime = 0L
    private val timerHandler = Handler(Looper.getMainLooper())
    private val timerRunnable = object : Runnable {
        override fun run() {
            if (isRecording.get()) {
                updateRecordingTimer()
                timerHandler.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        Log.i(TAG, "Starting streamlined Multi-Sensor Recording App")
        
        initializeViews()
        initializeComponents()
        requestPermissions()
    }

    /**
     * Initialize UI views
     */
    private fun initializeViews() {
        cameraPreview = findViewById(R.id.camera_preview)
        thermalPreview = findViewById(R.id.thermal_preview)
        recordButton = findViewById(R.id.record_button)
        recordingTimer = findViewById(R.id.recording_timer)
        
        cameraStatus = findViewById(R.id.camera_status)
        thermalStatus = findViewById(R.id.thermal_status)
        
        cameraConnectionStatus = findViewById(R.id.camera_connection_status)
        thermalConnectionStatus = findViewById(R.id.thermal_connection_status)
        gsrConnectionStatus = findViewById(R.id.gsr_connection_status)
        syncStatus = findViewById(R.id.sync_status)

        recordButton.setOnClickListener {
            if (isRecording.get()) {
                stopRecording()
            } else {
                startRecording()
            }
        }
    }

    /**
     * Initialize core components
     */
    private fun initializeComponents() {
        permissionManager = PermissionManager(this)
        rgbCamera = RgbCamera(this)
        thermalCamera = ThermalCamera(this)
        gsrSensor = GsrSensor(this)
        syncClockManager = SyncClockManager()
        
        // Initialize new functional requirement components
        sessionManager = SessionManager(this)
        pcCommunicationClient = PcCommunicationClient()
        faultToleranceManager = FaultToleranceManager(this)
        dataTransferManager = DataTransferManager(this)
        calibrationManager = CalibrationManager(this)
        
        // Setup callbacks and integration
        setupComponentCallbacks()
        
        // Update initial sync status
        updateSyncStatus()
    }

    /**
     * Request all required permissions
     */
    private fun requestPermissions() {
        permissionManager.requestAllPermissions(this) { granted ->
            if (granted) {
                Log.i(TAG, "All permissions granted")
                initializeDevices()
            } else {
                Log.w(TAG, "Permissions denied")
                Toast.makeText(this, "App requires all permissions to function", Toast.LENGTH_LONG).show()
            }
        }
    }

    /**
     * Initialize all devices
     */
    private fun initializeDevices() {
        Thread {
            // Register devices with fault tolerance manager
            faultToleranceManager.registerDevice("rgb_camera", DeviceType.RGB_CAMERA) {
                rgbCamera.initialize(cameraPreview, this@MainActivity)
            }
            
            faultToleranceManager.registerDevice("thermal_camera", DeviceType.THERMAL_CAMERA) {
                thermalCamera.initialize(thermalPreview)
            }
            
            faultToleranceManager.registerDevice("gsr_sensor", DeviceType.GSR_SENSOR) {
                gsrSensor.initialize()
            }

            // Initialize RGB camera
            val rgbInitialized = rgbCamera.initialize(cameraPreview, this)
            runOnUiThread {
                updateCameraStatus(rgbInitialized)
                faultToleranceManager.updateDeviceHealth(
                    "rgb_camera", 
                    if (rgbInitialized) DeviceStatus.CONNECTED else DeviceStatus.ERROR
                )
            }

            // Initialize thermal camera
            val thermalInitialized = thermalCamera.initialize(thermalPreview)
            runOnUiThread {
                updateThermalStatus(thermalInitialized)
                faultToleranceManager.updateDeviceHealth(
                    "thermal_camera", 
                    if (thermalInitialized) DeviceStatus.CONNECTED else DeviceStatus.ERROR
                )
            }

            // Initialize GSR sensor
            val gsrInitialized = gsrSensor.initialize()
            runOnUiThread {
                updateGsrStatus(gsrInitialized)
                faultToleranceManager.updateDeviceHealth(
                    "gsr_sensor", 
                    if (gsrInitialized) DeviceStatus.CONNECTED else DeviceStatus.ERROR
                )
            }

            // Auto-connect to GSR sensor if available
            if (gsrInitialized) {
                gsrSensor.scanForDevices { devices ->
                    if (devices.isNotEmpty()) {
                        // Auto-connect to first available device
                        val deviceAddress = devices.first().substringAfter("(").substringBefore(")")
                        val connected = gsrSensor.connect(deviceAddress)
                        runOnUiThread {
                            updateGsrConnectionStatus(connected)
                        }
                    }
                }
            }

            // Perform initial time synchronization
            lifecycleScope.launch {
                Log.i(TAG, "Attempting initial time synchronization...")
                val syncSuccess = performTimeSync()
                Log.i(TAG, "Initial time sync ${if (syncSuccess) "successful" else "failed"}")
            }

            // Attempt to connect to PC server (if configured)
            attemptPcConnection()

            Log.i(TAG, "Device initialization completed")
        }.start()
    }

    /**
     * Start recording session
     */
    private fun startRecording() {
        if (!allDevicesReady()) {
            Toast.makeText(this, "Not all devices are ready", Toast.LENGTH_SHORT).show()
            return
        }

        Thread {
            try {
                // Create new session
                val session = sessionManager.createSession()
                if (session == null) {
                    runOnUiThread {
                        Toast.makeText(this, "Failed to create session", Toast.LENGTH_SHORT).show()
                    }
                    return@Thread
                }

                // Start session
                if (!sessionManager.startSession()) {
                    runOnUiThread {
                        Toast.makeText(this, "Failed to start session", Toast.LENGTH_SHORT).show()
                    }
                    return@Thread
                }

                // Get synchronized timestamp for consistent timing across all devices
                val syncedTimestamp = syncClockManager.getCurrentSyncedTime()
                val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date(syncedTimestamp))
                val sessionDir = sessionManager.getSessionDirectory()

                Log.i(TAG, "Starting recording session: ${session.sessionId} with synchronized timestamp: $syncedTimestamp")
                
                // Start RGB recording
                val rgbFile = File(sessionDir, "rgb_$timestamp.mp4")
                val rgbStarted = rgbCamera.startRecording(rgbFile)
                if (rgbStarted) {
                    sessionManager.addRecordedFile("rgb_video", rgbFile.absolutePath, rgbFile.length())
                }

                // Start thermal recording
                val thermalStarted = thermalCamera.startRecording()
                if (thermalStarted) {
                    sessionManager.addRecordedFile("thermal_video", "thermal_$timestamp.raw", 0L)
                }

                // Start GSR streaming
                val gsrStarted = gsrSensor.startStreaming()
                if (gsrStarted) {
                    val gsrFile = File(sessionDir, "gsr_$timestamp.csv")
                    sessionManager.addRecordedFile("gsr_data", gsrFile.absolutePath, 0L)
                }

                if (rgbStarted && thermalStarted && gsrStarted) {
                    isRecording.set(true)
                    recordingStartTime = syncedTimestamp // Use synced time for consistent timing
                    
                    runOnUiThread {
                        recordButton.text = getString(R.string.stop_recording)
                        recordButton.setBackgroundColor(ContextCompat.getColor(this, R.color.red))
                        timerHandler.post(timerRunnable)
                        Toast.makeText(this, "Recording started (Session: ${session.sessionId})", Toast.LENGTH_SHORT).show()
                    }
                    
                    Log.i(TAG, "Multi-sensor recording started with time sync for session: ${session.sessionId}")
                } else {
                    // Recording failed, terminate session
                    sessionManager.terminateSession("Failed to start all recording streams")
                    runOnUiThread {
                        Toast.makeText(this, "Failed to start recording", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting recording", e)
                sessionManager.terminateSession("Recording error: ${e.message}")
                runOnUiThread {
                    Toast.makeText(this, "Recording error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }

    /**
     * Stop recording session
     */
    private fun stopRecording() {
        Thread {
            try {
                val session = sessionManager.getCurrentSession()
                
                // Stop all recordings
                rgbCamera.stopRecording()
                thermalCamera.stopRecording()
                gsrSensor.stopStreaming()

                isRecording.set(false)
                
                // Stop session
                sessionManager.stopSession()

                runOnUiThread {
                    recordButton.text = getString(R.string.start_recording)
                    recordButton.setBackgroundColor(ContextCompat.getColor(this, R.color.primary))
                    recordingTimer.text = "00:00"
                    timerHandler.removeCallbacks(timerRunnable)
                    
                    val sessionId = session?.sessionId ?: "unknown"
                    Toast.makeText(this, "Recording stopped (Session: $sessionId)", Toast.LENGTH_SHORT).show()
                }

                Log.i(TAG, "Multi-sensor recording stopped")
                
                // Start automatic file transfer to PC if connected
                session?.let { sessionInfo ->
                    if (pcCommunicationClient.isConnected()) {
                        Log.i(TAG, "Starting automatic file transfer for session: ${sessionInfo.sessionId}")
                        dataTransferManager.uploadSessionData(sessionInfo, getPcAddress())
                    }
                }

            } catch (e: Exception) {
                Log.e(TAG, "Error stopping recording", e)
                runOnUiThread {
                    Toast.makeText(this, "Error stopping recording: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }

    /**
     * Check if all devices are ready for recording
     */
    private fun allDevicesReady(): Boolean {
        return rgbCamera.isConnected() && 
               thermalCamera.isConnected() && 
               gsrSensor.isConnected()
    }

    /**
     * Update recording timer display
     */
    private fun updateRecordingTimer() {
        val currentTime = syncClockManager.getCurrentSyncedTime()
        val elapsed = (currentTime - recordingStartTime) / 1000
        val minutes = elapsed / 60
        val seconds = elapsed % 60
        recordingTimer.text = String.format("%02d:%02d", minutes, seconds)
    }

    /**
     * Update camera status display
     */
    private fun updateCameraStatus(initialized: Boolean) {
        cameraStatus.text = if (initialized) "Ready" else "Error"
        cameraStatus.setTextColor(ContextCompat.getColor(this, if (initialized) R.color.green else R.color.red))
        
        cameraConnectionStatus.text = if (rgbCamera.isConnected()) "Connected" else "Disconnected"
        cameraConnectionStatus.setTextColor(ContextCompat.getColor(this, if (rgbCamera.isConnected()) R.color.green else R.color.red))
    }

    /**
     * Update thermal camera status display
     */
    private fun updateThermalStatus(initialized: Boolean) {
        thermalStatus.text = if (initialized) "Ready" else "Error"
        thermalStatus.setTextColor(ContextCompat.getColor(this, if (initialized) R.color.green else R.color.red))
        
        thermalConnectionStatus.text = if (thermalCamera.isConnected()) "Connected" else "Disconnected"
        thermalConnectionStatus.setTextColor(ContextCompat.getColor(this, if (thermalCamera.isConnected()) R.color.green else R.color.red))
    }

    /**
     * Update GSR sensor status display
     */
    private fun updateGsrStatus(initialized: Boolean) {
        gsrConnectionStatus.text = if (initialized) "Initialized" else "Error"
        gsrConnectionStatus.setTextColor(ContextCompat.getColor(this, if (initialized) R.color.orange else R.color.red))
    }

    /**
     * Update GSR connection status display
     */
    private fun updateGsrConnectionStatus(connected: Boolean) {
        gsrConnectionStatus.text = if (connected) "Connected" else "Disconnected"
        gsrConnectionStatus.setTextColor(ContextCompat.getColor(this, if (connected) R.color.green else R.color.red))
    }

    /**
     * Update time synchronization status display
     */
    private fun updateSyncStatus() {
        val syncStatusInfo = syncClockManager.getSyncStatus()
        val isValid = syncClockManager.isSyncValid()
        
        val statusText = when {
            syncStatusInfo.isSynchronized && isValid -> "Synced (${syncStatusInfo.clockOffsetMs}ms)"
            syncStatusInfo.isSynchronized && !isValid -> "Expired"
            else -> "Not Synced"
        }
        
        val color = when {
            syncStatusInfo.isSynchronized && isValid -> R.color.green
            syncStatusInfo.isSynchronized && !isValid -> R.color.orange
            else -> R.color.red
        }
        
        syncStatus.text = statusText
        syncStatus.setTextColor(ContextCompat.getColor(this, color))
    }

    /**
     * Perform time synchronization with PC
     * This is a demo implementation - in real usage, PC timestamp would come from network
     */
    private suspend fun performTimeSync(): Boolean {
        return try {
            // Demo: simulate PC timestamp (in real implementation, this would come from PC server)
            val simulatedPcTimestamp = System.currentTimeMillis() + 100L // Simulate 100ms offset
            val success = syncClockManager.synchronizeWithPc(simulatedPcTimestamp, "manual_sync")
            
            runOnUiThread {
                updateSyncStatus()
            }
            
            success
        } catch (e: Exception) {
            Log.e(TAG, "Time synchronization failed", e)
            false
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        
        // Stop recording if active
        if (isRecording.get()) {
            stopRecording()
        }
        
        // Release all resources
        rgbCamera.release()
        thermalCamera.release()
        gsrSensor.release()
        
        // Cleanup new components
        pcCommunicationClient.cleanup()
        faultToleranceManager.cleanup()
        dataTransferManager.cleanup()
        
        timerHandler.removeCallbacks(timerRunnable)
        
        Log.i(TAG, "MainActivity destroyed, resources released")
    }

    /**
     * Setup callbacks for new functional requirement components
     */
    private fun setupComponentCallbacks() {
        // PC Communication callbacks
        pcCommunicationClient.setCommandCallback { command ->
            handlePcCommand(command)
        }
        
        pcCommunicationClient.setConnectionCallback { connected, message ->
            runOnUiThread {
                if (connected) {
                    Toast.makeText(this, "Connected to PC server", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "PC connection lost: $message", Toast.LENGTH_SHORT).show()
                }
            }
        }
        
        // Fault tolerance callbacks
        faultToleranceManager.setDeviceRecoveryCallback { deviceId, success, message ->
            runOnUiThread {
                if (success) {
                    Toast.makeText(this, "Device $deviceId recovered", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Device $deviceId recovery failed: $message", Toast.LENGTH_SHORT).show()
                }
            }
        }
        
        faultToleranceManager.setSystemHealthCallback { isHealthy, deviceHealthMap ->
            // Update UI with system health status
            runOnUiThread {
                // You could update a system health indicator here
            }
        }
        
        // Data transfer callbacks
        dataTransferManager.setTransferProgressCallback { fileName, bytesTransferred, totalBytes, progress ->
            runOnUiThread {
                // Update transfer progress in UI
                Log.d(TAG, "Transfer progress: $fileName - ${progress.toInt()}%")
            }
        }
        
        dataTransferManager.setTransferCompleteCallback { success, errorMessage, results ->
            runOnUiThread {
                if (success) {
                    Toast.makeText(this, "Session data uploaded successfully", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Upload failed: $errorMessage", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    /**
     * Handle commands received from PC server
     */
    private fun handlePcCommand(command: com.multisensor.recording.network.PcCommand) {
        when (command.action) {
            "start_recording" -> {
                runOnUiThread {
                    if (!isRecording.get()) {
                        startRecording()
                    }
                }
                pcCommunicationClient.sendResponse(command.action, true, "Recording started")
            }
            
            "stop_recording" -> {
                runOnUiThread {
                    if (isRecording.get()) {
                        stopRecording()
                    }
                }
                pcCommunicationClient.sendResponse(command.action, true, "Recording stopped")
            }
            
            "sync_signal" -> {
                // Handle synchronization signal (e.g., flash screen)
                val signalType = command.parameters["signalType"] as? String ?: "flash"
                performSyncSignal(signalType)
                pcCommunicationClient.sendResponse(command.action, true, "Sync signal executed")
            }
            
            "get_status" -> {
                val status = org.json.JSONObject().apply {
                    put("isRecording", isRecording.get())
                    put("sessionActive", sessionManager.isActive())
                    put("deviceHealth", faultToleranceManager.isSystemHealthy())
                    put("syncStatus", syncClockManager.isSyncValid())
                }
                pcCommunicationClient.sendResponse(command.action, true, "Status retrieved", status)
            }
            
            else -> {
                Log.w(TAG, "Unknown PC command: ${command.action}")
                pcCommunicationClient.sendResponse(command.action, false, "Unknown command")
            }
        }
    }

    /**
     * Perform synchronization signal (screen flash, etc.)
     */
    private fun performSyncSignal(signalType: String) {
        when (signalType) {
            "flash" -> {
                // Flash screen white briefly for visual sync marker
                runOnUiThread {
                    val originalColor = window.decorView.background
                    window.decorView.setBackgroundColor(android.graphics.Color.WHITE)
                    
                    Handler(Looper.getMainLooper()).postDelayed({
                        window.decorView.background = originalColor
                    }, 100) // Flash for 100ms
                }
            }
            // Add other signal types as needed
        }
        
        Log.i(TAG, "Executed sync signal: $signalType")
    }

    /**
     * Attempt to connect to PC server
     */
    private fun attemptPcConnection() {
        // Try to connect to PC on local network
        // In a real implementation, this could use network discovery or configuration
        val pcAddress = getPcAddress()
        if (pcAddress.isNotEmpty()) {
            lifecycleScope.launch {
                val connected = pcCommunicationClient.connectToPc(pcAddress)
                Log.i(TAG, "PC connection attempt: ${if (connected) "success" else "failed"}")
            }
        }
    }

    /**
     * Get PC server address (placeholder implementation)
     */
    private fun getPcAddress(): String {
        // In a real implementation, this could come from:
        // - Network discovery
        // - User configuration
        // - Default gateway detection
        return "192.168.1.100" // Placeholder
    }
}