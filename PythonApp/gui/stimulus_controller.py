"""
Stimulus Controller for Multi-Sensor Recording System Controller

This module implements the StimulusController class which manages video stimulus presentation
using Qt Multimedia components (QMediaPlayer and QVideoWidget). It provides functionality for
video loading, playback control, full-screen display, keyboard shortcuts, and timing logging.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.5 - Stimulus Presentation Controller
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

class TimingLogger:
    """Handles experiment timing and event logging."""

    def __init__(self, log_directory: str = "logs"):
        self.log_directory = log_directory
        self.current_log_file: Optional[str] = None
        self.experiment_start_time: Optional[float] = None
        self.event_counter = 0

        os.makedirs(log_directory, exist_ok=True)

    def start_experiment_log(self, video_file: str) -> str:
        """
        Start a new experiment log file.

        Args:
            video_file (str): Path to the stimulus video file

        Returns:
            str: Path to the created log file
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.current_log_file = os.path.join(
            self.log_directory, f"experiment_log_{timestamp}.json"
        )

        self.experiment_start_time = time.time()
        self.event_counter = 0

        log_data = {
            "experiment_info": {
                "start_time": self.experiment_start_time,
                "start_time_formatted": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(self.experiment_start_time)
                ),
                "stimulus_file": video_file,
                "stimulus_filename": os.path.basename(video_file),
            },
            "events": [],
        }

        with open(self.current_log_file, "w") as f:
            json.dump(log_data, f, indent=2)

        return self.current_log_file

    def log_stimulus_start(self, video_duration_ms: int):
        """
        Log stimulus playback start.

        Args:
            video_duration_ms (int): Video duration in milliseconds
        """
        if not self.current_log_file or not self.experiment_start_time:
            return

        current_time = time.time()
        dt = datetime.fromtimestamp(current_time)
        event = {
            "event_type": "stimulus_start",
            "timestamp": current_time,
            "timestamp_formatted": dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "experiment_time": current_time - self.experiment_start_time,
            "video_duration_ms": video_duration_ms,
            "video_duration_s": video_duration_ms / 1000.0,
        }

        self._append_event(event)

    def log_event_marker(self, video_position_ms: int, marker_label: str = ""):
        """
        Log an event marker during stimulus presentation.

        Args:
            video_position_ms (int): Current video position in milliseconds
            marker_label (str): Optional label for the marker
        """
        if not self.current_log_file or not self.experiment_start_time:
            return

        current_time = time.time()
        self.event_counter += 1
        dt = datetime.fromtimestamp(current_time)

        event = {
            "event_type": "event_marker",
            "marker_number": self.event_counter,
            "marker_label": marker_label or f"Marker {self.event_counter}",
            "timestamp": current_time,
            "timestamp_formatted": dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "experiment_time": current_time - self.experiment_start_time,
            "video_position_ms": video_position_ms,
            "video_position_s": video_position_ms / 1000.0,
        }

        self._append_event(event)

    def log_stimulus_end(self, video_position_ms: int, reason: str = "completed"):
        """
        Log stimulus playback end.

        Args:
            video_position_ms (int): Final video position in milliseconds
            reason (str): Reason for ending (completed, stopped, error)
        """
        if not self.current_log_file or not self.experiment_start_time:
            return

        current_time = time.time()
        dt = datetime.fromtimestamp(current_time)
        event = {
            "event_type": "stimulus_end",
            "timestamp": current_time,
            "timestamp_formatted": dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "experiment_time": current_time - self.experiment_start_time,
            "video_position_ms": video_position_ms,
            "video_position_s": video_position_ms / 1000.0,
            "end_reason": reason,
            "total_markers": self.event_counter,
        }

        self._append_event(event)

    def _append_event(self, event: Dict[str, Any]):
        """Append an event to the current log file."""
        if not self.current_log_file:
            return

        try:
            with open(self.current_log_file, "r") as f:
                log_data = json.load(f)

            log_data["events"].append(event)

            with open(self.current_log_file, "w") as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            print(f"[DEBUG_LOG] Error writing to log file: {e}")

