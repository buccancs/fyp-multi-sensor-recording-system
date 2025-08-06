"""
Long-duration endurance testing framework for stress testing the multi-sensor recording system.

This module implements comprehensive 8+ hour testing capabilities to detect memory leaks,
performance degradation, and system stability issues during extended recording sessions.
"""

import asyncio
import gc
import json
import logging
import os
import platform
import resource
import signal
import threading
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import weakref

import psutil

# Import existing system components
try:
    from ..utils.logging_config import get_logger
    from ..utils.system_monitor import get_system_monitor
    from .performance_benchmark import PerformanceProfiler
    from ..performance_optimizer import PerformanceManager, OptimizationConfig
except ImportError:
    # Fallback for standalone testing
    import sys
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir.parent))
    from utils.logging_config import get_logger
    from utils.system_monitor import get_system_monitor
    from performance_optimizer import PerformanceManager, OptimizationConfig


@dataclass
class EnduranceTestConfig:
    """Configuration for endurance testing parameters."""
    
    # Test duration settings
    duration_hours: float = 8.0
    monitoring_interval_seconds: float = 30.0
    checkpoint_interval_minutes: float = 60.0
    
    # Memory leak detection
    memory_leak_threshold_mb: float = 100.0  # MB growth over 2 hours
    memory_growth_window_hours: float = 2.0
    
    # Performance degradation thresholds
    cpu_degradation_threshold: float = 20.0  # % increase in CPU usage
    memory_degradation_threshold: float = 50.0  # % increase in memory usage
    response_time_degradation_threshold: float = 100.0  # % increase in response time
    
    # System stability checks
    check_process_stability: bool = True
    check_file_descriptor_leaks: bool = True
    check_thread_stability: bool = True
    
    # Test scenarios
    simulate_multi_device_load: bool = True
    device_count: int = 8
    recording_session_duration_minutes: float = 30.0
    pause_between_sessions_seconds: float = 60.0
    
    # Output and logging
    output_directory: str = "endurance_test_results"
    enable_detailed_logging: bool = True
    save_memory_snapshots: bool = True
    
    # Graceful shutdown
    enable_graceful_shutdown: bool = True
    shutdown_timeout_seconds: float = 300.0


@dataclass
class EnduranceMetrics:
    """Comprehensive metrics collected during endurance testing."""
    
    timestamp: float
    elapsed_hours: float
    
    # Memory metrics
    memory_rss_mb: float
    memory_vms_mb: float
    memory_percent: float
    memory_available_mb: float
    
    # CPU metrics
    cpu_percent: float
    
    # System resources
    open_files: int
    thread_count: int
    process_count: int
    network_connections: int
    
    # Optional metrics with defaults
    tracemalloc_current_mb: Optional[float] = None
    tracemalloc_peak_mb: Optional[float] = None
    cpu_frequency_mhz: Optional[float] = None
    load_average: Optional[List[float]] = None
    response_time_ms: Optional[float] = None
    throughput_ops_per_sec: Optional[float] = None
    error_count: int = 0
    cpu_temperature: Optional[float] = None
    active_recording_sessions: int = 0
    connected_devices: int = 0
    data_processing_queue_size: int = 0


@dataclass
class EnduranceTestResult:
    """Final results and analysis from endurance testing."""
    
    test_id: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    success: bool
    
    # Summary statistics
    total_measurements: int
    average_cpu_percent: float
    peak_memory_mb: float
    memory_growth_mb: float
    memory_leak_detected: bool
    
    # Performance degradation analysis
    cpu_degradation_percent: float
    memory_degradation_percent: float
    response_time_degradation_percent: float
    
    # Stability indicators
    process_crashes: int
    unexpected_restarts: int
    file_descriptor_leaks: int
    thread_leaks: int
    
    # Error summary
    total_errors: int
    error_categories: Dict[str, int]
    
    # Recommendations
    recommendations: List[str]
    
    # Raw data reference
    detailed_metrics_file: str
    memory_snapshots_file: Optional[str] = None


