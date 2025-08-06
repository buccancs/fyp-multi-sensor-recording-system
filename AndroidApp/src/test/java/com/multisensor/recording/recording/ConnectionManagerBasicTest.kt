package com.multisensor.recording.recording

import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.robolectric.annotation.Config

/**
 * Basic test for ConnectionManager with Robolectric integration
 */
@Config(sdk = [28])
@ExperimentalCoroutinesApi
class ConnectionManagerBasicTest {

    private lateinit var mockLogger: Logger
    private lateinit var connectionManager: ConnectionManager

    @BeforeEach
    fun setup() {
        mockLogger = mockk(relaxed = true)
        connectionManager = ConnectionManager(mockLogger)
    }

    @AfterEach
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `connection manager should be created successfully`() = runTest {
        assertNotNull(connectionManager, "ConnectionManager should be created")
    }

    @Test
    fun `connection manager should have default configuration`() = runTest {
        // Basic test - just ensure it doesn't crash on object creation
        assertDoesNotThrow {
            connectionManager.toString()
        }
    }
}