# File Naming and Organization Standards

## Overview

This document defines the standardized file naming conventions and organization patterns used throughout the Multi-Sensor Synchronized Recording System. Following these standards ensures consistency, discoverability, and proper integration with the system's data management components.

## Core Principles

### 1. Predictability
- All file names follow consistent patterns
- Timestamps use standardized format (YYYYMMDD_HHMMSS)
- Device identifiers are consistent across all files

### 2. Sortability
- File names sort chronologically when listed alphabetically
- Session folders appear in chronological order
- Related files group together in directory listings

### 3. Human Readability
- File names are descriptive and self-documenting
- No cryptic abbreviations or codes
- Component separation using underscores

### 4. System Compatibility
- No special characters that cause filesystem issues
- Compatible across Windows, macOS, and Linux
- Safe for network transfers and archiving

## Directory Structure Standards

### Root Level Organization

```
project-root/
├── PythonApp/recordings/          # Main session recordings
├── calibration_data/              # Calibration sessions  
├── docs/                          # Documentation
├── tools/                         # Utility scripts
└── external/                      # External dependencies
```

### Session Directory Naming

**Pattern:** `[custom_name_]YYYYMMDD_HHMMSS/`

**Rules:**
- Always end with timestamp in YYYYMMDD_HHMMSS format
- Custom names use only alphanumeric characters, hyphens, and underscores
- No spaces in folder names (use underscores instead)
- Maximum total length: 100 characters

**Examples:**
```
session_20250731_143022/           # Default session
experiment_A_20250731_143022/      # Named experiment
pilot_study_20250731_143022/       # Custom study name
stress_test_run_20250731_143022/   # Multi-word name with underscores
```

### Session Internal Structure

**Standard layout for every session:**
```
session_YYYYMMDD_HHMMSS/
├── session_metadata.json         # Required: Session information
├── session_YYYYMMDD_HHMMSS_log.json  # Required: Event log
├── devices/                      # Device-specific data
│   └── [device_id]/              # One folder per device
├── webcam/                       # PC webcam recordings
├── processing/                   # Post-processing outputs
├── exports/                      # Data exports
└── stimulus/                     # Stimulus-related files
```

## File Naming Conventions

### Session-Level Files

#### Session Metadata
- **File:** `session_metadata.json`
- **Description:** Core session information and file registry
- **Required:** Yes
- **Location:** Session root directory

#### Session Event Log
- **Pattern:** `session_YYYYMMDD_HHMMSS_log.json`
- **Description:** Chronological log of all session events
- **Required:** Yes
- **Location:** Session root directory
- **Example:** `session_20250731_143022_log.json`

### Device Data Files

#### Video Files

**Pattern:** `[device_id]_[video_type]_YYYYMMDD_HHMMSS.mp4`

**Video Types:**
- `rgb` - Regular color video
- `thermal` - Thermal camera video
- `depth` - Depth camera video (if available)

**Examples:**
```
phone_1_rgb_20250731_143022.mp4
phone_1_thermal_20250731_143022.mp4
phone_2_rgb_20250731_143022.mp4
webcam_1_rgb_20250731_143022.mp4
```

#### Sensor Data Files

**Pattern:** `[device_id]_[sensor_type]_YYYYMMDD_HHMMSS.csv`

**Sensor Types:**
- `gsr` - Galvanic Skin Response
- `motion` - Accelerometer/Gyroscope data
- `heart_rate` - Heart rate monitor data
- `temperature` - Temperature sensor data

**Examples:**
```
phone_1_gsr_20250731_143022.csv
phone_1_motion_20250731_143022.csv
shimmer_01_gsr_20250731_143022.csv
```

### Webcam Files

**Pattern:** `webcam_[id]_YYYYMMDD_HHMMSS.mp4`

**Examples:**
```
webcam_1_20250731_143022.mp4       # Primary webcam
webcam_2_20250731_143022.mp4       # Secondary webcam  
webcam_left_20250731_143022.mp4    # Named webcam position
webcam_right_20250731_143022.mp4   # Named webcam position
```

### Calibration Files

#### Calibration Images
**Pattern:** `[device_id]_calib_[type]_[sequence]_YYYYMMDD_HHMMSS.jpg`

**Types:**
- `chessboard` - Chessboard pattern images
- `circles` - Circle pattern images
- `intrinsic` - Intrinsic calibration images
- `extrinsic` - Extrinsic calibration images

**Examples:**
```
phone_1_calib_chessboard_001_20250731_143022.jpg
phone_1_calib_chessboard_002_20250731_143022.jpg
webcam_1_calib_intrinsic_001_20250731_143022.jpg
```

#### Calibration Results
**Pattern:** `[device_id]_calib_result_[type]_YYYYMMDD_HHMMSS.json`

**Examples:**
```
phone_1_calib_result_intrinsic_20250731_143022.json
multi_device_calib_result_extrinsic_20250731_143022.json
```

### Processing Output Files

#### Hand Segmentation Results
**Location:** `processing/hand_segmentation/`

**Patterns:**
- Cropped videos: `[source_name]_hands_cropped_YYYYMMDD_HHMMSS.mp4`
- Mask videos: `[source_name]_hands_mask_YYYYMMDD_HHMMSS.mp4`
- Annotations: `[source_name]_hands_annotations_YYYYMMDD_HHMMSS.json`

**Examples:**
```
phone_1_rgb_hands_cropped_20250731_143022.mp4
phone_1_rgb_hands_mask_20250731_143022.mp4
phone_1_rgb_hands_annotations_20250731_143022.json
```

#### Synchronization Data
**Location:** `processing/synchronization/`

**Pattern:** `sync_data_YYYYMMDD_HHMMSS.json`

**Example:** `sync_data_20250731_143022.json`

