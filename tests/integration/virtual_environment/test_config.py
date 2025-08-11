"""
Virtual Test Environment Configuration

This module provides configuration classes for the virtual test environment,
allowing easy customization of test scenarios, device simulation parameters,
and validation criteria.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import tempfile
@dataclass
class VirtualTestConfig:
    """
    Configuration for the virtual test environment.
    
    This class centralizes all configuration options for running virtual
    tests, from basic test parameters to detailed device simulation settings.
    """
    test_name: str = "virtual_test"
    test_description: str = "Virtual multi-device GSR recording test"
    test_duration_minutes: float = 5.0
    device_count: int = 3
    server_host: str = "127.0.0.1"
    server_port: int = 9000
    server_timeout_seconds: float = 30.0
    headless_mode: bool = True
    enable_gui: bool = False
    enable_detailed_logging: bool = True
    log_level: str = "INFO"
    device_capabilities: List[str] = field(default_factory=lambda: ["rgb_video", "thermal", "shimmer"])
    device_connection_delay_seconds: float = 1.0
    device_response_delay_ms: int = 50
    auto_start_recording: bool = True
    recording_duration_minutes: float = 2.0
    pause_between_sessions_seconds: float = 10.0
    session_count: int = 1
    gsr_sampling_rate_hz: int = 128
    rgb_fps: int = 30
    thermal_fps: int = 9
    enable_stress_events: bool = True
    stress_event_intensity: float = 0.7
    simulate_file_transfers: bool = True
    video_file_size_mb: float = 50.0
    thermal_file_size_mb: float = 10.0
    file_transfer_chunk_size: int = 8192
    enable_performance_monitoring: bool = True
    monitoring_interval_seconds: float = 5.0
    memory_leak_threshold_mb: float = 100.0
    cpu_usage_threshold_percent: float = 80.0
    validate_data_integrity: bool = True
    validate_synchronization: bool = True
    max_sync_jitter_ms: float = 50.0
    validate_throughput: bool = True
    min_throughput_mbps: float = 1.0
    output_directory: str = ""
    save_detailed_logs: bool = True
    save_performance_metrics: bool = True
    save_raw_data_samples: bool = False
    generate_summary_report: bool = True
    ci_mode: bool = False
    fail_fast: bool = False
    timeout_multiplier: float = 1.0
    use_docker: bool = False
    docker_image: str = "gsr-virtual-test:latest"
    docker_network: str = "bridge"
    def __post_init__(self):
        """Post-initialization validation and defaults"""
        if not self.output_directory:
            timestamp = int(time.time()) if 'time' in globals() else 0
            self.output_directory = str(Path(tempfile.gettempdir()) / f"gsr_virtual_test_{timestamp}")
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        if self.device_count < 1:
            raise ValueError("device_count must be at least 1")
        if self.device_count > 20:
            raise ValueError("device_count should not exceed 20 for stability")
        if self.test_duration_minutes <= 0:
            raise ValueError("test_duration_minutes must be positive")
        if self.recording_duration_minutes > self.test_duration_minutes:
            self.recording_duration_minutes = self.test_duration_minutes * 0.8
        if self.ci_mode and self.timeout_multiplier != 1.0:
            self.server_timeout_seconds *= self.timeout_multiplier
            self.device_connection_delay_seconds *= self.timeout_multiplier
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "VirtualTestConfig":
        """Create config from dictionary"""
        return cls(**config_dict)
    @classmethod
    def from_json_file(cls, file_path: Union[str, Path]) -> "VirtualTestConfig":
        """Load configuration from JSON file"""
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        import dataclasses
        return dataclasses.asdict(self)
    def to_json_file(self, file_path: Union[str, Path]) -> None:
        """Save configuration to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []
        total_gsr_samples_per_sec = self.device_count * self.gsr_sampling_rate_hz
        if total_gsr_samples_per_sec > 10000:
            issues.append(f"Very high GSR data rate: {total_gsr_samples_per_sec} samples/sec total")
        total_video_frames_per_sec = self.device_count * self.rgb_fps
        if total_video_frames_per_sec > 300:
            issues.append(f"Very high video frame rate: {total_video_frames_per_sec} frames/sec total")
        estimated_memory_mb = self.estimate_memory_usage()
        if estimated_memory_mb > 4000:
            issues.append(f"High estimated memory usage: {estimated_memory_mb:.1f} MB")
        try:
            Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create output directory {self.output_directory}: {e}")
        return issues
    def estimate_memory_usage(self) -> float:
        """
        Estimate memory usage for the test configuration.
        
        Returns:
            Estimated memory usage in MB
        """
        base_memory_mb = 50.0
        memory_per_device_mb = 5.0
        gsr_buffer_mb = self.device_count * 0.1
        video_buffer_mb = self.device_count * 2.0
        thermal_buffer_mb = self.device_count * 0.5
        total_mb = (base_memory_mb +
                   (self.device_count * memory_per_device_mb) +
                   gsr_buffer_mb + video_buffer_mb + thermal_buffer_mb)
        return total_mb
    def estimate_data_volume(self) -> Dict[str, float]:
        """
        Estimate total data volume for the test.
        
        Returns:
            Dictionary with data volume estimates
        """
        duration_seconds = self.test_duration_minutes * 60
        gsr_samples_total = duration_seconds * self.gsr_sampling_rate_hz * self.device_count
        gsr_mb = (gsr_samples_total * 12) / (1024 * 1024)
        video_frames_total = duration_seconds * self.rgb_fps * self.device_count
        video_mb = video_frames_total * 0.05
        thermal_frames_total = duration_seconds * self.thermal_fps * self.device_count
        thermal_mb = thermal_frames_total * 0.006
        file_transfer_mb = 0.0
        if self.simulate_file_transfers:
            file_transfer_mb = self.device_count * (self.video_file_size_mb + self.thermal_file_size_mb)
        total_mb = gsr_mb + video_mb + thermal_mb + file_transfer_mb
        return {
            "gsr_mb": round(gsr_mb, 2),
            "video_mb": round(video_mb, 2),
            "thermal_mb": round(thermal_mb, 2),
            "file_transfer_mb": round(file_transfer_mb, 2),
            "total_mb": round(total_mb, 2),
            "duration_seconds": duration_seconds,
            "device_count": self.device_count,
        }
