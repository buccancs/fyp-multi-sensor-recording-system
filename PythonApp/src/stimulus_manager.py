"""
StimulusManager - Advanced stimulus presentation system

Provides multi-monitor support, precise timing controls, and audio-visual
coordination for research-grade stimulus presentation.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import sys
import os
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QDesktopWidget, QMainWindow)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QScreen, QPixmap, QFont, QPalette, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl


@dataclass
class MonitorInfo:
    """Information about available monitors"""
    monitor_id: int
    name: str
    geometry: QRect
    is_primary: bool = False
    dpi: float = 96.0


@dataclass
class StimulusConfig:
    """Configuration for stimulus presentation"""
    stimulus_type: str = "video"  # video, image, text, pattern
    content_path: Optional[str] = None
    duration_ms: int = 5000
    timing_precision_us: int = 1000
    audio_enabled: bool = True
    fullscreen: bool = True
    monitor_id: int = 0
    background_color: str = "#000000"
    text_content: Optional[str] = None
    font_size: int = 48
    synchronization_markers: List[int] = field(default_factory=list)


@dataclass
class StimulusEvent:
    """Stimulus presentation event"""
    event_type: str
    timestamp: float
    monitor_id: int
    stimulus_config: StimulusConfig
    duration_actual_ms: Optional[float] = None


class StimulusWindow(QMainWindow):
    """Fullscreen stimulus presentation window"""
    
    def __init__(self, monitor_info: MonitorInfo, config: StimulusConfig):
        super().__init__()
        self.monitor_info = monitor_info
        self.config = config
        self.media_player: Optional[QMediaPlayer] = None
        self.video_widget: Optional[QVideoWidget] = None
        
        self.setup_window()
        self.setup_content()
    
    def setup_window(self):
        """Setup fullscreen window on specified monitor"""
        # Set window properties
        self.setWindowTitle("Stimulus Presentation")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Set geometry to monitor
        self.setGeometry(self.monitor_info.geometry)
        
        # Set background color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.config.background_color))
        self.setPalette(palette)
        
        if self.config.fullscreen:
            self.showFullScreen()
    
    def setup_content(self):
        """Setup stimulus content based on configuration"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.config.stimulus_type == "video" and self.config.content_path:
            self.setup_video_content(layout)
        elif self.config.stimulus_type == "image" and self.config.content_path:
            self.setup_image_content(layout)
        elif self.config.stimulus_type == "text":
            self.setup_text_content(layout)
        elif self.config.stimulus_type == "pattern":
            self.setup_pattern_content(layout)
    
    def setup_video_content(self, layout):
        """Setup video stimulus content"""
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        
        # Load video file
        if os.path.exists(self.config.content_path):
            media_content = QMediaContent(QUrl.fromLocalFile(self.config.content_path))
            self.media_player.setMedia(media_content)
        
        layout.addWidget(self.video_widget)
    
    def setup_image_content(self, layout):
        """Setup image stimulus content"""
        label = QLabel()
        if os.path.exists(self.config.content_path):
            pixmap = QPixmap(self.config.content_path)
            # Scale to fit screen while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.monitor_info.geometry.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
        
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    
    def setup_text_content(self, layout):
        """Setup text stimulus content"""
        label = QLabel(self.config.text_content or "Stimulus Text")
        label.setAlignment(Qt.AlignCenter)
        
        # Set font
        font = QFont()
        font.setPointSize(self.config.font_size)
        label.setFont(font)
        
        # Set text color (white on black background)
        label.setStyleSheet("color: white;")
        
        layout.addWidget(label)
    
    def setup_pattern_content(self, layout):
        """Setup pattern stimulus content"""
        # Create simple test pattern
        label = QLabel("● TEST PATTERN ●")
        label.setAlignment(Qt.AlignCenter)
        
        font = QFont()
        font.setPointSize(72)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: white;")
        
        layout.addWidget(label)
    
    def start_presentation(self):
        """Start stimulus presentation"""
        if self.media_player and self.config.stimulus_type == "video":
            if self.config.audio_enabled:
                self.media_player.setMuted(False)
            else:
                self.media_player.setMuted(True)
            self.media_player.play()
    
    def stop_presentation(self):
        """Stop stimulus presentation"""
        if self.media_player:
            self.media_player.stop()


