package com.multisensor.recording.util

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import org.junit.Test

class SimpleArchitectureTest : BaseUnitTest() {

    @Test
    fun `should run basic test with modern architecture`() {
        val testValue = "Modern Test Architecture"

        val result = testValue.length

        assertThat(result).isEqualTo(23)
        assertThat(testValue).contains("Modern")
    }

    @Test
    fun `should work with Truth assertions`() {
        val numbers = listOf(1, 2, 3, 4, 5)

        assertThat(numbers).hasSize(5)
        assertThat(numbers).contains(3)
        assertThat(numbers).containsExactly(1, 2, 3, 4, 5).inOrder()
    }

    @Test
    fun `should demonstrate MockK integration via base class`() {

        assertThat(testDispatcher).isNotNull()
    }

    @Test
    fun `should handle coroutines testing`() {

        assertThat(testDispatcher.scheduler.currentTime).isEqualTo(0L)
    }

    @Test
    fun `should work with Kotlin collections`() {
        val map = mapOf("key1" to "value1", "key2" to "value2")

        assertThat(map).hasSize(2)
        assertThat(map).containsKey("key1")
        assertThat(map).containsEntry("key2", "value2")
    }
}