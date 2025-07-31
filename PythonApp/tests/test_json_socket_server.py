#!/usr/bin/env python3
"""
Automated Test Suite for JsonSocketServer

This module provides comprehensive unit and integration tests for the JsonSocketServer
functionality, including message processing, device management, and GUI integration.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.2 - Device Connection Manager and Socket Server Testing
"""

import json
import os
import socket
import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from network.device_server import (
    JsonSocketServer,
    create_command_message,
    decode_base64_image,
)
from tests.test_device_simulator import DeviceSimulator


class TestJsonSocketServer(unittest.TestCase):
    """Test cases for JsonSocketServer functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.server = JsonSocketServer(
            host="127.0.0.1", port=9001
        )  # Use different port for testing
        self.server_thread = None

    def tearDown(self):
        """Clean up after each test method."""
        if self.server_thread and self.server_thread.is_alive():
            self.server.stop_server()
            self.server_thread.join(timeout=2)

    def start_server(self):
        """Start the server in a separate thread."""
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.5)  # Give server time to start

    def test_server_initialization(self):
        """Test server initialization."""
        self.assertEqual(self.server.host, "127.0.0.1")
        self.assertEqual(self.server.port, 9001)
        self.assertFalse(self.server.running)
        self.assertEqual(len(self.server.clients), 0)

    def test_server_start_stop(self):
        """Test server start and stop functionality."""
        # Start server
        self.start_server()
        time.sleep(0.5)
        self.assertTrue(self.server.running)

        # Stop server
        self.server.stop_server()
        time.sleep(0.5)
        self.assertFalse(self.server.running)

    def test_device_connection(self):
        """Test device connection and registration."""
        self.start_server()

        # Create mock signal handlers
        device_connected_mock = Mock()
        self.server.device_connected.connect(device_connected_mock)

        # Connect a simulated device
        device = DeviceSimulator("TestDevice1", port=9001)
        self.assertTrue(device.connect())

        # Send hello message
        self.assertTrue(device.send_hello(["camera", "thermal"]))
        time.sleep(0.5)

        # Verify device was registered
        self.assertIn("TestDevice1", self.server.clients)
        device_connected_mock.emit.assert_called_once()

        device.disconnect()

    def test_multiple_device_connections(self):
        """Test multiple simultaneous device connections."""
        self.start_server()

        devices = []
        for i in range(3):
            device = DeviceSimulator(f"TestDevice{i+1}", port=9001)
            self.assertTrue(device.connect())
            self.assertTrue(device.send_hello())
            devices.append(device)
            time.sleep(0.2)

        # Verify all devices are registered
        self.assertEqual(len(self.server.clients), 3)
        for i in range(3):
            self.assertIn(f"TestDevice{i+1}", self.server.clients)

        # Disconnect all devices
        for device in devices:
            device.disconnect()

        time.sleep(0.5)
        self.assertEqual(len(self.server.clients), 0)

    def test_message_processing(self):
        """Test different message type processing."""
        self.start_server()

        # Create mock signal handlers
        status_received_mock = Mock()
        preview_frame_mock = Mock()
        sensor_data_mock = Mock()
        notification_mock = Mock()

        self.server.status_received.connect(status_received_mock)
        self.server.preview_frame_received.connect(preview_frame_mock)
        self.server.sensor_data_received.connect(sensor_data_mock)
        self.server.notification_received.connect(notification_mock)

        # Connect device
        device = DeviceSimulator("TestDevice1", port=9001)
        self.assertTrue(device.connect())
        self.assertTrue(device.send_hello())
        time.sleep(0.2)

        # Test status message
        self.assertTrue(device.send_status(battery=75, temperature=36.0))
        time.sleep(0.2)
        status_received_mock.emit.assert_called_once()

        # Test preview frame message
        self.assertTrue(device.send_preview_frame("rgb"))
        time.sleep(0.2)
        preview_frame_mock.emit.assert_called_once()

        # Test sensor data message
        self.assertTrue(device.send_sensor_data(gsr=0.6, ppg=80.0))
        time.sleep(0.2)
        sensor_data_mock.emit.assert_called_once()

        # Test notification message
        self.assertTrue(device.send_notification("recording_started"))
        time.sleep(0.2)
        notification_mock.emit.assert_called_once()

        device.disconnect()

    def test_command_sending(self):
        """Test sending commands to devices."""
        self.start_server()

        # Connect device
        device = DeviceSimulator("TestDevice1", port=9001)
        self.assertTrue(device.connect())
        self.assertTrue(device.send_hello())
        time.sleep(0.2)

        # Test individual command
        command = create_command_message("start_recording")
        self.assertTrue(self.server.send_command("TestDevice1", command))

        # Test broadcast command
        command = create_command_message("stop_recording")
        count = self.server.broadcast_command(command)
        self.assertEqual(count, 1)

        device.disconnect()

    def test_device_disconnection(self):
        """Test device disconnection handling."""
        self.start_server()

        # Create mock signal handler
        device_disconnected_mock = Mock()
        self.server.device_disconnected.connect(device_disconnected_mock)

        # Connect and disconnect device
        device = DeviceSimulator("TestDevice1", port=9001)
        self.assertTrue(device.connect())
        self.assertTrue(device.send_hello())
        time.sleep(0.2)

        self.assertIn("TestDevice1", self.server.clients)

        device.disconnect()
        time.sleep(0.5)

        # Verify device was removed
        self.assertNotIn("TestDevice1", self.server.clients)
        device_disconnected_mock.emit.assert_called_once()

    def test_error_handling(self):
        """Test error handling for invalid messages."""
        self.start_server()

        # Create mock error handler
        error_occurred_mock = Mock()
        self.server.error_occurred.connect(error_occurred_mock)

        # Connect device
        device = DeviceSimulator("TestDevice1", port=9001)
        self.assertTrue(device.connect())

        # Send invalid JSON (this should be handled gracefully)
        try:
            device.socket.send(b"\x00\x00\x00\x05invalid")
            time.sleep(0.2)
        except:
            pass  # Expected to fail

        device.disconnect()

    def test_get_connected_devices(self):
        """Test getting list of connected devices."""
        self.start_server()

        # Initially no devices
        self.assertEqual(len(self.server.get_connected_devices()), 0)
        self.assertEqual(self.server.get_device_count(), 0)

        # Connect devices
        devices = []
        for i in range(2):
            device = DeviceSimulator(f"TestDevice{i+1}", port=9001)
            self.assertTrue(device.connect())
            self.assertTrue(device.send_hello())
            devices.append(device)
            time.sleep(0.2)

        # Check device count and list
        self.assertEqual(self.server.get_device_count(), 2)
        connected_devices = self.server.get_connected_devices()
        self.assertIn("TestDevice1", connected_devices)
        self.assertIn("TestDevice2", connected_devices)

        # Test is_device_connected
        self.assertTrue(self.server.is_device_connected("TestDevice1"))
        self.assertFalse(self.server.is_device_connected("NonExistentDevice"))

        # Disconnect devices
        for device in devices:
            device.disconnect()


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_create_command_message(self):
        """Test command message creation."""
        command = create_command_message("start_recording", session_id="test123")

        self.assertEqual(command["type"], "command")
        self.assertEqual(command["command"], "start_recording")
        self.assertEqual(command["session_id"], "test123")
        self.assertIn("timestamp", command)

    def test_decode_base64_image(self):
        """Test base64 image decoding."""
        # Test valid base64 data
        test_data = b"test image data"
        import base64

        encoded_data = base64.b64encode(test_data).decode("utf-8")

        decoded = decode_base64_image(encoded_data)
        self.assertEqual(decoded, test_data)

        # Test data URL format
        data_url = f"data:image/png;base64,{encoded_data}"
        decoded = decode_base64_image(data_url)
        self.assertEqual(decoded, test_data)

        # Test invalid data
        invalid_decoded = decode_base64_image("invalid_base64_data")
        self.assertIsNone(invalid_decoded)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.server = JsonSocketServer(host="127.0.0.1", port=9002)
        self.server_thread = None

    def tearDown(self):
        """Clean up after tests."""
        if self.server_thread and self.server_thread.is_alive():
            self.server.stop_server()
            self.server_thread.join(timeout=2)

    def start_server(self):
        """Start server in separate thread."""
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.5)

    def test_complete_device_lifecycle(self):
        """Test complete device connection lifecycle."""
        self.start_server()

        # Track all signals
        signals_received = {
            "device_connected": [],
            "status_received": [],
            "preview_frame_received": [],
            "ack_received": [],
            "device_disconnected": [],
        }

        def track_signal(signal_name):
            def handler(*args):
                signals_received[signal_name].append(args)

            return handler

        self.server.device_connected.connect(track_signal("device_connected"))
        self.server.status_received.connect(track_signal("status_received"))
        self.server.preview_frame_received.connect(
            track_signal("preview_frame_received")
        )
        self.server.ack_received.connect(track_signal("ack_received"))
        self.server.device_disconnected.connect(track_signal("device_disconnected"))

        # Complete device lifecycle
        device = DeviceSimulator("LifecycleDevice", port=9002)

        # 1. Connect and register
        self.assertTrue(device.connect())
        self.assertTrue(device.send_hello(["camera", "thermal", "imu"]))
        time.sleep(0.2)

        # 2. Send various messages
        self.assertTrue(device.send_status(battery=80))
        self.assertTrue(device.send_preview_frame("rgb"))
        time.sleep(0.2)

        # 3. Receive and acknowledge command
        command = create_command_message("start_recording")
        self.assertTrue(self.server.send_command("LifecycleDevice", command))
        time.sleep(0.1)
        self.assertTrue(device.send_ack("start_recording", success=True))
        time.sleep(0.2)

        # 4. Disconnect
        device.disconnect()
        time.sleep(0.5)

        # Verify all signals were received
        self.assertEqual(len(signals_received["device_connected"]), 1)
        self.assertEqual(len(signals_received["status_received"]), 1)
        self.assertEqual(len(signals_received["preview_frame_received"]), 1)
        self.assertEqual(len(signals_received["ack_received"]), 1)
        self.assertEqual(len(signals_received["device_disconnected"]), 1)

    def test_concurrent_device_operations(self):
        """Test concurrent operations with multiple devices."""
        self.start_server()

        # Connect multiple devices
        devices = []
        for i in range(3):
            device = DeviceSimulator(f"ConcurrentDevice{i+1}", port=9002)
            self.assertTrue(device.connect())
            self.assertTrue(device.send_hello())
            devices.append(device)
            time.sleep(0.1)

        # Send messages concurrently
        threads = []
        for i, device in enumerate(devices):

            def send_messages(dev, device_num):
                dev.send_status(battery=90 - device_num * 10)
                dev.send_preview_frame("rgb" if device_num % 2 == 0 else "thermal")
                dev.send_sensor_data(gsr=0.5 + device_num * 0.1)

            thread = threading.Thread(target=send_messages, args=(device, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        time.sleep(0.5)

        # Verify all devices are still connected
        self.assertEqual(self.server.get_device_count(), 3)

        # Test broadcast command
        command = create_command_message("stop_recording")
        count = self.server.broadcast_command(command)
        self.assertEqual(count, 3)

        # Disconnect all devices
        for device in devices:
            device.disconnect()

        time.sleep(0.5)
        self.assertEqual(self.server.get_device_count(), 0)


def run_tests():
    """Run all test suites."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestJsonSocketServer))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunctions))
    test_suite.addTest(unittest.makeSuite(TestIntegrationScenarios))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
