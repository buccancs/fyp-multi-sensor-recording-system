"""
Session Management Module
=========================

Manages recording sessions with coordinated start/stop across devices.
Handles session metadata, file organization, and status tracking.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    """Configuration for a recording session."""
    session_name: str
    output_directory: str
    duration_seconds: int = -1  # -1 for unlimited
    auto_start_all_devices: bool = True
    create_subdirectories: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SessionInfo:
    """Information about a recording session."""
    session_id: str
    config: SessionConfig
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "created"  # created, recording, stopped, error
    participating_devices: List[str] = None
    output_files: Dict[str, List[str]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.participating_devices is None:
            self.participating_devices = []
        if self.output_files is None:
            self.output_files = {}
    
    def to_dict(self) -> dict:
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


class SessionManager:
    """Manages recording sessions and device coordination."""
    
    def __init__(self, base_output_dir: str = "recordings"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        self.active_session: Optional[SessionInfo] = None
        self.session_history: List[SessionInfo] = []
        self.network_server = None
        
        # Load session history
        self._load_session_history()
    
    def set_network_server(self, server):
        """Set the network server for device communication."""
        self.network_server = server
    
    def create_session(self, config: SessionConfig) -> SessionInfo:
        """Create a new recording session."""
        if self.active_session and self.active_session.status == "recording":
            raise RuntimeError("Cannot create session while another is recording")
        
        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}_{config.session_name}"
        
        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            config=config
        )
        
        # Create output directory
        if config.create_subdirectories:
            session_dir = self.base_output_dir / session_id
            session_dir.mkdir(exist_ok=True)
            # Update config with actual directory
            config.output_directory = str(session_dir)
        
        self.active_session = session_info
        logger.info(f"Created session: {session_id}")
        
        return session_info
    
    def start_recording(self) -> bool:
        """Start recording for the active session."""
        if not self.active_session:
            raise RuntimeError("No active session")
        
        if self.active_session.status == "recording":
            raise RuntimeError("Session is already recording")
        
        if not self.network_server:
            raise RuntimeError("Network server not configured")
        
        try:
            # Get connected devices
            connected_devices = self.network_server.get_connected_devices()
            if not connected_devices:
                raise RuntimeError("No devices connected")
            
            # Send start recording command to all devices
            session_data = {
                'session_id': self.active_session.session_id,
                'output_directory': self.active_session.config.output_directory,
                'session_config': self.active_session.config.to_dict()
            }
            
            successful_devices = self.network_server.broadcast_command(
                'start_recording', 
                session_data
            )
            
            if not successful_devices:
                raise RuntimeError("Failed to start recording on any device")
            
            # Update session info
            self.active_session.start_time = datetime.now()
            self.active_session.status = "recording"
            self.active_session.participating_devices = successful_devices
            
            logger.info(f"Started recording session {self.active_session.session_id} "
                       f"on devices: {successful_devices}")
            
            # Save session metadata
            self._save_session_metadata()
            
            return True
            
        except Exception as e:
            self.active_session.status = "error"
            self.active_session.error_message = str(e)
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Stop recording for the active session."""
        if not self.active_session:
            raise RuntimeError("No active session")
        
        if self.active_session.status != "recording":
            raise RuntimeError("Session is not recording")
        
        if not self.network_server:
            raise RuntimeError("Network server not configured")
        
        try:
            # Send stop recording command to all devices
            successful_devices = self.network_server.broadcast_command('stop_recording')
            
            # Update session info
            self.active_session.end_time = datetime.now()
            self.active_session.status = "stopped"
            
            logger.info(f"Stopped recording session {self.active_session.session_id}")
            
            # Save final session metadata
            self._save_session_metadata()
            
            # Add to history
            self.session_history.append(self.active_session)
            self._save_session_history()
            
            # Clear active session
            self.active_session = None
            
            return True
            
        except Exception as e:
            if self.active_session:
                self.active_session.status = "error"
                self.active_session.error_message = str(e)
            logger.error(f"Failed to stop recording: {e}")
            return False
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.active_session:
            return {
                'has_active_session': False,
                'session_info': None
            }
        
        # Calculate duration if recording
        duration_seconds = None
        if self.active_session.start_time:
            end_time = self.active_session.end_time or datetime.now()
            duration_seconds = (end_time - self.active_session.start_time).total_seconds()
        
        return {
            'has_active_session': True,
            'session_info': self.active_session.to_dict(),
            'duration_seconds': duration_seconds,
            'connected_devices': (
                list(self.network_server.get_connected_devices().keys()) 
                if self.network_server else []
            )
        }
    
    def get_session_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get session history."""
        return [session.to_dict() for session in self.session_history[-limit:]]
    
    def _save_session_metadata(self):
        """Save session metadata to file."""
        if not self.active_session:
            return
        
        metadata_file = Path(self.active_session.config.output_directory) / "session_metadata.json"
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(self.active_session.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session metadata: {e}")
    
    def _save_session_history(self):
        """Save session history to file."""
        history_file = self.base_output_dir / "session_history.json"
        
        try:
            history_data = [session.to_dict() for session in self.session_history]
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session history: {e}")
    
    def _load_session_history(self):
        """Load session history from file."""
        history_file = self.base_output_dir / "session_history.json"
        
        if not history_file.exists():
            return
        
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
            
            self.session_history = []
            for session_data in history_data:
                # Convert ISO strings back to datetime objects
                if session_data.get('start_time'):
                    session_data['start_time'] = datetime.fromisoformat(session_data['start_time'])
                if session_data.get('end_time'):
                    session_data['end_time'] = datetime.fromisoformat(session_data['end_time'])
                
                # Reconstruct config object
                config_data = session_data['config']
                config = SessionConfig(**config_data)
                session_data['config'] = config
                
                session_info = SessionInfo(**session_data)
                self.session_history.append(session_info)
                
            logger.info(f"Loaded {len(self.session_history)} sessions from history")
            
        except Exception as e:
            logger.error(f"Failed to load session history: {e}")
            self.session_history = []