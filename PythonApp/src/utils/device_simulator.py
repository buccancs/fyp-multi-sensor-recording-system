#!/usr/bin/env python3
"""
Device Simulator for Multi-Sensor Recording System
Provides realistic fake device data for demonstration and thesis documentation.

This module generates believable device configurations and sensor data
that would be typical in a psychophysiology research environment.

Author: Multi-Sensor Recording System Team
Date: 2025-08-04
Purpose: Thesis Documentation with Realistic Devices
"""

import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Types of devices in the system"""
    SHIMMER_GSR = "shimmer_gsr"
    SHIMMER_ECG = "shimmer_ecg"
    ANDROID_PHONE = "android_phone"
    ANDROID_TABLET = "android_tablet"
    USB_WEBCAM = "usb_webcam"
    NETWORK_CAMERA = "network_camera"


@dataclass
class FakeDevice:
    """Realistic fake device configuration"""
    device_id: str
    device_type: DeviceType
    name: str
    mac_address: Optional[str]
    ip_address: Optional[str]
    battery_level: Optional[int]
    signal_quality: str
    is_connected: bool
    is_recording: bool
    firmware_version: str
    last_seen: datetime
    sensor_capabilities: List[str]
    sampling_rate: Optional[int] = None
    data_samples_count: int = 0


class DeviceSimulator:
    """
    Generates realistic fake devices for demonstration purposes.
    
    Creates believable configurations for Shimmer sensors, Android devices,
    and webcams that would be typical in a research laboratory setting.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize device simulator with optional seed for reproducible results"""
        random.seed(seed)
        self.devices = {}
        self.session_start_time = datetime.now() - timedelta(minutes=15)
        
    def get_fake_shimmer_devices(self) -> List[FakeDevice]:
        """Generate realistic Shimmer sensor devices"""
        shimmer_devices = [
            FakeDevice(
                device_id="shimmer_001",
                device_type=DeviceType.SHIMMER_GSR,
                name="Shimmer3 GSR Unit #1",
                mac_address="00:06:66:7A:12:34",
                ip_address=None,
                battery_level=82,
                signal_quality="Excellent",
                is_connected=True,
                is_recording=True,
                firmware_version="BoilerPlate 0.11.2",
                last_seen=datetime.now() - timedelta(seconds=2),
                sensor_capabilities=["GSR", "PPG_A13", "Internal ADC A12", "Internal ADC A13"],
                sampling_rate=128,
                data_samples_count=15680
            )
        ]
        return shimmer_devices
    
    def get_fake_android_devices(self) -> List[FakeDevice]:
        """Generate realistic Android devices"""
        android_devices = [
            FakeDevice(
                device_id="android_001",
                device_type=DeviceType.ANDROID_PHONE,
                name="Samsung Galaxy S22 (Participant 1)",
                mac_address="AC:37:43:77:89:AB",
                ip_address="192.168.1.101",
                battery_level=74,
                signal_quality="Excellent",
                is_connected=True,
                is_recording=True,
                firmware_version="Android 14, App v2.4.1",
                last_seen=datetime.now() - timedelta(seconds=3),
                sensor_capabilities=["Front Camera", "Rear Camera", "Accelerometer", "Gyroscope", "Magnetometer", "Light Sensor"],
                data_samples_count=9240
            ),
            FakeDevice(
                device_id="android_002",
                device_type=DeviceType.ANDROID_PHONE,
                name="Samsung Galaxy S22 (Participant 2)",
                mac_address="14:7D:DA:A1:23:45",
                ip_address="192.168.1.102", 
                battery_level=89,
                signal_quality="Good",
                is_connected=True,
                is_recording=False,
                firmware_version="Android 14, App v2.4.1",
                last_seen=datetime.now() - timedelta(seconds=1),
                sensor_capabilities=["Front Camera", "Rear Camera", "Accelerometer", "Gyroscope", "Magnetometer", "Light Sensor"],
                data_samples_count=0
            )
        ]
        return android_devices
    
    def get_fake_webcam_devices(self) -> List[FakeDevice]:
        """Generate realistic webcam devices"""
        webcam_devices = [
            FakeDevice(
                device_id="webcam_001",
                device_type=DeviceType.USB_WEBCAM,
                name="Logitech Brio 4K (Facial)",
                mac_address=None,
                ip_address=None,
                battery_level=None,
                signal_quality="Excellent",
                is_connected=True,
                is_recording=True,
                firmware_version="USB 3.0, 3840x2160@30fps",
                last_seen=datetime.now() - timedelta(seconds=1),
                sensor_capabilities=["4K Video Recording", "HDR", "Auto Focus", "Face Detection"],
                data_samples_count=27000  # 30fps * 15min * 60s
            ),
            FakeDevice(
                device_id="webcam_002", 
                device_type=DeviceType.USB_WEBCAM,
                name="Logitech Brio 4K (Overview)",
                mac_address=None,
                ip_address=None,
                battery_level=None,
                signal_quality="Good",
                is_connected=True,
                is_recording=True,
                firmware_version="USB 3.0, 1920x1080@60fps",
                last_seen=datetime.now() - timedelta(seconds=2),
                sensor_capabilities=["4K Video Recording", "HDR", "Auto Focus", "Wide Field of View"],
                data_samples_count=54000  # 60fps * 15min * 60s
            )
        ]
        return webcam_devices
    
    def get_all_fake_devices(self) -> Dict[str, List[FakeDevice]]:
        """Get all fake devices organized by type"""
        return {
            "shimmer_devices": self.get_fake_shimmer_devices(),
            "android_devices": self.get_fake_android_devices(), 
            "webcam_devices": self.get_fake_webcam_devices()
        }
    
    def get_fake_session_data(self) -> Dict[str, Any]:
        """Generate realistic session data"""
        return {
            "current_session": {
                "session_id": "PSYC_2025_P001_S003",
                "participant_id": "P001",
                "start_time": self.session_start_time.isoformat(),
                "duration_minutes": 15.3,
                "status": "Recording",
                "data_quality": "Excellent",
                "devices_active": 4,  # 1 Shimmer + 2 Samsung + 1 active Brio
                "total_samples": 105920  # Updated based on new device counts
            },
            "recent_sessions": [
                {
                    "session_id": "PSYC_2025_P001_S002",
                    "participant_id": "P001", 
                    "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "duration_minutes": 22.7,
                    "status": "Completed",
                    "data_quality": "Good",
                    "file_size_mb": 145.2
                },
                {
                    "session_id": "PSYC_2025_P001_S001",
                    "participant_id": "P001",
                    "start_time": (datetime.now() - timedelta(days=1)).isoformat(), 
                    "duration_minutes": 18.1,
                    "status": "Completed",
                    "data_quality": "Excellent",
                    "file_size_mb": 98.7
                },
                {
                    "session_id": "PSYC_2025_P000_CALIB",
                    "participant_id": "P000",
                    "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
                    "duration_minutes": 5.0,
                    "status": "Calibration",
                    "data_quality": "Excellent", 
                    "file_size_mb": 12.3
                }
            ]
        }
    
    def get_fake_system_status(self) -> Dict[str, Any]:
        """Generate realistic system status data"""
        return {
            "system_info": {
                "version": "3.1.1 Enhanced",
                "uptime_hours": 4.2,
                "cpu_usage": 12.5,
                "memory_usage": 34.7,
                "disk_free_gb": 847.2,
                "network_status": "Connected"
            },
            "recording_stats": {
                "total_sessions_today": 12,
                "total_data_collected_mb": 2847.5,
                "average_session_duration": 16.8,
                "data_quality_average": 92.3
            }
        }
    
    def simulate_real_time_data(self, device_id: str) -> Dict[str, Any]:
        """Generate realistic real-time sensor data for a device"""
        now = time.time()
        
        if "shimmer" in device_id:
            if "gsr" in device_id.lower():
                return {
                    "timestamp": now,
                    "device_id": device_id,
                    "gsr_conductance": round(random.uniform(2.5, 8.2), 3),
                    "ppg_a13": round(random.uniform(1800, 2200), 1),
                    "accel_x": round(random.uniform(-0.5, 0.5), 3),
                    "accel_y": round(random.uniform(-0.5, 0.5), 3),
                    "accel_z": round(random.uniform(0.8, 1.2), 3)
                }
            else:  # ECG device
                return {
                    "timestamp": now,
                    "device_id": device_id,
                    "ecg_ra_ll": round(random.uniform(-1.5, 1.5), 3),
                    "ecg_la_ll": round(random.uniform(-1.2, 1.2), 3),
                    "heart_rate": random.randint(65, 85),
                    "gyro_x": round(random.uniform(-5, 5), 2),
                    "gyro_y": round(random.uniform(-5, 5), 2),
                    "gyro_z": round(random.uniform(-5, 5), 2)
                }
        
        return {
            "timestamp": now,
            "device_id": device_id,
            "status": "active",
            "data_rate": random.uniform(28, 32)
        }


# Create global simulator instance
_device_simulator = DeviceSimulator()

def get_device_simulator() -> DeviceSimulator:
    """Get the global device simulator instance"""
    return _device_simulator