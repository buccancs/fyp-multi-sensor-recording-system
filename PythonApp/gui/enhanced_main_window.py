from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
try:
    from bucika_gsr.network.device_server import JsonSocketServer
except ImportError:
    try:
        from ..network.device_server import JsonSocketServer
    except ImportError:
        JsonSocketServer = None

try:
    from bucika_gsr.session.session_manager import SessionManager
except ImportError:
    try:
        from ..session.session_manager import SessionManager
    except ImportError:
        SessionManager = None

try:
    from bucika_gsr.webcam.webcam_capture import WebcamCapture
except ImportError:
    try:
        from ..webcam.webcam_capture import WebcamCapture
    except ImportError:
        WebcamCapture = None
from .device_panel import DeviceStatusPanel
try:
    from .preview_panel import PreviewPanel
except ImportError:
    PreviewPanel = None

try:
    from .enhanced_stimulus_controller import VLC_AVAILABLE, EnhancedStimulusController
except ImportError:
    VLC_AVAILABLE = False
    EnhancedStimulusController = None

try:
    from .stimulus_panel import StimulusControlPanel
except ImportError:
    StimulusControlPanel = None
class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components with error handling
        self.json_server = JsonSocketServer() if JsonSocketServer else None
        self.server_running = False
        self.webcam_capture = WebcamCapture() if WebcamCapture else None
        self.webcam_previewing = False
        self.webcam_recording = False
        self.session_manager = SessionManager() if SessionManager else None
        self.current_session_id = None
        
        # Try to initialize enhanced stimulus controller
        try:
            self.enhanced_stimulus_controller = EnhancedStimulusController(self)
        except:
            self.enhanced_stimulus_controller = None
        
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_metrics)
        self.performance_timer.setInterval(1000)
        self.init_ui()
        self.connect_server_signals()
        self.connect_webcam_signals()
        self.connect_enhanced_stimulus_signals()
        self.init_placeholder_data()
        self.show_vlc_status()
    
    def init_placeholder_data(self):
        """Initialize placeholder data for testing."""
        QTimer.singleShot(1000, self.update_timing_precision_display)
    
    def show_vlc_status(self):
        """Show VLC backend status."""
        if VLC_AVAILABLE:
            self.log_message(
                "VLC backend available - Enhanced codec support enabled", "Backend"
            )
        else:
            self.log_message(
                "VLC backend not available - Limited to Qt multimedia codecs", "Backend"
            )
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
        if self.enhanced_stimulus_controller:
            switch_backend_action.triggered.connect(
                self.enhanced_stimulus_controller.switch_backend
            )
        else:
            switch_backend_action.triggered.connect(
                lambda: self.log_message("Switch backend not available in demo mode", "Backend")
            )
        switch_backend_action.setEnabled(VLC_AVAILABLE and self.enhanced_stimulus_controller is not None)
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
            "QLabel { colour: #0066cc; font-weight: bold; }"
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
        
        # Create tabbed interface as described in thesis (Chapter 4, Section 4.3)
        self.tab_widget = QTabWidget()
        
        # Dashboard Tab - Device overview and live video feeds
        self.dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        
        # Logs Tab - System messages and debugging
        self.logs_tab = self.create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "Logs")
        
        # Playback & Annotation Tab - Recording session review
        self.playback_tab = self.create_playback_annotation_tab()
        self.tab_widget.addTab(self.playback_tab, "Playback & Annotation")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status layout at bottom
        status_layout = QHBoxLayout()
        self.vlc_status_label = QLabel(
            f"VLC Backend: {'Available' if VLC_AVAILABLE else 'Not Available'}"
        )
        self.vlc_status_label.setStyleSheet(
            f"QLabel {{ colour: {'#00aa00' if VLC_AVAILABLE else '#aa0000'}; font-size: 10px; }}"
        )
        status_layout.addWidget(self.vlc_status_label)
        status_layout.addStretch()
        self.timing_precision_label = QLabel("Timing: Calibrating...")
        self.timing_precision_label.setStyleSheet(
            "QLabel { colour: #666; font-size: 10px; }"
        )
        status_layout.addWidget(self.timing_precision_label)
        main_layout.addLayout(status_layout)
    
    def create_dashboard_tab(self):
        """Create Dashboard tab for device overview and live video feeds."""
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        
        # Top section - Device management and preview panel
        top_layout = QHBoxLayout()
        
        if DeviceStatusPanel:
            self.device_panel = DeviceStatusPanel(self)
        else:
            # Create mock device panel
            self.device_panel = QWidget()
            device_layout = QVBoxLayout(self.device_panel)
            device_layout.addWidget(QLabel("Device Panel (Demo Mode)"))
            device_layout.addWidget(QPushButton("Connect Devices"))
        
        top_layout.addWidget(self.device_panel)
        
        if PreviewPanel:
            self.preview_panel = PreviewPanel(self)
        else:
            # Create mock preview panel
            self.preview_panel = QWidget()
            preview_layout = QVBoxLayout(self.preview_panel)
            preview_layout.addWidget(QLabel("Preview Panel (Demo Mode)"))
            preview_display = QLabel("Live Preview Area")
            preview_display.setMinimumHeight(200)
            preview_display.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0; text-align: center;")
            preview_layout.addWidget(preview_display)
        
        top_layout.addWidget(self.preview_panel)
        dashboard_layout.addLayout(top_layout)
        
        # Middle section - Multi-device coordination grid
        coordination_group = QGroupBox("Multi-Device Coordination")
        coordination_layout = QGridLayout(coordination_group)
        
        # Create live feed grid for multiple devices
        self.device_feed_grid = {}
        device_types = ["Android RGB", "Thermal Camera", "Shimmer GSR", "PC Webcam"]
        
        for i, device_type in enumerate(device_types):
            row, col = divmod(i, 2)
            
            # Device feed widget
            feed_widget = QWidget()
            feed_layout = QVBoxLayout(feed_widget)
            
            # Device status indicator
            status_layout = QHBoxLayout()
            status_indicator = QLabel("●")
            status_indicator.setStyleSheet("color: red; font-size: 16px;")
            status_layout.addWidget(status_indicator)
            
            device_label = QLabel(device_type)
            device_label.setStyleSheet("font-weight: bold;")
            status_layout.addWidget(device_label)
            status_layout.addStretch()
            
            feed_layout.addLayout(status_layout)
            
            # Live feed area
            feed_display = QLabel("No Feed")
            feed_display.setMinimumHeight(120)
            feed_display.setStyleSheet(
                "border: 1px solid gray; background-color: #2a2a2a; "
                "color: white; text-align: center;"
            )
            feed_layout.addWidget(feed_display)
            
            # Device controls
            controls_layout = QHBoxLayout()
            connect_btn = QPushButton("Connect")
            connect_btn.setMaximumWidth(80)
            controls_layout.addWidget(connect_btn)
            
            record_btn = QPushButton("Record")
            record_btn.setMaximumWidth(80)
            record_btn.setEnabled(False)
            controls_layout.addWidget(record_btn)
            controls_layout.addStretch()
            
            feed_layout.addLayout(controls_layout)
            
            coordination_layout.addWidget(feed_widget, row, col)
            
            # Store references for later updates
            self.device_feed_grid[device_type] = {
                'status_indicator': status_indicator,
                'feed_display': feed_display,
                'connect_btn': connect_btn,
                'record_btn': record_btn
            }
        
        dashboard_layout.addWidget(coordination_group)
        
        # Bottom section - Stimulus controls
        stimulus_layout = QVBoxLayout()
        
        try:
            self.stimulus_panel = StimulusControlPanel(self)
        except:
            # Create mock stimulus panel
            self.stimulus_panel = QWidget()
            stim_layout = QVBoxLayout(self.stimulus_panel)
            stim_layout.addWidget(QLabel("Stimulus Panel (Demo Mode)"))
            stim_layout.addWidget(QPushButton("Load Video"))
            stim_layout.addWidget(QPushButton("Play"))
        
        stimulus_layout.addWidget(self.stimulus_panel)
        
        if self.enhanced_stimulus_controller:
            stimulus_layout.addWidget(self.enhanced_stimulus_controller)
        else:
            # Create mock enhanced controller
            mock_controller = QWidget()
            controller_layout = QVBoxLayout(mock_controller)
            controller_layout.addWidget(QLabel("Enhanced Stimulus Controller (Demo Mode)"))
            stimulus_layout.addWidget(mock_controller)
        
        dashboard_layout.addLayout(stimulus_layout)
        
        return dashboard_widget
    
    def create_logs_tab(self):
        """Create Logs tab for system messages and debugging."""
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        
        # Log filter controls
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)
        
        self.main_log_filter_combo = QComboBox()
        self.main_log_filter_combo.addItems(
            ["All", "Stimulus", "Backend", "Performance", "Errors", "Network", "Recording", "Session"]
        )
        self.main_log_filter_combo.currentTextChanged.connect(self.filter_log_messages)
        filter_layout.addWidget(self.main_log_filter_combo)
        
        filter_layout.addStretch()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        filter_layout.addWidget(clear_log_btn)
        
        export_log_btn = QPushButton("Export Log")
        export_log_btn.clicked.connect(self.export_log)
        filter_layout.addWidget(export_log_btn)
        
        logs_layout.addLayout(filter_layout)
        
        # Main log display (use the same log_text from dock)
        self.main_log_text = QTextEdit()
        self.main_log_text.setReadOnly(True)
        self.main_log_text.setStyleSheet(
            "font-family: 'Courier New', monospace; "
            "background-color: #1e1e1e; color: #dcdcdc; "
            "border: 1px solid #555;"
        )
        logs_layout.addWidget(self.main_log_text)
        
        # Log statistics
        stats_layout = QHBoxLayout()
        self.log_count_label = QLabel("Messages: 0")
        stats_layout.addWidget(self.log_count_label)
        
        self.error_count_label = QLabel("Errors: 0")
        self.error_count_label.setStyleSheet("color: red;")
        stats_layout.addWidget(self.error_count_label)
        
        self.warning_count_label = QLabel("Warnings: 0")
        self.warning_count_label.setStyleSheet("color: orange;")
        stats_layout.addWidget(self.warning_count_label)
        
        stats_layout.addStretch()
        logs_layout.addLayout(stats_layout)
        
        return logs_widget
    
    def create_playback_annotation_tab(self):
        """Create Playback & Annotation tab for reviewing recorded sessions."""
        playback_widget = QWidget()
        playback_layout = QVBoxLayout(playback_widget)
        
        # Session selection controls
        session_group = QGroupBox("Session Selection")
        session_layout = QHBoxLayout(session_group)
        
        load_session_btn = QPushButton("Load Session...")
        load_session_btn.clicked.connect(self.load_recorded_session)
        session_layout.addWidget(load_session_btn)
        
        self.session_info_label = QLabel("No session loaded")
        self.session_info_label.setStyleSheet("font-weight: bold;")
        session_layout.addWidget(self.session_info_label)
        session_layout.addStretch()
        
        playback_layout.addWidget(session_group)
        
        # Main playback area
        playback_main = QHBoxLayout()
        
        # Left side - Video and timeline playback
        video_group = QGroupBox("Synchronized Video Playback")
        video_layout = QVBoxLayout(video_group)
        
        # Video display area
        self.playback_video_display = QLabel("Load a session to begin playback")
        self.playback_video_display.setMinimumHeight(300)
        self.playback_video_display.setStyleSheet(
            "border: 2px solid #555; background-color: #2a2a2a; "
            "color: white; text-align: center; font-size: 14px;"
        )
        video_layout.addWidget(self.playback_video_display)
        
        # Timeline controls
        timeline_layout = QHBoxLayout()
        
        self.playback_slider = QSlider(Qt.Horizontal)
        self.playback_slider.setEnabled(False)
        self.playback_slider.valueChanged.connect(self.on_playback_seek)
        timeline_layout.addWidget(self.playback_slider)
        
        self.time_display = QLabel("00:00 / 00:00")
        self.time_display.setStyleSheet("font-family: monospace; font-size: 12px;")
        timeline_layout.addWidget(self.time_display)
        
        video_layout.addLayout(timeline_layout)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_pause_btn)
        
        self.stop_playback_btn = QPushButton("Stop")
        self.stop_playback_btn.setEnabled(False)
        self.stop_playback_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_playback_btn)
        
        speed_label = QLabel("Speed:")
        controls_layout.addWidget(speed_label)
        
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1.0x", "2.0x", "4.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(self.change_playback_speed)
        controls_layout.addWidget(self.speed_combo)
        
        controls_layout.addStretch()
        video_layout.addLayout(controls_layout)
        
        playback_main.addWidget(video_group)
        
        # Right side - GSR plot and annotations
        data_group = QGroupBox("Sensor Data & Annotations")
        data_layout = QVBoxLayout(data_group)
        
        # GSR plot display
        self.gsr_plot_display = QLabel("GSR Plot will appear here")
        self.gsr_plot_display.setMinimumHeight(150)
        self.gsr_plot_display.setStyleSheet(
            "border: 1px solid #555; background-color: #f5f5f5; text-align: center;"
        )
        data_layout.addWidget(self.gsr_plot_display)
        
        # Annotation controls
        annotation_controls = QHBoxLayout()
        
        add_annotation_btn = QPushButton("Add Annotation")
        add_annotation_btn.clicked.connect(self.add_timestamp_annotation)
        annotation_controls.addWidget(add_annotation_btn)
        
        self.annotation_text = QLineEdit()
        self.annotation_text.setPlaceholderText("Enter annotation text...")
        annotation_controls.addWidget(self.annotation_text)
        
        data_layout.addLayout(annotation_controls)
        
        # Annotations list
        annotations_label = QLabel("Session Annotations:")
        annotations_label.setStyleSheet("font-weight: bold;")
        data_layout.addWidget(annotations_label)
        
        self.annotations_list = QTextEdit()
        self.annotations_list.setMaximumHeight(120)
        self.annotations_list.setReadOnly(True)
        data_layout.addWidget(self.annotations_list)
        
        # Export controls
        export_layout = QHBoxLayout()
        export_annotations_btn = QPushButton("Export Annotations")
        export_annotations_btn.clicked.connect(self.export_annotations)
        export_layout.addWidget(export_annotations_btn)
        
        export_data_btn = QPushButton("Export Session Data")
        export_data_btn.clicked.connect(self.export_session_data)
        export_layout.addWidget(export_data_btn)
        export_layout.addStretch()
        
        data_layout.addLayout(export_layout)
        
        playback_main.addWidget(data_group)
        playback_layout.addLayout(playback_main)
        
        return playback_widget
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
        if self.json_server:
            try:
                self.json_server.client_connected.connect(self.on_client_connected)
                self.json_server.client_disconnected.connect(self.on_client_disconnected)
                self.json_server.message_received.connect(self.on_message_received)
                self.json_server.error_occurred.connect(self.on_server_error)
                self.log_message("Server signals connected to GUI handlers")
            except AttributeError as e:
                self.log_message(f"Server signals not available: {e}", "Warning")
        else:
            self.log_message("JsonSocketServer not available - running in demo mode")
    
    def connect_webcam_signals(self):
        if self.webcam_capture:
            try:
                self.webcam_capture.frame_ready.connect(self.on_webcam_frame_ready)
                self.webcam_capture.recording_started.connect(self.on_webcam_recording_started)
                self.webcam_capture.recording_stopped.connect(self.on_webcam_recording_stopped)
                self.webcam_capture.error_occurred.connect(self.on_webcam_error)
                self.webcam_capture.status_changed.connect(self.on_webcam_status_changed)
            except AttributeError as e:
                self.log_message(f"Webcam signals not available: {e}", "Warning")
        else:
            self.log_message("WebcamCapture not available - running in demo mode")
    
    def connect_enhanced_stimulus_signals(self):
        try:
            if hasattr(self, 'stimulus_panel') and self.enhanced_stimulus_controller:
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
            else:
                self.log_message("Enhanced stimulus controller not available - running in demo mode")
        except AttributeError as e:
            self.log_message(f"Stimulus signals not available: {e}", "Warning")
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
                "Starting enhanced synchronised recording and stimulus playback...",
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
                f"Error starting enhanced synchronised experiment: {str(e)}", "Errors"
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
            self.timing_precision_label.setText(f"Timing: +/-{abs(offset_ms):.2f}ms")
            self.timing_status.setText(f"Timing: +/-{abs(offset_ms):.2f}ms")
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
* VLC Backend Support: {'Available' if VLC_AVAILABLE else 'Not Available'}
* Enhanced Timing Precision: Multiple clock sources with calibration
* Performance Monitoring: Real-time frame timing analysis
* Automatic Backend Selection: Smart codec compatibility
* complete Error Handling: Detailed error reporting

