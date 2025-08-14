"""
Main Window GUI Module
======================

Simple, clean GUI for the multi-sensor recording system.
Provides essential controls for device management and recording.
"""

import logging
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QPushButton, QLabel, QTextEdit, QGroupBox,
        QLineEdit, QSpinBox, QCheckBox, QMessageBox,
        QTimer, QStatusBar, QTabWidget
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit, QGroupBox,
        QLineEdit, QSpinBox, QCheckBox, QMessageBox,
        QTimer, QStatusBar, QTabWidget
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT_VERSION = 5

from PythonApp.network import JsonSocketServer
from PythonApp.session import SessionManager, SessionConfig

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.server: Optional[JsonSocketServer] = None
        self.session_manager: Optional[SessionManager] = None
        
        self.setWindowTitle("Multi-Sensor Recording System")
        self.setMinimumSize(800, 600)
        
        # Initialize components
        self._init_backend()
        self._init_ui()
        self._init_timers()
        
        # Start server
        self._start_server()
    
    def _init_backend(self):
        """Initialize backend components."""
        try:
            self.server = JsonSocketServer(host="0.0.0.0", port=8080)
            self.session_manager = SessionManager()
            self.session_manager.set_network_server(self.server)
            logger.info("Backend components initialized")
        except Exception as e:
            logger.error(f"Failed to initialize backend: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize backend: {e}")
    
    def _init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        self._create_recording_tab(tab_widget)
        self._create_devices_tab(tab_widget)
        self._create_settings_tab(tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_recording_tab(self, tab_widget: QTabWidget):
        """Create the recording control tab."""
        recording_widget = QWidget()
        layout = QVBoxLayout(recording_widget)
        
        # Session configuration group
        session_group = QGroupBox("Session Configuration")
        session_layout = QVBoxLayout(session_group)
        
        # Session name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Session Name:"))
        self.session_name_input = QLineEdit("recording_session")
        name_layout.addWidget(self.session_name_input)
        session_layout.addLayout(name_layout)
        
        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(-1)  # -1 for unlimited
        self.duration_input.setMaximum(7200)  # 2 hours max
        self.duration_input.setValue(-1)
        self.duration_input.setSpecialValueText("Unlimited")
        duration_layout.addWidget(self.duration_input)
        session_layout.addLayout(duration_layout)
        
        # Auto-start option
        self.auto_start_checkbox = QCheckBox("Auto-start all connected devices")
        self.auto_start_checkbox.setChecked(True)
        session_layout.addWidget(self.auto_start_checkbox)
        
        layout.addWidget(session_group)
        
        # Recording controls group
        controls_group = QGroupBox("Recording Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.create_session_btn = QPushButton("Create Session")
        self.create_session_btn.clicked.connect(self._create_session)
        button_layout.addWidget(self.create_session_btn)
        
        self.start_recording_btn = QPushButton("Start Recording")
        self.start_recording_btn.clicked.connect(self._start_recording)
        self.start_recording_btn.setEnabled(False)
        button_layout.addWidget(self.start_recording_btn)
        
        self.stop_recording_btn = QPushButton("Stop Recording")
        self.stop_recording_btn.clicked.connect(self._stop_recording)
        self.stop_recording_btn.setEnabled(False)
        button_layout.addWidget(self.stop_recording_btn)
        
        controls_layout.addLayout(button_layout)
        
        # Session status
        self.session_status_label = QLabel("No active session")
        self.session_status_label.setStyleSheet("QLabel { color: gray; }")
        controls_layout.addWidget(self.session_status_label)
        
        layout.addWidget(controls_group)
        
        # Log display
        log_group = QGroupBox("Session Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(200)
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)
        
        layout.addWidget(log_group)
        
        tab_widget.addTab(recording_widget, "Recording")
    
    def _create_devices_tab(self, tab_widget: QTabWidget):
        """Create the devices monitoring tab."""
        devices_widget = QWidget()
        layout = QVBoxLayout(devices_widget)
        
        # Server status group
        server_group = QGroupBox("Server Status")
        server_layout = QVBoxLayout(server_group)
        
        self.server_status_label = QLabel("Server: Stopped")
        server_layout.addWidget(self.server_status_label)
        
        server_button_layout = QHBoxLayout()
        self.start_server_btn = QPushButton("Start Server")
        self.start_server_btn.clicked.connect(self._start_server)
        server_button_layout.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("Stop Server")
        self.stop_server_btn.clicked.connect(self._stop_server)
        server_button_layout.addWidget(self.stop_server_btn)
        
        server_layout.addLayout(server_button_layout)
        layout.addWidget(server_group)
        
        # Connected devices group
        devices_group = QGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_display = QTextEdit()
        self.devices_display.setReadOnly(True)
        devices_layout.addWidget(self.devices_display)
        
        layout.addWidget(devices_group)
        
        tab_widget.addTab(devices_widget, "Devices")
    
    def _create_settings_tab(self, tab_widget: QTabWidget):
        """Create the settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Network settings group
        network_group = QGroupBox("Network Settings")
        network_layout = QVBoxLayout(network_group)
        
        # Port setting
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Server Port:"))
        self.port_input = QSpinBox()
        self.port_input.setMinimum(1024)
        self.port_input.setMaximum(65535)
        self.port_input.setValue(8080)
        port_layout.addWidget(self.port_input)
        network_layout.addLayout(port_layout)
        
        layout.addWidget(network_group)
        
        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_input = QLineEdit("recordings")
        output_dir_layout.addWidget(self.output_dir_input)
        output_layout.addLayout(output_dir_layout)
        
        layout.addWidget(output_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        tab_widget.addTab(settings_widget, "Settings")
    
    def _init_timers(self):
        """Initialize update timers."""
        # Update UI every second
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(1000)  # 1 second
        
        # Cleanup dead connections every 30 seconds
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_connections)
        self.cleanup_timer.start(30000)  # 30 seconds
    
    def _start_server(self):
        """Start the network server."""
        if self.server and not self.server.running:
            port = self.port_input.value()
            self.server.port = port
            
            if self.server.start_server():
                self.server_status_label.setText(f"Server: Running on port {port}")
                self.server_status_label.setStyleSheet("QLabel { color: green; }")
                self.start_server_btn.setEnabled(False)
                self.stop_server_btn.setEnabled(True)
                self.status_bar.showMessage(f"Server started on port {port}")
                self._log_message(f"Server started on port {port}")
            else:
                QMessageBox.critical(self, "Error", "Failed to start server")
    
    def _stop_server(self):
        """Stop the network server."""
        if self.server and self.server.running:
            self.server.stop_server()
            self.server_status_label.setText("Server: Stopped")
            self.server_status_label.setStyleSheet("QLabel { color: red; }")
            self.start_server_btn.setEnabled(True)
            self.stop_server_btn.setEnabled(False)
            self.status_bar.showMessage("Server stopped")
            self._log_message("Server stopped")
    
    def _create_session(self):
        """Create a new recording session."""
        try:
            config = SessionConfig(
                session_name=self.session_name_input.text() or "recording_session",
                output_directory=self.output_dir_input.text() or "recordings",
                duration_seconds=self.duration_input.value(),
                auto_start_all_devices=self.auto_start_checkbox.isChecked()
            )
            
            session_info = self.session_manager.create_session(config)
            
            self.create_session_btn.setEnabled(False)
            self.start_recording_btn.setEnabled(True)
            
            self._log_message(f"Created session: {session_info.session_id}")
            self.status_bar.showMessage(f"Session created: {session_info.session_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create session: {e}")
            logger.error(f"Failed to create session: {e}")
    
    def _start_recording(self):
        """Start recording."""
        try:
            if self.session_manager.start_recording():
                self.start_recording_btn.setEnabled(False)
                self.stop_recording_btn.setEnabled(True)
                
                self._log_message("Recording started")
                self.status_bar.showMessage("Recording in progress...")
            else:
                QMessageBox.critical(self, "Error", "Failed to start recording")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start recording: {e}")
            logger.error(f"Failed to start recording: {e}")
    
    def _stop_recording(self):
        """Stop recording."""
        try:
            if self.session_manager.stop_recording():
                self.start_recording_btn.setEnabled(False)
                self.stop_recording_btn.setEnabled(False)
                self.create_session_btn.setEnabled(True)
                
                self._log_message("Recording stopped")
                self.status_bar.showMessage("Recording stopped")
            else:
                QMessageBox.critical(self, "Error", "Failed to stop recording")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop recording: {e}")
            logger.error(f"Failed to stop recording: {e}")
    
    def _update_ui(self):
        """Update UI with current status."""
        if not self.server or not self.session_manager:
            return
        
        # Update connected devices display
        devices = self.server.get_connected_devices()
        device_text = f"Connected Devices ({len(devices)}):\n\n"
        
        for device_id, device_info in devices.items():
            status = "🟢" if device_info['is_alive'] else "🔴"
            recording = "🎬" if device_info['is_recording'] else "⏸️"
            device_text += f"{status} {recording} {device_id}\n"
            device_text += f"   Address: {device_info['address']}\n"
            device_text += f"   Connected: {device_info['connected_time'][:19]}\n\n"
        
        if not devices:
            device_text += "No devices connected\n"
            device_text += "\nTo connect Android devices:\n"
            device_text += "1. Enable USB debugging on Android device\n"
            device_text += "2. Open the Android app\n"
            device_text += "3. Enter PC IP address and port 8080\n"
            device_text += "4. Tap 'Connect to PC'\n"
        
        self.devices_display.setText(device_text)
        
        # Update session status
        session_status = self.session_manager.get_session_status()
        if session_status['has_active_session']:
            session_info = session_status['session_info']
            status = session_info['status']
            
            if status == "recording" and session_status['duration_seconds']:
                duration = int(session_status['duration_seconds'])
                mins, secs = divmod(duration, 60)
                status_text = f"Recording: {mins:02d}:{secs:02d}"
                self.session_status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            else:
                status_text = f"Session: {status}"
                self.session_status_label.setStyleSheet("QLabel { color: blue; }")
            
            self.session_status_label.setText(status_text)
        else:
            self.session_status_label.setText("No active session")
            self.session_status_label.setStyleSheet("QLabel { color: gray; }")
    
    def _cleanup_connections(self):
        """Clean up dead device connections."""
        if self.server:
            self.server.cleanup_dead_connections()
    
    def _log_message(self, message: str):
        """Add message to log display."""
        timestamp = logger.name  # Simple timestamp alternative
        self.log_display.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End if PYQT_VERSION == 6 else cursor.End)
        self.log_display.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Handle application close."""
        try:
            # Stop any active recording
            if (self.session_manager and 
                self.session_manager.active_session and 
                self.session_manager.active_session.status == "recording"):
                
                reply = QMessageBox.question(
                    self, 
                    "Recording Active", 
                    "Recording is active. Stop recording and exit?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    if PYQT_VERSION == 6 else
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == (QMessageBox.StandardButton.Yes if PYQT_VERSION == 6 else QMessageBox.Yes):
                    self.session_manager.stop_recording()
                else:
                    event.ignore()
                    return
            
            # Stop server
            if self.server and self.server.running:
                self.server.stop_server()
            
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()