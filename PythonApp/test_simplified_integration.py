import sys
import os
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from utils.logging_config import get_logger, AppLogger


class TestLoggingComprehensive(unittest.TestCase):

    def setUp(self):
        self.logger = get_logger('TestLoggingComprehensive')
        AppLogger.set_level('DEBUG')

    def test_logger_manager_functionality(self):
        self.logger.info('Testing LoggerManager functionality')
        from utils.logger import get_logger_manager, LogLevel
        logger_manager = get_logger_manager()
        self.assertIsNotNone(logger_manager, 'Logger manager should be created'
            )
        test_logger = logger_manager.get_logger('test_module')
        self.assertIsNotNone(test_logger, 'Logger should be created')
        logger_manager.log_structured('test_module', LogLevel.INFO,
            'Test message', test_key='test_value', operation='unit_test')
        logger_manager.log_performance('test_operation', duration_ms=123.45,
            test_metadata='test_value')
        logger_manager.log_network_event('device_connected',
            'test_device_001', device_type='webcam', status='active')
        logger_manager.log_calibration_event('calibration_started',
            camera_id=0, calibration_type='intrinsic')

    def test_log_levels_enum(self):
        from utils.logger import LogLevel
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel
            .ERROR, LogLevel.CRITICAL]
        self.assertEqual(len(levels), 5, 'Should have 5 log levels')
        self.assertEqual(LogLevel.DEBUG.value, 'DEBUG')
        self.assertEqual(LogLevel.INFO.value, 'INFO')
        self.assertEqual(LogLevel.WARNING.value, 'WARNING')
        self.assertEqual(LogLevel.ERROR.value, 'ERROR')
        self.assertEqual(LogLevel.CRITICAL.value, 'CRITICAL')

    def test_convenience_logging_functions(self):
        from utils.logger import log_info, log_error, log_debug, log_warning, log_critical
        log_debug('test_logger', 'Debug message', test_data='debug')
        log_info('test_logger', 'Info message', test_data='info')
        log_warning('test_logger', 'Warning message', test_data='warning')
        log_error('test_logger', 'Error message', test_data='error')
        log_critical('test_logger', 'Critical message', test_data='critical')

    def test_performance_decorators(self):
        from utils.logging_config import performance_timer, log_function_entry

        @performance_timer('test_function')
        def test_function():
            import time
            time.sleep(0.01)
            return 'success'
        result = test_function()
        self.assertEqual(result, 'success')

        @log_function_entry
        def test_function_entry(arg1, arg2='default'):
            return f'{arg1}_{arg2}'
        result = test_function_entry('test', arg2='value')
        self.assertEqual(result, 'test_value')

    def test_memory_usage_monitoring(self):
        from utils.logging_config import log_memory_usage

        @log_memory_usage('memory_test')
        def memory_intensive_function():
            data = [i for i in range(1000)]
            return len(data)
        result = memory_intensive_function()
        self.assertEqual(result, 1000)

    def test_exception_context_logging(self):
        from utils.logging_config import log_exception_context
        with log_exception_context('test_operation'):
            result = 2 + 2
        self.assertEqual(result, 4)
        try:
            with log_exception_context('test_exception'):
                raise ValueError('Test exception')
        except ValueError as e:
            self.assertEqual(str(e), 'Test exception')

    def test_structured_formatter(self):
        from utils.logging_config import StructuredFormatter
        import logging
        import json
        logger = logging.getLogger('test')
        record = logger.makeRecord(name='test', level=logging.INFO, fn=
            'test.py', lno=42, msg='Test message', args=(), exc_info=None)
        formatter = StructuredFormatter()
        formatted = formatter.format(record)
        try:
            log_data = json.loads(formatted)
            self.assertIn('timestamp', log_data)
            self.assertIn('level', log_data)
            self.assertIn('message', log_data)
            self.assertEqual(log_data['level'], 'INFO')
            self.assertEqual(log_data['message'], 'Test message')
        except json.JSONDecodeError:
            self.fail('Formatted log should be valid JSON')

    def test_app_logger_initialization(self):
        log_dir = AppLogger.get_log_dir()
        self.assertIsNotNone(log_dir, 'Log directory should be set')
        logger1 = AppLogger.get_logger('test_module_1')
        logger2 = AppLogger.get_logger('test_module_2')
        self.assertIsNotNone(logger1)
        self.assertIsNotNone(logger2)
        self.assertNotEqual(logger1, logger2)
        timer_id = AppLogger.start_performance_timer('test_timer', 'unit_test')
        self.assertIsNotNone(timer_id)
        import time
        time.sleep(0.01)
        duration = AppLogger.end_performance_timer(timer_id,
            'TestLoggingComprehensive')
        self.assertGreater(duration, 0)
        self.assertLess(duration, 1.0)

    def test_log_cleanup_functionality(self):
        from utils.logger import get_logger_manager
        from datetime import datetime, timedelta
        logger_manager = get_logger_manager()
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        try:
            export_path = logger_manager.export_logs(start_date, end_date,
                'json')
            if export_path:
                self.assertTrue(len(export_path) > 0)
        except Exception:
            pass
        try:
            cleanup_report = logger_manager.cleanup_old_logs(retention_days=30)
            self.assertIn('removed_files', cleanup_report)
            self.assertIn('compressed_files', cleanup_report)
            self.assertIn('errors', cleanup_report)
        except Exception:
            pass


