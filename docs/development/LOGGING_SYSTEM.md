# Comprehensive Logging System

This document describes the comprehensive logging system implemented across the Multi-Sensor Recording System for both Python and Android components.

## Overview

The logging system provides:
- **Centralized configuration** for consistent logging across all modules
- **Multiple output destinations** (console and files) 
- **Log rotation** to prevent disk space issues
- **Structured formatting** with timestamps and context
- **Performance tracking** and debugging utilities
- **Thread-safe operations** for concurrent environments

## Python Logging (`PythonApp/src/utils/logging_config.py`)

### Features

- **Centralized Configuration**: Single point of control for all logging settings
- **Color-coded Console Output**: Different colors for different log levels
- **File Rotation**: Automatic rotation when files exceed size limits (10MB application, 5MB errors)
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Exception Tracking**: Full stack traces for debugging
- **Performance Decorators**: Automatic function entry/exit logging

### Usage

```python
from utils.logging_config import get_logger

# Get logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General application flow")
logger.warning("Something unexpected happened")
logger.error("An error occurred", exc_info=True)
logger.critical("System is in critical state")
```

### Configuration

Set environment variable `MSR_LOG_LEVEL` to control logging level:
```bash
export MSR_LOG_LEVEL=DEBUG  # Show all logs
export MSR_LOG_LEVEL=INFO   # Show INFO and above (default)
export MSR_LOG_LEVEL=ERROR  # Show only errors
```

### Log Files

Logs are written to `/logs/` directory:
- `application.log`: All application logs with rotation
- `errors.log`: Error and critical logs only

## Android Logging (`AndroidApp/src/main/java/.../util/AppLogger.kt`)

### Features

- **Structured Log Tags**: Consistent tagging with `MSR_` prefix
- **Thread Information**: Automatic thread name and timestamp inclusion
- **Specialized Logging Methods**: For network, recording, sensor, and file operations
- **Performance Timing**: Built-in timing utilities
- **Memory Usage Tracking**: Monitor memory consumption
- **Log Level Control**: Runtime enable/disable of debug and verbose logging

### Usage

```kotlin
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

class MyClass {
    fun someMethod() {
        // Using static methods
        AppLogger.i("MyClass", "Method started")
        AppLogger.logRecording("MyClass", "start recording", "camera_front")
        
        // Using extension functions
        logI("This is an info message")
        logE("This is an error message")
        
        // Performance timing
        AppLogger.startTiming("MyClass", "video_processing")
        // ... do work ...
        AppLogger.endTiming("MyClass", "video_processing")
    }
}
```

### Specialized Logging Methods

```kotlin
// Lifecycle events
AppLogger.logLifecycle("MainActivity", "onCreate")

// Network operations
AppLogger.logNetwork("NetworkClient", "HTTP GET", "https://api.example.com", "200 OK")

// Recording operations
AppLogger.logRecording("CameraRecorder", "start recording", "1920x1080@30fps")

// Sensor data
AppLogger.logSensor("ShimmerDevice", "reading", "GSR", "value=1.23")

// File operations
AppLogger.logFile("FileManager", "save", "video.mp4", 50*1024*1024L) // 50MB

// State changes
AppLogger.logStateChange("CameraRecorder", "IDLE", "RECORDING")

// Memory usage
AppLogger.logMemoryUsage("MainActivity", "After camera initialization")
```

## Integration with Existing Systems

### SessionLogger Integration

The new logging system works alongside the existing `SessionLogger`:
- **SessionLogger**: Handles session-specific events and metadata
- **AppLogger**: Handles general application logging and debugging

Both systems can be used together without conflicts.

### Example Integration

```python
from utils.logging_config import get_logger
from session.session_logger import get_session_logger

class MyRecordingManager:
    def __init__(self):
        self.logger = get_logger(__name__)          # Application logging
        self.session_logger = get_session_logger()  # Session events
    
    def start_recording(self, session_id):
        self.logger.info(f"Starting recording for session {session_id}")
        self.session_logger.log_recording_start(["device1", "device2"], session_id)
        # ... recording logic ...
        self.logger.debug("Recording started successfully")
```

## Log Levels and When to Use Them

### DEBUG
- Function entry/exit
- Variable values during troubleshooting
- Detailed state information
- **Use sparingly** - can be verbose

### INFO  
- Application startup/shutdown
- Major operation completion
- User actions and their results
- **Primary level** for operational awareness

### WARNING
- Unexpected but recoverable conditions
- Deprecated feature usage
- Configuration issues that don't stop execution
- **Indicates potential issues**

### ERROR
- Operation failures that affect functionality
- Exception handling
- Invalid user input
- **Requires attention** but app continues

### CRITICAL
- System failures
- Unrecoverable errors
- Security issues
- **Immediate attention required**

## Performance Considerations

### Python
- Log files are rotated automatically to prevent disk issues
- Console output can be disabled for production
- File handlers use buffering for performance

### Android
- Debug/verbose logging can be disabled in production
- Structured logging reduces parsing overhead
- Memory usage tracking helps identify leaks

## Testing

### Python Tests
```bash
cd PythonApp
python3 test_logging.py           # Basic logging test
python3 test_integration_logging.py  # Comprehensive integration test
```

### Android Tests
The `LoggingTest.kt` utility can be called from any Android activity:
```kotlin
LoggingTest.runLoggingTest(this)
```

## Configuration Files

### Python Logging Levels
Create `.env` file or set environment variables:
```bash
MSR_LOG_LEVEL=DEBUG
MSR_LOG_DIR=/custom/log/path
```

### Android Logging Control
```kotlin
// Enable/disable logging levels at runtime
AppLogger.setDebugEnabled(true)
AppLogger.setVerboseEnabled(false)
```

## Best Practices

1. **Use appropriate log levels** - Don't log everything as INFO
2. **Include context** - Add relevant parameters and state information
3. **Avoid logging sensitive data** - Passwords, tokens, personal information
4. **Use structured logging** - Consistent format makes parsing easier
5. **Log exceptions with stack traces** - Use `exc_info=True` in Python, provide `Throwable` in Android
6. **Monitor log file sizes** - Especially in long-running applications
7. **Use performance logging** - Track slow operations and memory usage

## Troubleshooting

### Python Issues
- **Logs not appearing**: Check log level settings
- **File permission errors**: Ensure write access to log directory
- **Import errors**: Verify `utils/logging_config.py` is in Python path

### Android Issues  
- **Logs not visible**: Use `adb logcat` or Android Studio Logcat viewer
- **Performance impact**: Disable debug logging in release builds
- **Tag filtering**: Use `adb logcat MSR_*:V *:S` to show only app logs

### Viewing Logs

#### Python Logs
```bash
# View live application logs
tail -f logs/application.log

# View only errors  
tail -f logs/errors.log

# Filter by log level
grep "ERROR" logs/application.log
```

#### Android Logs
```bash
# View live Android logs (all MSR tags)
adb logcat MSR_*:V *:S

# View specific component
adb logcat MSR_MainActivity:V *:S

# Save logs to file
adb logcat MSR_*:V *:S > android_logs.txt
```

This comprehensive logging system ensures that you can "fully follow what's happening" in both Python and Android components of the Multi-Sensor Recording System.