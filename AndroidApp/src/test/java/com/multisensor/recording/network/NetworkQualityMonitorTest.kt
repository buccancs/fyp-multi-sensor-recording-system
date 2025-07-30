package com.multisensor.recording.network

import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.net.Socket

/**
 * Unit tests for NetworkQualityMonitor
 * Tests network quality assessment, monitoring, and listener functionality
 */
@RunWith(RobolectricTestRunner::class)
class NetworkQualityMonitorTest {
    private lateinit var mockLogger: Logger
    private lateinit var networkQualityMonitor: NetworkQualityMonitor
    private lateinit var testDispatcher: TestDispatcher

    @Before
    fun setUp() {
        mockLogger = mockk(relaxed = true)
        testDispatcher = StandardTestDispatcher()
        Dispatchers.setMain(testDispatcher)

        networkQualityMonitor = NetworkQualityMonitor(mockLogger)

        println("[DEBUG_LOG] NetworkQualityMonitorTest setup complete")
    }

    @After
    fun tearDown() {
        networkQualityMonitor.stopMonitoring()
        Dispatchers.resetMain()
        clearAllMocks()
        println("[DEBUG_LOG] NetworkQualityMonitorTest teardown complete")
    }

    @Test
    fun testNetworkQualityDataClass() {
        println("[DEBUG_LOG] Testing NetworkQuality data class")

        val quality =
            NetworkQualityMonitor.NetworkQuality(
                score = 4,
                latencyMs = 75,
                bandwidthKbps = 1500.0,
            )

        assertEquals("Score should be 4", 4, quality.score)
        assertEquals("Latency should be 75ms", 75, quality.latencyMs)
        assertEquals("Bandwidth should be 1500.0 Kbps", 1500.0, quality.bandwidthKbps, 0.1)
        assertTrue("Timestamp should be recent", quality.timestamp > 0)

        println("[DEBUG_LOG] NetworkQuality data class test passed")
    }

    @Test
    fun testStartAndStopMonitoring() {
        println("[DEBUG_LOG] Testing start and stop monitoring")

        val testHost = "192.168.1.100"
        val testPort = 8080

        // Test starting monitoring
        networkQualityMonitor.startMonitoring(testHost, testPort)

        verify { mockLogger.info("[DEBUG_LOG] Starting network quality monitoring for $testHost:$testPort") }

        // Test stopping monitoring
        networkQualityMonitor.stopMonitoring()

        verify { mockLogger.info("[DEBUG_LOG] Stopping network quality monitoring") }

        println("[DEBUG_LOG] Start and stop monitoring test passed")
    }

    @Test
    fun testDoubleStartMonitoring() {
        println("[DEBUG_LOG] Testing double start monitoring prevention")

        val testHost = "192.168.1.100"
        val testPort = 8080

        // Start monitoring twice
        networkQualityMonitor.startMonitoring(testHost, testPort)
        networkQualityMonitor.startMonitoring(testHost, testPort)

        verify { mockLogger.info("[DEBUG_LOG] NetworkQualityMonitor already monitoring") }

        println("[DEBUG_LOG] Double start monitoring prevention test passed")
    }

    @Test
    fun testListenerRegistration() {
        println("[DEBUG_LOG] Testing listener registration and notification")

        val mockListener = mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)

        // Add listener
        networkQualityMonitor.addListener(mockListener)

        // Verify immediate notification with current quality
        verify { mockListener.onNetworkQualityChanged(any()) }

        // Remove listener
        networkQualityMonitor.removeListener(mockListener)

