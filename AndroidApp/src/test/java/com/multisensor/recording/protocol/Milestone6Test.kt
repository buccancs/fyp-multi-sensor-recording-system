package com.multisensor.recording.protocol

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.multisensor.recording.config.CommonConstants
import org.json.JSONObject
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Milestone 6 tests to verify shared constants and schema synchronization.
 *
 * These tests verify the key requirements from Milestone 6:
 * 1. Generated constants are accessible and correct
 * 2. Schema validation works for handshake messages
 * 3. Message creation and validation works correctly
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class Milestone6Test {
    private lateinit var context: Context
    private lateinit var schemaManager: SchemaManager
    private lateinit var handshakeManager: HandshakeManager

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        schemaManager = SchemaManager.getInstance(context)
        handshakeManager = HandshakeManager(context)
    }

    @Test
    fun testGeneratedConstantsAreAccessible() {
        // Test that generated constants are accessible and have expected values
        assert(CommonConstants.PROTOCOL_VERSION == 1)
        assert(CommonConstants.APP_VERSION == "1.0.0")

        // Test network constants
        assert(CommonConstants.Network.HOST == "192.168.0.100")
        assert(CommonConstants.Network.PORT == 9000)
        assert(CommonConstants.Network.TIMEOUT_SECONDS == 30)

        // Test device constants
        assert(CommonConstants.Devices.CAMERA_ID == 0)
        assert(CommonConstants.Devices.FRAME_RATE == 30)
        assert(CommonConstants.Devices.RESOLUTION_WIDTH == 1920)
        assert(CommonConstants.Devices.RESOLUTION_HEIGHT == 1080)

        // Test calibration constants
        assert(CommonConstants.Calibration.PATTERN_TYPE == "chessboard")
        assert(CommonConstants.Calibration.PATTERN_ROWS == 7)
        assert(CommonConstants.Calibration.PATTERN_COLS == 6)
        assert(CommonConstants.Calibration.SQUARE_SIZE_M == 0.0245)
    }

    @Test
    fun testHandshakeMessageCreation() {
        // Test that handshake messages can be created with correct structure
        val handshakeMessage =
            JSONObject().apply {
                put("type", "handshake")
                put("timestamp", System.currentTimeMillis())
                put("protocol_version", CommonConstants.PROTOCOL_VERSION)
                put("device_name", "Test Device")
                put("app_version", CommonConstants.APP_VERSION)
                put("device_type", "android")
            }

        // Verify the message has all required fields
        assert(handshakeMessage.has("type"))
        assert(handshakeMessage.has("timestamp"))
        assert(handshakeMessage.has("protocol_version"))
        assert(handshakeMessage.has("device_name"))
        assert(handshakeMessage.has("app_version"))
        assert(handshakeMessage.has("device_type"))

        // Verify field values
        assert(handshakeMessage.getString("type") == "handshake")
        assert(handshakeMessage.getInt("protocol_version") == CommonConstants.PROTOCOL_VERSION)
        assert(handshakeMessage.getString("app_version") == CommonConstants.APP_VERSION)
        assert(handshakeMessage.getString("device_type") == "android")
    }

    @Test
    fun testHandshakeAckMessageCreation() {
        // Test that handshake ack messages can be created
        val handshakeAck =
            handshakeManager.createHandshakeAck(
                clientProtocolVersion = 1,
                compatible = true,
                message = "Test compatibility",
            )

        // Verify the message has all required fields
        assert(handshakeAck.has("type"))
        assert(handshakeAck.has("timestamp"))
        assert(handshakeAck.has("protocol_version"))
        assert(handshakeAck.has("server_name"))
        assert(handshakeAck.has("server_version"))
        assert(handshakeAck.has("compatible"))

        // Verify field values
        assert(handshakeAck.getString("type") == "handshake_ack")
        assert(handshakeAck.getInt("protocol_version") == CommonConstants.PROTOCOL_VERSION)
        assert(handshakeAck.getString("server_version") == CommonConstants.APP_VERSION)
        assert(handshakeAck.getBoolean("compatible") == true)
    }

    @Test
    fun testVersionCompatibilityCheck() {
        // Test version compatibility logic
        assert(handshakeManager.areVersionsCompatible(1, 1) == true)
        assert(handshakeManager.areVersionsCompatible(1, 2) == false)
        assert(handshakeManager.areVersionsCompatible(2, 1) == false)
    }

    @Test
    fun testSchemaManagerMessageCreation() {
        // Test that schema manager can create basic messages
        val startRecordMessage = schemaManager.createMessage("start_record")
        assert(startRecordMessage.has("type"))
        assert(startRecordMessage.has("timestamp"))
        assert(startRecordMessage.getString("type") == "start_record")

        val deviceStatusMessage = schemaManager.createMessage("device_status")
        assert(deviceStatusMessage.has("type"))
        assert(deviceStatusMessage.has("timestamp"))
        assert(deviceStatusMessage.getString("type") == "device_status")

        val handshakeMessage = schemaManager.createMessage("handshake")
        assert(handshakeMessage.has("type"))
        assert(handshakeMessage.has("timestamp"))
        assert(handshakeMessage.getString("type") == "handshake")
    }

    @Test
    fun testBasicMessageValidation() {
        // Test basic message validation
        val validMessage =
            JSONObject().apply {
                put("type", "start_record")
                put("timestamp", System.currentTimeMillis())
                put("session_id", "test_session")
            }

        val invalidMessage =
            JSONObject().apply {
                put("type", "start_record")
                // Missing timestamp - should fail validation
            }

        // Valid message should pass
        assert(schemaManager.validateMessage(validMessage) == true)

        // Invalid message should fail
        assert(schemaManager.validateMessage(invalidMessage) == false)
    }

    @Test
    fun testHandshakeProcessing() {
        // Test handshake acknowledgment processing
        val compatibleAck =
            JSONObject().apply {
                put("type", "handshake_ack")
                put("timestamp", System.currentTimeMillis())
                put("protocol_version", CommonConstants.PROTOCOL_VERSION)
                put("server_name", "Test Server")
                put("server_version", "1.0.0")
                put("compatible", true)
            }

        val incompatibleAck =
            JSONObject().apply {
                put("type", "handshake_ack")
                put("timestamp", System.currentTimeMillis())
                put("protocol_version", 2) // Different version
                put("server_name", "Test Server")
                put("server_version", "2.0.0")
                put("compatible", false)
                put("message", "Version mismatch")
            }

        // Compatible ack should return true
        assert(handshakeManager.processHandshakeAck(compatibleAck) == true)

        // Incompatible ack should return false
        assert(handshakeManager.processHandshakeAck(incompatibleAck) == false)
    }
}
