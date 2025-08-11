# Migration Guide: Physical to Virtual Testing

This guide helps you transition from physical hardware testing to the virtual test environment for the GSR Recording System.

## 📋 Overview

The Virtual Test Environment provides a comprehensive simulation of the GSR recording system without requiring physical Android devices or hardware sensors. This migration guide covers the transition process, capability comparisons, and best practices.

## 🔄 Migration Process

### Phase 1: Assessment and Preparation

#### 1. Assess Current Testing Setup
```bash
# Document your current physical setup
echo "Current physical testing setup:"
echo "- Number of Android devices: ?"
echo "- Sensor types: Shimmer GSR, RGB cameras, thermal cameras"
echo "- Test scenarios: ?"
echo "- Test duration: ?"
echo "- Data validation methods: ?"
```

#### 2. Install Virtual Environment
```bash
# Clone and setup virtual environment
cd tests/integration/virtual_environment
./setup_dev_environment.sh

# Verify installation
python -c "from tests.integration.virtual_environment import VirtualTestConfig; print('✓ Ready')"
```

### Phase 2: Capability Mapping

#### Physical vs Virtual Capabilities Matrix

| Aspect | Physical Testing | Virtual Testing | Migration Notes |
|--------|------------------|-----------------|-----------------|
| **Device Count** | Limited by hardware (1-6 devices) | Unlimited (tested up to 6+) | ✅ **Same or better** |
| **GSR Data** | Real sensor readings | Synthetic with realistic patterns | ⚠️ **Deterministic simulation** |
| **Video Data** | Real camera feeds | Procedural RGB generation | ⚠️ **Synthetic content** |
| **Thermal Data** | Real thermal cameras | Simulated heat patterns | ⚠️ **Pattern-based simulation** |
| **Network Behaviour** | Real network conditions | Configurable latency/delays | ✅ **Controllable conditions** |
| **Synchronisation** | Hardware-dependent timing | Deterministic timing | ✅ **More reliable** |
| **Data Integrity** | Real-world variations | Consistent patterns | ✅ **Reproducible results** |
| **Setup Time** | 15-30 minutes | 2-5 minutes | ✅ **Faster** |
| **Reproducibility** | Variable conditions | Identical results | ✅ **Perfect reproducibility** |
| **Cost** | High (devices, maintenance) | Low (software only) | ✅ **Cost effective** |
| **Scalability** | Limited by hardware | Highly scalable | ✅ **Better scaling** |
| **CI/CD Integration** | Difficult/impossible | Native support | ✅ **CI/CD ready** |

### Phase 3: Test Scenario Conversion

#### Convert Physical Test Cases

**Before (Physical):**
```python
# Physical test setup
def setup_physical_test():
    devices = connect_android_devices()  # Wait for manual connection
    start_shimmer_sensors(devices)
    configure_cameras(devices)
    return devices

def run_stress_test():
    devices = setup_physical_test()
    record_for_minutes(10)
    validate_data_files()
```

**After (Virtual):**
```python
# Virtual test equivalent
def setup_virtual_test():
    config = VirtualTestConfig(
        test_name="stress_test_migration",
        device_count=3,  # Same as physical setup
        test_duration_minutes=10,
        device_capabilities=["shimmer", "rgb_video", "thermal"],
        gsr_sampling_rate_hz=128,  # Match physical sampling rate
    )
    runner = VirtualTestRunner(config)
    return runner

async def run_stress_test():
    runner = setup_virtual_test()
    metrics = await runner.run_test()
    validate_virtual_data(metrics)
```

#### Test Scenario Mapping

| Physical Test Scenario | Virtual Equivalent | Configuration |
|------------------------|-------------------|---------------|
| **Single Device Test** | `VirtualTestScenario.create_quick_test()` | 1 device, 2 minutes |
| **Multi-Device Sync** | `VirtualTestScenario.create_synchronization_test()` | 3-6 devices, sync validation |
| **Stress Testing** | `VirtualTestScenario.create_stress_test()` | High data rates, long duration |
| **Endurance Testing** | Custom config with `test_duration_minutes=60` | Extended duration |
| **Network Issues** | Custom config with `response_delay_ms=200` | Simulated network problems |

