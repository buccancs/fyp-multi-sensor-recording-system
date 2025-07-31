# Data Management Documentation

Welcome to the comprehensive documentation hub for the data storage and management system used in the Multi-Sensor Synchronized Recording System. This documentation suite has been carefully designed to provide both researchers and developers with clear insights into how their recorded data is organized, stored, and accessed within the system.

The multi-sensor recording system generates substantial amounts of data across various devices and sensors, including RGB and thermal cameras, GSR sensors, motion sensors, and webcam recordings. Understanding how this data is structured and named is crucial for efficient data analysis and research workflows. This documentation provides complete transparency into the data organization system, ensuring that users can quickly locate their recordings and understand the relationships between different data files.

## 📚 Documentation Files

The documentation is organized into user-focused and developer-focused sections to serve different audiences and use cases effectively.

### For Users and Researchers
The user documentation focuses on practical guidance for finding and working with recorded data without requiring deep technical knowledge of the system internals.

- **[Data Storage Quick Reference](DATA_STORAGE_QUICK_REFERENCE.md)** - This is your starting point! This guide provides immediate answers to common questions like "Where is my data?" and "How do I find recordings from a specific session?" It includes practical examples and step-by-step instructions for navigating the file system.

- **[Data Structure Documentation](DATA_STRUCTURE_DOCUMENTATION.md)** - This comprehensive resource explains the complete technical architecture of how data is organized. It covers file hierarchies, data schemas, relationships between files, and provides detailed explanations of each data type and its purpose within the recording system.

- **[Shimmer3 GSR+ Quick Reference](SHIMMER3_GSR_PLUS_QUICK_REFERENCE.md)** - Essential quick-start guide for developers integrating Shimmer3 GSR+ devices, including setup instructions, configuration examples, and common use cases.

### For Developers and Technical Users  
The developer documentation provides the technical specifications and standards needed for system maintenance, extension, and integration.

- **[File Naming Standards](FILE_NAMING_STANDARDS.md)** - This detailed specification document covers all naming conventions used throughout the system. It explains the rationale behind naming patterns, provides examples for different scenarios, and includes validation guidelines to ensure consistency across all recorded data.

- **[JSON Schemas](schemas/)** - This directory contains machine-readable schema definitions that formally specify the structure and validation rules for all JSON files in the system. These schemas enable automated validation and serve as authoritative references for data format specifications.

### Device-Specific Technical Documentation
Comprehensive technical documentation for the individual sensor platforms and devices integrated into the system.

- **[Shimmer3 GSR+ Comprehensive Documentation](SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md)** - Master thesis-level technical documentation covering Shimmer3 GSR+ physiological sensor integration, including hardware specifications, Android API integration, communication protocols, data processing algorithms, and implementation best practices.

- **[Topdon TC001 Thermal Camera Documentation](TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md)** - Comprehensive technical documentation for thermal camera integration, covering hardware specifications, SDK architecture, USB communication protocols, Android integration patterns, and performance optimization strategies.

## 🗂️ File Organization Overview

The recording system employs a hierarchical file organization strategy that balances accessibility with technical precision. Each recording session creates a self-contained directory structure that includes all related data files, metadata, and processing results. This approach ensures that researchers can easily locate all materials related to a specific experimental session while maintaining clear separation between different recording sessions.

The system organizes data in a predictable, time-based hierarchical structure that makes it easy to locate recordings chronologically and understand the relationships between different data types:

```
PythonApp/recordings/
├── session_20250731_143022/      # Each session gets its own timestamped folder
│   ├── session_metadata.json     # Comprehensive overview of what was recorded
│   ├── session_20250731_143022_log.json  # Detailed chronological log of all events  
│   ├── devices/                  # Organized storage for all connected device data
│   ├── webcam/                   # Computer-based camera recordings
│   └── processing/               # Post-recording analysis and processing results
└── session_20250731_150445/      # Each additional session follows the same pattern
```

This organization strategy ensures that all data related to a single recording session remains grouped together, making it straightforward to archive, share, or analyze complete experimental datasets. The timestamp-based folder naming also provides natural chronological ordering when viewing session directories.

## 🎯 Quick Start Guide

Getting started with the data organization system is straightforward once you understand the basic navigation principles. The system has been designed to be intuitive for researchers who may not have extensive technical backgrounds while still providing the detailed information that advanced users require.

### Finding Your Data

The process of locating your recorded data follows a simple, step-by-step approach that takes advantage of the system's organized structure:

1. **Navigate to the recordings folder:** Begin by opening the `PythonApp/recordings/` directory, which serves as the central repository for all recorded sessions. This folder contains all session directories organized chronologically.

2. **Locate your session:** Session folders are named using a timestamp format `session_YYYYMMDD_HHMMSS/`, making it easy to identify recordings by date and time. If you provided a custom name during recording, it will appear as a prefix like `experiment_A_20250731_143022/`.

3. **Review session information:** Each session folder contains a `session_metadata.json` file that provides a comprehensive overview of what was recorded during that session. This file serves as your guide to understanding all the data files available in that session.

4. **Examine the event timeline:** The session log file `session_*_log.json` contains a detailed chronological record of everything that happened during the recording, including when each device started recording, any issues that occurred, and when the session ended.

### Understanding File Names

