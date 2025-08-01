# Android Test Suite Architecture

This document describes the comprehensive modern test architecture implemented for the Multi-Sensor Recording Android application.

## Test Architecture Overview

The test suite follows modern Android testing best practices with a clean, hierarchical structure that promotes maintainability and comprehensive coverage.

### Base Test Classes

#### BaseUnitTest
- **Purpose**: Foundation for pure unit tests without Android dependencies
- **Features**: MockK setup, coroutine test dispatcher, Logger mocking
- **Usage**: `class MyTest : BaseUnitTest()`

#### BaseRobolectricTest  
- **Purpose**: Android component tests requiring Android context
- **Features**: Robolectric environment, application context, MockK setup
- **Usage**: `class MyAndroidTest : BaseRobolectricTest()`

#### BaseInstrumentedTest
- **Purpose**: Instrumented tests with Hilt dependency injection
- **Features**: Hilt testing setup, Android instrumentation context
- **Usage**: `class MyInstrumentedTest : BaseInstrumentedTest()`

#### BaseUiIntegrationTest
- **Purpose**: UI integration tests with Espresso
- **Features**: UI testing utilities, view interactions, Hilt integration
- **Usage**: `class MyUITest : BaseUiIntegrationTest()`

#### BaseHardwareIntegrationTest
- **Purpose**: Hardware integration tests for devices and sensors
- **Features**: Hardware mocking, device simulation, sensor testing
- **Usage**: `class MyHardwareTest : BaseHardwareIntegrationTest()`

### Test Data Factories

#### SessionInfoTestFactory
Creates consistent `SessionInfo` test data:
```kotlin
val activeSession = SessionInfoTestFactory.createActiveSession()
val completedSession = SessionInfoTestFactory.createCompletedSession()
val errorSession = SessionInfoTestFactory.createErrorSession("Connection failed")
```

#### UiStateTestFactory
Creates UI state test scenarios:
```kotlin
val recordingState = UiStateTestFactory.createRecordingState()
val connectedState = UiStateTestFactory.createConnectedState()
val errorState = UiStateTestFactory.createErrorState("Network error")
```

#### RecordingTestFactory
Creates recording statistics and network quality data:
```kotlin
val stats = RecordingTestFactory.createRecordingStatistics()
val networkQuality = NetworkTestFactory.createExcellentNetworkQuality()
```

### Test Organization

```
src/test/java/com/multisensor/recording/
├── testbase/           # Base test classes
├── testfixtures/       # Test data factories
├── testsuite/          # Test suite definitions
├── recording/          # Recording component tests
│   ├── session/        # Session management tests
│   └── ...
├── ui/                 # UI component tests
│   ├── viewmodel/      # ViewModel tests
│   └── components/     # UI component tests
├── network/            # Network component tests
├── service/            # Service layer tests
├── util/               # Utility tests
└── ...
```

### Test Categories

#### Unit Tests (src/test)
- **Session Management**: SessionInfo business logic, duration calculations
- **UI State Management**: ViewModel tests, UI state validation  
- **Network Components**: Connection handling, data transfer, quality monitoring
- **Recording Logic**: Recording manager, device control, error handling
- **Utilities**: Logging, permissions, user feedback

#### Instrumented Tests (src/androidTest)  
- **UI Integration**: Activity tests, user interaction flows
- **Service Integration**: Background service testing, lifecycle management
- **Hardware Integration**: Device communication, sensor data collection
- **Storage Integration**: File operations, data persistence

### Test Suite Execution

#### Run All Unit Tests
```bash
./gradlew AndroidApp:test
```

#### Run Specific Test Suite
```bash  
./gradlew AndroidApp:testDevDebugUnitTest
```

#### Run Instrumented Tests
```bash
./gradlew AndroidApp:connectedDebugAndroidTest
```

#### Generate Coverage Reports
```bash
./gradlew AndroidApp:jacocoTestReport
```

### Modern Testing Frameworks

#### MockK
- Kotlin-native mocking framework
- Used consistently across all tests
- Provides comprehensive mocking capabilities

