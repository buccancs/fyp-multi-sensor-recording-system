package com.multisensor.recording.network

import org.junit.Assert.*
import org.junit.Test

/**
 * Non-Android unit tests for NetworkProtocol
 * Tests message creation, parsing, validation, and data classes without requiring Android dependencies
 */
class NetworkProtocolBusinessLogicTest {

    @Test
    fun `createCommand should create properly formatted command`() {
        // When
        val command = NetworkProtocol.MessageFormat.createCommand("START_RECORDING")
        
        // Then
        assertNotNull("Command should not be null", command)
        assertTrue("Command should not be empty", command.isNotEmpty())
        assertTrue("Command should contain START_RECORDING", command.contains("START_RECORDING"))
    }

    @Test
    fun `createCommand should handle parameters correctly`() {
        // Given
        val parameters = mapOf(
            "session_id" to "test_123",
            "quality" to "high",
            "fps" to "30"
        )
        
        // When
        val command = NetworkProtocol.MessageFormat.createCommand("CONFIGURE", parameters)
        
        // Then
        assertNotNull("Command should not be null", command)
        assertTrue("Command should contain CONFIGURE", command.contains("CONFIGURE"))
        assertTrue("Command should contain session_id", command.contains("session_id"))
        assertTrue("Command should contain test_123", command.contains("test_123"))
        assertTrue("Command should contain quality", command.contains("quality"))
        assertTrue("Command should contain high", command.contains("high"))
    }

    @Test
    fun `createCommand should handle empty parameters`() {
        // When
        val command = NetworkProtocol.MessageFormat.createCommand("STOP_RECORDING", emptyMap())
        
        // Then
        assertNotNull("Command should not be null", command)
        assertTrue("Command should contain STOP_RECORDING", command.contains("STOP_RECORDING"))
    }

    @Test
    fun `createResponse should create properly formatted response`() {
        // When
        val response = NetworkProtocol.MessageFormat.createResponse("SUCCESS")
        
        // Then
        assertNotNull("Response should not be null", response)
        assertTrue("Response should not be empty", response.isNotEmpty())
        assertTrue("Response should contain SUCCESS", response.contains("SUCCESS"))
    }

    @Test
    fun `createResponse should handle data correctly`() {
        // Given
        val data = "Recording started successfully"
        
        // When
        val response = NetworkProtocol.MessageFormat.createResponse("SUCCESS", data)
        
        // Then
        assertNotNull("Response should not be null", response)
        assertTrue("Response should contain SUCCESS", response.contains("SUCCESS"))
        assertTrue("Response should contain data", response.contains(data))
    }

    @Test
    fun `createAck should create acknowledgment message`() {
        // When
        val ack = NetworkProtocol.MessageFormat.createAck("START_RECORDING")
        
        // Then
        assertNotNull("Ack should not be null", ack)
        assertTrue("Ack should not be empty", ack.isNotEmpty())
        assertTrue("Ack should contain START_RECORDING", ack.contains("START_RECORDING"))
    }

    @Test
    fun `createError should create error message`() {
        // When
        val error = NetworkProtocol.MessageFormat.createError("INVALID_COMMAND")
        
        // Then
        assertNotNull("Error should not be null", error)
        assertTrue("Error should not be empty", error.isNotEmpty())
        assertTrue("Error should contain INVALID_COMMAND", error.contains("INVALID_COMMAND"))
    }

    @Test
    fun `createError should handle details correctly`() {
        // Given
        val details = "Command not recognized by server"
        
        // When
        val error = NetworkProtocol.MessageFormat.createError("INVALID_COMMAND", details)
        
        // Then
        assertNotNull("Error should not be null", error)
        assertTrue("Error should contain error code", error.contains("INVALID_COMMAND"))
        assertTrue("Error should contain details", error.contains(details))
    }

    @Test
    fun `createStatus should create status message`() {
        // When
        val status = NetworkProtocol.MessageFormat.createStatus("RECORDING")
        
        // Then
        assertNotNull("Status should not be null", status)
        assertTrue("Status should not be empty", status.isNotEmpty())
        assertTrue("Status should contain RECORDING", status.contains("RECORDING"))
    }