### Phase 4: Data Validation Migration

#### Update Validation Methods

**Physical Data Validation:**
```python
def validate_physical_data():
    gsr_files = glob("*.gsr")
    video_files = glob("*.mp4")
    thermal_files = glob("*.thermal")
    
    # Check file existence and sizes
    assert len(gsr_files) > 0
    assert len(video_files) > 0
    # Manual inspection required
```

**Virtual Data Validation:**
```python
def validate_virtual_data(metrics):
    # Automated validation with known patterns
    assert metrics.data_samples_collected > 1000
    assert metrics.devices_connected == metrics.devices_spawned
    assert metrics.synchronization_error_ms < 10
    
    # Validate synthetic data characteristics
    validate_gsr_patterns(metrics.gsr_data)
    validate_video_generation(metrics.video_stats)
    validate_thermal_patterns(metrics.thermal_data)
```

#### Validation Advantages

| Validation Aspect | Physical | Virtual | Benefits |
|-------------------|----------|---------|-----------|
| **Data Completeness** | Manual checking | Automated validation | ✅ **Automated** |
| **Timing Accuracy** | Hardware-dependent | Deterministic | ✅ **Precise** |
| **Pattern Recognition** | Difficult | Built-in patterns | ✅ **Predictable** |
| **Error Detection** | Post-processing | Real-time | ✅ **Immediate** |

## 🎯 Best Practices for Migration

### 1. Gradual Transition Strategy

```bash
# Week 1: Install and familiarize
./setup_dev_environment.sh
python quick_test.py

# Week 2: Convert simple test cases
pytest test_pytest_integration.py -v

# Week 3: Implement complex scenarios
python test_runner.py --scenario stress --devices 5

# Week 4: Full CI/CD integration
# Deploy to CI pipeline
```

### 2. Maintain Parallel Testing (Recommended)

During transition, run both physical and virtual tests:

```python
# Hybrid testing approach
async def comprehensive_test():
    # Virtual testing for development and CI
    virtual_metrics = await run_virtual_test()
    
    # Physical testing for final validation (weekly)
    if is_validation_week():
        physical_results = run_physical_test()
        compare_results(virtual_metrics, physical_results)
```

### 3. Custom Synthetic Data Patterns

Calibrate virtual data to match your physical patterns:

```python
# Customize synthetic data to match your hardware
class CustomSyntheticDataGenerator(SyntheticDataGenerator):
    def __init__(self, calibration_data=None):
        super().__init__()
        if calibration_data:
            self.calibrate_from_physical_data(calibration_data)
    
    def calibrate_from_physical_data(self, physical_data):
        # Adjust synthetic patterns to match physical characteristics
        self.gsr_baseline = np.mean(physical_data['gsr'])
        self.gsr_noise_level = np.std(physical_data['gsr']) * 0.1
        self.stress_event_magnitude = physical_data['stress_magnitude']
```

## 🔧 Configuration Migration

### Environment Variables

Create a configuration mapping for easy migration:

```bash
# .env file for migration
# Physical test settings
PHYSICAL_DEVICE_COUNT=3
PHYSICAL_TEST_DURATION=600  # 10 minutes
PHYSICAL_GSR_RATE=128

# Virtual test settings (mapped from physical)
VIRTUAL_DEVICE_COUNT=${PHYSICAL_DEVICE_COUNT}
VIRTUAL_TEST_DURATION_MINUTES=$((PHYSICAL_TEST_DURATION / 60))
VIRTUAL_GSR_SAMPLING_RATE_HZ=${PHYSICAL_GSR_RATE}
```

### Test Configuration Migration

```python
# config_migration.py
class TestConfigMigration:
    @staticmethod
    def from_physical_config(physical_config):
        return VirtualTestConfig(
            test_name=f"migrated_{physical_config.test_name}",
            device_count=physical_config.device_count,
            test_duration_minutes=physical_config.duration_seconds / 60,
            device_capabilities=physical_config.sensor_types,
            gsr_sampling_rate_hz=physical_config.gsr_sampling_rate,
            rgb_fps=physical_config.camera_fps,
            thermal_fps=physical_config.thermal_fps,
            # Virtual-specific optimisations
            simulate_file_transfers=True,
            enable_stress_events=True,
            headless_mode=True,
        )
```

