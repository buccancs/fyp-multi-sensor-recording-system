package com.multisensor.recording.recording

import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import org.mockito.kotlin.verify
import org.mockito.kotlin.any
import com.multisensor.recording.util.Logger

/**
 * comprehensive test suite for connection manager
 * tests bluetooth device connection management, retry logic, and health monitoring
 */
class ConnectionManagerTest {
    
    @Mock
    private lateinit var mockLogger: Logger
    
    private lateinit var connectionManager: ConnectionManager
    
    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        connectionManager = ConnectionManager(mockLogger)
    }
    
    @Test
    fun `should start connection management successfully`() {
        // when
        connectionManager.startManagement()
        
        // then - management start should be logged
        verify(mockLogger).info(any())
        
        // and - should report as managing
        val stats = connectionManager.getOverallStatistics()
        assertTrue(stats["isManaging"] as Boolean)
    }
    
    @Test
    fun `should stop connection management cleanly`() {
        // given
        connectionManager.startManagement()
        
        // when
        connectionManager.stopManagement()
        
        // then
        verify(mockLogger).info(any())
        
        // and - should report as not managing
        val stats = connectionManager.getOverallStatistics()
        assertFalse(stats["isManaging"] as Boolean)
    }
    
    @Test
    fun `should attempt device connection with retry logic`() = runTest {
        // given
        val deviceId = "shimmer_device_001"
        val mockConnectionFunction: suspend () -> Boolean = { true }
        
        // when
        val result = connectionManager.connectWithRetry(deviceId, mockConnectionFunction)
        
        // then
        assertTrue(result)
        verify(mockLogger).info(any())
    }
    
    @Test
    fun `should handle connection failures gracefully`() = runTest {
        // given
        val deviceId = "shimmer_device_002"
        val mockConnectionFunction: suspend () -> Boolean = { false }
        
        // when
        val result = connectionManager.connectWithRetry(deviceId, mockConnectionFunction)
        
        // then
        assertFalse(result)
        verify(mockLogger).error(any())
    }
    
    @Test
    fun `should track connection statistics correctly`() = runTest {
        // given
        val deviceId = "shimmer_device_003"
        val mockConnectionFunction: suspend () -> Boolean = { true }
        
        // when
        connectionManager.connectWithRetry(deviceId, mockConnectionFunction)
        
        // then
        val stats = connectionManager.getConnectionStatistics(deviceId)
        assertEquals(deviceId, stats["deviceId"])
        assertTrue((stats["totalAttempts"] as Int) > 0)
    }
    
    @Test
    fun `should start auto-reconnection for device`() {
        // given
        val deviceId = "shimmer_device_004"
        val mockConnectionFunction: suspend () -> Boolean = { true }
        connectionManager.startManagement()
        
        // when
        connectionManager.startAutoReconnection(deviceId, mockConnectionFunction)
        
        // then - should not throw exception and start reconnection monitoring
        verify(mockLogger).info(any())
    }
    
    @Test
    fun `should stop auto-reconnection for device`() {
        // given
        val deviceId = "shimmer_device_005" 
        val mockConnectionFunction: suspend () -> Boolean = { true }
        connectionManager.startManagement()
        connectionManager.startAutoReconnection(deviceId, mockConnectionFunction)
        
        // when
        connectionManager.stopAutoReconnection(deviceId)
        
        // then
        verify(mockLogger).debug(any())
    }
    
    @Test
    fun `should start health monitoring for device`() {
        // given
        val deviceId = "shimmer_device_006"
        connectionManager.startManagement()
        
        // when
        connectionManager.startHealthMonitoring(deviceId)
        
        // then - should not throw exception
        // Health monitoring starts in background
    }
    
    @Test
    fun `should get overall connection statistics`() {
        // when
        val stats = connectionManager.getOverallStatistics()
        
        // then
        assertNotNull(stats)
        assertTrue(stats.containsKey("totalDevices"))
        assertTrue(stats.containsKey("healthyDevices"))
        assertTrue(stats.containsKey("unhealthyDevices"))
        assertTrue(stats.containsKey("totalConnectionAttempts"))
        assertTrue(stats.containsKey("successfulConnections"))
        assertTrue(stats.containsKey("failedConnections"))
        assertTrue(stats.containsKey("successRate"))
        assertTrue(stats.containsKey("isManaging"))
    }
    
    @Test
    fun `should reset device statistics correctly`() = runTest {
        // given
        val deviceId = "shimmer_device_007"
        val mockConnectionFunction: suspend () -> Boolean = { true }
        connectionManager.connectWithRetry(deviceId, mockConnectionFunction)
        
        // when
        connectionManager.resetDeviceStatistics(deviceId)
        
        // then
        verify(mockLogger).info(any())
        val stats = connectionManager.getConnectionStatistics(deviceId)
        assertEquals(0, stats["totalAttempts"])
    }
    
    @Test
    fun `should reset all statistics correctly`() {
        // when
        connectionManager.resetAllStatistics()
        
        // then
        verify(mockLogger).info(any())
        val stats = connectionManager.getOverallStatistics()
        assertEquals(0, stats["totalDevices"])
        assertEquals(0L, stats["totalConnectionAttempts"])
    }
    
    @Test
    fun `should cleanup resources properly`() {
        // given
        connectionManager.startManagement()
        
        // when
        connectionManager.cleanup()
        
        // then
        verify(mockLogger).info(any())
        val stats = connectionManager.getOverallStatistics()
        assertFalse(stats["isManaging"] as Boolean)
    }
}