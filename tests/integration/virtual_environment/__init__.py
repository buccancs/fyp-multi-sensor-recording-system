"""
Virtual Test Environment for GSR Recording System

This module provides a comprehensive virtual test environment that can simulate
multiple Android devices connecting to the PC controller, generating realistic
sensor data streams to test system performance, synchronization, and data handling
without requiring physical hardware.

Key components:
- VirtualDeviceClient: Simulates Android device connection and behavior
- SyntheticDataGenerator: Generates realistic sensor data streams
- TestRunner: Orchestrates multi-device test scenarios
- MetricsCollector: Monitors performance and validates system behavior
"""

__version__ = "1.0.0"
__author__ = "GSR Research Team"

from .virtual_device_client import VirtualDeviceClient, VirtualDeviceConfig
from .synthetic_data_generator import SyntheticDataGenerator
from .test_runner import VirtualTestRunner
from .test_config import VirtualTestConfig, VirtualTestScenario

__all__ = [
    "VirtualDeviceClient",
    "VirtualDeviceConfig", 
    "SyntheticDataGenerator", 
    "VirtualTestRunner",
    "VirtualTestConfig",
    "VirtualTestScenario",
]