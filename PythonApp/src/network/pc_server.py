"""
PC TCP Server for Android Device Communication

This module implements a TCP server that accepts connections from Android devices
and handles the JsonMessage protocol for bidirectional communication.
It provides the PC-side counterpart to the Android JsonSocketClient.

Features:
- TCP server on configurable port (default 9000)
- JsonMessage protocol support
- Multi-device connection management
- Real-time command and data exchange
- Device capability discovery and management
- File transfer support
- Automatic reconnection handling

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import asyncio
import json
import logging
import socket
import struct
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Set
import threading
from concurrent.futures import ThreadPoolExecutor


@dataclass
class ConnectedDevice:
    """Information about a connected Android device"""
    device_id: str
    capabilities: List[str]
    connection_time: float
    last_heartbeat: float
    status: Dict[str, Any]
    socket: socket.socket
    address: tuple


@dataclass
class JsonMessage:
    """Base class for JSON messages"""
    type: str = ""
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> Optional['JsonMessage']:
        """Parse JSON string to message object"""
        try:
            data = json.loads(json_str)
            message_type = data.get('type')
            
            # Route to appropriate message class based on type
            if message_type == 'hello':
                return HelloMessage.from_dict(data)
            elif message_type == 'status':
                return StatusMessage.from_dict(data)
            elif message_type == 'sensor_data':
                return SensorDataMessage.from_dict(data)
            elif message_type == 'ack':
                return AckMessage.from_dict(data)
            elif message_type == 'file_info':
                return FileInfoMessage.from_dict(data)
            elif message_type == 'file_chunk':
                return FileChunkMessage.from_dict(data)
            elif message_type == 'file_end':
                return FileEndMessage.from_dict(data)
            else:
                # Generic message for unknown types
                return JsonMessage(type=message_type, **{k: v for k, v in data.items() if k != 'type'})
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.error(f"Error parsing JSON message: {e}")
            return None


@dataclass
class HelloMessage(JsonMessage):
    """Device introduction message"""
    device_id: str = ""
    capabilities: List[str] = None
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "hello"
        super().__post_init__()
        if self.capabilities is None:
            self.capabilities = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelloMessage':
        return cls(
            type=data.get('type', 'hello'),
            device_id=data.get('device_id', ''),
            capabilities=data.get('capabilities', []),
            timestamp=data.get('timestamp')
        )


@dataclass
class StatusMessage(JsonMessage):
    """Device status update message"""
    battery: Optional[int] = None
    storage: Optional[str] = None
    temperature: Optional[float] = None
    recording: bool = False
    connected: bool = True
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "status"
        super().__post_init__()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusMessage':
        return cls(
            type=data.get('type', 'status'),
            battery=data.get('battery'),
            storage=data.get('storage'),
            temperature=data.get('temperature'),
            recording=data.get('recording', False),
            connected=data.get('connected', True),
            timestamp=data.get('timestamp')
        )


@dataclass
class SensorDataMessage(JsonMessage):
    """Sensor data update message"""
    values: Dict[str, float] = None
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "sensor_data"
        super().__post_init__()
        if self.values is None:
            self.values = {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorDataMessage':
        return cls(
            type=data.get('type', 'sensor_data'),
            values=data.get('values', {}),
            timestamp=data.get('timestamp')
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorDataMessage':
        return cls(
            type=data.get('type', 'sensor_data'),
            values=data.get('values', {}),
            timestamp=data.get('timestamp')
        )


@dataclass
class AckMessage(JsonMessage):
    """Acknowledgment message"""
    cmd: str = ""
    status: str = "ok"  # "ok" or "error"
    message: Optional[str] = None
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "ack"
        super().__post_init__()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AckMessage':
        return cls(
            type=data.get('type', 'ack'),
            cmd=data.get('cmd', ''),
            status=data.get('status', 'ok'),
            message=data.get('message'),
            timestamp=data.get('timestamp')
        )


@dataclass
class FileInfoMessage(JsonMessage):
    """File transfer info message"""
    name: str = ""
    size: int = 0
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "file_info"
        super().__post_init__()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileInfoMessage':
        return cls(
            type=data.get('type', 'file_info'),
            name=data.get('name', ''),
            size=data.get('size', 0),
            timestamp=data.get('timestamp')
        )


@dataclass
class FileChunkMessage(JsonMessage):
    """File transfer chunk message"""
    seq: int = 0
    data: str = ""  # Base64 encoded
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "file_chunk"
        super().__post_init__()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileChunkMessage':
        return cls(
            type=data.get('type', 'file_chunk'),
            seq=data.get('seq', 0),
            data=data.get('data', ''),
            timestamp=data.get('timestamp')
        )


@dataclass
class FileEndMessage(JsonMessage):
    """File transfer end message"""
    name: str = ""
    
    def __post_init__(self):
        if not hasattr(self, 'type') or not self.type:
            self.type = "file_end"
        super().__post_init__()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileEndMessage':
        return cls(
            type=data.get('type', 'file_end'),
            name=data.get('name', ''),
            timestamp=data.get('timestamp')
        )


# Command messages (PC to Android)
@dataclass
class StartRecordCommand(JsonMessage):
    """Command to start recording"""
    session_id: str = ""
    record_video: bool = True
    record_thermal: bool = True
    record_shimmer: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        self.type = "start_record"


@dataclass
class StopRecordCommand(JsonMessage):
    """Command to stop recording"""
    
    def __post_init__(self):
        super().__post_init__()
        self.type = "stop_record"


@dataclass
class FlashSyncCommand(JsonMessage):
    """Command to trigger LED flash sync"""
    duration_ms: int = 200
    sync_id: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = "flash_sync"


@dataclass
class BeepSyncCommand(JsonMessage):
    """Command to trigger audio beep sync"""
    frequency_hz: int = 1000
    duration_ms: int = 200
    volume: float = 0.8
    sync_id: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = "beep_sync"


class PCServer:
    """
    PC TCP Server for Android Device Communication
    
    Implements the server-side counterpart to Android's JsonSocketClient,
    providing bidirectional communication using the JsonMessage protocol.
    """
    
    def __init__(self, port: int = 9000, logger: Optional[logging.Logger] = None):
        """Initialize PC server"""
        self.port = port
        self.logger = logger or logging.getLogger(__name__)
        
        # Server state
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.connected_devices: Dict[str, ConnectedDevice] = {}
        
        # Threading
        self.server_thread: Optional[threading.Thread] = None
        self.client_threads: Dict[str, threading.Thread] = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Callbacks
        self.message_callbacks: List[Callable[[str, JsonMessage], None]] = []
        self.device_callbacks: List[Callable[[str, ConnectedDevice], None]] = []
        self.disconnect_callbacks: List[Callable[[str], None]] = []
        
        # Configuration
        self.heartbeat_interval = 30.0  # seconds
        self.heartbeat_timeout = 60.0   # seconds
        self.message_buffer_size = 4096
        self.max_message_size = 1024 * 1024  # 1MB
        
        self.logger.info(f"PCServer initialized for port {port}")
    
    def start(self) -> bool:
        """Start the TCP server"""
        try:
            if self.is_running:
                self.logger.warning("Server already running")
                return True
            
            self.logger.info(f"Starting PC server on port {self.port}...")
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            
            self.is_running = True
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop, name="PCServer")
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Start heartbeat monitoring
            self.thread_pool.submit(self._heartbeat_monitor)
            
            self.logger.info(f"PC server started successfully on port {self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start PC server: {e}")
            self.is_running = False
            return False
    
    def stop(self) -> None:
        """Stop the TCP server"""
        try:
            self.logger.info("Stopping PC server...")
            self.is_running = False
            
            # Close all client connections
            for device_id in list(self.connected_devices.keys()):
                self._disconnect_device(device_id)
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            # Wait for server thread
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            self.logger.info("PC server stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping PC server: {e}")
    
    def send_message(self, device_id: str, message: JsonMessage) -> bool:
        """Send message to specific device"""
        if device_id not in self.connected_devices:
            self.logger.error(f"Device not connected: {device_id}")
            return False
        
        try:
            device = self.connected_devices[device_id]
            json_data = message.to_json()
            json_bytes = json_data.encode('utf-8')
            
            # Send length-prefixed message
            length_header = struct.pack('>I', len(json_bytes))
            device.socket.sendall(length_header + json_bytes)
            
            self.logger.debug(f"Sent message to {device_id}: {message.type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message to {device_id}: {e}")
            self._disconnect_device(device_id)
            return False
    
    def broadcast_message(self, message: JsonMessage) -> int:
        """Broadcast message to all connected devices"""
        success_count = 0
        for device_id in list(self.connected_devices.keys()):
            if self.send_message(device_id, message):
                success_count += 1
        return success_count
    
    def get_connected_devices(self) -> Dict[str, ConnectedDevice]:
        """Get copy of connected devices"""
        return self.connected_devices.copy()
    
    def add_message_callback(self, callback: Callable[[str, JsonMessage], None]) -> None:
        """Add callback for incoming messages"""
        self.message_callbacks.append(callback)
    
    def add_device_callback(self, callback: Callable[[str, ConnectedDevice], None]) -> None:
        """Add callback for device connections"""
        self.device_callbacks.append(callback)
    
    def add_disconnect_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for device disconnections"""
        self.disconnect_callbacks.append(callback)
    
    def _server_loop(self) -> None:
        """Main server loop accepting connections"""
        try:
            while self.is_running:
                try:
                    # Accept new connection
                    client_socket, address = self.server_socket.accept()
                    self.logger.info(f"New connection from {address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        name=f"Client-{address[0]}:{address[1]}"
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.is_running:
                        self.logger.error(f"Server socket error: {e}")
                        break
                    
        except Exception as e:
            self.logger.error(f"Error in server loop: {e}")
        finally:
            self.is_running = False
    
    def _handle_client(self, client_socket: socket.socket, address: tuple) -> None:
        """Handle individual client connection"""
        device_id = None
        try:
            client_socket.settimeout(30.0)  # 30 second timeout
            
            while self.is_running:
                # Read length header (4 bytes)
                length_data = self._recv_exact(client_socket, 4)
                if not length_data:
                    break
                
                message_length = struct.unpack('>I', length_data)[0]
                
                if message_length <= 0 or message_length > self.max_message_size:
                    self.logger.error(f"Invalid message length: {message_length}")
                    break
                
                # Read message data
                message_data = self._recv_exact(client_socket, message_length)
                if not message_data:
                    break
                
                # Parse JSON message
                json_string = message_data.decode('utf-8')
                message = JsonMessage.from_json(json_string)
                
                if not message:
                    self.logger.warning(f"Failed to parse message from {address}")
                    continue
                
                # Handle hello message to establish device identity
                if isinstance(message, HelloMessage) and not device_id:
                    device_id = message.device_id
                    device = ConnectedDevice(
                        device_id=device_id,
                        capabilities=message.capabilities,
                        connection_time=time.time(),
                        last_heartbeat=time.time(),
                        status={},
                        socket=client_socket,
                        address=address
                    )
                    
                    self.connected_devices[device_id] = device
                    self.client_threads[device_id] = threading.current_thread()
                    
                    self.logger.info(f"Device registered: {device_id} with capabilities: {message.capabilities}")
                    
                    # Notify callbacks
                    for callback in self.device_callbacks:
                        try:
                            callback(device_id, device)
                        except Exception as e:
                            self.logger.error(f"Error in device callback: {e}")
                
                # Update last heartbeat
                if device_id and device_id in self.connected_devices:
                    self.connected_devices[device_id].last_heartbeat = time.time()
                
                # Process message
                if device_id:
                    self.logger.debug(f"Received {message.type} from {device_id}")
                    
                    # Notify message callbacks
                    for callback in self.message_callbacks:
                        try:
                            callback(device_id, message)
                        except Exception as e:
                            self.logger.error(f"Error in message callback: {e}")
                
        except socket.timeout:
            self.logger.warning(f"Client {address} timed out")
        except Exception as e:
            self.logger.error(f"Error handling client {address}: {e}")
        finally:
            # Clean up connection
            if device_id:
                self._disconnect_device(device_id)
            else:
                try:
                    client_socket.close()
                except:
                    pass
    
    def _recv_exact(self, sock: socket.socket, length: int) -> Optional[bytes]:
        """Receive exact number of bytes"""
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _disconnect_device(self, device_id: str) -> None:
        """Disconnect and clean up device"""
        if device_id not in self.connected_devices:
            return
        
        try:
            device = self.connected_devices[device_id]
            device.socket.close()
            
            del self.connected_devices[device_id]
            if device_id in self.client_threads:
                del self.client_threads[device_id]
            
            self.logger.info(f"Device disconnected: {device_id}")
            
            # Notify callbacks
            for callback in self.disconnect_callbacks:
                try:
                    callback(device_id)
                except Exception as e:
                    self.logger.error(f"Error in disconnect callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error disconnecting device {device_id}: {e}")
    
    def _heartbeat_monitor(self) -> None:
        """Monitor device heartbeats and disconnect stale connections"""
        while self.is_running:
            try:
                current_time = time.time()
                stale_devices = []
                
                for device_id, device in self.connected_devices.items():
                    if current_time - device.last_heartbeat > self.heartbeat_timeout:
                        stale_devices.append(device_id)
                
                for device_id in stale_devices:
                    self.logger.warning(f"Device {device_id} heartbeat timeout, disconnecting")
                    self._disconnect_device(device_id)
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat monitor: {e}")
                time.sleep(5.0)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    def on_message(device_id: str, message: JsonMessage):
        print(f"Message from {device_id}: {message.type}")
        if isinstance(message, SensorDataMessage):
            print(f"  Sensor data: {message.values}")
    
    def on_device_connected(device_id: str, device: ConnectedDevice):
        print(f"Device connected: {device_id} with capabilities: {device.capabilities}")
    
    def on_device_disconnected(device_id: str):
        print(f"Device disconnected: {device_id}")
    
    # Create and start server
    server = PCServer(port=9000)
    server.add_message_callback(on_message)
    server.add_device_callback(on_device_connected)
    server.add_disconnect_callback(on_device_disconnected)
    
    try:
        if server.start():
            print("Server started successfully. Press Ctrl+C to stop.")
            
            # Keep server running
            while True:
                time.sleep(1)
                
                # Example: send commands to devices
                devices = server.get_connected_devices()
                if devices:
                    # Send sync flash to all devices
                    sync_cmd = FlashSyncCommand(duration_ms=200, sync_id="test_sync")
                    server.broadcast_message(sync_cmd)
                    time.sleep(10)
    
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop()