#!/usr/bin/env python3
"""
Chapter 5 Evaluation and Testing - Validation Script

This script validates that the Chapter 5 testing requirements are implemented 
according to the problem statement specification.

Requirements validated:
5.1 Testing Strategy Overview
5.1.1 Multi-Level Testing Approach
5.1.2 Validation Methodology Framework 
5.2 Unit Testing (Android and PC Components) 
5.2.1 Android Component Testing
5.2.2 PC Component Testing
5.2.3 Algorithm Validation and Performance Testing
5.3 Integration Testing (Multi-Device Synchronization & Networking)
5.3.1 Multi-Device Coordination Testing
5.3.2 Network Performance and Reliability Testing
5.3.3 Synchronization Precision Validation
5.4 System Performance Evaluation 
5.4.1 Throughput and Scalability Assessment
5.4.2 Reliability and Fault Tolerance Evaluation
5.4.3 User Experience and Usability Evaluation
5.5 Results Analysis and Discussion 
5.5.1 Performance Validation Results
5.5.2 Reliability and Robustness Assessment 
5.5.3 Usability and Effectiveness Evaluation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class Chapter5Validator:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.python_app = self.repo_root / "PythonApp"
        self.android_app = self.repo_root / "AndroidApp"
        self.docs_path = self.repo_root / "docs" / "thesis_report"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "test_executions": {},
            "documentation_validation": {},
            "overall_compliance": False
        }
        
    def validate_documentation_structure(self):
        """Validate that Chapter 5 documentation follows the required structure."""
        print("📋 Validating Chapter 5 Documentation Structure...")
        
        chapter5_file = self.docs_path / "Chapter_5_Evaluation_and_Testing.md"
        
        if not chapter5_file.exists():
            print(f"❌ Chapter 5 file not found: {chapter5_file}")
            return False
            
        content = chapter5_file.read_text()
        
        # Required sections from problem statement
        required_sections = [
            "5.1 Testing Strategy Overview",
            "5.1.1 Multi-Level Testing Approach", 
            "5.1.2 Validation Methodology Framework",
            "5.2 Unit Testing (Android and PC Components)",
            "5.2.1 Android Component Testing",
            "5.2.2 PC Component Testing", 
            "5.2.3 Algorithm Validation and Performance Testing",
            "5.3 Integration Testing (Multi-Device Synchronization & Networking)",
            "5.3.1 Multi-Device Coordination Testing",
            "5.3.2 Network Performance and Reliability Testing",
            "5.3.3 Synchronization Precision Validation",
            "5.4 System Performance Evaluation",
            "5.4.1 Throughput and Scalability Assessment",
            "5.4.2 Reliability and Fault Tolerance Evaluation", 
            "5.4.3 User Experience and Usability Evaluation",
            "5.5 Results Analysis and Discussion",
            "5.5.1 Performance Validation Results",
            "5.5.2 Reliability and Robustness Assessment",
            "5.5.3 Usability and Effectiveness Evaluation"
        ]
        
        missing_sections = []
        found_sections = []
        
        for section in required_sections:
            if section in content:
                found_sections.append(section)
                print(f"  ✅ Found: {section}")
            else:
                missing_sections.append(section)
                print(f"  ❌ Missing: {section}")
        
        self.results["documentation_validation"] = {
            "chapter5_exists": True,
            "required_sections": len(required_sections),
            "found_sections": len(found_sections),
            "missing_sections": missing_sections,
            "compliance_percentage": (len(found_sections) / len(required_sections)) * 100
        }
        
        compliance = len(missing_sections) == 0
        print(f"📊 Documentation Compliance: {len(found_sections)}/{len(required_sections)} sections ({self.results['documentation_validation']['compliance_percentage']:.1f}%)")
        return compliance
        
    def validate_unit_testing_framework(self):
        """Validate unit testing implementation (5.2)."""
        print("\n🧪 Validating Unit Testing Framework...")
        
        # Check for Python test files
        python_tests = list(self.python_app.glob("test_*.py"))
        print(f"  📁 Python test files found: {len(python_tests)}")
        
        # Check for Android test files  
        android_test_dirs = [
            self.android_app / "src" / "test" / "java",
            self.android_app / "src" / "androidTest" / "java"
        ]
        
        android_tests = []
        for test_dir in android_test_dirs:
            if test_dir.exists():
                android_tests.extend(list(test_dir.rglob("*Test.kt")))
        
        print(f"  📁 Android test files found: {len(android_tests)}")
        
        # Test execution validation
        test_executions = {}
        
        # Run a representative Python test
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.python_app / "run_quick_recording_session_test.py")
            ], capture_output=True, text=True, timeout=60, cwd=self.python_app)
            
            test_executions["python_quick_test"] = {
                "success": result.returncode == 0,
                "stdout_lines": len(result.stdout.splitlines()),
                "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0
            }
            print(f"  ✅ Python quick test: {'PASS' if result.returncode == 0 else 'FAIL'}")
            
        except Exception as e:
            test_executions["python_quick_test"] = {"success": False, "error": str(e)}
            print(f"  ❌ Python quick test failed: {e}")
        
        self.results["test_executions"] = test_executions
        
        # Algorithm validation check
        algo_tests = [f for f in python_tests if "calibration" in f.name.lower() or "algorithm" in f.name.lower()]
        print(f"  🧮 Algorithm validation tests: {len(algo_tests)}")
        
        return len(python_tests) > 0 and len(android_tests) > 0
        
    def validate_integration_testing_framework(self):
        """Validate integration testing implementation (5.3)."""
        print("\n🔗 Validating Integration Testing Framework...")
        
        # Check for integration test files
        integration_tests = [
            f for f in self.python_app.glob("test_*.py") 
            if any(keyword in f.name.lower() for keyword in [
                "integration", "network", "multi", "sync", "coordination"
            ])
        ]
        
        print(f"  📁 Integration test files: {len(integration_tests)}")
        for test in integration_tests:
            print(f"    • {test.name}")
        
        # Run integration test
        try:
            result = subprocess.run([
                sys.executable,
                str(self.python_app / "test_integration_logging.py")
            ], capture_output=True, text=True, timeout=60, cwd=self.python_app)
            
            integration_success = result.returncode == 0
            print(f"  ✅ Integration test execution: {'PASS' if integration_success else 'FAIL'}")
            
        except Exception as e:
            integration_success = False
            print(f"  ❌ Integration test failed: {e}")
        
        # Multi-device coordination validation
        multi_device_tests = [f for f in integration_tests if "multi" in f.name.lower()]
        print(f"  📱 Multi-device tests: {len(multi_device_tests)}")
        
        # Network performance validation
        network_tests = [f for f in integration_tests if "network" in f.name.lower()]
        print(f"  🌐 Network performance tests: {len(network_tests)}")
        
        # Synchronization precision validation
        sync_tests = [f for f in integration_tests if "sync" in f.name.lower()]
        print(f"  ⏱️  Synchronization tests: {len(sync_tests)}")
        
        return len(integration_tests) > 0 and integration_success
        
    def validate_performance_evaluation_framework(self):
        """Validate system performance evaluation implementation (5.4)."""
        print("\n📊 Validating Performance Evaluation Framework...")
        
        # Check for performance test files
        performance_tests = [
            f for f in self.python_app.glob("test_*.py")
            if any(keyword in f.name.lower() for keyword in [
                "performance", "stress", "benchmark", "scalability", "reliability"
            ])
        ]
        
        print(f"  📁 Performance test files: {len(performance_tests)}")
        for test in performance_tests:
            print(f"    • {test.name}")
        
        # Run performance test
        try:
            result = subprocess.run([
                sys.executable,
                str(self.python_app / "test_hardware_sensor_simulation.py")
            ], capture_output=True, text=True, timeout=90, cwd=self.python_app)
            
            perf_success = result.returncode == 0
            print(f"  ✅ Performance test execution: {'PASS' if perf_success else 'FAIL'}")
            
        except Exception as e:
            perf_success = False
            print(f"  ❌ Performance test failed: {e}")
        
        # Throughput and scalability assessment
        throughput_tests = [f for f in performance_tests if "stress" in f.name.lower() or "enhanced" in f.name.lower()]
        print(f"  🚀 Throughput/scalability tests: {len(throughput_tests)}")
        
        # Reliability and fault tolerance evaluation
        reliability_tests = [f for f in performance_tests if "reliability" in f.name.lower() or "fault" in f.name.lower()]
        print(f"  🛡️  Reliability tests: {len(reliability_tests)}")
        
        return len(performance_tests) > 0 and perf_success
        
    def validate_results_analysis_framework(self):
        """Validate results analysis and discussion implementation (5.5)."""
        print("\n📈 Validating Results Analysis Framework...")
        
        # Check for test result files
        result_files = list(self.python_app.glob("*results*.json"))
        log_files = list(self.python_app.glob("logs/*.log")) if (self.python_app / "logs").exists() else []
        
        print(f"  📊 Test result files: {len(result_files)}")
        print(f"  📝 Log files: {len(log_files)}")
        
        # Check for analysis scripts
        analysis_scripts = [
            f for f in self.python_app.glob("*.py")
            if any(keyword in f.name.lower() for keyword in [
                "summary", "analysis", "report", "comprehensive"
            ])
        ]
        
        print(f"  📋 Analysis scripts: {len(analysis_scripts)}")
        for script in analysis_scripts:
            print(f"    • {script.name}")
        
        # Validate testing QA framework exists
        qa_framework = self.repo_root / "docs" / "TESTING_QA_FRAMEWORK.md"
        qa_exists = qa_framework.exists()
        print(f"  📖 QA Framework documentation: {'EXISTS' if qa_exists else 'MISSING'}")
        
        return len(analysis_scripts) > 0 and qa_exists
        
    def validate_test_configuration(self):
        """Validate test configuration files."""
        print("\n⚙️  Validating Test Configuration...")
        
        config_files = {
            "pytest.ini": self.repo_root / "pytest.ini",
            "pyproject.toml": self.repo_root / "pyproject.toml", 
            "test-requirements.txt": self.repo_root / "test-requirements.txt"
        }
        
        for name, path in config_files.items():
            exists = path.exists()
            print(f"  📄 {name}: {'EXISTS' if exists else 'MISSING'}")
            
        return any(path.exists() for path in config_files.values())
        
    def generate_compliance_report(self):
        """Generate final compliance report."""
        print("\n" + "="*60)
        print("📋 CHAPTER 5 EVALUATION AND TESTING - COMPLIANCE REPORT")
        print("="*60)
        
        validations = {
            "Documentation Structure": self.validate_documentation_structure(),
            "Unit Testing Framework": self.validate_unit_testing_framework(),
            "Integration Testing": self.validate_integration_testing_framework(), 
            "Performance Evaluation": self.validate_performance_evaluation_framework(),
            "Results Analysis": self.validate_results_analysis_framework(),
            "Test Configuration": self.validate_test_configuration()
        }
        
        self.results["validation_results"] = validations
        
        passed = sum(validations.values())
        total = len(validations)
        compliance_percentage = (passed / total) * 100
        
        print(f"\n📊 VALIDATION SUMMARY:")
        for name, result in validations.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {name}: {status}")
        
        print(f"\n🎯 OVERALL COMPLIANCE: {passed}/{total} ({compliance_percentage:.1f}%)")
        
        if compliance_percentage >= 80:
            print("🎉 Chapter 5 requirements are substantially implemented!")
            self.results["overall_compliance"] = True
        elif compliance_percentage >= 60:
            print("⚠️  Chapter 5 requirements are partially implemented.")
        else:
            print("❌ Chapter 5 requirements need significant work.")
            
        # Save results
        results_file = self.repo_root / "chapter5_validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📁 Detailed results saved to: {results_file}")
        
        return self.results["overall_compliance"]

def main():
    """Main validation function."""
    print("🚀 Starting Chapter 5 Evaluation and Testing Validation...")
    print(f"📂 Repository: {Path(__file__).parent}")
    
    validator = Chapter5Validator()
    success = validator.generate_compliance_report()
    
    print("\n" + "="*60)
    if success:
        print("✅ Chapter 5 validation PASSED - Requirements substantially met!")
        return 0
    else:
        print("❌ Chapter 5 validation FAILED - Requirements not fully met.")
        return 1

if __name__ == "__main__":
    sys.exit(main())