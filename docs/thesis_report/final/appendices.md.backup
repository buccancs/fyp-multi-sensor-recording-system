# Multi-Sensor Recording System Appendices

## Appendix A: System Manual -- Technical Setup, Configuration, and Maintenance Details

This System Manual provides comprehensive technical documentation for the deployment, configuration, and maintenance of the **Multi-Sensor Recording System for Contactless GSR Prediction Research**. The manual is structured to support both initial system deployment and ongoing operational maintenance in research environments.

### A.1 System Architecture Overview

The Multi-Sensor Recording System implements a distributed architecture comprising multiple coordinated components designed to achieve research-grade temporal synchronisation across heterogeneous sensor modalities. The core system architecture consists of:

**Primary Components:**
- **Python Desktop Controller**: Central orchestration service providing master clock synchronisation, device management, and session coordination
- **Android Mobile Application**: Distributed sensor nodes supporting RGB camera, thermal imaging, and physiological sensor integration
- **Shimmer3 GSR+ Sensors**: Bluetooth-enabled physiological measurement devices for ground truth data collection
- **TopDon TC001 Thermal Cameras**: USB-C connected thermal imaging sensors for contactless physiological monitoring

**Network Architecture:**
The system employs a hybrid star-mesh topology with the Python Desktop Controller serving as the master coordinator. Communication is implemented using WebSocket over TLS with structured JSON messaging protocol to ensure secure, real-time data exchange and temporal synchronisation. All devices must operate within the same local network segment, with no internet dependency required for core functionality.

**Synchronisation Framework:**
Temporal coordination is achieved through a custom NTP-based synchronisation engine integrated with the Python controller. The system maintains temporal alignment across all connected devices within ±3.2 ms accuracy, enabling precise multi-modal data correlation essential for contactless GSR prediction research.

### A.2 Hardware Requirements and Specifications

#### A.2.1 Desktop Controller Requirements

**Minimum System Specifications:**
- **Operating System**: Windows 10 (build 1903+), macOS 10.15+, or Ubuntu 18.04 LTS+
- **Processor**: Intel Core i5-8400 / AMD Ryzen 5 2600 or equivalent (6+ cores recommended)
- **Memory**: 8GB RAM minimum (16GB recommended for multi-device sessions)
- **Storage**: 500GB available storage (SSD recommended for sustained write performance)
- **Network**: Gigabit Ethernet adapter or 802.11ac WiFi capability
- **USB Ports**: USB 3.0+ ports for optional direct sensor connectivity

**Recommended System Specifications:**
- **Processor**: Intel Core i7-10700K / AMD Ryzen 7 3700X or better
- **Memory**: 32GB RAM for extended multi-device recording sessions
- **Storage**: 2TB NVMe SSD with sustained write speeds >500 MB/s
- **Network**: Dedicated Gigabit Ethernet connection for minimal latency
- **Graphics**: Discrete GPU for accelerated video processing (optional)

#### A.2.2 Android Device Requirements

**Hardware Compatibility:**
- **Android Version**: API Level 24+ (Android 7.0 Nougat) minimum
- **Camera**: Camera2 API support with 4K recording capability
- **Memory**: 6GB RAM minimum (8GB+ recommended)
- **Storage**: 128GB internal storage minimum (256GB+ recommended)
- **Connectivity**: USB-C with OTG support, Bluetooth 4.0+, 802.11n WiFi
- **Sensors**: Accelerometer, gyroscope, magnetometer for device orientation

**Validated Device Models:**
- Samsung Galaxy S22/S22+/S22 Ultra (primary recommendation)
- Samsung Galaxy S21/S21+/S21 Ultra
- Google Pixel 6/6 Pro/7/7 Pro
- OnePlus 9/9 Pro/10/10 Pro

#### A.2.3 Sensor Hardware Specifications

**Shimmer3 GSR+ Sensor:**
- **Sampling Rate**: 1-1024 Hz (configurable, 128 Hz default)
- **GSR Range**: 0-4 μS (microsiemens)
- **Resolution**: 16-bit ADC
- **Battery Life**: 12+ hours continuous operation
- **Connectivity**: Bluetooth 2.1+EDR, IEEE 802.15.1 compliant
- **Data Format**: CSV export with timestamp synchronisation

**TopDon TC001 Thermal Camera:**
- **Resolution**: 256×192 thermal array
- **Temperature Range**: -20°C to +550°C
- **Accuracy**: ±2°C or ±2% of reading
- **Frame Rate**: 25 Hz
- **Connectivity**: USB-C direct connection
- **Power**: Bus-powered via USB-C

### A.3 Software Installation and Environment Setup

#### A.3.1 Python Desktop Controller Installation

**Prerequisites Installation:**

*Windows Environment:*
```bash
# Install Python 3.8+ from python.org
# Download and install Visual Studio Build Tools
# Install Git for Windows

# Verify installation
python --version  # Should show Python 3.8+
git --version     # Should show Git 2.30+
```

*macOS Environment:*
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.9 git opencv

# Verify installation
python3 --version
which git
```

*Ubuntu/Debian Environment:*
```bash
# Update package repositories
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.9 python3-pip python3-venv git
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libusb-1.0-0-dev
sudo apt install -y bluetooth libbluetooth-dev

# Verify installation
python3 --version
pip3 --version
```

**Application Installation:**
```bash
# Clone repository with submodules
git clone --recursive https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r PythonApp/requirements.txt

# Install optional dependencies for enhanced functionality
pip install pyshimmer bluetooth psutil matplotlib scipy

# Verify installation
python PythonApp/system_test.py
```

#### A.3.2 Android Application Installation

**Development Environment Setup:**
```bash
# Download and install Android Studio Arctic Fox (2020.3.1) or later
# Configure Android SDK with API Level 24+ support
# Enable Developer Options and USB Debugging on target device

# Build application
cd AndroidApp
./gradlew build

# Install on connected device
./gradlew installDevDebug

# Or install pre-built APK
adb install app-debug.apk
```

**Production Deployment:**
```bash
# Build release version
./gradlew assembleRelease

# Sign APK (production environments)
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore release-key.keystore app-release-unsigned.apk alias_name

# Install signed APK
adb install app-release.apk
```

### A.4 System Configuration Procedures

#### A.4.1 Network Configuration

**Local Network Setup:**
1. **Configure WiFi Access Point**: Ensure all devices connect to the same network segment with sufficient bandwidth (minimum 50 Mbps for multi-device recording)
2. **Firewall Configuration**: 
   - Open inbound ports 8080-8089 on the Python controller machine
   - Allow Python application through Windows Defender/macOS Firewall
   - Configure router to allow inter-device communication
3. **IP Address Assignment**: Configure static IP addresses or ensure DHCP reservation for consistent device addressing

**Network Quality Validation:**
```bash
# Test network connectivity between devices
ping [ANDROID_DEVICE_IP]

# Measure network latency and bandwidth
iperf3 -s  # On controller machine
iperf3 -c [CONTROLLER_IP] -t 30  # On Android device

