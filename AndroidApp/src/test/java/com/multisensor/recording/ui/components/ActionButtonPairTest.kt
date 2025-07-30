package com.multisensor.recording.ui.components

import android.content.Context
import android.widget.Button
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.*
import org.mockito.Mockito.*

/**
 * Unit tests for ActionButtonPair component
 * Ensures proper functionality and styling of button pairs
 */
@RunWith(AndroidJUnit4::class)
class ActionButtonPairTest {

    private lateinit var context: Context
    private lateinit var actionButtonPair: ActionButtonPair

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        actionButtonPair = ActionButtonPair(context)
    }

    @Test
    fun testInitialState() {
        // Test that the component initializes correctly
        assertNotNull(actionButtonPair)
        assertEquals(2, actionButtonPair.childCount)
        
        // Verify both children are buttons
        assertTrue(actionButtonPair.getChildAt(0) is Button)
        assertTrue(actionButtonPair.getChildAt(1) is Button)
    }

    @Test
    fun testSetButtons() {
        // Test setting button text and styles
        actionButtonPair.setButtons(
            "Start Recording",
            "Stop Recording",
            ActionButtonPair.ButtonStyle.PRIMARY,
            ActionButtonPair.ButtonStyle.SECONDARY
        )
        
        val leftButton = actionButtonPair.getLeftButton()
        val rightButton = actionButtonPair.getRightButton()
        
        assertEquals("Start Recording", leftButton.text)
        assertEquals("Stop Recording", rightButton.text)
    }

    @Test
    fun testSetButtonsWithDefaultStyles() {
        // Test setting buttons with default styles
        actionButtonPair.setButtons("Connect", "Disconnect")
        
        val leftButton = actionButtonPair.getLeftButton()
        val rightButton = actionButtonPair.getRightButton()
        
        assertEquals("Connect", leftButton.text)
        assertEquals("Disconnect", rightButton.text)
    }

    @Test
    fun testSetButtonsWithAllStyles() {
        // Test all button styles
        val styles = arrayOf(
            ActionButtonPair.ButtonStyle.PRIMARY,
            ActionButtonPair.ButtonStyle.SECONDARY,
            ActionButtonPair.ButtonStyle.NEUTRAL,
            ActionButtonPair.ButtonStyle.WARNING
        )
        
        for (leftStyle in styles) {
            for (rightStyle in styles) {
                actionButtonPair.setButtons("Left", "Right", leftStyle, rightStyle)
                // Verify buttons are set (color verification would require more complex setup)
                assertEquals("Left", actionButtonPair.getLeftButton().text)
                assertEquals("Right", actionButtonPair.getRightButton().text)
            }
        }
    }

    @Test
    fun testSetOnClickListeners() {
        // Test setting click listeners
        var leftClicked = false
        var rightClicked = false
        
        val leftListener = android.view.View.OnClickListener { leftClicked = true }
        val rightListener = android.view.View.OnClickListener { rightClicked = true }
        
        actionButtonPair.setOnClickListeners(leftListener, rightListener)
        
        // Simulate clicks
        actionButtonPair.getLeftButton().performClick()
        actionButtonPair.getRightButton().performClick()
        
        assertTrue(leftClicked)
        assertTrue(rightClicked)
    }

    @Test
    fun testSetOnClickListenersWithNull() {
        // Test setting null click listeners
        actionButtonPair.setOnClickListeners(null, null)
        
        // Should not throw exception
        actionButtonPair.getLeftButton().performClick()
        actionButtonPair.getRightButton().performClick()
    }

    @Test
    fun testSetButtonsEnabled() {
        // Test enabling/disabling buttons
        actionButtonPair.setButtonsEnabled(true, false)
        
        assertTrue(actionButtonPair.getLeftButton().isEnabled)
        assertFalse(actionButtonPair.getRightButton().isEnabled)
        
        actionButtonPair.setButtonsEnabled(false, true)
        
        assertFalse(actionButtonPair.getLeftButton().isEnabled)
        assertTrue(actionButtonPair.getRightButton().isEnabled)
    }

    @Test
    fun testGetLeftButton() {
        // Test getting left button reference
        val leftButton = actionButtonPair.getLeftButton()
        assertNotNull(leftButton)
        assertTrue(leftButton is Button)
        assertEquals(actionButtonPair.getChildAt(0), leftButton)
    }

    @Test
    fun testGetRightButton() {
        // Test getting right button reference
        val rightButton = actionButtonPair.getRightButton()
        assertNotNull(rightButton)
        assertTrue(rightButton is Button)
        assertEquals(actionButtonPair.getChildAt(1), rightButton)
    }

    @Test
    fun testLayoutOrientation() {
        // Test that the layout is horizontal
        assertEquals(android.widget.LinearLayout.HORIZONTAL, actionButtonPair.orientation)
    }

    @Test
    fun testButtonLayoutParams() {
        // Test that buttons have correct layout parameters
        val leftButton = actionButtonPair.getLeftButton()
        val rightButton = actionButtonPair.getRightButton()
        
        val leftParams = leftButton.layoutParams as android.widget.LinearLayout.LayoutParams
        val rightParams = rightButton.layoutParams as android.widget.LinearLayout.LayoutParams
        
        // Both buttons should have equal weight
        assertEquals(1f, leftParams.weight, 0.01f)
        assertEquals(1f, rightParams.weight, 0.01f)
        
        // Width should be 0 (for weight distribution)
        assertEquals(0, leftParams.width)
        assertEquals(0, rightParams.width)
    }

    @Test
    fun testRecordingButtonScenario() {
        // Test typical recording button scenario
        actionButtonPair.setButtons("Start Recording", "Stop Recording")
        actionButtonPair.setButtonsEnabled(true, false) // Initially only start is enabled
        
        var recordingStarted = false
        var recordingStopped = false
        
        actionButtonPair.setOnClickListeners(
            { 
                recordingStarted = true
                actionButtonPair.setButtonsEnabled(false, true) // Switch to stop enabled
            },
            { 
                recordingStopped = true
                actionButtonPair.setButtonsEnabled(true, false) // Switch back to start enabled
            }
        )
        
        // Simulate start recording
        actionButtonPair.getLeftButton().performClick()
        assertTrue(recordingStarted)
        assertFalse(actionButtonPair.getLeftButton().isEnabled)
        assertTrue(actionButtonPair.getRightButton().isEnabled)
        
        // Simulate stop recording
        actionButtonPair.getRightButton().performClick()
        assertTrue(recordingStopped)
        assertTrue(actionButtonPair.getLeftButton().isEnabled)
        assertFalse(actionButtonPair.getRightButton().isEnabled)
    }

    @Test
    fun testConnectDisconnectScenario() {
        // Test typical connect/disconnect button scenario
        actionButtonPair.setButtons(
            "Connect",
            "Disconnect",
            ActionButtonPair.ButtonStyle.PRIMARY,
            ActionButtonPair.ButtonStyle.SECONDARY
        )
        
        var connected = false
        
        actionButtonPair.setOnClickListeners(
            { 
                connected = true
                actionButtonPair.setButtonsEnabled(false, true)
            },
            { 
                connected = false
                actionButtonPair.setButtonsEnabled(true, false)
            }
        )
        
        // Test connection flow
        actionButtonPair.getLeftButton().performClick()
        assertTrue(connected)
        
        actionButtonPair.getRightButton().performClick()
        assertFalse(connected)
    }

    @Test
    fun testMultipleStyleChanges() {
        // Test changing styles multiple times
        actionButtonPair.setButtons("Test1", "Test2", ActionButtonPair.ButtonStyle.PRIMARY, ActionButtonPair.ButtonStyle.SECONDARY)
        actionButtonPair.setButtons("Test3", "Test4", ActionButtonPair.ButtonStyle.NEUTRAL, ActionButtonPair.ButtonStyle.WARNING)
        actionButtonPair.setButtons("Test5", "Test6", ActionButtonPair.ButtonStyle.WARNING, ActionButtonPair.ButtonStyle.PRIMARY)
        
        assertEquals("Test5", actionButtonPair.getLeftButton().text)
        assertEquals("Test6", actionButtonPair.getRightButton().text)
    }
}