import cv2
import json
import numpy as np
import os
import pytest
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calibration.calibration_manager import CalibrationManager
from calibration.calibration_result import CalibrationResult
from calibration.calibration_processor import CalibrationProcessor


class TestCalibrationManagerInitialization:

    def test_manager_initialization(self):
        manager = CalibrationManager()
        assert manager is not None
        assert hasattr(manager, 'calibration_processor')
        assert hasattr(manager, 'current_session')
        assert hasattr(manager, 'captured_frames')
        assert hasattr(manager, 'calibration_results')
        assert manager.current_session is None
        assert len(manager.captured_frames) == 0
        assert len(manager.calibration_results) == 0

    def test_processor_integration(self):
        manager = CalibrationManager()
        assert isinstance(manager.calibration_processor, CalibrationProcessor)
        assert manager.calibration_processor is not None

    def test_default_configuration(self):
        manager = CalibrationManager()
        assert hasattr(manager, 'pattern_size')
        assert hasattr(manager, 'square_size')
        assert hasattr(manager, 'min_frames_required')
        assert manager.min_frames_required >= 5
        assert manager.square_size > 0


class TestCalibrationSessionManagement:

    def setup_method(self):
        self.manager = CalibrationManager()
        self.mock_device_ids = ['device_1', 'device_2']
        self.session_name = 'test_calibration_session'

    def test_start_calibration_session_success(self):
        result = self.manager.start_calibration_session(self.
            mock_device_ids, self.session_name)
        assert result['success'] is True
        assert 'session_id' in result
        assert result['session_id'] is not None
        assert self.manager.current_session is not None
        assert self.manager.current_session['session_id'] == result[
            'session_id']
        assert self.manager.current_session['device_ids'
            ] == self.mock_device_ids
        assert self.manager.current_session['session_name'
            ] == self.session_name

    def test_start_session_with_empty_devices(self):
        result = self.manager.start_calibration_session([], self.session_name)
        assert result['success'] is False
        assert 'error' in result
        assert 'No devices' in result['error']
        assert self.manager.current_session is None

    def test_start_session_with_existing_session(self):
        self.manager.start_calibration_session(self.mock_device_ids, self.
            session_name)
        result = self.manager.start_calibration_session(['device_3'],
            'another_session')
        assert result['success'] is False
        assert 'already active' in result['error']

    def test_end_calibration_session_success(self):
        self.manager.start_calibration_session(self.mock_device_ids, self.
            session_name)
        result = self.manager.end_calibration_session()
        assert result['success'] is True
        assert self.manager.current_session is None
        assert len(self.manager.captured_frames) == 0

    def test_end_session_without_active_session(self):
        result = self.manager.end_calibration_session()
        assert result['success'] is False
        assert 'No active session' in result['error']

    def test_session_state_persistence(self):
        self.manager.start_calibration_session(self.mock_device_ids, self.
            session_name)
        session = self.manager.current_session
        assert session['device_ids'] == self.mock_device_ids
        assert session['session_name'] == self.session_name
        assert 'start_time' in session
        assert 'session_id' in session


