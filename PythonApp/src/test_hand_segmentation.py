"""
Tests for Hand Segmentation Module

Comprehensive tests for hand segmentation functionality including
unit tests, integration tests, and end-to-end processing tests.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import cv2

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hand_segmentation import (
    HandSegmentationEngine,
    SegmentationConfig,
    SegmentationMethod,
    SessionPostProcessor,
    create_segmentation_engine,
    create_session_post_processor
)
from hand_segmentation.utils import (
    HandRegion,
    ProcessingResult,
    create_bounding_box_from_landmarks,
    crop_frame_to_region,
    create_hand_mask_from_landmarks
)


class TestHandSegmentationUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_bounding_box_from_landmarks(self):
        """Test bounding box creation from landmarks."""
        landmarks = [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]
        bbox = create_bounding_box_from_landmarks(landmarks, 100, 100, padding=10)
        
        # Expected: x=0, y=0, w=100, h=100 (with padding and clipping)
        self.assertEqual(bbox[0], 0)  # x
        self.assertEqual(bbox[1], 0)  # y
        self.assertEqual(bbox[2], 100)  # width
        self.assertEqual(bbox[3], 100)  # height
    
    def test_crop_frame_to_region(self):
        """Test frame cropping functionality."""
        # Create test frame
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # Crop region
        bbox = (10, 10, 50, 50)
        cropped = crop_frame_to_region(frame, bbox)
        
        self.assertEqual(cropped.shape, (50, 50, 3))
    
    def test_hand_mask_creation(self):
        """Test hand mask creation from landmarks."""
        landmarks = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        mask = create_hand_mask_from_landmarks(landmarks, (100, 100))
        
        self.assertEqual(mask.shape, (100, 100))
        self.assertTrue(np.any(mask > 0))  # Should have some non-zero pixels


class TestSegmentationConfig(unittest.TestCase):
    """Test segmentation configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SegmentationConfig()
        
        self.assertEqual(config.method, SegmentationMethod.MEDIAPIPE)
        self.assertEqual(config.min_detection_confidence, 0.5)
        self.assertEqual(config.max_num_hands, 2)
        self.assertTrue(config.output_cropped)
        self.assertTrue(config.output_masks)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = SegmentationConfig(
            method=SegmentationMethod.COLOR_BASED,
            min_detection_confidence=0.7,
            max_num_hands=1,
            output_cropped=False
        )
        
        self.assertEqual(config.method, SegmentationMethod.COLOR_BASED)
        self.assertEqual(config.min_detection_confidence, 0.7)
        self.assertEqual(config.max_num_hands, 1)
        self.assertFalse(config.output_cropped)


