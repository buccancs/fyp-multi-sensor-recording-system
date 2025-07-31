# Chapter 4: System Architecture and Design

## 1. Introduction to System Architecture

The contactless GSR prediction system represents a sophisticated distributed computing architecture that seamlessly integrates multiple heterogeneous hardware platforms, diverse multi-modal sensor technologies, real-time signal processing capabilities, and state-of-the-art machine learning algorithms into a cohesive research platform. This system architecture addresses the fundamental challenges inherent in distributed physiological monitoring systems, including precise multi-device temporal synchronization, real-time data processing with sub-second latency requirements, robust inter-device communication protocols, and scalable deployment architectures that can accommodate varying research configurations while maintaining the exacting standards of research-grade measurement accuracy and clinical reliability demanded by physiological research applications.

The architectural complexity stems from the inherently distributed nature of the measurement problem, where multiple sensing devices must operate in perfect coordination to capture synchronized multi-modal data streams from subjects under study. Unlike traditional centralized measurement systems, this distributed approach enables the flexible positioning of sensing devices around subjects while maintaining precise temporal relationships between data streams from different modalities. This distributed sensing capability is essential for contactless monitoring applications where sensor placement flexibility directly impacts measurement quality and experimental feasibility.

This comprehensive chapter presents an in-depth technical analysis of the complete system architecture, with particular emphasis on the design decisions, engineering trade-offs, and implementation strategies that enable effective integration of all system components into a functioning research platform. The architecture draws upon established patterns from distributed systems engineering while incorporating novel approaches specifically developed for multi-modal physiological monitoring applications. The discussion encompasses both the theoretical foundations underlying the architectural decisions and the practical implementation considerations that drive system design choices.

The architectural analysis reveals how the system successfully balances competing requirements such as real-time performance versus processing accuracy, distributed autonomy versus centralized coordination, and research flexibility versus operational reliability. These fundamental trade-offs permeate every aspect of the system design, from low-level communication protocols to high-level data processing workflows, requiring careful consideration of how architectural decisions propagate through the entire system hierarchy.

### 1.1 Architectural Principles and Design Philosophy

The foundational architectural principles governing this system's design reflect decades of evolution in distributed systems engineering, adapted specifically for the unique challenges posed by real-time physiological monitoring applications. These principles form the theoretical foundation upon which all subsequent design decisions are evaluated and implemented.

**Modularity and Separation of Concerns:**
The system architecture employs rigorous modular design principles that create clear, well-defined boundaries between distinct functional domains, enabling each component to operate as an independent, self-contained unit with precisely specified interfaces. This architectural approach draws heavily from the principles of domain-driven design, where each module encapsulates specific domain knowledge and functionality while exposing minimal, well-documented interfaces to other system components. The modular separation extends beyond simple code organization to encompass data models, communication protocols, and deployment strategies, ensuring that changes within one module do not propagate uncontrolled effects throughout the system.

The implementation of strict separation of concerns enables independent development lifecycles for different system components, allowing specialized teams to focus on their areas of expertise without requiring deep knowledge of other system domains. This architectural decision proves particularly valuable in research environments where different aspects of the system may evolve at different rates based on research priorities and technological advances. For example, improvements to machine learning algorithms can be implemented and validated independently of changes to camera processing pipelines, enabling more agile development and validation processes.

The modular architecture also facilitates comprehensive testing strategies, where each module can be thoroughly tested in isolation before integration testing validates inter-module interactions. This testing approach significantly improves system reliability by enabling early detection of issues within individual components before they manifest as complex system-level failures that are difficult to diagnose and resolve.

**Distributed Processing and Computational Load Balancing:**
The architecture implements sophisticated distributed processing strategies that intelligently leverage the unique computational capabilities and resource constraints of each system component. Rather than employing a simple centralized processing model, the system distributes computational workloads based on careful analysis of processing requirements, available computational resources, power constraints, and communication costs associated with data movement between components.

Mobile devices, despite their computational limitations, handle computationally intensive but localized tasks such as real-time image processing for hand detection and region-of-interest extraction. This design decision minimizes the need to transmit high-bandwidth video data across the network while leveraging the specialized image processing capabilities of modern mobile processors. The local processing approach also provides important benefits in terms of privacy protection, as raw video data remains on the capture device rather than being transmitted across potentially insecure network connections.

The desktop controller system manages higher-level coordination tasks, complex signal processing algorithms, and machine learning inference operations that benefit from the increased computational resources and specialized hardware (such as discrete GPUs) available on desktop platforms. This distribution strategy optimizes overall system performance while maintaining reasonable power consumption on battery-powered mobile devices.

The distributed processing architecture also incorporates sophisticated load balancing mechanisms that can dynamically adjust processing distribution based on real-time system conditions. When mobile device battery levels drop or thermal constraints limit processing capability, the system can automatically shift additional processing load to the desktop controller, maintaining overall system performance despite changing operational conditions.

**Fault Tolerance and System Resilience:**
The architecture incorporates multiple layers of fault tolerance mechanisms designed to ensure continued system operation despite component failures, network disruptions, or environmental challenges commonly encountered in research settings. These resilience mechanisms operate at multiple system levels, from low-level hardware error detection to high-level workflow recovery strategies.

At the communication level, the system implements redundant communication paths with automatic failover capabilities. When the primary Wi-Fi communication channel experiences disruption, backup communication mechanisms can maintain critical coordination functions while the system works to restore full connectivity. The communication layer also implements sophisticated error detection and correction mechanisms that can identify and compensate for data corruption or loss during transmission.

Data integrity protection extends throughout the system, with comprehensive checksums, validation algorithms, and redundant storage mechanisms ensuring that collected research data remains intact despite system failures. The system maintains multiple copies of critical data and implements automated recovery procedures that can restore lost data from backup sources without requiring manual intervention.

The fault tolerance architecture also includes graceful degradation strategies that allow the system to continue operating with reduced functionality when certain components fail. For example, if one camera device fails during a multi-device measurement session, the system can continue collecting data from remaining devices while automatically adjusting processing algorithms to account for the reduced sensor coverage.

**Scalability and Future Extensibility:**
The system design incorporates forward-looking architectural decisions that anticipate future growth in device count, processing requirements, sensor modalities, and functional capabilities. Rather than optimizing solely for current requirements, the architecture provides extension points and expansion mechanisms that can accommodate future enhancements without requiring fundamental architectural redesign.

The communication protocol design supports dynamic device discovery and configuration, enabling new sensor devices to be added to existing measurement sessions without requiring system restart or reconfiguration. This capability proves essential for research applications where experimental requirements may evolve during data collection or where different research studies require different sensor configurations.

