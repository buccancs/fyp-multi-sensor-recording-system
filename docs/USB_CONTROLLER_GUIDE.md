# USB Controller Guide

## Overview

The UsbController is a sophisticated component responsible for managing USB device interactions in the multi-sensor recording system. It provides comprehensive support for TOPDON thermal cameras with enhanced multi-device capabilities, state persistence, and robust error handling.

## Architecture

### Key Components

1. **UsbController** - Main controller class handling USB device management
2. **UsbDeviceManager** - Low-level USB operations and device detection
3. **MainActivity Integration** - Clean callback-based UI integration
4. **State Persistence** - Device state preservation across app restarts
5. **Multi-Device Support** - Simultaneous handling of multiple USB devices

### Design Principles

- **Separation of Concerns**: Clear separation between USB logic and UI components
- **Callback-Based Communication**: Clean interface for UI updates and events
- **State Management**: Comprehensive tracking of device states and connections
- **Resilient Error Handling**: Robust error recovery and user feedback
- **Performance Optimization**: Efficient periodic scanning and resource management

## Features

### Core Functionality

#### Single Device Support
- Automatic detection of supported TOPDON thermal cameras
- Device attachment/detachment handling
- Permission-aware initialization
- Status updates and user notifications

#### Multi-Device Support ⭐ *Enhanced*
- **Simultaneous Device Tracking**: Support for multiple TOPDON devices connected at once
- **Unique Device Identification**: Each device tracked by vendor ID, product ID, and device name
- **Connection Statistics**: Track connection times and connection counts per device
- **Smart Status Updates**: Contextual status messages based on device count
- **Device Management**: Get device lists, check connection status, and retrieve device information

#### State Persistence ⭐ *Enhanced*
- **Multi-Device State**: Preserve state for multiple connected devices
- **Connection History**: Track historical connections and usage patterns
- **Preference Storage**: Robust SharedPreferences-based persistence
- **State Recovery**: Automatic restoration of device state on app restart

#### Advanced Monitoring
- **Periodic Scanning**: Configurable interval-based device scanning (5-second default)
- **Real-Time Detection**: Immediate response to system USB events
- **Connection Validation**: Cross-reference system events with actual device presence
- **Resource Management**: Proper cleanup and lifecycle management

## API Reference

### UsbController Public Methods

#### Device Management
```kotlin
// Get list of currently connected supported devices
fun getConnectedSupportedDevicesList(): List<UsbDevice>

// Get count of connected supported devices
fun getConnectedSupportedDeviceCount(): Int

// Check if specific device is connected
fun isDeviceConnected(deviceKey: String): Boolean

// Get device information by key
fun getDeviceInfoByKey(deviceKey: String): UsbDevice?
```

#### Connection Tracking
```kotlin
// Get connection time for device
fun getDeviceConnectionTime(deviceKey: String): Long?

// Get total connection count for device
fun getDeviceConnectionCount(deviceKey: String): Int

// Check for previously connected devices
fun hasPreviouslyConnectedDevice(context: Context): Boolean
```

#### Status and Monitoring
```kotlin
// Initialize USB monitoring
fun initializeUsbMonitoring(context: Context)

// Stop periodic scanning
fun stopPeriodicScanning()

// Get comprehensive status summary
fun getUsbStatusSummary(context: Context): String

// Get multi-device status summary
fun getMultiDeviceStatusSummary(context: Context): String
```

#### Event Handling
```kotlin
// Handle USB device intents from system
fun handleUsbDeviceIntent(context: Context, intent: Intent)

// Set callback for USB events
fun setCallback(callback: UsbCallback)
```

### UsbCallback Interface

```kotlin
interface UsbCallback {
    fun onSupportedDeviceAttached(device: UsbDevice)
    fun onUnsupportedDeviceAttached(device: UsbDevice)
    fun onDeviceDetached(device: UsbDevice)
    fun onUsbError(message: String)
    fun updateStatusText(text: String)
    fun initializeRecordingSystem()
    fun areAllPermissionsGranted(): Boolean
}
```

