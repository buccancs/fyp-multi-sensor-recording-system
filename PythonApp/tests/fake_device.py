import base64
import json
import logging
import os
import random
import socket
import sys
import threading
import time
from typing import Dict, Any, Optional, List, Callable
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protocol import create_message, validate_message, get_host, get_port
logger = logging.getLogger(__name__)


class FakeAndroidDevice:

    def __init__(self, device_id: str='fake_device_001', host: Optional[str
        ]=None, port: Optional[int]=None):
        self.device_id = device_id
        self.host = host or get_host()
        self.port = port or get_port()
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.recording = False
        self.session_id: Optional[str] = None
        self.frame_counter = 0
        self.chunk_counter = 0
        self.battery_level = 85.0
        self.storage_available = 1024.0
        self.running = False
        self.message_thread: Optional[threading.Thread] = None
        self.preview_thread: Optional[threading.Thread] = None
        self.on_command_received: Optional[Callable[[Dict[str, Any]], None]
            ] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        logger.info(f'Initialized fake device {device_id}')

    def connect(self, timeout: float=10.0) ->bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            self.message_thread = threading.Thread(target=self.
                _message_handler, daemon=True)
            self.message_thread.start()
            self._send_device_status()
            if self.on_connected:
                self.on_connected()
            logger.info(
                f'Fake device {self.device_id} connected to {self.host}:{self.port}'
                )
            return True
        except Exception as e:
            logger.error(f'Failed to connect fake device: {e}')
            self.connected = False
            return False

    def disconnect(self) ->None:
        self.running = False
        self.recording = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        if self.on_disconnected:
            self.on_disconnected()
        logger.info(f'Fake device {self.device_id} disconnected')

    def _message_handler(self) ->None:
        while self.running and self.connected:
            try:
                length_data = self._recv_exact(4)
                if not length_data:
                    break
                message_length = int.from_bytes(length_data, byteorder='big')
                message_data = self._recv_exact(message_length)
                if not message_data:
                    break
                message = json.loads(message_data.decode('utf-8'))
                if not validate_message(message):
                    logger.warning(f'Received invalid message: {message}')
                    continue
                self._handle_message(message)
            except json.JSONDecodeError as e:
                logger.error(f'Failed to parse message JSON: {e}')
            except Exception as e:
                logger.error(f'Error in message handler: {e}')
                break
        self.disconnect()

    def _recv_exact(self, length: int) ->Optional[bytes]:
        if not self.socket:
            return None
        data = b''
        while len(data) < length:
            try:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                continue
            except Exception:
                return None
        return data

    def _handle_message(self, message: Dict[str, Any]) ->None:
        message_type = message.get('type')
        if self.on_command_received:
            self.on_command_received(message)
        if message_type == 'start_record':
            self._handle_start_record(message)
        elif message_type == 'stop_record':
            self._handle_stop_record(message)
        elif message_type == 'calibration_start':
            self._handle_calibration_start(message)
        else:
            logger.info(f'Received message type: {message_type}')

    def _handle_start_record(self, message: Dict[str, Any]) ->None:
        self.session_id = message.get('session_id')
        self.recording = True
        self.frame_counter = 0
        self.chunk_counter = 0
        ack_msg = create_message('ack', message_id=str(message.get(
            'timestamp', 0)), success=True)
        self._send_message(ack_msg)
        self.preview_thread = threading.Thread(target=self.
            _send_preview_frames, daemon=True)
        self.preview_thread.start()
        threading.Timer(2.0, self._send_file_chunks).start()
        logger.info(f'Started recording session: {self.session_id}')

    def _handle_stop_record(self, message: Dict[str, Any]) ->None:
        self.recording = False
        ack_msg = create_message('ack', message_id=str(message.get(
            'timestamp', 0)), success=True)
        self._send_message(ack_msg)
        logger.info(f'Stopped recording session: {self.session_id}')
        self.session_id = None

    def _handle_calibration_start(self, message: Dict[str, Any]) ->None:
        threading.Timer(1.0, self._send_calibration_result).start()
        logger.info('Started calibration process')

    def _send_preview_frames(self) ->None:
        while self.recording and self.connected:
            try:
                fake_image_data = self._generate_fake_image()
                preview_msg = create_message('preview_frame', frame_id=self
                    .frame_counter, image_data=fake_image_data, width=640,
                    height=480)
                self._send_message(preview_msg)
                self.frame_counter += 1
                time.sleep(0.1)
            except Exception as e:
                logger.error(f'Error sending preview frame: {e}')
                break

    def _send_file_chunks(self) ->None:
        if not self.recording:
            return
        file_id = f'video_{self.session_id}_{int(time.time())}'
        total_chunks = 5
        for chunk_index in range(total_chunks):
            if not self.recording:
                break
            fake_chunk_data = base64.b64encode(b'fake_video_data_chunk_' +
                str(chunk_index).encode()).decode()
            chunk_msg = create_message('file_chunk', file_id=file_id,
                chunk_index=chunk_index, total_chunks=total_chunks,
                chunk_data=fake_chunk_data, chunk_size=len(fake_chunk_data),
                file_type='video')
            self._send_message(chunk_msg)
            time.sleep(0.5)
        logger.info(f'Completed sending file chunks for {file_id}')

    def _send_calibration_result(self) ->None:
        result_msg = create_message('calibration_result', success=True,
            rms_error=0.8, camera_matrix=[[800, 0, 320], [0, 800, 240], [0,
            0, 1]], distortion_coefficients=[0.1, -0.2, 0.0, 0.0, 0.0])
        self._send_message(result_msg)
        logger.info('Sent calibration result')

    def _send_device_status(self) ->None:
        status = 'recording' if self.recording else 'idle'
        status_msg = create_message('device_status', device_id=self.
            device_id, status=status, battery_level=self.battery_level,
            storage_available=self.storage_available)
        self._send_message(status_msg)

    def _generate_fake_image(self) ->str:
        fake_data = b'\xff\xd8\xff\xe0' + b'fake_jpeg_data_' + str(self.
            frame_counter).encode() + b'\xff\xd9'
        return base64.b64encode(fake_data).decode()

    def _send_message(self, message: Dict[str, Any]) ->bool:
        if not self.connected or not self.socket:
            return False
        try:
            if not validate_message(message):
                logger.error(f'Attempted to send invalid message: {message}')
                return False
            message_data = json.dumps(message).encode('utf-8')
            message_length = len(message_data)
            length_bytes = message_length.to_bytes(4, byteorder='big')
            self.socket.sendall(length_bytes + message_data)
            return True
        except Exception as e:
            logger.error(f'Failed to send message: {e}')
            return False

    def simulate_battery_drain(self) ->None:
        if self.battery_level > 10:
            self.battery_level -= random.uniform(0.1, 0.5)
            self._send_device_status()

    def simulate_storage_usage(self) ->None:
        if self.recording and self.storage_available > 100:
            self.storage_available -= random.uniform(1, 5)
            self._send_device_status()


