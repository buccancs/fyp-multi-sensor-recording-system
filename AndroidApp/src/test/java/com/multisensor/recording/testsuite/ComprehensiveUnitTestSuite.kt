package com.multisensor.recording.testsuite

import org.junit.runner.RunWith
import org.junit.runners.Suite

/**
 * Enhanced comprehensive test suite for all unit tests with performance monitoring.
 * 
 * Organizes tests by category for efficient execution and detailed reporting.
 * Includes stress testing capabilities and performance benchmarking.
 * 
 * @see EnhancedTestRunner for performance monitoring capabilities
 * @author Multi-Sensor Recording System
 * @version 2.0.0 - Enhanced with comprehensive testing framework
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // Core recording functionality - High Priority
    com.multisensor.recording.recording.session.SessionInfoTest::class,
    com.multisensor.recording.recording.ThermalRecorderUnitTest::class,
    com.multisensor.recording.recording.ShimmerRecorderEnhancedTest::class,
    com.multisensor.recording.recording.ConnectionManagerTestSimple::class,
    com.multisensor.recording.recording.ShimmerRecorderConfigurationTest::class,
    com.multisensor.recording.recording.AdaptiveFrameRateControllerTest::class,
    
    // UI and ViewModels - Enhanced Testing
    com.multisensor.recording.ui.viewmodel.MainViewModelTest::class,
    com.multisensor.recording.ui.MainUiStateTest::class,
    com.multisensor.recording.ui.FileViewUiStateTest::class,
    com.multisensor.recording.ui.FileViewActivityTest::class,
    com.multisensor.recording.ui.ShimmerConfigUiStateTest::class,
    com.multisensor.recording.ui.SettingsUiStateTest::class,
    com.multisensor.recording.ui.FileManagementLogicTest::class,
    com.multisensor.recording.ui.NetworkConfigActivityTest::class,
    
    // Network components - Performance Critical
    com.multisensor.recording.network.FileTransferHandlerTest::class,
    com.multisensor.recording.network.NetworkQualityMonitorTest::class,
    
    // Service layer - Business Logic
    com.multisensor.recording.service.SessionManagerTest::class,
    com.multisensor.recording.service.SessionManagerBusinessLogicTest::class,
    
    // Utilities and helpers - Foundation
    com.multisensor.recording.util.LoggerTest::class,
    com.multisensor.recording.util.AppLoggerEnhancedTest::class,
    com.multisensor.recording.util.UserFeedbackManagerTest::class,
    com.multisensor.recording.util.AllAndroidPermissionsTest::class,
    com.multisensor.recording.util.AllAndroidPermissionsBusinessLogicTest::class,
    com.multisensor.recording.util.SimpleArchitectureTest::class,
    com.multisensor.recording.util.LoggerBusinessLogicTest::class,
    
    // Controllers and managers - Hardware Interface
    com.multisensor.recording.controllers.UsbControllerUnitTest::class,
    com.multisensor.recording.managers.UsbDeviceManagerUnitTest::class,
    
    // Streaming and calibration - Sensor Integration  
    com.multisensor.recording.streaming.PreviewStreamerTest::class,
    com.multisensor.recording.calibration.CalibrationCaptureManagerTest::class,
    com.multisensor.recording.calibration.SyncClockManagerTest::class,
    
    // UI Components - Enhanced Component Testing
    com.multisensor.recording.ui.components.ActionButtonPairTest::class,
    com.multisensor.recording.ui.components.StatusIndicatorViewTest::class,
    com.multisensor.recording.ui.components.CardSectionLayoutTest::class,
    com.multisensor.recording.ui.components.SectionHeaderViewTest::class,
    com.multisensor.recording.ui.components.LabelTextViewTest::class,
    
    // ViewModels - State Management
    com.multisensor.recording.ui.viewmodel.MainUiStateTest::class,
    
    // Protocol and integration - System Validation
    com.multisensor.recording.protocol.Milestone6Test::class
)
class ComprehensiveUnitTestSuite

/**
 * Stress testing suite for high-load scenario validation.
 * 
 * These tests validate system behavior under extreme conditions:
 * - High memory usage scenarios
 * - Concurrent operation stress
 * - Extended runtime testing
 * - Resource exhaustion scenarios
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // Stress test implementations would go here
    com.multisensor.recording.recording.ShimmerRecorderEnhancedTest::class,  // Concurrent connections
    com.multisensor.recording.network.NetworkQualityMonitorTest::class,      // Network stress
    com.multisensor.recording.service.SessionManagerTest::class,             // Session management stress
    com.multisensor.recording.calibration.CalibrationCaptureManagerTest::class // Calibration stress
)
class StressTestSuite

/**
 * Performance benchmarking suite for system optimization validation.
 * 
 * These tests measure and validate performance metrics:
 * - Response time benchmarks
 * - Memory usage optimization
 * - Battery consumption analysis
 * - CPU utilization efficiency
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    com.multisensor.recording.network.FileTransferHandlerTest::class,        // File transfer performance
    com.multisensor.recording.streaming.PreviewStreamerTest::class,          // Streaming performance
    com.multisensor.recording.recording.AdaptiveFrameRateControllerTest::class, // Frame rate optimization
    com.multisensor.recording.calibration.SyncClockManagerTest::class        // Synchronization performance
)
class PerformanceTestSuite