## Usage Examples

### Basic Setup

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity(), UsbController.UsbCallback {
    
    @Inject
    lateinit var usbController: UsbController
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Setup USB controller
        usbController.setCallback(this)
        usbController.initializeUsbMonitoring(this)
        
        // Handle initial USB intent
        usbController.handleUsbDeviceIntent(this, intent)
    }
    
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        usbController.handleUsbDeviceIntent(this, intent)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        usbController.stopPeriodicScanning()
    }
}
```

### Multi-Device Management

```kotlin
// Check connected device count
val deviceCount = usbController.getConnectedSupportedDeviceCount()
println("Connected devices: $deviceCount")

// Get list of all connected devices
val devices = usbController.getConnectedSupportedDevicesList()
devices.forEach { device ->
    val deviceKey = "${device.vendorId}_${device.productId}_${device.deviceName}"
    val connectionTime = usbController.getDeviceConnectionTime(deviceKey)
    val connectionCount = usbController.getDeviceConnectionCount(deviceKey)
    
    println("Device: ${device.deviceName}")
    println("  Connected at: ${Date(connectionTime ?: 0)}")
    println("  Total connections: $connectionCount")
}

// Check specific device
val deviceKey = "3034_14593_/dev/bus/usb/001/001"
if (usbController.isDeviceConnected(deviceKey)) {
    val device = usbController.getDeviceInfoByKey(deviceKey)
    println("Device ${device?.deviceName} is connected")
}
```

### Status Monitoring

```kotlin
// Get comprehensive status
val statusSummary = usbController.getUsbStatusSummary(this)
println(statusSummary)

// Get multi-device specific summary
val multiDeviceStatus = usbController.getMultiDeviceStatusSummary(this)
println(multiDeviceStatus)
```

### Implementing Callbacks

```kotlin
override fun onSupportedDeviceAttached(device: UsbDevice) {
    val deviceCount = usbController.getConnectedSupportedDeviceCount()
    val message = when (deviceCount) {
        1 -> "First thermal camera connected!"
        else -> "Thermal camera #$deviceCount connected!"
    }
    showToast(message)
}

override fun onDeviceDetached(device: UsbDevice) {
    val remainingCount = usbController.getConnectedSupportedDeviceCount()
    val message = when (remainingCount) {
        0 -> "All thermal cameras disconnected"
        else -> "Thermal camera disconnected. $remainingCount remaining."
    }
    showToast(message)
}

override fun updateStatusText(text: String) {
    statusTextView.text = text
}

