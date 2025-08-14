"""
Camera Calibration Module
========================

Provides camera calibration utilities for thermal-RGB alignment.
Uses OpenCV for camera calibration and stereo rectification.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np

logger = logging.getLogger(__name__)

# Try to import OpenCV
try:
    import cv2
    OPENCV_AVAILABLE = True
    logger.info("OpenCV available for camera calibration")
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not available - calibration features disabled")


@dataclass
class CalibrationPattern:
    """Configuration for calibration pattern."""
    pattern_type: str = "checkerboard"  # "checkerboard" or "circles"
    pattern_size: Tuple[int, int] = (9, 6)  # (width, height) in pattern units
    square_size: float = 25.0  # Size of each square/circle in mm
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CameraIntrinsics:
    """Camera intrinsic parameters."""
    camera_matrix: np.ndarray
    distortion_coeffs: np.ndarray
    image_size: Tuple[int, int]
    reprojection_error: float
    
    def to_dict(self) -> dict:
        return {
            'camera_matrix': self.camera_matrix.tolist(),
            'distortion_coeffs': self.distortion_coeffs.tolist(),
            'image_size': self.image_size,
            'reprojection_error': self.reprojection_error
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            camera_matrix=np.array(data['camera_matrix']),
            distortion_coeffs=np.array(data['distortion_coeffs']),
            image_size=tuple(data['image_size']),
            reprojection_error=data['reprojection_error']
        )


@dataclass
class StereoCalibration:
    """Stereo calibration parameters for camera pair."""
    rgb_intrinsics: CameraIntrinsics
    thermal_intrinsics: CameraIntrinsics
    rotation_matrix: np.ndarray
    translation_vector: np.ndarray
    essential_matrix: np.ndarray
    fundamental_matrix: np.ndarray
    reprojection_error: float
    
    def to_dict(self) -> dict:
        return {
            'rgb_intrinsics': self.rgb_intrinsics.to_dict(),
            'thermal_intrinsics': self.thermal_intrinsics.to_dict(),
            'rotation_matrix': self.rotation_matrix.tolist(),
            'translation_vector': self.translation_vector.tolist(),
            'essential_matrix': self.essential_matrix.tolist(),
            'fundamental_matrix': self.fundamental_matrix.tolist(),
            'reprojection_error': self.reprojection_error
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            rgb_intrinsics=CameraIntrinsics.from_dict(data['rgb_intrinsics']),
            thermal_intrinsics=CameraIntrinsics.from_dict(data['thermal_intrinsics']),
            rotation_matrix=np.array(data['rotation_matrix']),
            translation_vector=np.array(data['translation_vector']),
            essential_matrix=np.array(data['essential_matrix']),
            fundamental_matrix=np.array(data['fundamental_matrix']),
            reprojection_error=data['reprojection_error']
        )


class CalibrationSession:
    """Manages a calibration session for collecting calibration images."""
    
    def __init__(self, session_id: str, pattern: CalibrationPattern, output_dir: str):
        self.session_id = session_id
        self.pattern = pattern
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.rgb_images: List[np.ndarray] = []
        self.thermal_images: List[np.ndarray] = []
        self.capture_count = 0
        self.max_captures = 20
        
        # Pattern detection configuration
        self.detection_flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        if self.pattern.pattern_type == "checkerboard":
            self.detection_flags += cv2.CALIB_CB_FAST_CHECK
    
    def add_image_pair(self, rgb_image: np.ndarray, thermal_image: np.ndarray) -> Tuple[bool, str]:
        """Add a pair of RGB and thermal images to the calibration session."""
        if not OPENCV_AVAILABLE:
            return False, "OpenCV not available"
        
        if self.capture_count >= self.max_captures:
            return False, f"Maximum captures ({self.max_captures}) reached"
        
        try:
            # Convert images to grayscale for pattern detection
            rgb_gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY) if len(rgb_image.shape) == 3 else rgb_image
            thermal_gray = cv2.cvtColor(thermal_image, cv2.COLOR_BGR2GRAY) if len(thermal_image.shape) == 3 else thermal_image
            
            # Detect calibration pattern in both images
            rgb_found, rgb_corners = self._detect_pattern(rgb_gray)
            thermal_found, thermal_corners = self._detect_pattern(thermal_gray)
            
            if not rgb_found:
                return False, "Pattern not detected in RGB image"
            
            if not thermal_found:
                return False, "Pattern not detected in thermal image"
            
            # Store images
            self.rgb_images.append(rgb_image.copy())
            self.thermal_images.append(thermal_image.copy())
            
            # Save images to disk
            rgb_filename = self.output_dir / f"rgb_{self.capture_count:03d}.png"
            thermal_filename = self.output_dir / f"thermal_{self.capture_count:03d}.png"
            
            cv2.imwrite(str(rgb_filename), rgb_image)
            cv2.imwrite(str(thermal_filename), thermal_image)
            
            self.capture_count += 1
            
            logger.info(f"Captured image pair {self.capture_count}/{self.max_captures} for calibration")
            return True, f"Captured {self.capture_count}/{self.max_captures}"
            
        except Exception as e:
            logger.error(f"Error adding image pair: {e}")
            return False, f"Error: {e}"
    
    def _detect_pattern(self, image: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """Detect calibration pattern in image."""
        if self.pattern.pattern_type == "checkerboard":
            found, corners = cv2.findChessboardCorners(
                image, 
                self.pattern.pattern_size,
                self.detection_flags
            )
            
            if found:
                # Refine corner positions
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners = cv2.cornerSubPix(image, corners, (11, 11), (-1, -1), criteria)
            
            return found, corners
        
        elif self.pattern.pattern_type == "circles":
            found, centers = cv2.findCirclesGrid(
                image,
                self.pattern.pattern_size,
                cv2.CALIB_CB_SYMMETRIC_GRID
            )
            return found, centers
        
        else:
            return False, None
    
    def is_ready_for_calibration(self) -> bool:
        """Check if enough images have been captured for calibration."""
        return len(self.rgb_images) >= 10  # Minimum 10 image pairs
    
    def get_status(self) -> dict:
        """Get current calibration session status."""
        return {
            'session_id': self.session_id,
            'capture_count': self.capture_count,
            'max_captures': self.max_captures,
            'progress_percent': (self.capture_count / self.max_captures) * 100,
            'ready_for_calibration': self.is_ready_for_calibration(),
            'pattern': self.pattern.to_dict()
        }


class CalibrationManager:
    """Manages camera calibration processes and results."""
    
    def __init__(self, calibration_dir: str = "calibrations"):
        self.calibration_dir = Path(calibration_dir)
        self.calibration_dir.mkdir(exist_ok=True)
        
        self.active_session: Optional[CalibrationSession] = None
        self.stored_calibrations: Dict[str, dict] = {}
        
        # Load existing calibrations
        self._load_stored_calibrations()
    
    def start_calibration_session(self, device_id: str, pattern: CalibrationPattern) -> CalibrationSession:
        """Start a new calibration session."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"calibration_{device_id}_{timestamp}"
        
        session_dir = self.calibration_dir / session_id
        self.active_session = CalibrationSession(session_id, pattern, str(session_dir))
        
        logger.info(f"Started calibration session: {session_id}")
        return self.active_session
    
    def add_calibration_images(self, rgb_image: np.ndarray, thermal_image: np.ndarray) -> Tuple[bool, str]:
        """Add images to the active calibration session."""
        if not self.active_session:
            return False, "No active calibration session"
        
        return self.active_session.add_image_pair(rgb_image, thermal_image)
    
    def compute_calibration(self, device_id: str) -> Tuple[bool, Optional[StereoCalibration], str]:
        """Compute calibration from captured images."""
        if not OPENCV_AVAILABLE:
            return False, None, "OpenCV not available"
        
        if not self.active_session:
            return False, None, "No active calibration session"
        
        if not self.active_session.is_ready_for_calibration():
            return False, None, "Not enough images captured"
        
        try:
            # Prepare object points
            object_points = self._generate_object_points()
            
            # Detect corners in all images
            rgb_image_points = []
            thermal_image_points = []
            valid_object_points = []
            
            for i, (rgb_img, thermal_img) in enumerate(zip(self.active_session.rgb_images, self.active_session.thermal_images)):
                rgb_gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY) if len(rgb_img.shape) == 3 else rgb_img
                thermal_gray = cv2.cvtColor(thermal_img, cv2.COLOR_BGR2GRAY) if len(thermal_img.shape) == 3 else thermal_img
                
                rgb_found, rgb_corners = self.active_session._detect_pattern(rgb_gray)
                thermal_found, thermal_corners = self.active_session._detect_pattern(thermal_gray)
                
                if rgb_found and thermal_found:
                    rgb_image_points.append(rgb_corners)
                    thermal_image_points.append(thermal_corners)
                    valid_object_points.append(object_points)
            
            if len(valid_object_points) < 10:
                return False, None, "Not enough valid image pairs for calibration"
            
            # Get image sizes
            rgb_image_size = self.active_session.rgb_images[0].shape[:2][::-1]
            thermal_image_size = self.active_session.thermal_images[0].shape[:2][::-1]
            
            # Calibrate individual cameras
            rgb_intrinsics = self._calibrate_single_camera(
                valid_object_points, rgb_image_points, rgb_image_size
            )
            
            thermal_intrinsics = self._calibrate_single_camera(
                valid_object_points, thermal_image_points, thermal_image_size
            )
            
            # Perform stereo calibration
            stereo_calibration = self._calibrate_stereo_cameras(
                valid_object_points, rgb_image_points, thermal_image_points,
                rgb_intrinsics, thermal_intrinsics, rgb_image_size
            )
            
            # Save calibration
            self._save_calibration(device_id, stereo_calibration)
            
            logger.info(f"Calibration completed for {device_id}, error: {stereo_calibration.reprojection_error:.3f}")
            return True, stereo_calibration, "Calibration successful"
            
        except Exception as e:
            logger.error(f"Error computing calibration: {e}")
            return False, None, f"Calibration error: {e}"
    
    def _generate_object_points(self) -> np.ndarray:
        """Generate 3D object points for the calibration pattern."""
        pattern = self.active_session.pattern
        object_points = np.zeros((pattern.pattern_size[0] * pattern.pattern_size[1], 3), np.float32)
        object_points[:, :2] = np.mgrid[0:pattern.pattern_size[0], 0:pattern.pattern_size[1]].T.reshape(-1, 2)
        object_points *= pattern.square_size
        return object_points
    
    def _calibrate_single_camera(self, object_points: List[np.ndarray], 
                                image_points: List[np.ndarray], 
                                image_size: Tuple[int, int]) -> CameraIntrinsics:
        """Calibrate a single camera."""
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, image_size, None, None
        )
        
        return CameraIntrinsics(
            camera_matrix=camera_matrix,
            distortion_coeffs=dist_coeffs,
            image_size=image_size,
            reprojection_error=ret
        )
    
    def _calibrate_stereo_cameras(self, object_points: List[np.ndarray],
                                 rgb_image_points: List[np.ndarray],
                                 thermal_image_points: List[np.ndarray],
                                 rgb_intrinsics: CameraIntrinsics,
                                 thermal_intrinsics: CameraIntrinsics,
                                 image_size: Tuple[int, int]) -> StereoCalibration:
        """Perform stereo calibration between RGB and thermal cameras."""
        
        # Stereo calibration
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
        
        ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
            object_points,
            rgb_image_points,
            thermal_image_points,
            rgb_intrinsics.camera_matrix,
            rgb_intrinsics.distortion_coeffs,
            thermal_intrinsics.camera_matrix,
            thermal_intrinsics.distortion_coeffs,
            image_size,
            criteria=criteria,
            flags=cv2.CALIB_FIX_INTRINSIC
        )
        
        return StereoCalibration(
            rgb_intrinsics=rgb_intrinsics,
            thermal_intrinsics=thermal_intrinsics,
            rotation_matrix=R,
            translation_vector=T,
            essential_matrix=E,
            fundamental_matrix=F,
            reprojection_error=ret
        )
    
    def _save_calibration(self, device_id: str, calibration: StereoCalibration):
        """Save calibration results to file."""
        timestamp = datetime.now().isoformat()
        
        calibration_data = {
            'device_id': device_id,
            'timestamp': timestamp,
            'calibration': calibration.to_dict()
        }
        
        filename = self.calibration_dir / f"{device_id}_calibration.json"
        
        with open(filename, 'w') as f:
            json.dump(calibration_data, f, indent=2)
        
        # Store in memory
        self.stored_calibrations[device_id] = calibration_data
        
        logger.info(f"Saved calibration for {device_id} to {filename}")
    
    def load_calibration(self, device_id: str) -> Optional[StereoCalibration]:
        """Load calibration for a device."""
        if device_id in self.stored_calibrations:
            calibration_data = self.stored_calibrations[device_id]
            return StereoCalibration.from_dict(calibration_data['calibration'])
        
        # Try to load from file
        filename = self.calibration_dir / f"{device_id}_calibration.json"
        if filename.exists():
            try:
                with open(filename, 'r') as f:
                    calibration_data = json.load(f)
                
                self.stored_calibrations[device_id] = calibration_data
                return StereoCalibration.from_dict(calibration_data['calibration'])
                
            except Exception as e:
                logger.error(f"Error loading calibration for {device_id}: {e}")
        
        return None
    
    def _load_stored_calibrations(self):
        """Load all stored calibrations from disk."""
        for calibration_file in self.calibration_dir.glob("*_calibration.json"):
            try:
                with open(calibration_file, 'r') as f:
                    calibration_data = json.load(f)
                
                device_id = calibration_data['device_id']
                self.stored_calibrations[device_id] = calibration_data
                
            except Exception as e:
                logger.error(f"Error loading calibration from {calibration_file}: {e}")
        
        logger.info(f"Loaded {len(self.stored_calibrations)} stored calibrations")
    
    def get_available_calibrations(self) -> List[dict]:
        """Get list of available calibrations."""
        calibrations = []
        
        for device_id, calibration_data in self.stored_calibrations.items():
            calibrations.append({
                'device_id': device_id,
                'timestamp': calibration_data['timestamp'],
                'reprojection_error': calibration_data['calibration']['reprojection_error']
            })
        
        return calibrations
    
    def get_session_status(self) -> Optional[dict]:
        """Get status of active calibration session."""
        if self.active_session:
            return self.active_session.get_status()
        return None
    
    def end_session(self):
        """End the active calibration session."""
        if self.active_session:
            logger.info(f"Ended calibration session: {self.active_session.session_id}")
            self.active_session = None


