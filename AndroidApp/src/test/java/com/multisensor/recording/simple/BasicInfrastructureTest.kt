package com.multisensor.recording.simple

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

/**
 * Basic infrastructure test to ensure JUnit 5 is working
 */
class BasicInfrastructureTest {

    @Test
    fun `test framework should be working`() {
        assertTrue(true, "JUnit 5 framework should be operational")
    }

    @Test
    fun `basic assertions should work`() {
        assertEquals(2, 1 + 1, "Basic arithmetic should work")
        assertNotNull("test", "String should not be null")
    }

    @Test
    fun `kotlin coroutines should be available`() {
        // Test that coroutines dependency is available
        val result = kotlinx.coroutines.runBlocking {
            "coroutines working"
        }
        assertEquals("coroutines working", result)
    }
}