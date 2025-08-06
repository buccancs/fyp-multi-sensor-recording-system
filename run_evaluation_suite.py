
"""
Comprehensive Evaluation Suite Runner

This script runs the complete evaluation suite implementing the testing strategy
outlined in Chapter 5 of the thesis documentation.

Usage:
    python run_evaluation_suite.py [options]
    
Options:
    --category CATEGORY    Run specific test category (foundation, integration, system, performance)
    --parallel            Enable parallel test execution where possible
    --output-dir DIR      Directory for test reports and artifacts
    --config-file FILE    Configuration file for test parameters
    --verbose            Enable verbose logging
    --quick              Run quick validation tests only
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

from evaluation_suite.framework.test_framework import TestFramework
from evaluation_suite.framework.test_categories import TestCategory, TestConfiguration, QualityThresholds
from evaluation_suite.framework.quality_validator import QualityValidator

from evaluation_suite.foundation.android_tests import create_android_foundation_suite
from evaluation_suite.foundation.pc_tests import create_pc_foundation_suite
from evaluation_suite.integration.integration_tests import create_real_integration_suite

class EvaluationSuiteRunner:
    """Main evaluation suite runner"""
    
    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._setup_logging()

        quality_thresholds = self._load_quality_thresholds()
        self.test_framework = TestFramework(quality_thresholds)

        config = TestConfiguration(
            parallel_execution=args.parallel,
            generate_reports=True,
            collect_metrics=True,
            timeout_seconds=600 if args.quick else 1800
        )
        self.test_framework.configure(config)
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.args.verbose else logging.INFO

        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        log_file = self.output_dir / f"evaluation_suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        print(f"Logging to: {log_file}")
    
    def _load_quality_thresholds(self) -> QualityThresholds:
        """Load quality thresholds from configuration"""
        if self.args.config_file and Path(self.args.config_file).exists():
            try:
                with open(self.args.config_file, 'r') as f:
                    config_data = json.load(f)

                thresholds_data = config_data.get('quality_thresholds', {})
                return QualityThresholds(**thresholds_data)
                
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}. Using defaults.")

        thresholds = QualityThresholds()
        if self.args.quick:

            thresholds.minimum_success_rate = 0.90
            thresholds.maximum_execution_time = 600.0
            thresholds.minimum_coverage = 0.70
        
        return thresholds
    
    def _register_test_suites(self):
        """Register all test suites with the framework"""
        self.logger.info("Registering test suites...")

        if not self.args.category or self.args.category == 'foundation':
            android_suite = create_android_foundation_suite()
            self.test_framework.register_test_suite("android_foundation", android_suite)
            
            pc_suite = create_pc_foundation_suite()
            self.test_framework.register_test_suite("pc_foundation", pc_suite)

        if not self.args.category or self.args.category == 'integration':
            integration_suite = create_real_integration_suite()
            self.test_framework.register_test_suite("integration_tests", integration_suite)

        if not self.args.category or self.args.category == 'system':
            self.logger.info("System test suites not yet implemented")

        if not self.args.category or self.args.category == 'performance':
            self.logger.info("Performance test suites not yet implemented")
    
    async def run_evaluation(self):
        """Run the complete evaluation suite"""
        self.logger.info("="*60)
        self.logger.info("Multi-Sensor Recording System - Comprehensive Evaluation Suite")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        
        try:

            self._register_test_suites()

            if self.args.category:
                category = TestCategory[self.args.category.upper()]
                self.logger.info(f"Running {category.name} test category")
                results = await self.test_framework.run_test_category(category)
            else:
                self.logger.info("Running complete evaluation suite")
                results = await self.test_framework.run_all_tests()

            await self._generate_final_report(results, start_time)

            self._display_summary(results)
            
            return results
            
        except KeyboardInterrupt:
            self.logger.warning("Evaluation interrupted by user")
            return None
        except Exception as e:
            self.logger.error(f"Evaluation failed with error: {e}")
            raise
    
    async def _generate_final_report(self, results, start_time):
        """Generate comprehensive final report"""
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        self.logger.info("Generating comprehensive evaluation report...")

        report_data = {
            "evaluation_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_seconds": total_duration,
                "test_configuration": {
                    "category_filter": self.args.category,
                    "parallel_execution": self.args.parallel,
                    "quick_mode": self.args.quick,
                    "output_directory": str(self.output_dir)
                }
            },
            "test_results": results.get_summary_report() if results else {},
            "quality_assessment": self._assess_overall_quality(results),
            "recommendations": self._generate_recommendations(results)
        }

        report_file = self.output_dir / "comprehensive_evaluation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        summary_file = self.output_dir / "evaluation_summary.md"
        await self._generate_markdown_summary(report_data, summary_file)
        
        self.logger.info(f"Reports saved to: {self.output_dir}")
        self.logger.info(f"  - Detailed report: {report_file}")
        self.logger.info(f"  - Summary report: {summary_file}")
    
    def _assess_overall_quality(self, results):
        """Assess overall system quality based on test results"""
        if not results:
            return {"overall_quality": 0.0, "assessment": "No results available"}

        success_rate = results.overall_success_rate
        quality_score = results.overall_quality_score
        coverage = results.overall_coverage

        if success_rate > 0.95 and quality_score > 0.90:
            quality_level = "Excellent"
        elif success_rate > 0.90 and quality_score > 0.80:
            quality_level = "Good"
        elif success_rate > 0.80 and quality_score > 0.70:
            quality_level = "Acceptable"
        else:
            quality_level = "Needs Improvement"
        
        return {
            "overall_quality": quality_score,
            "success_rate": success_rate,
            "coverage_percentage": coverage,
            "quality_level": quality_level,
            "research_ready": success_rate > 0.95 and quality_score > 0.85
        }
    
    def _generate_recommendations(self, results):
        """Generate actionable recommendations based on results"""
        if not results:
            return ["Complete evaluation suite execution to generate recommendations"]
        
        recommendations = []

        if results.overall_success_rate < 0.95:
            recommendations.append(
                f"Improve test success rate (current: {results.overall_success_rate:.1%}, target: >95%)"
            )

        if results.overall_quality_score < 0.85:
            recommendations.append(
                f"Enhance system quality (current: {results.overall_quality_score:.3f}, target: >0.85)"
            )

        if results.overall_coverage < 80.0:
            recommendations.append(
                f"Increase test coverage (current: {results.overall_coverage:.1f}%, target: >80%)"
            )

        for suite_name, suite_results in results.suite_results.items():
            if suite_results.success_rate < 0.90:
                recommendations.append(
                    f"Address failures in {suite_name} suite "
                    f"(success rate: {suite_results.success_rate:.1%})"
                )
        
        if not recommendations:
            recommendations.append("System meets all quality targets - ready for research deployment")
        
        return recommendations
    
    async def _generate_markdown_summary(self, report_data, output_file):
        """Generate human-readable markdown summary"""
        content = [
            "# Multi-Sensor Recording System - Evaluation Summary\n",
            f"**Generated:** {datetime.now().isoformat()}\n",
            f"**Duration:** {report_data['evaluation_summary']['total_duration_seconds']:.1f} seconds\n"
        ]

        if 'test_results' in report_data and report_data['test_results']:
            results = report_data['test_results']['statistics']
            content.extend([
                "\n## Test Execution Summary\n",
                f"- **Total Suites:** {results['total_suites']}",
                f"- **Total Tests:** {results['total_tests']}",
                f"- **Success Rate:** {results['success_rate']}%",
                f"- **Quality Score:** {results['quality_score']}",
                f"- **Coverage:** {results['coverage_percentage']}%\n"
            ])

        if 'quality_assessment' in report_data:
            quality = report_data['quality_assessment']
            content.extend([
                "\n## Quality Assessment\n",
                f"- **Quality Level:** {quality.get('quality_level', 'Unknown')}",
                f"- **Research Ready:** {'Yes' if quality.get('research_ready', False) else 'No'}",
                f"- **Overall Quality Score:** {quality.get('overall_quality', 0):.3f}\n"
            ])

        if 'recommendations' in report_data:
            content.append("\n## Recommendations\n")
            for i, rec in enumerate(report_data['recommendations'], 1):
                content.append(f"{i}. {rec}")

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))
    
    def _display_summary(self, results):
        """Display execution summary to console"""
        print("\n" + "="*60)
        print("EVALUATION SUITE EXECUTION SUMMARY")
        print("="*60)
        
        if not results:
            print("No results available")
            return
        
        print(f"Total Suites: {results.total_suites}")
        print(f"Total Tests: {results.total_tests}")
        print(f"Success Rate: {results.overall_success_rate:.1%}")
        print(f"Quality Score: {results.overall_quality_score:.3f}")
        print(f"Coverage: {results.overall_coverage:.1f}%")
        print(f"Execution Time: {results.total_execution_time:.1f} seconds")

        print("\nSuite Results:")
        for suite_name, suite_results in results.suite_results.items():
            status = "✓" if suite_results.success_rate > 0.90 else "✗"
            print(f"  {status} {suite_name}: {suite_results.success_rate:.1%} "
                  f"({suite_results.passed_tests}/{suite_results.total_tests})")
        
        print("="*60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run the Multi-Sensor Recording System Evaluation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--category',
        choices=['foundation', 'integration', 'system', 'performance'],
        help='Run specific test category only'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel test execution where possible'
    )
    
    parser.add_argument(
        '--output-dir',
        default='evaluation_results',
        help='Directory for test reports and artifacts (default: evaluation_results)'
    )
    
    parser.add_argument(
        '--config-file',
        help='Configuration file for test parameters'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick validation tests only'
    )
    
    args = parser.parse_args()

    runner = EvaluationSuiteRunner(args)
    
    try:

        results = asyncio.run(runner.run_evaluation())

        if results and results.overall_success_rate > 0.90:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nEvaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()