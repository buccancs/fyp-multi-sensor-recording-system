# GSR Recording System - Test Runner Guide

## Overview

This repository includes a comprehensive **Virtual Test Environment** that simulates multiple Android devices connecting to the PC controller, allowing you to test the entire GSR recording system without requiring physical hardware.

## Quick Start

### Prerequisites

- Python 3.10+ 
- 4GB+ RAM for multi-device tests
- Docker (optional, for containerized testing)

### 1. Setup Environment

**Automated Setup (Recommended):**
```bash
# Linux/macOS
cd tests/integration/virtual_environment
./setup_dev_environment.sh

# Windows
cd tests\integration\virtual_environment
powershell -ExecutionPolicy Bypass -File setup_dev_environment.ps1
```

**Manual Setup:**
```bash
pip install pytest pytest-asyncio psutil numpy opencv-python-headless
```

### 2. Run Tests

#### Quick Test (2 minutes)
```bash
cd tests/integration/virtual_environment
./run_virtual_test.sh --scenario quick --devices 2 --duration 1.0
```

#### CI Test (3 minutes)
```bash
./run_virtual_test.sh --scenario ci --devices 3 --duration 3.0
```

#### Stress Test (30 minutes)
```bash
./run_virtual_test.sh --scenario stress --devices 6 --duration 30.0
```

#### Simple Python Test
```bash
# From project root
python tests/integration/virtual_environment/quick_test.py
```

### 3. Docker Tests

```bash
cd tests/integration/virtual_environment

# Quick Docker test
./run_virtual_test.sh --docker --scenario quick --devices 2

# Build and run manually
docker build -t gsr-virtual-test -f Dockerfile ../../..
docker run --rm gsr-virtual-test --scenario quick --devices 2
```

## Test Scenarios

| Scenario | Duration | Devices | Purpose |
|----------|----------|---------|---------|
| `quick` | 1-2 min | 2 | Fast validation |
| `ci` | 3 min | 3 | CI/CD pipeline |
| `stress` | 30 min | 6 | Performance testing |
| `sync` | 10 min | 5 | Synchronization validation |

## Configuration

### Environment Variables
```bash
export GSR_TEST_DEVICE_COUNT=3          # Number of virtual devices
export GSR_TEST_DURATION_MINUTES=5.0    # Test duration
export GSR_TEST_CI_MODE=true             # Enable CI optimizations
export GSR_TEST_LOG_LEVEL=INFO           # Logging level
```

### Command Line Options
```bash
./run_virtual_test.sh --help
# Options:
#   -s, --scenario    Test scenario (quick, stress, sync, ci)
#   -d, --devices     Number of virtual devices 
#   -t, --duration    Test duration in minutes
#   -D, --docker      Run using Docker
#   -v, --verbose     Enable verbose output
#   -c, --ci          Run in CI mode
```

## Understanding Test Results

### Success Output
```
✓ Test quick_test: PASSED
✓ All devices connected (3/3)
✓ All sessions completed (1/1)
✓ Data integrity validation passed
✓ Synchronization validation passed
✓ Performance validation passed
Test Summary: 1/1 passed
```

### Test Reports
Results are saved to `test_results/` with detailed JSON reports:
```json
{
  "test_info": {
    "name": "quick_test",
    "duration_seconds": 62.5
  },
  "summary": {
    "overall_passed": true,
    "devices_connected": "3/3",
    "data_samples_collected": 24576
  },
  "performance": {
    "peak_memory_mb": 156.2,
    "peak_cpu_percent": 45.8
  }
}
```

## Pytest Integration

### Run Specific Test Files
```bash
# From project root
pytest tests/integration/virtual_environment/test_pytest_integration.py -v
pytest tests/integration/virtual_environment/test_real_pc_integration.py -v
pytest tests/integration/virtual_environment/test_performance_benchmarks.py -v
```

### Run All Virtual Environment Tests
```bash
pytest tests/integration/virtual_environment/ -v
```

### Pytest with Custom Markers
```bash
# Run only quick tests
pytest tests/integration/virtual_environment/ -m "quick" -v

# Run only integration tests
pytest tests/integration/virtual_environment/ -m "integration" -v
```

## VS Code Integration

