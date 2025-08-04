import os
import pytest
import shutil
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCalibrationDialogEnvironment:

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_pyqt5_gui_imports(self):
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
            from PyQt5.QtWidgets import QPushButton, QProgressBar, QTextEdit, QGroupBox
            from PyQt5.QtWidgets import QCheckBox, QSpinBox, QSlider, QGridLayout
            from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
            from PyQt5.QtWidgets import QFileDialog, QTabWidget, QWidget
            from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
            from PyQt5.QtGui import QPixmap, QFont, QIcon
            assert True
        except ImportError as e:
            pytest.fail(f'PyQt5 GUI import failed: {e}')

    def test_calibration_dialog_dependencies(self):
        try:
            import cv2
            import numpy as np
            import json
            import time
            assert True
        except ImportError as e:
            pytest.fail(f'CalibrationDialog dependency import failed: {e}')


class TestCalibrationDialogInitialization:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_dialog_initialization(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            assert dialog is not None
            assert dialog.device_server == self.mock_device_server
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_dialog_window_properties(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            assert dialog.windowTitle() == 'Camera Calibration - Milestone 3.4'
            assert dialog.isModal() is True
            size = dialog.size()
            assert size.width() >= 800
            assert size.height() >= 600
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_dialog_components_initialization(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            assert hasattr(dialog, 'start_session_btn')
            assert hasattr(dialog, 'end_session_btn')
            assert hasattr(dialog, 'capture_frame_btn')
            assert hasattr(dialog, 'compute_btn')
            assert hasattr(dialog, 'save_btn')
            assert hasattr(dialog, 'load_btn')
            assert hasattr(dialog, 'close_btn')
            assert hasattr(dialog, 'overlay_checkbox')
            assert hasattr(dialog, 'overlay_alpha_slider')
            assert dialog.end_session_btn.isEnabled() is False
            assert dialog.capture_frame_btn.isEnabled() is False
            assert dialog.compute_btn.isEnabled() is False
            assert dialog.save_btn.isEnabled() is False
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogSessionManagement:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_start_calibration_session_success(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.start_calibration_session.return_value = {'success':
                True, 'session_id': 'test_session_123'}
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            with patch.object(dialog, 'get_connected_devices', return_value
                =['device_1', 'device_2']):
                dialog.start_calibration_session()
            assert dialog.current_session == 'test_session_123'
            assert dialog.start_session_btn.isEnabled() is False
            assert dialog.end_session_btn.isEnabled() is True
            assert dialog.capture_frame_btn.isEnabled() is True
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_start_session_no_devices(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            with patch.object(dialog, 'get_connected_devices', return_value=[]
                ):
                with patch('PyQt5.QtWidgets.QMessageBox.warning'
                    ) as mock_warning:
                    dialog.start_calibration_session()
                    mock_warning.assert_called_once()
            assert dialog.current_session is None
            assert dialog.start_session_btn.isEnabled() is True
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_end_calibration_session(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.end_calibration_session.return_value = {'success':
                True}
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.current_session = 'test_session_123'
            dialog.end_calibration_session()
            assert dialog.current_session is None
            assert dialog.start_session_btn.isEnabled() is True
            assert dialog.end_session_btn.isEnabled() is False
            assert dialog.capture_frame_btn.isEnabled() is False
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogFrameCapture:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_capture_calibration_frame_success(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.capture_calibration_frame.return_value = {'success':
                True, 'total_frames': 3, 'timestamp': '2025-07-29T12:00:00',
                'pattern_detected': True}
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.current_session = 'test_session'
            dialog.capture_calibration_frame()
            assert dialog.frame_counter_label.text() == 'Frames captured: 3'
            assert dialog.capture_progress.value() == 3
            assert dialog.frames_list.count() == 1
            if 3 >= 5:
                assert dialog.compute_btn.isEnabled() is True
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_capture_frame_failure(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.capture_calibration_frame.return_value = {'success':
                False, 'error': 'Device communication failed'}
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.current_session = 'test_session'
            with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
                dialog.capture_calibration_frame()
                mock_warning.assert_called_once()
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogComputation:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_compute_calibration_success(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            from calibration.calibration_result import CalibrationResult
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_result = Mock(spec=CalibrationResult)
            mock_result.get_calibration_summary.return_value = {'rgb_error':
                0.5, 'thermal_error': 0.7, 'stereo_error': 0.8, 'rgb_fx': 
                1000.0, 'rgb_fy': 1000.0, 'rgb_cx': 320.0, 'rgb_cy': 240.0,
                'thermal_fx': 500.0, 'thermal_fy': 500.0, 'thermal_cx': 
                160.0, 'thermal_cy': 120.0, 'translation':
                '[1.0, 0.0, 0.0]', 'rotation_angles': '[0.0, 0.0, 0.0]'}
            mock_manager.compute_calibration.return_value = {'success': 
                True, 'results': {'device_1': mock_result}}
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.current_session = 'test_session'
            dialog.compute_calibration()
            assert dialog.save_btn.isEnabled() is True
            assert dialog.overlay_checkbox.isEnabled() is True
            assert len(dialog.device_results) == 1
            assert 'device_1' in dialog.device_results
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    @patch('gui.calibration_dialog.CalibrationManager')
    def test_compute_calibration_failure(self, mock_manager_class):
        try:
            from gui.calibration_dialog import CalibrationDialog
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.compute_calibration.return_value = {'success': 
                False, 'error': 'Insufficient calibration data'}
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.current_session = 'test_session'
            with patch('PyQt5.QtWidgets.QMessageBox.critical'
                ) as mock_critical:
                dialog.compute_calibration()
                mock_critical.assert_called_once()
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogResultsManagement:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_save_calibration_results(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            from calibration.calibration_result import CalibrationResult
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            mock_result = Mock(spec=CalibrationResult)
            mock_result.save_to_file = Mock()
            dialog.device_results = {'device_1': mock_result}
            test_filename = os.path.join(self.temp_dir, 'test_calibration.json'
                )
            with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName',
                return_value=(test_filename, '')):
                with patch('PyQt5.QtWidgets.QMessageBox.information'
                    ) as mock_info:
                    dialog.save_calibration()
                    mock_info.assert_called_once()
            mock_result.save_to_file.assert_called_once()
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_load_calibration_results(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            from calibration.calibration_result import CalibrationResult
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            test_filename = os.path.join(self.temp_dir, 'test_calibration.json'
                )
            with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                return_value=(test_filename, '')):
                with patch.object(CalibrationResult, 'load_from_file'
                    ) as mock_load:
                    mock_result = Mock(spec=CalibrationResult)
                    mock_load.return_value = mock_result
                    with patch('PyQt5.QtWidgets.QMessageBox.information'
                        ) as mock_info:
                        dialog.load_calibration()
                        mock_info.assert_called_once()
            assert len(dialog.device_results) == 1
            assert dialog.save_btn.isEnabled() is True
            assert dialog.overlay_checkbox.isEnabled() is True
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogOverlayFunctionality:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_overlay_toggle_functionality(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            from calibration.calibration_result import CalibrationResult
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            mock_result = Mock(spec=CalibrationResult)
            dialog.device_results = {'device_1': mock_result}
            dialog.results_tabs = Mock()
            dialog.results_tabs.currentIndex.return_value = 0
            dialog.results_tabs.tabText.return_value = 'device_1'
            with patch.object(dialog, 'overlay_toggled') as mock_signal:
                dialog.toggle_overlay(True)
                mock_signal.emit.assert_called_once_with('device_1', True)
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_alpha_slider_functionality(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.update_alpha_label(50)
            assert dialog.overlay_alpha_label.text() == 'Alpha: 50%'
            dialog.update_alpha_label(75)
            assert dialog.overlay_alpha_label.text() == 'Alpha: 75%'
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogErrorHandling:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_exception_handling_in_session_start(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            with patch.object(dialog, 'get_connected_devices', side_effect=
                Exception('Connection error')):
                with patch('PyQt5.QtWidgets.QMessageBox.critical'
                    ) as mock_critical:
                    dialog.start_calibration_session()
                    mock_critical.assert_called_once()
        except ImportError:
            pytest.skip('CalibrationDialog not available')

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_exception_handling_in_frame_capture(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            dialog.current_session = 'test_session'
            with patch.object(dialog.calibration_manager,
                'capture_calibration_frame', side_effect=Exception(
                'Capture error')):
                with patch('PyQt5.QtWidgets.QMessageBox.critical'
                    ) as mock_critical:
                    dialog.capture_calibration_frame()
                    mock_critical.assert_called_once()
        except ImportError:
            pytest.skip('CalibrationDialog not available')


class TestCalibrationDialogSignalHandling:

    def setup_method(self):
        self.mock_device_server = Mock()
        self.mock_parent = Mock()

    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason=
        'Skip GUI tests in CI')
    def test_signal_connections(self):
        try:
            from gui.calibration_dialog import CalibrationDialog
            dialog = CalibrationDialog(self.mock_device_server, self.
                mock_parent)
            assert hasattr(dialog, 'calibration_completed')
            assert hasattr(dialog, 'overlay_toggled')
            from PyQt5.QtCore import pyqtSignal
            assert isinstance(dialog.calibration_completed, pyqtSignal)
            assert isinstance(dialog.overlay_toggled, pyqtSignal)
        except ImportError:
            pytest.skip('CalibrationDialog not available')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
