package com.multisensor.recording.testbase

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.multisensor.recording.util.Logger
import io.mockk.MockKAnnotations
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockkObject
import io.mockk.unmockkAll
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Before
import org.junit.Rule

/**
 * Base class for unit tests providing common setup and utilities
 * 
 * Features:
 * - MockK setup and cleanup
 * - Coroutine test dispatcher management
 * - Architecture components instant task execution
 * - Logger mocking for consistent test output
 */
@OptIn(ExperimentalCoroutinesApi::class)
abstract class BaseUnitTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    protected open val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()

    @Before
    open fun setUp() {
        MockKAnnotations.init(this)
        Dispatchers.setMain(testDispatcher)
        setupLogger()
    }

    @After
    open fun tearDown() {
        Dispatchers.resetMain()
        clearAllMocks()
        unmockkAll()
    }

    private fun setupLogger() {
        // Logger is injected via Hilt, no need to mock static methods
        // Individual tests should mock Logger instances as needed
    }
}