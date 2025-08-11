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

# Add project root to path
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
        # Initialize real PC server
        pc_server = PCServer(port=9001)  # Use different port to avoid conflicts
        
        try:
            # Start PC server
            await pc_server.start()
            
            # Wait for server to be ready
            await asyncio.sleep(0.1)
            
            # Create virtual device
            device_config = VirtualDeviceConfig(
                device_id="real_pc_test_device",
                capabilities=["shimmer", "rgb_video", "thermal"],
                server_host="127.0.0.1",
                server_port=9001,
                response_delay_ms=50,
                heartbeat_interval_seconds=2.0
            )
            
            virtual_device = VirtualDeviceClient(device_config, test_logger)
            
            # Connect virtual device to real PC server
            connected = await asyncio.wait_for(
                virtual_device.connect(), 
                timeout=5.0
            )
            
            assert connected, "Virtual device should connect to real PC server"
            assert virtual_device.is_connected()
            
            # Send some data
            data_generator = SyntheticDataGenerator(seed=42)
            gsr_samples = data_generator.generate_gsr_batch(10)
            
            # Send GSR data
            for sample in gsr_samples[:3]:  # Send a few samples
                await virtual_device.send_gsr_data(sample)
                await asyncio.sleep(0.01)  # Small delay between samples
            
            # Clean up
            await virtual_device.disconnect()
            
        finally:
            # Ensure server is stopped
            await pc_server.stop()

    @pytest.mark.asyncio 
    async def test_android_device_manager_with_virtual_devices(self, test_logger):
        """Test AndroidDeviceManager with virtual devices"""
        # Initialize real AndroidDeviceManager
        device_manager = AndroidDeviceManager(port=9002)
        
        try:
            # Start device manager
            await device_manager.start()
            await asyncio.sleep(0.1)
            
            # Create multiple virtual devices
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
            
            # Connect all devices
            for device in devices:
                connected = await asyncio.wait_for(
                    device.connect(),
                    timeout=3.0
                )
                assert connected, f"Device {device.device_id} should connect"
            
            # Give time for device manager to register devices
            await asyncio.sleep(0.5)
            
            # Check that device manager sees the connected devices
            connected_devices = device_manager.get_connected_devices()
            assert len(connected_devices) >= 2, "Device manager should see connected devices"
            
            # Disconnect all devices
            for device in devices:
                await device.disconnect()
                
        finally:
            # Clean up
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
            
            # Test connection protocol
            assert await device.connect()
            
            # Test status message
            await device.send_status_update("recording")
            
            # Test heartbeat
            await device.send_heartbeat()
            
            # Test sensor data protocol
            data_generator = SyntheticDataGenerator(seed=123)
            gsr_sample = data_generator.generate_gsr_sample()
            await device.send_gsr_data(gsr_sample)
            
            # Test file transfer protocol (simulate)
            if device.config.simulate_file_transfers:
                await device.simulate_video_file_transfer("test_video.mp4")
            
            # Test disconnect protocol
            await device.disconnect()
            
        finally:
            await pc_server.stop()

    def test_pc_server_import_compatibility(self):
        """Test that we can import and use PC server components"""
        # Test that we can create PC server instance
        server = PCServer(port=9999)
        assert server is not None
        assert server.port == 9999
        
        # Test AndroidDeviceManager
        manager = AndroidDeviceManager(port=9998)
        assert manager is not None

    @pytest.mark.asyncio
    async def test_stress_test_with_real_components(self, test_logger):
        """Stress test with real PC components and multiple virtual devices"""
        pc_server = PCServer(port=9004)
        
        try:
            await pc_server.start()
            await asyncio.sleep(0.1)
            
            # Create multiple virtual devices for stress testing
            devices = []
            for i in range(3):  # Reduced number for CI stability
                config = VirtualDeviceConfig(
                    device_id=f"stress_test_device_{i:03d}",
                    capabilities=["shimmer"],
                    server_host="127.0.0.1",
                    server_port=9004,
                    response_delay_ms=10,  # Fast response
                    heartbeat_interval_seconds=1.0
                )
                device = VirtualDeviceClient(config, test_logger)
                devices.append(device)
            
            # Connect all devices concurrently
            connect_tasks = [device.connect() for device in devices]
            results = await asyncio.gather(*connect_tasks, return_exceptions=True)
            
            # Count successful connections
            successful_connections = sum(1 for result in results if result is True)
            assert successful_connections >= 2, f"At least 2 devices should connect, got {successful_connections}"
            
            # Send data from connected devices
            data_generator = SyntheticDataGenerator(seed=456)
            for device in devices:
                if device.is_connected():
                    for _ in range(5):  # Send 5 samples per device
                        sample = data_generator.generate_gsr_sample()
                        await device.send_gsr_data(sample)
                        await asyncio.sleep(0.01)
            
            # Disconnect all devices
            disconnect_tasks = [device.disconnect() for device in devices if device.is_connected()]
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
            
        finally:
            await pc_server.stop()


@pytest.mark.skipif(PC_APP_AVAILABLE, reason="Testing import failure path")
class TestPCAppUnavailable:
    """Test behavior when PC app components are not available"""
    
    def test_graceful_degradation_without_pc_app(self):
        """Test that virtual environment works without PC app components"""
        # Virtual environment should still work for basic functionality
        data_generator = SyntheticDataGenerator(seed=789)
        
        # Should be able to generate data
        gsr_samples = data_generator.generate_gsr_batch(10)
        assert len(gsr_samples) == 10
        
        # Should be able to create virtual device config
        config = VirtualDeviceConfig(
            device_id="test_device",
            capabilities=["shimmer"]
        )
        assert config.device_id == "test_device"


# Conditional test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.network,
]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])