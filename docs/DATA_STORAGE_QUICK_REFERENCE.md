# Data Storage Quick Reference Guide

## 🗂️ Where Is My Data?

### Quick Access Paths

```bash
# Main recordings folder
cd PythonApp/recordings/

# List all sessions 
ls PythonApp/recordings/
# Output: session_20250731_143022/ session_20250731_150445/ ...

# Access a specific session
cd PythonApp/recordings/session_20250731_143022/

# View session summary
cat session_metadata.json

# See what happened during recording  
cat session_20250731_143022_log.json
```

### File Locations at a Glance

| Data Type | Location | Example File |
|-----------|----------|--------------|
| **Session Info** | `session_metadata.json` | Session overview & file list |
| **Event Log** | `session_YYYYMMDD_HHMMSS_log.json` | Detailed timeline of events |
| **Phone Videos** | `devices/phone_1/rgb_videos/` | `phone_1_rgb_20250731_143022.mp4` |
| **Thermal Videos** | `devices/phone_1/thermal_videos/` | `phone_1_thermal_20250731_143022.mp4` |
| **Webcam Videos** | `webcam/` | `webcam_1_20250731_143022.mp4` |
| **Sensor Data** | `devices/phone_1/sensor_data/` | `phone_1_gsr_20250731_143022.csv` |
| **Hand Analysis** | `processing/hand_segmentation/` | Cropped videos & masks |

## 📁 Understanding Your Session Folder

Each recording session creates a folder like this:

```
session_20250731_143022/
├── 📄 session_metadata.json          ← START HERE - Overview of everything
├── 📄 session_20250731_143022_log.json ← Timeline of what happened  
├── 📁 devices/                       ← Data from phones/sensors
│   ├── 📁 phone_1/
│   │   ├── 📁 rgb_videos/            ← Regular camera videos
│   │   ├── 📁 thermal_videos/        ← Heat camera videos
│   │   └── 📁 sensor_data/           ← Heart rate, stress data
│   └── 📁 phone_2/                   ← Second phone (if used)
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
4. **Check the main documentation** at `docs/DATA_STRUCTURE_DOCUMENTATION.md`

---

**Remember:** Every session creates its own folder with all data organized inside. Start with `session_metadata.json` to understand what was recorded!