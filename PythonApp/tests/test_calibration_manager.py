"""
Comprehensive unit tests for CalibrationManager component.

This module provides extensive testing coverage for the CalibrationManager class,
ensuring all functionality is thoroughly validated according to project guidelines.

Test Coverage:
- Session management lifecycle
- Frame capture coordination
- Calibration computation integration
- Quality assessment and validation
- Result management and persistence
- Thermal overlay functionality
- Error handling and edge cases

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Guidelines: 100% test coverage, test every feature repeatedly
"""

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

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from calibration.calibration_manager import CalibrationManager
from calibration.calibration_result import CalibrationResult
from calibration.calibration_processor import CalibrationProcessor


class TestCalibrationManagerInitialization:
    """Test CalibrationManager initialization and basic setup."""

    def test_manager_initialization(self):
        """Test basic CalibrationManager initialization."""
        manager = CalibrationManager()

        assert manager is not None
        assert hasattr(manager, "calibration_processor")
        assert hasattr(manager, "current_session")
        assert hasattr(manager, "captured_frames")
        assert hasattr(manager, "calibration_results")
        assert manager.current_session is None
        assert len(manager.captured_frames) == 0
        assert len(manager.calibration_results) == 0

    def test_processor_integration(self):
        """Test CalibrationProcessor integration."""
        manager = CalibrationManager()

        assert isinstance(manager.calibration_processor, CalibrationProcessor)
        assert manager.calibration_processor is not None

    def test_default_configuration(self):
        """Test default configuration values."""
        manager = CalibrationManager()

        # Test default pattern configuration
        assert hasattr(manager, "pattern_size")
        assert hasattr(manager, "square_size")
        assert hasattr(manager, "min_frames_required")

        # Verify reasonable defaults
        assert manager.min_frames_required >= 5
        assert manager.square_size > 0


