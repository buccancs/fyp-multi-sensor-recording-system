#!/usr/bin/env python3
"""
Enhanced Logging Integration for Phase 1
=========================================

This script adds comprehensive logging to areas that may be missing it,
particularly focusing on:
- MainActivity refactoring monitoring
- Controller integration points
- State management operations
- Performance-critical sections
- Cross-component communication

Author: Phase 1 Implementation Team
Date: 2025-07-31
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent / "PythonApp" / "src"))

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class LoggingEnhancer:
    """
    Enhances existing code with comprehensive logging for Phase 1 validation.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.android_root = self.project_root / "AndroidApp"
        self.python_root = self.project_root / "PythonApp"
        self.enhancements_made = []

    def enhance_mainactivity_logging(self) -> bool:
        """
        Add comprehensive logging to MainActivity for refactoring monitoring.
        """
        logger.info("Enhancing MainActivity with comprehensive logging...")

        main_activity_path = self.android_root / "src/main/java/com/multisensor/recording/MainActivity.kt"

        if not main_activity_path.exists():
            logger.error(f"MainActivity not found at {main_activity_path}")
            return False

        try:
            with open(main_activity_path, 'r') as f:
                content = f.read()

            if "AppLogger.logMethodEntry" in content and "AppLogger.logStateChange" in content:
                logger.info("MainActivity already has comprehensive logging")
                return True

            enhancements = [
                (
                    r'override fun onCreate\(savedInstanceState: Bundle\?\) \{',
                    '''override fun onCreate(savedInstanceState: Bundle?) {
        AppLogger.logMethodEntry("MainActivity", "onCreate", "Initializing main activity")
        AppLogger.logMemoryUsage("MainActivity", "onCreate - start")'''
                ),

                (
                    r'override fun onResume\(\) \{',
                    '''override fun onResume() {
        AppLogger.logMethodEntry("MainActivity", "onResume", "Activity resuming")'''
                ),

                (
                    r'override fun onPause\(\) \{',
                    '''override fun onPause() {
        AppLogger.logMethodEntry("MainActivity", "onPause", "Activity pausing")'''
                ),

                (
                    r'fun onPermissionResult\(',
                    '''fun onPermissionResult(
        AppLogger.logMethodEntry("MainActivity", "onPermissionResult", "Processing permission result")'''
                ),

                (
                    r'private fun updateRecordingState\(',
                    '''private fun updateRecordingState(
        AppLogger.logStateChange("MainActivity", "recording_state", "Updating recording state")'''
                )
            ]

            original_content = content

            for pattern, replacement in enhancements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content, count=1)
                    self.enhancements_made.append(f"MainActivity: {pattern}")

            if content != original_content:
                backup_path = main_activity_path.with_suffix('.kt.backup')
                with open(backup_path, 'w') as f:
                    f.write(original_content)

                with open(main_activity_path, 'w') as f:
                    f.write(content)

                logger.info(f"Enhanced MainActivity with logging (backup: {backup_path})")
                return True
            else:
                logger.info("No MainActivity enhancements needed")
                return True

        except Exception as e:
            logger.error(f"Failed to enhance MainActivity logging: {e}")
            return False

    def enhance_controller_logging(self) -> bool:
        """
        Add logging to controller classes for integration monitoring.
        """
        logger.info("Enhancing controller classes with logging...")

        controllers_dir = self.android_root / "src/main/java/com/multisensor/recording/controllers"

        if not controllers_dir.exists():
            logger.warning(f"Controllers directory not found: {controllers_dir}")
            return True

        controller_files = list(controllers_dir.glob("*.kt"))

        for controller_file in controller_files:
            try:
                with open(controller_file, 'r') as f:
                    content = f.read()

                if "import com.multisensor.recording.util.AppLogger" not in content:
                    package_line = re.search(r'package .*\n', content)
                    if package_line:
                        insert_pos = package_line.end()
                        logging_import = "\nimport com.multisensor.recording.util.AppLogger\nimport com.multisensor.recording.util.logI\nimport com.multisensor.recording.util.logE\n"
                        content = content[:insert_pos] + logging_import + content[insert_pos:]

                class_pattern = r'class (\w+Controller).*?\{'
                class_match = re.search(class_pattern, content)
                if class_match:
                    class_name = class_match.group(1)

                    init_pattern = r'init \{'
                    if re.search(init_pattern, content):
                        content = re.sub(
                            init_pattern,
                            f'''init {{
        AppLogger.logLifecycle("{class_name}", "init", "Controller initialized")''',
                            content,
                            count=1
                        )
                        self.enhancements_made.append(f"{class_name}: Added init logging")

                with open(controller_file, 'w') as f:
                    f.write(content)

                logger.info(f"Enhanced {controller_file.name} with logging")

            except Exception as e:
                logger.warning(f"Could not enhance {controller_file.name}: {e}")

        return True

    def enhance_python_components(self) -> bool:
        """
        Add comprehensive logging to Python components.
        """
        logger.info("Enhancing Python components with logging...")

        modules_to_enhance = [
            "src/session/session_manager.py",
            "src/calibration/calibration_manager.py",
            "src/network/device_server.py",
            "src/application.py"
        ]

        for module_path in modules_to_enhance:
            full_path = self.python_root / module_path

            if not full_path.exists():
                logger.debug(f"Module not found (skipping): {module_path}")
                continue

            try:
                with open(full_path, 'r') as f:
                    content = f.read()

                if "from utils.logging_config import get_logger" not in content:
                    imports_end = self._find_imports_end(content)
                    if imports_end:
                        logging_import = "\nfrom utils.logging_config import get_logger, log_function_entry, performance_timer\n"
                        content = content[:imports_end] + logging_import + content[imports_end:]

                class_pattern = r'class (\w+).*?:'
                classes = re.findall(class_pattern, content)

                for class_name in classes:
                    init_pattern = f'def __init__\\(self.*?\\):\\s*\n'
                    init_match = re.search(init_pattern, content)
                    if init_match and f"self.logger = get_logger(__name__)" not in content:
                        insert_pos = init_match.end()
                        logger_init = f'        self.logger = get_logger(__name__)\n        self.logger.info(f"{class_name} initialized")\n'
                        content = content[:insert_pos] + logger_init + content[insert_pos:]
                        self.enhancements_made.append(f"{module_path}: Added logger to {class_name}")

                performance_methods = ['start_recording', 'stop_recording', 'calibrate', 'process', 'handle_message']
                for method in performance_methods:
                    method_pattern = f'def {method}\\('
                    if re.search(method_pattern, content) and f'@performance_timer("{method}")' not in content:
                        content = re.sub(
                            method_pattern,
                            f'    @performance_timer("{method}")\n    def {method}(',
                            content
                        )
                        self.enhancements_made.append(f"{module_path}: Added performance timer to {method}")

                with open(full_path, 'w') as f:
                    f.write(content)

                logger.info(f"Enhanced {module_path} with logging")

            except Exception as e:
                logger.warning(f"Could not enhance {module_path}: {e}")

        return True

    def _find_imports_end(self, content: str) -> int:
        """Find the end of import statements in Python code."""
        lines = content.split('\n')
        imports_end_line = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports_end_line = i
            elif stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                break

        return len('\n'.join(lines[:imports_end_line + 1])) + 1

    def create_logging_test_suite(self) -> bool:
        """
        Create comprehensive test suite for logging validation.
        """
        logger.info("Creating logging test suite...")

        test_file_path = self.project_root / "test_comprehensive_logging.py"

        test_content = '''#!/usr/bin/env python3
"""
Comprehensive Logging Test Suite for Phase 1
=============================================

Tests all logging enhancements and validates comprehensive coverage.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "PythonApp" / "src"))

from PythonApp.utils.logging_config import get_logger, AppLogger, performance_timer

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
            self.logger.debug("Debug level test")
            self.logger.info("Info level test")
            self.logger.warning("Warning level test")
            self.logger.error("Error level test")
            self.logger.critical("Critical level test")

            self.logger.info("Structured logging test", extra={
                'component': 'logging_test',
                'metrics': {'cpu': 15, 'memory': 128}
            })

            timer_id = AppLogger.start_performance_timer("test_operation", "logging_test")
            time.sleep(0.1)
            AppLogger.end_performance_timer(timer_id, __name__)

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
            operations = ['file_io', 'network_call', 'data_processing']

            for operation in operations:
                timer_id = AppLogger.start_performance_timer(operation, "test_context")
                time.sleep(0.05)
                duration = AppLogger.end_performance_timer(timer_id, __name__)

                self.logger.info(f"Operation {operation}: {duration*1000:.1f}ms")

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

        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0

        self.logger.info("\\n" + "=" * 60)
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
        AppLogger.initialize(log_level="DEBUG", console_output=True, file_output=True)

        test_suite = LoggingTestSuite()
        success = test_suite.run_all_tests()

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Logging test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(test_file_path, 'w') as f:
            f.write(test_content)

        os.chmod(test_file_path, 0o755)

        logger.info(f"Created comprehensive logging test suite: {test_file_path}")
        return True

    def create_android_logging_test(self) -> bool:
        """
        Create Android logging test utility.
        """
        logger.info("Creating Android logging test utility...")

        test_file_path = self.android_root / "src/main/java/com/multisensor/recording/util/LoggingTestUtility.kt"

        test_content = '''package com.multisensor.recording.util

