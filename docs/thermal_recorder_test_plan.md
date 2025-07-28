# ThermalRecorder Manual Test Plan

## Overview
This document provides a comprehensive manual test plan for the ThermalRecorder module implementation (Milestone 2.3). The test plan covers all major functionality areas including USB permission handling, thermal recording, file integrity, preview display, and concurrent operation with other recording systems.

## Prerequisites
- Samsung Galaxy S21/S22 device with Android API 24+
- Topdon TC001 or TC001 Plus thermal camera
- USB-C OTG cable
- Windows PC with multi-sensor recording control application
- Wi-Fi network for device communication
- Test objects with different temperatures (hot water, ice pack, etc.)

## Test Environment Setup
1. Install the multi-sensor recording app on Samsung device
2. Ensure USB host mode is enabled on the device
3. Connect device to Wi-Fi network
4. Start PC controller application
5. Establish socket connection between device and PC

## Test Categories

### 1. USB Permission Flow and Device Detection

#### Test 1.1: Initial Device Connection
**Objective**: Verify USB permission request and device detection

**Steps**:
1. Launch the multi-sensor recording app
2. Connect Topdon thermal camera via USB-C OTG
3. Observe USB permission dialog

**Expected Results**:
- USB permission dialog appears automatically
- Dialog shows correct device name (Topdon thermal camera)
- App logs show device detection with correct PID (0x3901, 0x5840, 0x5830, or 0x5838)

**Pass Criteria**: ✅ Permission dialog appears and device is detected correctly

#### Test 1.2: Permission Grant
**Objective**: Verify camera initialization after permission grant

**Steps**:
1. Grant USB permission when prompted
2. Check app logs for initialization messages
3. Verify thermal camera status in app UI

**Expected Results**:
- Permission granted successfully
- Camera initialization completes without errors
- ThermalCameraStatus shows isAvailable = true
- App logs show "Thermal camera initialized successfully"

**Pass Criteria**: ✅ Camera initializes and becomes available

#### Test 1.3: Permission Denial
**Objective**: Verify graceful handling of permission denial

**Steps**:
1. Connect thermal camera
2. Deny USB permission when prompted
3. Check app behavior and error handling

**Expected Results**:
- App handles denial gracefully without crashing
- Error message logged: "USB permission denied for device"
- ThermalCameraStatus shows isAvailable = false
- User can retry by reconnecting device

**Pass Criteria**: ✅ Permission denial handled gracefully

#### Test 1.4: Device Reconnection
**Objective**: Verify device attach/detach handling

**Steps**:
1. Connect and initialize thermal camera
2. Unplug camera during idle state
3. Reconnect camera
4. Grant permission again

**Expected Results**:
- Device detach detected and logged
- Camera status updated to unavailable
- Reconnection triggers new permission request
- Camera reinitializes successfully after permission grant

**Pass Criteria**: ✅ Device reconnection works correctly

### 2. Thermal Recording and File Integrity

#### Test 2.1: Basic Recording Session
**Objective**: Verify thermal data recording functionality

**Steps**:
1. Initialize thermal camera
2. Start recording session via PC controller
3. Record for 30 seconds with thermal camera pointed at test objects
4. Stop recording session
5. Check session directory for thermal data file

**Expected Results**:
- Recording starts successfully
- Thermal data file created: `thermal_{sessionId}.dat`
- File size approximately 2.45 MB for 30 seconds (30s × 25fps × 98KB/frame)
- Session logs show frame count and data size
- No frame drops or errors during recording

**Pass Criteria**: ✅ Thermal data file created with expected size and no errors

#### Test 2.2: File Format Validation
**Objective**: Verify thermal data file format integrity

**Steps**:
1. Complete a recording session
2. Extract thermal data file from device
3. Parse file header and frame data using test script
4. Validate file structure and data integrity

**Expected Results**:
- File header contains "THERMAL1" identifier (8 bytes)
- Width and height values are 256 and 192 respectively
- Frame records contain 8-byte timestamps + 98KB temperature data
- Frame count matches expected value (duration × 25fps)
- Temperature values are within reasonable ranges

**Pass Criteria**: ✅ File format is correct and data is valid

#### Test 2.3: Long Duration Recording
**Objective**: Verify system stability during extended recording

**Steps**:
1. Start thermal recording session
2. Record continuously for 5 minutes
3. Monitor device temperature and performance
4. Stop recording and validate file integrity

**Expected Results**:
- Recording completes without interruption
- File size approximately 735 MB (5min × 2.45MB/min)
- No significant frame drops (< 1% loss acceptable)
- Device remains responsive throughout
- No thermal throttling warnings
- Memory usage remains stable

**Pass Criteria**: ✅ Extended recording completes successfully with stable performance

#### Test 2.4: Temperature Data Accuracy
**Objective**: Verify radiometric data accuracy