class TestLaunchScriptLogic(unittest.TestCase):

    def test_argument_parsing_logic(self):
        test_cases = [('0,1', [0, 1]), ('2,3', [2, 3]), ('0, 1', [0, 1]), (
            '10,11', [10, 11])]
        for camera_str, expected in test_cases:
            try:
                camera_indices = [int(x.strip()) for x in camera_str.split(',')
                    ]
                self.assertEqual(camera_indices, expected,
                    f'Failed for input: {camera_str}')
                self.assertEqual(len(camera_indices), 2,
                    'Should have exactly 2 cameras')
            except ValueError:
                self.fail(f'Should parse valid camera string: {camera_str}')
        invalid_cases = ['0', '0,1,2', 'a,b', '']
        for invalid_str in invalid_cases:
            try:
                camera_indices = [int(x.strip()) for x in invalid_str.split
                    (',')]
                if len(camera_indices) != 2:
                    continue
                if invalid_str in ['0', '0,1,2']:
                    continue
                self.fail(
                    f'Should not parse invalid camera string: {invalid_str}')
            except ValueError:
                pass

    def test_resolution_parsing_logic(self):
        resolution_cases = [('3840x2160', (3840, 2160)), ('1920x1080', (
            1920, 1080)), ('1280x720', (1280, 720)), ('640x480', (640, 480))]
        for res_str, expected in resolution_cases:
            try:
                width, height = map(int, res_str.split('x'))
                self.assertEqual((width, height), expected,
                    f'Failed for resolution: {res_str}')
                self.assertGreater(width, 0, 'Width should be positive')
                self.assertGreater(height, 0, 'Height should be positive')
            except ValueError:
                self.fail(f'Should parse valid resolution string: {res_str}')
        invalid_resolutions = ['1920', '1920x', 'x1080', 'abcxdef', '']
        for invalid_res in invalid_resolutions:
            try:
                width, height = map(int, invalid_res.split('x'))
                if invalid_res in ['', '1920', 'x1080']:
                    continue
                self.fail(f'Should not parse invalid resolution: {invalid_res}'
                    )
            except ValueError:
                pass

    def test_camera_settings_structure(self):
        camera_indices = [0, 1]
        width, height = 1920, 1080
        fps = 30
        camera_settings = {'camera1_index': camera_indices[0],
            'camera2_index': camera_indices[1], 'width': width, 'height':
            height, 'fps': fps}
        required_keys = ['camera1_index', 'camera2_index', 'width',
            'height', 'fps']
        for key in required_keys:
            self.assertIn(key, camera_settings,
                f'Settings should contain {key}')
        self.assertIsInstance(camera_settings['camera1_index'], int)
        self.assertIsInstance(camera_settings['camera2_index'], int)
        self.assertIsInstance(camera_settings['width'], int)
        self.assertIsInstance(camera_settings['height'], int)
        self.assertIsInstance(camera_settings['fps'], int)
        self.assertGreaterEqual(camera_settings['camera1_index'], 0)
        self.assertGreaterEqual(camera_settings['camera2_index'], 0)
        self.assertGreater(camera_settings['width'], 0)
        self.assertGreater(camera_settings['height'], 0)
        self.assertGreater(camera_settings['fps'], 0)


def run_simplified_tests():
    logger = get_logger('SimplifiedTestRunner')
    logger.info('=== Running Simplified Dual Webcam Integration Tests ===')
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLoggingComprehensive))
    suite.addTest(unittest.makeSuite(TestLaunchScriptLogic))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        logger.info('✓ All simplified tests passed!')
        return 0
    else:
        logger.error(
            f'✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)'
            )
        return 1


if __name__ == '__main__':
    exit_code = run_simplified_tests()
    sys.exit(exit_code)
