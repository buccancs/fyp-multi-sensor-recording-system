package com.multisensor.recording.network

import android.content.Context
import android.util.Log
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger

/**
 * FR8: Fault Tolerance and Recovery - Device error recovery and reconnection
 * Handles device disconnections, errors, and automatic recovery mechanisms
 */
class FaultToleranceManager(private val context: Context) {
    
    companion object {
        private const val TAG = "FaultToleranceManager"
        private const val MAX_RETRY_ATTEMPTS = 3
        private const val RETRY_DELAY_MS = 2000L
        private const val HEALTH_CHECK_INTERVAL_MS = 10000L
        private const val RECOVERY_TIMEOUT_MS = 30000L
    }

    // Recovery state
    private val isRecoveryActive = AtomicBoolean(false)
    private val deviceHealthStatus = ConcurrentHashMap<String, DeviceHealth>()
    private val retryCounters = ConcurrentHashMap<String, AtomicInteger>()
    
    // Coroutine scope for recovery operations
    private val recoveryScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var healthCheckJob: Job? = null
    
    // Callbacks
    private var deviceRecoveryCallback: ((String, Boolean, String?) -> Unit)? = null
    private var systemHealthCallback: ((Boolean, Map<String, DeviceHealth>) -> Unit)? = null

    init {
        startHealthMonitoring()
    }

    /**
     * Register a device for fault tolerance monitoring
     */
    fun registerDevice(deviceId: String, deviceType: DeviceType, recoveryHandler: suspend () -> Boolean) {
        val health = DeviceHealth(
            deviceId = deviceId,
            deviceType = deviceType,
            status = DeviceStatus.UNKNOWN,
            lastSeen = System.currentTimeMillis(),
            recoveryHandler = recoveryHandler
        )
        
        deviceHealthStatus[deviceId] = health
        retryCounters[deviceId] = AtomicInteger(0)
        
        Logger.i(TAG, "Registered device for monitoring: $deviceId ($deviceType)")
    }

    /**
     * Update device health status
     */
    fun updateDeviceHealth(deviceId: String, status: DeviceStatus, errorMessage: String? = null) {
        val health = deviceHealthStatus[deviceId] ?: return
        
        health.status = status
        health.lastSeen = System.currentTimeMillis()
        health.errorMessage = errorMessage
        
        if (status == DeviceStatus.ERROR || status == DeviceStatus.DISCONNECTED) {
            Logger.w(TAG, "Device $deviceId reported ${status.name}: $errorMessage")
            triggerRecovery(deviceId)
        } else if (status == DeviceStatus.CONNECTED) {
            // Device recovered successfully
            retryCounters[deviceId]?.set(0)
            Logger.i(TAG, "Device $deviceId recovered successfully")
        }
        
        // Notify system health callback
        systemHealthCallback?.invoke(isSystemHealthy(), deviceHealthStatus.toMap())
    }

    /**
     * Report device error and trigger recovery
     */
    fun reportDeviceError(deviceId: String, error: Exception) {
        Logger.e(TAG, "Device error reported for $deviceId", error)
        updateDeviceHealth(deviceId, DeviceStatus.ERROR, error.message)
    }

    /**
     * Trigger manual recovery for a device
     */
    fun triggerRecovery(deviceId: String) {
        val health = deviceHealthStatus[deviceId] ?: return
        val retryCount = retryCounters[deviceId] ?: return
        
        if (retryCount.get() >= MAX_RETRY_ATTEMPTS) {
            Logger.w(TAG, "Max retry attempts reached for device $deviceId")
            health.status = DeviceStatus.FAILED
            deviceRecoveryCallback?.invoke(deviceId, false, "Max retry attempts exceeded")
            return
        }

        if (isRecoveryActive.get()) {
            Logger.d(TAG, "Recovery already in progress for device $deviceId")
            return
        }

        Logger.i(TAG, "Triggering recovery for device $deviceId (attempt ${retryCount.get() + 1}/$MAX_RETRY_ATTEMPTS)")
        
        recoveryScope.launch {
            performDeviceRecovery(deviceId)
        }
    }

