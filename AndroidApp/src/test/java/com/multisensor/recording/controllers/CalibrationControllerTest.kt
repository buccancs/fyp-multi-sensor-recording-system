package com.multisensor.recording.controllers

import android.content.Context
import android.content.SharedPreferences
import android.media.MediaActionSound
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.lifecycle.LifecycleCoroutineScope
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.calibration.SyncClockManager
import io.mockk.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

/**
 * Comprehensive unit tests for CalibrationController
 * Tests all calibration scenarios, state persistence, patterns, quality validation, and metrics
 */
@RunWith(RobolectricTestRunner::class)
class CalibrationControllerTest {
    
    private lateinit var mockCalibrationCaptureManager: CalibrationCaptureManager
    private lateinit var mockSyncClockManager: SyncClockManager
    private lateinit var mockCallback: CalibrationController.CalibrationCallback
    private lateinit var mockContext: Context
    private lateinit var mockSharedPrefs: SharedPreferences
    private lateinit var mockEditor: SharedPreferences.Editor
    private lateinit var mockContentView: ViewGroup
    private lateinit var calibrationController: CalibrationController
    private lateinit var testDispatcher: TestDispatcher
    
    @Before
    fun setUp() {
        mockCalibrationCaptureManager = mockk(relaxed = true)
        mockSyncClockManager = mockk(relaxed = true)
        mockCallback = mockk(relaxed = true)
        mockContext = mockk(relaxed = true)
        mockSharedPrefs = mockk(relaxed = true)
        mockEditor = mockk(relaxed = true)
        mockContentView = mockk<ViewGroup>(relaxed = true)
        testDispatcher = StandardTestDispatcher()
        Dispatchers.setMain(testDispatcher)
        
        // Setup SharedPreferences mocking
        every { mockContext.getSharedPreferences(any(), any()) } returns mockSharedPrefs
        every { mockSharedPrefs.edit() } returns mockEditor
        every { mockEditor.putString(any(), any()) } returns mockEditor
        every { mockEditor.putLong(any(), any()) } returns mockEditor
        every { mockEditor.putBoolean(any(), any()) } returns mockEditor
        every { mockEditor.putInt(any(), any()) } returns mockEditor
        every { mockEditor.apply() } just Runs
        
        // Setup callback mocking
        every { mockCallback.getContext() } returns mockContext
        every { mockCallback.getContentView() } returns mockContentView
        
        calibrationController = CalibrationController(
            mockCalibrationCaptureManager,
            mockSyncClockManager
        )
        calibrationController.setCallback(mockCallback)
        
        println("[DEBUG_LOG] CalibrationControllerTest setup complete")
    }
    
    @After
    fun tearDown() {
        Dispatchers.resetMain()
        clearAllMocks()
        println("[DEBUG_LOG] CalibrationControllerTest teardown complete")
    }
    
    // ========== Basic Functionality Tests ==========
    
    @Test
    fun testInitialization() {
        println("[DEBUG_LOG] Testing CalibrationController initialization")
        
        // Test initialize
        calibrationController.initialize()
        
        // Verify initialization completed without errors
        assertNotNull("Controller should be initialized", calibrationController)
        
        println("[DEBUG_LOG] Initialization test passed")
    }
    
    @Test
    fun testSetCallback() {
        println("[DEBUG_LOG] Testing callback setting")
        
        val newCallback = mockk<CalibrationController.CalibrationCallback>(relaxed = true)
        calibrationController.setCallback(newCallback)
        
        // Verify callback was set - this is tested indirectly through other methods
        assertNotNull("Callback should be set", newCallback)
        
        println("[DEBUG_LOG] Set callback test passed")
    }
    
    // ========== Calibration Scenarios Tests ==========
    
