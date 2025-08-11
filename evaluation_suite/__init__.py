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