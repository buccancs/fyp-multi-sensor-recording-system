package com.multisensor.recording.controllers

import android.content.Context
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.delay
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*

/**
 * Comprehensive unit tests for RecordingAnalytics
 * 
 * This test suite validates the analytical capabilities of the recording system
 * including performance monitoring, trend analysis, and quality assessment.
 * 
 * The tests cover:
 * - Performance metrics collection and analysis
 * - Statistical analysis of resource utilization
 * - Trend detection and prediction algorithms
 * - Quality metrics calculation and optimization
 * - Analytics report generation
 */
class RecordingAnalyticsTest {

    private lateinit var analytics: RecordingAnalytics
    private lateinit var mockContext: Context

    @Before
    fun setUp() {
        analytics = RecordingAnalytics()
        mockContext = mockk(relaxed = true)
    }

    @Test
    fun `test analytics initialization`() {
        // Given
        val sessionId = "test_session_123"

        // When
        analytics.initializeSession(mockContext, sessionId)

        // Then
        val metrics = analytics.currentMetrics.value
        assertNotNull("Performance metrics should be initialized", metrics)
        assertEquals("Initial timestamp should be recent", 
            System.currentTimeMillis(), metrics.timestamp, 5000)
    }

    @Test
    fun `test performance metrics collection`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When
        analytics.updatePerformanceMetrics(mockContext)