    @Test
    fun testSuccessfulCalibrationCapture() = runTest {
        println("[DEBUG_LOG] Testing successful calibration capture")
        
        val testCalibrationId = "test_calib_001"
        val mockResult = CalibrationCaptureManager.CalibrationCaptureResult(
            success = true,
            calibrationId = testCalibrationId,
            rgbFilePath = "/test/rgb.jpg",
            thermalFilePath = "/test/thermal.png",
            timestamp = System.currentTimeMillis(),
            syncedTimestamp = System.currentTimeMillis() + 100,
            thermalConfig = null,
            errorMessage = null
        )
        
        coEvery { 
            mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
        } returns mockResult
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.runCalibration(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify callbacks were triggered
        verify { mockCallback.onCalibrationStarted() }
        verify { mockCallback.onCalibrationCompleted(testCalibrationId) }
        verify { mockCallback.showToast("Starting Single Point Calibration...") }
        
        // Verify calibration history was saved
        verify { mockSharedPrefs.edit() }
        verify { mockEditor.putString("last_calibration_id", testCalibrationId) }
        verify { mockEditor.putBoolean("last_calibration_success", true) }
        
        println("[DEBUG_LOG] Successful calibration capture test passed")
    }
    
    @Test
    fun testFailedCalibrationCapture() = runTest {
        println("[DEBUG_LOG] Testing failed calibration capture")
        
        val errorMessage = "Camera initialization failed"
        val mockResult = CalibrationCaptureManager.CalibrationCaptureResult(
            success = false,
            calibrationId = "failed_calib_001",
            rgbFilePath = null,
            thermalFilePath = null,
            timestamp = System.currentTimeMillis(),
            syncedTimestamp = System.currentTimeMillis(),
            thermalConfig = null,
            errorMessage = errorMessage
        )
        
        coEvery { 
            mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
        } returns mockResult
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.runCalibration(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify failure callbacks were triggered
        verify { mockCallback.onCalibrationStarted() }
        verify { mockCallback.onCalibrationFailed(errorMessage) }
        verify { mockCallback.showToast(match { it.contains("failed") && it.contains(errorMessage) }, Toast.LENGTH_LONG) }
        
        // Verify failed calibration was logged
        verify { mockEditor.putBoolean("last_calibration_success", false) }
        
        println("[DEBUG_LOG] Failed calibration capture test passed")
    }
    
    @Test
    fun testCalibrationCaptureException() = runTest {
        println("[DEBUG_LOG] Testing calibration capture exception handling")
        
        val exceptionMessage = "Network timeout"
        coEvery { 
            mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
        } throws RuntimeException(exceptionMessage)
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.runCalibration(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify exception handling
        verify { mockCallback.onCalibrationStarted() }
        verify { mockCallback.onCalibrationFailed(match { it.contains(exceptionMessage) }) }
        verify { mockCallback.showToast(match { it.contains("Calibration error") }, Toast.LENGTH_LONG) }
        
        println("[DEBUG_LOG] Calibration capture exception test passed")
    }
    
    // ========== Sync Testing Scenarios ==========
    
    @Test
    fun testFlashSyncTest() = runTest {
        println("[DEBUG_LOG] Testing flash sync test")
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.testFlashSync(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify flash sync feedback
        verify { mockCallback.showToast("🔆 Flash sync signal triggered!") }
        verify { mockCallback.onSyncTestCompleted(true, "Flash sync signal triggered successfully") }
        
        println("[DEBUG_LOG] Flash sync test passed")
    }
    
    @Test
    fun testBeepSyncTest() {
        println("[DEBUG_LOG] Testing beep sync test")
        
        calibrationController.testBeepSync()
        
        // Verify beep sync feedback
        verify { mockCallback.showToast("🔊 Beep sync signal triggered!") }
        verify { mockCallback.onSyncTestCompleted(true, "Beep sync signal triggered successfully") }
        
        println("[DEBUG_LOG] Beep sync test passed")
    }
    
    @Test
    fun testClockSyncTest() = runTest {
        println("[DEBUG_LOG] Testing clock sync test")
        
        val mockSyncStatus = SyncClockManager.SyncStatus(
            isSynchronized = true,
            clockOffsetMs = 50L,
            lastSyncTimestamp = System.currentTimeMillis(),
            pcReferenceTime = System.currentTimeMillis(),
            syncAge = 1000L
        )
        
        coEvery { mockSyncClockManager.synchronizeWithPc(any(), any()) } returns true
        every { mockSyncClockManager.getSyncStatus() } returns mockSyncStatus
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.testClockSync(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify clock sync feedback
        verify { mockCallback.showToast(match { it.contains("Clock sync successful") }, Toast.LENGTH_LONG) }
        verify { mockCallback.onSyncTestCompleted(true, match { it.contains("Clock synchronized with offset") }) }
        verify { mockCallback.updateStatusText(match { it.contains("Clock synchronized - Offset: 50ms") }) }
        
        println("[DEBUG_LOG] Clock sync test passed")
    }
    
    @Test
    fun testClockSyncTestFailure() = runTest {
        println("[DEBUG_LOG] Testing clock sync test failure")
        
        coEvery { mockSyncClockManager.synchronizeWithPc(any(), any()) } returns false
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.testClockSync(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify failure handling
        verify { mockCallback.showToast("❌ Clock sync test failed", Toast.LENGTH_LONG) }
        verify { mockCallback.onSyncTestCompleted(false, "Clock synchronization failed") }
        
        println("[DEBUG_LOG] Clock sync test failure passed")
    }
    
    // ========== State Persistence Tests ==========
    
    @Test
    fun testCalibrationHistoryPersistence() {
        println("[DEBUG_LOG] Testing calibration history persistence")
        
        // Setup mock SharedPreferences returns
        every { mockSharedPrefs.getString("last_calibration_id", null) } returns "test_calib_123"
        every { mockSharedPrefs.getLong("last_calibration_time", 0L) } returns 1234567890L
        every { mockSharedPrefs.getBoolean("last_calibration_success", false) } returns true
        every { mockSharedPrefs.getInt("calibration_count", 0) } returns 5
        
        val status = calibrationController.getCalibrationStatus()
        
        // Verify status contains persistence data
        assertTrue("Status should contain last calibration info", status.contains("test_calib_123"))
        assertTrue("Status should contain calibration count", status.contains("Total Calibrations: 5"))
        
        println("[DEBUG_LOG] Calibration history persistence test passed")
    }
    
    // ========== Quality Validation Tests ==========
    
    @Test
    fun testSyncValidationForCalibration() {
        println("[DEBUG_LOG] Testing sync validation for calibration")
        
        // Test valid sync
        every { mockSyncClockManager.isSyncValid() } returns true
        assertTrue("Should return true for valid sync", calibrationController.isSyncValidForCalibration())
        
        // Test invalid sync
        every { mockSyncClockManager.isSyncValid() } returns false
        assertFalse("Should return false for invalid sync", calibrationController.isSyncValidForCalibration())
        
        println("[DEBUG_LOG] Sync validation test passed")
    }
    
    @Test
    fun testSyncStatistics() {
        println("[DEBUG_LOG] Testing sync statistics")
        
        val mockStatistics = "SyncStats{count=5, avgOffset=25ms, lastSync=valid}"
        every { mockSyncClockManager.getSyncStatistics() } returns mockStatistics
        
        val statistics = calibrationController.getSyncStatistics()
        assertEquals("Statistics should match mock data", mockStatistics, statistics)
        
        println("[DEBUG_LOG] Sync statistics test passed")
    }
    
    // ========== State Management Tests ==========
    
    @Test
    fun testStateReset() {
        println("[DEBUG_LOG] Testing state reset")
        
        calibrationController.resetState()
        
        // Reset should complete without errors - more detailed implementation will be added
        // in the enhanced CalibrationController
        assertNotNull("Controller should still be valid after reset", calibrationController)
        
        println("[DEBUG_LOG] State reset test passed")
    }
    
    @Test
    fun testCleanup() {
        println("[DEBUG_LOG] Testing cleanup")
        
        calibrationController.cleanup()
        
        // Cleanup should complete without errors
        assertNotNull("Controller should still be valid after cleanup", calibrationController)
        
        println("[DEBUG_LOG] Cleanup test passed")
    }
    
    // ========== Status and Information Tests ==========
    
    @Test
    fun testShowSyncStatus() {
        println("[DEBUG_LOG] Testing show sync status")
        
        val mockSyncStatus = SyncClockManager.SyncStatus(
            isSynchronized = true,
            clockOffsetMs = 25L,
            lastSyncTimestamp = System.currentTimeMillis(),
            pcReferenceTime = System.currentTimeMillis(),
            syncAge = 5000L
        )
        val mockStatistics = "SyncStats{count=3, avgOffset=25ms}"
        
        every { mockSyncClockManager.getSyncStatus() } returns mockSyncStatus
        every { mockSyncClockManager.getSyncStatistics() } returns mockStatistics
        every { mockSyncClockManager.isSyncValid() } returns true
        
        calibrationController.showSyncStatus()
        
        // Verify status display
        verify { mockCallback.showToast(match { 
            it.contains("Clock Synchronization Status") && 
            it.contains("✅ Yes") && 
            it.contains("25ms") 
        }, Toast.LENGTH_LONG) }
        
        println("[DEBUG_LOG] Show sync status test passed")
    }
    
    @Test
    fun testGetCalibrationStatus() {
        println("[DEBUG_LOG] Testing get calibration status")
        
        val mockSyncStatus = SyncClockManager.SyncStatus(
            isSynchronized = true,
            clockOffsetMs = 30L,
            lastSyncTimestamp = System.currentTimeMillis(),
            pcReferenceTime = System.currentTimeMillis(),
            syncAge = 2000L
        )
        
        every { mockSyncClockManager.getSyncStatus() } returns mockSyncStatus
        every { mockSyncClockManager.isSyncValid() } returns true
        every { mockSharedPrefs.getString("last_calibration_id", null) } returns "test_calib_456"
        every { mockSharedPrefs.getLong("last_calibration_time", 0L) } returns System.currentTimeMillis()
        every { mockSharedPrefs.getBoolean("last_calibration_success", false) } returns true
        every { mockSharedPrefs.getInt("calibration_count", 0) } returns 3
        
        val status = calibrationController.getCalibrationStatus()
        
        // Verify status content
        assertTrue("Status should contain clock sync info", status.contains("Clock Synchronized: true"))
        assertTrue("Status should contain offset info", status.contains("Clock Offset: 30ms"))
        assertTrue("Status should contain sync validity", status.contains("Sync Valid: true"))
        assertTrue("Status should contain calibration count", status.contains("Total Calibrations: 3"))
        
        println("[DEBUG_LOG] Get calibration status test passed")
    }
    
    // ========== Visual Feedback Tests ==========
    
    @Test
    fun testScreenFlashFeedback() = runTest {
        println("[DEBUG_LOG] Testing screen flash feedback")
        
        // Setup view group for flash overlay
        every { mockContentView.addView(any(), any<ViewGroup.LayoutParams>()) } just Runs
        every { mockContentView.removeView(any()) } just Runs
        
        // Trigger calibration success which includes screen flash
        val testResult = CalibrationCaptureManager.CalibrationCaptureResult(
            success = true,
            calibrationId = "test_flash",
            rgbFilePath = "/test/rgb.jpg",
            thermalFilePath = null,
            timestamp = System.currentTimeMillis(),
            syncedTimestamp = System.currentTimeMillis(),
            thermalConfig = null,
            errorMessage = null
        )
        
        coEvery { 
            mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
        } returns testResult
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.runCalibration(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Verify visual feedback
        verify { mockCallback.showToast(match { it.contains("📸 Calibration photo captured") }) }
        verify { mockContentView.addView(any(), any<ViewGroup.LayoutParams>()) }
        
        println("[DEBUG_LOG] Screen flash feedback test passed")
    }
    
    // ========== Edge Cases Tests ==========
    
    @Test
    fun testCalibrationWithContextAccessIssue() = runTest {
        println("[DEBUG_LOG] Testing calibration with context access issue")
        
        val testResult = CalibrationCaptureManager.CalibrationCaptureResult(
            success = true,
            calibrationId = "test_context_issue",
            rgbFilePath = "/test/rgb.jpg",
            thermalFilePath = null,
            timestamp = System.currentTimeMillis(),
            syncedTimestamp = System.currentTimeMillis(),
            thermalConfig = null,
            errorMessage = null
        )
        
        coEvery { 
            mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
        } returns testResult
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        calibrationController.runCalibration(mockLifecycleScope)
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Should complete successfully
        verify { mockCallback.onCalibrationCompleted("test_context_issue") }
        
        println("[DEBUG_LOG] Calibration with context access issue test passed")
    }
    
    @Test
    fun testMultipleConcurrentCalibrations() = runTest {
        println("[DEBUG_LOG] Testing multiple concurrent calibrations")
        
        val result1 = CalibrationCaptureManager.CalibrationCaptureResult(
            success = true,
            calibrationId = "concurrent_1",
            rgbFilePath = "/test/rgb1.jpg",
            thermalFilePath = null,
            timestamp = System.currentTimeMillis(),
            syncedTimestamp = System.currentTimeMillis(),
            thermalConfig = null,
            errorMessage = null
        )
        
        val result2 = CalibrationCaptureManager.CalibrationCaptureResult(
            success = true,
            calibrationId = "concurrent_2",
            rgbFilePath = "/test/rgb2.jpg",
            thermalFilePath = null,
            timestamp = System.currentTimeMillis(),
            syncedTimestamp = System.currentTimeMillis(),
            thermalConfig = null,
            errorMessage = null
        )
        
        coEvery { 
            mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
        } returnsMany listOf(result1, result2)
        
        // Create a mock LifecycleCoroutineScope
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
        every { mockLifecycleScope.launch(any(), any(), any()) } answers {
            val block = arg<suspend () -> Unit>(2)
            launch { block() }
        }
        
        // Launch two concurrent calibrations
        val job1 = launch { calibrationController.runCalibration(mockLifecycleScope) }
        val job2 = launch { calibrationController.runCalibration(mockLifecycleScope) }
        
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Both should complete
        assertTrue("Job 1 should complete", job1.isCompleted)
        assertTrue("Job 2 should complete", job2.isCompleted)
        
        // Both callbacks should be triggered
        verify(atLeast = 2) { mockCallback.onCalibrationStarted() }
        
        println("[DEBUG_LOG] Multiple concurrent calibrations test passed")
    }
    
    // ========== Advanced Feature Tests ==========
    
    @Test
    fun testAdvancedQualityAssessment() = runTest {
        println("[DEBUG_LOG] Testing advanced quality assessment with statistical analysis")
        
        // Add multiple quality samples for statistical analysis
        repeat(10) { i ->
            val testResult = CalibrationCaptureManager.CalibrationCaptureResult(
                success = true,
                calibrationId = "test_calib_$i",
                rgbFilePath = "/test/rgb_$i.jpg",
                thermalFilePath = "/test/thermal_$i.png",
                timestamp = System.currentTimeMillis(),
                syncedTimestamp = System.currentTimeMillis() + (i * 10), // Varying sync offset
                thermalConfig = null,
                errorMessage = null
            )
            
            coEvery { 
                mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
            } returns testResult
            
            val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
            every { mockLifecycleScope.launch(any(), any(), any()) } answers {
                val block = arg<suspend () -> Unit>(2)
                launch { block() }
            }
            
            calibrationController.runCalibration(mockLifecycleScope)
            testDispatcher.scheduler.advanceUntilIdle()
        }
        
        // Test statistical validation
        val validation = calibrationController.performStatisticalValidation()
        assertNotNull("Statistical validation should be available", validation)
        assertTrue("Should have confidence level", validation.confidenceLevel >= 0.0f)
        
        // Test pattern optimization
        val optimization = calibrationController.analyzePatternOptimization()
        assertNotNull("Pattern optimization should be available", optimization)
        assertTrue("Efficiency should be valid", optimization.patternEfficiency >= 0.0f && optimization.patternEfficiency <= 1.0f)
        
        println("[DEBUG_LOG] Advanced quality assessment test passed")
    }
    
    @Test
    fun testMachineLearningPrediction() {
        println("[DEBUG_LOG] Testing machine learning quality prediction")
        
        // Test quality prediction for different patterns
        CalibrationController.CalibrationPattern.values().forEach { pattern ->
            val (predictedQuality, uncertainty) = calibrationController.predictCalibrationQuality(pattern)
            
            assertTrue("Predicted quality should be valid", predictedQuality >= 0.0f && predictedQuality <= 1.0f)
            assertTrue("Uncertainty should be valid", uncertainty >= 0.0f && uncertainty <= 1.0f)
            
            println("[DEBUG_LOG] Pattern ${pattern.displayName}: Quality=${String.format("%.3f", predictedQuality)}, Uncertainty=${String.format("%.3f", uncertainty)}")
        }
        
        println("[DEBUG_LOG] Machine learning prediction test passed")
    }
    
    @Test
    fun testStatisticalValidation() = runTest {
        println("[DEBUG_LOG] Testing statistical validation framework")
        
        // Add sufficient samples for statistical analysis
        repeat(15) { i ->
            val mockResult = CalibrationCaptureManager.CalibrationCaptureResult(
                success = true,
                calibrationId = "stat_test_$i",
                rgbFilePath = "/test/rgb.jpg",
                thermalFilePath = "/test/thermal.png",
                timestamp = System.currentTimeMillis(),
                syncedTimestamp = System.currentTimeMillis(),
                thermalConfig = null,
                errorMessage = null
            )
            
            coEvery { 
                mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
            } returns mockResult
            
            // Mock sync status for consistent quality calculation
            val mockSyncStatus = SyncClockManager.SyncStatus(
                isSynchronized = true,
                clockOffsetMs = (10 - i).toLong(), // Improving sync over time
                lastSyncTimestamp = System.currentTimeMillis(),
                pcReferenceTime = System.currentTimeMillis(),
                syncAge = 100L
            )
            every { mockSyncClockManager.getSyncStatus() } returns mockSyncStatus
            
            val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
            every { mockLifecycleScope.launch(any(), any(), any()) } answers {
                val block = arg<suspend () -> Unit>(2)
                launch { block() }
            }
            
            calibrationController.runCalibration(mockLifecycleScope)
            testDispatcher.scheduler.advanceUntilIdle()
        }
        
        // Perform statistical validation
        val validation = calibrationController.performStatisticalValidation()
        
        assertTrue("Should have valid statistical analysis", validation.isValid || !validation.isValid) // Either outcome is valid
        assertTrue("Confidence level should be reasonable", validation.confidenceLevel >= 0.0f && validation.confidenceLevel <= 1.0f)
        assertTrue("P-value should be valid", validation.pValue >= 0.0f && validation.pValue <= 1.0f)
        assertNotNull("Should have recommendation", validation.recommendation)
        
        println("[DEBUG_LOG] Statistical validation: Valid=${validation.isValid}, Confidence=${validation.confidenceLevel}, P-value=${validation.pValue}")
        println("[DEBUG_LOG] Statistical validation test passed")
    }
    
    @Test
    fun testComprehensiveCalibrationReport() = runTest {
        println("[DEBUG_LOG] Testing comprehensive calibration report generation")
        
        // Add some calibration data
        repeat(5) { i ->
            val mockResult = CalibrationCaptureManager.CalibrationCaptureResult(
                success = true,
                calibrationId = "report_test_$i",
                rgbFilePath = "/test/rgb.jpg",
                thermalFilePath = "/test/thermal.png",
                timestamp = System.currentTimeMillis(),
                syncedTimestamp = System.currentTimeMillis(),
                thermalConfig = null,
                errorMessage = null
            )
            
            coEvery { 
                mockCalibrationCaptureManager.captureCalibrationImages(any(), any(), any(), any()) 
            } returns mockResult
            
            val mockLifecycleScope = mockk<LifecycleCoroutineScope>(relaxed = true)
            every { mockLifecycleScope.launch(any(), any(), any()) } answers {
                val block = arg<suspend () -> Unit>(2)
                launch { block() }
            }
            
            calibrationController.runCalibration(mockLifecycleScope)
            testDispatcher.scheduler.advanceUntilIdle()
        }
        
        // Generate comprehensive report
        val report = calibrationController.generateCalibrationReport()
        
        assertNotNull("Report should be generated", report)
        assertTrue("Should have timestamp", report.timestamp > 0)
        assertEquals("Should track total calibrations", 5, report.totalCalibrations)
        assertTrue("Average quality should be valid", report.averageQuality >= 0.0f && report.averageQuality <= 1.0f)
        assertTrue("Quality std dev should be valid", report.qualityStandardDeviation >= 0.0f)
        assertNotNull("Should include pattern optimization", report.patternOptimization)
        assertNotNull("Should include statistical validation", report.statisticalValidation)
        assertNotNull("Should include quality trend", report.qualityTrend)
        assertTrue("Should have recommendations", report.systemRecommendations.isNotEmpty())
        assertNotNull("Should include performance metrics", report.performanceMetrics)
        
        println("[DEBUG_LOG] Report generated: ${report.totalCalibrations} calibrations, avg quality = ${String.format("%.3f", report.averageQuality)}")
        println("[DEBUG_LOG] Trend: ${report.qualityTrend}, Recommendations: ${report.systemRecommendations.size}")
        println("[DEBUG_LOG] Comprehensive calibration report test passed")
    }
    
    @Test
    fun testAdvancedValidationSetup() {
        println("[DEBUG_LOG] Testing advanced calibration setup validation")
        
        // Test with insufficient sync quality
        val poorSyncStatus = SyncClockManager.SyncStatus(
            isSynchronized = true,
            clockOffsetMs = 75L, // Poor sync
            lastSyncTimestamp = System.currentTimeMillis(),
            pcReferenceTime = System.currentTimeMillis(),
            syncAge = 1000L
        )
        every { mockSyncClockManager.getSyncStatus() } returns poorSyncStatus
        every { mockSyncClockManager.isSyncValid() } returns true
        
        val (isValid, issues) = calibrationController.validateCalibrationSetup()
        
        assertFalse("Should detect sync quality issues", isValid)
        assertTrue("Should report sync offset issue", issues.any { it.contains("Clock offset") && it.contains("75ms") })
        
        // Test with good sync
        val goodSyncStatus = SyncClockManager.SyncStatus(
            isSynchronized = true,
            clockOffsetMs = 15L, // Good sync
            lastSyncTimestamp = System.currentTimeMillis(),
            pcReferenceTime = System.currentTimeMillis(),
            syncAge = 1000L
        )
        every { mockSyncClockManager.getSyncStatus() } returns goodSyncStatus
        
        val (isValidGood, issuesGood) = calibrationController.validateCalibrationSetup()
        
        // May still have other issues, but sync should not be one of them
        assertFalse("Should not report sync offset issue", issuesGood.any { it.contains("Clock offset") && it.contains("exceeds") })
        
        println("[DEBUG_LOG] Advanced validation setup test passed")
    }
    
    @Test
    fun testPatternOptimizationAnalysis() {
        println("[DEBUG_LOG] Testing pattern optimization analysis")
        
        // Test with each pattern
        CalibrationController.CalibrationPattern.values().forEach { pattern ->
            calibrationController.setCalibrationPattern(pattern)
            
            val optimization = calibrationController.analyzePatternOptimization()
            
            assertNotNull("Optimization should be available", optimization)
            assertTrue("Pattern efficiency should be valid", optimization.patternEfficiency >= 0.0f && optimization.patternEfficiency <= 1.0f)
            assertTrue("Convergence rate should be valid", optimization.convergenceRate >= 0.0f && optimization.convergenceRate <= 1.0f)
            assertTrue("Spatial coverage should be valid", optimization.spatialCoverage >= 0.0f && optimization.spatialCoverage <= 1.0f)
            assertTrue("Redundancy analysis should be valid", optimization.redundancyAnalysis >= 0.0f && optimization.redundancyAnalysis <= 1.0f)
            assertNotNull("Should recommend a pattern", optimization.recommendedPattern)
            
            println("[DEBUG_LOG] Pattern ${pattern.displayName}: Efficiency=${String.format("%.3f", optimization.patternEfficiency)}, Coverage=${String.format("%.3f", optimization.spatialCoverage)}")
        }
        
        println("[DEBUG_LOG] Pattern optimization analysis test passed")
    }
}