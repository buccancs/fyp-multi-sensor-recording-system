#!/usr/bin/env python3
"""
Comprehensive Network Module Tests
==================================

This module provides comprehensive unit tests for all network-related
functionality in the PythonApp.

Test coverage:
- Device Server: JSON socket communication, device management
- Device Client: Connection handling, message processing
- Android Device Manager: Device discovery, coordination
- PC Server: Multi-device coordination, data aggregation
- Enhanced Device Server: Advanced features, performance optimization

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import asyncio
import json
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from network.device_server import JsonSocketServer, RemoteDevice, create_command_message
    from network.device_client import DeviceClient
    from network.android_device_manager import AndroidDeviceManager
    from network.pc_server import PCServer, HelloMessage, SensorDataMessage, StatusMessage
    from network.enhanced_device_server import (
        EnhancedDeviceServer, EnhancedRemoteDevice, NetworkMessage, MessagePriority
    )
    NETWORK_MODULES_AVAILABLE = True
except ImportError as e:
    NETWORK_MODULES_AVAILABLE = False
    print(f"Warning: Network modules not available: {e}")

try:
    from session.session_manager import SessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False


class TestRemoteDevice(unittest.TestCase):
    """Test RemoteDevice data structure and functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_socket = Mock()
        self.mock_socket.getpeername.return_value = ('192.168.1.100', 12345)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_remote_device_creation(self):
        """Test RemoteDevice creation and initialization."""
        device = RemoteDevice(
            socket=self.mock_socket,
            device_id="test_device_001",
            device_type="android",
            capabilities=["camera", "sensors", "gsr"]
        )
        
        self.assertEqual(device.device_id, "test_device_001")
        self.assertEqual(device.device_type, "android")
        self.assertEqual(device.capabilities, ["camera", "sensors", "gsr"])
        self.assertIsNotNone(device.connected_at)
        self.assertTrue(device.is_connected)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_remote_device_status_tracking(self):
        """Test RemoteDevice status and health tracking."""
        device = RemoteDevice(socket=self.mock_socket, device_id="test_device")
        
        # Test initial status
        self.assertTrue(device.is_connected)
        self.assertEqual(device.status, "connected")
        
        # Test status updates
        device.update_status("recording")
        self.assertEqual(device.status, "recording")
        
        # Test last seen timestamp
        initial_last_seen = device.last_seen
        time.sleep(0.01)
        device.update_last_seen()
        self.assertGreater(device.last_seen, initial_last_seen)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_remote_device_metrics(self):
        """Test RemoteDevice performance and health metrics."""
        device = RemoteDevice(socket=self.mock_socket, device_id="test_device")
        
        # Test message counting
        initial_count = device.messages_received
        device.increment_message_count()
        self.assertEqual(device.messages_received, initial_count + 1)
        
        # Test throughput calculation
        device.update_throughput(1024)  # 1KB
        self.assertGreater(device.bytes_received, 0)
        
        # Test health check
        health = device.get_health_status()
        self.assertIsInstance(health, dict)
        self.assertIn('is_connected', health)
        self.assertIn('last_seen_delta', health)
        self.assertIn('messages_received', health)


