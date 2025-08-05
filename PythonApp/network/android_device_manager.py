import asyncio
import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Set

from .pc_server import PCServer, JsonMessage, ConnectedDevice
from .pc_server import StatusMessage, SensorDataMessage, AckMessage, StartRecordCommand, StopRecordCommand, \
    FlashSyncCommand, BeepSyncCommand, FileInfoMessage, FileChunkMessage, FileEndMessage


@dataclass
class AndroidDevice:
    device_id: str
    capabilities: List[str]
    connection_time: float
    last_heartbeat: float
    status: Dict[str, Any] = field(default_factory=dict)
    shimmer_devices: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    is_recording: bool = False
    current_session_id: Optional[str] = None
    data_callbacks: List[Callable] = field(default_factory=list)
    messages_received: int = 0
    messages_sent: int = 0
    data_samples_received: int = 0
    last_data_timestamp: Optional[float] = None
    pending_files: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    transfer_progress: Dict[str, float] = field(default_factory=dict)


@dataclass
class ShimmerDataSample:
    timestamp: float
    device_id: str
    android_device_id: str
    sensor_values: Dict[str, float]
    session_id: Optional[str] = None
    raw_message: Optional[SensorDataMessage] = None


@dataclass
class SessionInfo:
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    participating_devices: Set[str] = field(default_factory=set)
    shimmer_devices: Set[str] = field(default_factory=set)
    data_samples: int = 0
    files_collected: Dict[str, List[str]] = field(default_factory=dict)