class TestFrameCaptureCoordination:

    def setup_method(self):
        self.manager = CalibrationManager()
        self.mock_device_server = Mock()
        self.mock_device_ids = ['device_1', 'device_2']
        self.manager.start_calibration_session(self.mock_device_ids,
            'test_session')

    @patch('src.calibration.calibration_manager.time.time')
    def test_capture_calibration_frame_success(self, mock_time):
        mock_time.return_value = 1234567890.0
        self.mock_device_server.broadcast_command.return_value = 2
        with patch.object(self.manager, '_receive_calibration_frames'
            ) as mock_receive:
            mock_receive.return_value = {'success': True, 'frames': {
                'device_1': {'rgb': np.zeros((480, 640, 3)), 'thermal': np.
                zeros((240, 320))}, 'device_2': {'rgb': np.zeros((480, 640,
                3)), 'thermal': np.zeros((240, 320))}}}
            result = self.manager.capture_calibration_frame(self.
                mock_device_server)
        assert result['success'] is True
        assert result['total_frames'] == 1
        assert 'timestamp' in result
        assert len(self.manager.captured_frames) == 1

    def test_capture_frame_without_session(self):
        manager = CalibrationManager()
        result = manager.capture_calibration_frame(self.mock_device_server)
        assert result['success'] is False
        assert 'No active session' in result['error']

    def test_capture_frame_server_failure(self):
        self.mock_device_server.broadcast_command.return_value = 0
        result = self.manager.capture_calibration_frame(self.mock_device_server
            )
        assert result['success'] is False
        assert 'Failed to send' in result['error']

    @patch('src.calibration.calibration_manager.cv2.findChessboardCorners')
    def test_pattern_detection_validation(self, mock_find_corners):
        mock_find_corners.return_value = True, np.array([[100, 100], [200, 
            200]])
        self.mock_device_server.broadcast_command.return_value = 1
        with patch.object(self.manager, '_receive_calibration_frames'
            ) as mock_receive:
            mock_receive.return_value = {'success': True, 'frames': {
                'device_1': {'rgb': np.zeros((480, 640, 3)), 'thermal': np.
                zeros((240, 320))}}}
            result = self.manager.capture_calibration_frame(self.
                mock_device_server)
        assert result['success'] is True
        assert result.get('pattern_detected', False) is True

    def test_frame_storage_structure(self):
        self.mock_device_server.broadcast_command.return_value = 1
        with patch.object(self.manager, '_receive_calibration_frames'
            ) as mock_receive:
            mock_receive.return_value = {'success': True, 'frames': {
                'device_1': {'rgb': np.zeros((480, 640, 3)), 'thermal': np.
                zeros((240, 320))}}}
            self.manager.capture_calibration_frame(self.mock_device_server)
        assert len(self.manager.captured_frames) == 1
        frame_data = self.manager.captured_frames[0]
        assert 'timestamp' in frame_data
        assert 'frames' in frame_data
        assert 'device_1' in frame_data['frames']
        assert 'rgb' in frame_data['frames']['device_1']
        assert 'thermal' in frame_data['frames']['device_1']


class TestCalibrationComputation:

    def setup_method(self):
        self.manager = CalibrationManager()
        self.mock_device_ids = ['device_1']
        self.manager.start_calibration_session(self.mock_device_ids,
            'test_session')
        self._add_mock_frames()

    def _add_mock_frames(self):
        for i in range(10):
            frame_data = {'timestamp': f'2025-07-29T12:00:{i:02d}',
                'frames': {'device_1': {'rgb': np.random.randint(0, 255, (
                480, 640, 3), dtype=np.uint8), 'thermal': np.random.randint
                (0, 255, (240, 320), dtype=np.uint8)}}}
            self.manager.captured_frames.append(frame_data)

    @patch(
        'src.calibration.calibration_processor.CalibrationProcessor.process_calibration'
        )
    def test_compute_calibration_success(self, mock_process):
        mock_result = CalibrationResult('device_1')
        mock_result.rgb_camera_matrix = np.eye(3)
        mock_result.rgb_dist_coeffs = np.zeros(5)
        mock_result.thermal_camera_matrix = np.eye(3)
        mock_result.thermal_dist_coeffs = np.zeros(5)
        mock_result.rotation_matrix = np.eye(3)
        mock_result.translation_vector = np.zeros(3)
        mock_result.rgb_reprojection_error = 0.5
        mock_result.thermal_reprojection_error = 0.7
        mock_result.stereo_reprojection_error = 0.8
        mock_process.return_value = {'device_1': mock_result}
        result = self.manager.compute_calibration()
        assert result['success'] is True
        assert 'results' in result
        assert 'device_1' in result['results']
        assert len(self.manager.calibration_results) == 1

    def test_compute_calibration_insufficient_frames(self):
        self.manager.captured_frames = []
        result = self.manager.compute_calibration()
        assert result['success'] is False
        assert 'Insufficient frames' in result['error']

    def test_compute_calibration_without_session(self):
        manager = CalibrationManager()
        result = manager.compute_calibration()
        assert result['success'] is False
        assert 'No active session' in result['error']

    @patch(
        'src.calibration.calibration_processor.CalibrationProcessor.process_calibration'
        )
    def test_compute_calibration_processing_failure(self, mock_process):
        mock_process.side_effect = Exception('Processing failed')
        result = self.manager.compute_calibration()
        assert result['success'] is False
        assert 'Processing failed' in result['error']

    @patch(
        'src.calibration.calibration_processor.CalibrationProcessor.process_calibration'
        )
    def test_calibration_quality_assessment(self, mock_process):
        mock_result = CalibrationResult('device_1')
        mock_result.rgb_reprojection_error = 5.0
        mock_result.thermal_reprojection_error = 7.0
        mock_result.stereo_reprojection_error = 8.0
        mock_process.return_value = {'device_1': mock_result}
        result = self.manager.compute_calibration()
        assert result['success'] is True
        assert 'quality_warnings' in result or result['results']['device_1'
            ].rgb_reprojection_error > 1.0


