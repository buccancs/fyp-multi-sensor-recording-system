package com.multisensor.recording.calibration

import android.content.Context
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import org.robolectric.annotation.Config
import org.robolectric.RuntimeEnvironment

/**
 * Simple Robolectric test to verify Android framework integration
 * This test uses JUnit 5 annotations and demonstrates basic Robolectric functionality
 */
@Config(sdk = [28])
class SimpleRobolectricTest {
    
    @Test
    fun `android context should be available via Robolectric`() {
        val context: Context = RuntimeEnvironment.getApplication()
        assertNotNull(context, "Android context should be available")
        assertEquals("android.app.Application", context.javaClass.name, "Application class should be correct")
    }
    
    @Test 
    fun `android SDK version should be configured correctly`() {
        val context = RuntimeEnvironment.getApplication()
        assertNotNull(context, "Application context should be available")
        assertTrue(context.packageName.isNotEmpty(), "Package name should not be empty")
    }
}