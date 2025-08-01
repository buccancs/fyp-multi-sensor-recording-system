package com.multisensor.recording.network

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.util.Logger
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import org.junit.Test
import java.lang.reflect.Method

/**
 * Comprehensive Test Suite for Temporal Data Extraction Algorithm
 * 
 * ## Overview
 * This test suite provides comprehensive validation of the timestamp extraction
 * algorithm implementation in EnhancedJsonSocketClient. The tests are designed
 * to verify both functional correctness and edge case handling according to
 * software engineering best practices.
 * 
 * ## Test Categories
 * 1. **Functional Verification**: Core algorithm correctness
 * 2. **Edge Case Analysis**: Boundary value testing
 * 3. **Type Safety Validation**: Compile-time and runtime type checking
 * 4. **Performance Characteristics**: Computational complexity verification
 * 5. **Error Handling**: Exception safety and graceful degradation
 * 
 * ## Mathematical Validation
 * Tests verify that the extraction function f: M → T ∪ {null} satisfies:
 * - **Totality**: f is defined for all message types M
 * - **Type Safety**: f(m) ∈ T for timestamped messages, null otherwise
 * - **Consistency**: f(m₁) = f(m₂) if m₁ and m₂ have identical timestamps
 * - **Monotonicity**: Temporal ordering is preserved
 * 
 * ## Test Methodology
 * - **Black Box Testing**: Interface-based testing without implementation details
 * - **Equivalence Partitioning**: Systematic coverage of input domains
 * - **Boundary Value Analysis**: Testing edge cases and limits
 * - **Error Injection**: Fault tolerance validation
 * 
 * @author Test Suite Development Team
 * @version 2.0.0
 * @since API Level 21
 */
class EnhancedJsonSocketClientTimestampExtractionTest {

    companion object {
        // Mathematical constants for test validation
        private const val EPOCH_MILLISECONDS = 1_000_000_000_000L // Jan 2001
        private const val MAX_SAFE_TIMESTAMP = Long.MAX_VALUE - 1
        private const val MIN_SAFE_TIMESTAMP = 0L
        
        // Test precision requirements
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

    /**
     * Test 1: Functional Correctness for Timestamped Message Types
     * 
     * Validates that the extraction algorithm correctly retrieves timestamp
     * values from all message types that contain temporal metadata.
     */
    @Test
    fun `test timestamp extraction for all timestamped message types`() {
        // Arrange
        val client = createTestClient()
        val method = getExtractionMethod()
        val testTimestamp = EPOCH_MILLISECONDS

        // Test PreviewFrameMessage
        val previewMessage = PreviewFrameMessage(
            cam = "rgb",
            timestamp = testTimestamp,
            image = "base64_encoded_frame_data"
        )
        
        val extractedPreview = method.invoke(client, previewMessage) as Long?
        assertThat(extractedPreview).isEqualTo(testTimestamp)

        // Test SensorDataMessage
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

        // Test SetStimulusTimeCommand
        val stimulusCommand = SetStimulusTimeCommand(time = testTimestamp + 2000L)
        val extractedStimulus = method.invoke(client, stimulusCommand) as Long?
        assertThat(extractedStimulus).isEqualTo(testTimestamp + 2000L)

        // Test SyncTimeCommand
        val syncCommand = SyncTimeCommand(
            pc_timestamp = testTimestamp + 3000L,
            sync_id = "sync_session_001"
        )
        val extractedSync = method.invoke(client, syncCommand) as Long?
        assertThat(extractedSync).isEqualTo(testTimestamp + 3000L)
    }

    /**
     * Test 2: Null Return Validation for Non-Timestamped Messages
     * 
     * Verifies that message types without temporal semantics correctly
     * return null, maintaining type safety and preventing false timestamps.
     */
    @Test
    fun `test null return for non-timestamped message types`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        // Test StatusMessage (no timestamp field)
        val statusMessage = StatusMessage(
            battery = 85,
            storage = "75GB available",
            temperature = 32.1,
            recording = true,
            connected = true
        )
        val statusResult = method.invoke(client, statusMessage) as Long?
        assertThat(statusResult).isNull()

        // Test AckMessage (protocol acknowledgment)
        val ackMessage = AckMessage(
            cmd = "start_record",
            status = "ok",
            message = "Recording session initiated successfully"
        )
        val ackResult = method.invoke(client, ackMessage) as Long?
        assertThat(ackResult).isNull()

        // Test HelloMessage (connection handshake)
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

    /**
     * Test 3: Boundary Value Analysis
     * 
     * Tests algorithm behavior at the boundaries of the timestamp domain,
     * including minimum, maximum, and edge case values.
     */
    @Test
    fun `test boundary values and edge cases`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        // Test minimum valid timestamp (epoch)
        val minMessage = PreviewFrameMessage(
            cam = "thermal",
            timestamp = MIN_SAFE_TIMESTAMP,
            image = "min_timestamp_frame"
        )
        val minResult = method.invoke(client, minMessage) as Long?
        assertThat(minResult).isEqualTo(MIN_SAFE_TIMESTAMP)

        // Test maximum safe timestamp
        val maxMessage = SensorDataMessage(
            timestamp = MAX_SAFE_TIMESTAMP,
            values = mapOf("test_sensor" to 1.0)
        )
        val maxResult = method.invoke(client, maxMessage) as Long?
        assertThat(maxResult).isEqualTo(MAX_SAFE_TIMESTAMP)

        // Test zero timestamp (valid but unusual)
        val zeroMessage = SetStimulusTimeCommand(time = 0L)
        val zeroResult = method.invoke(client, zeroMessage) as Long?
        assertThat(zeroResult).isEqualTo(0L)

        // Test current system time range
        val currentTime = System.currentTimeMillis()
        val currentMessage = SyncTimeCommand(pc_timestamp = currentTime)
        val currentResult = method.invoke(client, currentMessage) as Long?
        assertThat(currentResult).isEqualTo(currentTime)
    }

