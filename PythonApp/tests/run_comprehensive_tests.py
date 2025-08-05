#!/usr/bin/env python3
"""
Comprehensive Test Runner for All Python Tests
==============================================

This module orchestrates the execution of all comprehensive test suites
for the Python components of the Multi-Sensor Recording System.

Test suites included:
- Calibration module comprehensive tests
- Network module comprehensive tests  
- Session management comprehensive tests
- GUI component tests (if available)
- Hand segmentation tests (if available)
- Webcam capture tests (if available)

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import json
import os
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
try:
    from test_calibration_comprehensive import run_calibration_tests
    CALIBRATION_TESTS_AVAILABLE = True
except ImportError:
    CALIBRATION_TESTS_AVAILABLE = False

try:
    from test_network_comprehensive import run_network_tests
    NETWORK_TESTS_AVAILABLE = True
except ImportError:
    NETWORK_TESTS_AVAILABLE = False

try:
    from test_session_comprehensive import run_session_tests  
    SESSION_TESTS_AVAILABLE = True
except ImportError:
    SESSION_TESTS_AVAILABLE = False

# Try to import additional test modules
try:
    from test_gui_comprehensive import run_gui_tests
    GUI_TESTS_AVAILABLE = True
except ImportError:
    GUI_TESTS_AVAILABLE = False

try:
    from test_webcam_comprehensive import run_webcam_tests
    WEBCAM_TESTS_AVAILABLE = True
except ImportError:
    WEBCAM_TESTS_AVAILABLE = False

try:
    from test_hand_segmentation_comprehensive import run_hand_segmentation_tests
    HAND_SEGMENTATION_TESTS_AVAILABLE = True
except ImportError:
    HAND_SEGMENTATION_TESTS_AVAILABLE = False


class ComprehensiveTestRunner:
    """Comprehensive test runner for all Python modules."""
    
    def __init__(self):
        self.results = {
            "test_run_timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "working_directory": str(Path.cwd()),
            "test_suites": {},
            "overall_summary": {},
            "environment_info": self._get_environment_info()
        }
        
        self.available_test_suites = {
            "calibration": {
                "available": CALIBRATION_TESTS_AVAILABLE,
                "runner": run_calibration_tests if CALIBRATION_TESTS_AVAILABLE else None,
                "description": "Camera calibration system tests"
            },
            "network": {
                "available": NETWORK_TESTS_AVAILABLE,
                "runner": run_network_tests if NETWORK_TESTS_AVAILABLE else None,
                "description": "Network communication and device management tests"
            },
            "session": {
                "available": SESSION_TESTS_AVAILABLE,
                "runner": run_session_tests if SESSION_TESTS_AVAILABLE else None,
                "description": "Session management and coordination tests"
            },
            "gui": {
                "available": GUI_TESTS_AVAILABLE,
                "runner": run_gui_tests if GUI_TESTS_AVAILABLE else None,
                "description": "GUI component and interaction tests"
            },
            "webcam": {
                "available": WEBCAM_TESTS_AVAILABLE,
                "runner": run_webcam_tests if WEBCAM_TESTS_AVAILABLE else None,
                "description": "Webcam capture and processing tests"
            },
            "hand_segmentation": {
                "available": HAND_SEGMENTATION_TESTS_AVAILABLE,
                "runner": run_hand_segmentation_tests if HAND_SEGMENTATION_TESTS_AVAILABLE else None,
                "description": "Hand segmentation and computer vision tests"
            }
        }
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for test context."""
        env_info = {
            "python_version": sys.version_info[:3],
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
            "available_modules": {}
        }
        
        # Check for key dependencies
        dependencies = [
            ("opencv-python", "cv2"),
            ("numpy", "numpy"),
            ("PyQt5", "PyQt5"),
            ("matplotlib", "matplotlib"),
            ("scipy", "scipy"),
            ("pandas", "pandas"),
            ("pytest", "pytest")
        ]
        
        for dep_name, import_name in dependencies:
            try:
                __import__(import_name)
                env_info["available_modules"][dep_name] = True
            except ImportError:
                env_info["available_modules"][dep_name] = False
        
        return env_info
    
    def run_single_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a single test suite and return results."""
        suite_info = self.available_test_suites[suite_name]
        
        result = {
            "suite_name": suite_name,
            "description": suite_info["description"],
            "available": suite_info["available"],
            "start_time": None,
            "end_time": None,
            "duration": 0.0,
            "success": False,
            "error_message": None
        }
        
        if not suite_info["available"]:
            result["error_message"] = f"Test suite {suite_name} not available"
            return result
        
        if not suite_info["runner"]:
            result["error_message"] = f"Test runner for {suite_name} not found"
            return result
        
        print(f"\n🧪 Running {suite_name} test suite...")
        print(f"   Description: {suite_info['description']}")
        
        result["start_time"] = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            success = suite_info["runner"]()
            result["success"] = success
            
            if success:
                print(f"✅ {suite_name} tests PASSED")
            else:
                print(f"❌ {suite_name} tests FAILED")
                
        except Exception as e:
            result["success"] = False
            result["error_message"] = str(e)
            print(f"💥 {suite_name} tests ERROR: {e}")
        
        end_time = time.time()
        result["end_time"] = datetime.now().isoformat()
        result["duration"] = end_time - start_time
        
        return result
    
    def run_all_test_suites(self, filter_suites: List[str] = None) -> Dict[str, Any]:
        """Run all available test suites."""
        print("=" * 80)
        print("🚀 COMPREHENSIVE PYTHON TEST SUITE RUNNER")
        print("=" * 80)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📂 Working directory: {Path.cwd()}")
        
        # Show available test suites
        print(f"\n📋 Available test suites:")
        for suite_name, suite_info in self.available_test_suites.items():
            status = "✅ Available" if suite_info["available"] else "❌ Not Available"
            print(f"   {suite_name:20} - {status} - {suite_info['description']}")
        
        # Determine which suites to run
        if filter_suites:
            suites_to_run = [s for s in filter_suites if s in self.available_test_suites]
        else:
            suites_to_run = list(self.available_test_suites.keys())
        
        available_suites = [s for s in suites_to_run if self.available_test_suites[s]["available"]]
        
        print(f"\n🎯 Running {len(available_suites)} test suites...")
        
        # Run each test suite
        suite_results = {}
        overall_start_time = time.time()
        
        for suite_name in available_suites:
            suite_result = self.run_single_test_suite(suite_name)
            suite_results[suite_name] = suite_result
            self.results["test_suites"][suite_name] = suite_result
        
        overall_duration = time.time() - overall_start_time
        
        # Calculate summary statistics
        total_suites = len(suite_results)
        passed_suites = sum(1 for r in suite_results.values() if r["success"])
        failed_suites = total_suites - passed_suites
        success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
        
        summary = {
            "total_suites_run": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": failed_suites,
            "success_rate": success_rate,
            "total_duration": overall_duration,
            "overall_success": failed_suites == 0
        }
        
        self.results["overall_summary"] = summary
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for suite_name, result in suite_results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            duration = f"{result['duration']:.2f}s"
            print(f"   {suite_name:20} - {status:10} - {duration:8} - {result['description']}")
            
            if not result["success"] and result["error_message"]:
                print(f"      ⚠️  Error: {result['error_message']}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total test suites: {total_suites}")
        print(f"   Passed: {passed_suites}")
        print(f"   Failed: {failed_suites}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Total duration: {overall_duration:.2f} seconds")
        
        if summary["overall_success"]:
            print(f"\n🎉 ALL PYTHON TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️  SOME PYTHON TESTS FAILED - CHECK RESULTS ABOVE")
        
        # Save detailed results
        self._save_results()
        
        return self.results
    
    def _save_results(self) -> None:
        """Save test results to JSON file."""
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"python_comprehensive_tests_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")
    
    def generate_html_report(self) -> str:
        """Generate an HTML report of test results."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Python Comprehensive Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .test-suite {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .unavailable {{ background-color: #f0f0f0; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Python Comprehensive Test Results</h1>
        <p><strong>Generated:</strong> {self.results['test_run_timestamp']}</p>
        <p><strong>Python Version:</strong> {self.results['python_version'].split()[0]}</p>
        <p><strong>Working Directory:</strong> {self.results['working_directory']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Test Suites:</strong> {self.results['overall_summary']['total_suites_run']}</p>
        <p><strong>Passed:</strong> {self.results['overall_summary']['passed_suites']}</p>
        <p><strong>Failed:</strong> {self.results['overall_summary']['failed_suites']}</p>
        <p><strong>Success Rate:</strong> {self.results['overall_summary']['success_rate']:.1f}%</p>
        <p><strong>Total Duration:</strong> {self.results['overall_summary']['total_duration']:.2f} seconds</p>
    </div>
    
    <h2>Test Suite Results</h2>
    <table>
        <tr>
            <th>Test Suite</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Description</th>
        </tr>
"""
        
        for suite_name, result in self.results["test_suites"].items():
            status_class = "passed" if result["success"] else "failed"
            status_text = "PASSED" if result["success"] else "FAILED"
            duration = f"{result['duration']:.2f}s"
            
            html_content += f"""
        <tr class="{status_class}">
            <td>{suite_name}</td>
            <td>{status_text}</td>
            <td>{duration}</td>
            <td>{result['description']}</td>
        </tr>
"""
        
        html_content += """
    </table>
    
    <h2>Environment Information</h2>
    <table>
        <tr>
            <th>Module</th>
            <th>Available</th>
        </tr>
"""
        
        for module, available in self.results["environment_info"]["available_modules"].items():
            status = "Yes" if available else "No"
            status_class = "passed" if available else "failed"
            
            html_content += f"""
        <tr class="{status_class}">
            <td>{module}</td>
            <td>{status}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        # Save HTML report
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = results_dir / f"python_test_report_{timestamp}.html"
        
        try:
            with open(html_file, 'w') as f:
                f.write(html_content)
            print(f"📄 HTML report saved to: {html_file}")
            return str(html_file)
        except Exception as e:
            print(f"⚠️  Could not save HTML report: {e}")
            return ""


def main():
    """Main test runner entry point."""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Python Test Runner")
    parser.add_argument("--suites", nargs="*", 
                       help="Specific test suites to run (default: all available)")
    parser.add_argument("--html", action="store_true",
                       help="Generate HTML report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Create and run test runner
    runner = ComprehensiveTestRunner()
    results = runner.run_all_test_suites(filter_suites=args.suites)
    
    # Generate HTML report if requested
    if args.html:
        runner.generate_html_report()
    
    # Return appropriate exit code
    overall_success = results["overall_summary"]["overall_success"]
    return 0 if overall_success else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)