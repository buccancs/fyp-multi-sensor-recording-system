# Dependency Injection Guidelines

## Overview

This document establishes comprehensive guidelines for using Dependency Injection (DI) throughout the Multi-Sensor Recording System. The Android application uses Hilt for DI, while the Python application follows manual injection principles. These guidelines ensure consistency, testability, and maintainability across both platforms.

## Android Application - Hilt Dependency Injection

### Architecture Principles

The Android application implements DI following these core principles:
- **Constructor Injection**: Preferred method for all dependencies
- **Interface-Based Design**: Program to interfaces, not implementations
- **Proper Scoping**: Match component lifecycle with dependency scope
- **Testability**: Design for easy mock substitution during testing

### Scoping Strategy

#### @Singleton Scope
Use for components that should live for the entire application lifecycle:

```kotlin
@Singleton
class Logger @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // Logger implementation
}

@Singleton
class DeviceConnectionManager @Inject constructor(
    private val logger: Logger,
    private val networkManager: NetworkManager
) {
    // Device management implementation
}
```

**Suitable for:**
- Logging infrastructure
- Configuration managers
- Network managers
- Database repositories
- Hardware device managers

#### @ActivityScoped
Use for components tied to Activity lifecycle:

```kotlin
@ActivityScoped
class MainActivityCoordinator @Inject constructor(
    private val deviceManager: DeviceConnectionManager,
    private val logger: Logger
) {
    // Activity-specific coordination logic
}
```

**Suitable for:**
- UI controllers
- Activity-specific coordinators
- Navigation managers

#### @ViewModelScoped (Hilt @HiltViewModel)
Use for ViewModels with proper lifecycle management:

```kotlin
@HiltViewModel
class MainViewModelRefactored @Inject constructor(
    private val recordingController: RecordingSessionController,
    private val deviceManager: DeviceConnectionManager,
    private val fileManager: FileTransferManager,
    private val calibrationManager: CalibrationManager
) : ViewModel() {
    // ViewModel implementation with proper delegation
}
```

### Module Organization

#### Core Application Module
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    @Provides
    @Singleton
    fun provideContext(@ApplicationContext context: Context): Context = context
    
    // Core infrastructure dependencies
}
```

#### Security Module
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object SecurityModule {
    
    @Provides
    @Singleton
    fun provideSecurityUtils(
        @ApplicationContext context: Context,
        logger: Logger
    ): SecurityUtils {
        return SecurityUtils(context, logger)
    }
}
```

#### Network Module (Recommended Future Addition)
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideJsonSocketClient(
        logger: Logger,
        securityUtils: SecurityUtils
    ): JsonSocketClient {
        return JsonSocketClient(logger, securityUtils)
    }
    
    @Provides
    @Singleton
    fun provideNetworkManager(
        socketClient: JsonSocketClient,
        logger: Logger
    ): NetworkManager {
        return NetworkManager(socketClient, logger)
    }
}
```

### Controller Injection Patterns

#### Specialized Controllers
All specialized controllers follow consistent injection patterns:

```kotlin
@Singleton
class RecordingSessionController @Inject constructor(
    private val cameraRecorder: CameraRecorder,
    private val thermalRecorder: ThermalRecorder,
    private val shimmerRecorder: ShimmerRecorder,
    private val logger: Logger
) {
    // Recording coordination logic
}

@Singleton
class CalibrationManager @Inject constructor(
    private val calibrationCapture: CalibrationCaptureManager,
    private val syncClockManager: SyncClockManager,
    private val logger: Logger
) {
    // Calibration process management
}
```

#### Key Benefits:
- **Single Responsibility**: Each controller has focused dependencies
- **Testability**: Easy to mock individual dependencies
- **Flexibility**: Can swap implementations without changing clients

### Testing with Dependency Injection

#### Test Module Creation
```kotlin
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [AppModule::class]
)
object TestAppModule {
    
    @Provides
    @Singleton
    fun provideTestLogger(): Logger = mockk<Logger>()
    
    @Provides
    @Singleton
    fun provideTestDeviceManager(logger: Logger): DeviceConnectionManager {
        return TestDeviceConnectionManager(logger)
    }
}
```

#### Test Implementation Example
```kotlin
@HiltAndroidTest
class RecordingSessionControllerTest {
    
    @get:Rule
    var hiltRule = HiltAndroidRule(this)
    
    @Inject
    lateinit var recordingController: RecordingSessionController
    
    @Inject
    lateinit var mockLogger: Logger
    
    @Before
    fun setUp() {
        hiltRule.inject()
    }
    
    @Test
    fun `should start recording successfully`() = runTest {
        // Test implementation with injected dependencies
    }
}
```

### Best Practices for Android DI

1. **Prefer Constructor Injection**: Always use constructor injection over field injection
2. **Use Interfaces**: Define clear interfaces for major components
3. **Avoid Circular Dependencies**: Design dependency graphs to be acyclic
4. **Minimize Scope Pollution**: Use the narrowest possible scope for each component
5. **Document Dependencies**: Clear documentation for complex dependency relationships

## Python Application - Manual Dependency Injection

### Architecture Principles

The Python application follows manual DI principles while maintaining the benefits of loose coupling:

```python
class CalibrationManager:
    """Manages camera calibration processes with injected dependencies."""
    
    def __init__(self, logger: Logger, file_manager: FileManager):
        self.logger = logger
        self.file_manager = file_manager
    
    def start_calibration(self, device_id: str) -> CalibrationResult:
        self.logger.info(f"Starting calibration for device {device_id}")
        # Calibration logic
