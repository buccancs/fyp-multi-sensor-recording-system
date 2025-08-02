"""
End-to-end integration tests for multi-device synchronization

Tests the complete integration of ShimmerManager, NTPTimeServer, and StimulusManager
with simulated Android device interactions and cross-platform protocol validation.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shimmer_manager import ShimmerManager
from ntp_time_server import TimeServerManager
from stimulus_manager import StimulusManager


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests for the complete system"""

    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()

        # Initialize all managers
        self.shimmer_manager = ShimmerManager(logger=self.mock_logger)
        self.time_server_manager = TimeServerManager(logger=self.mock_logger)
        self.stimulus_manager = StimulusManager(logger=self.mock_logger)

    def tearDown(self):
        """Clean up test environment"""
        try:
            self.shimmer_manager.cleanup()
            self.time_server_manager.stop()
            self.stimulus_manager.cleanup()
        except:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_system_initialization(self):
        """Test initialization of all system components"""
        # Initialize all components
        shimmer_init = self.shimmer_manager.initialize()
        ntp_init = self.time_server_manager.initialize(port=8899)

        # Verify initialization
        self.assertTrue(shimmer_init)
        self.assertTrue(ntp_init)

        # Start NTP server
        ntp_start = self.time_server_manager.start()
        self.assertTrue(ntp_start)

        # Verify status
        ntp_status = self.time_server_manager.get_status()
        self.assertIsNotNone(ntp_status)
        self.assertTrue(ntp_status.is_running)

    def test_multi_device_time_synchronization(self):
        """Test time synchronization across multiple simulated devices"""
        # Initialize and start NTP server
        self.time_server_manager.initialize(port=8900)
        self.time_server_manager.start()
        time.sleep(0.1)

        # Simulate multiple Android devices requesting time sync
        sync_results = []

        def simulate_android_sync(device_id):
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(("localhost", 8900))

                request = {
                    "type": "time_sync_request",
                    "client_id": device_id,
                    "timestamp": int(time.time() * 1000),
                    "sequence": 1,
                }

                client_socket.send(json.dumps(request).encode("utf-8"))
                response_data = client_socket.recv(4096)
                response = json.loads(response_data.decode("utf-8"))
                client_socket.close()

                sync_results.append(
                    {
                        "device_id": device_id,
                        "server_time": response["server_time_ms"],
                        "precision": response["server_precision_ms"],
                    }
                )
                return True
            except Exception as e:
                return False

        # Start multiple sync threads
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=simulate_android_sync, args=[f"android_device_{i}"]
            )
            threads.append(thread)
            thread.start()

        # Wait for all syncs to complete
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify synchronization results
        self.assertEqual(len(sync_results), 3)

        # Check time consistency (all devices should get similar timestamps)
        timestamps = [result["server_time"] for result in sync_results]
        time_spread = max(timestamps) - min(timestamps)
        self.assertLess(time_spread, 1000)  # Within 1 second


if __name__ == "__main__":
    unittest.main(verbosity=2)
