import asyncio
import json
import os
import socket
import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from network.enhanced_device_server import EnhancedDeviceServer, EnhancedRemoteDevice, MessagePriority, ConnectionState, NetworkMessage


class TestLatencyMeasurement(unittest.TestCase):

    def setUp(self):
        self.server = EnhancedDeviceServer(host='127.0.0.1', port=9001,
            max_connections=5, heartbeat_interval=1.0)
        self.mock_devices = []

    def tearDown(self):
        for device in self.mock_devices:
            device.disconnect()
        if self.server.running:
            self.server.stop_server()

    def test_latency_calculation_basic(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))
        test_latencies = [10.0, 15.0, 20.0, 12.0, 18.0]
        for latency in test_latencies:
            device.update_latency(latency)
        self.assertEqual(len(device.stats.latency_samples), 5)
        self.assertAlmostEqual(device.stats.average_latency, 15.0, places=1)
        self.assertEqual(device.stats.min_latency, 10.0)
        self.assertEqual(device.stats.max_latency, 20.0)
        self.assertGreater(device.stats.jitter, 0)

    def test_ping_pong_handling(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))
        ping_timestamp = time.time()
        ping_data = f'ping:test_ping_1:{ping_timestamp}:1'
        self.server.handle_ping_message(device, ping_data, ping_timestamp)
        self.assertEqual(device.stats.pong_count, 1)
        self.assertGreater(len(device.stats.latency_samples), 0)

    def test_jitter_calculation(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))
        high_jitter_latencies = [10.0, 50.0, 5.0, 45.0, 15.0, 40.0]
        for latency in high_jitter_latencies:
            device.update_latency(latency)
        high_jitter = device.stats.jitter
        device.stats.latency_samples.clear()
        low_jitter_latencies = [20.0, 21.0, 19.0, 20.5, 19.5, 20.2]
        for latency in low_jitter_latencies:
            device.update_latency(latency)
        low_jitter = device.stats.jitter
        self.assertGreater(high_jitter, low_jitter)

    def test_packet_loss_calculation(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))
        device.stats.ping_count = 10
        device.stats.pong_count = 8
        device.update_latency(10.0)
        self.assertAlmostEqual(device.stats.packet_loss_rate, 20.0, places=1)

    def test_network_quality_assessment(self):
        self.assertTrue(self.server.start_server())
        time.sleep(0.1)
        devices_data = [('excellent_device', [5.0, 6.0, 4.0, 5.5, 4.5]), (
            'good_device', [60.0, 70.0, 65.0, 55.0, 75.0]), ('poor_device',
            [250.0, 300.0, 280.0, 320.0, 290.0])]
        for device_id, latencies in devices_data:
            mock_socket = Mock()
            device = EnhancedRemoteDevice(device_id=device_id, capabilities
                =['camera'], client_socket=mock_socket, address=(
                '127.0.0.1', 12345))
            with self.server.devices_mutex:
                self.server.devices[device_id] = device
            for latency in latencies:
                device.update_latency(latency)
        stats = self.server.get_network_statistics()
        self.assertEqual(stats['active_devices'], 3)
        self.assertIn('overall_stats', stats)
        self.assertIn('network_quality', stats['overall_stats'])
        for device_id, _ in devices_data:
            device_stats = self.server.get_device_latency_statistics(device_id)
            self.assertIn('average_latency', device_stats)
            self.assertIn('jitter', device_stats)
            self.assertIn('packet_loss_rate', device_stats)

    def test_latency_statistics_api(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))
        with self.server.devices_mutex:
            self.server.devices['test_device_1'] = device
        test_latencies = [10.0, 15.0, 12.0, 18.0, 14.0]
        for latency in test_latencies:
            device.update_latency(latency)
        stats = self.server.get_device_latency_statistics('test_device_1')
        self.assertEqual(stats['device_id'], 'test_device_1')
        self.assertAlmostEqual(stats['average_latency'], 13.8, places=1)
        self.assertEqual(stats['min_latency'], 10.0)
        self.assertEqual(stats['max_latency'], 18.0)
        self.assertEqual(stats['sample_count'], 5)
        self.assertIsInstance(stats['recent_samples'], list)
        empty_stats = self.server.get_device_latency_statistics('non_existent')
        self.assertIn('error', empty_stats)

    def test_adaptive_quality_based_on_latency(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))
        device.adapt_streaming_quality(25.0, 0.01)
        self.assertEqual(device.streaming_quality, 'high')
        self.assertEqual(device.max_frame_rate, 30)
        device.adapt_streaming_quality(250.0, 0.15)
        self.assertEqual(device.streaming_quality, 'low')
        self.assertEqual(device.max_frame_rate, 5)
        device.adapt_streaming_quality(100.0, 0.07)
        self.assertEqual(device.streaming_quality, 'medium')
        self.assertEqual(device.max_frame_rate, 15)

    def test_timestamp_accuracy(self):
        start_time = time.time()
        message = {'type': 'heartbeat', 'timestamp': start_time}
        time.sleep(0.01)
        process_time = time.time()
        latency = (process_time - message['timestamp']) * 1000
        self.assertGreater(latency, 5.0)
        self.assertLess(latency, 50.0)

    def test_concurrent_latency_measurement(self):
        mock_socket = Mock()
        device = EnhancedRemoteDevice(device_id='test_device_1',
            capabilities=['camera'], client_socket=mock_socket, address=(
            '127.0.0.1', 12345))

        def add_latencies(start_latency, count):
            for i in range(count):
                device.update_latency(start_latency + i)
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_latencies, args=(i * 10, 10))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(device.stats.latency_samples), 50)
        self.assertGreater(device.stats.average_latency, 0)
        self.assertGreater(device.stats.max_latency, device.stats.min_latency)


class TestLatencyIntegration(unittest.TestCase):

    def setUp(self):
        self.server = EnhancedDeviceServer(host='127.0.0.1', port=9002,
            max_connections=5, heartbeat_interval=0.5)

    def tearDown(self):
        if self.server.running:
            self.server.stop_server()

    def test_end_to_end_latency_measurement(self):
        self.assertTrue(self.server.start_server())
        time.sleep(0.1)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(('127.0.0.1', 9002))
            handshake = {'type': 'handshake', 'device_id':
                'integration_test_device', 'capabilities': ['camera',
                'enhanced_latency'], 'timestamp': time.time()}
            json_data = json.dumps(handshake).encode('utf-8')
            length_header = len(json_data).to_bytes(4, 'big')
            client_socket.sendall(length_header + json_data)
            time.sleep(0.1)
            ping_timestamp = time.time()
            ping_message = {'type': 'status', 'storage':
                f'ping:test_ping:{ping_timestamp}:1', 'timestamp':
                ping_timestamp, 'battery': 80, 'connected': True}
            json_data = json.dumps(ping_message).encode('utf-8')
            length_header = len(json_data).to_bytes(4, 'big')
            client_socket.sendall(length_header + json_data)
            time.sleep(0.1)
            stats = self.server.get_network_statistics()
            self.assertGreater(stats['active_devices'], 0)
            if 'integration_test_device' in stats['devices']:
                device_stats = stats['devices']['integration_test_device'][
                    'stats']
                self.assertGreaterEqual(device_stats['pong_count'], 1)
        finally:
            client_socket.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
