# Chapter 4: System Architecture and Design

## 1. Introduction to System Architecture

The contactless GSR prediction system represents a complex distributed architecture that integrates multiple hardware platforms, diverse sensor modalities, real-time processing capabilities, and advanced machine learning algorithms. The system architecture must address the challenges of multi-device coordination, real-time data processing, reliable communication, and scalable deployment while maintaining research-grade accuracy and clinical reliability.

This chapter presents a comprehensive analysis of the system architecture, focusing on the design decisions that enable effective integration of all system components. The architecture follows established patterns for distributed systems while incorporating novel approaches specific to multi-modal physiological monitoring applications.

### 1.1 Architectural Principles

**Modularity and Separation of Concerns:**
The system architecture employs strict modular design principles, separating distinct functional areas into independent components with well-defined interfaces. This approach enables independent development, testing, and maintenance of different system aspects while facilitating future enhancements and modifications.

**Distributed Processing:**
Processing capabilities are distributed across multiple devices and platforms, leveraging the computational strengths of each component. Mobile devices handle local data acquisition and preprocessing, while the desktop controller manages coordination, analysis, and storage. This distribution optimizes performance while maintaining system responsiveness.

**Fault Tolerance and Resilience:**
The architecture incorporates multiple levels of fault tolerance to ensure continued operation despite component failures. Redundant communication paths, automatic failover mechanisms, and graceful degradation strategies maintain system functionality under adverse conditions.

**Scalability and Extensibility:**
The system design anticipates future growth in device count, processing requirements, and functional capabilities. Scalable communication protocols, modular processing pipelines, and extensible data formats support system evolution without requiring architectural redesign.

**Security and Privacy:**
Privacy protection and data security are integrated into the architecture at all levels, from local data processing to network communication and storage. Multi-layered security approaches protect sensitive physiological data throughout the system lifecycle.

### 1.2 Architectural Context

**Research Environment Requirements:**
The system must operate effectively in diverse research environments, from controlled laboratory settings to naturalistic field studies. This requirement drives architectural decisions regarding portability, setup simplicity, and environmental robustness.

**Multi-Stakeholder Support:**
Different stakeholders interact with the system in various roles, requiring flexible interfaces and access controls. Researchers need comprehensive control and monitoring capabilities, while subjects require simple, non-intrusive interfaces that minimize experimental disruption.

**Regulatory and Ethical Compliance:**
The architecture must support compliance with research ethics requirements, data protection regulations, and potential medical device standards. This compliance is achieved through built-in privacy protection, audit capabilities, and validation frameworks.

## 2. Overall System Architecture

### 2.1 High-Level Architecture Overview

The contactless GSR prediction system employs a distributed architecture consisting of multiple interconnected subsystems, each optimized for specific functions within the overall system workflow.

**Core Architectural Components:**

**Mobile Data Acquisition Units (Android Devices):**
- Primary function: Real-time multi-modal data capture
- Secondary function: Local preprocessing and data buffering
- Hardware: Samsung Galaxy S22 smartphones with attached thermal cameras
- Communication: Wi-Fi networking for coordination and data transmission
- Local processing: Hand detection, ROI extraction, initial signal processing
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
