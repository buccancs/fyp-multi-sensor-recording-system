import base64
import json
import logging
import os
import socket
import struct
import sys
import threading
import time
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
logging.basicConfig(level=logging.INFO, format=
    '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeviceSimulator:

    def __init__(self, device_id: str, host: str='127.0.0.1', port: int=9000):
        self.device_id = device_id
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False

    def connect(self) ->bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(
                f'Device {self.device_id} connected to {self.host}:{self.port}'
                )
            return True
        except Exception as e:
            logger.error(f'Device {self.device_id} failed to connect: {e}')
            return False

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        self.running = False
        logger.info(f'Device {self.device_id} disconnected')

    def send_message(self, message: Dict[str, Any]) ->bool:
        if not self.connected or not self.socket:
            logger.error(f'Device {self.device_id} not connected')
            return False
        try:
            json_data = json.dumps(message).encode('utf-8')
            length_header = struct.pack('>I', len(json_data))
            self.socket.send(length_header + json_data)
            logger.debug(
                f"Device {self.device_id} sent message: {message.get('type', 'unknown')}"
                )
            return True
        except Exception as e:
            logger.error(f'Device {self.device_id} failed to send message: {e}'
                )
            return False

    def send_hello(self, capabilities: list=None) ->bool:
        if capabilities is None:
            capabilities = ['camera', 'thermal', 'imu', 'gsr']
        hello_message = {'type': 'hello', 'device_id': self.device_id,
            'capabilities': capabilities, 'timestamp': time.time()}
        return self.send_message(hello_message)

    def send_status(self, battery: int=85, temperature: float=36.5,
        recording: bool=False, storage: int=75) ->bool:
        status_message = {'type': 'status', 'battery': battery,
            'temperature': temperature, 'recording': recording, 'storage':
            storage, 'connected': True, 'timestamp': time.time()}
        return self.send_message(status_message)

    def send_preview_frame(self, frame_type: str='rgb', image_data: bytes=None
        ) ->bool:
        if image_data is None:
            image_data = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
                )
        base64_data = base64.b64encode(image_data).decode('utf-8')
        frame_message = {'type': 'preview_frame', 'frame_type': frame_type,
            'frame_data': base64_data, 'timestamp': time.time()}
        return self.send_message(frame_message)

    def send_sensor_data(self, gsr: float=0.5, ppg: float=75.0) ->bool:
        sensor_message = {'type': 'sensor_data', 'gsr': gsr, 'ppg': ppg,
            'accelerometer': {'x': 0.1, 'y': 0.2, 'z': 9.8}, 'gyroscope': {
            'x': 0.01, 'y': 0.02, 'z': 0.03}, 'magnetometer': {'x': 25.0,
            'y': 30.0, 'z': 45.0}, 'timestamp': time.time()}
        return self.send_message(sensor_message)

    def send_ack(self, command: str, success: bool=True, message: str=
        'Command executed successfully') ->bool:
        ack_message = {'type': 'ack', 'cmd': command, 'status': 'ok' if
            success else 'error', 'message': message, 'timestamp': time.time()}
        return self.send_message(ack_message)

    def send_notification(self, event_type: str, event_data: Dict[str, Any]
        =None) ->bool:
        if event_data is None:
            event_data = {}
        notification_message = {'type': 'notification', 'event_type':
            event_type, 'event_data': event_data, 'timestamp': time.time()}
        return self.send_message(notification_message)

    def receive_message(self) ->Optional[Dict[str, Any]]:
        if not self.connected or not self.socket:
            return None
        try:
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            message_length = struct.unpack('>I', length_data)[0]
            json_data = b''
            while len(json_data) < message_length:
                chunk = self.socket.recv(message_length - len(json_data))
                if not chunk:
                    return None
                json_data += chunk
            message = json.loads(json_data.decode('utf-8'))
            logger.debug(
                f"Device {self.device_id} received: {message.get('type', 'unknown')}"
                )
            return message
        except Exception as e:
            logger.error(
                f'Device {self.device_id} failed to receive message: {e}')
            return None

    def run_simulation(self, duration: int=30):
        if not self.connect():
            return
        self.running = True
        if not self.send_hello():
            self.disconnect()
            return
        start_time = time.time()
        last_status = start_time
        last_frame = start_time
        last_sensor = start_time
        logger.info(
            f'Device {self.device_id} starting simulation for {duration} seconds'
            )
        try:
            while self.running and time.time() - start_time < duration:
                current_time = time.time()
                if current_time - last_status >= 5:
                    battery = max(10, 100 - int((current_time - start_time) *
                        2))
                    self.send_status(battery=battery)
                    last_status = current_time
                if current_time - last_frame >= 2:
                    frame_type = 'rgb' if int(current_time
                        ) % 4 < 2 else 'thermal'
                    self.send_preview_frame(frame_type=frame_type)
                    last_frame = current_time
                if current_time - last_sensor >= 1:
                    gsr = 0.3 + 0.4 * (current_time % 10) / 10
                    ppg = 70 + 10 * (current_time % 5) / 5
                    self.send_sensor_data(gsr=gsr, ppg=ppg)
                    last_sensor = current_time
                self.socket.settimeout(0.1)
                try:
                    message = self.receive_message()
                    if message and message.get('type') == 'command':
                        command = message.get('command', 'unknown')
                        logger.info(
                            f'Device {self.device_id} received command: {command}'
                            )
                        if command in ['start_recording', 'stop_recording',
                            'capture_calibration']:
                            self.send_ack(command, success=True)
                        else:
                            self.send_ack(command, success=False, message=
                                'Unknown command')
                except socket.timeout:
                    pass
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info(f'Device {self.device_id} simulation interrupted')
        finally:
            self.disconnect()


