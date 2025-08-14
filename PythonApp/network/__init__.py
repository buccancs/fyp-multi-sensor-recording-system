"""
Network Communication Module
============================

Simple JSON socket server for communicating with Android devices.
Handles device connections, command distribution, and status updates.
Includes security features and enhanced message handling.
"""

import json
import logging
import socket
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AndroidDevice:
    """Represents a connected Android device."""
    
    def __init__(self, device_id: str, socket_conn: socket.socket, address: tuple):
        self.device_id = device_id
        self.socket = socket_conn
        self.address = address
        self.connected_time = datetime.now()
        self.last_heartbeat = datetime.now()
        self.is_recording = False
        self.device_info = {}
        self.authenticated = False
        self.permissions: List[str] = []
        
    def send_message(self, message: dict) -> bool:
        """Send JSON message to device."""
        try:
            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {self.device_id}: {e}")
            return False
    
    def is_alive(self) -> bool:
        """Check if device connection is still alive."""
        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        return time_since_heartbeat < 30  # 30 second timeout


class JsonSocketServer:
    """Enhanced JSON socket server for Android device communication."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.devices: Dict[str, AndroidDevice] = {}
        self.message_handlers = {}
        self.server_thread = None
        
        # Security and synchronization components
        self.security_manager = None
        self.session_synchronizer = None
        self.transfer_manager = None
        
        # Register default message handlers
        self._register_handlers()
    
    def set_security_manager(self, security_manager):
        """Set the security manager for authentication."""
        self.security_manager = security_manager
    
    def set_session_synchronizer(self, synchronizer):
        """Set the session synchronizer for device coordination."""
        self.session_synchronizer = synchronizer
    
    def set_transfer_manager(self, transfer_manager):
        """Set the transfer manager for file operations."""
        self.transfer_manager = transfer_manager
    
    def _register_handlers(self):
        """Register default message handlers."""
        self.message_handlers = {
            'device_info': self._handle_device_info,
            'authentication': self._handle_authentication,
            'heartbeat': self._handle_heartbeat,
            'recording_status': self._handle_recording_status,
            'file_list_response': self._handle_file_list_response,
            'file_chunk': self._handle_file_chunk,
            'file_complete': self._handle_file_complete,
            'sync_response': self._handle_sync_response,
            'error': self._handle_error
        }
    
    def start_server(self) -> bool:
        """Start the socket server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            logger.info(f"Socket server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the socket server."""
        self.running = False
        
        # Close all device connections
        for device in list(self.devices.values()):
            self._disconnect_device(device.device_id)
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Socket server stopped")
    
    def _server_loop(self):
        """Main server loop to accept connections."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connection."""
        device_id = None
        buffer = ""
        
        try:
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages (newline-delimited JSON)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line.strip())
                            device_id = self._process_message(message, client_socket, address)
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON from {address}: {e}")
        
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        
        finally:
            if device_id:
                self._disconnect_device(device_id)
            try:
                client_socket.close()
            except:
                pass
    
    def _process_message(self, message: dict, client_socket: socket.socket, address: tuple) -> Optional[str]:
        """Process incoming message from device."""
        message_type = message.get('type')
        device_id = message.get('device_id')
        
        # Handle device registration
        if message_type == 'device_info' and device_id:
            if device_id not in self.devices:
                device = AndroidDevice(device_id, client_socket, address)
                self.devices[device_id] = device
                logger.info(f"Device registered: {device_id} from {address}")
        
        # Update device info if already connected
        if device_id in self.devices:
            device = self.devices[device_id]
            device.last_heartbeat = datetime.now()
            
            # Handle message
            handler = self.message_handlers.get(message_type)
            if handler:
                handler(device, message)
            else:
                logger.warning(f"No handler for message type: {message_type}")
        
        return device_id
    
    def _handle_device_info(self, device: AndroidDevice, message: dict):
        """Handle device info message."""
        device.device_info = message.get('data', {})
        logger.info(f"Device info updated for {device.device_id}: {device.device_info}")
    
    def _handle_authentication(self, device: AndroidDevice, message: dict):
        """Handle authentication message."""
        if not self.security_manager:
            # No security manager - allow all connections
            device.authenticated = True
            device.permissions = ["record", "transfer", "sync"]
            self._send_auth_response(device, True, "Authentication disabled")
            return
        
        auth_data = message.get('data', {})
        token = auth_data.get('token')
        
        if not token:
            self._send_auth_response(device, False, "No authentication token provided")
            return
        
        # Validate token
        if self.security_manager.authenticate_device(device.device_id, token):
            device.authenticated = True
            device.permissions = auth_data.get('requested_permissions', ["record"])
            self._send_auth_response(device, True, "Authentication successful")
            logger.info(f"Device {device.device_id} authenticated successfully")
        else:
            self._send_auth_response(device, False, "Invalid authentication token")
            logger.warning(f"Authentication failed for device {device.device_id}")
    
    def _send_auth_response(self, device: AndroidDevice, success: bool, message: str):
        """Send authentication response to device."""
        response = {
            'type': 'auth_response',
            'success': success,
            'message': message,
            'permissions': device.permissions if success else []
        }
        device.send_message(response)
    
    def _handle_heartbeat(self, device: AndroidDevice, message: dict):
        """Handle heartbeat message."""
        # Update session synchronizer if available
        if self.session_synchronizer:
            self.session_synchronizer.update_device_heartbeat(device.device_id)
    
    def _handle_recording_status(self, device: AndroidDevice, message: dict):
        """Handle recording status update."""
        status_data = message.get('data', {})
        device.is_recording = status_data.get('is_recording', False)
        logger.info(f"Recording status for {device.device_id}: {device.is_recording}")
    
    def _handle_file_list_response(self, device: AndroidDevice, message: dict):
        """Handle file list response from device."""
        if not self.transfer_manager:
            logger.warning("No transfer manager available for file list response")
            return
        
        data = message.get('data', {})
        session_id = data.get('session_id')
        file_list = data.get('files', [])
        
        if session_id and file_list:
            self.transfer_manager.handle_file_list_response(device.device_id, session_id, file_list)
    
    def _handle_file_chunk(self, device: AndroidDevice, message: dict):
        """Handle file chunk from device."""
        if not self.transfer_manager:
            logger.warning("No transfer manager available for file chunk")
            return
        
        data = message.get('data', {})
        file_id = data.get('file_id')
        chunk_data = data.get('chunk_data')
        chunk_index = data.get('chunk_index', 0)
        
        if file_id and chunk_data is not None:
            self.transfer_manager.handle_file_chunk(file_id, chunk_data, chunk_index)
    
    def _handle_file_complete(self, device: AndroidDevice, message: dict):
        """Handle file transfer completion from device."""
        if not self.transfer_manager:
            logger.warning("No transfer manager available for file completion")
            return
        
        data = message.get('data', {})
        file_id = data.get('file_id')
        
        if file_id:
            self.transfer_manager.handle_file_complete(file_id)
    
    def _handle_sync_response(self, device: AndroidDevice, message: dict):
        """Handle synchronization response from device."""
        data = message.get('data', {})
        sync_type = data.get('sync_type')
        sync_id = data.get('sync_id')
        
        logger.debug(f"Sync response from {device.device_id}: {sync_type} #{sync_id}")
    
    def _handle_error(self, device: AndroidDevice, message: dict):
        """Handle error message from device."""
        error_data = message.get('data', {})
        logger.error(f"Error from {device.device_id}: {error_data}")
    
    def _disconnect_device(self, device_id: str):
        """Disconnect and remove device."""
        if device_id in self.devices:
            device = self.devices[device_id]
            try:
                device.socket.close()
            except:
                pass
            del self.devices[device_id]
            logger.info(f"Device disconnected: {device_id}")
    
    def broadcast_command(self, command: str, data: dict = None) -> List[str]:
        """Broadcast command to all connected devices."""
        message = {
            'type': 'command',
            'command': command,
            'data': data or {},
            'timestamp': time.time()
        }
        
        successful_devices = []
        failed_devices = []
        
        for device_id, device in list(self.devices.items()):
            if device.send_message(message):
                successful_devices.append(device_id)
            else:
                failed_devices.append(device_id)
                self._disconnect_device(device_id)
        
        if failed_devices:
            logger.warning(f"Failed to send command to devices: {failed_devices}")
        
        return successful_devices
    
    def send_command_to_device(self, device_id: str, command: str, data: dict = None) -> bool:
        """Send command to specific device."""
        if device_id not in self.devices:
            logger.error(f"Device not connected: {device_id}")
            return False
        
        message = {
            'type': 'command',
            'command': command,
            'data': data or {},
            'timestamp': time.time()
        }
        
        device = self.devices[device_id]
        success = device.send_message(message)
        
        if not success:
            self._disconnect_device(device_id)
        
        return success
    
    def get_connected_devices(self) -> Dict[str, dict]:
        """Get information about connected devices."""
        device_info = {}
        
        for device_id, device in self.devices.items():
            device_info[device_id] = {
                'device_id': device_id,
                'address': device.address,
                'connected_time': device.connected_time.isoformat(),
                'last_heartbeat': device.last_heartbeat.isoformat(),
                'is_recording': device.is_recording,
                'is_alive': device.is_alive(),
                'authenticated': device.authenticated,
                'permissions': device.permissions,
                'device_info': device.device_info
            }
        
        return device_info
    
    def add_test_device(self, device_id: str = "test_device") -> bool:
        """Add a test device for validation purposes."""
        try:
            from datetime import datetime
            
            # Create a mock device object
            class MockDevice:
                def __init__(self, device_id: str):
                    self.device_id = device_id
                    self.address = "127.0.0.1:test"
                    self.connected_time = datetime.now()
                    self.last_heartbeat = datetime.now()
                    self.is_recording = False
                    self.authenticated = True
                    self.permissions = ["recording", "file_transfer"]  # Add permissions
                    self.device_info = {  # Add device info
                        "device_id": device_id,
                        "device_type": "android",
                        "model": "test_device",
                        "os_version": "test"
                    }
                
                def is_alive(self):
                    return True
                
                def send_message(self, message: dict) -> bool:
                    """Mock send message method."""
                    # Simulate successful message sending
                    return True
            
            self.devices[device_id] = MockDevice(device_id)
            logger.info(f"Added test device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add test device: {e}")
            return False
    
    def cleanup_dead_connections(self):
        """Remove devices that haven't sent heartbeat recently."""
        dead_devices = [
            device_id for device_id, device in self.devices.items()
            if not device.is_alive()
        ]
        
        for device_id in dead_devices:
            logger.warning(f"Removing dead connection: {device_id}")
            self._disconnect_device(device_id)