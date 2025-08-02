package com.multisensor.recording.ui

/**
 * UI State data class for MainActivity
 * 
 * This class represents everything the UI needs to know to draw itself at any given moment.
 * Following modern Android architecture guidelines, this centralizes all UI state management
 * and eliminates the need for imperative UI updates scattered throughout the Activity.
 * 
 * Benefits:
 * - Single source of truth for UI state
 * - Predictable state changes
 * - Easy to test UI logic
 * - Lifecycle-safe UI updates
 */
data class MainUiState(
    // System Status
    val statusText: String = "Initializing...",
    val isInitialized: Boolean = false,
    
    // Recording State
    val isRecording: Boolean = false,
    val recordingDuration: Long = 0L,
    val recordingSessionId: String? = null,
    val isReadyToRecord: Boolean = false,
    
    // Connection Status
    val isPcConnected: Boolean = false,
    val isShimmerConnected: Boolean = false,
    val isThermalConnected: Boolean = false,
    val isGsrConnected: Boolean = false,
    val isNetworkConnected: Boolean = false,
    val isCameraConnected: Boolean = false,
    
    // Device Information
    val batteryLevel: Int = -1,
    val batteryStatus: BatteryStatus = BatteryStatus.UNKNOWN,
    val shimmerDeviceId: String = "",
    val networkAddress: String = "",
    
    // UI Control States
    val showManualControls: Boolean = true,  // Enable manual controls by default
    val showPermissionsButton: Boolean = false,
    val isCalibrationRunning: Boolean = false,
    
    // Calibration State
    val isCameraCalibrated: Boolean = false,
    val isThermalCalibrated: Boolean = false,
    val isShimmerCalibrated: Boolean = false,
    val isCalibratingCamera: Boolean = false,
    val isCalibratingThermal: Boolean = false,
    val isCalibratingShimmer: Boolean = false,
    val isSystemValidated: Boolean = false,
    val isValidating: Boolean = false,
    val isDiagnosticsRunning: Boolean = false,
    val diagnosticsCompleted: Boolean = false,
    
    // Storage and File Management
    val storageUsed: Long = 0L,
    val storageAvailable: Long = 0L,
    val storageTotal: Long = 0L,
    val sessionCount: Int = 0,
    val fileCount: Int = 0,
    val isTransferring: Boolean = false,
    
    // Streaming State
    val isStreaming: Boolean = false,
    val streamingFrameRate: Int = 0,
    val streamingDataSize: String = "",
    
    // Error Handling
    val errorMessage: String? = null,
    val showErrorDialog: Boolean = false,
    
    // Loading States
    val isLoadingRecording: Boolean = false,
    val isLoadingCalibration: Boolean = false,
    val isLoadingPermissions: Boolean = false,
    
    // Shimmer Specific State
    val shimmerDeviceInfo: ShimmerDeviceInfo? = null,
    val shimmerBatteryLevel: Int = -1,
    
    // Thermal Camera State
    val thermalPreviewAvailable: Boolean = false,
    val thermalTemperature: Float? = null,
    
    // Session Information
    val currentSessionInfo: SessionDisplayInfo? = null
) {
    
    /**
     * Computed property to determine if recording can be started
     * Modified to be more permissive for debugging and testing
     */
    val canStartRecording: Boolean
        get() = isInitialized && 
                !isRecording && 
                !isLoadingRecording && 
                showManualControls  // Allow recording if manual controls are enabled
    
    /**
     * Computed property to determine if recording can be stopped
     */
    val canStopRecording: Boolean
        get() = isRecording && !isLoadingRecording
    
    /**
     * Computed property to determine if calibration can be run
     */
    val canRunCalibration: Boolean
        get() = isInitialized && 
                !isRecording && 
                !isCalibrationRunning && 
                !isLoadingCalibration
    
    /**
     * Computed property for overall system health status
     */
    val systemHealthStatus: SystemHealthStatus
        get() = when {
            !isInitialized -> SystemHealthStatus.INITIALIZING
            errorMessage != null -> SystemHealthStatus.ERROR
            isRecording -> SystemHealthStatus.RECORDING
            isPcConnected && (isShimmerConnected || isThermalConnected) -> SystemHealthStatus.READY
            isPcConnected -> SystemHealthStatus.PARTIAL_CONNECTION
            else -> SystemHealthStatus.DISCONNECTED
        }
}

/**
 * Battery status enumeration
 */
enum class BatteryStatus {
    UNKNOWN,
    CHARGING,
    DISCHARGING,
    NOT_CHARGING,
    FULL
}

/**
 * System health status enumeration
 */
enum class SystemHealthStatus {
    INITIALIZING,
    READY,
    PARTIAL_CONNECTION,
    DISCONNECTED,
    RECORDING,
    ERROR
}

/**
 * Shimmer device information
 */
data class ShimmerDeviceInfo(
    val deviceName: String,
    val macAddress: String,
    val isConnected: Boolean,
    val signalStrength: Int = -1,
    val firmwareVersion: String? = null
)

/**
 * Session display information for UI
 */
data class SessionDisplayInfo(
    val sessionId: String,
    val startTime: Long,
    val duration: Long,
    val deviceCount: Int,
    val recordingMode: String,
    val status: String
)