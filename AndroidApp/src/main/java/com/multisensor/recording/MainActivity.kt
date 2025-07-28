package com.multisensor.recording

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.ui.MainViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Main activity for the Multi-Sensor Recording System.
 * Provides the primary user interface for controlling recording sessions,
 * viewing camera previews, and monitoring system status.
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    
    // Required permissions for multi-sensor recording
    private val requiredPermissions = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.WRITE_EXTERNAL_STORAGE,
        Manifest.permission.READ_EXTERNAL_STORAGE,
        Manifest.permission.BLUETOOTH,
        Manifest.permission.BLUETOOTH_ADMIN,
        Manifest.permission.ACCESS_FINE_LOCATION // Required for Bluetooth scanning
    )
    
    // Permission request launcher
    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            initializeRecordingSystem()
        } else {
            showPermissionDeniedMessage()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize view binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        
        // Setup UI
        setupUI()
        
        // Check and request permissions
        checkPermissions()
        
        // Observe ViewModel state
        observeViewModel()
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
        val missingPermissions = requiredPermissions.filter { permission ->
            ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED
        }
        
        if (missingPermissions.isNotEmpty()) {
            permissionLauncher.launch(missingPermissions.toTypedArray())
        } else {
            initializeRecordingSystem()
        }
    }
    
    private fun initializeRecordingSystem() {
        // Get TextureView from layout for camera preview
        val textureView = binding.texturePreview
        
        // Initialize system with TextureView for enhanced CameraRecorder integration
        viewModel.initializeSystem(textureView)
        binding.statusText.text = "System initialized - Ready to record"
    }
    
    private fun showPermissionDeniedMessage() {
        Toast.makeText(
            this,
            "All permissions are required for multi-sensor recording",
            Toast.LENGTH_LONG
        ).show()
        binding.statusText.text = "Permissions required - Please grant all permissions"
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
    
    override fun onDestroy() {
        super.onDestroy()
        // Ensure recording service is stopped when activity is destroyed
        if (viewModel.isRecording.value == true) {
            stopRecording()
        }
    }
}