def test_single_device():
    logger.info('=== Testing Single Device Connection ===')
    device = DeviceSimulator('TestDevice1')
    if not device.connect():
        logger.error('Failed to connect device')
        return False
    if not device.send_hello(['camera', 'thermal', 'imu']):
        logger.error('Failed to send hello message')
        device.disconnect()
        return False
    time.sleep(1)
    if not device.send_status(battery=78, temperature=37.2):
        logger.error('Failed to send status message')
        device.disconnect()
        return False
    time.sleep(1)
    if not device.send_preview_frame('rgb'):
        logger.error('Failed to send preview frame')
        device.disconnect()
        return False
    time.sleep(1)
    if not device.send_sensor_data(gsr=0.6, ppg=80.0):
        logger.error('Failed to send sensor data')
        device.disconnect()
        return False
    time.sleep(1)
    if not device.send_notification('recording_started', {'session_id':
        'test_123'}):
        logger.error('Failed to send notification')
        device.disconnect()
        return False
    time.sleep(2)
    device.disconnect()
    logger.info('Single device test completed successfully')
    return True


def test_multiple_devices():
    logger.info('=== Testing Multiple Device Connections ===')
    devices = [DeviceSimulator('TestDevice1'), DeviceSimulator(
        'TestDevice2'), DeviceSimulator('TestDevice3')]
    connected_devices = []
    for device in devices:
        if device.connect():
            connected_devices.append(device)
            device.send_hello()
            time.sleep(0.5)
    if len(connected_devices) != len(devices):
        logger.error(
            f'Only {len(connected_devices)}/{len(devices)} devices connected')
    for i, device in enumerate(connected_devices):
        device.send_status(battery=90 - i * 10)
        device.send_preview_frame('rgb' if i % 2 == 0 else 'thermal')
        time.sleep(0.2)
    time.sleep(2)
    for device in connected_devices:
        device.disconnect()
    logger.info(
        f'Multiple device test completed with {len(connected_devices)} devices'
        )
    return len(connected_devices) == len(devices)


def test_device_simulation():
    logger.info('=== Testing Device Simulation ===')
    device = DeviceSimulator('SimulationDevice')
    simulation_thread = threading.Thread(target=device.run_simulation, args
        =(10,))
    simulation_thread.start()
    simulation_thread.join()
    logger.info('Device simulation test completed')
    return True


def main():
    logger.info('Starting JsonSocketServer Device Simulator Tests')
    tests = [('Single Device Test', test_single_device), (
        'Multiple Devices Test', test_multiple_devices), (
        'Device Simulation Test', test_device_simulation)]
    passed = 0
    total = len(tests)
    for test_name, test_func in tests:
        try:
            logger.info(f'\n--- Running {test_name} ---')
            if test_func():
                logger.info(f'✓ {test_name} PASSED')
                passed += 1
            else:
                logger.error(f'✗ {test_name} FAILED')
        except Exception as e:
            logger.error(f'✗ {test_name} FAILED with exception: {e}')
        time.sleep(2)
    logger.info(f'\n=== Test Results ===')
    logger.info(f'Passed: {passed}/{total}')
    logger.info(f'Failed: {total - passed}/{total}')
    if passed == total:
        logger.info('All tests passed! ✓')
        return 0
    else:
        logger.error('Some tests failed! ✗')
        return 1


if __name__ == '__main__':
    exit(main())