class TestJsonSocketServer(unittest.TestCase):
    """Test JsonSocketServer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_port = 9999  # Use high port to avoid conflicts

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_json_socket_server_initialization(self):
        """Test JsonSocketServer initialization."""
        if SESSION_MANAGER_AVAILABLE:
            session_manager = Mock()
            server = JsonSocketServer(port=self.test_port, session_manager=session_manager)
            self.assertEqual(server.port, self.test_port)
            self.assertEqual(server.session_manager, session_manager)
        else:
            server = JsonSocketServer(port=self.test_port)
            self.assertEqual(server.port, self.test_port)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_message_creation_and_validation(self):
        """Test JSON message creation and validation."""
        # Test command message creation
        command_msg = create_command_message("start_recording", {"duration": 30})
        
        self.assertIsInstance(command_msg, dict)
        self.assertEqual(command_msg["type"], "command")
        self.assertEqual(command_msg["command"], "start_recording")
        self.assertEqual(command_msg["parameters"]["duration"], 30)
        self.assertIn("timestamp", command_msg)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    @patch('socket.socket')
    def test_server_socket_setup(self, mock_socket_class):
        """Test server socket setup and configuration."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        server = JsonSocketServer(port=self.test_port)
        server.setup_server_socket()
        
        # Verify socket configuration
        mock_socket.setsockopt.assert_called()
        mock_socket.bind.assert_called_with(('', self.test_port))
        mock_socket.listen.assert_called()

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_device_registration_and_management(self):
        """Test device registration and management."""
        server = JsonSocketServer(port=self.test_port)
        
        # Mock device registration
        mock_socket = Mock()
        mock_socket.getpeername.return_value = ('192.168.1.100', 12345)
        
        device = RemoteDevice(
            socket=mock_socket,
            device_id="test_android_001",
            device_type="android"
        )
        
        # Test device registration
        server.register_device(device)
        self.assertIn("test_android_001", server.connected_devices)
        self.assertEqual(server.connected_devices["test_android_001"], device)
        
        # Test device retrieval
        retrieved_device = server.get_device("test_android_001")
        self.assertEqual(retrieved_device, device)
        
        # Test device removal
        server.unregister_device("test_android_001")
        self.assertNotIn("test_android_001", server.connected_devices)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_message_broadcasting(self):
        """Test message broadcasting to multiple devices."""
        server = JsonSocketServer(port=self.test_port)
        
        # Create mock devices
        devices = []
        for i in range(3):
            mock_socket = Mock()
            mock_socket.getpeername.return_value = (f'192.168.1.{100+i}', 12345)
            
            device = RemoteDevice(
                socket=mock_socket,
                device_id=f"device_{i:03d}",
                device_type="android"
            )
            devices.append(device)
            server.register_device(device)
        
        # Test broadcast message
        broadcast_msg = create_command_message("sync_clocks", {"timestamp": time.time()})
        
        with patch.object(server, 'send_message_to_device') as mock_send:
            server.broadcast_message(broadcast_msg)
            
            # Verify message sent to all devices
            self.assertEqual(mock_send.call_count, 3)
            for device in devices:
                mock_send.assert_any_call(device.device_id, broadcast_msg)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_session_file_collection(self):
        """Test session file collection functionality."""
        if not SESSION_MANAGER_AVAILABLE:
            self.skipTest("SessionManager not available")
            
        mock_session_manager = Mock()
        mock_session_manager.get_current_session_directory.return_value = str(self.test_dir)
        
        server = JsonSocketServer(port=self.test_port, session_manager=mock_session_manager)
        
        # Create mock device
        mock_socket = Mock()
        mock_socket.getpeername.return_value = ('192.168.1.100', 12345)
        
        device = RemoteDevice(socket=mock_socket, device_id="test_device")
        server.register_device(device)
        
        # Test file collection request
        with patch.object(server, 'send_message_to_device') as mock_send:
            collected_count = server.request_all_session_files("test_session_123")
            
            # Verify file collection message sent
            mock_send.assert_called()
            call_args = mock_send.call_args[0]
            self.assertEqual(call_args[0], "test_device")  # device_id
            self.assertEqual(call_args[1]["type"], "command")
            self.assertEqual(call_args[1]["command"], "send_session_files")


