# User Guide - Camera Calibration and Shimmer Integration

This guide provides step-by-step instructions for using the newly implemented camera calibration system and Shimmer sensor integration.

## Camera Calibration System

### Overview

The camera calibration system provides comprehensive OpenCV-based calibration for both RGB and thermal cameras, enabling precise spatial alignment and distortion correction.

### Quick Start

#### 1. Basic Calibration Setup

```bash
# Navigate to project directory
cd /path/to/bucika_gsr

# Activate the Python environment
conda activate thermal-env

# Run calibration demonstration
python PythonApp/test_calibration_implementation.py
```

#### 2. Prepare Calibration Pattern

You'll need a printed calibration pattern:
- **Chessboard pattern**: 9x6 squares (default)
- **Circle grid pattern**: Alternative option
- **Square size**: 25mm (recommended for optimal accuracy)

Print the pattern on rigid material (foam board recommended) to avoid bending.

#### 3. Capture Calibration Images

```python
from calibration.calibration import CalibrationManager

# Initialize calibration manager
calibration_manager = CalibrationManager()

# Capture calibration images (manual process)
# - Hold pattern at various angles and distances
# - Ensure pattern fills 20-80% of frame
# - Capture 15-25 images for good coverage
success = calibration_manager.capture_calibration_images(num_images=20)
```

#### 4. Perform Calibration

```python
import cv2

# Load your calibration images
images = []
for i in range(20):
    img = cv2.imread(f"calibration_images/calib_{i:03d}.jpg")
    if img is not None:
        images.append(img)

# Detect calibration patterns
image_points = []
successful_images = []

for image in images:
    success, corners = calibration_manager.detect_calibration_pattern(image)
    if success:
        image_points.append(corners)
        successful_images.append(image)

print(f"Successfully detected patterns in {len(image_points)} images")

# Perform single camera calibration
if len(image_points) >= 10:  # Minimum 10 successful detections
    result = calibration_manager.calibrate_single_camera(
        successful_images, 
        image_points, 
        (1920, 1080)  # Image size (width, height)
    )
    
    print(f"Calibration completed with RMS error: {result['rms_error']:.3f}")
    print(f"Quality recommendation: {result.get('quality_assessment', 'Unknown')}")
```

#### 5. Save and Load Calibration Data

```python
# Save calibration results
success = calibration_manager.save_calibration_data("camera_calibration.json")
if success:
    print("Calibration data saved successfully")

# Load calibration data later
loaded = calibration_manager.load_calibration_data("camera_calibration.json")
if loaded:
    print("Calibration data loaded successfully")
    print(f"Camera matrix:\n{calibration_manager.rgb_camera_matrix}")
```

### Advanced Features

#### Stereo Calibration (RGB-Thermal)

For systems with both RGB and thermal cameras:

```python
# Capture calibration images from both cameras simultaneously
rgb_images = [cv2.imread(f"rgb_calib_{i:03d}.jpg") for i in range(20)]
thermal_images = [cv2.imread(f"thermal_calib_{i:03d}.png") for i in range(20)]

# Detect patterns in both image sets
rgb_points = []
thermal_points = []

for rgb_img, thermal_img in zip(rgb_images, thermal_images):
    rgb_success, rgb_corners = calibration_manager.detect_calibration_pattern(rgb_img)
    thermal_success, thermal_corners = calibration_manager.detect_calibration_pattern(thermal_img)
    
    if rgb_success and thermal_success:
        rgb_points.append(rgb_corners)
        thermal_points.append(thermal_corners)

# Perform stereo calibration
if len(rgb_points) >= 10:
    stereo_result = calibration_manager.calibrate_stereo_cameras(
        rgb_images, thermal_images, rgb_points, thermal_points, (1920, 1080)
    )
    
    print(f"Stereo calibration RMS error: {stereo_result['rms_error']:.3f}")
```

#### Quality Assessment

