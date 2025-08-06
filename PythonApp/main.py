import os
import sys

from PyQt5.QtCore import Qt, qVersion
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from .utils.logging_config import AppLogger, get_logger

log_level = os.environ.get("MSR_LOG_LEVEL", "INFO")
AppLogger.set_level(log_level)
from .gui.enhanced_ui_main_window import EnhancedMainWindow
from .production.runtime_security_checker import validate_runtime_security, SecurityValidationError

logger = get_logger(__name__)


def main():
    logger.info(
        "=== Multi-Sensor Recording System Controller Starting (Enhanced UI) ==="
    )
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PyQt5 available, Qt version: {qVersion()}")
    
    # Perform runtime security validation before starting application
    try:
        logger.info("🔒 Performing runtime security validation...")
        validate_runtime_security()
        logger.info("🔒 Runtime security validation completed successfully")
    except SecurityValidationError as e:
        logger.error(f"🔒 SECURITY VALIDATION FAILED: {e}")
        logger.error("🔒 Application startup aborted due to security issues")
        print(f"\n❌ SECURITY ERROR: {e}")
        print("🔒 Please fix security issues before running the application")
        sys.exit(1)
    except Exception as e:
        logger.warning(f"🔒 Security validation encountered an error: {e}")
        logger.warning("🔒 Continuing startup with security warning")
    
    try:
        logger.debug("Configuring high DPI scaling")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        logger.debug("Creating QApplication instance")
        app = QApplication(sys.argv)
        app.setApplicationName("Multi-Sensor Recording System Controller - Enhanced")
        app.setApplicationVersion("3.1.1")
        app.setOrganizationName("Multi-Sensor Recording System Team")
        app.setStyle("Fusion")
        logger.info("Application properties configured with enhanced UI")
        logger.debug("Creating Enhanced MainWindow instance")
        main_window = EnhancedMainWindow()
        logger.info("Enhanced MainWindow created successfully")
        logger.debug("Showing main window")
        main_window.show()
        logger.info("Enhanced main window displayed")
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
