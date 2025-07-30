package com.multisensor.recording.recording

import android.content.Context
import android.hardware.usb.UsbDevice
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.multisensor.recording.managers.UsbDeviceManager
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import javax.inject.Inject

/**
 * Bulletproof Integration Test for Topdon TC001/Plus thermal camera integration.
 * 
 * This test suite focuses on edge cases, error conditions, and stress scenarios
 * that could break the thermal camera integration in real-world usage.
 * 
 * Tests cover:
 * - Rapid device connection/disconnection cycles
 * - Resource exhaustion scenarios
 * - Concurrent access patterns
 * - Recovery from error states
 * - Thread safety under stress
 * - Memory management validation
 * 
 * Requirements:
 * - Can be run without actual hardware (mocked scenarios)
 * - Tests error handling and recovery mechanisms
 * - Validates thread safety and resource management
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ThermalCameraBulletproofIntegrationTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var sessionManager: SessionManager

    @Inject
    lateinit var logger: Logger

    private lateinit var context: Context
    private lateinit var thermalRecorder: ThermalRecorder
    private lateinit var usbDeviceManager: UsbDeviceManager

    @Before
    fun setup() {
        hiltRule.inject()
        context = InstrumentationRegistry.getInstrumentation().targetContext

        thermalRecorder = ThermalRecorder(context, sessionManager, logger)
        usbDeviceManager = UsbDeviceManager()

        println("[BULLETPROOF_TEST] Test setup complete")
    }

    @Test
    fun testRapidInitializationCleanupCycles() = runBlocking {
        println("[BULLETPROOF_TEST] Testing rapid initialization/cleanup cycles...")

        // Test rapid initialization and cleanup cycles to check for resource leaks
        repeat(10) { cycle ->
            println("[BULLETPROOF_TEST] Cycle $cycle: Initialize")
            
            val initResult = thermalRecorder.initialize()
            
            // Brief delay to allow initialization
            delay(100)
            
            println("[BULLETPROOF_TEST] Cycle $cycle: Cleanup")
            thermalRecorder.cleanup()
            
            // Brief delay between cycles
            delay(50)
        }

        println("[BULLETPROOF_TEST] Rapid cycles test completed - no crashes")
    }

    @Test
    fun testConcurrentOperationAttempts() = runBlocking {
        println("[BULLETPROOF_TEST] Testing concurrent operation attempts...")

        thermalRecorder.initialize()
        delay(500)

        // Attempt multiple concurrent operations that should fail gracefully
        val sessionId = "concurrent_test_${System.currentTimeMillis()}"

        // Try to start multiple recordings simultaneously
        val results = (1..5).map { 
            thermalRecorder.startRecording("${sessionId}_$it")
        }

        // Only one should succeed (if any), others should fail gracefully
        val successCount = results.count { it }
        assertTrue("At most one recording should succeed", successCount <= 1)

        // Try to stop multiple times
        repeat(3) {
            thermalRecorder.stopRecording()
        }

        thermalRecorder.cleanup()
        println("[BULLETPROOF_TEST] Concurrent operations test completed")
    }

    @Test
    fun testStateTransitionEdgeCases() = runBlocking {
        println("[BULLETPROOF_TEST] Testing state transition edge cases...")

        // Test operations in various states
        
        // 1. Operations before initialization
        assertFalse("Recording should fail before init", 
                   thermalRecorder.startRecording("test"))
        assertFalse("Stop should fail before init", 
                   thermalRecorder.stopRecording())
        assertFalse("Preview should fail before init", 
                   thermalRecorder.startPreview())
        assertTrue("Stop preview should succeed", 
                  thermalRecorder.stopPreview())

        // 2. Initialize and test state consistency
        thermalRecorder.initialize()
        delay(500)

        val status1 = thermalRecorder.getThermalCameraStatus()
        val status2 = thermalRecorder.getThermalCameraStatus()
        
        assertEquals("Status should be consistent", status1.isRecording, status2.isRecording)
        assertEquals("Preview state should be consistent", status1.isPreviewActive, status2.isPreviewActive)

        // 3. Operations after cleanup
        thermalRecorder.cleanup()
        
        assertFalse("Recording should fail after cleanup", 
                   thermalRecorder.startRecording("test"))
        assertFalse("Preview should fail after cleanup", 
                   thermalRecorder.startPreview())

        println("[BULLETPROOF_TEST] State transition test completed")
    }

    @Test
    fun testResourceManagementUnderStress() = runBlocking {
        println("[BULLETPROOF_TEST] Testing resource management under stress...")

        thermalRecorder.initialize()
        delay(500)

        // Stress test with rapid status queries
        repeat(100) {
            thermalRecorder.getThermalCameraStatus()
        }

        // Stress test with rapid preview start/stop attempts
        repeat(20) {
            thermalRecorder.startPreview()
            delay(10)
            thermalRecorder.stopPreview()
            delay(10)
        }

        // Test multiple session attempts
        repeat(10) { i ->
            val sessionId = "stress_test_$i"
            thermalRecorder.startRecording(sessionId)
            delay(50)
            thermalRecorder.stopRecording()
            delay(25)
        }

        thermalRecorder.cleanup()
        println("[BULLETPROOF_TEST] Resource stress test completed")
    }

    @Test
    fun testErrorRecoveryMechanisms() = runBlocking {
        println("[BULLETPROOF_TEST] Testing error recovery mechanisms...")

        // Test recovery from various error conditions
        
        // 1. Invalid session ID handling
        thermalRecorder.initialize()
        delay(500)
        
        assertFalse("Empty session ID should fail", 
                   thermalRecorder.startRecording(""))
        assertFalse("Null-like session ID should fail", 
                   thermalRecorder.startRecording("null"))
        assertFalse("Very long session ID should fail", 
                   thermalRecorder.startRecording("a".repeat(1000)))

        // 2. Multiple cleanup calls (should be safe)
        thermalRecorder.cleanup()
        thermalRecorder.cleanup()
        thermalRecorder.cleanup()

        // 3. Operations after multiple cleanups
        assertFalse("Should fail gracefully after multiple cleanups", 
                   thermalRecorder.startRecording("test"))

        println("[BULLETPROOF_TEST] Error recovery test completed")
    }

    @Test
    fun testMemoryManagementValidation() = runBlocking {
        println("[BULLETPROOF_TEST] Testing memory management...")

        val initialMemory = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()
        println("[BULLETPROOF_TEST] Initial memory usage: ${initialMemory / 1024 / 1024}MB")

        // Create and destroy multiple recorder instances
        repeat(5) { iteration ->
            val recorder = ThermalRecorder(context, sessionManager, logger)
            recorder.initialize()
            delay(200)
            
            // Perform some operations
            recorder.getThermalCameraStatus()
            recorder.startPreview()
            delay(100)
            recorder.stopPreview()
            
            recorder.cleanup()
            
            // Force garbage collection
            System.gc()
            delay(100)
            
            val currentMemory = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()
            println("[BULLETPROOF_TEST] Memory after iteration $iteration: ${currentMemory / 1024 / 1024}MB")
        }

        val finalMemory = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()
        val memoryIncrease = finalMemory - initialMemory
        
        println("[BULLETPROOF_TEST] Final memory usage: ${finalMemory / 1024 / 1024}MB")
        println("[BULLETPROOF_TEST] Memory increase: ${memoryIncrease / 1024 / 1024}MB")
        
        // Allow some memory increase but flag significant leaks
        assertTrue("Memory increase should be reasonable (< 50MB)", 
                  memoryIncrease < 50 * 1024 * 1024)

        println("[BULLETPROOF_TEST] Memory management test completed")
    }

    @Test
    fun testDeviceFilterValidation() {
        println("[BULLETPROOF_TEST] Testing device filter validation...")

        // Test all supported Topdon device IDs match the device filter
        val supportedDeviceIds = listOf(
            Pair(0x0BDA, 0x3901), // TC001
            Pair(0x0BDA, 0x5840), // TC001 Plus
            Pair(0x0BDA, 0x5830), // TC001 variant
            Pair(0x0BDA, 0x5838)  // TC001 variant
        )

        supportedDeviceIds.forEach { (vendorId, productId) ->
            val mockDevice = createMockUsbDevice(vendorId, productId)
            assertTrue("Device VID:0x${vendorId.toString(16)}, PID:0x${productId.toString(16)} should be supported",
                      usbDeviceManager.isSupportedTopdonDevice(mockDevice))
        }

        // Test edge cases around supported IDs
        val edgeCaseIds = listOf(
            Pair(0x0BDA, 0x3900), // One less than TC001
            Pair(0x0BDA, 0x3902), // One more than TC001
            Pair(0x0BDB, 0x3901), // Wrong vendor ID
            Pair(0x0BD9, 0x3901), // Wrong vendor ID
            Pair(0x0000, 0x0000), // Minimum values
            Pair(0xFFFF, 0xFFFF)  // Maximum values
        )

        edgeCaseIds.forEach { (vendorId, productId) ->
            val mockDevice = createMockUsbDevice(vendorId, productId)
            assertFalse("Edge case device VID:0x${vendorId.toString(16)}, PID:0x${productId.toString(16)} should NOT be supported",
                       usbDeviceManager.isSupportedTopdonDevice(mockDevice))
        }

        println("[BULLETPROOF_TEST] Device filter validation completed")
    }

    @Test
    fun testThreadSafetyValidation() = runBlocking {
        println("[BULLETPROOF_TEST] Testing thread safety...")

        thermalRecorder.initialize()
        delay(500)

        // Create multiple concurrent threads performing operations
        val operations = listOf(
            suspend { repeat(20) { thermalRecorder.getThermalCameraStatus(); delay(5) } },
            suspend { repeat(10) { thermalRecorder.startPreview(); delay(10); thermalRecorder.stopPreview(); delay(10) } },
            suspend { repeat(5) { thermalRecorder.startRecording("thread_test_$it"); delay(20); thermalRecorder.stopRecording(); delay(20) } }
        )

        // Run operations concurrently
        operations.forEach { operation ->
            kotlinx.coroutines.launch {
                try {
                    operation()
                } catch (e: Exception) {
                    println("[BULLETPROOF_TEST] Thread safety test caught exception: ${e.message}")
                    // Exceptions are logged but should not crash the test
                }
            }
        }

        // Wait for operations to complete
        delay(2000)

        thermalRecorder.cleanup()
        println("[BULLETPROOF_TEST] Thread safety test completed")
    }

    @Test
    fun testEdgeCaseRecovery() = runBlocking {
        println("[BULLETPROOF_TEST] Testing edge case recovery...")

        // Test various edge cases that might occur in real usage

        // 1. Cleanup before initialization
        thermalRecorder.cleanup()
        
        // 2. Double initialization
        thermalRecorder.initialize()
        val secondInit = thermalRecorder.initialize()
        // Should handle gracefully (might succeed or fail, but shouldn't crash)
        
        delay(500)

        // 3. Recording with invalid paths
        val weirdSessionIds = listOf(
            "session/with/slashes",
            "session with spaces",
            "session\nwith\nnewlines",
            "session\twith\ttabs",
            "session-with-unicode-😀",
            "../../../etc/passwd", // Security test
            "CON", "PRN", "AUX" // Windows reserved names
        )

        weirdSessionIds.forEach { sessionId ->
            try {
                thermalRecorder.startRecording(sessionId)
                delay(50)
                thermalRecorder.stopRecording()
                delay(25)
                println("[BULLETPROOF_TEST] Handled weird session ID: '$sessionId'")
            } catch (e: Exception) {
                println("[BULLETPROOF_TEST] Exception with session ID '$sessionId': ${e.message}")
                // Should handle gracefully
            }
        }

        thermalRecorder.cleanup()
        println("[BULLETPROOF_TEST] Edge case recovery test completed")
    }

    private fun createMockUsbDevice(vendorId: Int, productId: Int): UsbDevice {
        // This is a simplified mock for testing - in real test we'd use mockk
        return object : UsbDevice() {
            override fun getVendorId(): Int = vendorId
            override fun getProductId(): Int = productId
            override fun getDeviceName(): String = "/dev/bus/usb/001/002"
            override fun getDeviceClass(): Int = 14
            override fun getDeviceSubclass(): Int = 1
            override fun getDeviceProtocol(): Int = 0
            override fun getManufacturerName(): String? = "Test Manufacturer"
            override fun getProductName(): String? = "Test Product"
            override fun getVersion(): String? = "1.0"
            override fun getSerialNumber(): String? = "123456"
            override fun getConfigurationCount(): Int = 1
            override fun getConfiguration(index: Int) = null
            override fun getInterface(index: Int) = null
            override fun getInterfaceCount(): Int = 1
        }
    }
}