class FakeDeviceManager:

    def __init__(self):
        self.devices: List[FakeAndroidDevice] = []
        self.running = False

    def add_device(self, device_id: str, host: Optional[str]=None, port:
        Optional[int]=None) ->FakeAndroidDevice:
        device = FakeAndroidDevice(device_id, host, port)
        self.devices.append(device)
        return device

    def connect_all(self) ->int:
        connected_count = 0
        for device in self.devices:
            if device.connect():
                connected_count += 1
        return connected_count

    def disconnect_all(self) ->None:
        for device in self.devices:
            device.disconnect()

    def start_recording_all(self, session_id: str) ->None:
        start_msg = create_message('start_record', session_id=session_id)
        for device in self.devices:
            if device.connected:
                device._send_message(start_msg)

    def stop_recording_all(self, session_id: str) ->None:
        stop_msg = create_message('stop_record', session_id=session_id)
        for device in self.devices:
            if device.connected:
                device._send_message(stop_msg)


def create_test_device(device_id: str='test_device') ->FakeAndroidDevice:
    return FakeAndroidDevice(device_id)


def run_basic_test() ->bool:
    device = create_test_device()
    try:
        if not device.connect(timeout=5.0):
            logger.error('Failed to connect to server')
            return False
        time.sleep(2.0)
        device.disconnect()
        logger.info('Basic fake device test completed successfully')
        return True
    except Exception as e:
        logger.error(f'Basic test failed: {e}')
        return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    success = run_basic_test()
    exit(0 if success else 1)
