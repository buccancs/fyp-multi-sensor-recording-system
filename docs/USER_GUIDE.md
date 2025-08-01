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

---

## Comprehensive Testing Guide

The Multi-Sensor Recording System includes an extensive testing framework designed to validate all aspects of system functionality under various real-world conditions. This testing capability has been significantly extended to meet the comprehensive requirements for research-grade reliability and data integrity.

### Testing Philosophy and Approach

The testing framework validates the complete system as specified in the original requirements: "create a test, when both the PC and Android app is started and we start a recording session if a phone is connected to the PC/IDE, what we start from the computer. Use the available sensors and simulate the rest on the correct port, just like in real life. And test the communication, networking, file saving, post processing, button reaction and any freezing or crashing. Also check the logs whether it logged correctly everything."

The enhanced testing approach goes beyond these requirements to include:
- **Performance validation** under stress conditions with memory and CPU monitoring
- **Network resilience testing** with latency, packet loss, and connection recovery simulation
- **Data integrity assurance** with checksum validation and corruption detection
- **Concurrent session testing** for multi-user research scenarios
- **Error injection testing** to validate robust error recovery mechanisms

### Quick Start Testing

#### Running the Complete Test Suite

The most comprehensive way to validate the system is to run the complete enhanced test suite:

```bash
# Navigate to the project directory
cd /path/to/bucika_gsr

# Activate the Python environment
conda activate thermal-env

# Run the complete enhanced test suite
python PythonApp/run_complete_test_suite.py
```

This command executes all testing categories and provides a comprehensive report of system functionality, including:
- Foundation tests for basic component integration
- Core functionality tests for recording session lifecycle
- Hardware integration tests with realistic sensor simulation
- Enhanced stress testing for performance validation
- Network resilience testing for connection reliability
- Data integrity testing for corruption detection and recovery
- Complete end-to-end system validation

#### Understanding Test Results

The test suite provides detailed output and saves results to the `test_results/` directory:

```bash
# View test results
ls test_results/
# complete_test_results.json          - Overall test suite summary
# enhanced_stress_test_results.json   - Performance and resource testing
# network_resilience_test_results.json - Network condition testing
# data_integrity_test_results.json    - Data quality validation
```

### Individual Testing Categories

#### Foundation and Integration Testing

These tests validate the basic system components and their integration:

```bash
# Test logging system and component integration
python PythonApp/test_integration_logging.py

# Test calibration implementation
python PythonApp/test_calibration_implementation.py

# Test Shimmer sensor integration
python PythonApp/test_shimmer_implementation.py
```

**What these tests validate:**
- Logging system functionality across all components
- Camera calibration accuracy and quality assessment
- Shimmer sensor connectivity and data streaming
- Component integration and error handling

#### Core Recording Functionality Testing

These tests validate the primary recording capabilities:

```bash
# Test PC-Android coordination and recording lifecycle
python PythonApp/test_focused_recording_session.py

# Test comprehensive sensor simulation on correct ports
python PythonApp/test_hardware_sensor_simulation.py

# Test complete end-to-end recording system
python PythonApp/test_comprehensive_recording_session.py
```

**What these tests validate:**
- PC and Android app coordination with socket communication
- Phone connection to PC/IDE simulation with realistic protocols
- Recording session initiation from computer with proper session management
- Available sensor usage with rest simulated on correct ports (USB, Bluetooth, TCP/UDP)
- Communication and networking with message exchange validation
- File saving and post-processing with metadata generation
- Button reaction and UI responsiveness with timing validation
- Error handling and crash recovery with comprehensive logging

#### Enhanced Performance and Stress Testing

These tests validate system performance under demanding conditions:

```bash
# Test memory usage, CPU performance, and concurrent sessions
python PythonApp/test_enhanced_stress_testing.py

# Test network resilience with latency and packet loss
python PythonApp/test_network_resilience.py

# Test data integrity with corruption detection
python PythonApp/test_data_integrity_validation.py
```

**What these tests validate:**
- **Memory Performance**: Memory usage monitoring during extended sessions, leak detection, and resource cleanup validation
- **CPU Performance**: System performance under high sensor data throughput and concurrent processing
- **Concurrent Sessions**: Multi-session scalability testing with multiple simultaneous recordings
- **Network Resilience**: Connection reliability under various network conditions including latency (1ms-500ms), packet loss (0.1%-10%), and bandwidth limitations
- **Data Integrity**: Checksum validation (MD5/SHA256), corruption detection, and file format integrity for all data types

