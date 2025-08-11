#!/usr/bin/env python3
"""
Virtual Test Environment - Example Usage Script

This script demonstrates how to use the virtual test environment
components programmatically. It shows various usage patterns and
provides a foundation for custom test implementations.
"""

import asyncio
import logging
import sys
import tempfile
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.virtual_environment import (
    VirtualTestConfig,
    VirtualTestRunner,
    TestScenario,
    VirtualDeviceClient,
    VirtualDeviceConfig,
    SyntheticDataGenerator,
)


async def example_1_basic_data_generation():
    """Example 1: Basic synthetic data generation"""
    print("Example 1: Basic Synthetic Data Generation")
    print("-" * 50)
    
    # Create data generator
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate GSR data samples
    print("Generating GSR samples:")
    for i in range(5):
        gsr_value = generator.generate_gsr_sample()
        print(f"  Sample {i+1}: {gsr_value:.4f} μS")
    
    # Generate batch of samples
    batch = generator.generate_gsr_batch(10)
    print(f"Generated batch of {len(batch)} samples")
    print(f"  Range: {min(batch):.4f} - {max(batch):.4f} μS")
    
    # Generate video frame
    rgb_frame = generator.generate_rgb_frame()
    print(f"Generated RGB frame: {len(rgb_frame)} bytes")
    
    # Generate thermal frame
    thermal_frame = generator.generate_thermal_frame()
    print(f"Generated thermal frame: {len(thermal_frame)} bytes")
    
    # Show statistics
    stats = generator.get_statistics()
    print(f"Generator stats: {stats}")
    
    print("✓ Data generation example completed\n")


async def example_2_virtual_device():
    """Example 2: Single virtual device interaction"""
    print("Example 2: Virtual Device Interaction")
    print("-" * 50)
    
    # Create device configuration
    config = VirtualDeviceConfig(
        device_id="example_device",
        capabilities=["shimmer"],
        server_host="127.0.0.1",
        server_port=9001,  # Use different port
        gsr_sampling_rate_hz=10,  # Lower rate for example
    )
    
    print(f"Created device config: {config.device_id}")
    print(f"Capabilities: {config.capabilities}")
    
    # Create virtual device
    device = VirtualDeviceClient(config)
    
    # Note: This example doesn't actually connect since we'd need a running server
    # In real usage, you would:
    # if await device.connect():
    #     print("Device connected successfully")
    #     await asyncio.sleep(5)  # Let it run for a bit
    #     await device.disconnect()
    
    # Show device statistics
    stats = device.get_statistics()
    print(f"Device stats: {stats}")
    
    print("✓ Virtual device example completed\n")


async def example_3_custom_configuration():
    """Example 3: Custom test configuration"""
    print("Example 3: Custom Test Configuration")
    print("-" * 50)
    
    # Create custom configuration
    config = VirtualTestConfig(
        test_name="example_test",
        test_description="Example custom test configuration",
        device_count=2,
        test_duration_minutes=1.0,
        recording_duration_minutes=0.5,
        
        # Data generation settings
        gsr_sampling_rate_hz=64,  # Lower rate
        rgb_fps=15,  # Lower frame rate
        thermal_fps=5,
        
        # Test settings
        enable_stress_events=False,
        simulate_file_transfers=False,
        enable_performance_monitoring=True,
        
        # Output
        output_directory=tempfile.mkdtemp(),
        save_detailed_logs=True,
        generate_summary_report=True,
    )
    
    print(f"Test configuration: {config.test_name}")
    print(f"Duration: {config.test_duration_minutes} minutes")
    print(f"Devices: {config.device_count}")
    print(f"Output: {config.output_directory}")
    
    # Validate configuration
    issues = config.validate()
    if issues:
        print(f"Configuration issues: {issues}")
    else:
        print("✓ Configuration is valid")
    
    # Show estimates
    memory_est = config.estimate_memory_usage()
    data_est = config.estimate_data_volume()
    print(f"Estimated memory: {memory_est:.1f} MB")
    print(f"Estimated data: {data_est['total_mb']:.1f} MB")
    
    # Save configuration
    config_file = Path(config.output_directory) / "example_config.json"
    config.to_json_file(config_file)
    print(f"Configuration saved to: {config_file}")
    
    print("✓ Custom configuration example completed\n")


async def example_4_predefined_scenarios():
    """Example 4: Using predefined test scenarios"""
    print("Example 4: Predefined Test Scenarios")
    print("-" * 50)
    
    # Create different scenarios
    scenarios = [
        TestScenario.create_quick_test(),
        TestScenario.create_ci_test(),
        TestScenario.create_synchronization_test(),
    ]
    
    for scenario in scenarios:
        print(f"Scenario: {scenario.name}")
        print(f"  Description: {scenario.description}")
        print(f"  Duration: {scenario.config.test_duration_minutes} minutes")
        print(f"  Devices: {scenario.config.device_count}")
        print(f"  Expected outcomes: {list(scenario.expected_outcomes.keys())}")
        print()
    
    print("✓ Predefined scenarios example completed\n")


