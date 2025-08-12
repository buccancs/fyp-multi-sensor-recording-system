"""
Hardware-in-the-Loop Testing Utilities
======================================

Provides utility functions for hardware detection, configuration,
and test management for physical devices in the testing environment.

Features:
- Hardware device discovery and enumeration
- Test configuration for different hardware setups
- Hardware health monitoring during tests
- Test data validation for real sensor readings
"""

import os
import sys
import time
import threading
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Hardware interface imports
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    serial = None

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    bluetooth = None

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    usb = None


@dataclass
class HardwareConfig:
    """Configuration for hardware testing environments."""
    use_real_hardware: bool = False
    shimmer_timeout: float = 5.0
    thermal_timeout: float = 5.0
    mock_data_quality: str = "good"  # good, fair, poor
    enable_stress_testing: bool = True
    max_connection_retries: int = 3


@dataclass
class HardwareStatus:
    """Status information for hardware devices."""
    device_type: str
    device_id: str
    connected: bool
    last_seen: datetime
    error_count: int = 0
    data_quality: str = "unknown"


@dataclass
class DeviceInfo:
    """Information about detected hardware devices."""
    device_id: str
    device_type: str
    name: str
    address: str  # Bluetooth address or USB path
    capabilities: List[str]
    status: str = "detected"


def detect_shimmer_devices(timeout: float = 5.0) -> List[Dict[str, Any]]:
    """
    Detect available Shimmer sensor devices.
    
    Args:
        timeout: Maximum time to spend scanning
        
    Returns:
        List of device information dictionaries
    """
    devices = []
    
    if not BLUETOOTH_AVAILABLE:
        logger.warning("Bluetooth not available for Shimmer detection")
        return devices
        
    try:
        # Scan for Bluetooth devices
        logger.info(f"Scanning for Shimmer devices (timeout: {timeout}s)")
        
        if bluetooth:
            # Perform Bluetooth device discovery
            nearby_devices = bluetooth.discover_devices(
                duration=int(timeout), 
                lookup_names=True,
                flush_cache=True
            )
            
            for addr, name in nearby_devices:
                # Check if device appears to be a Shimmer
                if name and ('shimmer' in name.lower() or 'gsr' in name.lower()):
                    device_info = {
                        'address': addr,
                        'name': name,
                        'device_type': 'shimmer_gsr',
                        'capabilities': ['gsr', 'bluetooth'],
                        'status': 'detected'
                    }
                    devices.append(device_info)
                    logger.info(f"Found Shimmer device: {name} ({addr})")
                    
    except Exception as e:
        logger.error(f"Error during Shimmer device discovery: {e}")
        
    logger.info(f"Shimmer device scan complete: {len(devices)} devices found")
    return devices


def detect_thermal_cameras(timeout: float = 5.0) -> List[Dict[str, Any]]:
    """
    Detect available thermal camera devices.
    
    Args:
        timeout: Maximum time to spend scanning
        
    Returns:
        List of camera information dictionaries
    """
    cameras = []
    
    if not USB_AVAILABLE:
        logger.warning("USB not available for thermal camera detection")
        return cameras
        
    try:
        logger.info(f"Scanning for thermal cameras (timeout: {timeout}s)")
        
        # Scan USB devices
        devices = usb.core.find(find_all=True)
        
        for device in devices:
            try:
                # Check if device might be a thermal camera
                # Common thermal camera vendor IDs
                thermal_vendors = [
                    0x045e,  # Microsoft (some thermal cameras)
                    0x1e4e,  # Topdon
                    0x0547,  # Anchor Chips
                    0x1a86,  # QinHeng Electronics
                ]
                
                if device.idVendor in thermal_vendors:
                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "Unknown"
                        product = usb.util.get_string(device, device.iProduct) if device.iProduct else "Unknown"
                    except:
                        manufacturer = "Unknown"
                        product = "Unknown"
                        
                    camera_info = {
                        'device_id': f"USB_{device.idVendor:04x}:{device.idProduct:04x}",
                        'name': f"{manufacturer} {product}",
                        'device_type': 'thermal_camera',
                        'vendor_id': device.idVendor,
                        'product_id': device.idProduct,
                        'capabilities': ['thermal', 'usb', 'video'],
                        'resolution': (160, 120),  # Default thermal resolution
                        'status': 'detected'
                    }
                    cameras.append(camera_info)
                    logger.info(f"Found thermal camera: {manufacturer} {product}")
                    
            except Exception as e:
                logger.debug(f"Error checking USB device: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error during thermal camera discovery: {e}")
        
    logger.info(f"Thermal camera scan complete: {len(cameras)} cameras found")
    return cameras


