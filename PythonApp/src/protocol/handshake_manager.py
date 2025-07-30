"""
HandshakeManager for Python - handles initial handshake with version checking.

This module implements the handshake protocol described in Milestone 6 to ensure
compatibility between Android and Python applications by exchanging protocol
version information at connection start.
"""

import json
import logging
import socket
import time
from typing import Dict, Any, Optional, Tuple
import platform

from .config_loader import get_config_manager
from .schema_utils import get_schema_manager

logger = logging.getLogger(__name__)


class HandshakeManager:
    """Manages handshake protocol for version compatibility checking."""
    
    def __init__(self):
        """Initialize the handshake manager."""
        self.config_manager = get_config_manager()
        self.schema_manager = get_schema_manager()
        self.protocol_version = self.config_manager.get('protocol_version', 1)
        self.app_version = self.config_manager.get('version', '1.0.0')
    
    def send_handshake(self, sock: socket.socket) -> bool:
        """
        Send handshake message to the client.
        
        Args:
            sock: Connected socket to send handshake through
            
        Returns:
            True if handshake was sent successfully, False otherwise
        """
        try:
            handshake_message = self._create_handshake_message()
            message_json = json.dumps(handshake_message)
            
            logger.info(f"Sending handshake: {message_json}")
            
            # Send message with newline delimiter
            sock.send(message_json.encode('utf-8'))
            sock.send(b'\n')
            
            logger.info("Handshake sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send handshake: {e}")
            return False
    
    def process_handshake(self, handshake_message: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Process received handshake message and determine compatibility.
        
        Args:
            handshake_message: Dictionary containing handshake message
            
        Returns:
            Tuple of (compatible, message) where compatible is bool and message is str
        """
        try:
            # Validate the message against schema
            if not self.schema_manager.validate_message(handshake_message):
                logger.error("Invalid handshake message format")
                return False, "Invalid handshake message format"
            
            client_protocol_version = handshake_message.get('protocol_version')
            device_name = handshake_message.get('device_name', 'Unknown Device')
            app_version = handshake_message.get('app_version', 'Unknown')
            device_type = handshake_message.get('device_type', 'unknown')
            
            logger.info(f"Received handshake from {device_name} ({device_type}) v{app_version}")
            logger.info(f"Client protocol version: {client_protocol_version}")
            logger.info(f"Server protocol version: {self.protocol_version}")
            
            # Check version compatibility
            compatible = self._are_versions_compatible(client_protocol_version, self.protocol_version)
            
            if not compatible:
                message = f"Protocol version mismatch: client v{client_protocol_version}, server v{self.protocol_version}"
                logger.warning(message)
                logger.warning("Consider updating both applications to the same version")
                return False, message
            
            logger.info("Handshake successful - protocol versions compatible")
            return True, "Protocol versions compatible"
            
        except Exception as e:
            error_msg = f"Error processing handshake: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_handshake_ack(self, sock: socket.socket, compatible: bool, message: str = "") -> bool:
        """
        Send handshake acknowledgment message.
        
        Args:
            sock: Connected socket to send acknowledgment through
            compatible: Whether the protocol versions are compatible
            message: Optional message about compatibility status
            
        Returns:
            True if acknowledgment was sent successfully, False otherwise
        """
        try:
            ack_message = self._create_handshake_ack(compatible, message)
            message_json = json.dumps(ack_message)
            
            logger.info(f"Sending handshake ack: {message_json}")
            
            # Send message with newline delimiter
            sock.send(message_json.encode('utf-8'))
            sock.send(b'\n')
            
            logger.info("Handshake acknowledgment sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send handshake acknowledgment: {e}")
            return False
    
    def process_handshake_ack(self, ack_message: Dict[str, Any]) -> bool:
        """
        Process received handshake acknowledgment.
        
        Args:
            ack_message: Dictionary containing handshake acknowledgment
            
        Returns:
            True if handshake is compatible, False otherwise
        """
        try:
            # Validate the message against schema
            if not self.schema_manager.validate_message(ack_message):
                logger.error("Invalid handshake acknowledgment format")
                return False
            
            server_protocol_version = ack_message.get('protocol_version')
            server_name = ack_message.get('server_name', 'Unknown Server')
            server_version = ack_message.get('server_version', 'Unknown')
            compatible = ack_message.get('compatible', False)
            message = ack_message.get('message', '')
            
            logger.info(f"Received handshake ack from {server_name} v{server_version}")
            logger.info(f"Server protocol version: {server_protocol_version}")
            logger.info(f"Client protocol version: {self.protocol_version}")
            
            if not compatible:
                logger.warning("Protocol version mismatch detected!")
                logger.warning(f"Server message: {message}")
                
                # Log detailed version information for debugging
                if server_protocol_version != self.protocol_version:
                    logger.warning(f"Version mismatch: Python v{self.protocol_version}, Server v{server_protocol_version}")
                    logger.warning("Consider updating both applications to the same version")
                
                return False
            
            logger.info("Handshake successful - protocol versions compatible")
            if message:
                logger.info(f"Server message: {message}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing handshake acknowledgment: {e}")
            return False
    
    def _create_handshake_message(self) -> Dict[str, Any]:
        """
        Create handshake message with device information.
        
        Returns:
            Dictionary containing handshake message
        """
        return self.schema_manager.create_message('handshake', 
            protocol_version=self.protocol_version,
            device_name=self._get_device_name(),
            app_version=self.app_version,
            device_type='pc'
        )
    
    def _create_handshake_ack(self, compatible: bool, message: str = "") -> Dict[str, Any]:
        """
        Create handshake acknowledgment message.
        
        Args:
            compatible: Whether the protocol versions are compatible
            message: Optional message about compatibility status
            
        Returns:
            Dictionary containing handshake acknowledgment
        """
        ack_data = {
            'protocol_version': self.protocol_version,
            'server_name': 'Python PC Controller',
            'server_version': self.app_version,
            'compatible': compatible
        }
        
        if message:
            ack_data['message'] = message
        
        return self.schema_manager.create_message('handshake_ack', **ack_data)
    
    def _get_device_name(self) -> str:
        """
        Get a human-readable device name.
        
        Returns:
            Device name string
        """
        try:
            return f"{platform.system()} {platform.node()}"
        except Exception:
            return "Python PC"
    
    def _are_versions_compatible(self, client_version: int, server_version: int) -> bool:
        """
        Check if two protocol versions are compatible.
        
        Currently implements exact version matching, but could be extended
        to support backward compatibility rules in the future.
        
        Args:
            client_version: Client protocol version
            server_version: Server protocol version
            
        Returns:
            True if versions are compatible
        """
        # For now, require exact version match
        # In the future, this could implement more sophisticated compatibility rules
        return client_version == server_version


# Module-level convenience functions
_handshake_manager = None

def get_handshake_manager() -> HandshakeManager:
    """Get the global handshake manager instance."""
    global _handshake_manager
    if _handshake_manager is None:
        _handshake_manager = HandshakeManager()
    return _handshake_manager

def send_handshake(sock: socket.socket) -> bool:
    """Send handshake message using the global manager."""
    return get_handshake_manager().send_handshake(sock)

def process_handshake(handshake_message: Dict[str, Any]) -> Tuple[bool, str]:
    """Process handshake message using the global manager."""
    return get_handshake_manager().process_handshake(handshake_message)

def send_handshake_ack(sock: socket.socket, compatible: bool, message: str = "") -> bool:
    """Send handshake acknowledgment using the global manager."""
    return get_handshake_manager().send_handshake_ack(sock, compatible, message)

def process_handshake_ack(ack_message: Dict[str, Any]) -> bool:
    """Process handshake acknowledgment using the global manager."""
    return get_handshake_manager().process_handshake_ack(ack_message)
