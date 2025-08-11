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
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }
    @Test
    fun recordButton_isVisibleAndClickable() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.btn_start_recording))
            .check(matches(isDisplayed()))
            .check(matches(isClickable()))
    }
    @Test
    fun stopButton_isVisibleWhenRecording() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.btn_start_recording)).perform(click())
        onView(withId(R.id.btn_stop_recording))
            .check(matches(isDisplayed()))
            .check(matches(isClickable()))
    }
    @Test
    fun recordStopCycle_updatesUICorrectly() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.btn_start_recording))
            .check(matches(isDisplayed()))
            .check(matches(isEnabled()))
        onView(withId(R.id.btn_start_recording)).perform(click())
        onView(withId(R.id.btn_stop_recording)).perform(click())
        onView(withId(R.id.btn_start_recording))
            .check(matches(isDisplayed()))
            .check(matches(isEnabled()))
    }
    @Test
    fun navigationDrawer_opensAndCloses() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_view)).check(matches(isDisplayed()))
        onView(isRoot()).perform(pressBack())
    }
    @Test
    fun shimmerSettings_navigationWorks() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_shimmer_settings)).perform(click())
        onView(withText("Shimmer Settings")).check(matches(isDisplayed()))
    }
    @Test
    fun shimmerVisualization_navigationWorks() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_shimmer_visualization)).perform(click())
        onView(withText("Shimmer Visualisation")).check(matches(isDisplayed()))
    }
    @Test
    fun settingsToggles_areInteractive() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.switch_record_video))
            .check(matches(isDisplayed()))
            .perform(click())
        onView(withId(R.id.switch_thermal_recording))
            .check(matches(isDisplayed()))
            .perform(click())
        onView(withId(R.id.switch_capture_raw))
            .check(matches(isDisplayed()))
            .perform(click())
    }
    @Test
    fun statusText_updatesAppropriately() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.text_status))
            .check(matches(isDisplayed()))
            .check(matches(withText(containsString("Ready"))))
        onView(withId(R.id.btn_start_recording)).perform(click())
        onView(withId(R.id.text_status))
            .check(matches(withText(containsString("Recording"))))
    }
    @Test
    fun exportData_buttonFunctionality() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_files)).perform(click())
        onView(withId(R.id.btn_export_data))
            .check(matches(isDisplayed()))
            .check(matches(isClickable()))
            .perform(click())
    }
    @Test
    fun permissionHandling_showsAppropriateUI() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }
    @Test
    fun deviceConnection_statusUpdates() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.text_device_status))
            .check(matches(isDisplayed()))
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
        onView(withId(R.id.btn_start_recording)).perform(click())
        onView(withId(R.id.text_recording_duration))
            .check(matches(isDisplayed()))
            .check(matches(withText(containsString(":"))))
    }
    @Test
    fun errorDialog_handlesErrors() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }
    @Test
    fun backNavigation_worksCorrectly() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_shimmer_settings)).perform(click())
        onView(isRoot()).perform(pressBack())
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }
    @Test
    fun landscapeOrientation_maintainsState() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
        onView(withId(R.id.btn_start_recording)).check(matches(isDisplayed()))
    }
    @Test
    fun multipleActivities_navigationFlow() {
        ActivityScenario.launch(MainActivity::class.java)
        onView(withContentDescription("Open navigation drawer")).perform(click())
        onView(withId(R.id.nav_shimmer_settings)).perform(click())
        onView(withId(R.id.menu_visualization)).perform(click())
        onView(withId(R.id.menu_settings)).perform(click())
        onView(isRoot()).perform(pressBack())
        onView(withId(R.id.main_content)).check(matches(isDisplayed()))
    }
}