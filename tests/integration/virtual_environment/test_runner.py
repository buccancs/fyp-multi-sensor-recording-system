"""
Virtual Test Environment Runner

This module provides the main test orchestration functionality for the virtual
test environment. It coordinates multiple virtual devices, manages the PC server,
collects metrics, and validates test outcomes.

Key responsibilities:
- Start/stop PC server in headless test mode
- Spawn and coordinate multiple virtual device clients
- Monitor system performance and collect metrics
- Validate data integrity and synchronisation
- Generate comprehensive test reports
"""
import asyncio
import json
import logging
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
import traceback
import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the virtual_environment directory to the path for direct imports
virtual_env_path = Path(__file__).parent
sys.path.insert(0, str(virtual_env_path))

from PythonApp.network.android_device_manager import AndroidDeviceManager, ShimmerDataSample, SessionInfo
from PythonApp.network.pc_server import PCServer
from virtual_device_client import VirtualDeviceClient, VirtualDeviceConfig
from synthetic_data_generator import SyntheticDataGenerator, estimate_data_volume
from test_config import VirtualTestConfig, VirtualTestScenario
@dataclass
class VirtualTestMetrics:
    """Metrics collected during test execution"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    devices_spawned: int = 0
    devices_connected: int = 0
    devices_completed: int = 0
    device_connection_times: List[float] = field(default_factory=list)
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_data_samples: int = 0
    total_files_transferred: int = 0
    data_throughput_mbps: float = 0.0
    sessions_started: int = 0
    sessions_completed: int = 0
    session_durations: List[float] = field(default_factory=list)
    peak_memory_mb: float = 0.0
    avg_cpu_percent: float = 0.0
    peak_cpu_percent: float = 0.0
    data_integrity_passed: bool = False
    synchronization_passed: bool = False
    performance_passed: bool = False
    overall_passed: bool = False
    error_count: int = 0
    warning_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
@dataclass
class DeviceTestResult:
    """Results for a single virtual device"""
    device_id: str
    success: bool
    connection_time: float
    messages_sent: int = 0
    messages_received: int = 0
    data_samples_sent: int = 0
    files_transferred: int = 0
    uptime_seconds: float = 0.0
    error_message: Optional[str] = None
    final_statistics: Optional[Dict[str, Any]] = None
class VirtualTestRunner:
    """
    Main orchestrator for virtual test environment.
    
    This class manages the complete test lifecycle:
    1. Initialize PC server in headless mode
    2. Spawn virtual device clients
    3. Execute test scenarios (recording sessions)
    4. Monitor performance and collect metrics
    5. Validate results and generate reports
    """
    def __init__(self, config: VirtualTestConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or self._setup_logger()
        self.device_manager: Optional[AndroidDeviceManager] = None
        self.virtual_devices: List[VirtualDeviceClient] = []
        self.device_configs: List[VirtualDeviceConfig] = []
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self._start_time = datetime.now()
        self.device_results: List[DeviceTestResult] = []
        self.performance_monitoring_enabled = True
        self.performance_data: List[Dict[str, Any]] = []
        self.performance_monitor: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.thread_pool = ThreadPoolExecutor(max_workers=config.device_count + 5)
        self.progress_callbacks: List[Callable] = []
        self.metric_callbacks: List[Callable] = []
        self.collected_data_samples: List[ShimmerDataSample] = []
        self.session_events: List[Tuple[str, float, Dict[str, Any]]] = []
        self.logger.info(f"VirtualTestRunner initialized for {config.device_count} devices")
        
    @property
    def metrics(self) -> "VirtualTestMetrics":
        """Get or create test metrics"""
        if not hasattr(self, '_metrics'):
            self._metrics = VirtualTestMetrics(start_time=self._start_time)
        return self._metrics
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the test runner"""
        logger = logging.getLogger(f"VirtualTestRunner-{self.config.test_name}")
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        logger.setLevel(level_map.get(self.config.log_level, logging.INFO))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            if self.config.save_detailed_logs:
                log_file = Path(self.config.output_directory) / f"{self.config.test_name}.log"
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        return logger
    async def run_test(self) -> "VirtualTestMetrics":
        """
        Execute the complete virtual test.
        
        Returns:
            VirtualTestMetrics with complete test results
        """
        try:
            self.logger.info(f"Starting virtual test: {self.config.test_name}")
            self.logger.info(f"Configuration: {self.config.device_count} devices, {self.config.test_duration_minutes} minutes")
            self.start_time = datetime.now()
            self.metrics.start_time = self.start_time
            self.is_running = True
            self._setup_signal_handlers()
            validation_issues = self.config.validate()
            if validation_issues:
                self.logger.warning(f"Configuration issues: {validation_issues}")
                self.metrics.warnings.extend(validation_issues)
                self.metrics.warning_count += len(validation_issues)
            self.logger.info("Phase 1: Initializing PC server")
            await self._initialize_pc_server()
            self.logger.info("Phase 2: Starting performance monitoring")
            self._start_performance_monitoring()
            self.logger.info("Phase 3: Spawning virtual devices")
            await self._spawn_virtual_devices()
            self.logger.info("Phase 4: Executing test scenarios")
            await self._execute_test_scenarios()
            self.logger.info("Phase 5: Finalizing test")
            await self._finalize_test()
            self._validate_results()
            await self._generate_report()
            self.logger.info(f"Test completed successfully in {self.metrics.duration_seconds:.1f}s")
        except Exception as e:
            self.logger.error(f"Test failed with error: {e}")
            self.logger.debug(traceback.format_exc())
            self.metrics.errors.append(str(e))
            self.metrics.error_count += 1
            self.metrics.overall_passed = False
        finally:
            self.is_running = False
            self.stop_event.set()
            await self._cleanup()
        return self.metrics
    async def _initialize_pc_server(self) -> None:
        """Initialize the PC server in headless test mode"""
        try:
            self.device_manager = AndroidDeviceManager(
                server_port=self.config.server_port,
                logger=self.logger.getChild("DeviceManager")
            )
            self.device_manager.add_data_callback(self._on_data_received)
            self.device_manager.add_status_callback(self._on_device_status)
            self.device_manager.add_session_callback(self._on_session_event)
            if not self.device_manager.initialize():
                raise RuntimeError("Failed to initialize PC server")
            self.logger.info(f"PC server started on port {self.config.server_port}")
            await asyncio.sleep(0.5)
        except Exception as e:
            self.logger.error(f"Failed to initialize PC server: {e}")
            raise
    async def _spawn_virtual_devices(self) -> None:
        """Spawn and connect virtual device clients"""
        try:
            for i in range(self.config.device_count):
                device_config = VirtualDeviceConfig(
                    device_id=f"virtual_device_{i+1:03d}",
                    capabilities=self.config.device_capabilities.copy(),
                    server_host=self.config.server_host,
                    server_port=self.config.server_port,
                    gsr_sampling_rate_hz=self.config.gsr_sampling_rate_hz,
                    rgb_fps=self.config.rgb_fps,
                    thermal_fps=self.config.thermal_fps,
                    response_delay_ms=self.config.device_response_delay_ms,
                )
                self.device_configs.append(device_config)
            self.metrics.devices_spawned = len(self.device_configs)
            connection_tasks = []
            for i, config in enumerate(self.device_configs):
                delay = i * self.config.device_connection_delay_seconds
                task = asyncio.create_task(
                    self._connect_device_with_delay(config, delay)
                )
                connection_tasks.append(task)
            connection_results = await asyncio.gather(*connection_tasks, return_exceptions=True)
            for i, result in enumerate(connection_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Device {i+1} connection failed: {result}")
                    self.metrics.errors.append(f"Device {i+1} connection failed: {result}")
                    self.metrics.error_count += 1
                elif result:
                    self.virtual_devices.append(result)
                    self.metrics.devices_connected += 1
            self.logger.info(f"Connected {self.metrics.devices_connected}/{self.metrics.devices_spawned} devices")
            await asyncio.sleep(2.0)
            connected_devices = self.device_manager.get_connected_devices()
            if len(connected_devices) != self.metrics.devices_connected:
                self.logger.warning(
                    f"Device count mismatch: {len(connected_devices)} registered, "
                    f"{self.metrics.devices_connected} connected"
                )
        except Exception as e:
            self.logger.error(f"Failed to spawn virtual devices: {e}")
            raise
    async def _connect_device_with_delay(self, config: VirtualDeviceConfig, delay: float) -> Optional[VirtualDeviceClient]:
        """Connect a single device with optional delay"""
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            device = VirtualDeviceClient(config, self.logger.getChild(config.device_id))
            connection_start = time.time()
            if await device.connect():
                connection_time = time.time() - connection_start
                self.metrics.device_connection_times.append(connection_time)
                self.logger.info(f"Device {config.device_id} connected in {connection_time:.2f}s")
                return device
            else:
                self.logger.error(f"Device {config.device_id} failed to connect")
                return None
        except Exception as e:
            self.logger.error(f"Error connecting device {config.device_id}: {e}")
            return None
    async def _execute_test_scenarios(self) -> None:
        """Execute the main test scenarios"""
        try:
            test_end_time = self.start_time + timedelta(minutes=self.config.test_duration_minutes)
            for session_num in range(self.config.session_count):
                if datetime.now() >= test_end_time or self.stop_event.is_set():
                    break
                session_id = f"{self.config.test_name}_session_{session_num + 1}"
                self.logger.info(f"Starting session {session_num + 1}/{self.config.session_count}: {session_id}")
                await self._execute_recording_session(session_id)
                if session_num < self.config.session_count - 1:
                    pause_time = self.config.pause_between_sessions_seconds
                    self.logger.info(f"Pausing {pause_time}s between sessions")
                    await asyncio.sleep(pause_time)
            remaining_time = (test_end_time - datetime.now()).total_seconds()
            if remaining_time > 0:
                self.logger.info(f"Waiting {remaining_time:.1f}s for test duration to complete")
                await asyncio.sleep(min(remaining_time, 30))
        except Exception as e:
            self.logger.error(f"Error in test scenario execution: {e}")
            raise
    async def _execute_recording_session(self, session_id: str) -> None:
        """Execute a single recording session"""
        try:
            session_start_time = time.time()
            if self.config.auto_start_recording:
                success = self.device_manager.start_session(
                    session_id=session_id,
                    record_shimmer=True,
                    record_video="rgb_video" in self.config.device_capabilities,
                    record_thermal="thermal" in self.config.device_capabilities,
                )
                if success:
                    self.metrics.sessions_started += 1
                    self.logger.info(f"Recording session started: {session_id}")
                    recording_duration = self.config.recording_duration_minutes * 60
                    await asyncio.sleep(recording_duration)
                    if self.device_manager.stop_session():
                        session_duration = time.time() - session_start_time
                        self.metrics.sessions_completed += 1
                        self.metrics.session_durations.append(session_duration)
                        self.logger.info(f"Recording session completed in {session_duration:.1f}s")
                    else:
                        self.logger.error(f"Failed to stop recording session: {session_id}")
                        self.metrics.errors.append(f"Failed to stop session {session_id}")
                        self.metrics.error_count += 1
                else:
                    self.logger.error(f"Failed to start recording session: {session_id}")
                    self.metrics.errors.append(f"Failed to start session {session_id}")
                    self.metrics.error_count += 1
        except Exception as e:
            self.logger.error(f"Error in recording session {session_id}: {e}")
            self.metrics.errors.append(f"Session {session_id} error: {e}")
            self.metrics.error_count += 1
    def _start_performance_monitoring(self) -> None:
        """Start background performance monitoring"""
        if not self.config.enable_performance_monitoring:
            return
        def monitor_performance():
            import psutil
            process = psutil.Process()
            while self.is_running and not self.stop_event.is_set():
                try:
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    cpu_percent = process.cpu_percent()
                    self.metrics.peak_memory_mb = max(self.metrics.peak_memory_mb, memory_mb)
                    self.metrics.peak_cpu_percent = max(self.metrics.peak_cpu_percent, cpu_percent)
                    if memory_mb > self.config.memory_leak_threshold_mb:
                        self.logger.warning(f"High memory usage: {memory_mb:.1f}MB")
                    if cpu_percent > self.config.cpu_usage_threshold_percent:
                        self.logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                    for callback in self.metric_callbacks:
                        try:
                            callback({
                                "timestamp": time.time(),
                                "memory_mb": memory_mb,
                                "cpu_percent": cpu_percent,
                            })
                        except Exception as e:
                            self.logger.debug(f"Metric callback error: {e}")
                    self.stop_event.wait(self.config.monitoring_interval_seconds)
                except Exception as e:
                    self.logger.error(f"Performance monitoring error: {e}")
                    time.sleep(5.0)
        self.performance_monitor = threading.Thread(
            target=monitor_performance,
            name="PerformanceMonitor",
            daemon=True
        )
        self.performance_monitor.start()
        self.logger.info("Performance monitoring started")
    def _on_data_received(self, sample: ShimmerDataSample) -> None:
        """Callback for received data samples"""
        self.collected_data_samples.append(sample)
        self.metrics.total_data_samples += 1
        if self.metrics.total_data_samples % 1000 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            data_rate = self.metrics.total_data_samples / elapsed if elapsed > 0 else 0
            self.logger.debug(f"Data samples: {self.metrics.total_data_samples}, rate: {data_rate:.1f} samples/s")
    def _on_device_status(self, device_id: str, device) -> None:
        """Callback for device status updates"""
        self.logger.debug(f"Status update from {device_id}: recording={device.is_recording}")
    def _on_session_event(self, session: SessionInfo) -> None:
        """Callback for session events"""
        event_type = "session_started" if session.end_time is None else "session_completed"
        self.session_events.append((event_type, time.time(), {
            "session_id": session.session_id,
            "device_count": len(session.participating_devices),
            "data_samples": session.data_samples,
        }))
        if session.end_time:
            duration = session.end_time - session.start_time
            self.logger.info(f"Session completed: {session.session_id}, {duration:.1f}s, {session.data_samples} samples")
    async def _finalize_test(self) -> None:
        """Finalize test and collect final metrics"""
        try:
            self.metrics.end_time = datetime.now()
            self.metrics.duration_seconds = (self.metrics.end_time - self.start_time).total_seconds()
            for device in self.virtual_devices:
                try:
                    stats = device.get_statistics()
                    result = DeviceTestResult(
                        device_id=stats["device_id"],
                        success=stats["is_connected"],
                        connection_time=stats.get("uptime_seconds", 0),
                        messages_sent=stats["messages_sent"],
                        messages_received=stats["messages_received"],
                        data_samples_sent=stats["data_samples_sent"],
                        files_transferred=stats["files_transferred"],
                        uptime_seconds=stats.get("uptime_seconds", 0),
                        final_statistics=stats,
                    )
                    self.device_results.append(result)
                    self.metrics.devices_completed += 1
                except Exception as e:
                    self.logger.error(f"Error collecting device statistics: {e}")
            self.metrics.total_messages_sent = sum(r.messages_sent for r in self.device_results)
            self.metrics.total_messages_received = sum(r.messages_received for r in self.device_results)
            self.metrics.total_files_transferred = sum(r.files_transferred for r in self.device_results)
            if self.metrics.duration_seconds > 0:
                data_volume = self.config.estimate_data_volume()
                self.metrics.data_throughput_mbps = data_volume["total_mb"] / (self.metrics.duration_seconds / 60) / 8
            self.logger.info(f"Final metrics: {self.metrics.total_data_samples} samples, {self.metrics.total_messages_sent} messages sent")
        except Exception as e:
            self.logger.error(f"Error finalizing test: {e}")
    def _validate_results(self) -> None:
        """Validate test results against expected outcomes"""
        try:
            if self.config.validate_data_integrity:
                expected_samples = self._calculate_expected_samples()
                sample_ratio = self.metrics.total_data_samples / expected_samples if expected_samples > 0 else 0
                if sample_ratio >= 0.95:
                    self.metrics.data_integrity_passed = True
                    self.logger.info(f"Data integrity PASSED: {sample_ratio:.1%} of expected samples received")
                else:
                    self.logger.warning(f"Data integrity FAILED: {sample_ratio:.1%} of expected samples received")
                    self.metrics.warnings.append(f"Low data integrity: {sample_ratio:.1%}")
                    self.metrics.warning_count += 1
            else:
                self.metrics.data_integrity_passed = True
            memory_ok = self.metrics.peak_memory_mb <= self.config.memory_leak_threshold_mb
            cpu_ok = self.metrics.peak_cpu_percent <= self.config.cpu_usage_threshold_percent
            self.metrics.performance_passed = memory_ok and cpu_ok
            if not memory_ok:
                self.logger.warning(f"Memory usage exceeded threshold: {self.metrics.peak_memory_mb:.1f}MB")
            if not cpu_ok:
                self.logger.warning(f"CPU usage exceeded threshold: {self.metrics.peak_cpu_percent:.1f}%")
            if self.config.validate_synchronization:
                self.metrics.synchronization_passed = len(self.session_events) > 0
            else:
                self.metrics.synchronization_passed = True
            self.metrics.overall_passed = (
                self.metrics.data_integrity_passed and
                self.metrics.performance_passed and
                self.metrics.synchronization_passed and
                self.metrics.error_count == 0 and
                self.metrics.devices_connected >= self.config.device_count * 0.8
            )
            self.logger.info(f"Validation results: Overall={'PASS' if self.metrics.overall_passed else 'FAIL'}")
        except Exception as e:
            self.logger.error(f"Error validating results: {e}")
            self.metrics.overall_passed = False
    def _calculate_expected_samples(self) -> int:
        """Calculate expected number of data samples"""
        recording_duration_total = sum(self.metrics.session_durations)
        if recording_duration_total == 0:
            recording_duration_total = self.config.recording_duration_minutes * 60 * self.config.session_count
        expected_samples = int(
            recording_duration_total *
            self.config.gsr_sampling_rate_hz *
            self.metrics.devices_connected
        )
        return expected_samples
    async def _generate_report(self) -> None:
        """Generate comprehensive test report"""
        try:
            if not self.config.generate_summary_report:
                return
            report = {
                "test_info": {
                    "name": self.config.test_name,
                    "description": self.config.test_description,
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.metrics.end_time.isoformat() if self.metrics.end_time else None,
                    "duration_seconds": self.metrics.duration_seconds,
                    "configuration": self.config.to_dict(),
                },
                "summary": {
                    "overall_passed": self.metrics.overall_passed,
                    "devices_connected": f"{self.metrics.devices_connected}/{self.metrics.devices_spawned}",
                    "sessions_completed": f"{self.metrics.sessions_completed}/{self.metrics.sessions_started}",
                    "data_samples_collected": self.metrics.total_data_samples,
                    "error_count": self.metrics.error_count,
                    "warning_count": self.metrics.warning_count,
                },
                "performance": {
                    "peak_memory_mb": round(self.metrics.peak_memory_mb, 2),
                    "peak_cpu_percent": round(self.metrics.peak_cpu_percent, 2),
                    "data_throughput_mbps": round(self.metrics.data_throughput_mbps, 2),
                },
                "validation": {
                    "data_integrity_passed": self.metrics.data_integrity_passed,
                    "synchronization_passed": self.metrics.synchronization_passed,
                    "performance_passed": self.metrics.performance_passed,
                },
                "device_results": [
                    {
                        "device_id": r.device_id,
                        "success": r.success,
                        "messages_sent": r.messages_sent,
                        "data_samples_sent": r.data_samples_sent,
                        "files_transferred": r.files_transferred,
                        "uptime_seconds": round(r.uptime_seconds, 2),
                    }
                    for r in self.device_results
                ],
                "errors": self.metrics.errors,
                "warnings": self.metrics.warnings,
            }
            report_file = Path(self.config.output_directory) / f"{self.config.test_name}_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Test report saved: {report_file}")
            if self.config.save_performance_metrics:
                metrics_file = Path(self.config.output_directory) / f"{self.config.test_name}_metrics.json"
                with open(metrics_file, 'w') as f:
                    json.dump({
                        "collected_data_samples": len(self.collected_data_samples),
                        "session_events": self.session_events,
                        "device_connection_times": self.metrics.device_connection_times,
                        "session_durations": self.metrics.session_durations,
                    }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
    async def _cleanup(self) -> None:
        """Cleanup resources"""
        try:
            self.logger.info("Cleaning up test resources...")
            for device in self.virtual_devices:
                try:
                    await device.disconnect()
                except Exception as e:
                    self.logger.debug(f"Error disconnecting device: {e}")
            if self.device_manager:
                self.device_manager.shutdown()
            if self.performance_monitor and self.performance_monitor.is_alive():
                self.stop_event.set()
                self.performance_monitor.join(timeout=5.0)
            try:
                self.thread_pool.shutdown(wait=True)
            except Exception as e:
                self.logger.debug(f"ThreadPoolExecutor already shut down: {e}")
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.stop_event.set()
            self.is_running = False
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    def add_progress_callback(self, callback: Callable) -> None:
        """Add callback for progress updates"""
        self.progress_callbacks.append(callback)
    def add_metric_callback(self, callback: Callable) -> None:
        """Add callback for metric updates"""
        self.metric_callbacks.append(callback)
async def run_test_scenario(scenario: VirtualTestScenario, logger: Optional[logging.Logger] = None) -> "VirtualTestMetrics":
    """
    Run a specific test scenario.
    
    Args:
        scenario: The test scenario to run
        logger: Optional logger instance
        
    Returns:
        VirtualTestMetrics with results
    """
    runner = VirtualTestRunner(scenario.config, logger)
    return await runner.run_test()
async def run_test_matrix(scenarios: List[VirtualTestScenario], logger: Optional[logging.Logger] = None) -> List["VirtualTestMetrics"]:
    """
    Run multiple test scenarios sequentially.
    
    Args:
        scenarios: List of test scenarios to run
        logger: Optional logger instance
        
    Returns:
        List of VirtualTestMetrics, one per scenario
    """
    results = []
    for i, scenario in enumerate(scenarios):
        if logger:
            logger.info(f"Running scenario {i+1}/{len(scenarios)}: {scenario.name}")
        try:
            metrics = await run_test_scenario(scenario, logger)
            results.append(metrics)
            if logger:
                status = "PASSED" if metrics.overall_passed else "FAILED"
                logger.info(f"Scenario {scenario.name} {status} in {metrics.duration_seconds:.1f}s")
        except Exception as e:
            if logger:
                logger.error(f"Scenario {scenario.name} failed with exception: {e}")
            failed_metrics = VirtualTestMetrics(
                start_time=datetime.now(),
                end_time=datetime.now(),
                overall_passed=False,
                error_count=1,
                errors=[str(e)]
            )
            results.append(failed_metrics)
    return results
if __name__ == "__main__":
    import argparse
    def main():
        parser = argparse.ArgumentParser(description="Virtual Test Environment Runner")
        parser.add_argument("--config", type=str, help="Configuration file path")
        parser.add_argument("--scenario", type=str, choices=["quick", "stress", "sync", "ci"],
                          default="quick", help="Predefined test scenario")
        parser.add_argument("--devices", type=int, default=3, help="Number of virtual devices")
        parser.add_argument("--duration", type=float, default=2.0, help="Test duration in minutes")
        parser.add_argument("--output", type=str, help="Output directory")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
        args = parser.parse_args()
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger("VirtualTestRunner")
        if args.config:
            config = VirtualTestConfig.from_json_file(args.config)
        else:
            scenario_map = {
                "quick": VirtualTestScenario.create_quick_test(),
                "stress": VirtualTestScenario.create_stress_test(),
                "sync": VirtualTestScenario.create_synchronization_test(),
                "ci": VirtualTestScenario.create_ci_test(),
            }
            scenario = scenario_map[args.scenario]
            config = scenario.config
            config.device_count = args.devices
            config.test_duration_minutes = args.duration
            if args.output:
                config.output_directory = args.output
        async def run():
            runner = VirtualTestRunner(config, logger)
            metrics = await runner.run_test()
            status = "PASSED" if metrics.overall_passed else "FAILED"
            print(f"\nTest {status}")
            print(f"Duration: {metrics.duration_seconds:.1f}s")
            print(f"Devices: {metrics.devices_connected}/{metrics.devices_spawned}")
            print(f"Data samples: {metrics.total_data_samples}")
            print(f"Errors: {metrics.error_count}")
            if not metrics.overall_passed:
                sys.exit(1)
        asyncio.run(run())
    main()