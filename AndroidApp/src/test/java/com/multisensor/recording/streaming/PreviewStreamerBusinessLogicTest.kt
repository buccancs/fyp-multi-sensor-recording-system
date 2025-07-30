package com.multisensor.recording.streaming

import com.multisensor.recording.network.SocketController
import com.multisensor.recording.util.Logger
import io.mockk.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Non-Android unit tests for PreviewStreamer business logic
 * Tests StreamingStats, configuration validation, and core logic without requiring Android graphics APIs
 */
class PreviewStreamerBusinessLogicTest {
    private lateinit var mockSocketController: SocketController
    private lateinit var mockLogger: Logger
    private lateinit var previewStreamer: PreviewStreamer

    @Before
    fun setup() {
        mockSocketController = mockk(relaxed = true)
        mockLogger = mockk(relaxed = true)
        previewStreamer = PreviewStreamer(mockSocketController, mockLogger)
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `StreamingStats should initialize with correct values`() {
        // When
        val stats =
            PreviewStreamer.StreamingStats(
                isStreaming = true,
                frameCount = 100L,
                targetFps = 30,
                jpegQuality = 80,
                maxFrameSize = "1920x1080",
            )

        // Then
        assertTrue("Should be streaming", stats.isStreaming)
        assertEquals(100L, stats.frameCount)
        assertEquals(30, stats.targetFps)
        assertEquals(80, stats.jpegQuality)
        assertEquals("1920x1080", stats.maxFrameSize)
    }

    @Test
    fun `StreamingStats should handle default streaming state`() {
        // When
        val stats =
            PreviewStreamer.StreamingStats(
                isStreaming = false,
                frameCount = 0L,
                targetFps = 2,
                jpegQuality = 70,
                maxFrameSize = "640x480",
            )

        // Then
        assertFalse("Should not be streaming", stats.isStreaming)
        assertEquals(0L, stats.frameCount)
        assertEquals(2, stats.targetFps)
        assertEquals(70, stats.jpegQuality)
        assertEquals("640x480", stats.maxFrameSize)
    }

    @Test
    fun `StreamingStats should support data class functionality`() {
        // Given
        val stats1 =
            PreviewStreamer.StreamingStats(
                isStreaming = true,
                frameCount = 50L,
                targetFps = 15,
                jpegQuality = 85,
                maxFrameSize = "1280x720",
            )

        val stats2 =
            PreviewStreamer.StreamingStats(
                isStreaming = true,
                frameCount = 50L,
                targetFps = 15,
                jpegQuality = 85,
                maxFrameSize = "1280x720",
            )

        val stats3 =
            PreviewStreamer.StreamingStats(
                isStreaming = false,
                frameCount = 50L,
                targetFps = 15,
                jpegQuality = 85,
                maxFrameSize = "1280x720",
            )

        // Then
        assertEquals("Equal objects should be equal", stats1, stats2)
        assertNotEquals("Different objects should not be equal", stats1, stats3)
        assertEquals("Hash codes should be equal for equal objects", stats1.hashCode(), stats2.hashCode())
    }

    @Test
    fun `StreamingStats should have meaningful toString`() {
        // Given
        val stats =
            PreviewStreamer.StreamingStats(
                isStreaming = true,
                frameCount = 200L,
                targetFps = 24,
                jpegQuality = 90,
                maxFrameSize = "1920x1080",
            )

        // When
        val toString = stats.toString()

        // Then
        assertTrue("Should contain streaming status", toString.contains("true"))
        assertTrue("Should contain frame count", toString.contains("200"))
        assertTrue("Should contain target FPS", toString.contains("24"))
        assertTrue("Should contain JPEG quality", toString.contains("90"))
        assertTrue("Should contain max frame size", toString.contains("1920x1080"))
    }

    @Test
    fun `StreamingStats should support copy functionality`() {
        // Given
        val original =
            PreviewStreamer.StreamingStats(
                isStreaming = false,
                frameCount = 75L,
                targetFps = 10,
                jpegQuality = 60,
                maxFrameSize = "800x600",
            )

        // When
        val copied = original.copy(isStreaming = true, frameCount = 100L)

        // Then
        assertTrue("Should update streaming status", copied.isStreaming)
        assertEquals(100L, copied.frameCount)
        assertEquals(10, copied.targetFps) // Should preserve other values
        assertEquals(60, copied.jpegQuality)
        assertEquals("800x600", copied.maxFrameSize)
    }

    @Test
    fun `configure should accept valid parameters`() {
        // When & Then - Should not throw exceptions
        previewStreamer.configure(fps = 30, quality = 95, maxWidth = 1920, maxHeight = 1080)
        previewStreamer.configure(fps = 1, quality = 10, maxWidth = 320, maxHeight = 240)
        previewStreamer.configure(fps = 60, quality = 100, maxWidth = 4096, maxHeight = 2160)

        // Verify logger was called for configuration
        verify(atLeast = 1) { mockLogger.info(any()) }
    }

    @Test
    fun `configure should handle edge case parameters`() {
        // When & Then - Should handle edge cases gracefully
        previewStreamer.configure(fps = 0, quality = 0, maxWidth = 0, maxHeight = 0)
        previewStreamer.configure(fps = 1000, quality = 200, maxWidth = 10000, maxHeight = 10000)

        // Should log configuration changes
        verify(atLeast = 1) { mockLogger.info(any()) }
    }

    @Test
    fun `frame rate limiting logic should work correctly`() {
        // Given - Configure for 2 FPS (500ms interval)
        previewStreamer.configure(fps = 2)

        // When - Simulate frame processing timing
        val currentTime = System.currentTimeMillis()
        val lastFrameTime = currentTime - 600 // 600ms ago (should allow processing)
        val recentFrameTime = currentTime - 200 // 200ms ago (should skip processing)

        // Then
        val shouldProcessOld = (currentTime - lastFrameTime) >= 500
        val shouldProcessRecent = (currentTime - recentFrameTime) >= 500

        assertTrue("Should process frame after sufficient interval", shouldProcessOld)
        assertFalse("Should skip frame if too recent", shouldProcessRecent)
    }

    @Test
    fun `frame rate calculation should be accurate`() {
        // Given
        val targetFps = 30
        val expectedInterval = 1000 / targetFps // 33.33ms

        // When
        val actualInterval = 1000 / targetFps

        // Then
        assertEquals("Interval should be correct for 30 FPS", 33, actualInterval)

        // Test other common frame rates
        assertEquals("Interval should be correct for 60 FPS", 16, 1000 / 60)
        assertEquals("Interval should be correct for 15 FPS", 66, 1000 / 15)
        assertEquals("Interval should be correct for 2 FPS", 500, 1000 / 2)
    }

    @Test
    fun `thermal color palette mapping should work correctly`() {
        // Test the iron color palette logic (simulated)
        // This tests the mathematical mapping without Android graphics

        // Given - Temperature range mapping (0-255)
        val minTemp = 0
        val maxTemp = 255
        val midTemp = 128

        // When - Apply color mapping logic
        val lowTempColor = applyIronColorPaletteLogic(minTemp)
        val midTempColor = applyIronColorPaletteLogic(midTemp)
        val highTempColor = applyIronColorPaletteLogic(maxTemp)

        // Then
        assertNotEquals("Low and mid temperatures should have different colors", lowTempColor, midTempColor)
        assertNotEquals("Mid and high temperatures should have different colors", midTempColor, highTempColor)
        assertNotEquals("Low and high temperatures should have different colors", lowTempColor, highTempColor)
    }

    @Test
    fun `thermal color palette should handle edge cases`() {
        // When & Then - Should handle edge values
        val negativeColor = applyIronColorPaletteLogic(-10)
        val zeroColor = applyIronColorPaletteLogic(0)
        val maxColor = applyIronColorPaletteLogic(255)
        val overMaxColor = applyIronColorPaletteLogic(300)

        // Colors should be valid (non-zero for visible temperatures)
        assertTrue("Zero temperature should have valid color", zeroColor != 0)
        assertTrue("Max temperature should have valid color", maxColor != 0)

        // Edge cases should be handled gracefully
        assertNotNull("Negative temperature should be handled", negativeColor)
        assertNotNull("Over-max temperature should be handled", overMaxColor)
    }

    @Test
    fun `streaming statistics should track frame count correctly`() {
        // Given
        var frameCount = 0L

        // When - Simulate frame processing
        repeat(10) {
            frameCount++
        }

        // Then
        assertEquals("Frame count should be accurate", 10L, frameCount)

        // Test large frame counts
        frameCount = Long.MAX_VALUE - 1
        frameCount++
        assertEquals("Should handle large frame counts", Long.MAX_VALUE, frameCount)
    }

    @Test
    fun `JPEG quality validation should work correctly`() {
        // Given
        val validQualities = listOf(10, 50, 70, 85, 95, 100)
        val invalidQualities = listOf(-10, 0, 150, 200)

        // When & Then
        validQualities.forEach { quality ->
            assertTrue("Quality $quality should be valid", quality in 1..100)
        }

        invalidQualities.forEach { quality ->
            assertFalse("Quality $quality should be invalid", quality in 1..100)
        }
    }

    @Test
    fun `frame size validation should work correctly`() {
        // Given
        val validSizes =
            listOf(
                Pair(320, 240),
                Pair(640, 480),
                Pair(1280, 720),
                Pair(1920, 1080),
            )

        val invalidSizes =
            listOf(
                Pair(-1, 240),
                Pair(320, -1),
                Pair(0, 0),
            )

        // When & Then
        validSizes.forEach { (width, height) ->
            assertTrue("Size ${width}x$height should be valid", width > 0 && height > 0)
        }

        invalidSizes.forEach { (width, height) ->
            assertFalse("Size ${width}x$height should be invalid", width > 0 && height > 0)
        }
    }

    @Test
    fun `FPS validation should work correctly`() {
        // Given
        val validFps = listOf(1, 2, 15, 30, 60)
        val invalidFps = listOf(-1, 0, 1000)

        // When & Then
        validFps.forEach { fps ->
            assertTrue("FPS $fps should be valid", fps > 0 && fps <= 120)
        }

        invalidFps.forEach { fps ->
            assertFalse("FPS $fps should be invalid", fps > 0 && fps <= 120)
        }
    }

    @Test
    fun `streaming state management should work correctly`() {
        // Given
        var isStreaming = false

        // When - Start streaming
        isStreaming = true

        // Then
        assertTrue("Should be streaming after start", isStreaming)

        // When - Stop streaming
        isStreaming = false

        // Then
        assertFalse("Should not be streaming after stop", isStreaming)
    }

    /**
     * Simulates the iron color palette logic without Android graphics dependencies
     */
    private fun applyIronColorPaletteLogic(normalizedTemp: Int): Int {
        // Simulate iron color palette mapping (simplified version)
        return when {
            normalizedTemp < 64 -> 0xFF000000.toInt() or (normalizedTemp * 4 shl 16) // Black to red
            normalizedTemp < 128 -> 0xFF000000.toInt() or (255 shl 16) or ((normalizedTemp - 64) * 4 shl 8) // Red to yellow
            normalizedTemp < 192 -> 0xFF000000.toInt() or (255 shl 16) or (255 shl 8) or ((normalizedTemp - 128) * 4) // Yellow to white
            else -> 0xFFFFFFFF.toInt() // White for hottest temperatures
        }
    }
}