override fun onUsbError(message: String) {
    Log.e("USB", "Error: $message")
    showErrorDialog(message)
}
```

## State Persistence

### Device State Storage

The UsbController automatically saves device state information including:

- **Last Connected Device**: Device name, vendor/product IDs, connection time
- **Connection Counts**: Total connections per device
- **Multi-Device State**: Currently connected device keys and information
- **Historical Data**: Previous connection times and statistics

### Restoration Process

On app startup, the controller:

1. Restores previous multi-device state from SharedPreferences
2. Rebuilds connection tracking maps
3. Performs initial device scan to validate current state
4. Updates tracking with actual connected devices

## Supported Devices

### TOPDON Thermal Cameras

| Model | Vendor ID | Product ID | Description |
|-------|-----------|------------|-------------|
| TC001 | 0x0BDA | 0x3901 | TOPDON TC001 series cameras |
| TC001 Plus | 0x0BDA | 0x5840 | TOPDON TC001 Plus |
| TC001 Variant | 0x0BDA | 0x5830 | TOPDON TC001 variant |
| TC001 Variant | 0x0BDA | 0x5838 | TOPDON TC001 variant |

### Device Key Format

Each device is uniquely identified using the format:
```
{vendorId}_{productId}_{deviceName}
```

Example: `3034_14593_/dev/bus/usb/001/001`

## Configuration

### Constants

```kotlin
companion object {
    private const val USB_PREFS_NAME = "usb_device_prefs"
    private const val SCANNING_INTERVAL_MS = 5000L // 5 seconds
}
```

### Customization Options

- **Scanning Interval**: Modify `SCANNING_INTERVAL_MS` for different polling frequencies
- **Preference Keys**: Customize SharedPreferences keys for different storage schemes
- **Device Support**: Extend supported device list in UsbDeviceManager

## Error Handling

### Common Error Scenarios

1. **Device Not Found**: Null device in USB intent
2. **Permission Denied**: Missing USB permissions
3. **State Corruption**: SharedPreferences corruption
4. **Memory Issues**: Resource cleanup failures

### Error Recovery

- Graceful degradation when state cannot be restored
- Automatic retry mechanisms for transient failures
- User-friendly error messages with actionable guidance
- Comprehensive logging for debugging

## Performance Considerations

### Optimization Strategies

1. **Efficient Scanning**: 5-second intervals balance responsiveness and battery usage
2. **Resource Management**: Proper Handler cleanup and memory management
3. **State Caching**: In-memory device tracking reduces database calls
4. **Lazy Initialization**: Components initialized only when needed

### Memory Management

- Proper cleanup in `onDestroy()`
- Handler callback removal
- Map clearing on shutdown
- Weak references where appropriate

## Testing

### Unit Test Coverage

The UsbController includes comprehensive unit tests covering:

- ✅ Basic device attachment/detachment
- ✅ Multi-device scenarios
- ✅ State persistence and restoration
- ✅ Connection tracking and statistics
- ✅ Error handling and edge cases
- ✅ Status text generation
- ✅ Device key management
- ✅ Mixed device scenarios (supported/unsupported)

### Test Examples

```kotlin
@Test
fun `should track multiple simultaneous devices`() {
    // Test connecting multiple devices
    // Verify tracking and status updates
}

@Test
fun `should handle device detachment in multi-device scenario`() {
    // Test removing devices from multi-device setup
    // Verify remaining devices and status updates
}

@Test
fun `should track device connection times and counts`() {
    // Test connection statistics tracking
    // Verify historical data persistence
}
```

## Migration Guide

### From Previous Version

If upgrading from a previous USB implementation:

1. **Replace Direct USB Calls**: Change direct UsbDeviceManager usage to UsbController
2. **Update Callback Interface**: Implement UsbController.UsbCallback instead of UsbDeviceManager.UsbDeviceCallback
3. **Initialize Monitoring**: Add `usbController.initializeUsbMonitoring(this)` to onCreate
4. **Update Cleanup**: Add `usbController.stopPeriodicScanning()` to onDestroy
5. **Handle Multi-Device**: Update UI to handle multiple device scenarios

### Backward Compatibility

The enhanced UsbController maintains compatibility with single-device workflows while adding multi-device capabilities.

## Troubleshooting

### Common Issues

1. **Devices Not Detected**
   - Check USB permissions in manifest
   - Verify device filter configuration
   - Ensure cable connection and device power

2. **State Not Persisting**
   - Verify app has storage permissions
   - Check SharedPreferences accessibility
   - Review device key generation

3. **Performance Issues**
   - Monitor scanning interval settings
   - Check for Handler callback leaks
   - Verify proper cleanup in lifecycle methods

### Debug Information

Use the status summary methods for debugging:

```kotlin
// Get detailed debug information
val debugInfo = usbController.getUsbStatusSummary(this)
Log.d("USB_DEBUG", debugInfo)