### Advanced Testing Scenarios

#### Stress Testing and Performance Validation

The enhanced stress testing validates system performance under research-grade load conditions:

```python
# Example: Custom stress test configuration
from test_enhanced_stress_testing import StressTester
import asyncio

async def custom_stress_test():
    tester = StressTester()
    
    # Test with extended duration and more devices
    result = await tester.run_memory_stress_test(duration_seconds=120)  # 2 minutes
    concurrent_result = await tester.run_concurrent_session_test(num_sessions=8)  # 8 sessions
    
    print(f"Memory test success: {result.success}")
    print(f"Max memory usage: {result.max_memory_mb:.1f}MB")
    print(f"Concurrent sessions success: {concurrent_result.success}")

# Run custom test
asyncio.run(custom_stress_test())
```

**Performance Metrics Validated:**
- Memory usage peaks and leak detection
- CPU utilization under load
- Network throughput and latency
- Disk I/O performance
- Thread pool utilization
- Resource cleanup efficiency

#### Network Resilience and Connectivity Testing

The network resilience testing simulates various real-world network conditions:

**Network Conditions Tested:**
- **Perfect Network**: Baseline testing with ideal conditions (1ms latency, 0% loss)
- **High Latency**: Satellite-like conditions (500ms latency, 100ms jitter)
- **Packet Loss**: Moderate loss conditions (5% packet loss, 50ms latency)
- **Limited Bandwidth**: Cellular-like conditions (1 Mbps, 100ms latency, 1% loss)
- **Unstable Connection**: Frequent disconnections with recovery testing

**How to run specific network condition tests:**

```python
# Example: Test specific network condition
from test_network_resilience import NetworkResilienceTester, NetworkCondition
import asyncio

async def test_specific_condition():
    tester = NetworkResilienceTester()
    
    # Create custom network condition
    poor_wifi = NetworkCondition(
        name="Poor WiFi",
        latency_ms=200.0,
        packet_loss_percent=8.0,
        bandwidth_mbps=0.5,
        jitter_ms=150.0,
        connection_drops=True,
        description="Poor WiFi conditions in remote research facility"
    )
    
    result = await tester.test_network_condition(poor_wifi, duration=60)
    print(f"Test success: {result.success}")
    print(f"Message loss: {result.message_loss_percent:.1f}%")
    print(f"Recovery time: {result.recovery_time_seconds:.1f}s")

asyncio.run(test_specific_condition())
```

#### Data Integrity and Corruption Testing

The data integrity testing ensures research data reliability:

**Types of Corruption Tested:**
- **Random Byte Corruption**: Random bit flips in file content (1-5% of file)
- **Header Corruption**: Corruption of file headers affecting format validation
- **File Truncation**: Partial file loss scenarios (5-10% of file size)
- **Checksum Validation**: MD5 and SHA256 verification for all file types
- **Format Validation**: File format integrity for MP4, CSV, JSON, and binary data

**Data Types Validated:**
- **Video Files**: MP4 format integrity and header validation
- **Thermal Data**: Binary format validation with expected frame counts
- **GSR Data**: CSV format validation with column structure and data type checking
- **Metadata**: JSON format validation with required field verification

### Session Data Validation

Beyond the enhanced testing framework, the system provides tools for validating recorded session data:

#### Complete Session Validation

```bash
# Validate all recorded sessions
python tools/validate_data_schemas.py --all-sessions

# Validate specific session
python tools/validate_data_schemas.py --session PythonApp/recordings/session_20250731_143022

# Validate session integrity with checksums
python tools/validate_session_integrity.py --session session_20250731_143022 --verify-checksums
```

#### Session Data Quality Analysis

```bash
# Analyze session data quality and synchronization
python tools/analyze_session_quality.py --session session_20250731_143022

# Generate comprehensive session report
python tools/generate_session_report.py --session session_20250731_143022 --format html

# Export session data for analysis
python tools/export_session_data.py --session session_20250731_143022 --format csv
```

### Test Configuration and Customization

#### Customizing Test Parameters

The testing framework allows customization of test parameters for specific research needs:

```python
# Example: Custom test configuration
test_config = {
    "stress_test": {
        "duration_seconds": 300,  # 5 minutes
        "num_devices": 12,        # 12 simulated devices
        "data_rate_multiplier": 2.0  # 2x normal data rate
    },
    "network_test": {
        "latency_range": [10, 1000],  # 10ms to 1000ms
        "packet_loss_range": [0.1, 15.0],  # 0.1% to 15%
        "test_duration": 180  # 3 minutes per condition
    },
    "integrity_test": {
        "corruption_levels": [0.5, 1.0, 2.0, 5.0],  # Corruption percentages
        "file_types": ["video", "thermal", "gsr", "metadata"]
    }
}
```

