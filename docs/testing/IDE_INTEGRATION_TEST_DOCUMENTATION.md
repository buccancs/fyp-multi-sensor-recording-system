# IDE Integration Test Suite Documentation

## Overview

The IDE Integration Test Suite is a comprehensive testing framework that fulfills the requirement to **"create a test that starts the PC app and the Android app through the IntelliJ IDE and tries all the buttons based on the navigation graph, knowing what follows what and checks if it was successful or not. also log everything"**.

## Test Architecture

The test suite consists of three main components:

### 1. Main Test Coordinator (`test_ide_integration_suite.py`)
- **Purpose**: Orchestrates the complete testing workflow
- **Responsibilities**:
  - Launches both PC and Android apps through IntelliJ/Gradle
  - Coordinates test execution between both applications
  - Collects and aggregates results from all test components
  - Generates comprehensive reports and logs

### 2. Android UI Test (`AndroidApp/src/androidTest/java/com/multisensor/recording/IDEIntegrationUITest.kt`)
- **Purpose**: Tests Android app navigation and button interactions
- **Testing Framework**: Android Espresso UI Testing Framework
- **Coverage**:
  - Navigation drawer functionality
  - Bottom navigation functionality
  - Fragment transitions (Recording, Devices, Calibration, Files)
  - Activity launches (Settings, Network Config, Shimmer Config)
  - Button interactions in each screen
  - Navigation flow validation

### 3. Python UI Test (`PythonApp/test_python_ui_integration.py`)
- **Purpose**: Tests Python desktop app UI elements and interactions
- **Testing Framework**: PyQt5 Testing Framework (QTest)
- **Coverage**:
  - Tab navigation (Recording, Devices, Calibration, Files)
  - Button interactions in each tab
  - Menu functionality
  - Status indicators and updates
  - Window operations and responsiveness

## Navigation Graph Testing

### Android App Navigation Structure

The test follows the complete navigation graph as defined in `nav_graph.xml`:

```
Main Navigation (Drawer + Bottom):
├── Recording Fragment (nav_recording)
│   ├── Start Recording Button
│   ├── Stop Recording Button
│   └── Preview Toggle Button
├── Devices Fragment (nav_devices)
│   ├── Connect Devices Button
│   ├── Scan Devices Button
│   └── Device Settings Button
├── Calibration Fragment (nav_calibration)
│   ├── Start Calibration Button
│   ├── Calibration Settings Button
│   └── View Results Button
└── Files Fragment (nav_files)
    ├── Browse Files Button
    ├── Export Data Button
    └── Delete Session Button

Settings Activities:
├── Settings Activity (nav_settings)
├── Network Config Activity (nav_network)
└── Shimmer Config Activity (nav_shimmer)

Bottom Navigation Shortcuts:
├── Record (bottom_nav_recording)
├── Monitor (bottom_nav_monitor)
└── Calibrate (bottom_nav_calibrate)
```

### Python App UI Structure

The test covers the tabbed interface structure:

```
Tab Navigation:
├── Recording Tab
│   ├── Start/Stop Recording Buttons
│   ├── Preview Controls
│   └── Session Settings
├── Devices Tab
│   ├── PC Connection Controls
│   ├── Android Connection Controls
│   ├── Shimmer Connection Controls
│   └── Device Scanning
├── Calibration Tab
│   ├── Calibration Controls
│   ├── Load/Save Calibration
│   └── Results Viewing
└── Files Tab
    ├── Data Export Controls
    ├── File Management
    └── Session Operations
```

## Running the Tests

### Complete IDE Integration Test Suite

```bash
# Run the complete test suite (recommended)
cd /home/runner/work/bucika_gsr/bucika_gsr
python test_ide_integration_suite.py

# Or via Gradle
./gradlew :PythonApp:runIDEIntegrationTest
```

### Individual Component Tests

#### Python UI Test Only
```bash
cd PythonApp
python test_python_ui_integration.py

# Or via Gradle
./gradlew :PythonApp:runPythonUITest
```

#### Android UI Test Only
```bash
# Requires connected Android device
./gradlew :AndroidApp:runIDEIntegrationUITest

# Or via ADB directly
adb shell am instrument -w -e class com.multisensor.recording.IDEIntegrationUITest \
  com.multisensor.recording.test/androidx.test.runner.AndroidJUnitRunner
```

## Test Execution Flow

### 1. Initialization Phase
- **Environment Setup**: Validates ADB availability, Python dependencies
- **Application Launch**: 
  - Launches Python app via `./gradlew :PythonApp:runDesktopApp`
  - Builds and installs Android app via `./gradlew :AndroidApp:assembleDebug`
  - Launches Android app via ADB commands

### 2. Testing Phase

#### Python App Testing
1. **Tab Navigation**: Tests navigation between all tabs
2. **Button Interactions**: Tests all buttons in each tab
3. **Navigation Flows**: Tests multi-step navigation sequences
4. **Menu Functionality**: Tests menu accessibility and operations
5. **Status Indicators**: Validates status indicator visibility and updates

#### Android App Testing
1. **Drawer Navigation**: Tests all drawer menu items
2. **Bottom Navigation**: Tests bottom navigation shortcuts
3. **Fragment Testing**: Tests each fragment's buttons and functionality
4. **Activity Testing**: Tests settings activities and back navigation
5. **Flow Validation**: Tests complex navigation flows between screens

### 3. Validation Phase
- **Success Criteria**: Each interaction is validated for success/failure
- **Response Time Measurement**: All interactions are timed
- **Error Handling**: Graceful handling of missing elements or failures
- **State Validation**: Ensures proper navigation state after each operation