class TestResultManagement:

    def setup_method(self):
        self.manager = CalibrationManager()
        self.temp_dir = tempfile.mkdtemp()
        self.test_result = CalibrationResult('device_1')
        self._setup_test_result()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_test_result(self):
        self.test_result.rgb_camera_matrix = np.eye(3)
        self.test_result.rgb_dist_coeffs = np.zeros(5)
        self.test_result.thermal_camera_matrix = np.eye(3)
        self.test_result.thermal_dist_coeffs = np.zeros(5)
        self.test_result.rotation_matrix = np.eye(3)
        self.test_result.translation_vector = np.zeros(3)
        self.test_result.rgb_reprojection_error = 0.5
        self.test_result.thermal_reprojection_error = 0.7
        self.test_result.stereo_reprojection_error = 0.8

    def test_save_calibration_results(self):
        self.manager.calibration_results = {'device_1': self.test_result}
        save_path = os.path.join(self.temp_dir, 'calibration_device_1.json')
        result = self.manager.save_calibration_results(save_path)
        assert result['success'] is True
        assert os.path.exists(save_path)
        with open(save_path, 'r') as f:
            data = json.load(f)
            assert 'device_id' in data
            assert data['device_id'] == 'device_1'

    def test_load_calibration_results(self):
        save_path = os.path.join(self.temp_dir, 'calibration_device_1.json')
        self.test_result.save_to_file(save_path)
        result = self.manager.load_calibration_results(save_path)
        assert result['success'] is True
        assert 'device_1' in self.manager.calibration_results
        loaded_result = self.manager.calibration_results['device_1']
        assert loaded_result.device_id == 'device_1'

    def test_save_results_without_data(self):
        save_path = os.path.join(self.temp_dir, 'empty_calibration.json')
        result = self.manager.save_calibration_results(save_path)
        assert result['success'] is False
        assert 'No calibration results' in result['error']

    def test_load_nonexistent_file(self):
        nonexistent_path = os.path.join(self.temp_dir, 'nonexistent.json')
        result = self.manager.load_calibration_results(nonexistent_path)
        assert result['success'] is False
        assert 'File not found' in result['error'
            ] or 'does not exist' in result['error']

    def test_result_validation_on_load(self):
        invalid_path = os.path.join(self.temp_dir, 'invalid_calibration.json')
        with open(invalid_path, 'w') as f:
            json.dump({'invalid': 'data'}, f)
        result = self.manager.load_calibration_results(invalid_path)
        assert result['success'] is False
        assert 'Invalid' in result['error'] or 'validation' in result['error']


