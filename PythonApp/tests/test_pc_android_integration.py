import asyncio
import base64
import json
import os
import sys
import threading
import time
import unittest
from typing import Dict, List, Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from network.enhanced_device_server import EnhancedDeviceServer, MessagePriority, ConnectionState


class AndroidDeviceSimulator:

    def __init__(self, device_id: str, capabilities: List[str]=None):
        self.device_id = device_id
        self.capabilities = capabilities or ['rgb_video', 'thermal',
            'shimmer', 'enhanced_client']
        self.socket = None
        self.connected = False
        self.running = False
        self.recording = False
        self.battery_level = 85
        self.storage_available = '15.2 GB'
        self.temperature = 36.5
        self.streaming_preview = False
        self.streaming_quality = 'medium'
        self.frame_counter = 0
        self.command_handlers = {'start_recording': self.
            handle_start_recording, 'stop_recording': self.
            handle_stop_recording, 'capture_calibration': self.
            handle_capture_calibration, 'set_streaming_quality': self.
            handle_set_streaming_quality, 'get_status': self.
            handle_get_status, 'start_preview': self.handle_start_preview,
            'stop_preview': self.handle_stop_preview}
        self.commands_received = 0
        self.frames_sent = 0
        self.last_heartbeat = time.time()

    def connect(self, host: str='127.0.0.1', port: int=9001) ->bool:
        try:
            import socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            print(
                f'Android simulator {self.device_id} connected to {host}:{port}'
                )
            return True
        except Exception as e:
            print(f'Connection failed: {e}')
            return False

    def disconnect(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        print(f'Android simulator {self.device_id} disconnected')

    def start_simulation(self):
        if not self.connected:
            return False
        self.running = True
        if not self.send_handshake():
            return False
        threading.Thread(target=self.message_loop, daemon=True).start()
        threading.Thread(target=self.status_update_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        print(f'Android simulator {self.device_id} started')
        return True

    def send_handshake(self) ->bool:
        handshake = {'type': 'handshake', 'device_id': self.device_id,
            'capabilities': self.capabilities, 'app_version': '1.0.0',
            'device_type': 'android', 'timestamp': time.time()}
        return self.send_message(handshake)

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

    def receive_message(self, timeout: float=1.0) ->Optional[dict]:
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
        except Exception:
            return None

    def message_loop(self):
        while self.running and self.connected:
            message = self.receive_message(timeout=0.5)
            if message:
                self.process_message(message)
            time.sleep(0.01)

    def process_message(self, message: dict):
        msg_type = message.get('type')
        if msg_type == 'command':
            self.handle_command(message)
        elif msg_type == 'heartbeat':
            self.handle_heartbeat(message)
        elif msg_type == 'handshake_ack':
            self.handle_handshake_ack(message)
        else:
            print(f'Unknown message type: {msg_type}')

    def handle_command(self, message: dict):
        command = message.get('command')
        self.commands_received += 1
        print(f'Android {self.device_id} received command: {command}')
        success = True
        error_message = None
        if command in self.command_handlers:
            try:
                result = self.command_handlers[command](message)
                success = result.get('success', True)
                error_message = result.get('error', None)
            except Exception as e:
                success = False
                error_message = str(e)
        else:
            success = False
            error_message = f'Unknown command: {command}'
        self.send_ack(command, success, error_message)

    def send_ack(self, command: str, success: bool, error_message: str=None):
        ack = {'type': 'ack', 'cmd': command, 'status': 'ok' if success else
            'error', 'message': error_message, 'timestamp': time.time()}
        self.send_message(ack)

    def handle_start_recording(self, message: dict) ->dict:
        session_id = message.get('session_id', 'unknown')
        self.recording = True
        if not self.streaming_preview:
            self.streaming_preview = True
            threading.Thread(target=self.preview_streaming_loop, daemon=True
                ).start()
        print(
            f'Android {self.device_id} started recording session: {session_id}'
            )
        return {'success': True}

    def handle_stop_recording(self, message: dict) ->dict:
        self.recording = False
        self.streaming_preview = False
        print(f'Android {self.device_id} stopped recording')
        return {'success': True}

    def handle_capture_calibration(self, message: dict) ->dict:
        calibration_id = message.get('calibration_id', 'cal_' + str(int(
            time.time())))
        capture_rgb = message.get('capture_rgb', True)
        capture_thermal = message.get('capture_thermal', True)
        time.sleep(0.5)
        calibration_result = {'type': 'calibration_result',
            'calibration_id': calibration_id, 'success': True, 'rms_error':
            0.45, 'images_captured': {'rgb': capture_rgb, 'thermal':
            capture_thermal}, 'timestamp': time.time()}
        self.send_message(calibration_result)
        print(
            f'Android {self.device_id} captured calibration: {calibration_id}')
        return {'success': True}

    def handle_set_streaming_quality(self, message: dict) ->dict:
        quality = message.get('quality', 'medium')
        self.streaming_quality = quality
        print(f'Android {self.device_id} set streaming quality to: {quality}')
        return {'success': True}

    def handle_get_status(self, message: dict) ->dict:
        self.send_status_update()
        return {'success': True}

    def handle_start_preview(self, message: dict) ->dict:
        if not self.streaming_preview:
            self.streaming_preview = True
            threading.Thread(target=self.preview_streaming_loop, daemon=True
                ).start()
        print(f'Android {self.device_id} started preview streaming')
        return {'success': True}

    def handle_stop_preview(self, message: dict) ->dict:
        self.streaming_preview = False
        print(f'Android {self.device_id} stopped preview streaming')
        return {'success': True}

    def handle_heartbeat(self, message: dict):
        self.last_heartbeat = time.time()
        response = {'type': 'heartbeat_response', 'timestamp': time.time()}
        self.send_message(response)

    def handle_handshake_ack(self, message: dict):
        compatible = message.get('compatible', False)
        if compatible:
            print(f'Android {self.device_id} handshake acknowledged')
        else:
            print(f'Android {self.device_id} protocol incompatible')

    def status_update_loop(self):
        while self.running and self.connected:
            time.sleep(10)
            if self.recording:
                self.battery_level = max(0, self.battery_level - 1)
            self.send_status_update()

    def send_status_update(self):
        status = {'type': 'status', 'battery': self.battery_level,
            'storage': self.storage_available, 'temperature': self.
            temperature, 'recording': self.recording, 'connected': True,
            'timestamp': time.time()}
        self.send_message(status)

    def heartbeat_loop(self):
        while self.running and self.connected:
            time.sleep(5)
            heartbeat = {'type': 'heartbeat', 'timestamp': time.time()}
            self.send_message(heartbeat)

    def preview_streaming_loop(self):
        frame_rates = {'low': 5, 'medium': 15, 'high': 30}
        while self.streaming_preview and self.running and self.connected:
            fps = frame_rates.get(self.streaming_quality, 15)
            frame_interval = 1.0 / fps
            self.send_preview_frame()
            self.frames_sent += 1
            time.sleep(frame_interval)

    def send_preview_frame(self):
        frame_size = {'low': 100, 'medium': 500, 'high': 1000}
        size = frame_size.get(self.streaming_quality, 500)
        mock_image_data = os.urandom(size)
        image_b64 = base64.b64encode(mock_image_data).decode('utf-8')
        frame = {'type': 'preview_frame', 'frame_type': 'rgb', 'image_data':
            image_b64, 'width': 640, 'height': 480, 'frame_id': self.
            frame_counter, 'quality': self.streaming_quality, 'timestamp':
            time.time()}
        self.send_message(frame)
        self.frame_counter += 1

    def get_statistics(self) ->dict:
        return {'device_id': self.device_id, 'connected': self.connected,
            'recording': self.recording, 'streaming': self.
            streaming_preview, 'commands_received': self.commands_received,
            'frames_sent': self.frames_sent, 'battery_level': self.
            battery_level, 'last_heartbeat': self.last_heartbeat}


class PCController:

    def __init__(self, server: EnhancedDeviceServer):
        self.server = server
        self.connected_devices = {}
        self.command_responses = {}
        self.server.device_connected.connect(self.on_device_connected)
        self.server.device_disconnected.connect(self.on_device_disconnected)
        self.server.message_received.connect(self.on_message_received)
        self.server.preview_frame_received.connect(self.
            on_preview_frame_received)

    def on_device_connected(self, device_id: str, device_info: dict):
        self.connected_devices[device_id] = device_info
        print(f'PC Controller: Device {device_id} connected')

    def on_device_disconnected(self, device_id: str, reason: str):
        if device_id in self.connected_devices:
            del self.connected_devices[device_id]
        print(f'PC Controller: Device {device_id} disconnected - {reason}')

    def on_message_received(self, device_id: str, message: dict):
        msg_type = message.get('type')
        if msg_type == 'ack':
            command = message.get('cmd')
            status = message.get('status')
            self.command_responses[f'{device_id}_{command}'] = {'success': 
                status == 'ok', 'message': message.get('message'),
                'timestamp': time.time()}
            print(
                f'PC Controller: ACK from {device_id} for {command}: {status}')
        elif msg_type == 'status':
            print(
                f"PC Controller: Status from {device_id} - Battery: {message.get('battery')}%, Recording: {message.get('recording')}"
                )
        elif msg_type == 'calibration_result':
            print(
                f"PC Controller: Calibration result from {device_id} - Success: {message.get('success')}, RMS Error: {message.get('rms_error')}"
                )

    def on_preview_frame_received(self, device_id: str, frame_type: str,
        frame_data: bytes, metadata: dict):
        frame_id = metadata.get('frame_id', 0)
        quality = metadata.get('quality', 'unknown')
        size = len(frame_data)
        print(
            f'PC Controller: Preview frame from {device_id} - Type: {frame_type}, Frame: {frame_id}, Quality: {quality}, Size: {size} bytes'
            )

    def send_command_to_device(self, device_id: str, command: str, **kwargs
        ) ->bool:
        success = self.server.send_command_to_device(device_id, command, **
            kwargs)
        if success:
            print(f'PC Controller: Sent {command} to {device_id}')
        else:
            print(f'PC Controller: Failed to send {command} to {device_id}')
        return success

    def broadcast_command(self, command: str, **kwargs) ->int:
        count = self.server.broadcast_command(command, **kwargs)
        print(f'PC Controller: Broadcasted {command} to {count} devices')
        return count

    def wait_for_ack(self, device_id: str, command: str, timeout: float=5.0
        ) ->bool:
        start_time = time.time()
        ack_key = f'{device_id}_{command}'
        while time.time() - start_time < timeout:
            if ack_key in self.command_responses:
                response = self.command_responses[ack_key]
                del self.command_responses[ack_key]
                return response['success']
            time.sleep(0.1)
        print(
            f'PC Controller: Timeout waiting for ACK from {device_id} for {command}'
            )
        return False

    def get_connected_devices(self) ->List[str]:
        return list(self.connected_devices.keys())


class TestPCAndroidIntegration(unittest.TestCase):

    def setUp(self):
        self.server = EnhancedDeviceServer(host='127.0.0.1', port=9003,
            heartbeat_interval=2.0)
        self.pc_controller = PCController(self.server)
        self.android_devices = []

    def tearDown(self):
        for device in self.android_devices:
            device.disconnect()
        if self.server.running:
            self.server.stop_server()

    def start_test_environment(self):
        success = self.server.start_server()
        self.assertTrue(success, 'Server should start')
        time.sleep(0.5)

    def create_android_device(self, device_id: str) ->AndroidDeviceSimulator:
        device = AndroidDeviceSimulator(device_id)
        self.assertTrue(device.connect(port=9003),
            f'Device {device_id} should connect')
        self.assertTrue(device.start_simulation(),
            f'Device {device_id} should start')
        self.android_devices.append(device)
        time.sleep(1.0)
        return device

    def test_basic_pc_android_communication(self):
        self.start_test_environment()
        android_device = self.create_android_device('test_phone_1')
        devices = self.pc_controller.get_connected_devices()
        self.assertIn('test_phone_1', devices)
        success = self.pc_controller.send_command_to_device('test_phone_1',
            'get_status')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('test_phone_1',
            'get_status')
        self.assertTrue(ack_received, 'Should receive acknowledgment')

    def test_recording_control_workflow(self):
        self.start_test_environment()
        android_device = self.create_android_device('recording_phone')
        success = self.pc_controller.send_command_to_device('recording_phone',
            'start_recording', session_id='test_session_001')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('recording_phone',
            'start_recording')
        self.assertTrue(ack_received, 'Should acknowledge start recording')
        time.sleep(1.0)
        stats = android_device.get_statistics()
        self.assertTrue(stats['recording'], 'Device should be recording')
        self.assertTrue(stats['streaming'], 'Device should be streaming')
        success = self.pc_controller.send_command_to_device('recording_phone',
            'stop_recording')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('recording_phone',
            'stop_recording')
        self.assertTrue(ack_received, 'Should acknowledge stop recording')
        time.sleep(1.0)
        stats = android_device.get_statistics()
        self.assertFalse(stats['recording'], 'Device should stop recording')

    def test_calibration_workflow(self):
        self.start_test_environment()
        android_device = self.create_android_device('calibration_phone')
        success = self.pc_controller.send_command_to_device('calibration_phone'
            , 'capture_calibration', calibration_id='test_cal_001',
            capture_rgb=True, capture_thermal=True)
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('calibration_phone',
            'capture_calibration')
        self.assertTrue(ack_received, 'Should acknowledge calibration command')
        time.sleep(2.0)

    def test_real_time_streaming(self):
        self.start_test_environment()
        android_device = self.create_android_device('streaming_phone')
        success = self.pc_controller.send_command_to_device('streaming_phone',
            'start_preview')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('streaming_phone',
            'start_preview')
        self.assertTrue(ack_received, 'Should acknowledge start preview')
        time.sleep(3.0)
        stats = android_device.get_statistics()
        self.assertGreater(stats['frames_sent'], 0,
            'Should have sent preview frames')
        success = self.pc_controller.send_command_to_device('streaming_phone',
            'set_streaming_quality', quality='high')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('streaming_phone',
            'set_streaming_quality')
        self.assertTrue(ack_received, 'Should acknowledge quality change')
        success = self.pc_controller.send_command_to_device('streaming_phone',
            'stop_preview')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('streaming_phone',
            'stop_preview')
        self.assertTrue(ack_received, 'Should acknowledge stop preview')

    def test_multiple_device_control(self):
        self.start_test_environment()
        devices = []
        for i in range(3):
            device = self.create_android_device(f'multi_phone_{i}')
            devices.append(device)
        connected_devices = self.pc_controller.get_connected_devices()
        self.assertEqual(len(connected_devices), 3,
            'All devices should be connected')
        count = self.pc_controller.broadcast_command('start_recording',
            session_id='multi_session_001')
        self.assertEqual(count, 3, 'Command should be sent to all devices')
        for i in range(3):
            ack_received = self.pc_controller.wait_for_ack(f'multi_phone_{i}',
                'start_recording')
            self.assertTrue(ack_received, f'Device {i} should acknowledge')
        time.sleep(1.0)
        for device in devices:
            stats = device.get_statistics()
            self.assertTrue(stats['recording'],
                'All devices should be recording')
        success = self.pc_controller.send_command_to_device('multi_phone_1',
            'set_streaming_quality', quality='low')
        self.assertTrue(success)
        count = self.pc_controller.broadcast_command('stop_recording')
        self.assertEqual(count, 3, 'Stop command should reach all devices')

    def test_error_recovery_and_reconnection(self):
        self.start_test_environment()
        android_device = self.create_android_device('recovery_phone')
        devices = self.pc_controller.get_connected_devices()
        self.assertIn('recovery_phone', devices)
        android_device.socket.close()
        android_device.connected = False
        time.sleep(3.0)
        devices = self.pc_controller.get_connected_devices()
        self.assertNotIn('recovery_phone', devices)
        android_device.connect(port=9003)
        android_device.start_simulation()
        time.sleep(2.0)
        devices = self.pc_controller.get_connected_devices()
        self.assertIn('recovery_phone', devices)
        success = self.pc_controller.send_command_to_device('recovery_phone',
            'get_status')
        self.assertTrue(success)
        ack_received = self.pc_controller.wait_for_ack('recovery_phone',
            'get_status')
        self.assertTrue(ack_received, 'Commands should work after reconnection'
            )

    def test_heartbeat_and_connection_monitoring(self):
        self.start_test_environment()
        android_device = self.create_android_device('heartbeat_phone')
        time.sleep(10.0)
        stats = android_device.get_statistics()
        self.assertGreater(stats['last_heartbeat'], time.time() - 10,
            'Recent heartbeat should be recorded')
        server_stats = self.server.get_network_statistics()
        device_stats = server_stats['devices']['heartbeat_phone']
        self.assertTrue(device_stats['is_alive'], 'Device should be alive')


def run_integration_tests():
    print('Starting PC-Android Integration Tests')
    print('=' * 60)
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPCAndroidIntegration))
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    print('\n' + '=' * 60)
    print('PC-Android Integration Test Summary:')
    print(f'Tests run: {result.testsRun}')
    print(f'Failures: {len(result.failures)}')
    print(f'Errors: {len(result.errors)}')
    if result.wasSuccessful():
        print('✅ All integration tests passed!')
        print('✅ PC can reliably control Android device')
        print('✅ Rock-solid networking implementation verified')
    else:
        print('❌ Some integration tests failed')
        if result.failures:
            print('\nFailures:')
            for test, trace in result.failures:
                print(f'- {test}')
        if result.errors:
            print('\nErrors:')
            for test, trace in result.errors:
                print(f'- {test}')
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
