# Multi-Sensor Recording System - Architecture Documentation

## Overview

The Multi-Sensor Recording System implements a **PC master-controller architecture** with **offline-first local recording** capabilities and **JSON socket protocol** for standardized communication. This document provides comprehensive architectural guidance, focusing on layer separation, cross-cutting concerns, and dependency management patterns.

## Layer Architecture

The system follows a strict layered architecture to maintain separation of concerns:

### 1. Presentation Layer (UI)
- **Components**: Activities, Fragments, ViewModels
- **Responsibilities**: User interface rendering, user interaction handling, UI state management
- **Dependencies**: Can only access Business Logic layer through Controllers/Managers
- **Restrictions**: Must NOT directly import from Network, Service, or Recording packages

```kotlin
// ✅ Correct: UI accessing business logic through controllers
class MainActivity @Inject constructor(
    private val recordingController: RecordingSessionController
)

// ❌ Forbidden: UI directly accessing services
class MainActivity @Inject constructor(
    private val shimmerService: ShimmerService // VIOLATION
)
```

### 2. Business Logic Layer
- **Components**: Controllers, Managers, Use Cases
- **Responsibilities**: Domain logic, business rules, data orchestration
- **Dependencies**: Can access Service Layer and Infrastructure utilities
- **Restrictions**: Must NOT directly import UI components (Activities, Fragments)

### 3. Service Layer 
- **Components**: Recording services, Network services, Device services
- **Responsibilities**: Core application services, external API communication
- **Dependencies**: Can access Infrastructure layer and data repositories
- **Restrictions**: Must NOT depend on UI or Business Logic layers

### 4. Infrastructure Layer
- **Components**: Logging, Security, Persistence, Synchronization utilities
- **Responsibilities**: Cross-cutting concerns, system utilities
- **Dependencies**: Framework and platform APIs only
- **Access Pattern**: All layers can access infrastructure utilities

## Cross-Cutting Concerns Documentation

### Logging Infrastructure

The system provides centralized logging through infrastructure utilities.

#### Usage Guidelines
```kotlin
// ✅ Correct: Use centralized logging utility
class RecordingService @Inject constructor(
    private val logger: Logger
) {
    fun startRecording() {
        logger.info("Starting recording session", mapOf("sessionId" to sessionId))
    }
}

// ❌ Forbidden: Direct Android Log usage
class RecordingService {
    fun startRecording() {
        Log.d("RecordingService", "Starting recording") // VIOLATION
    }
}
```

#### Logger Interface
```kotlin
interface Logger {
    fun debug(message: String, context: Map<String, Any> = emptyMap())
    fun info(message: String, context: Map<String, Any> = emptyMap())
    fun warn(message: String, context: Map<String, Any> = emptyMap())
    fun error(message: String, throwable: Throwable? = null, context: Map<String, Any> = emptyMap())
}
```

### Synchronization Engine

Centralized synchronization for multi-device coordination and timing precision.

#### Usage Guidelines
```kotlin
// Access synchronization through dependency injection
class MultiDeviceCoordinator @Inject constructor(
    private val syncEngine: SynchronizationEngine
) {
    suspend fun synchronizeDevices(devices: List<Device>) {
        val syncResult = syncEngine.synchronize(devices)
        // Handle synchronization result
    }
}
```

#### SynchronizationEngine Interface
```kotlin
interface SynchronizationEngine {
    suspend fun synchronize(devices: List<Device>): SynchronizationResult
    fun getCurrentTimestamp(): Long
    fun calculateOffset(device: Device): TimestampOffset
}
```

### Error Handling Infrastructure

Standardized error handling across all system components.

#### Error Handling Patterns
```kotlin
// Use Result-based error handling for operations that can fail
class CalibrationManager @Inject constructor(
    private val logger: Logger
) {
    suspend fun performCalibration(): Result<CalibrationResult> {
        return try {
            val result = doCalibration()
            Result.success(result)
        } catch (e: CalibrationException) {
            logger.error("Calibration failed", e, mapOf("deviceId" to deviceId))
            Result.failure(e)
        }
    }
}
```

#### Exception Hierarchy
```kotlin
sealed class SystemException(message: String, cause: Throwable? = null) : Exception(message, cause)
class NetworkException(message: String, cause: Throwable? = null) : SystemException(message, cause)
class DeviceException(message: String, cause: Throwable? = null) : SystemException(message, cause)
class CalibrationException(message: String, cause: Throwable? = null) : SystemException(message, cause)
```

## Dependency Injection Patterns

### Hilt Configuration

The system uses Hilt for dependency injection to enable testability and flexibility.

#### Scope Guidelines
```kotlin
// Controllers and Managers - Use @Singleton for system-wide services
@Singleton
class RecordingSessionController @Inject constructor(...)

// UI ViewModels - Use @HiltViewModel
@HiltViewModel 
class MainViewModelRefactored @Inject constructor(...)

// Activity-scoped dependencies
@ActivityScoped
class UIStateManager @Inject constructor(...)
```