The data processing pipeline architecture employs plugin-based extensibility mechanisms that allow new signal processing algorithms, machine learning models, or analysis techniques to be integrated into the system without modifying core system components. This extensibility approach enables the system to evolve with advancing research methodologies while maintaining backward compatibility with existing datasets and analysis workflows.

Scalability considerations also extend to data storage and management, where the system architecture supports both local and cloud-based storage options with automatic scaling based on data volume requirements. The storage architecture can seamlessly transition between different storage backends as research data volumes grow beyond local storage capacity.

**Security, Privacy, and Ethical Data Handling:**
Privacy protection and data security considerations are integrated into every level of the system architecture, reflecting the sensitive nature of physiological data and the stringent requirements of human subjects research. The security architecture implements defense-in-depth strategies that provide multiple layers of protection against unauthorized access, data corruption, and privacy breaches.

Local data processing minimizes the exposure of sensitive raw data by performing initial analysis on capture devices before transmitting only processed results across network connections. This approach significantly reduces the attack surface for potential privacy breaches while also improving system performance by reducing network bandwidth requirements.

Communication security employs industry-standard encryption protocols with key management systems designed specifically for research environments. The system supports both symmetric and asymmetric encryption approaches, with automatic key rotation and secure key distribution mechanisms that ensure communication security without requiring complex manual key management procedures.

Data anonymization and pseudonymization capabilities are built into the core data processing pipeline, enabling researchers to protect subject privacy while maintaining the data relationships necessary for scientific analysis. The system supports configurable anonymization policies that can be tailored to specific research requirements and regulatory compliance needs.

### 1.2 Architectural Context and Environmental Considerations

The architectural design must accommodate the complex and varied requirements imposed by different research environments, user populations, and experimental methodologies, requiring flexible adaptation capabilities while maintaining consistent performance and reliability standards across diverse operational contexts.

**Research Environment Requirements and Operational Flexibility:**
The system must demonstrate robust operational capability across an exceptionally wide range of research environments, from highly controlled laboratory settings with stable environmental conditions and reliable infrastructure to naturalistic field studies conducted in unpredictable environments with limited infrastructure support. This environmental diversity drives fundamental architectural decisions regarding system portability, setup complexity, environmental robustness, and infrastructure dependencies.

In controlled laboratory environments, the system can leverage stable power supplies, high-quality network infrastructure, and controlled lighting and temperature conditions to optimize measurement accuracy and system performance. The architecture takes advantage of these favorable conditions by implementing more sophisticated processing algorithms and higher-resolution data collection modes that might not be feasible in resource-constrained field environments.

Conversely, in field research environments, the system must operate effectively with limited power availability, unreliable network connectivity, and highly variable environmental conditions that can significantly impact measurement quality. The architecture addresses these challenges through adaptive power management strategies, offline operation capabilities, and robust environmental compensation algorithms that maintain measurement validity despite suboptimal conditions.

The architectural flexibility extends to physical setup requirements, where the system can accommodate different spatial configurations based on research space constraints and experimental requirements. Whether deployed in a small clinical examination room or a large behavioral research laboratory, the system adapts its sensor placement strategies and communication topologies to optimize performance within available space constraints.

**Multi-Stakeholder Support and Role-Based System Interaction:**
The system architecture must support fundamentally different interaction patterns and requirements for various stakeholder groups, each with distinct goals, technical expertise levels, and system access needs. This multi-stakeholder support requires sophisticated user interface design, flexible access control mechanisms, and adaptable system behavior that can provide appropriate functionality and information to each user role.

Research investigators require comprehensive system control and monitoring capabilities, including access to detailed system status information, real-time data quality assessments, experimental parameter configuration options, and troubleshooting tools. The architecture provides these users with powerful interfaces that expose the full complexity and capability of the system while maintaining safety mechanisms that prevent accidental system damage or data loss.

Research subjects interact with the system through carefully designed interfaces that minimize cognitive load and experimental disruption while providing necessary feedback about system status and measurement progress. The subject-facing interfaces prioritize simplicity, clarity, and non-intrusiveness, hiding the underlying system complexity while maintaining transparency about data collection activities to support informed consent requirements.

Technical support personnel require diagnostic access to system internals, including detailed logging information, performance metrics, hardware status monitoring, and remote troubleshooting capabilities. The architecture provides specialized interfaces and tools that enable efficient system maintenance and problem resolution without requiring physical access to deployed systems.

System administrators need comprehensive oversight capabilities for multi-system deployments, including centralized monitoring, configuration management, software update distribution, and security policy enforcement. The architecture supports these requirements through centralized management interfaces that can coordinate multiple distributed system instances while maintaining appropriate security boundaries.

**Regulatory and Ethical Compliance Framework:**
The architecture incorporates comprehensive compliance mechanisms designed to support adherence to research ethics requirements, data protection regulations, and emerging medical device standards that may apply to physiological monitoring systems used in clinical research contexts. These compliance features are integrated into the fundamental system design rather than being added as afterthoughts, ensuring that compliance support does not compromise system performance or reliability.

The compliance framework begins with built-in privacy protection mechanisms that implement privacy-by-design principles throughout the system architecture. Personal data minimization strategies ensure that the system collects, processes, and stores only the minimum data necessary for research objectives, while comprehensive data anonymization capabilities enable research analysis while protecting subject privacy.

Audit and traceability capabilities provide comprehensive logging of all system activities, data access events, and configuration changes, creating an immutable audit trail that supports research integrity validation and regulatory compliance verification. The audit system operates independently of other system components, ensuring that audit data remains intact even if other system components experience failures or security breaches.

The architecture also supports configurable data retention and deletion policies that enable compliance with varying regulatory requirements across different research contexts and jurisdictions. Automated data lifecycle management ensures that personal data is retained only as long as necessary for research purposes and is securely deleted when retention periods expire.

Consent management capabilities integrated into the system architecture support dynamic consent models where research subjects can modify their consent preferences throughout the research study. The system automatically adapts data collection and processing activities based on current consent status, ensuring ongoing compliance with subject preferences and regulatory requirements.

## 2. Overall System Architecture

## 2. Overall System Architecture

### 2.1 High-Level Architecture Overview and System Topology

The contactless GSR prediction system employs a sophisticated distributed architecture consisting of multiple interconnected subsystems, each specifically optimized for distinct functional roles within the comprehensive data acquisition, processing, and analysis workflow. This distributed approach enables the system to leverage the unique capabilities of different hardware platforms while managing the complex coordination required for real-time multi-modal physiological monitoring.

The architectural topology reflects careful consideration of the fundamental requirements for contactless physiological monitoring, including the need for flexible sensor positioning, real-time data processing, reliable inter-device communication, and scalable deployment strategies. Unlike monolithic systems that concentrate all functionality within a single device, this distributed architecture enables optimal placement of different functional components based on their specific requirements and constraints.

**Core Architectural Components and Their Functional Roles:**

