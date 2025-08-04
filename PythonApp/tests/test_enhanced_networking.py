import asyncio
import base64
import json
import os
import random
import socket
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import List
from unittest.mock import Mock, patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from network.enhanced_device_server import EnhancedDeviceServer, EnhancedRemoteDevice, MessagePriority, ConnectionState, NetworkMessage


class MockDevice:

    def __init__(self, device_id: str, capabilities: List[str]=None):
        self.device_id = device_id
        self.capabilities = capabilities or ['camera', 'thermal']
        self.socket = None
        self.connected = False

    def connect(self, host: str='127.0.0.1', port: int=9001) ->bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            return True
        except Exception as e:
            print(f'Mock device connection failed: {e}')
            return False

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.socket = None

    def send_handshake(self) ->bool:
        message = {'type': 'handshake', 'device_id': self.device_id,
            'capabilities': self.capabilities, 'timestamp': time.time()}
        return self.send_message(message)

    def send_message(self, message: dict) ->bool:
        if not self.connected or not self.socket:
            return False
        try:
            json_data = json.dumps(message).encode('utf-8')
            length_header = len(json_data).to_bytes(4, 'big')
            self.socket.sendall(length_header + json_data)
            return True
        except Exception as e:
            print(f'Send error: {e}')
            return False

    def receive_message(self, timeout: float=1.0) ->dict:
        if not self.connected or not self.socket:
            return None
        try:
            self.socket.settimeout(timeout)
            length_data = self.socket.recv(4)
            if len(length_data) != 4:
                return None
            message_length = int.from_bytes(length_data, 'big')
            json_data = b''
            while len(json_data) < message_length:
                chunk = self.socket.recv(message_length - len(json_data))
                if not chunk:
                    return None
                json_data += chunk
            return json.loads(json_data.decode('utf-8'))
        except socket.timeout:
            return None
        except Exception as e:
            print(f'Receive error: {e}')
            return None

    def send_heartbeat(self) ->bool:
        message = {'type': 'heartbeat', 'timestamp': time.time()}
        return self.send_message(message)

    def send_status(self, **kwargs) ->bool:
        message = {'type': 'status', 'timestamp': time.time(), **kwargs}
        return self.send_message(message)

    def send_preview_frame(self, frame_type: str='rgb') ->bool:
        test_image = b'test_image_data_' + os.urandom(100)
        image_b64 = base64.b64encode(test_image).decode('utf-8')
        message = {'type': 'preview_frame', 'frame_type': frame_type,
            'image_data': image_b64, 'width': 640, 'height': 480,
            'timestamp': time.time()}
        return self.send_message(message)


