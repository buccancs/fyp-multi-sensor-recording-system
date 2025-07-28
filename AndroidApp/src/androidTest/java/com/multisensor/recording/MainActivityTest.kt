package com.multisensor.recording

import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.rule.GrantPermissionRule
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Integration tests for MainActivity using Espresso and Hilt
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class MainActivityTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @get:Rule
    val permissionRule: GrantPermissionRule = GrantPermissionRule.grant(
        android.Manifest.permission.CAMERA,
        android.Manifest.permission.RECORD_AUDIO,
        android.Manifest.permission.WRITE_EXTERNAL_STORAGE,
        android.Manifest.permission.READ_EXTERNAL_STORAGE,
        android.Manifest.permission.BLUETOOTH,
        android.Manifest.permission.BLUETOOTH_ADMIN,
        android.Manifest.permission.ACCESS_FINE_LOCATION
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun mainActivity_displaysCorrectInitialState() {
        // Given
        ActivityScenario.launch(MainActivity::class.java)

        // Then
        onView(withId(R.id.startRecordingButton))
            .check(matches(isDisplayed()))
            .check(matches(isEnabled()))

        onView(withId(R.id.stopRecordingButton))
            .check(matches(isDisplayed()))
            .check(matches(not(isEnabled())))

        onView(withId(R.id.calibrationButton))
            .check(matches(isDisplayed()))
            .check(matches(isEnabled()))

        onView(withId(R.id.statusText))
            .check(matches(isDisplayed()))
    }

    @Test
    fun startRecordingButton_updatesUIState() {
        // Given
        ActivityScenario.launch(MainActivity::class.java)

        // When
        onView(withId(R.id.startRecordingButton))
            .perform(click())

        // Then
        // Note: In a real test, we would need to handle the service interaction
        // For now, we just verify the button exists and is clickable
        onView(withId(R.id.startRecordingButton))
            .check(matches(isDisplayed()))
    }

    @Test
    fun calibrationButton_isClickable() {
        // Given
        ActivityScenario.launch(MainActivity::class.java)

        // When
        onView(withId(R.id.calibrationButton))
            .perform(click())

        // Then
        // Verify the button is clickable and doesn't crash the app
        onView(withId(R.id.calibrationButton))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recordingIndicator_isVisible() {
        // Given
        ActivityScenario.launch(MainActivity::class.java)

        // Then
        onView(withId(R.id.recordingIndicator))
            .check(matches(isDisplayed()))
    }

    @Test
    fun previewComponents_areVisible() {
        // Given
        ActivityScenario.launch(MainActivity::class.java)

        // Then
        onView(withId(R.id.rgbPreview))
            .check(matches(isDisplayed()))

        onView(withId(R.id.thermalPreview))
            .check(matches(isDisplayed()))
    }
}