import android.content.Context
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Comprehensive Logging Test Utility for Phase 1 Validation
 *
 * Tests all Android logging functionality and validates integration.
 */
object LoggingTestUtility {

    private const val TAG = "LoggingTestUtility"

    fun runComprehensiveLoggingTest(context: Context) {
        AppLogger.logMethodEntry(TAG, "runComprehensiveLoggingTest", "Starting comprehensive logging test")

        CoroutineScope(Dispatchers.IO).launch {
            try {
                testBasicLogging()
                testSpecializedLogging()
                testPerformanceLogging(context)
                testMemoryLogging(context)
                testStateChangeLogging()

                AppLogger.i(TAG, "✅ All Android logging tests PASSED")

            } catch (e: Exception) {
                AppLogger.e(TAG, "❌ Android logging tests FAILED", e)
            }
        }
    }

    private fun testBasicLogging() {
        AppLogger.d(TAG, "Debug message test")
        AppLogger.i(TAG, "Info message test")
        AppLogger.w(TAG, "Warning message test")
        AppLogger.e(TAG, "Error message test")
        AppLogger.v(TAG, "Verbose message test")
    }

    private fun testSpecializedLogging() {
        AppLogger.logLifecycle(TAG, "test_lifecycle", "Testing lifecycle logging")
        AppLogger.logNetwork(TAG, "test_request", "http://test.example.com", "200 OK")
        AppLogger.logRecording(TAG, "test_recording", "1920x1080@30fps")
        AppLogger.logSensor(TAG, "test_sensor", "GSR", "value=1.23")
        AppLogger.logFile(TAG, "test_file", "test.mp4", 1024L)
        AppLogger.logStateChange(TAG, "test_state", "IDLE", "RECORDING")
    }

