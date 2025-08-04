import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from hand_segmentation import HandSegmentationEngine, SegmentationConfig, SegmentationMethod, SessionPostProcessor, create_segmentation_engine, create_session_post_processor
from hand_segmentation.utils import HandRegion, ProcessingResult, create_bounding_box_from_landmarks, crop_frame_to_region, create_hand_mask_from_landmarks


class TestHandSegmentationUtils(unittest.TestCase):

    def test_bounding_box_from_landmarks(self):
        landmarks = [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]
        bbox = create_bounding_box_from_landmarks(landmarks, 100, 100,
            padding=10)
        self.assertEqual(bbox[0], 0)
        self.assertEqual(bbox[1], 0)
        self.assertEqual(bbox[2], 100)
        self.assertEqual(bbox[3], 100)

    def test_crop_frame_to_region(self):
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        bbox = 10, 10, 50, 50
        cropped = crop_frame_to_region(frame, bbox)
        self.assertEqual(cropped.shape, (50, 50, 3))

    def test_hand_mask_creation(self):
        landmarks = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        mask = create_hand_mask_from_landmarks(landmarks, (100, 100))
        self.assertEqual(mask.shape, (100, 100))
        self.assertTrue(np.any(mask > 0))


class TestSegmentationConfig(unittest.TestCase):

    def test_default_config(self):
        config = SegmentationConfig()
        self.assertEqual(config.method, SegmentationMethod.MEDIAPIPE)
        self.assertEqual(config.min_detection_confidence, 0.5)
        self.assertEqual(config.max_num_hands, 2)
        self.assertTrue(config.output_cropped)
        self.assertTrue(config.output_masks)

    def test_custom_config(self):
        config = SegmentationConfig(method=SegmentationMethod.COLOR_BASED,
            min_detection_confidence=0.7, max_num_hands=1, output_cropped=False
            )
        self.assertEqual(config.method, SegmentationMethod.COLOR_BASED)
        self.assertEqual(config.min_detection_confidence, 0.7)
        self.assertEqual(config.max_num_hands, 1)
        self.assertFalse(config.output_cropped)


class TestHandSegmentationEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = SegmentationConfig(method=SegmentationMethod.
            COLOR_BASED, output_cropped=True, output_masks=True)
        self.engine = HandSegmentationEngine(self.config)

    def tearDown(self):
        if hasattr(self, 'engine'):
            self.engine.cleanup()
        shutil.rmtree(self.test_dir)

    def test_engine_initialization(self):
        self.assertFalse(self.engine.is_initialized)
        success = self.engine.initialize()
        self.assertTrue(success)
        self.assertTrue(self.engine.is_initialized)

    def test_supported_methods(self):
        methods = self.engine.get_supported_methods()
        expected_methods = ['mediapipe', 'color_based', 'contour_based']
        self.assertEqual(sorted(methods), sorted(expected_methods))

    def test_frame_processing(self):
        self.engine.initialize()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[30:70, 30:70] = [10, 50, 150]
        hand_regions = self.engine.segmentation_model.process_frame(frame)
        self.assertIsInstance(hand_regions, list)

    def create_test_video(self, path: str, frames: int=10, fps: int=30):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(path), fourcc, fps, (100, 100))
        for i in range(frames):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            x = 20 + i * 2
            frame[30:70, x:x + 20] = [10, 50, 150]
            writer.write(frame)
        writer.release()

    def test_video_processing(self):
        video_path = os.path.join(self.test_dir, 'test_video.mp4')
        self.create_test_video(video_path, frames=5)
        self.engine.initialize()
        output_dir = os.path.join(self.test_dir, 'output')
        result = self.engine.process_video(video_path, output_dir)
        self.assertIsInstance(result, ProcessingResult)
        self.assertEqual(result.input_video_path, video_path)
        self.assertEqual(result.output_directory, output_dir)
        self.assertGreater(result.processed_frames, 0)


class TestSessionPostProcessor(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.recordings_dir = os.path.join(self.test_dir, 'recordings')
        self.processor = create_session_post_processor(self.recordings_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_test_session(self, session_id: str):
        session_dir = Path(self.recordings_dir) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        video_path = session_dir / 'test_video.mp4'
        self.create_test_video(str(video_path), frames=3)
        return session_dir

    def create_test_video(self, path: str, frames: int=3, fps: int=30):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(path), fourcc, fps, (50, 50))
        for i in range(frames):
            frame = np.ones((50, 50, 3), dtype=np.uint8) * (i * 50 + 50)
            writer.write(frame)
        writer.release()

    def test_session_discovery(self):
        sessions = self.processor.discover_sessions()
        self.assertEqual(len(sessions), 0)
        self.create_test_session('test_session_001')
        sessions = self.processor.discover_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertIn('test_session_001', sessions)

    def test_get_session_videos(self):
        session_id = 'test_session_002'
        self.create_test_session(session_id)
        videos = self.processor.get_session_videos(session_id)
        self.assertEqual(len(videos), 1)
        self.assertTrue(videos[0].endswith('test_video.mp4'))

    def test_processing_status(self):
        session_id = 'test_session_003'
        self.create_test_session(session_id)
        status = self.processor.get_processing_status(session_id)
        self.assertEqual(len(status), 1)
        self.assertFalse(list(status.values())[0])

    def test_available_methods(self):
        methods = self.processor.get_available_methods()
        expected = ['mediapipe', 'color_based', 'contour_based']
        self.assertEqual(sorted(methods), sorted(expected))


class TestIntegrationEndToEnd(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.recordings_dir = os.path.join(self.test_dir, 'recordings')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_realistic_test_video(self, path: str, frames: int=10):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(path), fourcc, 30, (320, 240))
        for i in range(frames):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            frame[:] = [20, 30, 40]
            center_x = 160 + int(20 * np.sin(i * 0.5))
            center_y = 120 + int(10 * np.cos(i * 0.3))
            cv2.circle(frame, (center_x, center_y), 30, [15, 100, 180], -1)
            for j in range(5):
                angle = j * 0.6 + i * 0.1
                finger_x = center_x + int(25 * np.cos(angle))
                finger_y = center_y + int(25 * np.sin(angle))
                cv2.circle(frame, (finger_x, finger_y), 8, [10, 80, 160], -1)
            writer.write(frame)
        writer.release()

    def test_end_to_end_processing(self):
        session_id = 'integration_test_session'
        session_dir = Path(self.recordings_dir) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        video_path = session_dir / 'webcam_recording.mp4'
        self.create_realistic_test_video(str(video_path), frames=5)
        processor = create_session_post_processor(self.recordings_dir)
        sessions = processor.discover_sessions()
        self.assertIn(session_id, sessions)
        results = processor.process_session(session_id, method=
            'color_based', output_cropped=True, output_masks=True)
        self.assertEqual(len(results), 1)
        result = list(results.values())[0]
        self.assertIsInstance(result, ProcessingResult)
        self.assertGreater(result.processed_frames, 0)
        output_dir = session_dir / 'hand_segmentation_webcam_recording'
        self.assertTrue(output_dir.exists())
        metadata_file = output_dir / 'processing_metadata.json'
        self.assertTrue(metadata_file.exists())
        status = processor.get_processing_status(session_id)
        self.assertEqual(len(status), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
