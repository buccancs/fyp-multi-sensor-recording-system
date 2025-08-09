# Unified Test Documentation

This document provides a comprehensive overview of the testing strategy and implementation for the Multi-Sensor Recording System for Contactless GSR Prediction Research.

## Overview

The system employs a multi-layered testing approach that ensures reliability, performance, and security across all components:

- **Python Desktop Controller**: Unit tests, integration tests, and GUI tests
- **Android Mobile Application**: Unit tests, UI tests, and device integration tests  
- **Multi-Device Synchronization**: Protocol tests and timing validation
- **End-to-End System Tests**: Complete recording session validation

## Test Execution

For detailed test execution instructions, see:
- [Test Execution Guide](docs/test_execution_guide.md)
- [Test Troubleshooting](docs/test_troubleshooting.md)

## Test Categories

### Unit Tests
- **Python**: Located in `tests/` directory, run with `pytest`
- **Android**: Located in `AndroidApp/src/test/`, run with `./gradlew test`

### Integration Tests  
- **Network Protocol**: WebSocket communication validation
- **Device Synchronization**: Multi-device timing accuracy
- **Data Pipeline**: End-to-end data flow verification

### Performance Tests
- **Synchronization Accuracy**: <10ms timing precision
- **Resource Usage**: Memory and CPU monitoring
- **Battery Optimization**: Android power consumption

### Security Tests
- **Data Privacy**: No sensitive data in logs
- **Network Security**: Encrypted communication validation
- **Hardware Security**: Android keystore integration

## Quick Start

```bash
# Run all Python tests
cd PythonApp && python -m pytest

# Run all Android tests  
cd AndroidApp && ./gradlew test

# Run evaluation suite
cd evaluation_suite && python -m pytest
```

## Test Results

Recent test execution results are maintained in:
- [Evaluation Results](results/evaluation_results/)
- [Quick Test Results](results/quick_test_results/)

## Contributing

When adding new features:
1. Write tests before implementation (TDD approach)
2. Ensure >80% code coverage for new modules
3. Validate against existing test suite
4. Update this documentation for new test categories

For detailed contribution guidelines and test requirements, see the individual component README files and the evaluation suite documentation.