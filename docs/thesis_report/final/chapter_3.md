# Chapter 3: Requirements and System Analysis

## 3.1 Problem Statement and Research Context

Traditional **GSR** measurement requires intrusive skin-contact sensors, limiting natural behavior. The research problem is how to **predict GSR contactlessly** using thermal imaging and visual cameras without sacrificing accuracy. While cameras and thermal sensors can capture physiological cues correlating with stress, **no integrated system existed** to simultaneously collect synchronized thermal, visual, and reference GSR data for developing contactless GSR prediction models.

The project developed a **Multi-Sensor Recording System for Contactless GSR Prediction** designed to collect **synchronized multi-modal data streams**--visual video, thermal infrared imagery, and **GSR readings from a Shimmer sensor**--in real time. By aligning these streams with sub-millisecond precision, the system creates datasets for training machine learning models that estimate stress from camera data alone. The solution must be both scientifically rigorous (accurate timing, reliable signals) and practical (mobile devices, untethered subjects).

## 3.2 Requirements Engineering Approach

Requirements were derived using stakeholder-driven analysis and iterative prototyping. **Stakeholder analysis** identified: (1) **Research scientists** requiring accurate, high-fidelity data; (2) **Study participants** needing unobtrusive monitoring; (3) **Technical maintainers** requiring maintainable, extensible software; and (4) **Ethics committees** concerned with data security and participant safety.

The approach was **iterative and incremental**, following an agile-like process. Initial core requirements were established from research objectives, and a **prototype system** validated feasibility. Testing revealed additional requirements (automated device re-connection, stimulus event logging). The project adhered to **IEEE guidelines** for systematic documentation, classifying requirements into functional and non-functional categories with thorough test suite validation (>95% coverage).

## 3.3 Functional Requirements Overview

**Key Functional Requirements:**

| Priority | Requirement | Description |
|----------|-------------|-------------|
| H | **Multi-Device Coordination** | PC-based master controller manages multiple Android recording devices |
| H | **User Interface** | Intuitive GUI for session configuration, device status, and recording control |
| H | **High-Precision Synchronization** | Synchronize all data streams with ≤1ms accuracy |
| H | **Visual Video Capture** | HD RGB video recording at ≥30 FPS |
| H | **Thermal Imaging** | Thermal infrared video capture synchronized with other streams |
| H | **GSR Sensor Integration** | Shimmer GSR sensor data collection via Bluetooth |
| H | **Session Management** | Create sessions with unique IDs and metadata |
| H | **Local Data Storage** | Offline-first design with local device storage |
| M | **Data Aggregation** | Automatic file transfer from devices to PC after sessions |
| M | **Real-Time Monitoring** | Status updates including battery, storage, connectivity |
| M | **Event Annotation** | Mark stimulus events with timestamps during recording |

## 3.4 Non-Functional Requirements

**Key Non-Functional Requirements:**

| Priority | Requirement | Description |
|----------|-------------|-------------|
| H | **Real-Time Performance** | Capture video at full frame rate and sensor data without drops |
| H | **Synchronization Accuracy** | Timestamp discrepancies below millisecond thresholds |
| H | **Reliability and Fault Tolerance** | Graceful error handling and automatic reconnection |
| H | **Data Integrity** | File verification and accurate timestamps |
| H | **Usability** | Easy-to-use interface for non-expert researchers |
| M | **Scalability** | Support multiple devices with linear performance impact |
| M | **Maintainability** | Modular architecture following clean code principles |
| M | **Portability** | Cross-platform compatibility without specialized hardware |

## 3.5 Use Case Scenarios

**Primary Use Case - Stress Induction Experiment:**
1. Researcher sets up session with participant
2. System connects Android devices and Shimmer sensors
3. Calibration ensures proper sensor alignment
4. Recording begins with synchronized data capture (GSR, thermal, RGB)
5. Stress stimulus applied with event annotation
6. Session ends with automatic data transfer to PC
7. Post-processing generates analysis-ready dataset

**Alternative Scenarios:**
- Multi-participant studies with multiple device sets
- Longitudinal studies with repeated sessions
- Field studies using portable setup

## 3.6 System Analysis (Architecture & Data Flow)

**Architecture Overview:**
- **Distributed System:** PC controller coordinates multiple Android sensor nodes
- **Master-Slave Pattern:** PC orchestrates timing and data collection
- **Offline-First Design:** Local storage ensures data integrity
- **Multi-Modal Integration:** Synchronized capture from diverse sensors

**Data Flow:**
1. **Initialization:** Device discovery and sensor pairing
2. **Synchronization:** Master clock establishes unified timeline
3. **Capture:** Parallel recording on all devices with timestamping
4. **Storage:** Local files with session metadata
5. **Aggregation:** Transfer and centralization on PC
6. **Processing:** Optional automated analysis pipeline

## 3.7 Data Requirements and Management

**Data Types:**
- **GSR Data:** High-frequency (128Hz) conductance measurements from Shimmer sensors
- **Thermal Video:** Infrared imagery (256×192 resolution, 25-30 FPS)
- **RGB Video:** High-definition visual recording (720p-4K, 30+ FPS)
- **Metadata:** Session information, device status, event annotations

**Storage Requirements:**
- **Session Organization:** Unique identifiers with structured folder hierarchy
- **File Formats:** Standard formats (MP4, CSV, JSON) for compatibility
- **Synchronization Data:** Timestamp alignment for cross-modal analysis
- **Backup Strategy:** Distributed storage with integrity verification

**Data Management:**
- **Privacy Protection:** Local processing with optional encryption
- **Quality Assurance:** Automated validation and error detection
- **Archival:** Long-term storage with metadata preservation
- **Access Control:** Researcher permissions and participant anonymization

------------------------------------------------------------------------