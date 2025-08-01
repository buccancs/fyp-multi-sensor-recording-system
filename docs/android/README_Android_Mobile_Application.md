# Android Mobile Application: Distributed Mobile Data Collection Node

## Overview

The Android Mobile Application serves as a sophisticated **distributed mobile data collection node** within the Multi-Sensor Recording System. It is responsible for capturing synchronized data from multiple sensor modalities:

- **Phone's built-in camera** (4K video recording with RAW image capture)
- **Attached thermal camera** (Topdon TC001 via USB-C OTG)
- **Connected Shimmer physiological sensor** (Shimmer3 GSR+ via Bluetooth)

The application operates as a coordinated node in a distributed architecture, communicating with a PC controller via WiFi socket connections to enable precise temporal synchronization across all data sources.

## Architecture Overview

```mermaid
graph TB
    subgraph "Android Mobile Node"
        subgraph "Hardware Layer"
            CAM[Samsung S22 Camera<br/>4K + RAW Capture]
            THERMAL[Topdon TC001<br/>Thermal Camera]
            SHIMMER[Shimmer3 GSR+<br/>Physiological Sensor]
        end
        
        subgraph "Android Application"
            MA[MainActivity<br/>UI Coordinator]
            VM[MainViewModel<br/>State Management]
            
            subgraph "Recording Layer"
                CR[CameraRecorder<br/>Camera2 API]
                TR[ThermalRecorder<br/>Topdon SDK]
                SR[ShimmerRecorder<br/>Bluetooth]
                SM[SessionManager<br/>Data Organization]
            end
            
            subgraph "Communication Layer"
                PCH[PCCommunicationHandler<br/>Socket Client]
                PS[PreviewStreamer<br/>Real-time Streaming]
                NM[NetworkManager<br/>Connection Management]
            end
            
            subgraph "Controller Layer"
                CC[CalibrationController]
                SC[ShimmerController]
                UC[UsbController]
                NC[NetworkController]
                PC[PermissionController]
            end
        end
    end
    
    subgraph "PC Controller"
        SERVER[Socket Server<br/>Central Coordinator]
    end
    
    CAM --> CR
    THERMAL --> TR
    SHIMMER --> SR
    
    CR --> SM
    TR --> SM
    SR --> SM
    
    SM --> PCH
    CR --> PS
    
    PCH --> SERVER
    PS --> SERVER
    
    MA --> VM
    VM --> CR
    VM --> TR
    VM --> SR
    
    CC --> CR
    CC --> TR
    SC --> SR
    UC --> TR
    NC --> PCH
    PC --> MA
```

## Core Features

### 📱 Multi-Sensor Data Collection

#### 1. Camera Recording (Camera2 API)
- **4K Video Recording**: High-quality video capture at configurable frame rates
- **RAW Image Capture**: Simultaneous DNG/RAW image capture for calibration
- **Dual Capture Mode**: Video and still image capture in parallel
- **Manual Camera Controls**: ISO, exposure time, focus distance configuration
- **Preview Streaming**: Real-time video preview transmission to PC controller

#### 2. Thermal Imaging (Topdon SDK Integration)
- **Real-time Thermal Capture**: Live thermal imaging via USB-C OTG
- **Temperature Measurement**: Accurate temperature readings across the frame
- **Thermal Data Export**: Binary thermal data with metadata preservation
- **Device Management**: Automatic USB device detection and initialization
- **Calibration Support**: Thermal-RGB alignment for synchronized recording

#### 3. Physiological Sensing (Shimmer3 GSR+)
- **Bluetooth Communication**: Wireless connection to Shimmer3 GSR+ sensors
- **Real-time GSR Data**: Galvanic skin response measurement and streaming
- **Sampling Rate Control**: Configurable data collection frequencies
- **Session-based Recording**: Organized data collection with timestamps
- **Multiple Sensor Support**: Simultaneous connection to multiple Shimmer devices

### 🌐 Distributed Architecture

#### Network Communication
- **Socket-based Protocol**: JSON message communication with PC controller
- **Real-time Synchronization**: Microsecond-precision timing coordination
- **Preview Streaming**: Live video transmission for monitoring
- **Command Interface**: Remote control of recording operations
- **Status Reporting**: Continuous device health and status updates

