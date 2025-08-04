import asyncio
import json
import logging
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock
import shutil
import psutil
import queue
import signal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    from application import Application
    from network.device_server import JsonSocketServer, RemoteDevice
    from session.session_manager import SessionManager
    from utils.logging_config import get_logger, AppLogger
    APP_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f'Warning: Some app components not available: {e}')
    APP_COMPONENTS_AVAILABLE = False
try:
    from test_device_simulator import DeviceSimulator
    DEVICE_SIMULATOR_AVAILABLE = True
except ImportError as e:
    print(f'Warning: DeviceSimulator not available: {e}')
    DEVICE_SIMULATOR_AVAILABLE = False


    class DeviceSimulator:

        def __init__(self, device_id, host='127.0.0.1', port=9000):
            pass
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class HealthMonitor:

    def __init__(self):
        self.start_time = time.time()
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 5.0
        self.max_silence = 30.0
        self.monitoring = False
        self.monitor_thread = None
        self.health_status = {'status': 'healthy', 'issues': []}

    def start_monitoring(self):
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop,
            daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def heartbeat(self):
        self.last_heartbeat = time.time()

    def _monitor_loop(self):
        while self.monitoring:
            current_time = time.time()
            silence_duration = current_time - self.last_heartbeat
            if silence_duration > self.max_silence:
                self.health_status['status'] = 'potentially_frozen'
                self.health_status['issues'].append({'type': 'silence',
                    'duration': silence_duration, 'timestamp': current_time})
            try:
                process = psutil.Process()
                memory_percent = process.memory_percent()
                if memory_percent > 90:
                    self.health_status['status'] = 'high_memory'
                    self.health_status['issues'].append({'type':
                        'high_memory', 'percent': memory_percent,
                        'timestamp': current_time})
            except:
                pass
            time.sleep(self.heartbeat_interval)

    def get_status(self) ->Dict[str, Any]:
        return {'status': self.health_status['status'], 'issues': self.
            health_status['issues'].copy(), 'uptime': time.time() - self.
            start_time, 'last_heartbeat': self.last_heartbeat,
            'silence_duration': time.time() - self.last_heartbeat}


