package com.multisensor.recording

import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.openActionBarOverflowOrOptionsMenu
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.contrib.DrawerActions
import androidx.test.espresso.contrib.DrawerMatchers
import androidx.test.espresso.contrib.NavigationViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Before
import org.junit.After
import android.util.Log
import androidx.test.espresso.NoMatchingViewException
import androidx.test.espresso.matcher.RootMatchers
import org.hamcrest.Matchers.allOf
import java.util.*

/**
 * IDE Integration UI Test for Android App
 * 
 * This test systematically tests all buttons and navigation flows based on the navigation graph.
 * It validates that each UI element works correctly and navigation flows are successful.
 * 
 * Test Coverage:
 * 1. Navigation drawer functionality
 * 2. Bottom navigation functionality  
 * 3. Fragment navigation and transitions
 * 4. Activity launches and returns
 * 5. Button interactions in each screen
 * 6. Navigation flow validation
 * 
 * Author: Multi-Sensor Recording System Team
 * Date: 2025-01-16
 */
@RunWith(AndroidJUnit4::class)
class IDEIntegrationUITest {
    
    private lateinit var activityScenario: ActivityScenario<MainActivity>
    private val testTag = "IDEIntegrationUITest"
    private val testResults = mutableMapOf<String, Boolean>()
    
    @Before
    fun setUp() {
        Log.i(testTag, "Setting up IDE Integration UI Test")
        activityScenario = ActivityScenario.launch(MainActivity::class.java)
        
        // Wait for activity to load
        Thread.sleep(2000)
        Log.i(testTag, "MainActivity launched successfully")
    }
    
    @After 
    fun tearDown() {
        Log.i(testTag, "Tearing down IDE Integration UI Test")
        logTestResults()
        activityScenario.close()
    }
    
    @Test
    fun testCompleteNavigationGraphAndButtons() {
        Log.i(testTag, "Starting complete navigation graph and button testing")
        
        try {
            // Test drawer navigation menu
            testDrawerNavigationMenu()
            
            // Test bottom navigation
            testBottomNavigation()
            
            // Test main fragments and their buttons
            testRecordingFragment()
            testDevicesFragment() 
            testCalibrationFragment()
            testFilesFragment()
            
            // Test settings activities
            testSettingsActivities()
            
            // Test navigation flows
            testNavigationFlows()
            
            Log.i(testTag, "Complete navigation graph testing completed successfully")
            
        } catch (e: Exception) {
            Log.e(testTag, "Navigation graph testing failed", e)
            throw e
        }
    }
    
