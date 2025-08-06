# Cross-Cutting Concerns Documentation

## Overview

This document provides comprehensive guidance on cross-cutting concerns in the Multi-Sensor Recording System. Cross-cutting concerns are aspects of the system that span multiple layers and components, requiring centralized implementation to maintain consistency and avoid code duplication.

## Infrastructure Layer Components

### 1. Centralized Logging Infrastructure

#### Purpose
Provide consistent logging across all system components with structured logging, configurable levels, and context preservation.

#### Implementation Guidelines

**Android (Kotlin)**
```kotlin
// Dependency injection for logger
@Singleton
class LoggerImpl @Inject constructor(
    @ApplicationContext private val context: Context
) : Logger {
    
    override fun debug(message: String, context: Map<String, Any>) {
        // Structured logging with context
    }
    
    override fun info(message: String, context: Map<String, Any>) {
        // Info level logging
    }
    
    override fun error(message: String, throwable: Throwable?, context: Map<String, Any>) {
        // Error logging with stack traces
    }
}

// Usage in components
class RecordingSessionController @Inject constructor(
    private val logger: Logger
) {
    fun startRecording(sessionId: String) {
        logger.info("Recording session started", mapOf(
            "sessionId" to sessionId,
            "timestamp" to System.currentTimeMillis()
        ))
    }
}
```

**Python**
```python
# Centralized logging configuration
import logging
from typing import Dict, Any, Optional

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure logger with structured format."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, context: Dict[str, Any] = None):
        context_str = f" | Context: {context}" if context else ""
        self.logger.info(f"{message}{context_str}")
    
    def error(self, message: str, exc_info: Optional[Exception] = None, context: Dict[str, Any] = None):
        context_str = f" | Context: {context}" if context else ""
        self.logger.error(f"{message}{context_str}", exc_info=exc_info)

# Usage in components
class CalibrationManager:
    def __init__(self):
        self.logger = StructuredLogger(__name__)
    
    def perform_calibration(self, device_id: str):
        self.logger.info("Starting calibration", {"device_id": device_id})
```

#### Best Practices
- **Always use dependency injection** for logger instances
- **Include relevant context** in log messages (session IDs, device IDs, timestamps)
- **Avoid direct platform logging** (android.util.Log, print statements)
- **Use appropriate log levels** (DEBUG for development, INFO for operations, ERROR for failures)

### 2. Synchronization Engine

#### Purpose
Ensure precise timing coordination across multiple devices with microsecond-level accuracy.

#### Implementation Guidelines

**Core Interface**
```kotlin
interface SynchronizationEngine {
    suspend fun synchronizeDevices(devices: List<Device>): SynchronizationResult
    fun getCurrentTimestamp(): Long
    fun calculateOffset(device: Device): TimestampOffset
    suspend fun establishSyncProtocol(devices: List<Device>): SyncProtocol
}

data class SynchronizationResult(
    val success: Boolean,
    val synchronizedDevices: List<Device>,
    val averageOffset: Long,
    val maxOffset: Long,
    val precision: Double
)
```

**Usage Pattern**
```kotlin
class MultiDeviceCoordinator @Inject constructor(
    private val syncEngine: SynchronizationEngine,
    private val logger: Logger
) {
    suspend fun startSynchronizedRecording(devices: List<Device>) {
        val syncResult = syncEngine.synchronizeDevices(devices)
        
        if (syncResult.success) {
            logger.info("Device synchronization successful", mapOf(
                "deviceCount" to devices.size,
                "averageOffset" to syncResult.averageOffset,
                "precision" to syncResult.precision
            ))
        } else {
            logger.error("Device synchronization failed", context = mapOf(
                "failedDevices" to devices.filter { !syncResult.synchronizedDevices.contains(it) }
            ))
        }
    }
}
```

#### Configuration
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object SynchronizationModule {
    
    @Provides
    @Singleton
    fun provideSynchronizationEngine(
        logger: Logger
    ): SynchronizationEngine = SynchronizationEngineImpl(
        targetPrecision = 1000L, // 1ms target precision
        maxRetries = 3,
        logger = logger
    )
}
```

### 3. Error Handling Infrastructure

#### Purpose
Provide consistent error handling patterns across all system components with proper error propagation and recovery strategies.

#### Implementation Guidelines

**Error Hierarchy**
```kotlin
sealed class SystemException(
    message: String, 
    cause: Throwable? = null,
    val errorCode: String,
    val recoverable: Boolean = false
) : Exception(message, cause)

