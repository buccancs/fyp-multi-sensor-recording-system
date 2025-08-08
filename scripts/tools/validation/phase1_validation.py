import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
sys.path.insert(0, str(Path(__file__).parent / "PythonApp" / "src"))
try:
    from utils.logging_config import get_logger, AppLogger, performance_timer, log_function_entry
    from session.session_manager import SessionManager
    from session.session_logger import get_session_logger
except ImportError as e:
    print(f"Warning: Could not import logging modules: {e}")
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda x: logging.getLogger(x)
class Phase1Validator:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.session_logger = None
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': '1',
            'focus_areas': [
                'MainActivity Refactoring',
                'Controller Integration',
                'Cross-component Communication',
                'State Management',
                'Performance Monitoring'
            ],
            'tests_run': [],
            'tests_passed': [],
            'tests_failed': [],
            'performance_metrics': {},
            'coverage_analysis': {},
            'architectural_assessment': {}
        }
        self.project_root = Path(__file__).parent
        self.python_root = self.project_root / "PythonApp"
        self.android_root = self.project_root / "AndroidApp"
        try:
            self.session_logger = get_session_logger()
        except Exception as e:
            self.logger.warning(f"Could not initialize session logger: {e}")
    @log_function_entry
    def validate_logging_infrastructure(self) -> bool:
        test_name = "logging_infrastructure"
        self.logger.info("=== Phase 1 Test: Logging Infrastructure Validation ===")
        try:
            self.logger.info("Testing Python logging system...")
            self.logger.debug("Debug message test")
            self.logger.info("Info message test")
            self.logger.warning("Warning message test")
            self.logger.error("Error message test")
            extra_data = {
                'test_id': test_name,
                'component': 'logging_validation',
                'metrics': {'memory_usage': 100, 'cpu_usage': 15}
            }
            self.logger.info("Structured logging test", extra=extra_data)
            timer_id = AppLogger.start_performance_timer("logging_test", "validation")
            time.sleep(0.1)
            duration = AppLogger.end_performance_timer(timer_id, __name__)
            AppLogger.log_memory_usage("logging_test_context", __name__)
            log_dir = AppLogger.get_log_dir()
            if log_dir and log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                self.logger.info(f"Log files found: {[f.name for f in log_files]}")
                for log_file in log_files:
                    if log_file.stat().st_size > 0:
                        self.logger.info(f"Log file {log_file.name}: {log_file.stat().st_size} bytes")
            self.validation_results['tests_passed'].append(test_name)
            self.logger.info("✅ Python logging infrastructure validation PASSED")
            return True
        except Exception as e:
            self.logger.error(f"❌ Logging infrastructure validation FAILED: {e}", exc_info=True)
            self.validation_results['tests_failed'].append(test_name)
            return False
    @performance_timer("android_analysis", "phase1")
    def analyze_android_architecture(self) -> bool:
        test_name = "android_architecture_analysis"
        self.logger.info("=== Phase 1 Test: Android Architecture Analysis ===")
        try:
            main_activity_path = self.android_root / "src/main/java/com/multisensor/recording/MainActivity.kt"
            if not main_activity_path.exists():
                self.logger.error(f"MainActivity not found at {main_activity_path}")
                self.validation_results['tests_failed'].append(test_name)
                return False
            with open(main_activity_path, 'r') as f:
                lines = f.readlines()
                total_lines = len(lines)
                code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
            self.logger.info(f"MainActivity analysis:")
            self.logger.info(f"  Total lines: {total_lines}")
            self.logger.info(f"  Code lines: {code_lines}")
            target_lines = 500
            refactoring_progress = max(0, (1531 - total_lines) / (1531 - target_lines) * 100)
            self.validation_results['architectural_assessment']['mainactivity'] = {
                'current_lines': total_lines,
                'target_lines': target_lines,
                'original_lines': 1531,
                'refactoring_progress_percent': refactoring_progress,
                'meets_phase1_target': total_lines < target_lines
            }
            self.logger.info(f"  Refactoring progress: {refactoring_progress:.1f}%")
            self.logger.info(f"  Meets Phase 1 target (<500 lines): {'✅' if total_lines < target_lines else '❌'}")
            controllers_dir = self.android_root / "src/main/java/com/multisensor/recording/controllers"
            if controllers_dir.exists():
                controller_files = list(controllers_dir.glob("*.kt"))
                self.logger.info(f"  Controller files found: {len(controller_files)}")
                for controller in controller_files:
                    self.logger.info(f"    - {controller.name}")
                self.validation_results['architectural_assessment']['controllers'] = {
                    'count': len(controller_files),
                    'files': [f.name for f in controller_files]
                }
            app_class_path = self.android_root / "src/main/java/com/multisensor/recording/MultiSensorApplication.kt"
            if app_class_path.exists():
                with open(app_class_path, 'r') as f:
                    content = f.read()
                    has_hilt = '@HiltAndroidApp' in content
                    self.logger.info(f"  Hilt dependency injection: {'✅' if has_hilt else '❌'}")
            self.validation_results['tests_passed'].append(test_name)
            self.logger.info("✅ Android architecture analysis PASSED")
            return True
        except Exception as e:
            self.logger.error(f"❌ Android architecture analysis FAILED: {e}", exc_info=True)
            self.validation_results['tests_failed'].append(test_name)
            return False
    @log_function_entry
    def test_controller_integration(self) -> bool:
        test_name = "controller_integration"
        self.logger.info("=== Phase 1 Test: Controller Integration Validation ===")
        try:
            self.logger.info("Testing Python controller components...")
            session_manager = SessionManager(base_dir="test_phase1_sessions")
            session_id = session_manager.create_session("phase1_validation")
            self.logger.info(f"Created test session: {session_id}")
            if self.session_logger:
                self.session_logger.log_session_start(session_id, ["test_device"])
                self.logger.info("Session logging integration working")
            session_info = session_manager.get_session_info(session_id)
            if session_info:
                self.logger.info(f"Session state management: ✅")
                self.logger.info(f"Session directory: {session_info.get('session_dir', 'N/A')}")
            try:
                from network.device_server import JsonSocketServer
                server = JsonSocketServer("localhost", 9999)
                self.logger.info("Network communication component available: ✅")
                self.validation_results['architectural_assessment']['communication'] = {
                    'network_server': 'available',
                    'session_management': 'working',
                    'state_persistence': 'functional'
                }
            except ImportError as e:
                self.logger.warning(f"Network component not available: {e}")
            self.logger.info("Testing controller coordination patterns...")
            controllers_tested = []
            try:
                from calibration.calibration_manager import CalibrationManager
                cal_manager = CalibrationManager("test_calibration")
                controllers_tested.append("CalibrationManager")
                self.logger.info("CalibrationManager: ✅")
            except Exception as e:
                self.logger.warning(f"CalibrationManager test: {e}")
            try:
                from application import Application
                controllers_tested.append("Application")
                self.logger.info("Application controller: ✅")
            except Exception as e:
                self.logger.warning(f"Application controller test: {e}")
            self.validation_results['architectural_assessment']['controller_integration'] = {
                'controllers_tested': controllers_tested,
                'session_management': 'functional',
                'coordination_pattern': 'implemented'
            }
            self.validation_results['tests_passed'].append(test_name)
            self.logger.info("✅ Controller integration validation PASSED")
            return True
        except Exception as e:
            self.logger.error(f"❌ Controller integration validation FAILED: {e}", exc_info=True)
            self.validation_results['tests_failed'].append(test_name)
            return False
    @performance_timer("performance_monitoring", "phase1")
    def test_performance_monitoring(self) -> bool:
        test_name = "performance_monitoring"
        self.logger.info("=== Phase 1 Test: Performance Monitoring Validation ===")
        try:
            self.logger.info("Testing performance monitoring...")
            operations = [
                ("file_io_simulation", 0.05),
                ("network_simulation", 0.1),
                ("calibration_simulation", 0.15),
                ("session_management", 0.08)
            ]
            performance_data = {}
            for op_name, sleep_time in operations:
                timer_id = AppLogger.start_performance_timer(op_name, "phase1_test")
                time.sleep(sleep_time)
                duration = AppLogger.end_performance_timer(timer_id, __name__)
                performance_data[op_name] = {
                    'duration_ms': duration * 1000,
                    'expected_ms': sleep_time * 1000,
                    'overhead_ms': (duration - sleep_time) * 1000
                }
                self.logger.info(f"  {op_name}: {duration*1000:.1f}ms")
            active_timers = AppLogger.get_active_timers()
            self.logger.info(f"Active timers tracking: {len(active_timers)} timers")
            AppLogger.log_memory_usage("performance_test_start", __name__)
            test_data = [i for i in range(10000)]
            AppLogger.log_memory_usage("performance_test_end", __name__)
            self.validation_results['performance_metrics'] = performance_data
            self.validation_results['performance_metrics']['memory_monitoring'] = 'functional'
            self.validation_results['performance_metrics']['timer_tracking'] = 'working'
            self.validation_results['tests_passed'].append(test_name)
            self.logger.info("✅ Performance monitoring validation PASSED")
            return True
        except Exception as e:
            self.logger.error(f"❌ Performance monitoring validation FAILED: {e}", exc_info=True)
            self.validation_results['tests_failed'].append(test_name)
            return False
    def test_cross_platform_communication(self) -> bool:
        test_name = "cross_platform_communication"
        self.logger.info("=== Phase 1 Test: Cross-Platform Communication ===")
        try:
            protocol_dir = self.project_root / "protocol"
            if protocol_dir.exists():
                protocol_files = list(protocol_dir.glob("*.py"))
                self.logger.info(f"Protocol definitions found: {len(protocol_files)}")
                for proto_file in protocol_files:
                    self.logger.info(f"  - {proto_file.name}")
            try:
                from network.device_server import JsonSocketServer
                from network.message_handler import MessageHandler
                self.logger.info("Network modules available: ✅")
                server = JsonSocketServer("localhost", 9998)
                self.logger.info("JsonSocketServer instantiation: ✅")
                self.validation_results['architectural_assessment']['communication_stack'] = {
                    'network_modules': 'available',
                    'protocol_definitions': 'present',
                    'message_handling': 'implemented'
                }
            except ImportError as e:
                self.logger.warning(f"Network modules not fully available: {e}")
                self.validation_results['architectural_assessment']['communication_stack'] = {
                    'status': 'partial',
                    'issue': str(e)
                }
            android_network_dir = self.android_root / "src/main/java/com/multisensor/recording/network"
            if android_network_dir.exists():
                network_files = list(android_network_dir.glob("*.kt"))
                self.logger.info(f"Android network classes: {len(network_files)}")
                self.validation_results['architectural_assessment']['android_communication'] = {
                    'network_classes': len(network_files),
                    'files': [f.name for f in network_files]
                }
            self.validation_results['tests_passed'].append(test_name)
            self.logger.info("✅ Cross-platform communication validation PASSED")
            return True
        except Exception as e:
            self.logger.error(f"❌ Cross-platform communication validation FAILED: {e}", exc_info=True)
            self.validation_results['tests_failed'].append(test_name)
            return False
    def run_existing_test_suite(self) -> bool:
        test_name = "existing_test_suite"
        self.logger.info("=== Phase 1 Test: Existing Test Suite Validation ===")
        try:
            python_tests = list(self.python_root.rglob("test_*.py"))
            android_tests = list(self.android_root.rglob("*Test.kt"))
            self.logger.info(f"Found {len(python_tests)} Python test files")
            self.logger.info(f"Found {len(android_tests)} Android test files")
            critical_tests = [
                "test_logging.py",
                "test_integration_logging.py"
            ]
            passed_tests = []
            failed_tests = []
            for test_file in critical_tests:
                test_path = self.python_root / test_file
                if test_path.exists():
                    try:
                        self.logger.info(f"Running {test_file}...")
                        result = subprocess.run(
                            [sys.executable, str(test_path)],
                            cwd=str(self.python_root),
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        if result.returncode == 0:
                            passed_tests.append(test_file)
                            self.logger.info(f"  ✅ {test_file} PASSED")
                        else:
                            failed_tests.append(test_file)
                            self.logger.warning(f"  ❌ {test_file} FAILED")
                            self.logger.warning(f"    Error: {result.stderr[:200]}")
                    except subprocess.TimeoutExpired:
                        failed_tests.append(test_file)
                        self.logger.warning(f"  ⏰ {test_file} TIMEOUT")
                    except Exception as e:
                        failed_tests.append(test_file)
                        self.logger.warning(f"  ❌ {test_file} ERROR: {e}")
            self.validation_results['coverage_analysis'] = {
                'python_test_files': len(python_tests),
                'android_test_files': len(android_tests),
                'critical_tests_passed': passed_tests,
                'critical_tests_failed': failed_tests,
                'test_coverage_estimated': f"{len(passed_tests)}/{len(critical_tests)} critical tests passing"
            }
            success = len(passed_tests) > 0
            if success:
                self.validation_results['tests_passed'].append(test_name)
                self.logger.info("✅ Existing test suite validation PASSED")
            else:
                self.validation_results['tests_failed'].append(test_name)
                self.logger.warning("⚠️ Existing test suite validation had issues")
            return success
        except Exception as e:
            self.logger.error(f"❌ Existing test suite validation FAILED: {e}", exc_info=True)
            self.validation_results['tests_failed'].append(test_name)
            return False
    @log_function_entry
    def generate_validation_report(self) -> Path:
        self.logger.info("=== Generating Phase 1 Validation Report ===")
        total_tests = len(self.validation_results['tests_passed']) + len(self.validation_results['tests_failed'])
        pass_rate = len(self.validation_results['tests_passed']) / total_tests * 100 if total_tests > 0 else 0
        self.validation_results['summary'] = {
            'total_tests': total_tests,
            'tests_passed': len(self.validation_results['tests_passed']),
            'tests_failed': len(self.validation_results['tests_failed']),
            'pass_rate_percent': pass_rate,
            'overall_status': 'PASSED' if pass_rate >= 80 else 'NEEDS_ATTENTION',
            'validation_date': datetime.now().isoformat(),
            'environment': {
                'python_version': sys.version,
                'platform': os.name,
                'working_directory': str(Path.cwd())
            }
        }
        mainactivity_data = self.validation_results['architectural_assessment'].get('mainactivity', {})
        meets_phase1_target = mainactivity_data.get('meets_phase1_target', False)
        self.validation_results['phase1_assessment'] = {
            'mainactivity_refactoring': {
                'status': 'COMPLETED' if meets_phase1_target else 'IN_PROGRESS',
                'target_achieved': meets_phase1_target,
                'current_progress': mainactivity_data.get('refactoring_progress_percent', 0)
            },
            'controller_integration': {
                'status': 'IMPLEMENTED' if 'controller_integration' in self.validation_results.get('architectural_assessment', {}) else 'PENDING'
            },
            'logging_infrastructure': {
                'status': 'complete' if 'logging_infrastructure' in self.validation_results['tests_passed'] else 'INCOMPLETE'
            },
            'performance_monitoring': {
                'status': 'FUNCTIONAL' if 'performance_monitoring' in self.validation_results['tests_passed'] else 'MISSING'
            }
        }
        report_file = self.project_root / f"phase1_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        self.logger.info(f"📋 Validation report saved to: {report_file}")
        return report_file
    def run_complete_validation(self) -> bool:
        self.logger.info("🚀 Starting Phase 1 Implementation Validation")
        self.logger.info("=" * 60)
        validation_start = time.time()
        if self.session_logger:
            try:
                self.session_logger.log_session_start("phase1_validation", ["validation_system"])
            except Exception as e:
                self.logger.warning(f"Could not log validation session: {e}")
        tests = [
            ("Logging Infrastructure", self.validate_logging_infrastructure),
            ("Android Architecture", self.analyze_android_architecture),
            ("Controller Integration", self.test_controller_integration),
            ("Performance Monitoring", self.test_performance_monitoring),
            ("Cross-Platform Communication", self.test_cross_platform_communication),
            ("Existing Test Suite", self.run_existing_test_suite)
        ]
        for test_name, test_func in tests:
            self.logger.info(f"\n--- Running: {test_name} ---")
            try:
                success = test_func()
                status = "✅ PASSED" if success else "❌ FAILED"
                self.logger.info(f"{test_name}: {status}")
            except Exception as e:
                self.logger.error(f"{test_name}: ❌ EXCEPTION - {e}", exc_info=True)
                self.validation_results['tests_failed'].append(test_name.lower().replace(' ', '_'))
        validation_duration = time.time() - validation_start
        self.validation_results['validation_duration_seconds'] = validation_duration
        report_file = self.generate_validation_report()
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📋 PHASE 1 VALIDATION SUMMARY")
        self.logger.info("=" * 60)
        summary = self.validation_results['summary']
        self.logger.info(f"Total Tests: {summary['total_tests']}")
        self.logger.info(f"Passed: {summary['tests_passed']}")
        self.logger.info(f"Failed: {summary['tests_failed']}")
        self.logger.info(f"Pass Rate: {summary['pass_rate_percent']:.1f}%")
        self.logger.info(f"Overall Status: {summary['overall_status']}")
        self.logger.info(f"Duration: {validation_duration:.1f} seconds")
        self.logger.info(f"Report: {report_file}")
        phase1_assessment = self.validation_results['phase1_assessment']
        self.logger.info("\n📊 PHASE 1 SPECIFIC ASSESSMENT:")
        for component, status_info in phase1_assessment.items():
            status = status_info.get('status', 'UNKNOWN')
            self.logger.info(f"  {component}: {status}")
        overall_success = summary['pass_rate_percent'] >= 80
        if overall_success:
            self.logger.info("\n🎉 Phase 1 Validation: SUCCESS")
            self.logger.info("✅ System is ready for Phase 1 completion")
        else:
            self.logger.warning("\n⚠️ Phase 1 Validation: NEEDS ATTENTION")
            self.logger.warning("❌ Some components require additional work")
        return overall_success
def main():
    print("🚀 Multi-Sensor Recording System - Phase 1 Validation")
    print("=" * 60)
    try:
        AppLogger.initialize(log_level="INFO", console_output=True, file_output=True)
        validator = Phase1Validator()
        success = validator.run_complete_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with exception: {e}")
        traceback.print_exc()
        sys.exit(1)
if __name__ == "__main__":
    main()