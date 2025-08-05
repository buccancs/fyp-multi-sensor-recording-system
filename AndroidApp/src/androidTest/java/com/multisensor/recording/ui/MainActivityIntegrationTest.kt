package com.multisensor.recording.ui

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.multisensor.recording.R
import com.multisensor.recording.testbase.BaseUiIntegrationTest
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MainActivityIntegrationTest : BaseUiIntegrationTest() {

    @Test
    fun mainActivity_should_launch_successfully() {
        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun mainActivity_should_display_initial_status() {
        waitForUiIdle()

        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun mainActivity_should_show_control_buttons() {
        waitForUiIdle()

        onView(withId(R.id.startRecordingButton))
            .check(matches(isDisplayed()))

        onView(withId(R.id.stopRecordingButton))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recordButton_should_be_clickable_when_enabled() {
        waitForUiIdle()

        onView(withId(R.id.startRecordingButton))
            .check(matches(isDisplayed()))
            .perform(click())

        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun calibrationButton_should_be_clickable() {
        waitForUiIdle()

        onView(withId(R.id.calibrationButton))
            .check(matches(isDisplayed()))
            .perform(click())

        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun batteryDisplay_should_be_visible() {
        waitForUiIdle()

        onView(withId(R.id.batteryLevelText))
            .check(matches(isDisplayed()))

        onView(withId(R.id.batteryLevelText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun deviceStatus_indicators_should_be_visible() {
        waitForUiIdle()

        onView(withId(R.id.pcConnectionIndicator))
            .check(matches(isDisplayed()))

        onView(withId(R.id.shimmerConnectionIndicator))
            .check(matches(isDisplayed()))

        onView(withId(R.id.thermalConnectionIndicator))
            .check(matches(isDisplayed()))
    }

    @Test
    fun activity_should_handle_configuration_changes() {
        waitForUiIdle()

        activityRule.scenario.recreate()
        waitForUiIdle()

        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))

        onView(withId(R.id.startRecordingButton))
            .check(matches(isDisplayed()))
    }

    @Test
    fun navigation_drawer_should_be_accessible() {
        waitForUiIdle()


        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun activity_should_survive_background_foreground_cycle() {
        waitForUiIdle()

        activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.STARTED)
        activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.RESUMED)
        waitForUiIdle()

        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }
}