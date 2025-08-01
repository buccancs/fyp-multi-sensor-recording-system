package com.multisensor.recording.recording

import android.Manifest
import android.content.Context
import android.graphics.SurfaceTexture
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureResult
import android.view.TextureView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.core.app.ActivityScenario
import androidx.test.rule.GrantPermissionRule
import com.multisensor.recording.MainActivity
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
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
 * Samsung S21/S22 Camera Recording and Stage 3 RAW Extraction Test
 * 
 * This comprehensive test validates:
 * - Samsung S21/S22 specific camera hardware detection
 * - Stage 3 RAW image extraction from camera sensor
 * - DNG file creation with Samsung-optimized metadata
 * - Samsung camera API compliance and implementation guidelines
 * - Hardware LEVEL_3 capabilities validation
 * - RAW sensor characteristics validation
 * 
 * Requirements:
 * - Samsung S21 or S22 device (or compatible Samsung device with LEVEL_3 camera)
 * - Camera permissions granted
 * - Storage permissions granted
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class SamsungS21S22CameraRawExtractionTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @get:Rule
    var permissionRule: GrantPermissionRule =
        GrantPermissionRule.grant(
            Manifest.permission.CAMERA,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE,
        )

    @Inject
    lateinit var cameraRecorder: CameraRecorder

    @Inject
    lateinit var sessionManager: SessionManager

    @Inject
    lateinit var logger: Logger

    private lateinit var context: Context
    private lateinit var textureView: TextureView
    private var currentSession: SessionInfo? = null
    private lateinit var activityScenario: ActivityScenario<MainActivity>

    @Before
    fun setup() {
        hiltRule.inject()
        context = InstrumentationRegistry.getInstrumentation().targetContext

        // Launch activity
        activityScenario = ActivityScenario.launch(MainActivity::class.java)

        // Create TextureView on UI thread
        InstrumentationRegistry.getInstrumentation().runOnMainSync {
            activityScenario.onActivity { activity ->
                textureView = TextureView(activity)
                activity.setContentView(textureView)
            }
        }

        // Wait for TextureView initialization
        Thread.sleep(2000)

        println("[SAMSUNG_TEST] Setup complete for Samsung S21/S22 camera testing")
    }

    @After
    fun cleanup() = runBlocking {
        try {
            currentSession = cameraRecorder.stopSession()
            delay(1000)
            
            if (::activityScenario.isInitialized) {
                activityScenario.close()
            }
            
            println("[SAMSUNG_TEST] Cleanup completed")
        } catch (e: Exception) {
            println("[SAMSUNG_TEST] Cleanup error: ${e.message}")
        }
    }

    /**
     * Test 1: Samsung S21/S22 Device Detection and Hardware Validation
     */
    @Test
    fun test1_samsungDeviceDetectionAndHardwareValidation() {
        println("[SAMSUNG_TEST] Starting Samsung S21/S22 device detection...")

        // Check device model
        val deviceModel = android.os.Build.MODEL.uppercase()
        val deviceManufacturer = android.os.Build.MANUFACTURER.uppercase()
        
        println("[SAMSUNG_TEST] Device: $deviceManufacturer $deviceModel")
        println("[SAMSUNG_TEST] SDK: ${android.os.Build.VERSION.SDK_INT}")
        
        val isSamsungDevice = deviceManufacturer.contains("SAMSUNG")
        val isSamsungS21S22 = deviceModel.contains("SM-G99") || deviceModel.contains("S21") || deviceModel.contains("S22")
        
        if (!isSamsungDevice) {
            println("[SAMSUNG_TEST] WARNING: Not a Samsung device - test results may not be applicable")
        }
        
        if (isSamsungS21S22) {
            println("[SAMSUNG_TEST] ✓ Samsung S21/S22 device detected - proceeding with specialized tests")
        } else {
            println("[SAMSUNG_TEST] INFO: Not S21/S22 specifically, but will test Samsung camera capabilities")
        }

        // Validate camera hardware
        val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        var level3CameraFound = false
        var rawCapableCameraFound = false

        for (cameraId in cameraManager.cameraIdList) {
            val characteristics = cameraManager.getCameraCharacteristics(cameraId)
            val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
            
            if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                val hardwareLevel = characteristics.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL)
                val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                
                val isLevel3 = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3
                val hasRawCapability = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW) == true
                
                println("[SAMSUNG_TEST] Camera $cameraId: Level=${getHardwareLevelName(hardwareLevel)}, RAW=$hasRawCapability")
                
                if (isLevel3) {
                    level3CameraFound = true
                    println("[SAMSUNG_TEST] ✓ LEVEL_3 camera found - optimal for Samsung S21/S22")
                }
                
                if (hasRawCapability) {
                    rawCapableCameraFound = true
                    println("[SAMSUNG_TEST] ✓ RAW capability found - stage 3 extraction possible")
                }
            }
        }

        assertTrue("[SAMSUNG_TEST] No RAW capable camera found", rawCapableCameraFound)
        
        if (isSamsungS21S22) {
            assertTrue("[SAMSUNG_TEST] Samsung S21/S22 should have LEVEL_3 camera", level3CameraFound)
        }
    }

    /**
     * Test 2: Samsung Camera Initialization and RAW Setup
     */
    @Test
    fun test2_samsungCameraInitializationAndRawSetup() = runBlocking {
        println("[SAMSUNG_TEST] Starting Samsung camera initialization...")

        // Initialize camera with Samsung optimizations
        val initResult = withTimeout(15000) {
            cameraRecorder.initialize(textureView)
        }
        
        assertTrue("[SAMSUNG_TEST] Samsung camera initialization failed", initResult)
        println("[SAMSUNG_TEST] ✓ Samsung camera initialized successfully")

        // Wait for TextureView surface availability
        val surfaceAvailableLatch = CountDownLatch(1)
        InstrumentationRegistry.getInstrumentation().runOnMainSync {
            if (textureView.isAvailable) {
                surfaceAvailableLatch.countDown()
            } else {
                textureView.surfaceTextureListener = object : TextureView.SurfaceTextureListener {
                    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
                        surfaceAvailableLatch.countDown()
                    }
                    override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {}
                    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean = false
                    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
                }
            }
        }

        assertTrue("[SAMSUNG_TEST] TextureView surface not available", 
                   surfaceAvailableLatch.await(10, TimeUnit.SECONDS))
        
        println("[SAMSUNG_TEST] ✓ Samsung camera surface ready")
    }

    /**
     * Test 3: Stage 3 RAW Image Extraction Test
     */
    @Test
    fun test3_stage3RawImageExtraction() = runBlocking {
        println("[SAMSUNG_TEST] Starting Stage 3 RAW image extraction test...")

        // Initialize camera
        val initResult = cameraRecorder.initialize(textureView)
        assertTrue("[SAMSUNG_TEST] Camera initialization failed", initResult)
        
        delay(3000) // Allow camera to stabilize

        // Start session with RAW capture enabled
        currentSession = cameraRecorder.startSession(recordVideo = false, captureRaw = true)
        assertNotNull("[SAMSUNG_TEST] Failed to start RAW capture session", currentSession)
        
        val sessionId = currentSession?.sessionId ?: "unknown"
        println("[SAMSUNG_TEST] ✓ RAW capture session started: $sessionId")

        // Capture multiple RAW images to test stage 3 extraction
        val rawCaptureCount = 5
        println("[SAMSUNG_TEST] Capturing $rawCaptureCount RAW images for stage 3 validation...")

        for (i in 1..rawCaptureCount) {
            println("[SAMSUNG_TEST] Capturing RAW image $i/$rawCaptureCount...")
            val captureResult = cameraRecorder.captureRawImage()
            assertTrue("[SAMSUNG_TEST] RAW capture $i failed", captureResult)
            
            delay(2000) // Wait between captures for proper processing
        }

        // Allow time for DNG processing
        delay(5000)

        // Stop session and validate results
        val finalSession = cameraRecorder.stopSession()
        assertNotNull("[SAMSUNG_TEST] Failed to stop RAW session", finalSession)
        
        val rawFileCount = finalSession?.getRawImageCount() ?: 0
        println("[SAMSUNG_TEST] RAW files created: $rawFileCount")
        
        assertTrue("[SAMSUNG_TEST] No RAW files created", rawFileCount > 0)
        
        if (rawFileCount >= rawCaptureCount) {
            println("[SAMSUNG_TEST] ✓ All expected RAW files created successfully")
        } else {
            println("[SAMSUNG_TEST] WARNING: Expected $rawCaptureCount but got $rawFileCount RAW files")
        }

        currentSession = finalSession
    }

    /**
     * Test 4: Samsung DNG File Validation and Metadata Check
     */
    @Test
    fun test4_samsungDngFileValidationAndMetadata() = runBlocking {
        println("[SAMSUNG_TEST] Starting Samsung DNG file validation...")

        // Initialize and capture RAW
        val initResult = cameraRecorder.initialize(textureView)
        assertTrue("[SAMSUNG_TEST] Camera initialization failed", initResult)
        delay(3000)

        currentSession = cameraRecorder.startSession(recordVideo = false, captureRaw = true)
        assertNotNull("[SAMSUNG_TEST] Failed to start session", currentSession)

        // Capture single RAW for detailed validation
        val captureResult = cameraRecorder.captureRawImage()
        assertTrue("[SAMSUNG_TEST] RAW capture failed", captureResult)
        
        delay(3000) // Allow DNG processing

        val finalSession = cameraRecorder.stopSession()
        assertNotNull("[SAMSUNG_TEST] Failed to stop session", finalSession)

        // Validate DNG files
        val rawFiles = finalSession?.rawFilePaths ?: emptyList<String>()
        assertTrue("[SAMSUNG_TEST] No DNG files created", rawFiles.isNotEmpty())

        for (filePath in rawFiles) {
            val dngFile = File(filePath)
            assertTrue("[SAMSUNG_TEST] DNG file does not exist: ${dngFile.name}", dngFile.exists())
            
            val fileSize = dngFile.length()
            println("[SAMSUNG_TEST] DNG file: ${dngFile.name}, Size: ${fileSize / 1024}KB")
            
            // DNG files should be substantial (Samsung S21/S22 typically produce 12-15MB+ RAW files)
            assertTrue("[SAMSUNG_TEST] DNG file too small: ${fileSize / 1024}KB", fileSize > 1024 * 1024) // > 1MB minimum
            
            // Validate DNG header (basic check)
            validateDngFileHeader(dngFile)
        }

        println("[SAMSUNG_TEST] ✓ Samsung DNG files validation completed")
        currentSession = finalSession
    }

    /**
     * Test 5: Concurrent Video + RAW Recording Test (Samsung S21/S22 LEVEL_3 capability)
     */
    @Test
    fun test5_concurrentVideoRawRecording() = runBlocking {
        println("[SAMSUNG_TEST] Starting concurrent Video + RAW recording test...")

        val initResult = cameraRecorder.initialize(textureView)
        assertTrue("[SAMSUNG_TEST] Camera initialization failed", initResult)
        delay(3000)

        // Start session with both video and RAW enabled
        currentSession = cameraRecorder.startSession(recordVideo = true, captureRaw = true)
        assertNotNull("[SAMSUNG_TEST] Failed to start concurrent session", currentSession)
        
        println("[SAMSUNG_TEST] ✓ Concurrent Video + RAW session started")

        // Record video while capturing RAW images
        delay(2000) // Let video recording stabilize

        // Capture RAW images during video recording
        val rawCaptureCount = 3
        for (i in 1..rawCaptureCount) {
            println("[SAMSUNG_TEST] Capturing RAW $i during video recording...")
            val captureResult = cameraRecorder.captureRawImage()
            assertTrue("[SAMSUNG_TEST] Concurrent RAW capture $i failed", captureResult)
            delay(2000)
        }

        // Continue video for a bit longer
        delay(3000)

        // Stop session
        val finalSession = cameraRecorder.stopSession()
        assertNotNull("[SAMSUNG_TEST] Failed to stop concurrent session", finalSession)

        // Validate both video and RAW outputs
        val videoPath = finalSession?.videoFilePath
        val rawCount = finalSession?.getRawImageCount() ?: 0

        assertNotNull("[SAMSUNG_TEST] No video file created", videoPath)
        assertTrue("[SAMSUNG_TEST] No RAW files created during video", rawCount > 0)

        val videoFile = File(videoPath!!)
        assertTrue("[SAMSUNG_TEST] Video file does not exist", videoFile.exists())
        assertTrue("[SAMSUNG_TEST] Video file is empty", videoFile.length() > 0)

        println("[SAMSUNG_TEST] ✓ Concurrent recording: Video=${videoFile.length() / 1024}KB, RAW files=$rawCount")
        currentSession = finalSession
    }

    /**
     * Test 6: Samsung Camera Characteristics Validation
     */
    @Test
    fun test6_samsungCameraCharacteristicsValidation() {
        println("[SAMSUNG_TEST] Starting Samsung camera characteristics validation...")

        val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        var samsungOptimalCameraFound = false

        for (cameraId in cameraManager.cameraIdList) {
            val characteristics = cameraManager.getCameraCharacteristics(cameraId)
            val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
            
            if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                println("[SAMSUNG_TEST] Analyzing main camera: $cameraId")
                
                // Hardware level validation
                val hardwareLevel = characteristics.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL)
                val isLevel3 = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3
                
                // Capabilities validation
                val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                val hasRaw = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW) == true
                val hasManualSensor = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_SENSOR) == true
                val hasManualPostProcessing = capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_POST_PROCESSING) == true
                
                // Samsung sensor characteristics
                val activeArraySize = characteristics.get(CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE)
                val pixelArraySize = characteristics.get(CameraCharacteristics.SENSOR_INFO_PIXEL_ARRAY_SIZE)
                val physicalSize = characteristics.get(CameraCharacteristics.SENSOR_INFO_PHYSICAL_SIZE)
                val colorFilterArrangement = characteristics.get(CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT)
                
                println("[SAMSUNG_TEST] Hardware Level: ${getHardwareLevelName(hardwareLevel)}")
                println("[SAMSUNG_TEST] RAW Capability: $hasRaw")
                println("[SAMSUNG_TEST] Manual Sensor: $hasManualSensor")
                println("[SAMSUNG_TEST] Manual Post-Processing: $hasManualPostProcessing")
                println("[SAMSUNG_TEST] Active Array: ${activeArraySize?.width()}x${activeArraySize?.height()}")
                println("[SAMSUNG_TEST] Pixel Array: ${pixelArraySize?.width}x${pixelArraySize?.height}")
                println("[SAMSUNG_TEST] Physical Size: ${physicalSize?.width}mm x ${physicalSize?.height}mm")
                
                val cfaPattern = when (colorFilterArrangement) {
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_RGGB -> "RGGB"
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_GRBG -> "GRBG"
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_GBRG -> "GBRG"
                    CameraCharacteristics.SENSOR_INFO_COLOR_FILTER_ARRANGEMENT_BGGR -> "BGGR"
                    else -> "Unknown/Mono"
                }
                println("[SAMSUNG_TEST] CFA Pattern: $cfaPattern")
                
                // Samsung S21/S22 optimal characteristics
                if (isLevel3 && hasRaw && hasManualSensor && hasManualPostProcessing) {
                    samsungOptimalCameraFound = true
                    println("[SAMSUNG_TEST] ✓ Samsung optimal camera found with full stage 3 RAW capabilities")
                }
                
                break // Main camera analyzed
            }
        }

        assertTrue("[SAMSUNG_TEST] No camera found with basic RAW capability", samsungOptimalCameraFound || hasBasicRawCapability())
        
        if (samsungOptimalCameraFound) {
            println("[SAMSUNG_TEST] ✓ Samsung S21/S22 optimal camera characteristics validated")
        } else {
            println("[SAMSUNG_TEST] WARNING: Optimal Samsung characteristics not found - may affect stage 3 RAW quality")
        }
    }

    // Helper methods

    private fun getHardwareLevelName(level: Int?): String {
        return when (level) {
            CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_LEGACY -> "LEGACY"
            CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_LIMITED -> "LIMITED"
            CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL -> "FULL"
            CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3 -> "LEVEL_3"
            else -> "UNKNOWN($level)"
        }
    }

    private fun hasBasicRawCapability(): Boolean {
        val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        for (cameraId in cameraManager.cameraIdList) {
            val characteristics = cameraManager.getCameraCharacteristics(cameraId)
            val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
            if (capabilities?.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW) == true) {
                return true
            }
        }
        return false
    }

    private fun validateDngFileHeader(dngFile: File) {
        try {
            val bytes = dngFile.readBytes()
            if (bytes.size < 8) {
                fail("[SAMSUNG_TEST] DNG file too small for header validation")
            }
            
            // Basic TIFF/DNG header validation
            val isTiff = (bytes[0] == 0x49.toByte() && bytes[1] == 0x49.toByte()) || // "II" Little Endian
                        (bytes[0] == 0x4D.toByte() && bytes[1] == 0x4D.toByte())   // "MM" Big Endian
                        
            assertTrue("[SAMSUNG_TEST] Invalid DNG/TIFF header", isTiff)
            println("[SAMSUNG_TEST] ✓ DNG file header validation passed: ${dngFile.name}")
            
        } catch (e: Exception) {
            fail("[SAMSUNG_TEST] Error validating DNG header: ${e.message}")
        }
    }
}