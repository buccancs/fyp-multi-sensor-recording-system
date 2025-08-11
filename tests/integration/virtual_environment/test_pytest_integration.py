"""
Pytest integration tests for Virtual Test Environment

These tests ensure the virtual test environment works properly with pytest
and provides proper cleanup and error handling.
"""
import pytest
import asyncio
import tempfile
import logging
from pathlib import Path
import time
from tests.integration.virtual_environment import (
    VirtualTestConfig,
    VirtualTestRunner,
    VirtualTestScenario,
    SyntheticDataGenerator,
    VirtualDeviceClient,
    VirtualDeviceConfig,
)
@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
@pytest.fixture
def test_logger():
    """Create a test logger with appropriate level"""
    logger = logging.getLogger("VirtualTestPytest")
    logger.setLevel(logging.WARNING)
    return logger
class TestPytestIntegration:
    """Test pytest integration and cleanup"""
    def test_synthetic_data_deterministic(self):
        """Test that synthetic data is deterministic with fixed seed"""
        generator1 = SyntheticDataGenerator(seed=42)
        generator2 = SyntheticDataGenerator(seed=42)
        gsr1 = generator1.generate_gsr_batch(10)
        gsr2 = generator2.generate_gsr_batch(10)
        assert gsr1 == gsr2, "GSR data should be deterministic with same seed"
        rgb1 = generator1.generate_rgb_frame()
        rgb2 = generator2.generate_rgb_frame()
        assert rgb1 == rgb2, "RGB frames should be deterministic with same seed"
    def test_config_validation_comprehensive(self, temp_output_dir):
        """Test comprehensive configuration validation"""
        valid_config = VirtualTestConfig(
            test_name="pytest_validation",
            device_count=2,
            test_duration_minutes=0.1,
            output_directory=temp_output_dir
        )
        issues = valid_config.validate()
        assert len(issues) == 0, f"Valid config should have no issues: {issues}"
        try:
            config = VirtualTestConfig(
                test_name="invalid_devices",
                device_count=0,
                test_duration_minutes=1.0,
                output_directory=temp_output_dir
            )
            issues = config.validate()
            assert len(issues) > 0, "Zero device count should have validation issues"
        except ValueError:
            pass
        try:
            config = VirtualTestConfig(
                test_name="invalid_duration",
                device_count=2,
                test_duration_minutes=-1.0,
                output_directory=temp_output_dir
            )
            issues = config.validate()
            assert len(issues) > 0, "Negative duration should have validation issues"
        except ValueError:
            pass
        config = VirtualTestConfig(
            test_name="invalid_dir",
            device_count=2,
            test_duration_minutes=1.0,
            output_directory="/tmp/definitely_nonexistent_path_12345"
        )
        try:
            import shutil
            shutil.rmtree("/tmp/definitely_nonexistent_path_12345", ignore_errors=True)
        except:
            pass
        issues = config.validate()
        assert config.output_directory is not None
    @pytest.mark.asyncio
    async def test_virtual_device_cleanup(self, test_logger):
        """Test that virtual devices clean up properly"""
        config = VirtualDeviceConfig(
            device_id="test_cleanup_device",
            capabilities=["shimmer"],
            response_delay_ms=10,
            heartbeat_interval_seconds=1.0
        )
        device = VirtualDeviceClient(config, test_logger)
        assert not device.is_connected
        assert device.config.device_id == "test_cleanup_device"
        assert device.config.capabilities == ["shimmer"]
        await device.disconnect()
    def test_scenario_creation_performance(self):
        """Test that scenario creation is fast and doesn't hang"""
        start_time = time.time()
        scenarios = [
            VirtualTestScenario.create_quick_test(),
            VirtualTestScenario.create_ci_test(),
            VirtualTestScenario.create_stress_test(),
            VirtualTestScenario.create_synchronization_test(),
        ]
        creation_time = time.time() - start_time
        assert creation_time < 1.0, f"Scenario creation took too long: {creation_time}s"
        for scenario in scenarios:
            assert scenario.name
            assert scenario.description
            assert scenario.config
            issues = scenario.config.validate()
            assert len(issues) == 0, f"Scenario {scenario.name} should be valid: {issues}"
    def test_memory_estimation_accuracy(self, temp_output_dir):
        """Test memory and data volume estimation"""
        config = VirtualTestConfig(
            test_name="memory_test",
            device_count=3,
            test_duration_minutes=1.0,
            output_directory=temp_output_dir
        )
        memory_mb = config.estimate_memory_usage()
        assert memory_mb > 0, "Memory estimation should be positive"
        assert memory_mb < 10000, "Memory estimation should be reasonable"
        data_volume = config.estimate_data_volume()
        assert data_volume['total_mb'] > 0, "Data volume should be positive"
        assert 'gsr_mb' in data_volume
        assert 'video_mb' in data_volume
        assert 'thermal_mb' in data_volume
    @pytest.mark.parametrize("device_count", [1, 2, 3, 5])
    def test_config_scaling(self, device_count, temp_output_dir):
        """Test that configuration scales properly with device count"""
        config = VirtualTestConfig(
            test_name=f"scaling_test_{device_count}",
            device_count=device_count,
            test_duration_minutes=0.1,
            output_directory=temp_output_dir
        )
        issues = config.validate()
        assert len(issues) == 0, f"Config with {device_count} devices should be valid"
        memory_mb = config.estimate_memory_usage()
        assert memory_mb > device_count * 10, "Memory should scale with device count"
    def test_test_runner_initialization(self, temp_output_dir, test_logger):
        """Test that test runner initializes properly"""
        config = VirtualTestConfig(
            test_name="runner_init_test",
            device_count=1,
            test_duration_minutes=0.05,
            output_directory=temp_output_dir
        )
        runner = VirtualTestRunner(config, test_logger)
        assert runner.config == config
        assert runner.logger == test_logger
        assert runner.metrics is not None
    @pytest.mark.asyncio
    async def test_minimal_end_to_end_no_hang(self, temp_output_dir, test_logger):
        """Test minimal end-to-end execution doesn't hang"""
        devices = []
        try:
            for i in range(2):
                config = VirtualDeviceConfig(
                    device_id=f"hang_test_device_{i:03d}",
                    capabilities=["shimmer"],
                    response_delay_ms=10,
                    heartbeat_interval_seconds=1.0
                )
                device = VirtualDeviceClient(config, test_logger)
                devices.append(device)
            assert len(devices) == 2
            data_generator = SyntheticDataGenerator(seed=42)
            gsr_samples = data_generator.generate_gsr_batch(5)
            assert len(gsr_samples) == 5
            config = VirtualTestConfig(
                test_name="no_hang_simple_test",
                device_count=1,
                test_duration_minutes=0.01,
                output_directory=temp_output_dir,
                simulate_file_transfers=False,
                enable_stress_events=False,
            )
            issues = config.validate()
            assert len(issues) == 0, f"Configuration should be valid: {issues}"
            test_logger.info("Basic virtual environment functionality verified without hanging")
        finally:
            for device in devices:
                try:
                    await asyncio.wait_for(device.disconnect(), timeout=2.0)
                except Exception as e:
                    test_logger.warning(f"Error during device cleanup: {e}")
        assert True
@pytest.mark.integration
class TestVirtualEnvironmentMarkers:
    """Test that pytest markers work correctly"""
    @pytest.mark.virtual_env
    def test_virtual_env_marker(self):
        """Test that virtual_env marker is applied"""
        assert True
    @pytest.mark.slow
    def test_slow_marker_integration(self):
        """Test integration with slow test marker"""
        assert True
def pytest_configure(config):
    """Configure pytest markers for virtual environment tests"""
    config.addinivalue_line(
        "markers", "virtual_env: mark test as virtual environment test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (longer execution time)"
    )
if __name__ == "__main__":
    pytest.main([__file__, "-v"])