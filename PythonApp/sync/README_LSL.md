# Enhanced Time Synchronization with Lab Streaming Layer (LSL)

The multi-sensor recording system now supports both traditional NTP-like synchronization and Lab Streaming Layer (LSL) for research-grade time synchronization and data streaming.

## Features

### Enhanced Synchronization Manager

The `EnhancedSynchronizationManager` automatically selects the best available synchronization method:

- **NTP-like Synchronization**: Custom UDP-based time server with sub-millisecond accuracy
- **LSL Synchronization**: Lab Streaming Layer integration for research environments
- **Automatic Fallback**: Falls back to NTP when LSL is unavailable
- **Unified API**: Single interface for both synchronization methods

### Lab Streaming Layer Integration

#### What is LSL?

Lab Streaming Layer (LSL) is a system for the unified collection of measurement time series in research experiments. It handles:
- Networking and time synchronization
- Real-time data access
- Record and playback capabilities
- Multi-modal data coordination

#### LSL Components

1. **LSLTimeSync**: High-precision time synchronization using LSL's clock
2. **LSLSensorStream**: GSR data streaming through LSL
3. **LSLDeviceCoordinator**: Multi-device coordination and command broadcasting

## Installation

### Prerequisites

For full LSL functionality, install the Lab Streaming Layer library:

```bash
pip install pylsl
```

### Alternative: Using Without LSL

The system gracefully degrades to NTP-like synchronization when LSL is not available.

## Usage

### Basic Usage

```python
from sync import EnhancedSynchronizationManager

# Create enhanced sync manager (prefers LSL if available)
sync_manager = EnhancedSynchronizationManager(prefer_lsl=True)

# Start synchronization service
success = sync_manager.start_synchronization_service()

# Get synchronized time
current_time = sync_manager.get_synchronized_time()

# Send synchronization signals
sync_manager.send_sync_signal("flash")
sync_manager.send_sync_signal("audio", {"frequency": 1000})

# Stop service
sync_manager.stop_synchronization_service()
```

### LSL-Specific Features

```python
# Register sensors for LSL streaming
sync_manager.register_sensor_for_lsl("gsr_sensor_1", "GSR")

# Push sensor data to LSL streams
sync_manager.push_sensor_data_to_lsl("gsr_sensor_1", 5.25)

# Calibrate LSL time with reference streams
sync_manager.calibrate_lsl_time_sync("reference_stream_name")

# Get comprehensive status
status = sync_manager.get_synchronization_status()
```

### GUI Integration

The enhanced synchronization is fully integrated into the main GUI:

1. **Sync Tab**: Shows both NTP and LSL status
2. **Method Selection**: Automatically displays active method
3. **LSL Controls**: 
   - "Calibrate LSL Time Sync" button
   - "Discover LSL Streams" button
4. **Real-time Status**: Shows LSL availability and stream information

## Configuration

### Synchronization Method Selection

```python
# Prefer LSL (default)
sync_manager = EnhancedSynchronizationManager(prefer_lsl=True)

# Prefer NTP-like
sync_manager = EnhancedSynchronizationManager(prefer_lsl=False)
```

### LSL Stream Configuration

- **GSR Streams**: 2 channels (GSR value + timestamp)
- **Sync Streams**: Single channel for coordination commands
- **Sampling Rate**: 128 Hz for GSR data
- **Format**: 32-bit float

## Research Benefits

### Multi-Modal Synchronization

LSL enables precise synchronization across different data modalities:
- GSR sensors (128 Hz)
- Thermal cameras (30 Hz)
- Android devices (variable rates)
- External equipment (ECG, EEG, etc.)

### Time Accuracy

- **NTP-like**: Sub-5ms accuracy for local network
- **LSL**: Sub-millisecond accuracy with hardware time sources
- **Clock Correction**: Automatic drift compensation

### Data Integration

LSL streams can be recorded and analyzed with standard research tools:
- **LabRecorder**: Record all streams simultaneously
- **MATLAB**: Real-time analysis with LSL toolbox
- **Python**: Analysis with `pylsl` library

## Troubleshooting

### LSL Not Available

```
⚠️ LSL library (pylsl) not available - install with: pip install pylsl
```

**Solution**: Install pylsl or use NTP-like synchronization

### No LSL Streams Found

```
No LSL streams found on the network
```

**Solution**: Ensure other LSL applications are running and broadcasting streams

### LSL Calibration Failed

```
LSL time synchronization calibration failed
```

**Solution**: Check for reference LSL streams on the network

## Technical Details

### LSL Stream Specifications

#### GSR Data Stream
- **Name**: `GSR_{sensor_id}`
- **Type**: `GSR`
- **Channels**: 2 (value, timestamp)
- **Rate**: 128 Hz
- **Format**: cf_float32

#### Sync Command Stream
- **Name**: `GSR_DeviceCoordinator`
- **Type**: `Commands`
- **Channels**: 1 (JSON commands)
- **Rate**: Irregular
- **Format**: cf_string

#### Time Sync Stream
- **Name**: `GSR_TimeSync`
- **Type**: `Sync`
- **Channels**: 1 (timestamps)
- **Rate**: Irregular
- **Format**: cf_float32

### Performance Characteristics

- **Latency**: < 1ms for local LSL streams
- **Throughput**: Supports 8+ concurrent GSR sensors
- **Reliability**: Automatic reconnection and error recovery
- **Scalability**: No practical limit on LSL stream count

## Integration with Shimmer GSR+ Hardware

The LSL integration works seamlessly with real Shimmer GSR+ sensors:

```python
# Register real sensor for LSL streaming
sensor_id = "shimmer_001"
sync_manager.register_sensor_for_lsl(sensor_id, "GSR")

# During data collection (from Shimmer sensor)
gsr_value = shimmer_sensor.read_gsr()
timestamp = sync_manager.get_synchronized_time()
sync_manager.push_sensor_data_to_lsl(sensor_id, gsr_value, timestamp)
```

This enables real-time GSR data streaming through LSL while maintaining compatibility with the existing Shimmer integration.

## Research Workflow Example

1. **Setup Phase**:
   - Start LSL applications (LabRecorder, analysis tools)
   - Initialize enhanced synchronization manager
   - Calibrate LSL time synchronization

2. **Recording Phase**:
   - Start synchronized recording across all devices
   - Send periodic sync signals for alignment
   - Stream GSR data through LSL in real-time

3. **Analysis Phase**:
   - Access recorded LSL data with timestamps
   - Analyze multi-modal data with preserved synchronization
   - Export results with accurate timing information

This enhanced synchronization system provides a robust foundation for contactless GSR prediction research with support for both standalone operation and integration into larger research infrastructures.