"""
Configuration and Schema Integrity Tests.

This module provides tests to validate the integrity of the configuration
and schema files. It ensures that the config and schema files are complete,
consistent, and match the application's expectations.
"""

import json
import logging
import os
import pytest
import sys

# Import protocol utilities
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from protocol import (
    get_config_manager,
    get_schema_manager,
    validate_config,
    get_valid_message_types,
    create_message,
)

logger = logging.getLogger(__name__)


class ConfigIntegrityTester:
    """Tests configuration file integrity and structure."""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.required_sections = ["network", "devices", "UI", "calibration"]
        self.optional_sections = [
            "session",
            "logging",
            "testing",
            "performance",
            "security",
        ]

    def test_config_file_exists(self) -> bool:
        """Test that the configuration file exists and is readable."""
        try:
            config_path = self.config_manager.config_path
            return os.path.exists(config_path) and os.path.isfile(config_path)
        except Exception as e:
            logger.error(f"Error checking config file existence: {e}")
            return False

    def test_config_json_valid(self) -> bool:
        """Test that the configuration file contains valid JSON."""
        try:
            with open(self.config_manager.config_path, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            return False

    def test_required_sections_exist(self) -> bool:
        """Test that all required configuration sections exist."""
        config = self.config_manager.config
        if not config:
            return False

        missing_sections = []
        for section in self.required_sections:
            if section not in config:
                missing_sections.append(section)

        if missing_sections:
            logger.error(f"Missing required config sections: {missing_sections}")
            return False

        return True

    def test_network_config_structure(self) -> bool:
        """Test network configuration section structure."""
        network = self.config_manager.get_network_config()

        required_keys = ["host", "port"]
        optional_keys = [
            "protocol",
            "timeout_seconds",
            "buffer_size",
            "max_connections",
            "heartbeat_interval",
            "reconnect_attempts",
        ]

        # Check required keys
        for key in required_keys:
            if key not in network:
                logger.error(f"Missing required network config key: {key}")
                return False

        # Validate types and values
        if not isinstance(network.get("host"), str):
            logger.error("Network host must be a string")
            return False

        port = network.get("port")
        if not isinstance(port, int) or port <= 0 or port > 65535:
            logger.error(f"Invalid network port: {port}")
            return False

        return True

    def test_devices_config_structure(self) -> bool:
        """Test devices configuration section structure."""
        devices = self.config_manager.get_devices_config()

        required_keys = ["camera_id", "frame_rate"]

        # Check required keys
        for key in required_keys:
            if key not in devices:
                logger.error(f"Missing required devices config key: {key}")
                return False

        # Validate frame rate
        frame_rate = devices.get("frame_rate")
        if not isinstance(frame_rate, int) or frame_rate <= 0:
            logger.error(f"Invalid frame rate: {frame_rate}")
            return False

        # Validate resolution if present
        if "resolution" in devices:
            resolution = devices["resolution"]
            if not isinstance(resolution, dict):
                logger.error("Resolution must be a dictionary")
                return False

            if "width" not in resolution or "height" not in resolution:
                logger.error("Resolution must have width and height")
                return False

            if (
                not isinstance(resolution["width"], int)
                or not isinstance(resolution["height"], int)
                or resolution["width"] <= 0
                or resolution["height"] <= 0
            ):
                logger.error("Invalid resolution values")
                return False

        return True

    def test_calibration_config_structure(self) -> bool:
        """Test calibration configuration section structure."""
        calibration = self.config_manager.get_calibration_config()

        required_keys = [
            "pattern_rows",
            "pattern_cols",
            "square_size_m",
            "error_threshold",
        ]

        # Check required keys
        for key in required_keys:
            if key not in calibration:
                logger.error(f"Missing required calibration config key: {key}")
                return False

        # Validate pattern size
        rows = calibration.get("pattern_rows")
        cols = calibration.get("pattern_cols")

        if not isinstance(rows, int) or rows <= 0:
            logger.error(f"Invalid pattern rows: {rows}")
            return False

        if not isinstance(cols, int) or cols <= 0:
            logger.error(f"Invalid pattern cols: {cols}")
            return False

        # Validate square size
        square_size = calibration.get("square_size_m")
        if not isinstance(square_size, (int, float)) or square_size <= 0:
            logger.error(f"Invalid square size: {square_size}")
            return False

        # Validate error threshold
        threshold = calibration.get("error_threshold")
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            logger.error(f"Invalid error threshold: {threshold}")
            return False

        return True

    def test_config_cross_validation(self) -> bool:
        """Test cross-validation between different config sections."""
        # Example: Check that preview resolution is smaller than main resolution
        devices = self.config_manager.get_devices_config()

        if "resolution" in devices and "preview_resolution" in devices:
            main_res = devices["resolution"]
            preview_res = devices["preview_resolution"]

            if (
                preview_res["width"] > main_res["width"]
                or preview_res["height"] > main_res["height"]
            ):
                logger.warning("Preview resolution larger than main resolution")

        return True


class SchemaIntegrityTester:
    """Tests schema file integrity and structure."""

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.expected_message_types = {
            "start_record",
            "stop_record",
            "preview_frame",
            "file_chunk",
            "device_status",
            "ack",
            "calibration_start",
            "calibration_result",
        }

    def test_schema_file_exists(self) -> bool:
        """Test that the schema file exists and is readable."""
        try:
            schema_path = self.schema_manager.schema_path
            return os.path.exists(schema_path) and os.path.isfile(schema_path)
        except Exception as e:
            logger.error(f"Error checking schema file existence: {e}")
            return False

    def test_schema_json_valid(self) -> bool:
        """Test that the schema file contains valid JSON."""
        try:
            with open(self.schema_manager.schema_path, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error reading schema file: {e}")
            return False

    def test_schema_structure(self) -> bool:
        """Test that the schema has the expected structure."""
        schema = self.schema_manager.schema
        if not schema:
            return False

        # Check for required top-level keys
        required_keys = ["$schema", "title", "oneOf"]
        for key in required_keys:
            if key not in schema:
                logger.error(f"Missing required schema key: {key}")
                return False

        # Check that oneOf is a list
        if not isinstance(schema["oneOf"], list):
            logger.error("Schema oneOf must be a list")
            return False

        return True

    def test_message_types_coverage(self) -> bool:
        """Test that all expected message types are defined in schema."""
        valid_types = set(get_valid_message_types())

        missing_types = self.expected_message_types - valid_types
        if missing_types:
            logger.error(f"Missing message types in schema: {missing_types}")
            return False

        extra_types = valid_types - self.expected_message_types
        if extra_types:
            logger.info(f"Additional message types in schema: {extra_types}")

        return True

    def test_message_validation(self) -> bool:
        """Test that schema validation works for known message types."""
        test_messages = [
            {
                "type": "start_record",
                "timestamp": 1234567890000,
                "session_id": "test_session",
            },
            {
                "type": "preview_frame",
                "timestamp": 1234567890000,
                "frame_id": 1,
                "image_data": "base64_data_here",
                "width": 640,
                "height": 480,
            },
            {
                "type": "device_status",
                "timestamp": 1234567890000,
                "device_id": "test_device",
                "status": "idle",
            },
        ]

        for message in test_messages:
            if not self.schema_manager.validate_message(message):
                logger.error(f"Valid message failed validation: {message}")
                return False

        return True

    def test_invalid_message_rejection(self) -> bool:
        """Test that invalid messages are properly rejected."""
        invalid_messages = [
            # Missing required fields
            {"type": "start_record", "timestamp": 1234567890000},  # Missing session_id
            {"timestamp": 1234567890000, "session_id": "test"},  # Missing type
            {"type": "start_record", "session_id": "test"},  # Missing timestamp
            # Invalid field types
            {"type": "start_record", "timestamp": "invalid", "session_id": "test"},
            {
                "type": "preview_frame",
                "timestamp": 1234567890000,
                "frame_id": "invalid",
                "image_data": "data",
                "width": 640,
                "height": 480,
            },
            # Unknown message type
            {"type": "unknown_type", "timestamp": 1234567890000},
        ]

        for message in invalid_messages:
            if self.schema_manager.validate_message(message):
                logger.error(f"Invalid message passed validation: {message}")
                return False

        return True


# Pytest test functions
@pytest.fixture
def config_tester():
    """Fixture providing a ConfigIntegrityTester instance."""
    return ConfigIntegrityTester()


@pytest.fixture
def schema_tester():
    """Fixture providing a SchemaIntegrityTester instance."""
    return SchemaIntegrityTester()


def test_config_file_exists(config_tester):
    """Test that configuration file exists."""
    assert config_tester.test_config_file_exists()


def test_config_json_valid(config_tester):
    """Test that configuration file contains valid JSON."""
    assert config_tester.test_config_json_valid()


def test_config_required_sections(config_tester):
    """Test that all required configuration sections exist."""
    assert config_tester.test_required_sections_exist()


def test_network_config_structure(config_tester):
    """Test network configuration structure."""
    assert config_tester.test_network_config_structure()


def test_devices_config_structure(config_tester):
    """Test devices configuration structure."""
    assert config_tester.test_devices_config_structure()


def test_calibration_config_structure(config_tester):
    """Test calibration configuration structure."""
    assert config_tester.test_calibration_config_structure()


def test_config_cross_validation(config_tester):
    """Test cross-validation between config sections."""
    assert config_tester.test_config_cross_validation()


def test_config_validation_function():
    """Test the global config validation function."""
    assert validate_config()


def test_schema_file_exists(schema_tester):
    """Test that schema file exists."""
    assert schema_tester.test_schema_file_exists()


def test_schema_json_valid(schema_tester):
    """Test that schema file contains valid JSON."""
    assert schema_tester.test_schema_json_valid()


def test_schema_structure(schema_tester):
    """Test schema file structure."""
    assert schema_tester.test_schema_structure()


def test_message_types_coverage(schema_tester):
    """Test that all expected message types are covered."""
    assert schema_tester.test_message_types_coverage()


def test_message_validation(schema_tester):
    """Test that valid messages pass validation."""
    assert schema_tester.test_message_validation()


def test_invalid_message_rejection(schema_tester):
    """Test that invalid messages are rejected."""
    assert schema_tester.test_invalid_message_rejection()


def test_message_creation():
    """Test message creation utilities."""
    # Test creating different message types
    start_msg = create_message("start_record", session_id="test_session")
    assert start_msg["type"] == "start_record"
    assert start_msg["session_id"] == "test_session"
    assert "timestamp" in start_msg

    preview_msg = create_message(
        "preview_frame", frame_id=1, image_data="test_data", width=640, height=480
    )
    assert preview_msg["type"] == "preview_frame"
    assert preview_msg["frame_id"] == 1
    assert preview_msg["width"] == 640
    assert preview_msg["height"] == 480


def test_config_schema_consistency():
    """Test consistency between config and schema."""
    # Test that calibration config matches schema expectations
    config_manager = get_config_manager()
    calibration_config = config_manager.get_calibration_config()

    # Create a calibration message using config values
    pattern_size = {
        "rows": calibration_config.get("pattern_rows", 7),
        "cols": calibration_config.get("pattern_cols", 6),
    }

    cal_msg = create_message(
        "calibration_start",
        pattern_type=calibration_config.get("pattern_type", "chessboard"),
        pattern_size=pattern_size,
    )

    # Message should validate against schema
    schema_manager = get_schema_manager()
    assert schema_manager.validate_message(cal_msg)


@pytest.mark.integration
def test_config_reload():
    """Test configuration reloading functionality."""
    config_manager = get_config_manager()

    # Get initial config
    initial_host = config_manager.get_host()

    # Reload config
    config_manager.reload_config()

    # Should still work
    reloaded_host = config_manager.get_host()
    assert reloaded_host == initial_host


@pytest.mark.integration
def test_schema_reload():
    """Test schema reloading functionality."""
    schema_manager = get_schema_manager()

    # Get initial message types
    initial_types = set(get_valid_message_types())

    # Reload schema
    schema_manager.reload_schema()

    # Should still work
    reloaded_types = set(get_valid_message_types())
    assert reloaded_types == initial_types


def test_config_convenience_functions():
    """Test configuration convenience functions."""
    from protocol import get_host, get_port, get_frame_rate, get_resolution

    # These should all return reasonable values
    host = get_host()
    assert isinstance(host, str)
    assert len(host) > 0

    port = get_port()
    assert isinstance(port, int)
    assert 1 <= port <= 65535

    frame_rate = get_frame_rate()
    assert isinstance(frame_rate, int)
    assert frame_rate > 0

    resolution = get_resolution()
    assert isinstance(resolution, tuple)
    assert len(resolution) == 2
    assert all(isinstance(x, int) and x > 0 for x in resolution)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run basic integrity tests
    print("Running configuration and schema integrity tests...")

    # Test configuration
    config_tester = ConfigIntegrityTester()
    config_tests = [
        ("Config file exists", config_tester.test_config_file_exists),
        ("Config JSON valid", config_tester.test_config_json_valid),
        ("Required sections exist", config_tester.test_required_sections_exist),
        ("Network config structure", config_tester.test_network_config_structure),
        ("Devices config structure", config_tester.test_devices_config_structure),
        (
            "Calibration config structure",
            config_tester.test_calibration_config_structure,
        ),
        ("Config cross-validation", config_tester.test_config_cross_validation),
    ]

    # Test schema
    schema_tester = SchemaIntegrityTester()
    schema_tests = [
        ("Schema file exists", schema_tester.test_schema_file_exists),
        ("Schema JSON valid", schema_tester.test_schema_json_valid),
        ("Schema structure", schema_tester.test_schema_structure),
        ("Message types coverage", schema_tester.test_message_types_coverage),
        ("Message validation", schema_tester.test_message_validation),
        ("Invalid message rejection", schema_tester.test_invalid_message_rejection),
    ]

    all_tests = config_tests + schema_tests
    passed = 0
    failed = 0

    for test_name, test_func in all_tests:
        try:
            if test_func():
                print(f"✓ {test_name}")
                passed += 1
            else:
                print(f"✗ {test_name}")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("All integrity tests passed!")
    else:
        print("Some tests failed. Check the logs for details.")

    exit(0 if failed == 0 else 1)
