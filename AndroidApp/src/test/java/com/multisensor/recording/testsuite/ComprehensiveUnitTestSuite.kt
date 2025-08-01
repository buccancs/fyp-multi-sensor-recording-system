package com.multisensor.recording.testsuite

import org.junit.runner.RunWith
import org.junit.runners.Suite

/**
 * Complete test suite for all unit tests using modern test architecture
 * 
 * Organizes tests by category for efficient execution and reporting
 */
@RunWith(Suite::class)
@Suite.SuiteClasses(
    // Core recording functionality
    com.multisensor.recording.recording.session.SessionInfoTest::class,
    com.multisensor.recording.recording.RecordingManagerTest::class,
    com.multisensor.recording.recording.ThermalRecorderUnitTest::class,
    com.multisensor.recording.recording.ShimmerRecorderEnhancedTest::class,
    com.multisensor.recording.recording.ConnectionManagerTest::class,
    
    // UI and ViewModels
    com.multisensor.recording.ui.viewmodel.MainViewModelTest::class,
    com.multisensor.recording.ui.MainUiStateTest::class,
    com.multisensor.recording.ui.FileViewUiStateTest::class,
    com.multisensor.recording.ui.FileViewActivityTest::class,
    com.multisensor.recording.ui.MainViewModelEnhancedTest::class,
    
    // Network components
    com.multisensor.recording.network.NetworkManagerTest::class,
    com.multisensor.recording.network.FileTransferHandlerTest::class,
    com.multisensor.recording.network.NetworkQualityMonitorTest::class,
    
    // Service layer
    com.multisensor.recording.service.SessionManagerTest::class,
    com.multisensor.recording.service.SessionManagerBusinessLogicTest::class,
    
    // Utilities and helpers
    com.multisensor.recording.util.LoggerTest::class,
    com.multisensor.recording.util.AppLoggerEnhancedTest::class,
    com.multisensor.recording.util.UserFeedbackManagerTest::class,
    com.multisensor.recording.util.AllAndroidPermissionsTest::class,
    
    // Controllers and managers
    com.multisensor.recording.controllers.UsbControllerUnitTest::class,
    com.multisensor.recording.managers.UsbDeviceManagerUnitTest::class,
    
    // Streaming and calibration
    com.multisensor.recording.streaming.PreviewStreamerTest::class,
    com.multisensor.recording.calibration.CalibrationCaptureManagerTest::class,
    com.multisensor.recording.calibration.SyncClockManagerTest::class,
    
    // UI Components
    com.multisensor.recording.ui.components.ActionButtonPairTest::class,
    com.multisensor.recording.ui.components.StatusIndicatorViewTest::class,
    com.multisensor.recording.ui.components.CardSectionLayoutTest::class,
    
    // Protocol and integration
    com.multisensor.recording.protocol.Milestone6Test::class
)
class ComprehensiveUnitTestSuite