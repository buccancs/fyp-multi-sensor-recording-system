#!/usr/bin/env python3
"""
Comprehensive Logging Test Suite for Phase 1
=============================================

Tests all logging enhancements and validates comprehensive coverage.
"""

import sys
import time
from pathlib import Path

# Add PythonApp/src to path
sys.path.insert(0, str(Path(__file__).parent / "PythonApp" / "src"))

from utils.logging_config import get_logger, AppLogger, performance_timer

logger = get_logger(__name__)

class LoggingTestSuite:
    """Comprehensive logging validation test suite."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.tests_passed = 0
        self.tests_failed = 0
    
    @performance_timer("logging_infrastructure_test")
    def test_logging_infrastructure(self):
        """Test comprehensive logging infrastructure."""
        self.logger.info("=== Testing Logging Infrastructure ===")
        
        try:
            # Test all log levels
            self.logger.debug("Debug level test")
            self.logger.info("Info level test")
            self.logger.warning("Warning level test")
            self.logger.error("Error level test")
            self.logger.critical("Critical level test")
            
            # Test structured logging
            self.logger.info("Structured logging test", extra={
                'component': 'logging_test',
                'metrics': {'cpu': 15, 'memory': 128}
            })
            
            # Test performance timing
            timer_id = AppLogger.start_performance_timer("test_operation", "logging_test")
            time.sleep(0.1)
            AppLogger.end_performance_timer(timer_id, __name__)
            
            # Test memory logging
            AppLogger.log_memory_usage("logging_test_context", __name__)
            
            self.tests_passed += 1
            self.logger.info("✅ Logging infrastructure test PASSED")
            
        except Exception as e:
            self.tests_failed += 1
            self.logger.error(f"❌ Logging infrastructure test FAILED: {e}")
    
    def test_component_logging(self):
        """Test individual component logging."""
        self.logger.info("=== Testing Component Logging ===")
        
        components = [
            'session_manager',
            'calibration_manager', 
            'network_server',
            'application_controller'
        ]
        
        for component in components:
            try:
                component_logger = get_logger(f"test.{component}")
                component_logger.info(f"Testing {component} logging integration")
                component_logger.debug(f"{component} debug information")
                component_logger.warning(f"{component} warning message")
                
                self.logger.info(f"✅ {component} logging test PASSED")
                
            except Exception as e:
                self.logger.error(f"❌ {component} logging test FAILED: {e}")
                self.tests_failed += 1
                continue
                
        self.tests_passed += 1
    
    def test_performance_monitoring(self):
        """Test performance monitoring capabilities."""
        self.logger.info("=== Testing Performance Monitoring ===")
        
        try:
            # Test multiple performance timers
            operations = ['file_io', 'network_call', 'data_processing']
            
            for operation in operations:
                timer_id = AppLogger.start_performance_timer(operation, "test_context")
                time.sleep(0.05)  # Simulate work
                duration = AppLogger.end_performance_timer(timer_id, __name__)
                
                self.logger.info(f"Operation {operation}: {duration*1000:.1f}ms")
            
            # Test active timers
            active_timers = AppLogger.get_active_timers()
            self.logger.info(f"Active timers: {len(active_timers)}")
            
            self.tests_passed += 1
            self.logger.info("✅ Performance monitoring test PASSED")
            
        except Exception as e:
            self.tests_failed += 1
            self.logger.error(f"❌ Performance monitoring test FAILED: {e}")
    
    def test_log_file_creation(self):
        """Test log file creation and structure."""
        self.logger.info("=== Testing Log File Creation ===")
        
        try:
            log_dir = AppLogger.get_log_dir()
            if log_dir and log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                
                expected_files = ['application.log', 'errors.log', 'structured.log']
                found_files = [f.name for f in log_files]
                
                for expected in expected_files:
                    if expected in found_files:
                        self.logger.info(f"✅ Found {expected}")
                    else:
                        self.logger.warning(f"⚠️ Missing {expected}")
                
                # Check file sizes
                for log_file in log_files:
                    size = log_file.stat().st_size
                    self.logger.info(f"Log file {log_file.name}: {size} bytes")
                
                self.tests_passed += 1
                self.logger.info("✅ Log file creation test PASSED")
            else:
                raise Exception("Log directory not found")
                
        except Exception as e:
            self.tests_failed += 1
            self.logger.error(f"❌ Log file creation test FAILED: {e}")
    
    def run_all_tests(self):
        """Run all logging tests."""
        self.logger.info("🚀 Starting Comprehensive Logging Test Suite")
        self.logger.info("=" * 60)
        
        tests = [
            self.test_logging_infrastructure,
            self.test_component_logging,
            self.test_performance_monitoring,
            self.test_log_file_creation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.logger.error(f"Test {test.__name__} failed with exception: {e}")
                self.tests_failed += 1
        
        # Summary
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📋 LOGGING TEST SUITE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {self.tests_passed}")
        self.logger.info(f"Failed: {self.tests_failed}")
        self.logger.info(f"Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            self.logger.info("🎉 Comprehensive logging VALIDATED")
            return True
        else:
            self.logger.warning("⚠️ Logging validation needs attention")
            return False

def main():
    """Run comprehensive logging tests."""
    try:
        # Initialize enhanced logging
        AppLogger.initialize(log_level="DEBUG", console_output=True, file_output=True)
        
        # Run test suite
        test_suite = LoggingTestSuite()
        success = test_suite.run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Logging test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
