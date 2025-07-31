# Android Application Design and Implementation

## 1. Introduction to Android Application Design

The Android application serves as the primary data acquisition component of the contactless GSR prediction system, responsible for coordinating multiple sensors, processing real-time video streams, and maintaining reliable communication with the central control system. The application design prioritizes real-time performance, reliability, and power efficiency while providing a user-friendly interface for research subjects.

This document presents a comprehensive analysis of the Android application architecture, design patterns, implementation strategies, and optimization techniques employed to meet the demanding requirements of physiological research applications.

### 1.1 Design Philosophy and Principles

**Research-First Design:**
The application design prioritizes research requirements over consumer application conventions, emphasizing data quality, temporal precision, and experimental validity over traditional user experience metrics.

**Modular Architecture:**
The system employs a highly modular design that separates concerns between data acquisition, processing, communication, and user interface components, enabling independent development and testing of each subsystem.

**Performance Optimization:**
All design decisions are evaluated for their impact on real-time performance, with particular attention to camera processing, network communication, and power consumption optimization.

**Fault Tolerance:**
The application is designed to continue data collection despite transient failures, employing robust error recovery mechanisms and graceful degradation strategies.

**Scientific Validation:**
The design incorporates extensive logging, quality assessment, and validation capabilities to support scientific rigor and reproducibility in research applications.

### 1.2 Platform-Specific Considerations

**Android Ecosystem Integration:**
The application leverages Android's strengths in multi-threaded processing, background services, and hardware abstraction while working within the constraints of the mobile platform.

**Hardware Optimization:**
Design decisions account for the specific capabilities and limitations of target hardware, particularly the Samsung Galaxy S22 platform with attached thermal cameras.

**Power Management:**
Mobile device power constraints drive architectural decisions regarding processing distribution, background operation, and resource utilization optimization.

**Security and Privacy:**
Android's security model influences data handling, storage, and communication design to ensure participant privacy and data protection.

## 2. Application Architecture Overview

### 2.1 Architectural Pattern Selection

The Android application employs a Clean Architecture pattern enhanced with reactive programming principles to handle the complex requirements of real-time multi-modal data processing.

**Clean Architecture Benefits:**
- Clear separation of business logic from framework dependencies
- Enhanced testability through dependency inversion
- Improved maintainability and code organization
- Flexibility for future platform or technology changes

**Reactive Programming Integration:**
- RxJava/Kotlin Coroutines for asynchronous data streams
- Event-driven architecture for sensor coordination
- Backpressure handling for high-frequency data sources
- Composable data processing pipelines

### 2.2 Layer Architecture Definition

**Presentation Layer (UI):**
```kotlin
// Activities and Fragments
- MainActivity: Primary application interface
- CalibrationActivity: System calibration workflows
- RecordingActivity: Data collection interface
- SettingsActivity: Configuration management

// ViewModels
- MainViewModel: Main application state management
- RecordingViewModel: Recording session coordination
- CameraViewModel: Camera state and configuration
- SensorViewModel: Sensor data management

// Custom Views
- CameraPreviewView: Real-time camera preview with overlays
- SignalQualityIndicator: Visual signal quality feedback
- HandGuidanceOverlay: Subject positioning guidance
- StatusIndicatorPanel: System status visualization
```

**Domain Layer (Business Logic):**
```kotlin
// Use Cases
- StartRecordingUseCase: Recording session initiation
- ProcessVideoFrameUseCase: Real-time frame processing
- SynchronizeDataUseCase: Multi-modal data alignment
- AssessSignalQualityUseCase: Quality monitoring

// Repository Interfaces
- CameraRepository: Camera data access abstraction
- SensorRepository: Physiological sensor access
- NetworkRepository: Communication interface
- StorageRepository: Data persistence interface

// Domain Models
- RecordingSession: Session metadata and configuration
- VideoFrame: Frame data with metadata
- SensorReading: Physiological measurements
- HandLandmarks: Hand pose estimation results
```

**Data Layer (Infrastructure):**
```kotlin
// Data Sources
- Camera2DataSource: Camera hardware abstraction
- ThermalCameraDataSource: Thermal camera integration
- ShimmerSensorDataSource: GSR sensor communication
- NetworkDataSource: Remote communication

// Repositories Implementation
- CameraRepositoryImpl: Camera data management
- SensorRepositoryImpl: Sensor data coordination
- NetworkRepositoryImpl: Network protocol handling
- StorageRepositoryImpl: Local data persistence

// Database
- Room database for metadata and configuration
- File system management for media data
- Shared preferences for user settings
```

**Framework Layer:**
```kotlin
// Android Framework Integration
- Services: Background data collection
- BroadcastReceivers: System event handling
- ContentProviders: Data sharing interfaces
- Dependency Injection: Hilt/Dagger configuration
```

## 3. Core Component Design

### 3.1 Camera System Design

The camera system represents the most critical component of the Android application, responsible for high-quality video capture, real-time processing, and precise timing control.

**3.1.1 Camera Architecture**