class StimulusVideoWidget(QVideoWidget):
    """Custom QVideoWidget with keyboard shortcut support."""

    space_pressed = pyqtSignal()
    escape_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        """Handle keyboard events for shortcuts."""
        if event.key() == Qt.Key_Space:
            self.space_pressed.emit()
            event.accept()
        elif event.key() == Qt.Key_Escape:
            self.escape_pressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to toggle full-screen."""
        if self.isFullScreen():
            self.setFullScreen(False)
        else:
            self.showFullScreen()
        event.accept()

class StimulusController(QWidget):
    """
    Main controller for stimulus presentation functionality.

    This class manages video playback using QMediaPlayer and QVideoWidget,
    handles full-screen display, keyboard shortcuts, and timing logging.
    """

    status_changed = pyqtSignal(str)
    experiment_started = pyqtSignal()
    experiment_ended = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = StimulusVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        self.timing_logger = TimingLogger()
        self.current_video_file: Optional[str] = None
        self.is_experiment_active = False

        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.setInterval(100)

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        self.video_widget.hide()
        layout.addWidget(self.video_widget)

        self.status_label = QLabel("Stimulus Controller Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()

        self.test_play_btn = QPushButton("Test Play")
        self.test_play_btn.clicked.connect(self.test_play)
        self.test_play_btn.setEnabled(False)
        button_layout.addWidget(self.test_play_btn)

        self.test_pause_btn = QPushButton("Test Pause")
        self.test_pause_btn.clicked.connect(self.test_pause)
        self.test_pause_btn.setEnabled(False)
        button_layout.addWidget(self.test_pause_btn)

        self.test_fullscreen_btn = QPushButton("Test Full-Screen")
        self.test_fullscreen_btn.clicked.connect(self.test_fullscreen)
        self.test_fullscreen_btn.setEnabled(False)
        button_layout.addWidget(self.test_fullscreen_btn)

        layout.addLayout(button_layout)

    def connect_signals(self):
        """Connect media player and widget signals."""
        self.media_player.stateChanged.connect(self.on_state_changed)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.error.connect(self.on_media_error)

        self.video_widget.space_pressed.connect(self.toggle_play_pause)
        self.video_widget.escape_pressed.connect(self.exit_fullscreen)

        self.space_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.space_shortcut.activated.connect(self.toggle_play_pause)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.exit_fullscreen)

    def load_video(self, file_path: str) -> bool:
        """
        Load a video file for stimulus presentation.

        Args:
            file_path (str): Path to the video file

        Returns:
            bool: True if loading was successful, False otherwise
        """
        if not os.path.exists(file_path):
            self.error_occurred.emit(f"Video file not found: {file_path}")
            return False

        supported_formats = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".m4v", ".3gp"]
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in supported_formats:
            self.error_occurred.emit(f"Unsupported video format: {file_ext}")
            return False

        try:
            self.media_player.stop()

            file_url = QUrl.fromLocalFile(os.path.abspath(file_path))
            media_content = QMediaContent(file_url)

            self.media_player.setMedia(media_content)

            self.current_video_file = file_path

            self.test_play_btn.setEnabled(True)
            self.test_pause_btn.setEnabled(True)
            self.test_fullscreen_btn.setEnabled(True)

            self.status_changed.emit(f"Loaded: {os.path.basename(file_path)}")
            print(f"[DEBUG_LOG] Video loaded successfully: {file_path}")
            print(f"[DEBUG_LOG] Media URL: {file_url.toString()}")

            return True

        except Exception as e:
            self.error_occurred.emit(f"Error loading video: {str(e)}")
            print(f"[DEBUG_LOG] Error loading video: {e}")
            return False

    def start_stimulus_playback(self, screen_index: int = 0) -> bool:
        """
        Start stimulus playback with experiment logging.

        Args:
            screen_index (int): Index of screen to display on (0 = primary)

        Returns:
            bool: True if playback started successfully, False otherwise
        """
        if not self.current_video_file:
            self.error_occurred.emit("No video file loaded")
            return False

        if self.is_experiment_active:
            self.error_occurred.emit("Experiment already active")
            return False

        try:
            log_file = self.timing_logger.start_experiment_log(self.current_video_file)
            print(f"[DEBUG_LOG] Started experiment log: {log_file}")

            self.position_video_on_screen(screen_index)

            self.video_widget.show()
            self.video_widget.showFullScreen()
            self.video_widget.setFocus()

            self.media_player.play()
            self.position_timer.start()

            self.is_experiment_active = True
            self.experiment_started.emit()
            self.status_changed.emit("Experiment Started - Stimulus Playing")

            print(f"[DEBUG_LOG] Stimulus playback started on screen {screen_index}")
            return True

        except Exception as e:
            self.error_occurred.emit(f"Error starting stimulus playback: {str(e)}")
            print(f"[DEBUG_LOG] Error starting stimulus playback: {e}")
            return False

    def stop_stimulus_playback(self, reason: str = "stopped"):
        """
        Stop stimulus playback and end experiment logging.

        Args:
            reason (str): Reason for stopping (stopped, completed, error)
        """
        if not self.is_experiment_active:
            return

        try:
            self.media_player.pause()
            self.position_timer.stop()

            current_position = self.media_player.position()
            self.timing_logger.log_stimulus_end(current_position, reason)

            self.video_widget.hide()

            self.is_experiment_active = False
            self.experiment_ended.emit()
            self.status_changed.emit(f"Experiment Ended - {reason.title()}")

            print(f"[DEBUG_LOG] Stimulus playback stopped: {reason}")

        except Exception as e:
            self.error_occurred.emit(f"Error stopping stimulus playback: {str(e)}")
            print(f"[DEBUG_LOG] Error stopping stimulus playback: {e}")

    def mark_event(self, label: str = ""):
        """
        Mark an event during stimulus presentation.

        Args:
            label (str): Optional label for the event marker
        """
        if not self.is_experiment_active:
            return

        try:
            current_position = self.media_player.position()
            self.timing_logger.log_event_marker(current_position, label)

            marker_num = self.timing_logger.event_counter
            self.status_changed.emit(
                f"Event Marker {marker_num} - {current_position/1000:.1f}s"
            )

            print(f"[DEBUG_LOG] Event marker {marker_num} at {current_position}ms")

        except Exception as e:
            self.error_occurred.emit(f"Error marking event: {str(e)}")
            print(f"[DEBUG_LOG] Error marking event: {e}")

    def position_video_on_screen(self, screen_index: int):
        """
        Position the video widget on the specified screen.

        Args:
            screen_index (int): Index of the target screen
        """
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            target_screen = screens[screen_index]
            geometry = target_screen.geometry()
            self.video_widget.setGeometry(geometry)
            print(f"[DEBUG_LOG] Video positioned on screen {screen_index}: {geometry}")
        else:
            print(
                f"[DEBUG_LOG] Invalid screen index {screen_index}, using primary screen"
            )

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            print("[DEBUG_LOG] Playback paused via shortcut")
        else:
            self.media_player.play()
            print("[DEBUG_LOG] Playback resumed via shortcut")

    def exit_fullscreen(self):
        """Exit full-screen mode."""
        if self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
            self.video_widget.hide()
            print("[DEBUG_LOG] Exited full-screen mode")

            if self.is_experiment_active:
                self.stop_stimulus_playback("user_exit")

    def test_play(self):
        """Test play functionality."""
        self.media_player.play()
        self.video_widget.show()

    def test_pause(self):
        """Test pause functionality."""
        self.media_player.pause()

    def test_fullscreen(self):
        """Test full-screen functionality."""
        self.video_widget.show()
        self.video_widget.showFullScreen()
        self.video_widget.setFocus()

    def on_state_changed(self, state):
        """Handle media player state changes."""
        state_names = {
            QMediaPlayer.StoppedState: "Stopped",
            QMediaPlayer.PlayingState: "Playing",
            QMediaPlayer.PausedState: "Paused",
        }
        state_name = state_names.get(state, "Unknown")
        print(f"[DEBUG_LOG] Media player state changed: {state_name}")

        if state == QMediaPlayer.PlayingState and self.is_experiment_active:
            duration = self.media_player.duration()
            self.timing_logger.log_stimulus_start(duration)

    def on_media_status_changed(self, status):
        """Handle media status changes."""
        if status == QMediaPlayer.EndOfMedia and self.is_experiment_active:
            print("[DEBUG_LOG] Video reached end of media")
            self.stop_stimulus_playback("completed")

    def on_position_changed(self, position):
        """Handle position changes during playback."""

    def on_duration_changed(self, duration):
        """Handle duration changes when media is loaded."""
        if duration > 0:
            duration_s = duration / 1000.0
            print(f"[DEBUG_LOG] Video duration: {duration_s:.1f} seconds")

    def on_media_error(self, error):
        """Handle media player errors."""
        error_messages = {
            QMediaPlayer.NoError: "No error",
            QMediaPlayer.ResourceError: "Resource error - file not found or corrupted",
            QMediaPlayer.FormatError: "Format error - unsupported video format",
            QMediaPlayer.NetworkError: "Network error",
            QMediaPlayer.AccessDeniedError: "Access denied - insufficient permissions",
            QMediaPlayer.ServiceMissingError: "Service missing - codec not available",
        }

        error_msg = error_messages.get(error, f"Unknown error ({error})")
        self.error_occurred.emit(f"Media player error: {error_msg}")
        print(f"[DEBUG_LOG] Media player error: {error_msg}")

        if self.is_experiment_active:
            self.stop_stimulus_playback("error")

    def update_position(self):
        """Update position information during playback."""
        if (
            self.is_experiment_active
            and self.media_player.state() == QMediaPlayer.PlayingState
        ):
            position = self.media_player.position()
            duration = self.media_player.duration()

            if duration > 0:
                progress = (position / duration) * 100
                self.status_label.setText(
                    f"Playing: {position/1000:.1f}s / {duration/1000:.1f}s ({progress:.1f}%)"
                )

    def get_current_position(self) -> int:
        """Get current playback position in milliseconds."""
        return self.media_player.position()

    def get_duration(self) -> int:
        """Get video duration in milliseconds."""
        return self.media_player.duration()

    def is_playing(self) -> bool:
        """Check if video is currently playing."""
        return self.media_player.state() == QMediaPlayer.PlayingState

    def is_experiment_running(self) -> bool:
        """Check if an experiment is currently active."""
        return self.is_experiment_active
