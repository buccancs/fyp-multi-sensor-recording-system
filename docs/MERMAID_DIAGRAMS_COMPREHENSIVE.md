# Multi-Sensor Recording System - Comprehensive Architecture Diagrams

## Table of Contents

1. [Hardware Setup Architecture](#hardware-setup-architecture)
2. [Android App Architecture](#android-app-architecture)
3. [PC App Architecture](#pc-app-architecture)
4. [Complete Data Flow Architecture](#complete-data-flow-architecture)
5. [Synchronization Flow](#synchronization-flow)
6. [Networking Architecture](#networking-architecture)
7. [Data Collection Flow](#data-collection-flow)
8. [Session Management Flow](#session-management-flow)
9. [Individual Sensor Integration](#individual-sensor-integration)
10. [Camera2 Image Processing Flow](#camera2-image-processing-flow)
11. [Data File System Architecture](#data-file-system-architecture)
12. [Data Export Workflow](#data-export-workflow)
13. [Layer Architecture](#layer-architecture)
14. [Software Architecture of Android](#software-architecture-of-android)
15. [Software Architecture of PC App](#software-architecture-of-pc-app)
16. [Software Installation Flow](#software-installation-flow)
17. [System Architecture Deployment Flow](#system-architecture-deployment-flow)
18. [Testing Architecture](#testing-architecture)

---

## Hardware Setup Architecture

This diagram illustrates the physical hardware configuration and connectivity between all components in the multi-sensor recording system.

```mermaid
graph TB
    subgraph "Research Laboratory Setup"
        subgraph "Mobile Sensor Nodes"
            subgraph "Device Node 1"
                S22_1[Samsung Galaxy S22 #1<br/>📱 Primary Android Device]
                TC001_1[TopDon TC001 #1<br/>🌡️ Thermal Camera<br/>USB-C OTG]
                GSR_1[Shimmer3 GSR+ #1<br/>📊 Physiological Sensor<br/>Bluetooth LE]
                
                S22_1 ---|USB-C OTG| TC001_1
                S22_1 ---|Bluetooth LE| GSR_1
            end
            
            subgraph "Device Node 2"
                S22_2[Samsung Galaxy S22 #2<br/>📱 Secondary Android Device]
                TC001_2[TopDon TC001 #2<br/>🌡️ Thermal Camera<br/>USB-C OTG]
                GSR_2[Shimmer3 GSR+ #2<br/>📊 Physiological Sensor<br/>Bluetooth LE]
                
                S22_2 ---|USB-C OTG| TC001_2
                S22_2 ---|Bluetooth LE| GSR_2
            end
        end
        
        subgraph "Stationary Recording Infrastructure"
            PC[💻 Windows PC<br/>Master Controller<br/>Intel i7/i9 + 16GB+ RAM]
            BRIO_1[Logitech Brio 4K #1<br/>📹 USB Webcam<br/>4K @ 30fps]
            BRIO_2[Logitech Brio 4K #2<br/>📹 USB Webcam<br/>4K @ 30fps]
            STORAGE[💾 High-Speed Storage<br/>NVMe SSD 1TB+<br/>For Multi-Stream Recording]
            
            PC ---|USB 3.0| BRIO_1
            PC ---|USB 3.0| BRIO_2
            PC ---|SATA/NVMe| STORAGE
        end
        
        subgraph "Network Infrastructure"
            ROUTER[🌐 WiFi Router<br/>802.11ac/ax<br/>5GHz Preferred]
            SWITCH[🔗 Gigabit Switch<br/>Low Latency Network]
            
            ROUTER --- SWITCH
        end
    end
    
    subgraph "Connectivity Layer"
        S22_1 ---|WiFi 5GHz<br/>Socket Protocol| ROUTER
        S22_2 ---|WiFi 5GHz<br/>Socket Protocol| ROUTER
        PC ---|Ethernet<br/>Gigabit| SWITCH
        SWITCH --- ROUTER
    end
    
    subgraph "Power Management"
        UPS[⚡ Uninterruptible Power Supply<br/>Battery Backup]
        CHARGER_1[🔌 USB-C Fast Charger #1]
        CHARGER_2[🔌 USB-C Fast Charger #2]
        
        UPS --- PC
        UPS --- ROUTER
        UPS --- SWITCH
        CHARGER_1 --- S22_1
        CHARGER_2 --- S22_2
    end
    
    subgraph "Environmental Considerations"
        LIGHTING[💡 Controlled Lighting<br/>Consistent Illumination]
        TEMP[🌡️ Temperature Control<br/>20-25°C Optimal]
        ACOUSTIC[🔇 Acoustic Isolation<br/>Minimal Interference]
    end
```

## Android App Architecture

Enhanced architecture diagram showing the complete Android application structure with detailed component interactions.

```mermaid
graph TB
    subgraph "Android Application Architecture"
        subgraph "Presentation Layer"
            subgraph "Activities & Fragments"
                MA[MainActivity.kt<br/>🏠 Main Activity<br/>UI Orchestrator]
                RF[RecordingFragment<br/>📹 Recording Controls]
                DF[DevicesFragment<br/>📱 Device Management]
                CF[CalibrationFragment<br/>🎯 Calibration UI]
                FF[FilesFragment<br/>📁 File Management]
            end
            
            subgraph "ViewModels & State"
                MVM[MainViewModel<br/>🧠 UI State Management]
                RSM[RecordingStateManager<br/>📊 Recording State]
                DSM[DeviceStateManager<br/>🔗 Device Status]
            end
            
            subgraph "UI Utilities"
                UC[UIController<br/>🎨 UI Component Validation]
                NU[NavigationUtils<br/>🧭 Navigation Management]
                UU[UIUtils<br/>🛠️ UI Helper Functions]
                MAC[MainActivityCoordinator<br/>⚡ Activity Coordination]
            end
        end
        
        subgraph "Domain Layer"
            subgraph "Recording Components"
                CR[CameraRecorder<br/>📷 Camera2 API Integration<br/>4K Video + RAW Capture]
                TR[ThermalRecorder<br/>🌡️ TopDon SDK Integration<br/>Thermal Image Capture]
                SR[ShimmerRecorder<br/>📊 Bluetooth GSR Integration<br/>Physiological Data]
            end
            
            subgraph "Session Management"
                SM[SessionManager<br/>📋 Recording Sessions<br/>Lifecycle Management]
                SI[SessionInfo<br/>ℹ️ Session Metadata<br/>Status Tracking]
                SS[SensorSample<br/>📈 Data Point Abstraction]
            end
            
            subgraph "Communication"
                PCH[PCCommunicationHandler<br/>🔗 PC Socket Communication<br/>Command Processing]
                CM[ConnectionManager<br/>🌐 Network Management<br/>Reconnection Logic]
                PS[PreviewStreamer<br/>📡 Live Preview Streaming<br/>Real-time Transmission]
            end
        end
        
        subgraph "Data Layer"
            subgraph "Device Management"
                DST[DeviceStatusTracker<br/>📊 Multi-Device Status<br/>Health Monitoring]
                BM[BluetoothManager<br/>📶 Bluetooth Connectivity<br/>Shimmer Integration]
                UM[USBManager<br/>🔌 USB-C OTG Management<br/>Thermal Camera Control]
            end
            
            subgraph "Storage & Persistence"
                FS[FileSystemManager<br/>💾 Local Storage<br/>Session Organization]
                MS[MetadataSerializer<br/>📝 JSON Serialization<br/>Session Persistence]
                CS[ConfigurationStore<br/>⚙️ Settings Persistence<br/>Shared Preferences]
            end
        end
        
        subgraph "Infrastructure Layer"
            subgraph "Android Framework Integration"
                CAM2[Camera2 API<br/>📸 Low-level Camera Control<br/>Concurrent Capture]
                BLE[Bluetooth LE API<br/>📡 Low Energy Communication<br/>Shimmer Protocol]
                NET[Network API<br/>🌐 Socket Communication<br/>OkHttp Integration]
            end
            
            subgraph "Hardware Abstraction"
                HAL[Hardware Abstraction Layer<br/>🔧 Device-specific Adaptations]
                PERM[Permission Manager<br/>🔐 Runtime Permissions<br/>Security Enforcement]
                LIFE[Lifecycle Manager<br/>♻️ Component Lifecycle<br/>Resource Management]
            end
        end
    end
    
    %% Connections between layers
    MA --> MVM
    MVM --> SM
    MA --> UC
    UC --> MAC
    MAC --> NU
    
    RF --> RSM
    DF --> DSM
    CF --> CM
    FF --> FS
    
    MVM --> CR
    MVM --> TR
    MVM --> SR
    
    CR --> PCH
    TR --> PCH
    SR --> PCH
    PCH --> CM
    
    CR --> PS
    PS --> CM
    
    SM --> SI
    SR --> SS
    
    CR --> DST
    TR --> DST
    SR --> DST
    
    SR --> BM
    TR --> UM
    
    SI --> MS
    MS --> FS
    DSM --> CS
    
    CR --> CAM2
    SR --> BLE
    PCH --> NET
    
    BM --> BLE
    UM --> HAL
    CM --> NET
    
    MA --> PERM
    SM --> LIFE
```

## PC App Architecture

Comprehensive architecture diagram for the Python desktop controller application.

```mermaid
graph TB
    subgraph "Python Desktop Controller Architecture"
        subgraph "Application Layer"
            subgraph "Main Entry Point"
                APP[application.py<br/>🚀 Main Application Entry<br/>PyQt5 Application Lifecycle]
                MAIN[main.py<br/>📋 Alternative Entry Point<br/>Command Line Interface]
            end
            
            subgraph "Enhanced UI Components"
                EUI[enhanced_main_with_web.py<br/>🌐 Web-Enhanced Interface<br/>Modern UI Components]
                DUI[demo_enhanced_ui.py<br/>🎨 UI Demonstration<br/>Component Showcase]
            end
        end
        
        subgraph "Presentation Layer"
            subgraph "PyQt5 GUI Framework"
                MW[MainWindow<br/>🖼️ Primary Window<br/>Tab-based Interface]
                RT[RecordingTab<br/>🎬 Recording Controls<br/>Session Management]
                DT[DevicesTab<br/>📱 Device Connections<br/>Status Monitoring]
                CT[CalibrationTab<br/>🎯 Camera Calibration<br/>Quality Assessment]
                FT[FilesTab<br/>📁 Data Management<br/>Export Controls]
            end
            
            subgraph "Common UI Components"
                MB[ModernButton<br/>🔘 Standardized Buttons<br/>Hover Effects & Theming]
                SI[StatusIndicator<br/>🚥 Visual Status Display<br/>Color-coded Feedback]
                PI[ProgressIndicator<br/>📊 Operation Progress<br/>Real-time Updates]
                CMgr[ConnectionManager<br/>🔗 Device Connection UI<br/>Unified Controls]
            end
        end
        
        subgraph "Business Logic Layer"
            subgraph "Camera Management"
                WM[WebcamManager<br/>📹 USB Camera Control<br/>Multi-camera Support]
                DWS[DualWebcamSystem<br/>👁️ Dual Camera Coordination<br/>Synchronized Capture]
                CAM[CameraController<br/>🎮 Camera Operations<br/>Settings Management]
                REC[RecordingPipeline<br/>🎞️ Video Processing<br/>Encoding & Storage]
            end
            
            subgraph "Calibration System"
                CM[CalibrationManager<br/>📐 Complete Implementation<br/>Pattern Detection]
                CP[CalibrationProcessor<br/>🧮 OpenCV Integration<br/>Mathematical Processing]
                CQA[CalibrationQualityAssessment<br/>✅ Quality Metrics<br/>Coverage Analysis]
                CR[CalibrationResult<br/>📊 Result Management<br/>Validation & Storage]
                CDCC[CrossDeviceCalibrationCoordinator<br/>🔄 Multi-device Coordination<br/>Synchronized Calibration]
            end
            
            subgraph "Shimmer Integration"
                SM[ShimmerManager<br/>📡 Multi-Library Support<br/>Bluetooth Integration]
                SPC[ShimmerPCIntegration<br/>💻 PC Direct Connection<br/>Serial Communication]
                SB[ShimmerBluetooth<br/>📶 Bluetooth Protocol<br/>Direct Device Connection]
                SA[ShimmerAndroid<br/>📱 Android Mediated<br/>Indirect Connection]
                SD[ShimmerDataProcessor<br/>📈 Stream Processing<br/>Real-time Analysis]
            end
        end
        
        subgraph "Network & Communication Layer"
            subgraph "Session Management"
                SMgr[SessionManager<br/>📋 Socket Server<br/>Multi-device Coordination]
                NCH[NetworkCommunicationHandler<br/>🌐 Protocol Implementation<br/>Message Processing]
                DS[DeviceService<br/>🔧 Device Lifecycle<br/>Connection Management]
            end
            
            subgraph "Protocol Implementation"
                JSON[JSONProtocolHandler<br/>📄 Message Serialization<br/>Command Processing]
                WS[WebSocketHandler<br/>🔌 WebSocket Communication<br/>Real-time Streaming]
                TCP[TCPSocketManager<br/>🌐 TCP Socket Management<br/>Reliable Communication]
            end
        end
        
        subgraph "Data Processing Layer"
            subgraph "Core Processing"
                DP[DataProcessor<br/>⚙️ Multi-modal Processing<br/>Data Transformation]
                SYNC[SynchronizationEngine<br/>⏱️ Temporal Alignment<br/>Microsecond Precision]
                EXP[DataExporter<br/>📤 Export Pipeline<br/>Multiple Formats]
            end
            
            subgraph "Advanced Processing"
                CV[ComputerVision<br/>👁️ OpenCV Integration<br/>Image Analysis]
                ML[MachineLearning<br/>🤖 Data Analysis<br/>Pattern Recognition]
                STIM[StimulusController<br/>🎯 Experimental Control<br/>Timing Precision]
            end
        end
        
        subgraph "Infrastructure Layer"
            subgraph "System Integration"
                LOG[LoggingSystem<br/>📝 Comprehensive Logging<br/>Debug & Audit Trail]
                CONFIG[ConfigurationManager<br/>⚙️ Settings Management<br/>Environment Configuration]
                ERR[ErrorHandler<br/>🚨 Exception Management<br/>Recovery Mechanisms]
            end
            
            subgraph "Hardware Interface"
                USB[USBDeviceManager<br/>🔌 USB Device Detection<br/>Hardware Monitoring]
                BT[BluetoothAdapter<br/>📶 Bluetooth Management<br/>Device Discovery]
                FS[FileSystemManager<br/>💾 Storage Management<br/>Session Organization]
            end
        end
    end
    
    %% Application Flow Connections
    APP --> MW
    MAIN --> APP
    EUI --> MW
    
    MW --> RT
    MW --> DT
    MW --> CT
    MW --> FT
    
    RT --> MB
    RT --> SI
    RT --> PI
    DT --> CMgr
    
    RT --> SMgr
    DT --> WM
    CT --> CM
    FT --> EXP
    
    WM --> DWS
    DWS --> CAM
    CAM --> REC
    
    CM --> CP
    CP --> CQA
    CQA --> CR
    CM --> CDCC
    
    SMgr --> NCH
    NCH --> DS
    NCH --> JSON
    
    DS --> WS
    DS --> TCP
    
    REC --> DP
    DP --> SYNC
    SYNC --> EXP
    
    CP --> CV
    STIM --> ML
    
    SMgr --> LOG
    CM --> CONFIG
    DP --> ERR
    
    WM --> USB
    SM --> BT
    EXP --> FS
```

## Complete Data Flow Architecture

Enhanced data flow architecture showing detailed data pathways, processing stages, and synchronization mechanisms.

```mermaid
graph TB
    subgraph "Multi-Modal Data Collection Infrastructure"
        subgraph "Mobile Sensor Arrays"
            subgraph "Mobile Node 1"
                A1_CAM[📷 RGB Camera<br/>Samsung S22 #1<br/>4K @ 30fps<br/>H.264/H.265 Encoding]
                A1_THER[🌡️ Thermal Camera<br/>TopDon TC001 #1<br/>256x192 @ 25fps<br/>16-bit Raw + Processed]
                A1_GSR[📊 GSR Sensor<br/>Shimmer3 GSR+ #1<br/>1024 Hz Sampling<br/>Real-time Processing]
            end
            
            subgraph "Mobile Node 2"
                A2_CAM[📷 RGB Camera<br/>Samsung S22 #2<br/>4K @ 30fps<br/>H.264/H.265 Encoding]
                A2_THER[🌡️ Thermal Camera<br/>TopDon TC001 #2<br/>256x192 @ 25fps<br/>16-bit Raw + Processed]
                A2_GSR[📊 GSR Sensor<br/>Shimmer3 GSR+ #2<br/>1024 Hz Sampling<br/>Real-time Processing]
            end
        end
        
        subgraph "Stationary Sensor Infrastructure"
            W1[📹 USB Webcam #1<br/>Logitech Brio 4K<br/>4K @ 30fps<br/>Hardware H.264 Encoding]
            W2[📹 USB Webcam #2<br/>Logitech Brio 4K<br/>4K @ 30fps<br/>Hardware H.264 Encoding]
            ENV[🌡️ Environmental Sensors<br/>Temperature, Humidity<br/>Ambient Light Monitoring]
        end
    end
    
    subgraph "Real-Time Processing & Coordination Hub"
        subgraph "Master Controller"
            PC[💻 Windows PC Controller<br/>⚡ Real-time Orchestration<br/>🕰️ Master Clock Reference<br/>📊 Performance Monitoring]
        end
        
        subgraph "Synchronization Engine"
            SYNC[⏱️ Temporal Synchronization<br/>🎯 Microsecond Precision<br/>📈 Drift Compensation<br/>🔄 Cross-device Alignment]
            CLK[🕰️ Master Clock<br/>⚡ High-resolution Timing<br/>📡 NTP Synchronization<br/>⏰ Timestamp Generation]
        end
        
        subgraph "Processing Pipeline"
            PROC[⚙️ Data Processing Engine<br/>🔄 Multi-threaded Processing<br/>📊 Real-time Analytics<br/>🧮 Statistical Analysis]
            CAL[📐 Calibration System<br/>🎯 Geometric Correction<br/>🌡️ Sensor Calibration<br/>✅ Quality Validation]
        end
        
        subgraph "Stimulus Control"
            STIM[🎯 Stimulus Presentation<br/>⚡ Precise Timing Control<br/>📊 Event Logging<br/>🎮 Interactive Control]
            EXP[🧪 Experiment Controller<br/>📋 Protocol Management<br/>📊 Data Collection Logic<br/>⏱️ Session Timing]
        end
    end
    
    subgraph "Network Communication Layer"
        subgraph "Protocol Stack"
            WIFI[📡 WiFi 802.11ac/ax<br/>🚀 5GHz Band Priority<br/>📊 QoS Management<br/>🔒 WPA3 Security]
            SOCK[🔌 Socket Protocol<br/>📄 JSON Message Format<br/>⚡ Low-latency Communication<br/>🔄 Automatic Reconnection]
            BT[📶 Bluetooth LE<br/>📊 Shimmer Protocol<br/>⚡ Energy Efficient<br/>🔗 Reliable Pairing]
        end
        
        subgraph "Data Streams"
            PREVIEW[📡 Live Preview Stream<br/>🎞️ Compressed Video<br/>⚡ Real-time Transmission<br/>📊 Adaptive Quality]
            CMD[📋 Command Channel<br/>⚡ Bi-directional Control<br/>✅ Acknowledgment Protocol<br/>🔄 State Synchronization]
            STATUS[📊 Status Updates<br/>⚡ Health Monitoring<br/>📈 Performance Metrics<br/>🚨 Error Reporting]
        end
    end
    
    subgraph "Comprehensive Data Storage Architecture"
        subgraph "Primary Storage"
            VID[🎞️ Video Files<br/>📁 MP4 Containers<br/>🗜️ H.264/H.265 Codecs<br/>📊 Multiple Resolutions]
            RAW[📸 RAW Images<br/>📁 DNG Format<br/>🎯 Calibration Targets<br/>🔍 High Dynamic Range]
            THER[🌡️ Thermal Data<br/>📁 Binary + CSV Format<br/>📊 Temperature Maps<br/>⏱️ Synchronized Timestamps]
        end
        
        subgraph "Sensor Data"
            GSR[📊 Physiological Data<br/>📁 CSV Format<br/>📈 High-frequency Sampling<br/>⏱️ Precise Timestamps]
            META[📋 Session Metadata<br/>📄 JSON Format<br/>⚙️ Configuration Data<br/>📊 Quality Metrics]
            LOGS[📝 System Logs<br/>📁 Structured Logging<br/>🐛 Debug Information<br/>📊 Performance Data]
        end
        
        subgraph "Processed Data"
            SYNC_DATA[🔄 Synchronized Datasets<br/>⏱️ Temporal Alignment<br/>📊 Cross-modal Correlation<br/>✅ Quality Validated]
            EXPORT[📤 Export Packages<br/>📁 Research-ready Format<br/>📊 Analysis Tools<br/>📋 Documentation]
        end
    end
    
    %% Data Flow Connections
    A1_CAM -->|🛜 WiFi Stream| WIFI
    A1_THER -->|🛜 WiFi Stream| WIFI
    A1_GSR -->|📶 Bluetooth| BT
    
    A2_CAM -->|🛜 WiFi Stream| WIFI
    A2_THER -->|🛜 WiFi Stream| WIFI
    A2_GSR -->|📶 Bluetooth| BT
    
    W1 -->|🔌 USB 3.0| PC
    W2 -->|🔌 USB 3.0| PC
    ENV -->|🔌 USB/Serial| PC
    
    WIFI --> SOCK
    BT --> PC
    SOCK --> PC
    
    PC --> SYNC
    PC --> PROC
    PC --> CAL
    PC --> STIM
    
    SYNC --> CLK
    CLK --> EXP
    
    PROC --> VID
    PROC --> RAW
    PROC --> THER
    PROC --> GSR
    PROC --> META
    PROC --> LOGS
    
    CAL -.->|📐 Correction Data| VID
    CAL -.->|📐 Correction Data| RAW
    CAL -.->|🌡️ Calibration| THER
    
    STIM -.->|⏱️ Event Timing| META
    EXP -.->|📊 Experiment Data| META
    
    VID --> SYNC_DATA
    RAW --> SYNC_DATA
    THER --> SYNC_DATA
    GSR --> SYNC_DATA
    META --> SYNC_DATA
    
    SYNC_DATA --> EXPORT
    
    PC -->|📡 Preview Request| PREVIEW
    PC -->|📋 Control Commands| CMD
    PC -->|📊 Status Query| STATUS
    
    PREVIEW --> PC
    CMD --> PC
    STATUS --> PC
```

## Synchronization Flow

Detailed sequence diagram showing the complete synchronization process with timing precision and error handling.

```mermaid
sequenceDiagram
    participant PC as 💻 PC Controller<br/>Master Clock
    participant A1 as 📱 Android #1<br/>Mobile Node
    participant A2 as 📱 Android #2<br/>Mobile Node
    participant S1 as 📊 Shimmer3 #1<br/>GSR Sensor
    participant S2 as 📊 Shimmer3 #2<br/>GSR Sensor
    participant W1 as 📹 USB Webcam #1<br/>Stationary Camera
    participant W2 as 📹 USB Webcam #2<br/>Stationary Camera
    
    Note over PC,W2: System Initialization & Discovery Phase
    
    PC->>PC: 🚀 Initialize Master Clock<br/>High-resolution Timer
    PC->>PC: 🔍 Scan USB Devices<br/>Detect Webcams
    
    PC->>W1: 🎥 Initialize Camera #1<br/>Configure Settings
    PC->>W2: 🎥 Initialize Camera #2<br/>Configure Settings
    
    W1-->>PC: ✅ Camera Ready<br/>Capabilities Report
    W2-->>PC: ✅ Camera Ready<br/>Capabilities Report
    
    Note over PC,W2: Network Discovery & Connection Phase
    
    PC->>PC: 🌐 Start Socket Server<br/>Port 8080 + Preview Ports
    
    A1->>PC: 🔗 Connect Request<br/>Device ID + Capabilities
    PC->>A1: ✅ Connection Accepted<br/>Session Token
    
    A2->>PC: 🔗 Connect Request<br/>Device ID + Capabilities
    PC->>A2: ✅ Connection Accepted<br/>Session Token
    
    Note over PC,W2: Sensor Initialization Phase
    
    A1->>S1: 📶 Bluetooth Discovery<br/>Shimmer Protocol
    S1-->>A1: ✅ Pairing Successful<br/>Device Info
    
    A2->>S2: 📶 Bluetooth Discovery<br/>Shimmer Protocol
    S2-->>A2: ✅ Pairing Successful<br/>Device Info
    
    A1->>S1: ⚙️ Configure Sampling<br/>1024 Hz GSR Settings
    S1-->>A1: ✅ Configuration Set<br/>Ready for Recording
    
    A2->>S2: ⚙️ Configure Sampling<br/>1024 Hz GSR Settings
    S2-->>A2: ✅ Configuration Set<br/>Ready for Recording
    
    Note over PC,W2: Clock Synchronization Phase (Critical Timing)
    
    PC->>A1: ⏱️ Clock Sync Request<br/>T0 = PC_timestamp
    A1->>A1: 📊 Measure Local Time<br/>T1 = Android_timestamp
    A1->>PC: ⏱️ Clock Response<br/>T1 + Network_delay
    
    PC->>A2: ⏱️ Clock Sync Request<br/>T0 = PC_timestamp  
    A2->>A2: 📊 Measure Local Time<br/>T1 = Android_timestamp
    A2->>PC: ⏱️ Clock Response<br/>T1 + Network_delay
    
    PC->>PC: 🧮 Calculate Offsets<br/>Compensate Network Latency
    PC->>A1: 📐 Time Offset Correction<br/>Δt1 = calculated_offset
    PC->>A2: 📐 Time Offset Correction<br/>Δt2 = calculated_offset
    
    Note over PC,W2: Recording Preparation Phase
    
    PC->>PC: 📋 Create Session Folder<br/>Generate Session ID
    PC->>PC: 📄 Initialize Metadata<br/>Device Configuration
    
    PC->>A1: 🎬 Prepare Recording<br/>Session Config
    A1->>A1: 📁 Create Local Storage<br/>Session Folder
    A1->>PC: ✅ Ready for Recording<br/>Storage Confirmed
    
    PC->>A2: 🎬 Prepare Recording<br/>Session Config
    A2->>A2: 📁 Create Local Storage<br/>Session Folder
    A2->>PC: ✅ Ready for Recording<br/>Storage Confirmed
    
    Note over PC,W2: Synchronized Recording Start (Critical Timing)
    
    PC->>PC: ⏰ Calculate Start Time<br/>T_start = now + 2000ms
    
    PC->>A1: 🚀 Start Recording Command<br/>T_start = synchronized_time
    PC->>A2: 🚀 Start Recording Command<br/>T_start = synchronized_time
    PC->>W1: 🎥 Start USB Recording<br/>T_start = synchronized_time
    PC->>W2: 🎥 Start USB Recording<br/>T_start = synchronized_time
    
    par Synchronized Recording Initiation
        A1->>A1: ⏳ Wait for T_start<br/>Precise Timing
        A1->>A1: 🎬 Start Camera Recording<br/>RGB + RAW Capture
        A1->>A1: 🌡️ Start Thermal Recording<br/>TC001 Capture
        A1->>S1: 📊 Start GSR Recording<br/>Begin Data Stream
    and
        A2->>A2: ⏳ Wait for T_start<br/>Precise Timing
        A2->>A2: 🎬 Start Camera Recording<br/>RGB + RAW Capture
        A2->>A2: 🌡️ Start Thermal Recording<br/>TC001 Capture
        A2->>S2: 📊 Start GSR Recording<br/>Begin Data Stream
    and
        PC->>PC: ⏳ Wait for T_start<br/>Precise Timing
        PC->>PC: 🎥 Start Webcam #1<br/>4K Capture
        PC->>PC: 🎥 Start Webcam #2<br/>4K Capture
    end
    
    Note over PC,W2: Active Recording Phase with Monitoring
    
    loop Real-time Data Streaming
        S1->>A1: 📊 GSR Data Packet<br/>1024 Hz Samples
        S2->>A2: 📊 GSR Data Packet<br/>1024 Hz Samples
        
        A1->>PC: 📡 Preview Frame + Status<br/>Compressed Stream
        A2->>PC: 📡 Preview Frame + Status<br/>Compressed Stream
        
        A1->>PC: 📊 Device Status Update<br/>Health + Performance
        A2->>PC: 📊 Device Status Update<br/>Health + Performance
        
        PC->>PC: 📈 Monitor Performance<br/>Resource Usage
        PC->>PC: 🔄 Log Synchronization<br/>Timestamp Validation
    end
    
    Note over PC,W2: Recording Termination Phase
    
    PC->>A1: 🛑 Stop Recording Command<br/>Graceful Shutdown
    PC->>A2: 🛑 Stop Recording Command<br/>Graceful Shutdown
    PC->>W1: 🛑 Stop USB Recording<br/>Finalize Files
    PC->>W2: 🛑 Stop USB Recording<br/>Finalize Files
    
    par Synchronized Recording Stop
        A1->>S1: 🛑 Stop GSR Recording<br/>Finalize Data
        A1->>A1: 🛑 Stop Camera Recording<br/>Finalize Video
        A1->>A1: 🛑 Stop Thermal Recording<br/>Finalize Thermal
        A1->>PC: ✅ Recording Stopped<br/>File Count + Size
    and
        A2->>S2: 🛑 Stop GSR Recording<br/>Finalize Data
        A2->>A2: 🛑 Stop Camera Recording<br/>Finalize Video
        A2->>A2: 🛑 Stop Thermal Recording<br/>Finalize Thermal
        A2->>PC: ✅ Recording Stopped<br/>File Count + Size
    end
    
    Note over PC,W2: Post-Recording Validation Phase
    
    PC->>PC: 📊 Generate Session Report<br/>Synchronization Analysis
    PC->>PC: ✅ Validate Data Integrity<br/>File Completeness Check
    PC->>PC: 📋 Update Session Metadata<br/>Final Statistics
    
    PC->>A1: 📄 Request Session Summary<br/>Local Statistics
    A1-->>PC: 📊 Session Summary<br/>Files + Metadata
    
    PC->>A2: 📄 Request Session Summary<br/>Local Statistics
    A2-->>PC: 📊 Session Summary<br/>Files + Metadata
    
    PC->>PC: 📁 Archive Session Data<br/>Backup + Organization
```

## Networking Architecture

Comprehensive networking architecture showing protocol layers, security, and communication patterns.

```mermaid
graph TB
    subgraph "Multi-Layer Network Architecture"
        subgraph "Physical Network Infrastructure"
            subgraph "Wireless Infrastructure"
                ROUTER[🌐 WiFi Router/Access Point<br/>📡 802.11ac/ax (WiFi 6)<br/>🚀 5GHz Primary Band<br/>📊 QoS Traffic Shaping]
                MESH[🔗 Mesh Network Support<br/>📶 Extended Coverage<br/>🔄 Automatic Roaming<br/>⚡ Load Balancing]
            end
            
            subgraph "Wired Infrastructure"
                SWITCH[🔗 Gigabit Ethernet Switch<br/>⚡ Low-latency Switching<br/>📊 Port Mirroring<br/>🔒 VLAN Support]
                BACKBONE[🌐 Network Backbone<br/>🚀 Gigabit Connectivity<br/>📈 Bandwidth Management<br/>🔄 Redundancy]
            end
        end
        
        subgraph "Network Protocol Stack"
            subgraph "Application Layer Protocols"
                HTTP[🌐 HTTP/HTTPS<br/>📄 RESTful API<br/>🔒 TLS 1.3 Encryption<br/>📊 JSON Data Format]
                WS[🔌 WebSocket Protocol<br/>⚡ Real-time Communication<br/>📡 Bi-directional Streaming<br/>🔄 Automatic Reconnection]
                CUSTOM[📋 Custom Protocol<br/>⚡ Low-latency Commands<br/>📊 Binary + JSON Hybrid<br/>✅ Acknowledgment System]
            end
            
            subgraph "Transport Layer"
                TCP[🚛 TCP Protocol<br/>✅ Reliable Delivery<br/>🔄 Connection Management<br/>📊 Flow Control]
                UDP[📡 UDP Protocol<br/>⚡ Low-latency Streaming<br/>🎞️ Video/Audio Data<br/>📊 Best-effort Delivery]
            end
            
            subgraph "Network Layer"
                IPv4[🌐 IPv4 Addressing<br/>📍 192.168.x.x Range<br/>🔗 NAT Translation<br/>🛣️ Routing Tables]
                IPv6[🌐 IPv6 Support<br/>🚀 Future-ready<br/>🔒 Built-in Security<br/>📈 Extended Address Space]
            end
        end
        
        subgraph "Device Communication Layers"
            subgraph "PC Controller (Server)"
                subgraph "Server Components"
                    SS[🖥️ Socket Server<br/>📍 Port 8080 (Control)<br/>⚡ Multi-threaded<br/>🔄 Connection Pool]
                    PS[📡 Preview Server<br/>📍 Ports 8081-8090<br/>🎞️ Video Streaming<br/>📊 Adaptive Bitrate]
                    API[🔗 REST API Server<br/>📍 Port 8000<br/>📄 JSON Endpoints<br/>🔒 Authentication]
                end
                
                subgraph "Communication Handlers"
                    NCH[📋 Network Communication Handler<br/>📄 Message Processing<br/>🔄 Protocol Management<br/>📊 Performance Monitoring]
                    SMH[📋 Session Management Handler<br/>🎯 Multi-device Coordination<br/>⏱️ Synchronization Logic<br/>📊 State Management]
                    EH[🚨 Error Handler<br/>🔄 Recovery Mechanisms<br/>📝 Logging System<br/>📊 Health Monitoring]
                end
            end
            
            subgraph "Android Clients"
                subgraph "Device 1 Communication"
                    SC1[📱 Socket Client #1<br/>🔗 Connection Management<br/>⚡ Auto-reconnection<br/>📊 Heartbeat Protocol]
                    PCH1[📋 PC Communication Handler #1<br/>📄 Message Parsing<br/>✅ Command Execution<br/>📊 Status Reporting]
                    PVS1[📡 Preview Streamer #1<br/>🎞️ Video Compression<br/>📊 Quality Adaptation<br/>⚡ Real-time Encoding]
                end
                
                subgraph "Device 2 Communication"
                    SC2[📱 Socket Client #2<br/>🔗 Connection Management<br/>⚡ Auto-reconnection<br/>📊 Heartbeat Protocol]
                    PCH2[📋 PC Communication Handler #2<br/>📄 Message Parsing<br/>✅ Command Execution<br/>📊 Status Reporting]
                    PVS2[📡 Preview Streamer #2<br/>🎞️ Video Compression<br/>📊 Quality Adaptation<br/>⚡ Real-time Encoding]
                end
            end
        end
        
        subgraph "Security & Quality of Service"
            subgraph "Network Security"
                WPA3[🔒 WPA3 Encryption<br/>🛡️ Advanced Security<br/>🔐 Key Management<br/>🚫 Unauthorized Access]
                FW[🛡️ Firewall Rules<br/>🚫 Port Filtering<br/>📋 Access Control Lists<br/>📊 Traffic Monitoring]
                VPN[🔒 VPN Support<br/>🌐 Secure Remote Access<br/>🔐 Encrypted Tunneling<br/>🌍 Geographic Flexibility]
            end
            
            subgraph "Quality of Service"
                QOS[📊 QoS Management<br/>⚡ Traffic Prioritization<br/>📈 Bandwidth Allocation<br/>🎯 Latency Optimization]
                DSCP[🏷️ DSCP Marking<br/>📊 Traffic Classification<br/>⚡ Priority Queuing<br/>🎯 Service Differentiation]
                BWM[📈 Bandwidth Management<br/>🎛️ Rate Limiting<br/>📊 Fair Queuing<br/>⚡ Congestion Control]
            end
        end
        
        subgraph "Communication Patterns"
            subgraph "Control Communications"
                CMD[📋 Command Channel<br/>⚡ Bi-directional Control<br/>✅ Request-Response Pattern<br/>🔄 State Synchronization]
                SYNC[⏱️ Synchronization Messages<br/>🎯 Clock Alignment<br/>📊 Timestamp Exchange<br/>⚡ Precision Timing]
                STATUS[📊 Status Updates<br/>⚡ Health Monitoring<br/>📈 Performance Metrics<br/>🚨 Error Notifications]
            end
            
            subgraph "Data Streaming"
                PREVIEW[📡 Live Preview Streaming<br/>🎞️ Compressed Video<br/>📊 Adaptive Quality<br/>⚡ Real-time Transmission]
                BULK[📦 Bulk Data Transfer<br/>💾 File Synchronization<br/>📊 Progress Monitoring<br/>✅ Integrity Verification]
                META[📄 Metadata Exchange<br/>📋 Configuration Data<br/>📊 Session Information<br/>🔄 State Persistence]
            end
        end
    end
    
    %% Network Flow Connections
    ROUTER ---|Ethernet| SWITCH
    SWITCH ---|Gigabit| BACKBONE
    
    SS -->|TCP| ROUTER
    PS -->|UDP/TCP| ROUTER
    API -->|HTTP/HTTPS| ROUTER
    
    SC1 -->|WiFi 5GHz| ROUTER
    SC2 -->|WiFi 5GHz| ROUTER
    
    SS --> NCH
    NCH --> SMH
    SMH --> EH
    
    PS --> PVS1
    PS --> PVS2
    
    PCH1 --> SC1
    PCH2 --> SC2
    
    WPA3 -.->|Security| ROUTER
    FW -.->|Protection| SWITCH
    QOS -.->|Traffic Management| ROUTER
    
    CMD -.->|Control Flow| NCH
    SYNC -.->|Timing| SMH
    STATUS -.->|Monitoring| EH
    
    PREVIEW -.->|Streaming| PS
    BULK -.->|Transfer| API
    META -.->|Configuration| SS
```

## Data Collection Flow

Comprehensive flowchart showing the complete data collection process with error handling and quality assurance.

```mermaid
flowchart TD
    START([🚀 Recording Session Start])
    
    subgraph "Pre-Recording Setup"
        INIT[📋 Initialize System<br/>🔧 Hardware Detection<br/>📊 Status Verification]
        CONFIG[⚙️ Load Configuration<br/>📄 Session Parameters<br/>🎯 Quality Settings]
        CALIB[📐 Apply Calibration<br/>✅ Validation Check<br/>📊 Quality Assessment]
    end
    
    subgraph "Device Preparation"
        subgraph "Mobile Devices"
            A1_PREP[📱 Android #1 Prep<br/>📁 Storage Setup<br/>🔋 Battery Check<br/>📡 Network Test]
            A2_PREP[📱 Android #2 Prep<br/>📁 Storage Setup<br/>🔋 Battery Check<br/>📡 Network Test]
        end
        
        subgraph "PC Components"
            PC_PREP[💻 PC Controller Prep<br/>💾 Storage Check<br/>📈 Performance Monitor<br/>🔗 USB Device Scan]
            WEB_PREP[📹 Webcam Preparation<br/>🎥 Camera Initialization<br/>⚙️ Settings Configuration<br/>🎞️ Test Capture]
        end
        
        subgraph "Sensor Networks"
            GSR_PREP[📊 GSR Sensor Prep<br/>📶 Bluetooth Connection<br/>⚙️ Sampling Configuration<br/>📈 Signal Validation]
            THER_PREP[🌡️ Thermal Prep<br/>🔌 USB-C Connection<br/>🎯 Temperature Calibration<br/>📸 Test Capture]
        end
    end
    
    subgraph "Synchronization Layer"
        CLOCK_SYNC[⏰ Clock Synchronization<br/>🎯 Time Alignment<br/>📊 Offset Calculation<br/>✅ Precision Validation]
        START_COORD[🚀 Start Coordination<br/>📋 Command Broadcasting<br/>⏱️ Scheduled Start Time<br/>🔄 Acknowledgment Collection]
    end
    
    subgraph "Active Data Collection"
        subgraph "Sensor Data Streams"
            RGB_STREAM[📷 RGB Video Stream<br/>🎞️ 4K @ 30fps<br/>📄 H.264/H.265 Encoding<br/>⏱️ Timestamp Embedding]
            THERMAL_STREAM[🌡️ Thermal Stream<br/>🌡️ 256x192 @ 25fps<br/>📊 16-bit Raw Data<br/>📈 Temperature Mapping]
            GSR_STREAM[📊 GSR Data Stream<br/>📈 1024 Hz Sampling<br/>⚡ Real-time Processing<br/>📋 Quality Monitoring]
            WEBCAM_STREAM[📹 USB Webcam Stream<br/>🎥 4K @ 30fps<br/>💻 Hardware Encoding<br/>💾 Direct Storage]
        end
        
        subgraph "Real-time Monitoring"
            STATUS_MON[📊 Status Monitoring<br/>🔋 Battery Levels<br/>💾 Storage Space<br/>📡 Network Quality]
            PREVIEW_MON[👁️ Preview Monitoring<br/>🎞️ Live Stream Display<br/>🎯 Quality Assessment<br/>⚠️ Error Detection]
            PERF_MON[⚡ Performance Monitoring<br/>🖥️ CPU Usage<br/>💾 Memory Usage<br/>🌡️ Temperature Levels]
        end
    end
    
    subgraph "Data Processing Pipeline"
        subgraph "Real-time Processing"
            SYNC_PROC[🔄 Synchronization Processing<br/>⏱️ Timestamp Validation<br/>📊 Drift Compensation<br/>🎯 Alignment Correction]
            QUALITY_PROC[✅ Quality Processing<br/>📊 Signal Quality Check<br/>🚨 Error Detection<br/>🔧 Auto-correction]
            META_PROC[📋 Metadata Processing<br/>📄 Session Information<br/>⚙️ Configuration Data<br/>📊 Performance Metrics]
        end
        
        subgraph "Storage Management"
            LOCAL_STORE[💾 Local Storage<br/>📁 File Organization<br/>🗂️ Session Folders<br/>📝 Naming Convention]
            BACKUP_STORE[📦 Backup Storage<br/>🔄 Redundant Copies<br/>✅ Integrity Verification<br/>📊 Progress Tracking]
            COMPRESS_STORE[🗜️ Compression Storage<br/>📊 Space Optimization<br/>⚡ Real-time Compression<br/>📈 Quality Preservation]
        end
    end
    
    subgraph "Error Handling & Recovery"
        ERROR_DETECT[🚨 Error Detection<br/>📊 Signal Monitoring<br/>🔍 Anomaly Detection<br/>⚠️ Threshold Checking]
        AUTO_RECOVER[🔧 Auto Recovery<br/>🔄 Connection Retry<br/>⚡ Resource Reallocation<br/>📊 State Restoration]
        MANUAL_INTER[👤 Manual Intervention<br/>🚨 User Notification<br/>🎮 Manual Controls<br/>📋 Decision Logging]
    end
    
    subgraph "Session Termination"
        STOP_COORD[🛑 Stop Coordination<br/>📋 Stop Commands<br/>⏱️ Graceful Shutdown<br/>✅ Completion Verification]
        DATA_FINAL[📊 Data Finalization<br/>📁 File Closure<br/>📋 Metadata Update<br/>✅ Integrity Check]
        SESSION_REPORT[📄 Session Report<br/>📊 Statistics Generation<br/>📈 Quality Assessment<br/>📋 Summary Creation]
    end
    
    %% Flow Connections
    START --> INIT
    INIT --> CONFIG
    CONFIG --> CALIB
    
    CALIB --> A1_PREP
    CALIB --> A2_PREP
    CALIB --> PC_PREP
    CALIB --> WEB_PREP
    CALIB --> GSR_PREP
    CALIB --> THER_PREP
    
    A1_PREP --> CLOCK_SYNC
    A2_PREP --> CLOCK_SYNC
    PC_PREP --> CLOCK_SYNC
    WEB_PREP --> CLOCK_SYNC
    GSR_PREP --> CLOCK_SYNC
    THER_PREP --> CLOCK_SYNC
    
    CLOCK_SYNC --> START_COORD
    START_COORD --> RGB_STREAM
    START_COORD --> THERMAL_STREAM
    START_COORD --> GSR_STREAM
    START_COORD --> WEBCAM_STREAM
    
    RGB_STREAM --> STATUS_MON
    THERMAL_STREAM --> PREVIEW_MON
    GSR_STREAM --> PERF_MON
    WEBCAM_STREAM --> STATUS_MON
    
    STATUS_MON --> SYNC_PROC
    PREVIEW_MON --> QUALITY_PROC
    PERF_MON --> META_PROC
    
    SYNC_PROC --> LOCAL_STORE
    QUALITY_PROC --> BACKUP_STORE
    META_PROC --> COMPRESS_STORE
    
    LOCAL_STORE --> ERROR_DETECT
    BACKUP_STORE --> ERROR_DETECT
    COMPRESS_STORE --> ERROR_DETECT
    
    ERROR_DETECT --> AUTO_RECOVER
    AUTO_RECOVER --> MANUAL_INTER
    MANUAL_INTER --> RGB_STREAM
    
    LOCAL_STORE --> STOP_COORD
    BACKUP_STORE --> STOP_COORD
    COMPRESS_STORE --> STOP_COORD
    
    STOP_COORD --> DATA_FINAL
    DATA_FINAL --> SESSION_REPORT
    
    SESSION_REPORT --> END([📁 Session Complete])
```

## Session Management Flow

Detailed flowchart showing the complete session lifecycle from initialization to data export.

```mermaid
flowchart TD
    START([🎬 Session Management Start])
    
    subgraph "Session Initialization"
        CREATE_ID[🆔 Generate Session ID<br/>📅 Timestamp-based<br/>🔢 Unique Identifier<br/>📋 Format: session_YYYYMMDD_HHMMSS]
        SETUP_DIR[📁 Setup Directory Structure<br/>📂 Main Session Folder<br/>📁 Device-specific Subfolders<br/>📄 Metadata Files]
        INIT_META[📋 Initialize Metadata<br/>⚙️ Configuration Parameters<br/>🕰️ Start Timestamp<br/>📊 Device Information]
    end
    
    subgraph "Device Registration"
        REG_DEVICES[📱 Register Devices<br/>🔗 Connection Verification<br/>📊 Capability Assessment<br/>✅ Status Validation]
        ASSIGN_ROLES[🎯 Assign Device Roles<br/>📱 Primary/Secondary Mobile<br/>📹 Camera Assignments<br/>📊 Sensor Allocation]
        CONFIG_DEVICES[⚙️ Configure Devices<br/>📄 Apply Settings<br/>🎯 Quality Parameters<br/>⏱️ Timing Configuration]
    end
    
    subgraph "Pre-Recording Phase"
        CALIB_CHECK[🎯 Calibration Check<br/>📐 Geometric Validation<br/>🌡️ Thermal Calibration<br/>✅ Quality Verification]
        STORAGE_CHECK[💾 Storage Verification<br/>📊 Available Space<br/>⚡ Write Speed Test<br/>🔄 Backup Availability]
        NETWORK_TEST[🌐 Network Testing<br/>📶 Connection Quality<br/>⏱️ Latency Measurement<br/>📈 Bandwidth Assessment]
    end
    
    subgraph "Recording Session Management"
        subgraph "Session Control"
            START_SESSION[🚀 Start Recording Session<br/>⏰ Synchronized Start<br/>📋 Command Broadcasting<br/>✅ Confirmation Collection]
            MONITOR_SESSION[👁️ Monitor Active Session<br/>📊 Real-time Status<br/>🔋 Resource Monitoring<br/>⚠️ Error Detection]
            CONTROL_SESSION[🎮 Session Control<br/>⏸️ Pause/Resume<br/>⚙️ Quality Adjustment<br/>🛑 Emergency Stop]
        end
        
        subgraph "Data Management"
            STREAM_MANAGE[📡 Stream Management<br/>🎞️ Video Streams<br/>📊 Sensor Data<br/>🌡️ Thermal Data]
            BUFFER_MANAGE[💾 Buffer Management<br/>🔄 Circular Buffers<br/>⚡ Memory Optimization<br/>📊 Flow Control]
            SYNC_MANAGE[⏱️ Synchronization Management<br/>🕰️ Timestamp Alignment<br/>📈 Drift Correction<br/>🎯 Precision Maintenance]
        end
    end
    
    subgraph "Real-time Quality Assurance"
        SIGNAL_QA[📊 Signal Quality Assessment<br/>📈 SNR Monitoring<br/>🎯 Threshold Checking<br/>📋 Quality Logging]
        SYNC_QA[⏱️ Synchronization QA<br/>🕰️ Timing Validation<br/>📊 Offset Monitoring<br/>⚠️ Drift Detection]
        DATA_QA[✅ Data Integrity QA<br/>🔍 Corruption Detection<br/>📊 Completeness Check<br/>🔧 Auto-correction]
    end
    
    subgraph "Session State Management"
        STATE_TRACK[📊 State Tracking<br/>🎯 Recording Status<br/>📱 Device States<br/>🔗 Connection Status]
        EVENT_LOG[📝 Event Logging<br/>⏱️ Timestamped Events<br/>🚨 Error Logging<br/>📊 Performance Metrics]
        CHECKPOINT[🔖 Checkpoint Management<br/>💾 State Persistence<br/>🔄 Recovery Points<br/>📋 Resume Capability]
    end
    
    subgraph "Session Termination"
        STOP_SESSION[🛑 Stop Recording Session<br/>📋 Stop Commands<br/>⏱️ Graceful Shutdown<br/>⏳ Completion Wait]
        FINALIZE_DATA[📊 Finalize Data<br/>📁 File Closure<br/>📋 Metadata Update<br/>✅ Integrity Verification]
        GENERATE_REPORT[📄 Generate Session Report<br/>📊 Statistics Compilation<br/>📈 Quality Analysis<br/>⚠️ Error Summary]
    end
    
    subgraph "Post-Processing & Export"
        DATA_VALIDATION[✅ Data Validation<br/>🔍 Completeness Check<br/>📊 Quality Assessment<br/>🔧 Error Correction]
        SYNC_PROCESSING[🔄 Synchronization Processing<br/>⏱️ Final Alignment<br/>📊 Cross-correlation<br/>🎯 Precision Optimization]
        EXPORT_PREP[📦 Export Preparation<br/>📁 Data Organization<br/>📋 Metadata Assembly<br/>🗜️ Compression Options]
        EXPORT_EXECUTE[📤 Execute Export<br/>💾 Multiple Formats<br/>📊 Research Package<br/>📋 Documentation]
    end
    
    subgraph "Session Archival"
        ARCHIVE_SESSION[📦 Archive Session<br/>💾 Long-term Storage<br/>🔒 Data Security<br/>📋 Index Generation]
        CLEANUP[🧹 Cleanup Operations<br/>🗑️ Temporary Files<br/>💾 Cache Cleanup<br/>📊 Resource Release]
        BACKUP_VERIFY[✅ Backup Verification<br/>🔍 Integrity Check<br/>📊 Redundancy Verification<br/>📋 Backup Catalog]
    end
    
    %% Flow Connections
    START --> CREATE_ID
    CREATE_ID --> SETUP_DIR
    SETUP_DIR --> INIT_META
    
    INIT_META --> REG_DEVICES
    REG_DEVICES --> ASSIGN_ROLES
    ASSIGN_ROLES --> CONFIG_DEVICES
    
    CONFIG_DEVICES --> CALIB_CHECK
    CALIB_CHECK --> STORAGE_CHECK
    STORAGE_CHECK --> NETWORK_TEST
    
    NETWORK_TEST --> START_SESSION
    START_SESSION --> MONITOR_SESSION
    MONITOR_SESSION --> CONTROL_SESSION
    
    START_SESSION --> STREAM_MANAGE
    STREAM_MANAGE --> BUFFER_MANAGE
    BUFFER_MANAGE --> SYNC_MANAGE
    
    MONITOR_SESSION --> SIGNAL_QA
    SIGNAL_QA --> SYNC_QA
    SYNC_QA --> DATA_QA
    
    CONTROL_SESSION --> STATE_TRACK
    STATE_TRACK --> EVENT_LOG
    EVENT_LOG --> CHECKPOINT
    
    DATA_QA --> STOP_SESSION
    CHECKPOINT --> STOP_SESSION
    STOP_SESSION --> FINALIZE_DATA
    FINALIZE_DATA --> GENERATE_REPORT
    
    GENERATE_REPORT --> DATA_VALIDATION
    DATA_VALIDATION --> SYNC_PROCESSING
    SYNC_PROCESSING --> EXPORT_PREP
    EXPORT_PREP --> EXPORT_EXECUTE
    
    EXPORT_EXECUTE --> ARCHIVE_SESSION
    ARCHIVE_SESSION --> CLEANUP
    CLEANUP --> BACKUP_VERIFY
    
    BACKUP_VERIFY --> END([✅ Session Management Complete])
```

## Individual Sensor Integration

Comprehensive diagram showing detailed integration architecture for each sensor type in the multi-sensor recording system.

```mermaid
graph TB
    subgraph "Individual Sensor Integration Architecture"
        subgraph "Samsung S22 Built-in Camera Integration"
            subgraph "Camera2 API Layer"
                CAM2_MGR[📷 CameraManager<br/>🔍 Device Discovery<br/>📊 Capability Enumeration<br/>⚙️ Characteristics Query]
                CAM2_DEV[📱 CameraDevice<br/>🔗 Session Management<br/>⚙️ Configuration Control<br/>📊 State Monitoring]
                CAM2_SESS[🎬 CameraCaptureSession<br/>🎯 Capture Requests<br/>🔄 Repeating Sessions<br/>📊 Result Processing]
            end
            
            subgraph "Capture Configuration"
                IMG_READER[📸 ImageReader<br/>🎞️ YUV_420_888 Format<br/>📊 Multiple Buffers<br/>⚡ Async Processing]
                SURF_VIEW[🖼️ SurfaceView<br/>👁️ Preview Display<br/>⚡ Real-time Rendering<br/>🎯 UI Integration]
                MEDIA_REC[🎥 MediaRecorder<br/>📹 H.264/H.265 Encoding<br/>💾 MP4 Container<br/>⚙️ Quality Settings]
            end
            
            subgraph "Processing Pipeline"
                FRAME_PROC[🖼️ Frame Processing<br/>🎯 ROI Extraction<br/>📊 Quality Assessment<br/>⏱️ Timestamp Addition]
                FORMAT_CONV[🔄 Format Conversion<br/>📊 Color Space Transform<br/>🎯 Resolution Scaling<br/>📈 Quality Optimization]
                PREVIEW_STREAM[📡 Preview Streaming<br/>🗜️ JPEG Compression<br/>📶 Network Transmission<br/>⚡ Real-time Delivery]
            end
        end
        
        subgraph "Logitech Brio 4K USB Webcam Integration"
            subgraph "USB Interface Layer"
                USB_ENUM[🔌 USB Enumeration<br/>🔍 Device Detection<br/>📊 Descriptor Parsing<br/>⚙️ Endpoint Configuration]
                UVC_DRIVER[📹 UVC Driver Interface<br/>📊 Video Class Support<br/>⚙️ Control Extensions<br/>🎯 Format Negotiation]
                DIRECT_SHOW[🖥️ DirectShow/V4L2<br/>🎞️ Media Foundation<br/>⚙️ Filter Graph<br/>📊 Format Selection]
            end
            
            subgraph "Capture Management"
                WEBCAM_MGR[📹 WebcamManager<br/>🔍 Multi-camera Support<br/>⚙️ Settings Management<br/>📊 Status Monitoring]
                CAP_ENGINE[🎥 Capture Engine<br/>⚡ Hardware Acceleration<br/>💾 Direct Memory Access<br/>🔄 Buffer Management]
                SYNC_CTRL[⏱️ Sync Controller<br/>🕰️ Frame Timing<br/>📊 Timestamp Generation<br/>🎯 Precision Control]
            end
            
            subgraph "Quality Control"
                AUTO_FOCUS[🎯 Auto Focus Control<br/>⚡ Continuous AF<br/>📊 Focus Quality<br/>🔧 Manual Override]
                AUTO_EXPO[☀️ Auto Exposure<br/>📊 Histogram Analysis<br/>⚙️ ISO/Shutter Control<br/>🎯 Target Brightness]
                WHITE_BAL[🎨 White Balance<br/>🌡️ Color Temperature<br/>📊 Scene Analysis<br/>🎯 Natural Colors]
            end
        end
        
        subgraph "TopDon TC001 Thermal Camera Integration"
            subgraph "USB-C OTG Interface"
                OTG_MGR[🔌 OTG Manager<br/>⚡ USB Host Mode<br/>🔍 Device Recognition<br/>⚙️ Power Management]
                TOPDON_SDK[🌡️ TopDon SDK<br/>📊 Native Library<br/>🔗 JNI Interface<br/>📄 API Wrapper]
                THERMAL_DEV[🌡️ Thermal Device<br/>⚙️ Sensor Configuration<br/>📊 Calibration Data<br/>🎯 Temperature Range]
            end
            
            subgraph "Thermal Processing"
                RAW_CAPTURE[📊 Raw Thermal Capture<br/>📈 16-bit ADC Data<br/>🌡️ Temperature Matrix<br/>⏱️ Frame Timing]
                TEMP_CONV[🌡️ Temperature Conversion<br/>📊 Radiometric Calculation<br/>🎯 Emissivity Correction<br/>📈 Non-linearity Compensation]
                FALSE_COLOR[🎨 False Color Mapping<br/>🌈 Palette Application<br/>📊 Contrast Enhancement<br/>🎯 Visual Representation]
            end
            
            subgraph "Calibration System"
                THERMAL_CAL[🎯 Thermal Calibration<br/>🌡️ Blackbody Reference<br/>📊 Gain/Offset Correction<br/>✅ Accuracy Validation]
                GEOMETRIC_CAL[📐 Geometric Calibration<br/>🎯 Lens Distortion<br/>📊 Pixel Mapping<br/>🔗 RGB Alignment]
                TEMPORAL_CAL[⏱️ Temporal Calibration<br/>🕰️ Frame Synchronization<br/>📊 Delay Compensation<br/>🎯 Timestamp Alignment]
            end
        end
        
        subgraph "Shimmer3 GSR+ Sensor Integration"
            subgraph "Bluetooth LE Interface"
                BLE_MGR[📶 BLE Manager<br/>🔍 Device Scanning<br/>🔗 Connection Management<br/>📊 Service Discovery]
                SHIMMER_PROT[📊 Shimmer Protocol<br/>📄 Custom GATT Services<br/>⚙️ Configuration Commands<br/>📈 Data Streaming]
                CONN_MGR[🔗 Connection Manager<br/>📶 Signal Monitoring<br/>🔄 Auto-reconnection<br/>⚡ Power Management]
            end
            
            subgraph "GSR Data Processing"
                RAW_GSR[📊 Raw GSR Data<br/>📈 ADC Samples<br/>⚡ 1024 Hz Sampling<br/>📋 16-bit Resolution]
                SIGNAL_PROC[📈 Signal Processing<br/>🔍 Noise Filtering<br/>📊 Baseline Correction<br/>📈 Feature Extraction]
                CALIB_PROC[🎯 Calibration Processing<br/>⚙️ Gain/Offset Correction<br/>📊 Individual Calibration<br/>✅ Quality Validation]
            end
            
            subgraph "Real-time Analysis"
                STREAM_PROC[📡 Stream Processing<br/>⚡ Real-time Analysis<br/>📊 Statistical Measures<br/>🚨 Anomaly Detection]
                BUFFER_MGR[💾 Buffer Management<br/>🔄 Circular Buffers<br/>📊 Data Windowing<br/>⚡ Memory Optimization]
                SYNC_PROC[⏱️ Sync Processing<br/>🕰️ Timestamp Alignment<br/>📊 Cross-modal Sync<br/>🎯 Precision Timing]
            end
        end
    end
    
    %% Integration Connections
    CAM2_MGR --> CAM2_DEV
    CAM2_DEV --> CAM2_SESS
    CAM2_SESS --> IMG_READER
    CAM2_SESS --> SURF_VIEW
    CAM2_SESS --> MEDIA_REC
    
    IMG_READER --> FRAME_PROC
    FRAME_PROC --> FORMAT_CONV
    FORMAT_CONV --> PREVIEW_STREAM
    
    USB_ENUM --> UVC_DRIVER
    UVC_DRIVER --> DIRECT_SHOW
    DIRECT_SHOW --> WEBCAM_MGR
    WEBCAM_MGR --> CAP_ENGINE
    CAP_ENGINE --> SYNC_CTRL
    
    SYNC_CTRL --> AUTO_FOCUS
    AUTO_FOCUS --> AUTO_EXPO
    AUTO_EXPO --> WHITE_BAL
    
    OTG_MGR --> TOPDON_SDK
    TOPDON_SDK --> THERMAL_DEV
    THERMAL_DEV --> RAW_CAPTURE
    RAW_CAPTURE --> TEMP_CONV
    TEMP_CONV --> FALSE_COLOR
    
    RAW_CAPTURE --> THERMAL_CAL
    THERMAL_CAL --> GEOMETRIC_CAL
    GEOMETRIC_CAL --> TEMPORAL_CAL
    
    BLE_MGR --> SHIMMER_PROT
    SHIMMER_PROT --> CONN_MGR
    CONN_MGR --> RAW_GSR
    RAW_GSR --> SIGNAL_PROC
    SIGNAL_PROC --> CALIB_PROC
    
    CALIB_PROC --> STREAM_PROC
    STREAM_PROC --> BUFFER_MGR
    BUFFER_MGR --> SYNC_PROC
```

## Camera2 Image Processing Flow

Detailed flowchart showing the Android Camera2 API image processing pipeline from capture to storage.

```mermaid
flowchart TD
    START([📷 Camera2 Processing Start])
    
    subgraph "Camera Initialization"
        CAM_PERM[🔐 Camera Permissions<br/>📱 Runtime Permission Check<br/>✅ Camera Access Grant<br/>🚨 Permission Denial Handling]
        CAM_DISC[🔍 Camera Discovery<br/>📊 CameraManager Query<br/>📱 Available Cameras<br/>📋 Capability Assessment]
        CAM_CHAR[📊 Camera Characteristics<br/>🎯 Supported Formats<br/>📏 Resolution Options<br/>⚙️ Feature Capabilities]
    end
    
    subgraph "Surface Configuration"
        SURF_PREP[🖼️ Surface Preparation<br/>📱 SurfaceView Setup<br/>📸 ImageReader Creation<br/>🎥 MediaRecorder Surface]
        FORMAT_SEL[📊 Format Selection<br/>🎞️ YUV_420_888 for Processing<br/>📸 JPEG for Stills<br/>🎥 H.264/H.265 for Video]
        SIZE_CONFIG[📏 Size Configuration<br/>🎯 4K Video (3840x2160)<br/>📸 High-res Stills<br/>👁️ Preview Resolution]
    end
    
    subgraph "Session Management"
        SESS_CREATE[🎬 Session Creation<br/>📋 CameraCaptureSession<br/>🎯 Multiple Outputs<br/>⚙️ Session Configuration]
        SESS_CONFIG[⚙️ Session Configuration<br/>🎥 Video + Still Capture<br/>👁️ Preview Stream<br/>📡 Network Stream]
        SESS_START[🚀 Session Start<br/>⚡ Repeating Requests<br/>📊 Capture Results<br/>🔄 Continuous Operation]
    end
    
    subgraph "Capture Request Pipeline"
        REQ_BUILD[📋 Request Building<br/>🎯 Capture Parameters<br/>⚙️ Camera Controls<br/>📊 Metadata Tags]
        AUTO_CONTROLS[🤖 Auto Controls<br/>🎯 Auto Focus (AF)<br/>☀️ Auto Exposure (AE)<br/>🎨 Auto White Balance (AWB)]
        MANUAL_CTRL[🎮 Manual Controls<br/>📊 ISO Settings<br/>⏱️ Shutter Speed<br/>🎯 Focus Distance]
    end
    
    subgraph "Image Processing Pipeline"
        subgraph "RAW Processing"
            RAW_CAPTURE[📸 RAW Capture<br/>📊 DngCreator Support<br/>🔍 Bayer Pattern<br/>📈 High Dynamic Range]
            RAW_PROCESS[🔧 RAW Processing<br/>📊 Demosaicing<br/>🎨 Color Correction<br/>📈 Tone Mapping]
            DNG_SAVE[💾 DNG Saving<br/>📁 Adobe DNG Format<br/>📋 Metadata Embedding<br/>🎯 Calibration Data]
        end
        
        subgraph "YUV Processing"
            YUV_CAPTURE[📊 YUV Capture<br/>🎞️ YUV_420_888<br/>📊 Multi-plane Data<br/>⚡ Real-time Processing]
            YUV_PROCESS[🔧 YUV Processing<br/>🎨 Color Space Conversion<br/>📊 Noise Reduction<br/>🎯 Sharpening]
            JPEG_ENCODE[🗜️ JPEG Encoding<br/>📊 Quality Selection<br/>⚡ Hardware Acceleration<br/>📄 EXIF Metadata]
        end
        
        subgraph "Video Processing"
            VIDEO_CAPTURE[🎥 Video Capture<br/>🎞️ H.264/H.265 Encoding<br/>📊 Hardware Encoder<br/>⚡ Real-time Performance]
            FRAME_PROCESS[🖼️ Frame Processing<br/>📊 Frame Rate Control<br/>🎯 Quality Adjustment<br/>⏱️ Timestamp Injection]
            STREAM_OUTPUT[📡 Stream Output<br/>💾 Local Storage<br/>📶 Network Streaming<br/>📊 Quality Adaptation]
        end
    end
    
    subgraph "Preview & Monitoring"
        PREVIEW_PROC[👁️ Preview Processing<br/>🖼️ SurfaceView Rendering<br/>⚡ Real-time Display<br/>🎯 UI Integration]
        PREVIEW_STREAM[📡 Preview Streaming<br/>🗜️ JPEG Compression<br/>📶 Network Transmission<br/>📊 Adaptive Quality]
        STATUS_MON[📊 Status Monitoring<br/>📈 Frame Rate Tracking<br/>🔋 Performance Metrics<br/>🚨 Error Detection]
    end
    
    subgraph "Synchronization & Timing"
        TIMESTAMP[⏱️ Timestamp Management<br/>🕰️ Frame Timestamps<br/>📊 Monotonic Time<br/>🎯 Precision Timing]
        SYNC_CTRL[🔄 Sync Control<br/>⚡ External Triggers<br/>📊 Cross-device Sync<br/>🎯 Frame Alignment]
        BUFFER_SYNC[💾 Buffer Synchronization<br/>🔄 Frame Buffering<br/>📊 Memory Management<br/>⚡ Flow Control]
    end
    
    subgraph "Quality Control & Validation"
        QUALITY_CHECK[✅ Quality Assessment<br/>📊 Image Quality Metrics<br/>🎯 Focus Quality<br/>☀️ Exposure Validation]
        ERROR_HANDLE[🚨 Error Handling<br/>🔧 Recovery Mechanisms<br/>📝 Error Logging<br/>🚨 User Notification]
        CALIB_VALID[🎯 Calibration Validation<br/>📐 Geometric Accuracy<br/>🎨 Color Accuracy<br/>📊 Quality Metrics]
    end
    
    subgraph "Data Storage & Export"
        LOCAL_STORAGE[💾 Local Storage<br/>📁 Session Organization<br/>📋 File Naming<br/>📊 Metadata Storage]
        EXPORT_PREP[📦 Export Preparation<br/>🗜️ Compression Options<br/>📋 Metadata Assembly<br/>📊 Quality Reports]
        FINAL_OUTPUT[📤 Final Output<br/>📁 Multiple Formats<br/>📊 Research Package<br/>📋 Documentation]
    end
    
    %% Flow Connections
    START --> CAM_PERM
    CAM_PERM --> CAM_DISC
    CAM_DISC --> CAM_CHAR
    
    CAM_CHAR --> SURF_PREP
    SURF_PREP --> FORMAT_SEL
    FORMAT_SEL --> SIZE_CONFIG
    
    SIZE_CONFIG --> SESS_CREATE
    SESS_CREATE --> SESS_CONFIG
    SESS_CONFIG --> SESS_START
    
    SESS_START --> REQ_BUILD
    REQ_BUILD --> AUTO_CONTROLS
    AUTO_CONTROLS --> MANUAL_CTRL
    
    MANUAL_CTRL --> RAW_CAPTURE
    MANUAL_CTRL --> YUV_CAPTURE
    MANUAL_CTRL --> VIDEO_CAPTURE
    
    RAW_CAPTURE --> RAW_PROCESS
    RAW_PROCESS --> DNG_SAVE
    
    YUV_CAPTURE --> YUV_PROCESS
    YUV_PROCESS --> JPEG_ENCODE
    
    VIDEO_CAPTURE --> FRAME_PROCESS
    FRAME_PROCESS --> STREAM_OUTPUT
    
    YUV_CAPTURE --> PREVIEW_PROC
    PREVIEW_PROC --> PREVIEW_STREAM
    PREVIEW_STREAM --> STATUS_MON
    
    STREAM_OUTPUT --> TIMESTAMP
    TIMESTAMP --> SYNC_CTRL
    SYNC_CTRL --> BUFFER_SYNC
    
    BUFFER_SYNC --> QUALITY_CHECK
    QUALITY_CHECK --> ERROR_HANDLE
    ERROR_HANDLE --> CALIB_VALID
    
    DNG_SAVE --> LOCAL_STORAGE
    JPEG_ENCODE --> LOCAL_STORAGE
    STREAM_OUTPUT --> LOCAL_STORAGE
    
    LOCAL_STORAGE --> EXPORT_PREP
    EXPORT_PREP --> FINAL_OUTPUT
    
    FINAL_OUTPUT --> END([📁 Camera2 Processing Complete])
```

## Data File System Architecture

Comprehensive diagram showing the complete data storage organization and file system structure.

```mermaid
graph TB
    subgraph "Multi-Sensor Data File System Architecture"
        subgraph "Root Storage Structure"
            ROOT[📁 Root Storage Directory<br/>💾 /recordings/<br/>🗂️ Session-based Organization<br/>📋 Hierarchical Structure]
            
            subgraph "Session Organization"
                SESS_MAIN[📂 Session Folders<br/>📅 session_YYYYMMDD_HHMMSS/<br/>🆔 Unique Identifiers<br/>📋 Chronological Ordering]
                SESS_META[📄 Session Metadata<br/>📋 session_metadata.json<br/>⚙️ Configuration Data<br/>📊 Quality Metrics]
                SESS_LOG[📝 Session Logs<br/>📋 session_log.txt<br/>🚨 Error Reports<br/>📊 Performance Data]
            end
        end
        
        subgraph "Device-Specific Storage"
            subgraph "Android Device Storage"
                AND_ROOT[📱 Android Storage Root<br/>📁 /android_device_[ID]/<br/>🆔 Device Identification<br/>📊 Capability Metadata]
                
                subgraph "Video Data"
                    RGB_VID[🎞️ RGB Video Files<br/>📁 /rgb_video/<br/>🎥 video_HHMMSS.mp4<br/>📊 H.264/H.265 Encoded]
                    RGB_RAW[📸 RAW Image Files<br/>📁 /raw_images/<br/>📷 image_HHMMSS.dng<br/>📊 Adobe DNG Format]
                    RGB_THUMB[🖼️ Thumbnail Images<br/>📁 /thumbnails/<br/>🖼️ thumb_HHMMSS.jpg<br/>📊 Preview Quality]
                end
                
                subgraph "Thermal Data"
                    THER_RAW[🌡️ Thermal Raw Data<br/>📁 /thermal_raw/<br/>📊 thermal_HHMMSS.bin<br/>📈 16-bit Binary]
                    THER_CSV[📊 Thermal CSV Data<br/>📁 /thermal_csv/<br/>📋 thermal_HHMMSS.csv<br/>🌡️ Temperature Matrix]
                    THER_VIS[🎨 Thermal Visualization<br/>📁 /thermal_visual/<br/>🌈 thermal_HHMMSS.png<br/>🎨 False Color]
                end
                
                subgraph "Sensor Data"
                    GSR_DATA[📊 GSR Data Files<br/>📁 /gsr_data/<br/>📈 gsr_HHMMSS.csv<br/>⚡ 1024 Hz Samples]
                    GSR_META[📋 GSR Metadata<br/>📁 /gsr_metadata/<br/>📄 gsr_meta_HHMMSS.json<br/>⚙️ Sensor Configuration]
                    GSR_QUAL[✅ GSR Quality Data<br/>📁 /gsr_quality/<br/>📊 quality_HHMMSS.json<br/>📈 Signal Quality Metrics]
                end
            end
            
            subgraph "PC Controller Storage"
                PC_ROOT[💻 PC Storage Root<br/>📁 /pc_controller/<br/>🖥️ Central Coordination<br/>📊 Master Records]
                
                subgraph "USB Webcam Data"
                    WEB_VID[📹 Webcam Video Files<br/>📁 /webcam_video/<br/>🎥 webcam_[ID]_HHMMSS.mp4<br/>📊 4K H.264 Encoded]
                    WEB_FRAME[🖼️ Webcam Frame Captures<br/>📁 /webcam_frames/<br/>📷 frame_[ID]_HHMMSS.jpg<br/>📊 Calibration Images]
                    WEB_CALIB[🎯 Calibration Data<br/>📁 /calibration/<br/>📐 calib_[ID]_HHMMSS.json<br/>📊 Intrinsic Parameters]
                end
                
                subgraph "Synchronization Data"
                    SYNC_LOG[⏱️ Synchronization Logs<br/>📁 /sync_logs/<br/>📋 sync_HHMMSS.log<br/>🕰️ Timestamp Records]
                    SYNC_OFFSET[📊 Time Offset Data<br/>📁 /time_offsets/<br/>📄 offset_HHMMSS.json<br/>⏱️ Clock Corrections]
                    SYNC_QUAL[✅ Sync Quality Metrics<br/>📁 /sync_quality/<br/>📊 quality_HHMMSS.json<br/>🎯 Precision Metrics]
                end
                
                subgraph "System Monitoring"
                    SYS_PERF[📊 Performance Logs<br/>📁 /performance/<br/>📋 perf_HHMMSS.log<br/>💻 Resource Usage]
                    SYS_ERR[🚨 Error Logs<br/>📁 /errors/<br/>📋 error_HHMMSS.log<br/>🚨 Exception Reports]
                    SYS_NET[🌐 Network Logs<br/>📁 /network/<br/>📋 network_HHMMSS.log<br/>📶 Communication Records]
                end
            end
        end
        
        subgraph "Processed Data Storage"
            PROC_ROOT[⚙️ Processed Data Root<br/>📁 /processed/<br/>🔄 Post-processing Results<br/>📊 Analysis Ready]
            
            subgraph "Synchronized Datasets"
                SYNC_VID[🔄 Synchronized Videos<br/>📁 /sync_videos/<br/>🎞️ Temporal Alignment<br/>⏱️ Common Timeline]
                SYNC_DATA[📊 Synchronized Sensor Data<br/>📁 /sync_data/<br/>📈 Cross-modal Alignment<br/>⏱️ Unified Timestamps]
                SYNC_META[📋 Sync Metadata<br/>📁 /sync_metadata/<br/>📄 Alignment Parameters<br/>📊 Quality Metrics]
            end
            
            subgraph "Analysis Products"
                ANALYSIS[📊 Analysis Results<br/>📁 /analysis/<br/>📈 Statistical Analysis<br/>🧮 Feature Extraction]
                REPORTS[📄 Generated Reports<br/>📁 /reports/<br/>📋 Session Summaries<br/>📊 Quality Assessments]
                EXPORT[📦 Export Packages<br/>📁 /exports/<br/>📤 Research-ready Data<br/>📋 Documentation]
            end
        end
        
        subgraph "Archive & Backup Storage"
            ARCHIVE_ROOT[📦 Archive Storage<br/>💾 Long-term Storage<br/>🔒 Data Preservation<br/>📋 Indexing System]
            
            subgraph "Backup Structure"
                BACKUP_PRIM[💾 Primary Backup<br/>📁 /backup/primary/<br/>🔄 Real-time Replication<br/>✅ Integrity Verification]
                BACKUP_SEC[💾 Secondary Backup<br/>📁 /backup/secondary/<br/>📦 Compressed Archives<br/>🗜️ Space Optimization]
                BACKUP_OFF[☁️ Offsite Backup<br/>📁 /backup/offsite/<br/>🌐 Cloud Storage<br/>🔒 Encrypted Transfer]
            end
            
            subgraph "Version Control"
                VERSION[📋 Version Control<br/>📁 /versions/<br/>🔄 Change Tracking<br/>📊 Diff Records]
                CHECKSUM[✅ Checksum Records<br/>📁 /checksums/<br/>🔍 Integrity Validation<br/>📊 Hash Values]
                INDEX[📑 Archive Index<br/>📁 /index/<br/>🔍 Search Metadata<br/>📋 Catalog System]
            end
        end
        
        subgraph "Metadata & Configuration"
            META_ROOT[📋 Metadata Storage<br/>📁 /metadata/<br/>📊 System Configuration<br/>📄 Documentation]
            
            subgraph "Configuration Files"
                DEVICE_CONFIG[⚙️ Device Configurations<br/>📁 /config/devices/<br/>📱 Device-specific Settings<br/>🎯 Capability Profiles]
                SESSION_CONFIG[📋 Session Configurations<br/>📁 /config/sessions/<br/>🎬 Recording Parameters<br/>📊 Quality Settings]
                CALIB_CONFIG[🎯 Calibration Configurations<br/>📁 /config/calibration/<br/>📐 Calibration Parameters<br/>✅ Validation Results]
            end
            
            subgraph "Documentation"
                DOC_SCHEMA[📄 Data Schemas<br/>📁 /documentation/schemas/<br/>📋 Format Specifications<br/>📊 Validation Rules]
                DOC_API[📖 API Documentation<br/>📁 /documentation/api/<br/>🔗 Interface Specifications<br/>📋 Usage Examples]
                DOC_USER[👤 User Documentation<br/>📁 /documentation/user/<br/>📖 Operation Manuals<br/>🎯 Best Practices]
            end
        end
    end
    
    %% File System Connections
    ROOT --> SESS_MAIN
    SESS_MAIN --> SESS_META
    SESS_MAIN --> SESS_LOG
    
    SESS_MAIN --> AND_ROOT
    AND_ROOT --> RGB_VID
    AND_ROOT --> THER_RAW
    AND_ROOT --> GSR_DATA
    
    RGB_VID --> RGB_RAW
    RGB_RAW --> RGB_THUMB
    
    THER_RAW --> THER_CSV
    THER_CSV --> THER_VIS
    
    GSR_DATA --> GSR_META
    GSR_META --> GSR_QUAL
    
    SESS_MAIN --> PC_ROOT
    PC_ROOT --> WEB_VID
    PC_ROOT --> SYNC_LOG
    PC_ROOT --> SYS_PERF
    
    WEB_VID --> WEB_FRAME
    WEB_FRAME --> WEB_CALIB
    
    SYNC_LOG --> SYNC_OFFSET
    SYNC_OFFSET --> SYNC_QUAL
    
    SYS_PERF --> SYS_ERR
    SYS_ERR --> SYS_NET
    
    SESS_MAIN --> PROC_ROOT
    PROC_ROOT --> SYNC_VID
    PROC_ROOT --> ANALYSIS
    
    SYNC_VID --> SYNC_DATA
    SYNC_DATA --> SYNC_META
    
    ANALYSIS --> REPORTS
    REPORTS --> EXPORT
    
    ROOT --> ARCHIVE_ROOT
    ARCHIVE_ROOT --> BACKUP_PRIM
    BACKUP_PRIM --> BACKUP_SEC
    BACKUP_SEC --> BACKUP_OFF
    
    ARCHIVE_ROOT --> VERSION
    VERSION --> CHECKSUM
    CHECKSUM --> INDEX
    
    ROOT --> META_ROOT
    META_ROOT --> DEVICE_CONFIG
    META_ROOT --> DOC_SCHEMA
    
    DEVICE_CONFIG --> SESSION_CONFIG
    SESSION_CONFIG --> CALIB_CONFIG
    
    DOC_SCHEMA --> DOC_API
    DOC_API --> DOC_USER
```

## Data Export Workflow

Comprehensive flowchart showing the complete data export and analysis preparation workflow.

```mermaid
flowchart TD
    START([📦 Data Export Start])
    
    subgraph "Export Configuration"
        EXPORT_TYPE[📊 Select Export Type<br/>📄 Research Package<br/>📈 Analysis Dataset<br/>🔄 Raw Data Archive]
        FORMAT_SEL[📋 Format Selection<br/>📊 CSV/JSON/HDF5<br/>🎞️ Video Formats<br/>📄 Documentation Types]
        QUALITY_SET[⚙️ Quality Settings<br/>🎯 Compression Level<br/>📊 Metadata Inclusion<br/>📋 Validation Options]
    end
    
    subgraph "Data Validation & Integrity"
        INTEGRITY_CHECK[✅ Integrity Verification<br/>🔍 File Completeness<br/>📊 Checksum Validation<br/>🚨 Corruption Detection]
        SYNC_VALIDATE[⏱️ Synchronization Validation<br/>🕰️ Timestamp Consistency<br/>📊 Alignment Quality<br/>🎯 Precision Metrics]
        QUALITY_ASSESS[📊 Quality Assessment<br/>📈 Signal Quality<br/>🎯 Calibration Accuracy<br/>📋 Completeness Score]
    end
    
    subgraph "Pre-processing Pipeline"
        DATA_CLEAN[🧹 Data Cleaning<br/>🔍 Outlier Detection<br/>📊 Noise Reduction<br/>🚨 Artifact Removal]
        SYNC_PROCESS[🔄 Synchronization Processing<br/>⏱️ Final Alignment<br/>📊 Cross-correlation<br/>🎯 Precision Optimization]
        CALIB_APPLY[🎯 Calibration Application<br/>📐 Geometric Correction<br/>🌡️ Thermal Calibration<br/>📊 Color Correction]
    end
    
    subgraph "Data Organization"
        STRUCT_ORG[📁 Structure Organization<br/>📂 Hierarchical Layout<br/>📋 Naming Convention<br/>🗂️ Category Grouping]
        META_COMPILE[📋 Metadata Compilation<br/>📄 Session Information<br/>⚙️ Configuration Data<br/>📊 Quality Metrics]
        DOC_GEN[📖 Documentation Generation<br/>📄 Dataset Description<br/>📋 Usage Instructions<br/>🔗 Reference Materials]
    end
    
    subgraph "Format-Specific Processing"
        subgraph "Video Export"
            VID_PROCESS[🎞️ Video Processing<br/>📊 Format Conversion<br/>🗜️ Compression Settings<br/>📋 Codec Selection]
            VID_SYNC[⏱️ Video Synchronization<br/>🔄 Frame Alignment<br/>📊 Temporal Matching<br/>🎯 Multi-stream Sync]
            VID_PACKAGE[📦 Video Packaging<br/>📁 Container Format<br/>📋 Metadata Embedding<br/>🎞️ Multi-track Support]
        end
        
        subgraph "Sensor Data Export"
            SENSOR_CONV[📊 Sensor Data Conversion<br/>📈 Format Standardization<br/>⏱️ Timestamp Alignment<br/>📋 Unit Conversion]
            SENSOR_FILTER[🔍 Sensor Data Filtering<br/>📊 Quality-based Selection<br/>🎯 Feature Extraction<br/>📈 Statistical Summary]
            SENSOR_PACKAGE[📦 Sensor Data Packaging<br/>📄 CSV/JSON Export<br/>📋 Metadata Inclusion<br/>📊 Schema Validation]
        end
        
        subgraph "Thermal Data Export"
            THERMAL_PROC[🌡️ Thermal Processing<br/>📊 Temperature Conversion<br/>🎨 Visualization Generation<br/>📈 Statistical Analysis]
            THERMAL_FORMAT[📋 Thermal Formatting<br/>📄 Multiple Formats<br/>🌈 Color Map Export<br/>📊 Raw Data Preservation]
            THERMAL_VALID[✅ Thermal Validation<br/>🎯 Calibration Check<br/>📊 Accuracy Assessment<br/>🌡️ Range Validation]
        end
    end
    
    subgraph "Archive Creation"
        COMPRESS[🗜️ Data Compression<br/>📦 Archive Creation<br/>⚡ Compression Algorithms<br/>📊 Size Optimization]
        ENCRYPT[🔒 Data Encryption<br/>🛡️ Security Application<br/>🔐 Key Management<br/>📋 Access Control]
        BUNDLE[📦 Bundle Creation<br/>📁 Complete Package<br/>📋 Manifest Generation<br/>✅ Integrity Sealing]
    end
    
    subgraph "Quality Assurance"
        FINAL_VALIDATE[✅ Final Validation<br/>🔍 Complete Package Check<br/>📊 Format Compliance<br/>📋 Documentation Review]
        TEST_IMPORT[🧪 Test Import<br/>📥 Validation Import<br/>📊 Data Accessibility<br/>🔧 Tool Compatibility]
        QUALITY_REPORT[📄 Quality Report<br/>📊 Export Summary<br/>📈 Quality Metrics<br/>⚠️ Known Issues]
    end
    
    subgraph "Delivery & Distribution"
        EXPORT_DELIVERY[📤 Export Delivery<br/>💾 Local Storage<br/>☁️ Cloud Upload<br/>📧 Email Notification]
        ACCESS_SETUP[🔗 Access Setup<br/>👤 User Permissions<br/>📋 Access Documentation<br/>🔐 Security Briefing]
        BACKUP_EXPORT[💾 Export Backup<br/>📦 Archive Storage<br/>🔄 Version Control<br/>📋 Backup Verification]
    end
    
    subgraph "Post-Export Support"
        SUPPORT_DOC[📖 Support Documentation<br/>📋 Usage Guidelines<br/>🔧 Tool Recommendations<br/>📞 Support Contacts]
        VERSION_TRACK[📋 Version Tracking<br/>🔄 Export Versioning<br/>📊 Change Logging<br/>📦 Update Management]
        FEEDBACK_COL[📝 Feedback Collection<br/>📊 User Experience<br/>🔧 Improvement Requests<br/>📈 Usage Analytics]
    end
    
    %% Workflow Connections
    START --> EXPORT_TYPE
    EXPORT_TYPE --> FORMAT_SEL
    FORMAT_SEL --> QUALITY_SET
    
    QUALITY_SET --> INTEGRITY_CHECK
    INTEGRITY_CHECK --> SYNC_VALIDATE
    SYNC_VALIDATE --> QUALITY_ASSESS
    
    QUALITY_ASSESS --> DATA_CLEAN
    DATA_CLEAN --> SYNC_PROCESS
    SYNC_PROCESS --> CALIB_APPLY
    
    CALIB_APPLY --> STRUCT_ORG
    STRUCT_ORG --> META_COMPILE
    META_COMPILE --> DOC_GEN
    
    DOC_GEN --> VID_PROCESS
    DOC_GEN --> SENSOR_CONV
    DOC_GEN --> THERMAL_PROC
    
    VID_PROCESS --> VID_SYNC
    VID_SYNC --> VID_PACKAGE
    
    SENSOR_CONV --> SENSOR_FILTER
    SENSOR_FILTER --> SENSOR_PACKAGE
    
    THERMAL_PROC --> THERMAL_FORMAT
    THERMAL_FORMAT --> THERMAL_VALID
    
    VID_PACKAGE --> COMPRESS
    SENSOR_PACKAGE --> COMPRESS
    THERMAL_VALID --> COMPRESS
    
    COMPRESS --> ENCRYPT
    ENCRYPT --> BUNDLE
    
    BUNDLE --> FINAL_VALIDATE
    FINAL_VALIDATE --> TEST_IMPORT
    TEST_IMPORT --> QUALITY_REPORT
    
    QUALITY_REPORT --> EXPORT_DELIVERY
    EXPORT_DELIVERY --> ACCESS_SETUP
    ACCESS_SETUP --> BACKUP_EXPORT
    
    BACKUP_EXPORT --> SUPPORT_DOC
    SUPPORT_DOC --> VERSION_TRACK
    VERSION_TRACK --> FEEDBACK_COL
    
    FEEDBACK_COL --> END([✅ Export Complete])
```