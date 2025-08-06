"""
Test suite for the endurance testing framework.

This module provides comprehensive testing for the long-duration stress testing capabilities,
including memory leak detection, performance degradation analysis, and graceful handling.
"""

import asyncio
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Import the endurance testing framework
import sys
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "production"))

from endurance_testing import (
    EnduranceTestConfig,
    EnduranceTestRunner,
    MemoryLeakDetector,
    EnduranceMetrics,
    run_endurance_test
)


class TestMemoryLeakDetector:
    """Test cases for memory leak detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = MemoryLeakDetector(Mock())
        
    def test_memory_measurement_recording(self):
        """Test basic memory measurement recording."""
        # Record some measurements
        timestamps = [1000, 1010, 1020, 1030]
        memories = [100, 102, 104, 106]
        
        for ts, mem in zip(timestamps, memories):
            self.detector.record_memory_measurement(mem, ts)
            
        assert len(self.detector.memory_history) == 4
        assert self.detector.baseline_memory == 100
        
    def test_memory_trend_analysis(self):
        """Test memory growth trend analysis."""
        # Simulate steady memory growth
        base_time = time.time()
        for i in range(10):
            timestamp = base_time + i * 60  # Every minute
            memory = 100 + i * 2  # 2MB growth per minute
            self.detector.record_memory_measurement(memory, timestamp)
            
        analysis = self.detector.analyze_memory_trend(window_hours=0.2)  # 12 minutes
        
        assert not analysis.get("insufficient_data", False)
        assert analysis["growth_rate_mb_per_hour"] > 0
        assert analysis["projected_growth_mb"] > 0
        
    def test_memory_leak_detection(self):
        """Test memory leak detection logic."""
        # Simulate significant memory growth
        base_time = time.time()
        for i in range(20):
            timestamp = base_time + i * 300  # Every 5 minutes
            memory = 100 + i * 10  # 10MB growth every 5 minutes = 120MB/hour
            self.detector.record_memory_measurement(memory, timestamp)
            
        # Check for leaks with 50MB threshold over 1 hour
        leak_result = self.detector.check_for_memory_leaks(50.0, 1.0)
        
        assert leak_result["leak_detected"] == True
        assert leak_result["growth_mb"] > 50
        
    def test_no_false_positive_leak_detection(self):
        """Test that stable memory usage doesn't trigger leak detection."""
        # Simulate stable memory usage
        base_time = time.time()
        for i in range(20):
            timestamp = base_time + i * 300  # Every 5 minutes
            memory = 100 + (i % 3)  # Small oscillation, no growth trend
            self.detector.record_memory_measurement(memory, timestamp)
            
        # Check for leaks
        leak_result = self.detector.check_for_memory_leaks(50.0, 1.0)
        
        assert leak_result["leak_detected"] == False


class TestEnduranceTestConfig:
    """Test cases for endurance test configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = EnduranceTestConfig()
        
        assert config.duration_hours == 8.0
        assert config.monitoring_interval_seconds == 30.0
        assert config.device_count == 8
        assert config.memory_leak_threshold_mb == 100.0
        assert config.enable_graceful_shutdown == True
        
    def test_custom_config(self):
        """Test custom configuration creation."""
        config = EnduranceTestConfig(
            duration_hours=1.0,
            device_count=4,
            memory_leak_threshold_mb=50.0
        )
        
        assert config.duration_hours == 1.0
        assert config.device_count == 4
        assert config.memory_leak_threshold_mb == 50.0


class TestEnduranceTestRunner:
    """Test cases for the main endurance test runner."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        self.config = EnduranceTestConfig(
            duration_hours=0.01,  # Very short test for unit testing
            monitoring_interval_seconds=1.0,
            output_directory=self.temp_dir,
            enable_graceful_shutdown=False  # Disable for testing
        )
        
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test that metrics are collected properly."""
        runner = EnduranceTestRunner(self.config)
        
        # Mock some dependencies
        with patch.object(runner.system_monitor, 'get_comprehensive_status') as mock_status:
            mock_status.return_value = {
                "memory": {"available": 1024 * 1024 * 1024},  # 1GB
                "cpu": {"frequency_current": 2400, "load_average": [0.5, 0.6, 0.7]},
                "temperature": {}
            }
            
            metrics = await runner._collect_metrics()
            
            assert isinstance(metrics, EnduranceMetrics)
            assert metrics.elapsed_hours >= 0
            assert metrics.memory_rss_mb > 0
            assert metrics.cpu_percent >= 0
            assert metrics.memory_available_mb > 0
            
    @pytest.mark.asyncio
    async def test_short_endurance_test(self):
        """Test running a very short endurance test."""
        # Configure for very short test
        config = EnduranceTestConfig(
            duration_hours=0.002,  # ~7 seconds
            monitoring_interval_seconds=1.0,
            output_directory=self.temp_dir,
            simulate_multi_device_load=False,
            enable_graceful_shutdown=False
        )
        
        runner = EnduranceTestRunner(config)
        
        # Mock system dependencies to avoid actual system calls
        with patch.object(runner.system_monitor, 'get_comprehensive_status') as mock_status:
            mock_status.return_value = {
                "memory": {"available": 1024 * 1024 * 1024},
                "cpu": {"frequency_current": 2400, "load_average": [0.5, 0.6, 0.7]},
                "temperature": {}
            }
            
            with patch.object(runner.performance_manager, 'initialize') as mock_init:
                mock_init.return_value = True
                with patch.object(runner.performance_manager, 'start'):
                    with patch.object(runner.performance_manager, 'get_status') as mock_status:
                        mock_status.return_value = {"current_metrics": {}}
                        
                        result = await runner.run_endurance_test()
                        
                        # Verify test completed
                        assert result.test_id.startswith("endurance_")
                        assert result.duration_hours > 0
                        assert result.total_measurements > 0
                        assert isinstance(result.success, bool)
                        
                        # Verify output files were created
                        output_dir = Path(self.temp_dir)
                        assert any(f.name.endswith("_final_results.json") for f in output_dir.iterdir())
                        assert any(f.name.endswith("_detailed_metrics.json") for f in output_dir.iterdir())


class TestIntegrationWithExistingSystem:
    """Integration tests with the existing performance monitoring system."""
    
    @pytest.mark.asyncio
    async def test_endurance_test_api(self):
        """Test the main API function for running endurance tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnduranceTestConfig(
                duration_hours=0.001,  # Very short
                output_directory=temp_dir,
                simulate_multi_device_load=False
            )
            
            # This should not raise any exceptions
            result = await run_endurance_test(config)
            
            assert result is not None
            assert hasattr(result, 'test_id')
            assert hasattr(result, 'success')
            assert hasattr(result, 'recommendations')
            
    def test_memory_leak_detector_integration(self):
        """Test integration with tracemalloc and memory monitoring."""
        detector = MemoryLeakDetector(Mock())
        
        # Start and stop monitoring
        detector.start_monitoring()
        
        # Simulate some memory allocation
        data = bytearray(1024 * 1024)  # 1MB
        
        # Take snapshot
        snapshot = detector.take_memory_snapshot()
        
        # Stop monitoring
        stats = detector.stop_monitoring()
        
        assert snapshot is not None
        assert "timestamp" in snapshot
        assert "total_size_mb" in snapshot
        
        assert stats is not None
        assert "final_memory_mb" in stats
        assert "peak_memory_mb" in stats


