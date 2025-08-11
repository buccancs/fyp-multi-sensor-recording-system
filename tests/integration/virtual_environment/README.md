# Virtual Test Environment for GSR Recording System

This directory contains a comprehensive virtual test environment that simulates multiple Android devices connecting to the PC controller, generating realistic sensor data streams to test system performance, synchronization, and data handling without requiring physical hardware.

## Overview

The virtual test environment implements socket-based mock Android devices that mimic the behavior of real smartphones running the GSR recording app. It provides:

- **Multiple Virtual Devices**: Simulate 3-6 (or more) Android devices simultaneously
- **Realistic Sensor Data**: Generate synthetic GSR, RGB video, and thermal data at proper rates
- **Complete Protocol Support**: Full implementation of the PC-Android communication protocol
- **Performance Monitoring**: Track system resource usage and validate performance thresholds
- **Automated Validation**: Verify data integrity, synchronization accuracy, and throughput
- **CI/CD Integration**: Docker support and GitHub Actions workflows for automated testing

## Architecture

### Components

1. **VirtualDeviceClient** (`virtual_device_client.py`)
   - Simulates an Android device connecting via TCP socket
   - Implements the complete JSON message protocol
   - Handles recording commands, sync signals, and file transfers
   - Generates realistic response delays and heartbeat behavior

2. **SyntheticDataGenerator** (`synthetic_data_generator.py`)
   - Generates realistic sensor data streams:
     - GSR: 128Hz with physiological patterns (stress events, noise, drift)
     - RGB Video: 30fps with procedural content and motion
     - Thermal: 9fps with heat patterns and moving hotspots
   - Configurable data characteristics and batch generation

3. **VirtualTestRunner** (`test_runner.py`)
   - Orchestrates complete test scenarios
   - Manages device lifecycle and coordination
   - Monitors performance and collects metrics
   - Validates results and generates reports

4. **TestConfiguration** (`test_config.py`)
   - Comprehensive configuration system
   - Predefined test scenarios (quick, stress, endurance, CI)
   - Environment variable support and validation

## Quick Start

### Prerequisites

- Python 3.10+ with the project dependencies installed
- At least 4GB RAM and 2 CPU cores for multi-device tests
- Docker (optional, for containerized testing)

### Basic Usage

1. **Quick Test** (2 devices, 1 minute):
   ```bash
   cd tests/integration/virtual_environment
   python test_runner.py --scenario quick --devices 2 --duration 1.0
   ```

2. **Using the Shell Script**:
   ```bash
   ./run_virtual_test.sh --scenario quick --devices 3 --duration 2.0 --verbose
   ```

3. **CI Test**:
   ```bash
   ./run_virtual_test.sh --ci --scenario ci --devices 3
   ```

4. **Docker Test**:
   ```bash
   ./run_virtual_test.sh --docker --scenario stress --devices 5 --duration 10.0
   ```

### Test Scenarios

#### Quick Test
- **Purpose**: Fast functionality validation
- **Duration**: 1 minute
- **Devices**: 2
- **Data**: Basic GSR streaming, no file transfers
- **Use Case**: Development, PR validation

#### Stress Test  
- **Purpose**: High-load validation with realistic data rates
- **Duration**: 30 minutes
- **Devices**: 6
- **Data**: Full sensor suite (GSR 128Hz, RGB 30fps, Thermal 9fps)
- **Use Case**: Performance validation, load testing

#### Synchronization Test
- **Purpose**: Validate multi-device timing accuracy
- **Duration**: 10 minutes  
- **Devices**: 5
- **Data**: Clean GSR data for timing analysis
- **Use Case**: Synchronization algorithm validation

#### CI Test
- **Purpose**: Conservative test for CI pipelines
- **Duration**: 3 minutes
- **Devices**: 3
- **Data**: Moderate load with file transfers
- **Use Case**: Automated testing, regression detection

#### Endurance Test
- **Purpose**: Long-term stability and memory leak detection
- **Duration**: 2+ hours
- **Devices**: 4
- **Data**: Continuous operation with multiple sessions
- **Use Case**: Stability validation, memory leak detection

## Configuration

### Environment Variables

The test environment supports configuration via environment variables:

