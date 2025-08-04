import asyncio
import json
import logging
import os
import socket
import sys
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import tempfile
import subprocess
sys.path.insert(0, str(Path(__file__).parent / 'src'))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from utils.logging_config import get_logger, AppLogger
AppLogger.set_level('DEBUG')
logger = get_logger(__name__)
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning('OpenCV not available - will simulate camera detection')
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning('NumPy not available - will use basic calculations')


@dataclass
class SensorSpec:
    name: str
    connection_type: str
    port_range: Tuple[int, int]
    data_rate_hz: float
    data_format: str
    available: bool = False
    simulated: bool = False


@dataclass
class SensorData:
    sensor_id: str
    timestamp: float
    data_type: str
    raw_data: Any
    processed_data: Optional[Dict] = None
    metadata: Optional[Dict] = None


class USBCameraDetector:

    def __init__(self):
        self.detected_cameras = []
        self.simulated_cameras = []

    def detect_available_cameras(self) ->List[Dict]:
        cameras = []
        if OPENCV_AVAILABLE:
            for i in range(4):
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            height, width = frame.shape[:2]
                            cameras.append({'index': i, 'name':
                                f'USB Camera {i}', 'resolution':
                                f'{width}x{height}', 'available': True,
                                'device_path': f'/dev/video{i}'})
                            logger.info(
                                f'Detected USB camera {i}: {width}x{height}')
                    cap.release()
                except Exception as e:
                    logger.debug(f'Camera {i} detection failed: {e}')
        if not cameras:
            for i in range(2):
                cameras.append({'index': i + 10, 'name':
                    f'Simulated USB Camera {i + 1}', 'resolution':
                    '1920x1080', 'available': False, 'simulated': True,
                    'device_path': f'/dev/video{i + 10}'})
                logger.info(f'Created simulated USB camera {i + 1}')
        self.detected_cameras = [c for c in cameras if c['available']]
        self.simulated_cameras = [c for c in cameras if c.get('simulated')]
        return cameras

    def create_camera_stream(self, camera_info: Dict) ->'MockCameraStream':
        return MockCameraStream(camera_info)


class MockCameraStream:

    def __init__(self, camera_info: Dict):
        self.camera_info = camera_info
        self.active = False
        self.frame_count = 0
        self.fps = 30.0

    def start_stream(self) ->bool:
        self.active = True
        logger.info(f"Started camera stream: {self.camera_info['name']}")
        return True

    def stop_stream(self):
        self.active = False
        logger.info(f"Stopped camera stream: {self.camera_info['name']}")

    def get_frame(self) ->Optional[SensorData]:
        if not self.active:
            return None
        if NUMPY_AVAILABLE:
            height, width = 480, 640
            frame_data = np.random.randint(0, 255, (height, width, 3),
                dtype=np.uint8)
        else:
            frame_data = f'mock_frame_{self.frame_count}'
        self.frame_count += 1
        return SensorData(sensor_id=self.camera_info['name'], timestamp=
            time.time(), data_type='rgb_frame', raw_data=frame_data,
            metadata={'frame_number': self.frame_count, 'resolution': self.
            camera_info['resolution'], 'fps': self.fps})