**Mobile Data Acquisition Units (Android Devices) - Primary Sensing Platforms:**

These specialized sensing platforms serve as the cornerstone of the data acquisition infrastructure, responsible for capturing high-quality multi-modal sensor data while performing sophisticated real-time preprocessing to optimize system performance and data quality. Each mobile unit represents a complete sensing system capable of independent operation while participating in coordinated multi-device measurement sessions.

The mobile platforms perform several critical functions that leverage the unique capabilities of modern smartphone hardware. The primary function involves coordinating multiple sensor modalities to capture synchronized data streams that provide complementary information about physiological state. The RGB camera system captures high-resolution visible light imagery that enables detection of subtle color changes associated with blood volume variations, while the integrated thermal camera provides temperature distribution data that reveals sympathetic nervous system activation patterns.

The selection of Samsung Galaxy S22 smartphones as the hardware platform reflects careful analysis of the specific requirements for contactless physiological monitoring applications. These devices provide exceptional camera quality with precise exposure control, advanced image stabilization systems, and powerful mobile processors capable of real-time image processing. The high-quality display systems enable precise feedback to research subjects, while the robust wireless communication capabilities ensure reliable coordination with other system components.

The attachment of specialized thermal cameras transforms these mobile platforms into sophisticated multi-spectral sensing systems capable of simultaneous visible and infrared imaging. The thermal cameras provide temperature measurement capabilities with sensitivity sufficient to detect the subtle thermal changes associated with sympathetic activation and circulatory responses. The integration of thermal and visible cameras requires sophisticated calibration and synchronization mechanisms to ensure accurate alignment between the different imaging modalities.

Local preprocessing capabilities implemented on the mobile platforms significantly enhance overall system performance by reducing network bandwidth requirements and improving real-time responsiveness. Hand detection algorithms operating on the mobile devices identify regions of interest within the captured imagery, enabling focused analysis on physiologically relevant areas while reducing computational load on downstream processing systems. ROI extraction and initial signal conditioning prepare the sensor data for efficient transmission and further analysis.

The mobile platforms also implement sophisticated power management strategies that balance measurement quality with battery life constraints. Adaptive processing algorithms can modify their computational complexity based on available power levels, ensuring continued operation throughout extended measurement sessions while maintaining acceptable data quality standards.

**Desktop Controller System - Central Coordination and Processing Hub:**

The desktop controller system serves as the central nervous system of the distributed architecture, coordinating all system activities while providing the computational resources necessary for advanced signal processing and machine learning operations. This centralized coordination approach enables sophisticated multi-device synchronization while leveraging the superior computational capabilities available on desktop platforms.

The controller system implements comprehensive device management capabilities that enable automatic discovery, configuration, and coordination of mobile sensing units. The device management subsystem maintains real-time awareness of all connected devices, monitoring their operational status, battery levels, data quality metrics, and communication connectivity. This comprehensive monitoring enables proactive system management that can address potential issues before they impact data collection quality.

Real-time data processing capabilities implemented on the desktop controller enable sophisticated analysis techniques that would be computationally prohibitive on mobile platforms. Advanced signal processing algorithms extract physiological signals from multi-modal sensor data, while machine learning models provide real-time GSR predictions based on the processed signals. The desktop platform's superior computational resources enable more sophisticated algorithms and higher temporal resolution processing than would be feasible with distributed processing approaches.

The controller system also implements comprehensive data storage and management capabilities that ensure research data integrity while supporting flexible analysis workflows. Local storage systems provide high-speed access to recent data for real-time analysis, while archival storage systems ensure long-term data preservation for longitudinal research studies. The storage architecture supports both structured and unstructured data formats, accommodating the diverse data types generated by multi-modal sensing systems.

Visualization and user interface capabilities provide researchers with comprehensive real-time insight into system operation and data quality. The desktop interface presents synchronized views of all sensor data streams, enabling immediate assessment of measurement quality and system performance. Advanced visualization tools help researchers identify potential issues and optimize experimental configurations for specific research requirements.

**Network Communication Infrastructure - System Backbone:**

The network communication infrastructure forms the critical backbone that enables coordinated operation of the distributed system components. This communication layer must support multiple simultaneous data streams while maintaining precise temporal synchronization and ensuring reliable data delivery despite varying network conditions.

The wireless networking approach provides essential flexibility for research applications where sensor positioning requirements may conflict with wired connectivity constraints. Wi-Fi networking offers the bandwidth and latency characteristics necessary for real-time data transmission while supporting dynamic device configuration and mobile sensor positioning. The networking architecture implements sophisticated quality-of-service mechanisms that prioritize critical control traffic while ensuring adequate bandwidth allocation for data streams.

Communication protocol design emphasizes reliability and fault tolerance, with comprehensive error detection and recovery mechanisms that ensure data integrity despite temporary network disruptions. Automatic reconnection capabilities enable seamless recovery from network interruptions, while data buffering mechanisms prevent data loss during temporary connectivity issues.

The networking infrastructure also implements security mechanisms that protect sensitive physiological data during transmission. Encryption protocols ensure that intercepted network traffic cannot reveal personal health information, while authentication mechanisms prevent unauthorized devices from accessing the research system or contaminating collected data.

**Data Storage and Analysis Subsystem - Information Management:**

The data storage and analysis subsystem provides comprehensive information management capabilities that support both real-time research activities and long-term data preservation requirements. This subsystem must accommodate the high data volumes generated by multi-modal sensing while providing efficient access to historical data for longitudinal analysis.

Storage architecture design reflects the diverse requirements of different data types, from high-frequency sensor data requiring rapid access to processed analysis results requiring long-term preservation. The storage system implements hierarchical storage management that automatically migrates data between different storage tiers based on access patterns and retention requirements.

Data format standardization ensures compatibility between different system components while supporting future extensibility requirements. The storage system implements standardized data formats that facilitate interoperability with external analysis tools while maintaining comprehensive metadata that preserves the context necessary for scientific reproducibility.

Backup and disaster recovery mechanisms protect against data loss while supporting distributed deployment scenarios where different research sites may have varying infrastructure capabilities. Automated backup systems ensure regular data protection without requiring manual intervention, while recovery procedures enable rapid restoration of system functionality following hardware failures or other disruptions.
- Storage: Local buffering with automated backup to central storage

**Central Control Station (Desktop Computer):**
- Primary function: System coordination and comprehensive data management
- Secondary function: Advanced processing and analysis
- Hardware: High-performance Windows PC with substantial storage capacity
- Communication: Central hub for all device communication and coordination
- Processing: Machine learning inference, multi-device synchronization, data analysis
- Storage: Primary data repository with backup and archival capabilities

