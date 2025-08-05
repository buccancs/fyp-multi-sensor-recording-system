import os
import time
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QPushButton, QProgressBar, QSlider, QComboBox, QTextEdit, QTabWidget, QFrame, QSplitter, QToolBar, QStatusBar, QMenuBar, QAction, QMessageBox, QFileDialog, QSpacerItem, QSizePolicy, QApplication
try:
    from .device_panel import DeviceStatusPanel
except ImportError:
    DeviceStatusPanel = None
try:
    from .preview_panel import PreviewPanel
except ImportError:
    PreviewPanel = None
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


class ModernButton(QPushButton):

    def __init__(self, text='', icon_path=None, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setFont(QFont('Segoe UI', 9))
        self.setMinimumHeight(32)
        self.setCursor(Qt.PointingHandCursor)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))
        self.update_style()

    def update_style(self):
        if self.primary:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color:
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color:
                }
                QPushButton:pressed {
                    background-color:
                }
                QPushButton:disabled {
                    background-color:
                    color:
                }
            """
                )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color:
                    color:
                    border: 1px solid
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 400;
                }
                QPushButton:hover {
                    background-color:
                    border-color:
                }
                QPushButton:pressed {
                    background-color:
                }
                QPushButton:disabled {
                    background-color:
                    color:
                    border-color:
                }
            """
                )


class StatusIndicator(QWidget):

    def __init__(self, status='disconnected', parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = {'connected': '#107c10', 'disconnected': '#d13438',
            'warning': '#ff8c00', 'unknown': '#8a8886'}
        color = QColor(colors.get(self.status, colors['unknown']))
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)

    def set_status(self, status):
        self.status = status
        self.update()


