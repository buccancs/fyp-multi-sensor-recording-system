# Virtual Test Environment Troubleshooting Guide

This guide helps resolve common issues when working with the Virtual Test Environment for the GSR Recording System.

## 🔧 Setup and Installation Issues

### Python Version Compatibility

**Problem**: ImportError or syntax errors when importing virtual environment modules
```
ImportError: cannot import name 'VirtualTestScenario'
SyntaxError: invalid syntax
```

**Solution**:
1. Ensure Python 3.10 or higher is installed:
   ```bash
   python --version  # Should show 3.10.0 or higher
   ```
2. Use the setup script:
   ```bash
   cd tests/integration/virtual_environment
   ./setup_dev_environment.sh
   ```

### Dependency Installation Issues

**Problem**: Missing dependencies (numpy, opencv, psutil, etc.)
```
ModuleNotFoundError: No module named 'numpy'
ModuleNotFoundError: No module named 'cv2'
```

**Solution**:
1. Install virtual environment dependencies:
   ```bash
   pip install pytest pytest-asyncio psutil numpy opencv-python-headless
   ```
2. For headless environments, use opencv-python-headless instead of opencv-python
3. Install project in development mode:
   ```bash
   pip install -e .
   ```

### Import Path Issues

**Problem**: Cannot import virtual environment modules
```
ImportError: No module named 'tests.integration.virtual_environment'
```

**Solution**:
1. Ensure you're running from the project root directory
2. Add project root to Python path:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent.parent))
   ```

## 🌐 Network and Connection Issues

### Port Conflicts

**Problem**: Tests fail with port binding errors
```
OSError: [Errno 98] Address already in use
socket.error: [Errno 98] Address already in use
```

**Solution**:
1. Check for processes using ports 9000-9010:
   ```bash
   netstat -tlnp | grep 900
   lsof -i :9000
   ```
2. Kill conflicting processes:
   ```bash
   sudo kill -9 <PID>
   ```
3. Use different ports in configuration:
   ```python
   config = VirtualTestConfig(
       server_port=9500,  # Use non-standard port
       # ... other settings
   )
   ```

### Connection Timeouts

**Problem**: Virtual devices fail to connect or timeout
```
asyncio.TimeoutError: Device connection timed out
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solution**:
1. Increase connection timeout:
   ```python
   device_config = VirtualDeviceConfig(
       connection_timeout_seconds=10.0,  # Increase from default 5.0
       response_delay_ms=100,  # Reduce for faster response
   )
   ```
2. Check firewall settings:
   ```bash
   sudo ufw status
   sudo iptables -L
   ```
3. Use localhost explicitly:
   ```python
   server_host="127.0.0.1"  # Instead of "localhost"
   ```

### Network Interface Issues

**Problem**: Connection failures on specific network interfaces
```
ConnectionError: Cannot connect to server
```

**Solution**:
1. Bind to all interfaces in server configuration:
   ```python
   pc_server = PCServer(host="0.0.0.0", port=9000)
   ```
2. Check available network interfaces:
   ```bash
   ip addr show
   ifconfig
   ```

## 🧪 Test Execution Issues

### Async Test Hanging

**Problem**: Async tests hang indefinitely
```
# Test never completes, no output
```

**Solution**:
1. Use proper async cleanup:
   ```python
   @pytest.mark.asyncio
   async def test_example():
       runner = VirtualTestRunner(config, logger)
       try:
           result = await asyncio.wait_for(runner.run_test(), timeout=30.0)
       finally:
           await runner.cleanup()  # Ensure cleanup
   ```
2. Check for infinite loops in virtual device code
3. Add timeout to async operations:
   ```python
   await asyncio.wait_for(operation(), timeout=10.0)
   ```

### Pytest Collection Warnings

**Problem**: Pytest shows warnings about test class collection
```
PytestCollectionWarning: cannot collect test class 'TestScenario' because it has a __init__ constructor
```

**Solution**:
1. Rename classes that conflict with pytest conventions:
   ```python
   # Instead of TestScenario, use:
   class VirtualTestScenario:
       pass
   
   # Instead of TestMetrics, use:
   class VirtualTestMetrics:
       pass
   ```
2. Use pytest fixtures instead of __init__ constructors in test classes

### Memory Issues

**Problem**: Tests fail with out of memory errors
```
MemoryError: Unable to allocate array
OSError: [Errno 12] Cannot allocate memory
```

**Solution**:
1. Reduce test intensity:
   ```python
   config = VirtualTestConfig(
       device_count=2,  # Reduce from higher numbers
       gsr_sampling_rate_hz=32,  # Reduce from 128
       rgb_fps=5,  # Reduce from 30
       test_duration_minutes=0.1,  # Shorten test
   )
   ```
