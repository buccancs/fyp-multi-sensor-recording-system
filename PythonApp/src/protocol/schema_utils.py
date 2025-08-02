"""
Schema validation utilities for the synchronized multimodal recording system.

This module provides utilities for loading and validating JSON messages against
the unified protocol schema. It implements the schema-driven approach described
in Milestone 4 for ensuring consistent communication between Python and Android.
"""

import json
import os
import time
from typing import Dict, List, Any, Optional

# Import modern logging system
from utils.logging_config import get_logger

try:
    from jsonschema import ValidationError, Draft7Validator

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    # We'll log this warning after logger is initialized

logger = get_logger(__name__)

# Log warning after logger is initialized
if not JSONSCHEMA_AVAILABLE:
    logger.warning("jsonschema library not available. Using basic validation only.")


class SchemaManager:
    """Manages the unified JSON message schema for protocol validation."""

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the schema manager.

        Args:
            schema_path: Path to the message schema JSON file. If None, uses default path.
        """
        self.schema_path = schema_path or self._get_default_schema_path()
        self.schema: Optional[Dict[str, Any]] = None
        self.validator: Optional[Any] = None
        self._load_schema()

    def _get_default_schema_path(self) -> str:
        """Get the default path to the message schema file."""
        # Navigate from PythonApp/src/protocol to protocol/message_schema.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        return os.path.join(project_root, "protocol", "message_schema.json")

    def _load_schema(self) -> None:
        """Load the JSON schema from file."""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)

            if JSONSCHEMA_AVAILABLE:
                self.validator = Draft7Validator(self.schema)

            logger.info(f"Successfully loaded message schema from {self.schema_path}")

        except FileNotFoundError:
            logger.error(f"Schema file not found: {self.schema_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            raise

    def reload_schema(self) -> None:
        """Reload the schema from file (useful for development)."""
        self._load_schema()

    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate a message against the schema.

        Args:
            message: The message dictionary to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationError: If using jsonschema and validation fails
        """
        if not self.schema:
            logger.error("Schema not loaded")
            return False

        if not isinstance(message, dict):
            logger.error("Message must be a dictionary")
            return False

        # Basic validation - check for required type field
        if "type" not in message:
            logger.error("Message missing required 'type' field")
            return False

        if "timestamp" not in message:
            logger.error("Message missing required 'timestamp' field")
            return False

        # Use jsonschema if available for comprehensive validation
        if JSONSCHEMA_AVAILABLE and self.validator:
            try:
                self.validator.validate(message)
                return True
            except ValidationError as e:
                logger.error(f"Schema validation failed: {e.message}")
                return False
        else:
            # Basic validation without jsonschema
            return self._basic_validate(message)

    def _basic_validate(self, message: Dict[str, Any]) -> bool:
        """
        Basic validation without jsonschema library.

        Args:
            message: The message to validate

        Returns:
            True if basic validation passes
        """
        message_type = message.get("type")

        # Validate known message types
        if message_type == "start_record":
            return "session_id" in message
        elif message_type == "stop_record":
            return "session_id" in message
        elif message_type == "preview_frame":
            required_fields = ["frame_id", "image_data", "width", "height"]
            return all(field in message for field in required_fields)
        elif message_type == "file_chunk":
            required_fields = [
                "file_id",
                "chunk_index",
                "total_chunks",
                "chunk_data",
                "chunk_size",
                "file_type",
            ]
            return all(field in message for field in required_fields)
        elif message_type == "device_status":
            return "device_id" in message and "status" in message
        elif message_type == "ack":
            return "message_id" in message and "success" in message
        elif message_type == "calibration_start":
            return "pattern_type" in message and "pattern_size" in message
        elif message_type == "calibration_result":
            return "success" in message
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return True  # Allow unknown types for extensibility

    def get_valid_message_types(self) -> List[str]:
        """
        Get list of all valid message types from schema.

        Returns:
            List of valid message type strings
        """
        if not self.schema:
            return []

        message_types = []

        # Extract message types from oneOf schema structure
        if "oneOf" in self.schema:
            for message_def in self.schema["oneOf"]:
                if "allOf" in message_def:
                    for part in message_def["allOf"]:
                        if "properties" in part and "type" in part["properties"]:
                            type_def = part["properties"]["type"]
                            if "const" in type_def:
                                message_types.append(type_def["const"])

        return message_types

    def create_message(self, message_type: str, **kwargs) -> Dict[str, Any]:
        """
        Create a message with proper structure and timestamp.

        Args:
            message_type: The type of message to create
            **kwargs: Additional fields for the message

        Returns:
            Dictionary representing the message
        """
        message = {
            "type": message_type,
            "timestamp": int(time.time() * 1000),  # Unix timestamp in milliseconds
            **kwargs,
        }

        return message

    def get_message_template(self, message_type: str) -> Dict[str, Any]:
        """
        Get a template for a specific message type with required fields.

        Args:
            message_type: The message type to get template for

        Returns:
            Dictionary template with required fields
        """
        templates = {
            "start_record": {"type": "start_record", "timestamp": 0, "session_id": ""},
            "stop_record": {"type": "stop_record", "timestamp": 0, "session_id": ""},
            "preview_frame": {
                "type": "preview_frame",
                "timestamp": 0,
                "frame_id": 0,
                "image_data": "",
                "width": 0,
                "height": 0,
            },
            "file_chunk": {
                "type": "file_chunk",
                "timestamp": 0,
                "file_id": "",
                "chunk_index": 0,
                "total_chunks": 0,
                "chunk_data": "",
                "chunk_size": 0,
                "file_type": "video",
            },
            "device_status": {
                "type": "device_status",
                "timestamp": 0,
                "device_id": "",
                "status": "idle",
            },
            "ack": {"type": "ack", "timestamp": 0, "message_id": "", "success": True},
            "calibration_start": {
                "type": "calibration_start",
                "timestamp": 0,
                "pattern_type": "chessboard",
                "pattern_size": {"rows": 7, "cols": 6},
            },
            "calibration_result": {
                "type": "calibration_result",
                "timestamp": 0,
                "success": False,
            },
        }

        return templates.get(message_type, {"type": message_type, "timestamp": 0})


# Global schema manager instance
_schema_manager: Optional[SchemaManager] = None


def get_schema_manager() -> SchemaManager:
    """Get the global schema manager instance."""
    global _schema_manager
    if _schema_manager is None:
        _schema_manager = SchemaManager()
    return _schema_manager


def validate_message(message: Dict[str, Any]) -> bool:
    """
    Validate a message against the schema using the global schema manager.

    Args:
        message: The message to validate

    Returns:
        True if valid, False otherwise
    """
    return get_schema_manager().validate_message(message)


def get_valid_message_types() -> List[str]:
    """Get list of all valid message types."""
    return get_schema_manager().get_valid_message_types()


def create_message(message_type: str, **kwargs) -> Dict[str, Any]:
    """Create a properly formatted message."""
    return get_schema_manager().create_message(message_type, **kwargs)


def create_command_message(command_type: str, **kwargs) -> Dict[str, Any]:
    """
    Create a command message (backward compatibility with existing code).

    Args:
        command_type: The command type
        **kwargs: Additional message fields

    Returns:
        Formatted message dictionary
    """
    return create_message(command_type, **kwargs)
