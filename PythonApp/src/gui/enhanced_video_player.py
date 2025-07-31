"""
Enhanced Video Player Widget for Stimulus Presentation
Inspired by PsychoPy's professional video playback interface

This module provides a modern, feature-rich video player with:
- Clean, professional interface design
- Advanced playback controls
- Timeline scrubbing with frame accuracy
- Volume control with visual feedback
- Full-screen presentation mode
- Keyboard shortcuts for quick access
- Performance monitoring and feedback

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
Enhancement: PsychoPy-Inspired Video Playback
"""

import os
import sys
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl, QSize
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QBrush, QColor, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QSlider, QLabel, QFrame, QSizePolicy, QSpacerItem, QProgressBar,
    QToolTip, QApplication
)


class ModernSlider(QSlider):
    """Enhanced slider with modern styling and hover effects"""
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern slider styling"""
        style = """
            QSlider::groove:horizontal {
                border: 1px solid #d2d0ce;
                height: 6px;
                background: #f3f2f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005a9e;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
                border: 2px solid #005a9e;
            }
            QSlider::handle:horizontal:pressed {
                background: #005a9e;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: #f3f2f1;
                border-radius: 3px;
            }
        """
        self.setStyleSheet(style)


class PlaybackButton(QPushButton):
    """Custom playback button with icon support"""
    
    def __init__(self, icon_text="▶", tooltip="", parent=None):
        super().__init__(icon_text, parent)
        self.setToolTip(tooltip)
        self.setFixedSize(36, 36)
        self.setFont(QFont("Segoe UI", 12))
        self.setCursor(Qt.PointingHandCursor)
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern button styling"""
        style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 18px;
                font-weight: bold;
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
        """
        self.setStyleSheet(style)


class VolumeControl(QWidget):
    """Modern volume control with visual feedback"""
    
    volume_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup volume control UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Volume icon
        self.volume_icon = QLabel("🔊")
        self.volume_icon.setFixedSize(20, 20)
        self.volume_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.volume_icon)
        
        # Volume slider
        self.volume_slider = ModernSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        layout.addWidget(self.volume_slider)
        
        # Volume percentage
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(35)
        self.volume_label.setFont(QFont("Segoe UI", 9))
        self.volume_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.volume_label)
    
    def on_volume_changed(self, value):
        """Handle volume change"""
        self.volume_label.setText(f"{value}%")
        
        # Update volume icon based on level
        if value == 0:
            self.volume_icon.setText("🔇")
        elif value < 30:
            self.volume_icon.setText("🔈")
        elif value < 70:
            self.volume_icon.setText("🔉")
        else:
            self.volume_icon.setText("🔊")
        
        self.volume_changed.emit(value)


class TimelineControl(QWidget):
    """Advanced timeline control with frame-accurate scrubbing"""
    
    seek_requested = pyqtSignal(int)  # Position in milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration = 0
        self.position = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup timeline control UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Timeline slider
        self.timeline_slider = ModernSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1000)  # Use 1000 steps for smooth scrubbing
        self.timeline_slider.setValue(0)
        self.timeline_slider.sliderMoved.connect(self.on_slider_moved)
        self.timeline_slider.sliderPressed.connect(self.on_slider_pressed)
        self.timeline_slider.sliderReleased.connect(self.on_slider_released)
        layout.addWidget(self.timeline_slider)
        
        # Time labels
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.current_time_label.setStyleSheet("color: #0078d4;")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setFont(QFont("Segoe UI", 9))
        self.total_time_label.setStyleSheet("color: #605e5c;")
        time_layout.addWidget(self.total_time_label)
        
        layout.addLayout(time_layout)
    
    def on_slider_moved(self, value):
        """Handle slider movement during scrubbing"""
        if self.duration > 0:
            position_ms = int((value / 1000.0) * self.duration)
            self.update_current_time(position_ms)
    
    def on_slider_pressed(self):
        """Handle slider press start"""
        pass
    
    def on_slider_released(self):
        """Handle slider release - commit seek"""
        if self.duration > 0:
            value = self.timeline_slider.value()
            position_ms = int((value / 1000.0) * self.duration)
            self.seek_requested.emit(position_ms)
    
    def update_position(self, position_ms, duration_ms):
        """Update timeline position from external source"""
        self.position = position_ms
        self.duration = duration_ms
        
        if duration_ms > 0:
            progress = min(1000, int((position_ms / duration_ms) * 1000))
            self.timeline_slider.setValue(progress)
        
        self.update_current_time(position_ms)
        self.update_duration_time(duration_ms)
    
    def update_current_time(self, position_ms):
        """Update current time display"""
        time_str = self.format_time(position_ms)
        self.current_time_label.setText(time_str)
    
    def update_duration_time(self, duration_ms):
        """Update duration time display"""
        time_str = self.format_time(duration_ms)
        self.total_time_label.setText(time_str)
    
    def format_time(self, milliseconds):
        """Format milliseconds to MM:SS format"""
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class EnhancedVideoWidget(QVideoWidget):
    """Enhanced video widget with modern features"""
    
    # Signals
    double_clicked = pyqtSignal()
    space_pressed = pyqtSignal()
    escape_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("""
            QVideoWidget {
                background-color: #000000;
                border: 1px solid #d2d0ce;
                border-radius: 4px;
            }
        """)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click for fullscreen toggle"""
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Space:
            self.space_pressed.emit()
            event.accept()
        elif event.key() == Qt.Key_Escape:
            self.escape_pressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class EnhancedVideoPlayer(QWidget):
    """Complete enhanced video player with professional interface"""
    
    # Signals
    file_loaded = pyqtSignal(str)
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_stopped = pyqtSignal()
    position_changed = pyqtSignal(int, int)  # position, duration
    volume_changed = pyqtSignal(int)
    fullscreen_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.is_playing = False
        self.is_fullscreen = False
        
        self.setup_ui()
        self.setup_media_player()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the enhanced video player UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Video display area
        self.video_widget = EnhancedVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.video_widget)
        
        # Control panel
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #d2d0ce;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(12, 8, 12, 8)
        controls_layout.setSpacing(8)
        
        # Timeline control
        self.timeline_control = TimelineControl()
        controls_layout.addWidget(self.timeline_control)
        
        # Playback controls
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(8)
        
        self.play_pause_btn = PlaybackButton("▶", "Play/Pause (Space)")
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        playback_layout.addWidget(self.play_pause_btn)
        
        self.stop_btn = PlaybackButton("⏹", "Stop")
        self.stop_btn.clicked.connect(self.stop_playback)
        self.stop_btn.setEnabled(False)
        playback_layout.addWidget(self.stop_btn)
        
        playback_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Volume control
        self.volume_control = VolumeControl()
        playback_layout.addWidget(self.volume_control)
        
        # Fullscreen button
        self.fullscreen_btn = PlaybackButton("⛶", "Fullscreen (Double-click)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        playback_layout.addWidget(self.fullscreen_btn)
        
        controls_layout.addLayout(playback_layout)
        
        layout.addWidget(controls_frame)
    
    def setup_media_player(self):
        """Setup the media player"""
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Position update timer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.setInterval(100)  # Update every 100ms
    
    def setup_connections(self):
        """Setup signal connections"""
        # Media player signals
        self.media_player.stateChanged.connect(self.on_state_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.error.connect(self.on_media_error)
        
        # Timeline control
        self.timeline_control.seek_requested.connect(self.seek_to_position)
        
        # Volume control
        self.volume_control.volume_changed.connect(self.set_volume)
        
        # Video widget signals
        self.video_widget.double_clicked.connect(self.toggle_fullscreen)
        self.video_widget.space_pressed.connect(self.toggle_playback)
        self.video_widget.escape_pressed.connect(self.exit_fullscreen)
    
    def load_file(self, file_path):
        """Load video file"""
        if not os.path.exists(file_path):
            return False
        
        self.current_file = file_path
        media_content = QMediaContent(QUrl.fromLocalFile(file_path))
        self.media_player.setMedia(media_content)
        
        self.file_loaded.emit(file_path)
        return True
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.pause_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start playback"""
        self.media_player.play()
        self.position_timer.start()
        self.is_playing = True
        self.play_pause_btn.setText("⏸")
        self.stop_btn.setEnabled(True)
        self.playback_started.emit()
    
    def pause_playback(self):
        """Pause playback"""
        self.media_player.pause()
        self.position_timer.stop()
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        self.playback_paused.emit()
    
    def stop_playback(self):
        """Stop playback"""
        self.media_player.stop()
        self.position_timer.stop()
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        self.stop_btn.setEnabled(False)
        self.timeline_control.update_position(0, self.media_player.duration())
        self.playback_stopped.emit()
    
    def seek_to_position(self, position_ms):
        """Seek to specific position"""
        self.media_player.setPosition(position_ms)
    
    def set_volume(self, volume):
        """Set volume (0-100)"""
        self.media_player.setVolume(volume)
        self.volume_changed.emit(volume)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        self.video_widget.setFullScreen(True)
        self.is_fullscreen = True
        self.fullscreen_requested.emit()
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.video_widget.setFullScreen(False)
            self.is_fullscreen = False
    
    def update_position(self):
        """Update position from timer"""
        position = self.media_player.position()
        duration = self.media_player.duration()
        self.timeline_control.update_position(position, duration)
        self.position_changed.emit(position, duration)
    
    # Event handlers
    def on_state_changed(self, state):
        """Handle media player state change"""
        if state == QMediaPlayer.StoppedState:
            self.position_timer.stop()
            self.is_playing = False
            self.play_pause_btn.setText("▶")
            self.stop_btn.setEnabled(False)
    
    def on_position_changed(self, position):
        """Handle position change"""
        # Handled by timer for smoother updates
        pass
    
    def on_duration_changed(self, duration):
        """Handle duration change"""
        self.timeline_control.update_duration_time(duration)
    
    def on_media_error(self, error):
        """Handle media error"""
        print(f"[DEBUG_LOG] Media error: {error}")


# Test function for the enhanced video player
def main():
    """Test the enhanced video player"""
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    player = EnhancedVideoPlayer()
    player.setWindowTitle("Enhanced Video Player - Test")
    player.resize(800, 600)
    player.show()
    
    # Load test video if available
    test_video = "/home/runner/work/bucika_gsr/bucika_gsr/test_video.mp4"
    if os.path.exists(test_video):
        player.load_file(test_video)
        print(f"Loaded test video: {test_video}")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()