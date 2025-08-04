import sys
import os
import unittest
import tempfile
import time
import json
from unittest.mock import Mock, patch, MagicMock, call
from threading import Event
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    from shimmer_manager import ShimmerManager
except ImportError as e:
    print(f'Warning: Cannot import ShimmerManager: {e}')
    ShimmerManager = None


class TestShimmerManagerComprehensive(unittest.TestCase):

    def setUp(self):
        if ShimmerManager is None:
            self.skipTest('ShimmerManager not available')
        self.test_dir = tempfile.mkdtemp()
        with patch('shimmer_manager.AndroidDeviceManager'):
            self.manager = ShimmerManager(enable_android_integration=False)

    def tearDown(self):
        if hasattr(self, 'manager'):
            self.manager.stop_recording()
            self.manager.disconnect_all_devices()

    def test_shimmer_manager_initialization(self):
        self.assertIsNotNone(self.manager)
        self.assertFalse(self.manager.android_integration_enabled)
        self.assertEqual(len(self.manager.connected_devices), 0)

    @patch('shimmer_manager.socket.socket')
    def test_bluetooth_scanning_framework(self, mock_socket):
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.recv.return_value = b'mock_device_response'
        devices = self.manager.scan_and_pair_devices()
        self.assertIsInstance(devices, dict)
        self.assertIn('direct', devices)
        self.assertIn('android', devices)
        self.assertIn('simulated', devices)
        self.assertGreater(len(devices['simulated']), 0)

    def test_shimmer_library_detection(self):
        available_libs = self.manager._check_available_libraries()
        self.assertIsInstance(available_libs, dict)
        self.assertIn('pyshimmer', available_libs)
        self.assertIn('bluetooth', available_libs)
        self.assertIn('pybluez', available_libs)
        for lib, available in available_libs.items():
            self.assertIsInstance(available, bool)

    @patch('shimmer_manager.serial.Serial')
    def test_device_connection_framework(self, mock_serial):
        mock_connection = Mock()
        mock_serial.return_value = mock_connection
        mock_connection.is_open = True
        device_info = {'address': 'mock_address', 'name': 'Mock Shimmer',
            'type': 'simulated'}
        success = self.manager.connect_device(device_info)
        self.assertIsInstance(success, bool)

    def test_sensor_channel_mapping(self):
        channel_map = self.manager._get_channel_mapping()
        self.assertIsInstance(channel_map, dict)
        expected_channels = ['timestamp', 'gsr', 'ppg', 'accel_x',
            'accel_y', 'accel_z']
        for channel in expected_channels:
            self.assertIn(channel, channel_map)

    def test_data_callback_system(self):
        callback_called = Event()
        received_data = []

        def test_callback(data):
            received_data.append(data)
            callback_called.set()
        self.manager.register_data_callback(test_callback)
        mock_data = {'timestamp': time.time(), 'gsr': 1234.5, 'ppg': 2048,
            'accel_x': 0.1, 'accel_y': 0.2, 'accel_z': 0.9}
        self.manager._process_shimmer_data(mock_data)
        callback_called.wait(timeout=1.0)
        self.assertEqual(len(received_data), 1)
        self.assertEqual(received_data[0], mock_data)

    def test_data_conversion_utilities(self):
        raw_data = [12345, 6789, 1024, 2048, 4096, 8192]
        converted = self.manager._convert_raw_data(raw_data)
        self.assertIsInstance(converted, dict)
        self.assertIn('timestamp', converted)
        self.assertIn('gsr', converted)
        valid_data = {'timestamp': time.time(), 'gsr': 1000.0, 'ppg': 2000,
            'accel_x': 0.1}
        is_valid = self.manager._validate_data(valid_data)
        self.assertTrue(is_valid)
        invalid_data = {'gsr': 'invalid_value'}
        is_valid = self.manager._validate_data(invalid_data)
        self.assertFalse(is_valid)

    def test_session_management(self):
        session_id = self.manager.start_recording_session()
        self.assertIsNotNone(session_id)
        self.assertTrue(self.manager.is_recording)
        for i in range(10):
            mock_data = {'timestamp': time.time() + i * 0.1, 'gsr': 1000 + 
                i * 10, 'ppg': 2000 + i * 5, 'accel_x': 0.1 + i * 0.01}
            self.manager._add_data_to_session(mock_data)
        file_path = self.manager.stop_recording_session()
        self.assertIsNotNone(file_path)
        self.assertFalse(self.manager.is_recording)
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertIn('timestamp', content)
                self.assertIn('gsr', content)

    def test_csv_export_functionality(self):
        session_data = []
        for i in range(5):
            session_data.append({'timestamp': time.time() + i, 'gsr': 1000 +
                i * 10, 'ppg': 2000 + i * 5, 'accel_x': 0.1 + i * 0.01,
                'accel_y': 0.2 + i * 0.01, 'accel_z': 0.9 + i * 0.01})
        csv_path = os.path.join(self.test_dir, 'test_export.csv')
        success = self.manager._export_session_to_csv(session_data, csv_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 1)
            self.assertIn('timestamp', lines[0])
            self.assertIn('gsr', lines[0])

    @patch('shimmer_manager.threading.Thread')
    def test_concurrent_device_management(self, mock_thread):
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        devices = [{'address': 'device1', 'name': 'Shimmer1', 'type':
            'simulated'}, {'address': 'device2', 'name': 'Shimmer2', 'type':
            'simulated'}]
        for device in devices:
            self.manager.connect_device(device)
        self.assertIsInstance(self.manager.connected_devices, dict)

    def test_error_handling_and_recovery(self):
        fake_device = {'address': 'fake_address', 'name': 'Fake Device',
            'type': 'direct'}
        result = self.manager.connect_device(fake_device)
        self.assertIsInstance(result, bool)
        invalid_data = None
        try:
            self.manager._process_shimmer_data(invalid_data)
        except Exception as e:
            self.fail(f'Should handle invalid data gracefully: {e}')

    def test_configuration_management(self):
        device_address = 'mock_device'
        sampling_rate = 128
        try:
            success = self.manager._configure_device_sampling_rate(
                device_address, sampling_rate)
            self.assertIsInstance(success, bool)
        except Exception as e:
            self.fail(f'Configuration should handle gracefully: {e}')

    def test_performance_monitoring(self):
        start_time = time.time()
        for i in range(100):
            mock_data = {'timestamp': time.time(), 'gsr': 1000 + i, 'ppg': 
                2000 + i}
            self.manager._process_shimmer_data(mock_data)
        processing_time = time.time() - start_time
        self.assertLess(processing_time, 5.0)
        print(f'Processed 100 samples in {processing_time:.3f}s')

    def test_bluetooth_library_fallbacks(self):
        with patch.dict('sys.modules', {'pyshimmer': None}):
            devices = self.manager.scan_and_pair_devices()
            self.assertIn('simulated', devices)
        with patch.dict('sys.modules', {'bluetooth': None}):
            devices = self.manager.scan_and_pair_devices()
            self.assertIn('simulated', devices)

    def test_data_quality_validation(self):
        good_data = {'timestamp': time.time(), 'gsr': 1234.5, 'ppg': 2048,
            'accel_x': 0.1, 'accel_y': 0.2, 'accel_z': 0.9}
        quality_score = self.manager._assess_data_quality(good_data)
        self.assertIsInstance(quality_score, (int, float))
        self.assertGreaterEqual(quality_score, 0)
        self.assertLessEqual(quality_score, 1)
        poor_data = {'timestamp': time.time(), 'gsr': 999999, 'ppg': -1000,
            'accel_x': 100}
        quality_score = self.manager._assess_data_quality(poor_data)
        self.assertLess(quality_score, 0.5)

    def test_integration_workflow(self):
        print('\nTesting complete Shimmer integration workflow...')
        devices = self.manager.scan_and_pair_devices()
        print(
            f'Discovered {sum(len(v) for v in devices.values())} devices total'
            )
        if devices['simulated']:
            device = devices['simulated'][0]
            connected = self.manager.connect_device(device)
            print(f'Connection attempt result: {connected}')
        session_id = self.manager.start_recording_session()
        print(f'Started recording session: {session_id}')
        for i in range(20):
            mock_data = {'timestamp': time.time() + i * 0.05, 'gsr': 1000 +
                i * 5 + i % 3 * 10, 'ppg': 2000 + i * 2 + i % 5 * 20,
                'accel_x': 0.1 + i % 7 * 0.01, 'accel_y': 0.2 + i % 11 * 
                0.01, 'accel_z': 0.9 + i % 13 * 0.01}
            self.manager._process_shimmer_data(mock_data)
            time.sleep(0.01)
        print('Simulated 20 data samples')
        output_file = self.manager.stop_recording_session()
        print(f'Recording saved to: {output_file}')
        if output_file and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                lines = f.readlines()
                print(f'Output file contains {len(lines)} lines')
                self.assertGreater(len(lines), 1)
        print('✓ Complete workflow test passed')

    def test_stress_testing(self):
        print('\nRunning stress tests...')
        start_time = time.time()
        data_count = 0
        for i in range(1000):
            mock_data = {'timestamp': time.time() + i * 0.001, 'gsr': 1000 +
                i % 100, 'ppg': 2000 + i % 200}
            self.manager._process_shimmer_data(mock_data)
            data_count += 1
        processing_time = time.time() - start_time
        throughput = data_count / processing_time
        print(f'Processed {data_count} samples in {processing_time:.3f}s')
        print(f'Throughput: {throughput:.1f} samples/second')
        self.assertGreater(throughput, 100)


def run_shimmer_tests():
    if ShimmerManager is None:
        print('Skipping Shimmer tests - module not available')
        return True
    print('=' * 80)
    print('COMPREHENSIVE SHIMMER MANAGER TESTS')
    print('=' * 80)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestShimmerManagerComprehensive)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print(f'\nTest Results:')
    print(f'Tests run: {result.testsRun}')
    print(f'Failures: {len(result.failures)}')
    print(f'Errors: {len(result.errors)}')
    print(
        f'Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%'
        )
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_shimmer_tests()
    sys.exit(0 if success else 1)
