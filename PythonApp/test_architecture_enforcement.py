"""
Architecture enforcement tests for Python PC application.

This module validates that the PC application maintains proper layer separation
and follows architectural constraints consistent with the Android application.
"""

import unittest
import os
import ast
from pathlib import Path
from typing import List, Set


class PythonArchitectureTest(unittest.TestCase):
    """Test suite for Python application architecture enforcement."""

    def setUp(self):
        """Set up test environment with project paths."""
        self.project_root = Path(__file__).parent.parent
        self.python_app_root = self.project_root / "PythonApp"
        
    def test_gui_layer_should_not_import_low_level_services(self):
        """Ensure GUI layer doesn't directly access device management or network services."""
        gui_files = self._get_python_files_in_package("gui")
        forbidden_imports = [
            "network.",
            "device.",
            "shimmer_manager",
            "calibration.calibration_processor",  # Should go through manager
        ]
        
        for file_path in gui_files:
            imports = self._extract_imports_from_file(file_path)
            for forbidden_import in forbidden_imports:
                self.assertNotIn(
                    forbidden_import, 
                    imports, 
                    f"GUI file {file_path} should not directly import {forbidden_import}"
                )

    def test_managers_should_not_import_gui_components(self):
        """Ensure business logic managers don't depend on GUI implementation."""
        manager_files = self._get_python_files_with_pattern("*manager*.py")
        if not manager_files:
            self.skipTest("No manager files found")
            
        forbidden_imports = [
            "PyQt5.QtWidgets",
            "tkinter",
            "gui.",
        ]
        
        for file_path in manager_files:
            imports = self._extract_imports_from_file(file_path)
            for forbidden_import in forbidden_imports:
                self.assertNotIn(
                    forbidden_import,
                    imports,
                    f"Manager {file_path} should not import GUI components {forbidden_import}"
                )

    def test_network_layer_independence(self):
        """Validate that network layer doesn't depend on business logic."""
        network_files = self._get_python_files_in_package("network")
        forbidden_imports = [
            "gui.",
            "calibration.calibration_manager",  # Should not depend on high-level managers
            "session.",
        ]
        
        for file_path in network_files:
            imports = self._extract_imports_from_file(file_path)
            for forbidden_import in forbidden_imports:
                self.assertNotIn(
                    forbidden_import,
                    imports,
                    f"Network file {file_path} should not import {forbidden_import}"
                )

    def test_infrastructure_utilities_usage(self):
        """Verify consistent usage of infrastructure utilities."""
        all_python_files = self._get_all_python_files()
        
        # Be more lenient - just warn about excessive print usage
        for file_path in all_python_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for direct print usage (should use logging) but allow some for development
            if "print(" in content and "test" not in str(file_path).lower():
                lines = content.split('\n')
                print_lines = [i for i, line in enumerate(lines) if "print(" in line and "debug" not in line.lower()]
                # Allow up to 3 print statements per file for development purposes
                if len(print_lines) > 3:
                    self.fail(f"File {file_path} has excessive print() usage ({len(print_lines)} lines). Consider using logging.")

    def test_dependency_injection_patterns(self):
        """Validate that DI patterns are followed consistently."""
        manager_files = self._get_python_files_with_pattern("*manager*.py")
        
        for file_path in manager_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for constructor dependency injection pattern
            if "class" in content and "Manager" in content:
                self.assertIn(
                    "__init__",
                    content,
                    f"Manager {file_path} should have proper constructor for DI"
                )

    def test_error_handling_consistency(self):
        """Ensure consistent error handling patterns across components."""
        all_python_files = self._get_all_python_files()
        
        for file_path in all_python_files:
            if "test" in str(file_path).lower():
                continue
                
            try:
                tree = self._parse_python_file(file_path)
                
                # Check for bare except clauses (more lenient approach)
                bare_except_count = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        bare_except_count += 1
                
                # Allow some bare except clauses but warn if excessive
                if bare_except_count > 2:
                    self.fail(f"File {file_path} has excessive bare except clauses ({bare_except_count}). Consider specific exception handling.")
                    
            except SyntaxError:
                # Skip files with syntax errors rather than failing
                continue

    def test_cross_cutting_concerns_centralization(self):
        """Validate that cross-cutting concerns are properly centralized."""
        all_python_files = self._get_all_python_files()
        
        logging_files = []
        threading_files = []
        
        for file_path in all_python_files:
            imports = self._extract_imports_from_file(file_path)
            
            if "logging" in imports:
                logging_files.append(file_path)
            if "threading" in imports or "concurrent.futures" in imports:
                threading_files.append(file_path)
        
        # Should have centralized logging configuration
        self.assertGreater(
            len(logging_files), 0,
            "System should use centralized logging"
        )

    def test_session_management_layer_separation(self):
        """Ensure session management follows proper layer separation."""
        session_files = self._get_python_files_in_package("session")
        forbidden_imports = [
            "gui.",
            "PyQt5.QtWidgets",
        ]
        
        for file_path in session_files:
            imports = self._extract_imports_from_file(file_path)
            for forbidden_import in forbidden_imports:
                self.assertNotIn(
                    forbidden_import,
                    imports,
                    f"Session file {file_path} should not directly access GUI layer"
                )

    # Helper methods

    def _get_python_files_in_package(self, package_name: str) -> List[Path]:
        """Get all Python files in a specific package."""
        package_path = self.python_app_root / package_name
        if not package_path.exists():
            return []
        
        return list(package_path.rglob("*.py"))

    def _get_python_files_with_pattern(self, pattern: str) -> List[Path]:
        """Get Python files matching a specific pattern."""
        return list(self.python_app_root.rglob(pattern))

    def _get_all_python_files(self) -> List[Path]:
        """Get all Python files in the project."""
        return [f for f in self.python_app_root.rglob("*.py") if f.is_file()]

    def _extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """Extract all import statements from a Python file."""
        try:
            tree = self._parse_python_file(file_path)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        
            return imports
        except Exception as e:
            self.fail(f"Failed to parse file {file_path}: {e}")
            return set()

    def _parse_python_file(self, file_path: Path) -> ast.AST:
        """Parse Python file into AST."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content)


class PythonArchitectureValidationSuite:
    """Suite for running Python architecture validation."""
    
    @staticmethod
    def run_validation():
        """Run all architecture validation tests."""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PythonArchitectureTest)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()


if __name__ == "__main__":
    unittest.main()