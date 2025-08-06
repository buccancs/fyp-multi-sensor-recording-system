
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from bucika_gsr.network.device_server import JsonSocketServer
from bucika_gsr.session.session_manager import SessionManager
from bucika_gsr.webcam.webcam_capture import WebcamCapture

from .device_panel import DeviceStatusPanel
from .enhanced_stimulus_controller import VLC_AVAILABLE, EnhancedStimulusController
from .preview_panel import PreviewPanel
from .stimulus_panel import StimulusControlPanel


class EnhancedMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1400, 900)

        self.json_server = JsonSocketServer()
        self.server_running = False

        self.webcam_capture = WebcamCapture()
        self.webcam_previewing = False
        self.webcam_recording = False

        self.session_manager = SessionManager()
        self.current_session_id = None

        self.enhanced_stimulus_controller = EnhancedStimulusController(self)

        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_metrics)
        self.performance_timer.setInterval(1000)

        self.init_ui()

        self.connect_server_signals()

        self.connect_webcam_signals()

        self.connect_enhanced_stimulus_signals()

        self.init_placeholder_data()

        self.show_vlc_status()

    def init_ui(self):
        self.create_menu_bar()

        self.create_enhanced_toolbar()

        self.create_enhanced_central_widget()

        self.create_enhanced_log_dock()

        self.create_enhanced_status_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("Tools")

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        tools_menu.addAction(settings_action)

        stimulus_menu = menubar.addMenu("Stimulus")

        switch_backend_action = QAction("Switch Video Backend", self)
        switch_backend_action.triggered.connect(
            self.enhanced_stimulus_controller.switch_backend
        )
        switch_backend_action.setEnabled(VLC_AVAILABLE)
        stimulus_menu.addAction(switch_backend_action)

        test_timing_action = QAction("Test Timing Precision", self)
        test_timing_action.triggered.connect(self.test_timing_precision)
        stimulus_menu.addAction(test_timing_action)

        performance_monitor_action = QAction("Performance Monitor", self)
        performance_monitor_action.setCheckable(True)
        performance_monitor_action.triggered.connect(self.toggle_performance_monitoring)
        stimulus_menu.addAction(performance_monitor_action)

        view_menu = menubar.addMenu("View")

        self.show_log_action = QAction("Show Log", self)
        self.show_log_action.setCheckable(True)
        self.show_log_action.setChecked(False)
        self.show_log_action.triggered.connect(self.toggle_log_dock)
        view_menu.addAction(self.show_log_action)

        help_menu = menubar.addMenu("Help")

        about_action = QAction("About Enhanced Controller", self)
        about_action.triggered.connect(self.show_enhanced_about)
        help_menu.addAction(about_action)

        vlc_help_action = QAction("VLC Setup Guide", self)
        vlc_help_action.triggered.connect(self.show_vlc_setup_guide)
        help_menu.addAction(vlc_help_action)

    def create_enhanced_toolbar(self):
        toolbar = self.addToolBar("EnhancedControls")
        toolbar.setMovable(False)

        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.handle_connect)
        toolbar.addAction(connect_action)

        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.handle_disconnect)
        toolbar.addAction(disconnect_action)

        toolbar.addSeparator()

        start_action = QAction("Start Session", self)
        start_action.triggered.connect(self.handle_start)
        toolbar.addAction(start_action)

        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.handle_stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        backend_label = QLabel("Backend:")
        toolbar.addWidget(backend_label)

        self.backend_status_label = QLabel("Qt")
        self.backend_status_label.setStyleSheet(
            "QLabel { color: #0066cc; font-weight: bold; }"
        )
        toolbar.addWidget(self.backend_status_label)

        toolbar.addSeparator()

        perf_label = QLabel("Performance:")
        toolbar.addWidget(perf_label)

        self.performance_indicator = QProgressBar()
        self.performance_indicator.setRange(0, 100)
        self.performance_indicator.setValue(100)
        self.performance_indicator.setMaximumWidth(100)
        self.performance_indicator.setFormat("%p%")
        toolbar.addWidget(self.performance_indicator)

    def create_enhanced_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()

        self.device_panel = DeviceStatusPanel(self)
        top_layout.addWidget(self.device_panel)

        self.preview_panel = PreviewPanel(self)
        top_layout.addWidget(self.preview_panel)

        main_layout.addLayout(top_layout)

        stimulus_layout = QVBoxLayout()

        self.stimulus_panel = StimulusControlPanel(self)
        stimulus_layout.addWidget(self.stimulus_panel)

        stimulus_layout.addWidget(self.enhanced_stimulus_controller)

        main_layout.addLayout(stimulus_layout)

        status_layout = QHBoxLayout()

        self.vlc_status_label = QLabel(
            f"VLC Backend: {'Available' if VLC_AVAILABLE else 'Not Available'}"
        )
        self.vlc_status_label.setStyleSheet(
            f"QLabel {{ color: {'#00aa00' if VLC_AVAILABLE else '#aa0000'}; font-size: 10px; }}"
        )
        status_layout.addWidget(self.vlc_status_label)

        status_layout.addStretch()

        self.timing_precision_label = QLabel("Timing: Calibrating...")
        self.timing_precision_label.setStyleSheet(
            "QLabel { color: #666; font-size: 10px; }"
        )
        status_layout.addWidget(self.timing_precision_label)

        main_layout.addLayout(status_layout)

    def create_enhanced_log_dock(self):
        self.log_dock = QDockWidget("Enhanced System Log", self)
        self.log_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)

        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)

        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)

        self.log_filter_combo = QComboBox()
        self.log_filter_combo.addItems(
            ["All", "Stimulus", "Backend", "Performance", "Errors"]
        )
        self.log_filter_combo.currentTextChanged.connect(self.filter_log_messages)
        filter_layout.addWidget(self.log_filter_combo)

        filter_layout.addStretch()

        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        filter_layout.addWidget(clear_log_btn)

        log_layout.addLayout(filter_layout)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        self.log_dock.setWidget(log_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        self.log_dock.hide()

    def create_enhanced_status_bar(self):
        status_bar = self.statusBar()

        self.status_message = QLabel("Enhanced Controller Ready")
        status_bar.addWidget(self.status_message)

        status_bar.addPermanentWidget(QLabel("|"))

        self.backend_status = QLabel("Backend: Qt")
        status_bar.addPermanentWidget(self.backend_status)

        status_bar.addPermanentWidget(QLabel("|"))

        self.performance_status = QLabel("Performance: 100%")
        status_bar.addPermanentWidget(self.performance_status)

        status_bar.addPermanentWidget(QLabel("|"))

        self.timing_status = QLabel("Timing: Ready")
        status_bar.addPermanentWidget(self.timing_status)

    def connect_server_signals(self):
        self.json_server.client_connected.connect(self.on_client_connected)
        self.json_server.client_disconnected.connect(self.on_client_disconnected)
        self.json_server.message_received.connect(self.on_message_received)
        self.json_server.error_occurred.connect(self.on_server_error)

        self.log_message("Server signals connected to GUI handlers")

    def connect_webcam_signals(self):
        self.webcam_capture.frame_ready.connect(self.on_webcam_frame_ready)
        self.webcam_capture.recording_started.connect(self.on_webcam_recording_started)
        self.webcam_capture.recording_stopped.connect(self.on_webcam_recording_stopped)
        self.webcam_capture.error_occurred.connect(self.on_webcam_error)
        self.webcam_capture.status_changed.connect(self.on_webcam_status_changed)

    def connect_enhanced_stimulus_signals(self):
        self.stimulus_panel.file_loaded.connect(
            self.enhanced_stimulus_controller.load_video
        )
        self.stimulus_panel.play_requested.connect(
            self.enhanced_stimulus_controller.test_play
        )
        self.stimulus_panel.pause_requested.connect(
            self.enhanced_stimulus_controller.test_pause
        )
        self.stimulus_panel.seek_requested.connect(
            self.on_enhanced_stimulus_seek_requested
        )
        self.stimulus_panel.screen_changed.connect(
            self.on_enhanced_stimulus_screen_changed
        )

        self.stimulus_panel.start_recording_play_requested.connect(
            self.on_enhanced_start_recording_play_requested
        )
        self.stimulus_panel.mark_event_requested.connect(
            self.on_enhanced_mark_event_requested
        )

        self.enhanced_stimulus_controller.status_changed.connect(
            self.on_enhanced_stimulus_status_changed
        )
        self.enhanced_stimulus_controller.experiment_started.connect(
            self.on_enhanced_stimulus_experiment_started
        )
        self.enhanced_stimulus_controller.experiment_ended.connect(
            self.on_enhanced_stimulus_experiment_ended
        )
        self.enhanced_stimulus_controller.error_occurred.connect(
            self.on_enhanced_stimulus_error
        )
        self.enhanced_stimulus_controller.backend_changed.connect(
            self.on_backend_changed
        )

        self.log_message(
            "Enhanced stimulus signals connected to GUI handlers", "Stimulus"
        )

    def init_placeholder_data(self):
        QTimer.singleShot(1000, self.update_timing_precision_display)

    def show_vlc_status(self):
        if VLC_AVAILABLE:
            self.log_message(
                "VLC backend available - Enhanced codec support enabled", "Backend"
            )
        else:
            self.log_message(
                "VLC backend not available - Limited to Qt multimedia codecs", "Backend"
            )

    def on_enhanced_stimulus_seek_requested(self, position):
        duration = self.enhanced_stimulus_controller.get_duration()
        if duration > 0:
            seek_position = int((position / 100.0) * duration)
            if self.enhanced_stimulus_controller.current_backend:
                if hasattr(self.enhanced_stimulus_controller, "qt_media_player"):
                    self.enhanced_stimulus_controller.qt_media_player.setPosition(
                        seek_position
                    )
                elif hasattr(self.enhanced_stimulus_controller, "vlc_video_widget"):
                    self.enhanced_stimulus_controller.vlc_video_widget.set_position(
                        seek_position
                    )
            self.log_message(
                f"Enhanced stimulus seek to {position}% ({seek_position}ms)", "Stimulus"
            )

    def on_enhanced_stimulus_screen_changed(self, screen_index):
        self.log_message(
            f"Enhanced stimulus output screen changed to index {screen_index}",
            "Stimulus",
        )

    def on_enhanced_start_recording_play_requested(self):
        try:
            screen_index = self.stimulus_panel.get_selected_screen()

            self.log_message(
                "Starting enhanced synchronized recording and stimulus playback...",
                "Stimulus",
            )

            if self.server_running and self.json_server.connected_clients:
                self.json_server.broadcast_command("start_record")
                self.log_message("Sent start_record command to all devices", "Stimulus")

            if not self.webcam_recording:
                self.webcam_capture.start_recording()
                self.log_message("Started PC webcam recording", "Stimulus")

            if self.enhanced_stimulus_controller.start_stimulus_playback(screen_index):
                self.stimulus_panel.set_experiment_active(True)
                self.log_message("Enhanced experiment started successfully", "Stimulus")

                self.performance_timer.start()
            else:
                self.log_message("Failed to start enhanced stimulus playback", "Errors")

        except Exception as e:
            self.log_message(
                f"Error starting enhanced synchronized experiment: {str(e)}", "Errors"
            )
            QMessageBox.critical(
                self,
                "Enhanced Experiment Start Error",
                f"Failed to start experiment: {str(e)}",
            )

    def on_enhanced_mark_event_requested(self):
        try:
            self.enhanced_stimulus_controller.mark_event()
            self.log_message("Enhanced event marker added", "Stimulus")
        except Exception as e:
            self.log_message(f"Error adding enhanced event marker: {str(e)}", "Errors")

    def on_enhanced_stimulus_status_changed(self, status_message):
        self.status_message.setText(status_message)
        self.log_message(f"Enhanced Stimulus: {status_message}", "Stimulus")

    def on_enhanced_stimulus_experiment_started(self):
        self.stimulus_panel.set_experiment_active(True)
        self.log_message("Enhanced stimulus experiment started", "Stimulus")

    def on_enhanced_stimulus_experiment_ended(self):
        try:
            self.performance_timer.stop()

            if self.server_running and self.json_server.connected_clients:
                self.json_server.broadcast_command("stop_record")
                self.log_message("Sent stop_record command to all devices", "Stimulus")

            if self.webcam_recording:
                self.webcam_capture.stop_recording()
                self.log_message("Stopped PC webcam recording", "Stimulus")

            self.stimulus_panel.set_experiment_active(False)
            self.log_message(
                "Enhanced stimulus experiment ended - all recordings stopped",
                "Stimulus",
            )

        except Exception as e:
            self.log_message(f"Error stopping enhanced recordings: {str(e)}", "Errors")

    def on_enhanced_stimulus_error(self, error_message):
        self.log_message(f"Enhanced Stimulus Error: {error_message}", "Errors")
        QMessageBox.warning(self, "Enhanced Stimulus Error", error_message)

    def on_backend_changed(self, backend_name):
        self.backend_status_label.setText(backend_name.upper())
        self.backend_status.setText(f"Backend: {backend_name}")
        self.log_message(f"Video backend switched to: {backend_name}", "Backend")

    def test_timing_precision(self):
        try:
            timing_logger = self.enhanced_stimulus_controller.timing_logger
            timestamps = timing_logger.get_precise_timestamp()

            precision_info = f"Timing Precision Test:\n"
            precision_info += f"Clock Offset: {timing_logger.clock_offset*1000:.3f}ms\n"
            precision_info += f"System Time: {timestamps['system_time']:.6f}\n"
            precision_info += (
                f"Performance Time: {timestamps['performance_time']:.6f}\n"
            )
            precision_info += f"Corrected Time: {timestamps['corrected_time']:.6f}"

            QMessageBox.information(self, "Timing Precision Test", precision_info)
            self.log_message("Timing precision test completed", "Performance")

        except Exception as e:
            self.log_message(f"Timing precision test error: {str(e)}", "Errors")

    def toggle_performance_monitoring(self, enabled):
        if enabled:
            self.performance_timer.start()
            self.log_message("Performance monitoring enabled", "Performance")
        else:
            self.performance_timer.stop()
            self.log_message("Performance monitoring disabled", "Performance")

    def update_performance_metrics(self):
        try:
            if hasattr(self.enhanced_stimulus_controller, "frame_drop_count"):
                frame_drops = self.enhanced_stimulus_controller.frame_drop_count
                performance_score = max(0, 100 - (frame_drops * 2))

                self.performance_indicator.setValue(performance_score)
                self.performance_status.setText(f"Performance: {performance_score}%")

                if performance_score < 80:
                    self.log_message(
                        f"Performance warning: {performance_score}% (frame drops: {frame_drops})",
                        "Performance",
                    )

        except Exception as e:
            self.log_message(f"Performance monitoring error: {str(e)}", "Errors")

    def update_timing_precision_display(self):
        try:
            timing_logger = self.enhanced_stimulus_controller.timing_logger
            offset_ms = timing_logger.clock_offset * 1000

            self.timing_precision_label.setText(f"Timing: ±{abs(offset_ms):.2f}ms")
            self.timing_status.setText(f"Timing: ±{abs(offset_ms):.2f}ms")

        except Exception as e:
            self.log_message(f"Timing display update error: {str(e)}", "Errors")

    def filter_log_messages(self, filter_type):
        self.log_message(f"Log filter changed to: {filter_type}", "System")

    def clear_log(self):
        self.log_text.clear()
        self.log_message("Log cleared", "System")

    def show_enhanced_about(self):
        about_text = f"""
Enhanced Multi-Sensor Recording System Controller

Version: 3.5 Enhanced
Features:
• VLC Backend Support: {'Available' if VLC_AVAILABLE else 'Not Available'}
• Enhanced Timing Precision: Multiple clock sources with calibration
• Performance Monitoring: Real-time frame timing analysis
• Automatic Backend Selection: Smart codec compatibility
• Comprehensive Error Handling: Detailed error reporting

PsychoPy-Inspired Improvements:
• Frame-accurate timing control
• Hardware-accelerated video playback
• Robust codec support and fallback mechanisms
• Professional-grade synchronization accuracy

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
        setup_text = """
VLC Backend Setup Guide

To enable enhanced codec support with VLC backend:

1. Install VLC Media Player:
   - Download from: https://www.videolan.org/vlc/
   - Install with default settings

2. Install python-vlc:
   - Run: pip install python-vlc
   - Restart the application

3. Verify Installation:
   - Check status bar for "VLC Backend: Available"
   - Use "Switch Video Backend" from Stimulus menu

Benefits of VLC Backend:
• Support for additional formats: FLV, WebM, OGV, MPEG, TS
• Better codec compatibility
• Improved error handling
• Hardware acceleration support

Troubleshooting:
• If VLC not detected, ensure VLC is in system PATH
• For codec issues, try switching backends via menu
• Check logs for detailed error information
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{category}] {message}"

        self.log_text.append(formatted_message)

        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        print(f"[DEBUG_LOG] {formatted_message}")

    def on_client_connected(self, client_info):
        self.log_message(f"Client connected: {client_info}", "Network")

    def on_client_disconnected(self, client_info):
        self.log_message(f"Client disconnected: {client_info}", "Network")

    def on_message_received(self, message):
        self.log_message(f"Message received: {message}", "Network")

    def on_server_error(self, error):
        self.log_message(f"Server error: {error}", "Errors")

    def on_webcam_frame_ready(self, frame):

    def on_webcam_recording_started(self):
        self.webcam_recording = True
        self.log_message("Webcam recording started", "Recording")

    def on_webcam_recording_stopped(self):
        self.webcam_recording = False
        self.log_message("Webcam recording stopped", "Recording")

    def on_webcam_error(self, error):
        self.log_message(f"Webcam error: {error}", "Errors")

    def on_webcam_status_changed(self, status):
        self.log_message(f"Webcam status: {status}", "Recording")

    def handle_connect(self):
        self.log_message("Connect action triggered", "Network")

    def handle_disconnect(self):
        self.log_message("Disconnect action triggered", "Network")

    def handle_start(self):
        self.log_message("Start session action triggered", "Session")

    def handle_stop(self):
        self.log_message("Stop action triggered", "Session")

    def show_settings_dialog(self):
        self.log_message("Settings dialog requested", "System")

    def toggle_log_dock(self, visible):
        if visible:
            self.log_dock.show()
        else:
            self.log_dock.hide()


import time
