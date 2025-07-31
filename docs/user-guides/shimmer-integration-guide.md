# Enhanced Shimmer3 GSR+ Integration Guide

## Overview

The enhanced Shimmer3 GSR+ integration provides comprehensive support for Shimmer Research sensors with advanced features including real-time streaming, sensor configuration, data quality monitoring, and multi-device management.

## Features

### ✅ Core Functionality
- **Multi-device Support**: Connect and manage multiple Shimmer3 GSR+ devices simultaneously
- **Real-time Streaming**: Live data streaming with ObjectCluster processing
- **Session Recording**: CSV file logging with synchronized timestamps
- **SD Card Logging**: On-device logging capabilities
- **Connection Management**: Bluetooth pairing with retry logic and error recovery

### ✅ Enhanced Configuration
- **Sensor Channel Selection**: Configure individual sensors (GSR, PPG, Accel, Gyro, Mag, ECG, EMG)
- **Sampling Rate Control**: Real-time sampling rate updates (1-1000 Hz)
- **GSR Range Settings**: Configure GSR sensitivity ranges (0-4)
- **Accelerometer Ranges**: Set accelerometer sensitivity (±2g, ±4g, ±8g, ±16g)
- **3-Axis Sensor Support**: Individual X, Y, Z axis data extraction

### ✅ Data Quality & Monitoring
- **Real-time Metrics**: Signal quality assessment and sampling rate monitoring
- **Battery Monitoring**: Real-time battery level tracking with percentage calculation
- **Connection Stability**: Track reconnection attempts and connection health
- **Data Validation**: Comprehensive sensor data validation and error detection

### ✅ Advanced Features
- **Clock Synchronization**: Real-time clock sync between devices and system
- **EXG Configuration**: ECG/EMG configuration for supported devices
- **Connection Types**: Support for both BLE and Classic Bluetooth
- **Error Recovery**: Automatic reconnection with configurable retry attempts

## API Usage

### Basic Device Connection

```kotlin
// Initialize the recorder
val shimmerRecorder = ShimmerRecorder(context, sessionManager, logger)
shimmerRecorder.initialize()

// Scan for available devices
val availableDevices = shimmerRecorder.scanAndPairDevices()

// Connect to specific device
val connected = shimmerRecorder.connectSingleDevice(
    macAddress = "00:06:66:66:96:86",
    deviceName = "Shimmer3-GSR+",
    connectionType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
)
```

### Sensor Configuration

```kotlin
// Configure enabled sensors
val enabledChannels = setOf(
    SensorChannel.GSR,
    SensorChannel.PPG,
    SensorChannel.ACCEL_X,
    SensorChannel.ACCEL_Y,
    SensorChannel.ACCEL_Z
)
shimmerRecorder.setEnabledChannels(deviceId, enabledChannels)

// Set sampling rate
shimmerRecorder.setSamplingRate(deviceId, 51.2) // 51.2 Hz

// Configure GSR range
shimmerRecorder.setGSRRange(deviceId, 2) // Range 2: 220kΩ to 680kΩ

// Set accelerometer range
shimmerRecorder.setAccelRange(deviceId, 4) // ±4g
```

### Real-time Data Streaming

```kotlin
// Start streaming
shimmerRecorder.startStreaming()

// Data is automatically processed via ObjectCluster callbacks
// and converted to SensorSample objects for file writing and network streaming

// Stop streaming
shimmerRecorder.stopStreaming()
```

### Data Quality Monitoring

```kotlin
// Get real-time data quality metrics
val metrics = shimmerRecorder.getDataQualityMetrics(deviceId)
metrics?.let { m ->
    println("Sampling Rate: ${m.averageSamplingRate} Hz")
    println("Signal Quality: ${m.signalQuality}")
    println("Battery Level: ${m.batteryLevel}%")
    println("Connection: ${m.connectionStability}")
}

// Get comprehensive device information
val deviceInfo = shimmerRecorder.getDeviceInformation(deviceId)
deviceInfo?.let { info ->
    println(info.getDisplaySummary())
}
```

### Session Recording

```kotlin
// Start recording session
val sessionId = "session_${System.currentTimeMillis()}"
shimmerRecorder.startRecording(sessionId)

// Data is automatically logged to CSV files:
// - shimmer_deviceName_sessionId.csv

// Stop recording
shimmerRecorder.stopRecording()
```

### SD Card Logging

```kotlin
// Start SD logging on connected devices
shimmerRecorder.startSDLogging()

// Stop SD logging
shimmerRecorder.stopSDLogging()

// Check logging status
val isLogging = shimmerRecorder.isAnyDeviceSDLogging()
```

## Integration with UI Components

### Using ShimmerController

```kotlin
class MainActivity : AppCompatActivity(), ShimmerController.ShimmerCallback {
    private lateinit var shimmerController: ShimmerController
    private lateinit var viewModel: MainViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        shimmerController = ShimmerController(shimmerManager)
        shimmerController.setCallback(this)
    }

    // Launch device selection
    private fun selectShimmerDevice() {
        shimmerController.launchShimmerDeviceDialog(this, deviceSelectionLauncher)
    }

    // Configure sensors
    private fun configureSensors() {
        val channels = setOf("GSR", "PPG", "ACCEL_X", "ACCEL_Y", "ACCEL_Z")
        shimmerController.configureSensorChannels(viewModel, channels)
    }

    // Update sampling rate
    private fun setSamplingRate() {
        shimmerController.setSamplingRate(viewModel, 128.0) // 128 Hz
    }

    // Callback implementations
    override fun onDeviceSelected(address: String, name: String) {
        shimmerController.connectToSelectedDevice(viewModel)
    }

    override fun onConnectionStatusChanged(connected: Boolean) {
        updateUIConnectionStatus(connected)
    }
}
```

