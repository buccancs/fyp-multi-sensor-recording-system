package com.multisensor.recording.fragment

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.LayoutInflater
import android.view.SurfaceView
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.multisensor.recording.R
import com.multisensor.recording.camera.RgbCamera
import com.multisensor.recording.camera.ThermalCamera
import com.multisensor.recording.sensor.GsrSensor
import com.multisensor.recording.calibration.SyncClockManager
import com.multisensor.recording.session.SessionManager
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Recording Fragment - Multi-sensor recording controls and previews
 * Contains the original recording functionality from MainActivity
 */
class RecordingFragment : Fragment() {
    
    companion object {
        private const val TAG = "RecordingFragment"
    }

    // UI components
    private lateinit var cameraPreview: PreviewView
    private lateinit var thermalPreview: SurfaceView
    private lateinit var recordButton: Button
    private lateinit var recordingTimer: TextView
    private lateinit var cameraStatus: TextView
    private lateinit var thermalStatus: TextView
    private lateinit var cameraConnectionStatus: TextView
    private lateinit var thermalConnectionStatus: TextView
    private lateinit var gsrConnectionStatus: TextView
    private lateinit var syncStatus: TextView

    // Core components
    private lateinit var rgbCamera: RgbCamera
    private lateinit var thermalCamera: ThermalCamera
    private lateinit var gsrSensor: GsrSensor
    private lateinit var syncClockManager: SyncClockManager
    private lateinit var sessionManager: SessionManager

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

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_recording, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        initializeViews(view)
        initializeComponents()
    }

    private fun initializeViews(view: View) {
        cameraPreview = view.findViewById(R.id.camera_preview)
        thermalPreview = view.findViewById(R.id.thermal_preview)
        recordButton = view.findViewById(R.id.record_button)
        recordingTimer = view.findViewById(R.id.recording_timer)
        
        cameraStatus = view.findViewById(R.id.camera_status)
        thermalStatus = view.findViewById(R.id.thermal_status)
        
        cameraConnectionStatus = view.findViewById(R.id.camera_connection_status)
        thermalConnectionStatus = view.findViewById(R.id.thermal_connection_status)
        gsrConnectionStatus = view.findViewById(R.id.gsr_connection_status)
        syncStatus = view.findViewById(R.id.sync_status)

        recordButton.setOnClickListener {
            if (isRecording.get()) {
                stopRecording()
            } else {
                startRecording()
            }
        }
    }

    private fun initializeComponents() {
        requireContext().let { context ->
            rgbCamera = RgbCamera(context)
            thermalCamera = ThermalCamera(context)
            gsrSensor = GsrSensor(context)
            syncClockManager = SyncClockManager()
            sessionManager = SessionManager(context)
        }
        
        initializeDevices()
    }

    private fun initializeDevices() {
        Thread {
            // Initialize RGB camera
            val rgbInitialized = rgbCamera.initialize(cameraPreview, requireActivity())
            activity?.runOnUiThread {
                updateCameraStatus(rgbInitialized)
            }

            // Initialize thermal camera
            val thermalInitialized = thermalCamera.initialize(thermalPreview)
            activity?.runOnUiThread {
                updateThermalStatus(thermalInitialized)
            }

            // Initialize GSR sensor
            val gsrInitialized = gsrSensor.initialize()
            activity?.runOnUiThread {
                updateGsrStatus(gsrInitialized)
            }

            // Auto-connect to GSR sensor if available
            if (gsrInitialized) {
                gsrSensor.scanForDevices { devices ->
                    if (devices.isNotEmpty()) {
                        val deviceAddress = devices.first().substringAfter("(").substringBefore(")")
                        val connected = gsrSensor.connect(deviceAddress)
                        activity?.runOnUiThread {
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

    private fun startRecording() {
        if (!allDevicesReady()) {
            Toast.makeText(requireContext(), "Not all devices are ready", Toast.LENGTH_SHORT).show()
            return
        }

        Thread {
            try {
                // Create new session
                val session = sessionManager.createSession()
                if (session == null) {
                    activity?.runOnUiThread {
                        Toast.makeText(requireContext(), "Failed to create session", Toast.LENGTH_SHORT).show()
                    }
                    return@Thread
                }

                // Start session
                if (!sessionManager.startSession()) {
                    activity?.runOnUiThread {
                        Toast.makeText(requireContext(), "Failed to start session", Toast.LENGTH_SHORT).show()
                    }
                    return@Thread
                }

                // Get synchronized timestamp
                val syncedTimestamp = syncClockManager.getCurrentSyncedTime()
                val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date(syncedTimestamp))
                val sessionDir = sessionManager.getSessionDirectory()

                Log.i(TAG, "Starting recording session: ${session.sessionId}")
                
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
                    recordingStartTime = syncedTimestamp
                    
                    activity?.runOnUiThread {
                        recordButton.text = "Stop Recording"
                        recordButton.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.red))
                        timerHandler.post(timerRunnable)
                        Toast.makeText(requireContext(), "Recording started (Session: ${session.sessionId})", Toast.LENGTH_SHORT).show()
                    }
                    
                    Log.i(TAG, "Multi-sensor recording started for session: ${session.sessionId}")
                } else {
                    sessionManager.terminateSession("Failed to start all recording streams")
                    activity?.runOnUiThread {
                        Toast.makeText(requireContext(), "Failed to start recording", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting recording", e)
                sessionManager.terminateSession("Recording error: ${e.message}")
                activity?.runOnUiThread {
                    Toast.makeText(requireContext(), "Recording error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }

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

                activity?.runOnUiThread {
                    recordButton.text = "Start Recording"
                    recordButton.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.primary))
                    recordingTimer.text = "00:00"
                    timerHandler.removeCallbacks(timerRunnable)
                    
                    val sessionId = session?.sessionId ?: "unknown"
                    Toast.makeText(requireContext(), "Recording stopped (Session: $sessionId)", Toast.LENGTH_SHORT).show()
                }

                Log.i(TAG, "Multi-sensor recording stopped")

            } catch (e: Exception) {
                Log.e(TAG, "Error stopping recording", e)
                activity?.runOnUiThread {
                    Toast.makeText(requireContext(), "Error stopping recording: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }

    private fun allDevicesReady(): Boolean {
        return rgbCamera.isConnected() && 
               thermalCamera.isConnected() && 
               gsrSensor.isConnected()
    }

    private fun updateRecordingTimer() {
        val currentTime = syncClockManager.getCurrentSyncedTime()
        val elapsed = (currentTime - recordingStartTime) / 1000
        val minutes = elapsed / 60
        val seconds = elapsed % 60
        recordingTimer.text = String.format("%02d:%02d", minutes, seconds)
    }

    private fun updateCameraStatus(initialized: Boolean) {
        cameraStatus.text = if (initialized) "Ready" else "Error"
        cameraStatus.setTextColor(ContextCompat.getColor(requireContext(), if (initialized) R.color.green else R.color.red))
        
        cameraConnectionStatus.text = if (rgbCamera.isConnected()) "Connected" else "Disconnected"
        cameraConnectionStatus.setTextColor(ContextCompat.getColor(requireContext(), if (rgbCamera.isConnected()) R.color.green else R.color.red))
    }

    private fun updateThermalStatus(initialized: Boolean) {
        thermalStatus.text = if (initialized) "Ready" else "Error"
        thermalStatus.setTextColor(ContextCompat.getColor(requireContext(), if (initialized) R.color.green else R.color.red))
        
        thermalConnectionStatus.text = if (thermalCamera.isConnected()) "Connected" else "Disconnected"
        thermalConnectionStatus.setTextColor(ContextCompat.getColor(requireContext(), if (thermalCamera.isConnected()) R.color.green else R.color.red))
    }

    private fun updateGsrStatus(initialized: Boolean) {
        gsrConnectionStatus.text = if (initialized) "Initialized" else "Error"
        gsrConnectionStatus.setTextColor(ContextCompat.getColor(requireContext(), if (initialized) R.color.orange else R.color.red))
    }

    private fun updateGsrConnectionStatus(connected: Boolean) {
        gsrConnectionStatus.text = if (connected) "Connected" else "Disconnected"
        gsrConnectionStatus.setTextColor(ContextCompat.getColor(requireContext(), if (connected) R.color.green else R.color.red))
    }

    private suspend fun performTimeSync(): Boolean {
        return try {
            val simulatedPcTimestamp = System.currentTimeMillis() + 100L
            val success = syncClockManager.synchronizeWithPc(simulatedPcTimestamp, "manual_sync")
            
            activity?.runOnUiThread {
                updateSyncStatus()
            }
            
            success
        } catch (e: Exception) {
            Log.e(TAG, "Time synchronization failed", e)
            false
        }
    }

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
        syncStatus.setTextColor(ContextCompat.getColor(requireContext(), color))
    }

    override fun onDestroy() {
        super.onDestroy()
        
        // Stop recording if active
        if (isRecording.get()) {
            stopRecording()
        }
        
        // Release all resources
        if (::rgbCamera.isInitialized) rgbCamera.release()
        if (::thermalCamera.isInitialized) thermalCamera.release()
        if (::gsrSensor.isInitialized) gsrSensor.release()
        
        timerHandler.removeCallbacks(timerRunnable)
        
        Log.i(TAG, "RecordingFragment destroyed, all resources released")
    }
}