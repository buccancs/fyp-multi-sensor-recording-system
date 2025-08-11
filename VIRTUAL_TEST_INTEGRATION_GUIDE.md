# Virtual Test Environment - Complete Integration Guide

## 🚀 GitHub Integration Status: ✅ FULLY INTEGRATED

The virtual test environment is **fully integrated** with GitHub Actions and provides comprehensive CI/CD automation.

### GitHub Actions Workflows

#### 1. Automatic Testing on Every PR/Push
- **File**: `.github/workflows/virtual-test-environment.yml`
- **Triggers**: Push to main/develop, Pull Requests, Manual dispatch
- **Coverage**: Quick tests (10min), CI tests (15min), Performance tests (25min), Docker tests (20min)

#### 2. Matrix Testing Strategy
```yaml
Matrix Tests:
- Scenarios: [ci, quick]  
- Device counts: [2, 3, 5]
- Platforms: Ubuntu Latest
- Python: 3.11
```

#### 3. Automated Test Results
- **Artifact Collection**: All test results uploaded as artifacts
- **PR Comments**: Automatic test summary comments on pull requests  
- **Performance Monitoring**: CPU/Memory usage tracking with thresholds
- **Failure Detection**: Automatic CI failure on test failures

#### 4. Manual Workflow Dispatch
You can manually trigger tests from GitHub UI:
- Go to Actions → Virtual Test Environment
- Click "Run workflow"
- Choose scenario: `ci`, `quick`, `stress`, `sync`
- Set device count: `2-6` devices
- Set duration: `0.5-30` minutes

### GitHub Integration Features

✅ **Automatic PR Testing**: Every PR runs quick validation tests  
✅ **Multi-scenario Testing**: CI, quick, stress, and sync scenarios  
✅ **Performance Monitoring**: Memory and CPU usage tracking  
✅ **Docker Integration**: Containerized testing in CI  
✅ **Artifact Collection**: Test results, logs, and reports saved  
✅ **Test Result Validation**: JSON report parsing and pass/fail detection  
✅ **Cross-platform Support**: Linux CI with xvfb for headless operation  
✅ **Manual Triggering**: Workflow dispatch for on-demand testing  

## 🏠 Local Execution: ✅ FULLY SUPPORTED

### Quick Start (30 seconds)
```bash
# 1. Clone and navigate
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr/tests/integration/virtual_environment

# 2. Automated setup  
./setup_dev_environment.sh    # Linux/macOS
# OR
powershell -ExecutionPolicy Bypass -File setup_dev_environment.ps1  # Windows

# 3. Run test
./run_virtual_test.sh --scenario quick --devices 2 --duration 1.0
```

### Multiple Local Execution Methods

#### 1. Shell Script (Recommended)
```bash
cd tests/integration/virtual_environment

# Quick test (1 minute)
./run_virtual_test.sh --scenario quick --devices 2 --duration 1.0

# Standard CI test (3 minutes)  
./run_virtual_test.sh --scenario ci --devices 3 --duration 3.0

# Stress test (30 minutes)
./run_virtual_test.sh --scenario stress --devices 6 --duration 30.0

# Synchronization test
./run_virtual_test.sh --scenario sync --devices 4 --duration 5.0
```

#### 2. Direct Python Execution
```bash
cd tests/integration/virtual_environment

# Simple quick test
python quick_test.py

# Full test runner
python test_runner.py --scenario ci --devices 3 --duration 2.0 --verbose

# Performance benchmarks
python test_performance_benchmarks.py
```

#### 3. Pytest Integration
```bash
cd tests/integration/virtual_environment

# Run all virtual environment tests
pytest . -v

# Run specific test categories
pytest test_pytest_integration.py -v
pytest test_real_pc_integration.py -v  
pytest test_performance_benchmarks.py -v

# Run with markers
pytest -m "quick" -v
pytest -m "integration" -v
```

#### 4. Docker Local Execution
```bash
cd tests/integration/virtual_environment

# Build image
docker build -t gsr-virtual-test:local -f Dockerfile ../../..

# Run containerized test
docker run --rm \
  -v "$(pwd)/test_results:/app/test_results" \
  gsr-virtual-test:local \
  --scenario ci --devices 3 --duration 2.0

# Docker Compose (if available)
docker-compose up --build
```

#### 5. Makefile Commands
```bash
cd tests/integration/virtual_environment

# Quick commands via Makefile
make test-quick      # Quick test
make test-ci         # CI test  
make test-stress     # Stress test
make setup          # Environment setup
make clean          # Clean test results
```

### Local Development Features

