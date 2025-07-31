"""
Session Recovery Module for Multi-Sensor Recording System Controller

This module implements advanced error recovery capabilities for Milestone 3.8: Session Metadata Logging and Review.
It provides automatic session recovery, corrupted file detection and repair, disk space monitoring,
and backup logging capabilities.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
Milestone: 3.8 - Session Metadata Logging and Review (Advanced Error Recovery)
"""

import json
import psutil
import shutil
import threading
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List


class SessionRecoveryManager(QObject):
    """
    Advanced session recovery and error handling manager.

    This class provides:
    - Automatic session recovery after crashes
    - Corrupted file detection and repair
    - Disk space monitoring with cleanup
    - Backup logging to secondary locations
    - System health monitoring
    """

    # Qt signals for monitoring alerts
    disk_space_warning = pyqtSignal(str, float)  # Path, available GB
    disk_space_critical = pyqtSignal(str, float)  # Path, available GB
    session_recovered = pyqtSignal(str, str)  # Session ID, recovery details
    file_corruption_detected = pyqtSignal(str, str)  # File path, error details
    backup_completed = pyqtSignal(str, str)  # Session ID, backup path
    system_health_alert = pyqtSignal(str, str)  # Alert type, message

    def __init__(
        self, base_sessions_dir: str = "recordings", backup_dir: Optional[str] = None
    ):
        """
        Initialize session recovery manager.

        Args:
            base_sessions_dir (str): Base directory for session recordings
            backup_dir (str, optional): Secondary backup directory
        """
        super().__init__()
        self.base_sessions_dir = Path(base_sessions_dir)
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.recovery_log_file = self.base_sessions_dir / "recovery.log"

        # Recovery settings
        self.disk_warning_threshold_gb = 5.0  # Warn when less than 5GB free
        self.disk_critical_threshold_gb = 1.0  # Critical when less than 1GB free
        self.max_session_age_days = 30  # Auto-cleanup sessions older than 30 days
        self.backup_enabled = self.backup_dir is not None

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()

        # Initialize recovery system
        self.init_recovery_system()

        print(f"[DEBUG_LOG] SessionRecoveryManager initialized")
        print(f"[DEBUG_LOG] Base directory: {self.base_sessions_dir}")
        print(f"[DEBUG_LOG] Backup directory: {self.backup_dir}")
        print(f"[DEBUG_LOG] Backup enabled: {self.backup_enabled}")

    def init_recovery_system(self):
        """Initialize the recovery system and create necessary directories."""
        try:
            # Ensure directories exist
            self.base_sessions_dir.mkdir(parents=True, exist_ok=True)
            if self.backup_dir:
                self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Create recovery log if it doesn't exist
            if not self.recovery_log_file.exists():
                self.log_recovery_event("system_init", "Recovery system initialized")

            print("[DEBUG_LOG] Recovery system initialized successfully")

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to initialize recovery system: {e}")

    def start_monitoring(self):
        """Start background monitoring for disk space and system health."""
        if self.monitoring_active:
            print("[DEBUG_LOG] Monitoring already active")
            return

        self.monitoring_active = True
        self.stop_monitoring.clear()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        self.log_recovery_event("monitoring_start", "Background monitoring started")
        print("[DEBUG_LOG] Background monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False
        self.stop_monitoring.set()

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)

        self.log_recovery_event("monitoring_stop", "Background monitoring stopped")
        print("[DEBUG_LOG] Background monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop for system health checks."""
        while not self.stop_monitoring.is_set():
            try:
                # Check disk space
                self.check_disk_space()

                # Check for corrupted files
                self.scan_for_corrupted_files()

                # Perform automatic cleanup if needed
                self.auto_cleanup_old_sessions()

                # Wait before next check (every 60 seconds)
                if self.stop_monitoring.wait(60):
                    break

            except Exception as e:
                self.log_recovery_event(
                    "monitoring_error", f"Monitoring error: {str(e)}"
                )
                print(f"[DEBUG_LOG] Monitoring error: {e}")

    def check_disk_space(self):
        """Check available disk space and emit warnings if low."""
        try:
            # Check main sessions directory
            usage = psutil.disk_usage(str(self.base_sessions_dir))
            available_gb = usage.free / (1024**3)

            if available_gb < self.disk_critical_threshold_gb:
                self.disk_space_critical.emit(str(self.base_sessions_dir), available_gb)
                self.log_recovery_event(
                    "disk_critical",
                    f"Critical disk space: {available_gb:.1f}GB available",
                )
            elif available_gb < self.disk_warning_threshold_gb:
                self.disk_space_warning.emit(str(self.base_sessions_dir), available_gb)
                self.log_recovery_event(
                    "disk_warning", f"Low disk space: {available_gb:.1f}GB available"
                )

            # Check backup directory if enabled
            if self.backup_dir and self.backup_dir.exists():
                backup_usage = psutil.disk_usage(str(self.backup_dir))
                backup_available_gb = backup_usage.free / (1024**3)

                if backup_available_gb < self.disk_critical_threshold_gb:
                    self.system_health_alert.emit(
                        "backup_disk_critical",
                        f"Backup disk critical: {backup_available_gb:.1f}GB",
                    )

        except Exception as e:
            self.log_recovery_event(
                "disk_check_error", f"Disk space check failed: {str(e)}"
            )

    def scan_for_corrupted_files(self):
        """Scan for corrupted JSON log files and attempt repair."""
        try:
            for session_folder in self.base_sessions_dir.iterdir():
                if not session_folder.is_dir():
                    continue

                # Check JSON log files
                for json_file in session_folder.glob("*.json"):
                    if self.is_file_corrupted(json_file):
                        self.file_corruption_detected.emit(
                            str(json_file), "JSON corruption detected"
                        )
                        self.attempt_file_repair(json_file)

        except Exception as e:
            self.log_recovery_event(
                "corruption_scan_error", f"Corruption scan failed: {str(e)}"
            )

    def is_file_corrupted(self, file_path: Path) -> bool:
        """Check if a JSON file is corrupted."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            return False
        except (json.JSONDecodeError, UnicodeDecodeError, IOError):
            return True

    def attempt_file_repair(self, file_path: Path) -> bool:
        """Attempt to repair a corrupted JSON file."""
        try:
            # Create backup of corrupted file
            backup_path = file_path.with_suffix(".json.corrupted")
            shutil.copy2(file_path, backup_path)

            # Try to read and repair the file
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Attempt basic JSON repair
            repaired_content = self.repair_json_content(content)

            if repaired_content:
                # Write repaired content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(repaired_content)

                # Verify repair was successful
                if not self.is_file_corrupted(file_path):
                    self.log_recovery_event(
                        "file_repaired", f"Successfully repaired: {file_path}"
                    )
                    return True

            self.log_recovery_event(
                "file_repair_failed", f"Failed to repair: {file_path}"
            )
            return False

        except Exception as e:
            self.log_recovery_event(
                "file_repair_error", f"Repair error for {file_path}: {str(e)}"
            )
            return False

    def repair_json_content(self, content: str) -> Optional[str]:
        """Attempt to repair JSON content by fixing common issues."""
        try:
            # Remove null bytes and other problematic characters
            content = content.replace("\x00", "")

            # Try to find the last complete JSON object
            brace_count = 0
            last_valid_pos = 0

            for i, char in enumerate(content):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        last_valid_pos = i + 1

            if last_valid_pos > 0:
                truncated_content = content[:last_valid_pos]

                # Try to parse the truncated content
                try:
                    json.loads(truncated_content)
                    return truncated_content
                except json.JSONDecodeError:
                    pass

            # If truncation doesn't work, try to create a minimal valid JSON
            lines = content.split("\n")
            for i in range(len(lines) - 1, -1, -1):
                try:
                    partial_content = "\n".join(lines[:i])
                    if partial_content.strip().endswith(","):
                        partial_content = partial_content.rstrip().rstrip(",")

                    # Try to close any open structures
                    if partial_content.count("{") > partial_content.count("}"):
                        partial_content += "}"

                    json.loads(partial_content)
                    return partial_content
                except json.JSONDecodeError:
                    continue

            return None

        except Exception as e:
            print(f"[DEBUG_LOG] JSON repair error: {e}")
            return None

    def auto_cleanup_old_sessions(self):
        """Automatically clean up old sessions to free disk space."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_session_age_days)
            cleaned_count = 0
            freed_space = 0

            for session_folder in self.base_sessions_dir.iterdir():
                if not session_folder.is_dir():
                    continue

                # Check folder modification time
                folder_mtime = datetime.fromtimestamp(session_folder.stat().st_mtime)

                if folder_mtime < cutoff_date:
                    # Calculate folder size before deletion
                    folder_size = self.get_folder_size(session_folder)

                    # Create backup if enabled
                    if self.backup_enabled:
                        self.backup_session(session_folder)

                    # Remove old session
                    shutil.rmtree(session_folder)
                    cleaned_count += 1
                    freed_space += folder_size

                    self.log_recovery_event(
                        "session_cleanup",
                        f"Cleaned up old session: {session_folder.name}",
                    )

            if cleaned_count > 0:
                freed_mb = freed_space / (1024**2)
                self.log_recovery_event(
                    "cleanup_complete",
                    f"Cleaned {cleaned_count} sessions, freed {freed_mb:.1f}MB",
                )

        except Exception as e:
            self.log_recovery_event("cleanup_error", f"Auto cleanup failed: {str(e)}")

    def get_folder_size(self, folder_path: Path) -> int:
        """Calculate total size of a folder in bytes."""
        total_size = 0
        try:
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            print(f"[DEBUG_LOG] Error calculating folder size: {e}")
        return total_size

    def backup_session(self, session_folder: Path) -> bool:
        """Create backup of session folder."""
        if not self.backup_enabled or not self.backup_dir:
            return False

        try:
            backup_path = self.backup_dir / session_folder.name
            shutil.copytree(session_folder, backup_path, dirs_exist_ok=True)

            self.backup_completed.emit(session_folder.name, str(backup_path))
            self.log_recovery_event(
                "backup_created", f"Backed up session: {session_folder.name}"
            )
            return True

        except Exception as e:
            self.log_recovery_event(
                "backup_error", f"Backup failed for {session_folder.name}: {str(e)}"
            )
            return False

    def recover_incomplete_sessions(self) -> List[Dict]:
        """Scan for and recover incomplete sessions."""
        recovered_sessions = []

        try:
            for session_folder in self.base_sessions_dir.iterdir():
                if not session_folder.is_dir():
                    continue

                # Look for session log files
                log_files = list(session_folder.glob("*_log.json"))

                for log_file in log_files:
                    if self.is_session_incomplete(log_file):
                        recovery_info = self.recover_session(log_file)
                        if recovery_info:
                            recovered_sessions.append(recovery_info)
                            self.session_recovered.emit(
                                recovery_info["session_id"],
                                recovery_info["recovery_details"],
                            )

            if recovered_sessions:
                self.log_recovery_event(
                    "sessions_recovered",
                    f"Recovered {len(recovered_sessions)} incomplete sessions",
                )

        except Exception as e:
            self.log_recovery_event(
                "recovery_error", f"Session recovery failed: {str(e)}"
            )

        return recovered_sessions

    def is_session_incomplete(self, log_file: Path) -> bool:
        """Check if a session is incomplete (missing end_time or session_end event)."""
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            # Check if session has end_time
            if not session_data.get("end_time"):
                return True

            # Check if session has session_end event
            events = session_data.get("events", [])
            has_session_end = any(
                event.get("event") == "session_end" for event in events
            )

            return not has_session_end

        except Exception:
            return True  # Assume incomplete if I can't read it

    def recover_session(self, log_file: Path) -> Optional[Dict]:
        """Recover an incomplete session by adding missing end information."""
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            session_id = session_data.get("session", "unknown")

            # Add end_time if missing
            if not session_data.get("end_time"):
                # Use file modification time as approximate end time
                end_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                session_data["end_time"] = end_time.isoformat()

                # Calculate duration if start_time exists
                start_time_str = session_data.get("start_time")
                if start_time_str:
                    try:
                        start_time = datetime.fromisoformat(
                            start_time_str.replace("Z", "+00:00")
                        )
                        duration = (
                            end_time - start_time.replace(tzinfo=None)
                        ).total_seconds()
                        session_data["duration"] = duration
                    except Exception:
                        session_data["duration"] = 0

            # Add session_end event if missing
            events = session_data.get("events", [])
            has_session_end = any(
                event.get("event") == "session_end" for event in events
            )

            if not has_session_end:
                end_event = {
                    "event": "session_end",
                    "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "timestamp": datetime.now().isoformat(),
                    "recovered": True,
                }
                events.append(end_event)
                session_data["events"] = events

            # Mark as recovered and update status
            session_data["status"] = "recovered"
            session_data["recovery_time"] = datetime.now().isoformat()

            # Write recovered session back to file
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            recovery_info = {
                "session_id": session_id,
                "log_file": str(log_file),
                "recovery_time": session_data["recovery_time"],
                "recovery_details": "Added missing end_time and session_end event",
            }

            self.log_recovery_event(
                "session_recovered",
                f"Recovered session {session_id}: {recovery_info['recovery_details']}",
            )

            return recovery_info

        except Exception as e:
            self.log_recovery_event(
                "session_recovery_error",
                f"Failed to recover session {log_file}: {str(e)}",
            )
            return None

    def log_recovery_event(self, event_type: str, message: str):
        """Log recovery events to the recovery log file."""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {event_type}: {message}\n"

            with open(self.recovery_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to write recovery log: {e}")

    def get_recovery_statistics(self) -> Dict:
        """Get recovery system statistics."""
        try:
            stats = {
                "total_sessions": len(list(self.base_sessions_dir.glob("*/"))),
                "disk_usage": {},
                "backup_enabled": self.backup_enabled,
                "monitoring_active": self.monitoring_active,
                "recovery_log_size": 0,
            }

            # Disk usage statistics
            if self.base_sessions_dir.exists():
                usage = psutil.disk_usage(str(self.base_sessions_dir))
                stats["disk_usage"]["main"] = {
                    "total_gb": usage.total / (1024**3),
                    "used_gb": usage.used / (1024**3),
                    "free_gb": usage.free / (1024**3),
                }

            if self.backup_dir and self.backup_dir.exists():
                backup_usage = psutil.disk_usage(str(self.backup_dir))
                stats["disk_usage"]["backup"] = {
                    "total_gb": backup_usage.total / (1024**3),
                    "used_gb": backup_usage.used / (1024**3),
                    "free_gb": backup_usage.free / (1024**3),
                }

            # Recovery log size
            if self.recovery_log_file.exists():
                stats["recovery_log_size"] = self.recovery_log_file.stat().st_size

            return stats

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to get recovery statistics: {e}")
            return {}


# Global recovery manager instance
_recovery_manager_instance: Optional[SessionRecoveryManager] = None


def get_recovery_manager(
    base_sessions_dir: str = "recordings", backup_dir: Optional[str] = None
) -> SessionRecoveryManager:
    """
    Get the global recovery manager instance.
    Creates one if it doesn't exist.

    Args:
        base_sessions_dir (str): Base directory for session recordings
        backup_dir (str, optional): Secondary backup directory

    Returns:
        SessionRecoveryManager: Global recovery manager instance
    """
    global _recovery_manager_instance
    if _recovery_manager_instance is None:
        _recovery_manager_instance = SessionRecoveryManager(
            base_sessions_dir, backup_dir
        )
    return _recovery_manager_instance


def reset_recovery_manager() -> None:
    """Reset the global recovery manager instance (useful for testing)."""
    global _recovery_manager_instance
    if _recovery_manager_instance and _recovery_manager_instance.monitoring_active:
        _recovery_manager_instance.stop_monitoring()
    _recovery_manager_instance = None