#### Session Management
- **Coordinated Recording**: Synchronized start/stop across all sensors
- **Session Metadata**: Comprehensive recording session information
- **File Organization**: Automatic directory structure and naming
- **Data Validation**: Integrity checking and error recovery
- **Export Functions**: Standardized data export for analysis

### 🔧 Technical Implementation

#### Modern Android Development
- **Language**: Kotlin with Android Views and ViewBinding
- **Architecture**: Clean Architecture with MVVM pattern
- **Dependency Injection**: Hilt for component management
- **Concurrency**: Kotlin Coroutines for asynchronous operations
- **Database**: Room for local data persistence
- **Networking**: OkHttp for socket communication

#### Permission Management
- **Runtime Permissions**: Dynamic permission handling for all sensors
- **Background Execution**: Foreground service for continuous recording
- **Battery Optimization**: Power management for extended recording sessions
- **USB Permissions**: Automatic thermal camera access management

## User Interface

### 🎛️ Main Activity Interface

The MainActivity provides a comprehensive control interface for multi-sensor recording:

#### Navigation Structure
- **Navigation Drawer**: Organized access to all functional areas
  - Main Functions: Recording, Devices, Calibration, Files
  - Settings: Network Config, Shimmer Config, App Settings
  - Tools: Sync Tests, About, Diagnostics

- **Bottom Navigation**: Quick access to frequently used functions
  - Record: Start/stop recording operations
  - Monitor: Real-time sensor status monitoring
  - Calibrate: Camera and sensor calibration

#### Status Monitoring
- **Device Status Indicators**: Real-time connection status for all sensors
- **Recording Progress**: Session duration, data rates, storage usage
- **Network Status**: PC connection, bandwidth, latency information
- **Error Reporting**: Clear error messages and recovery guidance

#### Control Functions
- **Session Control**: Start/stop recording with synchronized timing
- **Preview Control**: Toggle real-time preview streaming
- **Calibration Control**: Initiate camera and sensor calibration
- **File Management**: Session review, export, and sharing

### 📊 Fragment-based Architecture

#### RecordingFragment
- **Recording Controls**: Start/stop buttons with session management
- **Real-time Monitoring**: Live sensor data display and status indicators
- **Session Information**: Current recording parameters and progress
- **Error Handling**: Recording issue detection and recovery

#### DevicesFragment
- **Connection Management**: Individual sensor connection controls
- **Device Discovery**: Automatic detection of available sensors
- **Status Monitoring**: Health indicators for all connected devices
- **Configuration Access**: Direct access to sensor-specific settings

#### CalibrationFragment
- **Calibration Workflows**: Step-by-step calibration procedures
- **Quality Assessment**: Calibration accuracy validation and recommendations
- **Pattern Detection**: Automatic calibration target recognition
- **Results Management**: Calibration data storage and retrieval

#### FilesFragment
- **Session Browser**: Navigate recorded sessions with preview
- **Data Export**: Export functions for analysis software
- **Storage Management**: Storage usage monitoring and cleanup
- **Sharing Functions**: Share session data via standard Android methods

## Data Flow Architecture

### 📈 Recording Workflow

```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant APP as Android App
    participant CAM as Camera2 API
    participant THERMAL as Topdon SDK
    participant SHIMMER as Shimmer3 GSR+
    
    PC->>APP: Connect Socket
    APP->>PC: Connection Established
    
    PC->>APP: Sync Clock Request
    APP->>PC: Clock Synchronized
    
    PC->>APP: Initialize Sensors
    APP->>CAM: Initialize Camera
    APP->>THERMAL: Connect USB Device
    APP->>SHIMMER: Connect Bluetooth
    
    CAM->>APP: Camera Ready
    THERMAL->>APP: Thermal Ready
    SHIMMER->>APP: GSR Ready
    
    APP->>PC: All Sensors Ready
    
    PC->>APP: Start Recording
    
    par Recording Operations
        APP->>CAM: Start Video Recording
        CAM->>APP: Video Stream
    and
        APP->>THERMAL: Start Thermal Capture
        THERMAL->>APP: Thermal Data
    and
        APP->>SHIMMER: Start GSR Recording
        SHIMMER->>APP: GSR Data
    end
    
    loop Real-time Streaming
        APP->>PC: Preview Stream
        APP->>PC: Status Updates
        APP->>PC: Sensor Data
    end
    
    PC->>APP: Stop Recording
    
    par Recording Termination
        APP->>CAM: Stop Recording
        APP->>THERMAL: Stop Capture
        APP->>SHIMMER: Stop Recording
    end
    
    APP->>APP: Finalize Session
    APP->>PC: Session Complete
```

