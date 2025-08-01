"""
Device Client for Multi-Sensor Recording System Controller

This module provides actual device communication functionality for handling
network communication with Android devices running the recording application.
It implements socket-based communication, device discovery, command protocols,
and connection management.

Author: Multi-Sensor Recording System Team
Date: 2025-01-01
Milestone: 4.1 - Device Communication Implementation
"""

import json
import socket
import threading
import time
from typing import Dict, Optional, Any

from PyQt5.QtCore import QThread, pyqtSignal


class DeviceClient(QThread):
    """
    Device communication client for managing connections with Android devices.

    This class implements socket-based communication with Android devices running
    the recording application. It handles device discovery, connection management,
    command sending, and data reception.

    Features:
    - Socket-based communication with Android devices
    - Device discovery and connection management
    - Command sending (START, STOP, CALIBRATE, etc.)
    - Video frame reception and processing
    - Status monitoring and error handling
    - Reconnection logic for dropped connections
    - Multi-device support with concurrent connections
    """

    # Signals for communicating with the main GUI thread
    device_connected = pyqtSignal(int, str)  # device_index, device_info
    device_disconnected = pyqtSignal(int)  # device_index
    frame_received = pyqtSignal(int, str, bytes)  # device_index, frame_type, frame_data
    status_updated = pyqtSignal(int, dict)  # device_index, status_info
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices: Dict[int, Dict[str, Any]] = (
            {}
        )  # Dictionary to store device connections
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.device_counter = 0
        self._device_lock = threading.Lock()

        # Network configuration
        self.server_port = 8080
        self.buffer_size = 4096
        self.connection_timeout = 30  # seconds
        self.heartbeat_interval = 5  # seconds
        self.max_reconnect_attempts = 3

    def run(self):
        """
        Main thread execution method - implements the server socket communication loop.

        This method sets up a server socket to listen for incoming device connections,
        handles new connections, and manages the main communication loop for all
        connected devices.
        """
        self.running = True

        try:
            # Set up server socket to listen for device connections
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # Non-blocking accept with timeout

            self.server_socket.bind(("0.0.0.0", self.server_port))
            self.server_socket.listen(5)

            print(f"[DEBUG_LOG] DeviceClient server started on port {self.server_port}")

            while self.running:
                try:
                    # Accept incoming connections with timeout
                    client_socket, address = self.server_socket.accept()
                    print(f"[DEBUG_LOG] New connection from {address}")

                    # Handle the new device connection in a separate thread
                    connection_thread = threading.Thread(
                        target=self.handle_device_connection,
                        args=(client_socket, address),
                        daemon=True,
                    )
                    connection_thread.start()

                except socket.timeout:
                    # Timeout is expected - continue the loop
                    continue
                except Exception as e:
                    if self.running:  # Only log if we're supposed to be running
                        self.error_occurred.emit(f"Server socket error: {str(e)}")
                    break

        except Exception as e:
            self.error_occurred.emit(f"Failed to start server: {str(e)}")
        finally:
            self._cleanup_server_socket()

        print("[DEBUG_LOG] DeviceClient thread stopped")

    def connect_to_device(self, device_ip: str, device_port: int = 8080) -> bool:
        """
        Connect to a specific device using socket connection.

        Args:
            device_ip (str): IP address of the device
            device_port (int): Port number for connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        print(
            f"[DEBUG_LOG] Attempting to connect to device at {device_ip}:{device_port}"
        )

        try:
            # Create socket connection to device
            device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            device_socket.settimeout(self.connection_timeout)
            device_socket.connect((device_ip, device_port))

            # Perform handshake and authentication
            handshake_data = {
                "type": "handshake",
                "client_type": "recording_controller",
                "protocol_version": "1.0",
                "timestamp": time.time(),
            }

            # Send handshake
            handshake_message = json.dumps(handshake_data).encode("utf-8")
            device_socket.send(handshake_message)

            # Wait for handshake response
            response = device_socket.recv(self.buffer_size)
            response_data = json.loads(response.decode("utf-8"))

            if response_data.get("status") == "accepted":
                # Register device in active connections
                with self._device_lock:
                    device_id = self.device_counter
                    self.device_counter += 1

                    self.devices[device_id] = {
                        "socket": device_socket,
                        "ip": device_ip,
                        "port": device_port,
                        "status": "connected",
                        "last_heartbeat": time.time(),
                        "device_info": response_data.get("device_info", {}),
                        "capabilities": response_data.get("capabilities", []),
                    }

                # Emit connection signal
                device_info = f"{device_ip}:{device_port}"
                self.device_connected.emit(device_id, device_info)

                print(
                    f"[DEBUG_LOG] Successfully connected to device {device_id} at {device_ip}:{device_port}"
                )
                return True
            else:
                # Handshake failed
                device_socket.close()
                error_msg = response_data.get("error", "Handshake rejected")
                self.error_occurred.emit(
                    f"Handshake failed with {device_ip}: {error_msg}"
                )
                return False

        except socket.timeout:
            self.error_occurred.emit(f"Connection timeout to {device_ip}:{device_port}")
            return False
        except ConnectionRefusedError:
            self.error_occurred.emit(f"Connection refused by {device_ip}:{device_port}")
            return False
        except json.JSONDecodeError:
            self.error_occurred.emit(f"Invalid handshake response from {device_ip}")
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to connect to {device_ip}: {str(e)}")
            return False

    def disconnect_device(self, device_index: int) -> None:
        """
        Disconnect from a specific device and clean up resources.

        Args:
            device_index (int): Index of the device to disconnect
        """
        print(f"[DEBUG_LOG] Disconnecting device {device_index}")

        with self._device_lock:
            if device_index in self.devices:
                device = self.devices[device_index]

                try:
                    # Send disconnect notification to device
                    disconnect_message = {
                        "type": "disconnect",
                        "reason": "client_initiated",
                        "timestamp": time.time(),
                    }

                    device_socket = device["socket"]
                    device_socket.send(json.dumps(disconnect_message).encode("utf-8"))

                    # Close socket connection gracefully
                    device_socket.shutdown(socket.SHUT_RDWR)
                    device_socket.close()

                except Exception as e:
                    print(f"[DEBUG_LOG] Error during disconnect cleanup: {e}")

                # Remove device from active connections
                del self.devices[device_index]

                # Emit disconnection signal
                self.device_disconnected.emit(device_index)

                print(f"[DEBUG_LOG] Device {device_index} disconnected successfully")
            else:
                print(f"[DEBUG_LOG] Device {device_index} not found for disconnection")

    def send_command(
        self,
        device_index: int,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a command to a specific device using JSON protocol.

        Args:
            device_index (int): Index of the target device
            command (str): Command to send (START, STOP, CALIBRATE, etc.)
            parameters (dict): Optional command parameters

        Returns:
            bool: True if command sent successfully, False otherwise
        """
        print(f"[DEBUG_LOG] Sending command '{command}' to device {device_index}")

        with self._device_lock:
            if device_index not in self.devices:
                print(f"[DEBUG_LOG] Device {device_index} not found")
                return False

            try:
                # Format command as JSON message
                message = {
                    "type": "command",
                    "command": command,
                    "parameters": parameters or {},
                    "timestamp": time.time(),
                    "message_id": f"{device_index}_{int(time.time() * 1000)}",
                }

                # Send command over socket connection
                device_socket = self.devices[device_index]["socket"]
                json_data = json.dumps(message).encode("utf-8")
                device_socket.send(json_data)

                # TODO: Implement acknowledgment handling and timeout/retry logic
                # For now, assume success if no exception is raised

                print(
                    f"[DEBUG_LOG] Command '{command}' sent successfully to device {device_index}"
                )
                return True

            except Exception as e:
                error_msg = f"Failed to send command '{command}' to device {device_index}: {str(e)}"
                self.error_occurred.emit(error_msg)
                print(f"[DEBUG_LOG] {error_msg}")

                # Remove failed device connection
                self._remove_failed_device(device_index)
                return False

    def stop_client(self) -> None:
        """
        Stop the device client and close all connections with proper cleanup.
        """
        print("[DEBUG_LOG] Stopping DeviceClient")
        self.running = False

        # Close all device connections
        with self._device_lock:
            for device_index in list(self.devices.keys()):
                self.disconnect_device(device_index)

        # Clean up server socket
        self._cleanup_server_socket()

        # Wait for thread to finish
        self.quit()
        self.wait()

        print("[DEBUG_LOG] DeviceClient stopped successfully")

    def get_connected_devices(self) -> Dict[int, Dict[str, Any]]:
        """
        Get list of currently connected devices with their information.

        Returns:
            dict: Dictionary of connected devices with their information including:
                  - Device IP and port
                  - Connection status
                  - Last heartbeat timestamp
                  - Device capabilities and status
        """
        with self._device_lock:
            # Return a copy of devices data with additional computed information
            devices_info = {}
            for device_id, device_data in self.devices.items():
                devices_info[device_id] = {
                    "ip": device_data["ip"],
                    "port": device_data["port"],
                    "status": device_data["status"],
                    "last_heartbeat": device_data["last_heartbeat"],
                    "connection_time": time.time()
                    - device_data.get("connected_at", time.time()),
                    "device_info": device_data.get("device_info", {}),
                    "capabilities": device_data.get("capabilities", []),
                }

            return devices_info

    def handle_device_connection(
        self, client_socket: socket.socket, address: tuple
    ) -> None:
        """
        Handle a new device connection from the server socket.

        Args:
            client_socket: Socket object for the connected device
            address: Address tuple (ip, port) of the connected device
        """
        print(f"[DEBUG_LOG] Handling new device connection from {address}")

        try:
            # Perform device identification and authentication
            client_socket.settimeout(self.connection_timeout)

            # Wait for handshake from device
            handshake_data = client_socket.recv(self.buffer_size)
            handshake = json.loads(handshake_data.decode("utf-8"))

            if handshake.get("type") == "handshake":
                # Process handshake and send response
                response = {
                    "status": "accepted",
                    "server_info": {"type": "recording_controller", "version": "1.0"},
                    "timestamp": time.time(),
                }

                client_socket.send(json.dumps(response).encode("utf-8"))

                # Register device in active connections
                with self._device_lock:
                    device_id = self.device_counter
                    self.device_counter += 1

                    self.devices[device_id] = {
                        "socket": client_socket,
                        "ip": address[0],
                        "port": address[1],
                        "status": "connected",
                        "last_heartbeat": time.time(),
                        "connected_at": time.time(),
                        "device_info": handshake.get("device_info", {}),
                        "capabilities": handshake.get("capabilities", []),
                    }

                # Emit connection signal
                device_info = f"{address[0]}:{address[1]}"
                self.device_connected.emit(device_id, device_info)

                # Start monitoring thread for this device
                monitor_thread = threading.Thread(
                    target=self._monitor_device, args=(device_id,), daemon=True
                )
                monitor_thread.start()

                print(
                    f"[DEBUG_LOG] Device {device_id} registered and monitoring started"
                )

            else:
                # Invalid handshake
                response = {
                    "status": "rejected",
                    "error": "Invalid handshake",
                    "timestamp": time.time(),
                }
                client_socket.send(json.dumps(response).encode("utf-8"))
                client_socket.close()

        except Exception as e:
            print(f"[DEBUG_LOG] Error handling device connection: {e}")
            try:
                client_socket.close()
            except:
                pass

    def _monitor_device(self, device_id: int) -> None:
        """
        Monitor a specific device for incoming messages and heartbeats.

        Args:
            device_id: ID of the device to monitor
        """
        print(f"[DEBUG_LOG] Starting device monitoring for device {device_id}")

        while self.running and device_id in self.devices:
            try:
                with self._device_lock:
                    if device_id not in self.devices:
                        break
                    device_socket = self.devices[device_id]["socket"]

                # Set a short timeout for non-blocking receive
                device_socket.settimeout(1.0)

                try:
                    data = device_socket.recv(self.buffer_size)
                    if data:
                        # Process received data
                        message = json.loads(data.decode("utf-8"))
                        self._process_device_message(device_id, message)
                    else:
                        # Socket closed by device
                        print(f"[DEBUG_LOG] Device {device_id} disconnected")
                        self._remove_failed_device(device_id)
                        break

                except socket.timeout:
                    # Timeout is normal - continue monitoring
                    continue

            except Exception as e:
                print(f"[DEBUG_LOG] Device {device_id} monitoring error: {e}")
                self._remove_failed_device(device_id)
                break

        print(f"[DEBUG_LOG] Device {device_id} monitoring stopped")

    def _process_device_message(self, device_id: int, message: Dict[str, Any]) -> None:
        """
        Process incoming messages from devices.

        Args:
            device_id: ID of the device that sent the message
            message: Parsed message data
        """
        message_type = message.get("type")

        if message_type == "heartbeat":
            # Update last heartbeat time
            with self._device_lock:
                if device_id in self.devices:
                    self.devices[device_id]["last_heartbeat"] = time.time()

        elif message_type == "frame":
            # Emit frame received signal
            frame_type = message.get("frame_type", "unknown")
            frame_data = message.get("data", b"")
            self.frame_received.emit(device_id, frame_type, frame_data)

        elif message_type == "status":
            # Emit status update signal
            status_info = message.get("status", {})
            self.status_updated.emit(device_id, status_info)

        else:
            print(
                f"[DEBUG_LOG] Unknown message type from device {device_id}: {message_type}"
            )

    def _remove_failed_device(self, device_id: int) -> None:
        """
        Remove a failed device connection and clean up resources.

        Args:
            device_id: ID of the device to remove
        """
        with self._device_lock:
            if device_id in self.devices:
                try:
                    self.devices[device_id]["socket"].close()
                except:
                    pass

                del self.devices[device_id]
                self.device_disconnected.emit(device_id)
                print(f"[DEBUG_LOG] Removed failed device {device_id}")

    def _cleanup_server_socket(self) -> None:
        """Clean up the server socket."""
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
