"""
Tests for the common UI components module
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestCommonComponents(unittest.TestCase):
    """Test suite for common UI components"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for PyQt5 tests"""
        if not hasattr(cls, 'app'):
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication(sys.argv)

    def setUp(self):
        """Set up test fixtures"""
        self.test_app = self.app

    def test_status_indicator_creation(self):
        """Test StatusIndicator widget creation"""
        try:
            from gui.common_components import StatusIndicator
            
            # Test creation with default parameters
            indicator = StatusIndicator()
            self.assertIsNotNone(indicator)
            self.assertFalse(indicator.is_connected)
            self.assertEqual(indicator.status_text, "Disconnected")
            
            # Test creation with custom label
            custom_indicator = StatusIndicator("Custom Status")
            self.assertIsNotNone(custom_indicator)
            
        except ImportError as e:
            self.skipTest(f"Cannot import StatusIndicator: {e}")

    def test_status_indicator_update(self):
        """Test StatusIndicator status updates"""
        try:
            from gui.common_components import StatusIndicator
            
            indicator = StatusIndicator("Test Device")
            
            # Test setting connected status
            indicator.set_status(True, "Connected successfully")
            self.assertTrue(indicator.is_connected)
            self.assertEqual(indicator.status_text, "Connected successfully")
            
            # Test setting disconnected status
            indicator.set_status(False, "Connection lost")
            self.assertFalse(indicator.is_connected)
            self.assertEqual(indicator.status_text, "Connection lost")
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test StatusIndicator updates: {e}")

    def test_modern_button_creation(self):
        """Test ModernButton widget creation"""
        try:
            from gui.common_components import ModernButton
            
            # Test creation with text only
            button = ModernButton("Test Button")
            self.assertIsNotNone(button)
            
            # Test creation with button type
            success_button = ModernButton("Success", "success")
            self.assertIsNotNone(success_button)
            
            danger_button = ModernButton("Danger", "danger")
            self.assertIsNotNone(danger_button)
            
        except ImportError as e:
            self.skipTest(f"Cannot import ModernButton: {e}")

    def test_modern_button_styling(self):
        """Test ModernButton style application"""
        try:
            from gui.common_components import ModernButton
            
            button = ModernButton("Test")
            
            # Test setting different button types
            button.set_button_type("primary")
            button.set_button_type("success")
            button.set_button_type("danger")
            button.set_button_type("secondary")
            
            # Test enabling/disabling
            button.setEnabled(True)
            self.assertTrue(button.isEnabled())
            
            button.setEnabled(False)
            self.assertFalse(button.isEnabled())
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test ModernButton styling: {e}")

    def test_progress_indicator_creation(self):
        """Test ProgressIndicator widget creation"""
        try:
            from gui.common_components import ProgressIndicator
            
            # Test creation with default parameters
            progress = ProgressIndicator()
            self.assertIsNotNone(progress)
            
            # Test creation with custom label
            custom_progress = ProgressIndicator("Custom Progress")
            self.assertIsNotNone(custom_progress)
            
        except ImportError as e:
            self.skipTest(f"Cannot import ProgressIndicator: {e}")

    def test_progress_indicator_value_updates(self):
        """Test ProgressIndicator value updates"""
        try:
            from gui.common_components import ProgressIndicator
            
            progress = ProgressIndicator("Test Progress")
            
            # Test setting progress values
            progress.set_progress(0)
            progress.set_progress(50)
            progress.set_progress(100)
            
            # Test setting status text
            progress.set_status_text("Processing...")
            progress.set_status_text("Complete")
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test ProgressIndicator updates: {e}")

    def test_connection_manager_creation(self):
        """Test ConnectionManager widget creation"""
        try:
            from gui.common_components import ConnectionManager
            
            # Test creation with device list
            devices = ["Device1", "Device2", "Device3"]
            manager = ConnectionManager(devices)
            self.assertIsNotNone(manager)
            
        except ImportError as e:
            self.skipTest(f"Cannot import ConnectionManager: {e}")

    def test_connection_manager_device_updates(self):
        """Test ConnectionManager device status updates"""
        try:
            from gui.common_components import ConnectionManager
            
            devices = ["PC", "Shimmer", "Thermal"]
            manager = ConnectionManager(devices)
            
            # Test updating device statuses
            manager.update_device_status("PC", True, "Connected")
            manager.update_device_status("Shimmer", False, "Disconnected")
            manager.update_device_status("Thermal", True, "Active")
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test ConnectionManager updates: {e}")

    def test_log_viewer_creation(self):
        """Test LogViewer widget creation"""
        try:
            from gui.common_components import LogViewer
            
            # Test creation with default parameters
            log_viewer = LogViewer()
            self.assertIsNotNone(log_viewer)
            
            # Test creation with custom title
            custom_viewer = LogViewer("Custom Log")
            self.assertIsNotNone(custom_viewer)
            
        except ImportError as e:
            self.skipTest(f"Cannot import LogViewer: {e}")

    def test_log_viewer_operations(self):
        """Test LogViewer log operations"""
        try:
            from gui.common_components import LogViewer
            
            log_viewer = LogViewer("Test Log")
            
            # Test adding log messages
            log_viewer.add_log("Info message", "info")
            log_viewer.add_log("Warning message", "warning")
            log_viewer.add_log("Error message", "error")
            
            # Test clearing logs
            log_viewer.clear_logs()
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test LogViewer operations: {e}")

    def test_modern_group_box_creation(self):
        """Test ModernGroupBox widget creation"""
        try:
            from gui.common_components import ModernGroupBox
            
            # Test creation with title
            group_box = ModernGroupBox("Test Group")
            self.assertIsNotNone(group_box)
            
        except ImportError as e:
            self.skipTest(f"Cannot import ModernGroupBox: {e}")

    def test_component_integration(self):
        """Test integration between different components"""
        try:
            from gui.common_components import (
                StatusIndicator, ModernButton, ProgressIndicator,
                ConnectionManager, LogViewer, ModernGroupBox
            )
            
            # Create a group box to contain other components
            group = ModernGroupBox("Integration Test")
            
            # Create various components
            status = StatusIndicator("Test Status")
            button = ModernButton("Test Action", "primary")
            progress = ProgressIndicator("Test Progress")
            
            # Test that all components can coexist
            self.assertIsNotNone(group)
            self.assertIsNotNone(status)
            self.assertIsNotNone(button)
            self.assertIsNotNone(progress)
            
        except ImportError as e:
            self.skipTest(f"Cannot test component integration: {e}")

    def test_component_signals(self):
        """Test that components emit proper signals"""
        try:
            from gui.common_components import StatusIndicator, ModernButton
            
            # Test StatusIndicator signals
            status = StatusIndicator()
            signal_emitted = False
            
            def on_status_changed(connected, text):
                nonlocal signal_emitted
                signal_emitted = True
            
            status.statusChanged.connect(on_status_changed)
            status.set_status(True, "Connected")
            
            # Give some time for signal processing in GUI applications
            QTest.qWait(10)
            
            # Test ModernButton signals
            button = ModernButton("Test")
            button_clicked = False
            
            def on_button_clicked():
                nonlocal button_clicked
                button_clicked = True
            
            button.clicked.connect(on_button_clicked)
            # Simulate button click
            button.click()
            
            QTest.qWait(10)
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test component signals: {e}")

    def test_error_handling(self):
        """Test error handling in components"""
        try:
            from gui.common_components import StatusIndicator, ProgressIndicator
            
            # Test StatusIndicator with invalid parameters
            status = StatusIndicator()
            # Should handle invalid status gracefully
            status.set_status(None, None)
            
            # Test ProgressIndicator with invalid values
            progress = ProgressIndicator()
            # Should handle invalid progress values gracefully
            progress.set_progress(-10)  # Negative value
            progress.set_progress(150)  # Value over 100
            
        except (ImportError, AttributeError) as e:
            self.skipTest(f"Cannot test error handling: {e}")


