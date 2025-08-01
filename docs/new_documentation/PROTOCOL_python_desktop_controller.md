# Python Desktop Controller Application - Protocol Documentation

## Overview

This document defines the data contracts, network protocols, and API specifications for the Python Desktop Controller Application. The controller communicates with Android devices via JSON over TCP sockets and manages USB devices through native system APIs.

## Network Communication Protocol

### JSON Socket Protocol

The primary communication method between the Python Desktop Controller and Android devices uses JSON messages over TCP sockets.

#### Connection Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Protocol | TCP | Reliable connection-oriented protocol |
| Port | 9000 | Default server port (configurable) |
| Message Format | JSON | Human-readable structured data |
| Encoding | UTF-8 | Unicode text encoding |
| Max Message Size | 10MB | Maximum single message size |
| Connection Timeout | 30 seconds | Initial connection timeout |
| Keep-Alive | 60 seconds | Heartbeat interval |

#### Message Structure

All messages follow a consistent JSON structure:

```json
{
  "message_type": "string",
  "timestamp": "ISO8601_timestamp", 
  "device_id": "unique_device_identifier",
  "session_id": "session_identifier",
  "sequence": 123,
  "payload": {
    // Message-specific data
  },
  "checksum": "optional_data_integrity_check"
}
```

**Common Fields:**

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `message_type` | String | Yes | Type of message (see Message Types below) |
| `timestamp` | String | Yes | ISO8601 timestamp when message was created |
| `device_id` | String | Yes | Unique identifier for the sending/receiving device |
| `session_id` | String | No | Session identifier for recording sessions |
| `sequence` | Integer | No | Message sequence number for ordering |
| `payload` | Object | Yes | Message-specific data payload |
| `checksum` | String | No | MD5 hash for data integrity verification |

### Message Types

#### Device Registration and Handshake

**Device Connect Request**
```json
{
  "message_type": "device_connect",
  "timestamp": "2025-01-31T14:30:00.000Z",
  "device_id": "android_device_001",
  "payload": {
    "device_name": "Samsung Galaxy S22",
    "app_version": "3.1.0",
    "capabilities": [
      "camera_recording",
      "thermal_imaging",
      "shimmer_sensors",
      "preview_streaming"
    ],
    "device_info": {
      "manufacturer": "Samsung",
      "model": "SM-G991B",
      "android_version": "14",
      "api_level": 34,
      "storage_available": 50000000000,
      "battery_level": 85
    }
  }
}
```

**Device Connect Response**
```json
{
  "message_type": "device_connect_response", 
  "timestamp": "2025-01-31T14:30:00.100Z",
  "device_id": "pc_controller",
  "payload": {
    "status": "accepted",
    "assigned_device_id": "android_device_001",
    "server_capabilities": [
      "session_management",
      "multi_device_coordination", 
      "usb_webcam_recording",
      "calibration_services"
    ],
    "server_info": {
      "controller_version": "3.1.0",
      "supported_protocols": ["json_socket_v1"],
      "max_devices": 8,
      "recording_formats": ["mp4", "mov", "csv", "json"]
    }
  }
}
```

#### Session Management

**Start Recording Command**
```json
{
  "message_type": "start_recording",
  "timestamp": "2025-01-31T14:35:00.000Z", 
  "device_id": "pc_controller",
  "session_id": "session_20250131_143500",
  "payload": {
    "session_name": "Experiment_1_Participant_A",
    "recording_parameters": {
      "duration": 300,
      "video_resolution": "1920x1080",
      "frame_rate": 30,
      "enable_thermal": true,
      "enable_shimmer": true,
      "recording_quality": "high"
    },
    "synchronization": {
      "sync_timestamp": "2025-01-31T14:35:10.000Z",
      "countdown_duration": 10
    }
  }
}
```

