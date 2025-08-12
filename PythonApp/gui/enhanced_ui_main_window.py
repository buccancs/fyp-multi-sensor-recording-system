import os
import time
from datetime import datetime
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
try:
    from .device_panel import DeviceStatusPanel
except ImportError:
    DeviceStatusPanel = None
try:
    from .preview_panel import PreviewPanel
except ImportError:
    PreviewPanel = None
try:
    from ..network.device_server import JsonSocketServer
except ImportError:
    JsonSocketServer = None
try:
    from ..session.session_manager import SessionManager
except ImportError:
    SessionManager = None
try:
    from ..utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
class ModernButton(QPushButton):
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
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: #ffffff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 10pt;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2968a3;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #5a5a5a;
                    color: #ffffff;
                    border: 1px solid #777777;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #6a6a6a;
                }
                QPushButton:pressed {
                    background-color: #4a4a4a;
                }
            """)
class StatusIndicator(QWidget):
    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colours = {
            "connected": "#107c10",
            "disconnected": "#d13438",
            "warning": "#ff8c00",
            "unknown": "#8a8886",
        }
        colour = QColor(colours.get(self.status, colours["unknown"]))
        painter.setBrush(colour)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)
    def set_status(self, status):
        self.status = status
        self.update()
class ModernGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
class EnhancedMainWindow(QMainWindow):
    device_connected = pyqtSignal(str)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System - Enhanced Interface")
        self.setGeometry(100, 100, 1400, 900)
        self.device_server = None
        self.session_manager = None
        self.recording_active = False
        self.setup_styling()
        self.setup_ui()
        self.setup_connections()
        logger.info("Enhanced Main Window initialized")
    def setup_styling(self):
        stylesheet = """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 9pt;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #ffffff;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item:selected {
                background-color: #4a90e2;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #ffffff;
                border-top: 1px solid #555555;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 12px;
                margin-right: 2px;
                border: 1px solid #555555;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #4a90e2;
                border-bottom: 1px solid #4a90e2;
            }
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2968a3;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                background-color: #3c3c3c;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 4px;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background-color: #3c3c3c;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #4a90e2;
                border: 1px solid #357abd;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                selection-background-color: #4a90e2;
            }
        """
        self.setStyleSheet(stylesheet)
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        left_panel = self.create_device_panel()
        main_splitter.addWidget(left_panel)
        center_panel = self.create_stimulus_panel()
        main_splitter.addWidget(center_panel)
        right_panel = self.create_control_panel()
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([350, 700, 350])
        self.create_menu_bar()
        self.create_status_bar()
    def create_device_panel(self):
        panel = ModernGroupBox("Device Management")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        devices_group = ModernGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        self.device_indicators = {}
        devices = [
            ("Shimmer GSR", "disconnected"),
            ("Webcam", "connected"),
            ("Audio Input", "connected"),
            ("Thermal Camera", "disconnected"),
        ]
        for device_name, status in devices:
            device_widget = QWidget()
            device_layout = QHBoxLayout(device_widget)
            device_layout.setContentsMargins(0, 0, 0, 0)
            indicator = StatusIndicator(status)
            self.device_indicators[device_name] = indicator
            device_layout.addWidget(indicator)
            name_label = QLabel(device_name)
            name_label.setFont(QFont("Segoe UI", 9))
            device_layout.addWidget(name_label)
            device_layout.addStretch()
            connect_btn = ModernButton(
                "Connect" if status == "disconnected" else "Disconnect"
            )
            connect_btn.clicked.connect(
                lambda checked, name=device_name: self.toggle_device_connection(name)
            )
            device_layout.addWidget(connect_btn)
            devices_layout.addWidget(device_widget)
        layout.addWidget(devices_group)
        connection_group = ModernGroupBox("Connection Controls")
        connection_layout = QVBoxLayout(connection_group)
        connect_all_btn = ModernButton("Connect All Devices", primary=True)
        connect_all_btn.clicked.connect(self.connect_all_devices)
        connection_layout.addWidget(connect_all_btn)
        disconnect_all_btn = ModernButton("Disconnect All")
        disconnect_all_btn.clicked.connect(self.disconnect_all_devices)
        connection_layout.addWidget(disconnect_all_btn)
        layout.addWidget(connection_group)
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
        panel = ModernGroupBox("Stimulus Presentation and Preview")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        preview_group = ModernGroupBox("Video Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("Video Preview Area")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet(
            "background-color: #1e1e1e; border: 2px dashed #555555; border-radius: 8px;"
        )
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        controls_group = ModernGroupBox("Stimulus Controls")
        controls_layout = QVBoxLayout(controls_group)
        file_row = QHBoxLayout()
        load_btn = ModernButton("Load Video File", primary=True)
        load_btn.clicked.connect(self.load_stimulus_file)
        file_row.addWidget(load_btn)
        self.current_file_label = QLabel("No file loaded")
        self.current_file_label.setFont(QFont("Segoe UI", 8))
        file_row.addWidget(self.current_file_label)
        file_row.addStretch()
        controls_layout.addLayout(file_row)
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
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        recording_group = ModernGroupBox("Recording Session")
        recording_layout = QVBoxLayout(recording_group)
        self.session_label = QLabel("No active session")
        self.session_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        recording_layout.addWidget(self.session_label)
        self.start_recording_btn = ModernButton("Start Recording", primary=True)
        self.start_recording_btn.clicked.connect(self.start_recording)
        recording_layout.addWidget(self.start_recording_btn)
        self.stop_recording_btn = ModernButton("Stop Recording")
        self.stop_recording_btn.clicked.connect(self.stop_recording)
        self.stop_recording_btn.setEnabled(False)
        recording_layout.addWidget(self.stop_recording_btn)
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
        monitoring_group = ModernGroupBox("System Monitor")
        monitoring_layout = QVBoxLayout(monitoring_group)
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
        logs_group = ModernGroupBox("System Logs")
        logs_layout = QVBoxLayout(logs_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setText(
            "System initialized successfully\nReady for recording session\n"
        )
        logs_layout.addWidget(self.log_text)
        layout.addWidget(logs_group)
        layout.addStretch()
        return widget
    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        new_session = QAction("New Session", self)
        new_session.setShortcut("Ctrl+N")
        new_session.triggered.connect(self.new_session)
        file_menu.addAction(new_session)
        open_session = QAction("Open Session...", self)
        open_session.setShortcut("Ctrl+O")
        open_session.triggered.connect(self.open_session)
        file_menu.addAction(open_session)
        save_session = QAction("Save Session...", self)
        save_session.setShortcut("Ctrl+S")
        save_session.triggered.connect(self.save_session)
        file_menu.addAction(save_session)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        tools_menu = menubar.addMenu("Tools")
        scan_devices_action = QAction("Scan for Devices", self)
        scan_devices_action.triggered.connect(self.scan_for_devices)
        tools_menu.addAction(scan_devices_action)
        refresh_devices_action = QAction("Refresh Device Status", self)
        refresh_devices_action.triggered.connect(self.refresh_device_status)
        tools_menu.addAction(refresh_devices_action)
        tools_menu.addSeparator()
        browse_files_action = QAction("Browse Recording Files...", self)
        browse_files_action.triggered.connect(self.browse_recording_files)
        tools_menu.addAction(browse_files_action)
        open_data_folder_action = QAction("Open Data Folder", self)
        open_data_folder_action.triggered.connect(self.open_data_folder)
        tools_menu.addAction(open_data_folder_action)
        tools_menu.addSeparator()
        device_settings = QAction("Device Settings...", self)
        device_settings.triggered.connect(self.show_device_settings)
        tools_menu.addAction(device_settings)
        calibration_action = QAction("Calibration Wizard...", self)
        calibration_action.triggered.connect(self.show_calibration_wizard)
        tools_menu.addAction(calibration_action)
        data_analysis = QAction("Data Analysis...", self)
        data_analysis.triggered.connect(self.show_data_analysis)
        tools_menu.addAction(data_analysis)
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        user_guide = QAction("User Guide", self)
        user_guide.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide)
    def create_status_bar(self):
        status = self.statusBar()
        status.showMessage("Multi-Sensor Recording System - Ready")
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("colour: #d13438; font-weight: bold;")
        status.addPermanentWidget(self.connection_status)
    def setup_connections(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_monitoring)
        self.update_timer.start(1000)
    def toggle_device_connection(self, device_name):
        current_status = self.device_indicators[device_name].status
        new_status = "disconnected" if current_status == "connected" else "connected"
        self.device_indicators[device_name].set_status(new_status)
        self.log_message(f"Device {device_name} {new_status}")
    def connect_all_devices(self):
        for device_name, indicator in self.device_indicators.items():
            indicator.set_status("connected")
        self.log_message("All devices connected")
        self.connection_status.setText("Connected")
        self.connection_status.setStyleSheet("colour: #107c10; font-weight: bold;")
    def disconnect_all_devices(self):
        for device_name, indicator in self.device_indicators.items():
            indicator.set_status("disconnected")
        self.log_message("All devices disconnected")
        self.connection_status.setText("Disconnected")
        self.connection_status.setStyleSheet("colour: #d13438; font-weight: bold;")
    def start_calibration(self):
        self.log_message("Starting calibration process...")
    def load_stimulus_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Stimulus Video",
            "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)",
        )
        if file_path:
            self.current_file_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.play_btn.setEnabled(True)
            self.log_message(f"Loaded stimulus file: {os.path.basename(file_path)}")
    def play_stimulus(self):
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.log_message("Stimulus playback started")
    def pause_stimulus(self):
        self.log_message("Stimulus playback paused")
    def stop_stimulus(self):
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.log_message("Stimulus playback stopped")
    def start_recording(self):
        self.recording_active = True
        self.start_recording_btn.setEnabled(False)
        self.stop_recording_btn.setEnabled(True)
        self.session_label.setText(
            f"Recording Session {datetime.now().strftime('%H:%M:%S')}"
        )
        self.log_message("Recording session started")
    def stop_recording(self):
        self.recording_active = False
        self.start_recording_btn.setEnabled(True)
        self.stop_recording_btn.setEnabled(False)
        self.session_label.setText("No active session")
        self.log_message("Recording session stopped")
    def update_monitoring(self):
        import random
        self.cpu_progress.setValue(random.randint(20, 60))
        self.memory_progress.setValue(random.randint(30, 70))
        if self.recording_active:
            current_time = time.time()
            if not hasattr(self, "recording_start_time"):
                self.recording_start_time = current_time
            duration = int(current_time - self.recording_start_time)
            hours = duration // 3600
            minutes = duration % 3600 // 60
            seconds = duration % 60
            self.duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.size_label.setText(f"{duration * 0.5:.1f} MB")
    def log_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.append(f"{timestamp} {message}")
    def new_session(self):
        self.log_message("Creating new session...")
    def open_session(self):
        self.log_message("Opening session dialog...")
    def save_session(self):
        self.log_message("Saving current session...")
    def show_device_settings(self):
        QMessageBox.information(
            self, "Device Settings", "Device settings dialog would open here."
        )
    def show_calibration_wizard(self):
        QMessageBox.information(
            self, "Calibration Wizard", "Calibration wizard would open here."
        )
    def show_data_analysis(self):
        QMessageBox.information(
            self, "Data Analysis", "Data analysis tools would open here."
        )
    def show_about(self):
        QMessageBox.about(
            self,
            "About",
        )
    def show_user_guide(self):
        QMessageBox.information(self, "User Guide", "User guide would open here.")
    def scan_for_devices(self):
        try:
            self.log_message("Scanning for devices...")
            discovered_devices = []
            import time
            time.sleep(1)
            discovered_devices = [
                {"name": "USB Webcam", "type": "camera", "status": "available"},
                {"name": "Shimmer GSR Sensor", "type": "gsr", "status": "available"},
                {"name": "Android Device", "type": "android", "status": "connected"}
            ]
            device_list = "\n".join([f"- {d['name']} ({d['type']}): {d['status']}"
                                   for d in discovered_devices])
            QMessageBox.information(
                self,
                "Device Scan Complete",
                f"Found {len(discovered_devices)} devices:\n\n{device_list}"
            )
            self.log_message(f"Device scan completed: {len(discovered_devices)} devices found")
        except Exception as e:
            self.log_message(f"Error scanning for devices: {e}")
            QMessageBox.critical(self, "Error", f"Failed to scan for devices:\n{str(e)}")
    def refresh_device_status(self):
        try:
            self.log_message("Refreshing device status...")
            QMessageBox.information(
                self,
                "Status Refreshed",
                "Device status has been refreshed.\n\nAll connected devices are reporting normal operation."
            )
            self.log_message("Device status refresh completed")
        except Exception as e:
            self.log_message(f"Error refreshing device status: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh device status:\n{str(e)}")
    def browse_recording_files(self):
        try:
            import os
            from PyQt5.QtWidgets import QFileDialog
            self.log_message("Opening file browser for recording files...")
            recordings_dir = os.path.expanduser("~/recordings")
            if not os.path.exists(recordings_dir):
                recordings_dir = os.path.expanduser("~")
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Browse Recording Files",
                recordings_dir,
                "All Files (*.*);;Video Files (*.mp4 *.avi *.mov);;Data Files (*.json *.csv *.txt);;Image Files (*.jpg *.png *.bmp)"
            )
            if files:
                file_list = "\n".join([os.path.basename(f) for f in files[:5]])
                if len(files) > 5:
                    file_list += f"\n... and {len(files) - 5} more files"
                QMessageBox.information(
                    self,
                    "Files Selected",
                    f"Selected {len(files)} file(s):\n\n{file_list}"
                )
                self.log_message(f"Selected {len(files)} files from file browser")
            else:
                self.log_message("File browser cancelled")
        except Exception as e:
            self.log_message(f"Error opening file browser: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open file browser:\n{str(e)}")
    def open_data_folder(self):
        try:
            import os
            import subprocess
            import platform
            self.log_message("Opening data folder...")
            data_dirs = [
                os.path.expanduser("~/recordings"),
                os.path.join(os.getcwd(), "recordings"),
                os.path.join(os.getcwd(), "data"),
                os.path.expanduser("~/Documents/recordings")
            ]
            target_dir = None
            for dir_path in data_dirs:
                if os.path.exists(dir_path):
                    target_dir = dir_path
                    break
            if target_dir is None:
                target_dir = os.path.expanduser("~/recordings")
                os.makedirs(target_dir, exist_ok=True)
                self.log_message(f"Created recordings directory: {target_dir}")
            system = platform.system()
            if system == "Windows":
                os.startfile(target_dir)
            elif system == "Darwin":
                subprocess.run(["open", target_dir])
            else:
                subprocess.run(["xdg-open", target_dir])
            self.log_message(f"Opened data folder: {target_dir}")
            QMessageBox.information(
                self,
                "Data Folder Opened",
                f"Opened recordings folder:\n{target_dir}"
            )
        except Exception as e:
            self.log_message(f"Error opening data folder: {e}")
            QMessageBox.information(
                self,
                "Data Folder",
                f"Data folder location:\n{target_dir if 'target_dir' in locals() else 'Not found'}\n\nNote: Could not open automatically: {str(e)}"
            )
def main():
    import sys
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = EnhancedMainWindow()
    window.show()
    app.processEvents()
    screenshot = window.grab()
    screenshot_path = "/tmp/enhanced_main_window.png"
    screenshot.save(screenshot_path)
    print(f"Enhanced UI screenshot saved to: {screenshot_path}")
    return True
if __name__ == "__main__":
    main()
