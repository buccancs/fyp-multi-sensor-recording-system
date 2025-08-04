package com.multisensor.recording.testsuite

import org.junit.runner.RunWith
import org.junit.runners.Suite

/**
 * Integration Test Suite
 * 
 * Groups all integration tests that require Android framework and device resources
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // UI integration tests
    com.multisensor.recording.ui.MainActivityIntegrationTest::class,
)
class IntegrationTestSuite