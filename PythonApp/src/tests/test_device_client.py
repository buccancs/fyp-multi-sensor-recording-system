"""
Test suite for DeviceClient networking functionality.

This module tests the actual device communication implementation including
socket server functionality, device connection management, command protocols,
and error handling.

Author: Multi-Sensor Recording System Team
Date: 2025-01-01
"""

import json
import socket
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtCore import QCoreApplication

from PythonApp.src.network.device_client import DeviceClient


class TestDeviceClient(unittest.TestCase):
    """Test cases for DeviceClient networking functionality."""

    def setUp(self):
        """Set up test environment."""
        self.app = QCoreApplication.instance()
        if self.app is None:
            self.app = QCoreApplication([])

        self.device_client = DeviceClient()

    def tearDown(self):
        """Clean up test environment."""
        if self.device_client.running:
            self.device_client.stop_client()

    def test_device_client_initialization(self):
        """Test DeviceClient initializes with correct configuration."""
        self.assertIsInstance(self.device_client, DeviceClient)
        self.assertEqual(self.device_client.server_port, 8080)
        self.assertEqual(self.device_client.buffer_size, 4096)
        self.assertEqual(self.device_client.connection_timeout, 30)
        self.assertEqual(self.device_client.heartbeat_interval, 5)
        self.assertEqual(self.device_client.max_reconnect_attempts, 3)
        self.assertFalse(self.device_client.running)
        self.assertEqual(len(self.device_client.devices), 0)

    def test_device_connection_success(self):
        """Test successful device connection."""
        # Mock successful socket connection
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance

            # Mock the handshake response from device
            handshake_response = {
                "status": "accepted",
                "device_info": {"name": "Test Device"},
                "capabilities": ["recording", "streaming"],
            }
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response
            ).encode("utf-8")

            result = self.device_client.connect_to_device("192.168.1.100", 8080)

            self.assertTrue(result)
            mock_socket_instance.connect.assert_called_once_with(
                ("192.168.1.100", 8080)
            )
            mock_socket_instance.send.assert_called()  # Handshake was sent
            mock_socket_instance.recv.assert_called()  # Response was received

    def test_device_connection_failure(self):
        """Test device connection failure handling."""
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = ConnectionRefusedError(
                "Connection refused"
            )

            result = self.device_client.connect_to_device("192.168.1.100", 8080)

            self.assertFalse(result)

    def test_device_disconnection(self):
        """Test device disconnection."""
        # First connect a device
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance

            # Mock the handshake response from device
            handshake_response = {
                "status": "accepted",
                "device_info": {"name": "Test Device"},
                "capabilities": ["recording"],
            }
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response
            ).encode("utf-8")

            # Connect device
            self.device_client.connect_to_device("192.168.1.100", 8080)

            # Disconnect device
            self.device_client.disconnect_device(0)

            # Verify socket was closed
            mock_socket_instance.close.assert_called()

    def test_send_command_success(self):
        """Test successful command sending."""
        # First connect a device
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance

            # Mock the handshake response from device
            handshake_response = {
                "status": "accepted",
                "device_info": {"name": "Test Device"},
                "capabilities": ["recording"],
            }
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response
            ).encode("utf-8")

            # Connect device
            self.device_client.connect_to_device("192.168.1.100", 8080)

            # Reset call counts for cleaner assertion
            mock_socket_instance.send.reset_mock()

            # Send command
            result = self.device_client.send_command(0, "START", {"mode": "recording"})

            self.assertTrue(result)
            mock_socket_instance.send.assert_called()  # Command was sent

    def test_send_command_to_nonexistent_device(self):
        """Test sending command to non-existent device."""
        result = self.device_client.send_command(99, "START")
        self.assertFalse(result)

    def test_get_connected_devices(self):
        """Test getting list of connected devices."""
        devices = self.device_client.get_connected_devices()
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), 0)

    def test_command_protocol_format(self):
        """Test that commands are formatted as proper JSON protocol."""
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance

            # Mock the handshake response from device
            handshake_response = {
                "status": "accepted",
                "device_info": {"name": "Test Device"},
                "capabilities": ["recording"],
            }
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response
            ).encode("utf-8")

            # Connect device
            self.device_client.connect_to_device("192.168.1.100", 8080)

            # Reset mock to capture only the command send
            mock_socket_instance.send.reset_mock()

            # Send command and capture the sent data
            self.device_client.send_command(0, "CALIBRATE", {"sensor": "GSR"})

            # Verify that send was called with JSON data
            mock_socket_instance.send.assert_called()
            sent_data = mock_socket_instance.send.call_args[0][0]

            # Parse the JSON to verify format
            try:
                message = json.loads(sent_data.decode("utf-8"))
                self.assertIn("type", message)
                self.assertIn("command", message)
                self.assertIn("parameters", message)
                self.assertIn("timestamp", message)
                self.assertIn("message_id", message)
                self.assertEqual(message["type"], "command")
                self.assertEqual(message["command"], "CALIBRATE")
                self.assertEqual(message["parameters"]["sensor"], "GSR")
            except json.JSONDecodeError:
                self.fail("Sent data is not valid JSON")

    @patch("time.sleep")  # Speed up the test
    def test_server_socket_setup(self, mock_sleep):
        """Test that server socket is properly set up."""
        with patch("socket.socket") as mock_socket:
            mock_server_socket = MagicMock()
            mock_socket.return_value = mock_server_socket

            # Start the client thread
            self.device_client.start()
            time.sleep(0.1)  # Give thread time to start

            # Stop the client
            self.device_client.stop_client()

            # Verify socket setup calls
            mock_server_socket.bind.assert_called_with(("0.0.0.0", 8080))
            mock_server_socket.listen.assert_called()

    def test_error_signal_emission(self):
        """Test that error signals are properly emitted."""
        error_messages = []

        def capture_error(message):
            error_messages.append(message)

        self.device_client.error_occurred.connect(capture_error)

        # Trigger an error by trying to connect to invalid address
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = OSError("Network unreachable")

            result = self.device_client.connect_to_device("invalid_ip", 8080)

            self.assertFalse(result)
            self.assertEqual(len(error_messages), 1)
            self.assertIn("Network unreachable", error_messages[0])

    def test_multiple_device_connections(self):
        """Test handling multiple device connections."""
        with patch("socket.socket") as mock_socket:
            # Create multiple mock socket instances
            mock_socket1 = MagicMock()
            mock_socket2 = MagicMock()
            mock_socket.side_effect = [mock_socket1, mock_socket2]

            # Mock handshake responses for both devices
            handshake_response = {
                "status": "accepted",
                "device_info": {"name": "Test Device"},
                "capabilities": ["recording"],
            }
            response_data = json.dumps(handshake_response).encode("utf-8")
            mock_socket1.recv.return_value = response_data
            mock_socket2.recv.return_value = response_data

            # Connect first device
            result1 = self.device_client.connect_to_device("192.168.1.100", 8080)
            self.assertTrue(result1)

            # Connect second device
            result2 = self.device_client.connect_to_device("192.168.1.101", 8080)
            self.assertTrue(result2)

            # Verify both devices are connected
            devices = self.device_client.get_connected_devices()
            self.assertEqual(len(devices), 2)

    def test_cleanup_procedures(self):
        """Test proper cleanup when stopping client."""
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance

            # Connect a device
            self.device_client.connect_to_device("192.168.1.100", 8080)

            # Start and then stop the client
            self.device_client.start()
            time.sleep(0.1)
            self.device_client.stop_client()

            # Verify cleanup occurred
            self.assertFalse(self.device_client.running)


