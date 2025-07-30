package com.multisensor.recording.integration

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.multisensor.recording.protocol.ConfigManager
import com.multisensor.recording.protocol.SchemaManager
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.net.Socket
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread

/**
 * Android Instrumentation Tests for Protocol Communication.
 *
 * This test class implements the Android instrumentation test hooks described
 * in Milestone 4 for exercising communication logic and state management.
 * It simulates the PC-server side within the Android test environment.
 */
@RunWith(AndroidJUnit4::class)
class ProtocolIntegrationTest {
    private lateinit var schemaManager: SchemaManager
    private lateinit var configManager: ConfigManager
    private lateinit var mockConnectionManager: MockConnectionManager

    @Before
    fun setUp() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        schemaManager = SchemaManager.getInstance(context)
        configManager = ConfigManager.getInstance(context)
        mockConnectionManager = MockConnectionManager()
    }

    @Test
    fun testSchemaManagerLoading() {
        // Test that schema manager loads successfully
        assertTrue("Schema should be loaded", schemaManager.isSchemaLoaded)

        // Test that valid message types are available
        val validTypes = schemaManager.validMessageTypes
        assertTrue("Should have valid message types", validTypes.isNotEmpty())

        // Check for expected message types
        val expectedTypes =
            setOf(
                "start_record",
                "stop_record",
                "preview_frame",
                "file_chunk",
                "device_status",
                "ack",
                "calibration_start",
                "calibration_result",
            )

        for (expectedType in expectedTypes) {
            assertTrue("Should contain $expectedType", validTypes.contains(expectedType))
        }
    }

    @Test
    fun testConfigManagerLoading() {
        // Test that config manager loads successfully
        assertTrue("Config should be loaded", configManager.isConfigLoaded)

        // Test basic configuration access
        val host = configManager.host
        val port = configManager.port

        assertNotNull("Host should not be null", host)
        assertTrue("Port should be positive", port > 0)
        assertTrue("Port should be valid", port <= 65535)
    }

    @Test
    fun testMessageValidation() {
        // Test valid message validation
        val validStartMessage =
            JSONObject().apply {
                put("type", "start_record")
                put("timestamp", System.currentTimeMillis())
                put("session_id", "test_session_123")
            }

        assertTrue(
            "Valid start message should pass validation",
            schemaManager.validateMessage(validStartMessage),
        )

        // Test invalid message rejection
        val invalidMessage =
            JSONObject().apply {
                put("type", "start_record")
                put("timestamp", System.currentTimeMillis())
                // Missing required session_id
            }

        assertFalse(
            "Invalid message should fail validation",
            schemaManager.validateMessage(invalidMessage),
        )
    }

    @Test
    fun testMessageCreation() {
        // Test creating different message types
        val startMessage = schemaManager.createMessage("start_record")
        assertEquals("start_record", startMessage.getString("type"))
        assertTrue("Should have timestamp", startMessage.has("timestamp"))
        assertTrue("Should have session_id field", startMessage.has("session_id"))

        val previewMessage = schemaManager.createMessage("preview_frame")
        assertEquals("preview_frame", previewMessage.getString("type"))
        assertTrue("Should have frame_id", previewMessage.has("frame_id"))
        assertTrue("Should have image_data", previewMessage.has("image_data"))
        assertTrue("Should have width", previewMessage.has("width"))
        assertTrue("Should have height", previewMessage.has("height"))
    }

    @Test
    fun testMockSocketConnection() {
        val latch = CountDownLatch(1)
        var receivedMessage: JSONObject? = null

        // Set up mock connection to receive messages
        mockConnectionManager.onMessageReceived = { message ->
            receivedMessage = message
            latch.countDown()
        }

        // Simulate sending a message
        val testMessage =
            schemaManager.createMessage("device_status").apply {
                put("device_id", "test_device")
                put("status", "idle")
                put("battery_level", 85)
                put("storage_available", 1024)
            }

        mockConnectionManager.sendMessage(testMessage)

        // Wait for message to be processed
        assertTrue(
            "Should receive message within timeout",
            latch.await(5, TimeUnit.SECONDS),
        )

        assertNotNull("Should have received a message", receivedMessage)
        assertEquals("device_status", receivedMessage?.getString("type"))
        assertEquals("test_device", receivedMessage?.getString("device_id"))
    }

    @Test
    fun testRecordingStateTransitions() {
        val stateManager = MockRecordingStateManager()

        // Test initial state
        assertEquals(RecordingState.IDLE, stateManager.currentState)

        // Test start recording transition
        val startMessage =
            schemaManager.createMessage("start_record").apply {
                put("session_id", "test_session")
            }

        stateManager.handleMessage(startMessage)
        assertEquals(RecordingState.RECORDING, stateManager.currentState)

        // Test stop recording transition
        val stopMessage =
            schemaManager.createMessage("stop_record").apply {
                put("session_id", "test_session")
            }

        stateManager.handleMessage(stopMessage)
        assertEquals(RecordingState.IDLE, stateManager.currentState)
    }

    @Test
    fun testMessageGenerationDuringRecording() {
        val messageCollector = mutableListOf<JSONObject>()
        val stateManager = MockRecordingStateManager()

        // Set up message collection
        stateManager.onMessageGenerated = { message ->
            messageCollector.add(message)
        }

        // Start recording
        val startMessage =
            schemaManager.createMessage("start_record").apply {
                put("session_id", "test_session")
            }
        stateManager.handleMessage(startMessage)

        // Simulate some time for message generation
        Thread.sleep(1000)

        // Stop recording
        val stopMessage =
            schemaManager.createMessage("stop_record").apply {
                put("session_id", "test_session")
            }
        stateManager.handleMessage(stopMessage)

        // Verify messages were generated
        assertTrue("Should have generated messages", messageCollector.isNotEmpty())

        // Check for expected message types
        val messageTypes = messageCollector.map { it.getString("type") }.toSet()
        assertTrue("Should generate preview frames", messageTypes.contains("preview_frame"))
        assertTrue("Should generate device status", messageTypes.contains("device_status"))
    }

    @Test
    fun testCalibrationFlow() {
        val stateManager = MockRecordingStateManager()
        val messageCollector = mutableListOf<JSONObject>()

        stateManager.onMessageGenerated = { message ->
            messageCollector.add(message)
        }

        // Start calibration
        val calibrationStart =
            schemaManager.createMessage("calibration_start").apply {
                put("pattern_type", "chessboard")
                put(
                    "pattern_size",
                    JSONObject().apply {
                        put("rows", 7)
                        put("cols", 6)
                    },
                )
            }

        stateManager.handleMessage(calibrationStart)

        // Wait for calibration to complete
        Thread.sleep(2000)

        // Check for calibration result
        val calibrationResults =
            messageCollector.filter {
                it.getString("type") == "calibration_result"
            }

        assertTrue("Should generate calibration result", calibrationResults.isNotEmpty())

        val result = calibrationResults.first()
        assertTrue("Should have success field", result.has("success"))
    }

    @Test
    fun testErrorHandling() {
        val stateManager = MockRecordingStateManager()

        // Test handling stop without start
        val stopMessage =
            schemaManager.createMessage("stop_record").apply {
                put("session_id", "nonexistent_session")
            }

        // Should handle gracefully without crashing
        stateManager.handleMessage(stopMessage)
        assertEquals(RecordingState.IDLE, stateManager.currentState)

        // Test handling invalid message
        val invalidMessage =
            JSONObject().apply {
                put("type", "unknown_type")
                put("timestamp", System.currentTimeMillis())
            }

        // Should handle gracefully
        stateManager.handleMessage(invalidMessage)
        assertEquals(RecordingState.IDLE, stateManager.currentState)
    }

    @Test
    fun testConfigSchemaConsistency() {
        // Test that calibration config matches schema expectations
        val calibrationConfig = configManager.calibrationConfig

        val patternRows = calibrationConfig.optInt("pattern_rows", 7)
        val patternCols = calibrationConfig.optInt("pattern_cols", 6)

        // Create calibration message using config values
        val calibrationMessage =
            schemaManager.createMessage("calibration_start").apply {
                put("pattern_type", calibrationConfig.optString("pattern_type", "chessboard"))
                put(
                    "pattern_size",
                    JSONObject().apply {
                        put("rows", patternRows)
                        put("cols", patternCols)
                    },
                )
            }

        // Message should validate against schema
        assertTrue(
            "Config-based message should validate",
            schemaManager.validateMessage(calibrationMessage),
        )
    }
}

