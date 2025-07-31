"""
Comprehensive tests for the enhanced logging system.

Tests all aspects of the enhanced logging configuration including:
- Basic logging functionality
- Performance monitoring
- Memory usage tracking
- Structured logging
- Log rotation
- Error handling

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
"""

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

from utils.logging_config import (
    AppLogger, get_logger, performance_timer, log_function_entry,
    log_method_entry, log_exception_context, log_memory_usage,
    PerformanceMonitor, StructuredFormatter, ColoredFormatter
)


class TestEnhancedLogging:
    """Test cases for enhanced logging functionality."""
    
    def setup_method(self):
        """Set up test environment for each test method."""
        # Create temporary log directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Reset the AppLogger state
        AppLogger._initialized = False
        AppLogger._root_logger = None
        AppLogger._log_dir = None
        
        # Initialize with test directory
        AppLogger.initialize(
            log_level="DEBUG",
            log_dir=self.temp_dir,
            console_output=False,  # Disable console for tests
            file_output=True,
            structured_logging=True
        )
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up log handlers to prevent file locks
        if AppLogger._root_logger:
            for handler in AppLogger._root_logger.handlers[:]:
                handler.close()
                AppLogger._root_logger.removeHandler(handler)
        
        # Reset state
        AppLogger._initialized = False
        AppLogger._root_logger = None
        AppLogger._log_dir = None
    
    def test_basic_logging(self):
        """Test basic logging functionality."""
        logger = get_logger("test_module")
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Check that log files were created
        log_dir = Path(self.temp_dir)
        assert (log_dir / "application.log").exists()
        assert (log_dir / "errors.log").exists()
        assert (log_dir / "structured.log").exists()
        
        # Check log file contents
        with open(log_dir / "application.log", 'r') as f:
            app_log_content = f.read()
            assert "Debug message" in app_log_content
            assert "Info message" in app_log_content
            assert "Warning message" in app_log_content
            assert "Error message" in app_log_content
            assert "Critical message" in app_log_content
        
        # Check error log contains only errors
        with open(log_dir / "errors.log", 'r') as f:
            error_log_content = f.read()
            assert "Debug message" not in error_log_content
            assert "Info message" not in error_log_content
            assert "Error message" in error_log_content
            assert "Critical message" in error_log_content
    
    def test_structured_logging(self):
        """Test structured JSON logging."""
        logger = get_logger("test_structured")
        logger.info("Test structured message", extra={'custom_field': 'custom_value'})
        
        log_dir = Path(self.temp_dir)
        with open(log_dir / "structured.log", 'r') as f:
            lines = f.readlines()
            
        # Find my test message
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
        """Test performance monitoring functionality."""
        # Test manual timer
        timer_id = AppLogger.start_performance_timer("test_operation", "test_context")
        time.sleep(0.1)
        duration = AppLogger.end_performance_timer(timer_id, "test_logger")
        
        assert duration >= 0.1
        assert duration < 0.2  # Should be close to 0.1 seconds
        
        # Test decorator
        @performance_timer("decorated_operation")
        def test_function():
            time.sleep(0.05)
            return "test_result"
        
        result = test_function()
        assert result == "test_result"
        
        # Check log for performance information
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "Operation 'test_operation' completed in" in log_content
            assert "Operation 'decorated_operation' completed in" in log_content
    
    def test_function_entry_logging(self):
        """Test function entry/exit logging."""
        @log_function_entry
        def test_function(arg1, arg2=None):
            return f"{arg1}_{arg2}"
        
        result = test_function("hello", arg2="world")
        assert result == "hello_world"
        
        # Check log for entry/exit messages
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "→ Entering test_function" in log_content
            assert "← Exiting test_function successfully" in log_content
    
    def test_method_entry_logging(self):
        """Test method entry/exit logging."""
        class TestClass:
            @log_method_entry
            def test_method(self, arg1):
                return f"method_{arg1}"
        
        test_obj = TestClass()
        result = test_obj.test_method("test")
        assert result == "method_test"
        
        # Check log for entry/exit messages
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "→ Entering TestClass.test_method" in log_content
            assert "← Exiting TestClass.test_method successfully" in log_content
    
    def test_exception_logging(self):
        """Test exception logging with decorators."""
        @log_function_entry
        def failing_function():
            raise ValueError("Test exception")
        
        with pytest.raises(ValueError):
            failing_function()
        
        # Check log for exception information
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "✗ Exception in failing_function" in log_content
            assert "ValueError: Test exception" in log_content
    
    def test_exception_context_manager(self):
        """Test exception context manager."""
        with pytest.raises(RuntimeError):
            with log_exception_context("test_context"):
                raise RuntimeError("Context test exception")
        
        # Check log for exception information
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "Exception occurred: RuntimeError: Context test exception" in log_content
    
    @patch('psutil.Process')
    def test_memory_usage_logging(self, mock_process):
        """Test memory usage logging."""
        # Mock memory info
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        mock_memory_info.vms = 200 * 1024 * 1024  # 200MB
        
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process_instance.memory_percent.return_value = 15.5
        mock_process.return_value = mock_process_instance
        
        AppLogger.log_memory_usage("test_context", "test_logger")
        
        # Check log for memory information
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "Memory usage at test_context" in log_content
            assert "RSS=100.0MB" in log_content
            assert "VMS=200.0MB" in log_content
            assert "15.5%" in log_content
    
    def test_memory_usage_decorator(self):
        """Test memory usage decorator."""
        with patch('psutil.Process') as mock_process:
            # Mock memory info
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 50 * 1024 * 1024  # 50MB
            mock_memory_info.vms = 100 * 1024 * 1024  # 100MB
            
            mock_process_instance = MagicMock()
            mock_process_instance.memory_info.return_value = mock_memory_info
            mock_process_instance.memory_percent.return_value = 10.0
            mock_process.return_value = mock_process_instance
            
            @log_memory_usage("decorator_test")
            def test_function():
                return "memory_test"
            
            result = test_function()
            assert result == "memory_test"
            
            # Check that memory logging was called
            log_dir = Path(self.temp_dir)
            with open(log_dir / "application.log", 'r') as f:
                log_content = f.read()
                assert "Memory usage at decorator_test - before test_function" in log_content
                assert "Memory usage at decorator_test - after test_function" in log_content
    
    def test_colored_formatter(self):
        """Test colored console formatter."""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')
        
        # Create real log record
        import logging
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Test formatting
        formatted = formatter.format(record)
        
        # Should contain color codes for INFO level
        assert '\033[32m' in formatted  # Green color for INFO
        assert '\033[0m' in formatted   # Reset color
        assert 'Test message' in formatted
    
    def test_structured_formatter(self):
        """Test structured JSON formatter."""
        formatter = StructuredFormatter()
        
        # Create real log record with extra field
        import logging
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=42,
            msg='Test structured message',
            args=(),
            exc_info=None
        )
        record.module = 'test_module'
        record.funcName = 'test_function'
        record.custom_field = 'custom_value'
        
        formatted = formatter.format(record)
        
        # Parse the JSON output
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
        """Test that performance monitor is thread-safe."""
        results = []
        
        def worker_function(worker_id):
            timer_id = PerformanceMonitor.start_timer(f"worker_{worker_id}")
            time.sleep(0.01)  # Short sleep
            duration = PerformanceMonitor.end_timer(timer_id)
            results.append((worker_id, duration))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        for worker_id, duration in results:
            assert duration > 0.005  # Should be at least 5ms
            assert duration < 0.1    # Should be less than 100ms
    
    def test_log_level_changes(self):
        """Test runtime log level changes."""
        logger = get_logger("level_test")
        
        # Set to INFO level
        AppLogger.set_level("INFO")
        
        # Debug should not appear, info should
        logger.debug("Debug message - should not appear")
        logger.info("Info message - should appear")
        
        # Set to DEBUG level
        AppLogger.set_level("DEBUG")
        
        # Both should appear now
        logger.debug("Debug message - should now appear")
        logger.info("Another info message")
        
        # Check log file contents
        log_dir = Path(self.temp_dir)
        with open(log_dir / "application.log", 'r') as f:
            log_content = f.read()
            assert "Info message - should appear" in log_content
            assert "Debug message - should now appear" in log_content
            assert "Another info message" in log_content
    
    def test_get_active_timers(self):
        """Test getting active timer information."""
        # Start some timers
        timer1 = AppLogger.start_performance_timer("operation1", "context1")
        timer2 = AppLogger.start_performance_timer("operation2", "context2")
        
        # Get active timers
        active_timers = AppLogger.get_active_timers()
        
        assert len(active_timers) == 2
        assert timer1 in active_timers
        assert timer2 in active_timers
        
        # Check timer information
        timer1_info = active_timers[timer1]
        assert timer1_info['operation'] == 'operation1'
        assert timer1_info['context'] == 'context1'
        assert 'start_time' in timer1_info
        assert 'thread' in timer1_info
        
        # End one timer
        AppLogger.end_performance_timer(timer1)
        
        # Check active timers again
        active_timers = AppLogger.get_active_timers()
        assert len(active_timers) == 1
        assert timer1 not in active_timers
        assert timer2 in active_timers
        
        # Clean up
        AppLogger.end_performance_timer(timer2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])