"""
Preview Panel for Multi-Sensor Recording System Controller

This module implements the PreviewPanel class which manages the tabbed video feed
display interface for RGB and thermal camera streams from multiple devices.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework (Optional Modularization)
"""

import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QListWidget, QListWidgetItem, QSplitter,
    QTextEdit, QGroupBox, QComboBox, QSpinBox, QProgressBar
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

# Import centralized logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class PreviewPanel(QTabWidget):
    """Preview panel widget for displaying video feeds from multiple devices."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        # Create Device 1 tab
        self.device1_widget = self.create_device_tab("Device 1")
        self.addTab(self.device1_widget, "Device 1")

        # Create Device 2 tab
        self.device2_widget = self.create_device_tab("Device 2")
        self.addTab(self.device2_widget, "Device 2")

        # Create PC Webcam tab
        self.webcam_widget = self.create_webcam_tab("PC Webcam")
        self.addTab(self.webcam_widget, "PC Webcam")

        # Create Playback tab
        self.playback_widget = self.create_playback_tab()
        self.addTab(self.playback_widget, "Playback")

        # Store references to labels for easy access
        self.rgb_labels = [self.device1_widget.rgb_label, self.device2_widget.rgb_label]
        self.thermal_labels = [
            self.device1_widget.thermal_label,
            self.device2_widget.thermal_label,
        ]
        self.webcam_label = self.webcam_widget.webcam_label

    def create_device_tab(self, device_name):
        """
        Create a tab widget for a single device with RGB and thermal feed displays.

        Args:
            device_name (str): Name of the device for labeling

        Returns:
            QWidget: The device tab widget
        """
        device_widget = QWidget()
        device_layout = QVBoxLayout(device_widget)

        # RGB camera feed label
        rgb_label = QLabel("RGB Camera Feed")
        rgb_label.setMinimumSize(320, 240)
        rgb_label.setStyleSheet(
            "background-color: black; color: white; border: 1px solid gray;"
        )
        rgb_label.setAlignment(Qt.AlignCenter)
        device_layout.addWidget(rgb_label)

        # Thermal camera feed label
        thermal_label = QLabel("Thermal Camera Feed")
        thermal_label.setMinimumSize(320, 240)
        thermal_label.setStyleSheet(
            "background-color: black; color: white; border: 1px solid gray;"
        )
        thermal_label.setAlignment(Qt.AlignCenter)
        device_layout.addWidget(thermal_label)

        # Add stretch to push labels to top
        device_layout.addStretch(1)

        # Store label references in the widget for easy access
        device_widget.rgb_label = rgb_label
        device_widget.thermal_label = thermal_label

        return device_widget

    def create_webcam_tab(self, device_name):
        """
        Create a tab widget for PC webcam feed display.

        Args:
            device_name (str): Name of the webcam for labeling

        Returns:
            QWidget: The webcam tab widget
        """
        webcam_widget = QWidget()
        webcam_layout = QVBoxLayout(webcam_widget)

        # Webcam feed label
        webcam_label = QLabel("PC Webcam Feed")
        webcam_label.setMinimumSize(640, 480)  # Larger size for webcam
        webcam_label.setStyleSheet(
            "background-color: black; color: white; border: 1px solid gray;"
        )
        webcam_label.setAlignment(Qt.AlignCenter)
        webcam_layout.addWidget(webcam_label)

        # Add stretch to push label to top
        webcam_layout.addStretch(1)

        # Store label reference in the widget for easy access
        webcam_widget.webcam_label = webcam_label

        return webcam_widget

    def create_playback_tab(self):
        """
        Create a tab widget for session playback and review.

        Returns:
            QWidget: The playback tab widget
        """
        playback_widget = QWidget()
        main_layout = QHBoxLayout(playback_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel: Session browser and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Session selection group
        session_group = QGroupBox("Recorded Sessions")
        session_layout = QVBoxLayout(session_group)

        # Session list widget
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.on_session_selected)
        session_layout.addWidget(self.session_list)

        # Refresh sessions button
        refresh_btn = QPushButton("Refresh Sessions")
        refresh_btn.clicked.connect(self.refresh_session_list)
        session_layout.addWidget(refresh_btn)

        left_layout.addWidget(session_group)

        # File browser group
        files_group = QGroupBox("Session Files")
        files_layout = QVBoxLayout(files_group)

        # Files list widget
        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        files_layout.addWidget(self.files_list)

        left_layout.addWidget(files_group)

        # Playback controls group
        controls_group = QGroupBox("Playback Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Media player setup
        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Control buttons layout
        controls_buttons = QHBoxLayout()

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_pause_media)
        controls_buttons.addWidget(self.play_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_media)
        controls_buttons.addWidget(self.stop_btn)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1.0x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(self.change_playback_speed)
        speed_layout.addWidget(self.speed_combo)
        controls_buttons.addLayout(speed_layout)

        controls_layout.addLayout(controls_buttons)

        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        controls_layout.addWidget(self.progress_slider)

        # Time labels
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        controls_layout.addLayout(time_layout)

        left_layout.addWidget(controls_group)

        # Add left panel to splitter
        splitter.addWidget(left_panel)

        # Right panel: Video display and session info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Video display
        video_group = QGroupBox("Video Playback")
        video_layout = QVBoxLayout(video_group)
        video_layout.addWidget(self.video_widget)
        right_layout.addWidget(video_group)

        # Session information
        info_group = QGroupBox("Session Information")
        info_layout = QVBoxLayout(info_group)

        self.session_info_text = QTextEdit()
        self.session_info_text.setMaximumHeight(150)
        self.session_info_text.setReadOnly(True)
        info_layout.addWidget(self.session_info_text)

        right_layout.addWidget(info_group)

        # Add right panel to splitter
        splitter.addWidget(right_panel)

        # Set splitter proportions (left: 30%, right: 70%)
        splitter.setSizes([300, 700])

        # Initialize playback state
        self.current_file_path = None
        self.is_playing = False
        self.slider_being_dragged = False

        # Connect media player signals
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.stateChanged.connect(self.update_play_button)

        # Store widget reference
        playback_widget.session_list = self.session_list
        playback_widget.files_list = self.files_list
        playback_widget.session_info_text = self.session_info_text

        # Initialize with available sessions
        self.refresh_session_list()

        return playback_widget

    def update_rgb_feed(self, device_index, pixmap):
        """
        Update the RGB camera feed for a specific device.

        Args:
            device_index (int): Index of the device (0-based)
            pixmap (QPixmap): The image to display
        """
        if 0 <= device_index < len(self.rgb_labels):
            self.rgb_labels[device_index].setPixmap(pixmap)

    def update_thermal_feed(self, device_index, pixmap):
        """
        Update the thermal camera feed for a specific device.

        Args:
            device_index (int): Index of the device (0-based)
            pixmap (QPixmap): The image to display
        """
        if 0 <= device_index < len(self.thermal_labels):
            self.thermal_labels[device_index].setPixmap(pixmap)

    def update_webcam_feed(self, pixmap):
        """
        Update the PC webcam feed.

        Args:
            pixmap (QPixmap): The image to display
        """
        if hasattr(self, "webcam_label") and self.webcam_label:
            self.webcam_label.setPixmap(pixmap)

    def clear_webcam_feed(self):
        """Clear the PC webcam feed display."""
        if hasattr(self, "webcam_label") and self.webcam_label:
            self.webcam_label.clear()
            self.webcam_label.setText("PC Webcam Feed")

    def clear_feed(self, device_index, feed_type="both"):
        """
        Clear the video feed display for a specific device.

        Args:
            device_index (int): Index of the device (0-based)
            feed_type (str): Type of feed to clear ("rgb", "thermal", or "both")
        """
        if 0 <= device_index < len(self.rgb_labels):
            if feed_type in ["rgb", "both"]:
                self.rgb_labels[device_index].clear()
                self.rgb_labels[device_index].setText("RGB Camera Feed")

            if feed_type in ["thermal", "both"]:
                self.thermal_labels[device_index].clear()
                self.thermal_labels[device_index].setText("Thermal Camera Feed")

    def clear_all_feeds(self):
        """Clear all video feeds from all devices and webcam."""
        for i in range(len(self.rgb_labels)):
            self.clear_feed(i, "both")
        self.clear_webcam_feed()

    def set_device_tab_active(self, device_index):
        """
        Set the active tab to show a specific device.

        Args:
            device_index (int): Index of the device (0-based)
        """
        if 0 <= device_index < self.count():
            self.setCurrentIndex(device_index)

    def get_active_device_index(self):
        """
        Get the index of the currently active device tab.

        Returns:
            int: Index of the active device (0-based)
        """
        return self.currentIndex()

    # Playback tab methods
    def refresh_session_list(self):
        """Refresh the list of recorded sessions."""
        try:
            self.session_list.clear()
            
            # Look for session folders in the PythonApp/recordings directory
            recordings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recordings")
            
            if os.path.exists(recordings_path):
                for item in sorted(os.listdir(recordings_path)):
                    item_path = os.path.join(recordings_path, item)
                    if os.path.isdir(item_path) and item.startswith("session_"):
                        # Create list item with session metadata
                        list_item = QListWidgetItem(item)
                        
                        # Get session info if available
                        info_file = os.path.join(item_path, "session_info.json")
                        if os.path.exists(info_file):
                            try:
                                import json
                                with open(info_file, 'r') as f:
                                    session_info = json.load(f)
                                
                                # Format display text with duration and device count
                                duration = session_info.get('duration', 0)
                                device_count = len(session_info.get('devices', []))
                                display_text = f"{item} ({duration:.1f}s, {device_count} devices)"
                                list_item.setText(display_text)
                                
                            except Exception as e:
                                logger.warning(f"Could not read session info for {item}: {e}")
                        
                        # Store full path in item data
                        list_item.setData(Qt.UserRole, item_path)
                        self.session_list.addItem(list_item)
                        
                logger.info(f"Found {self.session_list.count()} recorded sessions")
            else:
                logger.info("No recordings directory found")
                
        except Exception as e:
            logger.error(f"Error refreshing session list: {e}")

    def on_session_selected(self, item):
        """Handle session selection from the list."""
        try:
            session_path = item.data(Qt.UserRole)
            if not session_path:
                return
                
            # Clear and populate files list
            self.files_list.clear()
            
            # List all video files in the session directory
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            
            for file_name in sorted(os.listdir(session_path)):
                file_path = os.path.join(session_path, file_name)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file_name.lower())
                    if ext in video_extensions:
                        # Create file item
                        file_item = QListWidgetItem(file_name)
                        file_item.setData(Qt.UserRole, file_path)
                        
                        # Add file size info
                        try:
                            file_size = os.path.getsize(file_path)
                            size_mb = file_size / (1024 * 1024)
                            file_item.setText(f"{file_name} ({size_mb:.1f} MB)")
                        except:
                            pass
                            
                        self.files_list.addItem(file_item)
            
            # Display session information
            self.display_session_info(session_path)
            
            logger.info(f"Loaded session: {os.path.basename(session_path)} with {self.files_list.count()} video files")
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")

    def display_session_info(self, session_path):
        """Display session information in the info panel."""
        try:
            info_text = f"Session Path: {session_path}\n\n"
            
            # Try to load session info JSON
            info_file = os.path.join(session_path, "session_info.json")
            if os.path.exists(info_file):
                try:
                    import json
                    with open(info_file, 'r') as f:
                        session_info = json.load(f)
                    
                    info_text += f"Session ID: {session_info.get('session_id', 'Unknown')}\n"
                    info_text += f"Start Time: {session_info.get('start_time', 'Unknown')}\n"
                    info_text += f"Duration: {session_info.get('duration', 0):.1f} seconds\n"
                    info_text += f"Status: {session_info.get('status', 'Unknown')}\n\n"
                    
                    # List devices
                    devices = session_info.get('devices', [])
                    info_text += f"Devices ({len(devices)}):\n"
                    for device in devices:
                        device_id = device.get('id', 'Unknown')
                        device_type = device.get('type', 'Unknown')
                        info_text += f"  - {device_id} ({device_type})\n"
                    
                    # List files
                    files = session_info.get('files', [])
                    if files:
                        info_text += f"\nFiles ({len(files)}):\n"
                        for file_info in files:
                            file_name = file_info.get('filename', 'Unknown')
                            file_type = file_info.get('file_type', 'Unknown')
                            file_size = file_info.get('file_size', 0)
                            size_mb = file_size / (1024 * 1024) if file_size else 0
                            info_text += f"  - {file_name} ({file_type}, {size_mb:.1f} MB)\n"
                    
                except Exception as e:
                    info_text += f"Error reading session info: {e}\n"
            else:
                info_text += "No session info file available.\n"
            
            # List actual files in directory
            all_files = []
            try:
                for file_name in os.listdir(session_path):
                    file_path = os.path.join(session_path, file_name)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        size_mb = file_size / (1024 * 1024)
                        all_files.append(f"  - {file_name} ({size_mb:.1f} MB)")
                
                if all_files:
                    info_text += f"\nActual Files in Directory ({len(all_files)}):\n"
                    info_text += "\n".join(all_files)
                    
            except Exception as e:
                info_text += f"\nError listing directory files: {e}"
            
            self.session_info_text.setText(info_text)
            
        except Exception as e:
            self.session_info_text.setText(f"Error displaying session info: {e}")
            logger.error(f"Error displaying session info: {e}")

    def on_file_double_clicked(self, item):
        """Handle double-click on a file to start playback."""
        try:
            file_path = item.data(Qt.UserRole)
            if not file_path or not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return
                
            # Load and play the media file
            media_content = QMediaContent(QUrl.fromLocalFile(file_path))
            self.media_player.setMedia(media_content)
            self.current_file_path = file_path
            
            # Start playback
            self.media_player.play()
            self.is_playing = True
            
            logger.info(f"Started playback of: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"Error starting playback: {e}")

    def play_pause_media(self):
        """Toggle play/pause for media playback."""
        try:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.is_playing = False
            else:
                self.media_player.play()
                self.is_playing = True
                
        except Exception as e:
            logger.error(f"Error toggling playback: {e}")

    def stop_media(self):
        """Stop media playback."""
        try:
            self.media_player.stop()
            self.is_playing = False
            self.progress_slider.setValue(0)
            self.current_time_label.setText("00:00")
            
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")

    def change_playback_speed(self, speed_text):
        """Change playback speed."""
        try:
            speed_map = {
                "0.25x": 0.25,
                "0.5x": 0.5,
                "1.0x": 1.0,
                "1.5x": 1.5,
                "2.0x": 2.0
            }
            
            speed = speed_map.get(speed_text, 1.0)
            self.media_player.setPlaybackRate(speed)
            
        except Exception as e:
            logger.error(f"Error changing playback speed: {e}")

    def update_position(self, position):
        """Update progress slider position."""
        if not self.slider_being_dragged:
            duration = self.media_player.duration()
            if duration > 0:
                self.progress_slider.setValue(int((position / duration) * 100))
            
            # Update time label
            minutes = position // 60000
            seconds = (position % 60000) // 1000
            self.current_time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_duration(self, duration):
        """Update total duration display."""
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        self.total_time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_play_button(self, state):
        """Update play button text based on player state."""
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("Pause")
        else:
            self.play_btn.setText("Play")

    def on_slider_pressed(self):
        """Handle slider press to prevent automatic updates."""
        self.slider_being_dragged = True

    def on_slider_released(self):
        """Handle slider release to seek to new position."""
        self.slider_being_dragged = False
        
        duration = self.media_player.duration()
        if duration > 0:
            position = int((self.progress_slider.value() / 100) * duration)
            self.media_player.setPosition(position)

    def get_rgb_label(self, device_index):
        """
        Get the RGB label widget for a specific device.

        Args:
            device_index (int): Index of the device (0-based)

        Returns:
            QLabel: The RGB label widget, or None if invalid index
        """
        if 0 <= device_index < len(self.rgb_labels):
            return self.rgb_labels[device_index]
        return None

    def get_thermal_label(self, device_index):
        """
        Get the thermal label widget for a specific device.

        Args:
            device_index (int): Index of the device (0-based)

        Returns:
            QLabel: The thermal label widget, or None if invalid index
        """
        if 0 <= device_index < len(self.thermal_labels):
            return self.thermal_labels[device_index]
        return None
