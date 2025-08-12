#!/usr/bin/env python3
"""
Unified Test Runner for Multi-Sensor Recording System

This script consolidates and replaces multiple test execution scripts,
providing a single entry point for all testing needs across the system.

Consolidates functionality from:
- run_advanced_tests.sh
- run_local_test.sh  
- evaluation_suite test runners
- Individual test scripts

Usage:
    python run_unified_tests.py [options]
    
Examples:
    # Run all tests
    python run_unified_tests.py
    
    # Run specific test level
    python run_unified_tests.py --level unit
    python run_unified_tests.py --level integration
    python run_unified_tests.py --level system
    python run_unified_tests.py --level performance
    
    # Run specific categories
    python run_unified_tests.py --category android
    python run_unified_tests.py --category evaluation
    
    # Run in specific mode
    python run_unified_tests.py --mode ci
    python run_unified_tests.py --mode research
    python run_unified_tests.py --mode development
    
    # Quick validation
    python run_unified_tests.py --quick
    
    # Parallel execution
    python run_unified_tests.py --parallel
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import unified test framework components
try:
    from tests_unified.fixtures.test_utils import setup_test_environment, cleanup_test_environment
    from tests_unified.evaluation.metrics.quality_validator import QualityValidator
    from tests_unified.evaluation.metrics.performance_monitor import PerformanceMonitor
except ImportError:
    # Fallback for initial setup when modules don't exist yet
    pass

@dataclass
class TestConfiguration:
    """Test execution configuration"""
    level: Optional[str] = None
    category: Optional[str] = None
    mode: str = "development"
    quick: bool = False
    parallel: bool = False
    verbose: bool = False
    headless: bool = True
    timeout: Optional[int] = None
    output_dir: str = "test_results"
    config_file: Optional[str] = None

class UnifiedTestRunner:
    """
    Unified test execution framework that consolidates all testing capabilities
    into a single, coherent interface.
    """
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.project_root = PROJECT_ROOT
        self.test_root = self.project_root / "tests_unified"
        self.config_dir = self.test_root / "config"
        self.results_dir = Path(config.output_dir)
        
        # Load configuration
        self.test_config = self._load_test_config()
        self.quality_validator = None
        self.performance_monitor = None
        
        # Setup logging
        self._setup_logging()
        
        # Test results tracking
        self.test_results = {}
        self.overall_success = True
        
    def _load_test_config(self) -> Dict:
        """Load test configuration from YAML file"""
        config_file = self.config.config_file or (self.config_dir / "test_config.yaml")
        
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration when config file is not available"""
        return {
            "quality_thresholds": {
                "unit_tests": {"minimum_success_rate": 0.95},
                "integration_tests": {"minimum_success_rate": 0.90},
                "system_tests": {"minimum_success_rate": 0.95},
                "performance_tests": {"minimum_success_rate": 0.85}
            },
            "test_execution": {
                "timeouts": {"unit": 60, "integration": 180, "system": 600, "performance": 1800},
                "parallel": {"enabled": True, "max_workers": 4}
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.config.verbose else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.results_dir / "test_execution.log")
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run(self) -> bool:
        """Main execution method"""
        self.logger.info("Starting Unified Test Runner")
        self.logger.info(f"Configuration: {self.config}")
        
        try:
            # Setup test environment
            self._setup_environment()
            
            # Initialize monitoring and validation
            self._initialize_monitoring()
            
            # Execute tests based on configuration
            success = self._execute_tests()
            
            # Generate reports
            self._generate_reports()
            
            # Cleanup
            self._cleanup_environment()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return False
    
    def _setup_environment(self):
        """Setup test execution environment"""
        self.logger.info("Setting up test environment")
        
        # Create output directories
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "logs").mkdir(exist_ok=True)
        (self.results_dir / "artifacts").mkdir(exist_ok=True)
        
        # Set environment variables
        os.environ["GSR_TEST_MODE"] = self.config.mode
        os.environ["GSR_TEST_VERBOSE"] = str(self.config.verbose)
        os.environ["GSR_TEST_HEADLESS"] = str(self.config.headless)
        os.environ["GSR_TEST_RESULTS_DIR"] = str(self.results_dir)
        
        if self.config.quick:
            os.environ["GSR_TEST_QUICK_MODE"] = "true"
    
    def _initialize_monitoring(self):
        """Initialize quality validation and performance monitoring"""
        try:
            self.quality_validator = QualityValidator(self.test_config)
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.start_monitoring()
        except Exception as e:
            self.logger.warning(f"Could not initialize monitoring: {e}")
    
    def _execute_tests(self) -> bool:
        """Execute tests based on configuration"""
        
        if self.config.level:
            return self._run_test_level(self.config.level)
        elif self.config.category:
            return self._run_test_category(self.config.category)
        else:
            return self._run_all_tests()
    
    def _run_test_level(self, level: str) -> bool:
        """Run tests for a specific level (unit, integration, system, performance)"""
        self.logger.info(f"Running {level} tests")
        
        test_dir = self.test_root / level
        if not test_dir.exists():
            self.logger.error(f"Test directory not found: {test_dir}")
            return False
        
        return self._run_pytest(test_dir, markers=level)
    
    def _run_test_category(self, category: str) -> bool:
        """Run tests for a specific category (android, browser, visual, etc.)"""
        self.logger.info(f"Running {category} tests")
        
        # Map categories to directories
        category_mapping = {
            "android": ["unit/android", "integration", "system"],
            "browser": ["browser"],
            "visual": ["visual"],
            "hardware": ["hardware"],
            "evaluation": ["evaluation"],
            "performance": ["performance"]
        }
        
        if category not in category_mapping:
            self.logger.error(f"Unknown category: {category}")
            return False
        
        success = True
        for subdir in category_mapping[category]:
            test_dir = self.test_root / subdir
            if test_dir.exists():
                if not self._run_pytest(test_dir, markers=category):
                    success = False
        
        return success
    
    def _run_all_tests(self) -> bool:
        """Run all test levels in sequence"""
        self.logger.info("Running all tests")
        
        test_levels = ["unit", "integration", "system"]
        
        # Add performance tests if not in quick mode
        if not self.config.quick:
            test_levels.append("performance")
        
        success = True
        for level in test_levels:
            if not self._run_test_level(level):
                success = False
                if level in ["unit", "integration"]:  # Critical levels
                    self.logger.error(f"Critical test level {level} failed, stopping execution")
                    break
        
        return success
    
    def _run_pytest(self, test_dir: Path, markers: Optional[str] = None) -> bool:
        """Run pytest on a specific directory"""
        
        cmd = ["python", "-m", "pytest", str(test_dir)]
        
        # Add markers if specified
        if markers:
            cmd.extend(["-m", markers])
        
        # Add configuration
        cmd.extend([
            "--tb=short",
            "-v",
            f"--junitxml={self.results_dir}/junit-{test_dir.name}.xml",
            f"--cov=PythonApp",
            f"--cov-report=xml:{self.results_dir}/coverage-{test_dir.name}.xml"
        ])
        
        # Add timeout (only if pytest-timeout is available)
        timeout = self._get_timeout_for_level(test_dir.name)
        try:
            import pytest_timeout
            cmd.extend([f"--timeout={timeout}"])
        except ImportError:
            self.logger.warning("pytest-timeout not available, skipping timeout setting")
        
        # Add parallel execution if enabled
        if self.config.parallel and self._is_parallel_safe(test_dir.name):
            cmd.extend(["-n", "auto"])
        
        # Add verbose output if requested
        if self.config.verbose:
            cmd.extend(["-s"])
        
        self.logger.info(f"Executing: {' '.join(cmd)}")
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            execution_time = time.time() - start_time
            
            # Store results
            self.test_results[test_dir.name] = {
                "return_code": result.returncode,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                self.logger.info(f"✅ {test_dir.name} tests passed ({execution_time:.2f}s)")
                return True
            else:
                self.logger.error(f"❌ {test_dir.name} tests failed ({execution_time:.2f}s)")
                self.logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ {test_dir.name} tests timed out after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"❌ {test_dir.name} tests failed with exception: {e}")
            return False
    
    def _get_timeout_for_level(self, level: str) -> int:
        """Get timeout for specific test level"""
        if self.config.timeout:
            return self.config.timeout
        
        timeouts = self.test_config.get("test_execution", {}).get("timeouts", {})
        default_timeout = 300
        
        if self.config.quick:
            return timeouts.get("quick_mode", 120)
        
        return timeouts.get(level, default_timeout)
    
    def _is_parallel_safe(self, level: str) -> bool:
        """Check if test level is safe for parallel execution"""
        parallel_config = self.test_config.get("test_execution", {}).get("parallel", {})
        safe_levels = parallel_config.get("safe_for_parallel", ["unit", "integration"])
        return level in safe_levels
    
    def _generate_reports(self):
        """Generate comprehensive test reports"""
        self.logger.info("Generating test reports")
        
        # Generate summary report
        summary = self._generate_summary()
        
        # Save JSON report
        with open(self.results_dir / "test_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Generate markdown report
        self._generate_markdown_report(summary)
        
        # Quality validation if available
        if self.quality_validator:
            quality_report = self.quality_validator.validate_results(self.test_results)
            with open(self.results_dir / "quality_validation.json", "w") as f:
                json.dump(quality_report, f, indent=2, default=str)
    
    def _generate_summary(self) -> Dict:
        """Generate test execution summary"""
        total_tests = 0
        total_passed = 0
        total_time = 0
        
        for level, result in self.test_results.items():
            if result["return_code"] == 0:
                total_passed += 1
            total_tests += 1
            total_time += result["execution_time"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "level": self.config.level,
                "category": self.config.category,
                "mode": self.config.mode,
                "quick": self.config.quick,
                "parallel": self.config.parallel
            },
            "summary": {
                "total_test_levels": total_tests,
                "passed_levels": total_passed,
                "failed_levels": total_tests - total_passed,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "total_execution_time": total_time
            },
            "results": self.test_results
        }
    
    def _generate_markdown_report(self, summary: Dict):
        """Generate human-readable markdown report"""
        
        report = f"""# Unified Test Execution Report

**Generated:** {summary['timestamp']}
**Configuration:** {summary['configuration']}

## Summary

- **Test Levels Executed:** {summary['summary']['total_test_levels']}
- **Passed:** {summary['summary']['passed_levels']}
- **Failed:** {summary['summary']['failed_levels']}
- **Success Rate:** {summary['summary']['success_rate']:.1f}%
- **Total Execution Time:** {summary['summary']['total_execution_time']:.2f}s

## Test Level Results

"""
        
        for level, result in summary['results'].items():
            status = "✅ PASSED" if result['return_code'] == 0 else "❌ FAILED"
            report += f"""### {status} {level.title()}
- **Execution Time:** {result['execution_time']:.2f}s
- **Return Code:** {result['return_code']}

"""
        
        with open(self.results_dir / "test_summary.md", "w") as f:
            f.write(report)
    
    def _cleanup_environment(self):
        """Cleanup test environment"""
        self.logger.info("Cleaning up test environment")
        
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()
        
        # Cleanup any temporary files or processes
        try:
            cleanup_test_environment()
        except Exception as e:
            self.logger.warning(f"Cleanup warning: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Test Runner for Multi-Sensor Recording System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test selection
    parser.add_argument("--level", choices=["unit", "integration", "system", "performance"],
                       help="Run specific test level")
    parser.add_argument("--category", choices=["android", "browser", "visual", "hardware", "evaluation"],
                       help="Run specific test category")
    
    # Execution mode
    parser.add_argument("--mode", choices=["development", "ci", "research", "production"],
                       default="development", help="Test execution mode")
    
    # Execution options
    parser.add_argument("--quick", action="store_true", help="Run quick validation tests")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel test execution")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--headed", action="store_true", help="Run with GUI (not headless)")
    
    # Configuration
    parser.add_argument("--timeout", type=int, help="Test timeout in seconds")
    parser.add_argument("--output-dir", default="test_results", help="Output directory for results")
    parser.add_argument("--config-file", help="Test configuration file")
    
    args = parser.parse_args()
    
    # Create configuration
    config = TestConfiguration(
        level=args.level,
        category=args.category,
        mode=args.mode,
        quick=args.quick,
        parallel=args.parallel,
        verbose=args.verbose,
        headless=not args.headed,
        timeout=args.timeout,
        output_dir=args.output_dir,
        config_file=args.config_file
    )
    
    # Create and run test runner
    runner = UnifiedTestRunner(config)
    success = runner.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()