    @Test
    fun `createStatus should handle details correctly`() {
        // Given
        val details = "Recording in progress, 120 frames captured"
        
        // When
        val status = NetworkProtocol.MessageFormat.createStatus("RECORDING", details)
        
        // Then
        assertNotNull("Status should not be null", status)
        assertTrue("Status should contain RECORDING", status.contains("RECORDING"))
        assertTrue("Status should contain details", status.contains(details))
    }

    @Test
    fun `parseCommand should parse valid command correctly`() {
        // Given
        val commandMessage = NetworkProtocol.MessageFormat.createCommand("START_RECORDING", mapOf("session_id" to "test_456"))
        
        // When
        val parsed = NetworkProtocol.MessageFormat.parseCommand(commandMessage)
        
        // Then
        assertNotNull("Parsed command should not be null", parsed)
        assertEquals("Command should be START_RECORDING", "START_RECORDING", parsed.command)
        assertTrue("Parameters should contain session_id", parsed.parameters.containsKey("session_id"))
        assertEquals("Session ID should match", "test_456", parsed.parameters["session_id"])
    }

    @Test
    fun `parseCommand should handle command without parameters`() {
        // Given
        val commandMessage = NetworkProtocol.MessageFormat.createCommand("STOP_RECORDING")
        
        // When
        val parsed = NetworkProtocol.MessageFormat.parseCommand(commandMessage)
        
        // Then
        assertNotNull("Parsed command should not be null", parsed)
        assertEquals("Command should be STOP_RECORDING", "STOP_RECORDING", parsed.command)
        assertTrue("Parameters should be empty", parsed.parameters.isEmpty())
    }

    @Test
    fun `parseResponse should parse valid response correctly`() {
        // Given
        val responseMessage = NetworkProtocol.MessageFormat.createResponse("SUCCESS", "Operation completed")
        
        // When
        val parsed = NetworkProtocol.MessageFormat.parseResponse(responseMessage)
        
        // Then
        assertNotNull("Parsed response should not be null", parsed)
        assertEquals("Response should be SUCCESS", "SUCCESS", parsed.response)
        assertEquals("Data should match", "Operation completed", parsed.data)
    }

    @Test
    fun `parseResponse should handle response without data`() {
        // Given
        val responseMessage = NetworkProtocol.MessageFormat.createResponse("ERROR")
        
        // When
        val parsed = NetworkProtocol.MessageFormat.parseResponse(responseMessage)
        
        // Then
        assertNotNull("Parsed response should not be null", parsed)
        assertEquals("Response should be ERROR", "ERROR", parsed.response)
        assertTrue("Data should be empty", parsed.data.isEmpty())
    }

    @Test
    fun `ParsedCommand should support data class functionality`() {
        // Given
        val params1 = mapOf("key1" to "value1", "key2" to "value2")
        val params2 = mapOf("key1" to "value1", "key2" to "value2")
        val params3 = mapOf("key1" to "different", "key2" to "value2")
        
        val command1 = NetworkProtocol.ParsedCommand("TEST", params1)
        val command2 = NetworkProtocol.ParsedCommand("TEST", params2)
        val command3 = NetworkProtocol.ParsedCommand("TEST", params3)
        
        // Then
        assertEquals("Equal commands should be equal", command1, command2)
        assertNotEquals("Different commands should not be equal", command1, command3)
        assertEquals("Hash codes should be equal for equal objects", command1.hashCode(), command2.hashCode())
    }

    @Test
    fun `ParsedCommand should have meaningful toString`() {
        // Given
        val params = mapOf("session_id" to "test_789", "quality" to "medium")
        val command = NetworkProtocol.ParsedCommand("CONFIGURE", params)
        
        // When
        val toString = command.toString()
        
        // Then
        assertTrue("Should contain command name", toString.contains("CONFIGURE"))
        assertTrue("Should contain parameters", toString.contains("session_id") || toString.contains("test_789"))
    }

