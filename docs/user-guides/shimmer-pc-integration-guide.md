# Shimmer PC Integration Guide

## Overview

This guide provides comprehensive documentation for the Python PC-side Shimmer integration, which complements the Android Shimmer implementation to provide a complete, rock-solid ecosystem for Shimmer3 GSR+ device management.

## Architecture

The Python PC integration consists of several key components:

### Core Components

1. **PCServer** (`network/pc_server.py`)
   - TCP server listening on port 9000 (configurable)
   - Handles JsonMessage protocol for Android device communication
   - Manages multiple concurrent Android device connections
   - Length-prefixed message framing for reliable data transfer

2. **AndroidDeviceManager** (`network/android_device_manager.py`)
   - Coordinates multiple Android devices
   - Manages session recording across devices
   - Handles device pairing and authentication
   - Provides unified interface for Android device control

3. **Enhanced ShimmerManager** (`shimmer_manager.py`)
   - Unified interface for both direct and Android-mediated Shimmer connections
   - Comprehensive data validation and error handling
   - Real-time data streaming and CSV recording
   - Session-based data organization

4. **ShimmerPCApplication** (`shimmer_pc_app.py`)
   - Main application demonstrating the complete integration
   - Command-line interface with session management
   - Real-time monitoring and statistics
   - Production-ready error handling

## Features

### ✅ Multi-Connection Support
- **Direct Bluetooth**: Native PC connections to Shimmer devices (planned)
- **Android-Mediated**: Shimmer data streaming through Android devices
- **Simulation Mode**: Development and testing without hardware

### ✅ Real-Time Communication
- **Bidirectional Protocol**: Commands to Android, data from Android
- **JsonMessage Format**: Standardized message protocol
- **Automatic Reconnection**: Robust connection management
- **Heartbeat Monitoring**: Connection health tracking

### ✅ Session Management
- **Coordinated Recording**: Synchronized recording across multiple devices
- **Session Metadata**: Comprehensive session information tracking
- **File Organization**: Structured data storage by session
- **Multi-Device Coordination**: Unified control of all connected devices

### ✅ Data Processing
- **Real-Time Streaming**: Live data processing and callbacks
- **Data Validation**: Sensor range checking and error detection
- **CSV Export**: Structured data storage with comprehensive sensor fields
- **Comprehensive Sensors**: GSR, PPG, Accel, Gyro, Mag, ECG, EMG support

### ✅ Synchronization
- **Flash Sync**: LED flash synchronization signals
- **Audio Beep Sync**: Audio synchronization signals
- **Timestamp Coordination**: Precise timing across devices
- **Multi-Device Sync**: Coordinated signals to all devices

## Quick Start

### 1. Installation

```bash
cd PythonApp/src
pip install -r requirements.txt  # Install dependencies when available
```

### 2. Basic Usage

```python
from shimmer_manager import ShimmerManager

# Create manager with Android integration
manager = ShimmerManager(enable_android_integration=True)

# Initialize (starts Android device server on port 9000)
if manager.initialize():
    print("Shimmer Manager ready for Android device connections")
    
    # Wait for Android devices to connect
    # Android devices will automatically appear when connected
    
    # Start session recording
    session_id = f"session_{int(time.time())}"
    manager.start_android_session(session_id, record_shimmer=True)
    
    # Record for 30 seconds
    time.sleep(30)
    
    # Stop session
    manager.stop_android_session()
    
    # Cleanup
    manager.cleanup()
```

### 3. Command Line Application

```bash
# Start the PC application
python shimmer_pc_app.py --port 9000 --log-level INFO

# Auto-start a recording session
python shimmer_pc_app.py --session-id "test_session" --duration 60

# Custom port and debug logging
python shimmer_pc_app.py --port 8080 --log-level DEBUG
```

## Android Device Connection

### 1. Android Setup
Ensure your Android device is running the Multi-Sensor Recording app with Shimmer integration enabled.

### 2. Network Configuration
Both PC and Android device must be on the same network. The Android app will connect to the PC server automatically.

### 3. Connection Process
1. Start the PC application
2. Launch Android app
3. Configure PC server IP in Android settings (if needed)
4. Android device will automatically connect and register capabilities

## Data Flow

### Real-Time Data Streaming

```
Android Device (Shimmer Connected)
    ↓ (TCP, JsonMessage Protocol)
PC Server (Port 9000)
    ↓ (Internal Callbacks)
AndroidDeviceManager
    ↓ (Data Processing)
ShimmerManager
    ↓ (Data Validation & CSV)
Application Callbacks
```

### Session Recording

```
PC Application
    ↓ (Start Session Command)
AndroidDeviceManager
    ↓ (Broadcast to Android Devices)
Android Devices
    ↓ (Begin Recording)
Real-Time Data Stream
    ↓ (Continuous Data Flow)
PC CSV Files + Application Processing
```

## Message Protocol

### PC → Android Commands

```json
{
  "type": "start_record",
  "session_id": "session_123",
  "record_video": true,
  "record_thermal": true,
  "record_shimmer": true
}

{
  "type": "flash_sync",
  "duration_ms": 200,
  "sync_id": "sync_001"
}

{
  "type": "beep_sync",
  "frequency_hz": 1000,
  "duration_ms": 200,
  "volume": 0.8
}
```

### Android → PC Data

