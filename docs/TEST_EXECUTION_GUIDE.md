# Comprehensive Test Execution Guide

This guide provides detailed instructions for executing the comprehensive evaluation suite for the Multi-Sensor Recording System.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, Windows, or macOS
- **Memory**: Minimum 4GB RAM, recommended 8GB+ for stress testing
- **Storage**: 2GB free space for test artifacts and logs
- **Network**: Stable internet connection for network performance tests

### Required Dependencies
Install the required Python packages:

```bash
# Install core dependencies
pip install -r requirements.txt

# Additional dependencies for comprehensive testing
pip install psutil opencv-python numpy pytest asyncio
```

### Project Structure Verification
Ensure the following directories and files exist:
- `AndroidApp/src/main/java/com/multisensor/recording/`
- `PythonApp/calibration/calibration_manager.py`
- `PythonApp/network/pc_server.py` 
- `PythonApp/shimmer_manager.py`
- `evaluation_suite/`

## Quick Start Guide

### 1. Basic Test Execution

Run the complete evaluation suite with default settings:

```bash
python run_evaluation_suite.py
```

This executes all test categories and generates comprehensive reports.

### 2. Quick Validation

For rapid feedback during development:

```bash
python run_evaluation_suite.py --quick --verbose
```

Uses relaxed quality thresholds and provides detailed console output.

### 3. Parallel Execution

For faster execution on multi-core systems:

```bash
python run_evaluation_suite.py --parallel
```

Enables parallel execution where tests are independent.

## Test Categories

### Foundation Tests

Test individual Android and PC components:

```bash
# Run only foundation layer tests
python run_evaluation_suite.py --category foundation

# Run with verbose output to see detailed component validation
python run_evaluation_suite.py --category foundation --verbose
```

**Foundation tests validate:**
- Android component source code structure
- PC component implementation patterns
- Required dependencies and libraries
- Core functionality patterns

### Integration Tests

Test cross-component interactions and workflows:

```bash
# Run only integration layer tests
python run_evaluation_suite.py --category integration

# Run with extended timeout for stress tests
python run_evaluation_suite.py --category integration --config-file config/extended_timeouts.json
```

**Integration tests validate:**
- Multi-device coordination workflows
- Network communication protocols
- Synchronization precision and stability
- End-to-end recording workflows
- Error handling and recovery
- Performance under stress conditions

### System Tests

Test complete end-to-end functionality:

```bash
# Run only system layer tests (when implemented)
python run_evaluation_suite.py --category system
```

### Performance Tests

Test non-functional requirements:

```bash
# Run only performance layer tests (when implemented)
python run_evaluation_suite.py --category performance
```

## Advanced Configuration

### Custom Quality Thresholds

Create a configuration file to customize acceptance criteria:

```json
{
  "quality_thresholds": {
    "minimum_success_rate": 0.90,
    "maximum_execution_time": 3600.0,
    "minimum_coverage": 0.75,
    "sync_precision_ms": 2.0,
    "data_quality_score": 0.75,
    "measurement_accuracy": 0.90,
    "max_memory_usage_mb": 2048,
    "max_cpu_usage_percent": 80.0,
    "max_network_latency_ms": 200.0
  },
  "test_configuration": {
    "timeout_seconds": 900,
    "parallel_execution": true,
    "collect_metrics": true,
    "generate_reports": true,
    "stress_test_devices": 16,
    "extended_session_hours": 48
  }
}
```

Run with custom configuration:

```bash
python run_evaluation_suite.py --config-file config/custom_thresholds.json
```

### Output Directory Configuration

Specify custom output directory for test results:

```bash
python run_evaluation_suite.py --output-dir /path/to/test/results
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
python run_evaluation_suite.py --verbose --output-dir debug_results
```

## Test Results and Reports

### Generated Files

Each test execution creates:

1. **`comprehensive_evaluation_report.json`**
   - Complete test execution data
   - Performance metrics for each test
   - Quality assessment scores
   - Statistical analysis results

2. **`evaluation_summary.md`**
   - Human-readable summary
   - Quality level assessment
   - Actionable recommendations
   - Pass/fail status for each test category

3. **`evaluation_suite_YYYYMMDD_HHMMSS.log`**
   - Detailed execution logs
   - Debug information and error messages
   - Performance monitoring data
   - Test-by-test execution trace

### Quality Assessment Levels

The evaluation suite provides quality assessment:

- **Excellent** (>95% success, >0.90 quality score): Ready for production research use
- **Good** (>90% success, >0.80 quality score): Suitable for research with minor limitations
- **Acceptable** (>80% success, >0.70 quality score): Requires improvements before research use
- **Needs Improvement** (<80% success, <0.70 quality score): Significant issues requiring attention

### Interpreting Results

#### Success Rates
- **Foundation Tests**: Should achieve >95% success for stable system
- **Integration Tests**: Should achieve >90% success for reliable operation
- **Stress Tests**: Should achieve >85% success under adverse conditions

#### Performance Metrics
- **Synchronization Precision**: <1ms for research-grade timing
- **Memory Usage**: Should scale predictably with device count
- **CPU Usage**: Should remain <60% during normal operation
- **Network Latency**: Should be <100ms in test environment

