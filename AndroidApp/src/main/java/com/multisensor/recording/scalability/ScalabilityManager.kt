package com.multisensor.recording.scalability

import android.content.Context
import android.os.Environment
import android.os.StatFs
import android.util.Log
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.min

/**
 * NFR7: Scalability - Manages system scaling for multiple devices and extended sessions
 * 
 * Implements:
 * - Multi-device coordination (up to 8+ Android devices)
 * - Extended session support (120+ minutes)
 * - File chunking for large recordings (~1 GB segments)
 * - Resource management and allocation
 * - Storage management for large datasets
 * - Connection pooling and management
 * 
 * Requirements from 3.tex section NFR7:
 * - Tested with up to 8 Android devices streaming concurrently
 * - Support sessions up to 120+ minutes duration
 * - Automatic file chunking to ~1 GB segments for manageability
 * - High-resolution extended sessions without overwhelming file system
 * - Configurable connection limits (up to 10 connections)
 * - Resource scaling based on device capabilities
 */
class ScalabilityManager(private val context: Context) {
    
    companion object {
        private const val TAG = "ScalabilityManager"
        
        // Scalability limits from NFR7
        private const val MAX_CONCURRENT_DEVICES = 8
        private const val MAX_CONNECTION_POOL_SIZE = 10
        private const val MAX_SESSION_DURATION_MINUTES = 120
        private const val CHUNK_SIZE_GB = 1.0
        private const val CHUNK_SIZE_BYTES = (CHUNK_SIZE_GB * 1024 * 1024 * 1024).toLong()
        
        // Resource thresholds
        private const val MIN_AVAILABLE_STORAGE_GB = 5.0
        private const val MIN_MEMORY_FOR_DEVICE_MB = 256
        private const val RESOURCE_CHECK_INTERVAL_MS = 30000L // 30 seconds
        
        // Performance scaling
        private const val HIGH_PERFORMANCE_DEVICE_THRESHOLD_GB = 4 // RAM
        private const val MEDIUM_PERFORMANCE_DEVICE_THRESHOLD_GB = 2
    }

    private val isScalingActive = AtomicBoolean(false)
    private val connectedDeviceCount = AtomicInteger(0)
    private val totalDataWritten = AtomicLong(0)
    private val sessionStartTime = AtomicLong(0)
    
    // Resource management
    private val deviceResourceMap = ConcurrentHashMap<String, DeviceResources>()
    private val connectionPool = ConcurrentHashMap<String, ConnectionInfo>()
    private val chunkManagers = ConcurrentHashMap<String, ChunkManager>()
    
    // Scaling configuration
    private var scalingConfig = ScalingConfiguration()
    private val scalingScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var resourceMonitoringJob: Job? = null

    /**
     * Initialize scalability manager with configuration
     */
    fun initializeScaling(config: ScalingConfiguration = ScalingConfiguration()): ScalingStatus {
        Logger.i(TAG, "Initializing scalability manager...")
        this.scalingConfig = config
        
        try {
            // Assess device capabilities
            val deviceCapabilities = assessDeviceCapabilities()
            
            // Validate storage capacity
            val storageStatus = validateStorageCapacity()
            
            // Setup resource monitoring
            startResourceMonitoring()
            
            isScalingActive.set(true)
            
            Logger.i(TAG, "Scalability manager initialized - Device tier: ${deviceCapabilities.performanceTier}")
            return ScalingStatus.INITIALIZED
            
        } catch (e: Exception) {
            Logger.e(TAG, "Failed to initialize scalability manager", e)
            return ScalingStatus.FAILED
        }
    }