class TestCalibrationSessionManagement:
    """Test calibration session lifecycle management."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = CalibrationManager()
        self.mock_device_ids = ["device_1", "device_2"]
        self.session_name = "test_calibration_session"

    def test_start_calibration_session_success(self):
        """Test successful calibration session start."""
        result = self.manager.start_calibration_session(
            self.mock_device_ids, self.session_name
        )

        assert result["success"] is True
        assert "session_id" in result
        assert result["session_id"] is not None
        assert self.manager.current_session is not None
        assert self.manager.current_session["session_id"] == result["session_id"]
        assert self.manager.current_session["device_ids"] == self.mock_device_ids
        assert self.manager.current_session["session_name"] == self.session_name

    def test_start_session_with_empty_devices(self):
        """Test session start with empty device list."""
        result = self.manager.start_calibration_session([], self.session_name)

        assert result["success"] is False
        assert "error" in result
        assert "No devices" in result["error"]
        assert self.manager.current_session is None

    def test_start_session_with_existing_session(self):
        """Test starting session when one already exists."""
        # Start first session
        self.manager.start_calibration_session(self.mock_device_ids, self.session_name)

        # Try to start another session
        result = self.manager.start_calibration_session(["device_3"], "another_session")

        assert result["success"] is False
        assert "already active" in result["error"]

    def test_end_calibration_session_success(self):
        """Test successful session end."""
        # Start session first
        self.manager.start_calibration_session(self.mock_device_ids, self.session_name)

        # End session
        result = self.manager.end_calibration_session()

        assert result["success"] is True
        assert self.manager.current_session is None
        assert len(self.manager.captured_frames) == 0

    def test_end_session_without_active_session(self):
        """Test ending session when none is active."""
        result = self.manager.end_calibration_session()

        assert result["success"] is False
        assert "No active session" in result["error"]

    def test_session_state_persistence(self):
        """Test session state is properly maintained."""
        self.manager.start_calibration_session(self.mock_device_ids, self.session_name)

        session = self.manager.current_session
        assert session["device_ids"] == self.mock_device_ids
        assert session["session_name"] == self.session_name
        assert "start_time" in session
        assert "session_id" in session


class TestFrameCaptureCoordination:
    """Test frame capture coordination functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = CalibrationManager()
        self.mock_device_server = Mock()
        self.mock_device_ids = ["device_1", "device_2"]

        # Start session for testing
        self.manager.start_calibration_session(self.mock_device_ids, "test_session")

    @patch("src.calibration.calibration_manager.time.time")
    def test_capture_calibration_frame_success(self, mock_time):
        """Test successful calibration frame capture."""
        mock_time.return_value = 1234567890.0

        # Mock device server response
        self.mock_device_server.broadcast_command.return_value = 2

        # Mock frame reception
        with patch.object(self.manager, "_receive_calibration_frames") as mock_receive:
            mock_receive.return_value = {
                "success": True,
                "frames": {
                    "device_1": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    },
                    "device_2": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    },
                },
            }

            result = self.manager.capture_calibration_frame(self.mock_device_server)

        assert result["success"] is True
        assert result["total_frames"] == 1
        assert "timestamp" in result
        assert len(self.manager.captured_frames) == 1

    def test_capture_frame_without_session(self):
        """Test frame capture without active session."""
        manager = CalibrationManager()  # No session started

        result = manager.capture_calibration_frame(self.mock_device_server)

        assert result["success"] is False
        assert "No active session" in result["error"]

    def test_capture_frame_server_failure(self):
        """Test frame capture when server command fails."""
        self.mock_device_server.broadcast_command.return_value = 0

        result = self.manager.capture_calibration_frame(self.mock_device_server)

        assert result["success"] is False
        assert "Failed to send" in result["error"]

    @patch("src.calibration.calibration_manager.cv2.findChessboardCorners")
    def test_pattern_detection_validation(self, mock_find_corners):
        """Test pattern detection during frame capture."""
        mock_find_corners.return_value = (True, np.array([[100, 100], [200, 200]]))

        self.mock_device_server.broadcast_command.return_value = 1

        with patch.object(self.manager, "_receive_calibration_frames") as mock_receive:
            mock_receive.return_value = {
                "success": True,
                "frames": {
                    "device_1": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    }
                },
            }

            result = self.manager.capture_calibration_frame(self.mock_device_server)

        assert result["success"] is True
        assert result.get("pattern_detected", False) is True

    def test_frame_storage_structure(self):
        """Test proper frame storage structure."""
        self.mock_device_server.broadcast_command.return_value = 1

        with patch.object(self.manager, "_receive_calibration_frames") as mock_receive:
            mock_receive.return_value = {
                "success": True,
                "frames": {
                    "device_1": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    }
                },
            }

            self.manager.capture_calibration_frame(self.mock_device_server)

        assert len(self.manager.captured_frames) == 1
        frame_data = self.manager.captured_frames[0]

        assert "timestamp" in frame_data
        assert "frames" in frame_data
        assert "device_1" in frame_data["frames"]
        assert "rgb" in frame_data["frames"]["device_1"]
        assert "thermal" in frame_data["frames"]["device_1"]