**Physiological Reference Sensors (Shimmer3 GSR+):**
- Primary function: Ground truth GSR measurement for validation
- Secondary function: System calibration and accuracy verification
- Hardware: Research-grade wireless physiological sensors
- Communication: Bluetooth connectivity to mobile devices or central station
- Processing: High-resolution physiological signal acquisition
- Storage: Synchronized data logging with video streams

**Network Infrastructure:**
- Primary function: Real-time communication between all system components
- Secondary function: Data synchronization and coordination
- Technology: Wi-Fi networking with WebSocket protocols
- Features: Automatic device discovery, fault-tolerant communication, bandwidth optimization
- Security: Encrypted communication channels with access control

### 2.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CENTRAL CONTROL STATION                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   Coordination  │  │   Data Storage  │  │   Analysis      │    │
│  │   & Control     │  │   & Management  │  │   & ML Engine   │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│           │                     │                     │            │
└───────────┼─────────────────────┼─────────────────────┼────────────┘
            │                     │                     │
    ┌───────┴───────┐    ┌────────┴────────┐    ┌──────┴──────┐
    │               │    │                 │    │             │
┌───▼───┐       ┌───▼───┐│              ┌──▼──┐ │         ┌───▼───┐
│Device │       │Device ││              │ NAS │ │         │ Cloud │
│   1   │       │   2   ││              │Store│ │         │Backup │
└───┬───┘       └───┬───┘│              └─────┘ │         └───────┘
    │               │    │                      │
┌───▼───┐       ┌───▼───┐│                      │
│Thermal│       │Thermal││                      │
│Camera │       │Camera ││                      │
└───────┘       └───────┘│                      │
    │               │    │                      │
┌───▼───┐       ┌───▼───┐│              ┌───────▼─────────┐
│ GSR   │       │ GSR   ││              │   Wi-Fi Network │
│Sensor │       │Sensor ││              │   Infrastructure│
└───────┘       └───────┘│              └─────────────────┘
                         │
                         │
            ┌────────────▼────────────┐
            │    EXPERIMENTAL         │
            │    ENVIRONMENT          │
            │                         │
            │  ┌─────────────────┐   │
            │  │    Subject      │   │
            │  │   Positioning   │   │
            │  └─────────────────┘   │
            └─────────────────────────┘
```

### 2.3 Data Flow Architecture

**Real-Time Data Flow:**

1. **Acquisition Layer:**
   - Simultaneous capture from RGB cameras (30 FPS)
   - Thermal camera capture (15 FPS) synchronized with RGB
   - GSR sensor sampling (128-512 Hz) with precise timestamping
   - Environmental sensor logging for context

2. **Processing Layer:**
   - Hand detection and landmark extraction (MediaPipe)
   - Multi-ROI signal extraction from both modalities
   - Signal preprocessing and quality assessment
   - Feature extraction for machine learning inference

3. **Fusion Layer:**
   - Multi-modal feature combination (RGB + thermal)
   - Multi-ROI signal fusion with quality weighting
   - Temporal filtering and artifact rejection
   - Confidence estimation and uncertainty quantification

4. **Inference Layer:**
   - Real-time GSR prediction using trained models
   - Temporal smoothing and outlier detection
   - Alert generation for significant deviations
   - Performance monitoring and adaptation

5. **Output Layer:**
   - Real-time visualization and monitoring interfaces
   - Data logging and archival systems
   - External system integration and notifications
   - Research data export and sharing

**Offline Data Flow:**

1. **Data Import and Validation:**
   - Batch import of collected datasets
   - Data integrity verification and quality assessment
   - Metadata extraction and organization
   - Cross-modal temporal alignment verification

2. **Preprocessing Pipeline:**
   - Signal cleaning and artifact removal
   - Normalization and standardization procedures
   - Feature extraction and dimensionality reduction
   - Data augmentation for model training

3. **Analysis Pipeline:**
   - Statistical analysis and correlation studies
   - Machine learning model training and validation
   - Cross-subject and cross-condition analysis
   - Performance evaluation and benchmarking

4. **Results Generation:**
   - Automated report generation and visualization
   - Model performance metrics and comparisons
   - Scientific publication material preparation
   - Dataset documentation and metadata

### 2.4 Communication Architecture

**Network Topology:**
The system employs a star topology with the central control station as the hub, connecting to all mobile devices and sensors. This topology simplifies coordination and provides centralized monitoring and control capabilities.

**Communication Protocols:**

**WebSocket Protocol for Real-Time Communication:**
- Bidirectional communication between control station and mobile devices
- Low-latency message exchange for coordination and control
- Automatic reconnection and fault tolerance
- Heartbeat monitoring for connection status

**TCP/IP for Data Transfer:**
- Reliable file transfer for large data files
- Streaming data transfer for continuous monitoring
- Error detection and automatic retransmission
- Bandwidth optimization and flow control

**Bluetooth for Sensor Communication:**
- Direct connection between GSR sensors and mobile devices
- Low-power operation for extended battery life
- Automatic pairing and device discovery
- Error recovery and reconnection procedures

**Message Format Standardization:**
All inter-component communication uses standardized JSON message formats with defined schemas for different message types:
- Control messages for system coordination
- Data messages for sensor information transfer
- Status messages for health monitoring
- Alert messages for error conditions and notifications

## 3. Mobile Device Architecture (Android Application)

### 3.1 Android Application Architecture

The Android application follows Clean Architecture principles with clear separation between data, domain, and presentation layers. This architecture ensures maintainability, testability, and scalability while supporting the complex requirements of multi-modal data acquisition.

**Architecture Layers:**

**Presentation Layer:**
- Activities and Fragments for user interface
- ViewModels for UI state management
- Data binding for reactive UI updates
- Custom views for specialized visualizations

**Domain Layer:**
- Use cases for business logic encapsulation
- Repository interfaces for data access abstraction
- Domain models for core data structures
- Validation logic for data integrity

**Data Layer:**
- Repository implementations for data source coordination
- Data sources for external API integration
- Local database for caching and offline operation
- Network layer for remote communication

**Infrastructure Layer:**
- Dependency injection for component wiring
- Background services for continuous operation
- Notification system for user alerts
- Security layer for data protection

### 3.2 Core Android Components

**3.2.1 Camera Management System**

**Camera Controller Architecture:**
```kotlin
interface CameraController {
    suspend fun initializeCamera(): Result<Unit>
    suspend fun startPreview(): Result<Unit>
    suspend fun startRecording(): Result<Unit>
    suspend fun stopRecording(): Result<Unit>
    fun configureSettings(settings: CameraSettings): Result<Unit>
}

class Camera2Controller : CameraController {
    private val cameraManager: CameraManager
    private val imageReader: ImageReader
    private val surfaceView: SurfaceView
    private val recordingSession: CameraCaptureSession
    
