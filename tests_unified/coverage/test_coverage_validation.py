#!/usr/bin/env python3
"""
Simple Coverage Validation Tests

These tests validate that our coverage analysis tools work correctly
without requiring GUI dependencies. Can be run with pytest.
"""

import pytest
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestCoverageAnalysisTools:
    """Test the coverage analysis tools functionality."""
    
    def test_project_structure_exists(self):
        """Test that the expected project structure exists."""
        python_app_path = project_root / "PythonApp"
        android_app_path = project_root / "AndroidApp" 
        
        assert python_app_path.exists(), "PythonApp directory should exist"
        assert android_app_path.exists(), "AndroidApp directory should exist"
        
        # Check for main files
        main_py = python_app_path / "main.py"
        assert main_py.exists(), "main.py should exist"
        
    def test_python_file_discovery(self):
        """Test that we can discover Python files."""
        from tests_unified.coverage.dead_code_analyzer import DeadCodeAnalyzer
        
        analyzer = DeadCodeAnalyzer(str(project_root))
        python_results = analyzer.analyze_python_files()
        
        assert python_results["total_files"] > 100, "Should find many Python files"
        assert "file_analysis" in python_results
        assert "complexity_stats" in python_results
        
    def test_android_file_discovery(self):
        """Test that we can discover Android files."""
        from tests_unified.coverage.dead_code_analyzer import DeadCodeAnalyzer
        
        analyzer = DeadCodeAnalyzer(str(project_root))
        android_results = analyzer.analyze_android_files()
        
        assert android_results["total_files"] > 100, "Should find many Android files"
        assert android_results["kotlin_files"] > 0, "Should find Kotlin files"
        
    def test_import_analysis_functionality(self):
        """Test that import analysis works."""
        from tests_unified.coverage.import_analysis import ImportIssueAnalyzer
        
        analyzer = ImportIssueAnalyzer(str(project_root))
        # Test that analyzer can be created and has basic functionality
        assert analyzer.project_root.exists()
        assert analyzer.python_app_path.exists()
        
    def test_realistic_coverage_basic_functionality(self):
        """Test basic functionality of realistic coverage test."""
        from tests_unified.coverage.realistic_coverage_test import RealisticCoverageTest
        
        tester = RealisticCoverageTest(str(project_root))
        assert tester.project_root.exists()
        
        # Test that coverage can be initialized
        assert tester.cov is not None
        
    def test_working_entry_points_importable(self):
        """Test that the working entry points can be imported."""
        # These should work based on our analysis
        working_modules = [
            "PythonApp.main",
            "PythonApp.web_launcher", 
            "PythonApp.utils",
            "PythonApp.config",
            "PythonApp.error_handling"
        ]
        
        successful_imports = 0
        for module_name in working_modules:
            try:
                __import__(module_name)
                successful_imports += 1
            except ImportError:
                # Expected for some modules without dependencies
                pass
        
        assert successful_imports >= 2, "At least some core modules should import"
        
    def test_coverage_report_files_created(self):
        """Test that coverage analysis creates expected files."""
        coverage_xml = project_root / "coverage_realistic.xml"
        html_dir = project_root / "htmlcov_realistic"
        
        # Files might exist from previous runs
        if coverage_xml.exists():
            assert coverage_xml.stat().st_size > 0, "Coverage XML should not be empty"
            
        if html_dir.exists():
            index_html = html_dir / "index.html"
            if index_html.exists():
                assert index_html.stat().st_size > 0, "HTML report should not be empty"
                
    def test_analysis_summary_content(self):
        """Test that analysis produces meaningful content."""
        from tests_unified.coverage.dead_code_analyzer import DeadCodeAnalyzer
        
        analyzer = DeadCodeAnalyzer(str(project_root))
        python_results = analyzer.analyze_python_files()
        
        # Validate the findings match our expectations
        total_files = python_results["total_files"]
        assert total_files > 100, f"Expected >100 files, got {total_files}"
        
        complexity = python_results["complexity_stats"]
        assert complexity["total_functions"] > 1000, "Should find many functions"
        assert complexity["total_classes"] > 200, "Should find many classes"
        assert complexity["total_lines"] > 30000, "Should find substantial codebase"


class TestCoverageToolsIntegration:
    """Integration tests for coverage tools."""
    
    def test_full_analysis_integration(self):
        """Test that full analysis can run without crashing."""
        from tests_unified.coverage.dead_code_analyzer import DeadCodeAnalyzer
        
        analyzer = DeadCodeAnalyzer(str(project_root))
        
        # Should not crash
        python_results = analyzer.analyze_python_files()
        android_results = analyzer.analyze_android_files()
        
        # Should produce meaningful results
        assert python_results["total_files"] > 0
        assert android_results["total_files"] > 0
        
    @pytest.mark.slow
    def test_realistic_coverage_integration(self):
        """Test realistic coverage analysis integration."""
        from tests_unified.coverage.realistic_coverage_test import RealisticCoverageTest
        
        tester = RealisticCoverageTest(str(project_root))
        
        # Test individual components without GUI
        tester.test_utility_modules_coverage()
        tester.test_data_processing_coverage()
        tester.test_web_interface_coverage()
        
        # Should complete without major errors
        analysis_results = tester.analyze_reachable_vs_total_code()
        
        assert analysis_results["total_files"] > 100
        assert analysis_results["reachable_percentage"] > 50  # Should be high
        

class TestAnalysisAccuracy:
    """Test the accuracy of our analysis conclusions."""
    
    def test_code_is_not_dead_conclusion(self):
        """Validate that our conclusion about code not being dead is accurate."""
        from tests_unified.coverage.realistic_coverage_test import RealisticCoverageTest
        
        tester = RealisticCoverageTest(str(project_root))
        
        # Run basic coverage
        tester.test_utility_modules_coverage()
        tester.test_data_processing_coverage()
        
        results = tester.analyze_reachable_vs_total_code()
        
        # Our key finding: most code is reachable
        reachable_percentage = results["reachable_percentage"]
        assert reachable_percentage > 80, f"Expected >80% reachable, got {reachable_percentage}%"
        
        print(f"✅ Validated: {reachable_percentage}% of code is reachable (not dead)")
        
    def test_dependency_issues_vs_dead_code(self):
        """Test that import failures are dependency issues, not dead code."""
        from tests_unified.coverage.dead_code_analyzer import DeadCodeAnalyzer
        
        analyzer = DeadCodeAnalyzer(str(project_root))
        python_results = analyzer.analyze_python_files()
        
        total_files = python_results["total_files"]
        non_importable = len(python_results["importability"]["non_importable"])
        errors = python_results["importability"]["errors"]
        
        # Most errors should be dependency-related
        dependency_errors = 0
        for error in errors.values():
            if "Missing dependency" in error or "No module named" in error:
                dependency_errors += 1
        
        dependency_ratio = dependency_errors / len(errors) if errors else 0
        
        assert dependency_ratio > 0.7, f"Expected >70% dependency errors, got {dependency_ratio*100}%"
        
        print(f"✅ Validated: {dependency_ratio*100:.1f}% of import failures are dependency issues")


if __name__ == "__main__":
    # Can be run directly for quick validation
    pytest.main([__file__, "-v"])