def detect_all_hardware(timeout: float = 10.0) -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect all available hardware devices.
    
    Args:
        timeout: Maximum time to spend scanning
        
    Returns:
        Dictionary with device types as keys and device lists as values
    """
    logger.info("Starting comprehensive hardware detection")
    
    hardware = {
        'shimmer_devices': [],
        'thermal_cameras': [],
        'other_devices': []
    }
    
    # Split timeout between device types
    per_type_timeout = timeout / 2
    
    try:
        # Detect Shimmer sensors
        hardware['shimmer_devices'] = detect_shimmer_devices(per_type_timeout)
        
        # Detect thermal cameras
        hardware['thermal_cameras'] = detect_thermal_cameras(per_type_timeout)
        
        total_devices = sum(len(devices) for devices in hardware.values())
        logger.info(f"Hardware detection complete: {total_devices} devices found")
        
    except Exception as e:
        logger.error(f"Error during hardware detection: {e}")
        
    return hardware


def validate_gsr_data(data: Any) -> bool:
    """
    Validate GSR sensor data quality and format.
    
    Args:
        data: GSR data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    try:
        if hasattr(data, 'resistance'):
            # Check resistance value is reasonable
            if not (10.0 <= data.resistance <= 1000.0):  # kOhms
                return False
                
        if hasattr(data, 'conductance'):
            # Check conductance value is reasonable
            if not (1.0 <= data.conductance <= 100.0):  # μS
                return False
                
        if hasattr(data, 'timestamp'):
            # Check timestamp is recent
            current_time = time.time()
            if abs(current_time - data.timestamp) > 60.0:  # More than 1 minute old
                return False
                
        if hasattr(data, 'quality'):
            # Check quality indicator
            if data.quality not in ['good', 'fair', 'poor']:
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error validating GSR data: {e}")
        return False


def validate_thermal_frame(frame: Any) -> bool:
    """
    Validate thermal camera frame data quality and format.
    
    Args:
        frame: Thermal frame data to validate
        
    Returns:
        True if frame is valid, False otherwise
    """
    try:
        if not hasattr(frame, 'temperature_data'):
            return False
            
        if not hasattr(frame, 'timestamp'):
            return False
            
        temp_data = frame.temperature_data
        
        # Check data shape and type
        if not isinstance(temp_data, np.ndarray):
            return False
            
        if len(temp_data.shape) != 2:  # Should be 2D array
            return False
            
        # Check temperature ranges are reasonable
        if hasattr(frame, 'min_temp') and hasattr(frame, 'max_temp'):
            if not (-50.0 <= frame.min_temp <= frame.max_temp <= 200.0):
                return False
                
        # Check for invalid values
        if np.any(np.isnan(temp_data)) or np.any(np.isinf(temp_data)):
            return False
            
        # Check timestamp is recent
        current_time = time.time()
        if abs(current_time - frame.timestamp) > 60.0:  # More than 1 minute old
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating thermal frame: {e}")
        return False


def create_mock_environment() -> Dict[str, Any]:
    """
    Create a mock hardware environment for testing.
    
    Returns:
        Dictionary with mock device configurations
    """
    mock_env = {
        'shimmer_devices': [
            {
                'device_id': '00:06:66:66:66:66',
                'name': 'MockShimmer3',
                'device_type': 'shimmer_gsr',
                'capabilities': ['gsr', 'bluetooth'],
                'status': 'mock',
                'sample_rate': 128,
                'battery_level': 85
            }
        ],
        'thermal_cameras': [
            {
                'device_id': 'MockThermal_001',
                'name': 'Mock Thermal Camera',
                'device_type': 'thermal_camera',
                'capabilities': ['thermal', 'usb', 'video'],
                'status': 'mock',
                'resolution': (160, 120),
                'frame_rate': 30
            }
        ],
        'environment': {
            'test_mode': True,
            'mock_data_quality': 'good',
            'noise_level': 0.1,
            'simulation_time_factor': 1.0
        }
    }
    
    logger.info("Created mock hardware environment")
    return mock_env


