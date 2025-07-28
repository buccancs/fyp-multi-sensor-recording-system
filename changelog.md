# Changelog

All notable changes to the Multi-Sensor Recording System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-07-28

### Added - Milestone 1: Monorepo Setup
- **Gradle Multi-Project Structure**: Implemented complete monorepo setup for Android (Kotlin) + Python (PyQt5) development in Android Studio
- **Root Project Configuration**:
  - Created `settings.gradle` with AndroidApp and PythonApp modules
  - Created root `build.gradle` with common configuration and plugin versions
  - Added `gradle.properties` with project-wide settings and optimizations
  - Set up Gradle wrapper files (gradlew, gradlew.bat, gradle-wrapper.properties) for version 8.4
- **AndroidApp Module**:
  - Created complete Android module structure with `build.gradle`
  - Configured Android SDK (compileSdk 34, minSdk 24, targetSdk 34)
  - Added dependencies for Camera2 API, Kotlin coroutines, lifecycle components, networking, and Hilt DI
  - Created `AndroidManifest.xml` with essential permissions for camera, storage, network, Bluetooth, and foreground services
  - Set up standard Android source structure (src/main/java, res directories)
- **PythonApp Module**:
  - Created Python module with `build.gradle` using ru.vyarus.use-python plugin v3.0.0
  - Configured Python dependencies: PyQt5 5.15.7, OpenCV 4.8.0.74, NumPy 1.24.3, and supporting libraries
  - Added Gradle tasks: `runDesktopApp`, `runCalibration`, `testPythonSetup`
  - Created `main.py` with complete PyQt5 desktop controller application featuring:
    - Multi-sensor device status monitoring
    - Recording control interface (start/stop/calibration)
    - System logging and status updates
    - Extensible architecture for future sensor integration
- **Development Environment**:
  - Updated `.gitignore` with comprehensive entries for Android, Python, and Windows artifacts
  - Configured project for unified development in Android Studio on Windows
  - Set up virtual environment management through Gradle

### Technical Details
- **Architecture**: Clean separation between Android and Python modules while maintaining unified build system
- **Build System**: Gradle multi-project setup enabling consistent tooling across different technology stacks
- **IDE Integration**: Configured for Android Studio with Python plugin support
- **Version Control**: Comprehensive .gitignore covering all build artifacts and environment-specific files

### Future Work
- TODO: Add Shimmer SDK integration when available
- TODO: Add Topdon thermal camera SDK integration when available
- TODO: Implement actual device communication protocols
- TODO: Add camera calibration algorithms
- TODO: Implement data synchronization logic

### Notes
- This milestone establishes the foundation for the Multi-Sensor Synchronized Recording System
- All components are ready for feature implementation in subsequent milestones
- Project structure follows best practices for monorepo development and cross-platform integration