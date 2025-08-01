package com.multisensor.recording.ui.util

import android.content.Context
import android.view.View
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.test.core.app.ApplicationProvider
import com.multisensor.recording.R
import io.mockk.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class UIUtilsTest {

    private lateinit var context: Context
    private lateinit var mockView: View

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        mockView = mockk(relaxed = true)
        
        // Mock ContextCompat.getColor to return predictable values
        mockkStatic(ContextCompat::class)
        every { ContextCompat.getColor(any(), any()) } returns 0xFF000000.toInt()
    }

    @After
    fun tearDown() {
        clearAllMocks()
        unmockkStatic(ContextCompat::class)
    }

    @Test
    fun `updateConnectionIndicator should set connected color when connected`() {
        // When
        UIUtils.updateConnectionIndicator(context, mockView, true)

        // Then
        verify { ContextCompat.getColor(context, R.color.statusIndicatorConnected) }
        verify { mockView.setBackgroundColor(any()) }
    }

    @Test
    fun `updateConnectionIndicator should set disconnected color when not connected`() {
        // When
        UIUtils.updateConnectionIndicator(context, mockView, false)

        // Then
        verify { ContextCompat.getColor(context, R.color.statusIndicatorDisconnected) }
        verify { mockView.setBackgroundColor(any()) }
    }

    @Test
    fun `updateRecordingIndicator should set active color when recording`() {
        // When
        UIUtils.updateRecordingIndicator(context, mockView, true)

        // Then
        verify { ContextCompat.getColor(context, R.color.recordingActive) }
        verify { mockView.setBackgroundColor(any()) }
    }

    @Test
    fun `updateRecordingIndicator should set inactive color when not recording`() {
        // When
        UIUtils.updateRecordingIndicator(context, mockView, false)

        // Then
        verify { ContextCompat.getColor(context, R.color.recordingInactive) }
        verify { mockView.setBackgroundColor(any()) }
    }

    @Test
    fun `showStatusMessage should create short toast by default`() {
        // Given
        val message = "Test message"
        mockkStatic(Toast::class)
        val mockToast = mockk<Toast>(relaxed = true)
        every { Toast.makeText(context, message, Toast.LENGTH_SHORT) } returns mockToast

        // When
        UIUtils.showStatusMessage(context, message)

        // Then
        verify { Toast.makeText(context, message, Toast.LENGTH_SHORT) }
        verify { mockToast.show() }
    }

    @Test
    fun `showStatusMessage should create long toast when specified`() {
        // Given
        val message = "Test long message"
        mockkStatic(Toast::class)
        val mockToast = mockk<Toast>(relaxed = true)
        every { Toast.makeText(context, message, Toast.LENGTH_LONG) } returns mockToast

        // When
        UIUtils.showStatusMessage(context, message, true)

        // Then
        verify { Toast.makeText(context, message, Toast.LENGTH_LONG) }
        verify { mockToast.show() }
    }

    @Test
    fun `getConnectionStatusText should return connected status`() {
        // When
        val result = UIUtils.getConnectionStatusText("Device1", true)

        // Then
        assertEquals("Device1: Connected", result)
    }

    @Test
    fun `getConnectionStatusText should return PC waiting status`() {
        // When
        val result = UIUtils.getConnectionStatusText("PC", false)

        // Then
        assertEquals("PC: Waiting...", result)
    }

    @Test
    fun `getConnectionStatusText should return Shimmer off status`() {
        // When
        val result = UIUtils.getConnectionStatusText("Shimmer", false)

        // Then
        assertEquals("Shimmer: Off", result)
    }

    @Test
    fun `getConnectionStatusText should return thermal off status`() {
        // When
        val result = UIUtils.getConnectionStatusText("Thermal", false)

        // Then
        assertEquals("Thermal: Off", result)
    }

    @Test
    fun `getConnectionStatusText should return generic disconnected status`() {
        // When
        val result = UIUtils.getConnectionStatusText("GenericDevice", false)

        // Then
        assertEquals("GenericDevice: Disconnected", result)
    }

    @Test
    fun `formatBatteryText should format positive battery level`() {
        // When
        val result = UIUtils.formatBatteryText(75)

        // Then
        assertEquals("Battery: 75%", result)
    }

    @Test
    fun `formatBatteryText should format zero battery level`() {
        // When
        val result = UIUtils.formatBatteryText(0)

        // Then
        assertEquals("Battery: 0%", result)
    }

    @Test
    fun `formatBatteryText should format negative battery level`() {
        // When
        val result = UIUtils.formatBatteryText(-1)

        // Then
        assertEquals("Battery: ---%", result)
    }

    @Test
    fun `formatStreamingText should format active streaming`() {
        // When
        val result = UIUtils.formatStreamingText(true, 30, "1.2MB")

        // Then
        assertEquals("Streaming: 30fps (1.2MB)", result)
    }

    @Test
    fun `formatStreamingText should format inactive streaming`() {
        // When
        val result = UIUtils.formatStreamingText(false, 0, "0MB")

        // Then
        assertEquals("Ready to stream", result)
    }

    @Test
    fun `formatStreamingText should format ready when frame rate is zero`() {
        // When
        val result = UIUtils.formatStreamingText(true, 0, "0MB")

        // Then
        assertEquals("Ready to stream", result)
    }

    @Test
    fun `getRecordingStatusText should return recording status`() {
        // When
        val result = UIUtils.getRecordingStatusText(true)

        // Then
        assertEquals("Recording in progress...", result)
    }

    @Test
    fun `getRecordingStatusText should return ready status`() {
        // When
        val result = UIUtils.getRecordingStatusText(false)

        // Then
        assertEquals("Ready to record", result)
    }

    @Test
    fun `styleButton should apply primary button style`() {
        // When
        UIUtils.styleButton(context, mockView, UIUtils.ButtonType.PRIMARY, true)

        // Then
        verify { ContextCompat.getColor(context, R.color.colorSecondary) }
        verify { mockView.setBackgroundColor(any()) }
        verify { mockView.isEnabled = true }
        verify { mockView.alpha = 1.0f }
    }

    @Test
    fun `styleButton should apply success button style`() {
        // When
        UIUtils.styleButton(context, mockView, UIUtils.ButtonType.SUCCESS, true)

        // Then
        verify { ContextCompat.getColor(context, R.color.colorPrimary) }
        verify { mockView.setBackgroundColor(any()) }
        verify { mockView.isEnabled = true }
        verify { mockView.alpha = 1.0f }
    }

    @Test
    fun `styleButton should apply danger button style`() {
        // When
        UIUtils.styleButton(context, mockView, UIUtils.ButtonType.DANGER, true)

        // Then
        verify { ContextCompat.getColor(context, R.color.recordingActive) }
        verify { mockView.setBackgroundColor(any()) }
        verify { mockView.isEnabled = true }
        verify { mockView.alpha = 1.0f }
    }

    @Test
    fun `styleButton should apply secondary button style`() {
        // When
        UIUtils.styleButton(context, mockView, UIUtils.ButtonType.SECONDARY, true)

        // Then
        verify { ContextCompat.getColor(context, R.color.textColorSecondary) }
        verify { mockView.setBackgroundColor(any()) }
        verify { mockView.isEnabled = true }
        verify { mockView.alpha = 1.0f }
    }

    @Test
    fun `styleButton should apply disabled state`() {
        // When
        UIUtils.styleButton(context, mockView, UIUtils.ButtonType.PRIMARY, false)

        // Then
        verify { mockView.isEnabled = false }
        verify { mockView.alpha = 0.6f }
    }

    @Test
    fun `setViewVisibilityWithAnimation should show view`() {
        // Given
        val mockAnimator = mockk<View.ViewPropertyAnimator>(relaxed = true)
        every { mockView.animate() } returns mockAnimator
        every { mockAnimator.alpha(any()) } returns mockAnimator
        every { mockAnimator.setDuration(any()) } returns mockAnimator

        // When
        UIUtils.setViewVisibilityWithAnimation(mockView, true, 100)

        // Then
        verify { mockView.visibility = View.VISIBLE }
        verify { mockAnimator.alpha(1.0f) }
        verify { mockAnimator.setDuration(100) }
    }

    @Test
    fun `setViewVisibilityWithAnimation should hide view`() {
        // Given
        val mockAnimator = mockk<View.ViewPropertyAnimator>(relaxed = true)
        every { mockView.animate() } returns mockAnimator
        every { mockAnimator.alpha(any()) } returns mockAnimator
        every { mockAnimator.setDuration(any()) } returns mockAnimator
        every { mockAnimator.withEndAction(any()) } returns mockAnimator

        // When
        UIUtils.setViewVisibilityWithAnimation(mockView, false, 100)

        // Then
        verify { mockAnimator.alpha(0.0f) }
        verify { mockAnimator.setDuration(100) }
        verify { mockAnimator.withEndAction(any()) }
    }

    @Test
    fun `getOperationTimeout should return correct timeouts`() {
        // Test all operation types
        assertEquals(10000L, UIUtils.getOperationTimeout(UIUtils.OperationType.CONNECTION))
        assertEquals(5000L, UIUtils.getOperationTimeout(UIUtils.OperationType.RECORDING_START))
        assertEquals(3000L, UIUtils.getOperationTimeout(UIUtils.OperationType.RECORDING_STOP))
        assertEquals(30000L, UIUtils.getOperationTimeout(UIUtils.OperationType.CALIBRATION))
        assertEquals(15000L, UIUtils.getOperationTimeout(UIUtils.OperationType.FILE_OPERATION))
    }
}