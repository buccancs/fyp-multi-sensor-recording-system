# NetworkController Documentation

## Overview

The `NetworkController` is a comprehensive controller responsible for handling all streaming and network-related logic in the multi-sensor recording system. It has been completely enhanced with network monitoring, streaming quality management, error handling, and recovery mechanisms.

## Features Implemented

### ✅ Network Connectivity Monitoring
- **Modern Android API Support**: Uses `ConnectivityManager.NetworkCallback` for API 24+
- **Automatic Recovery**: Implements retry logic with exponential backoff
- **Network Type Detection**: Automatically detects WiFi, 4G LTE, 3G, 2G, Ethernet
- **Connection Quality Assessment**: Provides quality ratings based on network type

### ✅ Streaming Session Management
- **Coroutine-based Streaming**: Fully async streaming implementation using coroutines
- **Session Statistics**: Tracks transmission duration, bytes transmitted, average bitrate
- **Frame Rate Control**: Configurable frame rates based on quality settings
- **Adaptive Streaming**: Automatically adjusts quality based on network conditions

### ✅ Streaming Quality Management
```kotlin
enum class StreamingQuality {
    LOW("Low (480p, 15fps)"),      // 500 KB/s
    MEDIUM("Medium (720p, 30fps)"), // 1.2 MB/s
    HIGH("High (1080p, 30fps)"),   // 2.5 MB/s
    ULTRA("Ultra (1080p, 60fps)")  // 4.0 MB/s
}
```

### ✅ Error Handling and Recovery
- **Network Error Detection**: Distinguishes between recoverable and non-recoverable errors
- **Automatic Recovery**: Attempts streaming recovery when network is restored
- **Emergency Stop**: Provides emergency stop functionality with state preservation
- **Connection Retry Logic**: Implements configurable retry attempts with backoff

### ✅ Comprehensive Monitoring
- **Real-time Statistics**: Provides detailed network and streaming statistics
- **Debug Information**: Enhanced debug overlays with live metrics
- **Performance Metrics**: Tracks bandwidth utilization and transmission rates

## API Reference

### Core Methods

#### Network Monitoring
```kotlin
fun startNetworkMonitoring(context: Context)
fun stopNetworkMonitoring()
fun handleNetworkConnectivityChange(connected: Boolean)
```

#### Streaming Control
```kotlin
fun startStreaming(context: Context)
fun stopStreaming(context: Context)
fun emergencyStopStreaming(context: Context)
```

#### Quality Management
```kotlin
fun setStreamingQuality(quality: StreamingQuality)
fun updateStreamingMetrics(frameRate: Int, dataSize: String)
```

#### State Management
```kotlin
fun isStreamingActive(): Boolean
fun getStreamingMetrics(): Pair<Int, String>
fun getNetworkStatistics(context: Context?): Map<String, Any>
fun resetState()
fun cleanup()
```

### NetworkCallback Interface

The `NetworkCallback` interface provides comprehensive callbacks for UI integration:

```kotlin
interface NetworkCallback {
    fun onStreamingStarted()
    fun onStreamingStopped()
    fun onNetworkStatusChanged(connected: Boolean)
    fun onStreamingError(message: String)
    fun onStreamingQualityChanged(quality: StreamingQuality)
    fun onNetworkRecovery(networkType: String)
    fun updateStatusText(text: String)
    fun showToast(message: String, duration: Int)
    fun getStreamingIndicator(): View?
    fun getStreamingLabel(): View?
    fun getStreamingDebugOverlay(): TextView?
}
```

## Integration with MainActivity

### Dependency Injection
```kotlin
@Inject
lateinit var networkController: NetworkController
```

### Callback Implementation
The MainActivity implements `NetworkController.NetworkCallback` to receive all streaming and network events:

```kotlin
class MainActivity : AppCompatActivity(), NetworkController.NetworkCallback {
    
    private fun initializeNetworkController() {
        networkController.setCallback(this)
    }
    
    override fun onStreamingStarted() {
        // Update UI for streaming start
    }
    
    override fun onNetworkStatusChanged(connected: Boolean) {
        // Handle network status changes
    }
    
    // ... other callback implementations
}
```

