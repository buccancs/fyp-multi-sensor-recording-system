"""
Enhanced Main Window for Dual Webcam Recording System

This module extends the existing MainWindow to support dual Logitech Brio webcam 
recording with master clock synchronization across all connected devices including 
Android phone sensors.

Features:
- Dual webcam preview and recording
- Master clock synchronization with Android devices
- Synchronized recording control across all sensors
- Real-time sync quality monitoring
- Enhanced UI for dual camera management

Author: Multi-Sensor Recording System Team  
Date: 2025-07-31
"""

import os
import sys
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QAction, QMessageBox, QDockWidget, QPlainTextEdit, QLabel,
    QPushButton, QGroupBox, QProgressBar, QFrame, QSplitter,
    QTabWidget, QTextEdit, QCheckBox, QSpinBox, QComboBox
)

# Import existing components
from gui.main_window import MainWindow as BaseMainWindow
from gui.device_panel import DeviceStatusPanel
from gui.preview_panel import PreviewPanel

# Import new dual webcam components
from webcam.dual_webcam_capture import DualWebcamCapture, test_dual_webcam_access
from master_clock_synchronizer import MasterClockSynchronizer, get_master_synchronizer
from session.session_manager import SessionManager
from utils.logging_config import get_logger

logger = get_logger(__name__)


