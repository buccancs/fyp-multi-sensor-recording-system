#!/usr/bin/env python3
"""
Comprehensive Calibration Module Tests
=====================================

This module provides comprehensive unit tests for all calibration-related
functionality in the PythonApp.

Test coverage:
- CalibrationManager: Session management, calibration orchestration
- CalibrationProcessor: Image processing, pattern detection, parameter calculation
- CalibrationResult: Data validation, serialization, persistence
- Calibration integration: End-to-end calibration workflows

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from calibration.calibration_manager import CalibrationManager
    from calibration.calibration_processor import CalibrationProcessor  
    from calibration.calibration_result import CalibrationResult
    from calibration.calibration import create_calibration_pattern_points
    CALIBRATION_MODULES_AVAILABLE = True
except ImportError as e:
    CALIBRATION_MODULES_AVAILABLE = False
    print(f"Warning: Calibration modules not available: {e}")


class TestCalibrationResult(unittest.TestCase):
    """Test CalibrationResult data handling and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.sample_calibration_data = {
            'camera_matrix': [[1000.0, 0.0, 320.0], [0.0, 1000.0, 240.0], [0.0, 0.0, 1.0]],
            'distortion_coefficients': [0.1, -0.2, 0.0, 0.0, 0.0],
            'rms_error': 0.45,
            'image_size': [640, 480],
            'timestamp': '2025-01-16T12:00:00.000Z',
            'pattern_size': [9, 6],
            'square_size': 25.0,
            'num_images': 10
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_result_creation(self):
        """Test CalibrationResult creation and validation."""
        result = CalibrationResult(**self.sample_calibration_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.rms_error, 0.45)
        self.assertEqual(result.image_size, [640, 480])
        self.assertEqual(result.num_images, 10)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_result_validation(self):
        """Test CalibrationResult input validation."""
        # Test invalid camera matrix
        invalid_data = self.sample_calibration_data.copy()
        invalid_data['camera_matrix'] = [[1000.0, 0.0], [0.0, 1000.0]]  # Wrong dimensions
        
        with self.assertRaises((ValueError, TypeError)):
            CalibrationResult(**invalid_data)

        # Test negative RMS error
        invalid_data = self.sample_calibration_data.copy()
        invalid_data['rms_error'] = -0.5
        
        with self.assertRaises(ValueError):
            CalibrationResult(**invalid_data)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_result_serialization(self):
        """Test CalibrationResult JSON serialization."""
        result = CalibrationResult(**self.sample_calibration_data)
        
        # Test to dict conversion
        result_dict = result.to_dict()
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['rms_error'], 0.45)
        
        # Test JSON serialization
        json_str = result.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        loaded_data = json.loads(json_str)
        self.assertEqual(loaded_data['rms_error'], 0.45)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_result_file_operations(self):
        """Test CalibrationResult file save/load operations."""
        result = CalibrationResult(**self.sample_calibration_data)
        
        # Test save to file
        save_path = self.test_dir / "test_calibration.json"
        result.save_to_file(str(save_path))
        
        self.assertTrue(save_path.exists())
        
        # Test load from file
        loaded_result = CalibrationResult.load_from_file(str(save_path))
        self.assertEqual(loaded_result.rms_error, result.rms_error)
        self.assertEqual(loaded_result.image_size, result.image_size)


