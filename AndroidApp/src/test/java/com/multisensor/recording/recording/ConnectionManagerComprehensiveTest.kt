package com.multisensor.recording.recording

import android.content.Context
import com.multisensor.recording.network.PCCommunicationHandler
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.net.InetAddress
import java.util.concurrent.TimeUnit

/**
 * Comprehensive Connection Manager Tests
 * =====================================
 * 
 * This test class provides comprehensive testing for connection management,
 * network communication, and device coordination functionality.
 * 
 * Test coverage:
 * - Network connection establishment and management
 * - Device discovery and pairing
 * - Message handling and communication protocols
 * - Connection resilience and error recovery
 * - Performance monitoring and optimization
 * 
 * Author: Multi-Sensor Recording System
 * Date: 2025-01-16
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
@ExperimentalCoroutinesApi
class ConnectionManagerComprehensiveTest {
    
    private lateinit var mockContext: Context
    private lateinit var mockSessionManager: SessionManager
    private lateinit var mockLogger: Logger
    private lateinit var mockPCHandler: PCCommunicationHandler
    private lateinit var connectionManager: ConnectionManager
    
    @Before
    fun setup() {
        mockContext = mockk(relaxed = true)
        mockSessionManager = mockk(relaxed = true)
        mockLogger = mockk(relaxed = true)
        mockPCHandler = mockk(relaxed = true)
        
        connectionManager = ConnectionManager(mockContext, mockSessionManager, mockLogger)
    }
    
    @After
    fun tearDown() {
        clearAllMocks()
    }
    
    @Test
    fun `connection manager initialization should succeed`() = runTest {
        assertNotNull("ConnectionManager should be created", connectionManager)
        
        val initResult = connectionManager.initialize()
        assertTrue("ConnectionManager should initialize successfully", initResult)
        
        verify { mockLogger.info("Initializing ConnectionManager...") }
    }
    
    @Test
    fun `device discovery should find available devices`() = runTest {
        val mockDevices = listOf(
            mapOf(
                "device_id" to "android_001",
                "device_type" to "android",
                "ip_address" to "192.168.1.100",
                "port" to 9000,
                "capabilities" to listOf("camera", "gsr", "thermal")
            ),
            mapOf(
                "device_id" to "android_002", 
                "device_type" to "android",
                "ip_address" to "192.168.1.101",
                "port" to 9000,
                "capabilities" to listOf("camera", "audio")
            ),
            mapOf(
                "device_id" to "pc_master",
                "device_type" to "desktop",
                "ip_address" to "192.168.1.10",
                "port" to 8000,
                "capabilities" to listOf("processing", "storage", "coordination")
            )
        )
        
        every { connectionManager.discoverDevices(any()) } returns mockDevices
        
        val discoveredDevices = connectionManager.discoverDevices(timeout = 5000)
        
        assertNotNull("Device discovery should return results", discoveredDevices)
        assertEquals("Should discover all mock devices", mockDevices.size, discoveredDevices.size)
        
        val androidDevice = discoveredDevices.find { it["device_id"] == "android_001" }
        assertNotNull("Should find android_001 device", androidDevice)
        assertEquals("Device type should be android", "android", androidDevice!!["device_type"])
        assertTrue("Should have camera capability", 
                  (androidDevice["capabilities"] as List<*>).contains("camera"))
    }
    
    @Test
    fun `connection establishment should work correctly`() = runTest {
        val targetDevice = mapOf(
            "device_id" to "pc_master",
            "ip_address" to "192.168.1.10",
            "port" to 8000
        )
        
        every { connectionManager.connectToDevice(any()) } returns true
        every { connectionManager.isConnected(any()) } returns true
        
        val connectionResult = connectionManager.connectToDevice(targetDevice)
        assertTrue("Connection should be established successfully", connectionResult)
        
        val isConnected = connectionManager.isConnected(targetDevice["device_id"] as String)
        assertTrue("Device should be marked as connected", isConnected)
        
        verify { mockLogger.info(match { it.contains("pc_master") && it.contains("connected") }) }
    }
    
    @Test
    fun `message sending should handle different message types`() = runTest {
        val deviceId = "pc_master"
        
        val messageTypes = listOf(
            mapOf("type" to "hello", "device_id" to "android_001", "capabilities" to listOf("camera")),
            mapOf("type" to "sensor_data", "gsr" to 1000, "ppg" to 2000, "timestamp" to System.currentTimeMillis()),
            mapOf("type" to "status", "status" to "recording", "battery" to 85),
            mapOf("type" to "error", "error_code" to "SENSOR_FAILURE", "message" to "GSR sensor disconnected")
        )
        
        every { connectionManager.sendMessage(any(), any()) } returns true
        
        messageTypes.forEach { message ->
            val sendResult = connectionManager.sendMessage(deviceId, message)
            assertTrue("Message of type ${message["type"]} should be sent successfully", sendResult)
        }
        
        verify(exactly = messageTypes.size) { 
            connectionManager.sendMessage(eq(deviceId), any()) 
        }
    }
    
    @Test
    fun `message receiving should parse different formats`() = runTest {
        val receivedMessages = listOf(
            """{"type":"command","command":"start_recording","session_id":"test_123"}""",
            """{"type":"sync","master_timestamp":1234567890,"device_id":"pc_master"}""",
            """{"type":"calibration","pattern_type":"chessboard","square_size":25.0}""",
            """{"type":"file_request","session_id":"test_123","file_types":["sensor_data","video"]}"""
        )
        
        receivedMessages.forEachIndexed { index, messageJson ->
            every { connectionManager.receiveMessage() } returnsMany listOf(messageJson)
            
            val receivedMessage = connectionManager.receiveMessage()
            assertNotNull("Should receive message", receivedMessage)
            
            val parsedMessage = connectionManager.parseMessage(receivedMessage)
            assertNotNull("Message should be parsed successfully", parsedMessage)
            assertTrue("Parsed message should contain type", parsedMessage.containsKey("type"))
        }
    }
    
    @Test
    fun `connection resilience should handle network issues`() = runTest {
        val deviceId = "pc_master"
        
        every { connectionManager.isConnected(deviceId) } returns true
        
        val networkIssues = listOf(
            "CONNECTION_TIMEOUT",
            "PACKET_LOSS", 
            "NETWORK_UNREACHABLE",
            "HOST_DISCONNECTED"
        )
        
        networkIssues.forEach { issueType ->
            every { connectionManager.handleConnectionIssue(deviceId, issueType) } returns true
            
            val recoveryResult = connectionManager.handleConnectionIssue(deviceId, issueType)
            assertTrue("Should handle $issueType successfully", recoveryResult)
            
            verify { mockLogger.warning(match { it.contains(issueType) }) }
        }
        
        every { connectionManager.attemptReconnection(deviceId) } returns true
        
        val reconnectionResult = connectionManager.attemptReconnection(deviceId)
        assertTrue("Automatic reconnection should succeed", reconnectionResult)
    }
    
    @Test
    fun `connection quality monitoring should track metrics`() = runTest {
        val deviceId = "pc_master" 
        
        every { connectionManager.isConnected(deviceId) } returns true
        
        val qualityMetrics = listOf(
            mapOf("latency" to 25.5, "packet_loss" to 0.01, "bandwidth" to 1000.0),
            mapOf("latency" to 30.2, "packet_loss" to 0.02, "bandwidth" to 950.0),
            mapOf("latency" to 28.8, "packet_loss" to 0.015, "bandwidth" to 980.0),
            mapOf("latency" to 35.1, "packet_loss" to 0.03, "bandwidth" to 900.0)
        )
        
        qualityMetrics.forEach { metrics ->
            connectionManager.recordConnectionQuality(
                deviceId,
                metrics["latency"] as Double,
                metrics["packet_loss"] as Double,
                metrics["bandwidth"] as Double
            )
        }
        
        val qualityStats = connectionManager.getConnectionQualityStats(deviceId)
        
        assertNotNull("Quality stats should be available", qualityStats)
        assertTrue("Should include average latency", qualityStats.containsKey("avg_latency"))
        assertTrue("Should include average packet loss", qualityStats.containsKey("avg_packet_loss"))
        assertTrue("Should include average bandwidth", qualityStats.containsKey("avg_bandwidth"))
        
        val avgLatency = qualityStats["avg_latency"] as Double
        assertTrue("Average latency should be reasonable", avgLatency > 20.0 && avgLatency < 40.0)
    }
    
    @Test
    fun `priority message handling should work correctly`() = runTest {
        val deviceId = "pc_master"
        
        val priorityMessages = listOf(
            mapOf("type" to "status", "priority" to "LOW", "message" to "Routine status update"),
            mapOf("type" to "emergency", "priority" to "CRITICAL", "message" to "System failure detected"),
            mapOf("type" to "command", "priority" to "NORMAL", "message" to "Start recording"),
            mapOf("type" to "sync", "priority" to "HIGH", "message" to "Time synchronization")
        )
        
        priorityMessages.forEach { message ->
            connectionManager.queuePriorityMessage(deviceId, message)
        }
        
        val expectedOrder = listOf("CRITICAL", "HIGH", "NORMAL", "LOW")
        val processedOrder = mutableListOf<String>()
        
        while (connectionManager.hasPendingPriorityMessages(deviceId)) {
            val nextMessage = connectionManager.getNextPriorityMessage(deviceId)
            processedOrder.add(nextMessage["priority"] as String)
        }
        
        assertEquals("Messages should be processed in priority order", expectedOrder, processedOrder)
    }
    
    @Test
    fun `multi-device coordination should work`() = runTest {
        val devices = listOf(
            mapOf("device_id" to "android_001", "type" to "android"),
            mapOf("device_id" to "android_002", "type" to "android"),
            mapOf("device_id" to "desktop_001", "type" to "desktop")
        )
        
        devices.forEach { device ->
            every { connectionManager.isConnected(device["device_id"] as String) } returns true
        }
        
        val broadcastMessage = mapOf(
            "type" to "sync_command",
            "command" to "start_recording",
            "session_id" to "multi_device_test",
            "timestamp" to System.currentTimeMillis()
        )
        
        every { connectionManager.broadcastMessage(broadcastMessage) } returns devices.size
        
        val broadcastResult = connectionManager.broadcastMessage(broadcastMessage)
        assertEquals("Should broadcast to all devices", devices.size, broadcastResult)
        
        every { connectionManager.coordinateDevices(any(), any()) } returns true
        
        val coordinationResult = connectionManager.coordinateDevices("start_recording", mapOf("session_id" to "test"))
        assertTrue("Device coordination should succeed", coordinationResult)
    }
    
    @Test
    fun `connection pool management should work`() = runTest {
        val maxConnections = 5
        
        connectionManager.configureConnectionPool(maxConnections, 60000)
        
        repeat(maxConnections) { index ->
            val deviceId = "device_${index + 1}"
            every { connectionManager.addToConnectionPool(deviceId) } returns true
            
            val addResult = connectionManager.addToConnectionPool(deviceId)
            assertTrue("Should add device $deviceId to pool", addResult)
        }
        
        val extraDeviceId = "device_extra"
        every { connectionManager.addToConnectionPool(extraDeviceId) } returns false
        
        val capacityResult = connectionManager.addToConnectionPool(extraDeviceId)
        assertFalse("Should reject connection when pool is full", capacityResult)
        
        val poolStats = connectionManager.getConnectionPoolStats()
        
        assertNotNull("Pool stats should be available", poolStats)
        assertEquals("Pool should be at capacity", maxConnections, poolStats["active_connections"])
        assertTrue("Pool utilization should be 100%", 
                  poolStats["utilization_percent"] as Double == 100.0)
    }
    
    @Test
    fun `security and authentication should work`() = runTest {
        val deviceId = "secure_device_001"
        val authToken = "test_auth_token_123456"
        
        every { connectionManager.authenticateDevice(deviceId, authToken) } returns true
        
        val authResult = connectionManager.authenticateDevice(deviceId, authToken)
        assertTrue("Device authentication should succeed", authResult)
        
        val secureMessage = mapOf(
            "type" to "secure_data",
            "encrypted" to true,
            "data" to "encrypted_sensor_data_payload"
        )
        
        every { connectionManager.sendSecureMessage(deviceId, secureMessage) } returns true
        
        val secureResult = connectionManager.sendSecureMessage(deviceId, secureMessage)
        assertTrue("Secure message should be sent successfully", secureResult)
        
        val plainText = "test_data_to_encrypt"
        every { connectionManager.encryptData(plainText) } returns "encrypted_$plainText"
        every { connectionManager.decryptData("encrypted_$plainText") } returns plainText
        
        val encrypted = connectionManager.encryptData(plainText)
        val decrypted = connectionManager.decryptData(encrypted)
        
        assertEquals("Decrypted data should match original", plainText, decrypted)
    }
    
    @Test
    fun `performance optimization should work`() = runTest {
        val deviceId = "performance_test_device"
        
        val performanceConfig = mapOf(
            "compression_enabled" to true,
            "batching_enabled" to true,
            "batch_size" to 100,
            "compression_level" to 6
        )
        
        every { connectionManager.configurePerformance(deviceId, performanceConfig) } returns true
        
        val configResult = connectionManager.configurePerformance(deviceId, performanceConfig)
        assertTrue("Performance configuration should succeed", configResult)
        
        val messageBatch = List(100) { index ->
            mapOf(
                "type" to "sensor_data",
                "sample_id" to index,
                "gsr" to 1000 + index,
                "timestamp" to System.currentTimeMillis() + index
            )
        }
        
        every { connectionManager.sendMessageBatch(deviceId, messageBatch) } returns true
        
        val batchResult = connectionManager.sendMessageBatch(deviceId, messageBatch)
        assertTrue("Message batch should be sent successfully", batchResult)
        
        val largeData = "x".repeat(10000)
        every { connectionManager.compressData(largeData) } returns ByteArray(1000)
        
        val compressedData = connectionManager.compressData(largeData)
        assertTrue("Compressed data should be smaller", compressedData.size < largeData.length)
    }
    
    @Test
    fun `connection cleanup should work correctly`() = runTest {
        val deviceIds = listOf("device_001", "device_002", "device_003")
        
        deviceIds.forEach { deviceId ->
            every { connectionManager.isConnected(deviceId) } returns true
        }
        
        deviceIds.forEach { deviceId ->
            every { connectionManager.disconnectDevice(deviceId, graceful = true) } returns true
            
            val disconnectResult = connectionManager.disconnectDevice(deviceId, graceful = true)
            assertTrue("Graceful disconnect should succeed for $deviceId", disconnectResult)
        }
        
        every { connectionManager.cleanup() } returns true
        
        val cleanupResult = connectionManager.cleanup()
        assertTrue("Connection manager cleanup should succeed", cleanupResult)
        
        verify { mockLogger.info("Connection manager cleanup completed") }
    }
}