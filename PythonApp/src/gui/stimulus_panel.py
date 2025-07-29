"""
Stimulus Control Panel for Multi-Sensor Recording System Controller

This module implements the StimulusControlPanel class which manages media playback
controls including file selection, play/pause buttons, timeline control, and output screen selection.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework (Optional Modularization)
"""

import os
from PyQt5.QtWidgets import (
    QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QSlider, 
    QComboBox, QLabel, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal


class StimulusControlPanel(QGroupBox):
    """Stimulus control panel widget for media playback controls."""
    
    # Signals for communicating with parent window
    file_loaded = pyqtSignal(str)  # Emitted when a file is loaded
    play_requested = pyqtSignal()  # Emitted when play is requested
    pause_requested = pyqtSignal()  # Emitted when pause is requested
    seek_requested = pyqtSignal(int)  # Emitted when seeking to a position
    screen_changed = pyqtSignal(int)  # Emitted when output screen changes
    
    def __init__(self, parent=None):
        super().__init__("Stimulus Controls", parent)
        self.parent_window = parent
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        stim_layout = QHBoxLayout(self)
        
        # File selection
        self.stim_file_path = QLineEdit()
        self.stim_file_path.setPlaceholderText("No file loaded")
        self.stim_file_path.setReadOnly(True)
        stim_layout.addWidget(self.stim_file_path)
        
        # Browse button
        self.browse_btn = QPushButton("Load Stimulus...")
        self.browse_btn.clicked.connect(self.browse_stimulus_file)
        stim_layout.addWidget(self.browse_btn)
        
        # Play button
        self.play_btn = QPushButton("Play")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.handle_play)
        stim_layout.addWidget(self.play_btn)
        
        # Pause button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.handle_pause)
        stim_layout.addWidget(self.pause_btn)
        
        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.sliderMoved.connect(self.handle_seek)
        stim_layout.addWidget(self.timeline_slider)
        
        # Output screen selector
        screen_label = QLabel("Output Screen:")
        stim_layout.addWidget(screen_label)
        
        self.screen_combo = QComboBox()
        self.populate_screen_combo()
        self.screen_combo.currentIndexChanged.connect(self.handle_screen_change)
        stim_layout.addWidget(self.screen_combo)
    
    def populate_screen_combo(self):
        """Populate the screen combo box with available screens."""
        self.screen_combo.clear()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            screen_name = screen.name() or f"Screen {i+1}"
            screen_info = f"{screen_name} ({screen.size().width()}x{screen.size().height()})"
            self.screen_combo.addItem(screen_info)
        
        # Select second screen by default if available
        if len(screens) > 1:
            self.screen_combo.setCurrentIndex(1)
    
    def browse_stimulus_file(self):
        """Browse for stimulus file."""
        fname, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Stimulus Video", 
            "", 
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        if fname:
            self.load_file(fname)
    
    def load_file(self, file_path):
        """
        Load a stimulus file.
        
        Args:
            file_path (str): Path to the file to load
        """
        self.current_file = file_path
        self.stim_file_path.setText(file_path)
        
        # Enable play/pause buttons when file is loaded
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        
        # Reset timeline slider
        self.timeline_slider.setValue(0)
        
        # Emit signal and update parent status
        self.file_loaded.emit(file_path)
        if self.parent_window and hasattr(self.parent_window, 'statusBar'):
            self.parent_window.statusBar().showMessage(f"Loaded stimulus: {os.path.basename(file_path)}")
    
    def handle_play(self):
        """Handle play button press."""
        self.play_requested.emit()
        if self.parent_window and hasattr(self.parent_window, 'statusBar'):
            self.parent_window.statusBar().showMessage("Play stimulus (simulation)")
    
    def handle_pause(self):
        """Handle pause button press."""
        self.pause_requested.emit()
        if self.parent_window and hasattr(self.parent_window, 'statusBar'):
            self.parent_window.statusBar().showMessage("Pause stimulus (simulation)")
    
    def handle_seek(self, value):
        """
        Handle timeline slider movement.
        
        Args:
            value (int): Slider position (0-100)
        """
        self.seek_requested.emit(value)
        if self.parent_window and hasattr(self.parent_window, 'statusBar'):
            self.parent_window.statusBar().showMessage(f"Seek to {value}% (simulation)")
    
    def handle_screen_change(self, index):
        """
        Handle output screen selection change.
        
        Args:
            index (int): Selected screen index
        """
        self.screen_changed.emit(index)
    
    def get_current_file(self):
        """
        Get the currently loaded file path.
        
        Returns:
            str: Current file path, or None if no file loaded
        """
        return self.current_file
    
    def get_timeline_position(self):
        """
        Get the current timeline slider position.
        
        Returns:
            int: Timeline position (0-100)
        """
        return self.timeline_slider.value()
    
    def set_timeline_position(self, position):
        """
        Set the timeline slider position.
        
        Args:
            position (int): Position to set (0-100)
        """
        self.timeline_slider.setValue(position)
    
    def get_selected_screen(self):
        """
        Get the currently selected output screen index.
        
        Returns:
            int: Selected screen index
        """
        return self.screen_combo.currentIndex()
    
    def set_selected_screen(self, index):
        """
        Set the selected output screen.
        
        Args:
            index (int): Screen index to select
        """
        if 0 <= index < self.screen_combo.count():
            self.screen_combo.setCurrentIndex(index)
    
    def enable_controls(self, enabled=True):
        """
        Enable or disable all controls.
        
        Args:
            enabled (bool): True to enable, False to disable
        """
        self.browse_btn.setEnabled(enabled)
        self.play_btn.setEnabled(enabled and self.current_file is not None)
        self.pause_btn.setEnabled(enabled and self.current_file is not None)
        self.timeline_slider.setEnabled(enabled)
        self.screen_combo.setEnabled(enabled)
    
    def reset_controls(self):
        """Reset all controls to their initial state."""
        self.current_file = None
        self.stim_file_path.clear()
        self.stim_file_path.setPlaceholderText("No file loaded")
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.timeline_slider.setValue(0)
        self.populate_screen_combo()  # Refresh screen list
    
    def refresh_screens(self):
        """Refresh the list of available screens."""
        current_selection = self.screen_combo.currentIndex()
        self.populate_screen_combo()
        
        # Try to maintain the same selection if possible
        if current_selection < self.screen_combo.count():
            self.screen_combo.setCurrentIndex(current_selection)
