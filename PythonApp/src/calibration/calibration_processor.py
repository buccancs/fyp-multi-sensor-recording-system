"""
Calibration Processor for Multi-Sensor Recording System Controller

This module implements the CalibrationProcessor class for Milestone 3.4: Calibration Engine (OpenCV).
It contains OpenCV-specific functions for pattern detection, camera calibration computations,
and homography calculation for thermal-RGB alignment.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.4 - Calibration Engine (OpenCV)
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Any


class CalibrationProcessor:
    """
    OpenCV-based calibration processor for pattern detection and calibration computations.
    
    This class provides:
    - Calibration pattern detection (chessboard, circles, ArUco)
    - Camera intrinsic parameter calculation
    - Stereo calibration between RGB and thermal cameras
    - Homography computation for image overlay
    - Sub-pixel corner refinement
    """
    
    def __init__(self):
        """Initialize calibration processor with default settings."""
        # Corner refinement criteria
        self.corner_criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 
            30, 0.001
        )
        
        # Calibration flags
        self.calibration_flags = (
            cv2.CALIB_RATIONAL_MODEL | 
            cv2.CALIB_THIN_PRISM_MODEL | 
            cv2.CALIB_TILTED_MODEL
        )
        
        print("[DEBUG_LOG] CalibrationProcessor initialized")
    
    def detect_chessboard_corners(self, image: np.ndarray, 
                                pattern_size: Tuple[int, int]) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detect chessboard corners in an image.
        
        Args:
            image (np.ndarray): Input image (color or grayscale)
            pattern_size (Tuple[int, int]): Pattern size (width, height) in internal corners
            
        Returns:
            Tuple[bool, Optional[np.ndarray]]: Success flag and corner points
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners(
            gray, pattern_size, 
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        
        if ret:
            # Refine corner positions to sub-pixel accuracy
            corners = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), self.corner_criteria
            )
            return True, corners
        else:
            return False, None
    
    def detect_circles_grid(self, image: np.ndarray, 
                          pattern_size: Tuple[int, int]) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detect circles grid pattern in an image.
        
        Args:
            image (np.ndarray): Input image
            pattern_size (Tuple[int, int]): Pattern size (width, height)
            
        Returns:
            Tuple[bool, Optional[np.ndarray]]: Success flag and center points
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Find circles grid
        ret, centers = cv2.findCirclesGrid(
            gray, pattern_size, 
            cv2.CALIB_CB_SYMMETRIC_GRID
        )
        
        return ret, centers if ret else None
    
    def detect_aruco_markers(self, image: np.ndarray, 
                           dictionary_id: int = cv2.aruco.DICT_6X6_250) -> Tuple[bool, List[np.ndarray]]:
        """
        Detect ArUco markers in an image.
        
        Args:
            image (np.ndarray): Input image
            dictionary_id (int): ArUco dictionary ID
            
        Returns:
            Tuple[bool, List[np.ndarray]]: Success flag and marker corners
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Create ArUco dictionary and detector parameters
        aruco_dict = cv2.aruco.Dictionary_get(dictionary_id)
        parameters = cv2.aruco.DetectorParameters_create()
        
        # Detect markers
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters
        )
        
        if ids is not None and len(corners) > 0:
            return True, corners
        else:
            return False, []
    
    def create_object_points(self, pattern_size: Tuple[int, int], 
                           square_size: float) -> np.ndarray:
        """
        Create 3D object points for calibration pattern.
        
        Args:
            pattern_size (Tuple[int, int]): Pattern size (width, height)
            square_size (float): Size of each square in mm
            
        Returns:
            np.ndarray: 3D object points
        """
        # Create object points (assuming pattern lies on z=0 plane)
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
        objp *= square_size
        
        return objp
    
    def calibrate_camera_intrinsics(self, object_points: List[np.ndarray], 
                                  image_points: List[np.ndarray], 
                                  image_size: Tuple[int, int]) -> Tuple[float, np.ndarray, np.ndarray, List[np.ndarray], List[np.ndarray]]:
        """
        Calibrate camera intrinsic parameters.
        
        Args:
            object_points (List[np.ndarray]): 3D object points for each image
            image_points (List[np.ndarray]): 2D image points for each image
            image_size (Tuple[int, int]): Image size (width, height)
            
        Returns:
            Tuple: RMS error, camera matrix, distortion coefficients, rotation vectors, translation vectors
        """
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, image_size, None, None, 
            flags=self.calibration_flags
        )
        
        return ret, camera_matrix, dist_coeffs, rvecs, tvecs
    
    def calibrate_stereo_cameras(self, object_points: List[np.ndarray],
                               image_points1: List[np.ndarray], 
                               image_points2: List[np.ndarray],
                               camera_matrix1: np.ndarray, dist_coeffs1: np.ndarray,
                               camera_matrix2: np.ndarray, dist_coeffs2: np.ndarray,
                               image_size: Tuple[int, int]) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform stereo calibration between two cameras.
        
        Args:
            object_points (List[np.ndarray]): 3D object points
            image_points1 (List[np.ndarray]): Image points from camera 1
            image_points2 (List[np.ndarray]): Image points from camera 2
            camera_matrix1 (np.ndarray): Camera matrix for camera 1
            dist_coeffs1 (np.ndarray): Distortion coefficients for camera 1
            camera_matrix2 (np.ndarray): Camera matrix for camera 2
            dist_coeffs2 (np.ndarray): Distortion coefficients for camera 2
            image_size (Tuple[int, int]): Image size
            
        Returns:
            Tuple: RMS error, rotation matrix, translation vector, essential matrix, fundamental matrix
        """
        # Stereo calibration with fixed intrinsics
        ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
            object_points, image_points1, image_points2,
            camera_matrix1, dist_coeffs1,
            camera_matrix2, dist_coeffs2,
            image_size, 
            flags=cv2.CALIB_FIX_INTRINSIC
        )
        
        return ret, R, T, E, F
    
    def compute_homography(self, points1: np.ndarray, 
                         points2: np.ndarray) -> Optional[np.ndarray]:
        """
        Compute homography matrix between two sets of points.
        
        Args:
            points1 (np.ndarray): Points from first image
            points2 (np.ndarray): Corresponding points from second image
            
        Returns:
            np.ndarray: Homography matrix or None if computation fails
        """
        if len(points1) < 4 or len(points2) < 4:
            print("[DEBUG_LOG] Insufficient points for homography computation")
            return None
        
        try:
            # Reshape points if needed
            if points1.shape[1] == 1:
                points1 = points1.reshape(-1, 2)
            if points2.shape[1] == 1:
                points2 = points2.reshape(-1, 2)
            
            # Compute homography using RANSAC
            H, mask = cv2.findHomography(
                points1, points2, 
                cv2.RANSAC, 5.0
            )
            
            if H is not None:
                print(f"[DEBUG_LOG] Homography computed with {np.sum(mask)} inliers")
                return H
            else:
                print("[DEBUG_LOG] Homography computation failed")
                return None
                
        except Exception as e:
            print(f"[DEBUG_LOG] Homography computation error: {e}")
            return None
    
    def compute_reprojection_error(self, object_points: List[np.ndarray],
                                 image_points: List[np.ndarray],
                                 camera_matrix: np.ndarray, 
                                 dist_coeffs: np.ndarray,
                                 rvecs: List[np.ndarray], 
                                 tvecs: List[np.ndarray]) -> Tuple[float, List[float]]:
        """
        Compute reprojection error for calibration validation.
        
        Args:
            object_points (List[np.ndarray]): 3D object points
            image_points (List[np.ndarray]): 2D image points
            camera_matrix (np.ndarray): Camera matrix
            dist_coeffs (np.ndarray): Distortion coefficients
            rvecs (List[np.ndarray]): Rotation vectors
            tvecs (List[np.ndarray]): Translation vectors
            
        Returns:
            Tuple[float, List[float]]: Mean error and per-image errors
        """
        total_error = 0
        per_image_errors = []
        
        for i in range(len(object_points)):
            # Project 3D points to image plane
            projected_points, _ = cv2.projectPoints(
                object_points[i], rvecs[i], tvecs[i], 
                camera_matrix, dist_coeffs
            )
            
            # Calculate error
            error = cv2.norm(image_points[i], projected_points, cv2.NORM_L2) / len(projected_points)
            per_image_errors.append(error)
            total_error += error
        
        mean_error = total_error / len(object_points)
        return mean_error, per_image_errors
    
    def undistort_image(self, image: np.ndarray, 
                       camera_matrix: np.ndarray, 
                       dist_coeffs: np.ndarray) -> np.ndarray:
        """
        Undistort an image using camera calibration parameters.
        
        Args:
            image (np.ndarray): Input distorted image
            camera_matrix (np.ndarray): Camera matrix
            dist_coeffs (np.ndarray): Distortion coefficients
            
        Returns:
            np.ndarray: Undistorted image
        """
        h, w = image.shape[:2]
        
        # Get optimal new camera matrix
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coeffs, (w, h), 1, (w, h)
        )
        
        # Undistort image
        undistorted = cv2.undistort(
            image, camera_matrix, dist_coeffs, None, new_camera_matrix
        )
        
        # Crop the image based on ROI
        x, y, w, h = roi
        if w > 0 and h > 0:
            undistorted = undistorted[y:y+h, x:x+w]
        
        return undistorted
    
    def create_rectification_maps(self, camera_matrix1: np.ndarray, dist_coeffs1: np.ndarray,
                                camera_matrix2: np.ndarray, dist_coeffs2: np.ndarray,
                                image_size: Tuple[int, int], R: np.ndarray, T: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Create rectification maps for stereo image pair.
        
        Args:
            camera_matrix1 (np.ndarray): Camera matrix for camera 1
            dist_coeffs1 (np.ndarray): Distortion coefficients for camera 1
            camera_matrix2 (np.ndarray): Camera matrix for camera 2
            dist_coeffs2 (np.ndarray): Distortion coefficients for camera 2
            image_size (Tuple[int, int]): Image size
            R (np.ndarray): Rotation matrix between cameras
            T (np.ndarray): Translation vector between cameras
            
        Returns:
            Tuple: Rectification maps for both cameras (map1x, map1y, map2x, map2y)
        """
        # Compute rectification transforms
        R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
            camera_matrix1, dist_coeffs1,
            camera_matrix2, dist_coeffs2,
            image_size, R, T
        )
        
        # Compute rectification maps
        map1x, map1y = cv2.initUndistortRectifyMap(
            camera_matrix1, dist_coeffs1, R1, P1, image_size, cv2.CV_16SC2
        )
        map2x, map2y = cv2.initUndistortRectifyMap(
            camera_matrix2, dist_coeffs2, R2, P2, image_size, cv2.CV_16SC2
        )
        
        return map1x, map1y, map2x, map2y
    
    def apply_rectification(self, image1: np.ndarray, image2: np.ndarray,
                          map1x: np.ndarray, map1y: np.ndarray,
                          map2x: np.ndarray, map2y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply rectification to stereo image pair.
        
        Args:
            image1 (np.ndarray): First image
            image2 (np.ndarray): Second image
            map1x, map1y (np.ndarray): Rectification maps for first image
            map2x, map2y (np.ndarray): Rectification maps for second image
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Rectified images
        """
        rectified1 = cv2.remap(image1, map1x, map1y, cv2.INTER_LINEAR)
        rectified2 = cv2.remap(image2, map2x, map2y, cv2.INTER_LINEAR)
        
        return rectified1, rectified2
    
    def validate_calibration_quality(self, reprojection_error: float, 
                                   num_images: int, 
                                   pattern_coverage: float = None) -> dict:
        """
        Validate calibration quality based on various metrics.
        
        Args:
            reprojection_error (float): Mean reprojection error
            num_images (int): Number of calibration images used
            pattern_coverage (float, optional): Pattern coverage score
            
        Returns:
            dict: Quality assessment results
        """
        quality = {
            'reprojection_error': reprojection_error,
            'num_images': num_images,
            'quality_score': 'UNKNOWN',
            'recommendations': []
        }
        
        # Assess reprojection error
        if reprojection_error < 0.3:
            error_quality = 'EXCELLENT'
        elif reprojection_error < 0.5:
            error_quality = 'VERY_GOOD'
        elif reprojection_error < 1.0:
            error_quality = 'GOOD'
        elif reprojection_error < 2.0:
            error_quality = 'ACCEPTABLE'
        else:
            error_quality = 'POOR'
        
        # Assess number of images
        if num_images < 10:
            quality['recommendations'].append('Use more calibration images (recommended: 15-20)')
        elif num_images < 15:
            quality['recommendations'].append('Consider using more images for better accuracy')
        
        # Overall quality assessment
        if error_quality in ['EXCELLENT', 'VERY_GOOD'] and num_images >= 10:
            quality['quality_score'] = 'EXCELLENT'
        elif error_quality in ['GOOD'] and num_images >= 10:
            quality['quality_score'] = 'GOOD'
        elif error_quality in ['ACCEPTABLE'] and num_images >= 8:
            quality['quality_score'] = 'ACCEPTABLE'
        else:
            quality['quality_score'] = 'POOR'
            quality['recommendations'].extend([
                'Recapture calibration images',
                'Ensure good lighting conditions',
                'Use a high-contrast calibration pattern',
                'Vary pattern positions and orientations'
            ])
        
        return quality
    
    def draw_chessboard_corners(self, image: np.ndarray, 
                              pattern_size: Tuple[int, int], 
                              corners: np.ndarray, 
                              pattern_found: bool) -> np.ndarray:
        """
        Draw detected chessboard corners on image for visualization.
        
        Args:
            image (np.ndarray): Input image
            pattern_size (Tuple[int, int]): Pattern size
            corners (np.ndarray): Detected corners
            pattern_found (bool): Whether pattern was found
            
        Returns:
            np.ndarray: Image with drawn corners
        """
        result_image = image.copy()
        cv2.drawChessboardCorners(result_image, pattern_size, corners, pattern_found)
        return result_image


if __name__ == "__main__":
    # Test calibration processor
    print("[DEBUG_LOG] Testing CalibrationProcessor...")
    
    processor = CalibrationProcessor()
    
    # Test object points creation
    pattern_size = (9, 6)
    square_size = 25.0
    objp = processor.create_object_points(pattern_size, square_size)
    print(f"Created object points: {objp.shape}")
    
    # Test with synthetic chessboard image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    success, corners = processor.detect_chessboard_corners(test_image, pattern_size)
    print(f"Chessboard detection: {success}")
    
    print("[DEBUG_LOG] CalibrationProcessor test completed")