### Using MainViewModel

```kotlin
// Connect to device
viewModel.connectShimmerDevice(
    macAddress = "00:06:66:66:96:86",
    deviceName = "Shimmer3-GSR+",
    connectionType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
) { success ->
    if (success) {
        // Connected successfully
        configureDevice()
    }
}

// Configure sensors
viewModel.configureShimmerSensors(
    deviceId = "deviceId",
    enabledChannels = setOf(SensorChannel.GSR, SensorChannel.PPG)
) { success ->
    // Configuration complete
}

// Get real-time metrics
viewModel.getShimmerDataQuality(deviceId) { metrics ->
    metrics?.let {
        updateDataQualityDisplay(it.getDisplaySummary())
    }
}
```

## Sensor Channels

### Available Channels

| Channel | Description | Unit | Bitmask |
|---------|-------------|------|---------|
| GSR | Galvanic Skin Response | µS | 0x04 |
| PPG | Photoplethysmography | - | 0x4000 |
| ACCEL_X/Y/Z | Accelerometer (3-axis) | g | 0x80 |
| GYRO_X/Y/Z | Gyroscope (3-axis) | °/s | 0x40 |
| MAG_X/Y/Z | Magnetometer (3-axis) | gauss | 0x20 |
| ECG | Electrocardiography | mV | 0x10 |
| EMG | Electromyography | mV | 0x08 |

### Configuration Ranges

#### GSR Range Settings
- **0**: 10kΩ to 56kΩ
- **1**: 56kΩ to 220kΩ
- **2**: 220kΩ to 680kΩ
- **3**: 680kΩ to 4.7MΩ
- **4**: Auto Range

#### Accelerometer Range Settings
- **2**: ±2g
- **4**: ±4g
- **8**: ±8g
- **16**: ±16g

#### Sampling Rate Range
- **Minimum**: 1 Hz
- **Maximum**: 1000 Hz
- **Recommended**: 51.2 Hz (default)

## Data Format

### CSV Export Format

```csv
Timestamp_ms,DeviceTime_ms,SystemTime_ms,SessionTime_ms,DeviceId,SequenceNumber,
GSR_Conductance_uS,PPG_A13,
Accel_X_g,Accel_Y_g,Accel_Z_g,
Gyro_X_dps,Gyro_Y_dps,Gyro_Z_dps,
Mag_X_gauss,Mag_Y_gauss,Mag_Z_gauss,
ECG_mV,EMG_mV,Battery_Percentage
```

### JSON Streaming Format

```json
{
    "deviceId": "4455",
    "deviceTimestamp": 1234567890,
    "systemTimestamp": 1234567890,
    "sessionTimestamp": 12345,
    "sequenceNumber": 1000,
    "batteryLevel": 85,
    "sensorData": {
        "GSR": 2.5,
        "PPG": 512.0,
        "ACCEL_X": 0.1,
        "ACCEL_Y": 0.2,
        "ACCEL_Z": 9.8
    }
}
```

## Error Handling

### Common Issues and Solutions

1. **Connection Failed**
   - Verify device is paired in Android Bluetooth settings
   - Check device is powered on and in range
   - Ensure correct Bluetooth permissions are granted

2. **No Data Received**
   - Verify sensors are properly configured
   - Check device is in streaming mode
   - Ensure proper ObjectCluster callback setup

3. **Poor Signal Quality**
   - Check sensor contact and placement
   - Verify GSR range settings are appropriate
   - Monitor battery level and connection stability

4. **Permission Denied**
   - Request Bluetooth permissions (BLUETOOTH_SCAN, BLUETOOTH_CONNECT)
   - Request location permissions for Bluetooth scanning
   - Handle permission requests in Activity

## Best Practices

1. **Connection Management**
   - Always check connection status before operations
   - Implement proper reconnection logic
   - Handle connection timeouts gracefully

2. **Data Quality**
   - Monitor signal quality metrics regularly
   - Validate sensor data ranges
   - Track battery levels and warn users

3. **Performance**
   - Use appropriate sampling rates for your application
   - Batch data processing for efficiency
   - Implement proper resource cleanup

4. **User Experience**
   - Provide clear status feedback
   - Show connection and data quality indicators
   - Implement user-friendly error messages

## Testing

### Unit Tests

Run the enhanced test suite:
```bash
./gradlew testDebugUnitTest --tests "ShimmerRecorderEnhancedTest"
```

### Integration Testing

For real device testing:
1. Pair Shimmer3 GSR+ device with Android device
2. Run instrumented tests with actual hardware
3. Verify all sensor channels and configurations
4. Test data quality and streaming performance

## Troubleshooting

### Debug Logging

Enable detailed logging for troubleshooting:
```kotlin
// Log level in Logger configuration
logger.setLogLevel(Logger.Level.DEBUG)

// Check logs for diagnostic information
adb logcat | grep "ShimmerRecorder\|ShimmerController"
```

### Common Log Messages

- `[DEBUG_LOG] Shimmer device discovery diagnostic` - Device scanning
- `[DEBUG_LOG] Converting ObjectCluster from device` - Data processing
- `[DEBUG_LOG] Extracted sensor values` - Sensor data extraction
- `[DEBUG_LOG] Applying sensor bitmask` - Configuration updates

## Version Compatibility

- **Shimmer SDK**: 3.2.3_beta
- **Android API**: 24+ (Android 7.0)
- **Bluetooth**: Classic and BLE support
- **Java**: 17+ compatibility

For the latest updates and API changes, refer to the official Shimmer Research documentation and SDK releases.