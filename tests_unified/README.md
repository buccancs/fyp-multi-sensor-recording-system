# Unified Testing Framework for Multi-Sensor Recording System

This directory contains the consolidated and reorganized testing structure for the Multi-Sensor Recording System, consolidating tests from multiple scattered locations into a unified, hierarchical framework.

## Structure Overview

The unified testing framework follows a four-layer testing hierarchy that ensures comprehensive coverage from individual components to complete research workflows:

```
tests_unified/
├── unit/                    # Level 1: Component Testing
│   ├── android/            # Android component unit tests
│   ├── python/             # Python component unit tests
│   ├── calibration/        # Calibration system tests
│   ├── network/            # Network communication tests
│   └── sensors/            # Sensor integration tests
├── integration/            # Level 2: Cross-Component Testing
│   ├── device_coordination/    # Multi-device coordination
│   ├── network_protocols/      # Protocol communication
│   ├── synchronization/        # Timing and sync tests
│   └── session_management/     # Session lifecycle tests
├── system/                 # Level 3: End-to-End Testing
│   ├── workflows/          # Complete research workflows
│   ├── data_integrity/     # Multi-modal data validation
│   └── user_scenarios/     # Real-world usage scenarios
├── performance/            # Level 4: Performance & Quality
│   ├── load/               # Load and stress testing
│   ├── benchmarks/         # Performance benchmarking
│   ├── endurance/          # Long-running stability tests
│   └── quality/            # Research-grade quality validation
├── evaluation/             # Research Validation Framework
│   ├── foundation/         # Consolidated foundation tests
│   ├── compliance/         # Research compliance validation
│   └── metrics/            # Quality metrics and reporting
├── browser/                # Cross-Browser Compatibility
├── visual/                 # Visual Regression Testing
├── hardware/               # Hardware-in-the-Loop Testing
├── config/                 # Test configuration and fixtures
├── fixtures/               # Shared test fixtures and utilities
└── runners/                # Unified test execution scripts
```

## Migration from Previous Structure

This unified structure consolidates tests from:

- `/tests/` - Original test directory (browser, e2e, gui, hardware, integration, visual, web, load)
- `/evaluation_suite/` - Research validation framework
- `/PythonApp/` - Scattered test files and production testing
- Root-level test files

## Key Features

### 1. Hierarchical Organization
- **Clear separation** between test levels (unit → integration → system → performance)
- **Technology-agnostic** organization focused on testing concerns
- **Consistent structure** across all test categories

### 2. Research-Grade Quality
- **Comprehensive coverage** from component to end-to-end validation
- **Statistical validation** with confidence intervals and quality metrics
- **Research compliance** validation for scientific applications
- **Reproducible testing** with documented procedures

### 3. Unified Execution
- **Single test runner** supporting all test levels and types
- **Configurable execution** for different scenarios (CI, development, research)
- **Comprehensive reporting** with detailed metrics and recommendations

### 4. Backward Compatibility
- **Preserved functionality** from all previous test frameworks
- **Maintained markers** for existing CI/CD workflows
- **Compatible configuration** with existing tools and processes

## Usage

### Quick Start
```bash
# Run all tests
python tests_unified/runners/run_unified_tests.py

# Run specific test level
python tests_unified/runners/run_unified_tests.py --level unit
python tests_unified/runners/run_unified_tests.py --level integration
python tests_unified/runners/run_unified_tests.py --level system
python tests_unified/runners/run_unified_tests.py --level performance

# Run specific test category
python tests_unified/runners/run_unified_tests.py --category android
python tests_unified/runners/run_unified_tests.py --category evaluation

# Research validation mode
python tests_unified/runners/run_unified_tests.py --mode research
```

### Pytest Integration
```bash
# Run using pytest with new structure
pytest tests_unified/

# Run specific level
pytest tests_unified/unit/
pytest tests_unified/integration/

# Run with markers (preserved from original structure)
pytest -m "unit and not hardware_loop"
pytest -m "integration"
pytest -m "e2e"
```

## Quality Standards

The unified framework maintains research-grade quality standards:

- **Foundation Tests**: >95% success rate
- **Integration Tests**: >90% success rate  
- **System Tests**: >95% success rate
- **Performance Tests**: >85% success rate
- **Synchronization Precision**: <1ms temporal accuracy
- **Memory Usage**: <1GB peak usage during testing
- **Data Quality Score**: >0.8 for all collected data streams

## Test Categories and Markers

All existing pytest markers are preserved:

- `unit`, `integration`, `system`, `performance`
- `android`, `gui`, `network`, `hardware`
- `e2e`, `visual`, `load`, `browser`
- `slow`, `quick`, `hardware_loop`
- `security`, `privacy`, `accessibility`

## Configuration

Test configuration is centralized in `tests_unified/config/`:

- `pytest.ini` - Pytest configuration
- `test_config.yaml` - Unified test configuration
- `quality_thresholds.json` - Research quality standards
- `fixtures.py` - Shared test fixtures

## Documentation

- See individual README files in each subdirectory for specific details
- Test execution guides in `tests_unified/runners/`
- Migration documentation for updating existing tests
- Quality validation procedures in `tests_unified/evaluation/`

## Future Enhancements

- **Automated test discovery** and categorization
- **ML-based quality assessment** 
- **Cloud-distributed testing** across environments
- **Real-time performance monitoring** during development
- **Automated regression detection** with historical comparison