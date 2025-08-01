package com.multisensor.recording.controllers

import android.content.Context
import android.view.View
import android.widget.TextView
import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseRobolectricTest
import io.mockk.every
import io.mockk.impl.annotations.InjectMockKs
import io.mockk.impl.annotations.RelaxedMockK
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test

/**
 * Comprehensive unit tests for NetworkController streaming scenarios
 * 
 * Test Categories:
 * - Streaming indicator management
 * - Network connectivity monitoring
 * - Streaming quality metrics and monitoring
 * - Network error handling and recovery
 * - Actual streaming logic (start and stop)
 * - UI callback integration
 * - Emergency scenarios and error conditions
 */
@OptIn(ExperimentalCoroutinesApi::class)
class NetworkControllerTest : BaseRobolectricTest() {

    @RelaxedMockK
    private lateinit var mockContext: Context
    
    @RelaxedMockK 
    private lateinit var mockCallback: NetworkController.NetworkCallback
    
    @RelaxedMockK
    private lateinit var mockStreamingIndicator: View
    
    @RelaxedMockK
    private lateinit var mockStreamingLabel: View
    
    @RelaxedMockK
    private lateinit var mockStreamingDebugOverlay: TextView

    @InjectMockKs
    private lateinit var networkController: NetworkController

    @Before
    override fun setUp() {
        super.setUp()
        
        // Setup mock callback responses
        every { mockCallback.getStreamingIndicator() } returns mockStreamingIndicator
        every { mockCallback.getStreamingLabel() } returns mockStreamingLabel
        every { mockCallback.getStreamingDebugOverlay() } returns mockStreamingDebugOverlay
        
        // Set callback for the controller
        networkController.setCallback(mockCallback)
    }

    // ========== Streaming Indicator Management Tests ==========

    @Test
    fun `should show streaming indicator correctly`() {
        // When
        networkController.showStreamingIndicator(mockContext)

        // Then
        assertThat(networkController.isStreamingActive()).isTrue()
        verify { mockCallback.onStreamingStarted() }
        verify { mockStreamingIndicator.setBackgroundColor(any()) }
        verify { mockStreamingLabel.visibility = View.VISIBLE }
    }

    @Test
    fun `should hide streaming indicator correctly`() {
        // Given - start streaming first
        networkController.showStreamingIndicator(mockContext)
        
        // When
        networkController.hideStreamingIndicator(mockContext)

        // Then
        assertThat(networkController.isStreamingActive()).isFalse()
        verify { mockCallback.onStreamingStopped() }
        verify { mockStreamingIndicator.setBackgroundColor(any()) }
        verify { mockStreamingLabel.visibility = View.GONE }
    }

    @Test
    fun `should update streaming debug overlay with correct text`() {
        // Given
        networkController.updateStreamingMetrics(30, "1.5 MB/s")
        
        // When
        networkController.updateStreamingDebugOverlay()

        // Then
        verify { mockStreamingDebugOverlay.text = any() }
        verify { mockStreamingDebugOverlay.visibility = any() }
    }

    @Test
    fun `should update streaming UI based on recording state`() {
        // When recording is active
        networkController.updateStreamingUI(mockContext, isRecording = true)

        // Then
        verify { mockCallback.onStreamingStarted() }
        verify { mockStreamingLabel.visibility = View.VISIBLE }

        // When recording is stopped
        networkController.updateStreamingUI(mockContext, isRecording = false)

        // Then
        verify { mockCallback.onStreamingStopped() }
        verify { mockStreamingDebugOverlay.visibility = View.GONE }
    }

    // ========== Streaming Metrics Tests ==========

    @Test
    fun `should update streaming metrics correctly`() {
        // Given
        val frameRate = 60
        val dataSize = "2.1 MB/s"

        // When
        networkController.updateStreamingMetrics(frameRate, dataSize)

        // Then
        val (currentFrameRate, currentDataSize) = networkController.getStreamingMetrics()
        assertThat(currentFrameRate).isEqualTo(frameRate)
        assertThat(currentDataSize).isEqualTo(dataSize)
    }

