"""
Preview Panel for Multi-Sensor Recording System Controller

This module implements the PreviewPanel class which manages the tabbed video feed
display interface for RGB and thermal camera streams from multiple devices.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework (Optional Modularization)
"""

from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


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
        
        # Store references to labels for easy access
        self.rgb_labels = [self.device1_widget.rgb_label, self.device2_widget.rgb_label]
        self.thermal_labels = [self.device1_widget.thermal_label, self.device2_widget.thermal_label]
    
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
        rgb_label.setStyleSheet("background-color: black; color: white; border: 1px solid gray;")
        rgb_label.setAlignment(Qt.AlignCenter)
        device_layout.addWidget(rgb_label)
        
        # Thermal camera feed label
        thermal_label = QLabel("Thermal Camera Feed")
        thermal_label.setMinimumSize(320, 240)
        thermal_label.setStyleSheet("background-color: black; color: white; border: 1px solid gray;")
        thermal_label.setAlignment(Qt.AlignCenter)
        device_layout.addWidget(thermal_label)
        
        # Add stretch to push labels to top
        device_layout.addStretch(1)
        
        # Store label references in the widget for easy access
        device_widget.rgb_label = rgb_label
        device_widget.thermal_label = thermal_label
        
        return device_widget
    
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
        """Clear all video feeds from all devices."""
        for i in range(len(self.rgb_labels)):
            self.clear_feed(i, "both")
    
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
