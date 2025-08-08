"""
Shimmer module for device management and data collection.

This module breaks down the previously monolithic ShimmerManager into
focused, maintainable components.
"""

from .connection_handler import ShimmerConnectionHandler
from .data_processor import ShimmerDataProcessor
from .device_models import (
    ConnectionStatus,
    ConnectionType,
    DeviceConfiguration,
    DeviceState,
    DeviceStatus,
    ShimmerSample,
    ShimmerStatus,
)

__all__ = [
    "ShimmerConnectionHandler",
    "ShimmerDataProcessor",
    "ConnectionStatus",
    "ConnectionType",
    "DeviceConfiguration",
    "DeviceState",
    "DeviceStatus",
    "ShimmerSample",
    "ShimmerStatus",
]
