# Test Failure Troubleshooting Guide

This guide provides comprehensive troubleshooting information for the Multi-Sensor Recording System evaluation suite test failures.

## General Troubleshooting Approach

### 1. Initial Diagnosis

When tests fail, follow this systematic approach:

1. **Check Test Logs**: Review detailed execution logs for error messages
2. **Verify Environment**: Ensure all prerequisites are met
3. **Isolate Issue**: Run specific test categories to narrow down problems
4. **Check Resources**: Monitor system resources during test execution
5. **Review Configuration**: Verify test configuration matches system capabilities

### 2. Log Analysis

#### Understanding Log Levels
- **ERROR**: Critical failures requiring immediate attention
- **WARNING**: Issues that may affect test results but don't cause failures
- **INFO**: General execution information and progress updates
- **DEBUG**: Detailed execution traces for troubleshooting

#### Key Log Patterns
```
ERROR: CalibrationManager file not found
WARNING: Performance degraded at 12 devices  
INFO: Testing device discovery workflow...
DEBUG: Discovered device: android_01
```

## Foundation Test Failures

### Android Component Test Failures

#### CameraRecordingTest Failures

**Common Issues:**

1. **Android Source Not Available**
   ```
   ERROR: Android source code not available for testing
   ```
   
   **Diagnosis:**
   - Check if `AndroidApp/src/main/java/com/multisensor/recording/MainActivity.kt` exists
   - Verify proper Android project structure
   
   **Solution:**
   ```bash
   # Verify Android project structure
   ls -la AndroidApp/src/main/java/com/multisensor/recording/
   
   # Should contain MainActivity.kt and other source files
   find AndroidApp -name "*.kt" | head -5
   ```

2. **Missing Required Patterns**
   ```
   ERROR: Camera implementation test failed: Required patterns not found
   ```
   
   **Diagnosis:**
   - Source files exist but don't contain expected implementation patterns
   - Files may be empty or incomplete
   
   **Solution:**
   - Review MainActivity.kt for camera-related imports and functionality
   - Ensure Camera2 API integration is present
   - Check for required permissions in AndroidManifest.xml

#### ShimmerGSRTest Failures

**Common Issues:**

1. **ShimmerRecorder.kt Not Found**
   ```
   ERROR: ShimmerRecorder.kt not found
   ```
   
   **Solution:**
   ```bash
   # Verify ShimmerRecorder exists
   find AndroidApp -name "ShimmerRecorder.kt"
   
   # Check if it's in the expected location
   ls -la AndroidApp/src/main/java/com/multisensor/recording/recording/
   ```

2. **Missing Shimmer Library Integration**
   ```
   WARNING: Shimmer implementation patterns not found
   ```
   
   **Diagnosis:**
   - ShimmerRecorder.kt exists but lacks Shimmer library integration
   - Missing required imports or implementation patterns
   
   **Solution:**
   - Review ShimmerRecorder.kt for Shimmer-specific imports:
     - `ShimmerBluetoothManagerAndroid`
     - `ObjectCluster`
     - `ShimmerBluetooth`
   - Check build.gradle.kts for Shimmer dependencies

3. **Bluetooth Permissions Missing**
   ```
   ERROR: Bluetooth permissions test failed
   ```
   
   **Solution:**
   - Check AndroidManifest.xml for required permissions:
     ```xml
     <uses-permission android:name="android.permission.BLUETOOTH" />
     <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
     <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
     ```

#### NetworkCommunicationTest Failures

**Common Issues:**

1. **ConnectionManager Not Found**
   ```
   ERROR: ConnectionManager implementation test failed
   ```
   
   **Solution:**
   ```bash
   # Verify ConnectionManager exists
   find AndroidApp -name "ConnectionManager.kt"
   ```

2. **WebSocket Implementation Missing**
   ```
   WARNING: WebSocket implementation not detected
   ```
   
   **Diagnosis:**
   - Missing WebSocket dependencies in build.gradle.kts
   - No WebSocket-related code in source files
   
   **Solution:**
   - Check build.gradle.kts for WebSocket libraries (OkHttp, etc.)
   - Review network-related source files for WebSocket usage

#### ThermalCameraTest Failures

**Common Issues:**