    @Test
    fun `ParsedResponse should support data class functionality`() {
        // Given
        val response1 = NetworkProtocol.ParsedResponse("SUCCESS", "Data processed")
        val response2 = NetworkProtocol.ParsedResponse("SUCCESS", "Data processed")
        val response3 = NetworkProtocol.ParsedResponse("ERROR", "Data processed")
        
        // Then
        assertEquals("Equal responses should be equal", response1, response2)
        assertNotEquals("Different responses should not be equal", response1, response3)
        assertEquals("Hash codes should be equal for equal objects", response1.hashCode(), response2.hashCode())
    }

    @Test
    fun `ParsedResponse should have meaningful toString`() {
        // Given
        val response = NetworkProtocol.ParsedResponse("SUCCESS", "Recording completed successfully")
        
        // When
        val toString = response.toString()
        
        // Then
        assertTrue("Should contain response type", toString.contains("SUCCESS"))
        assertTrue("Should contain data", toString.contains("Recording completed") || toString.contains("successfully"))
    }

    @Test
    fun `isValidCommand should validate commands correctly`() {
        // Given
        val validCommands = listOf("START_RECORD", "STOP_RECORD", "CONFIGURE", "GET_STATUS")
        val invalidCommands = listOf("", "invalid", "123", "start recording")
        
        // When & Then
        validCommands.forEach { command ->
            assertTrue("$command should be valid", NetworkProtocol.Validation.isValidCommand(command))
        }
        
        invalidCommands.forEach { command ->
            assertFalse("$command should be invalid", NetworkProtocol.Validation.isValidCommand(command))
        }
    }

    @Test
    fun `isValidResponse should validate responses correctly`() {
        // Given
        val validResponses = listOf("ACK", "ERROR", "STATUS", "PONG")
        val invalidResponses = listOf("", "invalid", "123", "success")
        
        // When & Then
        validResponses.forEach { response ->
            assertTrue("$response should be valid", NetworkProtocol.Validation.isValidResponse(response))
        }
        
        invalidResponses.forEach { response ->
            assertFalse("$response should be invalid", NetworkProtocol.Validation.isValidResponse(response))
        }
    }

    @Test
    fun `isValidMessage should validate messages correctly`() {
        // Given
        val validMessages = listOf(
            NetworkProtocol.MessageFormat.createCommand("START_RECORD"),
            "invalid format", // Valid because it's not blank and under size limit
            "123"
        )
        val invalidMessages = listOf("", "   ", "\n", "\t") // Only blank messages are invalid
        
        // When & Then
        validMessages.forEach { message ->
            assertTrue("$message should be valid", NetworkProtocol.Validation.isValidMessage(message))
        }
        
        invalidMessages.forEach { message ->
            assertFalse("$message should be invalid", NetworkProtocol.Validation.isValidMessage(message))
        }
    }

    @Test
    fun `createHelloMessage should create proper hello message`() {
        // When
        val hello = NetworkProtocol.ClientInfo.createHelloMessage("device_123")
        
        // Then
        assertNotNull("Hello message should not be null", hello)
        assertTrue("Hello message should not be empty", hello.isNotEmpty())
        assertTrue("Hello message should contain device ID", hello.contains("device_123"))
    }

    @Test
    fun `createHelloMessage should handle default device ID`() {
        // When
        val hello = NetworkProtocol.ClientInfo.createHelloMessage()
        
        // Then
        assertNotNull("Hello message should not be null", hello)
        assertTrue("Hello message should not be empty", hello.isNotEmpty())
        assertTrue("Hello message should contain unknown", hello.contains("unknown"))
    }

    @Test
    fun `message creation should be consistent`() {
        // Given
        val command = "TEST_COMMAND"
        val parameters = mapOf("param1" to "value1")
        
        // When
        val message1 = NetworkProtocol.MessageFormat.createCommand(command, parameters)
        val message2 = NetworkProtocol.MessageFormat.createCommand(command, parameters)
        
        // Then
        assertEquals("Same command should produce same message", message1, message2)
    }

