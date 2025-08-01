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
        """Create the main recording control tab."""
        recording_widget = QWidget()
        layout = QVBoxLayout(recording_widget)
        
        # Title
        title = QLabel("Recording Control")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create splitter for better layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Controls
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Recording buttons
        self.start_button = QPushButton("Start Recording")
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-size: 14px; }")
        self.start_button.clicked.connect(self.start_recording)
        controls_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; font-size: 14px; }")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        controls_layout.addWidget(self.stop_button)
        
        # Status display
        self.status_label = QLabel("Ready to record")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        
        # Right side - Preview
        self.preview_panel = PreviewPanel(self)
        
        # Add to splitter
        splitter.addWidget(controls_frame)
        splitter.addWidget(self.preview_panel)
        splitter.setSizes([300, 700])  # Give more space to preview
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(recording_widget, "Recording")

    def create_devices_tab(self):
        """Create the device management tab."""
        devices_widget = QWidget()
        layout = QVBoxLayout(devices_widget)
        
        # Title
        title = QLabel("Device Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Device status panel
        self.device_panel = DeviceStatusPanel(self)
        layout.addWidget(self.device_panel)
        
        # Connection controls
        connection_layout = QHBoxLayout()
        
        connect_button = QPushButton("Connect Devices")
        connect_button.clicked.connect(self.connect_devices)
        connection_layout.addWidget(connect_button)
        
        disconnect_button = QPushButton("Disconnect All")
        disconnect_button.clicked.connect(self.disconnect_devices)
        connection_layout.addWidget(disconnect_button)
        
        connection_layout.addStretch()
        layout.addLayout(connection_layout)
        
        self.tab_widget.addTab(devices_widget, "Devices")

    def create_calibration_tab(self):
        """Create the calibration tab."""
        calibration_widget = QWidget()
        layout = QVBoxLayout(calibration_widget)
        
        # Title
        title = QLabel("Camera Calibration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Calibration controls
        calibration_button = QPushButton("Run Calibration")
        calibration_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-size: 14px; }")
        calibration_button.clicked.connect(self.run_calibration)
        layout.addWidget(calibration_button)
        
        # Calibration status
        self.calibration_status = QLabel("Ready for calibration")
        self.calibration_status.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.calibration_status)
        
        layout.addStretch()
        
        self.tab_widget.addTab(calibration_widget, "Calibration")

    def create_files_tab(self):
        """Create the files management tab."""
        files_widget = QWidget()
        layout = QVBoxLayout(files_widget)
        
        # Title
        title = QLabel("File Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # File operations
        file_layout = QHBoxLayout()
        
        open_folder_button = QPushButton("Open Recordings Folder")
        open_folder_button.clicked.connect(self.open_recordings_folder)
        file_layout.addWidget(open_folder_button)
        
        export_button = QPushButton("Export Data")
        export_button.clicked.connect(self.export_data)
        file_layout.addWidget(export_button)
        
        file_layout.addStretch()
        layout.addLayout(file_layout)
        
        # File list placeholder
        file_info = QLabel("Recent recordings will appear here")
        file_info.setStyleSheet("padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd;")
        layout.addWidget(file_info)
        
        layout.addStretch()
        
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

    # Action methods (simplified)
    def start_recording(self):
        """Start recording session."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Recording in progress...")
        self.status_bar.showMessage("Recording started")
        self.logger.info("Recording started")

    def stop_recording(self):
        """Stop recording session."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Recording stopped")
        self.status_bar.showMessage("Recording stopped")
        self.logger.info("Recording stopped")

    def connect_devices(self):
        """Connect to devices."""
        self.status_bar.showMessage("Connecting to devices...")
        self.logger.info("Device connection initiated")

    def disconnect_devices(self):
        """Disconnect all devices."""
        self.status_bar.showMessage("Disconnected from devices")
        self.logger.info("All devices disconnected")

    def run_calibration(self):
        """Run calibration process."""
        self.calibration_status.setText("Running calibration...")
        self.status_bar.showMessage("Calibration in progress...")
        self.logger.info("Calibration started")
        
        # Simulate calibration process
        QTimer.singleShot(2000, self.calibration_complete)

    def calibration_complete(self):
        """Handle calibration completion."""
        self.calibration_status.setText("Calibration completed successfully")
        self.status_bar.showMessage("Calibration complete")
        self.logger.info("Calibration completed")

    def open_recordings_folder(self):
        """Open recordings folder."""
        self.status_bar.showMessage("Opening recordings folder...")
        self.logger.info("Opening recordings folder")

    def export_data(self):
        """Export recorded data."""
        self.status_bar.showMessage("Exporting data...")
        self.logger.info("Data export initiated")

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