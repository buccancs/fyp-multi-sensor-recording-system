#!/usr/bin/env python3
"""
Realistic Coverage Test for Working Entry Points

This test actually exercises the importable modules and provides realistic
coverage analysis based on what code is actually reachable through the 
working entry points.
"""

import os
import sys
import coverage
from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib
import time


class RealisticCoverageTest:
    """Test coverage by exercising actual working entry points."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        # Initialize coverage
        self.cov = coverage.Coverage(
            source=["PythonApp"],
            omit=[
                "*/test*",
                "*/__pycache__/*",
                "*/tests/*"
            ]
        )
    
    def test_main_entry_point_coverage(self):
        """Test coverage through the main entry point."""
        print("🎯 Testing main entry point coverage...")
        
        self.cov.start()
        
        try:
            # Import and inspect the main module without running GUI
            with patch('PyQt5.QtWidgets.QApplication') as mock_app, \
                 patch('PyQt5.QtCore.qVersion', return_value="5.15.0"), \
                 patch('sys.exit') as mock_exit:
                
                # Mock QApplication to avoid GUI initialization
                mock_app_instance = MagicMock()
                mock_app.return_value = mock_app_instance
                mock_app_instance.exec_.return_value = 0
                
                import PythonApp.main
                
                # Import the main window class to see what it covers
                import PythonApp.gui.enhanced_ui_main_window
                
                # Access key attributes to trigger code coverage
                main_window_class = PythonApp.gui.enhanced_ui_main_window.EnhancedMainWindow
                
                print(f"  ✅ Successfully imported main entry point")
                
        except Exception as e:
            print(f"  ❌ Error testing main entry point: {e}")
        
        self.cov.stop()
        
    def test_utility_modules_coverage(self):
        """Test coverage of utility modules."""
        print("🛠️  Testing utility modules coverage...")
        
        self.cov.start()
        
        try:
            # Test working utility modules identified in previous analysis
            import PythonApp.utils
            import PythonApp.utils.logging_config
            import PythonApp.utils.android_connection_detector
            import PythonApp.utils.system_monitor
            
            import PythonApp.config
            import PythonApp.config.configuration_manager
            import PythonApp.config.system_configuration
            
            import PythonApp.error_handling
            import PythonApp.error_handling.recovery_manager
            
            # Exercise some functionality
            config_manager = PythonApp.config.configuration_manager.ConfigurationManager()
            logger = PythonApp.utils.logging_config.get_logger("test")
            
            print(f"  ✅ Successfully imported and exercised utility modules")
            
        except Exception as e:
            print(f"  ❌ Error testing utility modules: {e}")
        
        self.cov.stop()
    
    def test_protocol_and_network_coverage(self):
        """Test coverage of protocol and network modules."""
        print("🌐 Testing protocol and network modules coverage...")
        
        self.cov.start()
        
        try:
            import PythonApp.protocol
            import PythonApp.protocol.config_loader
            import PythonApp.protocol.enhanced_protocol
            import PythonApp.protocol.handshake_manager
            
            import PythonApp.network
            import PythonApp.network.device_client
            import PythonApp.network.android_device_manager
            
            # Try to exercise some functionality
            config_loader = PythonApp.protocol.config_loader.ConfigLoader()
            
            print(f"  ✅ Successfully imported protocol and network modules")
            
        except Exception as e:
            print(f"  ❌ Error testing protocol modules: {e}")
        
        self.cov.stop()
    
    def test_data_processing_coverage(self):
        """Test coverage of data processing modules."""
        print("📊 Testing data processing modules coverage...")
        
        self.cov.start()
        
        try:
            # Test processing modules that should work without hardware
            import PythonApp.calibration
            import PythonApp.calibration.calibration_processor
            import PythonApp.calibration.calibration_manager
            
            import PythonApp.recording
            
            print(f"  ✅ Successfully imported data processing modules")
            
        except Exception as e:
            print(f"  ❌ Error testing data processing modules: {e}")
        
        self.cov.stop()
    
    def test_web_interface_coverage(self):
        """Test coverage of web interface."""
        print("🌐 Testing web interface coverage...")
        
        self.cov.start()
        
        try:
            # Test web launcher which we know works
            import PythonApp.web_launcher
            
            # Try to import web components
            import PythonApp.web_ui
            
            print(f"  ✅ Successfully imported web interface modules")
            
        except Exception as e:
            print(f"  ❌ Error testing web interface: {e}")
        
        self.cov.stop()
    
    def run_all_coverage_tests(self):
        """Run all coverage tests and generate report."""
        print(f"\n{'='*60}")
        print("🧪 REALISTIC COVERAGE ANALYSIS")
        print(f"{'='*60}")
        
        # Start comprehensive coverage
        self.cov.start()
        
        # Run all tests
        self.test_main_entry_point_coverage()
        self.test_utility_modules_coverage()
        self.test_protocol_and_network_coverage()
        self.test_data_processing_coverage()
        self.test_web_interface_coverage()
        
        # Stop coverage and save
        self.cov.stop()
        self.cov.save()
        
        # Generate reports
        self.generate_coverage_reports()
    
    def generate_coverage_reports(self):
        """Generate and display coverage reports."""
        print(f"\n📊 COVERAGE REPORT GENERATION")
        print(f"-" * 40)
        
        try:
            # Generate HTML report
            html_dir = self.project_root / "htmlcov_realistic"
            html_dir.mkdir(exist_ok=True)
            
            self.cov.html_report(directory=str(html_dir))
            print(f"  ✅ HTML report generated: {html_dir}/index.html")
            
            # Generate XML report
            xml_file = self.project_root / "coverage_realistic.xml"
            self.cov.xml_report(outfile=str(xml_file))
            print(f"  ✅ XML report generated: {xml_file}")
            
            # Get coverage data
            coverage_data = self.cov.get_data()
            measured_files = list(coverage_data.measured_files())
            
            print(f"\n📈 COVERAGE STATISTICS")
            print(f"-" * 40)
            print(f"  • Files measured: {len(measured_files)}")
            
            # Display file list
            if measured_files:
                print(f"\n📁 MEASURED FILES:")
                for i, file_path in enumerate(sorted(measured_files)[:20]):  # Show first 20
                    relative_path = Path(file_path).relative_to(self.project_root)
                    print(f"    {i+1:2d}. {relative_path}")
                
                if len(measured_files) > 20:
                    print(f"    ... and {len(measured_files) - 20} more files")
            
            # Try to get line coverage data
            try:
                coverage_report = self.cov.report(show_missing=False, skip_covered=False)
                print(f"\n📊 Overall coverage: {coverage_report:.1f}%")
            except Exception as e:
                print(f"  ⚠️  Could not calculate overall coverage: {e}")
            
        except Exception as e:
            print(f"  ❌ Error generating coverage reports: {e}")
    
    def analyze_reachable_vs_total_code(self):
        """Analyze what percentage of total code is actually reachable."""
        print(f"\n🎯 REACHABLE CODE ANALYSIS")
        print(f"-" * 40)
        
        # Get all Python files
        all_python_files = list(self.project_root.glob("PythonApp/**/*.py"))
        all_python_files = [f for f in all_python_files if "__pycache__" not in str(f)]
        
        # Count total lines
        total_lines = 0
        for py_file in all_python_files:
            try:
                with open(py_file, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                continue
        
        # Get measured files
        coverage_data = self.cov.get_data()
        measured_files = list(coverage_data.measured_files())
        
        # Count measured lines
        measured_lines = 0
        for file_path in measured_files:
            try:
                with open(file_path, 'r') as f:
                    measured_lines += len(f.readlines())
            except:
                continue
        
        reachable_percentage = (measured_lines / total_lines * 100) if total_lines > 0 else 0
        
        print(f"  • Total Python files: {len(all_python_files)}")
        print(f"  • Files with coverage: {len(measured_files)}")
        print(f"  • Total lines of code: {total_lines:,}")
        print(f"  • Lines with coverage: {measured_lines:,}")
        print(f"  • Reachable code percentage: {reachable_percentage:.1f}%")
        
        # Assessment
        if reachable_percentage > 50:
            status = "✅ GOOD"
        elif reachable_percentage > 25:
            status = "⚠️  MODERATE"
        else:
            status = "🚨 LOW"
        
        print(f"  • Reachability status: {status}")
        
        return {
            "total_files": len(all_python_files),
            "measured_files": len(measured_files),
            "total_lines": total_lines,
            "measured_lines": measured_lines,
            "reachable_percentage": reachable_percentage
        }


def main():
    """Main entry point for realistic coverage testing."""
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    
    print("🧪 Starting realistic coverage analysis...")
    print(f"Project root: {project_root}")
    
    tester = RealisticCoverageTest(str(project_root))
    tester.run_all_coverage_tests()
    
    # Final analysis
    results = tester.analyze_reachable_vs_total_code()
    
    print(f"\n{'='*60}")
    print("📋 FINAL ASSESSMENT")
    print(f"{'='*60}")
    
    print(f"Based on testing actual working entry points:")
    print(f"  • {results['reachable_percentage']:.1f}% of code is reachable through working imports")
    print(f"  • {100 - results['reachable_percentage']:.1f}% appears to be unreachable/dead code")
    
    if results['reachable_percentage'] < 20:
        print(f"  🚨 CRITICAL: Most code appears to be dead or has dependency issues")
        print(f"  💡 RECOMMENDATION: Focus on fixing imports and dependencies")
    elif results['reachable_percentage'] < 50:
        print(f"  ⚠️  WARNING: Significant amount of potentially dead code")
        print(f"  💡 RECOMMENDATION: Review and clean up unreachable modules")
    else:
        print(f"  ✅ GOOD: Most code appears to be reachable")
        print(f"  💡 RECOMMENDATION: Consider detailed testing of individual components")


if __name__ == "__main__":
    main()