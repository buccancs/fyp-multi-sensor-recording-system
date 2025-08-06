package com.multisensor.recording.network

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.util.Logger
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import org.junit.Test
import java.lang.reflect.Method

class EnhancedJsonSocketClientTimestampExtractionTest {

    companion object {
        private const val EPOCH_MILLISECONDS = 1_000_000_000_000L
        private const val MAX_SAFE_TIMESTAMP = Long.MAX_VALUE - 1
        private const val MIN_SAFE_TIMESTAMP = 0L

        private const val TEMPORAL_PRECISION_MS = 1L
    }

    private fun createTestClient(): EnhancedJsonSocketClient {
        val mockLogger = mockk<Logger>(relaxed = true)
        val mockNetworkConfig = mockk<NetworkConfiguration> {
            every { getServerIp() } returns "127.0.0.1"
            every { getJsonPort() } returns 8080
            every { setServerIp(any()) } just runs
            every { setJsonPort(any()) } just runs
        }
        return EnhancedJsonSocketClient(mockLogger, mockNetworkConfig)
    }

    private fun getExtractionMethod(): Method {
        return EnhancedJsonSocketClient::class.java.getDeclaredMethod(
            "extractTimestampFromMessage",
            JsonMessage::class.java
        ).apply { isAccessible = true }
    }

    @Test
    fun `test timestamp extraction for all timestamped message types`() {
        val client = createTestClient()
        val method = getExtractionMethod()
        val testTimestamp = EPOCH_MILLISECONDS

        val previewMessage = PreviewFrameMessage(
            cam = "rgb",
            timestamp = testTimestamp,
            image = "base64_encoded_frame_data"
        )

        val extractedPreview = method.invoke(client, previewMessage) as Long?
        assertThat(extractedPreview).isEqualTo(testTimestamp)

        val sensorMessage = SensorDataMessage(
            timestamp = testTimestamp + 1000L,
            values = mapOf(
                "accelerometer_x" to 9.81,
                "accelerometer_y" to 0.12,
                "accelerometer_z" to -0.05,
                "temperature" to 23.5
            )
        )

        val extractedSensor = method.invoke(client, sensorMessage) as Long?
        assertThat(extractedSensor).isEqualTo(testTimestamp + 1000L)

        val stimulusCommand = SetStimulusTimeCommand(time = testTimestamp + 2000L)
        val extractedStimulus = method.invoke(client, stimulusCommand) as Long?
        assertThat(extractedStimulus).isEqualTo(testTimestamp + 2000L)

        val syncCommand = SyncTimeCommand(
            pc_timestamp = testTimestamp + 3000L,
            sync_id = "sync_session_001"
        )
        val extractedSync = method.invoke(client, syncCommand) as Long?
        assertThat(extractedSync).isEqualTo(testTimestamp + 3000L)
    }

    @Test
    fun `test null return for non-timestamped message types`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        val statusMessage = StatusMessage(
            battery = 85,
            storage = "75GB available",
            temperature = 32.1,
            recording = true,
            connected = true
        )
        val statusResult = method.invoke(client, statusMessage) as Long?
        assertThat(statusResult).isNull()

        val ackMessage = AckMessage(
            cmd = "start_record",
            status = "ok",
            message = "Recording session initiated successfully"
        )
        val ackResult = method.invoke(client, ackMessage) as Long?
        assertThat(ackResult).isNull()