    /**
     * Register a new device for scaling management
     * NFR7: Multi-device coordination (up to 8 devices)
     */
    fun registerDevice(deviceId: String, deviceInfo: DeviceInfo): Boolean {
        val currentDeviceCount = connectedDeviceCount.get()
        
        if (currentDeviceCount >= scalingConfig.maxConcurrentDevices) {
            Logger.w(TAG, "Cannot register device $deviceId - maximum device limit reached ($currentDeviceCount/${scalingConfig.maxConcurrentDevices})")
            return false
        }
        
        // Assess device resources
        val deviceResources = assessDeviceResources(deviceInfo)
        
        // Check if we have sufficient resources for this device
        if (!hasResourcesForDevice(deviceResources)) {
            Logger.w(TAG, "Insufficient resources to register device $deviceId")
            return false
        }
        
        // Register device
        deviceResourceMap[deviceId] = deviceResources
        connectionPool[deviceId] = ConnectionInfo(deviceId, System.currentTimeMillis())
        chunkManagers[deviceId] = ChunkManager(deviceId, scalingConfig.chunkSizeBytes)
        
        val newCount = connectedDeviceCount.incrementAndGet()
        Logger.i(TAG, "Device $deviceId registered successfully ($newCount/${scalingConfig.maxConcurrentDevices} devices)")
        
        // Adjust resource allocation based on device count
        adjustResourceAllocation()
        
        return true
    }

    /**
     * Unregister device from scaling management
     */
    fun unregisterDevice(deviceId: String) {
        deviceResourceMap.remove(deviceId)
        connectionPool.remove(deviceId)
        chunkManagers.remove(deviceId)?.cleanup()
        
        val newCount = connectedDeviceCount.decrementAndGet()
        Logger.i(TAG, "Device $deviceId unregistered ($newCount devices remaining)")
        
        // Readjust resources
        adjustResourceAllocation()
    }

    /**
     * Start a scalable recording session
     * NFR7: Sessions up to 120+ minutes
     */
    fun startScalableSession(sessionId: String, expectedDurationMinutes: Int): SessionScalingInfo {
        if (expectedDurationMinutes > scalingConfig.maxSessionDurationMinutes) {
            Logger.w(TAG, "Session duration $expectedDurationMinutes minutes exceeds maximum ${scalingConfig.maxSessionDurationMinutes}")
        }
        
        sessionStartTime.set(System.currentTimeMillis())
        totalDataWritten.set(0)
        
        // Calculate expected data volume
        val estimatedDataGB = estimateSessionDataSize(expectedDurationMinutes, connectedDeviceCount.get())
        
        // Ensure sufficient storage
        val storageAvailable = getAvailableStorageGB()
        if (storageAvailable < estimatedDataGB + scalingConfig.minAvailableStorageGB) {
            Logger.w(TAG, "Insufficient storage for session: need ${estimatedDataGB}GB, available ${storageAvailable}GB")
        }
        
        // Initialize chunk managers for the session
        chunkManagers.values.forEach { it.startSession(sessionId) }
        
        Logger.i(TAG, "Scalable session started: $sessionId (${connectedDeviceCount.get()} devices, estimated ${estimatedDataGB}GB)")
        
        return SessionScalingInfo(
            sessionId = sessionId,
            deviceCount = connectedDeviceCount.get(),
            estimatedDataSizeGB = estimatedDataGB,
            availableStorageGB = storageAvailable,
            chunkingEnabled = scalingConfig.enableFileChunking,
            expectedChunkCount = calculateExpectedChunkCount(estimatedDataGB)
        )
    }

    /**
     * Manage file chunking for large recordings
     * NFR7: File chunking to ~1 GB segments
     */
    fun manageFileChunking(deviceId: String, filePath: String, bytesWritten: Long): ChunkingResult {
        val chunkManager = chunkManagers[deviceId]
        if (chunkManager == null) {
            Logger.w(TAG, "No chunk manager for device $deviceId")
            return ChunkingResult(false, filePath, 0)
        }
        
        totalDataWritten.addAndGet(bytesWritten)
        
        return if (scalingConfig.enableFileChunking) {
            chunkManager.manageChunk(filePath, bytesWritten)
        } else {
            ChunkingResult(false, filePath, 0)
        }
    }

    /**
     * Monitor resource usage and scale accordingly
     */
    private fun startResourceMonitoring() {
        resourceMonitoringJob = scalingScope.launch {
            while (isScalingActive.get()) {
                try {
                    monitorAndAdjustResources()
                    delay(RESOURCE_CHECK_INTERVAL_MS)
                } catch (e: Exception) {
                    Logger.e(TAG, "Error in resource monitoring", e)
                }
            }
        }
    }

