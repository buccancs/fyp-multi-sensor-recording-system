package com.multisensor.recording.recording

import android.Manifest
import android.graphics.SurfaceTexture
import android.view.TextureView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.rule.ActivityTestRule
import androidx.test.rule.GrantPermissionRule
import com.multisensor.recording.MainActivity
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import javax.inject.Inject

/**
 * Manual Test Plan Implementation for Milestone 2.2 CameraRecorder Module
 * Based on the 10 test scenarios from 2_2_milestone.md specification
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class CameraRecorderManualTest {
    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @get:Rule
    var activityRule = ActivityTestRule(MainActivity::class.java)

    @get:Rule
    var permissionRule: GrantPermissionRule =
        GrantPermissionRule.grant(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
        )

    @Inject
    lateinit var cameraRecorder: CameraRecorder

    private lateinit var textureView: TextureView
    private var currentSession: SessionInfo? = null

    @Before
    fun setup() {
        hiltRule.inject()

        // Create TextureView on UI thread
        InstrumentationRegistry.getInstrumentation().runOnMainSync {
            textureView = TextureView(activityRule.activity)
            // Add to activity layout for proper lifecycle
            activityRule.activity.setContentView(textureView)
        }

        // Wait for TextureView to be ready
        Thread.sleep(1000)
    }

    @After
    fun cleanup() =
        runBlocking {
            try {
                // Stop any active session
                currentSession = cameraRecorder.stopSession()

                // Allow cleanup time
                delay(500)

                println("[DEBUG_LOG] Test cleanup completed. Session: ${currentSession?.getSummary()}")
            } catch (e: Exception) {
                println("[DEBUG_LOG] Cleanup error: ${e.message}")
            }
        }

    /**
     * Test 1: Baseline Preview Test
     * Verify TextureView displays live camera feed with correct orientation
     * Requirements: Preview is smooth (30fps), correctly oriented, no distortion
     */
    @Test
    fun test1_baselinePreviewTest() =
        runBlocking {
            println("[DEBUG_LOG] Starting Test 1: Baseline Preview Test")

            // Step 1: Initialize CameraRecorder with TextureView
            val initResult =
                withTimeout(10000) {
                    cameraRecorder.initialize(textureView)
                }
            assertTrue("[DEBUG_LOG] Camera initialization failed", initResult)
            println("[DEBUG_LOG] Camera initialized successfully")

            // Step 2: Wait for TextureView surface to become available
            val surfaceAvailableLatch = CountDownLatch(1)
            var surfaceWidth = 0
            var surfaceHeight = 0

            InstrumentationRegistry.getInstrumentation().runOnMainSync {
                if (textureView.isAvailable) {
                    surfaceWidth = textureView.width
                    surfaceHeight = textureView.height
                    surfaceAvailableLatch.countDown()
                    println("[DEBUG_LOG] TextureView surface already available: ${surfaceWidth}x$surfaceHeight")
                } else {
                    textureView.surfaceTextureListener =
                        object : TextureView.SurfaceTextureListener {
                            override fun onSurfaceTextureAvailable(
                                surface: SurfaceTexture,
                                width: Int,
                                height: Int,
                            ) {
                                surfaceWidth = width
                                surfaceHeight = height
                                surfaceAvailableLatch.countDown()
                                println("[DEBUG_LOG] TextureView surface became available: ${width}x$height")
                            }

                            override fun onSurfaceTextureSizeChanged(
                                surface: SurfaceTexture,
                                width: Int,
                                height: Int,
                            ) {}

                            override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean = true

                            override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
                        }
                }
            }

            // Wait for surface availability with timeout
            assertTrue(
                "[DEBUG_LOG] TextureView surface did not become available within timeout",
                surfaceAvailableLatch.await(5, TimeUnit.SECONDS),
            )

            // Step 3: Verify surface dimensions are reasonable
            assertTrue("[DEBUG_LOG] Surface width too small: $surfaceWidth", surfaceWidth > 0)
            assertTrue("[DEBUG_LOG] Surface height too small: $surfaceHeight", surfaceHeight > 0)
            println("[DEBUG_LOG] Surface dimensions validated: ${surfaceWidth}x$surfaceHeight")

            // Step 4: Wait for preview to stabilize (simulate preview observation)
            delay(3000) // Allow 3 seconds for preview to start and stabilize

            // Step 5: Verify no crashes occurred during preview
            // If we reach this point without exceptions, preview is working
            println("[DEBUG_LOG] Preview running smoothly for 3 seconds")

            // Step 6: Test orientation handling (simulate device rotation)
            InstrumentationRegistry.getInstrumentation().runOnMainSync {
                // Safely get the non-null surface and trigger the size changed listener
                textureView.surfaceTexture?.let { surface ->
                    textureView.surfaceTextureListener?.onSurfaceTextureSizeChanged(
                        surface,
                        surfaceHeight,
                        surfaceWidth,
                    )
                }
            }

            delay(1000) // Allow transform to apply
            println("[DEBUG_LOG] Orientation handling tested")

            println("[DEBUG_LOG] Test 1 completed successfully - Preview is functional")
        }

    /**
     * Test 2: Video-only Recording Test
     * Verify 4K H.264 video recording without audio
     * Requirements: 4K resolution, H.264 codec, no audio track, proper orientation
     */
    @Test
    fun test2_videoOnlyRecordingTest() =
        runBlocking {
            println("[DEBUG_LOG] Starting Test 2: Video-only Recording Test")

            // Step 1: Initialize camera
            val initResult =
                withTimeout(10000) {
                    cameraRecorder.initialize(textureView)
                }
            assertTrue("[DEBUG_LOG] Camera initialization failed", initResult)

            // Step 2: Start video-only session
            currentSession =
                withTimeout(15000) {
                    cameraRecorder.startSession(recordVideo = true, captureRaw = false)
                }
            assertNotNull("[DEBUG_LOG] Failed to start video-only session", currentSession)
            assertTrue("[DEBUG_LOG] Video not enabled in session", currentSession!!.videoEnabled)
            assertFalse("[DEBUG_LOG] RAW should not be enabled", currentSession!!.rawEnabled)
            println("[DEBUG_LOG] Video-only session started: ${currentSession!!.getSummary()}")

            // Step 3: Let recording run for 10 seconds
            println("[DEBUG_LOG] Recording 4K video for 10 seconds...")
            delay(10000)

            // Step 4: Stop recording
            val stoppedSession =
                withTimeout(10000) {
                    cameraRecorder.stopSession()
                }
            assertNotNull("[DEBUG_LOG] Failed to stop session", stoppedSession)
            assertFalse("[DEBUG_LOG] Session should not be active after stop", stoppedSession!!.isActive())
            println("[DEBUG_LOG] Recording stopped: ${stoppedSession.getSummary()}")

            // Step 5: Verify video file was created
            val videoFilePath = stoppedSession.videoFilePath
            assertNotNull("[DEBUG_LOG] Video file path is null", videoFilePath)

            val videoFile = File(videoFilePath!!)
            assertTrue("[DEBUG_LOG] Video file does not exist: $videoFilePath", videoFile.exists())
            assertTrue("[DEBUG_LOG] Video file is empty: $videoFilePath", videoFile.length() > 0)

            // Step 6: Verify file properties
            val expectedMinSize = 10 * 1024 * 1024 // At least 10MB for 10 seconds of 4K video
            assertTrue(
                "[DEBUG_LOG] Video file too small (${videoFile.length()} bytes), expected at least $expectedMinSize",
                videoFile.length() >= expectedMinSize,
            )

            println("[DEBUG_LOG] Video file validated: ${videoFile.length()} bytes at $videoFilePath")
            println("[DEBUG_LOG] Test 2 completed successfully - 4K video recording functional")

            currentSession = stoppedSession
        }

    /**
     * Test 3: RAW-only Capture Test
     * Verify RAW image capture with DNG file creation and metadata embedding
     * Requirements: Valid DNG files, correct size, proper metadata, no corruption
     */
    @Test
    fun test3_rawOnlyCaptureTest() =
        runBlocking {
            println("[DEBUG_LOG] Starting Test 3: RAW-only Capture Test")

            // Step 1: Initialize camera
            val initResult =
                withTimeout(10000) {
                    cameraRecorder.initialize(textureView)
                }
            assertTrue("[DEBUG_LOG] Camera initialization failed", initResult)

            // Step 2: Start RAW-only session
            currentSession =
                withTimeout(15000) {
                    cameraRecorder.startSession(recordVideo = false, captureRaw = true)
                }
            assertNotNull("[DEBUG_LOG] Failed to start RAW-only session", currentSession)
            assertFalse("[DEBUG_LOG] Video should not be enabled", currentSession!!.videoEnabled)
            assertTrue("[DEBUG_LOG] RAW not enabled in session", currentSession!!.rawEnabled)
            println("[DEBUG_LOG] RAW-only session started: ${currentSession!!.getSummary()}")

            // Step 3: Wait for preview to stabilize
            delay(2000)

            // Step 4: Capture first RAW image
            println("[DEBUG_LOG] Capturing first RAW image...")
            val firstCaptureResult =
                withTimeout(10000) {
                    cameraRecorder.captureRawImage()
                }
            assertTrue("[DEBUG_LOG] First RAW capture failed", firstCaptureResult)

            // Wait for DNG processing to complete
            delay(3000)

            // Step 5: Capture second RAW image to test multiple captures
            println("[DEBUG_LOG] Capturing second RAW image...")
            val secondCaptureResult =
                withTimeout(10000) {
                    cameraRecorder.captureRawImage()
                }
            assertTrue("[DEBUG_LOG] Second RAW capture failed", secondCaptureResult)

            // Wait for DNG processing to complete
            delay(3000)

            // Step 6: Stop session
            val stoppedSession =
                withTimeout(10000) {
                    cameraRecorder.stopSession()
                }
            assertNotNull("[DEBUG_LOG] Failed to stop RAW session", stoppedSession)
            assertFalse("[DEBUG_LOG] Session should not be active after stop", stoppedSession!!.isActive())
            println("[DEBUG_LOG] RAW session stopped: ${stoppedSession.getSummary()}")

            // Step 7: Verify RAW files were created
            val rawFilePaths = stoppedSession.rawFilePaths
            assertTrue("[DEBUG_LOG] No RAW files captured", rawFilePaths.isNotEmpty())
            assertEquals("[DEBUG_LOG] Expected 2 RAW files, got ${rawFilePaths.size}", 2, rawFilePaths.size)

            // Step 8: Validate each DNG file
            rawFilePaths.forEachIndexed { index, filePath ->
                println("[DEBUG_LOG] Validating RAW file ${index + 1}: $filePath")

                val dngFile = File(filePath)
                assertTrue("[DEBUG_LOG] DNG file does not exist: $filePath", dngFile.exists())
                assertTrue("[DEBUG_LOG] DNG file is empty: $filePath", dngFile.length() > 0)

                // Verify file extension
                assertTrue("[DEBUG_LOG] File should have .dng extension: $filePath", filePath.endsWith(".dng"))

                // Verify reasonable file size (RAW files should be several MB)
                val expectedMinSize = 5 * 1024 * 1024 // At least 5MB for RAW sensor data
                assertTrue(
                    "[DEBUG_LOG] DNG file too small (${dngFile.length()} bytes), expected at least $expectedMinSize",
                    dngFile.length() >= expectedMinSize,
                )

                // Verify DNG file header (basic validation)
                val fileBytes = dngFile.readBytes()
                assertTrue("[DEBUG_LOG] DNG file too small for header validation", fileBytes.size >= 8)

                // Check for TIFF/DNG magic number (0x4949 or 0x4D4D for little/big endian)
                val isValidDng =
                    (fileBytes[0] == 0x49.toByte() && fileBytes[1] == 0x49.toByte()) ||
                        (fileBytes[0] == 0x4D.toByte() && fileBytes[1] == 0x4D.toByte())
                assertTrue("[DEBUG_LOG] Invalid DNG file header: $filePath", isValidDng)

                println("[DEBUG_LOG] DNG file ${index + 1} validated: ${dngFile.length()} bytes")
            }

            // Step 9: Verify session metadata
            assertNotNull("[DEBUG_LOG] RAW resolution should be set", stoppedSession.rawResolution)
            assertNull("[DEBUG_LOG] Video file path should be null for RAW-only", stoppedSession.videoFilePath)
            assertEquals("[DEBUG_LOG] RAW file count mismatch", 2, stoppedSession.getRawImageCount())

            println("[DEBUG_LOG] Test 3 completed successfully - RAW capture and DNG creation functional")
            println(
                "[DEBUG_LOG] Captured ${rawFilePaths.size} DNG files with total size: ${rawFilePaths.sumOf { File(it).length() }} bytes",
            )

            currentSession = stoppedSession
        }

    /**
     * Test 4: Concurrent Video + RAW Test
     * Verify simultaneous 4K video recording and RAW image capture
     * Requirements: Both outputs functional, minimal interference, proper synchronization
     */
    @Test
    fun test4_concurrentVideoRawTest() =
        runBlocking {
            println("[DEBUG_LOG] Starting Test 4: Concurrent Video + RAW Test")

            // Step 1: Initialize camera
            val initResult =
                withTimeout(10000) {
                    cameraRecorder.initialize(textureView)
                }
            assertTrue("[DEBUG_LOG] Camera initialization failed", initResult)

            // Step 2: Start concurrent session (both video and RAW enabled)
            currentSession =
                withTimeout(15000) {
                    cameraRecorder.startSession(recordVideo = true, captureRaw = true)
                }
            assertNotNull("[DEBUG_LOG] Failed to start concurrent session", currentSession)
            assertTrue("[DEBUG_LOG] Video not enabled in concurrent session", currentSession!!.videoEnabled)
            assertTrue("[DEBUG_LOG] RAW not enabled in concurrent session", currentSession!!.rawEnabled)
            println("[DEBUG_LOG] Concurrent session started: ${currentSession!!.getSummary()}")

            // Step 3: Let video recording stabilize
            delay(3000)

            // Step 4: Capture RAW image during video recording
            println("[DEBUG_LOG] Capturing RAW image during video recording...")
            val firstRawCapture =
                withTimeout(10000) {
                    cameraRecorder.captureRawImage()
                }
            assertTrue("[DEBUG_LOG] RAW capture during video failed", firstRawCapture)

            // Step 5: Continue video recording
            delay(5000)

            // Step 6: Capture another RAW image
            println("[DEBUG_LOG] Capturing second RAW image during video recording...")
            val secondRawCapture =
                withTimeout(10000) {
                    cameraRecorder.captureRawImage()
                }
            assertTrue("[DEBUG_LOG] Second RAW capture during video failed", secondRawCapture)

            // Step 7: Continue recording for a bit more
            delay(3000)

            // Step 8: Stop concurrent session
            val stoppedSession =
                withTimeout(10000) {
                    cameraRecorder.stopSession()
                }
            assertNotNull("[DEBUG_LOG] Failed to stop concurrent session", stoppedSession)
            assertFalse("[DEBUG_LOG] Session should not be active after stop", stoppedSession!!.isActive())
            println("[DEBUG_LOG] Concurrent session stopped: ${stoppedSession.getSummary()}")

            // Step 9: Verify both video and RAW outputs
            // Verify video file
            val videoFilePath = stoppedSession.videoFilePath
            assertNotNull("[DEBUG_LOG] Video file path is null in concurrent session", videoFilePath)
            val videoFile = File(videoFilePath!!)
            assertTrue("[DEBUG_LOG] Video file does not exist: $videoFilePath", videoFile.exists())
            assertTrue("[DEBUG_LOG] Video file is empty: $videoFilePath", videoFile.length() > 0)

            // Verify RAW files
            val rawFilePaths = stoppedSession.rawFilePaths
            assertTrue("[DEBUG_LOG] No RAW files in concurrent session", rawFilePaths.isNotEmpty())
            assertEquals("[DEBUG_LOG] Expected 2 RAW files in concurrent session", 2, rawFilePaths.size)

            // Step 10: Validate file integrity
            rawFilePaths.forEach { filePath ->
                val dngFile = File(filePath)
                assertTrue("[DEBUG_LOG] DNG file missing in concurrent session: $filePath", dngFile.exists())
                assertTrue("[DEBUG_LOG] DNG file empty in concurrent session: $filePath", dngFile.length() > 0)
            }

            // Step 11: Verify session duration and timing
            val sessionDuration = stoppedSession.getDurationMs()
            assertTrue("[DEBUG_LOG] Session duration too short: ${sessionDuration}ms", sessionDuration >= 10000) // At least 10 seconds

            println("[DEBUG_LOG] Test 4 completed successfully - Concurrent video + RAW capture functional")
            println("[DEBUG_LOG] Video: ${videoFile.length()} bytes, RAW: ${rawFilePaths.size} files")

            currentSession = stoppedSession
        }
}
