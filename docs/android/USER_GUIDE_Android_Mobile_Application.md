# User Guide: Android Mobile Data Collection Node

## Quick Start Guide

### Pre-flight Checklist

Before starting a recording session, ensure the following prerequisites are met:

#### ✅ Hardware Setup
- [ ] Samsung S22 smartphone with sufficient battery (>50%)
- [ ] Topdon TC001 thermal camera connected via USB-C
- [ ] Shimmer3 GSR+ sensor paired via Bluetooth
- [ ] WiFi network connection established
- [ ] Minimum 2GB available storage space

#### ✅ Software Configuration
- [ ] Android app installed and permissions granted
- [ ] PC controller running and accessible on network
- [ ] Network configuration verified (IP address and port)
- [ ] All sensors calibrated and tested
- [ ] Session parameters configured

#### ✅ Environmental Setup
- [ ] Stable lighting conditions for thermal-contrast calibration
- [ ] Clear workspace for thermal camera field of view
- [ ] Participant electrodes properly attached for GSR measurement
- [ ] Network connectivity stable and tested

---

## Getting Started

### 1. Initial App Launch

When you first launch the Android Mobile Data Collection app:

1. **Grant Permissions**: The app will request necessary permissions
   - Camera access for video recording
   - Microphone access for audio capture
   - Storage access for session data
   - Location access for Bluetooth discovery
   - Bluetooth access for Shimmer sensors

2. **Network Configuration**: Configure PC controller connection
   - Navigate to Settings → Network Configuration
   - Enter PC controller IP address (e.g., 192.168.1.100)
   - Set communication port (default: 8080)
   - Test connection with "Test Connection" button

3. **Sensor Setup**: Initialize and configure sensors
   - Connect thermal camera via USB-C
   - Pair Shimmer3 GSR+ sensor via Bluetooth
   - Verify all sensors appear in Device Status

### 2. Main Interface Overview

The main interface provides comprehensive control over all recording functions:

#### Navigation Drawer
- **Recording**: Primary recording controls and session management
- **Devices**: Sensor connection status and configuration
- **Calibration**: Camera and sensor calibration procedures
- **Files**: Session data browser and export functions
- **Settings**: App configuration and preferences

#### Bottom Navigation Bar
- **Record**: Quick access to start/stop recording
- **Monitor**: Real-time sensor status monitoring
- **Calibrate**: One-touch calibration procedures

#### Status Indicators
- **Network Status**: PC connection quality (green/yellow/red)
- **Camera Status**: Camera readiness and recording state
- **Thermal Status**: Thermal camera connection and temperature
- **Shimmer Status**: GSR sensor connection and data rate
- **Storage Status**: Available storage space and session count

---

## Recording Procedures

### 3. Preparing for Recording

#### 3.1 Session Configuration

1. **Access Recording Tab**
   - Tap "Recording" in navigation drawer
   - Review current session parameters

2. **Configure Recording Parameters**
   - **Resolution**: Select video resolution (1080p/4K)
   - **Frame Rate**: Choose frame rate (30/60 fps)
   - **Recording Quality**: Set quality level (High/Ultra)
   - **Duration**: Set maximum recording duration

3. **Verify Sensor Configuration**
   - **Camera**: Check focus, exposure, and white balance
   - **Thermal**: Verify temperature range and calibration
   - **Shimmer**: Confirm sampling rate and sensor selection

#### 3.2 Pre-Recording Checklist

Before each recording session:

1. **Sensor Status Check**
   - All sensors show green "Connected" status
   - No error messages in status panel
   - Preview streams active and responsive

2. **Storage Verification**
   - Sufficient storage space available (recommended: >1GB per 10 minutes)
   - Previous session data exported or archived
   - Temporary files cleaned up

3. **Network Quality Check**
   - PC controller connection stable
   - Network latency acceptable (<50ms)
   - Bandwidth sufficient for preview streaming

### 4. Recording Session Workflow

#### 4.1 Starting a Recording Session

1. **Coordinate with PC Controller**
   - Ensure PC controller is ready to receive data
   - Verify all Android devices are connected
   - Confirm experimental protocol timing

