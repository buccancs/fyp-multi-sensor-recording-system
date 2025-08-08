"""
Data models and enums for Shimmer device management.

This module contains all the data structures that were previously embedded
in the shimmer_manager.py file.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ConnectionType(Enum):
    """Types of connections supported for Shimmer devices."""

    DIRECT_BLUETOOTH = "direct_bluetooth"
    ANDROID_MEDIATED = "android_mediated"
    SIMULATION = "simulation"


class DeviceState(Enum):
    """Current state of a Shimmer device."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"


class ConnectionStatus(Enum):
    """Connection status for device tracking."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ShimmerStatus:
    """
    Current status of a Shimmer device.

    This dataclass contains all the state information for a Shimmer device
    including connection status, streaming state, and device capabilities.
    """

    is_available: bool = False
    is_connected: bool = False
    is_recording: bool = False
    is_streaming: bool = False
    connection_type: ConnectionType = ConnectionType.SIMULATION
    device_state: DeviceState = DeviceState.DISCONNECTED
    sampling_rate: int = 0
    enabled_channels: Set[str] = None
    device_name: Optional[str] = None
    mac_address: Optional[str] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[int] = None
    signal_quality: Optional[str] = None
    samples_recorded: int = 0
    last_data_timestamp: Optional[float] = None
    android_device_id: Optional[str] = None
    last_error: Optional[str] = None
    connection_attempts: int = 0

    def __post_init__(self):
        """Initialize enabled_channels if None."""
        if self.enabled_channels is None:
            self.enabled_channels = set()


@dataclass
class ShimmerSample:
    """
    A single data sample from a Shimmer device.

    Contains all possible sensor readings and metadata for a single
    timestamp from a Shimmer device.
    """

    timestamp: float
    system_time: str
    device_id: str
    connection_type: ConnectionType = ConnectionType.SIMULATION
    android_device_id: Optional[str] = None
    gsr_conductance: Optional[float] = None
    ppg_a13: Optional[float] = None
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    mag_x: Optional[float] = None
    mag_y: Optional[float] = None
    mag_z: Optional[float] = None
    ecg: Optional[float] = None
    emg: Optional[float] = None
    battery_percentage: Optional[int] = None
    signal_strength: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass
class DeviceConfiguration:
    """
    Configuration settings for a Shimmer device.

    Defines how a device should be configured for data collection
    including enabled sensors and sampling parameters.
    """

    device_id: str
    mac_address: str
    enabled_channels: Set[str]
    connection_type: ConnectionType = ConnectionType.SIMULATION
    sampling_rate: int = 128
    android_device_id: Optional[str] = None
    auto_reconnect: bool = True
    data_validation: bool = True
    buffer_size: int = 1000


@dataclass
class DeviceStatus:
    """
    Status tracking for device management.

    Used for monitoring device health and connection state over time.
    """

    device_id: str
    mac_address: str
    connection_status: ConnectionStatus
    connection_type: ConnectionType
    last_seen: datetime
    is_streaming: bool = False
    samples_count: int = 0
    last_error: Optional[str] = None