    // Implementation details...
}
```

**Key Design Features:**
- Asynchronous camera operations using Kotlin coroutines
- Automatic camera parameter optimization for physiological monitoring
- Real-time preview with overlay for hand positioning guidance
- Simultaneous photo and video capture capabilities
- Integration with thermal camera synchronization

**Thermal Camera Integration:**
```kotlin
class ThermalCameraManager {
    private val topdonSdk: TopdonSDK
    private var thermalCallback: ThermalFrameCallback?
    
    fun initializeThermalCamera(): Result<Unit> {
        return try {
            topdonSdk.initialize()
            topdonSdk.setFrameCallback(thermalCallback)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    fun synchronizeWithRGB(rgbTimestamp: Long): ThermalFrame? {
        return findClosestThermalFrame(rgbTimestamp)
    }
}
```

**3.2.2 Sensor Integration System**

**GSR Sensor Controller:**
```kotlin
class ShimmerGSRController {
    private val bluetoothManager: BluetoothManager
    private val shimmerDevice: Shimmer
    private var dataCallback: GSRDataCallback?
    
    suspend fun connectToSensor(deviceAddress: String): Result<Unit>
    suspend fun startDataCollection(): Result<Unit>
    suspend fun configureSampling(rate: Int): Result<Unit>
    fun getLatestGSRReading(): GSRReading?
}
```

**Environmental Sensor Integration:**
```kotlin
class EnvironmentalSensorManager {
    private val sensorManager: SensorManager
    private val temperatureSensor: Sensor?
    private val humiditySensor: Sensor?
    private val lightSensor: Sensor?
    
    fun registerSensorListeners(): Result<Unit>
    fun getCurrentEnvironmentalData(): EnvironmentalData
}
```

**3.2.3 Real-Time Processing Pipeline**

**Hand Detection and Tracking:**
```kotlin
class HandDetectionProcessor {
    private val mediaPipe: MediaPipeHands
    private var landmarks: List<Landmark> = emptyList()
    
    fun processFrame(bitmap: Bitmap): HandDetectionResult {
        val results = mediaPipe.process(bitmap)
        landmarks = results.multiHandLandmarks()
        return HandDetectionResult(landmarks, results.confidence)
    }
    
    fun extractROIs(landmarks: List<Landmark>): List<ROI> {
        return listOf(
            ROI.indexFingerBase(landmarks[5]),
            ROI.ringFingerBase(landmarks[13]),
            ROI.palmCenter(calculatePalmCenter(landmarks))
        )
    }
}
```

**Signal Extraction Engine:**
```kotlin
class SignalExtractionEngine {
    private val signalProcessor: SignalProcessor
    private val qualityAssessor: SignalQualityAssessor
    
    fun extractSignals(
        rgbFrame: Bitmap,
        thermalFrame: ThermalFrame,
        rois: List<ROI>
    ): SignalExtractionResult {
        val rgbSignals = rois.map { roi -> 
            extractRGBSignal(rgbFrame, roi) 
        }
        val thermalSignals = rois.map { roi -> 
            extractThermalSignal(thermalFrame, roi) 
        }
        
        val quality = qualityAssessor.assess(rgbSignals, thermalSignals)
        
        return SignalExtractionResult(rgbSignals, thermalSignals, quality)
    }
}
```

**3.2.4 Communication and Networking**

**WebSocket Communication Manager:**
```kotlin
class NetworkCommunicationManager {
    private val webSocketClient: WebSocketClient
    private val messageQueue: Queue<NetworkMessage>
    private var connectionState: ConnectionState = Disconnected
    
    suspend fun connectToControlStation(address: String): Result<Unit>
    suspend fun sendMessage(message: NetworkMessage): Result<Unit>
    fun registerMessageHandler(handler: MessageHandler): Unit
    
    private fun handleReconnection() {
        // Automatic reconnection logic with exponential backoff
    }
}
```

**Data Synchronization Manager:**
```kotlin
class DataSynchronizationManager {
    private val timestampProvider: TimestampProvider
    private val syncBuffer: SynchronizationBuffer
    
    fun synchronizeData(
        rgbData: RGBData,
        thermalData: ThermalData,
        gsrData: GSRData
    ): SynchronizedDataPacket {
        val baseTimestamp = timestampProvider.getCurrentTimestamp()
        return SynchronizedDataPacket(
            timestamp = baseTimestamp,
            rgbData = rgbData.withTimestamp(baseTimestamp),
            thermalData = thermalData.withTimestamp(baseTimestamp),
            gsrData = gsrData.withTimestamp(baseTimestamp)
        )
    }
}
```

### 3.3 Android Application Data Architecture

**3.3.1 Local Data Management**

**Room Database Schema:**
```kotlin
@Entity(tableName = "recording_sessions")
data class RecordingSession(
    @PrimaryKey val sessionId: String,
    val startTime: Long,
    val endTime: Long?,
    val subjectId: String,
    val configuration: SessionConfiguration
)

@Entity(tableName = "sensor_data")
data class SensorDataEntity(
    @PrimaryKey val id: String,
    val sessionId: String,
    val timestamp: Long,
    val sensorType: SensorType,
    val data: ByteArray,
    val metadata: String
)

@Dao
interface RecordingDao {
    @Query("SELECT * FROM recording_sessions WHERE sessionId = :sessionId")
    suspend fun getSession(sessionId: String): RecordingSession?
    
    @Insert
    suspend fun insertSensorData(data: SensorDataEntity)
    
    @Query("SELECT * FROM sensor_data WHERE sessionId = :sessionId AND timestamp BETWEEN :start AND :end")
    suspend fun getSensorDataInRange(sessionId: String, start: Long, end: Long): List<SensorDataEntity>
}
```

**File System Organization:**
```
/Android/data/com.multisensor.recording/files/
├── sessions/
│   ├── {session_id}/
│   │   ├── metadata.json
│   │   ├── rgb_video/
│   │   │   ├── video_001.mp4
│   │   │   └── timestamps.csv
│   │   ├── thermal_video/
│   │   │   ├── thermal_001.bin
│   │   │   └── thermal_metadata.json
│   │   ├── gsr_data/
│   │   │   ├── gsr_001.csv
│   │   │   └── quality_metrics.json
│   │   └── processed_data/
│   │       ├── hand_landmarks.csv
│   │       ├── roi_signals.csv
│   │       └── predictions.csv
├── models/
│   ├── hand_detection.tflite
│   ├── gsr_prediction.tflite
│   └── model_metadata.json
└── configuration/
    ├── device_config.json
    ├── calibration_data.json
    └── user_preferences.json
```

**3.3.2 Background Processing Services**

**Data Collection Service:**
```kotlin
class DataCollectionService : Service() {
    private val cameraController: CameraController by inject()
    private val thermalController: ThermalCameraManager by inject()
    private val gsrController: ShimmerGSRController by inject()
    private val processingPipeline: ProcessingPipeline by inject()
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        startDataCollection()
        return START_STICKY
    }
    
    private fun startDataCollection() {
        GlobalScope.launch {
            val rgbFlow = cameraController.getFrameFlow()
            val thermalFlow = thermalController.getFrameFlow()
            val gsrFlow = gsrController.getDataFlow()
            
            combine(rgbFlow, thermalFlow, gsrFlow) { rgb, thermal, gsr ->
                processingPipeline.processData(rgb, thermal, gsr)
            }.collect { result ->
                handleProcessingResult(result)
            }
        }
    }
}
```

**Network Synchronization Service:**
```kotlin
class NetworkSyncService : Service() {
    private val communicationManager: NetworkCommunicationManager by inject()
    private val dataRepository: DataRepository by inject()
    
