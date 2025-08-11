#!/usr/bin/env python3
"""
Simple System Validator

This module runs basic system tests without fake data generation.
All results come from actual test execution.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class SystemValidator:
    """Simple system validator using actual tests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
    def run_basic_validation(self) -> Dict[str, Any]:
        """Run basic system validation"""
        self.logger.info("Running basic system validation")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
        
        # Test 1: Check Python app
        python_test = self._run_test("PythonApp/system_test.py")
        results["tests"].append(python_test)
        
        # Test 2: Check consolidated tests if available
        consolidated_test = self._run_test("tests/consolidated_tests.py")
        if consolidated_test["found"]:
            results["tests"].append(consolidated_test)
        
        # Calculate summary
        total_tests = len([t for t in results["tests"] if t["found"]])
        passed_tests = len([t for t in results["tests"] if t["success"]])
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return results
    
    def _run_test(self, test_path: str) -> Dict[str, Any]:
        """Run a single test file"""
        test_file = Path(test_path)
        result = {
            "test_path": test_path,
            "found": test_file.exists(),
            "success": False,
            "output": "",
            "error": ""
        }
        
        if not test_file.exists():
            result["error"] = "Test file not found"
            return result
            
        try:
            proc = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout
            result["error"] = proc.stderr
            
        except subprocess.TimeoutExpired:
            result["error"] = "Test timed out"
        except Exception as e:
            result["error"] = str(e)
            
        return result
    
    def save_results(self, results: Dict[str, Any]) -> str:
        """Save validation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"validation_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        return str(results_file)


def main():
    """Main validation entry point"""
    logging.basicConfig(level=logging.INFO)
    
    validator = SystemValidator()
    results = validator.run_basic_validation()
    results_file = validator.save_results(results)
    
    print(f"Validation complete: {results_file}")
    print(f"Summary: {results['summary']['passed_tests']}/{results['summary']['total_tests']} tests passed")
    
    return 0 if results['summary']['passed_tests'] > 0 else 1


if __name__ == "__main__":
    exit(main())