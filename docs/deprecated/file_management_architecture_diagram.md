# File Management Architecture Diagram

## Overview

This document provides visual representations of the file management architecture implemented for the MultiSensor Recording application. The diagrams show the component relationships, data flow, and integration points with the existing system.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        FVA[FileViewActivity]
        SRV[Sessions RecyclerView]
        FRV[Files RecyclerView]
        SIP[Session Info Panel]
        SF[Search & Filter]
    end
    
    subgraph "Business Logic Layer"
        SM[SessionManager]
        FP[FileProvider]
        CP[CommandProcessor]
    end
    
    subgraph "Data Layer"
        FS[File System]
        SI[SessionInfo]
        FC[File Cache]
    end
    
    subgraph "Recording System"
        RS[RecordingService]
        CR[CameraRecorder]
        TR[ThermalRecorder]
        SR[ShimmerRecorder]
    end
    
    subgraph "External Integration"
        EA[External Apps]
        SS[System Sharing]
    end
    
    %% User Interface Connections
    FVA --> SRV
    FVA --> FRV
    FVA --> SIP
    FVA --> SF
    
    %% Business Logic Connections
    FVA --> SM
    FVA --> FP
    SM --> SI
    SM --> FS
    FP --> SS
    
    %% Recording System Integration
    SM --> RS
    RS --> CR
    RS --> TR
    RS --> SR
    
    %% External Connections
    FP --> EA
    SS --> EA
    
    %% Data Flow
    FS --> FC
    FC --> SI
    
    style FVA fill:#e1f5fe
    style SM fill:#f3e5f5
    style FP fill:#e8f5e8
    style FS fill:#fff3e0
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FVA as FileViewActivity
    participant SM as SessionManager
    participant FS as File System
    participant FP as FileProvider
    participant EA as External App
    
    Note over U,EA: Session Loading Flow
    U->>FVA: Open File Browser
    FVA->>SM: getAllSessions()
    SM->>FS: Scan session folders
    FS-->>SM: Session directories
    SM->>SM: reconstructSessionInfo()
    SM-->>FVA: List<SessionInfo>
    FVA-->>U: Display sessions
    
    Note over U,EA: File Sharing Flow
    U->>FVA: Select file to share
    FVA->>FP: getUriForFile()
    FP->>FS: Generate secure URI
    FS-->>FP: File URI
    FP-->>FVA: Secure URI
    FVA->>EA: Share Intent
    EA-->>U: File shared
    
    Note over U,EA: Search and Filter Flow
    U->>FVA: Enter search query
    FVA->>FVA: filterSessions()
    FVA->>SRV: Update adapter
    SRV-->>U: Filtered results
    
    Note over U,EA: File Operations Flow
    U->>FVA: Delete file
    FVA->>SM: deleteFile()
    SM->>FS: Remove file
    FS-->>SM: Success/Error
    SM-->>FVA: Operation result
    FVA-->>U: Update UI
```

## Component Integration Diagram

```mermaid
graph LR
    subgraph "File Management System"
        direction TB
        FVA[FileViewActivity<br/>527 lines]
        
        subgraph "UI Components"
            SL[Sessions List]
            FL[Files List]
            SI[Session Info]
            SC[Search Controls]
        end
        
        subgraph "Data Management"
            SM[SessionManager<br/>Extensions]
            FO[File Operations]
            FC[File Cache]
        end
        
        subgraph "Security Layer"
            FP[FileProvider<br/>Configuration]
            UP[URI Permissions]
            SA[Secure Access]
        end
    end
    
    subgraph "Existing System"
        direction TB
        RS[RecordingService]
        CR[CameraRecorder]
        TR[ThermalRecorder]
        SHR[ShimmerRecorder]
        
        subgraph "Storage"
            EXT[External Storage]
            INT[Internal Storage]
            CACHE[Cache Directory]
        end
    end
    
    subgraph "Testing Framework"
        direction TB
        UT[Unit Tests<br/>10/10 passing]
        UIT[UI Tests<br/>5/9 passing]
        IT[Integration Tests]
    end
    
    %% Connections
    FVA --> SL
    FVA --> FL
    FVA --> SI
    FVA --> SC
    
    FVA --> SM
    SM --> FO
    SM --> FC
    
    FVA --> FP
    FP --> UP
    FP --> SA
    
    SM --> RS
    RS --> CR
    RS --> TR
    RS --> SHR
    
    SM --> EXT
    SM --> INT
    FC --> CACHE
    
    UT --> SM
    UIT --> FVA
    IT --> FP
    
    style FVA fill:#e3f2fd
    style SM fill:#f1f8e9
    style FP fill:#fce4ec
    style RS fill:#fff8e1