        val helloMessage = HelloMessage(
            device_id = "samsung_galaxy_s21_001",
            capabilities = listOf(
                "rgb_camera", "thermal_camera", "accelerometer",
                "gyroscope", "magnetometer", "gps"
            )
        )
        val helloResult = method.invoke(client, helloMessage) as Long?
        assertThat(helloResult).isNull()
    }

    @Test
    fun `test boundary values and edge cases`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        val minMessage = PreviewFrameMessage(
            cam = "thermal",
            timestamp = MIN_SAFE_TIMESTAMP,
            image = "min_timestamp_frame"
        )
        val minResult = method.invoke(client, minMessage) as Long?
        assertThat(minResult).isEqualTo(MIN_SAFE_TIMESTAMP)

        val maxMessage = SensorDataMessage(
            timestamp = MAX_SAFE_TIMESTAMP,
            values = mapOf("test_sensor" to 1.0)
        )
        val maxResult = method.invoke(client, maxMessage) as Long?
        assertThat(maxResult).isEqualTo(MAX_SAFE_TIMESTAMP)

        val zeroMessage = SetStimulusTimeCommand(time = 0L)
        val zeroResult = method.invoke(client, zeroMessage) as Long?
        assertThat(zeroResult).isEqualTo(0L)

        val currentTime = System.currentTimeMillis()
        val currentMessage = SyncTimeCommand(pc_timestamp = currentTime)
        val currentResult = method.invoke(client, currentMessage) as Long?
        assertThat(currentResult).isEqualTo(currentTime)
    }

    @Test
    fun `test temporal consistency and ordering preservation`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        val baseTime = System.currentTimeMillis()
        val timestamps = listOf(
            baseTime,
            baseTime + 100L,
            baseTime + 250L,
            baseTime + 500L,
            baseTime + 1000L
        )

        val extractedTimestamps = timestamps.mapIndexed { index, timestamp ->
            val message = when (index % 4) {
                0 -> PreviewFrameMessage(cam = "rgb", timestamp = timestamp, image = "frame_$index")
                1 -> SensorDataMessage(timestamp = timestamp, values = mapOf("sensor" to index.toDouble()))
                2 -> SetStimulusTimeCommand(time = timestamp)
                3 -> SyncTimeCommand(pc_timestamp = timestamp)
                else -> PreviewFrameMessage(cam = "thermal", timestamp = timestamp, image = "frame_$index")
            }
            method.invoke(client, message) as Long?
        }

        extractedTimestamps.forEach { timestamp ->
            assertThat(timestamp).isNotNull()
        }

        val sortedExtracted = extractedTimestamps.filterNotNull().sorted()
        assertThat(sortedExtracted).isEqualTo(timestamps)
    }

    @Test
    fun `test performance characteristics and complexity`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        val iterations = 10_000
        val testMessage = PreviewFrameMessage(
            cam = "rgb",
            timestamp = System.currentTimeMillis(),
            image = "performance_test_frame"
        )

        val startTime = System.nanoTime()

        repeat(iterations) {
            val result = method.invoke(client, testMessage) as Long?
            assertThat(result).isNotNull()
        }

        val endTime = System.nanoTime()
        val totalTimeMs = (endTime - startTime) / 1_000_000.0
        val avgTimePerOperation = totalTimeMs / iterations

        assertThat(avgTimePerOperation).isLessThan(0.01)

        println("Performance Analysis:")
        println("Total operations: $iterations")
        println("Total time: ${totalTimeMs}ms")
        println("Average time per operation: ${avgTimePerOperation}ms")
        println("Operations per second: ${1000.0 / avgTimePerOperation}")
    }

    @Test
    fun `test method signature and type safety`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        assertThat(method.name).isEqualTo("extractTimestampFromMessage")
        assertThat(method.parameterCount).isEqualTo(1)
        assertThat(method.parameterTypes[0]).isEqualTo(JsonMessage::class.java)
        assertThat(method.returnType).isEqualTo(Long::class.javaObjectType)

        assertThat(method.isAccessible).isTrue()

        try {
            val result = method.invoke(client, null)
            assertThat(result).isNull()
        } catch (e: Exception) {
            assertThat(e).isNotNull()
        }
    }

    @Test
    fun `test correct field mapping for each message type`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        val stimulusTime = 1234567890L
        val stimulusMessage = SetStimulusTimeCommand(time = stimulusTime)
        val extractedStimulus = method.invoke(client, stimulusMessage) as Long?
        assertThat(extractedStimulus).isEqualTo(stimulusTime)

        val pcTime = 9876543210L
        val syncMessage = SyncTimeCommand(pc_timestamp = pcTime)
        val extractedSync = method.invoke(client, syncMessage) as Long?
        assertThat(extractedSync).isEqualTo(pcTime)

        val time1 = System.currentTimeMillis()
        val time2 = time1 + 5000L

        val frame1 = PreviewFrameMessage(cam = "rgb", timestamp = time1, image = "frame1")
        val frame2 = PreviewFrameMessage(cam = "rgb", timestamp = time2, image = "frame2")

        val extracted1 = method.invoke(client, frame1) as Long?
        val extracted2 = method.invoke(client, frame2) as Long?

        assertThat(extracted1).isEqualTo(time1)
        assertThat(extracted2).isEqualTo(time2)
        assertThat(extracted2!! - extracted1!!).isEqualTo(5000L)
    }

    @Test
    fun `test realistic timestamp scenarios`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        val frameInterval = 33L
        val baseTimestamp = System.currentTimeMillis()

        val frameTimestamps = (0..29).map { frame ->
            baseTimestamp + (frame * frameInterval)
        }

        frameTimestamps.forEach { timestamp ->
            val frameMessage = PreviewFrameMessage(
                cam = "rgb",
                timestamp = timestamp,
                image = "frame_data_${timestamp}"
            )

            val extracted = method.invoke(client, frameMessage) as Long?
            assertThat(extracted).isEqualTo(timestamp)
        }

        val sensorInterval = 1L
        val sensorTimestamps = (0..999).map { sample ->
            baseTimestamp + (sample * sensorInterval)
        }

        sensorTimestamps.take(100).forEach { timestamp ->
            val sensorMessage = SensorDataMessage(
                timestamp = timestamp,
                values = mapOf(
                    "accelerometer_x" to (Math.random() * 20 - 10),
                    "accelerometer_y" to (Math.random() * 20 - 10),
                    "accelerometer_z" to (Math.random() * 20 - 10)
                )
            )

            val extracted = method.invoke(client, sensorMessage) as Long?
            assertThat(extracted).isEqualTo(timestamp)
        }
    }
}