1. **ThermalRecorder Missing**
   ```
   ERROR: ThermalRecorder.kt not found
   ```
   
   **Solution:**
   ```bash
   # Check for thermal recorder implementation
   find AndroidApp -name "*Thermal*.kt"
   find AndroidApp -name "*thermal*" -type f
   ```

2. **Thermal Dependencies Missing**
   ```
   WARNING: Thermal camera dependencies not found
   ```
   
   **Solution:**
   - Check build.gradle.kts for thermal camera libraries
   - Look for FLIR SDK or other thermal camera dependencies

#### SessionManagementTest Failures

**Common Issues:**

1. **SessionManager Not Found**
   ```
   ERROR: Session manager test failed
   ```
   
   **Solution:**
   ```bash
   # Look for session management files
   find AndroidApp -name "*Session*.kt"
   find AndroidApp -path "*/service/*" -name "*.kt"
   ```

### PC Component Test Failures

#### CalibrationSystemTest Failures

**Common Issues:**

1. **CalibrationManager Missing**
   ```
   ERROR: CalibrationManager file not found
   ```
   
   **Solution:**
   ```bash
   # Verify PC component structure
   ls -la PythonApp/calibration/
   ls -la PythonApp/calibration/calibration_manager.py
   ```

2. **OpenCV Dependencies Missing**
   ```
   ERROR: CalibrationProcessor file not found
   ```
   
   **Solution:**
   ```bash
   # Install OpenCV dependencies
   pip install opencv-python opencv-contrib-python
   
   # Verify calibration processor exists
   ls -la PythonApp/calibration/calibration_processor.py
   ```

#### NetworkServerTest Failures

**Common Issues:**

1. **PCServer Implementation Missing**
   ```
   ERROR: PC server implementation test failed
   ```
   
   **Solution:**
   ```bash
   # Check PC server files
   ls -la PythonApp/network/
   find PythonApp -name "*server*.py"
   ```

2. **Network Dependencies Missing**
   ```
   ERROR: Device manager test failed
   ```
   
   **Solution:**
   ```bash
   # Install network dependencies
   pip install websockets asyncio
   
   # Verify network components
   ls -la PythonApp/network/android_device_manager.py
   ```

#### SynchronizationEngineTest Failures

**Common Issues:**

1. **Clock Synchronization Missing**
   ```
   ERROR: Clock synchronization test failed
   ```
   
   **Solution:**
   ```bash
   # Check synchronization components
   ls -la PythonApp/master_clock_synchronizer.py
   ls -la PythonApp/ntp_time_server.py
   ```

## Integration Test Failures

### MultiDeviceCoordinationTest Failures

**Common Issues:**

1. **Device Discovery Failures**
   ```
   WARNING: Discovery rate below threshold: 75%
   ```
   
   **Diagnosis:**
   - Simulated device discovery failing due to timeout or resource issues
   - Network connectivity problems
   
   **Solution:**
   - Increase device discovery timeout in test configuration
   - Check system network configuration
   - Reduce number of simulated devices

2. **Session Management Failures**
   ```
   ERROR: Session management test failed
   ```
   
   **Solution:**
   - Check available system memory
   - Reduce session complexity in test configuration
   - Verify session management code exists in PC components

### NetworkPerformanceTest Failures

**Common Issues:**

1. **WebSocket Connection Failures**
   ```
   ERROR: Communication protocols test failed
   ```
   
   **Diagnosis:**
   - Network connectivity issues
   - Firewall blocking connections
   - Port conflicts
   
   **Solution:**
   ```bash
   # Check network connectivity
   ping google.com
   
   # Check port availability
   netstat -tuln | grep :8080
   
   # Test with relaxed thresholds
   python run_evaluation_suite.py --quick --category integration
   ```

2. **Bandwidth Utilization Issues**
   ```
   WARNING: Bandwidth utilization above threshold: 95%
   ```
   
   **Solution:**
   - Reduce simulated data rates in test configuration
   - Check for background network traffic
   - Adjust bandwidth limits in test configuration

### SynchronizationPrecisionTest Failures

**Common Issues:**

