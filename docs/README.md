# Data Management Documentation

This directory contains comprehensive documentation for the data storage and management system used in the Multi-Sensor Synchronized Recording System.

## 📚 Documentation Files

### For Users
- **[Data Storage Quick Reference](DATA_STORAGE_QUICK_REFERENCE.md)** - Start here! Quick guide to finding and understanding your data
- **[Data Structure Documentation](DATA_STRUCTURE_DOCUMENTATION.md)** - Complete technical documentation of file structures and schemas

### For Developers  
- **[File Naming Standards](FILE_NAMING_STANDARDS.md)** - Comprehensive naming conventions and organization standards
- **[JSON Schemas](schemas/)** - Machine-readable schema definitions for validation

## 🗂️ File Organization Summary

The system organizes data in a predictable, hierarchical structure:

```
PythonApp/recordings/
├── session_20250731_143022/      # Session folder (timestamp-based)
│   ├── session_metadata.json     # What was recorded
│   ├── session_20250731_143022_log.json  # When events happened  
│   ├── devices/                  # Data from phones/sensors
│   ├── webcam/                   # Computer camera videos
│   └── processing/               # Analysis results
└── session_20250731_150445/      # Another session
```

## 🎯 Quick Start Guide

### Finding Your Data

1. **Go to recordings folder:** `PythonApp/recordings/`
2. **Find your session:** Look for `session_YYYYMMDD_HHMMSS/` folders
3. **Check session info:** Read `session_metadata.json` for overview
4. **View timeline:** Check `session_*_log.json` for event timeline

### Understanding File Names

All files follow predictable patterns:

```bash
# Session folders
session_20250731_143022/           # Standard session
experiment_A_20250731_143022/      # Named session

# Video files  
phone_1_rgb_20250731_143022.mp4    # Phone RGB video
webcam_1_20250731_143022.mp4       # Webcam video

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