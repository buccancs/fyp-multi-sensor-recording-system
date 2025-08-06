# Development Environment Setup Guide

## Overview

This guide provides comprehensive setup instructions for the Multi-Sensor Recording System development environment, addressing the specific dependencies and configuration requirements for both Python desktop controller and Android mobile application components.

## System Requirements

### Minimum Requirements
- **Operating System**: Ubuntu 20.04+ / Windows 10+ / macOS 11+
- **Python**: 3.8+ (recommended: 3.9+)
- **Java**: JDK 11+ (for Android development)
- **Android Studio**: 2023.1+ (for Android app development)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 10GB free space

## Python Environment Setup

### 1. Core Dependencies Installation

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv
sudo apt-get install qt5-default pyqt5-dev-tools
sudo apt-get install portaudio19-dev

# Install system dependencies (macOS)
brew install python3 qt5 portaudio

# Install system dependencies (Windows)
# Download and install Python 3.9+ from python.org
# Download and install Qt5 from qt.io
```

### 2. Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Dependencies

```bash
# Install core dependencies
pip install PyQt5>=5.15.0
pip install numpy>=1.21.0
pip install opencv-python>=4.5.0
pip install requests>=2.25.0
pip install cryptography>=3.4.0
pip install scipy>=1.7.0
pip install matplotlib>=3.5.0
pip install pandas>=1.3.0
pip install pillow>=8.3.0
pip install ntplib>=0.4.0
pip install pyserial

# Install testing dependencies
pip install pytest>=7.0.0
pip install pytest-cov>=4.0.0
pip install pytest-mock>=3.10.0

# Install development dependencies
pip install black isort flake8 mypy
```

### 4. Shimmer SDK Setup

```bash
# The Shimmer Python SDK is included in the repository
# Additional setup may be required for specific platforms
# See docs/shimmer_integration_readme.md for details
```

## Android Environment Setup

### 1. Android Studio Installation

1. Download and install Android Studio from [developer.android.com](https://developer.android.com/studio)
2. Install Android SDK Platform 33 (API level 33)
3. Install Android Build Tools 33.0.0+
4. Configure SDK path in Android Studio

### 2. Gradle Configuration

```bash
# Ensure Java 11+ is installed and configured
java -version

# Set JAVA_HOME environment variable
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Linux
export JAVA_HOME=/usr/local/opt/openjdk@11            # macOS
# Windows: Set via System Properties > Environment Variables
```

### 3. Dependencies Resolution

Current known issues and workarounds:

```bash
# If Gradle build fails with dependency resolution errors:
cd AndroidApp
./gradlew clean
./gradlew --refresh-dependencies

# If specific library conflicts occur:
./gradlew build --stacktrace --info
# Review output for specific dependency conflicts
```

## Running the System

### Python Desktop Controller

```bash
# Navigate to Python app directory
cd PythonApp

# Run the main application
python main.py

# Or run with enhanced web interface
python enhanced_main_with_web.py
```

### Android Application

```bash
# Navigate to Android app directory
cd AndroidApp

# Build the application
./gradlew assembleDebug

# Install on connected device
./gradlew installDebug

# Run tests (when available)
./gradlew testDebugUnitTest
```

## Testing Environment Setup

### Python Tests

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run tests (note: some tests may fail due to GUI dependencies)
pytest tests/ -v

# Run tests without GUI dependencies
pytest tests/ -v -k "not gui and not qt"
```

### Android Tests

```bash
# Android unit tests are currently under development
# Integration tests can be run via:
./gradlew connectedDebugAndroidTest  # Requires connected device
```

## Known Issues and Workarounds

### 1. PyQt5 Installation Issues

**Issue**: PyQt5 installation fails on some systems
**Workaround**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5

# macOS
brew install pyqt5

# Windows
# Use Anaconda/Miniconda and install via conda
conda install pyqt
```

### 2. Shimmer Library Compatibility

**Issue**: Shimmer SDK may not be available on all platforms
**Workaround**: The system includes fallback mock implementations for development

### 3. Android Build Dependencies

**Issue**: Gradle dependency resolution failures
**Current Status**: Under investigation
**Workaround**: Use Android Studio IDE for building until resolved

### 4. Test Execution Environment

**Issue**: Some tests require specific hardware or GUI environment
**Workaround**: Use test filtering to run subset of compatible tests

## Development Workflow

### 1. Code Quality Checks

```bash
# Python code formatting
black PythonApp/
isort PythonApp/

# Python linting
flake8 PythonApp/
mypy PythonApp/

# Android code formatting
cd AndroidApp
./gradlew ktlintFormat
```

### 2. Testing Strategy

```bash
# Run core functionality tests
pytest tests/core/ -v

# Run integration tests (requires setup)
pytest tests/integration/ -v

# Generate coverage report
pytest tests/ --cov=PythonApp --cov-report=html
```

### 3. Documentation Updates

When modifying code, ensure documentation stays synchronized:

1. Update relevant README files
2. Check thesis documentation for accuracy
3. Update API documentation if interfaces change
4. Run documentation gap analysis

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated and dependencies installed
2. **GUI not starting**: Check PyQt5 installation and X11 forwarding (if using SSH)
3. **Permission errors**: Ensure proper permissions for device access (Android development)
4. **Network connectivity**: Check firewall settings for socket communication

### Getting Help

1. Check existing documentation in `docs/` directory
2. Review issue tracker for known problems
3. Check system logs for detailed error messages
4. Ensure all dependencies match specified versions

## Contributing to Development

1. Follow code formatting standards (Black for Python, ktlint for Kotlin)
2. Write tests for new functionality
3. Update documentation when adding features
4. Check for documentation-code alignment
5. Verify build status before submitting changes

This setup guide should be updated as the development environment evolves and issues are resolved.