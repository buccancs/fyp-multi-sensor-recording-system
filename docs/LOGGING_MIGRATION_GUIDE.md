# Logging System Migration Guide

## Overview

The Multi-Sensor Recording System has been updated with a modern, centralized logging system that provides structured logging, performance monitoring, file rotation, and enhanced debugging capabilities.

## New Logging System Features

### 🎯 Centralized Configuration
- Single import: `from utils.logging_config import get_logger`
- Auto-initialization with sensible defaults
- Consistent formatting across all modules

### 📊 Enhanced Capabilities
- **Structured JSON logging** for machine parsing
- **Performance monitoring** with built-in timers
- **Memory usage tracking** (when psutil available)
- **Colored console output** for better readability
- **File rotation** with multiple log files
- **Log export** functionality for analysis
- **Automatic cleanup** of old logs

### 📁 Log File Structure
```
PythonApp/logs/
├── application.log     # General application logs
├── errors.log         # Error-level logs only
├── structured.log     # JSON structured logs
└── exports/           # Exported log files
```

## Migration Instructions

### ✅ Recommended Usage (New)
```python
from utils.logging_config import get_logger

class MyClass:
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def my_method(self):
        self.logger.info("Operation started")
        try:
            # Your code here
            self.logger.debug("Debug information")
        except Exception as e:
            self.logger.error(f"Operation failed: {e}", exc_info=True)
```

### ❌ Old Usage (Deprecated)
```python
import logging

class MyClass:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def my_method(self):
        logging.basicConfig(...)  # Don't do this anymore
```

## Advanced Features

### Performance Monitoring
```python
from utils.logging_config import performance_timer, AppLogger

# Using decorator
@performance_timer("database_query")
def fetch_data():
    pass

# Using manual timing
timer_id = AppLogger.start_performance_timer("complex_operation")
# ... do work ...
duration = AppLogger.end_performance_timer(timer_id)
```

### Memory Monitoring
```python
from utils.logging_config import log_memory_usage, AppLogger

@log_memory_usage("data_processing")
def process_large_dataset():
    pass

# Manual memory logging
AppLogger.log_memory_usage("before_operation")
```

### Function Entry/Exit Logging
```python
from utils.logging_config import log_function_entry, log_method_entry

@log_function_entry
def my_function():
    pass

class MyClass:
    @log_method_entry  
    def my_method(self):
        pass
```

### Log Export and Cleanup
```python
from utils.logging_config import AppLogger
from datetime import datetime, timedelta

# Export logs for analysis
start_date = datetime.now() - timedelta(days=7)
end_date = datetime.now()
export_path = AppLogger.export_logs(start_date, end_date, 'json')

# Cleanup old logs (30 days retention)
cleanup_report = AppLogger.cleanup_old_logs(retention_days=30)
```

## Configuration

### Runtime Log Level Changes
```python
from utils.logging_config import AppLogger

# Change log level at runtime
AppLogger.set_level("DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Environment Variables
```bash
# Set log level via environment
export MSR_LOG_LEVEL=DEBUG
```

## Integration with Session Logger

The session logger has been enhanced to integrate with the new logging system:

```python
from session.session_logger import get_session_logger

session_logger = get_session_logger()
session_info = session_logger.start_session("my_experiment")
# Session events are now also logged to the main logging system
```

## Migration Status

### ✅ Migrated Modules
- `src/application.py`
- `src/production/deployment_automation.py`
- `src/production/performance_benchmark.py`
- `src/production/security_scanner.py`
- `src/shimmer_manager.py`
- `src/gui/main_controller.py`
- `src/gui/common_components.py`
- `src/session/session_logger.py`

### 📝 Deprecated Modules
- `src/utils/logger.py` - Use `utils.logging_config` instead

## Best Practices

1. **Use structured logging** for important events:
   ```python
   logger.info("User action completed", extra={
       'user_id': user_id,
       'action': 'calibration',
       'duration_ms': duration
   })
   ```

2. **Include context** in error messages:
   ```python
   logger.error(f"Failed to connect to device {device_id}", exc_info=True)
   ```

3. **Use appropriate log levels**:
   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General application flow
   - `WARNING`: Something unexpected happened
   - `ERROR`: Serious problem occurred
   - `CRITICAL`: Very serious error occurred

4. **Leverage performance monitoring** for optimization:
   ```python
   @performance_timer("calibration_process")
   def run_calibration():
       pass
   ```

## Testing

The logging system includes comprehensive integration tests:

```bash
cd PythonApp
python test_integration_logging.py
```

This validates:
- ✅ Centralized logging configuration
- ✅ Multiple module integration
- ✅ Different log levels and formatting
- ✅ Exception handling with stack traces
- ✅ Performance and memory logging
- ✅ Log file creation and rotation

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure to use `from utils.logging_config import get_logger`
2. **Log files not created**: Check write permissions in the PythonApp directory
3. **Performance monitoring**: Install `psutil` for memory monitoring features

### Debug Information

Check active timers:
```python
from utils.logging_config import AppLogger
active_timers = AppLogger.get_active_timers()
print(active_timers)
```

View log directory:
```python
from utils.logging_config import AppLogger
log_dir = AppLogger.get_log_dir()
print(f"Logs are stored in: {log_dir}")
```

## Benefits of Migration

- 🎯 **Consistency**: Unified logging across all modules
- 📊 **Visibility**: Better debugging and monitoring capabilities
- 🔧 **Maintainability**: Centralized configuration and management
- 📈 **Performance**: Built-in performance monitoring
- 🛡️ **Reliability**: Automatic log rotation and cleanup
- 📋 **Analysis**: Structured logs for better analysis tools