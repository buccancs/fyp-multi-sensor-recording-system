"""
PsychoPy-Inspired Enhanced Main Window for Multi-Sensor Recording System Controller

This module implements a clean, modern UI inspired by PsychoPy's professional interface design,
with improved visual hierarchy, better control organization, and enhanced stimulus presentation features.

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
    QMenuBar, QAction, QMessageBox, QFileDialog, QSpacerItem, QSizePolicy
)

# Import existing components
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .stimulus_controller import StimulusController

# Import networking and session management
from network.device_server import JsonSocketServer
from session.session_manager import SessionManager
from webcam.webcam_capture import WebcamCapture
from utils.logging_config import get_logger


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
        """Apply modern button styling"""
        if self.primary:
            style = """
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: 1px solid #005a9e;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                    border-color: #005a9e;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #f3f2f1;
                    color: #a19f9d;
                    border-color: #d2d0ce;
                }
            """
        else:
            style = """
                QPushButton {
                    background-color: #ffffff;
                    color: #323130;
                    border: 1px solid #d2d0ce;
                    border-radius: 4px;
                    padding: 6px 12px;
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
                    border-color: #d2d0ce;
                }
            """
        self.setStyleSheet(style)


class ModernGroupBox(QGroupBox):
    """Custom group box with modern styling"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        
        style = """
            QGroupBox {
                font-weight: 600;
                border: 1px solid #d2d0ce;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #faf9f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #323130;
                background-color: #faf9f8;
            }
        """
        self.setStyleSheet(style)


