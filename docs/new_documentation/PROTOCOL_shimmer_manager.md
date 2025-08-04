# Shimmer Manager and PC Application: Protocol Specification

## Table of Contents

- [Overview](#overview)
- [Data Structure Definitions](#data-structure-definitions)
  - [Core Data Classes](#core-data-classes)
  - [Device Status Structures](#device-status-structures)
  - [Configuration Data Types](#configuration-data-types)
  - [Network Message Formats](#network-message-formats)
- [CSV Data Export Format](#csv-data-export-format)
  - [Standard CSV Schema](#standard-csv-schema)
  - [Data Type Specifications](#data-type-specifications)
  - [File Naming Conventions](#file-naming-conventions)
  - [Data Validation Rules](#data-validation-rules)
- [Network Communication Protocol](#network-communication-protocol)
  - [Android Device Integration Messages](#android-device-integration-messages)
  - [PC Server Communication](#pc-server-communication)
  - [Synchronization Signal Protocol](#synchronization-signal-protocol)
  - [Session Management Messages](#session-management-messages)
- [API Specifications](#api-specifications)
  - [ShimmerManager Public API](#shimmermanager-public-api)
  - [ShimmerPCApplication Public API](#shimmerpcapplication-public-api)
  - [Callback Function Signatures](#callback-function-signatures)
  - [Error Handling Protocols](#error-handling-protocols)
- [Session Management Protocol](#session-management-protocol)
  - [Session Lifecycle Messages](#session-lifecycle-messages)
  - [Metadata Format Specifications](#metadata-format-specifications)
  - [File Organization Schema](#file-organization-schema)
- [Device Discovery and Connection Protocol](#device-discovery-and-connection-protocol)
  - [Bluetooth Discovery Protocol](#bluetooth-discovery-protocol)
  - [Android Device Registration](#android-device-registration)
  - [Device Capability Negotiation](#device-capability-negotiation)
- [Real-time Data Streaming Protocol](#real-time-data-streaming-protocol)
  - [Data Sample Format](#data-sample-format)
  - [Quality Assurance Metrics](#quality-assurance-metrics)
  - [Streaming Performance Parameters](#streaming-performance-parameters)

## Overview

This document defines the comprehensive data contracts, message formats, and communication protocols for the Shimmer Manager and PC Application components. These specifications ensure consistent data exchange, reliable device communication, and standardized file formats for research data collection and analysis.

The protocol specification covers three primary domains:
1. **Data Structures**: Internal data representations and type definitions
2. **Network Communication**: Message formats for device coordination
3. **File Formats**: Standardized export formats for research data

## Data Structure Definitions

### Core Data Classes

#### ShimmerSample Data Structure

**Purpose**: Standardized representation of sensor data from Shimmer devices

```python
@dataclass
class ShimmerSample:
    """Standardized Shimmer sensor data sample"""
    
    # Temporal Information (REQUIRED)
    timestamp: float                    # Unix timestamp with microsecond precision
    system_time: str                   # ISO 8601 formatted timestamp
    device_id: str                     # Unique device identifier
    
    # Connection Metadata (REQUIRED)
    connection_type: ConnectionType    # Enum: direct_bluetooth, android_mediated, simulation
    android_device_id: Optional[str]   # Associated Android device ID (if applicable)
    session_id: Optional[str]          # Recording session identifier
    
    # Physiological Sensors (OPTIONAL)
    gsr_conductance: Optional[float]   # Galvanic skin response (microsiemens)
    ppg_a13: Optional[float]          # Photoplethysmography (ADC units 0-4095)
    ecg: Optional[float]              # Electrocardiography (if available)
    emg: Optional[float]              # Electromyography (if available)
    
    # Motion Sensors (OPTIONAL)
    accel_x: Optional[float]          # X-axis acceleration (g-force, ±16g range)
    accel_y: Optional[float]          # Y-axis acceleration (g-force, ±16g range)
    accel_z: Optional[float]          # Z-axis acceleration (g-force, ±16g range)
    gyro_x: Optional[float]           # X-axis angular velocity (degrees/sec, ±2000°/s)
    gyro_y: Optional[float]           # Y-axis angular velocity (degrees/sec, ±2000°/s)
    gyro_z: Optional[float]           # Z-axis angular velocity (degrees/sec, ±2000°/s)
    mag_x: Optional[float]            # X-axis magnetometer (units vary by sensor)
    mag_y: Optional[float]            # Y-axis magnetometer (units vary by sensor)
    mag_z: Optional[float]            # Z-axis magnetometer (units vary by sensor)
    
    # Device Status (OPTIONAL)
    battery_percentage: Optional[int]  # Battery level (0-100%)
    signal_strength: Optional[float]   # Connection quality indicator
    
    # Extended Data (OPTIONAL)
    raw_data: Optional[Dict[str, Any]] # Raw sensor data for advanced processing
```

**Data Type Specifications**:

| Field Name | Data Type | Range/Format | Required | Description |
|------------|-----------|--------------|----------|-------------|
| timestamp | float | Unix timestamp | ✓ | Microsecond precision |
| system_time | str | ISO 8601 | ✓ | Human-readable timestamp |
| device_id | str | Alphanumeric | ✓ | Unique device identifier |
| connection_type | Enum | See ConnectionType | ✓ | Connection method |
| gsr_conductance | float | 0.0 - 100.0 | ✗ | Microsiemens (µS) |
| ppg_a13 | float | 0.0 - 4095.0 | ✗ | ADC units |
| accel_x/y/z | float | -16.0 - 16.0 | ✗ | G-force units |
| gyro_x/y/z | float | -2000.0 - 2000.0 | ✗ | Degrees per second |
| battery_percentage | int | 0 - 100 | ✗ | Percentage |

**JSON Serialization Example**:
```json
{
  "timestamp": 1641234567.123456,
  "system_time": "2022-01-03T15:42:47.123456Z",
  "device_id": "shimmer_00_06_66_66_66_66",
  "connection_type": "direct_bluetooth",
  "android_device_id": null,
  "session_id": "stress_study_20220103_154247",
  "gsr_conductance": 5.234,
  "ppg_a13": 2847.0,
  "accel_x": 0.234,
  "accel_y": -0.123,
  "accel_z": 0.987,
  "gyro_x": 12.45,
  "gyro_y": -3.21,
  "gyro_z": 8.76,
  "mag_x": null,
  "mag_y": null,
  "mag_z": null,
  "ecg": null,
  "emg": null,
  "battery_percentage": 85,
  "signal_strength": 0.95
}
```

### Device Status Structures

#### ShimmerStatus Data Structure

**Purpose**: Comprehensive device health and configuration monitoring

```python
@dataclass
class ShimmerStatus:
    """Comprehensive Shimmer device status information"""
    
    # Connection State (REQUIRED)
    is_available: bool                 # Device discoverable/reachable
    is_connected: bool                 # Active connection established
    is_recording: bool                 # Currently recording data
    is_streaming: bool                 # Currently streaming data
    connection_type: ConnectionType    # Active connection method
    device_state: DeviceState         # Current device state enum
    
    # Device Configuration (OPTIONAL)
    sampling_rate: int                 # Configured sampling rate (Hz)
    enabled_channels: Set[str]         # Active sensor channels
    device_name: Optional[str]         # Human-readable device name
    mac_address: Optional[str]         # Bluetooth MAC address
    firmware_version: Optional[str]    # Device firmware version
    
    # Runtime Status (OPTIONAL)
    battery_level: Optional[int]       # Battery percentage (0-100)
    signal_quality: Optional[str]      # Connection quality description
    samples_recorded: int              # Total samples in current session
    last_data_timestamp: Optional[float] # Last data reception time
    
    # Android Integration (OPTIONAL)
    android_device_id: Optional[str]   # Associated Android device
    
    # Error Tracking (OPTIONAL)
    last_error: Optional[str]          # Most recent error message
    connection_attempts: int           # Connection retry count
```

**DeviceState Enumeration**:
```python
class DeviceState(Enum):
    DISCONNECTED = "disconnected"      # No connection established
    CONNECTING = "connecting"          # Connection attempt in progress
    CONNECTED = "connected"            # Connected but not streaming
    STREAMING = "streaming"            # Actively streaming data
    ERROR = "error"                    # Error state requiring attention
```

**ConnectionType Enumeration**:
```python
class ConnectionType(Enum):
    DIRECT_BLUETOOTH = "direct_bluetooth"    # PC ↔ Bluetooth ↔ Shimmer
    ANDROID_MEDIATED = "android_mediated"    # PC ↔ Network ↔ Android ↔ Shimmer
    SIMULATION = "simulation"                # Software simulation mode
```

### Configuration Data Types

#### DeviceConfiguration Data Structure

**Purpose**: Device configuration parameters and settings

```python
@dataclass
class DeviceConfiguration:
    """Shimmer device configuration specification"""
    
    # Device Identification (REQUIRED)
    device_id: str                     # Unique device identifier
    mac_address: str                   # Bluetooth MAC address
    enabled_channels: Set[str]         # Sensor channels to activate
    
    # Connection Configuration (REQUIRED)
    connection_type: ConnectionType    # Preferred connection method
    sampling_rate: int = 128           # Sampling frequency in Hz
    
    # Android Integration (OPTIONAL)
    android_device_id: Optional[str] = None  # Target Android device
    
    # Advanced Configuration (OPTIONAL)
    auto_reconnect: bool = True        # Enable automatic reconnection
    data_validation: bool = True       # Enable real-time data validation
    buffer_size: int = 1000           # Data buffer size (samples)
    
    # Sensor-Specific Settings (OPTIONAL)
    sensor_range: Optional[Dict[str, Any]] = None  # Sensor range configurations
    calibration_data: Optional[Dict[str, Any]] = None  # Device calibration parameters
```

**Supported Sensor Channels**:
```python
SUPPORTED_CHANNELS = {
    "GSR",           # Galvanic skin response
    "PPG_A13",       # Photoplethysmography (internal ADC)
    "Accel_X",       # X-axis accelerometer
    "Accel_Y",       # Y-axis accelerometer
    "Accel_Z",       # Z-axis accelerometer
    "Gyro_X",        # X-axis gyroscope
    "Gyro_Y",        # Y-axis gyroscope
    "Gyro_Z",        # Z-axis gyroscope
    "Mag_X",         # X-axis magnetometer
    "Mag_Y",         # Y-axis magnetometer
    "Mag_Z",         # Z-axis magnetometer
    "ECG",           # Electrocardiography (if equipped)
    "EMG",           # Electromyography (if equipped)
}
```

### Network Message Formats

#### Android Device Integration Messages

**Device Registration Message**:
```json
{
  "message_type": "device_registration",
  "timestamp": 1641234567.123456,
  "android_device_id": "android_001",
  "capabilities": [
    "shimmer",
    "video_recording",
    "thermal_imaging",
    "gps"
  ],
  "shimmer_devices": [
    {
      "mac_address": "00:06:66:66:66:66",
      "device_name": "Shimmer3_GSR+",
      "firmware_version": "BoilerPlate 0.1.0",
      "available_sensors": ["GSR", "PPG_A13", "Accel_XYZ"]
    }
  ],
  "device_info": {
    "manufacturer": "Google",
    "model": "Pixel 6",
    "android_version": "12",
    "app_version": "1.2.3"
  }
}
```

**Shimmer Data Message**:
```json
{
  "message_type": "shimmer_data",
  "timestamp": 1641234567.123456,
  "android_device_id": "android_001",
  "shimmer_mac_address": "00:06:66:66:66:66",
  "session_id": "stress_study_20220103_154247",
  "sensor_data": {
    "gsr_conductance": 5.234,
    "ppg_a13": 2847,
    "accel_x": 0.234,
    "accel_y": -0.123,
    "accel_z": 0.987,
    "battery_percentage": 85
  },
  "data_quality": {
    "connection_strength": 0.95,
    "electrode_contact": "good",
    "motion_artifacts": "minimal"
  }
}
```

## CSV Data Export Format

### Standard CSV Schema

**Complete Field Specification**:

| Column Name | Data Type | Units | Precision | Required | Description |
|-------------|-----------|-------|-----------|----------|-------------|
| timestamp | float | seconds | 6 decimal places | ✓ | Unix timestamp |
| system_time | string | ISO 8601 | microseconds | ✓ | Human-readable time |
| device_id | string | - | - | ✓ | Device identifier |
| connection_type | string | enum | - | ✓ | Connection method |
| android_device_id | string | - | - | ✗ | Android device ID |
| session_id | string | - | - | ✗ | Session identifier |
| gsr_conductance | float | µS | 3 decimal places | ✗ | Skin conductance |
| ppg_a13 | float | ADC units | 0 decimal places | ✗ | Heart rate signal |
| accel_x | float | g | 3 decimal places | ✗ | X acceleration |
| accel_y | float | g | 3 decimal places | ✗ | Y acceleration |
| accel_z | float | g | 3 decimal places | ✗ | Z acceleration |
| gyro_x | float | °/s | 2 decimal places | ✗ | X angular velocity |
| gyro_y | float | °/s | 2 decimal places | ✗ | Y angular velocity |
| gyro_z | float | °/s | 2 decimal places | ✗ | Z angular velocity |
| mag_x | float | varies | 2 decimal places | ✗ | X magnetic field |
| mag_y | float | varies | 2 decimal places | ✗ | Y magnetic field |
| mag_z | float | varies | 2 decimal places | ✗ | Z magnetic field |
| ecg | float | mV | 3 decimal places | ✗ | ECG signal |
| emg | float | mV | 3 decimal places | ✗ | EMG signal |
| battery_percentage | integer | % | 0 decimal places | ✗ | Battery level |
| signal_strength | float | ratio | 2 decimal places | ✗ | Connection quality |

### Data Type Specifications

**Numerical Data Formatting**:
```python
CSV_FORMAT_SPECIFICATIONS = {
    'timestamp': {
        'type': 'float',
        'precision': 6,
        'example': '1641234567.123456',
        'validation': lambda x: x > 0
    },
    'gsr_conductance': {
        'type': 'float',
        'precision': 3,
        'range': (0.0, 100.0),
        'units': 'microsiemens',
        'example': '5.234'
    },
    'ppg_a13': {
        'type': 'float',
        'precision': 0,
        'range': (0.0, 4095.0),
        'units': 'ADC_units',
        'example': '2847'
    },
    'accel_x': {
        'type': 'float',
        'precision': 3,
        'range': (-16.0, 16.0),
        'units': 'g',
        'example': '0.234'
    },
    'battery_percentage': {
        'type': 'integer',
        'range': (0, 100),
        'units': 'percent',
        'example': '85'
    }
}
```

**Missing Data Representation**:
- Missing numerical values: Empty cell (no value)
- Missing string values: Empty cell (no value)
- Invalid data: Marked with comment field if available

### File Naming Conventions

**Standard Naming Pattern**:
```
{device_id}_data.csv
```

**Examples**:
- `shimmer_00_06_66_66_66_66_data.csv` (Direct Bluetooth device)
- `android_android_001_shimmer_data.csv` (Android-mediated device)
- `shimmer_simulation_001_data.csv` (Simulation device)

**Session Directory Structure**:
```
recordings/
└── {session_id}/
    ├── shimmer/
    │   ├── {device_id_1}_data.csv
    │   ├── {device_id_2}_data.csv
    │   └── shimmer_metadata.json
    ├── sync_events.log
    └── session_info.json
```

### Data Validation Rules

**Real-time Validation Constraints**:

```python
VALIDATION_RULES = {
    'temporal_validation': {
        'timestamp_monotonic': True,         # Timestamps must increase
        'max_time_gap': 1.0,                # Maximum gap between samples (seconds)
        'min_sample_rate': 64,              # Minimum acceptable sample rate (Hz)
        'max_sample_rate': 512              # Maximum acceptable sample rate (Hz)
    },
    'sensor_validation': {
        'gsr_conductance': {
            'min': 0.0,
            'max': 100.0,
            'outlier_threshold': 3.0        # Standard deviations from mean
        },
        'ppg_a13': {
            'min': 0.0,
            'max': 4095.0,
            'spike_detection': True         # Detect unrealistic spikes
        },
        'accel_magnitude': {
            'min': 0.0,
            'max': 20.0,                    # Vector magnitude in g
            'gravity_check': True           # Validate against gravity vector
        },
        'battery_percentage': {
            'min': 0,
            'max': 100,
            'decreasing_only': True         # Battery should only decrease
        }
    },
    'data_quality': {
        'completeness_threshold': 0.95,     # Minimum data completeness (95%)
        'max_consecutive_missing': 10,      # Maximum consecutive missing samples
        'connection_timeout': 30.0          # Connection loss timeout (seconds)
    }
}
```

## Network Communication Protocol

### Android Device Integration Messages

#### Session Control Messages

**Start Session Command**:
```json
{
  "message_type": "start_session",
  "timestamp": 1641234567.123456,
  "session_id": "stress_study_20220103_154247",
  "configuration": {
    "record_shimmer": true,
    "record_video": true,
    "record_thermal": false,
    "record_audio": false,
    "video_resolution": "1920x1080",
    "video_framerate": 30,
    "shimmer_sampling_rate": 128,
    "session_duration": 600
  },
  "synchronization": {
    "enable_sync_signals": true,
    "sync_signal_types": ["flash", "beep"],
    "ntp_server": "192.168.1.100"
  }
}
```

**Stop Session Command**:
```json
{
  "message_type": "stop_session",
  "timestamp": 1641234567.123456,
  "session_id": "stress_study_20220103_154247",
  "transfer_files": true,
  "cleanup_local_files": false
}
```

#### Synchronization Signal Messages

**Flash Synchronization Signal**:
```json
{
  "message_type": "sync_signal",
  "signal_type": "flash",
  "timestamp": 1641234567.123456,
  "parameters": {
    "duration_ms": 200,
    "intensity": 1.0,
    "color": "white",
    "marker_id": "STIMULUS_ONSET_01"
  }
}
```

**Audio Beep Signal**:
```json
{
  "message_type": "sync_signal",
  "signal_type": "beep",
  "timestamp": 1641234567.123456,
  "parameters": {
    "frequency_hz": 1000,
    "duration_ms": 100,
    "volume": 0.8,
    "marker_id": "RESPONSE_CUE_01"
  }
}
```

### PC Server Communication

#### Device Status Updates

**Device Status Message**:
```json
{
  "message_type": "device_status",
  "timestamp": 1641234567.123456,
  "android_device_id": "android_001",
  "shimmer_devices": [
    {
      "mac_address": "00:06:66:66:66:66",
      "connection_status": "connected",
      "battery_level": 85,
      "data_quality": "good",
      "samples_per_second": 128,
      "last_data_timestamp": 1641234567.120000
    }
  ],
  "system_status": {
    "storage_available_mb": 15420,
    "cpu_usage_percent": 23,
    "memory_usage_percent": 67,
    "temperature_celsius": 35
  }
}
```

#### File Transfer Protocol

**File Transfer Initiation**:
```json
{
  "message_type": "file_transfer_start",
  "timestamp": 1641234567.123456,
  "session_id": "stress_study_20220103_154247",
  "files": [
    {
      "file_type": "shimmer_data",
      "filename": "shimmer_data_20220103_154247.csv",
      "size_bytes": 2485760,
      "checksum_md5": "a1b2c3d4e5f6789012345678901234ab",
      "compression": "gzip"
    },
    {
      "file_type": "video",
      "filename": "video_20220103_154247.mp4",
      "size_bytes": 157286400,
      "checksum_md5": "b2c3d4e5f6789012345678901234abc1",
      "compression": "none"
    }
  ]
}
```

## API Specifications

### ShimmerManager Public API

#### Core Management Methods

```python
class ShimmerManager:
    def initialize() -> bool:
        """
        Initialize the Shimmer manager system
        
        Returns:
            bool: True if initialization successful
            
        Raises:
            ShimmerError: If initialization fails
        """
    
    def scan_and_pair_devices() -> Dict[str, List[str]]:
        """
        Discover available Shimmer devices across all connection types
        
        Returns:
            Dict mapping connection types to device lists:
            {
                'direct': ['mac_address_1', 'mac_address_2'],
                'android': ['android_device_1'],
                'simulated': ['sim_device_1']
            }
            
        Raises:
            DeviceDiscoveryError: If device discovery fails
        """
    
    def connect_devices(device_info: Union[List[str], Dict[str, List[str]]]) -> bool:
        """
        Connect to specified Shimmer devices
        
        Args:
            device_info: Device connection information
                - List[str]: Legacy format (MAC addresses)
                - Dict[str, List[str]]: Enhanced format with connection types
        
        Returns:
            bool: True if all connections successful
            
        Raises:
            DeviceConnectionError: If device connection fails
        """
    
    def start_streaming() -> bool:
        """
        Start data streaming from all connected devices
        
        Returns:
            bool: True if streaming started successfully
            
        Raises:
            StreamingError: If streaming initialization fails
        """
    
    def start_recording(session_id: str) -> bool:
        """
        Start recording data to CSV files
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            bool: True if recording started successfully
            
        Raises:
            SessionError: If recording session fails to start
        """
    
    def get_shimmer_status() -> Dict[str, ShimmerStatus]:
        """
        Get comprehensive status of all Shimmer devices
        
        Returns:
            Dict mapping device IDs to ShimmerStatus objects
        """
```

#### Configuration Methods

```python
def set_enabled_channels(device_id: str, channels: Set[str]) -> bool:
    """
    Configure enabled sensor channels for a device
    
    Args:
        device_id: Target device identifier
        channels: Set of channel names to enable
            Valid channels: {"GSR", "PPG_A13", "Accel_X", "Accel_Y", "Accel_Z", ...}
    
    Returns:
        bool: True if configuration successful
        
    Raises:
        ConfigurationError: If channel configuration fails
    """

def set_sampling_rate(device_id: str, rate_hz: int) -> bool:
    """
    Configure device sampling rate
    
    Args:
        device_id: Target device identifier
        rate_hz: Sampling rate in Hz (valid range: 1-512)
    
    Returns:
        bool: True if configuration successful
        
    Raises:
        ConfigurationError: If sampling rate invalid or set operation fails
    """
```

### ShimmerPCApplication Public API

#### Application Control Methods

```python
class ShimmerPCApplication:
    def initialize() -> bool:
        """
        Initialize the PC application with Shimmer integration
        
        Returns:
            bool: True if initialization successful
        """
    
    def start_session(session_id: str, record_shimmer: bool = True) -> bool:
        """
        Start a coordinated recording session
        
        Args:
            session_id: Unique session identifier
            record_shimmer: Enable Shimmer data recording
            
        Returns:
            bool: True if session started successfully
        """
    
    def stop_session() -> bool:
        """
        Stop the current recording session
        
        Returns:
            bool: True if session stopped successfully
        """
    
    def send_sync_signal(signal_type: str = "flash", **kwargs) -> int:
        """
        Send synchronization signal to all connected devices
        
        Args:
            signal_type: Type of sync signal ("flash" or "beep")
            **kwargs: Signal-specific parameters
                For "flash": duration_ms, intensity, color, marker_id
                For "beep": frequency_hz, duration_ms, volume, marker_id
        
        Returns:
            int: Number of devices that received the signal
        """
    
    def get_status_summary() -> Dict[str, Any]:
        """
        Get comprehensive application status summary
        
        Returns:
            Dict containing:
            {
                'android_devices': int,
                'shimmer_devices': int,
                'active_session': str | None,
                'data_samples_received': int,
                'devices_streaming': int,
                'devices_recording': int
            }
        """
```

### Callback Function Signatures

#### Data Processing Callbacks

```python
def data_callback(sample: ShimmerSample) -> None:
    """
    Process incoming Shimmer data sample
    
    Args:
        sample: ShimmerSample object containing sensor data
        
    Note:
        This callback is called for every data sample received.
        Implementation should be efficient to avoid blocking data flow.
    """

def status_callback(device_id: str, status: ShimmerStatus) -> None:
    """
    Handle device status updates
    
    Args:
        device_id: Device identifier
        status: Current ShimmerStatus object
        
    Note:
        Called when device connection state or configuration changes.
    """

def android_device_callback(device_id: str, status: Dict[str, Any]) -> None:
    """
    Handle Android device events
    
    Args:
        device_id: Android device identifier
        status: Android device status dictionary
        
    Note:
        Called when Android devices connect, disconnect, or update status.
    """

def connection_state_callback(device_id: str, state: DeviceState, 
                            connection_type: ConnectionType) -> None:
    """
    Handle connection state changes
    
    Args:
        device_id: Device identifier
        state: New DeviceState enum value
        connection_type: ConnectionType enum value
        
    Note:
        Called when device connection state transitions occur.
    """
```

### Error Handling Protocols

#### Exception Hierarchy

```python
class ShimmerError(Exception):
    """Base exception class for Shimmer-related errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()

class DeviceConnectionError(ShimmerError):
    """Device connection establishment failures"""
    pass

class DataValidationError(ShimmerError):
    """Data quality and validation failures"""
    pass

class SessionError(ShimmerError):
    """Session management and coordination failures"""
    pass

class NetworkError(ShimmerError):
    """Android device network communication failures"""
    pass

class ConfigurationError(ShimmerError):
    """Device configuration and setup failures"""
    pass
```

#### Error Response Format

```json
{
  "error": {
    "type": "DeviceConnectionError",
    "message": "Failed to establish Bluetooth connection to device 00:06:66:66:66:66",
    "error_code": "BT_CONNECTION_TIMEOUT",
    "timestamp": 1641234567.123456,
    "details": {
      "device_id": "shimmer_00_06_66_66_66_66",
      "mac_address": "00:06:66:66:66:66",
      "connection_type": "direct_bluetooth",
      "retry_count": 3,
      "last_seen": 1641234500.0
    },
    "suggested_actions": [
      "Check device battery level",
      "Verify Bluetooth pairing",
      "Restart Bluetooth service",
      "Move device closer to PC"
    ]
  }
}
```

## Session Management Protocol

### Session Lifecycle Messages

#### Session Metadata Format

**session_info.json**:
```json
{
  "session_id": "stress_study_20220103_154247",
  "start_time": "2022-01-03T15:42:47.123456Z",
  "end_time": "2022-01-03T15:52:47.987654Z",
  "duration_seconds": 600.864198,
  "participant_info": {
    "participant_id": "P001",
    "age": 25,
    "gender": "F",
    "study_group": "control"
  },
  "experimental_conditions": {
    "protocol": "stress_induction",
    "stimulus_type": "cognitive_load",
    "baseline_duration": 120,
    "stimulus_duration": 300,
    "recovery_duration": 180
  },
  "device_summary": {
    "total_devices": 2,
    "direct_bluetooth": 1,
    "android_mediated": 1,
    "total_samples": 153840,
    "data_quality": "excellent"
  },
  "sync_events": [
    {
      "timestamp": 1641234567.123456,
      "event_type": "flash",
      "marker_id": "BASELINE_END",
      "devices_notified": 2
    }
  ]
}
```

### File Organization Schema

**Complete Session Directory Structure**:
```
recordings/
└── {session_id}/
    ├── shimmer/
    │   ├── {device_id_1}_data.csv
    │   ├── {device_id_2}_data.csv
    │   └── shimmer_metadata.json
    ├── android/
    │   ├── {android_device_1}/
    │   │   ├── shimmer_data.csv
    │   │   ├── video_recording.mp4
    │   │   └── device_metadata.json
    │   └── {android_device_2}/
    │       └── ...
    ├── sync_events.log
    ├── session_info.json
    ├── data_quality_report.json
    └── analysis/
        ├── preprocessing_log.txt
        └── quality_metrics.csv
```

This comprehensive protocol specification ensures consistent data handling, reliable device communication, and standardized file formats across all components of the Shimmer Manager and PC Application system. The detailed type definitions, message formats, and API specifications provide the necessary contracts for robust system integration and research data collection.