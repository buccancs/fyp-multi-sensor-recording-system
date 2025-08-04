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

# Import device simulator for realistic demo data
try:
    from utils.device_simulator import get_device_simulator
    DEVICE_SIMULATOR_AVAILABLE = True
except ImportError:
    DEVICE_SIMULATOR_AVAILABLE = False
    get_device_simulator = lambda: None


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
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5a6fd8, stop:1 #6a4190);
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4e63c6, stop:1 #5e377e);
                }
                QPushButton:disabled {
                    background-color: #e8eaf6;
                    color: #9e9e9e;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2d3748;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 500;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f7fafc, stop:1 #edf2f7);
                    border-color: #cbd5e0;
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #edf2f7, stop:1 #e2e8f0);
                    border-color: #a0aec0;
                }
                QPushButton:disabled {
                    background-color: #f7fafc;
                    color: #a0aec0;
                    border-color: #e2e8f0;
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
        
        # Status colors - updated to modern palette
        colors = {
            "connected": "#10b981",    # Modern green
            "disconnected": "#ef4444", # Modern red
            "warning": "#f59e0b",      # Modern amber
            "unknown": "#6b7280"       # Modern gray
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
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 12px 0 12px;
                color: #1a202c;
                background-color: #ffffff;
                border-radius: 6px;
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
        
        # Setup UI
        self.setup_styling()
        self.setup_ui()
        self.setup_connections()
        
        logger.info("Enhanced Main Window initialized")
    
    def setup_styling(self):
        """Apply application-wide modern styling with enhanced visual design"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f7fafc, stop:1 #edf2f7);
                color: #1a202c;
            }
            
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                padding: 8px;
                color: white;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
            }
            
            QMenuBar::item:selected {
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
            }
            
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-top: 2px solid #e2e8f0;
                color: #4a5568;
                padding: 8px;
            }
            
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                width: 3px;
                height: 3px;
                border-radius: 2px;
            }
            
            QSplitter::handle:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            
            QLabel {
                color: #2d3748;
                font-weight: 500;
            }
            
            QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                selection-background-color: #667eea;
            }
            
            QTextEdit:focus {
                border-color: #667eea;
                outline: none;
            }
            
            QComboBox {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                min-height: 24px;
                font-weight: 500;
            }
            
            QComboBox:hover {
                border-color: #cbd5e0;
            }
            
            QComboBox:focus {
                border-color: #667eea;
            }
            
            QSlider::groove:horizontal {
                border: 2px solid #e2e8f0;
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f7fafc, stop:1 #edf2f7);
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: 2px solid #ffffff;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -8px 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4190);
                transform: scale(1.1);
            }
            
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f7fafc, stop:1 #edf2f7);
                font-weight: 600;
                color: #2d3748;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 6px;
                margin: 2px;
            }
            
            QTabWidget::pane {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                padding: 8px;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f7fafc, stop:1 #edf2f7);
                border: 2px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 24px;
                margin-right: 2px;
                font-weight: 500;
                color: #4a5568;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: 600;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e2e8f0, stop:1 #cbd5e0);
            }
        """)
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
        """Create device management panel with realistic fake devices"""
        panel = ModernGroupBox("Device Management")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Device status section
        devices_group = ModernGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Get realistic fake devices
        self.device_indicators = {}
        devices = []
        
        if DEVICE_SIMULATOR_AVAILABLE:
            simulator = get_device_simulator()
            all_devices = simulator.get_all_fake_devices()
            
            # Add Shimmer devices
            for device in all_devices["shimmer_devices"]:
                status = "connected" if device.is_connected else "disconnected"
                if device.is_recording:
                    status = "recording"
                
                device_name = f"{device.name} ({device.battery_level}%)"
                devices.append((device_name, status, device))
            
            # Add Android devices
            for device in all_devices["android_devices"]:
                status = "connected" if device.is_connected else "disconnected"
                if device.is_recording:
                    status = "recording"
                    
                device_name = f"{device.name} ({device.battery_level}%)"
                devices.append((device_name, status, device))
            
            # Add Webcam devices  
            for device in all_devices["webcam_devices"]:
                status = "connected" if device.is_connected else "disconnected"
                if device.is_recording:
                    status = "recording"
                    
                device_name = device.name
                devices.append((device_name, status, device))
        else:
            # Fallback to original static devices
            devices = [
                ("Shimmer GSR", "disconnected", None),
                ("Webcam", "connected", None),
                ("Audio Input", "connected", None),
                ("Thermal Camera", "disconnected", None)
            ]
        
        for device_name, status, device_obj in devices:
            device_widget = QWidget()
            device_layout = QHBoxLayout(device_widget)
            device_layout.setContentsMargins(0, 0, 0, 0)
            
            # Status indicator
            indicator = StatusIndicator(status)
            self.device_indicators[device_name] = indicator
            device_layout.addWidget(indicator)
            
            # Device name and details
            device_info_layout = QVBoxLayout()
            device_info_layout.setSpacing(2)
            
            name_label = QLabel(device_name)
            name_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
            device_info_layout.addWidget(name_label)
            
            # Add device details if available
            if device_obj:
                details_text = f"{device_obj.signal_quality} signal"
                if device_obj.sampling_rate:
                    details_text += f" • {device_obj.sampling_rate}Hz"
                if device_obj.data_samples_count > 0:
                    details_text += f" • {device_obj.data_samples_count:,} samples"
                    
                details_label = QLabel(details_text)
                details_label.setFont(QFont("Segoe UI", 8))
                details_label.setStyleSheet("color: #605e5c;")
                device_info_layout.addWidget(details_label)
            
            device_layout.addLayout(device_info_layout)
            device_layout.addStretch()
            
            # Connection button
            if status == "recording":
                connect_btn = ModernButton("Recording", primary=True)
                connect_btn.setEnabled(False)
            else:
                connect_btn = ModernButton("Connect" if status == "disconnected" else "Disconnect")
                connect_btn.clicked.connect(lambda checked, name=device_name: self.toggle_device_connection(name))
            device_layout.addWidget(connect_btn)
            
            devices_layout.addWidget(device_widget)
        
        layout.addWidget(devices_group)
        
        # Current session section
        if DEVICE_SIMULATOR_AVAILABLE:
            simulator = get_device_simulator()
            session_data = simulator.get_fake_session_data()
            
            session_group = ModernGroupBox("Current Session")
            session_layout = QVBoxLayout(session_group)
            
            current_session = session_data["current_session"]
            
            # Session ID
            session_id_label = QLabel(f"Session: {current_session['session_id']}")
            session_id_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
            session_layout.addWidget(session_id_label)
            
            # Participant
            participant_label = QLabel(f"Participant: {current_session['participant_id']}")
            participant_label.setFont(QFont("Segoe UI", 8))
            participant_label.setStyleSheet("color: #605e5c;")
            session_layout.addWidget(participant_label)
            
            # Duration 
            duration_label = QLabel(f"Duration: {current_session['duration_minutes']:.1f} min")
            duration_label.setFont(QFont("Segoe UI", 8))
            session_layout.addWidget(duration_label)
            
            # Status
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0, 0, 0, 0)
            
            status_indicator = StatusIndicator("recording" if current_session['status'] == "Recording" else "connected")
            status_layout.addWidget(status_indicator)
            
            status_label = QLabel(f"Status: {current_session['status']}")
            status_label.setFont(QFont("Segoe UI", 8))
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            
            session_layout.addWidget(status_widget)
            
            # Data quality and samples
            quality_label = QLabel(f"Quality: {current_session['data_quality']} • {current_session['total_samples']:,} samples")
            quality_label.setFont(QFont("Segoe UI", 8))
            quality_label.setStyleSheet("color: #605e5c;")
            session_layout.addWidget(quality_label)
            
            layout.addWidget(session_group)
        
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
        
        # Performance indicators
        perf_layout = QGridLayout()
        
        perf_layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setValue(25)
        perf_layout.addWidget(self.cpu_progress, 0, 1)
        
        perf_layout.addWidget(QLabel("Memory:"), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        self.memory_progress.setValue(45)
        perf_layout.addWidget(self.memory_progress, 1, 1)
        
        monitoring_layout.addLayout(perf_layout)
        
        layout.addWidget(monitoring_group)
        
        # System logs
        logs_group = ModernGroupBox("System Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setText("System initialized successfully\nReady for recording session\n")
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
        """Update system monitoring displays"""
        import random
        # Simulate CPU and memory usage
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