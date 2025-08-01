package com.multisensor.recording.persistence

import android.content.Context
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for Shimmer device state persistence
 * Handles all database operations for Shimmer device configurations and connection states
 * Supports multiple simultaneous devices with comprehensive state management
 */
@Singleton
class ShimmerDeviceStateRepository @Inject constructor(
    private val context: Context
) {
    
    private val database by lazy { SessionStateDatabase.getDatabase(context) }
    private val deviceStateDao by lazy { database.shimmerDeviceStateDao() }
    
    // ========== Device State Operations ==========
    
    /**
     * Save or update device state
     */
    suspend fun saveDeviceState(deviceState: ShimmerDeviceState) = withContext(Dispatchers.IO) {
        deviceStateDao.insertDeviceState(deviceState)
        logConnectionHistory(
            deviceState.deviceAddress,
            deviceState.deviceName,
            deviceState.connectionType,
            ConnectionAction.CONFIGURATION_APPLIED,
            true
        )
    }
    
    /**
     * Get device state by address
     */
    suspend fun getDeviceState(address: String): ShimmerDeviceState? = withContext(Dispatchers.IO) {
        deviceStateDao.getDeviceState(address)
    }
    
    /**
     * Get all stored device states
     */
    suspend fun getAllDeviceStates(): List<ShimmerDeviceState> = withContext(Dispatchers.IO) {
        deviceStateDao.getAllDeviceStates()
    }
    
    /**
     * Get connected devices
     */
    suspend fun getConnectedDevices(): List<ShimmerDeviceState> = withContext(Dispatchers.IO) {
        deviceStateDao.getConnectedDevices()
    }
    
    /**
     * Get devices that should auto-reconnect
     */
    suspend fun getAutoReconnectDevices(): List<ShimmerDeviceState> = withContext(Dispatchers.IO) {
        deviceStateDao.getAutoReconnectDevices()
    }
    
    /**
     * Delete device state
     */
    suspend fun deleteDeviceState(address: String) = withContext(Dispatchers.IO) {
        val deviceState = deviceStateDao.getDeviceState(address)
        if (deviceState != null) {
            deviceStateDao.deleteDeviceState(deviceState)
        }
    }
    
    // ========== Connection Management ==========
    
    /**
     * Update connection status for a device
     */
    suspend fun updateConnectionStatus(address: String, connected: Boolean, deviceName: String? = null, connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE? = null) = withContext(Dispatchers.IO) {
        val timestamp = System.currentTimeMillis()
        deviceStateDao.updateConnectionStatus(address, connected, timestamp)
        
        if (connected) {
            deviceStateDao.resetConnectionAttempts(address)
        }
        
        // Log connection history
        val existingDevice = deviceStateDao.getDeviceState(address)
        logConnectionHistory(
            address,
            deviceName ?: existingDevice?.deviceName ?: "Unknown",
            connectionType ?: existingDevice?.connectionType ?: ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC,
            if (connected) ConnectionAction.CONNECT_SUCCESS else ConnectionAction.DISCONNECT,
            true
        )
    }
    
    /**
     * Log connection attempt with error
     */
    suspend fun logConnectionAttempt(address: String, success: Boolean, error: String? = null, deviceName: String? = null, connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE? = null) = withContext(Dispatchers.IO) {
        if (!success) {
            deviceStateDao.incrementConnectionAttempts(address, error)
        }
        
        val existingDevice = deviceStateDao.getDeviceState(address)
        logConnectionHistory(
            address,
            deviceName ?: existingDevice?.deviceName ?: "Unknown",
            connectionType ?: existingDevice?.connectionType ?: ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC,
            if (success) ConnectionAction.CONNECT_SUCCESS else ConnectionAction.CONNECT_FAILED,
            success,
            error
        )
    }
    
    // ========== Configuration Management ==========
    
    /**
     * Update sensor configuration for a device
     */
    suspend fun updateSensorConfiguration(
        address: String,
        enabledSensors: Set<String>,
        samplingRate: Double,
        gsrRange: Int,
        sensorConfig: String? = null
    ) = withContext(Dispatchers.IO) {
        deviceStateDao.updateSensorConfiguration(address, enabledSensors, samplingRate, gsrRange, sensorConfig)
        
        val deviceState = deviceStateDao.getDeviceState(address)
        if (deviceState != null) {
            logConnectionHistory(
                address,
                deviceState.deviceName,
                deviceState.connectionType,
                ConnectionAction.CONFIGURATION_APPLIED,
                true
            )
        }
    }
    
    /**
     * Update streaming status
     */
    suspend fun updateStreamingStatus(address: String, streaming: Boolean) = withContext(Dispatchers.IO) {
        val timestamp = System.currentTimeMillis()
        deviceStateDao.updateStreamingStatus(address, streaming, timestamp)
        
        val deviceState = deviceStateDao.getDeviceState(address)
        if (deviceState != null) {
            logConnectionHistory(
                address,
                deviceState.deviceName,
                deviceState.connectionType,
                if (streaming) ConnectionAction.STREAMING_STARTED else ConnectionAction.STREAMING_STOPPED,
                true
            )
        }
    }
    
    /**
     * Update SD logging status
     */
    suspend fun updateSDLoggingStatus(address: String, logging: Boolean) = withContext(Dispatchers.IO) {
        val timestamp = System.currentTimeMillis()
        deviceStateDao.updateSDLoggingStatus(address, logging, timestamp)
        
        val deviceState = deviceStateDao.getDeviceState(address)
        if (deviceState != null) {
            logConnectionHistory(
                address,
                deviceState.deviceName,
                deviceState.connectionType,
                if (logging) ConnectionAction.SD_LOGGING_STARTED else ConnectionAction.SD_LOGGING_STOPPED,
                true
            )
        }
    }
    
    /**
     * Update device information (battery, signal, firmware)
     */
    suspend fun updateDeviceInfo(address: String, batteryLevel: Int, signalStrength: Int, firmwareVersion: String) = withContext(Dispatchers.IO) {
        deviceStateDao.updateDeviceInfo(address, batteryLevel, signalStrength, firmwareVersion)
    }
    
    // ========== Multiple Device Support ==========
    
    /**
     * Get devices by connection priority for auto-reconnection
     */
    suspend fun getDevicesByPriority(): List<ShimmerDeviceState> = withContext(Dispatchers.IO) {
        deviceStateDao.getAutoReconnectDevices()
    }
    
    /**
     * Set device connection priority
     */
    suspend fun setDeviceConnectionPriority(address: String, priority: Int) = withContext(Dispatchers.IO) {
        val deviceState = deviceStateDao.getDeviceState(address)
        if (deviceState != null) {
            val updatedState = deviceState.copy(
                preferredConnectionOrder = priority,
                lastUpdated = System.currentTimeMillis()
            )
            deviceStateDao.updateDeviceState(updatedState)
        }
    }
    
    /**
     * Enable/disable auto-reconnect for a device
     */
    suspend fun setAutoReconnectEnabled(address: String, enabled: Boolean) = withContext(Dispatchers.IO) {
        val deviceState = deviceStateDao.getDeviceState(address)
        if (deviceState != null) {
            val updatedState = deviceState.copy(
                autoReconnectEnabled = enabled,
                lastUpdated = System.currentTimeMillis()
            )
            deviceStateDao.updateDeviceState(updatedState)
        }
    }
    
    // ========== Observable Data ==========
    
    /**
     * Observe all device states for real-time updates
     */
    fun observeAllDeviceStates(): Flow<List<ShimmerDeviceState>> {
        return deviceStateDao.observeAllDeviceStates()
    }
    
    /**
     * Observe connected devices
     */
    fun observeConnectedDevices(): Flow<List<ShimmerDeviceState>> {
        return deviceStateDao.observeConnectedDevices()
    }
    
    /**
     * Observe specific device state
     */
    fun observeDeviceState(address: String): Flow<ShimmerDeviceState?> {
        return deviceStateDao.observeDeviceState(address)
    }
    
    // ========== Connection History ==========
    
    /**
     * Log connection history event
     */
    private suspend fun logConnectionHistory(
        address: String,
        name: String,
        connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE,
        action: ConnectionAction,
        success: Boolean,
        errorMessage: String? = null,
        duration: Long = 0
    ) {
        val history = ShimmerConnectionHistory(
            deviceAddress = address,
            deviceName = name,
            connectionType = connectionType,
            action = action,
            success = success,
            errorMessage = errorMessage,
            duration = duration
        )
        deviceStateDao.insertConnectionHistory(history)
    }
    
    /**
     * Get connection history for a device
     */
    suspend fun getConnectionHistory(address: String, limit: Int = 50): List<ShimmerConnectionHistory> = withContext(Dispatchers.IO) {
        deviceStateDao.getConnectionHistory(address, limit)
    }
    
    /**
     * Get recent connection history across all devices
     */
    suspend fun getRecentConnectionHistory(limit: Int = 100): List<ShimmerConnectionHistory> = withContext(Dispatchers.IO) {
        deviceStateDao.getRecentConnectionHistory(limit)
    }
    
    // ========== Maintenance Operations ==========
    
    /**
     * Clean up old data
     */
    suspend fun cleanupOldData(maxAge: Long = 30 * 24 * 60 * 60 * 1000L) = withContext(Dispatchers.IO) { // 30 days
        val cutoffTime = System.currentTimeMillis() - maxAge
        deviceStateDao.deleteOldDeviceStates(cutoffTime)
        deviceStateDao.deleteOldConnectionHistory(cutoffTime)
    }
    
    /**
     * Get diagnostic information
     */
    suspend fun getDiagnosticInfo(): Map<String, Any> = withContext(Dispatchers.IO) {
        val allDevices = deviceStateDao.getAllDeviceStates()
        val connectedDevices = deviceStateDao.getConnectedDevices()
        val recentHistory = deviceStateDao.getRecentConnectionHistory(10)
        val failedAttempts = deviceStateDao.getFailedConnectionAttempts(10)
        
        mapOf(
            "total_devices" to allDevices.size,
            "connected_devices" to connectedDevices.size,
            "auto_reconnect_devices" to allDevices.count { it.autoReconnectEnabled },
            "recent_history_count" to recentHistory.size,
            "recent_failed_attempts" to failedAttempts.size,
            "devices_with_errors" to allDevices.count { !it.lastConnectionError.isNullOrEmpty() }
        )
    }
}