def get_hardware_test_config() -> HardwareConfig:
    """
    Get hardware testing configuration from environment variables.
    
    Returns:
        Hardware configuration object
    """
    config = HardwareConfig()
    
    # Check environment variables
    config.use_real_hardware = os.getenv('USE_REAL_HARDWARE', 'false').lower() == 'true'
    config.shimmer_timeout = float(os.getenv('SHIMMER_TIMEOUT', '5.0'))
    config.thermal_timeout = float(os.getenv('THERMAL_TIMEOUT', '5.0'))
    config.mock_data_quality = os.getenv('MOCK_DATA_QUALITY', 'good')
    config.enable_stress_testing = os.getenv('ENABLE_STRESS_TESTING', 'true').lower() == 'true'
    config.max_connection_retries = int(os.getenv('MAX_CONNECTION_RETRIES', '3'))
    
    logger.info(f"Hardware test config: use_real={config.use_real_hardware}")
    return config


def monitor_hardware_health(devices: List[Any], duration: float = 10.0) -> Dict[str, Any]:
    """
    Monitor hardware device health over a specified duration.
    
    Args:
        devices: List of hardware devices to monitor
        duration: Monitoring duration in seconds
        
    Returns:
        Health monitoring report
    """
    start_time = time.time()
    health_report = {
        'start_time': start_time,
        'duration': duration,
        'devices': {},
        'errors': [],
        'warnings': []
    }
    
    for device in devices:
        device_id = getattr(device, 'device_id', str(id(device)))
        health_report['devices'][device_id] = {
            'connection_checks': 0,
            'successful_checks': 0,
            'errors': [],
            'last_check': None
        }
        
    logger.info(f"Starting hardware health monitoring for {duration} seconds")
    
    while time.time() - start_time < duration:
        for device in devices:
            device_id = getattr(device, 'device_id', str(id(device)))
            device_health = health_report['devices'][device_id]
            
            try:
                device_health['connection_checks'] += 1
                
                # Check if device is connected
                if hasattr(device, 'connected'):
                    if device.connected:
                        device_health['successful_checks'] += 1
                    else:
                        device_health['errors'].append({
                            'timestamp': time.time(),
                            'error': 'Device not connected'
                        })
                        
                device_health['last_check'] = time.time()
                
            except Exception as e:
                error_info = {
                    'timestamp': time.time(),
                    'error': str(e),
                    'device_id': device_id
                }
                device_health['errors'].append(error_info)
                health_report['errors'].append(error_info)
                
        time.sleep(1.0)  # Check every second
        
    # Calculate health statistics
    for device_id, device_health in health_report['devices'].items():
        if device_health['connection_checks'] > 0:
            device_health['success_rate'] = (
                device_health['successful_checks'] / device_health['connection_checks']
            )
        else:
            device_health['success_rate'] = 0.0
            
    health_report['end_time'] = time.time()
    logger.info("Hardware health monitoring complete")
    
    return health_report


