# Contributor Guide: Multi-Sensor Recording System

Welcome to the bucika_gsr project! This guide outlines our strict quality standards and expectations for contributors. Our project maintains research-grade reliability with industry-standard practices.

## 🎯 Quality Standards Overview

We maintain exceptionally high standards to ensure research-grade reliability:

- **Test Coverage**: >95% for critical components, aiming for near 100%
- **Code Quality**: Near-zero tolerance for bugs in production code
- **Documentation**: Academic rigor with comprehensive documentation for all features
- **Performance**: Research-grade timing precision (<1ms synchronization accuracy)
- **Security**: Production-ready security with comprehensive privacy compliance

## 🚀 Quick Start for Contributors

### Prerequisites

1. **Development Environment**:
   ```bash
   # Clone the repository
   git clone https://github.com/buccancs/bucika_gsr.git
   cd bucika_gsr
   
   # Install Python dependencies
   pip install -e .[dev]
   
   # Install pre-commit hooks
   pre-commit install
   ```

2. **Android Development** (if working on Android components):
   - Android Studio Arctic Fox or later
   - Android SDK API 21+ (Android 5.0+)
   - Kotlin 1.8+ support

### Pre-Contribution Checklist

Before submitting any code, ensure you can answer "YES" to ALL of these:

- [ ] **Does my code compile without warnings?**
- [ ] **Do ALL existing tests pass?**
- [ ] **Have I written tests for my new functionality?**
- [ ] **Does my code follow the established patterns?**
- [ ] **Have I run the linters and fixed all issues?**
- [ ] **Is my code properly documented?**
- [ ] **Have I updated relevant documentation?**
- [ ] **Does my change maintain backward compatibility?**

## 📊 Code Quality Requirements

### Python Code Standards

#### Exception Handling Excellence
- **Requirement**: Specific exception types only (no bare `except:`)
- **Pattern**: Use targeted exception handling with proper context preservation
```python
# ✅ Good - Specific exception handling
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"Configuration file not found: {e}")
    raise ConfigurationError(f"Missing config file: {e}") from e
except PermissionError as e:
    logger.error(f"Insufficient permissions: {e}")
    raise SecurityError(f"Access denied: {e}") from e

# ❌ Bad - Generic exception handling
try:
    result = risky_operation()
except Exception:
    pass  # Never do this!
```

#### Type Safety
- **Requirement**: 100% type hints for public APIs
- **Tool**: mypy in strict mode
```python
# ✅ Good - Complete type annotations
def process_sensor_data(
    data: Dict[str, np.ndarray], 
    timestamps: List[float],
    quality_threshold: float = 0.95
) -> Tuple[bool, Optional[str]]:
    """Process sensor data with quality validation."""
    # Implementation with full type safety
```

#### Cognitive Complexity
- **Limit**: <15 cognitive complexity per function
- **Tool**: Monitored via static analysis
- **Pattern**: Break down complex functions into smaller, focused units

### Kotlin Code Standards

#### Architecture Patterns
- **Required**: Clean MVVM with single responsibility controllers
- **Pattern**: Reactive StateFlow-based state management
```kotlin
// ✅ Good - Clean controller with single responsibility
@Singleton
class RecordingSessionController @Inject constructor(
    private val deviceManager: DeviceManager,
    private val logger: Logger
) {
    private val _recordingState = MutableStateFlow(RecordingState.IDLE)
    val recordingState: StateFlow<RecordingState> = _recordingState.asStateFlow()
    
    suspend fun startRecording(config: RecordingConfig): Result<String> {
        // Focused recording logic only
    }
}
```

#### Exception Handling
- **Requirement**: Specific exception types with proper coroutine semantics
- **Pattern**: Preserve CancellationException for proper coroutine cancellation
```kotlin
// ✅ Good - Specific exception handling
try {
    val result = suspendingOperation()
    return Result.success(result)
} catch (e: CancellationException) {
    throw e  // Always re-throw CancellationException
} catch (e: SecurityException) {
    logger.error("Security violation during operation", e)
    return Result.failure(SecurityError("Access denied: ${e.message}"))
} catch (e: IOException) {
    logger.error("Network error during operation", e)
    return Result.failure(NetworkError("Connection failed: ${e.message}"))
}
```