```kotlin
interface CameraManager {
    suspend fun initializeCamera(config: CameraConfiguration): Result<Unit>
    suspend fun startPreview(): Result<Unit>
    suspend fun startRecording(outputPath: String): Result<Unit>
    suspend fun stopRecording(): Result<Unit>
    suspend fun captureStillImage(): Result<File>
    fun getCameraCharacteristics(): CameraCharacteristics
    fun getPreviewSurface(): Surface
}

class Camera2ManagerImpl @Inject constructor(
    private val context: Context,
    private val cameraSelector: CameraSelector,
    private val imageProcessor: ImageProcessor
) : CameraManager {
    
    private var cameraDevice: CameraDevice? = null
    private var captureSession: CameraCaptureSession? = null
    private var imageReader: ImageReader? = null
    private var mediaRecorder: MediaRecorder? = null
    
    override suspend fun initializeCamera(config: CameraConfiguration): Result<Unit> {
        return withContext(Dispatchers.Main) {
            try {
                val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                val cameraId = selectOptimalCamera(cameraManager)
                
                // Configure camera parameters
                val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                configureCamera(characteristics, config)
                
                // Open camera device
                val cameraDevice = openCameraDevice(cameraManager, cameraId)
                this@Camera2ManagerImpl.cameraDevice = cameraDevice
                
                Result.success(Unit)
            } catch (e: Exception) {
                Log.e(TAG, "Camera initialization failed", e)
                Result.failure(e)
            }
        }
    }
    
    private suspend fun openCameraDevice(
        cameraManager: CameraManager, 
        cameraId: String
    ): CameraDevice = suspendCoroutine { continuation ->
        
        val stateCallback = object : CameraDevice.StateCallback() {
            override fun onOpened(camera: CameraDevice) {
                continuation.resume(camera)
            }
            
            override fun onDisconnected(camera: CameraDevice) {
                camera.close()
                continuation.resumeWithException(
                    RuntimeException("Camera disconnected")
                )
            }
            
            override fun onError(camera: CameraDevice, error: Int) {
                camera.close()
                continuation.resumeWithException(
                    RuntimeException("Camera error: $error")
                )
            }
        }
        
        cameraManager.openCamera(cameraId, stateCallback, backgroundHandler)
    }
    
    override suspend fun startRecording(outputPath: String): Result<Unit> {
        return try {
            setupMediaRecorder(outputPath)
            createCaptureSession()
            startRecordingSession()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun setupMediaRecorder(outputPath: String) {
        mediaRecorder = MediaRecorder().apply {
            setVideoSource(MediaRecorder.VideoSource.SURFACE)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setVideoEncoder(MediaRecorder.VideoEncoder.H264)
            setVideoSize(1920, 1080)
            setVideoFrameRate(30)
            setVideoEncodingBitRate(10_000_000) // 10 Mbps for high quality
            setOutputFile(outputPath)
            prepare()
        }
    }
    
    private suspend fun createCaptureSession(): CameraCaptureSession = 
        suspendCoroutine { continuation ->
            
            val surfaces = mutableListOf<Surface>().apply {
                add(previewSurface)
                add(mediaRecorder!!.surface)
                imageReader?.surface?.let { add(it) }
            }
            
            val sessionCallback = object : CameraCaptureSession.StateCallback() {
                override fun onConfigured(session: CameraCaptureSession) {
                    captureSession = session
                    continuation.resume(session)
                }
                
                override fun onConfigureFailed(session: CameraCaptureSession) {
                    continuation.resumeWithException(
                        RuntimeException("Session configuration failed")
                    )
                }
            }
            
            cameraDevice!!.createCaptureSession(
                surfaces, 
                sessionCallback, 
                backgroundHandler
            )
        }
}
```

**3.1.2 Camera Configuration and Optimization**

```kotlin
data class CameraConfiguration(
    val resolution: Size = Size(1920, 1080),
    val frameRate: Int = 30,
    val exposureMode: ExposureMode = ExposureMode.AUTO,
    val focusMode: FocusMode = FocusMode.CONTINUOUS_VIDEO,
    val stabilization: Boolean = true,
    val hdr: Boolean = false
)

class CameraOptimizer @Inject constructor() {
    
    fun optimizeForPhysiologicalMonitoring(
        characteristics: CameraCharacteristics
    ): CameraConfiguration {
        
        // Select optimal resolution for processing vs. quality trade-off
        val optimalResolution = selectOptimalResolution(characteristics)
        
        // Configure for consistent lighting and minimal artifacts
        return CameraConfiguration(
            resolution = optimalResolution,
            frameRate = 30, // Consistent with processing pipeline
            exposureMode = ExposureMode.MANUAL, // Prevent auto-exposure artifacts
            focusMode = FocusMode.FIXED, // Consistent focus for ROI tracking
            stabilization = true, // Reduce motion artifacts
            hdr = false // Avoid processing delays
        )
    }
    
    private fun selectOptimalResolution(
        characteristics: CameraCharacteristics
    ): Size {
        val streamConfigMap = characteristics.get(
            CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP
        )
        
        val availableSizes = streamConfigMap?.getOutputSizes(MediaRecorder::class.java)
            ?: return Size(1920, 1080)
        
        // Prefer 1080p for balance of quality and processing speed
        return availableSizes.find { it.width == 1920 && it.height == 1080 }
            ?: availableSizes.maxByOrNull { it.width * it.height }
            ?: Size(1920, 1080)
    }
    
    fun calculateOptimalExposure(
        characteristics: CameraCharacteristics,
        currentLighting: LightingConditions
    ): ExposureSettings {
        
        val exposureRange = characteristics.get(
            CameraCharacteristics.CONTROL_AE_COMPENSATION_RANGE
        )
        
        val isoRange = characteristics.get(
            CameraCharacteristics.SENSOR_INFO_SENSITIVITY_RANGE
        )
        
        return when (currentLighting) {
            LightingConditions.LOW_LIGHT -> ExposureSettings(
                iso = isoRange?.upper?.coerceAtMost(800) ?: 400,
                exposureTime = 1_000_000 / 15, // 1/15 second
                compensation = exposureRange?.upper ?: 0
            )
            LightingConditions.NORMAL -> ExposureSettings(
                iso = 200,
                exposureTime = 1_000_000 / 30, // 1/30 second
                compensation = 0
            )
            LightingConditions.BRIGHT -> ExposureSettings(
                iso = isoRange?.lower ?: 100,
                exposureTime = 1_000_000 / 60, // 1/60 second
                compensation = exposureRange?.lower ?: 0
            )
        }
    }
}
```

