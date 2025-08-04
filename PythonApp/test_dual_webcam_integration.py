import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from utils.logging_config import get_logger, AppLogger
from webcam.dual_webcam_capture import test_dual_webcam_access


class TestDualWebcamIntegration(unittest.TestCase):

    def setUp(self):
        self.logger = get_logger('TestDualWebcamIntegration')
        AppLogger.set_level('DEBUG')

    def test_camera_test_function_default_indices(self):
        self.logger.info('Testing camera test function with default indices')
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_cap1 = Mock()
            mock_cap2 = Mock()
            mock_cap1.isOpened.return_value = True
            mock_cap1.read.return_value = True, Mock(shape=(480, 640, 3))
            mock_cap2.isOpened.return_value = True
            mock_cap2.read.return_value = True, Mock(shape=(480, 640, 3))

            def video_capture_side_effect(index):
                if index == 0:
                    return mock_cap1
                elif index == 1:
                    return mock_cap2
                else:
                    mock_fail = Mock()
                    mock_fail.isOpened.return_value = False
                    return mock_fail
            mock_video_capture.side_effect = video_capture_side_effect
            result = test_dual_webcam_access()
            self.assertTrue(result,
                'Camera test should succeed with mocked cameras')
            self.assertEqual(mock_video_capture.call_count, 2)
            mock_cap1.release.assert_called_once()
            mock_cap2.release.assert_called_once()

    def test_camera_test_function_custom_indices(self):
        self.logger.info('Testing camera test function with custom indices')
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_cap2 = Mock()
            mock_cap3 = Mock()
            mock_cap2.isOpened.return_value = True
            mock_cap2.read.return_value = True, Mock(shape=(1080, 1920, 3))
            mock_cap3.isOpened.return_value = True
            mock_cap3.read.return_value = True, Mock(shape=(1080, 1920, 3))

            def video_capture_side_effect(index):
                if index == 2:
                    return mock_cap2
                elif index == 3:
                    return mock_cap3
                else:
                    mock_fail = Mock()
                    mock_fail.isOpened.return_value = False
                    return mock_fail
            mock_video_capture.side_effect = video_capture_side_effect
            result = test_dual_webcam_access([2, 3])
            self.assertTrue(result,
                'Camera test should succeed with custom indices')
            self.assertEqual(mock_video_capture.call_count, 2)
            mock_video_capture.assert_any_call(2)
            mock_video_capture.assert_any_call(3)

    def test_camera_test_function_failure(self):
        self.logger.info('Testing camera test function failure scenarios')
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_cap1 = Mock()
            mock_cap1.isOpened.return_value = False
            mock_video_capture.return_value = mock_cap1
            result = test_dual_webcam_access([0, 1])
            self.assertFalse(result,
                'Camera test should fail when first camera cannot open')
            mock_cap1.isOpened.return_value = True
            mock_cap1.read.return_value = False, None
            result = test_dual_webcam_access([0, 1])
            self.assertFalse(result,
                'Camera test should fail when first camera cannot read')

    def test_camera_test_invalid_indices(self):
        self.logger.info('Testing camera test function with invalid indices')
        result = test_dual_webcam_access([0])
        self.assertFalse(result,
            'Camera test should fail with only one camera index')
        result = test_dual_webcam_access([0, 1, 2])
        self.assertFalse(result,
            'Camera test should fail with more than two camera indices')

    @patch('PyQt5.QtWidgets.QApplication')
    def test_dual_webcam_main_window_import(self, mock_qapp):
        self.logger.info(
            'Testing DualWebcamMainWindow import and instantiation')
        try:
            from gui.dual_webcam_main_window import DualWebcamMainWindow
            with patch('gui.dual_webcam_main_window.test_dual_webcam_access'):
                main_window = DualWebcamMainWindow()
                self.assertIsNotNone(main_window,
                    'Main window should be created')
                self.assertEqual(main_window.camera_indices, [0, 1],
                    'Default camera indices should be [0, 1]')
            camera_indices = [2, 3]
            initial_settings = {'camera1_index': 2, 'camera2_index': 3,
                'width': 1920, 'height': 1080, 'fps': 30}
            with patch('gui.dual_webcam_main_window.test_dual_webcam_access'):
                main_window = DualWebcamMainWindow(camera_indices=
                    camera_indices, initial_settings=initial_settings)
                self.assertEqual(main_window.camera_indices, camera_indices)
                self.assertEqual(main_window.initial_settings, initial_settings
                    )
        except ImportError as e:
            self.fail(f'Could not import DualWebcamMainWindow: {e}')

    def test_launch_script_argument_parsing(self):
        self.logger.info('Testing launch script argument parsing')
        import sys
        original_argv = sys.argv.copy()
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from launch_dual_webcam import parse_arguments
            sys.argv = ['launch_dual_webcam.py']
            args = parse_arguments()
            self.assertEqual(args.cameras, '0,1')
            self.assertEqual(args.resolution, '3840x2160')
            self.assertEqual(args.fps, 30)
            self.assertFalse(args.test_only)
            sys.argv = ['launch_dual_webcam.py', '--cameras', '2,3',
                '--resolution', '1920x1080', '--fps', '60', '--test-only',
                '--log-level', 'DEBUG']
            args = parse_arguments()
            self.assertEqual(args.cameras, '2,3')
            self.assertEqual(args.resolution, '1920x1080')
            self.assertEqual(args.fps, 60)
            self.assertTrue(args.test_only)
            self.assertEqual(args.log_level, 'DEBUG')
        finally:
            sys.argv = original_argv

    def test_settings_parsing_in_launch_script(self):
        self.logger.info('Testing camera settings parsing')
        test_cases = [('0,1', [0, 1]), ('2,3', [2, 3]), ('0, 1', [0, 1]), (
            '10,11', [10, 11])]
        for camera_str, expected in test_cases:
            camera_indices = [int(x.strip()) for x in camera_str.split(',')]
            self.assertEqual(camera_indices, expected,
                f'Failed for input: {camera_str}')
        resolution_cases = [('3840x2160', (3840, 2160)), ('1920x1080', (
            1920, 1080)), ('1280x720', (1280, 720)), ('640x480', (640, 480))]
        for res_str, expected in resolution_cases:
            width, height = map(int, res_str.split('x'))
            self.assertEqual((width, height), expected,
                f'Failed for resolution: {res_str}')