2. **Initialize Recording**
   - Tap "Start Recording" button
   - Wait for "Recording Started" confirmation
   - Monitor sensor status indicators

3. **Session Monitoring**
   - Watch real-time data rates
   - Monitor storage usage
   - Check for error messages

#### 4.2 During Recording

**Visual Indicators:**
- **Red Recording Icon**: Active recording in progress
- **Timer Display**: Current session duration
- **Data Rate Indicators**: Real-time sensor data throughput
- **Storage Gauge**: Remaining storage capacity

**Quality Monitoring:**
- **Frame Rate**: Actual vs. target frame rate
- **Network Quality**: Connection stability
- **Sensor Health**: Individual sensor status
- **Error Count**: Number of dropped frames or connection issues

**Participant Instructions:**
- Maintain natural posture and movement
- Avoid covering thermal camera field of view
- Keep GSR electrodes properly positioned
- Follow experimental protocol timing

#### 4.3 Ending a Recording Session

1. **Coordinated Stop**
   - Wait for PC controller stop signal (automatic)
   - OR manually tap "Stop Recording" if needed

2. **Session Finalization**
   - Wait for "Session Complete" message
   - Review session summary statistics
   - Check for any error reports

3. **Data Verification**
   - Verify all expected data files created
   - Check file sizes are reasonable
   - Review session metadata

---

## Sensor Configuration

### 5. Camera Setup and Configuration

#### 5.1 Camera Settings

**Basic Configuration:**
- **Resolution**: 4K (3840×2160) for research quality
- **Frame Rate**: 30fps for standard recording, 60fps for motion analysis
- **Format**: H.264 for video, DNG for RAW images
- **Stabilization**: Optical stabilization enabled

**Advanced Settings:**
- **ISO**: Auto or manual (100-3200)
- **Shutter Speed**: Auto or manual (1/60 - 1/1000)
- **Focus**: Auto-focus or manual focus distance
- **White Balance**: Auto or manual color temperature

#### 5.2 RAW Image Capture

For calibration and precise analysis:
- **Format**: Adobe DNG (Digital Negative)
- **Timing**: Simultaneous with video recording
- **Frequency**: Configurable (every 1-10 seconds)
- **Quality**: Full resolution, uncompressed

### 6. Thermal Camera Integration

#### 6.1 Topdon TC001 Configuration

**Connection Setup:**
1. Connect thermal camera via USB-C OTG adapter
2. Grant USB device permissions when prompted
3. Wait for "Thermal Camera Connected" message
4. Verify thermal preview appears

**Temperature Settings:**
- **Range**: Auto-adjust or manual (-20°C to +400°C)
- **Emissivity**: Material-specific setting (0.1-1.0)
- **Palette**: Color mapping for temperature visualization
- **Calibration**: Regular background temperature calibration

#### 6.2 Thermal Data Export

**Data Formats:**
- **Binary Format**: Raw thermal data with temperature values
- **Metadata**: Camera parameters, calibration data, timestamps
- **Preview Video**: Visual representation for review
- **CSV Export**: Temperature readings at specific points

### 7. Shimmer3 GSR+ Sensor

#### 7.1 Bluetooth Pairing

**Initial Setup:**
1. Power on Shimmer3 GSR+ sensor
2. Navigate to Devices → Shimmer Configuration
3. Tap "Scan for Devices"
4. Select your Shimmer sensor from the list
5. Wait for "Paired Successfully" confirmation

**Pairing Troubleshooting:**
- Ensure sensor is in pairing mode (LED blinking)
- Clear Bluetooth cache if connection fails
- Restart sensor if not discoverable
- Check sensor battery level

#### 7.2 GSR Recording Configuration

**Sampling Settings:**
- **Sampling Rate**: 128Hz (recommended) or 256Hz/512Hz
- **Sensor Selection**: GSR, internal ADC
- **Range**: Automatic gain control or manual range
- **Buffer Size**: 1000 samples (configurable)