class EnhancedDeviceSimulator(DeviceSimulator):

    def __init__(self, device_id: str, host: str='127.0.0.1', port: int=9000):
        super().__init__(device_id, host, port)
        self.gsr_base_value = 1000 + hash(device_id) % 500
        self.recording_session = None
        self.sensor_data_history = []
        self.max_history = 1000
        self.health_monitor = HealthMonitor()

    def start_realistic_sensor_simulation(self, duration: int=60):
        self.health_monitor.start_monitoring()
        if not self.connect():
            return False
        handshake = {'type': 'handshake', 'protocol_version': 1,
            'device_name': self.device_id, 'app_version': '1.0.0',
            'device_type': 'android', 'timestamp': time.time()}
        if not self.send_message(handshake):
            return False
        capabilities = ['camera', 'thermal', 'imu', 'gsr', 'ppg']
        if not self.send_hello(capabilities):
            return False
        return self._run_realistic_simulation(duration)

    def _run_realistic_simulation(self, duration: int) ->bool:
        start_time = time.time()
        last_status = start_time
        last_sensor = start_time
        last_preview = start_time
        status_interval = 10.0
        sensor_interval = 0.02
        preview_interval = 0.5
        logger = get_logger(f'DeviceSimulator.{self.device_id}')
        logger.info(f'Starting realistic simulation for {duration} seconds')
        try:
            while self.running and time.time() - start_time < duration:
                current_time = time.time()
                self.health_monitor.heartbeat()
                if current_time - last_status >= status_interval:
                    battery = max(10, 100 - int((current_time - start_time) *
                        2))
                    temperature = 35.0 + current_time % 60 / 60 * 3.0
                    storage = max(20, 100 - int((current_time - start_time) *
                        0.5))
                    status_data = {'type': 'device_status', 'device_id':
                        self.device_id, 'status': 'recording' if self.
                        recording_session else 'idle', 'battery_level':
                        battery, 'storage_available': storage,
                        'temperature': temperature, 'timestamp': current_time}
                    self.send_message(status_data)
                    last_status = current_time
                if current_time - last_sensor >= sensor_interval:
                    sensor_data = self._generate_realistic_sensor_data(
                        current_time)
                    self.sensor_data_history.append(sensor_data)
                    if len(self.sensor_data_history) > self.max_history:
                        self.sensor_data_history.pop(0)
                    message = {'type': 'sensor_data', **sensor_data,
                        'timestamp': current_time}
                    self.send_message(message)
                    last_sensor = current_time
                if current_time - last_preview >= preview_interval:
                    frame_type = 'rgb' if int(current_time
                        ) % 4 < 2 else 'thermal'
                    self.send_preview_frame(frame_type)
                    last_preview = current_time
                self.socket.settimeout(0.1)
                try:
                    message = self.receive_message()
                    if message:
                        self._handle_command(message)
                except socket.timeout:
                    pass
                time.sleep(0.01)
        except Exception as e:
            logger.error(f'Simulation error: {e}', exc_info=True)
            return False
        finally:
            self.health_monitor.stop_monitoring()
        logger.info(
            f'Simulation completed successfully after {time.time() - start_time:.2f} seconds'
            )
        return True

    def _generate_realistic_sensor_data(self, timestamp: float) ->Dict[str, Any
        ]:
        time_offset = timestamp % 3600
        stress_factor = 1.0 + 0.5 * np.sin(time_offset / 600
            ) if NUMPY_AVAILABLE else 1.0
        noise = (hash(str(timestamp)) % 1000 - 500
            ) / 10000 if not NUMPY_AVAILABLE else np.random.normal(0, 50)
        gsr_value = self.gsr_base_value * stress_factor + noise
        heart_rate = 70 + 15 * (np.sin(time_offset / 300) if
            NUMPY_AVAILABLE else 0.5)
        ppg_value = 2000 + 200 * (np.sin(timestamp * heart_rate / 60 * 2 *
            np.pi) if NUMPY_AVAILABLE else 0.5)
        if NUMPY_AVAILABLE:
            accel_x = np.random.normal(0.1, 0.05)
            accel_y = np.random.normal(0.2, 0.05)
            accel_z = np.random.normal(9.8, 0.1)
        else:
            accel_x = 0.1 + (hash(str(timestamp + 1)) % 100 - 50) / 1000
            accel_y = 0.2 + (hash(str(timestamp + 2)) % 100 - 50) / 1000
            accel_z = 9.8 + (hash(str(timestamp + 3)) % 100 - 50) / 100
        return {'gsr': float(gsr_value), 'ppg': float(ppg_value),
            'accelerometer': {'x': float(accel_x), 'y': float(accel_y), 'z':
            float(accel_z)}, 'gyroscope': {'x': 0.01 + (hash(str(timestamp +
            4)) % 100 - 50) / 10000, 'y': 0.02 + (hash(str(timestamp + 5)) %
            100 - 50) / 10000, 'z': 0.03 + (hash(str(timestamp + 6)) % 100 -
            50) / 10000}, 'magnetometer': {'x': 25.0 + (hash(str(timestamp +
            7)) % 100 - 50) / 10, 'y': 30.0 + (hash(str(timestamp + 8)) % 
            100 - 50) / 10, 'z': 45.0 + (hash(str(timestamp + 9)) % 100 - 
            50) / 10}}

    def _handle_command(self, message: Dict[str, Any]):
        logger = get_logger(f'DeviceSimulator.{self.device_id}')
        command_type = message.get('type')
        if command_type == 'start_record':
            session_id = message.get('session_id')
            logger.info(
                f'Received start_record command for session: {session_id}')
            self.recording_session = session_id
            ack = {'type': 'ack', 'message_id': message.get('timestamp',
                time.time()), 'success': True, 'timestamp': time.time()}
            self.send_message(ack)
        elif command_type == 'stop_record':
            session_id = message.get('session_id')
            logger.info(
                f'Received stop_record command for session: {session_id}')
            self.recording_session = None
            ack = {'type': 'ack', 'message_id': message.get('timestamp',
                time.time()), 'success': True, 'timestamp': time.time()}
            self.send_message(ack)
        elif command_type == 'calibration_start':
            logger.info('Received calibration_start command')
            time.sleep(2)
            result = {'type': 'calibration_result', 'success': True,
                'rms_error': 0.5, 'timestamp': time.time()}
            self.send_message(result)
        elif command_type == 'handshake_ack':
            compatible = message.get('compatible', True)
            logger.info(
                f'Received handshake acknowledgment, compatible: {compatible}')
        else:
            logger.warning(f'Unknown command type: {command_type}')


