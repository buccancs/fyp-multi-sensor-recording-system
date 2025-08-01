# DeviceClient Networking Protocol Documentation

## Overview

The DeviceClient module implements a socket-based communication protocol for connecting with Android devices running the Multi-Sensor Recording System application. This document describes the networking protocol, communication patterns, and implementation details.

## Protocol Architecture

### Connection Model
- **Server-Client Architecture**: DeviceClient acts as a server listening on a configurable port (default: 8080)
- **Multi-Device Support**: Supports multiple concurrent device connections
- **Thread-Safe Operations**: All device operations are protected by threading locks
- **PyQt Integration**: Uses PyQt signals for asynchronous GUI communication

### Network Configuration
```python
self.server_port = 8080              # Server listening port
self.buffer_size = 4096              # Socket buffer size
self.connection_timeout = 30         # Connection timeout (seconds)
self.heartbeat_interval = 5          # Heartbeat interval (seconds)
self.max_reconnect_attempts = 3      # Maximum reconnection attempts
```

## Communication Protocol

### 1. Connection Establishment

#### Handshake Protocol
When a device connects, the following handshake occurs:

**Client → Server (Handshake Request)**
```json
{
    "type": "handshake",
    "client_type": "recording_controller",
    "protocol_version": "1.0",
    "timestamp": 1638360000.123
}
```

**Server → Client (Handshake Response)**
```json
{
    "status": "accepted",
    "device_info": {
        "name": "Android Recording Device",
        "model": "Samsung Galaxy S21",
        "version": "1.0"
    },
    "capabilities": ["recording", "streaming", "calibration"]
}
```

#### Connection States
- `"connecting"`: Initial connection attempt
- `"connected"`: Successfully connected and authenticated
- `"disconnected"`: Connection closed
- `"error"`: Connection failed or encountered error

### 2. Command Protocol

Commands are sent as structured JSON messages:

**Command Message Format**
```json
{
    "type": "command",
    "command": "START",
    "parameters": {
        "mode": "recording",
        "duration": 300,
        "sensors": ["GSR", "thermal"]
    },
    "timestamp": 1638360000.123,
    "message_id": "0_1638360000123"
}
```

#### Supported Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `START` | Start recording session | `mode`, `duration`, `sensors` |
| `STOP` | Stop current recording | None |
| `CALIBRATE` | Calibrate sensors | `sensor`, `type` |
| `STATUS` | Request device status | None |
| `PING` | Connection test | None |

**Example Commands:**

Start Recording:
```json
{
    "type": "command",
    "command": "START",
    "parameters": {
        "mode": "recording",
        "duration": 300,
        "sensors": ["GSR", "thermal", "camera"]
    }
}
```

Calibrate GSR Sensor:
```json
{
    "type": "command", 
    "command": "CALIBRATE",
    "parameters": {
        "sensor": "GSR",
        "type": "baseline"
    }
}
```

### 3. Data Streaming

#### Frame Reception
Devices can send various types of data frames:

**Frame Message Format**
```json
{
    "type": "frame",
    "frame_type": "thermal_image",
    "timestamp": 1638360000.123,
    "sequence_number": 1234,
    "data": "<base64_encoded_data>",
    "metadata": {
        "width": 640,
        "height": 480,
        "format": "RGB",
        "sensor_id": "thermal_cam_1"
    }
}
```

#### Supported Frame Types
- `"thermal_image"`: Thermal camera frames
- `"rgb_image"`: RGB camera frames  
- `"gsr_data"`: GSR sensor readings
- `"audio_data"`: Audio recordings
- `"sensor_data"`: Generic sensor data

### 4. Status Updates

Devices periodically send status information:

**Status Message Format**
```json
{
    "type": "status",
    "timestamp": 1638360000.123,
    "device_status": "recording",
    "battery_level": 85,
    "sensors": {
        "GSR": {
            "status": "active",
            "sample_rate": 1000,
            "last_reading": 0.5
        },
        "thermal": {
            "status": "active", 
            "temperature": 25.3
        }
    },
    "storage": {
        "available_mb": 1024,
        "used_mb": 256
    }
}
```

### 5. Heartbeat and Connection Monitoring

#### Heartbeat Protocol
Devices send periodic heartbeat messages:

```json
{
    "type": "heartbeat",
    "timestamp": 1638360000.123,
    "device_id": "android_device_001"
}
```

#### Connection Monitoring
- DeviceClient monitors each device in a separate thread
- Heartbeat messages update the `last_heartbeat` timestamp
- Failed connections are automatically cleaned up

### 6. Disconnection Protocol

#### Graceful Disconnection
**Client → Server (Disconnect Notification)**
```json
{
    "type": "disconnect",
    "reason": "client_initiated",
    "timestamp": 1638360000.123
}
```