class DualWebcamPreviewPanel(QWidget):
    """Preview panel for dual webcam feeds."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dual preview UI."""
        layout = QHBoxLayout(self)
        
        # Camera 1 preview
        camera1_group = QGroupBox("Camera 1 (Logitech Brio)")
        camera1_layout = QVBoxLayout(camera1_group)
        
        self.camera1_label = QLabel("Camera 1 Preview")
        self.camera1_label.setFixedSize(640, 360)
        self.camera1_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.camera1_label.setAlignment(Qt.AlignCenter)
        self.camera1_label.setText("Camera 1\nNo Preview")
        
        self.camera1_status = QLabel("Status: Disconnected")
        camera1_layout.addWidget(self.camera1_label)
        camera1_layout.addWidget(self.camera1_status)
        
        # Camera 2 preview
        camera2_group = QGroupBox("Camera 2 (Logitech Brio)")
        camera2_layout = QVBoxLayout(camera2_group)
        
        self.camera2_label = QLabel("Camera 2 Preview")
        self.camera2_label.setFixedSize(640, 360)
        self.camera2_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.camera2_label.setAlignment(Qt.AlignCenter)
        self.camera2_label.setText("Camera 2\nNo Preview")
        
        self.camera2_status = QLabel("Status: Disconnected")
        camera2_layout.addWidget(self.camera2_label)
        camera2_layout.addWidget(self.camera2_status)
        
        layout.addWidget(camera1_group)
        layout.addWidget(camera2_group)
        
    def update_camera1_frame(self, pixmap: QPixmap):
        """Update camera 1 preview frame."""
        if pixmap:
            self.camera1_label.setPixmap(pixmap.scaled(
                self.camera1_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            
    def update_camera2_frame(self, pixmap: QPixmap):
        """Update camera 2 preview frame."""
        if pixmap:
            self.camera2_label.setPixmap(pixmap.scaled(
                self.camera2_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            
    def update_camera_status(self, camera_num: int, status: str):
        """Update camera status display."""
        if camera_num == 1:
            self.camera1_status.setText(f"Status: {status}")
        elif camera_num == 2:
            self.camera2_status.setText(f"Status: {status}")


class SynchronizationStatusPanel(QWidget):
    """Panel for displaying synchronization status."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the synchronization status UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Synchronization Status")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Master clock info
        master_group = QGroupBox("Master Clock (PC)")
        master_layout = QVBoxLayout(master_group)
        
        self.master_time_label = QLabel("Master Time: --")
        self.ntp_status_label = QLabel("NTP Server: Stopped")
        self.connected_devices_label = QLabel("Connected Devices: 0")
        
        master_layout.addWidget(self.master_time_label)
        master_layout.addWidget(self.ntp_status_label)
        master_layout.addWidget(self.connected_devices_label)
        
        layout.addWidget(master_group)
        
        # Sync quality indicators
        sync_group = QGroupBox("Synchronization Quality")
        sync_layout = QVBoxLayout(sync_group)
        
        self.webcam_sync_label = QLabel("Webcam Sync: --")
        self.webcam_sync_bar = QProgressBar()
        self.webcam_sync_bar.setRange(0, 100)
        
        self.android_sync_label = QLabel("Android Devices: --")
        self.android_sync_bar = QProgressBar()
        self.android_sync_bar.setRange(0, 100)
        
        sync_layout.addWidget(self.webcam_sync_label)
        sync_layout.addWidget(self.webcam_sync_bar)
        sync_layout.addWidget(self.android_sync_label)
        sync_layout.addWidget(self.android_sync_bar)
        
        layout.addWidget(sync_group)
        
        # Device list
        devices_group = QGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_list = QTextEdit()
        self.devices_list.setMaximumHeight(150)
        self.devices_list.setReadOnly(True)
        
        devices_layout.addWidget(self.devices_list)
        layout.addWidget(devices_group)
        
    def update_master_time(self, timestamp: float):
        """Update master time display."""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        self.master_time_label.setText(f"Master Time: {dt.strftime('%H:%M:%S.%f')[:-3]}")
        
    def update_sync_quality(self, webcam_quality: float, android_quality: float):
        """Update synchronization quality displays."""
        # Update webcam sync
        webcam_percent = int(webcam_quality * 100)
        self.webcam_sync_bar.setValue(webcam_percent)
        self.webcam_sync_label.setText(f"Webcam Sync: {webcam_percent}%")
        
        # Update Android sync
        android_percent = int(android_quality * 100)
        self.android_sync_bar.setValue(android_percent)
        self.android_sync_label.setText(f"Android Devices: {android_percent}%")
        
    def update_device_list(self, devices: dict):
        """Update connected devices list."""
        device_text = ""
        for device_id, status in devices.items():
            sync_quality = int(status.sync_quality * 100)
            device_text += f"{device_id} ({status.device_type}): {sync_quality}% sync\n"
            
        self.devices_list.setText(device_text)
        self.connected_devices_label.setText(f"Connected Devices: {len(devices)}")


class RecordingControlPanel(QWidget):
    """Enhanced recording control panel for synchronized recording."""
    
    # Signals
    start_recording_requested = pyqtSignal(str)  # session_id
    stop_recording_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the recording control UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Synchronized Recording Control")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Session settings
        session_group = QGroupBox("Session Settings")
        session_layout = QGridLayout(session_group)
        
        session_layout.addWidget(QLabel("Session ID:"), 0, 0)
        self.session_id_input = QComboBox()
        self.session_id_input.setEditable(True)
        self.session_id_input.addItems(["session_001", "session_002", "session_003"])
        session_layout.addWidget(self.session_id_input, 0, 1)
        
        # Recording options
        self.record_webcam_check = QCheckBox("Record Webcams (Dual Brio 4K)")
        self.record_webcam_check.setChecked(True)
        self.record_android_video_check = QCheckBox("Record Android Video")
        self.record_android_video_check.setChecked(True)
        self.record_thermal_check = QCheckBox("Record Thermal Camera")
        self.record_thermal_check.setChecked(True)
        self.record_shimmer_check = QCheckBox("Record Shimmer Sensors")
        self.record_shimmer_check.setChecked(False)
        
        session_layout.addWidget(self.record_webcam_check, 1, 0, 1, 2)
        session_layout.addWidget(self.record_android_video_check, 2, 0, 1, 2)
        session_layout.addWidget(self.record_thermal_check, 3, 0, 1, 2)
        session_layout.addWidget(self.record_shimmer_check, 4, 0, 1, 2)
        
        layout.addWidget(session_group)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Synchronized Recording")
        self.start_button.setStyleSheet("QPushButton { background-color: green; color: white; font-weight: bold; }")
        self.start_button.clicked.connect(self.start_recording)
        
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setStyleSheet("QPushButton { background-color: red; color: white; font-weight: bold; }")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        
        layout.addLayout(controls_layout)
        
        # Status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid gray; }")
        layout.addWidget(self.status_label)
        
    def start_recording(self):
        """Handle start recording button click."""
        if not self.is_recording:
            session_id = self.session_id_input.currentText().strip()
            if not session_id:
                QMessageBox.warning(self, "Warning", "Please enter a session ID")
                return
                
            self.start_recording_requested.emit(session_id)
            
    def stop_recording(self):
        """Handle stop recording button click."""
        if self.is_recording:
            self.stop_recording_requested.emit()
            
    def set_recording_state(self, is_recording: bool):
        """Update UI based on recording state."""
        self.is_recording = is_recording
        self.start_button.setEnabled(not is_recording)
        self.stop_button.setEnabled(is_recording)
        
        if is_recording:
            self.status_label.setText("Status: Recording...")
            self.status_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid red; background-color: #ffeeee; }")
        else:
            self.status_label.setText("Status: Ready")
            self.status_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid gray; }")


class DualWebcamMainWindow(QMainWindow):
    """
    Enhanced Main Window for Dual Webcam Recording System.
    
    Integrates dual Logitech Brio webcam recording with master clock 
    synchronization for coordinated multi-device recording.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System - Dual Webcam Edition")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize components
        self.session_manager = SessionManager()
        self.master_synchronizer = None
        self.dual_webcam = None
        
        # State tracking
        self.is_recording = False
        self.current_session_id = None
        
        # Setup UI
        self.init_ui()
        
        # Initialize backend components
        self.init_backend_components()
        
        # Connect signals
        self.connect_signals()
        
        logger.info("DualWebcamMainWindow initialized")

    def init_ui(self):
        """Initialize the user interface."""
        # Create menu bar
        self.create_menu_bar()
        
        # Create main widget with tab layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Recording tab
        self.create_recording_tab()
        
        # Monitoring tab
        self.create_monitoring_tab()
        
        # Create status bar
        self.statusBar().showMessage("Ready - Initializing dual webcam system...")

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Test webcams action
        test_action = QAction('Test Dual Webcams', self)
        test_action.triggered.connect(self.test_webcams)
        file_menu.addAction(test_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        # Sync status action
        sync_action = QAction('Check Synchronization', self)
        sync_action.triggered.connect(self.check_synchronization)
        tools_menu.addAction(sync_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_recording_tab(self):
        """Create the main recording interface tab."""
        recording_widget = QWidget()
        layout = QHBoxLayout(recording_widget)
        
        # Left panel: Controls and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        # Recording controls
        self.recording_panel = RecordingControlPanel()
        left_layout.addWidget(self.recording_panel)
        
        # Synchronization status
        self.sync_panel = SynchronizationStatusPanel()
        left_layout.addWidget(self.sync_panel)
        
        left_layout.addStretch()
        
        # Right panel: Camera previews
        self.preview_panel = DualWebcamPreviewPanel()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.preview_panel)
        
        self.tab_widget.addTab(recording_widget, "Recording")

    def create_monitoring_tab(self):
        """Create the monitoring and logs tab."""
        monitoring_widget = QWidget()
        layout = QVBoxLayout(monitoring_widget)
        
        # Log display
        log_group = QGroupBox("System Logs")
        log_layout = QVBoxLayout(log_group)
        
        self.log_display = QPlainTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumBlockCount(1000)  # Limit log size
        
        log_layout.addWidget(self.log_display)
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(monitoring_widget, "Monitoring")

    def init_backend_components(self):
        """Initialize backend components."""
        try:
            # Test webcam access first
            if not test_dual_webcam_access():
                QMessageBox.warning(self, "Webcam Error", 
                    "Could not access dual webcams. Please ensure two cameras are connected.")
                self.statusBar().showMessage("Webcam access failed")
                return
            
            # Initialize master synchronizer
            self.master_synchronizer = MasterClockSynchronizer()
            
            # Initialize dual webcam capture
            self.dual_webcam = DualWebcamCapture(
                camera1_index=0,
                camera2_index=1,
                recording_fps=30,
                resolution=(3840, 2160),  # 4K for Brio
                sync_callback=self.on_webcam_sync_update
            )
            
            # Start master synchronizer
            if self.master_synchronizer.start():
                self.statusBar().showMessage("Master synchronization system started")
                self.sync_panel.ntp_status_label.setText("NTP Server: Running")
                
                # Add webcam sync callback
                self.master_synchronizer.add_webcam_sync_callback(self.on_master_sync_update)
                self.master_synchronizer.add_sync_status_callback(self.on_sync_status_update)
                
            else:
                QMessageBox.critical(self, "Sync Error", "Failed to start synchronization system")
                
            # Start webcam preview
            if self.dual_webcam.initialize_cameras():
                self.dual_webcam.start_preview()
                self.statusBar().showMessage("Dual webcam system ready")
            else:
                QMessageBox.warning(self, "Camera Error", "Failed to initialize cameras")
                
        except Exception as e:
            error_msg = f"Error initializing backend: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Initialization Error", error_msg)

    def connect_signals(self):
        """Connect UI signals to handlers."""
        # Recording control signals
        self.recording_panel.start_recording_requested.connect(self.start_synchronized_recording)
        self.recording_panel.stop_recording_requested.connect(self.stop_synchronized_recording)
        
        # Dual webcam signals
        if self.dual_webcam:
            self.dual_webcam.dual_frame_ready.connect(self.update_webcam_previews)
            self.dual_webcam.recording_started.connect(self.on_webcam_recording_started)
            self.dual_webcam.recording_stopped.connect(self.on_webcam_recording_stopped)
            self.dual_webcam.sync_status_changed.connect(self.on_webcam_sync_changed)
            self.dual_webcam.camera_status_changed.connect(self.on_camera_status_changed)
            self.dual_webcam.error_occurred.connect(self.on_webcam_error)
        
        # Timer for updating master time display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_master_time_display)
        self.timer.start(100)  # Update every 100ms

    def test_webcams(self):
        """Test dual webcam access."""
        success = test_dual_webcam_access()
        if success:
            QMessageBox.information(self, "Webcam Test", "Both webcams are accessible!")
        else:
            QMessageBox.warning(self, "Webcam Test", "Webcam access test failed!")

    def check_synchronization(self):
        """Check and display synchronization status."""
        if self.master_synchronizer:
            devices = self.master_synchronizer.get_connected_devices()
            sessions = self.master_synchronizer.get_active_sessions()
            
            msg = f"Connected devices: {len(devices)}\n"
            msg += f"Active sessions: {len(sessions)}\n\n"
            
            for device_id, status in devices.items():
                msg += f"{device_id}: {status.sync_quality*100:.1f}% sync quality\n"
                
            QMessageBox.information(self, "Synchronization Status", msg)
        else:
            QMessageBox.warning(self, "Sync Status", "Synchronization system not initialized")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
            "Multi-Sensor Recording System - Dual Webcam Edition\n\n"
            "Features:\n"
            "• Dual Logitech Brio 4K30 webcam recording\n"
            "• Master clock synchronization\n"  
            "• Android device integration\n"
            "• Multi-sensor coordination\n\n"
            "Version: 1.0.0")

    def start_synchronized_recording(self, session_id: str):
        """Start synchronized recording across all devices."""
        try:
            if self.is_recording:
                return
                
            # Start webcam recording if enabled
            webcam_started = False
            if (self.recording_panel.record_webcam_check.isChecked() and 
                self.dual_webcam):
                webcam_started = self.dual_webcam.start_recording(session_id)
                
            # Start synchronized recording via master synchronizer
            sync_started = False
            if self.master_synchronizer:
                sync_started = self.master_synchronizer.start_synchronized_recording(
                    session_id=session_id,
                    record_video=self.recording_panel.record_android_video_check.isChecked(),
                    record_thermal=self.recording_panel.record_thermal_check.isChecked(),
                    record_shimmer=self.recording_panel.record_shimmer_check.isChecked()
                )
                
            if webcam_started or sync_started:
                self.is_recording = True
                self.current_session_id = session_id
                self.recording_panel.set_recording_state(True)
                self.statusBar().showMessage(f"Recording session: {session_id}")
                self.log_message(f"Started recording session: {session_id}")
            else:
                QMessageBox.warning(self, "Recording Error", "Failed to start recording")
                
        except Exception as e:
            error_msg = f"Error starting recording: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Recording Error", error_msg)

    def stop_synchronized_recording(self):
        """Stop synchronized recording."""
        try:
            if not self.is_recording:
                return
                
            # Stop webcam recording
            if self.dual_webcam:
                files = self.dual_webcam.stop_recording()
                if files[0] and files[1]:
                    self.log_message(f"Webcam files saved: {files[0]}, {files[1]}")
                    
            # Stop synchronized recording
            if self.master_synchronizer and self.current_session_id:
                self.master_synchronizer.stop_synchronized_recording(self.current_session_id)
                
            self.is_recording = False
            self.recording_panel.set_recording_state(False)
            self.statusBar().showMessage("Recording stopped")
            self.log_message(f"Stopped recording session: {self.current_session_id}")
            self.current_session_id = None
            
        except Exception as e:
            error_msg = f"Error stopping recording: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Recording Error", error_msg)

    def update_webcam_previews(self, pixmap1: QPixmap, pixmap2: QPixmap):
        """Update webcam preview displays."""
        self.preview_panel.update_camera1_frame(pixmap1)
        self.preview_panel.update_camera2_frame(pixmap2)

    def update_master_time_display(self):
        """Update master time display."""
        if self.master_synchronizer:
            timestamp = self.master_synchronizer.get_master_timestamp()
            self.sync_panel.update_master_time(timestamp)

    def on_webcam_sync_update(self, timestamp: float):
        """Handle webcam synchronization update."""
        self.log_message(f"Webcam sync update: {timestamp}")

    def on_master_sync_update(self, timestamp: float):
        """Handle master synchronization update."""
        self.log_message(f"Master sync update: {timestamp}")

    def on_sync_status_update(self, devices: dict):
        """Handle synchronization status update."""
        self.sync_panel.update_device_list(devices)
        
        # Calculate average sync quality
        if devices:
            android_quality = sum(s.sync_quality for s in devices.values() 
                                if s.device_type == 'android') / max(1, len(devices))
        else:
            android_quality = 0.0
            
        webcam_quality = self.dual_webcam.get_sync_quality() if self.dual_webcam else 0.0
        self.sync_panel.update_sync_quality(webcam_quality, android_quality)

    def on_webcam_recording_started(self, file1: str, file2: str):
        """Handle webcam recording started."""
        self.log_message(f"Webcam recording started: {file1}, {file2}")

    def on_webcam_recording_stopped(self, file1: str, file2: str, duration: float):
        """Handle webcam recording stopped.""" 
        self.log_message(f"Webcam recording stopped: duration {duration:.1f}s")

    def on_webcam_sync_changed(self, quality: float):
        """Handle webcam sync quality change."""
        pass  # Updated via on_sync_status_update

    def on_camera_status_changed(self, status: dict):
        """Handle camera status change."""
        camera1_info = status.get('camera1', {})
        camera2_info = status.get('camera2', {})
        
        if camera1_info.get('active'):
            res = camera1_info.get('resolution', (0, 0))
            fps = camera1_info.get('fps', 0)
            self.preview_panel.update_camera_status(1, f"Active {res[0]}x{res[1]} @ {fps:.1f}fps")
        else:
            self.preview_panel.update_camera_status(1, "Disconnected")
            
        if camera2_info.get('active'):
            res = camera2_info.get('resolution', (0, 0))
            fps = camera2_info.get('fps', 0)
            self.preview_panel.update_camera_status(2, f"Active {res[0]}x{res[1]} @ {fps:.1f}fps")
        else:
            self.preview_panel.update_camera_status(2, "Disconnected")

    def on_webcam_error(self, error_msg: str):
        """Handle webcam error."""
        self.log_message(f"Webcam error: {error_msg}")
        QMessageBox.warning(self, "Webcam Error", error_msg)

    def log_message(self, message: str):
        """Add message to log display."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.log_display.appendPlainText(log_entry)
        logger.info(message)

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Stop recording if active
            if self.is_recording:
                self.stop_synchronized_recording()
                
            # Clean up webcam
            if self.dual_webcam:
                self.dual_webcam.cleanup()
                
            # Stop master synchronizer
            if self.master_synchronizer:
                self.master_synchronizer.stop()
                
            logger.info("DualWebcamMainWindow closed successfully")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = DualWebcamMainWindow()
    window.show()
    sys.exit(app.exec_())