class TestEnhancedNetworking(unittest.TestCase):

    def setUp(self):
        self.server = EnhancedDeviceServer(host='127.0.0.1', port=9001,
            heartbeat_interval=1.0)
        self.server_thread = None
        self.mock_devices = []

    def tearDown(self):
        for device in self.mock_devices:
            device.disconnect()
        self.mock_devices.clear()
        if self.server and self.server.running:
            self.server.stop_server()
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)

    def start_server(self):
        success = self.server.start_server()
        self.assertTrue(success, 'Server should start successfully')
        time.sleep(0.5)

    def create_mock_device(self, device_id: str) ->MockDevice:
        device = MockDevice(device_id)
        self.assertTrue(device.connect(port=9001),
            f'Device {device_id} should connect')
        self.assertTrue(device.send_handshake(),
            f'Device {device_id} should send handshake')
        self.mock_devices.append(device)
        time.sleep(0.2)
        return device

    def test_enhanced_server_startup(self):
        self.assertFalse(self.server.running)
        self.start_server()
        self.assertTrue(self.server.running)
        stats = self.server.get_network_statistics()
        self.assertEqual(stats['active_devices'], 0)
        self.assertEqual(stats['total_connections'], 0)

    def test_device_connection_with_handshake(self):
        self.start_server()
        connection_events = []

        def on_device_connected(device_id, device_info):
            connection_events.append(('connected', device_id, device_info))
        self.server.device_connected.connect(on_device_connected)
        device = self.create_mock_device('test_device_1')
        time.sleep(1.0)
        stats = self.server.get_network_statistics()
        self.assertEqual(stats['active_devices'], 1)
        self.assertIn('test_device_1', stats['devices'])
        self.assertEqual(len(connection_events), 1)
        self.assertEqual(connection_events[0][1], 'test_device_1')

    def test_heartbeat_mechanism(self):
        self.start_server()
        device = self.create_mock_device('heartbeat_test')
        for _ in range(3):
            self.assertTrue(device.send_heartbeat())
            time.sleep(0.5)
        stats = self.server.get_network_statistics()
        device_info = stats['devices']['heartbeat_test']
        self.assertTrue(device_info['is_alive'])
        time.sleep(3.0)
        stats = self.server.get_network_statistics()

    def test_message_priority_handling(self):
        self.start_server()
        device = self.create_mock_device('priority_test')
        messages_sent = []
        preview_msg = device.send_preview_frame('rgb')
        messages_sent.append(('preview', 'low'))
        status_msg = device.send_status(battery=75, recording=True)
        messages_sent.append(('status', 'high'))
        heartbeat_msg = device.send_heartbeat()
        messages_sent.append(('heartbeat', 'critical'))
        time.sleep(1.0)
        self.assertTrue(preview_msg)
        self.assertTrue(status_msg)
        self.assertTrue(heartbeat_msg)

    def test_adaptive_streaming_quality(self):
        self.start_server()
        device = self.create_mock_device('streaming_test')
        frame_count = 0
        start_time = time.time()
        for i in range(20):
            if device.send_preview_frame('rgb'):
                frame_count += 1
            time.sleep(0.05)
        duration = time.time() - start_time
        actual_fps = frame_count / duration
        self.assertLess(actual_fps, 18, 'Frame rate should be limited')
        print(f'Actual FPS: {actual_fps:.2f}')

    def test_connection_recovery(self):
        self.start_server()
        disconnection_events = []

        def on_device_disconnected(device_id, reason):
            disconnection_events.append((device_id, reason))
        self.server.device_disconnected.connect(on_device_disconnected)
        device = self.create_mock_device('recovery_test')
        device.socket.close()
        device.connected = False
        time.sleep(2.0)
        stats = self.server.get_network_statistics()
        self.assertEqual(stats['active_devices'], 0)

    def test_concurrent_device_connections(self):
        self.start_server()
        devices = []
        threads = []

        def connect_device(device_id):
            device = MockDevice(device_id)
            if device.connect(port=9001) and device.send_handshake():
                devices.append(device)
                self.mock_devices.append(device)
        for i in range(5):
            thread = threading.Thread(target=connect_device, args=(
                f'concurrent_device_{i}',))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        time.sleep(1.0)
        stats = self.server.get_network_statistics()
        self.assertEqual(stats['active_devices'], 5)
        self.assertEqual(len(devices), 5)
        message_threads = []

        def send_messages(device):
            for i in range(10):
                device.send_status(battery=random.randint(50, 100))
                device.send_preview_frame('rgb')
                time.sleep(0.1)
        for device in devices:
            thread = threading.Thread(target=send_messages, args=(device,))
            message_threads.append(thread)
            thread.start()
        for thread in message_threads:
            thread.join()
        print(f'Concurrent test completed with {len(devices)} devices')

    def test_large_message_handling(self):
        self.start_server()
        device = self.create_mock_device('large_msg_test')
        large_data = os.urandom(1024 * 1024)
        large_b64 = base64.b64encode(large_data).decode('utf-8')
        large_message = {'type': 'preview_frame', 'frame_type': 'rgb',
            'image_data': large_b64, 'width': 1920, 'height': 1080,
            'timestamp': time.time()}
        success = device.send_message(large_message)
        self.assertTrue(success, 'Large message should be sent successfully')
        time.sleep(2.0)
        stats = self.server.get_network_statistics()
        device_stats = stats['devices']['large_msg_test']
        self.assertGreater(device_stats['stats']['bytes_received'], 1024 * 1024
            )

    def test_error_handling_and_recovery(self):
        self.start_server()
        error_events = []

        def on_error_occurred(device_id, error_type, error_message):
            error_events.append((device_id, error_type, error_message))
        self.server.error_occurred.connect(on_error_occurred)
        device = self.create_mock_device('error_test')
        invalid_message = b'invalid_json_data'
        try:
            length_header = len(invalid_message).to_bytes(4, 'big')
            device.socket.send(length_header + invalid_message)
        except:
            pass
        time.sleep(1.0)
        self.assertTrue(device.send_status(battery=80))
        time.sleep(1.0)
        stats = self.server.get_network_statistics()
        if 'error_test' in stats['devices']:
            device_stats = stats['devices']['error_test']
            self.assertGreater(device_stats['stats']['error_count'], 0)

    def test_server_command_broadcasting(self):
        self.start_server()
        devices = []
        for i in range(3):
            device = self.create_mock_device(f'broadcast_test_{i}')
            devices.append(device)
        time.sleep(1.0)
        count = self.server.broadcast_command('start_recording', session_id
            ='test_session')
        self.assertEqual(count, 3, 'Command should be sent to all devices')
        for device in devices:
            response = device.receive_message(timeout=2.0)
            if response:
                self.assertEqual(response.get('type'), 'command')
                self.assertEqual(response.get('command'), 'start_recording')

    def test_network_statistics_accuracy(self):
        self.start_server()
        device = self.create_mock_device('stats_test')
        message_count = 10
        for i in range(message_count):
            device.send_status(battery=80 - i)
            device.send_preview_frame('rgb')
        time.sleep(2.0)
        stats = self.server.get_network_statistics()
        device_stats = stats['devices']['stats_test']
        self.assertGreaterEqual(device_stats['stats']['messages_received'],
            message_count * 2, 'Message count should be tracked accurately')
        self.assertGreater(device_stats['stats']['bytes_received'], 0,
            'Byte count should be tracked')


