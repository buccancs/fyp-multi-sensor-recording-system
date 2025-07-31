"""
Master Clock Synchronization Manager for Multi-Device Recording

This module implements a centralized synchronization system where the PC acts as the 
master clock for all connected devices including dual webcams, Android phone sensors 
(builtin camera, IR camera, shimmer), ensuring frame-level synchronization across 
all recording devices.

Features:
- PC master clock with high-precision timestamps
- NTP server integration for network time synchronization
- Android device clock synchronization
- Cross-device recording start/stop coordination
- Sync quality monitoring and validation
- Automatic drift correction

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import json
import logging
import ntplib
import socket
import threading
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Set
from concurrent.futures import ThreadPoolExecutor

# Import existing modules
from network.pc_server import PCServer, JsonMessage, StartRecordCommand, StopRecordCommand
from ntp_time_server import NTPTimeServer
from utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SyncStatus:
    """Synchronization status for a device"""
    device_id: str
    device_type: str  # 'android', 'webcam1', 'webcam2'
    is_synchronized: bool
    time_offset_ms: float
    last_sync_time: float
    sync_quality: float  # 0.0 to 1.0
    recording_active: bool
    frame_count: int


@dataclass
class SyncCommand:
    """Synchronization command for coordinated recording"""
    command_type: str  # 'start_record', 'stop_record', 'sync_timestamp'
    session_id: str
    master_timestamp: float
    target_devices: List[str]
    sync_tolerance_ms: float = 50.0  # Maximum allowed sync difference


@dataclass
class RecordingSession:
    """Information about an active recording session"""
    session_id: str
    start_timestamp: float
    devices: Set[str]
    webcam_files: Dict[str, str]  # webcam_id -> filepath
    android_files: Dict[str, List[str]]  # device_id -> list of files
    is_active: bool
    sync_quality: float


class MasterClockSynchronizer:
    """
    Master clock synchronization manager for multi-device recording.
    
    Coordinates synchronized recording across PC webcams and Android devices,
    ensuring all sensors record with synchronized timestamps from PC master clock.
    """
    
    def __init__(self, 
                 ntp_port: int = 8889,
                 pc_server_port: int = 9000,
                 sync_interval: float = 5.0,
                 logger_instance: Optional[logging.Logger] = None):
        """
        Initialize master clock synchronizer.
        
        Args:
            ntp_port: Port for NTP time server
            pc_server_port: Port for Android device communication
            sync_interval: Interval for synchronization checks (seconds)
            logger_instance: Optional logger instance
        """
        self.logger = logger_instance or logger
        self.sync_interval = sync_interval
        
        # Server components
        self.ntp_server = NTPTimeServer(logger=self.logger, port=ntp_port)
        self.pc_server = PCServer(port=pc_server_port, logger=self.logger)
        
        # Synchronization state
        self.connected_devices: Dict[str, SyncStatus] = {}
        self.active_sessions: Dict[str, RecordingSession] = {}
        self.master_start_time: Optional[float] = None
        
        # Threading
        self.is_running = False
        self.sync_thread: Optional[threading.Thread] = None
        self.thread_pool = ThreadPoolExecutor(max_workers=5)
        
        # Callbacks for external components
        self.webcam_sync_callbacks: List[Callable[[float], None]] = []
        self.session_callbacks: List[Callable[[str, RecordingSession], None]] = []
        self.sync_status_callbacks: List[Callable[[Dict[str, SyncStatus]], None]] = []
        
        # Configuration
        self.sync_tolerance_ms = 50.0  # Max allowed time difference
        self.quality_threshold = 0.8  # Minimum sync quality for recording
        
        # Setup server callbacks
        self.pc_server.add_device_callback(self._on_device_connected)
        self.pc_server.add_disconnect_callback(self._on_device_disconnected)
        self.pc_server.add_message_callback(self._on_message_received)
        
        self.logger.info("MasterClockSynchronizer initialized")

    def start(self) -> bool:
        """Start the master clock synchronization system."""
        try:
            self.logger.info("Starting master clock synchronization system...")
            
            # Start NTP server for time synchronization
            if not self.ntp_server.start():
                self.logger.error("Failed to start NTP server")
                return False
                
            # Start PC server for Android communication
            if not self.pc_server.start():
                self.logger.error("Failed to start PC server")
                self.ntp_server.stop()
                return False
            
            # Start synchronization monitoring
            self.is_running = True
            self.master_start_time = time.time()
            
            self.sync_thread = threading.Thread(target=self._sync_monitoring_loop, name="SyncMonitor")
            self.sync_thread.daemon = True
            self.sync_thread.start()
            
            self.logger.info("Master clock synchronization system started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start synchronization system: {e}")
            return False

    def stop(self):
        """Stop the master clock synchronization system."""
        try:
            self.logger.info("Stopping master clock synchronization system...")
            
            self.is_running = False
            
            # Stop active recording sessions
            for session_id in list(self.active_sessions.keys()):
                self.stop_synchronized_recording(session_id)
            
            # Stop servers
            self.pc_server.stop()
            self.ntp_server.stop()
            
            # Wait for sync thread
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5.0)
                
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            self.logger.info("Master clock synchronization system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping synchronization system: {e}")

    def get_master_timestamp(self) -> float:
        """Get current master timestamp."""
        return time.time()

    def start_synchronized_recording(self, 
                                   session_id: str, 
                                   target_devices: Optional[List[str]] = None,
                                   record_video: bool = True,
                                   record_thermal: bool = True,
                                   record_shimmer: bool = False) -> bool:
        """
        Start synchronized recording across all devices.
        
        Args:
            session_id: Unique session identifier
            target_devices: Specific devices to record from (None = all connected)
            record_video: Record video from Android cameras
            record_thermal: Record thermal camera data
            record_shimmer: Record shimmer sensor data
            
        Returns:
            bool: True if recording started successfully
        """
        try:
            if session_id in self.active_sessions:
                self.logger.error(f"Session {session_id} already active")
                return False
                
            # Determine target devices
            if target_devices is None:
                target_devices = list(self.connected_devices.keys())
                
            if not target_devices:
                self.logger.error("No target devices available for recording")
                return False
                
            # Check synchronization quality
            poor_sync_devices = []
            for device_id in target_devices:
                if device_id in self.connected_devices:
                    status = self.connected_devices[device_id]
                    if status.sync_quality < self.quality_threshold:
                        poor_sync_devices.append(device_id)
                        
            if poor_sync_devices:
                self.logger.warning(f"Devices with poor sync quality: {poor_sync_devices}")
                # Continue anyway, but log the warning
                
            # Get master timestamp for synchronized start
            master_timestamp = self.get_master_timestamp()
            
            # Create recording session
            session = RecordingSession(
                session_id=session_id,
                start_timestamp=master_timestamp,
                devices=set(target_devices),
                webcam_files={},
                android_files={},
                is_active=True,
                sync_quality=1.0
            )
            
            self.active_sessions[session_id] = session
            
            # Send start recording commands to Android devices
            android_devices = [d for d in target_devices 
                             if d in self.connected_devices and 
                             self.connected_devices[d].device_type == 'android']
            
            for device_id in android_devices:
                start_cmd = StartRecordCommand(
                    session_id=session_id,
                    record_video=record_video,
                    record_thermal=record_thermal,
                    record_shimmer=record_shimmer
                )
                start_cmd.timestamp = master_timestamp
                
                success = self.pc_server.send_message(device_id, start_cmd)
                if not success:
                    self.logger.error(f"Failed to send start command to {device_id}")
                else:
                    self.logger.info(f"Start recording command sent to {device_id}")
            
            # Notify webcam components via callbacks
            for callback in self.webcam_sync_callbacks:
                try:
                    callback(master_timestamp)
                except Exception as e:
                    self.logger.error(f"Error in webcam sync callback: {e}")
            
            # Notify session callbacks
            for callback in self.session_callbacks:
                try:
                    callback(session_id, session)
                except Exception as e:
                    self.logger.error(f"Error in session callback: {e}")
            
            self.logger.info(f"Synchronized recording started: session {session_id}, "
                           f"timestamp {master_timestamp}, devices: {target_devices}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting synchronized recording: {e}")
            return False

    def stop_synchronized_recording(self, session_id: str) -> bool:
        """
        Stop synchronized recording for a session.
        
        Args:
            session_id: Session to stop
            
        Returns:
            bool: True if recording stopped successfully
        """
        try:
            if session_id not in self.active_sessions:
                self.logger.error(f"Session {session_id} not found")
                return False
                
            session = self.active_sessions[session_id]
            if not session.is_active:
                self.logger.warning(f"Session {session_id} already stopped")
                return True
                
            # Get master timestamp for synchronized stop
            master_timestamp = self.get_master_timestamp()
            
            # Send stop recording commands to Android devices
            android_devices = [d for d in session.devices 
                             if d in self.connected_devices and 
                             self.connected_devices[d].device_type == 'android']
            
            for device_id in android_devices:
                stop_cmd = StopRecordCommand()
                stop_cmd.timestamp = master_timestamp
                
                success = self.pc_server.send_message(device_id, stop_cmd)
                if not success:
                    self.logger.error(f"Failed to send stop command to {device_id}")
                else:
                    self.logger.info(f"Stop recording command sent to {device_id}")
            
            # Mark session as inactive
            session.is_active = False
            
            # Calculate session duration
            duration = master_timestamp - session.start_timestamp
            
            self.logger.info(f"Synchronized recording stopped: session {session_id}, "
                           f"duration {duration:.1f}s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping synchronized recording: {e}")
            return False

    def add_webcam_sync_callback(self, callback: Callable[[float], None]):
        """Add callback for webcam synchronization events."""
        self.webcam_sync_callbacks.append(callback)

    def add_session_callback(self, callback: Callable[[str, RecordingSession], None]):
        """Add callback for recording session events."""
        self.session_callbacks.append(callback)

    def add_sync_status_callback(self, callback: Callable[[Dict[str, SyncStatus]], None]):
        """Add callback for synchronization status updates."""
        self.sync_status_callbacks.append(callback)

    def get_connected_devices(self) -> Dict[str, SyncStatus]:
        """Get current connected devices and their sync status."""
        return self.connected_devices.copy()

    def get_active_sessions(self) -> Dict[str, RecordingSession]:
        """Get current active recording sessions."""
        return self.active_sessions.copy()

    def _on_device_connected(self, device_id: str, device_info):
        """Handle Android device connection."""
        try:
            # Create sync status for new device
            sync_status = SyncStatus(
                device_id=device_id,
                device_type='android',
                is_synchronized=False,
                time_offset_ms=0.0,
                last_sync_time=time.time(),
                sync_quality=0.0,
                recording_active=False,
                frame_count=0
            )
            
            self.connected_devices[device_id] = sync_status
            
            # Start synchronization process for this device
            self._initiate_device_sync(device_id)
            
            self.logger.info(f"Android device connected: {device_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling device connection: {e}")

    def _on_device_disconnected(self, device_id: str):
        """Handle Android device disconnection."""
        try:
            if device_id in self.connected_devices:
                del self.connected_devices[device_id]
                
            # Remove device from active sessions
            for session in self.active_sessions.values():
                session.devices.discard(device_id)
                
            self.logger.info(f"Android device disconnected: {device_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling device disconnection: {e}")

    def _on_message_received(self, device_id: str, message: JsonMessage):
        """Handle messages from Android devices."""
        try:
            # Update device sync status based on message timestamp
            if device_id in self.connected_devices:
                device_status = self.connected_devices[device_id]
                current_time = time.time()
                
                # Calculate time offset
                time_offset_ms = (current_time - message.timestamp) * 1000
                device_status.time_offset_ms = time_offset_ms
                device_status.last_sync_time = current_time
                
                # Update sync quality based on time offset
                if abs(time_offset_ms) <= self.sync_tolerance_ms:
                    device_status.sync_quality = 1.0 - (abs(time_offset_ms) / self.sync_tolerance_ms)
                    device_status.is_synchronized = True
                else:
                    device_status.sync_quality = 0.0
                    device_status.is_synchronized = False
                    
                self.logger.debug(f"Device {device_id} sync update: offset {time_offset_ms:.1f}ms, "
                                f"quality {device_status.sync_quality:.2f}")
                
        except Exception as e:
            self.logger.error(f"Error processing message from {device_id}: {e}")

    def _initiate_device_sync(self, device_id: str):
        """Initiate synchronization process for a device."""
        try:
            # Send sync timestamp message
            sync_message = JsonMessage(type="sync_timestamp")
            sync_message.timestamp = self.get_master_timestamp()
            
            success = self.pc_server.send_message(device_id, sync_message)
            if success:
                self.logger.info(f"Sync initiated for device {device_id}")
            else:
                self.logger.error(f"Failed to initiate sync for device {device_id}")
                
        except Exception as e:
            self.logger.error(f"Error initiating device sync: {e}")

    def _sync_monitoring_loop(self):
        """Main synchronization monitoring loop."""
        while self.is_running:
            try:
                # Check device synchronization status
                for device_id, status in self.connected_devices.items():
                    current_time = time.time()
                    
                    # Check if device needs re-sync
                    if (current_time - status.last_sync_time) > self.sync_interval * 2:
                        self.logger.warning(f"Device {device_id} sync timeout, re-initiating")
                        self._initiate_device_sync(device_id)
                
                # Update overall sync quality for active sessions
                for session in self.active_sessions.values():
                    if session.is_active:
                        session_sync_qualities = []
                        for device_id in session.devices:
                            if device_id in self.connected_devices:
                                session_sync_qualities.append(
                                    self.connected_devices[device_id].sync_quality
                                )
                        
                        if session_sync_qualities:
                            session.sync_quality = sum(session_sync_qualities) / len(session_sync_qualities)
                        else:
                            session.sync_quality = 0.0
                
                # Notify sync status callbacks
                for callback in self.sync_status_callbacks:
                    try:
                        callback(self.connected_devices)
                    except Exception as e:
                        self.logger.error(f"Error in sync status callback: {e}")
                
                time.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in sync monitoring loop: {e}")
                time.sleep(1.0)


# Singleton instance for global access
_master_synchronizer: Optional[MasterClockSynchronizer] = None


def get_master_synchronizer() -> MasterClockSynchronizer:
    """Get the global master synchronizer instance."""
    global _master_synchronizer
    if _master_synchronizer is None:
        _master_synchronizer = MasterClockSynchronizer()
    return _master_synchronizer


def initialize_master_synchronizer(ntp_port: int = 8889, 
                                 pc_server_port: int = 9000) -> bool:
    """Initialize and start the global master synchronizer."""
    global _master_synchronizer
    try:
        _master_synchronizer = MasterClockSynchronizer(
            ntp_port=ntp_port,
            pc_server_port=pc_server_port
        )
        return _master_synchronizer.start()
    except Exception as e:
        logger.error(f"Failed to initialize master synchronizer: {e}")
        return False


def shutdown_master_synchronizer():
    """Shutdown the global master synchronizer."""
    global _master_synchronizer
    if _master_synchronizer:
        _master_synchronizer.stop()
        _master_synchronizer = None


if __name__ == "__main__":
    # Test the synchronization system
    logging.basicConfig(level=logging.INFO)
    
    sync_manager = MasterClockSynchronizer()
    
    try:
        if sync_manager.start():
            logger.info("Synchronization system started successfully")
            
            # Keep running for testing
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        sync_manager.stop()