### 3.2 Thermal Camera Integration

The thermal camera integration provides critical temperature information for GSR prediction, requiring careful coordination with the RGB camera system and specialized processing pipelines.

**3.2.1 Thermal Camera Architecture**

```kotlin
interface ThermalCameraManager {
    suspend fun initializeThermalCamera(): Result<Unit>
    suspend fun startThermalCapture(): Result<Unit>
    suspend fun stopThermalCapture(): Result<Unit>
    fun getThermalFrameFlow(): Flow<ThermalFrame>
    fun getCurrentTemperatureRange(): TemperatureRange
}

class TopdonThermalCameraManager @Inject constructor(
    private val context: Context,
    private val synchronizationManager: SynchronizationManager
) : ThermalCameraManager {
    
    private var usbManager: UsbManager? = null
    private var thermalDevice: UsbDevice? = null
    private var isCapturing = false
    private val thermalFrameSubject = PublishSubject.create<ThermalFrame>()
    
    override suspend fun initializeThermalCamera(): Result<Unit> {
        return withContext(Dispatchers.IO) {
            try {
                usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager
                
                // Find Topdon thermal camera device
                val deviceList = usbManager?.deviceList
                thermalDevice = deviceList?.values?.find { device ->
                    device.vendorId == TOPDON_VENDOR_ID && 
                    device.productId in TOPDON_PRODUCT_IDS
                }
                
                if (thermalDevice == null) {
                    return@withContext Result.failure(
                        RuntimeException("Topdon thermal camera not found")
                    )
                }
                
                // Request permission and initialize
                requestUsbPermission()
                initializeTopdonSDK()
                
                Result.success(Unit)
            } catch (e: Exception) {
                Log.e(TAG, "Thermal camera initialization failed", e)
                Result.failure(e)
            }
        }
    }
    
    private suspend fun initializeTopdonSDK() {
        // Initialize Topdon SDK with device-specific parameters
        val config = TopdonConfiguration(
            device = thermalDevice!!,
            resolution = ThermalResolution.RESOLUTION_256x192,
            frameRate = 25,
            temperatureRange = TemperatureRange(-20f, 100f),
            emissivity = 0.95f
        )
        
        TopdonSDK.initialize(config) { frame ->
            // Process thermal frame on background thread
            GlobalScope.launch(Dispatchers.IO) {
                val processedFrame = processThermalFrame(frame)
                thermalFrameSubject.onNext(processedFrame)
            }
        }
    }
    
    private fun processThermalFrame(rawFrame: TopdonFrame): ThermalFrame {
        val timestamp = synchronizationManager.getCurrentTimestamp()
        
        // Convert raw thermal data to temperature matrix
        val temperatureMatrix = convertToTemperature(rawFrame.data)
        
        // Apply calibration corrections
        val calibratedMatrix = applyThermalCalibration(temperatureMatrix)
        
        // Extract metadata
        val metadata = ThermalFrameMetadata(
            timestamp = timestamp,
            ambientTemperature = rawFrame.ambientTemp,
            emissivity = rawFrame.emissivity,
            minTemp = calibratedMatrix.min() ?: 0f,
            maxTemp = calibratedMatrix.max() ?: 0f
        )
        
        return ThermalFrame(
            data = calibratedMatrix,
            metadata = metadata,
            width = rawFrame.width,
            height = rawFrame.height
        )
    }
    
    private fun convertToTemperature(rawData: ByteArray): Array<FloatArray> {
        val width = 256
        val height = 192
        val temperatureMatrix = Array(height) { FloatArray(width) }
        
        for (y in 0 until height) {
            for (x in 0 until width) {
                val index = (y * width + x) * 2
                val rawValue = (rawData[index + 1].toInt() shl 8) or 
                              (rawData[index].toInt() and 0xFF)
                
                // Convert raw 14-bit value to temperature using device calibration
                temperatureMatrix[y][x] = rawValueToTemperature(rawValue)
            }
        }
        
        return temperatureMatrix
    }
    
    override fun getThermalFrameFlow(): Flow<ThermalFrame> {
        return thermalFrameSubject.asFlow()
            .onBackpressureBuffer(50) // Buffer up to 2 seconds at 25 FPS
            .observeOn(Schedulers.computation())
    }
}
```

