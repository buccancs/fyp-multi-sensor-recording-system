# System User Guide - Multi-Sensor Recording System

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [System Setup and Installation](#system-setup-and-installation)
3. [Navigation and User Interface](#navigation-and-user-interface)
4. [Device Management](#device-management)
5. [Recording Sessions](#recording-sessions)
6. [Camera Calibration](#camera-calibration)
7. [Data Management and Export](#data-management-and-export)
8. [Testing and Validation](#testing-and-validation)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Features](#advanced-features)

---

## Quick Start Guide

### System Overview

The Multi-Sensor Recording System enables synchronized data collection from multiple sensor modalities for research applications. The system combines Android mobile applications with a Python desktop controller to capture:

- **RGB video** from smartphone cameras (4K recording capability)
- **Thermal imaging** from attached thermal cameras
- **Physiological data** from Shimmer3 GSR+ sensors via Bluetooth
- **High-quality video** from USB webcams connected to PC
- **Synchronized timing** across all devices with microsecond precision

### Prerequisites Checklist

Before starting, ensure you have:
- [ ] **Java 17 or Java 21** installed on your system
- [ ] **Android smartphones** (Samsung S22 recommended) with thermal cameras
- [ ] **Windows PC** with USB ports for webcam connections
- [ ] **Shimmer3 GSR+ sensors** with charged batteries
- [ ] **USB webcams** (Logitech Brio 4K recommended)
- [ ] **WiFi network** for device communication
- [ ] **Android Studio** for app development (if needed)

### 5-Minute Setup

1. **Download and extract** the project repository
2. **Run automated setup**:
   ```bash
   python3 tools/development/setup.py
   ```
3. **Build the project**:
   ```bash
   ./gradlew build
   ```
4. **Install Android app** on smartphones:
   ```bash
   ./gradlew :AndroidApp:installDebug
   ```
5. **Start desktop controller**:
   ```bash
   ./gradlew :PythonApp:runDesktopApp
   ```

---

## System Setup and Installation

### Automated Installation

The system provides automated setup scripts that handle complete environment configuration:

#### Windows Setup
```powershell
# Run PowerShell as Administrator
tools/development/setup_dev_env.ps1
```

#### Linux/macOS Setup
```bash
# Make script executable
chmod +x tools/development/setup.sh
./tools/development/setup.sh
```

#### Complete Setup (All Platforms)
```bash
# Universal setup script
python3 tools/development/setup.py
```

These scripts automatically:
- Install Miniconda Python environment
- Configure all required dependencies
- Set up Android SDK components
- Validate build system integrity
- Configure device permissions

### Manual Installation

If automated setup fails, follow these manual steps:

#### 1. Java Installation
```bash
# Verify Java version
java -version

# Should show Java 17 or Java 21
# If not installed, download from:
# https://adoptopenjdk.net/
```

#### 2. Python Environment
```bash
# Install Miniconda (if not present)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create conda environment
conda env create -f environment.yml
conda activate thermal-env
```

#### 3. Android Configuration
```bash
# Set Android SDK path
export ANDROID_HOME=/path/to/android-sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME

# Verify Android SDK
$ANDROID_HOME/tools/bin/sdkmanager --list
```

#### 4. Build Verification
```bash
# Test complete build
./gradlew build

# Verify Python dependencies
python -c "import cv2, numpy, PyQt5; print('Dependencies OK')"
```

### Environment Validation

Run the validation script to ensure proper setup:

```bash
# Comprehensive environment check
python scripts/validate-build.py --verbose

# Quick validation
python scripts/validate-build.py --quick
```

---

## Navigation and User Interface

### Desktop Controller Interface

The Python desktop application provides the central control interface:

```
┌─────────────────────────────────────────────────────────────┐
│ Multi-Sensor Recording System - Desktop Controller         │
├─────────────────────────────────────────────────────────────┤
│ Session Management │ Device Status │ Recording Controls    │
├─────────────────────┼───────────────┼───────────────────────┤
│ ○ New Session      │ 📱 Phone 1    │ ●  REC              │
│ ▶ Start Recording  │ ✅ Connected   │ ⏸  PAUSE            │
│ ⏹ Stop Recording   │ 📱 Phone 2    │ ⏹  STOP             │
│ 💾 Save Session    │ ❌ Disconnected│ 🔄 SYNC             │
├─────────────────────┼───────────────┼───────────────────────┤
│ Real-Time Monitor   │ Quality Metrics│ Export Options       │
│ 📊 Data Streams     │ 📈 Signal Quality      │ 📁 CSV Export │
│ 🎥 Video Feeds      │ 🌡 Temperature │ 📊 MATLAB Export     │
│ 💓 GSR Readings     │ 🔗 Sync Status │ 📋 Report Generation │
└─────────────────────┴───────────────┴───────────────────────┘
```

### Mobile Application Interface

The Android application provides device-specific controls:

**Main Screen:**
- Session connection status
- Local recording controls
- Device configuration options
- Real-time data preview

**Navigation Tabs:**
- **Session:** Connection and recording management
- **Cameras:** RGB and thermal camera controls
- **Sensors:** GSR and motion sensor configuration
- **Settings:** Device preferences and diagnostics

---

## Device Management

### Mobile Device Setup

#### 1. Initial Configuration
1. **Install** the Android application on each smartphone
2. **Enable** developer options and USB debugging
3. **Grant** camera, storage, and location permissions
4. **Connect** thermal camera accessories (if using)
5. **Configure** device identifier in app settings

#### 2. Network Configuration
1. **Connect** all devices to the same WiFi network
2. **Note** the desktop controller's IP address
3. **Test** network connectivity between devices
4. **Configure** firewall settings if needed

#### 3. Bluetooth Sensor Pairing
1. **Turn on** Bluetooth on mobile devices
2. **Power on** Shimmer3 GSR+ sensors
3. **Pair** sensors through device settings
4. **Test** connection in the application
5. **Verify** data streaming functionality

### USB Webcam Setup

#### 1. Hardware Connection
1. **Connect** USB webcams to the desktop computer
2. **Verify** camera recognition in device manager
3. **Test** camera functionality with built-in applications
4. **Position** cameras for optimal field of view

#### 2. Software Configuration
1. **Start** the desktop controller application
2. **Navigate** to camera configuration panel
3. **Select** active cameras from detected devices
4. **Configure** resolution and frame rate settings
5. **Test** video capture functionality

---

## Recording Sessions

### Session Creation

#### 1. Pre-Recording Setup
1. **Launch** desktop controller application
2. **Create** new session with descriptive name
3. **Configure** session parameters:
   - Recording duration
   - Data quality settings
   - Output directory
   - Participant information

#### 2. Device Connection
1. **Start** mobile applications on all devices
2. **Connect** to desktop controller using WiFi
3. **Verify** all devices show "Connected" status
4. **Test** communication with ping/status checks

#### 3. Sensor Validation
1. **Check** all sensors are detected and responsive
2. **Verify** data streaming from each device
3. **Confirm** video feeds are active and clear
4. **Test** synchronization timing accuracy

### Recording Process

#### 1. Start Recording
```bash
# Desktop Controller Commands
Session → New Session → Configure → Start Recording

# Mobile App Actions
1. Tap "Connect to Controller"
2. Wait for "Ready" status
3. Recording starts automatically
```

#### 2. During Recording
- **Monitor** real-time data streams on desktop controller
- **Check** signal quality indicators regularly
- **Note** any warnings or error messages
- **Avoid** interrupting network connections

#### 3. Stop Recording
```bash
# Desktop Controller
Session → Stop Recording → Save Session

# Automatic Actions
- Data synchronization across devices
- File organization and naming
- Quality assessment generation
- Session metadata creation
```

### Session Management

#### Session Organization
```
recordings/
├── experiment_A_20250131_143022/
│   ├── session_metadata.json
│   ├── session_20250131_143022_log.json
│   ├── devices/
│   │   ├── phone_1/
│   │   ├── phone_2/
│   │   └── shimmer_01/
│   ├── webcam/
│   ├── processing/
│   └── exports/
```

#### File Types Generated
- **Video files:** RGB and thermal recordings (MP4 format)
- **Sensor data:** GSR and motion data (CSV format)
- **Metadata:** Session information and event logs (JSON format)
- **Calibration:** Camera calibration data (JSON format)

---

## Camera Calibration

### Calibration Process

#### 1. Preparation
1. **Print** calibration checkerboard patterns
2. **Mount** patterns on rigid surface
3. **Ensure** adequate lighting conditions
4. **Position** cameras for clear pattern view

#### 2. Calibration Capture
```bash
# Desktop Controller
Calibration → New Calibration → Select Devices → Start Capture

# Process
1. Show checkerboard to cameras
2. Move pattern to different positions
3. Capture 20-30 images per camera
4. Ensure variety in pattern orientations
```

#### 3. Calibration Computation
1. **Review** captured images for quality
2. **Remove** blurry or poorly detected images
3. **Run** calibration algorithm
4. **Assess** calibration quality metrics
5. **Save** calibration parameters

### Calibration Quality Assessment

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| **RMS Error** | < 0.5 pixels | 0.5-1.0 pixels | > 1.0 pixels |
| **Pattern Detection** | > 95% | 85-95% | < 85% |
| **Corner Accuracy** | < 0.1 pixels | 0.1-0.2 pixels | > 0.2 pixels |

---

## Data Management and Export

### Data Organization

#### Session Structure
Each recording session creates a hierarchical folder structure:

```
session_YYYYMMDD_HHMMSS/
├── session_metadata.json          # Session configuration and info
├── session_YYYYMMDD_HHMMSS_log.json  # Event timeline
├── devices/                       # Device-specific recordings
│   ├── phone_1/
│   │   ├── phone_1_rgb_YYYYMMDD_HHMMSS.mp4
│   │   ├── phone_1_thermal_YYYYMMDD_HHMMSS.mp4
│   │   └── phone_1_motion_YYYYMMDD_HHMMSS.csv
│   └── shimmer_01/
│       └── shimmer_01_gsr_YYYYMMDD_HHMMSS.csv
├── webcam/                        # PC camera recordings
│   ├── webcam_1_YYYYMMDD_HHMMSS.mp4
│   └── webcam_2_YYYYMMDD_HHMMSS.mp4
├── processing/                    # Analysis outputs
│   ├── hand_segmentation/
│   ├── synchronization/
│   └── quality_assessment/
└── exports/                       # Data exports
    ├── csv/
    ├── matlab/
    └── reports/
```

### Export Options

#### CSV Export
```bash
# Desktop Controller
Data → Export → CSV Format

# Includes
- Synchronized sensor data
- Timestamp alignment
- Quality metrics
- Session metadata
```

#### MATLAB Export
```bash
# Desktop Controller
Data → Export → MATLAB Format

# Generates
- .mat files with structured data
- Variable naming conventions
- Documentation scripts
- Analysis templates
```

#### Report Generation
```bash
# Desktop Controller
Reports → Generate Session Report

# Contains
- Session summary statistics
- Data quality assessment
- Device performance metrics
- Recommendations
```

---

## Testing and Validation

### System Testing

#### 1. Component Testing
```bash
# Test individual components
python PythonApp/test_calibration_implementation.py
python PythonApp/test_shimmer_implementation.py
python PythonApp/test_camera_recording.py
```

#### 2. Integration Testing
```bash
# Test complete system
python PythonApp/run_complete_test_suite.py

# Includes
- Device communication tests
- Data synchronization validation
- Recording quality assessment
- Error handling verification
```

#### 3. Performance Testing
```bash
# Performance benchmarks
python scripts/performance_testing.py

# Measures
- CPU and memory usage
- Network latency and throughput
- Storage I/O performance
- Battery consumption (mobile)
```

### Data Validation

#### Quality Checks
- **Temporal synchronization:** Verify timestamp alignment across devices
- **Data completeness:** Check for missing or corrupt data segments
- **Signal quality:** Assess sensor data quality and noise levels
- **Video quality:** Validate recording resolution and frame rates

#### Validation Tools
```bash
# Validate session data
python tools/validate_data_schemas.py --session path/to/session

# Check file naming
python tools/check_naming_conventions.py --directory recordings/

# Quality assessment
python tools/assess_session_quality.py --session path/to/session
```

---

## Troubleshooting

### Common Issues

#### Connection Problems

**Symptom:** Mobile devices cannot connect to desktop controller
**Solutions:**
1. Verify all devices on same WiFi network
2. Check firewall settings on desktop computer
3. Restart WiFi router and reconnect devices
4. Update IP address in mobile app settings

#### Recording Issues

**Symptom:** Poor video quality or missing data
**Solutions:**
1. Check available storage space on all devices
2. Verify camera permissions granted on mobile devices
3. Test individual device recording capabilities
4. Review network bandwidth and stability

#### Synchronization Problems

**Symptom:** Data timestamps not aligned across devices
**Solutions:**
1. Ensure all devices have accurate time settings
2. Check network latency between devices
3. Verify synchronization algorithm configuration
4. Re-run synchronization processing if needed

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| **E001** | Device connection timeout | Check network connectivity |
| **E002** | Sensor initialization failed | Restart sensor and check pairing |
| **E003** | Storage space insufficient | Free up disk space |
| **E004** | Camera access denied | Grant camera permissions |
| **E005** | Calibration pattern not detected | Improve lighting and pattern positioning |

### Performance Optimization

#### System Performance
1. **Close** unnecessary applications during recording
2. **Disable** automatic updates and background sync
3. **Use** SSD storage for better I/O performance
4. **Monitor** CPU and memory usage during sessions

#### Network Optimization
1. **Use** dedicated WiFi network for recordings
2. **Position** devices close to WiFi router
3. **Avoid** interference from other wireless devices
4. **Configure** QoS settings for priority traffic

---

## Advanced Features

### Multi-Session Analysis

#### Batch Processing
```bash
# Process multiple sessions
python scripts/batch_analysis.py --directory recordings/ --output results/

# Features
- Automated quality assessment
- Cross-session comparison
- Statistical analysis
- Report generation
```

#### Data Mining
```bash
# Advanced analytics
python scripts/data_mining.py --sessions session1,session2,session3

# Includes
- Pattern recognition
- Correlation analysis
- Machine learning insights
- Predictive modeling
```

### Custom Configuration

#### Session Templates
Create reusable session configurations:
```json
{
  "template_name": "stress_test_protocol",
  "recording_duration": 1800,
  "devices": ["phone_1", "phone_2", "shimmer_01"],
  "quality_settings": "high",
  "export_formats": ["csv", "matlab"]
}
```

#### Device Profiles
Configure device-specific settings:
```json
{
  "device_id": "phone_1",
  "camera_resolution": "4K",
  "thermal_settings": "high_sensitivity",
  "motion_sampling_rate": 100,
  "recording_location": "/sdcard/recordings/"
}
```

### Research Integration

#### Statistical Analysis
The system integrates with common research tools:
- **R integration:** Export data for statistical analysis
- **Python notebooks:** Jupyter integration for data exploration
- **MATLAB compatibility:** Direct data import for signal processing
- **SPSS format:** Export for social science research

#### Publication Support
- **Citation generation:** Automatic method description generation
- **Figure creation:** Automated visualization for publications
- **Data archival:** Long-term storage format compliance
- **Reproducibility:** Complete session recreation capabilities