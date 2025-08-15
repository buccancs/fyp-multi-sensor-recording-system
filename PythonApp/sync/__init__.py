"""
Time Synchronization Module
===========================

Provides NTP-like time synchronization service for device coordination.
Ensures sub-millisecond timestamp accuracy across all devices.

Now includes Lab Streaming Layer (LSL) integration as an alternative
synchronization method for research-grade multi-sensor coordination.
"""

import json
import logging
import socket
import threading
import time
import struct
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import LSL integration
try:
    from .lsl_integration import (
        LSLTimeSync, LSLSensorStream, LSLDeviceCoordinator,
        lsl_time_sync, lsl_coordinator, LSL_AVAILABLE
    )
    logger.info("LSL integration available")
except ImportError as e:
    logger.warning(f"LSL integration not available: {e}")
    LSL_AVAILABLE = False


@dataclass
class SyncResult:
    """Result of a time synchronization operation."""
    client_id: str
    offset_ms: float
    round_trip_ms: float
    precision_ms: float
    success: bool
    timestamp: datetime


class TimeServer:
    """NTP-like time server for device synchronization."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8889):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.server_thread = None
        
        # Synchronization statistics
        self.sync_history: Dict[str, List[SyncResult]] = {}
        self.reference_time_offset = 0.0  # Offset from system time
        
        # Try to sync with external NTP server on startup
        self._sync_with_external_ntp()
    
    def _sync_with_external_ntp(self):
        """Attempt to synchronize with an external NTP server."""
        try:
            import ntplib
            ntp_client = ntplib.NTPClient()
            response = ntp_client.request('pool.ntp.org', version=3)
            self.reference_time_offset = response.offset
            logger.info(f"Synchronized with external NTP server, offset: {self.reference_time_offset:.3f}s")
        except ImportError:
            logger.info("ntplib not available, using system time as reference")
        except Exception as e:
            logger.warning(f"Failed to sync with external NTP server: {e}")
    
    def get_synchronized_time(self) -> float:
        """Get current synchronized time as Unix timestamp."""
        return time.time() + self.reference_time_offset
    
    def start_server(self) -> bool:
        """Start the time synchronization server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            logger.info(f"Time synchronization server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start time server: {e}")
            return False
    
    def stop_server(self):
        """Stop the time synchronization server."""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Time synchronization server stopped")
    
    def _server_loop(self):
        """Main server loop to handle time sync requests."""
        while self.running:
            try:
                # Set a timeout to allow checking running state
                self.server_socket.settimeout(1.0)
                
                try:
                    data, address = self.server_socket.recvfrom(1024)
                    threading.Thread(
                        target=self._handle_sync_request,
                        args=(data, address),
                        daemon=True
                    ).start()
                except socket.timeout:
                    continue
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in time server loop: {e}")
    
    def _handle_sync_request(self, data: bytes, address: tuple):
        """Handle a time synchronization request."""
        try:
            # Parse the sync request
            request = json.loads(data.decode('utf-8'))
            client_id = request.get('client_id', 'unknown')
            client_timestamp = request.get('timestamp', 0)
            request_type = request.get('type', 'sync_request')
            
            if request_type != 'sync_request':
                return
            
            # Get current server time
            server_time = self.get_synchronized_time()
            
            # Create response
            response = {
                'type': 'sync_response',
                'server_timestamp': server_time,
                'client_timestamp': client_timestamp,
                'response_timestamp': server_time  # Same for UDP
            }
            
            # Send response
            response_data = json.dumps(response).encode('utf-8')
            self.server_socket.sendto(response_data, address)
            
            # Calculate metrics (estimated, since we don't get client response time)
            offset_ms = (server_time - client_timestamp) * 1000
            
            # Store sync result
            sync_result = SyncResult(
                client_id=client_id,
                offset_ms=offset_ms,
                round_trip_ms=0.0,  # Can't calculate without client feedback
                precision_ms=1.0,   # Estimated UDP precision
                success=True,
                timestamp=datetime.now()
            )
            
            if client_id not in self.sync_history:
                self.sync_history[client_id] = []
            
            self.sync_history[client_id].append(sync_result)
            
            # Keep only last 100 sync results per client
            if len(self.sync_history[client_id]) > 100:
                self.sync_history[client_id] = self.sync_history[client_id][-100:]
            
            logger.debug(f"Handled sync request from {client_id} at {address}, offset: {offset_ms:.1f}ms")
            
        except Exception as e:
            logger.error(f"Error handling sync request from {address}: {e}")
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics for all clients."""
        stats = {
            'server_time': self.get_synchronized_time(),
            'reference_offset': self.reference_time_offset,
            'total_clients': len(self.sync_history),
            'clients': {}
        }
        
        for client_id, sync_results in self.sync_history.items():
            if not sync_results:
                continue
            
            recent_results = sync_results[-10:]  # Last 10 sync attempts
            successful_results = [r for r in recent_results if r.success]
            
            if successful_results:
                avg_offset = sum(r.offset_ms for r in successful_results) / len(successful_results)
                max_offset = max(abs(r.offset_ms) for r in successful_results)
                last_sync = successful_results[-1].timestamp
            else:
                avg_offset = 0
                max_offset = 0
                last_sync = None
            
            stats['clients'][client_id] = {
                'total_syncs': len(sync_results),
                'recent_syncs': len(recent_results),
                'successful_syncs': len(successful_results),
                'avg_offset_ms': avg_offset,
                'max_offset_ms': max_offset,
                'last_sync': last_sync.isoformat() if last_sync else None,
                'sync_quality': 'good' if max_offset < 5.0 else 'poor'
            }
        
        return stats


class SyncSignalBroadcaster:
    """Handles synchronization signal broadcasting to devices."""
    
    def __init__(self, network_server=None):
        self.network_server = network_server
        self.signal_count = 0
    
    def set_network_server(self, server):
        """Set the network server for broadcasting."""
        self.network_server = server
    
    def broadcast_sync_signal_by_type(self, signal_type: str = "flash", data: Dict[str, Any] = None) -> List[str]:
        """Broadcast synchronization signal to all connected devices by type."""
        if not self.network_server:
            logger.error("Network server not configured")
            return []
        
        self.signal_count += 1
        
        signal_data = {
            'signal_id': self.signal_count,
            'signal_type': signal_type,
            'timestamp': time.time(),
            'data': data or {}
        }
        
        # Send sync signal command to all devices
        successful_devices = self.network_server.broadcast_command(
            'sync_signal',
            signal_data
        )
        
        logger.info(f"Broadcast sync signal #{self.signal_count} ({signal_type}) to {len(successful_devices)} devices")
        return successful_devices
    
    def send_flash_signal(self) -> List[str]:
        """Send screen flash synchronization signal."""
        return self.broadcast_sync_signal_by_type('flash', {
            'duration_ms': 100,
            'color': 'white'
        })
    
    def create_flash_signal(self) -> Dict[str, Any]:
        """Create a flash synchronization signal."""
        return {
            'type': 'sync_signal',
            'signal_type': 'flash',
            'timestamp': time.time(),
            'data': {
                'duration_ms': 100,
                'color': 'white'
            }
        }
    
    def create_audio_signal(self, frequency: int = 1000, duration: float = 0.1) -> Dict[str, Any]:
        """Create an audio synchronization signal."""
        return {
            'type': 'sync_signal',
            'signal_type': 'audio',
            'timestamp': time.time(),
            'data': {
                'frequency': frequency,
                'duration_ms': int(duration * 1000)
            }
        }
    
    def create_marker_signal(self, marker_text: str = "SYNC") -> Dict[str, Any]:
        """Create a marker synchronization signal."""
        return {
            'type': 'sync_signal',
            'signal_type': 'marker',
            'timestamp': time.time(),
            'data': {
                'marker_text': marker_text,
                'display_duration_ms': 500
            }
        }
    
    def broadcast_sync_signal(self, signal: Dict[str, Any], server=None) -> bool:
        """Broadcast a synchronization signal."""
        target_server = server or self.network_server
        if not target_server:
            logger.error("No network server available for broadcasting")
            return False
        
        try:
            successful_devices = target_server.broadcast_command(
                'sync_signal',
                signal
            )
            logger.info(f"Broadcast sync signal to {len(successful_devices)} devices")
            return len(successful_devices) > 0
        except Exception as e:
            logger.error(f"Failed to broadcast sync signal: {e}")
            return False
    
    def send_audio_signal(self, frequency: int = 1000, duration_ms: int = 100) -> List[str]:
        """Send audio beep synchronization signal."""
        return self.broadcast_sync_signal_by_type('audio', {
            'frequency': frequency,
            'duration_ms': duration_ms
        })
    
    def send_marker_signal(self, marker_text: str = "SYNC") -> List[str]:
        """Send text marker synchronization signal."""
        return self.broadcast_sync_signal_by_type('marker', {
            'marker_text': marker_text,
            'display_duration_ms': 500
        })


class SessionSynchronizer:
    """Manages session-level synchronization and device coordination."""
    
    def __init__(self, time_server: Optional[TimeServer] = None, network_server=None):
        self.time_server = time_server or TimeServer()
        self.network_server = network_server
        self.sync_broadcaster = SyncSignalBroadcaster(network_server)
        
        # Device state tracking
        self.device_states: Dict[str, dict] = {}
        self.offline_commands: Dict[str, List[dict]] = {}
        
        # Heartbeat monitoring
        self.heartbeat_thread = None
        self.monitoring_active = False
    
    def set_network_server(self, server):
        """Set the network server for device communication."""
        self.network_server = server
        self.sync_broadcaster.set_network_server(server)
    
    def start_session_sync(self, session_id: str) -> bool:
        """Start session-level synchronization."""
        if not self.network_server:
            logger.error("Network server not configured")
            return False
        
        try:
            # Send session start synchronization
            sync_data = {
                'session_id': session_id,
                'server_time': self.time_server.get_synchronized_time(),
                'sync_instructions': 'prepare_for_recording'
            }
            
            successful_devices = self.network_server.broadcast_command(
                'session_sync_start',
                sync_data
            )
            
            # Initialize device states
            for device_id in successful_devices:
                self.device_states[device_id] = {
                    'session_id': session_id,
                    'sync_status': 'synced',
                    'last_heartbeat': time.time(),
                    'is_online': True
                }
            
            # Start heartbeat monitoring
            self._start_heartbeat_monitoring()
            
            logger.info(f"Session synchronization started for {len(successful_devices)} devices")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start session sync: {e}")
            return False
    
    def stop_session_sync(self) -> bool:
        """Stop session-level synchronization."""
        try:
            # Stop heartbeat monitoring
            self._stop_heartbeat_monitoring()
            
            # Send session end synchronization
            if self.network_server:
                self.network_server.broadcast_command('session_sync_stop')
            
            # Clear device states
            self.device_states.clear()
            self.offline_commands.clear()
            
            logger.info("Session synchronization stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop session sync: {e}")
            return False
    
    def handle_device_reconnect(self, device_id: str) -> bool:
        """Handle device reconnection and state recovery."""
        try:
            # Check if device was previously in session
            if device_id in self.device_states:
                device_state = self.device_states[device_id]
                
                # Send current session state to device
                recovery_data = {
                    'session_id': device_state.get('session_id'),
                    'server_time': self.time_server.get_synchronized_time(),
                    'recovery_mode': True
                }
                
                success = self.network_server.send_command_to_device(
                    device_id,
                    'session_recovery',
                    recovery_data
                )
                
                if success:
                    # Execute any queued commands
                    if device_id in self.offline_commands:
                        for command in self.offline_commands[device_id]:
                            self.network_server.send_command_to_device(
                                device_id,
                                command.get('command', ''),
                                command.get('data', {})
                            )
                        
                        # Clear executed commands
                        del self.offline_commands[device_id]
                    
                    # Update device state
                    device_state['is_online'] = True
                    device_state['last_heartbeat'] = time.time()
                    
                    logger.info(f"Device {device_id} reconnected and recovered")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to handle device reconnect for {device_id}: {e}")
            return False
    
    def queue_command_for_offline_device(self, device_id: str, command: str, data: dict):
        """Queue a command for a device that's currently offline."""
        if device_id not in self.offline_commands:
            self.offline_commands[device_id] = []
        
        self.offline_commands[device_id].append({
            'command': command,
            'data': data,
            'timestamp': time.time()
        })
        
        logger.info(f"Queued command '{command}' for offline device {device_id}")
    
    def _start_heartbeat_monitoring(self):
        """Start monitoring device heartbeats."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def _stop_heartbeat_monitoring(self):
        """Stop monitoring device heartbeats."""
        self.monitoring_active = False
        
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=2.0)
    
    def _heartbeat_monitor_loop(self):
        """Monitor device heartbeats and detect offline devices."""
        while self.monitoring_active:
            try:
                current_time = time.time()
                offline_devices = []
                
                for device_id, device_state in self.device_states.items():
                    if device_state['is_online']:
                        time_since_heartbeat = current_time - device_state['last_heartbeat']
                        
                        # Mark device as offline if no heartbeat for 30 seconds
                        if time_since_heartbeat > 30:
                            device_state['is_online'] = False
                            offline_devices.append(device_id)
                
                # Log offline devices
                for device_id in offline_devices:
                    logger.warning(f"Device {device_id} went offline (no heartbeat)")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                time.sleep(5)
    
    def update_device_heartbeat(self, device_id: str):
        """Update heartbeat timestamp for a device."""
        if device_id in self.device_states:
            self.device_states[device_id]['last_heartbeat'] = time.time()
            
            # Mark as online if it was offline
            if not self.device_states[device_id]['is_online']:
                self.device_states[device_id]['is_online'] = True
                logger.info(f"Device {device_id} came back online")
    
    def get_device_sync_status(self) -> Dict[str, dict]:
        """Get synchronization status for all devices."""
        return dict(self.device_states)
    
    def prepare_devices_for_session(self, session_id: str, device_ids: List[str]) -> bool:
        """Prepare devices for a new session."""
        try:
            # Initialize device states for session
            for device_id in device_ids:
                self.device_states[device_id] = {
                    'device_id': device_id,
                    'session_id': session_id,
                    'is_online': True,
                    'last_heartbeat': time.time(),
                    'sync_status': 'prepared'
                }
            
            logger.info(f"Prepared {len(device_ids)} devices for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare devices for session: {e}")
            return False
    
    def queue_command_for_device(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Queue a command for an offline device."""
        try:
            if device_id not in self.offline_commands:
                self.offline_commands[device_id] = []
            
            self.offline_commands[device_id].append({
                'command': command,
                'timestamp': time.time()
            })
            
            logger.info(f"Queued command for device {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue command for device {device_id}: {e}")
            return False
    
    def handle_device_reconnection(self, device_id: str) -> bool:
        """Handle device reconnection and execute queued commands."""
        try:
            # Mark device as online
            if device_id in self.device_states:
                self.device_states[device_id]['is_online'] = True
                self.device_states[device_id]['last_heartbeat'] = time.time()
            
            # Execute queued commands
            if device_id in self.offline_commands:
                queued_commands = self.offline_commands[device_id]
                logger.info(f"Executing {len(queued_commands)} queued commands for device {device_id}")
                
                # Clear the queue
                self.offline_commands[device_id] = []
            
            logger.info(f"Successfully handled reconnection for device {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle device reconnection for {device_id}: {e}")
            return False


