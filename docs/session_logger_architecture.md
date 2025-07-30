# Session Logger Architecture Documentation

**Date:** 2025-07-30  
**Milestone:** 3.8 - Session Metadata Logging and Review  
**Author:** Multi-Sensor Recording System Team

## Overview

This document provides comprehensive architectural documentation for the SessionLogger system implemented in Milestone 3.8. The SessionLogger provides structured JSON event logging, real-time UI feedback, and post-session review capabilities for the Multi-Sensor Recording System.

## System Architecture Overview

```mermaid
graph TB
    subgraph "Multi-Sensor Recording System"
        subgraph "GUI Layer"
            MW[MainWindow]
            SRD[SessionReviewDialog]
            SP[StimulusPanel]
            DP[DevicePanel]
            PP[PreviewPanel]
        end
        
        subgraph "Session Management Layer"
            SL[SessionLogger]
            SM[SessionManager]
        end
        
        subgraph "Network Layer"
            JS[JsonSocketServer]
            DC[DeviceConnection]
        end
        
        subgraph "Media Layer"
            SC[StimulusController]
            WC[WebcamCapture]
        end
        
        subgraph "Storage Layer"
            JF[JSON Log Files]
            SF[Session Folders]
            VF[Video Files]
            CF[Calibration Files]
        end
    end
    
    subgraph "External Devices"
        AD[Android Devices]
        TC[Thermal Cameras]
        SH[Shimmer Sensors]
        USB[USB Webcams]
    end
    
    %% Main connections
    MW --> SL
    MW --> SM
    MW --> JS
    MW --> SC
    MW --> WC
    MW --> SRD
    
    SL --> JF
    SM --> SF
    SC --> VF
    WC --> VF
    
    JS --> AD
    AD --> TC
    AD --> SH
    WC --> USB
    
    %% Data flow
    SL -.->|Qt Signals| MW
    SRD -.->|File Access| SF
    SRD -.->|Read Logs| JF
    
    style SL fill:#e1f5fe
    style SRD fill:#e8f5e8
    style JF fill:#fff3e0
    style SF fill:#fff3e0
```

## SessionLogger Component Architecture

```mermaid
graph TB
    subgraph "SessionLogger Core"
        SL[SessionLogger Class]
        
        subgraph "Event Processing"
            EP[Event Processor]
            TG[Timestamp Generator]
            FMT[Event Formatter]
        end
        
        subgraph "Storage Management"
            JW[JSON Writer]
            FS[File System Manager]
            FL[File Locker]
        end
        
        subgraph "UI Integration"
            QS[Qt Signals]
            UM[UI Message Formatter]
        end
        
        subgraph "Thread Safety"
            TL[Threading Lock]
            TS[Thread Synchronizer]
        end
    end
    
    subgraph "External Interfaces"
        MW[MainWindow]
        SM[SessionManager]
        DISK[File System]
    end
    
    %% Internal connections
    SL --> EP
    SL --> JW
    SL --> QS
    SL --> TL
    
    EP --> TG
    EP --> FMT
    JW --> FS
    JW --> FL
    QS --> UM
    
    %% External connections
    MW -.->|Event Calls| SL
    SL -.->|Qt Signals| MW
    SM -.->|Session Info| SL
    FS --> DISK
    
    style SL fill:#e1f5fe
    style EP fill:#f3e5f5
    style JW fill:#e8f5e8
    style QS fill:#fff8e1
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant MW as MainWindow
    participant SL as SessionLogger
    participant SM as SessionManager
    participant JS as JsonSocketServer
    participant AD as Android Device
    participant FS as File System
    participant SRD as SessionReviewDialog
    
    Note over MW,SRD: Session Start Flow
    MW->>SM: create_session()
    MW->>SL: start_session(devices)
    SL->>FS: create_log_file()
    SL->>MW: session_started signal
    
    Note over MW,SRD: Event Logging Flow
    MW->>JS: broadcast_command("start_record")
    JS->>AD: send start command
    AD->>JS: acknowledge command
    JS->>MW: ack_received signal
    MW->>SL: log_device_ack(device_id)
    SL->>FS: write_event_to_json()
    SL->>MW: log_entry_added signal
    
    Note over MW,SRD: Session End Flow
    MW->>SL: end_session()
    SL->>FS: finalize_json_file()
    SL->>MW: session_ended signal
    MW->>SRD: show_session_review_dialog()
    SRD->>FS: read_session_files()
    SRD->>FS: read_json_log()
```

