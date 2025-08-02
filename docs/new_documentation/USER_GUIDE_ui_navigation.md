# User Guide: UI Navigation and Interface

## Table of Contents

- [Practical Guide for Using the Multi-Sensor Recording System Interface](#practical-guide-for-using-the-multi-sensor-recording-system-interface)
  - [Overview](#overview)
  - [Pre-flight Checklist](#pre-flight-checklist)
  - [Interface Modes](#interface-modes)
  - [Navigation Mode Guide](#navigation-mode-guide)
  - [Status Indicators Guide](#status-indicators-guide)

## Practical Guide for Using the Multi-Sensor Recording System Interface

### Overview

This guide provides step-by-step instructions for using the Multi-Sensor Recording System's user interface. The application features two main interface modes: **Direct Mode** (MainActivity) for immediate recording access and **Navigation Mode** (MainNavigationActivity) for organized feature access.

### Pre-flight Checklist

Before using the application, ensure the following:

- [ ] **Device Requirements**: Android 8.0+ (API level 26) device
- [ ] **Permissions**: Camera, microphone, storage, and location permissions granted
- [ ] **Hardware**: USB-C port for thermal camera connection
- [ ] **Storage**: Sufficient storage space for recordings (minimum 2GB recommended)
- [ ] **Battery**: Device charged above 20% for reliable operation
- [ ] **Network**: Wi-Fi connection for PC streaming (optional)
- [ ] **Thermal Camera**: TOPDON TC001 or compatible device
- [ ] **Shimmer Device**: Shimmer3 GSR+ or compatible sensor
- [ ] **Calibration Target**: Thermal-contrast checkerboard pattern

### Interface Modes

#### 1. Direct Mode (MainActivity)

**When to Use**: Quick recording sessions, immediate camera access, single-operator use

**Features**:
- Immediate access to recording controls
- Real-time camera preview
- Direct device status indicators
- Quick calibration access

**How to Access**:
1. Launch the app from the home screen
2. The app opens directly in Direct Mode by default

#### 2. Navigation Mode (MainNavigationActivity)

**When to Use**: Organized workflows, multi-user environments, feature exploration

**Features**:
- Tab-based navigation
- Organized feature sections
- Comprehensive device management
- Advanced settings access

**How to Access**:
1. From Direct Mode, tap the **Navigation Mode** button
2. Or launch via the "Navigation" shortcut (if configured)

### Navigation Mode Guide

#### Tab Structure

The Navigation Mode organizes features into four main tabs:

```
📱 Recording  |  🔗 Devices  |  📐 Calibration  |  📁 Files
```

#### Tab 1: Recording

**Purpose**: Primary recording controls and camera management

**Step-by-Step Recording Process**:

1. **Navigate to Recording Tab**
   - Tap the "Recording" tab (leftmost tab)
   - Wait for camera initialization

2. **Verify System Status**
   - Check status indicator at the top
   - Ensure it shows "System ready - Ready to record"
   - If not ready, address any displayed issues

3. **Start Recording**
   - Tap the **Start Recording** button
   - Observe the red recording indicator
   - Status changes to "Recording in progress..."

4. **Monitor Recording**
   - Watch the streaming indicator (green when active)
   - Monitor battery level
   - Check connection status indicators

5. **Stop Recording**
   - Tap the **Stop Recording** button
   - Wait for "Recording stopped" confirmation
   - Session automatically saved to Files

**Visual Indicators**:
- 🔴 **Recording Indicator**: Red when recording active
- 🟢 **Streaming Indicator**: Green when data streaming
- 🔋 **Battery Level**: Color-coded (Green > 50%, Yellow > 20%, Red < 20%)
- 📶 **Connection Status**: Individual indicators for PC, Shimmer, Thermal

#### Tab 2: Devices

**Purpose**: Device management and connection status

**Device Connection Guide**:

1. **Check Current Connections**
   - View connection status for all devices
   - PC Connection: Network streaming status
   - Shimmer GSR: Bluetooth sensor status
   - Thermal Camera: USB connection status

2. **Connect Shimmer Device**
   - Ensure Shimmer device is powered on
   - Tap **Connect Shimmer** button
   - Select device from Bluetooth scan results
   - Choose connection type (BT Classic or BLE)
   - Wait for "Connected" confirmation

3. **Connect Thermal Camera**
   - Connect TOPDON thermal camera via USB-C
   - Grant USB permission when prompted
   - Verify "Thermal: Connected" status

4. **Configure PC Streaming**
   - Ensure device and PC are on same network
   - Configure network settings in Settings menu
   - Monitor PC connection status

**Troubleshooting Device Issues**:
- **Shimmer Not Found**: Check Bluetooth enabled, device powered
- **Thermal Camera Not Detected**: Try different USB cable, check USB permissions
- **PC Connection Failed**: Verify network settings, firewall configuration

#### Tab 3: Calibration

**Purpose**: Camera calibration and synchronization

**Calibration Procedure**:

1. **Prepare Calibration Setup**
   - Position thermal-contrast checkerboard in view
   - Ensure adequate lighting
   - Clear camera lens and thermal sensor

2. **Start Calibration**
   - Tap **Run Calibration** button
   - Follow on-screen guidance
   - Position device at multiple angles as directed

3. **Capture Calibration Images**
   - Tap **Capture** for each position
   - Wait for visual and audio feedback:
     - 📸 Screen flash effect
     - 🔊 Camera shutter sound
     - ✅ "Photo captured!" message

4. **Complete Multi-Angle Calibration**
   - Move device to next position as guided
   - Repeat capture process
   - Complete all required angles (typically 5-8 positions)

5. **Verify Calibration Results**
   - Review calibration completion message
   - Check calibration ID for reference
   - Verify improved recording quality

**Calibration Tips**:
- Hold device steady during capture
- Ensure checkerboard fills 60-80% of camera view
- Avoid shadows or reflections on checkerboard
- Complete all angles in single session

#### Tab 4: Files

**Purpose**: File management, data export, and session review

**File Management Workflow**:

1. **View Recording Sessions**
   - Browse completed recording sessions
   - View session details (duration, file size, timestamp)
   - Check data integrity status

2. **Export Data**
   - Select session(s) for export
   - Choose export format (ZIP, individual files)
   - Confirm export location
   - Monitor export progress

3. **Session Management**
   - Delete old sessions to free space
   - Rename sessions for organization
   - Share sessions via standard Android sharing

**File Organization**:
```
📁 Multi-Sensor Recordings/
├── 📁 Sessions/
│   ├── 📁 Session_20240131_143022/
│   │   ├── 🎥 visible_camera.mp4
│   │   ├── 🌡️ thermal_data.bin
│   │   ├── 📊 shimmer_gsr.csv
│   │   └── 📋 session_metadata.json
│   └── 📁 Session_20240131_151045/
├── 📁 Calibration/
│   └── 📐 calibration_data.json
└── 📁 Exports/
    └── 📦 export_20240131.zip
```

### Status Indicators Guide

#### Connection Status Indicators

**PC Connection**:
- 🟢 **Green**: Connected and streaming
- 🔴 **Red**: Disconnected or network issue
- 🟡 **Yellow**: Connecting or limited connection

**Shimmer GSR Sensor**:
- 🟢 **Green**: Connected and receiving data
- 🔴 **Red**: Disconnected or pairing failed
- 🟡 **Yellow**: Connecting or pairing in progress

**Thermal Camera**:
- 🟢 **Green**: Connected and operational
- 🔴 **Red**: Disconnected or not detected
- 🟡 **Yellow**: Connected but initializing

#### System Status Messages

| Status Message | Meaning | Action Required |
|---------------|---------|-----------------|
| "System ready - Ready to record" | All systems operational | None - ready to start |
| "Requesting permissions..." | Permission check in progress | Wait or grant permissions |
| "Permissions required - Check Settings" | Missing permissions | Enable in Android Settings |
| "Recording in progress..." | Active recording session | Monitor or stop when complete |
| "Calibration in progress..." | Calibration procedure active | Follow calibration guidance |
| "Device initializing..." | Hardware setup in progress | Wait for completion |

### Advanced Navigation Features

#### Quick Actions

**Long Press Actions**:
- **Recording Button**: Quick session settings
- **Device Status**: Detailed connection info
- **Battery Indicator**: Power management options

**Gesture Navigation**:
- **Swipe Left/Right**: Switch between tabs quickly
- **Pull Down**: Refresh device status
- **Double Tap Status**: Show detailed system info

#### Settings and Configuration

**Accessing Advanced Settings**:
1. Tap the **Menu** button (three dots)
2. Select **Settings** from dropdown
3. Configure preferences:
   - Recording quality
   - Network parameters
   - Device timeouts
   - File naming conventions

**Network Configuration**:
1. Menu → **Network Config**
2. Configure streaming settings:
   - IP address and port
   - Protocol selection
   - Bandwidth limits
   - Encryption settings

**Shimmer Configuration**:
1. Menu → **Shimmer Config**
2. Adjust sensor parameters:
   - Sampling rate
   - Sensor selection
   - Data format
   - Connection preferences

### Troubleshooting Common Issues

#### UI Navigation Issues

**Tabs Not Responding**:
1. Check if recording is active (stops some navigation)
2. Restart app if tabs remain unresponsive
3. Clear app cache in Android Settings

**Permission Requests Loop**:
1. Tap **Settings** → **App Permissions**
2. Manually enable all required permissions
3. Return to app and tap **Request Permissions**

**Status Indicators Not Updating**:
1. Pull down to refresh status
2. Check device connections
3. Restart app if issues persist

#### Recording Workflow Issues

**Cannot Start Recording**:
- Verify all devices connected
- Check available storage space
- Ensure permissions granted
- Try calibration if camera issues

**Recording Stops Unexpectedly**:
- Check battery level (>20% recommended)
- Monitor storage space
- Verify device connections stable

**Poor Recording Quality**:
- Run calibration procedure
- Check lighting conditions
- Clean camera lenses
- Verify thermal camera positioning

### Accessibility Features

#### Visual Accessibility

**High Contrast Mode**:
1. Settings → **Accessibility**
2. Enable **High Contrast Mode**
3. Status indicators use brighter colors

**Large Text Support**:
- Respects Android system text size settings
- Compatible with TalkBack screen reader

#### Motor Accessibility

**Touch Assistance**:
- Larger touch targets for critical buttons
- Reduced precision requirements for gestures
- Voice commands for basic operations (if enabled)

### Best Practices

#### Efficient Workflow

1. **Pre-Session Setup**:
   - Check all device connections
   - Verify calibration status
   - Ensure adequate storage and battery

2. **During Recording**:
   - Monitor status indicators
   - Avoid unnecessary tab switching
   - Keep device stable for optimal quality

3. **Post-Session**:
   - Review recording immediately
   - Export or transfer data promptly
   - Clean up old sessions regularly

#### Battery Optimization

- Use Navigation Mode for extended sessions
- Connect to power during long recordings
- Monitor thermal camera power draw
- Close other apps to preserve battery

#### Data Management

- Regular exports to prevent data loss
- Organize sessions with descriptive names
- Monitor storage usage in Files tab
- Set up automatic cleanup policies

### Getting Help

#### In-App Help

**About Dialog**:
- Menu → **About**
- View app version and build information
- Access support contact information

**Status Information**:
- Double-tap status text for detailed system info
- Check device-specific status in Devices tab
- Review session details in Files tab

#### External Resources

- **Documentation**: Complete technical documentation
- **Support**: Contact support team for technical issues
- **Community**: User forums and discussion groups

### Conclusion

The Multi-Sensor Recording System provides a comprehensive and user-friendly interface for multi-modal data collection. By following this guide and understanding the navigation structure, users can efficiently conduct recording sessions, manage devices, and organize data.

The dual-mode interface accommodates both quick-access scenarios and comprehensive workflow requirements, ensuring optimal user experience across different use cases and user expertise levels.