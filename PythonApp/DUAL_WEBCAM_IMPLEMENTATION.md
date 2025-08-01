# Dual Webcam Recording System - Logger and Launch Script Implementation

## Overview

This implementation provides comprehensive logging functionality and enhanced launch script integration for the dual webcam recording system. The system includes advanced logging capabilities with file rotation, structured logging, performance monitoring, and a complete dual webcam main window interface.

## Features Implemented

### 1. Comprehensive Logging System (`logger.py`)

#### Core Features:
- **Multi-level Logging**: Support for DEBUG, INFO, WARNING, ERROR, and CRITICAL levels
- **File Rotation**: Automatic log file rotation with configurable size limits and backup counts
- **Structured Logging**: JSON-formatted logs with additional metadata for machine parsing
- **Performance Monitoring**: Built-in timing and memory usage tracking
- **Categorized Logging**: Separate loggers for application, network, calibration, and performance events

#### Key Components:
- `LogLevel` enum for consistent log level management
- `LoggerManager` class with comprehensive logging capabilities
- Specialized logging methods for different system components:
  - `log_performance()` - Performance metrics with optional psutil integration
  - `log_network_event()` - Network-related events with device tracking
  - `log_calibration_event()` - Calibration process monitoring
  - `log_structured()` - General structured logging with custom metadata

#### Advanced Features:
- **Log Export**: Export logs in JSON, CSV, or TXT formats with date filtering
- **Log Cleanup**: Automatic cleanup and compression of old log files
- **Memory Monitoring**: Optional integration with psutil for memory usage tracking
- **Thread-safe Operations**: All logging operations are thread-safe

### 2. Enhanced Logging Configuration (`logging_config.py`)

#### Advanced Features:
- **Structured JSON Formatter**: Outputs machine-readable JSON logs
- **Colored Console Output**: Color-coded log levels for improved readability
- **Performance Monitoring**: Built-in timer system for operation tracking
- **Decorators**: Function and method entry/exit logging decorators
- **Memory Usage Logging**: Memory usage monitoring with decorators
- **Exception Context Logging**: Automatic exception logging with context

#### Key Components:
- `AppLogger` class for centralized logging management
- `PerformanceMonitor` for timing operations
- `ColoredFormatter` for enhanced console output
- Multiple decorators for automated logging:
  - `@performance_timer` - Automatic function timing
  - `@log_function_entry` - Function entry/exit logging
  - `@log_memory_usage` - Memory usage monitoring

### 3. Dual Webcam Main Window (`dual_webcam_main_window.py`)

#### Features:
- **Dual Camera Preview**: Real-time preview from both cameras simultaneously
- **Camera Settings Panel**: Configurable camera indices, resolution, and frame rate
- **Recording Controls**: Start/stop recording with visual feedback
- **Performance Monitoring**: Real-time sync quality and frame rate display
- **Status Monitoring**: Connection status and FPS for each camera
- **Settings Persistence**: Apply initial settings from launch script

#### UI Components:
- `CameraPreviewWidget` - Individual camera preview with status
- `DualWebcamSettingsPanel` - Configuration panel for camera settings
- Real-time performance monitoring with progress bars
- Color-coded status indicators and recording controls

### 4. Enhanced Launch Script (`launch_dual_webcam.py`)

#### Improvements:
- **Camera Configuration Passing**: Properly passes camera indices and settings to main window
- **Comprehensive Argument Parsing**: Support for custom camera indices, resolution, and FPS
- **System Testing Integration**: Built-in camera testing before launching main application
- **Logging Integration**: Full integration with centralized logging system
- **Error Handling**: Robust error handling with informative messages

#### Command Line Options:
```bash
python launch_dual_webcam.py [options]

Options:
  --test-only           Test webcam access without starting full application
  --cameras N,M         Specify camera indices (default: 0,1)
  --resolution WxH      Set recording resolution (default: 3840x2160)
  --fps N              Set recording FPS (default: 30)
  --log-level LEVEL    Set logging level (DEBUG, INFO, WARNING, ERROR)
```

### 5. Enhanced Dual Webcam Capture (`dual_webcam_capture.py`)

#### Improvements:
- **Flexible Camera Testing**: `test_dual_webcam_access()` now supports custom camera indices
- **Additional Methods**: Added missing methods required by the main window:
  - `get_latest_frame()` - Get latest synchronized frame data
  - `get_camera_fps()` - Get FPS for individual cameras
  - `start_capture()` / `stop_capture()` - Simplified capture control
