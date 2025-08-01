package com.multisensor.recording.testfixtures

import com.multisensor.recording.network.NetworkQualityMonitor.NetworkQuality

/**
 * Test data factory for network and recording related objects
 * Provides consistent test data creation with sensible defaults
 */
object NetworkTestFactory {

    fun createNetworkQuality(
        score: Int = 4,
        latencyMs: Long = 50L,
        bandwidthKbps: Double = 1000.0,
        timestamp: Long = System.currentTimeMillis()
    ): NetworkQuality {
        return NetworkQuality(
            score = score,
            latencyMs = latencyMs,
            bandwidthKbps = bandwidthKbps,
            timestamp = timestamp
        )
    }

    fun createPoorNetworkQuality(): NetworkQuality {
        return createNetworkQuality(
            score = 1,
            latencyMs = 500L,
            bandwidthKbps = 100.0
        )
    }

    fun createExcellentNetworkQuality(): NetworkQuality {
        return createNetworkQuality(
            score = 5,
            latencyMs = 5L,
            bandwidthKbps = 2000.0
        )
    }
}

/**
 * Test data factory for recording statistics
 */
object RecordingTestFactory {

    fun createMockRecordingStatistics(
        sessionId: String = "test-session-${System.currentTimeMillis()}",
        duration: Long = 30000L,
        videoEnabled: Boolean = true,
        audioEnabled: Boolean = false,
        thermalEnabled: Boolean = true,
        framesRecorded: Int = 1800,
        dataSize: Long = 1024 * 1024 * 100, // 100MB
        averageFrameRate: Double = 60.0,
        droppedFrames: Int = 0
    ): Map<String, Any> {
        return mapOf(
            "sessionId" to sessionId,
            "duration" to duration,
            "videoEnabled" to videoEnabled,
            "audioEnabled" to audioEnabled,
            "thermalEnabled" to thermalEnabled,
            "framesRecorded" to framesRecorded,
            "dataSize" to dataSize,
            "averageFrameRate" to averageFrameRate,
            "droppedFrames" to droppedFrames,
            "timestamp" to System.currentTimeMillis()
        )
    }

    fun createLongMockRecordingStatistics(): Map<String, Any> {
        return createMockRecordingStatistics(
            duration = 300000L, // 5 minutes
            framesRecorded = 18000,
            dataSize = 1024 * 1024 * 1024, // 1GB
            averageFrameRate = 60.0
        )
    }

    fun createShortMockRecordingStatistics(): Map<String, Any> {
        return createMockRecordingStatistics(
            duration = 5000L, // 5 seconds
            framesRecorded = 300,
            dataSize = 1024 * 1024 * 10, // 10MB
            averageFrameRate = 60.0
        )
    }

    fun createProblematicMockRecordingStatistics(): Map<String, Any> {
        return createMockRecordingStatistics(
            duration = 30000L,
            framesRecorded = 1500, // Missing frames
            averageFrameRate = 50.0, // Lower than expected
            droppedFrames = 300
        )
    }
}