class NetworkException(
    message: String, 
    cause: Throwable? = null,
    errorCode: String = "NETWORK_ERROR"
) : SystemException(message, cause, errorCode, recoverable = true)

class DeviceException(
    message: String, 
    cause: Throwable? = null,
    errorCode: String = "DEVICE_ERROR"
) : SystemException(message, cause, errorCode, recoverable = true)

class CalibrationException(
    message: String, 
    cause: Throwable? = null,
    errorCode: String = "CALIBRATION_ERROR"
) : SystemException(message, cause, errorCode, recoverable = false)
```

**Result-Based Error Handling**
```kotlin
// Use Result<T> for operations that can fail
class DeviceManager @Inject constructor(
    private val logger: Logger
) {
    suspend fun connectToDevice(deviceId: String): Result<Device> {
        return try {
            val device = performConnection(deviceId)
            logger.info("Device connected successfully", mapOf("deviceId" to deviceId))
            Result.success(device)
        } catch (e: NetworkException) {
            logger.error("Failed to connect to device", e, mapOf("deviceId" to deviceId))
            Result.failure(e)
        }
    }
    
    // Error recovery patterns
    suspend fun connectWithRetry(deviceId: String, maxRetries: Int = 3): Result<Device> {
        repeat(maxRetries) { attempt ->
            val result = connectToDevice(deviceId)
            if (result.isSuccess) return result
            
            if (attempt < maxRetries - 1) {
                logger.warn("Connection attempt failed, retrying", mapOf(
                    "deviceId" to deviceId,
                    "attempt" to attempt + 1,
                    "maxRetries" to maxRetries
                ))
                delay(1000L * (attempt + 1)) // Exponential backoff
            }
        }
        return Result.failure(DeviceException("Failed to connect after $maxRetries attempts"))
    }
}
```

#### Error Recovery Strategies
```kotlin
class ErrorRecoveryManager @Inject constructor(
    private val logger: Logger
) {
    suspend fun handleError(error: SystemException, context: Map<String, Any> = emptyMap()): RecoveryAction {
        return when {
            error.recoverable -> {
                logger.warn("Recoverable error occurred", mapOf(
                    "errorCode" to error.errorCode,
                    "context" to context
                ))
                RecoveryAction.RETRY
            }
            else -> {
                logger.error("Non-recoverable error occurred", error, context)
                RecoveryAction.FAIL_GRACEFULLY
            }
        }
    }
}

enum class RecoveryAction {
    RETRY,
    FAIL_GRACEFULLY,
    ESCALATE
}
```

### 4. Security Infrastructure

#### Purpose
Provide centralized security utilities for encryption, authentication, and privacy compliance.

#### Implementation Guidelines

**Security Utilities**
```kotlin
@Singleton
class SecurityUtils @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {
    fun encryptData(data: ByteArray): EncryptedData? {
        return try {
            // Hardware-backed encryption using Android Keystore
            val encryptedData = performEncryption(data)
            logger.debug("Data encrypted successfully", mapOf("dataSize" to data.size))
            encryptedData
        } catch (e: SecurityException) {
            logger.error("Encryption failed", e)
            null
        }
    }
    
    fun generateAuthToken(): String {
        // Cryptographically secure token generation
        return generateSecureToken()
    }
    
    fun createSecureSSLContext(): SSLContext? {
        // Certificate pinning and TLS configuration
        return configureSSLContext()
    }
}
```

**Privacy Management**
```kotlin
@Singleton
class PrivacyManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {
    fun recordConsent(participantId: String?, studyId: String?) {
        logger.info("Privacy consent recorded", mapOf(
            "participantId" to (participantId?.let { anonymizeId(it) } ?: "anonymous"),
            "studyId" to studyId,
            "timestamp" to System.currentTimeMillis()
        ))
    }
    
    fun anonymizeMetadata(metadata: Map<String, Any>): Map<String, Any> {
        return metadata.mapValues { (key, value) ->
            when {
                key.contains("id", ignoreCase = true) -> anonymizeValue(value)
                key.contains("name", ignoreCase = true) -> anonymizeValue(value)
                else -> value
            }
        }
    }
    
