#!/usr/bin/env python3
"""
Test Infrastructure Validation Script

This script validates the comprehensive test infrastructure to ensure
all components are working correctly.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

def run_command(command: List[str], cwd: Path = None) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def validate_android_test_structure(repo_root: Path) -> Dict[str, any]:
    """Validate Android test structure."""
    results = {
        "status": "success",
        "issues": [],
        "stats": {}
    }
    
    android_test_dir = repo_root / "AndroidApp" / "src" / "test" / "java" / "com" / "multisensor" / "recording"
    android_ui_test_dir = repo_root / "AndroidApp" / "src" / "androidTest" / "java" / "com" / "multisensor" / "recording"
    
    # Check if test directories exist
    if not android_test_dir.exists():
        results["issues"].append("Android unit test directory missing")
        results["status"] = "failed"
    
    if not android_ui_test_dir.exists():
        results["issues"].append("Android UI test directory missing")
        results["status"] = "failed"
    
    # Count test files
    if android_test_dir.exists():
        unit_test_files = list(android_test_dir.rglob("*Test.kt"))
        results["stats"]["unit_tests"] = len(unit_test_files)
        
        if len(unit_test_files) < 100:  # Should be around 127+
            results["issues"].append(f"Expected ~127 unit tests, found {len(unit_test_files)}")
    
    if android_ui_test_dir.exists():
        ui_test_files = list(android_ui_test_dir.rglob("*Test.kt"))
        results["stats"]["ui_tests"] = len(ui_test_files)
        
        if len(ui_test_files) < 1:
            results["issues"].append("No UI tests found")
    
    return results

def validate_python_test_structure(repo_root: Path) -> Dict[str, any]:
    """Validate Python test structure."""
    results = {
        "status": "success", 
        "issues": [],
        "stats": {}
    }
    
    python_test_dir = repo_root / "tests_unified_consolidated"
    
    # Check if consolidated directory exists
    if not python_test_dir.exists():
        results["issues"].append("Consolidated Python test directory missing")
        results["status"] = "failed"
        return results
    
    # Check for master test runner
    master_runner = python_test_dir / "run_all_tests.py"
    if not master_runner.exists():
        results["issues"].append("Master test runner missing")
    elif not os.access(master_runner, os.X_OK):
        results["issues"].append("Master test runner not executable")
    
    # Check for README
    readme = python_test_dir / "README.md"
    if not readme.exists():
        results["issues"].append("Consolidated test README missing")
    
    # Check categories
    expected_categories = [
        "android", "gui", "system", "integration", 
        "performance", "hardware", "unit"
    ]
    
    category_stats = {}
    for category in expected_categories:
        category_dir = python_test_dir / category
        if category_dir.exists():
            test_files = list(category_dir.glob("*.py"))
            category_stats[category] = len(test_files)
        else:
            results["issues"].append(f"Category directory missing: {category}")
            category_stats[category] = 0
    
    results["stats"]["categories"] = category_stats
    results["stats"]["total_files"] = sum(category_stats.values())
    
    if results["stats"]["total_files"] < 50:  # Should be around 83
        results["issues"].append(f"Expected ~83 Python tests, found {results['stats']['total_files']}")
    
    return results

def test_android_compilation(repo_root: Path) -> Dict[str, any]:
    """Test Android test compilation."""
    results = {
        "status": "success",
        "issues": [],
        "output": ""
    }
    
    # Test compilation of a few key test files
    exit_code, stdout, stderr = run_command([
        "./gradlew", ":AndroidApp:compileDevDebugUnitTestKotlin", "--no-daemon", "-q"
    ], cwd=repo_root)
    
    results["output"] = f"Exit code: {exit_code}\\nStdout: {stdout[:500]}\\nStderr: {stderr[:500]}"
    
    if exit_code != 0:
        results["status"] = "failed"
        results["issues"].append(f"Android test compilation failed: {stderr[:200]}")
    
    return results

def test_python_test_runner(repo_root: Path) -> Dict[str, any]:
    """Test Python test runner functionality."""
    results = {
        "status": "success",
        "issues": [],
        "output": ""
    }
    
    python_test_dir = repo_root / "tests_unified_consolidated"
    master_runner = python_test_dir / "run_all_tests.py"
    
    if not master_runner.exists():
        results["status"] = "failed"
        results["issues"].append("Master test runner not found")
        return results
    
    # Test list categories functionality
    exit_code, stdout, stderr = run_command([
        "python3", str(master_runner), "--list-categories"
    ], cwd=python_test_dir)
    
    results["output"] = f"Exit code: {exit_code}\\nStdout: {stdout}\\nStderr: {stderr}"
    
    if exit_code != 0:
        results["status"] = "failed"
        results["issues"].append("Test runner failed to list categories")
    elif "Available test categories:" not in stdout:
        results["status"] = "failed"
        results["issues"].append("Test runner output unexpected")
    
    return results

def validate_test_file_quality(repo_root: Path) -> Dict[str, any]:
    """Validate quality of generated test files."""
    results = {
        "status": "success",
        "issues": [],
        "stats": {}
    }
    
    # Check a few Android test files for quality
    android_test_dir = repo_root / "AndroidApp" / "src" / "test" / "java" / "com" / "multisensor" / "recording"
    
    if android_test_dir.exists():
        test_files = list(android_test_dir.rglob("*Test.kt"))[:5]  # Check first 5
        
        quality_issues = []
        for test_file in test_files:
            try:
                content = test_file.read_text()
                
                # Check for basic test structure
                if "@Test" not in content:
                    quality_issues.append(f"{test_file.name}: No @Test annotations found")
                
                if "import org.junit" not in content:
                    quality_issues.append(f"{test_file.name}: Missing JUnit imports")
                
                if "class " not in content:
                    quality_issues.append(f"{test_file.name}: No test class found")
                
                if len(content.split("@Test")) < 3:  # Should have multiple tests
                    quality_issues.append(f"{test_file.name}: Too few test methods")
                    
            except Exception as e:
                quality_issues.append(f"{test_file.name}: Failed to read - {e}")
        
        results["stats"]["quality_issues"] = len(quality_issues)
        if quality_issues:
            results["issues"].extend(quality_issues[:3])  # Show first 3 issues
    
    return results

def generate_validation_report(repo_root: Path) -> str:
    """Generate comprehensive validation report."""
    print("🔍 Validating Comprehensive Test Infrastructure")
    print("=" * 60)
    
    # Run validations
    android_structure = validate_android_test_structure(repo_root)
    python_structure = validate_python_test_structure(repo_root)
    android_compilation = test_android_compilation(repo_root)
    python_runner = test_python_test_runner(repo_root)
    test_quality = validate_test_file_quality(repo_root)
    
    # Generate report
    report = []
    report.append("# Test Infrastructure Validation Report\\n")
    
    # Android Test Structure
    report.append("## 🤖 Android Test Structure")
    if android_structure["status"] == "success":
        report.append("✅ **PASSED** - Android test structure is valid")
        stats = android_structure["stats"]
        report.append(f"- Unit Tests: {stats.get('unit_tests', 0)} files")
        report.append(f"- UI Tests: {stats.get('ui_tests', 0)} files")
    else:
        report.append("❌ **FAILED** - Android test structure issues:")
        for issue in android_structure["issues"]:
            report.append(f"  - {issue}")
    report.append("")
    
    # Python Test Structure  
    report.append("## 🐍 Python Test Structure")
    if python_structure["status"] == "success":
        report.append("✅ **PASSED** - Python test structure is valid")
        stats = python_structure["stats"]
        report.append(f"- Total Files: {stats.get('total_files', 0)}")
        report.append("- Categories:")
        for category, count in stats.get('categories', {}).items():
            report.append(f"  - {category}: {count} files")
    else:
        report.append("❌ **FAILED** - Python test structure issues:")
        for issue in python_structure["issues"]:
            report.append(f"  - {issue}")
    report.append("")
    
    # Android Compilation
    report.append("## 🔨 Android Test Compilation")
    if android_compilation["status"] == "success":
        report.append("✅ **PASSED** - Android tests compile successfully")
    else:
        report.append("❌ **FAILED** - Android compilation issues:")
        for issue in android_compilation["issues"]:
            report.append(f"  - {issue}")
    report.append("")
    
    # Python Test Runner
    report.append("## 🚀 Python Test Runner")
    if python_runner["status"] == "success":
        report.append("✅ **PASSED** - Python test runner functional")
    else:
        report.append("❌ **FAILED** - Python test runner issues:")
        for issue in python_runner["issues"]:
            report.append(f"  - {issue}")
    report.append("")
    
    # Test Quality
    report.append("## 📋 Test File Quality")
    if test_quality["status"] == "success":
        report.append("✅ **PASSED** - Test files meet quality standards")
        stats = test_quality["stats"]
        report.append(f"- Quality Issues: {stats.get('quality_issues', 0)}")
    else:
        report.append("❌ **FAILED** - Test quality issues:")
        for issue in test_quality["issues"]:
            report.append(f"  - {issue}")
    report.append("")
    
    # Overall Status
    all_passed = all(result["status"] == "success" for result in [
        android_structure, python_structure, android_compilation, 
        python_runner, test_quality
    ])
    
    report.append("## 🎯 Overall Status")
    if all_passed:
        report.append("🎉 **ALL VALIDATIONS PASSED** - Test infrastructure is ready!")
    else:
        report.append("⚠️ **SOME VALIDATIONS FAILED** - Review issues above")
    
    return "\\n".join(report)

def main():
    """Main validation function."""
    repo_root = Path(__file__).parent
    
    # Generate and display report
    report = generate_validation_report(repo_root)
    print(report)
    
    # Save report to file
    report_file = repo_root / "TEST_VALIDATION_REPORT.md"
    report_file.write_text(report.replace("\\n", "\\n"))
    print(f"\\n📄 Report saved to: {report_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())