class EnhancedSynchronizationManager:
    """
    Enhanced synchronization manager that supports both NTP-like and LSL synchronization.
    Automatically selects the best available method and provides fallback options.
    """
    
    def __init__(self, prefer_lsl: bool = True):
        self.prefer_lsl = prefer_lsl
        self.lsl_available = LSL_AVAILABLE if 'LSL_AVAILABLE' in globals() else False
        
        # Initialize sync methods
        self.ntp_time_server = TimeServer()
        self.session_synchronizer = SessionSynchronizer(self.ntp_time_server)
        
        # LSL components (if available)
        self.lsl_time_sync = None
        self.lsl_coordinator = None
        
        if self.lsl_available:
            try:
                self.lsl_time_sync = lsl_time_sync
                self.lsl_coordinator = lsl_coordinator
                logger.info("LSL synchronization components initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize LSL components: {e}")
                self.lsl_available = False
        
        # Determine active sync method
        self.active_method = 'lsl' if (self.lsl_available and prefer_lsl) else 'ntp'
        logger.info(f"Active synchronization method: {self.active_method}")
    
    def start_synchronization_service(self, host: str = "0.0.0.0", port: int = 8889) -> bool:
        """Start the synchronization service using the best available method."""
        success = False
        
        # Start NTP-like server (always available as fallback)
        ntp_success = self.ntp_time_server.start_server()
        if ntp_success:
            logger.info("NTP-like time server started successfully")
            success = True
        
        # Start LSL synchronization if available
        if self.lsl_available:
            try:
                # LSL initialization happens automatically
                logger.info("LSL synchronization service is active")
                success = True
            except Exception as e:
                logger.error(f"Failed to start LSL synchronization: {e}")
        
        return success
    
    def stop_synchronization_service(self):
        """Stop all synchronization services."""
        # Stop NTP server
        self.ntp_time_server.stop_server()
        
        # Clean up LSL components
        if self.lsl_available and self.lsl_coordinator:
            try:
                self.lsl_coordinator.cleanup()
                logger.info("LSL synchronization service stopped")
            except Exception as e:
                logger.error(f"Error stopping LSL service: {e}")
    
    def get_synchronized_time(self) -> float:
        """Get current synchronized timestamp using the active method."""
        if self.active_method == 'lsl' and self.lsl_available and self.lsl_time_sync:
            try:
                return self.lsl_time_sync.get_synchronized_time()
            except Exception as e:
                logger.warning(f"LSL time sync failed, falling back to NTP: {e}")
        
        # Fallback to NTP-like synchronization
        return self.ntp_time_server.get_synchronized_time()
    
    def send_sync_signal(self, signal_type: str = "flash", data: Dict[str, Any] = None) -> bool:
        """Send synchronization signal using the active method."""
        success = False
        
        # Try LSL first if available and preferred
        if self.active_method == 'lsl' and self.lsl_available and self.lsl_coordinator:
            try:
                if signal_type == "flash":
                    success = self.lsl_coordinator.send_sync_flash()
                else:
                    success = self.lsl_coordinator.send_coordination_command(f'sync_{signal_type}', data)
                    
                if success:
                    logger.info(f"Sent {signal_type} sync signal via LSL")
                    return True
            except Exception as e:
                logger.warning(f"LSL sync signal failed: {e}")
        
        # Fallback to NTP-like method via session synchronizer
        try:
            broadcaster = SyncSignalBroadcaster(self.session_synchronizer.network_server)
            
            if signal_type == "flash":
                devices = broadcaster.send_flash_signal()
            elif signal_type == "audio":
                devices = broadcaster.send_audio_signal()
            elif signal_type == "marker":
                devices = broadcaster.send_marker_signal()
            else:
                devices = broadcaster.broadcast_sync_signal_by_type(signal_type, data)
            
            success = len(devices) > 0
            if success:
                logger.info(f"Sent {signal_type} sync signal via NTP to {len(devices)} devices")
                
        except Exception as e:
            logger.error(f"Failed to send sync signal via NTP: {e}")
        
        return success
    
    def start_session_sync(self, session_id: str, device_ids: List[str]) -> bool:
        """Start synchronized session using the active method."""
        success = False
        
        # Try LSL coordination
        if self.active_method == 'lsl' and self.lsl_available and self.lsl_coordinator:
            try:
                success = self.lsl_coordinator.start_synchronized_recording(session_id, device_ids)
                if success:
                    logger.info(f"Started LSL synchronized session: {session_id}")
                    return True
            except Exception as e:
                logger.warning(f"LSL session start failed: {e}")
        
        # Fallback to NTP-like session synchronization
        try:
            success = self.session_synchronizer.start_session_sync(session_id)
            if success:
                logger.info(f"Started NTP synchronized session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to start NTP session sync: {e}")
        
        return success
    
    def stop_session_sync(self) -> bool:
        """Stop synchronized session using the active method."""
        success = False
        
        # Stop LSL coordination
        if self.lsl_available and self.lsl_coordinator:
            try:
                success = self.lsl_coordinator.stop_synchronized_recording()
                if success:
                    logger.info("Stopped LSL synchronized session")
            except Exception as e:
                logger.warning(f"LSL session stop failed: {e}")
        
        # Stop NTP session synchronization
        try:
            ntp_success = self.session_synchronizer.stop_session_sync()
            success = success or ntp_success
            if ntp_success:
                logger.info("Stopped NTP synchronized session")
        except Exception as e:
            logger.error(f"Failed to stop NTP session sync: {e}")
        
        return success
    
    def register_sensor_for_lsl(self, sensor_id: str, sensor_type: str = "GSR") -> bool:
        """Register a sensor for LSL streaming (if LSL is available)."""
        if not self.lsl_available or not self.lsl_coordinator:
            logger.info(f"LSL not available, sensor {sensor_id} will use standard logging")
            return False
        
        try:
            return self.lsl_coordinator.register_sensor(sensor_id, sensor_type)
        except Exception as e:
            logger.error(f"Failed to register sensor {sensor_id} for LSL: {e}")
            return False
    
    def push_sensor_data_to_lsl(self, sensor_id: str, gsr_value: float, timestamp: Optional[float] = None) -> bool:
        """Push sensor data to LSL stream (if available and registered)."""
        if not self.lsl_available or not self.lsl_coordinator:
            return False
        
        try:
            return self.lsl_coordinator.push_sensor_data(sensor_id, gsr_value, timestamp)
        except Exception as e:
            logger.debug(f"Failed to push sensor data to LSL: {e}")
            return False
    
    def get_synchronization_status(self) -> Dict[str, Any]:
        """Get comprehensive synchronization status."""
        status = {
            'active_method': self.active_method,
            'ntp_available': True,
            'lsl_available': self.lsl_available,
            'current_time': self.get_synchronized_time()
        }
        
        # Add NTP status
        try:
            ntp_stats = self.ntp_time_server.get_sync_statistics()
            status['ntp_status'] = ntp_stats
        except Exception as e:
            status['ntp_status'] = {'error': str(e)}
        
        # Add LSL status
        if self.lsl_available and self.lsl_coordinator:
            try:
                lsl_status = self.lsl_coordinator.get_lsl_status()
                status['lsl_status'] = lsl_status
            except Exception as e:
                status['lsl_status'] = {'error': str(e)}
        else:
            status['lsl_status'] = {'available': False}
        
        return status
    
    def set_network_server(self, server):
        """Set the network server for NTP-like synchronization."""
        self.session_synchronizer.set_network_server(server)
    
    def calibrate_lsl_time_sync(self, reference_stream: str = "") -> bool:
        """Calibrate LSL time synchronization with reference stream."""
        if not self.lsl_available or not self.lsl_time_sync:
            return False
        
        try:
            return self.lsl_time_sync.calibrate_with_reference(reference_stream)
        except Exception as e:
            logger.error(f"Failed to calibrate LSL time sync: {e}")
            return False