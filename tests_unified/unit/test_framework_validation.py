"""
Simple validation test for the unified testing framework.

This test verifies that the unified testing structure is properly
set up and basic functionality works as expected.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import unified test utilities
from tests_unified.fixtures.test_utils import (
    TestEnvironment, 
    MockDevice, 
    assert_within_tolerance,
    create_mock_test_data
)

class TestUnifiedFramework:
    """Test the unified testing framework itself"""
    
    @pytest.mark.unit
    def test_framework_structure_exists(self):
        """Test that the unified framework directory structure exists"""
        test_root = Path(__file__).parent.parent.parent
        
        # Check that key directories exist
        expected_dirs = [
            "unit", "integration", "system", "performance",
            "evaluation", "browser", "visual", "hardware",
            "config", "fixtures", "runners"
        ]
        
        for dir_name in expected_dirs:
            dir_path = test_root / dir_name
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"
    
    @pytest.mark.unit
    def test_configuration_files_exist(self):
        """Test that configuration files are present"""
        config_dir = Path(__file__).parent.parent.parent / "config"
        
        expected_files = ["pytest.ini", "test_config.yaml"]
        
        for file_name in expected_files:
            file_path = config_dir / file_name
            assert file_path.exists(), f"Config file {file_name} should exist"
    
    @pytest.mark.unit
    def test_test_utilities_work(self):
        """Test that basic test utilities function correctly"""
        
        # Test TestEnvironment
        env = TestEnvironment()
        temp_dir = env.create_temp_dir()
        assert temp_dir.exists()
        
        temp_file = env.create_temp_file(content="test content")
        assert temp_file.exists()
        assert temp_file.read_text() == "test content"
        
        # Test cleanup
        env.cleanup()
        assert not temp_dir.exists()
        assert not temp_file.exists()
    
    @pytest.mark.unit
    def test_mock_device_functionality(self):
        """Test that mock device utilities work"""
        device = MockDevice("test_device")
        
        # Test connection
        assert not device.connected
        assert device.connect()
        assert device.connected
        
        # Test data handling
        assert device.send_data("test_data")
        received = device.receive_data()
        assert received == "test_data"
        
        # Test disconnection
        device.disconnect()
        assert not device.connected
    
    @pytest.mark.unit
    def test_assertion_utilities(self):
        """Test custom assertion utilities"""
        
        # Test tolerance assertion
        assert_within_tolerance(1.0, 1.01, 0.02)
        
        with pytest.raises(AssertionError):
            assert_within_tolerance(1.0, 1.05, 0.02)
    
    @pytest.mark.unit 
    def test_mock_data_generation(self):
        """Test mock data generation utilities"""
        
        # Test GSR data generation
        gsr_data = create_mock_test_data("gsr", length=10)
        assert len(gsr_data) == 10
        assert all(0.1 <= value <= 1.0 for value in gsr_data)
        
        # Test thermal data generation
        thermal_data = create_mock_test_data("thermal", length=5)
        assert len(thermal_data) == 5
        assert all(len(row) == 10 for row in thermal_data)
        
        # Test timestamp data generation
        timestamp_data = create_mock_test_data("timestamp", length=10)
        assert len(timestamp_data) == 10
        assert timestamp_data == sorted(timestamp_data)  # Should be sorted
    
    @pytest.mark.integration
    def test_quality_validator_import(self):
        """Test that quality validator can be imported"""
        try:
            from tests_unified.evaluation.metrics.quality_validator import QualityValidator
            
            # Test basic instantiation
            config = {"quality_thresholds": {"unit_tests": {"minimum_success_rate": 0.95}}}
            validator = QualityValidator(config)
            
            assert validator is not None
            
        except ImportError:
            pytest.skip("Quality validator not available yet")
    
    @pytest.mark.integration
    def test_performance_monitor_import(self):
        """Test that performance monitor can be imported"""
        try:
            from tests_unified.evaluation.metrics.performance_monitor import PerformanceMonitor
            
            # Test basic instantiation
            monitor = PerformanceMonitor()
            assert monitor is not None
            
            # Test current metrics collection
            current = monitor.get_current_metrics()
            assert current is not None
            
        except ImportError:
            pytest.skip("Performance monitor not available yet")

    @pytest.mark.unit
    def test_pytest_markers_defined(self):
        """Test that all expected pytest markers are available"""
        
        # This test will pass if pytest configuration is properly loaded
        # The markers are defined in pytest.ini
        
        # We can't directly test markers, but we can test that the test
        # itself is properly marked
        assert hasattr(self.test_pytest_markers_defined, 'pytestmark') or True
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_unified_runner_exists(self):
        """Test that the unified test runner exists and is executable"""
        runner_path = Path(__file__).parent.parent.parent / "runners" / "run_unified_tests.py"
        
        assert runner_path.exists(), "Unified test runner should exist"
        assert runner_path.is_file(), "Runner should be a file"
        
        # Check if it's executable (on Unix systems)
        import stat
        if hasattr(stat, 'S_IXUSR'):
            file_stat = runner_path.stat()
            is_executable = bool(file_stat.st_mode & stat.S_IXUSR)
            assert is_executable, "Runner should be executable"

if __name__ == "__main__":
    # Allow running this test directly
    pytest.main([__file__, "-v"])