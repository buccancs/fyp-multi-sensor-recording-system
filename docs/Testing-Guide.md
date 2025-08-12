# Comprehensive Testing Guide

## Overview

This guide provides complete instructions for executing the Multi-Sensor Recording System's test suite, covering all functional requirements (FR1–FR10) and non-functional requirements (NFR1–NFR8) from Chapter 3.

## Test Architecture

The testing framework covers three main components:
- **Android UI Tests**: Espresso/UiAutomator for mobile interface
- **Python Desktop Tests**: pytest-qt for PyQt5 GUI components  
- **Web Interface Tests**: Flask + Socket.IO + Playwright for web dashboard
- **Integration Tests**: Cross-component session orchestration

## Requirements-to-Tests Mapping

### Functional Requirements Coverage

- **FR1 Multi-Device Sensor Integration**
  - Android: `DevicesAndPermissionsTest.kt` - device discovery, connection flows, simulation mode
  - PyQt: `test_enhanced_main_window.py` - device panel functionality
  - Web: `test_web_dashboard.py` - device API endpoints (`/api/device/connect`, `/api/device/configure`)

- **FR2 Synchronized Multi-Modal Recording**
  - Android: `RecordingFlowTest.kt` - start/stop recording flows, session constraints
  - PyQt: Recording controls testing in main window tests
  - Web: Session lifecycle API (`/api/session/start`, `/api/session/stop`)
  - Integration: `test_session_orchestration.py` - cross-component synchronization

- **FR3 Time Synchronization Service**
  - Android: `CalibrationAndShimmerConfigTest.kt` - time sync service testing
  - Integration: Timing validation in orchestration tests

- **FR4 Session Management**
  - Android: Session constraint enforcement in `RecordingFlowTest.kt`
  - PyQt: Session menu actions and status display testing
  - Web: Session APIs and metadata handling
  - Integration: Complete session lifecycle testing

- **FR5 Data Recording and Storage**
  - Android: Data monitoring indicators in `RecordingFlowTest.kt`
  - Web: Playback APIs (`/api/playback/*`) and export functionality
  - Integration: Data aggregation testing

- **FR6 UI for Monitoring & Control**
  - Android: All test files cover UI elements and navigation
  - PyQt: Comprehensive GUI component testing
  - Web: Dashboard page rendering and API status endpoints

- **FR7 Device Synchronization & Signals**
  - Android: Sync signal testing in `CalibrationAndShimmerConfigTest.kt`
  - Integration: Device coordination validation

- **FR8 Fault Tolerance & Recovery**
  - Android: Device disconnect simulation in `DevicesAndPermissionsTest.kt`
  - Integration: Fault tolerance scenarios in orchestration tests

- **FR9 Calibration Utilities**
  - Android: `CalibrationAndShimmerConfigTest.kt` - complete calibration workflow
  - PyQt: Calibration menu actions

- **FR10 Data Transfer & Aggregation**
  - Web: Export/download API testing (`/api/session/*/download`)
  - Integration: Data aggregation after session completion

### Non-Functional Requirements Coverage

- **NFR1 Performance**
  - Android: Performance monitoring and real-time updates validation
  - Web: API response time testing and concurrent request handling
  - Integration: Multiple session performance testing

- **NFR2 Temporal Accuracy**
  - Android: Time synchronization service testing
  - Integration: Timing precision validation

- **NFR3 Reliability/Fault Tolerance**
  - Android: Error handling and recovery testing
  - PyQt: Error dialog handling
  - Web: Robust error responses
  - Integration: Device failure scenarios

- **NFR4 Data Integrity & Validation**
  - Web: API response validation and schema checking
  - Integration: Data consistency verification

- **NFR5 Security**
  - Web: Secret key configuration, error response security, no stack trace leaks
  - All: No sensitive data exposure in logs

- **NFR6 Usability**
  - Android: AccessibilityChecks integration for all UI tests
  - PyQt: UI element visibility and interaction testing
  - Web: Basic accessibility validation

- **NFR7 Scalability**
  - Web: Multiple device simulation and concurrent API testing
  - Integration: Multi-device coordination testing

- **NFR8 Maintainability & Modularity**
  - All tests maintain cognitive complexity under 15 through helper utilities
  - Modular test structure with reusable components

