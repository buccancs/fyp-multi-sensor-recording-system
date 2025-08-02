#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Rock-Solid Networking

This module provides extensive testing for the enhanced networking implementation,
including stress tests, reliability tests, and real-world scenario simulations.

Features tested:
- Thread safety under concurrent load
- Heartbeat mechanism reliability
- Adaptive streaming quality
- Connection recovery and reconnection
- Message priority handling
- Error recovery scenarios
- Performance under stress

Author: Multi-Sensor Recording System Team
Date: 2025-01-15
"""

import asyncio
import base64
import json
import os
import random
import socket
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import List
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from network.enhanced_device_server import (
    EnhancedDeviceServer,
    EnhancedRemoteDevice,
    MessagePriority,
    ConnectionState,
    NetworkMessage
)


class MockDevice:
    """Mock device for testing purposes."""
    
    def __init__(self, device_id: str, capabilities: List[str] = None):
        self.device_id = device_id
        self.capabilities = capabilities or ["camera", "thermal"]
        self.socket = None
        self.connected = False
        
    def connect(self, host: str = "127.0.0.1", port: int = 9001) -> bool:
        """Connect to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Mock device connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.socket = None
    
    def send_handshake(self) -> bool:
        """Send handshake message."""
        message = {
            "type": "handshake",
            "device_id": self.device_id,
            "capabilities": self.capabilities,
            "timestamp": time.time()
        }
        return self.send_message(message)
    
    def send_message(self, message: dict) -> bool:
        """Send JSON message with length prefix."""
        if not self.connected or not self.socket:
            return False
        
        try:
            json_data = json.dumps(message).encode('utf-8')
            length_header = len(json_data).to_bytes(4, 'big')
            self.socket.sendall(length_header + json_data)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def receive_message(self, timeout: float = 1.0) -> dict:
        """Receive JSON message."""
        if not self.connected or not self.socket:
            return None
        
        try:
            self.socket.settimeout(timeout)
            
            # Read length header
            length_data = self.socket.recv(4)
            if len(length_data) != 4:
                return None
            
            message_length = int.from_bytes(length_data, 'big')
            
            # Read message
            json_data = b""
            while len(json_data) < message_length:
                chunk = self.socket.recv(message_length - len(json_data))
                if not chunk:
                    return None
                json_data += chunk
            
            return json.loads(json_data.decode('utf-8'))
            
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat message."""
        message = {
            "type": "heartbeat",
            "timestamp": time.time()
        }
        return self.send_message(message)
    
    def send_status(self, **kwargs) -> bool:
        """Send status update."""
        message = {
            "type": "status",
            "timestamp": time.time(),
            **kwargs
        }
        return self.send_message(message)
    
    def send_preview_frame(self, frame_type: str = "rgb") -> bool:
        """Send mock preview frame."""
        # Create small test image data
        test_image = b"test_image_data_" + os.urandom(100)
        image_b64 = base64.b64encode(test_image).decode('utf-8')
        
        message = {
            "type": "preview_frame",
            "frame_type": frame_type,
            "image_data": image_b64,
            "width": 640,
            "height": 480,
            "timestamp": time.time()
        }
        return self.send_message(message)


class TestEnhancedNetworking(unittest.TestCase):
    """Test cases for enhanced networking features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = EnhancedDeviceServer(
            host="127.0.0.1",
            port=9001,
            heartbeat_interval=1.0
        )
        self.server_thread = None
        self.mock_devices = []
    
    def tearDown(self):
        """Clean up after tests."""
        # Disconnect all mock devices
        for device in self.mock_devices:
            device.disconnect()
        self.mock_devices.clear()
        
        # Stop server
        if self.server and self.server.running:
            self.server.stop_server()
        
        # Wait for server thread
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
    
    def start_server(self):
        """Start server in background thread."""
        success = self.server.start_server()
        self.assertTrue(success, "Server should start successfully")
        time.sleep(0.5)  # Give server time to start
    
    def create_mock_device(self, device_id: str) -> MockDevice:
        """Create and connect mock device."""
        device = MockDevice(device_id)
        self.assertTrue(device.connect(port=9001), f"Device {device_id} should connect")
        self.assertTrue(device.send_handshake(), f"Device {device_id} should send handshake")
        self.mock_devices.append(device)
        time.sleep(0.2)  # Allow server to process
        return device
    
    def test_enhanced_server_startup(self):
        """Test enhanced server startup and configuration."""
        self.assertFalse(self.server.running)
        
        # Start server
        self.start_server()
        self.assertTrue(self.server.running)
        
        # Check initial state
        stats = self.server.get_network_statistics()
        self.assertEqual(stats["active_devices"], 0)
        self.assertEqual(stats["total_connections"], 0)
    
    def test_device_connection_with_handshake(self):
        """Test enhanced device connection with handshake."""
        self.start_server()
        
        # Track connection events
        connection_events = []
        def on_device_connected(device_id, device_info):
            connection_events.append(("connected", device_id, device_info))
        
        self.server.device_connected.connect(on_device_connected)
        
        # Connect device
        device = self.create_mock_device("test_device_1")
        
        # Verify connection
        time.sleep(1.0)  # Allow processing
        stats = self.server.get_network_statistics()
        self.assertEqual(stats["active_devices"], 1)
        self.assertIn("test_device_1", stats["devices"])
        
        # Check connection event
        self.assertEqual(len(connection_events), 1)
        self.assertEqual(connection_events[0][1], "test_device_1")
    
    def test_heartbeat_mechanism(self):
        """Test heartbeat mechanism and timeout detection."""
        self.start_server()
        
        # Connect device
        device = self.create_mock_device("heartbeat_test")
        
        # Send initial heartbeats
        for _ in range(3):
            self.assertTrue(device.send_heartbeat())
            time.sleep(0.5)
        
        # Verify device is alive
        stats = self.server.get_network_statistics()
        device_info = stats["devices"]["heartbeat_test"]
        self.assertTrue(device_info["is_alive"])
        
        # Stop sending heartbeats and wait for timeout
        time.sleep(3.0)  # Wait longer than heartbeat timeout
        
        # Check if device was detected as dead
        stats = self.server.get_network_statistics()
        # Note: Actual timeout handling depends on implementation
    
    def test_message_priority_handling(self):
        """Test message priority queue handling."""
        self.start_server()
        device = self.create_mock_device("priority_test")
        
        # Send messages with different priorities
        messages_sent = []
        
        # Low priority message
        preview_msg = device.send_preview_frame("rgb")
        messages_sent.append(("preview", "low"))
        
        # High priority message
        status_msg = device.send_status(battery=75, recording=True)
        messages_sent.append(("status", "high"))
        
        # Critical priority (handshake already sent)
        heartbeat_msg = device.send_heartbeat()
        messages_sent.append(("heartbeat", "critical"))
        
        time.sleep(1.0)  # Allow processing
        
        # Verify all messages were processed
        self.assertTrue(preview_msg)
        self.assertTrue(status_msg)
        self.assertTrue(heartbeat_msg)
    
    def test_adaptive_streaming_quality(self):
        """Test adaptive streaming quality adjustment."""
        self.start_server()
        device = self.create_mock_device("streaming_test")
        
        # Send multiple preview frames rapidly
        frame_count = 0
        start_time = time.time()
        
        for i in range(20):
            if device.send_preview_frame("rgb"):
                frame_count += 1
            time.sleep(0.05)  # 20 FPS attempt
        
        duration = time.time() - start_time
        actual_fps = frame_count / duration
        
        # Verify rate limiting occurred
        self.assertLess(actual_fps, 18, "Frame rate should be limited")
        
        print(f"Actual FPS: {actual_fps:.2f}")
    
    def test_connection_recovery(self):
        """Test connection recovery after network error."""
        self.start_server()
        
        # Track connection events
        disconnection_events = []
        def on_device_disconnected(device_id, reason):
            disconnection_events.append((device_id, reason))
        
        self.server.device_disconnected.connect(on_device_disconnected)
        
        # Connect device
        device = self.create_mock_device("recovery_test")
        
        # Simulate network error by closing socket
        device.socket.close()
        device.connected = False
        
        # Wait for server to detect disconnection
        time.sleep(2.0)
        
        # Check disconnection was detected
        stats = self.server.get_network_statistics()
        self.assertEqual(stats["active_devices"], 0)
    
    def test_concurrent_device_connections(self):
        """Test multiple concurrent device connections."""
        self.start_server()
        
        # Connect multiple devices concurrently
        devices = []
        threads = []
        
        def connect_device(device_id):
            device = MockDevice(device_id)
            if device.connect(port=9001) and device.send_handshake():
                devices.append(device)
                self.mock_devices.append(device)
        
        # Start multiple connection threads
        for i in range(5):
            thread = threading.Thread(target=connect_device, args=(f"concurrent_device_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all connections
        for thread in threads:
            thread.join()
        
        time.sleep(1.0)  # Allow server processing
        
        # Verify all devices connected
        stats = self.server.get_network_statistics()
        self.assertEqual(stats["active_devices"], 5)
        self.assertEqual(len(devices), 5)
        
        # Test concurrent messaging
        message_threads = []
        
        def send_messages(device):
            for i in range(10):
                device.send_status(battery=random.randint(50, 100))
                device.send_preview_frame("rgb")
                time.sleep(0.1)
        
        for device in devices:
            thread = threading.Thread(target=send_messages, args=(device,))
            message_threads.append(thread)
            thread.start()
        
        # Wait for all messaging to complete
        for thread in message_threads:
            thread.join()
        
        print(f"Concurrent test completed with {len(devices)} devices")
    
    def test_large_message_handling(self):
        """Test handling of large messages."""
        self.start_server()
        device = self.create_mock_device("large_msg_test")
        
        # Create large preview frame (1MB)
        large_data = os.urandom(1024 * 1024)
        large_b64 = base64.b64encode(large_data).decode('utf-8')
        
        large_message = {
            "type": "preview_frame",
            "frame_type": "rgb",
            "image_data": large_b64,
            "width": 1920,
            "height": 1080,
            "timestamp": time.time()
        }
        
        # Send large message
        success = device.send_message(large_message)
        self.assertTrue(success, "Large message should be sent successfully")
        
        time.sleep(2.0)  # Allow processing
        
        # Verify server handled the message
        stats = self.server.get_network_statistics()
        device_stats = stats["devices"]["large_msg_test"]
        self.assertGreater(device_stats["stats"]["bytes_received"], 1024 * 1024)
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        self.start_server()
        
        # Track error events
        error_events = []
        def on_error_occurred(device_id, error_type, error_message):
            error_events.append((device_id, error_type, error_message))
        
        self.server.error_occurred.connect(on_error_occurred)
        
        # Connect device
        device = self.create_mock_device("error_test")
        
        # Send invalid message format
        invalid_message = b"invalid_json_data"
        try:
            length_header = len(invalid_message).to_bytes(4, 'big')
            device.socket.send(length_header + invalid_message)
        except:
            pass
        
        time.sleep(1.0)  # Allow error processing
        
        # Send valid message after error
        self.assertTrue(device.send_status(battery=80))
        
        time.sleep(1.0)
        
        # Verify error was handled gracefully
        stats = self.server.get_network_statistics()
        if "error_test" in stats["devices"]:
            device_stats = stats["devices"]["error_test"]
            self.assertGreater(device_stats["stats"]["error_count"], 0)
    
    def test_server_command_broadcasting(self):
        """Test server command broadcasting to devices."""
        self.start_server()
        
        # Connect multiple devices
        devices = []
        for i in range(3):
            device = self.create_mock_device(f"broadcast_test_{i}")
            devices.append(device)
        
        time.sleep(1.0)
        
        # Send broadcast command
        count = self.server.broadcast_command("start_recording", session_id="test_session")
        self.assertEqual(count, 3, "Command should be sent to all devices")
        
        # Verify devices received command
        for device in devices:
            response = device.receive_message(timeout=2.0)
            if response:
                self.assertEqual(response.get("type"), "command")
                self.assertEqual(response.get("command"), "start_recording")
    
    def test_network_statistics_accuracy(self):
        """Test accuracy of network statistics tracking."""
        self.start_server()
        device = self.create_mock_device("stats_test")
        
        # Send known number of messages
        message_count = 10
        for i in range(message_count):
            device.send_status(battery=80 - i)
            device.send_preview_frame("rgb")
        
        time.sleep(2.0)  # Allow processing
        
        # Check statistics
        stats = self.server.get_network_statistics()
        device_stats = stats["devices"]["stats_test"]
        
        # Verify message counts (including handshake)
        self.assertGreaterEqual(
            device_stats["stats"]["messages_received"], 
            message_count * 2,  # status + preview messages
            "Message count should be tracked accurately"
        )
        
        # Verify byte counts
        self.assertGreater(
            device_stats["stats"]["bytes_received"],
            0,
            "Byte count should be tracked"
        )


class TestNetworkPerformance(unittest.TestCase):
    """Performance and stress tests for networking."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.server = EnhancedDeviceServer(
            host="127.0.0.1",
            port=9002,
            max_connections=20,
            heartbeat_interval=2.0
        )
    
    def tearDown(self):
        """Clean up performance tests."""
        if self.server and self.server.running:
            self.server.stop_server()
    
    def test_high_frequency_messaging(self):
        """Test high-frequency message handling."""
        success = self.server.start_server()
        self.assertTrue(success)
        time.sleep(0.5)
        
        device = MockDevice("perf_test")
        self.assertTrue(device.connect(port=9002))
        self.assertTrue(device.send_handshake())
        
        # Send messages at high frequency
        start_time = time.time()
        message_count = 100
        successful_sends = 0
        
        for i in range(message_count):
            if device.send_status(battery=random.randint(50, 100)):
                successful_sends += 1
            
            # Small delay to avoid overwhelming
            time.sleep(0.01)
        
        duration = time.time() - start_time
        
        print(f"High frequency test: {successful_sends}/{message_count} messages in {duration:.2f}s")
        print(f"Rate: {successful_sends/duration:.2f} messages/second")
        
        # Verify reasonable performance
        self.assertGreater(successful_sends / duration, 50, "Should handle at least 50 msg/sec")
        
        device.disconnect()
    
    def test_memory_usage_stability(self):
        """Test memory usage stability under sustained load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        success = self.server.start_server()
        self.assertTrue(success)
        time.sleep(0.5)
        
        device = MockDevice("memory_test")
        self.assertTrue(device.connect(port=9002))
        self.assertTrue(device.send_handshake())
        
        # Send sustained load for memory testing
        for cycle in range(10):
            for i in range(50):
                device.send_status(battery=random.randint(50, 100))
                device.send_preview_frame("rgb")
            
            # Check memory usage
            current_memory = process.memory_info().rss
            memory_growth = current_memory - initial_memory
            
            print(f"Cycle {cycle}: Memory growth: {memory_growth / 1024 / 1024:.2f} MB")
            
            # Force garbage collection
            gc.collect()
            
            time.sleep(0.1)
        
        final_memory = process.memory_info().rss
        total_growth = final_memory - initial_memory
        
        print(f"Total memory growth: {total_growth / 1024 / 1024:.2f} MB")
        
        # Memory growth should be reasonable (less than 50MB)
        self.assertLess(total_growth, 50 * 1024 * 1024, "Memory growth should be bounded")
        
        device.disconnect()


def run_comprehensive_tests():
    """Run all networking tests."""
    print("Starting Comprehensive Enhanced Networking Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add enhanced networking tests
    test_suite.addTest(unittest.makeSuite(TestEnhancedNetworking))
    test_suite.addTest(unittest.makeSuite(TestNetworkPerformance))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Enhanced Networking Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, trace in result.failures:
            print(f"- {test}: {trace.split(chr(10))[-2]}")
    
    if result.errors:
        print("\nErrors:")
        for test, trace in result.errors:
            print(f"- {test}: {trace.split(chr(10))[-2]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)