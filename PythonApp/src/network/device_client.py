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
import ssl
import threading
import time
import uuid
from collections import defaultdict
from typing import Dict, Optional, Any, Tuple, List

from PyQt5.QtCore import QThread, pyqtSignal, QTimer


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

        # Enhanced features for reliable communication
        self._pending_acknowledgments: Dict[str, Dict[str, Any]] = {}
        self._ack_timeout = 10  # seconds
        self._retry_attempts = 3
        self._rate_limiter: Dict[str, List[float]] = defaultdict(list)
        self._max_requests_per_minute = 60
        
        # SSL/TLS configuration
        self._ssl_enabled = False
        self._ssl_context: Optional[ssl.SSLContext] = None
        self._ssl_certfile = None
        self._ssl_keyfile = None
        
        # Device capability management
        self._supported_capabilities = {
            "recording", "streaming", "calibration", 
            "thermal_imaging", "gsr_monitoring", "audio_capture"
        }
        
        # Performance monitoring
        self._message_stats = {
            "sent": 0, "received": 0, "errors": 0, 
            "avg_latency": 0.0, "connection_count": 0
        }

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

            # Configure SSL if enabled
            if self._ssl_enabled and self._ssl_context:
                self.server_socket = self._ssl_context.wrap_socket(
                    self.server_socket, server_side=True
                )
                print(f"[DEBUG_LOG] SSL/TLS enabled for secure communication")

            self.server_socket.bind(("0.0.0.0", self.server_port))
            self.server_socket.listen(5)

            print(f"[DEBUG_LOG] DeviceClient server started on port {self.server_port}")

            while self.running:
                try:
                    # Accept incoming connections with timeout
                    client_socket, address = self.server_socket.accept()
                    
                    # Check rate limiting before processing connection
                    if not self._check_rate_limit(address[0]):
                        print(f"[DEBUG_LOG] Rate limited connection from {address}")
                        client_socket.close()
                        continue
                        
                    print(f"[DEBUG_LOG] New connection from {address}")
                    self._message_stats["connection_count"] += 1

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

    def configure_ssl(self, certfile: str, keyfile: str, ca_certs: Optional[str] = None) -> bool:
        """
        Configure SSL/TLS encryption for secure communication.
        
        Args:
            certfile (str): Path to server certificate file
            keyfile (str): Path to server private key file  
            ca_certs (str, optional): Path to CA certificates for client verification
            
        Returns:
            bool: True if SSL configuration successful, False otherwise
        """
        try:
            self._ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self._ssl_context.load_cert_chain(certfile, keyfile)
            
            if ca_certs:
                self._ssl_context.load_verify_locations(ca_certs)
                self._ssl_context.verify_mode = ssl.CERT_REQUIRED
            else:
                self._ssl_context.verify_mode = ssl.CERT_NONE
                
            self._ssl_enabled = True
            self._ssl_certfile = certfile
            self._ssl_keyfile = keyfile
            
            print(f"[DEBUG_LOG] SSL/TLS configured successfully")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"SSL configuration failed: {str(e)}")
            return False

    def _check_rate_limit(self, device_ip: str) -> bool:
        """
        Check if device exceeds rate limiting thresholds.
        
        Args:
            device_ip (str): IP address of the device
            
        Returns:
            bool: True if within rate limit, False if exceeded
        """
        current_time = time.time()
        requests = self._rate_limiter[device_ip]
        
        # Remove requests older than 1 minute
        requests[:] = [req_time for req_time in requests if current_time - req_time < 60]
        
        if len(requests) >= self._max_requests_per_minute:
            print(f"[DEBUG_LOG] Rate limit exceeded for {device_ip}")
            return False
            
        requests.append(current_time)
        return True

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
        require_ack: bool = True,
    ) -> bool:
        """
        Send a command to a specific device using JSON protocol with acknowledgment support.

        Args:
            device_index (int): Index of the target device
            command (str): Command to send (START, STOP, CALIBRATE, etc.)
            parameters (dict): Optional command parameters
            require_ack (bool): Whether to require acknowledgment for reliable delivery

        Returns:
            bool: True if command sent successfully, False otherwise
        """
        print(f"[DEBUG_LOG] Sending command '{command}' to device {device_index}")

        with self._device_lock:
            if device_index not in self.devices:
                print(f"[DEBUG_LOG] Device {device_index} not found")
                return False

            device = self.devices[device_index]
            
            # Check rate limiting
            if not self._check_rate_limit(device["ip"]):
                self.error_occurred.emit(f"Rate limit exceeded for device {device_index}")
                return False

            try:
                # Generate unique message ID for acknowledgment tracking
                message_id = str(uuid.uuid4())
                timestamp = time.time()
                
                # Format command as JSON message
                message = {
                    "type": "command",
                    "command": command,
                    "parameters": parameters or {},
                    "timestamp": timestamp,
                    "message_id": message_id,
                    "require_ack": require_ack,
                }

                # Send command over socket connection
                device_socket = device["socket"]
                json_data = json.dumps(message).encode("utf-8")
                device_socket.send(json_data)
                
                # Track for acknowledgment if required
                if require_ack:
                    self._pending_acknowledgments[message_id] = {
                        "device_index": device_index,
                        "command": command,
                        "timestamp": timestamp,
                        "attempts": 1,
                        "max_attempts": self._retry_attempts,
                    }
                    
                    # Start acknowledgment timeout timer
                    QTimer.singleShot(
                        self._ack_timeout * 1000,
                        lambda: self._handle_ack_timeout(message_id)
                    )

                self._message_stats["sent"] += 1
                print(
                    f"[DEBUG_LOG] Command '{command}' sent successfully to device {device_index}"
                    f" (msg_id: {message_id})"
                )
                return True

            except Exception as e:
                error_msg = f"Failed to send command '{command}' to device {device_index}: {str(e)}"
                self.error_occurred.emit(error_msg)
                print(f"[DEBUG_LOG] {error_msg}")
                self._message_stats["errors"] += 1

                # Remove failed device connection
                self._remove_failed_device(device_index)
                return False

    def _handle_ack_timeout(self, message_id: str) -> None:
        """
        Handle acknowledgment timeout for reliable message delivery.
        
        Args:
            message_id (str): ID of the message that timed out
        """
        if message_id not in self._pending_acknowledgments:
            return
            
        ack_info = self._pending_acknowledgments[message_id]
        device_index = ack_info["device_index"]
        command = ack_info["command"]
        attempts = ack_info["attempts"]
        max_attempts = ack_info["max_attempts"]
        
        if attempts < max_attempts:
            # Retry sending the command
            print(f"[DEBUG_LOG] Retrying command '{command}' to device {device_index} "
                  f"(attempt {attempts + 1}/{max_attempts})")
            
            ack_info["attempts"] += 1
            ack_info["timestamp"] = time.time()
            
            # Resend the command
            with self._device_lock:
                if device_index in self.devices:
                    try:
                        device_socket = self.devices[device_index]["socket"]
                        message = {
                            "type": "command",
                            "command": command,
                            "parameters": ack_info.get("parameters", {}),
                            "timestamp": ack_info["timestamp"],
                            "message_id": message_id,
                            "require_ack": True,
                            "retry_attempt": attempts + 1,
                        }
                        
                        json_data = json.dumps(message).encode("utf-8")
                        device_socket.send(json_data)
                        
                        # Reset timeout timer
                        QTimer.singleShot(
                            self._ack_timeout * 1000,
                            lambda: self._handle_ack_timeout(message_id)
                        )
                        
                    except Exception as e:
                        print(f"[DEBUG_LOG] Retry failed for message {message_id}: {e}")
                        del self._pending_acknowledgments[message_id]
                        self._remove_failed_device(device_index)
        else:
            # Max attempts reached, give up
            print(f"[DEBUG_LOG] Max retry attempts reached for message {message_id}")
            del self._pending_acknowledgments[message_id]
            self.error_occurred.emit(
                f"Command '{command}' failed after {max_attempts} attempts to device {device_index}"
            )

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

    def negotiate_capabilities(self, device_index: int, requested_capabilities: List[str]) -> Dict[str, bool]:
        """
        Negotiate device capabilities to determine supported features.
        
        Args:
            device_index (int): Index of the target device
            requested_capabilities (List[str]): List of requested capabilities
            
        Returns:
            Dict[str, bool]: Dictionary mapping capabilities to availability
        """
        print(f"[DEBUG_LOG] Negotiating capabilities with device {device_index}")
        
        with self._device_lock:
            if device_index not in self.devices:
                return {}
                
            device = self.devices[device_index]
            device_capabilities = set(device.get("capabilities", []))
            
            # Check which requested capabilities are available
            capability_status = {}
            for capability in requested_capabilities:
                if capability in self._supported_capabilities and capability in device_capabilities:
                    capability_status[capability] = True
                else:
                    capability_status[capability] = False
                    
            # Send capability negotiation request
            negotiation_message = {
                "type": "capability_negotiation",
                "requested_capabilities": requested_capabilities,
                "supported_capabilities": list(self._supported_capabilities),
                "timestamp": time.time(),
                "message_id": str(uuid.uuid4()),
            }
            
            try:
                device_socket = device["socket"]
                json_data = json.dumps(negotiation_message).encode("utf-8")
                device_socket.send(json_data)
                
                print(f"[DEBUG_LOG] Capability negotiation completed for device {device_index}")
                return capability_status
                
            except Exception as e:
                self.error_occurred.emit(f"Capability negotiation failed for device {device_index}: {str(e)}")
                return {}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics and statistics for monitoring and analysis.
        
        Returns:
            Dict[str, Any]: Performance metrics including latency, throughput, error rates
        """
        with self._device_lock:
            connected_devices = len(self.devices)
            
        return {
            "connected_devices": connected_devices,
            "total_connections": self._message_stats["connection_count"],
            "messages_sent": self._message_stats["sent"],
            "messages_received": self._message_stats["received"],
            "error_count": self._message_stats["errors"],
            "average_latency_ms": self._message_stats["avg_latency"] * 1000,
            "pending_acknowledgments": len(self._pending_acknowledgments),
            "ssl_enabled": self._ssl_enabled,
            "rate_limit_per_minute": self._max_requests_per_minute,
        }
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
        Process incoming messages from devices with enhanced protocol support.

        Args:
            device_id: ID of the device that sent the message
            message: Parsed message data
        """
        message_type = message.get("type")
        timestamp = time.time()

        if message_type == "heartbeat":
            # Update last heartbeat time
            with self._device_lock:
                if device_id in self.devices:
                    self.devices[device_id]["last_heartbeat"] = timestamp

        elif message_type == "acknowledgment":
            # Handle command acknowledgment for reliable delivery
            message_id = message.get("message_id")
            if message_id and message_id in self._pending_acknowledgments:
                ack_info = self._pending_acknowledgments[message_id]
                
                # Calculate latency
                latency = timestamp - ack_info["timestamp"]
                self._update_latency_stats(latency)
                
                del self._pending_acknowledgments[message_id]
                print(f"[DEBUG_LOG] Received acknowledgment for message {message_id} "
                      f"(latency: {latency:.3f}s)")

        elif message_type == "frame":
            # Emit frame received signal
            frame_type = message.get("frame_type", "unknown")
            frame_data = message.get("data", b"")
            self.frame_received.emit(device_id, frame_type, frame_data)

        elif message_type == "status":
            # Emit status update signal
            status_info = message.get("status", {})
            self.status_updated.emit(device_id, status_info)

        elif message_type == "capability_response":
            # Handle capability negotiation response
            device_capabilities = message.get("capabilities", [])
            with self._device_lock:
                if device_id in self.devices:
                    self.devices[device_id]["capabilities"] = device_capabilities
            print(f"[DEBUG_LOG] Updated capabilities for device {device_id}: {device_capabilities}")

        elif message_type == "error":
            # Handle error messages from device
            error_msg = message.get("error", "Unknown error")
            self.error_occurred.emit(f"Device {device_id} error: {error_msg}")

        else:
            print(
                f"[DEBUG_LOG] Unknown message type from device {device_id}: {message_type}"
            )

        self._message_stats["received"] += 1

    def _update_latency_stats(self, latency: float) -> None:
        """
        Update latency statistics for performance monitoring.
        
        Args:
            latency (float): Message round-trip latency in seconds
        """
        # Simple exponential moving average
        alpha = 0.1
        if self._message_stats["avg_latency"] == 0:
            self._message_stats["avg_latency"] = latency
        else:
            self._message_stats["avg_latency"] = (
                alpha * latency + (1 - alpha) * self._message_stats["avg_latency"]
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