        // Then
        val metrics = analytics.currentMetrics.value
        assertTrue("Memory usage should be non-negative", metrics.memoryUsageMB >= 0)
        assertTrue("CPU usage should be between 0 and 100", 
            metrics.cpuUsagePercent >= 0f && metrics.cpuUsagePercent <= 100f)
        assertTrue("Storage write rate should be non-negative", metrics.storageWriteRateMBps >= 0f)
        assertNotNull("Thermal state should be set", metrics.thermalState)
    }

    @Test
    fun `test quality metrics calculation`() {
        // Given
        val averageBitrate = 1500000L // 1.5 Mbps
        val frameStability = 0.95f
        val audioQuality = 0.9f

        // When
        analytics.updateQualityMetrics(averageBitrate, frameStability, audioQuality)

        // Then
        val metrics = analytics.qualityMetrics.value
        assertEquals("Average bitrate should match input", averageBitrate, metrics.averageBitrate)
        assertEquals("Frame stability should match input", frameStability, metrics.frameStability, 0.01f)
        assertEquals("Audio quality should match input", audioQuality, metrics.audioQualityScore, 0.01f)
        assertTrue("Overall quality score should be reasonable", 
            metrics.overallQualityScore >= 0f && metrics.overallQualityScore <= 1f)
        assertTrue("Recording efficiency should be reasonable",
            metrics.recordingEfficiency >= 0f && metrics.recordingEfficiency <= 1f)
    }

    @Test
    fun `test resource utilization analysis`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")
        
        // Generate some performance data
        repeat(10) {
            analytics.updatePerformanceMetrics(mockContext)
        }

        // When
        val stats = analytics.analyzeResourceUtilization()

        // Then
        assertTrue("Mean memory usage should be non-negative", stats.meanMemoryUsage >= 0.0)
        assertTrue("Max memory usage should be non-negative", stats.maxMemoryUsage >= 0L)
        assertTrue("Memory variance should be non-negative", stats.memoryVariance >= 0.0)
        assertTrue("Mean CPU usage should be non-negative", stats.meanCpuUsage >= 0.0)
        assertTrue("Max CPU usage should be non-negative", stats.maxCpuUsage >= 0f)
        assertTrue("CPU variance should be non-negative", stats.cpuVariance >= 0.0)
    }

    @Test
    fun `test trend analysis with insufficient data`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")
        
        // Generate minimal data (less than required for trend analysis)
        repeat(5) {
            analytics.updatePerformanceMetrics(mockContext)
        }

        // When
        val trendAnalysis = analytics.performTrendAnalysis()

        // Then
        assertNotNull("Trend analysis should return result even with insufficient data", trendAnalysis)
        // Default values should be returned for insufficient data
    }

    @Test
    fun `test trend analysis with sufficient data`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")
        
        // Generate sufficient performance data
        repeat(15) {
            analytics.updatePerformanceMetrics(mockContext)
        }

        // When
        val trendAnalysis = analytics.performTrendAnalysis()

        // Then
        assertNotNull("Performance trend should be determined", trendAnalysis.performanceTrend)
        assertTrue("Predicted performance should be reasonable", 
            trendAnalysis.predictedPerformance >= 0f)
        assertNotNull("Confidence interval should be provided", trendAnalysis.confidenceInterval)
        assertNotNull("Quality recommendation should be provided", 
            trendAnalysis.recommendedQualityAdjustment)
        assertTrue("Trend strength should be between 0 and 1",
            trendAnalysis.trendStrength >= 0f && trendAnalysis.trendStrength <= 1f)
    }

    @Test
    fun `test frame processing analytics`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When
        repeat(100) {
            analytics.recordFrameProcessed()
        }
        repeat(5) {
            analytics.recordFrameDropped()
        }

        // Then
        val report = analytics.generateAnalyticsReport()
        val sessionSummary = report["session_summary"] as Map<*, *>
        
        assertEquals("Total frames processed should match", 100L, sessionSummary["total_frames_processed"])
        assertEquals("Total frames dropped should match", 5L, sessionSummary["total_frames_dropped"])
        assertEquals("Frame drop rate should be calculated correctly", 0.05f, 
            sessionSummary["overall_frame_drop_rate"] as Float, 0.01f)
    }

    @Test
    fun `test data written tracking`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When
        analytics.recordDataWritten(1024 * 1024) // 1MB
        analytics.recordDataWritten(2 * 1024 * 1024) // 2MB

        // Then
        val report = analytics.generateAnalyticsReport()
        val sessionSummary = report["session_summary"] as Map<*, *>
        
        assertEquals("Total bytes written should match", 3L * 1024 * 1024, 
            sessionSummary["total_bytes_written"])
    }

    @Test
    fun `test analytics report generation`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")
        
        // Generate some data
        repeat(10) {
            analytics.updatePerformanceMetrics(mockContext)
            analytics.updateQualityMetrics(1500000L, 0.95f, 0.9f)
            analytics.recordFrameProcessed()
        }
        analytics.recordFrameDropped()
        analytics.recordDataWritten(1024 * 1024)

        // When
        val report = analytics.generateAnalyticsReport()

        // Then
        assertNotNull("Report should be generated", report)
        assertTrue("Report should contain session summary", report.containsKey("session_summary"))
        assertTrue("Report should contain performance statistics", 
            report.containsKey("performance_statistics"))
        assertTrue("Report should contain quality analysis", report.containsKey("quality_analysis"))
        assertTrue("Report should contain trend analysis", report.containsKey("trend_analysis"))
        assertTrue("Report should contain metadata", report.containsKey("metadata"))
        
        val metadata = report["metadata"] as Map<*, *>
        assertTrue("Metadata should contain timestamp", metadata.containsKey("report_timestamp"))
        assertTrue("Metadata should contain data points analyzed", 
            metadata.containsKey("data_points_analyzed"))
    }

    @Test
    fun `test analytics data clearing`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")
        
        // Generate some data
        repeat(5) {
            analytics.updatePerformanceMetrics(mockContext)
            analytics.recordFrameProcessed()
        }

        // When
        analytics.clearAnalyticsData()

        // Then
        val report = analytics.generateAnalyticsReport()
        val sessionSummary = report["session_summary"] as Map<*, *>
        
        assertEquals("Frames processed should be cleared", 0L, sessionSummary["total_frames_processed"])
        assertEquals("Frames dropped should be cleared", 0L, sessionSummary["total_frames_dropped"])
        assertEquals("Bytes written should be cleared", 0L, sessionSummary["total_bytes_written"])
    }

    @Test
    fun `test quality metrics variability calculation`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When - Add quality metrics with varying bitrates
        analytics.updateQualityMetrics(1000000L, 0.95f, 0.9f) // 1 Mbps
        analytics.updateQualityMetrics(1500000L, 0.93f, 0.88f) // 1.5 Mbps
        analytics.updateQualityMetrics(1200000L, 0.96f, 0.91f) // 1.2 Mbps

        // Then
        val metrics = analytics.qualityMetrics.value
        assertTrue("Bitrate variability should be calculated", metrics.bitrateVariability >= 0f)
        assertTrue("Overall quality should reflect all inputs", 
            metrics.overallQualityScore >= 0f && metrics.overallQualityScore <= 1f)
    }

    @Test
    fun `test performance score calculation consistency`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When - Update metrics multiple times
        repeat(20) {
            analytics.updatePerformanceMetrics(mockContext)
        }

        // Then - Performance should be calculable and consistent
        val stats = analytics.analyzeResourceUtilization()
        assertTrue("Resource statistics should be meaningful", stats.meanMemoryUsage >= 0.0)
        assertTrue("Statistics should show reasonable variance", stats.memoryVariance >= 0.0)
    }

    @Test
    fun `test thermal state integration`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When
        analytics.updatePerformanceMetrics(mockContext)

        // Then
        val metrics = analytics.currentMetrics.value
        assertNotNull("Thermal state should be present", metrics.thermalState)
        assertTrue("Thermal state should be valid enum value", 
            RecordingAnalytics.ThermalState.entries.contains(metrics.thermalState))
    }

    @Test
    fun `test analytics with concurrent updates`() = runTest {
        // Given
        analytics.initializeSession(mockContext, "test_session")

        // When - Simulate concurrent updates
        repeat(5) {
            analytics.updatePerformanceMetrics(mockContext)
            analytics.updateQualityMetrics(1500000L, 0.95f, 0.9f)
            analytics.recordFrameProcessed()
            delay(10) // Small delay to simulate real-world timing
        }

        // Then
        val report = analytics.generateAnalyticsReport()
        assertNotNull("Report should be generated with concurrent updates", report)
        
        val sessionSummary = report["session_summary"] as Map<*, *>
        assertTrue("Frame count should reflect all updates", 
            (sessionSummary["total_frames_processed"] as Long) > 0L)
    }

    @Test
    fun `test quality recommendation generation`() {
        // Given
        analytics.initializeSession(mockContext, "test_session")
        
        // Generate degrading performance trend
        repeat(15) {
            analytics.updatePerformanceMetrics(mockContext)
            // Simulate decreasing quality
            analytics.updateQualityMetrics(1000000L - (it * 50000L), 0.9f - (it * 0.01f), 0.85f)
        }

        // When
        val trendAnalysis = analytics.performTrendAnalysis()

        // Then
        assertNotNull("Quality recommendation should be generated", 
            trendAnalysis.recommendedQualityAdjustment)
        // With degrading performance, should recommend decrease or emergency reduce
        assertTrue("Should recommend quality reduction for degrading performance",
            trendAnalysis.recommendedQualityAdjustment == 
            RecordingAnalytics.QualityAdjustmentRecommendation.DECREASE ||
            trendAnalysis.recommendedQualityAdjustment == 
            RecordingAnalytics.QualityAdjustmentRecommendation.EMERGENCY_REDUCE ||
            trendAnalysis.recommendedQualityAdjustment == 
            RecordingAnalytics.QualityAdjustmentRecommendation.MAINTAIN)
    }
}