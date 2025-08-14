# Evaluation Tests Structure

This directory contains organized evaluation tests for the Multi-Sensor Recording System.

## Directory Structure

### `/architecture/`
- **test_architecture_enforcement.py** - Code quality and architectural compliance validation tests
- Validates layered architecture, dependency injection patterns, and separation of concerns

### `/research/`
- **test_thesis_claims_validation.py** - Validates research claims and thesis assertions
- **requirements_coverage_analysis.py** - Analyzes coverage of functional and non-functional requirements
- **requirements_coverage_report.json** - Generated coverage analysis results

### `/framework/`
- **test_framework.py** - Test framework validation and infrastructure tests
- **test_categories.py** - Test categorization and marker validation
- **test_results.py** - Test result processing and reporting validation

### `/data_collection/`
- **measurement_collection.py** - Data collection and measurement validation tests
- Validates sensor data quality, synchronization, and measurement accuracy

### `/foundation/`
- **android_tests.py** - Platform-specific Android foundation tests
- **pc_tests.py** - Platform-specific PC/desktop foundation tests

### `/metrics/`
- **performance_monitor.py** - Performance monitoring and benchmarking utilities
- **quality_validator.py** - Quality metrics validation and analysis

### `/compliance/`
- Reserved for compliance and regulatory validation tests

## Test Markers

Evaluation tests use the following pytest markers:
- `@pytest.mark.evaluation` - General evaluation tests
- `@pytest.mark.research` - Research validation tests  
- `@pytest.mark.architecture` - Architecture compliance tests
- `@pytest.mark.performance` - Performance evaluation tests

## Running Evaluation Tests

```bash
# Run all evaluation tests
python -m pytest tests_unified/evaluation/ -m evaluation

# Run specific categories
python -m pytest tests_unified/evaluation/architecture/ -v
python -m pytest tests_unified/evaluation/research/ -v
python -m pytest tests_unified/evaluation/framework/ -v

# Run with specific markers
python -m pytest -m "evaluation and research"
python -m pytest -m "evaluation and architecture"
```