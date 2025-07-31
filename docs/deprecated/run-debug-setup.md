# Run and Debug Configuration Setup

This document describes the run and debug configurations available for the Multi-Sensor Recording System project.

## Prerequisites

- Android Studio or IntelliJ IDEA with Android plugin
- Python 3.x with PyQt5 installed
- Android SDK and emulator/device for Android testing

## Available Configurations

### Android Configurations

#### 1. Android App (devDebug)
- **Purpose**: Launch the main Android application in development mode
- **Target**: MainActivity with devDebug build variant
- **Features**: 
  - Full debugging support with breakpoints
  - Live preview and camera functionality
  - Development environment with debug logging

#### 2. Android Unit Tests
- **Purpose**: Run unit tests for Android components
- **Target**: All unit tests in AndroidApp/src/test
- **Features**:
  - Code coverage reporting
  - MockK and Robolectric support
  - Hilt dependency injection testing

#### 3. Android Instrumentation Tests
- **Purpose**: Run integration tests on device/emulator
- **Target**: All instrumentation tests in AndroidApp/src/androidTest
- **Features**:
  - Device/emulator execution
  - UI testing with Espresso
  - Camera and hardware testing capabilities

### Python Configurations

#### 1. Python App
- **Purpose**: Launch the Python controller application
- **Target**: PythonApp/src/main.py
- **Features**:
  - PyQt5 GUI application
  - Multi-sensor control interface
  - Network communication with Android devices

#### 2. Python Tests
- **Purpose**: Run Python unit tests
- **Target**: All tests in PythonApp/tests
- **Features**:
  - Pytest framework
  - Code coverage reporting
  - Verbose output for debugging

## Usage Instructions

### Running Configurations

1. **In Android Studio/IntelliJ IDEA**:
   - Open the project
   - Select desired configuration from the run configuration dropdown
   - Click the Run (▶️) or Debug (🐛) button

2. **For Android App**:
   - Ensure Android device/emulator is connected
   - Grant necessary permissions when prompted
   - The app will launch with camera and sensor capabilities

3. **For Python App**:
   - Ensure Python environment has PyQt5 installed
   - The GUI controller will launch for managing Android devices

### Debugging

- **Breakpoints**: Set breakpoints in code and use Debug configurations
- **Logging**: Check Android Logcat and Python console for debug output
- **Coverage**: Use coverage reports to analyze test effectiveness

## Gradle Fixes Applied

- **Hilt Plugin**: Added missing Hilt plugin classpath to root build.gradle
- **Build Sync**: Resolved dependency injection compilation issues
- **Module Configuration**: Proper module references for all configurations

## Module Configuration Fixes Applied

- **Module Definition**: Updated .idea/modules.xml to include AndroidApp and PythonApp modules
- **Module Files**: Created missing AndroidApp.iml and PythonApp.iml files with proper configurations
- **Root Module**: Renamed asdasd.iml to MultiSensorRecordingSystem.iml to match project name
- **Run Configurations**: Updated all run configurations to use correct module names:
  - Android App: Uses "AndroidApp" module
  - Android Unit Tests: Uses "AndroidApp" module
  - Android Instrumentation Tests: Uses "AndroidApp" module
  - Python App: Uses "PythonApp" module
  - Python Tests: Uses "PythonApp" module

## Troubleshooting

### Common Issues

1. **Gradle Sync Fails**:
   - Ensure Hilt plugin is properly configured
   - Check internet connection for dependency downloads
   - Clean and rebuild project

2. **Android App Won't Launch**:
   - Verify device/emulator is connected
   - Check camera and storage permissions
   - Ensure devDebug variant is selected

3. **Python App Issues**:
   - Install PyQt5: `pip install PyQt5`
   - Check Python interpreter configuration
   - Verify working directory is set to PythonApp

4. **Tests Not Running**:
   - Ensure test dependencies are downloaded
   - Check module paths in configurations
   - Verify test files exist in expected directories

5. **"No Module Specified" Error**:
   - Check that .idea/modules.xml includes all required modules
   - Verify that .iml files exist for each module (AndroidApp.iml, PythonApp.iml)
   - Ensure run configurations reference correct module names
   - Try refreshing Gradle project or reimporting project structure
   - Check that settings.gradle properly declares all modules

## Configuration Files

The run/debug configurations are stored in:
- `.idea/runConfigurations/Android_App_devDebug.xml`
- `.idea/runConfigurations/Android_Unit_Tests.xml`
- `.idea/runConfigurations/Android_Instrumentation_Tests.xml`
- `.idea/runConfigurations/Python_App.xml`
- `.idea/runConfigurations/Python_Tests.xml`

These files are included in version control for team consistency.