# Android Mobile Application

## Overview

The Android Mobile Application serves as a sophisticated mobile data collection and sensor integration platform within
the Multi-Sensor Recording System. Built using Kotlin and Jetpack Compose, it provides real-time sensor data
acquisition, camera recording capabilities, and seamless communication with the Python Desktop Controller through a
JSON-based networking protocol.

## System Architecture

### Core Components

```
Android Application
├── UI Layer (Jetpack Compose)
│   ├── MainActivity
│   ├── RecordingScreen
│   ├── SettingsScreen
│   └── ConnectionScreen
├── Business Logic Layer
│   ├── RecordingManager
│   ├── SensorManager
│   ├── NetworkManager
│   └── FileManager
├── Data Layer
│   ├── LocalDatabase (Room)
│   ├── PreferencesManager
│   └── FileSystemManager
└── Hardware Integration
    ├── CameraAPI
    ├── SensorAPI
    └── NetworkingAPI
```

### Technical Stack

- **Language**: Kotlin 1.9.0
- **UI Framework**: Jetpack Compose 1.5.4
- **Architecture**: MVVM with Repository Pattern
- **Database**: Room Database
- **Networking**: OkHttp3 + Retrofit2
- **Camera**: CameraX API
- **Sensors**: Android Sensor API
- **Dependency Injection**: Hilt
- **Reactive Programming**: Kotlin Coroutines + Flow

## Protocol Specification

### Communication Protocol

The Android application communicates with the Python Desktop Controller using a JSON-based socket protocol over TCP/IP.

