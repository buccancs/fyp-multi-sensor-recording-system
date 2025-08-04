import cv2
import json
import logging
import numpy as np
import os
import pytest
import sys
from typing import List, Tuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protocol import get_calibration_config, get_calibration_error_threshold
logger = logging.getLogger(__name__)


class CalibrationTestData:

    def __init__(self):
        self.config = get_calibration_config()
        self.pattern_size = self.config.get('pattern_rows', 7
            ), self.config.get('pattern_cols', 6)
        self.square_size = self.config.get('square_size_m', 0.0245)
        self.error_threshold = get_calibration_error_threshold()

    def generate_object_points(self) ->np.ndarray:
        objp = np.zeros((self.pattern_size[0] * self.pattern_size[1], 3),
            np.float32)
        objp[:, :2] = np.mgrid[0:self.pattern_size[0], 0:self.pattern_size[1]
            ].T.reshape(-1, 2)
        objp *= self.square_size
        return objp

    def generate_synthetic_image_points(self, num_images: int=15) ->List[np
        .ndarray]:
        camera_matrix = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]],
            dtype=np.float32)
        dist_coeffs = np.array([0.1, -0.2, 0.0, 0.0, 0.0], dtype=np.float32)
        objp = self.generate_object_points()
        image_points = []
        for i in range(num_images):
            rvec = np.array([0.1 * i, 0.05 * i, 0.02 * i], dtype=np.float32)
            tvec = np.array([0.1, 0.1, 0.5 + 0.1 * i], dtype=np.float32)
            imgpts, _ = cv2.projectPoints(objp, rvec, tvec, camera_matrix,
                dist_coeffs)
            imgpts = imgpts.reshape(-1, 2)
            noise = np.random.normal(0, 0.5, imgpts.shape)
            imgpts += noise
            image_points.append(imgpts.astype(np.float32))
        return image_points

    def load_real_calibration_data(self, data_dir: str) ->Tuple[List[np.
        ndarray], List[np.ndarray]]:
        object_points = []
        image_points = []
        if not os.path.exists(data_dir):
            logger.warning(f'Calibration data directory not found: {data_dir}')
            return object_points, image_points
        for filename in os.listdir(data_dir):
            if filename.endswith('_corners.json'):
                try:
                    with open(os.path.join(data_dir, filename), 'r') as f:
                        corners_data = json.load(f)
                    if 'corners' in corners_data:
                        imgpts = np.array(corners_data['corners'], dtype=np
                            .float32)
                        image_points.append(imgpts)
                        object_points.append(self.generate_object_points())
                except Exception as e:
                    logger.warning(
                        f'Failed to load calibration data from {filename}: {e}'
                        )
        logger.info(
            f'Loaded {len(image_points)} calibration images from {data_dir}')
        return object_points, image_points


class CalibrationTester:

    def __init__(self):
        self.test_data = CalibrationTestData()
        self.image_size = 640, 480

    def run_calibration(self, object_points: List[np.ndarray], image_points:
        List[np.ndarray]) ->Tuple[float, np.ndarray, np.ndarray]:
        if len(object_points) != len(image_points):
            raise ValueError('Number of object and image point sets must match'
                )
        if len(object_points) < 3:
            raise ValueError('Need at least 3 calibration images')
        flags = cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_ZERO_TANGENT_DIST
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, self.image_size, None, None, flags
            =flags)
        return ret, camera_matrix, dist_coeffs

    def validate_calibration_result(self, rms_error: float, camera_matrix:
        np.ndarray, dist_coeffs: np.ndarray) ->bool:
        if rms_error > self.test_data.error_threshold:
            logger.error(
                f'RMS error {rms_error:.3f} exceeds threshold {self.test_data.error_threshold}'
                )
            return False
        if camera_matrix.shape != (3, 3):
            logger.error(f'Invalid camera matrix shape: {camera_matrix.shape}')
            return False
        fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
        if fx < 100 or fx > 2000 or fy < 100 or fy > 2000:
            logger.error(
                f'Unreasonable focal lengths: fx={fx:.1f}, fy={fy:.1f}')
            return False
        cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]
        img_w, img_h = self.image_size
        if abs(cx - img_w / 2) > img_w / 4 or abs(cy - img_h / 2) > img_h / 4:
            logger.warning(
                f'Principal point far from center: ({cx:.1f}, {cy:.1f})')
        if len(dist_coeffs) >= 2:
            k1, k2 = dist_coeffs[0], dist_coeffs[1]
            if abs(k1) > 1.0 or abs(k2) > 1.0:
                logger.warning(
                    f'Large distortion coefficients: k1={k1:.3f}, k2={k2:.3f}')
        logger.info(f'Calibration validation passed: RMS={rms_error:.3f}')
        return True


@pytest.fixture
def calibration_tester():
    return CalibrationTester()


@pytest.fixture
def synthetic_calibration_data():
    test_data = CalibrationTestData()
    object_points = [test_data.generate_object_points() for _ in range(15)]
    image_points = test_data.generate_synthetic_image_points(15)
    return object_points, image_points


