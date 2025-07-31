#!/usr/bin/env python3
"""
Enhanced Main Application Entry Point for Multi-Sensor Recording System Controller

This is an enhanced startup script that uses the new PsychoPy-inspired UI design.
It provides a cleaner, more modern interface while maintaining all core functionality.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
Enhancement: PsychoPy-Inspired UI Integration
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


def main():
    """Enhanced application entry point with PsychoPy-inspired UI."""
    logger.info("=== Multi-Sensor Recording System Controller Starting (Enhanced UI) ===")
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
        
        # Set modern application style
        app.setStyle("Fusion")
        logger.debug("Applied Fusion style for modern appearance")

        # Create and show the enhanced main window
        logger.debug("Creating Enhanced Main Window")
        main_window = EnhancedMainWindow()
        
        # Show the window
        logger.debug("Showing main window")
        main_window.show()
        
        logger.info("Enhanced UI application startup complete - entering event loop")
        
        # Start the event loop
        exit_code = app.exec_()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Failed to start enhanced application: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)