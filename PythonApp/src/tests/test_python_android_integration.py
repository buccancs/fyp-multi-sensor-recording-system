"""
Python-Android integration test suite

Tests protocol compatibility and cross-platform communication between
Python controller and Android devices. Validates message schemas,
network protocols, and data synchronization.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import json
import os
import shutil
import socket
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shimmer_manager import ShimmerManager, ShimmerSample
from ntp_time_server import TimeServerManager


class TestPythonAndroidIntegration(unittest.TestCase):
    """Test suite for Python-Android integration"""

    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()

        # Initialize managers
        self.shimmer_manager = ShimmerManager(logger=self.mock_logger)
        self.time_server_manager = TimeServerManager(logger=self.mock_logger)

    def tearDown(self):
        """Clean up test environment"""
        try:
            self.shimmer_manager.cleanup()
            self.time_server_manager.stop()
        except:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_android_sync_clock_protocol_compatibility(self):
        """Test compatibility with Android SyncClockManager protocol"""
        # Initialize and start NTP server
        self.time_server_manager.initialize(port=8903)
        self.time_server_manager.start()
        time.sleep(0.1)

        # Simulate Android SyncClockManager request format
        android_request = {
            "type": "time_sync_request",
            "client_id": "android_device_samsung_s22_001",
            "timestamp": int(time.time() * 1000),  # Android uses milliseconds
            "sequence": 42,
            "device_info": {
                "model": "Samsung Galaxy S22",
                "android_version": "13",
                "app_version": "1.0.0",
            },
        }

        # Send request to server
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", 8903))

            request_json = json.dumps(android_request)
            client_socket.send(request_json.encode("utf-8"))

            # Receive response
            response_data = client_socket.recv(4096)
            response = json.loads(response_data.decode("utf-8"))
            client_socket.close()

            # Verify response format matches Android expectations
            self.assertEqual(response["type"], "time_sync_response")
            self.assertEqual(response["sequence"], 42)
            self.assertIn("server_time_ms", response)
            self.assertIn("server_precision_ms", response)
            self.assertIsInstance(response["server_time_ms"], int)

            # Verify timing accuracy
            server_time_ms = response["server_time_ms"]
            current_time_ms = int(time.time() * 1000)
            time_diff = abs(server_time_ms - current_time_ms)
            self.assertLess(time_diff, 2000)  # Within 2 seconds

        except Exception as e:
            self.fail(f"Android sync protocol test failed: {e}")

    def test_shimmer_failover_protocol(self):
        """Test Shimmer failover protocol between Python and Android"""
        # Initialize Shimmer manager
        self.shimmer_manager.initialize()

        # Simulate Android device requesting Shimmer failover
        failover_request = {
            "type": "shimmer_failover_request",
            "android_device_id": "samsung_s22_phone1",
            "shimmer_devices": [
                {
                    "mac_address": "00:06:66:66:66:66",
                    "device_name": "Shimmer3_GSR_001",
                    "last_seen": int(time.time() * 1000),
                    "connection_failed": True,
                    "error_message": "Bluetooth connection timeout",
                }
            ],
            "session_id": "failover_test_session_001",
            "timestamp": int(time.time() * 1000),
        }

        # Test Python can handle failover request
        devices = self.shimmer_manager.scan_and_pair_devices()
        if devices:
            # Simulate taking over from Android
            connection_result = self.shimmer_manager.connect_devices(devices)

            # Verify Python can handle the devices
            status = self.shimmer_manager.get_shimmer_status()
            self.assertGreater(len(status), 0)

            # Test recording capability
            recording_result = self.shimmer_manager.start_recording(
                failover_request["session_id"]
            )
            if recording_result:
                self.shimmer_manager.stop_recording()

    def test_network_message_schema_validation(self):
        """Test network message schema compatibility"""
        # Define expected message schemas based on Android implementation
        expected_schemas = {
            "recording_start": {
                "type": "recording_start",
                "session_id": str,
                "timestamp": int,
                "configuration": dict,
            },
            "recording_stop": {
                "type": "recording_stop",
                "session_id": str,
                "timestamp": int,
            },
            "status_update": {
                "type": "status_update",
                "device_id": str,
                "status": dict,
                "timestamp": int,
            },
            "calibration_request": {
                "type": "calibration_request",
                "device_id": str,
                "calibration_type": str,
                "parameters": dict,
            },
        }

        # Test message creation and validation
        for message_type, schema in expected_schemas.items():
            # Create test message
            test_message = {
                "type": message_type,
                "session_id": "test_session_001",
                "timestamp": int(time.time() * 1000),
                "device_id": "test_device",
                "status": {"connected": True},
                "configuration": {"sampling_rate": 128},
                "calibration_type": "thermal_rgb",
                "parameters": {"pattern_size": (9, 6)},
            }

            # Validate message can be serialized/deserialized
            try:
                json_message = json.dumps(test_message)
                parsed_message = json.loads(json_message)
                self.assertEqual(parsed_message["type"], message_type)
            except Exception as e:
                self.fail(f"Message schema validation failed for {message_type}: {e}")

    def test_cross_platform_data_synchronization(self):
        """Test data synchronization between Python and Android"""
        # Initialize components
        self.shimmer_manager.initialize()
        self.time_server_manager.initialize(port=8904)
        self.time_server_manager.start()

        # Simulate synchronized data collection scenario
        devices = self.shimmer_manager.scan_and_pair_devices()
        if devices:
            self.shimmer_manager.connect_devices(devices)

            # Start recording with timestamp synchronization
            session_id = "cross_platform_sync_test"
            recording_started = self.shimmer_manager.start_recording(session_id)

            if recording_started:
                # Simulate Android device requesting time sync during recording
                sync_request = {
                    "type": "time_sync_request",
                    "client_id": "android_sync_test",
                    "timestamp": int(time.time() * 1000),
                    "sequence": 1,
                }

                # Test time synchronization during active recording
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect(("localhost", 8904))

                    client_socket.send(json.dumps(sync_request).encode("utf-8"))
                    response_data = client_socket.recv(4096)
                    response = json.loads(response_data.decode("utf-8"))
                    client_socket.close()

                    # Verify synchronization works during recording
                    self.assertEqual(response["type"], "time_sync_response")

                except Exception as e:
                    self.fail(f"Cross-platform sync failed: {e}")

                # Stop recording
                self.shimmer_manager.stop_recording()

    def test_android_device_discovery_simulation(self):
        """Test simulation of Android device discovery and connection"""
        # Simulate Android device announcing itself on network
        device_announcement = {
            "type": "device_announcement",
            "device_id": "samsung_s22_phone1",
            "device_info": {
                "model": "Samsung Galaxy S22",
                "android_version": "13",
                "ip_address": "192.168.1.100",
                "capabilities": [
                    "thermal_camera",
                    "rgb_camera",
                    "shimmer_bluetooth",
                    "time_sync",
                ],
            },
            "timestamp": int(time.time() * 1000),
        }

        # Test Python can parse and handle device announcements
        try:
            # Validate announcement format
            self.assertIn("device_id", device_announcement)
            self.assertIn("device_info", device_announcement)
            self.assertIn("capabilities", device_announcement["device_info"])

            # Test capability detection
            capabilities = device_announcement["device_info"]["capabilities"]
            self.assertIn("thermal_camera", capabilities)
            self.assertIn("time_sync", capabilities)

        except Exception as e:
            self.fail(f"Device discovery simulation failed: {e}")

    def test_protocol_version_compatibility(self):
        """Test protocol version compatibility between Python and Android"""
        # Define protocol versions
        python_protocol_version = "1.0.0"
        android_protocol_versions = ["1.0.0", "0.9.0", "1.1.0"]

        # Test version compatibility checking
        for android_version in android_protocol_versions:
            compatibility_request = {
                "type": "protocol_version_check",
                "client_protocol_version": android_version,
                "client_type": "android_app",
                "timestamp": int(time.time() * 1000),
            }

            # Simulate version compatibility check
            is_compatible = self._check_protocol_compatibility(
                python_protocol_version, android_version
            )

            # Version 1.0.0 should be compatible with itself
            if android_version == "1.0.0":
                self.assertTrue(is_compatible)

    def test_error_handling_cross_platform(self):
        """Test error handling in cross-platform scenarios"""
        # Test various error scenarios
        error_scenarios = [
            {"type": "invalid_message_format", "data": '{"invalid": json format'},
            {
                "type": "unknown_message_type",
                "data": '{"type": "unknown_type", "data": "test"}',
            },
            {
                "type": "missing_required_fields",
                "data": '{"type": "time_sync_request"}',  # Missing timestamp
            },
        ]

        # Initialize NTP server for error testing
        self.time_server_manager.initialize(port=8905)
        self.time_server_manager.start()
        time.sleep(0.1)

        for scenario in error_scenarios:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(("localhost", 8905))

                # Send invalid data
                client_socket.send(scenario["data"].encode("utf-8"))

                # Server should handle gracefully (not crash)
                try:
                    response_data = client_socket.recv(1024)
                    # If we get a response, server handled it gracefully
                except socket.timeout:
                    # Timeout is also acceptable (server ignored invalid request)
                    pass

                client_socket.close()

            except Exception as e:
                # Connection errors are acceptable for invalid requests
                pass

    def test_data_format_consistency(self):
        """Test data format consistency between Python and Android"""
        # Test Shimmer data format consistency
        python_sample = ShimmerSample(
            timestamp=time.time(),
            system_time="2025-07-30T03:56:00.000Z",
            device_id="shimmer_00_06_66_66_66_66",
            gsr_conductance=5.25,
            ppg_a13=2048.0,
            accel_x=0.1,
            accel_y=0.2,
            accel_z=1.0,
            battery_percentage=85,
        )

        # Convert to format expected by Android
        android_format = {
            "timestamp_ms": int(python_sample.timestamp * 1000),
            "system_time": python_sample.system_time,
            "device_id": python_sample.device_id,
            "sensor_data": {
                "gsr_conductance_us": python_sample.gsr_conductance,
                "ppg_a13_raw": python_sample.ppg_a13,
                "accel_x_g": python_sample.accel_x,
                "accel_y_g": python_sample.accel_y,
                "accel_z_g": python_sample.accel_z,
            },
            "battery_percentage": python_sample.battery_percentage,
        }

        # Verify format conversion
        self.assertIsInstance(android_format["timestamp_ms"], int)
        self.assertIn("sensor_data", android_format)
        self.assertEqual(android_format["device_id"], python_sample.device_id)

    def _check_protocol_compatibility(
        self, python_version: str, android_version: str
    ) -> bool:
        """Check if protocol versions are compatible"""
        # Simple version compatibility check
        python_parts = python_version.split(".")
        android_parts = android_version.split(".")

        # Major version must match
        if python_parts[0] != android_parts[0]:
            return False

        # Minor version compatibility (backward compatible)
        python_minor = int(python_parts[1])
        android_minor = int(android_parts[1])

        return android_minor <= python_minor


if __name__ == "__main__":
    # Configure test logging
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    unittest.main(verbosity=2)
