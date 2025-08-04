import asyncio
import json
import logging
import socket
import struct
import sys
import time
import threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from network.pc_server import PCServer, HelloMessage, SensorDataMessage, StatusMessage
from network.android_device_manager import AndroidDeviceManager
from shimmer_manager import ShimmerManager


class MockAndroidDevice:

    def __init__(self, device_id: str, server_host: str='localhost',
        server_port: int=9000):
        self.device_id = device_id
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.is_connected = False
        self.is_running = False

    def connect(self) ->bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.is_connected = True
            hello_msg = HelloMessage(device_id=self.device_id, capabilities
                =['rgb_video', 'thermal', 'shimmer'])
            self._send_message(hello_msg)
            return True
        except Exception as e:
            print(f'Failed to connect mock device {self.device_id}: {e}')
            return False

    def start_simulation(self):
        self.is_running = True
        thread = threading.Thread(target=self._simulation_loop, daemon=True)
        thread.start()

    def stop_simulation(self):
        self.is_running = False

    def disconnect(self):
        self.is_running = False
        self.is_connected = False
        if self.socket:
            self.socket.close()

    def _send_message(self, message):
        if not self.socket or not self.is_connected:
            return
        try:
            json_data = message.to_json()
            json_bytes = json_data.encode('utf-8')
            length_header = struct.pack('>I', len(json_bytes))
            self.socket.sendall(length_header + json_bytes)
        except Exception as e:
            print(f'Error sending message from {self.device_id}: {e}')

    def _simulation_loop(self):
        sample_count = 0
        while self.is_running and self.is_connected:
            try:
                sensor_data = SensorDataMessage(values={'gsr_conductance': 
                    2.5 + 0.5 * (sample_count % 10), 'ppg_a13': 2048 + 100 *
                    (sample_count % 20), 'accel_x': 0.1 * (sample_count % 5
                    ), 'accel_y': 0.1 * (sample_count % 7), 'accel_z': 9.8 +
                    0.1 * (sample_count % 3), 'battery_percentage': 85 - 
                    sample_count // 100})
                self._send_message(sensor_data)
                if sample_count % 10 == 0:
                    status_msg = StatusMessage(battery=85 - sample_count //
                        100, temperature=32.5 + 0.5 * (sample_count % 6),
                        recording=True, connected=True)
                    self._send_message(status_msg)
                sample_count += 1
                time.sleep(0.1)
            except Exception as e:
                print(f'Error in simulation loop for {self.device_id}: {e}')
                break


def test_pc_server():
    print('=== Testing PC Server ===')
    messages_received = []
    devices_connected = []

    def on_message(device_id, message):
        messages_received.append((device_id, message.type))
        print(f'Received {message.type} from {device_id}')

    def on_device_connected(device_id, device):
        devices_connected.append(device_id)
        print(
            f'Device connected: {device_id} with capabilities: {device.capabilities}'
            )

    def on_device_disconnected(device_id):
        print(f'Device disconnected: {device_id}')
    server = PCServer(port=9001)
    server.add_message_callback(on_message)
    server.add_device_callback(on_device_connected)
    server.add_disconnect_callback(on_device_disconnected)
    if not server.start():
        print('❌ Failed to start PC server')
        return False
    try:
        mock_device = MockAndroidDevice('test_device_001', server_port=9001)
        if not mock_device.connect():
            print('❌ Mock device failed to connect')
            return False
        time.sleep(0.5)
        if 'test_device_001' not in devices_connected:
            print('❌ Device not registered with server')
            return False
        mock_device.start_simulation()
        time.sleep(3)
        if len(messages_received) < 10:
            print(f'❌ Expected more messages, got {len(messages_received)}')
            return False
        message_types = set(msg_type for _, msg_type in messages_received)
        expected_types = {'sensor_data', 'status'}
        if not expected_types.issubset(message_types):
            print(f'❌ Missing expected message types. Got: {message_types}')
            return False
        mock_device.disconnect()
        print('✅ PC Server test passed')
        return True
    finally:
        server.stop()


def test_android_device_manager():
    print('\n=== Testing Android Device Manager ===')
    data_samples_received = []
    status_updates = []

    def on_data(sample):
        data_samples_received.append(sample)
        if len(data_samples_received) % 10 == 0:
            print(f'Received {len(data_samples_received)} data samples')

    def on_status(device_id, device):
        status_updates.append((device_id, device))
        print(f'Status update from {device_id}')
    manager = AndroidDeviceManager(server_port=9002)
    manager.add_data_callback(on_data)
    manager.add_status_callback(on_status)
    if not manager.initialize():
        print('❌ Failed to initialize Android Device Manager')
        return False
    try:
        mock_device = MockAndroidDevice('test_android_001', server_port=9002)
        if not mock_device.connect():
            print('❌ Mock device failed to connect')
            return False
        time.sleep(0.5)
        devices = manager.get_connected_devices()
        if 'test_android_001' not in devices:
            print('❌ Device not registered with manager')
            return False
        mock_device.start_simulation()
        session_id = f'test_session_{int(time.time())}'
        if not manager.start_session(session_id, record_shimmer=True):
            print('❌ Failed to start session')
            return False
        time.sleep(3)
        if not manager.stop_session():
            print('❌ Failed to stop session')
            return False
        if len(data_samples_received) < 10:
            print(
                f'❌ Expected more data samples, got {len(data_samples_received)}'
                )
            return False
        mock_device.disconnect()
        print('✅ Android Device Manager test passed')
        return True
    finally:
        manager.shutdown()


def test_shimmer_manager():
    print('\n=== Testing Enhanced Shimmer Manager ===')
    shimmer_samples = []
    status_updates = []

    def on_shimmer_data(sample):
        shimmer_samples.append(sample)
        if len(shimmer_samples) % 10 == 0:
            print(f'Received {len(shimmer_samples)} Shimmer samples')

    def on_status_update(device_id, status):
        status_updates.append((device_id, status))
        print(f'Status update: {device_id} - {status.device_state.value}')
    manager = ShimmerManager(enable_android_integration=True)
    manager.android_server_port = 9003
    manager.add_data_callback(on_shimmer_data)
    manager.add_status_callback(on_status_update)
    if not manager.initialize():
        print('❌ Failed to initialize Enhanced Shimmer Manager')
        return False
    try:
        mock_device = MockAndroidDevice('test_shimmer_android', server_port
            =9003)
        if not mock_device.connect():
            print('❌ Mock device failed to connect')
            return False
        time.sleep(1)
        android_devices = manager.get_android_devices()
        if 'test_shimmer_android' not in android_devices:
            print('❌ Android device not registered')
            return False
        if not manager._connect_android_device('test_shimmer_android'):
            print('❌ Failed to connect Android device')
            return False
        mock_device.start_simulation()
        if not manager.start_streaming():
            print('❌ Failed to start streaming')
            return False
        session_id = f'shimmer_test_{int(time.time())}'
        if not manager.start_recording(session_id):
            print('❌ Failed to start recording')
            return False
        time.sleep(3)
        if not manager.stop_recording():
            print('❌ Failed to stop recording')
            return False
        if not manager.stop_streaming():
            print('❌ Failed to stop streaming')
            return False
        if len(shimmer_samples) < 10:
            print(
                f'❌ Expected more Shimmer samples, got {len(shimmer_samples)}')
            return False
        sample = shimmer_samples[0]
        if not sample.device_id.startswith('android_'):
            print(f'❌ Invalid device ID format: {sample.device_id}')
            return False
        if sample.gsr_conductance is None:
            print('❌ Missing GSR data in sample')
            return False
        mock_device.disconnect()
        print('✅ Enhanced Shimmer Manager test passed')
        return True
    finally:
        manager.cleanup()


def test_integration():
    print('🧪 Starting Shimmer PC Integration Tests\n')
    logging.basicConfig(level=logging.WARNING, format=
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    tests = [('PC Server', test_pc_server), ('Android Device Manager',
        test_android_device_manager), ('Enhanced Shimmer Manager',
        test_shimmer_manager)]
    passed = 0
    failed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f'❌ {test_name} test failed')
        except Exception as e:
            failed += 1
            print(f'❌ {test_name} test failed with exception: {e}')
        time.sleep(1)
    print(f'\n📊 Test Results:')
    print(f'  ✅ Passed: {passed}')
    print(f'  ❌ Failed: {failed}')
    print(f'  📈 Success Rate: {passed / (passed + failed) * 100:.1f}%')
    if failed == 0:
        print(
            '\n🎉 All tests passed! Shimmer PC integration is working correctly.'
            )
        return True
    else:
        print(f'\n⚠️  Some tests failed. Please check the implementation.')
        return False


if __name__ == '__main__':
    success = test_integration()
    sys.exit(0 if success else 1)
