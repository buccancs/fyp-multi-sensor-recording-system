#!/usr/bin/env python3
"""
Device Simulator Test Script for Milestone 3.2

This script simulates Android device connections to test the JsonSocketServer functionality.
It can simulate multiple devices connecting simultaneously and sending various message types.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.2 - Device Connection Manager and Socket Server Testing
"""

import base64
import json
import logging
import os
import socket
import struct
import sys
import threading
import time
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeviceSimulator:
    """Simulates an Android device connecting to the JsonSocketServer."""

    def __init__(self, device_id: str, host: str = "127.0.0.1", port: int = 9000):
        """
        Initialize device simulator.

        Args:
            device_id: Unique identifier for this simulated device
            host: Server host address
            port: Server port number
        """
        self.device_id = device_id
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False

    def connect(self) -> bool:
        """
        Connect to the JsonSocketServer.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Device {self.device_id} connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Device {self.device_id} failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from the server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        self.running = False
        logger.info(f"Device {self.device_id} disconnected")

    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a JSON message using length-prefixed protocol.

        Args:
            message: Dictionary to send as JSON

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected or not self.socket:
            logger.error(f"Device {self.device_id} not connected")
            return False

        try:
            # Convert message to JSON bytes
            json_data = json.dumps(message).encode("utf-8")

            # Send length header (4 bytes, big-endian) followed by JSON data
            length_header = struct.pack(">I", len(json_data))
            self.socket.send(length_header + json_data)

            logger.debug(
                f"Device {self.device_id} sent message: {message.get('type', 'unknown')}"
            )
            return True

        except Exception as e:
            logger.error(f"Device {self.device_id} failed to send message: {e}")
            return False

    def send_hello(self, capabilities: list = None) -> bool:
        """
        Send hello message to register with server.

        Args:
            capabilities: List of device capabilities

        Returns:
            True if sent successfully
        """
        if capabilities is None:
            capabilities = ["camera", "thermal", "imu", "gsr"]

        hello_message = {
            "type": "hello",
            "device_id": self.device_id,
            "capabilities": capabilities,
            "timestamp": time.time(),
        }

        return self.send_message(hello_message)

    def send_status(
        self,
        battery: int = 85,
        temperature: float = 36.5,
        recording: bool = False,
        storage: int = 75,
    ) -> bool:
        """
        Send status update message.

        Args:
            battery: Battery percentage (0-100)
            temperature: Device temperature in Celsius
            recording: Whether device is currently recording
            storage: Storage usage percentage (0-100)

        Returns:
            True if sent successfully
        """
        status_message = {
            "type": "status",
            "battery": battery,
            "temperature": temperature,
            "recording": recording,
            "storage": storage,
            "connected": True,
            "timestamp": time.time(),
        }

        return self.send_message(status_message)

    def send_preview_frame(
        self, frame_type: str = "rgb", image_data: bytes = None
    ) -> bool:
        """
        Send preview frame message with base64 encoded image.

        Args:
            frame_type: Type of frame ("rgb" or "thermal")
            image_data: Raw image bytes (will create dummy if None)

        Returns:
            True if sent successfully
        """
        if image_data is None:
            # Create a small dummy image (1x1 pixel PNG)
            image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        # Encode image as base64
        base64_data = base64.b64encode(image_data).decode("utf-8")

        frame_message = {
            "type": "preview_frame",
            "frame_type": frame_type,
            "frame_data": base64_data,
            "timestamp": time.time(),
        }

        return self.send_message(frame_message)

    def send_sensor_data(self, gsr: float = 0.5, ppg: float = 75.0) -> bool:
        """
        Send sensor data message.

        Args:
            gsr: GSR sensor value
            ppg: PPG sensor value

        Returns:
            True if sent successfully
        """
        sensor_message = {
            "type": "sensor_data",
            "gsr": gsr,
            "ppg": ppg,
            "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8},
            "gyroscope": {"x": 0.01, "y": 0.02, "z": 0.03},
            "magnetometer": {"x": 25.0, "y": 30.0, "z": 45.0},
            "timestamp": time.time(),
        }

        return self.send_message(sensor_message)

    def send_ack(
        self,
        command: str,
        success: bool = True,
        message: str = "Command executed successfully",
    ) -> bool:
        """
        Send acknowledgment message.

        Args:
            command: Command being acknowledged
            success: Whether command was successful
            message: Status message

        Returns:
            True if sent successfully
        """
        ack_message = {
            "type": "ack",
            "cmd": command,
            "status": "ok" if success else "error",
            "message": message,
            "timestamp": time.time(),
        }

        return self.send_message(ack_message)

    def send_notification(
        self, event_type: str, event_data: Dict[str, Any] = None
    ) -> bool:
        """
        Send notification message.

        Args:
            event_type: Type of event
            event_data: Additional event data

        Returns:
            True if sent successfully
        """
        if event_data is None:
            event_data = {}

        notification_message = {
            "type": "notification",
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": time.time(),
        }

        return self.send_message(notification_message)

    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        Receive a message from the server.

        Returns:
            Parsed JSON message or None if error
        """
        if not self.connected or not self.socket:
            return None

        try:
            # Read 4-byte length header
            length_data = self.socket.recv(4)
            if not length_data:
                return None

            # Parse message length
            message_length = struct.unpack(">I", length_data)[0]

            # Read JSON payload
            json_data = b""
            while len(json_data) < message_length:
                chunk = self.socket.recv(message_length - len(json_data))
                if not chunk:
                    return None
                json_data += chunk

            # Parse JSON
            message = json.loads(json_data.decode("utf-8"))
            logger.debug(
                f"Device {self.device_id} received: {message.get('type', 'unknown')}"
            )
            return message

        except Exception as e:
            logger.error(f"Device {self.device_id} failed to receive message: {e}")
            return None

    def run_simulation(self, duration: int = 30):
        """
        Run a complete device simulation for specified duration.

        Args:
            duration: Simulation duration in seconds
        """
        if not self.connect():
            return

        self.running = True

        # Send hello message
        if not self.send_hello():
            self.disconnect()
            return

        start_time = time.time()
        last_status = start_time
        last_frame = start_time
        last_sensor = start_time

        logger.info(
            f"Device {self.device_id} starting simulation for {duration} seconds"
        )

        try:
            while self.running and (time.time() - start_time) < duration:
                current_time = time.time()

                # Send status update every 5 seconds
                if current_time - last_status >= 5:
                    battery = max(
                        10, 100 - int((current_time - start_time) * 2)
                    )  # Simulate battery drain
                    self.send_status(battery=battery)
                    last_status = current_time

                # Send preview frame every 2 seconds
                if current_time - last_frame >= 2:
                    frame_type = "rgb" if int(current_time) % 4 < 2 else "thermal"
                    self.send_preview_frame(frame_type=frame_type)
                    last_frame = current_time

                # Send sensor data every 1 second
                if current_time - last_sensor >= 1:
                    gsr = 0.3 + 0.4 * (current_time % 10) / 10  # Simulate varying GSR
                    ppg = 70 + 10 * (current_time % 5) / 5  # Simulate varying PPG
                    self.send_sensor_data(gsr=gsr, ppg=ppg)
                    last_sensor = current_time

                # Check for incoming commands
                self.socket.settimeout(0.1)  # Non-blocking receive
                try:
                    message = self.receive_message()
                    if message and message.get("type") == "command":
                        command = message.get("command", "unknown")
                        logger.info(
                            f"Device {self.device_id} received command: {command}"
                        )

                        # Send acknowledgment
                        if command in [
                            "start_recording",
                            "stop_recording",
                            "capture_calibration",
                        ]:
                            self.send_ack(command, success=True)
                        else:
                            self.send_ack(
                                command, success=False, message="Unknown command"
                            )
                except socket.timeout:
                    pass  # No message received, continue

                time.sleep(0.1)  # Small delay to prevent busy waiting

        except KeyboardInterrupt:
            logger.info(f"Device {self.device_id} simulation interrupted")
        finally:
            self.disconnect()