```bash
export GSR_TEST_DEVICE_COUNT=5          # Number of virtual devices
export GSR_TEST_DURATION_MINUTES=10.0   # Test duration
export GSR_TEST_SERVER_PORT=9000        # PC server port
export GSR_TEST_CI_MODE=true            # Enable CI optimizations
export GSR_TEST_OUTPUT_DIR=/tmp/results # Output directory
export GSR_TEST_LOG_LEVEL=INFO          # Logging level
export GSR_TEST_HEADLESS=true           # Disable GUI components
```

### Configuration Files

Create custom test configurations in JSON format:

```json
{
  "test_name": "custom_test",
  "test_description": "Custom test configuration",
  "device_count": 4,
  "test_duration_minutes": 15.0,
  "recording_duration_minutes": 12.0,
  "gsr_sampling_rate_hz": 128,
  "rgb_fps": 30,
  "thermal_fps": 9,
  "enable_stress_events": true,
  "simulate_file_transfers": true,
  "enable_performance_monitoring": true,
  "validate_synchronization": true,
  "max_sync_jitter_ms": 50.0
}
```

Load with:
```bash
python test_runner.py --config custom_config.json
```

## Data Generation

### GSR (Galvanic Skin Response)
- **Rate**: 128 samples/second per device
- **Baseline**: ~0.8 μS with realistic drift
- **Noise**: Physiological noise and measurement artifacts  
- **Stress Events**: Configurable stress response spikes
- **Breathing/Heart**: Subtle periodic components

### RGB Video
- **Rate**: 30 frames/second per device
- **Content**: Procedural patterns with motion
- **Size**: ~50KB per compressed frame
- **File Transfer**: Simulated MP4 files after recording

### Thermal Imaging
- **Rate**: 9 frames/second per device
- **Resolution**: 64x48 pixels (configurable)
- **Content**: Heat patterns with moving hotspots
- **Data**: 16-bit temperature values
- **File Transfer**: Raw thermal data files

## Performance Monitoring

The test environment continuously monitors:

- **Memory Usage**: RSS, VMS, and available memory
- **CPU Usage**: Process and system CPU utilization
- **Network Throughput**: Data transfer rates and message counts
- **File Descriptors**: Open file count monitoring
- **Thread Count**: Active thread monitoring
- **Response Times**: Command response latencies

### Performance Thresholds

Default thresholds (configurable):
- Memory leak detection: 100MB growth over 2 hours
- CPU usage warning: >80% sustained
- Sync jitter limit: <50ms between devices
- Data integrity: >95% of expected samples received

## Validation and Metrics

### Data Integrity Validation
- Counts expected vs. received data samples
- Validates file transfer completeness
- Checks for data corruption or loss

### Synchronization Validation  
- Measures timing accuracy between devices
- Validates sync signal response times
- Checks for clock drift and jitter

### Performance Validation
- Monitors resource usage against thresholds
- Detects memory leaks and performance degradation
- Validates system stability over time

## Docker Usage

### Building the Image

```bash
cd tests/integration/virtual_environment
docker build -t gsr-virtual-test -f Dockerfile ../../..
```

### Running Tests

```bash
# Quick test
docker run --rm -v $(pwd)/results:/app/test_results \
  gsr-virtual-test --scenario quick --devices 2 --duration 1.0

# CI test  
docker run --rm -v $(pwd)/results:/app/test_results \
  -e GSR_TEST_CI_MODE=true \
  gsr-virtual-test --scenario ci --devices 3 --duration 2.0

# Custom configuration
docker run --rm -v $(pwd)/results:/app/test_results \
  -v $(pwd)/configs:/app/configs:ro \
  gsr-virtual-test --config /app/configs/custom.json
```

### Docker Compose

Use the provided `docker-compose.yml` for easier orchestration:

```bash
# Quick test
docker-compose up virtual-test

# Stress test
docker-compose --profile stress up stress-test

# CI test
docker-compose --profile ci up ci-test
```

## CI/CD Integration

### GitHub Actions

The workflow `.github/workflows/virtual-test-environment.yml` provides:

- **PR Validation**: Quick tests on pull requests
- **Comprehensive CI**: Multiple scenarios and device counts
- **Performance Baselines**: Stress tests on main branch  
- **Docker Testing**: Container-based validation
- **Result Aggregation**: Summary reports and artifacts

### Integration Examples

```yaml
# Add to your workflow
- name: Run Virtual GSR Test
  run: |
    cd tests/integration/virtual_environment
    ./run_virtual_test.sh --ci --scenario ci --devices 3
    
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: gsr-virtual-test-results
    path: tests/integration/virtual_environment/test_results/
```

