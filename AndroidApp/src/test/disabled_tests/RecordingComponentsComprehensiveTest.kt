package com.multisensor.recording.recording

import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import kotlinx.coroutines.test.runTest
import android.content.Context
import android.hardware.camera2.CameraManager
import android.media.MediaRecorder
import android.os.Environment
import java.io.File
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.test.assertFalse
import kotlin.test.assertNotNull

/**
 * Comprehensive Recording Components Tests
 * =======================================
 * 
 * This test suite provides comprehensive coverage for all recording-related
 * components in the Android application.
 * 
 * Test coverage:
 * - CameraRecorder: Video recording, configuration, quality management
 * - ThermalRecorder: Thermal sensor data recording, calibration
 * - ShimmerRecorder: Shimmer device integration, data synchronization
 * - Recording coordination: Multi-modal recording synchronization
 * 
 * Author: Multi-Sensor Recording System
 * Date: 2025-01-16
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class RecordingComponentsComprehensiveTest {

    @Mock
    private lateinit var mockContext: Context
    
    @Mock
    private lateinit var mockCameraManager: CameraManager
    
    @Mock
    private lateinit var mockMediaRecorder: MediaRecorder
    
    @Mock
    private lateinit var mockShimmerDevice: ShimmerDevice
    
    @Mock
    private lateinit var mockThermalSensor: ThermalSensor
    
    private lateinit var cameraRecorder: CameraRecorder
    private lateinit var thermalRecorder: ThermalRecorder
    private lateinit var shimmerRecorder: ShimmerRecorder

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        
        // Setup mock context
        whenever(mockContext.getSystemService(Context.CAMERA_SERVICE))
            .thenReturn(mockCameraManager)
        
        // Setup mock camera manager
        whenever(mockCameraManager.cameraIdList)
            .thenReturn(arrayOf("0", "1"))
        
        // Initialize recorders
        cameraRecorder = CameraRecorder(mockContext)
        thermalRecorder = ThermalRecorder(mockContext)
        shimmerRecorder = ShimmerRecorder(mockContext)
    }

    /**
     * Camera Recorder Tests
     */
    @Test
    fun `test camera recorder initialization`() {
        val config = CameraConfiguration(
            cameraId = "0",
            resolution = Resolution(1920, 1080),
            frameRate = 30,
            bitRate = 8000000
        )
        
        val result = cameraRecorder.initialize(config)
        
        assertTrue(result.isSuccess)
        assertEquals("0", cameraRecorder.getCurrentCameraId())
    }

    @Test
    fun `test camera recording start and stop`() = runTest {
        val outputFile = File(mockContext.filesDir, "test_video.mp4")
        
        // Setup mock media recorder
        whenever(mockMediaRecorder.start()).then { }
        whenever(mockMediaRecorder.stop()).then { }
        
        cameraRecorder.setMediaRecorder(mockMediaRecorder)
        
        // Start recording
        val startResult = cameraRecorder.startRecording(outputFile)
        assertTrue(startResult.isSuccess)
        assertTrue(cameraRecorder.isRecording())
        
        // Stop recording
        val stopResult = cameraRecorder.stopRecording()
        assertTrue(stopResult.isSuccess)
        assertFalse(cameraRecorder.isRecording())
        
        verify(mockMediaRecorder).start()
        verify(mockMediaRecorder).stop()
    }

    @Test
    fun `test camera configuration validation`() {
        val validConfig = CameraConfiguration(
            cameraId = "0",
            resolution = Resolution(1920, 1080),
            frameRate = 30,
            bitRate = 8000000
        )
        
        val invalidConfig = CameraConfiguration(
            cameraId = "999", // Invalid camera ID
            resolution = Resolution(8000, 6000), // Unsupported resolution
            frameRate = 120, // Unsupported frame rate
            bitRate = -1 // Invalid bit rate
        )
        
        assertTrue(cameraRecorder.validateConfiguration(validConfig))
        assertFalse(cameraRecorder.validateConfiguration(invalidConfig))
    }

    @Test
    fun `test camera preview management`() {
        val previewSurface = mock<android.view.Surface>()
        
        val result = cameraRecorder.startPreview(previewSurface)
        
        assertTrue(result.isSuccess)
        assertTrue(cameraRecorder.isPreviewActive())
        
        cameraRecorder.stopPreview()
        assertFalse(cameraRecorder.isPreviewActive())
    }

    @Test
    fun `test camera focus and exposure control`() {
        val focusPoint = FocusPoint(0.5f, 0.5f) // Center focus
        val exposureValue = 0 // Auto exposure
        
        val focusResult = cameraRecorder.setFocus(focusPoint)
        val exposureResult = cameraRecorder.setExposure(exposureValue)
        
        assertTrue(focusResult.isSuccess)
        assertTrue(exposureResult.isSuccess)
        assertEquals(focusPoint, cameraRecorder.getCurrentFocusPoint())
    }

    @Test
    fun `test camera error handling`() {
        // Simulate camera error
        whenever(mockCameraManager.openCamera(any(), any(), any()))
            .thenThrow(RuntimeException("Camera access denied"))
        
        val config = CameraConfiguration(
            cameraId = "0",
            resolution = Resolution(1920, 1080),
            frameRate = 30,
            bitRate = 8000000
        )
        
        val result = cameraRecorder.initialize(config)
        
        assertTrue(result.isFailure)
        assertNotNull(result.exceptionOrNull())
    }

    /**
     * Thermal Recorder Tests
     */
    @Test
    fun `test thermal recorder initialization`() {
        val config = ThermalConfiguration(
            samplingRate = 10, // 10 Hz
            temperatureRange = TemperatureRange(-10f, 60f),
            calibrationEnabled = true
        )
        
        whenever(mockThermalSensor.isAvailable()).thenReturn(true)
        thermalRecorder.setThermalSensor(mockThermalSensor)
        
        val result = thermalRecorder.initialize(config)
        
        assertTrue(result.isSuccess)
        assertTrue(thermalRecorder.isInitialized())
    }

    @Test
    fun `test thermal data recording`() = runTest {
        val outputFile = File(mockContext.filesDir, "thermal_data.csv")
        
        // Setup mock thermal sensor
        val mockTemperatureData = listOf(
            TemperatureReading(1642425600000, 25.5f, 0.1f), // timestamp, temp, confidence
            TemperatureReading(1642425600100, 25.7f, 0.1f),
            TemperatureReading(1642425600200, 25.6f, 0.1f)
        )
        
        whenever(mockThermalSensor.getTemperatureReadings())
            .thenReturn(mockTemperatureData)
        
        thermalRecorder.setThermalSensor(mockThermalSensor)
        
        // Start recording
        val startResult = thermalRecorder.startRecording(outputFile)
        assertTrue(startResult.isSuccess)
        
        // Simulate data collection
        thermalRecorder.collectData()
        
        // Stop recording
        val stopResult = thermalRecorder.stopRecording()
        assertTrue(stopResult.isSuccess)
        
        // Verify data was written
        assertTrue(outputFile.exists())
        assertTrue(outputFile.length() > 0)
    }

    @Test
    fun `test thermal calibration process`() {
        val calibrationConfig = ThermalCalibrationConfig(
            referenceTemperature = 25.0f,
            calibrationDuration = 30000, // 30 seconds
            stabilityThreshold = 0.1f
        )
        
        whenever(mockThermalSensor.calibrate(any())).thenReturn(
            CalibrationResult(
                success = true,
                offsetCorrection = -0.5f,
                gainCorrection = 1.02f,
                rmseError = 0.08f
            )
        )
        
        thermalRecorder.setThermalSensor(mockThermalSensor)
        
        val result = thermalRecorder.performCalibration(calibrationConfig)
        
        assertTrue(result.isSuccess)
        assertEquals(-0.5f, result.getOrNull()?.offsetCorrection)
        verify(mockThermalSensor).calibrate(calibrationConfig)
    }

    @Test
    fun `test thermal sensor health monitoring`() {
        whenever(mockThermalSensor.getHealth()).thenReturn(
            SensorHealth(
                isResponsive = true,
                signalQuality = 0.95f,
                lastUpdate = System.currentTimeMillis(),
                errorCount = 0
            )
        )
        
        thermalRecorder.setThermalSensor(mockThermalSensor)
        
        val health = thermalRecorder.checkSensorHealth()
        
        assertTrue(health.isResponsive)
        assertEquals(0.95f, health.signalQuality, 0.01f)
        assertEquals(0, health.errorCount)
    }

    /**
     * Shimmer Recorder Tests
     */
    @Test
    fun `test shimmer recorder initialization`() {
        val config = ShimmerConfiguration(
            deviceMacAddress = "00:06:66:AA:BB:CC",
            samplingRate = 512, // 512 Hz
            enabledSensors = listOf(SensorType.GSR, SensorType.ECG, SensorType.EMG),
            bluetoothTimeout = 30000
        )
        
        whenever(mockShimmerDevice.connect(any())).thenReturn(true)
        shimmerRecorder.setShimmerDevice(mockShimmerDevice)
        
        val result = shimmerRecorder.initialize(config)
        
        assertTrue(result.isSuccess)
        verify(mockShimmerDevice).connect(config.deviceMacAddress)
    }

    @Test
    fun `test shimmer data streaming`() = runTest {
        val outputFile = File(mockContext.filesDir, "shimmer_data.json")
        
        // Setup mock shimmer data
        val mockSensorData = listOf(
            ShimmerSensorData(
                timestamp = 1642425600000,
                gsr = 1.234f,
                ecg = 0.567f,
                emg = 0.890f,
                deviceId = "shimmer_001"
            ),
            ShimmerSensorData(
                timestamp = 1642425600002,
                gsr = 1.235f,
                ecg = 0.568f,
                emg = 0.891f,
                deviceId = "shimmer_001"
            )
        )
        
        whenever(mockShimmerDevice.isStreaming()).thenReturn(true)
        whenever(mockShimmerDevice.getLatestData()).thenReturn(mockSensorData)
        
        shimmerRecorder.setShimmerDevice(mockShimmerDevice)
        
        // Start streaming
        val startResult = shimmerRecorder.startStreaming(outputFile)
        assertTrue(startResult.isSuccess)
        
        // Collect data
        val collectedData = shimmerRecorder.collectStreamingData()
        assertEquals(2, collectedData.size)
        
        // Stop streaming
        val stopResult = shimmerRecorder.stopStreaming()
        assertTrue(stopResult.isSuccess)
        
        verify(mockShimmerDevice).startStreaming()
        verify(mockShimmerDevice).stopStreaming()
    }

    @Test
    fun `test shimmer device synchronization`() {
        val masterTimestamp = System.currentTimeMillis()
        
        whenever(mockShimmerDevice.synchronizeClock(masterTimestamp))
            .thenReturn(SyncResult(success = true, offsetMs = 2))
        
        shimmerRecorder.setShimmerDevice(mockShimmerDevice)
        
        val syncResult = shimmerRecorder.synchronizeWithMaster(masterTimestamp)
        
        assertTrue(syncResult.success)
        assertEquals(2L, syncResult.offsetMs)
        verify(mockShimmerDevice).synchronizeClock(masterTimestamp)
    }

    @Test
    fun `test shimmer connection recovery`() {
        // Simulate connection loss and recovery
        whenever(mockShimmerDevice.isConnected())
            .thenReturn(true)
            .thenReturn(false) // Lost connection
            .thenReturn(true)  // Reconnected
        
        whenever(mockShimmerDevice.reconnect()).thenReturn(true)
        
        shimmerRecorder.setShimmerDevice(mockShimmerDevice)
        
        // Check initial connection
        assertTrue(shimmerRecorder.checkConnectionHealth())
        
        // Detect disconnection and trigger recovery
        assertFalse(shimmerRecorder.checkConnectionHealth())
        val recoveryResult = shimmerRecorder.attemptRecovery()
        
        assertTrue(recoveryResult.isSuccess)
        verify(mockShimmerDevice).reconnect()
    }

    @Test
    fun `test shimmer data validation`() {
        val validData = ShimmerSensorData(
            timestamp = System.currentTimeMillis(),
            gsr = 1.234f,
            ecg = 0.567f,
            emg = 0.890f,
            deviceId = "shimmer_001"
        )
        
        val invalidData = ShimmerSensorData(
            timestamp = -1, // Invalid timestamp
            gsr = Float.NaN, // Invalid GSR value
            ecg = Float.POSITIVE_INFINITY, // Invalid ECG value
            emg = 0.890f,
            deviceId = "" // Empty device ID
        )
        
        assertTrue(shimmerRecorder.validateSensorData(validData))
        assertFalse(shimmerRecorder.validateSensorData(invalidData))
    }

    /**
     * Multi-Modal Recording Coordination Tests
     */
    @Test
    fun `test synchronized multi-modal recording`() = runTest {
        val recordingSession = MultiModalRecordingSession(
            sessionId = "session_001",
            outputDirectory = File(mockContext.filesDir, "multi_modal"),
            components = listOf(
                RecordingComponent.CAMERA,
                RecordingComponent.THERMAL,
                RecordingComponent.SHIMMER
            )
        )
        
        // Setup all recorders
        cameraRecorder.setMediaRecorder(mockMediaRecorder)
        thermalRecorder.setThermalSensor(mockThermalSensor)
        shimmerRecorder.setShimmerDevice(mockShimmerDevice)
        
        val coordinator = MultiModalRecordingCoordinator(
            cameraRecorder = cameraRecorder,
            thermalRecorder = thermalRecorder,
            shimmerRecorder = shimmerRecorder
        )
        
        // Start synchronized recording
        val startResult = coordinator.startSynchronizedRecording(recordingSession)
        assertTrue(startResult.isSuccess)
        
        // Verify all components started
        assertTrue(coordinator.isRecording())
        verify(mockMediaRecorder).start()
        verify(mockShimmerDevice).startStreaming()
        
        // Stop synchronized recording
        val stopResult = coordinator.stopSynchronizedRecording()
        assertTrue(stopResult.isSuccess)
        
        verify(mockMediaRecorder).stop()
        verify(mockShimmerDevice).stopStreaming()
    }

    @Test
    fun `test recording timestamp synchronization`() {
        val masterTimestamp = System.currentTimeMillis()
        val synchronizer = RecordingTimestampSynchronizer()
        
        // Synchronize all components
        val syncResults = synchronizer.synchronizeComponents(
            masterTimestamp,
            listOf(cameraRecorder, thermalRecorder, shimmerRecorder)
        )
        
        assertTrue(syncResults.all { it.success })
        
        // Check timestamp alignment
        val timestamps = syncResults.map { it.synchronizedTimestamp }
        val maxOffset = timestamps.maxOrNull()!! - timestamps.minOrNull()!!
        
        // All components should be synchronized within 10ms
        assertTrue(maxOffset <= 10)
    }

    @Test
    fun `test recording error recovery coordination`() {
        val coordinator = MultiModalRecordingCoordinator(
            cameraRecorder = cameraRecorder,
            thermalRecorder = thermalRecorder,
            shimmerRecorder = shimmerRecorder
        )
        
        // Simulate camera error during recording
        whenever(mockMediaRecorder.start()).thenThrow(RuntimeException("Camera error"))
        
        val recordingSession = MultiModalRecordingSession(
            sessionId = "session_002",
            outputDirectory = File(mockContext.filesDir, "error_recovery"),
            components = listOf(RecordingComponent.CAMERA, RecordingComponent.THERMAL)
        )
        
        val result = coordinator.startSynchronizedRecording(recordingSession)
        
        // Should handle error gracefully
        assertTrue(result.isFailure)
        assertFalse(coordinator.isRecording())
        
        // Should attempt recovery
        val recoveryResult = coordinator.attemptRecovery()
        assertNotNull(recoveryResult)
    }

    @Test
    fun `test recording quality assessment`() {
        val qualityAssessor = RecordingQualityAssessor()
        
        val cameraMetrics = CameraQualityMetrics(
            resolution = Resolution(1920, 1080),
            frameRate = 30.0f,
            bitRate = 8000000,
            droppedFrames = 2,
            averageExposure = 0.5f
        )
        
        val thermalMetrics = ThermalQualityMetrics(
            samplingRate = 10.0f,
            temperatureStability = 0.1f,
            calibrationAccuracy = 0.05f,
            missedSamples = 0
        )
        
        val shimmerMetrics = ShimmerQualityMetrics(
            samplingRate = 512.0f,
            signalToNoise = 45.0f,
            synchronizationAccuracy = 2.0f,
            packetLoss = 0.1f
        )
        
        val overallQuality = qualityAssessor.assessOverallQuality(
            cameraMetrics,
            thermalMetrics,
            shimmerMetrics
        )
        
        assertTrue(overallQuality.score >= 0.0f)
        assertTrue(overallQuality.score <= 1.0f)
        assertNotNull(overallQuality.recommendations)
    }

    @Test
    fun `test recording storage management`() {
        val storageManager = RecordingStorageManager(mockContext)
        
        val session = RecordingSession(
            sessionId = "session_003",
            duration = 300000, // 5 minutes
            estimatedFileSize = 500 * 1024 * 1024 // 500 MB
        )
        
        // Check available storage
        val storageInfo = storageManager.getStorageInfo()
        assertNotNull(storageInfo.availableSpace)
        assertNotNull(storageInfo.totalSpace)
        
        // Validate storage capacity
        val hasCapacity = storageManager.validateStorageCapacity(session)
        assertTrue(hasCapacity is StorageValidationResult)
        
        // Cleanup old recordings if needed
        if (!hasCapacity.hasCapacity) {
            val cleanupResult = storageManager.cleanupOldRecordings(session.estimatedFileSize)
            assertTrue(cleanupResult.isSuccess)
        }
    }
}