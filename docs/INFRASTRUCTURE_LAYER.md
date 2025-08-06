# Infrastructure Layer Documentation

## Overview

The Infrastructure Layer in the Multi-Sensor Recording System provides cross-cutting concerns that span across all application layers. This layer ensures consistent behavior for logging, synchronization, error handling, and other system-wide concerns while maintaining clean separation from business logic.

## Cross-Cutting Concerns

### 1. Logging Infrastructure

**Location**: `AndroidApp/src/main/java/com/multisensor/recording/util/Logger.kt`

The logging system provides centralized, structured logging capabilities across the entire application.

#### Core Features
- **Centralized Logging**: Single `@Singleton` Logger instance managed by Hilt DI
- **Multi-Level Support**: VERBOSE, DEBUG, INFO, WARNING, ERROR levels
- **File Persistence**: Automatic log file rotation with 7-day retention
- **Structured Output**: Consistent timestamp and context formatting
- **Thread-Safe**: Coroutine-based async file operations

#### Usage Guidelines

```kotlin
// Inject Logger in any component
@Singleton
class MyService @Inject constructor(
    private val logger: Logger
) {
    
    fun performOperation() {
        logger.info("Starting operation")
        try {
            // Business logic
            logger.debug("Operation step completed")
        } catch (e: Exception) {
            logger.error("Operation failed", e)
        }
    }
}
```

#### Best Practices
- **Use appropriate log levels**: ERROR for failures, INFO for major events, DEBUG for detailed flow
- **Include context**: Always log relevant identifiers (session ID, device ID, etc.)
- **Avoid PII**: Never log personally identifiable information
- **Use structured messages**: Consistent format for easier parsing

### 2. Synchronization Engine

**Location**: `AndroidApp/src/main/java/com/multisensor/recording/calibration/SyncClockManager.kt`

The synchronization system ensures precise temporal coordination across multiple devices and data streams.

#### Core Components
- **SyncClockManager**: Handles device-level time synchronization
- **Session Synchronizer** (Python): Coordinates cross-device session timing
- **Master Clock Synchronizer** (Python): Maintains central time reference

#### Synchronization Hierarchy
1. **Master PC Clock**: Central time authority
2. **Device Sync**: Each Android device synchronizes with master
3. **Sensor Alignment**: Individual sensor timestamps aligned to device time
4. **Cross-Modal Sync**: Thermal, camera, and GSR data temporally aligned

#### Usage Guidelines

```kotlin
// Initialize synchronization in device setup
@Inject
class DeviceConnectionManager @Inject constructor(
    private val syncClockManager: SyncClockManager,
    private val logger: Logger
) {
    
    suspend fun connectDevice() {
        try {
            syncClockManager.synchronizeWithMaster()
            logger.info("Device synchronized with master clock")
        } catch (e: SynchronizationException) {
            logger.error("Clock sync failed", e)
            // Handle sync failure
        }
    }
}
```

#### Performance Requirements
- **<1ms Accuracy**: Target synchronization precision
- **<500ms Sync Time**: Maximum time to achieve synchronization
- **Automatic Recovery**: Self-healing from temporary sync failures

### 3. Error Handling Framework

**Location**: Distributed across `controllers/`, `managers/`, and `util/` packages

The error handling framework provides consistent exception management and recovery strategies.

#### Error Categories
1. **Infrastructure Errors**: Network, storage, hardware failures
2. **Business Logic Errors**: Invalid states, configuration issues
3. **External Service Errors**: Shimmer device, thermal camera failures
4. **User Input Errors**: Permission denials, invalid configurations

#### Error Handling Patterns

```kotlin
// Standardized error handling with Result patterns
sealed class RecordingResult<T> {
    data class Success<T>(val data: T) : RecordingResult<T>()
    data class Error<T>(val exception: Throwable, val message: String) : RecordingResult<T>()
}

class RecordingSessionController @Inject constructor(
    private val logger: Logger
) {
    
    suspend fun startRecording(): RecordingResult<SessionInfo> {
        return try {
            val session = initializeSession()
            logger.info("Recording session started: ${session.id}")
            RecordingResult.Success(session)
        } catch (e: DeviceNotAvailableException) {
            logger.error("Device unavailable for recording", e)
            RecordingResult.Error(e, "Recording device not available")
        } catch (e: StorageInsufficientException) {
            logger.error("Insufficient storage for recording", e)
            RecordingResult.Error(e, "Not enough storage space")
        }
    }
}
```