```json
{
  "type": "hello",
  "device_id": "phone_001",
  "capabilities": ["rgb_video", "thermal", "shimmer"]
}

{
  "type": "sensor_data",
  "timestamp": 1642686000.123,
  "values": {
    "gsr_conductance": 2.5,
    "ppg_a13": 2048,
    "accel_x": 0.2,
    "accel_y": 0.1,
    "accel_z": 9.8
  }
}

{
  "type": "status",
  "battery": 85,
  "recording": true,
  "temperature": 32.5
}
```

## Configuration

### ShimmerManager Configuration

```python
manager = ShimmerManager(
    enable_android_integration=True,  # Enable Android device support
    logger=custom_logger,             # Custom logger instance
)

# Configure Android server port
manager.android_server_port = 8080

# Configure data validation ranges
manager.sensor_ranges['gsr_conductance'] = (0.0, 50.0)  # Custom GSR range
```

### PCServer Configuration

```python
server = PCServer(
    port=9000,                    # Server port
    logger=logger
)

# Configure timeouts and limits
server.heartbeat_timeout = 60.0     # Heartbeat timeout (seconds)
server.max_message_size = 2*1024*1024  # 2MB max message size
```

## Data Validation

The system includes comprehensive data validation:

### Sensor Range Checking
```python
sensor_ranges = {
    'gsr_conductance': (0.0, 100.0),   # microsiemens
    'ppg_a13': (0.0, 4095.0),          # ADC units
    'accel_x': (-16.0, 16.0),          # g
    'accel_y': (-16.0, 16.0),          # g
    'accel_z': (-16.0, 16.0),          # g
    'gyro_x': (-2000.0, 2000.0),       # degrees/sec
    'battery_percentage': (0, 100)      # percentage
}
```

### Data Quality Monitoring
- Timestamp validation
- Range checking for all sensor values
- Connection health monitoring
- Data rate monitoring

## Error Handling

### Connection Errors
- Automatic reconnection with exponential backoff
- Connection timeout handling
- Network error recovery
- Device disconnection detection

### Data Errors
- Invalid data sample filtering
- JSON parsing error handling
- Message protocol validation
- Buffer overflow protection

### Session Errors
- Session state validation
- Multi-device synchronization error handling
- File I/O error recovery
- Resource cleanup on failure

## Performance Optimization

### Threading Architecture
- Separate threads for network I/O, data processing, and file writing
- Thread pool for concurrent device handling
- Non-blocking queue operations
- Efficient memory management

### Data Processing
- Streaming data processing
- Configurable buffer sizes
- Batch CSV writing
- Memory-efficient data structures

## Monitoring and Logging

### Application Logs
```
2025-01-16 10:00:00 - ShimmerManager - INFO - Enhanced ShimmerManager initialized
2025-01-16 10:00:05 - PCServer - INFO - PC server started on port 9000
2025-01-16 10:00:10 - AndroidDeviceManager - INFO - Android device connected: phone_001
2025-01-16 10:00:15 - ShimmerManager - INFO - Device phone_001:shimmer streaming started
```

### Real-Time Statistics
- Data samples received per second
- Device connection status
- Session duration and data counts
- Error rates and recovery statistics

## Integration with Android

### Prerequisites
1. Android app with Shimmer integration (already implemented)
2. Network connectivity between PC and Android device
3. Shimmer3 GSR+ device paired with Android

### Setup Steps
1. Start PC application
2. Configure Android app with PC server IP
3. Connect Shimmer device to Android
4. Android app automatically connects to PC
5. Begin coordinated data collection

## Troubleshooting

### Common Issues

**Android device not connecting:**
- Check network connectivity
- Verify PC server is running on correct port
- Check firewall settings
- Verify Android app configuration

**No Shimmer data received:**
- Verify Shimmer device is connected to Android
- Check Android app Shimmer integration
- Verify device capabilities include "shimmer"
- Check data callback registration

**Session recording issues:**
- Verify session start command reaches Android devices
- Check file permissions for CSV output
- Verify session directory creation
- Check available disk space

### Debug Mode
Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via command line
python shimmer_pc_app.py --log-level DEBUG
```

## Extension Points

### Custom Data Processing
```python
def custom_data_callback(sample: ShimmerSample):
    # Custom processing logic
    if sample.gsr_conductance > threshold:
        trigger_alert()

manager.add_data_callback(custom_data_callback)
```

### Custom Device Events
```python
def custom_status_callback(device_id: str, status: ShimmerStatus):
    # Custom status monitoring
    update_dashboard(device_id, status)

manager.add_status_callback(custom_status_callback)
```

### Protocol Extensions
The JsonMessage protocol can be extended with new message types for custom functionality.

## Production Deployment

### Recommended Setup
- Dedicated PC for data collection
- Reliable network infrastructure
- Backup power for continuous operation
- Automated session management
- Data backup and archival

### Security Considerations
- Network encryption (future enhancement)
- Device authentication
- Data validation and sanitization
- Access control for session management

## Future Enhancements

### Planned Features
1. **Direct Bluetooth Integration**: Native PC connections to Shimmer devices
2. **Web Interface**: Browser-based control and monitoring
3. **Database Integration**: Direct database storage for large-scale studies
4. **Advanced Analytics**: Real-time signal processing and analysis
5. **Cloud Integration**: Cloud-based data storage and processing

### API Extensions
- REST API for external integration
- WebSocket for real-time web applications
- Plugin architecture for custom extensions
- Advanced synchronization protocols

## Conclusion

The Python PC-side Shimmer integration provides a robust, production-ready platform for comprehensive Shimmer device management. Combined with the Android integration, it delivers a complete ecosystem for multi-sensor data collection with professional-grade reliability and functionality.

For additional support or contributions, please refer to the project documentation and contribution guidelines.