**Recording Status Update**
```json
{
  "message_type": "recording_status",
  "timestamp": "2025-01-31T14:35:30.000Z",
  "device_id": "android_device_001", 
  "session_id": "session_20250131_143500",
  "sequence": 30,
  "payload": {
    "status": "recording",
    "recording_time": 30.5,
    "frames_recorded": 915,
    "file_size": 25600000,
    "storage_remaining": 49975000000,
    "battery_level": 84,
    "errors": []
  }
}
```

**Stop Recording Command**
```json
{
  "message_type": "stop_recording",
  "timestamp": "2025-01-31T14:40:00.000Z",
  "device_id": "pc_controller", 
  "session_id": "session_20250131_143500",
  "payload": {
    "stop_reason": "user_requested",
    "finalize_files": true,
    "upload_data": false
  }
}
```

#### Real-time Monitoring

**Device Status Update**
```json
{
  "message_type": "device_status",
  "timestamp": "2025-01-31T14:32:00.000Z",
  "device_id": "android_device_001",
  "payload": {
    "connection_status": "connected",
    "battery_level": 85,
    "storage_available": 50000000000,
    "memory_usage": 60,
    "cpu_usage": 25,
    "network_quality": "excellent",
    "camera_status": "ready", 
    "thermal_camera_status": "ready",
    "shimmer_status": "connected",
    "location": {
      "latitude": 47.6062,
      "longitude": -122.3321,
      "accuracy": 10
    }
  }
}
```

**Preview Frame Stream**
```json
{
  "message_type": "preview_frame",
  "timestamp": "2025-01-31T14:33:00.000Z",
  "device_id": "android_device_001",
  "sequence": 1000,
  "payload": {
    "frame_type": "rgb_camera",
    "frame_number": 1000,
    "frame_timestamp": "2025-01-31T14:33:00.000Z",
    "image_data": "base64_encoded_jpeg_data",
    "image_format": "jpeg",
    "image_size": {
      "width": 640,
      "height": 480
    },
    "compression_quality": 80
  }
}
```

#### Error Handling

**Error Notification**
```json
{
  "message_type": "error",
  "timestamp": "2025-01-31T14:36:00.000Z", 
  "device_id": "android_device_001",
  "session_id": "session_20250131_143500",
  "payload": {
    "error_code": "CAMERA_ACCESS_DENIED",
    "error_message": "Unable to access camera: Permission denied",
    "severity": "high",
    "recoverable": false,
    "suggested_action": "Grant camera permission in Android settings",
    "error_context": {
      "component": "camera_recorder",
      "operation": "start_recording",
      "timestamp": "2025-01-31T14:36:00.000Z"
    }
  }
}
```

**Heartbeat/Keep-Alive**
```json
{
  "message_type": "heartbeat",
  "timestamp": "2025-01-31T14:34:00.000Z",
  "device_id": "android_device_001", 
  "payload": {
    "status": "alive",
    "uptime": 300,
    "last_activity": "2025-01-31T14:33:55.000Z"
  }
}
```

## USB Device Integration

### Webcam Control Protocol

The Python Desktop Controller interfaces with USB webcams through OpenCV and platform-specific APIs.

#### Webcam Device Information

```python
{
  "device_id": "usb_webcam_001",
  "device_name": "Logitech BRIO 4K",
  "device_path": "/dev/video0",  # Linux
  "device_index": 0,             # Windows DirectShow index
  "capabilities": {
    "max_resolution": "3840x2160",
    "supported_formats": ["MJPG", "YUV2", "H264"],
    "frame_rates": [15, 30, 60],
    "has_audio": false,
    "auto_focus": true,
    "auto_exposure": true
  },
  "current_settings": {
    "resolution": "1920x1080", 
    "frame_rate": 30,
    "format": "MJPG",
    "brightness": 128,
    "contrast": 128,
    "saturation": 128
  }
}
```

#### Webcam Control Commands

**Start Recording**
```python
{
  "command": "start_recording",
  "device_id": "usb_webcam_001",
  "parameters": {
    "output_file": "/path/to/session/webcam_001.mp4",
    "resolution": "1920x1080",
    "frame_rate": 30,
    "codec": "h264",
    "quality": "high"
  }
}
```

