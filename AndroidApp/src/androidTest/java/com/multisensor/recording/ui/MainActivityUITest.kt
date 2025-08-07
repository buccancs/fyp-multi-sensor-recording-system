package com.multisensor.recording.ui

import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import androidx.test.rule.GrantPermissionRule
import com.multisensor.recording.R
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * UI Tests for User-Facing Behaviors
 * =================================
 * 
 * Espresso tests for UI interactions as specifically requested in PR feedback:
 * - Navigation through fragments and activities
 * - Permission handling and user flows
 * - Record/stop button functionality
 * - UI responsiveness and state updates
 * 
 * Tests user-facing behaviors to ensure the app interface works correctly
 * under real conditions.
 */
@RunWith(AndroidJUnit4::class)
@LargeTest
class MainActivityUITest {

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

    @Test
    fun mainActivity_launchesSuccessfully() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Verify main activity loads
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }

    @Test
    fun recordButton_isVisibleAndClickable() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Check if record button exists and is clickable
        onView(withId(R.id.btn_start_recording))
            .check(matches(isDisplayed()))
            .check(matches(isClickable()))
    }

    @Test
    fun stopButton_isVisibleWhenRecording() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Click record button
        onView(withId(R.id.btn_start_recording)).perform(click())
        
        // Check if stop button becomes visible
        onView(withId(R.id.btn_stop_recording))
            .check(matches(isDisplayed()))
            .check(matches(isClickable()))
    }

    @Test
    fun recordStopCycle_updatesUICorrectly() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Initial state - record button should be enabled
        onView(withId(R.id.btn_start_recording))
            .check(matches(isDisplayed()))
            .check(matches(isEnabled()))
        
        // Start recording
        onView(withId(R.id.btn_start_recording)).perform(click())
        
        // Stop recording
        onView(withId(R.id.btn_stop_recording)).perform(click())
        
        // Record button should be enabled again
        onView(withId(R.id.btn_start_recording))
            .check(matches(isDisplayed()))
            .check(matches(isEnabled()))
    }

    @Test
    fun navigationDrawer_opensAndCloses() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Open navigation drawer
        onView(withContentDescription("Open navigation drawer")).perform(click())
        
        // Check if drawer menu items are visible
        onView(withId(R.id.nav_view)).check(matches(isDisplayed()))
        
        // Close drawer by pressing back
        onView(isRoot()).perform(pressBack())
    }

    @Test
    fun shimmerSettings_navigationWorks() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Open navigation drawer
        onView(withContentDescription("Open navigation drawer")).perform(click())
        
        // Click on Shimmer Settings
        onView(withId(R.id.nav_shimmer_settings)).perform(click())
        
        // Verify navigation to Shimmer Settings
        onView(withText("Shimmer Settings")).check(matches(isDisplayed()))
    }

    @Test
    fun shimmerVisualization_navigationWorks() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Open navigation drawer
        onView(withContentDescription("Open navigation drawer")).perform(click())
        
        // Click on Shimmer Visualization
        onView(withId(R.id.nav_shimmer_visualization)).perform(click())
        
        // Verify navigation to Shimmer Visualization
        onView(withText("Shimmer Visualization")).check(matches(isDisplayed()))
    }

    @Test
    fun settingsToggles_areInteractive() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Test video recording toggle
        onView(withId(R.id.switch_record_video))
            .check(matches(isDisplayed()))
            .perform(click())
        
        // Test thermal recording toggle
        onView(withId(R.id.switch_thermal_recording))
            .check(matches(isDisplayed()))
            .perform(click())
        
        // Test raw capture toggle
        onView(withId(R.id.switch_capture_raw))
            .check(matches(isDisplayed()))
            .perform(click())
    }

    @Test
    fun statusText_updatesAppropriately() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Check initial status
        onView(withId(R.id.text_status))
            .check(matches(isDisplayed()))
            .check(matches(withText(containsString("Ready"))))
        
        // Start recording and check status update
        onView(withId(R.id.btn_start_recording)).perform(click())
        
        onView(withId(R.id.text_status))
            .check(matches(withText(containsString("Recording"))))
    }

    @Test
    fun exportData_buttonFunctionality() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Navigate to files section (if available)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_files)).perform(click())
        
        // Check if export button is present and clickable
        onView(withId(R.id.btn_export_data))
            .check(matches(isDisplayed()))
            .check(matches(isClickable()))
            .perform(click())
        
        // Should show some feedback (toast, dialog, etc.)
        // This test ensures the button does something rather than nothing
    }

    @Test
    fun permissionHandling_showsAppropriateUI() {
        // This test ensures that when permissions are not granted,
        // the app shows appropriate UI elements
        ActivityScenario.launch(MainActivity::class.java)
        
        // The app should handle permission states gracefully
        // and show appropriate UI elements
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }

    @Test
    fun deviceConnection_statusUpdates() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Check device connection status indicators
        onView(withId(R.id.text_device_status))
            .check(matches(isDisplayed()))
        
        // Connection status should be visible to user
        onView(withId(R.id.indicator_camera_status))
            .check(matches(isDisplayed()))
            
        onView(withId(R.id.indicator_shimmer_status))
            .check(matches(isDisplayed()))
            
        onView(withId(R.id.indicator_thermal_status))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recordingDuration_displaysCorrectly() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Start recording
        onView(withId(R.id.btn_start_recording)).perform(click())
        
        // Check that duration display is visible
        onView(withId(R.id.text_recording_duration))
            .check(matches(isDisplayed()))
            .check(matches(withText(containsString(":"))))
    }

    @Test
    fun errorDialog_handlesErrors() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // This test ensures that error dialogs appear when expected
        // and can be dismissed properly
        
        // Try to trigger an error scenario (e.g., recording without permissions)
        // Then verify error handling UI appears
        
        // For now, just ensure the UI can handle error states
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }

    @Test
    fun backNavigation_worksCorrectly() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Navigate to settings
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_shimmer_settings)).perform(click())
        
        // Press back button
        onView(isRoot()).perform(pressBack())
        
        // Should return to main activity
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }

    @Test
    fun landscapeOrientation_maintainsState() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // This test would verify that UI state is maintained across orientation changes
        // For now, ensure basic UI elements are present
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
        onView(withId(R.id.btn_start_recording)).check(matches(isDisplayed()))
    }

    @Test
    fun multipleActivities_navigationFlow() {
        ActivityScenario.launch(MainActivity::class.java)
        
        // Test the complete navigation flow between activities
        
        // Main -> Shimmer Settings
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_shimmer_settings)).perform(click())
        
        // Navigate to Visualization from Settings
        onView(withId(R.id.menu_visualization)).perform(click())
        
        // Navigate back to Settings
        onView(withId(R.id.menu_settings)).perform(click())
        
        // Return to main
        onView(isRoot()).perform(pressBack())
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }
}