    /**
     * Perform device recovery operation
     */
    private suspend fun performDeviceRecovery(deviceId: String) {
        val health = deviceHealthStatus[deviceId] ?: return
        val retryCount = retryCounters[deviceId] ?: return
        
        isRecoveryActive.set(true)
        health.status = DeviceStatus.RECOVERING
        
        try {
            Logger.i(TAG, "Starting recovery for device $deviceId")
            
            // Wait before retry
            delay(RETRY_DELAY_MS)
            
            // Call device-specific recovery handler
            val recoverySuccess = withTimeout(RECOVERY_TIMEOUT_MS) {
                health.recoveryHandler()
            }
            
            if (recoverySuccess) {
                health.status = DeviceStatus.CONNECTED
                health.lastSeen = System.currentTimeMillis()
                health.errorMessage = null
                retryCount.set(0)
                
                Logger.i(TAG, "Device $deviceId recovered successfully")
                deviceRecoveryCallback?.invoke(deviceId, true, null)
                
            } else {
                // Recovery failed, increment retry count
                val currentRetries = retryCount.incrementAndGet()
                
                if (currentRetries >= MAX_RETRY_ATTEMPTS) {
                    health.status = DeviceStatus.FAILED
                    Logger.w(TAG, "Device $deviceId recovery failed - max retries exceeded")
                    deviceRecoveryCallback?.invoke(deviceId, false, "Recovery failed after $MAX_RETRY_ATTEMPTS attempts")
                } else {
                    health.status = DeviceStatus.ERROR
                    Logger.w(TAG, "Device $deviceId recovery failed - will retry (attempt $currentRetries/$MAX_RETRY_ATTEMPTS)")
                    
                    // Schedule next retry
                    delay(RETRY_DELAY_MS)
                    performDeviceRecovery(deviceId)
                }
            }
            
        } catch (e: TimeoutCancellationException) {
            Logger.w(TAG, "Recovery timeout for device $deviceId")
            health.status = DeviceStatus.ERROR
            val currentRetries = retryCount.incrementAndGet()
            deviceRecoveryCallback?.invoke(deviceId, false, "Recovery timeout")
            
        } catch (e: Exception) {
            Logger.e(TAG, "Recovery error for device $deviceId", e)
            health.status = DeviceStatus.ERROR
            val currentRetries = retryCount.incrementAndGet()
            deviceRecoveryCallback?.invoke(deviceId, false, "Recovery error: ${e.message}")
            
        } finally {
            isRecoveryActive.set(false)
        }
    }

    /**
     * Start health monitoring for all devices
     */
    private fun startHealthMonitoring() {
        healthCheckJob = recoveryScope.launch {
            while (true) {
                delay(HEALTH_CHECK_INTERVAL_MS)
                
                val currentTime = System.currentTimeMillis()
                deviceHealthStatus.values.forEach { health ->
                    // Check for stale devices (no heartbeat)
                    if (health.status == DeviceStatus.CONNECTED) {
                        val timeSinceLastSeen = currentTime - health.lastSeen
                        if (timeSinceLastSeen > HEALTH_CHECK_INTERVAL_MS * 2) {
                            Logger.w(TAG, "Device ${health.deviceId} appears stale (${timeSinceLastSeen}ms since last seen)")
                            updateDeviceHealth(health.deviceId, DeviceStatus.DISCONNECTED, "Device timeout")
                        }
                    }
                }
                
                // Update system health
                systemHealthCallback?.invoke(isSystemHealthy(), deviceHealthStatus.toMap())
            }
        }
    }

    /**
     * Check if system is healthy (all devices operational)
     */
    fun isSystemHealthy(): Boolean {
        return deviceHealthStatus.values.all { health ->
            health.status == DeviceStatus.CONNECTED || health.status == DeviceStatus.UNKNOWN
        }
    }

    /**
     * Get health status for all devices
     */
    fun getDeviceHealthStatus(): Map<String, DeviceHealth> {
        return deviceHealthStatus.toMap()
    }

    /**
     * Get health status for specific device
     */
    fun getDeviceHealth(deviceId: String): DeviceHealth? {
        return deviceHealthStatus[deviceId]
    }

    /**
     * Reset retry counter for device
     */
    fun resetRetryCount(deviceId: String) {
        retryCounters[deviceId]?.set(0)
        Logger.d(TAG, "Reset retry count for device $deviceId")
    }

    /**
     * Set device recovery callback
     */
    fun setDeviceRecoveryCallback(callback: (String, Boolean, String?) -> Unit) {
        deviceRecoveryCallback = callback
    }

    /**
     * Set system health callback
     */
    fun setSystemHealthCallback(callback: (Boolean, Map<String, DeviceHealth>) -> Unit) {
        systemHealthCallback = callback
    }

    /**
     * Get system status summary
     */
    fun getSystemStatusSummary(): SystemStatus {
        val totalDevices = deviceHealthStatus.size
        val connectedDevices = deviceHealthStatus.values.count { it.status == DeviceStatus.CONNECTED }
        val failedDevices = deviceHealthStatus.values.count { it.status == DeviceStatus.FAILED }
        val recoveringDevices = deviceHealthStatus.values.count { it.status == DeviceStatus.RECOVERING }
        
        return SystemStatus(
            totalDevices = totalDevices,
            connectedDevices = connectedDevices,
            failedDevices = failedDevices,
            recoveringDevices = recoveringDevices,
            isHealthy = isSystemHealthy()
        )
    }

    /**
     * Cleanup resources
     */
    fun cleanup() {
        healthCheckJob?.cancel()
        recoveryScope.cancel()
        deviceHealthStatus.clear()
        retryCounters.clear()
    }
}

/**
 * Device health information
 */
data class DeviceHealth(
    val deviceId: String,
    val deviceType: DeviceType,
    var status: DeviceStatus,
    var lastSeen: Long,
    var errorMessage: String? = null,
    val recoveryHandler: suspend () -> Boolean
)

/**
 * Device types
 */
enum class DeviceType {
    RGB_CAMERA,
    THERMAL_CAMERA,
    GSR_SENSOR,
    PC_CONNECTION
}

/**
 * Device status
 */
enum class DeviceStatus {
    UNKNOWN,
    CONNECTED,
    DISCONNECTED,
    ERROR,
    RECOVERING,
    FAILED
}

/**
 * System status summary
 */
data class SystemStatus(
    val totalDevices: Int,
    val connectedDevices: Int,
    val failedDevices: Int,
    val recoveringDevices: Int,
    val isHealthy: Boolean
)