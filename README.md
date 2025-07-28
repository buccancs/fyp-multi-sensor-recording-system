# Multi-Sensor Synchronized Recording System

A comprehensive monorepo project combining an **Android mobile app** (Kotlin, Camera2 API, Shimmer sensors, USB thermal camera SDK) with a **Python desktop controller app** (PyQt5 UI, OpenCV for calibration, and socket networking) for synchronized multi-modal data recording.

## 🎯 Project Overview

This system enables synchronized recording from multiple data sources:
- **2 Android smartphones** (Samsung S22) with attached thermal cameras
- **2 Logitech Brio 4K USB webcams** connected to a Windows PC
- **Shimmer3 GSR+ physiological sensors** for biometric data
- **Windows PC controller** acting as the master orchestrator

The system is designed for research applications, particularly for capturing synchronized video, thermal, and physiological data during stimulus presentation experiments.

## 🏗️ Architecture

### Monorepo Structure
```
project-root/
├── settings.gradle              # Gradle settings: includes both modules
├── build.gradle                 # Root Gradle build configuration
├── gradle/wrapper/              # Gradle Wrapper files
├── gradlew & gradlew.bat        # Gradle wrapper scripts
├── AndroidApp/                  # Android app module (Kotlin + Camera2, Shimmer, etc.)
│   ├── build.gradle             # Android module build configuration
│   ├── src/main/                # Android source code
│   │   ├── AndroidManifest.xml  # Android app manifest
│   │   ├── java/...             # Kotlin source packages
│   │   └── res/...              # Android resources
├── PythonApp/                   # Python desktop app module (PyQt5, OpenCV)
│   ├── build.gradle             # Python module build configuration
│   ├── src/                     # Python source files
│   │   └── main.py              # Entry-point script for PyQt5 app
├── docs/                        # Project documentation
├── changelog.md                 # Project changelog
├── todo.md                      # Task tracking
└── .gitignore                   # Git ignore file
```

## 🚀 Quick Start

### Prerequisites

1. **Android Studio** (Arctic Fox or later)
2. **Python 3.8+** installed and available in PATH
3. **Java 8+** (usually included with Android Studio)
4. **Git** for version control

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd MultiSensorRecordingSystem
   ```

2. **Open in Android Studio:**
   - Launch Android Studio
   - Choose "Open an existing project"
   - Select the project root directory
   - Wait for Gradle sync to complete

3. **Install Python Plugin (if not already installed):**
   - Go to `File > Settings > Plugins > Marketplace`
   - Search for "Python" and install "Python Community Edition"
   - Restart Android Studio if prompted

4. **Verify Setup:**
   - The project should sync successfully
   - You should see both `AndroidApp` and `PythonApp` modules in the project view

## 🔧 Development Workflow

### Building the Android App

```bash
# Build debug APK
./gradlew :AndroidApp:assembleDebug

# Install on connected device
./gradlew :AndroidApp:installDebug
```

### Running the Python Desktop App

```bash
# Install Python dependencies and run the app
./gradlew :PythonApp:runDesktopApp

# Test Python environment setup
./gradlew :PythonApp:testPythonSetup

