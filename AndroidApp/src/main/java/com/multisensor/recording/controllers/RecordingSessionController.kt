package com.multisensor.recording.controllers

import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for managing recording sessions across multiple devices.
 * Follows single responsibility principle by focusing only on recording operations.
 * 
 * Coordinates recording activities between:
 * - Camera (RGB video/RAW capture)
 * - Thermal camera
 * - Shimmer sensors (GSR, accelerometer, etc.)
 * 
 * @param cameraRecorder Handles RGB camera recording operations
 * @param thermalRecorder Manages thermal camera recording
 * @param shimmerRecorder Controls Shimmer sensor recording
 * @param sessionManager Manages recording session lifecycle
 * @param logger Application logger
 */
@Singleton
class RecordingSessionController @Inject constructor(
    private val cameraRecorder: CameraRecorder,
    private val thermalRecorder: ThermalRecorder,
    private val shimmerRecorder: ShimmerRecorder,
    private val sessionManager: SessionManager,
    private val logger: Logger
) {
    
    /**
     * Represents the current state of a recording session
     */
    data class RecordingState(
        val isRecording: Boolean = false,
        val isPaused: Boolean = false,
        val sessionId: String? = null,
        val sessionInfo: String? = null,
        val recordingError: String? = null,
        val deviceStatuses: DeviceStatuses = DeviceStatuses()
    )
    
    /**
     * Status information for each recording device
     */
    data class DeviceStatuses(
        val cameraRecording: Boolean = false,
        val thermalRecording: Boolean = false,
        val shimmerRecording: Boolean = false
    )
    
    /**
     * Configuration for recording session
     */
    data class RecordingConfig(
        val recordVideo: Boolean = true,
        val captureRaw: Boolean = false,
        val enableThermal: Boolean = true,
        val enableShimmer: Boolean = true
    )
    
    private val _recordingState = MutableStateFlow(RecordingState())
    val recordingState: StateFlow<RecordingState> = _recordingState.asStateFlow()
    
    /**
     * Starts a new recording session with the specified configuration
     * 
     * @param config Recording configuration specifying which devices to use
     * @return Success status and session information
     */
    suspend fun startRecording(config: RecordingConfig = RecordingConfig()): Result<String> {
        return try {
            if (_recordingState.value.isRecording) {
                return Result.failure(IllegalStateException("Recording already in progress"))
            }
            
            logger.info("Starting recording session with config: $config")
            
            val sessionInfo = cameraRecorder.startSession(config.recordVideo, config.captureRaw)
            if (sessionInfo == null) {
                return Result.failure(RuntimeException("Failed to start camera recording"))
            }
            
            val sessionId = sessionManager.createNewSession()
            logger.info("Created session: $sessionId")
            
            val thermalStarted = if (config.enableThermal) {
                thermalRecorder.startRecording(sessionId)
            } else false
            
            val shimmerStarted = if (config.enableShimmer) {
                shimmerRecorder.startRecording(sessionId)
            } else false
            
            _recordingState.value = RecordingState(
                isRecording = true,
                sessionId = sessionId,
                sessionInfo = sessionInfo.getSummary(),
                deviceStatuses = DeviceStatuses(
                    cameraRecording = true,
                    thermalRecording = thermalStarted,
                    shimmerRecording = shimmerStarted
                )
            )
            
            val summary = "Session started: ${sessionInfo.getSummary()}"
            logger.info("Recording session started successfully: $summary")
            Result.success(summary)
            
        } catch (e: Exception) {
            logger.error("Failed to start recording session", e)
            _recordingState.value = _recordingState.value.copy(
                recordingError = "Failed to start recording: ${e.message}"
            )
            Result.failure(e)
        }
    }
    
    /**
     * Stops the current recording session
     * 
     * @return Success status and final session information
     */
    suspend fun stopRecording(): Result<String> {
        return try {
            if (!_recordingState.value.isRecording) {
                return Result.failure(IllegalStateException("No recording in progress"))
            }
            
            logger.info("Stopping recording session")
            
            val finalSessionInfo = cameraRecorder.stopSession()
            
            thermalRecorder.stopRecording()
            shimmerRecorder.stopRecording()
            
            sessionManager.finalizeCurrentSession()
            
            val summary = finalSessionInfo?.getSummary() ?: "Recording stopped"
            
            _recordingState.value = RecordingState(
                isRecording = false,
                sessionInfo = summary,
                deviceStatuses = DeviceStatuses()
            )
            
            logger.info("Recording session stopped successfully: $summary")
            Result.success(summary)
            
        } catch (e: Exception) {
            logger.error("Failed to stop recording session", e)
            _recordingState.value = _recordingState.value.copy(
                isRecording = false,
                recordingError = "Failed to stop recording: ${e.message}"
            )
            Result.failure(e)
        }
    }
    
    /**
     * Pauses the current recording session
     */
    suspend fun pauseRecording(): Result<Unit> {
        return try {
            if (!_recordingState.value.isRecording || _recordingState.value.isPaused) {
                return Result.failure(IllegalStateException("No active recording to pause"))
            }
            
            logger.info("Pausing recording session")
            
            _recordingState.value = _recordingState.value.copy(isPaused = true)
            
            logger.info("Recording session paused")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Failed to pause recording", e)
            Result.failure(e)
        }
    }
    
    /**
     * Resumes a paused recording session
     */
    suspend fun resumeRecording(): Result<Unit> {
        return try {
            if (!_recordingState.value.isRecording || !_recordingState.value.isPaused) {
                return Result.failure(IllegalStateException("No paused recording to resume"))
            }
            
            logger.info("Resuming recording session")
            
            _recordingState.value = _recordingState.value.copy(isPaused = false)
            
            logger.info("Recording session resumed")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Failed to resume recording", e)
            Result.failure(e)
        }
    }
    
    /**
     * Captures a manual RAW image during recording
     * 
     * @return Success status
     */
    suspend fun captureRawImage(): Result<Unit> {
        return try {
            if (!_recordingState.value.isRecording) {
                return Result.failure(IllegalStateException("No active recording session"))
            }
            
            logger.info("Capturing manual RAW image")
            val success = cameraRecorder.captureRawImage()
            
            if (success) {
                logger.info("RAW image captured successfully")
                Result.success(Unit)
            } else {
                Result.failure(RuntimeException("RAW capture failed"))
            }
            
        } catch (e: Exception) {
            logger.error("Failed to capture RAW image", e)
            Result.failure(e)
        }
    }
    
    /**
     * Gets the current recording status
     */
    fun getCurrentState(): RecordingState = _recordingState.value
    
    /**
     * Checks if recording is currently active
     */
    fun isRecording(): Boolean = _recordingState.value.isRecording
    
    /**
     * Clears any recording errors
     */
    fun clearError() {
        _recordingState.value = _recordingState.value.copy(recordingError = null)
    }
    
    /**
     * Emergency stop - stops recording without normal cleanup
     * Should only be used in error scenarios
     */
    suspend fun emergencyStop(): Result<Unit> {
        return try {
            logger.warning("Emergency stop requested")
            
            try { cameraRecorder.stopSession() } catch (e: Exception) { logger.error("Emergency camera stop failed", e) }
            try { thermalRecorder.stopRecording() } catch (e: Exception) { logger.error("Emergency thermal stop failed", e) }
            try { shimmerRecorder.stopRecording() } catch (e: Exception) { logger.error("Emergency shimmer stop failed", e) }
            try { sessionManager.finalizeCurrentSession() } catch (e: Exception) { logger.error("Emergency session finalization failed", e) }
            
            _recordingState.value = RecordingState()
            
            logger.info("Emergency stop completed")
            Result.success(Unit)
            
        } catch (e: Exception) {
            logger.error("Emergency stop failed", e)
            Result.failure(e)
        }
    }
}