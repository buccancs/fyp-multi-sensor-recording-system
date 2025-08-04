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
    QApplication, QSpinBox, QCheckBox, QLineEdit
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
    
    def setup_ui(self):
        """Setup the main user interface with tabbed layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # Create main tab widget
        self.main_tabs = QTabWidget()
        main_layout.addWidget(self.main_tabs)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_playback_tab()
        self.create_settings_tab()
        self.create_file_viewer_tab()
        
        # Setup menu and status bars
        self.create_menu_bar()
        self.create_status_bar()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with device management and recording controls"""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Create main splitter for dashboard
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Device management
        left_panel = self.create_device_panel()
        splitter.addWidget(left_panel)
        
        # Center panel - Live preview
        center_panel = self.create_live_preview_panel()
        splitter.addWidget(center_panel)
        
        # Right panel - Recording controls and logs
        right_panel = self.create_control_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30%, 40%, 30%)
        splitter.setSizes([350, 500, 350])
        
        self.main_tabs.addTab(tab_widget, "📊 Dashboard")
    
    def create_playback_tab(self):
        """Create playback tab for stimulus presentation and video playback"""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Create splitter for playback
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Playback controls and file browser
        left_panel = self.create_playback_controls_panel()
        splitter.addWidget(left_panel)
        
        # Center panel - Video preview and timeline
        center_panel = self.create_stimulus_panel()
        splitter.addWidget(center_panel)
        
        # Right panel - Session synchronization
        right_panel = self.create_sync_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (25%, 50%, 25%)
        splitter.setSizes([300, 600, 300])
        
        self.main_tabs.addTab(tab_widget, "▶️ Playback")
    
    def create_settings_tab(self):
        """Create settings tab for configuration options"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Create scroll area for settings
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(16)
        
        # Device Settings
        device_settings = self.create_device_settings_group()
        settings_layout.addWidget(device_settings)
        
        # Recording Settings
        recording_settings = self.create_recording_settings_group()
        settings_layout.addWidget(recording_settings)
        
        # Display Settings
        display_settings = self.create_display_settings_group()
        settings_layout.addWidget(display_settings)
        
        # Export Settings
        export_settings = self.create_export_settings_group()
        settings_layout.addWidget(export_settings)
        
        settings_layout.addStretch()
        
        scroll_area.setWidget(settings_widget)
        layout.addWidget(scroll_area)
        
        self.main_tabs.addTab(tab_widget, "⚙️ Settings")
    
    def create_file_viewer_tab(self):
        """Create file viewer tab for browsing and viewing recorded files"""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Create splitter for file viewer
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - File browser and filters
        left_panel = self.create_file_browser_panel()
        splitter.addWidget(left_panel)
        
        # Center panel - File preview and details
        center_panel = self.create_file_preview_panel()
        splitter.addWidget(center_panel)
        
        # Right panel - File operations and metadata
        right_panel = self.create_file_operations_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30%, 40%, 30%)
        splitter.setSizes([350, 500, 350])
        
        self.main_tabs.addTab(tab_widget, "📁 File Viewer")
    
    def create_live_preview_panel(self):
        """Create live preview panel for dashboard"""
        panel = ModernGroupBox("Live Preview")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Preview area (placeholder)
        self.live_preview_label = QLabel("Live Video Feeds")
        self.live_preview_label.setAlignment(Qt.AlignCenter)
        self.live_preview_label.setMinimumHeight(300)
        self.live_preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #d1d1d1;
                background-color: #f9f8f7;
                font-size: 16px;
                color: #605e5c;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.live_preview_label)
        
        # Quick actions
        actions_group = ModernGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        calibrate_btn = ModernButton("Quick Calibrate", primary=True)
        calibrate_btn.clicked.connect(self.quick_calibrate)
        actions_layout.addWidget(calibrate_btn)
        
        sync_btn = ModernButton("Sync Devices")
        sync_btn.clicked.connect(self.sync_devices)
        actions_layout.addWidget(sync_btn)
        
        test_btn = ModernButton("Test Recording")
        test_btn.clicked.connect(self.test_recording)
        actions_layout.addWidget(test_btn)
        
        layout.addWidget(actions_group)
        
        return panel
    
    def create_playback_controls_panel(self):
        """Create playback controls panel"""
        panel = ModernGroupBox("Playback Controls")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # File selection
        file_group = ModernGroupBox("Media Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Browse button
        browse_btn = ModernButton("Browse Media Files", primary=True)
        browse_btn.clicked.connect(self.browse_media_files)
        file_layout.addWidget(browse_btn)
        
        # Recent files list
        from PyQt5.QtWidgets import QListWidget, QListWidgetItem
        self.recent_files_list = QListWidget()
        self.recent_files_list.setMaximumHeight(120)
        
        # Add some sample recent files
        sample_files = [
            "experiment_2025_01_15_session_001.mp4",
            "calibration_video_thermal_rgb.avi", 
            "participant_P001_stimulus_001.mov",
            "training_session_overview.mp4"
        ]
        
        for file_name in sample_files:
            item = QListWidgetItem(file_name)
            self.recent_files_list.addItem(item)
        
        file_layout.addWidget(QLabel("Recent Files:"))
        file_layout.addWidget(self.recent_files_list)
        
        layout.addWidget(file_group)
        
        # Playback speed controls
        speed_group = ModernGroupBox("Playback Speed")
        speed_layout = QVBoxLayout(speed_group)
        
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(25)  # 0.25x
        self.speed_slider.setMaximum(200)  # 2.0x
        self.speed_slider.setValue(100)   # 1.0x
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setAlignment(Qt.AlignCenter)
        speed_layout.addWidget(self.speed_label)
        
        layout.addWidget(speed_group)
        
        # Playback options
        options_group = ModernGroupBox("Playback Options")
        options_layout = QVBoxLayout(options_group)
        
        from PyQt5.QtWidgets import QCheckBox
        self.loop_checkbox = QCheckBox("Loop playback")
        self.show_timestamps_checkbox = QCheckBox("Show timestamps")
        self.show_markers_checkbox = QCheckBox("Show event markers")
        
        self.show_timestamps_checkbox.setChecked(True)
        self.show_markers_checkbox.setChecked(True)
        
        options_layout.addWidget(self.loop_checkbox)
        options_layout.addWidget(self.show_timestamps_checkbox) 
        options_layout.addWidget(self.show_markers_checkbox)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        return panel
    
    def create_sync_panel(self):
        """Create synchronization panel for playback"""
        panel = ModernGroupBox("Session Synchronization")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Sync status
        sync_group = ModernGroupBox("Sync Status")
        sync_layout = QVBoxLayout(sync_group)
        
        # Time sync indicator
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        time_indicator = StatusIndicator("connected")
        time_layout.addWidget(time_indicator)
        
        time_label = QLabel("Time synchronized")
        time_layout.addWidget(time_label)
        time_layout.addStretch()
        
        sync_layout.addWidget(time_widget)
        
        # Session timeline
        self.sync_time_label = QLabel("00:00:00.000")
        self.sync_time_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.sync_time_label.setAlignment(Qt.AlignCenter)
        sync_layout.addWidget(self.sync_time_label)
        
        layout.addWidget(sync_group)
        
        # Event markers
        markers_group = ModernGroupBox("Event Markers")
        markers_layout = QVBoxLayout(markers_group)
        
        # Markers list
        from PyQt5.QtWidgets import QListWidget, QListWidgetItem
        self.markers_list = QListWidget()
        self.markers_list.setMaximumHeight(120)
        
        # Add sample markers
        sample_markers = [
            "00:02:15 - Stimulus Start",
            "00:02:18 - Participant Response", 
            "00:04:32 - Calibration Point",
            "00:07:45 - Stimulus End"
        ]
        
        for marker in sample_markers:
            item = QListWidgetItem(marker)
            self.markers_list.addItem(item)
        
        markers_layout.addWidget(self.markers_list)
        
        # Add marker button
        add_marker_btn = ModernButton("Add Marker")
        add_marker_btn.clicked.connect(self.add_playback_marker)
        markers_layout.addWidget(add_marker_btn)
        
        layout.addWidget(markers_group)
        
        layout.addStretch()
        
        return panel
    
    def create_device_settings_group(self):
        """Create device settings group"""
        group = ModernGroupBox("Device Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Connection settings
        conn_layout = QGridLayout()
        
        conn_layout.addWidget(QLabel("Server Port:"), 0, 0)
        from PyQt5.QtWidgets import QSpinBox
        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1000, 65535)
        self.port_spinbox.setValue(8080)
        conn_layout.addWidget(self.port_spinbox, 0, 1)
        
        conn_layout.addWidget(QLabel("Connection Timeout (s):"), 1, 0)
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 300)
        self.timeout_spinbox.setValue(30)
        conn_layout.addWidget(self.timeout_spinbox, 1, 1)
        
        layout.addLayout(conn_layout)
        
        # Auto-connect options
        from PyQt5.QtWidgets import QCheckBox
        self.auto_connect_checkbox = QCheckBox("Auto-connect to known devices")
        self.auto_reconnect_checkbox = QCheckBox("Auto-reconnect on connection loss")
        
        self.auto_connect_checkbox.setChecked(True)
        self.auto_reconnect_checkbox.setChecked(True)
        
        layout.addWidget(self.auto_connect_checkbox)
        layout.addWidget(self.auto_reconnect_checkbox)
        
        return group
    
    def create_recording_settings_group(self):
        """Create recording settings group"""
        group = ModernGroupBox("Recording Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        
        from PyQt5.QtWidgets import QLineEdit
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText("./recordings")
        output_layout.addWidget(self.output_dir_edit)
        
        browse_dir_btn = ModernButton("Browse")
        browse_dir_btn.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(browse_dir_btn)
        
        layout.addLayout(output_layout)
        
        # Recording options
        from PyQt5.QtWidgets import QCheckBox
        self.compress_checkbox = QCheckBox("Compress recordings")
        self.backup_checkbox = QCheckBox("Create backup copies")
        self.timestamp_checkbox = QCheckBox("Add timestamps to filenames")
        
        self.compress_checkbox.setChecked(True)
        self.timestamp_checkbox.setChecked(True)
        
        layout.addWidget(self.compress_checkbox)
        layout.addWidget(self.backup_checkbox)
        layout.addWidget(self.timestamp_checkbox)
        
        # Quality settings
        quality_layout = QGridLayout()
        
        quality_layout.addWidget(QLabel("Video Quality:"), 0, 0)
        from PyQt5.QtWidgets import QComboBox
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.quality_combo.setCurrentText("High")
        quality_layout.addWidget(self.quality_combo, 0, 1)
        
        quality_layout.addWidget(QLabel("Sample Rate (Hz):"), 1, 0)
        self.sample_rate_spinbox = QSpinBox()
        self.sample_rate_spinbox.setRange(1, 1000)
        self.sample_rate_spinbox.setValue(100)
        quality_layout.addWidget(self.sample_rate_spinbox, 1, 1)
        
        layout.addLayout(quality_layout)
        
        return group
    
    def create_display_settings_group(self):
        """Create display settings group"""
        group = ModernGroupBox("Display Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        from PyQt5.QtWidgets import QComboBox
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Modern (Default)", "Dark", "Light", "High Contrast"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        # Display options
        from PyQt5.QtWidgets import QCheckBox
        self.fullscreen_checkbox = QCheckBox("Use fullscreen for stimulus presentation")
        self.overlay_checkbox = QCheckBox("Show data overlay on preview")
        self.fps_checkbox = QCheckBox("Show FPS counter")
        
        self.fullscreen_checkbox.setChecked(True)
        self.overlay_checkbox.setChecked(True)
        
        layout.addWidget(self.fullscreen_checkbox)
        layout.addWidget(self.overlay_checkbox)
        layout.addWidget(self.fps_checkbox)
        
        # Preview settings
        preview_layout = QGridLayout()
        
        preview_layout.addWidget(QLabel("Preview Resolution:"), 0, 0)
        self.preview_res_combo = QComboBox()
        self.preview_res_combo.addItems(["640x480", "800x600", "1024x768", "1280x720", "1920x1080"])
        self.preview_res_combo.setCurrentText("1280x720")
        preview_layout.addWidget(self.preview_res_combo, 0, 1)
        
        preview_layout.addWidget(QLabel("Preview FPS:"), 1, 0)
        self.preview_fps_spinbox = QSpinBox()
        self.preview_fps_spinbox.setRange(10, 60)
        self.preview_fps_spinbox.setValue(30)
        preview_layout.addWidget(self.preview_fps_spinbox, 1, 1)
        
        layout.addLayout(preview_layout)
        
        return group
    
    def create_export_settings_group(self):
        """Create export settings group"""
        group = ModernGroupBox("Export Configuration") 
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Export format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        
        from PyQt5.QtWidgets import QComboBox
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "JSON", "HDF5", "MATLAB", "Excel"])
        self.export_format_combo.setCurrentText("CSV")
        format_layout.addWidget(self.export_format_combo)
        format_layout.addStretch()
        
        layout.addLayout(format_layout)
        
        # Export options
        from PyQt5.QtWidgets import QCheckBox
        self.include_metadata_checkbox = QCheckBox("Include metadata in export")
        self.include_timestamps_checkbox = QCheckBox("Include timestamps")
        self.separate_devices_checkbox = QCheckBox("Separate files per device")
        
        self.include_metadata_checkbox.setChecked(True)
        self.include_timestamps_checkbox.setChecked(True)
        
        layout.addWidget(self.include_metadata_checkbox)
        layout.addWidget(self.include_timestamps_checkbox)
        layout.addWidget(self.separate_devices_checkbox)
        
        # Apply/Reset buttons
        buttons_layout = QHBoxLayout()
        
        apply_btn = ModernButton("Apply Settings", primary=True)
        apply_btn.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(apply_btn)
        
        reset_btn = ModernButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return group
    
    def create_file_browser_panel(self):
        """Create file browser panel"""
        panel = ModernGroupBox("File Browser")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Directory navigation
        nav_layout = QHBoxLayout()
        
        from PyQt5.QtWidgets import QLineEdit
        self.current_dir_edit = QLineEdit()
        self.current_dir_edit.setText("./recordings")
        self.current_dir_edit.setReadOnly(True)
        nav_layout.addWidget(self.current_dir_edit)
        
        refresh_btn = ModernButton("⟲")
        refresh_btn.setMaximumWidth(40)
        refresh_btn.clicked.connect(self.refresh_file_browser)
        nav_layout.addWidget(refresh_btn)
        
        layout.addLayout(nav_layout)
        
        # File filters
        filter_group = ModernGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        from PyQt5.QtWidgets import QCheckBox
        self.video_filter = QCheckBox("Video files (.mp4, .avi)")
        self.data_filter = QCheckBox("Data files (.csv, .json)")
        self.log_filter = QCheckBox("Log files (.log, .txt)")
        self.all_filter = QCheckBox("All files")
        
        self.video_filter.setChecked(True)
        self.data_filter.setChecked(True)
        self.all_filter.setChecked(True)
        
        filter_layout.addWidget(self.video_filter)
        filter_layout.addWidget(self.data_filter)
        filter_layout.addWidget(self.log_filter)
        filter_layout.addWidget(self.all_filter)
        
        layout.addWidget(filter_group)
        
        # File tree
        from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Modified"])
        self.file_tree.setMaximumHeight(300)
        
        # Add sample files
        sample_sessions = [
            ("Session_2025_01_15_001", [
                ("participant_data.csv", "2.3 MB", "2025-01-15 14:30"),
                ("video_recording.mp4", "125.7 MB", "2025-01-15 14:30"),
                ("session_log.txt", "15.2 KB", "2025-01-15 14:35")
            ]),
            ("Session_2025_01_14_003", [
                ("gsr_data.csv", "1.8 MB", "2025-01-14 16:45"),
                ("thermal_video.avi", "89.3 MB", "2025-01-14 16:45"),
                ("calibration_results.json", "3.4 KB", "2025-01-14 16:40")
            ])
        ]
        
        for session_name, files in sample_sessions:
            session_item = QTreeWidgetItem([session_name, "Folder", ""])
            self.file_tree.addTopLevelItem(session_item)
            
            for file_name, size, modified in files:
                file_item = QTreeWidgetItem([file_name, size, modified])
                session_item.addChild(file_item)
        
        layout.addWidget(self.file_tree)
        
        layout.addStretch()
        
        return panel
    
    def create_file_preview_panel(self):
        """Create file preview panel"""
        panel = ModernGroupBox("File Preview")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Preview area
        self.file_preview_label = QLabel("Select a file to preview")
        self.file_preview_label.setAlignment(Qt.AlignCenter)
        self.file_preview_label.setMinimumHeight(300)
        self.file_preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #d1d1d1;
                background-color: #f9f8f7;
                font-size: 16px;
                color: #605e5c;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.file_preview_label)
        
        # File details
        details_group = ModernGroupBox("File Details")
        details_layout = QVBoxLayout(details_group)
        
        from PyQt5.QtWidgets import QTextEdit
        self.file_details_text = QTextEdit()
        self.file_details_text.setMaximumHeight(120)
        self.file_details_text.setReadOnly(True)
        self.file_details_text.setText("No file selected")
        details_layout.addWidget(self.file_details_text)
        
        layout.addWidget(details_group)
        
        return panel
    
    def create_file_operations_panel(self):
        """Create file operations panel"""
        panel = ModernGroupBox("File Operations")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Quick actions
        actions_group = ModernGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        open_btn = ModernButton("Open File", primary=True)
        open_btn.clicked.connect(self.open_selected_file)
        actions_layout.addWidget(open_btn)
        
        export_btn = ModernButton("Export Data")
        export_btn.clicked.connect(self.export_selected_file)
        actions_layout.addWidget(export_btn)
        
        analyze_btn = ModernButton("Analyze")
        analyze_btn.clicked.connect(self.analyze_selected_file)
        actions_layout.addWidget(analyze_btn)
        
        layout.addWidget(actions_group)
        
        # File management
        management_group = ModernGroupBox("File Management")
        management_layout = QVBoxLayout(management_group)
        
        copy_btn = ModernButton("Copy to...")
        copy_btn.clicked.connect(self.copy_selected_file)
        management_layout.addWidget(copy_btn)
        
        move_btn = ModernButton("Move to...")
        move_btn.clicked.connect(self.move_selected_file)
        management_layout.addWidget(move_btn)
        
        delete_btn = ModernButton("Delete")
        delete_btn.clicked.connect(self.delete_selected_file)
        management_layout.addWidget(delete_btn)
        
        layout.addWidget(management_group)
        
        # File statistics
        stats_group = ModernGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        from PyQt5.QtWidgets import QTextEdit
        self.file_stats_text = QTextEdit()
        self.file_stats_text.setMaximumHeight(100)
        self.file_stats_text.setReadOnly(True)
        self.file_stats_text.setText("Select a file to view statistics")
        stats_layout.addWidget(self.file_stats_text)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        return panel
    
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
    
    # New callback methods for tab functionality
    def quick_calibrate(self):
        """Quick calibration from dashboard"""
        self.log_message("Quick calibration initiated")
        QMessageBox.information(self, "Quick Calibrate", "Quick calibration started")
    
    def sync_devices(self):
        """Sync all connected devices"""
        self.log_message("Device synchronization initiated")
        QMessageBox.information(self, "Sync Devices", "Device synchronization completed")
    
    def test_recording(self):
        """Start a test recording"""
        self.log_message("Test recording started")
        QMessageBox.information(self, "Test Recording", "Test recording completed (5 seconds)")
    
    def browse_media_files(self):
        """Browse for media files"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Media File", "", 
            "Video Files (*.mp4 *.avi *.mov);;Audio Files (*.wav *.mp3);;All Files (*)"
        )
        if file_path:
            self.current_file_label.setText(os.path.basename(file_path))
            self.log_message(f"Media file loaded: {file_path}")
    
    def on_speed_changed(self, value):
        """Handle playback speed change"""
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        self.log_message(f"Playback speed changed to {speed:.1f}x")
    
    def add_playback_marker(self):
        """Add a new playback marker"""
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Add Marker", "Marker description:")
        if ok and text:
            # Get current time (placeholder)
            current_time = "00:05:23"
            marker_text = f"{current_time} - {text}"
            from PyQt5.QtWidgets import QListWidgetItem
            item = QListWidgetItem(marker_text)
            self.markers_list.addItem(item)
            self.log_message(f"Marker added: {marker_text}")
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)
            self.log_message(f"Output directory changed to: {directory}")
    
    def apply_settings(self):
        """Apply current settings"""
        self.log_message("Settings applied successfully")
        QMessageBox.information(self, "Settings", "Settings have been applied successfully")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Reset to defaults (placeholder)
            self.port_spinbox.setValue(8080)
            self.timeout_spinbox.setValue(30)
            self.output_dir_edit.setText("./recordings")
            self.quality_combo.setCurrentText("High")
            self.sample_rate_spinbox.setValue(100)
            self.log_message("Settings reset to defaults")
    
    def refresh_file_browser(self):
        """Refresh the file browser"""
        self.log_message("File browser refreshed")
        # In a real implementation, this would reload the file tree
    
    def open_selected_file(self):
        """Open the selected file"""
        current_item = self.file_tree.currentItem()
        if current_item and current_item.parent():  # Ensure it's a file, not a folder
            file_name = current_item.text(0)
            self.log_message(f"Opening file: {file_name}")
            QMessageBox.information(self, "Open File", f"Opening {file_name}")
    
    def export_selected_file(self):
        """Export the selected file"""
        current_item = self.file_tree.currentItem()
        if current_item and current_item.parent():
            file_name = current_item.text(0)
            self.log_message(f"Exporting file: {file_name}")
            QMessageBox.information(self, "Export File", f"Exporting {file_name}")
    
    def analyze_selected_file(self):
        """Analyze the selected file"""
        current_item = self.file_tree.currentItem()
        if current_item and current_item.parent():
            file_name = current_item.text(0)
            self.log_message(f"Analyzing file: {file_name}")
            QMessageBox.information(self, "Analyze File", f"Analysis started for {file_name}")
    
    def copy_selected_file(self):
        """Copy the selected file"""
        current_item = self.file_tree.currentItem()
        if current_item and current_item.parent():
            file_name = current_item.text(0)
            destination = QFileDialog.getExistingDirectory(self, "Select Destination")
            if destination:
                self.log_message(f"Copying {file_name} to {destination}")
                QMessageBox.information(self, "Copy File", f"File copied successfully")
    
    def move_selected_file(self):
        """Move the selected file"""
        current_item = self.file_tree.currentItem()
        if current_item and current_item.parent():
            file_name = current_item.text(0)
            destination = QFileDialog.getExistingDirectory(self, "Select Destination")
            if destination:
                self.log_message(f"Moving {file_name} to {destination}")
                QMessageBox.information(self, "Move File", f"File moved successfully")
    
    def delete_selected_file(self):
        """Delete the selected file"""
        current_item = self.file_tree.currentItem()
        if current_item and current_item.parent():
            file_name = current_item.text(0)
            reply = QMessageBox.question(
                self, "Delete File", 
                f"Are you sure you want to delete {file_name}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.log_message(f"Deleting file: {file_name}")
                # Remove from tree
                parent = current_item.parent()
                parent.removeChild(current_item)
                QMessageBox.information(self, "Delete File", f"File deleted successfully")


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