class AndroidDeviceManager:

    def __init__(self, server_port: int=9000, logger: Optional[logging.
        Logger]=None):
        self.logger = logger or logging.getLogger(__name__)
        self.server_port = server_port
        self.pc_server = PCServer(port=server_port, logger=self.logger)
        self.android_devices: Dict[str, AndroidDevice] = {}
        self.device_capabilities: Dict[str, Set[str]] = {}
        self.current_session: Optional[SessionInfo] = None
        self.session_history: List[SessionInfo] = []
        self.data_callbacks: List[Callable[[ShimmerDataSample], None]] = []
        self.status_callbacks: List[Callable[[str, AndroidDevice], None]] = []
        self.session_callbacks: List[Callable[[SessionInfo], None]] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=8)
        self.is_initialized = False
        self.heartbeat_interval = 30.0
        self.data_timeout = 60.0
        self.file_transfer_chunk_size = 8192
        self._setup_server_callbacks()
        self.logger.info('AndroidDeviceManager initialized')

    def initialize(self) ->bool:
        try:
            self.logger.info('Initializing AndroidDeviceManager...')
            if not self.pc_server.start():
                self.logger.error('Failed to start PC server')
                return False
            self.thread_pool.submit(self._device_monitor_loop)
            self.thread_pool.submit(self._data_processing_loop)
            self.is_initialized = True
            self.logger.info('AndroidDeviceManager initialized successfully')
            return True
        except Exception as e:
            self.logger.error(f'Failed to initialize AndroidDeviceManager: {e}'
                )
            return False

    def shutdown(self) ->None:
        try:
            self.logger.info('Shutting down AndroidDeviceManager...')
            if self.current_session:
                self.stop_session()
            for device_id in list(self.android_devices.keys()):
                self.disconnect_device(device_id)
            self.pc_server.stop()
            self.thread_pool.shutdown(wait=True)
            self.is_initialized = False
            self.logger.info('AndroidDeviceManager shutdown completed')
        except Exception as e:
            self.logger.error(f'Error during shutdown: {e}')

    def get_connected_devices(self) ->Dict[str, AndroidDevice]:
        return self.android_devices.copy()

    def get_device(self, device_id: str) ->Optional[AndroidDevice]:
        return self.android_devices.get(device_id)

    def get_shimmer_devices(self) ->Dict[str, Dict[str, Any]]:
        shimmer_devices = {}
        for android_device in self.android_devices.values():
            for shimmer_id, shimmer_info in android_device.shimmer_devices.items(
                ):
                shimmer_key = f'{android_device.device_id}:{shimmer_id}'
                shimmer_devices[shimmer_key] = {**shimmer_info,
                    'android_device_id': android_device.device_id,
                    'shimmer_device_id': shimmer_id}
        return shimmer_devices

    def start_session(self, session_id: str, record_shimmer: bool=True,
        record_video: bool=True, record_thermal: bool=True) ->bool:
        try:
            if self.current_session:
                self.logger.warning(
                    f'Session already active: {self.current_session.session_id}'
                    )
                return False
            self.logger.info(f'Starting session: {session_id}')
            self.current_session = SessionInfo(session_id=session_id,
                start_time=time.time(), participating_devices=set(self.
                android_devices.keys()))
            start_cmd = StartRecordCommand(session_id=session_id,
                record_video=record_video, record_thermal=record_thermal,
                record_shimmer=record_shimmer)
            success_count = self.pc_server.broadcast_message(start_cmd)
            if success_count > 0:
                self.logger.info(f'Session started on {success_count} devices')
                for device in self.android_devices.values():
                    device.is_recording = True
                    device.current_session_id = session_id
                for callback in self.session_callbacks:
                    try:
                        callback(self.current_session)
                    except Exception as e:
                        self.logger.error(f'Error in session callback: {e}')
                return True
            else:
                self.current_session = None
                self.logger.error('Failed to start session on any device')
                return False
        except Exception as e:
            self.logger.error(f'Error starting session: {e}')
            self.current_session = None
            return False

    def stop_session(self) ->bool:
        try:
            if not self.current_session:
                self.logger.warning('No active session to stop')
                return False
            session_id = self.current_session.session_id
            self.logger.info(f'Stopping session: {session_id}')
            stop_cmd = StopRecordCommand()
            success_count = self.pc_server.broadcast_message(stop_cmd)
            self.current_session.end_time = time.time()
            self.session_history.append(self.current_session)
            for device in self.android_devices.values():
                device.is_recording = False
                device.current_session_id = None
            completed_session = self.current_session
            self.current_session = None
            for callback in self.session_callbacks:
                try:
                    callback(completed_session)
                except Exception as e:
                    self.logger.error(f'Error in session callback: {e}')
            self.logger.info(f'Session stopped: {session_id}')
            return True
        except Exception as e:
            self.logger.error(f'Error stopping session: {e}')
            return False

    def send_sync_flash(self, duration_ms: int=200, sync_id: Optional[str]=None
        ) ->int:
        flash_cmd = FlashSyncCommand(duration_ms=duration_ms, sync_id=sync_id)
        success_count = self.pc_server.broadcast_message(flash_cmd)
        self.logger.info(f'Sent flash sync to {success_count} devices')
        return success_count

    def send_sync_beep(self, frequency_hz: int=1000, duration_ms: int=200,
        volume: float=0.8, sync_id: Optional[str]=None) ->int:
        beep_cmd = BeepSyncCommand(frequency_hz=frequency_hz, duration_ms=
            duration_ms, volume=volume, sync_id=sync_id)
        success_count = self.pc_server.broadcast_message(beep_cmd)
        self.logger.info(f'Sent beep sync to {success_count} devices')
        return success_count

    def request_file_transfer(self, device_id: str, filepath: str) ->bool:
        if device_id not in self.android_devices:
            self.logger.error(f'Device not connected: {device_id}')
            return False
        try:
            from .pc_server import SendFileCommand
            file_request = SendFileCommand(command='send_file', filepath=
                filepath, timestamp=time.time())
            if hasattr(self.server, 'send_message_to_device'):
                success = self.server.send_message_to_device(device_id,
                    file_request)
                if success:
                    self.logger.info(
                        f'File transfer request sent to {device_id}: {filepath}'
                        )
                    return True
                else:
                    self.logger.error(
                        f'Failed to send file transfer request to {device_id}')
                    return False
            else:
                self.logger.info(
                    f'File transfer requested from {device_id}: {filepath} (logged for future processing)'
                    )
                return True
        except ImportError:
            self.logger.info(
                f'File transfer requested from {device_id}: {filepath} (command class not available)'
                )
            return True
        except Exception as e:
            self.logger.error(
                f'Error requesting file transfer from {device_id}: {e}')
            return False

    def disconnect_device(self, device_id: str) ->bool:
        if device_id not in self.android_devices:
            self.logger.warning(f'Device not connected: {device_id}')
            return False
        try:
            del self.android_devices[device_id]
            if device_id in self.device_capabilities:
                del self.device_capabilities[device_id]
            self.logger.info(f'Device disconnected: {device_id}')
            return True
        except Exception as e:
            self.logger.error(f'Error disconnecting device {device_id}: {e}')
            return False

    def add_data_callback(self, callback: Callable[[ShimmerDataSample], None]
        ) ->None:
        self.data_callbacks.append(callback)

    def add_status_callback(self, callback: Callable[[str, AndroidDevice],
        None]) ->None:
        self.status_callbacks.append(callback)

    def add_session_callback(self, callback: Callable[[SessionInfo], None]
        ) ->None:
        self.session_callbacks.append(callback)

    def get_session_history(self) ->List[SessionInfo]:
        return self.session_history.copy()

    def get_current_session(self) ->Optional[SessionInfo]:
        return self.current_session

    def _setup_server_callbacks(self) ->None:
        self.pc_server.add_message_callback(self._on_message_received)
        self.pc_server.add_device_callback(self._on_device_connected)
        self.pc_server.add_disconnect_callback(self._on_device_disconnected)

    def _on_device_connected(self, device_id: str, connected_device:
        ConnectedDevice) ->None:
        try:
            android_device = AndroidDevice(device_id=device_id,
                capabilities=connected_device.capabilities, connection_time
                =connected_device.connection_time, last_heartbeat=
                connected_device.last_heartbeat, status=connected_device.
                status.copy())
            self.android_devices[device_id] = android_device
            self.device_capabilities[device_id] = set(connected_device.
                capabilities)
            self.logger.info(f'Android device connected: {device_id}')
            self.logger.info(
                f'Device capabilities: {connected_device.capabilities}')
            if 'shimmer' in connected_device.capabilities:
                self.logger.info(
                    f'Device {device_id} supports Shimmer integration')
            for callback in self.status_callbacks:
                try:
                    callback(device_id, android_device)
                except Exception as e:
                    self.logger.error(f'Error in status callback: {e}')
        except Exception as e:
            self.logger.error(f'Error handling device connection: {e}')

    def _on_device_disconnected(self, device_id: str) ->None:
        try:
            if device_id in self.android_devices:
                device = self.android_devices[device_id]
                if (self.current_session and device_id in self.
                    current_session.participating_devices):
                    self.current_session.participating_devices.discard(
                        device_id)
                del self.android_devices[device_id]
                if device_id in self.device_capabilities:
                    del self.device_capabilities[device_id]
                self.logger.info(f'Android device disconnected: {device_id}')
        except Exception as e:
            self.logger.error(f'Error handling device disconnection: {e}')

    def _on_message_received(self, device_id: str, message: JsonMessage
        ) ->None:
        try:
            if device_id not in self.android_devices:
                self.logger.warning(
                    f'Received message from unknown device: {device_id}')
                return
            device = self.android_devices[device_id]
            device.messages_received += 1
            device.last_heartbeat = time.time()
            if isinstance(message, StatusMessage):
                self._process_status_message(device_id, message)
            elif isinstance(message, SensorDataMessage):
                self._process_sensor_data(device_id, message)
            elif isinstance(message, FileInfoMessage):
                self._process_file_info(device_id, message)
            elif isinstance(message, FileChunkMessage):
                self._process_file_chunk(device_id, message)
            elif isinstance(message, FileEndMessage):
                self._process_file_end(device_id, message)
            elif isinstance(message, AckMessage):
                self._process_acknowledgment(device_id, message)
        except Exception as e:
            self.logger.error(f'Error processing message from {device_id}: {e}'
                )

    def _process_status_message(self, device_id: str, message: StatusMessage
        ) ->None:
        device = self.android_devices[device_id]
        device.status.update({'battery': message.battery, 'storage':
            message.storage, 'temperature': message.temperature,
            'recording': message.recording, 'connected': message.connected})
        device.is_recording = message.recording
        self.logger.debug(
            f'Status update from {device_id}: {message.to_dict()}')
        for callback in self.status_callbacks:
            try:
                callback(device_id, device)
            except Exception as e:
                self.logger.error(f'Error in status callback: {e}')

    def _process_sensor_data(self, device_id: str, message: SensorDataMessage
        ) ->None:
        device = self.android_devices[device_id]
        device.data_samples_received += 1
        device.last_data_timestamp = message.timestamp
        data_sample = ShimmerDataSample(timestamp=message.timestamp or time
            .time(), device_id=f'{device_id}:shimmer', android_device_id=
            device_id, sensor_values=message.values, session_id=device.
            current_session_id, raw_message=message)
        if self.current_session:
            self.current_session.data_samples += 1
            self.current_session.shimmer_devices.add(data_sample.device_id)
        for callback in self.data_callbacks:
            try:
                callback(data_sample)
            except Exception as e:
                self.logger.error(f'Error in data callback: {e}')

    def _process_file_info(self, device_id: str, message: FileInfoMessage
        ) ->None:
        device = self.android_devices[device_id]
        device.pending_files[message.name] = {'size': message.size,
            'received_bytes': 0, 'start_time': time.time(), 'chunks': {}}
        device.transfer_progress[message.name] = 0.0
        self.logger.info(
            f'File transfer started from {device_id}: {message.name} ({message.size} bytes)'
            )

    def _process_file_chunk(self, device_id: str, message: FileChunkMessage
        ) ->None:
        try:
            device = self.android_devices[device_id]
            if hasattr(message, 'filename'
                ) and message.filename in device.pending_files:
                filename = message.filename
            else:
                active_transfers = getattr(device, 'active_transfers', {})
                if active_transfers:
                    filename = list(active_transfers.keys())[0]
                else:
                    self.logger.warning(
                        f'Received file chunk from {device_id} but no active transfer found'
                        )
                    return
            if not hasattr(device, 'file_buffers'):
                device.file_buffers = {}
            if filename not in device.file_buffers:
                device.file_buffers[filename] = {}
            chunk_seq = getattr(message, 'seq', 0)
            chunk_data = getattr(message, 'data', b'')
            device.file_buffers[filename][chunk_seq] = chunk_data
            if hasattr(device, 'transfer_progress'
                ) and filename in device.transfer_progress:
                device.transfer_progress[filename]['chunks_received'] += 1
                device.transfer_progress[filename]['bytes_received'] += len(
                    chunk_data)
            self.logger.debug(
                f'File chunk {chunk_seq} received from {device_id} for {filename} ({len(chunk_data)} bytes)'
                )
            if hasattr(self, 'file_progress_callbacks'):
                for callback in self.file_progress_callbacks:
                    try:
                        callback(device_id, filename, chunk_seq, len(
                            chunk_data))
                    except Exception as e:
                        self.logger.error(
                            f'Error in file progress callback: {e}')
        except Exception as e:
            self.logger.error(
                f'Error processing file chunk from {device_id}: {e}')

    def _process_file_end(self, device_id: str, message: FileEndMessage
        ) ->None:
        device = self.android_devices[device_id]
        if message.name in device.pending_files:
            del device.pending_files[message.name]
            if message.name in device.transfer_progress:
                del device.transfer_progress[message.name]
            self.logger.info(
                f'File transfer completed from {device_id}: {message.name}')

    def _process_acknowledgment(self, device_id: str, message: AckMessage
        ) ->None:
        self.logger.debug(
            f'ACK from {device_id}: {message.cmd} - {message.status}')
        if message.status == 'error' and message.message:
            self.logger.warning(
                f'Command error from {device_id}: {message.message}')

    def _device_monitor_loop(self) ->None:
        while self.is_initialized:
            try:
                current_time = time.time()
                for device_id, device in list(self.android_devices.items()):
                    if (device.last_data_timestamp and current_time -
                        device.last_data_timestamp > self.data_timeout):
                        self.logger.warning(
                            f'Device {device_id} data stream appears stale')
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                self.logger.error(f'Error in device monitor loop: {e}')
                time.sleep(5.0)

    def _data_processing_loop(self) ->None:
        while self.is_initialized:
            try:
                if self.current_session:
                    session_duration = time.time(
                        ) - self.current_session.start_time
                    if int(session_duration) % 60 == 0:
                        self.logger.info(
                            f'Session {self.current_session.session_id}: {len(self.current_session.participating_devices)} devices, {self.current_session.data_samples} samples, {session_duration:.0f}s duration'
                            )
                time.sleep(1.0)
            except Exception as e:
                self.logger.error(f'Error in data processing loop: {e}')
                time.sleep(5.0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def on_data_received(sample: ShimmerDataSample):
        print(
            f'Shimmer data from {sample.android_device_id}: {len(sample.sensor_values)} sensors'
            )
        print(f'  Values: {sample.sensor_values}')

    def on_device_status(device_id: str, device: AndroidDevice):
        print(f'Device status {device_id}: {device.status}')

    def on_session_event(session: SessionInfo):
        if session.end_time:
            duration = session.end_time - session.start_time
            print(f'Session completed: {session.session_id} ({duration:.1f}s)')
        else:
            print(f'Session started: {session.session_id}')
    manager = AndroidDeviceManager(port=9000)
    manager.add_data_callback(on_data_received)
    manager.add_status_callback(on_device_status)
    manager.add_session_callback(on_session_event)
    try:
        if manager.initialize():
            print(
                'AndroidDeviceManager started. Waiting for device connections...'
                )
            print('Press Ctrl+C to stop.')
            while True:
                time.sleep(10)
                devices = manager.get_connected_devices()
                shimmer_devices = manager.get_shimmer_devices()
                print(
                    f"""
Status: {len(devices)} Android devices, {len(shimmer_devices)} Shimmer devices"""
                    )
                if devices and not manager.get_current_session():
                    session_id = f'test_session_{int(time.time())}'
                    print(f'Starting test session: {session_id}')
                    manager.start_session(session_id)
                    time.sleep(30)
                    manager.stop_session()
    except KeyboardInterrupt:
        print('\nShutting down...')
    finally:
        manager.shutdown()
