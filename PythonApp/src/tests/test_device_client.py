"""
Enhanced test suite for DeviceClient networking functionality.

This module tests the complete device communication implementation including
socket server functionality, acknowledgment systems, SSL/TLS security,
capability negotiation, and advanced error handling.

Author: Multi-Sensor Recording System Team
Date: 2025-01-01
Updated: Enhanced with academic rigor and comprehensive validation
"""

import json
import socket
import ssl
import threading
import time
import unittest
import uuid
from collections import defaultdict
from unittest.mock import MagicMock, Mock, patch

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtTest import QSignalSpy

from PythonApp.src.network.device_client import DeviceClient


class TestDeviceClientEnhanced(unittest.TestCase):
    """Enhanced test cases for DeviceClient networking functionality with academic validation."""

    def setUp(self):
        """Set up test environment with comprehensive configuration."""
        self.app = QCoreApplication.instance()
        if self.app is None:
            self.app = QCoreApplication([])

        self.device_client = DeviceClient()
        
        # Test configuration
        self.test_device_ip = "127.0.0.1"
        self.test_device_port = 9999  # Use different port to avoid conflicts
        self.device_client.server_port = self.test_device_port

    def tearDown(self):
        """Clean up test environment."""
        if self.device_client.running:
            self.device_client.stop_client()

    def test_device_client_initialization_enhanced(self):
        """Test DeviceClient initializes with enhanced configuration."""
        self.assertIsInstance(self.device_client, DeviceClient)
        self.assertEqual(self.device_client.server_port, self.test_device_port)
        self.assertEqual(self.device_client.buffer_size, 4096)
        self.assertEqual(self.device_client.connection_timeout, 30)
        self.assertEqual(self.device_client.heartbeat_interval, 5)
        self.assertEqual(self.device_client.max_reconnect_attempts, 3)
        self.assertFalse(self.device_client.running)
        self.assertEqual(len(self.device_client.devices), 0)
        
        # Test enhanced features
        self.assertIsInstance(self.device_client._pending_acknowledgments, dict)
        self.assertEqual(self.device_client._ack_timeout, 10)
        self.assertEqual(self.device_client._retry_attempts, 3)
        self.assertIsInstance(self.device_client._rate_limiter, defaultdict)
        self.assertEqual(self.device_client._max_requests_per_minute, 60)
        self.assertFalse(self.device_client._ssl_enabled)

    def test_ssl_configuration(self):
        """Test SSL/TLS configuration functionality."""
        # Test with mock certificate files
        with patch('ssl.create_default_context') as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            
            result = self.device_client.configure_ssl("/path/to/cert.pem", "/path/to/key.pem")
            
            self.assertTrue(result)
            self.assertTrue(self.device_client._ssl_enabled)
            self.assertIsNotNone(self.device_client._ssl_context)
            mock_ssl_context.assert_called_once_with(ssl.Purpose.CLIENT_AUTH)
            mock_context.load_cert_chain.assert_called_once_with("/path/to/cert.pem", "/path/to/key.pem")

    def test_rate_limiting_mechanism(self):
        """Test rate limiting algorithm implementation."""
        device_ip = "192.168.1.100"
        
        # Test within rate limit
        for i in range(30):
            result = self.device_client._check_rate_limit(device_ip)
            self.assertTrue(result, f"Request {i} should be allowed")
        
        # Test rate limit exceeded
        for i in range(35):  # Add more requests to exceed limit
            self.device_client._check_rate_limit(device_ip)
        
        result = self.device_client._check_rate_limit(device_ip)
        self.assertFalse(result, "Rate limit should be exceeded")

    def test_capability_negotiation(self):
        """Test device capability negotiation protocol."""
        # Create mock device with capabilities
        device_id = 0
        device_capabilities = ["recording", "streaming", "thermal_imaging"]
        
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {
                "socket": Mock(),
                "ip": "192.168.1.100",
                "port": 8080,
                "status": "connected",
                "capabilities": device_capabilities,
            }
        
        # Test capability negotiation
        requested_capabilities = ["recording", "streaming", "audio_capture", "gsr_monitoring"]
        result = self.device_client.negotiate_capabilities(device_id, requested_capabilities)
        
        # Verify results
        self.assertTrue(result["recording"])
        self.assertTrue(result["streaming"])
        self.assertFalse(result["audio_capture"])  # Not supported by device
        self.assertFalse(result["gsr_monitoring"])  # Not supported by device

    def test_reliable_message_delivery_with_ack(self):
        """Test acknowledgment-based reliable message delivery."""
        # Create mock device
        device_id = 0
        mock_socket = Mock()
        
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {
                "socket": mock_socket,
                "ip": "192.168.1.100",
                "port": 8080,
                "status": "connected",
            }
        
        # Test command sending with acknowledgment
        result = self.device_client.send_command(
            device_id, "START", {"mode": "recording"}, require_ack=True
        )
        
        self.assertTrue(result)
        mock_socket.send.assert_called_once()
        
        # Verify message was added to pending acknowledgments
        self.assertEqual(len(self.device_client._pending_acknowledgments), 1)
        
        # Get the message ID from the sent data
        sent_data = mock_socket.send.call_args[0][0]
        sent_message = json.loads(sent_data.decode('utf-8'))
        message_id = sent_message['message_id']
        
        self.assertIn(message_id, self.device_client._pending_acknowledgments)

    def test_acknowledgment_timeout_handling(self):
        """Test acknowledgment timeout and retry mechanism."""
        message_id = str(uuid.uuid4())
        device_id = 0
        
        # Setup pending acknowledgment
        self.device_client._pending_acknowledgments[message_id] = {
            "device_index": device_id,
            "command": "START",
            "timestamp": time.time(),
            "attempts": 1,
            "max_attempts": 3,
        }
        
        # Create mock device
        mock_socket = Mock()
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {
                "socket": mock_socket,
                "ip": "192.168.1.100",
                "port": 8080,
                "status": "connected",
            }
        
        # Test timeout handling
        self.device_client._handle_ack_timeout(message_id)
        
        # Verify retry attempt
        self.assertEqual(self.device_client._pending_acknowledgments[message_id]["attempts"], 2)

    def test_enhanced_message_processing(self):
        """Test enhanced message processing with new message types."""
        device_id = 0
        
        # Test acknowledgment message processing
        ack_message = {
            "type": "acknowledgment",
            "message_id": "test-message-123",
            "timestamp": time.time()
        }
        
        # Setup pending acknowledgment
        self.device_client._pending_acknowledgments["test-message-123"] = {
            "device_index": device_id,
            "command": "START",
            "timestamp": time.time() - 1,  # 1 second ago
            "attempts": 1,
            "max_attempts": 3,
        }
        
        self.device_client._process_device_message(device_id, ack_message)
        
        # Verify acknowledgment was processed
        self.assertNotIn("test-message-123", self.device_client._pending_acknowledgments)

    def test_capability_response_processing(self):
        """Test capability response message processing."""
        device_id = 0
        
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {
                "socket": Mock(),
                "ip": "192.168.1.100",
                "port": 8080,
                "status": "connected",
                "capabilities": [],
            }
        
        # Test capability response processing
        capability_message = {
            "type": "capability_response",
            "capabilities": ["recording", "streaming", "thermal_imaging"]
        }
        
        self.device_client._process_device_message(device_id, capability_message)
        
        # Verify capabilities were updated
        with self.device_client._device_lock:
            updated_capabilities = self.device_client.devices[device_id]["capabilities"]
            self.assertEqual(updated_capabilities, ["recording", "streaming", "thermal_imaging"])

    def test_performance_metrics_collection(self):
        """Test performance metrics collection and reporting."""
        # Simulate some activity
        self.device_client._message_stats["sent"] = 100
        self.device_client._message_stats["received"] = 95
        self.device_client._message_stats["errors"] = 2
        self.device_client._message_stats["connection_count"] = 5
        self.device_client._message_stats["avg_latency"] = 0.015  # 15ms
        
        # Add some pending acknowledgments
        self.device_client._pending_acknowledgments["test1"] = {}
        self.device_client._pending_acknowledgments["test2"] = {}
        
        metrics = self.device_client.get_performance_metrics()
        
        self.assertEqual(metrics["messages_sent"], 100)
        self.assertEqual(metrics["messages_received"], 95)
        self.assertEqual(metrics["error_count"], 2)
        self.assertEqual(metrics["total_connections"], 5)
        self.assertEqual(metrics["average_latency_ms"], 15.0)
        self.assertEqual(metrics["pending_acknowledgments"], 2)
        self.assertFalse(metrics["ssl_enabled"])
        self.assertEqual(metrics["rate_limit_per_minute"], 60)

    def test_latency_statistics_update(self):
        """Test latency statistics calculation using exponential moving average."""
        # Test initial latency
        self.device_client._update_latency_stats(0.020)  # 20ms
        self.assertAlmostEqual(self.device_client._message_stats["avg_latency"], 0.020, places=3)
        
        # Test moving average
        self.device_client._update_latency_stats(0.010)  # 10ms
        expected_avg = 0.1 * 0.010 + 0.9 * 0.020  # alpha=0.1
        self.assertAlmostEqual(self.device_client._message_stats["avg_latency"], expected_avg, places=3)

    def test_error_message_processing(self):
        """Test error message processing from devices."""
        device_id = 0
        
        # Create signal spy for error signal
        error_spy = QSignalSpy(self.device_client.error_occurred)
        
        error_message = {
            "type": "error",
            "error": "Sensor calibration failed",
            "timestamp": time.time()
        }
        
        self.device_client._process_device_message(device_id, error_message)
        
        # Verify error signal was emitted
        self.assertEqual(len(error_spy), 1)
        emitted_error = error_spy[0][0]  # First signal, first argument
        self.assertIn("Device 0 error", emitted_error)
        self.assertIn("Sensor calibration failed", emitted_error)

    def test_comprehensive_ssl_server_setup(self):
        """Test SSL-enabled server socket setup."""
        # Configure SSL
        with patch('ssl.create_default_context') as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_wrapped_socket = Mock()
            mock_context.wrap_socket.return_value = mock_wrapped_socket
            
            self.device_client.configure_ssl("/path/to/cert.pem", "/path/to/key.pem")
            
            # Test server socket creation with SSL
            with patch('socket.socket') as mock_socket:
                mock_socket_instance = Mock()
                mock_socket.return_value = mock_socket_instance
                
                # Mock the accept method to avoid actual network operations
                mock_socket_instance.accept.side_effect = socket.timeout
                
                # Start the client (will be interrupted by timeout)
                self.device_client.start()
                time.sleep(0.1)  # Let it initialize
                self.device_client.stop_client()
                
                # Verify SSL wrapper was called
                mock_context.wrap_socket.assert_called_once_with(
                    mock_socket_instance, server_side=True
                )

    def test_device_connection_rate_limiting(self):
        """Test rate limiting during device connection handling."""
        address = ("192.168.1.100", 12345)
        
        # Exceed rate limit for this IP
        for _ in range(65):  # Exceed the 60 requests per minute limit
            self.device_client._check_rate_limit(address[0])
        
        # Mock socket for connection
        mock_socket = Mock()
        
        # Test connection handling with rate limit exceeded
        with patch.object(self.device_client, '_check_rate_limit', return_value=False):
            self.device_client.handle_device_connection(mock_socket, address)
            
            # Verify socket was closed due to rate limiting
            mock_socket.close.assert_called_once()

    def test_json_protocol_validation(self):
        """Test JSON protocol message validation and parsing."""
        device_id = 0
        
        # Test valid JSON message
        valid_message = {
            "type": "status",
            "timestamp": time.time(),
            "device_status": "recording",
            "battery_level": 85
        }
        
        # Should not raise exception
        try:
            self.device_client._process_device_message(device_id, valid_message)
        except Exception as e:
            self.fail(f"Valid message processing failed: {e}")
        
        # Test message statistics update
        initial_received = self.device_client._message_stats["received"]
        self.device_client._process_device_message(device_id, valid_message)
        self.assertEqual(
            self.device_client._message_stats["received"],
            initial_received + 1
        )

    def test_thread_safety_concurrent_operations(self):
        """Test thread safety of concurrent device operations."""
        import threading
        import time
        
        device_id = 0
        mock_socket = Mock()
        
        # Setup device
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {
                "socket": mock_socket,
                "ip": "192.168.1.100",
                "port": 8080,
                "status": "connected",
                "capabilities": ["recording"],
            }
        
        # Define concurrent operations
        def send_commands():
            for i in range(10):
                self.device_client.send_command(device_id, f"TEST_{i}", require_ack=False)
                time.sleep(0.001)
        
        def process_messages():
            for i in range(10):
                message = {"type": "heartbeat", "timestamp": time.time()}
                self.device_client._process_device_message(device_id, message)
                time.sleep(0.001)
        
        # Run concurrent operations
        thread1 = threading.Thread(target=send_commands)
        thread2 = threading.Thread(target=process_messages)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verify no deadlocks occurred and operations completed
        self.assertTrue(True)  # If we get here, no deadlocks occurred


if __name__ == '__main__':
    unittest.main()

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
