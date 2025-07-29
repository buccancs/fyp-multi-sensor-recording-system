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
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QAction, QMessageBox,
    QDockWidget, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Import modular components
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .stimulus_panel import StimulusControlPanel


class MainWindow(QMainWindow):
    """Main window for the Multi-Sensor Recording System Controller."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize UI components
        self.init_ui()
        
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
    
    # Toolbar action handlers
    def handle_connect(self):
        """Handle connect button press."""
        self.statusBar().showMessage("Connect pressed - (simulation) connecting devices...")
        self.log_message("Connect button pressed - simulating device connection")
        # Simulate connection by updating device panel
        self.device_panel.update_all_devices_status(True)
        self.log_message("All devices marked as connected (simulation)")
    
    def handle_disconnect(self):
        """Handle disconnect button press."""
        self.statusBar().showMessage("Disconnect pressed - (simulation) disconnecting devices...")
        self.log_message("Disconnect button pressed - simulating device disconnection")
        # Simulate disconnection by updating device panel
        self.device_panel.update_all_devices_status(False)
        self.log_message("All devices marked as disconnected (simulation)")
    
    def handle_start(self):
        """Handle start session button press."""
        self.statusBar().showMessage("Session started (simulation)")
        self.log_message("Start Session button pressed - beginning recording session (simulation)")
    
    def handle_stop(self):
        """Handle stop button press."""
        self.statusBar().showMessage("Session stopped (simulation)")
        self.log_message("Stop button pressed - ending recording session (simulation)")
    
    def handle_capture_calibration(self):
        """Handle capture calibration button press."""
        self.statusBar().showMessage("Capturing calibration (simulation)")
        self.log_message("Capture Calibration button pressed - initiating calibration capture (simulation)")
