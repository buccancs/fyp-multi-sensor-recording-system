package com.multisensor.recording.testsuite

import org.junit.runner.RunWith
import org.junit.runners.Suite

/**
 * Complete test suite for all instrumented tests using modern test architecture
 * 
 * Organizes instrumented tests for efficient execution on emulators/devices
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // UI Integration Tests
    com.multisensor.recording.ui.MainActivityIntegrationTest::class,
    
    // Service Integration Tests
    com.multisensor.recording.service.RecordingServiceInstrumentedTest::class,
    
    // Hardware Integration Tests (would be added as needed)
    // com.multisensor.recording.hardware.ShimmerDeviceIntegrationTest::class,
    // com.multisensor.recording.hardware.ThermalCameraIntegrationTest::class,
    
    // Network Integration Tests
    // com.multisensor.recording.network.NetworkConnectionIntegrationTest::class,
    
    // Storage Integration Tests
    // com.multisensor.recording.storage.FileSystemIntegrationTest::class
)
class ComprehensiveInstrumentedTestSuite