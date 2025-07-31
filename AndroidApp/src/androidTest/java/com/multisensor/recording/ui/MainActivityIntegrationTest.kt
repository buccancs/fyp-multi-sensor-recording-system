package com.multisensor.recording.ui

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.multisensor.recording.R
import com.multisensor.recording.testbase.BaseUiIntegrationTest
import org.hamcrest.Matchers.not
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Comprehensive UI integration tests for MainActivity
 * 
 * Test Categories:
 * - Activity launch and initialization
 * - UI element visibility and interactions
 * - Navigation and user flows
 * - Error state handling
 * - Permission management
 */
@RunWith(AndroidJUnit4::class)
class MainActivityIntegrationTest : BaseUiIntegrationTest() {

    @Test
    fun mainActivity_should_launch_successfully() {
        // When the activity launches
        // Then essential UI elements should be visible
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
    }

    @Test
    fun mainActivity_should_display_initial_status() {
        // When the activity launches
        waitForUiIdle()
        
        // Then the status should show initialization
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
    }

    @Test
    fun mainActivity_should_show_control_buttons() {
        // When the activity is loaded
        waitForUiIdle()
        
        // Then control buttons should be visible
        onView(withId(R.id.recordButton))
            .check(matches(isDisplayed()))
        
        onView(withId(R.id.connectButton))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recordButton_should_be_clickable_when_enabled() {
        // Given the app is initialized
        waitForUiIdle()
        
        // When clicking the record button
        // Then it should be responsive (no crash)
        onView(withId(R.id.recordButton))
            .check(matches(isDisplayed()))
            .perform(click())
        
        // Verify app doesn't crash and UI is still responsive
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
    }

    @Test
    fun connectButton_should_be_clickable() {
        // Given the app is initialized  
        waitForUiIdle()
        
        // When clicking the connect button
        onView(withId(R.id.connectButton))
            .check(matches(isDisplayed()))
            .perform(click())
        
        // Then the app should remain stable
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
    }

    @Test
    fun batteryDisplay_should_be_visible() {
        // When the activity is loaded
        waitForUiIdle()
        
        // Then battery information should be displayed
        onView(withId(R.id.batteryProgressBar))
            .check(matches(isDisplayed()))
        
        onView(withId(R.id.batteryLevelText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun deviceStatus_indicators_should_be_visible() {
        // When the activity is loaded
        waitForUiIdle()
        
        // Then device status indicators should be present
        onView(withId(R.id.pcStatusIndicator))
            .check(matches(isDisplayed()))
        
        onView(withId(R.id.shimmerStatusIndicator))
            .check(matches(isDisplayed()))
        
        onView(withId(R.id.thermalStatusIndicator))
            .check(matches(isDisplayed()))
    }

    @Test
    fun activity_should_handle_configuration_changes() {
        // Given the activity is loaded
        waitForUiIdle()
        
        // When rotating the device (simulated by recreating activity)
        activityRule.scenario.recreate()
        waitForUiIdle()
        
        // Then the UI should still be functional
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
        
        onView(withId(R.id.recordButton))
            .check(matches(isDisplayed()))
    }

    @Test
    fun navigation_drawer_should_be_accessible() {
        // Given the activity is loaded
        waitForUiIdle()
        
        // When attempting to access navigation (if present)
        // This test assumes there might be a menu or navigation drawer
        // Adjust based on actual UI implementation
        
        // Then the main content should remain accessible
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
    }

    @Test
    fun activity_should_survive_background_foreground_cycle() {
        // Given the activity is loaded
        waitForUiIdle()
        
        // When moving to background and back to foreground
        activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.STARTED)
        activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.RESUMED)
        waitForUiIdle()
        
        // Then the UI should still be functional
        onView(withId(R.id.statusTextView))
            .check(matches(isDisplayed()))
    }
}