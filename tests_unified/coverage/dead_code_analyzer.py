#!/usr/bin/env python3
"""
Standalone Dead Code Analysis for Multi-Sensor Recording System

This script provides detailed analysis of both Python and Android applications
to identify dead/unreachable code without requiring pytest infrastructure.
"""

import ast
import os
import sys
import importlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from unittest.mock import MagicMock, patch
import traceback


class DeadCodeAnalyzer:
    """Comprehensive dead code analyzer for the multi-sensor recording system."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_app_path = self.project_root / "PythonApp"
        self.android_app_path = self.project_root / "AndroidApp"
        
    def analyze_python_files(self) -> Dict[str, Any]:
        """Analyze all Python files in the PythonApp directory."""
        print("🔍 Analyzing Python files...")
        
        # Discover all Python files
        python_files = []
        for py_file in self.python_app_path.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                python_files.append(py_file)
        
        print(f"Found {len(python_files)} Python files")
        
        results = {
            "total_files": len(python_files),
            "file_analysis": {},
            "importability": {"importable": [], "non_importable": [], "errors": {}},
            "complexity_stats": {
                "total_functions": 0,
                "total_classes": 0,
                "total_lines": 0,
                "files_with_issues": []
            }
        }
        
        # Analyze each file
        for py_file in python_files:
            file_info = self._analyze_single_python_file(py_file)
            relative_path = str(py_file.relative_to(self.project_root))
            results["file_analysis"][relative_path] = file_info
            
            # Update totals
            if "functions" in file_info:
                results["complexity_stats"]["total_functions"] += file_info["functions"]
            if "classes" in file_info:
                results["complexity_stats"]["total_classes"] += file_info["classes"]
            if "lines" in file_info:
                results["complexity_stats"]["total_lines"] += file_info["lines"]
            
            # Check if file has potential issues
            if file_info.get("potential_issues"):
                results["complexity_stats"]["files_with_issues"].append(relative_path)
        
        # Test importability
        self._test_importability(python_files, results["importability"])
        
        return results
    
    def _analyze_single_python_file(self, py_file: Path) -> Dict[str, Any]:
        """Analyze a single Python file."""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            lines = content.splitlines()
            file_info = {
                "lines": len(lines),
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "potential_issues": [],
                "size_category": "small"
            }
            
            # Categorize by size
            if file_info["lines"] > 500:
                file_info["size_category"] = "large"
            elif file_info["lines"] > 200:
                file_info["size_category"] = "medium"
            
            try:
                tree = ast.parse(content)
                
                function_names = []
                class_names = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        file_info["functions"] += 1
                        function_names.append(node.name)
                        
                        # Check for potential dead code indicators
                        if node.name.startswith('_') and not node.name.startswith('__'):
                            file_info["potential_issues"].append(f"Private function: {node.name}")
                            
                    elif isinstance(node, ast.ClassDef):
                        file_info["classes"] += 1
                        class_names.append(node.name)
                        
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        file_info["imports"] += 1
                
                file_info["function_names"] = function_names
                file_info["class_names"] = class_names
                
                # Analyze import density
                if file_info["functions"] > 0:
                    import_ratio = file_info["imports"] / file_info["functions"]
                    if import_ratio > 3:
                        file_info["potential_issues"].append(f"High import/function ratio: {import_ratio:.2f}")
                
                # Check for TODO/FIXME comments
                todo_count = content.lower().count("todo") + content.lower().count("fixme")
                if todo_count > 3:
                    file_info["potential_issues"].append(f"Many TODOs/FIXMEs: {todo_count}")
                
                # Check for empty functions/classes (potential stubs)
                empty_functions = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if len(node.body) == 1 and isinstance(node.body[0], (ast.Pass, ast.Ellipsis)):
                            empty_functions += 1
                
                if empty_functions > 0:
                    file_info["potential_issues"].append(f"Empty functions (stubs): {empty_functions}")
                
            except SyntaxError as e:
                file_info["syntax_error"] = str(e)
                file_info["potential_issues"].append("Syntax error - file may be broken")
            
            return file_info
            
        except Exception as e:
            return {"error": str(e), "potential_issues": ["File read error"]}
    
    def _test_importability(self, python_files: List[Path], results: Dict[str, Any]):
        """Test which Python modules can be imported."""
        print("🧪 Testing module importability...")
        
        # Add project root to Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue
                
            try:
                # Convert file path to module name
                relative_path = py_file.relative_to(self.project_root)
                module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
                module_name = ".".join(module_parts)
                
                # Try to import with extensive mocking
                with patch('PyQt5.QtWidgets.QApplication', MagicMock()), \
                     patch('PyQt6.QtWidgets.QApplication', MagicMock()), \
                     patch('PyQt5.QtCore.QTimer', MagicMock()), \
                     patch('PyQt6.QtCore.QTimer', MagicMock()), \
                     patch('PyQt5.QtWidgets.QMainWindow', MagicMock()), \
                     patch('PyQt6.QtWidgets.QMainWindow', MagicMock()), \
                     patch('cv2.VideoCapture', MagicMock()), \
                     patch('matplotlib.pyplot', MagicMock()), \
                     patch('numpy', MagicMock()), \
                     patch('pandas', MagicMock()), \
                     patch('scipy', MagicMock()):
                    
                    # Clear module cache
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                    
                    importlib.import_module(module_name)
                    results["importable"].append(module_name)
                    
            except Exception as e:
                error_msg = str(e)
                # Classify error types
                if "No module named" in error_msg:
                    error_type = "Missing dependency"
                elif "cannot import name" in error_msg:
                    error_type = "Import error"
                elif "invalid syntax" in error_msg.lower():
                    error_type = "Syntax error"
                else:
                    error_type = "Other error"
                
                results["non_importable"].append(module_name)
                results["errors"][module_name] = f"{error_type}: {error_msg[:100]}"
    
    def analyze_android_files(self) -> Dict[str, Any]:
        """Analyze Android Kotlin/Java files."""
        print("📱 Analyzing Android files...")
        
        source_files = []
        
        # Look for Android source files
        android_src_paths = [
            self.android_app_path / "src" / "main" / "java",
            self.android_app_path / "src" / "main" / "kotlin", 
            self.android_app_path / "app" / "src" / "main" / "java",
            self.android_app_path / "app" / "src" / "main" / "kotlin"
        ]
        
        for src_path in android_src_paths:
            if src_path.exists():
                for pattern in ["**/*.kt", "**/*.java"]:
                    source_files.extend(src_path.glob(pattern))
        
        print(f"Found {len(source_files)} Android source files")
        
        results = {
            "total_files": len(source_files),
            "kotlin_files": 0,
            "java_files": 0,
            "total_lines": 0,
            "file_analysis": {},
            "potential_issues": []
        }
        
        for source_file in source_files:
            file_info = self._analyze_android_file(source_file)
            relative_path = str(source_file.relative_to(self.project_root))
            results["file_analysis"][relative_path] = file_info
            
            if source_file.suffix == ".kt":
                results["kotlin_files"] += 1
            elif source_file.suffix == ".java":
                results["java_files"] += 1
            
            if "lines" in file_info:
                results["total_lines"] += file_info["lines"]
            
            # Collect potential issues
            if file_info.get("potential_issues"):
                for issue in file_info["potential_issues"]:
                    results["potential_issues"].append(f"{relative_path}: {issue}")
        
        return results
    
    def _analyze_android_file(self, source_file: Path) -> Dict[str, Any]:
        """Analyze a single Android source file."""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            file_info = {
                "lines": len(lines),
                "potential_issues": []
            }
            
            # Size analysis
            if len(lines) > 1000:
                file_info["potential_issues"].append(f"Very large file ({len(lines)} lines)")
            elif len(lines) > 500:
                file_info["potential_issues"].append(f"Large file ({len(lines)} lines)")
            
            # TODO/FIXME analysis
            todo_count = content.lower().count("todo") + content.lower().count("fixme")
            if todo_count > 5:
                file_info["potential_issues"].append(f"Many TODOs/FIXMEs ({todo_count})")
            
            # Look for commented out code blocks
            comment_lines = [line.strip() for line in lines if line.strip().startswith("//")]
            if len(comment_lines) > len(lines) * 0.3:
                file_info["potential_issues"].append("High proportion of comments (potential dead code)")
            
            # Simple pattern matching for unused imports/classes
            if "import " in content:
                import_count = content.count("import ")
                if import_count > 50:
                    file_info["potential_issues"].append(f"Many imports ({import_count}) - potential over-dependency")
            
            return file_info
            
        except Exception as e:
            return {"error": str(e), "potential_issues": ["File read error"]}
    
    def generate_comprehensive_report(self) -> None:
        """Generate and print a comprehensive dead code analysis report."""
        print(f"\n{'='*80}")
        print(f"🚨 COMPREHENSIVE DEAD CODE ANALYSIS REPORT")
        print(f"{'='*80}")
        
        # Analyze both applications
        python_results = self.analyze_python_files()
        android_results = self.analyze_android_files()
        
        # Python App Summary
        print(f"\n🐍 PYTHON APPLICATION ANALYSIS")
        print(f"-" * 50)
        
        total_python_files = python_results["total_files"]
        importable_count = len(python_results["importability"]["importable"])
        non_importable_count = len(python_results["importability"]["non_importable"])
        
        print(f"📊 Python Statistics:")
        print(f"  • Total Python files: {total_python_files}")
        print(f"  • Total lines of code: {python_results['complexity_stats']['total_lines']:,}")
        print(f"  • Total functions: {python_results['complexity_stats']['total_functions']}")
        print(f"  • Total classes: {python_results['complexity_stats']['total_classes']}")
        print(f"  • Importable modules: {importable_count} ({importable_count/total_python_files*100:.1f}%)")
        print(f"  • Non-importable modules: {non_importable_count} ({non_importable_count/total_python_files*100:.1f}%)")
        
        # Android App Summary
        print(f"\n📱 ANDROID APPLICATION ANALYSIS")
        print(f"-" * 50)
        
        print(f"📊 Android Statistics:")
        print(f"  • Total source files: {android_results['total_files']}")
        print(f"  • Kotlin files: {android_results['kotlin_files']}")
        print(f"  • Java files: {android_results['java_files']}")
        print(f"  • Total lines of code: {android_results['total_lines']:,}")
        
        # Dead Code Assessment
        print(f"\n⚠️  DEAD CODE ASSESSMENT")
        print(f"-" * 50)
        
        non_importable_ratio = non_importable_count / total_python_files if total_python_files > 0 else 0
        
        print(f"🔍 Dead Code Indicators:")
        print(f"  • Non-importable Python modules: {non_importable_ratio*100:.1f}%")
        
        if non_importable_ratio > 0.7:
            print(f"  🚨 CRITICAL: >70% of files cannot be imported!")
        elif non_importable_ratio > 0.5:
            print(f"  ⚠️  HIGH: >50% of files cannot be imported")
        elif non_importable_ratio > 0.3:
            print(f"  ⚠️  MEDIUM: >30% of files cannot be imported")
        else:
            print(f"  ✅ LOW: Most files are importable")
        
        # Top Import Errors
        if python_results["importability"]["errors"]:
            print(f"\n🔥 TOP IMPORT ERRORS:")
            error_types = {}
            for module, error in python_results["importability"]["errors"].items():
                error_type = error.split(":")[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {error_type}: {count} files")
        
        # Files with Issues
        files_with_issues = python_results["complexity_stats"]["files_with_issues"]
        if files_with_issues:
            print(f"\n⚠️  PYTHON FILES WITH POTENTIAL ISSUES ({len(files_with_issues)}):")
            for file_path in files_with_issues[:10]:  # Show top 10
                issues = python_results["file_analysis"][file_path].get("potential_issues", [])
                print(f"  • {file_path}: {', '.join(issues[:2])}")  # Show first 2 issues
        
        # Android Issues
        if android_results["potential_issues"]:
            print(f"\n⚠️  ANDROID FILES WITH POTENTIAL ISSUES ({len(android_results['potential_issues'])}):")
            for issue in android_results["potential_issues"][:10]:  # Show top 10
                print(f"  • {issue}")
        
        # Size Analysis
        print(f"\n📏 FILE SIZE ANALYSIS")
        print(f"-" * 50)
        
        large_python_files = []
        for file_path, info in python_results["file_analysis"].items():
            if info.get("size_category") == "large":
                large_python_files.append((file_path, info.get("lines", 0)))
        
        if large_python_files:
            large_python_files.sort(key=lambda x: x[1], reverse=True)
            print(f"🐍 Large Python files (>500 lines):")
            for file_path, lines in large_python_files[:5]:
                print(f"  • {file_path}: {lines} lines")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print(f"-" * 50)
        
        recommendations = []
        
        if non_importable_ratio > 0.5:
            recommendations.append("🧹 URGENT: Review and remove or fix non-importable modules")
        
        if len(files_with_issues) > total_python_files * 0.2:
            recommendations.append("🔧 Review files with high complexity or import issues")
        
        if len(large_python_files) > 5:
            recommendations.append("📏 Consider breaking down large files for maintainability")
        
        if android_results["total_files"] == 0:
            recommendations.append("📱 Investigate Android app structure - no source files found")
        
        if not recommendations:
            recommendations.append("✅ Code structure appears healthy overall")
        
        for rec in recommendations:
            print(f"  {rec}")
        
        # Final Summary
        print(f"\n📋 EXECUTIVE SUMMARY")
        print(f"-" * 50)
        
        total_files = total_python_files + android_results["total_files"]
        total_lines = python_results["complexity_stats"]["total_lines"] + android_results["total_lines"]
        
        print(f"  • Total project files: {total_files}")
        print(f"  • Total lines of code: {total_lines:,}")
        print(f"  • Estimated dead code ratio: {non_importable_ratio*100:.1f}%")
        
        if non_importable_ratio > 0.6:
            health_status = "🚨 CRITICAL"
        elif non_importable_ratio > 0.4:
            health_status = "⚠️  POOR"
        elif non_importable_ratio > 0.2:
            health_status = "⚠️  FAIR"
        else:
            health_status = "✅ GOOD"
        
        print(f"  • Code health status: {health_status}")
        
        print(f"\n{'='*80}")


def main():
    """Main entry point for the dead code analysis."""
    # Get the project root (assuming this script is in tests_unified/coverage/)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    
    print(f"🔍 Starting dead code analysis for project: {project_root}")
    
    analyzer = DeadCodeAnalyzer(str(project_root))
    analyzer.generate_comprehensive_report()


if __name__ == "__main__":
    main()