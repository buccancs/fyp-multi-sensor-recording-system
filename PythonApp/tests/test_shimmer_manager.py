import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shimmer_manager import ShimmerManager, ShimmerStatus, ShimmerSample, DeviceConfiguration, PYSHIMMER_AVAILABLE


class TestShimmerManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()
        self.mock_session_manager = Mock()
        self.shimmer_manager = ShimmerManager(session_manager=self.
            mock_session_manager, logger=self.mock_logger)

    def tearDown(self):
        if hasattr(self, 'shimmer_manager'):
            self.shimmer_manager.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        result = self.shimmer_manager.initialize()
        self.assertTrue(result)
        self.assertTrue(self.shimmer_manager.is_initialized)
        self.mock_logger.info.assert_called()

    def test_initialization_failure(self):
        with patch.object(self.shimmer_manager, '_start_background_threads',
            side_effect=Exception('Test error')):
            result = self.shimmer_manager.initialize()
            self.assertFalse(result)
            self.assertFalse(self.shimmer_manager.is_initialized)

    def test_device_scanning(self):
        devices = self.shimmer_manager.scan_and_pair_devices()
        if not PYSHIMMER_AVAILABLE:
            self.assertIsInstance(devices, list)
            self.assertGreater(len(devices), 0)
            for device in devices:
                self.assertRegex(device, '^[0-9A-Fa-f:]{17}$')
        self.mock_logger.info.assert_called()

    def test_device_connection(self):
        self.shimmer_manager.initialize()
        test_devices = ['00:06:66:66:66:66', '00:06:66:66:66:67']
        result = self.shimmer_manager.connect_devices(test_devices)
        if not PYSHIMMER_AVAILABLE:
            self.assertTrue(result)
            status = self.shimmer_manager.get_shimmer_status()
            self.assertGreater(len(status), 0)
            for device_id, device_status in status.items():
                self.assertIsInstance(device_status, ShimmerStatus)
                self.assertTrue(device_status.is_available)
                self.assertTrue(device_status.is_connected)

    def test_channel_configuration(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        channels = {'GSR', 'PPG_A13', 'Accel_X', 'Accel_Y', 'Accel_Z'}
        status = self.shimmer_manager.get_shimmer_status()
        for device_id in status.keys():
            result = self.shimmer_manager.set_enabled_channels(device_id,
                channels)
            self.assertTrue(result)
            self.assertIn(device_id, self.shimmer_manager.device_configurations
                )
            config = self.shimmer_manager.device_configurations[device_id]
            self.assertEqual(config.enabled_channels, channels)

    def test_streaming_control(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        result = self.shimmer_manager.start_streaming()
        self.assertTrue(result)
        self.assertTrue(self.shimmer_manager.is_streaming)
        status = self.shimmer_manager.get_shimmer_status()
        for device_status in status.values():
            self.assertTrue(device_status.is_streaming)
        result = self.shimmer_manager.stop_streaming()
        self.assertTrue(result)
        self.assertFalse(self.shimmer_manager.is_streaming)
        status = self.shimmer_manager.get_shimmer_status()
        for device_status in status.values():
            self.assertFalse(device_status.is_streaming)

    def test_recording_session(self):
        session_dir = Path(self.temp_dir) / 'test_session' / 'shimmer'
        self.mock_session_manager.get_session_directory.return_value = str(
            session_dir.parent)
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        session_id = 'test_session_123'
        result = self.shimmer_manager.start_recording(session_id)
        self.assertTrue(result)
        self.assertTrue(self.shimmer_manager.is_recording)
        self.assertEqual(self.shimmer_manager.current_session_id, session_id)
        self.assertTrue(session_dir.exists())
        csv_files = list(session_dir.glob('*.csv'))
        self.assertGreater(len(csv_files), 0)
        result = self.shimmer_manager.stop_recording()
        self.assertTrue(result)
        self.assertFalse(self.shimmer_manager.is_recording)
        self.assertIsNone(self.shimmer_manager.current_session_id)

    def test_data_callbacks(self):
        self.shimmer_manager.initialize()
        callback_data = []

        def test_callback(sample):
            callback_data.append(sample)
        self.shimmer_manager.add_data_callback(test_callback)
        test_sample = ShimmerSample(timestamp=time.time(), system_time=
            '2025-07-30T03:13:00', device_id='test_device', gsr_conductance
            =5.0, ppg_a13=2000.0, accel_x=0.1, accel_y=0.2, accel_z=1.0,
            battery_percentage=85)
        self.shimmer_manager._process_data_sample(test_sample)
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0], test_sample)

    def test_status_callbacks(self):
        self.shimmer_manager.initialize()
        callback_data = []

        def test_callback(device_id, status):
            callback_data.append((device_id, status))
        self.shimmer_manager.add_status_callback(test_callback)
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)

    def test_csv_data_logging(self):
        session_dir = Path(self.temp_dir) / 'csv_test_session' / 'shimmer'
        self.mock_session_manager.get_session_directory.return_value = str(
            session_dir.parent)
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        session_id = 'csv_test_session'
        self.shimmer_manager.start_recording(session_id)
        test_samples = []
        for i in range(5):
            sample = ShimmerSample(timestamp=time.time() + i, system_time=
                f'2025-07-30T03:13:{i:02d}', device_id=
                'shimmer_00_06_66_66_66_66', gsr_conductance=5.0 + i,
                ppg_a13=2000.0 + i * 10, accel_x=0.1 + i * 0.01, accel_y=
                0.2 + i * 0.01, accel_z=1.0 + i * 0.001, battery_percentage
                =85 - i)
            test_samples.append(sample)
            self.shimmer_manager._process_data_sample(sample)
        self.shimmer_manager.stop_recording()
        csv_files = list(session_dir.glob('*.csv'))
        self.assertGreater(len(csv_files), 0)
        import csv
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertGreater(len(rows), 0)
                expected_headers = ['timestamp', 'system_time', 'device_id',
                    'gsr_conductance', 'ppg_a13', 'accel_x', 'accel_y',
                    'accel_z', 'battery_percentage']
                self.assertEqual(list(reader.fieldnames), expected_headers)

    def test_simulated_data_generation(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.shimmer_manager.start_streaming()
        time.sleep(2.0)
        for device_id, data_queue in self.shimmer_manager.data_queues.items():
            self.assertGreater(data_queue.qsize(), 0)
        self.shimmer_manager.stop_streaming()

    def test_error_handling(self):
        result = self.shimmer_manager.start_streaming()
        self.assertFalse(result)
        result = self.shimmer_manager.set_enabled_channels('invalid_device',
            {'GSR'})
        self.assertFalse(result)
        result = self.shimmer_manager.start_recording('test_session')

    def test_cleanup(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.shimmer_manager.start_streaming()
        self.shimmer_manager.cleanup()
        self.assertFalse(self.shimmer_manager.is_initialized)
        self.assertFalse(self.shimmer_manager.is_streaming)
        self.assertFalse(self.shimmer_manager.is_recording)
        self.assertEqual(len(self.shimmer_manager.connected_devices), 0)
        self.assertEqual(len(self.shimmer_manager.device_status), 0)

    def test_thread_safety(self):
        self.shimmer_manager.initialize()
        devices = self.shimmer_manager.scan_and_pair_devices()
        self.shimmer_manager.connect_devices(devices)
        self.shimmer_manager.start_streaming()

        def concurrent_status_check():
            for _ in range(10):
                status = self.shimmer_manager.get_shimmer_status()
                self.assertIsInstance(status, dict)
                time.sleep(0.1)
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=concurrent_status_check)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join(timeout=5.0)
        self.shimmer_manager.stop_streaming()

    def test_data_structures(self):
        status = ShimmerStatus(is_available=True, is_connected=True,
            is_recording=False, is_streaming=True, sampling_rate=128,
            battery_level=85, signal_quality='Good', samples_recorded=1000,
            device_name='Shimmer3_GSR', mac_address='00:06:66:66:66:66',
            firmware_version='1.0.0')
        self.assertTrue(status.is_available)
        self.assertTrue(status.is_connected)
        self.assertEqual(status.sampling_rate, 128)
        self.assertEqual(status.battery_level, 85)
        sample = ShimmerSample(timestamp=time.time(), system_time=
            '2025-07-30T03:13:00', device_id='test_device', gsr_conductance
            =5.0, ppg_a13=2000.0, accel_x=0.1, accel_y=0.2, accel_z=1.0,
            battery_percentage=85)
        self.assertEqual(sample.device_id, 'test_device')
        self.assertEqual(sample.gsr_conductance, 5.0)
        self.assertEqual(sample.battery_percentage, 85)
        config = DeviceConfiguration(device_id='test_device', mac_address=
            '00:06:66:66:66:66', enabled_channels={'GSR', 'PPG_A13'},
            sampling_rate=128, connection_type='bluetooth')
        self.assertEqual(config.device_id, 'test_device')
        self.assertEqual(config.sampling_rate, 128)
        self.assertIn('GSR', config.enabled_channels)


class TestShimmerManagerIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_main_backup_integration(self):
        manager = ShimmerManager()
        try:
            self.assertTrue(manager.initialize())
            devices = manager.scan_and_pair_devices()
            if devices:
                manager.connect_devices(devices)
                channels = {'GSR', 'PPG_A13', 'Accel_X', 'Accel_Y', 'Accel_Z'}
                for device_id in manager.device_status:
                    manager.set_enabled_channels(device_id, channels)
                session_id = f'integration_test_{int(time.time())}'
                manager.start_recording(session_id)
                time.sleep(1.0)
                manager.stop_recording()
                status = manager.get_shimmer_status()
                for device_id, device_status in status.items():
                    self.assertGreaterEqual(device_status.samples_recorded, 0)
        finally:
            manager.cleanup()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format=
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    unittest.main(verbosity=2)
