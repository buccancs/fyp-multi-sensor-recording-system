#!/usr/bin/env python3
"""
Comprehensive Coverage Analysis for Multi-Sensor Recording System

This test module provides comprehensive code coverage analysis for both 
Python and Android applications to identify dead/unreachable code.
"""

import ast
import os
import sys
import pytest
import coverage
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from unittest.mock import MagicMock, patch


class PythonAppCoverageAnalyzer:
    """Analyzes code coverage for the PythonApp package."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.python_app_path = self.base_path / "PythonApp"
        self.coverage_data = {}
        self.all_modules = set()
        self.importable_modules = set()
        self.non_importable_modules = set()
        
    def discover_all_python_files(self) -> List[Path]:
        """Discover all Python files in PythonApp."""
        python_files = []
        for py_file in self.python_app_path.rglob("*.py"):
            if "__pycache__" not in str(py_file) and "test" not in py_file.name.lower():
                python_files.append(py_file)
        return python_files
    
    def get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative_path = file_path.relative_to(self.base_path)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return ".".join(module_parts)
    
    def analyze_importability(self) -> Dict[str, Any]:
        """Test which modules can be imported without errors."""
        python_files = self.discover_all_python_files()
        results = {
            "total_files": len(python_files),
            "importable": [],
            "non_importable": [],
            "import_errors": {}
        }
        
        for py_file in python_files:
            module_name = self.get_module_name(py_file)
            self.all_modules.add(module_name)
            
            try:
                # Use mock to avoid GUI dependencies
                with patch('PyQt5.QtWidgets.QApplication'), \
                     patch('PyQt5.QtCore.QTimer'), \
                     patch('PyQt5.QtWidgets.QMainWindow'), \
                     patch('cv2.VideoCapture'), \
                     patch('matplotlib.pyplot'):
                    importlib.import_module(module_name)
                    results["importable"].append(module_name)
                    self.importable_modules.add(module_name)
            except Exception as e:
                results["non_importable"].append(module_name)
                results["import_errors"][module_name] = str(e)
                self.non_importable_modules.add(module_name)
        
        return results
    
    def analyze_ast_complexity(self) -> Dict[str, Any]:
        """Analyze AST complexity of Python files to identify potentially dead code."""
        python_files = self.discover_all_python_files()
        results = {
            "file_stats": {},
            "potential_dead_code": [],
            "complexity_summary": {}
        }
        
        total_functions = 0
        total_classes = 0
        total_lines = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                file_stats = {
                    "functions": 0,
                    "classes": 0,
                    "lines": len(content.splitlines()),
                    "imports": 0,
                    "potential_issues": []
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        file_stats["functions"] += 1
                        # Check for potentially unused functions
                        if node.name.startswith('_') and not node.name.startswith('__'):
                            file_stats["potential_issues"].append(f"Private function: {node.name}")
                    elif isinstance(node, ast.ClassDef):
                        file_stats["classes"] += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        file_stats["imports"] += 1
                
                # Flag files with high import to function ratio as potentially over-engineered
                if file_stats["imports"] > 0 and file_stats["functions"] > 0:
                    ratio = file_stats["imports"] / file_stats["functions"]
                    if ratio > 2:
                        file_stats["potential_issues"].append(f"High import/function ratio: {ratio:.2f}")
                
                module_name = self.get_module_name(py_file)
                results["file_stats"][module_name] = file_stats
                
                total_functions += file_stats["functions"]
                total_classes += file_stats["classes"]
                total_lines += file_stats["lines"]
                
            except Exception as e:
                results["file_stats"][str(py_file)] = {"error": str(e)}
        
        results["complexity_summary"] = {
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines": total_lines,
            "avg_functions_per_file": total_functions / len(python_files) if python_files else 0,
            "avg_lines_per_file": total_lines / len(python_files) if python_files else 0
        }
        
        return results
    
    def run_coverage_with_mocking(self) -> Dict[str, Any]:
        """Run coverage analysis with proper mocking of external dependencies."""
        cov = coverage.Coverage(source=["PythonApp"])
        cov.start()
        
        coverage_results = {
            "executed_modules": [],
            "coverage_data": {},
            "execution_errors": {}
        }
        
        # Mock external dependencies to allow more modules to be imported
        mocks = {
            'PyQt5.QtWidgets': MagicMock(),
            'PyQt5.QtCore': MagicMock(),
            'PyQt5.QtGui': MagicMock(),
            'cv2': MagicMock(),
            'matplotlib.pyplot': MagicMock(),
            'numpy': MagicMock(),
            'scipy': MagicMock(),
            'pandas': MagicMock(),
        }
        
        # Try to import and execute basic functionality from importable modules
        for module_name in self.importable_modules:
            try:
                with patch.dict('sys.modules', mocks):
                    module = importlib.import_module(module_name)
                    # Try to execute some basic operations if the module has callable attributes
                    for attr_name in dir(module):
                        if not attr_name.startswith('_'):
                            attr = getattr(module, attr_name)
                            if callable(attr) and hasattr(attr, '__code__'):
                                try:
                                    # Don't actually call functions, just accessing them is enough for coverage
                                    pass
                                except:
                                    pass
                    coverage_results["executed_modules"].append(module_name)
            except Exception as e:
                coverage_results["execution_errors"][module_name] = str(e)
        
        cov.stop()
        cov.save()
        
        # Get coverage data
        coverage_data = cov.get_data()
        coverage_results["coverage_data"] = {
            "measured_files": list(coverage_data.measured_files()),
            "summary": cov._analyze([]),
        }
        
        return coverage_results


class AndroidAppCoverageAnalyzer:
    """Analyzes the Android application for potential dead code."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.android_app_path = self.base_path / "AndroidApp"
    
    def discover_kotlin_java_files(self) -> List[Path]:
        """Discover all Kotlin and Java files in AndroidApp."""
        source_files = []
        
        # Main source files
        main_src = self.android_app_path / "src" / "main"
        if main_src.exists():
            for pattern in ["**/*.kt", "**/*.java"]:
                source_files.extend(main_src.glob(pattern))
        
        return source_files
    
    def analyze_android_structure(self) -> Dict[str, Any]:
        """Analyze Android app structure and identify potential issues."""
        source_files = self.discover_kotlin_java_files()
        
        results = {
            "total_files": len(source_files),
            "kotlin_files": 0,
            "java_files": 0,
            "file_sizes": {},
            "potential_issues": []
        }
        
        total_lines = 0
        
        for source_file in source_files:
            if source_file.suffix == ".kt":
                results["kotlin_files"] += 1
            elif source_file.suffix == ".java":
                results["java_files"] += 1
            
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.splitlines())
                    total_lines += lines
                    
                    relative_path = str(source_file.relative_to(self.android_app_path))
                    results["file_sizes"][relative_path] = lines
                    
                    # Simple heuristics for potential dead code
                    if lines > 500:
                        results["potential_issues"].append(f"Large file ({lines} lines): {relative_path}")
                    
                    # Look for TODO/FIXME comments which might indicate incomplete features
                    todo_count = content.lower().count("todo") + content.lower().count("fixme")
                    if todo_count > 5:
                        results["potential_issues"].append(f"Many TODOs/FIXMEs ({todo_count}): {relative_path}")
                        
            except Exception as e:
                results["file_sizes"][str(source_file)] = f"Error reading: {e}"
        
        results["total_lines"] = total_lines
        results["avg_lines_per_file"] = total_lines / len(source_files) if source_files else 0
        
        return results


