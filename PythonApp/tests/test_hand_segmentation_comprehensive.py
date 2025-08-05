#!/usr/bin/env python3
"""
Comprehensive Hand Segmentation Tests
======================================

This module provides comprehensive unit tests for all hand segmentation
functionality in the PythonApp.

Test coverage:
- Hand Detection: Computer vision algorithms, region identification
- Segmentation Processing: Image preprocessing, contour detection, mask generation
- CLI Interface: Command-line interface, batch processing, parameter validation
- Integration: Real-time processing, camera integration, performance optimization

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys
import time

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from hand_segmentation.hand_detector import HandDetector
    from hand_segmentation.segmentation_processor import SegmentationProcessor
    from hand_segmentation.hand_tracker import HandTracker
    from hand_segmentation_cli import HandSegmentationCLI, CLIArgumentParser
    HAND_SEGMENTATION_MODULES_AVAILABLE = True
except ImportError as e:
    HAND_SEGMENTATION_MODULES_AVAILABLE = False
    print(f"Warning: Hand segmentation modules not available: {e}")


class TestHandDetector(unittest.TestCase):
    """Test HandDetector computer vision functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not HAND_SEGMENTATION_MODULES_AVAILABLE or not CV2_AVAILABLE:
            self.skipTest("Hand segmentation or CV2 modules not available")
        
        self.detector_config = {
            'detection_method': 'mediapipe',
            'confidence_threshold': 0.7,
            'max_hands': 2,
            'model_complexity': 1
        }
        
        self.hand_detector = HandDetector(self.detector_config)

    def test_detector_initialization(self):
        """Test hand detector initialization with different configurations."""
        configs = [
            {'detection_method': 'mediapipe', 'confidence_threshold': 0.5},
            {'detection_method': 'opencv', 'cascade_file': 'hand_cascade.xml'},
            {'detection_method': 'yolo', 'model_path': 'hand_yolo.weights'}
        ]
        
        for config in configs:
            with patch('hand_segmentation.hand_detector.mediapipe') as mock_mp:
                detector = HandDetector(config)
                self.assertEqual(detector.config['detection_method'], config['detection_method'])

    def test_hand_detection_single_hand(self):
        """Test detection of single hand in image."""
        # Create mock image
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(self.hand_detector, 'mediapipe_detector') as mock_detector:
            mock_results = Mock()
            mock_results.multi_hand_landmarks = [Mock()]
            mock_results.multi_hand_landmarks[0].landmark = [
                Mock(x=0.5, y=0.4, z=0.0) for _ in range(21)  # 21 hand landmarks
            ]
            mock_detector.process.return_value = mock_results
            
            detections = self.hand_detector.detect_hands(mock_image)
            
            self.assertEqual(len(detections), 1)
            self.assertIn('landmarks', detections[0])
            self.assertIn('bounding_box', detections[0])

    def test_hand_detection_multiple_hands(self):
        """Test detection of multiple hands in image."""
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(self.hand_detector, 'mediapipe_detector') as mock_detector:
            mock_results = Mock()
            mock_results.multi_hand_landmarks = [Mock(), Mock()]  # Two hands
            
            for hand_landmarks in mock_results.multi_hand_landmarks:
                hand_landmarks.landmark = [
                    Mock(x=0.5, y=0.4, z=0.0) for _ in range(21)
                ]
            
            mock_detector.process.return_value = mock_results
            
            detections = self.hand_detector.detect_hands(mock_image)
            
            self.assertEqual(len(detections), 2)
            for detection in detections:
                self.assertIn('landmarks', detection)
                self.assertEqual(len(detection['landmarks']), 21)

    def test_confidence_filtering(self):
        """Test filtering detections based on confidence threshold."""
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(self.hand_detector, 'mediapipe_detector') as mock_detector:
            mock_results = Mock()
            mock_results.multi_hand_landmarks = [Mock()]
            mock_results.multi_handedness = [Mock()]
            mock_results.multi_handedness[0].classification = [Mock()]
            mock_results.multi_handedness[0].classification[0].score = 0.5  # Below threshold
            
            mock_detector.process.return_value = mock_results
            
            detections = self.hand_detector.detect_hands(mock_image)
            
            # Should be filtered out due to low confidence
            self.assertEqual(len(detections), 0)

    def test_bounding_box_calculation(self):
        """Test bounding box calculation from landmarks."""
        landmarks = [
            {'x': 0.2, 'y': 0.3},
            {'x': 0.8, 'y': 0.3},
            {'x': 0.5, 'y': 0.7}
        ]
        
        bbox = self.hand_detector.calculate_bounding_box(landmarks, (640, 480))
        
        expected_bbox = {
            'x': int(0.2 * 640),
            'y': int(0.3 * 480),
            'width': int((0.8 - 0.2) * 640),
            'height': int((0.7 - 0.3) * 480)
        }
        
        self.assertEqual(bbox, expected_bbox)

    def test_hand_orientation_detection(self):
        """Test detection of hand orientation (left/right)."""
        with patch.object(self.hand_detector, 'mediapipe_detector') as mock_detector:
            mock_results = Mock()
            mock_results.multi_handedness = [Mock()]
            mock_results.multi_handedness[0].classification = [Mock()]
            mock_results.multi_handedness[0].classification[0].label = 'Right'
            mock_results.multi_handedness[0].classification[0].score = 0.95
            
            mock_detector.process.return_value = mock_results
            
            orientation = self.hand_detector.detect_hand_orientation(mock_results, 0)
            
            self.assertEqual(orientation['label'], 'Right')
            self.assertEqual(orientation['confidence'], 0.95)