    override fun onCreate() {
        super.onCreate()
        setupPeriodicSync()
    }
    
    private fun setupPeriodicSync() {
        val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()
            
        WorkManager.getInstance(this).enqueue(workRequest)
    }
}
```

### 3.4 Android Performance Optimization

**3.4.1 Memory Management**

**Image Processing Optimization:**
```kotlin
class OptimizedImageProcessor {
    private val imagePool: ObjectPool<Bitmap> = ObjectPool(
        createObject = { Bitmap.createBitmap(1920, 1080, Bitmap.Config.RGB_565) },
        resetObject = { bitmap -> bitmap.eraseColor(Color.TRANSPARENT) },
        maxPoolSize = 10
    )
    
    fun processImage(inputBitmap: Bitmap): ProcessingResult {
        val workingBitmap = imagePool.acquire()
        try {
            // Perform processing using pooled bitmap
            return performImageProcessing(workingBitmap, inputBitmap)
        } finally {
            imagePool.release(workingBitmap)
        }
    }
}
```

**Memory-Efficient Data Structures:**
```kotlin
class CircularBuffer<T>(private val capacity: Int) {
    private val buffer = Array<Any?>(capacity) { null }
    private var head = 0
    private var tail = 0
    private var size = 0
    
    fun add(item: T) {
        buffer[tail] = item
        tail = (tail + 1) % capacity
        if (size < capacity) {
            size++
        } else {
            head = (head + 1) % capacity
        }
    }
    
    @Suppress("UNCHECKED_CAST")
    fun get(index: Int): T? {
        if (index >= size) return null
        val actualIndex = (head + index) % capacity
        return buffer[actualIndex] as T?
    }
}
```

**3.4.2 Processing Pipeline Optimization**

**Parallel Processing Architecture:**
```kotlin
class ParallelProcessingPipeline {
    private val processingDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()
    private val ioDispatcher = Dispatchers.IO
    
    suspend fun processFrame(frame: VideoFrame): ProcessingResult = withContext(processingDispatcher) {
        val handDetectionJob = async { detectHands(frame) }
        val qualityAssessmentJob = async { assessQuality(frame) }
        val signalExtractionJob = async { extractSignals(frame) }
        
        val handResults = handDetectionJob.await()
        val qualityResults = qualityAssessmentJob.await()
        val signalResults = signalExtractionJob.await()
        
        combineResults(handResults, qualityResults, signalResults)
    }
}
```

**Battery Optimization:**
```kotlin
class PowerOptimizationManager {
    private val powerManager: PowerManager
    private val batteryManager: BatteryManager
    
    fun optimizeForPowerSaving() {
        when {
            getBatteryLevel() < 20 -> {
                // Reduce frame rate and processing quality
                setCameraFrameRate(15)
                setProcessingQuality(ProcessingQuality.LOW)
            }
            getBatteryLevel() < 50 -> {
                // Moderate optimization
                setCameraFrameRate(20)
                setProcessingQuality(ProcessingQuality.MEDIUM)
            }
            else -> {
                // Full performance
                setCameraFrameRate(30)
                setProcessingQuality(ProcessingQuality.HIGH)
            }
        }
    }
    
    private fun getBatteryLevel(): Int {
        return batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }
}
```

## 4. Desktop Application Architecture (Python)

### 4.1 Desktop Application Architecture Overview

The desktop application serves as the central control and coordination hub for the entire system, implementing a sophisticated architecture that manages multi-device communication, real-time data processing, comprehensive visualization, and extensive data management capabilities.

**Architectural Pattern:**
The desktop application follows the Model-View-Controller (MVC) pattern enhanced with additional layers for complex data processing and external system integration. This architecture provides clear separation of concerns while maintaining the flexibility needed for research applications.

**Core Architecture Layers:**

**Presentation Layer (View):**
- PyQt5-based user interfaces for researcher interaction
- Real-time data visualization using matplotlib integration
- Custom widgets for specialized scientific visualization
- Responsive design supporting multiple monitor configurations

**Controller Layer:**
- Application logic coordination and workflow management
- User input processing and validation
- System state management and configuration
- Error handling and user feedback coordination

**Service Layer:**
- Business logic implementation for research workflows
- Data processing coordination and pipeline management
- External system integration and API management
- Background task coordination and scheduling

**Data Access Layer (Model):**
- Database connectivity and data persistence
- File system management and organization
- Network communication and protocol handling
- Data validation and integrity checking

**Infrastructure Layer:**
- Logging and monitoring systems
- Configuration management and environment setup
- Security and authentication services
- Performance monitoring and optimization

### 4.2 Core Desktop Application Components

**4.2.1 Application Framework and Structure**

**Main Application Class:**
```python
class GSRPredictionApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("GSR Prediction System")
        self.setApplicationVersion("1.0.0")
        
        # Initialize core components
        self.config_manager = ConfigurationManager()
        self.device_manager = DeviceManager()
        self.data_manager = DataManager()
        self.analysis_engine = AnalysisEngine()
        
        # Setup main window
        self.main_window = MainWindow()
        self.setup_signal_connections()
        
    def setup_signal_connections(self):
        """Connect signals between major components"""
        self.device_manager.device_connected.connect(
            self.main_window.update_device_status
        )
        self.data_manager.data_received.connect(
            self.main_window.update_data_display
        )
        
    def run(self):
        """Main application entry point"""
        self.main_window.show()
        return self.exec_()
```

**Configuration Management System:**
```python
class ConfigurationManager:
    def __init__(self):
        self.config_file = Path.home() / ".gsr_prediction" / "config.json"
        self.default_config = {
            "network": {
                "discovery_port": 8888,
                "data_port": 8889,
                "timeout": 30
            },
            "recording": {
                "default_duration": 300,
                "sample_rate": 30,
                "quality_threshold": 0.7
            },
            "analysis": {
                "model_path": "./models/gsr_prediction.tflite",
                "batch_size": 32,
                "confidence_threshold": 0.8
            }
        }
        self.load_configuration()
        