    @Test
    fun `should update streaming indicator with dynamic metrics`() {
        // Given
        val frameRate = 45
        val dataSize = "1.8 MB/s"

        // When
        networkController.updateStreamingIndicator(mockContext, isStreaming = true, frameRate, dataSize)

        // Then
        verify { mockStreamingDebugOverlay.text = "Streaming: ${frameRate}fps ($dataSize)" }
        verify { mockStreamingDebugOverlay.visibility = View.VISIBLE }
        verify { mockStreamingLabel.visibility = View.VISIBLE }
    }

    @Test
    fun `should handle streaming indicator with zero frame rate`() {
        // When
        networkController.updateStreamingIndicator(mockContext, isStreaming = true, frameRate = 0)

        // Then
        verify { mockStreamingDebugOverlay.visibility = View.GONE }
        verify { mockStreamingLabel.visibility = View.GONE }
    }

    // ========== Network Connectivity Monitoring Tests ==========

    @Test
    fun `should handle network connectivity changes`() {
        // Given - streaming is active
        networkController.showStreamingIndicator(mockContext)

        // When network disconnects
        networkController.handleNetworkConnectivityChange(connected = false)

        // Then
        verify { mockCallback.onNetworkStatusChanged(false) }
        verify { mockCallback.onStreamingError("Network connection lost during streaming") }
    }

    @Test
    fun `should handle network reconnection gracefully`() {
        // When network reconnects
        networkController.handleNetworkConnectivityChange(connected = true)

        // Then
        verify { mockCallback.onNetworkStatusChanged(true) }
    }

    @Test
    fun `should not show streaming error when network disconnects while not streaming`() {
        // Given - not streaming
        assertThat(networkController.isStreamingActive()).isFalse()

        // When network disconnects
        networkController.handleNetworkConnectivityChange(connected = false)

        // Then
        verify { mockCallback.onNetworkStatusChanged(false) }
        verify(exactly = 0) { mockCallback.onStreamingError(any()) }
    }

    // ========== Streaming Quality Management Tests ==========

    @Test
    fun `should set streaming quality to LOW correctly`() {
        // Given
        networkController.showStreamingIndicator(mockContext)

        // When
        networkController.setStreamingQuality(NetworkController.StreamingQuality.LOW)

        // Then
        val (frameRate, dataSize) = networkController.getStreamingMetrics()
        assertThat(frameRate).isEqualTo(15)
        assertThat(dataSize).isEqualTo("500 KB/s")
        verify { mockCallback.updateStatusText(any()) }
    }

    @Test
    fun `should set streaming quality to HIGH correctly`() {
        // Given
        networkController.showStreamingIndicator(mockContext)

        // When
        networkController.setStreamingQuality(NetworkController.StreamingQuality.HIGH)

        // Then
        val (frameRate, dataSize) = networkController.getStreamingMetrics()
        assertThat(frameRate).isEqualTo(30)
        assertThat(dataSize).isEqualTo("2.5 MB/s")
        verify { mockCallback.updateStatusText(match { it.contains("High") }) }
    }

    @Test
    fun `should not update metrics when setting quality while not streaming`() {
        // Given - not streaming
        assertThat(networkController.isStreamingActive()).isFalse()

        // When
        networkController.setStreamingQuality(NetworkController.StreamingQuality.ULTRA)

        // Then
        val (frameRate, dataSize) = networkController.getStreamingMetrics()
        assertThat(frameRate).isEqualTo(0) // Should remain default
        assertThat(dataSize).isEqualTo("0 KB/s") // Should remain default
    }

    // ========== Actual Streaming Logic Tests ==========

    @Test
    fun `should start streaming session successfully`() = runTest {
        // When
        networkController.startStreaming(mockContext)

        // Then
        assertThat(networkController.isStreamingActive()).isTrue()
        verify { mockCallback.onStreamingStarted() }
        verify { mockCallback.updateStatusText("Streaming started") }
        
        val (frameRate, dataSize) = networkController.getStreamingMetrics()
        assertThat(frameRate).isEqualTo(30) // Default frame rate
        assertThat(dataSize).isEqualTo("1.2 MB/s") // Default data size
    }