## Test Execution Instructions

### Prerequisites

```bash
# Install Python test dependencies
pip install -e ".[dev]"

# Install additional testing tools
pip install pytest-qt>=4.4.0 pytest-benchmark>=4.0.0 pytest-rerunfailures>=14.0
pip install playwright>=1.48.0 Flask>=3.1.0 Flask-SocketIO>=5.4.0

# Install Playwright browsers
playwright install chromium
```

### Android UI Tests

#### Basic Execution
```bash
# Build and run all Android tests
./gradlew :AndroidApp:connectedAndroidTest

# Run specific test class
./gradlew :AndroidApp:connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.multisensor.recording.NavigationTest

# Run with coverage
./gradlew :AndroidApp:createDebugCoverageReport
```

#### Individual Test Categories
```bash
# Navigation and UI flow testing
adb shell am instrument -w -e class com.multisensor.recording.NavigationTest com.multisensor.recording/com.multisensor.recording.CustomTestRunner

# Recording functionality
adb shell am instrument -w -e class com.multisensor.recording.RecordingFlowTest com.multisensor.recording/com.multisensor.recording.CustomTestRunner

# Device management and permissions
adb shell am instrument -w -e class com.multisensor.recording.DevicesAndPermissionsTest com.multisensor.recording/com.multisensor.recording.CustomTestRunner

# Calibration and configuration
adb shell am instrument -w -e class com.multisensor.recording.CalibrationAndShimmerConfigTest com.multisensor.recording/com.multisensor.recording.CustomTestRunner
```

#### Samsung Device Manual Testing
After each change, manually run tests on Samsung device:
```bash
# Connect Samsung device via USB debugging
adb devices

# Install and run tests
./gradlew :AndroidApp:connectedAndroidTest --info

# Collect logs and screenshots
adb logcat -s TestRunner:* > android_test_logs.txt
adb exec-out screencap -p > screenshot.png
```

### Python Desktop GUI Tests

```bash
# Run all GUI tests with Qt offscreen mode
QT_QPA_PLATFORM=offscreen pytest tests/gui/ -v

# Run with coverage
QT_QPA_PLATFORM=offscreen pytest tests/gui/ --cov=PythonApp/gui --cov-report=xml

# Run specific test categories
pytest tests/gui/test_enhanced_main_window.py::TestDeviceManagement -v
pytest tests/gui/test_enhanced_main_window.py::TestSessionManagement -v
pytest tests/gui/test_enhanced_main_window.py::TestRecordingControls -v

# Run with retries for flaky GUI tests
pytest tests/gui/ --reruns 3 --reruns-delay 1
```

### Web Interface Tests

#### Flask API Tests
```bash
# Run all web API tests
pytest tests/web/test_web_dashboard.py -v

# Run with coverage
pytest tests/web/ --cov=PythonApp/web_ui --cov-report=xml

# Run specific test categories
pytest tests/web/test_web_dashboard.py::TestWebRoutes -v
pytest tests/web/test_web_dashboard.py::TestAPIRoutes -v
pytest tests/web/test_web_dashboard.py::TestSocketIOEvents -v
pytest tests/web/test_web_dashboard.py::TestSecurityFeatures -v
```

#### Playwright UI Tests (Future)
```bash
# Install and run Playwright tests (when implemented)
playwright install
pytest tests/web_ui/ --headed  # For debugging
pytest tests/web_ui/           # Headless for CI
```

### Integration Tests

```bash
# Run cross-component integration tests
pytest tests/integration/test_session_orchestration.py -v -m integration

# Run with performance monitoring
pytest tests/integration/ --benchmark-only

# Run fault tolerance scenarios
pytest tests/integration/test_session_orchestration.py::TestFaultTolerance -v
```

### Complete Test Suite

```bash
# Run all tests with coverage
pytest tests/ --cov=PythonApp --cov-report=xml --cov-report=html

# Exclude external directories
pytest tests/ --cov=PythonApp --cov-report=xml --ignore=external/ --ignore=docs/generated_docs/

# Run with parallel execution
pytest tests/ -n auto

# Run with retries for stability
pytest tests/ --reruns 2 --reruns-delay 1
```

