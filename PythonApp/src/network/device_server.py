"""
Device Server for Multi-Sensor Recording System Controller

This module implements the JsonSocketServer class which handles TCP connections
from Android devices on port 9000. It processes JSON messages and emits PyQt signals
for GUI integration.

Extracted and enhanced from main_backup.py for Milestone 3.2 integration.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.2 - Device Connection Manager and Socket Server
"""

import base64
import json
import os
import socket
import struct
import threading
import time
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, List, Optional, Any

# Import centralized logging
from utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)


class RemoteDevice:
    """
    Represents a connected remote device with comprehensive state management.

    This class replaces the simple socket mapping with a more robust device
    representation that includes capabilities, status, and connection information.
    """

    def __init__(
        self, device_id: str, capabilities: List[str], client_socket: socket.socket
    ):
        """
        Initialize a remote device.

        Args:
            device_id: Unique identifier for the device
            capabilities: List of device capabilities (camera, thermal, imu, etc.)
            client_socket: Socket connection to the device
        """
        self.device_id = device_id
        self.capabilities = capabilities
        self.client_socket = client_socket
        self.connected = True
        self.last_seen = time.time()

        # Device status information
        self.status = {
            "battery": None,
            "temperature": None,
            "storage": None,
            "recording": False,
            "last_update": time.time(),
        }

        # Connection statistics
        self.connection_stats = {
            "connected_at": time.time(),
            "messages_received": 0,
            "messages_sent": 0,
            "last_activity": time.time(),
        }

        # Device capabilities flags for easy checking
        self.has_camera = "camera" in capabilities
        self.has_thermal = "thermal" in capabilities
        self.has_imu = "imu" in capabilities
        self.has_gsr = "gsr" in capabilities

        logger.info(
            f"RemoteDevice created: {device_id} with capabilities: {capabilities}"
        )

    def update_status(self, status_data: Dict[str, Any]):
        """
        Update device status information.

        Args:
            status_data: Dictionary containing status updates
        """
        self.status.update(status_data)
        self.status["last_update"] = time.time()
        self.last_seen = time.time()
        self.connection_stats["last_activity"] = time.time()

        logger.debug(f"Device {self.device_id} status updated: {status_data}")

    def increment_message_count(self, message_type: str = "received"):
        """
        Increment message counters for statistics.

        Args:
            message_type: Type of message ('received' or 'sent')
        """
        if message_type == "received":
            self.connection_stats["messages_received"] += 1
        elif message_type == "sent":
            self.connection_stats["messages_sent"] += 1

        self.connection_stats["last_activity"] = time.time()
        self.last_seen = time.time()

    def is_alive(self, timeout_seconds: int = 30) -> bool:
        """
        Check if device is considered alive based on last activity.

        Args:
            timeout_seconds: Timeout in seconds for considering device alive

        Returns:
            True if device is alive, False otherwise
        """
        return (time.time() - self.last_seen) < timeout_seconds

    def get_connection_duration(self) -> float:
        """
        Get the duration of the current connection in seconds.

        Returns:
            Connection duration in seconds
        """
        return time.time() - self.connection_stats["connected_at"]

    def get_device_info(self) -> Dict[str, Any]:
        """
        Get comprehensive device information.

        Returns:
            Dictionary containing all device information
        """
        return {
            "device_id": self.device_id,
            "capabilities": self.capabilities,
            "connected": self.connected,
            "status": self.status.copy(),
            "connection_stats": self.connection_stats.copy(),
            "last_seen": self.last_seen,
            "connection_duration": self.get_connection_duration(),
            "is_alive": self.is_alive(),
        }

    def disconnect(self):
        """Mark device as disconnected and close socket."""
        self.connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass

        logger.info(
            f"RemoteDevice {self.device_id} disconnected after {self.get_connection_duration():.1f} seconds"
        )


