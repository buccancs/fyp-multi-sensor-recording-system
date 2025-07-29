"""
Device Status Panel for Multi-Sensor Recording System Controller

This module implements the DeviceStatusPanel class which manages the device list
and connection status display for the GUI application.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework (Optional Modularization)
"""

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QListWidget


class DeviceStatusPanel(QGroupBox):
    """Device status panel widget for displaying connected devices and their status."""
    
    def __init__(self, parent=None):
        super().__init__("Devices", parent)
        self.init_ui()
        self.init_placeholder_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create layout
        device_layout = QVBoxLayout(self)
        
        # Device list widget
        self.device_list = QListWidget()
        device_layout.addWidget(self.device_list)
        
        # Set maximum width to prevent it from taking too much space
        self.setMaximumWidth(250)
    
    def init_placeholder_data(self):
        """Initialize placeholder data for testing."""
        # Add placeholder devices to the list
        self.device_list.addItem("Device 1 (Disconnected)")
        self.device_list.addItem("Device 2 (Disconnected)")
    
    def update_device_status(self, device_index, connected):
        """
        Update the connection status of a device.
        
        Args:
            device_index (int): Index of the device (0-based)
            connected (bool): True if connected, False if disconnected
        """
        if 0 <= device_index < self.device_list.count():
            item = self.device_list.item(device_index)
            status = "Connected" if connected else "Disconnected"
            item.setText(f"Device {device_index + 1} ({status})")
    
    def update_all_devices_status(self, connected):
        """
        Update the connection status of all devices.
        
        Args:
            connected (bool): True if connected, False if disconnected
        """
        for i in range(self.device_list.count()):
            self.update_device_status(i, connected)
    
    def get_device_count(self):
        """
        Get the number of devices in the list.
        
        Returns:
            int: Number of devices
        """
        return self.device_list.count()
    
    def add_device(self, device_name, connected=False):
        """
        Add a new device to the list.
        
        Args:
            device_name (str): Name of the device
            connected (bool): Initial connection status
        """
        status = "Connected" if connected else "Disconnected"
        self.device_list.addItem(f"{device_name} ({status})")
    
    def remove_device(self, device_index):
        """
        Remove a device from the list.
        
        Args:
            device_index (int): Index of the device to remove (0-based)
        """
        if 0 <= device_index < self.device_list.count():
            self.device_list.takeItem(device_index)
    
    def clear_devices(self):
        """Clear all devices from the list."""
        self.device_list.clear()
