"""
Simplified Main Window for Multi-Sensor Recording System Controller

This module implements a clean, tabbed interface that replaces the complex
navigation structure with a simple, intuitive design focused on the main
functional areas: Recording, Devices, Calibration, and Files.

Author: Multi-Sensor Recording System Team
Date: 2025-08-01
Purpose: Navigation Architecture Redesign - Simplicity and Cleanliness
"""

import logging
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QSplitter,
    QMessageBox,
    QAction,
    QMenuBar,
    QStatusBar,
    QFrame
)

# Import essential components
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .calibration_dialog import CalibrationDialog
from .common_components import (
    ModernButton, ModernGroupBox, StatusIndicator, 
    ProgressIndicator, LogViewer, ConnectionManager
)


class SimplifiedMainWindow(QMainWindow):
    """
    Simplified main window with clean tabbed interface.
    
    Replaces the complex multi-panel architecture with a simple
    tab-based navigation focusing on core functionality.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Window setup
        self.setWindowTitle("Multi-Sensor Recording System - Simplified")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize core components
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        self.logger.info("Simplified main window initialized")

    def setup_ui(self):
        """Setup the simplified tabbed user interface."""
        # Central widget with tab layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs for main functional areas
        self.create_recording_tab()
        self.create_devices_tab()
        self.create_calibration_tab()
        self.create_files_tab()
        
        self.logger.info("Simplified UI setup completed")

    def create_recording_tab(self):
        """Create the main recording control tab using modern components."""
        recording_widget = QWidget()
        layout = QVBoxLayout(recording_widget)
        
        # Title using modern styling
        title = QLabel("Recording Control")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create splitter for better layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Controls using modern group box
        controls_group = ModernGroupBox("Recording Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Recording buttons using modern button components
        self.start_button = ModernButton("Start Recording", "success")
        self.start_button.clicked.connect(self.start_recording)
        controls_layout.addWidget(self.start_button)
        
        self.stop_button = ModernButton("Stop Recording", "danger")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        controls_layout.addWidget(self.stop_button)
        
        # Status display using status indicator
        self.status_indicator = StatusIndicator("Recording Status")
        self.status_indicator.set_status(False, "Ready to record")
        controls_layout.addWidget(self.status_indicator)
        
        # Progress indicator for recording operations
        self.progress_indicator = ProgressIndicator("Session Progress")
        controls_layout.addWidget(self.progress_indicator)
        
        controls_layout.addStretch()
        
        # Right side - Preview
        preview_group = ModernGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_panel = PreviewPanel(self)
        preview_layout.addWidget(self.preview_panel)
        
        # Add to splitter
        splitter.addWidget(controls_group)
        splitter.addWidget(preview_group)
        splitter.setSizes([300, 700])  # Give more space to preview
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(recording_widget, "Recording")

    def create_devices_tab(self):
        """Create the device management tab using modern components."""
        devices_widget = QWidget()
        layout = QVBoxLayout(devices_widget)
        
        # Title
        title = QLabel("Device Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Device connection managers
        devices_group = ModernGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Create connection managers for different device types
        self.pc_connection = ConnectionManager("PC Controller")
        self.pc_connection.connectionRequested.connect(lambda: self.connect_device("PC"))
        self.pc_connection.disconnectionRequested.connect(lambda: self.disconnect_device("PC"))
        devices_layout.addWidget(self.pc_connection)
        
        self.android_connection = ConnectionManager("Android Devices")
        self.android_connection.connectionRequested.connect(lambda: self.connect_device("Android"))
        self.android_connection.disconnectionRequested.connect(lambda: self.disconnect_device("Android"))
        devices_layout.addWidget(self.android_connection)
        
        self.shimmer_connection = ConnectionManager("Shimmer Sensors")
        self.shimmer_connection.connectionRequested.connect(lambda: self.connect_device("Shimmer"))
        self.shimmer_connection.disconnectionRequested.connect(lambda: self.disconnect_device("Shimmer"))
        devices_layout.addWidget(self.shimmer_connection)
        
        layout.addWidget(devices_group)
        
        # Global connection controls
        controls_group = ModernGroupBox("Global Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        connect_all_button = ModernButton("Connect All", "success")
        connect_all_button.clicked.connect(self.connect_all_devices)
        controls_layout.addWidget(connect_all_button)
        
        disconnect_all_button = ModernButton("Disconnect All", "danger")
        disconnect_all_button.clicked.connect(self.disconnect_all_devices)
        controls_layout.addWidget(disconnect_all_button)
        
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        layout.addStretch()
        
        self.tab_widget.addTab(devices_widget, "Devices")

    def create_calibration_tab(self):
        """Create the calibration tab using modern components."""
        calibration_widget = QWidget()
        layout = QVBoxLayout(calibration_widget)
        
        # Title
        title = QLabel("Camera Calibration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Calibration controls group
        calibration_group = ModernGroupBox("Calibration Controls")
        calibration_layout = QVBoxLayout(calibration_group)
        
        # Calibration button using modern component
        calibration_button = ModernButton("Run Calibration", "primary")
        calibration_button.clicked.connect(self.run_calibration)
        calibration_layout.addWidget(calibration_button)
        
        # Calibration status indicator
        self.calibration_status = StatusIndicator("Calibration Status")
        self.calibration_status.set_status(False, "Ready for calibration")
        calibration_layout.addWidget(self.calibration_status)
        
        # Calibration progress indicator
        self.calibration_progress = ProgressIndicator("Calibration Progress")
        calibration_layout.addWidget(self.calibration_progress)
        
        layout.addWidget(calibration_group)
        layout.addStretch()
        
        self.tab_widget.addTab(calibration_widget, "Calibration")

    def create_files_tab(self):
        """Create the files management tab using modern components."""
        files_widget = QWidget()
        layout = QVBoxLayout(files_widget)
        
        # Title
        title = QLabel("File Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # File operations group
        operations_group = ModernGroupBox("File Operations")
        operations_layout = QHBoxLayout(operations_group)
        
        open_folder_button = ModernButton("Open Recordings Folder", "primary")
        open_folder_button.clicked.connect(self.open_recordings_folder)
        operations_layout.addWidget(open_folder_button)
        
        export_button = ModernButton("Export Data", "secondary")
        export_button.clicked.connect(self.export_data)
        operations_layout.addWidget(export_button)
        
        operations_layout.addStretch()
        layout.addWidget(operations_group)
        
        # System log viewer
        log_group = ModernGroupBox("System Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_viewer = LogViewer("Recent Activity")
        log_layout.addWidget(self.log_viewer)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(files_widget, "Files")

    def setup_menu(self):
        """Setup simplified menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    # Action methods using modern components
    def start_recording(self):
        """Start recording session with enhanced feedback."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_indicator.set_status(True, "Recording in progress...")
        self.progress_indicator.set_indeterminate(True)
        self.status_bar.showMessage("Recording started")
        self.logger.info("Recording started")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Recording session started", "INFO")

    def stop_recording(self):
        """Stop recording session with enhanced feedback."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_indicator.set_status(False, "Recording stopped")
        self.progress_indicator.set_indeterminate(False)
        self.progress_indicator.set_progress(100, "Session complete")
        self.status_bar.showMessage("Recording stopped")
        self.logger.info("Recording stopped")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Recording session stopped", "INFO")

    def connect_device(self, device_type):
        """Connect to a specific device type."""
        self.status_bar.showMessage(f"Connecting to {device_type}...")
        self.logger.info(f"{device_type} connection initiated")
        
        # Simulate connection process
        QTimer.singleShot(1500, lambda: self.connection_complete(device_type, True))
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry(f"Connecting to {device_type}", "INFO")

    def disconnect_device(self, device_type):
        """Disconnect from a specific device type."""
        self.status_bar.showMessage(f"Disconnecting from {device_type}...")
        self.logger.info(f"{device_type} disconnection initiated")
        
        # Update connection manager
        if device_type == "PC" and hasattr(self, 'pc_connection'):
            self.pc_connection.set_connection_status(False, "Disconnected")
        elif device_type == "Android" and hasattr(self, 'android_connection'):
            self.android_connection.set_connection_status(False, "Disconnected")
        elif device_type == "Shimmer" and hasattr(self, 'shimmer_connection'):
            self.shimmer_connection.set_connection_status(False, "Disconnected")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry(f"Disconnected from {device_type}", "INFO")

    def connection_complete(self, device_type, success):
        """Handle connection completion."""
        if success:
            status_text = "Connected"
            log_level = "INFO"
            message = f"Connected to {device_type}"
        else:
            status_text = "Connection failed"
            log_level = "ERROR"
            message = f"Failed to connect to {device_type}"
        
        # Update appropriate connection manager
        if device_type == "PC" and hasattr(self, 'pc_connection'):
            self.pc_connection.set_connection_status(success, status_text)
        elif device_type == "Android" and hasattr(self, 'android_connection'):
            self.android_connection.set_connection_status(success, status_text)
        elif device_type == "Shimmer" and hasattr(self, 'shimmer_connection'):
            self.shimmer_connection.set_connection_status(success, status_text)
        
        self.status_bar.showMessage(message)
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry(message, log_level)

    def connect_all_devices(self):
        """Connect to all devices sequentially."""
        self.logger.info("Connecting to all devices")
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Initiating connection to all devices", "INFO")
        
        # Connect to devices in sequence
        device_types = ["PC", "Android", "Shimmer"]
        for i, device_type in enumerate(device_types):
            QTimer.singleShot(i * 1000, lambda dt=device_type: self.connect_device(dt))

    def disconnect_all_devices(self):
        """Disconnect from all devices."""
        self.logger.info("Disconnecting from all devices")
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Disconnecting from all devices", "INFO")
        
        device_types = ["PC", "Android", "Shimmer"]
        for device_type in device_types:
            self.disconnect_device(device_type)

    def run_calibration(self):
        """Run calibration process with enhanced feedback."""
        self.calibration_status.set_status(True, "Running calibration...")
        self.calibration_progress.set_progress(0, "Starting calibration...")
        self.status_bar.showMessage("Calibration in progress...")
        self.logger.info("Calibration started")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Camera calibration started", "INFO")
        
        # Simulate calibration progress
        self.calibration_timer = QTimer()
        self.calibration_step = 0
        self.calibration_timer.timeout.connect(self.update_calibration_progress)
        self.calibration_timer.start(200)  # Update every 200ms

    def update_calibration_progress(self):
        """Update calibration progress indicators."""
        self.calibration_step += 1
        progress = min(100, self.calibration_step * 5)
        
        if progress < 100:
            self.calibration_progress.set_progress(progress, f"Calibrating... {progress}%")
        else:
            self.calibration_timer.stop()
            self.calibration_complete()

    def calibration_complete(self):
        """Handle calibration completion with enhanced feedback."""
        self.calibration_status.set_status(False, "Calibration completed successfully")
        self.calibration_progress.set_progress(100, "Calibration complete")
        self.status_bar.showMessage("Calibration complete")
        self.logger.info("Calibration completed")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Camera calibration completed successfully", "INFO")

    def open_recordings_folder(self):
        """Open recordings folder with enhanced feedback."""
        self.status_bar.showMessage("Opening recordings folder...")
        self.logger.info("Opening recordings folder")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Opening recordings folder", "INFO")

    def export_data(self):
        """Export recorded data with enhanced feedback."""
        self.status_bar.showMessage("Exporting data...")
        self.logger.info("Data export initiated")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Data export initiated", "INFO")

    def show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(self, "Settings", "Settings dialog - Coming soon!")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            "Multi-Sensor Recording System\n"
            "Simplified Navigation Architecture\n"
            "Version 1.0.0\n\n"
            "Focus: Simplicity and Cleanliness"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        event.accept()