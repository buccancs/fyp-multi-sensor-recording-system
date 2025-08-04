package com.multisensor.recording

import android.app.Activity
import android.graphics.Bitmap
import android.os.Environment
import android.util.Log
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
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
 * Simple Screenshot Test for Android Application
 * 
 * A simplified version that captures basic app screenshots without
 * complex dependencies, suitable for initial screenshot generation.
 */
@RunWith(AndroidJUnit4::class)
class SimpleScreenshotTest {

    private lateinit var activityScenario: ActivityScenario<MainActivity>
    private val testTag = "SimpleScreenshotTest"
    private lateinit var screenshotDir: File
    private val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())

    @Before
    fun setUp() {
        Log.i(testTag, "Setting up Simple Screenshot Test")
        
        // Create screenshots directory
        setupScreenshotDirectory()
        
        // Launch MainActivity
        activityScenario = ActivityScenario.launch(MainActivity::class.java)
        
        // Wait for activity to fully load
        Thread.sleep(3000)
        Log.i(testTag, "MainActivity launched successfully")
    }

    @After
    fun tearDown() {
        Log.i(testTag, "Simple screenshot test completed. Screenshots saved to: ${screenshotDir.absolutePath}")
        activityScenario.close()
    }

    private fun setupScreenshotDirectory() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val baseDir = File(context.getExternalFilesDir(Environment.DIRECTORY_PICTURES), "screenshots")
        screenshotDir = File(baseDir, "simple_screenshots_$timestamp")
        
        if (!screenshotDir.exists()) {
            screenshotDir.mkdirs()
        }
        
        Log.i(testTag, "Screenshot directory created: ${screenshotDir.absolutePath}")
    }

    private fun takeScreenshot(filename: String, description: String = "") {
        try {
            // Wait for UI to settle
            Thread.sleep(1000)
            
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
    fun captureBasicScreenshots() {
        Log.i(testTag, "Starting basic screenshot capture")
        
        try {
            // 1. Main Screen - Initial State
            takeScreenshot("01_main_screen_initial", "Main screen on app launch")
            
            // 2. Try to access main UI elements
            try {
                // Check if toolbar is present
                onView(withId(R.id.toolbar)).check(matches(isDisplayed()))
                takeScreenshot("02_main_screen_with_toolbar", "Main screen showing toolbar")
            } catch (e: Exception) {
                Log.w(testTag, "Toolbar not found, continuing...", e)
            }
            
            // 3. Try to open navigation drawer if it exists
            try {
                // Look for drawer layout
                onView(withId(R.id.drawer_layout)).check(matches(isDisplayed()))
                takeScreenshot("03_main_screen_with_drawer", "Main screen with drawer available")
            } catch (e: Exception) {
                Log.w(testTag, "Drawer layout not found, continuing...", e)
            }
            
            // 4. Try bottom navigation if it exists
            try {
                onView(withId(R.id.bottom_navigation)).check(matches(isDisplayed()))
                takeScreenshot("04_main_screen_with_bottom_nav", "Main screen with bottom navigation")
            } catch (e: Exception) {
                Log.w(testTag, "Bottom navigation not found, continuing...", e)
            }
            
            // 5. Try to access navigation host fragment
            try {
                onView(withId(R.id.nav_host_fragment)).check(matches(isDisplayed()))
                takeScreenshot("05_main_screen_with_fragments", "Main screen with fragment container")
            } catch (e: Exception) {
                Log.w(testTag, "Fragment container not found, continuing...", e)
            }
            
            // 6. Take a final screenshot after any interactions
            takeScreenshot("06_main_screen_final", "Final main screen state")
            
            Log.i(testTag, "Basic screenshot capture completed successfully")
            
        } catch (e: Exception) {
            Log.e(testTag, "Error during screenshot capture", e)
            takeScreenshot("99_error_state", "Error occurred during screenshot capture")
        }
    }

    @Test
    fun captureAppIcon() {
        Log.i(testTag, "Capturing app icon and basic info")
        
        try {
            // Take screenshot of the main screen for app icon purposes
            takeScreenshot("app_icon_screenshot", "Screenshot for app icon extraction")
            
            // Try to capture any splash screen or loading state
            Thread.sleep(2000)
            takeScreenshot("app_loaded_state", "App in loaded state")
            
        } catch (e: Exception) {
            Log.e(testTag, "Error capturing app icon", e)
        }
    }
}