    @Test
    fun `should stop streaming session successfully`() = runTest {
        // Given - start streaming first
        networkController.startStreaming(mockContext)
        
        // When
        networkController.stopStreaming(mockContext)

        // Then
        assertThat(networkController.isStreamingActive()).isFalse()
        verify { mockCallback.onStreamingStopped() }
        verify { mockCallback.updateStatusText("Streaming stopped") }
        
        val (frameRate, dataSize) = networkController.getStreamingMetrics()
        assertThat(frameRate).isEqualTo(0)
        assertThat(dataSize).isEqualTo("0 KB/s")
    }

    // ========== Network Statistics Tests ==========

    @Test
    fun `should return valid network statistics`() {
        // When
        val statistics = networkController.getNetworkStatistics(mockContext)

        // Then
        assertThat(statistics).containsKey("streaming_active")
        assertThat(statistics).containsKey("frame_rate")
        assertThat(statistics).containsKey("data_size")
        assertThat(statistics).containsKey("timestamp")
        assertThat(statistics).containsKey("network_type")
        assertThat(statistics).containsKey("bandwidth_estimate")
        assertThat(statistics).containsKey("connection_quality")
    }

    @Test
    fun `should return streaming status summary`() {
        // Given
        networkController.updateStreamingMetrics(25, "1.1 MB/s")

        // When
        val status = networkController.getStreamingStatus(mockContext)

        // Then
        assertThat(status).contains("Streaming Status:")
        assertThat(status).contains("Frame Rate: 25fps")
        assertThat(status).contains("Data Size: 1.1 MB/s")
        assertThat(status).contains("Network Connected:")
        assertThat(status).contains("Network Type:")
        assertThat(status).contains("Bandwidth Estimate:")
    }

    // ========== Emergency and Error Handling Tests ==========

    @Test
    fun `should handle emergency streaming stop`() = runTest {
        // Given - streaming is active
        networkController.startStreaming(mockContext)
        
        // When
        networkController.emergencyStopStreaming(mockContext)

        // Then
        assertThat(networkController.isStreamingActive()).isFalse()
        verify { mockCallback.updateStatusText(match { it.contains("Emergency stop completed") }) }
        verify { mockCallback.showToast(match { it.contains("Emergency stop") }, any()) }
    }

    @Test
    fun `should reset state correctly`() {
        // Given - streaming is active with metrics
        networkController.startStreaming(mockContext)
        networkController.updateStreamingMetrics(60, "3.0 MB/s")
        
        // When
        networkController.resetState()

        // Then
        assertThat(networkController.isStreamingActive()).isFalse()
        val (frameRate, dataSize) = networkController.getStreamingMetrics()
        assertThat(frameRate).isEqualTo(0)
        assertThat(dataSize).isEqualTo("0 KB/s")
    }

    @Test
    fun `should handle callback being null gracefully`() {
        // Given - remove callback
        networkController.setCallback(null)

        // When & Then - should not crash
        networkController.showStreamingIndicator(mockContext)
        networkController.hideStreamingIndicator(mockContext)
        networkController.updateStreamingDebugOverlay()
        networkController.handleNetworkConnectivityChange(false)
    }

    // ========== StreamingQuality Enum Tests ==========

    @Test
    fun `StreamingQuality enum should have correct display names`() {
        assertThat(NetworkController.StreamingQuality.LOW.displayName).isEqualTo("Low (480p, 15fps)")
        assertThat(NetworkController.StreamingQuality.MEDIUM.displayName).isEqualTo("Medium (720p, 30fps)")
        assertThat(NetworkController.StreamingQuality.HIGH.displayName).isEqualTo("High (1080p, 30fps)")
        assertThat(NetworkController.StreamingQuality.ULTRA.displayName).isEqualTo("Ultra (1080p, 60fps)")
    }

    // ========== Network Type and Bandwidth Tests ==========

    @Test
    fun `should handle network statistics without context`() {
        // When
        val statistics = networkController.getNetworkStatistics(context = null)

        // Then
        assertThat(statistics["network_type"]).isEqualTo("Context unavailable")
        assertThat(statistics).containsKey("streaming_active")
        assertThat(statistics).containsKey("frame_rate")
        assertThat(statistics).containsKey("timestamp")
    }

    @Test
    fun `should return status summary without context`() {
        // When
        val status = networkController.getStreamingStatus(context = null)

        // Then
        assertThat(status).contains("Network Type: Unknown")
        assertThat(status).contains("Network Connected: false")
        assertThat(status).contains("Streaming Status:")
    }
}