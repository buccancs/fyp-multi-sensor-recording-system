"""
Application class for the Multi-Sensor Recording System.

This module implements the Application class that serves as a dependency injection
container and application entry point. It creates and wires all backend services
and provides them to the MainController.

Created: 2025-07-30
Author: Junie (Architectural Refactoring)
"""

import logging
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject

# Import backend services
from network.device_server import JsonSocketServer
from session.session_manager import SessionManager
from session.session_logger import get_session_logger
from webcam.webcam_capture import WebcamCapture
from gui.stimulus_controller import StimulusController
from gui.main_controller import MainController
from gui.main_window import MainWindow


class Application(QObject):
    """
    Main Application class that serves as a dependency injection container.
    
    This class is responsible for:
    - Creating and configuring all backend services
    - Wiring dependencies between services
    - Providing services to the MainController
    - Managing application lifecycle
    """
    
    def __init__(self):
        """Initialize the application and create all services."""
        super().__init__()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Backend services
        self.session_manager = None
        self.json_server = None
        self.webcam_capture = None
        self.stimulus_controller = None
        self.main_controller = None
        self.main_window = None
        
        # Create services
        self._create_services()
        
        self.logger.info("Application initialized successfully")
    
    def _create_services(self):
        """Create and configure all backend services."""
        try:
            # Create session manager first (needed by other services)
            self.session_manager = SessionManager()
            self.logger.info("SessionManager created")
            
            # Create JSON server with session manager integration
            self.json_server = JsonSocketServer(session_manager=self.session_manager)
            self.logger.info("JsonSocketServer created")
            
            # Create webcam capture
            self.webcam_capture = WebcamCapture()
            self.logger.info("WebcamCapture created")
            
            # Create stimulus controller (will be passed the main window later)
            # Note: StimulusController needs the main window, so we'll create it after
            self.stimulus_controller = None
            
            # Create main controller
            self.main_controller = MainController()
            self.logger.info("MainController created")
            
        except Exception as e:
            self.logger.error(f"Failed to create services: {e}")
            raise
    
    def create_main_window(self):
        """Create the main window and complete the dependency injection."""
        try:
            # Create main window
            self.main_window = MainWindow()
            self.logger.info("MainWindow created")
            
            # Now create stimulus controller with main window reference
            self.stimulus_controller = StimulusController(self.main_window)
            self.logger.info("StimulusController created")
            
            # Inject dependencies into main controller
            self.main_controller.inject_dependencies(
                session_manager=self.session_manager,
                json_server=self.json_server,
                webcam_capture=self.webcam_capture,
                stimulus_controller=self.stimulus_controller
            )
            self.logger.info("Dependencies injected into MainController")
            
            # Inject main controller into main window
            self.main_window.set_controller(self.main_controller)
            self.logger.info("MainController injected into MainWindow")
            
            return self.main_window
            
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}")
            raise
    
    def run(self):
        """Run the application."""
        try:
            # Create and show main window
            main_window = self.create_main_window()
            main_window.show()
            
            self.logger.info("Application started successfully")
            return main_window
            
        except Exception as e:
            self.logger.error(f"Failed to run application: {e}")
            raise
    
    def cleanup(self):
        """Clean up application resources."""
        try:
            if self.main_controller:
                self.main_controller.cleanup()
            
            if self.json_server:
                self.json_server.cleanup()
            
            if self.webcam_capture:
                self.webcam_capture.cleanup()
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during application cleanup: {e}")


def main():
    """Main entry point for the application."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Qt application
    qt_app = QApplication(sys.argv)
    
    try:
        # Create and run our application
        app = Application()
        main_window = app.run()
        
        # Set up cleanup on exit
        qt_app.aboutToQuit.connect(app.cleanup)
        
        # Run Qt event loop
        sys.exit(qt_app.exec_())
        
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()