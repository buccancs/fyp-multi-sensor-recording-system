# Multi-Sensor Recording System for Contactless GSR Prediction Research

[![CI/CD Status](https://github.com/buccancs/bucika_gsr/workflows/Virtual%20Test%20Environment/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/virtual-test-environment.yml)
[![Performance Tests](https://github.com/buccancs/bucika_gsr/workflows/Performance%20Monitoring/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/performance-monitoring.yml)
[![Code Quality](https://github.com/buccancs/bucika_gsr/workflows/Enhanced%20Code%20Quality/badge.svg)](https://github.com/buccancs/bucika_gsr/actions/workflows/enhanced_code_quality.yml)

A comprehensive research platform for contactless Galvanic Skin Response (GSR) prediction using multi-sensor data fusion, featuring synchronized Android mobile applications and PC-based data recording with real-time analysis capabilities.

## 🚀 Quick Start (30 seconds)

**Test the entire system without any hardware:**

```bash
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
./run_local_test.sh
```

**Comprehensive testing with multiple scenarios:**

```bash
cd tests/integration/virtual_environment
./setup_dev_environment.sh
./run_virtual_test.sh --scenario quick --devices 2 --duration 1.0
```

**Run specific test scenarios:**

```bash
./run_virtual_test.sh --scenario ci --devices 3
./run_virtual_test.sh --scenario stress --devices 5 --duration 5.0
pytest tests/integration/virtual_environment/test_pytest_integration.py -v
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

## 🔧 Comprehensive Test Environment

### Test Execution Options

**Quick Tests (1-2 minutes):**
```bash
./run_local_test.sh
python tests/integration/virtual_environment/quick_test.py
./tests/integration/virtual_environment/run_virtual_test.sh --scenario quick --devices 2
```

**CI/Development Tests (3-5 minutes):**
```bash
pytest tests/integration/virtual_environment/test_pytest_integration.py -v
./tests/integration/virtual_environment/run_virtual_test.sh --scenario ci --devices 3
pytest tests/integration/virtual_environment/ -m "quick" -v
```

**Extended Performance Tests:**
```bash
./tests/integration/virtual_environment/run_virtual_test.sh --scenario stress --devices 6 --duration 30
python tests/integration/virtual_environment/test_performance_benchmarks.py --profile
```

### Environment Setup

**Automated Setup (Recommended):**
```bash
cd tests/integration/virtual_environment

# Linux/macOS
./setup_dev_environment.sh

# Windows
powershell -ExecutionPolicy Bypass -File setup_dev_environment.ps1
```

**Manual Setup:**
```bash
pip install pytest pytest-asyncio psutil numpy opencv-python-headless
pip install -r test-requirements.txt
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
- **[📚 Architecture Documentation](architecture.md)** - System architecture overview
- **[🛠️ Troubleshooting](tests/integration/virtual_environment/TROUBLESHOOTING.md)** - Issue resolution
- **[🧪 Test Documentation](tests/integration/virtual_environment/)** - Comprehensive test guides

---

**Status**: ✅ **Production Ready** | 🧪 **Fully Tested** | 🚀 **CI/CD Integrated** | 📱 **Hardware-Free Testing**
