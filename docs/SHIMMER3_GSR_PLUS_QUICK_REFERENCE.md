# Shimmer3 GSR+ Quick Reference Guide

## Overview

This quick reference provides immediate access to essential information for Shimmer3 GSR+ integration. For comprehensive documentation, see [SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md).

## Quick Setup

### 1. Dependencies
```gradle
// Add to app/build.gradle
implementation 'com.shimmerresearch:shimmer_android_api:latest_version'
implementation 'androidx.hilt:hilt-android:2.44'
```

### 2. Permissions (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

### 3. Basic Integration
```kotlin
// Initialize Shimmer Manager
val shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(context)

// Connect to device
shimmerBluetoothManager.connectShimmerDevice("00:06:66:66:96:86")

// Configure sensors
val shimmer = shimmerBluetoothManager.getShimmerBtMap()["00:06:66:66:96:86"]
shimmer?.let {
    it.writeEnabledSensors(Configuration.Shimmer3.SENSOR_GSR)
    it.writeSamplingRate(51.2) // 51.2 Hz
    it.writeGSRRange(2) // Range 2: 220kΩ to 680kΩ
}

// Start streaming
shimmerBluetoothManager.startStreaming("00:06:66:66:96:86")
```

## Sensor Configuration

### GSR Range Settings
| Range | Resistance | Conductance | Use Case |
|-------|------------|-------------|----------|
| 0     | 10kΩ - 56kΩ | 18-100 µS | High arousal |
| 1     | 56kΩ - 220kΩ | 4.5-18 µS | Normal |
| 2     | 220kΩ - 680kΩ | 1.5-4.5 µS | Dry skin |
| 3     | 680kΩ - 4.7MΩ | 0.2-1.5 µS | Very dry |
| 4     | Auto Range | Dynamic | Adaptive |

### Sampling Rates
- **Low Power**: 1-10 Hz (battery optimization)
- **Standard**: 25-51.2 Hz (general use)
- **High Resolution**: 102.4-204.8 Hz (research)
- **Maximum**: Up to 1000 Hz (specialized applications)

### Enabled Sensors
```kotlin
// Common sensor combinations
val gsrOnly = Configuration.Shimmer3.SENSOR_GSR
val gsrWithPPG = Configuration.Shimmer3.SENSOR_GSR or Configuration.Shimmer3.SENSOR_PPG_A13
val fullSensorSet = Configuration.Shimmer3.SENSOR_GSR or 
                   Configuration.Shimmer3.SENSOR_PPG_A13 or 
                   Configuration.Shimmer3.SENSOR_LSM303DLHC_ACCEL
```

## Data Processing

### ObjectCluster Data Extraction
```kotlin
// Handle incoming data
shimmerBluetoothManager.setDataCallback { shimmerDevice, objectCluster ->
    // Extract GSR data
    val gsrConductance = objectCluster.getFormatClusterValue(
        Configuration.Shimmer3.ObjectClusterSensorName.GSR_CONDUCTANCE, 
        "CAL"
    )
    
    // Extract PPG data
    val ppgToHeartRate = objectCluster.getFormatClusterValue(
        Configuration.Shimmer3.ObjectClusterSensorName.PPG_TO_HR, 
        "CAL"
    )
    
    // Extract accelerometer data
    val accelX = objectCluster.getFormatClusterValue(
        Configuration.Shimmer3.ObjectClusterSensorName.LSM303DLHC_ACCEL_X, 
        "CAL"
    )
}
```

### Data Quality Metrics
```kotlin
fun assessDataQuality(samples: List<Double>): DataQuality {
    val snr = calculateSNR(samples)
    val artifactCount = detectArtifacts(samples)
    val continuity = assessContinuity(samples)
    
    return DataQuality(
        signalToNoiseRatio = snr,
        artifactLevel = artifactCount,
        continuityScore = continuity
    )
}
```

## Connection Management

### Device Discovery
```kotlin
// Start scanning
shimmerBluetoothManager.startDeviceDiscovery()

// Handle discovered devices
shimmerBluetoothManager.setDeviceDiscoveryCallback { device ->
    if (device.name?.contains("Shimmer") == true) {
        // Found Shimmer device
        val macAddress = device.address
        connectToDevice(macAddress)
    }
}
```

