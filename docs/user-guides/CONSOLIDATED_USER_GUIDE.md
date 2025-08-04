# Multi-Sensor Recording System - Consolidated User Guide

A comprehensive guide for users of the Multi-Sensor Synchronized Recording System.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Recording Workflows](#recording-workflows)
5. [Data Analysis](#data-analysis)
6. [Calibration](#calibration)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Quick Start Guide

### Prerequisites
- **Java 17 or Java 21** (recommended for optimal compatibility)
- **Conda/Miniconda** for Python environment management
- **Android Studio** (Arctic Fox or later) for Android development
- **Git** for version control

### Automated Setup
Run the complete automated setup:
```bash
# Complete automated setup (recommended)
python3 tools/development/setup.py

# Platform-specific setup
# Windows:
tools/development/setup_dev_env.ps1

# Linux/macOS:
tools/development/setup.sh
```

### Quick Build Commands
```bash
# Activate Python environment
conda activate gsr-env

# Build entire project
./gradlew build

# Run desktop application
./gradlew :PythonApp:runDesktopApp

# Build Android APK
./gradlew :AndroidApp:assembleDebug

# Run Python tests and validations
./gradlew :PythonApp:runPythonTests
```

## Installation

### System Requirements

#### Hardware Requirements
- **2 Android smartphones** (Samsung S22 recommended) with USB-C OTG support
- **2 Logitech Brio 4K USB webcams** for stationary high-quality video capture
- **Shimmer3 GSR+ physiological sensors** for biometric data collection
- **Windows PC** acting as the master orchestrator (minimum 8GB RAM, 50GB free space)
- **WiFi network** for device communication

#### Software Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS 10.15+
- **Java**: Version 17 or 21 (recommended)
- **Python**: 3.9-3.12 (automatically installed via Conda)
- **Android SDK**: Automatically configured during setup
- **Git**: For version control and repository management

### Installation Steps

#### 1. Clone Repository
```bash
git clone --recursive https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
```

#### 2. Run Automated Setup
The project includes automated setup scripts that handle complete environment configuration:

**Windows:**
```powershell
# Run as Administrator
.\tools\development\setup_dev_env.ps1
```

**Linux/macOS:**
```bash
chmod +x tools/development/setup.sh
./tools/development/setup.sh
```

**Python Script (Cross-platform):**
```bash
python3 tools/development/setup.py
```

#### 3. Verify Installation
```bash
# Check requirements
python tools/check_requirements.py --verbose

# Build and test
./gradlew build
./gradlew :PythonApp:runPythonTests
```

## Basic Usage

### First Recording Session

#### 1. Start Desktop Controller
```bash
conda activate gsr-env
./gradlew :PythonApp:runDesktopApp
```

#### 2. Install Android App
```bash
# Build and install debug APK
./gradlew :AndroidApp:assembleDebug
./gradlew :AndroidApp:installDebug
```

#### 3. Connect Devices
1. **Connect Android devices** to the same WiFi network as the PC
2. **Launch the Android app** on both devices
3. **Configure network settings** in the app to point to the PC's IP address
4. **Connect USB webcams** to the PC
5. **Pair Shimmer3 sensors** with Android devices via Bluetooth

#### 4. Start Recording
1. **Open Desktop Controller** and navigate to the Recording tab
2. **Verify device connections** in the Devices tab
3. **Configure recording settings** (duration, quality, sensors)
4. **Click "Start Recording"** to begin synchronized data collection
5. **Monitor progress** in real-time through the interface
6. **Stop recording** when complete

## Recording Workflows

### Standard Recording Session

#### Pre-Recording Setup
1. **Environment Preparation**
   - Ensure adequate lighting for camera recording
   - Position thermal cameras for optimal coverage
   - Verify Shimmer3 sensors are charged and properly attached
   - Check available storage space on all devices

2. **Device Configuration**
   - Configure camera resolution and frame rate settings
   - Set thermal camera temperature range and sensitivity
   - Adjust Shimmer3 GSR+ sampling rate and sensor configuration
   - Verify network connectivity and latency

3. **Calibration**
   - Run camera calibration for intrinsic parameters
   - Perform stereo calibration for RGB-thermal alignment
   - Validate Shimmer3 sensor baseline readings
   - Test system synchronization accuracy

#### Recording Process
1. **Session Initialization**
   - Create new recording session with descriptive name
   - Configure participant information and experimental conditions
   - Set recording duration and quality parameters
   - Initialize all sensor connections

2. **Recording Execution**
   - Start synchronized recording across all devices
   - Monitor real-time data streams and device status
   - Track recording progress and data quality indicators
   - Handle any connection issues or errors gracefully

3. **Session Completion**
   - Stop recording on all devices simultaneously
   - Verify data integrity and completeness
   - Generate session metadata and summary reports
   - Organize files in structured session folders

### Multi-Participant Sessions

#### Session Management
- **Participant Identification**: Assign unique IDs and configure device assignments
- **Simultaneous Recording**: Coordinate multiple Android devices for group recordings
- **Data Organization**: Maintain separate data streams while preserving synchronization
- **Quality Control**: Monitor all participants' data quality in real-time

#### Workflow Optimization
- **Parallel Setup**: Configure multiple devices simultaneously
- **Batch Processing**: Process multiple participants' data efficiently
- **Session Templates**: Save and reuse common configuration patterns
- **Automated Validation**: Verify data quality automatically after each session

## Data Analysis

### Data Structure

#### Session Organization
```
recordings/
├── session_YYYYMMDD_HHMMSS/
│   ├── session_metadata.json          # Session configuration and timing
│   ├── device_001/                    # Android device #1 data
│   │   ├── video_rgb.mp4             # RGB video recording
│   │   ├── thermal_data/             # Thermal imaging data
│   │   └── shimmer_gsr.csv           # GSR sensor data
│   ├── device_002/                    # Android device #2 data
│   │   └── [same structure]
│   ├── usb_webcam_001.mp4            # USB webcam #1 recording
│   ├── usb_webcam_002.mp4            # USB webcam #2 recording
│   └── processing_log.json           # Processing and analysis metadata
```

#### Data Formats
- **Video Data**: MP4 format with H.264 encoding, configurable resolution and frame rate
- **Thermal Data**: Binary format with accompanying metadata, temperature values in Celsius
- **GSR Data**: CSV format with timestamps, raw sensor values, and processed measurements
- **Metadata**: JSON format with session information, device configuration, and synchronization data

### Analysis Workflows

#### Basic Data Export
```bash
# Export session data for analysis
python PythonApp/src/data_export.py --session session_20250103_120000 --format csv

# Generate analysis reports
python PythonApp/src/analysis_reports.py --session session_20250103_120000 --output reports/
```

#### Advanced Processing
- **Temporal Synchronization**: Align data streams using high-precision timestamps
- **Signal Processing**: Apply filtering and processing to GSR and other sensor data
- **Video Analysis**: Extract features from RGB and thermal video streams
- **Statistical Analysis**: Generate descriptive statistics and correlation analyses

### Data Validation

#### Integrity Checks
```bash
# Validate data schemas and integrity
python tools/validate_data_schemas.py --session recordings/session_20250103_120000

# Check file completeness and corruption
python tools/validate_session_integrity.py --session session_20250103_120000
```

#### Quality Assessment
- **Synchronization Accuracy**: Verify temporal alignment across all data streams
- **Signal Quality**: Assess sensor data quality and identify artifacts
- **Video Quality**: Check for dropped frames, exposure issues, and focus problems
- **Completeness**: Ensure all expected data files are present and properly formatted

## Calibration

### Camera Calibration

#### Intrinsic Calibration
```bash
# Run camera calibration system
./gradlew :PythonApp:runCalibration

# Test calibration implementation
python PythonApp/test_calibration_implementation.py
```

**Calibration Process:**
1. **Prepare Calibration Pattern**: Use standard chessboard or circle grid pattern
2. **Capture Calibration Images**: Collect 20-30 images at various angles and distances
3. **Pattern Detection**: Automated detection of calibration pattern in images
4. **Parameter Calculation**: Compute intrinsic camera parameters and distortion coefficients
5. **Quality Assessment**: Evaluate calibration quality using RMS error and coverage analysis

#### Stereo Calibration
For RGB-thermal camera pairs:
1. **Capture Synchronized Images**: Record simultaneous RGB and thermal calibration images
2. **Pattern Matching**: Detect calibration patterns in both image modalities
3. **Stereo Parameter Calculation**: Compute rotation and translation between cameras
4. **Validation**: Verify alignment accuracy using test images

### Sensor Calibration

#### Shimmer3 GSR+ Calibration
```bash
# Test Shimmer integration and calibration
python PythonApp/test_shimmer_implementation.py
```

**Calibration Steps:**
1. **Baseline Recording**: Capture 2-3 minutes of baseline GSR data
2. **Range Validation**: Verify sensor operates within expected value ranges
3. **Sampling Rate Verification**: Confirm actual sampling rate matches configuration
4. **Response Testing**: Validate sensor responsiveness to controlled stimuli

#### System Synchronization
- **Clock Synchronization**: Align device clocks to microsecond precision
- **Latency Measurement**: Measure and compensate for communication delays
- **Trigger Validation**: Verify simultaneous start/stop across all devices
- **Drift Correction**: Account for clock drift during long recording sessions

## Troubleshooting

### Common Issues

#### Connection Problems
**Android devices not connecting:**
- Verify WiFi network connectivity on all devices
- Check firewall settings on PC (allow port 8080)
- Confirm IP address configuration in Android app
- Restart network services if needed

**USB webcams not detected:**
- Check USB connection and try different ports
- Verify camera drivers are installed
- Ensure cameras are not in use by other applications
- Test cameras individually to isolate issues

**Shimmer3 Bluetooth pairing fails:**
- Ensure Shimmer3 sensors are charged and powered on
- Clear Bluetooth cache on Android devices
- Re-pair devices following proper sequence
- Check for interference from other Bluetooth devices

#### Recording Issues
**Synchronization problems:**
- Verify all devices show synchronized time
- Check network latency and stability
- Restart synchronization process
- Use wired connections if possible for critical timing

**Poor data quality:**
- Check sensor placement and contact quality
- Verify environmental conditions (lighting, temperature)
- Adjust recording parameters for conditions
- Clean sensor contacts and calibration patterns

**Storage space errors:**
- Monitor available disk space on all devices
- Configure automatic cleanup of old sessions
- Use external storage for long recordings
- Compress or archive completed sessions

#### Performance Issues
**Slow recording start:**
- Close unnecessary applications
- Check system resource usage (CPU, memory)
- Optimize network settings for lower latency
- Update device drivers and software

**Frame drops or data loss:**
- Reduce recording quality/resolution if needed
- Ensure adequate storage I/O performance
- Monitor CPU and memory usage during recording
- Use faster storage devices (SSD) when possible

### Diagnostic Tools

#### System Health Check
```bash
# Run comprehensive system check
python tools/check_requirements.py --verbose

# Test all components
python PythonApp/run_comprehensive_tests.py
```

#### Performance Monitoring
```bash
# Monitor system performance during recording
python PythonApp/test_enhanced_stress_testing.py

# Check network resilience
python PythonApp/test_network_resilience.py
```

#### Data Validation
```bash
# Validate recorded session data
python tools/validate_data_schemas.py --session recordings/session_YYYYMMDD_HHMMSS

# Check data integrity
python tools/validate_session_integrity.py --session session_YYYYMMDD_HHMMSS
```

## FAQ

### General Questions

**Q: What is the maximum recording duration?**
A: Recording duration is limited primarily by available storage space. With adequate storage, sessions can run for several hours. Consider storage requirements: 4K video requires approximately 1GB per 2-3 minutes.

**Q: How many devices can be synchronized simultaneously?**
A: The system supports up to 8 Android devices plus 2 USB webcams simultaneously. Performance may vary based on network capacity and PC specifications.

**Q: Can the system work without internet connectivity?**
A: Yes, the system operates on local WiFi networks without internet access. Only local network connectivity between devices is required.

### Technical Questions

**Q: What video formats are supported?**
A: The system records video in MP4 format with H.264 encoding. RAW image capture is also supported for advanced analysis.

**Q: How accurate is the synchronization?**
A: The system achieves microsecond-precision synchronization across all devices using network time protocol and hardware timestamps.

**Q: Can I use different Android devices?**
A: While optimized for Samsung S22, the system works with most Android devices running Android 7.0+ with USB-C OTG support and sufficient processing power.

### Data Analysis Questions

**Q: What analysis software is recommended?**
A: The system exports data in standard formats compatible with MATLAB, Python (pandas/numpy), R, and specialized analysis software like ELAN or OpenPose.

**Q: How do I synchronize data from different modalities?**
A: All data includes high-precision timestamps. Use the provided synchronization utilities to align data streams temporally.

**Q: Can I process data in real-time?**
A: Basic real-time monitoring is available through the desktop interface. For advanced real-time processing, consider the streaming APIs for custom applications.

### Troubleshooting Questions

**Q: What should I do if recording fails to start?**
A: Check device connections, verify network connectivity, ensure adequate storage space, and review the troubleshooting section above for specific error messages.

**Q: How do I recover from a crashed recording session?**
A: The system includes automatic recovery mechanisms. Check the session folder for partial data files and use the data validation tools to assess what data was successfully recorded.

**Q: Why is my data quality poor?**
A: Data quality depends on proper sensor placement, environmental conditions, and device configuration. Review calibration procedures and optimal recording conditions.

---

For additional support and detailed technical information, see the [Implementation Guide](../implementation/CONSOLIDATED_IMPLEMENTATION_GUIDE.md) and [API Reference](../API_REFERENCE.md).