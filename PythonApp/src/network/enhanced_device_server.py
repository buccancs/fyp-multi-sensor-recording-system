"""
Enhanced Device Server for Rock-Solid Networking

This module implements a robust, thread-safe device server with advanced features for
reliable communication between PC and Android devices:

- Thread-safe message queuing with priority handling
- Heartbeat mechanism for connection monitoring
- Adaptive quality streaming for real-time preview
- Enhanced error recovery and reconnection logic
- Flow control and buffer management
- Comprehensive monitoring and diagnostics

Author: Multi-Sensor Recording System Team
Date: 2025-01-15
"""

import base64
import json
import queue
import socket
import struct
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, auto
import weakref

from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QMutex, QMutexLocker

# Import centralized logging
from utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)


class MessagePriority(Enum):
    """Message priority levels for queue management."""
    CRITICAL = 1    # Commands, ACKs
    HIGH = 2        # Status updates, errors
    NORMAL = 3      # Sensor data
    LOW = 4         # Preview frames, non-critical data


class ConnectionState(Enum):
    """Connection state enumeration."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    RECONNECTING = auto()
    ERROR = auto()


@dataclass
class NetworkMessage:
    """Enhanced message structure with metadata."""
    type: str
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    requires_ack: bool = False
    message_id: Optional[str] = None


@dataclass
class ConnectionStats:
    """Connection statistics for monitoring."""
    connected_at: float = field(default_factory=time.time)
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    reconnection_count: int = 0
    error_count: int = 0
    average_latency: float = 0.0
    latency_samples: deque = field(default_factory=lambda: deque(maxlen=100))
    min_latency: float = float('inf')
    max_latency: float = 0.0
    jitter: float = 0.0
    packet_loss_rate: float = 0.0
    ping_count: int = 0
    pong_count: int = 0


class EnhancedRemoteDevice:
    """
    Enhanced remote device representation with advanced connection management.
    """

    def __init__(self, device_id: str, capabilities: List[str], 
                 client_socket: socket.socket, address: Tuple[str, int]):
        """Initialize enhanced remote device."""
        self.device_id = device_id
        self.capabilities = capabilities
        self.client_socket = client_socket
        self.address = address
        self.state = ConnectionState.CONNECTED
        
        # Thread safety
        self.mutex = QMutex()
        
        # Message queuing
        self.outbound_queue = queue.PriorityQueue()
        self.pending_acks = {}  # message_id -> (timestamp, callback)
        
        # Statistics and monitoring
        self.stats = ConnectionStats()
        
        # Heartbeat management
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 5.0  # seconds
        self.heartbeat_timeout = 15.0  # seconds
        
        # Streaming configuration
        self.streaming_quality = 'medium'  # low, medium, high
        self.max_frame_rate = 15  # fps for preview streaming
        self.last_frame_time = 0.0
        
        # Buffer management
        self.send_buffer_size = 64 * 1024  # 64KB
        self.recv_buffer_size = 64 * 1024  # 64KB
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        logger.info(f"Enhanced RemoteDevice created: {device_id} @ {address[0]}:{address[1]}")

    def is_alive(self) -> bool:
        """Check if device is considered alive based on heartbeat."""
        with QMutexLocker(self.mutex):
            return (time.time() - self.last_heartbeat) < self.heartbeat_timeout

    def should_send_frame(self) -> bool:
        """Check if I should send a preview frame based on rate limiting."""
        current_time = time.time()
        frame_interval = 1.0 / self.max_frame_rate
        
        if current_time - self.last_frame_time >= frame_interval:
            self.last_frame_time = current_time
            return True
        return False

    def adapt_streaming_quality(self, network_latency: float, error_rate: float):
        """Adapt streaming quality based on network conditions."""
        with QMutexLocker(self.mutex):
            if error_rate > 0.1 or network_latency > 200:  # 200ms
                self.streaming_quality = 'low'
                self.max_frame_rate = 5
            elif error_rate < 0.05 and network_latency < 50:  # 50ms
                self.streaming_quality = 'high'
                self.max_frame_rate = 30
            else:
                self.streaming_quality = 'medium'
                self.max_frame_rate = 15

    def queue_message(self, message: NetworkMessage):
        """Queue message for sending with priority handling."""
        priority_value = message.priority.value
        self.outbound_queue.put((priority_value, time.time(), message))

    def get_next_message(self, timeout: float = 0.1) -> Optional[NetworkMessage]:
        """Get next message from queue."""
        try:
            _, _, message = self.outbound_queue.get(timeout=timeout)
            return message
        except queue.Empty:
            return None

    def update_latency(self, latency: float):
        """Update latency statistics with advanced metrics."""
        with QMutexLocker(self.mutex):
            self.stats.latency_samples.append(latency)
            
            # Update min/max latency
            self.stats.min_latency = min(self.stats.min_latency, latency)
            self.stats.max_latency = max(self.stats.max_latency, latency)
            
            # Calculate average latency
            if self.stats.latency_samples:
                self.stats.average_latency = sum(self.stats.latency_samples) / len(self.stats.latency_samples)
                
                # Calculate jitter (standard deviation of latency)
                if len(self.stats.latency_samples) >= 2:
                    variance = sum((x - self.stats.average_latency) ** 2 for x in self.stats.latency_samples) / len(self.stats.latency_samples)
                    self.stats.jitter = variance ** 0.5
                
                # Update packet loss rate based on ping/pong ratio
                if self.stats.ping_count > 0:
                    self.stats.packet_loss_rate = max(0, (self.stats.ping_count - self.stats.pong_count) / self.stats.ping_count * 100)
    
    def update_ping_stats(self, is_response: bool = False):
        """Update ping/pong statistics."""
        with QMutexLocker(self.mutex):
            if is_response:
                self.stats.pong_count += 1
            else:
                self.stats.ping_count += 1

    def increment_error_count(self):
        """Increment error counters."""
        with QMutexLocker(self.mutex):
            self.stats.error_count += 1
            self.consecutive_errors += 1

    def reset_error_count(self):
        """Reset consecutive error count."""
        with QMutexLocker(self.mutex):
            self.consecutive_errors = 0

    def should_reconnect(self) -> bool:
        """Check if device should be disconnected due to errors."""
        with QMutexLocker(self.mutex):
            return self.consecutive_errors >= self.max_consecutive_errors

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive device status."""
        with QMutexLocker(self.mutex):
            return {
                "device_id": self.device_id,
                "state": self.state.name,
                "capabilities": self.capabilities,
                "address": f"{self.address[0]}:{self.address[1]}",
                "is_alive": self.is_alive(),
                "streaming_quality": self.streaming_quality,
                "stats": {
                    "messages_sent": self.stats.messages_sent,
                    "messages_received": self.stats.messages_received,
                    "bytes_sent": self.stats.bytes_sent,
                    "bytes_received": self.stats.bytes_received,
                    "error_count": self.stats.error_count,
                    "average_latency": round(self.stats.average_latency, 2),
                    "min_latency": round(self.stats.min_latency, 2) if self.stats.min_latency != float('inf') else 0,
                    "max_latency": round(self.stats.max_latency, 2),
                    "jitter": round(self.stats.jitter, 2),
                    "packet_loss_rate": round(self.stats.packet_loss_rate, 2),
                    "ping_count": self.stats.ping_count,
                    "pong_count": self.stats.pong_count,
                    "connection_duration": round(time.time() - self.stats.connected_at, 1),
                    "latency_samples": len(self.stats.latency_samples)
                }
            }