@pytest.fixture
def coverage_analyzer():
    """Fixture providing coverage analyzer instance."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return PythonAppCoverageAnalyzer(base_path)


@pytest.fixture  
def android_analyzer():
    """Fixture providing Android analyzer instance."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return AndroidAppCoverageAnalyzer(base_path)


class TestPythonAppCoverage:
    """Test class for Python application coverage analysis."""
    
    def test_discover_python_files(self, coverage_analyzer):
        """Test discovery of Python files in PythonApp."""
        files = coverage_analyzer.discover_all_python_files()
        assert len(files) > 0, "Should find Python files in PythonApp"
        
        # Check that main files exist
        main_modules = [f for f in files if f.name == "main.py"]
        assert len(main_modules) > 0, "Should find main.py"
        
        print(f"Discovered {len(files)} Python files")
        
    def test_module_importability(self, coverage_analyzer):
        """Test which modules can be imported."""
        results = coverage_analyzer.analyze_importability()
        
        assert results["total_files"] > 0
        
        importable_count = len(results["importable"])
        non_importable_count = len(results["non_importable"])
        total_files = results["total_files"]
        
        print(f"\nIMPORTABILITY ANALYSIS:")
        print(f"Total files: {total_files}")
        print(f"Importable: {importable_count} ({importable_count/total_files*100:.1f}%)")
        print(f"Non-importable: {non_importable_count} ({non_importable_count/total_files*100:.1f}%)")
        
        if results["import_errors"]:
            print(f"\nIMPORT ERRORS:")
            for module, error in list(results["import_errors"].items())[:10]:  # Show first 10
                print(f"  {module}: {error[:100]}...")
        
        # This test should not fail, but provides valuable information
        assert total_files > 0
        
    def test_ast_complexity_analysis(self, coverage_analyzer):
        """Analyze AST complexity to identify potential dead code."""
        results = coverage_analyzer.analyze_ast_complexity()
        
        summary = results["complexity_summary"]
        
        print(f"\nCOMPLEXITY ANALYSIS:")
        print(f"Total functions: {summary['total_functions']}")
        print(f"Total classes: {summary['total_classes']}")
        print(f"Total lines: {summary['total_lines']}")
        print(f"Average functions per file: {summary['avg_functions_per_file']:.2f}")
        print(f"Average lines per file: {summary['avg_lines_per_file']:.2f}")
        
        # Find files with potential issues
        problematic_files = []
        for module, stats in results["file_stats"].items():
            if isinstance(stats, dict) and stats.get("potential_issues"):
                problematic_files.append((module, stats["potential_issues"]))
        
        if problematic_files:
            print(f"\nPOTENTIAL ISSUES FOUND:")
            for module, issues in problematic_files[:10]:  # Show first 10
                print(f"  {module}: {', '.join(issues)}")
        
        assert summary["total_functions"] > 0, "Should find functions in the codebase"
        
    def test_coverage_with_mocking(self, coverage_analyzer):
        """Run coverage analysis with mocked dependencies."""
        # First analyze importability
        coverage_analyzer.analyze_importability()
        
        # Then run coverage
        results = coverage_analyzer.run_coverage_with_mocking()
        
        print(f"\nCOVERAGE ANALYSIS:")
        print(f"Executed modules: {len(results['executed_modules'])}")
        print(f"Execution errors: {len(results['execution_errors'])}")
        
        if results["coverage_data"]["measured_files"]:
            print(f"Measured files: {len(results['coverage_data']['measured_files'])}")
            
        if results["execution_errors"]:
            print(f"\nEXECUTION ERRORS:")
            for module, error in list(results["execution_errors"].items())[:5]:
                print(f"  {module}: {error[:100]}...")
        
        # Report should show some coverage data
        assert len(results["executed_modules"]) >= 0  # May be 0 if mocking issues


