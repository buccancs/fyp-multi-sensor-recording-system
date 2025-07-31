package com.multisensor.recording.testsuite

import org.junit.runner.RunWith
import org.junit.runners.Suite

/**
 * Core Unit Test Suite
 * 
 * Groups all unit tests for core business logic components that don't require Android framework
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // Session management tests
    com.multisensor.recording.recording.session.SessionInfoTest::class,
    
    // UI state tests  
    com.multisensor.recording.ui.viewmodel.MainUiStateTest::class,
    
    // Network components tests
    com.multisensor.recording.network.NetworkQualityMonitorTest::class,
)
class CoreUnitTestSuite