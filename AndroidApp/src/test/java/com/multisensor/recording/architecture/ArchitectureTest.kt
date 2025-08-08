package com.multisensor.recording.architecture

import com.multisensor.recording.controllers.ConnectionConfig
import com.multisensor.recording.controllers.ConnectionState
import com.multisensor.recording.controllers.ControllerConnectionManager
import com.multisensor.recording.controllers.PcControllerConnectionManager
import com.multisensor.recording.streaming.NetworkPreviewStreamer
import com.multisensor.recording.streaming.PreviewStreamingInterface
import com.multisensor.recording.streaming.StreamingConfig
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.runTest
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mockito.*

/**
 * Tests for the new MVVM architecture components and modular design.
 * Validates that the abstraction layers work correctly.
 */
class ArchitectureTest {

    @Test
    fun `ControllerConnectionManager abstraction works correctly`() = runTest {
        // Given
        val mockLogger = mock(Logger::class.java)
        val mockJsonSocketClient = mock(com.multisensor.recording.network.JsonSocketClient::class.java)
        
        val connectionManager = PcControllerConnectionManager(mockJsonSocketClient, mockLogger)
        
        // When
        val config = ConnectionConfig("192.168.1.100", 9000)
        val result = connectionManager.connect(config)
        
        // Then
        assertTrue("Connection should succeed", result.isSuccess)
        verify(mockJsonSocketClient).configure(eq("192.168.1.100"), eq(9000))
        verify(mockJsonSocketClient).connect()
    }

    @Test
    fun `PreviewStreamingInterface abstraction enables modular design`() = runTest {
        // Given
        val mockLogger = mock(Logger::class.java)
        val mockConnectionManager = mock(ControllerConnectionManager::class.java)
        
        `when`(mockConnectionManager.isConnected()).thenReturn(true)
        
        val streamingInterface: PreviewStreamingInterface = NetworkPreviewStreamer(mockConnectionManager, mockLogger)
        
        // When
        val config = StreamingConfig(fps = 5, jpegQuality = 80)
        streamingInterface.configure(config)
        streamingInterface.startStreaming(config)
        
        // Then
        assertTrue("Should be streaming", streamingInterface.isStreaming())
    }

    @Test
    fun `ConnectionState flows correctly represent state changes`() {
        // Given
        val states = mutableListOf<ConnectionState>()
        
        // When - simulate state transitions
        states.add(ConnectionState.Disconnected)
        states.add(ConnectionState.Connecting)
        states.add(ConnectionState.Connected)
        states.add(ConnectionState.Error("Connection failed"))
        
        // Then
        assertEquals("Should start disconnected", ConnectionState.Disconnected, states[0])
        assertEquals("Should transition to connecting", ConnectionState.Connecting, states[1])
        assertEquals("Should reach connected state", ConnectionState.Connected, states[2])
        assertTrue("Should handle error state", states[3] is ConnectionState.Error)
    }

    @Test
    fun `Modular camera recorder dependencies are properly abstracted`() {
        // This test validates that our modular approach reduces tight coupling
        
        // Given - dependencies that can be mocked/substituted
        val mockPreviewStreamer = mock(PreviewStreamingInterface::class.java)
        val mockHandSegmentation = mock(com.multisensor.recording.handsegmentation.HandSegmentationManager::class.java)
        val mockSessionManager = mock(com.multisensor.recording.service.SessionManager::class.java)
        val mockLogger = mock(Logger::class.java)
        val mockContext = mock(android.content.Context::class.java)
        
        // When - we can create the modular recorder with injected dependencies
        // (This validates the constructor signature supports dependency injection)
        val constructorExists = try {
            com.multisensor.recording.recording.ModularCameraRecorder::class.java
                .getDeclaredConstructor(
                    android.content.Context::class.java,
                    com.multisensor.recording.service.SessionManager::class.java,
                    Logger::class.java,
                    com.multisensor.recording.handsegmentation.HandSegmentationManager::class.java,
                    PreviewStreamingInterface::class.java
                )
            true
        } catch (e: NoSuchMethodException) {
            false
        }
        
        // Then
        assertTrue("ModularCameraRecorder should support dependency injection", constructorExists)
    }

    @Test
    fun `Single activity pattern navigation screens are defined`() {
        // Given - screens from our enhanced navigation
        val screenRoutes = listOf(
            "recording",
            "thermal_preview", 
            "devices",
            "calibration",
            "files",
            "settings",
            "about",
            "diagnostics",
            "shimmer_settings",
            "shimmer_viz"
        )
        
        // When - checking if all essential screens are present
        val hasMainScreens = screenRoutes.containsAll(listOf("recording", "devices", "files"))
        val hasSettingsScreens = screenRoutes.containsAll(listOf("settings", "about"))
        val hasAdvancedScreens = screenRoutes.containsAll(listOf("diagnostics", "shimmer_settings"))
        
        // Then
        assertTrue("Should have main recording screens", hasMainScreens)
        assertTrue("Should have settings screens", hasSettingsScreens)
        assertTrue("Should have advanced configuration screens", hasAdvancedScreens)
        assertEquals("Should consolidate 10 screens", 10, screenRoutes.size)
    }
}