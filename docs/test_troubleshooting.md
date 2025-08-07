# Test Troubleshooting Guide

## Overview

This guide provides solutions for common issues encountered when running the Multi-Sensor Recording System's test suite.

## Common Issues and Solutions

### Build and Compilation Issues

#### Missing Dependencies
**Problem**: Import errors when running tests
```
ImportError: No module named 'PyQt5'
```

**Solution**:
```bash
# Install required dependencies
pip install -e ".[dev]"

# For thorough testing
pip install -e ".[dev,shimmer,calibration,android]"
```

#### Undefined Names/Types
**Problem**: Syntax errors with undefined types
```
F821 undefined name 'Tuple'
```

**Solution**: Import missing types in module headers:
```python
from typing import Any, Dict, List, Optional, Tuple
```

### Network and Connectivity Issues

#### Device Discovery Failures
**Problem**: Android devices not detected
**Solution**:
1. Ensure all devices on same WiFi network
2. Check firewall settings allow local network communication
3. Verify Android app has network permissions

#### WebSocket Connection Timeouts
**Problem**: Connection timeouts during testing
**Solution**:
1. Increase timeout values in test configuration
2. Check network stability and bandwidth
3. Reduce concurrent device connections for testing

### Android-Specific Issues

#### Permission Denied Errors
**Problem**: Android tests fail with permission errors
**Solution**:
1. Grant all requested permissions in Android app
2. Enable developer options on Android devices
3. Check USB debugging is enabled

#### Bluetooth Connection Issues
**Problem**: Shimmer sensor connection failures
**Solution**:
1. Verify Bluetooth is enabled on Android devices
2. Pair Shimmer devices before testing
3. Check device compatibility with Shimmer sensors

### Performance Issues

#### Slow Test Execution
**Problem**: Tests taking too long to complete
**Solution**:
```bash
# Use quick mode for development
python run_evaluation_suite.py --quick

# Use parallel execution
python run_evaluation_suite.py --parallel

# Test specific categories only
python run_evaluation_suite.py --category android_foundation
```

#### Memory Issues
**Problem**: Out of memory errors during testing
**Solution**:
1. Reduce concurrent device connections
2. Increase system memory allocation
3. Use quick test mode to reduce resource usage

### Data and Synchronization Issues

#### Timestamp Synchronization Failures
**Problem**: Timing precision below requirements
**Solution**:
1. Ensure NTP synchronization is working
2. Check system clock accuracy
3. Reduce network latency between devices

#### Data Quality Issues
**Problem**: Invalid or corrupted test data
**Solution**:
1. Verify device calibration
2. Check sensor connection quality
3. Validate data format compliance

## Debug Mode and Logging

### Enable Debug Logging
```bash
# Run with verbose output
python run_evaluation_suite.py --verbose --debug

# Generate detailed logs
python run_evaluation_suite.py --log-level DEBUG
```

### Log Analysis
Common log patterns to look for:
- Connection establishment messages
- Error patterns and stack traces
- Performance timing information
- Data validation results

## Advanced Troubleshooting

### Component Isolation Testing
```bash
# Test individual components
python run_evaluation_suite.py --test calibration_manager_test
python run_evaluation_suite.py --test network_communication_test
python run_evaluation_suite.py --test shimmer_integration_test
```

### Environment Validation
```bash
# Check system requirements
python -c "import PyQt5, cv2, numpy; print('Core dependencies OK')"

# Verify network configuration
python -c "import socket; print(f'Local IP: {socket.gethostbyname(socket.gethostname())}')"

# Check available devices
python run_evaluation_suite.py --list-devices
```

## Getting Help

### Documentation Resources
- **[Unified Test Documentation](../UNIFIED_TEST_DOCUMENTATION.md)**: Complete test framework overview
- **[Test Execution Guide](./test_execution_guide.md)**: Step-by-step execution instructions
- **[Architecture Documentation](./architecture.md)**: System design and components

### Support Channels
1. Check existing issues in project repository
2. Review test execution logs for specific error patterns
3. Consult community documentation and forums
4. Contact development team with detailed error information

### Reporting Issues
When reporting test issues, include:
- Complete error message and stack trace
- System configuration (OS, Python version, dependencies)
- Test command used
- Network configuration details
- Device specifications and configurations

## Best Practices

### Development Testing
- Run quick tests frequently during development
- Use category-specific tests for focused debugging
- Maintain clean test environment with proper dependencies

### Production Validation
- Run complete test suite before releases
- Validate performance under expected load conditions
- Test with representative device configurations

### Continuous Integration
- Automate test execution in CI/CD pipeline
- Set appropriate timeout values for automated testing
- Monitor test performance trends over time