class StatusIndicator(QLabel):
    """Modern status indicator with color coding"""
    
    def __init__(self, text="Status", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(80, 24)
        self.setMaximumHeight(24)
        self.setFont(QFont("Segoe UI", 8))
        self.set_status("disconnected")
    
    def set_status(self, status):
        """Set status with appropriate color coding"""
        colors = {
            "connected": "#107c10",      # Green
            "disconnected": "#d13438",   # Red  
            "recording": "#ff8c00",      # Orange
            "ready": "#0078d4",          # Blue
            "warning": "#ffb900"         # Yellow
        }
        
        color = colors.get(status, "#605e5c")  # Default gray
        
        style = f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 4px;
                padding: 2px 8px;
                font-weight: 600;
            }}
        """
        self.setStyleSheet(style)


class EnhancedStimulusPanel(ModernGroupBox):
    """Enhanced stimulus control panel with modern design"""
    
    # Signals
    file_loaded = pyqtSignal(str)
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    volume_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__("Stimulus Control", parent)
        self.current_file = None
        self.is_playing = False
        self.duration = 0
        self.position = 0
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the enhanced stimulus control UI"""
        layout = QVBoxLayout(self)
        
        # File selection row
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("No stimulus file loaded")
        self.file_label.setFont(QFont("Segoe UI", 9))
        self.file_label.setStyleSheet("color: #605e5c; padding: 4px;")
        file_layout.addWidget(self.file_label, 1)
        
        self.browse_btn = ModernButton("Browse...", primary=False)
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        layout.addLayout(file_layout)
        
        # Media controls row
        controls_layout = QHBoxLayout()
        
        self.play_btn = ModernButton("▶ Play", primary=True)
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = ModernButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Volume control
        volume_label = QLabel("Volume:")
        volume_label.setFont(QFont("Segoe UI", 9))
        controls_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(80)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        controls_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(30)
        self.volume_label.setFont(QFont("Segoe UI", 9))
        controls_layout.addWidget(self.volume_label)
        
        layout.addLayout(controls_layout)
        
        # Timeline row
        timeline_layout = QHBoxLayout()
        
        self.time_label = QLabel("00:00")
        self.time_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        timeline_layout.addWidget(self.time_label)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.setEnabled(False)
        self.timeline_slider.sliderMoved.connect(self.seek_requested.emit)
        timeline_layout.addWidget(self.timeline_slider, 1)
        
        self.duration_label = QLabel("00:00")
        self.duration_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        timeline_layout.addWidget(self.duration_label)
        
        layout.addLayout(timeline_layout)
        
        # Connect volume slider to label update
        self.volume_slider.valueChanged.connect(lambda v: self.volume_label.setText(f"{v}%"))
    
    def browse_file(self):
        """Browse for stimulus file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Stimulus File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load stimulus file"""
        self.current_file = file_path
        filename = os.path.basename(file_path)
        self.file_label.setText(f"Loaded: {filename}")
        self.play_btn.setEnabled(True)
        self.timeline_slider.setEnabled(True)
        self.file_loaded.emit(file_path)
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start playback"""
        self.is_playing = True
        self.play_btn.setText("⏸ Pause")
        self.stop_btn.setEnabled(True)
        self.play_requested.emit()
    
    def pause_playback(self):
        """Pause playback"""
        self.is_playing = False
        self.play_btn.setText("▶ Play")
        self.pause_requested.emit()
    
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        self.play_btn.setText("▶ Play")
        self.stop_btn.setEnabled(False)
        self.timeline_slider.setValue(0)
        self.time_label.setText("00:00")
        self.stop_requested.emit()
    
    def update_position(self, position, duration):
        """Update timeline position"""
        self.position = position
        self.duration = duration
        
        if duration > 0:
            progress = int((position / duration) * 100)
            self.timeline_slider.setValue(progress)
        
        # Update time labels
        pos_time = self.format_time(position)
        dur_time = self.format_time(duration)
        self.time_label.setText(pos_time)
        self.duration_label.setText(dur_time)
    
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


class PsychoPyInspiredMainWindow(QMainWindow):
    """Main window with PsychoPy-inspired modern design"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # Initialize backend components
        self.session_manager = SessionManager()
        self.json_server = JsonSocketServer(session_manager=self.session_manager)
        self.webcam_capture = WebcamCapture()
        self.stimulus_controller = StimulusController(self)
        
        # State variables
        self.server_running = False
        self.webcam_previewing = False
        self.webcam_recording = False
        self.current_session_id = None
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        self.apply_modern_styling()
        
        self.logger.info("PsychoPy-inspired main window initialized")
    
    def init_ui(self):
        """Initialize the user interface with modern design"""
        self.setWindowTitle("Multi-Sensor Recording System - Enhanced Interface")
        self.setMinimumSize(1200, 800)
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application font
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        
        # Create central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create toolbar
        self.create_modern_toolbar()
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Left panel - Device Management
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Preview and Stimulus
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([300, 1000])
        main_layout.addWidget(content_splitter)
        
        # Create modern status bar
        self.create_modern_status_bar()
    
    def create_modern_toolbar(self):
        """Create modern toolbar with grouped actions"""
        toolbar = self.addToolBar("Main Controls")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        
        # Connection group
        self.connect_action = QAction("🔗 Connect", self)
        self.connect_action.setToolTip("Start device server and connect to devices")
        self.connect_action.triggered.connect(self.handle_connect)
        toolbar.addAction(self.connect_action)
        
        self.disconnect_action = QAction("🔌 Disconnect", self)
        self.disconnect_action.setToolTip("Stop device server and disconnect all devices")
        self.disconnect_action.triggered.connect(self.handle_disconnect)
        toolbar.addAction(self.disconnect_action)
        
        toolbar.addSeparator()
        
        # Session group
        self.start_session_action = QAction("🎬 Start Session", self)
        self.start_session_action.setToolTip("Begin new recording session")
        self.start_session_action.triggered.connect(self.handle_start_session)
        toolbar.addAction(self.start_session_action)
        
        self.stop_session_action = QAction("⏹ Stop Session", self)
        self.stop_session_action.setToolTip("End current recording session")
        self.stop_session_action.triggered.connect(self.handle_stop_session)
        self.stop_session_action.setEnabled(False)
        toolbar.addAction(self.stop_session_action)
        
        toolbar.addSeparator()
        
        # Status indicator
        self.server_status = StatusIndicator("Disconnected")
        toolbar.addWidget(self.server_status)
        
        # Apply toolbar styling
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #d2d0ce;
                spacing: 4px;
                padding: 4px;
            }
            QToolBar QAction {
                margin: 2px;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QToolBar QAction:hover {
                background-color: #e1dfdd;
            }
        """)
    
    def create_left_panel(self):
        """Create left panel with device management"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Device Status Section
        self.device_group = ModernGroupBox("Connected Devices")
        device_layout = QVBoxLayout(self.device_group)
        
        # Device list would go here - simplified for now
        self.device_status_label = QLabel("No devices connected")
        self.device_status_label.setAlignment(Qt.AlignCenter)
        self.device_status_label.setStyleSheet("color: #605e5c; padding: 20px;")
        device_layout.addWidget(self.device_status_label)
        
        layout.addWidget(self.device_group)
        
        # Session Info Section  
        self.session_group = ModernGroupBox("Session Information")
        session_layout = QVBoxLayout(self.session_group)
        
        self.session_info_label = QLabel("No active session")
        self.session_info_label.setAlignment(Qt.AlignCenter)
        self.session_info_label.setStyleSheet("color: #605e5c; padding: 20px;")
        session_layout.addWidget(self.session_info_label)
        
        layout.addWidget(self.session_group)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """Create right panel with preview and stimulus controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Preview Section
        self.preview_group = ModernGroupBox("Video Preview & Stimulus Control")
        preview_layout = QVBoxLayout(self.preview_group)
        
        # Import and create enhanced video player
        from .enhanced_video_player import EnhancedVideoPlayer
        
        self.enhanced_video_player = EnhancedVideoPlayer()
        preview_layout.addWidget(self.enhanced_video_player)
        
        layout.addWidget(self.preview_group)
        
        # Remove the old stimulus panel as it's now integrated
        # self.stimulus_panel = EnhancedStimulusPanel()
        # layout.addWidget(self.stimulus_panel)
        
        return panel
    
    def create_modern_status_bar(self):
        """Create modern status bar with multiple indicators"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #d2d0ce;
                padding: 4px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Main status message
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 9))
        status_bar.addWidget(self.status_label)
        
        status_bar.addPermanentWidget(QLabel("|"))
        
        # Recording indicator
        self.recording_status = StatusIndicator("Not Recording")
        self.recording_status.set_status("disconnected")
        status_bar.addPermanentWidget(self.recording_status)
        
        status_bar.addPermanentWidget(QLabel("|"))
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        status_bar.addPermanentWidget(self.time_label)
        
        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(1000)
        self.update_time_display()
    
    def setup_connections(self):
        """Setup signal connections"""
        # Enhanced video player connections
        self.enhanced_video_player.file_loaded.connect(self.on_video_file_loaded)
        self.enhanced_video_player.playback_started.connect(self.on_playback_started)
        self.enhanced_video_player.playback_paused.connect(self.on_playback_paused)
        self.enhanced_video_player.playback_stopped.connect(self.on_playback_stopped)
        self.enhanced_video_player.position_changed.connect(self.on_position_changed)
        
        # Server connections (simplified)
        # self.json_server.device_connected.connect(self.on_device_connected)
        # self.json_server.device_disconnected.connect(self.on_device_disconnected)
        
        self.logger.info("Signal connections established")
    
    def apply_modern_styling(self):
        """Apply modern styling to the entire application"""
        app_style = """
            QMainWindow {
                background-color: #ffffff;
                color: #323130;
            }
            QWidget {
                background-color: #ffffff;
                color: #323130;
            }
            QTabWidget::pane {
                border: 1px solid #d2d0ce;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #f3f2f1;
                color: #323130;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #d2d0ce;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #0078d4;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e1dfdd;
            }
        """
        self.setStyleSheet(app_style)
    
    def update_time_display(self):
        """Update time display in status bar"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
    
    # Event handlers
    def handle_connect(self):
        """Handle connect action"""
        if not self.server_running:
            self.logger.info("Starting device server...")
            # self.json_server.start()
            self.server_running = True
            self.server_status.set_status("connected")
            self.server_status.setText("Connected")
            self.status_label.setText("Server started - waiting for devices...")
            self.device_status_label.setText("Waiting for device connections...")
    
    def handle_disconnect(self):
        """Handle disconnect action"""
        if self.server_running:
            self.logger.info("Stopping device server...")
            # self.json_server.stop_server()
            self.server_running = False
            self.server_status.set_status("disconnected")
            self.server_status.setText("Disconnected")
            self.status_label.setText("Server stopped")
            self.device_status_label.setText("No devices connected")
    
    def handle_start_session(self):
        """Handle start session action"""
        if not self.server_running:
            QMessageBox.warning(self, "Warning", "Please connect to devices first.")
            return
        
        session_info = self.session_manager.create_session()
        self.current_session_id = session_info["session_id"]
        
        self.recording_status.set_status("recording")
        self.recording_status.setText("Recording")
        self.status_label.setText(f"Session {self.current_session_id} started")
        self.session_info_label.setText(f"Active Session: {self.current_session_id}")
        
        self.start_session_action.setEnabled(False)
        self.stop_session_action.setEnabled(True)
        
        self.logger.info(f"Session {self.current_session_id} started")
    
    def handle_stop_session(self):
        """Handle stop session action"""
        if self.current_session_id:
            completed_session = self.session_manager.end_session()
            
            self.recording_status.set_status("ready")
            self.recording_status.setText("Ready")
            self.status_label.setText("Session completed")
            self.session_info_label.setText("No active session")
            
            self.start_session_action.setEnabled(True)
            self.stop_session_action.setEnabled(False)
            
            if completed_session:
                duration = completed_session.get('duration', 0)
                self.logger.info(f"Session {self.current_session_id} completed (duration: {duration:.1f}s)")
            
            self.current_session_id = None
    
    # Enhanced video player event handlers
    def on_video_file_loaded(self, file_path):
        """Handle video file loaded"""
        filename = os.path.basename(file_path)
        self.status_label.setText(f"Loaded stimulus video: {filename}")
        self.logger.info(f"Video file loaded: {filename}")
    
    def on_playback_started(self):
        """Handle playback started"""
        self.status_label.setText("Video playback started")
        self.logger.info("Video playback started")
    
    def on_playback_paused(self):
        """Handle playback paused"""
        self.status_label.setText("Video playback paused")
        self.logger.info("Video playback paused")
    
    def on_playback_stopped(self):
        """Handle playback stopped"""
        self.status_label.setText("Video playback stopped")
        self.logger.info("Video playback stopped")
    
    def on_position_changed(self, position, duration):
        """Handle video position change"""
        # Update any position-dependent UI elements
        pass
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.server_running:
            self.handle_disconnect()
        
        if self.webcam_capture:
            self.webcam_capture.cleanup()
        
        self.logger.info("Application closing")
        event.accept()


# Alternative simplified entry point for testing
def main():
    """Main function for testing the enhanced window"""
    import sys
    import os
    
    # Set offscreen platform for headless operation
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = PsychoPyInspiredMainWindow()
    # window.show()  # Comment out for headless testing
    
    print("PsychoPy-inspired window created successfully")
    
    # For headless testing, just create and cleanup
    window.close()
    
    return True

if __name__ == "__main__":
    main()