#### Processing Metadata
**Pattern:** `processing_metadata.json`
**Location:** Each processing subdirectory
**Description:** Metadata about processing operations performed

### Export Files

#### CSV Exports
**Location:** `exports/csv/`

**Patterns:**
- Session summary: `session_summary_YYYYMMDD_HHMMSS.csv`
- Device data: `[device_id]_[data_type]_export_YYYYMMDD_HHMMSS.csv`
- Combined data: `combined_[data_type]_YYYYMMDD_HHMMSS.csv`

**Examples:**
```
session_summary_20250731_143022.csv
phone_1_gsr_export_20250731_143022.csv
combined_motion_20250731_143022.csv
```

#### MATLAB Exports
**Location:** `exports/matlab/`

**Pattern:** `[description]_YYYYMMDD_HHMMSS.mat`

**Examples:**
```
session_data_20250731_143022.mat
gsr_analysis_20250731_143022.mat
```

## Device Identifier Standards

### Device Naming Convention

**Pattern:** `[device_type]_[identifier]`

**Device Types:**
- `phone` - Android smartphones
- `webcam` - PC webcams
- `shimmer` - Shimmer sensor devices
- `thermal` - Standalone thermal cameras

**Identifier Rules:**
- Use numbers (1, 2, 3...) for multiple devices of same type
- Use descriptive names for positioned devices (left, right, center)
- Maximum length: 20 characters
- Only alphanumeric characters and underscores

**Valid Examples:**
```
phone_1, phone_2, phone_3
webcam_1, webcam_2  
webcam_left, webcam_right, webcam_center
shimmer_01, shimmer_02
thermal_handheld, thermal_fixed
```

**Invalid Examples:**
```
phone-1          # No hyphens
phone 1          # No spaces
phone#1          # No special characters
My Phone         # No spaces or capitals
```

## Timestamp Standards

### Format Specification

**File names:** `YYYYMMDD_HHMMSS`
- YYYY: 4-digit year
- MM: 2-digit month (01-12)
- DD: 2-digit day (01-31)
- HH: 2-digit hour (00-23)
- MM: 2-digit minute (00-59)
- SS: 2-digit second (00-59)

**JSON metadata:** ISO 8601 format with timezone
- Format: `YYYY-MM-DDTHH:MM:SS.ssssss+TZ`
- Example: `2025-07-31T14:30:22.123456+00:00`

### Timezone Handling

- All timestamps in file names use local system time
- All timestamps in JSON metadata include timezone information
- Processing scripts handle timezone conversion automatically

## Implementation Guidelines

### For Developers

#### Creating New File Types

When adding support for new file types:

1. **Define naming pattern** following existing conventions
2. **Update schema definitions** in `docs/api/`
3. **Add validation rules** to validation tools
4. **Document in this file** with examples
5. **Update SessionManager** to track new file types

#### Code Integration

```python
# Use centralized timestamp formatting
from datetime import datetime

def generate_timestamp():
    """Generate standardized timestamp for file names."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_filename(device_id, file_type, extension):
    """Generate standardized filename."""
    timestamp = generate_timestamp()
    return f"{device_id}_{file_type}_{timestamp}.{extension}"

# Example usage
filename = generate_filename("phone_1", "rgb", "mp4")
# Returns: "phone_1_rgb_20250731_143022.mp4"
```

#### Validation Integration

```python
# Validate file names against patterns
import re

def validate_session_folder_name(folder_name):
    """Validate session folder naming convention."""
    pattern = r'^[a-zA-Z0-9_-]*_\d{8}_\d{6}$'
    return re.match(pattern, folder_name) is not None

def validate_device_file_name(filename):
    """Validate device file naming convention."""
    pattern = r'^[a-zA-Z0-9_]+_[a-zA-Z0-9_]+_\d{8}_\d{6}\.[a-zA-Z0-9]+$'
    return re.match(pattern, filename) is not None
```

### For System Administrators

#### Backup and Archival

- File naming patterns support chronological sorting
- Use timestamps in file names for automated cleanup scripts
- Archive sessions by moving entire session folders
- Maintain directory structure for data integrity

#### Storage Management

- Monitor session folder sizes (typical: 100MB - 10GB per session)
- Plan for long-term storage based on timestamp patterns
- Use file patterns for automated data retention policies

## Validation and Quality Assurance

### Automated Validation

Use the provided validation tools:

```bash
# Validate all sessions
python tools/validate_data_schemas.py --all-sessions

# Validate specific session
python tools/validate_data_schemas.py --session PythonApp/recordings/session_20250731_143022

# Check naming conventions
python tools/check_naming_conventions.py --directory PythonApp/recordings
```

### Manual Verification Checklist

For each session, verify:

- [ ] Session folder follows naming convention
- [ ] `session_metadata.json` exists and validates
- [ ] Session log file exists with matching timestamp
- [ ] All device files follow naming patterns
- [ ] Processing outputs use consistent naming
- [ ] No files with invalid characters or spaces

## Migration and Legacy Support

### Handling Existing Data

When updating naming conventions:

1. **Grandfather existing files** - don't break working sessions
2. **Provide migration scripts** for important data
3. **Update validation** to handle legacy patterns temporarily
4. **Document transition period** in changelog

### Version Compatibility

- Mark schema versions in JSON files
- Support reading multiple format versions
- Provide clear migration paths for data formats

---

**Document Version:** 1.0  
**Last Updated:** 2025-07-31  
**Maintainer:** Multi-Sensor Recording System Team

## Related Documents

- [Data Structure Documentation](DATA_STRUCTURE_DOCUMENTATION.md)
- [Data Storage Quick Reference](DATA_STORAGE_QUICK_REFERENCE.md)
- [JSON Schema Definitions](schemas/)
- [Validation Tools](../tools/validate_data_schemas.py)