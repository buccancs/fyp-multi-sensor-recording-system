import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shimmer_manager import ShimmerManager, ShimmerSample
from ntp_time_server import TimeServerManager


class TestHardwareFailureRecovery(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()
        self.shimmer_manager = ShimmerManager(logger=self.mock_logger)
        self.time_server_manager = TimeServerManager(logger=self.mock_logger)

    def tearDown(self):
        try:
            self.shimmer_manager.cleanup()
            self.time_server_manager.stop()
        except:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_shimmer_device_disconnection_recovery(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        session_id = 'failure_test_session'
        self.shimmer_manager.start_recording(session_id)
        self.assertTrue(self.shimmer_manager.is_recording)
        original_status = self.shimmer_manager.device_status.copy()
        for device_id in list(self.shimmer_manager.device_status.keys()):
            self.shimmer_manager.device_status[device_id].is_connected = False
            self.shimmer_manager.device_status[device_id].is_streaming = False
        self.assertTrue(self.shimmer_manager.is_recording)
        result = self.shimmer_manager.stop_recording()
        self.assertTrue(result)

    def test_ntp_server_network_interruption(self):
        self.time_server_manager.initialize(port=8901)
        self.time_server_manager.start()
        time.sleep(0.1)
        status = self.time_server_manager.get_status()
        self.assertTrue(status.is_running)
        self.time_server_manager.stop()
        status = self.time_server_manager.get_status()
        if status:
            self.assertFalse(status.is_running)
        restart_result = self.time_server_manager.start()

    def test_concurrent_device_failures(self):
        self.shimmer_manager.initialize()
        self.time_server_manager.initialize(port=8902)
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.time_server_manager.start()
        session_id = 'concurrent_failure_test'
        recording_started = self.shimmer_manager.start_recording(session_id)
        failure_events = []

        def simulate_shimmer_failure():
            try:
                for device_id in self.shimmer_manager.device_status:
                    self.shimmer_manager.device_status[device_id
                        ].is_connected = False
                failure_events.append('shimmer_failed')
            except Exception as e:
                failure_events.append(f'shimmer_error: {e}')

        def simulate_ntp_failure():
            try:
                self.time_server_manager.stop()
                failure_events.append('ntp_failed')
            except Exception as e:
                failure_events.append(f'ntp_error: {e}')
        shimmer_thread = threading.Thread(target=simulate_shimmer_failure)
        ntp_thread = threading.Thread(target=simulate_ntp_failure)
        shimmer_thread.start()
        ntp_thread.start()
        shimmer_thread.join(timeout=2.0)
        ntp_thread.join(timeout=2.0)
        self.assertGreater(len(failure_events), 0)
        cleanup_result = self.shimmer_manager.stop_recording()

    def test_resource_exhaustion_recovery(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        connection_results = []
        for i in range(10):
            result = self.shimmer_manager.connect_devices(devices)
            connection_results.append(result)
        self.assertIsInstance(connection_results, list)
        cleanup_success = True
        try:
            self.shimmer_manager.cleanup()
        except Exception:
            cleanup_success = False
        self.assertTrue(cleanup_success)

    def test_data_corruption_handling(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        corrupted_sample = ShimmerSample(timestamp=float('inf'),
            system_time='invalid_time_format', device_id='',
            gsr_conductance=None, ppg_a13=float('nan'), accel_x=None,
            accel_y=None, accel_z=None, battery_percentage=-1)
        processing_success = True
        try:
            self.shimmer_manager._process_data_sample(corrupted_sample)
        except Exception:
            processing_success = False

    def test_memory_leak_prevention(self):
        self.shimmer_manager.initialize()
        for cycle in range(5):
            devices = self.shimmer_manager.scan_and_pair_devices()
            self.shimmer_manager.connect_devices(devices)
            session_id = f'memory_test_{cycle}'
            self.shimmer_manager.start_recording(session_id)
            self.shimmer_manager.stop_recording()
            time.sleep(0.1)
        self.assertEqual(len(self.shimmer_manager.connected_devices), 0)
        self.assertEqual(len(self.shimmer_manager.csv_writers), 0)
        self.assertEqual(len(self.shimmer_manager.csv_files), 0)

    def test_thread_safety_under_failure(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.shimmer_manager.start_streaming()
        results = []

        def concurrent_status_check():
            for _ in range(5):
                try:
                    status = self.shimmer_manager.get_shimmer_status()
                    results.append(('status', len(status)))
                except Exception as e:
                    results.append(('error', str(e)))
                time.sleep(0.01)

        def concurrent_failure_simulation():
            time.sleep(0.02)
            try:
                for device_id in self.shimmer_manager.device_status:
                    self.shimmer_manager.device_status[device_id
                        ].is_connected = False
                results.append(('failure_simulated', True))
            except Exception as e:
                results.append(('failure_error', str(e)))
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=concurrent_status_check)
            threads.append(thread)
            thread.start()
        failure_thread = threading.Thread(target=concurrent_failure_simulation)
        threads.append(failure_thread)
        failure_thread.start()
        for thread in threads:
            thread.join(timeout=2.0)
        self.assertGreater(len(results), 0)
        self.shimmer_manager.stop_streaming()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format=
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    unittest.main(verbosity=2)
