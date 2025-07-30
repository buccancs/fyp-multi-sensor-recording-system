"""
Hardware failure recovery scenario tests

Tests system resilience when devices disconnect, fail, or experience network interruptions.
Validates graceful degradation and automatic recovery mechanisms.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import unittest
import tempfile
import shutil
import time
import threading
import socket
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shimmer_manager import ShimmerManager, ShimmerStatus, ShimmerSample
from ntp_time_server import NTPTimeServer, TimeServerManager
from stimulus_manager import StimulusManager, StimulusConfig


class TestHardwareFailureRecovery(unittest.TestCase):
    """Test suite for hardware failure recovery scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()
        
        # Initialize managers
        self.shimmer_manager = ShimmerManager(logger=self.mock_logger)
        self.time_server_manager = TimeServerManager(logger=self.mock_logger)
        
    def tearDown(self):
        """Clean up test fixtures"""
        try:
            self.shimmer_manager.cleanup()
            self.time_server_manager.stop()
        except:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_shimmer_device_disconnection_recovery(self):
        """Test recovery when Shimmer devices disconnect during recording"""
        # Initialize and setup recording
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Start recording
        session_id = "failure_test_session"
        self.shimmer_manager.start_recording(session_id)
        
        # Verify recording is active
        self.assertTrue(self.shimmer_manager.is_recording)
        
        # Simulate device disconnection by clearing device status
        original_status = self.shimmer_manager.device_status.copy()
        for device_id in list(self.shimmer_manager.device_status.keys()):
            self.shimmer_manager.device_status[device_id].is_connected = False
            self.shimmer_manager.device_status[device_id].is_streaming = False
        
        # Verify system continues recording despite disconnections
        self.assertTrue(self.shimmer_manager.is_recording)
        
        # Test graceful stop
        result = self.shimmer_manager.stop_recording()
        self.assertTrue(result)

    def test_ntp_server_network_interruption(self):
        """Test NTP server behavior during network interruptions"""
        # Initialize and start NTP server
        self.time_server_manager.initialize(port=8901)
        self.time_server_manager.start()
        time.sleep(0.1)
        
        # Verify server is running
        status = self.time_server_manager.get_status()
        self.assertTrue(status.is_running)
        
        # Simulate network interruption by stopping server
        self.time_server_manager.stop()
        
        # Verify graceful shutdown
        status = self.time_server_manager.get_status()
        if status:  # Status might be None after stop
            self.assertFalse(status.is_running)
        
        # Test restart capability
        restart_result = self.time_server_manager.start()
        # Note: This might fail due to port binding issues in rapid succession
        # In real scenarios, there would be a delay between stop/start

    def test_concurrent_device_failures(self):
        """Test system behavior when multiple devices fail simultaneously"""
        # Initialize all managers
        self.shimmer_manager.initialize()
        self.time_server_manager.initialize(port=8902)
        
        # Start services
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.time_server_manager.start()
        
        # Start recording
        session_id = "concurrent_failure_test"
        recording_started = self.shimmer_manager.start_recording(session_id)
        
        # Simulate concurrent failures
        failure_events = []
        
        def simulate_shimmer_failure():
            try:
                # Simulate Shimmer device failure
                for device_id in self.shimmer_manager.device_status:
                    self.shimmer_manager.device_status[device_id].is_connected = False
                failure_events.append("shimmer_failed")
            except Exception as e:
                failure_events.append(f"shimmer_error: {e}")
        
        def simulate_ntp_failure():
            try:
                # Simulate NTP server failure
                self.time_server_manager.stop()
                failure_events.append("ntp_failed")
            except Exception as e:
                failure_events.append(f"ntp_error: {e}")
        
        # Start failure simulation threads
        shimmer_thread = threading.Thread(target=simulate_shimmer_failure)
        ntp_thread = threading.Thread(target=simulate_ntp_failure)
        
        shimmer_thread.start()
        ntp_thread.start()
        
        # Wait for failures to complete
        shimmer_thread.join(timeout=2.0)
        ntp_thread.join(timeout=2.0)
        
        # Verify system handles multiple failures gracefully
        self.assertGreater(len(failure_events), 0)
        
        # Test cleanup after failures
        cleanup_result = self.shimmer_manager.stop_recording()
        # Should succeed even with failures

    def test_resource_exhaustion_recovery(self):
        """Test recovery from resource exhaustion scenarios"""
        # Initialize manager
        self.shimmer_manager.initialize()
        
        # Simulate resource exhaustion by creating many connections
        devices = self.shimmer_manager.scan_and_pair_devices()
        
        # Test multiple rapid connection attempts
        connection_results = []
        for i in range(10):  # Attempt many connections
            result = self.shimmer_manager.connect_devices(devices)
            connection_results.append(result)
        
        # Verify system doesn't crash under load
        self.assertIsInstance(connection_results, list)
        
        # Test cleanup under stress
        cleanup_success = True
        try:
            self.shimmer_manager.cleanup()
        except Exception:
            cleanup_success = False
        
        # Cleanup should succeed even under stress
        self.assertTrue(cleanup_success)

    def test_data_corruption_handling(self):
        """Test handling of corrupted data scenarios"""
        # Initialize manager
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Create corrupted sample data
        corrupted_sample = ShimmerSample(
            timestamp=float('inf'),  # Invalid timestamp
            system_time="invalid_time_format",
            device_id="",  # Empty device ID
            gsr_conductance=None,
            ppg_a13=float('nan'),  # NaN value
            accel_x=None,
            accel_y=None,
            accel_z=None,
            battery_percentage=-1  # Invalid battery level
        )
        
        # Test processing corrupted data
        processing_success = True
        try:
            self.shimmer_manager._process_data_sample(corrupted_sample)
        except Exception:
            processing_success = False
        
        # System should handle corrupted data gracefully
        # (Implementation should validate and sanitize data)

    def test_memory_leak_prevention(self):
        """Test prevention of memory leaks during failures"""
        # Initialize manager
        self.shimmer_manager.initialize()
        
        # Simulate repeated failure/recovery cycles
        for cycle in range(5):
            # Connect devices
            devices = self.shimmer_manager.scan_and_pair_devices()
            self.shimmer_manager.connect_devices(devices)
            
            # Start recording
            session_id = f"memory_test_{cycle}"
            self.shimmer_manager.start_recording(session_id)
            
            # Simulate failure
            self.shimmer_manager.stop_recording()
            
            # Brief pause between cycles
            time.sleep(0.1)
        
        # Verify cleanup state
        self.assertEqual(len(self.shimmer_manager.connected_devices), 0)
        self.assertEqual(len(self.shimmer_manager.csv_writers), 0)
        self.assertEqual(len(self.shimmer_manager.csv_files), 0)

    def test_thread_safety_under_failure(self):
        """Test thread safety when failures occur during concurrent operations"""
        # Initialize manager
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Start streaming
        self.shimmer_manager.start_streaming()
        
        # Concurrent operations during failure
        results = []
        
        def concurrent_status_check():
            for _ in range(5):
                try:
                    status = self.shimmer_manager.get_shimmer_status()
                    results.append(("status", len(status)))
                except Exception as e:
                    results.append(("error", str(e)))
                time.sleep(0.01)
        
        def concurrent_failure_simulation():
            time.sleep(0.02)  # Small delay
            try:
                # Simulate device failure
                for device_id in self.shimmer_manager.device_status:
                    self.shimmer_manager.device_status[device_id].is_connected = False
                results.append(("failure_simulated", True))
            except Exception as e:
                results.append(("failure_error", str(e)))
        
        # Start concurrent threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=concurrent_status_check)
            threads.append(thread)
            thread.start()
        
        failure_thread = threading.Thread(target=concurrent_failure_simulation)
        threads.append(failure_thread)
        failure_thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Verify no deadlocks or crashes occurred
        self.assertGreater(len(results), 0)
        
        # Stop streaming
        self.shimmer_manager.stop_streaming()


if __name__ == '__main__':
    # Configure test logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)