class TestDeviceClient(unittest.TestCase):
    """Test DeviceClient functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_host = "127.0.0.1"
        self.test_port = 9998

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_device_client_initialization(self):
        """Test DeviceClient initialization."""
        client = DeviceClient(
            device_id="client_test_001",
            device_type="android",
            host=self.test_host,
            port=self.test_port
        )
        
        self.assertEqual(client.device_id, "client_test_001")
        self.assertEqual(client.device_type, "android")
        self.assertEqual(client.host, self.test_host)
        self.assertEqual(client.port, self.test_port)
        self.assertFalse(client.is_connected)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    @patch('socket.socket')
    def test_client_connection(self, mock_socket_class):
        """Test client connection to server."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = DeviceClient(
            device_id="client_test_001",
            device_type="android",
            host=self.test_host,
            port=self.test_port
        )
        
        # Mock successful connection
        mock_socket.connect.return_value = None
        
        # Test connection
        result = client.connect()
        
        self.assertTrue(result)
        mock_socket.connect.assert_called_with((self.test_host, self.test_port))

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_message_sending(self):
        """Test message sending functionality."""
        client = DeviceClient(device_id="client_test_001", device_type="android")
        
        # Mock connected state
        client.socket = Mock()
        client.is_connected = True
        
        # Test message sending
        test_message = {"type": "sensor_data", "gsr": 1000, "timestamp": time.time()}
        
        result = client.send_message(test_message)
        self.assertTrue(result)
        
        # Verify socket send was called
        client.socket.send.assert_called()

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_message_receiving(self):
        """Test message receiving and processing."""
        client = DeviceClient(device_id="client_test_001", device_type="android")
        
        # Mock connected state and socket
        client.socket = Mock()
        client.is_connected = True
        
        # Mock received data
        test_message = {"type": "command", "command": "start_recording"}
        json_data = json.dumps(test_message).encode('utf-8')
        length_header = f"{len(json_data):010d}".encode('utf-8')
        
        client.socket.recv.side_effect = [length_header, json_data]
        
        # Test message receiving
        received_message = client.receive_message()
        
        self.assertIsNotNone(received_message)
        self.assertEqual(received_message["type"], "command")
        self.assertEqual(received_message["command"], "start_recording")

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_hello_message_sending(self):
        """Test hello message sending during connection."""
        client = DeviceClient(
            device_id="client_test_001",
            device_type="android",
            capabilities=["camera", "gsr", "thermal"]
        )
        
        # Mock connected state
        client.socket = Mock()
        client.is_connected = True
        
        # Test hello message
        with patch.object(client, 'send_message') as mock_send:
            client.send_hello_message()
            
            # Verify hello message format
            mock_send.assert_called_once()
            hello_msg = mock_send.call_args[0][0]
            
            self.assertEqual(hello_msg["type"], "hello")
            self.assertEqual(hello_msg["device_id"], "client_test_001")
            self.assertEqual(hello_msg["device_type"], "android")
            self.assertEqual(hello_msg["capabilities"], ["camera", "gsr", "thermal"])