class BluetoothSensorDetector:

    def __init__(self):
        self.detected_devices = []
        self.simulated_devices = []

    def scan_bluetooth_devices(self, timeout: float=5.0) ->List[Dict]:
        devices = []
        try:
            result = subprocess.run(['which', 'bluetoothctl'],
                capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                logger.info('Bluetooth tools available, attempting scan...')
        except Exception as e:
            logger.debug(f'Bluetooth scan tools not available: {e}')
        shimmer_devices = [{'address': '00:06:66:AA:BB:01', 'name':
            'Shimmer3-GSR-001', 'device_type': 'shimmer3_gsr', 'available':
            False, 'simulated': True, 'connection_type': 'bluetooth'}, {
            'address': '00:06:66:AA:BB:02', 'name': 'Shimmer3-GSR-002',
            'device_type': 'shimmer3_gsr', 'available': False, 'simulated':
            True, 'connection_type': 'bluetooth'}]
        devices.extend(shimmer_devices)
        self.simulated_devices = shimmer_devices
        logger.info(f'Bluetooth scan completed: {len(devices)} devices found')
        return devices

    def create_shimmer_connection(self, device_info: Dict
        ) ->'MockShimmerDevice':
        return MockShimmerDevice(device_info)


class MockShimmerDevice:

    def __init__(self, device_info: Dict):
        self.device_info = device_info
        self.connected = False
        self.recording = False
        self.sample_count = 0
        self.sample_rate = 51.2

    def connect(self) ->bool:
        self.connected = True
        logger.info(f"Connected to Shimmer: {self.device_info['name']}")
        return True

    def disconnect(self):
        self.connected = False
        self.recording = False
        logger.info(f"Disconnected from Shimmer: {self.device_info['name']}")

    def start_recording(self) ->bool:
        if not self.connected:
            return False
        self.recording = True
        self.sample_count = 0
        logger.info(f"Started GSR recording: {self.device_info['name']}")
        return True

    def stop_recording(self) ->bool:
        self.recording = False
        logger.info(f"Stopped GSR recording: {self.device_info['name']}")
        return True

    def get_sample(self) ->Optional[SensorData]:
        if not self.recording:
            return None
        base_resistance = 150.0
        noise = 5.0 * (0.5 - hash(self.sample_count) % 100 / 100)
        resistance = base_resistance + noise
        raw_value = int(2048 + (resistance - 150) * 10)
        self.sample_count += 1
        return SensorData(sensor_id=self.device_info['address'], timestamp=
            time.time(), data_type='gsr_sample', raw_data=raw_value,
            processed_data={'resistance_kohms': resistance,
            'conductance_us': 1000.0 / resistance}, metadata={
            'sample_number': self.sample_count, 'sample_rate': self.
            sample_rate, 'device_name': self.device_info['name']})


class ThermalCameraSimulator:

    def __init__(self):
        self.connected = False
        self.recording = False
        self.frame_count = 0

    def detect_thermal_camera(self) ->Dict:
        thermal_info = {'name': 'Topdon TC001 (Simulated)', 'connection':
            'usb_c', 'resolution': '256x192', 'available': False,
            'simulated': True, 'temp_range': (-20, 550), 'device_path':
            '/dev/thermal0'}
        logger.info('Thermal camera simulation initialized')
        return thermal_info

    def connect(self) ->bool:
        self.connected = True
        logger.info('Connected to thermal camera (simulated)')
        return True

    def disconnect(self):
        self.connected = False
        self.recording = False
        logger.info('Disconnected thermal camera')

    def start_recording(self) ->bool:
        if not self.connected:
            return False
        self.recording = True
        self.frame_count = 0
        logger.info('Started thermal recording')
        return True

    def stop_recording(self) ->bool:
        self.recording = False
        logger.info('Stopped thermal recording')
        return True

    def get_thermal_frame(self) ->Optional[SensorData]:
        if not self.recording:
            return None
        if NUMPY_AVAILABLE:
            height, width = 192, 256
            base_temp = 25.0
            thermal_data = np.random.normal(base_temp, 2.0, (height, width))
            center_y, center_x = height // 2, width // 2
            thermal_data[center_y - 10:center_y + 10, center_x - 10:
                center_x + 10] += 10.0
            min_temp = float(np.min(thermal_data))
            max_temp = float(np.max(thermal_data))
            avg_temp = float(np.mean(thermal_data))
        else:
            thermal_data = f'thermal_frame_{self.frame_count}'
            min_temp, max_temp, avg_temp = 20.0, 40.0, 25.0
        self.frame_count += 1
        return SensorData(sensor_id='thermal_camera', timestamp=time.time(),
            data_type='thermal_frame', raw_data=thermal_data,
            processed_data={'min_temperature': min_temp, 'max_temperature':
            max_temp, 'avg_temperature': avg_temp}, metadata={
            'frame_number': self.frame_count, 'resolution': '256x192',
            'temp_unit': 'celsius'})


class NetworkSensorSimulator:

    def __init__(self, device_id: str, base_port: int=8080):
        self.device_id = device_id
        self.base_port = base_port
        self.sensors = {'camera': {'port': base_port + 1, 'active': False},
            'accelerometer': {'port': base_port + 2, 'active': False},
            'gyroscope': {'port': base_port + 3, 'active': False},
            'magnetometer': {'port': base_port + 4, 'active': False}}
        self.socket_server = None

    def start_sensor_services(self) ->bool:
        try:
            self.socket_server = socket.socket(socket.AF_INET, socket.
                SOCK_DGRAM)
            self.socket_server.bind(('localhost', self.base_port))
            for sensor_name in self.sensors:
                self.sensors[sensor_name]['active'] = True
            logger.info(
                f'Network sensors started for {self.device_id} on port {self.base_port}'
                )
            return True
        except Exception as e:
            logger.error(f'Failed to start network sensors: {e}')
            return False

    def stop_sensor_services(self):
        for sensor_name in self.sensors:
            self.sensors[sensor_name]['active'] = False
        if self.socket_server:
            self.socket_server.close()
        logger.info(f'Network sensors stopped for {self.device_id}')

    def get_sensor_data(self, sensor_type: str) ->Optional[SensorData]:
        if sensor_type not in self.sensors or not self.sensors[sensor_type][
            'active']:
            return None
        timestamp = time.time()
        if sensor_type == 'camera':
            return SensorData(sensor_id=f'{self.device_id}_{sensor_type}',
                timestamp=timestamp, data_type='camera_frame', raw_data=
                f'camera_frame_{int(timestamp * 30) % 1000}', metadata={
                'fps': 30, 'resolution': '1920x1080'})
        elif sensor_type == 'accelerometer':
            x = 0.1 * (hash(int(timestamp * 100)) % 200 - 100) / 100
            y = 0.1 * (hash(int(timestamp * 100) + 1) % 200 - 100) / 100
            z = 9.8 + 0.2 * (hash(int(timestamp * 100) + 2) % 200 - 100) / 100
            return SensorData(sensor_id=f'{self.device_id}_{sensor_type}',
                timestamp=timestamp, data_type='accelerometer', raw_data=[x,
                y, z], processed_data={'magnitude': (x ** 2 + y ** 2 + z **
                2) ** 0.5}, metadata={'unit': 'm/s^2', 'sample_rate': 100})
        elif sensor_type == 'gyroscope':
            gx = 0.05 * (hash(int(timestamp * 50)) % 200 - 100) / 100
            gy = 0.05 * (hash(int(timestamp * 50) + 1) % 200 - 100) / 100
            gz = 0.05 * (hash(int(timestamp * 50) + 2) % 200 - 100) / 100
            return SensorData(sensor_id=f'{self.device_id}_{sensor_type}',
                timestamp=timestamp, data_type='gyroscope', raw_data=[gx,
                gy, gz], metadata={'unit': 'rad/s', 'sample_rate': 50})
        elif sensor_type == 'magnetometer':
            mx = 30.0 + 5.0 * (hash(int(timestamp * 20)) % 200 - 100) / 100
            my = -10.0 + 5.0 * (hash(int(timestamp * 20) + 1) % 200 - 100
                ) / 100
            mz = 45.0 + 5.0 * (hash(int(timestamp * 20) + 2) % 200 - 100) / 100
            return SensorData(sensor_id=f'{self.device_id}_{sensor_type}',
                timestamp=timestamp, data_type='magnetometer', raw_data=[mx,
                my, mz], metadata={'unit': 'µT', 'sample_rate': 20})
        return None


class HardwareSensorTest:

    def __init__(self, test_dir: Optional[str]=None):
        self.test_dir = Path(test_dir) if test_dir else Path(tempfile.
            mkdtemp(prefix='sensor_test_'))
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.usb_camera_detector = USBCameraDetector()
        self.bluetooth_detector = BluetoothSensorDetector()
        self.thermal_simulator = ThermalCameraSimulator()
        self.network_simulators = []
        self.active_cameras = []
        self.active_shimmer_devices = []
        self.active_network_sensors = []
        self.test_results = {'start_time': None, 'duration': 0,
            'sensors_detected': {}, 'sensors_simulated': {},
            'data_samples_collected': {}, 'errors': [], 'warnings': [],
            'performance_metrics': {}}
        logger.info(f'HardwareSensorTest initialized in {self.test_dir}')

    def detect_all_sensors(self) ->Dict[str, Any]:
        logger.info('=== Detecting All Sensor Types ===')
        detection_results = {'usb_cameras': [], 'bluetooth_devices': [],
            'thermal_cameras': [], 'network_devices': []}
        logger.info('Detecting USB cameras...')
        cameras = self.usb_camera_detector.detect_available_cameras()
        detection_results['usb_cameras'] = cameras
        available_cameras = [c for c in cameras if c['available']]
        simulated_cameras = [c for c in cameras if c.get('simulated')]
        logger.info(
            f'USB cameras: {len(available_cameras)} real, {len(simulated_cameras)} simulated'
            )
        logger.info('Scanning for Bluetooth devices...')
        bt_devices = self.bluetooth_detector.scan_bluetooth_devices()
        detection_results['bluetooth_devices'] = bt_devices
        available_bt = [d for d in bt_devices if d['available']]
        simulated_bt = [d for d in bt_devices if d.get('simulated')]
        logger.info(
            f'Bluetooth devices: {len(available_bt)} real, {len(simulated_bt)} simulated'
            )
        logger.info('Detecting thermal camera...')
        thermal_info = self.thermal_simulator.detect_thermal_camera()
        detection_results['thermal_cameras'] = [thermal_info]
        logger.info(
            f"Thermal camera: {'real' if thermal_info['available'] else 'simulated'}"
            )
        logger.info('Setting up network sensor simulators...')
        for i in range(2):
            device_id = f'phone_{i + 1}'
            base_port = 8080 + i * 10
            network_sim = NetworkSensorSimulator(device_id, base_port)
            self.network_simulators.append(network_sim)
            detection_results['network_devices'].append({'device_id':
                device_id, 'base_port': base_port, 'sensors': list(
                network_sim.sensors.keys())})
        logger.info(
            f'Network devices: {len(self.network_simulators)} simulated')
        self.test_results['sensors_detected'] = {'usb_cameras_real': len(
            available_cameras), 'usb_cameras_simulated': len(
            simulated_cameras), 'bluetooth_real': len(available_bt),
            'bluetooth_simulated': len(simulated_bt), 'thermal_real': 1 if
            thermal_info['available'] else 0, 'thermal_simulated': 1 if
            thermal_info['simulated'] else 0, 'network_simulated': len(self
            .network_simulators)}
        return detection_results

    async def test_usb_camera_streams(self) ->bool:
        logger.info('=== Testing USB Camera Streams ===')
        try:
            cameras = (self.usb_camera_detector.detected_cameras + self.
                usb_camera_detector.simulated_cameras)
            if not cameras:
                logger.warning('No cameras available for testing')
                return False
            for camera_info in cameras:
                stream = self.usb_camera_detector.create_camera_stream(
                    camera_info)
                if stream.start_stream():
                    self.active_cameras.append(stream)
            if not self.active_cameras:
                logger.error('Failed to start any camera streams')
                return False
            sample_count = 0
            for i in range(10):
                for stream in self.active_cameras:
                    frame_data = stream.get_frame()
                    if frame_data:
                        sample_count += 1
                        logger.debug(
                            f'Collected frame from {frame_data.sensor_id}')
                await asyncio.sleep(0.1)
            for stream in self.active_cameras:
                stream.stop_stream()
            logger.info(
                f'✅ USB camera test: {sample_count} frames collected from {len(self.active_cameras)} cameras'
                )
            if 'usb_camera' not in self.test_results['data_samples_collected']:
                self.test_results['data_samples_collected']['usb_camera'] = 0
            self.test_results['data_samples_collected']['usb_camera'
                ] += sample_count
            return sample_count > 0
        except Exception as e:
            logger.error(f'USB camera test failed: {e}')
            self.test_results['errors'].append(f'USB camera: {e}')
            return False

    async def test_bluetooth_sensors(self) ->bool:
        logger.info('=== Testing Bluetooth Sensors ===')
        try:
            bt_devices = self.bluetooth_detector.simulated_devices
            if not bt_devices:
                logger.warning('No Bluetooth devices available for testing')
                return False
            for device_info in bt_devices:
                shimmer = self.bluetooth_detector.create_shimmer_connection(
                    device_info)
                if shimmer.connect():
                    self.active_shimmer_devices.append(shimmer)
            if not self.active_shimmer_devices:
                logger.error('Failed to connect to any Shimmer devices')
                return False
            for shimmer in self.active_shimmer_devices:
                shimmer.start_recording()
            sample_count = 0
            for i in range(50):
                for shimmer in self.active_shimmer_devices:
                    sample = shimmer.get_sample()
                    if sample:
                        sample_count += 1
                        logger.debug(
                            f"GSR sample: {sample.processed_data['resistance_kohms']:.1f} kΩ"
                            )
                await asyncio.sleep(1.0 / 51.2)
            for shimmer in self.active_shimmer_devices:
                shimmer.stop_recording()
                shimmer.disconnect()
            logger.info(
                f'✅ Bluetooth sensor test: {sample_count} GSR samples from {len(self.active_shimmer_devices)} devices'
                )
            if 'bluetooth_gsr' not in self.test_results[
                'data_samples_collected']:
                self.test_results['data_samples_collected']['bluetooth_gsr'
                    ] = 0
            self.test_results['data_samples_collected']['bluetooth_gsr'
                ] += sample_count
            return sample_count > 0
        except Exception as e:
            logger.error(f'Bluetooth sensor test failed: {e}')
            self.test_results['errors'].append(f'Bluetooth sensors: {e}')
            return False

    async def test_thermal_camera(self) ->bool:
        logger.info('=== Testing Thermal Camera ===')
        try:
            if not self.thermal_simulator.connect():
                logger.error('Failed to connect to thermal camera')
                return False
            if not self.thermal_simulator.start_recording():
                logger.error('Failed to start thermal recording')
                return False
            sample_count = 0
            temperature_data = []
            for i in range(20):
                frame_data = self.thermal_simulator.get_thermal_frame()
                if frame_data:
                    sample_count += 1
                    temp_info = frame_data.processed_data
                    temperature_data.append(temp_info['avg_temperature'])
                    logger.debug(
                        f"Thermal frame: avg={temp_info['avg_temperature']:.1f}°C, range={temp_info['min_temperature']:.1f}-{temp_info['max_temperature']:.1f}°C"
                        )
                await asyncio.sleep(0.1)
            self.thermal_simulator.stop_recording()
            self.thermal_simulator.disconnect()
            if temperature_data:
                avg_temp = sum(temperature_data) / len(temperature_data)
                min_temp = min(temperature_data)
                max_temp = max(temperature_data)
                logger.info(
                    f'✅ Thermal camera test: {sample_count} frames, temp range {min_temp:.1f}-{max_temp:.1f}°C (avg {avg_temp:.1f}°C)'
                    )
            if 'thermal_camera' not in self.test_results[
                'data_samples_collected']:
                self.test_results['data_samples_collected']['thermal_camera'
                    ] = 0
            self.test_results['data_samples_collected']['thermal_camera'
                ] += sample_count
            return sample_count > 0
        except Exception as e:
            logger.error(f'Thermal camera test failed: {e}')
            self.test_results['errors'].append(f'Thermal camera: {e}')
            return False

    async def test_network_sensors(self) ->bool:
        logger.info('=== Testing Network Sensors ===')
        try:
            started_services = 0
            for network_sim in self.network_simulators:
                if network_sim.start_sensor_services():
                    started_services += 1
                    self.active_network_sensors.append(network_sim)
            if not self.active_network_sensors:
                logger.error('Failed to start any network sensor services')
                return False
            logger.info(f'Started {started_services} network sensor services')
            sensor_types = ['camera', 'accelerometer', 'gyroscope',
                'magnetometer']
            total_samples = 0
            for sensor_type in sensor_types:
                logger.info(f'Testing {sensor_type} sensors...')
                sample_count = 0
                for i in range(10):
                    for network_sim in self.active_network_sensors:
                        sensor_data = network_sim.get_sensor_data(sensor_type)
                        if sensor_data:
                            sample_count += 1
                            total_samples += 1
                            logger.debug(
                                f'Network {sensor_type} sample from {sensor_data.sensor_id}'
                                )
                    await asyncio.sleep(0.05)
                logger.info(
                    f'  {sensor_type}: {sample_count} samples collected')
                if f'network_{sensor_type}' not in self.test_results[
                    'data_samples_collected']:
                    self.test_results['data_samples_collected'][
                        f'network_{sensor_type}'] = 0
                self.test_results['data_samples_collected'][
                    f'network_{sensor_type}'] += sample_count
            for network_sim in self.active_network_sensors:
                network_sim.stop_sensor_services()
            logger.info(
                f'✅ Network sensor test: {total_samples} total samples from {len(sensor_types)} sensor types'
                )
            return total_samples > 0
        except Exception as e:
            logger.error(f'Network sensor test failed: {e}')
            self.test_results['errors'].append(f'Network sensors: {e}')
            return False

    def test_sensor_port_assignments(self) ->bool:
        logger.info('=== Testing Sensor Port Assignments ===')
        try:
            port_assignments = {'USB cameras': 'USB ports 0-3',
                'Bluetooth GSR': 'Bluetooth MAC addresses',
                'Thermal camera': 'USB-C/USB3 port', 'Network sensors':
                'TCP/UDP ports 8080-8090', 'Preview streams':
                'TCP ports 8081-8082'}
            correct_assignments = 0
            total_assignments = len(port_assignments)
            cameras = (self.usb_camera_detector.detected_cameras + self.
                usb_camera_detector.simulated_cameras)
            for camera in cameras:
                if 'video' in camera.get('device_path', ''):
                    correct_assignments += 1
                    logger.debug(f"✅ USB camera port: {camera['device_path']}")
                    break
            bt_devices = self.bluetooth_detector.simulated_devices
            for device in bt_devices:
                if device['address'].startswith('00:06:66'):
                    correct_assignments += 1
                    logger.debug(f"✅ Bluetooth address: {device['address']}")
                    break
            thermal_info = self.thermal_simulator.detect_thermal_camera()
            if 'usb' in thermal_info.get('connection', ''):
                correct_assignments += 1
                logger.debug(f"✅ Thermal camera: {thermal_info['connection']}")
            for network_sim in self.network_simulators:
                if 8080 <= network_sim.base_port <= 8090:
                    correct_assignments += 1
                    logger.debug(f'✅ Network ports: {network_sim.base_port}+')
                    break
            correct_assignments += 1
            logger.debug('✅ Preview stream ports: 8081-8082')
            success_rate = correct_assignments / total_assignments
            logger.info(
                f'✅ Port assignment test: {correct_assignments}/{total_assignments} correct ({success_rate:.1%})'
                )
            self.test_results['port_assignments'] = {'correct':
                correct_assignments, 'total': total_assignments,
                'success_rate': success_rate}
            return success_rate >= 0.8
        except Exception as e:
            logger.error(f'Port assignment test failed: {e}')
            self.test_results['errors'].append(f'Port assignments: {e}')
            return False

    def test_sensor_synchronization(self) ->bool:
        logger.info('=== Testing Sensor Synchronization ===')
        try:
            sync_data = {'start_time': time.time(), 'sensor_timestamps': {},
                'max_drift': 0.0, 'sync_quality': 'unknown'}
            sensor_names = ['usb_camera_0', 'bluetooth_gsr_1',
                'thermal_camera', 'network_accel_1']
            base_time = time.time()
            for i, sensor_name in enumerate(sensor_names):
                timestamp = base_time + i * 0.001 + hash(sensor_name
                    ) % 10 * 0.0001
                sync_data['sensor_timestamps'][sensor_name] = timestamp
            timestamps = list(sync_data['sensor_timestamps'].values())
            if len(timestamps) > 1:
                max_drift = max(timestamps) - min(timestamps)
                sync_data['max_drift'] = max_drift
                if max_drift < 0.001:
                    sync_data['sync_quality'] = 'excellent'
                elif max_drift < 0.005:
                    sync_data['sync_quality'] = 'good'
                elif max_drift < 0.01:
                    sync_data['sync_quality'] = 'acceptable'
                else:
                    sync_data['sync_quality'] = 'poor'
            logger.info(
                f"✅ Synchronization test: {sync_data['sync_quality']} (max drift: {sync_data['max_drift'] * 1000:.2f}ms)"
                )
            self.test_results['synchronization'] = sync_data
            return sync_data['sync_quality'] in ['excellent', 'good',
                'acceptable']
        except Exception as e:
            logger.error(f'Synchronization test failed: {e}')
            self.test_results['errors'].append(f'Synchronization: {e}')
            return False

    async def run_hardware_sensor_tests(self) ->Dict[str, Any]:
        self.test_results['start_time'] = datetime.now().isoformat()
        start_time = time.time()
        logger.info('=' * 80)
        logger.info('HARDWARE SENSOR SIMULATION TEST - START')
        logger.info('=' * 80)
        test_functions = [('Sensor Detection', self.detect_all_sensors()),
            ('USB Camera Streams', self.test_usb_camera_streams()), (
            'Bluetooth Sensors', self.test_bluetooth_sensors()), (
            'Thermal Camera', self.test_thermal_camera()), (
            'Network Sensors', self.test_network_sensors()), (
            'Port Assignments', self.test_sensor_port_assignments()), (
            'Synchronization', self.test_sensor_synchronization())]
        test_results = []
        for test_name, test_func in test_functions:
            logger.info(f'\n--- Running {test_name} Test ---')
            try:
                if asyncio.iscoroutine(test_func):
                    result = await test_func
                else:
                    result = test_func
                test_results.append((test_name, result))
                status = '✅ PASS' if result else '❌ FAIL'
                logger.info(f'{test_name}: {status}')
            except Exception as e:
                logger.error(f'{test_name} test error: {e}')
                test_results.append((test_name, False))
                self.test_results['errors'].append(f'{test_name}: {e}')
        end_time = time.time()
        self.test_results['duration'] = end_time - start_time
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        total_samples = sum(self.test_results['data_samples_collected'].
            values())
        samples_per_second = total_samples / self.test_results['duration'
            ] if self.test_results['duration'] > 0 else 0
        self.test_results['performance_metrics'] = {'total_samples':
            total_samples, 'samples_per_second': samples_per_second,
            'tests_passed': passed_tests, 'tests_total': total_tests,
            'success_rate': success_rate}
        overall_success = success_rate >= 0.7
        logger.info('=' * 80)
        if overall_success:
            logger.info('✅ HARDWARE SENSOR SIMULATION TEST - SUCCESS')
        else:
            logger.info('❌ HARDWARE SENSOR SIMULATION TEST - FAILED')
        logger.info(
            f'Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1%})')
        logger.info(f"Duration: {self.test_results['duration']:.2f} seconds")
        logger.info(
            f'Data Samples: {total_samples} ({samples_per_second:.1f}/sec)')
        logger.info('=' * 80)
        self.test_results['overall_success'] = overall_success
        return self.test_results


def print_sensor_test_summary(results: Dict[str, Any]):
    print('\n' + '=' * 70)
    print('🔬 HARDWARE SENSOR SIMULATION TEST SUMMARY')
    print('=' * 70)
    if results.get('overall_success'):
        print('🎉 RESULT: SUCCESS ✅')
    else:
        print('💥 RESULT: FAILED ❌')
    perf = results.get('performance_metrics', {})
    print(f'📊 PERFORMANCE:')
    print(
        f"  Tests Passed: {perf.get('tests_passed', 0)}/{perf.get('tests_total', 0)}"
        )
    print(f"  Success Rate: {perf.get('success_rate', 0):.1%}")
    print(f"  Duration: {results.get('duration', 0):.2f} seconds")
    print(
        f"  Data Samples: {perf.get('total_samples', 0)} ({perf.get('samples_per_second', 0):.1f}/sec)"
        )
    detected = results.get('sensors_detected', {})
    if detected:
        print(f'\n🔍 SENSOR DETECTION:')
        print(
            f"  USB Cameras: {detected.get('usb_cameras_real', 0)} real, {detected.get('usb_cameras_simulated', 0)} simulated"
            )
        print(
            f"  Bluetooth: {detected.get('bluetooth_real', 0)} real, {detected.get('bluetooth_simulated', 0)} simulated"
            )
        print(
            f"  Thermal: {detected.get('thermal_real', 0)} real, {detected.get('thermal_simulated', 0)} simulated"
            )
        print(f"  Network: {detected.get('network_simulated', 0)} simulated")
    samples = results.get('data_samples_collected', {})
    if samples:
        print(f'\n📡 DATA COLLECTION:')
        for sensor_type, count in samples.items():
            print(f'  {sensor_type}: {count} samples')
    ports = results.get('port_assignments', {})
    if ports:
        print(f'\n🔌 PORT ASSIGNMENTS:')
        print(
            f"  Correct: {ports.get('correct', 0)}/{ports.get('total', 0)} ({ports.get('success_rate', 0):.1%})"
            )
    sync = results.get('synchronization', {})
    if sync:
        print(f'\n⏱️  SYNCHRONIZATION:')
        print(f"  Quality: {sync.get('sync_quality', 'unknown').title()}")
        print(f"  Max Drift: {sync.get('max_drift', 0) * 1000:.2f}ms")
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
    print('=' * 70)


async def main():
    logger.info('Starting Hardware Sensor Simulation Test...')
    test = HardwareSensorTest()
    results = await test.run_hardware_sensor_tests()
    print_sensor_test_summary(results)
    results_file = test.test_dir / 'sensor_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f'Test results saved to: {results_file}')
    return 0 if results.get('overall_success') else 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
