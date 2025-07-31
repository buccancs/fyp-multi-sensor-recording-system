# Data Structure and Storage Documentation

## Overview

The Multi-Sensor Synchronized Recording System uses a comprehensive, hierarchical file structure to organize and store data from multiple sensors and devices. This document provides complete documentation of how data is saved, organized, and named throughout the system.

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [File Naming Conventions](#file-naming-conventions)
3. [Data Schemas](#data-schemas)
4. [Data Types and Organization](#data-types-and-organization)
5. [User Guide](#user-guide)
6. [Developer Guidelines](#developer-guidelines)

## Directory Structure

### Root Data Organization

```
project-root/
├── PythonApp/
│   ├── recordings/                    # Main session recordings
│   │   ├── session_YYYYMMDD_HHMMSS/   # Individual session folders
│   │   └── ...
│   ├── test_recordings/               # Test session data
│   ├── test_videos/                   # Test video processing outputs
│   └── test_logs/                     # Test logging outputs
├── calibration_data/                  # Camera calibration sessions
│   ├── session_name_YYYYMMDD_HHMMSS/  # Calibration session folders
│   └── ...
├── AndroidApp/                        # Android app generated data
│   └── (device-specific storage)
└── external/                          # External library data
```

### Session Folder Structure

Each recording session creates a dedicated folder with the following internal structure:

```
session_YYYYMMDD_HHMMSS/
├── session_metadata.json             # Core session information
├── session_YYYYMMDD_HHMMSS_log.json  # Detailed event logging
├── devices/                          # Device-specific data
│   ├── device_id/                    # Individual device folders
│   │   ├── rgb_videos/               # RGB video recordings
│   │   ├── thermal_videos/           # Thermal camera recordings  
│   │   ├── sensor_data/              # GSR/physiological data
│   │   └── calibration/              # Device calibration data
│   └── ...
├── webcam/                           # PC webcam recordings
│   ├── webcam_1_YYYYMMDD_HHMMSS.mp4  # Webcam video files
│   └── webcam_2_YYYYMMDD_HHMMSS.mp4
├── stimulus/                         # Stimulus presentation data
│   ├── stimulus_log.json             # Stimulus timing data
│   └── media_files/                  # Stimulus media copies
├── processing/                       # Post-processing outputs
│   ├── hand_segmentation/            # Hand tracking results
│   ├── synchronization/              # Multi-device sync data
│   └── analysis/                     # Analysis results
└── exports/                          # Exported/converted data
    ├── csv/                          # CSV exports
    ├── matlab/                       # MATLAB format exports
    └── summary/                      # Summary reports
```

## File Naming Conventions

### Session Naming

Sessions follow a standardized naming pattern:

```
Pattern: [session_name_]YYYYMMDD_HHMMSS
Examples:
- session_20250731_143022          # Default session
- experiment_A_20250731_143022     # Named session
- pilot_study_20250731_143022      # Custom named session
```

### Device File Naming

Files from devices follow device-specific patterns:

#### Android Phone Files
```
Pattern: [device_id]_[data_type]_YYYYMMDD_HHMMSS.[ext]
Examples:
- phone_1_rgb_20250731_143022.mp4      # RGB video
- phone_1_thermal_20250731_143022.mp4   # Thermal video
- phone_2_gsr_20250731_143022.csv       # GSR sensor data
```

#### PC Webcam Files  
```
Pattern: webcam_[id]_YYYYMMDD_HHMMSS.mp4
Examples:
- webcam_1_20250731_143022.mp4         # Primary webcam
- webcam_2_20250731_143022.mp4         # Secondary webcam
```

#### Calibration Files
```
Pattern: [device_id]_calib_[type]_YYYYMMDD_HHMMSS.[ext]
Examples:
- phone_1_calib_intrinsic_20250731_143022.json
- webcam_1_calib_chessboard_20250731_143022.jpg
```

### Log and Metadata Files

```
Pattern: [session_id]_[type].json
Examples:
- session_20250731_143022_log.json       # Event log
- session_metadata.json                  # Session metadata
- processing_metadata.json               # Processing results
- stimulus_log.json                      # Stimulus timing
```

## Data Schemas

### Session Metadata Schema

**File:** `session_metadata.json`

```json
{
  "session_id": "string",           // Unique session identifier
  "session_name": "string",         // Human-readable session name  
  "folder_path": "string",          // Full path to session folder
  "start_time": "ISO8601",          // Session start timestamp
  "end_time": "ISO8601|null",       // Session end timestamp
  "duration": "number|null",        // Duration in seconds
  "status": "enum",                 // "active" | "completed" | "error"
  "devices": {                      // Connected devices
    "device_id": {
      "device_type": "enum",        // "android_phone" | "pc_webcam" | "shimmer_gsr"
      "capabilities": ["string"],   // Device capabilities list
      "added_time": "ISO8601",      // When device was added
      "status": "enum"              // "connected" | "disconnected" | "error"
    }
  },
  "files": {                        // Recorded files by device
    "device_id": [
      {
        "file_type": "enum",        // "rgb_video" | "thermal_video" | "gsr_data" | "webcam_video"
        "file_path": "string",      // Relative path to file
        "file_size": "number",      // File size in bytes
        "created_time": "ISO8601"   // File creation timestamp
      }
    ]
  },
  "post_processing": {              // Post-processing status
    "hand_segmentation_completed": "boolean",
    "hand_segmentation_timestamp": "ISO8601|null",
    "synchronization_completed": "boolean",
    "export_completed": "boolean"
  }
}
```

### Session Log Schema

**File:** `[session_id]_log.json`

```json
{
  "session": "string",              // Session identifier
  "session_name": "string",         // Session name
  "start_time": "ISO8601",          // Log start time
  "end_time": "ISO8601|null",       // Log end time
  "duration": "number|null",        // Duration in seconds
  "devices": [                      // Device list at session start
    {
      "id": "string",
      "type": "string",
      "capabilities": ["string"]
    }
  ],
  "events": [                       // Chronological event list
    {
      "event": "enum",              // Event type (see Event Types below)
      "time": "HH:MM:SS.mmm",       // Time within session
      "timestamp": "ISO8601",       // Full timestamp
      // Event-specific fields...
    }
  ],
  "calibration_files": ["string"],  // Calibration files used
  "status": "enum"                  // "active" | "completed"
}
```

### Event Types in Session Logs

| Event Type | Description | Additional Fields |
|------------|-------------|-------------------|
| `session_start` | Session initiated | `devices: string[]` |
| `session_end` | Session completed | - |
| `device_connected` | Device connected | `device: string`, `device_type: string`, `capabilities: string[]` |
| `device_disconnected` | Device disconnected | `device: string`, `reason: string` |
| `start_record` | Recording started | `devices: string[]`, `session: string` |
| `stop_record` | Recording stopped | - |
| `device_ack` | Device acknowledged command | `device: string`, `command: string` |
| `stimulus_play` | Stimulus started | `media: string`, `media_path?: string` |
| `stimulus_stop` | Stimulus stopped | `media: string` |
| `marker` | User marker inserted | `label: string`, `stim_time?: string` |
| `file_received` | File received from device | `device: string`, `filename: string`, `size?: number`, `file_type: string` |
| `calibration_capture` | Calibration image captured | `device: string`, `file: string` |
| `calibration_done` | Calibration completed | `result_file?: string` |
| `error` | Error occurred | `error_type: string`, `message: string`, `device?: string` |

### Calibration Data Schema

**File:** `session_info.json` (in calibration folders)

```json
{
  "session_name": "string",         // Calibration session name
  "session_folder": "string",       // Folder path
  "device_ids": ["string"],         // Devices being calibrated
  "start_time": "ISO8601",          // Calibration start time
  "pattern_type": "enum",           // "chessboard" | "circles" | "asymmetric_circles"
  "pattern_size": [9, 6],           // Pattern dimensions [width, height]
  "square_size": "number",          // Physical square size in mm
  "status": "enum"                  // "active" | "completed" | "failed"
}
```

### Hand Segmentation Results Schema

**File:** `processing_metadata.json` (in processing folders)

```json
{
  "processing_type": "hand_segmentation",
  "method": "enum",                 // "mediapipe" | "yolo" | "manual"
  "source_videos": ["string"],     // Input video files
  "start_time": "ISO8601",          // Processing start time
  "end_time": "ISO8601",            // Processing completion time
  "duration": "number",             // Processing duration in seconds
  "results": {
    "total_frames": "number",       // Total frames processed
    "hands_detected_frames": "number", // Frames with hands detected
    "detection_rate": "number",     // Percentage of frames with hands
    "output_files": {
      "cropped_videos": ["string"], // Cropped hand videos
      "mask_videos": ["string"],    // Hand mask videos
      "annotations": ["string"]     // Annotation files
    }
  },
  "parameters": {
    "confidence_threshold": "number",
    "crop_margin": "number",
    "output_resolution": [640, 480]
  }
}
```

## Data Types and Organization

### Video Data

#### RGB Videos
- **Format:** MP4 (H.264 encoding)
- **Resolution:** 1920x1080 (configurable)
- **Frame Rate:** 30 FPS (configurable)
- **Location:** `devices/[device_id]/rgb_videos/`
- **Naming:** `[device_id]_rgb_YYYYMMDD_HHMMSS.mp4`

#### Thermal Videos  
- **Format:** MP4 or custom thermal format
- **Resolution:** Device-dependent (typically 384x288)
- **Frame Rate:** 30 FPS or device maximum
- **Location:** `devices/[device_id]/thermal_videos/`
- **Naming:** `[device_id]_thermal_YYYYMMDD_HHMMSS.mp4`

#### Webcam Videos
- **Format:** MP4 (H.264 encoding)  
- **Resolution:** 1920x1080 or 4K (configurable)
- **Frame Rate:** 30 FPS (configurable)
- **Location:** `webcam/`
- **Naming:** `webcam_[id]_YYYYMMDD_HHMMSS.mp4`

### Sensor Data

#### GSR (Galvanic Skin Response) Data
- **Format:** CSV with headers
- **Sampling Rate:** Device-dependent (typically 128 Hz)
- **Columns:** `timestamp, gsr_value, resistance, temperature`
- **Location:** `devices/[device_id]/sensor_data/`
- **Naming:** `[device_id]_gsr_YYYYMMDD_HHMMSS.csv`

#### Accelerometer/Gyroscope Data
- **Format:** CSV with headers
- **Sampling Rate:** Device-dependent (typically 200 Hz)
- **Columns:** `timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z`
- **Location:** `devices/[device_id]/sensor_data/`
- **Naming:** `[device_id]_motion_YYYYMMDD_HHMMSS.csv`

### Calibration Data

#### Camera Intrinsic Calibration
- **Format:** JSON with camera matrix and distortion coefficients
- **Location:** `devices/[device_id]/calibration/`
- **Naming:** `[device_id]_intrinsic_YYYYMMDD_HHMMSS.json`

#### Multi-Camera Extrinsic Calibration
- **Format:** JSON with rotation and translation matrices
- **Location:** `calibration_data/[session]/`
- **Naming:** `multi_camera_extrinsic_YYYYMMDD_HHMMSS.json`

### Processing Outputs

#### Hand Segmentation Results
- **Cropped Videos:** MP4 files with hand regions extracted
- **Mask Videos:** Black/white mask videos showing hand regions
- **Annotation Files:** JSON files with hand keypoints and bounding boxes
- **Location:** `processing/hand_segmentation/`

#### Synchronization Data
- **Format:** JSON with timestamp alignment data
- **Location:** `processing/synchronization/`
- **Content:** Cross-device time offset calculations and sync markers

## User Guide

### Finding Your Data

After completing a recording session, your data will be organized as follows:

1. **Main Session Folder:** Located in `PythonApp/recordings/session_YYYYMMDD_HHMMSS/`
2. **Session Summary:** Check `session_metadata.json` for an overview of recorded files
3. **Event Timeline:** Review `session_YYYYMMDD_HHMMSS_log.json` for detailed event timing
4. **Video Files:** Find in `devices/[device_name]/` and `webcam/` subfolders
5. **Sensor Data:** Located in `devices/[device_name]/sensor_data/`

### Understanding File Timestamps

All timestamps in the system use ISO 8601 format (`YYYY-MM-DDTHH:MM:SS.mmmmmmZ`) for precision and consistency. File names use a simplified format (`YYYYMMDD_HHMMSS`) for filesystem compatibility.

### Data Access Examples

```bash
# List all sessions
ls PythonApp/recordings/

# View session metadata
cat PythonApp/recordings/session_20250731_143022/session_metadata.json

# Find all video files in a session
find PythonApp/recordings/session_20250731_143022/ -name "*.mp4"

# Check session events
cat PythonApp/recordings/session_20250731_143022/session_20250731_143022_log.json
```

### Data Export Options

The system provides several export formats:

1. **CSV Exports:** Sensor data and event logs in CSV format (`exports/csv/`)
2. **MATLAB Exports:** `.mat` files for MATLAB analysis (`exports/matlab/`)
3. **Summary Reports:** Human-readable session summaries (`exports/summary/`)

## Developer Guidelines

### Adding New Data Types

When adding support for new data types:

1. **Follow Naming Conventions:** Use the established patterns for consistency
2. **Update Schemas:** Add schema definitions to this document
3. **Location Guidelines:** Place data in appropriate subdirectories
4. **Metadata Integration:** Update session metadata to track new file types
5. **Logging Integration:** Log relevant events in session logs

### File System Best Practices

1. **Use Relative Paths:** Store relative paths in metadata for portability
2. **Atomic Operations:** Ensure file operations are atomic to prevent corruption
3. **Error Handling:** Implement proper error handling for I/O operations
4. **Cleanup Procedures:** Provide mechanisms for cleaning up incomplete sessions

### Schema Validation

All JSON files should be validated against their schemas. Use the provided schema definitions to validate:

```python
import json
import jsonschema

# Load schema and data
with open('session_metadata_schema.json') as f:
    schema = json.load(f)

with open('session_metadata.json') as f:
    data = json.load(f)

# Validate
jsonschema.validate(data, schema)
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-07-31  
**Maintainer:** Multi-Sensor Recording System Team