/**
 * Mock connection manager for testing network communication without real sockets.
 */
class MockConnectionManager {
    var onMessageReceived: ((JSONObject) -> Unit)? = null
    private val messageQueue = mutableListOf<JSONObject>()

    fun sendMessage(message: JSONObject) {
        // Simulate message transmission
        thread {
            Thread.sleep(10) // Simulate network delay
            onMessageReceived?.invoke(message)
        }
    }

    fun getReceivedMessages(): List<JSONObject> = messageQueue.toList()
}

/**
 * Mock recording state manager for testing state transitions.
 */
enum class RecordingState {
    IDLE,
    RECORDING,
    CALIBRATING,
    ERROR,
}

class MockRecordingStateManager {
    var currentState = RecordingState.IDLE
    var onMessageGenerated: ((JSONObject) -> Unit)? = null
    private var currentSessionId: String? = null

    fun handleMessage(message: JSONObject) {
        val messageType = message.optString("type")

        when (messageType) {
            "start_record" -> {
                if (currentState == RecordingState.IDLE) {
                    currentSessionId = message.optString("session_id")
                    currentState = RecordingState.RECORDING
                    startGeneratingMessages()
                }
            }

            "stop_record" -> {
                if (currentState == RecordingState.RECORDING) {
                    currentState = RecordingState.IDLE
                    currentSessionId = null
                }
            }

            "calibration_start" -> {
                currentState = RecordingState.CALIBRATING
                startCalibrationProcess()
            }
        }
    }

    private fun startGeneratingMessages() {
        thread {
            var frameId = 0
            while (currentState == RecordingState.RECORDING) {
                // Generate preview frame
                val previewFrame =
                    JSONObject().apply {
                        put("type", "preview_frame")
                        put("timestamp", System.currentTimeMillis())
                        put("frame_id", frameId++)
                        put("image_data", "fake_image_data_$frameId")
                        put("width", 640)
                        put("height", 480)
                    }
                onMessageGenerated?.invoke(previewFrame)

                // Generate device status
                val deviceStatus =
                    JSONObject().apply {
                        put("type", "device_status")
                        put("timestamp", System.currentTimeMillis())
                        put("device_id", "test_device")
                        put("status", "recording")
                        put("battery_level", 85)
                        put("storage_available", 1024)
                    }
                onMessageGenerated?.invoke(deviceStatus)

                Thread.sleep(100) // 10 FPS simulation
            }
        }
    }

    private fun startCalibrationProcess() {
        thread {
            Thread.sleep(1500) // Simulate calibration time

            val calibrationResult =
                JSONObject().apply {
                    put("type", "calibration_result")
                    put("timestamp", System.currentTimeMillis())
                    put("success", true)
                    put("rms_error", 0.8)
                }
            onMessageGenerated?.invoke(calibrationResult)

            currentState = RecordingState.IDLE
        }
    }
}