    private fun anonymizeValue(value: Any): String {
        // Implement anonymization logic
        return "ANONYMIZED_${value.hashCode()}"
    }
}
```

### 5. Performance Monitoring Infrastructure

#### Purpose
Provide centralized performance monitoring and optimization utilities.

#### Implementation Guidelines

**Performance Metrics**
```kotlin
@Singleton
class PerformanceMonitor @Inject constructor(
    private val logger: Logger
) {
    private val metrics = ConcurrentHashMap<String, PerformanceMetric>()
    
    fun startTimer(operationName: String): String {
        val timerId = UUID.randomUUID().toString()
        metrics[timerId] = PerformanceMetric(
            operationName = operationName,
            startTime = System.nanoTime()
        )
        return timerId
    }
    
    fun endTimer(timerId: String) {
        metrics[timerId]?.let { metric ->
            val duration = System.nanoTime() - metric.startTime
            logger.info("Operation completed", mapOf(
                "operation" to metric.operationName,
                "durationMs" to duration / 1_000_000
            ))
            metrics.remove(timerId)
        }
    }
    
    inline fun <T> measureOperation(operationName: String, operation: () -> T): T {
        val timerId = startTimer(operationName)
        return try {
            operation()
        } finally {
            endTimer(timerId)
        }
    }
}

data class PerformanceMetric(
    val operationName: String,
    val startTime: Long
)
```

## Usage Guidelines for Development Teams

### 1. Accessing Cross-Cutting Concerns

**Through Dependency Injection**
```kotlin
class AnyComponent @Inject constructor(
    private val logger: Logger,
    private val syncEngine: SynchronizationEngine,
    private val securityUtils: SecurityUtils,
    private val performanceMonitor: PerformanceMonitor
) {
    // Use infrastructure services through DI
}
```

### 2. Component Registration

**Infrastructure Module**
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object InfrastructureModule {
    
    @Provides
    @Singleton
    fun provideLogger(@ApplicationContext context: Context): Logger = LoggerImpl(context)
    
    @Provides
    @Singleton  
    fun provideSynchronizationEngine(logger: Logger): SynchronizationEngine = 
        SynchronizationEngineImpl(logger)
    
    @Provides
    @Singleton
    fun provideSecurityUtils(@ApplicationContext context: Context, logger: Logger): SecurityUtils = 
        SecurityUtils(context, logger)
    
    @Provides
    @Singleton
    fun providePerformanceMonitor(logger: Logger): PerformanceMonitor = 
        PerformanceMonitor(logger)
}
```

### 3. Testing Infrastructure Components

**Mock Implementations**
```kotlin
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [InfrastructureModule::class]
)
@Module
object TestInfrastructureModule {
    
    @Provides
    @Singleton
    fun provideTestLogger(): Logger = MockLogger()
    
    @Provides
    @Singleton
    fun provideTestSyncEngine(): SynchronizationEngine = MockSynchronizationEngine()
}

class MockLogger : Logger {
    val logs = mutableListOf<LogEntry>()
    
    override fun info(message: String, context: Map<String, Any>) {
        logs.add(LogEntry("INFO", message, context))
    }
    
    // ... other methods
}
```

## Best Practices

### 1. Consistency
- Always use infrastructure utilities instead of platform-specific APIs
- Follow established patterns for error handling and logging
- Use dependency injection for all infrastructure components

### 2. Performance
- Use structured logging with appropriate levels
- Implement performance monitoring for critical operations
- Consider asynchronous patterns for non-blocking operations

### 3. Security
- Never log sensitive information
- Use centralized encryption utilities
- Implement proper error handling to prevent information leakage

### 4. Testability
- Provide mock implementations for all infrastructure components
- Use dependency injection to enable test doubles
- Implement behavior verification for infrastructure interactions

## Maintenance and Evolution

### 1. Adding New Cross-Cutting Concerns
1. Define clear interface contracts
2. Implement with dependency injection support
3. Add to infrastructure module configuration
4. Create test doubles for unit testing
5. Update this documentation

### 2. Updating Existing Concerns
1. Maintain backward compatibility
2. Update all usage sites consistently
3. Update test doubles accordingly
4. Refresh documentation

### 3. Monitoring Usage
- Use architecture tests to validate proper usage
- Monitor for direct platform API usage
- Review code regularly for anti-patterns

This infrastructure provides a solid foundation for consistent, maintainable, and testable cross-cutting concerns across the entire Multi-Sensor Recording System.