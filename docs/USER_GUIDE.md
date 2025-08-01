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

For additional support and troubleshooting, refer to the API Reference documentation and the comprehensive test scripts provided with the system.