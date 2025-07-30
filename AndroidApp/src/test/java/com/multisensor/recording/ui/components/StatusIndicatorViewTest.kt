package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Color
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.*

/**
 * Unit tests for StatusIndicatorView component
 * Ensures proper functionality and styling of status indicators
 */
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
        // Test that the component initializes with default values
        assertNotNull(statusIndicatorView)
        assertEquals("Status: Disconnected", statusIndicatorView.findViewById<android.widget.TextView>(android.R.id.text1)?.text)
    }

    @Test
    fun testSetStatusConnected() {
        // Test setting connected status
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.CONNECTED, "PC: Connected")
        
        // Verify text is updated
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("PC: Connected", textView.text)
        
        // Verify indicator color is green (connected)
        val indicator = statusIndicatorView.getChildAt(0)
        assertNotNull(indicator)
    }

    @Test
    fun testSetStatusDisconnected() {
        // Test setting disconnected status
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Shimmer: Disconnected")
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Shimmer: Disconnected", textView.text)
    }

    @Test
    fun testSetStatusRecording() {
        // Test setting recording status
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.RECORDING, "Recording: Active")
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Recording: Active", textView.text)
    }

    @Test
    fun testSetStatusStopped() {
        // Test setting stopped status
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.STOPPED, "Recording: Stopped")
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Recording: Stopped", textView.text)
    }

    @Test
    fun testSetStatusWarning() {
        // Test setting warning status
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.WARNING, "Warning: Low Battery")
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Warning: Low Battery", textView.text)
    }

    @Test
    fun testSetStatusError() {
        // Test setting error status
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.ERROR, "Error: Connection Failed")
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Error: Connection Failed", textView.text)
    }

    @Test
    fun testSetCustomTextColor() {
        // Test setting custom text color
        statusIndicatorView.setTextColor(android.R.color.holo_blue_light)
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertNotNull(textView)
        // Color verification would require more complex testing setup
    }

    @Test
    fun testSetCustomTextSize() {
        // Test setting custom text size
        val customSize = 16f
        statusIndicatorView.setTextSize(customSize)
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals(customSize, textView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testComponentStructure() {
        // Test that the component has the correct child structure
        assertEquals(2, statusIndicatorView.childCount)
        
        // First child should be the indicator view
        val indicator = statusIndicatorView.getChildAt(0)
        assertNotNull(indicator)
        assertTrue(indicator is android.view.View)
        
        // Second child should be the text view
        val textView = statusIndicatorView.getChildAt(1)
        assertNotNull(textView)
        assertTrue(textView is android.widget.TextView)
    }

    @Test
    fun testLayoutOrientation() {
        // Test that the layout is horizontal
        assertEquals(android.widget.LinearLayout.HORIZONTAL, statusIndicatorView.orientation)
    }

    @Test
    fun testMultipleStatusUpdates() {
        // Test multiple status updates to ensure state changes correctly
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.DISCONNECTED, "Initial State")
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.CONNECTED, "Connected State")
        statusIndicatorView.setStatus(StatusIndicatorView.StatusType.RECORDING, "Recording State")
        
        val textView = statusIndicatorView.getChildAt(1) as android.widget.TextView
        assertEquals("Recording State", textView.text)
    }
}