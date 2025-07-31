# Session Logging User Manual

**Date:** 2025-07-30  
**Milestone:** 3.8 - Session Metadata Logging and Review  
**Author:** Multi-Sensor Recording System Team

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Session Management](#session-management)
4. [Event Logging](#event-logging)
5. [Post-Session Review](#post-session-review)
6. [Error Recovery](#error-recovery)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

## Overview

The Session Logging system provides comprehensive metadata logging and review capabilities for the Multi-Sensor Recording System. It captures all session events, provides real-time feedback, and enables detailed post-session analysis.

### Key Features

- **Comprehensive Event Logging**: Captures all session events with precise timestamps
- **Real-Time UI Feedback**: Live log viewer with immediate event display
- **Post-Session Review**: Detailed session analysis with file management
- **Error Recovery**: Automatic crash recovery and corrupted file repair
- **Thread-Safe Operations**: Concurrent logging from multiple components
- **JSON Format**: Structured, human-readable log files

## Getting Started

### System Requirements

- Python 3.7 or higher
- PyQt5 framework
- Sufficient disk space for session logs and recordings
- Write permissions to the recordings directory

### Initial Setup

The session logging system is automatically initialized when the application starts. No manual configuration is required for basic operation.

```python
# Session logging is automatically available through the global instance
from session.session_logger import get_session_logger

logger = get_session_logger()
```

### Basic Usage

1. **Start the Application**: Launch the Multi-Sensor Recording System Controller
2. **Begin Session**: Click "Start Session" to begin recording and logging
3. **Monitor Events**: View real-time events in the Session Log panel
4. **End Session**: Click "Stop Session" to complete recording
5. **Review Session**: Choose to review session data when prompted

## Session Management

### Starting a Session

Sessions are automatically started when you begin recording:

1. Connect your devices (Android phones, webcams, etc.)
2. Click the **"Start Session"** button in the toolbar
3. The system will:
   - Create a unique session ID
   - Initialize logging
   - Create a session folder
   - Begin capturing events

### Session Information

Each session includes:
- **Session ID**: Unique identifier (e.g., `session_20250730_143022`)
- **Start/End Times**: Precise timestamps with millisecond accuracy
- **Device List**: All connected devices and their capabilities
- **Event Timeline**: Chronological list of all session events
- **File Inventory**: All files created during the session

### Session Folders

Sessions are organized in individual folders:
```
recordings/
├── session_20250730_143022/
│   ├── session_20250730_143022_log.json
│   ├── session_metadata.json
│   ├── webcam_video.mp4
│   ├── phone1_rgb.mp4
│   ├── phone1_thermal.mp4
│   └── calibration_files/
└── session_20250730_144530/
    └── ...
```

## Event Logging

### Event Types

The system logs the following event types:

#### Session Events
- **session_start**: Session initialization
- **session_end**: Session completion

#### Device Events
- **device_connected**: Device connection
- **device_disconnected**: Device disconnection
- **device_ack**: Command acknowledgment from device

#### Recording Events
- **start_record**: Recording start command
- **stop_record**: Recording stop command
- **file_received**: File transfer completion

#### Stimulus Events
- **stimulus_play**: Stimulus playback start
- **stimulus_stop**: Stimulus playback end
- **marker**: User-generated event marker

#### Error Events
- **error**: System errors and warnings

### Event Structure

Each event includes:
```json
{
  "event": "stimulus_play",
  "time": "14:30:22.123",
  "timestamp": "2025-07-30T14:30:22.123456",
  "media": "video1.mp4",
  "device": "pc_webcam"
}
```

### Real-Time Monitoring

The **Session Log** panel provides real-time event monitoring:

1. **Access**: View → Show Log (or use the toolbar toggle)
2. **Features**:
   - Millisecond-precision timestamps
   - Color-coded event types
   - Auto-scrolling to latest events
   - Monospace font for clarity
   - Dark theme for reduced eye strain

## Post-Session Review

### Accessing Session Review

After completing a session, you'll be prompted to review the session data:

1. Click **"Yes"** when asked to review session data
2. The Session Review Dialog will open automatically
3. Alternatively, you can access previous sessions through the File menu

### Review Dialog Features

The Session Review Dialog provides four main tabs:

#### Files Tab
- **File List**: All files created during the session
- **File Details**: Size, type, and modification information
- **File Actions**:
  - Double-click to open files with default applications
  - "Open File" button for selected file
  - "Open Folder" button to access session directory

#### Statistics Tab
- **Session Metrics**: Duration, device count, event count
- **File Statistics**: Total files, combined size
- **Event Breakdown**: Count by event type
- **Device Information**: Connected devices and capabilities

#### Events Tab
- **Event Timeline**: Chronological list of all events
- **Color Coding**:
  - Blue: Session start/end events
  - Green: Stimulus events
  - Yellow: User markers
  - Red: Error events
- **Detailed Information**: Full event data with timestamps

#### Calibration Tab (if applicable)
- **Calibration Files**: List of captured calibration images
- **File Status**: Verification of file existence and size
- **Results**: Calibration outcomes and quality metrics

### Export Functionality

Export session data for external analysis:

1. Click **"Export Session Data"** in the review dialog
2. A comprehensive JSON summary will be created
3. The export includes:
   - Complete session information
   - File inventory with metadata
   - Export timestamp for tracking

## Error Recovery

### Automatic Recovery

The system includes robust error recovery mechanisms:

#### Crash Recovery
- **Immediate Disk Writes**: Events are written immediately to prevent data loss
- **Valid JSON Maintenance**: Log files remain valid even during crashes
- **Session Recovery**: Incomplete sessions are automatically detected and recovered

#### File Corruption Handling
- **Automatic Detection**: Background scanning for corrupted files
- **Intelligent Repair**: Attempts to repair corrupted JSON files
- **Backup Creation**: Corrupted files are backed up before repair

#### Disk Space Management
- **Space Monitoring**: Continuous monitoring of available disk space
- **Automatic Cleanup**: Old sessions are automatically removed when space is low
- **Backup Options**: Sessions can be backed up before cleanup

### Manual Recovery

If automatic recovery fails, you can manually recover sessions:

1. **Locate Session Folder**: Navigate to the recordings directory
2. **Check Log File**: Open the `*_log.json` file in a text editor
3. **Verify JSON Format**: Ensure the file is valid JSON
4. **Contact Support**: If recovery is not possible, contact technical support

## Advanced Features

### Custom Markers

Add custom event markers during sessions:

1. **During Stimulus Playback**: Click the "Mark Event" button
2. **Automatic Labeling**: Markers are automatically numbered
3. **Stimulus Correlation**: Markers include stimulus timeline position
4. **Multiple Markers**: Add as many markers as needed

### Performance Monitoring

Monitor system performance during sessions:

- **Event Rate**: Track events per second
- **Memory Usage**: Monitor memory consumption
- **Disk I/O**: Track file write performance
- **Thread Safety**: Concurrent logging from multiple sources

### Integration Points

The session logging system integrates with:

- **Device Manager**: Logs all device interactions
- **Stimulus Controller**: Tracks media playback and markers
- **Webcam Capture**: Records PC webcam events
- **Calibration System**: Logs calibration procedures
- **Error Handling**: Captures and categorizes all errors

## Troubleshooting

### Common Issues

#### Session Log Not Visible
**Problem**: The session log panel is not visible  
**Solution**: 
1. Go to View → Show Log
2. Or click the log toggle button in the toolbar
3. The panel should appear at the bottom of the window

#### Events Not Being Logged
**Problem**: Events are not appearing in the log  
**Solution**:
1. Check that a session is active (session started)
2. Verify the recordings directory is writable
3. Check available disk space
4. Restart the application if necessary

#### Session Review Dialog Won't Open
**Problem**: Cannot open session review after completion  
**Solution**:
1. Check that the session folder exists in recordings directory
2. Verify the log file is not corrupted
3. Try opening the session folder manually
4. Check file permissions

#### Poor Performance During Logging
**Problem**: Application becomes slow during intensive logging  
**Solution**:
1. Check available system memory
2. Verify disk space and I/O performance
3. Reduce the number of concurrent devices
4. Consider using an SSD for better performance

#### Corrupted Log Files
**Problem**: Log files appear corrupted or unreadable  
**Solution**:
1. The system will automatically attempt repair
2. Check for `.corrupted` backup files
3. Use the recovery manager to restore sessions
4. Contact support for manual recovery assistance

### Error Messages

#### "No active session to log event"
- **Cause**: Attempting to log events without starting a session
- **Solution**: Start a session before performing recording operations

#### "Failed to write session log to disk"
- **Cause**: Insufficient disk space or permission issues
- **Solution**: Check disk space and file permissions

#### "Session folder could not be located"
- **Cause**: Session folder was moved or deleted
- **Solution**: Check the recordings directory and restore from backup if available

### Performance Optimization

#### For Large Sessions
- Ensure sufficient RAM (8GB+ recommended)
- Use SSD storage for better I/O performance
- Monitor disk space regularly
- Consider session segmentation for very long recordings

#### For Multiple Devices
- Use a dedicated network for device communication
- Ensure stable power supply for all devices
- Monitor network bandwidth usage
- Consider device prioritization for critical recordings

## API Reference

### SessionLogger Class

#### Core Methods

```python
def start_session(session_name: Optional[str] = None, 
                 devices: Optional[List[Dict]] = None) -> Dict:
    """Start a new session and initialize logging."""

def log_event(event_type: str, details: Optional[Dict] = None) -> None:
    """Log an event with timestamp and details."""

def end_session() -> Optional[Dict]:
    """End the current session and finalize logging."""
```

#### Event Logging Methods

```python
def log_device_connected(device_id: str, device_type: str = "unknown", 
                        capabilities: Optional[List[str]] = None) -> None:
    """Log device connection event."""

def log_recording_start(devices: List[str], 
                       session_id: Optional[str] = None) -> None:
    """Log recording start command."""

def log_stimulus_play(media_name: str, 
                     media_path: Optional[str] = None) -> None:
    """Log stimulus playback start."""

def log_marker(label: str, stim_time: Optional[str] = None) -> None:
    """Log user marker event."""

def log_error(error_type: str, message: str, 
             device_id: Optional[str] = None) -> None:
    """Log error event."""
```

#### Utility Methods

```python
def get_current_session() -> Optional[Dict]:
    """Get current session information."""

def is_session_active() -> bool:
    """Check if a session is currently active."""
```

### SessionReviewDialog Class

#### Constructor

```python
def __init__(self, session_data: Dict, session_folder: str, parent=None):
    """Initialize session review dialog."""
```

#### Utility Functions

```python
def show_session_review_dialog(session_data: Dict, session_folder: str, 
                              parent=None) -> Optional[SessionReviewDialog]:
    """Convenience function to show session review dialog."""
```

### Global Functions

```python
def get_session_logger() -> SessionLogger:
    """Get the global session logger instance."""

def reset_session_logger() -> None:
    """Reset the global session logger instance."""
```

## Best Practices

### Session Management
1. **Always start sessions** before beginning recording operations
2. **Use descriptive session names** when possible
3. **Monitor disk space** regularly, especially for long sessions
4. **End sessions properly** to ensure data integrity

### Event Logging
1. **Log significant events** to maintain comprehensive records
2. **Use appropriate event types** for better categorization
3. **Include relevant details** in event data
4. **Avoid excessive logging** that might impact performance

### File Management
1. **Organize sessions** by date or experiment type
2. **Back up important sessions** to external storage
3. **Clean up old sessions** regularly to free disk space
4. **Verify file integrity** after important sessions

### Performance
1. **Monitor system resources** during intensive sessions
2. **Use SSD storage** for better I/O performance
3. **Limit concurrent operations** when possible
4. **Regular maintenance** of the recordings directory

## Support and Resources

### Documentation
- **Architecture Documentation**: `docs/session_logger_architecture.md`
- **API Documentation**: Inline code documentation
- **Troubleshooting Guide**: This document, Section 8

### Technical Support
- **Issue Reporting**: Use the project's issue tracking system
- **Log Files**: Include session logs and recovery logs when reporting issues
- **System Information**: Provide OS, Python version, and hardware specifications

### Community Resources
- **User Forums**: Community discussions and tips
- **Example Code**: Sample implementations and integrations
- **Best Practices**: Community-contributed guidelines and recommendations

---

*This manual covers the core functionality of the Session Logging system. For advanced customization and development information, refer to the technical documentation and API reference.*
