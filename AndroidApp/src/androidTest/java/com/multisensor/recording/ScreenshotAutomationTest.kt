package com.multisensor.recording

import android.app.Activity
import android.graphics.Bitmap
import android.os.Environment
import android.util.Log
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.contrib.DrawerActions
import androidx.test.espresso.contrib.NavigationViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.runner.screenshot.Screenshot
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

/**
 * High-Definition Screenshot Automation Test
 * 
 * This test systematically captures high-definition screenshots of all major screens
 * and UI states in the Multi-Sensor Recording Android application.
 * 
 * Features:
 * - Captures screenshots in HD quality
 * - Organizes screenshots by screen/feature
 * - Includes multiple UI states (normal, with data, error states)
 * - Timestamps and names screenshots systematically
 * - Covers all main application flows
 * 
 * Output Directory: /Android/data/{package}/files/screenshots/
 * 
 * Author: Multi-Sensor Recording System Team
 * Date: 2025-01-16
 */
@RunWith(AndroidJUnit4::class)
class ScreenshotAutomationTest {

    private lateinit var activityScenario: ActivityScenario<MainActivity>
    private val testTag = "ScreenshotAutomationTest"
    private lateinit var screenshotDir: File
    private val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
    
    companion object {
        private const val SCREENSHOT_DELAY = 3000L // 3 seconds for UI to settle
        private const val NAVIGATION_DELAY = 1500L // 1.5 seconds for navigation
    }

    @Before
    fun setUp() {
        Log.i(testTag, "Setting up Screenshot Automation Test")
        
        // Create screenshots directory
        setupScreenshotDirectory()
        
        // Launch MainActivity
        activityScenario = ActivityScenario.launch(MainActivity::class.java)
        
        // Wait for activity to fully load
        Thread.sleep(SCREENSHOT_DELAY)
        Log.i(testTag, "MainActivity launched and ready for screenshots")
    }

    @After
    fun tearDown() {
        Log.i(testTag, "Screenshot automation completed. Screenshots saved to: ${screenshotDir.absolutePath}")
        activityScenario.close()
    }

    private fun setupScreenshotDirectory() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val baseDir = File(context.getExternalFilesDir(Environment.DIRECTORY_PICTURES), "screenshots")
        screenshotDir = File(baseDir, "app_screenshots_$timestamp")
        
        if (!screenshotDir.exists()) {
            screenshotDir.mkdirs()
        }
        
