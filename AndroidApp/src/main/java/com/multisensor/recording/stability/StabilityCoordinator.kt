package com.multisensor.recording.stability

import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.network.NetworkRecoveryManager
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.RecordingStateManager
import com.multisensor.recording.recording.RecordingState
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.PerformanceMonitor
import com.multisensor.recording.util.ResourceMonitor
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Central coordinator for system stability and reliability.
 * Orchestrates error handling, recovery actions, and resource management across all components.
 */
@Singleton
class StabilityCoordinator @Inject constructor(
    private val recordingStateManager: RecordingStateManager,
    private val performanceMonitor: PerformanceMonitor,
    private val resourceMonitor: ResourceMonitor,
    private val shimmerManager: ShimmerManager,
    private val networkRecoveryManager: NetworkRecoveryManager,
    private val cameraRecorder: CameraRecorder,
    private val logger: Logger
) : PerformanceMonitor.StabilityActionsListener,
    ResourceMonitor.ResourceWarningListener {
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private val _systemStability = MutableStateFlow(SystemStability())
    val systemStability: StateFlow<SystemStability> = _systemStability.asStateFlow()
    
    private val _stabilityActions = MutableStateFlow<List<StabilityAction>>(emptyList())
    val stabilityActions: StateFlow<List<StabilityAction>> = _stabilityActions.asStateFlow()
    
    private var lastStabilityCheck = 0L
    private val stabilityCheckInterval = 5000L // 5 seconds
    
    companion object {
        private const val TAG = "StabilityCoordinator"
        private const val MAX_CONCURRENT_ISSUES = 3
        private const val CRITICAL_RESOURCE_THRESHOLD = 0.1 // 10% remaining
        private const val RECOVERY_TIMEOUT_MS = 30000L // 30 seconds
    }
    
    init {
        setupStabilityMonitoring()
    }
    
    private fun setupStabilityMonitoring() {
        // Set up listeners
        performanceMonitor.setStabilityActionsListener(this)
        resourceMonitor.setResourceWarningListener(this)
        
        // Start comprehensive stability monitoring
        scope.launch {
            monitorSystemStability()
        }
        
        logger.info("$TAG: Stability coordinator initialized")
    }
    
    private suspend fun monitorSystemStability() {
        while (scope.isActive) {
            try {
                val currentTime = System.currentTimeMillis()
                
                if (currentTime - lastStabilityCheck >= stabilityCheckInterval) {
                    assessSystemStability()
                    lastStabilityCheck = currentTime
                }
                
                delay(1000) // Check every second, assess every 5 seconds
            } catch (e: Exception) {
                logger.error("$TAG: Error in stability monitoring", e)
                delay(5000) // Back off on error
            }
        }
    }
    
    private suspend fun assessSystemStability() {
        val recordingState = recordingStateManager.recordingState.value
        val resourceStatus = resourceMonitor.resourceStatus.value
        val performanceMetrics = performanceMonitor.performanceMetrics.value
        val shimmerHealth = shimmerManager.getConnectionHealth()
        val networkState = networkRecoveryManager.connectionState.value
        
        val activeIssues = mutableListOf<SystemIssue>()
        val stabilityScore = calculateStabilityScore(
            recordingState, resourceStatus, performanceMetrics, 
            shimmerHealth, networkState, activeIssues
        )
        
        val systemStability = SystemStability(
            score = stabilityScore,
            isStable = stabilityScore >= 70 && activeIssues.size <= MAX_CONCURRENT_ISSUES,
            activeIssues = activeIssues,
            canStartRecording = canStartRecording(activeIssues),
            shouldStopRecording = shouldStopRecording(stabilityScore, activeIssues),
            lastAssessment = System.currentTimeMillis()
        )
        
        _systemStability.value = systemStability
        
        // Take proactive actions if needed
        if (!systemStability.isStable) {
            handleStabilityIssues(activeIssues)
        }
        
        logger.debug("$TAG: Stability assessment - Score: $stabilityScore, Issues: ${activeIssues.size}")
    }
    
    private fun calculateStabilityScore(
        recordingState: RecordingState,
        resourceStatus: ResourceMonitor.ResourceStatus,
        performanceMetrics: PerformanceMonitor.PerformanceMetrics,
        shimmerHealth: ShimmerManager.ConnectionHealth,
        networkState: NetworkRecoveryManager.NetworkConnectionState,
        activeIssues: MutableList<SystemIssue>
    ): Int {
        var score = 100
        
        // Recording state health (20 points)
        when (recordingState) {
            RecordingState.ERROR -> {
                score -= 30
                activeIssues.add(SystemIssue.RECORDING_ERROR)
            }
            RecordingState.STARTING, RecordingState.STOPPING -> score -= 5
            else -> { /* No penalty */ }
        }
        
        // Resource health (30 points)
        if (resourceStatus.availableStorageMB < 100) {
            score -= 20
            activeIssues.add(SystemIssue.LOW_STORAGE)
        } else if (resourceStatus.availableStorageMB < 500) {
            score -= 10
        }
        
        if (resourceStatus.freeMemoryPercent < 15) {
            score -= 15
            activeIssues.add(SystemIssue.LOW_MEMORY)
        } else if (resourceStatus.freeMemoryPercent < 25) {
            score -= 8
        }
        
        // Performance health (25 points)
        if (performanceMetrics.heapUtilization > 90) {
            score -= 20
            activeIssues.add(SystemIssue.HIGH_MEMORY_USAGE)
        } else if (performanceMetrics.heapUtilization > 80) {
            score -= 10
        }
        
        if (performanceMetrics.currentFps > 0 && performanceMetrics.currentFps < 30) {
            score -= 15
            activeIssues.add(SystemIssue.LOW_FRAME_RATE)
        }
        
        // Shimmer connectivity (15 points)
        if (!shimmerHealth.isConnected && shimmerHealth.consecutiveFailures > 3) {
            score -= 15
            activeIssues.add(SystemIssue.SHIMMER_DISCONNECTED)
        } else if (!shimmerHealth.isConnected) {
            score -= 8
        }
        
        // Network connectivity (10 points)
        if (!networkState.isConnected) {
            score -= 10
            activeIssues.add(SystemIssue.NETWORK_DISCONNECTED)
        }
        
        return score.coerceIn(0, 100)
    }
    
    private fun canStartRecording(activeIssues: List<SystemIssue>): Boolean {
        val criticalIssues = listOf(
            SystemIssue.LOW_STORAGE,
            SystemIssue.LOW_MEMORY,
            SystemIssue.RECORDING_ERROR
        )
        
        return activeIssues.none { it in criticalIssues }
    }
    
    private fun shouldStopRecording(score: Int, activeIssues: List<SystemIssue>): Boolean {
        val emergencyIssues = listOf(
            SystemIssue.LOW_STORAGE,
            SystemIssue.HIGH_MEMORY_USAGE
        )
        
        return score < 40 || activeIssues.any { it in emergencyIssues }
    }
    
    private suspend fun handleStabilityIssues(issues: List<SystemIssue>) {
        logger.warning("$TAG: Handling ${issues.size} stability issues: $issues")
        
        val actions = mutableListOf<StabilityAction>()
        
        for (issue in issues) {
            val action = when (issue) {
                SystemIssue.LOW_STORAGE -> {
                    StabilityAction(
                        type = StabilityActionType.EMERGENCY_STOP,
                        description = "Stopping recording due to low storage",
                        priority = ActionPriority.CRITICAL
                    )
                }
                SystemIssue.LOW_MEMORY -> {
                    performanceMonitor.triggerGarbageCollection()
                    StabilityAction(
                        type = StabilityActionType.MEMORY_CLEANUP,
                        description = "Triggered garbage collection for low memory",
                        priority = ActionPriority.HIGH
                    )
                }
                SystemIssue.HIGH_MEMORY_USAGE -> {
                    performanceMonitor.triggerGarbageCollection()
                    StabilityAction(
                        type = StabilityActionType.PERFORMANCE_OPTIMIZATION,
                        description = "Optimizing performance for high memory usage",
                        priority = ActionPriority.HIGH
                    )
                }
                SystemIssue.SHIMMER_DISCONNECTED -> {
                    scope.launch {
                        shimmerManager.clearErrorState()
                    }
                    StabilityAction(
                        type = StabilityActionType.SENSOR_RECOVERY,
                        description = "Attempting Shimmer reconnection",
                        priority = ActionPriority.MEDIUM
                    )
                }
                SystemIssue.NETWORK_DISCONNECTED -> {
                    networkRecoveryManager.attemptReconnection()
                    StabilityAction(
                        type = StabilityActionType.NETWORK_RECOVERY,
                        description = "Attempting network reconnection",
                        priority = ActionPriority.MEDIUM
                    )
                }
                else -> {
                    StabilityAction(
                        type = StabilityActionType.MONITORING,
                        description = "Monitoring issue: $issue",
                        priority = ActionPriority.LOW
                    )
                }
            }
            
            actions.add(action)
        }
        
        _stabilityActions.value = actions
        
        // Execute critical actions immediately
        val criticalActions = actions.filter { it.priority == ActionPriority.CRITICAL }
        for (action in criticalActions) {
            executeCriticalAction(action)
        }
    }
    
    private suspend fun executeCriticalAction(action: StabilityAction) {
        when (action.type) {
            StabilityActionType.EMERGENCY_STOP -> {
                logger.error("$TAG: Executing emergency stop")
                try {
                    if (recordingStateManager.recordingState.value == RecordingState.RECORDING) {
                        cameraRecorder.stopSession()
                    }
                } catch (e: Exception) {
                    logger.error("$TAG: Error during emergency stop", e)
                }
            }
            else -> {
                logger.info("$TAG: Executed action: ${action.description}")
            }
        }
    }
    
    // PerformanceMonitor.StabilityActionsListener implementation
    override fun onMemoryPressureDetected(utilizationPercent: Double) {
        logger.warning("$TAG: Memory pressure detected: ${utilizationPercent.toInt()}%")
        scope.launch {
            val action = StabilityAction(
                type = StabilityActionType.MEMORY_CLEANUP,
                description = "Memory pressure response: ${utilizationPercent.toInt()}% utilization",
                priority = if (utilizationPercent > 90) ActionPriority.CRITICAL else ActionPriority.HIGH
            )
            
            val currentActions = _stabilityActions.value.toMutableList()
            currentActions.add(action)
            _stabilityActions.value = currentActions
        }
    }
    
    override fun onPerformanceDegradation(fps: Double) {
        logger.warning("$TAG: Performance degradation detected: ${fps.toInt()} FPS")
        scope.launch {
            val action = StabilityAction(
                type = StabilityActionType.PERFORMANCE_OPTIMIZATION,
                description = "Performance optimization: ${fps.toInt()} FPS",
                priority = ActionPriority.MEDIUM
            )
            
            val currentActions = _stabilityActions.value.toMutableList()
            currentActions.add(action)
            _stabilityActions.value = currentActions
        }
    }
    
    override fun onSustainedHighUtilization() {
        logger.error("$TAG: Sustained high utilization detected")
        scope.launch {
            val action = StabilityAction(
                type = StabilityActionType.SYSTEM_OPTIMIZATION,
                description = "Responding to sustained high utilization",
                priority = ActionPriority.HIGH
            )
            
            val currentActions = _stabilityActions.value.toMutableList()
            currentActions.add(action)
            _stabilityActions.value = currentActions
        }
    }
    
    override fun onPotentialLeakDetected(activityCount: Int, viewCount: Int) {
        logger.warning("$TAG: Potential memory leak: $activityCount activities, $viewCount views")
        scope.launch {
            val action = StabilityAction(
                type = StabilityActionType.MEMORY_CLEANUP,
                description = "Memory leak response: $activityCount activities, $viewCount views",
                priority = ActionPriority.HIGH
            )
            
            val currentActions = _stabilityActions.value.toMutableList()
            currentActions.add(action)
            _stabilityActions.value = currentActions
        }
    }
    
    override fun onStabilityActionRequired(actionType: PerformanceMonitor.StabilityActionType) {
        logger.info("$TAG: Stability action required: $actionType")
        // Additional actions can be implemented here based on specific performance action types
    }
    
    // ResourceMonitor.ResourceWarningListener implementation
    override fun onStorageWarning(availableMB: Long) {
        logger.warning("$TAG: Storage warning: ${availableMB}MB available")
    }
    
    override fun onStorageCritical(availableMB: Long) {
        logger.error("$TAG: Critical storage level: ${availableMB}MB available")
        scope.launch {
            val action = StabilityAction(
                type = StabilityActionType.EMERGENCY_STOP,
                description = "Critical storage level: ${availableMB}MB",
                priority = ActionPriority.CRITICAL
            )
            
            executeCriticalAction(action)
        }
    }
    
    override fun onMemoryWarning(freeMemoryPercent: Double) {
        logger.warning("$TAG: Memory warning: ${freeMemoryPercent.toInt()}% free")
    }
    
    override fun onMemoryCritical(freeMemoryPercent: Double) {
        logger.error("$TAG: Critical memory level: ${freeMemoryPercent.toInt()}% free")
        scope.launch {
            performanceMonitor.triggerGarbageCollection()
        }
    }
    
    override fun onResourceConstraint(constraint: ResourceMonitor.ResourceConstraint) {
        logger.error("$TAG: Resource constraint: $constraint")
        scope.launch {
            val action = StabilityAction(
                type = when (constraint) {
                    ResourceMonitor.ResourceConstraint.STORAGE_FULL -> StabilityActionType.EMERGENCY_STOP
                    ResourceMonitor.ResourceConstraint.MEMORY_EXHAUSTED -> StabilityActionType.MEMORY_CLEANUP
                    ResourceMonitor.ResourceConstraint.STORAGE_UNAVAILABLE -> StabilityActionType.EMERGENCY_STOP
                },
                description = "Resource constraint: $constraint",
                priority = ActionPriority.CRITICAL
            )
            
            executeCriticalAction(action)
        }
    }
    
    /**
     * Cleanup method for proper resource management.
     */
    fun cleanup() {
        logger.info("$TAG: Cleaning up stability coordinator")
        scope.cancel()
    }
}