def test_single_device():
    """Test single device connection and message sending."""
    logger.info("=== Testing Single Device Connection ===")

    device = DeviceSimulator("TestDevice1")

    if not device.connect():
        logger.error("Failed to connect device")
        return False

    # Test hello message
    if not device.send_hello(["camera", "thermal", "imu"]):
        logger.error("Failed to send hello message")
        device.disconnect()
        return False

    time.sleep(1)

    # Test status message
    if not device.send_status(battery=78, temperature=37.2):
        logger.error("Failed to send status message")
        device.disconnect()
        return False

    time.sleep(1)

    # Test preview frame
    if not device.send_preview_frame("rgb"):
        logger.error("Failed to send preview frame")
        device.disconnect()
        return False

    time.sleep(1)

    # Test sensor data
    if not device.send_sensor_data(gsr=0.6, ppg=80.0):
        logger.error("Failed to send sensor data")
        device.disconnect()
        return False

    time.sleep(1)

    # Test notification
    if not device.send_notification("recording_started", {"session_id": "test_123"}):
        logger.error("Failed to send notification")
        device.disconnect()
        return False

    time.sleep(2)
    device.disconnect()

    logger.info("Single device test completed successfully")
    return True


def test_multiple_devices():
    """Test multiple devices connecting simultaneously."""
    logger.info("=== Testing Multiple Device Connections ===")

    devices = [
        DeviceSimulator("TestDevice1"),
        DeviceSimulator("TestDevice2"),
        DeviceSimulator("TestDevice3"),
    ]

    # Connect all devices
    connected_devices = []
    for device in devices:
        if device.connect():
            connected_devices.append(device)
            device.send_hello()
            time.sleep(0.5)

    if len(connected_devices) != len(devices):
        logger.error(f"Only {len(connected_devices)}/{len(devices)} devices connected")

    # Send messages from all devices
    for i, device in enumerate(connected_devices):
        device.send_status(battery=90 - i * 10)
        device.send_preview_frame("rgb" if i % 2 == 0 else "thermal")
        time.sleep(0.2)

    time.sleep(2)

    # Disconnect all devices
    for device in connected_devices:
        device.disconnect()

    logger.info(f"Multiple device test completed with {len(connected_devices)} devices")
    return len(connected_devices) == len(devices)


def test_device_simulation():
    """Test full device simulation."""
    logger.info("=== Testing Device Simulation ===")

    device = DeviceSimulator("SimulationDevice")

    # Run simulation in a separate thread
    simulation_thread = threading.Thread(target=device.run_simulation, args=(10,))
    simulation_thread.start()

    # Wait for simulation to complete
    simulation_thread.join()

    logger.info("Device simulation test completed")
    return True


def main():
    """Main test function."""
    logger.info("Starting JsonSocketServer Device Simulator Tests")

    tests = [
        ("Single Device Test", test_single_device),
        ("Multiple Devices Test", test_multiple_devices),
        ("Device Simulation Test", test_device_simulation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            logger.info(f"\n--- Running {test_name} ---")
            if test_func():
                logger.info(f"✓ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")

        time.sleep(2)  # Delay between tests

    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Failed: {total - passed}/{total}")

    if passed == total:
        logger.info("All tests passed! ✓")
        return 0
    else:
        logger.error("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    exit(main())
