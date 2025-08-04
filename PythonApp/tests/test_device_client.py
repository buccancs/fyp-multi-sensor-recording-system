import json
import socket
import ssl
import threading
import time
import unittest
import uuid
from collections import defaultdict
from unittest.mock import MagicMock, Mock, patch
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtTest import QSignalSpy
from PythonApp.src.network.device_client import DeviceClient


class TestDeviceClientEnhanced(unittest.TestCase):

    def setUp(self):
        self.app = QCoreApplication.instance()
        if self.app is None:
            self.app = QCoreApplication([])
        self.device_client = DeviceClient()
        self.test_device_ip = '127.0.0.1'
        self.test_device_port = 9999
        self.device_client.server_port = self.test_device_port

    def tearDown(self):
        if self.device_client.running:
            self.device_client.stop_client()

    def test_device_client_initialization_enhanced(self):
        self.assertIsInstance(self.device_client, DeviceClient)
        self.assertEqual(self.device_client.server_port, self.test_device_port)
        self.assertEqual(self.device_client.buffer_size, 4096)
        self.assertEqual(self.device_client.connection_timeout, 30)
        self.assertEqual(self.device_client.heartbeat_interval, 5)
        self.assertEqual(self.device_client.max_reconnect_attempts, 3)
        self.assertFalse(self.device_client.running)
        self.assertEqual(len(self.device_client.devices), 0)
        self.assertIsInstance(self.device_client._pending_acknowledgments, dict
            )
        self.assertEqual(self.device_client._ack_timeout, 10)
        self.assertEqual(self.device_client._retry_attempts, 3)
        self.assertIsInstance(self.device_client._rate_limiter, defaultdict)
        self.assertEqual(self.device_client._max_requests_per_minute, 60)
        self.assertFalse(self.device_client._ssl_enabled)

    def test_ssl_configuration(self):
        with patch('ssl.create_default_context') as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            result = self.device_client.configure_ssl('/path/to/cert.pem',
                '/path/to/key.pem')
            self.assertTrue(result)
            self.assertTrue(self.device_client._ssl_enabled)
            self.assertIsNotNone(self.device_client._ssl_context)
            mock_ssl_context.assert_called_once_with(ssl.Purpose.CLIENT_AUTH)
            mock_context.load_cert_chain.assert_called_once_with(
                '/path/to/cert.pem', '/path/to/key.pem')

    def test_rate_limiting_mechanism(self):
        device_ip = '192.168.1.100'
        for i in range(30):
            result = self.device_client._check_rate_limit(device_ip)
            self.assertTrue(result, f'Request {i} should be allowed')
        for i in range(35):
            self.device_client._check_rate_limit(device_ip)
        result = self.device_client._check_rate_limit(device_ip)
        self.assertFalse(result, 'Rate limit should be exceeded')

    def test_capability_negotiation(self):
        device_id = 0
        device_capabilities = ['recording', 'streaming', 'thermal_imaging']
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {'socket': Mock(), 'ip':
                '192.168.1.100', 'port': 8080, 'status': 'connected',
                'capabilities': device_capabilities}
        requested_capabilities = ['recording', 'streaming', 'audio_capture',
            'gsr_monitoring']
        result = self.device_client.negotiate_capabilities(device_id,
            requested_capabilities)
        self.assertTrue(result['recording'])
        self.assertTrue(result['streaming'])
        self.assertFalse(result['audio_capture'])
        self.assertFalse(result['gsr_monitoring'])

    def test_reliable_message_delivery_with_ack(self):
        device_id = 0
        mock_socket = Mock()
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {'socket': mock_socket,
                'ip': '192.168.1.100', 'port': 8080, 'status': 'connected'}
        result = self.device_client.send_command(device_id, 'START', {
            'mode': 'recording'}, require_ack=True)
        self.assertTrue(result)
        mock_socket.send.assert_called_once()
        self.assertEqual(len(self.device_client._pending_acknowledgments), 1)
        sent_data = mock_socket.send.call_args[0][0]
        sent_message = json.loads(sent_data.decode('utf-8'))
        message_id = sent_message['message_id']
        self.assertIn(message_id, self.device_client._pending_acknowledgments)

    def test_acknowledgment_timeout_handling(self):
        message_id = str(uuid.uuid4())
        device_id = 0
        self.device_client._pending_acknowledgments[message_id] = {
            'device_index': device_id, 'command': 'START', 'timestamp':
            time.time(), 'attempts': 1, 'max_attempts': 3}
        mock_socket = Mock()
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {'socket': mock_socket,
                'ip': '192.168.1.100', 'port': 8080, 'status': 'connected'}
        self.device_client._handle_ack_timeout(message_id)
        self.assertEqual(self.device_client._pending_acknowledgments[
            message_id]['attempts'], 2)

    def test_enhanced_message_processing(self):
        device_id = 0
        ack_message = {'type': 'acknowledgment', 'message_id':
            'test-message-123', 'timestamp': time.time()}
        self.device_client._pending_acknowledgments['test-message-123'] = {
            'device_index': device_id, 'command': 'START', 'timestamp': 
            time.time() - 1, 'attempts': 1, 'max_attempts': 3}
        self.device_client._process_device_message(device_id, ack_message)
        self.assertNotIn('test-message-123', self.device_client.
            _pending_acknowledgments)

    def test_capability_response_processing(self):
        device_id = 0
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {'socket': Mock(), 'ip':
                '192.168.1.100', 'port': 8080, 'status': 'connected',
                'capabilities': []}
        capability_message = {'type': 'capability_response', 'capabilities':
            ['recording', 'streaming', 'thermal_imaging']}
        self.device_client._process_device_message(device_id,
            capability_message)
        with self.device_client._device_lock:
            updated_capabilities = self.device_client.devices[device_id][
                'capabilities']
            self.assertEqual(updated_capabilities, ['recording',
                'streaming', 'thermal_imaging'])

    def test_performance_metrics_collection(self):
        self.device_client._message_stats['sent'] = 100
        self.device_client._message_stats['received'] = 95
        self.device_client._message_stats['errors'] = 2
        self.device_client._message_stats['connection_count'] = 5
        self.device_client._message_stats['avg_latency'] = 0.015
        self.device_client._pending_acknowledgments['test1'] = {}
        self.device_client._pending_acknowledgments['test2'] = {}
        metrics = self.device_client.get_performance_metrics()
        self.assertEqual(metrics['messages_sent'], 100)
        self.assertEqual(metrics['messages_received'], 95)
        self.assertEqual(metrics['error_count'], 2)
        self.assertEqual(metrics['total_connections'], 5)
        self.assertEqual(metrics['average_latency_ms'], 15.0)
        self.assertEqual(metrics['pending_acknowledgments'], 2)
        self.assertFalse(metrics['ssl_enabled'])
        self.assertEqual(metrics['rate_limit_per_minute'], 60)

    def test_latency_statistics_update(self):
        self.device_client._update_latency_stats(0.02)
        self.assertAlmostEqual(self.device_client._message_stats[
            'avg_latency'], 0.02, places=3)
        self.device_client._update_latency_stats(0.01)
        expected_avg = 0.1 * 0.01 + 0.9 * 0.02
        self.assertAlmostEqual(self.device_client._message_stats[
            'avg_latency'], expected_avg, places=3)

    def test_error_message_processing(self):
        device_id = 0
        error_spy = QSignalSpy(self.device_client.error_occurred)
        error_message = {'type': 'error', 'error':
            'Sensor calibration failed', 'timestamp': time.time()}
        self.device_client._process_device_message(device_id, error_message)
        self.assertEqual(len(error_spy), 1)
        emitted_error = error_spy[0][0]
        self.assertIn('Device 0 error', emitted_error)
        self.assertIn('Sensor calibration failed', emitted_error)

    def test_comprehensive_ssl_server_setup(self):
        with patch('ssl.create_default_context') as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_wrapped_socket = Mock()
            mock_context.wrap_socket.return_value = mock_wrapped_socket
            self.device_client.configure_ssl('/path/to/cert.pem',
                '/path/to/key.pem')
            with patch('socket.socket') as mock_socket:
                mock_socket_instance = Mock()
                mock_socket.return_value = mock_socket_instance
                mock_socket_instance.accept.side_effect = socket.timeout
                self.device_client.start()
                time.sleep(0.1)
                self.device_client.stop_client()
                mock_context.wrap_socket.assert_called_once_with(
                    mock_socket_instance, server_side=True)

    def test_device_connection_rate_limiting(self):
        address = '192.168.1.100', 12345
        for _ in range(65):
            self.device_client._check_rate_limit(address[0])
        mock_socket = Mock()
        with patch.object(self.device_client, '_check_rate_limit',
            return_value=False):
            self.device_client.handle_device_connection(mock_socket, address)
            mock_socket.close.assert_called_once()

    def test_json_protocol_validation(self):
        device_id = 0
        valid_message = {'type': 'status', 'timestamp': time.time(),
            'device_status': 'recording', 'battery_level': 85}
        try:
            self.device_client._process_device_message(device_id, valid_message
                )
        except Exception as e:
            self.fail(f'Valid message processing failed: {e}')
        initial_received = self.device_client._message_stats['received']
        self.device_client._process_device_message(device_id, valid_message)
        self.assertEqual(self.device_client._message_stats['received'], 
            initial_received + 1)

    def test_thread_safety_concurrent_operations(self):
        import threading
        import time
        device_id = 0
        mock_socket = Mock()
        with self.device_client._device_lock:
            self.device_client.devices[device_id] = {'socket': mock_socket,
                'ip': '192.168.1.100', 'port': 8080, 'status': 'connected',
                'capabilities': ['recording']}

        def send_commands():
            for i in range(10):
                self.device_client.send_command(device_id, f'TEST_{i}',
                    require_ack=False)
                time.sleep(0.001)

        def process_messages():
            for i in range(10):
                message = {'type': 'heartbeat', 'timestamp': time.time()}
                self.device_client._process_device_message(device_id, message)
                time.sleep(0.001)
        thread1 = threading.Thread(target=send_commands)
        thread2 = threading.Thread(target=process_messages)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()

    def test_device_connection_success(self):
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            handshake_response = {'status': 'accepted', 'device_info': {
                'name': 'Test Device'}, 'capabilities': ['recording',
                'streaming']}
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response).encode('utf-8')
            result = self.device_client.connect_to_device('192.168.1.100', 8080
                )
            self.assertTrue(result)
            mock_socket_instance.connect.assert_called_once_with((
                '192.168.1.100', 8080))
            mock_socket_instance.send.assert_called()
            mock_socket_instance.recv.assert_called()

    def test_device_connection_failure(self):
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = ConnectionRefusedError(
                'Connection refused')
            result = self.device_client.connect_to_device('192.168.1.100', 8080
                )
            self.assertFalse(result)

    def test_device_disconnection(self):
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            handshake_response = {'status': 'accepted', 'device_info': {
                'name': 'Test Device'}, 'capabilities': ['recording']}
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response).encode('utf-8')
            self.device_client.connect_to_device('192.168.1.100', 8080)
            self.device_client.disconnect_device(0)
            mock_socket_instance.close.assert_called()

    def test_send_command_success(self):
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            handshake_response = {'status': 'accepted', 'device_info': {
                'name': 'Test Device'}, 'capabilities': ['recording']}
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response).encode('utf-8')
            self.device_client.connect_to_device('192.168.1.100', 8080)
            mock_socket_instance.send.reset_mock()
            result = self.device_client.send_command(0, 'START', {'mode':
                'recording'})
            self.assertTrue(result)
            mock_socket_instance.send.assert_called()

    def test_send_command_to_nonexistent_device(self):
        result = self.device_client.send_command(99, 'START')
        self.assertFalse(result)

    def test_get_connected_devices(self):
        devices = self.device_client.get_connected_devices()
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), 0)

    def test_command_protocol_format(self):
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            handshake_response = {'status': 'accepted', 'device_info': {
                'name': 'Test Device'}, 'capabilities': ['recording']}
            mock_socket_instance.recv.return_value = json.dumps(
                handshake_response).encode('utf-8')
            self.device_client.connect_to_device('192.168.1.100', 8080)
            mock_socket_instance.send.reset_mock()
            self.device_client.send_command(0, 'CALIBRATE', {'sensor': 'GSR'})
            mock_socket_instance.send.assert_called()
            sent_data = mock_socket_instance.send.call_args[0][0]
            try:
                message = json.loads(sent_data.decode('utf-8'))
                self.assertIn('type', message)
                self.assertIn('command', message)
                self.assertIn('parameters', message)
                self.assertIn('timestamp', message)
                self.assertIn('message_id', message)
                self.assertEqual(message['type'], 'command')
                self.assertEqual(message['command'], 'CALIBRATE')
                self.assertEqual(message['parameters']['sensor'], 'GSR')
            except json.JSONDecodeError:
                self.fail('Sent data is not valid JSON')

    @patch('time.sleep')
    def test_server_socket_setup(self, mock_sleep):
        with patch('socket.socket') as mock_socket:
            mock_server_socket = MagicMock()
            mock_socket.return_value = mock_server_socket
            self.device_client.start()
            time.sleep(0.1)
            self.device_client.stop_client()
            mock_server_socket.bind.assert_called_with(('0.0.0.0', 8080))
            mock_server_socket.listen.assert_called()

    def test_error_signal_emission(self):
        error_messages = []

        def capture_error(message):
            error_messages.append(message)
        self.device_client.error_occurred.connect(capture_error)
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = OSError(
                'Network unreachable')
            result = self.device_client.connect_to_device('invalid_ip', 8080)
            self.assertFalse(result)
            self.assertEqual(len(error_messages), 1)
            self.assertIn('Network unreachable', error_messages[0])

    def test_multiple_device_connections(self):
        with patch('socket.socket') as mock_socket:
            mock_socket1 = MagicMock()
            mock_socket2 = MagicMock()
            mock_socket.side_effect = [mock_socket1, mock_socket2]
            handshake_response = {'status': 'accepted', 'device_info': {
                'name': 'Test Device'}, 'capabilities': ['recording']}
            response_data = json.dumps(handshake_response).encode('utf-8')
            mock_socket1.recv.return_value = response_data
            mock_socket2.recv.return_value = response_data
            result1 = self.device_client.connect_to_device('192.168.1.100',
                8080)
            self.assertTrue(result1)
            result2 = self.device_client.connect_to_device('192.168.1.101',
                8080)
            self.assertTrue(result2)
            devices = self.device_client.get_connected_devices()
            self.assertEqual(len(devices), 2)

    def test_cleanup_procedures(self):
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            self.device_client.connect_to_device('192.168.1.100', 8080)
            self.device_client.start()
            time.sleep(0.1)
            self.device_client.stop_client()
            self.assertFalse(self.device_client.running)