class EnhancedDeviceServer(QThread):
    """
    Enhanced Device Server with rock-solid networking features.
    
    Features:
    - Thread-safe message queuing with priorities
    - Heartbeat mechanism for connection monitoring
    - Adaptive quality streaming
    - Enhanced error recovery
    - Flow control and buffer management
    - Comprehensive monitoring
    """

    # Enhanced signals for comprehensive event handling
    device_connected = pyqtSignal(str, dict)  # device_id, device_info
    device_disconnected = pyqtSignal(str, str)  # device_id, reason
    device_status_changed = pyqtSignal(str, str)  # device_id, new_status
    
    # Message signals
    message_received = pyqtSignal(str, dict)  # device_id, message
    message_sent = pyqtSignal(str, dict)  # device_id, message
    message_failed = pyqtSignal(str, dict, str)  # device_id, message, error
    
    # Preview streaming
    preview_frame_received = pyqtSignal(str, str, bytes, dict)  # device_id, frame_type, data, metadata
    streaming_quality_changed = pyqtSignal(str, str)  # device_id, new_quality
    
    # Network monitoring
    network_stats_updated = pyqtSignal(dict)  # overall network statistics
    connection_quality_changed = pyqtSignal(str, float)  # device_id, quality_score
    
    # Error handling
    error_occurred = pyqtSignal(str, str, str)  # device_id, error_type, error_message
    warning_occurred = pyqtSignal(str, str)  # device_id, warning_message

    def __init__(self, host: str = "0.0.0.0", port: int = 9000, 
                 max_connections: int = 10, heartbeat_interval: float = 5.0):
        """Initialize enhanced device server."""
        super().__init__()
        
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.heartbeat_interval = heartbeat_interval
        
        # Server state
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        
        # Thread-safe device management
        self.devices: Dict[str, EnhancedRemoteDevice] = {}
        self.devices_mutex = QMutex()
        
        # Connection management
        self.client_handlers: Dict[str, threading.Thread] = {}
        self.connection_pool = []
        
        # Heartbeat system
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeats)
        
        # Message tracking
        self.message_counter = 0
        self.pending_messages: Dict[str, NetworkMessage] = {}
        
        # Network monitoring
        self.network_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_messages": 0,
            "total_bytes": 0,
            "error_rate": 0.0,
            "average_latency": 0.0
        }
        
        # Performance optimization
        self.enable_compression = True
        self.compression_threshold = 1024  # bytes
        
        logger.info(f"Enhanced Device Server initialized: {host}:{port}")

    def start_server(self):
        """Start the enhanced server."""
        if self.running:
            logger.warning("Server is already running")
            return False

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Set socket buffers
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64 * 1024)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64 * 1024)
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            
            self.running = True
            self.start()  # Start QThread
            
            # Start heartbeat timer
            self.heartbeat_timer.start(int(self.heartbeat_interval * 1000))
            
            logger.info(f"Enhanced Device Server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.error_occurred.emit("server", "startup", str(e))
            return False

    def stop_server(self):
        """Stop the server gracefully."""
        logger.info("Stopping Enhanced Device Server...")
        
        self.running = False
        self.heartbeat_timer.stop()
        
        # Disconnect all devices
        with QMutexLocker(self.devices_mutex):
            for device_id in list(self.devices.keys()):
                self.disconnect_device(device_id, "Server shutdown")
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Wait for thread to finish
        if self.isRunning():
            self.wait(5000)  # 5 second timeout
        
        logger.info("Enhanced Device Server stopped")

    def run(self):
        """Main server thread - accept connections."""
        while self.running and self.server_socket:
            try:
                client_socket, address = self.server_socket.accept()
                
                if len(self.devices) >= self.max_connections:
                    logger.warning(f"Maximum connections reached, rejecting {address}")
                    client_socket.close()
                    continue
                
                # Configure client socket
                client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                client_socket.settimeout(30.0)  # 30 second timeout
                
                # Create handler thread
                handler_thread = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_socket, address),
                    daemon=True
                )
                handler_thread.start()
                
                logger.info(f"New client connection from {address[0]}:{address[1]}")
                
            except socket.error as e:
                if self.running:
                    logger.error(f"Accept error: {e}")
                    self.error_occurred.emit("server", "accept", str(e))
            except Exception as e:
                if self.running:
                    logger.error(f"Unexpected server error: {e}")
                    self.error_occurred.emit("server", "unexpected", str(e))

    def handle_client_connection(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle individual client connection with enhanced features."""
        client_addr = f"{address[0]}:{address[1]}"
        device_id = None
        device = None
        
        try:
            # Wait for handshake message
            handshake_msg = self.receive_message(client_socket, timeout=10.0)
            if not handshake_msg or handshake_msg.get('type') != 'handshake':
                logger.warning(f"Invalid handshake from {client_addr}")
                return
            
            device_id = handshake_msg.get('device_id')
            capabilities = handshake_msg.get('capabilities', [])
            
            if not device_id:
                logger.warning(f"Missing device_id in handshake from {client_addr}")
                return
            
            # Create enhanced device
            device = EnhancedRemoteDevice(device_id, capabilities, client_socket, address)
            
            # Register device
            with QMutexLocker(self.devices_mutex):
                self.devices[device_id] = device
                self.client_handlers[device_id] = threading.current_thread()
            
            # Send handshake acknowledgment
            ack_msg = {
                'type': 'handshake_ack',
                'protocol_version': 1,
                'server_name': 'Enhanced Device Server',
                'server_version': '1.0.0',
                'compatible': True,
                'timestamp': time.time()
            }
            self.send_message(device, ack_msg, MessagePriority.CRITICAL)
            
            # Emit connection signal
            self.device_connected.emit(device_id, device.get_status_summary())
            
            # Start message sender thread
            sender_thread = threading.Thread(
                target=self.message_sender_loop,
                args=(device,),
                daemon=True
            )
            sender_thread.start()
            
            # Main message receiving loop
            self.message_receiver_loop(device)
            
        except Exception as e:
            logger.error(f"Client handler error for {client_addr}: {e}")
            self.error_occurred.emit(device_id or client_addr, "handler", str(e))
        finally:
            # Cleanup
            if device_id and device:
                self.disconnect_device(device_id, "Connection closed")

    def message_receiver_loop(self, device: EnhancedRemoteDevice):
        """Main message receiving loop for a device."""
        while self.running and device.state == ConnectionState.CONNECTED:
            try:
                message = self.receive_message(device.client_socket, timeout=1.0)
                if not message:
                    continue
                
                # Update device statistics
                device.stats.messages_received += 1
                device.last_heartbeat = time.time()
                device.reset_error_count()
                
                # Process message
                self.process_message(device, message)
                
            except socket.timeout:
                # Check if device is still alive
                if not device.is_alive():
                    logger.warning(f"Device {device.device_id} heartbeat timeout")
                    break
            except Exception as e:
                logger.error(f"Receive error for {device.device_id}: {e}")
                device.increment_error_count()
                if device.should_reconnect():
                    break

    def message_sender_loop(self, device: EnhancedRemoteDevice):
        """Message sending loop for a device."""
        while self.running and device.state == ConnectionState.CONNECTED:
            try:
                message = device.get_next_message(timeout=0.5)
                if not message:
                    continue
                
                # Send message
                success = self.send_message_immediate(device, message)
                if success:
                    device.stats.messages_sent += 1
                    device.reset_error_count()
                    self.message_sent.emit(device.device_id, message.payload)
                else:
                    device.increment_error_count()
                    self.message_failed.emit(device.device_id, message.payload, "Send failed")
                    
                    if device.should_reconnect():
                        break
                        
            except Exception as e:
                logger.error(f"Send error for {device.device_id}: {e}")
                device.increment_error_count()

    def send_message_immediate(self, device: EnhancedRemoteDevice, message: NetworkMessage) -> bool:
        """Send message immediately to device."""
        try:
            # Serialize message
            json_data = json.dumps(message.payload).encode('utf-8')
            
            # Apply compression if needed
            if self.enable_compression and len(json_data) > self.compression_threshold:
                # Note: Compression implementation would go here
                pass
            
            # Send with length prefix
            length_header = struct.pack('>I', len(json_data))
            device.client_socket.sendall(length_header + json_data)
            
            device.stats.bytes_sent += len(length_header) + len(json_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {device.device_id}: {e}")
            return False

    def receive_message(self, sock: socket.socket, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Receive message with timeout."""
        sock.settimeout(timeout)
        try:
            # Read length header
            length_data = self.recv_exact(sock, 4)
            if not length_data:
                return None
            
            message_length = struct.unpack('>I', length_data)[0]
            if message_length <= 0 or message_length > 10 * 1024 * 1024:  # 10MB max
                raise ValueError(f"Invalid message length: {message_length}")
            
            # Read message
            json_data = self.recv_exact(sock, message_length)
            if not json_data:
                return None
            
            return json.loads(json_data.decode('utf-8'))
            
        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"Receive message error: {e}")
            return None

    def recv_exact(self, sock: socket.socket, length: int) -> Optional[bytes]:
        """Receive exactly 'length' bytes."""
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def process_message(self, device: EnhancedRemoteDevice, message: Dict[str, Any]):
        """Process received message with enhanced handling."""
        msg_type = message.get('type', 'unknown')
        
        # Update latency if message has timestamp
        if 'timestamp' in message:
            latency = (time.time() - message['timestamp']) * 1000  # ms
            device.update_latency(latency)
        
        # Handle different message types
        if msg_type == 'heartbeat':
            self.handle_heartbeat(device, message)
        elif msg_type == 'status':
            self.handle_status_update(device, message)
        elif msg_type == 'preview_frame':
            self.handle_preview_frame(device, message)
        elif msg_type == 'ack':
            self.handle_acknowledgment(device, message)
        elif msg_type == 'sensor_data':
            self.handle_sensor_data(device, message)
        else:
            # Generic message handling
            self.message_received.emit(device.device_id, message)

    def handle_preview_frame(self, device: EnhancedRemoteDevice, message: Dict[str, Any]):
        """Handle preview frame with adaptive quality."""
        if not device.should_send_frame():
            return  # Rate limiting
        
        frame_type = message.get('frame_type', 'rgb')
        image_data = message.get('image_data', '')
        width = message.get('width', 0)
        height = message.get('height', 0)
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
            metadata = {
                'width': width,
                'height': height,
                'frame_type': frame_type,
                'quality': device.streaming_quality,
                'timestamp': message.get('timestamp', time.time())
            }
            
            self.preview_frame_received.emit(device.device_id, frame_type, image_bytes, metadata)
            
            # Adapt quality based on network conditions
            error_rate = device.stats.error_count / max(1, device.stats.messages_received)
            device.adapt_streaming_quality(device.stats.average_latency, error_rate)
            
        except Exception as e:
            logger.error(f"Preview frame processing error: {e}")

    def handle_heartbeat(self, device: EnhancedRemoteDevice, message: Dict[str, Any]):
        """Handle heartbeat message."""
        # Send heartbeat response
        response = NetworkMessage(
            type='heartbeat_response',
            payload={
                'type': 'heartbeat_response',
                'timestamp': time.time(),
                'server_time': time.time()
            },
            priority=MessagePriority.HIGH
        )
        device.queue_message(response)

    def send_heartbeats(self):
        """Send heartbeat to all connected devices."""
        with QMutexLocker(self.devices_mutex):
            current_time = time.time()
            for device in list(self.devices.values()):
                if device.is_alive():
                    heartbeat = NetworkMessage(
                        type='heartbeat',
                        payload={
                            'type': 'heartbeat',
                            'timestamp': current_time
                        },
                        priority=MessagePriority.HIGH
                    )
                    device.queue_message(heartbeat)
                else:
                    # Device is not responding, disconnect
                    self.disconnect_device(device.device_id, "Heartbeat timeout")

    def send_command_to_device(self, device_id: str, command: str, **kwargs) -> bool:
        """Send command to specific device."""
        with QMutexLocker(self.devices_mutex):
            device = self.devices.get(device_id)
            if not device:
                logger.warning(f"Device {device_id} not found")
                return False
        
        message = NetworkMessage(
            type='command',
            payload={
                'type': 'command',
                'command': command,
                'timestamp': time.time(),
                **kwargs
            },
            priority=MessagePriority.CRITICAL,
            requires_ack=True
        )
        
        device.queue_message(message)
        return True

    def broadcast_command(self, command: str, **kwargs) -> int:
        """Broadcast command to all connected devices."""
        count = 0
        with QMutexLocker(self.devices_mutex):
            for device_id in self.devices:
                if self.send_command_to_device(device_id, command, **kwargs):
                    count += 1
        return count

    def disconnect_device(self, device_id: str, reason: str = "Unknown"):
        """Disconnect device gracefully."""
        with QMutexLocker(self.devices_mutex):
            device = self.devices.get(device_id)
            if not device:
                return
            
            try:
                device.client_socket.close()
            except:
                pass
            
            device.state = ConnectionState.DISCONNECTED
            del self.devices[device_id]
            
            if device_id in self.client_handlers:
                del self.client_handlers[device_id]
        
        self.device_disconnected.emit(device_id, reason)
        logger.info(f"Device {device_id} disconnected: {reason}")

    def get_network_statistics(self) -> Dict[str, Any]:
        """Get comprehensive network statistics."""
        with QMutexLocker(self.devices_mutex):
            stats = {
                "active_devices": len(self.devices),
                "total_connections": self.network_stats["total_connections"],
                "overall_stats": {
                    "total_messages": sum(device.stats.messages_sent + device.stats.messages_received for device in self.devices.values()),
                    "total_bytes": sum(device.stats.bytes_sent + device.stats.bytes_received for device in self.devices.values()),
                    "average_latency": self._calculate_overall_latency(),
                    "network_quality": self._assess_overall_network_quality()
                },
                "devices": {}
            }
            
            for device_id, device in self.devices.items():
                stats["devices"][device_id] = device.get_status_summary()
        
        return stats
    
    def _calculate_overall_latency(self) -> float:
        """Calculate overall average latency across all devices."""
        if not self.devices:
            return 0.0
        
        total_latency = 0.0
        device_count = 0
        
        for device in self.devices.values():
            if device.stats.latency_samples:
                total_latency += device.stats.average_latency
                device_count += 1
        
        return total_latency / device_count if device_count > 0 else 0.0
    
    def _assess_overall_network_quality(self) -> str:
        """Assess overall network quality."""
        if not self.devices:
            return "unknown"
        
        avg_latency = self._calculate_overall_latency()
        
        if avg_latency < 50:
            return "excellent"
        elif avg_latency < 100:
            return "good"
        elif avg_latency < 200:
            return "fair"
        else:
            return "poor"
    
    def get_device_latency_statistics(self, device_id: str) -> Dict[str, Any]:
        """Get detailed latency statistics for a specific device."""
        with QMutexLocker(self.devices_mutex):
            device = self.devices.get(device_id)
            if not device:
                return {"error": f"Device {device_id} not found"}
            
            with QMutexLocker(device.mutex):
                return {
                    "device_id": device_id,
                    "average_latency": device.stats.average_latency,
                    "min_latency": device.stats.min_latency if device.stats.min_latency != float('inf') else 0,
                    "max_latency": device.stats.max_latency,
                    "jitter": device.stats.jitter,
                    "packet_loss_rate": device.stats.packet_loss_rate,
                    "ping_count": device.stats.ping_count,
                    "pong_count": device.stats.pong_count,
                    "sample_count": len(device.stats.latency_samples),
                    "recent_samples": list(device.stats.latency_samples)[-10:] if device.stats.latency_samples else []
                }

    def handle_status_update(self, device: EnhancedRemoteDevice, message: Dict[str, Any]):
        """Handle device status update."""
        # Check if this is a ping message embedded in storage field
        storage = message.get('storage', '')
        if isinstance(storage, str) and storage.startswith('ping:'):
            self.handle_ping_message(device, storage, message.get('timestamp', time.time()))
        else:
            # Process regular status data
            status_data = {k: v for k, v in message.items() if k != 'type'}
            self.message_received.emit(device.device_id, message)
    
    def handle_ping_message(self, device: EnhancedRemoteDevice, ping_data: str, original_timestamp: float):
        """Handle ping message and send pong response."""
        try:
            # Parse ping data: "ping:pingId:timestamp:sequence"
            parts = ping_data.split(':')
            if len(parts) >= 4:
                ping_id = parts[1]
                ping_timestamp = float(parts[2])
                sequence = int(parts[3])
                
                # Create pong response embedded in status message
                current_time = time.time()
                pong_data = f"pong:{ping_id}:{ping_timestamp}:{current_time}:{sequence}"
                
                response = NetworkMessage(
                    type='status',
                    payload={
                        'type': 'status',
                        'storage': pong_data,
                        'timestamp': current_time,
                        'battery': None,
                        'temperature': None,
                        'recording': False,
                        'connected': True
                    },
                    priority=MessagePriority.HIGH
                )
                device.queue_message(response)
                
                # Update device latency with ping timing
                ping_latency = (current_time - ping_timestamp) * 1000  # Convert to ms
                device.update_latency(ping_latency / 2)  # Half for one-way latency
                device.update_ping_stats(is_response=True)  # This is a pong response
                
                logger.debug(f"Responded to ping {ping_id} from {device.device_id}, RTT: {ping_latency:.2f}ms")
                
        except Exception as e:
            logger.error(f"Error handling ping message: {e}")

    def handle_acknowledgment(self, device: EnhancedRemoteDevice, message: Dict[str, Any]):
        """Handle message acknowledgment."""
        message_id = message.get('message_id')
        success = message.get('success', False)
        
        if message_id in self.pending_messages:
            del self.pending_messages[message_id]
        
        self.message_received.emit(device.device_id, message)

    def handle_sensor_data(self, device: EnhancedRemoteDevice, message: Dict[str, Any]):
        """Handle sensor data message."""
        self.message_received.emit(device.device_id, message)

    def send_message(self, device: EnhancedRemoteDevice, message_data: Dict[str, Any], 
                    priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Queue message for sending."""
        message = NetworkMessage(
            type=message_data.get('type', 'unknown'),
            payload=message_data,
            priority=priority
        )
        device.queue_message(message)
        return True


# Utility functions
def create_command_message(command: str, **kwargs) -> Dict[str, Any]:
    """Create command message with standard format."""
    return {
        'type': 'command',
        'command': command,
        'timestamp': time.time(),
        **kwargs
    }


def decode_base64_image(data: str) -> Optional[bytes]:
    """Decode base64 image data."""
    try:
        # Handle data URL format
        if data.startswith('data:'):
            data = data.split(',', 1)[1]
        
        return base64.b64decode(data)
    except Exception as e:
        logger.error(f"Base64 decode error: {e}")
        return None