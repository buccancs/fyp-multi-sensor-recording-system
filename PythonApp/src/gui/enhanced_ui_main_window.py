"""
Enhanced Main Window with PsychoPy-Inspired Design
Clean, modern UI enhancement for the Multi-Sensor Recording System Controller

This module provides an enhanced version of the main window with:
- Modern, clean design inspired by PsychoPy
- Better visual hierarchy and spacing
- Professional color scheme
- Improved control organization
- Enhanced user experience

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
Enhancement: PsychoPy-Inspired UI Design
"""

import os
import time
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QProgressBar, QSlider, QComboBox,
    QTextEdit, QTabWidget, QFrame, QSplitter, QToolBar, QStatusBar,
    QMenuBar, QAction, QMessageBox, QFileDialog, QSpacerItem, QSizePolicy,
    QApplication
)

# Import basic components (avoiding problematic multimedia ones)
try:
    from .device_panel import DeviceStatusPanel
except ImportError:
    DeviceStatusPanel = None

try:
    from .preview_panel import PreviewPanel
except ImportError:
    PreviewPanel = None

# Import networking and session management (with fallbacks)
try:
    from network.device_server import JsonSocketServer
except ImportError:
    JsonSocketServer = None

try:
    from session.session_manager import SessionManager
except ImportError:
    SessionManager = None

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from utils.fake_data_generator import get_fake_data_generator, generate_realistic_device_status_text
except ImportError:
    # Fallback if fake data generator is not available
    def get_fake_data_generator():
        return None
    def generate_realistic_device_status_text():
        return "Device data generator not available"