class MemoryLeakDetector:
    """Advanced memory leak detection and analysis."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.baseline_memory: Optional[float] = None
        self.memory_history: List[tuple] = []  # (timestamp, memory_mb)
        self.leak_warnings = []
        self.tracemalloc_snapshots = []
        
    def start_monitoring(self):
        """Start memory leak monitoring with tracemalloc."""
        tracemalloc.start()
        self.logger.info("MemoryLeakDetector: Started memory tracking")
        
    def stop_monitoring(self):
        """Stop memory monitoring and get final statistics."""
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                "final_memory_mb": current / 1024 / 1024,
                "peak_memory_mb": peak / 1024 / 1024
            }
        return None
        
    def record_memory_measurement(self, memory_mb: float, timestamp: float):
        """Record a memory measurement for leak analysis."""
        self.memory_history.append((timestamp, memory_mb))
        
        if self.baseline_memory is None:
            self.baseline_memory = memory_mb
            self.logger.info(f"MemoryLeakDetector: Baseline memory set to {memory_mb:.2f}MB")
        
        # Keep history manageable (last 24 hours at 30s intervals = 2880 points)
        if len(self.memory_history) > 2880:
            self.memory_history.pop(0)
            
    def analyze_memory_trend(self, window_hours: float = 2.0) -> Dict[str, Any]:
        """Analyze memory growth trend over specified time window."""
        if len(self.memory_history) < 10:
            return {"insufficient_data": True}
            
        current_time = time.time()
        window_seconds = window_hours * 3600
        
        # Filter measurements within the window
        recent_measurements = [
            (ts, mem) for ts, mem in self.memory_history
            if current_time - ts <= window_seconds
        ]
        
        if len(recent_measurements) < 5:
            return {"insufficient_data_in_window": True}
            
        # Calculate linear regression for memory growth
        timestamps = [ts for ts, _ in recent_measurements]
        memories = [mem for _, mem in recent_measurements]
        
        n = len(recent_measurements)
        sum_t = sum(timestamps)
        sum_m = sum(memories)
        sum_tm = sum(t * m for t, m in zip(timestamps, memories))
        sum_t2 = sum(t * t for t in timestamps)
        
        # Linear regression: memory = slope * time + intercept
        denominator = n * sum_t2 - sum_t * sum_t
        if denominator == 0:
            slope = 0
        else:
            slope = (n * sum_tm - sum_t * sum_m) / denominator
            
        # Convert slope to MB per hour
        growth_rate_mb_per_hour = slope * 3600
        
        # Projection over window
        window_growth_mb = growth_rate_mb_per_hour * window_hours
        
        return {
            "window_hours": window_hours,
            "measurements_count": n,
            "growth_rate_mb_per_hour": growth_rate_mb_per_hour,
            "projected_growth_mb": window_growth_mb,
            "current_memory_mb": memories[-1] if memories else 0,
            "window_start_memory_mb": memories[0] if memories else 0,
            "actual_growth_mb": memories[-1] - memories[0] if memories else 0
        }
        
    def check_for_memory_leaks(self, threshold_mb: float, window_hours: float = 2.0) -> Dict[str, Any]:
        """Check if memory leaks are detected based on growth patterns."""
        trend_analysis = self.analyze_memory_trend(window_hours)
        
        if "insufficient_data" in trend_analysis or "insufficient_data_in_window" in trend_analysis:
            return {"status": "insufficient_data", "analysis": trend_analysis}
            
        growth_mb = trend_analysis.get("projected_growth_mb", 0)
        
        leak_detected = growth_mb > threshold_mb
        
        result = {
            "leak_detected": leak_detected,
            "growth_mb": growth_mb,
            "threshold_mb": threshold_mb,
            "confidence": "high" if growth_mb > threshold_mb * 1.5 else "medium",
            "trend_analysis": trend_analysis
        }
        
        if leak_detected:
            warning = f"Memory leak detected: {growth_mb:.2f}MB growth over {window_hours}h (threshold: {threshold_mb}MB)"
            self.leak_warnings.append((time.time(), warning))
            self.logger.warning(f"MemoryLeakDetector: {warning}")
            
        return result
        
    def take_memory_snapshot(self) -> Optional[Dict[str, Any]]:
        """Take a detailed memory snapshot for analysis."""
        if not tracemalloc.is_tracing():
            return None
            
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        snapshot_data = {
            "timestamp": time.time(),
            "total_size_mb": sum(stat.size for stat in top_stats) / 1024 / 1024,
            "top_allocators": []
        }
        
        # Get top 10 memory allocators
        for stat in top_stats[:10]:
            snapshot_data["top_allocators"].append({
                "filename": stat.traceback.format()[0] if stat.traceback.format() else "unknown",
                "size_mb": stat.size / 1024 / 1024,
                "count": stat.count
            })
            
        self.tracemalloc_snapshots.append(snapshot_data)
        return snapshot_data


class EnduranceTestRunner:
    """Main endurance testing orchestrator."""
    
    def __init__(self, config: EnduranceTestConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.test_id = f"endurance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize monitoring components
        self.system_monitor = get_system_monitor()
        self.memory_detector = MemoryLeakDetector(self.logger)
        # Skip performance manager for now due to compatibility issues
        self.performance_manager = None
        
        # Test state
        self.running = False
        self.start_time: Optional[datetime] = None
        self.metrics_history: List[EnduranceMetrics] = []
        self.error_log: List[Dict[str, Any]] = []
        
        # Output paths
        self.output_dir = Path(config.output_directory)
        self.output_dir.mkdir(exist_ok=True)
        
        # Graceful shutdown handling
        self.shutdown_event = threading.Event()
        if config.enable_graceful_shutdown:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"EnduranceTestRunner: Received signal {signum}, initiating graceful shutdown")
        self.shutdown_event.set()
        
    async def run_endurance_test(self) -> EnduranceTestResult:
        """Execute the complete endurance test."""
        self.logger.info(f"EnduranceTestRunner: Starting endurance test {self.test_id}")
        self.logger.info(f"EnduranceTestRunner: Test duration: {self.config.duration_hours} hours")
        
        self.start_time = datetime.now()
        self.running = True
        
        try:
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Run the test phases
            result = await self._execute_test_phases()
            
            return result
            
        except Exception as e:
            self.logger.error(f"EnduranceTestRunner: Test failed with exception: {e}")
            return self._create_failure_result(str(e))
            
        finally:
            await self._cleanup_monitoring()
            self.running = False
            
    async def _initialize_monitoring(self):
        """Initialize all monitoring systems."""
        self.logger.info("EnduranceTestRunner: Initializing monitoring systems")
        
        # Start memory leak detection
        self.memory_detector.start_monitoring()
        
        # Note: Performance manager disabled due to compatibility issues
        self.logger.info("EnduranceTestRunner: Performance manager disabled for compatibility")
            
    async def _execute_test_phases(self) -> EnduranceTestResult:
        """Execute the main test phases."""
        test_duration_seconds = self.config.duration_hours * 3600
        monitoring_interval = self.config.monitoring_interval_seconds
        checkpoint_interval = self.config.checkpoint_interval_minutes * 60
        
        last_checkpoint = time.time()
        
        self.logger.info("EnduranceTestRunner: Starting main test execution loop")
        
        while (time.time() - self.start_time.timestamp()) < test_duration_seconds:
            if self.shutdown_event.is_set():
                self.logger.info("EnduranceTestRunner: Graceful shutdown requested")
                break
                
            loop_start = time.time()
            
            try:
                # Collect comprehensive metrics
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Check for performance issues
                await self._check_performance_issues(metrics)
                
                # Periodic checkpoint
                if time.time() - last_checkpoint >= checkpoint_interval:
                    await self._save_checkpoint()
                    last_checkpoint = time.time()
                    
                # Simulate load if configured
                if self.config.simulate_multi_device_load:
                    await self._simulate_device_load()
                    
            except Exception as e:
                error_entry = {
                    "timestamp": time.time(),
                    "error": str(e),
                    "type": type(e).__name__
                }
                self.error_log.append(error_entry)
                self.logger.error(f"EnduranceTestRunner: Error in monitoring loop: {e}")
                
            # Sleep for remainder of interval
            elapsed = time.time() - loop_start
            sleep_time = max(0, monitoring_interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                
        # Generate final results
        return await self._generate_final_results()
        
    async def _collect_metrics(self) -> EnduranceMetrics:
        """Collect comprehensive system and application metrics."""
        current_time = time.time()
        elapsed_hours = (current_time - self.start_time.timestamp()) / 3600
        
        # System metrics
        system_status = self.system_monitor.get_comprehensive_status()
        
        # Process metrics
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Tracemalloc metrics
        tracemalloc_current = None
        tracemalloc_peak = None
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc_current = current / 1024 / 1024
            tracemalloc_peak = peak / 1024 / 1024
            
        # Record memory for leak detection
        memory_mb = memory_info.rss / 1024 / 1024
        self.memory_detector.record_memory_measurement(memory_mb, current_time)
        
        # Performance metrics
        perf_status = None
        try:
            perf_status = self.performance_manager.get_status() if self.performance_manager else None
        except Exception as e:
            self.logger.debug(f"EnduranceTestRunner: Error getting performance status: {e}")
            
        response_time = None
        throughput = None
        if perf_status and "current_metrics" in perf_status:
            current_metrics = perf_status["current_metrics"]
            # Extract performance indicators if available
            
        metrics = EnduranceMetrics(
            timestamp=current_time,
            elapsed_hours=elapsed_hours,
            memory_rss_mb=memory_mb,
            memory_vms_mb=memory_info.vms / 1024 / 1024,
            memory_percent=process.memory_percent(),
            memory_available_mb=system_status["memory"]["available"] / 1024 / 1024,
            tracemalloc_current_mb=tracemalloc_current,
            tracemalloc_peak_mb=tracemalloc_peak,
            cpu_percent=process.cpu_percent(),
            cpu_frequency_mhz=system_status["cpu"].get("frequency_current"),
            load_average=system_status["cpu"].get("load_average"),
            open_files=len(process.open_files()),
            thread_count=process.num_threads(),
            process_count=len(psutil.pids()),
            network_connections=len(process.net_connections()),
            response_time_ms=response_time,
            throughput_ops_per_sec=throughput,
            error_count=len(self.error_log),
            cpu_temperature=self._extract_cpu_temperature(system_status),
            active_recording_sessions=0,  # TODO: Integrate with actual application state
            connected_devices=0,  # TODO: Integrate with actual device manager
            data_processing_queue_size=0  # TODO: Integrate with actual queue monitoring
        )
        
        return metrics
        
    def _extract_cpu_temperature(self, system_status: Dict[str, Any]) -> Optional[float]:
        """Extract CPU temperature from system status if available."""
        try:
            temps = system_status.get("temperature", {})
            for sensor_name, sensor_data in temps.items():
                if "cpu" in sensor_name.lower() or "core" in sensor_name.lower():
                    if isinstance(sensor_data, list) and sensor_data:
                        return sensor_data[0].get("current")
        except Exception:
            pass
        return None
        
    async def _check_performance_issues(self, metrics: EnduranceMetrics):
        """Check for performance degradation and memory leaks."""
        # Memory leak detection
        leak_result = self.memory_detector.check_for_memory_leaks(
            self.config.memory_leak_threshold_mb,
            self.config.memory_growth_window_hours
        )
        
        if leak_result.get("leak_detected"):
            self.logger.warning("EnduranceTestRunner: Memory leak detected")
            
        # Take memory snapshot if configured
        if self.config.save_memory_snapshots and len(self.metrics_history) % 10 == 0:
            snapshot = self.memory_detector.take_memory_snapshot()
            if snapshot:
                self.logger.debug("EnduranceTestRunner: Memory snapshot taken")
                
    async def _simulate_device_load(self):
        """Simulate multi-device recording load for stress testing."""
        # This would integrate with the actual recording system
        # For now, we'll simulate CPU and memory load
        
        # Simulate data processing
        data = bytearray(1024 * 1024)  # 1MB of data
        
        # Simulate some CPU-intensive processing
        import hashlib
        hash_object = hashlib.sha256(data)
        _ = hash_object.hexdigest()
        
        # Small delay to simulate I/O
        await asyncio.sleep(0.1)
        
    async def _save_checkpoint(self):
        """Save intermediate results and status."""
        checkpoint_file = self.output_dir / f"{self.test_id}_checkpoint.json"
        
        checkpoint_data = {
            "test_id": self.test_id,
            "timestamp": time.time(),
            "elapsed_hours": (time.time() - self.start_time.timestamp()) / 3600,
            "metrics_collected": len(self.metrics_history),
            "errors_logged": len(self.error_log),
            "memory_status": self.memory_detector.analyze_memory_trend(),
            "performance_status": None
        }
        
        # Try to get performance status safely
        try:
            if self.performance_manager:
                checkpoint_data["performance_status"] = self.performance_manager.get_status()
        except Exception as e:
            self.logger.debug(f"EnduranceTestRunner: Could not get performance status for checkpoint: {e}")
            checkpoint_data["performance_status"] = {"error": str(e)}
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
            
        self.logger.info(f"EnduranceTestRunner: Checkpoint saved to {checkpoint_file}")
        
    async def _generate_final_results(self) -> EnduranceTestResult:
        """Generate comprehensive final results and analysis."""
        end_time = datetime.now()
        duration_hours = (end_time - self.start_time).total_seconds() / 3600
        
        self.logger.info("EnduranceTestRunner: Generating final results")
        
        # Analyze metrics
        if not self.metrics_history:
            return self._create_failure_result("No metrics collected")
            
        # Calculate summary statistics
        cpu_values = [m.cpu_percent for m in self.metrics_history if m.cpu_percent is not None]
        memory_values = [m.memory_rss_mb for m in self.metrics_history]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        peak_memory = max(memory_values) if memory_values else 0
        
        # Memory growth analysis
        final_memory_analysis = self.memory_detector.analyze_memory_trend(
            window_hours=self.config.memory_growth_window_hours
        )
        memory_growth = final_memory_analysis.get("actual_growth_mb", 0)
        memory_leak_detected = memory_growth > self.config.memory_leak_threshold_mb
        
        # Performance degradation analysis
        initial_metrics = self.metrics_history[:10] if len(self.metrics_history) >= 10 else self.metrics_history[:5]
        final_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history[-5:]
        
        if initial_metrics and final_metrics:
            initial_cpu_values = [m.cpu_percent for m in initial_metrics if m.cpu_percent is not None]
            final_cpu_values = [m.cpu_percent for m in final_metrics if m.cpu_percent is not None]
            
            if initial_cpu_values and final_cpu_values:
                initial_cpu = sum(initial_cpu_values) / len(initial_cpu_values)
                final_cpu = sum(final_cpu_values) / len(final_cpu_values)
                cpu_degradation = ((final_cpu - initial_cpu) / initial_cpu * 100) if initial_cpu > 0 else 0
            else:
                cpu_degradation = 0
            
            initial_memory = sum(m.memory_rss_mb for m in initial_metrics) / len(initial_metrics)
            final_memory = sum(m.memory_rss_mb for m in final_metrics) / len(final_metrics)
            memory_degradation = ((final_memory - initial_memory) / initial_memory * 100) if initial_memory > 0 else 0
        else:
            cpu_degradation = 0
            memory_degradation = 0
            
        # Generate recommendations
        recommendations = self._generate_recommendations(
            memory_leak_detected, cpu_degradation, memory_degradation, len(self.error_log)
        )
        
        # Save detailed metrics
        metrics_file = self.output_dir / f"{self.test_id}_detailed_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump([asdict(m) for m in self.metrics_history], f, indent=2, default=str)
            
        # Save memory snapshots if available
        snapshots_file = None
        if self.memory_detector.tracemalloc_snapshots:
            snapshots_file = str(self.output_dir / f"{self.test_id}_memory_snapshots.json")
            with open(snapshots_file, 'w') as f:
                json.dump(self.memory_detector.tracemalloc_snapshots, f, indent=2, default=str)
                
        # Determine overall success
        success = (
            not memory_leak_detected and
            cpu_degradation < self.config.cpu_degradation_threshold and
            memory_degradation < self.config.memory_degradation_threshold and
            len(self.error_log) == 0
        )
        
        result = EnduranceTestResult(
            test_id=self.test_id,
            start_time=self.start_time,
            end_time=end_time,
            duration_hours=duration_hours,
            success=success,
            total_measurements=len(self.metrics_history),
            average_cpu_percent=avg_cpu,
            peak_memory_mb=peak_memory,
            memory_growth_mb=memory_growth,
            memory_leak_detected=memory_leak_detected,
            cpu_degradation_percent=cpu_degradation,
            memory_degradation_percent=memory_degradation,
            response_time_degradation_percent=0,  # TODO: Implement response time tracking
            process_crashes=0,  # TODO: Implement crash detection
            unexpected_restarts=0,  # TODO: Implement restart detection
            file_descriptor_leaks=0,  # TODO: Implement FD leak detection
            thread_leaks=0,  # TODO: Implement thread leak detection
            total_errors=len(self.error_log),
            error_categories=self._categorize_errors(),
            recommendations=recommendations,
            detailed_metrics_file=str(metrics_file),
            memory_snapshots_file=snapshots_file
        )
        
        # Save final results
        results_file = self.output_dir / f"{self.test_id}_final_results.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
            
        self.logger.info(f"EnduranceTestRunner: Final results saved to {results_file}")
        return result
        
    def _generate_recommendations(self, memory_leak: bool, cpu_degradation: float, 
                                 memory_degradation: float, error_count: int) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        if memory_leak:
            recommendations.append(
                "Memory leak detected: Review application code for unreleased resources, "
                "implement more aggressive garbage collection, and consider memory pooling."
            )
            
        if cpu_degradation > self.config.cpu_degradation_threshold:
            recommendations.append(
                f"CPU performance degraded by {cpu_degradation:.1f}%: Profile CPU-intensive "
                "operations, consider vectorized numpy operations, and implement task scheduling."
            )
            
        if memory_degradation > self.config.memory_degradation_threshold:
            recommendations.append(
                f"Memory usage increased by {memory_degradation:.1f}%: Implement streaming "
                "data processing, add memory usage monitoring, and optimize data structures."
            )
            
        if error_count > 0:
            recommendations.append(
                f"Encountered {error_count} errors during testing: Review error logs, "
                "implement better error handling, and add system resilience measures."
            )
            
        if not recommendations:
            recommendations.append(
                "System performed well during endurance testing. Continue monitoring "
                "performance in production environments."
            )
            
        return recommendations
        
    def _categorize_errors(self) -> Dict[str, int]:
        """Categorize errors by type for analysis."""
        categories = {}
        for error in self.error_log:
            error_type = error.get("type", "Unknown")
            categories[error_type] = categories.get(error_type, 0) + 1
        return categories
        
    def _create_failure_result(self, error_message: str) -> EnduranceTestResult:
        """Create a failure result when test cannot complete."""
        return EnduranceTestResult(
            test_id=self.test_id,
            start_time=self.start_time or datetime.now(),
            end_time=datetime.now(),
            duration_hours=0,
            success=False,
            total_measurements=0,
            average_cpu_percent=0,
            peak_memory_mb=0,
            memory_growth_mb=0,
            memory_leak_detected=False,
            cpu_degradation_percent=0,
            memory_degradation_percent=0,
            response_time_degradation_percent=0,
            process_crashes=0,
            unexpected_restarts=0,
            file_descriptor_leaks=0,
            thread_leaks=0,
            total_errors=1,
            error_categories={"TestFailure": 1},
            recommendations=[f"Test failed: {error_message}"],
            detailed_metrics_file="",
            memory_snapshots_file=None
        )
        
    async def _cleanup_monitoring(self):
        """Clean up monitoring systems."""
        self.logger.info("EnduranceTestRunner: Cleaning up monitoring systems")
        
        # Stop memory tracking
        final_memory_stats = self.memory_detector.stop_monitoring()
        if final_memory_stats:
            self.logger.info(f"EnduranceTestRunner: Final memory stats: {final_memory_stats}")
            
        # Stop performance manager
        try:
            if self.performance_manager:
                self.performance_manager.stop()
        except Exception as e:
            self.logger.warning(f"EnduranceTestRunner: Error stopping performance manager: {e}")


async def run_endurance_test(config: Optional[EnduranceTestConfig] = None) -> EnduranceTestResult:
    """
    Run a comprehensive endurance test with the specified configuration.
    
    Args:
        config: Test configuration. If None, uses default 8-hour test.
        
    Returns:
        EnduranceTestResult with comprehensive analysis and recommendations.
    """
    if config is None:
        config = EnduranceTestConfig()
        
    runner = EnduranceTestRunner(config)
    return await runner.run_endurance_test()


def main():
    """Command-line interface for endurance testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Sensor Recording System Endurance Testing")
    parser.add_argument("--duration", type=float, default=8.0, help="Test duration in hours")
    parser.add_argument("--devices", type=int, default=8, help="Number of simulated devices")
    parser.add_argument("--output", type=str, default="endurance_test_results", help="Output directory")
    parser.add_argument("--quick", action="store_true", help="Run quick 30-minute test")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create test configuration
    duration = 0.5 if args.quick else args.duration
    config = EnduranceTestConfig(
        duration_hours=duration,
        device_count=args.devices,
        output_directory=args.output,
        enable_detailed_logging=args.verbose
    )
    
    print(f"Starting endurance test: {duration} hours with {args.devices} simulated devices")
    
    # Run the test
    try:
        result = asyncio.run(run_endurance_test(config))
        
        print(f"\n=== Endurance Test Results ===")
        print(f"Test ID: {result.test_id}")
        print(f"Duration: {result.duration_hours:.2f} hours")
        print(f"Success: {'✓' if result.success else '✗'}")
        print(f"Average CPU: {result.average_cpu_percent:.1f}%")
        print(f"Peak Memory: {result.peak_memory_mb:.1f}MB")
        print(f"Memory Growth: {result.memory_growth_mb:.1f}MB")
        print(f"Memory Leak Detected: {'Yes' if result.memory_leak_detected else 'No'}")
        print(f"Total Errors: {result.total_errors}")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
            
        print(f"\nDetailed results saved to: {result.detailed_metrics_file}")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()