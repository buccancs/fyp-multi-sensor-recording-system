package com.multisensor.recording.ui

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for MainActivity that manages UI state and coordinates
 * with recording components and services.
 */
@HiltViewModel
class MainViewModel @Inject constructor(
    private val cameraRecorder: CameraRecorder,
    private val thermalRecorder: ThermalRecorder,
    private val shimmerRecorder: ShimmerRecorder,
    private val sessionManager: SessionManager,
    private val logger: Logger
) : ViewModel() {
    
    // Recording state
    private val _isRecording = MutableLiveData<Boolean>(false)
    val isRecording: LiveData<Boolean> = _isRecording
    
    // System status
    private val _systemStatus = MutableLiveData<String>("Initializing...")
    val systemStatus: LiveData<String> = _systemStatus
    
    // Error messages
    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage
    
    // Camera preview availability
    private val _cameraPreviewAvailable = MutableLiveData<Boolean>(false)
    val cameraPreviewAvailable: LiveData<Boolean> = _cameraPreviewAvailable
    
    // Thermal preview availability
    private val _thermalPreviewAvailable = MutableLiveData<Boolean>(false)
    val thermalPreviewAvailable: LiveData<Boolean> = _thermalPreviewAvailable
    
    // Shimmer connection status
    private val _shimmerConnected = MutableLiveData<Boolean>(false)
    val shimmerConnected: LiveData<Boolean> = _shimmerConnected
    
    init {
        logger.info("MainViewModel initialized")
    }
    
    /**
     * Initialize the recording system components
     */
    fun initializeSystem() {
        viewModelScope.launch {
            try {
                logger.info("Initializing recording system...")
                _systemStatus.value = "Initializing cameras and sensors..."
                
                // Initialize camera recorder
                val cameraInitialized = cameraRecorder.initialize()
                _cameraPreviewAvailable.value = cameraInitialized
                
                if (!cameraInitialized) {
                    _errorMessage.value = "Failed to initialize camera"
                    logger.error("Camera initialization failed")
                }
                
                // Initialize thermal recorder
                val thermalInitialized = thermalRecorder.initialize()
                _thermalPreviewAvailable.value = thermalInitialized
                
                if (!thermalInitialized) {
                    logger.warning("Thermal camera not available")
                }
                
                // Initialize Shimmer recorder
                val shimmerInitialized = shimmerRecorder.initialize()
                _shimmerConnected.value = shimmerInitialized
                
                if (!shimmerInitialized) {
                    logger.warning("Shimmer sensor not connected")
                }
                
                // Update system status
                val statusMessage = buildString {
                    append("System ready - ")
                    append("Camera: ${if (cameraInitialized) "OK" else "FAIL"}, ")
                    append("Thermal: ${if (thermalInitialized) "OK" else "N/A"}, ")
                    append("Shimmer: ${if (shimmerInitialized) "OK" else "N/A"}")
                }
                
                _systemStatus.value = statusMessage
                logger.info("System initialization complete: $statusMessage")
                
            } catch (e: Exception) {
                _errorMessage.value = "System initialization failed: ${e.message}"
                _systemStatus.value = "Initialization failed"
                logger.error("System initialization error", e)
            }
        }
    }
    
    /**
     * Start recording session
     */
    fun startRecording() {
        if (_isRecording.value == true) {
            logger.warning("Recording already in progress")
            return
        }
        
        viewModelScope.launch {
            try {
                logger.info("Starting recording session...")
                _systemStatus.value = "Starting recording..."
                
                // Create new session
                val sessionId = sessionManager.createNewSession()
                logger.info("Created new session: $sessionId")
                
                // Start all recorders
                val cameraStarted = cameraRecorder.startRecording(sessionId)
                val thermalStarted = thermalRecorder.startRecording(sessionId)
                val shimmerStarted = shimmerRecorder.startRecording(sessionId)
                
                if (cameraStarted) {
                    _isRecording.value = true
                    _systemStatus.value = "Recording in progress - Session: $sessionId"
                    logger.info("Recording started successfully")
                } else {
                    _errorMessage.value = "Failed to start camera recording"
                    logger.error("Failed to start camera recording")
                }
                
                // Log component status
                logger.info("Recording status - Camera: $cameraStarted, Thermal: $thermalStarted, Shimmer: $shimmerStarted")
                
            } catch (e: Exception) {
                _errorMessage.value = "Failed to start recording: ${e.message}"
                _systemStatus.value = "Recording start failed"
                logger.error("Recording start error", e)
            }
        }
    }
    
    /**
     * Stop recording session
     */
    fun stopRecording() {
        if (_isRecording.value != true) {
            logger.warning("No recording in progress")
            return
        }
        
        viewModelScope.launch {
            try {
                logger.info("Stopping recording session...")
                _systemStatus.value = "Stopping recording..."
                
                // Stop all recorders
                cameraRecorder.stopRecording()
                thermalRecorder.stopRecording()
                shimmerRecorder.stopRecording()
                
                // Finalize session
                sessionManager.finalizeCurrentSession()
                
                _isRecording.value = false
                _systemStatus.value = "Recording stopped - Ready"
                logger.info("Recording stopped successfully")
                
            } catch (e: Exception) {
                _errorMessage.value = "Error stopping recording: ${e.message}"
                logger.error("Recording stop error", e)
            }
        }
    }
    
    /**
     * Run calibration process
     */
    fun runCalibration() {
        viewModelScope.launch {
            try {
                logger.info("Starting calibration process...")
                _systemStatus.value = "Running calibration..."
                
                // TODO: Implement actual calibration logic
                // For now, this is a placeholder that simulates calibration
                
                // Simulate calibration delay
                kotlinx.coroutines.delay(2000)
                
                _systemStatus.value = "Calibration completed - Ready"
                logger.info("Calibration completed")
                
            } catch (e: Exception) {
                _errorMessage.value = "Calibration failed: ${e.message}"
                _systemStatus.value = "Calibration failed - Ready"
                logger.error("Calibration error", e)
            }
        }
    }
    
    /**
     * Clear error message after it's been displayed
     */
    fun clearError() {
        _errorMessage.value = null
    }
    
    override fun onCleared() {
        super.onCleared()
        logger.info("MainViewModel cleared")
        
        // Ensure recording is stopped when ViewModel is cleared
        if (_isRecording.value == true) {
            viewModelScope.launch {
                try {
                    cameraRecorder.stopRecording()
                    thermalRecorder.stopRecording()
                    shimmerRecorder.stopRecording()
                } catch (e: Exception) {
                    logger.error("Error stopping recording in onCleared", e)
                }
            }
        }
    }
}