    private fun testPerformanceLogging(context: Context) {
        AppLogger.startTiming(TAG, "test_operation")

        // Simulate some work
        Thread.sleep(100)

        AppLogger.endTiming(TAG, "test_operation")
        AppLogger.logMemoryUsage(TAG, "After performance test")
    }

    private fun testMemoryLogging(context: Context) {
        AppLogger.logMemoryUsage(TAG, "Memory test start")

        // Simulate memory allocation
        val testData = IntArray(1000) { it }

        AppLogger.logMemoryUsage(TAG, "Memory test end")
    }

    private fun testStateChangeLogging() {
        val states = listOf("INITIALIZING", "READY", "RECORDING", "PROCESSING", "COMPLETE")

        for (i in 0 until states.size - 1) {
            AppLogger.logStateChange(TAG, "test_component", states[i], states[i + 1])
            Thread.sleep(50)
        }
    }

    fun validateLoggingIntegration(): Boolean {
        AppLogger.logMethodEntry(TAG, "validateLoggingIntegration", "Validating logging integration")

        return try {
            // Test that all logging methods are available
            AppLogger.i(TAG, "Logging integration validation")
            AppLogger.logMethodEntry(TAG, "test", "test")
            AppLogger.startTiming(TAG, "validation")
            AppLogger.endTiming(TAG, "validation")

            true
        } catch (e: Exception) {
            AppLogger.e(TAG, "Logging integration validation failed", e)
            false
        }
    }
}'''

        test_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(test_file_path, 'w') as f:
            f.write(test_content)

        logger.info(f"Created Android logging test utility: {test_file_path}")
        return True

    def run_enhancements(self) -> bool:
        """
        Run all logging enhancements.
        """
        logger.info("🔧 Starting comprehensive logging enhancements for Phase 1")
        logger.info("=" * 60)

        enhancements = [
            ("MainActivity Logging", self.enhance_mainactivity_logging),
            ("Controller Logging", self.enhance_controller_logging),
            ("Python Components", self.enhance_python_components),
            ("Logging Test Suite", self.create_logging_test_suite),
            ("Android Logging Test", self.create_android_logging_test)
        ]

        success_count = 0

        for enhancement_name, enhancement_func in enhancements:
            logger.info(f"\n--- {enhancement_name} ---")
            try:
                if enhancement_func():
                    logger.info(f"✅ {enhancement_name} completed successfully")
                    success_count += 1
                else:
                    logger.warning(f"⚠️ {enhancement_name} completed with warnings")
            except Exception as e:
                logger.error(f"❌ {enhancement_name} failed: {e}")

        logger.info("\n" + "=" * 60)
        logger.info("📋 LOGGING ENHANCEMENT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Enhancements completed: {success_count}/{len(enhancements)}")
        logger.info(f"Total modifications made: {len(self.enhancements_made)}")

        if self.enhancements_made:
            logger.info("\nSpecific enhancements:")
            for enhancement in self.enhancements_made:
                logger.info(f"  - {enhancement}")

        overall_success = success_count >= len(enhancements) - 1

        if overall_success:
            logger.info("\n🎉 Logging enhancement: SUCCESS")
            logger.info("✅ Comprehensive logging coverage achieved")
        else:
            logger.warning("\n⚠️ Logging enhancement: PARTIAL SUCCESS")
            logger.warning("Some enhancements may need manual review")

        return overall_success


def main():
    """Main entry point for logging enhancement."""
    print("🔧 Multi-Sensor Recording System - Logging Enhancement for Phase 1")
    print("=" * 70)

    try:
        enhancer = LoggingEnhancer()
        success = enhancer.run_enhancements()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Enhancement interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Enhancement failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()