package com.multisensor.recording.recording

import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*
import com.multisensor.recording.util.Logger

/**
 * comprehensive test suite for pc communication handler
 * tests socket communication, command processing, and error handling
 */
class PCCommunicationHandlerTest {
    
    @Mock
    private lateinit var mockLogger: Logger
    
    @Mock  
    private lateinit var mockConnectionManager: ConnectionManager
    
    @Mock
    private lateinit var mockSessionManager: SessionManager
    
    private lateinit var pcCommunicationHandler: PCCommunicationHandler
    
    @Before
    fun setup() {
        MockitoAnnotations.initMocks(this)
        pcCommunicationHandler = PCCommunicationHandler(mockLogger, mockConnectionManager, mockSessionManager)
    }
    
    @Test
    fun `should establish connection to pc successfully`() = runTest {
        // given
        val serverAddress = "192.168.1.100"
        val serverPort = 8080
        whenever(mockConnectionManager.connectWithRetry(any(), any())).thenReturn(true)
        
        // when
        val result = pcCommunicationHandler.establishConnection(serverAddress, serverPort)
        
        // then
        assertTrue(result)
        verify(mockConnectionManager).connectWithRetry(any(), any())
        verify(mockLogger).logI(any())
    }
    
    @Test
    fun `should handle connection failure gracefully`() = runTest {
        // given
        val serverAddress = "192.168.1.100" 
        val serverPort = 8080
        whenever(mockConnectionManager.connectWithRetry(any(), any())).thenReturn(false)
        
        // when
        val result = pcCommunicationHandler.establishConnection(serverAddress, serverPort)
        
        // then
        assertFalse(result)
        verify(mockLogger).logE(any())
    }
    
    @Test
    fun `should send device status updates to pc`() = runTest {
        // given
        val deviceStatus = DeviceStatus(
            batteryLevel = 85,
            isRecording = true,
            thermalConnected = true,
            shimmerConnected = false
        )
        whenever(mockConnectionManager.getConnectionStatus()).thenReturn(ConnectionManager.ConnectionStatus.CONNECTED)
        
        // when
        pcCommunicationHandler.sendStatusUpdate(deviceStatus)
        
        // then
        verify(mockConnectionManager).sendData(any())
    }
    
    @Test
    fun `should process start recording command from pc`() = runTest {
        // given
        val startCommand = """{"command": "start_recording", "sessionId": "test_123"}"""
        var commandReceived = false
        
        pcCommunicationHandler.setMessageHandler { command ->
            if (command.contains("start_recording")) {
                commandReceived = true
            }
        }
        
        // when
        pcCommunicationHandler.handleIncomingData(startCommand)
        
        // then
        assertTrue(commandReceived)
        verify(mockLogger).logI(any())
    }
    
    @Test
    fun `should handle malformed json commands gracefully`() = runTest {
        // given
        val malformedCommand = """{"command": "invalid_json"...}"""
        
        // when
        pcCommunicationHandler.handleIncomingData(malformedCommand)
        
        // then
        verify(mockLogger).logE(any())
    }
    
    @Test  
    fun `should disconnect from pc cleanly`() = runTest {
        // given
        whenever(mockConnectionManager.getConnectionStatus()).thenReturn(ConnectionManager.ConnectionStatus.CONNECTED)
        
        // when
        pcCommunicationHandler.closeConnection()
        
        // then
        verify(mockConnectionManager).disconnect()
        verify(mockLogger).logI(any())
    }
    
    @Test
    fun `should stream preview data to pc when connected`() = runTest {
        // given
        val previewData = byteArrayOf(0x12, 0x34, 0x56, 0x78)
        whenever(mockConnectionManager.getConnectionStatus()).thenReturn(ConnectionManager.ConnectionStatus.CONNECTED)
        
        // when
        pcCommunicationHandler.sendPreviewData(previewData)
        
        // then
        verify(mockConnectionManager).sendData(previewData)
    }
    
    private data class DeviceStatus(
        val batteryLevel: Int,
        val isRecording: Boolean,
        val thermalConnected: Boolean,
        val shimmerConnected: Boolean
    )
}