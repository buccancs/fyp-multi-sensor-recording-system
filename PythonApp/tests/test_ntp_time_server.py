"""
Comprehensive tests for NTPTimeServer functionality

Tests cover server startup/shutdown, time synchronization, NTP integration,
client handling, status monitoring, and integration with main application.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import json
import os
import socket
import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ntp_time_server import (
    NTPTimeServer,
    TimeServerManager,
    TimeServerStatus,
    TimeSyncResponse,
)


class TestNTPTimeServer(unittest.TestCase):
    """Test suite for NTPTimeServer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.test_port = 8890  # Use different port for testing

        # Create NTPTimeServer instance
        self.ntp_server = NTPTimeServer(logger=self.mock_logger, port=self.test_port)

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, "ntp_server"):
            self.ntp_server.stop_server()
            time.sleep(0.1)  # Allow cleanup

    def test_server_initialization(self):
        """Test NTP server initialization"""
        # Test server properties
        self.assertEqual(self.ntp_server.port, self.test_port)
        self.assertFalse(self.ntp_server.is_running)
        self.assertIsNotNone(self.ntp_server.ntp_client)
        self.assertEqual(len(self.ntp_server.ntp_servers), 3)

        # Verify logger calls
        self.mock_logger.info.assert_called()

    def test_server_start_stop(self):
        """Test server start and stop functionality"""
        # Test server start
        result = self.ntp_server.start_server()
        self.assertTrue(result)
        self.assertTrue(self.ntp_server.is_running)

        # Verify server is listening
        time.sleep(0.1)  # Allow server to start

        # Test server stop
        self.ntp_server.stop_server()
        self.assertFalse(self.ntp_server.is_running)

        # Verify logger calls
        self.mock_logger.info.assert_called()

    def test_server_double_start(self):
        """Test starting server when already running"""
        # Start server first time
        result1 = self.ntp_server.start_server()
        self.assertTrue(result1)

        # Try to start again
        result2 = self.ntp_server.start_server()
        self.assertTrue(result2)  # Should return True but not restart

        # Verify warning logged
        self.mock_logger.warning.assert_called()

    def test_precise_timestamp(self):
        """Test precise timestamp generation"""
        # Test basic timestamp
        timestamp1 = self.ntp_server.get_precise_timestamp()
        time.sleep(0.01)
        timestamp2 = self.ntp_server.get_precise_timestamp()

        self.assertIsInstance(timestamp1, float)
        self.assertIsInstance(timestamp2, float)
        self.assertGreater(timestamp2, timestamp1)

        # Test millisecond timestamp
        ms_timestamp = self.ntp_server.get_timestamp_milliseconds()
        self.assertIsInstance(ms_timestamp, int)
        self.assertGreater(ms_timestamp, 1600000000000)  # After 2020

    @patch("ntplib.NTPClient.request")
    def test_ntp_synchronization_success(self, mock_ntp_request):
        """Test successful NTP synchronization"""
        # Mock NTP response
        mock_response = Mock()
        mock_response.tx_time = time.time() + 0.1  # 100ms offset
        mock_response.delay = 0.02  # 20ms delay
        mock_response.precision = -20  # High precision
        mock_ntp_request.return_value = mock_response

        # Test synchronization
        result = self.ntp_server.synchronize_with_ntp()
        self.assertTrue(result)

        # Verify status updated
        status = self.ntp_server.get_server_status()
        self.assertTrue(status.is_synchronized)
        self.assertEqual(status.reference_source, "ntp")
        self.assertIsNotNone(status.last_ntp_sync)

    @patch("ntplib.NTPClient.request")
    def test_ntp_synchronization_failure(self, mock_ntp_request):
        """Test NTP synchronization failure handling"""
        # Mock NTP failure
        mock_ntp_request.side_effect = Exception("NTP server unreachable")

        # Test synchronization
        result = self.ntp_server.synchronize_with_ntp()
        self.assertFalse(result)

        # Verify fallback to system time
        status = self.ntp_server.get_server_status()
        self.assertFalse(status.is_synchronized)
        self.assertEqual(status.reference_source, "system")

    def test_time_sync_request_handling(self):
        """Test handling of time synchronization requests"""
        # Start server
        self.ntp_server.start_server()
        time.sleep(0.1)

        # Create test request
        request_data = {
            "type": "time_sync_request",
            "client_id": "test_client",
            "timestamp": time.time(),
            "sequence": 1,
        }

        # Send request to server
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", self.test_port))

            # Send request
            request_json = json.dumps(request_data)
            client_socket.send(request_json.encode("utf-8"))

            # Receive response
            response_data = client_socket.recv(4096)
            response = json.loads(response_data.decode("utf-8"))

            # Verify response format
            self.assertEqual(response["type"], "time_sync_response")
            self.assertEqual(response["sequence"], 1)
            self.assertIn("server_timestamp", response)
            self.assertIn("server_time_ms", response)
            self.assertIn("server_precision_ms", response)

            client_socket.close()

        except Exception as e:
            self.fail(f"Time sync request failed: {e}")

    def test_invalid_request_handling(self):
        """Test handling of invalid requests"""
        # Start server
        self.ntp_server.start_server()
        time.sleep(0.1)

        # Send invalid JSON
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", self.test_port))

            # Send invalid data
            client_socket.send(b"invalid json data")
            client_socket.close()

            # Should not crash server
            time.sleep(0.1)
            self.assertTrue(self.ntp_server.is_running)

        except Exception as e:
            self.fail(f"Invalid request handling failed: {e}")

    def test_server_status_tracking(self):
        """Test server status tracking and metrics"""
        # Get initial status
        status = self.ntp_server.get_server_status()
        self.assertFalse(status.is_running)
        self.assertEqual(status.client_count, 0)
        self.assertEqual(status.requests_served, 0)

        # Start server and check status
        self.ntp_server.start_server()
        time.sleep(0.1)

        status = self.ntp_server.get_server_status()
        self.assertTrue(status.is_running)

    def test_callback_functionality(self):
        """Test sync callback functionality"""
        # Add callback
        callback_data = []

        def test_callback(response):
            callback_data.append(response)

        self.ntp_server.add_sync_callback(test_callback)

        # Start server
        self.ntp_server.start_server()
        time.sleep(0.1)

        # Send sync request
        request_data = {
            "type": "time_sync_request",
            "client_id": "callback_test",
            "timestamp": time.time(),
            "sequence": 42,
        }

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", self.test_port))

            request_json = json.dumps(request_data)
            client_socket.send(request_json.encode("utf-8"))

            # Wait for response
            response_data = client_socket.recv(4096)
            client_socket.close()

            # Wait for callback processing
            time.sleep(0.1)

            # Verify callback was called
            self.assertEqual(len(callback_data), 1)
            self.assertIsInstance(callback_data[0], TimeSyncResponse)
            self.assertEqual(callback_data[0].sequence_number, 42)

        except Exception as e:
            self.fail(f"Callback test failed: {e}")

    def test_concurrent_requests(self):
        """Test handling of concurrent sync requests"""
        # Start server
        self.ntp_server.start_server()
        time.sleep(0.1)

        # Send multiple concurrent requests
        def send_request(client_id):
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(("localhost", self.test_port))

                request_data = {
                    "type": "time_sync_request",
                    "client_id": client_id,
                    "timestamp": time.time(),
                    "sequence": 1,
                }

                request_json = json.dumps(request_data)
                client_socket.send(request_json.encode("utf-8"))

                response_data = client_socket.recv(4096)
                response = json.loads(response_data.decode("utf-8"))

                client_socket.close()
                return response["type"] == "time_sync_response"

            except Exception:
                return False

        # Start multiple threads
        threads = []
        results = []

        for i in range(5):
            thread = threading.Thread(
                target=lambda i=i: results.append(send_request(f"client_{i}"))
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify all requests succeeded
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))

    def test_server_error_recovery(self):
        """Test server error recovery scenarios"""
        # Test port already in use
        # Start first server
        self.ntp_server.start_server()

        # Try to start second server on same port
        server2 = NTPTimeServer(logger=Mock(), port=self.test_port)
        result = server2.start_server()
        self.assertFalse(result)  # Should fail

        # Clean up
        server2.stop_server()