class ModernGroupBox(QGroupBox):

    def __init__(self, title='', parent=None):
        super().__init__(title, parent)
        self.setFont(QFont('Segoe UI', 9, QFont.Bold))
        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                border: 1px solid
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                background-color:
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color:
            }
        """
            )


class EnhancedMainWindow(QMainWindow):
    device_connected = pyqtSignal(str)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            'Multi-Sensor Recording System - Enhanced Interface')
        self.setGeometry(100, 100, 1400, 900)
        self.device_server = None
        self.session_manager = None
        self.recording_active = False
        self.setup_styling()
        self.setup_ui()
        self.setup_connections()
        logger.info('Enhanced Main Window initialized')

    def setup_styling(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color:
                color:
            }

            QMenuBar {
                background-color:
                border-bottom: 1px solid
                padding: 4px;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background-color:
            }

            QStatusBar {
                background-color:
                border-top: 1px solid
                color:
            }

            QSplitter::handle {
                background-color:
                width: 2px;
                height: 2px;
            }

            QSplitter::handle:hover {
                background-color:
            }

            QLabel {
                color:
            }

            QTextEdit {
                border: 1px solid
                border-radius: 4px;
                background-color:
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }

            QComboBox {
                border: 1px solid
                border-radius: 4px;
                padding: 6px 12px;
                background-color:
                min-height: 20px;
            }

            QComboBox:hover {
                border-color:
            }

            QSlider::groove:horizontal {
                border: 1px solid
                height: 4px;
                background:
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                background:
                border: 1px solid
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }

            QSlider::handle:horizontal:hover {
                background:
            }

            QProgressBar {
                border: 1px solid
                border-radius: 4px;
                text-align: center;
                background-color:
            }

            QProgressBar::chunk {
                background-color:
                border-radius: 3px;
            }
        """
            )

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
        panel = ModernGroupBox('Device Management')
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        devices_group = ModernGroupBox('Connected Devices')
        devices_layout = QVBoxLayout(devices_group)
        self.device_indicators = {}
        devices = [('Shimmer GSR', 'disconnected'), ('Webcam', 'connected'),
            ('Audio Input', 'connected'), ('Thermal Camera', 'disconnected')]
        for device_name, status in devices:
            device_widget = QWidget()
            device_layout = QHBoxLayout(device_widget)
            device_layout.setContentsMargins(0, 0, 0, 0)
            indicator = StatusIndicator(status)
            self.device_indicators[device_name] = indicator
            device_layout.addWidget(indicator)
            name_label = QLabel(device_name)
            name_label.setFont(QFont('Segoe UI', 9))
            device_layout.addWidget(name_label)
            device_layout.addStretch()
            connect_btn = ModernButton('Connect' if status ==
                'disconnected' else 'Disconnect')
            connect_btn.clicked.connect(lambda checked, name=device_name:
                self.toggle_device_connection(name))
            device_layout.addWidget(connect_btn)
            devices_layout.addWidget(device_widget)
        layout.addWidget(devices_group)
        connection_group = ModernGroupBox('Connection Controls')
        connection_layout = QVBoxLayout(connection_group)
        connect_all_btn = ModernButton('Connect All Devices', primary=True)
        connect_all_btn.clicked.connect(self.connect_all_devices)
        connection_layout.addWidget(connect_all_btn)
        disconnect_all_btn = ModernButton('Disconnect All')
        disconnect_all_btn.clicked.connect(self.disconnect_all_devices)
        connection_layout.addWidget(disconnect_all_btn)
        layout.addWidget(connection_group)
        calibration_group = ModernGroupBox('Calibration')
        calibration_layout = QVBoxLayout(calibration_group)
        start_calibration_btn = ModernButton('Start Calibration', primary=True)
        start_calibration_btn.clicked.connect(self.start_calibration)
        calibration_layout.addWidget(start_calibration_btn)
        calibration_status = QLabel('Status: Ready')
        calibration_status.setFont(QFont('Segoe UI', 8))
        calibration_layout.addWidget(calibration_status)
        layout.addWidget(calibration_group)
        layout.addStretch()
        return panel

    def create_stimulus_panel(self):
        panel = ModernGroupBox('Stimulus Presentation and Preview')
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        preview_group = ModernGroupBox('Video Preview')
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel('Video Preview Area')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed
                background-color:
                font-size: 16px;
                color:
                border-radius: 4px;
            }
        """
            )
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        controls_group = ModernGroupBox('Stimulus Controls')
        controls_layout = QVBoxLayout(controls_group)
        file_row = QHBoxLayout()
        load_btn = ModernButton('Load Video File', primary=True)
        load_btn.clicked.connect(self.load_stimulus_file)
        file_row.addWidget(load_btn)
        self.current_file_label = QLabel('No file loaded')
        self.current_file_label.setFont(QFont('Segoe UI', 8))
        file_row.addWidget(self.current_file_label)
        file_row.addStretch()
        controls_layout.addLayout(file_row)
        playback_row = QHBoxLayout()
        self.play_btn = ModernButton('Play')
        self.play_btn.clicked.connect(self.play_stimulus)
        self.play_btn.setEnabled(False)
        playback_row.addWidget(self.play_btn)
        self.pause_btn = ModernButton('Pause')
        self.pause_btn.clicked.connect(self.pause_stimulus)
        self.pause_btn.setEnabled(False)
        playback_row.addWidget(self.pause_btn)
        self.stop_btn = ModernButton('Stop')
        self.stop_btn.clicked.connect(self.stop_stimulus)
        self.stop_btn.setEnabled(False)
        playback_row.addWidget(self.stop_btn)
        playback_row.addStretch()
        controls_layout.addLayout(playback_row)
        progress_layout = QHBoxLayout()
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        progress_layout.addWidget(self.progress_slider)
        self.time_label = QLabel('00:00 / 00:00')
        self.time_label.setFont(QFont('Consolas', 8))
        progress_layout.addWidget(self.time_label)
        controls_layout.addLayout(progress_layout)
        layout.addWidget(controls_group)
        return panel

    def create_control_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        recording_group = ModernGroupBox('Recording Session')
        recording_layout = QVBoxLayout(recording_group)
        self.session_label = QLabel('No active session')
        self.session_label.setFont(QFont('Segoe UI', 9, QFont.Bold))
        recording_layout.addWidget(self.session_label)
        self.start_recording_btn = ModernButton('Start Recording', primary=True
            )
        self.start_recording_btn.clicked.connect(self.start_recording)
        recording_layout.addWidget(self.start_recording_btn)
        self.stop_recording_btn = ModernButton('Stop Recording')
        self.stop_recording_btn.clicked.connect(self.stop_recording)
        self.stop_recording_btn.setEnabled(False)
        recording_layout.addWidget(self.stop_recording_btn)
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel('Duration:'))
        self.duration_label = QLabel('00:00:00')
        self.duration_label.setFont(QFont('Consolas', 9))
        status_layout.addWidget(self.duration_label)
        status_layout.addStretch()
        recording_layout.addLayout(status_layout)
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel('Data size:'))
        self.size_label = QLabel('0 MB')
        self.size_label.setFont(QFont('Consolas', 9))
        size_layout.addWidget(self.size_label)
        size_layout.addStretch()
        recording_layout.addLayout(size_layout)
        layout.addWidget(recording_group)
        monitoring_group = ModernGroupBox('System Monitor')
        monitoring_layout = QVBoxLayout(monitoring_group)
        perf_layout = QGridLayout()
        perf_layout.addWidget(QLabel('CPU:'), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setValue(25)
        perf_layout.addWidget(self.cpu_progress, 0, 1)
        perf_layout.addWidget(QLabel('Memory:'), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        self.memory_progress.setValue(45)
        perf_layout.addWidget(self.memory_progress, 1, 1)
        monitoring_layout.addLayout(perf_layout)
        layout.addWidget(monitoring_group)
        logs_group = ModernGroupBox('System Logs')
        logs_layout = QVBoxLayout(logs_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setText(
            'System initialized successfully\nReady for recording session\n')
        logs_layout.addWidget(self.log_text)
        layout.addWidget(logs_group)
        layout.addStretch()
        return widget

    def create_menu_bar(self):
        menubar = self.menuBar()
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
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        user_guide = QAction('User Guide', self)
        user_guide.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide)

    def create_status_bar(self):
        status = self.statusBar()
        status.showMessage('Multi-Sensor Recording System - Ready')
        self.connection_status = QLabel('Disconnected')
        self.connection_status.setStyleSheet(
            'color: #d13438; font-weight: bold;')
        status.addPermanentWidget(self.connection_status)

    def setup_connections(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_monitoring)
        self.update_timer.start(1000)

    def toggle_device_connection(self, device_name):
        current_status = self.device_indicators[device_name].status
        new_status = ('disconnected' if current_status == 'connected' else
            'connected')
        self.device_indicators[device_name].set_status(new_status)
        self.log_message(f'Device {device_name} {new_status}')

    def connect_all_devices(self):
        for device_name, indicator in self.device_indicators.items():
            indicator.set_status('connected')
        self.log_message('All devices connected')
        self.connection_status.setText('Connected')
        self.connection_status.setStyleSheet(
            'color: #107c10; font-weight: bold;')

    def disconnect_all_devices(self):
        for device_name, indicator in self.device_indicators.items():
            indicator.set_status('disconnected')
        self.log_message('All devices disconnected')
        self.connection_status.setText('Disconnected')
        self.connection_status.setStyleSheet(
            'color: #d13438; font-weight: bold;')

    def start_calibration(self):
        self.log_message('Starting calibration process...')

    def load_stimulus_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
            'Load Stimulus Video', '',
            'Video Files (*.mp4 *.avi *.mov);;All Files (*)')
        if file_path:
            self.current_file_label.setText(
                f'Loaded: {os.path.basename(file_path)}')
            self.play_btn.setEnabled(True)
            self.log_message(
                f'Loaded stimulus file: {os.path.basename(file_path)}')

    def play_stimulus(self):
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.log_message('Stimulus playback started')

    def pause_stimulus(self):
        self.log_message('Stimulus playback paused')

    def stop_stimulus(self):
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.log_message('Stimulus playback stopped')

    def start_recording(self):
        self.recording_active = True
        self.start_recording_btn.setEnabled(False)
        self.stop_recording_btn.setEnabled(True)
        self.session_label.setText(
            f"Recording Session {datetime.now().strftime('%H:%M:%S')}")
        self.log_message('Recording session started')

    def stop_recording(self):
        self.recording_active = False
        self.start_recording_btn.setEnabled(True)
        self.stop_recording_btn.setEnabled(False)
        self.session_label.setText('No active session')
        self.log_message('Recording session stopped')

    def update_monitoring(self):
        import random
        self.cpu_progress.setValue(random.randint(20, 60))
        self.memory_progress.setValue(random.randint(30, 70))
        if self.recording_active:
            current_time = time.time()
            if not hasattr(self, 'recording_start_time'):
                self.recording_start_time = current_time
            duration = int(current_time - self.recording_start_time)
            hours = duration // 3600
            minutes = duration % 3600 // 60
            seconds = duration % 60
            self.duration_label.setText(
                f'{hours:02d}:{minutes:02d}:{seconds:02d}')
            self.size_label.setText(f'{duration * 0.5:.1f} MB')

    def log_message(self, message):
        timestamp = datetime.now().strftime('[%H:%M:%S]')
        self.log_text.append(f'{timestamp} {message}')

    def new_session(self):
        self.log_message('Creating new session...')

    def open_session(self):
        self.log_message('Opening session dialog...')

    def save_session(self):
        self.log_message('Saving current session...')

    def show_device_settings(self):
        QMessageBox.information(self, 'Device Settings',
            'Device settings dialog would open here.')

    def show_calibration_wizard(self):
        QMessageBox.information(self, 'Calibration Wizard',
            'Calibration wizard would open here.')

    def show_data_analysis(self):
        QMessageBox.information(self, 'Data Analysis',
            'Data analysis tools would open here.')

    def show_about(self):
        QMessageBox.about(self, 'About',
            """Multi-Sensor Recording System
Enhanced Interface v2.0

Professional-grade data collection system
inspired by PsychoPy design principles."""
            )

    def show_user_guide(self):
        QMessageBox.information(self, 'User Guide',
            'User guide would open here.')


def main():
    import sys
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EnhancedMainWindow()
    window.show()
    app.processEvents()
    screenshot = window.grab()
    screenshot_path = '/tmp/enhanced_main_window.png'
    screenshot.save(screenshot_path)
    print(f'Enhanced UI screenshot saved to: {screenshot_path}')
    return True


if __name__ == '__main__':
    main()
