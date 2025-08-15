"""
Lab Streaming Layer (LSL) Integration
====================================

Provides LSL-based time synchronization and data streaming for multi-sensor research.
LSL handles networking, time-synchronization, and real-time data access for research experiments.
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# Try to import LSL library
try:
    import pylsl
    LSL_AVAILABLE = True
    logger.info("LSL library (pylsl) available")
except ImportError:
    LSL_AVAILABLE = False
    logger.warning("LSL library (pylsl) not available - install with: pip install pylsl")
    # Create mock pylsl for graceful degradation
    class MockPyLSL:
        class StreamInfo:
            def __init__(self, name, type, channel_count, sampling_rate, format, source_id):
                self.name = name
                self.type = type
                self.channel_count = channel_count
                self.sampling_rate = sampling_rate
                self.format = format
                self.source_id = source_id
        
        class StreamOutlet:
            def __init__(self, info):
                self.info = info
                
            def push_sample(self, data, timestamp=None):
                pass
                
            def push_chunk(self, data, timestamps=None):
                pass
        
        class StreamInlet:
            def __init__(self, info):
                self.info = info
                
            def pull_sample(self, timeout=0.0):
                return None, None
                
            def time_correction(self):
                return 0.0
        
        @staticmethod
        def resolve_stream(prop="", value="", timeout=1.0):
            return []
        
        @staticmethod
        def local_clock():
            return time.time()
        
        cf_float32 = 'cf_float32'
        cf_string = 'cf_string'
        cf_int32 = 'cf_int32'
    
    pylsl = MockPyLSL()


@dataclass
class LSLStreamInfo:
    """Information about an LSL stream."""
    name: str
    type: str
    channel_count: int
    sampling_rate: float
    format: str
    source_id: str
    is_available: bool = False


class LSLTimeSync:
    """LSL-based time synchronization service."""
    
    def __init__(self):
        self.is_available = LSL_AVAILABLE
        self.sync_stream = None
        self.sync_outlet = None
        self.time_correction = 0.0
        self.reference_streams: Dict[str, Any] = {}
        
        if self.is_available:
            self._initialize_sync_stream()
    
    def _initialize_sync_stream(self):
        """Initialize LSL synchronization stream."""
        try:
            # Create synchronization stream
            info = pylsl.StreamInfo(
                name="GSR_TimeSync",
                type="Sync",
                channel_count=1,
                sampling_rate=0,  # Irregular rate
                format=pylsl.cf_float32,
                source_id="gsr_system_sync"
            )
            
            # Add metadata
            channels = info.desc().append_child("channels")
            ch = channels.append_child("channel")
            ch.append_child_value("label", "sync_timestamp")
            ch.append_child_value("unit", "seconds")
            ch.append_child_value("type", "timestamp")
            
            self.sync_outlet = pylsl.StreamOutlet(info)
            logger.info("LSL synchronization stream created: GSR_TimeSync")
            
        except Exception as e:
            logger.error(f"Failed to initialize LSL sync stream: {e}")
            self.is_available = False
    
    def get_synchronized_time(self) -> float:
        """Get LSL-synchronized timestamp."""
        if not self.is_available:
            return time.time()
        
        try:
            return pylsl.local_clock() + self.time_correction
        except Exception as e:
            logger.error(f"Error getting LSL time: {e}")
            return time.time()
    
    def send_sync_marker(self, marker_data: Dict[str, Any]) -> bool:
        """Send synchronization marker through LSL."""
        if not self.is_available or not self.sync_outlet:
            logger.warning("LSL sync not available for marker")
            return False
        
        try:
            timestamp = self.get_synchronized_time()
            # Send marker as timestamp
            self.sync_outlet.push_sample([timestamp], timestamp)
            
            logger.debug(f"Sent LSL sync marker: {marker_data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send LSL sync marker: {e}")
            return False
    
    def calibrate_with_reference(self, reference_stream_name: str = "") -> bool:
        """Calibrate time synchronization with reference LSL stream."""
        if not self.is_available:
            return False
        
        try:
            # Look for reference streams
            if reference_stream_name:
                streams = pylsl.resolve_stream('name', reference_stream_name, timeout=2.0)
            else:
                # Look for any sync streams
                streams = pylsl.resolve_stream('type', 'Sync', timeout=2.0)
            
            if not streams:
                logger.info("No reference LSL sync streams found")
                return False
            
            # Connect to first available reference stream
            ref_info = streams[0]
            ref_inlet = pylsl.StreamInlet(ref_info)
            
            # Calculate time correction
            self.time_correction = ref_inlet.time_correction()
            
            logger.info(f"LSL time synchronized with reference stream: {ref_info.name()}")
            logger.info(f"Time correction: {self.time_correction:.6f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed LSL time calibration: {e}")
            return False
    
    def discover_available_streams(self) -> List[LSLStreamInfo]:
        """Discover available LSL streams on the network."""
        if not self.is_available:
            return []
        
        try:
            # Resolve all available streams
            streams = pylsl.resolve_stream(timeout=3.0)
            
            stream_list = []
            for stream_info in streams:
                lsl_info = LSLStreamInfo(
                    name=stream_info.name(),
                    type=stream_info.type(),
                    channel_count=stream_info.channel_count(),
                    sampling_rate=stream_info.nominal_srate(),
                    format=stream_info.channel_format(),
                    source_id=stream_info.source_id(),
                    is_available=True
                )
                stream_list.append(lsl_info)
            
            logger.info(f"Discovered {len(stream_list)} LSL streams")
            return stream_list
            
        except Exception as e:
            logger.error(f"Failed to discover LSL streams: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get LSL synchronization status."""
        return {
            'lsl_available': self.is_available,
            'sync_stream_active': self.sync_outlet is not None,
            'time_correction': self.time_correction,
            'current_time': self.get_synchronized_time(),
            'reference_streams': len(self.reference_streams)
        }