**Data Quality:**
- **Signal Quality Monitoring**: Real-time signal quality indicator
- **Electrode Contact**: Check impedance measurements
- **Baseline Calibration**: Automatic baseline adjustment
- **Artifact Detection**: Motion artifact identification

---

## Calibration Procedures

### 8. Camera Calibration

#### 8.1 Intrinsic Calibration

**Equipment Needed:**
- Printed checkerboard pattern (9×6 squares)
- Good lighting conditions
- Stable hands or tripod

**Procedure:**
1. Navigate to Calibration → Camera Calibration
2. Tap "Start Intrinsic Calibration"
3. Hold checkerboard pattern in camera view
4. Slowly move pattern to different positions:
   - Center of frame
   - All four corners
   - Various distances (30cm to 2m)
   - Different orientations (rotated, tilted)

**Quality Indicators:**
- **Pattern Detection**: Green outline around detected corners
- **Coverage**: Progress bar showing frame coverage
- **RMS Error**: Target <0.5 pixels for good calibration
- **Sample Count**: Minimum 20 high-quality images

#### 8.2 Stereo Calibration (RGB-Thermal)

**Equipment Needed:**
- Thermal-contrast checkerboard (heated/cooled squares)
- Stable positioning for both cameras
- Controlled temperature environment

**Procedure:**
1. Navigate to Calibration → Stereo Calibration
2. Ensure both RGB and thermal cameras active
3. Hold thermal-contrast pattern visible to both cameras
4. Capture 15-20 image pairs with pattern in different positions
5. Review calibration results and stereo reprojection error

**Quality Targets:**
- **Stereo RMS Error**: <1.0 pixels
- **Translation Accuracy**: <5mm for research applications
- **Rotation Accuracy**: <2 degrees

### 9. System Synchronization

#### 9.1 Clock Synchronization

**Automatic Synchronization:**
1. Connect to PC controller
2. Navigate to Settings → Sync Settings
3. Tap "Synchronize Clock"
4. Wait for "Sync Complete" confirmation

**Manual Verification:**
- Check timestamp alignment between devices
- Verify microsecond precision if required
- Test synchronization with known events

#### 9.2 Sensor Timing Calibration

**Latency Measurement:**
- **Camera Latency**: ~33ms (at 30fps)
- **Thermal Latency**: ~100ms (hardware dependent)
- **Shimmer Latency**: ~10ms (Bluetooth dependent)
- **Network Latency**: Variable (measure before each session)

---

## Data Management

### 10. Session Data Organization

#### 10.1 File Structure

Each recording session creates a structured data directory:

```
Session_YYYYMMDD_HHMMSS/
├── metadata.json                 # Session parameters and timing
├── camera/
│   ├── video.mp4                # Primary video recording
│   ├── raw_images/              # DNG format images
│   └── camera_params.json       # Camera settings used
├── thermal/
│   ├── thermal_data.bin         # Binary thermal measurements
│   ├── thermal_preview.mp4      # Visual thermal video
│   └── temperature_log.csv      # Point temperature readings
├── shimmer/
│   ├── gsr_data.csv            # GSR measurements with timestamps
│   ├── sensor_config.json      # Shimmer configuration
│   └── quality_metrics.json    # Signal quality assessment
└── logs/
    ├── session.log             # Event log with timestamps
    ├── errors.log              # Error conditions
    └── sync_data.json          # Synchronization information
```

#### 10.2 Data Export Functions

**Export Options:**
1. **Individual Sessions**: Export specific session data
2. **Batch Export**: Export multiple sessions
3. **Compressed Archive**: ZIP file for easy transfer
4. **Cloud Upload**: Direct upload to research storage

**Export Formats:**
- **Original Data**: Preserves all original file formats
- **Analysis-Ready**: Converted to common research formats
- **Metadata Only**: Session information without raw data
- **Preview Package**: Reduced-size data for quick review

### 11. Quality Assurance

#### 11.1 Data Integrity Verification

**Automatic Checks:**
- File size validation
- Timestamp consistency verification
- Metadata completeness check
- Synchronization accuracy assessment

**Manual Verification:**
- Visual inspection of video quality
- Thermal data range checking
- GSR signal quality review
- Session duration confirmation

