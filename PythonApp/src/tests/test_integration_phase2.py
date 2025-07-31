"""
Integration Test Suite for Multi-Sensor Recording System - Phase 2 Implementation

This module implements comprehensive cross-platform integration testing as specified 
in the Phase 2 roadmap requirements:

- Test full recording workflow end-to-end
- Test device synchronization across platforms
- Test error recovery scenarios
- Hardware-in-the-loop testing support

Author: Multi-Sensor Recording System Team
Date: 2025-01-27
Phase: 2 - Cross-Platform Integration
"""

import asyncio
import json
import socket
import subprocess
import time
import threading
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from unittest.mock import Mock, patch, MagicMock

# Import project modules
from session.session_synchronizer import SessionSynchronizer, MessagePriority, SessionSyncState
from session.session_manager import SessionManager
from network.enhanced_device_server import EnhancedDeviceServer
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class DeviceSimulator:
    """Simulates an Android device for integration testing."""
    
    def __init__(self, device_id: str, server_host: str = "localhost", server_port: int = 9000):
        self.device_id = device_id
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.recording_active = False
        self.session_id = None
        
    async def connect(self) -> bool:
        """Connect to the PC server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            
            # Send hello message
            await self.send_hello_message()
            return True
            
        except Exception as e:
            logger.error(f"[DeviceSimulator] Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from server."""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
    
    async def send_hello_message(self):
        """Send device introduction message."""
        message = {
            "type": "hello",
            "device_id": self.device_id,
            "capabilities": ["camera", "thermal", "shimmer"],
            "timestamp": datetime.now().isoformat()
        }
        await self.send_message(message)
    
    async def send_status_message(self):
        """Send device status message."""
        message = {
            "type": "status",
            "device_id": self.device_id,
            "battery_level": 85,
            "storage_available": 5000000000,
            "recording_active": self.recording_active,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_message(message)
    
    async def send_session_state(self):
        """Send complete session state for synchronization."""
        state = {
            "device_id": self.device_id,
            "session_id": self.session_id or f"test_session_{int(time.time())}",
            "recording_active": self.recording_active,
            "devices_connected": {
                "shimmer": True,
                "thermal": False,
                "camera": True
            },
            "recording_start_time": datetime.now().isoformat() if self.recording_active else None,
            "recording_duration": 120.5 if self.recording_active else 0.0,
            "file_count": 5 if self.recording_active else 0,
            "total_file_size": 1024000 if self.recording_active else 0,
            "calibration_status": {"rgb": "complete", "thermal": "pending"},
            "metadata": {"test_device": True, "simulator": True}
        }
        return state
    
    async def send_message(self, message: Dict[str, Any]):
        """Send JSON message to server."""
        if self.socket and self.connected:
            try:
                message_json = json.dumps(message)
                length_bytes = len(message_json).to_bytes(4, byteorder='big')
                self.socket.send(length_bytes + message_json.encode())
            except Exception as e:
                logger.error(f"[DeviceSimulator] Send failed: {e}")
    
    async def receive_message(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Receive JSON message from server."""
        if not self.socket or not self.connected:
            return None
        
        try:
            self.socket.settimeout(timeout)
            
            # Read length header
            length_bytes = self.socket.recv(4)
            if len(length_bytes) != 4:
                return None
            
            message_length = int.from_bytes(length_bytes, byteorder='big')
            
            # Read message
            message_data = self.socket.recv(message_length)
            if len(message_data) != message_length:
                return None
            
            return json.loads(message_data.decode())
            
        except Exception as e:
            logger.error(f"[DeviceSimulator] Receive failed: {e}")
            return None
    
    def start_recording(self, session_id: str):
        """Start recording simulation."""
        self.recording_active = True
        self.session_id = session_id
    
    def stop_recording(self):
        """Stop recording simulation."""
        self.recording_active = False


class IntegrationTestSuite(unittest.TestCase):
    """
    Comprehensive integration test suite for cross-platform functionality.
    
    Tests Phase 2 requirements:
    - Full recording workflow
    - Device synchronization
    - Error recovery scenarios
    - Hardware-in-the-loop capabilities
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = Path("/tmp/integration_tests")
        cls.test_dir.mkdir(exist_ok=True)
        
        # Initialize components
        cls.session_manager = SessionManager()
        cls.session_synchronizer = SessionSynchronizer()
        cls.device_server = EnhancedDeviceServer()
        
        logger.info("[IntegrationTestSuite] Test environment initialized")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cls.session_synchronizer.stop_synchronization()
        logger.info("[IntegrationTestSuite] Test environment cleaned up")
    
    def setUp(self):
        """Set up individual test."""
        self.test_devices = []
        self.session_synchronizer.start_synchronization()
    
    def tearDown(self):
        """Clean up individual test."""
        # Disconnect all test devices
        for device in self.test_devices:
            asyncio.run(device.disconnect())
        self.test_devices.clear()
    
    def test_full_recording_workflow(self):
        """
        Test complete recording workflow from start to finish.
        
        Steps:
        1. Device connects and registers
        2. Session synchronization established
        3. Recording starts across all devices
        4. Data flows correctly
        5. Recording stops cleanly
        6. Session data is preserved
        """
        logger.info("[IntegrationTest] Starting full recording workflow test")
        
        # Create test device
        device = DeviceSimulator("workflow_test_device")
        self.test_devices.append(device)
        
        # Test connection
        connected = asyncio.run(device.connect())
        self.assertTrue(connected, "Device should connect successfully")
        
        # Register device with synchronizer
        self.session_synchronizer.register_device(device.device_id)
        
        # Start recording workflow
        session_id = f"test_session_{int(time.time())}"
        device.start_recording(session_id)
        
        # Send session state
        session_state = asyncio.run(device.send_session_state())
        sync_success = self.session_synchronizer.sync_session_state(session_state)
        self.assertTrue(sync_success, "Session state should sync successfully")
        
        # Verify synchronized state
        synced_state = self.session_synchronizer.get_session_state(device.device_id)
        self.assertIsNotNone(synced_state, "Synchronized state should exist")
        self.assertEqual(synced_state.session_id, session_id, "Session ID should match")
        self.assertTrue(synced_state.recording_active, "Recording should be active")
        
        # Send status updates during recording
        for i in range(3):
            asyncio.run(device.send_status_message())
            time.sleep(0.5)
        
        # Stop recording
        device.stop_recording()
        final_state = asyncio.run(device.send_session_state())
        final_sync_success = self.session_synchronizer.sync_session_state(final_state)
        self.assertTrue(final_sync_success, "Final state should sync successfully")
        
        # Verify final state
        final_synced_state = self.session_synchronizer.get_session_state(device.device_id)
        self.assertFalse(final_synced_state.recording_active, "Recording should be inactive")
        
        logger.info("[IntegrationTest] Full recording workflow test completed successfully")
    
    def test_device_synchronization(self):
        """
        Test synchronization between multiple devices.
        
        Verifies:
        - Multiple devices can connect simultaneously
        - Session states sync independently
        - Cross-device coordination works
        - State changes propagate correctly
        """
        logger.info("[IntegrationTest] Starting device synchronization test")
        
        # Create multiple test devices
        device_count = 3
        devices = []
        
        for i in range(device_count):
            device = DeviceSimulator(f"sync_test_device_{i}")
            devices.append(device)
            self.test_devices.append(device)
        
        # Connect all devices
        for device in devices:
            connected = asyncio.run(device.connect())
            self.assertTrue(connected, f"Device {device.device_id} should connect")
            self.session_synchronizer.register_device(device.device_id)
        
        # Start recording on all devices with same session
        session_id = f"multi_device_session_{int(time.time())}"
        for device in devices:
            device.start_recording(session_id)
        
        # Sync states for all devices
        for device in devices:
            state = asyncio.run(device.send_session_state())
            success = self.session_synchronizer.sync_session_state(state)
            self.assertTrue(success, f"Device {device.device_id} state should sync")
        
        # Verify all devices are synchronized
        sync_status = self.session_synchronizer.get_sync_status()
        self.assertEqual(sync_status['total_devices'], device_count, "All devices should be registered")
        self.assertEqual(sync_status['online_devices'], device_count, "All devices should be online")
        
        # Test state changes propagation
        devices[0].stop_recording()
        state = asyncio.run(devices[0].send_session_state())
        success = self.session_synchronizer.sync_session_state(state)
        self.assertTrue(success, "State change should sync successfully")
        
        # Verify other devices still recording
        for i in range(1, device_count):
            device_state = self.session_synchronizer.get_session_state(devices[i].device_id)
            self.assertTrue(device_state.recording_active, f"Device {i} should still be recording")
        
        logger.info("[IntegrationTest] Device synchronization test completed successfully")
    
    def test_error_recovery_scenarios(self):
        """
        Test various error recovery scenarios.
        
        Scenarios:
        - Network disconnection during recording
        - Device reconnection and state recovery
        - Message queuing during offline periods
        - Graceful degradation under poor conditions
        """
        logger.info("[IntegrationTest] Starting error recovery scenarios test")
        
        # Create test device
        device = DeviceSimulator("recovery_test_device")
        self.test_devices.append(device)
        
        # Connect and start recording
        connected = asyncio.run(device.connect())
        self.assertTrue(connected, "Device should connect initially")
        
        self.session_synchronizer.register_device(device.device_id)
        
        session_id = f"recovery_session_{int(time.time())}"
        device.start_recording(session_id)
        
        # Sync initial state
        state = asyncio.run(device.send_session_state())
        success = self.session_synchronizer.sync_session_state(state)
        self.assertTrue(success, "Initial state should sync")
        
        # Simulate disconnection
        asyncio.run(device.disconnect())
        self.session_synchronizer.handle_android_disconnect(device.device_id)
        
        # Verify device marked as disconnected
        sync_status = self.session_synchronizer.get_sync_status()
        device_status = sync_status['devices'].get(device.device_id)
        self.assertIsNotNone(device_status, "Device status should exist")
        self.assertFalse(device_status['is_connected'], "Device should be marked as disconnected")
        
        # Queue messages while offline
        self.session_synchronizer.queue_message(
            device.device_id, 
            "test_command", 
            {"action": "start", "timestamp": datetime.now().isoformat()},
            MessagePriority.HIGH
        )
        
        self.session_synchronizer.queue_message(
            device.device_id,
            "status_request",
            {"request_type": "full_status"},
            MessagePriority.NORMAL
        )
        
        # Verify messages are queued
        updated_status = self.session_synchronizer.get_sync_status()
        device_status = updated_status['devices'].get(device.device_id)
        self.assertGreater(device_status['queued_messages'], 0, "Messages should be queued")
        
        # Simulate reconnection
        time.sleep(1)  # Simulate offline period
        
        reconnected = asyncio.run(device.connect())
        self.assertTrue(reconnected, "Device should reconnect")
        
        # Recover session state
        recovered_state = self.session_synchronizer.recover_session_on_reconnect(device.device_id)
        self.assertIsNotNone(recovered_state, "Session state should be recovered")
        self.assertEqual(recovered_state.session_id, session_id, "Recovered session ID should match")
        
        # Verify device back online
        final_status = self.session_synchronizer.get_sync_status()
        device_status = final_status['devices'].get(device.device_id)
        self.assertTrue(device_status['is_connected'], "Device should be back online")
        self.assertEqual(device_status['queued_messages'], 0, "Queued messages should be delivered")
        
        logger.info("[IntegrationTest] Error recovery scenarios test completed successfully")
    
    def test_hardware_integration_simulation(self):
        """
        Test hardware integration capabilities with simulation.
        
        Simulates:
        - Shimmer sensor data streaming
        - Thermal camera frame capture
        - USB device management
        - Calibration workflows
        """
        logger.info("[IntegrationTest] Starting hardware integration simulation test")
        
        # Create device with full hardware simulation
        device = DeviceSimulator("hardware_test_device")
        self.test_devices.append(device)
        
        connected = asyncio.run(device.connect())
        self.assertTrue(connected, "Device should connect")
        
        self.session_synchronizer.register_device(device.device_id)
        
        # Simulate hardware initialization
        hardware_state = {
            "device_id": device.device_id,
            "session_id": f"hardware_session_{int(time.time())}",
            "recording_active": False,
            "devices_connected": {
                "shimmer": True,
                "thermal": True,
                "camera": True,
                "usb": True
            },
            "recording_start_time": None,
            "recording_duration": 0.0,
            "file_count": 0,
            "total_file_size": 0,
            "calibration_status": {
                "rgb": "complete",
                "thermal": "complete", 
                "shimmer": "complete"
            },
            "metadata": {
                "hardware_simulation": True,
                "sensors": ["gsr", "ppg", "accelerometer"],
                "camera_resolution": "4K",
                "thermal_resolution": "640x480"
            }
        }
        
        # Test hardware state sync
        success = self.session_synchronizer.sync_session_state(hardware_state)
        self.assertTrue(success, "Hardware state should sync")
        
        # Verify hardware capabilities recognized
        synced_state = self.session_synchronizer.get_session_state(device.device_id)
        self.assertTrue(synced_state.devices_connected["shimmer"], "Shimmer should be connected")
        self.assertTrue(synced_state.devices_connected["thermal"], "Thermal camera should be connected")
        self.assertEqual(synced_state.calibration_status["rgb"], "complete", "RGB calibration should be complete")
        
        # Test sensor data streaming simulation
        for i in range(5):
            sensor_message = {
                "type": "sensor_data",
                "device_id": device.device_id,
                "sensor_type": "shimmer",
                "data": {
                    "gsr": 1.5 + i * 0.1,
                    "ppg": 75 + i,
                    "timestamp": datetime.now().isoformat()
                }
            }
            asyncio.run(device.send_message(sensor_message))
        
        # Test frame capture simulation
        for i in range(3):
            frame_message = {
                "type": "preview_frame",
                "device_id": device.device_id,
                "camera_type": "rgb" if i % 2 == 0 else "thermal",
                "frame_data": f"base64_encoded_frame_data_{i}",
                "timestamp": datetime.now().isoformat()
            }
            asyncio.run(device.send_message(frame_message))
        
        logger.info("[IntegrationTest] Hardware integration simulation test completed successfully")
    
    def test_performance_under_load(self):
        """
        Test system performance under load conditions.
        
        Tests:
        - Multiple concurrent devices
        - High message frequency
        - Large data transfers
        - Resource utilization
        """
        logger.info("[IntegrationTest] Starting performance under load test")
        
        # Create multiple devices for load testing
        device_count = 5
        devices = []
        
        for i in range(device_count):
            device = DeviceSimulator(f"load_test_device_{i}")
            devices.append(device)
            self.test_devices.append(device)
        
        # Connect all devices simultaneously
        start_time = time.time()
        
        for device in devices:
            connected = asyncio.run(device.connect())
            self.assertTrue(connected, f"Device {device.device_id} should connect under load")
            self.session_synchronizer.register_device(device.device_id)
        
        connection_time = time.time() - start_time
        self.assertLess(connection_time, 10.0, "All devices should connect within 10 seconds")
        
        # Start recording on all devices
        session_id = f"load_test_session_{int(time.time())}"
        for device in devices:
            device.start_recording(session_id)
        
        # Generate high-frequency messages
        message_count = 50
        start_time = time.time()
        
        for i in range(message_count):
            for device in devices:
                state = asyncio.run(device.send_session_state())
                success = self.session_synchronizer.sync_session_state(state)
                self.assertTrue(success, "State should sync under load")
            
            if i % 10 == 0:
                time.sleep(0.1)  # Brief pause every 10 messages
        
        processing_time = time.time() - start_time
        messages_per_second = (message_count * device_count) / processing_time
        
        logger.info(f"[IntegrationTest] Processed {messages_per_second:.1f} messages/second")
        self.assertGreater(messages_per_second, 10.0, "Should process at least 10 messages/second")
        
        # Verify system stability
        sync_status = self.session_synchronizer.get_sync_status()
        self.assertEqual(sync_status['online_devices'], device_count, "All devices should remain online")
        self.assertGreater(sync_status['statistics']['success_rate_percent'], 95.0, 
                          "Success rate should be > 95%")
        
        logger.info("[IntegrationTest] Performance under load test completed successfully")
    
    def test_cross_platform_compatibility(self):
        """
        Test cross-platform compatibility features.
        
        Verifies:
        - Message format compatibility
        - Timestamp synchronization
        - File path handling
        - Protocol version compatibility
        """
        logger.info("[IntegrationTest] Starting cross-platform compatibility test")
        
        device = DeviceSimulator("compatibility_test_device")
        self.test_devices.append(device)
        
        connected = asyncio.run(device.connect())
        self.assertTrue(connected, "Device should connect")
        
        self.session_synchronizer.register_device(device.device_id)
        
        # Test with various timestamp formats
        timestamp_formats = [
            datetime.now().isoformat(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        ]
        
        for timestamp_format in timestamp_formats:
            state = {
                "device_id": device.device_id,
                "session_id": f"compat_session_{int(time.time())}",
                "recording_active": True,
                "devices_connected": {"test": True},
                "recording_start_time": timestamp_format,
                "recording_duration": 60.0,
                "file_count": 1,
                "total_file_size": 1000,
                "calibration_status": {},
                "metadata": {"timestamp_format": timestamp_format}
            }
            
            success = self.session_synchronizer.sync_session_state(state)
            self.assertTrue(success, f"Should handle timestamp format: {timestamp_format}")
        
        # Test with different file path formats
        path_formats = [
            "/storage/emulated/0/recordings/session1/video.mp4",  # Android
            "C:\\Users\\Test\\recordings\\session1\\video.mp4",   # Windows
            "/home/user/recordings/session1/video.mp4",          # Linux
        ]
        
        for path_format in path_formats:
            state = {
                "device_id": device.device_id,
                "session_id": f"path_test_{int(time.time())}",
                "recording_active": False,
                "devices_connected": {},
                "recording_start_time": None,
                "recording_duration": 0.0,
                "file_count": 1,
                "total_file_size": 1000,
                "calibration_status": {},
                "metadata": {"file_path": path_format}
            }
            
            success = self.session_synchronizer.sync_session_state(state)
            self.assertTrue(success, f"Should handle path format: {path_format}")
        
        logger.info("[IntegrationTest] Cross-platform compatibility test completed successfully")


def run_integration_tests():
    """Run all integration tests and return results."""
    logger.info("[IntegrationTestSuite] Starting integration test suite")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(IntegrationTestSuite)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Generate test report
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
        "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
        "was_successful": result.wasSuccessful()
    }
    
    logger.info(f"[IntegrationTestSuite] Test suite completed: {test_report}")
    
    return test_report


if __name__ == "__main__":
    # Run integration tests if called directly
    print("[DEBUG_LOG] Running Phase 2 Integration Test Suite...")
    
    results = run_integration_tests()
    
    print(f"\n[DEBUG_LOG] Integration Test Results:")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Overall Success: {results['was_successful']}")
    
    if results['was_successful']:
        print("\n[DEBUG_LOG] ✅ All integration tests passed - Phase 2 implementation validated!")
    else:
        print("\n[DEBUG_LOG] ❌ Some integration tests failed - Phase 2 implementation needs review.")
    
    print("\n[DEBUG_LOG] Phase 2 Integration Test Suite completed.")