class TestPCServer(unittest.TestCase):
    """Test PCServer multi-device coordination functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_port = 9997

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_pc_server_initialization(self):
        """Test PCServer initialization."""
        server = PCServer(port=self.test_port)
        
        self.assertEqual(server.port, self.test_port)
        self.assertIsInstance(server.connected_devices, dict)
        self.assertIsInstance(server.device_status, dict)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_hello_message_processing(self):
        """Test hello message processing and device registration."""
        server = PCServer(port=self.test_port)
        
        # Create hello message
        hello_msg = HelloMessage(
            device_id="android_001",
            device_type="android",
            capabilities=["camera", "gsr"],
            version="1.0.0"
        )
        
        # Mock socket
        mock_socket = Mock()
        mock_socket.getpeername.return_value = ('192.168.1.100', 12345)
        
        # Process hello message
        with patch.object(server, 'register_device') as mock_register:
            server.process_hello_message(hello_msg.to_dict(), mock_socket)
            
            # Verify device registration
            mock_register.assert_called_once()

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available") 
    def test_sensor_data_aggregation(self):
        """Test sensor data collection and aggregation."""
        server = PCServer(port=self.test_port)
        
        # Register mock devices
        devices = []
        for i in range(2):
            mock_socket = Mock()
            mock_socket.getpeername.return_value = (f'192.168.1.{100+i}', 12345)
            
            device = RemoteDevice(
                socket=mock_socket,
                device_id=f"device_{i:03d}",
                device_type="android"
            )
            devices.append(device)
            server.register_device(device)
        
        # Create sensor data messages
        sensor_data = []
        for i, device in enumerate(devices):
            data_msg = SensorDataMessage(
                device_id=device.device_id,
                timestamp=time.time(),
                gsr=1000 + i * 10,
                ppg=2000 + i * 20,
                accelerometer=[0.1, 0.2, 0.9]
            )
            sensor_data.append(data_msg)
        
        # Process sensor data
        for data_msg in sensor_data:
            server.process_sensor_data(data_msg.to_dict())
        
        # Verify data aggregation
        aggregated_data = server.get_aggregated_sensor_data()
        self.assertIsInstance(aggregated_data, dict)
        self.assertEqual(len(aggregated_data), 2)  # Two devices

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_synchronization_commands(self):
        """Test synchronization command distribution."""
        server = PCServer(port=self.test_port)
        
        # Register mock devices
        mock_devices = []
        for i in range(3):
            mock_socket = Mock()
            device = RemoteDevice(
                socket=mock_socket,
                device_id=f"sync_device_{i:03d}",
                device_type="android"
            )
            mock_devices.append(device)
            server.register_device(device)
        
        # Test synchronization command
        with patch.object(server, 'broadcast_message') as mock_broadcast:
            server.broadcast_sync_command("start_recording", {"session_id": "test_123"})
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
            
            # Verify message format
            call_args = mock_broadcast.call_args[0][0]
            self.assertEqual(call_args["type"], "command")
            self.assertEqual(call_args["command"], "start_recording")
            self.assertEqual(call_args["parameters"]["session_id"], "test_123")


class TestEnhancedDeviceServer(unittest.TestCase):
    """Test EnhancedDeviceServer advanced functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_port = 9996

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_enhanced_device_server_initialization(self):
        """Test EnhancedDeviceServer initialization."""
        server = EnhancedDeviceServer(port=self.test_port)
        
        self.assertEqual(server.port, self.test_port)
        self.assertIsNotNone(server.message_queue)
        self.assertIsNotNone(server.priority_queue)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_priority_message_handling(self):
        """Test priority-based message handling."""
        server = EnhancedDeviceServer(port=self.test_port)
        
        # Create messages with different priorities
        low_priority_msg = NetworkMessage(
            content={"type": "status", "message": "Low priority"},
            priority=MessagePriority.LOW,
            device_id="test_device"
        )
        
        high_priority_msg = NetworkMessage(
            content={"type": "emergency", "message": "High priority"},
            priority=MessagePriority.HIGH,
            device_id="test_device"
        )
        
        # Add messages to queue (low priority first)
        server.queue_message(low_priority_msg)
        server.queue_message(high_priority_msg)
        
        # Verify high priority message is processed first
        next_message = server.get_next_priority_message()
        self.assertEqual(next_message.priority, MessagePriority.HIGH)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_connection_resilience(self):
        """Test connection resilience and recovery."""
        server = EnhancedDeviceServer(port=self.test_port)
        
        # Create enhanced remote device
        mock_socket = Mock()
        mock_socket.getpeername.return_value = ('192.168.1.100', 12345)
        
        device = EnhancedRemoteDevice(
            socket=mock_socket,
            device_id="resilient_device",
            device_type="android"
        )
        
        # Test connection health monitoring
        initial_health = device.get_connection_health()
        self.assertIsInstance(initial_health, dict)
        self.assertIn('connection_quality', initial_health)
        
        # Simulate connection issues
        device.record_connection_issue("timeout")
        device.record_connection_issue("packet_loss")
        
        # Verify issue tracking
        health_after_issues = device.get_connection_health()
        self.assertGreater(len(device.connection_issues), 0)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_performance_monitoring(self):
        """Test performance monitoring and metrics collection."""
        server = EnhancedDeviceServer(port=self.test_port)
        
        # Simulate message processing
        for i in range(10):
            start_time = time.time()
            
            # Simulate processing delay
            time.sleep(0.001)
            
            processing_time = time.time() - start_time
            server.record_message_processing_time(processing_time)
        
        # Get performance metrics
        metrics = server.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('average_processing_time', metrics)
        self.assertIn('messages_processed', metrics)
        self.assertIn('total_processing_time', metrics)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_load_balancing(self):
        """Test load balancing across multiple devices."""
        server = EnhancedDeviceServer(port=self.test_port)
        
        # Register multiple devices
        devices = []
        for i in range(4):
            mock_socket = Mock()
            device = EnhancedRemoteDevice(
                socket=mock_socket,
                device_id=f"load_device_{i:03d}",
                device_type="android"
            )
            devices.append(device)
            server.register_device(device)
        
        # Simulate varying loads
        for i, device in enumerate(devices):
            # Different load levels
            device.current_load = i * 25  # 0%, 25%, 50%, 75%
        
        # Test load balancing decision
        least_loaded_device = server.get_least_loaded_device()
        self.assertEqual(least_loaded_device.device_id, "load_device_000")


