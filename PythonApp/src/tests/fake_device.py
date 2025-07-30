"""
Fake Android Device Simulator for Integration Testing.

This module provides a lightweight simulated Android client that connects to the
Python server over a socket and follows the defined protocol. It enables offline
testing of the PC application's behavior without requiring physical devices.
"""

import base64
import json
import logging
import os
import random
import socket

# Import protocol utilities
import sys
import threading
import time
from typing import Dict, Any, Optional, List, Callable

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from protocol import create_message, validate_message, get_host, get_port

logger = logging.getLogger(__name__)


class FakeAndroidDevice:
    """Simulates an Android device for testing purposes."""

    def __init__(
        self,
        device_id: str = "fake_device_001",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Initialize the fake Android device.

        Args:
            device_id: Unique identifier for this fake device
            host: Server host to connect to (uses config if None)
            port: Server port to connect to (uses config if None)
        """
        self.device_id = device_id
        self.host = host or get_host()
        self.port = port or get_port()
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.recording = False
        self.session_id: Optional[str] = None

        # Simulation parameters
        self.frame_counter = 0
        self.chunk_counter = 0
        self.battery_level = 85.0
        self.storage_available = 1024.0  # MB

        # Threading
        self.running = False
        self.message_thread: Optional[threading.Thread] = None
        self.preview_thread: Optional[threading.Thread] = None

        # Callbacks for testing
        self.on_command_received: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None

        logger.info(f"Initialized fake device {device_id}")

    def connect(self, timeout: float = 10.0) -> bool:
        """
        Connect to the Python server.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True

            # Start message handling thread
            self.message_thread = threading.Thread(
                target=self._message_handler, daemon=True
            )
            self.message_thread.start()

            # Send initial device status
            self._send_device_status()

            if self.on_connected:
                self.on_connected()

            logger.info(
                f"Fake device {self.device_id} connected to {self.host}:{self.port}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect fake device: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the server."""
        self.running = False
        self.recording = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        self.connected = False

        if self.on_disconnected:
            self.on_disconnected()

        logger.info(f"Fake device {self.device_id} disconnected")

    def _message_handler(self) -> None:
        """Handle incoming messages from the server."""
        while self.running and self.connected:
            try:
                # Receive message length (4 bytes)
                length_data = self._recv_exact(4)
                if not length_data:
                    break

                message_length = int.from_bytes(length_data, byteorder="big")

                # Receive message data
                message_data = self._recv_exact(message_length)
                if not message_data:
                    break

                # Parse JSON message
                message = json.loads(message_data.decode("utf-8"))

                # Validate message against schema
                if not validate_message(message):
                    logger.warning(f"Received invalid message: {message}")
                    continue

                # Handle the message
                self._handle_message(message)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message JSON: {e}")
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                break

        self.disconnect()

    def _recv_exact(self, length: int) -> Optional[bytes]:
        """Receive exactly the specified number of bytes."""
        if not self.socket:
            return None

        data = b""
        while len(data) < length:
            try:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                continue
            except Exception:
                return None

        return data

    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle a received message based on its type."""
        message_type = message.get("type")

        if self.on_command_received:
            self.on_command_received(message)

        if message_type == "start_record":
            self._handle_start_record(message)
        elif message_type == "stop_record":
            self._handle_stop_record(message)
        elif message_type == "calibration_start":
            self._handle_calibration_start(message)
        else:
            logger.info(f"Received message type: {message_type}")

    def _handle_start_record(self, message: Dict[str, Any]) -> None:
        """Handle start recording command."""
        self.session_id = message.get("session_id")
        self.recording = True
        self.frame_counter = 0
        self.chunk_counter = 0

        # Send acknowledgment
        ack_msg = create_message(
            "ack", message_id=str(message.get("timestamp", 0)), success=True
        )
        self._send_message(ack_msg)

        # Start sending preview frames
        self.preview_thread = threading.Thread(
            target=self._send_preview_frames, daemon=True
        )
        self.preview_thread.start()

        # Simulate file chunks after a delay
        threading.Timer(2.0, self._send_file_chunks).start()

        logger.info(f"Started recording session: {self.session_id}")

    def _handle_stop_record(self, message: Dict[str, Any]) -> None:
        """Handle stop recording command."""
        self.recording = False

        # Send acknowledgment
        ack_msg = create_message(
            "ack", message_id=str(message.get("timestamp", 0)), success=True
        )
        self._send_message(ack_msg)

        logger.info(f"Stopped recording session: {self.session_id}")
        self.session_id = None

    def _handle_calibration_start(self, message: Dict[str, Any]) -> None:
        """Handle calibration start command."""
        # Simulate calibration process
        threading.Timer(1.0, self._send_calibration_result).start()

        logger.info("Started calibration process")

    def _send_preview_frames(self) -> None:
        """Send preview frames while recording."""
        while self.recording and self.connected:
            try:
                # Generate fake image data (small placeholder)
                fake_image_data = self._generate_fake_image()

                preview_msg = create_message(
                    "preview_frame",
                    frame_id=self.frame_counter,
                    image_data=fake_image_data,
                    width=640,
                    height=480,
                )

                self._send_message(preview_msg)
                self.frame_counter += 1

                # Send at ~10 FPS for testing
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error sending preview frame: {e}")
                break

    def _send_file_chunks(self) -> None:
        """Send file chunks to simulate recorded data transfer."""
        if not self.recording:
            return

        # Simulate sending a video file in chunks
        file_id = f"video_{self.session_id}_{int(time.time())}"
        total_chunks = 5  # Small file for testing

        for chunk_index in range(total_chunks):
            if not self.recording:
                break

            # Generate fake chunk data
            fake_chunk_data = base64.b64encode(
                b"fake_video_data_chunk_" + str(chunk_index).encode()
            ).decode()

            chunk_msg = create_message(
                "file_chunk",
                file_id=file_id,
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                chunk_data=fake_chunk_data,
                chunk_size=len(fake_chunk_data),
                file_type="video",
            )

            self._send_message(chunk_msg)
            time.sleep(0.5)  # Simulate transfer delay

        logger.info(f"Completed sending file chunks for {file_id}")

    def _send_calibration_result(self) -> None:
        """Send calibration result."""
        # Simulate successful calibration with low error
        result_msg = create_message(
            "calibration_result",
            success=True,
            rms_error=0.8,  # Below threshold
            camera_matrix=[[800, 0, 320], [0, 800, 240], [0, 0, 1]],
            distortion_coefficients=[0.1, -0.2, 0.0, 0.0, 0.0],
        )

        self._send_message(result_msg)
        logger.info("Sent calibration result")

    def _send_device_status(self) -> None:
        """Send device status update."""
        status = "recording" if self.recording else "idle"

        status_msg = create_message(
            "device_status",
            device_id=self.device_id,
            status=status,
            battery_level=self.battery_level,
            storage_available=self.storage_available,
        )

        self._send_message(status_msg)

    def _generate_fake_image(self) -> str:
        """Generate fake image data for preview frames."""
        # Create a small fake JPEG-like data
        fake_data = (
            b"\xff\xd8\xff\xe0"
            + b"fake_jpeg_data_"
            + str(self.frame_counter).encode()
            + b"\xff\xd9"
        )
        return base64.b64encode(fake_data).decode()

    def _send_message(self, message: Dict[str, Any]) -> bool:
        """Send a message to the server."""
        if not self.connected or not self.socket:
            return False

        try:
            # Validate message before sending
            if not validate_message(message):
                logger.error(f"Attempted to send invalid message: {message}")
                return False

            # Serialize message
            message_data = json.dumps(message).encode("utf-8")
            message_length = len(message_data)

            # Send length prefix (4 bytes) + message data
            length_bytes = message_length.to_bytes(4, byteorder="big")
            self.socket.sendall(length_bytes + message_data)

            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def simulate_battery_drain(self) -> None:
        """Simulate battery draining over time."""
        if self.battery_level > 10:
            self.battery_level -= random.uniform(0.1, 0.5)
            self._send_device_status()

    def simulate_storage_usage(self) -> None:
        """Simulate storage being used during recording."""
        if self.recording and self.storage_available > 100:
            self.storage_available -= random.uniform(1, 5)
            self._send_device_status()


class FakeDeviceManager:
    """Manages multiple fake devices for testing."""

    def __init__(self):
        self.devices: List[FakeAndroidDevice] = []
        self.running = False

    def add_device(
        self, device_id: str, host: Optional[str] = None, port: Optional[int] = None
    ) -> FakeAndroidDevice:
        """Add a new fake device."""
        device = FakeAndroidDevice(device_id, host, port)
        self.devices.append(device)
        return device

    def connect_all(self) -> int:
        """Connect all devices. Returns number of successful connections."""
        connected_count = 0
        for device in self.devices:
            if device.connect():
                connected_count += 1
        return connected_count

    def disconnect_all(self) -> None:
        """Disconnect all devices."""
        for device in self.devices:
            device.disconnect()

    def start_recording_all(self, session_id: str) -> None:
        """Start recording on all connected devices."""
        start_msg = create_message("start_record", session_id=session_id)
        for device in self.devices:
            if device.connected:
                device._send_message(start_msg)

    def stop_recording_all(self, session_id: str) -> None:
        """Stop recording on all connected devices."""
        stop_msg = create_message("stop_record", session_id=session_id)
        for device in self.devices:
            if device.connected:
                device._send_message(stop_msg)


# Test utility functions
def create_test_device(device_id: str = "test_device") -> FakeAndroidDevice:
    """Create a fake device for testing."""
    return FakeAndroidDevice(device_id)


def run_basic_test() -> bool:
    """Run a basic test of the fake device."""
    device = create_test_device()

    try:
        # Connect to server
        if not device.connect(timeout=5.0):
            logger.error("Failed to connect to server")
            return False

        # Wait a bit for initial communication
        time.sleep(2.0)

        # Disconnect
        device.disconnect()

        logger.info("Basic fake device test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Basic test failed: {e}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run basic test
    success = run_basic_test()
    exit(0 if success else 1)