The system provides comprehensive quality assessment:

```python
# Assess calibration quality
quality_result = calibration_manager.assess_calibration_quality(
    successful_images, image_points, 
    calibration_manager.rgb_camera_matrix, 
    calibration_manager.rgb_distortion_coeffs
)

print(f"Calibration quality score: {quality_result['overall_score']:.2f}")
print(f"Recommendation: {quality_result['recommendation']}")
print(f"Coverage analysis: {quality_result['coverage_analysis']}")
```

## Shimmer Sensor Integration

### Overview

The Shimmer integration system provides comprehensive Bluetooth connectivity for Shimmer3 GSR+ sensors, supporting multiple connection methods and real-time data streaming.

### Quick Start

#### 1. Basic Shimmer Setup

```bash
# Test Shimmer integration
python PythonApp/test_shimmer_implementation.py
```

#### 2. Device Discovery

```python
from shimmer_manager import ShimmerManager

# Initialize Shimmer manager
shimmer_manager = ShimmerManager()

# Discover available devices
devices = shimmer_manager.discover_devices()

print(f"Found {len(devices)} Shimmer devices:")
for device in devices:
    print(f"  - {device['name']} ({device['address']})")
```

#### 3. Connect to Device

```python
# Connect to first available device
if devices:
    device_address = devices[0]['address']
    success = shimmer_manager.connect_device(device_address)
    
    if success:
        print(f"Successfully connected to {device_address}")
        
        # Get device information
        device_info = shimmer_manager.get_device_info(device_address)
        print(f"Device info: {device_info}")
    else:
        print("Failed to connect to device")
```

#### 4. Start Data Streaming

```python
# Configure and start streaming
channels = ['GSR', 'PPG', 'ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']
sampling_rate = 51.2  # Hz

success = shimmer_manager.start_streaming(
    device_address, 
    channels, 
    sampling_rate
)

if success:
    print(f"Started streaming {len(channels)} channels at {sampling_rate}Hz")
```

#### 5. Record Data Session

```python
# Start recording session
session_success = shimmer_manager.start_recording_session(
    session_name="experiment_001",
    output_directory="./recordings"
)

if session_success:
    print("Recording session started")
    
    # Let recording run for desired duration
    import time
    time.sleep(30)  # Record for 30 seconds
    
    # Stop recording
    shimmer_manager.stop_recording_session()
    print("Recording session completed")

# Stop streaming
shimmer_manager.stop_streaming(device_address)
```

### Advanced Features

#### Multiple Device Management

```python
# Connect to multiple devices
connected_devices = []

for device in devices[:2]:  # Connect to first 2 devices
    address = device['address']
    if shimmer_manager.connect_device(address):
        connected_devices.append(address)
        print(f"Connected to {address}")

# Start streaming on all connected devices
for address in connected_devices:
    shimmer_manager.start_streaming(
        address, 
        ['GSR', 'PPG'], 
        sampling_rate=51.2
    )

print(f"Streaming from {len(connected_devices)} devices")
```

#### Connection Type Selection

```python
from shimmer_manager import ConnectionType

# Try different connection methods
connection_types = [
    ConnectionType.PYSHIMMER,
    ConnectionType.ANDROID_MEDIATED
]

for conn_type in connection_types:
    success = shimmer_manager.connect_device(device_address, conn_type)
    if success:
        print(f"Connected using {conn_type.value}")
        break
    else:
        print(f"Failed to connect using {conn_type.value}")
```

#### Data Processing Callbacks

```python
# Define data processing callback
def process_shimmer_data(data_sample):
    """Process incoming Shimmer data sample"""
    timestamp = data_sample['timestamp']
    gsr_value = data_sample.get('GSR', None)
    ppg_value = data_sample.get('PPG', None)
    
    print(f"Time: {timestamp:.3f}, GSR: {gsr_value}, PPG: {ppg_value}")

# Register callback
shimmer_manager.register_data_callback(process_shimmer_data)
```