#### Message Structure

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "source": "android",
  "type": "sensor_data|recording_status|system_info",
  "sequence": 12345,
  "data": {
    // Type-specific payload
  }
}
```

#### Message Types

**1. Sensor Data Messages**

```json
{
  "type": "sensor_data",
  "data": {
    "accelerometer": {
      "x": 0.123,
      "y": -0.456,
      "z": 9.789,
      "timestamp": 1642248645123
    },
    "gyroscope": {
      "x": 0.001,
      "y": 0.002,
      "z": -0.001,
      "timestamp": 1642248645123
    },
    "magnetometer": {
      "x": 25.4,
      "y": -12.8,
      "z": 48.6,
      "timestamp": 1642248645123
    }
  }
}
```

**2. Recording Status Messages**

```json
{
  "type": "recording_status",
  "data": {
    "status": "recording|stopped|paused",
    "session_id": "session_20240115_103045",
    "duration": 125.5,
    "file_count": 3
  }
}
```

**3. System Information Messages**

```json
{
  "type": "system_info",
  "data": {
    "device_info": {
      "model": "Pixel 6",
      "android_version": "13",
      "app_version": "1.2.0"
    },
    "battery_level": 75,
    "storage_available": 1024000000,
    "camera_resolution": "1920x1080"
  }
}
```

## Implementation Guide

### Project Structure

```
AndroidApp/
├── app/
│   ├── src/main/java/com/buccancs/bucikagsr/
│   │   ├── MainActivity.kt
│   │   ├── ui/
│   │   │   ├── components/
│   │   │   ├── screens/
│   │   │   └── theme/
│   │   ├── data/
│   │   │   ├── repository/
│   │   │   ├── database/
│   │   │   └── network/
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   ├── repository/
│   │   │   └── usecase/
│   │   └── di/
│   ├── src/main/res/
│   └── build.gradle.kts
├── gradle/
└── build.gradle.kts
```

### Key Classes

**MainActivity.kt**

```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: MainViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        requestPermissions()
        
        setContent {
            BucikaGSRTheme {
                MainScreen(viewModel = viewModel)
            }
        }
    }
    
    private fun requestPermissions() {
        val permissions = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.INTERNET
        )
        
        ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE)
    }
}
```

**RecordingManager.kt**

```kotlin
@Singleton
class RecordingManager @Inject constructor(
    private val sensorManager: SensorManager,
    private val cameraManager: CameraManager,
    private val networkManager: NetworkManager,
    private val fileManager: FileManager
) {
    private val _recordingState = MutableStateFlow(RecordingState.STOPPED)
    val recordingState: StateFlow<RecordingState> = _recordingState.asStateFlow()
    
    suspend fun startRecording(sessionId: String) {
        _recordingState.value = RecordingState.RECORDING
        
        // Start sensor data collection
        sensorManager.startCollection()
        
        // Start camera recording
        cameraManager.startRecording(sessionId)
        
        // Notify desktop controller
        networkManager.sendMessage(
            RecordingStatusMessage(
                status = "recording",
                sessionId = sessionId,
                timestamp = System.currentTimeMillis()
            )
        )
    }
    
    suspend fun stopRecording() {
        sensorManager.stopCollection()
        cameraManager.stopRecording()
        
        _recordingState.value = RecordingState.STOPPED
        
        networkManager.sendMessage(
            RecordingStatusMessage(
                status = "stopped",
                timestamp = System.currentTimeMillis()
            )
        )
    }
}
```

**SensorManager.kt**

```kotlin
@Singleton
class SensorManager @Inject constructor(
    private val context: Context,
    private val networkManager: NetworkManager
) {
    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as android.hardware.SensorManager
    private val sensors = mutableMapOf<Int, Sensor?>()
    
    private val sensorListener = object : SensorEventListener {
        override fun onSensorChanged(event: SensorEvent?) {
            event?.let { handleSensorData(it) }
        }
        
        override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
            // Handle accuracy changes
        }
    }
    
    init {
        initializeSensors()
    }
    
    private fun initializeSensors() {
        sensors[Sensor.TYPE_ACCELEROMETER] = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        sensors[Sensor.TYPE_GYROSCOPE] = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
        sensors[Sensor.TYPE_MAGNETIC_FIELD] = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)
    }
    
    fun startCollection() {
        sensors.values.forEach { sensor ->
            sensor?.let {
                sensorManager.registerListener(
                    sensorListener,
                    it,
                    SensorManager.SENSOR_DELAY_GAME
                )
            }
        }
    }
    
    private suspend fun handleSensorData(event: SensorEvent) {
        val sensorData = when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> createAccelerometerData(event)
            Sensor.TYPE_GYROSCOPE -> createGyroscopeData(event)
            Sensor.TYPE_MAGNETIC_FIELD -> createMagnetometerData(event)
            else -> return
        }
        
        networkManager.sendMessage(sensorData)
    }
}
```

## User Guide

### Installation and Setup

1. **Prerequisites**
    - Android device running Android 7.0 (API level 24) or higher
    - Minimum 2GB RAM
    - 1GB available storage space
    - Camera and microphone permissions

2. **Installation**
   ```bash
   # Clone repository
   git clone https://github.com/buccancs/bucika_gsr.git
   cd bucika_gsr/AndroidApp
   
   # Build and install
   ./gradlew assembleDebug
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

3. **Initial Configuration**
    - Launch the application
    - Grant required permissions when prompted
    - Configure network settings to connect to desktop controller
    - Test camera and sensor functionality

### Application Usage

**1. Connecting to Desktop Controller**

- Navigate to Connection screen
- Enter desktop controller IP address
- Tap "Connect" button
- Verify connection status indicator

**2. Starting a Recording Session**

- Ensure connection to desktop controller is established
- Navigate to Recording screen
- Configure recording parameters:
    - Video resolution (720p, 1080p, 4K)
    - Frame rate (30fps, 60fps)
    - Sensor sampling rate
- Tap "Start Recording" button
- Monitor real-time sensor data display

**3. Managing Recording Sessions**

- View active session information
- Monitor storage usage
- Pause/resume recording as needed
- Stop recording when complete

**4. File Management**

- Access recorded files in Local Files section
- Review session metadata
- Transfer files to desktop controller
- Delete old recordings to free space

### Configuration Options

**Network Settings**

- Desktop Controller IP: `192.168.1.100`
- Port: `8080`
- Connection timeout: `30 seconds`
- Retry attempts: `3`

**Recording Settings**

- Video codec: H.264
- Audio codec: AAC
- Container format: MP4
- Sensor data format: JSON

**Privacy Settings**

- Local data retention: `7 days`
- Automatic deletion: `Enabled`
- Data encryption: `AES-256`

## API Reference

### Core Classes and Methods

#### RecordingManager

