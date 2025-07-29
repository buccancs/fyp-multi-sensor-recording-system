# Webcam Troubleshooting Guide

## Multi-Sensor Recording System - PC Webcam Integration

**Version:** 3.3  
**Date:** 2025-07-29  
**Milestone:** 3.3 - Webcam Capture Integration (PC Recording)

---

## Table of Contents

1. [Quick Diagnostic Checklist](#quick-diagnostic-checklist)
2. [Camera Detection Issues](#camera-detection-issues)
3. [Recording Problems](#recording-problems)
4. [Performance Issues](#performance-issues)
5. [Synchronization Problems](#synchronization-problems)
6. [Error Message Reference](#error-message-reference)
7. [Advanced Diagnostics](#advanced-diagnostics)
8. [System-Specific Issues](#system-specific-issues)
9. [Recovery Procedures](#recovery-procedures)
10. [Support and Escalation](#support-and-escalation)

---

## Quick Diagnostic Checklist

### Before You Start

Run through this checklist to identify the most common issues:

- [ ] **Camera Connection**: Is the camera physically connected and powered?
- [ ] **Application Permissions**: Does the app have camera access permissions?
- [ ] **Other Applications**: Are other programs using the camera (Skype, Teams, etc.)?
- [ ] **Driver Status**: Are camera drivers installed and up to date?
- [ ] **System Resources**: Is there sufficient CPU, memory, and disk space?
- [ ] **Network Connection**: Are Android devices properly connected (if applicable)?

### Quick Tests

1. **Camera Test**: Open Windows Camera app to verify basic functionality
2. **Application Test**: Launch the Multi-Sensor Recording System
3. **Preview Test**: Check if webcam preview appears in PC Webcam tab
4. **Recording Test**: Try a short 5-second recording
5. **File Test**: Verify the recorded file plays correctly

---

## Camera Detection Issues

### Problem: No Cameras Detected

#### Symptoms
- Empty camera list in settings
- "No camera available" message
- Black screen in preview panel

#### Diagnostic Steps

1. **Check Physical Connection**
   ```
   - USB cameras: Try different USB ports
   - Built-in cameras: Check device manager
   - Verify power LED (if present) is on
   ```

2. **Verify in Device Manager**
   ```
   1. Press Win + X, select Device Manager
   2. Expand "Cameras" or "Imaging devices"
   3. Look for your camera device
   4. Check for warning icons (yellow triangle)
   ```

3. **Test with Windows Camera App**
   ```
   1. Open Windows Camera app
   2. If it works here but not in our app, it's a software issue
   3. If it doesn't work here, it's a hardware/driver issue
   ```

#### Solutions

**Hardware Issues:**
- Try different USB port (preferably USB 3.0)
- Test camera on another computer
- Check cable integrity for USB cameras
- Restart computer to reset USB controllers

**Driver Issues:**
- Update camera drivers through Device Manager
- Download latest drivers from manufacturer
- Uninstall and reinstall camera drivers
- Run Windows Update for generic drivers

**Permission Issues:**
- Check Windows Privacy Settings:
  ```
  Settings > Privacy > Camera
  - Enable "Allow apps to access your camera"
  - Enable for desktop apps
  ```

### Problem: Camera Detected but Not Working

#### Symptoms
- Camera appears in device list
- Preview shows black screen or error
- "Camera cannot be opened" error

#### Diagnostic Steps

1. **Check Camera Index**
   ```
   - Try different camera indices (0, 1, 2, etc.)
   - Some systems have virtual cameras that occupy indices
   ```

2. **Test Camera Properties**
   ```
   - Check supported resolutions
   - Verify frame rate capabilities
   - Test different video formats
   ```

3. **Resource Conflict Check**
   ```
   - Close all other camera applications
   - Check Task Manager for camera processes
   - Look for background apps using camera
   ```

#### Solutions

**Index Issues:**
- Use automatic camera detection in settings
- Manually try different camera indices
- Check for virtual cameras (OBS, ManyCam, etc.)

**Resource Conflicts:**
- Close competing applications:
  ```
  - Skype, Microsoft Teams, Zoom
  - OBS Studio, XSplit
  - Browser tabs with camera access
  - Windows Camera app
  ```

**Format Issues:**
- Try different resolution settings
- Use MJPG codec for compatibility
- Reduce frame rate requirements

---

## Recording Problems

### Problem: Recording Fails to Start

#### Symptoms
- Error message when clicking "Start Session"
- Recording button remains inactive
- Status shows "Failed to start recording"

#### Diagnostic Steps

1. **Check Disk Space**
   ```
   - Verify sufficient free space (at least 1GB)
   - Check recording directory permissions
   - Test writing to recording folder
   ```

2. **Verify Camera Access**
   ```
   - Ensure preview is working
   - Check camera is not locked by another process
   - Verify camera supports recording resolution
   ```

3. **Test Codec Availability**
   ```
   - Try different video codecs
   - Check codec installation
   - Test with MJPG (most compatible)
   ```

#### Solutions

**Storage Issues:**
- Free up disk space
- Change recording directory to different drive
- Check folder permissions (write access required)

**Camera Issues:**
- Restart application to release camera
- Use camera recovery function in Tools menu
- Try lower resolution/frame rate

**Codec Issues:**
- System automatically tries fallback codecs
- Manually select MJPG codec
- Install additional codec packs if needed

### Problem: Recording Stops Unexpectedly

#### Symptoms
- Recording starts but stops after few seconds
- Incomplete video files
- "Recording interrupted" error

#### Diagnostic Steps

1. **Check System Resources**
   ```
   - Monitor CPU usage during recording
   - Check available RAM
   - Verify disk write speed
   ```

2. **Review Error Logs**
   ```
   - Check application log panel
   - Look for specific error messages
   - Note timing of interruption
   ```

3. **Test Recording Duration**
   ```
   - Try shorter recordings (10 seconds)
   - Gradually increase duration
   - Identify failure threshold
   ```

#### Solutions

**Performance Issues:**
- Reduce recording resolution
- Lower frame rate
- Close background applications
- Use faster storage device

**Hardware Issues:**
- Check USB connection stability
- Use powered USB hub for external cameras
- Verify camera doesn't overheat

**Software Issues:**
- Update application to latest version
- Restart application between recordings
- Check for Windows updates

---

## Performance Issues

### Problem: Low Frame Rate

#### Symptoms
- Choppy preview or recording
- Frame rate below expected value
- Performance warnings in logs

#### Diagnostic Steps

1. **Monitor System Performance**
   ```
   - Check CPU usage (should be < 80%)
   - Monitor memory consumption
   - Verify disk I/O performance
   ```

2. **Test Different Settings**
   ```
   - Try lower resolution
   - Reduce preview frame rate
   - Test different codecs
   ```

3. **Check Camera Capabilities**
   ```
   - Verify camera supports target frame rate
   - Test with camera manufacturer software
   - Check USB bandwidth limitations
   ```

#### Solutions

**System Optimization:**
- Close unnecessary applications
- Disable Windows visual effects
- Set application to high priority
- Use performance power plan

**Recording Optimization:**
- Reduce recording resolution (1080p → 720p)
- Lower frame rate (30fps → 24fps)
- Use hardware-accelerated codec
- Enable preview scaling

**Hardware Upgrades:**
- Use USB 3.0 ports for cameras
- Add more RAM if usage is high
- Use SSD for recording storage
- Upgrade to faster CPU

### Problem: High CPU Usage

#### Symptoms
- CPU usage > 80% during recording
- System becomes unresponsive
- Fan noise increases significantly

#### Diagnostic Steps

1. **Identify CPU Bottlenecks**
   ```
   - Use Task Manager to monitor processes
   - Check which component uses most CPU
   - Monitor during different operations
   ```

2. **Test Optimization Settings**
   ```
   - Disable preview during recording
   - Reduce preview resolution
   - Try different codecs
   ```

#### Solutions

**Immediate Fixes:**
- Reduce preview frame rate to 15fps
- Lower preview resolution to 320x240
- Disable preview scaling
- Use MJPG codec (less CPU intensive)

**Long-term Solutions:**
- Upgrade hardware
- Use dedicated recording computer
- Implement hardware acceleration
- Optimize application settings

---

## Synchronization Problems

### Problem: Webcam and Device Recordings Not Aligned

#### Symptoms
- Time offset between webcam and device videos
- Inconsistent start times
- Sync markers don't align

#### Diagnostic Steps

1. **Check Network Latency**
   ```
   - Ping Android devices
   - Monitor network connection quality
   - Test with devices on same network
   ```

2. **Verify Time Synchronization**
   ```
   - Check PC and device clocks
   - Ensure NTP synchronization
   - Note time zone differences
   ```

3. **Test Sync Accuracy**
   ```
   - Use visual sync markers (clap, flash)
   - Record sync test with all devices
   - Measure timing differences
   ```

#### Solutions

**Network Optimization:**
- Use wired connection for PC
- Ensure devices on same WiFi network
- Reduce network congestion
- Use 5GHz WiFi band

**Time Synchronization:**
- Enable automatic time sync on all devices
- Use NTP server for precise timing
- Account for network latency in analysis

**Sync Improvement:**
- Use countdown before recording
- Implement sync signals
- Add timing markers to recordings
- Use post-processing alignment

### Problem: Commands Not Reaching Devices

#### Symptoms
- Devices don't start/stop recording
- "Device not responding" errors
- Inconsistent device behavior

#### Diagnostic Steps

1. **Check Device Connections**
   ```
   - Verify devices appear in device list
   - Test ping to device IP addresses
   - Check device status indicators
   ```

2. **Test Command Delivery**
   ```
   - Send individual commands to devices
   - Monitor command acknowledgments
   - Check for timeout errors
   ```

#### Solutions

**Connection Issues:**
- Restart device server
- Reconnect devices manually
- Check firewall settings
- Use USB tethering as backup

**Command Issues:**
- Increase command timeout values
- Implement retry mechanisms
- Use device-specific command formats
- Check device app status

---

## Error Message Reference

### Camera Errors

#### "Camera 0 is already in use by another application"

**Cause:** Another program is accessing the camera

**Immediate Action:**
1. Close other camera applications
2. Check Task Manager for camera processes
3. Use camera recovery in Tools menu

**Prevention:**
- Close camera apps before starting recording
- Set application to exclusive camera mode
- Use camera resource management

#### "Could not open camera X"

**Cause:** Camera hardware not accessible

**Immediate Action:**
1. Check camera connection
2. Try different camera index
3. Restart application

**Prevention:**
- Verify camera drivers are installed
- Test camera with other applications
- Use automatic camera detection

#### "Camera opened but cannot read frames"

**Cause:** Camera driver or hardware issue

**Immediate Action:**
1. Update camera drivers
2. Try different USB port
3. Test with manufacturer software

**Prevention:**
- Keep drivers updated
- Use high-quality USB cables
- Avoid USB hubs when possible

### Recording Errors

#### "Could not initialize video writer"

**Cause:** Codec or file system issue

**Immediate Action:**
1. Try different codec (MJPG)
2. Check disk space and permissions
3. Change recording directory

**Prevention:**
- Use compatible codecs
- Ensure sufficient storage
- Test recording directory access

#### "Recording interrupted unexpectedly"

**Cause:** System resource or hardware issue

**Immediate Action:**
1. Check system resources
2. Verify camera connection
3. Review error logs

**Prevention:**
- Monitor system performance
- Use stable hardware connections
- Implement resource monitoring

### Network Errors

#### "Device connection timeout"

**Cause:** Network connectivity issue

**Immediate Action:**
1. Check network connection
2. Restart device server
3. Verify device IP addresses

**Prevention:**
- Use stable network connections
- Implement connection monitoring
- Set appropriate timeout values

#### "Synchronization failed with device"

**Cause:** Command delivery or timing issue

**Immediate Action:**
1. Retry command manually
2. Check device status
3. Verify network latency

**Prevention:**
- Use reliable network protocols
- Implement retry mechanisms
- Monitor sync accuracy

---

## Advanced Diagnostics

### Log Analysis

#### Enabling Detailed Logging

1. **Application Logs**
   ```
   - Enable log panel: View > Show Log
   - Set log level to DEBUG
   - Save logs for analysis
   ```

2. **System Logs**
   ```
   - Check Windows Event Viewer
   - Look for camera-related errors
   - Monitor USB device events
   ```

#### Log Interpretation

**Camera Initialization Logs:**
```
[DEBUG_LOG] Camera initialized: 1280x720 @ 30.0 FPS
[DEBUG_LOG] Camera 0 reserved for webcam_capture
```

**Error Patterns:**
```
[DEBUG_LOG] Error testing camera 0: [Errno 22] Invalid argument
[DEBUG_LOG] Camera 0 recovery (attempt 1)
[DEBUG_LOG] Camera 0 recovery successful
```

### Performance Profiling

#### CPU Usage Analysis

1. **Task Manager Monitoring**
   ```
   - Monitor during different operations
   - Identify CPU-intensive components
   - Check for memory leaks
   ```

2. **Application Profiling**
   ```
   - Use built-in performance monitoring
   - Track frame processing times
   - Monitor codec performance
   ```

#### Memory Usage Tracking

1. **Memory Leak Detection**
   ```
   - Monitor memory usage over time
   - Check for gradual increases
   - Test with long recordings
   ```

2. **Resource Optimization**
   ```
   - Identify memory-intensive operations
   - Optimize buffer sizes
   - Implement garbage collection
   ```

### Network Diagnostics

#### Connection Testing

1. **Basic Connectivity**
   ```
   ping [device_ip]
   telnet [device_ip] [port]
   ```

2. **Bandwidth Testing**
   ```
   - Test network throughput
   - Monitor packet loss
   - Check latency variations
   ```

#### Protocol Analysis

1. **Command Tracking**
   ```
   - Monitor command send/receive
   - Check acknowledgment timing
   - Verify message integrity
   ```

2. **Sync Analysis**
   ```
   - Measure command propagation time
   - Track device response times
   - Analyze timing variations
   ```

---

## System-Specific Issues

### Windows 10/11 Issues

#### Camera Privacy Settings

**Problem:** Camera blocked by privacy settings

**Solution:**
1. Go to Settings > Privacy & Security > Camera
2. Enable "Camera access"
3. Enable "Let desktop apps access your camera"
4. Restart application

#### Driver Compatibility

**Problem:** Generic drivers don't work properly

**Solution:**
1. Download manufacturer-specific drivers
2. Disable driver signature enforcement if needed
3. Use compatibility mode for older drivers

### USB-Specific Issues

#### USB 3.0 Compatibility

**Problem:** Camera doesn't work on USB 3.0 ports

**Solution:**
1. Try USB 2.0 ports
2. Update USB 3.0 drivers
3. Use powered USB hub

#### Power Management

**Problem:** USB devices being suspended

**Solution:**
1. Disable USB selective suspend:
   ```
   Control Panel > Power Options > Change plan settings
   > Change advanced power settings > USB settings
   > USB selective suspend setting > Disabled
   ```

### Antivirus/Security Software

#### Camera Access Blocking

**Problem:** Security software blocks camera access

**Solution:**
1. Add application to antivirus whitelist
2. Disable real-time protection temporarily
3. Configure security software exceptions

#### Network Blocking

**Problem:** Firewall blocks device communication

**Solution:**
1. Add application to firewall exceptions
2. Configure port forwarding if needed
3. Use Windows Defender exceptions

---

## Recovery Procedures

### Automatic Recovery

#### Camera Resource Recovery

The system includes automatic recovery for common issues:

1. **Resource Conflict Recovery**
   ```
   - Detects camera access conflicts
   - Attempts to release and reacquire camera
   - Uses exponential backoff for retries
   ```

2. **Codec Fallback**
   ```
   - Tests codec availability
   - Automatically switches to working codec
   - Maintains recording quality when possible
   ```

3. **Network Recovery**
   ```
   - Monitors device connections
   - Retries failed commands
   - Implements connection restoration
   ```

#### Manual Recovery Triggers

1. **Camera Recovery**
   ```
   Tools > Camera Recovery
   - Forces camera release
   - Reinitializes camera system
   - Tests all available cameras
   ```

2. **Network Recovery**
   ```
   Tools > Network Recovery
   - Restarts device server
   - Reconnects all devices
   - Validates connections
   ```

### Emergency Procedures

#### Complete System Reset

If all else fails:

1. **Application Reset**
   ```
   - Close application completely
   - Delete configuration files
   - Restart with default settings
   ```

2. **System Reset**
   ```
   - Restart computer
   - Disconnect/reconnect cameras
   - Reset network connections
   ```

3. **Clean Installation**
   ```
   - Uninstall application
   - Remove configuration files
   - Reinstall from scratch
   ```

#### Data Recovery

If recordings are corrupted:

1. **File Recovery**
   ```
   - Check session folders for partial files
   - Use video repair tools
   - Extract frames from corrupted videos
   ```

2. **Metadata Recovery**
   ```
   - Check session metadata files
   - Reconstruct timing information
   - Use log files for session details
   ```

---

## Support and Escalation

### Self-Service Resources

1. **Documentation**
   - User Manual: Complete feature guide
   - Configuration Guide: Detailed setup instructions
   - FAQ: Common questions and answers

2. **Testing Tools**
   - Built-in test framework
   - Camera detection utility
   - Performance monitoring tools

3. **Community Resources**
   - User forums and discussions
   - Knowledge base articles
   - Video tutorials

### Information to Collect

Before seeking support, gather:

1. **System Information**
   ```
   - Operating system version
   - Camera model and drivers
   - Application version
   - Hardware specifications
   ```

2. **Error Details**
   ```
   - Exact error messages
   - Steps to reproduce
   - Log files
   - Screenshots/videos
   ```

3. **Configuration**
   ```
   - Current settings
   - Recent changes
   - Network configuration
   - Connected devices
   ```

### Escalation Levels

1. **Level 1: Basic Support**
   - Common issues and solutions
   - Configuration assistance
   - Basic troubleshooting

2. **Level 2: Technical Support**
   - Advanced diagnostics
   - System-specific issues
   - Performance optimization

3. **Level 3: Engineering Support**
   - Software bugs
   - Hardware compatibility
   - Feature requests

### Creating Support Tickets

Include the following information:

1. **Problem Description**
   - Clear, concise summary
   - Steps to reproduce
   - Expected vs. actual behavior

2. **Environment Details**
   - System specifications
   - Software versions
   - Network configuration

3. **Diagnostic Information**
   - Log files
   - Error messages
   - Test results

4. **Impact Assessment**
   - Severity level
   - Business impact
   - Workaround availability

---

## Appendix

### Diagnostic Commands

#### Windows Camera Test
```cmd
# Test camera with PowerShell
Get-PnpDevice -Class Camera
Get-WmiObject Win32_PnPEntity | Where-Object {$_.Name -like "*camera*"}
```

#### Network Diagnostics
```cmd
# Test device connectivity
ping [device_ip]
telnet [device_ip] 9000
netstat -an | findstr 9000
```

#### System Information
```cmd
# Gather system info
systeminfo
dxdiag /t systeminfo.txt
msinfo32
```

### Common File Locations

- **Configuration**: `webcam_config.json`
- **Logs**: `recordings/[session]/session_log.txt`
- **Test Results**: `test_results/test_report_[timestamp].json`
- **Error Logs**: Application log panel

### Recovery Scripts

#### Camera Reset Script
```python
# Reset camera configuration
import json
config = {
    "camera_index": 0,
    "auto_detect_cameras": True,
    "fallback_codecs": ["mp4v", "XVID", "MJPG"]
}
with open("webcam_config.json", "w") as f:
    json.dump(config, f, indent=2)
```

---

*This troubleshooting guide is designed to help you resolve common issues with the webcam integration feature. For additional support, please refer to the User Manual and Configuration Guide.*