def apply_calibration_to_images(rgb_image: np.ndarray, thermal_image: np.ndarray, 
                               calibration: StereoCalibration) -> Tuple[np.ndarray, np.ndarray]:
    """Apply calibration to rectify and align RGB and thermal images."""
    if not OPENCV_AVAILABLE:
        return rgb_image, thermal_image
    
    try:
        # Compute rectification maps
        R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
            calibration.rgb_intrinsics.camera_matrix,
            calibration.rgb_intrinsics.distortion_coeffs,
            calibration.thermal_intrinsics.camera_matrix,
            calibration.thermal_intrinsics.distortion_coeffs,
            calibration.rgb_intrinsics.image_size,
            calibration.rotation_matrix,
            calibration.translation_vector
        )
        
        # Create rectification maps
        map1_rgb, map2_rgb = cv2.initUndistortRectifyMap(
            calibration.rgb_intrinsics.camera_matrix,
            calibration.rgb_intrinsics.distortion_coeffs,
            R1, P1, calibration.rgb_intrinsics.image_size, cv2.CV_16SC2
        )
        
        map1_thermal, map2_thermal = cv2.initUndistortRectifyMap(
            calibration.thermal_intrinsics.camera_matrix,
            calibration.thermal_intrinsics.distortion_coeffs,
            R2, P2, calibration.thermal_intrinsics.image_size, cv2.CV_16SC2
        )
        
        # Apply rectification
        rgb_rectified = cv2.remap(rgb_image, map1_rgb, map2_rgb, cv2.INTER_LINEAR)
        thermal_rectified = cv2.remap(thermal_image, map1_thermal, map2_thermal, cv2.INTER_LINEAR)
        
        return rgb_rectified, thermal_rectified
        
    except Exception as e:
        logger.error(f"Error applying calibration: {e}")
        return rgb_image, thermal_image