class JsonSocketServer(QThread):
    """
    JSON Socket Server for Milestone 3.2 Device Connection Manager.

    Implements length-prefixed JSON message protocol for bidirectional communication
    with Android devices on port 9000. Handles multiple device connections using
    multi-threading and emits PyQt signals for thread-safe GUI updates.
    """

    # Signals for GUI integration (thread-safe communication)
    device_connected = pyqtSignal(str, list)  # device_id, capabilities
    device_disconnected = pyqtSignal(str)  # device_id
    status_received = pyqtSignal(str, dict)  # device_id, status_data
    ack_received = pyqtSignal(str, str, bool, str)  # device_id, cmd, success, message
    preview_frame_received = pyqtSignal(
        str, str, str
    )  # device_id, frame_type, base64_data
    sensor_data_received = pyqtSignal(str, dict)  # device_id, sensor_data
    notification_received = pyqtSignal(
        str, str, dict
    )  # device_id, event_type, event_data
    error_occurred = pyqtSignal(str, str)  # device_id, error_message

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9000,
        use_newline_protocol: bool = False,
        session_manager=None,
    ):
        """
        Initialize the JSON Socket Server.

        Args:
            host (str): Host address to bind to (default: '0.0.0.0' for all interfaces)
            port (int): Port number to listen on (default: 9000)
            use_newline_protocol (bool): Use newline-delimited JSON instead of length-prefixed (default: False)
            session_manager: SessionManager instance for session directory integration (default: None)
        """
        super().__init__()
        self.host = host
        self.port = port
        self.use_newline_protocol = use_newline_protocol
        self.session_manager = session_manager
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.devices: Dict[str, RemoteDevice] = {}  # device_id -> RemoteDevice mapping
        self.clients: Dict[str, socket.socket] = {}  # device_id -> client socket mapping
        self.client_threads: List[threading.Thread] = []

        protocol_type = (
            "newline-delimited" if use_newline_protocol else "length-prefixed"
        )
        logger.info(
            f"JsonSocketServer initialized for {host}:{port} using {protocol_type} JSON protocol"
        )

    def run(self):
        """Main server thread execution method."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            logger.info(f"JSON Socket server started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_json_client,
                        args=(client_socket, address),
                        daemon=True,
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)

                except socket.error as e:
                    if self.running:
                        logger.error(f"JSON socket accept error: {e}")
                        self.error_occurred.emit("server", f"Accept error: {str(e)}")

        except Exception as e:
            logger.error(f"JSON socket server error: {e}")
            self.error_occurred.emit("server", f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_json_client(self, client_socket: socket.socket, address: tuple):
        """
        Handle individual JSON client connections with length-prefixed framing.

        Args:
            client_socket: Socket object for the connected client
            address: Address tuple (ip, port) of the connected client
        """
        client_addr = f"{address[0]}:{address[1]}"
        device_id = None

        logger.info(f"JSON client connected: {client_addr}")

        try:
            while self.running:
                # Read 4-byte length header
                length_data = self.recv_exact(client_socket, 4)
                if not length_data:
                    break

                # Parse message length (big-endian)
                message_length = struct.unpack(">I", length_data)[0]

                if message_length <= 0 or message_length > 10 * 1024 * 1024:  # Max 10MB
                    logger.error(f"Invalid message length: {message_length}")
                    self.error_occurred.emit(
                        device_id or client_addr,
                        f"Invalid message length: {message_length}",
                    )
                    break

                # Read JSON payload
                json_data = self.recv_exact(client_socket, message_length)
                if not json_data:
                    break

                # Process JSON message
                try:
                    message = json.loads(json_data.decode("utf-8"))
                    device_id = self.process_json_message(
                        client_socket, client_addr, message
                    )

                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error from {client_addr}: {e}")
                    self.error_occurred.emit(
                        device_id or client_addr, f"JSON decode error: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"JSON client handling error for {client_addr}: {e}")
            self.error_occurred.emit(
                device_id or client_addr, f"Client handling error: {str(e)}"
            )
        finally:
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                device.disconnect()
                del self.devices[device_id]
                if device_id in self.clients:
                    del self.clients[device_id]
                self.device_disconnected.emit(device_id)
                logger.info(f"Device {device_id} disconnected")
            else:
                client_socket.close()
            logger.info(f"JSON client disconnected: {client_addr}")

    def recv_exact(self, sock: socket.socket, length: int) -> Optional[bytes]:
        """
        Receive exactly 'length' bytes from socket.

        Args:
            sock: Socket to receive from
            length: Number of bytes to receive

        Returns:
            Received data or None if connection closed
        """
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def process_json_message(
        self, client_socket: socket.socket, client_addr: str, message: Dict[str, Any]
    ) -> Optional[str]:
        """
        Process incoming JSON message and emit appropriate signals.

        Args:
            client_socket: Socket object for the client
            client_addr: Client address string
            message: Parsed JSON message dictionary

        Returns:
            Device ID if available, None otherwise
        """
        message_type = message.get("type", "unknown")
        logger.debug(f"Received JSON message from {client_addr}: {message_type}")

        if message_type == "hello":
            device_id = message.get("device_id", client_addr)
            capabilities = message.get("capabilities", [])

            # Create RemoteDevice object and store it
            remote_device = RemoteDevice(device_id, capabilities, client_socket)
            self.devices[device_id] = remote_device
            self.clients[device_id] = client_socket

            # Emit device connected signal
            self.device_connected.emit(device_id, capabilities)

            logger.info(
                f"Device registered: {device_id} with capabilities: {capabilities}"
            )
            return device_id

        elif message_type == "status":
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                status_data = {
                    "battery": message.get("battery"),
                    "storage": message.get("storage"),
                    "temperature": message.get("temperature"),
                    "recording": message.get("recording", False),
                    "connected": message.get("connected", True),
                    "timestamp": message.get("timestamp"),
                }
                device.update_status(status_data)
                device.increment_message_count("received")
                self.status_received.emit(device_id, status_data)
                logger.debug(f"Status update from {device_id}: {status_data}")

        elif message_type == "preview_frame":
            device_id = self.find_device_id(client_socket)
            if device_id:
                frame_type = message.get("frame_type", "rgb")  # 'rgb' or 'thermal'
                frame_data = message.get("frame_data", "")

                if frame_data:
                    self.preview_frame_received.emit(device_id, frame_type, frame_data)
                    logger.debug(
                        f"Preview frame received from {device_id}: {frame_type}"
                    )
                else:
                    logger.warning(f"Empty frame data from {device_id}")

        elif message_type == "sensor_data":
            device_id = self.find_device_id(client_socket)
            if device_id:
                sensor_data = {
                    "gsr": message.get("gsr"),
                    "ppg": message.get("ppg"),
                    "accelerometer": message.get("accelerometer"),
                    "gyroscope": message.get("gyroscope"),
                    "magnetometer": message.get("magnetometer"),
                    "timestamp": message.get("timestamp"),
                }
                self.sensor_data_received.emit(device_id, sensor_data)
                logger.debug(f"Sensor data from {device_id}")

        elif message_type == "notification":
            device_id = self.find_device_id(client_socket)
            if device_id:
                event_type = message.get("event_type", "unknown")
                event_data = message.get("event_data", {})
                self.notification_received.emit(device_id, event_type, event_data)
                logger.info(f"Notification from {device_id}: {event_type}")

        elif message_type == "ack":
            device_id = self.find_device_id(client_socket)
            if device_id:
                cmd = message.get("cmd", "")
                status = message.get("status", "unknown")
                success = status == "ok"
                error_message = message.get("message", "")
                self.ack_received.emit(device_id, cmd, success, error_message)
                logger.debug(f"ACK from {device_id} for {cmd}: {status}")

        elif message_type == "file_info":
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                filename = message.get("name", "unknown")
                filesize = message.get("size", 0)

                # Initialize file transfer state
                device.file_transfer_state = {
                    "filename": filename,
                    "expected_size": filesize,
                    "received_bytes": 0,
                    "file_handle": None,
                    "chunks_received": 0,
                }

                # Create session directory and open file for writing
                session_dir = self.get_session_directory()
                if session_dir:
                    filepath = os.path.join(session_dir, f"{device_id}_{filename}")
                    try:
                        device.file_transfer_state["file_handle"] = open(filepath, "wb")
                        logger.info(
                            f"Started receiving file {filename} from {device_id} ({filesize} bytes)"
                        )
                    except Exception as e:
                        logger.error(f"Failed to create file {filepath}: {e}")
                        device.file_transfer_state = None
                else:
                    logger.error(f"No session directory available for file transfer")
                    device.file_transfer_state = None

        elif message_type == "file_chunk":
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                if (
                    hasattr(device, "file_transfer_state")
                    and device.file_transfer_state
                ):
                    seq = message.get("seq", 0)
                    base64_data = message.get("data", "")

                    try:
                        # Decode Base64 data
                        chunk_data = base64.b64decode(base64_data)

                        # Write chunk to file
                        if device.file_transfer_state["file_handle"]:
                            device.file_transfer_state["file_handle"].write(chunk_data)
                            device.file_transfer_state["received_bytes"] += len(
                                chunk_data
                            )
                            device.file_transfer_state["chunks_received"] += 1

                            # Log progress periodically
                            if seq % 100 == 0:
                                progress = (
                                    device.file_transfer_state["received_bytes"]
                                    * 100.0
                                    / device.file_transfer_state["expected_size"]
                                )
                                logger.debug(
                                    f"File transfer progress from {device_id}: {progress:.1f}% "
                                    f"({device.file_transfer_state['received_bytes']}/{device.file_transfer_state['expected_size']} bytes)"
                                )

                    except Exception as e:
                        logger.error(
                            f"Error processing file chunk from {device_id}: {e}"
                        )
                else:
                    logger.warning(
                        f"Received file chunk from {device_id} without file_info"
                    )

        elif message_type == "file_end":
            device_id = self.find_device_id(client_socket)
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                if (
                    hasattr(device, "file_transfer_state")
                    and device.file_transfer_state
                ):
                    filename = message.get("name", "unknown")

                    try:
                        # Close file handle
                        if device.file_transfer_state["file_handle"]:
                            device.file_transfer_state["file_handle"].close()

                        # Verify file size
                        expected_size = device.file_transfer_state["expected_size"]
                        received_size = device.file_transfer_state["received_bytes"]
                        chunks_received = device.file_transfer_state["chunks_received"]

                        if received_size == expected_size:
                            logger.info(
                                f"File transfer completed successfully: {filename} from {device_id} "
                                f"({received_size} bytes, {chunks_received} chunks)"
                            )

                            # Send acknowledgment
                            ack_message = {
                                "type": "file_received",
                                "name": filename,
                                "status": "ok",
                            }
                            self.send_command(device_id, ack_message)
                        else:
                            logger.error(
                                f"File transfer size mismatch: expected {expected_size}, "
                                f"received {received_size} bytes"
                            )

                            # Send error acknowledgment
                            ack_message = {
                                "type": "file_received",
                                "name": filename,
                                "status": "error",
                            }
                            self.send_command(device_id, ack_message)

                        # Clean up transfer state
                        device.file_transfer_state = None

                    except Exception as e:
                        logger.error(
                            f"Error finalizing file transfer from {device_id}: {e}"
                        )
                        device.file_transfer_state = None
                else:
                    logger.warning(
                        f"Received file_end from {device_id} without active transfer"
                    )

        else:
            device_id = self.find_device_id(client_socket)
            logger.warning(
                f"Unknown message type '{message_type}' from {device_id or client_addr}"
            )

        return self.find_device_id(client_socket)

    def find_device_id(self, client_socket: socket.socket) -> Optional[str]:
        """
        Find device_id for a given client socket.

        Args:
            client_socket: Socket to find device ID for

        Returns:
            Device ID if found, None otherwise
        """
        for device_id, device in self.devices.items():
            if device.client_socket == client_socket:
                return device_id
        return None

    def send_command(self, device_id: str, command_dict: Dict[str, Any]) -> bool:
        """
        Send JSON command to specific device using length-prefixed framing.

        Args:
            device_id: Target device identifier
            command_dict: Command dictionary to send

        Returns:
            True if command sent successfully, False otherwise
        """
        if device_id not in self.devices:
            logger.warning(f"Device {device_id} not connected")
            return False

        try:
            device = self.devices[device_id]
            json_data = json.dumps(command_dict).encode("utf-8")

            # Send length header (4 bytes, big-endian) followed by JSON data
            length_header = struct.pack(">I", len(json_data))
            device.client_socket.send(length_header + json_data)

            # Update device statistics
            device.increment_message_count("sent")

            logger.debug(
                f"Sent command to {device_id}: {command_dict.get('type', 'unknown')}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending command to {device_id}: {e}")
            self.error_occurred.emit(device_id, f"Command send error: {str(e)}")
            return False

    def broadcast_command(self, command_dict: Dict[str, Any]) -> int:
        """
        Send JSON command to all connected devices.

        Args:
            command_dict: Command dictionary to broadcast

        Returns:
            Number of devices that received the command successfully
        """
        success_count = 0
        for device_id in list(self.devices.keys()):
            if self.send_command(device_id, command_dict):
                success_count += 1

        logger.info(f"Broadcast command to {success_count}/{len(self.devices)} devices")
        return success_count

    def get_connected_devices(self) -> List[str]:
        """
        Get list of currently connected device IDs.

        Returns:
            List of connected device IDs
        """
        return list(self.clients.keys())

    def get_device_count(self) -> int:
        """
        Get number of currently connected devices.

        Returns:
            Number of connected devices
        """
        return len(self.clients)

    def is_device_connected(self, device_id: str) -> bool:
        """
        Check if a specific device is connected.

        Args:
            device_id: Device ID to check

        Returns:
            True if device is connected, False otherwise
        """
        return device_id in self.clients

    def stop_server(self):
        """Stop the JSON socket server and close all connections."""
        logger.info("Stopping JSON socket server...")
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # Close all client connections
        for device_id, client_socket in list(self.clients.items()):
            try:
                client_socket.close()
                self.device_disconnected.emit(device_id)
            except:
                pass

        self.clients.clear()
        logger.info("JSON socket server stopped")

    def get_session_directory(self) -> Optional[str]:
        """
        Get the current session directory for file storage.
        Uses SessionManager's session directory if available, otherwise falls back to creating own directory.

        Returns:
            Path to session directory or None if not available
        """
        try:
            # Use SessionManager's session directory if available
            if self.session_manager:
                session_folder = self.session_manager.get_session_folder()
                if session_folder:
                    session_dir = str(session_folder)
                    logger.debug(
                        f"Using SessionManager session directory: {session_dir}"
                    )
                    return session_dir
                else:
                    logger.warning(
                        "SessionManager available but no active session found"
                    )

            # Fallback: Create sessions directory if SessionManager is not available
            base_dir = os.path.join(os.getcwd(), "sessions")
            os.makedirs(base_dir, exist_ok=True)

            # Use current timestamp for session directory if no specific session is active
            import datetime

            session_name = datetime.datetime.now().strftime("session_%Y%m%d_%H%M%S")
            session_dir = os.path.join(base_dir, session_name)
            os.makedirs(session_dir, exist_ok=True)

            logger.debug(f"Fallback session directory: {session_dir}")
            return session_dir

        except Exception as e:
            logger.error(f"Failed to get session directory: {e}")
            return None

    def request_file_from_device(
        self, device_id: str, filepath: str, filetype: str = None
    ) -> bool:
        """
        Request a file from a specific device - Milestone 3.6

        Args:
            device_id: Target device identifier
            filepath: Path to file on device
            filetype: Optional file type descriptor

        Returns:
            True if request sent successfully, False otherwise
        """
        if device_id not in self.devices:
            logger.warning(f"Device {device_id} not connected")
            return False

        try:
            send_file_command = {
                "type": "send_file",
                "filepath": filepath,
                "filetype": filetype,
            }

            success = self.send_command(device_id, send_file_command)
            if success:
                logger.info(f"Requested file {filepath} from device {device_id}")
            else:
                logger.error(
                    f"Failed to request file {filepath} from device {device_id}"
                )

            return success

        except Exception as e:
            logger.error(f"Error requesting file from device {device_id}: {e}")
            return False

    def request_all_session_files(self, session_id: str) -> int:
        """
        Request all session files from all connected devices - Milestone 3.6

        Args:
            session_id: Session identifier

        Returns:
            Number of devices that received file requests
        """
        success_count = 0

        for device_id, device in self.devices.items():
            try:
                # Determine expected files based on device capabilities
                expected_files = self.get_expected_files_for_device(
                    device_id, session_id, device.capabilities
                )

                # Request each expected file
                for filepath in expected_files:
                    if self.request_file_from_device(device_id, filepath):
                        success_count += 1
                        # Add small delay between requests to avoid overwhelming the device
                        import time

                        time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error requesting files from device {device_id}: {e}")

        logger.info(
            f"Requested session files from {success_count} device file combinations"
        )
        return success_count

    def get_expected_files_for_device(
        self, device_id: str, session_id: str, capabilities: List[str]
    ) -> List[str]:
        """
        Get list of expected files for a device based on its capabilities

        Args:
            device_id: Device identifier
            session_id: Session identifier
            capabilities: Device capabilities

        Returns:
            List of expected file paths
        """
        expected_files = []

        # Base path on device (this should match the Android app's file structure)
        base_path = f"/storage/emulated/0/MultiSensorRecording/sessions/{session_id}"

        # Add expected files based on capabilities
        if "rgb_video" in capabilities or "camera" in capabilities:
            expected_files.append(f"{base_path}/{session_id}_{device_id}_rgb.mp4")

        if "thermal" in capabilities:
            expected_files.append(f"{base_path}/{session_id}_{device_id}_thermal.mp4")

        if "shimmer" in capabilities:
            expected_files.append(f"{base_path}/{session_id}_{device_id}_sensors.csv")

        logger.debug(f"Expected files for {device_id}: {expected_files}")
        return expected_files

    def cleanup(self):
        """Clean up server resources."""
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # Wait for client threads to finish (with timeout)
        for thread in self.client_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        self.client_threads.clear()
        logger.info("JSON socket server cleanup completed")


def decode_base64_image(base64_data: str) -> Optional[bytes]:
    """
    Decode base64 image data to bytes.

    Args:
        base64_data: Base64 encoded image string

    Returns:
        Decoded image bytes or None if decoding fails
    """
    try:
        # Remove data URL prefix if present
        if base64_data.startswith("data:image/"):
            base64_data = base64_data.split(",", 1)[1]

        return base64.b64decode(base64_data)
    except Exception as e:
        logger.error(f"Error decoding base64 image: {e}")
        return None


def create_command_message(command_type: str, **kwargs) -> Dict[str, Any]:
    """
    Create a standardized command message dictionary.

    Args:
        command_type: Type of command (e.g., 'start_recording', 'stop_recording')
        **kwargs: Additional command parameters

    Returns:
        Command message dictionary
    """
    import time

    command = {
        "type": "command",
        "command": command_type,
        "timestamp": time.time(),
        **kwargs,
    }

    return command
