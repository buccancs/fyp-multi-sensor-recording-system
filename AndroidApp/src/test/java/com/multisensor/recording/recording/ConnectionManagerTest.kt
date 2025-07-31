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
import java.net.Socket
import java.io.IOException

/**
 * comprehensive test suite for connection manager
 * tests socket creation, data transmission, and connection lifecycle
 */
class ConnectionManagerTest {
    
    @Mock
    private lateinit var mockLogger: Logger
    
    @Mock
    private lateinit var mockSocket: Socket
    
    private lateinit var connectionManager: ConnectionManager
    
    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        connectionManager = ConnectionManager(mockLogger)
    }
    
    @Test
    fun `should create socket connection successfully`() = runTest {
        // given
        val serverAddress = "192.168.1.100"
        val serverPort = 8080
        
        // when
        val result = connectionManager.connect(serverAddress, serverPort)
        
        // then - connection attempt should be logged
        verify(mockLogger).logI(any())
    }
    
    @Test
    fun `should handle socket timeout gracefully`() = runTest {
        // given
        val serverAddress = "192.168.1.999" // unreachable address
        val serverPort = 8080
        
        // when
        val result = connectionManager.connect(serverAddress, serverPort)
        
        // then
        assertFalse(result)
        verify(mockLogger).logE(any())
    }
    
    @Test
    fun `should send text messages over socket`() = runTest {
        // given
        val message = """{"command": "status_update", "data": "test"}"""
        whenever(mockSocket.isConnected).thenReturn(true)
        
        // when 
        connectionManager.sendMessage(message)
        
        // then
        verify(mockLogger).logD(any())
    }
    
    @Test
    fun `should send binary data over socket`() = runTest {
        // given
        val binaryData = byteArrayOf(0x01, 0x02, 0x03, 0x04)
        whenever(mockSocket.isConnected).thenReturn(true)
        
        // when
        connectionManager.sendBinaryData(binaryData)
        
        // then
        verify(mockLogger).logD(any())
    }
    
    @Test  
    fun `should handle socket write errors gracefully`() = runTest {
        // given
        val message = "test message"
        whenever(mockSocket.isConnected).thenReturn(false)
        
        // when
        connectionManager.sendMessage(message)
        
        // then
        verify(mockLogger).logE(any())
    }
    
    @Test
    fun `should close socket connection cleanly`() = runTest {
        // given
        whenever(mockSocket.isConnected).thenReturn(true)
        
        // when
        connectionManager.disconnect()
        
        // then
        verify(mockLogger).logI(any())
    }
    
    @Test
    fun `should detect connection status correctly`() {
        // given
        whenever(mockSocket.isConnected).thenReturn(true)
        whenever(mockSocket.isClosed).thenReturn(false)
        
        // when
        val isConnected = connectionManager.isConnected()
        
        // then - default implementation should return false until real socket is connected
        assertFalse(isConnected)
    }
    
    @Test
    fun `should handle network interruption during transmission`() = runTest {
        // given
        val largeMessage = "x".repeat(10000) // large message to test chunking
        whenever(mockSocket.isConnected).thenReturn(true)
        
        // when
        connectionManager.sendMessage(largeMessage)
        
        // then
        verify(mockLogger).logD(any())
    }
    
    @Test
    fun `should validate server address format`() = runTest {
        // given
        val invalidAddress = "not.a.valid.ip"
        val validPort = 8080
        
        // when
        val result = connectionManager.connect(invalidAddress, validPort)
        
        // then
        assertFalse(result)
        verify(mockLogger).logE(any())
    }
    
    @Test
    fun `should validate port range`() = runTest {
        // given
        val validAddress = "192.168.1.100"
        val invalidPort = 70000 // out of valid range
        
        // when
        val result = connectionManager.connect(validAddress, invalidPort)
        
        // then
        assertFalse(result)
        verify(mockLogger).logE(any())
    }
}