### Connection Status
```kotlin
// Check connection status
val isConnected = shimmerBluetoothManager.getShimmerState("00:06:66:66:96:86") == 
                  ShimmerBluetoothManagerAndroid.BT_STATE.CONNECTED

// Handle connection events
shimmerBluetoothManager.setConnectionCallback { deviceAddress, state ->
    when (state) {
        ShimmerBluetoothManagerAndroid.BT_STATE.CONNECTED -> {
            // Device connected successfully
            configureDevice(deviceAddress)
        }
        ShimmerBluetoothManagerAndroid.BT_STATE.CONNECTING -> {
            // Connection in progress
        }
        ShimmerBluetoothManagerAndroid.BT_STATE.NONE -> {
            // Device disconnected
            handleDisconnection(deviceAddress)
        }
    }
}
```

## Error Handling

### Common Issues
| Issue | Cause | Solution |
|-------|-------|----------|
| Connection timeout | Device out of range | Move closer, check battery |
| Poor signal quality | Bad electrode contact | Check skin prep, electrode gel |
| Data dropouts | Bluetooth interference | Reduce interference, check range |
| Battery drain | High sampling rate | Reduce rate or use power saving |

### Retry Logic
```kotlin
suspend fun connectWithRetry(
    macAddress: String, 
    maxRetries: Int = 3
): Boolean {
    repeat(maxRetries) { attempt ->
        try {
            shimmerBluetoothManager.connectShimmerDevice(macAddress)
            delay(2000) // Wait for connection
            
            if (isConnected(macAddress)) {
                return true
            }
        } catch (e: Exception) {
            logW("Connection attempt ${attempt + 1} failed: ${e.message}")
            delay(1000 * (attempt + 1)) // Exponential backoff
        }
    }
    return false
}
```

## File Integration

### Session-based Recording
```kotlin
// Start session recording
val sessionId = "session_${System.currentTimeMillis()}"
val shimmerDataFile = File(sessionDir, "shimmer_${deviceId}_data.csv")

// Write CSV header
shimmerDataFile.writeText("timestamp,gsr_conductance,ppg_hr,accel_x,accel_y,accel_z\n")

// Process and save data
shimmerBluetoothManager.setDataCallback { device, objectCluster ->
    val csvLine = buildString {
        append(objectCluster.systemTimeStamp)
        append(",${objectCluster.getFormatClusterValue("GSR Conductance", "CAL")}")
        append(",${objectCluster.getFormatClusterValue("PPG to Heart Rate", "CAL")}")
        append(",${objectCluster.getFormatClusterValue("Low Noise Accelerometer X", "CAL")}")
        append(",${objectCluster.getFormatClusterValue("Low Noise Accelerometer Y", "CAL")}")
        append(",${objectCluster.getFormatClusterValue("Low Noise Accelerometer Z", "CAL")}")
        append("\n")
    }
    shimmerDataFile.appendText(csvLine)
}
```

## Performance Tips

### Battery Optimization
```kotlin
// Reduce sampling rate when not actively recording
if (!isActivelyRecording) {
    shimmer.writeSamplingRate(1.0) // 1 Hz for minimal battery usage
}

// Use appropriate sensor combinations
val lowPowerConfig = Configuration.Shimmer3.SENSOR_GSR // GSR only
val standardConfig = Configuration.Shimmer3.SENSOR_GSR or 
                    Configuration.Shimmer3.SENSOR_PPG_A13 // GSR + PPG
```

### Memory Management
```kotlin
// Use circular buffer for real-time data
class CircularBuffer<T>(private val capacity: Int) {
    private val buffer = arrayOfNulls<Any>(capacity) as Array<T?>
    private var writeIndex = 0
    private var size = 0
    
    fun add(item: T) {
        buffer[writeIndex] = item
        writeIndex = (writeIndex + 1) % capacity
        if (size < capacity) size++
    }
    
    fun getLatest(count: Int): List<T> {
        // Return latest 'count' items
    }
}
```

## Resources

- **Full Documentation**: [SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md)
- **Official API**: [https://github.com/ShimmerEngineering/Shimmer-Java-Android-API](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API)
- **Integration Guide**: [../AndroidApp/SHIMMER_INTEGRATION_GUIDE.md](../AndroidApp/SHIMMER_INTEGRATION_GUIDE.md)
- **Implementation Example**: [../AndroidApp/src/main/java/com/multisensor/recording/](../AndroidApp/src/main/java/com/multisensor/recording/)

## Support

For issues and questions:
- Check [Troubleshooting section](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md#14-troubleshooting-and-diagnostics) in full documentation
- Visit [Shimmer Support Forum](https://www.shimmersensing.com/support/)
- Review [GitHub Issues](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/issues)