@pytest.mark.integration
def test_calibration_with_synthetic_data(calibration_tester,
    synthetic_calibration_data):
    object_points, image_points = synthetic_calibration_data
    rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
        object_points, image_points)
    assert calibration_tester.validate_calibration_result(rms_error,
        camera_matrix, dist_coeffs)
    assert rms_error < calibration_tester.test_data.error_threshold
    assert camera_matrix.shape == (3, 3)
    assert dist_coeffs.size >= 4


@pytest.mark.integration
def test_calibration_insufficient_images(calibration_tester):
    test_data = CalibrationTestData()
    object_points = [test_data.generate_object_points() for _ in range(2)]
    image_points = test_data.generate_synthetic_image_points(2)
    with pytest.raises(ValueError, match='Need at least 3 calibration images'):
        calibration_tester.run_calibration(object_points, image_points)


@pytest.mark.integration
def test_calibration_mismatched_points(calibration_tester):
    test_data = CalibrationTestData()
    object_points = [test_data.generate_object_points() for _ in range(5)]
    image_points = test_data.generate_synthetic_image_points(3)
    with pytest.raises(ValueError, match=
        'Number of object and image point sets must match'):
        calibration_tester.run_calibration(object_points, image_points)


@pytest.mark.integration
def test_calibration_with_noise(calibration_tester):
    test_data = CalibrationTestData()
    object_points = [test_data.generate_object_points() for _ in range(20)]
    image_points = []
    for i in range(20):
        imgpts = test_data.generate_synthetic_image_points(1)[0]
        noise = np.random.normal(0, 2.0, imgpts.shape)
        imgpts += noise
        image_points.append(imgpts)
    rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
        object_points, image_points)
    assert rms_error < 5.0
    assert camera_matrix.shape == (3, 3)


@pytest.mark.integration
def test_calibration_config_loading():
    config = get_calibration_config()
    assert 'pattern_rows' in config
    assert 'pattern_cols' in config
    assert 'square_size_m' in config
    assert 'error_threshold' in config
    assert config['pattern_rows'] > 0
    assert config['pattern_cols'] > 0
    assert config['square_size_m'] > 0
    assert config['error_threshold'] > 0


@pytest.mark.integration
def test_calibration_pattern_generation():
    test_data = CalibrationTestData()
    objp = test_data.generate_object_points()
    expected_points = test_data.pattern_size[0] * test_data.pattern_size[1]
    assert objp.shape == (expected_points, 3)
    assert np.allclose(objp[:, 2], 0)
    max_x = objp[:, 0].max()
    max_y = objp[:, 1].max()
    expected_max_x = (test_data.pattern_size[0] - 1) * test_data.square_size
    expected_max_y = (test_data.pattern_size[1] - 1) * test_data.square_size
    assert abs(max_x - expected_max_x) < 1e-06
    assert abs(max_y - expected_max_y) < 1e-06


@pytest.mark.integration
def test_calibration_with_real_data():
    test_data = CalibrationTestData()
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..',
        'test_data', 'calibration')
    object_points, image_points = test_data.load_real_calibration_data(data_dir
        )
    if len(object_points) >= 3:
        calibration_tester = CalibrationTester()
        rms_error, camera_matrix, dist_coeffs = (calibration_tester.
            run_calibration(object_points, image_points))
        assert calibration_tester.validate_calibration_result(rms_error,
            camera_matrix, dist_coeffs)
    else:
        pytest.skip('No real calibration data available')


def test_calibration_error_threshold_config():
    threshold = get_calibration_error_threshold()
    assert 0.1 <= threshold <= 10.0
    assert isinstance(threshold, (int, float))


@pytest.mark.integration
@pytest.mark.slow
def test_calibration_performance():
    test_data = CalibrationTestData()
    calibration_tester = CalibrationTester()
    num_images = 50
    object_points = [test_data.generate_object_points() for _ in range(
        num_images)]
    image_points = test_data.generate_synthetic_image_points(num_images)
    import time
    start_time = time.time()
    rms_error, camera_matrix, dist_coeffs = calibration_tester.run_calibration(
        object_points, image_points)
    end_time = time.time()
    calibration_time = end_time - start_time
    assert calibration_time < 5.0
    assert calibration_tester.validate_calibration_result(rms_error,
        camera_matrix, dist_coeffs)
    logger.info(
        f'Calibration with {num_images} images took {calibration_time:.2f} seconds'
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    tester = CalibrationTester()
    test_data = CalibrationTestData()
    object_points = [test_data.generate_object_points() for _ in range(10)]
    image_points = test_data.generate_synthetic_image_points(10)
    try:
        rms_error, camera_matrix, dist_coeffs = tester.run_calibration(
            object_points, image_points)
        if tester.validate_calibration_result(rms_error, camera_matrix,
            dist_coeffs):
            print(f'✓ Calibration test passed: RMS error = {rms_error:.3f}')
            print(f'Camera matrix:\n{camera_matrix}')
            print(f'Distortion coefficients: {dist_coeffs}')
        else:
            print('✗ Calibration test failed validation')
    except Exception as e:
        print(f'✗ Calibration test failed with error: {e}')
        import traceback
        traceback.print_exc()