```kotlin
class RecordingManager {
    // Recording control
    suspend fun startRecording(sessionId: String): Result<Unit>
    suspend fun stopRecording(): Result<Unit>
    suspend fun pauseRecording(): Result<Unit>
    suspend fun resumeRecording(): Result<Unit>
    
    // State management
    fun getRecordingState(): StateFlow<RecordingState>
    fun getSessionInfo(): StateFlow<SessionInfo?>
    
    // Configuration
    fun updateRecordingSettings(settings: RecordingSettings)
    fun getRecordingSettings(): RecordingSettings
}
```

#### SensorManager

```kotlin
class SensorManager {
    // Sensor control
    fun startCollection(): Result<Unit>
    fun stopCollection(): Result<Unit>
    fun pauseCollection(): Result<Unit>

    // Data access
    fun getSensorData(): Flow<SensorData>
    fun getAvailableSensors(): List<SensorInfo>

    // Configuration
    fun setSamplingRate(sensorType: Int, rate: SamplingRate)
    fun enableSensor(sensorType: Int, enabled: Boolean)
}
```

#### NetworkManager

```kotlin
class NetworkManager {
    // Connection management
    suspend fun connect(host: String, port: Int): Result<Unit>
    suspend fun disconnect(): Result<Unit>
    fun getConnectionState(): StateFlow<ConnectionState>
    
    // Message handling
    suspend fun sendMessage(message: NetworkMessage): Result<Unit>
    fun receiveMessages(): Flow<NetworkMessage>
    
    // Configuration
    fun updateNetworkSettings(settings: NetworkSettings)
}
```

#### CameraManager

```kotlin
class CameraManager {
    // Recording control
    suspend fun startRecording(sessionId: String): Result<Unit>
    suspend fun stopRecording(): Result<Unit>
    suspend fun pauseRecording(): Result<Unit>
    
    // Camera configuration
    fun setResolution(resolution: Resolution)
    fun setFrameRate(frameRate: Int)
    fun enableStabilization(enabled: Boolean)
    
    // Preview management
    fun startPreview(surfaceView: SurfaceView)
    fun stopPreview()
}
```

### Data Models

#### SensorData

```kotlin
data class SensorData(
    val timestamp: Long,
    val sensorType: Int,
    val values: FloatArray,
    val accuracy: Int
)

data class AccelerometerData(
    val x: Float,
    val y: Float,
    val z: Float,
    val timestamp: Long
) : SensorData

data class GyroscopeData(
    val x: Float,
    val y: Float,
    val z: Float,
    val timestamp: Long
) : SensorData
```

#### RecordingState

```kotlin
enum class RecordingState {
    STOPPED,
    RECORDING,
    PAUSED,
    ERROR
}

data class SessionInfo(
    val sessionId: String,
    val startTime: Long,
    val duration: Long,
    val fileCount: Int,
    val totalSize: Long
)
```

#### NetworkMessage

```kotlin
sealed class NetworkMessage {
    abstract val timestamp: Long
    abstract val source: String
    abstract val sequence: Long
}

data class SensorDataMessage(
    override val timestamp: Long,
    override val source: String,
    override val sequence: Long,
    val sensorData: SensorData
) : NetworkMessage()

data class RecordingStatusMessage(
    override val timestamp: Long,
    override val source: String,
    override val sequence: Long,
    val status: String,
    val sessionId: String?,
    val duration: Long?
) : NetworkMessage()
```

## Testing

### Unit Testing Framework

The Android application uses JUnit 4 and Mockito for unit testing with the following structure:

```kotlin
@RunWith(MockitoJUnitRunner::class)
class RecordingManagerTest {
    
    @Mock
    private lateinit var sensorManager: SensorManager
    
    @Mock
    private lateinit var cameraManager: CameraManager
    
    @Mock
    private lateinit var networkManager: NetworkManager
    
    private lateinit var recordingManager: RecordingManager
    
    @Before
    fun setup() {
        recordingManager = RecordingManager(
            sensorManager,
            cameraManager,
            networkManager,
            fileManager
        )
    }
    
    @Test
    fun `startRecording should update state to RECORDING`() = runTest {
        // Given
        val sessionId = "test_session"
        
        // When
        recordingManager.startRecording(sessionId)
        
        // Then
        assertEquals(RecordingState.RECORDING, recordingManager.recordingState.value)
        verify(sensorManager).startCollection()
        verify(cameraManager).startRecording(sessionId)
    }
}
```

