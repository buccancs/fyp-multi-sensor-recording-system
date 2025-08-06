# Test Suite

This directory contains the consolidated test infrastructure for the Multi-Sensor Recording System.

## Structure

- `consolidated_tests.py` - All Python test suites in one file
- `run_tests.py` - Python test runner
- `run_android_tests.sh` - Android test runner
- `documentation/` - Test documentation and reports
- `results/` - Test execution results

## Running Tests

**Python Tests:**
```bash
cd tests/
python run_tests.py
```

**Android Tests:**
```bash
cd tests/
./run_android_tests.sh
```
