#!/usr/bin/env python3
"""
Realistic Fake Data Generator for Multi-Sensor Recording System UI
Provides convincing device data, sensor readings, and system information for demos.

This module generates realistic data to make the application appear fully functional
during demonstrations and screenshots, including:
- Device information and status
- System monitoring data  
- Session data and recordings
- Calibration results
- Log entries
"""

import random
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """Information about a connected device"""
    device_id: str
    device_name: str
    device_type: str
    status: str
    battery_level: float
    storage_available: float
    storage_total: float
    temperature: float
    connection_quality: str
    last_seen: datetime


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_activity: float
    temperature: float


class RealisticFakeDataGenerator:
    """Generates realistic fake data for UI demonstration"""
    
    def __init__(self):
        """Initialize the fake data generator"""
        self.devices = []
        self.system_start_time = datetime.now()
        self.session_counter = 0
        self.last_metrics_update = time.time()
        
        # Initialize with realistic devices
        self._create_fake_devices()
        
    def _create_fake_devices(self):
        """Create a set of realistic fake devices"""
        device_configs = [
            {
                "device_id": "thermal_cam_001",
                "device_name": "FLIR Lepton 3.5",
                "device_type": "thermal_camera",
                "base_temp": 22.5,
                "battery_range": (75, 95),
                "storage_total": 64000,  # 64GB
            },
            {
                "device_id": "rgb_cam_001", 
                "device_name": "Logitech C920 HD",
                "device_type": "rgb_camera",
                "base_temp": 28.0,
                "battery_range": (80, 100),
                "storage_total": 128000,  # 128GB
            },
            {
                "device_id": "android_dev_001",
                "device_name": "Samsung Galaxy S21",
                "device_type": "android_phone",
                "base_temp": 31.2,
                "battery_range": (45, 85),
                "storage_total": 256000,  # 256GB
            },
            {
                "device_id": "imu_sensor_001",
                "device_name": "Shimmer3 IMU",
                "device_type": "imu_sensor", 
                "base_temp": 25.8,
                "battery_range": (60, 90),
                "storage_total": 32000,  # 32GB
            },
            {
                "device_id": "pc_webcam_001",
                "device_name": "Integrated Webcam",
                "device_type": "pc_webcam",
                "base_temp": 35.5,
                "battery_range": (100, 100),  # Always powered
                "storage_total": 500000,  # 500GB (PC storage)
            }
        ]
        
        for config in device_configs:
            device = DeviceInfo(
                device_id=config["device_id"],
                device_name=config["device_name"],
                device_type=config["device_type"],
                status=random.choice(["connected", "recording", "idle"]),
                battery_level=random.uniform(*config["battery_range"]),
                storage_available=random.uniform(
                    config["storage_total"] * 0.3,
                    config["storage_total"] * 0.8
                ),
                storage_total=config["storage_total"],
                temperature=config["base_temp"] + random.uniform(-2, 3),
                connection_quality=random.choice(["excellent", "good", "fair"]),
                last_seen=datetime.now() - timedelta(seconds=random.randint(0, 300))
            )
            self.devices.append(device)
    
    def get_device_list(self) -> List[DeviceInfo]:
        """Get list of fake devices with current status"""
        # Randomly update device status to simulate dynamic system
        for device in self.devices:
            if random.random() < 0.1:  # 10% chance to update each call
                self._update_device_status(device)
        
        return self.devices
    
    def _update_device_status(self, device: DeviceInfo):
        """Update device status with realistic changes"""
        # Battery drain during recording
        if device.status == "recording":
            device.battery_level = max(0, device.battery_level - random.uniform(0.1, 0.5))
            device.storage_available = max(0, device.storage_available - random.uniform(10, 50))
        
        # Slight temperature variations
        device.temperature += random.uniform(-0.5, 0.5)
        
        # Occasional status changes
        if random.random() < 0.05:
            if device.status == "idle":
                device.status = "connected" if random.random() < 0.7 else "recording"
            elif device.status == "connected":
                device.status = "idle" if random.random() < 0.8 else "recording"
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get realistic system performance metrics"""
        now = time.time()
        
        # Create realistic CPU usage (higher during recording)
        base_cpu = 15 if not self._is_recording() else 45
        cpu_variation = random.uniform(-10, 15)
        cpu_usage = max(5, min(95, base_cpu + cpu_variation))
        
        # Memory usage that slowly increases over time
        runtime_minutes = (now - self.last_metrics_update) / 60
        base_memory = 35 + runtime_minutes * 0.5  # Slight memory leak simulation
        memory_variation = random.uniform(-5, 10)
        memory_usage = max(20, min(85, base_memory + memory_variation))
        
        # Disk usage (slowly increases with recordings)
        disk_usage = 45 + random.uniform(-3, 8)
        
        # Network activity (higher during device communication)
        network_activity = random.uniform(5, 25) if self._has_connected_devices() else random.uniform(0, 5)
        
        # System temperature
        system_temp = 42 + random.uniform(-5, 12)
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_activity=network_activity,
            temperature=system_temp
        )
    
    def _is_recording(self) -> bool:
        """Check if any device is currently recording"""
        return any(device.status == "recording" for device in self.devices)
    
    def _has_connected_devices(self) -> bool:
        """Check if there are connected devices"""
        return any(device.status in ["connected", "recording"] for device in self.devices)
    
    def get_realistic_log_entries(self, count: int = 10) -> List[str]:
        """Generate realistic log entries"""
        log_templates = [
            "Device {device} connected successfully",
            "Thermal calibration completed for {device} (RMS error: {error:.3f})",
            "Recording session started with {count} active devices",
            "Frame synchronization achieved across all devices",
            "Storage usage warning: {device} at {percent}% capacity",
            "Network latency measured: {latency}ms to {device}",
            "Auto-save completed: session_{session_id}",
            "Device {device} battery level: {battery}%",
            "Quality check passed for {device} video stream",
            "Background process optimization completed",
            "Memory usage stabilized at {memory}%",
            "Thermal sensor calibration drift detected: {drift}°C",
            "File transfer completed: {filename} ({size} MB)",
            "System performance: CPU {cpu}%, Memory {memory}%",
            "Device discovery scan completed: {count} devices found"
        ]
        
        logs = []
        for i in range(count):
            template = random.choice(log_templates)
            device = random.choice(self.devices)
            
            # Generate realistic values for placeholders
            log_entry = template.format(
                device=device.device_name,
                error=random.uniform(0.1, 0.8),
                count=len([d for d in self.devices if d.status != "idle"]),
                percent=int(random.uniform(75, 95)),
                latency=random.randint(12, 85),
                session_id=f"2025{random.randint(1000, 9999)}",
                battery=int(device.battery_level),
                memory=random.randint(30, 75),
                drift=random.uniform(0.1, 2.5),
                filename=f"{device.device_id}_{random.randint(1000, 9999)}.mp4",
                size=random.uniform(15, 250),
                cpu=random.randint(20, 65)
            )
            
            # Add timestamp
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 30))
            logs.append(f"[{timestamp.strftime('%H:%M:%S')}] {log_entry}")
        
        return logs
    
    def get_session_data(self) -> Dict[str, Any]:
        """Generate realistic session/recording data"""
        session_id = f"session_2025_{random.randint(1000, 9999)}"
        
        return {
            "session_id": session_id,
            "start_time": (datetime.now() - timedelta(minutes=random.randint(5, 45))).isoformat(),
            "duration": random.uniform(30, 300),  # 30 seconds to 5 minutes
            "status": random.choice(["recording", "completed", "processing"]),
            "device_count": len([d for d in self.devices if d.status != "idle"]),
            "total_frames": random.randint(900, 15000),
            "file_size_mb": random.uniform(25, 500),
            "quality_score": random.uniform(0.85, 0.98),
            "sync_accuracy": random.uniform(0.92, 0.999)
        }
    
    def get_calibration_data(self) -> Dict[str, Any]:
        """Generate realistic calibration results"""
        return {
            "calibration_id": f"cal_{int(time.time())}",
            "device_id": random.choice(self.devices).device_id,
            "timestamp": datetime.now().isoformat(),
            "rms_error": random.uniform(0.15, 0.75),
            "successful": True,
            "camera_matrix": [
                [random.uniform(780, 820), 0, random.uniform(310, 330)],
                [0, random.uniform(780, 820), random.uniform(230, 250)], 
                [0, 0, 1]
            ],
            "distortion_coefficients": [
                random.uniform(-0.3, 0.3) for _ in range(5)
            ],
            "reprojection_error": random.uniform(0.1, 0.6),
            "calibration_flags": ["CALIB_FIX_PRINCIPAL_POINT", "CALIB_ZERO_TANGENT_DIST"]
        }
    
    def create_realistic_session_files(self, recordings_dir: str, count: int = 5):
        """Create realistic session directories and files"""
        os.makedirs(recordings_dir, exist_ok=True)
        
        for i in range(count):
            # Generate session info
            session_date = datetime.now() - timedelta(days=random.randint(0, 30))
            session_id = session_date.strftime("session_%Y_%m_%d_%H_%M_%S")
            session_path = os.path.join(recordings_dir, session_id)
            os.makedirs(session_path, exist_ok=True)
            
            # Create realistic session info
            duration = random.uniform(45, 600)  # 45 seconds to 10 minutes
            active_devices = random.sample(self.devices, random.randint(2, len(self.devices)))
            
            files = []
            for device in active_devices:
                # Generate multiple file types per device
                file_types = ["video", "thermal", "imu_data"]
                for file_type in file_types:
                    if random.random() < 0.7:  # 70% chance for each file type
                        filename = f"{device.device_id}_{file_type}.mp4"
                        file_size = random.randint(5242880, 104857600)  # 5MB to 100MB
                        files.append({
                            "filename": filename,
                            "file_type": file_type,
                            "file_size": file_size,
                            "device_id": device.device_id,
                            "duration": duration,
                            "frame_rate": random.choice([30, 60, 120]),
                            "resolution": random.choice(["1920x1080", "1280x720", "640x480"])
                        })
                        
                        # Create actual file (small placeholder)
                        file_path = os.path.join(session_path, filename)
                        with open(file_path, 'wb') as f:
                            f.write(b'0' * min(1024 * 100, file_size))  # Max 100KB for demo
            
            session_info = {
                "session_id": session_id,
                "start_time": session_date.isoformat(),
                "end_time": (session_date + timedelta(seconds=duration)).isoformat(),
                "duration": duration,
                "status": "completed",
                "devices": [
                    {
                        "id": device.device_id,
                        "name": device.device_name,
                        "type": device.device_type,
                        "status": "completed"
                    } for device in active_devices
                ],
                "files": files,
                "quality_metrics": {
                    "sync_accuracy": random.uniform(0.95, 0.999),
                    "frame_drops": random.randint(0, 5),
                    "average_latency": random.uniform(15, 45),
                    "storage_efficiency": random.uniform(0.85, 0.98)
                },
                "calibration_applied": random.choice([True, False]),
                "notes": f"Recording session with {len(active_devices)} devices"
            }
            
            # Save session info
            with open(os.path.join(session_path, 'session_info.json'), 'w') as f:
                json.dump(session_info, f, indent=2)
        
        print(f"Created {count} realistic session directories in {recordings_dir}")


# Global instance for easy access
_fake_data_generator = None

def get_fake_data_generator() -> RealisticFakeDataGenerator:
    """Get the global fake data generator instance"""
    global _fake_data_generator
    if _fake_data_generator is None:
        _fake_data_generator = RealisticFakeDataGenerator()
    return _fake_data_generator


def generate_realistic_device_status_text() -> str:
    """Generate device status text for display"""
    generator = get_fake_data_generator()
    devices = generator.get_device_list()
    
    status_lines = []
    for device in devices:
        storage_pct = (device.storage_available / device.storage_total) * 100
        status_lines.append(
            f"🔗 {device.device_name} | "
            f"Battery: {device.battery_level:.0f}% | "
            f"Storage: {storage_pct:.0f}% | "
            f"Temp: {device.temperature:.1f}°C | "
            f"Status: {device.status.title()}"
        )
    
    return "\n".join(status_lines)


if __name__ == "__main__":
    # Demo the fake data generator
    generator = RealisticFakeDataGenerator()
    
    print("=== Fake Device Data ===")
    for device in generator.get_device_list():
        print(f"{device.device_name}: {device.status}, Battery: {device.battery_level:.1f}%")
    
    print("\n=== System Metrics ===")
    metrics = generator.get_system_metrics()
    print(f"CPU: {metrics.cpu_usage:.1f}%, Memory: {metrics.memory_usage:.1f}%")
    
    print("\n=== Log Entries ===")
    for log in generator.get_realistic_log_entries(5):
        print(log)
    
    print("\n=== Session Data ===")
    session = generator.get_session_data()
    print(f"Session: {session['session_id']}, Duration: {session['duration']:.1f}s")