## Output and Reports

### Test Reports

Each test generates comprehensive JSON reports:

```json
{
  "test_info": {
    "name": "quick_test",
    "start_time": "2024-01-15T10:30:00Z",
    "duration_seconds": 62.5
  },
  "summary": {
    "overall_passed": true,
    "devices_connected": "3/3",
    "sessions_completed": "1/1", 
    "data_samples_collected": 24576,
    "error_count": 0
  },
  "performance": {
    "peak_memory_mb": 156.2,
    "peak_cpu_percent": 45.8,
    "data_throughput_mbps": 2.4
  },
  "validation": {
    "data_integrity_passed": true,
    "synchronization_passed": true,
    "performance_passed": true
  }
}
```

### Artifacts

- **Test Reports**: JSON summaries with pass/fail status
- **Performance Metrics**: Detailed resource usage over time
- **Log Files**: Complete execution logs (if enabled)
- **Raw Data Samples**: Data samples for analysis (optional)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check for existing processes
   lsof -i :9000
   # Kill if necessary
   sudo kill <pid>
   ```

2. **Memory Issues**
   ```bash
   # Reduce device count or duration
   export GSR_TEST_DEVICE_COUNT=2
   export GSR_TEST_DURATION_MINUTES=1.0
   ```

3. **Docker Build Issues**
   ```bash
   # Clean Docker cache
   docker system prune -f
   # Rebuild without cache
   docker build --no-cache -t gsr-virtual-test .
   ```

4. **Permission Issues**
   ```bash
   # Make script executable
   chmod +x run_virtual_test.sh
   # Fix output directory permissions
   sudo chown -R $USER:$USER test_results/
   ```

### Debug Mode

Enable verbose logging and debug output:

```bash
export GSR_TEST_LOG_LEVEL=DEBUG
python test_runner.py --scenario quick --devices 1 --duration 0.5 --verbose
```

### Performance Tuning

For resource-constrained environments:

```bash
# Minimal test
export GSR_TEST_DEVICE_COUNT=1
export GSR_TEST_DURATION_MINUTES=0.5
./run_virtual_test.sh --scenario quick --devices 1 --duration 0.5
```

## Development

### Adding New Test Scenarios

1. Create configuration in `test_config.py`:
   ```python
   @classmethod
   def create_custom_test(cls) -> "TestScenario":
       config = VirtualTestConfig(
           test_name="custom_test",
           # ... configuration
       )
       return cls(name="Custom Test", config=config)
   ```

2. Add to scenario choices in `test_runner.py`

3. Update documentation and examples

### Extending Data Generation

1. Add new sensor type to `SyntheticDataGenerator`
2. Update `VirtualDeviceClient` to handle new data type
3. Add validation logic to `VirtualTestRunner`
4. Update configuration options

### Custom Validation

Implement custom validation logic:

```python
class CustomTestRunner(VirtualTestRunner):
    def _validate_custom_metric(self) -> bool:
        # Custom validation logic
        return True
        
    def _validate_results(self) -> None:
        super()._validate_results()
        custom_passed = self._validate_custom_metric()
        self.metrics.custom_validation_passed = custom_passed
```

## Contributing

When contributing to the virtual test environment:

1. Run the full test suite before submitting
2. Update documentation for new features
3. Add appropriate test scenarios for new functionality
4. Ensure Docker builds work correctly
5. Validate CI integration

## Performance Benchmarks

Typical resource usage (Ubuntu 22.04, 8GB RAM, 4 cores):

| Scenario | Devices | Duration | Peak Memory | Peak CPU | Throughput |
|----------|---------|----------|-------------|----------|------------|
| Quick    | 2       | 1min     | ~80MB      | ~30%     | 1.2 MB/s   |
| CI       | 3       | 3min     | ~120MB     | ~45%     | 2.1 MB/s   |
| Stress   | 6       | 30min    | ~250MB     | ~65%     | 4.8 MB/s   |

These benchmarks help validate system performance and detect regressions.

## Future Enhancements

Planned improvements:

- **Real-time visualization dashboard** for test monitoring
- **Automated performance regression detection**
- **Integration with external monitoring tools** (Prometheus, Grafana)
- **Support for additional sensor types** (EEG, ECG)
- **Advanced failure injection** for resilience testing
- **Cloud deployment options** for large-scale testing

---

For questions or issues with the virtual test environment, please refer to the project documentation or create an issue in the repository.