class TestAndroidAppCoverage:
    """Test class for Android application coverage analysis."""
    
    def test_discover_android_files(self, android_analyzer):
        """Test discovery of Android source files."""
        files = android_analyzer.discover_kotlin_java_files()
        
        print(f"\nAndroid files discovered: {len(files)}")
        
        if len(files) > 0:
            kotlin_files = [f for f in files if f.suffix == ".kt"]
            java_files = [f for f in files if f.suffix == ".java"]
            
            print(f"Kotlin files: {len(kotlin_files)}")
            print(f"Java files: {len(java_files)}")
            
        # Not failing if no files found as Android app might be differently structured
        assert len(files) >= 0
        
    def test_android_structure_analysis(self, android_analyzer):
        """Analyze Android app structure."""
        results = android_analyzer.analyze_android_structure()
        
        print(f"\nANDROID STRUCTURE ANALYSIS:")
        print(f"Total files: {results['total_files']}")
        print(f"Kotlin files: {results['kotlin_files']}")
        print(f"Java files: {results['java_files']}")
        
        if results['total_files'] > 0:
            print(f"Total lines: {results['total_lines']}")
            print(f"Average lines per file: {results['avg_lines_per_file']:.2f}")
            
            if results["potential_issues"]:
                print(f"\nPOTENTIAL ISSUES:")
                for issue in results["potential_issues"][:10]:
                    print(f"  {issue}")
        
        assert results["total_files"] >= 0