**3.2.2 RGB-Thermal Synchronization**

```kotlin
class RGBThermalSynchronizer @Inject constructor(
    private val timeProvider: TimeProvider
) {
    
    private val rgbFrameBuffer = CircularBuffer<TimestampedRGBFrame>(capacity = 100)
    private val thermalFrameBuffer = CircularBuffer<ThermalFrame>(capacity = 100)
    
    data class SynchronizedFrame(
        val rgbFrame: TimestampedRGBFrame,
        val thermalFrame: ThermalFrame,
        val synchronizationQuality: Float,
        val timeDifference: Long
    )
    
    fun synchronizeFrames(
        rgbFrame: TimestampedRGBFrame,
        thermalFrame: ThermalFrame
    ): SynchronizedFrame? {
        
        // Add frames to buffers
        rgbFrameBuffer.add(rgbFrame)
        thermalFrameBuffer.add(thermalFrame)
        
        // Find best temporal match
        val bestMatch = findBestTemporalMatch(rgbFrame, thermalFrame)
        
        return bestMatch?.let { (matchedRGB, matchedThermal, timeDiff) ->
            val quality = calculateSynchronizationQuality(timeDiff)
            
            SynchronizedFrame(
                rgbFrame = matchedRGB,
                thermalFrame = matchedThermal,
                synchronizationQuality = quality,
                timeDifference = timeDiff
            )
        }
    }
    
    private fun findBestTemporalMatch(
        targetRGBFrame: TimestampedRGBFrame,
        targetThermalFrame: ThermalFrame
    ): Triple<TimestampedRGBFrame, ThermalFrame, Long>? {
        
        val targetTimestamp = targetRGBFrame.timestamp
        var bestMatch: Triple<TimestampedRGBFrame, ThermalFrame, Long>? = null
        var minTimeDifference = Long.MAX_VALUE
        
        // Search for closest thermal frame to RGB timestamp
        for (i in 0 until thermalFrameBuffer.size) {
            val thermalFrame = thermalFrameBuffer.get(i) ?: continue
            val timeDifference = abs(thermalFrame.metadata.timestamp - targetTimestamp)
            
            if (timeDifference < minTimeDifference) {
                minTimeDifference = timeDifference
                bestMatch = Triple(targetRGBFrame, thermalFrame, timeDifference)
            }
        }
        
        // Only return if synchronization is within acceptable tolerance
        return if (minTimeDifference <= MAX_SYNC_TOLERANCE_MS) bestMatch else null
    }
    
    private fun calculateSynchronizationQuality(timeDifference: Long): Float {
        // Quality decreases linearly from 1.0 at perfect sync to 0.0 at max tolerance
        return 1.0f - (timeDifference.toFloat() / MAX_SYNC_TOLERANCE_MS)
    }
    
    companion object {
        private const val MAX_SYNC_TOLERANCE_MS = 50L // 50ms maximum acceptable difference
    }
}
```

### 3.3 Sensor Integration System

The sensor integration system manages communication with physiological sensors, particularly the Shimmer3 GSR+ devices, providing high-resolution ground truth data for validation and calibration.

**3.3.1 GSR Sensor Management**