**Steps**:
1. Start thermal recording
2. Point camera at objects with known temperatures
3. Record temperature reference measurements
4. Extract and analyze thermal data from recorded file
5. Compare recorded values with reference measurements

**Expected Results**:
- Temperature values correlate with reference measurements
- Hot objects show higher values than cold objects
- Temperature gradients are visible in data
- No corrupted or invalid temperature readings

**Pass Criteria**: ✅ Temperature data shows reasonable correlation with actual temperatures

### 3. Live Preview Display and Streaming

#### Test 3.1: Local Preview Display
**Objective**: Verify thermal preview on device screen

**Steps**:
1. Initialize thermal camera with preview surface
2. Start preview mode
3. Point camera at various objects with different temperatures
4. Observe preview display quality and responsiveness

**Expected Results**:
- Thermal preview appears on device screen
- Iron color palette applied correctly (black→red→yellow→white)
- Hot objects appear in warm colors (red/yellow/white)
- Cold objects appear in cool colors (black/dark red)
- Preview updates smoothly at ~15-25 fps
- Image scaling maintains aspect ratio

**Pass Criteria**: ✅ Local preview displays correctly with proper thermal colorization

#### Test 3.2: PC Streaming Integration
**Objective**: Verify thermal frame streaming to PC

**Steps**:
1. Establish socket connection between device and PC
2. Start thermal recording with preview streaming
3. Monitor PC application for thermal frame reception
4. Verify frame quality and update rate

**Expected Results**:
- PC receives thermal frames via socket connection
- Frames tagged with "THERMAL" identifier
- Frame rate throttled to ~10 fps for bandwidth efficiency
- JPEG compression reduces frame size to ~5-10 KB
- No significant streaming delays or backlog

**Pass Criteria**: ✅ Thermal frames stream successfully to PC with good quality

#### Test 3.3: Preview Performance Impact
**Objective**: Verify preview doesn't affect recording performance

**Steps**:
1. Start thermal recording with preview enabled
2. Monitor recording performance metrics
3. Compare with recording without preview
4. Check for frame drops or performance degradation

**Expected Results**:
- Recording performance unaffected by preview
- No additional frame drops when preview is active
- CPU and memory usage remain within acceptable limits
- File writing performance maintained

**Pass Criteria**: ✅ Preview operation doesn't impact recording performance

### 4. Concurrent Operation with Other Recorders

#### Test 4.1: RGB + Thermal Recording
**Objective**: Verify simultaneous RGB and thermal recording

**Steps**:
1. Initialize both RGB camera and thermal camera
2. Start synchronized recording session
3. Record for 2 minutes with both cameras active
4. Stop recording and verify both data files

**Expected Results**:
- Both recordings start simultaneously
- RGB video file and thermal data file created
- No interference between recording systems
- Timestamps show synchronized start/stop times
- Both files have expected sizes and quality

**Pass Criteria**: ✅ RGB and thermal recording work simultaneously without interference

#### Test 4.2: Full Multi-Sensor Recording
**Objective**: Verify thermal recording with all sensors active

**Steps**:
1. Initialize thermal camera, RGB camera, and Shimmer sensors
2. Start full multi-sensor recording session
3. Record for 3 minutes with all systems active
4. Monitor system performance and resource usage
5. Verify all data files are created correctly

**Expected Results**:
- All recording systems start and stop in sync
- Thermal, RGB, and Shimmer data files created
- No resource conflicts or performance issues
- Session summary shows all modalities active
- File sizes and quality meet expectations

**Pass Criteria**: ✅ All recording systems operate concurrently without issues

#### Test 4.3: Resource Management
**Objective**: Verify proper resource allocation and cleanup

**Steps**:
1. Start and stop multiple recording sessions
2. Monitor memory usage and resource allocation
3. Check for memory leaks or resource conflicts
4. Verify proper cleanup after each session

**Expected Results**:
- Memory usage returns to baseline after each session
- No memory leaks detected
- USB resources properly released
- Background threads terminated correctly
- No resource conflicts between sessions

**Pass Criteria**: ✅ Resources managed properly with no leaks or conflicts

### 5. Error Handling and Edge Cases

#### Test 5.1: Camera Disconnection During Recording
**Objective**: Verify graceful handling of camera disconnection

**Steps**:
1. Start thermal recording session
2. Disconnect thermal camera during active recording
3. Observe app behavior and error handling
4. Check recorded data file integrity

**Expected Results**:
- Disconnection detected immediately
- Recording stops gracefully
- Thermal data file closed properly
- File contains valid data up to disconnection point
- Error logged: "Current thermal camera detached"
- Other recording systems continue if active

**Pass Criteria**: ✅ Camera disconnection handled gracefully without data corruption

#### Test 5.2: No Camera Connected
**Objective**: Verify behavior when starting recording without camera