1. **Temporal Accuracy Issues**
   ```
   ERROR: Max sync difference: 2.5ms (threshold: 1.0ms)
   ```
   
   **Diagnosis:**
   - System clock resolution insufficient
   - High system load affecting timing
   - Test running on virtual machine with timing issues
   
   **Solution:**
   - Run tests on physical hardware
   - Reduce system load during testing
   - Adjust precision thresholds for test environment:
     ```json
     {
       "quality_thresholds": {
         "sync_precision_ms": 5.0
       }
     }
     ```

### EndToEndRecordingTest Failures

**Common Issues:**

1. **Device Setup Workflow Failures**
   ```
   ERROR: Device setup workflow test failed
   ```
   
   **Solution:**
   - Increase timeout for device setup operations
   - Reduce number of simulated devices
   - Check system resources during test execution

2. **Recording Workflow Failures**
   ```
   ERROR: Recording workflow test failed
   ```
   
   **Solution:**
   - Monitor system resources (CPU, memory) during test
   - Adjust workflow timing parameters
   - Check for resource conflicts with other processes

### ErrorHandlingRecoveryTest Failures

**Common Issues:**

1. **Recovery Rate Below Threshold**
   ```
   WARNING: Recovery rate: 75% (threshold: 80%)
   ```
   
   **Solution:**
   - This may indicate actual issues with error handling implementation
   - Review error recovery logic in PC and Android components
   - Adjust recovery rate thresholds if appropriate for test environment

### PerformanceStressTest Failures

**Common Issues:**

1. **High Device Count Performance Issues**
   ```
   WARNING: Performance degraded at 8 devices
   ```
   
   **Diagnosis:**
   - Expected behavior under stress conditions
   - System reaching resource limits
   
   **Solution:**
   - Document performance limits for system specification
   - Adjust device count limits based on target hardware
   - Configure graceful degradation thresholds

2. **Resource Exhaustion**
   ```
   ERROR: Resource limitations test failed
   ```
   
   **Solution:**
   - Monitor system resources during test execution
   - Ensure adequate system memory and CPU for stress testing
   - Adjust stress test parameters for available resources

## System-Level Issues

### Memory Issues

**Symptoms:**
- Tests fail with out-of-memory errors
- System becomes unresponsive during test execution
- Gradual performance degradation

**Solutions:**

1. **Increase Available Memory**
   ```bash
   # Check current memory usage
   free -h
   
   # Monitor memory during test execution
   watch -n 1 'free -h && ps aux | grep python | head -5'
   ```

2. **Optimize Test Execution**
   ```bash
   # Run tests in categories to reduce memory pressure
   python run_evaluation_suite.py --category foundation
   python run_evaluation_suite.py --category integration
   
   # Use quick mode to reduce test complexity
   python run_evaluation_suite.py --quick
   ```

3. **Adjust Test Configuration**
   ```json
   {
     "test_configuration": {
       "stress_test_devices": 4,
       "parallel_execution": false,
       "extended_session_hours": 1
     }
   }
   ```

### CPU Performance Issues

**Symptoms:**
- Tests timeout frequently
- System becomes sluggish during test execution
- CPU usage consistently above 90%

**Solutions:**

1. **Monitor CPU Usage**
   ```bash
   # Check CPU usage during tests
   top -p $(pgrep -f run_evaluation_suite.py)
   
   # Monitor system load
   uptime
   ```

2. **Reduce Test Load**
   ```bash
   # Disable parallel execution
   python run_evaluation_suite.py --parallel false
   
   # Run specific test categories
   python run_evaluation_suite.py --category foundation --quick
   ```

### Network Connectivity Issues

**Symptoms:**
- Network tests consistently fail
- Connection timeouts
- Variable test results

**Solutions:**

1. **Check Network Stability**
   ```bash
   # Test network connectivity
   ping -c 10 google.com
   
   # Check for packet loss
   mtr google.com
   ```

2. **Adjust Network Timeouts**
   ```json
   {
     "test_configuration": {
       "network_timeout_seconds": 30,
       "connection_retry_attempts": 5
     }
   }
   ```

## Configuration-Related Issues

### Invalid Configuration Files

**Error:** `Failed to load config file: Invalid JSON`

**Solution:**
```bash
# Validate JSON syntax
python -m json.tool config/custom_thresholds.json

# Use default configuration
python run_evaluation_suite.py  # without --config-file
```

### Threshold Configuration Issues

**Error:** Tests fail due to overly strict thresholds

