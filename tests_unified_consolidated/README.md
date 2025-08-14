# Consolidated Test Suite

This directory contains all Python tests consolidated from across the repository into a unified, organized structure.

## Test Organization

### Test Categories

- **`android/`** - Android app integration and device tests (24 files)
- **`gui/`** - GUI and user interface tests (12 files)
- **`system/`** - System and environment tests (4 files)
- **`integration/`** - Multi-component integration tests (8 files)
- **`performance/`** - Performance, load, and endurance tests (4 files)
- **`network/`** - Network communication tests (0 files)
- **`hardware/`** - Hardware integration tests (8 files)
- **`unit/`** - Unit tests for individual components (23 files)
- **`e2e/`** - End-to-end workflow tests (0 files)
- **`fixtures/`** - Test fixtures and utilities (0 files)
- **`utils/`** - Test utilities and helpers (0 files)
- **`config/`** - Test configuration files (0 files)

### Total: 93 test files

## Running Tests

### Run All Tests
```bash
python run_all_tests.py
```

### Run Specific Category
```bash
python run_all_tests.py --category android
python run_all_tests.py --category gui
python run_all_tests.py --category system
```

### List Available Categories
```bash
python run_all_tests.py --list-categories
```

### Using pytest directly
```bash
# Run all tests
pytest -v

# Run specific category
pytest android/ -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## Test Framework

- **pytest** - Primary testing framework
- **Robolectric** - Android unit testing
- **Appium** - Android UI testing
- **PyQt5 Testing** - GUI testing
- **asyncio** - Async test support
- **Mock/MagicMock** - Test doubles

## Coverage Goals

- **Unit Tests**: 95%+ line coverage
- **Integration Tests**: All component interactions
- **GUI Tests**: All user interaction paths
- **Android Tests**: All activities and workflows
- **Performance Tests**: All critical performance paths

## Test Structure Standards

Each test file should include:
- Comprehensive docstring describing test scope
- Setup and teardown methods
- Edge case and error condition testing
- Performance and resource usage validation
- Clear assertions with descriptive messages

## Continuous Integration

These tests are integrated into the CI/CD pipeline:
- **Fast Lane**: Unit and basic integration tests
- **Nightly**: Full test suite including performance tests
- **Release**: Complete validation including UI and E2E tests

## Contributing

When adding new tests:
1. Place in appropriate category directory
2. Follow existing naming conventions
3. Include comprehensive test coverage
4. Add appropriate fixtures and utilities
5. Update this README if adding new categories
