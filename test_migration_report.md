# Test Migration Report

## Summary

- **Total test files found:** 4
- **Files to migrate:** 4
- **Files already in unified structure:** 0

## Files by Category

### Unit
- [CLIPBOARD] To migrate `/home/runner/work/bucika_gsr/bucika_gsr/test_device_connectivity.py`
- [CLIPBOARD] To migrate `/home/runner/work/bucika_gsr/bucika_gsr/test_thermal_recorder_security_fix.py`

### Android
- [CLIPBOARD] To migrate `/home/runner/work/bucika_gsr/bucika_gsr/test_android_connection_detection.py`

### Integration
- [CLIPBOARD] To migrate `/home/runner/work/bucika_gsr/bucika_gsr/test_pc_server_integration.py`

## Migration Plan
- `/home/runner/work/bucika_gsr/bucika_gsr/test_device_connectivity.py` -> `/home/runner/work/bucika_gsr/bucika_gsr/tests_unified/unit/python/test_device_connectivity.py`
- `/home/runner/work/bucika_gsr/bucika_gsr/test_thermal_recorder_security_fix.py` -> `/home/runner/work/bucika_gsr/bucika_gsr/tests_unified/unit/python/test_thermal_recorder_security_fix.py`
- `/home/runner/work/bucika_gsr/bucika_gsr/test_android_connection_detection.py` -> `/home/runner/work/bucika_gsr/bucika_gsr/tests_unified/unit/android/test_android_connection_detection.py`
- `/home/runner/work/bucika_gsr/bucika_gsr/test_pc_server_integration.py` -> `/home/runner/work/bucika_gsr/bucika_gsr/tests_unified/integration/device_coordination/test_pc_server_integration.py`

## Next Steps

1. **Review the migration plan** above
2. **Run migration:** `python tests_unified/migration/migrate_tests.py --execute`
3. **Update CI/CD workflows** to use unified test runner
4. **Update documentation** with new test structure
5. **Test the migration** by running unified test suite

## Migration Commands

```bash
# Dry run (default)
python tests_unified/migration/migrate_tests.py

# Execute migration
python tests_unified/migration/migrate_tests.py --execute

# Generate report only
python tests_unified/migration/migrate_tests.py --report-only
```

## Unified Test Runner Usage

After migration, use the unified test runner:

```bash
# Run all tests
python tests_unified/runners/run_unified_tests.py

# Run specific categories
python tests_unified/runners/run_unified_tests.py --category android
python tests_unified/runners/run_unified_tests.py --level unit

# Quick validation
python tests_unified/runners/run_unified_tests.py --quick
```
