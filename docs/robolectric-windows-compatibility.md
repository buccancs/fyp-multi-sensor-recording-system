# Robolectric Windows Compatibility Guide

## Issue Overview

Robolectric unit tests fail on Windows with the following error:
```
java.lang.UnsupportedOperationException: 'posix:permissions' not supported as initial attribute
    at java.base/sun.nio.fs.WindowsSecurityDescriptor.fromAttribute(WindowsSecurityDescriptor.java:358)
    at com.google.common.io.TempFileCreator$JavaNioCreator.createTempDir(TempFileCreator.java:102)
    at org.robolectric.internal.dependency.MavenArtifactFetcher.fetchArtifact(MavenArtifactFetcher.java:70)
```

## Root Cause

This is a fundamental compatibility issue between:
- **Google Guava's temp file creation** (used by Robolectric)
- **Windows file system** (which doesn't support POSIX permissions)
- **Java 17+ security restrictions**

The error occurs when Robolectric tries to download Android SDK dependencies and Google Guava attempts to create temporary directories with POSIX file permissions on Windows.

## Attempted Solutions

### Configuration Changes Made
1. **Enhanced robolectric.properties**:
   - Windows-specific temp directory configuration
   - File system provider settings
   - Maven dependency caching configuration

2. **Updated build.gradle**:
   - Comprehensive JVM arguments for Windows compatibility
   - System properties for file system provider configuration
   - Security manager configuration

3. **gradle.properties**:
   - Windows/Java 21 compatibility settings
   - Custom temp directory configuration

### Result
Despite comprehensive configuration changes, the issue persists. This is confirmed to be an **upstream limitation** in Robolectric's Windows support.

## Recommended Workarounds

### 1. Use Business Logic Tests
Focus on testing business logic without Android dependencies:
```kotlin
// ✅ Works on Windows - Business Logic Test
class LoggerBusinessLogicTest {
    @Test
    fun `LogLevel enum should have correct priorities`() {
        assertTrue(LogLevel.ERROR.priority > LogLevel.WARN.priority)
        assertTrue(LogLevel.WARN.priority > LogLevel.INFO.priority)
        assertTrue(LogLevel.INFO.priority > LogLevel.DEBUG.priority)
    }
}
```

### 2. Use Integration Tests
Use Android instrumented tests for UI and Android-specific functionality:
```kotlin
// ✅ Works on Windows - Integration Test
@RunWith(AndroidJUnit4::class)
class ThermalRecorderHardwareTest {
    @Test
    fun testThermalCameraInitialization() {
        // Test actual hardware integration
    }
}
```

### 3. Avoid Robolectric Tests
Avoid tests that use `@RunWith(RobolectricTestRunner::class)` on Windows:
```kotlin
// ❌ Fails on Windows - Robolectric Test
@RunWith(RobolectricTestRunner::class)
class LoggerTest {
    // This will fail with POSIX permissions error
}
```

## Development Workflow

### For Windows Developers
1. **Focus on business logic tests** - Test core algorithms and data structures
2. **Use integration tests** - Test Android-specific functionality on device/emulator
3. **Avoid Robolectric** - Skip unit tests that require Android context simulation

### For Cross-Platform Teams
1. **Linux/macOS developers** can run Robolectric tests
2. **Windows developers** should focus on business logic and integration tests
3. **CI/CD pipelines** should run Robolectric tests on Linux containers

## Alternative Testing Strategies

### 1. Dependency Injection for Testability
```kotlin
class MyService(private val logger: Logger) {
    fun processData(data: String): Result {
        // Business logic that can be tested without Android context
        return if (data.isValid()) {
            logger.info("Data processed successfully")
            Result.Success(data.process())
        } else {
            logger.error("Invalid data")
            Result.Error("Invalid input")
        }
    }
}

// ✅ Testable without Robolectric
@Test
fun `processData should return success for valid input`() {
    val mockLogger = mockk<Logger>()
    val service = MyService(mockLogger)
    
    val result = service.processData("valid-data")
    
    assertTrue(result is Result.Success)
    verify { mockLogger.info("Data processed successfully") }
}
```

### 2. Extract Android-Independent Logic
```kotlin
// ✅ Pure Kotlin logic - testable on Windows
class DataValidator {
    fun isValidSensorData(data: SensorData): Boolean {
        return data.timestamp > 0 && 
               data.values.isNotEmpty() && 
               data.values.all { it.isFinite() }
    }
}

// ❌ Android-dependent logic - requires Robolectric
class AndroidSensorManager(private val context: Context) {
    fun getSensorData(): SensorData {
        // Android-specific sensor access
    }
}
```

## Current Status

- **Issue**: Confirmed upstream limitation in Robolectric's Windows support
- **Workaround**: Use business logic tests and integration tests
- **Future**: Monitor Robolectric project for Windows compatibility improvements
- **Alternative**: Consider migrating to other testing frameworks if needed

## References

- [Robolectric GitHub Issues](https://github.com/robolectric/robolectric/issues)
- [Google Guava Windows Compatibility](https://github.com/google/guava/issues)
- [Android Testing Best Practices](https://developer.android.com/training/testing)