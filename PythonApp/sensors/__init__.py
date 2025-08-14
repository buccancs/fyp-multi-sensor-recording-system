"""
Sensor Integration Module
========================

Handles integration with various sensor devices including Shimmer GSR sensors.
Provides simulation mode for testing and development.
"""

import json
import logging
import threading
import time
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SensorSample:
    """Represents a single sensor data sample."""
    timestamp: float
    device_id: str
    sensor_type: str
    data: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'device_id': self.device_id,
            'sensor_type': self.sensor_type,
            'data': self.data
        }


class ShimmerGSRSensor:
    """Handles connection to Shimmer GSR+ sensors."""
    
    def __init__(self, device_id: str, port: Optional[str] = None):
        self.device_id = device_id
        self.port = port
        self.is_connected = False
        self.is_streaming = False
        self.connection = None
        self.streaming_thread = None
        self.data_callback: Optional[Callable[[SensorSample], None]] = None
        self.sample_rate = 128  # Hz
        
        # Try to import PyShimmer library
        self._pyshimmer_available = False
        try:
            global PyShimmer
            from pyshimmer import PyShimmer
            self._pyshimmer_available = True
            logger.info("PyShimmer library available")
        except ImportError:
            logger.warning("PyShimmer library not available, using simulation mode")
    
    def set_data_callback(self, callback: Callable[[SensorSample], None]):
        """Set callback function for incoming sensor data."""
        self.data_callback = callback
    
    def connect(self) -> bool:
        """Connect to the Shimmer sensor."""
        if self.is_connected:
            return True
        
        try:
            if self._pyshimmer_available and self.port:
                # Use real PyShimmer connection
                self.connection = PyShimmer(self.port)
                if self.connection.connect():
                    self.is_connected = True
                    logger.info(f"Connected to Shimmer sensor {self.device_id} on {self.port}")
                    return True
                else:
                    logger.error(f"Failed to connect to Shimmer sensor on {self.port}")
                    return False
            else:
                # Use simulation mode
                self.connection = "simulation"
                self.is_connected = True
                logger.info(f"Connected to simulated Shimmer sensor {self.device_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error connecting to Shimmer sensor: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the Shimmer sensor."""
        if self.is_streaming:
            self.stop_streaming()
        
        if self.connection and self.connection != "simulation":
            try:
                self.connection.disconnect()
            except:
                pass
        
        self.connection = None
        self.is_connected = False
        logger.info(f"Disconnected from Shimmer sensor {self.device_id}")
    
    def start_streaming(self) -> bool:
        """Start streaming data from the sensor."""
        if not self.is_connected:
            logger.error("Cannot start streaming - sensor not connected")
            return False
        
        if self.is_streaming:
            return True
        
        try:
            if self.connection == "simulation":
                # Start simulation streaming
                self.streaming_thread = threading.Thread(target=self._simulate_streaming, daemon=True)
            else:
                # Start real streaming
                self.streaming_thread = threading.Thread(target=self._real_streaming, daemon=True)
            
            self.is_streaming = True
            self.streaming_thread.start()
            logger.info(f"Started streaming from Shimmer sensor {self.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting streaming: {e}")
            return False
    
    def stop_streaming(self):
        """Stop streaming data from the sensor."""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        if self.streaming_thread and self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=2.0)
        
        logger.info(f"Stopped streaming from Shimmer sensor {self.device_id}")
    
    def _simulate_streaming(self):
        """Simulate GSR data streaming for testing."""
        import random
        import math
        
        base_gsr = 10.0  # Base GSR in microsiemens
        time_offset = 0
        
        while self.is_streaming:
            try:
                # Generate realistic GSR data with some variation
                variation = math.sin(time_offset * 0.1) * 2.0  # Slow variation
                noise = random.gauss(0, 0.5)  # Random noise
                gsr_value = max(0, base_gsr + variation + noise)
                
                # Create sample
                sample = SensorSample(
                    timestamp=time.time(),
                    device_id=self.device_id,
                    sensor_type="gsr",
                    data={
                        'gsr': gsr_value,
                        'ppg': random.randint(600, 800),  # Simulated PPG
                        'accel_x': random.gauss(0, 0.1),
                        'accel_y': random.gauss(0, 0.1),
                        'accel_z': random.gauss(1.0, 0.1)
                    }
                )
                
                if self.data_callback:
                    self.data_callback(sample)
                
                time_offset += 1
                time.sleep(1.0 / self.sample_rate)  # 128 Hz
                
            except Exception as e:
                logger.error(f"Error in simulation streaming: {e}")
                break
    
    def _real_streaming(self):
        """Handle real sensor data streaming."""
        while self.is_streaming and self.connection:
            try:
                # Read data from real Shimmer sensor
                data = self.connection.read_data()
                if data:
                    sample = SensorSample(
                        timestamp=time.time(),
                        device_id=self.device_id,
                        sensor_type="gsr",
                        data=data
                    )
                    
                    if self.data_callback:
                        self.data_callback(sample)
                
                time.sleep(1.0 / self.sample_rate)
                
            except Exception as e:
                logger.error(f"Error in real streaming: {e}")
                break