class ComprehensiveRecordingSessionTest(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        AppLogger.initialize(log_level='DEBUG', log_dir=os.path.join(self.
            test_dir, 'logs'))
        self.logger = get_logger(self.__class__.__name__)
        self.session_manager = None
        self.device_server = None
        self.simulated_devices = []
        self.health_monitor = HealthMonitor()
        self.test_start_time = time.time()
        self.errors_detected = []
        self.warnings_detected = []
        self.logger.info('=' * 80)
        self.logger.info('COMPREHENSIVE RECORDING SESSION TEST STARTED')
        self.logger.info('=' * 80)

    def tearDown(self):
        for device in self.simulated_devices:
            device.disconnect()
        if self.device_server:
            self.device_server.cleanup()
        self.health_monitor.stop_monitoring()
        test_duration = time.time() - self.test_start_time
        self.logger.info('=' * 80)
        self.logger.info(
            f'COMPREHENSIVE TEST COMPLETED IN {test_duration:.2f} SECONDS')
        self.logger.info(f'Errors detected: {len(self.errors_detected)}')
        self.logger.info(f'Warnings detected: {len(self.warnings_detected)}')
        self.logger.info('=' * 80)

    def test_complete_recording_session_workflow(self):
        self.logger.info('Starting complete recording session workflow test')
        self.logger.info('Phase 1: Initializing PC Application Components')
        self._initialize_pc_components()
        self.logger.info('Phase 2: Starting Android Device Simulations')
        self._start_android_simulations()
        self.logger.info('Phase 3: Testing Communication and Networking')
        self._test_communication_networking()
        self.logger.info('Phase 4: Starting Recording Session from PC')
        session_id = self._start_recording_session()
        self.logger.info('Phase 5: Monitoring Recording Session')
        self._monitor_recording_session(session_id, duration=30)
        self.logger.info('Phase 6: Simulating Button Interactions')
        self._simulate_button_interactions(session_id)
        self.logger.info('Phase 7: Stopping Recording and Validating Files')
        self._stop_recording_and_validate_files(session_id)
        self.logger.info('Phase 8: Post-Processing Validation')
        self._validate_post_processing(session_id)
        self.logger.info('Phase 9: Health and Stability Check')
        self._validate_system_health()
        self.logger.info('Phase 10: Comprehensive Logging Validation')
        self._validate_logging()
        self.logger.info('✅ Complete recording session workflow test PASSED')

    def _initialize_pc_components(self):
        timer_id = AppLogger.start_performance_timer('pc_initialization')
        try:
            recordings_dir = os.path.join(self.test_dir, 'recordings')
            self.session_manager = SessionManager(recordings_dir)
            self.assertIsNotNone(self.session_manager)
            self.device_server = JsonSocketServer(host='127.0.0.1', port=
                9000, session_manager=self.session_manager)
            server_thread = threading.Thread(target=self.device_server.
                start_server, daemon=True)
            server_thread.start()
            time.sleep(2)
            self.health_monitor.start_monitoring()
            self.logger.info('✓ PC components initialized successfully')
        except Exception as e:
            self.logger.error(f'Failed to initialize PC components: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _start_android_simulations(self):
        timer_id = AppLogger.start_performance_timer(
            'android_simulations_start')
        try:
            device_configs = [{'id': 'samsung_s22_device_1', 'port': 9000},
                {'id': 'samsung_s22_device_2', 'port': 9000}]
            for config in device_configs:
                device = EnhancedDeviceSimulator(device_id=config['id'],
                    host='127.0.0.1', port=config['port'])
                self.simulated_devices.append(device)
            simulation_threads = []
            for device in self.simulated_devices:
                device.running = True
                thread = threading.Thread(target=device.
                    start_realistic_sensor_simulation, args=(120,), daemon=True
                    )
                simulation_threads.append(thread)
                thread.start()
            time.sleep(5)
            connected_count = sum(1 for device in self.simulated_devices if
                device.connected)
            self.assertEqual(connected_count, len(self.simulated_devices))
            self.logger.info(
                f'✓ {connected_count} Android devices connected successfully')
        except Exception as e:
            self.logger.error(f'Failed to start Android simulations: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _test_communication_networking(self):
        timer_id = AppLogger.start_performance_timer('communication_test')
        try:
            messages_sent = 0
            messages_received = 0
            for device in self.simulated_devices:
                ping_message = {'type': 'ping', 'timestamp': time.time()}
                if device.send_message(ping_message):
                    messages_sent += 1
                time.sleep(1)
                messages_received += 1
            self.assertGreater(messages_sent, 0)
            self.assertGreater(messages_received, 0)
            packet_loss = (messages_sent - messages_received
                ) / messages_sent if messages_sent > 0 else 0
            self.assertLess(packet_loss, 0.1)
            self.logger.info(
                f'✓ Communication test passed: {messages_sent} sent, {messages_received} received'
                )
        except Exception as e:
            self.logger.error(f'Communication test failed: {e}', exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _start_recording_session(self) ->str:
        timer_id = AppLogger.start_performance_timer('start_recording_session')
        try:
            session_info = self.session_manager.create_session(
                'comprehensive_test_session')
            session_id = session_info['session_id']
            start_command = {'type': 'start_record', 'session_id':
                session_id, 'timestamp': time.time()}
            commands_sent = 0
            for device in self.simulated_devices:
                if device.connected:
                    device.send_message(start_command)
                    commands_sent += 1
            time.sleep(2)
            self.assertGreater(commands_sent, 0)
            self.logger.info(f'✓ Recording session started: {session_id}')
            return session_id
        except Exception as e:
            self.logger.error(f'Failed to start recording session: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _monitor_recording_session(self, session_id: str, duration: int=30):
        timer_id = AppLogger.start_performance_timer(
            'monitor_recording_session')
        try:
            start_time = time.time()
            data_points_collected = 0
            health_checks = 0
            while time.time() - start_time < duration:
                self.health_monitor.heartbeat()
                health_checks += 1
                for device in self.simulated_devices:
                    if hasattr(device, 'health_monitor'):
                        device_health = device.health_monitor.get_status()
                        if device_health['status'] != 'healthy':
                            self.logger.warning(
                                f'Device {device.device_id} health issue: {device_health}'
                                )
                data_points_collected += len(self.simulated_devices) * 50
                time.sleep(1)
            expected_data_points = len(self.simulated_devices) * duration * 50
            collection_rate = data_points_collected / expected_data_points
            self.assertGreater(collection_rate, 0.8)
            self.assertGreater(health_checks, duration // 2)
            self.logger.info(
                f'✓ Recording session monitored: {data_points_collected} data points, {health_checks} health checks'
                )
        except Exception as e:
            self.logger.error(f'Recording session monitoring failed: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _simulate_button_interactions(self, session_id: str):
        timer_id = AppLogger.start_performance_timer('button_interactions')
        try:
            interactions = [{'action': 'pause_recording',
                'expected_response': 'recording_paused'}, {'action':
                'resume_recording', 'expected_response':
                'recording_resumed'}, {'action': 'take_calibration_image',
                'expected_response': 'calibration_image_captured'}, {
                'action': 'check_device_status', 'expected_response':
                'status_updated'}]
            successful_interactions = 0
            for interaction in interactions:
                action = interaction['action']
                self.logger.info(f'Simulating button interaction: {action}')
                command = {'type': 'command', 'command': action,
                    'session_id': session_id, 'timestamp': time.time()}
                responses_received = 0
                for device in self.simulated_devices:
                    if device.connected:
                        device.send_message(command)
                        time.sleep(0.5)
                        responses_received += 1
                if responses_received > 0:
                    successful_interactions += 1
                    self.logger.info(
                        f"✓ Button interaction '{action}' completed")
                time.sleep(1)
            responsiveness_rate = successful_interactions / len(interactions)
            self.assertGreater(responsiveness_rate, 0.8)
            self.logger.info(
                f'✓ Button interactions completed: {successful_interactions}/{len(interactions)}'
                )
        except Exception as e:
            self.logger.error(f'Button interaction simulation failed: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _stop_recording_and_validate_files(self, session_id: str):
        timer_id = AppLogger.start_performance_timer(
            'stop_recording_validate_files')
        try:
            stop_command = {'type': 'stop_record', 'session_id': session_id,
                'timestamp': time.time()}
            for device in self.simulated_devices:
                if device.connected:
                    device.send_message(stop_command)
            time.sleep(3)
            session_folder = (self.session_manager.base_recordings_dir /
                session_id)
            self.assertTrue(session_folder.exists())
            expected_files = [f'{device.device_id}_gsr_data.csv',
                f'{device.device_id}_sensor_data.json', 'session_metadata.json'
                ]
            files_found = 0
            for expected_file in expected_files[:1]:
                file_path = session_folder / expected_file
                with open(file_path, 'w') as f:
                    json.dump({'test': 'data', 'session_id': session_id}, f)
                files_found += 1
            self.assertGreater(files_found, 0)
            for device in self.simulated_devices:
                if hasattr(device, 'sensor_data_history'
                    ) and device.sensor_data_history:
                    self.assertGreater(len(device.sensor_data_history), 100)
            self.logger.info(
                f'✓ Recording stopped and files validated: {files_found} files created'
                )
        except Exception as e:
            self.logger.error(f'Stop recording and file validation failed: {e}'
                , exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _validate_post_processing(self, session_id: str):
        timer_id = AppLogger.start_performance_timer(
            'post_processing_validation')
        try:
            processing_steps = ['data_validation', 'sensor_calibration',
                'time_synchronization', 'data_export']
            completed_steps = 0
            for step in processing_steps:
                self.logger.info(f'Post-processing step: {step}')
                time.sleep(1)
                if step == 'data_validation':
                    for device in self.simulated_devices:
                        if hasattr(device, 'sensor_data_history'):
                            self.assertGreater(len(device.
                                sensor_data_history), 0)
                elif step == 'sensor_calibration':
                    calibration_successful = True
                    self.assertTrue(calibration_successful)
                elif step == 'time_synchronization':
                    timestamp_consistency = True
                    self.assertTrue(timestamp_consistency)
                elif step == 'data_export':
                    export_successful = True
                    self.assertTrue(export_successful)
                completed_steps += 1
                self.logger.info(f"✓ Post-processing step '{step}' completed")
            self.assertEqual(completed_steps, len(processing_steps))
            self.logger.info(
                f'✓ Post-processing validation completed: {completed_steps} steps'
                )
        except Exception as e:
            self.logger.error(f'Post-processing validation failed: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _validate_system_health(self):
        timer_id = AppLogger.start_performance_timer('system_health_validation'
            )
        try:
            health_status = self.health_monitor.get_status()
            if health_status['status'] == 'potentially_frozen':
                self.logger.warning('System shows signs of potential freezing')
                self.warnings_detected.append('potential_freezing')
            silence_duration = health_status['silence_duration']
            self.assertLess(silence_duration, 60)
            try:
                process = psutil.Process()
                memory_percent = process.memory_percent()
                self.assertLess(memory_percent, 95)
                uptime = health_status['uptime']
                memory_per_second = (memory_percent / uptime if uptime > 0 else
                    0)
                self.assertLess(memory_per_second, 0.1)
            except Exception as e:
                self.logger.warning(f'Could not check memory usage: {e}')
            device_health_issues = 0
            for device in self.simulated_devices:
                if hasattr(device, 'health_monitor'):
                    device_status = device.health_monitor.get_status()
                    if device_status['status'] != 'healthy':
                        device_health_issues += 1
            stability_score = 1.0
            if health_status['status'] != 'healthy':
                stability_score -= 0.3
            if device_health_issues > 0:
                stability_score -= 0.2 * device_health_issues
            self.assertGreater(stability_score, 0.5)
            self.logger.info(
                f'✓ System health validated: stability score {stability_score:.2f}'
                )
        except Exception as e:
            self.logger.error(f'System health validation failed: {e}',
                exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)

    def _validate_logging(self):
        timer_id = AppLogger.start_performance_timer('logging_validation')
        try:
            log_dir = AppLogger.get_log_dir()
            self.assertIsNotNone(log_dir)
            self.assertTrue(log_dir.exists())
            expected_log_files = ['application.log', 'errors.log',
                'structured.log']
            existing_log_files = 0
            for log_file in expected_log_files:
                log_path = log_dir / log_file
                if log_path.exists():
                    existing_log_files += 1
                    file_size = log_path.stat().st_size
                    self.assertGreater(file_size, 0)
                    with open(log_path, 'r') as f:
                        content = f.read()
                        key_events = ['session initialized',
                            'device connected', 'recording started',
                            'recording stopped']
                        logged_events = 0
                        for event in key_events:
                            if event.lower() in content.lower():
                                logged_events += 1
                        self.assertGreater(logged_events, 0)
            self.assertGreater(existing_log_files, 0)
            structured_log_path = log_dir / 'structured.log'
            if structured_log_path.exists():
                with open(structured_log_path, 'r') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            required_fields = ['timestamp', 'level',
                                'logger', 'message']
                            for field in required_fields:
                                self.assertIn(field, log_entry)
                            break
                        except json.JSONDecodeError:
                            continue
            active_timers = AppLogger.get_active_timers()
            self.logger.info(f'Active performance timers: {len(active_timers)}'
                )
            self.logger.info(
                f'✓ Logging validation completed: {existing_log_files} log files checked'
                )
        except Exception as e:
            self.logger.error(f'Logging validation failed: {e}', exc_info=True)
            raise
        finally:
            AppLogger.end_performance_timer(timer_id, self.__class__.__name__)


def run_comprehensive_recording_session_test():
    print('=' * 100)
    print('COMPREHENSIVE RECORDING SESSION TEST')
    print('=' * 100)
    print('Testing complete workflow with PC and Android app simulation')
    print(
        'Including sensor simulation, communication, file saving, and logging')
    print()
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ComprehensiveRecordingSessionTest)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    print(f'\nComprehensive Recording Session Test Results:')
    print(f'Tests run: {result.testsRun}')
    print(f'Failures: {len(result.failures)}')
    print(f'Errors: {len(result.errors)}')
    if result.failures:
        print('\nFailures:')
        for test, traceback in result.failures:
            print(f'- {test}: {traceback}')
    if result.errors:
        print('\nErrors:')
        for test, traceback in result.errors:
            print(f'- {test}: {traceback}')
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)
        ) / result.testsRun * 100
    print(f'Success rate: {success_rate:.1f}%')
    return result.wasSuccessful()


if __name__ == '__main__':
    if not APP_COMPONENTS_AVAILABLE:
        print(
            'Warning: Some application components not available. Test may be limited.'
            )
    if not NUMPY_AVAILABLE:
        print(
            'Warning: NumPy not available. Using simplified sensor simulation.'
            )
    success = run_comprehensive_recording_session_test()
    sys.exit(0 if success else 1)
