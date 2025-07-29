# Milestone 2.8 Architecture Documentation
## Calibration Capture and Sync Features

### Overview

Milestone 2.8 introduces advanced calibration capture and synchronization features to the Multi-Sensor Recording System. This document provides comprehensive architectural documentation including system design, component interactions, and data flow diagrams.

### System Architecture

The Milestone 2.8 implementation consists of several key components working together to provide calibration capture and synchronization functionality:

```mermaid
graph TB
    subgraph "PC Controller"
        PC[PC Application]
        PC --> |Commands| NET[Network Interface]
    end
    
    subgraph "Android Application"
        subgraph "Network Layer"
            NET --> |Socket| JSC[JsonSocketClient]
            JSC --> CP[CommandProcessor]
        end
        
        subgraph "Calibration System"
            CP --> |CALIBRATE| CCM[CalibrationCaptureManager]
            CCM --> CR[CameraRecorder]
            CCM --> TR[ThermalRecorder]
            CCM --> SCM[SyncClockManager]
        end
        
        subgraph "Sync System"
            CP --> |SYNC_TIME| SCM
            CP --> |FLASH_SYNC| FS[Flash Sync Handler]
            CP --> |BEEP_SYNC| BS[Beep Sync Handler]
        end
        
        subgraph "Storage System"
            CCM --> |Save Images| FS_STORAGE[File System]
            SCM --> |Sync Markers| FS_STORAGE
        end
        
        subgraph "UI Layer"
            MA[MainActivity] --> CCM
            MA --> SCM
            MA --> |Manual Controls| CP
        end
    end
    
    subgraph "Hardware"
        CR --> |RGB Camera| CAM[Phone Camera]
        TR --> |Thermal Camera| THERMAL[Topdon IR Camera]
        FS --> |Flash Control| FLASH[Camera Flash/Torch]
        BS --> |Audio Control| SPEAKER[Audio System]
    end
```

### Component Architecture

#### 1. CalibrationCaptureManager

The central coordinator for dual-camera calibration capture operations.

```mermaid
classDiagram
    class CalibrationCaptureManager {
        -Context context
        -CameraRecorder cameraRecorder
        -ThermalRecorder thermalRecorder
        -SyncClockManager syncClockManager
        -Logger logger
        -AtomicInteger captureCounter
        
        +captureCalibrationImages(calibrationId, captureRgb, captureThermal, highResolution) CalibrationCaptureResult
        +getCalibrationSessions() List~CalibrationSession~
        +deleteCalibrationSession(calibrationId) Boolean
        +getCalibrationStatistics() CalibrationStatistics
        -generateCalibrationId() String
        -getCalibrationDirectory() File
    }
    
    class CalibrationCaptureResult {
        +Boolean success
        +String calibrationId
        +String rgbFilePath
        +String thermalFilePath
        +Long timestamp
        +Long syncedTimestamp
        +String errorMessage
    }
    
    class CalibrationSession {
        +String calibrationId
        +File rgbFile
        +File thermalFile
        +Long timestamp
    }
    
    class CalibrationStatistics {
        +Int totalSessions
        +Int completeSessions
        +Int rgbOnlySessions
        +Int thermalOnlySessions
        +Int totalCaptures
    }
    
    CalibrationCaptureManager --> CalibrationCaptureResult
    CalibrationCaptureManager --> CalibrationSession
    CalibrationCaptureManager --> CalibrationStatistics
```

#### 2. SyncClockManager

Manages clock synchronization with PC and provides synchronized timestamps.

```mermaid
classDiagram
    class SyncClockManager {
        -Logger logger
        -Mutex mutex
        -Long clockOffsetMs
        -Long lastSyncTimestamp
        -Long pcReferenceTime
        -Boolean isSynchronized
        
        +synchronizeWithPc(pcTimestamp, syncId) Boolean
        +getSyncedTimestamp(deviceTimestamp) Long
        +getCurrentSyncedTime() Long
        +isSyncValid() Boolean
        +getSyncStatus() SyncStatus
        +resetSync()
        +deviceToPcTime(deviceTimestamp) Long
        +pcToDeviceTime(pcTimestamp) Long
        +getSyncStatistics() String
        +estimateNetworkLatency(pcTimestamp, requestSentTime) Long
        +validateSyncHealth() Boolean
    }
    
    class SyncStatus {
        +Boolean isSynchronized
        +Long clockOffsetMs
        +Long lastSyncTimestamp
        +Long pcReferenceTime
        +Long syncAge
    }
    
    SyncClockManager --> SyncStatus
```

#### 3. CommandProcessor Enhancement

Extended to handle new Milestone 2.8 commands.