## Coverage Analysis

### Generating Coverage Reports
```bash
# Combined Python coverage
pytest tests/ --cov=PythonApp --cov-report=html --cov-report=xml

# Android coverage
./gradlew :AndroidApp:createDebugCoverageReport

# View HTML reports
open htmlcov/index.html                                    # Python
open AndroidApp/build/reports/coverage/debug/index.html   # Android
```

### Coverage Exclusions
The following directories are excluded from coverage analysis:
- `external/`
- `docs/generated_docs/`
- `*/test*`
- `*/venv/*`

### Target Coverage Metrics
- Unit test coverage: >90%
- Integration test coverage: >80%
- UI interaction coverage: >70%

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/comprehensive-tests.yml
name: Comprehensive Test Suite

on: [push, pull_request]

jobs:
  android-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Setup Android SDK
        uses: android-actions/setup-android@v2
      - name: Run Android Tests
        run: ./gradlew :AndroidApp:connectedAndroidTest
      - name: Upload Android Coverage
        uses: codecov/codecov-action@v3
        with:
          file: AndroidApp/build/reports/coverage/debug/report.xml

  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          playwright install chromium
      - name: Run GUI Tests
        run: QT_QPA_PLATFORM=offscreen pytest tests/gui/ --cov=PythonApp/gui
      - name: Run Web Tests
        run: pytest tests/web/ --cov=PythonApp/web_ui
      - name: Run Integration Tests
        run: pytest tests/integration/ --cov=PythonApp
      - name: Upload Python Coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage.xml
```

## Troubleshooting

### Common Issues

#### Android Tests
- **IdlingResource timeouts**: Increase timeout values in CustomIdlingResource
- **Device not found**: Ensure USB debugging enabled and device connected
- **Permission dialogs**: Handle with UiAutomator in DevicesAndPermissionsTest

#### PyQt Tests
- **Display issues**: Use `QT_QPA_PLATFORM=offscreen` environment variable
- **Widget not found**: Check widget hierarchy and object names
- **Threading issues**: Use `qtbot.waitUntil()` for asynchronous operations

#### Web Tests
- **Flask import errors**: Ensure Flask and Flask-SocketIO are installed
- **SocketIO connection issues**: Check server startup and port conflicts
- **Test isolation**: Use separate test databases/configurations

#### Integration Tests
- **Component availability**: Tests gracefully skip when components unavailable
- **Mock controller**: Verify mock setup matches real controller interface
- **Timing issues**: Use appropriate wait conditions between operations

### Debug Commands
```bash
# Verbose Android test execution
adb shell am instrument -w -e debug true -e class com.multisensor.recording.NavigationTest com.multisensor.recording/androidx.test.runner.AndroidJUnitRunner

# PyQt test debugging
pytest tests/gui/ -v -s --pdb

# Web test debugging with server logs
pytest tests/web/ -v -s --log-cli-level=DEBUG

# Integration test step-by-step
pytest tests/integration/ -v -s --capture=no
```

### Performance Monitoring
```bash
# Android performance profiling
./gradlew :AndroidApp:connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.enablePerformanceReporting=true

# Python benchmarking
pytest tests/ --benchmark-only --benchmark-sort=mean

# Memory usage monitoring
pytest tests/ --memray
```

## Test Maintenance

### Regular Tasks
1. Update test dependencies monthly
2. Review and update test data fixtures quarterly
3. Analyze coverage reports and improve low-coverage areas
4. Update Samsung device testing procedures as needed
5. Refresh mock data and scenarios based on real usage patterns

### Adding New Tests
1. Follow existing naming conventions (`test_*.py`, `*Test.kt`)
2. Use helper utilities to maintain cognitive complexity under 15
3. Include requirement traceability comments (e.g., `# FR4: Session Management`)
4. Add appropriate pytest markers for categorization
5. Update this guide with new test categories

### Code Quality Checks
```bash
# Python linting
flake8 tests/
black --check tests/
isort --check tests/

# Android linting
./gradlew :AndroidApp:ktlintCheck
./gradlew :AndroidApp:detekt
```

This comprehensive testing strategy ensures all requirements from Chapter 3 are thoroughly validated across all system components while maintaining high code quality and reliability standards.