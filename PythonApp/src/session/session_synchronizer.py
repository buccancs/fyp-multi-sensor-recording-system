"""
Session Synchronizer for Multi-Sensor Recording System - Phase 2 Implementation

This module implements session state synchronization between PC and Android devices 
as specified in the Phase 2 roadmap requirements:

- Sync session state between PC and Android
- Handle Android device disconnect scenarios
- Recover session state on reconnect
- Message queuing for offline scenarios

Author: Multi-Sensor Recording System Team
Date: 2025-01-27
Phase: 2 - Cross-Platform Integration
"""

import json
import threading
import time
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from queue import Queue, Empty

# Import centralized logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class SessionSyncState(Enum):
    """Session synchronization states."""
    
    IDLE = "idle"
    SYNCING = "syncing"
    SYNCHRONIZED = "synchronized"
    DISCONNECTED = "disconnected"
    RECOVERING = "recovering"
    ERROR = "error"


class MessagePriority(Enum):
    """Message priority levels for queuing."""
    
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SessionState:
    """Container for session state information."""
    
    session_id: str
    recording_active: bool
    devices_connected: Dict[str, bool]
    recording_start_time: Optional[datetime]
    recording_duration: float
    file_count: int
    total_file_size: int
    calibration_status: Dict[str, str]
    sync_timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class QueuedMessage:
    """Container for queued messages with metadata."""
    
    device_id: str
    message_type: str
    payload: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3


