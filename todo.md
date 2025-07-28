# TODO - Multi-Sensor Recording System

This document tracks remaining tasks, future work items, and improvements for the Multi-Sensor Recording System project.

## Immediate Tasks (Milestone 1 Completion)

### Testing & Validation
- [ ] Test Gradle sync in Android Studio
- [ ] Verify Android module builds successfully
- [ ] Test Python environment setup and dependency installation
- [ ] Validate gradlew commands work on Windows
- [ ] Test runDesktopApp Gradle task
- [ ] Verify Python imports work correctly

### Documentation
- [ ] Create comprehensive README.md with setup instructions
- [ ] Add architecture diagrams (Mermaid format)
- [ ] Document development workflow
- [ ] Add troubleshooting guide

### Build System
- [ ] Create setup.ps1 bootstrapping script
- [ ] Add validation scripts for environment setup
- [ ] Test build system on fresh Windows installation

## Milestone 2.1: Android Application Implementation

### Core Android Components
- [ ] Create MainActivity class in com.multisensor.recording package
- [ ] Implement MultiSensorApplication class for Hilt setup
- [ ] Create RecordingService for foreground recording
- [ ] Implement SessionManager for file organization

### Recording Modules
- [ ] Implement CameraRecorder for 4K RGB + RAW capture
- [ ] Create ThermalRecorder for IR camera integration
- [ ] Implement ShimmerRecorder for Bluetooth sensor data
- [ ] Add PreviewStreamer for real-time preview transmission

### Communication
- [ ] Implement SocketController for PC communication
- [ ] Create network protocol definitions
- [ ] Add device discovery and pairing logic

### UI Components
- [ ] Design and implement main activity layout
- [ ] Create camera preview components
- [ ] Add recording status indicators
- [ ] Implement settings and configuration screens

## Milestone 2.2+: Advanced Android Features

### Hardware Integration
- [ ] Integrate Shimmer3 GSR+ SDK when available
- [ ] Integrate Topdon thermal camera SDK when available
- [ ] Implement USB OTG thermal camera support
- [ ] Add hardware-accelerated video encoding

### Data Management
- [ ] Implement local data storage and organization
- [ ] Add data compression and optimization
- [ ] Create data transfer protocols to PC
- [ ] Implement backup and recovery mechanisms

### Performance & Reliability
- [ ] Add thermal management for continuous recording
- [ ] Implement power management optimizations
- [ ] Add error handling and recovery
- [ ] Create comprehensive logging system

## Milestone 3.x: Python Desktop Controller

### Core Desktop Features
- [ ] Implement actual device communication protocols
- [ ] Add USB webcam capture and recording
- [ ] Create stimulus presentation system
- [ ] Implement real-time device monitoring

### Camera Calibration
- [ ] Implement camera intrinsic calibration
- [ ] Add stereo camera calibration
- [ ] Create thermal-RGB camera alignment
- [ ] Add calibration validation tools

### Data Processing
- [ ] Implement data synchronization algorithms
- [ ] Add multi-stream video processing
- [ ] Create data export and analysis tools
- [ ] Implement real-time preview aggregation

### User Interface Enhancements
- [ ] Add device configuration panels
- [ ] Implement recording session management
- [ ] Create data visualization components
- [ ] Add experiment protocol management

## Technical Debt & Improvements

### Code Quality
- [ ] Add comprehensive unit tests for Android components
- [ ] Create integration tests for Python modules
- [ ] Implement code coverage reporting
- [ ] Add static code analysis tools

### Build System
- [ ] Add CI/CD pipeline configuration
- [ ] Implement automated testing on multiple Android versions
- [ ] Add Python version compatibility testing
- [ ] Create automated release builds

### Documentation
- [ ] Generate API documentation for Android components
- [ ] Create Python module documentation
- [ ] Add code examples and tutorials
- [ ] Create video setup guides

### Security & Privacy
- [ ] Implement secure communication protocols
- [ ] Add data encryption for sensitive recordings
- [ ] Create privacy compliance documentation
- [ ] Implement secure credential management

## Future Enhancements

### Platform Support
- [ ] Consider macOS support for Python controller
- [ ] Evaluate Linux compatibility
- [ ] Investigate iOS app possibility

### Advanced Features
- [ ] Add machine learning integration for data analysis
- [ ] Implement cloud storage and synchronization
- [ ] Create web-based monitoring dashboard
- [ ] Add support for additional sensor types

### Research Features
- [ ] Implement advanced synchronization algorithms
- [ ] Add support for multiple participant recording
- [ ] Create automated experiment protocols
- [ ] Add real-time data analysis capabilities

## Known Issues & Limitations

### Current Limitations
- MainActivity class referenced in AndroidManifest.xml but not yet created
- Python module imports show validation warnings (expected until environment is set up)
- Gradle wrapper JAR file not included (will be downloaded on first sync)
- No actual hardware integration yet (placeholder implementations)

### Technical Constraints
- Requires Python 3.x installation on development machine
- Android Studio with Python plugin needed for full IDE support
- Windows-specific paths and scripts (cross-platform support needed)
- Thermal camera SDK integration pending vendor documentation

## Notes

- Items marked with TODO comments in code should be tracked here
- Completed items should be moved to changelog.md
- High-priority items should be addressed in current milestone
- Future ideas should be moved to backlog.md when appropriate