    def load_configuration(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config.copy()
            self.save_configuration()
            
    def save_configuration(self):
        """Save current configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
```

**4.2.2 Device Management and Communication**

**Device Discovery and Management:**
```python
class DeviceManager(QObject):
    device_connected = pyqtSignal(dict)
    device_disconnected = pyqtSignal(str)
    data_received = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.devices = {}
        self.discovery_server = None
        self.communication_servers = {}
        
    def start_device_discovery(self):
        """Start UDP broadcast for device discovery"""
        self.discovery_server = DeviceDiscoveryServer(
            port=8888,
            callback=self.handle_device_discovery
        )
        self.discovery_server.start()
        
    def handle_device_discovery(self, device_info, address):
        """Handle discovered device and establish connection"""
        device_id = device_info.get('device_id')
        if device_id not in self.devices:
            # Create WebSocket connection for real-time communication
            ws_client = WebSocketClient(
                f"ws://{address[0]}:{device_info.get('ws_port')}"
            )
            ws_client.message_received.connect(
                lambda msg: self.data_received.emit(device_id, msg)
            )
            
            self.devices[device_id] = {
                'info': device_info,
                'address': address,
                'websocket': ws_client,
                'status': 'connected'
            }
            
            self.device_connected.emit(device_info)
            
    def send_command(self, device_id: str, command: dict):
        """Send command to specific device"""
        if device_id in self.devices:
            ws_client = self.devices[device_id]['websocket']
            ws_client.send_message(command)
            
    def broadcast_command(self, command: dict):
        """Send command to all connected devices"""
        for device_id in self.devices:
            self.send_command(device_id, command)
```

**WebSocket Communication Implementation:**
```python
class WebSocketClient(QObject):
    message_received = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool)
    
    def __init__(self, uri):
        super().__init__()
        self.uri = uri
        self.websocket = None
        self.loop = None
        self.thread = None
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connection_status_changed.emit(True)
            
            # Listen for messages
            async for message in self.websocket:
                data = json.loads(message)
                self.message_received.emit(data)
                
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            self.connection_status_changed.emit(False)
            
    def send_message(self, message: dict):
        """Send message through WebSocket"""
        if self.websocket and not self.websocket.closed:
            asyncio.create_task(
                self.websocket.send(json.dumps(message))
            )
```

**4.2.3 Real-Time Data Processing and Visualization**

**Data Processing Pipeline:**
```python
class RealTimeDataProcessor(QObject):
    processing_complete = pyqtSignal(dict)
    quality_alert = pyqtSignal(str, float)
    
    def __init__(self):
        super().__init__()
        self.signal_buffer = {}
        self.quality_assessor = SignalQualityAssessor()
        self.ml_inference_engine = MLInferenceEngine()
        
    def process_incoming_data(self, device_id: str, data: dict):
        """Process real-time data from devices"""
        data_type = data.get('type')
        timestamp = data.get('timestamp')
        
        if data_type == 'video_frame':
            self.process_video_frame(device_id, data, timestamp)
        elif data_type == 'sensor_data':
            self.process_sensor_data(device_id, data, timestamp)
        elif data_type == 'hand_landmarks':
            self.process_hand_landmarks(device_id, data, timestamp)
            
    def process_video_frame(self, device_id: str, frame_data: dict, timestamp: float):
        """Process incoming video frame data"""
        # Decode frame data
        frame_bytes = base64.b64decode(frame_data['image_data'])
        frame = cv2.imdecode(
            np.frombuffer(frame_bytes, np.uint8), 
            cv2.IMREAD_COLOR
        )
        
        # Extract signals from ROIs if landmarks available
        if device_id in self.signal_buffer and 'landmarks' in self.signal_buffer[device_id]:
            landmarks = self.signal_buffer[device_id]['landmarks']
            roi_signals = self.extract_roi_signals(frame, landmarks)
            
            # Assess signal quality
            quality_score = self.quality_assessor.assess_frame_quality(
                frame, roi_signals
            )
            
            if quality_score < 0.5:
                self.quality_alert.emit(device_id, quality_score)
                
            # Store for ML inference
            self.buffer_for_inference(device_id, roi_signals, timestamp)
            
    def extract_roi_signals(self, frame, landmarks):
        """Extract RGB signals from regions of interest"""
        rois = [
            self.get_roi_region(frame, landmarks[5]),   # Index finger base
            self.get_roi_region(frame, landmarks[13]),  # Ring finger base
            self.get_roi_region(frame, self.calculate_palm_center(landmarks))
        ]
        
        signals = []
        for roi in rois:
            # Calculate mean RGB values for ROI
            mean_rgb = np.mean(roi, axis=(0, 1))
            signals.append(mean_rgb)
            
        return np.array(signals)
        
    def buffer_for_inference(self, device_id: str, signals: np.ndarray, timestamp: float):
        """Buffer signals for machine learning inference"""
        if device_id not in self.signal_buffer:
            self.signal_buffer[device_id] = {
                'signals': deque(maxlen=150),  # 5 seconds at 30 FPS
                'timestamps': deque(maxlen=150)
            }
            
        self.signal_buffer[device_id]['signals'].append(signals)
        self.signal_buffer[device_id]['timestamps'].append(timestamp)
        
        # Perform inference if sufficient data available
        if len(self.signal_buffer[device_id]['signals']) >= 90:  # 3 seconds minimum
            self.perform_gsr_inference(device_id)
```

**Machine Learning Inference Engine:**
```python
class MLInferenceEngine:
    def __init__(self, model_path: str):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Initialize preprocessing pipeline
        self.preprocessor = SignalPreprocessor()
        
    def predict_gsr(self, signal_sequence: np.ndarray) -> Tuple[float, float]:
        """Predict GSR value from signal sequence"""
        # Preprocess signals
        processed_signals = self.preprocessor.preprocess(signal_sequence)
        
        # Prepare input tensor
        input_data = np.expand_dims(processed_signals, axis=0).astype(np.float32)
        
        # Perform inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        # Extract prediction and confidence
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        confidence = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        
        return float(prediction), float(confidence)
        
class SignalPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.filter_params = {
            'lowcut': 0.1,
            'highcut': 5.0,
            'fs': 30.0,
            'order': 4
        }
        
    def preprocess(self, signals: np.ndarray) -> np.ndarray:
        """Preprocess signal sequence for ML inference"""
        # Apply bandpass filter
        filtered_signals = self.apply_bandpass_filter(signals)
        
        # Normalize signals
        normalized_signals = self.scaler.fit_transform(
            filtered_signals.reshape(-1, filtered_signals.shape[-1])
        ).reshape(filtered_signals.shape)
        
        # Extract features
        features = self.extract_features(normalized_signals)
        
        return features
        
    def apply_bandpass_filter(self, signals: np.ndarray) -> np.ndarray:
        """Apply bandpass filter to remove noise"""
        from scipy.signal import butter, filtfilt
        
        nyquist = 0.5 * self.filter_params['fs']
        low = self.filter_params['lowcut'] / nyquist
        high = self.filter_params['highcut'] / nyquist
        
        b, a = butter(
            self.filter_params['order'], 
            [low, high], 
            btype='band'
        )
        
        return filtfilt(b, a, signals, axis=0)
```

**4.2.4 Data Visualization and User Interface**

**Main Window Implementation:**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GSR Prediction System - Control Center")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize UI components
        self.setup_ui()
        self.setup_status_bar()
        self.setup_menu_bar()
        
        # Initialize data visualization
        self.visualization_manager = VisualizationManager()
        
    def setup_ui(self):
        """Setup main user interface layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for device control
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
        # Right panel for data visualization
        visualization_panel = self.create_visualization_panel()
        main_layout.addWidget(visualization_panel, 3)
        
    def create_control_panel(self) -> QWidget:
        """Create device control and monitoring panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Device status section
        device_group = QGroupBox("Connected Devices")
        device_layout = QVBoxLayout(device_group)
        
        self.device_list = QListWidget()
        device_layout.addWidget(self.device_list)
        
        # Recording controls
        recording_group = QGroupBox("Recording Control")
        recording_layout = QVBoxLayout(recording_group)
        
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.calibrate_button = QPushButton("Calibrate System")
        
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.calibrate_button.clicked.connect(self.calibrate_system)
        
        recording_layout.addWidget(self.start_button)
        recording_layout.addWidget(self.stop_button)
        recording_layout.addWidget(self.calibrate_button)
        
        # Session configuration
        session_group = QGroupBox("Session Configuration")
        session_layout = QFormLayout(session_group)
        
        self.subject_id_edit = QLineEdit()
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(60, 3600)
        self.duration_spinbox.setValue(300)
        
        session_layout.addRow("Subject ID:", self.subject_id_edit)
        session_layout.addRow("Duration (s):", self.duration_spinbox)
        
        # Add all groups to panel
        layout.addWidget(device_group)
        layout.addWidget(recording_group)
        layout.addWidget(session_group)
        layout.addStretch()
        
        return panel
        
    def create_visualization_panel(self) -> QWidget:
        """Create data visualization panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tabbed interface for different visualizations
        tab_widget = QTabWidget()
        
        # Real-time data tab
        realtime_tab = RealTimeVisualizationWidget()
        tab_widget.addTab(realtime_tab, "Real-time Data")
        
        # Signal quality tab
        quality_tab = SignalQualityWidget()
        tab_widget.addTab(quality_tab, "Signal Quality")
        
        # Analysis results tab
        analysis_tab = AnalysisResultsWidget()
        tab_widget.addTab(analysis_tab, "Analysis Results")
        
        layout.addWidget(tab_widget)
        
        return panel
```

**Real-Time Visualization Widget:**
```python
class RealTimeVisualizationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_plots()
        self.data_buffer = {}
        
    def setup_plots(self):
        """Setup matplotlib plots for real-time visualization"""
        self.figure = plt.Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # Create subplots
        self.gsr_plot = self.figure.add_subplot(3, 1, 1)
        self.rgb_plot = self.figure.add_subplot(3, 1, 2)
        self.quality_plot = self.figure.add_subplot(3, 1, 3)
        
        # Setup plot properties
        self.gsr_plot.set_title("GSR Prediction")
        self.gsr_plot.set_ylabel("GSR (μS)")
        
        self.rgb_plot.set_title("RGB Signal")
        self.rgb_plot.set_ylabel("Signal Amplitude")
        
        self.quality_plot.set_title("Signal Quality")
        self.quality_plot.set_ylabel("Quality Score")
        self.quality_plot.set_xlabel("Time (s)")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)  # Update every 100ms
        