## 📊 Performance Comparison

### Metrics to Monitor During Migration

| Metric | Physical Baseline | Virtual Target | Validation |
|--------|------------------|----------------|------------|
| **Setup Time** | 15-30 min | < 5 min | ✅ Faster |
| **Test Execution** | Variable | Consistent | ✅ Predictable |
| **Data Volume** | Device dependent | Configurable | ✅ Scalable |
| **Error Rate** | 5-10% | < 1% | ✅ More reliable |
| **Reproducibility** | ~70% | 100% | ✅ Perfect |

### Performance Benchmarks

```python
# Run migration performance comparison
def compare_migration_performance():
    # Measure virtual performance
    virtual_start = time.time()
    virtual_metrics = run_virtual_test_suite()
    virtual_duration = time.time() - virtual_start
    
    # Compare with historical physical data
    physical_baseline = load_physical_baseline()
    
    print(f"Setup time: {virtual_metrics.setup_time}s vs {physical_baseline.setup_time}s")
    print(f"Test execution: {virtual_duration}s vs {physical_baseline.execution_time}s")
    print(f"Success rate: {virtual_metrics.success_rate}% vs {physical_baseline.success_rate}%")
```

## 🚨 Common Migration Issues

### Issue 1: Data Pattern Differences
**Problem**: Virtual data doesn't match expected physical patterns
**Solution**: 
```python
# Calibrate virtual data generator
generator = SyntheticDataGenerator()
generator.load_calibration_from_file("physical_data_baseline.json")
```

### Issue 2: Timing Sensitivity
**Problem**: Tests rely on specific hardware timing
**Solution**:
```python
# Use deterministic timing in virtual environment
config = VirtualTestConfig(
    device_response_delay_ms=50,  # Consistent timing
    heartbeat_interval_seconds=2.0,  # Predictable intervals
)
```

### Issue 3: File Size Expectations
**Problem**: Virtual files don't match physical file sizes
**Solution**:
```python
# Configure realistic file sizes
config = VirtualTestConfig(
    simulate_file_transfers=True,
    video_file_size_mb=100,  # Match physical camera files
    thermal_file_size_mb=50,  # Match thermal camera files
)
```

## ✅ Migration Checklist

### Pre-Migration
- [ ] Document current physical test setup
- [ ] Install virtual test environment
- [ ] Run basic virtual tests
- [ ] Identify critical test scenarios

### During Migration
- [ ] Convert test scenarios one by one
- [ ] Validate virtual results against physical baselines
- [ ] Update test automation scripts
- [ ] Train team on virtual environment

### Post-Migration
- [ ] Integrate virtual tests into CI/CD
- [ ] Establish performance monitoring
- [ ] Create documentation for team
- [ ] Schedule periodic physical validation

### Validation Criteria
- [ ] All test scenarios converted successfully
- [ ] Virtual test results are consistent and reproducible
- [ ] CI/CD pipeline includes virtual tests
- [ ] Team is comfortable with virtual environment
- [ ] Performance metrics meet or exceed physical testing

## 🎓 Training and Support

### Team Training Plan
1. **Week 1**: Introduction to virtual environment
2. **Week 2**: Hands-on test conversion
3. **Week 3**: Advanced configuration and customization
4. **Week 4**: CI/CD integration and automation

### Support Resources
- **Documentation**: `README.md`, `IMPLEMENTATION_SUMMARY.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **Examples**: `examples.py`, test files
- **Community**: GitHub Issues, team Slack channel

## 🔮 Future Considerations

### Hybrid Testing Strategy
- Use virtual testing for development and CI/CD
- Maintain physical testing for final validation
- Periodic calibration of virtual environment

### Continuous Improvement
- Collect feedback on virtual vs physical differences
- Enhance synthetic data patterns based on real-world data
- Optimise performance based on usage patterns

### Migration Success Metrics
- Reduced test setup time by >80%
- Increased test reproducibility to 100%
- Enabled automated CI/CD testing
- Reduced hardware maintenance costs
- Improved developer productivity

---

**Migration Support**: For questions or issues during migration, consult `TROUBLESHOOTING.md` or create a GitHub issue with the `migration` label.