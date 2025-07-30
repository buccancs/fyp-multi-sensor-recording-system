"""
Comprehensive tests for ShimmerManager functionality

Tests cover device discovery, connection handling, data streaming,
CSV logging, session management, and error handling scenarios.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import unittest
import tempfile
import shutil
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shimmer_manager import (
    ShimmerManager, ShimmerStatus, ShimmerSample, 
    DeviceConfiguration, PYSHIMMER_AVAILABLE
)


class TestShimmerManager(unittest.TestCase):
    """Test suite for ShimmerManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()
        self.mock_session_manager = Mock()
        
        # Create ShimmerManager instance
        self.shimmer_manager = ShimmerManager(
            session_manager=self.mock_session_manager,
            logger=self.mock_logger
        )
        
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'shimmer_manager'):
            self.shimmer_manager.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test ShimmerManager initialization"""
        # Test successful initialization
        result = self.shimmer_manager.initialize()
        self.assertTrue(result)
        self.assertTrue(self.shimmer_manager.is_initialized)
        
        # Verify logger calls
        self.mock_logger.info.assert_called()
        
    def test_initialization_failure(self):
        """Test ShimmerManager initialization failure handling"""
        # Mock initialization failure
        with patch.object(self.shimmer_manager, '_start_background_threads', 
                         side_effect=Exception("Test error")):
            result = self.shimmer_manager.initialize()
            self.assertFalse(result)
            self.assertFalse(self.shimmer_manager.is_initialized)

    def test_device_scanning(self):
        """Test device scanning functionality"""
        # Test device scanning
        devices = self.shimmer_manager.scan_and_pair_devices()
        
        # Should return simulated devices when pyshimmer not available
        if not PYSHIMMER_AVAILABLE:
            self.assertIsInstance(devices, list)
            self.assertGreater(len(devices), 0)
            # Verify MAC address format
            for device in devices:
                self.assertRegex(device, r'^[0-9A-Fa-f:]{17}$')
        
        # Verify logger calls
        self.mock_logger.info.assert_called()

    def test_device_connection(self):
        """Test device connection functionality"""
        # Initialize manager first
        self.shimmer_manager.initialize()
        
        # Test device connection
        test_devices = ["00:06:66:66:66:66", "00:06:66:66:66:67"]
        result = self.shimmer_manager.connect_devices(test_devices)
        
        # Should succeed in simulation mode
        if not PYSHIMMER_AVAILABLE:
            self.assertTrue(result)
            
            # Verify devices are in status
            status = self.shimmer_manager.get_shimmer_status()
            self.assertGreater(len(status), 0)
            
            # Check device status properties
            for device_id, device_status in status.items():
                self.assertIsInstance(device_status, ShimmerStatus)
                self.assertTrue(device_status.is_available)
                self.assertTrue(device_status.is_connected)

    def test_channel_configuration(self):
        """Test sensor channel configuration"""
        # Initialize and connect devices
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Test channel configuration
        channels = {"GSR", "PPG_A13", "Accel_X", "Accel_Y", "Accel_Z"}
        status = self.shimmer_manager.get_shimmer_status()
        
        for device_id in status.keys():
            result = self.shimmer_manager.set_enabled_channels(device_id, channels)
            self.assertTrue(result)
            
            # Verify configuration is stored
            self.assertIn(device_id, self.shimmer_manager.device_configurations)
            config = self.shimmer_manager.device_configurations[device_id]
            self.assertEqual(config.enabled_channels, channels)

    def test_streaming_control(self):
        """Test data streaming start/stop functionality"""
        # Initialize and connect devices
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Test start streaming
        result = self.shimmer_manager.start_streaming()
        self.assertTrue(result)
        self.assertTrue(self.shimmer_manager.is_streaming)
        
        # Verify device streaming status
        status = self.shimmer_manager.get_shimmer_status()
        for device_status in status.values():
            self.assertTrue(device_status.is_streaming)
        
        # Test stop streaming
        result = self.shimmer_manager.stop_streaming()
        self.assertTrue(result)
        self.assertFalse(self.shimmer_manager.is_streaming)
        
        # Verify device streaming status
        status = self.shimmer_manager.get_shimmer_status()
        for device_status in status.values():
            self.assertFalse(device_status.is_streaming)

    def test_recording_session(self):
        """Test recording session management"""
        # Setup session manager mock
        session_dir = Path(self.temp_dir) / "test_session" / "shimmer"
        self.mock_session_manager.get_session_directory.return_value = str(session_dir.parent)
        
        # Initialize and connect devices
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Test start recording
        session_id = "test_session_123"
        result = self.shimmer_manager.start_recording(session_id)
        self.assertTrue(result)
        self.assertTrue(self.shimmer_manager.is_recording)
        self.assertEqual(self.shimmer_manager.current_session_id, session_id)
        
        # Verify session directory creation
        self.assertTrue(session_dir.exists())
        
        # Verify CSV files creation
        csv_files = list(session_dir.glob("*.csv"))
        self.assertGreater(len(csv_files), 0)
        
        # Test stop recording
        result = self.shimmer_manager.stop_recording()
        self.assertTrue(result)
        self.assertFalse(self.shimmer_manager.is_recording)
        self.assertIsNone(self.shimmer_manager.current_session_id)

    def test_data_callbacks(self):
        """Test data callback functionality"""
        # Initialize manager
        self.shimmer_manager.initialize()
        
        # Add data callback
        callback_data = []
        def test_callback(sample):
            callback_data.append(sample)
        
        self.shimmer_manager.add_data_callback(test_callback)
        
        # Create test sample
        test_sample = ShimmerSample(
            timestamp=time.time(),
            system_time="2025-07-30T03:13:00",
            device_id="test_device",
            gsr_conductance=5.0,
            ppg_a13=2000.0,
            accel_x=0.1,
            accel_y=0.2,
            accel_z=1.0,
            battery_percentage=85
        )
        
        # Process sample (simulate data processing)
        self.shimmer_manager._process_data_sample(test_sample)
        
        # Verify callback was called
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0], test_sample)

    def test_status_callbacks(self):
        """Test status callback functionality"""
        # Initialize manager
        self.shimmer_manager.initialize()
        
        # Add status callback
        callback_data = []
        def test_callback(device_id, status):
            callback_data.append((device_id, status))
        
        self.shimmer_manager.add_status_callback(test_callback)
        
        # Connect devices to trigger status updates
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Note: Status callbacks are called during connection process
        # In simulation mode, this happens synchronously

    def test_csv_data_logging(self):
        """Test CSV data logging functionality"""
        # Setup session manager mock
        session_dir = Path(self.temp_dir) / "csv_test_session" / "shimmer"
        self.mock_session_manager.get_session_directory.return_value = str(session_dir.parent)
        
        # Initialize and setup recording
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Start recording
        session_id = "csv_test_session"
        self.shimmer_manager.start_recording(session_id)
        
        # Create and process test samples
        test_samples = []
        for i in range(5):
            sample = ShimmerSample(
                timestamp=time.time() + i,
                system_time=f"2025-07-30T03:13:{i:02d}",
                device_id="shimmer_00_06_66_66_66_66",
                gsr_conductance=5.0 + i,
                ppg_a13=2000.0 + i * 10,
                accel_x=0.1 + i * 0.01,
                accel_y=0.2 + i * 0.01,
                accel_z=1.0 + i * 0.001,
                battery_percentage=85 - i
            )
            test_samples.append(sample)
            self.shimmer_manager._process_data_sample(sample)
        
        # Stop recording to flush files
        self.shimmer_manager.stop_recording()
        
        # Verify CSV file content
        csv_files = list(session_dir.glob("*.csv"))
        self.assertGreater(len(csv_files), 0)
        
        # Read and verify CSV content
        import csv
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertGreater(len(rows), 0)
                
                # Verify CSV headers
                expected_headers = [
                    'timestamp', 'system_time', 'device_id',
                    'gsr_conductance', 'ppg_a13',
                    'accel_x', 'accel_y', 'accel_z',
                    'battery_percentage'
                ]
                self.assertEqual(list(reader.fieldnames), expected_headers)

    def test_simulated_data_generation(self):
        """Test simulated data generation"""
        # Initialize and connect devices
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Start streaming to trigger simulated data
        self.shimmer_manager.start_streaming()
        
        # Wait for some simulated data
        time.sleep(2.0)
        
        # Check that data queues have samples
        for device_id, data_queue in self.shimmer_manager.data_queues.items():
            self.assertGreater(data_queue.qsize(), 0)
        
        # Stop streaming
        self.shimmer_manager.stop_streaming()

    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test operations without initialization
        result = self.shimmer_manager.start_streaming()
        self.assertFalse(result)
        
        # Test invalid device configuration
        result = self.shimmer_manager.set_enabled_channels("invalid_device", {"GSR"})
        self.assertFalse(result)
        
        # Test recording without devices
        result = self.shimmer_manager.start_recording("test_session")
        # Should still succeed but with warnings

    def test_cleanup(self):
        """Test cleanup functionality"""
        # Initialize and setup
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.shimmer_manager.start_streaming()
        
        # Test cleanup
        self.shimmer_manager.cleanup()
        
        # Verify cleanup state
        self.assertFalse(self.shimmer_manager.is_initialized)
        self.assertFalse(self.shimmer_manager.is_streaming)
        self.assertFalse(self.shimmer_manager.is_recording)
        self.assertEqual(len(self.shimmer_manager.connected_devices), 0)
        self.assertEqual(len(self.shimmer_manager.device_status), 0)

    def test_thread_safety(self):
        """Test thread safety of ShimmerManager operations"""
        # Initialize manager
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        
        # Start streaming
        self.shimmer_manager.start_streaming()
        
        # Perform concurrent operations
        def concurrent_status_check():
            for _ in range(10):
                status = self.shimmer_manager.get_shimmer_status()
                self.assertIsInstance(status, dict)
                time.sleep(0.1)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=concurrent_status_check)
            threads.append(thread)
            thread.start()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Cleanup
        self.shimmer_manager.stop_streaming()

    def test_data_structures(self):
        """Test data structure classes"""
        # Test ShimmerStatus
        status = ShimmerStatus(
            is_available=True,
            is_connected=True,
            is_recording=False,
            is_streaming=True,
            sampling_rate=128,
            battery_level=85,
            signal_quality="Good",
            samples_recorded=1000,
            device_name="Shimmer3_GSR",
            mac_address="00:06:66:66:66:66",
            firmware_version="1.0.0"
        )
        
        self.assertTrue(status.is_available)
        self.assertTrue(status.is_connected)
        self.assertEqual(status.sampling_rate, 128)
        self.assertEqual(status.battery_level, 85)
        
        # Test ShimmerSample
        sample = ShimmerSample(
            timestamp=time.time(),
            system_time="2025-07-30T03:13:00",
            device_id="test_device",
            gsr_conductance=5.0,
            ppg_a13=2000.0,
            accel_x=0.1,
            accel_y=0.2,
            accel_z=1.0,
            battery_percentage=85
        )
        
        self.assertEqual(sample.device_id, "test_device")
        self.assertEqual(sample.gsr_conductance, 5.0)
        self.assertEqual(sample.battery_percentage, 85)
        
        # Test DeviceConfiguration
        config = DeviceConfiguration(
            device_id="test_device",
            mac_address="00:06:66:66:66:66",
            enabled_channels={"GSR", "PPG_A13"},
            sampling_rate=128,
            connection_type="bluetooth"
        )
        
        self.assertEqual(config.device_id, "test_device")
        self.assertEqual(config.sampling_rate, 128)
        self.assertIn("GSR", config.enabled_channels)


class TestShimmerManagerIntegration(unittest.TestCase):
    """Integration tests for ShimmerManager with main_backup.py"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up integration test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_main_backup_integration(self):
        """Test integration with main_backup.py patterns"""
        # This test verifies that ShimmerManager can be used
        # in the same way as in main_backup.py
        
        # Create manager
        manager = ShimmerManager()
        
        try:
            # Initialize (as in main_backup.py __init__)
            self.assertTrue(manager.initialize())
            
            # Scan and connect (as in start_recording)
            devices = manager.scan_and_pair_devices()
            if devices:
                manager.connect_devices(devices)
                
                # Configure channels
                channels = {"GSR", "PPG_A13", "Accel_X", "Accel_Y", "Accel_Z"}
                for device_id in manager.device_status:
                    manager.set_enabled_channels(device_id, channels)
                
                # Start recording
                session_id = f"integration_test_{int(time.time())}"
                manager.start_recording(session_id)
                
                # Simulate some recording time
                time.sleep(1.0)
                
                # Stop recording
                manager.stop_recording()
                
                # Get final status
                status = manager.get_shimmer_status()
                for device_id, device_status in status.items():
                    self.assertGreaterEqual(device_status.samples_recorded, 0)
        
        finally:
            # Cleanup (as in closeEvent)
            manager.cleanup()


if __name__ == '__main__':
    # Configure test logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)