### Troubleshooting

#### Common Issues

**Device Discovery Problems:**
```python
# Check if Bluetooth is available
if not shimmer_manager.is_bluetooth_available():
    print("Bluetooth not available - check system Bluetooth settings")

# Check for library dependencies
if not shimmer_manager.check_dependencies():
    print("Missing optional dependencies - install pyshimmer, bluetooth, or pybluez")
```

**Connection Issues:**
```python
# Verify device pairing
paired_devices = shimmer_manager.get_paired_devices()
print(f"Paired devices: {[d['address'] for d in paired_devices]}")

# Test connection with different methods
for conn_type in ConnectionType:
    try:
        success = shimmer_manager.connect_device(device_address, conn_type)
        if success:
            print(f"Success with {conn_type.value}")
            break
    except Exception as e:
        print(f"Failed with {conn_type.value}: {e}")
```

**Data Streaming Issues:**
```python
# Check device status
status = shimmer_manager.get_device_status(device_address)
print(f"Device status: {status}")

# Verify channel configuration
available_channels = shimmer_manager.get_available_channels(device_address)
print(f"Available channels: {available_channels}")
```

## Integration with Android App

### Android-PC Coordination

The system supports coordinated operation between Android devices and PC:

```python
# Start coordinated recording session
def start_coordinated_session():
    # 1. Start PC-based Shimmer recording
    shimmer_manager.start_recording_session("coordinated_session", "./recordings")
    
    # 2. Send command to Android devices to start recording
    # (via existing socket communication)
    
    # 3. Start stimulus presentation if needed
    # (via existing stimulus system)
    
    print("Coordinated session started")

# Stop coordinated session
def stop_coordinated_session():
    # 1. Stop Android recording
    # 2. Stop PC Shimmer recording
    shimmer_manager.stop_recording_session()
    
    # 3. Stop stimulus presentation
    print("Coordinated session stopped")
```

### Data Synchronization

```python
# Synchronize timestamps across all data sources
from datetime import datetime

# Get synchronized timestamp
sync_timestamp = datetime.now().timestamp()

# Include sync timestamp in all data records
data_record = {
    'sync_timestamp': sync_timestamp,
    'shimmer_data': shimmer_data,
    'android_data': android_data,
    'stimulus_events': stimulus_events
}
```

## Best Practices

### Calibration Best Practices

1. **Pattern Quality**: Use high-quality printed patterns on rigid surfaces
2. **Image Variety**: Capture images with pattern at various angles and distances
3. **Coverage**: Ensure pattern appears across entire image area in different positions
4. **Quantity**: Use 15-25 successful pattern detections for robust calibration
5. **Validation**: Always check calibration quality metrics before using results

### Shimmer Best Practices

1. **Device Preparation**: Ensure devices are charged and properly paired
2. **Connection Testing**: Test connections before important recordings
3. **Backup Methods**: Use multiple connection types for reliability
4. **Data Validation**: Monitor data quality during streaming
5. **Session Management**: Use descriptive session names and organized directory structure

### System Integration

1. **Synchronized Recording**: Use coordinated start/stop commands
2. **Timestamp Alignment**: Ensure all data sources use synchronized timestamps
3. **Error Handling**: Implement proper error recovery for device disconnections
4. **Data Backup**: Regularly backup calibration data and recorded sessions
5. **Performance Monitoring**: Monitor system performance during multi-device recording

## Testing and Validation Workflows

The multi-sensor recording system includes comprehensive testing capabilities that allow users to validate system functionality, troubleshoot issues, and ensure optimal performance. This section provides detailed guidance on using the testing framework for various validation scenarios.

### Quick System Validation

For rapid system validation, especially useful during initial setup or after system updates, use the quick recording session test:

```bash
# Navigate to the Python application directory
cd PythonApp

# Run quick comprehensive validation
python run_quick_recording_session_test.py
```

