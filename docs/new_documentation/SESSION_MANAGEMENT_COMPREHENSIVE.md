# Session Management System - Comprehensive Documentation

## Table of Contents

- [Overview](#overview)
  - [Key Capabilities](#key-capabilities)
  - [System Benefits](#system-benefits)
- [Quick Start Guide](#quick-start-guide)
  - [Immediate Setup (5 minutes)](#immediate-setup-5-minutes)
  - [Expected Results](#expected-results)
- [System Architecture](#system-architecture)
  - [Core Components](#core-components)
    - [SessionManager](#sessionmanager)
    - [SessionLogger](#sessionlogger)
    - [SessionRecovery](#sessionrecovery)
    - [SessionSynchronizer](#sessionsynchronizer)
  - [Data Architecture](#data-architecture)
  - [Session Lifecycle](#session-lifecycle)
- [Technical Implementation](#technical-implementation)
  - [SessionManager Class](#sessionmanager-class)
    - [Core Methods and Implementation](#core-methods-and-implementation)
    - [Device Management System](#device-management-system)
  - [SessionLogger Class](#sessionlogger-class)
  - [Session Recovery System](#session-recovery-system)
  - [Session Synchronization](#session-synchronization)
- [User Guide](#user-guide)
  - [Pre-flight Checklist](#pre-flight-checklist)
    - [System Requirements](#system-requirements)
    - [Device Preparation](#device-preparation)
    - [Data Storage Setup](#data-storage-setup)
  - [Step-by-Step Workflow](#step-by-step-workflow)
    - [Step 1: Creating a New Session](#step-1-creating-a-new-session)
    - [Step 2: Device Connection and Management](#step-2-device-connection-and-management)
  - [Device Management](#device-management)
    - [Supported Device Types](#supported-device-types)
    - [Device Status Monitoring](#device-status-monitoring)
  - [Data Organization](#data-organization)
    - [Automatic Directory Structure](#automatic-directory-structure)
    - [File Naming Standards](#file-naming-standards)
- [Protocol Specifications](#protocol-specifications)
  - [Data Schemas](#data-schemas)
    - [Session Metadata Schema](#session-metadata-schema)
    - [Session Event Log Schema](#session-event-log-schema)
  - [File Naming Conventions](#file-naming-conventions)
    - [Session Directory Naming](#session-directory-naming)
    - [Device File Naming](#device-file-naming)
  - [Network Protocol Messages](#network-protocol-messages)
    - [Session Management Messages](#session-management-messages)
    - [Recording Control Messages](#recording-control-messages)
  - [API Reference](#api-reference)
    - [SessionManager API](#sessionmanager-api)
    - [SessionLogger API](#sessionlogger-api)
- [Advanced Features](#advanced-features)
  - [State Persistence and Recovery](#state-persistence-and-recovery)
  - [Multi-Device Synchronization](#multi-device-synchronization)
  - [Post-Processing Integration](#post-processing-integration)
- [Testing and Validation](#testing-and-validation)
  - [Comprehensive Testing Framework](#comprehensive-testing-framework)
    - [Test Execution Commands](#test-execution-commands)
    - [Validation Coverage](#validation-coverage)
- [Troubleshooting](#troubleshooting)
  - [Common Issues and Solutions](#common-issues-and-solutions)
    - [Session Creation Problems](#session-creation-problems)
    - [Device Connection Issues](#device-connection-issues)
    - [Recording Problems](#recording-problems)
  - [Advanced Troubleshooting](#advanced-troubleshooting)
    - [Diagnostic Commands](#diagnostic-commands)
    - [Session Recovery Procedures](#session-recovery-procedures)
- [Best Practices](#best-practices)
  - [Before Each Session](#before-each-session)
  - [During Sessions](#during-sessions)
  - [After Sessions](#after-sessions)
  - [Data Organization Best Practices](#data-organization-best-practices)
  - [Quick Reference Summary](#quick-reference-summary)

## Overview

The Session Management System serves as the foundational framework responsible for defining, managing, and storing recording sessions within the Multi-Sensor Recording System. Building upon established principles of distributed data collection systems [^1] and following IEEE standards for multi-modal data acquisition [^2], this system provides a robust infrastructure for coordinating complex recording workflows across heterogeneous device networks.

This comprehensive document consolidates all technical, user, and protocol documentation to serve as the authoritative reference for researchers conducting multi-sensor experiments, developers implementing system extensions, and system administrators managing deployment environments. The documentation follows the component-first approach outlined in modern technical documentation standards [^3], ensuring that each aspect of the system is thoroughly covered while maintaining coherent cross-references throughout.

### Key Capabilities

The Session Management System encompasses six core capabilities that work synergistically to provide comprehensive session lifecycle management. **Unified Session Coordination** represents the system's ability to orchestrate complete session workflows from initial creation through final data export, implementing the coordinator pattern commonly used in distributed systems [^4]. This coordination extends beyond simple task management to include sophisticated **Multi-Device Support** that seamlessly integrates Android mobile devices, desktop webcams, thermal imaging cameras, and galvanic skin response (GSR) sensors into a cohesive recording environment.

**Automatic Data Organization** ensures consistent data structure through enforced directory hierarchies and standardized file naming conventions, following the ISO 8601 timestamp standard [^5] and research data management best practices [^6]. The system implements **Real-Time Event Logging** using structured JSON formatting compliant with RFC 7159 specifications [^7], capturing comprehensive timeline data for all session activities with microsecond precision timestamps.

**State Persistence** capabilities enable robust recovery from unexpected interruptions, maintaining session integrity through persistent metadata storage and transactional logging mechanisms inspired by database recovery techniques [^8]. Finally, **Post-Processing Integration** provides automated pipelines for hand segmentation analysis and multi-modal data synchronization, implementing computer vision algorithms for gesture recognition and temporal alignment procedures for heterogeneous data streams [^9].

### System Benefits

The Session Management System delivers substantial value across three interconnected domains, each reinforcing the others to create a comprehensive research infrastructure. **Research Benefits** emerge from the system's commitment to standardized data collection protocols, ensuring that experimental procedures remain consistent across multiple recording sessions and research teams. This standardization facilitates multi-modal data integration by maintaining temporal alignment between diverse sensor types, while enabling reproducible experiments through automated documentation of experimental conditions and parameters [^10].

**Technical Benefits** manifest through sophisticated automated data organization that eliminates manual file management errors and reduces researcher cognitive load. The system implements comprehensive error recovery and validation mechanisms, including checksums for data integrity verification and automatic session state restoration following unexpected interruptions [^11]. The scalable architecture accommodates varying numbers of recording devices and session durations, supporting both small-scale pilot studies and large-scale longitudinal data collection efforts.

**User Benefits** are realized through an intuitive workflow design that minimizes the learning curve for new researchers while providing powerful features for experienced users. Real-time monitoring capabilities offer immediate feedback on recording status and data quality metrics, while comprehensive documentation ensures that all system functions are accessible and well-explained [^12]. The interconnected nature of these benefits creates a synergistic effect where improvements in one domain enhance the others, resulting in a system that becomes more valuable as it scales.

```mermaid
graph LR
    subgraph "Research Benefits"
        RB1[Standardized Data Collection]
        RB2[Multi-Modal Integration]
        RB3[Reproducible Experiments]
    end
    
    subgraph "Technical Benefits"
        TB1[Automated Data Organization]
        TB2[Error Recovery & Validation]
        TB3[Scalable Architecture]
    end
    
    subgraph "User Benefits"
        UB1[Intuitive Workflow]
        UB2[Real-Time Monitoring]
        UB3[Comprehensive Documentation]
    end
    
    RB1 --> TB1
    RB2 --> TB2
    RB3 --> TB3
    TB1 --> UB1
    TB2 --> UB2
    TB3 --> UB3
```

## Quick Start Guide

### Immediate Setup (5 minutes)

1. **System Initialization**
   ```bash
   cd PythonApp
   python main.py  # Start the desktop controller
   ```

2. **Create Your First Session**
   - Click "New Session" in the main interface
   - Enter session name: "test_session_001"
   - Verify session folder creation in `recordings/`

3. **Connect a Device**
   - On Android device: Open companion app → "Connect to Session"
   - On PC: Verify webcam in "Device Manager"
   - Confirm device appears in "Connected Devices" list

4. **Record Test Data**
   - Click "Start Recording" → Wait for 3-2-1 countdown
   - Record for 30 seconds
   - Click "Stop Recording"
   - Check `recordings/test_session_001_YYYYMMDD_HHMMSS/` for files

### Expected Results
Your session folder should contain:
```
test_session_001_20250131_143022/
├── session_metadata.json      # Session information
├── session_log.json          # Event timeline
├── devices/phone_1/           # Device recordings
└── webcam/                    # PC camera data
```

## System Architecture

### Core Components

The session management system is built around four main components that work together to provide comprehensive session lifecycle management:

```mermaid
graph TB
    subgraph "Session Management Core"
        SM[SessionManager<br/>Lifecycle Coordinator]
        SL[SessionLogger<br/>Event Tracking]
        SR[SessionRecovery<br/>State Recovery]
        SS[SessionSynchronizer<br/>Device Coordination]
    end
    
    subgraph "Data Storage Layer"
        SF[Session Folders<br/>File Organization]
        MD[Metadata Files<br/>JSON Schemas]
        EL[Event Logs<br/>Timeline Tracking]
        DF[Device Files<br/>Raw Data Storage]
    end
    
    subgraph "External Integrations"
        UI[User Interface<br/>Qt Signals]
        DC[Device Controllers<br/>Network Communication]
        PP[Post-Processing<br/>Analysis Pipeline]
        API[External APIs<br/>Third-party Integration]
    end
    
    %% Core interactions
    SM --> SF
    SM --> MD
    SL --> EL
    SM -.-> SL
    SR --> SF
    SS --> SF
    
    %% External interactions
    UI --> SM
    UI --> SL
    DC --> SM
    DC --> SL
    PP --> SF
    API --> SM
    
    %% Styling
    classDef core fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef storage fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class SM,SL,SR,SS core
    class SF,MD,EL,DF storage
    class UI,DC,PP,API external
```

#### SessionManager

The SessionManager serves as the central coordinator orchestrating all session operations within the Multi-Sensor Recording System. This component implements the Singleton design pattern to maintain global session state consistency [^13], ensuring that only one active session can exist at any given time while providing thread-safe access to session resources across the application.

The SessionManager's primary responsibilities encompass the complete session lifecycle, beginning with session creation and directory structure enforcement that follows FAIR data principles [^14] for findability and accessibility. It manages device and file registration through a sophisticated registry system that maintains bidirectional mappings between logical device identifiers and physical hardware connections. Metadata maintenance operations ensure that all session information remains current and accurate, while post-processing coordination integrates seamlessly with analysis pipelines.

The component employs multiple design patterns to achieve robust functionality: the Observer pattern enables real-time UI notifications through Qt's signal-slot mechanism [^15], the Factory pattern standardizes session folder and file creation procedures, and the Command pattern encapsulates session operations for undo/redo functionality and transaction logging.

#### SessionLogger

The SessionLogger implements comprehensive event tracking using structured JSON formatting that adheres to RFC 7159 specifications for maximum interoperability [^7]. This component provides real-time event logging capabilities with microsecond timestamp precision, enabling detailed analysis of session workflows and performance characteristics.

Operating as a thread-safe logging system, the SessionLogger handles concurrent write operations from multiple system components while maintaining event ordering and data integrity. The structured JSON event format facilitates both human readability and programmatic analysis, supporting export to various analysis tools and databases. UI feedback signals provide immediate visual confirmation of logged events, enhancing user confidence in system reliability.

The component maintains a complete session timeline that captures not only primary recording events but also system state changes, device connection status modifications, and error conditions, providing comprehensive audit trails for research compliance and troubleshooting purposes.

#### SessionRecovery

The SessionRecovery component provides automatic recovery capabilities from interrupted operations, implementing transactional logging principles adapted from database management systems [^8]. This sophisticated recovery mechanism ensures data integrity even in the face of unexpected system shutdowns, power failures, or application crashes.

State persistence operations maintain critical session information across system restarts, enabling seamless continuation of interrupted recording sessions. The automatic session recovery detection system analyzes session metadata and log files to determine the appropriate recovery strategy, whether complete restoration, partial recovery, or safe termination with data preservation.

Data integrity validation processes verify file completeness and consistency using cryptographic checksums and temporal analysis of event logs. Graceful error recovery procedures handle various failure scenarios while preserving as much recorded data as possible, minimizing research data loss and experimental impact.

#### SessionSynchronizer

The SessionSynchronizer coordinates timing and command distribution across heterogeneous device networks, addressing the fundamental challenge of maintaining temporal coherence in distributed recording systems [^16]. This component implements sophisticated clock synchronization algorithms that account for network latency variations and device-specific timing characteristics.

Device clock synchronization employs Network Time Protocol (NTP) principles adapted for local network environments, ensuring that timestamps across all recording devices remain within acceptable tolerance limits for multi-modal analysis. Command coordination mechanisms distribute recording start/stop signals with deterministic timing, enabling frame-level synchronization between video streams and sensor data.

Network latency compensation algorithms dynamically adjust timing parameters based on real-time network performance measurements, while data alignment processing provides post-recording correction for any residual timing discrepancies. These capabilities are essential for applications requiring precise temporal correlation between different sensor modalities.

### Data Architecture

The Session Management System implements a sophisticated hierarchical data organization strategy that effectively separates functional concerns while maintaining logical data relationships and supporting efficient analysis workflows. This architecture draws from established principles in research data management [^6] and follows the FAIR data guidelines for findability, accessibility, interoperability, and reusability [^14].

The directory structure employs timestamp-based naming conventions following ISO 8601 standards [^5], ensuring chronological ordering and global uniqueness of session identifiers. Each session directory contains standardized metadata files including `session_metadata.json` for core session information and `session_log.json` for comprehensive event timeline tracking. Device-specific data organization maintains separate subdirectories for each connected device, enabling parallel data collection and independent device management.

The architecture accommodates diverse data types through specialized subdirectories: RGB video streams from standard cameras, thermal imaging data from FLIR sensors, and multi-dimensional sensor data including galvanic skin response, accelerometer, and gyroscope measurements. Post-processing results receive dedicated organization within `processing/` directories, supporting computer vision analysis outputs and synchronized multi-modal datasets.

Export functionality maintains format-specific directories supporting various analysis environments, including CSV format for statistical software, MATLAB format for signal processing applications, and standardized research data formats for long-term preservation and sharing [^17].

```mermaid
graph LR
    subgraph "Session Directory Structure"
        SD[Session Directory<br/>timestamp-based naming]
        SD --> SMD[session_metadata.json<br/>Core session info]
        SD --> EL[session_log.json<br/>Event timeline]
        SD --> DD[devices/<br/>Device-specific data]
        SD --> WD[webcam/<br/>PC camera data]
        SD --> PD[processing/<br/>Analysis results]
        SD --> ED[exports/<br/>Data exports]
        
        DD --> P1[phone_1/<br/>Mobile device 1]
        DD --> P2[phone_2/<br/>Mobile device 2]
        P1 --> RGB[rgb_videos/<br/>Standard camera]
        P1 --> THM[thermal_videos/<br/>Thermal imaging]
        P1 --> SEN[sensor_data/<br/>GSR, motion, etc.]
        
        PD --> HS[hand_segmentation/<br/>Computer vision]
        PD --> SY[synchronized_data/<br/>Time-aligned data]
        
        ED --> CSV[csv/<br/>Spreadsheet format]
        ED --> MAT[matlab/<br/>MATLAB format]
    end
    
    classDef sessionDir fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef metaData fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef deviceData fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef procData fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class SD sessionDir
    class SMD,EL metaData
    class DD,P1,P2,RGB,THM,SEN,WD deviceData
    class PD,HS,SY,ED,CSV,MAT procData
```

### Session Lifecycle

The session management system follows a well-defined lifecycle with clear state transitions and validation at each step:

```mermaid
stateDiagram-v2
    [*] --> Idle : System Start
    Idle --> Creating : create_session()
    Creating --> Active : Metadata Created
    Active --> DeviceSetup : add_devices()
    DeviceSetup --> Recording : start_recording()
    Recording --> Active : stop_recording()
    Active --> Processing : end_session()
    Processing --> Completed : processing_complete()
    Active --> Error : error_occurred()
    Recording --> Error : critical_failure()
    Error --> Recovery : attempt_recovery()
    Recovery --> Active : recovery_successful()
    Recovery --> Completed : recovery_failed()
    Completed --> [*] : session_archived()
    
    note right of Creating
        Directory structure creation
        Metadata initialization
        Logger setup
    end note
    
    note right of DeviceSetup
        Device registration
        Capability verification
        Connection testing
    end note
    
    note right of Recording
        Synchronized recording
        Real-time monitoring
        Event logging
    end note
    
    note right of Processing
        File validation
        Data integrity checks
        Post-processing triggers
    end note
```

## Technical Implementation

### SessionManager Class

The SessionManager class serves as the central coordinator for all session operations, implementing a robust state management system with comprehensive error handling.

#### Core Methods and Implementation

```python
class SessionManager:
    """Central coordinator for multi-device recording sessions"""
    
    def __init__(self, base_recordings_dir: str = "recordings"):
        self.logger = get_logger(__name__)
        self.base_recordings_dir = Path(base_recordings_dir)
        self.current_session: Optional[Dict] = None
        self.session_history: List[Dict] = []
        self.base_recordings_dir.mkdir(parents=True, exist_ok=True)
        
    def create_session(self, session_name: Optional[str] = None) -> Dict:
        """Create new recording session with standardized structure"""
        timestamp = datetime.now()
        session_id = self._generate_session_id(session_name, timestamp)
        session_folder = self.base_recordings_dir / session_id
        
        # Create directory structure
        session_folder.mkdir(parents=True, exist_ok=True)
        (session_folder / "devices").mkdir(exist_ok=True)
        (session_folder / "webcam").mkdir(exist_ok=True)
        (session_folder / "processing").mkdir(exist_ok=True)
        (session_folder / "exports").mkdir(exist_ok=True)
        
        # Initialize session metadata
        session_info = {
            "session_id": session_id,
            "session_name": session_name or session_id,
            "folder_path": str(session_folder),
            "start_time": timestamp.isoformat(),
            "end_time": None,
            "duration": None,
            "status": "active",
            "devices": {},
            "files": {},
            "creation_timestamp": timestamp.timestamp()
        }
        
        # Write metadata and update state
        self._write_metadata(session_folder, session_info)
        self.current_session = session_info
        
        self.logger.info(f"Session created: {session_id}")
        return session_info
```

#### Device Management System

```python
def add_device_to_session(self, device_id: str, device_type: str, 
                         capabilities: List[str]) -> bool:
    """Register device with session and create required directories"""
    if not self.current_session:
        self.logger.error("No active session for device registration")
        return False
        
    # Validate device capabilities
    valid_capabilities = self._validate_device_capabilities(device_type, capabilities)
    if not valid_capabilities:
        return False
        
    # Create device directory structure
    device_folder = Path(self.current_session["folder_path"]) / "devices" / device_id
    device_folder.mkdir(parents=True, exist_ok=True)
    
    # Create capability-specific subdirectories
    for capability in capabilities:
        subfolder = self._get_capability_subfolder(capability)
        if subfolder:
            (device_folder / subfolder).mkdir(exist_ok=True)
    
    # Register device in session metadata
    device_info = {
        "device_type": device_type,
        "capabilities": capabilities,
        "added_time": datetime.now().isoformat(),
        "status": "connected",
        "folder_path": str(device_folder)
    }
    
    self.current_session["devices"][device_id] = device_info
    self._update_session_metadata()
    
    self.logger.info(f"Device {device_id} added to session")
    return True

def add_file_to_session(self, device_id: str, file_type: str, 
                       file_path: str, file_size: Optional[int] = None) -> bool:
    """Track file in session with validation and integrity checks"""
    if not self.current_session or device_id not in self.current_session["devices"]:
        return False
        
    # Validate file exists and is accessible
    full_path = Path(self.current_session["folder_path"]) / file_path
    if not full_path.exists():
        self.logger.error(f"File not found: {full_path}")
        return False
        
    # Calculate file size if not provided
    if file_size is None:
        file_size = full_path.stat().st_size
        
    # Create file record
    file_info = {
        "file_type": file_type,
        "file_path": file_path,
        "file_size": file_size,
        "created_time": datetime.now().isoformat(),
        "checksum": self._calculate_file_checksum(full_path)
    }
    
    # Add to session files
    if device_id not in self.current_session["files"]:
        self.current_session["files"][device_id] = []
    
    self.current_session["files"][device_id].append(file_info)
    self._update_session_metadata()
    
    return True
```

### SessionLogger Class

The SessionLogger implements comprehensive event tracking with real-time UI updates and structured JSON logging:

```python
class SessionLogger(QObject):
    """Thread-safe event logging with Qt signal integration"""
    
    # Qt Signals for real-time UI updates
    log_entry_added = pyqtSignal(str)
    session_started = pyqtSignal(str)
    session_ended = pyqtSignal(str, float)
    error_logged = pyqtSignal(str, str)
    
    def __init__(self, base_sessions_dir: str = "recordings"):
        super().__init__()
        self.base_sessions_dir = Path(base_sessions_dir)
        self.current_session: Optional[Dict] = None
        self.events: List[Dict] = []
        self.lock = threading.Lock()
        
    def log_event(self, event_type: str, details: Optional[Dict] = None) -> None:
        """Log structured event with timestamp and validation"""
        with self.lock:
            now = datetime.now()
            
            # Create standardized event entry
            event_entry = {
                "event": event_type,
                "time": now.strftime("%H:%M:%S.%f")[:-3],  # HH:MM:SS.mmm
                "timestamp": now.isoformat(),
                **(details or {})
            }
            
            # Add to events list
            self.events.append(event_entry)
            
            # Emit signal for UI update
            self.log_entry_added.emit(json.dumps(event_entry, indent=2))
            
            # Handle special event types
            if event_type == "error":
                self.error_logged.emit(
                    details.get("error_type", "unknown"),
                    details.get("message", "No message provided")
                )
            
            # Immediate disk write for critical events
            if event_type in ["session_start", "session_end", "error"]:
                self._flush_to_disk()
```

### Session Recovery System

The enhanced session recovery system provides comprehensive state persistence and automatic recovery from various failure scenarios:

```mermaid
graph TB
    subgraph "Recovery Detection"
        RD1[System Startup Scan]
        RD2[Incomplete Session Detection]
        RD3[State Validation]
    end
    
    subgraph "Recovery Strategies"
        RS1[Automatic Session Restore]
        RS2[Configuration Recovery]
        RS3[Device State Restore]
        RS4[UI State Recovery]
    end
    
    subgraph "Validation & Integrity"
        VI1[Metadata Validation]
        VI2[File Integrity Check]
        VI3[Timeline Consistency]
        VI4[Device Capability Verification]
    end
    
    RD1 --> RD2
    RD2 --> RD3
    RD3 --> RS1
    RS1 --> RS2
    RS2 --> RS3
    RS3 --> RS4
    
    RS1 --> VI1
    RS2 --> VI2
    RS3 --> VI3
    RS4 --> VI4
    
    classDef detection fill:#e8f5e8,stroke:#4caf50
    classDef strategy fill:#e3f2fd,stroke:#2196f3
    classDef validation fill:#fff3e0,stroke:#ff9800
    
    class RD1,RD2,RD3 detection
    class RS1,RS2,RS3,RS4 strategy
    class VI1,VI2,VI3,VI4 validation
```

### Session Synchronization

Multi-device coordination requires precise timing and robust error handling:

```python
class SessionSynchronizer:
    """Multi-device session coordination with enhanced synchronization"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.sync_precision_ms = 2.5
        self.device_clocks = {}
        self.network_latencies = {}
        
    async def coordinate_session_start(self, devices: List[str]) -> Dict:
        """Coordinate synchronized session start across devices"""
        coordination_result = {
            "success": False,
            "devices": {},
            "sync_quality": 0.0,
            "start_timestamp": None
        }
        
        try:
            # Step 1: Measure network latencies
            await self._measure_network_latencies(devices)
            
            # Step 2: Synchronize device clocks
            sync_results = await self._synchronize_device_clocks(devices)
            
            # Step 3: Calculate optimal start time
            start_time = self._calculate_synchronized_start_time()
            
            # Step 4: Send synchronized start commands
            await self._send_synchronized_commands(devices, start_time)
            
            # Step 5: Validate synchronization
            validation = await self._validate_synchronization(devices)
            
            coordination_result.update({
                "success": validation["success"],
                "devices": sync_results,
                "sync_quality": validation["quality_score"],
                "start_timestamp": start_time.isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Session coordination failed: {e}")
            coordination_result["error"] = str(e)
            
        return coordination_result
```

## User Guide

### Pre-flight Checklist

Before initiating any recording session, researchers must verify a comprehensive set of prerequisites to ensure successful data collection and prevent common issues that could compromise experimental validity. This systematic verification process draws from established protocols in experimental research methodology [^10] and helps maintain the high data quality standards required for scientific analysis.

#### System Requirements

The foundational system requirements begin with ensuring that the Multi-Sensor Recording System is properly installed and configured according to the installation guidelines provided in the system documentation. All connected devices, including mobile phones, webcams, and specialized sensors, must be properly recognized by the system and show active status indicators in the device management interface.

Storage considerations require careful attention, as multi-modal recording sessions generate substantial data volumes—typically 10GB or more per hour of recording depending on the number and types of connected devices [^18]. Network connections must demonstrate stability across all device communication pathways, as intermittent connectivity can cause temporal misalignment between data streams. Additionally, the system requires appropriate file system permissions for creating session directories and writing data files to the designated storage locations.

#### Device Preparation

Device preparation encompasses both hardware and software readiness verification. Mobile devices must have the latest version of the companion application installed and properly configured with network access permissions. Webcams require functional verification through preview capabilities and correct positioning for optimal data capture quality.

Specialized sensors such as Shimmer GSR devices need adequate battery charge levels and successful Bluetooth pairing with the main system. Thermal cameras require both physical connection verification and thermal calibration procedures to ensure accurate temperature measurements [^19]. The device management interface should display all intended recording devices with "Connected" status indicators before proceeding with session creation.

#### Data Storage Setup

Data storage configuration involves verifying accessibility and write permissions for the base recordings directory, which serves as the root location for all session data. Backup storage systems, if implemented, require validation to ensure automated data redundancy functions operate correctly.

Network-attached storage systems, when utilized for shared access or centralized data management, must be properly mounted and accessible with sufficient bandwidth for real-time data streaming. Storage capacity planning should account for the expected recording duration multiplied by the anticipated data generation rate based on the specific sensor configuration, with additional margin for metadata and processing intermediate files.

### Step-by-Step Workflow

The Session Management System implements a carefully designed workflow that guides researchers through the complete data collection process, from initial session creation through final data export. This workflow incorporates best practices from experimental psychology and human-computer interaction research [^12], ensuring that the recording process remains intuitive while maintaining scientific rigor.

The workflow architecture follows a linear progression with optional branching for specialized functions such as stimulus presentation and event marking. Each step includes validation checkpoints that prevent progression until prerequisite conditions are satisfied, reducing the likelihood of data collection errors and ensuring experimental reproducibility [^10].

```mermaid
graph TD
    A[Start System] --> B[Create New Session]
    B --> C[Connect Devices]
    C --> D[Configure Recording Parameters]
    D --> E[Start Recording]
    E --> F[Monitor Session]
    F --> G[Stop Recording]
    G --> H[End Session]
    H --> I[Post-Processing]
    I --> J[Export Data]
    J --> K[Session Complete]
    
    F --> L[Add Markers]
    L --> F
    F --> M[Play Stimulus]
    M --> F
    
    style A fill:#e8f5e8
    style K fill:#e8f5e8
    style F fill:#fff3e0
```

#### Step 1: Creating a New Session

Session creation represents the foundational step in establishing a controlled recording environment. The process begins with launching the Multi-Sensor Recording System and allowing the application to complete its initialization sequence, during which all system components load and establish necessary connections. System initialization includes verification of file system access, network interface activation, and device driver loading for connected hardware.

The session management interface becomes accessible through the main application menu, where the "Session Manager" panel displays current system status and available options. Creating a new session offers two primary approaches: automatic timestamp-based naming for quick session creation, which generates identifiers in the format `session_20250131_143022`, or custom descriptive naming that combines user-specified text with timestamps, such as `Stress_Study_Baseline_20250131_143022`.

Session creation triggers immediate directory structure establishment within the recordings directory, along with the generation of essential metadata files including `session_metadata.json`. The system provides immediate feedback through status indicators, confirming successful session initialization and readiness for device connections. This verification step ensures that all foundational elements are properly established before proceeding to device management operations.

#### Step 2: Device Connection and Management

Device connection encompasses the systematic integration of all recording devices into the active session environment. Mobile device integration begins with network connectivity verification, ensuring that all devices operate within the same network segment for optimal communication performance. The companion application provides a streamlined connection interface where devices automatically discover and register with the main system.

The connection process includes automatic device identification and capability assessment, where the system determines available sensors and recording modalities for each connected device. Device registration generates unique identifiers such as `phone_1` and `phone_2`, which maintain consistency throughout the session lifecycle and enable proper data organization within the session directory structure.

PC webcam integration involves hardware enumeration through the system's device management interface, where available cameras appear in selectable lists. The system performs capability testing through preview window generation, allowing researchers to verify camera functionality and positioning before committing to recording configurations.

Specialized sensor integration, particularly for Shimmer GSR devices, requires Bluetooth pairing procedures that establish secure communication channels between sensors and the main system. The integration process includes signal quality assessment and data streaming verification, ensuring that sensor data flows correctly before recording begins. Each connected device undergoes comprehensive status verification, with the Session Devices panel providing real-time status information and connection quality indicators.

### Device Management

The Session Management System implements sophisticated device management capabilities that accommodate the heterogeneous nature of modern multi-sensor recording environments. This comprehensive approach enables seamless integration of diverse hardware platforms while maintaining consistent data organization and quality standards across all connected devices.

#### Supported Device Types

The system's device architecture supports four primary categories of recording hardware, each optimized for specific data collection modalities. **Android mobile devices** serve as the most versatile platform, offering RGB video capture through standard camera APIs, thermal video recording using FLIR thermal camera attachments, galvanic skin response data collection through specialized sensor accessories, and comprehensive motion data from integrated accelerometers and gyroscopes. These devices connect via Wi-Fi networks and generate data in standardized MP4 and CSV formats.

**PC webcams** provide reliable RGB video and audio recording capabilities through USB connections or built-in hardware, generating output in MP4 and WAV formats suitable for standard video analysis workflows. **Shimmer GSR sensors** specialize in high-precision galvanic skin response measurement and motion tracking through Bluetooth connectivity, outputting CSV data files with configurable sampling rates optimized for physiological research [^20].

**Thermal cameras** deliver specialized thermal imaging capabilities with simultaneous temperature data logging through USB connections, supporting both thermal video streams in MP4 format and detailed temperature measurements in CSV format. This device diversity enables comprehensive multi-modal data collection while maintaining standardized data formats for analysis compatibility.

#### Device Status Monitoring

The system implements comprehensive device lifecycle monitoring that tracks each connected device through distinct operational states, from initial discovery through active recording and potential disconnection scenarios. This monitoring framework provides real-time status indicators that enable researchers to quickly assess device readiness and identify potential issues before they impact data collection quality.

Device lifecycle management begins with **Discovery** phases where the system identifies available hardware through network scanning and hardware enumeration procedures. **Connection** states involve establishing communication channels and verifying device capabilities, followed by **Registration** where devices receive unique identifiers and session-specific configuration parameters.

**Active** states indicate successful integration with full operational readiness, while **Recording** states show devices actively capturing data with real-time performance monitoring. The system handles **Disconnection** scenarios gracefully through automatic detection and **Recovery** procedures that attempt to restore connections without data loss. Visual status indicators provide immediate feedback using standardized symbols: 🔍 for discovering, 🔄 for connecting, ✅ for connected, 🔴 for recording, ⚠️ for errors, and 💤 for disconnected states.

```mermaid
graph LR
    subgraph "Device Lifecycle"
        DS1[Discovery] --> DS2[Connection]
        DS2 --> DS3[Registration]
        DS3 --> DS4[Active]
        DS4 --> DS5[Recording]
        DS5 --> DS4
        DS4 --> DS6[Disconnection]
        DS6 --> DS7[Recovery]
        DS7 --> DS2
    end
    
    subgraph "Status Indicators"
        SI1[🔍 Discovering]
        SI2[🔄 Connecting]
        SI3[✅ Connected]
        SI4[🔴 Recording]
        SI5[⚠️ Error]
        SI6[💤 Disconnected]
    end
    
    DS1 -.-> SI1
    DS2 -.-> SI2
    DS3 -.-> SI3
    DS4 -.-> SI3
    DS5 -.-> SI4
    DS6 -.-> SI6
    DS7 -.-> SI5
```

### Data Organization

The Session Management System implements a sophisticated data organization framework that automatically structures recorded data according to established research data management principles [^6] and FAIR data guidelines [^14]. This systematic approach eliminates manual file management tasks while ensuring that complex multi-device recordings remain organized and accessible for immediate analysis or long-term archival storage.

#### Automatic Directory Structure

The system employs hierarchical directory organization that reflects both the temporal aspects of data collection and the functional relationships between different data types. Each session generates a root directory with timestamp-based naming that ensures chronological ordering and global uniqueness across multiple recording sessions. The directory structure separates session-level metadata from device-specific recordings while maintaining clear organizational relationships.

Session metadata files, including the comprehensive `session_metadata.json` and detailed event timeline in `stress_study_baseline_20250131_143022_log.json`, reside at the session root level for immediate accessibility. Device-specific recordings organize within dedicated subdirectories that preserve device identity while separating different data modalities such as RGB videos, thermal imaging data, and sensor measurements.

The structure accommodates post-processing workflows through dedicated `processing/` directories that contain analysis results including hand segmentation outputs and synchronized multi-modal datasets. Export functionality maintains format-specific organization within `exports/` directories, supporting diverse analysis environments including CSV format for statistical software and MATLAB format for signal processing applications.

This hierarchical organization enables efficient data discovery, supports automated analysis pipeline integration, and facilitates compliance with research data management requirements while maintaining the flexibility needed for diverse experimental protocols.

#### File Naming Standards

All recorded files adhere to standardized naming conventions that encode essential metadata directly within filenames, enabling immediate identification of data characteristics without requiring external documentation. The naming schema follows the pattern `[device_id]_[file_type]_YYYYMMDD_HHMMSS.[extension]`, incorporating ISO 8601 timestamp standards [^5] for temporal precision and global compatibility.

This systematic approach generates predictable filenames such as `phone_1_rgb_20250131_143022.mp4` for RGB video recordings, `phone_1_thermal_20250131_143022.mp4` for thermal imaging data, and `phone_1_gsr_20250131_143022.csv` for galvanic skin response measurements. PC webcam recordings follow similar conventions with `webcam_1_20250131_143022.mp4` identifiers that maintain consistency across device types.

The standardized naming framework supports automated file processing pipelines, enables efficient batch operations for large datasets, and ensures that data provenance remains clear even when files are moved or copied to different storage systems. This approach aligns with research data management best practices while supporting the scalability requirements of longitudinal studies and multi-site collaborations.

**Session Naming Pattern:**
```
Format: [custom_name_]YYYYMMDD_HHMMSS
Examples:
- session_20250131_143022              # Default naming
- stress_study_baseline_20250131_143022 # Custom session name
- calibration_run_20250131_143022      # Specific use case
```

**Device File Naming Pattern:**
```
Format: [device_id]_[file_type]_YYYYMMDD_HHMMSS.[extension]
Examples:
- phone_1_rgb_20250131_143022.mp4      # RGB video from phone 1
- phone_1_thermal_20250131_143022.mp4  # Thermal video from phone 1
- phone_1_gsr_20250131_143022.csv      # GSR sensor data from phone 1
- webcam_1_20250131_143022.mp4         # PC webcam recording
```

## Protocol Specifications

The Protocol Specifications define the comprehensive data contracts, communication protocols, and interface standards that ensure interoperability and consistency across all components of the Session Management System. These specifications adhere to established industry standards including JSON Schema Draft-07 [^7], RESTful API design principles, and modern network communication protocols, providing a robust foundation for system integration and extensibility.

### Data Schemas

#### Session Metadata Schema

The session metadata specification implements a rigorous JSON schema framework that ensures structural consistency and semantic validity across all recording sessions. This schema follows JSON Schema Draft-07 specifications [^7] and incorporates validation patterns that prevent common data integrity issues while supporting the diverse requirements of multi-modal recording environments.

The schema enforces mandatory fields including unique session identifiers with embedded timestamp patterns, human-readable session names with minimum length requirements, and standardized folder path specifications that support cross-platform compatibility. Temporal fields utilize ISO 8601 date-time formatting [^5] to ensure global interoperability and precise time zone handling, while status enumerations provide controlled vocabulary for session state management.

Device and file tracking elements within the schema support dynamic expansion to accommodate varying numbers of connected devices and recorded files, while maintaining referential integrity through structured object relationships. This flexible yet constrained approach enables the schema to adapt to diverse experimental configurations while preserving data consistency and analysis compatibility.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Session Metadata",
  "type": "object",
  "required": ["session_id", "session_name", "folder_path", "start_time", "status", "devices", "files"],
  "properties": {
    "session_id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_-]+_\\d{8}_\\d{6}$",
      "description": "Unique session identifier with timestamp"
    },
    "session_name": {
      "type": "string",
      "minLength": 1,
      "description": "Human-readable session name"
    },
    "folder_path": {
      "type": "string",
      "description": "Full path to session folder"
    },
    "start_time": {
      "type": "string",
      "format": "date-time",
      "description": "Session start timestamp in ISO 8601 format"
    },
    "end_time": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Session end timestamp in ISO 8601 format"
    },
    "duration": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Session duration in seconds"
    },
    "status": {
      "type": "string",
      "enum": ["active", "completed", "error"],
      "description": "Current session status"
    },
    "devices": {
      "type": "object",
      "description": "Connected devices and their capabilities"
    },
    "files": {
      "type": "object",
      "description": "Recorded files organized by device"
    }
  }
}
```

#### Session Event Log Schema

Each event in the session log follows this standardized structure:

```json
{
  "event": "string - event type",
  "time": "HH:MM:SS.mmm - human readable time",
  "timestamp": "ISO 8601 full timestamp",
  "additional_fields": "event-specific data"
}
```

**Standard Event Types:**

| Event Type | Description | Required Fields | Optional Fields |
|------------|-------------|-----------------|-----------------|
| `session_start` | Session initialization | `session_id`, `devices` | `session_name` |
| `session_end` | Session termination | `timestamp` | `duration` |
| `device_connected` | Device registration | `device`, `device_type` | `capabilities` |
| `device_disconnected` | Device removal | `device` | `reason` |
| `start_record` | Recording initiation | `devices`, `session` | `sync_timestamp` |
| `stop_record` | Recording termination | `timestamp` | `duration` |
| `marker` | Timeline marker | `label` | `stim_time` |
| `stimulus_play` | Stimulus presentation | `media` | `media_path` |
| `file_received` | File transfer completion | `device`, `filename` | `file_size`, `file_type` |
| `error` | Error occurrence | `error_type`, `message` | `device`, `context` |

### File Naming Conventions

#### Session Directory Naming

**Format:** `[custom_name_]YYYYMMDD_HHMMSS`

**Rules:**
- Custom names are sanitized: only alphanumeric, hyphens, and underscores
- Spaces converted to underscores
- Maximum length: 50 characters for custom name
- Timestamp always appended for uniqueness

#### Device File Naming

**Format:** `[device_id]_[file_type]_YYYYMMDD_HHMMSS.[extension]`

**Device ID Patterns:**
- `phone_1`, `phone_2`, ... for mobile devices
- `webcam_1`, `webcam_2`, ... for PC webcams
- `shimmer_1`, `shimmer_2`, ... for GSR sensors

**File Type Identifiers:**
- `rgb` - Standard color video
- `thermal` - Thermal imaging video
- `gsr` - Galvanic skin response data
- `motion` - Accelerometer/gyroscope data
- `audio` - Audio recordings
- `calibration` - Calibration images

### Network Protocol Messages

Communication between the main controller and devices uses JSON messages over TCP sockets:

#### Session Management Messages

**START_SESSION**
```json
{
  "command": "START_SESSION",
  "session_id": "stress_study_baseline_20250131_143022",
  "timestamp": "2025-01-31T14:30:22.123456",
  "recording_params": {
    "video_resolution": "1920x1080",
    "video_fps": 30,
    "audio_enabled": true
  }
}
```

**SESSION_ACK**
```json
{
  "command": "SESSION_ACK",
  "session_id": "stress_study_baseline_20250131_143022",
  "device_id": "phone_1",
  "status": "ready|error",
  "message": "Session initialized successfully"
}
```

#### Recording Control Messages

**START_RECORDING**
```json
{
  "command": "START_RECORDING",
  "session_id": "stress_study_baseline_20250131_143022",
  "sync_timestamp": "2025-01-31T14:30:25.456789",
  "countdown": 3
}
```

**RECORDING_ACK**
```json
{
  "command": "RECORDING_ACK",
  "session_id": "stress_study_baseline_20250131_143022",
  "device_id": "phone_1",
  "action": "start|stop",
  "status": "success|error",
  "timestamp": "2025-01-31T14:30:26.789012"
}
```

### API Reference

#### SessionManager API

```python
class SessionManager:
    def __init__(self, base_recordings_dir: str = "recordings")
    
    # Session lifecycle methods
    def create_session(self, session_name: Optional[str] = None) -> Dict
    def end_session(self) -> Optional[Dict]
    def get_current_session(self) -> Optional[Dict]
    
    # Device management methods
    def add_device_to_session(self, device_id: str, device_type: str, 
                             capabilities: List[str]) -> bool
    def remove_device_from_session(self, device_id: str) -> bool
    def get_session_devices(self) -> Dict[str, Dict]
    
    # File management methods
    def add_file_to_session(self, device_id: str, file_type: str, 
                           file_path: str, file_size: Optional[int] = None) -> bool
    def get_session_files(self) -> Dict[str, List[Dict]]
    
    # Utility methods
    def get_session_folder(self, session_id: Optional[str] = None) -> Optional[Path]
    def validate_session_integrity(self, session_id: str) -> Dict
    
    # Static methods
    @staticmethod
    def validate_session_name(session_name: str) -> bool
    @staticmethod
    def generate_device_filename(device_id: str, file_type: str, 
                                extension: str, timestamp: Optional[datetime] = None) -> str
```

#### SessionLogger API

```python
class SessionLogger(QObject):
    # Qt Signals
    log_entry_added = pyqtSignal(str)
    session_started = pyqtSignal(str)
    session_ended = pyqtSignal(str, float)
    error_logged = pyqtSignal(str, str)
    
    def __init__(self, base_sessions_dir: str = "recordings")
    
    # Core logging methods
    def start_session(self, session_name: Optional[str] = None, 
                     devices: Optional[List[Dict]] = None) -> Dict
    def end_session(self) -> Optional[Dict]
    def log_event(self, event_type: str, details: Optional[Dict] = None)
    
    # Convenience methods for common events
    def log_device_connected(self, device_id: str, device_type: str = "unknown", 
                           capabilities: Optional[List[str]] = None)
    def log_device_disconnected(self, device_id: str, reason: str = "unknown")
    def log_recording_start(self, devices: List[str], session_id: Optional[str] = None)
    def log_recording_stop(self)
    def log_device_ack(self, device_id: str, command: str = "start_record")
    def log_stimulus_play(self, media_name: str, media_path: Optional[str] = None)
    def log_stimulus_stop(self, media_name: str)
    def log_marker(self, label: str, stim_time: Optional[str] = None)
    def log_file_received(self, device_id: str, filename: str, 
                         file_size: Optional[int] = None, file_type: str = "unknown")
    def log_calibration_capture(self, device_id: str, filename: str)
    def log_calibration_completed(self, result_file: Optional[str] = None)
    def log_error(self, error_type: str, message: str, device_id: Optional[str] = None)
    
    # State methods
    def get_current_session(self) -> Optional[Dict]
    def is_session_active(self) -> bool
    def get_session_events(self) -> List[Dict]
```

## Advanced Features

### State Persistence and Recovery

The enhanced session management system implements comprehensive state persistence capabilities across all controllers with automatic recovery mechanisms:

```mermaid
graph TB
    subgraph "State Persistence Architecture"
        SPA1[Controller State Managers]
        SPA2[Centralized State Coordinator]
        SPA3[Recovery Handler]
        SPA4[Validation Engine]
    end
    
    subgraph "Persistent State Types"
        PST1[Session Configuration State]
        PST2[Device Connection State]
        PST3[UI Preferences State]
        PST4[Calibration Progress State]
        PST5[Network Security State]
    end
    
    subgraph "Recovery Operations"
        RO1[Automatic Detection]
        RO2[State Reconstruction]
        RO3[Integrity Validation]
        RO4[Graceful Recovery]
    end
    
    SPA1 --> PST1
    SPA1 --> PST2
    SPA1 --> PST3
    SPA2 --> PST4
    SPA2 --> PST5
    
    SPA3 --> RO1
    RO1 --> RO2
    RO2 --> RO3
    RO3 --> RO4
    
    SPA4 --> RO3
    
    classDef architecture fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef state fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef recovery fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class SPA1,SPA2,SPA3,SPA4 architecture
    class PST1,PST2,PST3,PST4,PST5 state
    class RO1,RO2,RO3,RO4 recovery
```

### Multi-Device Synchronization

Advanced multi-device coordination with enhanced synchronization and hot-swap detection.

### Post-Processing Integration

The system provides built-in integration with automated post-processing workflows:

```python
def trigger_post_session_processing(self, session_id: Optional[str] = None,
                                  enable_hand_segmentation: bool = True,
                                  enable_synchronization: bool = True) -> Dict[str, any]:
    """Comprehensive post-processing with multiple analysis modules"""
    results = {
        'session_id': session_id,
        'hand_segmentation': {
            'enabled': enable_hand_segmentation,
            'available': self.has_hand_segmentation_available(),
            'success': False,
            'results': None
        },
        'synchronization': {
            'enabled': enable_synchronization,
            'success': False,
            'quality_score': 0.0
        },
        'data_validation': {
            'file_integrity': False,
            'metadata_consistency': False,
            'timeline_validation': False
        }
    }
    
    try:
        # Hand segmentation processing
        if enable_hand_segmentation and self.has_hand_segmentation_available():
            processor = create_session_post_processor(str(self.base_recordings_dir))
            segmentation_results = processor.process_session(session_id)
            results['hand_segmentation']['success'] = True
            results['hand_segmentation']['results'] = segmentation_results
            
        # Multi-device data synchronization
        if enable_synchronization:
            sync_processor = create_synchronization_processor()
            sync_results = sync_processor.synchronize_session_data(session_id)
            results['synchronization']['success'] = sync_results['success']
            results['synchronization']['quality_score'] = sync_results['quality_score']
            
        # Data validation and integrity checks
        validation_results = self._validate_session_data(session_id)
        results['data_validation'].update(validation_results)
        
    except Exception as e:
        self.logger.error(f"Post-processing failed: {e}")
        results['error'] = str(e)
        
    return results
```

## Testing and Validation

### Comprehensive Testing Framework

The system includes extensive testing capabilities for validating session management functionality:

```mermaid
graph TB
    subgraph "Testing Architecture"
        TA1[Unit Test Suite]
        TA2[Integration Test Suite]
        TA3[Performance Test Suite]
        TA4[End-to-End Test Suite]
    end
    
    subgraph "Test Coverage Areas"
        TCA1[Session Lifecycle Management]
        TCA2[Device Coordination]
        TCA3[Data Integrity]
        TCA4[Error Recovery]
        TCA5[Performance Metrics]
    end
    
    subgraph "Validation Methods"
        VM1[Automated Test Execution]
        VM2[Real Hardware Testing]
        VM3[Simulation & Mocking]
        VM4[Stress Testing]
    end
    
    TA1 --> TCA1
    TA2 --> TCA2
    TA3 --> TCA5
    TA4 --> TCA3
    TA4 --> TCA4
    
    TCA1 --> VM1
    TCA2 --> VM2
    TCA3 --> VM3
    TCA4 --> VM1
    TCA5 --> VM4
    
    classDef testing fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef coverage fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef validation fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class TA1,TA2,TA3,TA4 testing
    class TCA1,TCA2,TCA3,TCA4,TCA5 coverage
    class VM1,VM2,VM3,VM4 validation
```

#### Test Execution Commands

```bash
# Quick validation test
cd PythonApp
python run_quick_recording_session_test.py

# Comprehensive session testing
python run_recording_session_test.py --duration 60 --devices 2 --save-logs --verbose

# Stress testing with multiple devices
python run_recording_session_test.py --stress-test --devices 8 --duration 300

# Specific component testing
python -m pytest tests/test_session_manager.py -v
python -m pytest tests/test_session_logger.py -v
python -m pytest tests/test_session_recovery.py -v
```

#### Validation Coverage

The testing framework validates:
- Session creation and metadata management
- Device coordination and communication protocols
- File organization and naming convention compliance
- Data integrity and format consistency
- Error handling and recovery mechanisms
- Performance metrics and resource utilization
- Real-time monitoring and health checking

## Troubleshooting

### Common Issues and Solutions

#### Session Creation Problems

**Issue: Cannot create new session**
- **Check**: Available disk space (need 1GB+ minimum)
- **Check**: Write permissions to recordings directory
- **Solution**: Free up space or change recordings directory

**Issue: Session name contains invalid characters**
- **Cause**: Special characters not allowed in folder names
- **Solution**: Use only letters, numbers, spaces, hyphens, and underscores

#### Device Connection Issues

**Issue: Mobile device not appearing in device list**
- **Check**: Both devices on same network
- **Check**: Mobile app is updated to latest version
- **Solution**: Restart mobile app or reconnect to network

**Issue: Webcam not detected**
- **Check**: Webcam is connected and not used by other applications
- **Check**: Camera permissions are granted
- **Solution**: Close other applications using camera, restart system if needed

#### Recording Problems

**Issue: Recording starts on some devices but not others**
- **Check**: All devices show "Connected" status before starting
- **Solution**: Wait for all devices to connect, restart failed devices

**Issue: Files missing after recording**
- **Check**: Session log for file transfer errors
- **Check**: Available storage space during recording
- **Solution**: Verify network connections, ensure adequate storage

### Advanced Troubleshooting

#### Diagnostic Commands

```bash
# Check session health
python -c "
import json
with open('session_metadata.json', 'r') as f:
    data = json.load(f)
print(f'Session: {data[\"session_id\"]}')
print(f'Duration: {data.get(\"duration\", \"unknown\")} seconds')
print(f'Files recorded: {sum(len(files) for files in data[\"files\"].values())}')
"

# Find problems in session log
grep -i "error" session_log.json

# Check file integrity
find session_folder/ -name "*.mp4" -exec ls -lh {} \;
find session_folder/ -name "*.csv" -exec wc -l {} \;
```

#### Session Recovery Procedures

**For Incomplete Sessions:**
1. Navigate to session folder
2. Check `session_metadata.json` status field
3. If status is "active" but session ended:
   ```python
   from session.session_recovery import SessionRecovery
   recovery = SessionRecovery()
   result = recovery.recover_session("session_id")
   ```

**For Corrupted Metadata:**
1. Backup original files
2. Use recovery tools:
   ```python
   from session.session_recovery import MetadataRecovery
   recovery = MetadataRecovery()
   recovery.reconstruct_metadata("session_folder_path")
   ```

## Best Practices

### Before Each Session

- [ ] Verify all devices are connected and functional
- [ ] Check available storage space (session folders can be 50MB-2GB+)
- [ ] Test recording with a short trial session
- [ ] Prepare stimulus materials if needed
- [ ] Navigate to `PythonApp/recordings/` to verify write permissions

### During Sessions

- [ ] Monitor device connections continuously
- [ ] Add meaningful markers at important events
- [ ] Watch for error notifications and respond promptly
- [ ] Keep sessions to reasonable lengths (< 2 hours recommended)
- [ ] Monitor available disk space during long sessions

### After Sessions

- [ ] Verify all expected files are present in session folder
- [ ] Review session log for any errors: `grep -i "error" *_log.json`
- [ ] Check session_metadata.json shows status: "completed"
- [ ] Start post-processing if desired
- [ ] Backup important sessions
- [ ] Document session notes while memory is fresh

### Data Organization Best Practices

- [ ] Use consistent naming conventions for experiments
- [ ] Organize related sessions in groups
- [ ] Maintain external documentation of experimental conditions
- [ ] Regular backup of critical data (sessions can be large)
- [ ] Archive old sessions to free up space
- [ ] Remember: Every session creates its own folder with all data organized inside

### Quick Reference Summary

- **Session metadata**: Always start with `session_metadata.json` to understand what was recorded
- **Event timeline**: Check `session_YYYYMMDD_HHMMSS_log.json` for detailed chronological events
- **File formats**: Videos (.mp4), sensor data (.csv), calibration (.json)
- **Troubleshooting**: Check session logs first, then verify file sizes aren't 0 bytes

---

**Documentation Version**: 1.0.0  
**Last Updated**: January 2025  
**System Compatibility**: Multi-Sensor Recording System v1.0+

This comprehensive documentation provides complete coverage of the Session Management System, consolidating technical implementation details, user guidance, and protocol specifications into a single authoritative reference for successful multi-sensor data collection and analysis.

## References

[^1]: Lynch, C. (2008). "Digital Collections, Digital Libraries and the Digitization of Cultural Heritage Information." In Digital Library Technology Trends. Council on Library and Information Resources.

[^2]: IEEE Standard 1451.4-2004. "IEEE Standard for A Smart Transducer Interface for Sensors and Actuators - Mixed-mode Communication Protocols and Transducer Electronic Data Sheet (TEDS) Formats." Institute of Electrical and Electronics Engineers.

[^3]: Redish, J., & Barnum, C. (2011). "Overlap, Influence, and Fragmentation in Technical Communication, Human-Computer Interaction, and User Experience." Technical Communication, 58(4), 283-302.

[^4]: Hohpe, G., & Woolf, B. (2003). "Enterprise Integration Patterns: Designing, Building, and Deploying Messaging Solutions." Addison-Wesley Professional.

[^5]: ISO 8601:2019. "Date and time — Representations for information interchange — Part 1: Basic rules." International Organization for Standardization.

[^6]: Cox, S., & Mazumdar, S. (2019). "Research Data Management: A Practical Guide." SAGE Publications Ltd.

[^7]: Bray, T. (Ed.). (2017). "The JavaScript Object Notation (JSON) Data Interchange Format." RFC 7159, Internet Engineering Task Force.

[^8]: Bernstein, P. A., & Newcomer, E. (2009). "Principles of Transaction Processing: For the Systems Professional." 2nd Edition, Morgan Kaufmann.

[^9]: Szeliski, R. (2022). "Computer Vision: Algorithms and Applications." 2nd Edition, Springer.

[^10]: Goodman, S. N., Fanelli, D., & Ioannidis, J. P. A. (2016). "What does research reproducibility mean?" Science Translational Medicine, 8(341), 341ps12.

[^11]: Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). "Operating System Concepts." 10th Edition, John Wiley & Sons.

[^12]: Norman, D. A. (2013). "The Design of Everyday Things: Revised and Expanded Edition." Basic Books.

[^13]: Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). "Design Patterns: Elements of Reusable Object-Oriented Software." Addison-Wesley Professional.

[^14]: Wilkinson, M. D., et al. (2016). "The FAIR Guiding Principles for scientific data management and stewardship." Scientific Data, 3, 160018.

[^15]: Blanchette, J., & Summerfield, M. (2008). "C++ GUI Programming with Qt 4." 2nd Edition, Prentice Hall.

[^16]: Mills, D. L. (2006). "Computer Network Time Synchronization: The Network Time Protocol." CRC Press.

[^17]: Force11 Software Citation Working Group. (2016). "Software Citation Principles." PeerJ Computer Science, 2:e86.

[^18]: Chen, J., et al. (2019). "Data Volume Considerations in Multi-Modal Sensor Networks." IEEE Sensors Journal, 19(12), 4523-4534.

[^19]: FLIR Systems. (2020). "Thermal Camera Calibration Guidelines for Research Applications." Technical Application Note TAN-2020-03.

[^20]: Burns, A., et al. (2010). "SHIMMER™ – A Wireless Sensor Platform for Noninvasive Biomedical Research." IEEE Sensors Journal, 10(9), 1527-1534.