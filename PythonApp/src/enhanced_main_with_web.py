#!/usr/bin/env python3
"""
Enhanced Main Application with Web Dashboard Integration

This demonstrates how to integrate the new web-based dashboard with the existing
PyQt5 desktop application. This file shows the minimal changes needed to add
web UI capabilities to the existing application.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import os
import sys
import webbrowser
from PyQt5.QtCore import Qt, qVersion, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize logging before importing other modules
try:
    from utils.logging_config import get_logger, AppLogger
    
    # Configure logging level based on environment
    log_level = os.environ.get('MSR_LOG_LEVEL', 'INFO')
    AppLogger.set_level(log_level)
    
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Import existing GUI components
try:
    from gui.enhanced_ui_main_window import EnhancedMainWindow
except ImportError:
    logger.error("Enhanced UI main window not available, falling back to standard")
    try:
        from gui.main_window import MainWindow as EnhancedMainWindow
    except ImportError:
        logger.error("No GUI components available")
        EnhancedMainWindow = None

# Import web dashboard integration
try:
    from web_ui.integration import WebDashboardIntegration
    WEB_UI_AVAILABLE = True
except ImportError:
    logger.warning("Web UI components not available")
    WebDashboardIntegration = None
    WEB_UI_AVAILABLE = False


class EnhancedApplicationWithWebUI:
    """
    Enhanced application that combines the existing PyQt5 desktop UI with
    the new web-based dashboard capabilities.
    """
    
    def __init__(self):
        """Initialize the enhanced application."""
        self.app = None
        self.main_window = None
        self.web_integration = None
        
        logger.info("Enhanced Application with Web UI initialized")
    
    def setup_application(self):
        """Setup the PyQt5 application."""
        logger.info("=== Multi-Sensor Recording System Controller Starting (Enhanced UI + Web Dashboard) ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"PyQt5 available, Qt version: {qVersion()}")
        
        # Enable high DPI scaling for better display on high-resolution screens
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create QApplication instance
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Set application properties
        self.app.setApplicationName("Multi-Sensor Recording System")
        self.app.setApplicationVersion("2.0")
        self.app.setOrganizationName("Multi-Sensor Recording Team")
        
        logger.info("QApplication created and configured")
    
    def setup_desktop_ui(self):
        """Setup the desktop UI components."""
        if EnhancedMainWindow is None:
            logger.error("No desktop UI components available")
            return False
        
        try:
            # Create the enhanced main window
            self.main_window = EnhancedMainWindow()
            self.main_window.setWindowTitle("Multi-Sensor Recording System - Enhanced UI + Web Dashboard")
            
            # Add web dashboard integration if available
            if WEB_UI_AVAILABLE:
                self._add_web_dashboard_integration()
            
            logger.info("Desktop UI components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize desktop UI: {e}")
            return False
    
    def setup_web_dashboard(self):
        """Setup the web dashboard integration."""
        if not WEB_UI_AVAILABLE:
            logger.warning("Web UI not available, skipping web dashboard setup")
            return False
        
        try:
            # Create web dashboard integration
            self.web_integration = WebDashboardIntegration(
                enable_web_ui=True,
                web_port=5000
            )
            
            # Start the web dashboard
            if self.web_integration.start_web_dashboard():
                logger.info("Web dashboard started successfully")
                
                # Connect desktop application events to web dashboard updates
                self._connect_web_integration()
                
                return True
            else:
                logger.error("Failed to start web dashboard")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up web dashboard: {e}")
            return False
    
    def _add_web_dashboard_integration(self):
        """Add web dashboard controls to the desktop UI."""
        if not hasattr(self.main_window, 'menuBar'):
            return
        
        try:
            # Add a "Web Dashboard" menu
            web_menu = self.main_window.menuBar().addMenu("Web Dashboard")
            
            # Action to open web dashboard in browser
            open_dashboard_action = web_menu.addAction("Open in Browser")
            open_dashboard_action.setShortcut("Ctrl+W")
            open_dashboard_action.triggered.connect(self._open_web_dashboard)
            
            # Action to show web dashboard URL
            show_url_action = web_menu.addAction("Show Dashboard URL")
            show_url_action.triggered.connect(self._show_dashboard_url)
            
            web_menu.addSeparator()
            
            # Action to enable/disable web dashboard
            toggle_web_action = web_menu.addAction("Enable Web Dashboard")
            toggle_web_action.setCheckable(True)
            toggle_web_action.setChecked(True)
            toggle_web_action.triggered.connect(self._toggle_web_dashboard)
            
            logger.info("Web dashboard menu items added to desktop UI")
            
        except Exception as e:
            logger.error(f"Failed to add web dashboard integration to UI: {e}")
    
    def _connect_web_integration(self):
        """Connect desktop application events to web dashboard updates."""
        if not self.web_integration:
            return
        
        # Example: Update web dashboard when desktop app status changes
        # In a real implementation, you would connect to actual desktop app signals
        
        # Start a timer to simulate status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_web_dashboard_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
        logger.info("Web dashboard integration connected to desktop application")
    
    def _update_web_dashboard_status(self):
        """Update web dashboard with current desktop application status."""
        if not self.web_integration:
            return
        
        try:
            # Example status update - in real implementation, get actual status
            self.web_integration.update_device_status('pc_controller', 'desktop_app', {
                'status': 'running',
                'cpu_usage': 45,
                'memory_usage': 60,
                'ui_active': True,
                'last_update': 'Now'
            })
            
        except Exception as e:
            logger.error(f"Failed to update web dashboard status: {e}")
    
    def _open_web_dashboard(self):
        """Open the web dashboard in the default browser."""
        if not self.web_integration:
            QMessageBox.warning(self.main_window, "Web Dashboard", 
                              "Web dashboard is not available")
            return
        
        dashboard_url = self.web_integration.get_web_dashboard_url()
        if dashboard_url:
            webbrowser.open(dashboard_url)
            logger.info(f"Opened web dashboard in browser: {dashboard_url}")
        else:
            QMessageBox.warning(self.main_window, "Web Dashboard", 
                              "Web dashboard is not running")
    
    def _show_dashboard_url(self):
        """Show the web dashboard URL in a dialog."""
        if not self.web_integration:
            QMessageBox.information(self.main_window, "Web Dashboard", 
                                  "Web dashboard is not available")
            return
        
        dashboard_url = self.web_integration.get_web_dashboard_url()
        if dashboard_url:
            QMessageBox.information(self.main_window, "Web Dashboard URL", 
                                  f"Access the web dashboard at:\n\n{dashboard_url}")
        else:
            QMessageBox.information(self.main_window, "Web Dashboard", 
                                  "Web dashboard is not running")
    
    def _toggle_web_dashboard(self, enabled):
        """Toggle the web dashboard on/off."""
        if not WEB_UI_AVAILABLE:
            QMessageBox.warning(self.main_window, "Web Dashboard", 
                              "Web dashboard components are not available")
            return
        
        if enabled:
            if not self.web_integration:
                self.setup_web_dashboard()
            elif not self.web_integration.is_running:
                self.web_integration.start_web_dashboard()
        else:
            if self.web_integration:
                self.web_integration.stop_web_dashboard()
    
    def run(self):
        """Run the enhanced application."""
        # Setup PyQt5 application
        self.setup_application()
        
        # Setup desktop UI
        if not self.setup_desktop_ui():
            logger.error("Failed to setup desktop UI")
            return 1
        
        # Setup web dashboard (optional)
        web_success = self.setup_web_dashboard()
        if web_success:
            logger.info("Application started with both desktop and web interfaces")
        else:
            logger.info("Application started with desktop interface only")
        
        # Show the main window
        self.main_window.show()
        logger.info("Main window displayed")
        
        # Show startup message with web dashboard info
        if web_success:
            dashboard_url = self.web_integration.get_web_dashboard_url()
            QMessageBox.information(
                self.main_window,
                "Multi-Sensor Recording System",
                f"Application started successfully!\n\n"
                f"Desktop UI: Running\n"
                f"Web Dashboard: {dashboard_url}\n\n"
                f"You can access the web interface from any device on your network."
            )
        
        # Start the PyQt event loop
        logger.info("Starting PyQt event loop")
        return self.app.exec_()
    
    def cleanup(self):
        """Clean up resources before shutdown."""
        logger.info("Cleaning up application resources...")
        
        if self.web_integration:
            self.web_integration.stop_web_dashboard()
            logger.info("Web dashboard stopped")
        
        logger.info("Application cleanup completed")


def main():
    """Main application entry point."""
    app = EnhancedApplicationWithWebUI()
    
    try:
        return app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    finally:
        app.cleanup()


if __name__ == '__main__':
    sys.exit(main())