class TestNetworkIntegration(unittest.TestCase):
    """Test network module integration scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_client_server_communication(self):
        """Test complete client-server communication flow."""
        # This would require actual socket communication
        # For unit tests, we use mocks to verify the interface
        
        server_port = 9995
        server = JsonSocketServer(port=server_port)
        
        client = DeviceClient(
            device_id="integration_test_001",
            device_type="android",
            host="127.0.0.1",
            port=server_port
        )
        
        # Mock the actual network calls
        with patch('socket.socket'):
            # Test connection establishment
            self.assertIsNotNone(server)
            self.assertIsNotNone(client)
            
            # Verify proper initialization
            self.assertEqual(server.port, server_port)
            self.assertEqual(client.port, server_port)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_multi_device_coordination(self):
        """Test coordination between multiple devices."""
        server = PCServer(port=9994)
        
        # Simulate multiple device connections
        device_configs = [
            {"id": "android_001", "type": "android", "capabilities": ["camera", "gsr"]},
            {"id": "android_002", "type": "android", "capabilities": ["thermal", "audio"]},
            {"id": "desktop_001", "type": "desktop", "capabilities": ["processing", "storage"]}
        ]
        
        # Register devices
        for config in device_configs:
            mock_socket = Mock()
            mock_socket.getpeername.return_value = ('192.168.1.100', 12345)
            
            device = RemoteDevice(
                socket=mock_socket,
                device_id=config["id"],
                device_type=config["type"],
                capabilities=config["capabilities"]
            )
            server.register_device(device)
        
        # Verify all devices registered
        self.assertEqual(len(server.connected_devices), 3)
        
        # Test coordinated command distribution
        with patch.object(server, 'send_message_to_device') as mock_send:
            server.coordinate_recording_start("session_123")
            
            # Verify command sent to all devices
            self.assertEqual(mock_send.call_count, 3)

    @unittest.skipUnless(NETWORK_MODULES_AVAILABLE, "Network modules not available")
    def test_error_handling_and_recovery(self):
        """Test network error handling and recovery mechanisms."""
        server = JsonSocketServer(port=9993)
        
        # Test handling of malformed messages
        malformed_messages = [
            b"invalid json data",
            b'{"incomplete": json',
            b'{"type": "unknown_type"}',
            b''  # Empty message
        ]
        
        for bad_message in malformed_messages:
            # This should not raise exceptions
            try:
                # In real implementation, this would parse the message
                result = server.handle_malformed_message(bad_message)
                # Should return error response or handle gracefully
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Server should handle malformed message gracefully: {e}")


def run_network_tests():
    """Run all network tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestRemoteDevice,
        TestJsonSocketServer,
        TestDeviceClient,
        TestPCServer,
        TestEnhancedDeviceServer,
        TestNetworkIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("COMPREHENSIVE NETWORK MODULE TESTS")
    print("=" * 70)
    
    if not NETWORK_MODULES_AVAILABLE:
        print("❌ Network modules not available - skipping tests")
        exit(1)
    
    success = run_network_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL NETWORK TESTS PASSED")
        exit(0)
    else:
        print("❌ SOME NETWORK TESTS FAILED")
        exit(1)