"""
CalibrationQualityAssessment - Python port of Android calibration quality assessment

Provides automated quality evaluation for calibration images using computer vision algorithms.
Ported from Android CalibrationQualityAssessment.kt with enhanced Python capabilities.

Features:
- Calibration pattern detection (chessboard and circle grid)
- Image sharpness and contrast analysis
- RGB-thermal alignment verification
- Quality scoring and re-capture recommendations

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import math
import time


class PatternType(Enum):
    """Calibration pattern types"""
    CHESSBOARD = "chessboard"
    CIRCLE_GRID = "circle_grid"
    ASYMMETRIC_CIRCLE_GRID = "asymmetric_circle_grid"


@dataclass
class PatternDetectionResult:
    """Pattern detection result for calibration images"""
    pattern_found: bool
    pattern_type: PatternType
    corner_count: int
    pattern_score: float  # 0.0 to 1.0
    geometric_distortion: float
    completeness: float  # Percentage of expected pattern found
    corners: Optional[np.ndarray] = None


@dataclass
class SharpnessMetrics:
    """Image sharpness analysis metrics"""
    laplacian_variance: float
    gradient_magnitude: float
    edge_density: float
    sharpness_score: float  # 0.0 to 1.0


@dataclass
class ContrastMetrics:
    """Image contrast analysis metrics"""
    dynamic_range: int
    histogram_spread: float
    local_contrast: float
    contrast_score: float  # 0.0 to 1.0


@dataclass
class AlignmentMetrics:
    """RGB-thermal alignment analysis metrics"""
    feature_match_count: int
    alignment_error_pixels: float
    transformation_matrix: Optional[np.ndarray]
    alignment_score: float  # 0.0 to 1.0


@dataclass
class CalibrationQualityResult:
    """Complete calibration quality assessment result"""
    overall_quality_score: float  # 0.0 to 1.0
    is_acceptable: bool
    pattern_detection: PatternDetectionResult
    sharpness_metrics: SharpnessMetrics
    contrast_metrics: ContrastMetrics
    alignment_metrics: Optional[AlignmentMetrics] = None
    recommendations: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0


class CalibrationQualityAssessment:
    """
    Advanced calibration quality assessment using computer vision
    
    Provides automated quality evaluation for calibration images with 95% accuracy
    correlation with manual evaluation (target from Android implementation).
    """
    
    # Quality assessment thresholds (from Android implementation)
    MIN_SHARPNESS_SCORE = 0.3
    MIN_CONTRAST_SCORE = 0.4
    MIN_PATTERN_SCORE = 0.6
    MIN_ALIGNMENT_SCORE = 0.5
    
    # Pattern detection parameters
    CHESSBOARD_ROWS = 9
    CHESSBOARD_COLS = 6
    CIRCLE_GRID_ROWS = 4
    CIRCLE_GRID_COLS = 11
    
    # Image analysis parameters
    LAPLACIAN_THRESHOLD = 100.0
    CONTRAST_PERCENTILE = 0.95
    ALIGNMENT_MAX_ERROR = 10.0  # pixels
    
    def __init__(self, logger=None):
        """Initialize calibration quality assessment"""
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize OpenCV components
        self.orb_detector = cv2.ORB_create(nfeatures=1000)
        self.bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        self.logger.info("CalibrationQualityAssessment initialized")

    def assess_calibration_quality(
        self, 
        image: np.ndarray, 
        pattern_type: PatternType = PatternType.CHESSBOARD,
        reference_image: Optional[np.ndarray] = None
    ) -> CalibrationQualityResult:
        """
        Perform comprehensive calibration quality assessment
        
        Args:
            image: Input calibration image (BGR format)
            pattern_type: Type of calibration pattern to detect
            reference_image: Optional reference image for alignment assessment
            
        Returns:
            CalibrationQualityResult: Complete quality assessment
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting calibration quality assessment for {pattern_type.value} pattern")
            
            # Convert to grayscale for analysis
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Perform pattern detection
            pattern_result = self._detect_calibration_pattern(gray_image, pattern_type)
            
            # Analyze image sharpness
            sharpness_metrics = self._analyze_sharpness(gray_image)
            
            # Analyze image contrast
            contrast_metrics = self._analyze_contrast(gray_image)
            
            # Analyze alignment if reference image provided
            alignment_metrics = None
            if reference_image is not None:
                alignment_metrics = self._analyze_alignment(image, reference_image)
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_quality(
                pattern_result, sharpness_metrics, contrast_metrics, alignment_metrics
            )
            
            # Determine if quality is acceptable
            is_acceptable = self._is_quality_acceptable(
                overall_score, pattern_result, sharpness_metrics, contrast_metrics, alignment_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                pattern_result, sharpness_metrics, contrast_metrics, alignment_metrics
            )
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            result = CalibrationQualityResult(
                overall_quality_score=overall_score,
                is_acceptable=is_acceptable,
                pattern_detection=pattern_result,
                sharpness_metrics=sharpness_metrics,
                contrast_metrics=contrast_metrics,
                alignment_metrics=alignment_metrics,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
            self.logger.info(f"Quality assessment completed: score={overall_score:.3f}, "
                           f"acceptable={is_acceptable}, time={processing_time:.1f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during calibration quality assessment: {e}")
            # Return failed result
            return CalibrationQualityResult(
                overall_quality_score=0.0,
                is_acceptable=False,
                pattern_detection=PatternDetectionResult(
                    pattern_found=False,
                    pattern_type=pattern_type,
                    corner_count=0,
                    pattern_score=0.0,
                    geometric_distortion=1.0,
                    completeness=0.0
                ),
                sharpness_metrics=SharpnessMetrics(0.0, 0.0, 0.0, 0.0),
                contrast_metrics=ContrastMetrics(0, 0.0, 0.0, 0.0),
                recommendations=["Error during assessment - please retry"],
                processing_time_ms=(time.time() - start_time) * 1000
            )

    def _detect_calibration_pattern(self, gray_image: np.ndarray, pattern_type: PatternType) -> PatternDetectionResult:
        """Detect calibration pattern in image"""
        try:
            if pattern_type == PatternType.CHESSBOARD:
                return self._detect_chessboard_pattern(gray_image)
            elif pattern_type == PatternType.CIRCLE_GRID:
                return self._detect_circle_grid_pattern(gray_image)
            elif pattern_type == PatternType.ASYMMETRIC_CIRCLE_GRID:
                return self._detect_asymmetric_circle_grid_pattern(gray_image)
            else:
                raise ValueError(f"Unsupported pattern type: {pattern_type}")
                
        except Exception as e:
            self.logger.error(f"Error detecting calibration pattern: {e}")
            return PatternDetectionResult(
                pattern_found=False,
                pattern_type=pattern_type,
                corner_count=0,
                pattern_score=0.0,
                geometric_distortion=1.0,
                completeness=0.0
            )

    def _detect_chessboard_pattern(self, gray_image: np.ndarray) -> PatternDetectionResult:
        """Detect chessboard calibration pattern"""
        pattern_size = (self.CHESSBOARD_COLS, self.CHESSBOARD_ROWS)
        
        # Find chessboard corners
        found, corners = cv2.findChessboardCorners(
            gray_image, 
            pattern_size,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        
        if found and corners is not None:
            # Refine corner positions
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners_refined = cv2.cornerSubPix(gray_image, corners, (11, 11), (-1, -1), criteria)
            
            # Calculate pattern quality metrics
            pattern_score = self._calculate_chessboard_quality(corners_refined, pattern_size)
            geometric_distortion = self._calculate_geometric_distortion(corners_refined, pattern_size)
            completeness = len(corners_refined) / (pattern_size[0] * pattern_size[1])
            
            return PatternDetectionResult(
                pattern_found=True,
                pattern_type=PatternType.CHESSBOARD,
                corner_count=len(corners_refined),
                pattern_score=pattern_score,
                geometric_distortion=geometric_distortion,
                completeness=completeness,
                corners=corners_refined
            )
        else:
            return PatternDetectionResult(
                pattern_found=False,
                pattern_type=PatternType.CHESSBOARD,
                corner_count=0,
                pattern_score=0.0,
                geometric_distortion=1.0,
                completeness=0.0
            )

    def _detect_circle_grid_pattern(self, gray_image: np.ndarray) -> PatternDetectionResult:
        """Detect circle grid calibration pattern"""
        pattern_size = (self.CIRCLE_GRID_COLS, self.CIRCLE_GRID_ROWS)
        
        # Find circle grid
        found, centers = cv2.findCirclesGrid(
            gray_image,
            pattern_size,
            cv2.CALIB_CB_SYMMETRIC_GRID
        )
        
        if found and centers is not None:
            # Calculate pattern quality metrics
            pattern_score = self._calculate_circle_grid_quality(centers, pattern_size)
            geometric_distortion = self._calculate_geometric_distortion(centers, pattern_size)
            completeness = len(centers) / (pattern_size[0] * pattern_size[1])
            
            return PatternDetectionResult(
                pattern_found=True,
                pattern_type=PatternType.CIRCLE_GRID,
                corner_count=len(centers),
                pattern_score=pattern_score,
                geometric_distortion=geometric_distortion,
                completeness=completeness,
                corners=centers
            )
        else:
            return PatternDetectionResult(
                pattern_found=False,
                pattern_type=PatternType.CIRCLE_GRID,
                corner_count=0,
                pattern_score=0.0,
                geometric_distortion=1.0,
                completeness=0.0
            )

    def _detect_asymmetric_circle_grid_pattern(self, gray_image: np.ndarray) -> PatternDetectionResult:
        """Detect asymmetric circle grid calibration pattern"""
        pattern_size = (self.CIRCLE_GRID_COLS, self.CIRCLE_GRID_ROWS)
        
        # Find asymmetric circle grid
        found, centers = cv2.findCirclesGrid(
            gray_image,
            pattern_size,
            cv2.CALIB_CB_ASYMMETRIC_GRID
        )
        
        if found and centers is not None:
            pattern_score = self._calculate_circle_grid_quality(centers, pattern_size)
            geometric_distortion = self._calculate_geometric_distortion(centers, pattern_size)
            completeness = len(centers) / (pattern_size[0] * pattern_size[1])
            
            return PatternDetectionResult(
                pattern_found=True,
                pattern_type=PatternType.ASYMMETRIC_CIRCLE_GRID,
                corner_count=len(centers),
                pattern_score=pattern_score,
                geometric_distortion=geometric_distortion,
                completeness=completeness,
                corners=centers
            )
        else:
            return PatternDetectionResult(
                pattern_found=False,
                pattern_type=PatternType.ASYMMETRIC_CIRCLE_GRID,
                corner_count=0,
                pattern_score=0.0,
                geometric_distortion=1.0,
                completeness=0.0
            )

    def _analyze_sharpness(self, gray_image: np.ndarray) -> SharpnessMetrics:
        """Analyze image sharpness using multiple metrics"""
        try:
            # Laplacian variance (primary sharpness metric)
            laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
            laplacian_variance = laplacian.var()
            
            # Gradient magnitude
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.mean(np.sqrt(grad_x**2 + grad_y**2))
            
            # Edge density
            edges = cv2.Canny(gray_image, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Calculate normalized sharpness score
            sharpness_score = min(1.0, laplacian_variance / self.LAPLACIAN_THRESHOLD)
            
            return SharpnessMetrics(
                laplacian_variance=laplacian_variance,
                gradient_magnitude=gradient_magnitude,
                edge_density=edge_density,
                sharpness_score=sharpness_score
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing sharpness: {e}")
            return SharpnessMetrics(0.0, 0.0, 0.0, 0.0)

    def _analyze_contrast(self, gray_image: np.ndarray) -> ContrastMetrics:
        """Analyze image contrast using multiple metrics"""
        try:
            # Dynamic range
            dynamic_range = int(gray_image.max()) - int(gray_image.min())
            
            # Histogram spread
            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
            hist_spread = np.std(hist)
            
            # Local contrast (using standard deviation)
            local_contrast = np.std(gray_image.astype(np.float32))
            
            # Calculate normalized contrast score
            contrast_score = min(1.0, dynamic_range / 255.0)
            
            return ContrastMetrics(
                dynamic_range=dynamic_range,
                histogram_spread=hist_spread,
                local_contrast=local_contrast,
                contrast_score=contrast_score
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing contrast: {e}")
            return ContrastMetrics(0, 0.0, 0.0, 0.0)

    def _analyze_alignment(self, image1: np.ndarray, image2: np.ndarray) -> AlignmentMetrics:
        """Analyze alignment between two images (e.g., RGB and thermal)"""
        try:
            # Convert to grayscale if needed
            gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY) if len(image1.shape) == 3 else image1
            gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY) if len(image2.shape) == 3 else image2
            
            # Detect features
            kp1, des1 = self.orb_detector.detectAndCompute(gray1, None)
            kp2, des2 = self.orb_detector.detectAndCompute(gray2, None)
            
            if des1 is not None and des2 is not None:
                # Match features
                matches = self.bf_matcher.match(des1, des2)
                matches = sorted(matches, key=lambda x: x.distance)
                
                if len(matches) >= 4:
                    # Extract matched points
                    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                    
                    # Find homography
                    transformation_matrix, mask = cv2.findHomography(
                        src_pts, dst_pts, cv2.RANSAC, 5.0
                    )
                    
                    # Calculate alignment error
                    if transformation_matrix is not None:
                        # Transform points and calculate error
                        transformed_pts = cv2.perspectiveTransform(src_pts, transformation_matrix)
                        alignment_error = np.mean(np.linalg.norm(transformed_pts - dst_pts, axis=2))
                        
                        # Calculate alignment score
                        alignment_score = max(0.0, 1.0 - (alignment_error / self.ALIGNMENT_MAX_ERROR))
                        
                        return AlignmentMetrics(
                            feature_match_count=len(matches),
                            alignment_error_pixels=alignment_error,
                            transformation_matrix=transformation_matrix,
                            alignment_score=alignment_score
                        )
            
            # Failed alignment
            return AlignmentMetrics(
                feature_match_count=0,
                alignment_error_pixels=float('inf'),
                transformation_matrix=None,
                alignment_score=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing alignment: {e}")
            return AlignmentMetrics(0, float('inf'), None, 0.0)

    def _calculate_chessboard_quality(self, corners: np.ndarray, pattern_size: Tuple[int, int]) -> float:
        """Calculate quality score for chessboard pattern"""
        try:
            if len(corners) != pattern_size[0] * pattern_size[1]:
                return 0.0
            
            # Reshape corners to grid
            corners_grid = corners.reshape(pattern_size[1], pattern_size[0], 2)
            
            # Calculate regularity of spacing
            spacing_errors = []
            for i in range(pattern_size[1] - 1):
                for j in range(pattern_size[0] - 1):
                    # Calculate expected vs actual spacing
                    horizontal_spacing = np.linalg.norm(corners_grid[i, j+1] - corners_grid[i, j])
                    vertical_spacing = np.linalg.norm(corners_grid[i+1, j] - corners_grid[i, j])
                    
                    # Add to error if spacing is inconsistent
                    if horizontal_spacing > 0 and vertical_spacing > 0:
                        spacing_ratio = horizontal_spacing / vertical_spacing
                        spacing_errors.append(abs(spacing_ratio - 1.0))
            
            if spacing_errors:
                avg_spacing_error = np.mean(spacing_errors)
                quality_score = max(0.0, 1.0 - avg_spacing_error)
            else:
                quality_score = 0.0
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Error calculating chessboard quality: {e}")
            return 0.0

    def _calculate_circle_grid_quality(self, centers: np.ndarray, pattern_size: Tuple[int, int]) -> float:
        """Calculate quality score for circle grid pattern"""
        try:
            if len(centers) != pattern_size[0] * pattern_size[1]:
                return 0.0
            
            # Calculate regularity of circle positions
            centers_flat = centers.reshape(-1, 2)
            
            # Calculate average distance between adjacent circles
            distances = []
            for i in range(len(centers_flat)):
                for j in range(i + 1, len(centers_flat)):
                    dist = np.linalg.norm(centers_flat[i] - centers_flat[j])
                    distances.append(dist)
            
            if distances:
                # Quality based on consistency of distances
                distance_std = np.std(distances)
                distance_mean = np.mean(distances)
                if distance_mean > 0:
                    quality_score = max(0.0, 1.0 - (distance_std / distance_mean))
                else:
                    quality_score = 0.0
            else:
                quality_score = 0.0
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Error calculating circle grid quality: {e}")
            return 0.0

    def _calculate_geometric_distortion(self, points: np.ndarray, pattern_size: Tuple[int, int]) -> float:
        """Calculate geometric distortion of detected pattern"""
        try:
            if len(points) < 4:
                return 1.0
            
            # For simplicity, calculate distortion as deviation from expected grid regularity
            points_flat = points.reshape(-1, 2)
            
            # Calculate bounding box
            min_x, min_y = np.min(points_flat, axis=0)
            max_x, max_y = np.max(points_flat, axis=0)
            
            # Expected aspect ratio
            expected_ratio = pattern_size[0] / pattern_size[1]
            actual_ratio = (max_x - min_x) / (max_y - min_y) if (max_y - min_y) > 0 else 1.0
            
            # Distortion as deviation from expected ratio
            distortion = abs(actual_ratio - expected_ratio) / expected_ratio
            
            return min(1.0, distortion)
            
        except Exception as e:
            self.logger.error(f"Error calculating geometric distortion: {e}")
            return 1.0

    def _calculate_overall_quality(
        self,
        pattern_result: PatternDetectionResult,
        sharpness_metrics: SharpnessMetrics,
        contrast_metrics: ContrastMetrics,
        alignment_metrics: Optional[AlignmentMetrics]
    ) -> float:
        """Calculate overall quality score"""
        try:
            # Weighted combination of quality metrics
            weights = {
                'pattern': 0.4,
                'sharpness': 0.3,
                'contrast': 0.2,
                'alignment': 0.1
            }
            
            overall_score = (
                weights['pattern'] * pattern_result.pattern_score +
                weights['sharpness'] * sharpness_metrics.sharpness_score +
                weights['contrast'] * contrast_metrics.contrast_score
            )
            
            if alignment_metrics is not None:
                overall_score += weights['alignment'] * alignment_metrics.alignment_score
            else:
                # Redistribute alignment weight to other metrics
                overall_score = overall_score / (1.0 - weights['alignment'])
            
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating overall quality: {e}")
            return 0.0

    def _is_quality_acceptable(
        self,
        overall_score: float,
        pattern_result: PatternDetectionResult,
        sharpness_metrics: SharpnessMetrics,
        contrast_metrics: ContrastMetrics,
        alignment_metrics: Optional[AlignmentMetrics]
    ) -> bool:
        """Determine if calibration quality is acceptable"""
        try:
            # Check individual thresholds
            if not pattern_result.pattern_found:
                return False
            
            if pattern_result.pattern_score < self.MIN_PATTERN_SCORE:
                return False
            
            if sharpness_metrics.sharpness_score < self.MIN_SHARPNESS_SCORE:
                return False
            
            if contrast_metrics.contrast_score < self.MIN_CONTRAST_SCORE:
                return False
            
            if alignment_metrics is not None and alignment_metrics.alignment_score < self.MIN_ALIGNMENT_SCORE:
                return False
            
            # Overall score threshold
            return overall_score >= 0.7
            
        except Exception as e:
            self.logger.error(f"Error determining quality acceptability: {e}")
            return False

    def _generate_recommendations(
        self,
        pattern_result: PatternDetectionResult,
        sharpness_metrics: SharpnessMetrics,
        contrast_metrics: ContrastMetrics,
        alignment_metrics: Optional[AlignmentMetrics]
    ) -> List[str]:
        """Generate recommendations for improving calibration quality"""
        recommendations = []
        
        try:
            if not pattern_result.pattern_found:
                recommendations.append("Calibration pattern not detected - ensure pattern is visible and well-lit")
            elif pattern_result.pattern_score < self.MIN_PATTERN_SCORE:
                recommendations.append("Pattern quality is low - check for occlusions or distortions")
            
            if sharpness_metrics.sharpness_score < self.MIN_SHARPNESS_SCORE:
                recommendations.append("Image is blurry - ensure camera is in focus and stable")
            
            if contrast_metrics.contrast_score < self.MIN_CONTRAST_SCORE:
                recommendations.append("Image contrast is low - improve lighting conditions")
            
            if alignment_metrics is not None and alignment_metrics.alignment_score < self.MIN_ALIGNMENT_SCORE:
                recommendations.append("Poor alignment between images - check camera positioning")
            
            if pattern_result.completeness < 0.9:
                recommendations.append("Pattern is partially occluded - ensure full pattern visibility")
            
            if pattern_result.geometric_distortion > 0.3:
                recommendations.append("Significant geometric distortion detected - check camera angle")
            
            if not recommendations:
                recommendations.append("Calibration quality is acceptable")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Error generating recommendations")
        
        return recommendations


if __name__ == "__main__":
    # Test calibration quality assessment
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create assessment instance
    assessment = CalibrationQualityAssessment()
    
    # Create test image (synthetic chessboard)
    test_image = np.zeros((480, 640), dtype=np.uint8)
    
    # Simple test pattern
    for i in range(0, 480, 60):
        for j in range(0, 640, 80):
            if ((i // 60) + (j // 80)) % 2 == 0:
                test_image[i:i+60, j:j+80] = 255
    
    # Assess quality
    result = assessment.assess_calibration_quality(test_image, PatternType.CHESSBOARD)
    
    print(f"Overall Quality Score: {result.overall_quality_score:.3f}")
    print(f"Is Acceptable: {result.is_acceptable}")
    print(f"Pattern Found: {result.pattern_detection.pattern_found}")
    print(f"Sharpness Score: {result.sharpness_metrics.sharpness_score:.3f}")
    print(f"Contrast Score: {result.contrast_metrics.contrast_score:.3f}")
    print(f"Processing Time: {result.processing_time_ms:.1f}ms")
    print("Recommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")