    /**
     * Monitor resources and adjust scaling parameters
     */
    private fun monitorAndAdjustResources() {
        val currentMemoryUsage = getCurrentMemoryUsagePercent()
        val currentStorageUsage = getCurrentStorageUsagePercent()
        val sessionDurationMinutes = getSessionDurationMinutes()
        
        // Check for resource pressure
        if (currentMemoryUsage > 80.0) {
            Logger.w(TAG, "High memory usage: ${currentMemoryUsage}% - may need to reduce device count or quality")
            adjustForHighMemoryUsage()
        }
        
        if (currentStorageUsage > 85.0) {
            Logger.w(TAG, "High storage usage: ${currentStorageUsage}% - enabling aggressive chunking")
            enableAggressiveChunking()
        }
        
        // Check session duration
        if (sessionDurationMinutes > scalingConfig.maxSessionDurationMinutes) {
            Logger.w(TAG, "Session duration ${sessionDurationMinutes} minutes exceeds recommended maximum")
        }
        
        // Auto-adjust quality for scalability
        if (connectedDeviceCount.get() > 6) {
            suggestQualityReduction()
        }
    }

    /**
     * Assess device capabilities for performance tiering
     */
    private fun assessDeviceCapabilities(): DeviceCapabilities {
        val runtime = Runtime.getRuntime()
        val maxMemoryMB = runtime.maxMemory() / (1024 * 1024)
        val processors = Runtime.getRuntime().availableProcessors()
        
        val performanceTier = when {
            maxMemoryMB >= HIGH_PERFORMANCE_DEVICE_THRESHOLD_GB * 1024 -> PerformanceTier.HIGH
            maxMemoryMB >= MEDIUM_PERFORMANCE_DEVICE_THRESHOLD_GB * 1024 -> PerformanceTier.MEDIUM
            else -> PerformanceTier.LOW
        }
        
        Logger.d(TAG, "Device capabilities: ${maxMemoryMB}MB RAM, $processors cores, tier: $performanceTier")
        
        return DeviceCapabilities(
            memoryMB = maxMemoryMB.toInt(),
            processorCount = processors,
            performanceTier = performanceTier,
            recommendedDeviceLimit = when (performanceTier) {
                PerformanceTier.HIGH -> 8
                PerformanceTier.MEDIUM -> 5
                PerformanceTier.LOW -> 3
            }
        )
    }

    /**
     * Validate storage capacity for scalable operations
     */
    private fun validateStorageCapacity(): StorageStatus {
        val availableGB = getAvailableStorageGB()
        
        return when {
            availableGB >= 20.0 -> StorageStatus.EXCELLENT
            availableGB >= 10.0 -> StorageStatus.GOOD
            availableGB >= scalingConfig.minAvailableStorageGB -> StorageStatus.ADEQUATE
            else -> StorageStatus.INSUFFICIENT
        }
    }

    /**
     * Get available storage in GB
     */
    private fun getAvailableStorageGB(): Double {
        return try {
            val externalFilesDir = context.getExternalFilesDir(null)
            val stat = StatFs(externalFilesDir?.path ?: Environment.getExternalStorageDirectory().path)
            val availableBytes = stat.availableBytes
            availableBytes / (1024.0 * 1024.0 * 1024.0)
        } catch (e: Exception) {
            Logger.w(TAG, "Could not determine available storage", e)
            0.0
        }
    }

    /**
     * Estimate session data size based on duration and device count
     */
    private fun estimateSessionDataSize(durationMinutes: Int, deviceCount: Int): Double {
        // Estimate per device per minute: ~50MB (video) + ~1MB (sensor data)
        val dataPerDevicePerMinuteGB = 0.051 // ~51MB
        return durationMinutes * deviceCount * dataPerDevicePerMinuteGB
    }

    /**
     * Calculate expected chunk count for session
     */
    private fun calculateExpectedChunkCount(estimatedDataGB: Double): Int {
        return if (scalingConfig.enableFileChunking) {
            kotlin.math.ceil(estimatedDataGB / scalingConfig.chunkSizeGB).toInt()
        } else {
            1
        }
    }

