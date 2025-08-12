# Data Collection Guidelines - Academic Integrity

## 🚨 CRITICAL: No Fake Data in Research

This repository implements a multi-sensor recording system for academic research. To maintain **academic integrity** and research validity, the following strict guidelines apply:

## Test vs. Production Code

### ❌ **TEST CODE** (Never for Real Experiments)
- Files in `tests/` directory
- Code blocks marked with "synthetic", "fake", or "test only"
- Any function containing `if __name__ == "__main__"` demo code
- Mock/simulated data generators

**These are for code validation only and generate synthetic data.**

### ✅ **PRODUCTION CODE** (For Real Experiments)
- `PythonApp/recording/production_data_recorder.py` - Enforces real hardware
- Hardware validation modules
- Authenticated sensor interfaces
- Real-time data capture from physical devices

## Academic Research Requirements

### For Real Experiments, You MUST:

1. **Use Actual Hardware**
   - Physical Shimmer3 GSR+ devices
   - Real Topdon TC001 thermal cameras
   - Actual smartphone cameras
   - No simulators or mock devices

2. **Validate Hardware Connections**
   ```python
   from recording.production_data_recorder import ProductionDataRecorder
   
   # This enforces real hardware validation
   recorder = ProductionDataRecorder(session, logger)
   recorder.validate_hardware_connection("shimmer_gsr", real_connection_callback)
   ```

3. **Ethics Approval**
   - Obtain proper ethics committee approval
   - Document participant consent
   - Follow institutional guidelines

4. **Data Authenticity**
   - All data must come from real sensors
   - No synthetic or generated data
   - Complete audit trail of data sources

## Detecting and Preventing Fake Data

The `ProductionDataRecorder` class actively prevents fake data:

```python
# This will REJECT any data containing fake markers
try:
    recorder.record_sensor_data(device_type, data)
except SyntheticDataError:
    print("Fake data detected and rejected!")
```

## File Structure

```
PythonApp/
├── recording/
│   ├── comprehensive_data_recorder.py  # ⚠️  Contains test code (see warnings)
│   └── production_data_recorder.py     # ✅  Production use only
├── tests/                              # ❌  All synthetic data
│   ├── test_performance_verification.py
│   ├── test_thesis_claims_validation.py
│   └── ...
└── ...
```

## Warnings in Code

Look for these warning markers that indicate test-only code:

```python
# WARNING: THIS IS TEST/DEMO CODE ONLY
# SYNTHETIC DATA FOR TESTING ONLY
# NOT FOR REAL EXPERIMENTAL DATA
```

## Validation Report

For real experiments, always generate a validation report:

```python
recorder.export_validation_report("validation_report.json")
```

This creates an audit trail proving data authenticity.

## Academic Compliance

This system is designed to meet academic integrity standards:

- **No data fabrication**: All production data must be authentic
- **Full traceability**: Complete audit logs of data sources  
- **Hardware verification**: Enforced connection to real devices
- **Ethics compliance**: Built-in support for consent and anonymization

## Contact

For questions about proper usage for academic research, contact the research team or refer to your institution's research integrity guidelines.

---

**Remember: Academic integrity is paramount. When in doubt, verify that your data collection uses real hardware and authentic sensor readings.**