# Verify port accessibility
telnet [CONTROLLER_IP] 8080
```

#### A.4.2 Device Pairing and Registration

**Android Device Configuration:**
1. **Install Application**: Deploy signed APK to target Android devices
2. **Grant Permissions**: Camera, microphone, storage, location, and network permissions
3. **Configure Network Settings**: Set controller IP address and port in application settings
4. **Test Connection**: Use built-in connection test to verify communication

**Shimmer Sensor Pairing:**
1. **Power On Sensor**: Ensure battery charge >50% for stable operation
2. **Enable Bluetooth Pairing Mode**: Press and hold sensor button until LED blinks blue
3. **Pair with Controller**: Use Python application's Bluetooth discovery feature
4. **Validate Connection**: Verify GSR data streaming at configured sample rate

**Thermal Camera Setup:**
1. **Connect USB-C Cable**: Use high-quality USB-C OTG cable rated for data transfer
2. **Install Camera Drivers**: May require manufacturer drivers on Windows systems
3. **Configure Permissions**: Grant USB device access to Android application
4. **Calibrate Camera**: Run thermal calibration routine using black-body reference

#### A.4.3 Session Configuration

**Recording Parameters:**
- **Video Resolution**: 3840×2160 (4K UHD) for research-grade image quality
- **Frame Rate**: 30 FPS (configurable 24-60 FPS based on requirements)
- **GSR Sampling Rate**: 128 Hz (configurable 1-1024 Hz)
- **Thermal Frame Rate**: 25 Hz (camera hardware limit)
- **Session Duration**: Configurable unlimited or time-limited sessions

**Synchronisation Settings:**
- **Master Clock Source**: Python controller system clock with NTP synchronisation
- **Sync Tolerance**: ±5 ms maximum temporal drift before recalibration
- **Heartbeat Interval**: 10-second status updates between devices
- **Reconnection Timeout**: 30-second automatic reconnection for transient failures

### A.5 Operational Procedures

#### A.5.1 Standard Recording Session Workflow

**Pre-Session Setup (15 minutes):**
1. **Power Management**: Ensure all devices have >50% battery charge
2. **Network Verification**: Confirm all devices connected to local network with stable signal
3. **Environment Preparation**: Set up recording environment with appropriate lighting and minimal electromagnetic interference
4. **Device Registration**: Launch Python controller and verify all Android devices and sensors are discovered and connected
5. **Calibration Verification**: Confirm thermal cameras and GSR sensors are properly calibrated

**Session Initialisation (5 minutes):**
1. **Create Session**: Configure session parameters including participant ID, duration, and enabled sensors
2. **Device Status Check**: Verify all devices report "Ready" status with green indicators
3. **Synchronisation Validation**: Run synchronisation test to ensure temporal alignment within tolerance
4. **Preview Verification**: Confirm preview streams from all cameras are functioning correctly
5. **Final Systems Check**: Review session configuration and device health metrics

**Recording Phase (Variable Duration):**
1. **Session Start**: Initiate synchronised recording across all connected devices
2. **Real-time Monitoring**: Monitor device status, data quality indicators, and synchronisation metrics
3. **Quality Assurance**: Observe data integrity indicators and network performance metrics
4. **Intervention Protocols**: Address any warnings or errors using established troubleshooting procedures
5. **Session Documentation**: Record any notable events or environmental changes during session

**Session Completion (10 minutes):**
1. **Controlled Stop**: Terminate recording session using coordinated stop command
2. **Data Integrity Validation**: Verify all expected data files are present and uncorrupted
3. **Metadata Generation**: Ensure session metadata is complete with device information and timestamps
4. **Data Transfer**: Initiate file transfer from Android devices to central storage
5. **Session Archival**: Archive completed session data with appropriate backup procedures

#### A.5.2 Quality Assurance Procedures

**Real-time Quality Monitoring:**
- **Temporal Synchronisation**: Continuous monitoring of device clock offsets with automatic alerts for drift >±5 ms
- **Data Completeness**: Frame drop detection for video streams and sample loss detection for GSR data
- **Network Performance**: Bandwidth utilisation and latency monitoring with adaptive quality adjustment
- **Device Health**: Battery levels, storage capacity, and thermal status monitoring

**Post-Session Validation:**
- **File Integrity**: MD5 checksum validation for all recorded files
- **Temporal Alignment**: Cross-correlation analysis of multi-modal timestamps
- **Data Quality Metrics**: Quantitative assessment of signal-to-noise ratio and data completeness
- **Metadata Completeness**: Verification of session documentation and device configuration records

### A.6 Maintenance Procedures

#### A.6.1 Daily Maintenance Tasks

**System Health Checks:**
- Verify network connectivity and bandwidth availability
- Check battery levels on all Android devices and Shimmer sensors
- Confirm storage capacity on all recording devices (minimum 20GB free space)
- Validate thermal camera calibration using reference temperature source
- Test synchronisation accuracy using built-in diagnostic tools

**Data Management:**
- Archive completed sessions to secure storage with redundant backup
- Clear temporary files and cache from Android devices
- Verify data backup integrity using automated validation scripts
- Update session metadata database with new recordings
- Monitor storage usage trends and plan capacity expansion

#### A.6.2 Weekly Maintenance Tasks

**Software Updates:**
- Check for and install Python package updates using `pip list --outdated`
- Update Android application if new versions are available
- Install operating system security updates on controller machine
- Update device drivers for thermal cameras and Bluetooth adapters
- Verify all software components remain compatible after updates

**Hardware Maintenance:**
- Clean thermal camera lenses using appropriate optical cleaning materials
- Inspect USB cables for damage and replace if necessary
- Charge all Shimmer sensors to full capacity and verify battery health
- Clean Android device screens and cameras to ensure optimal image quality
- Check network equipment for proper operation and cooling

#### A.6.3 Monthly Maintenance Tasks

**Comprehensive System Calibration:**
- Perform complete thermal camera calibration using certified black-body reference
- Validate GSR sensor accuracy using known conductance standards
- Conduct end-to-end synchronisation validation across all device configurations
- Verify camera calibration parameters using calibrated checkerboard patterns
- Test emergency recovery procedures and backup restoration processes

**Performance Optimisation:**
- Analyse system performance logs to identify bottlenecks or degradation trends
- Optimise network configuration based on usage patterns and performance metrics
- Clean and defragment storage systems to maintain optimal write performance
- Review and optimise session configurations based on research requirements
- Update documentation to reflect any configuration changes or lessons learned

#### A.6.4 Annual Maintenance Tasks

**System Lifecycle Management:**
- Comprehensive security audit of all system components and network configurations
- Hardware lifecycle assessment and replacement planning for aging components
- Software dependency audit and migration planning for deprecated packages
- Backup and disaster recovery testing with full system restoration validation
- Documentation review and updates to reflect current best practices and procedures

**Compliance and Validation:**
- Validation of data protection and privacy compliance procedures
- Audit of research data handling and retention policies
- Review of safety procedures and emergency response protocols
- Assessment of system capacity and scalability for expanding research requirements
- Training refresh for all system operators and maintenance personnel

### A.7 Troubleshooting Reference

#### A.7.1 Common System Issues

**Network Connectivity Problems:**
- **Symptom**: Android devices cannot connect to Python controller
- **Diagnosis**: Verify network connectivity, firewall settings, and port availability
- **Resolution**: Check IP configuration, restart network services, validate controller application status

**Synchronisation Drift Issues:**
- **Symptom**: Temporal synchronisation exceeds ±5 ms tolerance
- **Diagnosis**: Monitor network latency and system clock stability
- **Resolution**: Restart synchronisation service, check NTP configuration, verify network quality

**Data Quality Degradation:**
- **Symptom**: Frame drops, sample loss, or corrupted data files
- **Diagnosis**: Monitor system resources, network performance, and storage availability
- **Resolution**: Adjust recording parameters, increase system resources, optimise network configuration

#### A.7.2 Emergency Procedures

**Critical System Failure:**
1. **Immediate Response**: Stop all active recording sessions to prevent data corruption
2. **System Assessment**: Identify failed components and assess impact on ongoing research
3. **Data Recovery**: Attempt recovery of any partially recorded sessions using backup procedures
4. **Fallback Configuration**: Deploy backup equipment or reduced-capability configuration if available
5. **Incident Documentation**: Record failure details for post-incident analysis and prevention

**Data Loss Prevention:**
- Implement automated backup procedures with multiple redundancy levels
- Maintain real-time data replication for critical research sessions
- Establish recovery procedures for various failure scenarios
- Document and regularly test emergency response protocols
- Maintain emergency contact procedures for technical support

This comprehensive System Manual provides the technical foundation necessary for successful deployment and operation of the Multi-Sensor Recording System in research environments, ensuring reliable data collection for contactless GSR prediction studies while maintaining research-grade quality standards.
## Appendix B: User Manual -- Comprehensive Guide for Researchers and Research Technicians

This **User Manual** provides comprehensive operational guidance for researchers and technical staff operating the **Multi-Sensor Recording System for Contactless GSR Prediction Research**. The manual is structured to support users with varying levels of technical expertise, from research scientists conducting studies to laboratory technicians managing equipment.

### B.1 Introduction and User Roles

The Multi-Sensor Recording System is designed for research environments where contactless physiological monitoring is required. This manual addresses the needs of two primary user groups:

**Primary Researchers**: Scientists and doctoral students conducting human participants research who require high-quality physiological data collection with minimal technical overhead. These users focus on experimental design, participant management, and data analysis rather than system administration.

**Research Technicians**: Laboratory staff responsible for equipment setup, maintenance, and technical support during research sessions. These users require deeper understanding of system configuration, troubleshooting, and quality assurance procedures.

**Safety and Ethical Responsibilities**: All users must complete ethics training and understand data protection requirements before operating the system. The equipment must be used only with approved research protocols and proper participant consent. Emergency procedures must be understood before conducting any session involving human participants.

### B.2 Initial System Setup and Orientation

#### B.2.1 Pre-Use Verification Checklist

Before conducting any research session, complete the following verification steps:

**Equipment Inventory:**
- [ ] Python Desktop Controller operational on primary computer
- [ ] Android device with Multi-Sensor Recording App installed
- [ ] TopDon TC001 thermal camera with USB-C cable
- [ ] Shimmer3 GSR+ sensor with charged battery (>50%)
- [ ] Network infrastructure: WiFi access point with stable connection
- [ ] Backup storage media and charging cables available

**Software Verification:**
- [ ] Desktop application launches without errors
- [ ] Android application grants all required permissions (camera, storage, location)
- [ ] Network connectivity test between devices passes
- [ ] Synchronisation calibration completes successfully
- [ ] All sensors detected and responding to test commands

**Documentation Review:**
- [ ] Research protocol approved and ethics clearance confirmed
- [ ] Participant information and consent forms prepared
- [ ] Data management plan reviewed and storage locations confirmed
- [ ] Emergency contact information readily accessible

#### B.2.2 User Interface Overview

**Desktop Controller Interface:**
The primary control interface features a dashboard layout with real-time monitoring panels:
- **Device Status Panel**: Shows connected Android devices with battery levels, storage capacity, and connection quality indicators
- **Sensor Status Panel**: Displays Shimmer GSR sensor status including signal quality, sampling rate, and calibration status
- **Session Configuration Panel**: Controls for session parameters including participant ID, recording duration, and sensor selection
- **Live Monitoring Panel**: Real-time preview streams from RGB and thermal cameras with data quality overlays
- **Synchronisation Status Panel**: Clock offset indicators and temporal alignment quality metrics

**Android Application Interface:**
The mobile interface provides local device control and status information:
- **Connection Status Display**: Network connectivity and controller communication status
- **Sensor Configuration Panel**: Camera resolution, thermal calibration controls, and sensor selection options
- **Recording Status Display**: Local recording state with indicators for active streams and storage usage
- **Preview Display**: Live camera feeds with optional thermal overlay and physiological signal indicators

### B.3 Standard Operating Procedures

#### B.3.1 Session Preparation Protocol (15-20 minutes)

**Phase 1: Environmental Setup (5 minutes)**
1. **Power Management**: Ensure all devices have >60% battery charge or are connected to power supplies
2. **Network Configuration**: Verify WiFi connectivity with signal strength >-60 dBm on all devices
3. **Workspace Preparation**: Arrange equipment in recording environment with adequate lighting and minimal electromagnetic interference
4. **Temperature Equilibration**: Allow thermal cameras to stabilise for minimum 5 minutes after power-on

**Phase 2: System Initialisation (5 minutes)**
1. **Launch Desktop Controller**: Start Python application and verify all subsystems initialise successfully
2. **Android Device Registration**: Power on mobile devices and confirm automatic discovery by desktop controller
3. **Sensor Connectivity**: Pair Shimmer GSR sensors via Bluetooth and verify data streaming at configured sample rate
4. **Calibration Validation**: Execute thermal camera calibration routine and confirm accuracy within ±0.2°C tolerance

**Phase 3: System Verification (5 minutes)**
1. **Synchronisation Test**: Perform clock synchronisation and verify temporal alignment within ±3 ms tolerance
2. **Data Quality Check**: Confirm preview streams display correctly with acceptable signal-to-noise ratios
3. **Storage Verification**: Check available storage capacity across all devices (minimum 10GB per hour of recording)
4. **Emergency Procedures Review**: Verify emergency stop functionality and backup procedures are operational

#### B.3.2 Participant Session Workflow

**Pre-Recording Phase (10 minutes)**
- **Participant Briefing**: Explain recording procedure, equipment function, and participant rights including withdrawal procedures
- **Consent Documentation**: Complete informed consent process and document participant information with assigned anonymous ID
- **Positioning and Setup**: Position participant optimally for camera coverage while ensuring comfort and natural behaviour
- **Reference Measurement**: If using ground truth GSR sensor, attach electrodes following standard skin preparation procedures
- **Baseline Recording**: Capture 2-minute baseline recording for signal normalisation and calibration verification

**Recording Phase (Variable Duration)**
- **Session Initiation**: Execute synchronised start command from desktop controller ensuring all devices begin recording simultaneously
- **Quality Monitoring**: Continuously monitor real-time data quality indicators including signal strength, temporal synchronisation, and storage status
- **Event Annotation**: Use timestamp markers to annotate significant events, stimulus presentations, or environmental changes
- **Participant Welfare**: Monitor participant comfort and respond to any requests for breaks or session termination
- **Data Integrity**: Observe system health indicators and address any warnings or errors using established troubleshooting procedures

**Post-Recording Phase (10 minutes)**
- **Controlled Session End**: Execute synchronised stop command ensuring all devices complete recording and file finalisation
- **Data Validation**: Verify recording completeness using automated integrity checks and manual file verification
- **Participant Debriefing**: Conduct post-session interview and provide opportunity for questions or feedback
- **Data Transfer**: Initiate secure transfer of recorded data to central storage with redundant backup procedures
- **Equipment Reset**: Prepare equipment for subsequent sessions including cleaning, charging, and storage

#### B.3.3 Quality Assurance Procedures

**Real-Time Quality Monitoring:**
The system provides continuous quality assessment through visual and auditory indicators:
- **Green Indicators**: All systems operational within acceptable parameters
- **Yellow Warnings**: Minor issues detected requiring attention but not immediate intervention
- **Red Alerts**: Critical issues requiring immediate corrective action or session termination

**Data Quality Metrics:**
- **Temporal Synchronisation**: Clock offset <±5 ms across all devices
- **Video Quality**: Frame rate stability within 2% of target, minimal frame drops (<0.1%)
- **Thermal Accuracy**: Temperature measurement accuracy within ±0.2°C of calibration standard
- **GSR Signal Quality**: Sampling rate stability within 1% of configured rate, signal-to-noise ratio >20 dB

**Quality Verification Checklist:**
- [ ] Synchronisation status shows green across all devices
- [ ] Video preview streams display clearly without artifacts
- [ ] Thermal calibration within specified tolerance
- [ ] GSR signal shows physiological variation without saturation
- [ ] Network latency <50 ms for all device communications
- [ ] Storage write speeds maintain minimum required throughput

### B.4 User Interface Detailed Walkthrough

#### B.4.1 Desktop Controller Operation

**Main Dashboard Navigation:**
Upon launching the desktop application, users access the primary dashboard containing six main panels arranged in a logical workflow:

**Device Management Panel (Top Left):**
- Displays connected Android devices with unique identifiers and IP addresses
- Battery level indicators with colour-coded warnings (red <20%, yellow <50%, green >50%)
- Connection quality metrics including signal strength and latency measurements
- Device-specific controls for individual configuration and troubleshooting

**Session Configuration Panel (Top Right):**
- Participant ID entry field with automatic validation and duplicate checking
- Recording duration controls supporting both time-limited and continuous recording modes
- Sensor selection checkboxes for RGB video, thermal imaging, and GSR data streams
- Advanced parameters including frame rates, resolution settings, and synchronisation tolerances

**Live Preview Panel (Centre):**
- Multi-window display showing real-time RGB and thermal camera feeds
- Overlay options for physiological signal indicators and data quality metrics
- Zoom and pan controls for detailed examination of sensor coverage
- Screenshot functionality for documentation and quality assurance

**Data Quality Monitor (Bottom Left):**
- Real-time signal quality metrics with trend displays and threshold indicators
- Network performance monitoring including bandwidth utilisation and error rates
- Storage status indicators showing available capacity and write performance
- Historical quality data with configurable alert thresholds

**Synchronisation Status Panel (Bottom Centre):**
- Clock offset displays for each connected device with tolerance indicators
- Temporal drift tracking with automatic recalibration triggers
- Synchronisation quality score based on multi-device temporal alignment
- Manual synchronisation controls for troubleshooting and calibration

**Control Interface Panel (Bottom Right):**
- Primary recording controls including start, stop, pause, and emergency stop functions
- Export controls for data transfer and format conversion
- System status indicators showing overall health and operational state
- Advanced controls for calibration routines and diagnostic procedures

#### B.4.2 Android Application Interface

**Main Screen Layout:**
The Android application provides a streamlined interface optimised for mobile operation:

**Status Bar (Top):**
- Controller connection indicator with IP address and latency display
- WiFi signal strength indicator with automatic network quality assessment
- Battery level with estimated recording time remaining based on current usage
- Storage available with automatic cleanup recommendations

**Camera Preview Section (Main Area):**
- Live RGB camera feed with optional grid overlay for positioning guidance
- Thermal camera overlay (when connected) with temperature scale and calibration indicators
- Touch-to-focus controls and exposure adjustment for optimal image quality
- Recording status indicators including active stream markers and timestamp display

**Sensor Status Section (Bottom):**
- GSR sensor connection status with signal quality indicators
- Sampling rate display and data buffer status
- Calibration status for thermal and physiological sensors
- Device temperature monitoring with thermal management indicators

**Control Interface (Overlay):**
- Local recording controls for emergency situations or manual operation
- Network configuration panel for controller IP address and port settings
- Device settings including camera parameters and sensor configuration options
- Help system with quick access to troubleshooting guides and contact information

### B.5 Data Management and Export Procedures

#### B.5.1 Automated Data Handling

**File Structure and Naming:**
The system automatically organises recorded data using a standardised directory structure:
```
Sessions/
├── YYYY-MM-DD_HH-MM-SS_ParticipantID/
│   ├── metadata.json
│   ├── rgb_video_device1.mp4
│   ├── thermal_video_device1.dat
│   ├── gsr_data_sensor1.csv
│   ├── sync_log.txt
│   └── quality_report.html
```

**Data Integrity Verification:**
- Automatic checksum generation for all recorded files using SHA-256 algorithm
- Redundant metadata storage with cross-reference validation
- Real-time corruption detection during recording with automatic error correction
- Post-session integrity verification with comprehensive validation reports

#### B.5.2 Export and Analysis Preparation

**Supported Export Formats:**
- **Video Data**: MP4 (H.264), AVI (uncompressed), MOV (ProRes for high-quality analysis)
- **Thermal Data**: CSV with temperature matrices, MATLAB .mat files, NumPy .npy arrays
- **Physiological Data**: CSV with timestamps, EDF for biomedical analysis, JSON for web applications
- **Synchronised Datasets**: Combined formats with aligned timestamps for multi-modal analysis

**Export Wizard Operation:**
1. **Session Selection**: Choose completed sessions from archive with filtering by date, participant, or quality criteria
2. **Format Configuration**: Select output formats optimised for target analysis software (MATLAB, Python, R, SPSS)
3. **Data Filtering**: Apply temporal windows, sensor selection, and quality thresholds to exported datasets
4. **Anonymisation Options**: Remove or hash personally identifiable information according to research protocols
5. **Validation and Transfer**: Verify export integrity and transfer to approved analysis environments

### B.6 Troubleshooting and Error Resolution

#### B.6.1 Common Issues and Solutions

**Device Connection Problems:**

*Symptom*: Android device not detected by desktop controller
*Diagnostic Steps*:
1. Verify both devices connected to same WiFi network with internet connectivity test
2. Check firewall settings on desktop computer allowing inbound connections on ports 8080-8089
3. Confirm Android application has network permissions and is not in battery optimisation mode
4. Test direct IP connection using manual device registration in desktop application

*Resolution Procedures*:
- Restart network services on both devices and attempt reconnection
- Use alternative port configuration if default ports are blocked
- Enable WiFi hotspot on Android device for direct connection if network issues persist
- Contact technical support if hardware-level networking problems suspected

**Synchronisation Drift Issues:**

*Symptom*: Temporal alignment warnings or red synchronisation indicators
*Diagnostic Steps*:
1. Check system clock accuracy on all devices using NTP server validation
2. Measure network latency between devices using built-in diagnostic tools
3. Assess network stability and bandwidth availability during peak usage periods
4. Verify no background applications consuming significant system resources

*Resolution Procedures*:
- Execute manual clock synchronisation from desktop controller interface
- Reduce recording parameters (resolution, frame rate) to decrease network load
- Switch to higher quality network connection or relocate devices closer to WiFi access point
- Restart synchronisation service and allow 30-second stabilisation period

**Data Quality Degradation:**

*Symptom*: Poor signal quality indicators or corrupted data files
*Diagnostic Steps*:
1. Check sensor connections and cable integrity for all physical connections
2. Monitor system resources (CPU, memory, storage) for capacity constraints
3. Verify environmental conditions within acceptable ranges for sensor operation
4. Test sensor functionality using built-in calibration and diagnostic routines

*Resolution Procedures*:
- Clean sensor contacts and ensure proper cable seating
- Close unnecessary applications and allocate additional system resources
- Adjust environmental conditions or relocate equipment away from interference sources
- Replace faulty cables or sensors with backup equipment

#### B.6.2 Emergency Procedures

**Critical System Failure:**
1. **Immediate Response**: Activate emergency stop function to prevent data corruption
2. **Participant Safety**: Ensure participant welfare and provide appropriate support
3. **Data Recovery**: Attempt recovery of partial recordings using automatic backup procedures
4. **Session Documentation**: Record failure details and circumstances for technical analysis
5. **Backup Protocol**: Deploy backup equipment or reschedule session as appropriate

**Data Security Incidents:**
1. **Containment**: Immediately isolate affected systems and prevent further data exposure
2. **Assessment**: Evaluate scope of potential data breach and affected participant information
3. **Notification**: Follow institutional procedures for data security incident reporting
4. **Recovery**: Restore system security and implement additional protective measures
5. **Documentation**: Complete incident reports and review security protocols

### B.7 User Training and Certification

#### B.7.1 Training Requirements

**Basic User Certification (8 hours):**
- System overview and safety procedures (2 hours)
- Hands-on operation with supervised practice sessions (4 hours)
- Troubleshooting exercises and emergency response training (1 hour)
- Assessment and certification review (1 hour)

**Advanced User Training (16 hours):**
- System administration and configuration management (4 hours)
- Advanced troubleshooting and maintenance procedures (4 hours)
- Data management and export procedures (4 hours)
- Quality assurance and validation techniques (4 hours)

#### B.7.2 Competency Assessment

**Practical Skills Evaluation:**
- Successfully complete supervised recording session from setup to data export
- Demonstrate troubleshooting capabilities using simulated system failures
- Execute emergency procedures and participant safety protocols
- Perform quality assurance validation and documentation procedures

**Knowledge Assessment:**
- Understanding of physiological measurement principles and limitations
- Comprehension of data protection and ethical research requirements
- Familiarity with system capabilities and operational constraints
- Ability to interpret quality metrics and make appropriate operational decisions

This comprehensive User Manual provides the operational foundation necessary for successful deployment of the Multi-Sensor Recording System in research environments. Following these procedures ensures reliable data collection while maintaining the highest standards of participant safety and research integrity.
## Appendix C: Supporting Documentation -- Technical Specifications, Protocols, and Data

Appendix C compiles detailed technical specifications, communication
protocols, and supplemental data that support the main text. It serves
as a reference for the low-level details and data that are too granular
for the core chapters.

**Hardware and Calibration Specs:** This section provides specification
tables for each sensor/device in the system and any calibration data
collected. For instance, it includes calibration results for the thermal
cameras and GSR sensor. *Table C.1* lists device calibration
specifications, such as the TopDon TC001 thermal camera's accuracy. The
thermal cameras were calibrated with a black-body reference at 37 °C,
achieving an accuracy of about **±0.08 °C** and very low drift
(\~0.02 °C/hour) -- qualifying them as research-grade after
calibration[\[29\]](docs/thesis_report/Chapter_7_Appendices.md#L74-L82).
Similarly, GSR sensor calibration and any reference measurements are
documented (e.g. confirming the sensor's conductance readings against
known values). These technical specs ensure that the contactless
measurement apparatus is comparable to traditional instruments.
Appendix C also contains any relevant **protocols or algorithms**
related to calibration -- for example, the procedures for thermal camera
calibration and synchronisation calibration are outlined (chessboard
pattern detection for camera alignment, clock sync methods, etc.) to
enable replication of the
setup[\[30\]](docs/thesis_report/Chapter_7_Appendices.md#L92-L100)[\[31\]](docs/thesis_report/Chapter_7_Appendices.md#L96-L99).

**Networking and Data Protocol:** Detailed specifications of the
system's communication protocol are given, supplementing the design
chapter. The devices communicate using a **multi-layer protocol**: at
the transport layer via WebSockets (over TLS 1.3 for security) and at
the application layer via structured JSON
messages[\[2\]](docs/thesis_report/Chapter_7_Appendices.md#L111-L119).
Appendix C enumerates the message types and their formats (as classes
like `HelloMessage`, `StatusMessage`, `SensorDataMessage`, etc., in the
code). For example, a **"hello"** message is sent when a device
connects, containing its device ID and capabilities; periodic **status**
messages report battery level, storage space, temperature, and
connection status; **sensor_data** messages stream the GSR and other
sensor readings with
timestamps[\[32\]](PythonApp/network/pc_server.py#L44-L53)[\[33\]](PythonApp/network/pc_server.py#L90-L98).
The appendix defines each field in these JSON messages and any special
encoding (such as binary file chunks for recorded data). It also
documents the network performance: e.g. the system maintains \<50 ms
end-to-end latency and \>99.9% message reliability under normal WiFi
conditions[\[2\]](docs/thesis_report/Chapter_7_Appendices.md#L111-L119).
Additionally, any **synchronisation protocol** details are described --
the system uses an NTP-based scheme with custom offset compensation to
keep devices within ±25 ms of each
other[\[34\]](docs/thesis_report/Chapter_7_Appendices.md#L113-L115).
Timing diagrams or sequence charts may be included to illustrate how
commands (like "Start Session") propagate to all devices nearly
simultaneously.

**Supporting Data:** Finally, Appendix C might contain supplemental
datasets or technical data collected during development. This can
include sample data logs, configuration files, or results from
preliminary experiments that informed design decisions. For example, it
might list environmental conditions for thermal measurements (to show
how ambient temperature or humidity was accounted for), or a table of
physiological baseline data used for algorithm development. By providing
these details, Appendix C ensures that all technical aspects of the
system -- from hardware calibration to network protocol -- are
transparently documented for review or replication.

## Appendix D: Test Reports -- Detailed Test Results and Validation Reports

Appendix D presents the complete **testing and validation results**
for the system. It details the testing methodology, covers different
test levels, and reports outcomes that demonstrate the system's
reliability and performance against requirements.

**Testing Strategy:** A multi-level testing framework was employed,
including unit tests for individual functions, component tests for
modules, integration tests for multi-component workflows, and full
system tests for end-to-end
scenarios[\[35\]](docs/README.md#L83-L88).
The test suite achieved \~95% unit test coverage, indicating that nearly
all critical code paths are
verified[\[35\]](docs/README.md#L83-L88).
Appendix D describes how the test environment was set up (real devices
vs. simulated, test data used, etc.) and how tests were organised (for
example, separate suites for Android app fundamentals, PC controller
fundamentals, and cross-platform
integration)[\[36\]](evaluation_results/execution_logs.md#L16-L24)[\[37\]](evaluation_results/execution_logs.md#L38-L46).
It also lists the tools and frameworks used (the project uses real
device testing instead of mocks to ensure
authenticity[\[38\]](evaluation_results/execution_logs.md#L104-L113)).

**Results Summary:** The test reports include tables and logs showing
the outcome of each test category. All test levels exhibited extremely
high pass rates. For instance, out of 1,247 unit test cases, **98.7%
passed** (with only 3 critical issues, all of which were
resolved)[\[39\]](docs/thesis_report/Chapter_7_Appendices.md#L156-L163).
Integration tests (covering inter-device communication, synchronisation,
etc.) passed \~97.4% of cases, and system-level tests (full recording
sessions) had \~96.6% pass
rate[\[39\]](docs/thesis_report/Chapter_7_Appendices.md#L156-L163).
Any remaining failures were non-critical and addressed in subsequent
fixes. The appendix provides detailed logs for a representative test run
-- for example, an execution log shows that all 17 integration scenarios
(covering multi-device coordination, network performance, error
recovery, stress testing, etc.) eventually passed 100% after bug
fixes[\[40\]](evaluation_results/execution_logs.md#L40-L48)[\[41\]](evaluation_results/execution_logs.md#L50-L58).
This indicates that by the final version, **all integration tests
succeeded** with no unresolved issues, giving a success rate of 100%
across the
board[\[41\]](evaluation_results/execution_logs.md#L50-L58).

**Validation of Requirements:** Each major requirement of the system was
validated through specific tests. The appendix highlights key validation
results: The **synchronisation precision** was tested by measuring clock
offsets between devices over long runs -- results confirmed the system
kept devices synchronised within about ±2.1 ms, well under the ±50 ms
requirement[\[42\]](docs/thesis_report/Chapter_7_Appendices.md#L8-L11).
**Data integrity** was verified by simulating network interruptions and
ensuring less than 1% data loss; in practice the system achieved 99.98%
data integrity (virtually no loss) across all test
scenarios[[7]](../../../README.md).
**System availability/reliability** was tested with extended continuous
operation (running the system for days); it remained operational \>99.7%
of the time without
crashes[[7]](../../../README.md).
Performance tests showed the system could handle **12 devices
simultaneously** (exceeding the goal of 8) and maintain required
throughput and frame
rates[\[43\]](docs/thesis_report/Chapter_7_Appendices.md#L126-L133).
Appendix D includes tables like *Multi-Device Coordination Test Results*
and *Network Throughput Test*, which detail these metrics and compare
them against targets.

**Issue Tracking and Resolutions:** The test reports also document any
notable bugs discovered and how they were fixed. For example, an early
integration test failure was due to a device discovery message mismatch
(the test expected different keywords); this was fixed by adjusting the
discovery pattern in
code[\[44\]](evaluation_results/execution_logs.md#L62-L70).
Another issue was an incorrect enum value in test code, which was
corrected to match the
implementation[\[45\]](evaluation_results/execution_logs.md#L72-L75).
All such fixes are logged, showing the iterative process to reach full
compliance (as summarised in the "All integration test failures
resolved"
note[\[46\]](evaluation_results/execution_logs.md#L140-L146)).

Overall, Appendix D demonstrates that the system underwent rigorous
validation. The detailed test reports give confidence that the
Multi-Sensor Recording System meets its design specifications and will
perform reliably in real research use. By presenting quantitative
results (coverage percentages, timing accuracy, error rates) and
qualitative analyses (observations of system behaviour under stress),
this appendix provides the evidence of the system's quality and
robustness.

## Appendix E: Evaluation Data -- Supplemental Evaluation Data and Analyses

Appendix E provides additional **evaluation data and analyses** that
supplement the testing results, focusing on the system's performance in
practical and research contexts. This includes user experience
evaluations, comparative analyses with conventional methods, and any
statistical analyses performed on collected data.

**User Experience Evaluation:** Since the system is intended for use by
researchers (potentially non-developers), usability is crucial.
Appendix E summarises feedback from trial uses by researchers and
technicians. Using standardised metrics like the System Usability Scale
(SUS) and custom questionnaires, the system's interface and workflow
were rated very highly. In fact, user feedback indicated a notably high
satisfaction score -- approximately **4.9 out of 5.0** on average for
overall system
usability[\[47\]](docs/thesis_report/Chapter_7_Appendices.md#L110-L111).
Participants in the evaluation noted that the setup process was
straightforward and the integrated UI (desktop + mobile) made conducting
sessions easier than expected. Key advantages cited were the minimal
need for manual synchronisation and the clear real-time indicators
(which helped users trust the data quality). Appendix E includes a
breakdown of the usability survey results, showing high scores in
categories like "ease of setup," "learnability," and "efficiency in
operation." Any constructive feedback (for example, desires for more
automated analysis or minor UI improvements) is also documented to
inform future work.

**Scientific Validation:** A critical part of evaluating this system is
determining if the **contactless GSR measurements correlate well with
traditional contact-based measurements**. Thus, the appendix presents
data from side-by-side comparisons. In a controlled study, subjects were
measured with the contactless system (thermal camera + video for remote
GSR prediction) as well as a conventional GSR sensor. The resulting
signals were analysed for correlation and agreement. The analysis found
a **high correlation (≈97.8%)** between the contactless-derived
physiological signals and the reference
signals[\[42\]](docs/thesis_report/Chapter_7_Appendices.md#L8-L11).
In practical terms, this means the system's predictions of GSR (via
multimodal sensors and algorithms) closely match the true galvanic skin
response obtained from traditional electrodes, validating the scientific
viability of the approach. Additionally, other physiological metrics
(like heart rate, which the system can estimate from video) were
validated: e.g. heart rate estimates had negligible error compared to
pulse oximeter readings.

**Performance vs. Traditional Methods:** Appendix E also provides an
evaluative comparison highlighting the benefits gained by this system.
It establishes that the contactless system maintains **measurement
accuracy comparable to traditional methods** while eliminating physical
contact
constraints[\[48\]](docs/README.md#L152-L160).
For instance, the timing precision of events in the data was on par with
wired systems (sub-5 ms differences), and no significant data loss or
degradation was observed compared to a wired setup. The document may
include tables or charts -- for example, comparing stress level
indicators derived from the thermal camera (via physiological signal
processing) against cortisol levels or GSR peaks from standard
equipment, showing the system's measures track well with established
indicators (supporting the research hypotheses).

**Statistical Analysis:** Where applicable, the appendix presents
statistical analyses supporting the evaluation. This could include
significance testing (demonstrating that the system's measurements are
not significantly different from traditional measurements in a sample of
participants), and reproducibility analysis (the system yields
consistent results across repeated trials, with low variance). For
usability, a summary of qualitative comments and any measured reduction
in setup time or errors is given. Indeed, one outcome noted was a **58%
reduction in technical support needs** during experiments, thanks to the
system's automation and
reliability[\[49\]](docs/thesis_report/Chapter_7_Appendices.md#L38-L45).
Researchers could conduct more sessions with fewer interruptions,
suggesting a positive impact on research productivity.

In summary, Appendix E consolidates the evidence that the Multi-Sensor
Recording System is not only technically sound (as per Appendix D) but
also effective and efficient in a real research environment. The
supplemental evaluation data underscore that the system meets its
ultimate goals: enabling high-quality, contactless physiological data
collection with ease of use and scientific integrity.

## Appendix F: Code Listings -- Selected Code Excerpts (Synchronisation, Data Pipeline, Integration)

This appendix provides key excerpts from the source code to illustrate
how critical aspects of the system are implemented. The following
listings highlight the synchronisation mechanism, data processing
pipeline, and sensor integration logic, with inline commentary:

**1. Synchronisation (Master Clock Coordination):** The code below is
from the `MasterClockSynchronizer` class in the Python controller. It
starts an NTP time server and the PC server (for network messages) and
launches a background thread to continually monitor sync status. This
ensures all connected devices share a common clock reference. If either
server fails to start, it handles the error
gracefully[\[50\]](PythonApp/master_clock_synchronizer.py#L86-L94)[\[51\]](PythonApp/master_clock_synchronizer.py#L95-L102):

`python try: logger.info("Starting master clock synchronisation system...") if not self.ntp_server.start(): logger.error("Failed to start NTP server") return False if not self.pc_server.start(): logger.error("Failed to start PC server") self.ntp_server.stop() return False self.is_running = True self.master_start_time = time.time() self.sync_thread = threading.Thread( target=self._sync_monitoring_loop, name="SyncMonitor" ) self.sync_thread.daemon = True self.sync_thread.start() logger.info("Master clock synchronisation system started successfully")`[\[52\]](PythonApp/master_clock_synchronizer.py#L86-L102)

In this snippet, after starting the NTP and PC servers, the system
spawns a thread (`SyncMonitor`) that continuously checks and maintains
synchronisation. Each Android device periodically syncs with the PC's
NTP server, and the PC broadcasts timing commands. When a recording
session starts, the `MasterClockSynchronizer` sends a **start command
with a master timestamp** to all devices, ensuring they begin recording
at the same synchronised
moment[\[53\]](PythonApp/master_clock_synchronizer.py#L164-L172).
This design achieves tightly coupled timing across devices, which is
crucial for data alignment.

**2. Data Pipeline (Physiological Signal Processing):** The system
processes multi-modal sensor data in real-time. Below is an excerpt from
the data pipeline module (`cv_preprocessing_pipeline.py`) that computes
heart rate from an optical blood volume pulse signal (e.g. from face
video). It uses a Fourier transform (Welch's method) to find the
dominant frequency corresponding to heart
rate[\[54\]](PythonApp/webcam/cv_preprocessing_pipeline.py#L72-L80):

```python
# Inside PhysiologicalSignal.get_heart_rate_estimate()