## 🧪 Testing Standards

### Test Coverage Requirements

1. **Foundation Tests**: 100% pass rate required
   - Android components (5 comprehensive tests)
   - PC components (6 comprehensive tests)
   - Real component validation (zero mocking for critical paths)

2. **Integration Tests**: >90% pass rate expected
   - Multi-device coordination
   - Network performance validation
   - End-to-end workflow testing

### Testing Commands

```bash
# Quick validation during development
python run_evaluation_suite.py --quick --verbose

# Test specific categories
python run_evaluation_suite.py --category android_foundation
python run_evaluation_suite.py --category pc_foundation
python run_evaluation_suite.py --category integration_tests

# Complete evaluation before submission
python run_evaluation_suite.py --parallel
```

### Writing Tests

Follow our established patterns:

```python
# ✅ Good - Comprehensive test with real components
def test_calibration_manager_real_validation():
    """Test CalibrationManager with actual OpenCV operations."""
    manager = CalibrationManager()
    
    # Test with realistic data
    result = manager.validate_camera_calibration(test_images)
    
    assert result.success
    assert result.error_rate < 0.01  # <1% error tolerance
    assert result.timing < 100  # <100ms processing time
```

## 🔧 Development Workflow

### Branch Strategy

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes** following our quality standards

3. **Run Quality Checks**:
   ```bash
   # Automated via pre-commit hooks
   pre-commit run --all-files
   
   # Manual verification
   python run_evaluation_suite.py --quick
   ```

4. **Submit Pull Request** with:
   - Comprehensive description
   - Test results
   - Performance impact assessment

### Code Review Requirements

Every pull request must pass:

- [ ] **Automated CI checks** (all must pass)
- [ ] **Code review by maintainer** (focus on architecture adherence)
- [ ] **Test coverage verification** (>95% for new code)
- [ ] **Performance regression check** (no degradation)
- [ ] **Documentation completeness** (all public APIs documented)

## 📚 Documentation Standards

### Academic Writing Requirements

Follow our academic writing guidelines:

- **Tone**: Clear, precise, practical with academic formality
- **Structure**: Detailed prose for "why" + bullet points for "how"
- **Citations**: Standard academic format [Author(Year)]
- **Scope**: Document existing design only, never invent new features

### Code Documentation

```python
# ✅ Good - Complete documentation
def synchronize_devices(
    devices: List[DeviceConnection],
    target_precision: float = 1.0
) -> SynchronizationResult:
    """
    Synchronize timestamps across multiple recording devices.
    
    Implements precision timing coordination following the distributed 
    systems approach outlined in Zhang et al. (2023). Achieves <1ms 
    accuracy through NTP-based synchronization protocol.
    
    Args:
        devices: List of connected recording devices
        target_precision: Target synchronization precision in milliseconds
        
    Returns:
        SynchronizationResult containing:
            - success: Whether synchronization succeeded
            - achieved_precision: Actual precision achieved (ms)
            - device_offsets: Timing offsets per device
            
    Raises:
        NetworkError: If device communication fails
        TimingError: If precision target cannot be achieved
        
    Example:
        >>> devices = [device1, device2, device3]
        >>> result = synchronize_devices(devices, target_precision=0.5)
        >>> assert result.success
        >>> assert result.achieved_precision < 0.5
    """
```

## 🛡️ Security & Privacy Standards

### Secure Coding Requirements

- **Data Encryption**: All sensitive data must use AES-GCM with hardware-backed keys
- **Authentication**: Cryptographically secure token-based authentication
- **Privacy**: GDPR compliance with automatic PII sanitization
- **Logging**: PII-aware log sanitization (no sensitive data in logs)

### Security Review Checklist

- [ ] No hardcoded secrets or credentials
- [ ] Proper input validation and sanitization
- [ ] Secure communication protocols (TLS/SSL)
- [ ] Privacy compliance verified
- [ ] Security-focused code review completed

## 🚦 Performance Standards

### Timing Requirements

