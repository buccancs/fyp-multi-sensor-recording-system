#!/usr/bin/env python3
"""
Comprehensive Test Suite for Advanced Dual Webcam System

This test suite provides extensive validation of the enhanced dual webcam system
including advanced synchronization algorithms, computer vision preprocessing,
and physiological signal extraction capabilities.

Test Categories:
- Unit tests for individual components
- Integration tests for system-level functionality  
- Performance benchmarking and validation
- Error handling and robustness testing
- Academic-quality validation metrics

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import unittest
import sys
import os
import time
import threading
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import test subjects
from webcam.advanced_sync_algorithms import (
    AdaptiveSynchronizer, SynchronizationStrategy, SyncFrame, TimingMetrics
)
from webcam.cv_preprocessing_pipeline import (
    AdvancedROIDetector, PhysiologicalSignalExtractor, 
    ROIDetectionMethod, SignalExtractionMethod, PhysiologicalSignal
)
from webcam.dual_webcam_capture import DualWebcamCapture, test_dual_webcam_access
from utils.logging_config import get_logger

logger = get_logger(__name__)


class TestAdvancedSynchronization(unittest.TestCase):
    """Test suite for advanced synchronization algorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.synchronizer = AdaptiveSynchronizer(
            target_fps=30.0,
            sync_threshold_ms=16.67,
            strategy=SynchronizationStrategy.ADAPTIVE_HYBRID
        )
        
        # Create test frames
        self.test_frame1 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.test_frame2 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_synchronizer_initialization(self):
        """Test synchronizer initialization with various parameters."""
        sync = AdaptiveSynchronizer(target_fps=60.0, sync_threshold_ms=8.33)
        
        self.assertEqual(sync.target_fps, 60.0)
        self.assertEqual(sync.sync_threshold_ms, 8.33)
        self.assertEqual(sync.frame_interval_ms, 1000.0 / 60.0)
        self.assertIsNotNone(sync.timing_buffer)
        self.assertIsNotNone(sync.metrics)
    
    def test_synchronize_frames_basic(self):
        """Test basic frame synchronization functionality."""
        timestamp1 = time.time()
        timestamp2 = timestamp1 + 0.005  # 5ms offset
        
        sync_frame = self.synchronizer.synchronize_frames(
            self.test_frame1, self.test_frame2, timestamp1, timestamp2
        )
        
        self.assertIsInstance(sync_frame, SyncFrame)
        self.assertEqual(sync_frame.frame_id, 0)
        self.assertGreater(sync_frame.sync_quality, 0.0)
        self.assertLessEqual(sync_frame.sync_quality, 1.0)
        self.assertEqual(sync_frame.camera1_frame.shape, self.test_frame1.shape)
        self.assertEqual(sync_frame.camera2_frame.shape, self.test_frame2.shape)
    
    def test_synchronization_strategies(self):
        """Test different synchronization strategies."""
        strategies = [
            SynchronizationStrategy.MASTER_SLAVE,
            SynchronizationStrategy.CROSS_CORRELATION,
            SynchronizationStrategy.HARDWARE_SYNC,
            SynchronizationStrategy.ADAPTIVE_HYBRID
        ]
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                sync = AdaptiveSynchronizer(strategy=strategy)
                sync_frame = sync.synchronize_frames(
                    self.test_frame1, self.test_frame2, time.time(), time.time()
                )
                self.assertIsNotNone(sync_frame)
                self.assertGreaterEqual(sync_frame.sync_quality, 0.0)
    
    def test_adaptive_parameter_adjustment(self):
        """Test adaptive parameter adjustment over time."""
        # Process multiple frames to trigger adaptation
        for i in range(50):
            timestamp1 = time.time()
            timestamp2 = timestamp1 + np.random.uniform(-0.01, 0.01)  # Random offset
            
            self.synchronizer.synchronize_frames(
                self.test_frame1, self.test_frame2, timestamp1, timestamp2
            )
        
        # Check that metrics are being tracked
        diagnostics = self.synchronizer.get_diagnostics()
        self.assertGreater(diagnostics['metrics']['frames_processed'], 0)
        self.assertIn('adaptive_threshold_ms', diagnostics)
    
    def test_performance_metrics(self):
        """Test comprehensive performance metrics collection."""
        # Process frames with known timing patterns
        for i in range(20):
            offset = 0.001 * (i % 5)  # Varying offsets
            timestamp1 = time.time()
            timestamp2 = timestamp1 + offset
            
            self.synchronizer.synchronize_frames(
                self.test_frame1, self.test_frame2, timestamp1, timestamp2
            )
        
        diagnostics = self.synchronizer.get_diagnostics()
        metrics = diagnostics['metrics']
        
        self.assertEqual(metrics['frames_processed'], 20)
        self.assertGreaterEqual(metrics['mean_offset_ms'], 0)
        self.assertGreaterEqual(metrics['std_dev_offset_ms'], 0)
        self.assertIsInstance(metrics['violation_rate'], float)
    
    def test_sync_frame_methods(self):
        """Test SyncFrame utility methods."""
        sync_frame = SyncFrame(
            timestamp=time.time(),
            frame_id=1,
            camera1_frame=self.test_frame1,
            camera2_frame=self.test_frame2,
            camera1_hardware_ts=time.time(),
            camera2_hardware_ts=time.time() + 0.001
        )
        
        offset_ms = sync_frame.get_sync_offset_ms()
        self.assertGreater(offset_ms, 0)
        self.assertLess(offset_ms, 10)  # Should be around 1ms