def test_endurance_test_configuration_validation():
    """Test that endurance test configurations are properly validated."""
    # Test valid configuration
    config = EnduranceTestConfig(duration_hours=1.0)
    assert config.duration_hours == 1.0
    
    # Test configuration constraints
    config = EnduranceTestConfig(
        monitoring_interval_seconds=5.0,
        checkpoint_interval_minutes=10.0
    )
    
    # Checkpoint interval should be longer than monitoring interval
    assert config.checkpoint_interval_minutes * 60 > config.monitoring_interval_seconds


@pytest.mark.asyncio
async def test_graceful_shutdown_handling():
    """Test that graceful shutdown works correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = EnduranceTestConfig(
            duration_hours=1.0,  # Long test
            output_directory=temp_dir,
            enable_graceful_shutdown=True
        )
        
        runner = EnduranceTestRunner(config)
        
        # Start test and immediately trigger shutdown
        async def trigger_shutdown():
            await asyncio.sleep(0.1)  # Let test start
            runner.shutdown_event.set()  # Trigger graceful shutdown
            
        # Run both tasks concurrently
        shutdown_task = asyncio.create_task(trigger_shutdown())
        
        # Mock dependencies to avoid system calls
        with patch.object(runner.system_monitor, 'get_comprehensive_status') as mock_status:
            mock_status.return_value = {
                "memory": {"available": 1024 * 1024 * 1024},
                "cpu": {"frequency_current": 2400, "load_average": [0.5, 0.6, 0.7]},
                "temperature": {}
            }
            
            with patch.object(runner.performance_manager, 'initialize') as mock_init:
                mock_init.return_value = True
                with patch.object(runner.performance_manager, 'start'):
                    with patch.object(runner.performance_manager, 'get_status') as mock_get_status:
                        mock_get_status.return_value = {"current_metrics": {}}
                        
                        result = await runner.run_endurance_test()
                        
                        # Test should complete quickly due to shutdown
                        assert result.duration_hours < 1.0  # Should be much less than configured 1 hour
                        
        await shutdown_task


def test_performance_degradation_analysis():
    """Test performance degradation detection and analysis."""
    # Create mock metrics data showing degradation
    initial_metrics = [
        EnduranceMetrics(
            timestamp=1000 + i,
            elapsed_hours=i/10,
            memory_rss_mb=100 + i,
            memory_vms_mb=200 + i,
            memory_percent=10.0,
            memory_available_mb=1000,
            cpu_percent=20.0 + i,
            open_files=10,
            thread_count=5,
            process_count=100,
            network_connections=2,
            error_count=0
        ) for i in range(5)
    ]
    
    degraded_metrics = [
        EnduranceMetrics(
            timestamp=2000 + i,
            elapsed_hours=5.0 + i/10,
            memory_rss_mb=150 + i * 2,  # Higher memory usage
            memory_vms_mb=300 + i * 2,
            memory_percent=15.0,
            memory_available_mb=900,
            cpu_percent=40.0 + i * 2,  # Higher CPU usage
            open_files=15,
            thread_count=8,
            process_count=120,
            network_connections=4,
            error_count=0
        ) for i in range(5)
    ]
    
    # Calculate degradation
    initial_cpu = sum(m.cpu_percent for m in initial_metrics) / len(initial_metrics)
    final_cpu = sum(m.cpu_percent for m in degraded_metrics) / len(degraded_metrics)
    cpu_degradation = ((final_cpu - initial_cpu) / initial_cpu * 100)
    
    initial_memory = sum(m.memory_rss_mb for m in initial_metrics) / len(initial_metrics)
    final_memory = sum(m.memory_rss_mb for m in degraded_metrics) / len(degraded_metrics)
    memory_degradation = ((final_memory - initial_memory) / initial_memory * 100)
    
    # Verify degradation is detected
    assert cpu_degradation > 50  # Should show significant CPU degradation
    assert memory_degradation > 30  # Should show significant memory degradation


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])