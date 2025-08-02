"""
Calibration Test Suite for Integration Testing.

This module provides tests to verify the calibration logic without needing
manual intervention. It uses known input data to run the calibration routine
and validates the results against expected thresholds.
"""

import cv2
import json
import logging
import numpy as np
import os
import pytest
import sys
from typing import List, Tuple

# Import protocol utilities
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from protocol import get_calibration_config, get_calibration_error_threshold

logger = logging.getLogger(__name__)


class CalibrationTestData:
    """Manages test data for calibration tests."""

    def __init__(self):
        self.config = get_calibration_config()
        self.pattern_size = (
            self.config.get("pattern_rows", 7),
            self.config.get("pattern_cols", 6),
        )
        self.square_size = self.config.get("square_size_m", 0.0245)
        self.error_threshold = get_calibration_error_threshold()

    def generate_object_points(self) -> np.ndarray:
        """
        Generate object points for calibration pattern.

        Returns:
            Array of 3D object points in real-world coordinates
        """
        # Create object points for chessboard pattern
        objp = np.zeros((self.pattern_size[0] * self.pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[
            0 : self.pattern_size[0], 0 : self.pattern_size[1]
        ].T.reshape(-1, 2)
        objp *= self.square_size  # Scale by square size in meters

        return objp

    def generate_synthetic_image_points(self, num_images: int = 15) -> List[np.ndarray]:
        """
        Generate synthetic image points for testing.

        Args:
            num_images: Number of calibration images to simulate

        Returns:
            List of image point arrays
        """
        # Synthetic camera parameters for generating test data
        camera_matrix = np.array(
            [[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32
        )

        dist_coeffs = np.array([0.1, -0.2, 0.0, 0.0, 0.0], dtype=np.float32)

        # Generate object points
        objp = self.generate_object_points()

        image_points = []

        for i in range(num_images):
            # Create different poses for each image
            rvec = np.array([0.1 * i, 0.05 * i, 0.02 * i], dtype=np.float32)
            tvec = np.array([0.1, 0.1, 0.5 + 0.1 * i], dtype=np.float32)

            # Project 3D points to 2D image points
            imgpts, _ = cv2.projectPoints(objp, rvec, tvec, camera_matrix, dist_coeffs)
            imgpts = imgpts.reshape(-1, 2)

            # Add small amount of noise to make it realistic
            noise = np.random.normal(0, 0.5, imgpts.shape)
            imgpts += noise

            image_points.append(imgpts.astype(np.float32))

        return image_points

    def load_real_calibration_data(
        self, data_dir: str
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Load real calibration data from files if available.

        Args:
            data_dir: Directory containing calibration data files

        Returns:
            Tuple of (object_points_list, image_points_list)
        """
        object_points = []
        image_points = []

        if not os.path.exists(data_dir):
            logger.warning(f"Calibration data directory not found: {data_dir}")
            return object_points, image_points

        # Look for calibration data files
        for filename in os.listdir(data_dir):
            if filename.endswith("_corners.json"):
                try:
                    with open(os.path.join(data_dir, filename), "r") as f:
                        corners_data = json.load(f)

                    if "corners" in corners_data:
                        imgpts = np.array(corners_data["corners"], dtype=np.float32)
                        image_points.append(imgpts)
                        object_points.append(self.generate_object_points())

                except Exception as e:
                    logger.warning(
                        f"Failed to load calibration data from {filename}: {e}"
                    )

        logger.info(f"Loaded {len(image_points)} calibration images from {data_dir}")
        return object_points, image_points


class CalibrationTester:
    """Performs calibration tests and validation."""

    def __init__(self):
        self.test_data = CalibrationTestData()
        self.image_size = (640, 480)  # Default test image size

    def run_calibration(
        self, object_points: List[np.ndarray], image_points: List[np.ndarray]
    ) -> Tuple[float, np.ndarray, np.ndarray]:
        """
        Run camera calibration with given points.

        Args:
            object_points: List of 3D object point arrays
            image_points: List of 2D image point arrays

        Returns:
            Tuple of (rms_error, camera_matrix, distortion_coefficients)
        """
        if len(object_points) != len(image_points):
            raise ValueError("Number of object and image point sets must match")

        if len(object_points) < 3:
            raise ValueError("Need at least 3 calibration images")

        # Run OpenCV calibration
        flags = cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_ZERO_TANGENT_DIST

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, self.image_size, None, None, flags=flags
        )

        return ret, camera_matrix, dist_coeffs

    def validate_calibration_result(
        self, rms_error: float, camera_matrix: np.ndarray, dist_coeffs: np.ndarray
    ) -> bool:
        """
        Validate calibration results against expected criteria.

        Args:
            rms_error: RMS reprojection error
            camera_matrix: Camera intrinsic matrix
            dist_coeffs: Distortion coefficients

        Returns:
            True if calibration meets quality criteria
        """
        # Check RMS error threshold
        if rms_error > self.test_data.error_threshold:
            logger.error(
                f"RMS error {rms_error:.3f} exceeds threshold {self.test_data.error_threshold}"
            )
            return False

        # Validate camera matrix structure
        if camera_matrix.shape != (3, 3):
            logger.error(f"Invalid camera matrix shape: {camera_matrix.shape}")
            return False

        # Check focal lengths are reasonable (not too small or too large)
        fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
        if fx < 100 or fx > 2000 or fy < 100 or fy > 2000:
            logger.error(f"Unreasonable focal lengths: fx={fx:.1f}, fy={fy:.1f}")
            return False

        # Check principal point is roughly in image center
        cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]
        img_w, img_h = self.image_size
        if abs(cx - img_w / 2) > img_w / 4 or abs(cy - img_h / 2) > img_h / 4:
            logger.warning(f"Principal point far from center: ({cx:.1f}, {cy:.1f})")

        # Check distortion coefficients are reasonable
        if len(dist_coeffs) >= 2:
            k1, k2 = dist_coeffs[0], dist_coeffs[1]
            if abs(k1) > 1.0 or abs(k2) > 1.0:
                logger.warning(
                    f"Large distortion coefficients: k1={k1:.3f}, k2={k2:.3f}"
                )

        logger.info(f"Calibration validation passed: RMS={rms_error:.3f}")
        return True


# Test functions for pytest
@pytest.fixture
def calibration_tester():
    """Fixture providing a CalibrationTester instance."""
    return CalibrationTester()


@pytest.fixture
def synthetic_calibration_data():
    """Fixture providing synthetic calibration data."""
    test_data = CalibrationTestData()
    object_points = [test_data.generate_object_points() for _ in range(15)]
    image_points = test_data.generate_synthetic_image_points(15)
    return object_points, image_points


@pytest.mark.integration
def test_calibration_with_synthetic_data(
    calibration_tester, synthetic_calibration_data
):
    """Test calibration with synthetic data."""
    object_points, image_points = synthetic_calibration_data

    # Run calibration
    rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
        object_points, image_points
    )

    # Validate results
    assert calibration_tester.validate_calibration_result(
        rms_error, camera_matrix, dist_coeffs
    )

    # Check specific values
    assert rms_error < calibration_tester.test_data.error_threshold
    assert camera_matrix.shape == (3, 3)
    assert len(dist_coeffs) >= 4


@pytest.mark.integration
def test_calibration_insufficient_images(calibration_tester):
    """Test calibration with insufficient number of images."""
    test_data = CalibrationTestData()

    # Only 2 images (insufficient)
    object_points = [test_data.generate_object_points() for _ in range(2)]
    image_points = test_data.generate_synthetic_image_points(2)

    # Should raise ValueError
    with pytest.raises(ValueError, match="Need at least 3 calibration images"):
        calibration_tester.run_calibration(object_points, image_points)


@pytest.mark.integration
def test_calibration_mismatched_points(calibration_tester):
    """Test calibration with mismatched object and image points."""
    test_data = CalibrationTestData()

    object_points = [test_data.generate_object_points() for _ in range(5)]
    image_points = test_data.generate_synthetic_image_points(3)  # Different count

    # Should raise ValueError
    with pytest.raises(
        ValueError, match="Number of object and image point sets must match"
    ):
        calibration_tester.run_calibration(object_points, image_points)


@pytest.mark.integration
def test_calibration_with_noise(calibration_tester):
    """Test calibration robustness with noisy data."""
    test_data = CalibrationTestData()

    # Generate data with more noise
    object_points = [test_data.generate_object_points() for _ in range(20)]
    image_points = []

    # Add significant noise to test robustness
    for i in range(20):
        imgpts = test_data.generate_synthetic_image_points(1)[0]
        noise = np.random.normal(0, 2.0, imgpts.shape)  # Higher noise
        imgpts += noise
        image_points.append(imgpts)

    # Run calibration
    rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
        object_points, image_points
    )

    # With higher noise, error might be higher but should still be reasonable
    assert rms_error < 5.0  # More lenient threshold for noisy data
    assert camera_matrix.shape == (3, 3)


@pytest.mark.integration
def test_calibration_config_loading():
    """Test that calibration configuration is loaded correctly."""
    config = get_calibration_config()

    # Check required configuration keys
    assert "pattern_rows" in config
    assert "pattern_cols" in config
    assert "square_size_m" in config
    assert "error_threshold" in config

    # Check reasonable values
    assert config["pattern_rows"] > 0
    assert config["pattern_cols"] > 0
    assert config["square_size_m"] > 0
    assert config["error_threshold"] > 0


@pytest.mark.integration
def test_calibration_pattern_generation():
    """Test object point generation for calibration pattern."""
    test_data = CalibrationTestData()
    objp = test_data.generate_object_points()

    # Check shape
    expected_points = test_data.pattern_size[0] * test_data.pattern_size[1]
    assert objp.shape == (expected_points, 3)

    # Check that Z coordinates are zero (planar pattern)
    assert np.allclose(objp[:, 2], 0)

    # Check scaling by square size
    max_x = objp[:, 0].max()
    max_y = objp[:, 1].max()
    expected_max_x = (test_data.pattern_size[0] - 1) * test_data.square_size
    expected_max_y = (test_data.pattern_size[1] - 1) * test_data.square_size

    assert abs(max_x - expected_max_x) < 1e-6
    assert abs(max_y - expected_max_y) < 1e-6


@pytest.mark.integration
def test_calibration_with_real_data():
    """Test calibration with real data if available."""
    test_data = CalibrationTestData()
    data_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "test_data", "calibration"
    )

    object_points, image_points = test_data.load_real_calibration_data(data_dir)

    if len(object_points) >= 3:  # Only run if I have real data
        calibration_tester = CalibrationTester()

        rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
            object_points, image_points
        )

        # Real data should meet quality criteria
        assert calibration_tester.validate_calibration_result(
            rms_error, camera_matrix, dist_coeffs
        )
    else:
        pytest.skip("No real calibration data available")


def test_calibration_error_threshold_config():
    """Test that error threshold is properly configured."""
    threshold = get_calibration_error_threshold()

    # Should be a reasonable value (typically 0.5 to 2.0 pixels)
    assert 0.1 <= threshold <= 10.0
    assert isinstance(threshold, (int, float))


# Performance test
@pytest.mark.integration
@pytest.mark.slow
def test_calibration_performance():
    """Test calibration performance with larger dataset."""
    test_data = CalibrationTestData()
    calibration_tester = CalibrationTester()

    # Generate larger dataset
    num_images = 50
    object_points = [test_data.generate_object_points() for _ in range(num_images)]
    image_points = test_data.generate_synthetic_image_points(num_images)

    import time

    start_time = time.time()

    rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
        object_points, image_points
    )

    end_time = time.time()
    calibration_time = end_time - start_time

    # Calibration should complete in reasonable time (< 5 seconds for 50 images)
    assert calibration_time < 5.0

    # Results should still be good
    assert calibration_tester.validate_calibration_result(
        rms_error, camera_matrix, dist_coeffs
    )

    logger.info(
        f"Calibration with {num_images} images took {calibration_time:.2f} seconds"
    )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run basic calibration test
    tester = CalibrationTester()
    test_data = CalibrationTestData()

    # Generate test data
    object_points = [test_data.generate_object_points() for _ in range(10)]
    image_points = test_data.generate_synthetic_image_points(10)

    # Run calibration
    try:
        rms_error, camera_matrix, dist_coeffs = tester.run_calibration(
            object_points, image_points
        )

        if tester.validate_calibration_result(rms_error, camera_matrix, dist_coeffs):
            print(f"✓ Calibration test passed: RMS error = {rms_error:.3f}")
            print(f"Camera matrix:\n{camera_matrix}")
            print(f"Distortion coefficients: {dist_coeffs}")
        else:
            print("✗ Calibration test failed validation")

    except Exception as e:
        print(f"✗ Calibration test failed with error: {e}")
        import traceback

        traceback.print_exc()
