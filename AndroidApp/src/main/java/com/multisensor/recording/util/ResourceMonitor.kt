package com.multisensor.recording.util

import android.content.Context
import android.os.Environment
import android.os.StatFs
import com.multisensor.recording.recording.ErrorType
import com.multisensor.recording.recording.RecordingError
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Monitors system resources (storage, memory) and provides early warnings
 * to prevent recording failures due to resource constraints.
 */
@Singleton
class ResourceMonitor @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var monitoringJob: Job? = null
    
    private val _resourceStatus = MutableStateFlow(ResourceStatus())
    val resourceStatus: StateFlow<ResourceStatus> = _resourceStatus.asStateFlow()
    
    private val _resourceWarnings = MutableStateFlow<List<ResourceWarning>>(emptyList())
    val resourceWarnings: StateFlow<List<ResourceWarning>> = _resourceWarnings.asStateFlow()
    
    private var resourceWarningListener: ResourceWarningListener? = null
    
    companion object {
        private const val TAG = "ResourceMonitor"
        
        // Thresholds for warnings and critical levels
        private const val STORAGE_WARNING_MB = 500L      // 500MB
        private const val STORAGE_CRITICAL_MB = 100L     // 100MB
        private const val MEMORY_WARNING_PERCENT = 85.0  // 85%
        private const val MEMORY_CRITICAL_PERCENT = 95.0 // 95%
        
        // Minimum requirements for recording
        private const val MIN_STORAGE_FOR_RECORDING_MB = 200L  // 200MB
        private const val MIN_MEMORY_FOR_RECORDING_PERCENT = 20.0  // 20% free memory
        
        private const val MONITORING_INTERVAL_MS = 10_000L // 10 seconds
    }
    
    interface ResourceWarningListener {
        fun onStorageWarning(availableMB: Long)
        fun onStorageCritical(availableMB: Long)
        fun onMemoryWarning(freeMemoryPercent: Double)
        fun onMemoryCritical(freeMemoryPercent: Double)
        fun onResourceConstraint(constraint: ResourceConstraint)
    }
    
    fun startMonitoring() {
        if (monitoringJob?.isActive == true) {
            logger.debug("$TAG: Resource monitoring already active")
            return
        }
        
        logger.info("$TAG: Starting resource monitoring")
        
        monitoringJob = scope.launch {
            while (isActive) {
                try {
                    val status = collectResourceStatus()
                    _resourceStatus.value = status
                    
                    analyzeResources(status)
                    
                    delay(MONITORING_INTERVAL_MS)
                } catch (e: Exception) {
                    logger.error("$TAG: Error during resource monitoring", e)
                    delay(MONITORING_INTERVAL_MS * 2) // Back off on error
                }
            }
        }
    }
    
    fun stopMonitoring() {
        logger.info("$TAG: Stopping resource monitoring")
        monitoringJob?.cancel()
        monitoringJob = null
    }
    
    fun setResourceWarningListener(listener: ResourceWarningListener) {
        this.resourceWarningListener = listener
        logger.info("$TAG: Resource warning listener set")
    }
    
    /**
     * Checks if there are sufficient resources to start a recording session.
     */
    suspend fun checkResourcesForRecording(estimatedDurationMinutes: Int): Result<Unit> {
        return withContext(Dispatchers.IO) {
            val status = collectResourceStatus()
            val warnings = mutableListOf<ResourceWarning>()
            
            // Check storage requirements
            val estimatedStorageNeededMB = estimateStorageNeeded(estimatedDurationMinutes)
            if (status.availableStorageMB < estimatedStorageNeededMB + MIN_STORAGE_FOR_RECORDING_MB) {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.INSUFFICIENT_STORAGE,
                        message = "Insufficient storage: ${status.availableStorageMB}MB available, need ${estimatedStorageNeededMB + MIN_STORAGE_FOR_RECORDING_MB}MB",
                        severity = WarningSeverity.CRITICAL,
                        timestamp = System.currentTimeMillis()
                    )
                )
            }
            
            // Check memory requirements  
            if (status.freeMemoryPercent < MIN_MEMORY_FOR_RECORDING_PERCENT) {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.INSUFFICIENT_MEMORY,
                        message = "Low memory: ${status.freeMemoryPercent.toInt()}% free, need at least ${MIN_MEMORY_FOR_RECORDING_PERCENT.toInt()}%",
                        severity = WarningSeverity.CRITICAL,
                        timestamp = System.currentTimeMillis()
                    )
                )
            }
            
            // Check if storage is writable
            if (!status.isStorageWritable) {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.STORAGE_NOT_WRITABLE,
                        message = "Storage is not writable - cannot save recordings",
                        severity = WarningSeverity.CRITICAL,
                        timestamp = System.currentTimeMillis()
                    )
                )
            }
            
            if (warnings.any { it.severity == WarningSeverity.CRITICAL }) {
                val criticalWarnings = warnings.filter { it.severity == WarningSeverity.CRITICAL }
                val errorMessage = criticalWarnings.joinToString("; ") { it.message }
                
                return@withContext Result.failure(
                    IllegalStateException("Cannot start recording: $errorMessage")
                )
            }
            
            if (warnings.isNotEmpty()) {
                _resourceWarnings.value = warnings
                logger.warning("$TAG: Resource warnings for recording: ${warnings.size} warnings")
            }
            
            Result.success(Unit)
        }
    }
    
    /**
     * Estimates storage needed for a recording session.
     */
    private fun estimateStorageNeeded(durationMinutes: Int): Long {
        // Rough estimate: 50MB per minute for HD video + sensors
        // This is conservative to ensure we don't run out of space
        return (durationMinutes * 50L).coerceAtLeast(100L) // Minimum 100MB
    }
    
    private suspend fun collectResourceStatus(): ResourceStatus {
        return withContext(Dispatchers.IO) {
            val runtime = Runtime.getRuntime()
            
            // Memory calculations
            val totalMemory = runtime.totalMemory()
            val freeMemory = runtime.freeMemory()
            val maxMemory = runtime.maxMemory()
            val usedMemory = totalMemory - freeMemory
            val freeMemoryPercent = ((maxMemory - usedMemory).toDouble() / maxMemory.toDouble()) * 100
            
            // Storage calculations
            val storageStats = getStorageStats()
            
            ResourceStatus(
                availableStorageMB = storageStats.first,
                totalStorageMB = storageStats.second,
                freeMemoryPercent = freeMemoryPercent,
                usedMemoryMB = (usedMemory / 1024 / 1024).toDouble(),
                maxMemoryMB = (maxMemory / 1024 / 1024).toDouble(),
                isStorageWritable = isExternalStorageWritable(),
                timestamp = System.currentTimeMillis()
            )
        }
    }
    
    private fun getStorageStats(): Pair<Long, Long> {
        return try {
            // Try external storage first (SD card or external memory)
            val externalDir = context.getExternalFilesDir(null)
            if (externalDir != null && externalDir.exists()) {
                val stats = StatFs(externalDir.path)
                val availableBytes = stats.availableBytes
                val totalBytes = stats.totalBytes
                
                Pair(availableBytes / 1024 / 1024, totalBytes / 1024 / 1024)
            } else {
                // Fall back to internal storage
                val internalDir = context.filesDir
                val stats = StatFs(internalDir.path)
                val availableBytes = stats.availableBytes
                val totalBytes = stats.totalBytes
                
                Pair(availableBytes / 1024 / 1024, totalBytes / 1024 / 1024)
            }
        } catch (e: Exception) {
            logger.error("$TAG: Error getting storage stats", e)
            Pair(0L, 0L) // Return safe defaults
        }
    }
    
    private fun isExternalStorageWritable(): Boolean {
        return Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED
    }
    
    private fun analyzeResources(status: ResourceStatus) {
        val warnings = mutableListOf<ResourceWarning>()
        
        // Check storage levels
        when {
            status.availableStorageMB < STORAGE_CRITICAL_MB -> {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.STORAGE_CRITICAL,
                        message = "Critical storage space: ${status.availableStorageMB}MB remaining",
                        severity = WarningSeverity.CRITICAL,
                        timestamp = System.currentTimeMillis()
                    )
                )
                resourceWarningListener?.onStorageCritical(status.availableStorageMB)
            }
            status.availableStorageMB < STORAGE_WARNING_MB -> {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.STORAGE_LOW,
                        message = "Low storage space: ${status.availableStorageMB}MB remaining",
                        severity = WarningSeverity.WARNING,
                        timestamp = System.currentTimeMillis()
                    )
                )
                resourceWarningListener?.onStorageWarning(status.availableStorageMB)
            }
        }
        
        // Check memory levels
        when {
            status.freeMemoryPercent < (100 - MEMORY_CRITICAL_PERCENT) -> {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.MEMORY_CRITICAL,
                        message = "Critical memory usage: ${status.freeMemoryPercent.toInt()}% free",
                        severity = WarningSeverity.CRITICAL,
                        timestamp = System.currentTimeMillis()
                    )
                )
                resourceWarningListener?.onMemoryCritical(status.freeMemoryPercent)
            }
            status.freeMemoryPercent < (100 - MEMORY_WARNING_PERCENT) -> {
                warnings.add(
                    ResourceWarning(
                        type = ResourceWarningType.MEMORY_LOW,
                        message = "Low memory: ${status.freeMemoryPercent.toInt()}% free",
                        severity = WarningSeverity.WARNING,
                        timestamp = System.currentTimeMillis()
                    )
                )
                resourceWarningListener?.onMemoryWarning(status.freeMemoryPercent)
            }
        }
        
        // Check for resource constraints
        if (warnings.any { it.severity == WarningSeverity.CRITICAL }) {
            val constraint = if (warnings.any { it.type == ResourceWarningType.STORAGE_CRITICAL }) {
                ResourceConstraint.STORAGE_FULL
            } else {
                ResourceConstraint.MEMORY_EXHAUSTED
            }
            resourceWarningListener?.onResourceConstraint(constraint)
        }
        
        _resourceWarnings.value = warnings
    }
    
    fun cleanup() {
        logger.info("$TAG: Cleaning up resource monitor")
        stopMonitoring()
        resourceWarningListener = null
        scope.cancel()
    }
}

/**
 * Current status of system resources.
 */
data class ResourceStatus(
    val availableStorageMB: Long = 0,
    val totalStorageMB: Long = 0,
    val freeMemoryPercent: Double = 0.0,
    val usedMemoryMB: Double = 0.0,
    val maxMemoryMB: Double = 0.0,
    val isStorageWritable: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Warning about resource constraints.
 */
data class ResourceWarning(
    val type: ResourceWarningType,
    val message: String,
    val severity: WarningSeverity,
    val timestamp: Long
)

enum class ResourceWarningType {
    STORAGE_LOW,
    STORAGE_CRITICAL,
    STORAGE_NOT_WRITABLE,
    MEMORY_LOW,
    MEMORY_CRITICAL,
    INSUFFICIENT_STORAGE,
    INSUFFICIENT_MEMORY
}

enum class WarningSeverity {
    INFO,
    WARNING,
    CRITICAL
}

enum class ResourceConstraint {
    STORAGE_FULL,
    MEMORY_EXHAUSTED,
    STORAGE_UNAVAILABLE
}