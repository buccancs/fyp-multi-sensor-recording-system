#!/usr/bin/env python3
"""
Comprehensive Time Synchronization Tests
=========================================

This module provides comprehensive unit tests for all time synchronization
functionality in the PythonApp.

Test coverage:
- Master Clock Synchronizer: NTP synchronization, precision timing
- NTP Time Server: Network time protocol implementation, client management
- Cross-device timing: Multi-device synchronization, offset correction
- Timing accuracy: Precision measurement, drift compensation

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
import time
import threading
import socket
from queue import Queue
import struct

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from master_clock_synchronizer import MasterClockSynchronizer, ClockSyncManager
    from ntp_time_server import NTPTimeServer, NTPClient, NTPPacket
    TIME_SYNC_MODULES_AVAILABLE = True
except ImportError as e:
    TIME_SYNC_MODULES_AVAILABLE = False
    print(f"Warning: Time synchronization modules not available: {e}")

try:
    import ntplib
    NTPLIB_AVAILABLE = True
except ImportError:
    NTPLIB_AVAILABLE = False


class TestMasterClockSynchronizer(unittest.TestCase):
    """Test MasterClockSynchronizer precision timing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not TIME_SYNC_MODULES_AVAILABLE:
            self.skipTest("Time synchronization modules not available")
        
        self.sync_config = {
            'ntp_servers': [
                'pool.ntp.org',
                'time.google.com',
                'time.cloudflare.com'
            ],
            'sync_interval': 300,  # 5 minutes
            'precision_threshold': 0.001,  # 1ms
            'max_offset': 1.0,  # 1 second
            'local_time_server': {
                'enabled': True,
                'port': 123,
                'precision': -20  # microsecond precision
            }
        }
        
        self.master_sync = MasterClockSynchronizer(self.sync_config)

    def test_synchronizer_initialization(self):
        """Test master clock synchronizer initialization."""
        self.assertEqual(self.master_sync.config['sync_interval'], 300)
        self.assertIsNotNone(self.master_sync.ntp_servers)
        self.assertEqual(len(self.master_sync.ntp_servers), 3)

    def test_ntp_server_query(self):
        """Test querying NTP servers for time synchronization."""
        with patch('master_clock_synchronizer.ntplib.NTPClient') as mock_ntp_client:
            mock_client = Mock()
            mock_ntp_client.return_value = mock_client
            
            # Mock NTP response
            mock_response = Mock()
            mock_response.tx_time = time.time()
            mock_response.offset = -0.002  # 2ms offset
            mock_response.delay = 0.05  # 50ms round-trip
            mock_response.precision = -20  # microsecond precision
            
            mock_client.request.return_value = mock_response
            
            sync_result = self.master_sync.query_ntp_server('pool.ntp.org')
            
            self.assertTrue(sync_result.success)
            self.assertEqual(sync_result.offset, -0.002)
            self.assertEqual(sync_result.delay, 0.05)
            mock_client.request.assert_called_with('pool.ntp.org')

    def test_multiple_server_synchronization(self):
        """Test synchronization with multiple NTP servers."""
        with patch('master_clock_synchronizer.ntplib.NTPClient') as mock_ntp_client:
            mock_client = Mock()
            mock_ntp_client.return_value = mock_client
            
            # Mock responses from different servers
            mock_responses = [
                Mock(tx_time=time.time(), offset=-0.001, delay=0.03, precision=-20),
                Mock(tx_time=time.time(), offset=-0.002, delay=0.05, precision=-19),
                Mock(tx_time=time.time(), offset=-0.0015, delay=0.04, precision=-20)
            ]
            
            mock_client.request.side_effect = mock_responses
            
            sync_results = self.master_sync.synchronize_with_multiple_servers()
            
            self.assertEqual(len(sync_results), 3)
            self.assertTrue(all(result.success for result in sync_results))
            
            # Calculate consensus time
            consensus_offset = self.master_sync.calculate_consensus_offset(sync_results)
            self.assertAlmostEqual(consensus_offset, -0.0015, places=4)

    def test_local_clock_adjustment(self):
        """Test local system clock adjustment based on NTP sync."""
        initial_time = time.time()
        offset = -0.005  # 5ms behind
        
        with patch('time.time') as mock_time:
            mock_time.return_value = initial_time
            
            adjustment_result = self.master_sync.adjust_local_clock(offset)
            
            self.assertTrue(adjustment_result.success)
            self.assertEqual(adjustment_result.applied_offset, offset)
            self.assertIsNotNone(adjustment_result.adjusted_time)

    def test_synchronization_accuracy_validation(self):
        """Test validation of synchronization accuracy."""
        # Test different accuracy scenarios
        accuracy_tests = [
            (0.0005, True),   # 0.5ms - within threshold
            (0.001, True),    # 1ms - at threshold
            (0.002, False),   # 2ms - exceeds threshold
            (0.1, False)      # 100ms - far exceeds threshold
        ]
        
        for offset, expected_valid in accuracy_tests:
            is_accurate = self.master_sync.validate_synchronization_accuracy(offset)
            self.assertEqual(is_accurate, expected_valid)

    def test_drift_compensation(self):
        """Test clock drift compensation over time."""
        # Simulate clock drift measurements
        drift_measurements = [
            (0, 0.0),      # Initial measurement
            (300, 0.001),  # 1ms drift after 5 minutes
            (600, 0.002),  # 2ms drift after 10 minutes
            (900, 0.003)   # 3ms drift after 15 minutes
        ]
        
        for timestamp, measured_offset in drift_measurements:
            self.master_sync.record_drift_measurement(timestamp, measured_offset)
        
        # Calculate drift rate
        drift_rate = self.master_sync.calculate_drift_rate()
        expected_drift_rate = 0.003 / 900  # 3ms over 15 minutes
        
        self.assertAlmostEqual(drift_rate, expected_drift_rate, places=6)
        
        # Predict future offset
        future_time = 1200  # 20 minutes
        predicted_offset = self.master_sync.predict_future_offset(future_time)
        expected_offset = drift_rate * future_time
        
        self.assertAlmostEqual(predicted_offset, expected_offset, places=6)

    def test_sync_error_handling(self):
        """Test error handling in synchronization process."""
        with patch('master_clock_synchronizer.ntplib.NTPClient') as mock_ntp_client:
            mock_client = Mock()
            mock_ntp_client.return_value = mock_client
            
            # Simulate network error
            mock_client.request.side_effect = socket.timeout("Connection timeout")
            
            sync_result = self.master_sync.query_ntp_server('unreachable.server')
            
            self.assertFalse(sync_result.success)
            self.assertIsNotNone(sync_result.error_message)

    def test_synchronization_statistics(self):
        """Test collection of synchronization statistics."""
        # Simulate synchronization history
        sync_history = [
            {'timestamp': time.time() - 600, 'offset': -0.001, 'delay': 0.03},
            {'timestamp': time.time() - 300, 'offset': -0.002, 'delay': 0.04},
            {'timestamp': time.time(), 'offset': -0.0015, 'delay': 0.035}
        ]
        
        for sync_data in sync_history:
            self.master_sync.record_sync_result(sync_data)
        
        stats = self.master_sync.get_synchronization_statistics()
        
        self.assertEqual(stats.total_syncs, 3)
        self.assertAlmostEqual(stats.average_offset, -0.0015, places=4)
        self.assertAlmostEqual(stats.average_delay, 0.035, places=4)
        self.assertGreater(stats.precision, 0)


