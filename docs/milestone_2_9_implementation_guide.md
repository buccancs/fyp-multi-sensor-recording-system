# Milestone 2.9: Implementation Guide

## Overview
This guide provides implementation details for the advanced calibration system features in Milestone 2.9.

## Enhanced SyncClockManager Usage

### Basic Enhanced Synchronization
```kotlin
@Inject
lateinit var syncClockManager: SyncClockManager

// Enhanced NTP-style synchronization
val success = syncClockManager.synchronizeWithPc(pcTimestamp, "sync_001")

// Get quality metrics
val qualityMetrics = syncClockManager.getSyncQualityMetrics()
logger.info("Sync accuracy: ${qualityMetrics?.accuracy}ms")
```

### Quality Monitoring
```kotlin
// Check sync quality
val syncStatus = syncClockManager.getSyncStatus()
if (syncStatus.isSynchronized) {
    val qualityScore = syncClockManager.syncQualityScore
    when {
        qualityScore > 0.8f -> logger.info("Excellent sync quality")
        qualityScore > 0.6f -> logger.info("Good sync quality")
        else -> logger.warning("Poor sync quality - consider re-sync")
    }
}
```

## CalibrationQualityAssessment Usage

### Basic Quality Assessment
```kotlin
@Inject
lateinit var qualityAssessment: CalibrationQualityAssessment

// Assess calibration image pair
val qualityScore = qualityAssessment.assessCalibrationQuality(
    rgbImage = rgbBitmap,
    thermalImage = thermalBitmap
)

// Handle recommendation
when (qualityScore.recommendation) {
    QualityRecommendation.EXCELLENT -> acceptCalibration()
    QualityRecommendation.RETAKE_REQUIRED -> requestRetake()
    else -> showQualityFeedback(qualityScore)
}
```

### Detailed Analysis
```kotlin
// Get detailed analysis
logger.info("Overall Score: ${qualityScore.overallScore}")
logger.info("Pattern Score: ${qualityScore.patternDetectionScore}")
logger.info("Sharpness Score: ${qualityScore.sharpnessScore}")
logger.info("Analysis Details:\n${qualityScore.analysisDetails}")
```

## Integration with CalibrationCaptureManager

### Enhanced Capture Flow
```kotlin
class EnhancedCalibrationFlow @Inject constructor(
    private val captureManager: CalibrationCaptureManager,
    private val qualityAssessment: CalibrationQualityAssessment,
    private val syncManager: SyncClockManager
) {
    
    suspend fun performEnhancedCalibration(): CalibrationResult {
        // Ensure sync quality
        if (!syncManager.isSyncValid()) {
            syncManager.synchronizeWithPc(getCurrentPcTime())
        }
        
        // Capture with enhanced timing
        val captureResult = captureManager.captureCalibrationImages("enhanced_001")
        
        // Assess quality
        val qualityScore = qualityAssessment.assessCalibrationQuality(
            captureResult.rgbImage, captureResult.thermalImage
        )
        
        return CalibrationResult(captureResult, qualityScore)
    }
}
```

## Testing Implementation

### Unit Testing Enhanced Sync
```kotlin
@Test
fun testEnhancedSynchronization() {
    val pcTimestamp = System.currentTimeMillis()
    val success = syncClockManager.synchronizeWithPc(pcTimestamp)
    
    assertTrue(success)
    assertTrue(syncClockManager.isSyncValid())
    
    val metrics = syncClockManager.getSyncQualityMetrics()
    assertNotNull(metrics)
    assertTrue(metrics.accuracy < 10.0f) // ±10ms target
}
```

### Quality Assessment Testing
```kotlin
@Test
fun testQualityAssessment() {
    val mockRgbImage = createMockBitmap(1920, 1080)
    val mockThermalImage = createMockBitmap(640, 480)
    
    val result = runBlocking {
        qualityAssessment.assessCalibrationQuality(mockRgbImage, mockThermalImage)
    }
    
    assertTrue(result.overallScore >= 0.0f)
    assertTrue(result.overallScore <= 1.0f)
    assertNotNull(result.recommendation)
}
```

## Performance Considerations

### Memory Management
- Quality assessment processes large bitmaps - ensure proper disposal
- Sync measurements are limited to MAX_SYNC_SAMPLES (8) automatically
- Use background threads for quality assessment (already implemented)

### Optimization Tips
- Cache quality assessment results for identical images
- Monitor sync quality score and re-sync when below threshold
- Use appropriate image resolutions for quality assessment

## Error Handling

### Sync Errors
```kotlin
try {
    val success = syncClockManager.synchronizeWithPc(pcTimestamp)
    if (!success) {
        logger.error("Synchronization failed - check network connectivity")
        // Fallback to device time or retry
    }
} catch (e: Exception) {
    logger.error("Sync error: ${e.message}")
}
```

### Quality Assessment Errors
```kotlin
try {
    val quality = qualityAssessment.assessCalibrationQuality(rgb, thermal)
    if (quality.recommendation == QualityRecommendation.RETAKE_REQUIRED) {
        // Handle retake scenario
    }
} catch (e: Exception) {
    logger.error("Quality assessment failed: ${e.message}")
    // Use fallback quality scoring or manual review
}
```

## Configuration

### Sync Parameters
```kotlin
// Adjust sync parameters if needed (in SyncClockManager companion object)
private const val TARGET_ACCURACY_MS = 10L
private const val MAX_SYNC_SAMPLES = 8
private const val OUTLIER_THRESHOLD_FACTOR = 2.0
```

### Quality Thresholds
```kotlin
// Adjust quality thresholds (in CalibrationQualityAssessment companion object)
private const val MIN_SHARPNESS_SCORE = 0.3f
private const val MIN_CONTRAST_SCORE = 0.4f
private const val MIN_PATTERN_SCORE = 0.6f
private const val MIN_ALIGNMENT_SCORE = 0.5f
```

## Next Steps

1. Integrate enhanced features into existing calibration workflow
2. Test with real hardware on Samsung devices
3. Monitor performance and adjust thresholds as needed
4. Implement remaining multi-camera and preview features
5. Add OpenCV integration for full computer vision capabilities
