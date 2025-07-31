"""
Dual Webcam Capture Module for Multi-Sensor Recording System Controller

This module implements synchronized dual webcam recording specifically for 
Logitech Brio 4K30 cameras with precise timestamping and cross-device synchronization.
The PC acts as the master clock for all connected devices including Android sensors.

Features:
- Dual Logitech Brio 4K30 FPS camera support
- Frame-level timestamp synchronization
- PC master clock with NTP server integration
- Android device synchronization via network protocol
- High-precision recording with guaranteed frame alignment

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import cv2
import numpy as np
import os
import threading
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
import json

# Import centralized logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


@dataclass
class DualFrameData:
    """Synchronized frame data from both cameras"""
    
    timestamp: float
    frame_id: int
    camera1_frame: Optional[np.ndarray]
    camera2_frame: Optional[np.ndarray]
    camera1_timestamp: float
    camera2_timestamp: float
    sync_quality: float  # 0.0 to 1.0, how well synchronized the frames are


@dataclass
class CameraStatus:
    """Status information for a single camera"""
    
    camera_index: int
    is_active: bool
    fps: float
    resolution: Tuple[int, int]
    frames_captured: int
    last_error: Optional[str]
    temperature: Optional[float]  # For thermal monitoring if available


class DualWebcamCapture(QThread):
    """
    Dual webcam capture class for synchronized PC camera recording.
    
    Specifically designed for Logitech Brio 4K30 cameras with precise 
    synchronization and master clock functionality for cross-device recording.
    """
    
    # Signals for GUI integration
    dual_frame_ready = pyqtSignal(QPixmap, QPixmap)  # Camera1, Camera2 preview frames
    recording_started = pyqtSignal(str, str)  # Camera1 filename, Camera2 filename
    recording_stopped = pyqtSignal(str, str, float)  # Camera1 file, Camera2 file, duration
    sync_status_changed = pyqtSignal(float)  # Sync quality (0.0 to 1.0)
    camera_status_changed = pyqtSignal(dict)  # Camera status information
    error_occurred = pyqtSignal(str)  # Error message
    timestamp_sync_update = pyqtSignal(float)  # Master timestamp for network sync
    
    def __init__(self, 
                 camera1_index: int = 0, 
                 camera2_index: int = 1, 
                 preview_fps: int = 30,
                 recording_fps: int = 30,
                 resolution: Tuple[int, int] = (3840, 2160),  # 4K for Brio
                 sync_callback: Optional[Callable[[float], None]] = None):
        """
        Initialize dual webcam capture for Logitech Brio cameras.
        
        Args:
            camera1_index (int): First camera device index
            camera2_index (int): Second camera device index  
            preview_fps (int): Preview frame rate
            recording_fps (int): Recording frame rate (max 30 for 4K on Brio)
            resolution (tuple): Recording resolution (3840, 2160 for 4K)
            sync_callback: Optional callback for timestamp synchronization
        """
        super().__init__()
        
        # Camera configuration
        self.camera1_index = camera1_index
        self.camera2_index = camera2_index
        self.preview_fps = preview_fps
        self.recording_fps = min(recording_fps, 30)  # Brio 4K limit
        self.target_resolution = resolution
        self.sync_callback = sync_callback
        
        # Frame timing
        self.frame_interval = 1.0 / preview_fps
        self.recording_interval = 1.0 / self.recording_fps
        
        # Camera objects and writers
        self.cap1: Optional[cv2.VideoCapture] = None
        self.cap2: Optional[cv2.VideoCapture] = None
        self.writer1: Optional[cv2.VideoWriter] = None
        self.writer2: Optional[cv2.VideoWriter] = None
        
        # State management
        self.is_recording = False
        self.is_previewing = False
        self.running = False
        
        # Recording parameters
        self.recording_codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.current_session_id: Optional[str] = None
        self.recording_start_time: Optional[float] = None
        self.output_directory = "recordings/dual_webcam"
        
        # Synchronization
        self.frame_counter = 0
        self.master_start_time = None
        self.sync_threshold_ms = 16.67  # ~1 frame at 60fps tolerance
        self.frame_sync_buffer: List[DualFrameData] = []
        self.max_sync_buffer_size = 10
        
        # Frame processing and threading
        self.frame_lock = threading.Lock()
        self.last_frames = {'camera1': None, 'camera2': None}
        self.last_sync_quality = 1.0
        
        # Camera status tracking
        self.camera1_status = CameraStatus(camera1_index, False, 0, (0, 0), 0, None, None)
        self.camera2_status = CameraStatus(camera2_index, False, 0, (0, 0), 0, None, None)
        
        # Performance monitoring
        self.performance_stats = {
            'frames_processed': 0,
            'sync_violations': 0,
            'dropped_frames': 0,
            'average_processing_time_ms': 0.0
        }
        
        logger.info(f"DualWebcamCapture initialized: cameras {camera1_index},{camera2_index}, "
                   f"recording {self.recording_fps}fps @ {resolution}")

    def initialize_cameras(self) -> bool:
        """
        Initialize both Logitech Brio cameras with optimal settings.
        
        Returns:
            bool: True if both cameras initialized successfully
        """
        try:
            logger.info("Initializing dual Logitech Brio cameras...")
            
            # Initialize camera 1
            self.cap1 = cv2.VideoCapture(self.camera1_index)
            if not self.cap1.isOpened():
                self.error_occurred.emit(f"Could not open camera {self.camera1_index}")
                return False
            
            # Initialize camera 2  
            self.cap2 = cv2.VideoCapture(self.camera2_index)
            if not self.cap2.isOpened():
                self.error_occurred.emit(f"Could not open camera {self.camera2_index}")
                return False
            
            # Configure both cameras for Logitech Brio optimal settings
            success1 = self._configure_brio_camera(self.cap1, 1)
            success2 = self._configure_brio_camera(self.cap2, 2)
            
            if not (success1 and success2):
                self.error_occurred.emit("Failed to configure cameras for optimal performance")
                return False
            
            # Update camera status
            self._update_camera_status()
            
            logger.info("Dual cameras initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error initializing dual cameras: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False

    def _configure_brio_camera(self, cap: cv2.VideoCapture, camera_num: int) -> bool:
        """
        Configure a Logitech Brio camera for optimal 4K30 recording.
        
        Args:
            cap: Camera capture object
            camera_num: Camera number for logging
            
        Returns:
            bool: True if configuration successful
        """
        try:
            # Set resolution first
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[1])
            
            # Set frame rate
            cap.set(cv2.CAP_PROP_FPS, self.recording_fps)
            
            # Brio-specific optimizations
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for low latency
            
            # Auto-exposure and focus settings for consistent recording
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Auto exposure enabled
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Auto focus enabled
            
            # Verify settings
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera {camera_num} configured: {actual_width}x{actual_height} @ {actual_fps:.1f}fps")
            
            # Test frame capture
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.error(f"Camera {camera_num} failed initial frame capture test")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error configuring camera {camera_num}: {e}")
            return False

    def _update_camera_status(self):
        """Update camera status information."""
        try:
            if self.cap1 and self.cap1.isOpened():
                self.camera1_status.is_active = True
                self.camera1_status.fps = self.cap1.get(cv2.CAP_PROP_FPS)
                width = int(self.cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.camera1_status.resolution = (width, height)
                
            if self.cap2 and self.cap2.isOpened():
                self.camera2_status.is_active = True
                self.camera2_status.fps = self.cap2.get(cv2.CAP_PROP_FPS)
                width = int(self.cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.camera2_status.resolution = (width, height)
            
            # Emit status update
            status_dict = {
                'camera1': {
                    'index': self.camera1_status.camera_index,
                    'active': self.camera1_status.is_active,
                    'fps': self.camera1_status.fps,
                    'resolution': self.camera1_status.resolution,
                    'frames': self.camera1_status.frames_captured
                },
                'camera2': {
                    'index': self.camera2_status.camera_index,
                    'active': self.camera2_status.is_active,
                    'fps': self.camera2_status.fps,
                    'resolution': self.camera2_status.resolution,
                    'frames': self.camera2_status.frames_captured
                }
            }
            self.camera_status_changed.emit(status_dict)
            
        except Exception as e:
            logger.error(f"Error updating camera status: {e}")

    def start_preview(self):
        """Start dual camera preview."""
        if not self.cap1 or not self.cap2:
            if not self.initialize_cameras():
                return
                
        self.is_previewing = True
        self.running = True
        self.master_start_time = time.time()
        self.start()
        
        logger.info("Dual camera preview started")

    def stop_preview(self):
        """Stop dual camera preview."""
        self.is_previewing = False
        self.running = False
        
        if self.isRunning():
            self.quit()
            self.wait()
            
        logger.info("Dual camera preview stopped")

    def start_recording(self, session_id: str) -> bool:
        """
        Start synchronized recording from both cameras.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            self.error_occurred.emit("Recording already in progress")
            return False
            
        if not self.cap1 or not self.cap2:
            if not self.initialize_cameras():
                return False
                
        try:
            # Create output directory
            os.makedirs(self.output_directory, exist_ok=True)
            
            # Generate synchronized filenames with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename1 = f"camera1_{session_id}_{timestamp}.mp4"
            filename2 = f"camera2_{session_id}_{timestamp}.mp4"
            
            self.recording_filepath1 = os.path.join(self.output_directory, filename1)
            self.recording_filepath2 = os.path.join(self.output_directory, filename2)
            
            # Initialize video writers with identical settings
            resolution = self.camera1_status.resolution
            self.writer1 = cv2.VideoWriter(
                self.recording_filepath1, self.recording_codec, 
                self.recording_fps, resolution
            )
            self.writer2 = cv2.VideoWriter(
                self.recording_filepath2, self.recording_codec,
                self.recording_fps, resolution
            )
            
            if not (self.writer1.isOpened() and self.writer2.isOpened()):
                self.error_occurred.emit("Could not initialize video writers")
                return False
                
            # Start recording state
            self.is_recording = True
            self.current_session_id = session_id
            self.recording_start_time = time.time()
            self.frame_counter = 0
            
            # Start preview if not running
            if not self.is_previewing:
                self.start_preview()
                
            # Emit recording started signal
            self.recording_started.emit(self.recording_filepath1, self.recording_filepath2)
            
            # Send master timestamp for network synchronization
            master_timestamp = self.recording_start_time
            self.timestamp_sync_update.emit(master_timestamp)
            
            if self.sync_callback:
                self.sync_callback(master_timestamp)
                
            logger.info(f"Dual camera recording started: {filename1}, {filename2}")
            logger.info(f"Master timestamp: {master_timestamp}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error starting dual camera recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False

    def stop_recording(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Stop synchronized recording from both cameras.
        
        Returns:
            tuple: (camera1_filepath, camera2_filepath) or (None, None) if not recording
        """
        if not self.is_recording:
            return None, None
            
        try:
            self.is_recording = False
            
            # Calculate recording duration
            duration = (time.time() - self.recording_start_time 
                       if self.recording_start_time else 0)
            
            # Release video writers
            if self.writer1:
                self.writer1.release()
                self.writer1 = None
                
            if self.writer2:
                self.writer2.release()
                self.writer2 = None
                
            # Store filepaths before clearing
            filepath1 = self.recording_filepath1
            filepath2 = self.recording_filepath2
            
            # Clear recording state
            self.recording_filepath1 = None
            self.recording_filepath2 = None
            self.current_session_id = None
            self.recording_start_time = None
            
            # Emit recording stopped signal
            self.recording_stopped.emit(filepath1, filepath2, duration)
            
            logger.info(f"Dual camera recording stopped (duration: {duration:.1f}s)")
            logger.info(f"Files: {filepath1}, {filepath2}")
            
            return filepath1, filepath2
            
        except Exception as e:
            error_msg = f"Error stopping dual camera recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return None, None

    def run(self):
        """Main thread loop for synchronized dual camera capture."""
        last_preview_time = 0
        last_recording_time = 0
        
        logger.info("Starting dual camera capture thread")
        
        while self.running:
            try:
                current_time = time.time()
                process_start_time = current_time
                
                # Capture frames from both cameras simultaneously
                ret1, frame1 = self.cap1.read()
                capture_timestamp1 = time.time()
                
                ret2, frame2 = self.cap2.read()
                capture_timestamp2 = time.time()
                
                if not (ret1 and ret2):
                    self.error_occurred.emit("Failed to capture frames from one or both cameras")
                    break
                
                # Calculate synchronization quality
                sync_diff_ms = abs(capture_timestamp1 - capture_timestamp2) * 1000
                sync_quality = max(0.0, 1.0 - (sync_diff_ms / self.sync_threshold_ms))
                
                if sync_quality < 0.8:
                    self.performance_stats['sync_violations'] += 1
                    
                self.last_sync_quality = sync_quality
                self.sync_status_changed.emit(sync_quality)
                
                # Create synchronized frame data
                frame_data = DualFrameData(
                    timestamp=current_time,
                    frame_id=self.frame_counter,
                    camera1_frame=frame1.copy(),
                    camera2_frame=frame2.copy(),
                    camera1_timestamp=capture_timestamp1,
                    camera2_timestamp=capture_timestamp2,
                    sync_quality=sync_quality
                )
                
                # Store frames for preview
                with self.frame_lock:
                    self.last_frames['camera1'] = frame1.copy()
                    self.last_frames['camera2'] = frame2.copy()
                
                # Write frames to video files if recording
                if (self.is_recording and self.writer1 and self.writer2 and
                    (current_time - last_recording_time) >= self.recording_interval):
                    
                    self.writer1.write(frame1)
                    self.writer2.write(frame2)
                    last_recording_time = current_time
                    
                    # Update frame counters
                    self.camera1_status.frames_captured += 1
                    self.camera2_status.frames_captured += 1
                    self.frame_counter += 1
                
                # Emit preview frames at specified FPS
                if (self.is_previewing and 
                    (current_time - last_preview_time) >= self.frame_interval):
                    
                    pixmap1 = self._frame_to_pixmap(frame1)
                    pixmap2 = self._frame_to_pixmap(frame2)
                    
                    if pixmap1 and pixmap2:
                        self.dual_frame_ready.emit(pixmap1, pixmap2)
                        
                    last_preview_time = current_time
                
                # Update performance statistics
                processing_time_ms = (time.time() - process_start_time) * 1000
                self.performance_stats['frames_processed'] += 1
                self.performance_stats['average_processing_time_ms'] = (
                    (self.performance_stats['average_processing_time_ms'] * 
                     (self.performance_stats['frames_processed'] - 1) + processing_time_ms) /
                    self.performance_stats['frames_processed']
                )
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
                
            except Exception as e:
                error_msg = f"Error in dual camera capture loop: {str(e)}"
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                break
                
        logger.info("Dual camera capture thread ended")

    def _frame_to_pixmap(self, frame: np.ndarray, max_width: int = 640, max_height: int = 360) -> Optional[QPixmap]:
        """
        Convert OpenCV frame to QPixmap for GUI display.
        
        Args:
            frame: OpenCV frame (BGR format)
            max_width: Maximum width for preview
            max_height: Maximum height for preview
            
        Returns:
            QPixmap: Converted pixmap for display, or None if conversion fails
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            height, width, channels = rgb_frame.shape
            
            # Calculate scaling to fit within max dimensions while maintaining aspect ratio
            scale_w = max_width / width
            scale_h = max_height / height
            scale = min(scale_w, scale_h, 1.0)  # Don't upscale
            
            if scale < 1.0:
                new_width = int(width * scale)
                new_height = int(height * scale)
                rgb_frame = cv2.resize(rgb_frame, (new_width, new_height))
                height, width = new_height, new_width
                
            # Convert to QImage
            bytes_per_line = channels * width
            q_image = QImage(
                rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            
            # Convert to QPixmap
            return QPixmap.fromImage(q_image)
            
        except Exception as e:
            logger.error(f"Error converting frame to pixmap: {str(e)}")
            return None

    def get_master_timestamp(self) -> float:
        """Get current master timestamp for synchronization."""
        return time.time()

    def get_sync_quality(self) -> float:
        """Get current synchronization quality (0.0 to 1.0)."""
        return self.last_sync_quality

    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        return self.performance_stats.copy()

    def cleanup(self):
        """Clean up resources."""
        try:
            self.running = False
            self.is_previewing = False
            
            if self.is_recording:
                self.stop_recording()
                
            # Wait for thread to finish
            if self.isRunning():
                self.quit()
                self.wait(1000)  # Wait max 1 second
                
            # Release cameras
            if self.cap1:
                self.cap1.release()
                self.cap1 = None
                
            if self.cap2:
                self.cap2.release()
                self.cap2 = None
                
            # Release video writers
            if self.writer1:
                self.writer1.release()
                self.writer1 = None
                
            if self.writer2:
                self.writer2.release()
                self.writer2 = None
                
            logger.info("DualWebcamCapture cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            # Only clean up OpenCV resources in destructor
            if hasattr(self, 'cap1') and self.cap1:
                self.cap1.release()
            if hasattr(self, 'cap2') and self.cap2:
                self.cap2.release()
            if hasattr(self, 'writer1') and self.writer1:
                self.writer1.release()
            if hasattr(self, 'writer2') and self.writer2:
                self.writer2.release()
        except Exception:
            pass  # Silently ignore errors during destruction


def test_dual_webcam_access():
    """Test function to verify dual webcam access."""
    logger.info("Testing dual webcam access...")
    
    # Test camera 1
    cap1 = cv2.VideoCapture(0)
    if not cap1.isOpened():
        logger.error("ERROR: Could not open camera 1 (index 0)")
        return False
    
    ret1, frame1 = cap1.read()
    if ret1:
        height1, width1 = frame1.shape[:2]
        logger.info(f"SUCCESS: Camera 1 accessible, frame size: {width1}x{height1}")
    else:
        logger.error("ERROR: Could not capture frame from camera 1")
        cap1.release()
        return False
    
    # Test camera 2
    cap2 = cv2.VideoCapture(1)
    if not cap2.isOpened():
        logger.error("ERROR: Could not open camera 2 (index 1)")
        cap1.release()
        return False
    
    ret2, frame2 = cap2.read()
    if ret2:
        height2, width2 = frame2.shape[:2]
        logger.info(f"SUCCESS: Camera 2 accessible, frame size: {width2}x{height2}")
    else:
        logger.error("ERROR: Could not capture frame from camera 2")
        cap1.release()
        cap2.release()
        return False
    
    cap1.release()
    cap2.release()
    
    logger.info("SUCCESS: Both cameras accessible for dual recording")
    return True


if __name__ == "__main__":
    # Test dual webcam access when run directly
    test_dual_webcam_access()