class StimulusManager:
    """
    Advanced stimulus presentation manager
    
    Provides multi-monitor support, precise timing, and audio-visual coordination
    """
    
    def __init__(self, logger=None):
        """Initialize StimulusManager"""
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        self.available_monitors: List[MonitorInfo] = []
        self.stimulus_windows: Dict[int, StimulusWindow] = {}
        self.presentation_timers: Dict[int, QTimer] = {}
        self.event_callbacks: List[Callable[[StimulusEvent], None]] = []
        self.presentation_history: List[StimulusEvent] = []
        
        # Timing and synchronization
        self.high_precision_timer = QTimer()
        self.high_precision_timer.setSingleShot(True)
        self.synchronization_offset_ms = 0.0
        
        self.logger.info("StimulusManager initialized")

    def initialize(self) -> bool:
        """Initialize stimulus manager"""
        try:
            self.logger.info("Initializing StimulusManager...")
            
            # Detect available monitors
            app = QApplication.instance()
            if not app:
                self.logger.error("No QApplication instance found")
                return False
            
            # Get monitor information
            desktop = QDesktopWidget()
            screens = app.screens()
            
            self.available_monitors = []
            for i, screen in enumerate(screens):
                monitor_info = MonitorInfo(
                    monitor_id=i,
                    name=screen.name(),
                    geometry=screen.geometry(),
                    is_primary=(i == desktop.primaryScreen()),
                    dpi=screen.logicalDotsPerInch()
                )
                self.available_monitors.append(monitor_info)
                
                self.logger.info(f"Monitor {i}: {monitor_info.name} "
                               f"({monitor_info.geometry.width()}x{monitor_info.geometry.height()}) "
                               f"{'[PRIMARY]' if monitor_info.is_primary else ''}")
            
            self.is_initialized = True
            self.logger.info(f"StimulusManager initialized with {len(self.available_monitors)} monitors")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize StimulusManager: {e}")
            return False

    def get_monitor_count(self) -> int:
        """Get number of available monitors"""
        return len(self.available_monitors)

    def get_monitor_info(self, monitor_id: int) -> Optional[MonitorInfo]:
        """Get information about specific monitor"""
        if 0 <= monitor_id < len(self.available_monitors):
            return self.available_monitors[monitor_id]
        return None

    def get_primary_monitor_id(self) -> int:
        """Get ID of primary monitor"""
        for monitor in self.available_monitors:
            if monitor.is_primary:
                return monitor.monitor_id
        return 0

    def get_secondary_monitor_id(self) -> Optional[int]:
        """Get ID of first secondary monitor (for participant display)"""
        for monitor in self.available_monitors:
            if not monitor.is_primary:
                return monitor.monitor_id
        return None

    def present_stimulus(self, config: StimulusConfig) -> bool:
        """Present stimulus with advanced timing"""
        try:
            if not self.is_initialized:
                self.logger.error("StimulusManager not initialized")
                return False
            
            # Validate monitor ID
            if config.monitor_id >= len(self.available_monitors):
                self.logger.error(f"Invalid monitor ID: {config.monitor_id}")
                return False
            
            monitor_info = self.available_monitors[config.monitor_id]
            self.logger.info(f"Presenting {config.stimulus_type} stimulus on monitor {config.monitor_id}")
            
            # Create stimulus window
            stimulus_window = StimulusWindow(monitor_info, config)
            self.stimulus_windows[config.monitor_id] = stimulus_window
            
            # Show window
            stimulus_window.show()
            
            # Start presentation with precise timing
            start_time = time.time()
            stimulus_window.start_presentation()
            
            # Create presentation event
            event = StimulusEvent(
                event_type="stimulus_start",
                timestamp=start_time,
                monitor_id=config.monitor_id,
                stimulus_config=config
            )
            self.presentation_history.append(event)
            
            # Call event callbacks
            for callback in self.event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")
            
            # Set up automatic stop timer if duration specified
            if config.duration_ms > 0:
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(
                    lambda: self._stop_stimulus_presentation(config.monitor_id, start_time)
                )
                timer.start(config.duration_ms)
                self.presentation_timers[config.monitor_id] = timer
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error presenting stimulus: {e}")
            return False

    def stop_stimulus(self, monitor_id: int) -> bool:
        """Stop stimulus presentation on specified monitor"""
        try:
            if monitor_id in self.stimulus_windows:
                self._stop_stimulus_presentation(monitor_id, time.time())
                return True
            else:
                self.logger.warning(f"No active stimulus on monitor {monitor_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping stimulus: {e}")
            return False

    def stop_all_stimuli(self) -> None:
        """Stop all active stimulus presentations"""
        try:
            monitor_ids = list(self.stimulus_windows.keys())
            for monitor_id in monitor_ids:
                self.stop_stimulus(monitor_id)
                
        except Exception as e:
            self.logger.error(f"Error stopping all stimuli: {e}")

    def present_synchronized_stimuli(self, configs: List[StimulusConfig]) -> bool:
        """Present multiple stimuli with synchronized timing"""
        try:
            if not configs:
                return False
            
            self.logger.info(f"Presenting {len(configs)} synchronized stimuli")
            
            # Prepare all windows first
            windows = []
            for config in configs:
                if config.monitor_id >= len(self.available_monitors):
                    self.logger.error(f"Invalid monitor ID: {config.monitor_id}")
                    continue
                
                monitor_info = self.available_monitors[config.monitor_id]
                window = StimulusWindow(monitor_info, config)
                window.show()
                windows.append((window, config))
                self.stimulus_windows[config.monitor_id] = window
            
            # Start all presentations simultaneously
            start_time = time.time()
            for window, config in windows:
                window.start_presentation()
                
                # Create event
                event = StimulusEvent(
                    event_type="synchronized_stimulus_start",
                    timestamp=start_time,
                    monitor_id=config.monitor_id,
                    stimulus_config=config
                )
                self.presentation_history.append(event)
            
            # Set up synchronized stop timers
            max_duration = max(config.duration_ms for config in configs if config.duration_ms > 0)
            if max_duration > 0:
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: self.stop_all_stimuli())
                timer.start(max_duration)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error presenting synchronized stimuli: {e}")
            return False

    def add_event_callback(self, callback: Callable[[StimulusEvent], None]) -> None:
        """Add callback for stimulus events"""
        self.event_callbacks.append(callback)

    def get_presentation_history(self) -> List[StimulusEvent]:
        """Get history of stimulus presentations"""
        return self.presentation_history.copy()

    def _stop_stimulus_presentation(self, monitor_id: int, start_time: float) -> None:
        """Internal method to stop stimulus presentation"""
        try:
            if monitor_id in self.stimulus_windows:
                window = self.stimulus_windows[monitor_id]
                window.stop_presentation()
                window.close()
                del self.stimulus_windows[monitor_id]
                
                # Clean up timer
                if monitor_id in self.presentation_timers:
                    self.presentation_timers[monitor_id].stop()
                    del self.presentation_timers[monitor_id]
                
                # Create stop event
                stop_time = time.time()
                duration_ms = (stop_time - start_time) * 1000
                
                event = StimulusEvent(
                    event_type="stimulus_stop",
                    timestamp=stop_time,
                    monitor_id=monitor_id,
                    stimulus_config=None,  # Could store config if needed
                    duration_actual_ms=duration_ms
                )
                self.presentation_history.append(event)
                
                # Call callbacks
                for callback in self.event_callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        self.logger.error(f"Error in stop event callback: {e}")
                
                self.logger.info(f"Stopped stimulus on monitor {monitor_id} (duration: {duration_ms:.1f}ms)")
                
        except Exception as e:
            self.logger.error(f"Error stopping stimulus presentation: {e}")

    def cleanup(self) -> None:
        """Clean up stimulus manager resources"""
        try:
            self.logger.info("Cleaning up StimulusManager...")
            
            # Stop all active presentations
            self.stop_all_stimuli()
            
            # Clean up timers
            for timer in self.presentation_timers.values():
                timer.stop()
            self.presentation_timers.clear()
            
            # Clear data
            self.stimulus_windows.clear()
            self.event_callbacks.clear()
            
            self.is_initialized = False
            self.logger.info("StimulusManager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    # Test stimulus manager
    app = QApplication(sys.argv)
    manager = StimulusManager()
    
    if manager.initialize():
        print(f"Found {manager.get_monitor_count()} monitors")
        
        config = StimulusConfig(
            stimulus_type="test_pattern",
            duration_ms=3000
        )
        manager.present_stimulus(config)
    
    manager.cleanup()
