"""
Network Communication Module
============================

Enhanced JSON socket server for communicating with Android devices.
Uses shared_protocols for standardized message format and communication.
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
import sys
from pathlib import Path

# Add shared_protocols to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from shared_protocols.network_protocol import (
    MessageType, BaseMessage, HelloMessage, DeviceStatusMessage,
    SessionControlMessage, DataMessage, CalibrationMessage,
    CommandMessage, ResponseMessage, ErrorMessage,
    create_message_from_json, create_error_response, create_success_response,
    STANDARD_COMMANDS, STANDARD_ERROR_CODES
)
from shared_protocols.data_structures import DeviceInfo, DeviceState, DeviceType

logger = logging.getLogger(__name__)


class AndroidDevice:
    """Represents a connected Android device using shared protocols."""
    
    def __init__(self, device_id: str, socket_conn: socket.socket, address: tuple):
        self.device_id = device_id
        self.socket = socket_conn
        self.address = address
        self.connected_time = datetime.now()
        self.last_heartbeat = datetime.now()
        self.is_recording = False
        self.device_info = DeviceInfo(
            device_id=device_id,
            device_type=DeviceType.ANDROID_PHONE,
            capabilities=[],
            firmware_version="unknown",
            connection_time=time.time()
        )
        self.device_state = DeviceState.CONNECTED
        self.authenticated = False
        self.permissions: List[str] = []
        self.protocol_version = "1.0"
        self.legacy_info = {}  # Store legacy device info
        
    def send_message(self, message: BaseMessage) -> bool:
        """Send message using shared protocol format."""
        try:
            message_str = message.to_json() + '\n'
            self.socket.send(message_str.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {self.device_id}: {e}")
            return False
    
    def send_dict_message(self, message: dict) -> bool:
        """Send legacy dictionary message (for backward compatibility)."""
        try:
            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Failed to send dict message to {self.device_id}: {e}")
            return False
    
    def is_alive(self) -> bool:
        """Check if device connection is still alive."""
        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        return time_since_heartbeat < 30  # 30 second timeout


class JsonSocketServer:
    """Enhanced JSON socket server using shared protocols for Android device communication."""
    
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
        
        # Register message handlers for shared protocols
        self._register_shared_protocol_handlers()
        # Register legacy handlers for backward compatibility
        self._register_legacy_handlers()
    
    def set_security_manager(self, security_manager):
        """Set the security manager for authentication."""
        self.security_manager = security_manager
    
    def set_session_synchronizer(self, synchronizer):
        """Set the session synchronizer for device coordination."""
        self.session_synchronizer = synchronizer
    
    def set_transfer_manager(self, transfer_manager):
        """Set the transfer manager for file operations."""
        self.transfer_manager = transfer_manager
    
    def _register_shared_protocol_handlers(self):
        """Register message handlers for shared protocol message types."""
        self.message_handlers.update({
            MessageType.HELLO: self._handle_hello_message,
            MessageType.HEARTBEAT: self._handle_heartbeat_message,
            MessageType.DEVICE_STATUS: self._handle_device_status_message,
            MessageType.SESSION_START: self._handle_session_control_message,
            MessageType.SESSION_STOP: self._handle_session_control_message,
            MessageType.SESSION_STATUS: self._handle_session_status_message,
            MessageType.DATA_SAMPLE: self._handle_data_message,
            MessageType.DATA_BATCH: self._handle_data_message,
            MessageType.CALIBRATION_START: self._handle_calibration_message,
            MessageType.CALIBRATION_CAPTURE: self._handle_calibration_message,
            MessageType.CALIBRATION_COMPLETE: self._handle_calibration_message,
            MessageType.COMMAND: self._handle_command_message,
            MessageType.RESPONSE: self._handle_response_message,
            MessageType.ERROR: self._handle_error_message,
            MessageType.GOODBYE: self._handle_goodbye_message
        })
    
    def _register_legacy_handlers(self):
        """Register legacy message handlers for backward compatibility."""
        self.message_handlers.update({
            'device_info': self._handle_legacy_device_info,
            'authentication': self._handle_legacy_authentication,
            'heartbeat': self._handle_legacy_heartbeat,
            'recording_status': self._handle_legacy_recording_status,
            'file_list_response': self._handle_legacy_file_list_response,
            'file_chunk': self._handle_legacy_file_chunk,
            'file_complete': self._handle_legacy_file_complete,
            'sync_response': self._handle_legacy_sync_response,
            'error': self._handle_legacy_error,
            'hello': self._handle_legacy_hello,
            'command': self._handle_legacy_command,
            'response': self._handle_legacy_response
        })
    
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
    
    def _process_message(self, message_data: dict, client_socket: socket.socket, address: tuple) -> Optional[str]:
        """Process incoming message from device."""
        device_id = None
        
        try:
            # Try to parse as shared protocol message first
            message_json = json.dumps(message_data)
            parsed_message = create_message_from_json(message_json)
            
            if isinstance(parsed_message, ErrorMessage):
                # Failed to parse as shared protocol, try legacy format
                return self._process_legacy_message(message_data, client_socket, address)
            
            # Extract device ID from the message
            device_id = parsed_message.device_id
            message_type = parsed_message.message_type
            
            # Handle device registration for HELLO messages
            if message_type == MessageType.HELLO and device_id:
                if device_id not in self.devices:
                    device = AndroidDevice(device_id, client_socket, address)
                    self.devices[device_id] = device
                    logger.info(f"Device registered via HELLO: {device_id} from {address}")
            
            # Update device info if already connected
            if device_id and device_id in self.devices:
                device = self.devices[device_id]
                device.last_heartbeat = datetime.now()
                
                # Handle message with shared protocol handler
                handler = self.message_handlers.get(message_type)
                if handler:
                    handler(device, parsed_message)
                else:
                    logger.warning(f"No handler for message type: {message_type}")
            else:
                logger.warning(f"Message from unregistered device: {device_id}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Fallback to legacy processing
            return self._process_legacy_message(message_data, client_socket, address)
        
        return device_id
    
    def _process_legacy_message(self, message: dict, client_socket: socket.socket, address: tuple) -> Optional[str]:
        """Process legacy message format for backward compatibility."""
        message_type = message.get('type')
        device_id = message.get('device_id')
        
        # Handle device registration
        if message_type == 'device_info' and device_id:
            if device_id not in self.devices:
                device = AndroidDevice(device_id, client_socket, address)
                self.devices[device_id] = device
                logger.info(f"Device registered via legacy: {device_id} from {address}")
        
        # Update device info if already connected
        if device_id in self.devices:
            device = self.devices[device_id]
            device.last_heartbeat = datetime.now()
            
            # Handle message with legacy handler
            handler = self.message_handlers.get(message_type)
            if handler:
                handler(device, message)
            else:
                logger.warning(f"No handler for legacy message type: {message_type}")
        
        return device_id
    
    # Shared Protocol Message Handlers
    
    def _handle_hello_message(self, device: AndroidDevice, message: HelloMessage):
        """Handle HELLO message using shared protocol."""
        device.device_info = message.device_info
        device.protocol_version = message.protocol_version
        logger.info(f"HELLO from {device.device_id}: {message.device_info.model} v{message.protocol_version}")
        
        # Send welcome response
        response = ResponseMessage(
            original_command="hello",
            success=True,
            result={"server_version": "1.0", "features": ["recording", "sync", "calibration"]},
            device_id=device.device_id
        )
        device.send_message(response)
    
    def _handle_heartbeat_message(self, device: AndroidDevice, message: BaseMessage):
        """Handle HEARTBEAT message using shared protocol."""
        device.last_heartbeat = datetime.now()
        if self.session_synchronizer:
            self.session_synchronizer.update_device_heartbeat(device.device_id)
        logger.debug(f"Heartbeat from {device.device_id}")
    
    def _handle_device_status_message(self, device: AndroidDevice, message: DeviceStatusMessage):
        """Handle DEVICE_STATUS message using shared protocol."""
        device.device_state = message.device_state
        if message.battery_level is not None:
            device.device_info.model = f"{device.device_info.model} (Battery: {message.battery_level}%)"
        logger.info(f"Device status for {device.device_id}: {message.device_state}")
    
    def _handle_session_control_message(self, device: AndroidDevice, message: SessionControlMessage):
        """Handle SESSION_START/STOP messages using shared protocol."""
        if message.message_type == MessageType.SESSION_START:
            device.is_recording = True
            logger.info(f"Session started on {device.device_id}")
        elif message.message_type == MessageType.SESSION_STOP:
            device.is_recording = False
            logger.info(f"Session stopped on {device.device_id}")
    
    def _handle_session_status_message(self, device: AndroidDevice, message: BaseMessage):
        """Handle SESSION_STATUS message using shared protocol."""
        logger.debug(f"Session status from {device.device_id}")
    
    def _handle_data_message(self, device: AndroidDevice, message: DataMessage):
        """Handle DATA_SAMPLE/DATA_BATCH messages using shared protocol."""
        sample_count = len(message.samples)
        logger.debug(f"Received {sample_count} data samples from {device.device_id}")
    
    def _handle_calibration_message(self, device: AndroidDevice, message: CalibrationMessage):
        """Handle calibration messages using shared protocol."""
        logger.info(f"Calibration {message.action} from {device.device_id}")
    
    def _handle_command_message(self, device: AndroidDevice, message: CommandMessage):
        """Handle COMMAND message using shared protocol."""
        command = message.command
        parameters = message.parameters or {}
        
        logger.info(f"Command '{command}' from {device.device_id}")
        
        # Process standard commands
        if command in STANDARD_COMMANDS.values():
            response = self._process_standard_command(device, command, parameters)
        else:
            response = create_error_response(
                command, 
                STANDARD_ERROR_CODES["INVALID_COMMAND"],
                f"Unknown command: {command}"
            )
        
        response.device_id = device.device_id
        device.send_message(response)
    
    def _handle_response_message(self, device: AndroidDevice, message: ResponseMessage):
        """Handle RESPONSE message using shared protocol."""
        logger.info(f"Response from {device.device_id}: {message.original_command} -> {message.success}")
    
    def _handle_error_message(self, device: AndroidDevice, message: ErrorMessage):
        """Handle ERROR message using shared protocol."""
        logger.error(f"Error from {device.device_id}: {message.error_code} - {message.error_message}")
    
    def _handle_goodbye_message(self, device: AndroidDevice, message: BaseMessage):
        """Handle GOODBYE message using shared protocol."""
        logger.info(f"Goodbye from {device.device_id}")
        self._disconnect_device(device.device_id)
    
    def _process_standard_command(self, device: AndroidDevice, command: str, parameters: dict) -> ResponseMessage:
        """Process standard commands and return response."""
        try:
            if command == STANDARD_COMMANDS["PING"]:
                return create_success_response(command, {"pong": True, "timestamp": time.time()})
            
            elif command == STANDARD_COMMANDS["GET_STATUS"]:
                return create_success_response(command, {
                    "device_state": device.device_state.value,
                    "is_recording": device.is_recording,
                    "authenticated": device.authenticated,
                    "last_heartbeat": device.last_heartbeat.isoformat()
                })
            
            elif command == STANDARD_COMMANDS["START_STREAMING"]:
                device.is_recording = True
                return create_success_response(command, {"streaming": True})
            
            elif command == STANDARD_COMMANDS["STOP_STREAMING"]:
                device.is_recording = False
                return create_success_response(command, {"streaming": False})
            
            elif command == STANDARD_COMMANDS["SYNC_TIME"]:
                if self.session_synchronizer:
                    sync_time = self.session_synchronizer.get_current_time()
                    return create_success_response(command, {"sync_time": sync_time})
                else:
                    return create_error_response(command, "E002", "No synchronizer available")
            
            else:
                return create_error_response(
                    command,
                    STANDARD_ERROR_CODES["INVALID_COMMAND"],
                    f"Command not implemented: {command}"
                )
                
        except Exception as e:
            return create_error_response(command, "E999", f"Command processing error: {e}")
    
    # Legacy Message Handlers (for backward compatibility)
    
    def _handle_legacy_device_info(self, device: AndroidDevice, message: dict):
        """Handle legacy device info message."""
        device_info_data = message.get('data', {})
        device.device_info.firmware_version = device_info_data.get('model', 'unknown')
        # Store additional info in a separate field since DeviceInfo doesn't have these
        device.legacy_info = device_info_data
        logger.info(f"Legacy device info updated for {device.device_id}: {device_info_data}")
    
    def _handle_legacy_authentication(self, device: AndroidDevice, message: dict):
        """Handle legacy authentication message."""
        if not self.security_manager:
            # No security manager - allow all connections
            device.authenticated = True
            device.permissions = ["record", "transfer", "sync"]
            self._send_legacy_auth_response(device, True, "Authentication disabled")
            return
        
        auth_data = message.get('data', {})
        token = auth_data.get('token')
        
        if not token:
            self._send_legacy_auth_response(device, False, "No authentication token provided")
            return
        
        # Validate token
        if self.security_manager.authenticate_device(device.device_id, token):
            device.authenticated = True
            device.permissions = auth_data.get('requested_permissions', ["record"])
            self._send_legacy_auth_response(device, True, "Authentication successful")
            logger.info(f"Device {device.device_id} authenticated successfully")
        else:
            self._send_legacy_auth_response(device, False, "Invalid authentication token")
            logger.warning(f"Authentication failed for device {device.device_id}")
    
    def _send_legacy_auth_response(self, device: AndroidDevice, success: bool, message: str):
        """Send legacy authentication response to device."""
        response = {
            'type': 'auth_response',
            'success': success,
            'message': message,
            'permissions': device.permissions if success else []
        }
        device.send_dict_message(response)
    
    def _handle_legacy_heartbeat(self, device: AndroidDevice, message: dict):
        """Handle legacy heartbeat message."""
        # Update session synchronizer if available
        if self.session_synchronizer:
            self.session_synchronizer.update_device_heartbeat(device.device_id)
    
    def _handle_legacy_recording_status(self, device: AndroidDevice, message: dict):
        """Handle legacy recording status update."""
        status_data = message.get('data', {})
        device.is_recording = status_data.get('is_recording', False)
        logger.info(f"Legacy recording status for {device.device_id}: {device.is_recording}")
    
    def _handle_legacy_file_list_response(self, device: AndroidDevice, message: dict):
        """Handle legacy file list response from device."""
        if not self.transfer_manager:
            logger.warning("No transfer manager available for file list response")
            return
        
        data = message.get('data', {})
        session_id = data.get('session_id')
        file_list = data.get('files', [])
        
        if session_id and file_list:
            self.transfer_manager.handle_file_list_response(device.device_id, session_id, file_list)
    
    def _handle_legacy_file_chunk(self, device: AndroidDevice, message: dict):
        """Handle legacy file chunk from device."""
        if not self.transfer_manager:
            logger.warning("No transfer manager available for file chunk")
            return
        
        data = message.get('data', {})
        file_id = data.get('file_id')
        chunk_data = data.get('chunk_data')
        chunk_index = data.get('chunk_index', 0)
        
        if file_id and chunk_data is not None:
            self.transfer_manager.handle_file_chunk(file_id, chunk_data, chunk_index)
    
    def _handle_legacy_file_complete(self, device: AndroidDevice, message: dict):
        """Handle legacy file transfer completion from device."""
        if not self.transfer_manager:
            logger.warning("No transfer manager available for file completion")
            return
        
        data = message.get('data', {})
        file_id = data.get('file_id')
        
        if file_id:
            self.transfer_manager.handle_file_complete(file_id)
    
    def _handle_legacy_sync_response(self, device: AndroidDevice, message: dict):
        """Handle legacy synchronization response from device."""
        data = message.get('data', {})
        sync_type = data.get('sync_type')
        sync_id = data.get('sync_id')
        
        logger.debug(f"Legacy sync response from {device.device_id}: {sync_type} #{sync_id}")
    
    def _handle_legacy_error(self, device: AndroidDevice, message: dict):
        """Handle legacy error message from device."""
        error_data = message.get('data', {})
        logger.error(f"Legacy error from {device.device_id}: {error_data}")
    
    def _handle_legacy_hello(self, device: AndroidDevice, message: dict):
        """Handle legacy hello message."""
        logger.info(f"Legacy hello from {device.device_id}")
        # Send legacy welcome response
        response = {
            'type': 'hello_response',
            'success': True,
            'server_version': '1.0',
            'features': ['recording', 'sync', 'calibration']
        }
        device.send_dict_message(response)
    
    def _handle_legacy_command(self, device: AndroidDevice, message: dict):
        """Handle legacy command message."""
        command = message.get('command', '')
        data = message.get('data', {})
        
        logger.info(f"Legacy command '{command}' from {device.device_id}")
        
        # Send legacy response
        response = {
            'type': 'response',
            'command': command,
            'success': True,
            'message': f"Command {command} processed",
            'timestamp': time.time()
        }
        device.send_dict_message(response)
    
    def _handle_legacy_response(self, device: AndroidDevice, message: dict):
        """Handle legacy response message."""
        command = message.get('command', '')
        success = message.get('success', False)
        logger.info(f"Legacy response from {device.device_id}: {command} -> {success}")
    
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
    
    def broadcast_command(self, command: str, data: dict = None, use_shared_protocol: bool = True) -> List[str]:
        """Broadcast command to all connected devices."""
        successful_devices = []
        failed_devices = []
        
        for device_id, device in list(self.devices.items()):
            if self.send_command_to_device(device_id, command, data, use_shared_protocol):
                successful_devices.append(device_id)
            else:
                failed_devices.append(device_id)
        
        if failed_devices:
            logger.warning(f"Failed to send command to devices: {failed_devices}")
        
        return successful_devices
    
    def send_command_to_device(self, device_id: str, command: str, data: dict = None, use_shared_protocol: bool = True) -> bool:
        """Send command to specific device using shared protocol or legacy format."""
        if device_id not in self.devices:
            logger.error(f"Device not connected: {device_id}")
            return False
        
        device = self.devices[device_id]
        
        if use_shared_protocol:
            # Use shared protocol format
            message = CommandMessage(
                command=command,
                parameters=data or {},
                device_id=device_id
            )
            success = device.send_message(message)
        else:
            # Use legacy format
            message = {
                'type': 'command',
                'command': command,
                'data': data or {},
                'timestamp': time.time()
            }
            success = device.send_dict_message(message)
        
        if not success:
            self._disconnect_device(device_id)
        
        return success
    
    def broadcast_session_control(self, action: str, session_config: dict = None) -> List[str]:
        """Broadcast session control message using shared protocol."""
        from shared_protocols.data_structures import SessionConfig, DeviceType
        
        # Convert dict to SessionConfig if provided
        config = None
        if session_config:
            config = SessionConfig(
                session_id=session_config.get('session_id', 'default_session'),
                session_name=session_config.get('session_name', 'Default Session'),
                participant_id=session_config.get('participant_id', 'default_participant'),
                researcher_id=session_config.get('researcher_id', 'default_researcher'),
                experiment_type=session_config.get('experiment_type', 'default'),
                expected_duration_minutes=session_config.get('expected_duration_minutes', 60),
                devices_enabled=session_config.get('devices_enabled', [DeviceType.ANDROID_PHONE]),
                sampling_rates=session_config.get('sampling_rates', {'default': 128.0})
            )
        
        message = SessionControlMessage(
            action=action,
            session_config=config
        )
        
        successful_devices = []
        failed_devices = []
        
        for device_id, device in list(self.devices.items()):
            message.device_id = device_id
            if device.send_message(message):
                successful_devices.append(device_id)
            else:
                failed_devices.append(device_id)
                self._disconnect_device(device_id)
        
        if failed_devices:
            logger.warning(f"Failed to send session control to devices: {failed_devices}")
        
        return successful_devices
    
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
                'device_info': device.device_info.to_dict(),
                'device_state': device.device_state.value,
                'protocol_version': device.protocol_version,
                'legacy_info': getattr(device, 'legacy_info', {})
            }
        
        return device_info
    
    def add_test_device(self, device_id: str = "test_device") -> bool:
        """Add a test device for validation purposes."""
        try:
            from datetime import datetime
            from shared_protocols.data_structures import DeviceInfo, DeviceState
            
            # Create a mock device object
            class MockDevice:
                def __init__(self, device_id: str):
                    self.device_id = device_id
                    self.address = "127.0.0.1:test"
                    self.connected_time = datetime.now()
                    self.last_heartbeat = datetime.now()
                    self.is_recording = False
                    self.authenticated = True
                    self.permissions = ["recording", "file_transfer"]
                    self.device_info = DeviceInfo(
                        device_id=device_id,
                        device_type=DeviceType.ANDROID_PHONE,
                        capabilities=["recording", "thermal", "rgb"],
                        firmware_version="test_version",
                        connection_time=time.time()
                    )
                    self.device_state = DeviceState.CONNECTED
                    self.protocol_version = "1.0"
                    self.legacy_info = {
                        "model": "test_device",
                        "os_version": "test"
                    }
                
                def is_alive(self):
                    return True
                
                def send_message(self, message: BaseMessage) -> bool:
                    """Mock send message method."""
                    # Simulate successful message sending
                    return True
                
                def send_dict_message(self, message: dict) -> bool:
                    """Mock send dict message method."""
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