class TestThermalOverlayFunctionality:

    def setup_method(self):
        self.manager = CalibrationManager()
        self.test_result = CalibrationResult('device_1')
        self._setup_overlay_data()

    def _setup_overlay_data(self):
        self.test_result.homography_matrix = np.eye(3)
        self.manager.calibration_results = {'device_1': self.test_result}
        self.rgb_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.
            uint8)
        self.thermal_image = np.random.randint(0, 255, (240, 320), dtype=np
            .uint8)

    def test_apply_thermal_overlay_success(self):
        result = self.manager.apply_thermal_overlay('device_1', self.
            rgb_image, self.thermal_image, alpha=0.3)
        assert result['success'] is True
        assert 'overlay_image' in result
        assert result['overlay_image'].shape == self.rgb_image.shape

    def test_overlay_without_calibration(self):
        manager = CalibrationManager()
        result = manager.apply_thermal_overlay('device_1', self.rgb_image,
            self.thermal_image)
        assert result['success'] is False
        assert 'No calibration data' in result['error']

    def test_overlay_alpha_blending(self):
        alpha_values = [0.0, 0.3, 0.5, 0.7, 1.0]
        for alpha in alpha_values:
            result = self.manager.apply_thermal_overlay('device_1', self.
                rgb_image, self.thermal_image, alpha=alpha)
            assert result['success'] is True
            assert result['alpha'] == alpha

    def test_overlay_with_invalid_images(self):
        result = self.manager.apply_thermal_overlay('device_1', None, self.
            thermal_image)
        assert result['success'] is False
        assert 'Invalid' in result['error']

    def test_overlay_color_mapping(self):
        with patch('cv2.applyColorMap') as mock_colormap:
            mock_colormap.return_value = np.random.randint(0, 255, (240, 
                320, 3), dtype=np.uint8)
            result = self.manager.apply_thermal_overlay('device_1', self.
                rgb_image, self.thermal_image, colormap='jet')
            assert result['success'] is True
            mock_colormap.assert_called_once()


class TestErrorHandlingAndEdgeCases:

    def setup_method(self):
        self.manager = CalibrationManager()

    def test_invalid_device_ids(self):
        invalid_ids = [None, '', [], [''], [None]]
        for invalid_id in invalid_ids:
            result = self.manager.start_calibration_session(invalid_id, 'test')
            assert result['success'] is False

    def test_memory_management_large_frames(self):
        self.manager.start_calibration_session(['device_1'], 'memory_test')
        for i in range(50):
            large_frame = {'timestamp': f'2025-07-29T12:00:{i:02d}',
                'frames': {'device_1': {'rgb': np.random.randint(0, 255, (
                1080, 1920, 3), dtype=np.uint8), 'thermal': np.random.
                randint(0, 255, (480, 640), dtype=np.uint8)}}}
            self.manager.captured_frames.append(large_frame)
        assert len(self.manager.captured_frames) == 50
        result = self.manager.end_calibration_session()
        assert result['success'] is True
        assert len(self.manager.captured_frames) == 0

    def test_concurrent_operations(self):
        self.manager.start_calibration_session(['device_1'], 'concurrent_test')
        with patch.object(self.manager, '_receive_calibration_frames'
            ) as mock_receive:
            mock_receive.return_value = {'success': True, 'frames': {
                'device_1': {'rgb': np.zeros((480, 640, 3)), 'thermal': np.
                zeros((240, 320))}}}
            mock_server = Mock()
            mock_server.broadcast_command.return_value = 1
            results = []
            for _ in range(5):
                result = self.manager.capture_calibration_frame(mock_server)
                results.append(result)
            for result in results:
                assert result['success'] is True
            assert len(self.manager.captured_frames) == 5

    def test_resource_cleanup_on_error(self):
        self.manager.start_calibration_session(['device_1'], 'cleanup_test')
        self.manager.captured_frames.append({'timestamp':
            '2025-07-29T12:00:00', 'frames': {'device_1': {'rgb': np.zeros(
            (480, 640, 3)), 'thermal': np.zeros((240, 320))}}})
        with patch.object(self.manager.calibration_processor,
            'process_calibration') as mock_process:
            mock_process.side_effect = Exception('Computation error')
            result = self.manager.compute_calibration()
            assert result['success'] is False
        cleanup_result = self.manager.end_calibration_session()
        assert cleanup_result['success'] is True
        assert len(self.manager.captured_frames) == 0