**Solution:**
1. **Review Default Thresholds**
   ```json
   {
     "quality_thresholds": {
       "minimum_success_rate": 0.80,
       "sync_precision_ms": 2.0,
       "measurement_accuracy": 0.85
     }
   }
   ```

2. **Use Quick Mode for Development**
   ```bash
   python run_evaluation_suite.py --quick
   ```

## Environment-Specific Issues

### Virtual Machine Issues

**Common Problems:**
- Timing precision issues due to virtualization
- Resource contention with host system
- Network configuration complications

**Solutions:**
1. **Adjust Timing Thresholds**
   ```json
   {
     "quality_thresholds": {
       "sync_precision_ms": 10.0,
       "max_network_latency_ms": 500.0
     }
   }
   ```

2. **Allocate Adequate Resources**
   - Minimum 4GB RAM for VM
   - At least 2 CPU cores
   - Stable network bridge configuration

### Docker/Container Issues

**Common Problems:**
- Limited resource access
- Network isolation
- File system permission issues

**Solutions:**
1. **Resource Allocation**
   ```bash
   # Run with adequate resources
   docker run --memory=4g --cpus=2 <image>
   ```

2. **Network Configuration**
   ```bash
   # Use host networking for network tests
   docker run --network=host <image>
   ```

## Advanced Troubleshooting

### Debug Mode Execution

Enable maximum debugging information:

```bash
# Maximum verbosity and debug output
python -u run_evaluation_suite.py --verbose --output-dir debug_logs 2>&1 | tee execution.log
```

### Selective Test Execution

Run individual tests for targeted debugging:

```python
# Create custom test runner for specific test
import asyncio
from evaluation_suite.foundation.android_tests import ShimmerGSRTest

async def debug_single_test():
    test = ShimmerGSRTest("debug_shimmer_test")
    test_env = {}
    await test.setup(test_env)
    result = await test.execute(test_env)
    print(f"Result: {result.success}")
    print(f"Error: {result.error_message}")

asyncio.run(debug_single_test())
```

### Performance Profiling

Profile test execution to identify bottlenecks:

```bash
# Profile test execution
python -m cProfile -o test_profile.prof run_evaluation_suite.py --quick

# Analyze profile results
python -m pstats test_profile.prof
```

### Log Analysis Tools

Use advanced log analysis for pattern detection:

```bash
# Search for specific error patterns
grep -r "ERROR" evaluation_results/

# Count error types
grep "ERROR" evaluation_results/*.log | cut -d: -f3 | sort | uniq -c

# Monitor real-time logs
tail -f evaluation_results/evaluation_suite_*.log | grep -E "(ERROR|WARNING)"
```

## Getting Additional Help

### Collecting Diagnostic Information

When reporting issues, include:

1. **System Information**
   ```bash
   # System details
   uname -a
   python --version
   pip list | grep -E "(opencv|psutil|numpy)"
   ```

2. **Test Execution Logs**
   ```bash
   # Complete log with maximum verbosity
   python run_evaluation_suite.py --verbose --output-dir diagnostic_logs
   ```

3. **Configuration Details**
   ```bash
   # Current configuration
   cat config/custom_thresholds.json  # if using custom config
   ```

4. **Resource Utilization**
   ```bash
   # System resources during test execution
   free -h && df -h && uptime
   ```

### Issue Reporting Template

When reporting test failures, provide:

```
**Test Failure Report**

Environment:
- OS: [Linux/Windows/macOS version]
- Python: [version]
- Memory: [available RAM]
- Test Category: [foundation/integration/system/performance]

Error:
- Test Name: [specific test that failed]
- Error Message: [exact error message]
- Success Rate: [percentage if available]

Logs:
[Include relevant log excerpts]

Configuration:
[Include any custom configuration used]

Steps to Reproduce:
1. [Command executed]
2. [Any specific conditions]

Expected vs Actual:
- Expected: [what should happen]
- Actual: [what actually happened]
```

### Community Resources

- **Documentation**: Refer to additional documentation in `docs/` directory
- **Source Code**: Review test implementations for understanding expected behavior
- **Configuration Examples**: Check `config/` directory for example configurations

This comprehensive troubleshooting guide should help resolve most test execution issues. For persistent problems, systematic log analysis and environmental verification typically reveal the root cause.