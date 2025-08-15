# New Minimal Python Implementation

This directory contains a **completely rebuilt** Python application that replaces the complex original implementation with a clean, minimal approach focused on core functionality.

## What Changed

### ❌ Removed (from original complex implementation)
- Complex GUI with multiple tabs and advanced features
- Extensive calibration system with OpenCV integration
- Shimmer sensor integration
- Multi-camera support with advanced configuration
- Complex session recovery and metadata systems
- Performance optimization modules
- Advanced error handling and logging systems
- Native backend wrappers
- Web UI components
- Stimulus presentation system

### ✅ Kept (essential functionality only)
- **JSON Socket Server** - Simple communication with Android devices
- **Basic GUI** - Clean PyQt interface for recording control
- **Session Management** - Simple session creation and device coordination
- **Network Communication** - Device registration and command broadcasting
- **Basic Utilities** - Essential helper functions

## Architecture

The new implementation follows a clean, modular structure:

```
PythonApp/
├── __init__.py          # Package initialization
├── main.py              # Application entry point
├── network/             # Network communication
│   └── __init__.py      # JsonSocketServer, AndroidDevice
├── session/             # Session management
│   └── __init__.py      # SessionManager, SessionConfig
├── gui/                 # User interface
│   ├── __init__.py
│   └── main_window.py   # MainWindow (PyQt)
└── utils/               # Utilities
    ├── __init__.py      # Basic helper functions
    ├── system_monitor.py
    ├── logging_config.py
    └── android_connection_detector.py
```

## Core Components

### 1. JsonSocketServer
- Accepts connections from Android devices
- Handles JSON message protocol
- Broadcasts commands to all connected devices
- Manages device lifecycle (connect/disconnect)

### 2. SessionManager
- Creates recording sessions with configuration
- Coordinates start/stop commands across devices
- Tracks session metadata and status
- Manages output directories

### 3. MainWindow (GUI)
- Tabbed interface: Recording, Devices, Settings
- Session configuration and control
- Device status monitoring
- Simple, clean design

## Usage

### Starting the Application
```bash
python PythonApp/main.py
```

### Basic Workflow
1. **Start Server**: Click "Start Server" in Devices tab
2. **Connect Devices**: Android devices connect to PC IP on port 8080
3. **Create Session**: Configure session name and settings
4. **Start Recording**: Begin coordinated recording across all devices
5. **Stop Recording**: End session and save data

### Dependencies
- PyQt6 or PyQt5 (GUI framework)
- numpy (data processing)
- opencv-python (basic computer vision)
- psutil (system monitoring)

## Testing

Run the integration tests:
```bash
python test_new_python_implementation.py
```

## Migration Notes

This is a **complete rewrite** that maintains compatibility with:
- Android app communication protocol (JSON over sockets)
- Basic session structure and file organization
- Core recording workflow

However, advanced features from the original implementation are not included in this minimal version. They can be added incrementally if needed.

## Benefits of Minimal Approach

1. **Maintainability**: Much simpler codebase (~500 lines vs ~5000+ lines)
2. **Reliability**: Fewer components means fewer failure points
3. **Performance**: Lightweight with faster startup and lower resource usage
4. **Understandability**: Clear, focused modules that are easy to understand
5. **Extensibility**: Clean architecture makes it easy to add features incrementally

## Future Extensions

If needed, features can be added back incrementally:
- Camera calibration system
- Shimmer sensor integration  
- Advanced GUI features
- Performance optimization
- Web interface
- Advanced error handling

The minimal implementation provides a solid foundation for these additions while keeping the core system simple and reliable.