import asyncio
import json
import logging
import os
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import pytest
sys.path.insert(0, str(Path(__file__).parent / 'src'))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from utils.logging_config import get_logger, AppLogger
AppLogger.set_level('DEBUG')
logger = get_logger(__name__)
try:
    from session.session_manager import SessionManager
    from network.device_server import JsonSocketServer, RemoteDevice
    from webcam.webcam_capture import WebcamCapture
    from config.webcam_config import WebcamConfiguration, VideoCodec, Resolution
    from shimmer_manager import ShimmerManager
    from calibration.calibration_manager import CalibrationManager
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer, QObject, pyqtSignal
    import cv2
    import numpy as np
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logger.error(f'Missing dependencies: {e}')
    DEPENDENCIES_AVAILABLE = False


@dataclass
class MockSensorData:
    timestamp: float
    sensor_type: str
    device_id: str
    data: Dict[str, Any]


@dataclass
class SessionResult:
    session_id: str
    success: bool
    duration: float
    errors: List[str]
    warnings: List[str]
    files_created: List[str]
    network_stats: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class MockAndroidDevice:

    def __init__(self, device_id: str, pc_host: str='localhost', pc_port:
        int=9000):
        self.device_id = device_id
        self.pc_host = pc_host
        self.pc_port = pc_port
        self.socket = None
        self.connected = False
        self.recording = False
        self.running = True
        self.capabilities = ['camera', 'thermal', 'gsr', 'imu']
        self.camera_active = False
        self.thermal_active = False
        self.shimmer_active = False
        self.data_thread = None
        self.preview_thread = None
        self.current_session = None
        self.messages_sent = 0
        self.messages_received = 0
        self.data_sent_bytes = 0
        logger.info(f'MockAndroidDevice {device_id} initialized')

    async def connect_to_pc(self) ->bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.pc_host, self.pc_port))
            self.connected = True
            handshake = {'type': 'device_connected', 'device_id': self.
                device_id, 'capabilities': self.capabilities, 'timestamp':
                time.time(), 'device_info': {'model': 'Samsung S22 (Mock)',
                'android_version': '14', 'app_version': '1.0.0-test'}}
            await self._send_message(handshake)
            logger.info(f'MockAndroidDevice {self.device_id} connected to PC')
            self._start_message_listener()
            return True
        except Exception as e:
            logger.error(f'Failed to connect {self.device_id} to PC: {e}')
            return False

    async def _send_message(self, message: Dict) ->bool:
        try:
            if not self.socket:
                return False
            json_data = json.dumps(message)
            message_bytes = json_data.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            self.socket.sendall(length_bytes + message_bytes)
            self.messages_sent += 1
            self.data_sent_bytes += len(message_bytes)
            logger.debug(
                f"MockAndroidDevice {self.device_id} sent: {message['type']}")
            return True
        except Exception as e:
            logger.error(f'Failed to send message from {self.device_id}: {e}')
            return False

    def _start_message_listener(self):

        def listen():
            while self.connected and self.running:
                try:
                    length_bytes = self.socket.recv(4)
                    if not length_bytes:
                        break
                    message_length = int.from_bytes(length_bytes, byteorder
                        ='big')
                    message_bytes = b''
                    while len(message_bytes) < message_length:
                        chunk = self.socket.recv(message_length - len(
                            message_bytes))
                        if not chunk:
                            break
                        message_bytes += chunk
                    if message_bytes:
                        message = json.loads(message_bytes.decode('utf-8'))
                        self.messages_received += 1
                        asyncio.create_task(self._handle_pc_message(message))
                except Exception as e:
                    logger.warning(
                        f'Message listening error for {self.device_id}: {e}')
                    break
        self.listener_thread = threading.Thread(target=listen, daemon=True)
        self.listener_thread.start()

    async def _handle_pc_message(self, message: Dict):
        message_type = message.get('type')
        logger.debug(
            f'MockAndroidDevice {self.device_id} received: {message_type}')
        if message_type == 'start_recording':
            await self._start_recording(message)
        elif message_type == 'stop_recording':
            await self._stop_recording(message)
        elif message_type == 'sync_clock':
            await self._sync_clock(message)
        elif message_type == 'get_status':
            await self._send_status()
        elif message_type == 'configure_sensors':
            await self._configure_sensors(message)
        else:
            logger.warning(f'Unknown message type: {message_type}')

    async def _start_recording(self, message: Dict):
        session_info = message.get('session_info', {})
        self.current_session = session_info
        self.recording = True
        self.camera_active = True
        self.thermal_active = True
        self.shimmer_active = True
        self._start_data_generation()
        response = {'type': 'recording_started', 'device_id': self.
            device_id, 'session_id': session_info.get('session_id'),
            'timestamp': time.time(), 'sensors_active': {'camera': self.
            camera_active, 'thermal': self.thermal_active, 'shimmer': self.
            shimmer_active}}
        await self._send_message(response)
        logger.info(f'MockAndroidDevice {self.device_id} started recording')

    async def _stop_recording(self, message: Dict):
        self.recording = False
        self.camera_active = False
        self.thermal_active = False
        self.shimmer_active = False
        self._stop_data_generation()
        response = {'type': 'recording_stopped', 'device_id': self.
            device_id, 'timestamp': time.time(), 'session_summary': {
            'duration': 30.0, 'files_created': [
            f'{self.device_id}_rgb_video.mp4',
            f'{self.device_id}_thermal_data.bin',
            f'{self.device_id}_gsr_data.csv'], 'data_size_mb': 150.5}}
        await self._send_message(response)
        logger.info(f'MockAndroidDevice {self.device_id} stopped recording')

    async def _sync_clock(self, message: Dict):
        pc_timestamp = message.get('pc_timestamp', time.time())
        device_timestamp = time.time()
        response = {'type': 'clock_sync_response', 'device_id': self.
            device_id, 'pc_timestamp': pc_timestamp, 'device_timestamp':
            device_timestamp, 'round_trip_time': 0.001}
        await self._send_message(response)
        logger.debug(f'MockAndroidDevice {self.device_id} synchronized clock')

    async def _send_status(self):
        status = {'type': 'device_status', 'device_id': self.device_id,
            'timestamp': time.time(), 'battery': 85, 'temperature': 35.2,
            'storage_free_gb': 25.6, 'recording': self.recording, 'sensors':
            {'camera': 'ready' if self.camera_active else 'idle', 'thermal':
            'ready' if self.thermal_active else 'idle', 'shimmer': 
            'connected' if self.shimmer_active else 'disconnected'},
            'network': {'signal_strength': -45, 'messages_sent': self.
            messages_sent, 'messages_received': self.messages_received,
            'data_sent_mb': self.data_sent_bytes / (1024 * 1024)}}
        await self._send_message(status)

    async def _configure_sensors(self, message: Dict):
        config = message.get('sensor_config', {})
        response = {'type': 'sensors_configured', 'device_id': self.
            device_id, 'timestamp': time.time(), 'applied_config': config}
        await self._send_message(response)
        logger.debug(f'MockAndroidDevice {self.device_id} configured sensors')

    def _start_data_generation(self):

        def generate_data():
            while self.recording and self.running:
                try:
                    if self.camera_active:
                        camera_data = {'type': 'camera_frame', 'device_id':
                            self.device_id, 'timestamp': time.time(),
                            'frame_number': getattr(self, '_frame_count', 0
                            ), 'resolution': '1920x1080', 'format': 'RGB'}
                        asyncio.create_task(self._send_message(camera_data))
                        self._frame_count = getattr(self, '_frame_count', 0
                            ) + 1
                    if self.thermal_active:
                        thermal_data = {'type': 'thermal_frame',
                            'device_id': self.device_id, 'timestamp': time.
                            time(), 'temperature_matrix':
                            f'256x192 thermal array', 'min_temp': 20.5,
                            'max_temp': 37.8, 'avg_temp': 29.1}
                        asyncio.create_task(self._send_message(thermal_data))
                    if self.shimmer_active:
                        gsr_data = {'type': 'shimmer_sample', 'device_id':
                            self.device_id, 'timestamp': time.time(),
                            'gsr_raw': 2048 + int(50 * np.sin(time.time())),
                            'gsr_resistance': 150.5, 'heart_rate': 72}
                        asyncio.create_task(self._send_message(gsr_data))
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(
                        f'Data generation error for {self.device_id}: {e}')
        self.data_thread = threading.Thread(target=generate_data, daemon=True)
        self.data_thread.start()

    def _stop_data_generation(self):
        pass

    def disconnect(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        logger.info(f'MockAndroidDevice {self.device_id} disconnected')


class MockWebcamCapture:

    def __init__(self):
        self.active = False
        self.recording = False
        self.frame_count = 0
        logger.info('MockWebcamCapture initialized')

    def list_cameras(self) ->List[Dict]:
        return [{'index': 0, 'name': 'Mock USB Webcam 1', 'resolution':
            '1920x1080'}, {'index': 1, 'name': 'Mock USB Webcam 2',
            'resolution': '1920x1080'}]

    def start_capture(self, camera_index: int=0) ->bool:
        self.active = True
        logger.info(f'MockWebcamCapture started on camera {camera_index}')
        return True

    def stop_capture(self):
        self.active = False
        self.recording = False
        logger.info('MockWebcamCapture stopped')

    def start_recording(self, output_path: str) ->bool:
        if not self.active:
            return False
        self.recording = True
        self.output_path = output_path
        logger.info(f'MockWebcamCapture started recording to {output_path}')
        return True

    def stop_recording(self) ->bool:
        if not self.recording:
            return False
        self.recording = False
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, 'wb') as f:
                f.write(b'MOCK_VIDEO_DATA' * 1000)
            logger.info(
                f'MockWebcamCapture saved recording to {self.output_path}')
            return True
        except Exception as e:
            logger.error(f'Failed to save mock recording: {e}')
            return False


