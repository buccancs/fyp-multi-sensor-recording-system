# Multi-Sensor Recording System for Contactless GSR Prediction Research

[![CI/CD Status](https://github.com/buccancs/bucika_gsr/workflows/Virtual%20Test%20Environment/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/virtual-test-environment.yml)
[![Performance Tests](https://github.com/buccancs/bucika_gsr/workflows/Performance%20Monitoring/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/performance-monitoring.yml)
[![Code Quality](https://github.com/buccancs/bucika_gsr/workflows/Enhanced%20Code%20Quality/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/enhanced_code_quality.yml)

A comprehensive research platform for contactless Galvanic Skin Response (GSR) prediction using multi-sensor data fusion, featuring synchronised Android mobile applications and PC-based data recording with real-time analysis capabilities. **Now with unified architecture eliminating code duplication across platforms through consolidated calibration, recording, and monitoring systems.**

## 🚀 Quick Start (30 seconds)

**Cross-Platform Test System:**

*Universal Python (Windows/Linux/macOS)*:
```bash
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
python run_local_tests.py
```

*Linux/macOS*:
```bash
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
./run_local_tests.sh
```

*Windows*:
```cmd
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
run_local_tests.bat
```

**Advanced testing options:**

```bash
# Quick validation (< 2 minutes)
python run_local_tests.py quick

# Complete test suite with requirements validation
python run_local_tests.py full

# Requirements traceability (thesis compliance)
python run_local_tests.py requirements

# Platform-specific testing
python run_local_tests.py pc       # Desktop application
python run_local_tests.py android  # Mobile application
python run_local_tests.py gui      # GUI tests both platforms

# Performance benchmarks
python run_local_tests.py performance
```

**Direct unified framework usage:**

```bash
# All tests with automated requirements validation
python tests_unified/runners/run_unified_tests.py

# Specific test levels
python tests_unified/runners/run_unified_tests.py --level unit
python tests_unified/runners/run_unified_tests.py --level integration

# Validate 100% FR/NFR coverage
python tests_unified/runners/run_unified_tests.py --validate-requirements
```

## 📱 System Overview

This research platform enables contactless GSR prediction through synchronised multi-sensor data collection with **unified architecture eliminating code duplication**:

- **📱 Android Mobile Application**: Real-time RGB video and thermal imaging capture with unified UI architecture and camera switching capabilities
- **🖥️ PC Controller Application**: Centralized data recording and synchronisation with enhanced device coordination
- **📊 Shimmer GSR Sensors**: Ground truth physiological measurements with improved initialization timing
- **🧪 Virtual Test Environment**: Complete system simulation without hardware dependencies
- **⚡ Real-time Processing**: Live data analysis and visualisation with sub-millisecond precision
- **🔄 Unified Architecture**: **Consolidated calibration, recording, and monitoring systems** eliminating duplication between Android and Python platforms
- **🌐 Shared Protocols**: Common data structures and network protocols ensuring consistency across platforms

## ✨ Key Features

### 🔧 Unified Architecture & Code Consolidation
- **Consolidated Calibration System**: Single unified CalibrationManager eliminating duplicate implementations
- **Unified Data Recording**: Comprehensive UnifiedDataRecorder consolidating separate recording systems
- **Consolidated Logging Framework**: Single logging system with backwards compatibility across platforms
- **Shared Protocol Framework**: Common data structures and network protocols for Android and Python apps
- **System Monitoring**: Unified performance optimization and resource management

### 🔧 Hardware-Free Testing
- **Virtual Device Simulation**: Test with 2-6 simulated Android devices
- **Realistic Data Generation**: GSR (128Hz), RGB (30fps), Thermal (9fps)
- **Complete Protocol Simulation**: Full message exchange and file transfer
- **No Physical Dependencies**: Test entire system without hardware

### 📊 Multi-Sensor Data Fusion with Unified Components
- **Synchronised Recording**: Precise timestamp alignment across all sensors with improved initialization coordination
- **Multiple Data Streams**: GSR, RGB video, thermal imaging, device metadata
- **Camera Preview Switching**: Toggle between RGB and thermal camera views with real-time preview control
- **Unified Architecture**: **Consolidated components eliminating code duplication** between platforms
- **Enhanced Error Handling**: Improved camera initialization timing preventing "CameraRecorder not initialized" errors
- **Real-time Visualisation**: Live data monitoring and analysis with consistent UI patterns
- **Data Export**: CSV, JSON, and binary formats for research analysis

### 🌐 Network Communication
- **Bluetooth Low Energy (BLE)**: Efficient mobile-PC communication
- **JSON Protocol**: Structured message exchange and control
- **File Transfer**: Secure video and thermal data transmission
- **Heartbeat Monitoring**: Connection health and automatic recovery
- **Enhanced Device Coordination**: Improved initialization timing and error recovery

### 🧪 Comprehensive Testing Framework
- **4 Test Scenarios**: Quick (1min), CI (3min), Stress (30min), Sync validation
- **Cross-Platform Support**: Windows, Linux, macOS with multiple runner options
- **GitHub Actions Integration**: Automated CI/CD with full test coverage
- **Performance Monitoring**: CPU, memory, and throughput analysis
- **GUI Testing**: Complete UI/UX validation for both desktop and mobile platforms
- **Component Testing**: Comprehensive tests for unified UI components and camera switching functionality

## 🏃‍♂️ Getting Started

### Prerequisites
- Python 3.7+ (for PC application and virtual testing)
- Android 8.0+ (for mobile application)  
- 4GB+ RAM (for multi-device virtual testing)
- Windows 10+, Linux, or macOS (cross-platform support)
- Optional: Shimmer GSR+ sensors for ground truth data

### Installation Methods

#### 1. Quick Test Run (Recommended First Step)

*Universal Cross-Platform*:
```bash
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
python run_local_tests.py  # Works on Windows, Linux, macOS
```

*Platform-Specific*:
```bash
# Linux/macOS
./run_local_tests.sh

# Windows (Batch)
run_local_tests.bat

# Windows (PowerShell)
.\run_local_tests.ps1
```

#### 2. Virtual Test Environment Setup
```bash
cd tests/integration/virtual_environment

# Automated setup (Linux/macOS)
./setup_dev_environment.sh

# Windows setup
powershell -ExecutionPolicy Bypass -File setup_dev_environment.ps1

# Run various test scenarios
./run_virtual_test.sh --scenario quick --devices 2    # Quick test
./run_virtual_test.sh --scenario ci --devices 3       # CI test  
./run_virtual_test.sh --scenario stress --devices 6   # Stress test
```

#### 3. Manual Python Setup
```bash
# Install dependencies
pip install pytest pytest-asyncio psutil numpy opencv-python-headless

# Run tests directly
cd tests/integration/virtual_environment
python quick_test.py                    # Simple test
python test_runner.py --scenario ci     # Full test runner
pytest . -v                            # Pytest integration
```

#### 4. Docker Environment
```bash
cd tests/integration/virtual_environment
docker build -t gsr-virtual-test -f Dockerfile ../../..
docker run --rm -v "$(pwd)/test_results:/app/test_results" gsr-virtual-test --scenario ci
```

### Real Hardware Setup

For actual data collection with physical devices:

1. **Android Application**: Install APK from `AndroidApp/` directory
2. **PC Application**: Run `python PythonApp/main.py` 
3. **Shimmer Sensors**: Pair GSR+ devices via Bluetooth
4. **Network Setup**: Configure WiFi/Bluetooth connectivity

## 🧪 Testing & Development

### Virtual Test Scenarios

| Scenario | Duration | Devices | Purpose |
|----------|----------|---------|---------|
| `quick`  | 1 min    | 2       | Fast validation |
| `ci`     | 3 min    | 3       | Continuous integration |
| `stress` | 30 min   | 6       | Performance testing |
| `sync`   | 5 min    | 4       | Synchronisation validation |

### GitHub Actions Integration

The repository includes comprehensive CI/CD automation:

- **✅ Automatic Testing**: Every PR triggers virtual test validation
- **✅ Matrix Testing**: Multiple scenarios and device configurations  
- **✅ Performance Monitoring**: Memory and CPU usage tracking
- **✅ Docker Testing**: Containerized environment validation
- **✅ Manual Dispatch**: On-demand testing via GitHub UI

View live test results: [GitHub Actions](https://github.com/buccancs/bucika_gsr/actions)

### Development Workflow

```bash
# Development setup
cd tests/integration/virtual_environment
./setup_dev_environment.sh

# Run tests during development
./run_virtual_test.sh --scenario quick --devices 2 --verbose

# Debug mode
GSR_TEST_LOG_LEVEL=DEBUG python test_runner.py --scenario quick

# Performance profiling  
python test_performance_benchmarks.py --profile
```

## 📊 Performance & Validation

### Benchmarks
- **Data Throughput**: 128 GSR samples/sec, 30 RGB frames/sec, 9 thermal frames/sec
- **Memory Usage**: <200MB for 3-device tests, <500MB for stress tests
- **CPU Usage**: <50% average, <80% peak during multi-device operation
- **Synchronisation**: <10ms timing accuracy between devices

### Test Coverage
- **✅ Protocol Validation**: Complete JSON message exchange testing
- **✅ Data Integrity**: Checksum validation and corruption detection
- **✅ Connection Handling**: Device connect/disconnect scenarios
- **✅ Performance Testing**: Memory leak detection and resource monitoring
- **✅ Real PC Integration**: End-to-end validation with actual PC application

## 🛠️ Unified Testing Framework

### Consolidated Research-Grade Testing Infrastructure

All testing has been consolidated into a single, comprehensive framework that **eliminates duplication** and provides consistent execution across all test types. **Code consolidation has unified calibration, recording, and monitoring systems** with full backwards compatibility.

**Quick Start - Recommended:**
```bash
# 30-second validation (works on all platforms)
python run_local_tests.py quick

# Complete test suite with dependency installation
python run_local_tests.py full --install-deps

# Platform-specific testing
python run_local_tests.py pc       # Desktop application tests
python run_local_tests.py android  # Mobile application tests
python run_local_tests.py gui      # GUI tests both platforms
```

**Advanced Testing Options:**
```bash
# Direct unified framework usage
python tests_unified/runners/run_unified_tests.py --quick

# Test specific levels
python tests_unified/runners/run_unified_tests.py --level unit
python tests_unified/runners/run_unified_tests.py --level integration
python tests_unified/runners/run_unified_tests.py --level system
python tests_unified/runners/run_unified_tests.py --level performance
```

**Academic Compliance Testing:**
```bash
# Validate all Functional & Non-Functional Requirements (FR/NFR)
python tests_unified/runners/run_unified_tests.py --validate-requirements

# Generate requirements traceability report
python tests_unified/runners/run_unified_tests.py --report-requirements-coverage

# Research mode with comprehensive analysis
python tests_unified/runners/run_unified_tests.py --mode research --all-levels
```

**Technology-Specific Testing:**
```bash
# Android application testing
python tests_unified/runners/run_unified_tests.py --category android

# Hardware integration testing
python tests_unified/runners/run_unified_tests.py --category hardware

# Visual validation testing
python tests_unified/runners/run_unified_tests.py --category visual
```

### Framework Architecture

**Consolidated 4-Layer Testing Hierarchy:**
- **Unit** (`tests_unified/unit/`): Component-level validation
- **Integration** (`tests_unified/integration/`): Cross-component testing  
- **System** (`tests_unified/system/`): End-to-end workflow validation
- **Performance** (`tests_unified/performance/`): Benchmarks and quality metrics
- **Evaluation** (`tests_unified/evaluation/`): Research validation and quality assessment

**Key Consolidation Benefits:**
- ✅ **Single Source of Truth**: All tests in `tests_unified/` directory
- ✅ **Eliminated Code Duplication**: **Unified calibration, recording, and logging systems**
- ✅ **Consistent Execution**: Universal test runners work across all platforms
- ✅ **Improved CI/CD**: Streamlined GitHub workflows with faster execution
- ✅ **Shared Protocols**: Common data structures and network protocols for both Android and Python platforms

**Architecture Improvements:**
- **Consolidated CalibrationManager**: Single implementation replacing duplicate classes
- **Unified DataRecorder**: Comprehensive recording system with production-grade validation
- **Shared Logging Framework**: Backwards-compatible logging with enhanced features
- **Common Protocols**: Standardized data structures in `shared_protocols/` module

**Requirements Coverage:** 15/15 FR/NFR requirements (100%) with automated validation
**Academic Compliance:** Full traceability aligned with thesis documentation
**CI/CD Integration:** All GitHub workflows updated for unified testing

📖 **Detailed Documentation:** [`tests_unified/README.md`](tests_unified/README.md)

### Environment Setup

**Unified Framework Setup (Recommended):**
```bash
# Install dependencies and run tests
./run_local_tests.sh --install-deps

# Or manually
pip install -r test-requirements.txt
pip install -e .
```

**Legacy Environment Setup:**
```bash
# Linux/macOS
cd tests/integration/virtual_environment
./setup_dev_environment.sh

# Windows
powershell -ExecutionPolicy Bypass -File setup_dev_environment.ps1
```

**Docker Setup:**
```bash
cd tests/integration/virtual_environment
docker build -t gsr-virtual-test -f Dockerfile ../../..
docker run --rm -v "$(pwd)/test_results:/app/test_results" gsr-virtual-test --scenario ci
```

### Configuration Options

Set environment variables for custom testing:
```bash
export GSR_TEST_LOG_LEVEL=DEBUG         # Enable debug logging
export GSR_TEST_DURATION=300            # Set custom test duration (seconds)
export GSR_TEST_DEVICE_COUNT=5          # Set device count
export GSR_TEST_PERFORMANCE_MODE=true   # Enable performance monitoring
```

## 🔍 Troubleshooting

### Common Issues and Solutions

**Python Environment Issues:**
```bash
# Fix Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip install --force-reinstall -r test-requirements.txt

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
```

**Test Failures:**
```bash
# Run with verbose output
./tests/integration/virtual_environment/run_virtual_test.sh --scenario quick --verbose

# Check test logs
cat tests/integration/virtual_environment/test_results/latest/test_log.txt

# Debug mode
GSR_TEST_LOG_LEVEL=DEBUG python tests/integration/virtual_environment/test_runner.py
```

**Performance Issues:**
- Reduce device count for lower-spec systems: `--devices 2`
- Use quick scenario for fast validation: `--scenario quick`
- Monitor system resources: `htop` or Task Manager
- Free memory before tests: restart terminal/IDE

**Windows-Specific Issues:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Use PowerShell script
cd tests\integration\virtual_environment
powershell -File setup_dev_environment.ps1
```

### Support Resources
- **Test Logs**: Check `tests/integration/virtual_environment/test_results/`
- **GitHub Issues**: Report problems with test output logs
- **Debug Mode**: Use `GSR_TEST_LOG_LEVEL=DEBUG` for detailed information

## 🛠️ Project Structure

```
bucika_gsr/
├── AndroidApp/                    # Android mobile application
├── PythonApp/                     # PC controller application  
│   ├── calibration/              # Unified calibration system
│   ├── recording/                # Consolidated data recording
│   ├── utils/                    # Unified logging and utilities
│   └── session/                  # Session management
├── shared_protocols/              # Common data structures and protocols
│   ├── data_structures.py        # Shared data formats
│   ├── network_protocol.py       # Common message formats
│   └── system_monitoring.py      # Unified monitoring
├── tests_unified/                 # Consolidated test framework
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── system/                   # System tests
│   └── performance/              # Performance benchmarks
├── tests/
│   └── integration/
│       └── virtual_environment/   # Virtual test framework
├── .github/workflows/             # CI/CD automation
├── docs/                         # Additional documentation
└── run_local_test.sh             # One-click local testing
```

## 🔬 Research Applications

This platform supports various research scenarios:

- **Stress Detection**: Real-time physiological response monitoring
- **Emotion Recognition**: Multi-modal data fusion for affective computing
- **Human-Computer Interaction**: Contactless interface development
- **Biomedical Research**: Non-invasive physiological measurement validation
- **Machine Learning**: Training data collection for GSR prediction models

## 🤝 Contributing

### Development Environment
```bash
# Setup development environment
cd tests/integration/virtual_environment
./setup_dev_environment.sh

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run comprehensive tests
./run_virtual_test.sh --scenario ci --devices 3 --verbose
```

### Testing Your Changes
```bash
# Quick validation
./run_virtual_test.sh --scenario quick --devices 2

# Full test suite
pytest tests/integration/virtual_environment/ -v

# Performance validation  
python tests/integration/virtual_environment/test_performance_benchmarks.py
```

## 📄 Licence

This project is licensed under the MIT Licence - see the [LICENCE](LICENCE) file for details.

## 🙏 Acknowledgments

- **UCL Department of Computer Science** - Research supervision and support
- **Shimmer Research** - GSR sensor hardware and SDK
- **Android Community** - Mobile development frameworks and libraries
- **Python Scientific Computing Stack** - Data processing and analysis tools

## 🔗 Quick Links

- **[🚀 Run Tests Now](./run_local_test.sh)** - One-click local testing
- **[📊 GitHub Actions](https://github.com/buccancs/bucika_gsr/actions)** - Live CI/CD status
- **[📚 Architecture Documentation](architecture.md)** - System architecture overview
- **[🛠️ Troubleshooting](tests/integration/virtual_environment/TROUBLESHOOTING.md)** - Issue resolution
- **[🧪 Test Documentation](tests/integration/virtual_environment/)** - Comprehensive test guides

---

**Status**: ✅ **Production Ready** | 🧪 **Fully Tested** | 🚀 **CI/CD Integrated** | 📱 **Hardware-Free Testing**