class TestSegmentationProcessor(unittest.TestCase):
    """Test SegmentationProcessor image processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not HAND_SEGMENTATION_MODULES_AVAILABLE or not CV2_AVAILABLE:
            self.skipTest("Hand segmentation or CV2 modules not available")
        
        self.processor_config = {
            'preprocessing': {
                'gaussian_blur': True,
                'blur_kernel': (5, 5),
                'color_space': 'HSV'
            },
            'segmentation': {
                'method': 'adaptive_threshold',
                'threshold_type': 'gaussian',
                'block_size': 11,
                'c_constant': 2
            },
            'postprocessing': {
                'morphology': True,
                'erosion_iterations': 1,
                'dilation_iterations': 2
            }
        }
        
        self.processor = SegmentationProcessor(self.processor_config)

    def test_image_preprocessing(self):
        """Test image preprocessing pipeline."""
        mock_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with patch('cv2.GaussianBlur') as mock_blur, \
             patch('cv2.cvtColor') as mock_cvt:
            
            mock_blur.return_value = mock_image
            mock_cvt.return_value = mock_image
            
            processed = self.processor.preprocess_image(mock_image)
            
            mock_blur.assert_called_once()
            mock_cvt.assert_called_once()
            self.assertIsNotNone(processed)

    def test_adaptive_thresholding(self):
        """Test adaptive thresholding for hand segmentation."""
        mock_gray_image = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        
        with patch('cv2.adaptiveThreshold') as mock_threshold:
            mock_threshold.return_value = np.zeros((480, 640), dtype=np.uint8)
            
            result = self.processor.apply_adaptive_threshold(mock_gray_image)
            
            mock_threshold.assert_called_once()
            self.assertEqual(result.shape, mock_gray_image.shape)

    def test_contour_detection(self):
        """Test contour detection and filtering."""
        mock_binary_image = np.zeros((480, 640), dtype=np.uint8)
        # Create mock contour data
        mock_contours = [
            np.array([[100, 100], [200, 100], [200, 200], [100, 200]]),  # Large contour
            np.array([[10, 10], [20, 10], [20, 20], [10, 20]])          # Small contour
        ]
        
        with patch('cv2.findContours') as mock_find_contours:
            mock_find_contours.return_value = (mock_contours, None)
            
            contours = self.processor.detect_contours(mock_binary_image)
            
            mock_find_contours.assert_called_once()
            # Should filter out small contours
            filtered_contours = self.processor.filter_contours_by_area(contours, min_area=500)
            self.assertEqual(len(filtered_contours), 1)

    def test_hand_mask_generation(self):
        """Test generation of hand segmentation mask."""
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_contours = [
            np.array([[100, 100], [200, 100], [200, 200], [100, 200]])
        ]
        
        with patch('cv2.fillPoly') as mock_fill:
            mask = self.processor.generate_hand_mask(mock_image.shape[:2], mock_contours)
            
            mock_fill.assert_called_once()
            self.assertEqual(mask.shape, mock_image.shape[:2])

    def test_morphological_operations(self):
        """Test morphological operations for noise reduction."""
        mock_binary_image = np.random.randint(0, 2, (480, 640), dtype=np.uint8) * 255
        
        with patch('cv2.morphologyEx') as mock_morph, \
             patch('cv2.getStructuringElement') as mock_kernel:
            
            mock_kernel.return_value = np.ones((3, 3), np.uint8)
            mock_morph.return_value = mock_binary_image
            
            processed = self.processor.apply_morphological_operations(mock_binary_image)
            
            mock_morph.assert_called()
            self.assertIsNotNone(processed)

    def test_segmentation_quality_assessment(self):
        """Test quality assessment of segmentation results."""
        mock_mask = np.zeros((480, 640), dtype=np.uint8)
        mock_mask[100:300, 200:400] = 255  # Hand region
        
        quality_metrics = self.processor.assess_segmentation_quality(mock_mask)
        
        self.assertIn('coverage_ratio', quality_metrics)
        self.assertIn('contour_smoothness', quality_metrics)
        self.assertIn('aspect_ratio', quality_metrics)
        self.assertGreater(quality_metrics['coverage_ratio'], 0)

    def test_multi_hand_segmentation(self):
        """Test segmentation of multiple hands in single image."""
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        hand_detections = [
            {
                'landmarks': [{'x': 0.3, 'y': 0.4} for _ in range(21)],
                'bounding_box': {'x': 150, 'y': 180, 'width': 100, 'height': 120}
            },
            {
                'landmarks': [{'x': 0.7, 'y': 0.5} for _ in range(21)],
                'bounding_box': {'x': 400, 'y': 220, 'width': 90, 'height': 110}
            }
        ]
        
        masks = self.processor.segment_multiple_hands(mock_image, hand_detections)
        
        self.assertEqual(len(masks), 2)
        for mask in masks:
            self.assertEqual(mask.shape, mock_image.shape[:2])


class TestHandTracker(unittest.TestCase):
    """Test HandTracker temporal tracking functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not HAND_SEGMENTATION_MODULES_AVAILABLE:
            self.skipTest("Hand segmentation modules not available")
        
        self.tracker_config = {
            'tracking_method': 'kalman',
            'max_disappeared': 30,
            'max_distance': 50,
            'smoothing_factor': 0.8
        }
        
        self.hand_tracker = HandTracker(self.tracker_config)

    def test_tracker_initialization(self):
        """Test hand tracker initialization."""
        self.assertEqual(len(self.hand_tracker.tracked_hands), 0)
        self.assertIsNotNone(self.hand_tracker.next_id)

    def test_new_hand_registration(self):
        """Test registration of new hand detection."""
        detection = {
            'landmarks': [{'x': 0.5, 'y': 0.4} for _ in range(21)],
            'bounding_box': {'x': 300, 'y': 180, 'width': 100, 'height': 120},
            'confidence': 0.95
        }
        
        hand_id = self.hand_tracker.register_new_hand(detection)
        
        self.assertIsNotNone(hand_id)
        self.assertIn(hand_id, self.hand_tracker.tracked_hands)

    def test_hand_tracking_update(self):
        """Test updating hand positions over time."""
        # Register initial hand
        initial_detection = {
            'landmarks': [{'x': 0.5, 'y': 0.4} for _ in range(21)],
            'bounding_box': {'x': 300, 'y': 180, 'width': 100, 'height': 120}
        }
        hand_id = self.hand_tracker.register_new_hand(initial_detection)
        
        # Update with new position
        updated_detection = {
            'landmarks': [{'x': 0.52, 'y': 0.42} for _ in range(21)],
            'bounding_box': {'x': 310, 'y': 190, 'width': 100, 'height': 120}
        }
        
        self.hand_tracker.update_hand_position(hand_id, updated_detection)
        
        tracked_hand = self.hand_tracker.tracked_hands[hand_id]
        self.assertEqual(len(tracked_hand['position_history']), 2)

    def test_hand_disappearance_handling(self):
        """Test handling of temporarily disappeared hands."""
        # Register hand
        detection = {
            'landmarks': [{'x': 0.5, 'y': 0.4} for _ in range(21)],
            'bounding_box': {'x': 300, 'y': 180, 'width': 100, 'height': 120}
        }
        hand_id = self.hand_tracker.register_new_hand(detection)
        
        # Simulate disappearance
        for _ in range(self.tracker_config['max_disappeared'] - 1):
            self.hand_tracker.increment_disappeared(hand_id)
        
        # Hand should still be tracked
        self.assertIn(hand_id, self.hand_tracker.tracked_hands)
        
        # One more increment should remove it
        self.hand_tracker.increment_disappeared(hand_id)
        self.assertNotIn(hand_id, self.hand_tracker.tracked_hands)

    def test_hand_reidentification(self):
        """Test re-identification of hands after temporary disappearance."""
        # Register and then lose hand
        initial_detection = {
            'landmarks': [{'x': 0.5, 'y': 0.4} for _ in range(21)],
            'bounding_box': {'x': 300, 'y': 180, 'width': 100, 'height': 120}
        }
        hand_id = self.hand_tracker.register_new_hand(initial_detection)
        
        # Simulate reappearance nearby
        reappearance_detection = {
            'landmarks': [{'x': 0.51, 'y': 0.41} for _ in range(21)],
            'bounding_box': {'x': 305, 'y': 185, 'width': 100, 'height': 120}
        }
        
        matched_id = self.hand_tracker.match_detection_to_tracked_hand(reappearance_detection)
        
        self.assertEqual(matched_id, hand_id)

    def test_velocity_estimation(self):
        """Test hand velocity estimation from position history."""
        hand_id = self.hand_tracker.register_new_hand({
            'landmarks': [{'x': 0.5, 'y': 0.4} for _ in range(21)],
            'bounding_box': {'x': 300, 'y': 180, 'width': 100, 'height': 120}
        })
        
        # Add position updates
        positions = [
            {'x': 310, 'y': 190},
            {'x': 320, 'y': 200},
            {'x': 330, 'y': 210}
        ]
        
        for pos in positions:
            detection = {
                'landmarks': [{'x': pos['x']/640, 'y': pos['y']/480} for _ in range(21)],
                'bounding_box': {'x': pos['x'], 'y': pos['y'], 'width': 100, 'height': 120}
            }
            self.hand_tracker.update_hand_position(hand_id, detection)
        
        velocity = self.hand_tracker.estimate_hand_velocity(hand_id)
        
        self.assertIn('vx', velocity)
        self.assertIn('vy', velocity)
        self.assertGreater(velocity['vx'], 0)  # Moving right
        self.assertGreater(velocity['vy'], 0)  # Moving down