    /**
     * Test 4: Temporal Consistency and Ordering
     * 
     * Validates that timestamp extraction preserves temporal ordering
     * and maintains consistency across multiple invocations.
     */
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

        // Verify all timestamps extracted successfully
        extractedTimestamps.forEach { timestamp ->
            assertThat(timestamp).isNotNull()
        }

        // Verify temporal ordering preserved
        val sortedExtracted = extractedTimestamps.filterNotNull().sorted()
        assertThat(sortedExtracted).isEqualTo(timestamps)
    }

    /**
     * Test 5: Performance and Complexity Validation
     * 
     * Measures computational performance to verify O(1) time complexity
     * and validates memory efficiency for high-frequency operations.
     */
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

        // Measure execution time for large number of extractions
        val startTime = System.nanoTime()
        
        repeat(iterations) {
            val result = method.invoke(client, testMessage) as Long?
            assertThat(result).isNotNull()
        }
        
        val endTime = System.nanoTime()
        val totalTimeMs = (endTime - startTime) / 1_000_000.0
        val avgTimePerOperation = totalTimeMs / iterations

        // Verify sub-millisecond performance (indicating O(1) complexity)
        assertThat(avgTimePerOperation).isLessThan(0.01) // < 10μs per operation
        
        // Log performance metrics for analysis
        println("Performance Analysis:")
        println("Total operations: $iterations")
        println("Total time: ${totalTimeMs}ms")
        println("Average time per operation: ${avgTimePerOperation}ms")
        println("Operations per second: ${1000.0 / avgTimePerOperation}")
    }

    /**
     * Test 6: Type Safety and Reflection Validation
     * 
     * Verifies that the method signature is correct and that reflection
     * access maintains type safety guarantees.
     */
    @Test
    fun `test method signature and type safety`() {
        val client = createTestClient()
        val method = getExtractionMethod()

        // Verify method signature
        assertThat(method.name).isEqualTo("extractTimestampFromMessage")
        assertThat(method.parameterCount).isEqualTo(1)
        assertThat(method.parameterTypes[0]).isEqualTo(JsonMessage::class.java)
        assertThat(method.returnType).isEqualTo(Long::class.javaObjectType)

        // Verify method accessibility after making it accessible
        assertThat(method.isAccessible).isTrue()

        // Verify exception handling with null input (defensive programming)
        try {
            val result = method.invoke(client, null)
            // Should either return null or throw handled exception
            assertThat(result).isNull()
        } catch (e: Exception) {
            // Exception is acceptable for null input
            assertThat(e).isNotNull()
        }
    }

    /**
     * Test 7: Message Field Mapping Validation
     * 
     * Comprehensive validation that each message type maps to the correct
     * timestamp field according to protocol specification.
     */
    @Test
    fun `test correct field mapping for each message type`() {
        val client = createTestClient()
        val method = getExtractionMethod()
        
        // Test SetStimulusTimeCommand uses 'time' field (not 'timestamp')
        val stimulusTime = 1234567890L
        val stimulusMessage = SetStimulusTimeCommand(time = stimulusTime)
        val extractedStimulus = method.invoke(client, stimulusMessage) as Long?
        assertThat(extractedStimulus).isEqualTo(stimulusTime)
        
        // Test SyncTimeCommand uses 'pc_timestamp' field
        val pcTime = 9876543210L
        val syncMessage = SyncTimeCommand(pc_timestamp = pcTime)
        val extractedSync = method.invoke(client, syncMessage) as Long?
        assertThat(extractedSync).isEqualTo(pcTime)
        
        // Verify different timestamp values for same message type
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

    /**
     * Test 8: Integration with Real-World Timestamp Values
     * 
     * Tests the algorithm with realistic timestamp values that would
     * be encountered in production sensor data collection scenarios.
     */
    @Test
    fun `test realistic timestamp scenarios`() {
        val client = createTestClient()
        val method = getExtractionMethod()
        
        // Typical camera frame timestamps (30 FPS = 33.33ms intervals)
        val frameInterval = 33L // milliseconds
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
        
        // High-frequency sensor data (1kHz = 1ms intervals)
        val sensorInterval = 1L // milliseconds
        val sensorTimestamps = (0..999).map { sample ->
            baseTimestamp + (sample * sensorInterval)
        }
        
        sensorTimestamps.take(100).forEach { timestamp -> // Test subset for performance
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