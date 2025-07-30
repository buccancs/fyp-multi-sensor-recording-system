# Android App Architecture Diagram

## Current Architecture Overview

This diagram illustrates the current Android application architecture and highlights the identified design flaws.

```mermaid
graph TB
    subgraph "Main Application Layer"
        MA[MainActivity<br/>GOD CLASS<br/>1,410 lines, 80+ methods<br/>- Permissions<br/>- USB Handling<br/>- UI Updates<br/>- Recording<br/>- Calibration<br/>- Shimmer Integration<br/>- Sync Testing<br/>- Battery Monitoring]
        
        subgraph "Other Activities"
            NCA[NetworkConfigActivity]
            FVA[FileViewActivity]
            SCA[ShimmerConfigActivity]
            SA[SettingsActivity]
        end
        
        MVM[MainViewModel]
        RS[RecordingService]
    end
    
    subgraph "IRCamera Library - 🚨 OVER-MODULARIZED"
        subgraph "Thermal Components - 🚨 CODE DUPLICATION"
            TC1[thermal<br/>- GalleryActivity<br/>- ThermalFragment<br/>- GalleryAdapter<br/>- ThermalActionEvent]
            TC2[thermal-ir<br/>- IRGalleryDetail04Activity<br/>- GalleryAdapter<br/>- ThermalActionEvent<br/>- 99+ classes]
            TC3[thermal-hik]
            TC4[thermal-lite]
            TC5[thermal04]
            TC6[thermal07]
        end
        
        subgraph "Lib Modules"
            LA[libapp]
            LC[libcom]
            LH[libhik]
            LI[libir]
            LM[libmatrix]
            LME[libmenu]
            LU[libui]
        end
        
        subgraph "Component Modules"
            CC[CommonComponent]
            E3D[edit3d]
            H[house]
            P[pseudo]
            T[transfer]
            U[user]
        end
        
        subgraph "Other Modules"
            BM[BleModule]
            RSB[RangeSeekBar]
            CL[commonlibrary]
        end
    end
    
    subgraph "External Libraries"
        subgraph "Shimmer SDK - 🚨 MULTIPLE VERSIONS"
            SS1[shimmerandroidinstrumentdriver-3.2.3_beta.aar]
            SS2[shimmerbluetoothmanager-0.11.4_beta.jar]
            SS3[shimmerdriver-0.11.4_beta.jar]
            SS4[shimmerdriverpc-0.11.4_beta.jar]
        end
        
        subgraph "Topdon Thermal SDK"
            TS1[topdon_1.3.7.aar]
            TS2[libusbdualsdk_1.3.4.aar]
            TS3[opengl_1.3.2.aar]
            TS4[suplib-release.aar]
        end
    end
    
    subgraph "Android System - 🚨 EXCESSIVE PERMISSIONS"
        AP[Android Permissions<br/>98+ permissions requested<br/>- CALL_PHONE<br/>- READ_SMS<br/>- MANAGE_EXTERNAL_STORAGE<br/>- CAMERA<br/>- RECORD_AUDIO<br/>- BLUETOOTH<br/>- LOCATION<br/>- And many more...]
    end
    
    %% Main connections
    MA --> MVM
    MA --> RS
    MA --> NCA
    MA --> FVA
    MA --> SCA
    MA --> SA
    
    %% MainActivity directly accesses everything (God Class problem)
    MA -.->|Direct Access| TC1
    MA -.->|Direct Access| TC2
    MA -.->|Direct Access| SS1
    MA -.->|Direct Access| TS1
    MA -.->|Requests All| AP
    
    %% Duplication arrows
    TC1 -.->|Duplicated Code| TC2
    TC2 -.->|Duplicated Code| TC3
    TC3 -.->|Duplicated Code| TC4
    TC4 -.->|Duplicated Code| TC5
    TC5 -.->|Duplicated Code| TC6
    
    %% External dependencies
    MA --> SS1
    MA --> SS2
    MA --> SS3
    MA --> SS4
    MA --> TS1
    MA --> TS2
    MA --> TS3
    MA --> TS4
    
    %% Styling
    classDef problemClass fill:#ffcccc,stroke:#ff0000,stroke-width:3px
    classDef duplicateClass fill:#ffffcc,stroke:#ffaa00,stroke-width:2px
    classDef normalClass fill:#ccffcc,stroke:#00aa00,stroke-width:1px
    
    class MA problemClass
    class TC1,TC2,TC3,TC4,TC5,TC6 duplicateClass
    class AP problemClass
    class MVM,RS,NCA,FVA,SCA,SA normalClass
```

