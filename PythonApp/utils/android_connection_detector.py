"""
Android Connection Detector Module
==================================

Mock implementation for device connectivity testing.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    USB = "usb"
    WIRELESS_ADB = "wireless_adb"


@dataclass
class AndroidDevice:
    device_id: str
    status: str
    model: str = "Unknown"
    android_version: str = "Unknown"
    connection_type: ConnectionType = ConnectionType.USB
    ip_address: Optional[str] = None
    port: Optional[int] = None


class AndroidConnectionDetector:
    """Mock Android connection detector."""
    
    def __init__(self):
        self.adb_path = "/usr/bin/adb"  # Mock path
    
    def detect_all_connections(self) -> Dict[str, AndroidDevice]:
        """Mock device detection."""
        # Return empty dict - no devices in test environment
        return {}
    
    def get_wireless_debugging_devices(self) -> List[AndroidDevice]:
        """Mock wireless device detection."""
        return []
    
    def get_ide_connected_devices(self) -> Dict[str, dict]:
        """Mock IDE device detection."""
        return {}