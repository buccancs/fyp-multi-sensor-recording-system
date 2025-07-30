"""
Session Logger Module for Multi-Sensor Recording System Controller

This module implements the SessionLogger class for Milestone 3.8: Session Metadata Logging and Review.
It provides comprehensive event logging with structured JSON format, capturing all key events,
timestamps, and relevant details for both live feedback and post-session analysis.

The SessionLogger creates a detailed diary of each session including device connections,
recording start/stop times, stimulus events, user markers, errors, and file transfers.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
Milestone: 3.8 - Session Metadata Logging and Review
"""

import os
import json
import threading
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal


class SessionLogger(QObject):
    """
    Comprehensive session logger for multi-device recording sessions.
    
    This class handles:
    - Structured JSON event logging with timestamps
    - Real-time event capture and disk flushing
    - UI update signals for live feedback
    - Session lifecycle management
    - Thread-safe logging operations
    """
    
    # Qt signals for UI updates
    log_entry_added = pyqtSignal(str)  # Human-readable log message for UI
    session_started = pyqtSignal(str)  # Session ID
    session_ended = pyqtSignal(str, float)  # Session ID, duration
    error_logged = pyqtSignal(str, str)  # Error type, message
    
    def __init__(self, base_sessions_dir: str = "recordings"):
        """
        Initialize session logger.
        
        Args:
            base_sessions_dir (str): Base directory for all session recordings
        """
        super().__init__()
        self.base_sessions_dir = Path(base_sessions_dir)
        self.current_session: Optional[Dict] = None
        self.log_file_path: Optional[Path] = None
        self.events: List[Dict] = []
        self.session_start_time: Optional[datetime] = None
        self.lock = threading.Lock()  # Thread safety for logging operations
        
        # Ensure base directory exists
        self.base_sessions_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[DEBUG_LOG] SessionLogger initialized with base directory: {self.base_sessions_dir}")
    
    def start_session(self, session_name: Optional[str] = None, devices: Optional[List[Dict]] = None) -> Dict:
        """
        Start a new session and initialize logging.
        
        Args:
            session_name (str, optional): Custom session name
            devices (List[Dict], optional): List of connected devices with metadata
            
        Returns:
            Dict: Session information including session_id, start_time, log_file_path
        """
        with self.lock:
            if self.current_session:
                print("[DEBUG_LOG] Warning: Starting new session while another is active. Ending previous session.")
                self.end_session()
            
            # Generate session ID and timestamp
            self.session_start_time = datetime.now()
            timestamp_str = self.session_start_time.strftime("%Y%m%d_%H%M%S")
            
            if session_name:
                # Sanitize custom name for filesystem
                safe_name = "".join(c for c in session_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                session_id = f"{safe_name}_{timestamp_str}"
            else:
                session_id = f"session_{timestamp_str}"
            
            # Create session folder
            session_folder = self.base_sessions_dir / session_id
            session_folder.mkdir(parents=True, exist_ok=True)
            
            # Initialize session structure
            self.current_session = {
                "session": session_id,
                "session_name": session_name or session_id,
                "start_time": self.session_start_time.isoformat(),
                "end_time": None,
                "duration": None,
                "devices": devices or [],
                "events": [],
                "calibration_files": [],
                "status": "active"
            }
            
            # Set up log file
            self.log_file_path = session_folder / f"{session_id}_log.json"
            self.events = []
            
            # Log session start event
            self.log_event("session_start", {
                "session_id": session_id,
                "devices": [d.get("id", "unknown") for d in (devices or [])]
            })
            
            # Write initial session structure to disk
            self._flush_to_disk()
            
            # Emit UI signal
            ui_message = f"Session {session_id} started. Devices: {', '.join([d.get('id', 'unknown') for d in (devices or [])])}"
            self.log_entry_added.emit(ui_message)
            self.session_started.emit(session_id)
            
            print(f"[DEBUG_LOG] Session started: {session_id} at {session_folder}")
            
            return {
                "session_id": session_id,
                "start_time": self.session_start_time.isoformat(),
                "log_file_path": str(self.log_file_path),
                "session_folder": str(session_folder)
            }
    
    def log_event(self, event_type: str, details: Optional[Dict] = None) -> None:
        """
        Log an event with timestamp and details.
        
        Args:
            event_type (str): Type of event (e.g., 'start_record', 'device_ack', 'marker', etc.)
            details (Dict, optional): Additional event-specific details
        """
        if not self.current_session:
            print(f"[DEBUG_LOG] Warning: Attempted to log event '{event_type}' with no active session")
            return
        
        with self.lock:
            # Create event entry
            event_time = datetime.now()
            event_entry = {
                "event": event_type,
                "time": event_time.strftime("%H:%M:%S.%f")[:-3],  # HH:MM:SS.mmm format
                "timestamp": event_time.isoformat(),  # Full ISO timestamp
            }
            
            # Add details if provided
            if details:
                event_entry.update(details)
            
            # Add to events list
            self.events.append(event_entry)
            self.current_session["events"] = self.events
            
            # Flush to disk immediately for robustness
            self._flush_to_disk()
            
            # Generate human-readable message for UI
            ui_message = self._format_event_for_ui(event_entry)
            self.log_entry_added.emit(ui_message)
            
            # Special handling for error events
            if event_type == "error":
                error_type = details.get("error_type", "unknown") if details else "unknown"
                error_message = details.get("message", "No details") if details else "No details"
                self.error_logged.emit(error_type, error_message)
            
            print(f"[DEBUG_LOG] Event logged: {event_type} - {ui_message}")
    
    def log_device_connected(self, device_id: str, device_type: str = "unknown", capabilities: Optional[List[str]] = None) -> None:
        """Log device connection event."""
        self.log_event("device_connected", {
            "device": device_id,
            "device_type": device_type,
            "capabilities": capabilities or []
        })
    
    def log_device_disconnected(self, device_id: str, reason: str = "unknown") -> None:
        """Log device disconnection event."""
        self.log_event("device_disconnected", {
            "device": device_id,
            "reason": reason
        })
    
    def log_recording_start(self, devices: List[str], session_id: Optional[str] = None) -> None:
        """Log recording start command."""
        self.log_event("start_record", {
            "devices": devices,
            "session": session_id or (self.current_session.get("session") if self.current_session else None)
        })
    
    def log_recording_stop(self) -> None:
        """Log recording stop command."""
        self.log_event("stop_record")
    
    def log_device_ack(self, device_id: str, command: str = "start_record") -> None:
        """Log device acknowledgment."""
        self.log_event("device_ack", {
            "device": device_id,
            "command": command
        })
    
    def log_stimulus_play(self, media_name: str, media_path: Optional[str] = None) -> None:
        """Log stimulus playback start."""
        details = {"media": media_name}
        if media_path:
            details["media_path"] = media_path
        self.log_event("stimulus_play", details)
    
    def log_stimulus_stop(self, media_name: str) -> None:
        """Log stimulus playback stop."""
        self.log_event("stimulus_stop", {"media": media_name})
    
    def log_marker(self, label: str, stim_time: Optional[str] = None) -> None:
        """Log user marker event."""
        details = {"label": label}
        if stim_time:
            details["stim_time"] = stim_time
        self.log_event("marker", details)
    
    def log_file_received(self, device_id: str, filename: str, file_size: Optional[int] = None, file_type: str = "unknown") -> None:
        """Log file reception from device."""
        details = {
            "device": device_id,
            "filename": filename,
            "file_type": file_type
        }
        if file_size is not None:
            details["size"] = file_size
        self.log_event("file_received", details)
    
    def log_calibration_capture(self, device_id: str, filename: str) -> None:
        """Log calibration image capture."""
        self.log_event("calibration_capture", {
            "device": device_id,
            "file": filename
        })
        
        # Add to calibration files list
        if self.current_session and filename not in self.current_session["calibration_files"]:
            self.current_session["calibration_files"].append(filename)
    
    def log_calibration_completed(self, result_file: Optional[str] = None) -> None:
        """Log calibration completion."""
        details = {}
        if result_file:
            details["result_file"] = result_file
        self.log_event("calibration_done", details)
    
    def log_error(self, error_type: str, message: str, device_id: Optional[str] = None) -> None:
        """Log error event."""
        details = {
            "error_type": error_type,
            "message": message
        }
        if device_id:
            details["device"] = device_id
        self.log_event("error", details)
    
    def end_session(self) -> Optional[Dict]:
        """
        End the current session and finalize logging.
        
        Returns:
            Dict: Final session information, or None if no active session
        """
        if not self.current_session:
            print("[DEBUG_LOG] No active session to end")
            return None
        
        with self.lock:
            # Calculate session duration
            end_time = datetime.now()
            duration = (end_time - self.session_start_time).total_seconds()
            
            # Log session end event
            self.log_event("session_end")
            
            # Update session metadata
            self.current_session["end_time"] = end_time.isoformat()
            self.current_session["duration"] = duration
            self.current_session["status"] = "completed"
            
            # Final flush to disk
            self._flush_to_disk()
            
            session_id = self.current_session["session"]
            completed_session = self.current_session.copy()
            
            # Emit UI signals
            ui_message = f"Session {session_id} completed. Duration: {duration:.1f}s. Log saved to {self.log_file_path}"
            self.log_entry_added.emit(ui_message)
            self.session_ended.emit(session_id, duration)
            
            # Reset state
            self.current_session = None
            self.log_file_path = None
            self.events = []
            self.session_start_time = None
            
            print(f"[DEBUG_LOG] Session ended: {session_id} (duration: {duration:.1f}s)")
            
            return completed_session
    
    def get_current_session(self) -> Optional[Dict]:
        """Get current session information."""
        return self.current_session.copy() if self.current_session else None
    
    def is_session_active(self) -> bool:
        """Check if a session is currently active."""
        return self.current_session is not None
    
    def _flush_to_disk(self) -> None:
        """Write current session data to disk (thread-safe)."""
        if not self.current_session or not self.log_file_path:
            return
        
        try:
            # Write complete JSON structure
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
                f.flush()  # Force write to disk
                os.fsync(f.fileno())  # Ensure OS writes to disk
        except Exception as e:
            print(f"[DEBUG_LOG] Error writing session log to disk: {e}")
    
    def _format_event_for_ui(self, event_entry: Dict) -> str:
        """Format event entry for human-readable UI display."""
        event_type = event_entry.get("event", "unknown")
        time_str = event_entry.get("time", "unknown")
        
        if event_type == "session_start":
            devices = event_entry.get("devices", [])
            return f"{time_str} - Session started. Devices: {', '.join(devices) if devices else 'None'}"
        
        elif event_type == "device_connected":
            device = event_entry.get("device", "unknown")
            device_type = event_entry.get("device_type", "unknown")
            return f"{time_str} - Device connected: {device} ({device_type})"
        
        elif event_type == "device_disconnected":
            device = event_entry.get("device", "unknown")
            reason = event_entry.get("reason", "unknown")
            return f"{time_str} - Device disconnected: {device} (reason: {reason})"
        
        elif event_type == "start_record":
            devices = event_entry.get("devices", [])
            return f"{time_str} - Recording started on devices: {', '.join(devices) if devices else 'None'}"
        
        elif event_type == "stop_record":
            return f"{time_str} - Recording stopped"
        
        elif event_type == "device_ack":
            device = event_entry.get("device", "unknown")
            command = event_entry.get("command", "unknown")
            return f"{time_str} - {device} acknowledged {command}"
        
        elif event_type == "stimulus_play":
            media = event_entry.get("media", "unknown")
            return f"{time_str} - Stimulus started: {media}"
        
        elif event_type == "stimulus_stop":
            media = event_entry.get("media", "unknown")
            return f"{time_str} - Stimulus stopped: {media}"
        
        elif event_type == "marker":
            label = event_entry.get("label", "unknown")
            stim_time = event_entry.get("stim_time")
            if stim_time:
                return f"{time_str} - Marker '{label}' inserted (stimulus time: {stim_time})"
            else:
                return f"{time_str} - Marker '{label}' inserted"
        
        elif event_type == "file_received":
            device = event_entry.get("device", "unknown")
            filename = event_entry.get("filename", "unknown")
            size = event_entry.get("size")
            if size:
                size_mb = size / (1024 * 1024)
                return f"{time_str} - File received from {device}: {filename} ({size_mb:.1f} MB)"
            else:
                return f"{time_str} - File received from {device}: {filename}"
        
        elif event_type == "calibration_capture":
            device = event_entry.get("device", "unknown")
            filename = event_entry.get("file", "unknown")
            return f"{time_str} - Calibration image captured from {device}: {filename}"
        
        elif event_type == "calibration_done":
            result_file = event_entry.get("result_file")
            if result_file:
                return f"{time_str} - Calibration completed. Results saved to: {result_file}"
            else:
                return f"{time_str} - Calibration completed"
        
        elif event_type == "error":
            error_type = event_entry.get("error_type", "unknown")
            message = event_entry.get("message", "No details")
            device = event_entry.get("device")
            if device:
                return f"{time_str} - ERROR ({error_type}): {message} [Device: {device}]"
            else:
                return f"{time_str} - ERROR ({error_type}): {message}"
        
        elif event_type == "session_end":
            return f"{time_str} - Session ended"
        
        else:
            # Generic formatting for unknown event types
            return f"{time_str} - {event_type}: {str(event_entry)}"


# Global session logger instance
_session_logger_instance: Optional[SessionLogger] = None


def get_session_logger() -> SessionLogger:
    """
    Get the global session logger instance.
    Creates one if it doesn't exist.
    
    Returns:
        SessionLogger: Global session logger instance
    """
    global _session_logger_instance
    if _session_logger_instance is None:
        _session_logger_instance = SessionLogger()
    return _session_logger_instance


def reset_session_logger() -> None:
    """Reset the global session logger instance (useful for testing)."""
    global _session_logger_instance
    if _session_logger_instance and _session_logger_instance.is_session_active():
        _session_logger_instance.end_session()
    _session_logger_instance = None