class LSLSensorStream:
    """LSL stream for sensor data (GSR, etc.)."""
    
    def __init__(self, sensor_name: str, sensor_type: str = "GSR", sampling_rate: float = 128.0):
        self.sensor_name = sensor_name
        self.sensor_type = sensor_type
        self.sampling_rate = sampling_rate
        self.is_available = LSL_AVAILABLE
        self.outlet = None
        self.time_sync = LSLTimeSync()
        
        if self.is_available:
            self._create_stream()
    
    def _create_stream(self):
        """Create LSL outlet stream for sensor data."""
        try:
            # Create stream info for GSR data
            info = pylsl.StreamInfo(
                name=f"GSR_{self.sensor_name}",
                type=self.sensor_type,
                channel_count=2,  # GSR value + timestamp
                sampling_rate=self.sampling_rate,
                format=pylsl.cf_float32,
                source_id=f"shimmer_gsr_{self.sensor_name}"
            )
            
            # Add channel metadata
            channels = info.desc().append_child("channels")
            
            # GSR channel
            gsr_ch = channels.append_child("channel")
            gsr_ch.append_child_value("label", "GSR")
            gsr_ch.append_child_value("unit", "microsiemens")
            gsr_ch.append_child_value("type", "GSR")
            
            # Timestamp channel
            ts_ch = channels.append_child("channel")
            ts_ch.append_child_value("label", "timestamp")
            ts_ch.append_child_value("unit", "seconds")
            ts_ch.append_child_value("type", "timestamp")
            
            # Add acquisition metadata
            acquisition = info.desc().append_child("acquisition")
            acquisition.append_child_value("manufacturer", "Shimmer")
            acquisition.append_child_value("model", "GSR+")
            
            self.outlet = pylsl.StreamOutlet(info)
            logger.info(f"LSL sensor stream created: GSR_{self.sensor_name}")
            
        except Exception as e:
            logger.error(f"Failed to create LSL sensor stream: {e}")
            self.is_available = False
    
    def push_gsr_sample(self, gsr_value: float, timestamp: Optional[float] = None) -> bool:
        """Push a single GSR sample to LSL stream."""
        if not self.is_available or not self.outlet:
            return False
        
        try:
            if timestamp is None:
                timestamp = self.time_sync.get_synchronized_time()
            
            # Push sample with GSR value and timestamp
            sample = [gsr_value, timestamp]
            self.outlet.push_sample(sample, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to push GSR sample to LSL: {e}")
            return False
    
    def push_gsr_chunk(self, gsr_values: List[float], timestamps: Optional[List[float]] = None) -> bool:
        """Push multiple GSR samples to LSL stream."""
        if not self.is_available or not self.outlet:
            return False
        
        try:
            if timestamps is None:
                current_time = self.time_sync.get_synchronized_time()
                time_step = 1.0 / self.sampling_rate
                timestamps = [current_time - (len(gsr_values) - i - 1) * time_step 
                             for i in range(len(gsr_values))]
            
            # Prepare chunk data
            chunk_data = [[gsr_val, ts] for gsr_val, ts in zip(gsr_values, timestamps)]
            
            self.outlet.push_chunk(chunk_data, timestamps)
            
            logger.debug(f"Pushed {len(gsr_values)} GSR samples to LSL")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push GSR chunk to LSL: {e}")
            return False
    
    def close(self):
        """Close the LSL stream."""
        if self.outlet:
            try:
                # LSL outlets are automatically cleaned up
                self.outlet = None
                logger.info(f"Closed LSL sensor stream: {self.sensor_name}")
            except Exception as e:
                logger.error(f"Error closing LSL stream: {e}")


class LSLDeviceCoordinator:
    """Coordinates multiple devices using LSL for synchronization."""
    
    def __init__(self):
        self.is_available = LSL_AVAILABLE
        self.time_sync = LSLTimeSync()
        self.sensor_streams: Dict[str, LSLSensorStream] = {}
        self.coordinator_outlet = None
        
        if self.is_available:
            self._create_coordinator_stream()
    
    def _create_coordinator_stream(self):
        """Create LSL stream for device coordination commands."""
        try:
            info = pylsl.StreamInfo(
                name="GSR_DeviceCoordinator",
                type="Commands",
                channel_count=1,
                sampling_rate=0,  # Irregular rate
                format=pylsl.cf_string,
                source_id="gsr_device_coordinator"
            )
            
            # Add metadata
            channels = info.desc().append_child("channels")
            ch = channels.append_child("channel")
            ch.append_child_value("label", "command")
            ch.append_child_value("type", "command")
            
            self.coordinator_outlet = pylsl.StreamOutlet(info)
            logger.info("LSL device coordinator stream created")
            
        except Exception as e:
            logger.error(f"Failed to create LSL coordinator stream: {e}")
            self.is_available = False
    
    def register_sensor(self, sensor_id: str, sensor_type: str = "GSR") -> bool:
        """Register a sensor for LSL streaming."""
        if not self.is_available:
            return False
        
        try:
            if sensor_id not in self.sensor_streams:
                stream = LSLSensorStream(sensor_id, sensor_type)
                if stream.is_available:
                    self.sensor_streams[sensor_id] = stream
                    logger.info(f"Registered LSL sensor stream: {sensor_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to register LSL sensor {sensor_id}: {e}")
            return False
    
    def send_coordination_command(self, command: str, data: Dict[str, Any] = None) -> bool:
        """Send coordination command through LSL."""
        if not self.is_available or not self.coordinator_outlet:
            return False
        
        try:
            command_data = {
                'command': command,
                'timestamp': self.time_sync.get_synchronized_time(),
                'data': data or {}
            }
            
            # Send as JSON string
            command_json = json.dumps(command_data)
            self.coordinator_outlet.push_sample([command_json])
            
            logger.info(f"Sent LSL coordination command: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send LSL coordination command: {e}")
            return False
    
    def start_synchronized_recording(self, session_id: str, device_ids: List[str]) -> bool:
        """Start synchronized recording across all devices using LSL."""
        return self.send_coordination_command('start_recording', {
            'session_id': session_id,
            'device_ids': device_ids,
            'sync_timestamp': self.time_sync.get_synchronized_time()
        })
    
    def stop_synchronized_recording(self) -> bool:
        """Stop synchronized recording across all devices."""
        return self.send_coordination_command('stop_recording', {
            'stop_timestamp': self.time_sync.get_synchronized_time()
        })
    
    def send_sync_flash(self) -> bool:
        """Send synchronization flash signal through LSL."""
        return self.send_coordination_command('sync_flash', {
            'flash_timestamp': self.time_sync.get_synchronized_time(),
            'duration_ms': 100
        })
    
    def push_sensor_data(self, sensor_id: str, gsr_value: float, timestamp: Optional[float] = None) -> bool:
        """Push sensor data through LSL stream."""
        if sensor_id in self.sensor_streams:
            return self.sensor_streams[sensor_id].push_gsr_sample(gsr_value, timestamp)
        return False
    
    def get_lsl_status(self) -> Dict[str, Any]:
        """Get comprehensive LSL system status."""
        return {
            'lsl_available': self.is_available,
            'time_sync_status': self.time_sync.get_status(),
            'active_sensor_streams': list(self.sensor_streams.keys()),
            'coordinator_active': self.coordinator_outlet is not None,
            'available_streams': self.time_sync.discover_available_streams()
        }
    
    def cleanup(self):
        """Clean up all LSL streams and resources."""
        try:
            # Close all sensor streams
            for stream in self.sensor_streams.values():
                stream.close()
            self.sensor_streams.clear()
            
            # Coordinator outlet cleanup (automatic in LSL)
            self.coordinator_outlet = None
            
            logger.info("LSL coordinator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during LSL cleanup: {e}")


# Singleton instances for global access
lsl_time_sync = LSLTimeSync()
lsl_coordinator = LSLDeviceCoordinator()