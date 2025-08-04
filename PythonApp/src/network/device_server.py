import base64
import json
import os
import socket
import struct
import threading
import time
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, List, Optional, Any
from utils.logging_config import get_logger
logger = get_logger(__name__)


class RemoteDevice:

    def __init__(self, device_id: str, capabilities: List[str],
        client_socket: socket.socket):
        self.device_id = device_id
        self.capabilities = capabilities
        self.client_socket = client_socket
        self.connected = True
        self.last_seen = time.time()
        self.status = {'battery': None, 'temperature': None, 'storage':
            None, 'recording': False, 'last_update': time.time()}
        self.connection_stats = {'connected_at': time.time(),
            'messages_received': 0, 'messages_sent': 0, 'last_activity':
            time.time()}
        self.has_camera = 'camera' in capabilities
        self.has_thermal = 'thermal' in capabilities
        self.has_imu = 'imu' in capabilities
        self.has_gsr = 'gsr' in capabilities
        logger.info(
            f'RemoteDevice created: {device_id} with capabilities: {capabilities}'
            )

    def update_status(self, status_data: Dict[str, Any]):
        self.status.update(status_data)
        self.status['last_update'] = time.time()
        self.last_seen = time.time()
        self.connection_stats['last_activity'] = time.time()
        logger.debug(f'Device {self.device_id} status updated: {status_data}')

    def increment_message_count(self, message_type: str='received'):
        if message_type == 'received':
            self.connection_stats['messages_received'] += 1
        elif message_type == 'sent':
            self.connection_stats['messages_sent'] += 1
        self.connection_stats['last_activity'] = time.time()
        self.last_seen = time.time()

    def is_alive(self, timeout_seconds: int=30) ->bool:
        return time.time() - self.last_seen < timeout_seconds

    def get_connection_duration(self) ->float:
        return time.time() - self.connection_stats['connected_at']

    def get_device_info(self) ->Dict[str, Any]:
        return {'device_id': self.device_id, 'capabilities': self.
            capabilities, 'connected': self.connected, 'status': self.
            status.copy(), 'connection_stats': self.connection_stats.copy(),
            'last_seen': self.last_seen, 'connection_duration': self.
            get_connection_duration(), 'is_alive': self.is_alive()}

    def disconnect(self):
        self.connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        logger.info(
            f'RemoteDevice {self.device_id} disconnected after {self.get_connection_duration():.1f} seconds'
            )


