# Chapter 4: Design and Implementation

## 4.1 System Architecture Overview

The **Multi-Sensor Recording System** is implemented as a distributed architecture with an Android mobile application and Python-based desktop controller. The Android device functions as a sensor node for data capture, while the PC acts as central coordinator. This **PC-Android design** follows a master-slave paradigm where the Python desktop application orchestrates Android sensor nodes, achieving precise synchronized operation.

The architecture emphasizes **temporal synchronization, reliability, and modularity**. A custom network communication layer enables command-and-control messages, status updates, and data previews over Wi-Fi/LAN. The system employs event-driven communication with robust error handling, ensuring transient network issues don't compromise sessions. Each device buffers and locally stores data for uninterrupted collection, realigning streams when connectivity is restored.

**Key Architectural Features:**
- **Distributed Processing:** PC coordination with autonomous Android nodes
- **Fault Tolerance:** Local buffering and error recovery mechanisms
- **Real-Time Synchronization:** Unified timing across all devices
- **Modular Design:** Extensible for additional sensors and devices

## 4.2 Android Application Design and Sensor Integration

The **Android application** provides complete sensor data collection functionality with modular architecture supporting multiple sensor types. Built using **MVVM pattern** with **Hilt dependency injection**, the app separates concerns for maintainability and testability.

### 4.2.1 Thermal Camera Integration (Topdon)

The **Topdon TC001 thermal camera** integrates via USB-C connection using **USB Video Class (UVC)** protocol. Implementation uses Android's **Camera2 API** with custom thermal processing pipeline:

**Technical Implementation:**
- **Direct USB Integration:** No additional drivers required
- **Real-Time Processing:** Frame capture at 25-30 FPS with temperature calibration
- **Synchronized Recording:** Timestamps aligned with session master clock
- **Data Format:** Standard video files with thermal metadata

### 4.2.2 GSR Sensor Integration (Shimmer)

**Shimmer3 GSR+ sensor** connects via **Bluetooth Low Energy (BLE)** with dedicated communication protocol:

**Technical Implementation:**
- **BLE Protocol:** Custom packet handling for high-frequency data (128Hz)
- **Real-Time Streaming:** Continuous data flow with buffer management
- **Automatic Reconnection:** Fault tolerance for connection drops
- **Data Logging:** CSV format with precise timestamping

## 4.3 Desktop Controller Design and Functionality

The **Python desktop controller** provides centralized session management, device coordination, and data processing. Built with **modular architecture** using separate components for networking, sensor management, and UI.

**Core Components:**
- **Session Manager:** Creates and manages recording sessions with metadata
- **Device Server:** Handles network communication with Android devices
- **Shimmer Manager:** Direct GSR sensor integration and data collection
- **Synchronization Engine:** Master clock for temporal alignment
- **Data Pipeline:** Automated processing and file management

**User Interface:**
- **PyQt5 GUI:** Intuitive interface for researchers
- **Real-Time Monitoring:** Device status, battery, storage indicators
- **Session Control:** Start/stop recording with event annotation
- **Data Management:** Automatic file transfer and organization

## 4.4 Communication Protocol and Synchronization

**Network Protocol:**
- **JSON-based messaging** over TCP/IP for command and status exchange
- **RESTful-style commands** for device control (start, stop, configure)
- **WebSocket-like streaming** for real-time status updates
- **File transfer protocol** with integrity verification

**Synchronization Mechanism:**
- **Master Clock:** PC generates unified timeline for all devices
- **Timestamp Alignment:** Sub-millisecond precision using NTP-like protocol
- **Event Coordination:** Simultaneous start/stop across distributed nodes
- **Drift Correction:** Continuous clock synchronization during sessions

## 4.5 Data Processing Pipeline

**Real-Time Processing:**
- **Stream Management:** Concurrent handling of multiple data types
- **Quality Assurance:** Frame rate monitoring and data validation
- **Event Logging:** Automatic annotation of system events and user markers
- **Preview Generation:** Low-latency thumbnails for operator feedback

**Post-Session Processing:**
- **Data Aggregation:** Automatic file collection from distributed devices
- **Format Standardization:** Conversion to analysis-ready formats
- **Synchronization Verification:** Timestamp alignment validation
- **Optional Analysis:** Automated hand segmentation and feature extraction

## 4.6 Implementation Challenges and Solutions

**Major Challenges Addressed:**

1. **Precise Synchronization:**
   - *Challenge:* Sub-millisecond timing across distributed devices
   - *Solution:* Master clock with continuous drift correction and local buffering

2. **Multi-Sensor Integration:**
   - *Challenge:* Different protocols (USB, Bluetooth, network)
   - *Solution:* Abstracted sensor interfaces with unified timing

3. **Network Reliability:**
   - *Challenge:* Maintaining connections during long sessions
   - *Solution:* Robust reconnection logic and local data persistence

4. **Real-Time Performance:**
   - *Challenge:* High-frequency data without frame drops
   - *Solution:* Asynchronous processing with dedicated threads per sensor

5. **Cross-Platform Compatibility:**
   - *Challenge:* Android-PC integration across different OS versions
   - *Solution:* Standard protocols (TCP/IP, UVC) with abstraction layers

**Technical Innovations:**
- **Hybrid Offline-Online Architecture:** Local persistence with network coordination
- **Dynamic Device Discovery:** Automatic sensor detection and configuration
- **Scalable Threading Model:** Linear performance scaling with device count
- **Modular Sensor Framework:** Easy integration of new sensor types

------------------------------------------------------------------------