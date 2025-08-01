package com.multisensor.recording.testsuite

import org.junit.runner.RunWith
import org.junit.runners.Suite

/**
 * Enhanced comprehensive test suite for all instrumented tests with performance monitoring.
 * 
 * Organizes instrumented tests for efficient execution on emulators/devices with
 * comprehensive performance analysis and hardware validation.
 * 
 * @see EnhancedTestRunner for performance monitoring capabilities
 * @author Multi-Sensor Recording System
 * @version 2.0.0 - Enhanced with comprehensive testing framework
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // UI Integration Tests - Enhanced
    com.multisensor.recording.ui.MainActivityIntegrationTest::class,
    com.multisensor.recording.ui.FileViewActivityUITest::class,
    
    // Hardware Integration Tests - Production Ready
    com.multisensor.recording.recording.ThermalRecorderHardwareTest::class,
    com.multisensor.recording.recording.ComprehensiveCameraAccessTest::class,
    com.multisensor.recording.recording.BluetoothDiagnosticTest::class,
    com.multisensor.recording.recording.ShimmerRecorderDirectTest::class,
    
    // System Integration Tests - Comprehensive Validation
    com.multisensor.recording.integration.DataFlowIntegrationTest::class,
    com.multisensor.recording.integration.MultiSensorCoordinationTest::class,
    com.multisensor.recording.integration.ProtocolIntegrationTest::class,
    com.multisensor.recording.integration.FileIOIntegrationTest::class,
    com.multisensor.recording.integration.Milestone28IntegrationTest::class
)
class ComprehensiveInstrumentedTestSuite

/**
 * Hardware stress testing suite for device validation under extreme conditions.
 * 
 * These tests validate hardware integration and performance under stress:
 * - Thermal camera intensive operations
 * - Bluetooth connection reliability under load
 * - Multi-sensor coordination stress testing
 * - Extended recording session validation
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    com.multisensor.recording.recording.ThermalCameraBulletproofIntegrationTest::class,
    com.multisensor.recording.integration.MultiSensorCoordinationTest::class,
    com.multisensor.recording.integration.DataFlowIntegrationTest::class
)
class HardwareStressTestSuite

/**
 * UI performance testing suite for user experience validation.
 * 
 * These tests measure and validate UI performance metrics:
 * - Touch response latency
 * - UI rendering performance
 * - Memory usage during UI operations
 * - Battery consumption analysis
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    com.multisensor.recording.ui.MainActivityIntegrationTest::class,
    com.multisensor.recording.ui.FileViewActivityUITest::class
)
class UIPerformanceTestSuite

/**
 * Manual testing suite for scenarios requiring human interaction.
 * 
 * These tests require manual interaction and validation:
 * - Physical device testing scenarios
 * - Human-in-the-loop validation
 * - Real-world usage pattern testing
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    com.multisensor.recording.recording.CameraRecorderManualTest::class,
    com.multisensor.recording.recording.ShimmerRecorderManualTest::class
)
class ManualTestSuite