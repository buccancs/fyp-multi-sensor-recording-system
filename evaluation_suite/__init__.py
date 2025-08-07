"""
complete Evaluation Suite for Multi-Sensor Recording System

This evaluation suite implements the thorough testing strategy outlined 
in Chapter 5 of the thesis documentation, providing systematic validation
across all system abstraction levels.

Testing Architecture:
- Foundation Testing Layer: Unit tests for components and algorithms
- Integration Testing Layer: Cross-component and cross-platform testing
- System Testing Layer: End-to-end workflow validation
- Performance Testing Layer: Performance, reliability, and usability evaluation

Components:
- TestFramework: Central test coordination and execution
- QualityValidator: Test result validation and quality assessment
- Multi-layer test suites: complete test coverage
- Performance monitoring: Real-time metrics collection
- Reporting system: complete test analysis and documentation
"""

__version__ = "1.0.0"
__author__ = "Multi-Sensor Recording System Team"

from .framework.test_framework import TestFramework
from .framework.quality_validator import QualityValidator
from .framework.test_categories import TestCategory
from .framework.test_results import TestResults, TestResult, SuiteResults

__all__ = [
    "TestFramework",
    "QualityValidator", 
    "TestCategory",
    "TestResults",
    "TestResult",
    "SuiteResults"
]