Launch configurations are available in `.vscode/launch.json`:

1. **Quick Virtual Test** - Fast 2-device test
2. **CI Virtual Test** - 3-device CI validation  
3. **Debug Virtual Device** - Single device debugging
4. **Performance Benchmark** - Performance validation

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
lsof -i :9000
sudo kill <pid>
```

**Permission Issues:**
```bash
chmod +x run_virtual_test.sh
sudo chown -R $USER:$USER test_results/
```

**Memory Issues:**
```bash
export GSR_TEST_DEVICE_COUNT=1
export GSR_TEST_DURATION_MINUTES=0.5
```

**Dependencies Missing:**
```bash
cd tests/integration/virtual_environment
./setup_dev_environment.sh --fix-dependencies
```

### Debug Mode
```bash
export GSR_TEST_LOG_LEVEL=DEBUG
python tests/integration/virtual_environment/quick_test.py
```

## What Gets Tested

### Virtual Device Simulation
- ✅ Socket-based Android device simulation
- ✅ Complete JSON protocol implementation
- ✅ Device lifecycle (connect → record → disconnect)
- ✅ Realistic response delays and heartbeat

### Synthetic Data Generation
- ✅ GSR data at 128Hz with physiological patterns
- ✅ RGB video at 30fps with motion simulation
- ✅ Thermal imaging at 9fps with heat patterns
- ✅ File transfer simulation

### System Validation
- ✅ Data integrity and synchronization accuracy
- ✅ Performance monitoring (CPU, memory, throughput)
- ✅ Real PC application integration
- ✅ Multi-device coordination

### CI/CD Testing
- ✅ Automated test execution
- ✅ Performance regression detection
- ✅ Cross-platform compatibility
- ✅ Docker containerization

## Benefits

- 🚫 **No Physical Hardware Required** - Test without Android devices or sensors
- ⚡ **Fast Feedback** - Complete system tests in minutes vs hours
- 🔄 **Reproducible Results** - Deterministic synthetic data eliminates flakiness
- 🧪 **Comprehensive Coverage** - Tests all system components and edge cases
- 📊 **Performance Monitoring** - Built-in benchmarking and regression detection
- 🐳 **CI/CD Ready** - Automated testing in continuous integration pipelines

## Documentation

- **📖 [Complete Guide](tests/integration/virtual_environment/README.md)** - Comprehensive documentation
- **🔧 [Implementation Details](tests/integration/virtual_environment/IMPLEMENTATION_SUMMARY.md)** - Technical architecture
- **🆘 [Troubleshooting Guide](tests/integration/virtual_environment/TROUBLESHOOTING.md)** - Solutions for common issues
- **📋 [Migration Guide](tests/integration/virtual_environment/MIGRATION_GUIDE.md)** - Transition from physical testing

## Examples

### Basic Usage Examples
```bash
# Quick validation (30 seconds)
./run_virtual_test.sh --scenario quick --devices 1 --duration 0.5

# Development test (2 minutes)
./run_virtual_test.sh --scenario quick --devices 2 --duration 2.0 --verbose

# CI pipeline test
./run_virtual_test.sh --ci --scenario ci --devices 3

# Performance test
./run_virtual_test.sh --scenario stress --devices 5 --duration 10.0

# Docker test with custom output
./run_virtual_test.sh --docker --scenario quick --output ./my_results
```

### Python API Examples
```python
# Simple test
from tests.integration.virtual_environment import VirtualTestScenario, VirtualTestRunner

scenario = VirtualTestScenario.create_quick_test()
runner = VirtualTestRunner(scenario.config)
metrics = await runner.run_test()
print(f"Test passed: {metrics.overall_passed}")
```

## Getting Help

1. **📖 Check Documentation** - Start with this guide and the detailed README
2. **🔍 Run Diagnostics** - Use `./setup_dev_environment.sh --help`
3. **🐛 Debug Mode** - Set `GSR_TEST_LOG_LEVEL=DEBUG` for detailed logs
4. **❓ GitHub Issues** - Create an issue with the `virtual-environment` label

---

**Ready to test?** Start with: `./tests/integration/virtual_environment/run_virtual_test.sh --scenario quick --devices 2 --duration 1.0`