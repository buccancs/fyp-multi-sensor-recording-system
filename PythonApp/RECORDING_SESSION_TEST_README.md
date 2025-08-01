# Comprehensive Recording Session Test

This document describes the comprehensive recording session test implementation that validates the complete multi-sensor recording system workflow as specified in the requirements.

## Overview

The test simulates a realistic recording session where both the PC and Android app are started, and a recording session is initiated from the computer. It tests all critical aspects of the system including communication, networking, file saving, post-processing, button reactions, and comprehensive logging validation.

## Test Implementation

### Files Created

1. **`test_comprehensive_recording_session.py`** - Main comprehensive test with full feature validation
2. **`run_recording_session_test.py`** - Enhanced test runner with configuration options
3. **`run_quick_recording_session_test.py`** - Simplified test for quick validation
4. **Updated `run_comprehensive_tests.py`** - Integration with existing test infrastructure

### Requirements Validated

The test validates all requirements specified in the problem statement:

#### ✅ PC and Android App Startup Simulation
- Initializes PC application components (SessionManager, JsonSocketServer)
- Starts multiple Android device simulations with realistic sensor capabilities
- Establishes proper communication channels on correct ports

#### ✅ Recording Session Initiated from Computer
- Creates recording session using SessionManager from PC side
- Sends start recording commands to all connected Android devices
- Validates command acknowledgments and session coordination

#### ✅ Sensor Simulation on Correct Ports
- Simulates realistic GSR sensor data with proper physiological characteristics
- Uses port 9000 (or configurable) as specified for real-world usage
- Generates PPG, accelerometer, gyroscope, and magnetometer data
- Maintains 50Hz sampling rate as per real sensor specifications

#### ✅ Communication and Networking Testing
- Tests JSON message protocol between PC and Android devices
- Validates message acknowledgments and error handling
- Monitors packet loss and connection stability
- Tests handshake and device registration procedures

#### ✅ File Saving and Data Persistence
- Creates session folders with proper naming conventions
- Saves sensor data in CSV and JSON formats
- Validates file integrity and content structure
- Tests metadata persistence and session information

#### ✅ Post-Processing Validation
- Data validation and integrity checks
- Sensor calibration simulation
- Time synchronization verification
- Data export format validation

#### ✅ Button Reaction Simulation
- Simulates various UI button interactions (pause, resume, calibration)
- Tests command processing and response times
- Validates UI responsiveness and error handling
- Tests device status updates and feedback

#### ✅ Freezing and Crashing Detection
- Implements HealthMonitor for continuous system monitoring
- Tracks heartbeat signals and silence duration detection
- Monitors memory usage and potential memory leaks
- Validates system stability under load

#### ✅ Comprehensive Logging Validation
- Tests structured JSON logging for machine parsing
- Validates log file creation and rotation
- Checks for key events in log entries (session start, device connections, etc.)
- Verifies performance timing logs and error tracking

## Usage

### Quick Test (Recommended for CI/CD)

```bash
cd PythonApp
python run_quick_recording_session_test.py
```

This runs a simplified version that covers all core requirements without additional dependencies.

### Comprehensive Test (Full Feature Validation)

```bash
cd PythonApp
python run_recording_session_test.py --duration 60 --devices 2 --save-logs --verbose
```

Available options:
- `--duration SECONDS`: Recording simulation duration (default: 30)
- `--devices COUNT`: Number of Android devices to simulate (default: 2)
- `--port PORT`: Server port to use (default: 9000)
- `--verbose`: Enable verbose output
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--save-logs`: Save detailed logs to file
- `--health-check`: Enable continuous health monitoring

### Integration with Existing Tests

```bash
cd PythonApp
python run_comprehensive_tests.py
```

The recording session test is now integrated with the existing comprehensive test suite.

## Test Architecture

### Enhanced Device Simulator

The `EnhancedDeviceSimulator` class extends the existing `DeviceSimulator` with:

- Realistic GSR sensor data generation with physiological characteristics
- Health monitoring with heartbeat tracking
- Proper message acknowledgment handling
- Session state management
- Performance metrics collection

### Health Monitor

The `HealthMonitor` class provides:

- Continuous system health tracking
- Freeze detection through silence monitoring
- Memory usage monitoring
- Performance metrics collection
- Issue reporting and categorization

### Comprehensive Test Phases

The test follows a structured approach with 10 phases:

1. **PC Application Initialization** - Setup core components
2. **Android Device Simulations** - Start multiple device simulators
3. **Communication Testing** - Validate networking and protocols
4. **Recording Session Start** - Initiate session from PC
5. **Session Monitoring** - Track recording with realistic data
6. **Button Interaction Simulation** - Test UI responsiveness
7. **Recording Session Stop** - Validate session termination
8. **Post-Processing** - Test data processing workflows
9. **Health Validation** - Check system stability
10. **Logging Validation** - Verify comprehensive logging

## Technical Details

### Communication Protocol

The test uses the JSON socket protocol as defined in `protocol/message_schema.json`:

- Length-prefixed message protocol
- JSON message format with timestamps
- Device handshake and capability negotiation
- Command acknowledgment system
- Status update messages

### Sensor Data Simulation

Realistic sensor data generation includes:

- **GSR**: Base value with stress factor simulation and noise
- **PPG**: Heart rate simulation (60-100 BPM)
- **Accelerometer**: Static positioning with small movements
- **Gyroscope**: Low-frequency rotation simulation
- **Magnetometer**: Environmental magnetic field simulation

### Performance Monitoring

The test includes comprehensive performance monitoring:

- Operation timing with microsecond precision
- Memory usage tracking and leak detection
- Network throughput measurement
- Data processing rate validation
- System resource utilization

## Expected Outcomes

A successful test run should show:

```
✅ COMPREHENSIVE RECORDING SESSION TEST COMPLETED SUCCESSFULLY!
All requirements have been validated:
• PC and Android app startup simulation ✓
• Recording session initiated from computer ✓
• Sensor simulation on correct ports ✓
• Communication and networking testing ✓
• File saving and data persistence ✓
• Post-processing validation ✓
• Button reaction simulation ✓
• Freezing/crashing detection ✓
• Comprehensive logging validation ✓
```

## Error Handling

The test includes robust error handling for:

- Network connection failures
- Device simulation errors
- File system issues
- Memory allocation problems
- Protocol violations
- Performance degradation

## Continuous Integration

The test is designed for CI/CD integration:

- Exit codes: 0 for success, 1 for failure
- Structured logging for automated analysis
- Configurable timeouts and thresholds
- Minimal external dependencies
- Performance benchmarking

## Troubleshooting

### Common Issues

1. **Port conflicts**: Use `--port` to specify alternative port
2. **Timeout issues**: Increase `--duration` for longer validation
3. **Memory warnings**: Normal for comprehensive testing
4. **Import errors**: Ensure all dependencies are available

### Debug Mode

For detailed debugging:

```bash
python run_recording_session_test.py --log-level DEBUG --save-logs --verbose
```

This creates detailed logs in the specified log directory for analysis.

## Future Enhancements

Potential areas for expansion:

- Real hardware device integration
- Network latency simulation
- Multi-threaded stress testing
- GUI automation testing
- Database integration testing
- Cloud synchronization testing

## Conclusion

This comprehensive recording session test validates all specified requirements and provides a robust foundation for ensuring the multi-sensor recording system works correctly in real-world scenarios. The test can be used for development validation, CI/CD integration, and regression testing.