@dataclass
class VirtualTestScenario:
    """
    Predefined test scenario with specific configuration.
    
    Test scenarios provide ready-made configurations for common testing needs.
    """
    name: str
    description: str
    config: VirtualTestConfig
    expected_outcomes: Dict[str, Any] = field(default_factory=dict)
    @classmethod
    def create_quick_test(cls) -> "VirtualTestScenario":
        """Create a quick test scenario (1 minute, 2 devices)"""
        config = VirtualTestConfig(
            test_name="quick_test",
            test_description="Quick functionality test with minimal duration",
            test_duration_minutes=1.0,
            recording_duration_minutes=0.5,
            device_count=2,
            session_count=1,
            enable_stress_events=False,
            simulate_file_transfers=False,
        )
        return cls(
            name="Quick Test",
            description="Fast test for basic functionality validation",
            config=config,
            expected_outcomes={
                "duration_under_seconds": 90,
                "devices_connected": 2,
                "data_samples_min": 50,
                "no_errors": True,
            }
        )
    @classmethod
    def create_stress_test(cls) -> "VirtualTestScenario":
        """Create a stress test scenario (30 minutes, 6 devices)"""
        config = VirtualTestConfig(
            test_name="stress_test",
            test_description="Stress test with multiple devices and high data rates",
            test_duration_minutes=30.0,
            recording_duration_minutes=25.0,
            device_count=6,
            session_count=3,
            enable_stress_events=True,
            stress_event_intensity=0.8,
            simulate_file_transfers=True,
            gsr_sampling_rate_hz=128,
            rgb_fps=30,
            thermal_fps=9,
        )
        return cls(
            name="Stress Test",
            description="High-load test with multiple devices and realistic data rates",
            config=config,
            expected_outcomes={
                "devices_connected": 6,
                "sessions_completed": 3,
                "data_integrity_100_percent": True,
                "max_memory_usage_mb": 500,
                "max_cpu_usage_percent": 70,
            }
        )
    @classmethod
    def create_endurance_test(cls) -> "VirtualTestScenario":
        """Create an endurance test scenario (2 hours, 4 devices)"""
        config = VirtualTestConfig(
            test_name="endurance_test",
            test_description="Long-duration test for stability and memory leak detection",
            test_duration_minutes=120.0,
            recording_duration_minutes=110.0,
            device_count=4,
            session_count=5,
            enable_stress_events=True,
            stress_event_intensity=0.5,
            simulate_file_transfers=True,
            enable_performance_monitoring=True,
            monitoring_interval_seconds=30.0,
            memory_leak_threshold_mb=200.0,
        )
        return cls(
            name="Endurance Test",
            description="Long-duration test for stability validation",
            config=config,
            expected_outcomes={
                "devices_connected": 4,
                "sessions_completed": 5,
                "no_memory_leaks": True,
                "uptime_minutes": 120,
                "stable_performance": True,
            }
        )
    @classmethod
    def create_synchronization_test(cls) -> "VirtualTestScenario":
        """Create a synchronisation validation test"""
        config = VirtualTestConfig(
            test_name="sync_test",
            test_description="Test multi-device synchronisation accuracy",
            test_duration_minutes=10.0,
            recording_duration_minutes=8.0,
            device_count=5,
            session_count=3,
            validate_synchronization=True,
            max_sync_jitter_ms=25.0,
            enable_stress_events=False,
            simulate_file_transfers=False,
        )
        return cls(
            name="Synchronisation Test",
            description="Validate timing synchronisation between devices",
            config=config,
            expected_outcomes={
                "devices_connected": 5,
                "sync_jitter_under_ms": 25,
                "sync_accuracy_validated": True,
                "timing_drift_minimal": True,
            }
        )
    @classmethod
    def create_ci_test(cls) -> "VirtualTestScenario":
        """Create a CI-friendly test scenario"""
        config = VirtualTestConfig(
            test_name="ci_test",
            test_description="CI/CD pipeline test with conservative settings",
            test_duration_minutes=3.0,
            recording_duration_minutes=2.0,
            device_count=3,
            session_count=1,
            ci_mode=True,
            timeout_multiplier=2.0,
            fail_fast=True,
            enable_stress_events=False,
            simulate_file_transfers=True,
            video_file_size_mb=10.0,
            thermal_file_size_mb=2.0,
            enable_detailed_logging=False,
        )
        return cls(
            name="CI Test",
            description="Continuous integration test with conservative settings",
            config=config,
            expected_outcomes={
                "duration_under_seconds": 300,
                "devices_connected": 3,
                "no_timeouts": True,
                "files_transferred": True,
                "exit_code_zero": True,
            }
        )
