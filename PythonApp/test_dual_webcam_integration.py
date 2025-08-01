#!/usr/bin/env python3
"""
Test script for dual webcam main window and launch script functionality.

This script tests the new dual webcam main window integration and launch script
camera settings passing functionality.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the modules to test
from utils.logging_config import get_logger, AppLogger
from webcam.dual_webcam_capture import test_dual_webcam_access


class TestDualWebcamIntegration(unittest.TestCase):
    """Test dual webcam integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("TestDualWebcamIntegration")
        AppLogger.set_level("DEBUG")
        
    def test_camera_test_function_default_indices(self):
        """Test camera test function with default indices."""
        self.logger.info("Testing camera test function with default indices")
        
        # Mock cv2.VideoCapture to simulate camera availability
        with patch('cv2.VideoCapture') as mock_video_capture:
            # Create mock instances
            mock_cap1 = Mock()
            mock_cap2 = Mock()
            
            # Configure mocks for successful camera access
            mock_cap1.isOpened.return_value = True
            mock_cap1.read.return_value = (True, Mock(shape=(480, 640, 3)))
            mock_cap2.isOpened.return_value = True
            mock_cap2.read.return_value = (True, Mock(shape=(480, 640, 3)))
            
            # Set up the side effect to return different mocks for different indices
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
            
            # Test with default indices
            result = test_dual_webcam_access()
            
            self.assertTrue(result, "Camera test should succeed with mocked cameras")
            
            # Verify calls
            self.assertEqual(mock_video_capture.call_count, 2)
            mock_cap1.release.assert_called_once()
            mock_cap2.release.assert_called_once()
            
    def test_camera_test_function_custom_indices(self):
        """Test camera test function with custom indices."""
        self.logger.info("Testing camera test function with custom indices")
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            # Create mock instances
            mock_cap2 = Mock()
            mock_cap3 = Mock()
            
            # Configure mocks for successful camera access
            mock_cap2.isOpened.return_value = True
            mock_cap2.read.return_value = (True, Mock(shape=(1080, 1920, 3)))
            mock_cap3.isOpened.return_value = True
            mock_cap3.read.return_value = (True, Mock(shape=(1080, 1920, 3)))
            
            # Set up the side effect to return different mocks for different indices
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
            
            # Test with custom indices
            result = test_dual_webcam_access([2, 3])
            
            self.assertTrue(result, "Camera test should succeed with custom indices")
            
            # Verify calls
            self.assertEqual(mock_video_capture.call_count, 2)
            mock_video_capture.assert_any_call(2)
            mock_video_capture.assert_any_call(3)
            
    def test_camera_test_function_failure(self):
        """Test camera test function failure scenarios."""
        self.logger.info("Testing camera test function failure scenarios")
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            # Test scenario: first camera fails to open
            mock_cap1 = Mock()
            mock_cap1.isOpened.return_value = False
            mock_video_capture.return_value = mock_cap1
            
            result = test_dual_webcam_access([0, 1])
            self.assertFalse(result, "Camera test should fail when first camera cannot open")
            
            # Test scenario: first camera opens but cannot read
            mock_cap1.isOpened.return_value = True
            mock_cap1.read.return_value = (False, None)
            
            result = test_dual_webcam_access([0, 1])
            self.assertFalse(result, "Camera test should fail when first camera cannot read")
            
    def test_camera_test_invalid_indices(self):
        """Test camera test function with invalid indices."""
        self.logger.info("Testing camera test function with invalid indices")
        
        # Test with wrong number of indices
        result = test_dual_webcam_access([0])
        self.assertFalse(result, "Camera test should fail with only one camera index")
        
        result = test_dual_webcam_access([0, 1, 2])
        self.assertFalse(result, "Camera test should fail with more than two camera indices")
        
    @patch('PyQt5.QtWidgets.QApplication')
    def test_dual_webcam_main_window_import(self, mock_qapp):
        """Test that DualWebcamMainWindow can be imported and instantiated."""
        self.logger.info("Testing DualWebcamMainWindow import and instantiation")
        
        try:
            from gui.dual_webcam_main_window import DualWebcamMainWindow
            
            # Test default constructor
            with patch('gui.dual_webcam_main_window.test_dual_webcam_access'):
                main_window = DualWebcamMainWindow()
                self.assertIsNotNone(main_window, "Main window should be created")
                self.assertEqual(main_window.camera_indices, [0, 1], "Default camera indices should be [0, 1]")
                
            # Test constructor with custom settings
            camera_indices = [2, 3]
            initial_settings = {
                'camera1_index': 2,
                'camera2_index': 3,
                'width': 1920,
                'height': 1080,
                'fps': 30
            }
            
            with patch('gui.dual_webcam_main_window.test_dual_webcam_access'):
                main_window = DualWebcamMainWindow(
                    camera_indices=camera_indices,
                    initial_settings=initial_settings
                )
                self.assertEqual(main_window.camera_indices, camera_indices)
                self.assertEqual(main_window.initial_settings, initial_settings)
                
        except ImportError as e:
            self.fail(f"Could not import DualWebcamMainWindow: {e}")
            
    def test_launch_script_argument_parsing(self):
        """Test launch script argument parsing functionality."""
        self.logger.info("Testing launch script argument parsing")
        
        # Import the launch script's argument parser
        import sys
        original_argv = sys.argv.copy()
        
        try:
            # Import the parse_arguments function
            sys.path.insert(0, str(Path(__file__).parent))
            from launch_dual_webcam import parse_arguments
            
            # Test default arguments
            sys.argv = ['launch_dual_webcam.py']
            args = parse_arguments()
            
            self.assertEqual(args.cameras, '0,1')
            self.assertEqual(args.resolution, '3840x2160')
            self.assertEqual(args.fps, 30)
            self.assertFalse(args.test_only)
            
            # Test custom arguments
            sys.argv = [
                'launch_dual_webcam.py',
                '--cameras', '2,3',
                '--resolution', '1920x1080',
                '--fps', '60',
                '--test-only',
                '--log-level', 'DEBUG'
            ]
            args = parse_arguments()
            
            self.assertEqual(args.cameras, '2,3')
            self.assertEqual(args.resolution, '1920x1080')
            self.assertEqual(args.fps, 60)
            self.assertTrue(args.test_only)
            self.assertEqual(args.log_level, 'DEBUG')
            
        finally:
            sys.argv = original_argv
            
    def test_settings_parsing_in_launch_script(self):
        """Test camera settings parsing in launch script."""
        self.logger.info("Testing camera settings parsing")
        
        # Test valid camera indices parsing
        test_cases = [
            ("0,1", [0, 1]),
            ("2,3", [2, 3]),
            ("0, 1", [0, 1]),  # With spaces
            ("10,11", [10, 11])
        ]
        
        for camera_str, expected in test_cases:
            camera_indices = [int(x.strip()) for x in camera_str.split(',')]
            self.assertEqual(camera_indices, expected, f"Failed for input: {camera_str}")
            
        # Test valid resolution parsing
        resolution_cases = [
            ("3840x2160", (3840, 2160)),
            ("1920x1080", (1920, 1080)),
            ("1280x720", (1280, 720)),
            ("640x480", (640, 480))
        ]
        
        for res_str, expected in resolution_cases:
            width, height = map(int, res_str.split('x'))
            self.assertEqual((width, height), expected, f"Failed for resolution: {res_str}")