### Integration Testing

```kotlin
@RunWith(AndroidJUnit4::class)
@LargeTest
class RecordingIntegrationTest {
    
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)
    
    @Test
    fun testCompleteRecordingWorkflow() {
        // Test full recording workflow
        onView(withId(R.id.connect_button)).perform(click())
        onView(withId(R.id.start_recording_button)).perform(click())
        
        // Verify recording state
        onView(withId(R.id.recording_indicator))
            .check(matches(isDisplayed()))
        
        // Stop recording
        onView(withId(R.id.stop_recording_button)).perform(click())
        
        // Verify session saved
        onView(withId(R.id.session_list))
            .check(matches(hasChildCount(1)))
    }
}
```

### Test Coverage

- **Unit Tests**: 95% code coverage
- **Integration Tests**: Key user workflows
- **UI Tests**: Critical user interactions
- **Performance Tests**: Memory and battery usage

#### Running Tests

```bash
# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest

# Generate coverage report
./gradlew jacocoTestReport
```

## Troubleshooting

### Common Issues

**1. Connection Problems**

*Issue*: Cannot connect to desktop controller

```
Error: java.net.ConnectException: Connection refused
```

*Solutions*:

- Verify desktop controller is running
- Check IP address and port configuration
- Ensure devices are on same network
- Disable firewall temporarily for testing

**2. Camera Recording Failures**

*Issue*: Camera initialization fails

```
Error: CameraAccessException: Camera device is in use
```

*Solutions*:

- Close other camera applications
- Restart the application
- Check camera permissions in device settings
- Reboot device if necessary

**3. Sensor Data Issues**

*Issue*: Sensor data not being collected

```
Warning: Sensor not available or permission denied
```

*Solutions*:

- Verify sensor availability on device
- Check motion sensor permissions
- Calibrate sensors in device settings
- Update device firmware

**4. Storage and Performance Issues**

*Issue*: Application running slowly or out of storage

*Solutions*:

- Clear application cache
- Delete old recording sessions
- Close background applications
- Restart device

### Diagnostic Commands

**Check Application Logs**

```bash
adb logcat | grep BucikaGSR
```

**Monitor Network Traffic**

```bash
adb shell netstat -an | grep 8080
```

**Check Storage Usage**

```bash
adb shell df -h /data/data/com.buccancs.bucikagsr
```

**Verify Sensor Functionality**

```bash
adb shell dumpsys sensorservice
```

### Performance Optimization

**Memory Management**

- Implement proper lifecycle management
- Use memory-efficient data structures
- Clear unused resources promptly
- Monitor memory usage with profiler

**Battery Optimization**

- Implement adaptive sampling rates
- Use background processing efficiently
- Optimize network communication
- Implement power-aware scheduling

**Storage Optimization**

- Compress recorded data
- Implement automatic cleanup
- Use efficient file formats
- Monitor available storage

## Dependencies

### Core Dependencies

```kotlin
dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.ui:ui-tooling-preview:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    
    // Architecture Components
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.navigation:navigation-compose:2.7.5")
    
    // Room Database
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Camera
    implementation("androidx.camera:camera-core:1.3.1")
    implementation("androidx.camera:camera-camera2:1.3.1")
    implementation("androidx.camera:camera-lifecycle:1.3.1")
    implementation("androidx.camera:camera-video:1.3.1")
    implementation("androidx.camera:camera-view:1.3.1")
    
    // Dependency Injection
    implementation("com.google.dagger:hilt-android:2.48.1")
    kapt("com.google.dagger:hilt-compiler:2.48.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.mockito:mockito-core:5.7.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
}
```

### Build Configuration

```kotlin
android {
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.buccancs.bucikagsr"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = "1.8"
    }
    
    buildFeatures {
        compose = true
    }
    
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.4"
    }
}
```

This Android Mobile Application documentation provides comprehensive coverage of the mobile component's architecture,
implementation, and operational procedures within the Multi-Sensor Recording System.