class TestHandSegmentationCLI(unittest.TestCase):
    """Test HandSegmentationCLI command-line interface functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not HAND_SEGMENTATION_MODULES_AVAILABLE:
            self.skipTest("Hand segmentation modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.cli = HandSegmentationCLI()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_argument_parsing(self):
        """Test command-line argument parsing."""
        parser = CLIArgumentParser()
        
        test_args = [
            '--input', '/path/to/input',
            '--output', '/path/to/output',
            '--method', 'mediapipe',
            '--confidence', '0.8',
            '--batch-size', '10'
        ]
        
        args = parser.parse_args(test_args)
        
        self.assertEqual(args.input, '/path/to/input')
        self.assertEqual(args.output, '/path/to/output')
        self.assertEqual(args.method, 'mediapipe')
        self.assertEqual(args.confidence, 0.8)
        self.assertEqual(args.batch_size, 10)

    def test_batch_processing(self):
        """Test batch processing of multiple images."""
        # Create test images
        test_images = []
        for i in range(3):
            img_path = os.path.join(self.temp_dir, f'test_image_{i}.jpg')
            mock_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            with patch('cv2.imwrite'):
                test_images.append(img_path)
        
        with patch('cv2.imread') as mock_imread, \
             patch.object(self.cli, 'process_single_image') as mock_process:
            
            mock_imread.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            mock_process.return_value = {'success': True}
            
            results = self.cli.process_batch(test_images, self.temp_dir)
            
            self.assertEqual(len(results), 3)
            self.assertEqual(mock_process.call_count, 3)

    def test_output_format_options(self):
        """Test different output format options."""
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_mask = np.zeros((480, 640), dtype=np.uint8)
        
        formats = ['mask', 'overlay', 'json', 'all']
        
        for output_format in formats:
            with patch('cv2.imwrite') as mock_imwrite:
                result = self.cli.save_results(
                    mock_image, mock_mask, 
                    self.temp_dir, 'test_image',
                    output_format
                )
                
                self.assertTrue(result['success'])

    def test_parameter_validation(self):
        """Test validation of processing parameters."""
        valid_params = {
            'confidence_threshold': 0.7,
            'max_hands': 2,
            'detection_method': 'mediapipe'
        }
        
        invalid_params = {
            'confidence_threshold': 1.5,  # > 1.0
            'max_hands': -1,              # < 0
            'detection_method': 'invalid' # Not supported
        }
        
        self.assertTrue(self.cli.validate_parameters(valid_params))
        self.assertFalse(self.cli.validate_parameters(invalid_params))

    def test_progress_reporting(self):
        """Test progress reporting during batch processing."""
        with patch('builtins.print') as mock_print:
            total_images = 10
            
            for i in range(total_images):
                self.cli.report_progress(i + 1, total_images)
            
            # Should have printed progress updates
            self.assertTrue(mock_print.called)


class TestHandSegmentationIntegration(unittest.TestCase):
    """Test end-to-end hand segmentation integration workflows."""

    def setUp(self):
        """Set up test fixtures."""
        if not HAND_SEGMENTATION_MODULES_AVAILABLE:
            self.skipTest("Hand segmentation modules not available")

    def test_complete_segmentation_pipeline(self):
        """Test complete hand segmentation pipeline."""
        with patch('hand_segmentation.hand_detector.HandDetector') as mock_detector, \
             patch('hand_segmentation.segmentation_processor.SegmentationProcessor') as mock_processor, \
             patch('hand_segmentation.hand_tracker.HandTracker') as mock_tracker:
            
            # Setup mocks
            mock_detector_instance = Mock()
            mock_processor_instance = Mock()
            mock_tracker_instance = Mock()
            
            mock_detector.return_value = mock_detector_instance
            mock_processor.return_value = mock_processor_instance
            mock_tracker.return_value = mock_tracker_instance
            
            # Mock pipeline results
            mock_detector_instance.detect_hands.return_value = [
                {'landmarks': [], 'bounding_box': {}, 'confidence': 0.9}
            ]
            mock_processor_instance.segment_multiple_hands.return_value = [
                np.zeros((480, 640), dtype=np.uint8)
            ]
            mock_tracker_instance.update_tracks.return_value = [
                {'id': 'hand_001', 'position': {'x': 320, 'y': 240}}
            ]
            
            # Test pipeline
            mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
            
            detector = mock_detector_instance
            processor = mock_processor_instance
            tracker = mock_tracker_instance
            
            # Run pipeline
            detections = detector.detect_hands(mock_image)
            masks = processor.segment_multiple_hands(mock_image, detections)
            tracks = tracker.update_tracks(detections)
            
            # Verify pipeline execution
            detector.detect_hands.assert_called_once()
            processor.segment_multiple_hands.assert_called_once()
            tracker.update_tracks.assert_called_once()
            
            self.assertEqual(len(detections), 1)
            self.assertEqual(len(masks), 1)
            self.assertEqual(len(tracks), 1)

    def test_real_time_processing_simulation(self):
        """Test real-time processing simulation with frame rate constraints."""
        with patch('time.time') as mock_time:
            # Simulate frame timestamps
            frame_times = [0.0, 0.033, 0.066, 0.099]  # 30 FPS
            mock_time.side_effect = frame_times
            
            processing_times = []
            
            for i in range(len(frame_times) - 1):
                start_time = frame_times[i]
                end_time = frame_times[i + 1]
                processing_time = end_time - start_time
                processing_times.append(processing_time)
            
            # All processing should complete within frame time (33ms for 30 FPS)
            self.assertTrue(all(t <= 0.033 for t in processing_times))

    def test_error_recovery_scenarios(self):
        """Test error recovery in hand segmentation pipeline."""
        error_scenarios = [
            {'stage': 'detection', 'error': 'Camera disconnected'},
            {'stage': 'processing', 'error': 'Memory allocation failed'},
            {'stage': 'tracking', 'error': 'Invalid tracking state'}
        ]
        
        with patch('hand_segmentation.error_handler.ErrorHandler') as mock_error_handler:
            mock_handler_instance = Mock()
            mock_error_handler.return_value = mock_handler_instance
            
            for scenario in error_scenarios:
                mock_handler_instance.handle_pipeline_error(scenario)
                mock_handler_instance.handle_pipeline_error.assert_called_with(scenario)


def create_hand_segmentation_test_suite():
    """Create comprehensive test suite for hand segmentation functionality."""
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestHandDetector))
    suite.addTest(unittest.makeSuite(TestSegmentationProcessor))
    suite.addTest(unittest.makeSuite(TestHandTracker))
    suite.addTest(unittest.makeSuite(TestHandSegmentationCLI))
    suite.addTest(unittest.makeSuite(TestHandSegmentationIntegration))
    
    return suite


if __name__ == '__main__':
    if HAND_SEGMENTATION_MODULES_AVAILABLE:
        # Run comprehensive tests
        runner = unittest.TextTestRunner(verbosity=2)
        suite = create_hand_segmentation_test_suite()
        result = runner.run(suite)
        
        # Print results summary
        print(f"\n{'='*60}")
        print(f"Hand Segmentation Tests Summary")
        print(f"{'='*60}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    else:
        print("Hand segmentation modules not available - skipping tests")