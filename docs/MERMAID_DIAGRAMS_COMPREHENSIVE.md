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