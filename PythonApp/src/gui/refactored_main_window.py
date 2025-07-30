"""
Refactored Main Window for the Multi-Sensor Recording System Controller.

This module implements the refactored MainWindow class that follows the MVC pattern
by only handling UI events and delegating all business logic to the MainController.
This eliminates the "God Controller" anti-pattern by separating UI concerns from
business logic.

Created: 2025-07-30
Author: Junie (Architectural Refactoring)
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

# Import UI components
from .calibration_dialog import CalibrationDialog
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .session_review_dialog import show_session_review_dialog
from .stimulus_panel import StimulusControlPanel


class RefactoredMainWindow(QMainWindow):
    """
    Refactored Main window for the Multi-Sensor Recording System Controller.
    
    This class now follows the MVC pattern by:
    - Only handling UI events and rendering
    - Delegating all business logic to the MainController
    - Using dependency injection to receive the controller
    - Maintaining loose coupling with the business layer
    """

    def __init__(self):
        """Initialize the main window UI components only."""
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1200, 800)

        # Controller (injected via dependency injection)
        self.controller = None
        
        # UI state (view-specific state only)
        self.device_panels = {}  # device_id -> DeviceStatusPanel
        self.log_messages = []
        
        # Initialize UI components
        self.init_ui()
        
        # Note: Signal connections will be made after controller injection

    def set_controller(self, controller):
        """
        Inject the MainController dependency.
        
        This method implements dependency injection by providing the view
        with a controller to handle all business logic operations.
        
        Args:
            controller: MainController instance
        """
        self.controller = controller
        
        # Connect controller signals to UI handlers
        self._connect_controller_signals()
        
        # Initialize placeholder data
        self.init_placeholder_data()

    def _connect_controller_signals(self):
        """Connect controller signals to UI update methods."""
        if not self.controller:
            raise RuntimeError("Controller must be injected before connecting signals")
        
        # Server status signals
        self.controller.server_status_changed.connect(self._on_server_status_changed)
        
        # Device management signals
        self.controller.device_connected.connect(self._on_device_connected)
        self.controller.device_disconnected.connect(self._on_device_disconnected)
        self.controller.device_status_received.connect(self._on_device_status_received)
        
        # Data signals
        self.controller.preview_frame_received.connect(self._on_preview_frame_received)
        self.controller.webcam_frame_ready.connect(self._on_webcam_frame_ready)
        self.controller.sensor_data_received.connect(self._on_sensor_data_received)
        
        # Event signals
        self.controller.recording_started.connect(self._on_recording_started)
        self.controller.recording_stopped.connect(self._on_recording_stopped)
        self.controller.calibration_completed.connect(self._on_calibration_completed)
        
        # Status signals
        self.controller.webcam_status_changed.connect(self._on_webcam_status_changed)
        self.controller.session_status_changed.connect(self._on_session_status_changed)
        
        # Error signals
        self.controller.error_occurred.connect(self._on_error_occurred)

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

        # Stop Session action
        stop_action = QAction("Stop Session", self)
        stop_action.triggered.connect(self.handle_stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # Calibration action
        calibration_action = QAction("Calibration", self)
        calibration_action.triggered.connect(self.open_calibration_dialog)
        toolbar.addAction(calibration_action)

    def create_central_widget(self):
        """Create the central widget and layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel for device status
        self.device_status_panel = DeviceStatusPanel()
        main_layout.addWidget(self.device_status_panel, 1)

        # Right panel for preview
        self.preview_panel = PreviewPanel()
        main_layout.addWidget(self.preview_panel, 2)

        # Bottom panel for stimulus controls
        self.stimulus_panel = StimulusControlPanel()
        
        # Create vertical layout for right side
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.preview_panel, 3)
        right_layout.addWidget(self.stimulus_panel, 1)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 2)

    def create_log_dock(self):
        """Create the log dock widget."""
        self.log_dock = QDockWidget("System Log", self)
        self.log_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        # Create log text widget
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)  # Limit log size

        self.log_dock.setWidget(self.log_text)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        # Initially hide the log dock
        self.log_dock.hide()

    def toggle_log_dock(self):
        """Toggle the visibility of the log dock."""
        if self.log_dock.isVisible():
            self.log_dock.hide()
            self.show_log_action.setText("Show Log")
            self.show_log_action.setChecked(False)
        else:
            self.log_dock.show()
            self.show_log_action.setText("Hide Log")
            self.show_log_action.setChecked(True)

    def log_message(self, message):
        """
        Add a message to the log display.
        
        Args:
            message (str): Message to log
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_messages.append(formatted_message)
        self.log_text.appendPlainText(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def create_status_bar(self):
        """Create the status bar."""
        self.statusBar().showMessage("Ready")

    def init_placeholder_data(self):
        """Initialize placeholder data for UI components."""
        # This method can be used to set up initial UI state
        self.log_message("Multi-Sensor Recording System Controller initialized")
        self.log_message("Waiting for device connections...")

    # UI Event Handlers (delegate to controller)

    def handle_connect(self):
        """Handle connect button click - delegate to controller."""
        if not self.controller:
            self.log_message("Error: Controller not initialized")
            return
        
        self.log_message("Starting server...")
        success = self.controller.start_server()
        if success:
            self.log_message("Server started successfully")
        else:
            self.log_message("Failed to start server")

    def handle_disconnect(self):
        """Handle disconnect button click - delegate to controller."""
        if not self.controller:
            self.log_message("Error: Controller not initialized")
            return
        
        self.log_message("Stopping server...")
        success = self.controller.stop_server()
        if success:
            self.log_message("Server stopped successfully")
        else:
            self.log_message("Failed to stop server")

    def handle_start(self):
        """Handle start session button click - delegate to controller."""
        if not self.controller:
            self.log_message("Error: Controller not initialized")
            return
        
        self.log_message("Starting recording session...")
        
        # Start webcam preview if not already running
        if not self.controller.is_webcam_previewing():
            self.controller.start_webcam_preview()
        
        # Start session
        session_id = self.controller.start_session()
        if session_id:
            # Start webcam recording
            self.controller.start_webcam_recording(session_id)
            
            # Send start command to all devices
            self.controller.broadcast_command("START_RECORDING", {"session_id": session_id})
            
            self.log_message(f"Recording session started: {session_id}")
        else:
            self.log_message("Failed to start recording session")

    def handle_stop(self):
        """Handle stop session button click - delegate to controller."""
        if not self.controller:
            self.log_message("Error: Controller not initialized")
            return
        
        current_session = self.controller.get_current_session_id()
        if not current_session:
            self.log_message("No active session to stop")
            return
        
        self.log_message("Stopping recording session...")
        
        # Send stop command to all devices
        self.controller.broadcast_command("STOP_RECORDING")
        
        # Stop webcam recording
        self.controller.stop_webcam_recording()
        
        # Stop session
        success = self.controller.stop_session()
        if success:
            self.log_message(f"Recording session stopped: {current_session}")
            
            # Show session review dialog
            self._show_session_review(current_session)
        else:
            self.log_message("Failed to stop recording session")

    def open_calibration_dialog(self):
        """Open calibration dialog - delegate to controller."""
        if not self.controller:
            self.log_message("Error: Controller not initialized")
            return
        
        connected_devices = self.controller.get_connected_devices()
        if not connected_devices:
            QMessageBox.warning(
                self,
                "No Devices",
                "No devices are currently connected. Please connect devices before calibration."
            )
            return
        
        # Create and show calibration dialog
        dialog = CalibrationDialog(connected_devices, self)
        if dialog.exec_() == CalibrationDialog.Accepted:
            selected_devices = dialog.get_selected_devices()
            calibration_params = dialog.get_calibration_parameters()
            
            self.log_message(f"Starting calibration for devices: {selected_devices}")
            
            # Send calibration command to selected devices
            for device_id in selected_devices:
                self.controller.send_command_to_device(
                    device_id, 
                    "START_CALIBRATION", 
                    calibration_params
                )

    def show_settings_dialog(self):
        """Show settings dialog."""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            "Multi-Sensor Recording System Controller\n\n"
            "Refactored Architecture with MVC Pattern\n"
            "Version: 2.0 (Architectural Refactoring)\n"
            "Date: 2025-07-30"
        )

    # Controller Signal Handlers (UI updates only)

    def _on_server_status_changed(self, is_running):
        """Handle server status changes."""
        status = "Running" if is_running else "Stopped"
        self.statusBar().showMessage(f"Server: {status}")
        self.log_message(f"Server status changed: {status}")

    def _on_device_connected(self, device_id, capabilities):
        """Handle device connection."""
        self.log_message(f"Device connected: {device_id} with capabilities: {capabilities}")
        
        # Create device panel if not exists
        if device_id not in self.device_panels:
            device_panel = DeviceStatusPanel()
            device_panel.set_device_info(device_id, capabilities)
            self.device_panels[device_id] = device_panel
            self.device_status_panel.add_device_panel(device_id, device_panel)

    def _on_device_disconnected(self, device_id):
        """Handle device disconnection."""
        self.log_message(f"Device disconnected: {device_id}")
        
        # Remove device panel
        if device_id in self.device_panels:
            self.device_status_panel.remove_device_panel(device_id)
            del self.device_panels[device_id]

    def _on_device_status_received(self, device_id, status_data):
        """Handle device status updates."""
        if device_id in self.device_panels:
            self.device_panels[device_id].update_status(status_data)

    def _on_preview_frame_received(self, device_id, frame_type, base64_data):
        """Handle preview frame updates."""
        try:
            pixmap = self.decode_base64_to_pixmap(base64_data)
            if pixmap:
                self.preview_panel.update_device_preview(device_id, frame_type, pixmap)
        except Exception as e:
            self.log_message(f"Error updating preview for {device_id}: {e}")

    def _on_webcam_frame_ready(self, pixmap):
        """Handle webcam frame updates."""
        self.preview_panel.update_webcam_preview(pixmap)

    def _on_sensor_data_received(self, device_id, sensor_data):
        """Handle sensor data updates."""
        # Update device panel with sensor data
        if device_id in self.device_panels:
            self.device_panels[device_id].update_sensor_data(sensor_data)

    def _on_recording_started(self, session_id):
        """Handle recording start."""
        self.log_message(f"Recording started for session: {session_id}")
        self.statusBar().showMessage(f"Recording: {session_id}")

    def _on_recording_stopped(self, session_id, duration):
        """Handle recording stop."""
        self.log_message(f"Recording stopped for session: {session_id} (duration: {duration:.1f}s)")
        self.statusBar().showMessage("Ready")

    def _on_calibration_completed(self, device_id, result):
        """Handle calibration completion."""
        success = result.get('success', False)
        message = result.get('message', 'Unknown result')
        
        if success:
            self.log_message(f"Calibration completed successfully for {device_id}: {message}")
            QMessageBox.information(
                self,
                "Calibration Complete",
                f"Calibration completed successfully for {device_id}\n\n{message}"
            )
        else:
            self.log_message(f"Calibration failed for {device_id}: {message}")
            QMessageBox.warning(
                self,
                "Calibration Failed",
                f"Calibration failed for {device_id}\n\n{message}"
            )

    def _on_webcam_status_changed(self, status_message):
        """Handle webcam status changes."""
        self.log_message(f"Webcam: {status_message}")

    def _on_session_status_changed(self, session_id, is_active):
        """Handle session status changes."""
        status = "Active" if is_active else "Inactive"
        self.log_message(f"Session {session_id}: {status}")

    def _on_error_occurred(self, component, error_message):
        """Handle error messages."""
        self.log_message(f"ERROR [{component}]: {error_message}")
        
        # Show critical errors in message box
        if "CRITICAL" in error_message.upper() or "FATAL" in error_message.upper():
            QMessageBox.critical(
                self,
                f"Critical Error - {component}",
                error_message
            )

    # Utility Methods

    def decode_base64_to_pixmap(self, base64_data):
        """
        Decode base64 image data to QPixmap.
        
        Args:
            base64_data (str): Base64 encoded image data
            
        Returns:
            QPixmap: Decoded pixmap or None if failed
        """
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            
            # Create pixmap from image data
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                return pixmap
            else:
                self.log_message("Failed to load pixmap from image data")
                return None
                
        except Exception as e:
            self.log_message(f"Error decoding base64 image: {e}")
            return None

    def _show_session_review(self, session_id):
        """Show session review dialog."""
        try:
            # Collect session files through controller
            # Note: This would need to be implemented in the controller
            session_files = []  # TODO: Get from controller
            
            show_session_review_dialog(session_id, session_files, self)
            
        except Exception as e:
            self.log_message(f"Error showing session review: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Ask for confirmation if recording is active
            if self.controller and self.controller.get_current_session_id():
                reply = QMessageBox.question(
                    self,
                    "Recording Active",
                    "A recording session is currently active. Do you want to stop it and exit?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.handle_stop()
                else:
                    event.ignore()
                    return
            
            # Cleanup controller
            if self.controller:
                self.controller.cleanup()
            
            self.log_message("Application shutting down...")
            event.accept()
            
        except Exception as e:
            self.log_message(f"Error during shutdown: {e}")
            event.accept()  # Accept anyway to prevent hanging