```kotlin
interface GSRSensorManager {
    suspend fun discoverSensors(): Result<List<GSRSensor>>
    suspend fun connectToSensor(sensorId: String): Result<Unit>
    suspend fun startDataCollection(config: GSRConfiguration): Result<Unit>
    suspend fun stopDataCollection(): Result<Unit>
    fun getGSRDataFlow(): Flow<GSRReading>
    fun getCurrentConnectionStatus(): ConnectionStatus
}

class ShimmerGSRManager @Inject constructor(
    private val bluetoothManager: BluetoothManager,
    private val dataProcessor: GSRDataProcessor
) : GSRSensorManager {
    
    private var shimmerDevice: Shimmer? = null
    private var isConnected = false
    private var isCollecting = false
    private val gsrDataSubject = PublishSubject.create<GSRReading>()
    
    override suspend fun discoverSensors(): Result<List<GSRSensor>> {
        return withContext(Dispatchers.IO) {
            try {
                val bluetoothAdapter = bluetoothManager.adapter
                if (!bluetoothAdapter.isEnabled) {
                    return@withContext Result.failure(
                        RuntimeException("Bluetooth not enabled")
                    )
                }
                
                val pairedDevices = bluetoothAdapter.bondedDevices
                val shimmerDevices = pairedDevices.filter { device ->
                    device.name?.contains("Shimmer", ignoreCase = true) == true
                }.map { device ->
                    GSRSensor(
                        id = device.address,
                        name = device.name ?: "Unknown Shimmer",
                        address = device.address,
                        type = SensorType.SHIMMER_GSR_PLUS
                    )
                }
                
                Result.success(shimmerDevices)
            } catch (e: Exception) {
                Log.e(TAG, "Sensor discovery failed", e)
                Result.failure(e)
            }
        }
    }
    
    override suspend fun connectToSensor(sensorId: String): Result<Unit> {
        return withContext(Dispatchers.IO) {
            try {
                shimmerDevice = Shimmer(sensorId).apply {
                    setDataProcessingCallback { data ->
                        processShimmerData(data)
                    }
                    
                    setConnectionCallback { status ->
                        isConnected = (status == ConnectionStatus.CONNECTED)
                    }
                }
                
                shimmerDevice?.connect()
                
                // Wait for connection with timeout
                var waitTime = 0
                while (!isConnected && waitTime < CONNECTION_TIMEOUT_MS) {
                    delay(100)
                    waitTime += 100
                }
                
                if (isConnected) {
                    configureShimmerSensor()
                    Result.success(Unit)
                } else {
                    Result.failure(RuntimeException("Connection timeout"))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Sensor connection failed", e)
                Result.failure(e)
            }
        }
    }
    
    private fun configureShimmerSensor() {
        shimmerDevice?.apply {
            // Enable GSR sensor
            enableSensor(Shimmer.SENSOR_GSR)
            
            // Configure sampling rate
            setSamplingRate(SAMPLING_RATE_256_HZ)
            
            // Set GSR range for optimal resolution
            setGSRRange(GSR_RANGE_AUTO)
            
            // Enable real-time data streaming
            setStreamingMode(true)
        }
    }
    
    private fun processShimmerData(data: ShimmerData) {
        GlobalScope.launch(Dispatchers.Default) {
            try {
                val gsrReading = GSRReading(
                    timestamp = System.currentTimeMillis(),
                    gsrValue = data.getGSRValue(),
                    gsrResistance = data.getGSRResistance(),
                    skinConductance = data.getSkinConductance(),
                    quality = assessSignalQuality(data),
                    metadata = GSRMetadata(
                        sensorId = shimmerDevice?.bluetoothAddress ?: "",
                        samplingRate = shimmerDevice?.getSamplingRate() ?: 0,
                        gsrRange = shimmerDevice?.getGSRRange() ?: 0
                    )
                )
                
                gsrDataSubject.onNext(gsrReading)
            } catch (e: Exception) {
                Log.e(TAG, "Error processing GSR data", e)
            }
        }
    }
    
    private fun assessSignalQuality(data: ShimmerData): Float {
        // Implement signal quality assessment based on:
        // - Signal amplitude stability
        // - Noise level analysis
        // - Electrode contact quality
        // - Movement artifact detection
        
        val signalAmplitude = data.getGSRValue()
        val signalStability = calculateSignalStability(data)
        val noiseLevel = calculateNoiseLevel(data)
        
        return when {
            signalAmplitude < MIN_SIGNAL_THRESHOLD -> 0.2f
            noiseLevel > MAX_NOISE_THRESHOLD -> 0.3f
            signalStability < MIN_STABILITY_THRESHOLD -> 0.5f
            else -> 1.0f - noiseLevel / MAX_NOISE_THRESHOLD
        }
    }
    
    override fun getGSRDataFlow(): Flow<GSRReading> {
        return gsrDataSubject.asFlow()
            .onBackpressureBuffer(1000) // Buffer 4 seconds at 256 Hz
            .observeOn(Schedulers.computation())
    }
}
```

### 3.4 Real-Time Processing Pipeline

The real-time processing pipeline handles the complex task of coordinating multi-modal data streams, extracting physiological signals, and performing machine learning inference with minimal latency.

**3.4.1 Processing Pipeline Architecture**