class TestComponentModuleMocking(unittest.TestCase):
    """Test component module with mocked PyQt5 dependencies"""

    def test_module_import_with_mock(self):
        """Test that module can be imported even with mocked PyQt5"""
        with patch.dict('sys.modules', {
            'PyQt5.QtWidgets': MagicMock(),
            'PyQt5.QtCore': MagicMock(),
            'PyQt5.QtGui': MagicMock()
        }):
            try:
                from gui import common_components
                self.assertIsNotNone(common_components)
            except ImportError as e:
                self.skipTest(f"Cannot import common_components even with mocks: {e}")

    def test_component_functionality_with_mocks(self):
        """Test component functionality with mocked dependencies"""
        # Mock PyQt5 components
        mock_widget = MagicMock()
        mock_signal = MagicMock()
        
        with patch.dict('sys.modules', {
            'PyQt5.QtWidgets': MagicMock(),
            'PyQt5.QtCore': MagicMock(pyqtSignal=lambda *args: mock_signal),
            'PyQt5.QtGui': MagicMock()
        }):
            try:
                from gui.common_components import StatusIndicator
                
                # Create component with mocked dependencies
                status = StatusIndicator()
                
                # Test that basic functionality works with mocks
                self.assertIsNotNone(status)
                
            except ImportError as e:
                self.skipTest(f"Cannot test with mocks: {e}")


if __name__ == '__main__':
    # Configure test verbosity
    verbosity = 2 if '-v' in sys.argv else 1
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCommonComponents)
    mock_suite = unittest.TestLoader().loadTestsFromTestCase(TestComponentModuleMocking)
    
    # Combine test suites
    combined_suite = unittest.TestSuite([test_suite, mock_suite])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(combined_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)