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

# Import network server
from network.device_server import JsonSocketServer, create_command_message


class MainWindow(QMainWindow):
    """Main window for the Multi-Sensor Recording System Controller."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize network server
        self.json_server = JsonSocketServer()
        self.server_running = False
        
        # Initialize UI components
        self.init_ui()
        
        # Connect server signals to GUI handlers
        self.connect_server_signals()
        
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
        
        # Capture Calibration action
        calib_action = QAction("Capture Calibration", self)
        calib_action.triggered.connect(self.handle_capture_calibration)
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
        """Handle start session button press - send start command to all devices."""
        if self.server_running:
            command = create_command_message('start_recording')
            count = self.json_server.broadcast_command(command)
            self.log_message(f"Start recording command sent to {count} devices")
            self.statusBar().showMessage(f"Recording started on {count} devices")
        else:
            self.statusBar().showMessage("Server not running - cannot start recording")
    
    def handle_stop(self):
        """Handle stop button press - send stop command to all devices."""
        if self.server_running:
            command = create_command_message('stop_recording')
            count = self.json_server.broadcast_command(command)
            self.log_message(f"Stop recording command sent to {count} devices")
            self.statusBar().showMessage(f"Recording stopped on {count} devices")
        else:
            self.statusBar().showMessage("Server not running - cannot stop recording")
    
    def handle_capture_calibration(self):
        """Handle capture calibration button press - send calibration command."""
        if self.server_running:
            command = create_command_message('capture_calibration')
            count = self.json_server.broadcast_command(command)
            self.log_message(f"Calibration capture command sent to {count} devices")
            self.statusBar().showMessage(f"Calibration capture initiated on {count} devices")
        else:
            self.statusBar().showMessage("Server not running - cannot capture calibration")
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.server_running:
            self.log_message("Shutting down server before closing...")
            self.json_server.stop_server()
        event.accept()