### 4. Reporting Phase
- **Comprehensive Logging**: All interactions logged with timestamps
- **JSON Results**: Detailed results saved in structured format
- **Markdown Reports**: Human-readable summary reports
- **Success Metrics**: Overall success rates and performance metrics

## Test Results and Logging

### Result Structure

The test generates comprehensive results in the following structure:

```json
{
  "test_suite": "IDE Integration Test Suite",
  "start_time": "2025-01-16T10:30:00",
  "end_time": "2025-01-16T10:35:00",
  "total_duration": 300.5,
  "overall_success": true,
  
  "python_app": {
    "overall_success": true,
    "tab_navigation": {
      "Recording": {"success": true, "navigation_time": 0.5},
      "Devices": {"success": true, "navigation_time": 0.4}
    },
    "button_interactions": {
      "recording": {
        "start_recording_button": {"success": true, "response_time": 0.2},
        "stop_recording_button": {"success": true, "response_time": 0.1}
      }
    }
  },
  
  "android_app": {
    "overall_success": true,
    "navigation_tests": {
      "nav_recording": {"success": true, "navigation_method": "drawer_menu", "load_time": 1.2}
    },
    "button_tests": {
      "nav_recording": {
        "button_results": {
          "start_recording": {"success": true, "response_time": 0.5}
        }
      }
    },
    "flow_validation": {
      "nav_recording": {
        "flow_tests": {
          "nav_devices": {"success": true, "flow_time": 1.8}
        }
      }
    }
  },
  
  "summary": {
    "total_tests": 85,
    "passed_tests": 82,
    "failed_tests": 3,
    "success_rate": 96.5,
    "navigation_coverage": {
      "total_destinations": 10,
      "tested_destinations": 10,
      "coverage_percentage": 100.0
    }
  }
}
```

### Generated Reports

#### 1. JSON Results
- **File**: `test_results/ide_integration_test_results_YYYYMMDD_HHMMSS.json`
- **Content**: Complete structured test results
- **Usage**: Automated analysis, CI/CD integration

#### 2. Markdown Summary
- **File**: `test_results/ide_integration_summary_YYYYMMDD_HHMMSS.md`
- **Content**: Human-readable test summary with pass/fail indicators
- **Usage**: Manual review, documentation

#### 3. Log Files
- **File**: `ide_integration_test.log`
- **Content**: Detailed execution logs with timestamps
- **Usage**: Debugging, detailed analysis

## Success Validation Criteria

### Navigation Success
- **Criterion**: Target screen/fragment loads within timeout
- **Validation**: UI element visibility, correct content display
- **Timeout**: 3 seconds for navigation, 5 seconds for activity launch

### Button Interaction Success
- **Criterion**: Button responds to click within timeout
- **Validation**: No exceptions, expected UI state changes
- **Timeout**: 2 seconds for button response

### Flow Validation Success
- **Criterion**: Multi-step navigation completes successfully
- **Validation**: Each step succeeds, final state is correct
- **Timeout**: 5 seconds per step

## Error Handling and Recovery

### Graceful Degradation
- **Missing Elements**: Tests continue with warnings for missing UI elements
- **Timeout Handling**: Tests fail gracefully with detailed error messages
- **Device Connectivity**: Switches to simulation mode if Android device unavailable

### Recovery Mechanisms
- **Navigation Recovery**: Returns to known state after failed navigation
- **Connection Recovery**: Attempts to reconnect to devices before failing
- **State Reset**: Resets application state between test sections

## Integration with CI/CD

### Gradle Integration
```bash
# Build task includes test validation
./gradlew build

# Specific test tasks
./gradlew runIDEIntegrationTest        # Complete suite
./gradlew runPythonUITest              # Python UI only
./gradlew runIDEIntegrationUITest      # Android UI only
```

### Test Environment Requirements
- **Python**: PyQt5, pytest, mock (auto-installed via Gradle)
- **Android**: Connected device or emulator, ADB available
- **System**: 4GB RAM minimum, 10GB free disk space

### Automated Reporting
- **Exit Codes**: 0 for success, 1 for failure (CI/CD compatible)
- **Result Files**: Structured JSON for automated analysis
- **Notification**: Summary logged to stdout for CI/CD visibility

## Troubleshooting

### Common Issues

#### 1. Android Device Not Found
```bash
# Check device connection
adb devices

# Enable USB debugging on device
# Install app manually if needed
./gradlew :AndroidApp:installDebug
```

#### 2. PyQt5 Not Available
```bash
# Test runs in simulation mode automatically
# Install PyQt5 manually if needed
pip install PyQt5
```

#### 3. Gradle Build Failures
```bash
# Clean and rebuild
./gradlew clean build

# Check Java version (requires Java 17+)
java -version
```

### Debug Mode
```bash
# Run with verbose logging
python test_ide_integration_suite.py --verbose

# Check specific component
python PythonApp/test_python_ui_integration.py
```

## Extension Points

### Adding New Navigation Tests
1. **Update Navigation Graph**: Modify `NavigationGraph` class in main test
2. **Add UI Elements**: Update `ui_structure` in Python test
3. **Implement Test Logic**: Add specific test methods
4. **Update Validation**: Add success criteria for new elements

### Custom Test Scenarios
1. **Extend Test Sequence**: Modify `test_sequence` in navigation graph
2. **Add Performance Tests**: Extend timing measurements
3. **Add Stress Tests**: Implement load testing scenarios
4. **Add Error Injection**: Simulate failure conditions

This comprehensive test suite ensures complete validation of the multi-sensor recording system's user interface, providing confidence in the navigation flows and button interactions across both PC and Android applications.