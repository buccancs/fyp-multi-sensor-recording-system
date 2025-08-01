package com.multisensor.recording.persistence

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import androidx.room.Delete
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import kotlinx.coroutines.flow.Flow

/**
 * DAO for Shimmer device state persistence operations
 * Supports multiple simultaneous devices and comprehensive state management
 */
@Dao
interface ShimmerDeviceStateDao {
    
    // ========== Device State Operations ==========
    
    /**
     * Insert or replace Shimmer device state
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDeviceState(deviceState: ShimmerDeviceState)
    
    /**
     * Update existing device state
     */
    @Update
    suspend fun updateDeviceState(deviceState: ShimmerDeviceState)
    
    /**
     * Delete device state
     */
    @Delete
    suspend fun deleteDeviceState(deviceState: ShimmerDeviceState)
    
    /**
     * Get device state by address
     */
    @Query("SELECT * FROM shimmer_device_state WHERE deviceAddress = :address")
    suspend fun getDeviceState(address: String): ShimmerDeviceState?
    
    /**
     * Get all stored device states
     */
    @Query("SELECT * FROM shimmer_device_state ORDER BY lastUpdated DESC")
    suspend fun getAllDeviceStates(): List<ShimmerDeviceState>
    
    /**
     * Get connected devices
     */
    @Query("SELECT * FROM shimmer_device_state WHERE isConnected = 1 ORDER BY preferredConnectionOrder ASC")
    suspend fun getConnectedDevices(): List<ShimmerDeviceState>
    
    /**
     * Get devices that should auto-reconnect
     */
    @Query("SELECT * FROM shimmer_device_state WHERE autoReconnectEnabled = 1 AND isConnected = 0 ORDER BY preferredConnectionOrder ASC")
    suspend fun getAutoReconnectDevices(): List<ShimmerDeviceState>
    
    /**
     * Get devices by connection type
     */
    @Query("SELECT * FROM shimmer_device_state WHERE connectionType = :connectionType ORDER BY lastUpdated DESC")
    suspend fun getDevicesByConnectionType(connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE): List<ShimmerDeviceState>
    
    /**
     * Get streaming devices
     */
    @Query("SELECT * FROM shimmer_device_state WHERE isStreaming = 1")
    suspend fun getStreamingDevices(): List<ShimmerDeviceState>
    
    /**
     * Get SD logging devices
     */
    @Query("SELECT * FROM shimmer_device_state WHERE isSDLogging = 1")
    suspend fun getSDLoggingDevices(): List<ShimmerDeviceState>
    
    /**
     * Update connection status for a device
     */
    @Query("UPDATE shimmer_device_state SET isConnected = :connected, lastConnectedTimestamp = :timestamp, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun updateConnectionStatus(address: String, connected: Boolean, timestamp: Long, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Update sensor configuration for a device
     */
    @Query("UPDATE shimmer_device_state SET enabledSensors = :sensors, samplingRate = :samplingRate, gsrRange = :gsrRange, sensorConfiguration = :config, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun updateSensorConfiguration(address: String, sensors: Set<String>, samplingRate: Double, gsrRange: Int, config: String?, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Update streaming status for a device
     */
    @Query("UPDATE shimmer_device_state SET isStreaming = :streaming, lastStreamingTimestamp = :timestamp, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun updateStreamingStatus(address: String, streaming: Boolean, timestamp: Long, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Update SD logging status for a device
     */
    @Query("UPDATE shimmer_device_state SET isSDLogging = :logging, lastSDLoggingTimestamp = :timestamp, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun updateSDLoggingStatus(address: String, logging: Boolean, timestamp: Long, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Update device information (battery, signal strength, etc.)
     */
    @Query("UPDATE shimmer_device_state SET batteryLevel = :battery, signalStrength = :signal, firmwareVersion = :firmware, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun updateDeviceInfo(address: String, battery: Int, signal: Int, firmware: String, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Increment connection attempts counter
     */
    @Query("UPDATE shimmer_device_state SET connectionAttempts = connectionAttempts + 1, lastConnectionError = :error, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun incrementConnectionAttempts(address: String, error: String?, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Reset connection attempts counter (after successful connection)
     */
    @Query("UPDATE shimmer_device_state SET connectionAttempts = 0, lastConnectionError = NULL, lastUpdated = :updateTime WHERE deviceAddress = :address")
    suspend fun resetConnectionAttempts(address: String, updateTime: Long = System.currentTimeMillis())
    
    /**
     * Delete devices last updated before specified timestamp (cleanup old entries)
     */
    @Query("DELETE FROM shimmer_device_state WHERE lastUpdated < :cutoffTime")
    suspend fun deleteOldDeviceStates(cutoffTime: Long)
    
    // ========== Observable Queries ==========
    
    /**
     * Observe all device states for real-time updates
     */
    @Query("SELECT * FROM shimmer_device_state ORDER BY lastUpdated DESC")
    fun observeAllDeviceStates(): Flow<List<ShimmerDeviceState>>
    
    /**
     * Observe connected devices
     */
    @Query("SELECT * FROM shimmer_device_state WHERE isConnected = 1 ORDER BY preferredConnectionOrder ASC")
    fun observeConnectedDevices(): Flow<List<ShimmerDeviceState>>
    
    /**
     * Observe specific device state
     */
    @Query("SELECT * FROM shimmer_device_state WHERE deviceAddress = :address")
    fun observeDeviceState(address: String): Flow<ShimmerDeviceState?>
    
    // ========== Connection History Operations ==========
    
    /**
     * Insert connection history entry
     */
    @Insert
    suspend fun insertConnectionHistory(history: ShimmerConnectionHistory)
    
    /**
     * Get connection history for a device
     */
    @Query("SELECT * FROM shimmer_connection_history WHERE deviceAddress = :address ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getConnectionHistory(address: String, limit: Int = 50): List<ShimmerConnectionHistory>
    
    /**
     * Get recent connection history across all devices
     */
    @Query("SELECT * FROM shimmer_connection_history ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecentConnectionHistory(limit: Int = 100): List<ShimmerConnectionHistory>
    
    /**
     * Get failed connection attempts for debugging
     */
    @Query("SELECT * FROM shimmer_connection_history WHERE success = 0 AND action = 'CONNECT_ATTEMPT' ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getFailedConnectionAttempts(limit: Int = 50): List<ShimmerConnectionHistory>
    
    /**
     * Delete old connection history entries
     */
    @Query("DELETE FROM shimmer_connection_history WHERE timestamp < :cutoffTime")
    suspend fun deleteOldConnectionHistory(cutoffTime: Long)
    
    /**
     * Count connection attempts for a device within time period
     */
    @Query("SELECT COUNT(*) FROM shimmer_connection_history WHERE deviceAddress = :address AND action = 'CONNECT_ATTEMPT' AND timestamp > :since")
    suspend fun countConnectionAttempts(address: String, since: Long): Int
}