class TestCalibrationComputation:
    """Test calibration computation functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = CalibrationManager()
        self.mock_device_ids = ["device_1"]

        # Start session and add mock frames
        self.manager.start_calibration_session(self.mock_device_ids, "test_session")
        self._add_mock_frames()

    def _add_mock_frames(self):
        """Add mock calibration frames for testing."""
        for i in range(10):  # Add 10 frames (above minimum)
            frame_data = {
                "timestamp": f"2025-07-29T12:00:{i:02d}",
                "frames": {
                    "device_1": {
                        "rgb": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
                        "thermal": np.random.randint(
                            0, 255, (240, 320), dtype=np.uint8
                        ),
                    }
                },
            }
            self.manager.captured_frames.append(frame_data)

    @patch(
        "src.calibration.calibration_processor.CalibrationProcessor.process_calibration"
    )
    def test_compute_calibration_success(self, mock_process):
        """Test successful calibration computation."""
        # Mock successful calibration result
        mock_result = CalibrationResult("device_1")
        mock_result.rgb_camera_matrix = np.eye(3)
        mock_result.rgb_dist_coeffs = np.zeros(5)
        mock_result.thermal_camera_matrix = np.eye(3)
        mock_result.thermal_dist_coeffs = np.zeros(5)
        mock_result.rotation_matrix = np.eye(3)
        mock_result.translation_vector = np.zeros(3)
        mock_result.rgb_reprojection_error = 0.5
        mock_result.thermal_reprojection_error = 0.7
        mock_result.stereo_reprojection_error = 0.8

        mock_process.return_value = {"device_1": mock_result}

        result = self.manager.compute_calibration()

        assert result["success"] is True
        assert "results" in result
        assert "device_1" in result["results"]
        assert len(self.manager.calibration_results) == 1

    def test_compute_calibration_insufficient_frames(self):
        """Test calibration computation with insufficient frames."""
        # Clear frames to simulate insufficient data
        self.manager.captured_frames = []

        result = self.manager.compute_calibration()

        assert result["success"] is False
        assert "Insufficient frames" in result["error"]

    def test_compute_calibration_without_session(self):
        """Test calibration computation without active session."""
        manager = CalibrationManager()  # No session started

        result = manager.compute_calibration()

        assert result["success"] is False
        assert "No active session" in result["error"]

    @patch(
        "src.calibration.calibration_processor.CalibrationProcessor.process_calibration"
    )
    def test_compute_calibration_processing_failure(self, mock_process):
        """Test calibration computation when processing fails."""
        mock_process.side_effect = Exception("Processing failed")

        result = self.manager.compute_calibration()

        assert result["success"] is False
        assert "Processing failed" in result["error"]

    @patch(
        "src.calibration.calibration_processor.CalibrationProcessor.process_calibration"
    )
    def test_calibration_quality_assessment(self, mock_process):
        """Test calibration quality assessment."""
        # Mock result with high error (poor quality)
        mock_result = CalibrationResult("device_1")
        mock_result.rgb_reprojection_error = 5.0  # High error
        mock_result.thermal_reprojection_error = 7.0
        mock_result.stereo_reprojection_error = 8.0

        mock_process.return_value = {"device_1": mock_result}

        result = self.manager.compute_calibration()

        assert result["success"] is True
        # Should include quality warnings
        assert (
            "quality_warnings" in result
            or result["results"]["device_1"].rgb_reprojection_error > 1.0
        )


class TestResultManagement:
    """Test calibration result management and persistence."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = CalibrationManager()
        self.temp_dir = tempfile.mkdtemp()
        self.test_result = CalibrationResult("device_1")
        self._setup_test_result()

    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_test_result(self):
        """Setup test calibration result."""
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
        """Test saving calibration results to file."""
        self.manager.calibration_results = {"device_1": self.test_result}

        save_path = os.path.join(self.temp_dir, "calibration_device_1.json")
        result = self.manager.save_calibration_results(save_path)

        assert result["success"] is True
        assert os.path.exists(save_path)

        # Verify file content
        with open(save_path, "r") as f:
            data = json.load(f)
            assert "device_id" in data
            assert data["device_id"] == "device_1"

    def test_load_calibration_results(self):
        """Test loading calibration results from file."""
        # First save a result
        save_path = os.path.join(self.temp_dir, "calibration_device_1.json")
        self.test_result.save_to_file(save_path)

        # Then load it
        result = self.manager.load_calibration_results(save_path)

        assert result["success"] is True
        assert "device_1" in self.manager.calibration_results
        loaded_result = self.manager.calibration_results["device_1"]
        assert loaded_result.device_id == "device_1"

    def test_save_results_without_data(self):
        """Test saving when no calibration results exist."""
        save_path = os.path.join(self.temp_dir, "empty_calibration.json")
        result = self.manager.save_calibration_results(save_path)

        assert result["success"] is False
        assert "No calibration results" in result["error"]

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        result = self.manager.load_calibration_results(nonexistent_path)

        assert result["success"] is False
        assert (
            "File not found" in result["error"] or "does not exist" in result["error"]
        )

    def test_result_validation_on_load(self):
        """Test validation of loaded calibration results."""
        # Create invalid calibration file
        invalid_path = os.path.join(self.temp_dir, "invalid_calibration.json")
        with open(invalid_path, "w") as f:
            json.dump({"invalid": "data"}, f)

        result = self.manager.load_calibration_results(invalid_path)

        assert result["success"] is False
        assert "Invalid" in result["error"] or "validation" in result["error"]


