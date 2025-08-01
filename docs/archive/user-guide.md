# User Guide

## Getting Started

The Multi-Sensor Synchronized Recording System provides a comprehensive platform for collecting synchronized data from multiple sensors including cameras, thermal imaging, and physiological sensors.

## Quick Setup

### Prerequisites

You need the following software installed:

- Java 11 or higher for Android development
- Conda or Miniconda for Python environment management  
- Git for version control

### Installation

Run the automated setup script:

```bash
python3 tools/development/setup.py
```

This will detect your platform and configure the environment automatically.

### Manual Setup

For platform-specific manual setup:

**Windows:**
```powershell
tools/development/setup_dev_env.ps1
```

**Linux/macOS:**
```bash
tools/development/setup.sh
```

## Running the Applications

### Python Desktop Application

```bash
# activate environment
conda activate thermal-env

# run the desktop controller
./gradlew :PythonApp:runDesktopApp
```

### Android Mobile Application

```bash
# build and install the APK
./gradlew :AndroidApp:assembleDebug
./gradlew :AndroidApp:installDebug
```

## Testing

### Running Tests

```bash
# run all python tests
./gradlew :PythonApp:runPythonTests

# run with pytest directly
python -m pytest

# run android tests
./gradlew :AndroidApp:testDebugUnitTest
```

### Test Coverage

Generate test coverage reports:

```bash
# python coverage
./gradlew :PythonApp:runPythonTestsWithCoverage

# coverage reports will be in PythonApp/htmlcov/
```

## Project Structure

```
bucika_gsr/
├── AndroidApp/          # mobile application
├── PythonApp/           # desktop controller
├── docs/                # documentation
│   ├── architecture/    # system architecture docs
│   ├── implementation/  # implementation reports  
│   ├── development/     # development guides
│   └── user-guide/      # user documentation
├── tools/               # development utilities
│   ├── development/     # setup and demo scripts
│   └── validation/      # testing and validation
├── calibration_data/    # sensor calibration files
└── protocol/            # communication protocol specs
```

## Troubleshooting

### Common Issues

**Environment Setup Failures:**
- Ensure Conda is installed and in your PATH
- Check that Java 11+ is available
- Run setup scripts with administrator privileges if needed

**Build Failures:**
- Clean the project: `./gradlew clean`
- Refresh dependencies: `./gradlew --refresh-dependencies`
- Check that all prerequisites are installed

**Test Failures:**
- Verify all dependencies are installed
- Check that test environment is properly configured
- Run tests individually to isolate issues

## Configuration

### Python Application

Configuration files are located in `PythonApp/src/config/`

- `webcam_config.py` - Camera configuration
- Network settings are configured in the main application

### Android Application  

Configuration is handled through Android's standard configuration mechanisms in `AndroidApp/src/main/res/`

## Data Output

Recorded data is stored in the `recordings/` directory with the following structure:

```
recordings/
└── session_YYYYMMDD_HHMMSS/
    ├── session_metadata.json
    ├── webcam_data/
    ├── thermal_data/
    └── sensor_data/
```

Each session includes comprehensive metadata about devices, timing, and data files.