- **Improved Error Handling**: Better error reporting and logging integration

## Usage Examples

### Basic Launch
```bash
# Launch with default settings (cameras 0,1 at 4K/30fps)
python launch_dual_webcam.py

# Test camera access only
python launch_dual_webcam.py --test-only

# Custom configuration
python launch_dual_webcam.py --cameras 2,3 --resolution 1920x1080 --fps 60
```

### Programmatic Usage
```python
from utils.logging_config import get_logger, performance_timer
from utils.logger import get_logger_manager, LogLevel
from gui.dual_webcam_main_window import DualWebcamMainWindow

# Get logger
logger = get_logger(__name__)

# Use performance monitoring
@performance_timer("camera_operation")
def setup_cameras():
    # Camera setup code
    pass

# Structured logging
logger_manager = get_logger_manager()
logger_manager.log_structured(
    "camera_system",
    LogLevel.INFO,
    "Camera initialized",
    camera_id=0,
    resolution="1920x1080"
)

# Create main window with settings
settings = {
    'camera1_index': 0,
    'camera2_index': 1,
    'width': 1920,
    'height': 1080,
    'fps': 30
}

main_window = DualWebcamMainWindow(
    camera_indices=[0, 1],
    initial_settings=settings
)
```

## Testing

### Comprehensive Test Suite
- **Unit Tests**: Core functionality testing without external dependencies
- **Integration Tests**: Full system testing with mocked dependencies
- **Performance Tests**: Timing and memory usage validation
- **Error Handling Tests**: Failure scenario testing

### Test Files:
- `test_simplified_integration.py` - Core logic tests (no external dependencies)
- `test_dual_webcam_integration.py` - Full integration tests (requires dependencies)
- `test_logging.py` - Basic logging functionality test

### Running Tests:
```bash
# Run simplified tests (no external dependencies required)
python test_simplified_integration.py

# Run basic logging test
python test_logging.py

# Run full integration tests (requires PyQt5, OpenCV)
python test_dual_webcam_integration.py
```

## Configuration

### Log Configuration
Logging can be configured via JSON file at `config/logging.json`:
```json
{
    "log_directory": "logs",
    "max_file_size_mb": 10,
    "backup_count": 5
}
```

### Default Log Structure
```
logs/
├── application/
│   └── application.log
├── network/
│   └── network.log
├── calibration/
│   └── calibration.log
├── performance/
│   └── performance.log
└── exports/
    └── [exported_logs]
```

## Performance Considerations

### Logging Performance
- **Asynchronous Logging**: All file operations are non-blocking
- **Structured Data**: Efficient JSON serialization with fallback handling
- **Memory Management**: Automatic cleanup of old logs and compression
- **Thread Safety**: All operations are thread-safe for multi-threaded applications

### Camera Performance
- **Optimized for Logitech Brio**: Specific optimizations for 4K30 recording
- **Synchronization**: Frame-level synchronization between cameras
- **Memory Efficient**: Minimal frame buffering to reduce memory usage
- **Error Recovery**: Automatic recovery from camera disconnections

## Future Enhancements

### TODO Items:
- [ ] Frame conversion utilities for preview display (QPixmap conversion)
- [ ] Network synchronization protocol implementation
- [ ] Advanced calibration integration
- [ ] Recording session management
- [ ] Real-time processing pipeline integration

### Potential Improvements:
- Integration with external logging services (e.g., ELK stack)
- Advanced performance analytics and reporting
- Remote camera monitoring and control
- Automated camera discovery and configuration
- Advanced synchronization algorithms

## Dependencies

### Required:
- Python 3.9+
- PyQt5 (for GUI components)
- OpenCV (for camera operations)

### Optional:
- psutil (for enhanced memory monitoring)
- Additional camera drivers as needed

## Error Handling

The system includes comprehensive error handling at multiple levels:
- **Camera Access Errors**: Detailed error messages for camera connection issues
- **Configuration Errors**: Validation and helpful error messages for invalid settings
- **Logging Errors**: Fallback mechanisms for logging failures
- **GUI Errors**: Graceful degradation for UI component failures

All errors are logged with appropriate context and user-friendly messages are displayed when appropriate.