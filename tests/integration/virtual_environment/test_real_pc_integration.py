"""
Integration tests with real PC Application components

These tests validate that the virtual test environment works correctly
with the actual PythonApp PC controller components.
"""
import pytest
import asyncio
import tempfile
import logging
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
try:
    from PythonApp.network.pc_server import PCServer
    from PythonApp.network.android_device_manager import AndroidDeviceManager
    PC_APP_AVAILABLE = True
except ImportError:
    PC_APP_AVAILABLE = False
from tests.integration.virtual_environment import (
    VirtualTestConfig,
    VirtualDeviceClient,
    VirtualDeviceConfig,
    SyntheticDataGenerator,
)
@pytest.mark.skipif(not PC_APP_AVAILABLE, reason="PythonApp not available")
class TestRealPCAppIntegration:
    """Test integration with real PC application components"""
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    @pytest.fixture
    def test_logger(self):
        """Create test logger"""
        logger = logging.getLogger("RealPCAppTest")
        logger.setLevel(logging.WARNING)
        return logger
    @pytest.mark.asyncio
    async def test_virtual_device_with_real_pc_server(self, test_logger, temp_output_dir):
        """Test virtual device connecting to real PC server"""
        pc_server = PCServer(port=9001)
        try:
            await pc_server.start()
            await asyncio.sleep(0.1)
            device_config = VirtualDeviceConfig(
                device_id="real_pc_test_device",
                capabilities=["shimmer", "rgb_video", "thermal"],
                server_host="127.0.0.1",
                server_port=9001,
                response_delay_ms=50,
                heartbeat_interval_seconds=2.0
            )
            virtual_device = VirtualDeviceClient(device_config, test_logger)
            connected = await asyncio.wait_for(
                virtual_device.connect(),
                timeout=5.0
            )
            assert connected, "Virtual device should connect to real PC server"
            assert virtual_device.is_connected()
            data_generator = SyntheticDataGenerator(seed=42)
            gsr_samples = data_generator.generate_gsr_batch(10)
            for sample in gsr_samples[:3]:
                await virtual_device.send_gsr_data(sample)
                await asyncio.sleep(0.01)
            await virtual_device.disconnect()
        finally:
            await pc_server.stop()
    @pytest.mark.asyncio
    async def test_android_device_manager_with_virtual_devices(self, test_logger):
        """Test AndroidDeviceManager with virtual devices"""
        device_manager = AndroidDeviceManager(server_port=9002)
        try:
            await device_manager.start()
            await asyncio.sleep(0.1)
            devices = []
            for i in range(2):
                config = VirtualDeviceConfig(
                    device_id=f"real_manager_test_device_{i:03d}",
                    capabilities=["shimmer"],
                    server_host="127.0.0.1",
                    server_port=9002,
                    response_delay_ms=30,
                    heartbeat_interval_seconds=3.0
                )
                device = VirtualDeviceClient(config, test_logger)
                devices.append(device)
            for device in devices:
                connected = await asyncio.wait_for(
                    device.connect(),
                    timeout=3.0
                )
                assert connected, f"Device {device.device_id} should connect"
            await asyncio.sleep(0.5)
            connected_devices = device_manager.get_connected_devices()
            assert len(connected_devices) >= 2, "Device manager should see connected devices"
            for device in devices:
                await device.disconnect()
        finally:
            await device_manager.stop()
    @pytest.mark.asyncio
    async def test_protocol_compatibility(self, test_logger):
        """Test that virtual devices use compatible protocol"""
        pc_server = PCServer(port=9003)
        try:
            await pc_server.start()
            await asyncio.sleep(0.1)
            config = VirtualDeviceConfig(
                device_id="protocol_test_device",
                capabilities=["shimmer", "rgb_video", "thermal"],
                server_host="127.0.0.1",
                server_port=9003
            )
            device = VirtualDeviceClient(config, test_logger)
            assert await device.connect()
            await device.send_status_update("recording")
            await device.send_heartbeat()
            data_generator = SyntheticDataGenerator(seed=123)
            gsr_sample = data_generator.generate_gsr_sample()
            await device.send_gsr_data(gsr_sample)
            if device.config.simulate_file_transfers:
                await device.simulate_video_file_transfer("test_video.mp4")
            await device.disconnect()
        finally:
            await pc_server.stop()
    def test_pc_server_import_compatibility(self):
        """Test that we can import and use PC server components"""
        server = PCServer(port=9999)
        assert server is not None
        assert server.port == 9999
        manager = AndroidDeviceManager(server_port=9998)
        assert manager is not None
    @pytest.mark.asyncio
    async def test_stress_test_with_real_components(self, test_logger):
        """Stress test with real PC components and multiple virtual devices"""
        pc_server = PCServer(port=9004)
        try:
            await pc_server.start()
            await asyncio.sleep(0.1)
            devices = []
            for i in range(3):
                config = VirtualDeviceConfig(
                    device_id=f"stress_test_device_{i:03d}",
                    capabilities=["shimmer"],
                    server_host="127.0.0.1",
                    server_port=9004,
                    response_delay_ms=10,
                    heartbeat_interval_seconds=1.0
                )
                device = VirtualDeviceClient(config, test_logger)
                devices.append(device)
            connect_tasks = [device.connect() for device in devices]
            results = await asyncio.gather(*connect_tasks, return_exceptions=True)
            successful_connections = sum(1 for result in results if result is True)
            assert successful_connections >= 2, f"At least 2 devices should connect, got {successful_connections}"
            data_generator = SyntheticDataGenerator(seed=456)
            for device in devices:
                if device.is_connected():
                    for _ in range(5):
                        sample = data_generator.generate_gsr_sample()
                        await device.send_gsr_data(sample)
                        await asyncio.sleep(0.01)
            disconnect_tasks = [device.disconnect() for device in devices if device.is_connected()]
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        finally:
            await pc_server.stop()
@pytest.mark.skipif(PC_APP_AVAILABLE, reason="Testing import failure path")
class TestPCAppUnavailable:
    """Test behaviour when PC app components are not available"""
    def test_graceful_degradation_without_pc_app(self):
        """Test that virtual environment works without PC app components"""
        data_generator = SyntheticDataGenerator(seed=789)
        gsr_samples = data_generator.generate_gsr_batch(10)
        assert len(gsr_samples) == 10
        config = VirtualDeviceConfig(
            device_id="test_device",
            capabilities=["shimmer"]
        )
        assert config.device_id == "test_device"
pytestmark = [
    pytest.mark.integration,
    pytest.mark.network,
]
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])