class JsonSocketServer(QThread):
    device_connected = pyqtSignal(str, list)
    device_disconnected = pyqtSignal(str)
    status_received = pyqtSignal(str, dict)
    ack_received = pyqtSignal(str, str, bool, str)
    preview_frame_received = pyqtSignal(str, str, str)
    sensor_data_received = pyqtSignal(str, dict)
    notification_received = pyqtSignal(str, str, dict)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, host: str='0.0.0.0', port: int=9000,
        use_newline_protocol: bool=False, session_manager=None):
        super().__init__()
        self.host = host
        self.port = port
        self.use_newline_protocol = use_newline_protocol
        self.session_manager = session_manager
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.devices: Dict[str, RemoteDevice] = {}
        self.clients: Dict[str, socket.socket] = {}
        self.client_threads: List[threading.Thread] = []
        protocol_type = ('newline-delimited' if use_newline_protocol else
            'length-prefixed')
        logger.info(
            f'JsonSocketServer initialized for {host}:{port} using {protocol_type} JSON protocol'
            )

    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.
                SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.
                SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            logger.info(
                f'JSON Socket server started on {self.host}:{self.port}')
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(target=self.
                        handle_json_client, args=(client_socket, address),
                        daemon=True)
                    client_thread.start()
                    self.client_threads.append(client_thread)
                except socket.error as e:
                    if self.running:
                        logger.error(f'JSON socket accept error: {e}')
                        self.error_occurred.emit('server',
                            f'Accept error: {str(e)}')
        except Exception as e:
            logger.error(f'JSON socket server error: {e}')
            self.error_occurred.emit('server', f'Server error: {str(e)}')
        finally:
            self.cleanup()

    def handle_json_client(self, client_socket: socket.socket, address: tuple):
        client_addr = f'{address[0]}:{address[1]}'
        device_id = None
        logger.info(f'JSON client connected: {client_addr}')
        try:
            while self.running:
                length_data = self.recv_exact(client_socket, 4)
                if not length_data:
                    break
                message_length = struct.unpack('>I', length_data)[0]
                if message_length <= 0 or message_length > 10 * 1024 * 1024:
                    logger.error(f'Invalid message length: {message_length}')
                    self.error_occurred.emit(device_id or client_addr,
                        f'Invalid message length: {message_length}')
                    break
                json_data = self.recv_exact(client_socket, message_length)
                if not json_data:
                    break
                try:
                    message = json.loads(json_data.decode('utf-8'))
                    device_id = self.process_json_message(client_socket,
                        client_addr, message)
                except json.JSONDecodeError as e:
                    logger.error(f'JSON decode error from {client_addr}: {e}')
                    self.error_occurred.emit(device_id or client_addr,
                        f'JSON decode error: {str(e)}')
        except Exception as e:
            logger.error(f'JSON client handling error for {client_addr}: {e}')
            self.error_occurred.emit(device_id or client_addr,
                f'Client handling error: {str(e)}')
        finally:
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                device.disconnect()
                del self.devices[device_id]
                if device_id in self.clients:
                    del self.clients[device_id]
                self.device_disconnected.emit(device_id)
                logger.info(f'Device {device_id} disconnected')
            else:
                client_socket.close()
            logger.info(f'JSON client disconnected: {client_addr}')

    def recv_exact(self, sock: socket.socket, length: int) ->Optional[bytes]:
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def process_json_message(self, client_socket: socket.socket,
        client_addr: str, message: Dict[str, Any]) ->Optional[str]:
        message_type = message.get('type', 'unknown')
        logger.debug(
            f'Received JSON message from {client_addr}: {message_type}')
        if message_type == 'hello':
            device_id = message.get('device_id', client_addr)
            capabilities = message.get('capabilities', [])
            remote_device = RemoteDevice(device_id, capabilities, client_socket
                )
            self.devices[device_id] = remote_device
            self.clients[device_id] = client_socket
            self.device_connected.emit(device_id, capabilities)
            logger.info(
                f'Device registered: {device_id} with capabilities: {capabilities}'
                )
            return device_id
        elif message_type == 'status':
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                status_data = {'battery': message.get('battery'), 'storage':
                    message.get('storage'), 'temperature': message.get(
                    'temperature'), 'recording': message.get('recording', 
                    False), 'connected': message.get('connected', True),
                    'timestamp': message.get('timestamp')}
                device.update_status(status_data)
                device.increment_message_count('received')
                self.status_received.emit(device_id, status_data)
                logger.debug(f'Status update from {device_id}: {status_data}')
        elif message_type == 'preview_frame':
            device_id = self.find_device_id(client_socket)
            if device_id:
                frame_type = message.get('frame_type', 'rgb')
                frame_data = message.get('frame_data', '')
                if frame_data:
                    self.preview_frame_received.emit(device_id, frame_type,
                        frame_data)
                    logger.debug(
                        f'Preview frame received from {device_id}: {frame_type}'
                        )
                else:
                    logger.warning(f'Empty frame data from {device_id}')
        elif message_type == 'sensor_data':
            device_id = self.find_device_id(client_socket)
            if device_id:
                sensor_data = {'gsr': message.get('gsr'), 'ppg': message.
                    get('ppg'), 'accelerometer': message.get(
                    'accelerometer'), 'gyroscope': message.get('gyroscope'),
                    'magnetometer': message.get('magnetometer'),
                    'timestamp': message.get('timestamp')}
                self.sensor_data_received.emit(device_id, sensor_data)
                logger.debug(f'Sensor data from {device_id}')
        elif message_type == 'notification':
            device_id = self.find_device_id(client_socket)
            if device_id:
                event_type = message.get('event_type', 'unknown')
                event_data = message.get('event_data', {})
                self.notification_received.emit(device_id, event_type,
                    event_data)
                logger.info(f'Notification from {device_id}: {event_type}')
        elif message_type == 'ack':
            device_id = self.find_device_id(client_socket)
            if device_id:
                cmd = message.get('cmd', '')
                status = message.get('status', 'unknown')
                success = status == 'ok'
                error_message = message.get('message', '')
                self.ack_received.emit(device_id, cmd, success, error_message)
                logger.debug(f'ACK from {device_id} for {cmd}: {status}')
        elif message_type == 'file_info':
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                filename = message.get('name', 'unknown')
                filesize = message.get('size', 0)
                device.file_transfer_state = {'filename': filename,
                    'expected_size': filesize, 'received_bytes': 0,
                    'file_handle': None, 'chunks_received': 0}
                session_dir = self.get_session_directory()
                if session_dir:
                    filepath = os.path.join(session_dir,
                        f'{device_id}_{filename}')
                    try:
                        device.file_transfer_state['file_handle'] = open(
                            filepath, 'wb')
                        logger.info(
                            f'Started receiving file {filename} from {device_id} ({filesize} bytes)'
                            )
                    except Exception as e:
                        logger.error(f'Failed to create file {filepath}: {e}')
                        device.file_transfer_state = None
                else:
                    logger.error(
                        f'No session directory available for file transfer')
                    device.file_transfer_state = None
        elif message_type == 'file_chunk':
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                if hasattr(device, 'file_transfer_state'
                    ) and device.file_transfer_state:
                    seq = message.get('seq', 0)
                    base64_data = message.get('data', '')
                    try:
                        chunk_data = base64.b64decode(base64_data)
                        if device.file_transfer_state['file_handle']:
                            device.file_transfer_state['file_handle'].write(
                                chunk_data)
                            device.file_transfer_state['received_bytes'
                                ] += len(chunk_data)
                            device.file_transfer_state['chunks_received'] += 1
                            if seq % 100 == 0:
                                progress = device.file_transfer_state[
                                    'received_bytes'
                                    ] * 100.0 / device.file_transfer_state[
                                    'expected_size']
                                logger.debug(
                                    f"File transfer progress from {device_id}: {progress:.1f}% ({device.file_transfer_state['received_bytes']}/{device.file_transfer_state['expected_size']} bytes)"
                                    )
                    except Exception as e:
                        logger.error(
                            f'Error processing file chunk from {device_id}: {e}'
                            )
                else:
                    logger.warning(
                        f'Received file chunk from {device_id} without file_info'
                        )
        elif message_type == 'file_end':
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                if hasattr(device, 'file_transfer_state'
                    ) and device.file_transfer_state:
                    filename = message.get('name', 'unknown')
                    try:
                        if device.file_transfer_state['file_handle']:
                            device.file_transfer_state['file_handle'].close()
                        expected_size = device.file_transfer_state[
                            'expected_size']
                        received_size = device.file_transfer_state[
                            'received_bytes']
                        chunks_received = device.file_transfer_state[
                            'chunks_received']
                        if received_size == expected_size:
                            logger.info(
                                f'File transfer completed successfully: {filename} from {device_id} ({received_size} bytes, {chunks_received} chunks)'
                                )
                            ack_message = {'type': 'file_received', 'name':
                                filename, 'status': 'ok'}
                            self.send_command(device_id, ack_message)
                        else:
                            logger.error(
                                f'File transfer size mismatch: expected {expected_size}, received {received_size} bytes'
                                )
                            ack_message = {'type': 'file_received', 'name':
                                filename, 'status': 'error'}
                            self.send_command(device_id, ack_message)
                        device.file_transfer_state = None
                    except Exception as e:
                        logger.error(
                            f'Error finalizing file transfer from {device_id}: {e}'
                            )
                        device.file_transfer_state = None
                else:
                    logger.warning(
                        f'Received file_end from {device_id} without active transfer'
                        )
        else:
            device_id = self.find_device_id(client_socket)
            logger.warning(
                f"Unknown message type '{message_type}' from {device_id or client_addr}"
                )
        return self.find_device_id(client_socket)

    def find_device_id(self, client_socket: socket.socket) ->Optional[str]:
        for device_id, device in self.devices.items():
            if device.client_socket == client_socket:
                return device_id
        return None

    def send_command(self, device_id: str, command_dict: Dict[str, Any]
        ) ->bool:
        if device_id not in self.devices:
            logger.warning(f'Device {device_id} not connected')
            return False
        try:
            device = self.devices[device_id]
            json_data = json.dumps(command_dict).encode('utf-8')
            length_header = struct.pack('>I', len(json_data))
            device.client_socket.send(length_header + json_data)
            device.increment_message_count('sent')
            logger.debug(
                f"Sent command to {device_id}: {command_dict.get('type', 'unknown')}"
                )
            return True
        except Exception as e:
            logger.error(f'Error sending command to {device_id}: {e}')
            self.error_occurred.emit(device_id, f'Command send error: {str(e)}'
                )
            return False

    def broadcast_command(self, command_dict: Dict[str, Any]) ->int:
        success_count = 0
        for device_id in list(self.devices.keys()):
            if self.send_command(device_id, command_dict):
                success_count += 1
        logger.info(
            f'Broadcast command to {success_count}/{len(self.devices)} devices'
            )
        return success_count

    def get_connected_devices(self) ->List[str]:
        return list(self.clients.keys())

    def get_device_count(self) ->int:
        return len(self.clients)

    def is_device_connected(self, device_id: str) ->bool:
        return device_id in self.clients

    def stop_server(self):
        logger.info('Stopping JSON socket server...')
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        for device_id, client_socket in list(self.clients.items()):
            try:
                client_socket.close()
                self.device_disconnected.emit(device_id)
            except:
                pass
        self.clients.clear()
        logger.info('JSON socket server stopped')

    def get_session_directory(self) ->Optional[str]:
        try:
            if self.session_manager:
                session_folder = self.session_manager.get_session_folder()
                if session_folder:
                    session_dir = str(session_folder)
                    logger.debug(
                        f'Using SessionManager session directory: {session_dir}'
                        )
                    return session_dir
                else:
                    logger.warning(
                        'SessionManager available but no active session found')
            base_dir = os.path.join(os.getcwd(), 'sessions')
            os.makedirs(base_dir, exist_ok=True)
            import datetime
            session_name = datetime.datetime.now().strftime(
                'session_%Y%m%d_%H%M%S')
            session_dir = os.path.join(base_dir, session_name)
            os.makedirs(session_dir, exist_ok=True)
            logger.debug(f'Fallback session directory: {session_dir}')
            return session_dir
        except Exception as e:
            logger.error(f'Failed to get session directory: {e}')
            return None

    def request_file_from_device(self, device_id: str, filepath: str,
        filetype: str=None) ->bool:
        if device_id not in self.devices:
            logger.warning(f'Device {device_id} not connected')
            return False
        try:
            send_file_command = {'type': 'send_file', 'filepath': filepath,
                'filetype': filetype}
            success = self.send_command(device_id, send_file_command)
            if success:
                logger.info(
                    f'Requested file {filepath} from device {device_id}')
            else:
                logger.error(
                    f'Failed to request file {filepath} from device {device_id}'
                    )
            return success
        except Exception as e:
            logger.error(f'Error requesting file from device {device_id}: {e}')
            return False

    def request_all_session_files(self, session_id: str) ->int:
        success_count = 0
        for device_id, device in self.devices.items():
            try:
                expected_files = self.get_expected_files_for_device(device_id,
                    session_id, device.capabilities)
                for filepath in expected_files:
                    if self.request_file_from_device(device_id, filepath):
                        success_count += 1
                        import time
                        time.sleep(0.1)
            except Exception as e:
                logger.error(
                    f'Error requesting files from device {device_id}: {e}')
        logger.info(
            f'Requested session files from {success_count} device file combinations'
            )
        return success_count

    def get_expected_files_for_device(self, device_id: str, session_id: str,
        capabilities: List[str]) ->List[str]:
        expected_files = []
        base_path = (
            f'/storage/emulated/0/MultiSensorRecording/sessions/{session_id}')
        if 'rgb_video' in capabilities or 'camera' in capabilities:
            expected_files.append(
                f'{base_path}/{session_id}_{device_id}_rgb.mp4')
        if 'thermal' in capabilities:
            expected_files.append(
                f'{base_path}/{session_id}_{device_id}_thermal.mp4')
        if 'shimmer' in capabilities:
            expected_files.append(
                f'{base_path}/{session_id}_{device_id}_sensors.csv')
        logger.debug(f'Expected files for {device_id}: {expected_files}')
        return expected_files

    def cleanup(self):
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        for thread in self.client_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        self.client_threads.clear()
        logger.info('JSON socket server cleanup completed')


def decode_base64_image(base64_data: str) ->Optional[bytes]:
    try:
        if base64_data.startswith('data:image/'):
            base64_data = base64_data.split(',', 1)[1]
        return base64.b64decode(base64_data)
    except Exception as e:
        logger.error(f'Error decoding base64 image: {e}')
        return None


def create_command_message(command_type: str, **kwargs) ->Dict[str, Any]:
    import time
    command = {'type': 'command', 'command': command_type, 'timestamp':
        time.time(), **kwargs}
    return command