def load_config_from_env() -> VirtualTestConfig:
    """
    Load configuration from environment variables.
    
    Environment variables override default values using the pattern:
    GSR_TEST_<FIELD_NAME> (e.g., GSR_TEST_DEVICE_COUNT=5)
    """
    config = VirtualTestConfig()
    env_mapping = {
        "device_count": "GSR_TEST_DEVICE_COUNT",
        "test_duration_minutes": "GSR_TEST_DURATION_MINUTES",
        "server_port": "GSR_TEST_SERVER_PORT",
        "ci_mode": "GSR_TEST_CI_MODE",
        "output_directory": "GSR_TEST_OUTPUT_DIR",
        "log_level": "GSR_TEST_LOG_LEVEL",
        "headless_mode": "GSR_TEST_HEADLESS",
    }
    for field_name, env_var in env_mapping.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            field_type = type(getattr(config, field_name))
            if field_type == bool:
                converted_value = env_value.lower() in ('true', '1', 'yes', 'on')
            elif field_type == int:
                converted_value = int(env_value)
            elif field_type == float:
                converted_value = float(env_value)
            else:
                converted_value = env_value
            setattr(config, field_name, converted_value)
    return config
def create_test_matrix() -> List[VirtualTestScenario]:
    """
    Create a matrix of test scenarios for comprehensive validation.
    
    Returns:
        List of test scenarios covering different aspects
    """
    return [
        VirtualTestScenario.create_quick_test(),
        VirtualTestScenario.create_stress_test(),
        VirtualTestScenario.create_synchronization_test(),
        VirtualTestScenario.create_ci_test(),
    ]
def validate_system_requirements(config: VirtualTestConfig) -> Dict[str, Any]:
    """
    Validate that the system meets requirements for the test configuration.
    
    Args:
        config: Test configuration to validate against
        
    Returns:
        Dictionary with validation results
    """
    import psutil
    import shutil
    results = {
        "meets_requirements": True,
        "issues": [],
        "warnings": [],
        "system_info": {},
    }
    try:
        memory = psutil.virtual_memory()
        available_mb = memory.available / (1024 * 1024)
        required_mb = config.estimate_memory_usage()
        results["system_info"]["available_memory_mb"] = available_mb
        results["system_info"]["required_memory_mb"] = required_mb
        if available_mb < required_mb:
            results["meets_requirements"] = False
            results["issues"].append(f"Insufficient memory: need {required_mb:.1f}MB, have {available_mb:.1f}MB")
        elif available_mb < required_mb * 2:
            results["warnings"].append(f"Low memory headroom: {available_mb:.1f}MB available for {required_mb:.1f}MB required")
        cpu_count = psutil.cpu_count()
        recommended_cores = max(2, config.device_count // 2)
        results["system_info"]["cpu_cores"] = cpu_count
        results["system_info"]["recommended_cores"] = recommended_cores
        if cpu_count < recommended_cores:
            results["warnings"].append(f"Few CPU cores: have {cpu_count}, recommend {recommended_cores} for {config.device_count} devices")
        disk_usage = shutil.disk_usage(config.output_directory)
        available_gb = disk_usage.free / (1024**3)
        data_volume = config.estimate_data_volume()
        required_gb = data_volume["total_mb"] / 1024
        results["system_info"]["available_disk_gb"] = available_gb
        results["system_info"]["required_disk_gb"] = required_gb
        if available_gb < required_gb:
            results["meets_requirements"] = False
            results["issues"].append(f"Insufficient disk space: need {required_gb:.2f}GB, have {available_gb:.2f}GB")
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex((config.server_host, config.server_port))
            sock.close()
            if result == 0:
                results["warnings"].append(f"Port {config.server_port} appears to be in use")
        except Exception:
            pass
    except Exception as e:
        results["issues"].append(f"System validation error: {e}")
        results["meets_requirements"] = False
    return results
import time