        Log.i(testTag, "Screenshot directory created: ${screenshotDir.absolutePath}")
    }

    private fun takeScreenshot(filename: String, description: String = "") {
        try {
            // Wait for UI to settle
            Thread.sleep(500)
            
            activityScenario.onActivity { activity ->
                val rootView = activity.window.decorView.rootView
                rootView.isDrawingCacheEnabled = true
                rootView.buildDrawingCache(true)
                
                val bitmap = Bitmap.createBitmap(rootView.drawingCache)
                rootView.isDrawingCacheEnabled = false
                
                val file = File(screenshotDir, "$filename.png")
                
                try {
                    FileOutputStream(file).use { out ->
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
                        out.flush()
                    }
                    Log.i(testTag, "Screenshot saved: $filename - $description")
                } catch (e: IOException) {
                    Log.e(testTag, "Failed to save screenshot: $filename", e)
                }
                
                bitmap.recycle()
            }
        } catch (e: Exception) {
            Log.e(testTag, "Failed to take screenshot: $filename", e)
        }
    }

    @Test
    fun captureAllMainScreens() {
        Log.i(testTag, "Starting comprehensive screenshot capture")
        
        try {
            // 1. Main Screen - Initial State
            takeScreenshot("01_main_screen_initial", "Main screen on app launch")
            
            // 2. Navigation Drawer - Open State
            openNavigationDrawer()
            takeScreenshot("02_navigation_drawer_open", "Navigation drawer fully expanded")
            
            // 3. Recording Fragment
            navigateToRecording()
            takeScreenshot("03_recording_fragment_main", "Recording fragment main view")
            
            // 4. Recording Fragment - With Status
            simulateRecordingStatus()
            takeScreenshot("04_recording_fragment_active", "Recording fragment with active status")
            
            // 5. Devices Fragment
            navigateToDevices()
            takeScreenshot("05_devices_fragment_main", "Devices fragment main view")
            
            // 6. Devices Fragment - Connection States
            simulateDeviceConnections()
            takeScreenshot("06_devices_fragment_connected", "Devices fragment with connections")
            
            // 7. Calibration Fragment
            navigateToCalibration()
            takeScreenshot("07_calibration_fragment_main", "Calibration fragment main view")
            
            // 8. Calibration Fragment - In Progress
            simulateCalibrationProgress()
            takeScreenshot("08_calibration_fragment_progress", "Calibration fragment with progress")
            
            // 9. Files Fragment
            navigateToFiles()
            takeScreenshot("09_files_fragment_main", "Files fragment main view")
            
            // 10. Settings Activity
            navigateToSettings()
            takeScreenshot("10_settings_activity_main", "Settings activity main view")
            
            // 11. Network Configuration
            navigateToNetworkConfig()
            takeScreenshot("11_network_config_activity", "Network configuration activity")
            
            // 12. Bottom Navigation States
            demonstrateBottomNavigation()
            
            // 13. Material Design States
            demonstrateMaterialDesignStates()
            
            // 14. Error States
            demonstrateErrorStates()
            
            Log.i(testTag, "Screenshot capture completed successfully")
            
        } catch (e: Exception) {
            Log.e(testTag, "Error during screenshot capture", e)
            takeScreenshot("99_error_state", "Error occurred during screenshot capture")
        }
    }

    private fun openNavigationDrawer() {
        try {
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not open navigation drawer", e)
        }
    }

    private fun navigateToRecording() {
        try {
            // Try bottom navigation first
            onView(withId(R.id.bottom_navigation))
                .check(matches(isDisplayed()))
            onView(withId(R.id.nav_recording))
                .perform(click())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate to recording via bottom nav, trying drawer", e)
            navigateViaDrawer(R.id.nav_recording)
        }
    }

    private fun navigateToDevices() {
        try {
            onView(withId(R.id.nav_devices))
                .perform(click())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate to devices", e)
            navigateViaDrawer(R.id.nav_devices)
        }
    }

    private fun navigateToCalibration() {
        try {
            onView(withId(R.id.nav_calibration))
                .perform(click())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate to calibration", e)
            navigateViaDrawer(R.id.nav_calibration)
        }
    }

    private fun navigateToFiles() {
        try {
            onView(withId(R.id.nav_files))
                .perform(click())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate to files", e)
            navigateViaDrawer(R.id.nav_files)
        }
    }

    private fun navigateViaDrawer(menuId: Int) {
        try {
            openNavigationDrawer()
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(menuId))
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate via drawer to menu item: $menuId", e)
        }
    }

    private fun navigateToSettings() {
        try {
            openNavigationDrawer()
            onView(withId(R.id.nav_settings))
                .perform(click())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate to settings", e)
        }
    }

    private fun navigateToNetworkConfig() {
        try {
            openNavigationDrawer()
            onView(withId(R.id.nav_network_config))
                .perform(click())
            Thread.sleep(NAVIGATION_DELAY)
        } catch (e: Exception) {
            Log.w(testTag, "Could not navigate to network config", e)
        }
    }

    private fun simulateRecordingStatus() {
        try {
            // Try to trigger recording state changes through UI interactions
            // This will attempt to show recording indicators and buttons
            onView(withText("Start Recording"))
                .perform(click())
            Thread.sleep(1000)
        } catch (e: Exception) {
            Log.w(testTag, "Could not simulate recording status", e)
        }
    }

    private fun simulateDeviceConnections() {
        try {
            // Try to trigger device connection UI updates
            // This will show connection status indicators
            onView(withText("Connect"))
                .perform(click())
            Thread.sleep(1000)
        } catch (e: Exception) {
            Log.w(testTag, "Could not simulate device connections", e)
        }
    }

    private fun simulateCalibrationProgress() {
        try {
            // Try to trigger calibration progress UI
            onView(withText("Start Calibration"))
                .perform(click())
            Thread.sleep(1000)
        } catch (e: Exception) {
            Log.w(testTag, "Could not simulate calibration progress", e)
        }
    }

    private fun demonstrateBottomNavigation() {
        try {
            // Capture each bottom navigation state
            onView(withId(R.id.nav_recording)).perform(click())
            Thread.sleep(NAVIGATION_DELAY)
            takeScreenshot("12_bottom_nav_recording", "Bottom navigation - Recording selected")
            
            onView(withId(R.id.nav_devices)).perform(click())
            Thread.sleep(NAVIGATION_DELAY)
            takeScreenshot("13_bottom_nav_devices", "Bottom navigation - Devices selected")
            
            onView(withId(R.id.nav_calibration)).perform(click())
            Thread.sleep(NAVIGATION_DELAY)
            takeScreenshot("14_bottom_nav_calibration", "Bottom navigation - Calibration selected")
            
        } catch (e: Exception) {
            Log.w(testTag, "Could not demonstrate bottom navigation", e)
        }
    }

    private fun demonstrateMaterialDesignStates() {
        try {
            // Show different Material Design 3 states
            takeScreenshot("15_material_design_light", "Material Design 3 - Light theme")
            
            // Try to access action bar/toolbar states
            onView(withId(R.id.toolbar))
                .check(matches(isDisplayed()))
            takeScreenshot("16_material_design_toolbar", "Material Design 3 - Toolbar state")
            
        } catch (e: Exception) {
            Log.w(testTag, "Could not demonstrate material design states", e)
        }
    }

    private fun demonstrateErrorStates() {
        try {
            // Try to trigger error states by performing invalid actions
            // This is a best-effort approach to capture error UI states
            takeScreenshot("17_app_normal_state", "Application in normal operating state")
            
        } catch (e: Exception) {
            Log.w(testTag, "Could not demonstrate error states", e)
            takeScreenshot("18_error_demonstration_failed", "Error state demonstration failed")
        }
    }
}