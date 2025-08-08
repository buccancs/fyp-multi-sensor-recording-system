
import csv
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..utils.logging_config import get_logger
from .device_models import ShimmerSample

class ShimmerDataProcessor:

    def __init__(self):

        self.logger = get_logger(__name__)
        self.data_queues: Dict[str, queue.Queue] = {}
        self.csv_writers: Dict[str, csv.DictWriter] = {}
        self.csv_files: Dict[str, Any] = {}
        self.is_recording = False
        self.data_processing_thread: Optional[threading.Thread] = None
        self.file_writing_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.data_callbacks: List[Callable[[ShimmerSample], None]] = []

        self.sensor_ranges = {
            "gsr_conductance": (0.0, 100.0),
            "ppg_a13": (0.0, 4095.0),
            "accel_x": (-16.0, 16.0),
            "accel_y": (-16.0, 16.0),
            "accel_z": (-16.0, 16.0),
            "gyro_x": (-2000.0, 2000.0),
            "gyro_y": (-2000.0, 2000.0),
            "gyro_z": (-2000.0, 2000.0),
            "battery_percentage": (0, 100),
        }

    def add_data_callback(self, callback: Callable[[ShimmerSample], None]) -> None:

        self.data_callbacks.append(callback)

    def remove_data_callback(self, callback: Callable[[ShimmerSample], None]) -> None:

        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)

    def setup_data_queue(self, device_id: str, buffer_size: int = 1000) -> None:

        self.data_queues[device_id] = queue.Queue(maxsize=buffer_size)

    def start_recording(self, session_id: str, output_directory: Path) -> bool:

        try:
            self.logger.info(f"Starting data recording for session {session_id}")

            output_directory.mkdir(parents=True, exist_ok=True)

            for device_id in self.data_queues.keys():
                self._setup_csv_writer(device_id, session_id, output_directory)

            self.stop_event.clear()
            self.is_recording = True

            self.data_processing_thread = threading.Thread(
                target=self._data_processing_loop, name=f"DataProcessor-{session_id}"
            )
            self.data_processing_thread.start()

            self.file_writing_thread = threading.Thread(
                target=self._file_writing_loop, name=f"FileWriter-{session_id}"
            )
            self.file_writing_thread.start()

            self.logger.info("Data recording started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error starting data recording: {e}")
            return False

    def stop_recording(self) -> bool:

        try:
            self.logger.info("Stopping data recording")

            self.is_recording = False
            self.stop_event.set()

            if self.data_processing_thread and self.data_processing_thread.is_alive():
                self.data_processing_thread.join(timeout=5.0)

            if self.file_writing_thread and self.file_writing_thread.is_alive():
                self.file_writing_thread.join(timeout=5.0)

            self._close_csv_files()

            self.logger.info("Data recording stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping data recording: {e}")
            return False

    def add_sample(self, device_id: str, sample: ShimmerSample) -> bool:

        try:
            if not self.validate_sample_data(sample):
                self.logger.warning(f"Invalid sample data from device {device_id}")
                return False

            if device_id in self.data_queues:
                try:
                    self.data_queues[device_id].put_nowait(sample)
                    return True
                except queue.Full:
                    self.logger.warning(f"Data queue full for device {device_id}")
                    return False
            else:
                self.logger.warning(f"No data queue for device {device_id}")
                return False

        except Exception as e:
            self.logger.error(f"Error adding sample for device {device_id}: {e}")
            return False

    def validate_sample_data(self, sample: ShimmerSample) -> bool:

        try:
            if sample.timestamp <= 0:
                return False

            sensor_checks = [
                ("gsr_conductance", sample.gsr_conductance),
                ("ppg_a13", sample.ppg_a13),
                ("accel_x", sample.accel_x),
                ("accel_y", sample.accel_y),
                ("accel_z", sample.accel_z),
                ("gyro_x", sample.gyro_x),
                ("gyro_y", sample.gyro_y),
                ("gyro_z", sample.gyro_z),
                ("battery_percentage", sample.battery_percentage),
            ]

            for sensor_name, value in sensor_checks:
                if value is not None and sensor_name in self.sensor_ranges:
                    min_val, max_val = self.sensor_ranges[sensor_name]
                    if not min_val <= value <= max_val:
                        self.logger.warning(
                            f"Invalid {sensor_name} value: {value} (expected {min_val}-{max_val})"
                        )
                        return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating sample data: {e}")
            return False

    def _setup_csv_writer(
        self, device_id: str, session_id: str, output_directory: Path
    ) -> None:

        try:
            csv_filename = output_directory / f"{device_id}_{session_id}.csv"
            csv_file = open(csv_filename, "w", newline="")

            fieldnames = [
                "timestamp",
                "system_time",
                "device_id",
                "connection_type",
                "android_device_id",
                "gsr_conductance",
                "ppg_a13",
                "accel_x",
                "accel_y",
                "accel_z",
                "gyro_x",
                "gyro_y",
                "gyro_z",
                "mag_x",
                "mag_y",
                "mag_z",
                "ecg",
                "emg",
                "battery_percentage",
                "signal_strength",
                "session_id",
            ]

            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            self.csv_files[device_id] = csv_file
            self.csv_writers[device_id] = csv_writer

            self.logger.info(f"Set up CSV writer for device {device_id}")

        except Exception as e:
            self.logger.error(f"Error setting up CSV writer for {device_id}: {e}")

    def _close_csv_files(self) -> None:

        for device_id, csv_file in self.csv_files.items():
            try:
                csv_file.close()
                self.logger.info(f"Closed CSV file for device {device_id}")
            except Exception as e:
                self.logger.error(f"Error closing CSV file for {device_id}: {e}")

        self.csv_files.clear()
        self.csv_writers.clear()

    def _data_processing_loop(self) -> None:

        self.logger.info("Starting data processing loop")

        while not self.stop_event.is_set():
            try:
                self._process_all_device_queues()

                time.sleep(0.01)
            except Exception as e:
                self.logger.error(f"Error in data processing loop: {e}")
                time.sleep(0.1)

        self.logger.info("Data processing loop stopped")

    def _process_all_device_queues(self) -> None:

        for device_id, data_queue in self.data_queues.items():
            self._process_device_queue(device_id, data_queue)

    def _process_device_queue(self, device_id: str, data_queue: queue.Queue) -> None:

        try:
            while not data_queue.empty():
                sample = data_queue.get_nowait()
                self._process_single_sample(device_id, sample)
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f"Error processing data for {device_id}: {e}")

    def _process_single_sample(self, device_id: str, sample: ShimmerSample) -> None:

        self._call_data_callbacks(sample)

        if self.is_recording and device_id in self.csv_writers:
            self._write_sample_to_csv(device_id, sample)

    def _call_data_callbacks(self, sample: ShimmerSample) -> None:

        for callback in self.data_callbacks:
            try:
                callback(sample)
            except Exception as e:
                self.logger.error(f"Error in data callback: {e}")

    def _file_writing_loop(self) -> None:

        self.logger.info("Starting file writing loop")

        while not self.stop_event.is_set() or self.is_recording:
            try:

                for csv_file in self.csv_files.values():
                    try:
                        csv_file.flush()
                    except Exception as e:
                        self.logger.error(f"Error flushing CSV file: {e}")

                time.sleep(1.0)

            except Exception as e:
                self.logger.error(f"Error in file writing loop: {e}")
                time.sleep(1.0)

        self.logger.info("File writing loop stopped")

    def _write_sample_to_csv(self, device_id: str, sample: ShimmerSample) -> None:

        try:
            if device_id in self.csv_writers:
                row = {
                    "timestamp": sample.timestamp,
                    "system_time": sample.system_time,
                    "device_id": sample.device_id,
                    "connection_type": sample.connection_type.value,
                    "android_device_id": sample.android_device_id,
                    "gsr_conductance": sample.gsr_conductance,
                    "ppg_a13": sample.ppg_a13,
                    "accel_x": sample.accel_x,
                    "accel_y": sample.accel_y,
                    "accel_z": sample.accel_z,
                    "gyro_x": sample.gyro_x,
                    "gyro_y": sample.gyro_y,
                    "gyro_z": sample.gyro_z,
                    "mag_x": sample.mag_x,
                    "mag_y": sample.mag_y,
                    "mag_z": sample.mag_z,
                    "ecg": sample.ecg,
                    "emg": sample.emg,
                    "battery_percentage": sample.battery_percentage,
                    "signal_strength": sample.signal_strength,
                    "session_id": sample.session_id,
                }

                self.csv_writers[device_id].writerow(row)

        except Exception as e:
            self.logger.error(f"Error writing sample to CSV for {device_id}: {e}")

    def get_queue_size(self, device_id: str) -> int:

        if device_id in self.data_queues:
            return self.data_queues[device_id].qsize()
        return 0

    def clear_queues(self) -> None:

        for device_id, data_queue in self.data_queues.items():
            try:
                while not data_queue.empty():
                    data_queue.get_nowait()
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Error clearing queue for {device_id}: {e}")
