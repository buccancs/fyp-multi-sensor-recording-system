"""
Session Management Module for Multi-Sensor Recording System Controller

This module implements the SessionManager class for Milestone 3.3: Webcam Capture Integration.
It provides session folder creation, organization, and lifecycle management for coordinated
recording across multiple devices including PC webcam.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.3 - Webcam Capture Integration (PC Recording)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Import centralized logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class SessionManager:
    """
    Session manager for coordinating multi-device recording sessions.

    This class handles:
    - Session folder creation and organization
    - Session metadata management
    - Recording lifecycle coordination
    - File organization and naming
    """

    def __init__(self, base_recordings_dir: str = "recordings"):
        self.logger = get_logger(__name__)
        self.logger.info(f"for initialized")
        """
        Initialize session manager.

        Args:
            base_recordings_dir (str): Base directory for all recordings
        """
        self.base_recordings_dir = Path(base_recordings_dir)
        self.current_session: Optional[Dict] = None
        self.session_history: List[Dict] = []

        # Ensure base directory exists
        self.base_recordings_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"SessionManager initialized with base directory: {self.base_recordings_dir}")

    def create_session(self, session_name: Optional[str] = None) -> Dict:
        """
        Create a new recording session.

        Args:
            session_name (str, optional): Custom session name. If None, generates timestamp-based name.

        Returns:
            Dict: Session information including session_id, folder_path, start_time
        """
        logger.info(f"Creating new session with name: {session_name}")
        
        # Generate session ID and name
        timestamp = datetime.now()
        if session_name is None:
            session_id = timestamp.strftime("session_%Y%m%d_%H%M%S")
        else:
            # Sanitize custom name for filesystem
            safe_name = "".join(
                c for c in session_name if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            session_id = f"{safe_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Create session folder
        session_folder = self.base_recordings_dir / session_id
        session_folder.mkdir(parents=True, exist_ok=True)

        # Create session metadata
        session_info = {
            "session_id": session_id,
            "session_name": session_name or session_id,
            "folder_path": str(session_folder),
            "start_time": timestamp.isoformat(),
            "end_time": None,
            "duration": None,
            "devices": {},
            "files": {},
            "status": "active",
        }

        # Save session metadata
        metadata_file = session_folder / "session_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(session_info, f, indent=2)

        self.current_session = session_info

        print(f"[DEBUG_LOG] Session created: {session_id} at {session_folder}")
        return session_info

    def end_session(self) -> Optional[Dict]:
        """
        End the current recording session.

        Returns:
            Dict: Final session information, or None if no active session
        """
        if not self.current_session:
            print("[DEBUG_LOG] No active session to end")
            return None

        # Update session end time and duration
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        duration = (end_time - start_time).total_seconds()

        self.current_session["end_time"] = end_time.isoformat()
        self.current_session["duration"] = duration
        self.current_session["status"] = "completed"

        # Save updated metadata
        metadata_file = (
            Path(self.current_session["folder_path"]) / "session_metadata.json"
        )
        with open(metadata_file, "w") as f:
            json.dump(self.current_session, f, indent=2)

        # Add to session history
        self.session_history.append(self.current_session.copy())

        session_id = self.current_session["session_id"]
        print(f"[DEBUG_LOG] Session ended: {session_id} (duration: {duration:.1f}s)")

        completed_session = self.current_session
        self.current_session = None

        return completed_session

    def add_device_to_session(
        self, device_id: str, device_type: str, capabilities: List[str]
    ):
        """
        Add a device to the current session.

        Args:
            device_id (str): Unique device identifier
            device_type (str): Type of device (e.g., "android_phone", "pc_webcam")
            capabilities (List[str]): List of device capabilities
        """
        if not self.current_session:
            print("[DEBUG_LOG] No active session to add device to")
            return

        device_info = {
            "device_type": device_type,
            "capabilities": capabilities,
            "added_time": datetime.now().isoformat(),
            "status": "connected",
        }

        self.current_session["devices"][device_id] = device_info
        self._update_session_metadata()

        print(f"[DEBUG_LOG] Device added to session: {device_id} ({device_type})")

    def add_file_to_session(
        self,
        device_id: str,
        file_type: str,
        file_path: str,
        file_size: Optional[int] = None,
    ):
        """
        Add a recorded file to the current session.

        Args:
            device_id (str): Device that created the file
            file_type (str): Type of file (e.g., "webcam_video", "rgb_video", "thermal_video")
            file_path (str): Path to the recorded file
            file_size (int, optional): File size in bytes
        """
        if not self.current_session:
            print("[DEBUG_LOG] No active session to add file to")
            return

        if device_id not in self.current_session["files"]:
            self.current_session["files"][device_id] = []

        file_info = {
            "file_type": file_type,
            "file_path": file_path,
            "file_size": file_size,
            "created_time": datetime.now().isoformat(),
        }

        self.current_session["files"][device_id].append(file_info)
        self._update_session_metadata()

        print(
            f"[DEBUG_LOG] File added to session: {device_id} - {file_type} ({file_path})"
        )

    def get_session_folder(self, session_id: Optional[str] = None) -> Optional[Path]:
        """
        Get the folder path for a session.

        Args:
            session_id (str, optional): Session ID. If None, uses current session.

        Returns:
            Path: Session folder path, or None if session not found
        """
        if session_id is None:
            if self.current_session:
                return Path(self.current_session["folder_path"])
            else:
                return None

        # Search in session history
        for session in self.session_history:
            if session["session_id"] == session_id:
                return Path(session["folder_path"])

        # Check if it's the current session
        if self.current_session and self.current_session["session_id"] == session_id:
            return Path(self.current_session["folder_path"])

        return None

    def get_current_session(self) -> Optional[Dict]:
        """
        Get current active session information.

        Returns:
            Dict: Current session info, or None if no active session
        """
        return self.current_session.copy() if self.current_session else None

    def _update_session_metadata(self):
        """Update session metadata file with current session information."""
        if not self.current_session:
            return

        metadata_file = (
            Path(self.current_session["folder_path"]) / "session_metadata.json"
        )
        try:
            with open(metadata_file, "w") as f:
                json.dump(self.current_session, f, indent=2)
        except Exception as e:
            print(f"[DEBUG_LOG] Failed to update session metadata: {e}")


if __name__ == "__main__":
    # Test session manager functionality
    print("[DEBUG_LOG] Testing SessionManager...")

    manager = SessionManager("test_recordings")

    # Create a test session
    session = manager.create_session("test_session")
    print(f"Created session: {session['session_id']}")

    # Add devices
    manager.add_device_to_session("pc_webcam", "pc_webcam", ["video_recording"])
    manager.add_device_to_session(
        "phone_1", "android_phone", ["rgb_video", "thermal_video"]
    )

    # Add files
    manager.add_file_to_session("pc_webcam", "webcam_video", "webcam_test.mp4", 1024000)
    manager.add_file_to_session("phone_1", "rgb_video", "phone1_rgb.mp4", 2048000)

    # End session
    completed = manager.end_session()
    print(
        f"Completed session: {completed['session_id']} (duration: {completed['duration']:.1f}s)"
    )

    print("[DEBUG_LOG] SessionManager test completed successfully")