✅ **Cross-Platform Setup**: Linux, macOS, Windows support  
✅ **Automated Dependencies**: Python packages, system libraries  
✅ **Virtual Environment**: Isolated Python environment creation  
✅ **VS Code Integration**: Launch configurations and debugging  
✅ **Multiple Test Scenarios**: Pre-configured test types  
✅ **Real-time Monitoring**: CPU, memory, and performance tracking  
✅ **Detailed Logging**: Configurable log levels and output  
✅ **Result Analysis**: JSON reports and performance metrics  
✅ **Cleanup Automation**: Automatic resource cleanup after tests  

## 🛠️ Developer Workflow Integration

### VS Code Integration
The virtual test environment includes complete VS Code integration:

```json
# .vscode/launch.json configurations
{
  "name": "Virtual Test Quick",
  "type": "python", 
  "program": "test_runner.py",
  "args": ["--scenario", "quick", "--devices", "2", "--duration", "1.0"]
}
```

### Development Commands
```bash
# Setup development environment
./setup_dev_environment.sh

# Run development server with hot reload  
python test_runner.py --scenario ci --devices 2 --duration 10.0 --verbose

# Debug mode with detailed logging
GSR_TEST_LOG_LEVEL=DEBUG python test_runner.py --scenario quick --devices 1

# Performance profiling
python test_performance_benchmarks.py --profile --devices 3
```

## 📊 Monitoring and Results

### Test Results Location
```
tests/integration/virtual_environment/test_results/
├── {timestamp}_quick_report.json     # Test summary
├── {timestamp}_performance.json     # Performance metrics  
├── {timestamp}_devices.log         # Device logs
├── {timestamp}_pc_server.log       # PC server logs
└── synthetic_data/                  # Generated test data
```

### Performance Metrics Tracked
- **CPU Usage**: Peak and average during test execution
- **Memory Usage**: Peak memory consumption and leak detection  
- **Data Throughput**: Samples per second for each data type
- **Synchronization Accuracy**: Timing precision between devices
- **Error Rates**: Connection failures and data corruption
- **Test Duration**: Actual vs expected test execution time

### Result Analysis
```bash
# View latest test results
cd tests/integration/virtual_environment/test_results
cat *_report.json | jq '.summary'

# Performance analysis
cat *_performance.json | jq '.performance'

# Check for test failures
grep -r "ERROR\|FAILED" *.log
```

## 🔧 Configuration Options

### Environment Variables
```bash
# CI/CD mode
export GSR_TEST_CI_MODE=true
export GSR_TEST_HEADLESS=true  

# Logging configuration
export GSR_TEST_LOG_LEVEL=INFO    # DEBUG, INFO, WARNING, ERROR

# Performance tuning
export GSR_TEST_MEMORY_LIMIT=512  # MB
export GSR_TEST_CPU_LIMIT=80      # Percentage

# Test customization
export GSR_TEST_DATA_DIR=/tmp/gsr_test_data
export GSR_TEST_PORT_BASE=12000
```

### Configuration Files
- `test_config.py`: Main test configuration
- `test_configs/`: Scenario-specific configurations
- `docker-compose.yml`: Docker environment setup
- `Dockerfile`: Container build configuration

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Port Conflicts
```bash
# Check for port usage
netstat -tuln | grep 12000

# Kill conflicting processes
pkill -f "test_runner.py"
pkill -f "virtual_device_client.py"
```

#### Memory Issues
```bash
# Monitor memory usage
htop

# Reduce device count
./run_virtual_test.sh --scenario quick --devices 1 --duration 0.5
```

#### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
./setup_dev_environment.sh

# Check Python dependencies
pip list | grep -E "(pytest|asyncio|psutil)"
```

#### Docker Issues
```bash
# Clean Docker environment
docker system prune -f

# Rebuild image
docker build --no-cache -t gsr-virtual-test:local -f Dockerfile ../../..
```

For comprehensive troubleshooting, see: `TROUBLESHOOTING.md`

## 📚 Additional Resources

- **TEST_RUNNER_README.md**: Detailed usage instructions
- **MIGRATION_GUIDE.md**: Transitioning from physical to virtual testing  
- **IMPLEMENTATION_SUMMARY.md**: Technical architecture details
- **TROUBLESHOOTING.md**: Comprehensive issue resolution guide

## ✅ Verification Checklist

To verify your integration is working:

- [ ] GitHub Actions workflow triggers on PR/push
- [ ] Local setup script completes successfully
- [ ] Quick test runs and passes locally
- [ ] Docker test builds and runs successfully  
- [ ] VS Code integration works (if using VS Code)
- [ ] Test results are generated and readable
- [ ] Performance metrics are collected
- [ ] CI tests pass in GitHub Actions

**Status**: ✅ **FULLY INTEGRATED AND READY FOR USE**

Both GitHub integration and local execution are comprehensive and production-ready.