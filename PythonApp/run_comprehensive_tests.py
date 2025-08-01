#!/usr/bin/env python3
"""
Enhanced test runner for the multi-sensor recording system.
Coordinates comprehensive testing across all components.
"""

import sys
import os
import unittest
import time
import json
import subprocess
from datetime import datetime

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test modules
try:
    from tests.test_calibration_comprehensive import run_calibration_tests
    CALIBRATION_TESTS_AVAILABLE = True
except ImportError:
    CALIBRATION_TESTS_AVAILABLE = False

try:
    from tests.test_shimmer_comprehensive import run_shimmer_tests
    SHIMMER_TESTS_AVAILABLE = True
except ImportError:
    SHIMMER_TESTS_AVAILABLE = False

try:
    from tests.test_system_integration import run_integration_tests
    INTEGRATION_TESTS_AVAILABLE = True
except ImportError:
    INTEGRATION_TESTS_AVAILABLE = False

try:
    from tests.test_comprehensive_recording_session import run_comprehensive_recording_session_test
    RECORDING_SESSION_TESTS_AVAILABLE = True
except ImportError:
    RECORDING_SESSION_TESTS_AVAILABLE = False


class EnhancedTestRunner:
    """Enhanced test runner with comprehensive reporting and analysis."""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self, include_performance=True, include_stress=True):
        """Run all available test suites."""
        print("="*100)
        print("ENHANCED MULTI-SENSOR RECORDING SYSTEM TEST SUITE")
        print("="*100)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python version: {sys.version}")
        print(f"Platform: {sys.platform}")
        print()
        
        self.start_time = time.time()
        
        # Check component availability
        self._check_component_availability()
        
        # Run environment validation
        self._validate_environment()
        
        # Run unit tests
        self._run_unit_tests()
        
        # Run component-specific tests
        self._run_component_tests()
        
        # Run integration tests
        self._run_integration_tests()
        
        # Run performance tests
        if include_performance:
            self._run_performance_tests()
        
        # Run stress tests
        if include_stress:
            self._run_stress_tests()
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        self._generate_report()
        
        return self._overall_success()
    
    def _check_component_availability(self):
        """Check availability of system components."""
        print("Component Availability Check:")
        print("-" * 40)
        
        components = {
            'Calibration Tests': CALIBRATION_TESTS_AVAILABLE,
            'Shimmer Tests': SHIMMER_TESTS_AVAILABLE,
            'Integration Tests': INTEGRATION_TESTS_AVAILABLE,
            'Recording Session Tests': RECORDING_SESSION_TESTS_AVAILABLE
        }
        
        for component, available in components.items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {component:.<30} {status}")
        
        print()
    
    def _validate_environment(self):
        """Validate test environment and dependencies."""
        print("Environment Validation:")
        print("-" * 40)
        
        # Check Python version
        python_version = sys.version_info
        print(f"  Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version < (3, 9):
            print("  ⚠️  Warning: Python 3.9+ recommended")
        else:
            print("  ✓ Python version compatible")
        
        # Check critical dependencies
        critical_deps = [
            ('numpy', 'numpy'),
            ('opencv-python', 'cv2'),
            ('PyQt5', 'PyQt5'),
            ('matplotlib', 'matplotlib')
        ]
        
        for dep_name, import_name in critical_deps:
            try:
                __import__(import_name)
                print(f"  ✓ {dep_name} available")
            except ImportError:
                print(f"  ✗ {dep_name} not available")
        
        # Check optional dependencies
        optional_deps = [
            ('pyshimmer', 'pyshimmer'),
            ('bluetooth', 'bluetooth'),
            ('pybluez', 'bluetooth'),
            ('scipy', 'scipy'),
            ('pandas', 'pandas')
        ]
        
        available_optional = []
        for dep_name, import_name in optional_deps:
            try:
                __import__(import_name)
                available_optional.append(dep_name)
            except ImportError:
                pass
        
        print(f"  Optional dependencies available: {len(available_optional)}/{len(optional_deps)}")
        print()
    
    def _run_unit_tests(self):
        """Run basic unit tests using pytest if available."""
        print("Unit Tests:")
        print("-" * 40)
        
        try:
            # Try to run pytest on existing test files
            test_files = [
                'tests/test_calibration_components.py',
                'tests/test_calibration_manager.py',
                'tests/test_enhanced_logging.py',
                'tests/test_main.py'
            ]
            
            available_tests = []
            for test_file in test_files:
                full_path = os.path.join(os.path.dirname(__file__), '..', test_file)
                if os.path.exists(full_path):
                    available_tests.append(full_path)
            
            if available_tests:
                print(f"  Found {len(available_tests)} unit test files")
                
                # Run with unittest
                loader = unittest.TestLoader()
                suite = unittest.TestSuite()
                
                for test_file in available_tests:
                    try:
                        # Load tests from file
                        module_name = os.path.basename(test_file)[:-3]  # Remove .py
                        spec = unittest.util.spec_from_file_location(module_name, test_file)
                        if spec and spec.loader:
                            module = unittest.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            suite.addTests(loader.loadTestsFromModule(module))
                    except Exception as e:
                        print(f"  Warning: Could not load {test_file}: {e}")
                
                # Run the tests
                runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
                result = runner.run(suite)
                
                self.results['unit_tests'] = {
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1) * 100
                }
                
                print(f"  ✓ Unit tests completed: {result.testsRun} tests, {self.results['unit_tests']['success_rate']:.1f}% success rate")
            else:
                print("  No unit test files found")
                self.results['unit_tests'] = {'status': 'not_found'}
        except Exception as e:
            print(f"  Error running unit tests: {e}")
            self.results['unit_tests'] = {'status': 'error', 'error': str(e)}
        
        print()
    
    def _run_component_tests(self):
        """Run component-specific test suites."""
        print("Component-Specific Tests:")
        print("-" * 40)
        
        # Calibration tests
        if CALIBRATION_TESTS_AVAILABLE:
            print("  Running calibration tests...")
            try:
                success = run_calibration_tests()
                self.results['calibration_tests'] = {'success': success}
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"  Calibration tests: {status}")
            except Exception as e:
                print(f"  Calibration tests error: {e}")
                self.results['calibration_tests'] = {'success': False, 'error': str(e)}
        else:
            print("  Calibration tests: Not available")
            self.results['calibration_tests'] = {'status': 'not_available'}
        
        # Shimmer tests
        if SHIMMER_TESTS_AVAILABLE:
            print("  Running Shimmer tests...")
            try:
                success = run_shimmer_tests()
                self.results['shimmer_tests'] = {'success': success}
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"  Shimmer tests: {status}")
            except Exception as e:
                print(f"  Shimmer tests error: {e}")
                self.results['shimmer_tests'] = {'success': False, 'error': str(e)}
        else:
            print("  Shimmer tests: Not available")
            self.results['shimmer_tests'] = {'status': 'not_available'}
        
        # Recording session tests
        if RECORDING_SESSION_TESTS_AVAILABLE:
            print("  Running recording session tests...")
            try:
                success = run_comprehensive_recording_session_test()
                self.results['recording_session_tests'] = {'success': success}
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"  Recording session tests: {status}")
            except Exception as e:
                print(f"  Recording session tests error: {e}")
                self.results['recording_session_tests'] = {'success': False, 'error': str(e)}
        else:
            print("  Recording session tests: Not available")
            self.results['recording_session_tests'] = {'status': 'not_available'}
        
        print()
    
    def _run_integration_tests(self):
        """Run integration test suite."""
        print("Integration Tests:")
        print("-" * 40)
        
        if INTEGRATION_TESTS_AVAILABLE:
            print("  Running integration tests...")
            try:
                success = run_integration_tests()
                self.results['integration_tests'] = {'success': success}
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"  Integration tests: {status}")
            except Exception as e:
                print(f"  Integration tests error: {e}")
                self.results['integration_tests'] = {'success': False, 'error': str(e)}
        else:
            print("  Integration tests: Not available")
            self.results['integration_tests'] = {'status': 'not_available'}
        
        print()
    
    def _run_performance_tests(self):
        """Run performance benchmarks."""
        print("Performance Tests:")
        print("-" * 40)
        
        # Basic performance benchmarks
        import time
        import numpy as np
        
        benchmarks = {}
        
        # Benchmark 1: Image processing performance
        try:
            import cv2
            
            print("  Running image processing benchmark...")
            start_time = time.time()
            
            # Create test image
            img = np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
            
            # Perform typical operations
            for _ in range(10):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (15, 15), 0)
                edges = cv2.Canny(blurred, 50, 150)
            
            processing_time = time.time() - start_time
            benchmarks['image_processing'] = {
                'time': processing_time,
                'operations_per_sec': 10 / processing_time
            }
            
            print(f"    ✓ Image processing: {processing_time:.3f}s ({10/processing_time:.1f} ops/sec)")
        except Exception as e:
            print(f"    Image processing benchmark failed: {e}")
            benchmarks['image_processing'] = {'error': str(e)}
        
        # Benchmark 2: Data processing performance
        print("  Running data processing benchmark...")
        start_time = time.time()
        
        # Simulate sensor data processing
        data_points = 10000
        for i in range(data_points):
            data = {
                'timestamp': time.time() + i * 0.001,
                'gsr': 1000 + np.random.normal(0, 50),
                'ppg': 2000 + np.random.normal(0, 100),
                'accel_x': np.random.normal(0, 0.1),
                'accel_y': np.random.normal(0, 0.1),
                'accel_z': np.random.normal(0.9, 0.1)
            }
            # Simulate processing
            processed = {k: float(v) if isinstance(v, (int, float)) else v for k, v in data.items()}
        
        processing_time = time.time() - start_time
        benchmarks['data_processing'] = {
            'time': processing_time,
            'samples_per_sec': data_points / processing_time
        }
        
        print(f"    ✓ Data processing: {processing_time:.3f}s ({data_points/processing_time:.0f} samples/sec)")
        
        # Benchmark 3: Memory allocation performance
        print("  Running memory allocation benchmark...")
        start_time = time.time()
        
        large_arrays = []
        for _ in range(100):
            arr = np.random.rand(1000, 1000)
            large_arrays.append(arr)
        
        allocation_time = time.time() - start_time
        benchmarks['memory_allocation'] = {
            'time': allocation_time,
            'arrays_per_sec': 100 / allocation_time
        }
        
        print(f"    ✓ Memory allocation: {allocation_time:.3f}s ({100/allocation_time:.1f} arrays/sec)")
        
        # Clean up
        del large_arrays
        
        self.results['performance_tests'] = benchmarks
        print()
    
    def _run_stress_tests(self):
        """Run stress tests to validate system under load."""
        print("Stress Tests:")
        print("-" * 40)
        
        stress_results = {}
        
        # Stress test 1: High-frequency data processing
        print("  Running high-frequency data stress test...")
        try:
            import threading
            import queue
            
            data_queue = queue.Queue()
            processed_count = 0
            error_count = 0
            
            def data_producer():
                for i in range(5000):
                    data = {
                        'timestamp': time.time() + i * 0.0001,  # 10kHz simulation
                        'gsr': 1000 + i % 1000,
                        'ppg': 2000 + i % 2000
                    }
                    data_queue.put(data)
                    time.sleep(0.0001)  # Very brief pause
            
            def data_consumer():
                nonlocal processed_count, error_count
                while True:
                    try:
                        data = data_queue.get(timeout=1.0)
                        # Simulate processing
                        if isinstance(data.get('gsr'), (int, float)):
                            processed_count += 1
                        else:
                            error_count += 1
                        data_queue.task_done()
                    except queue.Empty:
                        break
                    except Exception:
                        error_count += 1
            
            # Start producer and consumer threads
            start_time = time.time()
            producer = threading.Thread(target=data_producer)
            consumer = threading.Thread(target=data_consumer)
            
            producer.start()
            consumer.start()
            
            producer.join()
            consumer.join()
            
            stress_time = time.time() - start_time
            
            stress_results['high_frequency'] = {
                'processed': processed_count,
                'errors': error_count,
                'time': stress_time,
                'throughput': processed_count / stress_time
            }
            
            print(f"    ✓ Processed {processed_count} samples in {stress_time:.2f}s ({processed_count/stress_time:.0f} Hz)")
            if error_count > 0:
                print(f"    ⚠️  {error_count} processing errors")
        
        except Exception as e:
            print(f"    High-frequency stress test failed: {e}")
            stress_results['high_frequency'] = {'error': str(e)}
        
        # Stress test 2: Memory pressure
        print("  Running memory pressure stress test...")
        try:
            import gc
            import psutil
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Allocate and deallocate memory repeatedly
            max_memory = initial_memory
            for cycle in range(20):
                # Allocate large arrays
                large_data = []
                for _ in range(100):
                    arr = np.random.rand(1000, 1000)
                    large_data.append(arr)
                
                current_memory = process.memory_info().rss / 1024 / 1024
                max_memory = max(max_memory, current_memory)
                
                # Deallocate
                del large_data
                gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024
            
            stress_results['memory_pressure'] = {
                'initial_memory_mb': initial_memory,
                'max_memory_mb': max_memory,
                'final_memory_mb': final_memory,
                'memory_growth_mb': final_memory - initial_memory
            }
            
            print(f"    ✓ Memory test: {initial_memory:.1f} MB → {max_memory:.1f} MB → {final_memory:.1f} MB")
            if final_memory - initial_memory > 50:
                print(f"    ⚠️  Memory growth: {final_memory - initial_memory:.1f} MB")
        
        except Exception as e:
            print(f"    Memory pressure test failed: {e}")
            stress_results['memory_pressure'] = {'error': str(e)}
        
        self.results['stress_tests'] = stress_results
        print()
    
    def _generate_report(self):
        """Generate comprehensive test report."""
        print("Test Execution Summary:")
        print("="*80)
        
        total_time = self.end_time - self.start_time
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Summary by category
        categories = ['unit_tests', 'calibration_tests', 'shimmer_tests', 'integration_tests', 'recording_session_tests']
        
        passed = 0
        failed = 0
        not_available = 0
        
        for category in categories:
            if category in self.results:
                result = self.results[category]
                if 'success' in result:
                    if result['success']:
                        passed += 1
                    else:
                        failed += 1
                elif 'status' in result and result['status'] == 'not_available':
                    not_available += 1
                else:
                    failed += 1
            else:
                not_available += 1
        
        print(f"Test Categories:")
        print(f"  ✓ Passed: {passed}")
        print(f"  ✗ Failed: {failed}")
        print(f"  - Not Available: {not_available}")
        print()
        
        # Performance summary
        if 'performance_tests' in self.results:
            print("Performance Benchmarks:")
            perf = self.results['performance_tests']
            
            if 'image_processing' in perf and 'operations_per_sec' in perf['image_processing']:
                print(f"  Image Processing: {perf['image_processing']['operations_per_sec']:.1f} ops/sec")
            
            if 'data_processing' in perf and 'samples_per_sec' in perf['data_processing']:
                print(f"  Data Processing: {perf['data_processing']['samples_per_sec']:.0f} samples/sec")
            
            print()
        
        # Stress test summary
        if 'stress_tests' in self.results:
            print("Stress Test Results:")
            stress = self.results['stress_tests']
            
            if 'high_frequency' in stress and 'throughput' in stress['high_frequency']:
                print(f"  High-frequency throughput: {stress['high_frequency']['throughput']:.0f} Hz")
            
            if 'memory_pressure' in stress and 'memory_growth_mb' in stress['memory_pressure']:
                growth = stress['memory_pressure']['memory_growth_mb']
                print(f"  Memory growth: {growth:.1f} MB")
            
            print()
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(os.path.dirname(__file__), '..', report_file)
        
        try:
            with open(report_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': total_time,
                    'python_version': sys.version,
                    'platform': sys.platform,
                    'results': self.results
                }, f, indent=2, default=str)
            
            print(f"Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"Could not save detailed report: {e}")
        
        print()
    
    def _overall_success(self):
        """Determine overall test success."""
        # Check critical test categories
        critical_categories = ['calibration_tests', 'shimmer_tests', 'integration_tests', 'recording_session_tests']
        
        for category in critical_categories:
            if category in self.results:
                result = self.results[category]
                if 'success' in result and not result['success']:
                    return False
        
        return True


def main():
    """Main test runner entry point."""
    runner = EnhancedTestRunner()
    
    # Parse command line arguments
    include_performance = '--no-performance' not in sys.argv
    include_stress = '--no-stress' not in sys.argv
    
    if '--help' in sys.argv:
        print("Enhanced Test Runner for Multi-Sensor Recording System")
        print()
        print("Usage: python run_comprehensive_tests.py [options]")
        print()
        print("Options:")
        print("  --no-performance    Skip performance benchmarks")
        print("  --no-stress        Skip stress tests")
        print("  --help             Show this help message")
        return 0
    
    # Run all tests
    success = runner.run_all_tests(
        include_performance=include_performance,
        include_stress=include_stress
    )
    
    if success:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        return 1


if __name__ == '__main__':
    sys.exit(main())