class TestTimeServerManager(unittest.TestCase):
    """Test suite for TimeServerManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.manager = TimeServerManager(logger=self.mock_logger)

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, "manager"):
            self.manager.stop()

    def test_manager_initialization(self):
        """Test TimeServerManager initialization"""
        result = self.manager.initialize(port=8891)
        self.assertTrue(result)
        self.assertIsNotNone(self.manager.time_server)

    def test_manager_start_stop(self):
        """Test manager start and stop functionality"""
        # Initialize first
        self.manager.initialize(port=8892)

        # Test start
        result = self.manager.start()
        self.assertTrue(result)

        # Test stop
        self.manager.stop()

        # Verify logger calls
        self.mock_logger.info.assert_called()

    def test_manager_status(self):
        """Test manager status retrieval"""
        # Test without initialization
        status = self.manager.get_status()
        self.assertIsNone(status)

        # Test with initialization
        self.manager.initialize(port=8893)
        self.manager.start()

        status = self.manager.get_status()
        self.assertIsNotNone(status)
        self.assertIsInstance(status, TimeServerStatus)

    def test_manager_timestamp(self):
        """Test manager timestamp functionality"""
        # Test without server
        timestamp = self.manager.get_timestamp_ms()
        self.assertIsInstance(timestamp, int)

        # Test with server
        self.manager.initialize(port=8894)
        self.manager.start()

        timestamp = self.manager.get_timestamp_ms()
        self.assertIsInstance(timestamp, int)
        self.assertGreater(timestamp, 1600000000000)


class TestNTPTimeServerIntegration(unittest.TestCase):
    """Integration tests for NTP server with main application"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.mock_logger = Mock()

    def tearDown(self):
        """Clean up integration test fixtures"""

    def test_main_application_integration(self):
        """Test integration with main_backup.py patterns"""
        # This test verifies that TimeServerManager can be used
        # in the same way as in main_backup.py

        # Create manager (as in main_backup.py __init__)
        manager = TimeServerManager(logger=self.mock_logger)

        try:
            # Initialize (as in main_backup.py __init__)
            self.assertTrue(manager.initialize(port=8895))

            # Start server (as in main_backup.py startup)
            self.assertTrue(manager.start())

            # Get status (as in update_status method)
            status = manager.get_status()
            self.assertIsNotNone(status)
            self.assertTrue(status.is_running)

            # Get timestamp (for synchronization)
            timestamp = manager.get_timestamp_ms()
            self.assertIsInstance(timestamp, int)

        finally:
            # Cleanup (as in closeEvent)
            manager.stop()

    def test_android_sync_protocol_compatibility(self):
        """Test compatibility with Android SyncClockManager protocol"""
        # Create and start server
        server = NTPTimeServer(logger=self.mock_logger, port=8896)

        try:
            server.start_server()
            time.sleep(0.1)

            # Simulate Android SyncClockManager request
            request_data = {
                "type": "time_sync_request",
                "client_id": "android_device_001",
                "timestamp": int(time.time() * 1000),  # Android uses milliseconds
                "sequence": 1,
            }

            # Send request
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", 8896))

            request_json = json.dumps(request_data)
            client_socket.send(request_json.encode("utf-8"))

            # Receive response
            response_data = client_socket.recv(4096)
            response = json.loads(response_data.decode("utf-8"))

            client_socket.close()

            # Verify response matches expected format for Android
            self.assertEqual(response["type"], "time_sync_response")
            self.assertIn("server_time_ms", response)  # Android expects milliseconds
            self.assertIn("server_precision_ms", response)
            self.assertIsInstance(response["server_time_ms"], int)

            # Verify timing values are reasonable
            server_time_ms = response["server_time_ms"]
            current_time_ms = int(time.time() * 1000)
            time_diff = abs(server_time_ms - current_time_ms)
            self.assertLess(time_diff, 1000)  # Within 1 second

        finally:
            server.stop_server()


if __name__ == "__main__":
    # Configure test logging
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    unittest.main(verbosity=2)
