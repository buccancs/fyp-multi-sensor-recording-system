package com.multisensor.recording.network

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import java.net.Socket
import java.io.OutputStream

/**
 * Comprehensive tests for NetworkManager using modern test architecture
 */
class NetworkManagerTest : BaseUnitTest() {

    private lateinit var networkManager: NetworkManager
    private val mockSocket: Socket = mockk(relaxed = true)
    private val mockOutputStream: OutputStream = mockk(relaxed = true)

    @Before
    override fun setUp() {
        super.setUp()
        networkManager = NetworkManager()
        every { mockSocket.isConnected } returns true
        every { mockSocket.outputStream } returns mockOutputStream
    }

    @Test
    fun `should initialize with disconnected state`() {
        // When & Then
        assertThat(networkManager.isConnected()).isFalse()
        assertThat(networkManager.getConnectionStatus()).isEqualTo(NetworkManager.ConnectionStatus.DISCONNECTED)
    }

    @Test
    fun `should connect to PC successfully`() = runTest {
        // Given
        val ipAddress = "192.168.1.100"
        val port = 8080
        
        // When
        val result = networkManager.connectToPC(ipAddress, port)
        
        // Then
        assertThat(result).isTrue()
        assertThat(networkManager.isConnected()).isTrue()
        assertThat(networkManager.getConnectionStatus()).isEqualTo(NetworkManager.ConnectionStatus.CONNECTED)
    }

    @Test
    fun `should fail to connect with invalid IP`() = runTest {
        // Given
        val invalidIP = "invalid.ip.address"
        val port = 8080
        
        // When
        val result = networkManager.connectToPC(invalidIP, port)
        
        // Then
        assertThat(result).isFalse()
        assertThat(networkManager.isConnected()).isFalse()
    }

    @Test
    fun `should disconnect successfully`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        
        // When
        networkManager.disconnect()
        
        // Then
        assertThat(networkManager.isConnected()).isFalse()
        assertThat(networkManager.getConnectionStatus()).isEqualTo(NetworkManager.ConnectionStatus.DISCONNECTED)
    }

    @Test
    fun `should send data when connected`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        val testData = "test data"
        
        // When
        val result = networkManager.sendData(testData.toByteArray())
        
        // Then
        assertThat(result).isTrue()
    }

    @Test
    fun `should fail to send data when disconnected`() = runTest {
        // Given
        val testData = "test data"
        
        // When
        val result = networkManager.sendData(testData.toByteArray())
        
        // Then
        assertThat(result).isFalse()
    }

    @Test
    fun `should handle connection timeout`() = runTest {
        // Given
        val timeoutMs = 1000L
        
        // When
        val result = networkManager.connectWithTimeout("192.168.1.100", 8080, timeoutMs)
        
        // Then
        assertThat(result).isTrue()
    }

    @Test
    fun `should detect network quality changes`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        
        // When
        val quality = networkManager.measureNetworkQuality()
        
        // Then
        assertThat(quality).isNotNull()
        assertThat(quality.latency).isAtLeast(0L)
        assertThat(quality.bandwidth).isAtLeast(0.0)
    }

    @Test
    fun `should retry connection on failure`() = runTest {
        // Given
        val maxRetries = 3
        
        // When
        val result = networkManager.connectWithRetry("192.168.1.100", 8080, maxRetries)
        
        // Then
        assertThat(result).isTrue()
    }

    @Test
    fun `should handle large data transfer`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        val largeData = ByteArray(1024 * 1024) // 1MB
        
        // When
        val result = networkManager.sendLargeData(largeData)
        
        // Then
        assertThat(result).isTrue()
    }

    @Test
    fun `should maintain connection heartbeat`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        
        // When
        networkManager.startHeartbeat()
        val isAlive = networkManager.isConnectionAlive()
        
        // Then
        assertThat(isAlive).isTrue()
    }

    @Test
    fun `should get connection statistics`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        networkManager.sendData("test".toByteArray())
        
        // When
        val stats = networkManager.getConnectionStatistics()
        
        // Then
        assertThat(stats.bytesSent).isGreaterThan(0L)
        assertThat(stats.connectionTime).isGreaterThan(0L)
        assertThat(stats.packetsTransmitted).isGreaterThan(0)
    }

    @Test
    fun `should handle network error recovery`() = runTest {
        // Given
        networkManager.connectToPC("192.168.1.100", 8080)
        
        // When
        networkManager.simulateNetworkError()
        val recovered = networkManager.attemptRecovery()
        
        // Then
        assertThat(recovered).isTrue()
        assertThat(networkManager.getConnectionStatus()).isEqualTo(NetworkManager.ConnectionStatus.CONNECTED)
    }

    @Test
    fun `should validate network configuration`() = runTest {
        // When
        val validConfig = networkManager.validateConfiguration("192.168.1.100", 8080)
        val invalidConfig = networkManager.validateConfiguration("", -1)
        
        // Then
        assertThat(validConfig).isTrue()
        assertThat(invalidConfig).isFalse()
    }
}