### 💾 Data Storage Organization

```
/Android/data/com.multisensor.recording/files/
├── sessions/
│   ├── session_YYYYMMDD_HHMMSS/
│   │   ├── metadata.json                 # Session information
│   │   ├── camera/
│   │   │   ├── video.mp4                # 4K video recording
│   │   │   ├── frames/                   # RAW image captures
│   │   │   │   ├── frame_001.dng
│   │   │   │   ├── frame_002.dng
│   │   │   │   └── ...
│   │   │   └── camera_params.json        # Camera settings
│   │   ├── thermal/
│   │   │   ├── thermal_data.bin          # Binary thermal data
│   │   │   ├── thermal_metadata.json     # Temperature calibration
│   │   │   └── thermal_preview.mp4       # Thermal video preview
│   │   ├── shimmer/
│   │   │   ├── gsr_data.csv             # GSR measurements
│   │   │   ├── shimmer_config.json       # Sensor configuration
│   │   │   └── timestamps.json           # Synchronization data
│   │   └── logs/
│   │       ├── session.log               # Session event log
│   │       ├── errors.log                # Error tracking
│   │       └── performance.log           # Performance metrics
├── calibration/
│   ├── camera_calibration.json           # Camera intrinsic parameters
│   ├── thermal_calibration.json          # Thermal camera parameters
│   └── stereo_calibration.json           # RGB-Thermal alignment
└── temp/
    ├── preview_frames/                   # Temporary preview data
    └── processing/                       # Temporary processing files
```

## Integration Protocols

### 🔌 PC Communication Protocol

#### JSON Message Format
```json
{
  "type": "command|response|status|data",
  "timestamp": 1640995200000,
  "session_id": "session_20220101_120000",
  "device_id": "android_device_01",
  "payload": {
    // Message-specific data
  }
}
```

#### Command Messages
- `CONNECT`: Establish communication with PC controller
- `SYNC_CLOCK`: Synchronize timing with master clock
- `START_RECORDING`: Begin synchronized recording session
- `STOP_RECORDING`: End recording session
- `START_PREVIEW`: Enable real-time preview streaming
- `STOP_PREVIEW`: Disable preview streaming
- `GET_STATUS`: Request device status information
- `CALIBRATE`: Initiate calibration procedures

#### Status Reporting
- `DEVICE_STATUS`: Current sensor connection status
- `RECORDING_STATUS`: Active recording information
- `NETWORK_STATUS`: Communication quality metrics
- `ERROR_STATUS`: Error conditions and recovery status
- `SENSOR_DATA`: Real-time sensor measurements

### 📡 Network Configuration

#### Connection Parameters
- **Protocol**: TCP Socket communication
- **Default Port**: 8080 (configurable)
- **Preview Port**: 8081 (video streaming)
- **Timeout**: 30 seconds for commands
- **Retry Policy**: Automatic reconnection with exponential backoff

#### Quality of Service
- **Bandwidth Adaptation**: Dynamic quality adjustment based on network conditions
- **Compression**: Configurable preview stream compression
- **Buffering**: Intelligent buffering for network resilience
- **Prioritization**: Critical commands prioritized over data streams

## Performance Characteristics

### ⚡ System Performance

#### Recording Capabilities
- **Simultaneous Sensors**: 3+ sensors recording concurrently
- **Recording Duration**: Extended sessions (hours) with stable performance
- **Data Throughput**: High-bandwidth data collection and transmission
- **Memory Management**: Efficient resource usage with automatic cleanup
- **Battery Optimization**: Extended recording with minimal battery drain

#### Real-time Processing
- **Preview Generation**: Low-latency video preview streaming
- **Data Processing**: Real-time sensor data validation and formatting
- **Network Streaming**: Continuous data transmission with quality adaptation
- **Error Recovery**: Automatic recovery from temporary failures

### 🔧 Resource Utilization

#### Memory Management
- **Efficient Buffering**: Circular buffers for continuous data streams
- **Garbage Collection**: Optimized object lifecycle management
- **Memory Monitoring**: Real-time memory usage tracking and alerts
- **Resource Cleanup**: Automatic resource release on session termination

