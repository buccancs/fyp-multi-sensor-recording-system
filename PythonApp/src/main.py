#!/usr/bin/env python3
"""
Main Application Entry Point for Multi-Sensor Recording System Controller

This is the startup script with enhanced PsychoPy-inspired UI design.
It creates a QApplication instance, instantiates the Enhanced Main Window, and starts the PyQt event loop.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
Enhancement: PsychoPy-Inspired UI as Default Interface
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

from gui.enhanced_ui_main_window import EnhancedMainWindow

# Get logger for this module
logger = get_logger(__name__)


def check_display_availability():
    """Check if a display server is available for GUI applications."""
    display = os.environ.get('DISPLAY')
    if not display:
        logger.warning("No DISPLAY environment variable set")
        return False
    return True


def main():
    """Main application entry point with enhanced PsychoPy-inspired UI."""
    logger.info("=== Multi-Sensor Recording System Controller Starting (Enhanced UI) ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PyQt5 available, Qt version: {qVersion()}")
    
    # Check for headless environment
    headless_mode = os.environ.get('MSR_HEADLESS', 'false').lower() == 'true'
    if headless_mode:
        logger.info("Running in headless mode (MSR_HEADLESS=true)")
        logger.warning("GUI will not be displayed in headless mode")
    
    try:
        # Check display availability first
        if not check_display_availability():
            logger.warning("No display server detected. GUI might not work properly.")
            logger.info("To run with virtual display, use: xvfb-run -a python main.py")
            logger.info("To run in headless mode, set: export MSR_HEADLESS=true")
        
        # Enable high DPI scaling for better display on high-resolution screens
        # These must be set before creating QApplication
        logger.debug("Configuring high DPI scaling")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Configure platform plugin for headless environments
        if headless_mode or not check_display_availability():
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            logger.info("Using offscreen Qt platform for headless operation")

        # Create QApplication instance
        logger.debug("Creating QApplication instance")
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("Multi-Sensor Recording System Controller - Enhanced")
        app.setApplicationVersion("3.1.1")
        app.setOrganizationName("Multi-Sensor Recording System Team")
        
        # Set modern application style
        app.setStyle("Fusion")
        logger.info("Application properties configured with enhanced UI")

        # Create and show the enhanced main window
        logger.debug("Creating Enhanced MainWindow instance")
        main_window = EnhancedMainWindow()
        logger.info("Enhanced MainWindow created successfully")

        if not headless_mode:
            logger.debug("Showing main window")
            main_window.show()
            logger.info("Enhanced main window displayed")
        else:
            logger.info("Running in headless mode - window not displayed")

        # Start the PyQt event loop
        logger.info("Starting PyQt event loop")
        exit_code = app.exec_()
        logger.info(f"Application exiting with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        # Provide helpful error messages for common issues
        error_msg = str(e)
        if "could not connect to display" in error_msg.lower():
            logger.error("Display connection error - running in headless environment")
            logger.error("Solutions:")
            logger.error("1. Use virtual display: xvfb-run -a python main.py")
            logger.error("2. Set headless mode: export MSR_HEADLESS=true")
            logger.error("3. Enable X11 forwarding if using SSH")
        elif "qt platform plugin" in error_msg.lower():
            logger.error("Qt platform plugin error - GUI initialization failed")
            logger.error("Solutions:")
            logger.error("1. Install required Qt packages: sudo apt-get install qt5-default")
            logger.error("2. Use virtual display: xvfb-run -a python main.py")
            logger.error("3. Set QT_QPA_PLATFORM=offscreen for headless mode")
        else:
            logger.error(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Application started from command line")
    main()