#### Quality Scores
- **Overall Quality**: Weighted score across all test dimensions
- **Research Readiness**: Boolean assessment for research deployment
- **Specific Recommendations**: Actionable guidance for improvements

## Troubleshooting

### Common Issues

#### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'psutil'`

**Solution**:
```bash
pip install psutil opencv-python numpy
```

#### Android Source Code Not Found

**Error**: Tests report "Android source code not available for testing"

**Solution**:
1. Verify `AndroidApp/src/main/java/com/multisensor/recording/` directory exists
2. Check that Kotlin source files are present
3. Ensure proper project structure

#### PC Components Not Available

**Error**: Tests report "Real PC components not available for testing"

**Solution**:
1. Verify `PythonApp/` directory structure
2. Check that required Python files exist:
   - `calibration/calibration_manager.py`
   - `network/pc_server.py`
   - `shimmer_manager.py`

#### Test Timeouts

**Error**: Tests fail with timeout errors

**Solution**:
1. Increase timeout values in configuration:
   ```json
   {
     "test_configuration": {
       "timeout_seconds": 1800
     }
   }
   ```
2. Use `--quick` flag for faster execution
3. Run specific categories instead of full suite

#### Memory Issues

**Error**: Out of memory during stress tests

**Solution**:
1. Increase system memory allocation
2. Reduce concurrent test execution:
   ```bash
   python run_evaluation_suite.py --category foundation
   ```
3. Adjust stress test parameters in configuration

### Performance Issues

#### Slow Execution

**Symptoms**: Tests take excessive time to complete

**Solutions**:
1. Enable parallel execution: `--parallel`
2. Use quick mode: `--quick`
3. Run specific test categories
4. Check system resource availability

#### Network Connectivity Issues

**Symptoms**: Network tests fail with connection errors

**Solutions**:
1. Verify internet connectivity
2. Check firewall settings
3. Adjust network timeout settings in configuration
4. Run tests on stable network connection

### Test Failures

#### Foundation Test Failures

**Investigate**:
1. Check that source code files exist and contain expected patterns
2. Verify dependencies are properly installed
3. Review detailed logs for specific failure reasons

#### Integration Test Failures

**Investigate**:
1. Check network connectivity and performance
2. Verify system resources (memory, CPU) are adequate
3. Review synchronization timing requirements
4. Check for environmental factors affecting test execution

#### Stress Test Failures

**Expected Behavior**: Some stress test failures under extreme conditions are normal

**Investigate**:
1. Review resource utilization during test execution
2. Check if failures occur at expected load thresholds
3. Verify graceful degradation behavior
4. Adjust stress test parameters if needed

## Integration with Development Workflow

### Pre-Commit Testing

Run foundation tests before committing changes:

```bash
# Quick validation before commit
python run_evaluation_suite.py --category foundation --quick
```

### Pre-Release Testing

Run comprehensive evaluation before releases:

```bash
# Complete evaluation with detailed reporting
python run_evaluation_suite.py --parallel --output-dir release_validation
```

### Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Comprehensive Evaluation
on: [push, pull_request]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install psutil opencv-python numpy
      - name: Run Evaluation Suite
        run: python run_evaluation_suite.py --quick --parallel --output-dir ci_results
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-reports
          path: ci_results/
```

## Best Practices

### Regular Testing

1. **Daily**: Run foundation tests during development
2. **Weekly**: Run integration tests to catch interaction issues
3. **Before Release**: Run complete evaluation suite
4. **Performance Monitoring**: Track quality trends over time

### Test Environment

1. **Consistent Environment**: Use same hardware/software for baseline comparisons
2. **Resource Monitoring**: Monitor system resources during test execution
3. **Network Stability**: Ensure stable network conditions for network tests
4. **Documentation**: Document any environmental factors affecting results

### Result Analysis

1. **Trend Monitoring**: Track quality scores over multiple executions
2. **Regression Detection**: Compare results with previous baselines
3. **Performance Analysis**: Focus on metrics relevant to research requirements
4. **Actionable Improvements**: Prioritize recommendations based on research impact

## Support and Documentation

### Additional Resources

- **API Documentation**: See `docs/api/` for detailed API documentation
- **Architecture Guide**: See `docs/ARCHITECTURE.md` for system design details
- **Development Guide**: See `docs/DEVELOPMENT.md` for contribution guidelines

### Getting Help

1. **Check Logs**: Review detailed execution logs for error messages
2. **Configuration**: Verify test configuration matches system capabilities
3. **Dependencies**: Ensure all required dependencies are installed
4. **Documentation**: Consult this guide and related documentation
5. **Issues**: Report persistent issues with detailed error logs and system information

## Future Enhancements

### Planned Improvements

1. **System Layer Implementation**: Complete end-to-end workflow testing
2. **Performance Layer Expansion**: Comprehensive performance and usability evaluation
3. **Automated Regression Detection**: Comparison with historical results
4. **Cloud Integration**: Distributed testing across multiple environments
5. **Real-time Monitoring**: Live performance monitoring during actual research sessions

### Contributing

To contribute to the evaluation suite:

1. Follow the test development patterns established in existing tests
2. Ensure new tests validate actual implementation code
3. Include comprehensive error handling and logging
4. Document test purpose, methodology, and acceptance criteria
5. Update this guide with any new test categories or procedures