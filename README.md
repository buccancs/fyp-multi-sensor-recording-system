# Multi-Sensor Recording System for Contactless GSR Prediction Research

[![CI/CD Status](https://github.com/buccancs/bucika_gsr/workflows/Virtual%20Test%20Environment/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/virtual-test-environment.yml)
[![Performance Tests](https://github.com/buccancs/bucika_gsr/workflows/Performance%20Monitoring/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/performance-monitoring.yml)
[![Code Quality](https://github.com/buccancs/bucika_gsr/workflows/Enhanced%20Code%20Quality/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/enhanced_code_quality.yml)

A comprehensive research platform for contactless Galvanic Skin Response (GSR) prediction using multi-sensor data fusion, featuring synchronized Android mobile applications and PC-based data recording with real-time analysis capabilities.

## 🚀 Quick Start (30 seconds)

**Test the entire system without any hardware:**

```bash
# Clone and run immediately
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
./run_local_test.sh
```

**Or run comprehensive tests:**

```bash
cd tests/integration/virtual_environment
./setup_dev_environment.sh                    # Automated setup
./run_virtual_test.sh --scenario quick --devices 2 --duration 1.0
```

## 📱 System Overview

This research platform enables contactless GSR prediction through synchronized multi-sensor data collection:

- **📱 Android Mobile Application**: Real-time RGB video and thermal imaging capture
- **🖥️ PC Controller Application**: Centralized data recording and synchronization
- **📊 Shimmer GSR Sensors**: Ground truth physiological measurements
- **🧪 Virtual Test Environment**: Complete system simulation without hardware
- **⚡ Real-time Processing**: Live data analysis and visualization

## ✨ Key Features

### 🔧 Hardware-Free Testing
- **Virtual Device Simulation**: Test with 2-6 simulated Android devices
- **Realistic Data Generation**: GSR (128Hz), RGB (30fps), Thermal (9fps)
- **Complete Protocol Simulation**: Full message exchange and file transfer
- **No Physical Dependencies**: Test entire system without hardware

### 📊 Multi-Sensor Data Fusion
- **Synchronized Recording**: Precise timestamp alignment across all sensors
- **Multiple Data Streams**: GSR, RGB video, thermal imaging, device metadata
- **Real-time Visualization**: Live data monitoring and analysis
- **Data Export**: CSV, JSON, and binary formats for research analysis

### 🌐 Network Communication
- **Bluetooth Low Energy (BLE)**: Efficient mobile-PC communication
- **JSON Protocol**: Structured message exchange and control
- **File Transfer**: Secure video and thermal data transmission
- **Heartbeat Monitoring**: Connection health and automatic recovery

### 🧪 Comprehensive Testing Framework
- **4 Test Scenarios**: Quick (1min), CI (3min), Stress (30min), Sync validation
- **GitHub Actions Integration**: Automated CI/CD with full test coverage
- **Performance Monitoring**: CPU, memory, and throughput analysis
- **Cross-Platform Support**: Linux, macOS, Windows compatibility

## 🏃‍♂️ Getting Started

### Prerequisites
- Python 3.10+ (for PC application and virtual testing)
- Android 8.0+ (for mobile application)
- 4GB+ RAM (for multi-device virtual testing)
- Optional: Shimmer GSR+ sensors for ground truth data

### Installation Methods

#### 1. Quick Test Run (Recommended First Step)
```bash
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
./run_local_test.sh  # Automated setup and test execution
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
| `sync`   | 5 min    | 4       | Synchronization validation |

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
- **Synchronization**: <10ms timing accuracy between devices

### Test Coverage
- **✅ Protocol Validation**: Complete JSON message exchange testing
- **✅ Data Integrity**: Checksum validation and corruption detection
- **✅ Connection Handling**: Device connect/disconnect scenarios
- **✅ Performance Testing**: Memory leak detection and resource monitoring
- **✅ Real PC Integration**: End-to-end validation with actual PC application

## 📚 Documentation

### Comprehensive Guides
- **[VIRTUAL_TEST_INTEGRATION_GUIDE.md](VIRTUAL_TEST_INTEGRATION_GUIDE.md)**: Complete GitHub and local integration guide
- **[TEST_RUNNER_README.md](TEST_RUNNER_README.md)**: Detailed test execution instructions  
- **[tests/integration/virtual_environment/MIGRATION_GUIDE.md](tests/integration/virtual_environment/MIGRATION_GUIDE.md)**: Transition from physical to virtual testing
- **[tests/integration/virtual_environment/TROUBLESHOOTING.md](tests/integration/virtual_environment/TROUBLESHOOTING.md)**: Issue resolution guide

### Technical Documentation
- **[tests/integration/virtual_environment/IMPLEMENTATION_SUMMARY.md](tests/integration/virtual_environment/IMPLEMENTATION_SUMMARY.md)**: Architecture details
- **[architecture.md](architecture.md)**: System architecture overview
- **[protocol/](protocol/)**: Communication protocol specifications

## 🛠️ Project Structure

```
bucika_gsr/
├── AndroidApp/                    # Android mobile application
├── PythonApp/                     # PC controller application  
├── tests/
│   └── integration/
│       └── virtual_environment/   # Virtual test framework
│           ├── run_virtual_test.sh       # Main test runner
│           ├── setup_dev_environment.sh  # Automated setup
│           ├── test_runner.py           # Python test orchestrator
│           ├── virtual_device_client.py # Virtual device simulation
│           └── synthetic_data_generator.py # Test data generation
├── .github/workflows/             # CI/CD automation
├── protocol/                      # Communication specifications
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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **UCL Department of Computer Science** - Research supervision and support
- **Shimmer Research** - GSR sensor hardware and SDK
- **Android Community** - Mobile development frameworks and libraries
- **Python Scientific Computing Stack** - Data processing and analysis tools

## 🔗 Quick Links

- **[🚀 Run Tests Now](./run_local_test.sh)** - One-click local testing
- **[📊 GitHub Actions](https://github.com/buccancs/bucika_gsr/actions)** - Live CI/CD status
- **[📚 Complete Integration Guide](VIRTUAL_TEST_INTEGRATION_GUIDE.md)** - Full setup documentation
- **[🧪 Test Runner Guide](TEST_RUNNER_README.md)** - Detailed testing instructions
- **[🛠️ Troubleshooting](tests/integration/virtual_environment/TROUBLESHOOTING.md)** - Issue resolution

---

**Status**: ✅ **Production Ready** | 🧪 **Fully Tested** | 🚀 **CI/CD Integrated** | 📱 **Hardware-Free Testing**