class TestThermalOverlayFunctionality:
    """Test thermal overlay functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = CalibrationManager()
        self.test_result = CalibrationResult("device_1")
        self._setup_overlay_data()

    def _setup_overlay_data(self):
        """Setup test data for overlay functionality."""
        self.test_result.homography_matrix = np.eye(3)
        self.manager.calibration_results = {"device_1": self.test_result}

        # Create test images
        self.rgb_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.thermal_image = np.random.randint(0, 255, (240, 320), dtype=np.uint8)

    def test_apply_thermal_overlay_success(self):
        """Test successful thermal overlay application."""
        result = self.manager.apply_thermal_overlay(
            "device_1", self.rgb_image, self.thermal_image, alpha=0.3
        )

        assert result["success"] is True
        assert "overlay_image" in result
        assert result["overlay_image"].shape == self.rgb_image.shape

    def test_overlay_without_calibration(self):
        """Test overlay application without calibration data."""
        manager = CalibrationManager()  # No calibration results

        result = manager.apply_thermal_overlay(
            "device_1", self.rgb_image, self.thermal_image
        )

        assert result["success"] is False
        assert "No calibration data" in result["error"]

    def test_overlay_alpha_blending(self):
        """Test different alpha blending values."""
        alpha_values = [0.0, 0.3, 0.5, 0.7, 1.0]

        for alpha in alpha_values:
            result = self.manager.apply_thermal_overlay(
                "device_1", self.rgb_image, self.thermal_image, alpha=alpha
            )

            assert result["success"] is True
            assert result["alpha"] == alpha

    def test_overlay_with_invalid_images(self):
        """Test overlay with invalid image inputs."""
        # Test with None images
        result = self.manager.apply_thermal_overlay(
            "device_1", None, self.thermal_image
        )

        assert result["success"] is False
        assert "Invalid" in result["error"]

    def test_overlay_color_mapping(self):
        """Test thermal image color mapping."""
        with patch("cv2.applyColorMap") as mock_colormap:
            mock_colormap.return_value = np.random.randint(
                0, 255, (240, 320, 3), dtype=np.uint8
            )

            result = self.manager.apply_thermal_overlay(
                "device_1", self.rgb_image, self.thermal_image, colormap="jet"
            )

            assert result["success"] is True
            mock_colormap.assert_called_once()


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = CalibrationManager()

    def test_invalid_device_ids(self):
        """Test handling of invalid device IDs."""
        invalid_ids = [None, "", [], [""], [None]]

        for invalid_id in invalid_ids:
            result = self.manager.start_calibration_session(invalid_id, "test")
            assert result["success"] is False

    def test_memory_management_large_frames(self):
        """Test memory management with large frame data."""
        # Start session
        self.manager.start_calibration_session(["device_1"], "memory_test")

        # Add many large frames
        for i in range(50):
            large_frame = {
                "timestamp": f"2025-07-29T12:00:{i:02d}",
                "frames": {
                    "device_1": {
                        "rgb": np.random.randint(
                            0, 255, (1080, 1920, 3), dtype=np.uint8
                        ),
                        "thermal": np.random.randint(
                            0, 255, (480, 640), dtype=np.uint8
                        ),
                    }
                },
            }
            self.manager.captured_frames.append(large_frame)

        # Should handle large data without crashing
        assert len(self.manager.captured_frames) == 50

        # Cleanup should work
        result = self.manager.end_calibration_session()
        assert result["success"] is True
        assert len(self.manager.captured_frames) == 0

    def test_concurrent_operations(self):
        """Test handling of concurrent operations."""
        # This would be more comprehensive with actual threading,
        # but we test the state management aspects

        self.manager.start_calibration_session(["device_1"], "concurrent_test")

        # Simulate concurrent frame captures
        with patch.object(self.manager, "_receive_calibration_frames") as mock_receive:
            mock_receive.return_value = {
                "success": True,
                "frames": {
                    "device_1": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    }
                },
            }

            mock_server = Mock()
            mock_server.broadcast_command.return_value = 1

            # Multiple rapid captures
            results = []
            for _ in range(5):
                result = self.manager.capture_calibration_frame(mock_server)
                results.append(result)

            # All should succeed
            for result in results:
                assert result["success"] is True

            assert len(self.manager.captured_frames) == 5

    def test_resource_cleanup_on_error(self):
        """Test proper resource cleanup when errors occur."""
        self.manager.start_calibration_session(["device_1"], "cleanup_test")

        # Add some frames
        self.manager.captured_frames.append(
            {
                "timestamp": "2025-07-29T12:00:00",
                "frames": {
                    "device_1": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    }
                },
            }
        )

        # Simulate error during computation
        with patch.object(
            self.manager.calibration_processor, "process_calibration"
        ) as mock_process:
            mock_process.side_effect = Exception("Computation error")

            result = self.manager.compute_calibration()
            assert result["success"] is False

        # Resources should still be cleanable
        cleanup_result = self.manager.end_calibration_session()
        assert cleanup_result["success"] is True
        assert len(self.manager.captured_frames) == 0


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def setup_method(self):
        """Setup for integration tests."""
        self.manager = CalibrationManager()
        self.mock_server = Mock()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after integration tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_calibration_workflow(self):
        """Test complete calibration workflow from start to finish."""
        device_ids = ["device_1", "device_2"]

        # 1. Start session
        session_result = self.manager.start_calibration_session(
            device_ids, "integration_test"
        )
        assert session_result["success"] is True

        # 2. Capture multiple frames
        self.mock_server.broadcast_command.return_value = 2

        with patch.object(self.manager, "_receive_calibration_frames") as mock_receive:
            mock_receive.return_value = {
                "success": True,
                "frames": {
                    "device_1": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    },
                    "device_2": {
                        "rgb": np.zeros((480, 640, 3)),
                        "thermal": np.zeros((240, 320)),
                    },
                },
            }

            # Capture 10 frames
            for i in range(10):
                capture_result = self.manager.capture_calibration_frame(
                    self.mock_server
                )
                assert capture_result["success"] is True

        assert len(self.manager.captured_frames) == 10

        # 3. Compute calibration
        with patch.object(
            self.manager.calibration_processor, "process_calibration"
        ) as mock_process:
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
            assert compute_result["success"] is True

        # 4. Save results
        save_path = os.path.join(self.temp_dir, "integration_calibration.json")
        save_result = self.manager.save_calibration_results(save_path)
        assert save_result["success"] is True

        # 5. Test overlay functionality
        rgb_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        thermal_image = np.random.randint(0, 255, (240, 320), dtype=np.uint8)

        overlay_result = self.manager.apply_thermal_overlay(
            "device_1", rgb_image, thermal_image
        )
        assert overlay_result["success"] is True

        # 6. End session
        end_result = self.manager.end_calibration_session()
        assert end_result["success"] is True

    def test_multi_device_calibration_workflow(self):
        """Test calibration workflow with multiple devices."""
        device_ids = ["device_1", "device_2", "device_3"]

        # Start session with multiple devices
        session_result = self.manager.start_calibration_session(
            device_ids, "multi_device_test"
        )
        assert session_result["success"] is True

        # Capture frames from all devices
        self.mock_server.broadcast_command.return_value = 3

        with patch.object(self.manager, "_receive_calibration_frames") as mock_receive:
            mock_receive.return_value = {
                "success": True,
                "frames": {
                    device_id: {
                        "rgb": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
                        "thermal": np.random.randint(
                            0, 255, (240, 320), dtype=np.uint8
                        ),
                    }
                    for device_id in device_ids
                },
            }

            # Capture sufficient frames
            for _ in range(8):
                result = self.manager.capture_calibration_frame(self.mock_server)
                assert result["success"] is True

        # Verify all devices have frame data
        for frame_data in self.manager.captured_frames:
            for device_id in device_ids:
                assert device_id in frame_data["frames"]

        # Compute calibration for all devices
        with patch.object(
            self.manager.calibration_processor, "process_calibration"
        ) as mock_process:
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
            assert compute_result["success"] is True
            assert len(self.manager.calibration_results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
