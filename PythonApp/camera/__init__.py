"""
Camera Module
============

Provides webcam management and live preview functionality for USB cameras.
Also includes video playback functionality for emotion elicitation experiments.
Integrates with OpenCV for camera capture and PyQt for GUI display.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import time
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import OpenCV
try:
    import cv2
    OPENCV_AVAILABLE = True
    logger.info("OpenCV available for camera functionality")
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not available - camera features disabled")

# Try to import PyQt for GUI integration
try:
    from PyQt6.QtCore import QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtWidgets import QLabel
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtCore import QThread, pyqtSignal, QTimer
        from PyQt5.QtGui import QImage, QPixmap
        from PyQt5.QtWidgets import QLabel
        PYQT_VERSION = 5
    except ImportError:
        PYQT_VERSION = None
        logger.warning("PyQt not available - GUI features disabled")


@dataclass
class CameraInfo:
    """Information about a detected camera."""
    index: int
    name: str
    width: int = 640
    height: int = 480
    fps: int = 30
    is_available: bool = True


class CameraCapture(QThread if PYQT_VERSION else object):
    """Thread for capturing frames from a webcam."""
    
    # Signals for PyQt integration
    if PYQT_VERSION:
        frame_ready = pyqtSignal(object)  # Emits numpy array
        error_occurred = pyqtSignal(str)
        camera_disconnected = pyqtSignal()
    
    def __init__(self, camera_index: int = 0):
        if PYQT_VERSION:
            super().__init__()
        
        self.camera_index = camera_index
        self.capture = None
        self.running = False
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480
        
    def initialize_camera(self) -> bool:
        """Initialize the camera capture."""
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV not available for camera capture")
            return False
            
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            if not self.capture.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
                
            # Set camera properties
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify actual properties
            actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.capture.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera {self.camera_index} initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera {self.camera_index}: {e}")
            return False
    
    def start_capture(self):
        """Start capturing frames."""
        if self.initialize_camera():
            self.running = True
            if PYQT_VERSION:
                self.start()  # Start the thread
            else:
                logger.warning("PyQt not available - cannot start threaded capture")
    
    def stop_capture(self):
        """Stop capturing frames."""
        self.running = False
        if PYQT_VERSION:
            self.wait()  # Wait for thread to finish
        if self.capture:
            self.capture.release()
            self.capture = None
    
    def run(self):
        """Main capture loop (runs in thread if PyQt available)."""
        if not self.capture:
            return
            
        while self.running:
            try:
                ret, frame = self.capture.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    if PYQT_VERSION:
                        self.camera_disconnected.emit()
                    break
                
                # Emit frame signal
                if PYQT_VERSION:
                    self.frame_ready.emit(frame)
                
                # Control frame rate
                time.sleep(1.0 / self.fps)
                
            except Exception as e:
                logger.error(f"Error capturing frame: {e}")
                if PYQT_VERSION:
                    self.error_occurred.emit(str(e))
                break
    
    def get_single_frame(self):
        """Get a single frame (for non-threaded operation)."""
        if not self.capture:
            return None
            
        ret, frame = self.capture.read()
        return frame if ret else None


class VideoPlayer(QThread if PYQT_VERSION else object):
    """Thread for playing video files for emotion elicitation experiments."""
    
    # Signals for PyQt integration
    if PYQT_VERSION:
        frame_ready = pyqtSignal(object)  # Emits numpy array
        position_changed = pyqtSignal(int)  # Current position in milliseconds
        duration_changed = pyqtSignal(int)  # Total duration in milliseconds
        playback_finished = pyqtSignal()
        error_occurred = pyqtSignal(str)
    
    def __init__(self, video_path: str = ""):
        if PYQT_VERSION:
            super().__init__()
        
        self.video_path = video_path
        self.capture = None
        self.playing = False
        self.paused = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480
        self.seek_to_frame = -1  # For seeking functionality
        
    def load_video(self, video_path: str) -> bool:
        """Load a video file for playback."""
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV not available for video playback")
            return False
            
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False
            
        try:
            # Release any existing capture
            if self.capture:
                self.capture.release()
                
            self.video_path = video_path
            self.capture = cv2.VideoCapture(video_path)
            
            if not self.capture.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return False
            
            # Get video properties
            self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.capture.get(cv2.CAP_PROP_FPS)
            self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            duration_ms = int((self.total_frames / self.fps) * 1000) if self.fps > 0 else 0
            
            logger.info(f"Video loaded: {video_path}")
            logger.info(f"  Dimensions: {self.frame_width}x{self.frame_height}")
            logger.info(f"  FPS: {self.fps}")
            logger.info(f"  Frames: {self.total_frames}")
            logger.info(f"  Duration: {duration_ms}ms")
            
            if PYQT_VERSION:
                self.duration_changed.emit(duration_ms)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading video {video_path}: {e}")
            return False
    
    def start_playback(self):
        """Start video playback."""
        if not self.capture:
            logger.error("No video loaded")
            return False
            
        self.playing = True
        self.paused = False
        
        if PYQT_VERSION:
            self.start()  # Start the thread
        else:
            logger.warning("PyQt not available - cannot start threaded playback")
            
        return True
    
    def pause_playback(self):
        """Pause video playback."""
        self.paused = True
    
    def resume_playback(self):
        """Resume video playback."""
        self.paused = False
    
    def stop_playback(self):
        """Stop video playback."""
        self.playing = False
        self.paused = False
        if PYQT_VERSION:
            self.wait()  # Wait for thread to finish
        if self.capture:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            self.current_frame = 0
    
    def seek_to_position(self, position_ms: int):
        """Seek to a specific position in the video."""
        if not self.capture or self.fps <= 0:
            return
            
        target_frame = int((position_ms / 1000.0) * self.fps)
        target_frame = max(0, min(target_frame, self.total_frames - 1))
        self.seek_to_frame = target_frame
    
    def get_current_position_ms(self) -> int:
        """Get current playback position in milliseconds."""
        if self.fps <= 0:
            return 0
        return int((self.current_frame / self.fps) * 1000)
    
    def get_duration_ms(self) -> int:
        """Get total video duration in milliseconds."""
        if self.fps <= 0:
            return 0
        return int((self.total_frames / self.fps) * 1000)
    
    def run(self):
        """Main playback loop (runs in thread if PyQt available)."""
        if not self.capture:
            return
            
        while self.playing:
            try:
                # Handle seeking
                if self.seek_to_frame >= 0:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.seek_to_frame)
                    self.current_frame = self.seek_to_frame
                    self.seek_to_frame = -1
                    
                    if PYQT_VERSION:
                        self.position_changed.emit(self.get_current_position_ms())
                
                # Handle pause
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                ret, frame = self.capture.read()
                if not ret:
                    logger.info("Video playback finished")
                    if PYQT_VERSION:
                        self.playback_finished.emit()
                    break
                
                # Emit frame signal
                if PYQT_VERSION:
                    self.frame_ready.emit(frame)
                    self.position_changed.emit(self.get_current_position_ms())
                
                self.current_frame += 1
                
                # Control frame rate
                time.sleep(1.0 / self.fps)
                
            except Exception as e:
                logger.error(f"Error during video playback: {e}")
                if PYQT_VERSION:
                    self.error_occurred.emit(str(e))
                break
    
    def release(self):
        """Release video resources."""
        self.stop_playback()
        if self.capture:
            self.capture.release()
            self.capture = None


class WebcamManager:
    """Manages USB webcam detection and streaming."""
    
    def __init__(self):
        self.available_cameras: List[CameraInfo] = []
        self.active_capture: Optional[CameraCapture] = None
        self.active_video_player: Optional[VideoPlayer] = None
        
    def detect_cameras(self) -> List[CameraInfo]:
        """Detect all available cameras."""
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available - cannot detect cameras")
            return []
            
        cameras = []
        
        # Test camera indices 0-4 (usually sufficient for most systems)
        for index in range(5):
            try:
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    # Get camera properties
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    camera_info = CameraInfo(
                        index=index,
                        name=f"Camera {index}",
                        width=width,
                        height=height,
                        fps=int(fps) if fps > 0 else 30
                    )
                    cameras.append(camera_info)
                    logger.info(f"Detected camera {index}: {width}x{height}")
                    
                cap.release()
                
            except Exception as e:
                logger.debug(f"Camera {index} not available: {e}")
                continue
        
        self.available_cameras = cameras
        return cameras
    
    def start_camera_preview(self, camera_index: int = 0) -> Optional[CameraCapture]:
        """Start preview for specified camera."""
        if self.active_capture:
            self.stop_camera_preview()
            
        # Stop video playback if active
        if self.active_video_player:
            self.stop_video_playback()
            
        self.active_capture = CameraCapture(camera_index)
        self.active_capture.start_capture()
        return self.active_capture
    
    def stop_camera_preview(self):
        """Stop the active camera preview."""
        if self.active_capture:
            self.active_capture.stop_capture()
            self.active_capture = None
    
    def start_video_playback(self, video_path: str) -> Optional[VideoPlayer]:
        """Start video playback for emotion elicitation."""
        if self.active_video_player:
            self.stop_video_playback()
            
        # Stop camera preview if active
        if self.active_capture:
            self.stop_camera_preview()
            
        self.active_video_player = VideoPlayer()
        if self.active_video_player.load_video(video_path):
            return self.active_video_player
        else:
            self.active_video_player = None
            return None
    
    def stop_video_playback(self):
        """Stop the active video playback."""
        if self.active_video_player:
            self.active_video_player.release()
            self.active_video_player = None
    
    def get_camera_info(self, camera_index: int) -> Optional[CameraInfo]:
        """Get information about a specific camera."""
        for camera in self.available_cameras:
            if camera.index == camera_index:
                return camera
        return None
    
    def is_camera_available(self, camera_index: int) -> bool:
        """Check if a camera is available."""
        return any(cam.index == camera_index for cam in self.available_cameras)
    
    def get_supported_video_formats(self) -> List[str]:
        """Get list of supported video file formats."""
        return [
            "mp4", "avi", "mov", "mkv", "wmv", "flv", 
            "webm", "m4v", "3gp", "ogv", "mpg", "mpeg"
        ]