class TestCalibrationProcessor(unittest.TestCase):
    """Test CalibrationProcessor image processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(CV2_AVAILABLE and CALIBRATION_MODULES_AVAILABLE, 
                        "OpenCV and calibration modules required")
    def test_calibration_processor_initialization(self):
        """Test CalibrationProcessor initialization."""
        processor = CalibrationProcessor(pattern_size=(9, 6), square_size=25.0)
        
        self.assertEqual(processor.pattern_size, (9, 6))
        self.assertEqual(processor.square_size, 25.0)
        self.assertIsNotNone(processor.object_points)

    @unittest.skipUnless(CV2_AVAILABLE and CALIBRATION_MODULES_AVAILABLE,
                        "OpenCV and calibration modules required") 
    def test_pattern_detection(self):
        """Test chessboard pattern detection."""
        processor = CalibrationProcessor(pattern_size=(9, 6), square_size=25.0)
        
        # Create synthetic chessboard image
        image = self._create_synthetic_chessboard(640, 480, (9, 6), 40)
        
        # Test pattern detection
        found, corners = processor.detect_pattern(image)
        
        self.assertTrue(found)
        self.assertIsNotNone(corners)
        self.assertEqual(len(corners), 9 * 6)  # 54 corners for 9x6 pattern

    @unittest.skipUnless(CV2_AVAILABLE and CALIBRATION_MODULES_AVAILABLE,
                        "OpenCV and calibration modules required")
    def test_calibration_calculation(self):
        """Test camera calibration calculation."""
        processor = CalibrationProcessor(pattern_size=(9, 6), square_size=25.0)
        
        # Generate multiple synthetic calibration images
        images = []
        image_points = []
        image_size = (640, 480)
        
        for i in range(10):
            # Create slightly different images to avoid singularity
            img = self._create_synthetic_chessboard(640, 480, (9, 6), 40 + i)
            images.append(img)
            
            found, corners = processor.detect_pattern(img)
            if found:
                image_points.append(corners)
        
        # Ensure we have enough valid images
        self.assertGreaterEqual(len(image_points), 5)
        
        # Test calibration calculation
        result = processor.calibrate_camera(images, image_points, image_size)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CalibrationResult)
        self.assertLess(result.rms_error, 5.0)  # Should be reasonable for synthetic data
        self.assertEqual(result.image_size, list(image_size))

    @unittest.skipUnless(CV2_AVAILABLE and CALIBRATION_MODULES_AVAILABLE,
                        "OpenCV and calibration modules required")
    def test_stereo_calibration(self):
        """Test stereo camera calibration."""
        processor = CalibrationProcessor(pattern_size=(9, 6), square_size=25.0)
        
        # Generate synthetic stereo images
        left_images = []
        right_images = []
        left_points = []
        right_points = []
        image_size = (640, 480)
        
        for i in range(8):
            # Create left and right images with slight offset
            left_img = self._create_synthetic_chessboard(640, 480, (9, 6), 40 + i)
            right_img = self._create_synthetic_chessboard(640, 480, (9, 6), 40 + i, offset_x=50)
            
            left_images.append(left_img)
            right_images.append(right_img)
            
            left_found, left_corners = processor.detect_pattern(left_img)
            right_found, right_corners = processor.detect_pattern(right_img)
            
            if left_found and right_found:
                left_points.append(left_corners)
                right_points.append(right_corners)
        
        # Ensure we have enough valid stereo pairs
        self.assertGreaterEqual(len(left_points), 5)
        
        # Test stereo calibration
        stereo_result = processor.calibrate_stereo_cameras(
            left_images, right_images, left_points, right_points, image_size
        )
        
        self.assertIsNotNone(stereo_result)
        self.assertIn('left_camera', stereo_result)
        self.assertIn('right_camera', stereo_result)
        self.assertIn('stereo_params', stereo_result)

    def _create_synthetic_chessboard(self, width, height, pattern_size, square_size, offset_x=0):
        """Create a synthetic chessboard image for testing."""
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        rows, cols = pattern_size[1] + 1, pattern_size[0] + 1
        board_width = cols * square_size
        board_height = rows * square_size
        
        # Center the board with optional offset
        start_x = (width - board_width) // 2 + offset_x
        start_y = (height - board_height) // 2
        
        # Draw chessboard pattern
        for row in range(rows):
            for col in range(cols):
                if (row + col) % 2 == 1:  # Black squares
                    x1 = start_x + col * square_size
                    y1 = start_y + row * square_size
                    x2 = min(x1 + square_size, width)
                    y2 = min(y1 + square_size, height)
                    
                    if x1 >= 0 and y1 >= 0 and x2 <= width and y2 <= height:
                        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), -1)
        
        return image


class TestCalibrationManager(unittest.TestCase):
    """Test CalibrationManager orchestration and session management."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_manager_initialization(self):
        """Test CalibrationManager initialization."""
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        self.assertEqual(manager.base_directory, str(self.test_dir))
        self.assertIsNotNone(manager.session_id)
        self.assertTrue(Path(manager.calibration_directory).exists())

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_session_management(self):
        """Test calibration session creation and management."""
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        # Test session creation
        session_info = manager.create_calibration_session("test_session")
        self.assertIsNotNone(session_info)
        self.assertIn('session_id', session_info)
        self.assertIn('directory', session_info)
        
        # Test session directory creation
        session_dir = Path(session_info['directory'])
        self.assertTrue(session_dir.exists())

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_workflow(self):
        """Test complete calibration workflow orchestration."""
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        # Start calibration session
        session_info = manager.create_calibration_session("workflow_test")
        
        # Mock calibration processor
        with patch.object(manager, 'processor') as mock_processor:
            mock_result = Mock(spec=CalibrationResult)
            mock_result.rms_error = 0.5
            mock_result.to_dict.return_value = {'rms_error': 0.5}
            mock_processor.calibrate_camera.return_value = mock_result
            
            # Test workflow execution
            result = manager.run_calibration_workflow([])  # Empty image list for test
            
            self.assertIsNotNone(result)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_persistence(self):
        """Test calibration result persistence and retrieval."""
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        # Create mock calibration result
        mock_result = Mock(spec=CalibrationResult)
        mock_result.to_dict.return_value = {
            'rms_error': 0.5,
            'image_size': [640, 480],
            'timestamp': '2025-01-16T12:00:00.000Z'
        }
        
        # Test save calibration
        save_path = manager.save_calibration_result(mock_result, "test_calibration")
        self.assertTrue(Path(save_path).exists())
        
        # Test load calibration
        loaded_result = manager.load_calibration_result("test_calibration")
        self.assertIsNotNone(loaded_result)

    @unittest.skipUnless(CALIBRATION_MODULES_AVAILABLE, "Calibration modules not available")
    def test_calibration_validation(self):
        """Test calibration result validation and quality checks."""
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        # Test good calibration
        good_result = Mock(spec=CalibrationResult)
        good_result.rms_error = 0.3
        good_result.num_images = 15
        
        validation = manager.validate_calibration_quality(good_result)
        self.assertTrue(validation['is_valid'])
        self.assertIn('quality_score', validation)
        
        # Test poor calibration
        poor_result = Mock(spec=CalibrationResult)
        poor_result.rms_error = 2.0
        poor_result.num_images = 3
        
        validation = manager.validate_calibration_quality(poor_result)
        self.assertFalse(validation['is_valid'])
        self.assertIn('issues', validation)


