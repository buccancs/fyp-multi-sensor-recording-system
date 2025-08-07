"""
Quality Validator for Test Results

Implements automated quality validation for test results following
the validation methodology framework from Chapter 5.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics

from .test_results import TestResults, SuiteResults, TestResult, TestStatus
from .test_categories import QualityThresholds, TestCategory, TestType

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Individual validation rule for test assessment"""
    name: str
    description: str
    threshold: float
    comparison: str  # 'gt', 'gte', 'lt', 'lte', 'eq', 'range'
    threshold_max: Optional[float] = None  # For range comparisons
    weight: float = 1.0  # Weight for overall quality calculation
    critical: bool = False  # Critical rules must pass


@dataclass
class ValidationIssue:
    """Represents a validation issue found during assessment"""
    rule_name: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    measured_value: float
    threshold_value: float
    test_names: List[str]


@dataclass
class SuiteValidation:
    """Validation results for a test suite"""
    suite_name: str
    suite_category: TestCategory
    
    success_rate_valid: bool = False
    performance_valid: bool = False
    quality_valid: bool = False
    coverage_valid: bool = False
    
    overall_valid: bool = False
    quality_score: float = 0.0
    
    issues: List[ValidationIssue] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class ValidationReport:
    """complete validation report for test execution"""
    execution_id: str
    timestamp: datetime
    
    overall_quality: float = 0.0
    overall_valid: bool = False
    
    suite_validations: Dict[str, SuiteValidation] = None
    critical_issues: List[ValidationIssue] = None
    quality_issues: List[ValidationIssue] = None
    recommendations: List[str] = None
    
    # Statistical validation results
    statistical_summary: Dict[str, float] = None
    confidence_intervals: Dict[str, Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.suite_validations is None:
            self.suite_validations = {}
        if self.critical_issues is None:
            self.critical_issues = []
        if self.quality_issues is None:
            self.quality_issues = []
        if self.recommendations is None:
            self.recommendations = []
        if self.statistical_summary is None:
            self.statistical_summary = {}
        if self.confidence_intervals is None:
            self.confidence_intervals = {}


class QualityValidator:
    """
    Automated quality validation for test results
    
    Implements the validation methodology framework with statistical validation,
    reproducibility assessment, and research compliance validation.
    """
    
    def __init__(self, quality_thresholds: Optional[QualityThresholds] = None):
        self.quality_thresholds = quality_thresholds or QualityThresholds()
        self.validation_rules: Dict[str, List[ValidationRule]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize default validation rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default validation rules for all test categories"""
        
        # Foundation layer rules
        foundation_rules = [
            ValidationRule(
                name="success_rate_foundation",
                description="Foundation tests must have >98% success rate",
                threshold=0.98,
                comparison="gte",
                weight=2.0,
                critical=True
            ),
            ValidationRule(
                name="execution_time_foundation", 
                description="Foundation tests should execute quickly",
                threshold=300.0,  # 5 minutes
                comparison="lte",
                weight=1.0
            ),
            ValidationRule(
                name="coverage_foundation",
                description="Foundation tests must achieve >90% coverage",
                threshold=0.90,
                comparison="gte",
                weight=1.5,
                critical=True
            )
        ]
        self.validation_rules[TestCategory.FOUNDATION.name] = foundation_rules
        
        # Integration layer rules
        integration_rules = [
            ValidationRule(
                name="success_rate_integration",
                description="Integration tests must have >95% success rate", 
                threshold=0.95,
                comparison="gte",
                weight=2.0,
                critical=True
            ),
            ValidationRule(
                name="latency_integration",
                description="Network latency should be <100ms",
                threshold=100.0,
                comparison="lte",
                weight=1.5
            ),
            ValidationRule(
                name="sync_precision",
                description="Synchronization precision must be <1ms",
                threshold=1.0,
                comparison="lte",
                weight=2.0,
                critical=True
            )
        ]
        self.validation_rules[TestCategory.INTEGRATION.name] = integration_rules
        
        # System layer rules
        system_rules = [
            ValidationRule(
                name="success_rate_system",
                description="System tests must have >95% success rate",
                threshold=0.95,
                comparison="gte", 
                weight=2.0,
                critical=True
            ),
            ValidationRule(
                name="data_quality_system",
                description="Data quality score must be >0.8",
                threshold=0.8,
                comparison="gte",
                weight=1.5,
                critical=True
            ),
            ValidationRule(
                name="workflow_completion",
                description="End-to-end workflows must complete successfully",
                threshold=0.95,
                comparison="gte",
                weight=2.0,
                critical=True
            )
        ]
        self.validation_rules[TestCategory.SYSTEM.name] = system_rules
        
        # Performance layer rules
        performance_rules = [
            ValidationRule(
                name="success_rate_performance",
                description="Performance tests must have >90% success rate",
                threshold=0.90,
                comparison="gte",
                weight=1.5
            ),
            ValidationRule(
                name="memory_usage",
                description="Memory usage should be <1GB",
                threshold=1000.0,
                comparison="lte",
                weight=1.0
            ),
            ValidationRule(
                name="cpu_usage",
                description="CPU usage should be <60%",
                threshold=60.0,
                comparison="lte", 
                weight=1.0
            ),
            ValidationRule(
                name="throughput_performance",
                description="Data throughput should meet target >25MB/s",
                threshold=25.0,
                comparison="gte",
                weight=1.5
            )
        ]
        self.validation_rules[TestCategory.PERFORMANCE.name] = performance_rules
    
    def register_validation_rule(self, test_category: TestCategory, rule: ValidationRule):
        """Register a custom validation rule for specific test category"""
        category_name = test_category.name
        if category_name not in self.validation_rules:
            self.validation_rules[category_name] = []
        self.validation_rules[category_name].append(rule)
        
        self.logger.info(f"Registered validation rule '{rule.name}' for category {category_name}")
    
    def validate_test_results(self, test_results: TestResults) -> ValidationReport:
        """
        Validate test results against quality criteria
        
        Performs thorough validation including:
        - Success rate validation
        - Performance threshold checking  
        - Statistical validation
        - Research compliance assessment
        """
        self.logger.info(f"Starting validation for execution {test_results.execution_id}")
        
        validation_report = ValidationReport(
            execution_id=test_results.execution_id,
            timestamp=datetime.now()
        )
        
        # Validate each test suite
        for suite_name, suite_results in test_results.suite_results.items():
            suite_validation = self._validate_suite_results(suite_results)
            validation_report.suite_validations[suite_name] = suite_validation
            
            # Collect critical issues
            for issue in suite_validation.issues:
                if issue.severity == 'critical':
                    validation_report.critical_issues.append(issue)
                else:
                    validation_report.quality_issues.append(issue)
        
        # Calculate overall quality score
        validation_report.overall_quality = self._calculate_overall_quality(validation_report)
        validation_report.overall_valid = len(validation_report.critical_issues) == 0
        
        # Generate statistical validation
        self._perform_statistical_validation(test_results, validation_report)
        
        # Generate recommendations
        validation_report.recommendations = self._generate_recommendations(validation_report)
        
        self.logger.info(f"Validation completed. Overall quality: {validation_report.overall_quality:.3f}")
        
        return validation_report
    
    def _validate_suite_results(self, suite_results: SuiteResults) -> SuiteValidation:
        """Validate individual test suite results"""
        suite_validation = SuiteValidation(
            suite_name=suite_results.suite_name,
            suite_category=suite_results.suite_category
        )
        
        category_name = suite_results.suite_category.name
        rules = self.validation_rules.get(category_name, [])
        
        for rule in rules:
            self._apply_validation_rule(rule, suite_results, suite_validation)
        
        # Determine overall suite validity
        suite_validation.overall_valid = (
            suite_validation.success_rate_valid and
            suite_validation.performance_valid and
            suite_validation.quality_valid and
            suite_validation.coverage_valid
        )
        
        # Calculate suite quality score
        suite_validation.quality_score = self._calculate_suite_quality_score(
            suite_results, suite_validation
        )
        
        return suite_validation
    
    def _apply_validation_rule(self, rule: ValidationRule, suite_results: SuiteResults, 
                              suite_validation: SuiteValidation):
        """Apply a specific validation rule to suite results"""
        
        # Extract measurement value based on rule name
        measured_value = self._extract_measurement_value(rule.name, suite_results)
        
        if measured_value is None:
            self.logger.warning(f"Could not extract value for rule {rule.name}")
            return
        
        # Perform comparison
        valid = self._compare_value(measured_value, rule.threshold, rule.comparison, rule.threshold_max)
        
        # Update suite validation flags
        if "success_rate" in rule.name:
            suite_validation.success_rate_valid = valid
        elif any(keyword in rule.name for keyword in ["latency", "cpu", "memory", "throughput"]):
            suite_validation.performance_valid = valid
        elif "quality" in rule.name:
            suite_validation.quality_valid = valid
        elif "coverage" in rule.name:
            suite_validation.coverage_valid = valid
        
        # Create validation issue if rule failed
        if not valid:
            severity = "critical" if rule.critical else "warning"
            issue = ValidationIssue(
                rule_name=rule.name,
                severity=severity,
                message=f"{rule.description} (measured: {measured_value:.3f}, threshold: {rule.threshold})",
                measured_value=measured_value,
                threshold_value=rule.threshold,
                test_names=[r.test_name for r in suite_results.test_results if not r.success]
            )
            suite_validation.issues.append(issue)
    
    def _extract_measurement_value(self, rule_name: str, suite_results: SuiteResults) -> Optional[float]:
        """Extract the appropriate measurement value for validation rule"""
        
        if "success_rate" in rule_name:
            return suite_results.success_rate
        elif "execution_time" in rule_name:
            return suite_results.average_execution_time
        elif "coverage" in rule_name:
            return suite_results.total_coverage / 100.0  # Convert percentage to fraction
        elif "latency" in rule_name:
            return suite_results.average_latency_ms
        elif "memory" in rule_name:
            return suite_results.peak_memory_mb
        elif "cpu" in rule_name:
            return suite_results.average_cpu_percent
        elif "quality" in rule_name:
            return suite_results.overall_quality_score
        elif "sync_precision" in rule_name:
            # Calculate average synchronization precision from test results
            sync_values = [
                r.performance_metrics.synchronization_precision_ms 
                for r in suite_results.test_results
                if r.performance_metrics.synchronization_precision_ms > 0
            ]
            return statistics.mean(sync_values) if sync_values else None
        elif "throughput" in rule_name:
            # Calculate average data throughput
            throughput_values = [
                r.performance_metrics.data_throughput_mb_per_sec
                for r in suite_results.test_results
                if r.performance_metrics.data_throughput_mb_per_sec > 0
            ]
            return statistics.mean(throughput_values) if throughput_values else None
        
        return None
    
    def _compare_value(self, measured: float, threshold: float, comparison: str, 
                      threshold_max: Optional[float] = None) -> bool:
        """Compare measured value against threshold using specified comparison"""
        
        if comparison == "gt":
            return measured > threshold
        elif comparison == "gte":
            return measured >= threshold
        elif comparison == "lt":
            return measured < threshold
        elif comparison == "lte":
            return measured <= threshold
        elif comparison == "eq":
            return abs(measured - threshold) < 1e-6
        elif comparison == "range" and threshold_max is not None:
            return threshold <= measured <= threshold_max
        else:
            self.logger.error(f"Unknown comparison operator: {comparison}")
            return False
    
    def _calculate_overall_quality(self, validation_report: ValidationReport) -> float:
        """Calculate overall quality score across all test suites"""
        
        if not validation_report.suite_validations:
            return 0.0
        
        # Weight quality scores by test count in each suite
        total_weight = 0.0
        weighted_sum = 0.0
        
        for suite_validation in validation_report.suite_validations.values():
            # Use suite test count as weight (if available from suite results)
            weight = 1.0  # Default weight
            weighted_sum += weight * suite_validation.quality_score
            total_weight += weight
        
        overall_quality = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Apply penalty for critical issues
        critical_penalty = len(validation_report.critical_issues) * 0.1
        overall_quality = max(0.0, overall_quality - critical_penalty)
        
        return min(1.0, overall_quality)
    
    def _calculate_suite_quality_score(self, suite_results: SuiteResults, 
                                     suite_validation: SuiteValidation) -> float:
        """Calculate quality score for individual test suite"""
        
        # Base score from success rate
        base_score = suite_results.success_rate
        
        # Performance factor
        performance_factor = 1.0
        if suite_results.average_cpu_percent > 0:
            performance_factor *= max(0.5, 1.0 - suite_results.average_cpu_percent / 100.0)
        
        # Coverage factor
        coverage_factor = suite_results.total_coverage / 100.0 if suite_results.total_coverage > 0 else 0.5
        
        # Quality factor from test-specific quality scores
        quality_factor = suite_results.overall_quality_score if suite_results.overall_quality_score > 0 else 0.5
        
        # Calculate weighted score
        quality_score = (
            0.4 * base_score +           # 40% success rate
            0.2 * performance_factor +   # 20% performance
            0.2 * coverage_factor +      # 20% coverage
            0.2 * quality_factor         # 20% test quality
        )
        
        return min(1.0, quality_score)
    
    def _perform_statistical_validation(self, test_results: TestResults, 
                                       validation_report: ValidationReport):
        """Perform statistical validation and confidence analysis"""
        
        # Collect all execution times
        execution_times = []
        for suite in test_results.suite_results.values():
            execution_times.extend([r.execution_time for r in suite.test_results if r.execution_time > 0])
        
        if execution_times:
            validation_report.statistical_summary["mean_execution_time"] = statistics.mean(execution_times)
            validation_report.statistical_summary["median_execution_time"] = statistics.median(execution_times)
            validation_report.statistical_summary["std_execution_time"] = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
            
            # Calculate 95% confidence interval for execution time
            if len(execution_times) > 1:
                mean_time = statistics.mean(execution_times)
                std_time = statistics.stdev(execution_times)
                margin = 1.96 * std_time / (len(execution_times) ** 0.5)  # 95% CI
                validation_report.confidence_intervals["execution_time"] = (
                    max(0, mean_time - margin), mean_time + margin
                )
        
        # Statistical validation for success rates
        success_rates = [suite.success_rate for suite in test_results.suite_results.values()]
        if success_rates:
            validation_report.statistical_summary["mean_success_rate"] = statistics.mean(success_rates)
            validation_report.statistical_summary["min_success_rate"] = min(success_rates)
    
    def _generate_recommendations(self, validation_report: ValidationReport) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Critical issue recommendations
        if validation_report.critical_issues:
            recommendations.append(
                f"CRITICAL: Address {len(validation_report.critical_issues)} critical issues "
                "before system deployment"
            )
        
        # Performance recommendations
        performance_issues = [
            issue for issue in validation_report.quality_issues 
            if any(keyword in issue.rule_name for keyword in ["cpu", "memory", "latency"])
        ]
        if performance_issues:
            recommendations.append(
                "Consider performance optimization for CPU/memory usage and network latency"
            )
        
        # Coverage recommendations
        coverage_issues = [
            issue for issue in validation_report.quality_issues
            if "coverage" in issue.rule_name
        ]
        if coverage_issues:
            recommendations.append(
                "Increase test coverage to meet research-grade quality standards"
            )
        
        # Quality score recommendations
        if validation_report.overall_quality < 0.85:
            recommendations.append(
                f"Overall quality score ({validation_report.overall_quality:.3f}) below target (0.85). "
                "Review test implementations and system performance"
            )
        
        return recommendations