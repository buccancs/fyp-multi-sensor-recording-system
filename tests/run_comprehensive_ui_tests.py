"""
Comprehensive UI/GUI Test Suite Runner
=====================================

Main test runner for comprehensive UI/GUI testing across Android and PC applications.
Integrates all test categories and provides detailed reporting for CI/CD pipelines.

Features:
- Unified test execution across platforms
- Detailed HTML and JSON reporting
- CI/CD integration support
- Test categorization and filtering
- Performance monitoring during tests
- Visual regression testing integration
"""

import pytest
import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "PythonApp"))
sys.path.append(str(project_root))


@dataclass
class TestSuiteConfig:
    """Test suite configuration."""
    test_categories: List[str]
    platforms: List[str]
    output_format: str
    report_dir: str
    run_visual_tests: bool
    run_performance_tests: bool
    parallel_execution: bool
    device_required: bool
    ci_mode: bool
    coverage_enabled: bool
    
    
@dataclass
class TestExecutionResult:
    """Test execution result summary."""
    category: str
    platform: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time: float
    coverage_percent: float
    report_path: str


class UITestSuiteRunner:
    """Main test suite runner."""
    
    def __init__(self, config: TestSuiteConfig):
        self.config = config
        self.results: List[TestExecutionResult] = []
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.config.report_dir, exist_ok=True)
        os.makedirs(os.path.join(self.config.report_dir, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(self.config.report_dir, "coverage"), exist_ok=True)
        
    def run_test_category(self, category: str, platform: str) -> TestExecutionResult:
        """Run tests for specific category and platform."""
        print(f"\n{'='*60}")
        print(f"Running {category} tests for {platform}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Build pytest command
        pytest_args = self._build_pytest_args(category, platform)
        
        # Execute tests
        try:
            result = subprocess.run(
                pytest_args,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            # Parse results
            test_result = self._parse_pytest_output(
                result, category, platform, execution_time
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            test_result = TestExecutionResult(
                category=category,
                platform=platform,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=execution_time,
                coverage_percent=0.0,
                report_path=""
            )
            print(f"⚠️  Tests timed out after {execution_time:.1f}s")
        
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestExecutionResult(
                category=category,
                platform=platform,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=execution_time,
                coverage_percent=0.0,
                report_path=""
            )
            print(f"❌ Test execution failed: {e}")
        
        self.results.append(test_result)
        self._print_result_summary(test_result)
        
        return test_result
    
    def _build_pytest_args(self, category: str, platform: str) -> List[str]:
        """Build pytest command arguments."""
        args = ["python", "-m", "pytest"]
        
        # Test file selection
        test_files = self._get_test_files(category, platform)
        args.extend(test_files)
        
        # Test markers
        markers = self._get_test_markers(category, platform)
        if markers:
            args.extend(["-m", " and ".join(markers)])
        
        # Output format
        if self.config.output_format == "html":
            report_file = os.path.join(
                self.config.report_dir, 
                f"{category}_{platform}_report.html"
            )
            args.extend(["--html", report_file, "--self-contained-html"])
        
        # JSON report
        json_report_file = os.path.join(
            self.config.report_dir,
            f"{category}_{platform}_report.json"
        )
        args.extend(["--json-report", f"--json-report-file={json_report_file}"])
        
        # Coverage
        if self.config.coverage_enabled:
            coverage_file = os.path.join(
                self.config.report_dir, "coverage",
                f"{category}_{platform}_coverage.xml"
            )
            args.extend([
                "--cov=PythonApp",
                "--cov-report=xml:" + coverage_file,
                "--cov-report=term-missing"
            ])
        
        # Parallel execution
        if self.config.parallel_execution and not self.config.ci_mode:
            args.extend(["-n", "auto"])
        
        # Verbosity and formatting
        args.extend(["-v", "--tb=short"])
        
        # CI mode adjustments
        if self.config.ci_mode:
            args.extend(["--maxfail=5", "--disable-warnings"])
        
        # Display setup for GUI tests
        if category in ["gui", "visual"] and platform == "pc":
            # Set display for headless GUI testing
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
        
        return args
    
    def _get_test_files(self, category: str, platform: str) -> List[str]:
        """Get test files for category and platform."""
        test_files = []
        
        if category == "gui" and platform == "android":
            test_files.append("tests/gui/test_android_ui_comprehensive.py")
        elif category == "gui" and platform == "pc":
            test_files.extend([
                "tests/gui/test_pc_gui_comprehensive.py",
                "tests/gui/test_enhanced_main_window.py"
            ])
        elif category == "visual":
            test_files.append("tests/visual/test_visual_regression.py")
        elif category == "e2e" and platform == "android":
            test_files.extend([
                "tests/e2e/test_android_comprehensive.py",
                "tests/e2e/test_appium_android.py"
            ])
        elif category == "integration":
            test_files.append("tests/integration/")
        elif category == "all":
            test_files.extend([
                "tests/gui/",
                "tests/e2e/",
                "tests/visual/"
            ])
        
        # Filter existing files
        existing_files = []
        for file_path in test_files:
            full_path = project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                print(f"⚠️  Test file not found: {file_path}")
        
        return existing_files
    
    def _get_test_markers(self, category: str, platform: str) -> List[str]:
        """Get pytest markers for filtering tests."""
        markers = []
        
        if category == "gui":
            markers.append("gui")
        elif category == "visual":
            markers.append("visual")
        elif category == "e2e":
            markers.append("e2e")
        elif category == "integration":
            markers.append("integration")
        
        if platform == "android":
            markers.append("android")
        elif platform == "pc":
            # Don't add specific PC marker to avoid filtering out tests
            pass
        
        # Exclude hardware tests in CI mode
        if self.config.ci_mode:
            markers.append("not hardware")
        
        return markers
    
    def _parse_pytest_output(self, result: subprocess.CompletedProcess, 
                           category: str, platform: str, execution_time: float) -> TestExecutionResult:
        """Parse pytest output to extract test results."""
        # Default values
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        coverage_percent = 0.0
        
        # Parse from output
        output_lines = result.stdout.split('\n')
        
        for line in output_lines:
            if " passed" in line and " failed" in line:
                # Parse line like: "5 failed, 10 passed, 2 skipped in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        passed_tests = int(parts[i-1])
                    elif part == "failed" and i > 0:
                        failed_tests = int(parts[i-1])
                    elif part == "skipped" and i > 0:
                        skipped_tests = int(parts[i-1])
            elif " passed in " in line:
                # Parse line like: "15 passed in 2.34s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        passed_tests = int(parts[i-1])
            elif "TOTAL" in line and "%" in line:
                # Parse coverage line like: "TOTAL 1234 567 54%"
                parts = line.split()
                for part in parts:
                    if part.endswith("%"):
                        try:
                            coverage_percent = float(part[:-1])
                        except ValueError:
                            pass
        
        total_tests = passed_tests + failed_tests + skipped_tests
        
        # Report path
        report_path = os.path.join(
            self.config.report_dir,
            f"{category}_{platform}_report.html"
        )
        
        return TestExecutionResult(
            category=category,
            platform=platform,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            execution_time=execution_time,
            coverage_percent=coverage_percent,
            report_path=report_path if os.path.exists(report_path) else ""
        )
    
    def _print_result_summary(self, result: TestExecutionResult):
        """Print test result summary."""
        print(f"\n📊 {result.category.upper()} Tests ({result.platform}) Summary:")
        print(f"   Total: {result.total_tests}")
        print(f"   ✅ Passed: {result.passed_tests}")
        print(f"   ❌ Failed: {result.failed_tests}")
        print(f"   ⏭️  Skipped: {result.skipped_tests}")
        print(f"   ⏱️  Time: {result.execution_time:.1f}s")
        if result.coverage_percent > 0:
            print(f"   📈 Coverage: {result.coverage_percent:.1f}%")
        print()
    
    def run_all_tests(self) -> Dict[str, List[TestExecutionResult]]:
        """Run all configured test categories."""
        print("🚀 Starting Comprehensive UI/GUI Test Suite")
        print(f"📋 Categories: {', '.join(self.config.test_categories)}")
        print(f"🖥️  Platforms: {', '.join(self.config.platforms)}")
        print(f"📁 Report Directory: {self.config.report_dir}")
        print()
        
        start_time = time.time()
        
        # Run tests for each category and platform
        for category in self.config.test_categories:
            for platform in self.config.platforms:
                if self._should_run_tests(category, platform):
                    self.run_test_category(category, platform)
                else:
                    print(f"⏭️  Skipping {category} tests for {platform}")
        
        total_time = time.time() - start_time
        
        # Generate final report
        self._generate_final_report(total_time)
        
        # Group results by category
        results_by_category = {}
        for result in self.results:
            if result.category not in results_by_category:
                results_by_category[result.category] = []
            results_by_category[result.category].append(result)
        
        return results_by_category
    
    def _should_run_tests(self, category: str, platform: str) -> bool:
        """Determine if tests should be run for category/platform combination."""
        # Skip device-required tests in CI without devices
        if self.config.ci_mode and not self.config.device_required:
            if category == "e2e" and platform == "android":
                return False
        
        # Skip visual tests if not configured
        if category == "visual" and not self.config.run_visual_tests:
            return False
        
        return True
    
    def _generate_final_report(self, total_time: float):
        """Generate final comprehensive report."""
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE UI/GUI TEST SUITE SUMMARY")
        print(f"{'='*80}")
        
        # Calculate totals
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        total_failed = sum(r.failed_tests for r in self.results)
        total_skipped = sum(r.skipped_tests for r in self.results)
        avg_coverage = sum(r.coverage_percent for r in self.results) / len(self.results) if self.results else 0
        
        print(f"🎯 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)" if total_tests > 0 else "   ✅ Passed: 0")
        print(f"   ❌ Failed: {total_failed} ({total_failed/total_tests*100:.1f}%)" if total_tests > 0 else "   ❌ Failed: 0")
        print(f"   ⏭️  Skipped: {total_skipped}")
        print(f"   ⏱️  Total Time: {total_time:.1f}s")
        if avg_coverage > 0:
            print(f"   📈 Avg Coverage: {avg_coverage:.1f}%")
        print()
        
        # Print category breakdown
        print("📋 Category Breakdown:")
        for result in self.results:
            status = "✅" if result.failed_tests == 0 else "❌"
            print(f"   {status} {result.category.upper()} ({result.platform}): "
                  f"{result.passed_tests}/{result.total_tests} passed")
        print()
        
        # Generate JSON report
        self._generate_json_report(total_time, total_tests, total_passed, total_failed, total_skipped, avg_coverage)
        
        # Overall success determination
        overall_success = total_failed == 0 and total_tests > 0
        if overall_success:
            print("🎉 ALL TESTS PASSED! UI/GUI test suite completed successfully.")
        else:
            print("⚠️  SOME TESTS FAILED. Review failed tests and fix issues.")
        
        print(f"📁 Detailed reports available in: {self.config.report_dir}")
        print()
        
        return overall_success
    
    def _generate_json_report(self, total_time: float, total_tests: int, 
                            total_passed: int, total_failed: int, total_skipped: int, avg_coverage: float):
        """Generate JSON report for CI/CD integration."""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": asdict(self.config),
            "summary": {
                "total_time": total_time,
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "skipped_tests": total_skipped,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "average_coverage": avg_coverage,
                "overall_success": total_failed == 0 and total_tests > 0
            },
            "results": [asdict(result) for result in self.results]
        }
        
        json_report_path = os.path.join(self.config.report_dir, "comprehensive_test_report.json")
        with open(json_report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 JSON report generated: {json_report_path}")


def create_default_config() -> TestSuiteConfig:
    """Create default test configuration."""
    return TestSuiteConfig(
        test_categories=["gui", "visual"],
        platforms=["android", "pc"],
        output_format="html",
        report_dir="/tmp/ui_test_reports",
        run_visual_tests=True,
        run_performance_tests=False,
        parallel_execution=True,
        device_required=False,
        ci_mode=os.getenv('CI', 'false').lower() == 'true',
        coverage_enabled=True
    )


def main():
    """Main entry point for test suite runner."""
    parser = argparse.ArgumentParser(description="Comprehensive UI/GUI Test Suite Runner")
    
    parser.add_argument("--categories", nargs="+", 
                       choices=["gui", "visual", "e2e", "integration", "all"],
                       default=["gui", "visual"],
                       help="Test categories to run")
    
    parser.add_argument("--platforms", nargs="+",
                       choices=["android", "pc", "all"],
                       default=["android", "pc"],
                       help="Platforms to test")
    
    parser.add_argument("--output-format", choices=["html", "json"],
                       default="html",
                       help="Output report format")
    
    parser.add_argument("--report-dir", default="/tmp/ui_test_reports",
                       help="Directory for test reports")
    
    parser.add_argument("--no-visual", action="store_true",
                       help="Skip visual regression tests")
    
    parser.add_argument("--no-parallel", action="store_true",
                       help="Disable parallel test execution")
    
    parser.add_argument("--ci-mode", action="store_true",
                       help="Run in CI mode (fewer resources, no real devices)")
    
    parser.add_argument("--with-coverage", action="store_true",
                       help="Enable code coverage reporting")
    
    args = parser.parse_args()
    
    # Expand "all" options
    if "all" in args.categories:
        args.categories = ["gui", "visual", "e2e", "integration"]
    if "all" in args.platforms:
        args.platforms = ["android", "pc"]
    
    # Create configuration
    config = TestSuiteConfig(
        test_categories=args.categories,
        platforms=args.platforms,
        output_format=args.output_format,
        report_dir=args.report_dir,
        run_visual_tests=not args.no_visual,
        run_performance_tests=False,
        parallel_execution=not args.no_parallel,
        device_required=False,
        ci_mode=args.ci_mode or os.getenv('CI', 'false').lower() == 'true',
        coverage_enabled=args.with_coverage
    )
    
    # Run test suite
    runner = UITestSuiteRunner(config)
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    overall_success = all(
        all(result.failed_tests == 0 for result in category_results)
        for category_results in results.values()
    )
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())