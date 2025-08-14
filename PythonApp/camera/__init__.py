"""
Camera Module
============

Provides webcam management and live preview functionality for USB cameras.
Integrates with OpenCV for camera capture and PyQt for GUI display.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import time

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


class WebcamManager:
    """Manages USB webcam detection and streaming."""
    
    def __init__(self):
        self.available_cameras: List[CameraInfo] = []
        self.active_capture: Optional[CameraCapture] = None
        
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
            
        self.active_capture = CameraCapture(camera_index)
        self.active_capture.start_capture()
        return self.active_capture
    
    def stop_camera_preview(self):
        """Stop the active camera preview."""
        if self.active_capture:
            self.active_capture.stop_capture()
            self.active_capture = None
    
    def get_camera_info(self, camera_index: int) -> Optional[CameraInfo]:
        """Get information about a specific camera."""
        for camera in self.available_cameras:
            if camera.index == camera_index:
                return camera
        return None
    
    def is_camera_available(self, camera_index: int) -> bool:
        """Check if a camera is available."""
        return any(cam.index == camera_index for cam in self.available_cameras)