2. Disable resource-intensive features:
   ```python
   config = VirtualTestConfig(
       simulate_file_transfers=False,
       save_detailed_logs=False,
       enable_stress_events=False,
   )
   ```
3. Check available memory:
   ```bash
   free -h
   top
   ```

## 🐳 Docker Issues

### Docker Build Failures

**Problem**: Docker build fails with dependency errors
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solution**:
1. Update Docker base image:
   ```dockerfile
   FROM python:3.11-slim-bullseye  # Use newer image
   ```
2. Install system dependencies:
   ```dockerfile
   RUN apt-get update && apt-get install -y \
       build-essential \
       libffi-dev \
       libssl-dev
   ```
3. Clear Docker cache:
   ```bash
   docker system prune -a
   ```

### Docker Runtime Issues

**Problem**: Container fails to run tests
```
docker: Error response from daemon: container crashed
```

**Solution**:
1. Check container logs:
   ```bash
   docker logs <container_id>
   ```
2. Run with interactive mode for debugging:
   ```bash
   docker run -it gsr-virtual-test /bin/bash
   ```
3. Add health checks to Dockerfile:
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
     CMD python -c "import tests.integration.virtual_environment" || exit 1
   ```

## 📊 Performance Issues

### Slow Test Execution

**Problem**: Tests take much longer than expected
```
# Tests that should take 1 minute take 10+ minutes
```

**Solution**:
1. Profile test execution:
   ```bash
   python -m cProfile -o profile.out test_runner.py
   python -c "import pstats; pstats.Stats('profile.out').sort_stats('cumulative').print_stats(20)"
   ```
2. Optimise configuration:
   ```python
   config = VirtualTestConfig(
       gsr_sampling_rate_hz=32,  # Reduce sampling rate
       response_delay_ms=10,  # Reduce delays
       heartbeat_interval_seconds=5.0,  # Increase interval
   )
   ```
3. Use smaller data sets:
   ```python
   # Generate smaller batches
   gsr_samples = generator.generate_gsr_batch(10)  # Instead of 1000
   ```

### High CPU Usage

**Problem**: Tests consume excessive CPU resources
```
# CPU usage stays at 100% for extended periods
```

**Solution**:
1. Add delays in busy loops:
   ```python
   while condition:
       await asyncio.sleep(0.01)  # Add small delay
       # ... loop body
   ```
2. Limit concurrent operations:
   ```python
   semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent devices
   ```
3. Use lower sample rates during testing

## 🔍 Data Generation Issues

### Inconsistent Synthetic Data

**Problem**: Generated data doesn't match expected patterns
```
AssertionError: GSR values outside expected range
```

**Solution**:
1. Use fixed random seeds:
   ```python
   generator = SyntheticDataGenerator(seed=42)
   ```
2. Validate data generation:
   ```python
   gsr_samples = generator.generate_gsr_batch(100)
   assert all(0.1 <= sample <= 5.0 for sample in gsr_samples)
   ```
3. Check generator configuration:
   ```python
   generator.stress_event_probability = 0.1  # Reasonable value
   generator.noise_amplitude = 0.02  # Not too high
   ```

### File Transfer Simulation Issues

**Problem**: File transfer simulation fails or hangs
```
FileNotFoundError: Simulated file not found
TimeoutError: File transfer timed out
```

**Solution**:
1. Disable file transfers for debugging:
   ```python
   config = VirtualTestConfig(
       simulate_file_transfers=False,
   )
   ```
2. Check output directory permissions:
   ```bash
   ls -la test_results/
   chmod 755 test_results/
   ```
3. Implement proper cleanup:
   ```python
   async def cleanup_files():
       for file_path in generated_files:
           try:
               os.remove(file_path)
           except OSError:
               pass
   ```

## 🚀 CI/CD Issues

### GitHub Actions Failures

**Problem**: Tests pass locally but fail in CI
```
Error: Process completed with exit code 1
```

**Solution**:
1. Check CI environment differences:
   ```yaml
   - name: Debug environment
     run: |
       python --version
       pip list
       df -h
       free -h
   ```
2. Use headless configuration:
   ```python
   config = VirtualTestConfig(
       ci_mode=True,
       headless=True,
       save_detailed_logs=False,
   )
   ```
3. Add retry logic for flaky tests:
   ```python
   @pytest.mark.flaky(reruns=3, reruns_delay=2)
   async def test_flaky_network_operation():
       pass
   ```

### Resource Limits in CI

**Problem**: CI environment runs out of resources
```
ERROR: Operation timed out
Error: The operation was cancelled
```

**Solution**:
1. Reduce test scope for CI:
   ```python
   if os.environ.get('CI'):
       config = VirtualTestConfig(
           device_count=2,  # Reduce from 5
           test_duration_minutes=0.5,  # Shorter tests
       )
   ```
2. Use matrix testing for parallel execution:
   ```yaml
   strategy:
     matrix:
       device_count: [1, 2, 3]
       scenario: [quick, ci]
   ```

## 🛠️ Development Environment Issues

### VS Code Integration

**Problem**: VS Code doesn't recognize virtual environment or shows import errors

**Solution**:
1. Set Python interpreter:
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Choose `.venv/bin/python` (Linux/macOS) or `.venv\Scripts\python.exe` (Windows)
2. Update workspace settings:
   ```json
   {
     "python.defaultInterpreterPath": "./.venv/bin/python",
     "python.testing.pytestEnabled": true
   }
   ```
3. Reload VS Code window: Ctrl+Shift+P → "Developer: Reload Window"

### Cross-Platform Compatibility

**macOS Specific Issues**:
```bash
# Install OpenCV dependencies
brew install opencv