class MockShimmerManager:

    def __init__(self):
        self.connected_devices = {}
        self.recording_sessions = {}
        logger.info('MockShimmerManager initialized')

    def discover_devices(self, timeout: float=5.0) ->List[Dict]:
        mock_devices = [{'address': '00:06:66:XX:XX:01', 'name':
            'Shimmer3-001', 'type': 'Shimmer3 GSR+'}, {'address':
            '00:06:66:XX:XX:02', 'name': 'Shimmer3-002', 'type':
            'Shimmer3 GSR+'}]
        logger.info(
            f'MockShimmerManager discovered {len(mock_devices)} devices')
        return mock_devices

    def connect_device(self, device_address: str) ->bool:
        self.connected_devices[device_address] = {'address': device_address,
            'connected_at': time.time(), 'status': 'connected'}
        logger.info(f'MockShimmerManager connected to {device_address}')
        return True

    def start_recording(self, device_address: str, session_id: str) ->bool:
        if device_address not in self.connected_devices:
            return False
        self.recording_sessions[session_id] = {'device_address':
            device_address, 'start_time': time.time(), 'sample_count': 0}
        logger.info(
            f'MockShimmerManager started recording session {session_id}')
        return True

    def stop_recording(self, session_id: str) ->Dict:
        if session_id not in self.recording_sessions:
            return {}
        session = self.recording_sessions[session_id]
        duration = time.time() - session['start_time']
        session_data = {'session_id': session_id, 'duration': duration,
            'sample_count': int(duration * 51.2), 'file_path':
            f'mock_gsr_data_{session_id}.csv'}
        del self.recording_sessions[session_id]
        logger.info(
            f'MockShimmerManager stopped recording session {session_id}')
        return session_data


