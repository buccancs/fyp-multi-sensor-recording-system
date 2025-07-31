# Shimmer3 GSR+ Quick Reference Guide

## Overview

This quick reference provides immediate access to essential information for Shimmer3 GSR+ integration within Android applications. The guide serves as a practical companion to the comprehensive documentation, offering streamlined instructions and examples that enable rapid implementation of physiological monitoring capabilities. For detailed technical analysis, theoretical background, and advanced implementation strategies, developers should consult the complete [SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md).

The Shimmer3 GSR+ represents a sophisticated wearable sensor platform that enables high-precision galvanic skin response measurements alongside complementary physiological signals. This integration guide focuses on the practical aspects of incorporating Shimmer3 devices into Android applications using the official Shimmer Research APIs and development frameworks.

## Quick Setup

The integration process involves several essential steps that establish the foundation for reliable Shimmer3 GSR+ communication and data collection. The following sections provide step-by-step instructions for setting up the development environment, configuring the necessary permissions, and implementing basic device integration functionality.

### 1. Dependencies

The first step requires adding the official Shimmer Research Android API to your project dependencies, along with any additional libraries needed for dependency injection and modern Android development patterns. The Shimmer Android API provides comprehensive device communication capabilities, data processing functions, and configuration management tools specifically designed for Shimmer sensor platforms.

```gradle
// Add to app/build.gradle
implementation 'com.shimmerresearch:shimmer_android_api:latest_version'
implementation 'androidx.hilt:hilt-android:2.44'
```

The Hilt dependency injection framework is recommended for managing Shimmer device instances and related services, as it provides clean architecture patterns that facilitate testing and maintainability. Additional dependencies may be required depending on your specific application architecture and data processing requirements.

### 2. Permissions (AndroidManifest.xml)

Android applications require explicit permissions for Bluetooth communication and location access, which are essential for discovering and connecting to Shimmer3 devices. The location permissions are required by Android for Bluetooth Low Energy device discovery, even though location services are not directly used by the Shimmer API.

```xml
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

Applications targeting Android 6.0 (API level 23) and higher must also implement runtime permission requests for location access. The Shimmer API includes helper functions that simplify the permission request process and provide clear user explanations for why these permissions are necessary.

### 3. Basic Integration

The basic integration example demonstrates the fundamental steps required to establish communication with a Shimmer3 GSR+ device, configure essential sensor parameters, and begin data streaming. This example provides the minimal code necessary for a functional integration while maintaining proper error handling and resource management.

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

This integration approach establishes a connection to the specified Shimmer3 device using its Bluetooth MAC address, configures the device to enable GSR sensing with appropriate range and sampling rate settings, and initiates real-time data streaming. The example includes proper null safety checks and uses the recommended API methods for device configuration.

## Sensor Configuration

Proper sensor configuration is crucial for obtaining high-quality physiological data that meets the specific requirements of your application. The Shimmer3 GSR+ provides extensive configuration options that allow developers to optimize device behavior for different use cases, ranging from low-power continuous monitoring to high-resolution research applications.

### GSR Range Settings

The GSR range configuration determines the measurement sensitivity and optimal resistance range for different skin conditions and application scenarios. Each range setting provides optimal performance for specific conductance levels, and proper range selection is essential for maximizing measurement accuracy and avoiding signal saturation.

| Range | Resistance | Conductance | Use Case |
|-------|------------|-------------|----------|
| 0     | 10kΩ - 56kΩ | 18-100 µS | High arousal |
| 1     | 56kΩ - 220kΩ | 4.5-18 µS | Normal |
| 2     | 220kΩ - 680kΩ | 1.5-4.5 µS | Dry skin |
| 3     | 680kΩ - 4.7MΩ | 0.2-1.5 µS | Very dry |
| 4     | Auto Range | Dynamic | Adaptive |

Range 0 is optimal for situations involving high emotional arousal or stress responses where skin conductance is expected to be elevated. Range 1 provides the best performance for normal measurement conditions with typical skin moisture levels. Range 2 is designed for participants with naturally dry skin or environmental conditions that reduce skin moisture. Range 3 accommodates very dry skin conditions that might occur in low-humidity environments or with certain participant demographics. Range 4 enables automatic range adjustment that adapts to changing skin conditions throughout the measurement session.

### Sampling Rates

The sampling rate configuration balances measurement precision, battery life, and data processing requirements. Higher sampling rates provide better temporal resolution for capturing rapid physiological changes but increase power consumption and data storage requirements.

**Low Power configurations** operating between 1-10 Hz are optimized for battery conservation and are suitable for applications requiring extended monitoring periods where rapid physiological changes are not expected. These configurations can extend battery life significantly while still capturing the essential characteristics of GSR signals.

**Standard configurations** operating between 25-51.2 Hz provide optimal balance between measurement quality and power consumption for most general-purpose applications. These rates capture the majority of physiologically relevant GSR signal components while maintaining reasonable power consumption and data processing requirements.

**High Resolution configurations** operating between 102.4-204.8 Hz are designed for research applications requiring detailed analysis of rapid physiological changes. These configurations provide excellent temporal resolution for capturing transient responses and enable sophisticated signal analysis techniques.

**Maximum sampling rates** up to 1000 Hz are available for specialized applications requiring extreme temporal precision. These rates are typically used for research applications involving rapid stimulus-response studies or detailed signal analysis requiring very high frequency content preservation.

### Enabled Sensors

The sensor combination configuration determines which physiological parameters are measured simultaneously, enabling comprehensive multi-modal monitoring or focused single-parameter studies. The Shimmer3 GSR+ supports various sensor combinations that can be optimized for specific research or application requirements.

```kotlin
// Common sensor combinations
val gsrOnly = Configuration.Shimmer3.SENSOR_GSR
val gsrWithPPG = Configuration.Shimmer3.SENSOR_GSR or Configuration.Shimmer3.SENSOR_PPG_A13
val fullSensorSet = Configuration.Shimmer3.SENSOR_GSR or 
                   Configuration.Shimmer3.SENSOR_PPG_A13 or 
                   Configuration.Shimmer3.SENSOR_LSM303DLHC_ACCEL