The system uses consistent, descriptive naming patterns that make it easy to identify file types and their associated recording sessions. All files follow logical patterns that encode important information directly in the filename:

Session folders use timestamps as their primary identifier, ensuring unique names and natural chronological sorting. When you provide a custom session name, it appears as a prefix to maintain both clarity and uniqueness:

```bash
# Standard session folders with timestamp-based names
session_20250731_143022/           # Session recorded on July 31, 2025 at 14:30:22
session_20250731_150445/           # Later session the same day

# Named sessions that include descriptive prefixes  
experiment_A_20250731_143022/      # Custom-named session for easy identification
calibration_20250731_143022/       # Specialized session type with descriptive name
```

Video files and sensor data files embed device identifiers, data types, and timestamps to ensure complete traceability and easy identification:

```bash
# Video files include device ID, camera type, and session timestamp
phone_1_rgb_20250731_143022.mp4    # RGB camera video from phone 1
phone_1_thermal_20250731_143022.mp4 # Thermal camera video from the same phone
webcam_1_20250731_143022.mp4       # Computer webcam recording

# Sensor data files follow similar patterns for consistency
phone_1_gsr_20250731_143022.csv    # GSR sensor data from phone 1
phone_1_motion_20250731_143022.csv # Motion sensor data from the same device
```

# Sensor data
phone_1_gsr_20250731_143022.csv    # GSR sensor data
```

### Data Validation

Verify your data integrity:

```bash
# Validate a specific session
python tools/validate_data_schemas.py --session PythonApp/recordings/session_20250731_143022

# Validate all sessions
python tools/validate_data_schemas.py --all-sessions
```

## 📋 Data Types Supported

| Type | Format | Location | Example |
|------|--------|----------|---------|
| **Session Info** | JSON | `session_metadata.json` | Session overview |
| **Event Log** | JSON | `session_*_log.json` | Timeline of events |
| **RGB Video** | MP4 | `devices/*/rgb_videos/` | Regular camera |
| **Thermal Video** | MP4 | `devices/*/thermal_videos/` | Heat camera |  
| **Webcam Video** | MP4 | `webcam/` | Computer camera |
| **GSR Data** | CSV | `devices/*/sensor_data/` | Stress/arousal |
| **Motion Data** | CSV | `devices/*/sensor_data/` | Accelerometer |
| **Calibration** | JSON/JPG | `devices/*/calibration/` | Camera calibration |
| **Hand Analysis** | MP4/JSON | `processing/hand_segmentation/` | Hand tracking |

## 🔧 For Developers

### Schema Validation

All data files are validated against JSON schemas:

```python
from tools.validate_data_schemas import DataSchemaValidator

validator = DataSchemaValidator()
is_valid, error = validator.validate_file(
    "session_metadata.json", 
    "session_metadata"
)
```

### Adding New Data Types

1. Define naming pattern in [File Naming Standards](FILE_NAMING_STANDARDS.md)
2. Create JSON schema in `schemas/` directory
3. Update validation tools
4. Update SessionManager to track new files
5. Document in this README

### Integration Points

The system integrates with:
- **SessionManager** - Creates and manages session folders
- **SessionLogger** - Logs events and creates timeline files
- **CalibrationManager** - Handles camera calibration data
- **Hand Segmentation** - Processes video for hand analysis

## 🛠️ Tools and Utilities

### Validation Tools
- `tools/validate_data_schemas.py` - Validate data against schemas
- Schema files in `docs/schemas/` - JSON schema definitions

### Usage Examples

```bash
# Check if schemas are valid
python tools/validate_data_schemas.py --check-schema docs/schemas/session_metadata_schema.json

# Validate specific session
python tools/validate_data_schemas.py --session PythonApp/recordings/session_20250731_143022

# Validate calibration data
python tools/validate_data_schemas.py --calibration calibration_data/test_session
```

## 📊 Data Flow

1. **Session Creation** - SessionManager creates folder structure
2. **Recording** - Devices save data using naming conventions  
3. **Event Logging** - SessionLogger tracks all events
4. **Validation** - Tools verify data integrity
5. **Processing** - Analysis creates additional data files
6. **Export** - Data converted to research formats

## 🆘 Troubleshooting

### Common Issues

**"Can't find my session"**
- Check `PythonApp/recordings/` folder
- Sessions named with timestamp: `session_YYYYMMDD_HHMMSS`

**"Data validation fails"** 
- Run validation tool for specific error messages
- Check file formats match schema requirements
- Verify file naming follows conventions

**"Missing files"**
- Check `session_metadata.json` for expected files
- Look for errors in `session_*_log.json`
- Verify device connection during recording

### Getting Help

1. Start with [Quick Reference Guide](DATA_STORAGE_QUICK_REFERENCE.md)
2. Check validation tool output for specific errors
3. Review session logs for recording issues
4. Consult [File Naming Standards](FILE_NAMING_STANDARDS.md) for naming rules

## 📈 Future Enhancements

Planned improvements to the data management system:

- [ ] Automated data cleanup tools
- [ ] Data compression and archival utilities  
- [ ] Integration with cloud storage systems
- [ ] Advanced search and filtering tools
- [ ] Data export wizards for research platforms

---

**Last Updated:** 2025-07-31  
**Version:** 1.0  
**Maintainers:** Multi-Sensor Recording System Team