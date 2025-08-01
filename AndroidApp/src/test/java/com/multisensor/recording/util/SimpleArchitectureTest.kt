package com.multisensor.recording.util

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import org.junit.Test

/**
 * Simple test to verify the modern test architecture works
 */
class SimpleArchitectureTest : BaseUnitTest() {

    @Test
    fun `should run basic test with modern architecture`() {
        // Given
        val testValue = "Modern Test Architecture"
        
        // When
        val result = testValue.length
        
        // Then
        assertThat(result).isEqualTo(23)
        assertThat(testValue).contains("Modern")
    }

    @Test
    fun `should work with Truth assertions`() {
        // Given
        val numbers = listOf(1, 2, 3, 4, 5)
        
        // When & Then
        assertThat(numbers).hasSize(5)
        assertThat(numbers).contains(3)
        assertThat(numbers).containsExactly(1, 2, 3, 4, 5).inOrder()
    }

    @Test
    fun `should demonstrate MockK integration via base class`() {
        // This test verifies that MockK setup in BaseUnitTest works
        // The Logger is mocked in the base class
        
        // When & Then - should not throw exceptions
        assertThat(testDispatcher).isNotNull()
    }

    @Test
    fun `should handle coroutines testing`() {
        // This test verifies that coroutine testing setup works
        
        // When & Then
        assertThat(testDispatcher.scheduler.currentTime).isEqualTo(0L)
    }

    @Test
    fun `should work with Kotlin collections`() {
        // Given
        val map = mapOf("key1" to "value1", "key2" to "value2")
        
        // When & Then
        assertThat(map).hasSize(2)
        assertThat(map).containsKey("key1")
        assertThat(map).containsEntry("key2", "value2")
    }
}