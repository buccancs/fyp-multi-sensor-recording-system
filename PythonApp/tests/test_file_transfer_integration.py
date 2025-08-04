import base64
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from network.device_server import JsonSocketServer, RemoteDevice


class TestFileTransferIntegration(unittest.TestCase):

    def setUp(self):
        self.server = JsonSocketServer(host='localhost', port=9001)
        self.test_dir = tempfile.mkdtemp()
        self.mock_socket = Mock()
        self.device_id = 'test_device_123'
        self.session_id = 'test_session_456'
        self.test_device = RemoteDevice(device_id=self.device_id,
            capabilities=['rgb_video', 'thermal', 'shimmer'], client_socket
            =self.mock_socket)
        self.server.devices[self.device_id] = self.test_device
        self.test_file_content = (
            b'Test file content for transfer validation. ' * 100)
        self.test_file_name = 'test_video.mp4'

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.server.cleanup()

    def test_file_info_message_processing(self):
        file_info_message = {'type': 'file_info', 'name': self.
            test_file_name, 'size': len(self.test_file_content)}
        with patch.object(self.server, 'get_session_directory',
            return_value=self.test_dir):
            self.server.process_json_message(self.mock_socket,
                'test_client', file_info_message)
            self.assertTrue(hasattr(self.test_device, 'file_transfer_state'))
            self.assertIsNotNone(self.test_device.file_transfer_state)
            self.assertEqual(self.test_device.file_transfer_state[
                'filename'], self.test_file_name)
            self.assertEqual(self.test_device.file_transfer_state[
                'expected_size'], len(self.test_file_content))
            self.assertEqual(self.test_device.file_transfer_state[
                'received_bytes'], 0)

    def test_file_chunk_message_processing(self):
        self.test_device.file_transfer_state = {'filename': self.
            test_file_name, 'expected_size': len(self.test_file_content),
            'received_bytes': 0, 'file_handle': None, 'chunks_received': 0}
        test_file_path = os.path.join(self.test_dir,
            f'{self.device_id}_{self.test_file_name}')
        self.test_device.file_transfer_state['file_handle'] = open(
            test_file_path, 'wb')
        chunk_data = self.test_file_content[:1000]
        base64_chunk = base64.b64encode(chunk_data).decode('ascii')
        file_chunk_message = {'type': 'file_chunk', 'seq': 1, 'data':
            base64_chunk}
        try:
            self.server.process_json_message(self.mock_socket,
                'test_client', file_chunk_message)
            self.assertEqual(self.test_device.file_transfer_state[
                'received_bytes'], len(chunk_data))
            self.assertEqual(self.test_device.file_transfer_state[
                'chunks_received'], 1)
            self.test_device.file_transfer_state['file_handle'].close()
            with open(test_file_path, 'rb') as f:
                written_content = f.read()
            self.assertEqual(written_content, chunk_data)
        finally:
            if self.test_device.file_transfer_state['file_handle']:
                self.test_device.file_transfer_state['file_handle'].close()

    def test_file_end_message_processing(self):
        test_file_path = os.path.join(self.test_dir,
            f'{self.device_id}_{self.test_file_name}')
        self.test_device.file_transfer_state = {'filename': self.
            test_file_name, 'expected_size': len(self.test_file_content),
            'received_bytes': len(self.test_file_content), 'file_handle':
            open(test_file_path, 'wb'), 'chunks_received': 5}
        self.test_device.file_transfer_state['file_handle'].write(self.
            test_file_content)
        file_end_message = {'type': 'file_end', 'name': self.test_file_name}
        with patch.object(self.server, 'send_command') as mock_send:
            self.server.process_json_message(self.mock_socket,
                'test_client', file_end_message)
            self.assertIsNone(self.test_device.file_transfer_state)
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            self.assertEqual(call_args[0], self.device_id)
            self.assertEqual(call_args[1]['type'], 'file_received')
            self.assertEqual(call_args[1]['status'], 'ok')

    def test_file_end_message_size_mismatch(self):
        test_file_path = os.path.join(self.test_dir,
            f'{self.device_id}_{self.test_file_name}')
        self.test_device.file_transfer_state = {'filename': self.
            test_file_name, 'expected_size': len(self.test_file_content),
            'received_bytes': len(self.test_file_content) - 100,
            'file_handle': open(test_file_path, 'wb'), 'chunks_received': 4}
        file_end_message = {'type': 'file_end', 'name': self.test_file_name}
        with patch.object(self.server, 'send_command') as mock_send:
            self.server.process_json_message(self.mock_socket,
                'test_client', file_end_message)
            self.assertIsNone(self.test_device.file_transfer_state)
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            self.assertEqual(call_args[1]['type'], 'file_received')
            self.assertEqual(call_args[1]['status'], 'error')

    def test_request_file_from_device(self):
        test_filepath = '/storage/test/file.mp4'
        with patch.object(self.server, 'send_command', return_value=True
            ) as mock_send:
            result = self.server.request_file_from_device(self.device_id,
                test_filepath, 'video')
            self.assertTrue(result)
            mock_send.assert_called_once_with(self.device_id, {'type':
                'send_file', 'filepath': test_filepath, 'filetype': 'video'})

    def test_request_file_from_nonexistent_device(self):
        result = self.server.request_file_from_device('nonexistent_device',
            '/test/file.mp4')
        self.assertFalse(result)

    def test_get_expected_files_for_device(self):
        expected_files = self.server.get_expected_files_for_device(self.
            device_id, self.session_id, ['rgb_video', 'thermal', 'shimmer'])
        self.assertEqual(len(expected_files), 3)
        file_types = [os.path.basename(f) for f in expected_files]
        self.assertTrue(any('rgb.mp4' in f for f in file_types))
        self.assertTrue(any('thermal.mp4' in f for f in file_types))
        self.assertTrue(any('sensors.csv' in f for f in file_types))
        for filepath in expected_files:
            self.assertIn(self.session_id, filepath)
            self.assertIn(self.device_id, filepath)

    def test_get_expected_files_partial_capabilities(self):
        expected_files = self.server.get_expected_files_for_device(self.
            device_id, self.session_id, ['rgb_video'])
        self.assertEqual(len(expected_files), 1)
        self.assertTrue(expected_files[0].endswith('rgb.mp4'))

    def test_request_all_session_files(self):
        device2_id = 'test_device_789'
        device2 = RemoteDevice(device_id=device2_id, capabilities=[
            'thermal'], client_socket=Mock())
        self.server.devices[device2_id] = device2
        with patch.object(self.server, 'request_file_from_device',
            return_value=True) as mock_request:
            result = self.server.request_all_session_files(self.session_id)
            self.assertGreater(result, 0)
            call_count = mock_request.call_count
            self.assertGreater(call_count, 0)
            calls = mock_request.call_args_list
            device_ids_called = set()
            for call in calls:
                device_ids_called.add(call[0][0])
            self.assertIn(self.device_id, device_ids_called)
            self.assertIn(device2_id, device_ids_called)

    @patch('os.makedirs')
    @patch('os.getcwd')
    def test_get_session_directory(self, mock_getcwd, mock_makedirs):
        mock_getcwd.return_value = '/test/working/dir'
        session_dir = self.server.get_session_directory()
        self.assertIsNotNone(session_dir)
        self.assertTrue(session_dir.startswith('/test/working/dir/sessions/'))
        self.assertIn('session_', session_dir)
        mock_makedirs.assert_called()

    def test_complete_file_transfer_workflow(self):
        with patch.object(self.server, 'get_session_directory',
            return_value=self.test_dir):
            file_info_message = {'type': 'file_info', 'name': self.
                test_file_name, 'size': len(self.test_file_content)}
            self.server.process_json_message(self.mock_socket,
                'test_client', file_info_message)
            chunk_size = 1000
            chunks = [self.test_file_content[i:i + chunk_size] for i in
                range(0, len(self.test_file_content), chunk_size)]
            for seq, chunk in enumerate(chunks, 1):
                base64_chunk = base64.b64encode(chunk).decode('ascii')
                file_chunk_message = {'type': 'file_chunk', 'seq': seq,
                    'data': base64_chunk}
                self.server.process_json_message(self.mock_socket,
                    'test_client', file_chunk_message)
            file_end_message = {'type': 'file_end', 'name': self.test_file_name
                }
            with patch.object(self.server, 'send_command') as mock_send:
                self.server.process_json_message(self.mock_socket,
                    'test_client', file_end_message)
                test_file_path = os.path.join(self.test_dir,
                    f'{self.device_id}_{self.test_file_name}')
                self.assertTrue(os.path.exists(test_file_path))
                with open(test_file_path, 'rb') as f:
                    received_content = f.read()
                self.assertEqual(received_content, self.test_file_content)
                mock_send.assert_called_once()
                call_args = mock_send.call_args[0]
                self.assertEqual(call_args[1]['status'], 'ok')

    def test_multiple_concurrent_transfers(self):
        devices = []
        for i in range(3):
            device_id = f'device_{i}'
            device = RemoteDevice(device_id=device_id, capabilities=[
                'rgb_video'], client_socket=Mock())
            self.server.devices[device_id] = device
            devices.append((device_id, device))
        with patch.object(self.server, 'get_session_directory',
            return_value=self.test_dir):
            for device_id, device in devices:
                file_info_message = {'type': 'file_info', 'name':
                    f'video_{device_id}.mp4', 'size': 1000}
                self.server.process_json_message(device.client_socket,
                    f'client_{device_id}', file_info_message)
            for device_id, device in devices:
                self.assertTrue(hasattr(device, 'file_transfer_state'))
                self.assertIsNotNone(device.file_transfer_state)
                self.assertEqual(device.file_transfer_state['filename'],
                    f'video_{device_id}.mp4')


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
