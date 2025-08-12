"""
Quality Validator for Unified Testing Framework

Provides research-grade quality validation and assessment capabilities
for the Multi-Sensor Recording System test results.
"""

import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QualityThresholds:
    """Quality thresholds for different test categories"""
    minimum_success_rate: float = 0.95
    maximum_execution_time: float = 300.0
    minimum_coverage: float = 0.80
    sync_precision_ms: float = 1.0
    data_quality_score: float = 0.8
    measurement_accuracy: float = 0.95

@dataclass 
class QualityAssessment:
    """Quality assessment results"""
    overall_score: float
    success_rate: float
    performance_score: float
    coverage_score: float
    research_readiness: str
    recommendations: List[str]
    detailed_metrics: Dict[str, Any]

class QualityValidator:
    """
    Validates test results against research-grade quality standards
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = self._load_thresholds()
    
    def _load_thresholds(self) -> Dict[str, QualityThresholds]:
        """Load quality thresholds from configuration"""
        thresholds = {}
        
        quality_config = self.config.get("quality_thresholds", {})
        
        for test_type, threshold_config in quality_config.items():
            thresholds[test_type] = QualityThresholds(
                minimum_success_rate=threshold_config.get("minimum_success_rate", 0.95),
                maximum_execution_time=threshold_config.get("maximum_execution_time", 300.0),
                minimum_coverage=threshold_config.get("minimum_coverage", 0.80),
                sync_precision_ms=threshold_config.get("sync_precision_ms", 1.0),
                data_quality_score=threshold_config.get("data_quality_score", 0.8),
                measurement_accuracy=threshold_config.get("measurement_accuracy", 0.95)
            )
        
        return thresholds
    
    def validate_results(self, test_results: Dict[str, Any]) -> QualityAssessment:
        """
        Validate test results against quality standards
        
        Args:
            test_results: Dictionary containing test execution results
            
        Returns:
            QualityAssessment with overall quality evaluation
        """
        
        # Calculate success rate
        success_rate = self._calculate_success_rate(test_results)
        
        # Calculate performance metrics
        performance_score = self._calculate_performance_score(test_results)
        
        # Calculate coverage metrics (placeholder - would integrate with actual coverage data)
        coverage_score = self._calculate_coverage_score(test_results)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(success_rate, performance_score, coverage_score)
        
        # Determine research readiness
        research_readiness = self._assess_research_readiness(overall_score, success_rate)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(test_results, success_rate, performance_score, coverage_score)
        
        # Collect detailed metrics
        detailed_metrics = self._collect_detailed_metrics(test_results, success_rate, performance_score, coverage_score)
        
        return QualityAssessment(
            overall_score=overall_score,
            success_rate=success_rate,
            performance_score=performance_score,
            coverage_score=coverage_score,
            research_readiness=research_readiness,
            recommendations=recommendations,
            detailed_metrics=detailed_metrics
        )
    
    def _calculate_success_rate(self, test_results: Dict[str, Any]) -> float:
        """Calculate overall test success rate"""
        if not test_results:
            return 0.0
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get("return_code") == 0)
        
        return passed_tests / total_tests if total_tests > 0 else 0.0
    
    def _calculate_performance_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate performance score based on execution times"""
        if not test_results:
            return 0.0
        
        execution_times = [result.get("execution_time", 0) for result in test_results.values()]
        
        if not execution_times:
            return 0.0
        
        # Calculate score based on execution time efficiency
        # Score decreases as execution time increases beyond expected thresholds
        avg_time = statistics.mean(execution_times)
        max_reasonable_time = 300.0  # 5 minutes as baseline
        
        if avg_time <= max_reasonable_time:
            return 1.0
        else:
            # Exponential decay for longer execution times
            return max(0.0, 1.0 - (avg_time - max_reasonable_time) / max_reasonable_time)
    
    def _calculate_coverage_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate coverage score (placeholder implementation)"""
        # In a real implementation, this would parse coverage reports
        # For now, return a baseline score
        return 0.75
    
    def _calculate_overall_score(self, success_rate: float, performance_score: float, coverage_score: float) -> float:
        """Calculate weighted overall quality score"""
        # Weighted average with success rate being most important
        weights = {
            "success": 0.5,
            "performance": 0.3, 
            "coverage": 0.2
        }
        
        overall_score = (
            success_rate * weights["success"] +
            performance_score * weights["performance"] +
            coverage_score * weights["coverage"]
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _assess_research_readiness(self, overall_score: float, success_rate: float) -> str:
        """Assess if system is ready for research use"""
        if overall_score >= 0.90 and success_rate >= 0.95:
            return "Research Ready"
        elif overall_score >= 0.75 and success_rate >= 0.85:
            return "Needs Minor Improvements"
        elif overall_score >= 0.60 and success_rate >= 0.70:
            return "Needs Major Improvements"
        else:
            return "Not Ready for Research"
    
    def _generate_recommendations(self, test_results: Dict[str, Any], success_rate: float, 
                                performance_score: float, coverage_score: float) -> List[str]:
        """Generate actionable recommendations for improvement"""
        recommendations = []
        
        # Success rate recommendations
        if success_rate < 0.95:
            failed_tests = [name for name, result in test_results.items() 
                          if result.get("return_code") != 0]
            recommendations.append(f"Address failing tests: {', '.join(failed_tests)}")
        
        # Performance recommendations
        if performance_score < 0.8:
            slow_tests = [name for name, result in test_results.items() 
                         if result.get("execution_time", 0) > 300]
            if slow_tests:
                recommendations.append(f"Optimize slow tests: {', '.join(slow_tests)}")
        
        # Coverage recommendations
        if coverage_score < 0.8:
            recommendations.append("Increase test coverage to meet research standards")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Test suite meets quality standards - continue monitoring")
        
        return recommendations
    
    def _collect_detailed_metrics(self, test_results: Dict[str, Any], success_rate: float,
                                performance_score: float, coverage_score: float) -> Dict[str, Any]:
        """Collect detailed quality metrics"""
        
        execution_times = [result.get("execution_time", 0) for result in test_results.values()]
        
        metrics = {
            "test_execution": {
                "total_test_suites": len(test_results),
                "passed_suites": sum(1 for r in test_results.values() if r.get("return_code") == 0),
                "failed_suites": sum(1 for r in test_results.values() if r.get("return_code") != 0),
                "success_rate_percent": success_rate * 100
            },
            "performance": {
                "avg_execution_time": statistics.mean(execution_times) if execution_times else 0,
                "max_execution_time": max(execution_times) if execution_times else 0,
                "min_execution_time": min(execution_times) if execution_times else 0,
                "performance_score": performance_score
            },
            "coverage": {
                "coverage_score": coverage_score,
                "estimated_coverage_percent": coverage_score * 100
            },
            "quality_assessment": {
                "timestamp": datetime.now().isoformat(),
                "overall_score": success_rate * 0.5 + performance_score * 0.3 + coverage_score * 0.2,
                "research_readiness_score": self._calculate_research_readiness_score(success_rate, performance_score)
            }
        }
        
        return metrics
    
    def _calculate_research_readiness_score(self, success_rate: float, performance_score: float) -> float:
        """Calculate specific research readiness score"""
        # Research requires high reliability and reasonable performance
        return min(1.0, success_rate * 0.7 + performance_score * 0.3)
    
    def generate_quality_report(self, assessment: QualityAssessment) -> str:
        """Generate human-readable quality report"""
        
        status_emoji = {
            "Research Ready": "✅",
            "Needs Minor Improvements": "⚠️", 
            "Needs Major Improvements": "⚠️",
            "Not Ready for Research": "❌"
        }
        
        emoji = status_emoji.get(assessment.research_readiness, "❓")
        
        report = f"""
# Quality Validation Report

## Overall Assessment
{emoji} **{assessment.research_readiness}**

**Overall Score:** {assessment.overall_score:.2f}/1.00 ({assessment.overall_score*100:.1f}%)

## Key Metrics
- **Success Rate:** {assessment.success_rate:.2f} ({assessment.success_rate*100:.1f}%)
- **Performance Score:** {assessment.performance_score:.2f} ({assessment.performance_score*100:.1f}%)
- **Coverage Score:** {assessment.coverage_score:.2f} ({assessment.coverage_score*100:.1f}%)

## Recommendations
"""
        
        for i, recommendation in enumerate(assessment.recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
## Detailed Metrics
```json
{json.dumps(assessment.detailed_metrics, indent=2)}
```
"""
        
        return report