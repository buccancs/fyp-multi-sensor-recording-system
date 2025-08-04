import pytest
import tempfile
import json
import time
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.logging_config import AppLogger, get_logger, performance_timer, log_function_entry, log_method_entry, log_exception_context, log_memory_usage, PerformanceMonitor, StructuredFormatter, ColoredFormatter


class TestEnhancedLogging:

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        AppLogger._initialized = False
        AppLogger._root_logger = None
        AppLogger._log_dir = None
        AppLogger.initialize(log_level='DEBUG', log_dir=self.temp_dir,
            console_output=False, file_output=True, structured_logging=True)

    def teardown_method(self):
        if AppLogger._root_logger:
            for handler in AppLogger._root_logger.handlers[:]:
                handler.close()
                AppLogger._root_logger.removeHandler(handler)
        AppLogger._initialized = False
        AppLogger._root_logger = None
        AppLogger._log_dir = None

    def test_basic_logging(self):
        logger = get_logger('test_module')
        logger.debug('Debug message')
        logger.info('Info message')
        logger.warning('Warning message')
        logger.error('Error message')
        logger.critical('Critical message')
        log_dir = Path(self.temp_dir)
        assert (log_dir / 'application.log').exists()
        assert (log_dir / 'errors.log').exists()
        assert (log_dir / 'structured.log').exists()
        with open(log_dir / 'application.log', 'r') as f:
            app_log_content = f.read()
            assert 'Debug message' in app_log_content
            assert 'Info message' in app_log_content
            assert 'Warning message' in app_log_content
            assert 'Error message' in app_log_content
            assert 'Critical message' in app_log_content
        with open(log_dir / 'errors.log', 'r') as f:
            error_log_content = f.read()
            assert 'Debug message' not in error_log_content
            assert 'Info message' not in error_log_content
            assert 'Error message' in error_log_content
            assert 'Critical message' in error_log_content

    def test_structured_logging(self):
        logger = get_logger('test_structured')
        logger.info('Test structured message', extra={'custom_field':
            'custom_value'})
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'structured.log', 'r') as f:
            lines = f.readlines()
        test_entry = None
        for line in lines:
            try:
                entry = json.loads(line.strip())
                if entry.get('message') == 'Test structured message':
                    test_entry = entry
                    break
            except json.JSONDecodeError:
                continue
        assert test_entry is not None
        assert test_entry['level'] == 'INFO'
        assert test_entry['logger'] == 'test_structured'
        assert test_entry['message'] == 'Test structured message'
        assert 'timestamp' in test_entry
        assert 'thread' in test_entry
        assert 'extra' in test_entry
        assert test_entry['extra']['custom_field'] == 'custom_value'

    def test_performance_monitoring(self):
        timer_id = AppLogger.start_performance_timer('test_operation',
            'test_context')
        time.sleep(0.1)
        duration = AppLogger.end_performance_timer(timer_id, 'test_logger')
        assert duration >= 0.1
        assert duration < 0.2

        @performance_timer('decorated_operation')
        def test_function():
            time.sleep(0.05)
            return 'test_result'
        result = test_function()
        assert result == 'test_result'
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert "Operation 'test_operation' completed in" in log_content
            assert "Operation 'decorated_operation' completed in" in log_content

    def test_function_entry_logging(self):

        @log_function_entry
        def test_function(arg1, arg2=None):
            return f'{arg1}_{arg2}'
        result = test_function('hello', arg2='world')
        assert result == 'hello_world'
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert '→ Entering test_function' in log_content
            assert '← Exiting test_function successfully' in log_content

    def test_method_entry_logging(self):


        class TestClass:

            @log_method_entry
            def test_method(self, arg1):
                return f'method_{arg1}'
        test_obj = TestClass()
        result = test_obj.test_method('test')
        assert result == 'method_test'
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert '→ Entering TestClass.test_method' in log_content
            assert '← Exiting TestClass.test_method successfully' in log_content

    def test_exception_logging(self):

        @log_function_entry
        def failing_function():
            raise ValueError('Test exception')
        with pytest.raises(ValueError):
            failing_function()
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert '✗ Exception in failing_function' in log_content
            assert 'ValueError: Test exception' in log_content

    def test_exception_context_manager(self):
        with pytest.raises(RuntimeError):
            with log_exception_context('test_context'):
                raise RuntimeError('Context test exception')
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert 'Exception occurred: RuntimeError: Context test exception' in log_content

    @patch('psutil.Process')
    def test_memory_usage_logging(self, mock_process):
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 100 * 1024 * 1024
        mock_memory_info.vms = 200 * 1024 * 1024
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process_instance.memory_percent.return_value = 15.5
        mock_process.return_value = mock_process_instance
        AppLogger.log_memory_usage('test_context', 'test_logger')
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert 'Memory usage at test_context' in log_content
            assert 'RSS=100.0MB' in log_content
            assert 'VMS=200.0MB' in log_content
            assert '15.5%' in log_content

    def test_memory_usage_decorator(self):
        with patch('psutil.Process') as mock_process:
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 50 * 1024 * 1024
            mock_memory_info.vms = 100 * 1024 * 1024
            mock_process_instance = MagicMock()
            mock_process_instance.memory_info.return_value = mock_memory_info
            mock_process_instance.memory_percent.return_value = 10.0
            mock_process.return_value = mock_process_instance

            @log_memory_usage('decorator_test')
            def test_function():
                return 'memory_test'
            result = test_function()
            assert result == 'memory_test'
            log_dir = Path(self.temp_dir)
            with open(log_dir / 'application.log', 'r') as f:
                log_content = f.read()
                assert 'Memory usage at decorator_test - before test_function' in log_content
                assert 'Memory usage at decorator_test - after test_function' in log_content

    def test_colored_formatter(self):
        formatter = ColoredFormatter('%(levelname)s: %(message)s')
        import logging
        record = logging.LogRecord(name='test_logger', level=logging.INFO,
            pathname='/test/path.py', lineno=42, msg='Test message', args=(
            ), exc_info=None)
        formatted = formatter.format(record)
        assert '\x1b[32m' in formatted
        assert '\x1b[0m' in formatted
        assert 'Test message' in formatted

    def test_structured_formatter(self):
        formatter = StructuredFormatter()
        import logging
        record = logging.LogRecord(name='test_logger', level=logging.INFO,
            pathname='/test/path.py', lineno=42, msg=
            'Test structured message', args=(), exc_info=None)
        record.module = 'test_module'
        record.funcName = 'test_function'
        record.custom_field = 'custom_value'
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        assert parsed['level'] == 'INFO'
        assert parsed['logger'] == 'test_logger'
        assert parsed['message'] == 'Test structured message'
        assert parsed['module'] == 'test_module'
        assert parsed['function'] == 'test_function'
        assert parsed['line'] == 42
        assert 'timestamp' in parsed
        assert 'extra' in parsed
        assert parsed['extra']['custom_field'] == 'custom_value'

    def test_performance_monitor_thread_safety(self):
        results = []

        def worker_function(worker_id):
            timer_id = PerformanceMonitor.start_timer(f'worker_{worker_id}')
            time.sleep(0.01)
            duration = PerformanceMonitor.end_timer(timer_id)
            results.append((worker_id, duration))
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        assert len(results) == 5
        for worker_id, duration in results:
            assert duration > 0.005
            assert duration < 0.1

    def test_log_level_changes(self):
        logger = get_logger('level_test')
        AppLogger.set_level('INFO')
        logger.debug('Debug message - should not appear')
        logger.info('Info message - should appear')
        AppLogger.set_level('DEBUG')
        logger.debug('Debug message - should now appear')
        logger.info('Another info message')
        log_dir = Path(self.temp_dir)
        with open(log_dir / 'application.log', 'r') as f:
            log_content = f.read()
            assert 'Info message - should appear' in log_content
            assert 'Debug message - should now appear' in log_content
            assert 'Another info message' in log_content

    def test_get_active_timers(self):
        timer1 = AppLogger.start_performance_timer('operation1', 'context1')
        timer2 = AppLogger.start_performance_timer('operation2', 'context2')
        active_timers = AppLogger.get_active_timers()
        assert len(active_timers) == 2
        assert timer1 in active_timers
        assert timer2 in active_timers
        timer1_info = active_timers[timer1]
        assert timer1_info['operation'] == 'operation1'
        assert timer1_info['context'] == 'context1'
        assert 'start_time' in timer1_info
        assert 'thread' in timer1_info
        AppLogger.end_performance_timer(timer1)
        active_timers = AppLogger.get_active_timers()
        assert len(active_timers) == 1
        assert timer1 not in active_timers
        assert timer2 in active_timers
        AppLogger.end_performance_timer(timer2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