class TestIntegrationScenarios:

    def setup_method(self):
        self.manager = CalibrationManager()
        self.mock_server = Mock()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_calibration_workflow(self):
        device_ids = ['device_1', 'device_2']
        session_result = self.manager.start_calibration_session(device_ids,
            'integration_test')
        assert session_result['success'] is True
        self.mock_server.broadcast_command.return_value = 2
        with patch.object(self.manager, '_receive_calibration_frames'
            ) as mock_receive:
            mock_receive.return_value = {'success': True, 'frames': {
                'device_1': {'rgb': np.zeros((480, 640, 3)), 'thermal': np.
                zeros((240, 320))}, 'device_2': {'rgb': np.zeros((480, 640,
                3)), 'thermal': np.zeros((240, 320))}}}
            for i in range(10):
                capture_result = self.manager.capture_calibration_frame(self
                    .mock_server)
                assert capture_result['success'] is True
        assert len(self.manager.captured_frames) == 10
        with patch.object(self.manager.calibration_processor,
            'process_calibration') as mock_process:
            mock_results = {}
            for device_id in device_ids:
                result = CalibrationResult(device_id)
                result.rgb_camera_matrix = np.eye(3)
                result.rgb_dist_coeffs = np.zeros(5)
                result.thermal_camera_matrix = np.eye(3)
                result.thermal_dist_coeffs = np.zeros(5)
                result.rotation_matrix = np.eye(3)
                result.translation_vector = np.zeros(3)
                result.homography_matrix = np.eye(3)
                mock_results[device_id] = result
            mock_process.return_value = mock_results
            compute_result = self.manager.compute_calibration()
            assert compute_result['success'] is True
        save_path = os.path.join(self.temp_dir, 'integration_calibration.json')
        save_result = self.manager.save_calibration_results(save_path)
        assert save_result['success'] is True
        rgb_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        thermal_image = np.random.randint(0, 255, (240, 320), dtype=np.uint8)
        overlay_result = self.manager.apply_thermal_overlay('device_1',
            rgb_image, thermal_image)
        assert overlay_result['success'] is True
        end_result = self.manager.end_calibration_session()
        assert end_result['success'] is True

    def test_multi_device_calibration_workflow(self):
        device_ids = ['device_1', 'device_2', 'device_3']
        session_result = self.manager.start_calibration_session(device_ids,
            'multi_device_test')
        assert session_result['success'] is True
        self.mock_server.broadcast_command.return_value = 3
        with patch.object(self.manager, '_receive_calibration_frames'
            ) as mock_receive:
            mock_receive.return_value = {'success': True, 'frames': {
                device_id: {'rgb': np.random.randint(0, 255, (480, 640, 3),
                dtype=np.uint8), 'thermal': np.random.randint(0, 255, (240,
                320), dtype=np.uint8)} for device_id in device_ids}}
            for _ in range(8):
                result = self.manager.capture_calibration_frame(self.
                    mock_server)
                assert result['success'] is True
        for frame_data in self.manager.captured_frames:
            for device_id in device_ids:
                assert device_id in frame_data['frames']
        with patch.object(self.manager.calibration_processor,
            'process_calibration') as mock_process:
            mock_results = {}
            for device_id in device_ids:
                result = CalibrationResult(device_id)
                result.rgb_camera_matrix = np.eye(3)
                result.rgb_dist_coeffs = np.zeros(5)
                result.thermal_camera_matrix = np.eye(3)
                result.thermal_dist_coeffs = np.zeros(5)
                result.rotation_matrix = np.eye(3)
                result.translation_vector = np.zeros(3)
                mock_results[device_id] = result
            mock_process.return_value = mock_results
            compute_result = self.manager.compute_calibration()
            assert compute_result['success'] is True
            assert len(self.manager.calibration_results) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