async def example_5_minimal_test():
    """Example 5: Run a minimal virtual test"""
    print("Example 5: Minimal Virtual Test")
    print("-" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger("ExampleTest")
    
    # Create minimal test configuration
    config = VirtualTestConfig(
        test_name="minimal_example",
        test_description="Minimal example test",
        device_count=1,
        test_duration_minutes=0.1,  # 6 seconds
        recording_duration_minutes=0.05,  # 3 seconds
        output_directory=tempfile.mkdtemp(),
        
        # Disable resource-intensive features
        simulate_file_transfers=False,
        enable_stress_events=False,
        save_detailed_logs=False,
        
        # Lower data rates
        gsr_sampling_rate_hz=32,
        rgb_fps=10,
        thermal_fps=3,
    )
    
    print(f"Running minimal test: {config.test_name}")
    print(f"Duration: {config.test_duration_minutes * 60:.0f} seconds")
    print(f"Output: {config.output_directory}")
    
    try:
        # Create and run test
        runner = VirtualTestRunner(config, logger)
        
        # Add progress callback
        def on_progress(event_data):
            print(f"Progress: {event_data}")
        
        runner.add_progress_callback(on_progress)
        
        # Run the test
        start_time = time.time()
        metrics = await runner.run_test()
        duration = time.time() - start_time
        
        # Show results
        print(f"\nTest completed in {duration:.1f}s")
        print(f"Overall passed: {metrics.overall_passed}")
        print(f"Devices connected: {metrics.devices_connected}")
        print(f"Data samples: {metrics.total_data_samples}")
        print(f"Sessions completed: {metrics.sessions_completed}")
        
        if metrics.errors:
            print(f"Errors: {metrics.errors}")
        
        # Check for report file
        report_files = list(Path(config.output_directory).glob("*_report.json"))
        if report_files:
            print(f"Report saved: {report_files[0]}")
        
        return metrics.overall_passed
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def example_6_monitoring_callbacks():
    """Example 6: Using monitoring callbacks"""
    print("Example 6: Monitoring Callbacks")
    print("-" * 50)
    
    # Create configuration
    config = VirtualTestConfig(
        test_name="monitoring_example",
        device_count=2,
        test_duration_minutes=0.2,  # 12 seconds
        output_directory=tempfile.mkdtemp(),
        enable_performance_monitoring=True,
        monitoring_interval_seconds=2.0,
    )
    
    # Setup logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    logger = logging.getLogger("MonitoringExample")
    
    # Create runner
    runner = VirtualTestRunner(config, logger)
    
    # Add monitoring callbacks
    metric_count = 0
    
    def on_metric_update(metric_data):
        nonlocal metric_count
        metric_count += 1
        memory_mb = metric_data.get('memory_mb', 0)
        cpu_percent = metric_data.get('cpu_percent', 0)
        print(f"Metrics #{metric_count}: Memory={memory_mb:.1f}MB, CPU={cpu_percent:.1f}%")
    
    progress_count = 0
    
    def on_progress_update(progress_data):
        nonlocal progress_count
        progress_count += 1
        print(f"Progress #{progress_count}: {progress_data}")
    
    runner.add_metric_callback(on_metric_update)
    runner.add_progress_callback(on_progress_update)
    
    try:
        print("Starting monitored test...")
        metrics = await runner.run_test()
        
        print(f"\nMonitoring completed:")
        print(f"  Metric updates: {metric_count}")
        print(f"  Progress updates: {progress_count}")
        print(f"  Test passed: {metrics.overall_passed}")
        print(f"  Peak memory: {metrics.peak_memory_mb:.1f}MB")
        print(f"  Peak CPU: {metrics.peak_cpu_percent:.1f}%")
        
        return metrics.overall_passed
        
    except Exception as e:
        print(f"Monitored test failed: {e}")
        return False


async def main():
    """Main example runner"""
    print("Virtual Test Environment - Usage Examples")
    print("=" * 60)
    print()
    
    examples = [
        ("Data Generation", example_1_basic_data_generation),
        ("Virtual Device", example_2_virtual_device),
        ("Custom Configuration", example_3_custom_configuration),
        ("Predefined Scenarios", example_4_predefined_scenarios),
        ("Minimal Test", example_5_minimal_test),
        ("Monitoring Callbacks", example_6_monitoring_callbacks),
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            print(f"Running {name} example...")
            result = await example_func()
            results[name] = result if result is not None else True
            print()
        except Exception as e:
            print(f"❌ {name} example failed: {e}")
            results[name] = False
            print()
    
    # Summary
    print("=" * 60)
    print("EXAMPLE SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:25} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All examples completed successfully!")
        print()
        print("Next steps:")
        print("- Try running: python test_runner.py --scenario quick --devices 2 --duration 1.0")
        print("- Explore: ./run_virtual_test.sh --help")
        print("- Read: README.md for comprehensive documentation")
    else:
        print("❌ Some examples failed. Check the output above for details.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)