This streamlined test performs a complete validation of the PC-Android simulation workflow in approximately 30 seconds. The test validates all essential system components including:

• **PC Application Initialization**: Verifies that all core components (SessionManager, JsonSocketServer, logging system) initialize correctly
• **Android Device Simulation**: Tests the creation and management of multiple simulated Android devices with realistic sensor capabilities
• **Communication Protocols**: Validates JSON socket communication between PC and Android components on production ports
• **Recording Session Management**: Tests complete recording lifecycle from session creation to data persistence
• **Sensor Data Generation**: Validates realistic sensor data simulation including GSR, PPG, accelerometer, gyroscope, and magnetometer data
• **File System Operations**: Verifies session folder creation, file naming conventions, and data persistence
• **Logging and Monitoring**: Tests comprehensive logging functionality and system health monitoring

The quick test provides immediate feedback with clear success/failure indicators and detailed error reporting when issues are detected.

### Comprehensive Testing Scenarios

For thorough system validation, use the enhanced test runner that supports multiple testing scenarios and extensive configuration options:

#### Basic Comprehensive Testing
```bash
# Standard comprehensive test with default parameters
python run_recording_session_test.py

# Extended test with longer duration and more devices
python run_recording_session_test.py --duration 120 --devices 4 --verbose

# Test with detailed logging and health monitoring
python run_recording_session_test.py --save-logs --health-check --log-level DEBUG
```

#### Advanced Testing Scenarios

**Stress Testing for High-Load Validation:**
```bash
# High-load stress testing with multiple devices
python run_recording_session_test.py --stress-test --devices 8 --duration 300

# Combined stress and performance testing
python run_recording_session_test.py --stress-test --performance-bench --save-logs
```

Stress testing validates system behavior under high-load conditions by simulating increased device counts, concurrent operations, and elevated data throughput. This testing scenario is particularly valuable for validating system scalability and identifying performance bottlenecks.

**Performance Benchmarking:**
```bash
# Detailed performance metrics collection
python run_recording_session_test.py --performance-bench --duration 90

# Performance benchmarking with system health monitoring
python run_recording_session_test.py --performance-bench --health-check --save-logs
```

Performance benchmarking provides detailed metrics on system throughput, latency, memory usage, and resource utilization. The benchmark results help optimize system configuration and identify areas for performance improvements.

**Stability and Long-Duration Testing:**
```bash
# Extended stability testing (minimum 10 minutes)
python run_recording_session_test.py --long-duration --health-check

# Long-duration test with memory leak detection
python run_recording_session_test.py --long-duration --memory-stress --save-logs
```

Long-duration testing validates system stability over extended periods, monitors for memory leaks, and ensures consistent performance during prolonged recording sessions.

**Error Condition and Recovery Testing:**
```bash
# Error simulation and recovery validation
python run_recording_session_test.py --error-simulation --devices 3

# Network issues and reconnection testing
python run_recording_session_test.py --network-issues --error-simulation

# Combined error and stress testing
python run_recording_session_test.py --error-simulation --network-issues --stress-test
```

Error condition testing intentionally introduces various failure scenarios to validate system recovery mechanisms, error handling, and graceful degradation capabilities.

### Component-Specific Testing

#### Camera Calibration Testing
```bash
# Test calibration system implementation
python test_calibration_implementation.py

# Run calibration with specific parameters
python -c "
from calibration.calibration import CalibrationManager
manager = CalibrationManager()
# Test pattern detection
success = manager.test_pattern_detection()
print(f'Pattern detection test: {\"PASSED\" if success else \"FAILED\"}')
"
```

#### Shimmer Sensor Testing
```bash
# Test Shimmer integration capabilities
python test_shimmer_implementation.py

# Test specific Shimmer connection methods
python -c "
from shimmer.shimmer_manager import ShimmerManager
manager = ShimmerManager()
# Test device discovery
devices = manager.discover_devices()
print(f'Discovered {len(devices)} Shimmer devices')
"
```