#### Disconnect Reasons
- `"client_initiated"`: User-requested disconnection
- `"server_shutdown"`: Server shutting down
- `"network_error"`: Network connectivity lost
- `"protocol_error"`: Protocol violation

## Implementation Details

### DeviceClient Class Structure

```python
class DeviceClient(QThread):
    # PyQt Signals
    device_connected = pyqtSignal(int, str)
    device_disconnected = pyqtSignal(int)
    frame_received = pyqtSignal(int, str, bytes)
    status_updated = pyqtSignal(int, dict)
    error_occurred = pyqtSignal(str)
```

### Key Methods

#### Connection Management
- `connect_to_device(ip, port)` - Connect to specific device
- `disconnect_device(device_index)` - Disconnect device
- `handle_device_connection(socket, address)` - Handle incoming connections

#### Communication
- `send_command(device_index, command, parameters)` - Send command to device
- `_process_device_message(device_id, message)` - Process incoming messages

#### Monitoring
- `_monitor_device(device_id)` - Monitor device in separate thread
- `get_connected_devices()` - Get list of connected devices

### Thread Safety

All device operations use threading locks:
```python
self._device_lock = threading.Lock()

with self._device_lock:
    # Thread-safe device operations
    device = self.devices[device_id]
```

### Error Handling

Comprehensive error handling with specific error types:
- Connection errors (timeout, refused, unreachable)
- Protocol errors (invalid JSON, missing fields)
- Network errors (socket failures, disconnections)
- Authentication errors (handshake failures)

### Device Information Storage

Each connected device stores:
```python
device_info = {
    'socket': socket_object,
    'ip': '192.168.1.100',
    'port': 8080,
    'status': 'connected',
    'last_heartbeat': 1638360000.123,
    'connected_at': 1638359000.000,
    'device_info': {...},
    'capabilities': [...]
}
```

## Usage Examples

### Basic Connection
```python
from PythonApp.src.network.device_client import DeviceClient

client = DeviceClient()
client.device_connected.connect(on_device_connected)
client.error_occurred.connect(on_error)

# Start server
client.start()

# Connect to device
success = client.connect_to_device("192.168.1.100", 8080)
```

### Sending Commands
```python
# Start recording
success = client.send_command(0, "START", {
    "mode": "recording",
    "duration": 300
})

# Calibrate sensor
success = client.send_command(0, "CALIBRATE", {
    "sensor": "GSR"
})
```

### Monitoring Devices
```python
devices = client.get_connected_devices()
for device_id, info in devices.items():
    print(f"Device {device_id}: {info['ip']} - {info['status']}")
```

## Security Considerations

### Authentication
- Basic handshake protocol for device identification
- TODO: Implement certificate-based authentication for production
- TODO: Add device whitelisting capabilities

### Network Security
- Server binds to configurable interface (default: all interfaces)
- TODO: Add SSL/TLS encryption for sensitive data
- TODO: Implement rate limiting and DoS protection

## Performance Characteristics

### Scalability
- Supports multiple concurrent device connections
- Each device monitored in separate thread
- Non-blocking socket operations with timeouts

### Resource Usage
- Memory: ~1KB per connected device
- CPU: Minimal overhead per device
- Network: Depends on frame streaming frequency

### Latency
- Command sending: < 10ms typical
- Heartbeat interval: 5 seconds configurable
- Connection timeout: 30 seconds configurable

## Future Enhancements

### Protocol Extensions
- [ ] Implement acknowledgment system for reliable delivery
- [ ] Add compression for large data frames
- [ ] Support for device capability negotiation
- [ ] Real-time streaming protocol optimization

### Security Improvements
- [ ] SSL/TLS encryption
- [ ] Certificate-based authentication
- [ ] Device whitelisting and blacklisting
- [ ] Audit logging

### Performance Optimizations
- [ ] Connection pooling
- [ ] Async/await pattern implementation
- [ ] Message queuing for high-throughput scenarios
- [ ] Adaptive heartbeat intervals

## Troubleshooting

### Common Issues

**Connection Refused**
- Check if device application is running
- Verify network connectivity
- Confirm port numbers match

**Handshake Timeout**  
- Increase connection timeout
- Check device compatibility
- Verify protocol version match

**Frame Reception Issues**
- Monitor network bandwidth
- Check buffer size configuration
- Verify frame format compatibility

### Debug Logging

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Debug messages include:
- Connection attempts and results
- Command sending and responses  
- Frame reception details
- Error conditions and cleanup

## Testing

### Unit Tests
Comprehensive test suite in `test_device_client.py`:
- Connection management tests
- Command protocol tests
- Error handling tests
- Multi-device tests

### Integration Tests
End-to-end testing with mock Android device:
- Real socket communication
- Protocol compliance verification
- Performance testing

### Load Testing
TODO: Implement load testing for multiple concurrent devices