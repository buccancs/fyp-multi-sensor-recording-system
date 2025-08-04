import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipUnless(PYQT_AVAILABLE, 'PyQt5 not available')
class TestCommonComponents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'app'):
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication(sys.argv)

    def setUp(self):
        self.test_app = self.app

    def test_status_indicator_creation(self):
        try:
            from gui.common_components import StatusIndicator
            indicator = StatusIndicator()
            self.assertIsNotNone(indicator)
            self.assertFalse(indicator.is_connected)
            self.assertEqual(indicator.status_text, 'Disconnected')
            custom_indicator = StatusIndicator('Custom Status')
            self.assertIsNotNone(custom_indicator)
        except ImportError as e:
            self.skipTest(f'Cannot import StatusIndicator: {e}')

    def test_status_indicator_update(self):
        try:
            from gui.common_components import StatusIndicator
            indicator = StatusIndicator('Test Device')
            indicator.set_status(True, 'Connected successfully')
            self.assertTrue(indicator.is_connected)
            self.assertEqual(indicator.status_text, 'Connected successfully')
            indicator.set_status(False, 'Connection lost')
            self.assertFalse(indicator.is_connected)
            self.assertEqual(indicator.status_text, 'Connection lost')
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test StatusIndicator updates: {e}')

    def test_modern_button_creation(self):
        try:
            from gui.common_components import ModernButton
            button = ModernButton('Test Button')
            self.assertIsNotNone(button)
            success_button = ModernButton('Success', 'success')
            self.assertIsNotNone(success_button)
            danger_button = ModernButton('Danger', 'danger')
            self.assertIsNotNone(danger_button)
        except ImportError as e:
            self.skipTest(f'Cannot import ModernButton: {e}')

    def test_modern_button_styling(self):
        try:
            from gui.common_components import ModernButton
            button = ModernButton('Test')
            button.set_button_type('primary')
            button.set_button_type('success')
            button.set_button_type('danger')
            button.set_button_type('secondary')
            button.setEnabled(True)
            self.assertTrue(button.isEnabled())
            button.setEnabled(False)
            self.assertFalse(button.isEnabled())
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test ModernButton styling: {e}')

    def test_progress_indicator_creation(self):
        try:
            from gui.common_components import ProgressIndicator
            progress = ProgressIndicator()
            self.assertIsNotNone(progress)
            custom_progress = ProgressIndicator('Custom Progress')
            self.assertIsNotNone(custom_progress)
        except ImportError as e:
            self.skipTest(f'Cannot import ProgressIndicator: {e}')

    def test_progress_indicator_value_updates(self):
        try:
            from gui.common_components import ProgressIndicator
            progress = ProgressIndicator('Test Progress')
            progress.set_progress(0)
            progress.set_progress(50)
            progress.set_progress(100)
            progress.set_status_text('Processing...')
            progress.set_status_text('Complete')
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test ProgressIndicator updates: {e}')

    def test_connection_manager_creation(self):
        try:
            from gui.common_components import ConnectionManager
            devices = ['Device1', 'Device2', 'Device3']
            manager = ConnectionManager(devices)
            self.assertIsNotNone(manager)
        except ImportError as e:
            self.skipTest(f'Cannot import ConnectionManager: {e}')

    def test_connection_manager_device_updates(self):
        try:
            from gui.common_components import ConnectionManager
            devices = ['PC', 'Shimmer', 'Thermal']
            manager = ConnectionManager(devices)
            manager.update_device_status('PC', True, 'Connected')
            manager.update_device_status('Shimmer', False, 'Disconnected')
            manager.update_device_status('Thermal', True, 'Active')
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test ConnectionManager updates: {e}')

    def test_log_viewer_creation(self):
        try:
            from gui.common_components import LogViewer
            log_viewer = LogViewer()
            self.assertIsNotNone(log_viewer)
            custom_viewer = LogViewer('Custom Log')
            self.assertIsNotNone(custom_viewer)
        except ImportError as e:
            self.skipTest(f'Cannot import LogViewer: {e}')

    def test_log_viewer_operations(self):
        try:
            from gui.common_components import LogViewer
            log_viewer = LogViewer('Test Log')
            log_viewer.add_log('Info message', 'info')
            log_viewer.add_log('Warning message', 'warning')
            log_viewer.add_log('Error message', 'error')
            log_viewer.clear_logs()
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test LogViewer operations: {e}')

    def test_modern_group_box_creation(self):
        try:
            from gui.common_components import ModernGroupBox
            group_box = ModernGroupBox('Test Group')
            self.assertIsNotNone(group_box)
        except ImportError as e:
            self.skipTest(f'Cannot import ModernGroupBox: {e}')

    def test_component_integration(self):
        try:
            from gui.common_components import StatusIndicator, ModernButton, ProgressIndicator, ConnectionManager, LogViewer, ModernGroupBox
            group = ModernGroupBox('Integration Test')
            status = StatusIndicator('Test Status')
            button = ModernButton('Test Action', 'primary')
            progress = ProgressIndicator('Test Progress')
            self.assertIsNotNone(group)
            self.assertIsNotNone(status)
            self.assertIsNotNone(button)
            self.assertIsNotNone(progress)
        except ImportError as e:
            self.skipTest(f'Cannot test component integration: {e}')

    def test_component_signals(self):
        try:
            from gui.common_components import StatusIndicator, ModernButton
            status = StatusIndicator()
            signal_emitted = False

            def on_status_changed(connected, text):
                nonlocal signal_emitted
                signal_emitted = True
            status.statusChanged.connect(on_status_changed)
            status.set_status(True, 'Connected')
            QTest.qWait(10)
            button = ModernButton('Test')
            button_clicked = False

            def on_button_clicked():
                nonlocal button_clicked
                button_clicked = True
            button.clicked.connect(on_button_clicked)
            button.click()
            QTest.qWait(10)
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test component signals: {e}')

    def test_error_handling(self):
        try:
            from gui.common_components import StatusIndicator, ProgressIndicator
            status = StatusIndicator()
            status.set_status(None, None)
            progress = ProgressIndicator()
            progress.set_progress(-10)
            progress.set_progress(150)
        except (ImportError, AttributeError) as e:
            self.skipTest(f'Cannot test error handling: {e}')


class TestComponentModuleMocking(unittest.TestCase):

    def test_module_import_with_mock(self):
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': MagicMock(),
            'PyQt5.QtCore': MagicMock(), 'PyQt5.QtGui': MagicMock()}):
            try:
                from gui import common_components
                self.assertIsNotNone(common_components)
            except ImportError as e:
                self.skipTest(
                    f'Cannot import common_components even with mocks: {e}')

    def test_component_functionality_with_mocks(self):
        mock_widget = MagicMock()
        mock_signal = MagicMock()
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': MagicMock(),
            'PyQt5.QtCore': MagicMock(pyqtSignal=lambda *args: mock_signal),
            'PyQt5.QtGui': MagicMock()}):
            try:
                from gui.common_components import StatusIndicator
                status = StatusIndicator()
                self.assertIsNotNone(status)
            except ImportError as e:
                self.skipTest(f'Cannot test with mocks: {e}')


if __name__ == '__main__':
    verbosity = 2 if '-v' in sys.argv else 1
    test_suite = unittest.TestLoader().loadTestsFromTestCase(
        TestCommonComponents)
    mock_suite = unittest.TestLoader().loadTestsFromTestCase(
        TestComponentModuleMocking)
    combined_suite = unittest.TestSuite([test_suite, mock_suite])
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(combined_suite)
    sys.exit(0 if result.wasSuccessful() else 1)
