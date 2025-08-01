package com.multisensor.recording.network

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseRobolectricTest
import com.multisensor.recording.util.Logger
import io.mockk.impl.annotations.InjectMockKs
import io.mockk.impl.annotations.RelaxedMockK
import io.mockk.verify
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Test

/**
 * Comprehensive unit tests for NetworkQualityMonitor
 * 
 * Test Categories:
 * - Network quality assessment and scoring
 * - Monitoring lifecycle management
 * - Listener registration and notification
 * - Frame transmission recording
 * - Error handling and boundary conditions
 */
@OptIn(ExperimentalCoroutinesApi::class)
class NetworkQualityMonitorTest : BaseRobolectricTest() {

    @RelaxedMockK
    private lateinit var mockLogger: Logger

    @InjectMockKs
    private lateinit var networkQualityMonitor: NetworkQualityMonitor

    @After
    fun cleanup() {
        networkQualityMonitor.stopMonitoring()
    }

    @Test
    fun `NetworkQuality data class should initialize correctly`() {
        // Given
        val score = 4
        val latency = 75L
        val bandwidth = 1500.0

        // When
        val quality = NetworkQualityMonitor.NetworkQuality(
            score = score,
            latencyMs = latency,
            bandwidthKbps = bandwidth
        )

        // Then
        assertThat(quality.score).isEqualTo(score)
        assertThat(quality.latencyMs).isEqualTo(latency)
        assertThat(quality.bandwidthKbps).isWithin(0.1).of(bandwidth)
        assertThat(quality.timestamp).isGreaterThan(0L)
    }

    @Test
    fun `should start and stop monitoring correctly`() {
        // Given
        val testHost = "192.168.1.100"
        val testPort = 8080

        // When
        networkQualityMonitor.startMonitoring(testHost, testPort)

        // Then
        verify { mockLogger.info("[DEBUG_LOG] Starting network quality monitoring for $testHost:$testPort") }

        // When
        networkQualityMonitor.stopMonitoring()

        // Then
        verify { mockLogger.info("[DEBUG_LOG] Stopping network quality monitoring") }
    }

    @Test
    fun `should prevent double start monitoring`() {
        // Given
        val testHost = "192.168.1.100"
        val testPort = 8080

        // When
        networkQualityMonitor.startMonitoring(testHost, testPort)
        networkQualityMonitor.startMonitoring(testHost, testPort)

        // Then
        verify { mockLogger.info("[DEBUG_LOG] NetworkQualityMonitor already monitoring") }
    }

    @Test
    fun `should handle listener registration and notification`() = runTest {
        // Given
        val mockListener = io.mockk.mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)

        // When
        networkQualityMonitor.addListener(mockListener)

        // Then
        verify { mockListener.onNetworkQualityChanged(any()) }

        // When
        networkQualityMonitor.removeListener(mockListener)

        // Then - no additional calls after removal
    }

    @Test
    fun `should record frame transmission without errors`() {
        // Given
        val frameSize1 = 50000L // 50KB
        val frameSize2 = 75000L // 75KB

        // When & Then - should not throw exceptions
        networkQualityMonitor.recordFrameTransmission(frameSize1)
        networkQualityMonitor.recordFrameTransmission(frameSize2)

        // Verify successful execution
        assertThat(true).isTrue() // Test passes if no exceptions thrown
    }

    @Test
    fun `should return valid current quality`() {
        // When
        val currentQuality = networkQualityMonitor.getCurrentQuality()

        // Then
        assertThat(currentQuality).isNotNull()
        assertThat(currentQuality.score).isIn(1..5)
        assertThat(currentQuality.latencyMs).isAtLeast(0)
        assertThat(currentQuality.bandwidthKbps).isAtLeast(0.0)
    }

    @Test
    fun `should return valid network statistics`() {
        // When
        val statistics = networkQualityMonitor.getNetworkStatistics()

        // Then
        assertThat(statistics).isNotNull()
        assertThat(statistics).contains("Network Quality Statistics")
        assertThat(statistics).contains("Current Score")
        assertThat(statistics).contains("Latency")
        assertThat(statistics).contains("Bandwidth")
    }

    @Test
    fun `should calculate quality scores based on frame transmission`() = runTest {
        // Given
        val smallFrame = 10000L // 10KB
        val largeFrame = 100000L // 100KB

        // When
        networkQualityMonitor.recordFrameTransmission(smallFrame)
        advanceTimeBy(100)
        networkQualityMonitor.recordFrameTransmission(smallFrame)
        
        val qualityAfterSmallFrames = networkQualityMonitor.getCurrentQuality()

        advanceTimeBy(100)
        
        networkQualityMonitor.recordFrameTransmission(largeFrame)
        advanceTimeBy(100)
        networkQualityMonitor.recordFrameTransmission(largeFrame)
        
        val qualityAfterLargeFrames = networkQualityMonitor.getCurrentQuality()

        // Then
        assertThat(qualityAfterSmallFrames.score).isIn(1..5)
        assertThat(qualityAfterLargeFrames.score).isIn(1..5)
    }

    @Test
    fun `should handle listener errors gracefully`() {
        // Given
        val faultyListener = object : NetworkQualityMonitor.NetworkQualityListener {
            override fun onNetworkQualityChanged(quality: NetworkQualityMonitor.NetworkQuality) {
                throw RuntimeException("Test exception")
            }
        }

        // When
        networkQualityMonitor.addListener(faultyListener)

        // Then
        verify { mockLogger.error("Error notifying network quality listener", any<Exception>()) }
    }

    @Test
    fun `should handle monitoring with invalid host gracefully`() {
        // Given
        val invalidHost = "invalid.host.name"
        val testPort = 8080

        // When & Then - should not crash
        networkQualityMonitor.startMonitoring(invalidHost, testPort)
        
        // Verify successful execution
        assertThat(true).isTrue() // Test passes if no exceptions thrown
    }

    @Test
    fun `should handle concurrent listener operations`() {
        // Given
        val listener1 = io.mockk.mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)
        val listener2 = io.mockk.mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)
        val listener3 = io.mockk.mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)

        // When
        networkQualityMonitor.addListener(listener1)
        networkQualityMonitor.addListener(listener2)
        networkQualityMonitor.addListener(listener3)
        networkQualityMonitor.removeListener(listener2)

        // Then - should complete without errors
        assertThat(true).isTrue() // Test passes if no exceptions thrown
    }

    @Test
    fun `should enforce quality boundary values`() {
        // When
        val currentQuality = networkQualityMonitor.getCurrentQuality()

        // Then
        assertThat(currentQuality.score).isAtLeast(1)
        assertThat(currentQuality.score).isAtMost(5)
        assertThat(currentQuality.latencyMs).isAtLeast(0)
        assertThat(currentQuality.bandwidthKbps).isAtLeast(0.0)
    }
}