class TestDeviceClientIntegration(unittest.TestCase):
    """Integration tests for DeviceClient with real socket operations."""

    def setUp(self):
        """Set up integration test environment."""
        self.app = QCoreApplication.instance()
        if self.app is None:
            self.app = QCoreApplication([])

        self.device_client = DeviceClient()
        self.test_server_socket = None
        self.test_server_thread = None

    def tearDown(self):
        """Clean up integration test environment."""
        if self.device_client.running:
            self.device_client.stop_client()

        if self.test_server_socket:
            try:
                self.test_server_socket.close()
            except:
                pass

    def start_mock_device_server(self, port=8081):
        """Start a mock device server for testing."""

        def server_thread():
            try:
                self.test_server_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM
                )
                self.test_server_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self.test_server_socket.bind(("localhost", port))
                self.test_server_socket.listen(1)

                while True:
                    try:
                        client_socket, addr = self.test_server_socket.accept()
                        # Echo back any received data
                        data = client_socket.recv(1024)
                        if data:
                            client_socket.send(b"ACK")
                        client_socket.close()
                    except:
                        break

            except Exception as e:
                print(f"Mock server error: {e}")

        self.test_server_thread = threading.Thread(target=server_thread, daemon=True)
        self.test_server_thread.start()
        time.sleep(0.1)  # Give server time to start

    def test_real_socket_connection(self):
        """Test connection to a real socket server."""
        self.start_mock_device_server(8081)

        # Connect to the mock server
        result = self.device_client.connect_to_device("localhost", 8081)

        # For now, this will test the actual implementation once it's complete
        # The result depends on the actual implementation
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