## Architecture Problems Visualization

```mermaid
graph LR
    subgraph "Current Issues"
        GC[God Class<br/>MainActivity<br/>1,410 lines]
        OM[Over-Modularization<br/>53 build.gradle files<br/>40 AndroidManifest.xml]
        CD[Code Duplication<br/>6 thermal modules<br/>Similar classes]
        EP[Excessive Permissions<br/>98+ permissions<br/>Security risk]
        PSC[Poor Separation<br/>Business logic in UI<br/>Hard to test]
    end
    
    subgraph "Impact"
        MT[Maintenance<br/>Nightmare]
        SR[Security<br/>Risk]
        PT[Poor<br/>Testability]
        CC[Cognitive<br/>Complexity]
        BC[Build<br/>Complexity]
    end
    
    GC --> MT
    GC --> PT
    GC --> CC
    OM --> BC
    OM --> MT
    CD --> MT
    CD --> CC
    EP --> SR
    PSC --> PT
    
    classDef problem fill:#ffcccc,stroke:#ff0000,stroke-width:2px
    classDef impact fill:#ffeeee,stroke:#cc0000,stroke-width:1px
    
    class GC,OM,CD,EP,PSC problem
    class MT,SR,PT,CC,BC impact
```

## Recommended Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        subgraph "Activities"
            MA2[MainActivity<br/>Simplified<br/>200 lines approx]
            OA[Other Activities]
        end
        
        subgraph "ViewModels"
            MVM2[MainViewModel]
            RVM[RecordingViewModel]
            PVM[PermissionViewModel]
            UVM[USBViewModel]
        end
        
        subgraph "Fragments"
            RF[RecordingFragment]
            CF[CalibrationFragment]
            SF[SettingsFragment]
        end
    end
    
    subgraph "Domain Layer"
        subgraph "Use Cases"
            RUC[RecordingUseCase]
            PUC[PermissionUseCase]
            CUC[CalibrationUseCase]
            UUC[USBUseCase]
        end
        
        subgraph "Repositories"
            RR[RecordingRepository]
            CR[ConfigRepository]
            DR[DeviceRepository]
        end
    end
    
    subgraph "Data Layer"
        subgraph "Data Sources"
            LDS[LocalDataSource]
            RDS[RemoteDataSource]
            DDS[DeviceDataSource]
        end
        
        subgraph "Services"
            RS2[RecordingService]
            DS[DeviceService]
        end
    end
    
    subgraph "Consolidated Thermal Module"
        TM[ThermalModule<br/>Unified Implementation<br/>Single responsibility]
    end
    
    subgraph "Essential Permissions Only"
        EP2[Essential Permissions<br/>- CAMERA<br/>- RECORD_AUDIO<br/>- WRITE_EXTERNAL_STORAGE<br/>- BLUETOOTH if needed]
    end
    
    %% Clean connections
    MA2 --> MVM2
    MA2 --> RF
    MA2 --> CF
    MA2 --> SF
    
    MVM2 --> RUC
    RVM --> RUC
    PVM --> PUC
    UVM --> UUC
    
    RUC --> RR
    PUC --> DR
    CUC --> CR
    UUC --> DR
    
    RR --> LDS
    RR --> RS2
    CR --> LDS
    DR --> DDS
    DR --> DS
    
    TM --> DS
    MA2 --> EP2
    
    classDef clean fill:#ccffcc,stroke:#00aa00,stroke-width:2px
    classDef layer fill:#e6f3ff,stroke:#0066cc,stroke-width:1px
    
    class MA2,MVM2,RVM,PVM,UVM,RF,CF,SF clean
    class RUC,PUC,CUC,UUC,RR,CR,DR layer
    class LDS,RDS,DDS,RS2,DS,TM,EP2 clean
```

## Key Improvements in Recommended Architecture

1. **Single Responsibility**: Each class has one clear purpose
2. **Clean Architecture**: Proper layer separation (Presentation → Domain → Data)
3. **Consolidated Modules**: Unified thermal module instead of 6 separate ones
4. **Essential Permissions**: Only request what's actually needed
5. **Testable Design**: Business logic separated from UI
6. **Maintainable Structure**: Clear dependencies and boundaries

## Migration Strategy

1. **Phase 1**: Remove excessive permissions, add TODO comments
2. **Phase 2**: Extract ViewModels and Use Cases from MainActivity
3. **Phase 3**: Consolidate thermal modules
4. **Phase 4**: Implement clean architecture layers
5. **Phase 5**: Add comprehensive testing