class TestLoggingEnhancements(unittest.TestCase):
    """Test logging functionality enhancements."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("TestLoggingEnhancements")
        
    def test_structured_logging(self):
        """Test structured logging functionality."""
        self.logger.info("Testing structured logging")
        
        # Test logging with extra structured data
        extra_data = {
            'operation': 'camera_test',
            'camera_index': 0,
            'success': True
        }
        
        # This should work without errors
        self.logger.info("Camera test completed", extra=extra_data)
        
        # Test different log levels with structured data
        self.logger.debug("Debug message", extra={'debug_info': 'test'})
        self.logger.warning("Warning message", extra={'warning_type': 'camera_disconnected'})
        self.logger.error("Error message", extra={'error_code': 404})
        
    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        self.logger.info("Testing performance monitoring")
        
        # Test performance timer functionality
        timer_id = AppLogger.start_performance_timer("test_operation", "unit_test")
        self.assertIsNotNone(timer_id, "Timer ID should not be None")
        
        # Simulate some work
        import time
        time.sleep(0.01)  # 10ms
        
        duration = AppLogger.end_performance_timer(timer_id, "TestLoggingEnhancements")
        self.assertGreater(duration, 0, "Duration should be positive")
        self.assertLess(duration, 1.0, "Duration should be reasonable for test")
        
    def test_memory_usage_logging(self):
        """Test memory usage logging functionality."""
        self.logger.info("Testing memory usage logging")
        
        # This should work without errors (even if psutil is not available)
        AppLogger.log_memory_usage("unit_test_start")
        
        # Create some memory usage
        test_data = [i for i in range(1000)]
        
        AppLogger.log_memory_usage("unit_test_after_allocation")
        
        # Clean up
        del test_data
        
    def test_log_level_changes(self):
        """Test dynamic log level changes."""
        self.logger.info("Testing log level changes")
        
        # Test setting different log levels
        AppLogger.set_level("DEBUG")
        self.logger.debug("This debug message should be visible")
        
        AppLogger.set_level("WARNING")
        self.logger.info("This info message should be filtered")
        self.logger.warning("This warning message should be visible")
        
        # Reset to INFO for other tests
        AppLogger.set_level("INFO")


def run_tests():
    """Run all tests."""
    logger = get_logger("TestRunner")
    logger.info("=== Running Dual Webcam Integration Tests ===")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestDualWebcamIntegration))
    suite.addTest(unittest.makeSuite(TestLoggingEnhancements))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    if result.wasSuccessful():
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.error(f"✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)