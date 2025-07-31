# Android Test Suite Architecture

This document describes the refactored Android test suite architecture for the Multi-Sensor Recording System.

## Overview

The test suite has been completely refactored to provide:
- **Consistent testing patterns** across all components
- **Modern testing frameworks** (MockK, Truth, Hilt Testing)
- **Organized test structure** by feature modules
- **Reusable test utilities** and data factories
- **Clear separation** between unit, integration, and UI tests

## Architecture

### Base Test Classes

Located in `com.multisensor.recording.testbase`:

#### `BaseUnitTest`
- Foundation for pure unit tests
- MockK setup and cleanup
- Coroutine test dispatcher management  
- Architecture components instant task execution
- Logger mocking for consistent test output

#### `BaseRobolectricTest`
- Extends `BaseUnitTest` for Android component testing
- Robolectric Android environment
- Application context access
- Use for tests requiring Android APIs without device

#### `BaseInstrumentedTest` 
- Foundation for instrumented tests
- Hilt dependency injection setup
- Android instrumentation context
- Use for tests requiring real device/emulator

#### `BaseUiIntegrationTest`
- Extends `BaseInstrumentedTest` for UI testing
- Activity scenario management
- Essential permission grants
- Common UI testing utilities

#### `BaseHardwareIntegrationTest`
- Extends `BaseInstrumentedTest` for hardware testing
- Hardware-specific permissions
- Timeout configurations for hardware operations
- Hardware availability checking

### Test Data Factories

Located in `com.multisensor.recording.testfixtures`:

#### `SessionInfoTestFactory`
- Creates consistent `SessionInfo` test data
- Predefined scenarios (active, completed, error sessions)
- Sensible defaults with customization options

#### `UiStateTestFactory`
- Creates consistent UI state test data
- Predefined UI scenarios (recording, connected, error states)
- Comprehensive state combinations

### Test Organization

Tests are organized by feature modules:

```
src/test/java/com/multisensor/recording/
├── testbase/          # Base test classes
├── testfixtures/      # Test data factories
├── testsuite/         # Test suite definitions
├── recording/
│   └── session/       # Session management tests
├── ui/
│   └── viewmodel/     # UI state and ViewModel tests
├── network/           # Network component tests
├── managers/          # Manager class tests
├── calibration/       # Calibration tests
└── legacy/            # Legacy tests (to be migrated)
```

```
src/androidTest/java/com/multisensor/recording/
├── testbase/          # Integration test base classes
├── testsuite/         # Integration test suites
├── ui/                # UI integration tests
├── recording/         # Recording integration tests
└── legacy/            # Legacy integration tests
```

## Test Categories

### Unit Tests (`src/test/`)
- **Pure unit tests**: No Android dependencies
- **Robolectric tests**: Require Android APIs but run on JVM
- Fast execution, no device required
- Focus on business logic validation

### Integration Tests (`src/androidTest/`)
- **UI integration tests**: User interface workflows
- **Hardware integration tests**: Device hardware interaction
- Require real device or emulator
- Focus on component interaction and user scenarios

## Testing Frameworks

### Primary Frameworks
- **JUnit 4**: Test runner and basic assertions
- **MockK**: Kotlin-friendly mocking framework
- **Google Truth**: Fluent assertion library
- **Hilt Testing**: Dependency injection testing
- **Espresso**: UI testing framework
- **Robolectric**: Android unit testing framework

### Coroutines Testing
- `kotlinx.coroutines.test` for coroutine testing
- `TestDispatcher` for deterministic testing
- `runTest` for coroutine test execution

## Usage Examples

### Unit Test Example

```kotlin
class MyComponentTest : BaseUnitTest() {
    @RelaxedMockK
    private lateinit var mockDependency: MyDependency
    
    @InjectMockKs
    private lateinit var component: MyComponent
    
    @Test
    fun `should perform action correctly`() = runTest {
        // Given
        val input = MyTestFactory.createInput()
        every { mockDependency.process(any()) } returns expectedResult
        
        // When
        val result = component.performAction(input)
        
        // Then
        assertThat(result).isEqualTo(expectedResult)
        verify { mockDependency.process(input) }
    }
}
```

### Integration Test Example

```kotlin
class MyActivityIntegrationTest : BaseUiIntegrationTest() {
    @Test
    fun `should display correct UI state`() {
        // Given
        waitForUiIdle()
        
        // When
        onView(withId(R.id.button)).perform(click())
        
        // Then
        onView(withId(R.id.textView))
            .check(matches(withText("Expected Text")))
    }
}
```

## Migration Guide

### From Legacy Tests

1. **Identify test category**: Unit, integration, or UI test
2. **Choose appropriate base class**: Based on test requirements
3. **Update imports**: Use Truth instead of JUnit assertions
4. **Use test factories**: Replace manual test data creation
5. **Update mocking**: Use MockK instead of Mockito
6. **Organize by feature**: Move to appropriate module directory

### Legacy Test Handling

Legacy tests are moved to `legacy/` directories during migration:
- Review and update to new architecture
- Remove redundant or obsolete tests
- Merge overlapping test coverage
- Ensure comprehensive coverage with new tests

## Running Tests

### Unit Tests
```bash
# Run all unit tests
./gradlew testDevDebugUnitTest

# Run specific test suite
./gradlew testDevDebugUnitTest --tests "com.multisensor.recording.testsuite.CoreUnitTestSuite"

# Run specific test class
./gradlew testDevDebugUnitTest --tests "com.multisensor.recording.recording.session.SessionInfoTest"
```

### Integration Tests
```bash
# Run all integration tests
./gradlew connectedDevDebugAndroidTest

# Run specific test suite
./gradlew connectedDevDebugAndroidTest --tests "com.multisensor.recording.testsuite.IntegrationTestSuite"

# Run specific test class
./gradlew connectedDevDebugAndroidTest --tests "com.multisensor.recording.ui.MainActivityIntegrationTest"
```

### Code Coverage
```bash
# Generate coverage report
./gradlew jacocoTestReport

# View report at: build/reports/jacoco/jacocoTestReport/html/index.html
```

## Best Practices

### Test Naming
- Use descriptive test names with `should_action_condition` format
- Use backticks for readable test names in Kotlin
- Group related tests with nested describe blocks when appropriate

### Test Structure
- Follow **Given-When-Then** pattern
- Use test data factories for consistent test data
- Mock external dependencies, test real business logic
- Keep tests focused on single responsibility

### Assertions
- Use Truth assertions for better readability
- Test both positive and negative scenarios
- Validate boundary conditions and edge cases
- Include error scenarios and exception handling

### Maintenance
- Update tests when requirements change
- Remove obsolete tests during refactoring
- Ensure tests are independent and can run in any order
- Review test coverage regularly and add missing tests

## Future Enhancements

- **Performance testing**: Add benchmarking tests for critical paths
- **Property-based testing**: Consider adding property-based tests
- **Visual regression testing**: Add screenshot comparison tests
- **End-to-end testing**: Add full user journey tests
- **Test parallelization**: Optimize test execution speed