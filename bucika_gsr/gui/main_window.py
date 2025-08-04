"""
Main Window for Multi-Sensor Recording System Controller

This module implements the MainWindow class which serves as the primary UI container
for Milestone 3.1: PyQt GUI Scaffolding and Application Framework.

The MainWindow provides:
- Menu bar with File, Tools, Help menus
- Toolbar with control buttons
- Status bar for messages
- Two-column layout: device status panel (left) and preview area (right)
- Bottom stimulus control panel

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework
"""

import base64
import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QAction,
    QMessageBox,
    QDockWidget,
    QPlainTextEdit,
)
# Import network server
from bucika_gsr.network.device_server import JsonSocketServer, create_command_message
from bucika_gsr.session.session_logger import get_session_logger
# Import session manager and logger
from bucika_gsr.session.session_manager import SessionManager
# Import webcam capture
from bucika_gsr.webcam.webcam_capture import WebcamCapture

from .calibration_dialog import CalibrationDialog
# Import modular components
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .session_review_dialog import show_session_review_dialog
from .stimulus_controller import StimulusController
from .stimulus_panel import StimulusControlPanel


class MainWindow(QMainWindow):
    """Main window for the Multi-Sensor Recording System Controller."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize session manager first (needed by JsonSocketServer)
        self.session_manager = SessionManager()
        self.current_session_id = None

        # Initialize session logger for comprehensive event logging
        self.session_logger = get_session_logger()

        # Initialize network server with session manager integration
        self.json_server = JsonSocketServer(session_manager=self.session_manager)
        self.server_running = False

        # Initialize webcam capture
        self.webcam_capture = WebcamCapture()
        self.webcam_previewing = False
        self.webcam_recording = False

        # Initialize stimulus controller (new for milestone 3.5)
        self.stimulus_controller = StimulusController(self)

        # Initialize UI components
        self.init_ui()

        # Connect server signals to GUI handlers
        self.connect_server_signals()

        # Connect webcam signals to GUI handlers
        self.connect_webcam_signals()

        # Connect stimulus controller signals (new for milestone 3.5)
        self.connect_stimulus_signals()

        # Connect session logger signals (new for milestone 3.8)
        self.connect_session_logger_signals()

        # Initialize placeholder data
        self.init_placeholder_data()

    def init_ui(self):
        """Initialize the user interface."""
        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create central widget and layout
        self.create_central_widget()

        # Create log dock widget
        self.create_log_dock()

        # Create status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Create the menu bar with File, Tools, Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        tools_menu.addAction(settings_action)

        # View menu
        view_menu = menubar.addMenu("View")

        self.show_log_action = QAction("Show Log", self)
        self.show_log_action.setCheckable(True)
        self.show_log_action.setChecked(False)  # Initially hidden
        self.show_log_action.triggered.connect(self.toggle_log_dock)
        view_menu.addAction(self.show_log_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar with control buttons."""
        toolbar = self.addToolBar("MainControls")
        toolbar.setMovable(False)

        # Connect action
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.handle_connect)
        toolbar.addAction(connect_action)

        # Disconnect action
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.handle_disconnect)
        toolbar.addAction(disconnect_action)

        toolbar.addSeparator()

        # Start Session action
        start_action = QAction("Start Session", self)
        start_action.triggered.connect(self.handle_start)
        toolbar.addAction(start_action)

        # Stop action
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.handle_stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # Calibration Dialog action
        calib_action = QAction("Open Calibration Dialog", self)
        calib_action.triggered.connect(self.open_calibration_dialog)
        toolbar.addAction(calib_action)

    def create_central_widget(self):
        """Create the central widget with main layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        central_vlayout = QVBoxLayout(central_widget)

        # Top panel with horizontal layout (device panel + preview area)
        top_panel = QWidget()
        top_hlayout = QHBoxLayout(top_panel)
        top_panel.setLayout(top_hlayout)

        # Create device status panel (left side)
        self.device_panel = DeviceStatusPanel(self)
        top_hlayout.addWidget(self.device_panel)

        # Create preview area (right side)
        self.preview_tabs = PreviewPanel(self)
        top_hlayout.addWidget(self.preview_tabs, 1)  # Give more space to preview

        central_vlayout.addWidget(top_panel)

        # Create stimulus control panel (bottom)
        self.stimulus_panel = StimulusControlPanel(self)
        central_vlayout.addWidget(self.stimulus_panel)

    def create_log_dock(self):
        """Create the log dock widget with enhanced session logging support (milestone 3.8)."""
        self.log_dock = QDockWidget("Session Log", self)

        # Use QPlainTextEdit for better performance with large text output
        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(200)  # Limit height

        # Set monospace font for clarity and enhanced styling
        self.log_widget.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 9pt;
                border: 1px solid #555555;
                selection-background-color: #404040;
            }
        """
        )

        # Enable line wrap for better readability
        self.log_widget.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.log_dock.setWidget(self.log_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        # Initially hide the log dock
        self.log_dock.hide()

        # Add initial log message
        self.log_message("Application started - Session logging system initialized")

    def toggle_log_dock(self):
        """Toggle the visibility of the log dock widget."""
        if self.log_dock.isVisible():
            self.log_dock.hide()
            self.show_log_action.setText("Show Log")
            self.show_log_action.setChecked(False)
            self.log_message("Log panel hidden")
        else:
            self.log_dock.show()
            self.show_log_action.setText("Hide Log")
            self.show_log_action.setChecked(True)
            self.log_message("Log panel shown")

    def log_message(self, message):
        """
        Add a timestamped message to the log with enhanced auto-scrolling (milestone 3.8).

        Args:
            message (str): The message to log
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        formatted_message = f"[{timestamp}] {message}"

        # Use appendPlainText for QPlainTextEdit
        self.log_widget.appendPlainText(formatted_message)

        # Enhanced auto-scroll to bottom - always show latest entry
        scrollbar = self.log_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # Ensure the cursor is at the end for consistent behavior
        cursor = self.log_widget.textCursor()
        cursor.movePosition(cursor.End)
        self.log_widget.setTextCursor(cursor)

    def create_status_bar(self):
        """Create the status bar."""
        self.statusBar().showMessage("Ready")

    def connect_server_signals(self):
        """Connect JsonSocketServer signals to GUI handler methods."""
        self.json_server.device_connected.connect(self.on_device_connected)
        self.json_server.device_disconnected.connect(self.on_device_disconnected)
        self.json_server.status_received.connect(self.on_status_received)
        self.json_server.ack_received.connect(self.on_ack_received)
        self.json_server.preview_frame_received.connect(self.on_preview_frame_received)
        self.json_server.sensor_data_received.connect(self.on_sensor_data_received)
        self.json_server.notification_received.connect(self.on_notification_received)
        self.json_server.error_occurred.connect(self.on_server_error)

        self.log_message("Server signals connected to GUI handlers")

    def connect_webcam_signals(self):
        """Connect WebcamCapture signals to GUI handler methods."""
        self.webcam_capture.frame_ready.connect(self.on_webcam_frame_ready)
        self.webcam_capture.recording_started.connect(self.on_webcam_recording_started)
        self.webcam_capture.recording_stopped.connect(self.on_webcam_recording_stopped)
        self.webcam_capture.error_occurred.connect(self.on_webcam_error)
        self.webcam_capture.status_changed.connect(self.on_webcam_status_changed)

    def connect_stimulus_signals(self):
        """Connect stimulus controller and panel signals (new for milestone 3.5)."""
        # Connect stimulus panel signals to stimulus controller
        self.stimulus_panel.file_loaded.connect(self.stimulus_controller.load_video)
        self.stimulus_panel.play_requested.connect(self.stimulus_controller.test_play)
        self.stimulus_panel.pause_requested.connect(self.stimulus_controller.test_pause)
        self.stimulus_panel.seek_requested.connect(self.on_stimulus_seek_requested)
        self.stimulus_panel.screen_changed.connect(self.on_stimulus_screen_changed)

        # Connect new milestone 3.5 signals
        self.stimulus_panel.start_recording_play_requested.connect(
            self.on_start_recording_play_requested
        )
        self.stimulus_panel.mark_event_requested.connect(self.on_mark_event_requested)

        # Connect stimulus controller signals to main window
        self.stimulus_controller.status_changed.connect(self.on_stimulus_status_changed)
        self.stimulus_controller.experiment_started.connect(
            self.on_stimulus_experiment_started
        )
        self.stimulus_controller.experiment_ended.connect(
            self.on_stimulus_experiment_ended
        )
        self.stimulus_controller.error_occurred.connect(self.on_stimulus_error)

        self.log_message("Webcam signals connected to GUI handlers")

    def connect_session_logger_signals(self):
        """Connect SessionLogger signals to GUI handler methods (new for milestone 3.8)."""
        self.session_logger.log_entry_added.connect(self.log_message)
        self.session_logger.session_started.connect(
            self.on_session_logger_session_started
        )
        self.session_logger.session_ended.connect(self.on_session_logger_session_ended)
        self.session_logger.error_logged.connect(self.on_session_logger_error)

        self.log_message("Session logger signals connected to GUI handlers")

    def init_placeholder_data(self):
        """Initialize placeholder data for testing."""
        # Placeholder data is now handled by the modular components

    # Menu action handlers
    def show_settings_dialog(self):
        """Show settings dialog (placeholder)."""
        self.log_message("Settings menu item selected - showing placeholder dialog")
        QMessageBox.information(
            self, "Settings", "Settings dialog not implemented yet."
        )
        self.log_message("Settings dialog closed")

    def show_about(self):
        """Show about dialog."""
        self.log_message("About menu item selected - showing application information")
        QMessageBox.about(
            self,
            "About",
            "Multi-Sensor Recording System Controller\n"
            "Version 3.1.0\n"
            "Milestone 3.1: PyQt GUI Scaffolding and Application Framework\n\n"
            "Author: Multi-Sensor Recording System Team\n"
            "Date: 2025-07-29",
        )
        self.log_message("About dialog closed")

    # Server signal handlers
    def on_device_connected(self, device_id, capabilities):
        """Handle device connection event."""
        self.log_message(
            f"Device connected: {device_id} with capabilities: {capabilities}"
        )

        # Create device display name with capability indicators
        capability_icons = []
        if "camera" in capabilities:
            capability_icons.append("📷")
        if "thermal" in capabilities:
            capability_icons.append("🌡️")
        if "imu" in capabilities:
            capability_icons.append("📱")
        if "gsr" in capabilities:
            capability_icons.append("⚡")

        device_display_name = f"{device_id} {''.join(capability_icons)}"
        self.device_panel.add_device(device_display_name, connected=True)
        self.statusBar().showMessage(
            f"Device {device_id} connected with capabilities: {', '.join(capabilities)}"
        )

        # Update device tab if needed
        device_index = self.get_device_index(device_id)
        if device_index >= 0:
            self.preview_tabs.set_device_tab_active(device_index)

    def on_device_disconnected(self, device_id):
        """Handle device disconnection event."""
        self.log_message(f"Device disconnected: {device_id}")
        device_index = self.get_device_index(device_id)
        if device_index >= 0:
            self.device_panel.update_device_status(device_index, connected=False)
            self.preview_tabs.clear_feed(device_index, "both")
        self.statusBar().showMessage(f"Device {device_id} disconnected")

    def on_status_received(self, device_id, status_data):
        """Handle device status update."""
        self.log_message(f"Status update from {device_id}: {status_data}")
        # Update device panel with status information
        device_index = self.get_device_index(device_id)
        if device_index >= 0:
            # Update device status in the panel
            battery = status_data.get("battery")
            recording = status_data.get("recording", False)
            status_text = f"{device_id}"
            if battery is not None:
                status_text += f" (Battery: {battery}%)"
            if recording:
                status_text += " [Recording]"

            # Update the device list item text
            if device_index < self.device_panel.get_device_count():
                item = self.device_panel.device_list.item(device_index)
                if item:
                    item.setText(status_text + " (Connected)")

    def on_ack_received(self, device_id, cmd, success, message):
        """Handle command acknowledgment from device."""
        status = "SUCCESS" if success else "FAILED"
        self.log_message(
            f"ACK from {device_id} for command '{cmd}': {status} - {message}"
        )

        # Log device acknowledgment to session logger
        if success:
            self.session_logger.log_device_ack(device_id, cmd)
            self.statusBar().showMessage(f"Command '{cmd}' completed on {device_id}")
        else:
            # Log as error if acknowledgment failed
            self.session_logger.log_error(
                "command_failed", f"Command '{cmd}' failed: {message}", device_id
            )
            self.statusBar().showMessage(
                f"Command '{cmd}' failed on {device_id}: {message}"
            )

    def on_preview_frame_received(self, device_id, frame_type, base64_data):
        """Handle preview frame from device."""
        device_index = self.get_device_index(device_id)
        if device_index >= 0:
            pixmap = self.decode_base64_to_pixmap(base64_data)
            if pixmap:
                if frame_type == "rgb":
                    self.preview_tabs.update_rgb_feed(device_index, pixmap)
                elif frame_type == "thermal":
                    self.preview_tabs.update_thermal_feed(device_index, pixmap)
                self.log_message(
                    f"Preview frame displayed from {device_id}: {frame_type}"
                )
            else:
                self.log_message(
                    f"Failed to decode frame from {device_id}: {frame_type}"
                )

    def on_sensor_data_received(self, device_id, sensor_data):
        """Handle sensor data from device."""
        self.log_message(f"Sensor data from {device_id}: {list(sensor_data.keys())}")
        
        # Add sensor data visualization
        try:
            # Update device panel with sensor data
            device_index = self.get_device_index(device_id)
            if device_index >= 0:
                # Extract key sensor values for display
                sensor_info = []
                
                # Handle IMU data
                if 'accelerometer' in sensor_data:
                    acc = sensor_data['accelerometer']
                    if isinstance(acc, dict):
                        sensor_info.append(f"Acc: X={acc.get('x', 0):.2f}, Y={acc.get('y', 0):.2f}, Z={acc.get('z', 0):.2f}")
                    else:
                        sensor_info.append(f"Acc: {acc}")
                
                if 'gyroscope' in sensor_data:
                    gyro = sensor_data['gyroscope']
                    if isinstance(gyro, dict):
                        sensor_info.append(f"Gyro: X={gyro.get('x', 0):.2f}, Y={gyro.get('y', 0):.2f}, Z={gyro.get('z', 0):.2f}")
                    else:
                        sensor_info.append(f"Gyro: {gyro}")
                
                # Handle GSR data
                if 'gsr' in sensor_data:
                    gsr = sensor_data['gsr']
                    if isinstance(gsr, (int, float)):
                        sensor_info.append(f"GSR: {gsr:.2f}")
                    elif isinstance(gsr, dict):
                        sensor_info.append(f"GSR: {gsr.get('value', 'N/A')}")
                    else:
                        sensor_info.append(f"GSR: {gsr}")
                
                # Handle temperature data
                if 'temperature' in sensor_data:
                    temp = sensor_data['temperature']
                    if isinstance(temp, (int, float)):
                        sensor_info.append(f"Temp: {temp:.1f}°C")
                    else:
                        sensor_info.append(f"Temp: {temp}")
                
                # Update device status with sensor info
                if sensor_info and device_index < self.device_panel.get_device_count():
                    item = self.device_panel.device_list.item(device_index)
                    if item:
                        current_text = item.text()
                        # Remove old sensor data if present
                        if " [Sensors:" in current_text:
                            current_text = current_text.split(" [Sensors:")[0]
                        
                        # Add new sensor data
                        sensor_summary = "; ".join(sensor_info[:2])  # Limit to first 2 sensors to avoid clutter
                        item.setText(f"{current_text} [Sensors: {sensor_summary}]")
                
                # Log sensor data to session logger if session is active
                if hasattr(self, 'session_logger') and self.session_logger.is_session_active():
                    # Convert sensor data to a format suitable for logging
                    sensor_values = {}
                    for key, value in sensor_data.items():
                        if isinstance(value, dict):
                            # Flatten nested dict
                            for subkey, subvalue in value.items():
                                sensor_values[f"{key}_{subkey}"] = subvalue
                        else:
                            sensor_values[key] = value
                    
                    # Log the sensor data
                    self.session_logger.log_sensor_data(device_id, sensor_values)
                
        except Exception as e:
            self.log_message(f"Error processing sensor data from {device_id}: {e}")

    def on_notification_received(self, device_id, event_type, event_data):
        """Handle notification from device."""
        self.log_message(f"Notification from {device_id}: {event_type} - {event_data}")
        self.statusBar().showMessage(f"Notification from {device_id}: {event_type}")

    def on_server_error(self, device_id, error_message):
        """Handle server error."""
        self.log_message(f"Server error for {device_id}: {error_message}")
        self.statusBar().showMessage(f"Error: {error_message}")

    # Webcam signal handlers
    def on_webcam_frame_ready(self, pixmap):
        """Handle new frame from webcam for preview."""
        self.preview_tabs.update_webcam_feed(pixmap)

    def on_webcam_recording_started(self, filepath):
        """Handle webcam recording started."""
        self.webcam_recording = True
        self.log_message(f"Webcam recording started: {filepath}")
        self.statusBar().showMessage("Webcam recording started")

    def on_webcam_recording_stopped(self, filepath, duration):
        """Handle webcam recording stopped."""
        self.webcam_recording = False
        self.log_message(
            f"Webcam recording stopped: {filepath} (duration: {duration:.1f}s)"
        )
        self.statusBar().showMessage(
            f"Webcam recording stopped (duration: {duration:.1f}s)"
        )

    def on_webcam_error(self, error_message):
        """Handle webcam error."""
        self.log_message(f"Webcam error: {error_message}")
        self.statusBar().showMessage(f"Webcam error: {error_message}")

    def on_webcam_status_changed(self, status_message):
        """Handle webcam status change."""
        self.log_message(f"Webcam status: {status_message}")

    # Stimulus controller signal handlers (new for milestone 3.5)
    def on_stimulus_seek_requested(self, position):
        """Handle stimulus seek request from panel."""
        # Convert percentage to milliseconds based on video duration
        duration = self.stimulus_controller.get_duration()
        if duration > 0:
            seek_position = int((position / 100.0) * duration)
            self.stimulus_controller.media_player.setPosition(seek_position)
            self.log_message(f"Stimulus seek to {position}% ({seek_position}ms)")

    def on_stimulus_screen_changed(self, screen_index):
        """Handle stimulus screen selection change."""
        self.log_message(f"Stimulus output screen changed to index {screen_index}")

    def on_start_recording_play_requested(self):
        """Handle synchronized recording start and stimulus playback."""
        try:
            # Get selected screen for stimulus display
            screen_index = self.stimulus_panel.get_selected_screen()

            # Start all recordings first
            self.log_message("Starting synchronized recording and stimulus playback...")

            # Start device recordings
            if self.server_running and self.json_server.connected_clients:
                self.json_server.broadcast_command("start_record")
                self.log_message("Sent start_record command to all devices")

            # Start PC webcam recording
            if not self.webcam_recording:
                self.webcam_capture.start_recording()
                self.log_message("Started PC webcam recording")

            # Start stimulus playback
            if self.stimulus_controller.start_stimulus_playback(screen_index):
                self.stimulus_panel.set_experiment_active(True)
                self.log_message("Experiment started successfully")
            else:
                self.log_message("Failed to start stimulus playback")

        except Exception as e:
            self.log_message(f"Error starting synchronized experiment: {str(e)}")
            QMessageBox.critical(
                self, "Experiment Start Error", f"Failed to start experiment: {str(e)}"
            )

    def on_mark_event_requested(self):
        """Handle event marker request during stimulus presentation."""
        try:
            # Get current stimulus time if available
            stim_time = None
            if hasattr(self.stimulus_controller, "get_current_position"):
                position_ms = self.stimulus_controller.get_current_position()
                if position_ms >= 0:
                    # Convert milliseconds to MM:SS.mmm format
                    minutes = position_ms // 60000
                    seconds = (position_ms % 60000) / 1000
                    stim_time = f"{minutes:02d}:{seconds:06.3f}"

            # Create marker with timestamp
            marker_label = f"Event_{len(self.stimulus_controller.event_markers) + 1 if hasattr(self.stimulus_controller, 'event_markers') else 1}"

            # Log marker to session logger
            self.session_logger.log_marker(marker_label, stim_time)

            # Add marker to stimulus controller
            self.stimulus_controller.mark_event()
            self.log_message("Event marker added")

        except Exception as e:
            self.log_message(f"Error adding event marker: {str(e)}")
            self.session_logger.log_error(
                "marker_failed", f"Failed to add event marker: {str(e)}"
            )

    def on_stimulus_status_changed(self, status_message):
        """Handle stimulus controller status changes."""
        self.statusBar().showMessage(status_message)
        self.log_message(f"Stimulus: {status_message}")

    def on_stimulus_experiment_started(self):
        """Handle stimulus experiment start notification."""
        # Get stimulus media name if available
        media_name = "unknown"
        if (
            hasattr(self.stimulus_controller, "current_media_file")
            and self.stimulus_controller.current_media_file
        ):
            media_name = os.path.basename(self.stimulus_controller.current_media_file)

        # Log stimulus playback start
        self.session_logger.log_stimulus_play(media_name)

        self.stimulus_panel.set_experiment_active(True)
        self.log_message("Stimulus experiment started")

    def on_stimulus_experiment_ended(self):
        """Handle stimulus experiment end notification."""
        try:
            # Get stimulus media name if available
            media_name = "unknown"
            if (
                hasattr(self.stimulus_controller, "current_media_file")
                and self.stimulus_controller.current_media_file
            ):
                media_name = os.path.basename(
                    self.stimulus_controller.current_media_file
                )

            # Log stimulus playback stop
            self.session_logger.log_stimulus_stop(media_name)

            # Stop all recordings
            if self.server_running and self.json_server.connected_clients:
                self.json_server.broadcast_command("stop_record")
                self.log_message("Sent stop_record command to all devices")

            # Stop PC webcam recording
            if self.webcam_recording:
                self.webcam_capture.stop_recording()
                self.log_message("Stopped PC webcam recording")

            self.stimulus_panel.set_experiment_active(False)
            self.log_message("Stimulus experiment ended - all recordings stopped")

        except Exception as e:
            self.log_message(f"Error stopping recordings: {str(e)}")
            self.session_logger.log_error(
                "stimulus_stop_failed", f"Error stopping recordings: {str(e)}"
            )

    def on_stimulus_error(self, error_message):
        """Handle stimulus controller errors."""
        self.log_message(f"Stimulus Error: {error_message}")

        # Log stimulus error to session logger
        self.session_logger.log_error("stimulus_error", error_message)

        QMessageBox.warning(self, "Stimulus Error", error_message)

    # Session logger signal handlers (new for milestone 3.8)
    def on_session_logger_session_started(self, session_id):
        """Handle session logger session started signal."""
        self.statusBar().showMessage(f"Session logging started: {session_id}")
        self.log_message(f"Session logging initialized for: {session_id}")

    def on_session_logger_session_ended(self, session_id, duration):
        """Handle session logger session ended signal."""
        self.statusBar().showMessage(
            f"Session logging completed: {session_id} ({duration:.1f}s)"
        )
        self.log_message(
            f"Session logging finalized for: {session_id} (duration: {duration:.1f}s)"
        )

        # Get session data for review dialog
        session_data = self.session_logger.get_current_session()
        if not session_data:
            # Try to get the completed session data from the last session
            # This is a fallback in case the session was already cleared
            session_data = {
                "session": session_id,
                "duration": duration,
                "status": "completed",
                "events": [],
                "devices": [],
                "calibration_files": [],
            }

        # Get session folder path
        session_folder = None
        if hasattr(self.session_manager, "get_session_folder"):
            session_folder = self.session_manager.get_session_folder()

        # Show completion message with option to review
        reply = QMessageBox.question(
            self,
            "Session Complete",
            f"Session {session_id} completed successfully.\n"
            f"Duration: {duration:.1f} seconds\n"
            f"All session data and logs have been saved.\n\n"
            f"Would you like to review the session data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        # Show session review dialog if requested
        if reply == QMessageBox.Yes and session_folder:
            try:
                show_session_review_dialog(session_data, str(session_folder), self)
                self.log_message(f"Session review dialog shown for: {session_id}")
            except Exception as e:
                self.log_message(f"Failed to show session review dialog: {str(e)}")
                QMessageBox.warning(
                    self,
                    "Review Dialog Error",
                    f"Failed to open session review dialog.\n\nError: {str(e)}",
                )
        elif reply == QMessageBox.Yes and not session_folder:
            QMessageBox.information(
                self,
                "Review Not Available",
                "Session review is not available because the session folder could not be located.",
            )

    def on_session_logger_error(self, error_type, error_message):
        """Handle session logger error signal."""
        self.log_message(f"Session Logger ERROR ({error_type}): {error_message}")
        # Highlight errors in status bar
        self.statusBar().showMessage(f"Session logging error: {error_type}")

    # Utility methods
    def get_device_index(self, device_id):
        """Get device index for device_id (simple mapping for now)."""
        # Simple mapping: Device 1 -> index 0, Device 2 -> index 1
        if "1" in device_id or device_id.endswith("_1"):
            return 0
        elif "2" in device_id or device_id.endswith("_2"):
            return 1
        else:
            # For other devices, use a simple hash-based approach
            return hash(device_id) % 2

    def decode_base64_to_pixmap(self, base64_data):
        """Decode base64 image data to QPixmap."""
        try:
            # Remove data URL prefix if present
            if base64_data.startswith("data:image/"):
                base64_data = base64_data.split(",", 1)[1]

            # Decode base64 to bytes
            image_data = base64.b64decode(base64_data)

            # Create QPixmap from image data
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                return pixmap
            else:
                self.log_message("Failed to load pixmap from image data")
                return None

        except Exception as e:
            self.log_message(f"Error decoding base64 image: {str(e)}")
            return None

    # Toolbar action handlers (updated to use real server)
    def handle_connect(self):
        """Handle connect button press - start the server."""
        if not self.server_running:
            self.log_message("Starting JSON socket server...")
            self.json_server.start()
            self.server_running = True
            self.statusBar().showMessage(
                "Server started - waiting for device connections..."
            )
        else:
            self.statusBar().showMessage("Server is already running")

    def handle_disconnect(self):
        """Handle disconnect button press - stop the server."""
        if self.server_running:
            self.log_message("Stopping JSON socket server...")
            self.json_server.stop_server()
            self.server_running = False
            self.device_panel.clear_devices()
            self.preview_tabs.clear_all_feeds()
            self.statusBar().showMessage("Server stopped - all devices disconnected")
        else:
            self.statusBar().showMessage("Server is not running")

    def handle_start(self):
        """Handle start session button press - send start command to all devices and start webcam."""
        if self.server_running:
            # Create new session
            session_info = self.session_manager.create_session()
            session_id = session_info["session_id"]
            self.current_session_id = session_id

            # Get connected devices for session logging
            connected_devices = []
            if hasattr(self.json_server, "connected_devices"):
                connected_devices = [
                    {"id": device_id, "type": "android_phone"}
                    for device_id in self.json_server.connected_devices.keys()
                ]

            # Add PC webcam to devices list
            connected_devices.append({"id": "pc_webcam", "type": "pc_webcam"})

            # Start comprehensive session logging
            self.session_logger.start_session(
                session_name=session_id, devices=connected_devices
            )

            # Log PC webcam device connection
            self.session_logger.log_device_connected(
                "pc_webcam", "pc_webcam", ["video_recording"]
            )

            # Add PC webcam as a device to the session
            self.session_manager.add_device_to_session(
                "pc_webcam", "pc_webcam", ["video_recording"]
            )

            # Set webcam output directory to session folder
            session_folder = self.session_manager.get_session_folder()
            if session_folder:
                self.webcam_capture.set_output_directory(str(session_folder))

            # Start webcam recording
            if not self.webcam_previewing:
                self.webcam_capture.start_preview()
                self.webcam_previewing = True

            webcam_started = self.webcam_capture.start_recording(session_id)

            # Prepare device list for recording start logging
            device_ids = ["pc_webcam"]
            if hasattr(self.json_server, "connected_devices"):
                device_ids.extend(self.json_server.connected_devices.keys())

            # Log recording start command
            self.session_logger.log_recording_start(device_ids, session_id)

            # Send start command to devices
            command = create_command_message("start_recording")
            count = self.json_server.broadcast_command(command)

            if webcam_started:
                self.log_message(
                    f"Session {session_id} started - webcam recording and {count} devices"
                )
                self.statusBar().showMessage(
                    f"Session started: webcam + {count} devices"
                )
            else:
                self.log_message(
                    f"Session {session_id} started - {count} devices (webcam failed)"
                )
                self.statusBar().showMessage(
                    f"Session started: {count} devices (webcam failed)"
                )
                # Log webcam error
                self.session_logger.log_error(
                    "webcam_start_failed", "PC webcam failed to start recording"
                )
        else:
            self.statusBar().showMessage("Server not running - cannot start recording")

    def handle_stop(self):
        """Handle stop button press - send stop command to all devices and stop webcam."""
        if self.server_running:
            # Log recording stop command
            self.session_logger.log_recording_stop()

            # Stop webcam recording
            webcam_filepath = self.webcam_capture.stop_recording()

            # Add webcam file to session if recording was successful
            if webcam_filepath and self.session_manager.get_current_session():
                try:
                    file_size = (
                        os.path.getsize(webcam_filepath)
                        if os.path.exists(webcam_filepath)
                        else None
                    )
                    self.session_manager.add_file_to_session(
                        "pc_webcam", "webcam_video", webcam_filepath, file_size
                    )

                    # Log file received from PC webcam
                    filename = (
                        os.path.basename(webcam_filepath)
                        if webcam_filepath
                        else "unknown"
                    )
                    self.session_logger.log_file_received(
                        "pc_webcam", filename, file_size, "webcam_video"
                    )

                except Exception as e:
                    self.log_message(f"Failed to add webcam file to session: {e}")
                    self.session_logger.log_error(
                        "file_save_failed",
                        f"Failed to add webcam file to session: {e}",
                        "pc_webcam",
                    )

            # Send stop command to devices
            command = create_command_message("stop_recording")
            count = self.json_server.broadcast_command(command)

            # End the session
            completed_session = self.session_manager.end_session()

            # End session logging
            if self.session_logger.is_session_active():
                self.session_logger.end_session()

            if webcam_filepath and completed_session:
                self.log_message(
                    f"Session {completed_session['session_id']} completed - webcam and {count} devices (duration: {completed_session['duration']:.1f}s)"
                )
                self.statusBar().showMessage(
                    f"Session completed: webcam + {count} devices"
                )
            elif completed_session:
                self.log_message(
                    f"Session {completed_session['session_id']} completed - {count} devices (no webcam recording)"
                )
                self.statusBar().showMessage(f"Session completed: {count} devices")
            else:
                self.log_message(
                    f"Recording stopped - {count} devices (no active session)"
                )
                self.statusBar().showMessage(f"Recording stopped: {count} devices")

            # Milestone 3.6: Trigger automatic file collection after recording stops
            if completed_session and completed_session.get("session_id"):
                session_id = completed_session["session_id"]
                self.log_message(
                    f"Initiating automatic file collection for session {session_id}"
                )
                # Add delay to allow devices to finalize their files before requesting transfer
                QTimer.singleShot(2000, lambda: self.collect_session_files(session_id))

            self.current_session_id = None
        else:
            self.statusBar().showMessage("Server not running - cannot stop recording")

    def collect_session_files(self, session_id: str):
        """
        Collect all files from devices for the completed session - Milestone 3.6

        Args:
            session_id: The session identifier for which to collect files
        """
        try:
            if not self.server_running or not self.json_server:
                self.log_message(f"Cannot collect session files: server not running")
                return

            # Request all session files from connected devices
            file_count = self.json_server.request_all_session_files(session_id)

            if file_count > 0:
                self.log_message(
                    f"Initiated file collection for session {session_id}: {file_count} file requests sent"
                )
                self.statusBar().showMessage(
                    f"Collecting session files... ({file_count} requests)"
                )
            else:
                self.log_message(
                    f"No files to collect for session {session_id} (no connected devices or no expected files)"
                )
                self.statusBar().showMessage("No session files to collect")

        except Exception as e:
            self.log_message(f"Error collecting session files: {e}")
            self.statusBar().showMessage("Error collecting session files")

    def open_calibration_dialog(self):
        """Open the comprehensive calibration dialog."""
        try:
            if not self.server_running:
                QMessageBox.warning(
                    self,
                    "Server Not Running",
                    "Please start the server before opening calibration dialog.",
                )
                return

            # Create and show calibration dialog
            dialog = CalibrationDialog(self.json_server, self)

            # Connect signals for overlay functionality
            dialog.overlay_toggled.connect(self.handle_overlay_toggle)
            dialog.calibration_completed.connect(self.handle_calibration_completed)

            # Show dialog
            result = dialog.exec_()

            if result == dialog.Accepted:
                self.log_message("Calibration dialog completed successfully")
                self.statusBar().showMessage("Calibration completed")
            else:
                self.log_message("Calibration dialog cancelled")
                self.statusBar().showMessage("Calibration cancelled")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to open calibration dialog: {str(e)}"
            )
            self.log_message(f"Error opening calibration dialog: {str(e)}")

    def handle_overlay_toggle(self, device_id: str, enabled: bool):
        """Handle thermal overlay toggle from calibration dialog."""
        try:
            self.log_message(
                f"Thermal overlay {'enabled' if enabled else 'disabled'} for {device_id}"
            )
            
            # Implement overlay functionality in preview panel
            device_index = self.get_device_index(device_id)
            if device_index >= 0 and hasattr(self.preview_tabs, 'set_thermal_overlay'):
                # Enable/disable thermal overlay for the specific device
                self.preview_tabs.set_thermal_overlay(device_index, enabled)
                
                # Update status message
                overlay_status = "enabled" if enabled else "disabled"
                self.statusBar().showMessage(f"Thermal overlay {overlay_status} for {device_id}")
                
                # Log overlay change to session logger if session is active
                if hasattr(self, 'session_logger') and self.session_logger.is_session_active():
                    self.session_logger.log_calibration_event(
                        'overlay_toggle',
                        device_id=device_id,
                        overlay_enabled=enabled
                    )
            else:
                # Fallback if preview panel doesn't support overlay yet
                self.log_message(f"Preview panel overlay not yet implemented for {device_id}")
                self.statusBar().showMessage("Thermal overlay feature not yet fully implemented")

        except Exception as e:
            self.log_message(f"Error toggling overlay: {str(e)}")
            self.statusBar().showMessage(f"Error toggling overlay: {str(e)}")

    def handle_calibration_completed(self, device_id: str, result):
        """Handle calibration completion from dialog."""
        try:
            self.log_message(f"Calibration completed for {device_id}")
            
            # Store calibration results for use in main application
            # Save calibration results to session if active
            if hasattr(self, 'session_manager') and self.session_manager.get_current_session():
                try:
                    # Create calibration result data structure
                    calibration_data = {
                        'device_id': device_id,
                        'timestamp': result.get('timestamp') if isinstance(result, dict) else None,
                        'calibration_type': result.get('type', 'thermal_rgb') if isinstance(result, dict) else 'thermal_rgb',
                        'result': result,
                        'status': 'completed'
                    }
                    
                    # Add calibration data to session
                    self.session_manager.add_calibration_result(device_id, calibration_data)
                    
                    # Log calibration completion to session logger
                    if hasattr(self, 'session_logger') and self.session_logger.is_session_active():
                        self.session_logger.log_calibration_event(
                            'calibration_completed',
                            device_id=device_id,
                            calibration_type=calibration_data['calibration_type'],
                            result_summary=str(result)[:100]  # Truncate for logging
                        )
                    
                    self.statusBar().showMessage(f"Calibration results saved for {device_id}")
                    
                except Exception as e:
                    self.log_message(f"Error saving calibration results: {e}")
                    self.statusBar().showMessage(f"Error saving calibration results")
            else:
                # Store in a temporary calibration results cache if no active session
                if not hasattr(self, 'calibration_results_cache'):
                    self.calibration_results_cache = {}
                
                self.calibration_results_cache[device_id] = {
                    'result': result,
                    'timestamp': self.get_current_timestamp(),
                    'status': 'completed'
                }
                
                self.log_message(f"Calibration results cached for {device_id} (no active session)")
                self.statusBar().showMessage(f"Calibration completed for {device_id} (cached)")

        except Exception as e:
            self.log_message(f"Error handling calibration completion: {str(e)}")
            self.statusBar().showMessage(f"Error handling calibration completion")
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def closeEvent(self, event):
        """Handle application close event."""
        if self.server_running:
            self.log_message("Shutting down server before closing...")
            self.json_server.stop_server()

        # Clean up webcam resources
        if self.webcam_capture:
            self.log_message("Cleaning up webcam resources...")
            self.webcam_capture.cleanup()

        event.accept()
