"""
Performance benchmarking and validation tests for Virtual Test Environment

These tests establish performance baselines and validate system performance
under various load conditions.
"""

import pytest
import asyncio
import time
import psutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

from tests.integration.virtual_environment import (
    VirtualTestConfig,
    VirtualTestRunner,
    VirtualTestScenario,
    SyntheticDataGenerator,
)


@dataclass
class PerformanceBenchmark:
    """Performance benchmark results"""
    test_name: str
    duration_seconds: float
    peak_memory_mb: float
    peak_cpu_percent: float
    average_memory_mb: float
    average_cpu_percent: float
    data_samples_generated: int
    throughput_samples_per_second: float
    device_count: int
    success: bool
    error_message: str = ""


class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.memory_samples = []
        self.cpu_samples = []
        self.monitoring = False
        self.monitor_task = None
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.memory_samples = []
        self.cpu_samples = []
        self.monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return results"""
        self.monitoring = False
        if self.monitor_task:
            await self.monitor_task
        
        if not self.memory_samples or not self.cpu_samples:
            return {
                "peak_memory_mb": 0,
                "peak_cpu_percent": 0,
                "average_memory_mb": 0,
                "average_cpu_percent": 0,
            }
        
        return {
            "peak_memory_mb": max(self.memory_samples),
            "peak_cpu_percent": max(self.cpu_samples),
            "average_memory_mb": sum(self.memory_samples) / len(self.memory_samples),
            "average_cpu_percent": sum(self.cpu_samples) / len(self.cpu_samples),
        }
    
    async def _monitor_loop(self):
        """Background monitoring loop"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                # Get memory usage in MB
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                
                # Get CPU usage percentage
                cpu_percent = process.cpu_percent()
                self.cpu_samples.append(cpu_percent)
                
                await asyncio.sleep(self.sample_interval)
            except Exception:
                # Ignore monitoring errors
                break


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def test_logger(self):
        """Create test logger with minimal output"""
        logger = logging.getLogger("PerformanceTest")
        logger.setLevel(logging.ERROR)  # Minimal logging for performance tests
        return logger
    
    async def _run_performance_test(
        self, 
        config: VirtualTestConfig, 
        test_logger: logging.Logger
    ) -> PerformanceBenchmark:
        """Run a performance test and collect metrics"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            await monitor.start_monitoring()
            
            runner = VirtualTestRunner(config, test_logger)
            metrics = await runner.run_test()
            
            duration = time.time() - start_time
            perf_stats = await monitor.stop_monitoring()
            
            return PerformanceBenchmark(
                test_name=config.test_name,
                duration_seconds=duration,
                peak_memory_mb=perf_stats["peak_memory_mb"],
                peak_cpu_percent=perf_stats["peak_cpu_percent"],
                average_memory_mb=perf_stats["average_memory_mb"],
                average_cpu_percent=perf_stats["average_cpu_percent"],
                data_samples_generated=metrics.data_samples_collected,
                throughput_samples_per_second=metrics.data_samples_collected / duration if duration > 0 else 0,
                device_count=config.device_count,
                success=metrics.overall_passed,
            )
            
        except Exception as e:
            duration = time.time() - start_time
            perf_stats = await monitor.stop_monitoring()
            
            return PerformanceBenchmark(
                test_name=config.test_name,
                duration_seconds=duration,
                peak_memory_mb=perf_stats.get("peak_memory_mb", 0),
                peak_cpu_percent=perf_stats.get("peak_cpu_percent", 0),
                average_memory_mb=perf_stats.get("average_memory_mb", 0),
                average_cpu_percent=perf_stats.get("average_cpu_percent", 0),
                data_samples_generated=0,
                throughput_samples_per_second=0,
                device_count=config.device_count,
                success=False,
                error_message=str(e),
            )
    
    @pytest.mark.asyncio
    async def test_baseline_performance_single_device(self, temp_output_dir, test_logger):
        """Establish baseline performance with single device"""
        config = VirtualTestConfig(
            test_name="baseline_single_device",
            device_count=1,
            test_duration_minutes=0.1,  # 6 seconds
            recording_duration_minutes=0.08,
            output_directory=temp_output_dir,
            gsr_sampling_rate_hz=128,
            simulate_file_transfers=False,
            enable_stress_events=False,
        )
        
        benchmark = await self._run_performance_test(config, test_logger)
        
        # Baseline expectations for single device
        assert benchmark.peak_memory_mb < 200, f"Memory usage too high: {benchmark.peak_memory_mb}MB"
        assert benchmark.duration_seconds < 15, f"Test took too long: {benchmark.duration_seconds}s"
        
        if benchmark.success:
            assert benchmark.throughput_samples_per_second > 50, f"Throughput too low: {benchmark.throughput_samples_per_second}"
    
    @pytest.mark.asyncio
    async def test_scaling_performance_multiple_devices(self, temp_output_dir, test_logger):
        """Test performance scaling with multiple devices"""
        device_counts = [1, 2, 3]
        benchmarks = []
        
        for device_count in device_counts:
            config = VirtualTestConfig(
                test_name=f"scaling_test_{device_count}_devices",
                device_count=device_count,
                test_duration_minutes=0.05,  # 3 seconds
                recording_duration_minutes=0.04,
                output_directory=temp_output_dir,
                gsr_sampling_rate_hz=64,  # Reduced for performance
                simulate_file_transfers=False,
                enable_stress_events=False,
            )
            
            benchmark = await self._run_performance_test(config, test_logger)
            benchmarks.append(benchmark)
        
        # Analyze scaling characteristics
        for i, benchmark in enumerate(benchmarks):
            device_count = device_counts[i]
            
            # Memory should scale reasonably with device count
            expected_max_memory = 50 + (device_count * 50)  # Base + per-device
            assert benchmark.peak_memory_mb < expected_max_memory, \
                f"Memory usage {benchmark.peak_memory_mb}MB too high for {device_count} devices"
            
            # Test should complete in reasonable time
            max_duration = 10 + (device_count * 2)  # Allow more time per device
            assert benchmark.duration_seconds < max_duration, \
                f"Test with {device_count} devices took too long: {benchmark.duration_seconds}s"
    
    @pytest.mark.asyncio
    async def test_data_generation_performance(self):
        """Test synthetic data generation performance"""
        data_generator = SyntheticDataGenerator(seed=42)
        
        # Test GSR batch generation performance
        start_time = time.time()
        gsr_samples = data_generator.generate_gsr_batch(1000)  # 1000 samples
        gsr_generation_time = time.time() - start_time
        
        assert len(gsr_samples) == 1000
        assert gsr_generation_time < 1.0, f"GSR generation too slow: {gsr_generation_time}s"
        
        # Test video frame generation performance
        start_time = time.time()
        for _ in range(10):  # 10 frames
            frame = data_generator.generate_rgb_frame()
            assert len(frame) > 1000  # Should generate substantial data
        rgb_generation_time = time.time() - start_time
        
        assert rgb_generation_time < 5.0, f"RGB generation too slow: {rgb_generation_time}s"
        
        # Test thermal frame generation
        start_time = time.time()
        for _ in range(10):  # 10 frames
            thermal = data_generator.generate_thermal_frame()
            assert len(thermal) == 64 * 48 * 2  # Expected thermal data size
        thermal_generation_time = time.time() - start_time
        
        assert thermal_generation_time < 2.0, f"Thermal generation too slow: {thermal_generation_time}s"
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, temp_output_dir, test_logger):
        """Test for memory leaks during repeated operations"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Run multiple short tests to check for memory leaks
        for i in range(3):
            config = VirtualTestConfig(
                test_name=f"memory_leak_test_{i}",
                device_count=1,
                test_duration_minutes=0.02,  # Very short
                recording_duration_minutes=0.01,
                output_directory=temp_output_dir,
                gsr_sampling_rate_hz=32,
                simulate_file_transfers=False,
                enable_stress_events=False,
            )
            
            try:
                await self._run_performance_test(config, test_logger)
            except Exception:
                # Allow failures but check memory anyway
                pass
            
            # Small delay between tests
            await asyncio.sleep(0.1)
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Allow some memory increase but detect significant leaks
        assert memory_increase < 100, f"Potential memory leak detected: {memory_increase}MB increase"
    
    @pytest.mark.asyncio
    async def test_stress_test_performance(self, temp_output_dir, test_logger):
        """Test performance under stress conditions"""
        config = VirtualTestConfig(
            test_name="stress_test_performance",
            device_count=4,  # More devices
            test_duration_minutes=0.2,  # 12 seconds
            recording_duration_minutes=0.15,
            output_directory=temp_output_dir,
            gsr_sampling_rate_hz=128,  # Full rate
            rgb_fps=30,  # Full rate
            thermal_fps=9,  # Full rate
            simulate_file_transfers=True,  # Enable file transfers
            enable_stress_events=True,  # Enable stress events
        )
        
        benchmark = await self._run_performance_test(config, test_logger)
        
        # Stress test expectations
        max_memory = 400  # MB
        max_duration = 30  # seconds
        
        assert benchmark.peak_memory_mb < max_memory, \
            f"Stress test memory usage too high: {benchmark.peak_memory_mb}MB"
        
        assert benchmark.duration_seconds < max_duration, \
            f"Stress test took too long: {benchmark.duration_seconds}s"
        
        # Should handle some load successfully
        if benchmark.success:
            assert benchmark.throughput_samples_per_second > 100, \
                f"Stress test throughput too low: {benchmark.throughput_samples_per_second}"
    
    def test_configuration_performance_impact(self, temp_output_dir):
        """Test impact of different configuration options on performance estimates"""
        base_config = VirtualTestConfig(
            test_name="config_performance_base",
            device_count=2,
            test_duration_minutes=1.0,
            output_directory=temp_output_dir,
        )
        
        base_memory = base_config.estimate_memory_usage()
        base_data = base_config.estimate_data_volume()
        
        # Test impact of increasing device count
        high_device_config = VirtualTestConfig(
            test_name="config_performance_devices",
            device_count=5,
            test_duration_minutes=1.0,
            output_directory=temp_output_dir,
        )
        
        high_device_memory = high_device_config.estimate_memory_usage()
        assert high_device_memory > base_memory, "Memory should increase with device count"
        
        # Test impact of increasing sample rates
        high_rate_config = VirtualTestConfig(
            test_name="config_performance_rates",
            device_count=2,
            test_duration_minutes=1.0,
            output_directory=temp_output_dir,
            gsr_sampling_rate_hz=256,  # Double rate
            rgb_fps=60,  # Double rate
        )
        
        high_rate_data = high_rate_config.estimate_data_volume()
        assert high_rate_data['total_mb'] > base_data['total_mb'], \
            "Data volume should increase with higher sample rates"
    
    @pytest.mark.asyncio
    async def test_concurrent_test_performance(self, temp_output_dir, test_logger):
        """Test performance when running multiple tests concurrently"""
        # Create multiple test configurations
        configs = []
        for i in range(2):  # Run 2 tests concurrently
            config = VirtualTestConfig(
                test_name=f"concurrent_test_{i}",
                device_count=1,
                test_duration_minutes=0.05,  # 3 seconds each
                recording_duration_minutes=0.04,
                output_directory=temp_output_dir,
                gsr_sampling_rate_hz=64,
                simulate_file_transfers=False,
            )
            configs.append(config)
        
        # Run tests concurrently
        start_time = time.time()
        tasks = [self._run_performance_test(config, test_logger) for config in configs]
        benchmarks = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time
        
        # Analyze concurrent performance
        successful_benchmarks = [b for b in benchmarks if isinstance(b, PerformanceBenchmark)]
        
        # Concurrent execution should be faster than sequential
        assert total_duration < 10, f"Concurrent tests took too long: {total_duration}s"
        
        # At least one test should succeed
        successful_count = sum(1 for b in successful_benchmarks if b.success)
        assert successful_count >= 1, "At least one concurrent test should succeed"


@pytest.mark.performance
class TestPerformanceRegression:
    """Performance regression detection tests"""
    
    PERFORMANCE_THRESHOLDS = {
        "max_memory_mb_single_device": 150,
        "max_duration_seconds_single_device": 12,
        "min_throughput_samples_per_second": 50,
        "max_memory_mb_multi_device": 300,
        "max_duration_seconds_multi_device": 20,
    }
    
    def test_performance_thresholds_documented(self):
        """Ensure performance thresholds are documented and reasonable"""
        # This test documents expected performance characteristics
        thresholds = self.PERFORMANCE_THRESHOLDS
        
        assert thresholds["max_memory_mb_single_device"] > 0
        assert thresholds["max_duration_seconds_single_device"] > 0
        assert thresholds["min_throughput_samples_per_second"] > 0
        
        # Thresholds should be reasonable for CI environments
        assert thresholds["max_memory_mb_single_device"] < 500
        assert thresholds["max_duration_seconds_single_device"] < 30


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])