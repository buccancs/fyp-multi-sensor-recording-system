"""
Protocol utilities for the synchronized multimodal recording system.

This package provides unified protocol and configuration management for
communication between Python PC application and Android devices.

Modules:
    schema_utils: JSON schema validation and message utilities
    config_loader: Shared configuration loading and management
"""

from .schema_utils import (
    SchemaManager,
    get_schema_manager,
    validate_message,
    get_valid_message_types,
    create_message,
    create_command_message
)

from .config_loader import (
    ConfigManager,
    get_config_manager,
    get_config,
    get_network_config,
    get_devices_config,
    get_ui_config,
    get_calibration_config,
    get_host,
    get_port,
    get_frame_rate,
    get_resolution,
    get_preview_scale,
    get_calibration_pattern_size,
    get_calibration_error_threshold,
    reload_config,
    validate_config
)

__version__ = "1.0.0"
__all__ = [
    # Schema utilities
    "SchemaManager",
    "get_schema_manager", 
    "validate_message",
    "get_valid_message_types",
    "create_message",
    "create_command_message",
    
    # Configuration utilities
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "get_network_config",
    "get_devices_config", 
    "get_ui_config",
    "get_calibration_config",
    "get_host",
    "get_port",
    "get_frame_rate",
    "get_resolution",
    "get_preview_scale",
    "get_calibration_pattern_size",
    "get_calibration_error_threshold",
    "reload_config",
    "validate_config"
]
