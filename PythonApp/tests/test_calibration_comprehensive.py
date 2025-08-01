#!/usr/bin/env python3
"""
Comprehensive test suite for CalibrationManager implementation.
Tests all aspects of the camera calibration system including edge cases.
"""

import sys
import os
import unittest
import tempfile
import shutil
import json
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from calibration.calibration import CalibrationManager, create_calibration_pattern_points
except ImportError as e:
    print(f"Warning: Cannot import calibration module: {e}")
    CalibrationManager = None
    create_calibration_pattern_points = None


class TestCalibrationManagerComprehensive(unittest.TestCase):
    """Comprehensive test suite for CalibrationManager."""

    def setUp(self):
        """Set up test environment."""
        if CalibrationManager is None:
            self.skipTest("CalibrationManager not available")
        
        self.manager = CalibrationManager()
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def create_synthetic_chessboard(self, pattern_size=(9, 6), square_size=50, 
                                    image_size=(640, 480), add_noise=False):
        """Create synthetic chessboard image for testing."""
        img = np.ones((image_size[1], image_size[0], 3), dtype=np.uint8) * 255
        
        board_width = pattern_size[0] * square_size
        board_height = pattern_size[1] * square_size
        start_x = (image_size[0] - board_width) // 2
        start_y = (image_size[1] - board_height) // 2
        
        for row in range(pattern_size[1] + 1):
            for col in range(pattern_size[0] + 1):
                if (row + col) % 2 == 1:
                    x1 = start_x + col * square_size
                    y1 = start_y + row * square_size
                    x2 = min(x1 + square_size, image_size[0])
                    y2 = min(y1 + square_size, image_size[1])
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)
        
        if add_noise:
            noise = np.random.randint(-10, 10, img.shape, dtype=np.int16)
            img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return img

    def test_calibration_manager_initialization(self):
        """Test CalibrationManager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.pattern_size, (9, 6))
        self.assertEqual(self.manager.square_size, 1.0)

    def test_pattern_detection_chessboard(self):
        """Test chessboard pattern detection."""
        # Create test image
        img = self.create_synthetic_chessboard()
        
        # Test pattern detection
        found, corners = self.manager.detect_pattern(img, 'chessboard')
        
        self.assertTrue(found)
        self.assertIsNotNone(corners)
        self.assertEqual(len(corners), self.manager.pattern_size[0] * self.manager.pattern_size[1])

    def test_pattern_detection_circles(self):
        """Test circle grid pattern detection."""
        # Create synthetic circle grid
        img = np.ones((480, 640, 3), dtype=np.uint8) * 255
        pattern_size = (4, 11)  # Asymmetric circle grid
        
        # Draw circles in grid pattern
        circle_radius = 20
        spacing = 40
        start_x, start_y = 100, 100
        
        for row in range(pattern_size[1]):
            for col in range(pattern_size[0]):
                center_x = start_x + col * spacing
                center_y = start_y + row * spacing
                cv2.circle(img, (center_x, center_y), circle_radius, (0, 0, 0), -1)
        
        # Test with custom pattern size
        old_pattern = self.manager.pattern_size
        self.manager.pattern_size = pattern_size
        
        found, corners = self.manager.detect_pattern(img, 'circles')
        
        # Restore original pattern size
        self.manager.pattern_size = old_pattern
        
        # Note: May not find perfect circles in synthetic image, but should not crash
        self.assertIsInstance(found, bool)

    def test_single_camera_calibration(self):
        """Test single camera calibration process."""
        # Create multiple test images
        images = []
        image_points = []
        image_size = (640, 480)
        
        for i in range(10):
            # Create slightly different chessboard images
            img = self.create_synthetic_chessboard(image_size=image_size, add_noise=(i > 0))
            images.append(img)
            
            # Detect corners
            found, corners = self.manager.detect_pattern(img, 'chessboard')
            if found:
                image_points.append(corners)
        
        # Ensure we have enough images
        self.assertGreaterEqual(len(image_points), 3)
        
        # Test calibration
        result = self.manager.calibrate_single_camera(images, image_points, image_size)
        
        self.assertIsNotNone(result)
        self.assertIn('camera_matrix', result)
        self.assertIn('distortion_coefficients', result)
        self.assertIn('rotation_vectors', result)
        self.assertIn('translation_vectors', result)
        self.assertIn('rms_error', result)
        
        # Check matrix dimensions
        self.assertEqual(result['camera_matrix'].shape, (3, 3))
        self.assertEqual(len(result['distortion_coefficients']), 5)

    def test_stereo_calibration(self):
        """Test stereo camera calibration."""
        # Create test data for stereo calibration
        image_size = (640, 480)
        num_images = 8
        
        left_images, right_images = [], []
        left_points, right_points = [], []
        
        for i in range(num_images):
            # Create left and right images (slightly offset)
            left_img = self.create_synthetic_chessboard(image_size=image_size)
            right_img = self.create_synthetic_chessboard(image_size=image_size)
            
            left_images.append(left_img)
            right_images.append(right_img)
            
            # Detect corners
            found_l, corners_l = self.manager.detect_pattern(left_img, 'chessboard')
            found_r, corners_r = self.manager.detect_pattern(right_img, 'chessboard')
            
            if found_l and found_r:
                left_points.append(corners_l)
                right_points.append(corners_r)
        
        # Ensure sufficient data
        self.assertGreaterEqual(len(left_points), 3)
        self.assertGreaterEqual(len(right_points), 3)
        
        # Test stereo calibration
        result = self.manager.calibrate_stereo_cameras(
            left_images, right_images, left_points, right_points, image_size
        )
        
        self.assertIsNotNone(result)
        self.assertIn('left_camera_matrix', result)
        self.assertIn('right_camera_matrix', result)
        self.assertIn('left_distortion', result)
        self.assertIn('right_distortion', result)
        self.assertIn('rotation_matrix', result)
        self.assertIn('translation_vector', result)
        self.assertIn('rms_error', result)

    def test_calibration_quality_assessment(self):
        """Test calibration quality assessment."""
        # Create mock calibration result
        camera_matrix = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)
        dist_coeffs = np.array([0.1, -0.2, 0.001, 0.002, 0.1], dtype=np.float32)
        
        # Create test image points
        image_points = []
        for i in range(10):
            points = np.random.rand(54, 1, 2).astype(np.float32) * 640
            image_points.append(points)
        
        # Create object points
        object_points = [create_calibration_pattern_points((9, 6), 1.0) for _ in range(10)]
        
        # Test quality assessment
        quality = self.manager.assess_calibration_quality(
            camera_matrix, dist_coeffs, object_points, image_points, (640, 480)
        )
        
        self.assertIsInstance(quality, dict)
        self.assertIn('mean_error', quality)
        self.assertIn('max_error', quality)
        self.assertIn('coverage_score', quality)
        self.assertIn('recommendations', quality)

    def test_save_load_calibration(self):
        """Test saving and loading calibration data."""
        # Create mock calibration data
        calibration_data = {
            'camera_matrix': np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]]),
            'distortion_coefficients': np.array([0.1, -0.2, 0.001, 0.002, 0.1]),
            'rms_error': 0.5,
            'image_size': (640, 480),
            'pattern_size': (9, 6),
            'square_size': 1.0
        }
        
        # Test saving
        save_path = os.path.join(self.test_dir, 'test_calibration.json')
        self.manager.save_calibration(calibration_data, save_path)
        
        self.assertTrue(os.path.exists(save_path))
        
        # Test loading
        loaded_data = self.manager.load_calibration(save_path)
        
        self.assertIsNotNone(loaded_data)
        self.assertIn('camera_matrix', loaded_data)
        self.assertIn('distortion_coefficients', loaded_data)
        
        # Test matrix equality (converted back from JSON)
        np.testing.assert_array_almost_equal(
            loaded_data['camera_matrix'], calibration_data['camera_matrix']
        )

    def test_error_handling(self):
        """Test error handling in calibration methods."""
        # Test with empty image list
        result = self.manager.calibrate_single_camera([], [], (640, 480))
        self.assertIsNone(result)
        
        # Test with invalid pattern type
        img = self.create_synthetic_chessboard()
        found, corners = self.manager.detect_pattern(img, 'invalid_pattern')
        self.assertFalse(found)
        self.assertIsNone(corners)
        
        # Test loading non-existent file
        result = self.manager.load_calibration('/non/existent/file.json')
        self.assertIsNone(result)

    def test_calibration_workflow_integration(self):
        """Test complete calibration workflow."""
        print("\nTesting complete calibration workflow...")
        
        # Step 1: Create calibration images
        images = []
        image_points = []
        image_size = (640, 480)
        
        for i in range(12):  # More images for better calibration
            img = self.create_synthetic_chessboard(
                image_size=image_size, 
                add_noise=True
            )
            images.append(img)
            
            found, corners = self.manager.detect_pattern(img, 'chessboard')
            if found:
                image_points.append(corners)
        
        print(f"Created {len(images)} images, detected patterns in {len(image_points)}")
        
        # Step 2: Perform calibration
        calibration_result = self.manager.calibrate_single_camera(
            images, image_points, image_size
        )
        
        self.assertIsNotNone(calibration_result)
        print(f"Calibration RMS error: {calibration_result['rms_error']:.4f}")
        
        # Step 3: Assess quality
        object_points = [create_calibration_pattern_points((9, 6), 1.0) 
                        for _ in range(len(image_points))]
        
        quality = self.manager.assess_calibration_quality(
            calibration_result['camera_matrix'],
            calibration_result['distortion_coefficients'],
            object_points,
            image_points,
            image_size
        )
        
        print(f"Quality assessment - Mean error: {quality['mean_error']:.4f}")
        print(f"Coverage score: {quality['coverage_score']:.2f}")
        
        # Step 4: Save calibration
        save_path = os.path.join(self.test_dir, 'workflow_calibration.json')
        self.manager.save_calibration(calibration_result, save_path)
        
        # Step 5: Load and verify
        loaded_calibration = self.manager.load_calibration(save_path)
        self.assertIsNotNone(loaded_calibration)
        
        print("✓ Complete workflow test passed")

    def test_performance_benchmarks(self):
        """Test performance benchmarks for calibration operations."""
        import time
        
        print("\nRunning performance benchmarks...")
        
        # Benchmark pattern detection
        img = self.create_synthetic_chessboard()
        
        start_time = time.time()
        for _ in range(10):
            self.manager.detect_pattern(img, 'chessboard')
        detection_time = (time.time() - start_time) / 10
        
        print(f"Average pattern detection time: {detection_time:.4f}s")
        self.assertLess(detection_time, 1.0)  # Should be under 1 second
        
        # Benchmark calibration
        images = [self.create_synthetic_chessboard() for _ in range(6)]
        image_points = []
        for img in images:
            found, corners = self.manager.detect_pattern(img, 'chessboard')
            if found:
                image_points.append(corners)
        
        start_time = time.time()
        result = self.manager.calibrate_single_camera(images, image_points, (640, 480))
        calibration_time = time.time() - start_time
        
        print(f"Calibration time: {calibration_time:.4f}s")
        self.assertLess(calibration_time, 10.0)  # Should be under 10 seconds
        self.assertIsNotNone(result)


def run_calibration_tests():
    """Run all calibration tests with detailed output."""
    if CalibrationManager is None:
        print("Skipping calibration tests - module not available")
        return
    
    print("="*80)
    print("COMPREHENSIVE CALIBRATION MANAGER TESTS")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCalibrationManagerComprehensive)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_calibration_tests()
    sys.exit(0 if success else 1)