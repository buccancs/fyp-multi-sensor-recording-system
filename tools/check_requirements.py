#!/usr/bin/env python3
"""
Comprehensive Requirements Checker for Multi-Sensor Recording System

This script validates that all project requirements are met, including:
- Python dependencies
- System requirements
- Documentation requirements
- Data schema requirements
- Testing framework requirements

Usage:
    python tools/check_requirements.py [--fix] [--verbose]
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import importlib.util


class RequirementsChecker:
    """Comprehensive requirements validation for the multi-sensor recording system."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the requirements checker."""
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "python_dependencies": {},
            "system_requirements": {},
            "documentation": {},
            "data_schemas": {},
            "testing_framework": {},
            "overall_status": "UNKNOWN"
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with optional verbosity."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        self.log("Checking Python version...")
        
        import sys
        version = sys.version_info
        min_version = (3, 9)
        max_version = (3, 12)
        
        if version[:2] < min_version:
            self.results["python_dependencies"]["version"] = {
                "status": "FAIL",
                "current": f"{version.major}.{version.minor}.{version.micro}",
                "required": f">= {min_version[0]}.{min_version[1]}",
                "message": f"Python version {version.major}.{version.minor} is too old"
            }
            return False
        elif version[:2] > max_version:
            self.results["python_dependencies"]["version"] = {
                "status": "WARNING", 
                "current": f"{version.major}.{version.minor}.{version.micro}",
                "required": f"<= {max_version[0]}.{max_version[1]}",
                "message": f"Python version {version.major}.{version.minor} might be too new"
            }
            return True
        else:
            self.results["python_dependencies"]["version"] = {
                "status": "PASS",
                "current": f"{version.major}.{version.minor}.{version.micro}",
                "required": f"{min_version[0]}.{min_version[1]} - {max_version[0]}.{max_version[1]}"
            }
            return True
    
    def check_python_dependencies(self) -> bool:
        """Check Python package dependencies."""
        self.log("Checking Python dependencies...")
        
        # Core dependencies from pyproject.toml
        core_deps = {
            "PyQt5": "5.15.0",
            "opencv-python": "4.8.0", 
            "numpy": "1.24.0",
            "matplotlib": "3.7.0",
            "requests": "2.30.0",
            "pillow": "10.0.0",
            "scipy": "1.10.0",
            "pandas": "2.0.0",
            "websockets": "11.0.0"
        }
        
        # Optional dependencies
        optional_deps = {
            "pytest": "7.0.0",
            "pytest-cov": "4.0.0", 
            "black": "23.0.0",
            "isort": "5.12.0",
            "mypy": "1.0.0",
            "bandit": "1.7.0"
        }
        
        all_deps_ok = True
        
        for package, min_version in core_deps.items():
            try:
                # Try to import the package
                if package == "opencv-python":
                    import cv2
                    installed_version = cv2.__version__
                elif package == "PyQt5":
                    from PyQt5.QtCore import QT_VERSION_STR
                    installed_version = QT_VERSION_STR
                else:
                    module = importlib.import_module(package.lower().replace('-', '_'))
                    installed_version = getattr(module, '__version__', 'unknown')
                
                self.results["python_dependencies"][package] = {
                    "status": "PASS",
                    "installed_version": installed_version,
                    "required_version": f">= {min_version}"
                }
                self.log(f"✓ {package}: {installed_version}")
                
            except ImportError as e:
                self.results["python_dependencies"][package] = {
                    "status": "FAIL",
                    "installed_version": "NOT_INSTALLED",
                    "required_version": f">= {min_version}",
                    "error": str(e)
                }
                self.log(f"✗ {package}: NOT INSTALLED", "ERROR")
                all_deps_ok = False
        
        # Check optional dependencies
        for package, min_version in optional_deps.items():
            try:
                module = importlib.import_module(package.replace('-', '_'))
                installed_version = getattr(module, '__version__', 'unknown')
                
                self.results["python_dependencies"][f"{package}_optional"] = {
                    "status": "PASS",
                    "installed_version": installed_version,
                    "required_version": f">= {min_version}",
                    "optional": True
                }
                self.log(f"✓ {package} (optional): {installed_version}")
                
            except ImportError:
                self.results["python_dependencies"][f"{package}_optional"] = {
                    "status": "MISSING",
                    "installed_version": "NOT_INSTALLED", 
                    "required_version": f">= {min_version}",
                    "optional": True
                }
                self.log(f"- {package} (optional): NOT INSTALLED", "INFO")
        
        return all_deps_ok
    
    def check_system_requirements(self) -> bool:
        """Check system-level requirements."""
        self.log("Checking system requirements...")
        
        system_ok = True
        
        # Check Java (for Android development)
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                java_version = result.stderr.split('\n')[0]
                self.results["system_requirements"]["java"] = {
                    "status": "PASS",
                    "version": java_version
                }
                self.log(f"✓ Java: {java_version}")
            else:
                raise subprocess.CalledProcessError(result.returncode, 'java')
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.results["system_requirements"]["java"] = {
                "status": "FAIL",
                "version": "NOT_INSTALLED",
                "message": "Java required for Android development"
            }
            self.log("✗ Java: NOT INSTALLED", "ERROR")
            system_ok = False
        
        # Check Gradle
        try:
            gradlew_path = self.project_root / "gradlew"
            if gradlew_path.exists():
                self.results["system_requirements"]["gradle"] = {
                    "status": "PASS",
                    "version": "gradlew wrapper available"
                }
                self.log("✓ Gradle: wrapper available")
            else:
                raise FileNotFoundError("gradlew not found")
        except FileNotFoundError:
            self.results["system_requirements"]["gradle"] = {
                "status": "FAIL",
                "version": "NOT_FOUND",
                "message": "Gradle wrapper not found"
            }
            self.log("✗ Gradle: wrapper not found", "ERROR")
            system_ok = False
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                git_version = result.stdout.strip()
                self.results["system_requirements"]["git"] = {
                    "status": "PASS",
                    "version": git_version
                }
                self.log(f"✓ Git: {git_version}")
            else:
                raise subprocess.CalledProcessError(result.returncode, 'git')
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.results["system_requirements"]["git"] = {
                "status": "FAIL",
                "version": "NOT_INSTALLED"
            }
            self.log("✗ Git: NOT INSTALLED", "ERROR")
            system_ok = False
        
        return system_ok
    
    def check_documentation_requirements(self) -> bool:
        """Check that required documentation exists."""
        self.log("Checking documentation requirements...")
        
        required_docs = [
            "README.md",
            "docs/DOCUMENTATION_INDEX.md",
            "docs/user-guides/CONSOLIDATED_USER_GUIDE.md",
            "docs/implementation/CONSOLIDATED_IMPLEMENTATION_GUIDE.md",
            "docs/TESTING_QA_FRAMEWORK.md"
        ]
        
        docs_ok = True
        
        for doc_path in required_docs:
            full_path = self.project_root / doc_path
            if full_path.exists():
                # Check if document has reasonable content
                content = full_path.read_text()
                word_count = len(content.split())
                
                if word_count > 100:  # Minimum reasonable content
                    self.results["documentation"][doc_path] = {
                        "status": "PASS",
                        "word_count": word_count
                    }
                    self.log(f"✓ {doc_path}: {word_count} words")
                else:
                    self.results["documentation"][doc_path] = {
                        "status": "WARNING",
                        "word_count": word_count,
                        "message": "Document exists but has minimal content"
                    }
                    self.log(f"⚠ {doc_path}: minimal content ({word_count} words)", "WARNING")
            else:
                self.results["documentation"][doc_path] = {
                    "status": "FAIL",
                    "message": "Required documentation missing"
                }
                self.log(f"✗ {doc_path}: NOT FOUND", "ERROR")
                docs_ok = False
        
        return docs_ok
    
    def check_data_schemas(self) -> bool:
        """Check that data schemas exist and are valid."""
        self.log("Checking data schema requirements...")
        
        schema_dir = self.project_root / "docs" / "schemas"
        required_schemas = [
            "session_metadata_schema.json",
            "session_log_schema.json", 
            "calibration_session_schema.json",
            "processing_metadata_schema.json"
        ]
        
        schemas_ok = True
        
        if not schema_dir.exists():
            # Create schema directory and basic schemas if missing
            self.log("Creating missing schema directory...", "WARNING")
            schema_dir.mkdir(parents=True, exist_ok=True)
            schemas_ok = False
        
        for schema_file in required_schemas:
            schema_path = schema_dir / schema_file
            if schema_path.exists():
                try:
                    with open(schema_path, 'r') as f:
                        schema_data = json.load(f)
                    
                    # Basic validation that it's a JSON schema
                    if "$schema" in schema_data and "type" in schema_data:
                        self.results["data_schemas"][schema_file] = {
                            "status": "PASS",
                            "valid_json": True
                        }
                        self.log(f"✓ {schema_file}: valid schema")
                    else:
                        self.results["data_schemas"][schema_file] = {
                            "status": "WARNING",
                            "valid_json": True,
                            "message": "Missing standard JSON schema fields"
                        }
                        self.log(f"⚠ {schema_file}: missing schema fields", "WARNING")
                        
                except json.JSONDecodeError as e:
                    self.results["data_schemas"][schema_file] = {
                        "status": "FAIL",
                        "valid_json": False,
                        "error": str(e)
                    }
                    self.log(f"✗ {schema_file}: invalid JSON", "ERROR")
                    schemas_ok = False
            else:
                self.results["data_schemas"][schema_file] = {
                    "status": "FAIL",
                    "message": "Schema file missing"
                }
                self.log(f"✗ {schema_file}: NOT FOUND", "ERROR")
                schemas_ok = False
        
        return schemas_ok
    
    def check_testing_framework(self) -> bool:
        """Check that testing framework is properly set up."""
        self.log("Checking testing framework requirements...")
        
        required_tests = [
            "PythonApp/run_quick_recording_session_test.py",
            "PythonApp/test_calibration_implementation.py",
            "PythonApp/test_shimmer_implementation.py",
            "PythonApp/test_integration_logging.py"
        ]
        
        testing_ok = True
        
        for test_file in required_tests:
            test_path = self.project_root / test_file
            if test_path.exists():
                self.results["testing_framework"][test_file] = {
                    "status": "PASS"
                }
                self.log(f"✓ {test_file}: exists")
            else:
                self.results["testing_framework"][test_file] = {
                    "status": "FAIL",
                    "message": "Required test file missing"
                }
                self.log(f"✗ {test_file}: NOT FOUND", "ERROR")
                testing_ok = False
        
        # Check pytest configuration
        pytest_config = self.project_root / "pytest.ini"
        pyproject_toml = self.project_root / "pyproject.toml"
        
        if pytest_config.exists() or pyproject_toml.exists():
            self.results["testing_framework"]["pytest_config"] = {
                "status": "PASS"
            }
            self.log("✓ Pytest configuration: found")
        else:
            self.results["testing_framework"]["pytest_config"] = {
                "status": "WARNING",
                "message": "No pytest configuration found"
            }
            self.log("⚠ Pytest configuration: not found", "WARNING")
        
        return testing_ok
    
    def create_missing_schemas(self):
        """Create missing data schemas with basic structure."""
        self.log("Creating missing data schemas...")
        
        schema_dir = self.project_root / "docs" / "schemas"
        schema_dir.mkdir(parents=True, exist_ok=True)
        
        # Basic session metadata schema
        session_metadata_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Session Metadata Schema",
            "description": "Schema for recording session metadata",
            "required": ["session_id", "timestamp", "devices"],
            "properties": {
                "session_id": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "devices": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "duration": {"type": "number"},
                "status": {"type": "string", "enum": ["completed", "failed", "in_progress"]}
            }
        }
        
        # Basic session log schema
        session_log_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object", 
            "title": "Session Log Schema",
            "description": "Schema for session log entries",
            "required": ["timestamp", "level", "message"],
            "properties": {
                "timestamp": {"type": "string", "format": "date-time"},
                "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                "message": {"type": "string"},
                "source": {"type": "string"}
            }
        }
        
        # Basic calibration session schema
        calibration_session_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Calibration Session Schema", 
            "description": "Schema for camera calibration sessions",
            "required": ["session_info", "calibration_results"],
            "properties": {
                "session_info": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string", "format": "date-time"},
                        "camera_type": {"type": "string"}
                    }
                },
                "calibration_results": {
                    "type": "object",
                    "properties": {
                        "rms_error": {"type": "number"},
                        "camera_matrix": {"type": "array"},
                        "distortion_coefficients": {"type": "array"}
                    }
                }
            }
        }
        
        # Basic processing metadata schema
        processing_metadata_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Processing Metadata Schema",
            "description": "Schema for data processing metadata",
            "required": ["processing_timestamp", "input_files", "output_files"],
            "properties": {
                "processing_timestamp": {"type": "string", "format": "date-time"},
                "input_files": {"type": "array", "items": {"type": "string"}},
                "output_files": {"type": "array", "items": {"type": "string"}},
                "processing_parameters": {"type": "object"}
            }
        }
        
        schemas = {
            "session_metadata_schema.json": session_metadata_schema,
            "session_log_schema.json": session_log_schema,
            "calibration_session_schema.json": calibration_session_schema,
            "processing_metadata_schema.json": processing_metadata_schema
        }
        
        for filename, schema in schemas.items():
            schema_path = schema_dir / filename
            with open(schema_path, 'w') as f:
                json.dump(schema, f, indent=2)
            self.log(f"Created schema: {filename}")
    
    def run_all_checks(self, fix_missing: bool = False) -> bool:
        """Run all requirement checks."""
        self.log("Starting comprehensive requirements check...")
        
        # Run all checks
        python_version_ok = self.check_python_version()
        python_deps_ok = self.check_python_dependencies()
        system_ok = self.check_system_requirements()
        docs_ok = self.check_documentation_requirements()
        schemas_ok = self.check_data_schemas()
        testing_ok = self.check_testing_framework()
        
        # Fix missing schemas if requested
        if fix_missing and not schemas_ok:
            self.create_missing_schemas()
            schemas_ok = self.check_data_schemas()  # Re-check after creation
        
        # Calculate overall status
        all_checks = [python_version_ok, python_deps_ok, system_ok, docs_ok, schemas_ok, testing_ok]
        
        if all(all_checks):
            self.results["overall_status"] = "PASS"
            self.log("✅ All requirements met!", "INFO")
        elif any(all_checks):
            self.results["overall_status"] = "PARTIAL"
            self.log("⚠️ Some requirements not met", "WARNING")
        else:
            self.results["overall_status"] = "FAIL"
            self.log("❌ Multiple requirements not met", "ERROR")
        
        return self.results["overall_status"] == "PASS"
    
    def generate_report(self) -> str:
        """Generate a detailed requirements report."""
        report = []
        report.append("# Multi-Sensor Recording System - Requirements Check Report")
        report.append(f"**Overall Status: {self.results['overall_status']}**\n")
        
        # Python Dependencies
        report.append("## Python Dependencies")
        for dep, info in self.results["python_dependencies"].items():
            status_icon = "✅" if info["status"] == "PASS" else "❌" if info["status"] == "FAIL" else "⚠️"
            report.append(f"- {status_icon} **{dep}**: {info.get('installed_version', 'N/A')} {info.get('message', '')}")
        
        # System Requirements
        report.append("\n## System Requirements")
        for req, info in self.results["system_requirements"].items():
            status_icon = "✅" if info["status"] == "PASS" else "❌"
            report.append(f"- {status_icon} **{req}**: {info.get('version', 'N/A')} {info.get('message', '')}")
        
        # Documentation
        report.append("\n## Documentation")
        for doc, info in self.results["documentation"].items():
            status_icon = "✅" if info["status"] == "PASS" else "❌" if info["status"] == "FAIL" else "⚠️"
            word_count = f"({info['word_count']} words)" if 'word_count' in info else ""
            report.append(f"- {status_icon} **{doc}**: {word_count} {info.get('message', '')}")
        
        # Data Schemas
        report.append("\n## Data Schemas")
        for schema, info in self.results["data_schemas"].items():
            status_icon = "✅" if info["status"] == "PASS" else "❌" if info["status"] == "FAIL" else "⚠️"
            report.append(f"- {status_icon} **{schema}**: {info.get('message', 'OK')}")
        
        # Testing Framework
        report.append("\n## Testing Framework")
        for test, info in self.results["testing_framework"].items():
            status_icon = "✅" if info["status"] == "PASS" else "❌" if info["status"] == "FAIL" else "⚠️"
            report.append(f"- {status_icon} **{test}**: {info.get('message', 'OK')}")
        
        return "\n".join(report)
    
    def save_results(self, output_path: Optional[str] = None):
        """Save check results to JSON file."""
        if output_path is None:
            output_path = self.project_root / "requirements_check_results.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"Results saved to: {output_path}")


def main():
    """Main entry point for requirements checker."""
    parser = argparse.ArgumentParser(description="Check multi-sensor recording system requirements")
    parser.add_argument("--fix", action="store_true", help="Fix missing requirements where possible")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--report", help="Generate markdown report to file")
    
    args = parser.parse_args()
    
    checker = RequirementsChecker(verbose=args.verbose)
    
    print("🔍 Multi-Sensor Recording System - Requirements Check")
    print("=" * 60)
    
    success = checker.run_all_checks(fix_missing=args.fix)
    
    # Save results
    checker.save_results(args.output)
    
    # Generate report if requested
    if args.report:
        report = checker.generate_report()
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {args.report}")
    
    print("\n" + "=" * 60)
    print(f"Overall Status: {checker.results['overall_status']}")
    
    if success:
        print("🎉 All requirements are met!")
        return 0
    else:
        print("⚠️ Some requirements need attention. Use --fix to auto-fix where possible.")
        return 1


if __name__ == "__main__":
    sys.exit(main())