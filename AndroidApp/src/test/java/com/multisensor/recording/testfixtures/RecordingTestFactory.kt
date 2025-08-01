package com.multisensor.recording.testfixtures

import com.multisensor.recording.network.NetworkQuality
import com.multisensor.recording.recording.RecordingStatistics

/**
 * Test data factory for network and recording related objects
 * Provides consistent test data creation with sensible defaults
 */
object NetworkTestFactory {

    fun createNetworkQuality(
        latency: Long = 50L,
        bandwidth: Double = 100.0,
        packetLoss: Double = 0.0,
        jitter: Long = 5L,
        connectionStable: Boolean = true
    ): NetworkQuality {
        return NetworkQuality(
            latency = latency,
            bandwidth = bandwidth,
            packetLoss = packetLoss,
            jitter = jitter,
            connectionStable = connectionStable,
            timestamp = System.currentTimeMillis()
        )
    }

    fun createPoorNetworkQuality(): NetworkQuality {
        return createNetworkQuality(
            latency = 500L,
            bandwidth = 10.0,
            packetLoss = 5.0,
            jitter = 100L,
            connectionStable = false
        )
    }

    fun createExcellentNetworkQuality(): NetworkQuality {
        return createNetworkQuality(
            latency = 5L,
            bandwidth = 1000.0,
            packetLoss = 0.0,
            jitter = 1L,
            connectionStable = true
        )
    }
}

/**
 * Test data factory for recording statistics
 */
object RecordingTestFactory {

    fun createRecordingStatistics(
        sessionId: String = "test-session-${System.currentTimeMillis()}",
        duration: Long = 30000L,
        videoEnabled: Boolean = true,
        audioEnabled: Boolean = false,
        thermalEnabled: Boolean = true,
        framesRecorded: Int = 1800,
        dataSize: Long = 1024 * 1024 * 100, // 100MB
        averageFrameRate: Double = 60.0,
        droppedFrames: Int = 0
    ): RecordingStatistics {
        return RecordingStatistics(
            sessionId = sessionId,
            duration = duration,
            videoEnabled = videoEnabled,
            audioEnabled = audioEnabled,
            thermalEnabled = thermalEnabled,
            framesRecorded = framesRecorded,
            dataSize = dataSize,
            averageFrameRate = averageFrameRate,
            droppedFrames = droppedFrames,
            timestamp = System.currentTimeMillis()
        )
    }

    fun createLongRecordingStatistics(): RecordingStatistics {
        return createRecordingStatistics(
            duration = 300000L, // 5 minutes
            framesRecorded = 18000,
            dataSize = 1024 * 1024 * 1024, // 1GB
            averageFrameRate = 60.0
        )
    }

    fun createShortRecordingStatistics(): RecordingStatistics {
        return createRecordingStatistics(
            duration = 5000L, // 5 seconds
            framesRecorded = 300,
            dataSize = 1024 * 1024 * 10, // 10MB
            averageFrameRate = 60.0
        )
    }

    fun createProblematicRecordingStatistics(): RecordingStatistics {
        return createRecordingStatistics(
            duration = 30000L,
            framesRecorded = 1500, // Missing frames
            averageFrameRate = 50.0, // Lower than expected
            droppedFrames = 300
        )
    }
}