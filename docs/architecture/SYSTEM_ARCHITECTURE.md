# System Architecture

## Overview

The Multi-Sensor Synchronized Recording System consists of two main components:

### Android Application
- **Language**: Kotlin
- **APIs**: Camera2, Shimmer sensors, USB thermal camera SDK
- **Purpose**: Mobile data collection platform

### Python Desktop Application  
- **Framework**: PyQt5
- **Libraries**: OpenCV, NumPy, SciPy
- **Purpose**: Data analysis and system control

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Sensor Recording System                │
├─────────────────────────┬───────────────────────────────────────┤
│     Android Client      │         Python Controller            │
│                         │                                       │
│  ┌─────────────────┐   │  ┌─────────────────┐                  │
│  │   Camera2 API   │   │  │   PyQt5 GUI     │                  │
│  └─────────────────┘   │  └─────────────────┘                  │
│  ┌─────────────────┐   │  ┌─────────────────┐                  │
│  │ Shimmer Sensors │   │  │ OpenCV Calib.   │                  │
│  └─────────────────┘   │  └─────────────────┘                  │
│  ┌─────────────────┐   │  ┌─────────────────┐                  │
│  │ Thermal Camera  │   │  │ Socket Network  │                  │
│  └─────────────────┘   │  └─────────────────┘                  │
└─────────────────────────┴───────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Network   │
                    │ Communication│
                    └─────────────┘
```

## Component Interaction

1. **Data Collection**: Android app captures multi-sensor data
2. **Network Sync**: Real-time communication via socket protocol  
3. **Analysis**: Python app processes and visualizes data
4. **Calibration**: Cross-platform calibration coordination

## File Structure

```
bucika_gsr/
├── AndroidApp/          # Mobile application
├── PythonApp/           # Desktop controller
├── docs/                # Documentation
├── tools/               # Development utilities
├── calibration_data/    # Sensor calibration
└── protocol/            # Communication protocol
```