```mermaid
classDiagram
    class CommandProcessor {
        -Context context
        -CalibrationCaptureManager calibrationCaptureManager
        -SyncClockManager syncClockManager
        -CameraRecorder cameraRecorder
        -ThermalRecorder thermalRecorder
        -JsonSocketClient jsonSocketClient
        -Logger logger
        
        +processCommand(command) Unit
        -handleCaptureCalibration(command) Unit
        -handleSyncTime(command) Unit
        -handleFlashSync(command) Unit
        -handleBeepSync(command) Unit
        -triggerVisualStimulusWithDuration(durationMs) Unit
        -triggerAudioStimulusWithParameters(frequencyHz, durationMs, volume) Unit
        -createFlashSyncMarker(syncId, durationMs) Unit
        -createBeepSyncMarker(syncId, frequencyHz, durationMs, volume) Unit
    }
```

### Data Flow Architecture

#### Calibration Capture Flow

```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant CP as CommandProcessor
    participant CCM as CalibrationCaptureManager
    participant SCM as SyncClockManager
    participant CR as CameraRecorder
    participant TR as ThermalRecorder
    participant FS as File System
    
    PC->>CP: CALIBRATE command
    CP->>CCM: captureCalibrationImages()
    
    par Dual Camera Capture
        CCM->>CR: captureCalibrationImage()
        CR->>CR: Capture RGB image
        CR-->>CCM: RGB file path
    and
        CCM->>TR: captureCalibrationImage()
        TR->>TR: Capture thermal image
        TR-->>CCM: Thermal file path
    end
    
    CCM->>SCM: getSyncedTimestamp()
    SCM-->>CCM: Synchronized timestamp
    
    CCM->>FS: Save calibration metadata
    CCM-->>CP: CalibrationCaptureResult
    CP-->>PC: Success acknowledgment
```

#### Clock Synchronization Flow

```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant CP as CommandProcessor
    participant SCM as SyncClockManager
    participant FS as File System
    
    PC->>CP: SYNC_TIME command (PC timestamp)
    CP->>SCM: synchronizeWithPc(pcTimestamp, syncId)
    
    SCM->>SCM: Calculate offset = pcTime - deviceTime
    SCM->>SCM: Store sync parameters
    SCM->>SCM: Validate timestamp
    
    alt Valid Synchronization
        SCM-->>CP: Success (true)
        CP->>FS: Create sync marker file
        CP-->>PC: Sync success acknowledgment
    else Invalid Synchronization
        SCM-->>CP: Failure (false)
        CP-->>PC: Sync failure acknowledgment
    end
```

#### Flash/Beep Sync Flow

```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant CP as CommandProcessor
    participant HW as Hardware
    participant FS as File System
    participant SCM as SyncClockManager
    
    alt Flash Sync
        PC->>CP: FLASH_SYNC command
        CP->>HW: triggerVisualStimulusWithDuration()
        HW->>HW: Turn on camera flash/torch
        HW->>HW: Wait for duration
        HW->>HW: Turn off camera flash/torch
        CP->>SCM: getSyncedTimestamp()
        CP->>FS: createFlashSyncMarker()
        CP-->>PC: Flash sync acknowledgment
    else Beep Sync
        PC->>CP: BEEP_SYNC command
        CP->>HW: triggerAudioStimulusWithParameters()
        HW->>HW: Generate tone with specified parameters
        CP->>SCM: getSyncedTimestamp()
        CP->>FS: createBeepSyncMarker()
        CP-->>PC: Beep sync acknowledgment
    end
```

### File System Architecture

#### Calibration File Organization

```
/Android/data/com.multisensor.recording/files/
├── Pictures/
│   └── Calibration/
│       ├── calib_20250729_171900_001_rgb.jpg
│       ├── calib_20250729_171900_001_thermal.png
│       ├── calib_20250729_171905_002_rgb.jpg
│       └── calib_20250729_171905_002_thermal.png
└── sync_markers/
    ├── flash_sync_sync001_1690647540123.txt
    ├── beep_sync_sync002_1690647545456.txt
    └── stimulus_sync_marker_1690647550789.txt
```

#### Sync Marker File Format

```
FLASH_SYNC_MARKER
sync_id=sync001
duration_ms=200
device_time=1690647540123
synced_time=1690647541123
session_id=session_20250729_171900
recording_active=true
```

### Network Protocol Extensions

#### New Command Types

```json
{
  "command": "capture_calibration",
  "calibration_id": "calib_001",
  "capture_rgb": true,
  "capture_thermal": true,
  "high_resolution": true
}
```

```json
{
  "command": "sync_time",
  "pc_timestamp": 1690647540123,
  "sync_id": "sync_001"
}
```

```json
{
  "command": "flash_sync",
  "duration_ms": 200,
  "sync_id": "flash_001"
}
```

