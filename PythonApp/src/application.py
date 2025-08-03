"""application class for multi-sensor recording system"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject

# Import modern logging system
from utils.logging_config import get_logger

# Import backend services
from network.device_server import JsonSocketServer
from session.session_manager import SessionManager
from session.session_logger import get_session_logger
from webcam.webcam_capture import WebcamCapture
from gui.stimulus_controller import StimulusController
from gui.main_controller import MainController
from gui.main_window import MainWindow
from gui.simplified_main_window import SimplifiedMainWindow


class Application(QObject):
    """dependency injection container for backend services"""
    
    def __init__(self, use_simplified_ui=True):
        super().__init__()
        self.logger = get_logger(__name__)
        self.use_simplified_ui = use_simplified_ui
        self.session_manager = None
        self.json_server = None
        self.webcam_capture = None
        self.stimulus_controller = None
        self.main_controller = None
        self.main_window = None
        self._create_services()
        self.logger.info("application initialized")
    
    def _create_services(self):
        """create backend services"""
        try:
            self.session_manager = SessionManager()
            self.json_server = JsonSocketServer(session_manager=self.session_manager)
            self.webcam_capture = WebcamCapture()
            self.stimulus_controller = None
            if not self.use_simplified_ui:
                self.main_controller = MainController()
        except Exception as e:
            self.logger.error(f"failed to create services: {e}")
            raise
    
    def create_main_window(self):
        """create main window and complete dependency injection"""
        try:
            if self.use_simplified_ui:
                self.main_window = SimplifiedMainWindow()
                self.logger.info("Created simplified main window")
            else:
                self.main_window = MainWindow()
                self.stimulus_controller = StimulusController(self.main_window)
                self.main_controller.inject_dependencies(
                    session_manager=self.session_manager,
                    json_server=self.json_server,
                    webcam_capture=self.webcam_capture,
                    stimulus_controller=self.stimulus_controller
                )
                self.main_window.set_controller(self.main_controller)
                self.logger.info("Created traditional main window")
            return self.main_window
        except Exception as e:
            self.logger.error(f"failed to create main window: {e}")
            raise
    
    def run(self):
        """run the application"""
        try:
            main_window = self.create_main_window()
            main_window.show()
            self.logger.info("application started")
            return main_window
        except Exception as e:
            self.logger.error(f"failed to run application: {e}")
            raise
    
    def cleanup(self):
        """clean up resources"""
        try:
            if self.main_controller:
                self.main_controller.cleanup()
            if self.json_server:
                self.json_server.cleanup()
            if self.webcam_capture:
                self.webcam_capture.cleanup()
            self.logger.info("cleanup completed")
        except Exception as e:
            self.logger.error(f"cleanup error: {e}")


def main():
    """application entry point"""
    # Modern logging is auto-initialized in logging_config.py
    logger = get_logger(__name__)
    
    qt_app = QApplication(sys.argv)
    try:
        # Use simplified UI by default for cleaner navigation
        app = Application(use_simplified_ui=True)
        main_window = app.run()
        qt_app.aboutToQuit.connect(app.cleanup)
        sys.exit(qt_app.exec_())
    except Exception as e:
        logger.error(f"application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()