```kotlin
class RealTimeProcessingPipeline @Inject constructor(
    private val handDetector: HandLandmarkDetector,
    private val signalExtractor: MultiModalSignalExtractor,
    private val qualityAssessor: SignalQualityAssessor,
    private val mlInferenceEngine: MLInferenceEngine,
    private val synchronizer: DataSynchronizer
) {
    
    private val processingScope = CoroutineScope(
        Dispatchers.Default + SupervisorJob()
    )
    
    data class ProcessingInput(
        val rgbFrame: TimestampedRGBFrame,
        val thermalFrame: ThermalFrame?,
        val gsrReading: GSRReading?,
        val timestamp: Long
    )
    
    data class ProcessingOutput(
        val gsrPrediction: Float,
        val confidence: Float,
        val signalQuality: Float,
        val handLandmarks: List<Landmark>?,
        val roiSignals: MultiModalSignals,
        val processingLatency: Long
    )
    
    fun processData(input: ProcessingInput): Flow<ProcessingOutput> = flow {
        val startTime = System.currentTimeMillis()
        
        try {
            // Step 1: Hand detection and landmark extraction
            val handLandmarks = detectHandLandmarks(input.rgbFrame)
            
            if (handLandmarks != null) {
                // Step 2: Multi-modal signal extraction
                val roiSignals = extractROISignals(
                    rgbFrame = input.rgbFrame,
                    thermalFrame = input.thermalFrame,
                    landmarks = handLandmarks
                )
                
                // Step 3: Signal quality assessment
                val signalQuality = assessSignalQuality(roiSignals, input.gsrReading)
                
                // Step 4: ML inference for GSR prediction
                val (prediction, confidence) = if (signalQuality > QUALITY_THRESHOLD) {
                    performGSRInference(roiSignals)
                } else {
                    Pair(0f, 0f) // No prediction for poor quality signals
                }
                
                val processingLatency = System.currentTimeMillis() - startTime
                
                emit(ProcessingOutput(
                    gsrPrediction = prediction,
                    confidence = confidence,
                    signalQuality = signalQuality,
                    handLandmarks = handLandmarks,
                    roiSignals = roiSignals,
                    processingLatency = processingLatency
                ))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Processing pipeline error", e)
            // Emit error state or default values
        }
    }.flowOn(Dispatchers.Default)
    
    private suspend fun detectHandLandmarks(
        rgbFrame: TimestampedRGBFrame
    ): List<Landmark>? = withContext(Dispatchers.Default) {
        
        val bitmap = BitmapFactory.decodeByteArray(
            rgbFrame.data, 0, rgbFrame.data.size
        )
        
        val results = handDetector.detectHands(bitmap)
        
        return@withContext if (results.isNotEmpty()) {
            results.first().landmarks
        } else {
            null
        }
    }
    
    private suspend fun extractROISignals(
        rgbFrame: TimestampedRGBFrame,
        thermalFrame: ThermalFrame?,
        landmarks: List<Landmark>
    ): MultiModalSignals = withContext(Dispatchers.Default) {
        
        // Define ROIs based on landmarks
        val rois = listOf(
            ROI.fromLandmark(landmarks[5], size = 20),   // Index finger base
            ROI.fromLandmark(landmarks[13], size = 20),  // Ring finger base
            ROI.fromLandmark(calculatePalmCenter(landmarks), size = 30) // Palm center
        )
        
        // Extract RGB signals
        val rgbSignals = signalExtractor.extractRGBSignals(rgbFrame, rois)
        
        // Extract thermal signals if available
        val thermalSignals = thermalFrame?.let { frame ->
            signalExtractor.extractThermalSignals(frame, rois)
        }
        
        return@withContext MultiModalSignals(
            rgbSignals = rgbSignals,
            thermalSignals = thermalSignals,
            rois = rois,
            timestamp = rgbFrame.timestamp
        )
    }
    
    private suspend fun performGSRInference(
        signals: MultiModalSignals
    ): Pair<Float, Float> = withContext(Dispatchers.Default) {
        
        // Prepare feature vector for ML model
        val features = prepareFeatureVector(signals)
        
        // Perform inference
        return@withContext mlInferenceEngine.predict(features)
    }
    
    private fun prepareFeatureVector(signals: MultiModalSignals): FloatArray {
        val features = mutableListOf<Float>()
        
        // Add RGB signal features
        signals.rgbSignals.forEach { roiSignal ->
            features.addAll(roiSignal.meanRGB.toList())
            features.add(roiSignal.greenChannelVariance)
            features.add(roiSignal.chrominanceSignal)
        }
        
        // Add thermal signal features if available
        signals.thermalSignals?.forEach { thermalSignal ->
            features.add(thermalSignal.meanTemperature)
            features.add(thermalSignal.temperatureVariance)
            features.add(thermalSignal.maxTemperature)
            features.add(thermalSignal.minTemperature)
        }
        
        return features.toFloatArray()
    }
}
```

**3.4.2 Machine Learning Inference Engine**

```kotlin
class MLInferenceEngine @Inject constructor(
    private val context: Context,
    private val modelManager: ModelManager
) {
    
    private var interpreter: Interpreter? = null
    private var inputTensor: ByteBuffer? = null
    private var outputTensor: Array<FloatArray>? = null
    
    suspend fun initialize(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            // Load TensorFlow Lite model
            val modelBuffer = modelManager.loadModel("gsr_prediction.tflite")
            
            // Configure interpreter options
            val options = Interpreter.Options().apply {
                setNumThreads(4) // Use multiple CPU cores
                setUseNNAPI(true) // Enable hardware acceleration if available
            }
            
            interpreter = Interpreter(modelBuffer, options)
            
            // Allocate input and output tensors
            val inputShape = interpreter!!.getInputTensor(0).shape()
            val outputShape = interpreter!!.getOutputTensor(0).shape()
            
            inputTensor = ByteBuffer.allocateDirect(4 * inputShape.reduce { acc, i -> acc * i })
                .order(ByteOrder.nativeOrder())
            
            outputTensor = Array(outputShape[0]) { FloatArray(outputShape[1]) }
            
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "ML engine initialization failed", e)
            Result.failure(e)
        }
    }
    
    suspend fun predict(features: FloatArray): Pair<Float, Float> = withContext(Dispatchers.Default) {
        try {
            // Prepare input tensor
            inputTensor!!.rewind()
            features.forEach { inputTensor!!.putFloat(it) }
            
            // Run inference
            interpreter!!.run(inputTensor, outputTensor)
            
            // Extract prediction and confidence
            val prediction = outputTensor!![0][0]
            val confidence = outputTensor!![0][1]
            
            Pair(prediction, confidence)
        } catch (e: Exception) {
            Log.e(TAG, "ML inference failed", e)
            Pair(0f, 0f)
        }
    }
    
    fun getModelInfo(): ModelInfo {
        return ModelInfo(
            inputShape = interpreter?.getInputTensor(0)?.shape(),
            outputShape = interpreter?.getOutputTensor(0)?.shape(),
            modelSize = modelManager.getModelSize(),
            version = modelManager.getModelVersion()
        )
    }
}
```

## 4. User Interface Design

### 4.1 Research-Oriented UI Design

The user interface design prioritizes research requirements over conventional mobile app design patterns, emphasizing data quality feedback, system status monitoring, and minimal experimental interference.

**4.1.1 Main Activity Design**