# Run calibration routines
./gradlew :PythonApp:runCalibration
```

### Available Gradle Tasks

- **Android Module:**
  - `assembleDebug` - Build debug APK
  - `assembleRelease` - Build release APK
  - `installDebug` - Install debug APK on connected device

- **Python Module:**
  - `pipInstall` - Install Python dependencies
  - `runDesktopApp` - Launch PyQt5 desktop controller
  - `runCalibration` - Run camera calibration routines
  - `testPythonSetup` - Verify Python environment

## 🛠️ Technology Stack

### Android App (Kotlin)
- **Language:** Kotlin
- **UI:** Android Views with ViewBinding
- **Camera:** Camera2 API for 4K recording + RAW capture
- **Networking:** OkHttp for socket communication
- **Dependency Injection:** Hilt
- **Concurrency:** Kotlin Coroutines
- **Architecture:** Clean Architecture with Repository pattern

### Python Desktop App
- **Language:** Python 3.8+
- **UI Framework:** PyQt5 5.15.7
- **Computer Vision:** OpenCV 4.8.0.74
- **Numerical Computing:** NumPy 1.24.3
- **Networking:** WebSockets, Requests
- **Image Processing:** Pillow

### Build System
- **Primary:** Gradle 8.4 with multi-project setup
- **Android Plugin:** 8.1.2
- **Python Integration:** ru.vyarus.use-python plugin 3.0.0

## 📱 Android App Features

### Current Implementation (Milestone 1)
- ✅ Project structure and build configuration
- ✅ Essential permissions and manifest setup
- ✅ Dependency injection setup (Hilt)
- ✅ Camera2 API dependencies

### Planned Features (Milestone 2+)
- 🔄 4K RGB video recording with RAW image capture
- 🔄 Thermal camera integration (Topdon SDK)
- 🔄 Shimmer3 GSR+ sensor Bluetooth communication
- 🔄 Real-time preview streaming to PC
- 🔄 Socket-based remote control interface
- 🔄 Local data storage and session management

## 🖥️ Desktop Controller Features

### Current Implementation (Milestone 1)
- ✅ PyQt5 GUI with device status monitoring
- ✅ Recording control interface (start/stop/calibration)
- ✅ System logging and status updates
- ✅ Extensible architecture for sensor integration

### Planned Features (Milestone 3+)
- 🔄 Real device communication protocols
- 🔄 USB webcam capture and recording
- 🔄 Camera calibration algorithms (intrinsic/extrinsic)
- 🔄 Stimulus presentation system
- 🔄 Data synchronization and export tools

## 🔧 Configuration

### Python Dependencies
The Python environment is managed automatically by Gradle. Dependencies are specified in `PythonApp/build.gradle`:

```gradle
python {
    pip 'pyqt5:5.15.7'
    pip 'opencv-python:4.8.0.74'
    pip 'numpy:1.24.3'
    pip 'requests:2.31.0'
    pip 'websockets:11.0.3'
    pip 'pillow:10.0.0'
}
```

### Android Configuration
Key Android settings in `AndroidApp/build.gradle`:
- **Compile SDK:** 34
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 34
- **Namespace:** `com.multisensor.recording`

## 🧪 Testing

### Running Tests
```bash
# Android unit tests
./gradlew :AndroidApp:test

# Android instrumented tests
./gradlew :AndroidApp:connectedAndroidTest

# Python environment test
./gradlew :PythonApp:testPythonSetup
```

## 📋 Development Guidelines

### Code Style
- **Kotlin:** Follow official Kotlin coding conventions
- **Python:** Follow PEP 8 style guide
- **Comments:** Minimal commenting, focus on self-documenting code
- **Cognitive Complexity:** Keep under 15 per function

### Git Workflow
- Use feature branches for new development
- Update `changelog.md` for all significant changes
- Update `todo.md` for incomplete work or future ideas
- Keep commits atomic and well-described

### Documentation
- Always maintain up-to-date documentation
- Generate Mermaid diagrams for architectural changes
- Update README.md for setup or workflow changes

## 🚨 Troubleshooting

### Common Issues

**Gradle Sync Fails:**
- Ensure Python is installed and in PATH
- Check internet connection for dependency downloads
- Try `./gradlew clean` and sync again

**Python Module Import Errors:**
- Run `./gradlew :PythonApp:pipInstall` to install dependencies
- Verify Python version is 3.8 or higher
- Check that virtual environment is created in `.gradle/python/`

**Android Build Errors:**
- Ensure Android SDK is properly configured
- Check that `local.properties` points to correct SDK location
- Verify all required Android SDK components are installed

**IDE Integration Issues:**
- Install Python plugin in Android Studio
- Ignore "No Python interpreter" warnings (expected)
- Use Gradle tasks to run Python code instead of IDE run configurations

## 📚 Documentation

- **Architecture:** See `docs/markdown/architecture.md`
- **Milestones:** See `docs/markdown/` for detailed implementation guides
- **Changelog:** See `changelog.md` for version history
- **TODO:** See `todo.md` for pending tasks and future work

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Update documentation as needed
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for multi-sensor research applications
- Inspired by modern Android development practices
- Leverages proven Python scientific computing stack
- Designed for Windows development environments

---

**Status:** Milestone 1 Complete ✅  
**Next:** Milestone 2.1 - Android Application Implementation  
**Last Updated:** 2025-07-28