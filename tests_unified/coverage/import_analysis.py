#!/usr/bin/env python3
"""
Detailed Import Issue Analysis

This script investigates specific import issues to understand why 85% of files 
cannot be imported and identify the root causes.
"""

import sys
import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch
import ast
import traceback


class ImportIssueAnalyzer:
    """Analyzes specific import issues in detail."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_app_path = self.project_root / "PythonApp"
        
        # Add project to path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    def analyze_main_entry_points(self):
        """Analyze the main entry points of the application."""
        print("🎯 Analyzing main entry points...")
        
        main_files = [
            "PythonApp.main",
            "PythonApp.application", 
            "PythonApp.enhanced_main_with_web",
            "PythonApp.shimmer_pc_app",
            "PythonApp.web_launcher"
        ]
        
        for module_name in main_files:
            print(f"\n📦 Testing: {module_name}")
            try:
                with self._create_mock_environment():
                    module = importlib.import_module(module_name)
                    print(f"  ✅ SUCCESS: {module_name} imported successfully")
                    
                    # Check if it has a main function
                    if hasattr(module, 'main'):
                        print(f"  🎯 Has main() function")
                    if hasattr(module, '__main__'):
                        print(f"  🎯 Has __main__ block")
                        
            except Exception as e:
                print(f"  ❌ FAILED: {str(e)[:200]}...")
                self._analyze_import_error(module_name, e)
    
    def analyze_core_modules(self):
        """Analyze core utility and configuration modules."""
        print(f"\n🔧 Analyzing core modules...")
        
        core_modules = [
            "PythonApp.utils",
            "PythonApp.config", 
            "PythonApp.error_handling",
            "PythonApp.protocol",
            "PythonApp.network"
        ]
        
        for module_name in core_modules:
            self._test_module_and_submodules(module_name)
    
    def _test_module_and_submodules(self, module_name):
        """Test a module and its submodules."""
        print(f"\n📦 Testing module tree: {module_name}")
        
        # Test the main module
        try:
            with self._create_mock_environment():
                module = importlib.import_module(module_name)
                print(f"  ✅ {module_name} - SUCCESS")
        except Exception as e:
            print(f"  ❌ {module_name} - FAILED: {str(e)[:100]}...")
        
        # Test submodules
        module_path = self.python_app_path / module_name.replace("PythonApp.", "").replace(".", "/")
        if module_path.exists() and module_path.is_dir():
            for py_file in module_path.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                    
                submodule_name = f"{module_name}.{py_file.stem}"
                try:
                    with self._create_mock_environment():
                        submodule = importlib.import_module(submodule_name)
                        print(f"    ✅ {submodule_name} - SUCCESS")
                except Exception as e:
                    print(f"    ❌ {submodule_name} - FAILED: {str(e)[:80]}...")
    
    def _create_mock_environment(self):
        """Create a comprehensive mock environment for testing imports."""
        mocks = {
            # PyQt5 mocks
            'PyQt5': MagicMock(),
            'PyQt5.QtWidgets': MagicMock(),
            'PyQt5.QtCore': MagicMock(),
            'PyQt5.QtGui': MagicMock(),
            
            # PyQt6 mocks  
            'PyQt6': MagicMock(),
            'PyQt6.QtWidgets': MagicMock(),
            'PyQt6.QtCore': MagicMock(),
            'PyQt6.QtGui': MagicMock(),
            
            # Computer vision
            'cv2': MagicMock(),
            
            # Scientific computing
            'numpy': MagicMock(),
            'scipy': MagicMock(),
            'pandas': MagicMock(),
            'matplotlib': MagicMock(),
            'matplotlib.pyplot': MagicMock(),
            
            # Networking & protocols
            'websockets': MagicMock(),
            'requests': MagicMock(),
            'zeroconf': MagicMock(),
            
            # Hardware interfaces
            'pylsl': MagicMock(),
            
            # Other dependencies
            'flask': MagicMock(),
            'flask_socketio': MagicMock(),
            'socketio': MagicMock(),
        }
        
        return patch.dict('sys.modules', mocks)
    
    def _analyze_import_error(self, module_name, error):
        """Analyze specific import error in detail."""
        error_str = str(error)
        
        if "No module named" in error_str:
            missing_module = error_str.split("'")[1] if "'" in error_str else "unknown"
            print(f"    🔍 Missing dependency: {missing_module}")
        elif "cannot import name" in error_str:
            print(f"    🔍 Import name error - dependency version issue?")
        elif "invalid syntax" in error_str.lower():
            print(f"    🔍 Syntax error in module")
        else:
            print(f"    🔍 Other error type")
    
    def test_simple_utility_modules(self):
        """Test simple utility modules that should import easily."""
        print(f"\n🛠️  Testing simple utility modules...")
        
        # Find modules that might be standalone utilities
        for py_file in self.python_app_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test" in py_file.name:
                continue
            
            # Check if it's a simple utility (small, few imports)
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                lines = content.splitlines()
                if len(lines) < 100:  # Small files
                    import_lines = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
                    if len(import_lines) < 5:  # Few imports
                        
                        relative_path = py_file.relative_to(self.project_root)
                        module_name = ".".join(list(relative_path.parts[:-1]) + [relative_path.stem])
                        
                        print(f"  📄 Testing simple module: {module_name} ({len(lines)} lines, {len(import_lines)} imports)")
                        
                        try:
                            with self._create_mock_environment():
                                importlib.import_module(module_name)
                                print(f"    ✅ SUCCESS")
                        except Exception as e:
                            print(f"    ❌ FAILED: {str(e)[:60]}...")
                            
            except Exception:
                continue
    
    def analyze_dependency_chains(self):
        """Analyze which modules depend on which others."""
        print(f"\n🔗 Analyzing dependency chains...")
        
        dependency_map = {}
        
        for py_file in self.python_app_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Parse AST to find imports
                try:
                    tree = ast.parse(content)
                    imports = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                    
                    relative_path = py_file.relative_to(self.project_root)
                    module_name = ".".join(list(relative_path.parts[:-1]) + [relative_path.stem])
                    
                    # Filter for internal dependencies
                    internal_deps = [imp for imp in imports if imp.startswith('PythonApp')]
                    external_deps = [imp for imp in imports if not imp.startswith('PythonApp') and not imp.startswith('.')]
                    
                    dependency_map[module_name] = {
                        'internal': internal_deps,
                        'external': external_deps
                    }
                    
                except SyntaxError:
                    continue
                    
            except Exception:
                continue
        
        # Find modules with no internal dependencies (potential entry points)
        print("\n🎯 Modules with minimal internal dependencies:")
        for module, deps in dependency_map.items():
            if len(deps['internal']) <= 1:  # 0 or 1 internal dependency
                print(f"  • {module}: {len(deps['external'])} external, {len(deps['internal'])} internal")
        
        # Find most common external dependencies
        print("\n📦 Most common external dependencies:")
        ext_dep_count = {}
        for deps in dependency_map.values():
            for dep in deps['external']:
                ext_dep_count[dep] = ext_dep_count.get(dep, 0) + 1
        
        for dep, count in sorted(ext_dep_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {dep}: used in {count} files")
    
    def run_comprehensive_analysis(self):
        """Run all analysis methods."""
        print("🔍 Starting comprehensive import issue analysis...")
        
        self.analyze_main_entry_points()
        self.analyze_core_modules() 
        self.test_simple_utility_modules()
        self.analyze_dependency_chains()
        
        print(f"\n{'='*60}")
        print("📋 IMPORT ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print("The analysis above shows why 85% of files cannot be imported.")
        print("Main issues are likely:")
        print("  1. Missing external dependencies (PyQt, cv2, etc.)")
        print("  2. Complex interdependencies between modules")
        print("  3. Modules designed to be run in specific contexts")
        print("\nThis doesn't necessarily mean the code is 'dead' - it may just")
        print("require proper environment setup and specific entry points.")


def main():
    """Main entry point."""
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    
    analyzer = ImportIssueAnalyzer(str(project_root))
    analyzer.run_comprehensive_analysis()


if __name__ == "__main__":
    main()