## Event Type Architecture

```mermaid
graph LR
    subgraph "Session Events"
        SS[session_start]
        SE[session_end]
    end
    
    subgraph "Device Events"
        DC[device_connected]
        DD[device_disconnected]
        DA[device_ack]
    end
    
    subgraph "Recording Events"
        SR[start_record]
        ST[stop_record]
        FR[file_received]
    end
    
    subgraph "Stimulus Events"
        SP[stimulus_play]
        STO[stimulus_stop]
        MK[marker]
    end
    
    subgraph "Calibration Events"
        CC[calibration_capture]
        CD[calibration_done]
    end
    
    subgraph "Error Events"
        ER[error]
    end
    
    subgraph "SessionLogger"
        SL[Event Logger]
        JF[JSON File]
    end
    
    SS --> SL
    SE --> SL
    DC --> SL
    DD --> SL
    DA --> SL
    SR --> SL
    ST --> SL
    FR --> SL
    SP --> SL
    STO --> SL
    MK --> SL
    CC --> SL
    CD --> SL
    ER --> SL
    
    SL --> JF
    
    style SL fill:#e1f5fe
    style JF fill:#fff3e0
```

## File System Architecture

```mermaid
graph TB
    subgraph "Project Root"
        subgraph "recordings/"
            subgraph "session_20250730_143022/"
                JL[session_20250730_143022_log.json]
                SM[session_metadata.json]
                
                subgraph "Device Files"
                    WV[webcam_video.mp4]
                    P1V[phone1_rgb.mp4]
                    P1T[phone1_thermal.mp4]
                    P2V[phone2_rgb.mp4]
                    P2T[phone2_thermal.mp4]
                end
                
                subgraph "Calibration Files"
                    C1[calib_phone1.jpg]
                    C2[calib_phone2.jpg]
                    CR[calibration_results.json]
                end
                
                subgraph "Export Files"
                    ES[session_summary.json]
                end
            end
        end
    end
    
    subgraph "SessionLogger"
        SL[SessionLogger]
    end
    
    subgraph "SessionReviewDialog"
        SRD[Review Dialog]
    end
    
    SL --> JL
    SL --> SM
    SRD --> JL
    SRD --> SM
    SRD --> WV
    SRD --> P1V
    SRD --> P1T
    SRD --> P2V
    SRD --> P2T
    SRD --> C1
    SRD --> C2
    SRD --> CR
    SRD --> ES
    
    style JL fill:#e1f5fe
    style SRD fill:#e8f5e8
```

## Qt Signal Integration Architecture

```mermaid
graph TB
    subgraph "SessionLogger Signals"
        LES[log_entry_added]
        SSS[session_started]
        SES[session_ended]
        ELS[error_logged]
    end
    
    subgraph "MainWindow Slots"
        LM[log_message]
        SLSS[on_session_logger_session_started]
        SLSE[on_session_logger_session_ended]
        SLE[on_session_logger_error]
    end
    
    subgraph "UI Components"
        LD[Log Dock Widget]
        SB[Status Bar]
        MB[Message Boxes]
        SRD[SessionReviewDialog]
    end
    
    LES -.->|Qt Signal| LM
    SSS -.->|Qt Signal| SLSS
    SES -.->|Qt Signal| SLSE
    ELS -.->|Qt Signal| SLE
    
    LM --> LD
    SLSS --> SB
    SLSE --> MB
    SLSE --> SRD
    SLE --> SB
    
    style LES fill:#e1f5fe
    style SSS fill:#e1f5fe
    style SES fill:#e1f5fe
    style ELS fill:#e1f5fe
    style SRD fill:#e8f5e8
```

## Thread Safety Architecture