#### Storage Management
- **Local Storage**: Organized session data storage with metadata
- **Compression**: Efficient data compression for storage optimization
- **Cleanup Policies**: Automatic cleanup of temporary and old data
- **Export Functions**: Streamlined data export for external analysis

## Development and Testing

### 🧪 Testing Framework

#### Unit Testing
- **Component Testing**: Individual sensor and controller validation
- **Mock Testing**: Isolated testing with sensor simulation
- **Performance Testing**: Resource usage and timing validation
- **Error Testing**: Failure condition simulation and recovery

#### Integration Testing
- **Sensor Integration**: Multi-sensor coordination testing
- **Network Testing**: PC communication protocol validation
- **Session Testing**: Complete recording workflow validation
- **Stress Testing**: Extended operation and resource stress testing

### 🔨 Build Configuration

#### Android Configuration
- **Compile SDK**: 34 (Android 14)
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 14)
- **Build Tools**: Gradle 8.11.1 with Kotlin 2.0.20

#### Dependencies
- **Core Libraries**: AndroidX libraries for modern Android development
- **Sensor SDKs**: Topdon SDK, Shimmer Android API
- **Networking**: OkHttp for socket communication
- **Database**: Room for local data persistence
- **Testing**: Comprehensive test framework with mocking

## Deployment and Configuration

### 📱 Installation Requirements

#### Hardware Requirements
- **Android Device**: Samsung S22 or compatible (Android 7.0+)
- **Thermal Camera**: Topdon TC001 or compatible USB-C thermal camera
- **Physiological Sensor**: Shimmer3 GSR+ or compatible Bluetooth sensor
- **Network**: WiFi network for PC communication
- **Storage**: Minimum 8GB available storage for session data

#### Software Configuration
- **Permissions**: Camera, microphone, location, storage, Bluetooth permissions
- **Network**: PC controller IP address and port configuration
- **Sensors**: Sensor-specific configuration and calibration
- **Storage**: Session data storage location and cleanup policies

### ⚙️ Configuration Management

#### Application Settings
- **Recording Parameters**: Resolution, frame rate, quality settings
- **Network Configuration**: PC connection settings and timeout values
- **Sensor Configuration**: Individual sensor settings and calibration
- **Storage Configuration**: Data storage location and retention policies
- **Performance Settings**: Resource usage and optimization settings

#### Calibration Configuration
- **Camera Calibration**: Intrinsic and extrinsic parameter configuration
- **Thermal Calibration**: Temperature calibration and alignment settings
- **Synchronization**: Timing synchronization and offset configuration
- **Quality Settings**: Calibration quality thresholds and validation

## Troubleshooting and Support

### 🔍 Common Issues and Solutions

#### Connection Issues
- **PC Communication**: Network configuration and firewall settings
- **Sensor Connection**: Bluetooth pairing and USB device permissions
- **Permission Errors**: Runtime permission management and recovery
- **Battery Optimization**: Power management and background execution

#### Recording Issues
- **Storage Space**: Automatic storage monitoring and cleanup
- **Sensor Failures**: Error detection and automatic recovery
- **Network Issues**: Connection resilience and data buffering
- **Performance Issues**: Resource optimization and monitoring

### 📞 Support Resources

#### Documentation
- **User Guides**: Step-by-step operational procedures
- **Technical Documentation**: Detailed implementation specifications
- **API Reference**: Complete interface and protocol documentation
- **Troubleshooting**: Common issues and resolution procedures

#### Development Support
- **Source Code**: Complete Android application source code
- **Build Instructions**: Detailed build and deployment procedures
- **Testing Framework**: Comprehensive testing and validation tools
- **Example Configurations**: Sample configurations for common use cases

---

## Summary

The Android Mobile Application represents a sophisticated **distributed mobile data collection node** that successfully integrates multiple sensor modalities into a coordinated recording system. Through its robust architecture, comprehensive sensor integration, and seamless PC communication, it enables researchers to collect synchronized multi-modal data with research-grade precision and reliability.

The application's modern Android development practices, comprehensive error handling, and extensive documentation make it a valuable tool for experimental research requiring precise temporal synchronization across diverse sensor types. Its distributed architecture allows for scalable deployment across multiple mobile devices, creating a powerful platform for multi-participant and multi-location data collection scenarios.