class TestHandSegmentationEngine(unittest.TestCase):
    """Test hand segmentation engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = SegmentationConfig(
            method=SegmentationMethod.COLOR_BASED,  # Use color-based for testing (no external deps)
            output_cropped=True,
            output_masks=True
        )
        self.engine = HandSegmentationEngine(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'engine'):
            self.engine.cleanup()
        shutil.rmtree(self.test_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertFalse(self.engine.is_initialized)
        success = self.engine.initialize()
        self.assertTrue(success)
        self.assertTrue(self.engine.is_initialized)
    
    def test_supported_methods(self):
        """Test getting supported methods."""
        methods = self.engine.get_supported_methods()
        expected_methods = ['mediapipe', 'color_based', 'contour_based']
        self.assertEqual(sorted(methods), sorted(expected_methods))
    
    def test_frame_processing(self):
        """Test single frame processing."""
        # Initialize engine
        self.engine.initialize()
        
        # Create test frame with skin-like colors
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Add a skin-colored region
        frame[30:70, 30:70] = [10, 50, 150]  # HSV-like skin color in BGR
        
        # Process frame
        hand_regions = self.engine.segmentation_model.process_frame(frame)
        
        # Should detect at least something (might be 0 if color doesn't match skin range)
        self.assertIsInstance(hand_regions, list)
    
    def create_test_video(self, path: str, frames: int = 10, fps: int = 30):
        """Create a test video file."""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(path), fourcc, fps, (100, 100))
        
        for i in range(frames):
            # Create frame with moving colored region
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            x = 20 + i * 2
            frame[30:70, x:x+20] = [10, 50, 150]  # Skin-like color
            writer.write(frame)
        
        writer.release()
    
    def test_video_processing(self):
        """Test video processing functionality."""
        # Create test video
        video_path = os.path.join(self.test_dir, "test_video.mp4")
        self.create_test_video(video_path, frames=5)
        
        # Initialize engine
        self.engine.initialize()
        
        # Process video
        output_dir = os.path.join(self.test_dir, "output")
        result = self.engine.process_video(video_path, output_dir)
        
        # Check result
        self.assertIsInstance(result, ProcessingResult)
        self.assertEqual(result.input_video_path, video_path)
        self.assertEqual(result.output_directory, output_dir)
        self.assertGreater(result.processed_frames, 0)


class TestSessionPostProcessor(unittest.TestCase):
    """Test session post-processor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.recordings_dir = os.path.join(self.test_dir, "recordings")
        self.processor = create_session_post_processor(self.recordings_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def create_test_session(self, session_id: str):
        """Create a test session directory with video files."""
        session_dir = Path(self.recordings_dir) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test video
        video_path = session_dir / "test_video.mp4"
        self.create_test_video(str(video_path), frames=3)
        
        return session_dir
    
    def create_test_video(self, path: str, frames: int = 3, fps: int = 30):
        """Create a simple test video."""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(path), fourcc, fps, (50, 50))
        
        for i in range(frames):
            frame = np.ones((50, 50, 3), dtype=np.uint8) * (i * 50 + 50)
            writer.write(frame)
        
        writer.release()
    
    def test_session_discovery(self):
        """Test session discovery."""
        # Initially no sessions
        sessions = self.processor.discover_sessions()
        self.assertEqual(len(sessions), 0)
        
        # Create test session
        self.create_test_session("test_session_001")
        
        # Should discover the session
        sessions = self.processor.discover_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertIn("test_session_001", sessions)
    
    def test_get_session_videos(self):
        """Test getting videos from a session."""
        session_id = "test_session_002"
        self.create_test_session(session_id)
        
        videos = self.processor.get_session_videos(session_id)
        self.assertEqual(len(videos), 1)
        self.assertTrue(videos[0].endswith("test_video.mp4"))
    
    def test_processing_status(self):
        """Test processing status checking."""
        session_id = "test_session_003"
        self.create_test_session(session_id)
        
        # Initially not processed
        status = self.processor.get_processing_status(session_id)
        self.assertEqual(len(status), 1)
        self.assertFalse(list(status.values())[0])
    
    def test_available_methods(self):
        """Test getting available methods."""
        methods = self.processor.get_available_methods()
        expected = ['mediapipe', 'color_based', 'contour_based']
        self.assertEqual(sorted(methods), sorted(expected))


class TestIntegrationEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.recordings_dir = os.path.join(self.test_dir, "recordings")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def create_realistic_test_video(self, path: str, frames: int = 10):
        """Create a more realistic test video with hand-like movement."""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(path), fourcc, 30, (320, 240))
        
        for i in range(frames):
            # Create frame with moving hand-like shape
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            
            # Add background
            frame[:] = [20, 30, 40]
            
            # Add hand-like colored region
            center_x = 160 + int(20 * np.sin(i * 0.5))
            center_y = 120 + int(10 * np.cos(i * 0.3))
            
            # Draw circle as simplified hand
            cv2.circle(frame, (center_x, center_y), 30, [15, 100, 180], -1)
            
            # Add some "fingers"
            for j in range(5):
                angle = j * 0.6 + i * 0.1
                finger_x = center_x + int(25 * np.cos(angle))
                finger_y = center_y + int(25 * np.sin(angle))
                cv2.circle(frame, (finger_x, finger_y), 8, [10, 80, 160], -1)
            
            writer.write(frame)
        
        writer.release()
    
    def test_end_to_end_processing(self):
        """Test complete end-to-end processing workflow."""
        # Create session structure
        session_id = "integration_test_session"
        session_dir = Path(self.recordings_dir) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test video
        video_path = session_dir / "webcam_recording.mp4"
        self.create_realistic_test_video(str(video_path), frames=5)
        
        # Create post-processor
        processor = create_session_post_processor(self.recordings_dir)
        
        # Verify session discovery
        sessions = processor.discover_sessions()
        self.assertIn(session_id, sessions)
        
        # Process session using color-based method (no external dependencies)
        results = processor.process_session(
            session_id,
            method="color_based",
            output_cropped=True,
            output_masks=True
        )
        
        # Verify results
        self.assertEqual(len(results), 1)
        result = list(results.values())[0]
        
        # Check that processing completed (success or failure is okay for test data)
        self.assertIsInstance(result, ProcessingResult)
        self.assertGreater(result.processed_frames, 0)
        
        # Check output directory was created
        output_dir = session_dir / "hand_segmentation_webcam_recording"
        self.assertTrue(output_dir.exists())
        
        # Check metadata file was created
        metadata_file = output_dir / "processing_metadata.json"
        self.assertTrue(metadata_file.exists())
        
        # Check processing status
        status = processor.get_processing_status(session_id)
        self.assertEqual(len(status), 1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)