#### Environment-Specific Testing

For different research environments, tests can be configured to match specific conditions:

```bash
# Test for laboratory environment (high-end network, stable power)
python PythonApp/run_complete_test_suite.py --profile laboratory

# Test for field research environment (variable network, power constraints)
python PythonApp/run_complete_test_suite.py --profile field_research

# Test for clinical environment (strict data integrity, compliance requirements)
python PythonApp/run_complete_test_suite.py --profile clinical
```

### Continuous Integration and Quality Assurance

#### Automated Testing in Development

The testing framework integrates with development workflows:

```bash
# Gradle-based testing for complete build validation
./gradlew build  # Includes all unit and integration tests

# Python-specific testing
./gradlew :PythonApp:runPythonTests
./gradlew :PythonApp:runPythonTestsWithCoverage

# Android-specific testing
./gradlew :AndroidApp:testDebugUnitTest
./gradlew :AndroidApp:connectedDebugAndroidTest
./gradlew :AndroidApp:lintDebug
```

#### Quality Gates and Metrics

The testing framework enforces quality gates for research-grade reliability:

**Coverage Requirements:**
- Unit test coverage: >90% for core components
- Integration test coverage: >85% for cross-component interactions
- End-to-end test coverage: 100% of critical user workflows

**Performance Requirements:**
- Memory usage: <512MB increase during extended sessions
- CPU usage: <80% average during normal operation
- Network recovery: <5 seconds for connection restoration
- Data integrity: 100% checksum validation pass rate

**Reliability Requirements:**
- Test success rate: >98% across all test categories
- Error recovery rate: >95% for all failure scenarios
- Data corruption detection: 100% for all corruption types tested

### Troubleshooting Test Failures

#### Common Test Issues and Solutions

**Memory Test Failures:**
- **Symptom**: Memory usage exceeds thresholds
- **Solution**: Check for memory leaks, verify garbage collection, reduce concurrent device count
- **Investigation**: Review memory usage graphs in test results

**Network Test Failures:**
- **Symptom**: High message loss or connection failures
- **Solution**: Verify network configuration, check firewall settings, validate retry logic
- **Investigation**: Examine network condition logs and connection timing

**Data Integrity Test Failures:**
- **Symptom**: Unexpected checksum matches or corruption not detected
- **Solution**: Verify file permissions, check disk space, validate corruption injection
- **Investigation**: Review file operation logs and checksum calculations

#### Test Environment Validation

Before running tests, validate the test environment:

```bash
# Validate test environment setup
python tools/validate_test_environment.py

# Check system resources
python tools/check_system_requirements.py --verbose

# Verify network connectivity
python tools/test_network_connectivity.py --comprehensive
```

### Research-Specific Testing Considerations

#### Multi-Participant Studies

For research involving multiple participants, the testing framework validates scalability:

- **Concurrent Session Testing**: Validates system performance with multiple simultaneous recordings
- **Resource Contention**: Tests system behavior when multiple sessions compete for resources
- **Data Isolation**: Ensures proper data separation between concurrent sessions
- **Synchronization Accuracy**: Validates temporal alignment across multiple simultaneous recordings

#### Long-Duration Studies

For extended research sessions, the testing framework validates long-term stability:

- **Extended Session Testing**: Validates system stability over hours of continuous operation
- **Memory Leak Detection**: Monitors for gradual resource consumption increases
- **Performance Degradation**: Detects system performance changes over time
- **Storage Capacity**: Validates proper handling of large data volumes

#### Data Quality Assurance

For research requiring high data quality standards, the testing framework provides:

- **Temporal Synchronization Validation**: Ensures microsecond-level timestamp accuracy
- **Sensor Data Quality**: Validates realistic data ranges and consistency
- **Calibration Accuracy**: Verifies camera calibration precision for spatial measurements
- **Cross-Device Correlation**: Validates data alignment across multiple recording devices

This comprehensive testing approach ensures that the Multi-Sensor Recording System meets the demanding requirements of scientific research while providing the reliability and data integrity essential for valid experimental results.

For additional support and troubleshooting, refer to the API Reference documentation and the comprehensive test scripts provided with the system.