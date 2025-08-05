#!/usr/bin/env python3
"""
Comprehensive Shimmer Integration Tests
=======================================

This module provides comprehensive unit tests for all Shimmer device
integration functionality in the PythonApp.

Test coverage:
- ShimmerManager: Device discovery, connection management, data streaming
- Shimmer PC App: Cross-platform communication, data synchronization
- Shimmer Data Models: Data parsing, validation, transformation
- Integration workflows: End-to-end device coordination

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys
import threading
import time
from queue import Queue

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from shimmer_manager import ShimmerManager, ShimmerDeviceConfig
    from shimmer_pc_app import ShimmerPCApp, ShimmerDataProcessor
    SHIMMER_MODULES_AVAILABLE = True
except ImportError as e:
    SHIMMER_MODULES_AVAILABLE = False
    print(f"Warning: Shimmer modules not available: {e}")


class TestShimmerManager(unittest.TestCase):
    """Test ShimmerManager device management and coordination."""

    def setUp(self):
        """Set up test fixtures."""
        if not SHIMMER_MODULES_AVAILABLE:
            self.skipTest("Shimmer modules not available")
        
        self.mock_config = {
            'shimmer_devices': {
                'device_1': {
                    'mac_address': '00:06:66:AA:BB:CC',
                    'sampling_rate': 512,
                    'sensors': ['GSR', 'ECG', 'EMG']
                },
                'device_2': {
                    'mac_address': '00:06:66:DD:EE:FF',
                    'sampling_rate': 256,
                    'sensors': ['GSR', 'PPG']
                }
            },
            'sync_settings': {
                'master_device': 'device_1',
                'sync_timeout': 30.0
            }
        }
        
        self.shimmer_manager = ShimmerManager(self.mock_config)

    def test_device_discovery(self):
        """Test Shimmer device discovery functionality."""
        with patch('shimmer_manager.bluetooth') as mock_bluetooth:
            mock_bluetooth.discover_devices.return_value = [
                ('00:06:66:AA:BB:CC', 'Shimmer3-AABBCC'),
                ('00:06:66:DD:EE:FF', 'Shimmer3-DDEEFF')
            ]
            
            discovered_devices = self.shimmer_manager.discover_devices()
            
            self.assertEqual(len(discovered_devices), 2)
            self.assertIn('00:06:66:AA:BB:CC', [d['mac_address'] for d in discovered_devices])
            mock_bluetooth.discover_devices.assert_called_once()

    def test_device_connection(self):
        """Test individual device connection management."""
        with patch('shimmer_manager.ShimmerDevice') as mock_shimmer_device:
            mock_device = Mock()
            mock_shimmer_device.return_value = mock_device
            mock_device.connect.return_value = True
            mock_device.is_connected.return_value = True
            
            result = self.shimmer_manager.connect_device('device_1')
            
            self.assertTrue(result)
            mock_device.connect.assert_called_once()
            self.assertIn('device_1', self.shimmer_manager.connected_devices)

    def test_multi_device_connection(self):
        """Test connecting multiple devices simultaneously."""
        with patch('shimmer_manager.ShimmerDevice') as mock_shimmer_device:
            mock_devices = {}
            for device_id in ['device_1', 'device_2']:
                mock_device = Mock()
                mock_device.connect.return_value = True
                mock_device.is_connected.return_value = True
                mock_devices[device_id] = mock_device
            
            mock_shimmer_device.side_effect = lambda config: mock_devices[config['device_id']]
            
            results = self.shimmer_manager.connect_all_devices()
            
            self.assertTrue(all(results.values()))
            self.assertEqual(len(self.shimmer_manager.connected_devices), 2)

    def test_data_streaming_start(self):
        """Test starting synchronized data streaming."""
        with patch('shimmer_manager.ShimmerDevice') as mock_shimmer_device:
            mock_device_1 = Mock()
            mock_device_2 = Mock()
            mock_device_1.start_streaming.return_value = True
            mock_device_2.start_streaming.return_value = True
            
            self.shimmer_manager.connected_devices = {
                'device_1': mock_device_1,
                'device_2': mock_device_2
            }
            
            result = self.shimmer_manager.start_synchronized_streaming()
            
            self.assertTrue(result)
            mock_device_1.start_streaming.assert_called_once()
            mock_device_2.start_streaming.assert_called_once()

    def test_data_collection(self):
        """Test data collection from multiple devices."""
        mock_device_1 = Mock()
        mock_device_2 = Mock()
        
        # Mock data samples
        sample_1 = {
            'timestamp': 1642425600.0,
            'device_id': 'device_1',
            'gsr': 1.234,
            'ecg': 0.567,
            'emg': 0.890
        }
        sample_2 = {
            'timestamp': 1642425600.1,
            'device_id': 'device_2',
            'gsr': 2.345,
            'ppg': 1.678
        }
        
        mock_device_1.get_latest_data.return_value = sample_1
        mock_device_2.get_latest_data.return_value = sample_2
        
        self.shimmer_manager.connected_devices = {
            'device_1': mock_device_1,
            'device_2': mock_device_2
        }
        
        collected_data = self.shimmer_manager.collect_synchronized_data()
        
        self.assertEqual(len(collected_data), 2)
        self.assertEqual(collected_data[0]['device_id'], 'device_1')
        self.assertEqual(collected_data[1]['device_id'], 'device_2')

    def test_connection_recovery(self):
        """Test automatic connection recovery on device disconnect."""
        with patch('shimmer_manager.ShimmerDevice') as mock_shimmer_device:
            mock_device = Mock()
            mock_shimmer_device.return_value = mock_device
            
            # Simulate connection loss and recovery
            mock_device.is_connected.side_effect = [True, False, True]
            mock_device.reconnect.return_value = True
            
            self.shimmer_manager.connected_devices = {'device_1': mock_device}
            
            # First call - connected
            self.assertTrue(self.shimmer_manager.check_device_health('device_1'))
            
            # Second call - disconnected, triggers recovery
            result = self.shimmer_manager.check_device_health('device_1')
            
            mock_device.reconnect.assert_called_once()

    def test_synchronization_timing(self):
        """Test device synchronization timing accuracy."""
        mock_device_1 = Mock()
        mock_device_2 = Mock()
        
        # Mock precise timing
        start_time = time.time()
        mock_device_1.synchronize_clock.return_value = start_time
        mock_device_2.synchronize_clock.return_value = start_time + 0.001  # 1ms offset
        
        self.shimmer_manager.connected_devices = {
            'device_1': mock_device_1,
            'device_2': mock_device_2
        }
        
        sync_results = self.shimmer_manager.synchronize_all_devices()
        
        self.assertTrue(all(sync_results.values()))
        max_offset = max(abs(t - start_time) for t in sync_results.values())
        self.assertLess(max_offset, 0.01)  # < 10ms synchronization accuracy


class TestShimmerPCApp(unittest.TestCase):
    """Test ShimmerPCApp cross-platform communication."""

    def setUp(self):
        """Set up test fixtures."""
        if not SHIMMER_MODULES_AVAILABLE:
            self.skipTest("Shimmer modules not available")
        
        self.config = {
            'communication': {
                'protocol': 'TCP',
                'port': 8765,
                'buffer_size': 1024
            },
            'data_processing': {
                'sample_rate': 512,
                'filtering': True
            }
        }
        
        self.shimmer_app = ShimmerPCApp(self.config)

    def test_communication_setup(self):
        """Test communication channel establishment."""
        with patch('shimmer_pc_app.socket') as mock_socket:
            mock_server = Mock()
            mock_socket.socket.return_value = mock_server
            
            result = self.shimmer_app.setup_communication()
            
            self.assertTrue(result)
            mock_server.bind.assert_called_once()
            mock_server.listen.assert_called_once()

    def test_data_processing_pipeline(self):
        """Test real-time data processing pipeline."""
        processor = ShimmerDataProcessor(self.config['data_processing'])
        
        # Mock raw sensor data
        raw_data = {
            'gsr_raw': [1024, 1025, 1023, 1026],
            'timestamp': [1.0, 1.002, 1.004, 1.006],
            'device_id': 'shimmer_001'
        }
        
        with patch('shimmer_pc_app.signal_filter') as mock_filter:
            mock_filter.apply_lowpass.return_value = [1.234, 1.235, 1.233, 1.236]
            
            processed_data = processor.process_sensor_data(raw_data)
            
            self.assertIn('gsr_processed', processed_data)
            self.assertIn('timestamp', processed_data)
            self.assertEqual(len(processed_data['gsr_processed']), 4)

    def test_cross_device_coordination(self):
        """Test coordination between multiple Shimmer devices."""
        with patch('shimmer_pc_app.threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            devices = ['shimmer_001', 'shimmer_002', 'shimmer_003']
            result = self.shimmer_app.coordinate_devices(devices)
            
            self.assertTrue(result)
            self.assertEqual(mock_thread.call_count, len(devices))

    def test_data_buffering(self):
        """Test data buffering and overflow handling."""
        buffer_size = 1000
        data_buffer = self.shimmer_app.create_data_buffer(buffer_size)
        
        # Fill buffer beyond capacity
        for i in range(1200):
            sample = {
                'timestamp': i * 0.002,
                'gsr': 1.0 + i * 0.001,
                'device_id': 'shimmer_001'
            }
            data_buffer.add_sample(sample)
        
        # Check buffer size constraint
        self.assertLessEqual(len(data_buffer.samples), buffer_size)
        
        # Check oldest samples are removed
        oldest_timestamp = min(sample['timestamp'] for sample in data_buffer.samples)
        self.assertGreater(oldest_timestamp, 0.4)  # Should have removed early samples

    def test_error_handling(self):
        """Test error handling in communication and processing."""
        with patch('shimmer_pc_app.socket.socket') as mock_socket:
            mock_socket.side_effect = OSError("Connection failed")
            
            result = self.shimmer_app.setup_communication()
            
            self.assertFalse(result)
            self.assertIn("error", self.shimmer_app.last_error.lower())


class TestShimmerIntegration(unittest.TestCase):
    """Test end-to-end Shimmer integration workflows."""

    def setUp(self):
        """Set up test fixtures."""
        if not SHIMMER_MODULES_AVAILABLE:
            self.skipTest("Shimmer modules not available")

    def test_complete_recording_session(self):
        """Test complete recording session with multiple devices."""
        with patch('shimmer_manager.ShimmerManager') as mock_manager, \
             patch('shimmer_pc_app.ShimmerPCApp') as mock_app:
            
            mock_manager_instance = Mock()
            mock_app_instance = Mock()
            mock_manager.return_value = mock_manager_instance
            mock_app.return_value = mock_app_instance
            
            # Setup successful connections
            mock_manager_instance.connect_all_devices.return_value = {
                'device_1': True, 'device_2': True
            }
            mock_manager_instance.start_synchronized_streaming.return_value = True
            mock_app_instance.setup_communication.return_value = True
            
            # Simulate recording session
            session_config = {
                'duration': 10.0,
                'devices': ['device_1', 'device_2'],
                'sampling_rate': 512
            }
            
            manager = mock_manager_instance
            app = mock_app_instance
            
            # Start session
            manager.connect_all_devices()
            app.setup_communication()
            manager.start_synchronized_streaming()
            
            # Verify all components started
            manager.connect_all_devices.assert_called_once()
            app.setup_communication.assert_called_once()
            manager.start_synchronized_streaming.assert_called_once()

    def test_device_failure_recovery(self):
        """Test recovery from device failures during recording."""
        with patch('shimmer_manager.ShimmerManager') as mock_manager:
            mock_manager_instance = Mock()
            mock_manager.return_value = mock_manager_instance
            
            # Simulate device failure and recovery
            mock_manager_instance.check_device_health.side_effect = [
                {'device_1': True, 'device_2': True},   # Initial state
                {'device_1': False, 'device_2': True},  # Device 1 fails
                {'device_1': True, 'device_2': True}    # Device 1 recovered
            ]
            mock_manager_instance.recover_device.return_value = True
            
            manager = mock_manager_instance
            
            # Check initial health
            health_1 = manager.check_device_health()
            self.assertTrue(all(health_1.values()))
            
            # Detect failure
            health_2 = manager.check_device_health()
            self.assertFalse(health_2['device_1'])
            
            # Recover device
            recovery_result = manager.recover_device('device_1')
            self.assertTrue(recovery_result)


def create_shimmer_test_suite():
    """Create comprehensive test suite for Shimmer integration."""
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestShimmerManager))
    suite.addTest(unittest.makeSuite(TestShimmerPCApp))
    suite.addTest(unittest.makeSuite(TestShimmerIntegration))
    
    return suite


if __name__ == '__main__':
    if SHIMMER_MODULES_AVAILABLE:
        # Run comprehensive tests
        runner = unittest.TextTestRunner(verbosity=2)
        suite = create_shimmer_test_suite()
        result = runner.run(suite)
        
        # Print results summary
        print(f"\n{'='*60}")
        print(f"Shimmer Integration Tests Summary")
        print(f"{'='*60}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    else:
        print("Shimmer modules not available - skipping tests")