// Get multi-device specific debug info
val multiDebugInfo = usbController.getMultiDeviceStatusSummary(this)
Log.d("USB_MULTI_DEBUG", multiDebugInfo)
```

## Future Enhancements

### Completed Advanced Features ✅

- **✅ Performance Analytics**: Real-time performance monitoring with academic-grade statistical analysis
- **✅ Connection Quality Monitoring**: Advanced quality assessment using signal stability analysis
- **✅ Device Prioritization**: Multi-criteria decision analysis for optimal device selection
- **✅ Academic Documentation**: Formal analysis with theoretical foundations and empirical validation

### Planned Features

- [ ] **Hot-Swap Detection**: Advanced detection of device replacement scenarios
- [ ] **Configuration Profiles**: Per-device configuration persistence
- [ ] **Network Monitoring**: Network-based device status reporting
- [ ] **Predictive Analytics**: Machine learning-based device behavior prediction
- [ ] **Cross-Platform Support**: Extension to iOS and desktop platforms

## Advanced Features (Academic Implementation)

### Performance Analytics System

The USB Controller now includes a comprehensive performance analytics system based on formal mathematical models:

#### Key Features:
- **Real-time Metrics Collection**: O(1) event recording with sliding window optimization
- **Statistical Analysis**: Percentile calculation, trimmed mean for outlier handling
- **Quality Assessment**: Multi-dimensional connection quality scoring
- **Resource Monitoring**: CPU, memory, and throughput efficiency tracking

#### Usage Example:
```kotlin
// Get comprehensive performance report
val report = usbController.getPerformanceAnalyticsReport(context)
println("Total Events: ${report.totalEvents}")
println("95th Percentile Response Time: ${report.percentile95ResponseTime}ms")
println("CPU Efficiency: ${report.cpuEfficiencyScore}")

// Monitor specific device quality
val deviceKey = "3034_14593_/dev/bus/usb/001/001"
val qualityReport = usbController.monitorDeviceConnectionQuality(deviceKey)
println(qualityReport)
```

### Device Prioritization System

Advanced multi-criteria decision analysis (MCDA) for optimal device selection:

#### Mathematical Foundation:
```
Priority Score = Σ(wᵢ × normalized_scoreᵢ)
```

Where weights are empirically derived:
- Connection Quality: 35%
- Connection History: 25% 
- Device Characteristics: 20%
- Resource Efficiency: 20%

#### Usage Example:
```kotlin
// Get device priority assessments
val assessments = usbController.getDevicePriorityAssessments()
assessments.forEach { assessment ->
    println("Device: ${assessment.deviceKey}")
    println("Priority Level: ${assessment.priorityLevel}")
    println("Score: ${assessment.priorityScore}")
    println("Confidence: ${assessment.confidence}")
}

// Optimize device selection for multi-device recording
val selection = usbController.getOptimizedDeviceSelection(maxDevices = 3)
println("Primary Device: ${selection.primaryDevice?.deviceKey}")
println("Secondary Devices: ${selection.secondaryDevices.size}")
println("Selection Quality: ${selection.optimizationMetrics.totalQualityScore}")
```

### Comprehensive System Analysis

Get academic-grade system analysis combining all metrics:

```kotlin
val systemStatus = usbController.getComprehensiveSystemStatus(context)
println(systemStatus)
```

This provides:
- Multi-device connection status
- Performance analytics summary
- Device prioritization results
- Optimization metrics
- System recommendations

### Adaptive Learning

The system implements adaptive learning for continuous optimization:

```kotlin
// Update device performance feedback for learning
usbController.updateDevicePerformanceFeedback(
    deviceKey = "device_001",
    performanceScore = 0.85,
    actualReliability = 0.9,
    resourceUsage = 0.3
)
```

This enables the system to:
- Adjust priority weights based on real performance
- Improve prediction accuracy over time
- Adapt to specific usage patterns
- Optimize for user-specific scenarios

### Extension Points

The UsbController is designed for extensibility:

- Custom device support through UsbDeviceManager extension
- Additional callback methods for specialized events
- Plugin architecture for third-party device integrations
- Configuration-driven device management

## Conclusion

The enhanced UsbController provides a robust, scalable solution for USB device management in multi-sensor recording applications. With comprehensive multi-device support, state persistence, and extensive testing, it offers a reliable foundation for thermal camera integration.

For questions or issues, refer to the unit tests for usage examples and consult the troubleshooting section for common problems.