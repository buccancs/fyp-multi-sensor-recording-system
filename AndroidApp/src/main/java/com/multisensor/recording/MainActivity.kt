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
import com.multisensor.recording.sensor.GsrSensor
import com.multisensor.recording.util.PermissionManager
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
            // Initialize RGB camera
            val rgbInitialized = rgbCamera.initialize(cameraPreview, this)
            runOnUiThread {
                updateCameraStatus(rgbInitialized)
            }

            // Initialize thermal camera
            val thermalInitialized = thermalCamera.initialize(thermalPreview)
            runOnUiThread {
                updateThermalStatus(thermalInitialized)
            }

            // Initialize GSR sensor
            val gsrInitialized = gsrSensor.initialize()
            runOnUiThread {
                updateGsrStatus(gsrInitialized)
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
            // Get synchronized timestamp for consistent timing across all devices
            val syncedTimestamp = syncClockManager.getCurrentSyncedTime()
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date(syncedTimestamp))
            val recordingDir = File(getExternalFilesDir(Environment.DIRECTORY_MOVIES), "recordings")
            if (!recordingDir.exists()) {
                recordingDir.mkdirs()
            }

            try {
                Log.i(TAG, "Starting recording with synchronized timestamp: $syncedTimestamp")
                
                // Start RGB recording
                val rgbFile = File(recordingDir, "rgb_$timestamp.mp4")
                val rgbStarted = rgbCamera.startRecording(rgbFile)

                // Start thermal recording
                val thermalStarted = thermalCamera.startRecording()

                // Start GSR streaming
                val gsrStarted = gsrSensor.startStreaming()

                if (rgbStarted && thermalStarted && gsrStarted) {
                    isRecording.set(true)
                    recordingStartTime = syncedTimestamp // Use synced time for consistent timing
                    
                    runOnUiThread {
                        recordButton.text = getString(R.string.stop_recording)
                        recordButton.setBackgroundColor(ContextCompat.getColor(this, R.color.red))
                        timerHandler.post(timerRunnable)
                        Toast.makeText(this, "Recording started (synced)", Toast.LENGTH_SHORT).show()
                    }
                    
                    Log.i(TAG, "Multi-sensor recording started with time sync")
                } else {
                    runOnUiThread {
                        Toast.makeText(this, "Failed to start recording", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting recording", e)
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
                // Stop all recordings
                rgbCamera.stopRecording()
                thermalCamera.stopRecording()
                gsrSensor.stopStreaming()

                isRecording.set(false)

                runOnUiThread {
                    recordButton.text = getString(R.string.start_recording)
                    recordButton.setBackgroundColor(ContextCompat.getColor(this, R.color.primary))
                    recordingTimer.text = "00:00"
                    timerHandler.removeCallbacks(timerRunnable)
                    Toast.makeText(this, "Recording stopped", Toast.LENGTH_SHORT).show()
                }

                Log.i(TAG, "Multi-sensor recording stopped")
            } catch (e: Exception) {
                Log.e(TAG, "Error stopping recording", e)
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
        
        timerHandler.removeCallbacks(timerRunnable)
        
        Log.i(TAG, "MainActivity destroyed, resources released")
    }
}