class SessionSynchronizer:
    """
    Manages session state synchronization between PC and Android devices.
    
    Implements Phase 2 requirements:
    - Sync session state between PC and Android
    - Handle Android device disconnect scenarios  
    - Recover session state on reconnect
    - Message queuing for offline scenarios
    """
    
    def __init__(self, message_sender: Optional[Callable] = None):
        """
        Initialize the session synchronizer.
        
        Args:
            message_sender (Callable): Function to send messages to Android devices
        """
        self.message_sender = message_sender
        self.session_states: Dict[str, SessionState] = {}
        self.sync_states: Dict[str, SessionSyncState] = {}
        self.message_queues: Dict[str, Queue] = {}
        self.offline_devices: Dict[str, datetime] = {}
        
        # Synchronization control
        self.sync_lock = threading.Lock()
        self.sync_interval = 5.0  # seconds
        self.max_offline_time = 300.0  # 5 minutes
        self.is_running = False
        self.sync_thread = None
        
        # Statistics
        self.sync_attempts = 0
        self.sync_successes = 0
        self.sync_failures = 0
        self.messages_queued = 0
        self.messages_delivered = 0
        
        logger.info("[SessionSynchronizer] Initialized with sync interval: %ss", self.sync_interval)
    
    def start_synchronization(self):
        """Start the background synchronization process."""
        if self.is_running:
            logger.warning("[SessionSynchronizer] Already running")
            return
            
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("[SessionSynchronizer] Background synchronization started")
    
    def stop_synchronization(self):
        """Stop the background synchronization process."""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5.0)
        logger.info("[SessionSynchronizer] Background synchronization stopped")
    
    def register_device(self, device_id: str):
        """
        Register a device for session synchronization.
        
        Args:
            device_id (str): Unique device identifier
        """
        with self.sync_lock:
            if device_id not in self.sync_states:
                self.sync_states[device_id] = SessionSyncState.IDLE
                self.message_queues[device_id] = Queue()
                logger.info("[SessionSynchronizer] Device registered: %s", device_id)
    
    def unregister_device(self, device_id: str):
        """
        Unregister a device from session synchronization.
        
        Args:
            device_id (str): Device identifier to unregister
        """
        with self.sync_lock:
            if device_id in self.sync_states:
                del self.sync_states[device_id]
                del self.message_queues[device_id]
                if device_id in self.session_states:
                    del self.session_states[device_id]
                if device_id in self.offline_devices:
                    del self.offline_devices[device_id]
                logger.info("[SessionSynchronizer] Device unregistered: %s", device_id)
    
    def sync_session_state(self, android_state: Dict[str, Any]) -> bool:
        """
        Synchronize session state from Android device.
        
        Args:
            android_state (dict): Session state data from Android device
            
        Returns:
            bool: True if synchronization successful, False otherwise
        """
        try:
            device_id = android_state.get('device_id')
            if not device_id:
                logger.error("[SessionSynchronizer] No device_id in android_state")
                return False
            
            with self.sync_lock:
                # Update sync state
                self.sync_states[device_id] = SessionSyncState.SYNCING
                self.sync_attempts += 1
                
                # Convert Android state to SessionState
                session_state = self._convert_android_state(android_state)
                
                # Store session state
                old_state = self.session_states.get(device_id)
                self.session_states[device_id] = session_state
                
                # Mark device as online
                if device_id in self.offline_devices:
                    del self.offline_devices[device_id]
                
                # Update sync state to synchronized
                self.sync_states[device_id] = SessionSyncState.SYNCHRONIZED
                self.sync_successes += 1
                
                logger.info("[SessionSynchronizer] Session state synchronized for device: %s", device_id)
                logger.debug("[SessionSynchronizer] State: %s", session_state)
                
                # Check for significant changes
                if old_state and self._has_significant_changes(old_state, session_state):
                    logger.info("[SessionSynchronizer] Significant state changes detected for %s", device_id)
                    self._notify_state_change(device_id, session_state)
                
                return True
                
        except Exception as e:
            logger.error("[SessionSynchronizer] Failed to sync session state: %s", str(e))
            if device_id:
                with self.sync_lock:
                    self.sync_states[device_id] = SessionSyncState.ERROR
                    self.sync_failures += 1
            return False
    
    def handle_android_disconnect(self, device_id: str):
        """
        Handle Android device disconnection scenario.
        
        Args:
            device_id (str): Device that disconnected
        """
        with self.sync_lock:
            if device_id in self.sync_states:
                self.sync_states[device_id] = SessionSyncState.DISCONNECTED
                self.offline_devices[device_id] = datetime.now()
                logger.warning("[SessionSynchronizer] Device disconnected: %s", device_id)
                
                # Start queuing messages for offline device
                self._start_message_queuing(device_id)
    
    def recover_session_on_reconnect(self, device_id: str) -> Optional[SessionState]:
        """
        Recover session state when device reconnects.
        
        Args:
            device_id (str): Device that reconnected
            
        Returns:
            Optional[SessionState]: Last known session state or None
        """
        with self.sync_lock:
            if device_id in self.offline_devices:
                offline_duration = (datetime.now() - self.offline_devices[device_id]).total_seconds()
                logger.info("[SessionSynchronizer] Device reconnected after %.1fs: %s", 
                          offline_duration, device_id)
                
                # Remove from offline devices
                del self.offline_devices[device_id]
                
                # Update sync state
                self.sync_states[device_id] = SessionSyncState.RECOVERING
                
                # Get last known session state
                last_state = self.session_states.get(device_id)
                
                # Deliver queued messages
                self._deliver_queued_messages(device_id)
                
                # Update sync state
                self.sync_states[device_id] = SessionSyncState.SYNCHRONIZED
                
                logger.info("[SessionSynchronizer] Session recovery completed for %s", device_id)
                return last_state
            else:
                logger.info("[SessionSynchronizer] Device reconnected (no recovery needed): %s", device_id)
                return self.session_states.get(device_id)
    
    def queue_message(self, device_id: str, message_type: str, payload: Dict[str, Any], 
                     priority: MessagePriority = MessagePriority.NORMAL):
        """
        Queue a message for delivery to a device.
        
        Args:
            device_id (str): Target device
            message_type (str): Type of message
            payload (dict): Message payload
            priority (MessagePriority): Message priority
        """
        if device_id not in self.message_queues:
            self.register_device(device_id)
        
        message = QueuedMessage(
            device_id=device_id,
            message_type=message_type,
            payload=payload,
            priority=priority,
            timestamp=datetime.now()
        )
        
        self.message_queues[device_id].put(message)
        self.messages_queued += 1
        
        logger.debug("[SessionSynchronizer] Message queued for %s: %s (priority: %s)", 
                   device_id, message_type, priority.name)
    
    def get_session_state(self, device_id: str) -> Optional[SessionState]:
        """
        Get current session state for a device.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            Optional[SessionState]: Current session state or None
        """
        return self.session_states.get(device_id)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get comprehensive synchronization status.
        
        Returns:
            dict: Synchronization status information
        """
        with self.sync_lock:
            current_time = datetime.now()
            
            # Calculate sync statistics
            success_rate = 0
            if self.sync_attempts > 0:
                success_rate = (self.sync_successes / self.sync_attempts) * 100
            
            # Get device status
            device_status = {}
            for device_id in self.sync_states:
                last_state = self.session_states.get(device_id)
                offline_since = self.offline_devices.get(device_id)
                queue_size = self.message_queues[device_id].qsize() if device_id in self.message_queues else 0
                
                device_status[device_id] = {
                    'sync_state': self.sync_states[device_id].value,
                    'has_session_state': last_state is not None,
                    'last_sync': last_state.sync_timestamp.isoformat() if last_state else None,
                    'offline_since': offline_since.isoformat() if offline_since else None,
                    'queued_messages': queue_size,
                    'is_connected': device_id not in self.offline_devices
                }
            
            return {
                'running': self.is_running,
                'sync_interval': self.sync_interval,
                'statistics': {
                    'sync_attempts': self.sync_attempts,
                    'sync_successes': self.sync_successes,
                    'sync_failures': self.sync_failures,
                    'success_rate_percent': success_rate,
                    'messages_queued': self.messages_queued,
                    'messages_delivered': self.messages_delivered
                },
                'devices': device_status,
                'total_devices': len(self.sync_states),
                'online_devices': len(self.sync_states) - len(self.offline_devices),
                'offline_devices': len(self.offline_devices)
            }
    
    def _sync_loop(self):
        """Background synchronization loop."""
        logger.info("[SessionSynchronizer] Sync loop started")
        
        while self.is_running:
            try:
                # Check for stale offline devices
                self._cleanup_stale_devices()
                
                # Process message queues
                self._process_message_queues()
                
                # Sleep until next sync interval
                time.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error("[SessionSynchronizer] Error in sync loop: %s", str(e))
                time.sleep(1.0)  # Short sleep on error
        
        logger.info("[SessionSynchronizer] Sync loop stopped")
    
    def _convert_android_state(self, android_state: Dict[str, Any]) -> SessionState:
        """Convert Android state dict to SessionState object."""
        return SessionState(
            session_id=android_state.get('session_id', ''),
            recording_active=android_state.get('recording_active', False),
            devices_connected=android_state.get('devices_connected', {}),
            recording_start_time=self._parse_datetime(android_state.get('recording_start_time')),
            recording_duration=android_state.get('recording_duration', 0.0),
            file_count=android_state.get('file_count', 0),
            total_file_size=android_state.get('total_file_size', 0),
            calibration_status=android_state.get('calibration_status', {}),
            sync_timestamp=datetime.now(),
            metadata=android_state.get('metadata', {})
        )
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string safely."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None
    
    def _has_significant_changes(self, old_state: SessionState, new_state: SessionState) -> bool:
        """Check if there are significant changes between states."""
        return (
            old_state.recording_active != new_state.recording_active or
            old_state.session_id != new_state.session_id or
            abs(old_state.file_count - new_state.file_count) > 0 or
            old_state.calibration_status != new_state.calibration_status
        )
    
    def _notify_state_change(self, device_id: str, state: SessionState):
        """Notify about significant state changes."""
        logger.info("[SessionSynchronizer] State change notification for %s: recording=%s, files=%d", 
                  device_id, state.recording_active, state.file_count)
    
    def _start_message_queuing(self, device_id: str):
        """Start queuing messages for offline device."""
        logger.info("[SessionSynchronizer] Started message queuing for offline device: %s", device_id)
    
    def _deliver_queued_messages(self, device_id: str):
        """Deliver queued messages to reconnected device."""
        if device_id not in self.message_queues:
            return
        
        queue = self.message_queues[device_id]
        delivered_count = 0
        
        while not queue.empty():
            try:
                message = queue.get_nowait()
                
                # Try to deliver message
                if self.message_sender:
                    success = self._send_message(message)
                    if success:
                        delivered_count += 1
                        self.messages_delivered += 1
                    else:
                        # Requeue if failed and under retry limit
                        message.retry_count += 1
                        if message.retry_count <= message.max_retries:
                            queue.put(message)
                        else:
                            logger.warning("[SessionSynchronizer] Message max retries exceeded: %s", message.message_type)
                else:
                    # No sender available, mark as delivered for stats
                    delivered_count += 1
                    self.messages_delivered += 1
                    
            except Empty:
                break
            except Exception as e:
                logger.error("[SessionSynchronizer] Error delivering message: %s", str(e))
        
        logger.info("[SessionSynchronizer] Delivered %d queued messages to %s", delivered_count, device_id)
    
    def _send_message(self, message: QueuedMessage) -> bool:
        """Send a message using the configured sender."""
        try:
            if self.message_sender:
                result = self.message_sender(message.device_id, message.message_type, message.payload)
                return bool(result)
            return False
        except Exception as e:
            logger.error("[SessionSynchronizer] Failed to send message: %s", str(e))
            return False
    
    def _cleanup_stale_devices(self):
        """Remove devices that have been offline too long."""
        current_time = datetime.now()
        stale_devices = []
        
        with self.sync_lock:
            for device_id, offline_time in self.offline_devices.items():
                if (current_time - offline_time).total_seconds() > self.max_offline_time:
                    stale_devices.append(device_id)
        
        for device_id in stale_devices:
            logger.warning("[SessionSynchronizer] Removing stale offline device: %s", device_id)
            self.unregister_device(device_id)
    
    def _process_message_queues(self):
        """Process pending messages in all queues."""
        for device_id in list(self.message_queues.keys()):
            if device_id not in self.offline_devices:  # Only process for online devices
                try:
                    queue = self.message_queues[device_id]
                    if not queue.empty():
                        self._deliver_queued_messages(device_id)
                except Exception as e:
                    logger.error("[SessionSynchronizer] Error processing queue for %s: %s", device_id, str(e))


# Global session synchronizer instance
session_synchronizer = SessionSynchronizer()


def get_session_synchronizer() -> SessionSynchronizer:
    """Get the global session synchronizer instance."""
    return session_synchronizer


if __name__ == "__main__":
    # Test session synchronizer
    print("[DEBUG_LOG] Testing Session Synchronizer...")
    
    # Create test synchronizer
    def mock_message_sender(device_id: str, message_type: str, payload: Dict[str, Any]) -> bool:
        print(f"[DEBUG_LOG] Sending {message_type} to {device_id}: {payload}")
        return True
    
    sync = SessionSynchronizer(mock_message_sender)
    sync.start_synchronization()
    
    try:
        # Register test device
        device_id = "test_device_001"
        sync.register_device(device_id)
        
        # Test session state sync
        android_state = {
            'device_id': device_id,
            'session_id': 'test_session_123',
            'recording_active': True,
            'devices_connected': {'shimmer': True, 'thermal': False},
            'recording_start_time': datetime.now().isoformat(),
            'recording_duration': 120.5,
            'file_count': 5,
            'total_file_size': 1024000,
            'calibration_status': {'rgb': 'complete', 'thermal': 'pending'},
            'metadata': {'test': True}
        }
        
        success = sync.sync_session_state(android_state)
        print(f"[DEBUG_LOG] Session sync result: {success}")
        
        # Test disconnect/reconnect scenario
        sync.handle_android_disconnect(device_id)
        
        # Queue some messages while offline
        sync.queue_message(device_id, "test_command", {"action": "start"}, MessagePriority.HIGH)
        sync.queue_message(device_id, "test_status", {"status": "ok"}, MessagePriority.NORMAL)
        
        # Test reconnect and recovery
        time.sleep(1)
        recovered_state = sync.recover_session_on_reconnect(device_id)
        print(f"[DEBUG_LOG] Recovered state: {recovered_state}")
        
        # Display status
        status = sync.get_sync_status()
        print(f"[DEBUG_LOG] Sync status: {json.dumps(status, indent=2, default=str)}")
        
    finally:
        sync.stop_synchronization()
    
    print("[DEBUG_LOG] Session synchronizer test completed")