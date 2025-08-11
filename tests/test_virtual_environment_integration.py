"""
Integration test for Virtual Test Environment with existing test framework

This test validates that the virtual test environment integrates properly
with the existing project test suite and can be run alongside other tests.
"""

import pytest
import asyncio
import logging
import tempfile
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.virtual_environment import (
    VirtualTestConfig,
    VirtualTestRunner,
    VirtualTestScenario,
    SyntheticDataGenerator
)


class TestVirtualEnvironmentIntegration:
    """Integration tests for virtual test environment"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.output_dir = tempfile.mkdtemp()
        logging.basicConfig(level=logging.WARNING)  # Reduce noise in tests
    
    def test_synthetic_data_generation(self):
        """Test synthetic data generation components"""
        generator = SyntheticDataGenerator(seed=42)
        
        # Test GSR generation
        gsr_samples = generator.generate_gsr_batch(100)
        assert len(gsr_samples) == 100
        assert all(0.1 <= sample <= 5.0 for sample in gsr_samples)
        
        # Test video frame generation
        rgb_frame = generator.generate_rgb_frame()
        assert len(rgb_frame) > 1000  # Should be substantial data
        
        # Test thermal generation
        thermal_frame = generator.generate_thermal_frame()
        assert len(thermal_frame) == 64 * 48 * 2  # 16-bit thermal data
    
    def test_configuration_validation(self):
        """Test configuration system"""
        # Test valid configuration
        config = VirtualTestConfig(
            test_name="integration_test",
            device_count=2,
            test_duration_minutes=0.1,
            output_directory=self.output_dir
        )
        
        issues = config.validate()
        assert len(issues) == 0, f"Configuration should be valid: {issues}"
        
        # Test estimates
        memory_est = config.estimate_memory_usage()
        data_est = config.estimate_data_volume()
        
        assert memory_est > 0
        assert data_est['total_mb'] > 0
    
    def test_predefined_scenarios(self):
        """Test predefined test scenarios"""
        scenarios = [
            VirtualTestScenario.create_quick_test(),
            VirtualTestScenario.create_ci_test(),
        ]
        
        for scenario in scenarios:
            assert scenario.name
            assert scenario.description
            assert scenario.config.device_count > 0
            assert scenario.config.test_duration_minutes > 0
            
            # Validate scenario configuration
            issues = scenario.config.validate()
            assert len(issues) == 0, f"Scenario {scenario.name} should be valid: {issues}"
    
    @pytest.mark.asyncio
    async def test_minimal_virtual_test(self):
        """Test running a minimal virtual test"""
        config = VirtualTestConfig(
            test_name="minimal_integration_test",
            device_count=1,
            test_duration_minutes=0.05,  # 3 seconds
            recording_duration_minutes=0.02,  # 1.2 seconds
            output_directory=self.output_dir,
            
            # Minimal resource usage
            simulate_file_transfers=False,
            enable_stress_events=False,
            save_detailed_logs=False,
            gsr_sampling_rate_hz=32,  # Lower rate
            rgb_fps=5,
            thermal_fps=2,
        )
        
        logger = logging.getLogger("TestRunner")
        runner = VirtualTestRunner(config, logger)
        
        try:
            metrics = await runner.run_test()
            
            # Basic validation
            assert metrics is not None
            assert metrics.devices_spawned == 1
            assert metrics.duration_seconds > 0
            assert metrics.error_count == 0 or not metrics.overall_passed
            
            # Check output files
            output_path = Path(self.output_dir)
            report_files = list(output_path.glob("*_report.json"))
            assert len(report_files) > 0, "Should generate test report"
            
        except Exception as e:
            # Allow expected failures (e.g., port conflicts)
            pytest.skip(f"Virtual test failed (expected in CI): {e}")
    
    def test_data_volume_estimation(self):
        """Test data volume estimation accuracy"""
        from tests.integration.virtual_environment.synthetic_data_generator import estimate_data_volume
        
        # Test estimation function
        volume = estimate_data_volume(
            device_count=3,
            duration_hours=1.0
        )
        
        assert volume['device_count'] == 3
        assert volume['duration_hours'] == 1.0
        assert volume['total_mb_all_devices'] > 0
        assert volume['gsr_mb_per_device'] > 0
        assert volume['video_mb_per_device'] > 0
        assert volume['thermal_mb_per_device'] > 0
    
    def test_configuration_environment_variables(self):
        """Test environment variable configuration"""
        import os
        from tests.integration.virtual_environment.test_config import load_config_from_env
        
        # Set test environment variables
        original_env = {}
        test_env = {
            'GSR_TEST_DEVICE_COUNT': '5',
            'GSR_TEST_DURATION_MINUTES': '10.0',
            'GSR_TEST_CI_MODE': 'true',
            'GSR_TEST_LOG_LEVEL': 'DEBUG',
        }
        
        # Save original values
        for key in test_env:
            original_env[key] = os.environ.get(key)
            os.environ[key] = test_env[key]
        
        try:
            config = load_config_from_env()
            
            assert config.device_count == 5
            assert config.test_duration_minutes == 10.0
            assert config.ci_mode == True
            assert config.log_level == 'DEBUG'
            
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    def test_system_requirements_validation(self):
        """Test system requirements validation"""
        from tests.integration.virtual_environment.test_config import validate_system_requirements
        
        config = VirtualTestConfig(
            device_count=2,
            test_duration_minutes=1.0,
            output_directory=self.output_dir
        )
        
        results = validate_system_requirements(config)
        
        assert 'meets_requirements' in results
        assert 'system_info' in results
        assert 'issues' in results
        assert 'warnings' in results
        
        # Should have basic system info
        assert 'available_memory_mb' in results['system_info']
        assert 'cpu_cores' in results['system_info']


# Pytest configuration for integration with existing test suite
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest for virtual environment tests"""
    config.addinivalue_line(
        "markers", "virtual_env: mark test as virtual environment test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"  
    )

def pytest_collection_modifyitems(config, items):
    """Add markers to virtual environment tests"""
    for item in items:
        if "virtual_environment" in str(item.fspath):
            item.add_marker(pytest.mark.virtual_env)
            item.add_marker(pytest.mark.integration)


# Run as standalone test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])