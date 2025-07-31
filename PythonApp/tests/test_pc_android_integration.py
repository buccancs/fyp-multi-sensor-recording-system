#!/usr/bin/env python3
"""
PC-Android Integration Test for Rock-Solid Networking

This test demonstrates and validates that the PC can reliably control the Android device
through the enhanced networking implementation. It simulates real-world scenarios
including recording control, calibration commands, and real-time streaming.

Features demonstrated:
- PC sending commands to Android device
- Android device responding with acknowledgments
- Real-time preview streaming from Android to PC
- Status monitoring and heartbeat mechanism
- Error recovery and reconnection
- Concurrent device management

Author: Multi-Sensor Recording System Team
Date: 2025-01-15
"""

import asyncio
import base64
import json
import os
import sys
import threading
import time
import unittest
from typing import Dict, List, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from network.enhanced_device_server import (
    EnhancedDeviceServer,
    MessagePriority,
    ConnectionState
)


class AndroidDeviceSimulator:
    """
    Simulator for Android device that responds to PC commands.
    
    This class simulates the Android app's behavior including:
    - Responding to recording commands
    - Sending status updates
    - Streaming preview frames
    - Handling calibration requests
    - Managing connection lifecycle
    """
    
    def __init__(self, device_id: str, capabilities: List[str] = None):
        self.device_id = device_id
        self.capabilities = capabilities or [
            "rgb_video", "thermal", "shimmer", "enhanced_client"
        ]
        
        # Connection management
        self.socket = None
        self.connected = False
        self.running = False
        
        # Device state
        self.recording = False
        self.battery_level = 85
        self.storage_available = "15.2 GB"
        self.temperature = 36.5
        
        # Streaming state
        self.streaming_preview = False
        self.streaming_quality = "medium"
        self.frame_counter = 0
        
        # Command handlers
        self.command_handlers = {
            "start_recording": self.handle_start_recording,
            "stop_recording": self.handle_stop_recording,
            "capture_calibration": self.handle_capture_calibration,
            "set_streaming_quality": self.handle_set_streaming_quality,
            "get_status": self.handle_get_status,
            "start_preview": self.handle_start_preview,
            "stop_preview": self.handle_stop_preview,
        }
        
        # Statistics
        self.commands_received = 0
        self.frames_sent = 0
        self.last_heartbeat = time.time()
    
    def connect(self, host: str = "127.0.0.1", port: int = 9001) -> bool:
        """Connect to PC server."""
        try:
            import socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            print(f"Android simulator {self.device_id} connected to {host}:{port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        print(f"Android simulator {self.device_id} disconnected")
    
    def start_simulation(self):
        """Start the device simulation."""
        if not self.connected:
            return False
        
        self.running = True
        
        # Send handshake
        if not self.send_handshake():
            return False
        
        # Start background threads
        threading.Thread(target=self.message_loop, daemon=True).start()
        threading.Thread(target=self.status_update_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        
        print(f"Android simulator {self.device_id} started")
        return True
    
    def send_handshake(self) -> bool:
        """Send handshake message to server."""
        handshake = {
            "type": "handshake",
            "device_id": self.device_id,
            "capabilities": self.capabilities,
            "app_version": "1.0.0",
            "device_type": "android",
            "timestamp": time.time()
        }
        return self.send_message(handshake)
    
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
    
    def receive_message(self, timeout: float = 1.0) -> Optional[dict]:
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
            
        except Exception:
            return None
    
    def message_loop(self):
        """Main message receiving loop."""
        while self.running and self.connected:
            message = self.receive_message(timeout=0.5)
            if message:
                self.process_message(message)
            time.sleep(0.01)
    
    def process_message(self, message: dict):
        """Process received message."""
        msg_type = message.get("type")
        
        if msg_type == "command":
            self.handle_command(message)
        elif msg_type == "heartbeat":
            self.handle_heartbeat(message)
        elif msg_type == "handshake_ack":
            self.handle_handshake_ack(message)
        else:
            print(f"Unknown message type: {msg_type}")
    
    def handle_command(self, message: dict):
        """Handle command from PC."""
        command = message.get("command")
        self.commands_received += 1
        
        print(f"Android {self.device_id} received command: {command}")
        
        # Execute command handler
        success = True
        error_message = None
        
        if command in self.command_handlers:
            try:
                result = self.command_handlers[command](message)
                success = result.get("success", True)
                error_message = result.get("error", None)
            except Exception as e:
                success = False
                error_message = str(e)
        else:
            success = False
            error_message = f"Unknown command: {command}"
        
        # Send acknowledgment
        self.send_ack(command, success, error_message)
    
    def send_ack(self, command: str, success: bool, error_message: str = None):
        """Send command acknowledgment."""
        ack = {
            "type": "ack",
            "cmd": command,
            "status": "ok" if success else "error",
            "message": error_message,
            "timestamp": time.time()
        }
        self.send_message(ack)
    
    def handle_start_recording(self, message: dict) -> dict:
        """Handle start recording command."""
        session_id = message.get("session_id", "unknown")
        self.recording = True
        
        # Start preview streaming if not already streaming
        if not self.streaming_preview:
            self.streaming_preview = True
            threading.Thread(target=self.preview_streaming_loop, daemon=True).start()
        
        print(f"Android {self.device_id} started recording session: {session_id}")
        return {"success": True}
    
    def handle_stop_recording(self, message: dict) -> dict:
        """Handle stop recording command."""
        self.recording = False
        self.streaming_preview = False
        
        print(f"Android {self.device_id} stopped recording")
        return {"success": True}
    
    def handle_capture_calibration(self, message: dict) -> dict:
        """Handle calibration capture command."""
        calibration_id = message.get("calibration_id", "cal_" + str(int(time.time())))
        capture_rgb = message.get("capture_rgb", True)
        capture_thermal = message.get("capture_thermal", True)
        
        # Simulate calibration capture
        time.sleep(0.5)  # Simulate capture time
        
        # Send calibration result
        calibration_result = {
            "type": "calibration_result",
            "calibration_id": calibration_id,
            "success": True,
            "rms_error": 0.45,
            "images_captured": {
                "rgb": capture_rgb,
                "thermal": capture_thermal
            },
            "timestamp": time.time()
        }
        self.send_message(calibration_result)
        
        print(f"Android {self.device_id} captured calibration: {calibration_id}")
        return {"success": True}
    
    def handle_set_streaming_quality(self, message: dict) -> dict:
        """Handle streaming quality change."""
        quality = message.get("quality", "medium")
        self.streaming_quality = quality
        
        print(f"Android {self.device_id} set streaming quality to: {quality}")
        return {"success": True}
    
    def handle_get_status(self, message: dict) -> dict:
        """Handle status request."""
        self.send_status_update()
        return {"success": True}
    
    def handle_start_preview(self, message: dict) -> dict:
        """Handle start preview command."""
        if not self.streaming_preview:
            self.streaming_preview = True
            threading.Thread(target=self.preview_streaming_loop, daemon=True).start()
        
        print(f"Android {self.device_id} started preview streaming")
        return {"success": True}
    
    def handle_stop_preview(self, message: dict) -> dict:
        """Handle stop preview command."""
        self.streaming_preview = False
        
        print(f"Android {self.device_id} stopped preview streaming")
        return {"success": True}
    
    def handle_heartbeat(self, message: dict):
        """Handle heartbeat from server."""
        self.last_heartbeat = time.time()
        
        # Send heartbeat response
        response = {
            "type": "heartbeat_response",
            "timestamp": time.time()
        }
        self.send_message(response)
    
    def handle_handshake_ack(self, message: dict):
        """Handle handshake acknowledgment."""
        compatible = message.get("compatible", False)
        if compatible:
            print(f"Android {self.device_id} handshake acknowledged")
        else:
            print(f"Android {self.device_id} protocol incompatible")
    
    def status_update_loop(self):
        """Send periodic status updates."""
        while self.running and self.connected:
            time.sleep(10)  # Every 10 seconds
            
            # Simulate battery drain
            if self.recording:
                self.battery_level = max(0, self.battery_level - 1)
            
            self.send_status_update()
    
    def send_status_update(self):
        """Send device status update."""
        status = {
            "type": "status",
            "battery": self.battery_level,
            "storage": self.storage_available,
            "temperature": self.temperature,
            "recording": self.recording,
            "connected": True,
            "timestamp": time.time()
        }
        self.send_message(status)
    
    def heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self.running and self.connected:
            time.sleep(5)  # Every 5 seconds
            
            heartbeat = {
                "type": "heartbeat",
                "timestamp": time.time()
            }
            self.send_message(heartbeat)
    
    def preview_streaming_loop(self):
        """Send preview frames while streaming."""
        frame_rates = {"low": 5, "medium": 15, "high": 30}
        
        while self.streaming_preview and self.running and self.connected:
            fps = frame_rates.get(self.streaming_quality, 15)
            frame_interval = 1.0 / fps
            
            self.send_preview_frame()
            self.frames_sent += 1
            
            time.sleep(frame_interval)
    
    def send_preview_frame(self):
        """Send mock preview frame."""
        # Create mock image data
        frame_size = {"low": 100, "medium": 500, "high": 1000}
        size = frame_size.get(self.streaming_quality, 500)
        
        mock_image_data = os.urandom(size)
        image_b64 = base64.b64encode(mock_image_data).decode('utf-8')
        
        frame = {
            "type": "preview_frame",
            "frame_type": "rgb",
            "image_data": image_b64,
            "width": 640,
            "height": 480,
            "frame_id": self.frame_counter,
            "quality": self.streaming_quality,
            "timestamp": time.time()
        }
        
        self.send_message(frame)
        self.frame_counter += 1
    
    def get_statistics(self) -> dict:
        """Get device statistics."""
        return {
            "device_id": self.device_id,
            "connected": self.connected,
            "recording": self.recording,
            "streaming": self.streaming_preview,
            "commands_received": self.commands_received,
            "frames_sent": self.frames_sent,
            "battery_level": self.battery_level,
            "last_heartbeat": self.last_heartbeat
        }


class PCController:
    """
    PC controller that manages Android devices and sends commands.
    """
    
    def __init__(self, server: EnhancedDeviceServer):
        self.server = server
        self.connected_devices = {}
        self.command_responses = {}
        
        # Connect to server signals
        self.server.device_connected.connect(self.on_device_connected)
        self.server.device_disconnected.connect(self.on_device_disconnected)
        self.server.message_received.connect(self.on_message_received)
        self.server.preview_frame_received.connect(self.on_preview_frame_received)
    
    def on_device_connected(self, device_id: str, device_info: dict):
        """Handle device connection."""
        self.connected_devices[device_id] = device_info
        print(f"PC Controller: Device {device_id} connected")
    
    def on_device_disconnected(self, device_id: str, reason: str):
        """Handle device disconnection."""
        if device_id in self.connected_devices:
            del self.connected_devices[device_id]
        print(f"PC Controller: Device {device_id} disconnected - {reason}")
    
    def on_message_received(self, device_id: str, message: dict):
        """Handle message from device."""
        msg_type = message.get("type")
        
        if msg_type == "ack":
            command = message.get("cmd")
            status = message.get("status")
            self.command_responses[f"{device_id}_{command}"] = {
                "success": status == "ok",
                "message": message.get("message"),
                "timestamp": time.time()
            }
            print(f"PC Controller: ACK from {device_id} for {command}: {status}")
        
        elif msg_type == "status":
            print(f"PC Controller: Status from {device_id} - "
                  f"Battery: {message.get('battery')}%, "
                  f"Recording: {message.get('recording')}")
        
        elif msg_type == "calibration_result":
            print(f"PC Controller: Calibration result from {device_id} - "
                  f"Success: {message.get('success')}, "
                  f"RMS Error: {message.get('rms_error')}")
    
    def on_preview_frame_received(self, device_id: str, frame_type: str, 
                                 frame_data: bytes, metadata: dict):
        """Handle preview frame from device."""
        frame_id = metadata.get("frame_id", 0)
        quality = metadata.get("quality", "unknown")
        size = len(frame_data)
        
        print(f"PC Controller: Preview frame from {device_id} - "
              f"Type: {frame_type}, Frame: {frame_id}, "
              f"Quality: {quality}, Size: {size} bytes")
    
    def send_command_to_device(self, device_id: str, command: str, **kwargs) -> bool:
        """Send command to specific device."""
        success = self.server.send_command_to_device(device_id, command, **kwargs)
        if success:
            print(f"PC Controller: Sent {command} to {device_id}")
        else:
            print(f"PC Controller: Failed to send {command} to {device_id}")
        return success
    
    def broadcast_command(self, command: str, **kwargs) -> int:
        """Broadcast command to all devices."""
        count = self.server.broadcast_command(command, **kwargs)
        print(f"PC Controller: Broadcasted {command} to {count} devices")
        return count
    
    def wait_for_ack(self, device_id: str, command: str, timeout: float = 5.0) -> bool:
        """Wait for command acknowledgment."""
        start_time = time.time()
        ack_key = f"{device_id}_{command}"
        
        while time.time() - start_time < timeout:
            if ack_key in self.command_responses:
                response = self.command_responses[ack_key]
                del self.command_responses[ack_key]
                return response["success"]
            time.sleep(0.1)
        
        print(f"PC Controller: Timeout waiting for ACK from {device_id} for {command}")
        return False
    
    def get_connected_devices(self) -> List[str]:
        """Get list of connected device IDs."""
        return list(self.connected_devices.keys())


class TestPCAndroidIntegration(unittest.TestCase):
    """Integration tests for PC-Android communication."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.server = EnhancedDeviceServer(
            host="127.0.0.1",
            port=9003,
            heartbeat_interval=2.0
        )
        self.pc_controller = PCController(self.server)
        self.android_devices = []
    
    def tearDown(self):
        """Clean up integration tests."""
        # Disconnect all Android devices
        for device in self.android_devices:
            device.disconnect()
        
        # Stop server
        if self.server.running:
            self.server.stop_server()
    
    def start_test_environment(self):
        """Start the test environment."""
        success = self.server.start_server()
        self.assertTrue(success, "Server should start")
        time.sleep(0.5)
    
    def create_android_device(self, device_id: str) -> AndroidDeviceSimulator:
        """Create and connect Android device simulator."""
        device = AndroidDeviceSimulator(device_id)
        self.assertTrue(device.connect(port=9003), f"Device {device_id} should connect")
        self.assertTrue(device.start_simulation(), f"Device {device_id} should start")
        self.android_devices.append(device)
        time.sleep(1.0)  # Allow handshake processing
        return device
    
    def test_basic_pc_android_communication(self):
        """Test basic PC-Android communication."""
        self.start_test_environment()
        
        # Create Android device
        android_device = self.create_android_device("test_phone_1")
        
        # Verify device is connected to PC
        devices = self.pc_controller.get_connected_devices()
        self.assertIn("test_phone_1", devices)
        
        # PC sends command to Android
        success = self.pc_controller.send_command_to_device(
            "test_phone_1", "get_status"
        )
        self.assertTrue(success)
        
        # Wait for ACK
        ack_received = self.pc_controller.wait_for_ack("test_phone_1", "get_status")
        self.assertTrue(ack_received, "Should receive acknowledgment")
    
    def test_recording_control_workflow(self):
        """Test complete recording control workflow."""
        self.start_test_environment()
        
        # Create Android device
        android_device = self.create_android_device("recording_phone")
        
        # Start recording session
        success = self.pc_controller.send_command_to_device(
            "recording_phone", "start_recording", session_id="test_session_001"
        )
        self.assertTrue(success)
        
        # Wait for ACK
        ack_received = self.pc_controller.wait_for_ack("recording_phone", "start_recording")
        self.assertTrue(ack_received, "Should acknowledge start recording")
        
        # Verify device is recording
        time.sleep(1.0)
        stats = android_device.get_statistics()
        self.assertTrue(stats["recording"], "Device should be recording")
        self.assertTrue(stats["streaming"], "Device should be streaming")
        
        # Stop recording
        success = self.pc_controller.send_command_to_device(
            "recording_phone", "stop_recording"
        )
        self.assertTrue(success)
        
        # Wait for ACK
        ack_received = self.pc_controller.wait_for_ack("recording_phone", "stop_recording")
        self.assertTrue(ack_received, "Should acknowledge stop recording")
        
        # Verify recording stopped
        time.sleep(1.0)
        stats = android_device.get_statistics()
        self.assertFalse(stats["recording"], "Device should stop recording")
    
    def test_calibration_workflow(self):
        """Test calibration command workflow."""
        self.start_test_environment()
        
        # Create Android device
        android_device = self.create_android_device("calibration_phone")
        
        # Send calibration command
        success = self.pc_controller.send_command_to_device(
            "calibration_phone", "capture_calibration",
            calibration_id="test_cal_001",
            capture_rgb=True,
            capture_thermal=True
        )
        self.assertTrue(success)
        
        # Wait for ACK
        ack_received = self.pc_controller.wait_for_ack("calibration_phone", "capture_calibration")
        self.assertTrue(ack_received, "Should acknowledge calibration command")
        
        # Additional time for calibration result message
        time.sleep(2.0)
    
    def test_real_time_streaming(self):
        """Test real-time preview streaming."""
        self.start_test_environment()
        
        # Create Android device
        android_device = self.create_android_device("streaming_phone")
        
        # Start preview streaming
        success = self.pc_controller.send_command_to_device(
            "streaming_phone", "start_preview"
        )
        self.assertTrue(success)
        
        # Wait for ACK
        ack_received = self.pc_controller.wait_for_ack("streaming_phone", "start_preview")
        self.assertTrue(ack_received, "Should acknowledge start preview")
        
        # Let streaming run for a few seconds
        time.sleep(3.0)
        
        # Verify frames were sent
        stats = android_device.get_statistics()
        self.assertGreater(stats["frames_sent"], 0, "Should have sent preview frames")
        
        # Change streaming quality
        success = self.pc_controller.send_command_to_device(
            "streaming_phone", "set_streaming_quality", quality="high"
        )
        self.assertTrue(success)
        
        ack_received = self.pc_controller.wait_for_ack("streaming_phone", "set_streaming_quality")
        self.assertTrue(ack_received, "Should acknowledge quality change")
        
        # Stop preview
        success = self.pc_controller.send_command_to_device(
            "streaming_phone", "stop_preview"
        )
        self.assertTrue(success)
        
        ack_received = self.pc_controller.wait_for_ack("streaming_phone", "stop_preview")
        self.assertTrue(ack_received, "Should acknowledge stop preview")
    
    def test_multiple_device_control(self):
        """Test controlling multiple Android devices simultaneously."""
        self.start_test_environment()
        
        # Create multiple Android devices
        devices = []
        for i in range(3):
            device = self.create_android_device(f"multi_phone_{i}")
            devices.append(device)
        
        # Verify all devices are connected
        connected_devices = self.pc_controller.get_connected_devices()
        self.assertEqual(len(connected_devices), 3, "All devices should be connected")
        
        # Broadcast start recording command
        count = self.pc_controller.broadcast_command(
            "start_recording", session_id="multi_session_001"
        )
        self.assertEqual(count, 3, "Command should be sent to all devices")
        
        # Wait for all ACKs
        for i in range(3):
            ack_received = self.pc_controller.wait_for_ack(
                f"multi_phone_{i}", "start_recording"
            )
            self.assertTrue(ack_received, f"Device {i} should acknowledge")
        
        # Verify all devices are recording
        time.sleep(1.0)
        for device in devices:
            stats = device.get_statistics()
            self.assertTrue(stats["recording"], "All devices should be recording")
        
        # Send individual commands to specific devices
        success = self.pc_controller.send_command_to_device(
            "multi_phone_1", "set_streaming_quality", quality="low"
        )
        self.assertTrue(success)
        
        # Stop all recordings
        count = self.pc_controller.broadcast_command("stop_recording")
        self.assertEqual(count, 3, "Stop command should reach all devices")
    
    def test_error_recovery_and_reconnection(self):
        """Test error recovery and reconnection scenarios."""
        self.start_test_environment()
        
        # Create Android device
        android_device = self.create_android_device("recovery_phone")
        
        # Verify initial connection
        devices = self.pc_controller.get_connected_devices()
        self.assertIn("recovery_phone", devices)
        
        # Simulate network disconnection
        android_device.socket.close()
        android_device.connected = False
        
        # Wait for server to detect disconnection
        time.sleep(3.0)
        
        # Verify device was removed from PC's device list
        devices = self.pc_controller.get_connected_devices()
        self.assertNotIn("recovery_phone", devices)
        
        # Simulate reconnection
        android_device.connect(port=9003)
        android_device.start_simulation()
        
        # Wait for reconnection to be processed
        time.sleep(2.0)
        
        # Verify device is back in PC's device list
        devices = self.pc_controller.get_connected_devices()
        self.assertIn("recovery_phone", devices)
        
        # Test that commands work after reconnection
        success = self.pc_controller.send_command_to_device(
            "recovery_phone", "get_status"
        )
        self.assertTrue(success)
        
        ack_received = self.pc_controller.wait_for_ack("recovery_phone", "get_status")
        self.assertTrue(ack_received, "Commands should work after reconnection")
    
    def test_heartbeat_and_connection_monitoring(self):
        """Test heartbeat mechanism and connection monitoring."""
        self.start_test_environment()
        
        # Create Android device
        android_device = self.create_android_device("heartbeat_phone")
        
        # Let heartbeats run for a while
        time.sleep(10.0)
        
        # Verify heartbeats are working
        stats = android_device.get_statistics()
        self.assertGreater(
            stats["last_heartbeat"], 
            time.time() - 10, 
            "Recent heartbeat should be recorded"
        )
        
        # Get server statistics
        server_stats = self.server.get_network_statistics()
        device_stats = server_stats["devices"]["heartbeat_phone"]
        
        # Verify device is considered alive
        self.assertTrue(device_stats["is_alive"], "Device should be alive")


def run_integration_tests():
    """Run PC-Android integration tests."""
    print("Starting PC-Android Integration Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPCAndroidIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PC-Android Integration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
        print("✅ PC can reliably control Android device")
        print("✅ Rock-solid networking implementation verified")
    else:
        print("❌ Some integration tests failed")
        
        if result.failures:
            print("\nFailures:")
            for test, trace in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nErrors:")
            for test, trace in result.errors:
                print(f"- {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)