class TestNTPTimeServer(unittest.TestCase):
    """Test NTPTimeServer implementation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not TIME_SYNC_MODULES_AVAILABLE:
            self.skipTest("Time synchronization modules not available")
        
        self.server_config = {
            'port': 8123,  # Non-standard port for testing
            'stratum': 2,
            'precision': -20,
            'reference_id': b'GPS\x00',
            'max_clients': 100,
            'rate_limit': 10  # requests per second per client
        }
        
        self.ntp_server = NTPTimeServer(self.server_config)

    def test_ntp_server_initialization(self):
        """Test NTP server initialization and configuration."""
        self.assertEqual(self.ntp_server.port, 8123)
        self.assertEqual(self.ntp_server.stratum, 2)
        self.assertEqual(self.ntp_server.precision, -20)
        self.assertFalse(self.ntp_server.is_running())

    def test_ntp_packet_creation(self):
        """Test NTP packet creation and parsing."""
        request_packet = NTPPacket()
        request_packet.mode = 3  # Client mode
        request_packet.version = 4  # NTP version 4
        request_packet.transmit_time = time.time()
        
        # Convert to bytes and back
        packet_bytes = request_packet.to_bytes()
        parsed_packet = NTPPacket.from_bytes(packet_bytes)
        
        self.assertEqual(parsed_packet.mode, 3)
        self.assertEqual(parsed_packet.version, 4)
        self.assertAlmostEqual(parsed_packet.transmit_time, request_packet.transmit_time, places=6)

    def test_ntp_response_generation(self):
        """Test NTP response packet generation."""
        # Create mock client request
        client_request = NTPPacket()
        client_request.mode = 3  # Client mode
        client_request.version = 4
        client_request.transmit_time = time.time()
        
        with patch('time.time') as mock_time:
            mock_time.return_value = 1642425600.123456
            
            response = self.ntp_server.create_response_packet(client_request)
            
            self.assertEqual(response.mode, 4)  # Server mode
            self.assertEqual(response.version, 4)
            self.assertEqual(response.stratum, self.server_config['stratum'])
            self.assertEqual(response.precision, self.server_config['precision'])
            self.assertAlmostEqual(response.receive_time, mock_time.return_value, places=6)

    def test_client_rate_limiting(self):
        """Test client request rate limiting."""
        client_ip = '192.168.1.100'
        
        # Test normal rate
        for i in range(5):
            allowed = self.ntp_server.check_rate_limit(client_ip)
            self.assertTrue(allowed)
        
        # Simulate rapid requests (exceeding rate limit)
        for i in range(20):
            self.ntp_server.check_rate_limit(client_ip)
        
        # Should be rate limited now
        allowed = self.ntp_server.check_rate_limit(client_ip)
        self.assertFalse(allowed)

    def test_server_statistics_tracking(self):
        """Test server statistics tracking."""
        # Simulate client requests
        client_ips = ['192.168.1.100', '192.168.1.101', '192.168.1.102']
        
        for ip in client_ips:
            for _ in range(5):
                self.ntp_server.handle_client_request(ip, Mock())
        
        stats = self.ntp_server.get_server_statistics()
        
        self.assertEqual(stats.total_requests, 15)
        self.assertEqual(stats.unique_clients, 3)
        self.assertGreater(stats.requests_per_second, 0)

    def test_time_source_validation(self):
        """Test validation of time source quality."""
        # Test different time source scenarios
        time_sources = [
            {'type': 'GPS', 'stratum': 1, 'precision': -20, 'expected_quality': 'EXCELLENT'},
            {'type': 'NTP', 'stratum': 2, 'precision': -18, 'expected_quality': 'GOOD'},
            {'type': 'LOCAL', 'stratum': 10, 'precision': -10, 'expected_quality': 'POOR'}
        ]
        
        for source in time_sources:
            quality = self.ntp_server.assess_time_source_quality(
                source['stratum'], 
                source['precision']
            )
            self.assertEqual(quality, source['expected_quality'])

    def test_server_start_stop(self):
        """Test NTP server start and stop functionality."""
        with patch('socket.socket') as mock_socket:
            mock_server_socket = Mock()
            mock_socket.return_value = mock_server_socket
            
            # Test server start
            start_result = self.ntp_server.start()
            self.assertTrue(start_result.success)
            self.assertTrue(self.ntp_server.is_running())
            
            # Verify socket configuration
            mock_server_socket.bind.assert_called_with(('', self.server_config['port']))
            
            # Test server stop
            stop_result = self.ntp_server.stop()
            self.assertTrue(stop_result.success)
            self.assertFalse(self.ntp_server.is_running())
            
            mock_server_socket.close.assert_called_once()


class TestCrossDeviceTimeSynchronization(unittest.TestCase):
    """Test cross-device time synchronization workflows."""

    def setUp(self):
        """Set up test fixtures."""
        if not TIME_SYNC_MODULES_AVAILABLE:
            self.skipTest("Time synchronization modules not available")
        
        self.sync_manager = ClockSyncManager()

    def test_device_discovery_for_sync(self):
        """Test discovery of devices for synchronization."""
        with patch('master_clock_synchronizer.network.discover_devices') as mock_discovery:
            mock_devices = [
                {'ip': '192.168.1.100', 'type': 'android', 'capabilities': ['ntp_client']},
                {'ip': '192.168.1.101', 'type': 'python', 'capabilities': ['ntp_server']},
                {'ip': '192.168.1.102', 'type': 'android', 'capabilities': ['ntp_client']}
            ]
            mock_discovery.return_value = mock_devices
            
            discovered_devices = self.sync_manager.discover_sync_capable_devices()
            
            self.assertEqual(len(discovered_devices), 3)
            ntp_clients = [d for d in discovered_devices if 'ntp_client' in d['capabilities']]
            self.assertEqual(len(ntp_clients), 2)

    def test_master_device_selection(self):
        """Test selection of master device for synchronization."""
        devices = [
            {'ip': '192.168.1.100', 'stratum': 3, 'precision': -15, 'stability': 0.8},
            {'ip': '192.168.1.101', 'stratum': 2, 'precision': -18, 'stability': 0.9},
            {'ip': '192.168.1.102', 'stratum': 4, 'precision': -12, 'stability': 0.7}
        ]
        
        master_device = self.sync_manager.select_master_device(devices)
        
        # Device with stratum 2 and best precision should be selected
        self.assertEqual(master_device['ip'], '192.168.1.101')
        self.assertEqual(master_device['stratum'], 2)

    def test_synchronized_recording_session(self):
        """Test synchronized recording session across devices."""
        devices = [
            {'ip': '192.168.1.100', 'type': 'android'},
            {'ip': '192.168.1.101', 'type': 'android'},
            {'ip': '192.168.1.102', 'type': 'python'}
        ]
        
        with patch.object(self.sync_manager, 'synchronize_device') as mock_sync:
            mock_sync.return_value = {'success': True, 'offset': 0.001}
            
            session_config = {
                'session_id': 'sync_test_001',
                'duration': 300,  # 5 minutes
                'sync_interval': 30  # Re-sync every 30 seconds
            }
            
            sync_results = self.sync_manager.start_synchronized_session(devices, session_config)
            
            self.assertTrue(sync_results.success)
            self.assertEqual(len(sync_results.device_offsets), 3)
            self.assertEqual(mock_sync.call_count, 3)

    def test_timing_precision_measurement(self):
        """Test measurement of timing precision across devices."""
        # Simulate timing measurements from multiple devices
        timing_data = {
            '192.168.1.100': [
                {'timestamp': 1642425600.000, 'local_time': 1642425600.001},
                {'timestamp': 1642425601.000, 'local_time': 1642425601.001},
                {'timestamp': 1642425602.000, 'local_time': 1642425602.001}
            ],
            '192.168.1.101': [
                {'timestamp': 1642425600.000, 'local_time': 1642425600.002},
                {'timestamp': 1642425601.000, 'local_time': 1642425601.002},
                {'timestamp': 1642425602.000, 'local_time': 1642425602.002}
            ]
        }
        
        precision_analysis = self.sync_manager.analyze_timing_precision(timing_data)
        
        self.assertIn('average_offset', precision_analysis)
        self.assertIn('max_jitter', precision_analysis)
        self.assertIn('synchronization_quality', precision_analysis)
        
        # Device 1 should have 1ms consistent offset
        device1_offset = precision_analysis['device_offsets']['192.168.1.100']
        self.assertAlmostEqual(device1_offset, 0.001, places=6)

    def test_sync_drift_correction(self):
        """Test correction of synchronization drift over time."""
        # Simulate drift over time
        initial_sync_time = time.time()
        drift_measurements = [
            (initial_sync_time, 0.0),
            (initial_sync_time + 300, 0.001),   # 1ms drift after 5 minutes
            (initial_sync_time + 600, 0.0025),  # 2.5ms drift after 10 minutes
            (initial_sync_time + 900, 0.004)    # 4ms drift after 15 minutes
        ]
        
        for timestamp, measured_drift in drift_measurements:
            self.sync_manager.record_drift_measurement('192.168.1.100', timestamp, measured_drift)
        
        # Calculate and apply drift correction
        correction = self.sync_manager.calculate_drift_correction('192.168.1.100')
        
        self.assertIsNotNone(correction.drift_rate)
        self.assertIsNotNone(correction.correction_factor)
        self.assertTrue(correction.should_correct)

    def test_synchronization_failure_recovery(self):
        """Test recovery from synchronization failures."""
        with patch.object(self.sync_manager, 'synchronize_device') as mock_sync:
            # Simulate intermittent failures
            mock_sync.side_effect = [
                {'success': False, 'error': 'Network timeout'},
                {'success': False, 'error': 'Device unreachable'},
                {'success': True, 'offset': 0.002}  # Recovery on third attempt
            ]
            
            recovery_result = self.sync_manager.attempt_sync_recovery('192.168.1.100')
            
            self.assertTrue(recovery_result.success)
            self.assertEqual(recovery_result.attempts, 3)
            self.assertEqual(mock_sync.call_count, 3)


def create_time_sync_test_suite():
    """Create comprehensive test suite for time synchronization functionality."""
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestMasterClockSynchronizer))
    suite.addTest(unittest.makeSuite(TestNTPTimeServer))
    suite.addTest(unittest.makeSuite(TestCrossDeviceTimeSynchronization))
    
    return suite


if __name__ == '__main__':
    if TIME_SYNC_MODULES_AVAILABLE:
        # Run comprehensive tests
        runner = unittest.TextTestRunner(verbosity=2)
        suite = create_time_sync_test_suite()
        result = runner.run(suite)
        
        # Print results summary
        print(f"\n{'='*60}")
        print(f"Time Synchronization Tests Summary")
        print(f"{'='*60}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    else:
        print("Time synchronization modules not available - skipping tests")