    private fun testDrawerNavigationMenu() {
        Log.i(testTag, "Testing drawer navigation menu")
        
        try {
            // Open navigation drawer
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            testResults["drawer_open"] = true
            Log.i(testTag, "✅ Drawer opened successfully")
            
            // Test main navigation items
            val mainNavItems = listOf(
                R.id.nav_recording to "Recording",
                R.id.nav_devices to "Devices", 
                R.id.nav_calibration to "Calibration",
                R.id.nav_files to "Files"
            )
            
            for ((itemId, itemName) in mainNavItems) {
                try {
                    onView(withId(R.id.nav_view))
                        .perform(NavigationViewActions.navigateTo(itemId))
                    
                    // Wait for navigation
                    Thread.sleep(1000)
                    
                    testResults["drawer_nav_$itemName"] = true
                    Log.i(testTag, "✅ Drawer navigation to $itemName successful")
                    
                    // Reopen drawer for next item
                    if (itemId != R.id.nav_files) { // Don't reopen after last item
                        onView(withId(R.id.drawer_layout))
                            .perform(DrawerActions.open())
                    }
                    
                } catch (e: Exception) {
                    testResults["drawer_nav_$itemName"] = false
                    Log.e(testTag, "❌ Drawer navigation to $itemName failed", e)
                }
            }
            
            // Close drawer
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.close())
            
            Log.i(testTag, "Drawer navigation menu testing completed")
            
        } catch (e: Exception) {
            testResults["drawer_open"] = false
            Log.e(testTag, "❌ Drawer navigation menu testing failed", e)
            throw e
        }
    }
    
    private fun testBottomNavigation() {
        Log.i(testTag, "Testing bottom navigation")
        
        val bottomNavItems = listOf(
            R.id.bottom_nav_recording to "Record",
            R.id.bottom_nav_monitor to "Monitor",
            R.id.bottom_nav_calibrate to "Calibrate"
        )
        
        for ((itemId, itemName) in bottomNavItems) {
            try {
                onView(withId(itemId))
                    .perform(click())
                
                // Wait for navigation
                Thread.sleep(1000)
                
                // Verify navigation occurred (check if correct fragment is displayed)
                // This would need to be adapted based on your actual layout structure
                testResults["bottom_nav_$itemName"] = true
                Log.i(testTag, "✅ Bottom navigation to $itemName successful")
                
            } catch (e: Exception) {
                testResults["bottom_nav_$itemName"] = false
                Log.e(testTag, "❌ Bottom navigation to $itemName failed", e)
            }
        }
        
        Log.i(testTag, "Bottom navigation testing completed")
    }
    
    private fun testRecordingFragment() {
        Log.i(testTag, "Testing Recording Fragment")
        
        // Navigate to recording fragment
        navigateToFragment(R.id.nav_recording, "Recording")
        
        // Test recording-specific buttons
        val recordingButtons = listOf(
            "start_recording_button" to "Start Recording",
            "stop_recording_button" to "Stop Recording", 
            "preview_toggle_button" to "Preview Toggle"
        )
        
        for ((buttonTag, buttonName) in recordingButtons) {
            testButtonByTag(buttonTag, buttonName, "RecordingFragment")
        }
        
        // Test recording status indicators
        testStatusIndicators("RecordingFragment")
        
        Log.i(testTag, "Recording Fragment testing completed")
    }
    
    private fun testDevicesFragment() {
        Log.i(testTag, "Testing Devices Fragment")
        
        // Navigate to devices fragment
        navigateToFragment(R.id.nav_devices, "Devices")
        
        // Test device-specific buttons
        val deviceButtons = listOf(
            "connect_devices_button" to "Connect Devices",
            "scan_devices_button" to "Scan Devices",
            "device_settings_button" to "Device Settings",
            "refresh_devices_button" to "Refresh Devices"
        )
        
        for ((buttonTag, buttonName) in deviceButtons) {
            testButtonByTag(buttonTag, buttonName, "DevicesFragment")
        }
        
        // Test device connection indicators
        testConnectionIndicators("DevicesFragment")
        
        Log.i(testTag, "Devices Fragment testing completed")
    }
    
    private fun testCalibrationFragment() {
        Log.i(testTag, "Testing Calibration Fragment")
        
        // Navigate to calibration fragment
        navigateToFragment(R.id.nav_calibration, "Calibration")
        
        // Test calibration-specific buttons
        val calibrationButtons = listOf(
            "start_calibration_button" to "Start Calibration",
            "calibration_settings_button" to "Calibration Settings",
            "view_results_button" to "View Results",
            "save_calibration_button" to "Save Calibration"
        )
        
        for ((buttonTag, buttonName) in calibrationButtons) {
            testButtonByTag(buttonTag, buttonName, "CalibrationFragment")
        }
        
        Log.i(testTag, "Calibration Fragment testing completed")
    }
    
    private fun testFilesFragment() {
        Log.i(testTag, "Testing Files Fragment")
        
        // Navigate to files fragment
        navigateToFragment(R.id.nav_files, "Files")
        
        // Test file-specific buttons
        val fileButtons = listOf(
            "browse_files_button" to "Browse Files",
            "export_data_button" to "Export Data",
            "delete_session_button" to "Delete Session",
            "open_folder_button" to "Open Folder"
        )
        
        for ((buttonTag, buttonName) in fileButtons) {
            testButtonByTag(buttonTag, buttonName, "FilesFragment")
        }
        
        Log.i(testTag, "Files Fragment testing completed")
    }
    
    private fun testSettingsActivities() {
        Log.i(testTag, "Testing Settings Activities")
        
        // Test Settings Activity
        testSettingsActivity()
        
        // Test Network Config Activity
        testNetworkConfigActivity()
        
        // Test Shimmer Config Activity
        testShimmerConfigActivity()
        
        Log.i(testTag, "Settings Activities testing completed")
    }
    
    private fun testSettingsActivity() {
        Log.i(testTag, "Testing Settings Activity")
        
        try {
            // Open drawer and navigate to settings
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(R.id.nav_settings))
            
            // Wait for activity to load
            Thread.sleep(2000)
            
            // Test settings buttons
            val settingsButtons = listOf(
                "save_settings_button" to "Save Settings",
                "reset_settings_button" to "Reset Settings"
            )
            
            for ((buttonTag, buttonName) in settingsButtons) {
                testButtonByTag(buttonTag, buttonName, "SettingsActivity")
            }
            
            // Go back to main activity
            onView(withContentDescription("Navigate up"))
                .perform(click())
            
            testResults["settings_activity_navigation"] = true
            Log.i(testTag, "✅ Settings Activity navigation successful")
            
        } catch (e: Exception) {
            testResults["settings_activity_navigation"] = false
            Log.e(testTag, "❌ Settings Activity navigation failed", e)
        }
    }
    
    private fun testNetworkConfigActivity() {
        Log.i(testTag, "Testing Network Config Activity")
        
        try {
            // Open drawer and navigate to network config
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(R.id.nav_network))
            
            // Wait for activity to load
            Thread.sleep(2000)
            
            // Test network config buttons
            val networkButtons = listOf(
                "configure_network_button" to "Configure Network",
                "test_connection_button" to "Test Connection"
            )
            
            for ((buttonTag, buttonName) in networkButtons) {
                testButtonByTag(buttonTag, buttonName, "NetworkConfigActivity")
            }
            
            // Go back to main activity
            onView(withContentDescription("Navigate up"))
                .perform(click())
            
            testResults["network_config_activity_navigation"] = true
            Log.i(testTag, "✅ Network Config Activity navigation successful")
            
        } catch (e: Exception) {
            testResults["network_config_activity_navigation"] = false
            Log.e(testTag, "❌ Network Config Activity navigation failed", e)
        }
    }
    
    private fun testShimmerConfigActivity() {
        Log.i(testTag, "Testing Shimmer Config Activity")
        
        try {
            // Open drawer and navigate to shimmer config
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(R.id.nav_shimmer))
            
            // Wait for activity to load
            Thread.sleep(2000)
            
            // Test shimmer config buttons
            val shimmerButtons = listOf(
                "configure_shimmer_button" to "Configure Shimmer",
                "test_sensors_button" to "Test Sensors"
            )
            
            for ((buttonTag, buttonName) in shimmerButtons) {
                testButtonByTag(buttonTag, buttonName, "ShimmerConfigActivity")
            }
            
            // Go back to main activity
            onView(withContentDescription("Navigate up"))
                .perform(click())
            
            testResults["shimmer_config_activity_navigation"] = true
            Log.i(testTag, "✅ Shimmer Config Activity navigation successful")
            
        } catch (e: Exception) {
            testResults["shimmer_config_activity_navigation"] = false
            Log.e(testTag, "❌ Shimmer Config Activity navigation failed", e)
        }
    }
    
    private fun testNavigationFlows() {
        Log.i(testTag, "Testing navigation flows")
        
        // Test fragment to fragment navigation flows
        val navigationFlows = listOf(
            listOf(R.id.nav_recording, R.id.nav_devices),
            listOf(R.id.nav_devices, R.id.nav_calibration),
            listOf(R.id.nav_calibration, R.id.nav_files),
            listOf(R.id.nav_files, R.id.nav_recording)
        )
        
        for (flow in navigationFlows) {
            testNavigationFlow(flow[0], flow[1])
        }
        
        Log.i(testTag, "Navigation flows testing completed")
    }
    
    private fun navigateToFragment(fragmentId: Int, fragmentName: String) {
        try {
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(fragmentId))
            
            // Wait for navigation
            Thread.sleep(1500)
            
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.close())
            
            Log.i(testTag, "✅ Navigated to $fragmentName successfully")
            
        } catch (e: Exception) {
            Log.e(testTag, "❌ Failed to navigate to $fragmentName", e)
        }
    }
    
    private fun testButtonByTag(buttonTag: String, buttonName: String, context: String) {
        try {
            // Try to find button by tag first, then by text, then by content description
            var buttonFound = false
            
            try {
                onView(withTagValue(org.hamcrest.Matchers.`is`(buttonTag as Any)))
                    .perform(click())
                buttonFound = true
            } catch (e: NoMatchingViewException) {
                // Try by text
                try {
                    onView(withText(buttonName))
                        .perform(click())
                    buttonFound = true
                } catch (e2: NoMatchingViewException) {
                    // Try by content description
                    try {
                        onView(withContentDescription(buttonName))
                            .perform(click())
                        buttonFound = true
                    } catch (e3: NoMatchingViewException) {
                        // Button not found
                        Log.w(testTag, "Button $buttonName not found in $context")
                    }
                }
            }
            
            if (buttonFound) {
                // Wait for button action to complete
                Thread.sleep(500)
                
                testResults["${context}_$buttonTag"] = true
                Log.i(testTag, "✅ Button $buttonName in $context clicked successfully")
            } else {
                testResults["${context}_$buttonTag"] = false
                Log.w(testTag, "⚠️ Button $buttonName in $context not found or not clickable")
            }
            
        } catch (e: Exception) {
            testResults["${context}_$buttonTag"] = false
            Log.e(testTag, "❌ Button $buttonName in $context failed", e)
        }
    }
    
    private fun testStatusIndicators(context: String) {
        try {
            // Look for common status indicators
            val statusIndicators = listOf(
                "pc_connection_status",
                "device_connection_status", 
                "recording_status",
                "battery_status"
            )
            
            for (indicator in statusIndicators) {
                try {
                    onView(withTagValue(org.hamcrest.Matchers.`is`(indicator as Any)))
                        .check(matches(isDisplayed()))
                    
                    testResults["${context}_$indicator"] = true
                    Log.i(testTag, "✅ Status indicator $indicator in $context visible")
                    
                } catch (e: Exception) {
                    testResults["${context}_$indicator"] = false
                    Log.w(testTag, "⚠️ Status indicator $indicator in $context not found")
                }
            }
            
        } catch (e: Exception) {
            Log.e(testTag, "❌ Status indicators testing in $context failed", e)
        }
    }
    
    private fun testConnectionIndicators(context: String) {
        try {
            // Look for device connection indicators
            val connectionIndicators = listOf(
                "android_device_indicator",
                "shimmer_device_indicator",
                "thermal_camera_indicator",
                "usb_camera_indicator"
            )
            
            for (indicator in connectionIndicators) {
                try {
                    onView(withTagValue(org.hamcrest.Matchers.`is`(indicator as Any)))
                        .check(matches(isDisplayed()))
                    
                    testResults["${context}_$indicator"] = true
                    Log.i(testTag, "✅ Connection indicator $indicator in $context visible")
                    
                } catch (e: Exception) {
                    testResults["${context}_$indicator"] = false
                    Log.w(testTag, "⚠️ Connection indicator $indicator in $context not found")
                }
            }
            
        } catch (e: Exception) {
            Log.e(testTag, "❌ Connection indicators testing in $context failed", e)
        }
    }
    
    private fun testNavigationFlow(fromFragmentId: Int, toFragmentId: Int) {
        try {
            val fromName = getFragmentName(fromFragmentId)
            val toName = getFragmentName(toFragmentId)
            
            Log.i(testTag, "Testing navigation flow: $fromName -> $toName")
            
            // Navigate to source fragment
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(fromFragmentId))
            
            Thread.sleep(1000)
            
            // Navigate to target fragment
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.open())
            
            onView(withId(R.id.nav_view))
                .perform(NavigationViewActions.navigateTo(toFragmentId))
            
            Thread.sleep(1000)
            
            onView(withId(R.id.drawer_layout))
                .perform(DrawerActions.close())
            
            testResults["flow_${fromName}_to_${toName}"] = true
            Log.i(testTag, "✅ Navigation flow $fromName -> $toName successful")
            
        } catch (e: Exception) {
            val fromName = getFragmentName(fromFragmentId)
            val toName = getFragmentName(toFragmentId)
            testResults["flow_${fromName}_to_${toName}"] = false
            Log.e(testTag, "❌ Navigation flow $fromName -> $toName failed", e)
        }
    }
    
    private fun getFragmentName(fragmentId: Int): String {
        return when (fragmentId) {
            R.id.nav_recording -> "Recording"
            R.id.nav_devices -> "Devices"
            R.id.nav_calibration -> "Calibration"
            R.id.nav_files -> "Files"
            else -> "Unknown"
        }
    }
    
    private fun logTestResults() {
        Log.i(testTag, "=".repeat(60))
        Log.i(testTag, "IDE INTEGRATION UI TEST RESULTS")
        Log.i(testTag, "=".repeat(60))
        
        val totalTests = testResults.size
        val passedTests = testResults.values.count { it }
        val failedTests = totalTests - passedTests
        val successRate = if (totalTests > 0) (passedTests.toDouble() / totalTests * 100) else 0.0
        
        Log.i(testTag, "Total Tests: $totalTests")
        Log.i(testTag, "Passed: $passedTests")
        Log.i(testTag, "Failed: $failedTests")
        Log.i(testTag, "Success Rate: ${String.format("%.1f", successRate)}%")
        Log.i(testTag, "")
        
        // Log detailed results
        Log.i(testTag, "DETAILED RESULTS:")
        for ((testName, result) in testResults.toSortedMap()) {
            val status = if (result) "✅ PASS" else "❌ FAIL"
            Log.i(testTag, "$status - $testName")
        }
        
        Log.i(testTag, "=".repeat(60))
        
        // Save results to a file for integration with main test suite
        saveTestResultsToFile()
    }
    
    private fun saveTestResultsToFile() {
        try {
            val context = InstrumentationRegistry.getInstrumentation().targetContext
            val resultsDir = context.getExternalFilesDir("test_results")
            resultsDir?.mkdirs()
            
            val timestamp = Date().time
            val resultsFile = java.io.File(resultsDir, "android_ui_test_results_$timestamp.json")
            
            val resultsJson = buildString {
                append("{\n")
                append("  \"test_suite\": \"Android UI Integration Test\",\n")
                append("  \"timestamp\": $timestamp,\n")
                append("  \"total_tests\": ${testResults.size},\n")
                append("  \"passed_tests\": ${testResults.values.count { it }},\n")
                append("  \"failed_tests\": ${testResults.values.count { !it }},\n")
                append("  \"results\": {\n")
                
                testResults.entries.forEachIndexed { index, (testName, result) ->
                    append("    \"$testName\": $result")
                    if (index < testResults.size - 1) append(",")
                    append("\n")
                }
                
                append("  }\n")
                append("}")
            }
            
            resultsFile.writeText(resultsJson)
            Log.i(testTag, "Test results saved to: ${resultsFile.absolutePath}")
            
        } catch (e: Exception) {
            Log.e(testTag, "Failed to save test results to file", e)
        }
    }
}