#### Recovery Strategies
- **Automatic Retry**: Network and device connection failures
- **Graceful Degradation**: Continue operation with reduced functionality
- **User Notification**: Clear error messages with actionable guidance
- **State Recovery**: Restore application state after failures

### 4. Dependency Injection Architecture

**Location**: `AndroidApp/src/main/java/com/multisensor/recording/di/`

The DI system ensures proper separation of concerns and testability throughout the application.

#### Module Organization
- **AppModule**: Core application dependencies
- **SecurityModule**: Security and encryption services
- **[Future] NetworkModule**: Network configuration and services

#### Scoping Strategy
- **@Singleton**: Logger, managers, long-lived services
- **@ActivityScoped**: UI controllers, view models
- **@ServiceScoped**: Background services and workers

#### Usage Guidelines

```kotlin
// Define dependencies with proper scoping
@Module
@InstallIn(SingletonComponent::class)
object CoreInfrastructureModule {
    
    @Provides
    @Singleton
    fun provideLogger(@ApplicationContext context: Context): Logger {
        return Logger(context)
    }
    
    @Provides
    @Singleton
    fun provideSyncClockManager(logger: Logger): SyncClockManager {
        return SyncClockManager(logger)
    }
}

// Inject in components
@Singleton
class MyService @Inject constructor(
    private val logger: Logger,
    private val syncManager: SyncClockManager
) {
    // Service implementation
}
```

### 5. Performance Monitoring

**Location**: `AndroidApp/src/main/java/com/multisensor/recording/util/PerformanceMonitor.kt`

The performance monitoring system provides real-time metrics and optimization insights.

#### Monitored Metrics
- **Memory Usage**: Heap allocation and garbage collection
- **CPU Utilization**: Per-component processing load
- **Network Performance**: Throughput and latency measurements
- **Storage I/O**: File operation performance
- **Battery Impact**: Power consumption tracking

#### Usage Guidelines

```kotlin
@Inject
class RecordingService @Inject constructor(
    private val performanceMonitor: PerformanceMonitor,
    private val logger: Logger
) {
    
    fun performRecording() {
        performanceMonitor.startMeasurement("recording_session")
        try {
            // Recording operations
        } finally {
            val metrics = performanceMonitor.endMeasurement("recording_session")
            logger.info("Recording performance: ${metrics.summary()}")
        }
    }
}
```

## Integration Guidelines

### For New Components

1. **Inject Required Infrastructure**: Always use DI to obtain Logger, SyncManager, etc.
2. **Follow Error Handling Patterns**: Use Result types and structured exception handling
3. **Implement Performance Monitoring**: Add measurements for performance-critical operations
4. **Maintain Sync Requirements**: Ensure temporal consistency in data operations

### For Architecture Evolution

1. **Preserve Interface Stability**: Changes to infrastructure should maintain backward compatibility
2. **Document Breaking Changes**: Any API changes must be documented with migration guidance
3. **Test Infrastructure Changes**: Comprehensive testing of cross-cutting concern modifications
4. **Monitor Impact**: Track performance impact of infrastructure modifications

## Quality Assurance

### Testing Strategy
- **Unit Tests**: Individual infrastructure component testing
- **Integration Tests**: Cross-component infrastructure interaction testing
- **Performance Tests**: Benchmark infrastructure performance characteristics
- **Failure Recovery Tests**: Validate error handling and recovery mechanisms

### Monitoring and Observability
- **Structured Logging**: Consistent log format for analysis
- **Performance Metrics**: Real-time performance tracking
- **Error Tracking**: Centralized error reporting and analysis
- **Health Checks**: Automated infrastructure health monitoring

## Future Considerations

### Scalability
- **Multi-Instance Support**: Prepare for multiple PC controllers
- **Distributed Logging**: Centralized log aggregation across devices
- **Advanced Synchronization**: Higher precision timing for expanded device counts

### Observability Enhancements
- **Metrics Export**: Integration with external monitoring systems
- **Distributed Tracing**: End-to-end request tracking across components
- **Alert System**: Proactive notification of infrastructure issues

---

This infrastructure layer documentation serves as the foundation for understanding and extending the cross-cutting concerns of the Multi-Sensor Recording System. All contributors should familiarize themselves with these patterns to maintain architectural consistency and system reliability.