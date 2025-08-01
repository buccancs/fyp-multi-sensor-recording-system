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