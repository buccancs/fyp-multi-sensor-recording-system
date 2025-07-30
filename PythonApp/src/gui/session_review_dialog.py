"""
Session Review Dialog for Multi-Sensor Recording System Controller

This module implements the SessionReviewDialog class for Milestone 3.8: Session Metadata Logging and Review.
It provides a comprehensive post-session review interface that displays session files, statistics,
and allows opening files with default applications.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
Milestone: 3.8 - Session Metadata Logging and Review
"""

import json
import os
import platform
import subprocess
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QTabWidget,
    QWidget,
    QGroupBox,
    QGridLayout,
    QMessageBox,
    QSplitter,
    QFrame,
)
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class SessionReviewDialog(QDialog):
    """
    Post-session review dialog for comprehensive session analysis.

    This dialog provides:
    - Session file listing with file opening capabilities
    - Session summary statistics and metadata
    - Calibration results display
    - Event timeline review
    - File size and duration analysis
    """

    # Signals
    file_open_requested = pyqtSignal(str)  # File path to open

    def __init__(self, session_data: Dict, session_folder: str, parent=None):
        """
        Initialize session review dialog.

        Args:
            session_data (Dict): Complete session data from SessionLogger
            session_folder (str): Path to session folder containing files
            parent: Parent widget
        """
        super().__init__(parent)
        self.session_data = session_data
        self.session_folder = Path(session_folder)
        self.session_files = []

        self.setWindowTitle(
            f"Session Review - {session_data.get('session', 'Unknown')}"
        )
        self.setModal(True)
        self.resize(900, 700)

        # Initialize UI
        self.init_ui()

        # Load session files and data
        self.load_session_files()
        self.populate_session_info()
        self.populate_file_list()
        self.populate_event_timeline()

        print(
            f"[DEBUG_LOG] SessionReviewDialog initialized for session: {session_data.get('session', 'Unknown')}"
        )

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Create header with session info
        self.create_header(layout)

        # Create main content area with tabs
        self.create_main_content(layout)

        # Create button bar
        self.create_button_bar(layout)

    def create_header(self, parent_layout):
        """Create header section with session title and basic info."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
        """
        )

        header_layout = QVBoxLayout(header_frame)

        # Session title
        session_name = self.session_data.get("session", "Unknown Session")
        title_label = QLabel(f"Session Review: {session_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # Session summary line
        start_time = self.session_data.get("start_time", "Unknown")
        duration = self.session_data.get("duration", 0)
        status = self.session_data.get("status", "Unknown")

        if isinstance(duration, (int, float)):
            duration_str = f"{duration:.1f} seconds"
        else:
            duration_str = str(duration)

        summary_label = QLabel(
            f"Started: {start_time} | Duration: {duration_str} | Status: {status}"
        )
        summary_label.setStyleSheet("color: #666666; font-size: 10pt;")
        header_layout.addWidget(summary_label)

        parent_layout.addWidget(header_frame)

    def create_main_content(self, parent_layout):
        """Create main content area with tabbed interface."""
        self.tab_widget = QTabWidget()

        # Files tab
        self.create_files_tab()

        # Statistics tab
        self.create_statistics_tab()

        # Events tab
        self.create_events_tab()

        # Calibration tab (if calibration data exists)
        if self.session_data.get("calibration_files"):
            self.create_calibration_tab()

        parent_layout.addWidget(self.tab_widget)

    def create_files_tab(self):
        """Create files tab with file listing and preview."""
        files_widget = QWidget()
        layout = QHBoxLayout(files_widget)

        # Left side: File list
        left_panel = QGroupBox("Session Files")
        left_layout = QVBoxLayout(left_panel)

        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_list.currentItemChanged.connect(self.on_file_selection_changed)
        left_layout.addWidget(self.file_list)

        # File action buttons
        file_buttons_layout = QHBoxLayout()

        self.open_file_btn = QPushButton("Open File")
        self.open_file_btn.clicked.connect(self.open_selected_file)
        self.open_file_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.open_file_btn)

        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.clicked.connect(self.open_session_folder)
        file_buttons_layout.addWidget(self.open_folder_btn)

        file_buttons_layout.addStretch()
        left_layout.addLayout(file_buttons_layout)

        # Right side: File details
        right_panel = QGroupBox("File Details")
        right_layout = QVBoxLayout(right_panel)

        self.file_details = QTextEdit()
        self.file_details.setReadOnly(True)
        self.file_details.setMaximumHeight(200)
        right_layout.addWidget(self.file_details)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        self.tab_widget.addTab(files_widget, "Files")

    def create_statistics_tab(self):
        """Create statistics tab with session metrics."""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)

        # Session statistics
        stats_group = QGroupBox("Session Statistics")
        stats_layout = QGridLayout(stats_group)

        row = 0

        # Basic session info
        stats_layout.addWidget(QLabel("Session ID:"), row, 0)
        stats_layout.addWidget(
            QLabel(self.session_data.get("session", "Unknown")), row, 1
        )
        row += 1

        stats_layout.addWidget(QLabel("Session Name:"), row, 0)
        stats_layout.addWidget(
            QLabel(self.session_data.get("session_name", "Unknown")), row, 1
        )
        row += 1

        # Timing information
        start_time = self.session_data.get("start_time", "Unknown")
        end_time = self.session_data.get("end_time", "Unknown")
        duration = self.session_data.get("duration", 0)

        stats_layout.addWidget(QLabel("Start Time:"), row, 0)
        stats_layout.addWidget(QLabel(start_time), row, 1)
        row += 1

        stats_layout.addWidget(QLabel("End Time:"), row, 0)
        stats_layout.addWidget(QLabel(end_time), row, 1)
        row += 1

        stats_layout.addWidget(QLabel("Duration:"), row, 0)
        if isinstance(duration, (int, float)):
            duration_str = f"{duration:.1f} seconds ({duration/60:.1f} minutes)"
        else:
            duration_str = str(duration)
        stats_layout.addWidget(QLabel(duration_str), row, 1)
        row += 1

        # Device information
        devices = self.session_data.get("devices", [])
        stats_layout.addWidget(QLabel("Devices:"), row, 0)
        device_count = len(devices)
        device_names = (
            [d.get("id", "Unknown") for d in devices]
            if isinstance(devices, list)
            else []
        )
        device_info = f"{device_count} devices: {', '.join(device_names)}"
        stats_layout.addWidget(QLabel(device_info), row, 1)
        row += 1

        # Event statistics
        events = self.session_data.get("events", [])
        stats_layout.addWidget(QLabel("Total Events:"), row, 0)
        stats_layout.addWidget(QLabel(str(len(events))), row, 1)
        row += 1

        # File statistics
        total_files = len(self.session_files)
        total_size = sum(f.get("size", 0) for f in self.session_files if f.get("size"))
        total_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0

        stats_layout.addWidget(QLabel("Total Files:"), row, 0)
        stats_layout.addWidget(QLabel(str(total_files)), row, 1)
        row += 1

        stats_layout.addWidget(QLabel("Total Size:"), row, 0)
        stats_layout.addWidget(QLabel(f"{total_size_mb:.1f} MB"), row, 1)
        row += 1

        layout.addWidget(stats_group)

        # Event type breakdown
        if events:
            event_group = QGroupBox("Event Breakdown")
            event_layout = QGridLayout(event_group)

            # Count event types
            event_counts = {}
            for event in events:
                event_type = event.get("event", "unknown")
                event_counts[event_type] = event_counts.get(event_type, 0) + 1

            row = 0
            for event_type, count in sorted(event_counts.items()):
                event_layout.addWidget(QLabel(f"{event_type}:"), row, 0)
                event_layout.addWidget(QLabel(str(count)), row, 1)
                row += 1

            layout.addWidget(event_group)

        layout.addStretch()

        self.tab_widget.addTab(stats_widget, "Statistics")

    def create_events_tab(self):
        """Create events tab with timeline view."""
        events_widget = QWidget()
        layout = QVBoxLayout(events_widget)

        events_group = QGroupBox("Event Timeline")
        events_layout = QVBoxLayout(events_group)

        self.events_list = QListWidget()
        self.events_list.setAlternatingRowColors(True)

        # Populate events
        events = self.session_data.get("events", [])
        for event in events:
            event_text = self.format_event_for_display(event)
            item = QListWidgetItem(event_text)

            # Color code different event types
            event_type = event.get("event", "unknown")
            if event_type == "error":
                item.setBackground(Qt.red)
                item.setForeground(Qt.white)
            elif event_type in ["session_start", "session_end"]:
                item.setBackground(Qt.blue)
                item.setForeground(Qt.white)
            elif event_type in ["stimulus_play", "stimulus_stop"]:
                item.setBackground(Qt.green)
            elif event_type == "marker":
                item.setBackground(Qt.yellow)

            self.events_list.addItem(item)

        events_layout.addWidget(self.events_list)
        layout.addWidget(events_group)

        self.tab_widget.addTab(events_widget, "Events")

    def create_calibration_tab(self):
        """Create calibration tab if calibration data exists."""
        calib_widget = QWidget()
        layout = QVBoxLayout(calib_widget)

        calib_group = QGroupBox("Calibration Results")
        calib_layout = QVBoxLayout(calib_group)

        # List calibration files
        calib_files = self.session_data.get("calibration_files", [])

        calib_info = QTextEdit()
        calib_info.setReadOnly(True)

        info_text = f"Calibration files captured during session:\n\n"
        for i, calib_file in enumerate(calib_files, 1):
            info_text += f"{i}. {calib_file}\n"

            # Check if file exists and add details
            file_path = self.session_folder / calib_file
            if file_path.exists():
                file_size = file_path.stat().st_size
                info_text += f"   Size: {file_size / 1024:.1f} KB\n"
                info_text += f"   Path: {file_path}\n"
            else:
                info_text += f"   Status: File not found\n"
            info_text += "\n"

        if not calib_files:
            info_text = "No calibration files were captured during this session."

        calib_info.setPlainText(info_text)
        calib_layout.addWidget(calib_info)

        layout.addWidget(calib_group)

        self.tab_widget.addTab(calib_widget, "Calibration")

    def create_button_bar(self, parent_layout):
        """Create bottom button bar."""
        button_layout = QHBoxLayout()

        # Export button
        export_btn = QPushButton("Export Session Data")
        export_btn.clicked.connect(self.export_session_data)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)

        parent_layout.addLayout(button_layout)

    def load_session_files(self):
        """Load all files from the session folder."""
        self.session_files = []

        if not self.session_folder.exists():
            print(f"[DEBUG_LOG] Session folder does not exist: {self.session_folder}")
            return

        # Scan session folder for files
        for file_path in self.session_folder.iterdir():
            if file_path.is_file():
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "type": self.get_file_type(file_path),
                }
                self.session_files.append(file_info)

        # Sort files by name
        self.session_files.sort(key=lambda x: x["name"])

        print(f"[DEBUG_LOG] Loaded {len(self.session_files)} files from session folder")

    def get_file_type(self, file_path: Path) -> str:
        """Determine file type based on extension."""
        suffix = file_path.suffix.lower()

        if suffix in [".mp4", ".avi", ".mov", ".mkv", ".wmv"]:
            return "Video"
        elif suffix in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return "Image"
        elif suffix in [".json"]:
            return "Data"
        elif suffix in [".txt", ".log"]:
            return "Log"
        else:
            return "Other"

    def populate_session_info(self):
        """Populate session information displays."""
        # This method can be extended to populate additional session info

    def populate_file_list(self):
        """Populate the file list widget."""
        self.file_list.clear()

        for file_info in self.session_files:
            # Create display text
            name = file_info["name"]
            size_mb = file_info["size"] / (1024 * 1024)
            file_type = file_info["type"]

            display_text = f"{name} ({file_type}, {size_mb:.1f} MB)"

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, file_info)  # Store file info in item

            # Add icon based on file type
            if file_type == "Video":
                item.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
            elif file_type == "Image":
                item.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
            elif file_type == "Data":
                item.setIcon(
                    self.style().standardIcon(self.style().SP_FileDialogDetailedView)
                )

            self.file_list.addItem(item)

    def populate_event_timeline(self):
        """Populate event timeline (already done in create_events_tab)."""

    def format_event_for_display(self, event: Dict) -> str:
        """Format event for display in timeline."""
        event_type = event.get("event", "unknown")
        time_str = event.get("time", "unknown")

        # Use the same formatting logic as SessionLogger
        if event_type == "session_start":
            devices = event.get("devices", [])
            return f"[{time_str}] Session started. Devices: {', '.join(devices) if devices else 'None'}"
        elif event_type == "device_connected":
            device = event.get("device", "unknown")
            device_type = event.get("device_type", "unknown")
            return f"[{time_str}] Device connected: {device} ({device_type})"
        elif event_type == "start_record":
            devices = event.get("devices", [])
            return f"[{time_str}] Recording started on devices: {', '.join(devices) if devices else 'None'}"
        elif event_type == "stimulus_play":
            media = event.get("media", "unknown")
            return f"[{time_str}] Stimulus started: {media}"
        elif event_type == "marker":
            label = event.get("label", "unknown")
            stim_time = event.get("stim_time")
            if stim_time:
                return f"[{time_str}] Marker '{label}' inserted (stimulus time: {stim_time})"
            else:
                return f"[{time_str}] Marker '{label}' inserted"
        elif event_type == "error":
            error_type = event.get("error_type", "unknown")
            message = event.get("message", "No details")
            device = event.get("device")
            if device:
                return (
                    f"[{time_str}] ERROR ({error_type}): {message} [Device: {device}]"
                )
            else:
                return f"[{time_str}] ERROR ({error_type}): {message}"
        else:
            # Generic formatting
            return f"[{time_str}] {event_type}: {str(event)}"

    def on_file_selection_changed(self, current, previous):
        """Handle file selection change."""
        if current:
            self.open_file_btn.setEnabled(True)

            # Show file details
            file_info = current.data(Qt.UserRole)
            if file_info:
                details_text = f"File: {file_info['name']}\n"
                details_text += f"Type: {file_info['type']}\n"
                details_text += f"Size: {file_info['size'] / (1024 * 1024):.2f} MB\n"
                details_text += (
                    f"Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                details_text += f"Path: {file_info['path']}\n"

                self.file_details.setPlainText(details_text)
        else:
            self.open_file_btn.setEnabled(False)
            self.file_details.clear()

    def on_file_double_clicked(self, item):
        """Handle file double-click to open file."""
        self.open_selected_file()

    def open_selected_file(self):
        """Open the selected file with default application."""
        current_item = self.file_list.currentItem()
        if not current_item:
            return

        file_info = current_item.data(Qt.UserRole)
        if not file_info:
            return

        file_path = file_info["path"]

        try:
            # Open file with default application
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])

            print(f"[DEBUG_LOG] Opened file: {file_path}")
            self.file_open_requested.emit(file_path)

        except Exception as e:
            QMessageBox.warning(
                self,
                "File Open Error",
                f"Failed to open file: {file_info['name']}\n\nError: {str(e)}",
            )
            print(f"[DEBUG_LOG] Failed to open file {file_path}: {e}")

    def open_session_folder(self):
        """Open the session folder in file explorer."""
        try:
            if platform.system() == "Windows":
                os.startfile(str(self.session_folder))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(self.session_folder)])
            else:  # Linux
                subprocess.run(["xdg-open", str(self.session_folder)])

            print(f"[DEBUG_LOG] Opened session folder: {self.session_folder}")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Folder Open Error",
                f"Failed to open session folder.\n\nError: {str(e)}",
            )
            print(
                f"[DEBUG_LOG] Failed to open session folder {self.session_folder}: {e}"
            )

    def export_session_data(self):
        """Export session data to a summary file."""
        try:
            # Create summary data
            summary = {
                "session_info": self.session_data,
                "files": self.session_files,
                "export_time": datetime.now().isoformat(),
            }

            # Save to session folder
            export_path = (
                self.session_folder
                / f"{self.session_data.get('session', 'session')}_summary.json"
            )

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

            QMessageBox.information(
                self, "Export Complete", f"Session summary exported to:\n{export_path}"
            )

            print(f"[DEBUG_LOG] Session summary exported to: {export_path}")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Error",
                f"Failed to export session data.\n\nError: {str(e)}",
            )
            print(f"[DEBUG_LOG] Failed to export session data: {e}")


def show_session_review_dialog(
    session_data: Dict, session_folder: str, parent=None
) -> Optional[SessionReviewDialog]:
    """
    Convenience function to show session review dialog.

    Args:
        session_data (Dict): Session data from SessionLogger
        session_folder (str): Path to session folder
        parent: Parent widget

    Returns:
        SessionReviewDialog: The dialog instance, or None if creation failed
    """
    try:
        dialog = SessionReviewDialog(session_data, session_folder, parent)
        dialog.exec_()
        return dialog
    except Exception as e:
        print(f"[DEBUG_LOG] Failed to create session review dialog: {e}")
        if parent:
            QMessageBox.critical(
                parent,
                "Session Review Error",
                f"Failed to open session review dialog.\n\nError: {str(e)}",
            )
        return None