**Stop Recording**
```python
{
  "command": "stop_recording",
  "device_id": "usb_webcam_001",
  "finalize": true
}
```

## File System Data Formats

### Session Directory Structure

Each recording session creates a structured directory containing all recorded data:

```
recordings/
└── session_20250131_143500/
    ├── session_metadata.json
    ├── android_device_001/
    │   ├── camera_video.mp4
    │   ├── thermal_data.bin
    │   ├── thermal_metadata.json
    │   ├── shimmer_data.csv
    │   └── device_log.txt
    ├── android_device_002/
    │   └── [similar structure]
    ├── usb_webcam_001/
    │   ├── webcam_video.mp4
    │   └── webcam_metadata.json
    ├── usb_webcam_002/
    │   └── [similar structure]
    ├── calibration_data/
    │   ├── calibration_results.json
    │   └── calibration_images/
    └── session_logs/
        ├── controller_log.txt
        ├── network_log.txt
        └── error_log.txt
```

### Session Metadata Format

**session_metadata.json**
```json
{
  "session_info": {
    "session_id": "session_20250131_143500",
    "session_name": "Experiment_1_Participant_A",
    "start_time": "2025-01-31T14:35:00.000Z",
    "end_time": "2025-01-31T14:40:00.000Z",
    "duration": 300.0,
    "researcher": "Dr. Smith",
    "experiment_id": "EXP_2025_001"
  },
  "devices": [
    {
      "device_id": "android_device_001",
      "device_type": "android_smartphone",
      "device_name": "Samsung Galaxy S22",
      "recording_status": "completed",
      "files_recorded": [
        "camera_video.mp4",
        "thermal_data.bin", 
        "shimmer_data.csv"
      ],
      "recording_stats": {
        "video_duration": 300.0,
        "video_frames": 9000,
        "thermal_frames": 3000,
        "shimmer_samples": 30000
      }
    }
  ],
  "recording_parameters": {
    "video_resolution": "1920x1080",
    "video_frame_rate": 30,
    "thermal_frame_rate": 10,
    "shimmer_sampling_rate": 100,
    "recording_quality": "high"
  },
  "synchronization": {
    "master_clock": "pc_controller",
    "sync_accuracy": 0.001,
    "time_reference": "utc"
  },
  "quality_metrics": {
    "dropped_frames": 0,
    "network_interruptions": 0,
    "sync_errors": 0,
    "data_integrity": "verified"
  }
}
```

### Video File Metadata

**webcam_metadata.json**
```json
{
  "file_info": {
    "filename": "webcam_video.mp4",
    "file_size": 156234567,
    "creation_time": "2025-01-31T14:35:00.000Z",
    "duration": 300.0,
    "checksum": "a1b2c3d4e5f6g7h8i9j0"
  },
  "video_properties": {
    "resolution": "1920x1080",
    "frame_rate": 30.0,
    "codec": "h264",
    "bitrate": 4000000,
    "color_space": "yuv420p",
    "total_frames": 9000
  },
  "recording_device": {
    "device_id": "usb_webcam_001",
    "device_name": "Logitech BRIO 4K",
    "driver_version": "1.2.3",
    "firmware_version": "2.4.6"
  },
  "calibration_applied": {
    "calibrated": true,
    "calibration_date": "2025-01-31T10:00:00.000Z",
    "distortion_corrected": true,
    "calibration_error": 0.15
  }
}
```

### Sensor Data Formats

**Shimmer GSR Data (shimmer_data.csv)**
```csv
timestamp,gsr_raw,gsr_kohms,skin_temp_celsius,accelerometer_x,accelerometer_y,accelerometer_z
2025-01-31T14:35:00.000Z,2048,150.5,32.1,0.98,-0.15,0.12
2025-01-31T14:35:00.010Z,2052,149.8,32.1,0.97,-0.14,0.13
2025-01-31T14:35:00.020Z,2055,149.2,32.2,0.96,-0.13,0.14
```