```mermaid
graph TB
    subgraph "Main Thread"
        MW[MainWindow]
        UI[UI Components]
    end
    
    subgraph "Background Threads"
        NT[Network Thread]
        WT[Webcam Thread]
        ST[Stimulus Thread]
    end
    
    subgraph "SessionLogger"
        SL[SessionLogger Core]
        TL[Threading Lock]
        QS[Qt Signals]
    end
    
    subgraph "File System"
        FS[JSON Files]
    end
    
    MW -->|Direct Calls| SL
    NT -->|Thread-Safe Calls| SL
    WT -->|Thread-Safe Calls| SL
    ST -->|Thread-Safe Calls| SL
    
    SL --> TL
    TL --> FS
    
    SL -.->|Qt Signals| MW
    SL -.->|Qt Signals| UI
    
    style TL fill:#ffebee
    style QS fill:#e8f5e8
```

## Integration Points

### 1. MainWindow Integration
- **Event Logging**: All major UI events are logged through SessionLogger
- **Signal Handling**: Qt signals provide real-time UI updates
- **Session Management**: Coordinates with SessionManager for folder management
- **Review Dialog**: Launches SessionReviewDialog after session completion

### 2. Device Integration
- **JsonSocketServer**: Logs device connections, acknowledgments, and errors
- **WebcamCapture**: Logs webcam recording events and file creation
- **Device Events**: All device interactions are captured with timestamps

### 3. Stimulus Integration
- **StimulusController**: Logs stimulus playback start/stop events
- **Event Markers**: User-generated markers with stimulus timeline correlation
- **Media Tracking**: Records media file names and playback timing

### 4. File System Integration
- **Session Folders**: Organized file structure per session
- **JSON Logging**: Structured event logging with immediate disk writes
- **File Tracking**: All session files are cataloged and accessible

## Performance Considerations

### 1. Thread Safety
- **Threading.Lock**: Ensures thread-safe access to shared resources
- **Qt Signals**: Proper cross-thread communication for UI updates
- **Atomic Operations**: File writes are atomic to prevent corruption

### 2. File I/O Optimization
- **Immediate Flushing**: Events are written immediately with fsync
- **JSON Structure**: Efficient JSON structure for fast parsing
- **File Locking**: Prevents concurrent access issues

### 3. Memory Management
- **Event Buffering**: Events are stored in memory and written to disk
- **Resource Cleanup**: Proper cleanup of file handles and resources
- **Memory Efficiency**: Minimal memory footprint for event storage

## Error Handling Strategy

### 1. Logging Errors
- **Categorized Errors**: Different error types for different scenarios
- **Context Information**: Device ID, timestamps, and error messages
- **Error Propagation**: Errors are logged and signaled to UI

### 2. Recovery Mechanisms
- **Crash Recovery**: Valid JSON maintained even during crashes
- **Session Recovery**: Ability to resume logging after interruption
- **File Validation**: JSON structure validation and repair

### 3. User Feedback
- **Real-Time Alerts**: Immediate error notification through UI
- **Error Logging**: All errors are logged for post-session analysis
- **Graceful Degradation**: System continues operating despite errors

## Future Enhancements

### 1. Advanced Analytics
- **Performance Metrics**: Detailed timing and performance analysis
- **Statistical Analysis**: Session statistics and trend analysis
- **Data Visualization**: Graphical representation of session data

### 2. Enhanced Review Features
- **Video Synchronization**: Synchronized playback of multiple video streams
- **Timeline Visualization**: Interactive timeline with event markers
- **Export Capabilities**: Multiple export formats for analysis tools

### 3. Cloud Integration
- **Remote Storage**: Cloud backup of session data
- **Collaborative Review**: Multi-user session review capabilities
- **Real-Time Monitoring**: Remote monitoring of active sessions

## Conclusion

The SessionLogger architecture provides a robust, scalable, and maintainable solution for comprehensive session metadata logging. The system integrates seamlessly with existing components while providing new capabilities for session review and analysis. The architecture supports future enhancements and maintains high performance through careful design of thread safety, file I/O, and error handling mechanisms.