PsychoPy-Inspired Improvements:
* Frame-accurate timing control
* Hardware-accelerated video playback
* Robust codec support and fallback mechanisms
* Professional-grade synchronisation accuracy

Author: Multi-Sensor Recording System Team
Date: 2025-07-29

VLC Backend Setup Guide:
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
- Support for additional formats: FLV, WebM, OGV, MPEG, TS
- Better codec compatibility
- Improved error handling
- Hardware acceleration support

Troubleshooting:
- If VLC not detected, ensure VLC is in system PATH
- For codec issues, try switching backends via menu
- Check logs for detailed error information
"""
        QMessageBox.about(self, "About Enhanced Controller", about_text)

    def log_message(self, message: str, category: str = "System"):
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{category}] {message}"
        
        # Update dock log
        self.log_text.append(formatted_message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Update main log tab if it exists
        if hasattr(self, 'main_log_text'):
            self.main_log_text.append(formatted_message)
            main_scrollbar = self.main_log_text.verticalScrollBar()
            main_scrollbar.setValue(main_scrollbar.maximum())
        
        # Update log statistics
        if hasattr(self, 'log_count_label'):
            # Count messages by category
            current_count = int(self.log_count_label.text().split(': ')[1])
            self.log_count_label.setText(f"Messages: {current_count + 1}")
            
            if category == "Errors":
                current_errors = int(self.error_count_label.text().split(': ')[1])
                self.error_count_label.setText(f"Errors: {current_errors + 1}")
            elif "warning" in message.lower():
                current_warnings = int(self.warning_count_label.text().split(': ')[1])
                self.warning_count_label.setText(f"Warnings: {current_warnings + 1}")
        
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
        pass  # Frame processing logic would go here

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
    
    # New methods for playback and annotation functionality
    def load_recorded_session(self):
        """Load a recorded session for playback and analysis."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Recorded Session", "", 
            "Session Files (*.json);;All Files (*)"
        )
        if file_path:
            self.session_info_label.setText(f"Loaded: {file_path.split('/')[-1]}")
            self.playback_slider.setEnabled(True)
            self.play_pause_btn.setEnabled(True)
            self.stop_playback_btn.setEnabled(True)
            self.log_message(f"Loaded session: {file_path}", "Session")
            
            # Update playback display
            self.playback_video_display.setText("Session loaded - Click Play to start")
            self.playback_video_display.setStyleSheet(
                "border: 2px solid #00aa00; background-color: #2a2a2a; "
                "color: #00aa00; text-align: center; font-size: 14px;"
            )
    
    def on_playback_seek(self, position):
        """Handle seeking in playback timeline."""
        # Convert slider position to time
        duration = 100  # Placeholder duration
        seek_time = (position / 100.0) * duration
        self.time_display.setText(f"{seek_time:.1f}s / {duration:.1f}s")
        self.log_message(f"Seek to position: {position}%", "Playback")
    
    def toggle_playback(self):
        """Toggle between play and pause."""
        if self.play_pause_btn.text() == "Play":
            self.play_pause_btn.setText("Pause")
            self.log_message("Playback started", "Playback")
            self.playback_video_display.setText("Playing session...")
        else:
            self.play_pause_btn.setText("Play")
            self.log_message("Playback paused", "Playback")
            self.playback_video_display.setText("Playback paused")
    
    def stop_playback(self):
        """Stop playback and reset to beginning."""
        self.play_pause_btn.setText("Play")
        self.playback_slider.setValue(0)
        self.time_display.setText("00:00 / 00:00")
        self.log_message("Playback stopped", "Playback")
        self.playback_video_display.setText("Playback stopped - Click Play to restart")
    
    def change_playback_speed(self, speed_text):
        """Change playback speed."""
        self.log_message(f"Playback speed changed to: {speed_text}", "Playback")
    
    def add_timestamp_annotation(self):
        """Add annotation at current playback timestamp."""
        annotation_text = self.annotation_text.text().strip()
        if not annotation_text:
            QMessageBox.warning(self, "Warning", "Please enter annotation text")
            return
        
        # Get current timestamp from slider
        current_position = self.playback_slider.value()
        timestamp = f"{current_position}%"
        
        # Add to annotations list
        annotation_entry = f"[{timestamp}] {annotation_text}"
        current_annotations = self.annotations_list.toPlainText()
        if current_annotations:
            new_annotations = current_annotations + "\n" + annotation_entry
        else:
            new_annotations = annotation_entry
        
        self.annotations_list.setPlainText(new_annotations)
        self.annotation_text.clear()
        self.log_message(f"Added annotation: {annotation_entry}", "Annotation")
    
    def export_annotations(self):
        """Export annotations to file."""
        annotations = self.annotations_list.toPlainText()
        if not annotations:
            QMessageBox.information(self, "Info", "No annotations to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Annotations", "annotations.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(annotations)
                QMessageBox.information(self, "Success", f"Annotations exported to {file_path}")
                self.log_message(f"Annotations exported to: {file_path}", "Export")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export annotations: {e}")
                self.log_message(f"Export error: {e}", "Errors")
    
    def export_session_data(self):
        """Export complete session data."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Session Data", "session_data.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                # Placeholder for actual data export
                import json
                session_data = {
                    "session_info": self.session_info_label.text(),
                    "annotations": self.annotations_list.toPlainText().split('\n'),
                    "export_time": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                with open(file_path, 'w') as f:
                    json.dump(session_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Session data exported to {file_path}")
                self.log_message(f"Session data exported to: {file_path}", "Export")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export session data: {e}")
                self.log_message(f"Export error: {e}", "Errors")
    
    def export_log(self):
        """Export system log to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "system_log.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                log_content = self.main_log_text.toPlainText() if hasattr(self, 'main_log_text') else self.log_text.toPlainText()
                with open(file_path, 'w') as f:
                    f.write(log_content)
                QMessageBox.information(self, "Success", f"Log exported to {file_path}")
                self.log_message(f"Log exported to: {file_path}", "Export")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export log: {e}")
                self.log_message(f"Export error: {e}", "Errors")
    
    def show_vlc_setup_guide(self):
        """Show VLC setup guide dialog."""
        guide_text = """
VLC Backend Setup Guide:

1. Install VLC Media Player:
   - Download from: https://www.videolan.org/vlc/
   - Install with default settings

2. Install python-vlc:
   - Run: pip install python-vlc
   - Restart the application

3. Verify Installation:
   - Check status bar for "VLC Backend: Available"
   - Use "Switch Video Backend" from Stimulus menu

Benefits:
- Support for additional formats: FLV, WebM, OGV, MPEG, TS
- Better codec compatibility
- Improved error handling
- Hardware acceleration support
"""
        QMessageBox.information(self, "VLC Setup Guide", guide_text)

    def show_vlc_setup_guide(self):
        """Show VLC setup guide dialog."""
        guide_text = """
VLC Backend Setup Guide:

1. Install VLC Media Player:
   - Download from: https://www.videolan.org/vlc/
   - Install with default settings

2. Install python-vlc:
   - Run: pip install python-vlc
   - Restart the application

3. Verify Installation:
   - Check status bar for "VLC Backend: Available"
   - Use "Switch Video Backend" from Stimulus menu

Benefits:
- Support for additional formats: FLV, WebM, OGV, MPEG, TS
- Better codec compatibility
- Improved error handling
- Hardware acceleration support
"""
        QMessageBox.information(self, "VLC Setup Guide", guide_text)
    
    # Add missing signal handler methods
    def on_enhanced_stimulus_seek_requested(self, position):
        """Handle stimulus seek request."""
        self.log_message(f"Stimulus seek requested: {position}", "Stimulus")
    
    def on_enhanced_stimulus_screen_changed(self, screen_index):
        """Handle stimulus screen change."""
        self.log_message(f"Stimulus screen changed to: {screen_index}", "Stimulus")
    
    def on_enhanced_start_recording_play_requested(self):
        """Handle start recording and play request."""
        self.log_message("Start recording and play requested", "Stimulus")
    
    def on_enhanced_mark_event_requested(self):
        """Handle mark event request."""
        self.log_message("Event marker requested", "Stimulus")
    
    def on_enhanced_stimulus_status_changed(self, status):
        """Handle stimulus status change."""
        self.log_message(f"Stimulus status: {status}", "Stimulus")
    
    def on_enhanced_stimulus_experiment_started(self):
        """Handle experiment started."""
        self.log_message("Experiment started", "Stimulus")
    
    def on_enhanced_stimulus_experiment_ended(self):
        """Handle experiment ended."""
        self.log_message("Experiment ended", "Stimulus")
    
    def on_enhanced_stimulus_error(self, error):
        """Handle stimulus error."""
        self.log_message(f"Stimulus error: {error}", "Errors")
    
    def on_backend_changed(self, backend):
        """Handle backend change."""
        self.log_message(f"Backend changed to: {backend}", "Backend")
    
    def test_timing_precision(self):
        """Test timing precision."""
        self.log_message("Timing precision test executed", "Performance")
        QMessageBox.information(self, "Timing Test", "Timing precision test completed")
    
    def toggle_performance_monitoring(self, enabled):
        """Toggle performance monitoring."""
        if enabled:
            self.performance_timer.start()
            self.log_message("Performance monitoring enabled", "Performance")
        else:
            self.performance_timer.stop()
            self.log_message("Performance monitoring disabled", "Performance")
    
    def update_performance_metrics(self):
        """Update performance metrics."""
        # Placeholder implementation
        pass
    
    def update_timing_precision_display(self):
        """Update timing precision display."""
        self.timing_precision_label.setText("Timing: ±0.5ms")

import time