#### 11.2 Error Detection and Recovery

**Common Issues:**
- **Storage Full**: Automatic cleanup and warning
- **Sensor Disconnection**: Automatic reconnection attempts
- **Network Interruption**: Local buffering and retry logic
- **Low Battery**: Power management and early warning

**Recovery Procedures:**
- **Partial Sessions**: Salvage available data
- **Corrupted Files**: Attempt data recovery
- **Missing Synchronization**: Estimate timing from metadata
- **Sensor Failures**: Mark affected data segments

---

## Troubleshooting

### 12. Common Issues and Solutions

#### 12.1 Connection Problems

**PC Communication Issues:**
- **Symptom**: "PC Controller Not Found"
- **Solution**: 
  1. Verify PC controller is running
  2. Check IP address and port configuration
  3. Test network connectivity with ping
  4. Restart networking components

**Sensor Connection Issues:**
- **Thermal Camera**: Check USB connection, grant permissions
- **Shimmer Sensor**: Verify Bluetooth pairing, check battery
- **General**: Restart app, reboot device if persistent

#### 12.2 Recording Problems

**Poor Video Quality:**
- Check lighting conditions
- Clean camera lens
- Verify stabilization settings
- Adjust focus and exposure

**Thermal Data Issues:**
- Verify thermal camera calibration
- Check temperature range settings
- Ensure proper thermal contrast
- Monitor for thermal drift

**GSR Signal Problems:**
- Check electrode contact quality
- Verify proper skin preparation
- Monitor for motion artifacts
- Adjust sampling rate if needed

#### 12.3 Performance Issues

**Slow Response:**
- Close unnecessary background apps
- Clear app cache and temporary files
- Restart device if memory is low
- Check available storage space

**Battery Drain:**
- Enable power saving mode
- Reduce screen brightness
- Disable unnecessary sensors during breaks
- Use external power source for long sessions

### 13. Advanced Features

#### 13.1 Multi-Device Coordination

**Setup Multiple Devices:**
1. Install app on all Android devices
2. Configure each with unique device ID
3. Connect all devices to same PC controller
4. Test synchronization across devices

**Coordinated Recording:**
- All devices start/stop simultaneously
- Shared session metadata
- Synchronized timestamps
- Combined data export

#### 13.2 Custom Configurations

**Research-Specific Settings:**
- Custom recording parameters for specific experiments
- Specialized calibration procedures
- Modified data export formats
- Integration with analysis software

**Protocol Integration:**
- Event marker insertion
- Stimulus timing synchronization
- Participant instruction display
- Automated session sequences

---

## Best Practices

### 14. Research Guidelines

#### 14.1 Data Collection Standards

**Preparation:**
- Always perform calibration before each session
- Verify all sensors before participant arrival
- Test complete workflow with pilot recordings
- Document all configuration parameters

**During Recording:**
- Monitor data quality continuously
- Maintain consistent environmental conditions
- Follow standardized protocols
- Document any unusual events

**Post-Recording:**
- Verify data integrity immediately
- Export data to secure storage
- Clean up temporary files
- Update session logs

#### 14.2 Quality Assurance

**Regular Maintenance:**
- Weekly calibration verification
- Monthly sensor performance testing
- Quarterly system updates
- Annual hardware inspection

**Documentation:**
- Maintain detailed session logs
- Record all configuration changes
- Document troubleshooting steps
- Keep calibration history

---

## Support and Resources

### 15. Getting Help

#### Technical Support
- **Documentation**: Complete technical documentation available
- **Troubleshooting Guide**: Common issues and solutions
- **FAQ**: Frequently asked questions and answers
- **Community Forum**: User discussion and experience sharing

#### Training Resources
- **Video Tutorials**: Step-by-step operational procedures
- **Training Sessions**: Hands-on training for new users
- **Best Practices Guide**: Research-specific recommendations
- **Case Studies**: Example research applications

---

This user guide provides comprehensive instructions for researchers using the Android Mobile Data Collection Node. For technical details and advanced configuration options, refer to the complete technical documentation.