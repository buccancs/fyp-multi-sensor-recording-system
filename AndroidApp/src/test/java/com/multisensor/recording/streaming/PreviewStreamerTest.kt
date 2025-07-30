package com.multisensor.recording.streaming

import android.graphics.ImageFormat
import android.media.Image
import com.multisensor.recording.network.JsonSocketClient
import com.multisensor.recording.network.PreviewFrameMessage
import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Before
import org.junit.Test
import java.nio.ByteBuffer

@ExperimentalCoroutinesApi
class PreviewStreamerTest {

    private lateinit var previewStreamer: PreviewStreamer
    private lateinit var mockJsonSocketClient: JsonSocketClient
    private lateinit var mockLogger: Logger

    @Before
    fun setUp() {
        mockLogger = mockk(relaxed = true)
        mockJsonSocketClient = mockk(relaxed = true)
        previewStreamer = PreviewStreamer(mockJsonSocketClient, mockLogger)
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `onRgbFrameAvailable should send frame when streaming`() = runTest {
        // Given
        previewStreamer.startStreaming()
        val mockImage = mockImage(ImageFormat.JPEG)

        // When
        previewStreamer.onRgbFrameAvailable(mockImage)

        // Then
        coVerify(timeout = 100) { mockJsonSocketClient.sendMessage(any<PreviewFrameMessage>()) }
        verify { mockImage.close() }
    }

    @Test
    fun `onRgbFrameAvailable should not send frame when not streaming`() = runTest {
        // Given
        val mockImage = mockImage(ImageFormat.JPEG)

        // When
        previewStreamer.onRgbFrameAvailable(mockImage)

        // Then
        coVerify(exactly = 0) { mockJsonSocketClient.sendMessage(any()) }
        verify { mockImage.close() }
    }

    @Test
    fun `onThermalFrameAvailable should send frame when streaming`() = runTest {
        // Given
        previewStreamer.startStreaming()
        val thermalData = ByteArray(256 * 192 * 2)

        // When
        previewStreamer.onThermalFrameAvailable(thermalData, 256, 192)

        // Then
        coVerify(timeout = 100) { mockJsonSocketClient.sendMessage(any<PreviewFrameMessage>()) }
    }

    @Test
    fun `frame rate control should skip frames correctly`() = runTest {
        // Given
        previewStreamer.configure(fps = 1) // 1 frame per second (1000ms interval)
        previewStreamer.startStreaming()
        val mockImage1 = mockImage(ImageFormat.JPEG)
        val mockImage2 = mockImage(ImageFormat.JPEG)

        // When
        previewStreamer.onRgbFrameAvailable(mockImage1) // This one should be processed
        Thread.sleep(100) // Wait less than the interval
        previewStreamer.onRgbFrameAvailable(mockImage2) // This one should be skipped

        // Then
        coVerify(exactly = 1) { mockJsonSocketClient.sendMessage(any<PreviewFrameMessage>()) }
        verify { mockImage1.close() }
        verify { mockImage2.close() }
    }

    // Helper function to create a mock Image
    private fun mockImage(format: Int): Image {
        val mockImage = mockk<Image>(relaxed = true)
        val mockPlane = mockk<Image.Plane>(relaxed = true)
        val mockBuffer = ByteBuffer.wrap(byteArrayOf(1, 2, 3))

        every { mockImage.format } returns format
        every { mockImage.planes } returns arrayOf(mockPlane)
        every { mockPlane.buffer } returns mockBuffer

        return mockImage
    }
}