class ModernButton(QPushButton):
    """Custom button with modern styling inspired by PsychoPy"""
    
    def __init__(self, text="", icon_path=None, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setFont(QFont("Segoe UI", 9))
        self.setMinimumHeight(32)
        self.setCursor(Qt.PointingHandCursor)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))
        
        self.update_style()
    
    def update_style(self):
        """Update button styling based on type"""
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #f3f2f1;
                    color: #a19f9d;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #323130;
                    border: 1px solid #8a8886;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 400;
                }
                QPushButton:hover {
                    background-color: #f3f2f1;
                    border-color: #323130;
                }
                QPushButton:pressed {
                    background-color: #edebe9;
                }
                QPushButton:disabled {
                    background-color: #f3f2f1;
                    color: #a19f9d;
                    border-color: #c8c6c4;
                }
            """)


class StatusIndicator(QWidget):
    """Modern status indicator with color coding"""
    
    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Status colors
        colors = {
            "connected": "#107c10",
            "disconnected": "#d13438", 
            "warning": "#ff8c00",
            "unknown": "#8a8886"
        }
        
        color = QColor(colors.get(self.status, colors["unknown"]))
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)
    
    def set_status(self, status):
        """Update status and repaint"""
        self.status = status
        self.update()


class ModernGroupBox(QGroupBox):
    """Enhanced group box with modern styling"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #323130;
            }
        """)


class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with PsychoPy-inspired design"""
    
    # Signals for better component communication
    device_connected = pyqtSignal(str)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System - Enhanced Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.device_server = None
        self.session_manager = None
        self.recording_active = False
        
        # Initialize fake data generator for realistic display
        self.fake_data = get_fake_data_generator()
        
        # Setup UI
        self.setup_styling()
        self.setup_ui()
        self.setup_connections()
        
        # Start realistic updates
        self.setup_realistic_updates()
        
        logger.info("Enhanced Main Window initialized")
    
    def setup_styling(self):
        """Apply application-wide modern styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #faf9f8;
                color: #323130;
            }
            
            QMenuBar {
                background-color: #f3f2f1;
                border-bottom: 1px solid #e1dfdd;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #e1dfdd;
            }
            
            QStatusBar {
                background-color: #f3f2f1;
                border-top: 1px solid #e1dfdd;
                color: #605e5c;
            }
            
            QSplitter::handle {
                background-color: #e1dfdd;
                width: 2px;
                height: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #c8c6c4;
            }
            
            QLabel {
                color: #323130;
            }
            
            QTextEdit {
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
            
            QComboBox {
                border: 1px solid #8a8886;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border-color: #323130;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #d1d1d1;
                height: 4px;
                background: #f3f2f1;
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005a9e;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
            
            QProgressBar {
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                text-align: center;
                background-color: #f3f2f1;
            }
            
            QProgressBar::chunk {
                background-color: #107c10;
                border-radius: 3px;
            }
        """)
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel - Device management
        left_panel = self.create_device_panel()
        main_splitter.addWidget(left_panel)
        
        # Center panel - Stimulus and preview
        center_panel = self.create_stimulus_panel()
        main_splitter.addWidget(center_panel)
        
        # Right panel - Recording controls and logs
        right_panel = self.create_control_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (25%, 50%, 25%)
        main_splitter.setSizes([350, 700, 350])
        
        # Setup menu and status bars
        self.create_menu_bar()
        self.create_status_bar()
    
    def create_device_panel(self):
        """Create device management panel"""
        panel = ModernGroupBox("Device Management")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Device status section
        devices_group = ModernGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Create scrollable device list with realistic data
        self.device_status_text = QTextEdit()
        self.device_status_text.setMaximumHeight(200)
        self.device_status_text.setReadOnly(True)
        self.device_status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f8f7;
                border: 1px solid #d1d1d1;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                color: #323130;
            }
        """)
        self.update_device_status_display()
        devices_layout.addWidget(self.device_status_text)
        
        # Device action buttons
        device_buttons_layout = QHBoxLayout()
        
        refresh_devices_btn = ModernButton("Refresh Devices")
        refresh_devices_btn.clicked.connect(self.refresh_device_status)
        device_buttons_layout.addWidget(refresh_devices_btn)
        
        device_diagnostics_btn = ModernButton("Device Diagnostics")
        device_diagnostics_btn.clicked.connect(self.show_device_diagnostics)
        device_buttons_layout.addWidget(device_diagnostics_btn)
        
        device_buttons_layout.addStretch()
        devices_layout.addLayout(device_buttons_layout)
        
        layout.addWidget(devices_group)
        
        # Connection controls
        connection_group = ModernGroupBox("Connection Controls")
        connection_layout = QVBoxLayout(connection_group)
        
        connect_all_btn = ModernButton("Connect All Devices", primary=True)
        connect_all_btn.clicked.connect(self.connect_all_devices)
        connection_layout.addWidget(connect_all_btn)
        
        disconnect_all_btn = ModernButton("Disconnect All")
        disconnect_all_btn.clicked.connect(self.disconnect_all_devices)
        connection_layout.addWidget(disconnect_all_btn)
        
        layout.addWidget(connection_group)
        
        # Calibration section
        calibration_group = ModernGroupBox("Calibration")
        calibration_layout = QVBoxLayout(calibration_group)
        
        start_calibration_btn = ModernButton("Start Calibration", primary=True)
        start_calibration_btn.clicked.connect(self.start_calibration)
        calibration_layout.addWidget(start_calibration_btn)
        
        calibration_status = QLabel("Status: Ready")
        calibration_status.setFont(QFont("Segoe UI", 8))
        calibration_layout.addWidget(calibration_status)
        
        layout.addWidget(calibration_group)
        
        layout.addStretch()
        
        return panel
    
    def create_stimulus_panel(self):
        """Create stimulus presentation panel"""
        panel = ModernGroupBox("Stimulus Presentation & Preview")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Video preview area
        preview_group = ModernGroupBox("Video Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview area (placeholder)
        self.preview_label = QLabel("Video Preview Area")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #d1d1d1;
                background-color: #f9f8f7;
                font-size: 16px;
                color: #605e5c;
                border-radius: 4px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Stimulus controls
        controls_group = ModernGroupBox("Stimulus Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # File management row
        file_row = QHBoxLayout()
        
        load_btn = ModernButton("Load Video File", primary=True)
        load_btn.clicked.connect(self.load_stimulus_file)
        file_row.addWidget(load_btn)
        
        self.current_file_label = QLabel("No file loaded")
        self.current_file_label.setFont(QFont("Segoe UI", 8))
        file_row.addWidget(self.current_file_label)
        file_row.addStretch()
        
        controls_layout.addLayout(file_row)
        
        # Playback controls row
        playback_row = QHBoxLayout()
        
        self.play_btn = ModernButton("Play")
        self.play_btn.clicked.connect(self.play_stimulus)
        self.play_btn.setEnabled(False)
        playback_row.addWidget(self.play_btn)
        
        self.pause_btn = ModernButton("Pause")
        self.pause_btn.clicked.connect(self.pause_stimulus)
        self.pause_btn.setEnabled(False)
        playback_row.addWidget(self.pause_btn)
        
        self.stop_btn = ModernButton("Stop")
        self.stop_btn.clicked.connect(self.stop_stimulus)
        self.stop_btn.setEnabled(False)
        playback_row.addWidget(self.stop_btn)
        
        playback_row.addStretch()
        
        controls_layout.addLayout(playback_row)
        
        # Progress and timing
        progress_layout = QHBoxLayout()
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        progress_layout.addWidget(self.progress_slider)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Consolas", 8))
        progress_layout.addWidget(self.time_label)
        
        controls_layout.addLayout(progress_layout)
        
        layout.addWidget(controls_group)
        
        return panel
    
    def create_control_panel(self):
        """Create recording controls and monitoring panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # Recording controls
        recording_group = ModernGroupBox("Recording Session")
        recording_layout = QVBoxLayout(recording_group)
        
        # Session info
        self.session_label = QLabel("No active session")
        self.session_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        recording_layout.addWidget(self.session_label)
        
        # Recording buttons
        self.start_recording_btn = ModernButton("Start Recording", primary=True)
        self.start_recording_btn.clicked.connect(self.start_recording)
        recording_layout.addWidget(self.start_recording_btn)
        
        self.stop_recording_btn = ModernButton("Stop Recording")
        self.stop_recording_btn.clicked.connect(self.stop_recording)
        self.stop_recording_btn.setEnabled(False)
        recording_layout.addWidget(self.stop_recording_btn)
        
        # Recording status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Duration:"))
        self.duration_label = QLabel("00:00:00")
        self.duration_label.setFont(QFont("Consolas", 9))
        status_layout.addWidget(self.duration_label)
        status_layout.addStretch()
        recording_layout.addLayout(status_layout)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Data size:"))
        self.size_label = QLabel("0 MB")
        self.size_label.setFont(QFont("Consolas", 9))
        size_layout.addWidget(self.size_label)
        size_layout.addStretch()
        recording_layout.addLayout(size_layout)
        
        layout.addWidget(recording_group)
        
        # System monitoring
        monitoring_group = ModernGroupBox("System Monitor")
        monitoring_layout = QVBoxLayout(monitoring_group)
        
        # Performance indicators with real-time labels
        perf_layout = QGridLayout()
        
        perf_layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setValue(25)
        perf_layout.addWidget(self.cpu_progress, 0, 1)
        
        self.cpu_label = QLabel("25%")
        self.cpu_label.setFont(QFont("Consolas", 8))
        perf_layout.addWidget(self.cpu_label, 0, 2)
        
        perf_layout.addWidget(QLabel("Memory:"), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        self.memory_progress.setValue(45)
        perf_layout.addWidget(self.memory_progress, 1, 1)
        
        self.memory_label = QLabel("45%")
        self.memory_label.setFont(QFont("Consolas", 8))
        perf_layout.addWidget(self.memory_label, 1, 2)
        
        perf_layout.addWidget(QLabel("Disk:"), 2, 0)
        self.disk_progress = QProgressBar()
        self.disk_progress.setMaximum(100)
        self.disk_progress.setValue(55)
        perf_layout.addWidget(self.disk_progress, 2, 1)
        
        self.disk_label = QLabel("55%")
        self.disk_label.setFont(QFont("Consolas", 8))
        perf_layout.addWidget(self.disk_label, 2, 2)
        
        perf_layout.addWidget(QLabel("Network:"), 3, 0)
        self.network_progress = QProgressBar()
        self.network_progress.setMaximum(100)
        self.network_progress.setValue(15)
        perf_layout.addWidget(self.network_progress, 3, 1)
        
        self.network_label = QLabel("15 MB/s")
        self.network_label.setFont(QFont("Consolas", 8))
        perf_layout.addWidget(self.network_label, 3, 2)
        
        monitoring_layout.addLayout(perf_layout)
        
        layout.addWidget(monitoring_group)
        
        # System logs
        logs_group = ModernGroupBox("System Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """)
        self.populate_realistic_logs()
        logs_layout.addWidget(self.log_text)
        
        layout.addWidget(logs_group)
        
        layout.addStretch()
        
        return widget
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_session = QAction('New Session', self)
        new_session.setShortcut('Ctrl+N')
        new_session.triggered.connect(self.new_session)
        file_menu.addAction(new_session)
        
        open_session = QAction('Open Session...', self)
        open_session.setShortcut('Ctrl+O')
        open_session.triggered.connect(self.open_session)
        file_menu.addAction(open_session)
        
        save_session = QAction('Save Session...', self)
        save_session.setShortcut('Ctrl+S')
        save_session.triggered.connect(self.save_session)
        file_menu.addAction(save_session)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        device_settings = QAction('Device Settings...', self)
        device_settings.triggered.connect(self.show_device_settings)
        tools_menu.addAction(device_settings)
        
        calibration_action = QAction('Calibration Wizard...', self)
        calibration_action.triggered.connect(self.show_calibration_wizard)
        tools_menu.addAction(calibration_action)
        
        data_analysis = QAction('Data Analysis...', self)
        data_analysis.triggered.connect(self.show_data_analysis)
        tools_menu.addAction(data_analysis)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        user_guide = QAction('User Guide', self)
        user_guide.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide)
    
    def create_status_bar(self):
        """Create application status bar"""
        status = self.statusBar()
        status.showMessage("Multi-Sensor Recording System - Ready")
        
        # Add permanent widgets
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: #d13438; font-weight: bold;")
        status.addPermanentWidget(self.connection_status)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Update timer for real-time monitoring
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_monitoring)
        self.update_timer.start(1000)  # Update every second
    
    # Event handlers
    def toggle_device_connection(self, device_name):
        """Toggle device connection"""
        current_status = self.device_indicators[device_name].status
        new_status = "disconnected" if current_status == "connected" else "connected"
        self.device_indicators[device_name].set_status(new_status)
        self.log_message(f"Device {device_name} {new_status}")
    
    def connect_all_devices(self):
        """Connect all devices"""
        for device_name, indicator in self.device_indicators.items():
            indicator.set_status("connected")
        self.log_message("All devices connected")
        self.connection_status.setText("Connected")
        self.connection_status.setStyleSheet("color: #107c10; font-weight: bold;")
    
    def disconnect_all_devices(self):
        """Disconnect all devices"""
        for device_name, indicator in self.device_indicators.items():
            indicator.set_status("disconnected")
        self.log_message("All devices disconnected")
        self.connection_status.setText("Disconnected")
        self.connection_status.setStyleSheet("color: #d13438; font-weight: bold;")
    
    def start_calibration(self):
        """Start device calibration"""
        self.log_message("Starting calibration process...")
    
    def load_stimulus_file(self):
        """Load stimulus video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Stimulus Video", "", 
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if file_path:
            self.current_file_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.play_btn.setEnabled(True)
            self.log_message(f"Loaded stimulus file: {os.path.basename(file_path)}")
    
    def play_stimulus(self):
        """Play stimulus video"""
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.log_message("Stimulus playback started")
    
    def pause_stimulus(self):
        """Pause stimulus video"""
        self.log_message("Stimulus playback paused")
    
    def stop_stimulus(self):
        """Stop stimulus video"""
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.log_message("Stimulus playback stopped")
    
    def start_recording(self):
        """Start recording session"""
        self.recording_active = True
        self.start_recording_btn.setEnabled(False)
        self.stop_recording_btn.setEnabled(True)
        self.session_label.setText(f"Recording Session {datetime.now().strftime('%H:%M:%S')}")
        self.log_message("Recording session started")
    
    def stop_recording(self):
        """Stop recording session"""
        self.recording_active = False
        self.start_recording_btn.setEnabled(True)
        self.stop_recording_btn.setEnabled(False)
        self.session_label.setText("No active session")
        self.log_message("Recording session stopped")
    
    def update_monitoring(self):
        """Update system monitoring displays with realistic data"""
        if self.fake_data:
            metrics = self.fake_data.get_system_metrics()
            
            # Update progress bars and labels
            self.cpu_progress.setValue(int(metrics.cpu_usage))
            self.cpu_label.setText(f"{metrics.cpu_usage:.1f}%")
            
            self.memory_progress.setValue(int(metrics.memory_usage))
            self.memory_label.setText(f"{metrics.memory_usage:.1f}%")
            
            self.disk_progress.setValue(int(metrics.disk_usage))
            self.disk_label.setText(f"{metrics.disk_usage:.1f}%")
            
            self.network_progress.setValue(int(min(100, metrics.network_activity)))
            self.network_label.setText(f"{metrics.network_activity:.1f} MB/s")
        else:
            # Fallback to simple random values
            import random
            self.cpu_progress.setValue(random.randint(20, 60))
            self.memory_progress.setValue(random.randint(30, 70))
        
        if self.recording_active:
            # Update recording duration and size
            current_time = time.time()
            if not hasattr(self, 'recording_start_time'):
                self.recording_start_time = current_time
            
            duration = int(current_time - self.recording_start_time)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            self.duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.size_label.setText(f"{duration * 0.5:.1f} MB")
    
    def log_message(self, message):
        """Add message to system log"""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.append(f"{timestamp} {message}")
    
    def setup_realistic_updates(self):
        """Setup timers for realistic data updates"""
        # Timer for system monitoring updates
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_monitoring)
        self.monitoring_timer.start(2000)  # Update every 2 seconds
        
        # Timer for device status updates
        self.device_timer = QTimer()
        self.device_timer.timeout.connect(self.update_device_status_display)
        self.device_timer.start(5000)  # Update every 5 seconds
        
        # Timer for log updates
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.add_realistic_log_entry)
        self.log_timer.start(10000)  # Update every 10 seconds
    
    def update_device_status_display(self):
        """Update device status display with realistic data"""
        if self.fake_data:
            devices = self.fake_data.get_device_list()
            device_lines = []
            
            for device in devices:
                storage_pct = (device.storage_available / device.storage_total) * 100
                status_icon = "🟢" if device.status == "connected" else "🔴" if device.status == "disconnected" else "🟡"
                
                device_line = (
                    f"{status_icon} {device.device_name}\n"
                    f"    Status: {device.status.title()} | "
                    f"Battery: {device.battery_level:.0f}% | "
                    f"Storage: {storage_pct:.0f}% | "
                    f"Temp: {device.temperature:.1f}°C\n"
                    f"    Connection: {device.connection_quality.title()} | "
                    f"Type: {device.device_type.replace('_', ' ').title()}\n"
                )
                device_lines.append(device_line)
            
            self.device_status_text.setText("\n".join(device_lines))
        else:
            self.device_status_text.setText("Device data generator not available")
    
    def refresh_device_status(self):
        """Manually refresh device status"""
        self.update_device_status_display()
        self.log_message("Device status refreshed")
    
    def show_device_diagnostics(self):
        """Show detailed device diagnostics"""
        if self.fake_data:
            devices = self.fake_data.get_device_list()
            diagnostics_text = "DEVICE DIAGNOSTICS REPORT\n" + "="*50 + "\n\n"
            
            for device in devices:
                diagnostics_text += f"Device: {device.device_name}\n"
                diagnostics_text += f"ID: {device.device_id}\n"
                diagnostics_text += f"Type: {device.device_type}\n"
                diagnostics_text += f"Status: {device.status}\n"
                diagnostics_text += f"Battery: {device.battery_level:.1f}%\n"
                diagnostics_text += f"Storage: {device.storage_available:.0f}/{device.storage_total:.0f} MB\n"
                diagnostics_text += f"Temperature: {device.temperature:.1f}°C\n"
                diagnostics_text += f"Connection Quality: {device.connection_quality}\n"
                diagnostics_text += f"Last Seen: {device.last_seen.strftime('%Y-%m-%d %H:%M:%S')}\n"
                diagnostics_text += "-" * 30 + "\n"
            
            QMessageBox.information(self, "Device Diagnostics", diagnostics_text)
        else:
            QMessageBox.information(self, "Device Diagnostics", "Device diagnostics not available")
    
    def populate_realistic_logs(self):
        """Populate log text with realistic entries"""
        if self.fake_data:
            logs = self.fake_data.get_realistic_log_entries(15)
            self.log_text.setText("\n".join(logs))
        else:
            self.log_text.setText("[00:00:00] System initialized successfully\n[00:00:01] Ready for recording session")
    
    def add_realistic_log_entry(self):
        """Add a new realistic log entry"""
        if self.fake_data:
            new_logs = self.fake_data.get_realistic_log_entries(1)
            if new_logs:
                self.log_text.append(new_logs[0])
    
    # Menu actions
    def new_session(self):
        """Create new session"""
        self.log_message("Creating new session...")
    
    def open_session(self):
        """Open existing session"""
        self.log_message("Opening session dialog...")
    
    def save_session(self):
        """Save current session"""
        self.log_message("Saving current session...")
    
    def show_device_settings(self):
        """Show device settings dialog"""
        QMessageBox.information(self, "Device Settings", "Device settings dialog would open here.")
    
    def show_calibration_wizard(self):
        """Show calibration wizard"""
        QMessageBox.information(self, "Calibration Wizard", "Calibration wizard would open here.")
    
    def show_data_analysis(self):
        """Show data analysis tools"""
        QMessageBox.information(self, "Data Analysis", "Data analysis tools would open here.")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About", 
            "Multi-Sensor Recording System\n"
            "Enhanced Interface v2.0\n\n"
            "Professional-grade data collection system\n"
            "inspired by PsychoPy design principles."
        )
    
    def show_user_guide(self):
        """Show user guide"""
        QMessageBox.information(self, "User Guide", "User guide would open here.")


def main():
    """Main function for testing"""
    import sys
    
    # Set environment for headless operation (for testing)
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = EnhancedMainWindow()
    window.show()
    
    # Process events to ensure rendering
    app.processEvents()
    
    # Take screenshot for demonstration
    screenshot = window.grab()
    screenshot_path = '/tmp/enhanced_main_window.png'
    screenshot.save(screenshot_path)
    print(f"Enhanced UI screenshot saved to: {screenshot_path}")
    
    return True


if __name__ == "__main__":
    main()