**Thermal Camera Data (thermal_metadata.json)**
```json
{
  "thermal_recording": {
    "file_format": "binary",
    "data_file": "thermal_data.bin",
    "frame_count": 3000,
    "frame_rate": 10.0,
    "resolution": "256x192",
    "temperature_range": {
      "min": 15.0,
      "max": 45.0
    },
    "calibration": {
      "emissivity": 0.95,
      "ambient_temp": 22.5,
      "distance": 0.5
    }
  },
  "binary_format": {
    "bytes_per_pixel": 2,
    "data_type": "uint16",
    "byte_order": "little_endian",
    "temperature_scale": 0.01,
    "temperature_offset": -273.15
  }
}
```

## API Reference

### Python Desktop Controller Internal APIs

#### Session Management API

```python
class SessionManager:
    def create_session(self, session_name: str, parameters: dict) -> str:
        """Create a new recording session"""
        
    def start_recording(self, session_id: str) -> bool:
        """Start recording for all connected devices"""
        
    def stop_recording(self, session_id: str) -> bool:
        """Stop recording and finalize session"""
        
    def get_session_status(self, session_id: str) -> dict:
        """Get current session status and statistics"""
        
    def get_session_list(self) -> List[dict]:
        """Get list of all recorded sessions"""
```

#### Device Management API  

```python
class DeviceManager:
    def discover_devices(self) -> List[dict]:
        """Discover available devices on network"""
        
    def connect_device(self, device_info: dict) -> bool:
        """Connect to a specific device"""
        
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a device"""
        
    def get_device_status(self, device_id: str) -> dict:
        """Get current device status"""
        
    def send_command(self, device_id: str, command: dict) -> dict:
        """Send command to device and wait for response"""
```

#### Webcam Control API

```python
class WebcamManager:
    def list_cameras(self) -> List[dict]:
        """List all available USB cameras"""
        
    def open_camera(self, camera_id: str, settings: dict) -> bool:
        """Open camera with specified settings"""
        
    def start_recording(self, camera_id: str, output_file: str) -> bool:
        """Start recording to file"""
        
    def stop_recording(self, camera_id: str) -> bool:
        """Stop recording and close file"""
        
    def get_frame(self, camera_id: str) -> numpy.ndarray:
        """Get single frame for preview"""
```

## Logging and Monitoring Protocols

### Log Message Format

**Structured Log Entry:**
```json
{
    "timestamp": "2024-01-31T10:30:45.123Z",
    "level": "INFO",
    "category": "session",
    "component": "SessionManager",
    "message": "Recording session started",
    "context": {
        "session_id": "session_20240131_103045",
        "device_count": 3,
        "duration_planned": 300
    },
    "metadata": {
        "thread_id": "main",
        "process_id": 1234,
        "memory_usage_mb": 256
    }
}
```

**Log Categories and Levels:**

| Category | Description | Typical Levels |
|----------|-------------|----------------|
| `session` | Session management operations | INFO, ERROR |
| `device` | Device communication events | DEBUG, INFO, WARNING |
| `network` | Network protocol messages | DEBUG, INFO, ERROR |
| `camera` | Camera operations and status | INFO, WARNING, ERROR |
| `calibration` | Calibration procedures | INFO, ERROR |
| `performance` | Performance metrics | DEBUG, INFO |
| `security` | Security and permissions | WARNING, ERROR, CRITICAL |

### Performance Monitoring

**Performance Metrics Protocol:**
```json
{
    "timestamp": "2024-01-31T10:30:45.123Z",
    "metrics": {
        "cpu_usage_percent": 45.2,
        "memory_usage_mb": 1024,
        "network_bandwidth_mbps": 12.5,
        "disk_usage_percent": 67.8,
        "active_devices": 3,
        "recording_fps": 30.0
    },
    "thresholds": {
        "cpu_warning": 80.0,
        "memory_warning": 2048,
        "disk_warning": 85.0
    }
}
```