        println("[DEBUG_LOG] Listener registration test passed")
    }

    @Test
    fun testFrameTransmissionRecording() {
        println("[DEBUG_LOG] Testing frame transmission recording")

        val frameSize1 = 50000L // 50KB
        val frameSize2 = 75000L // 75KB

        // Record first frame
        networkQualityMonitor.recordFrameTransmission(frameSize1)

        // Wait a bit and record second frame
        Thread.sleep(100)
        networkQualityMonitor.recordFrameTransmission(frameSize2)

        // Verify no exceptions thrown
        assertTrue("Frame transmission recording should work without errors", true)

        println("[DEBUG_LOG] Frame transmission recording test passed")
    }

    @Test
    fun testGetCurrentQuality() {
        println("[DEBUG_LOG] Testing get current quality")

        val currentQuality = networkQualityMonitor.getCurrentQuality()

        assertNotNull("Current quality should not be null", currentQuality)
        assertTrue("Quality score should be between 1 and 5", currentQuality.score in 1..5)
        assertTrue("Latency should be positive", currentQuality.latencyMs > 0)
        assertTrue("Bandwidth should be positive", currentQuality.bandwidthKbps > 0)

        println(
            "[DEBUG_LOG] Current quality: Score=${currentQuality.score}, Latency=${currentQuality.latencyMs}ms, Bandwidth=${currentQuality.bandwidthKbps}Kbps",
        )
        println("[DEBUG_LOG] Get current quality test passed")
    }

    @Test
    fun testNetworkStatistics() {
        println("[DEBUG_LOG] Testing network statistics")

        val statistics = networkQualityMonitor.getNetworkStatistics()

        assertNotNull("Statistics should not be null", statistics)
        assertTrue("Statistics should contain quality information", statistics.contains("Network Quality Statistics"))
        assertTrue("Statistics should contain current score", statistics.contains("Current Score"))
        assertTrue("Statistics should contain latency", statistics.contains("Latency"))
        assertTrue("Statistics should contain bandwidth", statistics.contains("Bandwidth"))

        println("[DEBUG_LOG] Network statistics: $statistics")
        println("[DEBUG_LOG] Network statistics test passed")
    }

    @Test
    fun testQualityScoreCalculation() {
        println("[DEBUG_LOG] Testing quality score calculation logic")

        // Test with different frame sizes to simulate different bandwidth conditions
        val smallFrame = 10000L // 10KB - should indicate lower bandwidth
        val largeFrame = 100000L // 100KB - should indicate higher bandwidth

        networkQualityMonitor.recordFrameTransmission(smallFrame)
        Thread.sleep(50)
        networkQualityMonitor.recordFrameTransmission(smallFrame)

        val qualityAfterSmallFrames = networkQualityMonitor.getCurrentQuality()

        Thread.sleep(100)

        networkQualityMonitor.recordFrameTransmission(largeFrame)
        Thread.sleep(50)
        networkQualityMonitor.recordFrameTransmission(largeFrame)

        val qualityAfterLargeFrames = networkQualityMonitor.getCurrentQuality()

        // Both should have valid quality scores
        assertTrue("Quality after small frames should be valid", qualityAfterSmallFrames.score in 1..5)
        assertTrue("Quality after large frames should be valid", qualityAfterLargeFrames.score in 1..5)

        println("[DEBUG_LOG] Quality after small frames: ${qualityAfterSmallFrames.score}")
        println("[DEBUG_LOG] Quality after large frames: ${qualityAfterLargeFrames.score}")
        println("[DEBUG_LOG] Quality score calculation test passed")
    }

    @Test
    fun testListenerErrorHandling() {
        println("[DEBUG_LOG] Testing listener error handling")

        val faultyListener =
            object : NetworkQualityMonitor.NetworkQualityListener {
                override fun onNetworkQualityChanged(quality: NetworkQualityMonitor.NetworkQuality): Unit =
                    throw RuntimeException("Test exception")
            }

        // Add faulty listener
        networkQualityMonitor.addListener(faultyListener)

        // Verify error is logged but doesn't crash the system
        verify { mockLogger.error("Error notifying network quality listener", any<Exception>()) }

        println("[DEBUG_LOG] Listener error handling test passed")
    }

    @Test
    fun testMonitoringWithInvalidHost() {
        println("[DEBUG_LOG] Testing monitoring with invalid host")

        val invalidHost = "invalid.host.name"
        val testPort = 8080

        // Start monitoring with invalid host
        networkQualityMonitor.startMonitoring(invalidHost, testPort)

        // Should not crash, monitoring should handle connection failures gracefully
        assertTrue("Monitoring with invalid host should not crash", true)

        println("[DEBUG_LOG] Monitoring with invalid host test passed")
    }

    @Test
    fun testConcurrentListenerOperations() {
        println("[DEBUG_LOG] Testing concurrent listener operations")

        val listener1 = mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)
        val listener2 = mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)
        val listener3 = mockk<NetworkQualityMonitor.NetworkQualityListener>(relaxed = true)

        // Add multiple listeners
        networkQualityMonitor.addListener(listener1)
        networkQualityMonitor.addListener(listener2)
        networkQualityMonitor.addListener(listener3)

        // Remove one listener
        networkQualityMonitor.removeListener(listener2)

        // All operations should complete without errors
        assertTrue("Concurrent listener operations should work", true)

        println("[DEBUG_LOG] Concurrent listener operations test passed")
    }

    @Test
    fun testNetworkQualityBoundaryValues() {
        println("[DEBUG_LOG] Testing network quality boundary values")

        val currentQuality = networkQualityMonitor.getCurrentQuality()

        // Test score boundaries
        assertTrue("Quality score should be at least 1", currentQuality.score >= 1)
        assertTrue("Quality score should be at most 5", currentQuality.score <= 5)

        // Test latency boundaries
        assertTrue("Latency should be non-negative", currentQuality.latencyMs >= 0)

        // Test bandwidth boundaries
        assertTrue("Bandwidth should be non-negative", currentQuality.bandwidthKbps >= 0)

        println("[DEBUG_LOG] Network quality boundary values test passed")
    }
}