class TestComputerVisionPipeline(unittest.TestCase):
    """Test suite for computer vision preprocessing pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.roi_detector = AdvancedROIDetector(
            method=ROIDetectionMethod.FACE_CASCADE,
            tracking_enabled=True
        )
        
        self.signal_extractor = PhysiologicalSignalExtractor(
            method=SignalExtractionMethod.MEAN_RGB,
            sampling_rate=30.0
        )
        
        # Create test face-like image
        self.test_image = self._create_test_face_image()
    
    def _create_test_face_image(self) -> np.ndarray:
        """Create a synthetic test image with face-like features."""
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        # Add face-like rectangular region
        cv2.rectangle(image, (200, 150), (440, 350), (180, 160, 140), -1)
        
        # Add simple features
        cv2.circle(image, (280, 220), 10, (50, 50, 50), -1)  # Left eye
        cv2.circle(image, (360, 220), 10, (50, 50, 50), -1)  # Right eye
        cv2.rectangle(image, (310, 270), (330, 290), (100, 80, 80), -1)  # Nose
        
        return image
    
    @patch('cv2.CascadeClassifier')
    def test_roi_detector_initialization(self, mock_cascade):
        """Test ROI detector initialization with different methods."""
        mock_cascade.return_value = Mock()
        
        detector = AdvancedROIDetector(method=ROIDetectionMethod.FACE_CASCADE)
        self.assertEqual(detector.method, ROIDetectionMethod.FACE_CASCADE)
        self.assertTrue(detector.tracking_enabled)
        self.assertIsNotNone(detector.roi_history)
    
    @patch('cv2.CascadeClassifier')
    def test_roi_detection_basic(self, mock_cascade):
        """Test basic ROI detection functionality."""
        # Mock cascade detection
        mock_classifier = Mock()
        mock_classifier.detectMultiScale.return_value = np.array([[200, 150, 240, 200]])
        mock_cascade.return_value = mock_classifier
        
        detector = AdvancedROIDetector(method=ROIDetectionMethod.FACE_CASCADE)
        roi = detector.detect_roi(self.test_image)
        
        self.assertIsNotNone(roi)
        self.assertEqual(len(roi), 4)  # (x, y, width, height)
        self.assertIsInstance(roi[0], (int, np.integer))
    
    def test_signal_extractor_initialization(self):
        """Test signal extractor initialization."""
        extractor = PhysiologicalSignalExtractor(
            method=SignalExtractionMethod.CHROM_METHOD,
            sampling_rate=60.0,
            signal_length_seconds=5.0
        )
        
        self.assertEqual(extractor.method, SignalExtractionMethod.CHROM_METHOD)
        self.assertEqual(extractor.sampling_rate, 60.0)
        self.assertEqual(extractor.buffer_size, 300)  # 60 * 5
    
    def test_signal_extraction_methods(self):
        """Test different signal extraction methods."""
        methods = [
            SignalExtractionMethod.MEAN_RGB,
            SignalExtractionMethod.CHROM_METHOD,
            SignalExtractionMethod.POS_METHOD
        ]
        
        roi_patch = self.test_image[150:350, 200:440]  # Extract face region
        
        for method in methods:
            with self.subTest(method=method):
                extractor = PhysiologicalSignalExtractor(method=method)
                
                # Add multiple frames to build up signal
                for i in range(100):
                    # Simulate slight color variations
                    variation = np.random.normal(0, 2, roi_patch.shape)
                    modified_patch = np.clip(roi_patch.astype(float) + variation, 0, 255).astype(np.uint8)
                    
                    signal = extractor.extract_signal(modified_patch)
                    
                    if signal is not None:  # Some methods need more data
                        self.assertIsInstance(signal, PhysiologicalSignal)
                        self.assertGreater(len(signal.signal_data), 0)
                        break
    
    def test_physiological_signal_properties(self):
        """Test PhysiologicalSignal class properties and methods."""
        # Create mock signal data
        signal_data = np.sin(2 * np.pi * 1.2 * np.linspace(0, 10, 300))  # 1.2 Hz signal (72 BPM)
        
        signal = PhysiologicalSignal(
            signal_data=signal_data,
            sampling_rate=30.0,
            timestamp=time.time()
        )
        
        # Test heart rate estimation
        hr_estimate = signal.get_heart_rate_estimate()
        self.assertIsNotNone(hr_estimate)
        self.assertGreater(hr_estimate, 60)  # Should be around 72 BPM
        self.assertLess(hr_estimate, 90)
    
    def test_roi_metrics_calculation(self):
        """Test ROI quality metrics calculation."""
        # Simulate ROI detection over multiple frames
        for i in range(10):
            # Simulate stable ROI with small variations
            x = 200 + np.random.randint(-5, 5)
            y = 150 + np.random.randint(-5, 5)
            roi = (x, y, 240, 200)
            
            self.roi_detector._update_roi_metrics(roi, self.test_image)
        
        metrics = self.roi_detector.get_metrics()
        self.assertGreater(metrics.frame_count, 0)
        self.assertGreaterEqual(metrics.stability_score, 0.0)
        self.assertLessEqual(metrics.stability_score, 1.0)


class TestDualWebcamIntegration(unittest.TestCase):
    """Test suite for dual webcam system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock camera indices that won't interfere with real hardware
        self.test_camera_indices = [99, 98]  # Non-existent cameras for testing
    
    def test_dual_webcam_initialization(self):
        """Test dual webcam capture initialization."""
        capture = DualWebcamCapture(
            camera1_index=self.test_camera_indices[0],
            camera2_index=self.test_camera_indices[1],
            resolution=(640, 480),
            preview_fps=30.0,
            recording_fps=30.0
        )
        
        self.assertEqual(capture.camera1_index, self.test_camera_indices[0])
        self.assertEqual(capture.camera2_index, self.test_camera_indices[1])
        self.assertEqual(capture.target_resolution, (640, 480))
        self.assertIsNotNone(capture.synchronizer)
        self.assertIsNotNone(capture.roi_detector)
        self.assertIsNotNone(capture.signal_extractor)
    
    def test_physiological_monitoring_controls(self):
        """Test physiological monitoring enable/disable."""
        capture = DualWebcamCapture(
            camera1_index=self.test_camera_indices[0],
            camera2_index=self.test_camera_indices[1]
        )
        
        # Test enabling monitoring
        capture.enable_physiological_monitoring(True)
        self.assertTrue(capture.enable_physio_monitoring)
        
        # Test disabling monitoring
        capture.enable_physiological_monitoring(False)
        self.assertFalse(capture.enable_physio_monitoring)
        self.assertIsNone(capture.current_roi)
        self.assertIsNone(capture.latest_physio_signal)
    
    def test_synchronization_strategy_changes(self):
        """Test changing synchronization strategies."""
        capture = DualWebcamCapture(
            camera1_index=self.test_camera_indices[0],
            camera2_index=self.test_camera_indices[1]
        )
        
        # Test valid strategy change
        capture.set_synchronization_strategy('master_slave')
        
        # Test invalid strategy (should log error)
        capture.set_synchronization_strategy('invalid_strategy')
    
    def test_metrics_and_diagnostics(self):
        """Test metrics collection and diagnostic functions."""
        capture = DualWebcamCapture(
            camera1_index=self.test_camera_indices[0],
            camera2_index=self.test_camera_indices[1]
        )
        
        # Test synchronization diagnostics
        sync_diag = capture.get_synchronization_diagnostics()
        self.assertIsInstance(sync_diag, dict)
        self.assertIn('strategy', sync_diag)
        
        # Test ROI metrics
        roi_metrics = capture.get_roi_metrics()
        self.assertIsInstance(roi_metrics, dict)
        
        # Test physiological signal (should be None initially)
        physio_signal = capture.get_latest_physiological_signal()
        self.assertIsNone(physio_signal)
    
    def test_data_export_functionality(self):
        """Test synchronization data export."""
        capture = DualWebcamCapture(
            camera1_index=self.test_camera_indices[0],
            camera2_index=self.test_camera_indices[1]
        )
        
        # Create temporary export file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_path = f.name
        
        try:
            # Test export
            success = capture.export_synchronization_data(export_path)
            self.assertTrue(success)
            
            # Verify file exists and contains valid JSON
            self.assertTrue(os.path.exists(export_path))
            
            import json
            with open(export_path, 'r') as f:
                data = json.load(f)
            
            self.assertIn('export_timestamp', data)
            self.assertIn('camera_configuration', data)
            self.assertIn('synchronization_diagnostics', data)
            
        finally:
            # Cleanup
            if os.path.exists(export_path):
                os.unlink(export_path)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarking test suite."""
    
    def test_synchronization_performance(self):
        """Benchmark synchronization algorithm performance."""
        synchronizer = AdaptiveSynchronizer(target_fps=30.0)
        
        # Create test frames
        frame1 = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        frame2 = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        # Benchmark synchronization speed
        start_time = time.time()
        iterations = 100
        
        for i in range(iterations):
            synchronizer.synchronize_frames(
                frame1, frame2, time.time(), time.time()
            )
        
        elapsed_time = time.time() - start_time
        avg_time_ms = (elapsed_time / iterations) * 1000
        
        # Performance assertions
        self.assertLess(avg_time_ms, 10.0, f"Synchronization too slow: {avg_time_ms:.2f}ms")
        
        logger.info(f"Synchronization performance: {avg_time_ms:.2f}ms per frame")
    
    def test_roi_detection_performance(self):
        """Benchmark ROI detection performance."""
        detector = AdvancedROIDetector(method=ROIDetectionMethod.FACE_CASCADE)
        
        # Create test image
        test_image = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        
        # Benchmark detection speed
        start_time = time.time()
        iterations = 50
        
        for i in range(iterations):
            detector.detect_roi(test_image)
        
        elapsed_time = time.time() - start_time
        avg_time_ms = (elapsed_time / iterations) * 1000
        
        # Performance assertions  
        self.assertLess(avg_time_ms, 50.0, f"ROI detection too slow: {avg_time_ms:.2f}ms")
        
        logger.info(f"ROI detection performance: {avg_time_ms:.2f}ms per frame")
    
    def test_signal_extraction_performance(self):
        """Benchmark signal extraction performance."""
        extractor = PhysiologicalSignalExtractor(method=SignalExtractionMethod.CHROM_METHOD)
        
        # Create test ROI patch
        roi_patch = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        # Build up signal buffer first
        for i in range(100):
            extractor.extract_signal(roi_patch)
        
        # Benchmark extraction speed
        start_time = time.time()
        iterations = 100
        
        for i in range(iterations):
            extractor.extract_signal(roi_patch)
        
        elapsed_time = time.time() - start_time
        avg_time_ms = (elapsed_time / iterations) * 1000
        
        # Performance assertions
        self.assertLess(avg_time_ms, 20.0, f"Signal extraction too slow: {avg_time_ms:.2f}ms")
        
        logger.info(f"Signal extraction performance: {avg_time_ms:.2f}ms per frame")


class TestErrorHandlingAndRobustness(unittest.TestCase):
    """Test suite for error handling and system robustness."""
    
    def test_invalid_frame_handling(self):
        """Test handling of invalid or corrupted frames."""
        synchronizer = AdaptiveSynchronizer()
        
        # Test with None frames
        result = synchronizer.synchronize_frames(None, None, time.time(), time.time())
        self.assertIsNotNone(result)  # Should handle gracefully
        
        # Test with empty frames
        empty_frame = np.array([])
        result = synchronizer.synchronize_frames(empty_frame, empty_frame, time.time(), time.time())
        self.assertIsNotNone(result)
    
    def test_roi_detection_edge_cases(self):
        """Test ROI detection with edge cases."""
        detector = AdvancedROIDetector()
        
        # Test with empty image
        empty_image = np.array([])
        roi = detector.detect_roi(empty_image)
        # Should handle gracefully without crashing
        
        # Test with very small image
        tiny_image = np.ones((10, 10, 3), dtype=np.uint8)
        roi = detector.detect_roi(tiny_image)
        # Should handle gracefully
        
        # Test with single channel image
        gray_image = np.ones((100, 100), dtype=np.uint8)
        try:
            roi = detector.detect_roi(gray_image)
        except Exception as e:
            # Should either handle gracefully or raise specific exception
            self.assertIsInstance(e, (ValueError, cv2.error))
    
    def test_signal_extraction_edge_cases(self):
        """Test signal extraction with edge cases."""
        extractor = PhysiologicalSignalExtractor()
        
        # Test with empty ROI
        empty_roi = np.array([])
        signal = extractor.extract_signal(empty_roi)
        self.assertIsNone(signal)  # Should return None for invalid input
        
        # Test with very small ROI
        tiny_roi = np.ones((2, 2, 3), dtype=np.uint8)
        signal = extractor.extract_signal(tiny_roi)
        # Should handle gracefully
        
        # Test with constant color ROI (no variation)
        constant_roi = np.ones((100, 100, 3), dtype=np.uint8) * 128
        for i in range(50):
            signal = extractor.extract_signal(constant_roi)
        # Should handle constant signal appropriately


def run_comprehensive_tests():
    """
    Run comprehensive test suite with detailed reporting.
    
    Returns:
        dict: Test results summary
    """
    logger.info("Starting comprehensive dual webcam system test suite")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAdvancedSynchronization,
        TestComputerVisionPipeline,
        TestDualWebcamIntegration,
        TestPerformanceBenchmarks,
        TestErrorHandlingAndRobustness
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate summary
    test_summary = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / 
                        max(1, result.testsRun)) * 100,
        'execution_time': getattr(result, 'execution_time', 'unknown')
    }
    
    logger.info(f"Test suite completed: {test_summary}")
    
    return test_summary


if __name__ == "__main__":
    # Import required modules at runtime to avoid import errors during module load
    try:
        import cv2
        import scipy.signal
        
        # Run comprehensive tests
        results = run_comprehensive_tests()
        
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST SUITE RESULTS")
        print("="*60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Failures: {results['failures']}")
        print(f"Errors: {results['errors']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print("="*60)
        
        # Exit with appropriate code
        exit_code = 0 if (results['failures'] == 0 and results['errors'] == 0) else 1
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"Required dependencies not available: {e}")
        print("Please install required packages: opencv-python, scipy, numpy")
        sys.exit(1)