```kotlin
class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)
        
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        binding.viewModel = viewModel
        binding.lifecycleOwner = this
        
        setupUI()
        observeViewModelData()
    }
    
    private fun setupUI() {
        // Setup camera preview
        binding.cameraPreview.surfaceProvider = 
            PreviewView.SurfaceProvider { surface ->
                viewModel.setCameraPreviewSurface(surface)
            }
        
        // Setup hand guidance overlay
        binding.handGuidanceOverlay.setGuidanceCallback { isPositionOptimal ->
            viewModel.updateHandPositioning(isPositionOptimal)
        }
        
        // Setup signal quality indicators
        binding.signalQualityPanel.setQualityThresholds(
            excellent = 0.9f,
            good = 0.7f,
            poor = 0.5f
        )
        
        // Setup recording controls
        binding.recordingControls.setRecordingCallback(object : RecordingCallback {
            override fun onStartRecording() = viewModel.startRecording()
            override fun onStopRecording() = viewModel.stopRecording()
            override fun onPauseRecording() = viewModel.pauseRecording()
        })
    }
    
    private fun observeViewModelData() {
        // Observe system status
        viewModel.systemStatus.observe(this) { status ->
            updateSystemStatusDisplay(status)
        }
        
        // Observe signal quality
        viewModel.signalQuality.observe(this) { quality ->
            binding.signalQualityPanel.updateQuality(quality)
        }
        
        // Observe hand landmarks
        viewModel.handLandmarks.observe(this) { landmarks ->
            binding.handGuidanceOverlay.updateLandmarks(landmarks)
        }
        
        // Observe recording state
        viewModel.recordingState.observe(this) { state ->
            updateRecordingUI(state)
        }
        
        // Observe errors and alerts
        viewModel.errorEvents.observe(this) { error ->
            showErrorDialog(error)
        }
    }
    
    private fun updateSystemStatusDisplay(status: SystemStatus) {
        binding.systemStatusPanel.apply {
            setCameraStatus(status.cameraStatus)
            setThermalCameraStatus(status.thermalStatus)
            setGSRSensorStatus(status.gsrSensorStatus)
            setNetworkStatus(status.networkStatus)
            setBatteryLevel(status.batteryLevel)
        }
    }
}
```

**4.1.2 Custom View Components**

```kotlin
class HandGuidanceOverlay @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {
    
    private var landmarks: List<Landmark>? = null
    private var guidanceState = GuidanceState.NO_HAND_DETECTED
    private var guidanceCallback: ((Boolean) -> Unit)? = null
    
    private val landmarkPaint = Paint().apply {
        color = Color.GREEN
        style = Paint.Style.FILL
        strokeWidth = 4f
    }
    
    private val guidancePaint = Paint().apply {
        style = Paint.Style.STROKE
        strokeWidth = 6f
    }
    
    private val textPaint = Paint().apply {
        color = Color.WHITE
        textSize = 48f
        typeface = Typeface.DEFAULT_BOLD
    }
    
    enum class GuidanceState {
        NO_HAND_DETECTED,
        HAND_TOO_FAR,
        HAND_TOO_CLOSE,
        HAND_OFF_CENTER,
        HAND_OPTIMAL
    }
    
    fun updateLandmarks(newLandmarks: List<Landmark>?) {
        landmarks = newLandmarks
        updateGuidanceState()
        invalidate()
    }
    
    private fun updateGuidanceState() {
        val currentLandmarks = landmarks
        guidanceState = if (currentLandmarks == null) {
            GuidanceState.NO_HAND_DETECTED
        } else {
            assessHandPositioning(currentLandmarks)
        }
        
        guidanceCallback?.invoke(guidanceState == GuidanceState.HAND_OPTIMAL)
    }
    
    private fun assessHandPositioning(landmarks: List<Landmark>): GuidanceState {
        val palmCenter = calculatePalmCenter(landmarks)
        val handBounds = calculateHandBounds(landmarks)
        
        // Check if hand is centered in frame
        val centerX = width / 2f
        val centerY = height / 2f
        val distanceFromCenter = sqrt(
            (palmCenter.x - centerX).pow(2) + (palmCenter.y - centerY).pow(2)
        )
        
        return when {
            distanceFromCenter > width * 0.3f -> GuidanceState.HAND_OFF_CENTER
            handBounds.width() < width * 0.2f -> GuidanceState.HAND_TOO_FAR
            handBounds.width() > width * 0.8f -> GuidanceState.HAND_TOO_CLOSE
            else -> GuidanceState.HAND_OPTIMAL
        }
    }
    
    override fun onDraw(canvas: Canvas?) {
        super.onDraw(canvas)
        canvas ?: return
        
        // Draw hand landmarks if available
        landmarks?.forEach { landmark ->
            canvas.drawCircle(
                landmark.x * width,
                landmark.y * height,
                8f,
                landmarkPaint
            )
        }
        
        // Draw guidance elements
        drawGuidanceElements(canvas)
        
        // Draw guidance text
        drawGuidanceText(canvas)
    }
    
    private fun drawGuidanceElements(canvas: Canvas) {
        when (guidanceState) {
            GuidanceState.HAND_OPTIMAL -> {
                guidancePaint.color = Color.GREEN
                canvas.drawRect(
                    width * 0.2f, height * 0.2f,
                    width * 0.8f, height * 0.8f,
                    guidancePaint
                )
            }
            GuidanceState.HAND_OFF_CENTER -> {
                guidancePaint.color = Color.YELLOW
                canvas.drawCircle(
                    width / 2f, height / 2f,
                    width * 0.15f,
                    guidancePaint
                )
            }
            else -> {
                guidancePaint.color = Color.RED
                canvas.drawRect(
                    width * 0.25f, height * 0.25f,
                    width * 0.75f, height * 0.75f,
                    guidancePaint
                )
            }
        }
    }
    
    private fun drawGuidanceText(canvas: Canvas) {
        val message = when (guidanceState) {
            GuidanceState.NO_HAND_DETECTED -> "Please place your hand in view"
            GuidanceState.HAND_TOO_FAR -> "Move your hand closer"
            GuidanceState.HAND_TOO_CLOSE -> "Move your hand further away"
            GuidanceState.HAND_OFF_CENTER -> "Center your hand in the frame"
            GuidanceState.HAND_OPTIMAL -> "Perfect positioning!"
        }
        
        val textBounds = Rect()
        textPaint.getTextBounds(message, 0, message.length, textBounds)
        
        val x = (width - textBounds.width()) / 2f
        val y = height * 0.9f
        
        canvas.drawText(message, x, y, textPaint)
    }
}
```

