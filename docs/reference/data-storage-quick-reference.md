# Data Storage Quick Reference Guide

Welcome to your essential guide for navigating and understanding the data storage system used in the Multi-Sensor Synchronized Recording System. This reference has been designed to quickly answer the most common questions researchers have about locating and accessing their recorded data. Whether you're looking for a specific recording session, trying to understand file organization, or need to quickly access different types of sensor data, this guide provides practical, step-by-step instructions to help you find what you need.

The recording system automatically organizes all your data into logical, timestamped folders that make it easy to locate recordings from specific sessions. Each recording session creates a comprehensive data package that includes video recordings, sensor data, metadata, and event logs, all organized in a predictable structure that you can navigate with confidence.

## 🗂️ Where Is My Data?

Understanding where your data is stored is the first step to effective data analysis. The system stores all recordings in a centralized location with a clear organizational hierarchy that separates different sessions while keeping related data grouped together.

### Quick Access Paths

These command-line examples show you the fastest way to navigate to your data and access key information about your recording sessions:

```bash
# Navigate to the main recordings folder where all session data is stored
cd PythonApp/recordings/

# List all recorded sessions to see what's available
ls PythonApp/recordings/
# Output shows timestamped session folders: session_20250731_143022/ session_20250731_150445/ ...

# Enter a specific session folder to explore its contents
cd PythonApp/recordings/session_20250731_143022/

# Read the session summary to understand what was recorded
cat session_metadata.json

# Review the detailed event log to see the timeline of what happened during recording
cat session_20250731_143022_log.json
```

These paths provide immediate access to the most important information about your recording sessions. The session metadata file gives you a high-level overview of all devices used and files created, while the event log provides a detailed chronological record of the entire recording process.

### File Locations at a Glance

The following table provides a quick reference for locating different types of data within your session folders. Each data type has a designated location and follows consistent naming patterns that make it easy to identify files and understand their purpose:

| Data Type | Location | Example File | Purpose |
|-----------|----------|--------------|---------|
| **Session Info** | `session_metadata.json` | Complete session overview | Provides comprehensive metadata about devices used, files created, and recording parameters |
| **Event Log** | `session_YYYYMMDD_HHMMSS_log.json` | Detailed timeline | Chronicles every event during recording including start/stop times, errors, and device status |
| **Phone Videos** | `devices/phone_1/rgb_videos/` | `phone_1_rgb_20250731_143022.mp4` | Standard camera recordings from connected mobile devices |
| **Thermal Videos** | `devices/phone_1/thermal_videos/` | `phone_1_thermal_20250731_143022.mp4` | Heat signature recordings from thermal camera attachments |
| **Webcam Videos** | `webcam/` | `webcam_1_20250731_143022.mp4` | Computer-based camera recordings for additional perspectives |
| **Sensor Data** | `devices/phone_1/sensor_data/` | `phone_1_gsr_20250731_143022.csv` | Physiological and motion sensor measurements in CSV format |
| **Hand Analysis** | `processing/hand_segmentation/` | Various processed files | Computer vision analysis results including cropped videos and segmentation masks |

This organization ensures that related data types are grouped logically while maintaining clear separation between different devices and processing stages. The consistent naming patterns help you quickly identify the specific data you need for your analysis.

## 📁 Understanding Your Session Folder

Each recording session creates a comprehensive, self-contained folder that includes all data collected during that specific recording period. Understanding the structure of these session folders is essential for efficiently accessing and analyzing your recorded data. The folder organization has been carefully designed to group related files while maintaining clear separation between different data types and processing stages.

Each recording session creates a folder with a structure like this, where all related data is logically organized and easy to navigate:

```
session_20250731_143022/
├── 📄 session_metadata.json          ← START HERE - Complete overview of the session
├── 📄 session_20250731_143022_log.json ← Detailed chronological timeline of all events  
├── 📁 devices/                       ← Data collected from all connected mobile devices
│   ├── 📁 phone_1/                   ← Data from the first connected phone
│   │   ├── 📁 rgb_videos/            ← Standard color camera recordings
│   │   ├── 📁 thermal_videos/        ← Heat signature camera recordings  
│   │   └── 📁 sensor_data/           ← GSR, heart rate, motion, and other sensor measurements
│   └── 📁 phone_2/                   ← Data from second phone if multiple devices were used
│       ├── 📁 rgb_videos/            ← Additional camera perspectives
│       └── 📁 sensor_data/           ← Additional sensor measurements for comparison
├── 📁 webcam/                        ← Computer-based camera recordings
│   ├── webcam_1_20250731_143022.mp4  ← Primary webcam recording
│   └── webcam_2_20250731_143022.mp4  ← Secondary webcam if available
├── 📁 processing/                    ← Post-recording analysis and processing results
│   ├── 📁 hand_segmentation/         ← Computer vision analysis of hand movements
│   └── 📁 synchronized_data/         ← Time-aligned data from multiple sources
└── 📁 exports/                       ← Data exported in various formats for analysis
    ├── 📁 csv/                       ← Spreadsheet-compatible data exports
    └── 📁 matlab/                    ← MATLAB-compatible data exports
```

