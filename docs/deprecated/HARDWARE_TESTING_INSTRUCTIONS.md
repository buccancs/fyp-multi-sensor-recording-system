# Hardware Testing Instructions - Milestone 2.5 Live Preview Streaming

**Date:** 2025-07-29  
**Status:** Ready for Samsung Device Testing  
**APK Location:** `AndroidApp/build/outputs/apk/dev/debug/AndroidApp-dev-debug.apk`

## Overview

This document provides step-by-step instructions for testing the Milestone 2.5 Live Preview Streaming implementation on Samsung devices with PC controller integration.

## Prerequisites

### Hardware Requirements
- **Samsung Android Device**: API Level 21+ (Android 5.0+)
- **PC/Laptop**: Windows, macOS, or Linux with Python 3.7+
- **Wi-Fi Network**: Both devices connected to same network
- **USB Cable**: For APK installation (optional - can use wireless)

### Software Requirements
- **Android**: APK file ready for installation
- **PC**: Python 3.7+, PyQt5 installed
- **Network**: Port 8080 accessible on PC

## Testing Procedure

### Step 1: PC Setup
1. **Install Python Dependencies**
   ```bash
   pip install PyQt5
   ```

2. **Start PC Socket Server**
   ```bash
   cd PythonApp/src
   python main.py
   ```

3. **Verify Server Status**
   - Confirm "Socket server started on 0.0.0.0:8080" message
   - GUI window should open with preview panels
   - Note PC's IP address for Android configuration

### Step 2: Android Device Setup
1. **Install APK**
   ```bash
   adb install AndroidApp/build/outputs/apk/dev/debug/AndroidApp-dev-debug.apk
   ```
   Or transfer APK to device and install manually

2. **Grant Permissions**
   - Camera permission
   - Storage permission
   - Network permission

3. **Configure Network**
   - Ensure device is on same Wi-Fi as PC
   - Note device IP address

### Step 3: Connection Testing
1. **Launch Android App**
   - Open Multi-Sensor Recording app
   - Verify camera preview displays

2. **Start Recording Session**
   - Tap "Start Recording" button
   - Verify streaming indicator shows "📶 Live"
   - Check debug overlay displays streaming stats

3. **Verify PC Reception**
   - PC GUI should show "Android device connected: [IP]:[PORT]"
   - RGB preview panel should display live camera feed
   - Connection status should show "Connected"

### Step 4: Performance Testing
1. **Frame Rate Validation**
   - Verify ~2fps frame rate on PC display
   - Check for smooth, consistent updates
   - Monitor for frame drops or delays

2. **Image Quality Testing**
   - Verify JPEG compression quality acceptable
   - Check 640x480 resolution maintained
   - Test various lighting conditions

3. **Network Performance**
   - Monitor bandwidth usage (~1.1 Mbps expected)
   - Test under different Wi-Fi conditions
   - Measure latency between capture and display

### Step 5: Thermal Camera Testing (if available)
1. **Thermal Sensor Integration**
   - If thermal camera available, verify thermal preview
   - Check iron color palette visualization
   - Validate thermal data transmission

2. **Multi-Stream Testing**
   - Test both RGB and thermal simultaneously
   - Verify independent frame rates
   - Check PC displays both streams correctly

## Expected Results

### Successful Test Indicators
- ✅ Android app connects to PC server automatically
- ✅ Live RGB camera preview displays on PC in real-time
- ✅ Frame rate maintains ~2fps consistently
- ✅ Image quality acceptable for monitoring purposes
- ✅ Network bandwidth usage within expected range (~1.1 Mbps)
- ✅ No significant battery drain or performance impact
- ✅ Streaming stops/starts with recording sessions

### Performance Benchmarks
- **Frame Rate**: 2fps ±0.5fps
- **Frame Size**: ~50KB JPEG compressed
- **Latency**: <500ms from capture to PC display
- **Bandwidth**: ~1.1 Mbps per camera stream
- **CPU Usage**: <10% on Android device
- **Memory Usage**: <100MB additional

## Troubleshooting

### Connection Issues
- **Problem**: Android can't connect to PC
- **Solution**: Check firewall settings, verify IP addresses, ensure port 8080 open

### Performance Issues
- **Problem**: Frame rate too low or inconsistent
- **Solution**: Check Wi-Fi signal strength, reduce other network traffic

### Image Quality Issues
- **Problem**: Blurry or pixelated preview
- **Solution**: Verify camera focus, check lighting conditions, test JPEG quality settings

## Test Results Documentation

### Required Measurements
1. **Connection Time**: Time from app start to PC connection
2. **Frame Rate**: Actual fps measured over 60-second period
3. **Latency**: Time from Android capture to PC display
4. **Bandwidth**: Network usage during streaming
5. **Battery Impact**: Battery drain rate during streaming
6. **Resource Usage**: CPU and memory usage on both devices

### Test Report Template
```
Hardware Testing Results - Milestone 2.5
Date: [DATE]
Device: [SAMSUNG MODEL]
Network: [WIFI DETAILS]

Connection Test: [PASS/FAIL]
Frame Rate: [X.X fps]
Latency: [XXX ms]
Bandwidth: [X.X Mbps]
Image Quality: [EXCELLENT/GOOD/ACCEPTABLE/POOR]
Battery Impact: [LOW/MEDIUM/HIGH]
Overall Status: [PASS/FAIL]

Notes: [ADDITIONAL OBSERVATIONS]
```

## Success Criteria

The hardware testing is considered successful if:
- ✅ Android-PC connection establishes within 10 seconds
- ✅ Frame rate maintains 1.5-2.5 fps consistently
- ✅ Latency remains under 1 second
- ✅ Image quality suitable for monitoring purposes
- ✅ No crashes or stability issues during 10-minute test
- ✅ Battery drain acceptable for recording session duration

## Next Steps After Testing

1. **Document Results**: Complete test report with measurements
2. **Update Documentation**: Add hardware validation results to changelog
3. **Address Issues**: Fix any identified problems
4. **Final Validation**: Confirm milestone completion
5. **Deployment**: Prepare for production use

---

**Testing Contact**: Development Team  
**Support**: Check logs in Android logcat and PC console for debugging  
**Status**: Ready for Samsung device validation
