"""
ShimmerManager - Python implementation for Shimmer sensor integration

This module provides comprehensive Shimmer sensor management functionality
for the multi-sensor recording system, serving as a failover mechanism
when Android phones cannot connect to Shimmer devices.

Based on the Android ShimmerRecorder implementation and using the pyshimmer library.
Implements Bluetooth device discovery, connection handling, real-time data streaming,
data buffering, CSV logging, and session-based data organization.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import csv
import logging
import os
import queue
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Set

# Add pyshimmer library to path
sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "AndroidApp", "libs", "pyshimmer"
    )
)

try:
    from serial import Serial
    from pyshimmer import ShimmerBluetooth, DEFAULT_BAUDRATE, DataPacket

    PYSHIMMER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PyShimmer library not available: {e}")
    PYSHIMMER_AVAILABLE = False

    # Create mock classes for development/testing
    class Serial:
        def __init__(self, *args, **kwargs):
            pass

    class ShimmerBluetooth:
        def __init__(self, *args, **kwargs):
            pass

    class DataPacket:
        def __init__(self, *args, **kwargs):
            pass

    DEFAULT_BAUDRATE = 115200


@dataclass
class ShimmerStatus:
    """Status information for a Shimmer device"""

    is_available: bool = False
    is_connected: bool = False
    is_recording: bool = False
    is_streaming: bool = False
    sampling_rate: int = 0
    battery_level: Optional[int] = None
    signal_quality: Optional[str] = None
    samples_recorded: int = 0
    device_name: Optional[str] = None
    mac_address: Optional[str] = None
    firmware_version: Optional[str] = None


@dataclass
class ShimmerSample:
    """Data sample from Shimmer sensor"""

    timestamp: float
    system_time: str
    device_id: str
    gsr_conductance: Optional[float] = None
    ppg_a13: Optional[float] = None
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    battery_percentage: Optional[int] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class DeviceConfiguration:
    """Configuration for a Shimmer device"""

    device_id: str
    mac_address: str
    enabled_channels: Set[str]
    sampling_rate: int = 128
    connection_type: str = "bluetooth"


class ShimmerManager:
    """
    Comprehensive Shimmer sensor management system

    Provides Bluetooth device discovery, connection handling, real-time data streaming,
    data buffering, CSV logging, and session-based data organization.
    Serves as failover mechanism when Android phones cannot connect to Shimmer devices.
    """

    def __init__(self, session_manager=None, logger=None):
        """Initialize ShimmerManager with dependencies"""
        self.session_manager = session_manager
        self.logger = logger or logging.getLogger(__name__)

        # Device management
        self.connected_devices: Dict[str, ShimmerBluetooth] = {}
        self.device_configurations: Dict[str, DeviceConfiguration] = {}
        self.device_status: Dict[str, ShimmerStatus] = {}

        # Data management
        self.data_queues: Dict[str, queue.Queue] = {}
        self.csv_writers: Dict[str, csv.DictWriter] = {}
        self.csv_files: Dict[str, Any] = {}

        # Threading and synchronization
        self.is_initialized = False
        self.is_recording = False
        self.is_streaming = False
        self.data_processing_thread: Optional[threading.Thread] = None
        self.file_writing_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        # Session management
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None

        # Callbacks
        self.data_callbacks: List[Callable[[ShimmerSample], None]] = []
        self.status_callbacks: List[Callable[[str, ShimmerStatus], None]] = []

        # Configuration
        self.default_sampling_rate = 128
        self.data_buffer_size = 1000
        self.connection_timeout = 30.0

        self.logger.info("ShimmerManager initialized")

    def initialize(self) -> bool:
        """
        Initialize the Shimmer manager

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing ShimmerManager...")

            if not PYSHIMMER_AVAILABLE:
                self.logger.warning(
                    "PyShimmer library not available - using simulation mode"
                )
                self.is_initialized = True
                return True

            # Initialize data structures
            self.connected_devices.clear()
            self.device_configurations.clear()
            self.device_status.clear()
            self.data_queues.clear()

            # Start background threads
            self._start_background_threads()

            self.is_initialized = True
            self.logger.info("ShimmerManager initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize ShimmerManager: {e}")
            return False

    def scan_and_pair_devices(self) -> List[str]:
        """
        Scan for available Shimmer devices and attempt pairing

        Returns:
            List[str]: List of discovered device MAC addresses
        """
        discovered_devices = []

        try:
            self.logger.info("Scanning for Shimmer devices...")

            if not PYSHIMMER_AVAILABLE:
                # Simulate device discovery for testing
                simulated_devices = [
                    "00:06:66:66:66:66",  # Shimmer3 GSR+
                    "00:06:66:66:66:67",  # Shimmer3 GSR+
                ]
                self.logger.info(
                    f"Simulated discovery: {len(simulated_devices)} devices found"
                )
                return simulated_devices

            # TODO: Implement actual Bluetooth scanning
            # This would involve using system Bluetooth APIs to discover Shimmer devices
            # For now, return empty list as real implementation requires platform-specific code

            self.logger.info(
                f"Device scan completed: {len(discovered_devices)} devices found"
            )
            return discovered_devices

        except Exception as e:
            self.logger.error(f"Error during device scanning: {e}")
            return []

    def connect_devices(self, device_addresses: List[str]) -> bool:
        """
        Connect to specified Shimmer devices

        Args:
            device_addresses: List of MAC addresses to connect to

        Returns:
            bool: True if all connections successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to {len(device_addresses)} devices...")

            success_count = 0
            for mac_address in device_addresses:
                if self._connect_single_device(mac_address):
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to connect to device: {mac_address}")

            all_connected = success_count == len(device_addresses)
            self.logger.info(
                f"Connection results: {success_count}/{len(device_addresses)} successful"
            )

            return all_connected

        except Exception as e:
            self.logger.error(f"Error connecting devices: {e}")
            return False

    def _connect_single_device(self, mac_address: str) -> bool:
        """Connect to a single Shimmer device"""
        try:
            device_id = f"shimmer_{mac_address.replace(':', '_')}"

            if not PYSHIMMER_AVAILABLE:
                # Simulate connection for testing
                self.device_status[device_id] = ShimmerStatus(
                    is_available=True,
                    is_connected=True,
                    device_name=f"Shimmer3_{device_id[-4:]}",
                    mac_address=mac_address,
                    firmware_version="1.0.0",
                    sampling_rate=self.default_sampling_rate,
                )
                self.data_queues[device_id] = queue.Queue(maxsize=self.data_buffer_size)
                self.logger.info(f"Simulated connection to {device_id}")
                return True

            # TODO: Implement actual device connection using pyshimmer
            # This would involve:
            # 1. Creating Serial connection to device
            # 2. Initializing ShimmerBluetooth instance
            # 3. Setting up data callbacks
            # 4. Configuring device parameters

            return False

        except Exception as e:
            self.logger.error(f"Error connecting to device {mac_address}: {e}")
            return False

    def set_enabled_channels(self, device_id: str, channels: Set[str]) -> bool:
        """
        Configure enabled sensor channels for a device

        Args:
            device_id: Device identifier
            channels: Set of channel names to enable

        Returns:
            bool: True if configuration successful
        """
        try:
            if device_id not in self.device_status:
                self.logger.error(f"Device not found: {device_id}")
                return False

            # Update device configuration
            if device_id not in self.device_configurations:
                self.device_configurations[device_id] = DeviceConfiguration(
                    device_id=device_id,
                    mac_address=self.device_status[device_id].mac_address or "",
                    enabled_channels=channels,
                )
            else:
                self.device_configurations[device_id].enabled_channels = channels

            self.logger.info(f"Configured channels for {device_id}: {channels}")
            return True

        except Exception as e:
            self.logger.error(f"Error configuring channels for {device_id}: {e}")
            return False

    def start_streaming(self) -> bool:
        """
        Start data streaming from all connected devices

        Returns:
            bool: True if streaming started successfully
        """
        try:
            if not self.is_initialized:
                self.logger.error("ShimmerManager not initialized")
                return False

            self.logger.info("Starting data streaming...")

            success_count = 0
            for device_id in self.connected_devices:
                if self._start_device_streaming(device_id):
                    success_count += 1

            # Also handle simulated devices
            for device_id in self.device_status:
                if device_id not in self.connected_devices:
                    if self._start_device_streaming(device_id):
                        success_count += 1

            self.is_streaming = success_count > 0
            self.logger.info(f"Streaming started for {success_count} devices")

            return self.is_streaming

        except Exception as e:
            self.logger.error(f"Error starting streaming: {e}")
            return False

    def _start_device_streaming(self, device_id: str) -> bool:
        """Start streaming for a single device"""
        try:
            if device_id in self.connected_devices:
                # Real device streaming
                device = self.connected_devices[device_id]
                device.start_streaming()

            # Update status
            if device_id in self.device_status:
                self.device_status[device_id].is_streaming = True

            # Start simulated data generation for testing
            if not PYSHIMMER_AVAILABLE:
                self._start_simulated_streaming(device_id)

            return True

        except Exception as e:
            self.logger.error(f"Error starting streaming for {device_id}: {e}")
            return False

    def stop_streaming(self) -> bool:
        """
        Stop data streaming from all devices

        Returns:
            bool: True if streaming stopped successfully
        """
        try:
            self.logger.info("Stopping data streaming...")

            for device_id in self.connected_devices:
                self._stop_device_streaming(device_id)

            # Also handle simulated devices
            for device_id in self.device_status:
                if device_id not in self.connected_devices:
                    self._stop_device_streaming(device_id)

            self.is_streaming = False
            self.logger.info("Data streaming stopped")

            return True

        except Exception as e:
            self.logger.error(f"Error stopping streaming: {e}")
            return False

    def _stop_device_streaming(self, device_id: str) -> bool:
        """Stop streaming for a single device"""
        try:
            if device_id in self.connected_devices:
                device = self.connected_devices[device_id]
                device.stop_streaming()

            # Update status
            if device_id in self.device_status:
                self.device_status[device_id].is_streaming = False

            return True

        except Exception as e:
            self.logger.error(f"Error stopping streaming for {device_id}: {e}")
            return False

    def start_recording(self, session_id: str) -> bool:
        """
        Start recording data to files

        Args:
            session_id: Session identifier for organizing data

        Returns:
            bool: True if recording started successfully
        """
        try:
            if not self.is_initialized:
                self.logger.error("ShimmerManager not initialized")
                return False

            self.logger.info(f"Starting recording for session: {session_id}")

            self.current_session_id = session_id
            self.session_start_time = datetime.now()

            # Create session directory
            session_dir = self._create_session_directory(session_id)
            if not session_dir:
                return False

            # Initialize CSV files for each device
            for device_id in self.device_status:
                if not self._initialize_csv_file(device_id, session_dir):
                    self.logger.error(f"Failed to initialize CSV file for {device_id}")
                    return False

            # Start streaming if not already started
            if not self.is_streaming:
                if not self.start_streaming():
                    self.logger.error("Failed to start streaming for recording")
                    return False

            self.is_recording = True
            self.logger.info(f"Recording started for session: {session_id}")

            return True

        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            return False

    def stop_recording(self) -> bool:
        """
        Stop recording and close all files

        Returns:
            bool: True if recording stopped successfully
        """
        try:
            if not self.is_recording:
                self.logger.warning("Recording not active")
                return True

            self.logger.info("Stopping recording...")

            # Close CSV files
            for device_id, writer in self.csv_writers.items():
                if device_id in self.csv_files:
                    self.csv_files[device_id].close()
                    self.logger.info(f"Closed CSV file for {device_id}")

            self.csv_writers.clear()
            self.csv_files.clear()

            self.is_recording = False
            self.current_session_id = None
            self.session_start_time = None

            self.logger.info("Recording stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            return False

    def get_shimmer_status(self) -> Dict[str, ShimmerStatus]:
        """
        Get status of all Shimmer devices

        Returns:
            Dict[str, ShimmerStatus]: Status information for each device
        """
        return self.device_status.copy()

    def add_data_callback(self, callback: Callable[[ShimmerSample], None]) -> None:
        """Add callback for real-time data processing"""
        self.data_callbacks.append(callback)

    def add_status_callback(
        self, callback: Callable[[str, ShimmerStatus], None]
    ) -> None:
        """Add callback for status updates"""
        self.status_callbacks.append(callback)

    def cleanup(self) -> None:
        """Clean up resources and disconnect devices"""
        try:
            self.logger.info("Cleaning up ShimmerManager...")

            # Stop recording and streaming
            if self.is_recording:
                self.stop_recording()
            if self.is_streaming:
                self.stop_streaming()

            # Stop background threads
            self.stop_event.set()
            if self.data_processing_thread and self.data_processing_thread.is_alive():
                self.data_processing_thread.join(timeout=5.0)
            if self.file_writing_thread and self.file_writing_thread.is_alive():
                self.file_writing_thread.join(timeout=5.0)

            # Disconnect devices
            for device_id, device in self.connected_devices.items():
                try:
                    device.shutdown()
                    self.logger.info(f"Disconnected device: {device_id}")
                except Exception as e:
                    self.logger.error(f"Error disconnecting {device_id}: {e}")

            # Clean up thread pool
            self.thread_pool.shutdown(wait=True)

            # Clear data structures
            self.connected_devices.clear()
            self.device_configurations.clear()
            self.device_status.clear()
            self.data_queues.clear()

            self.is_initialized = False
            self.logger.info("ShimmerManager cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _create_session_directory(self, session_id: str) -> Optional[Path]:
        """Create directory for session data"""
        try:
            if self.session_manager:
                session_dir = Path(
                    self.session_manager.get_session_directory(session_id)
                )
            else:
                # Fallback directory structure
                base_dir = Path("recordings")
                session_dir = base_dir / session_id / "shimmer"

            session_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created session directory: {session_dir}")
            return session_dir

        except Exception as e:
            self.logger.error(f"Error creating session directory: {e}")
            return None

    def _initialize_csv_file(self, device_id: str, session_dir: Path) -> bool:
        """Initialize CSV file for a device"""
        try:
            csv_file_path = session_dir / f"{device_id}_data.csv"
            csv_file = open(csv_file_path, "w", newline="")

            fieldnames = [
                "timestamp",
                "system_time",
                "device_id",
                "gsr_conductance",
                "ppg_a13",
                "accel_x",
                "accel_y",
                "accel_z",
                "battery_percentage",
            ]

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            self.csv_files[device_id] = csv_file
            self.csv_writers[device_id] = writer

            self.logger.info(f"Initialized CSV file for {device_id}: {csv_file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing CSV file for {device_id}: {e}")
            return False

    def _start_background_threads(self) -> None:
        """Start background processing threads"""
        self.stop_event.clear()

        self.data_processing_thread = threading.Thread(
            target=self._data_processing_loop, name="ShimmerDataProcessing"
        )
        self.data_processing_thread.daemon = True
        self.data_processing_thread.start()

        self.file_writing_thread = threading.Thread(
            target=self._file_writing_loop, name="ShimmerFileWriting"
        )
        self.file_writing_thread.daemon = True
        self.file_writing_thread.start()

    def _data_processing_loop(self) -> None:
        """Background thread for processing incoming data"""
        while not self.stop_event.is_set():
            try:
                # Process data from all device queues
                for device_id, data_queue in self.data_queues.items():
                    try:
                        # Non-blocking queue check
                        sample = data_queue.get_nowait()
                        self._process_data_sample(sample)
                    except queue.Empty:
                        continue
                    except Exception as e:
                        self.logger.error(f"Error processing data for {device_id}: {e}")

                time.sleep(0.01)  # Small delay to prevent busy waiting

            except Exception as e:
                self.logger.error(f"Error in data processing loop: {e}")
                time.sleep(1.0)

    def _file_writing_loop(self) -> None:
        """Background thread for writing data to files"""
        while not self.stop_event.is_set():
            try:
                if self.is_recording:
                    # File writing is handled in _process_data_sample
                    # This thread could be used for periodic file flushing
                    for csv_file in self.csv_files.values():
                        csv_file.flush()

                time.sleep(1.0)  # Flush every second

            except Exception as e:
                self.logger.error(f"Error in file writing loop: {e}")
                time.sleep(1.0)

    def _process_data_sample(self, sample: ShimmerSample) -> None:
        """Process a single data sample"""
        try:
            # Write to CSV if recording
            if self.is_recording and sample.device_id in self.csv_writers:
                writer = self.csv_writers[sample.device_id]
                writer.writerow(asdict(sample))

            # Update device status
            if sample.device_id in self.device_status:
                status = self.device_status[sample.device_id]
                status.samples_recorded += 1
                if sample.battery_percentage is not None:
                    status.battery_level = sample.battery_percentage

            # Call data callbacks
            for callback in self.data_callbacks:
                try:
                    callback(sample)
                except Exception as e:
                    self.logger.error(f"Error in data callback: {e}")

        except Exception as e:
            self.logger.error(f"Error processing data sample: {e}")

    def _start_simulated_streaming(self, device_id: str) -> None:
        """Start simulated data streaming for testing"""

        def simulate_data():
            while not self.stop_event.is_set() and self.is_streaming:
                try:
                    if (
                        device_id in self.device_status
                        and self.device_status[device_id].is_streaming
                    ):
                        sample = self._generate_simulated_sample(device_id)
                        if device_id in self.data_queues:
                            try:
                                self.data_queues[device_id].put_nowait(sample)
                            except queue.Full:
                                # Remove oldest sample and add new one
                                try:
                                    self.data_queues[device_id].get_nowait()
                                    self.data_queues[device_id].put_nowait(sample)
                                except queue.Empty:
                                    pass

                    time.sleep(
                        1.0 / self.default_sampling_rate
                    )  # Simulate sampling rate

                except Exception as e:
                    self.logger.error(
                        f"Error in simulated streaming for {device_id}: {e}"
                    )
                    time.sleep(1.0)

        # Start simulation in thread pool
        self.thread_pool.submit(simulate_data)

    def _generate_simulated_sample(self, device_id: str) -> ShimmerSample:
        """Generate simulated sensor data"""
        import random

        timestamp = time.time()
        system_time = datetime.now().isoformat()

        # Simulate realistic sensor values
        gsr_conductance = random.uniform(0.1, 10.0)  # microsiemens
        ppg_a13 = random.uniform(1000, 4000)  # ADC units
        accel_x = random.uniform(-2.0, 2.0)  # g
        accel_y = random.uniform(-2.0, 2.0)  # g
        accel_z = random.uniform(0.8, 1.2)  # g (gravity)
        battery_percentage = random.randint(20, 100)

        return ShimmerSample(
            timestamp=timestamp,
            system_time=system_time,
            device_id=device_id,
            gsr_conductance=gsr_conductance,
            ppg_a13=ppg_a13,
            accel_x=accel_x,
            accel_y=accel_y,
            accel_z=accel_z,
            battery_percentage=battery_percentage,
        )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and test ShimmerManager
    manager = ShimmerManager()

    try:
        # Initialize
        if manager.initialize():
            print("ShimmerManager initialized successfully")

            # Scan for devices
            devices = manager.scan_and_pair_devices()
            print(f"Found devices: {devices}")

            # Connect to devices
            if devices and manager.connect_devices(devices):
                print("Connected to devices")

                # Configure channels
                channels = {"GSR", "PPG_A13", "Accel_X", "Accel_Y", "Accel_Z"}
                for device_id in manager.device_status:
                    manager.set_enabled_channels(device_id, channels)

                # Start streaming
                if manager.start_streaming():
                    print("Streaming started")

                    # Start recording
                    session_id = f"test_session_{int(time.time())}"
                    if manager.start_recording(session_id):
                        print(f"Recording started for session: {session_id}")

                        # Record for 10 seconds
                        time.sleep(10)

                        # Stop recording
                        manager.stop_recording()
                        print("Recording stopped")

                    # Stop streaming
                    manager.stop_streaming()
                    print("Streaming stopped")

            # Get final status
            status = manager.get_shimmer_status()
            for device_id, device_status in status.items():
                print(
                    f"Device {device_id}: {device_status.samples_recorded} samples recorded"
                )

    finally:
        # Clean up
        manager.cleanup()
        print("ShimmerManager cleanup completed")
