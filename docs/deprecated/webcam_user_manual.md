# Webcam Features User Manual

## Multi-Sensor Recording System - PC Webcam Integration

**Version:** 3.3  
**Date:** 2025-07-29  
**Milestone:** 3.3 - Webcam Capture Integration (PC Recording)

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Webcam Configuration](#webcam-configuration)
4. [Recording Sessions](#recording-sessions)
5. [Preview and Monitoring](#preview-and-monitoring)
6. [Advanced Features](#advanced-features)
7. [File Management](#file-management)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The PC Webcam Integration feature allows you to record video from your computer's webcam alongside Android device recordings, creating synchronized multi-camera recording sessions. This feature is designed for researchers and professionals who need coordinated video capture from multiple sources.

### Key Features

- **Multi-Camera Support**: Automatically detect and select from multiple connected cameras
- **Synchronized Recording**: Start/stop webcam recording in sync with Android devices
- **Live Preview**: Real-time webcam feed display in the application interface
- **Session Management**: Organized recording sessions with automatic file naming and folder structure
- **Advanced Configuration**: Customizable recording parameters (resolution, frame rate, codec)
- **Error Recovery**: Automatic handling of camera conflicts and connection issues

---

## Getting Started

### System Requirements

- **Operating System**: Windows 10 or later
- **Hardware**: Built-in webcam or USB camera
- **Software**: Python 3.7+, OpenCV, PyQt5
- **Storage**: Sufficient disk space for video recordings

### Initial Setup

1. **Launch the Application**
   - Run the Multi-Sensor Recording System Controller
   - The application will automatically detect available cameras

2. **Verify Webcam Access**
   - Check the "PC Webcam" tab in the preview panel
   - You should see a live feed from your default camera
   - If no feed appears, see the [Troubleshooting](#troubleshooting) section

3. **Configure Settings** (Optional)
   - Access webcam settings through the Tools menu
   - Adjust recording quality and preview settings as needed

---

## Webcam Configuration

### Automatic Configuration

The system automatically configures optimal settings based on your hardware:

- **Camera Detection**: Scans for available cameras (indices 0-9)
- **Resolution Selection**: Chooses the best supported resolution
- **Codec Selection**: Tests and selects working video codecs
- **Fallback Options**: Configures backup codecs for reliability

### Manual Configuration

#### Camera Selection

If you have multiple cameras:

1. Go to **Tools > Webcam Settings**
2. Select your preferred camera from the dropdown
3. Click **Apply** to save changes

#### Recording Parameters

Configure recording quality:

- **Resolution**: Choose from available options (480p, 720p, 1080p, 4K)
- **Frame Rate**: Set recording FPS (15, 24, 30, 60)
- **Codec**: Select video codec (MP4V, XVID, MJPG, H264)
- **Quality**: Adjust compression quality (0-100%)

#### Preview Settings

Customize the live preview:

- **Preview Size**: Set maximum preview dimensions
- **Preview FPS**: Adjust preview frame rate for performance
- **Scaling**: Enable/disable automatic scaling
- **Aspect Ratio**: Maintain original proportions

### Configuration File

Settings are automatically saved to `webcam_config.json`:

```json
{
  "camera_index": 0,
  "camera_name": "Built-in Camera (HD 1280x720)",
  "recording": {
    "codec": "mp4v",
    "resolution": [1280, 720],
    "fps": 30,
    "quality": 80,
    "file_format": "mp4"
  },
  "preview": {
    "max_width": 640,
    "max_height": 480,
    "fps": 30,
    "enable_scaling": true,
    "maintain_aspect_ratio": true
  }
}
```

---

## Recording Sessions

### Starting a Recording Session

1. **Connect Devices** (if using Android devices)
   - Click **Connect** to start the device server
   - Wait for Android devices to connect

2. **Start Recording**
   - Click **Start Session** in the toolbar
   - The system will:
     - Create a new session folder with timestamp
     - Start webcam recording
     - Send start commands to connected devices
     - Display recording status

3. **Monitor Recording**
   - Watch the live preview to ensure proper framing
   - Check the status bar for recording confirmation
   - Observe the log panel for detailed information

### Stopping a Recording Session

1. **End Recording**
   - Click **Stop** in the toolbar
   - The system will:
     - Stop webcam recording
     - Send stop commands to devices
     - Finalize video files
     - Generate session metadata

2. **Verify Results**
   - Check the session folder for recorded files
   - Review the session log for any issues
   - Validate video file integrity

### Session Organization

Each recording session creates a structured folder:

```
recordings/
└── session_20250729_143022/
    ├── session_metadata.json
    ├── webcam_session_20250729_143022_143022.mp4
    ├── phone1_video.mp4 (if connected)
    ├── phone2_video.mp4 (if connected)
    └── session_log.txt
```

---

## Preview and Monitoring

### Live Preview

The **PC Webcam** tab shows real-time video feed:

- **Full-Screen Preview**: Click the preview to expand
- **Aspect Ratio**: Automatically maintained
- **Performance**: Optimized for smooth playback
- **Status Indicators**: Shows recording state

### Status Information

Monitor recording status through:

- **Status Bar**: Current operation and device count
- **Log Panel**: Detailed event logging
- **Preview Tabs**: Visual confirmation of active feeds

### Performance Monitoring

The system tracks:

- **Frame Rate**: Actual vs. target FPS
- **CPU Usage**: Processing load
- **Memory Usage**: RAM consumption
- **Disk Space**: Available storage

---

## Advanced Features

### Multiple Camera Support

Use multiple cameras simultaneously:

1. **Detection**: System automatically finds all cameras
2. **Selection**: Choose primary camera for recording
3. **Switching**: Change cameras without restarting
4. **Backup**: Automatic fallback to alternative cameras

### Codec Fallback System

Ensures recording reliability:

- **Primary Codec**: Preferred encoding format
- **Fallback Chain**: Alternative codecs if primary fails
- **Automatic Testing**: Validates codec availability
- **Error Recovery**: Switches codecs on encoding failure

### Error Recovery

Automatic handling of common issues:

- **Camera Conflicts**: Resolves resource access problems
- **Network Issues**: Recovers from device communication failures
- **Codec Problems**: Switches to working alternatives
- **Hardware Failures**: Finds alternative cameras

### Session Synchronization

Precise timing coordination:

- **Unified Start**: All devices begin recording together
- **Timestamp Logging**: Records exact start/stop times
- **Duration Tracking**: Calculates session length
- **Metadata Generation**: Creates detailed session information

---

## File Management

### Output Formats

Supported video formats:

- **MP4**: Default format with H.264/MP4V codec
- **AVI**: Alternative format with XVID/MJPG codec
- **Quality Options**: Configurable compression levels

### File Naming

Automatic naming convention:

```
webcam_[session_id]_[timestamp].mp4
```

Example: `webcam_session_20250729_143022_143022.mp4`

### Storage Management

- **Session Folders**: Organized by date and time
- **Metadata Files**: JSON format for easy parsing
- **Log Files**: Text format for troubleshooting
- **Cleanup Tools**: Remove old sessions automatically

### File Validation

Automatic quality checks:

- **Playback Testing**: Verifies video files are readable
- **Frame Validation**: Checks for corruption
- **Duration Verification**: Confirms expected length
- **Codec Compatibility**: Tests with standard players

---

## Troubleshooting

### Common Issues

#### No Webcam Preview

**Symptoms**: Black screen in PC Webcam tab

**Solutions**:
1. Check camera connection (USB cameras)
2. Verify camera permissions in Windows
3. Close other applications using the camera
4. Try different camera index in settings
5. Restart the application

#### Recording Fails to Start

**Symptoms**: Error message when starting session

**Solutions**:
1. Check available disk space
2. Verify camera is not in use by another app
3. Try different video codec in settings
4. Check camera hardware connection
5. Review log panel for specific errors

#### Poor Video Quality

**Symptoms**: Blurry or pixelated recordings

**Solutions**:
1. Increase recording resolution in settings
2. Adjust quality percentage (higher = better)
3. Check camera focus and lighting
4. Try different codec (H264 for better compression)
5. Ensure sufficient system resources

#### Synchronization Issues

**Symptoms**: Webcam and device recordings don't align

**Solutions**:
1. Check network connection to devices
2. Verify device clocks are synchronized
3. Use sync markers (clap or flash) for alignment
4. Review session logs for timing information
5. Consider network latency in analysis

### Error Messages

#### "Camera already in use"

**Cause**: Another application is accessing the camera

**Solution**: 
1. Close other camera applications (Skype, Teams, etc.)
2. Use Task Manager to end camera processes
3. Try camera recovery in Tools menu
4. Restart the application

#### "Codec not available"

**Cause**: Selected video codec is not supported

**Solution**:
1. System will automatically try fallback codecs
2. Manually select different codec in settings
3. Install additional codec packs if needed
4. Use MJPG codec as universal fallback

#### "Insufficient disk space"

**Cause**: Not enough storage for recording

**Solution**:
1. Free up disk space
2. Change recording location to different drive
3. Reduce recording quality/resolution
4. Clean up old session folders

### Performance Optimization

#### Improve Frame Rate

1. **Lower Preview Resolution**: Reduce preview size
2. **Close Background Apps**: Free up system resources
3. **USB 3.0 Connection**: Use faster USB ports for cameras
4. **Reduce Recording Resolution**: Lower quality for better performance

#### Reduce CPU Usage

1. **Limit Preview FPS**: Set lower preview frame rate
2. **Disable Scaling**: Turn off automatic preview scaling
3. **Use Hardware Acceleration**: Enable if available
4. **Optimize Codec**: Use hardware-accelerated codecs

### Getting Help

#### Log Information

Always check the log panel for detailed error information:

1. **Enable Log Panel**: View > Show Log
2. **Copy Log Messages**: Right-click to copy
3. **Save Log Files**: Logs are saved in session folders

#### Support Resources

- **Documentation**: Check troubleshooting guide
- **Configuration**: Review webcam configuration guide
- **Testing**: Use built-in test framework
- **Community**: Consult user forums and documentation

---

## Best Practices

### Before Recording

1. **Test Setup**: Verify all cameras work properly
2. **Check Storage**: Ensure sufficient disk space
3. **Close Applications**: Exit other camera-using programs
4. **Verify Settings**: Confirm recording parameters
5. **Test Sync**: Do a short test recording

### During Recording

1. **Monitor Status**: Watch for error messages
2. **Avoid Interruption**: Don't disconnect cameras
3. **Maintain Power**: Ensure stable power supply
4. **Check Performance**: Monitor system resources

### After Recording

1. **Verify Files**: Check all recordings completed
2. **Test Playback**: Ensure videos are playable
3. **Backup Data**: Copy important recordings
4. **Clean Workspace**: Remove temporary files
5. **Review Logs**: Check for any issues

---

## Appendix

### Supported Cameras

- **Built-in Webcams**: Most laptop integrated cameras
- **USB Cameras**: Standard UVC-compatible devices
- **Professional Cameras**: DSLR/mirrorless with USB output
- **Multiple Cameras**: Up to 10 simultaneous cameras

### Supported Codecs

- **MP4V**: MPEG-4 Part 2 (recommended)
- **H264**: Advanced Video Coding (best compression)
- **XVID**: MPEG-4 Part 2 variant (widely compatible)
- **MJPG**: Motion JPEG (universal compatibility)

### File Format Specifications

- **Container**: MP4 or AVI
- **Video Codec**: As selected in configuration
- **Audio**: Not currently supported
- **Metadata**: Embedded timing information

---

*For additional support, please refer to the Troubleshooting Guide and Configuration Guide documents.*