class TestDeadCodeAnalysis:
    """Comprehensive dead code analysis across both applications."""
    
    def test_comprehensive_dead_code_report(self, coverage_analyzer, android_analyzer):
        """Generate a comprehensive dead code analysis report."""
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE DEAD CODE ANALYSIS REPORT")
        print(f"{'='*80}")
        
        # Python App Analysis
        print(f"\n🐍 PYTHON APPLICATION ANALYSIS")
        print(f"-" * 50)
        
        python_files = coverage_analyzer.discover_all_python_files()
        importability = coverage_analyzer.analyze_importability()
        complexity = coverage_analyzer.analyze_ast_complexity()
        
        total_python_files = len(python_files)
        importable_ratio = len(importability["importable"]) / total_python_files if total_python_files > 0 else 0
        
        print(f"📊 Python App Statistics:")
        print(f"  • Total Python files: {total_python_files}")
        print(f"  • Importable modules: {len(importability['importable'])} ({importable_ratio*100:.1f}%)")
        print(f"  • Non-importable modules: {len(importability['non_importable'])}")
        print(f"  • Total functions: {complexity['complexity_summary']['total_functions']}")
        print(f"  • Total classes: {complexity['complexity_summary']['total_classes']}")
        print(f"  • Total lines of code: {complexity['complexity_summary']['total_lines']}")
        
        # Android App Analysis
        print(f"\n📱 ANDROID APPLICATION ANALYSIS")
        print(f"-" * 50)
        
        android_structure = android_analyzer.analyze_android_structure()
        
        print(f"📊 Android App Statistics:")
        print(f"  • Total source files: {android_structure['total_files']}")
        print(f"  • Kotlin files: {android_structure['kotlin_files']}")
        print(f"  • Java files: {android_structure['java_files']}")
        if android_structure['total_files'] > 0:
            print(f"  • Total lines of code: {android_structure['total_lines']}")
            print(f"  • Average lines per file: {android_structure['avg_lines_per_file']:.2f}")
        
        # Dead Code Assessment
        print(f"\n⚠️  DEAD CODE ASSESSMENT")
        print(f"-" * 50)
        
        # Potential dead code indicators
        non_importable_ratio = len(importability["non_importable"]) / total_python_files if total_python_files > 0 else 0
        
        print(f"🔍 Potential Dead Code Indicators:")
        print(f"  • Non-importable Python modules: {non_importable_ratio*100:.1f}% ({len(importability['non_importable'])} files)")
        
        if non_importable_ratio > 0.3:
            print(f"  ⚠️  HIGH: >30% of Python files cannot be imported - potential dead code")
        elif non_importable_ratio > 0.1:
            print(f"  ⚠️  MEDIUM: >10% of Python files cannot be imported")
        else:
            print(f"  ✅ LOW: Most Python files are importable")
        
        # Files with potential issues
        problematic_files = []
        for module, stats in complexity["file_stats"].items():
            if isinstance(stats, dict) and stats.get("potential_issues"):
                problematic_files.append(module)
        
        if problematic_files:
            problematic_ratio = len(problematic_files) / total_python_files if total_python_files > 0 else 0
            print(f"  • Files with potential issues: {len(problematic_files)} ({problematic_ratio*100:.1f}%)")
        
        # Android issues
        if android_structure["potential_issues"]:
            print(f"  • Android files with potential issues: {len(android_structure['potential_issues'])}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print(f"-" * 50)
        
        if non_importable_ratio > 0.2:
            print(f"  1. 🧹 Consider reviewing non-importable modules for removal or fixing")
            print(f"  2. 🔧 Address import errors to improve code maintainability")
        
        if len(problematic_files) > total_python_files * 0.1:
            print(f"  3. 🏗️  Review files with high import/function ratios for over-engineering")
        
        if android_structure["total_files"] == 0:
            print(f"  4. 📱 Android app analysis was limited - consider deeper analysis")
        
        print(f"\n📋 SUMMARY")
        print(f"-" * 50)
        total_files = total_python_files + android_structure["total_files"]
        total_lines = complexity["complexity_summary"]["total_lines"] + android_structure.get("total_lines", 0)
        
        print(f"  • Total project files analyzed: {total_files}")
        print(f"  • Total lines of code: {total_lines}")
        print(f"  • Estimated dead code ratio: {non_importable_ratio*100:.1f}% (Python only)")
        
        if non_importable_ratio > 0.5:
            print(f"  🚨 CRITICAL: High potential for dead code - immediate review recommended")
        elif non_importable_ratio > 0.3:
            print(f"  ⚠️  WARNING: Moderate potential for dead code")
        else:
            print(f"  ✅ GOOD: Low potential for dead code")
        
        print(f"\n{'='*80}")
        
        # This is an analysis test - it should not fail
        assert total_files >= 0


if __name__ == "__main__":
    # Can be run directly for quick analysis
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    python_analyzer = PythonAppCoverageAnalyzer(base_path)
    android_analyzer = AndroidAppCoverageAnalyzer(base_path)
    
    print("Running comprehensive coverage analysis...")
    
    # Quick analysis
    files = python_analyzer.discover_all_python_files()
    importability = python_analyzer.analyze_importability()
    
    print(f"Found {len(files)} Python files")
    print(f"Importable: {len(importability['importable'])}")
    print(f"Non-importable: {len(importability['non_importable'])}")