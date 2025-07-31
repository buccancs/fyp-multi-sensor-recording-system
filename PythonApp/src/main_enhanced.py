#!/usr/bin/env python3
"""
Enhanced Main Application Entry Point with PsychoPy-Inspired UI
for Multi-Sensor Recording System Controller

This is the enhanced startup script that uses the new PsychoPy-inspired interface
with modern design, better visual hierarchy, and improved stimulus presentation features.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
Enhancement: PsychoPy-Inspired UI Design
"""

import os
import sys
from PyQt5.QtCore import Qt, qVersion
from PyQt5.QtWidgets import QApplication

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize logging before importing other modules
from utils.logging_config import get_logger, AppLogger

# Configure logging level based on environment
log_level = os.environ.get('MSR_LOG_LEVEL', 'INFO')
AppLogger.set_level(log_level)

# Import the enhanced PsychoPy-inspired window
from gui.psychopy_inspired_window import PsychoPyInspiredMainWindow

# Get logger for this module
logger = get_logger(__name__)


def main():
    """Enhanced main application entry point."""
    logger.info("=== Enhanced Multi-Sensor Recording System Controller Starting ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PyQt5 available, Qt version: {qVersion()}")
    
    try:
        # Enable high DPI scaling for better display on high-resolution screens
        logger.debug("Configuring high DPI scaling")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Create QApplication instance
        logger.debug("Creating QApplication instance")
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("Multi-Sensor Recording System Controller - Enhanced")
        app.setApplicationVersion("3.1.0-Enhanced")
        app.setOrganizationName("Multi-Sensor Recording System Team")
        logger.info("Enhanced application properties configured")

        # Set application-wide style
        app.setStyle("Fusion")  # Modern look across platforms
        
        # Create and show the enhanced main window
        logger.debug("Creating PsychoPy-inspired MainWindow instance")
        main_window = PsychoPyInspiredMainWindow()
        logger.info("Enhanced MainWindow created successfully")
        
        logger.debug("Showing enhanced main window")
        main_window.show()
        logger.info("Enhanced main window displayed")

        # Start the PyQt event loop
        logger.info("Starting PyQt event loop")
        exit_code = app.exec_()
        logger.info(f"Enhanced application exiting with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal error during enhanced application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Enhanced application started from command line")
    main()