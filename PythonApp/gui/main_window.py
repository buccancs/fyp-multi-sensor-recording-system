"""
Main Window GUI Module
======================

Simple, clean GUI for the multi-sensor recording system.
Provides essential controls for device management and recording.
"""

import logging
import time
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QPushButton, QLabel, QTextEdit, QGroupBox,
        QLineEdit, QSpinBox, QCheckBox, QMessageBox,
        QStatusBar, QTabWidget, QComboBox, QFrame,
        QFileDialog, QSlider, QProgressBar
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont, QPixmap, QImage
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit, QGroupBox,
        QLineEdit, QSpinBox, QCheckBox, QMessageBox,
        QStatusBar, QTabWidget, QComboBox, QFrame,
        QFileDialog, QSlider, QProgressBar
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPixmap, QImage
    PYQT_VERSION = 5

from PythonApp.network import JsonSocketServer
from PythonApp.session import SessionManager, SessionConfig
from PythonApp.sensors import SensorManager
from PythonApp.sync import TimeServer, SessionSynchronizer, SyncSignalBroadcaster
from PythonApp.calibration import CalibrationManager, CalibrationPattern
from PythonApp.transfer import TransferManager
from PythonApp.security import SecurityManager
from PythonApp.camera import WebcamManager, CameraCapture, VideoPlayer, OPENCV_AVAILABLE

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.server: Optional[JsonSocketServer] = None
        self.session_manager: Optional[SessionManager] = None
        self.sensor_manager: Optional[SensorManager] = None
        self.time_server: Optional[TimeServer] = None
        self.session_synchronizer: Optional[SessionSynchronizer] = None
        self.sync_broadcaster: Optional[SyncSignalBroadcaster] = None
        self.calibration_manager: Optional[CalibrationManager] = None
        self.transfer_manager: Optional[TransferManager] = None
        self.security_manager: Optional[SecurityManager] = None
        self.webcam_manager: Optional[WebcamManager] = None
        self.active_camera_capture: Optional[CameraCapture] = None
        self.active_video_player: Optional[VideoPlayer] = None
        self.current_video_path: str = ""
        
        self.setWindowTitle("Multi-Sensor Recording System - Enhanced")
        self.setMinimumSize(1000, 700)
        
        # Initialize components
        self._init_backend()
        self._init_ui()
        self._init_timers()
        
        # Start server
        self._start_server()
    
    def _init_backend(self):
        """Initialize backend components."""
        try:
            # Initialize security manager
            self.security_manager = SecurityManager()
            
            # Initialize network server
            self.server = JsonSocketServer(host="0.0.0.0", port=8080)
            self.server.set_security_manager(self.security_manager)
            
            # Initialize time synchronization
            self.time_server = TimeServer(host="0.0.0.0", port=8889)
            
            # Initialize sensor manager
            self.sensor_manager = SensorManager()
            
            # Initialize session synchronizer
            self.session_synchronizer = SessionSynchronizer(self.time_server, self.server)
            self.server.set_session_synchronizer(self.session_synchronizer)
            
            # Initialize sync broadcaster
            self.sync_broadcaster = SyncSignalBroadcaster(self.server)
            
            # Initialize calibration manager
            self.calibration_manager = CalibrationManager()
            
            # Initialize transfer manager
            self.transfer_manager = TransferManager()
            self.transfer_manager.set_network_server(self.server)
            self.server.set_transfer_manager(self.transfer_manager)
            
            # Initialize session manager
            self.session_manager = SessionManager()
            self.session_manager.set_network_server(self.server)
            self.session_manager.set_sensor_manager(self.sensor_manager)
            self.session_manager.set_session_synchronizer(self.session_synchronizer)
            self.session_manager.set_transfer_manager(self.transfer_manager)
            
            # Initialize webcam manager
            self.webcam_manager = WebcamManager()
            
            # Add a default simulated sensor
            self.sensor_manager.add_sensor("simulated_gsr_01")
            
            logger.info("Backend components initialized successfully")
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
        self._create_sensors_tab(tab_widget)
        self._create_sync_tab(tab_widget)
        self._create_calibration_tab(tab_widget)
        self._create_media_tab(tab_widget)
        self._create_security_tab(tab_widget)
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
    
    def _create_sensors_tab(self, tab_widget: QTabWidget):
        """Create the sensors monitoring tab."""
        sensors_widget = QWidget()
        layout = QVBoxLayout(sensors_widget)
        
        # Sensor status group
        sensor_group = QGroupBox("GSR Sensors")
        sensor_layout = QVBoxLayout(sensor_group)
        
        self.sensors_display = QTextEdit()
        self.sensors_display.setReadOnly(True)
        self.sensors_display.setMaximumHeight(200)
        sensor_layout.addWidget(self.sensors_display)
        
        # Sensor controls
        sensor_controls = QHBoxLayout()
        
        self.add_sensor_btn = QPushButton("Add Simulated Sensor")
        self.add_sensor_btn.clicked.connect(self._add_simulated_sensor)
        sensor_controls.addWidget(self.add_sensor_btn)
        
        sensor_layout.addLayout(sensor_controls)
        layout.addWidget(sensor_group)
        
        # Time sync status group
        sync_group = QGroupBox("Time Synchronization")
        sync_layout = QVBoxLayout(sync_group)
        
        self.time_sync_display = QTextEdit()
        self.time_sync_display.setReadOnly(True)
        self.time_sync_display.setMaximumHeight(150)
        sync_layout.addWidget(self.time_sync_display)
        
        # Sync controls
        sync_controls = QHBoxLayout()
        
        self.start_time_server_btn = QPushButton("Start Time Server")
        self.start_time_server_btn.clicked.connect(self._start_time_server)
        sync_controls.addWidget(self.start_time_server_btn)
        
        self.stop_time_server_btn = QPushButton("Stop Time Server")
        self.stop_time_server_btn.clicked.connect(self._stop_time_server)
        self.stop_time_server_btn.setEnabled(False)
        sync_controls.addWidget(self.stop_time_server_btn)
        
        sync_layout.addLayout(sync_controls)
        layout.addWidget(sync_group)
        
        tab_widget.addTab(sensors_widget, "Sensors")
    
    def _create_sync_tab(self, tab_widget: QTabWidget):
        """Create the synchronization tab."""
        sync_widget = QWidget()
        layout = QVBoxLayout(sync_widget)
        
        # Sync signals group
        signals_group = QGroupBox("Synchronization Signals")
        signals_layout = QVBoxLayout(signals_group)
        
        # Signal buttons
        signal_buttons = QHBoxLayout()
        
        self.flash_signal_btn = QPushButton("Send Flash Signal")
        self.flash_signal_btn.clicked.connect(self._send_flash_signal)
        signal_buttons.addWidget(self.flash_signal_btn)
        
        self.audio_signal_btn = QPushButton("Send Audio Signal")
        self.audio_signal_btn.clicked.connect(self._send_audio_signal)
        signal_buttons.addWidget(self.audio_signal_btn)
        
        self.marker_signal_btn = QPushButton("Send Marker Signal")
        self.marker_signal_btn.clicked.connect(self._send_marker_signal)
        signal_buttons.addWidget(self.marker_signal_btn)
        
        signals_layout.addLayout(signal_buttons)
        layout.addWidget(signals_group)
        
        # Sync status group
        sync_status_group = QGroupBox("Device Synchronization Status")
        sync_status_layout = QVBoxLayout(sync_status_group)
        
        self.sync_status_display = QTextEdit()
        self.sync_status_display.setReadOnly(True)
        sync_status_layout.addWidget(self.sync_status_display)
        
        layout.addWidget(sync_status_group)
        
        tab_widget.addTab(sync_widget, "Sync")
    
    def _create_calibration_tab(self, tab_widget: QTabWidget):
        """Create the calibration tab."""
        calibration_widget = QWidget()
        layout = QVBoxLayout(calibration_widget)
        
        # Calibration controls group
        controls_group = QGroupBox("Camera Calibration")
        controls_layout = QVBoxLayout(controls_group)
        
        # Calibration info
        info_text = QLabel("Camera calibration allows for precise alignment between RGB and thermal cameras.\n"
                          "This feature requires OpenCV and calibration pattern images.")
        info_text.setWordWrap(True)
        controls_layout.addWidget(info_text)
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Target Device:"))
        self.calibration_device_input = QLineEdit("android_device_01")
        device_layout.addWidget(self.calibration_device_input)
        controls_layout.addLayout(device_layout)
        
        # Pattern settings
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Pattern Size:"))
        self.pattern_width_input = QSpinBox()
        self.pattern_width_input.setRange(3, 20)
        self.pattern_width_input.setValue(9)
        pattern_layout.addWidget(self.pattern_width_input)
        pattern_layout.addWidget(QLabel("x"))
        self.pattern_height_input = QSpinBox()
        self.pattern_height_input.setRange(3, 20)
        self.pattern_height_input.setValue(6)
        pattern_layout.addWidget(self.pattern_height_input)
        controls_layout.addLayout(pattern_layout)
        
        # Calibration buttons
        calibration_buttons = QHBoxLayout()
        
        self.start_calibration_btn = QPushButton("Start Calibration Session")
        self.start_calibration_btn.clicked.connect(self._start_calibration_session)
        calibration_buttons.addWidget(self.start_calibration_btn)
        
        self.end_calibration_btn = QPushButton("End Calibration Session")
        self.end_calibration_btn.clicked.connect(self._end_calibration_session)
        self.end_calibration_btn.setEnabled(False)
        calibration_buttons.addWidget(self.end_calibration_btn)
        
        controls_layout.addLayout(calibration_buttons)
        layout.addWidget(controls_group)
        
        # Calibration status
        status_group = QGroupBox("Calibration Status")
        status_layout = QVBoxLayout(status_group)
        
        self.calibration_status_display = QTextEdit()
        self.calibration_status_display.setReadOnly(True)
        self.calibration_status_display.setMaximumHeight(200)
        status_layout.addWidget(self.calibration_status_display)
        
        layout.addWidget(status_group)
        
        tab_widget.addTab(calibration_widget, "Calibration")
    
    def _create_media_tab(self, tab_widget: QTabWidget):
        """Create the media (camera preview + video playback) tab."""
        media_widget = QWidget()
        layout = QVBoxLayout(media_widget)
        
        # Create two main sections: Camera Preview and Video Playback
        
        # Camera Preview Section
        camera_group = QGroupBox("USB Camera Preview")
        camera_layout = QVBoxLayout(camera_group)
        
        # Camera info
        camera_info_text = QLabel("Real-time USB webcam preview for participant monitoring.\n"
                                 "Requires OpenCV and a connected USB camera.")
        camera_info_text.setWordWrap(True)
        camera_layout.addWidget(camera_info_text)
        
        # Camera selection and controls
        camera_controls_layout = QHBoxLayout()
        camera_controls_layout.addWidget(QLabel("Select Camera:"))
        self.camera_combo = QComboBox()
        camera_controls_layout.addWidget(self.camera_combo)
        
        self.refresh_cameras_btn = QPushButton("Refresh Cameras")
        self.refresh_cameras_btn.clicked.connect(self._refresh_cameras)
        camera_controls_layout.addWidget(self.refresh_cameras_btn)
        
        self.start_preview_btn = QPushButton("Start Camera Preview")
        self.start_preview_btn.clicked.connect(self._start_camera_preview)
        camera_controls_layout.addWidget(self.start_preview_btn)
        
        self.stop_preview_btn = QPushButton("Stop Camera Preview")
        self.stop_preview_btn.clicked.connect(self._stop_camera_preview)
        self.stop_preview_btn.setEnabled(False)
        camera_controls_layout.addWidget(self.stop_preview_btn)
        
        camera_layout.addLayout(camera_controls_layout)
        layout.addWidget(camera_group)
        
        # Video Playback Section
        video_group = QGroupBox("Video Playback for Emotion Elicitation")
        video_layout = QVBoxLayout(video_group)
        
        # Video info
        video_info_text = QLabel("Play video files to elicit emotional responses during experiments.\n"
                                "Supports common formats: MP4, AVI, MOV, etc.")
        video_info_text.setWordWrap(True)
        video_layout.addWidget(video_info_text)
        
        # Video file selection
        video_file_layout = QHBoxLayout()
        video_file_layout.addWidget(QLabel("Video File:"))
        self.video_path_label = QLabel("No video selected")
        self.video_path_label.setStyleSheet("QLabel { color: gray; }")
        video_file_layout.addWidget(self.video_path_label)
        
        self.browse_video_btn = QPushButton("Browse...")
        self.browse_video_btn.clicked.connect(self._browse_video_file)
        video_file_layout.addWidget(self.browse_video_btn)
        
        video_layout.addLayout(video_file_layout)
        
        # Video playback controls
        video_controls_layout = QHBoxLayout()
        
        self.play_video_btn = QPushButton("Play")
        self.play_video_btn.clicked.connect(self._handle_play_button)
        self.play_video_btn.setEnabled(False)
        video_controls_layout.addWidget(self.play_video_btn)
        
        self.pause_video_btn = QPushButton("Pause")
        self.pause_video_btn.clicked.connect(self._pause_video)
        self.pause_video_btn.setEnabled(False)
        video_controls_layout.addWidget(self.pause_video_btn)
        
        self.stop_video_btn = QPushButton("Stop")
        self.stop_video_btn.clicked.connect(self._stop_video)
        self.stop_video_btn.setEnabled(False)
        video_controls_layout.addWidget(self.stop_video_btn)
        
        video_layout.addLayout(video_controls_layout)
        
        # Video progress slider
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.video_progress_slider = QSlider(Qt.Horizontal)
        self.video_progress_slider.setEnabled(False)
        self.video_progress_slider.sliderPressed.connect(self._video_slider_pressed)
        self.video_progress_slider.sliderReleased.connect(self._video_slider_released)
        progress_layout.addWidget(self.video_progress_slider)
        
        self.video_time_label = QLabel("00:00 / 00:00")
        progress_layout.addWidget(self.video_time_label)
        
        video_layout.addLayout(progress_layout)
        layout.addWidget(video_group)
        
        # Shared display area for both camera and video
        display_group = QGroupBox("Media Display")
        display_layout = QVBoxLayout(display_group)
        
        # Create display label with fixed size
        self.media_display_label = QLabel()
        self.media_display_label.setMinimumSize(640, 480)
        self.media_display_label.setStyleSheet("QLabel { background-color: black; border: 1px solid gray; }")
        self.media_display_label.setAlignment(Qt.AlignCenter)
        self.media_display_label.setText("No media active\nStart camera preview or load a video to begin")
        self.media_display_label.setWordWrap(True)
        
        # Add display label to a frame for better appearance
        display_frame = QFrame()
        display_frame.setFrameStyle(QFrame.Box)
        display_frame_layout = QVBoxLayout(display_frame)
        display_frame_layout.addWidget(self.media_display_label)
        
        display_layout.addWidget(display_frame)
        layout.addWidget(display_group)
        
        # Media status
        status_group = QGroupBox("Media Status")
        status_layout = QVBoxLayout(status_group)
        
        self.media_status_display = QTextEdit()
        self.media_status_display.setReadOnly(True)
        self.media_status_display.setMaximumHeight(150)
        self.media_status_display.setText("Media system ready")
        status_layout.addWidget(self.media_status_display)
        
        layout.addWidget(status_group)
        
        tab_widget.addTab(media_widget, "Media & Stimuli")
        
        # Initialize camera list
        self._refresh_cameras()
        
        # Initialize video player state
        self._video_slider_dragging = False
    
    def _create_security_tab(self, tab_widget: QTabWidget):
        """Create the security tab."""
        security_widget = QWidget()
        layout = QVBoxLayout(security_widget)
        
        # Security status group
        status_group = QGroupBox("Security Status")
        status_layout = QVBoxLayout(status_group)
        
        self.security_status_display = QTextEdit()
        self.security_status_display.setReadOnly(True)
        self.security_status_display.setMaximumHeight(200)
        status_layout.addWidget(self.security_status_display)
        
        layout.addWidget(status_group)
        
        # Authentication controls group
        auth_group = QGroupBox("Authentication Management")
        auth_layout = QVBoxLayout(auth_group)
        
        # Token generation
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Device ID:"))
        self.token_device_input = QLineEdit("android_device_01")
        token_layout.addWidget(self.token_device_input)
        
        self.generate_token_btn = QPushButton("Generate Token")
        self.generate_token_btn.clicked.connect(self._generate_auth_token)
        token_layout.addWidget(self.generate_token_btn)
        
        auth_layout.addLayout(token_layout)
        
        # Token display
        self.token_display = QTextEdit()
        self.token_display.setMaximumHeight(100)
        self.token_display.setPlaceholderText("Generated authentication tokens will appear here...")
        auth_layout.addWidget(self.token_display)
        
        layout.addWidget(auth_group)
        
        tab_widget.addTab(security_widget, "Security")
    
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
    
    def _add_simulated_sensor(self):
        """Add a simulated GSR sensor."""
        try:
            import time
            sensor_id = f"simulated_gsr_{int(time.time())}"
            
            if self.sensor_manager and self.sensor_manager.add_sensor(sensor_id):
                self._log_message(f"Added simulated sensor: {sensor_id}")
            else:
                QMessageBox.warning(self, "Warning", "Failed to add simulated sensor")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add sensor: {e}")
    
    def _start_time_server(self):
        """Start the time synchronization server."""
        try:
            if self.time_server and self.time_server.start_server():
                self.start_time_server_btn.setEnabled(False)
                self.stop_time_server_btn.setEnabled(True)
                self._log_message("Time synchronization server started")
            else:
                QMessageBox.critical(self, "Error", "Failed to start time server")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start time server: {e}")
    
    def _stop_time_server(self):
        """Stop the time synchronization server."""
        try:
            if self.time_server:
                self.time_server.stop_server()
                self.start_time_server_btn.setEnabled(True)
                self.stop_time_server_btn.setEnabled(False)
                self._log_message("Time synchronization server stopped")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop time server: {e}")
    
    def _send_flash_signal(self):
        """Send flash synchronization signal."""
        try:
            if self.sync_broadcaster:
                devices = self.sync_broadcaster.send_flash_signal()
                self._log_message(f"Flash signal sent to {len(devices)} devices")
            else:
                QMessageBox.warning(self, "Warning", "Sync broadcaster not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send flash signal: {e}")
    
    def _send_audio_signal(self):
        """Send audio synchronization signal."""
        try:
            if self.sync_broadcaster:
                devices = self.sync_broadcaster.send_audio_signal()
                self._log_message(f"Audio signal sent to {len(devices)} devices")
            else:
                QMessageBox.warning(self, "Warning", "Sync broadcaster not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send audio signal: {e}")
    
    def _send_marker_signal(self):
        """Send marker synchronization signal."""
        try:
            if self.sync_broadcaster:
                devices = self.sync_broadcaster.send_marker_signal()
                self._log_message(f"Marker signal sent to {len(devices)} devices")
            else:
                QMessageBox.warning(self, "Warning", "Sync broadcaster not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send marker signal: {e}")
    
    def _start_calibration_session(self):
        """Start a camera calibration session."""
        try:
            if not self.calibration_manager:
                QMessageBox.warning(self, "Warning", "Calibration manager not available")
                return
            
            device_id = self.calibration_device_input.text() or "android_device_01"
            pattern = CalibrationPattern(
                pattern_size=(self.pattern_width_input.value(), self.pattern_height_input.value())
            )
            
            session = self.calibration_manager.start_calibration_session(device_id, pattern)
            
            self.start_calibration_btn.setEnabled(False)
            self.end_calibration_btn.setEnabled(True)
            
            self._log_message(f"Started calibration session for {device_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start calibration: {e}")
    
    def _end_calibration_session(self):
        """End the active calibration session."""
        try:
            if self.calibration_manager:
                self.calibration_manager.end_session()
                
                self.start_calibration_btn.setEnabled(True)
                self.end_calibration_btn.setEnabled(False)
                
                self._log_message("Ended calibration session")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to end calibration: {e}")
    
    def _generate_auth_token(self):
        """Generate an authentication token for a device."""
        try:
            if not self.security_manager:
                QMessageBox.warning(self, "Warning", "Security manager not available")
                return
            
            device_id = self.token_device_input.text() or "android_device_01"
            token_value, token_info = self.security_manager.generate_device_token(device_id)
            
            # Display token
            token_text = f"Device: {device_id}\nToken: {token_value}\nExpires: {token_info['expires_at']}\n\n"
            self.token_display.append(token_text)
            
            self._log_message(f"Generated authentication token for {device_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate token: {e}")
    
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
            auth = "🔐" if device_info['authenticated'] else "🔓"
            device_text += f"{status} {recording} {auth} {device_id}\n"
            device_text += f"   Address: {device_info['address']}\n"
            device_text += f"   Connected: {device_info['connected_time'][:19]}\n"
            device_text += f"   Permissions: {', '.join(device_info['permissions'])}\n\n"
        
        if not devices:
            device_text += "No devices connected\n"
            device_text += "\nTo connect Android devices:\n"
            device_text += "1. Enable USB debugging on Android device\n"
            device_text += "2. Open the Android app\n"
            device_text += "3. Enter PC IP address and port 8080\n"
            device_text += "4. Tap 'Connect to PC'\n"
        
        self.devices_display.setText(device_text)
        
        # Update sensor status
        if self.sensor_manager:
            sensor_status = self.sensor_manager.get_sensor_status()
            sensor_text = f"GSR Sensors ({len(sensor_status)}):\n\n"
            
            for sensor_id, status in sensor_status.items():
                connected = "🟢" if status['is_connected'] else "🔴"
                streaming = "📊" if status['is_streaming'] else "⏹️"
                sensor_text += f"{connected} {streaming} {sensor_id}\n"
                sensor_text += f"   Sample Rate: {status['sample_rate']} Hz\n"
                sensor_text += f"   Samples: {status['sample_count']}\n"
                sensor_text += f"   Port: {status['port'] or 'Simulated'}\n\n"
            
            if not sensor_status:
                sensor_text += "No sensors configured\n"
                sensor_text += "Click 'Add Simulated Sensor' to add a test sensor\n"
            
            self.sensors_display.setText(sensor_text)
        
        # Update time sync status
        if self.time_server:
            sync_stats = self.time_server.get_sync_statistics()
            sync_text = f"Time Server Status: {'Running' if self.time_server.running else 'Stopped'}\n"
            sync_text += f"Server Time: {datetime.fromtimestamp(sync_stats['server_time']).strftime('%H:%M:%S.%f')[:-3]}\n"
            sync_text += f"Reference Offset: {sync_stats['reference_offset']:.3f}s\n"
            sync_text += f"Total Clients: {sync_stats['total_clients']}\n\n"
            
            for client_id, client_stats in sync_stats['clients'].items():
                quality = "🟢" if client_stats['sync_quality'] == 'good' else "🟡"
                sync_text += f"{quality} {client_id}\n"
                sync_text += f"   Syncs: {client_stats['successful_syncs']}/{client_stats['recent_syncs']}\n"
                sync_text += f"   Avg Offset: {client_stats['avg_offset_ms']:.1f}ms\n"
                sync_text += f"   Last Sync: {client_stats['last_sync'][:19] if client_stats['last_sync'] else 'Never'}\n\n"
            
            self.time_sync_display.setText(sync_text)
        
        # Update sync status
        if self.session_synchronizer:
            sync_status = self.session_synchronizer.get_device_sync_status()
            sync_text = f"Device Synchronization:\n\n"
            
            for device_id, status in sync_status.items():
                online = "🟢" if status['is_online'] else "🔴"
                sync_text += f"{online} {device_id}\n"
                sync_text += f"   Session: {status.get('session_id', 'None')}\n"
                sync_text += f"   Status: {status.get('sync_status', 'Unknown')}\n\n"
            
            if not sync_status:
                sync_text += "No devices in active session\n"
            
            self.sync_status_display.setText(sync_text)
        
        # Update calibration status
        if self.calibration_manager:
            calibration_status = self.calibration_manager.get_session_status()
            if calibration_status:
                cal_text = f"Active Calibration Session:\n"
                cal_text += f"Session ID: {calibration_status['session_id']}\n"
                cal_text += f"Progress: {calibration_status['capture_count']}/{calibration_status['max_captures']}\n"
                cal_text += f"Pattern: {calibration_status['pattern']['pattern_size']}\n"
                cal_text += f"Ready: {'Yes' if calibration_status['ready_for_calibration'] else 'No'}\n"
            else:
                cal_text = "No active calibration session\n"
                available_calibrations = self.calibration_manager.get_available_calibrations()
                cal_text += f"\nStored Calibrations: {len(available_calibrations)}\n"
                for cal in available_calibrations[:3]:  # Show first 3
                    cal_text += f"  - {cal['device_id']} (Error: {cal['reprojection_error']:.3f})\n"
            
            self.calibration_status_display.setText(cal_text)
        
        # Update security status
        if self.security_manager:
            security_status = self.security_manager.get_security_status()
            sec_text = f"Security Configuration:\n"
            sec_text += f"TLS Enabled: {'Yes' if security_status['configuration']['tls_enabled'] else 'No'}\n"
            sec_text += f"Authentication Required: {'Yes' if security_status['configuration']['authentication_required'] else 'No'}\n"
            sec_text += f"Token Expiry: {security_status['configuration']['token_expiry_hours']} hours\n\n"
            
            sec_text += f"TLS Status:\n"
            sec_text += f"Enabled: {'Yes' if security_status['tls_status']['enabled'] else 'No'}\n"
            sec_text += f"Certificate: {security_status['tls_status']['certificate_file']}\n\n"
            
            sec_text += f"Authentication:\n"
            sec_text += f"Total Tokens: {security_status['authentication_status']['total_tokens']}\n"
            sec_text += f"Locked Devices: {security_status['authentication_status']['locked_devices']}\n\n"
            
            warnings = security_status['security_checks']['security_warnings']
            if warnings:
                sec_text += f"Security Warnings:\n"
                for warning in warnings[:3]:  # Show first 3 warnings
                    sec_text += f"  ⚠️ {warning}\n"
            else:
                sec_text += "✅ No security warnings\n"
            
            self.security_status_display.setText(sec_text)
        
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
    
    def _refresh_cameras(self):
        """Refresh the list of available cameras."""
        if not self.webcam_manager:
            return
            
        try:
            cameras = self.webcam_manager.detect_cameras()
            
            # Clear and repopulate combo box
            self.camera_combo.clear()
            
            if not cameras:
                self.camera_combo.addItem("No cameras detected")
                self.start_preview_btn.setEnabled(False)
                self._update_camera_status("No USB cameras detected")
            else:
                for camera in cameras:
                    self.camera_combo.addItem(f"Camera {camera.index} ({camera.width}x{camera.height})")
                self.start_preview_btn.setEnabled(True)
                self._update_camera_status(f"Found {len(cameras)} camera(s)")
                
        except Exception as e:
            logger.error(f"Error refreshing cameras: {e}")
            self._update_camera_status(f"Error detecting cameras: {e}")
    
    def _start_camera_preview(self):
        """Start the camera preview."""
        if not OPENCV_AVAILABLE:
            QMessageBox.warning(self, "OpenCV Required", "OpenCV is required for camera preview functionality.")
            return
            
        if not self.webcam_manager:
            return
            
        try:
            # Get selected camera index
            selected_text = self.camera_combo.currentText()
            if "No cameras" in selected_text:
                QMessageBox.warning(self, "No Camera", "No camera selected or available.")
                return
                
            camera_index = int(selected_text.split()[1])  # Extract index from "Camera X (...)"
            
            # Stop any existing preview
            self._stop_camera_preview()
            
            # Start new preview
            self.active_camera_capture = self.webcam_manager.start_camera_preview(camera_index)
            
            if self.active_camera_capture:
                # Connect signals for frame updates
                self.active_camera_capture.frame_ready.connect(self._update_camera_frame)
                self.active_camera_capture.error_occurred.connect(self._handle_camera_error)
                self.active_camera_capture.camera_disconnected.connect(self._handle_camera_disconnect)
                
                # Update UI
                self.start_preview_btn.setEnabled(False)
                self.stop_preview_btn.setEnabled(True)
                self.camera_combo.setEnabled(False)
                self.refresh_cameras_btn.setEnabled(False)
                
                self._update_camera_status(f"Camera {camera_index} preview started")
                logger.info(f"Camera {camera_index} preview started")
            else:
                self._update_camera_status("Failed to start camera preview")
                
        except Exception as e:
            logger.error(f"Error starting camera preview: {e}")
            self._update_camera_status(f"Error starting preview: {e}")
            QMessageBox.critical(self, "Camera Error", f"Failed to start camera preview: {e}")
    
    def _stop_camera_preview(self):
        """Stop the camera preview."""
        if self.active_camera_capture:
            try:
                self.active_camera_capture.stop_capture()
                self.active_camera_capture = None
                
                # Update UI
                self.start_preview_btn.setEnabled(True)
                self.stop_preview_btn.setEnabled(False)
                self.camera_combo.setEnabled(True)
                self.refresh_cameras_btn.setEnabled(True)
                
                # Clear preview
                self.media_display_label.clear()
                self.media_display_label.setText("Camera preview stopped\nClick 'Start Camera Preview' to begin")
                
                self._update_camera_status("Camera preview stopped")
                logger.info("Camera preview stopped")
                
            except Exception as e:
                logger.error(f"Error stopping camera preview: {e}")
                self._update_camera_status(f"Error stopping preview: {e}")
        
        if self.webcam_manager:
            self.webcam_manager.stop_camera_preview()
    
    def _update_camera_frame(self, frame):
        """Update the camera preview with a new frame."""
        try:
            if frame is None:
                return
                
            # Convert frame to RGB (OpenCV uses BGR)
            import cv2
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            
            # Create QImage
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Scale image to fit preview label while maintaining aspect ratio
            preview_size = self.media_display_label.size()
            scaled_pixmap = QPixmap.fromImage(q_image).scaled(
                preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            
            # Set the pixmap to the label
            self.media_display_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logger.error(f"Error updating camera frame: {e}")
            self._update_camera_status(f"Frame update error: {e}")
    
    def _handle_camera_error(self, error_message):
        """Handle camera error."""
        logger.error(f"Camera error: {error_message}")
        self._update_camera_status(f"Camera error: {error_message}")
        self._stop_camera_preview()
    
    def _handle_camera_disconnect(self):
        """Handle camera disconnection."""
        logger.warning("Camera disconnected")
        self._update_camera_status("Camera disconnected")
        self._stop_camera_preview()
        QMessageBox.warning(self, "Camera Disconnected", "The camera has been disconnected.")
    
    def _update_camera_status(self, message):
        """Update the media status display."""
        timestamp = time.strftime("%H:%M:%S")
        self.media_status_display.append(f"[{timestamp}] Camera: {message}")
        
        # Auto-scroll to bottom
        cursor = self.media_status_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End if PYQT_VERSION == 6 else cursor.End)
        self.media_status_display.setTextCursor(cursor)
    
    def _browse_video_file(self):
        """Browse for a video file to play."""
        try:
            # Get supported formats from webcam manager
            formats = self.webcam_manager.get_supported_video_formats() if self.webcam_manager else ["mp4", "avi", "mov"]
            format_filter = "Video Files (" + " ".join(f"*.{fmt}" for fmt in formats) + ");;All Files (*)"
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Video File for Emotion Elicitation",
                "",
                format_filter
            )
            
            if file_path:
                self.current_video_path = file_path
                filename = os.path.basename(file_path)
                self.video_path_label.setText(filename)
                self.video_path_label.setStyleSheet("QLabel { color: black; }")
                
                # Enable play button
                self.play_video_btn.setEnabled(True)
                self._update_video_status(f"Video loaded: {filename}")
                
                # Reset video controls
                self.video_progress_slider.setValue(0)
                self.video_time_label.setText("00:00 / 00:00")
                
        except Exception as e:
            logger.error(f"Error browsing video file: {e}")
            self._update_video_status(f"Error loading video: {e}")
            QMessageBox.critical(self, "Video Error", f"Failed to load video: {e}")
    
    def _play_video(self):
        """Start video playback."""
        if not OPENCV_AVAILABLE:
            QMessageBox.warning(self, "OpenCV Required", "OpenCV is required for video playback functionality.")
            return
            
        if not self.current_video_path:
            QMessageBox.warning(self, "No Video", "Please select a video file first.")
            return
            
        try:
            # Stop any active camera preview
            if self.active_camera_capture:
                self._stop_camera_preview()
            
            # Stop any existing video playback
            if self.active_video_player:
                self._stop_video()
            
            # Start new video playback
            self.active_video_player = self.webcam_manager.start_video_playback(self.current_video_path)
            
            if self.active_video_player:
                # Connect signals for video updates
                self.active_video_player.frame_ready.connect(self._update_video_frame)
                self.active_video_player.position_changed.connect(self._update_video_position)
                self.active_video_player.duration_changed.connect(self._update_video_duration)
                self.active_video_player.playback_finished.connect(self._handle_video_finished)
                self.active_video_player.error_occurred.connect(self._handle_video_error)
                
                # Start playback
                if self.active_video_player.start_playback():
                    # Update UI
                    self.play_video_btn.setEnabled(False)
                    self.pause_video_btn.setEnabled(True)
                    self.stop_video_btn.setEnabled(True)
                    self.video_progress_slider.setEnabled(True)
                    
                    # Disable camera controls during video playback
                    self.start_preview_btn.setEnabled(False)
                    self.camera_combo.setEnabled(False)
                    self.refresh_cameras_btn.setEnabled(False)
                    
                    self._update_video_status("Video playback started")
                    logger.info(f"Video playback started: {self.current_video_path}")
                else:
                    self._update_video_status("Failed to start video playback")
                    self.active_video_player = None
            else:
                self._update_video_status("Failed to load video for playback")
                
        except Exception as e:
            logger.error(f"Error starting video playback: {e}")
            self._update_video_status(f"Error starting playback: {e}")
            QMessageBox.critical(self, "Video Error", f"Failed to start video playback: {e}")
    
    def _pause_video(self):
        """Pause video playback."""
        if self.active_video_player:
            self.active_video_player.pause_playback()
            self.play_video_btn.setEnabled(True)
            self.pause_video_btn.setEnabled(False)
            self._update_video_status("Video playback paused")
    
    def _resume_video(self):
        """Resume video playback (same as play when paused)."""
        if self.active_video_player:
            self.active_video_player.resume_playback()
            self.play_video_btn.setEnabled(False)
            self.pause_video_btn.setEnabled(True)
            self._update_video_status("Video playback resumed")
    
    def _stop_video(self):
        """Stop video playback."""
        if self.active_video_player:
            try:
                self.active_video_player.stop_playback()
                self.active_video_player = None
                
                # Update UI
                self.play_video_btn.setEnabled(True if self.current_video_path else False)
                self.pause_video_btn.setEnabled(False)
                self.stop_video_btn.setEnabled(False)
                self.video_progress_slider.setEnabled(False)
                self.video_progress_slider.setValue(0)
                
                # Re-enable camera controls
                self.start_preview_btn.setEnabled(True)
                self.camera_combo.setEnabled(True)
                self.refresh_cameras_btn.setEnabled(True)
                
                # Clear video display
                self.media_display_label.clear()
                self.media_display_label.setText("Video playback stopped\nLoad a video or start camera preview")
                
                self._update_video_status("Video playback stopped")
                logger.info("Video playback stopped")
                
            except Exception as e:
                logger.error(f"Error stopping video playback: {e}")
                self._update_video_status(f"Error stopping playback: {e}")
        
        if self.webcam_manager:
            self.webcam_manager.stop_video_playback()
    
    def _update_video_frame(self, frame):
        """Update the video display with a new frame."""
        try:
            if frame is None:
                return
                
            # Convert frame to RGB (OpenCV uses BGR)
            import cv2
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            
            # Create QImage
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Scale image to fit display label while maintaining aspect ratio
            display_size = self.media_display_label.size()
            scaled_pixmap = QPixmap.fromImage(q_image).scaled(
                display_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            
            # Set the pixmap to the label
            self.media_display_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logger.error(f"Error updating video frame: {e}")
            self._update_video_status(f"Frame update error: {e}")
    
    def _update_video_position(self, position_ms):
        """Update video playback position."""
        if not self._video_slider_dragging and self.active_video_player:
            duration_ms = self.active_video_player.get_duration_ms()
            if duration_ms > 0:
                progress = int((position_ms / duration_ms) * 100)
                self.video_progress_slider.setValue(progress)
            
            # Update time display
            self._update_time_display(position_ms, duration_ms)
    
    def _update_video_duration(self, duration_ms):
        """Update video duration display."""
        if duration_ms > 0:
            self.video_progress_slider.setMaximum(100)  # Use percentage
            self._update_time_display(0, duration_ms)
    
    def _update_time_display(self, position_ms, duration_ms):
        """Update the time display label."""
        def ms_to_time_str(ms):
            total_seconds = ms // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        
        position_str = ms_to_time_str(position_ms)
        duration_str = ms_to_time_str(duration_ms)
        self.video_time_label.setText(f"{position_str} / {duration_str}")
    
    def _video_slider_pressed(self):
        """Handle video slider press (start dragging)."""
        self._video_slider_dragging = True
    
    def _video_slider_released(self):
        """Handle video slider release (seek to position)."""
        self._video_slider_dragging = False
        
        if self.active_video_player:
            slider_value = self.video_progress_slider.value()
            duration_ms = self.active_video_player.get_duration_ms()
            
            if duration_ms > 0:
                target_position_ms = int((slider_value / 100.0) * duration_ms)
                self.active_video_player.seek_to_position(target_position_ms)
                self._update_video_status(f"Seeking to {target_position_ms // 1000}s")
    
    def _handle_video_finished(self):
        """Handle video playback finished."""
        self._update_video_status("Video playback finished")
        
        # Reset controls but keep video loaded
        self.play_video_btn.setEnabled(True)
        self.pause_video_btn.setEnabled(False)
        self.video_progress_slider.setValue(0)
        
        # Re-enable camera controls
        self.start_preview_btn.setEnabled(True)
        self.camera_combo.setEnabled(True)
        self.refresh_cameras_btn.setEnabled(True)
    
    def _handle_video_error(self, error_message):
        """Handle video playback error."""
        logger.error(f"Video error: {error_message}")
        self._update_video_status(f"Video error: {error_message}")
        self._stop_video()
        QMessageBox.critical(self, "Video Error", f"Video playback error: {error_message}")
    
    def _update_video_status(self, message):
        """Update the video status display."""
        timestamp = time.strftime("%H:%M:%S")
        self.media_status_display.append(f"[{timestamp}] Video: {message}")
        
        # Auto-scroll to bottom
        cursor = self.media_status_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End if PYQT_VERSION == 6 else cursor.End)
        self.media_status_display.setTextCursor(cursor)
    
    def _handle_play_button(self):
        """Handle play button click - either start new playback or resume paused playback."""
        if self.active_video_player and self.active_video_player.paused:
            self._resume_video()
        else:
            self._play_video()
    
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
            
            # Stop all components
            if self.sensor_manager:
                self.sensor_manager.cleanup()
            
            # Stop camera preview and video playback
            self._stop_camera_preview()
            self._stop_video()
            
            if self.time_server and self.time_server.running:
                self.time_server.stop_server()
            
            if self.session_synchronizer:
                self.session_synchronizer.stop_session_sync()
            
            if self.calibration_manager:
                self.calibration_manager.end_session()
            
            if self.security_manager:
                self.security_manager.cleanup()
            
            if self.server and self.server.running:
                self.server.stop_server()
            
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()
    
    def start_session(self):
        """Start a session (alias for start_recording)."""
        self._start_recording()
    
    def stop_session(self):
        """Stop a session (alias for stop_recording)."""
        self._stop_recording()