```

GSR-only configurations minimize power consumption and data processing requirements while providing focused measurements of electrodermal activity. GSR with PPG combinations enable simultaneous monitoring of autonomic nervous system activity through both electrodermal and cardiovascular channels. Full sensor configurations provide comprehensive physiological monitoring that captures electrodermal, cardiovascular, and movement-related signals for complete contextual analysis.

## Data Processing

Effective data processing is essential for extracting meaningful physiological insights from the raw sensor data provided by the Shimmer3 GSR+ device. The Shimmer API provides sophisticated data structures and processing capabilities that enable real-time analysis and quality assessment of physiological signals.

### ObjectCluster Data Extraction

The ObjectCluster data structure represents the fundamental mechanism for accessing processed sensor data from Shimmer3 devices. This structure provides organized access to calibrated sensor values, timestamps, and metadata that enable comprehensive analysis of physiological signals. The data extraction process should be implemented with proper error handling to ensure robust operation under various signal conditions.

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

The "CAL" format specification ensures that extracted values are properly calibrated and represent meaningful physiological units. This calibrated data can be used directly for analysis without requiring additional conversion steps, simplifying the data processing pipeline and reducing the likelihood of calibration errors.

### Data Quality Metrics

Implementing comprehensive data quality assessment is crucial for ensuring the reliability and validity of physiological measurements. The quality assessment framework should evaluate multiple aspects of signal characteristics to provide comprehensive quality indicators that can guide data interpretation and processing decisions.

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

Signal-to-noise ratio calculations provide quantitative measures of signal quality that can be used to identify periods of poor data quality or sensor contact issues. Artifact detection algorithms identify abnormal signal characteristics that may indicate movement artifacts, electrical interference, or sensor placement problems. Continuity assessment evaluates data completeness and identifies gaps or interruptions in data collection that may affect analysis validity.

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

Developers seeking comprehensive information should begin with the full documentation available in [SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md), which provides master thesis-level technical analysis covering all aspects of Shimmer3 GSR+ integration, from hardware specifications to advanced implementation patterns.

The official API documentation is maintained in the [Shimmer Java Android API repository](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API), which contains the latest SDK updates, API references, and example implementations that demonstrate best practices for Android integration.

Practical implementation guidance is available through the [integration guide](../AndroidApp/SHIMMER_INTEGRATION_GUIDE.md), which provides step-by-step instructions for common integration scenarios. Working examples can be found in the [implementation directory](../AndroidApp/src/main/java/com/multisensor/recording/), which contains production-ready code that demonstrates proper API usage and architectural patterns.

## Support

When encountering issues or questions during implementation, developers should first consult the [troubleshooting section](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md#14-troubleshooting-and-diagnostics) in the comprehensive documentation, which provides systematic diagnostic procedures and solutions for common problems.

Additional support is available through the [Shimmer Support Forum](https://www.shimmersensing.com/support/), where community members and Shimmer Research engineers provide assistance with technical questions and implementation challenges.

For specific API issues or bug reports, developers should review existing [GitHub Issues](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/issues) and submit new issues with detailed descriptions and reproducible examples when necessary.