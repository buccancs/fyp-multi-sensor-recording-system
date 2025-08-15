# Multi-Sensor Recording System Architecture Diagrams

This file contains the core architecture diagrams for the Multi-Sensor Recording System, extracted and consolidated to provide ASCII-safe documentation sources.

## Primary System Architecture

```mermaid
graph TB
    subgraph "Multi-Sensor Recording System"
        subgraph "Android Application"
            direction TB
            MA[MainActivity<br/>Navigation Controller]
            MF[MainFragment<br/>Device Status]
            RF[RecordingFragment<br/>Session Control]
            SF[SettingsFragment<br/>Configuration]
            
            subgraph "Device Layer"
                RGB[RGB Camera<br/>Visual Recording]
                THERMAL[Thermal Camera<br/>Temperature Data]
                GSR[GSR Sensor<br/>Physiological Data]
            end
            
            subgraph "Management Layer"
                PM[PermissionManager<br/>API-Aware Permissions]
                SM[SessionManager<br/>Recording Lifecycle]
                SYNC[SyncManager<br/>Timestamp Coordination]
            end
        end
        
        subgraph "PC Master Controller"
            direction TB
            SERVER[Python Server<br/>Data Aggregation]
            CALIB[Calibration System<br/>Multi-Modal Alignment]
            STORAGE[Data Storage<br/>Research-Grade Persistence]
        end
        
        subgraph "Communication Layer"
            PROTOCOL[JSON Socket Protocol<br/>Real-Time Coordination]
        end
    end
    
    MA --> MF
    MA --> RF
    MA --> SF
    
    MF --> RGB
    MF --> THERMAL
    MF --> GSR
    
    RGB --> SM
    THERMAL --> SM
    GSR --> SM
    
    SM --> SYNC
    PM --> SM
    
    RF --> PROTOCOL
    PROTOCOL --> SERVER
    SERVER --> CALIB
    CALIB --> STORAGE
    
    SYNC -.-> PROTOCOL
```

## Permission Management Architecture

```mermaid
graph TB
    subgraph "API-Aware Permission Management"
        PM[PermissionManager]
        
        subgraph "API Level Detection"
            API_CHECK{API Level Check}
            API_30[API 30+ Scoped Storage]
            API_31[API 31+ Bluetooth]
            LEGACY[Legacy APIs]
        end
        
        subgraph "Permission Sets"
            CORE[Core Permissions<br/>Camera, Audio]
            STORAGE_NEW[Scoped Storage<br/>No External Write]
            STORAGE_OLD[External Storage<br/>Read/Write]
            BT_NEW[Bluetooth Connect/Scan]
            BT_OLD[Bluetooth/Admin]
            LOCATION[Location Services]
        end
        
        subgraph "Request Strategy"
            MINIMAL[Minimal Permission Set]
            FALLBACK[Graceful Fallback]
            RETRY[Retry Logic]
        end
    end
    
    PM --> API_CHECK
    API_CHECK -->|API 30+| API_30
    API_CHECK -->|API 31+| API_31
    API_CHECK -->|< API 30| LEGACY
    
    API_30 --> STORAGE_NEW
    LEGACY --> STORAGE_OLD
    API_31 --> BT_NEW
    LEGACY --> BT_OLD
    
    CORE --> MINIMAL
    STORAGE_NEW --> MINIMAL
    BT_NEW --> MINIMAL
    LOCATION --> MINIMAL
    
    MINIMAL --> FALLBACK
    FALLBACK --> RETRY
```

## ThermalCamera Initialization State Machine

```mermaid
stateDiagram-v2
    [*] --> NotInitialized
    
    NotInitialized --> Initializing: initialize()
    
    Initializing --> SecurityCheck: Check USB Permissions
    
    SecurityCheck --> SecurityFailed: SecurityException
    SecurityCheck --> InitializingSDK: Permissions OK
    
    SecurityFailed --> NotInitialized: isInitialized=false<br/>isReady=false
    
    InitializingSDK --> InitializationFailed: SDK Error
    InitializingSDK --> InitializedAndReady: Success
    
    InitializationFailed --> NotInitialized: isInitialized=false<br/>isReady=false
    
    InitializedAndReady --> DeviceDetection: Check Devices
    
    DeviceDetection --> ReadyWithDevice: Device Found
    DeviceDetection --> ReadyNoDevice: No Device
    
    ReadyWithDevice --> Recording: startRecording()
    ReadyNoDevice --> ReadyWithDevice: Device Connected
    
    Recording --> ReadyWithDevice: stopRecording()
    
    state SecurityFailed {
        [*] --> ErrorLogged
        ErrorLogged --> [*]
        note right : FIXED: No longer marks<br/>as initialized on<br/>security failure
    }
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        RGB_CAM[RGB Camera<br/>30 FPS Video]
        THERMAL_CAM[Thermal Camera<br/>25 FPS Thermal]
        GSR_SENSOR[GSR Sensor<br/>128 Hz Physiological]
    end
    
    subgraph "Android Processing"
        TIMESTAMP[Timestamp Sync<br/>System Clock]
        BUFFER[Data Buffering<br/>Memory Management]
        COMPRESS[Data Compression<br/>Efficient Storage]
    end
    
    subgraph "Communication"
        SOCKET[Socket Protocol<br/>JSON Messages]
        QUEUE[Message Queue<br/>Reliability]
    end
    
    subgraph "PC Processing"
        RECEIVE[Data Reception<br/>Multi-Stream]
        ALIGN[Temporal Alignment<br/>Synchronization]
        STORE[Persistent Storage<br/>Research Format]
    end
    
    RGB_CAM --> TIMESTAMP
    THERMAL_CAM --> TIMESTAMP
    GSR_SENSOR --> TIMESTAMP
    
    TIMESTAMP --> BUFFER
    BUFFER --> COMPRESS
    COMPRESS --> SOCKET
    
    SOCKET --> QUEUE
    QUEUE --> RECEIVE
    RECEIVE --> ALIGN
    ALIGN --> STORE
```

## Toast Management System

```mermaid
graph TB
    subgraph "ASCII-Only Message Management"
        TM[ToastManager]
        
        subgraph "Message Categories"
            SUCCESS["[SUCCESS] Messages<br/>Short Duration"]
            WARNING["[WARNING] Messages<br/>Long Duration"]
            ERROR["[ERROR] Messages<br/>Long Duration"]
            INFO["[INFO] Messages<br/>Short Duration"]
        end
        
        subgraph "Predefined Messages"
            USB["[USB] Device detected"]
            CONFIG["Configuration messages"]
            CONNECTION["Connection status"]
            PERMISSIONS["Permission status"]
        end
        
        subgraph "Usage Points"
            MAIN[MainActivity<br/>USB Events]
            FRAGMENTS[Fragments<br/>User Actions]
            MANAGERS[Managers<br/>Status Updates]
        end
    end
    
    TM --> SUCCESS
    TM --> WARNING
    TM --> ERROR
    TM --> INFO
    
    SUCCESS --> USB
    INFO --> CONFIG
    WARNING --> CONNECTION
    SUCCESS --> PERMISSIONS
    
    USB --> MAIN
    CONFIG --> FRAGMENTS
    CONNECTION --> FRAGMENTS
    PERMISSIONS --> MANAGERS
    
    note right of TM : Replaces direct Toast usage<br/>Enforces ASCII-only messages<br/>Consistent formatting
```

## Notes

- All diagrams use ASCII-safe characters only
- No emojis or Unicode symbols used
- Diagrams document actual implemented architecture
- State machine reflects fixed initialization semantics
- Permission flow shows API-level awareness
- Data flow represents actual implementation