"""
Hardware Testing Guide and Configuration
========================================

This document provides comprehensive guidance on running the hardware-in-the-loop
testing framework with both real devices and mock infrastructure.

## Overview

The hardware testing framework supports two modes:

1. **Mock Mode (Default)**: Uses simulated devices for CI/CD and development
2. **Real Hardware Mode**: Uses actual Shimmer sensors and thermal cameras

## Environment Variables

Configure the testing environment using these variables:

```bash
# Enable real hardware (default: false)
export USE_REAL_HARDWARE=true

# Android device testing
export USE_REAL_ANDROID_DEVICE=true
export ANDROID_DEVICE_NAME="Samsung Galaxy S10"
export APPIUM_SERVER_URL="http://localhost:4723"

# Hardware timeouts (seconds)
export SHIMMER_TIMEOUT=10.0
export THERMAL_TIMEOUT=10.0

# Mock configuration
export MOCK_DATA_QUALITY=good  # good, fair, poor
export ENABLE_STRESS_TESTING=true
export MAX_CONNECTION_RETRIES=3
```

## Mock Infrastructure Features

### Shimmer GSR Sensor Mock
- Realistic GSR data generation with breathing patterns
- Configurable sample rates (default: 128 Hz)
- Simulated stress response events
- Battery level simulation
- Connection stability testing

### Thermal Camera Mock
- Thermal frame generation with temperature gradients
- False color visualization
- Configurable resolution (default: 160x120)
- Hot spot simulation
- USB device enumeration

### Android Device Mock
- Complete Appium WebDriver simulation
- UI element interaction testing
- Screenshot capture
- Gesture simulation (swipe, tap, long press)
- App lifecycle testing
- Network connectivity simulation

## Running Tests

### Basic Hardware Tests

```bash
# Run all hardware tests (uses mocks by default)
pytest tests/hardware/ -v

# Run specific device tests
pytest tests/hardware/test_shimmer_integration.py -v
pytest tests/hardware/test_thermal_camera.py -v

# Run with real hardware
USE_REAL_HARDWARE=true pytest tests/hardware/ -v
```

### Android E2E Tests

```bash
# Run Android tests (uses mock by default)
pytest tests/e2e/test_android_comprehensive.py -v

# Run with real Android device (requires Appium server)
USE_REAL_ANDROID_DEVICE=true pytest tests/e2e/test_android_comprehensive.py -v

# Run specific Android test categories
pytest tests/e2e/ -m "android and hardware" -v
pytest tests/e2e/ -m "android and accessibility" -v
```

### Test Categories by Markers

```bash
# Hardware integration tests
pytest -m hardware -v

# Stress and performance tests
pytest -m stress -v

# Android-specific tests
pytest -m android -v

# Accessibility compliance tests
pytest -m accessibility -v

# End-to-end workflow tests
pytest -m e2e -v
```

## Real Hardware Setup

### Shimmer GSR Sensor Setup

1. **Hardware Requirements**:
   - Shimmer3 GSR+ device
   - Bluetooth-enabled computer
   - GSR electrodes

2. **Software Dependencies**:
   ```bash
   pip install pyshimmer
   pip install pybluez  # Linux/macOS
   pip install bleak    # Cross-platform alternative
   ```

3. **Device Preparation**:
   - Charge Shimmer device
   - Pair with computer via Bluetooth
   - Note the Bluetooth MAC address

4. **Configuration**:
   ```bash
   export USE_REAL_HARDWARE=true
   export SHIMMER_DEVICE_ADDRESS="00:06:66:66:66:66"
   ```

### Thermal Camera Setup

1. **Hardware Requirements**:
   - USB thermal camera (Topdon, FLIR, etc.)
   - USB cable

2. **Software Dependencies**:
   ```bash
   pip install opencv-python
   pip install pyusb
   ```

3. **Device Preparation**:
   - Connect camera via USB
   - Install any required drivers
   - Verify camera appears in device manager

4. **Linux Permissions**:
   ```bash
   # Add udev rule for thermal camera access
   sudo tee /etc/udev/rules.d/99-thermal-camera.rules << EOF
   SUBSYSTEM=="usb", ATTR{idVendor}=="1e4e", MODE="0666"
   EOF
   sudo udevadm control --reload-rules
   ```

### Android Device Setup

1. **Hardware Requirements**:
   - Android device or emulator
   - USB cable (for real device)
   - Computer with ADB installed

2. **Software Dependencies**:
   ```bash
   pip install appium-python-client
   npm install -g appium
   npm install -g appium-doctor
   ```

3. **Device Preparation**:
   - Enable Developer Options on Android device
   - Enable USB Debugging
   - Install GSR app on device
   - Start Appium server: `appium`

4. **Configuration**:
   ```bash
   export USE_REAL_ANDROID_DEVICE=true
   export ANDROID_DEVICE_NAME="Your Device Name"
   export APPIUM_SERVER_URL="http://localhost:4723"
   ```

## CI/CD Integration

### GitHub Actions Configuration

```yaml
name: Hardware Tests

on: [push, pull_request]

jobs:
  mock-hardware-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r test-requirements.txt
      
      - name: Run hardware tests (mock mode)
        run: |
          pytest tests/hardware/ -v --tb=short
      
      - name: Run Android tests (mock mode)
        run: |
          pytest tests/e2e/test_android_comprehensive.py -v --tb=short

  real-hardware-tests:
    runs-on: self-hosted  # Requires runner with hardware
    if: github.event_name == 'schedule'  # Only on nightly runs
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r test-requirements.txt
      
      - name: Run hardware tests (real hardware)
        env:
          USE_REAL_HARDWARE: true
        run: |
          pytest tests/hardware/ -v --tb=short
```

### Docker Support

```dockerfile
# Dockerfile for hardware testing environment
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libusb-1.0-0-dev \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY test-requirements.txt .
RUN pip install -r test-requirements.txt

# Copy test files
COPY tests/ /app/tests/
WORKDIR /app

# Run tests in mock mode by default
CMD ["pytest", "tests/hardware/", "-v"]
```

## Troubleshooting

### Common Issues

1. **Bluetooth Permission Denied**:
   ```bash
   # Add user to bluetooth group (Linux)
   sudo usermod -a -G bluetooth $USER
   # Logout and login again
   ```

2. **USB Device Not Found**:
   ```bash
   # Check device visibility
   lsusb
   # Check permissions
   ls -la /dev/bus/usb/
   ```

3. **Appium Connection Failed**:
   ```bash
   # Check Appium server status
   appium-doctor
   # Verify device connection
   adb devices
   ```

4. **Mock Tests Failing**:
   - Check pytest markers are registered in pytest.ini
   - Verify test dependencies are installed
   - Check log output for specific error details

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
pytest tests/hardware/ -v -s --tb=long

# Save logs to file
pytest tests/hardware/ -v --tb=short > test_output.log 2>&1
```

### Performance Optimization

For faster test execution:

```bash
# Run tests in parallel
pytest tests/hardware/ -n auto

# Skip slow tests
pytest tests/hardware/ -m "not stress"

# Run only essential tests
pytest tests/hardware/ -k "test_connection"
```

## Test Coverage Reports

Generate coverage reports for hardware tests:

```bash
# Run with coverage
pytest tests/hardware/ --cov=tests.hardware --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Contributing

When adding new hardware tests:

1. Follow the existing mock/real device pattern
2. Add appropriate pytest markers
3. Include comprehensive error handling
4. Test both success and failure scenarios
5. Document any new environment variables
6. Update this guide with new setup instructions

## Support

For issues with the hardware testing framework:

1. Check this documentation
2. Review existing GitHub issues
3. Check the troubleshooting section
4. Create a detailed issue report with:
   - Hardware configuration
   - Environment variables
   - Complete error logs
   - Steps to reproduce
"""