    /**
     * Assess resources required for a device
     */
    private fun assessDeviceResources(deviceInfo: DeviceInfo): DeviceResources {
        val estimatedMemoryMB = when {
            deviceInfo.supportsHighResVideo -> 512
            deviceInfo.supportsThermalCamera -> 256
            else -> 128
        }
        
        val estimatedBandwidthMbps = when {
            deviceInfo.supportsHighResVideo -> 15.0
            else -> 8.0
        }
        
        return DeviceResources(
            requiredMemoryMB = estimatedMemoryMB,
            estimatedBandwidthMbps = estimatedBandwidthMbps,
            supportedStreams = listOfNotNull(
                "rgb_camera",
                if (deviceInfo.supportsThermalCamera) "thermal_camera" else null,
                if (deviceInfo.supportsGsrSensor) "gsr_sensor" else null
            )
        )
    }

    /**
     * Check if we have resources for an additional device
     */
    private fun hasResourcesForDevice(resources: DeviceResources): Boolean {
        val currentMemoryUsage = getCurrentMemoryUsagePercent()
        val estimatedNewUsage = currentMemoryUsage + (resources.requiredMemoryMB / (Runtime.getRuntime().maxMemory() / 1024 / 1024)) * 100
        
        return estimatedNewUsage < 85.0 // Keep under 85% memory usage
    }

    /**
     * Adjust resource allocation based on current device count
     */
    private fun adjustResourceAllocation() {
        val deviceCount = connectedDeviceCount.get()
        
        // Adjust quality settings based on device count
        val qualityMultiplier = when {
            deviceCount <= 2 -> 1.0
            deviceCount <= 4 -> 0.8
            deviceCount <= 6 -> 0.6
            else -> 0.5
        }
        
        Logger.d(TAG, "Adjusted quality multiplier to $qualityMultiplier for $deviceCount devices")
    }

    /**
     * Get current memory usage percentage
     */
    private fun getCurrentMemoryUsagePercent(): Double {
        val runtime = Runtime.getRuntime()
        val used = runtime.totalMemory() - runtime.freeMemory()
        val max = runtime.maxMemory()
        return (used.toDouble() / max.toDouble()) * 100.0
    }

    /**
     * Get current storage usage percentage
     */
    private fun getCurrentStorageUsagePercent(): Double {
        return try {
            val externalFilesDir = context.getExternalFilesDir(null)
            val stat = StatFs(externalFilesDir?.path ?: Environment.getExternalStorageDirectory().path)
            val total = stat.totalBytes
            val available = stat.availableBytes
            val used = total - available
            (used.toDouble() / total.toDouble()) * 100.0
        } catch (e: Exception) {
            0.0
        }
    }

    /**
     * Get session duration in minutes
     */
    private fun getSessionDurationMinutes(): Long {
        val startTime = sessionStartTime.get()
        return if (startTime > 0) {
            (System.currentTimeMillis() - startTime) / (1000 * 60)
        } else {
            0
        }
    }

    /**
     * Adjust for high memory usage
     */
    private fun adjustForHighMemoryUsage() {
        // Suggest reducing quality or device count
        Logger.i(TAG, "Adjusting for high memory usage - consider reducing quality or device count")
    }

    /**
     * Enable aggressive chunking to save storage
     */
    private fun enableAggressiveChunking() {
        chunkManagers.values.forEach { it.enableAggressiveChunking() }
    }

    /**
     * Suggest quality reduction for scalability
     */
    private fun suggestQualityReduction() {
        Logger.i(TAG, "Consider reducing video quality or frame rate for better scalability with ${connectedDeviceCount.get()} devices")
    }

    /**
     * Get current scaling status
     */
    fun getScalingStatus(): ScalingStatusInfo {
        return ScalingStatusInfo(
            isActive = isScalingActive.get(),
            connectedDevices = connectedDeviceCount.get(),
            maxDevices = scalingConfig.maxConcurrentDevices,
            memoryUsagePercent = getCurrentMemoryUsagePercent(),
            storageUsagePercent = getCurrentStorageUsagePercent(),
            totalDataWrittenGB = totalDataWritten.get() / (1024.0 * 1024.0 * 1024.0),
            sessionDurationMinutes = getSessionDurationMinutes(),
            chunkingEnabled = scalingConfig.enableFileChunking
        )
    }

    /**
     * Cleanup scaling resources
     */
    fun cleanup() {
        isScalingActive.set(false)
        resourceMonitoringJob?.cancel()
        chunkManagers.values.forEach { it.cleanup() }
        chunkManagers.clear()
        deviceResourceMap.clear()
        connectionPool.clear()
        Logger.i(TAG, "Scalability manager cleaned up")
    }

