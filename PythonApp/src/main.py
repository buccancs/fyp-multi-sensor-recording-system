#!/usr/bin/env python3
"""
Main Application Entry Point for Multi-Sensor Recording System Controller

This is the startup script for Milestone 3.1: PyQt GUI Scaffolding and Application Framework.
It creates a QApplication instance, instantiates the Main Window, and starts the PyQt event loop.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Enable high DPI scaling for better display on high-resolution screens
    # These must be set before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Multi-Sensor Recording System Controller")
    app.setApplicationVersion("3.1.0")
    app.setOrganizationName("Multi-Sensor Recording System Team")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the PyQt event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
