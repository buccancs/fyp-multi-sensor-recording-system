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

import os
import base64
from io import BytesIO
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QAction, QMessageBox,
    QDockWidget, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

# Import modular components
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .stimulus_panel import StimulusControlPanel
from .calibration_dialog import CalibrationDialog

# Import network server
from network.device_server import JsonSocketServer, create_command_message

# Import webcam capture
from webcam.webcam_capture import WebcamCapture

# Import session manager
from session.session_manager import SessionManager


class MainWindow(QMainWindow):
    """Main window for the Multi-Sensor Recording System Controller."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize network server
        self.json_server = JsonSocketServer()
        self.server_running = False
        
        # Initialize webcam capture
        self.webcam_capture = WebcamCapture()
        self.webcam_previewing = False
        self.webcam_recording = False
        
        # Initialize session manager
        self.session_manager = SessionManager()
        self.current_session_id = None
        
        # Initialize UI components
        self.init_ui()
        
        # Connect server signals to GUI handlers
        self.connect_server_signals()
        
        # Connect webcam signals to GUI handlers
        self.connect_webcam_signals()
        
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
        """Create the log dock widget."""
        self.log_dock = QDockWidget("Log", self)
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(200)  # Limit height
        
        # Set some styling for the log widget
        self.log_widget.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                border: 1px solid #555555;
            }
        """)
        
        self.log_dock.setWidget(self.log_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        
        # Initially hide the log dock
        self.log_dock.hide()
        
        # Add initial log message
        self.log_message("Application started - Log system initialized")
    
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
        Add a timestamped message to the log.
        
        Args:
            message (str): The message to log
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_widget.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
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
        
        self.log_message("Webcam signals connected to GUI handlers")
    
    def init_placeholder_data(self):
        """Initialize placeholder data for testing."""
        # Placeholder data is now handled by the modular components
        pass
    
    # Menu action handlers
    def show_settings_dialog(self):
        """Show settings dialog (placeholder)."""
        self.log_message("Settings menu item selected - showing placeholder dialog")
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")
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
            "Date: 2025-07-29"
        )
        self.log_message("About dialog closed")
    
    # Server signal handlers
    def on_device_connected(self, device_id, capabilities):
        """Handle device connection event."""
        self.log_message(f"Device connected: {device_id} with capabilities: {capabilities}")
        
        # Create device display name with capability indicators
        capability_icons = []
        if 'camera' in capabilities:
            capability_icons.append('📷')
        if 'thermal' in capabilities:
            capability_icons.append('🌡️')
        if 'imu' in capabilities:
            capability_icons.append('📱')
        if 'gsr' in capabilities:
            capability_icons.append('⚡')
        
        device_display_name = f"{device_id} {''.join(capability_icons)}"
        self.device_panel.add_device(device_display_name, connected=True)
        self.statusBar().showMessage(f"Device {device_id} connected with capabilities: {', '.join(capabilities)}")
        
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
            battery = status_data.get('battery')
            recording = status_data.get('recording', False)
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
        self.log_message(f"ACK from {device_id} for command '{cmd}': {status} - {message}")
        if not success:
            self.statusBar().showMessage(f"Command '{cmd}' failed on {device_id}: {message}")
        else:
            self.statusBar().showMessage(f"Command '{cmd}' completed on {device_id}")
    
    def on_preview_frame_received(self, device_id, frame_type, base64_data):
        """Handle preview frame from device."""
        device_index = self.get_device_index(device_id)
        if device_index >= 0:
            pixmap = self.decode_base64_to_pixmap(base64_data)
            if pixmap:
                if frame_type == 'rgb':
                    self.preview_tabs.update_rgb_feed(device_index, pixmap)
                elif frame_type == 'thermal':
                    self.preview_tabs.update_thermal_feed(device_index, pixmap)
                self.log_message(f"Preview frame displayed from {device_id}: {frame_type}")
            else:
                self.log_message(f"Failed to decode frame from {device_id}: {frame_type}")
    
    def on_sensor_data_received(self, device_id, sensor_data):
        """Handle sensor data from device."""
        self.log_message(f"Sensor data from {device_id}: {list(sensor_data.keys())}")
        # TODO: Add sensor data visualization in future milestone
    
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
        self.log_message(f"Webcam recording stopped: {filepath} (duration: {duration:.1f}s)")
        self.statusBar().showMessage(f"Webcam recording stopped (duration: {duration:.1f}s)")
    
    def on_webcam_error(self, error_message):
        """Handle webcam error."""
        self.log_message(f"Webcam error: {error_message}")
        self.statusBar().showMessage(f"Webcam error: {error_message}")
    
    def on_webcam_status_changed(self, status_message):
        """Handle webcam status change."""
        self.log_message(f"Webcam status: {status_message}")
    
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
            if base64_data.startswith('data:image/'):
                base64_data = base64_data.split(',', 1)[1]
            
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
            self.statusBar().showMessage("Server started - waiting for device connections...")
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
            
            # Add PC webcam as a device to the session
            self.session_manager.add_device_to_session("pc_webcam", "pc_webcam", ["video_recording"])
            
            # Set webcam output directory to session folder
            session_folder = self.session_manager.get_session_folder()
            if session_folder:
                self.webcam_capture.set_output_directory(str(session_folder))
            
            # Start webcam recording
            if not self.webcam_previewing:
                self.webcam_capture.start_preview()
                self.webcam_previewing = True
            
            webcam_started = self.webcam_capture.start_recording(session_id)
            
            # Send start command to devices
            command = create_command_message('start_recording')
            count = self.json_server.broadcast_command(command)
            
            if webcam_started:
                self.log_message(f"Session {session_id} started - webcam recording and {count} devices")
                self.statusBar().showMessage(f"Session started: webcam + {count} devices")
            else:
                self.log_message(f"Session {session_id} started - {count} devices (webcam failed)")
                self.statusBar().showMessage(f"Session started: {count} devices (webcam failed)")
        else:
            self.statusBar().showMessage("Server not running - cannot start recording")
    
    def handle_stop(self):
        """Handle stop button press - send stop command to all devices and stop webcam."""
        if self.server_running:
            # Stop webcam recording
            webcam_filepath = self.webcam_capture.stop_recording()
            
            # Add webcam file to session if recording was successful
            if webcam_filepath and self.session_manager.get_current_session():
                try:
                    file_size = os.path.getsize(webcam_filepath) if os.path.exists(webcam_filepath) else None
                    self.session_manager.add_file_to_session("pc_webcam", "webcam_video", webcam_filepath, file_size)
                except Exception as e:
                    self.log_message(f"Failed to add webcam file to session: {e}")
            
            # Send stop command to devices
            command = create_command_message('stop_recording')
            count = self.json_server.broadcast_command(command)
            
            # End the session
            completed_session = self.session_manager.end_session()
            
            if webcam_filepath and completed_session:
                self.log_message(f"Session {completed_session['session_id']} completed - webcam and {count} devices (duration: {completed_session['duration']:.1f}s)")
                self.statusBar().showMessage(f"Session completed: webcam + {count} devices")
            elif completed_session:
                self.log_message(f"Session {completed_session['session_id']} completed - {count} devices (no webcam recording)")
                self.statusBar().showMessage(f"Session completed: {count} devices")
            else:
                self.log_message(f"Recording stopped - {count} devices (no active session)")
                self.statusBar().showMessage(f"Recording stopped: {count} devices")
            
            self.current_session_id = None
        else:
            self.statusBar().showMessage("Server not running - cannot stop recording")
    
    def open_calibration_dialog(self):
        """Open the comprehensive calibration dialog."""
        try:
            if not self.server_running:
                QMessageBox.warning(self, "Server Not Running", 
                                  "Please start the server before opening calibration dialog.")
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
            QMessageBox.critical(self, "Error", f"Failed to open calibration dialog: {str(e)}")
            self.log_message(f"Error opening calibration dialog: {str(e)}")
            
    def handle_overlay_toggle(self, device_id: str, enabled: bool):
        """Handle thermal overlay toggle from calibration dialog."""
        try:
            self.log_message(f"Thermal overlay {'enabled' if enabled else 'disabled'} for {device_id}")
            # TODO: Implement overlay functionality in preview panel
            # This would integrate with the preview panel to show/hide thermal overlay
            
        except Exception as e:
            self.log_message(f"Error toggling overlay: {str(e)}")
            
    def handle_calibration_completed(self, device_id: str, result):
        """Handle calibration completion from dialog."""
        try:
            self.log_message(f"Calibration completed for {device_id}")
            # TODO: Store calibration results for use in main application
            # This could be integrated with session management
            
        except Exception as e:
            self.log_message(f"Error handling calibration completion: {str(e)}")
    
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