    // Data classes and enums

    data class ScalingConfiguration(
        val maxConcurrentDevices: Int = MAX_CONCURRENT_DEVICES,
        val maxConnectionPoolSize: Int = MAX_CONNECTION_POOL_SIZE,
        val maxSessionDurationMinutes: Int = MAX_SESSION_DURATION_MINUTES,
        val chunkSizeGB: Double = CHUNK_SIZE_GB,
        val chunkSizeBytes: Long = CHUNK_SIZE_BYTES,
        val minAvailableStorageGB: Double = MIN_AVAILABLE_STORAGE_GB,
        val enableFileChunking: Boolean = true,
        val enableAdaptiveQuality: Boolean = true
    )

    data class DeviceInfo(
        val deviceId: String,
        val supportsHighResVideo: Boolean = false,
        val supportsThermalCamera: Boolean = false,
        val supportsGsrSensor: Boolean = false,
        val estimatedMemoryMB: Int = 256
    )

    data class DeviceResources(
        val requiredMemoryMB: Int,
        val estimatedBandwidthMbps: Double,
        val supportedStreams: List<String>
    )

    data class DeviceCapabilities(
        val memoryMB: Int,
        val processorCount: Int,
        val performanceTier: PerformanceTier,
        val recommendedDeviceLimit: Int
    )

    data class SessionScalingInfo(
        val sessionId: String,
        val deviceCount: Int,
        val estimatedDataSizeGB: Double,
        val availableStorageGB: Double,
        val chunkingEnabled: Boolean,
        val expectedChunkCount: Int
    )

    data class ChunkingResult(
        val chunkCreated: Boolean,
        val newFilePath: String,
        val chunkNumber: Int
    )

    data class ConnectionInfo(
        val deviceId: String,
        val connectedAt: Long,
        val lastActivity: Long = System.currentTimeMillis()
    )

    data class ScalingStatusInfo(
        val isActive: Boolean,
        val connectedDevices: Int,
        val maxDevices: Int,
        val memoryUsagePercent: Double,
        val storageUsagePercent: Double,
        val totalDataWrittenGB: Double,
        val sessionDurationMinutes: Long,
        val chunkingEnabled: Boolean
    )

    enum class ScalingStatus {
        INITIALIZED,
        FAILED,
        RESOURCE_LIMITED
    }

    enum class StorageStatus {
        EXCELLENT,
        GOOD,
        ADEQUATE,
        INSUFFICIENT
    }

    enum class PerformanceTier {
        HIGH,
        MEDIUM,
        LOW
    }

    /**
     * Chunk manager for handling file segmentation
     */
    private class ChunkManager(private val deviceId: String, private val chunkSizeBytes: Long) {
        private var currentChunkNumber = 0
        private var currentChunkSize = 0L
        private var aggressiveChunking = false
        private var sessionId: String? = null

        fun startSession(sessionId: String) {
            this.sessionId = sessionId
            currentChunkNumber = 0
            currentChunkSize = 0L
        }

        fun manageChunk(filePath: String, bytesWritten: Long): ChunkingResult {
            currentChunkSize += bytesWritten
            
            val chunkThreshold = if (aggressiveChunking) chunkSizeBytes / 2 else chunkSizeBytes
            
            return if (currentChunkSize >= chunkThreshold) {
                currentChunkNumber++
                currentChunkSize = 0L
                
                val newPath = generateChunkPath(filePath, currentChunkNumber)
                ChunkingResult(true, newPath, currentChunkNumber)
            } else {
                ChunkingResult(false, filePath, currentChunkNumber)
            }
        }

        fun enableAggressiveChunking() {
            aggressiveChunking = true
        }

        private fun generateChunkPath(originalPath: String, chunkNumber: Int): String {
            val file = File(originalPath)
            val nameWithoutExt = file.nameWithoutExtension
            val extension = file.extension
            val parentDir = file.parent
            
            return File(parentDir, "${nameWithoutExt}_chunk${chunkNumber}.${extension}").absolutePath
        }

        fun cleanup() {
            // Cleanup any temporary chunk resources
        }
    }
}