package com.multisensor.recording.ui

import android.content.Context
import android.os.BatteryManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.delay
import kotlinx.coroutines.Job
import javax.inject.Inject

@HiltViewModel
class MainViewModelEnhanced @Inject constructor(
    @ApplicationContext private val context: Context,
    private val cameraRecorder: CameraRecorder,
    private val thermalRecorder: ThermalRecorder,
    private val shimmerRecorder: ShimmerRecorder,
    private val sessionManager: SessionManager,
    private val logger: Logger,
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    private var batteryMonitoringJob: Job? = null
    private var connectionMonitoringJob: Job? = null
    private var recordingStatusJob: Job? = null

    private var lastStatusUpdate = 0L
    private val statusUpdateThrottle = 500L

    init {
        logger.info("Enhanced MainViewModel initialized with performance optimizations")
        startBackgroundMonitoring()
    }

    private fun updateUiState(update: (MainUiState) -> MainUiState) {
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastStatusUpdate > statusUpdateThrottle) {
            _uiState.value = update(_uiState.value)
            lastStatusUpdate = currentTime
        }
    }

    private fun forceUpdateUiState(update: (MainUiState) -> MainUiState) {
        _uiState.value = update(_uiState.value)
        lastStatusUpdate = System.currentTimeMillis()
    }

    private fun startBackgroundMonitoring() {
        batteryMonitoringJob = viewModelScope.launch {
            while (true) {
                updateBatteryStatus()
                delay(30000)
            }
        }

        connectionMonitoringJob = viewModelScope.launch {
            while (true) {
                updateConnectionStatus()
                delay(5000)
            }
        }
    }

    fun initializeSystemEnhanced(textureView: android.view.TextureView) {
        viewModelScope.launch {
            try {
                logger.info("Starting enhanced system initialization...")

                forceUpdateUiState { currentState ->
                    currentState.copy(
                        statusText = "Initializing system components...",
                        isLoadingPermissions = true,
                        errorMessage = null,
                        showErrorDialog = false
                    )
                }

                val cameraResult = initializeCameraWithErrorHandling(textureView)
                val thermalResult = initializeThermalWithErrorHandling()
                val shimmerResult = initializeShimmerWithErrorHandling()

                val statusMessage = buildString {
                    append("System Status - ")
                    append("Camera: ${if (cameraResult.success) "✓" else "✗"}")
                    append(", Thermal: ${if (thermalResult.success) "✓" else "✗"}")
                    append(", Shimmer: ${if (shimmerResult.success) "✓" else "✗"}")
                }

                val hasErrors = !cameraResult.success ||
                               (!thermalResult.success && thermalResult.required) ||
                               (!shimmerResult.success && shimmerResult.required)

                forceUpdateUiState { currentState ->
                    currentState.copy(
                        statusText = statusMessage,
                        isInitialized = !hasErrors,
                        isLoadingPermissions = false,
                        errorMessage = if (hasErrors) getInitializationErrorMessage(cameraResult, thermalResult, shimmerResult) else null,
                        showErrorDialog = hasErrors
                    )
                }

                logger.info("Enhanced system initialization completed: $statusMessage")

            } catch (exception: Exception) {
                logger.error("System initialization failed with exception", exception)

                forceUpdateUiState { currentState ->
                    currentState.copy(
                        statusText = "Initialization failed",
                        isInitialized = false,
                        isLoadingPermissions = false,
                        errorMessage = "Failed to initialize: ${exception.localizedMessage ?: "Unknown error"}",
                        showErrorDialog = true
                    )
                }
            }
        }
    }

    private suspend fun initializeCameraWithErrorHandling(textureView: android.view.TextureView): InitializationResult {
        return try {
            val success = cameraRecorder.initialize(textureView)
            if (success) {
                InitializationResult(true, "Camera initialized successfully")
            } else {
                InitializationResult(false, "Camera initialization failed", true)
            }
        } catch (exception: Exception) {
            logger.error("Camera initialization exception", exception)
            InitializationResult(false, "Camera error: ${exception.localizedMessage}", true)
        }
    }

    private suspend fun initializeThermalWithErrorHandling(): InitializationResult {
        return try {
            val success = thermalRecorder.initialize()
            if (success) {
                InitializationResult(true, "Thermal camera connected")
            } else {
                InitializationResult(false, "Thermal camera not available", false)
            }
        } catch (exception: Exception) {
            logger.warning("Thermal camera initialization exception", exception)
            InitializationResult(false, "Thermal camera error: ${exception.localizedMessage}", false)
        }
    }

    private suspend fun initializeShimmerWithErrorHandling(): InitializationResult {
        return try {
            val success = shimmerRecorder.initialize()
            if (success) {
                InitializationResult(true, "Shimmer sensor connected")
            } else {
                InitializationResult(false, "Shimmer sensor not available", false)
            }
        } catch (exception: Exception) {
            logger.warning("Shimmer sensor initialization exception", exception)
            InitializationResult(false, "Shimmer sensor error: ${exception.localizedMessage}", false)
        }
    }

    private fun updateBatteryStatus() {
        try {
            val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            val batteryLevel = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
            val isCharging = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_STATUS) == BatteryManager.BATTERY_STATUS_CHARGING

            val batteryStatus = when {
                isCharging -> BatteryStatus.CHARGING
                batteryLevel > 95 -> BatteryStatus.FULL
                batteryLevel > 20 -> BatteryStatus.DISCHARGING
                else -> BatteryStatus.DISCHARGING
            }

            updateUiState { currentState ->
                currentState.copy(
                    batteryLevel = batteryLevel,
                    batteryStatus = batteryStatus
                )
            }

            if (batteryLevel < 20 && !isCharging && _uiState.value.isRecording) {
                showLowBatteryWarning()
            }

        } catch (exception: Exception) {
            logger.warning("Failed to update battery status", exception)
        }
    }

    private fun updateConnectionStatus() {
        try {
            val isPcConnected = false

            val isShimmerConnected = shimmerRecorder.getShimmerStatus().isConnected

            val isThermalConnected = false

            updateUiState { currentState ->
                currentState.copy(
                    isPcConnected = isPcConnected,
                    isShimmerConnected = isShimmerConnected,
                    isThermalConnected = isThermalConnected
                )
            }

        } catch (exception: Exception) {
            logger.warning("Failed to update connection status", exception)
        }
    }

    fun startRecordingEnhanced() {
        viewModelScope.launch {
            try {
                val validationResult = validateRecordingConditions()
                if (!validationResult.isValid) {
                    showErrorMessage("Cannot start recording", validationResult.errorMessage)
                    return@launch
                }

                forceUpdateUiState { currentState ->
                    currentState.copy(
                        isLoadingRecording = true,
                        statusText = "Starting recording session..."
                    )
                }

                val sessionId = sessionManager.createNewSession()

                val sessionInfo = SessionInfo(
                    sessionId = sessionId,
                    startTime = System.currentTimeMillis()
                )

                val recordingStarted = sessionId.isNotEmpty()

                if (recordingStarted) {
                    forceUpdateUiState { currentState ->
                        currentState.copy(
                            isRecording = true,
                            isLoadingRecording = false,
                            recordingSessionId = sessionInfo.sessionId,
                            statusText = "Recording in progress - Session: ${sessionInfo.sessionId}",
                            currentSessionInfo = SessionDisplayInfo(
                                sessionId = sessionInfo.sessionId,
                                startTime = sessionInfo.startTime,
                                duration = 0L,
                                deviceCount = getConnectedDeviceCount(),
                                recordingMode = "Multi-sensor",
                                status = "Recording"
                            )
                        )
                    }

                    startRecordingStatusMonitoring()

                    logger.info("Enhanced recording started successfully: ${sessionInfo.sessionId}")
                } else {
                    throw Exception("Failed to start recording session")
                }

            } catch (exception: Exception) {
                logger.error("Failed to start enhanced recording", exception)

                forceUpdateUiState { currentState ->
                    currentState.copy(
                        isRecording = false,
                        isLoadingRecording = false,
                        errorMessage = "Recording failed: ${exception.localizedMessage ?: "Unknown error"}",
                        showErrorDialog = true
                    )
                }
            }
        }
    }

    fun stopRecordingEnhanced() {
        viewModelScope.launch {
            try {
                forceUpdateUiState { currentState ->
                    currentState.copy(
                        isLoadingRecording = true,
                        statusText = "Stopping recording session..."
                    )
                }

                sessionManager.finalizeCurrentSession()
                val sessionStopped = true

                recordingStatusJob?.cancel()
                recordingStatusJob = null

                if (sessionStopped) {
                    forceUpdateUiState { currentState ->
                        currentState.copy(
                            isRecording = false,
                            isLoadingRecording = false,
                            recordingSessionId = null,
                            statusText = "Recording stopped successfully. Files saved.",
                            currentSessionInfo = null
                        )
                    }

                    logger.info("Enhanced recording stopped successfully")
                } else {
                    throw Exception("Failed to stop recording session properly")
                }

            } catch (exception: Exception) {
                logger.error("Failed to stop enhanced recording", exception)

                forceUpdateUiState { currentState ->
                    currentState.copy(
                        isRecording = false,
                        isLoadingRecording = false,
                        errorMessage = "Stop recording failed: ${exception.localizedMessage ?: "Unknown error"}",
                        showErrorDialog = true
                    )
                }
            }
        }
    }

    private fun startRecordingStatusMonitoring() {
        recordingStatusJob = viewModelScope.launch {
            while (_uiState.value.isRecording) {
                val sessionInfo = sessionManager.getCurrentSession()
                if (sessionInfo != null) {
                    val duration = System.currentTimeMillis() - sessionInfo.startTime

                    updateUiState { currentState ->
                        currentState.copy(
                            recordingDuration = duration,
                            currentSessionInfo = currentState.currentSessionInfo?.copy(
                                duration = duration
                            )
                        )
                    }
                }
                delay(1000)
            }
        }
    }

    private fun validateRecordingConditions(): ValidationResult {
        val state = _uiState.value

        return when {
            !state.isInitialized -> ValidationResult(false, "System not initialized")
            state.isRecording -> ValidationResult(false, "Recording already in progress")
            state.batteryLevel < 15 && state.batteryStatus != BatteryStatus.CHARGING ->
                ValidationResult(false, "Battery level too low (${state.batteryLevel}%). Please charge device.")
            !state.isPcConnected && !state.showManualControls ->
                ValidationResult(false, "PC connection required for recording")
            else -> ValidationResult(true, "Ready to record")
        }
    }

    private fun getConnectedDeviceCount(): Int {
        val state = _uiState.value
        var count = 1
        if (state.isThermalConnected) count++
        if (state.isShimmerConnected) count++
        if (state.isPcConnected) count++
        return count
    }

    private fun showLowBatteryWarning() {
        forceUpdateUiState { currentState ->
            currentState.copy(
                errorMessage = "Low battery (${currentState.batteryLevel}%). Consider connecting charger for extended recording.",
                showErrorDialog = true
            )
        }
    }

    private fun showErrorMessage(title: String, message: String) {
        forceUpdateUiState { currentState ->
            currentState.copy(
                errorMessage = "$title: $message",
                showErrorDialog = true
            )
        }
    }

    fun clearErrorDialog() {
        forceUpdateUiState { currentState ->
            currentState.copy(
                errorMessage = null,
                showErrorDialog = false
            )
        }
    }

    private fun getInitializationErrorMessage(
        camera: InitializationResult,
        thermal: InitializationResult,
        shimmer: InitializationResult
    ): String {
        val errors = mutableListOf<String>()

        if (!camera.success) errors.add("Camera: ${camera.message}")
        if (!thermal.success && thermal.required) errors.add("Thermal: ${thermal.message}")
        if (!shimmer.success && shimmer.required) errors.add("Shimmer: ${shimmer.message}")

        return if (errors.isNotEmpty()) {
            "Initialization errors:\n${errors.joinToString("\n")}"
        } else {
            "Unknown initialization error"
        }
    }

    override fun onCleared() {
        super.onCleared()
        batteryMonitoringJob?.cancel()
        connectionMonitoringJob?.cancel()
        recordingStatusJob?.cancel()
        logger.info("Enhanced MainViewModel cleared and resources cleaned up")
    }

    private data class InitializationResult(
        val success: Boolean,
        val message: String,
        val required: Boolean = false
    )

    private data class ValidationResult(
        val isValid: Boolean,
        val errorMessage: String
    )
}