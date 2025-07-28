package com.multisensor.recording.ui

import android.view.TextureView
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.SessionInfo
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
    
    // Enhanced CameraRecorder integration - SessionInfo tracking
    private val _currentSessionInfo = MutableLiveData<SessionInfo?>()
    val currentSessionInfo: LiveData<SessionInfo?> = _currentSessionInfo
    
    // Recording mode configuration
    private val _recordVideoEnabled = MutableLiveData<Boolean>(true)
    val recordVideoEnabled: LiveData<Boolean> = _recordVideoEnabled
    
    private val _captureRawEnabled = MutableLiveData<Boolean>(false)
    val captureRawEnabled: LiveData<Boolean> = _captureRawEnabled
    
    init {
        logger.info("MainViewModel initialized")
    }
    
    /**
     * Initialize the recording system components with TextureView for camera preview
     */
    fun initializeSystem(textureView: TextureView) {
        viewModelScope.launch {
            try {
                logger.info("Initializing recording system with TextureView...")
                _systemStatus.value = "Initializing cameras and sensors..."
                
                // Initialize camera recorder with TextureView for live preview
                val cameraInitialized = cameraRecorder.initialize(textureView)
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
     * Start recording session with enhanced CameraRecorder API
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
                
                // Get recording mode configuration
                val recordVideo = _recordVideoEnabled.value ?: true
                val captureRaw = _captureRawEnabled.value ?: false
                
                logger.info("Recording mode - Video: $recordVideo, RAW: $captureRaw")
                
                // Start enhanced camera recorder with session configuration
                val sessionInfo = cameraRecorder.startSession(recordVideo, captureRaw)
                
                if (sessionInfo != null) {
                    // Update SessionInfo LiveData
                    _currentSessionInfo.value = sessionInfo
                    
                    // Create legacy session for other recorders
                    val sessionId = sessionManager.createNewSession()
                    logger.info("Created legacy session: $sessionId for thermal/shimmer recorders")
                    
                    // Start other recorders with legacy API
                    val thermalStarted = thermalRecorder.startRecording(sessionId)
                    val shimmerStarted = shimmerRecorder.startRecording(sessionId)
                    
                    _isRecording.value = true
                    _systemStatus.value = "Recording in progress - ${sessionInfo.getSummary()}"
                    logger.info("Recording started successfully: ${sessionInfo.getSummary()}")
                    
                    // Log component status
                    logger.info("Recording status - Camera: SessionInfo, Thermal: $thermalStarted, Shimmer: $shimmerStarted")
                    
                } else {
                    _errorMessage.value = "Failed to start camera recording session"
                    logger.error("Failed to start camera recording session")
                }
                
            } catch (e: Exception) {
                _errorMessage.value = "Failed to start recording: ${e.message}"
                _systemStatus.value = "Recording start failed"
                logger.error("Recording start error", e)
            }
        }
    }
    
    /**
     * Stop recording session with enhanced CameraRecorder API
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
                
                // Stop enhanced camera recorder and get final SessionInfo
                val finalSessionInfo = cameraRecorder.stopSession()
                
                if (finalSessionInfo != null) {
                    // Update SessionInfo LiveData with final session data
                    _currentSessionInfo.value = finalSessionInfo
                    
                    logger.info("Camera session stopped: ${finalSessionInfo.getSummary()}")
                    
                    // Stop other recorders with legacy API
                    thermalRecorder.stopRecording()
                    shimmerRecorder.stopRecording()
                    
                    // Finalize legacy session
                    sessionManager.finalizeCurrentSession()
                    
                    _isRecording.value = false
                    _systemStatus.value = "Recording stopped - ${finalSessionInfo.getSummary()}"
                    logger.info("Recording stopped successfully: ${finalSessionInfo.getSummary()}")
                    
                } else {
                    logger.warning("No SessionInfo returned from camera recorder stop")
                    
                    // Fallback: stop other recorders anyway
                    thermalRecorder.stopRecording()
                    shimmerRecorder.stopRecording()
                    sessionManager.finalizeCurrentSession()
                    
                    _isRecording.value = false
                    _systemStatus.value = "Recording stopped - Ready"
                    logger.info("Recording stopped (no session info)")
                }
                
            } catch (e: Exception) {
                _errorMessage.value = "Error stopping recording: ${e.message}"
                _systemStatus.value = "Recording stop failed"
                logger.error("Recording stop error", e)
                
                // Ensure recording state is reset even on error
                _isRecording.value = false
                _currentSessionInfo.value = null
            }
        }
    }
    
    /**
     * Manually capture RAW image during active recording session
     */
    fun captureRawImage() {
        if (_isRecording.value != true) {
            _errorMessage.value = "No active recording session for RAW capture"
            logger.warning("Attempted RAW capture without active session")
            return
        }
        
        val currentSession = _currentSessionInfo.value
        if (currentSession?.rawEnabled != true) {
            _errorMessage.value = "RAW capture not enabled for current session"
            logger.warning("Attempted RAW capture but RAW not enabled")
            return
        }
        
        viewModelScope.launch {
            try {
                logger.info("Triggering manual RAW capture...")
                _systemStatus.value = "Capturing RAW image..."
                
                val captureSuccess = cameraRecorder.captureRawImage()
                
                if (captureSuccess) {
                    _systemStatus.value = "RAW image captured - ${currentSession.getSummary()}"
                    logger.info("Manual RAW capture successful")
                } else {
                    _errorMessage.value = "Failed to capture RAW image"
                    logger.error("Manual RAW capture failed")
                    _systemStatus.value = "RAW capture failed - ${currentSession.getSummary()}"
                }
                
            } catch (e: Exception) {
                _errorMessage.value = "Error capturing RAW image: ${e.message}"
                logger.error("Manual RAW capture error", e)
                _systemStatus.value = "RAW capture error - ${currentSession?.getSummary() ?: "Unknown session"}"
            }
        }
    }
    
    /**
     * Set video recording enabled/disabled
     */
    fun setRecordVideoEnabled(enabled: Boolean) {
        if (_isRecording.value == true) {
            logger.warning("Cannot change recording mode during active session")
            return
        }
        
        _recordVideoEnabled.value = enabled
        logger.info("Video recording ${if (enabled) "enabled" else "disabled"}")
    }
    
    /**
     * Set RAW capture enabled/disabled
     */
    fun setCaptureRawEnabled(enabled: Boolean) {
        if (_isRecording.value == true) {
            logger.warning("Cannot change recording mode during active session")
            return
        }
        
        _captureRawEnabled.value = enabled
        logger.info("RAW capture ${if (enabled) "enabled" else "disabled"}")
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
                    cameraRecorder.stopSession()
                    thermalRecorder.stopRecording()
                    shimmerRecorder.stopRecording()
                } catch (e: Exception) {
                    logger.error("Error stopping recording in onCleared", e)
                }
            }
        }
    }
}