    def update_plots(self):
        """Update real-time plots with latest data"""
        if not self.data_buffer:
            return
            
        # Clear previous plots
        self.gsr_plot.clear()
        self.rgb_plot.clear()
        self.quality_plot.clear()
        
        for device_id, data in self.data_buffer.items():
            if 'timestamps' in data and len(data['timestamps']) > 0:
                timestamps = np.array(data['timestamps'])
                
                # Plot GSR predictions
                if 'gsr_predictions' in data:
                    self.gsr_plot.plot(
                        timestamps, 
                        data['gsr_predictions'], 
                        label=f"Device {device_id}",
                        linewidth=2
                    )
                    
                # Plot RGB signals
                if 'rgb_signals' in data:
                    rgb_signals = np.array(data['rgb_signals'])
                    self.rgb_plot.plot(
                        timestamps, 
                        rgb_signals[:, 1],  # Green channel
                        label=f"Device {device_id}",
                        alpha=0.7
                    )
                    
                # Plot quality scores
                if 'quality_scores' in data:
                    self.quality_plot.plot(
                        timestamps,
                        data['quality_scores'],
                        label=f"Device {device_id}",
                        marker='o',
                        markersize=3
                    )
        
        # Update plot properties
        self.gsr_plot.legend()
        self.gsr_plot.grid(True, alpha=0.3)
        
        self.rgb_plot.legend()
        self.rgb_plot.grid(True, alpha=0.3)
        
        self.quality_plot.legend()
        self.quality_plot.grid(True, alpha=0.3)
        self.quality_plot.axhline(y=0.7, color='r', linestyle='--', label='Quality Threshold')
        
        # Refresh canvas
        self.canvas.draw()
        
    def add_data_point(self, device_id: str, timestamp: float, data: dict):
        """Add new data point for visualization"""
        if device_id not in self.data_buffer:
            self.data_buffer[device_id] = {
                'timestamps': deque(maxlen=300),  # 30 seconds at 10Hz
                'gsr_predictions': deque(maxlen=300),
                'rgb_signals': deque(maxlen=300),
                'quality_scores': deque(maxlen=300)
            }
            
        buffer = self.data_buffer[device_id]
        buffer['timestamps'].append(timestamp)
        
        if 'gsr_prediction' in data:
            buffer['gsr_predictions'].append(data['gsr_prediction'])
        if 'rgb_signal' in data:
            buffer['rgb_signals'].append(data['rgb_signal'])
        if 'quality_score' in data:
            buffer['quality_scores'].append(data['quality_score'])
```

This completes the major sections of the System Architecture document. The document provides comprehensive coverage of the overall system architecture, mobile device architecture, and desktop application architecture with detailed implementation examples and design rationale. 

Would you like me to continue with additional sections like the Data Management Architecture, Security Architecture, or move on to create the next document in the series?