### Lifecycle Management
```kotlin
override fun onDestroy() {
    super.onDestroy()
    networkController.cleanup() // Proper resource cleanup
}
```

## Testing

### Comprehensive Test Coverage
The `NetworkControllerTest` provides complete test coverage with 20+ test scenarios:

- **Streaming Indicator Management Tests**
- **Network Connectivity Monitoring Tests**
- **Streaming Quality Management Tests**
- **Actual Streaming Logic Tests**
- **Network Statistics Tests**
- **Emergency and Error Handling Tests**
- **StreamingQuality Enum Tests**

### Test Categories
```kotlin
// Streaming UI Tests
@Test fun `should show streaming indicator correctly`()
@Test fun `should update streaming debug overlay with correct text`()

// Network Monitoring Tests
@Test fun `should handle network connectivity changes`()
@Test fun `should handle network reconnection gracefully`()

// Quality Management Tests
@Test fun `should set streaming quality to LOW correctly`()
@Test fun `should set streaming quality to HIGH correctly`()

// Streaming Logic Tests
@Test fun `should start streaming session successfully`()
@Test fun `should stop streaming session successfully`()

// Error Handling Tests
@Test fun `should handle emergency streaming stop`()
@Test fun `should reset state correctly`()
```

## Usage Examples

### Basic Usage
```kotlin
// Initialize network monitoring
networkController.startNetworkMonitoring(context)

// Start streaming
networkController.startStreaming(context)

// Change quality
networkController.setStreamingQuality(StreamingQuality.HIGH)

// Stop streaming
networkController.stopStreaming(context)
```

### Advanced Usage
```kotlin
// Get comprehensive statistics
val stats = networkController.getNetworkStatistics(context)
Log.d("Network", "Stats: $stats")

// Handle emergency scenarios
networkController.emergencyStopStreaming(context)

// Custom quality adaptation
val networkType = NetworkUtils.getNetworkType(context)
val quality = when (networkType) {
    "WiFi" -> StreamingQuality.ULTRA
    "4G LTE" -> StreamingQuality.HIGH
    "3G" -> StreamingQuality.MEDIUM
    else -> StreamingQuality.LOW
}
networkController.setStreamingQuality(quality)
```

## Architecture Benefits

### Separation of Concerns
- **Extracted from MainActivity**: Reduces MainActivity complexity
- **Single Responsibility**: Focused only on network and streaming logic
- **Testable**: Comprehensive unit test coverage
- **Injectable**: Uses Hilt dependency injection

### Modern Android Practices
- **Coroutines**: Async/await pattern for streaming
- **StateFlow**: Reactive state management
- **Modern APIs**: Uses latest Android networking APIs
- **Lifecycle Aware**: Proper resource management

### Error Resilience
- **Graceful Degradation**: Handles network issues gracefully
- **Automatic Recovery**: Recovers from temporary network issues
- **State Preservation**: Maintains state during recovery attempts
- **Emergency Handling**: Provides emergency stop capabilities

## Future Enhancements

### TODO: Advanced Streaming Protocols
- [ ] Implement RTMP streaming support
- [ ] Add WebRTC integration
- [ ] Support for HLS adaptive streaming

### TODO: Enhanced Network Features
- [ ] Implement advanced bandwidth estimation algorithms
- [ ] Add network prediction and caching
- [ ] Support for multiple concurrent streams

### TODO: Performance Optimizations
- [ ] Implement adaptive bitrate streaming
- [ ] Add frame dropping for network congestion
- [ ] Optimize memory usage for long sessions

## Integration Notes

1. **Dependency Injection**: NetworkController is injected via Hilt
2. **Lifecycle Management**: Call `cleanup()` in `onDestroy()`
3. **Callback Setup**: Implement `NetworkCallback` in your activity/fragment
4. **Error Handling**: Monitor callback methods for error conditions
5. **Testing**: Use provided test base class for consistent testing

## Performance Considerations

- **Memory Management**: Automatic cleanup of coroutines and callbacks
- **Network Efficiency**: Adaptive quality reduces bandwidth usage
- **CPU Usage**: Optimized frame processing and transmission
- **Battery Life**: Network monitoring is optimized for battery usage

This enhanced NetworkController provides a robust foundation for streaming and network operations in the multi-sensor recording system.