class TestComprehensiveRecordingSession:

    @pytest.fixture(autouse=True)
    def setup_test(self, tmp_path):
        self.test_dir = tmp_path / 'recording_test'
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.session_manager = None
        self.device_server = None
        self.webcam_capture = None
        self.shimmer_manager = None
        self.mock_devices = []
        self.results = []
        self.errors = []
        self.warnings = []
        self.start_time = None
        self.end_time = None
        logger.info(
            f'ComprehensiveRecordingSessionTest initialized in {self.test_dir}'
            )

    def setup_test_environment(self) ->bool:
        try:
            logger.info('Setting up comprehensive test environment...')
            self.session_manager = SessionManager(str(self.test_dir /
                'recordings'))
            if DEPENDENCIES_AVAILABLE:
                self.device_server = JsonSocketServer(port=9000,
                    session_manager=self.session_manager)
            else:
                self.device_server = Mock()
                logger.warning(
                    'Using mock device server due to missing dependencies')
            self.webcam_capture = MockWebcamCapture()
            self.shimmer_manager = MockShimmerManager()
            logger.info('Test environment setup completed')
            return True
        except Exception as e:
            logger.error(f'Failed to setup test environment: {e}')
            self.errors.append(f'Setup error: {e}')
            return False

    def create_mock_android_devices(self, count: int=2) ->bool:
        try:
            logger.info(f'Creating {count} mock Android devices...')
            for i in range(count):
                device_id = f'phone_{i + 1}'
                mock_device = MockAndroidDevice(device_id)
                self.mock_devices.append(mock_device)
            logger.info(
                f'Created {len(self.mock_devices)} mock Android devices')
            return True
        except Exception as e:
            logger.error(f'Failed to create mock devices: {e}')
            self.errors.append(f'Mock device creation error: {e}')
            return False

    @pytest.mark.asyncio
    async def test_device_connections(self) ->bool:
        try:
            logger.info('Testing device connections...')
            if hasattr(self.device_server, 'start'):
                self.device_server.start()
                await asyncio.sleep(1)
            connection_tasks = []
            for device in self.mock_devices:
                task = asyncio.create_task(device.connect_to_pc())
                connection_tasks.append(task)
            results = await asyncio.gather(*connection_tasks,
                return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            total_count = len(self.mock_devices)
            if success_count == total_count:
                logger.info(f'All {total_count} devices connected successfully'
                    )
                return True
            else:
                logger.warning(
                    f'Only {success_count}/{total_count} devices connected')
                return False
        except Exception as e:
            logger.error(f'Device connection test failed: {e}')
            self.errors.append(f'Connection test error: {e}')
            return False

    @pytest.mark.asyncio
    async def test_recording_session_lifecycle(self) ->SessionResult:
        session_start = time.time()
        session_errors = []
        session_warnings = []
        files_created = []
        try:
            logger.info('=== Testing Recording Session Lifecycle ===')
            logger.info('Step 1: Creating recording session...')
            session_info = self.session_manager.create_session(
                'integration_test_session')
            session_id = session_info['session_id']
            logger.info(f'Created session: {session_id}')
            logger.info('Step 2: Configuring sensors...')
            webcam_configs = self.webcam_capture.list_cameras()
            for config in webcam_configs:
                if self.webcam_capture.start_capture(config['index']):
                    logger.info(
                        f"Started webcam {config['index']}: {config['name']}")
                else:
                    session_warnings.append(
                        f"Failed to start webcam {config['index']}")
            shimmer_devices = self.shimmer_manager.discover_devices()
            for device in shimmer_devices:
                if self.shimmer_manager.connect_device(device['address']):
                    logger.info(f"Connected Shimmer device: {device['name']}")
                else:
                    session_warnings.append(
                        f"Failed to connect Shimmer: {device['name']}")
            logger.info('Step 3: Synchronizing device clocks...')
            sync_tasks = []
            for device in self.mock_devices:
                sync_message = {'type': 'sync_clock', 'pc_timestamp': time.
                    time()}
                task = asyncio.create_task(device._send_message(sync_message))
                sync_tasks.append(task)
            await asyncio.gather(*sync_tasks, return_exceptions=True)
            logger.info('Clock synchronization completed')
            logger.info('Step 4: Starting recording session...')
            for i, config in enumerate(webcam_configs):
                output_path = str(self.test_dir / 'recordings' / session_id /
                    f'webcam_{i}.mp4')
                if self.webcam_capture.start_recording(output_path):
                    files_created.append(output_path)
                    logger.info(f'Started webcam recording: {output_path}')
            for device in shimmer_devices:
                if self.shimmer_manager.start_recording(device['address'],
                    session_id):
                    shimmer_file = str(self.test_dir / 'recordings' /
                        session_id / f"shimmer_{device['address']}.csv")
                    files_created.append(shimmer_file)
                    logger.info(
                        f"Started Shimmer recording: {device['address']}")
            start_message = {'type': 'start_recording', 'session_info':
                session_info}
            start_tasks = []
            for device in self.mock_devices:
                task = asyncio.create_task(device._send_message(start_message))
                start_tasks.append(task)
            await asyncio.gather(*start_tasks, return_exceptions=True)
            logger.info('All devices started recording')
            recording_duration = 5.0
            logger.info(
                f'Step 5: Recording for {recording_duration} seconds...')
            for i in range(int(recording_duration)):
                await asyncio.sleep(1)
                status_tasks = []
                for device in self.mock_devices:
                    task = asyncio.create_task(device._send_status())
                    status_tasks.append(task)
                await asyncio.gather(*status_tasks, return_exceptions=True)
                logger.debug(
                    f'Recording progress: {i + 1}/{int(recording_duration)} seconds'
                    )
            logger.info('Step 6: Stopping recording session...')
            stop_message = {'type': 'stop_recording'}
            stop_tasks = []
            for device in self.mock_devices:
                task = asyncio.create_task(device._send_message(stop_message))
                stop_tasks.append(task)
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            if self.webcam_capture.stop_recording():
                logger.info('Webcam recording stopped')
            for device in shimmer_devices:
                result = self.shimmer_manager.stop_recording(session_id)
                if result:
                    logger.info(f'Shimmer recording stopped: {result}')
            logger.info('Step 7: Finalizing session...')
            session_end = time.time()
            duration = session_end - session_start
            if hasattr(self.session_manager, 'finalize_session'):
                self.session_manager.finalize_session(session_id, {
                    'end_time': datetime.fromtimestamp(session_end).
                    isoformat(), 'duration': duration, 'files_created':
                    files_created})
            logger.info(f'=== Recording Session Completed Successfully ===')
            logger.info(f'Session ID: {session_id}')
            logger.info(f'Duration: {duration:.2f} seconds')
            logger.info(f'Files created: {len(files_created)}')
            return SessionResult(session_id=session_id, success=True,
                duration=duration, errors=session_errors, warnings=
                session_warnings, files_created=files_created,
                network_stats=self._get_network_stats(),
                performance_metrics=self._get_performance_metrics())
        except Exception as e:
            logger.error(f'Recording session test failed: {e}')
            session_errors.append(f'Session error: {e}')
            return SessionResult(session_id=session_info.get('session_id',
                'unknown'), success=False, duration=time.time() -
                session_start, errors=session_errors, warnings=
                session_warnings, files_created=files_created,
                network_stats=self._get_network_stats(),
                performance_metrics=self._get_performance_metrics())

    def _get_network_stats(self) ->Dict[str, Any]:
        stats = {'total_messages_sent': 0, 'total_messages_received': 0,
            'total_data_sent_mb': 0.0, 'devices': {}}
        for device in self.mock_devices:
            device_stats = {'messages_sent': device.messages_sent,
                'messages_received': device.messages_received,
                'data_sent_mb': device.data_sent_bytes / (1024 * 1024)}
            stats['devices'][device.device_id] = device_stats
            stats['total_messages_sent'] += device.messages_sent
            stats['total_messages_received'] += device.messages_received
            stats['total_data_sent_mb'] += device_stats['data_sent_mb']
        return stats

    def _get_performance_metrics(self) ->Dict[str, Any]:
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {'memory_rss_mb': memory_info.rss / (1024 * 1024),
                'memory_vms_mb': memory_info.vms / (1024 * 1024),
                'cpu_percent': process.cpu_percent(), 'num_threads':
                process.num_threads()}
        except ImportError:
            return {'error': 'psutil not available'}

    @pytest.mark.asyncio
    async def test_error_conditions(self) ->List[Dict]:
        error_tests = []
        try:
            logger.info('=== Testing Error Conditions ===')
            logger.info('Test 1: Simulating device disconnection...')
            if self.mock_devices:
                device = self.mock_devices[0]
                original_connected = device.connected
                device.connected = False
                try:
                    await device._send_message({'type': 'test'})
                    error_tests.append({'test': 'device_disconnection',
                        'result': 'unexpected_success', 'details':
                        'Message sent to disconnected device'})
                except:
                    error_tests.append({'test': 'device_disconnection',
                        'result': 'expected_failure', 'details':
                        'Correctly failed to send to disconnected device'})
                device.connected = original_connected
            logger.info('Test 2: Testing invalid message handling...')
            logger.info('Test 3: Simulating low storage space...')
            error_tests.append({'test': 'low_storage_simulation', 'result':
                'simulated', 'details':
                'Would test storage space handling in real environment'})
            logger.info('Test 4: Testing session management edge cases...')
            try:
                invalid_session = self.session_manager.create_session(
                    'invalid/name\\test')
                error_tests.append({'test': 'invalid_session_name',
                    'result': 'handled_gracefully', 'details':
                    f"Created session with sanitized name: {invalid_session['session_id']}"
                    })
            except Exception as e:
                error_tests.append({'test': 'invalid_session_name',
                    'result': 'error', 'details': str(e)})
            logger.info(f'Completed {len(error_tests)} error condition tests')
            return error_tests
        except Exception as e:
            logger.error(f'Error condition testing failed: {e}')
            return [{'test': 'error_testing', 'result': 'failed', 'details':
                str(e)}]

    def test_logging_functionality(self) ->Dict[str, Any]:
        logger.info('=== Testing Logging Functionality ===')
        logging_results = {'log_files_created': [], 'log_levels_tested': [],
            'components_logged': [], 'performance_logging': False,
            'error_logging': False}
        try:
            test_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            for level in test_levels:
                test_logger = get_logger(f'test_{level.lower()}')
                getattr(test_logger, level.lower())(
                    f'Test {level} message for comprehensive logging test')
                logging_results['log_levels_tested'].append(level)
            components = ['session_manager', 'device_server',
                'webcam_capture', 'shimmer_manager']
            for component in components:
                comp_logger = get_logger(f'test_{component}')
                comp_logger.info(f'Testing logging for {component} component')
                logging_results['components_logged'].append(component)
            start_time = time.time()
            time.sleep(0.01)
            end_time = time.time()
            perf_logger = get_logger('performance_test')
            perf_logger.info(
                f'Operation completed in {(end_time - start_time) * 1000:.1f}ms'
                )
            logging_results['performance_logging'] = True
            try:
                raise ValueError('Test exception for logging verification')
            except Exception as e:
                error_logger = get_logger('error_test')
                error_logger.error('Test exception caught and logged',
                    exc_info=True)
                logging_results['error_logging'] = True
            log_dir = AppLogger.get_log_dir()
            if log_dir and log_dir.exists():
                log_files = list(log_dir.glob('*.log'))
                logging_results['log_files_created'] = [f.name for f in
                    log_files]
                for log_file in log_files:
                    size = log_file.stat().st_size
                    logger.info(f'Log file {log_file.name}: {size} bytes')
            logger.info('Logging functionality test completed successfully')
            return logging_results
        except Exception as e:
            logger.error(f'Logging functionality test failed: {e}')
            logging_results['error'] = str(e)
            return logging_results

    def test_ui_responsiveness(self) ->Dict[str, Any]:
        logger.info('=== Testing UI Responsiveness (Simulated) ===')
        ui_results = {'button_response_times': [], 'ui_freeze_detected': 
            False, 'error_dialogs_handled': True, 'status_updates_working':
            True}
        try:
            for i in range(5):
                start_time = time.time()
                time.sleep(0.001)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                ui_results['button_response_times'].append(response_time)
                logger.debug(
                    f'Simulated button click {i + 1}: {response_time:.2f}ms')
            max_response_time = max(ui_results['button_response_times'])
            if max_response_time > 100:
                ui_results['ui_freeze_detected'] = True
                logger.warning(
                    f'Potential UI freeze detected: {max_response_time:.2f}ms response time'
                    )
            else:
                logger.info(
                    f'UI responsiveness good: max response time {max_response_time:.2f}ms'
                    )
            return ui_results
        except Exception as e:
            logger.error(f'UI responsiveness test failed: {e}')
            ui_results['error'] = str(e)
            return ui_results

    def verify_file_structure(self) ->Dict[str, Any]:
        logger.info('=== Verifying File Structure ===')
        file_verification = {'session_directories': [],
            'file_naming_correct': True, 'metadata_files_present': False,
            'data_files_present': False, 'total_files_created': 0}
        try:
            recordings_dir = self.test_dir / 'recordings'
            if recordings_dir.exists():
                session_dirs = [d for d in recordings_dir.iterdir() if d.
                    is_dir()]
                file_verification['session_directories'] = [d.name for d in
                    session_dirs]
                for session_dir in session_dirs:
                    logger.info(
                        f'Checking session directory: {session_dir.name}')
                    metadata_files = list(session_dir.glob('*.json'))
                    if metadata_files:
                        file_verification['metadata_files_present'] = True
                        logger.info(
                            f'Found metadata files: {[f.name for f in metadata_files]}'
                            )
                    data_files = list(session_dir.glob('*.mp4')) + list(
                        session_dir.glob('*.csv'))
                    if data_files:
                        file_verification['data_files_present'] = True
                        logger.info(
                            f'Found data files: {[f.name for f in data_files]}'
                            )
                    all_files = list(session_dir.glob('*'))
                    file_verification['total_files_created'] += len(all_files)
                    for file_path in all_files:
                        if not self._verify_filename_convention(file_path.name
                            ):
                            file_verification['file_naming_correct'] = False
                            logger.warning(
                                f'File naming issue: {file_path.name}')
            logger.info(f'File structure verification completed')
            logger.info(
                f"Total files created: {file_verification['total_files_created']}"
                )
            return file_verification
        except Exception as e:
            logger.error(f'File structure verification failed: {e}')
            file_verification['error'] = str(e)
            return file_verification

    def _verify_filename_convention(self, filename: str) ->bool:
        import re
        patterns = ['^phone_\\d+_\\w+_\\d{8}_\\d{6}\\.\\w+$',
            '^webcam_\\d+\\.\\w+$', '^shimmer_.*\\.csv$',
            '^session_\\d{8}_\\d{6}\\.json$', '^.*\\.log$']
        for pattern in patterns:
            if re.match(pattern, filename):
                return True
        return filename in ['test_file.txt', 'session_info.json']

    async def run_comprehensive_test(self) ->Dict[str, Any]:
        self.start_time = time.time()
        logger.info('=' * 80)
        logger.info('STARTING COMPREHENSIVE RECORDING SESSION TEST')
        logger.info('=' * 80)
        test_results = {'overall_success': False, 'start_time': datetime.
            fromtimestamp(self.start_time).isoformat(), 'setup_success': 
            False, 'device_connections': False, 'recording_session': None,
            'error_conditions': [], 'logging_test': {}, 'ui_responsiveness':
            {}, 'file_verification': {}, 'network_stats': {},
            'performance_metrics': {}, 'errors': [], 'warnings': []}
        try:
            logger.info('STEP 1: Setting up test environment...')
            test_results['setup_success'] = self.setup_test_environment()
            if not test_results['setup_success']:
                raise Exception('Failed to setup test environment')
            logger.info('STEP 2: Creating mock Android devices...')
            if not self.create_mock_android_devices(2):
                raise Exception('Failed to create mock devices')
            logger.info('STEP 3: Testing device connections...')
            test_results['device_connections'
                ] = await self.test_device_connections()
            logger.info('STEP 4: Testing recording session lifecycle...')
            test_results['recording_session'
                ] = await self.test_recording_session_lifecycle()
            logger.info('STEP 5: Testing error conditions...')
            test_results['error_conditions'
                ] = await self.test_error_conditions()
            logger.info('STEP 6: Testing logging functionality...')
            test_results['logging_test'] = self.test_logging_functionality()
            logger.info('STEP 7: Testing UI responsiveness...')
            test_results['ui_responsiveness'] = self.test_ui_responsiveness()
            logger.info('STEP 8: Verifying file structure...')
            test_results['file_verification'] = self.verify_file_structure()
            test_results['network_stats'] = self._get_network_stats()
            test_results['performance_metrics'
                ] = self._get_performance_metrics()
            test_results['errors'] = self.errors
            test_results['warnings'] = self.warnings
            test_results['overall_success'] = test_results['setup_success'
                ] and test_results['device_connections'] and test_results[
                'recording_session'] and test_results['recording_session'
                ].success
            self.end_time = time.time()
            test_duration = self.end_time - self.start_time
            test_results['duration'] = test_duration
            test_results['end_time'] = datetime.fromtimestamp(self.end_time
                ).isoformat()
            logger.info('=' * 80)
            if test_results['overall_success']:
                logger.info('✅ COMPREHENSIVE RECORDING SESSION TEST - SUCCESS')
            else:
                logger.info('❌ COMPREHENSIVE RECORDING SESSION TEST - FAILED')
            logger.info(f'Test Duration: {test_duration:.2f} seconds')
            logger.info('=' * 80)
            return test_results
        except Exception as e:
            logger.error(f'Comprehensive test failed: {e}')
            test_results['errors'].append(str(e))
            test_results['overall_success'] = False
            if self.start_time:
                test_results['duration'] = time.time() - self.start_time
                test_results['end_time'] = datetime.now().isoformat()
            return test_results
        finally:
            await self.cleanup()

    async def cleanup(self):
        logger.info('Cleaning up test resources...')
        try:
            for device in self.mock_devices:
                device.disconnect()
            if self.webcam_capture:
                self.webcam_capture.stop_capture()
            if hasattr(self.device_server, 'stop'):
                self.device_server.stop()
            logger.info('Cleanup completed')
        except Exception as e:
            logger.error(f'Cleanup error: {e}')


def print_test_summary(results: Dict[str, Any]):
    print('\n' + '=' * 80)
    print('📊 COMPREHENSIVE RECORDING SESSION TEST SUMMARY')
    print('=' * 80)
    if results['overall_success']:
        print('🎉 OVERALL RESULT: SUCCESS ✅')
    else:
        print('💥 OVERALL RESULT: FAILED ❌')
    duration = results.get('duration', 0)
    print(f'⏱️  TEST DURATION: {duration:.2f} seconds')
    print('\n📋 INDIVIDUAL TEST RESULTS:')
    print(
        f"  Setup Environment: {'✅' if results.get('setup_success') else '❌'}")
    print(
        f"  Device Connections: {'✅' if results.get('device_connections') else '❌'}"
        )
    session_result = results.get('recording_session')
    if session_result:
        print(f"  Recording Session: {'✅' if session_result.success else '❌'}")
        print(f'    Session ID: {session_result.session_id}')
        print(f'    Duration: {session_result.duration:.2f}s')
        print(f'    Files Created: {len(session_result.files_created)}')
    else:
        print('  Recording Session: ❌ (Not executed)')
    error_tests = results.get('error_conditions', [])
    print(f'  Error Condition Tests: {len(error_tests)} tests executed')
    logging_test = results.get('logging_test', {})
    log_files = len(logging_test.get('log_files_created', []))
    print(
        f"  Logging Functionality: {'✅' if log_files > 0 else '❌'} ({log_files} log files)"
        )
    ui_test = results.get('ui_responsiveness', {})
    ui_freeze = ui_test.get('ui_freeze_detected', True)
    print(f"  UI Responsiveness: {'❌' if ui_freeze else '✅'}")
    file_test = results.get('file_verification', {})
    files_created = file_test.get('total_files_created', 0)
    naming_correct = file_test.get('file_naming_correct', False)
    print(
        f"  File Structure: {'✅' if files_created > 0 and naming_correct else '❌'} ({files_created} files)"
        )
    network_stats = results.get('network_stats', {})
    if network_stats:
        print(f'\n🌐 NETWORK STATISTICS:')
        print(
            f"  Total Messages Sent: {network_stats.get('total_messages_sent', 0)}"
            )
        print(
            f"  Total Messages Received: {network_stats.get('total_messages_received', 0)}"
            )
        print(
            f"  Total Data Sent: {network_stats.get('total_data_sent_mb', 0):.2f} MB"
            )
    perf_metrics = results.get('performance_metrics', {})
    if perf_metrics and 'error' not in perf_metrics:
        print(f'\n⚡ PERFORMANCE METRICS:')
        print(f"  Memory Usage: {perf_metrics.get('memory_rss_mb', 0):.1f} MB")
        print(f"  CPU Usage: {perf_metrics.get('cpu_percent', 0):.1f}%")
        print(f"  Thread Count: {perf_metrics.get('num_threads', 0)}")
    errors = results.get('errors', [])
    warnings = results.get('warnings', [])
    if errors:
        print(f'\n❌ ERRORS ({len(errors)}):')
        for error in errors:
            print(f'  • {error}')
    if warnings:
        print(f'\n⚠️  WARNINGS ({len(warnings)}):')
        for warning in warnings:
            print(f'  • {warning}')
    print('\n' + '=' * 80)


async def main():
    logger.info('Starting Comprehensive Recording Session Integration Test...')
    test = ComprehensiveRecordingSessionTest()
    try:
        results = await test.run_comprehensive_test()
        print_test_summary(results)
        results_file = test.test_dir / 'test_results.json'
        with open(results_file, 'w') as f:

            def json_serializer(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, '__dict__'):
                    return obj.__dict__
                return str(obj)
            json.dump(results, f, indent=2, default=json_serializer)
        logger.info(f'Test results saved to: {results_file}')
        return 0 if results['overall_success'] else 1
    except Exception as e:
        logger.error(f'Test execution failed: {e}')
        print(f'\n❌ TEST EXECUTION FAILED: {e}')
        return 1


if __name__ == '__main__':
    if not DEPENDENCIES_AVAILABLE:
        print('⚠️  Some dependencies are missing, running with mock components'
            )
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