#### Integration Testing
```bash
# Run complete integration test suite
python run_comprehensive_tests.py

# Generate detailed test report
python run_comprehensive_tests.py --generate-report --save-logs
```

### Testing Configuration and Troubleshooting

#### Test Configuration Options

The testing framework provides extensive configuration options to adapt testing scenarios to specific requirements:

**Duration and Scale Configuration:**
• `--duration SECONDS` - Set test duration to match typical usage patterns
• `--devices COUNT` - Configure device count to match deployment scenarios
• `--port PORT` - Test with different communication ports

**Logging and Monitoring Configuration:**
• `--verbose` - Enable detailed progress information for debugging
• `--log-level LEVEL` - Control logging verbosity (DEBUG for maximum detail)
• `--save-logs` - Persist logs for post-analysis and troubleshooting
• `--health-check` - Enable continuous system resource monitoring

**Advanced Testing Configuration:**
• `--stress-test` - Enable high-load testing scenarios
• `--performance-bench` - Collect detailed performance metrics
• `--error-simulation` - Test error conditions and recovery mechanisms
• `--network-issues` - Simulate network connectivity problems
• `--memory-stress` - Test memory usage under high data volumes

#### Troubleshooting Test Failures

When tests fail, use this systematic approach to identify and resolve issues:

**1. Enable Verbose Logging:**
```bash
python run_recording_session_test.py --verbose --log-level DEBUG --save-logs
```
This provides detailed execution information and saves logs for analysis.

**2. Test Individual Components:**
```bash
# Test calibration system separately
python test_calibration_implementation.py

# Test Shimmer integration independently
python test_shimmer_implementation.py
```
Component isolation helps identify the specific source of failures.

**3. Check System Resources:**
```bash
# Monitor system resources during testing
python run_recording_session_test.py --health-check --performance-bench
```
Resource monitoring reveals memory, CPU, or disk space issues.

**4. Validate Network Configuration:**
```bash
# Test with alternative ports
python run_recording_session_test.py --port 9001

# Test network connectivity
python run_recording_session_test.py --network-issues
```
Network diagnostics help identify connectivity problems.

**5. Analyze Error Patterns:**
Review saved log files for error patterns, resource constraints, or timing issues. Common issues include:
• Port conflicts with other applications
• Insufficient memory for high device counts
• Network connectivity problems
• Missing dependencies or configuration errors

#### Performance Optimization

Use performance testing results to optimize system configuration:

**Memory Optimization:**
• Monitor memory usage during testing with `--memory-stress`
• Adjust device count based on available system memory
• Use `--long-duration` testing to identify memory leaks

**Network Optimization:**
• Test different port configurations with `--port`
• Validate network stability with `--network-issues`
• Monitor communication latency during `--performance-bench`

**Scaling Optimization:**
• Use `--stress-test` to determine maximum device capacity
• Test concurrent operation limits
• Validate performance under realistic load conditions

### Test Results Interpretation

#### Success Indicators
Successful tests display comprehensive validation results:
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

#### Performance Metrics
Performance benchmarking provides detailed metrics:
• **Execution Time**: Total test duration and per-scenario timing
• **Resource Usage**: Memory consumption, CPU utilization, disk space
• **Communication Metrics**: Message throughput, latency, packet loss
• **Data Processing**: Sensor data generation rates, file I/O performance

#### Error Analysis
Failed tests provide detailed error information:
• **Error Location**: Specific test phase or component where failure occurred
• **Error Type**: Classification of error (network, memory, configuration, etc.)
• **Recovery Actions**: Suggested remediation steps and configuration changes
• **System State**: Resource usage and system health at time of failure

For additional support and troubleshooting, refer to the API Reference documentation and the comprehensive test scripts provided with the system.