```

### Registry Pattern for Complex Dependencies

For more complex scenarios, implement a simple service registry:

```python
class ServiceRegistry:
    """Simple service registry for dependency management."""
    
    def __init__(self):
        self._services = {}
    
    def register(self, service_type: type, instance: any):
        """Register a service instance."""
        self._services[service_type] = instance
    
    def get(self, service_type: type):
        """Retrieve a registered service."""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")
        return self._services[service_type]

# Usage example
registry = ServiceRegistry()
registry.register(Logger, Logger())
registry.register(NetworkManager, NetworkManager(registry.get(Logger)))
```

### Component Factory Pattern

For creating configured components:

```python
class ComponentFactory:
    """Factory for creating properly configured components."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._logger = Logger(config.get('log_level', 'INFO'))
    
    def create_session_manager(self) -> SessionManager:
        """Create a session manager with all dependencies."""
        network_manager = NetworkManager(self._logger)
        device_manager = DeviceManager(self._logger, network_manager)
        return SessionManager(self._logger, device_manager, self.config)
    
    def create_calibration_manager(self) -> CalibrationManager:
        """Create a calibration manager with dependencies."""
        file_manager = FileManager(self._logger)
        return CalibrationManager(self._logger, file_manager)
```

### Testing with Manual DI

```python
import unittest
from unittest.mock import Mock

class TestSessionManager(unittest.TestCase):
    
    def setUp(self):
        self.mock_logger = Mock(spec=Logger)
        self.mock_device_manager = Mock(spec=DeviceManager)
        self.session_manager = SessionManager(
            self.mock_logger, 
            self.mock_device_manager,
            {'session_timeout': 30}
        )
    
    def test_start_session(self):
        # Test with mocked dependencies
        result = self.session_manager.start_session('test_session')
        self.mock_logger.info.assert_called()
```

### Best Practices for Python DI

1. **Constructor Injection**: Pass dependencies through constructors
2. **Type Hints**: Use type hints for clear dependency contracts
3. **Interface Definition**: Define clear protocols for major components
4. **Factory Pattern**: Use factories for complex object creation
5. **Registry for Singletons**: Use registry pattern for singleton-like services

## Cross-Platform DI Guidelines

### Consistency Principles

1. **Same Interfaces**: Define similar interfaces across Android and Python
2. **Equivalent Scoping**: Match component lifecycles where applicable
3. **Parallel Testing**: Similar testing approaches on both platforms
4. **Documentation**: Consistent documentation of dependencies

### Example: Logger Interface Consistency

**Android:**
```kotlin
interface ILogger {
    fun info(message: String)
    fun error(message: String, throwable: Throwable? = null)
    fun debug(message: String)
}

@Singleton
class Logger @Inject constructor(
    @ApplicationContext private val context: Context
) : ILogger {
    // Implementation
}
```

**Python:**
```python
from abc import ABC, abstractmethod

class ILogger(ABC):
    @abstractmethod
    def info(self, message: str) -> None:
        pass
    
    @abstractmethod
    def error(self, message: str, exception: Exception = None) -> None:
        pass
    
    @abstractmethod
    def debug(self, message: str) -> None:
        pass

class Logger(ILogger):
    def __init__(self, log_level: str = 'INFO'):
        self.log_level = log_level
    
    # Implementation
```

## Migration Guidelines

### Adding New Dependencies

1. **Define Interface**: Start with clear interface definition
2. **Create Implementation**: Implement with proper constructor injection
3. **Update Modules**: Add to appropriate DI modules
4. **Write Tests**: Create comprehensive tests with mocked dependencies
5. **Update Documentation**: Document the new dependency relationships

### Refactoring Existing Code

1. **Identify Dependencies**: Map current hard-coded dependencies
2. **Extract Interfaces**: Define clear interfaces for dependencies
3. **Implement Injection**: Convert to constructor injection pattern
4. **Update Tests**: Migrate tests to use DI patterns
5. **Validate**: Ensure no functionality regression

## Quality Assurance

### Testing DI Configuration

1. **Module Tests**: Test DI module configurations
2. **Integration Tests**: Validate component wiring
3. **Circular Dependency Detection**: Automated checks for dependency cycles
4. **Performance Testing**: Measure DI overhead and optimization

### Documentation Requirements

1. **Dependency Graphs**: Visual representation of major dependencies
2. **Scope Documentation**: Clear explanation of component scopes
3. **Testing Examples**: Comprehensive testing examples for each pattern
4. **Migration Guides**: Step-by-step guides for adding new dependencies

---

These DI guidelines ensure consistent, testable, and maintainable dependency management throughout the Multi-Sensor Recording System. Follow these patterns to maintain architectural integrity and ease future development and testing efforts.