**Status Monitoring Protocol:**
```json
{
    "type": "status_update",
    "timestamp": "2024-01-31T10:30:45.123Z",
    "component": "device_manager",
    "status": {
        "overall_health": "healthy",
        "device_count": 3,
        "devices": {
            "android_001": {
                "status": "recording",
                "connection_quality": "excellent",
                "battery_level": 85,
                "storage_available_gb": 12.5
            },
            "webcam_001": {
                "status": "recording",
                "fps": 30.0,
                "resolution": "1920x1080"
            }
        }
    }
}
```

## Error Codes and Handling

### Network Error Codes

| Error Code | Description | Severity | Recovery Action |
|------------|-------------|----------|-----------------|
| NET_001 | Connection timeout | Medium | Retry connection |
| NET_002 | Connection lost during recording | High | Resume or restart session |
| NET_003 | Invalid message format | Low | Log and ignore message |
| NET_004 | Message checksum failure | Medium | Request retransmission |
| NET_005 | Port already in use | High | Change port or stop conflicting service |

### Device Error Codes

| Error Code | Description | Severity | Recovery Action |
|------------|-------------|----------|-----------------|
| DEV_001 | Camera access denied | High | Check permissions |
| DEV_002 | Storage full | Critical | Free space or change location |
| DEV_003 | Battery critically low | High | Connect charger |
| DEV_004 | Sensor connection failed | Medium | Reconnect sensor |
| DEV_005 | Recording format not supported | Medium | Change format settings |

### Session Error Codes

| Error Code | Description | Severity | Recovery Action |
|------------|-------------|----------|-----------------|
| SES_001 | Session already exists | Low | Use different name |
| SES_002 | Invalid session parameters | Medium | Correct parameters |
| SES_003 | No devices available | High | Connect devices |
| SES_004 | Recording failed to start | High | Check device status |
| SES_005 | Data corruption detected | Critical | Stop session and investigate |

## Protocol Versioning

### Version Compatibility

The JSON socket protocol supports versioning for backward compatibility:

```json
{
  "protocol_version": "1.0",
  "min_supported_version": "1.0",
  "max_supported_version": "1.2"
}
```

### Version History

| Version | Release Date | Major Changes |
|---------|--------------|---------------|
| 1.0 | 2025-01-01 | Initial protocol specification |
| 1.1 | 2025-02-01 | Added thermal camera support |
| 1.2 | 2025-03-01 | Enhanced error handling and recovery |

## Security Considerations

### Network Security

1. **Local Network Only**: Protocol designed for local network use only
2. **No Authentication**: Devices trust each other on local network
3. **Data Validation**: All messages validated for format and content
4. **Rate Limiting**: Protection against message flooding

### Data Security

1. **Local Storage**: All data stored locally by default
2. **File Permissions**: Restricted access to session directories  
3. **Data Integrity**: Checksums for all recorded files
4. **Privacy**: No personal data transmitted unless explicitly configured

## Protocol Extensions

### Custom Message Types

Developers can extend the protocol with custom message types:

```json
{
  "message_type": "custom_experiment_marker",
  "timestamp": "2025-01-31T14:36:00.000Z",
  "device_id": "android_device_001",
  "payload": {
    "marker_type": "stimulus_onset",
    "stimulus_id": "visual_cue_001",
    "marker_time": "2025-01-31T14:36:00.000Z"
  }
}
```

### Plugin Architecture

The controller supports plugins for custom functionality:

```python
class CustomPlugin:
    def handle_message(self, message: dict) -> dict:
        """Handle custom message type"""
        
    def process_data(self, session_data: dict) -> dict:
        """Post-process session data"""
```

This protocol documentation provides the complete specification for all data contracts and communication interfaces used by the Python Desktop Controller Application.