class TestNetworkPerformance(unittest.TestCase):

    def setUp(self):
        self.server = EnhancedDeviceServer(host='127.0.0.1', port=9002,
            max_connections=20, heartbeat_interval=2.0)

    def tearDown(self):
        if self.server and self.server.running:
            self.server.stop_server()

    def test_high_frequency_messaging(self):
        success = self.server.start_server()
        self.assertTrue(success)
        time.sleep(0.5)
        device = MockDevice('perf_test')
        self.assertTrue(device.connect(port=9002))
        self.assertTrue(device.send_handshake())
        start_time = time.time()
        message_count = 100
        successful_sends = 0
        for i in range(message_count):
            if device.send_status(battery=random.randint(50, 100)):
                successful_sends += 1
            time.sleep(0.01)
        duration = time.time() - start_time
        print(
            f'High frequency test: {successful_sends}/{message_count} messages in {duration:.2f}s'
            )
        print(f'Rate: {successful_sends / duration:.2f} messages/second')
        self.assertGreater(successful_sends / duration, 50,
            'Should handle at least 50 msg/sec')
        device.disconnect()

    def test_memory_usage_stability(self):
        import psutil
        import gc
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        success = self.server.start_server()
        self.assertTrue(success)
        time.sleep(0.5)
        device = MockDevice('memory_test')
        self.assertTrue(device.connect(port=9002))
        self.assertTrue(device.send_handshake())
        for cycle in range(10):
            for i in range(50):
                device.send_status(battery=random.randint(50, 100))
                device.send_preview_frame('rgb')
            current_memory = process.memory_info().rss
            memory_growth = current_memory - initial_memory
            print(
                f'Cycle {cycle}: Memory growth: {memory_growth / 1024 / 1024:.2f} MB'
                )
            gc.collect()
            time.sleep(0.1)
        final_memory = process.memory_info().rss
        total_growth = final_memory - initial_memory
        print(f'Total memory growth: {total_growth / 1024 / 1024:.2f} MB')
        self.assertLess(total_growth, 50 * 1024 * 1024,
            'Memory growth should be bounded')
        device.disconnect()


def run_comprehensive_tests():
    print('Starting Comprehensive Enhanced Networking Tests')
    print('=' * 60)
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestEnhancedNetworking))
    test_suite.addTest(unittest.makeSuite(TestNetworkPerformance))
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    print('\n' + '=' * 60)
    print('Enhanced Networking Test Summary:')
    print(f'Tests run: {result.testsRun}')
    print(f'Failures: {len(result.failures)}')
    print(f'Errors: {len(result.errors)}')
    print(
        f'Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%'
        )
    if result.failures:
        print('\nFailures:')
        for test, trace in result.failures:
            print(f'- {test}: {trace.split(chr(10))[-2]}')
    if result.errors:
        print('\nErrors:')
        for test, trace in result.errors:
            print(f'- {test}: {trace.split(chr(10))[-2]}')
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