class TestCalibrationIntegration(unittest.TestCase):
    """Test end-to-end calibration integration scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(CV2_AVAILABLE and CALIBRATION_MODULES_AVAILABLE,
                        "Full calibration stack required")
    def test_complete_calibration_pipeline(self):
        """Test complete calibration pipeline from images to result."""
        # Create calibration manager
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        # Generate synthetic calibration dataset
        images = []
        pattern_size = (9, 6)
        square_size = 25.0
        
        for i in range(12):
            img = self._create_test_chessboard(640, 480, pattern_size, 40 + i * 2)
            
            # Save image to test directory
            img_path = self.test_dir / f"calib_{i:02d}.png"
            cv2.imwrite(str(img_path), img)
            images.append(str(img_path))
        
        # Run complete calibration pipeline
        session_info = manager.create_calibration_session("pipeline_test")
        
        # Process calibration
        result = manager.run_calibration_from_images(images, pattern_size, square_size)
        
        # Validate results
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CalibrationResult)
        self.assertLess(result.rms_error, 1.0)  # Should be good for synthetic data
        self.assertEqual(result.pattern_size, list(pattern_size))
        self.assertEqual(result.square_size, square_size)
        self.assertGreaterEqual(result.num_images, 8)  # Should detect most patterns

    @unittest.skipUnless(CV2_AVAILABLE and CALIBRATION_MODULES_AVAILABLE,
                        "Full calibration stack required")
    def test_calibration_error_handling(self):
        """Test calibration error handling and recovery."""
        manager = CalibrationManager(base_directory=str(self.test_dir))
        
        # Test with insufficient images
        few_images = []
        for i in range(2):  # Too few images
            img = self._create_test_chessboard(640, 480, (9, 6), 40 + i * 10)
            img_path = self.test_dir / f"few_{i}.png"
            cv2.imwrite(str(img_path), img)
            few_images.append(str(img_path))
        
        # Should handle insufficient images gracefully
        result = manager.run_calibration_from_images(few_images, (9, 6), 25.0)
        self.assertIsNone(result)  # Should return None for insufficient data
        
        # Test with no valid patterns
        noise_images = []
        for i in range(5):
            # Create noise images with no chessboard
            noise_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            img_path = self.test_dir / f"noise_{i}.png"
            cv2.imwrite(str(img_path), noise_img)
            noise_images.append(str(img_path))
        
        # Should handle no detected patterns gracefully
        result = manager.run_calibration_from_images(noise_images, (9, 6), 25.0)
        self.assertIsNone(result)

    def _create_test_chessboard(self, width, height, pattern_size, square_size):
        """Create a synthetic chessboard for testing."""
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        rows, cols = pattern_size[1] + 1, pattern_size[0] + 1
        board_width = cols * square_size
        board_height = rows * square_size
        
        start_x = (width - board_width) // 2
        start_y = (height - board_height) // 2
        
        for row in range(rows):
            for col in range(cols):
                if (row + col) % 2 == 1:
                    x1 = start_x + col * square_size
                    y1 = start_y + row * square_size
                    x2 = min(x1 + square_size, width)
                    y2 = min(y1 + square_size, height)
                    
                    if x1 >= 0 and y1 >= 0 and x2 <= width and y2 <= height:
                        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), -1)
        
        return image


def run_calibration_tests():
    """Run all calibration tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestCalibrationResult,
        TestCalibrationProcessor, 
        TestCalibrationManager,
        TestCalibrationIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("COMPREHENSIVE CALIBRATION MODULE TESTS")
    print("=" * 70)
    
    if not CALIBRATION_MODULES_AVAILABLE:
        print("❌ Calibration modules not available - skipping tests")
        exit(1)
    
    if not CV2_AVAILABLE:
        print("⚠️  OpenCV not available - some tests will be skipped")
    
    success = run_calibration_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL CALIBRATION TESTS PASSED")
        exit(0)
    else:
        print("❌ SOME CALIBRATION TESTS FAILED")
        exit(1)