# If permission issues with setup script
chmod +x setup_dev_environment.sh

# Use Python 3 explicitly
python3 -m venv .venv
source .venv/bin/activate
```

**Windows Specific Issues**:
```cmd
# Use Windows-compatible paths in VS Code settings
{
  "python.defaultInterpreterPath": "./.venv/Scripts/python.exe"
}

# Install dependencies with Windows-compatible OpenCV
pip install opencv-python-headless

# Run setup with PowerShell
powershell -ExecutionPolicy Bypass -File setup_dev_environment.ps1

# Alternative: Use WSL2 for Linux-like environment
wsl --install
```

**Windows PowerShell Setup Script**:
Create `setup_dev_environment.ps1` for Windows users:
```powershell
# Check if Python is available
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.10 or higher."
    exit 1
}

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install pytest pytest-asyncio pytest-cov psutil numpy opencv-python-headless
pip install matplotlib pillow

Write-Host "✓ Windows setup complete. Use '.venv\Scripts\Activate.ps1' to activate."
```

### Debugging Virtual Devices

**Problem**: Difficult to debug virtual device behaviour

**Solution**:
1. Enable detailed logging:
   ```python
   logger = logging.getLogger("VirtualDevice")
   logger.setLevel(logging.DEBUG)
   ```
2. Add breakpoints in device lifecycle:
   ```python
   async def connect(self):
       breakpoint()  # Debug connection process
       # ... connection code
   ```
3. Use VS Code debugger configuration:
   ```json
   {
     "name": "Debug Virtual Device",
     "type": "python",
     "request": "launch",
     "program": "test_runner.py",
     "args": ["--scenario", "quick", "--verbose"],
     "console": "integratedTerminal",
     "stopOnEntry": false
   }
   ```

## 📚 Getting Help

### Log Analysis

1. Enable verbose logging:
   ```bash
   python test_runner.py --scenario quick --verbose --log-level DEBUG
   ```

2. Check test results directory:
   ```bash
   ls -la test_results/
   cat test_results/*_report.json
   cat test_results/*.log
   ```

### Performance Profiling

1. Run performance tests:
   ```bash
   pytest test_performance_benchmarks.py -v -m performance
   ```

2. Generate performance report:
   ```bash
   python -c "
   from tests.integration.virtual_environment import VirtualTestConfig
   config = VirtualTestConfig(device_count=3, test_duration_minutes=1.0)
   print(f'Memory estimate: {config.estimate_memory_usage()}MB')
   print(f'Data estimate: {config.estimate_data_volume()}')
   "
   ```

### Community Resources

- Check GitHub Issues: [Issues](https://github.com/buccancs/bucika_gsr/issues)
- Review Documentation: `tests/integration/virtual_environment/README.md`
- Implementation Details: `tests/integration/virtual_environment/IMPLEMENTATION_SUMMARY.md`

### Creating Issue Reports

When reporting issues, include:

1. Environment information:
   ```bash
   python --version
   pip list | grep -E "(pytest|numpy|opencv)"
   uname -a
   ```

2. Minimal reproduction case:
   ```python
   # Minimal code that reproduces the issue
   from tests.integration.virtual_environment import VirtualTestConfig
   config = VirtualTestConfig(test_name="reproduction_case", device_count=1)
   ```

3. Complete error message and stack trace
4. Configuration used
5. Expected vs actual behaviour