## 5. Data Management and Storage

### 5.1 Local Data Architecture

```kotlin
@Database(
    entities = [
        RecordingSession::class,
        SensorData::class,
        CalibrationData::class,
        SystemConfiguration::class
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun recordingDao(): RecordingDao
    abstract fun sensorDao(): SensorDao
    abstract fun calibrationDao(): CalibrationDao
    abstract fun configDao(): ConfigurationDao
    
    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "gsr_prediction_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}

@Entity(tableName = "recording_sessions")
data class RecordingSession(
    @PrimaryKey val sessionId: String,
    val subjectId: String,
    val startTimestamp: Long,
    val endTimestamp: Long?,
    val status: SessionStatus,
    val configuration: SessionConfiguration,
    val dataQuality: Float,
    val notes: String?
)

@Dao
interface RecordingDao {
    @Query("SELECT * FROM recording_sessions ORDER BY startTimestamp DESC")
    suspend fun getAllSessions(): List<RecordingSession>
    
    @Query("SELECT * FROM recording_sessions WHERE sessionId = :sessionId")
    suspend fun getSession(sessionId: String): RecordingSession?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSession(session: RecordingSession)
    
    @Update
    suspend fun updateSession(session: RecordingSession)
    
    @Delete
    suspend fun deleteSession(session: RecordingSession)
}
```

### 5.2 File System Organization

```kotlin
class FileSystemManager @Inject constructor(
    private val context: Context
) {
    
    private val baseDirectory = File(context.getExternalFilesDir(null), "gsr_data")
    
    fun createSessionDirectory(sessionId: String): File {
        val sessionDir = File(baseDirectory, sessionId)
        sessionDir.mkdirs()
        
        // Create subdirectories
        File(sessionDir, "video").mkdirs()
        File(sessionDir, "thermal").mkdirs()
        File(sessionDir, "gsr").mkdirs()
        File(sessionDir, "processed").mkdirs()
        File(sessionDir, "metadata").mkdirs()
        
        return sessionDir
    }
    
    fun getVideoFile(sessionId: String, timestamp: Long): File {
        val sessionDir = File(baseDirectory, sessionId)
        return File(sessionDir, "video/video_${timestamp}.mp4")
    }
    
    fun getThermalDataFile(sessionId: String, timestamp: Long): File {
        val sessionDir = File(baseDirectory, sessionId)
        return File(sessionDir, "thermal/thermal_${timestamp}.bin")
    }
    
    fun getGSRDataFile(sessionId: String): File {
        val sessionDir = File(baseDirectory, sessionId)
        return File(sessionDir, "gsr/gsr_data.csv")
    }
    
    fun getProcessedDataFile(sessionId: String, dataType: String): File {
        val sessionDir = File(baseDirectory, sessionId)
        return File(sessionDir, "processed/${dataType}.csv")
    }
    
    fun getSessionMetadataFile(sessionId: String): File {
        val sessionDir = File(baseDirectory, sessionId)
        return File(sessionDir, "metadata/session_metadata.json")
    }
    
    fun calculateDirectorySize(directory: File): Long {
        return directory.walkTopDown()
            .filter { it.isFile }
            .map { it.length() }
            .sum()
    }
    
    fun cleanupOldSessions(retentionDays: Int) {
        val cutoffTime = System.currentTimeMillis() - (retentionDays * 24 * 60 * 60 * 1000L)
        
        baseDirectory.listFiles()?.forEach { sessionDir ->
            if (sessionDir.isDirectory && sessionDir.lastModified() < cutoffTime) {
                sessionDir.deleteRecursively()
            }
        }
    }
}
```

This concludes the Android Application Design document. The document provides comprehensive coverage of the Android application architecture, including core components like camera management, thermal camera integration, sensor systems, real-time processing pipelines, user interface design, and data management systems. Each section includes detailed implementation examples and design rationale to support the complex requirements of physiological research applications.

Would you like me to continue with the remaining documents (Python Application Design, Networking & Synchronization, etc.) or would you like me to proceed to the next chapter?