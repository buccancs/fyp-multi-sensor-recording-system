# Android Multi-Modal Recording System Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph "UI Layer"
        MA[MainActivity]
        MV[MainViewModel]
        UI[activity_main.xml]
    end
    
    subgraph "Service Layer"
        RS[RecordingService<br/>Foreground Service]
        SM[SessionManager]
    end
    
    subgraph "Recording Components"
        CR[CameraRecorder<br/>4K RGB + RAW]
        TR[ThermalRecorder<br/>Topdon SDK]
        SR[ShimmerRecorder<br/>Bluetooth Sensors]
    end
    
    subgraph "Communication Layer"
        SC[SocketController<br/>TCP Client]
        PS[PreviewStreamer<br/>Real-time Streaming]
        NP[NetworkProtocol<br/>Command Definitions]
    end
    
    subgraph "Utility Layer"
        LOG[Logger<br/>File + Logcat]
        APP[MultiSensorApplication<br/>Hilt DI]
    end
    
    subgraph "External Systems"
        PC[PC Control Server]
        CAM[RGB Camera<br/>Camera2 API]
        THERMAL[Thermal Camera<br/>USB/Topdon]
        SHIMMER[Shimmer Sensors<br/>Bluetooth]
    end
    
    %% UI Layer Connections
    MA --> MV
    MA --> UI
    MV --> RS
    
    %% Service Layer Connections
    RS --> SM
    RS --> CR
    RS --> TR
    RS --> SR
    RS --> SC
    RS --> PS
    
    %% Recording Component Connections
    CR --> CAM
    TR --> THERMAL
    SR --> SHIMMER
    CR --> SM
    TR --> SM
    SR --> SM
    
    %% Communication Layer Connections
    SC --> PC
    SC --> NP
    PS --> SC
    PS --> CR
    PS --> TR
    
    %% Utility Layer Connections
    APP --> RS
    APP --> CR
    APP --> TR
    APP --> SR
    APP --> SC
    APP --> PS
    APP --> SM
    APP --> LOG
    
    %% Logging Connections
    LOG -.-> RS
    LOG -.-> CR
    LOG -.-> TR
    LOG -.-> SR
    LOG -.-> SC
    LOG -.-> PS
    LOG -.-> SM
    
    %% Styling
    classDef uiLayer fill:#e1f5fe
    classDef serviceLayer fill:#f3e5f5
    classDef recordingLayer fill:#e8f5e8
    classDef commLayer fill:#fff3e0
    classDef utilLayer fill:#fce4ec
    classDef externalLayer fill:#f5f5f5
    
    class MA,MV,UI uiLayer
    class RS,SM serviceLayer
    class CR,TR,SR recordingLayer
    class SC,PS,NP commLayer
    class LOG,APP utilLayer
    class PC,CAM,THERMAL,SHIMMER externalLayer
```

## Component Responsibilities

### UI Layer
- **MainActivity**: Main user interface with recording controls and preview displays
- **MainViewModel**: Reactive state management using LiveData and coroutines
- **activity_main.xml**: Layout with TextureView for camera preview and control buttons

### Service Layer
- **RecordingService**: Foreground service orchestrating all recording operations
- **SessionManager**: Manages recording sessions, file organization, and storage

### Recording Components
- **CameraRecorder**: Handles 4K RGB video recording and RAW image capture using Camera2 API
- **ThermalRecorder**: Manages thermal camera integration (Topdon SDK - currently simulated)
- **ShimmerRecorder**: Handles Shimmer sensor data collection via Bluetooth (currently simulated)

### Communication Layer
- **SocketController**: TCP client for PC communication with reconnection logic
- **PreviewStreamer**: Real-time frame streaming with YUV-to-JPEG conversion
- **NetworkProtocol**: Standardized command definitions and message formatting

### Utility Layer
- **Logger**: Comprehensive logging to both logcat and files with rotation
- **MultiSensorApplication**: Hilt dependency injection configuration

## Data Flow

```mermaid
sequenceDiagram
    participant UI as MainActivity
    participant VM as MainViewModel
    participant RS as RecordingService
    participant CR as CameraRecorder
    participant TR as ThermalRecorder
    participant SR as ShimmerRecorder
    participant SM as SessionManager
    participant PS as PreviewStreamer
    participant SC as SocketController
    
    UI->>VM: Start Recording
    VM->>RS: Start Recording Intent
    RS->>SM: Create New Session
    SM-->>RS: Session ID & File Paths
    
    par Recording Operations
        RS->>CR: Start RGB Recording
        CR->>CR: Configure Camera2 API
        CR-->>RS: Recording Started
        
        RS->>TR: Start Thermal Recording
        TR->>TR: Initialize Topdon SDK
        TR-->>RS: Recording Started
        
        RS->>SR: Start Shimmer Recording
        SR->>SR: Connect Bluetooth Sensors
        SR-->>RS: Recording Started
    end
    
    par Streaming Operations
        CR->>PS: RGB Frame Available
        TR->>PS: Thermal Frame Available
        PS->>SC: Send Preview Frame
        SC->>SC: Transmit to PC
    end
    
    par External Control
        SC->>SC: Receive PC Command
        SC->>RS: Process Command
        RS->>VM: Update State
        VM->>UI: Update UI
    end
```

## Architecture Principles

### Clean Architecture
- **Separation of Concerns**: Each component has a single responsibility
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Interface Segregation**: Components interact through well-defined interfaces

### Concurrency
- **Coroutines**: All blocking operations use Kotlin coroutines
- **Background Processing**: Heavy operations offloaded from main thread
- **Lifecycle Awareness**: Proper coroutine scope management

### Modularity
- **Independent Components**: Each recorder can be developed and tested separately
- **Extensible Design**: Easy to add new sensors or communication methods
- **Configuration Driven**: Behavior controlled through dependency injection

### Performance
- **Hardware Acceleration**: Uses hardware-accelerated codecs for video encoding
- **Memory Management**: Efficient frame processing and resource cleanup
- **Network Optimization**: Configurable streaming quality and frame rates

## Implementation Status

### ✅ Completed Components
- All core architecture components implemented
- Dependency injection with Hilt configured
- Foreground service with notification management
- Camera2 API integration for 4K recording
- TCP socket communication with PC
- Real-time preview streaming
- Comprehensive logging system
- Session management and file organization

### 🔄 Pending SDK Integration
- **Topdon SDK**: Replace thermal camera simulation with actual SDK calls
- **Shimmer SDK**: Replace sensor simulation with actual Bluetooth integration

### 🎯 Ready for Testing
- Build system configured and functional
- All components integrated and tested
- Architecture supports unit and integration testing
- Ready for hardware testing with actual devices