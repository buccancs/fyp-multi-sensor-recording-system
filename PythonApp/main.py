#!/usr/bin/env python3
"""
Multi-Sensor Recording System - Main Application
===============================================

Main entry point for the desktop controller application.
Provides a simple, clean interface for multi-sensor recording coordination.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are available."""
    missing = []
    
    try:
        import PyQt6  # noqa
    except ImportError:
        try:
            import PyQt5  # noqa
        except ImportError:
            missing.append("PyQt6 or PyQt5")
    
    try:
        import cv2  # noqa
    except ImportError:
        missing.append("opencv-python")
    
    try:
        import numpy  # noqa
    except ImportError:
        missing.append("numpy")
    
    if missing:
        logger.error(f"Missing required dependencies: {', '.join(missing)}")
        logger.error("Please install with: pip install PyQt6 opencv-python numpy")
        return False
    
    return True


def main():
    """Main application entry point."""
    logger.info("=== Multi-Sensor Recording System Controller Starting ===")
    logger.info(f"Python version: {sys.version}")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Cannot start application due to missing dependencies")
        sys.exit(1)
    
    try:
        # Import Qt after dependency check
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            logger.info("Using PyQt6")
        except ImportError:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt
            logger.info("Using PyQt5")
        
        from PythonApp.gui.main_window import MainWindow
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Multi-Sensor Recording System")
        
        # Enable high DPI scaling
        try:
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # PyQt6 handles this automatically
            pass
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Application started successfully")
        
        # Start Qt event loop
        exit_code = app.exec()
        logger.info(f"Application exiting with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()