**Steps**:
1. Start recording session without thermal camera connected
2. Attempt to enable thermal recording
3. Check error handling and user feedback

**Expected Results**:
- Thermal recording fails to start
- Clear error message: "ThermalRecorder not initialized"
- Other recording systems unaffected
- Session can continue with available sensors

**Pass Criteria**: ✅ Missing camera handled gracefully with clear error messages

#### Test 5.3: Storage Space Exhaustion
**Objective**: Verify behavior when storage space is insufficient

**Steps**:
1. Fill device storage to near capacity
2. Start thermal recording session
3. Monitor behavior as storage fills up
4. Check error handling and data integrity

**Expected Results**:
- Recording stops when storage is exhausted
- Error logged with storage space information
- Existing data files remain intact
- User notified of storage issue

**Pass Criteria**: ✅ Storage exhaustion handled without data corruption

### 6. Device Compatibility Testing

#### Test 6.1: TC001 Model Support
**Objective**: Verify support for original TC001 model

**Steps**:
1. Connect TC001 thermal camera
2. Verify device detection and initialization
3. Test all recording and preview functions
4. Validate data quality and format

**Expected Results**:
- TC001 detected with correct PID
- All functions work as expected
- Data format matches specifications
- Preview quality acceptable

**Pass Criteria**: ✅ TC001 model fully supported

#### Test 6.2: TC001 Plus Model Support
**Objective**: Verify support for TC001 Plus model

**Steps**:
1. Connect TC001 Plus thermal camera
2. Verify device detection and initialization
3. Test all recording and preview functions
4. Compare with TC001 functionality

**Expected Results**:
- TC001 Plus detected with correct PID
- All functions work identically to TC001
- No additional visible camera interference
- Data format consistent with TC001

**Pass Criteria**: ✅ TC001 Plus model fully supported

### 7. Performance and Stability Testing

#### Test 7.1: Memory Usage Monitoring
**Objective**: Verify memory usage remains within acceptable limits

**Steps**:
1. Monitor baseline memory usage
2. Start thermal recording with preview
3. Record for 10 minutes while monitoring memory
4. Check for memory leaks or excessive usage

**Expected Results**:
- Memory usage increases moderately during recording
- No continuous memory growth (leaks)
- Memory returns to baseline after recording stops
- Total usage remains under 100MB additional

**Pass Criteria**: ✅ Memory usage stable and within acceptable limits

#### Test 7.2: CPU Performance Impact
**Objective**: Verify CPU usage doesn't cause thermal throttling

**Steps**:
1. Monitor device temperature and CPU usage
2. Start intensive thermal recording session
3. Record for 15 minutes with all features active
4. Check for thermal throttling or performance degradation

**Expected Results**:
- CPU usage remains reasonable (< 50% sustained)
- Device temperature stays within normal range
- No thermal throttling warnings
- Recording performance maintained throughout

**Pass Criteria**: ✅ CPU performance impact acceptable

## Test Results Documentation

### Test Execution Log
| Test ID | Test Name | Date | Result | Notes |
|---------|-----------|------|--------|-------|
| 1.1 | Initial Device Connection | | | |
| 1.2 | Permission Grant | | | |
| 1.3 | Permission Denial | | | |
| ... | ... | | | |

### Issue Tracking
| Issue ID | Description | Severity | Status | Resolution |
|----------|-------------|----------|--------|------------|
| | | | | |

### Performance Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Frame Rate | 25 fps | | |
| File Size | ~2.45 MB/min | | |
| Memory Usage | < 100MB additional | | |
| CPU Usage | < 50% sustained | | |

## Test Completion Criteria

The ThermalRecorder implementation is considered ready for production when:

1. ✅ All USB permission and device detection tests pass
2. ✅ Thermal recording produces valid data files with correct format
3. ✅ Local preview displays thermal imagery with proper colorization
4. ✅ PC streaming delivers thermal frames without significant delays
5. ✅ Concurrent operation with other recorders works without interference
6. ✅ Error conditions are handled gracefully without crashes
7. ✅ Both TC001 and TC001 Plus models are fully supported
8. ✅ Performance metrics meet specified targets
9. ✅ Extended recording sessions complete successfully
10. ✅ Resource management prevents memory leaks and conflicts

## Notes for Testers

- Always test with actual thermal cameras when available
- Document any unexpected behavior or performance issues
- Pay special attention to error handling and edge cases
- Verify data integrity for all recorded files
- Monitor device performance throughout testing
- Test on both Samsung S21 and S22 if available
- Ensure Wi-Fi connectivity is stable during streaming tests
- Use consistent test objects for temperature validation

## Future Test Considerations

- Integration with actual Topdon SDK when available
- Calibration accuracy testing with certified temperature sources
- Extended battery life testing during thermal recording
- Network reliability testing for streaming functionality
- Multi-device synchronization testing