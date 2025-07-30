"""
Configuration loading utilities for the synchronized multimodal recording system.

This module provides utilities for loading and managing the shared configuration
file. It implements the shared configuration approach described in Milestone 4
for ensuring consistent parameters between Python and Android platforms.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages the shared configuration for the recording system."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the config JSON file. If None, uses default path.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Optional[Dict[str, Any]] = None
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the default path to the configuration file."""
        # Navigate from PythonApp/src/protocol to protocol/config.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        return os.path.join(project_root, "protocol", "config.json")

    def _load_config(self) -> None:
        """Load the configuration from file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            logger.info(f"Successfully loaded configuration from {self.config_path}")

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def reload_config(self) -> None:
        """Reload the configuration from file (useful for development)."""
        self._load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.

        Args:
            key: Dot-separated key path (e.g., 'network.port')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self.config:
            return default

        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.

        Args:
            section: Section name (e.g., 'network', 'devices')

        Returns:
            Dictionary containing the section data
        """
        if not self.config:
            return {}

        return self.config.get(section, {})

    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration section."""
        return self.get_section("network")

    def get_devices_config(self) -> Dict[str, Any]:
        """Get devices configuration section."""
        return self.get_section("devices")

    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration section."""
        return self.get_section("UI")

    def get_calibration_config(self) -> Dict[str, Any]:
        """Get calibration configuration section."""
        return self.get_section("calibration")

    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration section."""
        return self.get_section("session")

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration section."""
        return self.get_section("logging")

    def get_testing_config(self) -> Dict[str, Any]:
        """Get testing configuration section."""
        return self.get_section("testing")

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration section."""
        return self.get_section("performance")

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration section."""
        return self.get_section("security")

    # Convenience methods for commonly used values
    def get_host(self) -> str:
        """Get network host."""
        return self.get("network.host", "0.0.0.0")

    def get_port(self) -> int:
        """Get network port."""
        return self.get("network.port", 9000)

    def get_timeout(self) -> int:
        """Get network timeout in seconds."""
        return self.get("network.timeout_seconds", 30)

    def get_frame_rate(self) -> int:
        """Get camera frame rate."""
        return self.get("devices.frame_rate", 30)

    def get_resolution(self) -> tuple:
        """Get camera resolution as (width, height)."""
        res = self.get("devices.resolution", {"width": 1920, "height": 1080})
        return (res["width"], res["height"])

    def get_preview_resolution(self) -> tuple:
        """Get preview resolution as (width, height)."""
        res = self.get("devices.preview_resolution", {"width": 640, "height": 480})
        return (res["width"], res["height"])

    def get_preview_scale(self) -> float:
        """Get UI preview scale factor."""
        return self.get("UI.preview_scale", 0.5)

    def get_calibration_pattern_size(self) -> tuple:
        """Get calibration pattern size as (rows, cols)."""
        rows = self.get("calibration.pattern_rows", 7)
        cols = self.get("calibration.pattern_cols", 6)
        return (rows, cols)

    def get_calibration_square_size(self) -> float:
        """Get calibration square size in meters."""
        return self.get("calibration.square_size_m", 0.0245)

    def get_calibration_error_threshold(self) -> float:
        """Get calibration error threshold in pixels."""
        return self.get("calibration.error_threshold", 1.0)

    def get_session_directory(self) -> str:
        """Get session recording directory."""
        return self.get("session.session_directory", "recordings")

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.get("logging.level", "INFO")

    def is_fake_device_enabled(self) -> bool:
        """Check if fake device mode is enabled for testing."""
        return self.get("testing.fake_device_enabled", False)

    def validate_config(self) -> bool:
        """
        Validate the configuration structure and values.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.config:
            logger.error("Configuration not loaded")
            return False

        required_sections = ["network", "devices", "UI", "calibration"]

        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                return False

        # Validate network section
        network = self.get_network_config()
        if not network.get("host") or not network.get("port"):
            logger.error("Network configuration missing host or port")
            return False

        # Validate devices section
        devices = self.get_devices_config()
        if devices.get("frame_rate", 0) <= 0:
            logger.error("Invalid frame rate in devices configuration")
            return False

        # Validate calibration section
        calibration = self.get_calibration_config()
        if (
            calibration.get("pattern_rows", 0) <= 0
            or calibration.get("pattern_cols", 0) <= 0
        ):
            logger.error("Invalid calibration pattern size")
            return False

        logger.info("Configuration validation passed")
        return True


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value using the global config manager."""
    return get_config_manager().get(key, default)


def get_network_config() -> Dict[str, Any]:
    """Get network configuration section."""
    return get_config_manager().get_network_config()


def get_devices_config() -> Dict[str, Any]:
    """Get devices configuration section."""
    return get_config_manager().get_devices_config()


def get_ui_config() -> Dict[str, Any]:
    """Get UI configuration section."""
    return get_config_manager().get_ui_config()


def get_calibration_config() -> Dict[str, Any]:
    """Get calibration configuration section."""
    return get_config_manager().get_calibration_config()


# Convenience functions for commonly used values
def get_host() -> str:
    """Get network host."""
    return get_config_manager().get_host()


def get_port() -> int:
    """Get network port."""
    return get_config_manager().get_port()


def get_frame_rate() -> int:
    """Get camera frame rate."""
    return get_config_manager().get_frame_rate()


def get_resolution() -> tuple:
    """Get camera resolution."""
    return get_config_manager().get_resolution()


def get_preview_scale() -> float:
    """Get preview scale factor."""
    return get_config_manager().get_preview_scale()


def get_calibration_pattern_size() -> tuple:
    """Get calibration pattern size."""
    return get_config_manager().get_calibration_pattern_size()


def get_calibration_error_threshold() -> float:
    """Get calibration error threshold."""
    return get_config_manager().get_calibration_error_threshold()


def reload_config() -> None:
    """Reload the configuration from file."""
    get_config_manager().reload_config()


def validate_config() -> bool:
    """Validate the current configuration."""
    return get_config_manager().validate_config()