class SensorManager:
    """Manages multiple sensor devices and data collection."""
    
    def __init__(self, output_directory: str = "sensor_data"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        self.sensors: Dict[str, ShimmerGSRSensor] = {}
        self.data_writers: Dict[str, csv.DictWriter] = {}
        self.data_files: Dict[str, Any] = {}
        self.is_recording = False
        
        # Statistics
        self.sample_counts: Dict[str, int] = {}
        self.start_time: Optional[datetime] = None
    
    def add_sensor(self, device_id: str, port: Optional[str] = None) -> bool:
        """Add a sensor to the manager."""
        if device_id in self.sensors:
            logger.warning(f"Sensor {device_id} already exists")
            return True
        
        sensor = ShimmerGSRSensor(device_id, port)
        sensor.set_data_callback(self._on_sensor_data)
        
        if sensor.connect():
            self.sensors[device_id] = sensor
            self.sample_counts[device_id] = 0
            logger.info(f"Added sensor {device_id}")
            return True
        else:
            logger.error(f"Failed to connect sensor {device_id}")
            return False
    
    def remove_sensor(self, device_id: str):
        """Remove a sensor from the manager."""
        if device_id in self.sensors:
            sensor = self.sensors[device_id]
            sensor.disconnect()
            del self.sensors[device_id]
            
            if device_id in self.sample_counts:
                del self.sample_counts[device_id]
            
            logger.info(f"Removed sensor {device_id}")
    
    def start_recording(self, session_id: str) -> bool:
        """Start recording data from all sensors."""
        if self.is_recording:
            logger.warning("Already recording")
            return True
        
        if not self.sensors:
            logger.error("No sensors available")
            return False
        
        try:
            # Create session directory
            session_dir = self.output_directory / session_id
            session_dir.mkdir(exist_ok=True)
            
            # Start data files for each sensor
            for device_id, sensor in self.sensors.items():
                csv_file = session_dir / f"{device_id}_data.csv"
                file_handle = open(csv_file, 'w', newline='')
                
                fieldnames = ['timestamp', 'device_id', 'sensor_type', 'gsr', 'ppg', 'accel_x', 'accel_y', 'accel_z']
                writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
                writer.writeheader()
                
                self.data_files[device_id] = file_handle
                self.data_writers[device_id] = writer
                
                # Start streaming
                if not sensor.start_streaming():
                    logger.error(f"Failed to start streaming for sensor {device_id}")
                    return False
            
            self.is_recording = True
            self.start_time = datetime.now()
            logger.info(f"Started recording sensor data for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting sensor recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Stop recording data from all sensors."""
        if not self.is_recording:
            return True
        
        try:
            # Stop all sensors
            for sensor in self.sensors.values():
                sensor.stop_streaming()
            
            # Close all data files
            for file_handle in self.data_files.values():
                file_handle.close()
            
            self.data_files.clear()
            self.data_writers.clear()
            self.is_recording = False
            
            logger.info("Stopped recording sensor data")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping sensor recording: {e}")
            return False
    
    def _on_sensor_data(self, sample: SensorSample):
        """Handle incoming sensor data."""
        if not self.is_recording:
            return
        
        device_id = sample.device_id
        
        # Write to CSV
        if device_id in self.data_writers:
            row = {
                'timestamp': sample.timestamp,
                'device_id': sample.device_id,
                'sensor_type': sample.sensor_type,
                'gsr': sample.data.get('gsr', ''),
                'ppg': sample.data.get('ppg', ''),
                'accel_x': sample.data.get('accel_x', ''),
                'accel_y': sample.data.get('accel_y', ''),
                'accel_z': sample.data.get('accel_z', '')
            }
            
            self.data_writers[device_id].writerow(row)
            self.data_files[device_id].flush()  # Ensure data is written
        
        # Update statistics
        self.sample_counts[device_id] = self.sample_counts.get(device_id, 0) + 1
    
    def get_sensor_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all sensors."""
        status = {}
        
        for device_id, sensor in self.sensors.items():
            status[device_id] = {
                'device_id': device_id,
                'is_connected': sensor.is_connected,
                'is_streaming': sensor.is_streaming,
                'sample_count': self.sample_counts.get(device_id, 0),
                'port': sensor.port,
                'sample_rate': sensor.sample_rate
            }
        
        return status
    
    def discover_sensors(self) -> List[str]:
        """Discover available sensor devices."""
        discovered = []
        
        # Try to discover real Shimmer devices
        try:
            # This would typically use pyshimmer or other discovery methods
            # For now, return list of simulated sensors
            discovered.append("shimmer_gsr_001")
            discovered.append("shimmer_gsr_002")
            logger.info(f"Discovered sensors: {discovered}")
        except Exception as e:
            logger.warning(f"Sensor discovery failed: {e}")
            # Return at least one simulated sensor for testing
            discovered.append("shimmer_gsr_simulation")
        
        return discovered
    
    def log_sensor_data(self, sample: SensorSample):
        """Log sensor data to storage."""
        try:
            # If recording, data is already being logged via callback
            # This method allows manual logging of individual samples
            if sample.device_id not in self.sample_counts:
                self.sample_counts[sample.device_id] = 0
            
            self.sample_counts[sample.device_id] += 1
            
            # Create CSV file if it doesn't exist
            if sample.device_id not in self.data_files:
                csv_file = self.output_directory / f"{sample.device_id}_data.csv"
                file_handle = open(csv_file, 'w', newline='')
                fieldnames = ['timestamp', 'device_id', 'sensor_type'] + list(sample.data.keys())
                writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
                writer.writeheader()
                
                self.data_files[sample.device_id] = file_handle
                self.data_writers[sample.device_id] = writer
            
            # Write the data
            row = {
                'timestamp': sample.timestamp,
                'device_id': sample.device_id,
                'sensor_type': sample.sensor_type,
                **sample.data
            }
            self.data_writers[sample.device_id].writerow(row)
            self.data_files[sample.device_id].flush()
            
        except Exception as e:
            logger.error(f"Error logging sensor data: {e}")
    
    def cleanup(self):
        """Clean up all sensors and resources."""
        if self.is_recording:
            self.stop_recording()
        
        # Close data files
        for file_handle in self.data_files.values():
            try:
                file_handle.close()
            except:
                pass
        
        self.data_files.clear()
        self.data_writers.clear()
        
        for sensor in list(self.sensors.values()):
            sensor.disconnect()
        
        self.sensors.clear()
        self.sample_counts.clear()