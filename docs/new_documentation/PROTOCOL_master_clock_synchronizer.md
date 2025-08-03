# Master Clock Synchronizer - Protocol Specification

## Table of Contents

- [Overview](#overview)
- [Data Structures](#data-structures)
  - [Core Synchronization Classes](#core-synchronization-classes)
  - [Device Status Models](#device-status-models)
  - [Session Management Models](#session-management-models)
- [JSON Message Protocol](#json-message-protocol)
  - [Synchronization Messages](#synchronization-messages)
  - [Recording Control Messages](#recording-control-messages)
  - [Status and Monitoring Messages](#status-and-monitoring-messages)
- [API Reference](#api-reference)
  - [MasterClockSynchronizer Public Interface](#masterclocksynchronizer-public-interface)
  - [Callback Interfaces](#callback-interfaces)
  - [Utility Functions](#utility-functions)
- [Network Protocol Specifications](#network-protocol-specifications)
  - [NTP Server Protocol](#ntp-server-protocol)
  - [PC Server Communication](#pc-server-communication)
  - [Device Registration Protocol](#device-registration-protocol)
- [Integration Contracts](#integration-contracts)
  - [Webcam Controller Integration](#webcam-controller-integration)
  - [Android Device Integration](#android-device-integration)
  - [Session Manager Integration](#session-manager-integration)
- [Configuration Schema](#configuration-schema)
  - [Synchronization Parameters](#synchronization-parameters)
  - [Quality Thresholds](#quality-thresholds)
  - [Network Configuration](#network-configuration)
- [Event Schemas](#event-schemas)
  - [Device Events](#device-events)
  - [Session Events](#session-events)
  - [Quality Events](#quality-events)
- [Error Handling Protocol](#error-handling-protocol)
  - [Error Classifications](#error-classifications)
  - [Recovery Procedures](#recovery-procedures)
  - [Logging Standards](#logging-standards)

## Overview

This document defines the complete protocol specification for the Master Clock Synchronizer component, including data contracts, API interfaces, network protocols, and integration requirements. All components interacting with the synchronization system must adhere to these specifications.

## Data Structures

### Core Synchronization Classes

#### SyncStatus

Represents the synchronization status of a connected device.

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `device_id` | `str` | Yes | Unique identifier for the device |
| `device_type` | `str` | Yes | Type of device ('android', 'webcam1', 'webcam2') |
| `is_synchronized` | `bool` | Yes | Whether device is currently synchronized |
| `time_offset_ms` | `float` | Yes | Time offset from master clock in milliseconds |
| `last_sync_time` | `float` | Yes | Unix timestamp of last successful synchronization |
| `sync_quality` | `float` | Yes | Synchronization quality score (0.0 to 1.0) |
| `recording_active` | `bool` | Yes | Whether device is currently recording |
| `frame_count` | `int` | Yes | Current frame count for validation |

**Example JSON:**
```json
{
  "device_id": "Samsung_Galaxy_S21",
  "device_type": "android",
  "is_synchronized": true,
  "time_offset_ms": 12.3,
  "last_sync_time": 1644859200.123456,
  "sync_quality": 0.92,
  "recording_active": true,
  "frame_count": 1250
}
```

#### SyncCommand

Command structure for coordinated synchronization operations.

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `command_type` | `str` | Yes | Command type ('start_record', 'stop_record', 'sync_timestamp') |
| `session_id` | `str` | Yes | Unique session identifier |
| `master_timestamp` | `float` | Yes | Master clock timestamp for coordination |
| `target_devices` | `List[str]` | Yes | List of device IDs to target |
| `sync_tolerance_ms` | `float` | No | Maximum allowed synchronization difference (default: 50.0) |

**Example JSON:**
```json
{
  "command_type": "start_record",
  "session_id": "experiment_1644859200",
  "master_timestamp": 1644859200.123456,
  "target_devices": ["Samsung_Galaxy_S21", "Pixel_6_Pro"],
  "sync_tolerance_ms": 25.0
}
```

#### RecordingSession

Information about an active or completed recording session.

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `session_id` | `str` | Yes | Unique session identifier |
| `start_timestamp` | `float` | Yes | Unix timestamp when session started |
| `devices` | `Set[str]` | Yes | Set of device IDs participating in session |
| `webcam_files` | `Dict[str, str]` | Yes | Mapping of webcam ID to output file path |
| `android_files` | `Dict[str, List[str]]` | Yes | Mapping of device ID to list of output files |
| `is_active` | `bool` | Yes | Whether session is currently active |
| `sync_quality` | `float` | Yes | Overall session synchronization quality |

**Example JSON:**
```json
{
  "session_id": "experiment_1644859200",
  "start_timestamp": 1644859200.123456,
  "devices": ["Samsung_Galaxy_S21", "Pixel_6_Pro", "webcam1"],
  "webcam_files": {
    "webcam1": "/recordings/webcam1_1644859200.mp4"
  },
  "android_files": {
    "Samsung_Galaxy_S21": [
      "/recordings/samsung_video_1644859200.mp4",
      "/recordings/samsung_thermal_1644859200.bin"
    ]
  },
  "is_active": true,
  "sync_quality": 0.89
}
```

### Device Status Models

#### ConnectedDevice

Extended device information for network-connected devices.

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `device_id` | `str` | Yes | Unique device identifier |
| `capabilities` | `List[str]` | Yes | List of device capabilities |
| `connection_time` | `float` | Yes | Unix timestamp when device connected |
| `last_heartbeat` | `float` | Yes | Last heartbeat/ping timestamp |
| `status` | `Dict[str, Any]` | Yes | Current device status information |
| `network_info` | `Dict[str, str]` | No | Network connection information |

#### DeviceCapabilities

Standardized capability identifiers for devices.

| Capability | Description | Applicable Devices |
|------------|-------------|-------------------|
| `video_recording` | RGB video recording capability | Android devices |
| `thermal_recording` | Thermal camera recording | Android devices with thermal camera |
| `shimmer_recording` | Shimmer sensor data collection | Android devices with Shimmer |
| `audio_recording` | Audio recording capability | Android devices |
| `webcam_sync` | Webcam synchronization support | PC webcams |

### Session Management Models

#### SessionConfiguration

Configuration parameters for recording sessions.

| Field Name | Data Type | Required | Default | Description |
|------------|-----------|----------|---------|-------------|
| `record_video` | `bool` | No | `true` | Enable video recording |
| `record_thermal` | `bool` | No | `true` | Enable thermal recording |
| `record_shimmer` | `bool` | No | `false` | Enable Shimmer sensor recording |
| `record_audio` | `bool` | No | `false` | Enable audio recording |
| `video_resolution` | `str` | No | `"1080p"` | Video recording resolution |
| `video_fps` | `int` | No | `30` | Video frames per second |
| `thermal_fps` | `int` | No | `30` | Thermal camera frames per second |

## JSON Message Protocol

### Synchronization Messages

#### Sync Timestamp Message

Initiates time synchronization with a device.

**Message Type:** `sync_timestamp`

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `type` | `str` | Yes | Always "sync_timestamp" |
| `timestamp` | `float` | Yes | Master clock timestamp |
| `sequence_number` | `int` | No | Sequence number for tracking |
| `precision_ms` | `float` | No | Estimated timestamp precision |

**Example:**
```json
{
  "type": "sync_timestamp",
  "timestamp": 1644859200.123456,
  "sequence_number": 42,
  "precision_ms": 1.0
}
```

#### Sync Response Message

Response from device acknowledging timestamp synchronization.

**Message Type:** `sync_response`

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `type` | `str` | Yes | Always "sync_response" |
| `timestamp` | `float` | Yes | Device timestamp when received |
| `master_timestamp` | `float` | Yes | Received master timestamp |
| `sequence_number` | `int` | No | Matching sequence number |
| `device_time` | `float` | Yes | Device's current time |

**Example:**
```json
{
  "type": "sync_response",
  "timestamp": 1644859200.125890,
  "master_timestamp": 1644859200.123456,
  "sequence_number": 42,
  "device_time": 1644859200.125123
}
```

### Recording Control Messages

#### Start Record Command

Initiates synchronized recording on target devices.

**Message Type:** `start_record`

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `type` | `str` | Yes | Always "start_record" |
| `session_id` | `str` | Yes | Unique session identifier |
| `timestamp` | `float` | Yes | Master timestamp for recording start |
| `record_video` | `bool` | No | Enable video recording (default: true) |
| `record_thermal` | `bool` | No | Enable thermal recording (default: true) |
| `record_shimmer` | `bool` | No | Enable Shimmer recording (default: false) |
| `config` | `Dict` | No | Additional recording configuration |

**Example:**
```json
{
  "type": "start_record",
  "session_id": "experiment_1644859200",
  "timestamp": 1644859200.123456,
  "record_video": true,
  "record_thermal": true,
  "record_shimmer": false,
  "config": {
    "video_resolution": "1080p",
    "video_fps": 30
  }
}
```

#### Stop Record Command

Stops synchronized recording on target devices.

**Message Type:** `stop_record`

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `type` | `str` | Yes | Always "stop_record" |
| `session_id` | `str` | No | Session identifier (if applicable) |
| `timestamp` | `float` | Yes | Master timestamp for recording stop |
| `save_files` | `bool` | No | Whether to save recorded files (default: true) |

**Example:**
```json
{
  "type": "stop_record",
  "session_id": "experiment_1644859200",
  "timestamp": 1644859202.654321,
  "save_files": true
}
```

### Status and Monitoring Messages

#### Device Status Message

Regular status update from connected devices.

**Message Type:** `device_status`

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `type` | `str` | Yes | Always "device_status" |
| `device_id` | `str` | Yes | Device identifier |
| `timestamp` | `float` | Yes | Device timestamp |
| `battery_level` | `float` | No | Battery percentage (0.0-1.0) |
| `cpu_usage` | `float` | No | CPU usage percentage |
| `memory_usage` | `float` | No | Memory usage percentage |
| `recording_status` | `Dict` | No | Current recording status |
| `sync_status` | `Dict` | No | Synchronization status |

#### Heartbeat Message

Periodic connectivity check message.

**Message Type:** `heartbeat`

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| `type` | `str` | Yes | Always "heartbeat" |
| `timestamp` | `float` | Yes | Device timestamp |
| `sequence_number` | `int` | Yes | Incremental sequence number |

## API Reference

### MasterClockSynchronizer Public Interface

#### Constructor

```python
def __init__(self, 
             ntp_port: int = 8889,
             pc_server_port: int = 9000,
             sync_interval: float = 5.0,
             logger_instance: Optional[logging.Logger] = None)
```

**Parameters:**
- `ntp_port`: Port number for NTP time server
- `pc_server_port`: Port number for PC server communication
- `sync_interval`: Interval between synchronization checks (seconds)
- `logger_instance`: Optional logger instance

#### Core Methods

##### start() -> bool

Starts the master clock synchronization system.

**Returns:** `bool` - True if started successfully, False otherwise

**Raises:** `Exception` - If startup fails

##### stop() -> None

Stops the master clock synchronization system and cleans up resources.

##### get_master_timestamp() -> float

Returns the current master clock timestamp.

**Returns:** `float` - Unix timestamp with microsecond precision

##### start_synchronized_recording(session_id: str, target_devices: Optional[List[str]] = None, record_video: bool = True, record_thermal: bool = True, record_shimmer: bool = False) -> bool

Initiates synchronized recording across specified devices.

**Parameters:**
- `session_id`: Unique identifier for the recording session
- `target_devices`: List of device IDs to include (None = all connected)
- `record_video`: Enable video recording
- `record_thermal`: Enable thermal camera recording
- `record_shimmer`: Enable Shimmer sensor recording

**Returns:** `bool` - True if recording started successfully

##### stop_synchronized_recording(session_id: str) -> bool

Stops synchronized recording for the specified session.

**Parameters:**
- `session_id`: Session identifier to stop

**Returns:** `bool` - True if recording stopped successfully

##### get_connected_devices() -> Dict[str, SyncStatus]

Returns current connected devices and their synchronization status.

**Returns:** `Dict[str, SyncStatus]` - Device status dictionary

##### get_active_sessions() -> Dict[str, RecordingSession]

Returns currently active recording sessions.

**Returns:** `Dict[str, RecordingSession]` - Active sessions dictionary

### Callback Interfaces

#### Webcam Sync Callback

```python
def webcam_sync_callback(master_timestamp: float) -> None:
    """
    Called when synchronized recording starts/stops.
    
    Args:
        master_timestamp: Master clock timestamp for synchronization
    """
    pass
```

#### Session Event Callback

```python
def session_callback(session_id: str, session: RecordingSession) -> None:
    """
    Called when session state changes.
    
    Args:
        session_id: Session identifier
        session: Current session state
    """
    pass
```

#### Sync Status Callback

```python
def sync_status_callback(device_status: Dict[str, SyncStatus]) -> None:
    """
    Called when device synchronization status updates.
    
    Args:
        device_status: Current status of all connected devices
    """
    pass
```

### Utility Functions

#### initialize_master_synchronizer(ntp_port: int = 8889, pc_server_port: int = 9000) -> bool

Initializes and starts the global master synchronizer instance.

#### get_master_synchronizer() -> MasterClockSynchronizer

Returns the global master synchronizer instance (singleton pattern).

#### shutdown_master_synchronizer() -> None

Shuts down and cleans up the global master synchronizer instance.

## Network Protocol Specifications

### NTP Server Protocol

The Master Clock Synchronizer includes an embedded NTP server for Android device time synchronization.

**Protocol:** NTP (Network Time Protocol)
**Port:** 8889 (configurable)
**Transport:** UDP

#### Time Sync Request

| Field | Size | Description |
|-------|------|-------------|
| LI | 2 bits | Leap indicator |
| VN | 3 bits | Version number (4) |
| Mode | 3 bits | Protocol mode (3 = client) |
| Stratum | 8 bits | Stratum level |
| Poll | 8 bits | Poll interval |
| Precision | 8 bits | Clock precision |
| Root Delay | 32 bits | Round-trip delay to reference |
| Root Dispersion | 32 bits | Dispersion to reference |
| Reference ID | 32 bits | Reference clock identifier |
| Reference Timestamp | 64 bits | Reference timestamp |
| Origin Timestamp | 64 bits | Client transmission time |
| Receive Timestamp | 64 bits | Server reception time |
| Transmit Timestamp | 64 bits | Server transmission time |

#### Time Sync Response

Standard NTP response format with server timestamps providing precise time reference.

### PC Server Communication

**Protocol:** TCP with JSON messages
**Port:** 9000 (configurable)
**Transport:** TCP

#### Connection Handshake

1. **Client Connect:** Android device establishes TCP connection
2. **Hello Message:** Device sends identification and capabilities
3. **Welcome Response:** Server acknowledges and provides session info
4. **Sync Initiation:** Server initiates time synchronization

#### Message Format

All messages use length-prefixed JSON format:

```
[4-byte length][JSON message payload]
```

Length is sent as big-endian 32-bit integer indicating payload size.

### Device Registration Protocol

#### Registration Sequence

```mermaid
sequenceDiagram
    participant AD as Android Device
    participant PC as PC Server
    participant MCS as Master Clock Synchronizer
    
    AD->>PC: TCP Connect
    PC->>AD: Connection Accepted
    AD->>PC: Hello Message
    PC->>MCS: Device Connected Event
    MCS->>AD: Sync Timestamp Message
    AD->>MCS: Sync Response Message
    MCS->>MCS: Calculate Sync Quality
    MCS->>PC: Registration Complete
```

#### Hello Message Structure

```json
{
  "type": "hello",
  "device_id": "Samsung_Galaxy_S21",
  "capabilities": ["video_recording", "thermal_recording"],
  "timestamp": 1644859200.123456,
  "app_version": "1.2.3",
  "os_version": "Android 12"
}
```

## Integration Contracts

### Webcam Controller Integration

Webcam controllers must implement the following interface for synchronization:

```python
class WebcamSyncInterface:
    def on_sync_timestamp(self, timestamp: float) -> None:
        """
        Called when synchronized recording should start.
        
        Args:
            timestamp: Master timestamp for synchronization
        """
        pass
    
    def start_recording(self, session_id: str, timestamp: float) -> bool:
        """
        Start recording with synchronized timestamp.
        
        Args:
            session_id: Recording session identifier
            timestamp: Synchronized start timestamp
            
        Returns:
            bool: True if recording started successfully
        """
        pass
    
    def stop_recording(self, session_id: str, timestamp: float) -> bool:
        """
        Stop recording with synchronized timestamp.
        
        Args:
            session_id: Recording session identifier
            timestamp: Synchronized stop timestamp
            
        Returns:
            bool: True if recording stopped successfully
        """
        pass
```

### Android Device Integration

Android devices must implement the SyncClockManager interface:

```kotlin
interface SyncClockManager {
    fun startTimeSync(ntpServer: String, port: Int): Boolean
    fun getCurrentSyncedTime(): Long
    fun getSyncQuality(): Float
    fun onSyncCommand(command: SyncCommand)
    fun onRecordCommand(command: RecordCommand)
}
```

### Session Manager Integration

Session managers must implement event handling for coordination:

```python
class SessionManagerInterface:
    def on_session_started(self, session: RecordingSession) -> None:
        """Called when synchronized recording session starts"""
        pass
    
    def on_session_stopped(self, session: RecordingSession) -> None:
        """Called when synchronized recording session stops"""
        pass
    
    def on_session_quality_change(self, session_id: str, quality: float) -> None:
        """Called when session sync quality changes significantly"""
        pass
```

## Configuration Schema

### Synchronization Parameters

```json
{
  "synchronization": {
    "sync_tolerance_ms": 50.0,
    "sync_interval": 5.0,
    "quality_threshold": 0.8,
    "max_retry_attempts": 3,
    "retry_delay_ms": 1000,
    "drift_detection_threshold": 5.0,
    "auto_recovery_enabled": true
  }
}
```

### Quality Thresholds

```json
{
  "quality_thresholds": {
    "excellent": 0.9,
    "good": 0.7,
    "acceptable": 0.5,
    "poor": 0.0
  }
}
```

### Network Configuration

```json
{
  "network": {
    "ntp_port": 8889,
    "pc_server_port": 9000,
    "max_connections": 10,
    "connection_timeout_ms": 30000,
    "heartbeat_interval_ms": 5000,
    "message_timeout_ms": 10000
  }
}
```

## Event Schemas

### Device Events

#### Device Connected Event

```json
{
  "event_type": "device_connected",
  "timestamp": 1644859200.123456,
  "device_id": "Samsung_Galaxy_S21",
  "device_info": {
    "capabilities": ["video_recording", "thermal_recording"],
    "ip_address": "192.168.1.100",
    "app_version": "1.2.3"
  }
}
```

#### Device Disconnected Event

```json
{
  "event_type": "device_disconnected",
  "timestamp": 1644859200.123456,
  "device_id": "Samsung_Galaxy_S21",
  "reason": "connection_lost"
}
```

### Session Events

#### Session Started Event

```json
{
  "event_type": "session_started",
  "timestamp": 1644859200.123456,
  "session_id": "experiment_1644859200",
  "devices": ["Samsung_Galaxy_S21", "Pixel_6_Pro"],
  "configuration": {
    "record_video": true,
    "record_thermal": true,
    "record_shimmer": false
  }
}
```

#### Session Quality Change Event

```json
{
  "event_type": "session_quality_change",
  "timestamp": 1644859200.123456,
  "session_id": "experiment_1644859200",
  "previous_quality": 0.92,
  "current_quality": 0.73,
  "threshold_crossed": "good_to_acceptable"
}
```

### Quality Events

#### Sync Quality Alert

```json
{
  "event_type": "sync_quality_alert",
  "timestamp": 1644859200.123456,
  "device_id": "Samsung_Galaxy_S21",
  "sync_quality": 0.45,
  "time_offset_ms": 67.3,
  "alert_level": "warning"
}
```

## Error Handling Protocol

### Error Classifications

#### Network Errors

| Error Code | Description | Recovery Action |
|------------|-------------|-----------------|
| `NET_001` | Connection timeout | Retry connection |
| `NET_002` | Message parsing error | Request retransmission |
| `NET_003` | Protocol version mismatch | Update client/server |
| `NET_004` | Authentication failure | Re-authenticate |

#### Synchronization Errors

| Error Code | Description | Recovery Action |
|------------|-------------|-----------------|
| `SYNC_001` | Sync quality below threshold | Re-initiate synchronization |
| `SYNC_002` | Time offset too large | Force clock resync |
| `SYNC_003` | Device clock drift detected | Adjust sync parameters |
| `SYNC_004` | NTP server unavailable | Use system time fallback |

#### Session Errors

| Error Code | Description | Recovery Action |
|------------|-------------|-----------------|
| `SES_001` | Session start failure | Retry with subset of devices |
| `SES_002` | Recording initialization failed | Check device capabilities |
| `SES_003` | Session quality degraded | Alert user, continue recording |
| `SES_004` | Device dropped from session | Continue with remaining devices |

### Recovery Procedures

#### Automatic Recovery

```python
def auto_recovery_procedure(error_code: str, context: Dict) -> bool:
    """
    Automatic recovery based on error type.
    
    Args:
        error_code: Error classification code
        context: Error context information
        
    Returns:
        bool: True if recovery successful
    """
    if error_code.startswith("NET_"):
        return handle_network_error(error_code, context)
    elif error_code.startswith("SYNC_"):
        return handle_sync_error(error_code, context)
    elif error_code.startswith("SES_"):
        return handle_session_error(error_code, context)
    
    return False
```

#### Manual Recovery

For errors requiring manual intervention, the system provides detailed diagnostic information and recommended actions.

### Logging Standards

#### Log Levels

- **DEBUG**: Detailed synchronization timing information
- **INFO**: Normal operation events (device connect/disconnect, session start/stop)
- **WARNING**: Quality degradation, recoverable errors
- **ERROR**: Failed operations, configuration issues
- **CRITICAL**: System failures requiring immediate attention

#### Log Format

```
[TIMESTAMP] [LEVEL] [COMPONENT] [DEVICE_ID] - MESSAGE
```

Example:
```
[2022-02-14 12:00:00.123] [INFO] [MasterClockSync] [Samsung_Galaxy_S21] - Device synchronized with quality 0.92
```

This protocol specification provides the complete technical contract for all interactions with the Master Clock Synchronizer component, ensuring consistent and reliable integration across the entire Bucika GSR system.