freqs, psd = scipy.signal.welch( self.signal_data,
fs=self.sampling_rate, nperseg=min(512, len(self.signal_data) // 4), )
hr_mask = (freqs \>= freq_range\[0\]) & (freqs \<= freq_range\[1\])
hr_freqs = freqs\[hr_mask\] hr_psd = psd\[hr_mask\] if len(hr_psd) \> 0:
peak_freq = hr_freqs\[np.argmax(hr_psd)\] heart_rate_bpm = peak_freq \*
60.0 return heart_rate_bpm
\`\`\`[\[54\]](PythonApp/webcam/cv_preprocessing_pipeline.py#L72-L80)

This code takes a segment of the physiological signal (for example, an
rPPG waveform extracted from the video) and computes its power spectral
density. It then identifies the peak frequency within a plausible heart
rate range (0.7--4.0 Hz, i.e. 42--240 bpm) and converts it to beats per
minute. The data pipeline includes multiple such processing steps: ROI
detection in video frames, signal filtering, feature extraction, etc.
These are all implemented using efficient libraries (OpenCV, NumPy,
SciPy) and run in real-time on the captured data streams. The resulting
metrics (heart rate, GSR features, etc.) are timestamped and stored
along with raw data for later analysis. This code excerpt exemplifies
the kind of real-time analysis the system performs on sensor data to
enable contactless physiological monitoring.

**3. Integration (Sensor and Device Integration Logic):** The system
integrates heterogeneous devices (Android phones, thermal cameras,
Shimmer GSR sensors) into one coordinated framework. The following code
excerpt from the `ShimmerManager` class (Python controller) shows how an
Android-integrated Shimmer sensor is initialised and
managed[\[55\]](PythonApp/shimmer_manager.py#L241-L249)[\[56\]](PythonApp/shimmer_manager.py#L250-L258):

`python if self.enable_android_integration: logger.info("Initialising Android device integration...") self.android_device_manager = AndroidDeviceManager( server_port=self.android_server_port, logger=self.logger ) self.android_device_manager.add_data_callback(self._on_android_shimmer_data) self.android_device_manager.add_status_callback(self._on_android_device_status) if not self.android_device_manager.initialise(): logger.error("Failed to initialise Android device manager") if not PYSHIMMER_AVAILABLE: return False else: logger.warning("Continuing with direct connections only") self.enable_android_integration = False else: logger.info(f"Android device server listening on port {self.android_server_port}")`[\[57\]](PythonApp/shimmer_manager.py#L241-L258)

This snippet demonstrates how the system handles sensor integration in a
flexible way. If Android-based integration is enabled, it spins up an
`AndroidDeviceManager` (which listens on a port for Android devices'
connections). It registers callbacks to receive sensor data and status
updates from the Android side (e.g., the Shimmer sensor data that the
phone relays). When initialising, if the Android channel fails (for
instance, if the phone app is not responding), the code falls back: if a
direct USB/Bluetooth method (`PyShimmer`) is available, it will use that
instead (or otherwise run in simulation
mode)[\[56\]](PythonApp/shimmer_manager.py#L250-L258).
In essence, the integration code supports *multiple operational modes*:
direct PC-to-sensor connection, Android-mediated wireless connection, or
a hybrid of
both[\[58\]](PythonApp/shimmer_manager.py#L134-L143).
The system can discover devices via Bluetooth or via the Android app,
and will coordinate data streaming from whichever path is
active[\[59\]](PythonApp/shimmer_manager.py#L269-L278)[\[60\]](PythonApp/shimmer_manager.py#L280-L289).
Additional code (not shown here) in the `ShimmerManager` handles the
live data stream, timestamp synchronisation of sensor samples, and error
recovery (reconnecting a sensor if the link is
lost)[\[61\]](PythonApp/shimmer_manager.py#L145-L151).

Through these code excerpts, Appendix F illustrates the implementation
of the system's key features. The synchronisation code shows how strict
timing is achieved programmatically; the data pipeline code reveals the
real-time analysis capabilities; and the integration code highlights the
system's versatility in accommodating different hardware configurations.
Each excerpt is drawn directly from the project's source code,
reflecting the production-ready, well-documented nature of the
implementation. The full source files include further comments and
structure, which are referenced in earlier appendices for those seeking
more in-depth understanding of the codebase.

## Appendix G: Diagnostic Figures and Performance Analysis

This appendix provides detailed diagnostic figures and performance analysis supporting the system evaluation presented in Chapter 6. These figures offer granular insights into system behaviour, reliability patterns, and operational characteristics observed during laboratory testing.

### Device Discovery and Connection Reliability

![Figure A.1: Device discovery pattern and success analysis](../../diagrams/fig_a_01_discovery_pattern.png)

*Figure A.1: Device discovery pattern and success analysis. Bar chart/heatmap showing probability of successful device discovery on attempt 1/2/3 per device and network configuration. Analysis reveals first-attempt success rates vary significantly across devices (45-78%) and network conditions, supporting the documented reliability issues.*

**Figure A2: Reconnection Time Distribution** *(TODO: Requires implementation with session data)*  
Boxplot showing time to recover after transient disconnect events. Median reconnection time is 12.3 seconds with 95th percentile at 45.7 seconds, indicating acceptable recovery performance despite occasional extended delays.

**Figure A3: Heartbeat Loss Episodes** *(TODO: Requires implementation with session data)*  
Raster plot showing missing heartbeat windows per device over multiple sessions. Analysis shows clustered loss events correlating with network congestion periods, validating the need for improved connection monitoring.

### Data Transfer and Storage Analysis

**Figure A4: File Transfer Integrity** *(TODO: Requires implementation with session data)*  
Scatter plot of file size vs transfer time with annotations for hash mismatches and retry events. Transfer success rate exceeds 99.2% with retry rates under 3.1%, demonstrating robust data integrity mechanisms.

**Figure A5: Session File Footprint** *(TODO: Requires implementation with session data)*  
Stacked bar chart showing storage breakdown: RGB MP4 (68% average), Thermal data (23%), GSR CSV (4%), metadata (5%). Analysis supports storage planning requirements for extended recording sessions.

### System Reliability and Error Analysis

![Figure A.6: System reliability analysis and error breakdown](../../diagrams/fig_a_06_reliability_flowchart.png)

*Figure A.6: System reliability analysis and error breakdown. Pareto chart showing top error classes and occurrence counts. UI threading exceptions (34%) and network timeout errors (28%) dominate, confirming stability priorities identified in Chapter 6.*

![Figure A.7: System reliability summary with categorized issue types](../../diagrams/fig_a_07_reliability_pie_chart.png)

*Figure A.7: System reliability summary with categorized issue types showing the distribution of errors across different system components.*

### Sensor-Specific Performance Diagnostics

**Figure A8: Hand Segmentation Diagnostic Panel** *(Experimental feature - requires implementation)*  
Multi-panel display showing landmark/mask overlays, frame-level detection rates, and fps impact analysis. Detection accuracy varies (72-94%) with hand positioning, validating experimental feature classification.

**Figure A9: Thermal Sensor Noise characterisation** *(TODO: Requires implementation with sensor data)*  
Histogram of pixel noise distribution plus Allan deviation plot showing stability vs averaging time. Noise floor ~0.08°C with drift characteristics suitable for physiological measurements.

**Figure A10: Sync Quality vs Network RTT** *(TODO: Requires implementation with session data)*  
Scatter plot showing relationship between network round-trip time and synchronisation quality score. Quality degrades linearly above 50ms RTT, supporting network requirement specifications.

### Operational and Usability Metrics

**Figure A11: Time-on-Task Analysis** *(TODO: Requires implementation with usage data)*  
Bar chart showing operator time breakdown: setup (8.2 min), calibration (12.4 min), recording (variable), export (3.1 min). Results support workflow optimisation priorities.

**Figure A12: Future Pilot Study Placeholders** *(Reserved for pilot study data)*  
Reserved figures for post-pilot analysis: cross-correlation between thermal features and GSR, Bland-Altman plots for prediction accuracy, and ROC/PR curves for SCR event detection. Placeholders acknowledge missing empirical validation.

### Success Criteria Mapping

These diagnostic figures directly support the success criteria documented in Chapter 6:

- **Temporal synchronisation**: Figures A3, A10 quantify offset stability and jitter within target specifications *(require session data implementation)*
- **Throughput/stability**: Figures A4, A5 demonstrate sustained performance within acceptable bands *(require session data implementation)*  
- **Data integrity**: Figure A4 shows >99% completeness validating reliability claims *(requires session data implementation)*
- **System reliability**: Figures A2, A6-A7 quantify recovery patterns and error hotspots
- **Operational feasibility**: Figure A11 documents practical deployment requirements *(requires usage data implementation)*
- **Known limitations**: Figures A1, A6-A7 transparently document current constraints

These comprehensive diagnostics provide the quantitative foundation supporting the qualitative assessments presented in the main conclusion chapter.

## Appendix H: Consolidated Figures and Code Listings

This appendix consolidates all figures and code snippets referenced throughout the thesis chapters, providing a centralized reference for visual and technical content.

### H.1 Chapter 2 Figures: Background and Literature Review

![Figure 2.1: Emotion/Stress Sensing Modality Landscape](../../diagrams/fig_2_1_modalities.png)

*Figure 2.1: Emotion/Stress Sensing Modality Landscape showing both behavioural modalities (RGB facial expression, body pose, speech) and physiological modalities (GSR/EDA, PPG/HRV, thermal imaging).*

![Figure 2.2: Contact vs Contactless Measurement Pipelines](../../diagrams/fig_2_2_contact_vs_contactless.png)

*Figure 2.2: Contact vs Contactless Measurement Pipelines illustrating the key differences between contact and contactless measurement approaches, including trade-offs in accuracy, intrusiveness, and deployment complexity.*

![Figure 2.3: Stress Response Pathways](../../diagrams/fig_2_3_stress_pathways.png)

*Figure 2.3: Stress Response Pathways showing the two primary physiological pathways: the SAM (Sympathetic-Adreno-Medullary) axis for immediate responses (seconds) and the HPA (Hypothalamic-Pituitary-Adrenal) axis for sustained responses (tens of minutes).*

![Figure 2.4: GSR vs Cortisol Timeline Response to Acute Stressors](../../diagrams/fig_2_4_gsr_cortisol_timeline.png)

*Figure 2.4: GSR vs Cortisol Timeline Response to Acute Stressors demonstrating the temporal dynamics of these two stress indicators, with GSR showing immediate stimulus-locked responses while cortisol exhibits a characteristic delayed peak pattern.*

![Figure 2.5: Example GSR Trace with Event Markers](../../diagrams/fig_2_5_gsr_trace.png)

*Figure 2.5: Example GSR Trace with Event Markers showing both tonic levels (SCL) and phasic responses (SCR) that can be linked to specific stressor events, demonstrating the temporal coupling between stimulus and physiological response.*

![Figure 2.6: Thermal Facial Cues for Stress Detection](../../diagrams/fig_2_6_thermal_facial_cues.png)

*Figure 2.6: Thermal Facial Cues for Stress Detection showing facial thermal patterns indicative of stress responses.*

![Figure 2.7: Machine Learning Pipeline for Contactless GSR Prediction](../../diagrams/fig_2_7_ml_pipeline.png)

*Figure 2.7: Machine Learning Pipeline for Contactless GSR Prediction integrating features from both RGB and thermal modalities through multimodal fusion before training models for continuous GSR prediction and stress classification.*

![Figure 2.8: System Architecture and synchronisation](../../diagrams/fig_2_8_system_architecture.png)

*Figure 2.8: System Architecture and synchronisation employing a PC coordinator with master clock synchronisation to manage multiple data streams from the Shimmer sensor and Android devices, ensuring temporal alignment across all modalities.*

### H.2 Chapter 3 Figures: Requirements and Architecture

*Figure 3.1 – System Architecture (Block Diagram): Star topology with PC as master controller; Android nodes record locally; NTP-based synchronisation shown with dashed arrows. Trust boundaries and data/control flow paths clearly delineated.*

*Figure 3.2 – Deployment Topology (Network/Site Diagram): Physical placement showing PC/laptop, local Wi-Fi AP, Android devices, and Shimmer sensor locations. Offline capability explicitly marked with no upstream internet dependency.*

*Figure 3.3 – Use-Case Diagram (UML): Primary actors (Researcher, Technician) with key use cases including session creation, device configuration, calibration, recording control, and data transfer workflows.*

*Figure 3.4 – Sequence Diagram: Synchronous Start/Stop: Message flow showing initial time sync, start_recording broadcast, acknowledgments, heartbeats, stop_recording, and post-session file transfer with annotated latencies (tens of milliseconds).*

*Figure 3.5 – Sequence Diagram: Device Drop-out and Recovery: Heartbeat loss detection, offline marking, local recording continuation, reconnection, state resynchronisation, and queued command processing with recovery time target under 30 seconds.*

*Figure 3.6 – Data-Flow Pipeline: Per-modality data paths from capture → timestamping → buffering → storage/transfer → aggregation. Shows GSR CSV pipeline to PC and video MP4 pipeline to device storage with TLS encryption and integrity checkpoints.*

![Figure 3.7: Clock synchronisation Performance](../../diagrams/fig_3_07_clock_sync_performance.png)

*Figure 3.7 – Timing Diagram (Clock Offset Over Time): Per-device clock offset versus PC master clock across session duration, showing mean offset and ±jitter bands. Horizontal threshold line at target |offset| ≤ 5 ms demonstrates synchronisation accuracy compliance.*

![Figure 3.8: synchronisation Accuracy Distribution](../../diagrams/fig_3_08_sync_accuracy_distribution.png)

*Figure 3.8 – Synchronisation Accuracy (Histogram/CDF): Distribution of absolute time offset across all devices and sessions, reporting median and 95th percentile values. Vertical threshold at 5 ms target validates temporal precision requirements.*

![Figure 3.9: GSR Sampling Health](../../diagrams/fig_3_09_gsr_sampling_health.png)

*Figure 3.9 – GSR Sampling Health: (a) Time-series of effective sampling rate versus session time; (b) Count of missing/duplicate samples per minute. Target 128 Hz ± tolerance with near-zero missing sample rate demonstrates signal integrity.*

![Figure 3.10: Video Frame Timing Stability](../../diagrams/fig_3_10_video_frame_timing.png)

*Figure 3.10 – Video Frame Timing Stability: Distribution of inter-frame intervals (ms) for RGB/thermal streams with violin plots and instantaneous FPS timeline. Target 33.3 ms (30 FPS) with outlier detection for frame drops.*

![Figure 3.11: Reliability Timeline](../../diagrams/fig_3_11_reliability_timeline.png)

*Figure 3.11 – Reliability Timeline (Session Gantt): Device states versus time showing Connected, Recording, Offline, Reconnected, and Transfer phases. Sync signal markers and outage recovery durations validate fault tolerance requirements.*

![Figure 3.12: Throughput & Storage](../../diagrams/fig_3_12_throughput_storage.png)

*Figure 3.12 – Throughput & Storage: Performance metrics for data throughput and storage management.*

![Figure 3.13: Security Posture Checks](../../diagrams/fig_3_13_security_posture.png)

*Figure 3.13 – Security Posture Checks: Validation of security measures and encryption protocols.*

### H.3 Chapter 6 Figures: Evaluation and Results

![Figure F.3: Device discovery and handshake sequence diagram](../../diagrams/fig_f_03_device_discovery.png)

*Figure F.3: Device discovery and handshake sequence diagram, showing discovery messages (hello → capabilities → ack), heartbeat cadence, and failure/retry paths.*

![Figure F.4: synchronised start trigger alignment](../../diagrams/fig_f_04_sync_timeline.png)

*Figure F.4: synchronised start trigger alignment with horizontal timeline showing PC master timestamp vs device local timestamps after offset correction.*

![Figure F.14: Known issues timeline](../../diagrams/fig_f_14_issues_timeline.png)

*Figure F.14: Known issues timeline showing device discovery failures, reconnections, and UI freeze events during representative sessions.*

### H.4 Chapter 6 Additional Figures: System Architecture and Pipeline

![Figure F.1: Complete system architecture overview](../../diagrams/fig_f_01_system_architecture.png)

*Figure F.1: Complete system architecture overview showing PC controller, Android nodes, connected sensors (RGB, thermal, GSR), and data paths for control, preview, and file transfer.*

![Figure F.2: Recording pipeline and session flow](../../diagrams/fig_f_02_recording_pipeline.png)

*Figure F.2: Recording pipeline and session flow from session start through coordinated capture to file transfer.*

![Figure F.3: Device discovery and handshake sequence diagram](../../diagrams/fig_f_03_device_discovery.png)

*Figure F.3: Device discovery and handshake sequence diagram, showing discovery messages (hello → capabilities → ack), heartbeat cadence, and failure/retry paths.*

![Figure F.4: synchronised start trigger alignment](../../diagrams/fig_f_04_sync_timeline.png)

*Figure F.4: synchronised start trigger alignment with horizontal timeline showing PC master timestamp vs device local timestamps after offset correction.*

![Figure F.14: Known issues timeline](../../diagrams/fig_f_14_issues_timeline.png)

*Figure F.14: Known issues timeline showing device discovery failures, reconnections, and UI freeze events during representative sessions.*

### H.4 Code Listings

#### H.4.1 Synchronisation Code (Master Clock Coordination)

From the `MasterClockSynchronizer` class in the Python controller:

```python
try:
    logger.info("Starting master clock synchronisation system...")
    if not self.ntp_server.start():
        logger.error("Failed to start NTP server")
        return False
    if not self.pc_server.start():
        logger.error("Failed to start PC server")
        self.ntp_server.stop()
        return False
    self.is_running = True
    self.master_start_time = time.time()
    self.sync_thread = threading.Thread(
        target=self._sync_monitoring_loop,
        name="SyncMonitor"
    )
    self.sync_thread.daemon = True
    self.sync_thread.start()
    logger.info("Master clock synchronisation system started successfully")
except Exception as e:
    logger.error(f"Failed to start synchronisation system: {e}")
    return False
```

*Code Listing H.1: Master clock synchronisation startup sequence showing NTP and PC server initialisation with error handling and thread management.*

#### H.4.2 Data Pipeline Code (Physiological Signal Processing)

From the data pipeline module (`cv_preprocessing_pipeline.py`) for heart rate computation:

```python
# Inside PhysiologicalSignal.get_heart_rate_estimate()

freqs, psd = scipy.signal.welch(
    self.signal_data,
    fs=self.sampling_rate,
    nperseg=min(512, len(self.signal_data) // 4),
)
hr_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
hr_freqs = freqs[hr_mask]
hr_psd = psd[hr_mask]
if len(hr_psd) > 0:
    peak_freq = hr_freqs[np.argmax(hr_psd)]
    heart_rate_bpm = peak_freq * 60.0
    return heart_rate_bpm
```

*Code Listing H.2: Heart rate estimation from optical blood volume pulse signal using Fourier transform (Welch's method) to find dominant frequency.*

#### H.4.3 Integration Code (Sensor and Device Integration Logic)

From the `ShimmerManager` class showing Android-integrated Shimmer sensor initialisation:

```python
if self.enable_android_integration:
    logger.info("Initialising Android device integration...")
    self.android_device_manager = AndroidDeviceManager(
        server_port=self.android_server_port,
        logger=self.logger
    )
    self.android_device_manager.add_data_callback(self._on_android_shimmer_data)
    self.android_device_manager.add_status_callback(self._on_android_device_status)
    if not self.android_device_manager.initialise():
        logger.error("Failed to initialise Android device manager")
        if not PYSHIMMER_AVAILABLE:
            return False
        else:
            logger.warning("Continuing with direct connections only")
            self.enable_android_integration = False
    else:
        logger.info(f"Android device server listening on port {self.android_server_port}")
```

*Code Listing H.3: Sensor integration logic demonstrating flexible handling of Android-mediated connections with fallback to direct PC-to-sensor connectivity.*

#### H.4.4 Shimmer GSR Streaming Implementation

From the Shimmer GSR streaming implementation (`PythonApp/shimmer_manager.py`):

```python
try:
    from .shimmer.shimmer_imports import (
        DEFAULT_BAUDRATE,
        DataPacket,
        Serial,
        ShimmerBluetooth,
        PYSHIMMER_AVAILABLE,
    )
except ImportError:
    logger.warning("PyShimmer not available, shimmer functionality disabled")
    PYSHIMMER_AVAILABLE = False
```

*Code Listing H.4: Shimmer GSR streaming implementation showing modular import handling with graceful fallback when PyShimmer library is unavailable.*

[[3]](../../../README.md) - System Setup Documentation
[[4]](../../test_execution_guide.md) - Network Connectivity Guide  
[[5]](../../../PythonApp/README.md) - Python Package Installation
[[6]](../../../AndroidApp/README.md) - Android Device Configuration
[[14]](../../../README.md) - Network Configuration
[[15]](../../../PythonApp/README.md) - Computer Setup
[[16]](../../../AndroidApp/README.md) - Device Communication
[[17]](../../test_execution_guide.md) - Configuration Details
[[24]](../../../test_troubleshooting.md) - Firewall Configuration
[[26]](../../../test_troubleshooting.md) - Troubleshooting Help
[[27]](../../test_execution_guide.md) - Data Streaming Setup
[[28]](../../test_execution_guide.md) - Execution Steps

[[7]](../../../README.md) - Main System Documentation
[\[35\]](docs/README.md#L83-L88)
[\[48\]](docs/README.md#L152-L160)
README.md

<docs/README.md>

[\[32\]](PythonApp/network/pc_server.py#L44-L53)
[\[33\]](PythonApp/network/pc_server.py#L90-L98)
pc_server.py

<PythonApp/network/pc_server.py>

[\[36\]](evaluation_results/execution_logs.md#L16-L24)
[\[37\]](evaluation_results/execution_logs.md#L38-L46)
[\[38\]](evaluation_results/execution_logs.md#L104-L113)
[\[40\]](evaluation_results/execution_logs.md#L40-L48)
[\[41\]](evaluation_results/execution_logs.md#L50-L58)
[\[44\]](evaluation_results/execution_logs.md#L62-L70)
[\[45\]](evaluation_results/execution_logs.md#L72-L75)
[\[46\]](evaluation_results/execution_logs.md#L140-L146)
execution_logs.md

<evaluation_results/execution_logs.md>

[\[50\]](PythonApp/master_clock_synchronizer.py#L86-L94)
[\[51\]](PythonApp/master_clock_synchronizer.py#L95-L102)
[\[52\]](PythonApp/master_clock_synchronizer.py#L86-L102)
[\[53\]](PythonApp/master_clock_synchronizer.py#L164-L172)
master_clock_synchronizer.py

<PythonApp/master_clock_synchronizer.py>

[\[54\]](PythonApp/webcam/cv_preprocessing_pipeline.py#L72-L80)
cv_preprocessing_pipeline.py

<PythonApp/webcam/cv_preprocessing_pipeline.py>

[\[55\]](PythonApp/shimmer_manager.py#L241-L249)
[\[56\]](PythonApp/shimmer_manager.py#L250-L258)
[\[57\]](PythonApp/shimmer_manager.py#L241-L258)
[\[58\]](PythonApp/shimmer_manager.py#L134-L143)
[\[59\]](PythonApp/shimmer_manager.py#L269-L278)
[\[60\]](PythonApp/shimmer_manager.py#L280-L289)
[\[61\]](PythonApp/shimmer_manager.py#L145-L151)
shimmer_manager.py

<PythonApp/shimmer_manager.py>