#### DI Module Structure
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object InfrastructureModule {
    
    @Provides
    @Singleton
    fun provideLogger(): Logger = LoggerImpl()
    
    @Provides
    @Singleton
    fun provideSynchronizationEngine(): SynchronizationEngine = SynchronizationEngineImpl()
}
```

### Testing with DI

Leverage DI for test doubles and mocking:

```kotlin
// Test module for swapping implementations
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [InfrastructureModule::class]
)
@Module
object TestInfrastructureModule {
    
    @Provides
    @Singleton
    fun provideTestLogger(): Logger = MockLogger()
}
```

## Architecture Enforcement

### Static Analysis Rules

The system includes detekt rules to enforce architectural constraints:

#### Forbidden Import Rules
- UI layer cannot import `com.multisensor.recording.network.**`
- UI layer cannot import `com.multisensor.recording.service.**`  
- All layers should use centralized logging instead of `android.util.Log`

#### Architecture Tests
```kotlin
@Test
fun `UI layer should not directly import from network or service packages`() {
    // Validates that UI components don't bypass business logic layer
}

@Test
fun `Controllers should not directly import from UI packages`() {
    // Ensures business logic doesn't depend on UI implementation details
}
```

### Runtime Validation

```kotlin
// Architecture validation during development
class ArchitectureValidator {
    fun validateLayerSeparation() {
        // Runtime checks for proper layer separation
    }
}
```

## Scalability Considerations

### Current Capacity
- **Device Support**: Up to 8 concurrent Android recording devices
- **Architecture Pattern**: Star topology with PC master controller
- **Communication**: JSON socket protocol with WebSocket transport

### Scaling Beyond 8 Devices

#### Bottleneck Analysis
1. **Network Bandwidth**: Single PC controller may become network bottleneck
2. **Processing Power**: Central coordination requires significant CPU resources  
3. **Memory Usage**: Concurrent device management increases memory requirements

#### Scaling Strategies

##### Option 1: Hierarchical Architecture
```
PC Master Controller
├── Regional Controller 1 (Devices 1-4)
├── Regional Controller 2 (Devices 5-8)  
└── Regional Controller 3 (Devices 9-12)
```

##### Option 2: Distributed Star-Mesh
```kotlin
interface ClusterCoordinator {
    fun addNode(controller: PCController): Boolean
    fun distributeLoad(devices: List<Device>): LoadDistributionResult
    fun synchronizeCluster(): ClusterSyncResult
}
```

##### Option 3: Event-Driven Architecture
```kotlin
// Publish-subscribe pattern for device events
interface EventBus {
    fun publish(event: DeviceEvent)
    fun subscribe(eventType: Class<out DeviceEvent>, handler: EventHandler)
}
```

## Living Documentation Maintenance

### Documentation Update Process

1. **Code Changes**: Update relevant architecture documentation when making significant changes
2. **Diagram Synchronization**: Keep architecture diagrams current with implementation
3. **Review Process**: Include architecture review in code review checklist
4. **Automated Validation**: Use architecture tests to catch violations early

### Documentation Checklist
- [ ] Update layer descriptions when adding new components
- [ ] Refresh cross-cutting concern documentation for new utilities
- [ ] Update DI scope documentation for new services
- [ ] Validate architecture diagrams reflect current implementation
- [ ] Review scaling considerations when approaching device limits

### Architecture Decision Records (ADRs)

Document significant architectural decisions:

```markdown
# ADR-001: Centralized Logging Infrastructure

## Status
Accepted

## Context
Need consistent logging across all system components

## Decision
Implement centralized Logger interface with DI

## Consequences
- Improved debugging capabilities
- Consistent log format
- Testable logging behavior
```

## Integration Guidelines

### For New Components

1. **Identify Layer**: Determine appropriate architectural layer
2. **Define Dependencies**: Use DI for all external dependencies  
3. **Follow Patterns**: Implement established error handling and logging patterns
4. **Add Tests**: Include architecture tests for new components
5. **Update Documentation**: Refresh relevant architecture documentation

### For Existing Components

1. **Gradual Migration**: Migrate to new patterns incrementally
2. **Backward Compatibility**: Maintain compatibility during transition
3. **Testing**: Validate architectural compliance with tests
4. **Documentation**: Update documentation as components migrate

## Conclusion

This architecture documentation provides guidelines for maintaining clean layer separation, managing cross-cutting concerns, and ensuring scalability. The enforcement mechanisms (static analysis, architecture tests) help prevent architectural drift while the DI patterns enable testability and flexibility.

Regular review and updates of this documentation ensure it remains a valuable resource for development teams and maintains alignment with the actual system implementation.