class TestLoggingEnhancements(unittest.TestCase):

    def setUp(self):
        self.logger = get_logger('TestLoggingEnhancements')

    def test_structured_logging(self):
        self.logger.info('Testing structured logging')
        extra_data = {'operation': 'camera_test', 'camera_index': 0,
            'success': True}
        self.logger.info('Camera test completed', extra=extra_data)
        self.logger.debug('Debug message', extra={'debug_info': 'test'})
        self.logger.warning('Warning message', extra={'warning_type':
            'camera_disconnected'})
        self.logger.error('Error message', extra={'error_code': 404})

    def test_performance_monitoring(self):
        self.logger.info('Testing performance monitoring')
        timer_id = AppLogger.start_performance_timer('test_operation',
            'unit_test')
        self.assertIsNotNone(timer_id, 'Timer ID should not be None')
        import time
        time.sleep(0.01)
        duration = AppLogger.end_performance_timer(timer_id,
            'TestLoggingEnhancements')
        self.assertGreater(duration, 0, 'Duration should be positive')
        self.assertLess(duration, 1.0, 'Duration should be reasonable for test'
            )

    def test_memory_usage_logging(self):
        self.logger.info('Testing memory usage logging')
        AppLogger.log_memory_usage('unit_test_start')
        test_data = [i for i in range(1000)]
        AppLogger.log_memory_usage('unit_test_after_allocation')
        del test_data

    def test_log_level_changes(self):
        self.logger.info('Testing log level changes')
        AppLogger.set_level('DEBUG')
        self.logger.debug('This debug message should be visible')
        AppLogger.set_level('WARNING')
        self.logger.info('This info message should be filtered')
        self.logger.warning('This warning message should be visible')
        AppLogger.set_level('INFO')


def run_tests():
    logger = get_logger('TestRunner')
    logger.info('=== Running Dual Webcam Integration Tests ===')
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDualWebcamIntegration))
    suite.addTest(unittest.makeSuite(TestLoggingEnhancements))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        logger.info('✓ All tests passed!')
        return 0
    else:
        logger.error(
            f'✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)'
            )
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