```

## File Type Management Flow

```mermaid
graph TD
    subgraph "File Types"
        VF[Video Files<br/>MP4]
        RF[RAW Images<br/>DNG]
        TF[Thermal Data<br/>BIN]
    end
    
    subgraph "File Operations"
        FV[File Viewer]
        FS[File Sharing]
        FD[File Deletion]
        FE[File Export]
    end
    
    subgraph "MIME Type Handling"
        VM[video/*]
        IM[image/*]
        BM[application/octet-stream]
    end
    
    subgraph "External Integration"
        VA[Video Apps]
        IA[Image Apps]
        GA[Generic Apps]
    end
    
    %% File Type to Operations
    VF --> FV
    VF --> FS
    VF --> FD
    VF --> FE
    
    RF --> FV
    RF --> FS
    RF --> FD
    RF --> FE
    
    TF --> FV
    TF --> FS
    TF --> FD
    TF --> FE
    
    %% MIME Type Mapping
    VF --> VM
    RF --> IM
    TF --> BM
    
    %% External App Integration
    VM --> VA
    IM --> IA
    BM --> GA
    
    style VF fill:#ffebee
    style RF fill:#e8f5e8
    style TF fill:#e3f2fd
```

## Security and Permissions Flow

```mermaid
graph TB
    subgraph "Permission Management"
        RP[Runtime Permissions]
        SP[Storage Permissions]
        BP[Bluetooth Permissions]
    end
    
    subgraph "FileProvider Security"
        FP[FileProvider]
        AU[Authority Configuration]
        PP[Path Permissions]
        TU[Temporary URIs]
    end
    
    subgraph "File Access Control"
        AS[App Sandbox]
        ES[External Storage]
        CS[Cache Storage]
        SS[Secure Sharing]
    end
    
    subgraph "Data Protection"
        ED[Encrypted Data]
        SD[Secure Deletion]
        AP[Access Policies]
    end
    
    %% Permission Flow
    RP --> SP
    RP --> BP
    SP --> FP
    
    %% FileProvider Configuration
    FP --> AU
    FP --> PP
    FP --> TU
    
    %% Access Control
    PP --> AS
    PP --> ES
    PP --> CS
    TU --> SS
    
    %% Data Protection
    SS --> ED
    SS --> SD
    SS --> AP
    
    style FP fill:#e8f5e8
    style SS fill:#e3f2fd
    style ED fill:#fff3e0
```

## Testing Architecture

```mermaid
graph LR
    subgraph "Unit Testing"
        direction TB
        FML[FileManagementLogicTest<br/>10 tests]
        SIT[SessionInfo Tests]
        FHT[File Handling Tests]
        CT[Calculation Tests]
    end
    
    subgraph "UI Testing"
        direction TB
        FVAT[FileViewActivityUITest<br/>9 tests]
        ALT[Activity Launch Tests]
        SFT[Search Function Tests]
        RIT[RecyclerView Tests]
        RT[Rotation Tests]
    end
    
    subgraph "Integration Testing"
        direction TB
        SMT[SessionManager Tests]
        FPT[FileProvider Tests]
        FST[File System Tests]
    end
    
    subgraph "Test Results"
        direction TB
        UP[Unit: 100% Pass<br/>10/10]
        UIP[UI: 56% Pass<br/>5/9]
        IP[Integration: Verified]
    end
    
    %% Test Connections
    FML --> SIT
    FML --> FHT
    FML --> CT
    
    FVAT --> ALT
    FVAT --> SFT
    FVAT --> RIT
    FVAT --> RT
    
    SMT --> FST
    FPT --> FST
    
    %% Results
    FML --> UP
    FVAT --> UIP
    SMT --> IP
    
    style UP fill:#e8f5e8
    style UIP fill:#fff3e0
    style IP fill:#e3f2fd
```

## Performance and Optimization

```mermaid
graph TD
    subgraph "Performance Optimizations"
        LL[Lazy Loading]
        MM[Memory Management]
        SE[Storage Efficiency]
    end
    
    subgraph "Lazy Loading Strategies"
        AL[Async Loading]
        OD[On-Demand Files]
        BP[Background Processing]
    end
    
    subgraph "Memory Management"
        VR[View Recycling]
        BL[Bitmap Loading]
        LM[Lifecycle Management]
    end
    
    subgraph "Storage Efficiency"
        OF[Organized Files]
        TC[Temp Cleanup]
        SM[Space Monitoring]
    end
    
    %% Optimization Connections
    LL --> AL
    LL --> OD
    LL --> BP
    
    MM --> VR
    MM --> BL
    MM --> LM
    
    SE --> OF
    SE --> TC
    SE --> SM
    
    style LL fill:#e8f5e8
    style MM fill:#e3f2fd
    style SE fill:#fff3e0
```

## Future Enhancements Roadmap

```mermaid
graph TB
    subgraph "Phase 1: User Experience"
        TH[File Thumbnails]
        PV[File Previews]
        BO[Batch Operations]
    end
    
    subgraph "Phase 2: Advanced Features"
        CI[Cloud Integration]
        FC[File Compression]
        EF[Export Formats]
    end
    
    subgraph "Phase 3: Performance"
        CM[Caching Mechanisms]
        BS[Background Sync]
        PL[Progressive Loading]
    end
    
    subgraph "Phase 4: Enterprise"
        DD[Drag & Drop]
        AF[Advanced Filters]
        MD[Metadata Display]
    end
    
    %% Phase Dependencies
    TH --> PV
    PV --> BO
    BO --> CI
    CI --> FC
    FC --> EF
    EF --> CM
    CM --> BS
    BS --> PL
    PL --> DD
    DD --> AF
    AF --> MD
    
    style TH fill:#e8f5e8
    style CI fill:#e3f2fd
    style CM fill:#fff3e0
    style DD fill:#ffebee
```

## Conclusion

The file management architecture provides a comprehensive, secure, and performant solution for managing recorded session files. The modular design ensures easy maintenance and extensibility while following Android best practices for file handling and user experience.

Key architectural benefits:
- **Separation of Concerns**: Clear boundaries between UI, business logic, and data layers
- **Security First**: FileProvider implementation with proper permissions and access control
- **Performance Optimized**: Lazy loading, memory management, and efficient storage strategies
- **Testable Design**: Comprehensive test coverage with unit, UI, and integration tests
- **Future Ready**: Extensible architecture supporting planned enhancements

The implementation successfully integrates with the existing recording system while providing users with powerful file management capabilities through an intuitive and responsive interface.
