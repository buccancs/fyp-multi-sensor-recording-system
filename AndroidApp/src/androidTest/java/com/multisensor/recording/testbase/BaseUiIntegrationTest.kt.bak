package com.multisensor.recording.testbase

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.rule.GrantPermissionRule
import com.multisensor.recording.MainActivity
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Rule

/**
 * Base class for UI integration tests
 * 
 * Features:
 * - Activity scenario for UI testing
 * - Hilt dependency injection
 * - Essential permission grants
 * - Common UI testing utilities
 */
@HiltAndroidTest
abstract class BaseUiIntegrationTest : BaseInstrumentedTest() {

    @get:Rule(order = 0)
    override var hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1) 
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    // Grant essential permissions for UI tests
    // Note: Removed deprecated permissions for Android 15+ compatibility
    @get:Rule(order = 2)
    val permissionRule: GrantPermissionRule = GrantPermissionRule.grant(
        android.Manifest.permission.CAMERA,
        android.Manifest.permission.RECORD_AUDIO
    )

    /**
     * Common UI test utilities can be added here
     */
    protected fun waitForUiIdle() {
        Thread.sleep(100) // Simple wait - can be improved with IdlingResource
    }
}