#### Google Truth
- Fluent assertion library
- Replaces traditional JUnit assertions
- More readable and maintainable assertions

#### Hilt Testing
- Dependency injection testing
- Proper component isolation
- Easy test double injection

#### Coroutines Testing  
- TestDispatcher for deterministic testing
- Proper async code testing
- Coroutine scope management

### Test Naming Conventions

Tests follow descriptive naming patterns:
```kotlin
@Test
fun `should calculate correct duration for completed session`()

@Test  
fun `should handle network error recovery gracefully`()

@Test
fun `should update UI state when device connects`()
```

### CI/CD Integration

The CI/CD pipeline automatically:
- Runs all unit tests for multiple Java versions
- Executes instrumented tests on multiple API levels
- Generates comprehensive test reports
- Uploads test artifacts and coverage data
- Validates test architecture compliance

### Migration from Legacy Tests

Legacy tests have been removed and replaced with modern equivalents:
- **Old**: Mixed frameworks, inconsistent patterns
- **New**: Standardized base classes, consistent data factories
- **Benefits**: Better maintainability, comprehensive coverage, modern tooling

### Best Practices

1. **Use appropriate base classes** for different test types
2. **Leverage test factories** for consistent test data
3. **Follow naming conventions** for test clarity
4. **Mock external dependencies** using MockK
5. **Use Truth assertions** for readable tests
6. **Organize tests by feature** in logical directories
7. **Write descriptive test names** that explain intent
8. **Test both happy path and error scenarios**

### Coverage Goals

- **Unit Tests**: >90% code coverage for business logic
- **Integration Tests**: Critical user flows and service operations  
- **UI Tests**: Key user interactions and state changes
- **Hardware Tests**: Device communication and error handling

This modern test architecture provides a solid foundation for reliable, maintainable testing that scales with project growth and ensures high-quality software delivery.

## Comprehensive Recording Session Testing Integration

The Android test architecture integrates seamlessly with the comprehensive recording session testing framework to provide end-to-end validation of PC-Android communication workflows. This integration ensures that the Android application components work correctly within the complete multi-sensor recording system.

### PC-Android Integration Testing

The recording session testing framework validates the complete PC-Android simulation workflow through coordinated testing scenarios:

#### Android Component Simulation
The test framework simulates Android application behavior with realistic sensor data generation and communication protocols:

• **Device Simulator Integration**: Creates enhanced device simulators that mimic real Android application behavior including sensor data collection, message processing, and state management
• **Sensor Data Generation**: Generates physiologically accurate sensor data (GSR, PPG, accelerometer, gyroscope, magnetometer) that matches real Shimmer3 device output characteristics
• **Communication Protocol Testing**: Validates JSON socket communication between simulated Android devices and the PC controller using production communication protocols
• **State Synchronization**: Tests device state management and synchronization across multiple simulated Android devices with proper handshake and acknowledgment procedures

#### Integration Test Categories

**Basic Integration Testing:**
```bash
# Test basic PC-Android communication workflow
python PythonApp/run_quick_recording_session_test.py
```

This validates fundamental Android app integration including device registration, command processing, sensor data transmission, and session management coordination.

**Advanced Integration Testing:**
```bash
# Comprehensive PC-Android workflow validation
python PythonApp/run_recording_session_test.py --devices 4 --duration 120

# Stress testing with multiple Android devices
python PythonApp/run_recording_session_test.py --stress-test --devices 8
```

Advanced integration testing validates complex scenarios including multi-device coordination, high-load communication, error recovery, and performance optimization.

**Error Condition Integration Testing:**
```bash
# Test Android app error handling and recovery
python PythonApp/run_recording_session_test.py --error-simulation --network-issues
```

Error condition testing validates Android application resilience by simulating network failures, device disconnections, communication timeouts, and recovery procedures.

### Android-Specific Test Validation

The recording session test framework includes Android-specific validation scenarios that complement the existing Android test architecture:

#### Communication Protocol Validation
• **JSON Message Protocol**: Tests complete JSON message exchange between Android devices and PC controller including message formatting, acknowledgment procedures, and error handling
• **Socket Connection Management**: Validates socket connection establishment, maintenance, reconnection logic, and graceful disconnection procedures
• **Command Processing**: Tests Android device response to PC commands including recording start/stop, configuration updates, and status requests
• **Data Streaming**: Validates real-time sensor data streaming from Android devices to PC controller with proper timestamp synchronization

#### Device Behavior Simulation
• **Realistic Sensor Patterns**: Simulates authentic sensor data patterns that match real Android device sensor characteristics and sampling rates
• **Battery and Performance Simulation**: Tests Android device behavior under various resource constraints including battery levels, memory usage, and processing limitations
• **UI State Simulation**: Validates Android UI state updates in response to PC commands and system events
• **Error State Handling**: Tests Android application behavior during error conditions including network failures, sensor disconnections, and system overload

#### Session Lifecycle Integration
• **Session Initialization**: Tests complete session startup procedures including device discovery, capability negotiation, and system preparation
• **Recording Coordination**: Validates synchronized recording start/stop across multiple Android devices with proper timing and coordination
• **Data Persistence**: Tests Android device data storage, file management, and data integrity during recording sessions
• **Session Termination**: Validates graceful session shutdown procedures including data finalization, file cleanup, and resource management

### Integration Testing Best Practices

#### Test Environment Setup
For optimal integration testing results, ensure proper test environment configuration:

```bash
# Set up test environment with proper logging
export PYTHONPATH="${PYTHONPATH}:$(pwd)/PythonApp/src"
export LOG_LEVEL="DEBUG"

# Configure test parameters for comprehensive validation
python PythonApp/run_recording_session_test.py \
    --duration 90 \
    --devices 3 \
    --save-logs \
    --health-check \
    --performance-bench
```

#### Continuous Integration Integration
The recording session tests integrate with CI/CD pipelines to provide automated validation:

```bash
# CI/CD friendly integration testing
python PythonApp/run_quick_recording_session_test.py --log-level INFO

# Generate integration test reports
python PythonApp/run_recording_session_test.py --save-logs --performance-bench --generate-report
```

#### Performance and Scalability Testing
Integration testing includes performance validation to ensure system scalability:

• **Multi-Device Scaling**: Tests system behavior with increasing numbers of Android devices to validate scalability limits
• **High-Frequency Data Testing**: Validates system performance with high-frequency sensor data streams that match production usage patterns
• **Resource Utilization Monitoring**: Tracks memory usage, CPU utilization, and network bandwidth during integration testing
• **Latency and Throughput Measurement**: Measures communication latency and data throughput between Android devices and PC controller

### Test Results and Analysis

#### Integration Test Reporting
The recording session testing framework provides comprehensive reporting that complements Android test results:

• **Communication Metrics**: Reports on message exchange rates, acknowledgment timing, and protocol compliance
• **Device Coordination**: Validates synchronization accuracy and timing precision across multiple Android devices
• **Data Integrity**: Confirms sensor data accuracy, completeness, and consistency throughout the recording session
• **Error Recovery**: Documents error condition handling and recovery success rates

#### Troubleshooting Integration Issues
When integration tests fail, use systematic troubleshooting approaches:

1. **Component Isolation**: Test Android components separately using existing Android test suite, then test PC components independently
2. **Communication Analysis**: Use verbose logging to analyze message exchange patterns and identify communication failures
3. **Timing Analysis**: Examine synchronization timing and identify coordination issues between PC and Android components
4. **Resource Analysis**: Monitor system resources to identify performance bottlenecks or resource constraints

#### Validation Criteria
Successful integration testing validates these critical requirements:

• **Functional Integration**: All PC-Android communication functions work correctly with proper command processing and data exchange
• **Performance Integration**: System maintains acceptable performance levels under realistic load conditions with multiple Android devices
• **Reliability Integration**: System demonstrates consistent behavior with proper error handling and recovery mechanisms
• **Scalability Integration**: System handles increasing device counts and data volumes within specified performance parameters

This comprehensive integration testing approach ensures that the Android application components work seamlessly within the complete multi-sensor recording system while maintaining the high standards of quality and reliability established by the modern Android test architecture.