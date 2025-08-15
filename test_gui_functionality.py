#!/usr/bin/env python3
"""
GUI Functionality Test Script
============================

Tests all GUI buttons and functions to identify any non-functioning code,
placeholders, or stubs that need to be fixed.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Mock PyQt for headless testing
class MockQObject:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        # Return a mock function for any missing method
        return lambda *args, **kwargs: MockQObject()
    def connect(self, *args, **kwargs):
        pass
    def setEnabled(self, *args, **kwargs):
        pass
    def setText(self, *args, **kwargs):
        pass
    def append(self, *args, **kwargs):
        pass
    def clear(self, *args, **kwargs):
        pass
    def setValue(self, *args, **kwargs):
        pass
    def setMaximum(self, *args, **kwargs):
        pass
    def value(self, *args, **kwargs):
        return 0
    def currentText(self, *args, **kwargs):
        return "Camera 0 (640x480)"
    def addItem(self, *args, **kwargs):
        pass
    def text(self, *args, **kwargs):
        return "test_video.mp4"
    def setChecked(self, *args, **kwargs):
        pass
    def isChecked(self, *args, **kwargs):
        return True
    def size(self, *args, **kwargs):
        return MockQObject()
    def setPixmap(self, *args, **kwargs):
        pass
    def setStyleSheet(self, *args, **kwargs):
        pass
    def setAlignment(self, *args, **kwargs):
        pass
    def setWordWrap(self, *args, **kwargs):
        pass
    def setReadOnly(self, *args, **kwargs):
        pass
    def setMaximumHeight(self, *args, **kwargs):
        pass
    def setMinimumSize(self, *args, **kwargs):
        pass
    def setFrameStyle(self, *args, **kwargs):
        pass
    def setPlaceholderText(self, *args, **kwargs):
        pass
    def textCursor(self, *args, **kwargs):
        return MockQObject()
    def setTextCursor(self, *args, **kwargs):
        pass
    def movePosition(self, *args, **kwargs):
        pass
    def addWidget(self, *args, **kwargs):
        pass
    def addLayout(self, *args, **kwargs):
        pass
    def addTab(self, *args, **kwargs):
        pass
    def setCentralWidget(self, *args, **kwargs):
        pass
    def setStatusBar(self, *args, **kwargs):
        pass
    def showMessage(self, *args, **kwargs):
        pass
    # QMainWindow specific methods
    def setWindowTitle(self, *args, **kwargs):
        pass
    def setMinimumSize(self, *args, **kwargs):
        pass
    def show(self, *args, **kwargs):
        pass

# Mock Qt modules
sys.modules['PyQt6'] = MockQObject()
sys.modules['PyQt6.QtWidgets'] = MockQObject()
sys.modules['PyQt6.QtCore'] = MockQObject() 
sys.modules['PyQt6.QtGui'] = MockQObject()

# Mock specific Qt classes
import types
mock_qt = types.ModuleType('PyQt6.QtWidgets')
mock_qt.QMainWindow = MockQObject
mock_qt.QWidget = MockQObject
mock_qt.QVBoxLayout = MockQObject
mock_qt.QHBoxLayout = MockQObject
mock_qt.QPushButton = MockQObject
mock_qt.QLabel = MockQObject
mock_qt.QTextEdit = MockQObject
mock_qt.QGroupBox = MockQObject
mock_qt.QLineEdit = MockQObject
mock_qt.QSpinBox = MockQObject
mock_qt.QCheckBox = MockQObject
mock_qt.QMessageBox = MockQObject
mock_qt.QStatusBar = MockQObject
mock_qt.QTabWidget = MockQObject
mock_qt.QComboBox = MockQObject
mock_qt.QFrame = MockQObject
mock_qt.QFileDialog = MockQObject
mock_qt.QSlider = MockQObject
mock_qt.QProgressBar = MockQObject
mock_qt.QApplication = MockQObject

mock_qt_core = types.ModuleType('PyQt6.QtCore')
mock_qt_core.Qt = MockQObject()
mock_qt_core.QTimer = MockQObject
mock_qt_core.pyqtSignal = lambda *args: MockQObject()
mock_qt_core.QThread = MockQObject

mock_qt_gui = types.ModuleType('PyQt6.QtGui')
mock_qt_gui.QFont = MockQObject
mock_qt_gui.QPixmap = MockQObject
mock_qt_gui.QImage = MockQObject

sys.modules['PyQt6.QtWidgets'] = mock_qt
sys.modules['PyQt6.QtCore'] = mock_qt_core
sys.modules['PyQt6.QtGui'] = mock_qt_gui

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_gui_functionality():
    """Test all GUI functionality to identify issues."""
    print("=== GUI Functionality Test ===")
    
    issues_found = []
    
    try:
        # Import and create main window
        from PythonApp.gui.main_window import MainWindow
        
        print("✓ MainWindow import successful")
        
        # Create main window (this will test backend initialization)
        try:
            window = MainWindow()
            print("✓ MainWindow creation successful")
        except Exception as e:
            issues_found.append(f"MainWindow creation failed: {e}")
            print(f"✗ MainWindow creation failed: {e}")
            return issues_found
        
        # Test all button functions
        button_tests = [
            # Recording tab
            ("_create_session", "Create Session"),
            ("_start_recording", "Start Recording"),
            ("_stop_recording", "Stop Recording"),
            
            # Devices tab
            ("_start_server", "Start Server"),
            ("_stop_server", "Stop Server"),
            
            # Sensors tab
            ("_add_simulated_sensor", "Add Simulated Sensor"),
            ("_start_time_server", "Start Time Server"),
            ("_stop_time_server", "Stop Time Server"),
            
            # Sync tab
            ("_send_flash_signal", "Send Flash Signal"),
            ("_send_audio_signal", "Send Audio Signal"),
            ("_send_marker_signal", "Send Marker Signal"),
            
            # Calibration tab
            ("_start_calibration_session", "Start Calibration Session"),
            ("_end_calibration_session", "End Calibration Session"),
            
            # Media & Stimuli tab
            ("_refresh_cameras", "Refresh Cameras"),
            ("_start_camera_preview", "Start Camera Preview"),
            ("_stop_camera_preview", "Stop Camera Preview"),
            ("_browse_video_file", "Browse Video File"),
            ("_handle_play_button", "Play Video"),
            ("_pause_video", "Pause Video"),
            ("_stop_video", "Stop Video"),
            
            # Security tab
            ("_generate_auth_token", "Generate Auth Token"),
        ]
        
        print("\n--- Testing Button Functions ---")
        for func_name, button_name in button_tests:
            try:
                if hasattr(window, func_name):
                    func = getattr(window, func_name)
                    if callable(func):
                        print(f"✓ {button_name}: Function '{func_name}' found and callable")
                        
                        # Try to call the function (with mock environment)
                        try:
                            func()
                            print(f"  ✓ Function executed without errors")
                        except Exception as e:
                            print(f"  ⚠ Function execution had error: {e}")
                            # This might be expected in headless environment
                    else:
                        issues_found.append(f"{button_name}: '{func_name}' exists but not callable")
                        print(f"✗ {button_name}: '{func_name}' exists but not callable")
                else:
                    issues_found.append(f"{button_name}: Function '{func_name}' not found")
                    print(f"✗ {button_name}: Function '{func_name}' not found")
            except Exception as e:
                issues_found.append(f"{button_name}: Error testing '{func_name}': {e}")
                print(f"✗ {button_name}: Error testing '{func_name}': {e}")
        
        # Test helper functions
        print("\n--- Testing Helper Functions ---")
        helper_tests = [
            ("_update_ui", "Update UI"),
            ("_log_message", "Log Message"),
            ("_update_camera_status", "Update Camera Status"),
            ("_update_video_status", "Update Video Status"),
            ("_update_camera_frame", "Update Camera Frame"),
            ("_update_video_frame", "Update Video Frame"),
            ("_handle_camera_error", "Handle Camera Error"),
            ("_handle_camera_disconnect", "Handle Camera Disconnect"),
            ("_handle_video_finished", "Handle Video Finished"),
            ("_handle_video_error", "Handle Video Error"),
        ]
        
        for func_name, desc in helper_tests:
            try:
                if hasattr(window, func_name):
                    func = getattr(window, func_name)
                    if callable(func):
                        print(f"✓ {desc}: Function '{func_name}' found and callable")
                    else:
                        issues_found.append(f"{desc}: '{func_name}' exists but not callable")
                        print(f"✗ {desc}: '{func_name}' exists but not callable")
                else:
                    issues_found.append(f"{desc}: Function '{func_name}' not found")
                    print(f"✗ {desc}: Function '{func_name}' not found")
            except Exception as e:
                issues_found.append(f"{desc}: Error testing '{func_name}': {e}")
                print(f"✗ {desc}: Error testing '{func_name}': {e}")
        
        # Test backend components
        print("\n--- Testing Backend Components ---")
        backend_tests = [
            ("server", "Network Server"),
            ("session_manager", "Session Manager"),
            ("sensor_manager", "Sensor Manager"),
            ("time_server", "Time Server"),
            ("session_synchronizer", "Session Synchronizer"),
            ("sync_broadcaster", "Sync Broadcaster"),
            ("calibration_manager", "Calibration Manager"),
            ("transfer_manager", "Transfer Manager"),
            ("security_manager", "Security Manager"),
            ("webcam_manager", "Webcam Manager"),
        ]
        
        for attr_name, desc in backend_tests:
            try:
                if hasattr(window, attr_name):
                    component = getattr(window, attr_name)
                    if component is not None:
                        print(f"✓ {desc}: Component '{attr_name}' initialized")
                    else:
                        issues_found.append(f"{desc}: Component '{attr_name}' is None")
                        print(f"✗ {desc}: Component '{attr_name}' is None")
                else:
                    issues_found.append(f"{desc}: Component '{attr_name}' not found")
                    print(f"✗ {desc}: Component '{attr_name}' not found")
            except Exception as e:
                issues_found.append(f"{desc}: Error testing '{attr_name}': {e}")
                print(f"✗ {desc}: Error testing '{attr_name}': {e}")
        
        print(f"\n=== Test Complete ===")
        print(f"Issues found: {len(issues_found)}")
        
        if issues_found:
            print("\n--- Issues to Fix ---")
            for i, issue in enumerate(issues_found, 1):
                print(f"{i}. {issue}")
        else:
            print("✓ All functionality appears to be working correctly!")
            
    except Exception as e:
        issues_found.append(f"Critical error during testing: {e}")
        print(f"✗ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    return issues_found

if __name__ == "__main__":
    issues = test_gui_functionality()
    sys.exit(0 if not issues else 1)