```json
{
  "command": "beep_sync",
  "frequency_hz": 1000,
  "duration_ms": 500,
  "volume": 0.8,
  "sync_id": "beep_001"
}
```

### UI Architecture Integration

#### MainActivity Enhancements

```mermaid
graph LR
    subgraph "MainActivity UI Components"
        CB[Calibration Button]
        SS[Sync Status Display]
        FB[Flash Test Button]
        BB[Beep Test Button]
        CS[Clock Sync Button]
    end
    
    subgraph "Backend Integration"
        CB --> CCM[CalibrationCaptureManager]
        SS --> SCM[SyncClockManager]
        FB --> CP[CommandProcessor.testFlashSync]
        BB --> CP2[CommandProcessor.testBeepSync]
        CS --> CP3[CommandProcessor.testClockSync]
    end
    
    subgraph "Feedback Systems"
        CCM --> VF[Visual Feedback]
        CCM --> AF[Audio Feedback]
        CCM --> TF[Toast Messages]
    end
```

### Performance Considerations

#### Timing Requirements

- **Calibration Capture Coordination**: RGB and thermal captures should occur within 100ms of each other
- **Clock Synchronization Accuracy**: ±50ms accuracy for multi-device coordination
- **Flash/Beep Sync Response**: <10ms response time from command reception to stimulus trigger
- **File I/O Performance**: Calibration images saved within 2 seconds of capture

#### Memory Management

- **Image Buffer Management**: Proper cleanup of Camera2 Image objects and Bitmap resources
- **Concurrent Operations**: Thread-safe calibration capture with atomic counters
- **File System Cleanup**: Automatic cleanup of old calibration sessions if storage is limited

### Error Handling Architecture

```mermaid
graph TD
    subgraph "Error Sources"
        CE[Camera Errors]
        TE[Thermal Errors]
        SE[Sync Errors]
        NE[Network Errors]
        FE[File System Errors]
    end
    
    subgraph "Error Handling"
        CE --> EH[Error Handler]
        TE --> EH
        SE --> EH
        NE --> EH
        FE --> EH
    end
    
    subgraph "Recovery Actions"
        EH --> UR[User Notification]
        EH --> LG[Error Logging]
        EH --> RT[Retry Logic]
        EH --> FB[Fallback Behavior]
    end
```

### Testing Architecture

#### Test Coverage Strategy

```mermaid
graph TB
    subgraph "Unit Tests"
        UT1[CalibrationCaptureManagerTest]
        UT2[SyncClockManagerTest]
        UT3[CommandProcessorTest]
    end
    
    subgraph "Integration Tests"
        IT1[Milestone28IntegrationTest]
        IT2[DataFlowIntegrationTest]
        IT3[NetworkIntegrationTest]
    end
    
    subgraph "UI Tests"
        UIT1[MainActivity UI Tests]
        UIT2[Calibration Workflow Tests]
        UIT3[Sync Status Display Tests]
    end
    
    subgraph "Hardware Tests"
        HT1[Camera Integration Tests]
        HT2[Thermal Camera Tests]
        HT3[Flash/Audio Tests]
    end
```

### Security Considerations

#### Data Protection

- **Calibration Images**: Stored in app-specific external storage with appropriate permissions
- **Sync Markers**: Contains timing information but no sensitive data
- **Network Commands**: Validated and sanitized before processing
- **File Access**: Proper FileProvider implementation for secure file sharing

#### Access Control

- **Camera Permissions**: Required for RGB camera and flash control
- **Storage Permissions**: Managed through scoped storage or legacy permissions
- **Network Access**: Local network communication only, no internet access required

### Deployment Architecture

#### Component Dependencies

```mermaid
graph LR
    subgraph "Core Dependencies"
        CCM --> CR[CameraRecorder]
        CCM --> TR[ThermalRecorder]
        CCM --> SCM[SyncClockManager]
        CP --> CCM
        CP --> SCM
    end
    
    subgraph "External Dependencies"
        CR --> CAM2[Camera2 API]
        TR --> TSDK[Topdon SDK]
        CP --> NET[Network Layer]
        ALL --> HILT[Hilt DI]
    end
```

### Future Enhancements

#### Planned Improvements

1. **Advanced Sync Algorithms**: NTP-style round-trip time compensation
2. **Multi-Camera Support**: Support for multiple RGB cameras per device
3. **Calibration Validation**: Automatic quality assessment of calibration images
4. **Cloud Integration**: Optional cloud storage for calibration data
5. **Real-time Preview**: Live preview during calibration capture
6. **Batch Operations**: Multiple calibration captures in sequence

### Conclusion

Milestone 2.8 successfully implements a comprehensive calibration capture and synchronization system with robust architecture, proper error handling, and extensive test coverage. The modular design allows for easy maintenance and future enhancements while maintaining high performance and reliability standards.