The session metadata file serves as your primary entry point for understanding what data is available. It contains comprehensive information about which devices were connected, what types of data were recorded, file locations, recording parameters, and any issues that occurred during the session. This file acts as a roadmap to all other data in the session folder.
├── 📁 webcam/                        ← Computer camera videos
├── 📁 processing/                    ← Analysis results (if run)
└── 📁 exports/                       ← Data exports (CSV, etc.)
```

## 🔍 Finding Specific Data

### I want to see all videos from my session:
```bash
find session_20250731_143022/ -name "*.mp4"
```

### I want to see all sensor data:
```bash
find session_20250731_143022/ -name "*.csv"
```

### I want to know what happened when:
```bash
# Look for specific events (start, stop, errors)
grep "start_record\|stop_record\|error" session_20250731_143022_log.json
```

### I want to see file sizes:
```bash
ls -lh session_20250731_143022/devices/*/rgb_videos/
ls -lh session_20250731_143022/webcam/
```

## 📊 Reading Session Information

### Session Metadata (session_metadata.json)
This file tells you everything about your recording:

```json
{
  "session_id": "session_20250731_143022",
  "start_time": "2025-07-31T14:30:22.123456",
  "duration": 125.5,
  "devices": {
    "phone_1": {
      "device_type": "android_phone",
      "capabilities": ["rgb_video", "thermal_video", "gsr_data"]
    }
  },
  "files": {
    "phone_1": [
      {
        "file_type": "rgb_video", 
        "file_path": "devices/phone_1/rgb_videos/phone_1_rgb_20250731_143022.mp4",
        "file_size": 52428800
      }
    ]
  }
}
```

**What this tells you:**
- Session lasted 125.5 seconds (about 2 minutes)
- Used 1 Android phone with camera and sensors
- Recorded 1 video file (50 MB)

### Session Log (session_YYYYMMDD_HHMMSS_log.json)
This file shows you exactly what happened when:

```json
{
  "events": [
    {
      "event": "session_start",
      "time": "14:30:22.123",
      "devices": ["phone_1"]
    },
    {
      "event": "start_record", 
      "time": "14:30:25.456",
      "devices": ["phone_1"]
    },
    {
      "event": "marker",
      "time": "14:31:10.789", 
      "label": "stimulus_start"
    },
    {
      "event": "stop_record",
      "time": "14:32:27.654"
    }
  ]
}
```

**What this tells you:**
- Recording started 3 seconds after session began
- A marker was placed at 45 seconds into recording
- Recording stopped after about 2 minutes

## 🏷️ File Naming Explained

All files follow predictable naming patterns:

### Session Names
```
Format: [custom_name_]YYYYMMDD_HHMMSS
Examples:
- session_20250731_143022     (default)
- experiment_A_20250731_143022 (custom name)
```

### Device Files  
```
Format: [device]_[type]_YYYYMMDD_HHMMSS.[extension]
Examples:
- phone_1_rgb_20250731_143022.mp4      (video)
- phone_1_gsr_20250731_143022.csv      (sensor data)
- webcam_1_20250731_143022.mp4         (webcam)
```

## 📈 Data Formats

### Video Files (.mp4)
- **Resolution:** Usually 1920x1080 (Full HD)
- **Frame Rate:** 30 frames per second
- **Codec:** H.264 (standard video format)
- **Playable in:** VLC, Windows Media Player, any video player

### Sensor Data (.csv)
- **Format:** Comma-separated values (opens in Excel)
- **Columns:** timestamp, sensor_value, additional_metrics
- **Sample Rate:** Varies by sensor (typically 128-200 samples/second)

## 🚀 Quick Actions

### Export Session to CSV
```bash
# Look for export folder in your session
ls session_20250731_143022/exports/csv/
```

### Check Session Health
```bash
# Verify all expected files are present
python -c "
import json
with open('session_metadata.json', 'r') as f:
    data = json.load(f)
print(f'Session: {data[\"session_id\"]}')
print(f'Duration: {data.get(\"duration\", \"unknown\")} seconds')
print(f'Files recorded: {sum(len(files) for files in data[\"files\"].values())}')
"
```

### Find Problems
```bash
# Look for errors in session log
grep -i "error" session_20250731_143022_log.json
```

## 🆘 Troubleshooting

### "I can't find my session"
- Check `PythonApp/recordings/` folder
- Look for folders with format `session_YYYYMMDD_HHMMSS`
- If using custom names, look for `[name]_YYYYMMDD_HHMMSS`

### "My video won't play"
- Check file size (should be > 0 bytes)
- Try VLC media player (handles more formats)
- Check session log for recording errors

### "I don't see sensor data"
- Check `devices/[device_name]/sensor_data/` folder
- Verify device was connected (check session_metadata.json)
- Look for .csv files with device name

### "Session seems incomplete"
- Check session status in metadata: should be "completed"
- Look for "session_end" event in log
- Check for error events in log

## 📞 Getting Help

1. **Check the session log** for error messages
2. **Verify file sizes** aren't 0 bytes  
3. **Look at session metadata** for device status
4. **Check the main documentation** at `docs/technical/DATA_STRUCTURE_DOCUMENTATION.md`

---

**Remember:** Every session creates its own folder with all data organized inside. Start with `session_metadata.json` to understand what was recorded!