    @Test
    fun `parsing should be inverse of creation`() {
        // Given
        val originalCommand = "START_RECORD"
        val originalParams = mapOf("session_id" to "test_999", "quality" to "high")
        
        // When
        val message = NetworkProtocol.MessageFormat.createCommand(originalCommand, originalParams)
        val parsed = NetworkProtocol.MessageFormat.parseCommand(message)
        
        // Then
        assertEquals("Parsed command should match original", originalCommand, parsed.command)
        assertEquals("Parsed parameters should match original", originalParams, parsed.parameters)
    }

    @Test
    fun `response parsing should be inverse of creation`() {
        // Given
        val originalResponse = "SUCCESS"
        val originalData = "Operation completed successfully"
        
        // When
        val message = NetworkProtocol.MessageFormat.createResponse(originalResponse, originalData)
        val parsed = NetworkProtocol.MessageFormat.parseResponse(message)
        
        // Then
        assertEquals("Parsed response should match original", originalResponse, parsed.response)
        assertEquals("Parsed data should match original", originalData, parsed.data)
    }

    @Test
    fun `protocol should handle special characters`() {
        // Given
        val specialData = "Data with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        // When
        val response = NetworkProtocol.MessageFormat.createResponse("SUCCESS", specialData)
        val parsed = NetworkProtocol.MessageFormat.parseResponse(response)
        
        // Then
        assertEquals("Special characters should be preserved", specialData, parsed.data)
    }

    @Test
    fun `protocol should handle empty strings`() {
        // When
        val emptyCommand = NetworkProtocol.MessageFormat.createCommand("")
        val emptyResponse = NetworkProtocol.MessageFormat.createResponse("")
        val emptyAck = NetworkProtocol.MessageFormat.createAck("")
        
        // Then
        assertNotNull("Empty command should not be null", emptyCommand)
        assertNotNull("Empty response should not be null", emptyResponse)
        assertNotNull("Empty ack should not be null", emptyAck)
    }

    @Test
    fun `protocol should handle large data`() {
        // Given
        val largeData = "x".repeat(1000) // 1KB of data
        
        // When
        val response = NetworkProtocol.MessageFormat.createResponse("SUCCESS", largeData)
        val parsed = NetworkProtocol.MessageFormat.parseResponse(response)
        
        // Then
        assertEquals("Large data should be preserved", largeData, parsed.data)
        assertEquals("Large data length should match", 1000, parsed.data.length)
    }

    @Test
    fun `protocol constants should be accessible`() {
        // Then
        assertNotNull("Commands should be accessible", NetworkProtocol.Commands.START_RECORD)
        assertNotNull("Responses should be accessible", NetworkProtocol.Responses.ACK)
        assertNotNull("Status should be accessible", NetworkProtocol.Status.READY)
        assertNotNull("Error codes should be accessible", NetworkProtocol.ErrorCodes.UNKNOWN_COMMAND)
        assertNotNull("Config params should be accessible", NetworkProtocol.ConfigParams.SERVER_IP)
        assertNotNull("Defaults should be accessible", NetworkProtocol.Defaults.SERVER_IP)
        assertNotNull("Protocol version should be accessible", NetworkProtocol.PROTOCOL_VERSION)
    }

    @Test
    fun `default values should be reasonable`() {
        // Then
        assertTrue("Default server IP should be valid", NetworkProtocol.Defaults.SERVER_IP.isNotEmpty())
        assertTrue("Default port should be valid", NetworkProtocol.Defaults.SERVER_PORT > 0)
        assertTrue("Default FPS should be positive", NetworkProtocol.Defaults.PREVIEW_FPS > 0)
        assertTrue("Default quality should be valid", NetworkProtocol.Defaults.PREVIEW_QUALITY in 1..100)
        assertTrue("Default width should be positive", NetworkProtocol.Defaults.PREVIEW_WIDTH > 0)
        assertTrue("Default height should be positive", NetworkProtocol.Defaults.PREVIEW_HEIGHT > 0)
    }
}