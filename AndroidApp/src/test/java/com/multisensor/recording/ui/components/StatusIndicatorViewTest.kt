package com.multisensor.recording.ui.components

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class StatusIndicatorViewTest {

    private lateinit var context: Context
    private lateinit var statusIndicatorView: StatusIndicatorView

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        statusIndicatorView = StatusIndicatorView(context)
    }

    @Test
    fun testInitialState() {
        assertNotNull(statusIndicatorView)
        assertEquals(
            "Status: Disconnected",
            statusIndicatorView.findViewById<android.widget.TextView>(android.R.id.text1)?.text
        )
    }

    @Test
    fun testSetStatusConnected() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.CONNECTED, "PC: Connected")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("PC: Connected", textView.text)

        val indicator = statusIndicatorView.getChildAt(0)
        assertNotNull(indicator)
    }

    @Test
    fun testSetStatusDisconnected() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Shimmer: Disconnected")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Shimmer: Disconnected", textView.text)
    }

    @Test
    fun testSetStatusRecording() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.RECORDING, "Recording: Active")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Recording: Active", textView.text)
    }

    @Test
    fun testSetStatusStopped() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.STOPPED, "Recording: Stopped")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Recording: Stopped", textView.text)
    }

    @Test
    fun testSetStatusWarning() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.WARNING, "Warning: Low Battery")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Warning: Low Battery", textView.text)
    }

    @Test
    fun testSetStatusError() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.ERROR, "Error: Connection Failed")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Error: Connection Failed", textView.text)
    }

    @Test
    fun testSetCustomTextColor() {
        statusIndicatorView.setTextColor(android.R.color.holo_blue_light)

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertNotNull(textView)
    }

    @Test
    fun testSetCustomTextSize() {
        val customSize = 16f
        statusIndicatorView.setTextSize(customSize)

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals(customSize, textView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testComponentStructure() {
        assertEquals(2, statusIndicatorView.childCount)

        val indicator = statusIndicatorView.getChildAt(0)
        assertNotNull(indicator)
        assertTrue(indicator is android.view.View)

        val textView = statusIndicatorView.getChildAt(1)
        assertNotNull(textView)
        assertTrue(textView is android.widget.TextView)
    }

    @Test
    fun testLayoutOrientation() {
        assertEquals(android.widget.LinearLayout.HORIZONTAL, statusIndicatorView.orientation)
    }

    @Test
    fun testMultipleStatusUpdates() {
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Initial State")
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.CONNECTED, "Connected State")
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.RECORDING, "Recording State")

        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Recording State", textView.text)
    }
}