/**
 * Represents the overall system stability status.
 */
data class SystemStability(
    val score: Int = 100,
    val isStable: Boolean = true,
    val activeIssues: List<SystemIssue> = emptyList(),
    val canStartRecording: Boolean = true,
    val shouldStopRecording: Boolean = false,
    val lastAssessment: Long = System.currentTimeMillis()
)

/**
 * Types of system issues that can affect stability.
 */
enum class SystemIssue {
    LOW_STORAGE,
    LOW_MEMORY,
    HIGH_MEMORY_USAGE,
    LOW_FRAME_RATE,
    SHIMMER_DISCONNECTED,
    NETWORK_DISCONNECTED,
    RECORDING_ERROR,
    SENSOR_FAILURE
}

/**
 * Represents a stability action taken by the system.
 */
data class StabilityAction(
    val type: StabilityActionType,
    val description: String,
    val priority: ActionPriority,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Types of stability actions.
 */
enum class StabilityActionType {
    MEMORY_CLEANUP,
    PERFORMANCE_OPTIMIZATION,
    SYSTEM_OPTIMIZATION,
    EMERGENCY_STOP,
    SENSOR_RECOVERY,
    NETWORK_RECOVERY,
    MONITORING
}

/**
 * Priority levels for stability actions.
 */
enum class ActionPriority {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}