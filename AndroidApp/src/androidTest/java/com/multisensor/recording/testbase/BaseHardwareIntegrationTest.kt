package com.multisensor.recording.testbase

import androidx.test.rule.GrantPermissionRule
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Rule

/**
 * Base class for hardware integration tests
 * 
 * Features:
 * - Hilt dependency injection for hardware components
 * - Hardware-specific permission grants
 * - Common hardware testing utilities
 * - Timeout configurations for hardware operations
 */
@HiltAndroidTest
abstract class BaseHardwareIntegrationTest : BaseInstrumentedTest() {

    @get:Rule(order = 0)
    override var hiltRule = HiltAndroidRule(this)

    // Grant hardware-related permissions
    @get:Rule(order = 1)
    val permissionRule: GrantPermissionRule = GrantPermissionRule.grant(
        android.Manifest.permission.CAMERA,
        android.Manifest.permission.RECORD_AUDIO,
        android.Manifest.permission.ACCESS_FINE_LOCATION,
        android.Manifest.permission.ACCESS_COARSE_LOCATION,
        android.Manifest.permission.BLUETOOTH_CONNECT,
        android.Manifest.permission.BLUETOOTH_SCAN,
        android.Manifest.permission.BLUETOOTH_ADVERTISE
    )

    companion object {
        const val HARDWARE_TIMEOUT_MS = 10000L
        const val CONNECTION_TIMEOUT_MS = 5000L
        const val DATA_PROCESSING_TIMEOUT_MS = 3000L
    }

    /**
     * Wait for hardware operations with timeout
     */
    protected fun waitForHardwareOperation(timeoutMs: Long = HARDWARE_TIMEOUT_MS) {
        Thread.sleep(timeoutMs.coerceAtMost(1000)) // Cap at 1 second for tests
    }

    /**
     * Check if hardware is available for testing
     */
    protected fun isHardwareAvailable(): Boolean {
        // Override in specific test classes to check hardware availability
        return true
    }
}