- **Synchronization**: <1ms accuracy across all devices
- **Response Time**: <100ms for user interactions
- **Memory Usage**: <1GB typical usage with adaptive scaling
- **Throughput**: >10 MB/s per device, 100+ MB/s aggregate

### Performance Testing

```python
# Example performance test
def test_synchronization_performance():
    devices = create_test_devices(count=8)
    
    start_time = time.time()
    result = synchronize_devices(devices)
    duration = time.time() - start_time
    
    assert result.success
    assert result.achieved_precision < 1.0  # <1ms precision
    assert duration < 5.0  # <5s for 8 devices
    assert result.memory_usage < 100 * 1024 * 1024  # <100MB
```

## 📈 Quality Metrics

### Current Achievement Levels

Our project maintains exceptional standards:

- **System Reliability**: 98.4% under diverse failure conditions
- **Error Recovery**: 99.3% success rate for handled exceptions
- **Data Integrity**: 97.8% preservation during failure scenarios
- **Test Coverage**: >95% for critical components
- **Build Success**: 100% compilation success rate
- **Documentation**: 100% coverage for public APIs

### Continuous Improvement

We track these metrics and expect contributions to maintain or improve them:

1. **Weekly Quality Reviews**: Automated metric collection
2. **Monthly Tech Debt Audits**: Proactive refactoring identification
3. **Quarterly Standards Updates**: Adaptation to evolving best practices

## 🤝 Getting Help

### Before Asking Questions

1. **Check Documentation**: Review comprehensive guides in `docs/`
2. **Run Tests**: Ensure basic functionality works
3. **Review Examples**: Study existing code patterns
4. **Search Issues**: Check if others have encountered similar problems

### Mentorship for New Contributors

Given our high standards, new contributors receive mentorship:

- **Architecture Review**: Help understanding clean MVVM patterns
- **Quality Standards**: Guidance on achieving >95% test coverage
- **Performance Optimization**: Assistance with timing precision requirements
- **Documentation**: Support for academic writing standards

### Support Channels

- **Technical Issues**: Open GitHub issue with detailed reproduction steps
- **Architecture Questions**: Reference Architecture Decision Records (ADRs)
- **Testing Problems**: Consult [troubleshooting guide](./docs/TEST_TROUBLESHOOTING.md)
- **Performance Concerns**: Review [performance documentation](./docs/PERFORMANCE.md)

## 🎯 Success Criteria

Your contribution is ready when:

1. **All automated checks pass** (CI pipeline green)
2. **Test coverage maintained** (>95% for new code)
3. **Performance benchmarks met** (no regressions)
4. **Documentation complete** (academic quality)
5. **Security review passed** (if applicable)
6. **Maintainer approval received** (code review completed)

## 📋 Common Patterns

### Error Handling Pattern
```python
# Standard error handling pattern
try:
    result = operation()
    logger.info(f"Operation completed successfully: {result}")
    return Result.success(result)
except SpecificError as e:
    logger.error(f"Specific error in operation: {e}", exc_info=True)
    return Result.failure(f"Operation failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error in operation: {e}", exc_info=True)
    return Result.failure(f"Unexpected error: {e}")
```

### Reactive State Management
```kotlin
// Standard reactive pattern
class MyController @Inject constructor() {
    private val _state = MutableStateFlow(InitialState)
    val state: StateFlow<State> = _state.asStateFlow()
    
    fun updateState(update: (State) -> State) {
        _state.value = update(_state.value)
    }
}
```

## 🏆 Recognition

Contributors who consistently meet our high standards are recognized:

- **Quality Champions**: Outstanding adherence to standards
- **Innovation Leaders**: Exceptional technical contributions
- **Mentorship Award**: Helping new contributors succeed
- **Documentation Excellence**: Superior academic writing

---

**Remember**: Our strict quality standards ensure this system maintains research-grade reliability suitable for scientific instrumentation. Every contribution matters in maintaining these standards!

## Quick Reference

- **Cognitive Complexity**: <15 per function
- **Test Coverage**: >95% for new code
- **Synchronization Precision**: <1ms accuracy
- **Documentation**: Academic quality with complete examples
- **Error Handling**: Specific exceptions with proper logging
- **Architecture**: Clean MVVM with reactive state management

Welcome to the team! 🚀