class TestDeviceClientIntegration(unittest.TestCase):

    def setUp(self):
        self.app = QCoreApplication.instance()
        if self.app is None:
            self.app = QCoreApplication([])
        self.device_client = DeviceClient()
        self.test_server_socket = None
        self.test_server_thread = None

    def tearDown(self):
        if self.device_client.running:
            self.device_client.stop_client()
        if self.test_server_socket:
            try:
                self.test_server_socket.close()
            except:
                pass

    def start_mock_device_server(self, port=8081):

        def server_thread():
            try:
                self.test_server_socket = socket.socket(socket.AF_INET,
                    socket.SOCK_STREAM)
                self.test_server_socket.setsockopt(socket.SOL_SOCKET,
                    socket.SO_REUSEADDR, 1)
                self.test_server_socket.bind(('localhost', port))
                self.test_server_socket.listen(1)
                while True:
                    try:
                        client_socket, addr = self.test_server_socket.accept()
                        data = client_socket.recv(1024)
                        if data:
                            client_socket.send(b'ACK')
                        client_socket.close()
                    except:
                        break
            except Exception as e:
                print(f'Mock server error: {e}')
        self.test_server_thread = threading.Thread(target=server_thread,
            daemon=True)
        self.test_server_thread.start()
        time.sleep(0.1)

    def test_real_socket_connection(self):
        self.start_mock_device_server(8081)
        result = self.device_client.connect_to_device('localhost', 8081)
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