@dataclass
class HardwareDevice:
    """Represents a physical hardware device for testing."""
    device_id: str
    device_type: str
    interface: str  # 'bluetooth', 'usb', 'serial'
    address: str
    name: str
    status: str = 'disconnected'
    last_seen: Optional[datetime] = None
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class HardwareDiscovery:
    """Discovers and manages physical hardware devices for testing."""
    
    def __init__(self):
        self.discovered_devices = {}
        self.monitoring_active = False
        self.monitor_thread = None
    
    def discover_devices(self, timeout_seconds: int = 30) -> List[HardwareDevice]:
        """Discover all available hardware devices."""
        devices = []
        
        # Discover Bluetooth devices
        if BLUETOOTH_AVAILABLE:
            devices.extend(self._discover_bluetooth_devices(timeout_seconds))
        
        # Discover USB devices
        if USB_AVAILABLE:
            devices.extend(self._discover_usb_devices())
        
        # Discover Serial devices
        if SERIAL_AVAILABLE:
            devices.extend(self._discover_serial_devices())
        
        # Update device registry
        for device in devices:
            self.discovered_devices[device.device_id] = device
        
        return devices
    
    def _discover_bluetooth_devices(self, timeout_seconds: int) -> List[HardwareDevice]:
        """Discover Bluetooth devices (Shimmer sensors)."""
        devices = []
        
        try:
            print("Scanning for Bluetooth devices...")
            nearby_devices = bluetooth.discover_devices(
                duration=min(timeout_seconds, 8),
                lookup_names=True,
                flush_cache=True
            )
            
            for addr, name in nearby_devices:
                # Check if device is a Shimmer sensor
                if self._is_shimmer_device(name, addr):
                    device = HardwareDevice(
                        device_id=f"bt_{addr.replace(':', '')}",
                        device_type="shimmer",
                        interface="bluetooth",
                        address=addr,
                        name=name or "Unknown Shimmer",
                        status="discovered",
                        last_seen=datetime.now(),
                        capabilities=["gsr", "accelerometer", "gyroscope"]
                    )
                    devices.append(device)
                    print(f"Found Shimmer device: {name} ({addr})")
        
        except Exception as e:
            print(f"Bluetooth discovery failed: {e}")
        
        return devices
    
    def _discover_usb_devices(self) -> List[HardwareDevice]:
        """Discover USB devices (thermal cameras, etc.)."""
        devices = []
        
        try:
            usb_devices = usb.core.find(find_all=True)
            
            for dev in usb_devices:
                # Check for thermal camera devices
                if self._is_thermal_camera_device(dev):
                    device = HardwareDevice(
                        device_id=f"usb_{dev.idVendor:04x}_{dev.idProduct:04x}_{dev.address}",
                        device_type="thermal_camera",
                        interface="usb",
                        address=f"usb://{dev.bus}/{dev.address}",
                        name=self._get_usb_device_name(dev),
                        status="discovered",
                        last_seen=datetime.now(),
                        capabilities=["thermal_imaging", "temperature_measurement"]
                    )
                    devices.append(device)
                    print(f"Found thermal camera: {device.name} ({device.address})")
        
        except Exception as e:
            print(f"USB discovery failed: {e}")
        
        return devices
    
    def _discover_serial_devices(self) -> List[HardwareDevice]:
        """Discover Serial/COM port devices."""
        devices = []
        
        try:
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                # Check if port has a connected device
                if port.device and self._is_valid_serial_device(port):
                    device = HardwareDevice(
                        device_id=f"serial_{port.device.replace('/', '_')}",
                        device_type="serial_device",
                        interface="serial",
                        address=port.device,
                        name=port.description or "Serial Device",
                        status="discovered",
                        last_seen=datetime.now(),
                        capabilities=["serial_communication"]
                    )
                    devices.append(device)
                    print(f"Found serial device: {device.name} ({device.address})")
        
        except Exception as e:
            print(f"Serial discovery failed: {e}")
        
        return devices
    
    def _is_shimmer_device(self, name: str, address: str) -> bool:
        """Check if Bluetooth device is a Shimmer sensor."""
        if not name:
            return False
        
        shimmer_indicators = ["shimmer", "shim", "gsr", "sensor"]
        name_lower = name.lower()
        
        return any(indicator in name_lower for indicator in shimmer_indicators)
    
    def _is_thermal_camera_device(self, usb_device) -> bool:
        """Check if USB device is a thermal camera."""
        # Common thermal camera vendor/product IDs
        thermal_camera_ids = [
            (0x289d, 0x0010),  # TOPDON thermal camera
            (0x1234, 0x5678),  # Example thermal camera
        ]
        
        device_id = (usb_device.idVendor, usb_device.idProduct)
        return device_id in thermal_camera_ids
    
    def _get_usb_device_name(self, usb_device) -> str:
        """Get human-readable name for USB device."""
        try:
            manufacturer = usb.util.get_string(usb_device, usb_device.iManufacturer)
            product = usb.util.get_string(usb_device, usb_device.iProduct)
            
            if manufacturer and product:
                return f"{manufacturer} {product}"
            elif product:
                return product
            else:
                return f"USB Device {usb_device.idVendor:04x}:{usb_device.idProduct:04x}"
        except:
            return f"USB Device {usb_device.idVendor:04x}:{usb_device.idProduct:04x}"
    
    def _is_valid_serial_device(self, port) -> bool:
        """Check if serial port has a valid device."""
        # Basic validation - could be enhanced with device-specific checks
        return port.vid is not None or port.pid is not None
    
    def start_device_monitoring(self):
        """Start continuous device monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_devices, daemon=True)
        self.monitor_thread.start()
    
    def stop_device_monitoring(self):
        """Stop device monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_devices(self):
        """Continuously monitor device availability."""
        while self.monitoring_active:
            try:
                current_devices = self.discover_devices(timeout_seconds=5)
                
                # Update device status
                current_device_ids = {d.device_id for d in current_devices}
                
                for device_id, device in self.discovered_devices.items():
                    if device_id in current_device_ids:
                        device.status = "available"
                        device.last_seen = datetime.now()
                    else:
                        device.status = "unavailable"
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Device monitoring error: {e}")
                time.sleep(5)


