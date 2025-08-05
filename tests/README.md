# Test Suite

Consolidated test suite for all components of the multi-sensor recording system. This directory contains comprehensive test coverage for the entire system.

## Contents

- **consolidated_tests.py** - Single consolidated test file containing all test cases from 83 original test files

## Test Coverage

The consolidated test suite includes:
- Unit tests for all Python modules
- Integration tests for system components
- Network communication testing
- GUI component validation
- Calibration system testing
- Session management testing
- Error handling validation
- Performance benchmarking tests

## Test Categories

Tests are organized by functionality:
- Core application logic tests
- Network protocol testing
- User interface component tests
- Sensor data processing validation
- Calibration accuracy testing
- Session management verification
- Error handling and recovery tests

## Usage

Run the complete test suite:
```bash
pytest tests/consolidated_tests.py
```

The consolidated approach ensures all test functionality is preserved while maintaining a clean, organized testing structure.