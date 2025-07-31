#!/usr/bin/env python3
"""
Main Application Entry Point for Multi-Sensor Recording System Controller

This is the startup script for Milestone 3.1: PyQt GUI Scaffolding and Application Framework.
It creates a QApplication instance, instantiates the Main Window, and starts the PyQt event loop.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework
"""

import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize logging before importing other modules
from utils.logging_config import get_logger, AppLogger

# Configure logging level based on environment
log_level = os.environ.get('MSR_LOG_LEVEL', 'INFO')
AppLogger.set_level(log_level)

from gui.dual_webcam_main_window import DualWebcamMainWindow

# Get logger for this module
logger = get_logger(__name__)


def main():
    """Main application entry point."""
    logger.info("=== Multi-Sensor Recording System Controller Starting ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PyQt5 available, Qt version: {Qt.qVersion()}")
    
    try:
        # Enable high DPI scaling for better display on high-resolution screens
        # These must be set before creating QApplication
        logger.debug("Configuring high DPI scaling")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Create QApplication instance
        logger.debug("Creating QApplication instance")
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("Multi-Sensor Recording System Controller")
        app.setApplicationVersion("3.1.0")
        app.setOrganizationName("Multi-Sensor Recording System Team")
        logger.info("Application properties configured")

        # Create and show the main window
        logger.debug("Creating DualWebcamMainWindow instance")
        main_window = DualWebcamMainWindow()
        logger.info("DualWebcamMainWindow created successfully")
        
        logger.debug("Showing main window")
        main_window.show()
        logger.info("Main window displayed")

        # Start the PyQt event loop
        logger.info("Starting PyQt event loop")
        exit_code = app.exec_()
        logger.info(f"Application exiting with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Application started from command line")
    main()