class HardwareTestConfiguration:
    """Manages test configuration for different hardware setups."""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(__file__).parent / "hardware_test_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load hardware test configuration."""
        default_config = {
            "required_devices": {
                "shimmer": {"min_count": 1, "max_count": 3},
                "thermal_camera": {"min_count": 0, "max_count": 1}
            },
            "test_timeouts": {
                "discovery_timeout": 30,
                "connection_timeout": 15,
                "data_collection_timeout": 60
            },
            "test_parameters": {
                "shimmer": {
                    "sampling_rate": 128,
                    "test_duration_seconds": 10,
                    "expected_data_rate": 120  # samples per second
                },
                "thermal_camera": {
                    "frame_rate": 30,
                    "test_duration_seconds": 5,
                    "expected_frame_rate": 25  # frames per second
                }
            },
            "test_environment": {
                "lab_setup": True,
                "automated_test": True,
                "require_all_devices": False
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get_required_devices(self) -> Dict:
        """Get required device configuration."""
        return self.config.get("required_devices", {})
    
    def get_test_parameters(self, device_type: str) -> Dict:
        """Get test parameters for specific device type."""
        return self.config.get("test_parameters", {}).get(device_type, {})
    
    def is_lab_setup(self) -> bool:
        """Check if running in lab setup."""
        return self.config.get("test_environment", {}).get("lab_setup", False)


class HardwareTestValidator:
    """Validates hardware test data and results."""
    
    def __init__(self):
        self.validation_rules = {
            "shimmer_gsr": {
                "min_value": 0.0,
                "max_value": 10.0,
                "units": "microsiemens"
            },
            "shimmer_accelerometer": {
                "min_value": -16.0,
                "max_value": 16.0,
                "units": "g"
            },
            "thermal_temperature": {
                "min_value": -20.0,
                "max_value": 150.0,
                "units": "celsius"
            }
        }
    
    def validate_shimmer_data(self, data: List[Dict]) -> Dict:
        """Validate Shimmer sensor data."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sample_count": len(data),
            "data_quality": {}
        }
        
        if not data:
            validation_result["valid"] = False
            validation_result["errors"].append("No data samples received")
            return validation_result
        
        # Validate GSR data
        gsr_values = [sample.get("gsr", 0) for sample in data if "gsr" in sample]
        if gsr_values:
            gsr_validation = self._validate_sensor_values(
                gsr_values, self.validation_rules["shimmer_gsr"]
            )
            validation_result["data_quality"]["gsr"] = gsr_validation
            
            if not gsr_validation["valid"]:
                validation_result["errors"].extend(gsr_validation["errors"])
        
        # Validate accelerometer data
        accel_values = []
        for sample in data:
            if "accelerometer" in sample:
                accel_data = sample["accelerometer"]
                if isinstance(accel_data, dict):
                    accel_values.extend([accel_data.get("x", 0), accel_data.get("y", 0), accel_data.get("z", 0)])
        
        if accel_values:
            accel_validation = self._validate_sensor_values(
                accel_values, self.validation_rules["shimmer_accelerometer"]
            )
            validation_result["data_quality"]["accelerometer"] = accel_validation
            
            if not accel_validation["valid"]:
                validation_result["warnings"].extend(accel_validation["errors"])
        
        # Check data continuity
        timestamps = [sample.get("timestamp", 0) for sample in data]
        if timestamps:
            timestamp_gaps = self._check_timestamp_continuity(timestamps)
            if timestamp_gaps > len(data) * 0.05:  # More than 5% gaps
                validation_result["warnings"].append(f"High timestamp gap count: {timestamp_gaps}")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result
    
    def validate_thermal_data(self, frames: List[Dict]) -> Dict:
        """Validate thermal camera data."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "frame_count": len(frames),
            "data_quality": {}
        }
        
        if not frames:
            validation_result["valid"] = False
            validation_result["errors"].append("No thermal frames received")
            return validation_result
        
        # Validate temperature data
        temp_values = []
        for frame in frames:
            if "temperature_data" in frame:
                temp_data = frame["temperature_data"]
                if isinstance(temp_data, list):
                    temp_values.extend(temp_data)
        
        if temp_values:
            temp_validation = self._validate_sensor_values(
                temp_values, self.validation_rules["thermal_temperature"]
            )
            validation_result["data_quality"]["temperature"] = temp_validation
            
            if not temp_validation["valid"]:
                validation_result["errors"].extend(temp_validation["errors"])
        
        # Check frame rate consistency
        timestamps = [frame.get("timestamp", 0) for frame in frames]
        if len(timestamps) > 1:
            frame_rate = self._calculate_frame_rate(timestamps)
            validation_result["data_quality"]["frame_rate"] = frame_rate
            
            if frame_rate < 20:  # Below expected minimum
                validation_result["warnings"].append(f"Low frame rate: {frame_rate:.1f} fps")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result
    
    def _validate_sensor_values(self, values: List[float], rules: Dict) -> Dict:
        """Validate sensor values against rules."""
        result = {
            "valid": True,
            "errors": [],
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
            "mean_value": sum(values) / len(values) if values else 0,
            "sample_count": len(values)
        }
        
        if not values:
            result["valid"] = False
            result["errors"].append("No values to validate")
            return result
        
        # Check range
        min_val, max_val = min(values), max(values)
        if min_val < rules["min_value"]:
            result["errors"].append(f"Value below minimum: {min_val} < {rules['min_value']}")
        
        if max_val > rules["max_value"]:
            result["errors"].append(f"Value above maximum: {max_val} > {rules['max_value']}")
        
        # Check for impossible values (NaN, inf)
        invalid_count = sum(1 for v in values if not isinstance(v, (int, float)) or v != v)
        if invalid_count > 0:
            result["errors"].append(f"Invalid values found: {invalid_count}")
        
        result["valid"] = len(result["errors"]) == 0
        return result
    
    def _check_timestamp_continuity(self, timestamps: List[float]) -> int:
        """Check for gaps in timestamp sequence."""
        if len(timestamps) < 2:
            return 0
        
        sorted_timestamps = sorted(timestamps)
        gaps = 0
        
        for i in range(1, len(sorted_timestamps)):
            time_diff = sorted_timestamps[i] - sorted_timestamps[i-1]
            # If gap is more than 2x expected interval, count as gap
            expected_interval = 1.0 / 128  # Assuming 128 Hz sampling
            if time_diff > expected_interval * 2:
                gaps += 1
        
        return gaps
    
    def _calculate_frame_rate(self, timestamps: List[float]) -> float:
        """Calculate average frame rate from timestamps."""
        if len(timestamps) < 2:
            return 0.0
        
        sorted_timestamps = sorted(timestamps)
        total_time = sorted_timestamps[-1] - sorted_timestamps[0]
        
        if total_time <= 0:
            return 0.0
        
        return (len(timestamps) - 1) / total_time


def get_hardware_test_config() -> HardwareTestConfiguration:
    """Get default hardware test configuration."""
    return HardwareTestConfiguration()


def discover_test_hardware(timeout_seconds: int = 30) -> List[HardwareDevice]:
    """Discover hardware devices for testing."""
    discovery = HardwareDiscovery()
    return discovery.discover_devices(timeout_seconds)


def validate_test_environment() -> Dict:
    """Validate that test environment is ready for hardware testing."""
    result = {
        "ready": True,
        "issues": [],
        "capabilities": []
    }
    
    # Check for required libraries
    if not BLUETOOTH_AVAILABLE:
        result["issues"].append("Bluetooth support not available (install pybluez)")
    else:
        result["capabilities"].append("bluetooth")
    
    if not USB_AVAILABLE:
        result["issues"].append("USB support not available (install pyusb)")
    else:
        result["capabilities"].append("usb")
    
    if not SERIAL_AVAILABLE:
        result["issues"].append("Serial support not available (install pyserial)")
    else:
        result["capabilities"].append("serial")
    
    # Check for hardware devices
    try:
        devices = discover_test_hardware(timeout_seconds=10)
        if devices:
            result["capabilities"].append(f"hardware_devices ({len(devices)} found)")
        else:
            result["issues"].append("No hardware devices discovered")
    except Exception as e:
        result["issues"].append(f"Hardware discovery failed: {e}")
    
    result["ready"] = len(result["issues"]) == 0
    return result


if __name__ == "__main__":
    # Test hardware utilities
    print("Validating test environment...")
    env_status = validate_test_environment()
    
    print(f"Environment ready: {env_status['ready']}")
    print(f"Capabilities: {env_status['capabilities']}")
    if env_status['issues']:
        print(f"Issues: {env_status['issues']}")
    
    if env_status['ready']:
        print("\nDiscovering hardware devices...")
        devices = discover_test_hardware()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device.name} ({device.device_type}) at {device.address}")