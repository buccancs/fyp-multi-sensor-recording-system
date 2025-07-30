package com.multisensor.recording.recording

import android.content.Context
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.streaming.PreviewStreamer
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
 * Hardware test for ThermalRecorder with connected Topdon thermal camera.
 * This test requires an actual Topdon TC001/Plus camera to be connected via USB-C OTG.
 *
 * To run this test:
 * 1. Connect your Topdon thermal camera to the phone via USB-C OTG
 * 2. Run: ./gradlew connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.multisensor.recording.recording.ThermalRecorderHardwareTest
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ThermalRecorderHardwareTest {
    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var sessionManager: SessionManager

    @Inject
    lateinit var logger: Logger

    private lateinit var context: Context
    private lateinit var thermalRecorder: ThermalRecorder

    @Before
    fun setup() {
        hiltRule.inject()
        context = InstrumentationRegistry.getInstrumentation().targetContext

        // Create ThermalRecorder instance
        thermalRecorder = ThermalRecorder(context, sessionManager, logger)

        println("[DEBUG_LOG] ThermalRecorder hardware test setup complete")
    }

    @Test
    fun testThermalCameraDetectionAndInitialization() =
        runBlocking {
            println("[DEBUG_LOG] Starting thermal camera detection test...")

            // Initialize ThermalRecorder
            val initResult = thermalRecorder.initialize()
            println("[DEBUG_LOG] ThermalRecorder initialization result: $initResult")

            // Wait for USB device detection and permission handling
            println("[DEBUG_LOG] Waiting for USB device detection (10 seconds)...")
            delay(10000) // Wait 10 seconds for device detection and permission

            // Check thermal camera status
            val status = thermalRecorder.getThermalCameraStatus()
            println("[DEBUG_LOG] Thermal camera status:")
            println("[DEBUG_LOG] - Available: ${status.isAvailable}")
            println("[DEBUG_LOG] - Device name: ${status.deviceName}")
            println("[DEBUG_LOG] - Width: ${status.width}")
            println("[DEBUG_LOG] - Height: ${status.height}")
            println("[DEBUG_LOG] - Frame rate: ${status.frameRate}")

            // If camera is available, test preview
            if (status.isAvailable) {
                println("[DEBUG_LOG] Camera detected! Testing preview...")

                val previewResult = thermalRecorder.startPreview()
                println("[DEBUG_LOG] Preview start result: $previewResult")

                if (previewResult) {
                    // Let preview run for 5 seconds
                    delay(5000)

                    val updatedStatus = thermalRecorder.getThermalCameraStatus()
                    println("[DEBUG_LOG] Preview status:")
                    println("[DEBUG_LOG] - Preview active: ${updatedStatus.isPreviewActive}")
                    println("[DEBUG_LOG] - Frame count: ${updatedStatus.frameCount}")

                    // Stop preview
                    thermalRecorder.stopPreview()
                    println("[DEBUG_LOG] Preview stopped")
                }
            } else {
                println("[DEBUG_LOG] No thermal camera detected. Please check:")
                println("[DEBUG_LOG] 1. Camera is connected via USB-C OTG")
                println("[DEBUG_LOG] 2. USB permissions were granted")
                println("[DEBUG_LOG] 3. Camera is a supported Topdon model (TC001/Plus)")
            }

            // Cleanup
            thermalRecorder.cleanup()
            println("[DEBUG_LOG] Test completed")
        }

    @Test
    fun testThermalRecordingBasicFunctionality() =
        runBlocking {
            println("[DEBUG_LOG] Starting thermal recording functionality test...")

            // Initialize ThermalRecorder
            val initResult = thermalRecorder.initialize()
            println("[DEBUG_LOG] ThermalRecorder initialization result: $initResult")

            // Wait for device detection
            delay(10000)

            val status = thermalRecorder.getThermalCameraStatus()
            if (!status.isAvailable) {
                println("[DEBUG_LOG] No thermal camera available - skipping recording test")
                return@runBlocking
            }

            println("[DEBUG_LOG] Testing thermal recording...")

            // Start recording
            val sessionId = "test_session_${System.currentTimeMillis()}"
            val recordingResult = thermalRecorder.startRecording(sessionId)
            println("[DEBUG_LOG] Recording start result: $recordingResult")

            if (recordingResult) {
                // Record for 10 seconds
                println("[DEBUG_LOG] Recording for 10 seconds...")
                delay(10000)

                val recordingStatus = thermalRecorder.getThermalCameraStatus()
                println("[DEBUG_LOG] Recording status:")
                println("[DEBUG_LOG] - Recording: ${recordingStatus.isRecording}")
                println("[DEBUG_LOG] - Frame count: ${recordingStatus.frameCount}")

                // Stop recording
                val stopResult = thermalRecorder.stopRecording()
                println("[DEBUG_LOG] Recording stop result: $stopResult")

                // Check final frame count
                val finalStatus = thermalRecorder.getThermalCameraStatus()
                println("[DEBUG_LOG] Final frame count: ${finalStatus.frameCount}")

                // Expected frame count should be around 250 frames (10 seconds * 25 fps)
                val expectedFrames = 250
                val actualFrames = finalStatus.frameCount
                val frameCountOk = actualFrames > (expectedFrames * 0.8) // Allow 20% tolerance

                println("[DEBUG_LOG] Frame count validation:")
                println("[DEBUG_LOG] - Expected: ~$expectedFrames frames")
                println("[DEBUG_LOG] - Actual: $actualFrames frames")
                println("[DEBUG_LOG] - Validation: ${if (frameCountOk) "PASS" else "FAIL"}")
            }

            // Cleanup
            thermalRecorder.cleanup()
            println("[DEBUG_LOG] Recording test completed")
        }
}
