#!/usr/bin/env python3
"""
Virtual Test Environment - Quick Test Script

This script provides a simple way to test the virtual environment functionality
without running the full test suite. It's useful for development and debugging.
"""

import asyncio
import logging
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.virtual_environment import (
    VirtualTestConfig,
    VirtualTestRunner, 
    VirtualTestScenario,
    VirtualDeviceClient,
    VirtualDeviceConfig,
    SyntheticDataGenerator
)


async def test_basic_functionality():
    """Test basic virtual device client functionality"""
    print("Testing basic virtual device functionality...")
    
    # Test synthetic data generation
    print("1. Testing synthetic data generation...")
    data_gen = SyntheticDataGenerator(seed=42)
    
    # Generate some GSR samples
    gsr_samples = [data_gen.generate_gsr_sample() for _ in range(10)]
    print(f"   Generated {len(gsr_samples)} GSR samples: {gsr_samples[:3]}...")
    
    # Generate video frame
    rgb_frame = data_gen.generate_rgb_frame()
    print(f"   Generated RGB frame: {len(rgb_frame)} bytes")
    
    # Generate thermal frame  
    thermal_frame = data_gen.generate_thermal_frame()
    print(f"   Generated thermal frame: {len(thermal_frame)} bytes")
    
    print("   ✓ Synthetic data generation working")
    
    # Test configuration
    print("2. Testing configuration...")
    config = VirtualTestConfig(
        test_name="basic_test",
        device_count=2,
        test_duration_minutes=0.5,
        recording_duration_minutes=0.2,
        output_directory=tempfile.mkdtemp()
    )
    
    validation_issues = config.validate()
    if validation_issues:
        print(f"   Configuration issues: {validation_issues}")
    else:
        print("   ✓ Configuration valid")
    
    # Test estimation functions
    memory_est = config.estimate_memory_usage()
    data_est = config.estimate_data_volume()
    print(f"   Estimated memory usage: {memory_est:.1f} MB")
    print(f"   Estimated data volume: {data_est['total_mb']:.1f} MB")
    
    print("   ✓ Configuration working")
    
    print("Basic functionality test completed successfully!")


async def test_quick_scenario():
    """Test a quick scenario end-to-end"""
    print("\nTesting quick scenario end-to-end...")
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("QuickTest")
    
    # Create a minimal test scenario
    scenario = VirtualTestScenario.create_quick_test()
    
    # Override for even quicker test
    scenario.config.test_duration_minutes = 0.2
    scenario.config.recording_duration_minutes = 0.1
    scenario.config.device_count = 2
    scenario.config.output_directory = tempfile.mkdtemp()
    
    print(f"Running scenario: {scenario.name}")
    print(f"Devices: {scenario.config.device_count}")
    print(f"Duration: {scenario.config.test_duration_minutes} minutes")
    
    try:
        # Run the test
        runner = VirtualTestRunner(scenario.config, logger)
        metrics = await runner.run_test()
        
        # Check results
        if metrics.overall_passed:
            print("✓ Quick scenario test PASSED")
            print(f"  Duration: {metrics.duration_seconds:.1f}s")
            print(f"  Devices connected: {metrics.devices_connected}")
            print(f"  Data samples: {metrics.total_data_samples}")
            print(f"  Sessions completed: {metrics.sessions_completed}")
        else:
            print("✗ Quick scenario test FAILED")
            print(f"  Errors: {metrics.error_count}")
            print(f"  Warnings: {metrics.warning_count}")
            for error in metrics.errors[:3]:  # Show first 3 errors
                print(f"    Error: {error}")
        
        return metrics.overall_passed
        
    except Exception as e:
        print(f"✗ Quick scenario test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_device_communication():
    """Test direct device communication"""
    print("\nTesting direct device communication...")
    
    try:
        # Create device config
        device_config = VirtualDeviceConfig(
            device_id="test_device_001",
            capabilities=["shimmer"],
            server_host="127.0.0.1",
            server_port=9001,  # Use different port to avoid conflicts
            gsr_sampling_rate_hz=10,  # Lower rate for testing
        )
        
        print(f"Testing device: {device_config.device_id}")
        print(f"Capabilities: {device_config.capabilities}")
        
        # Note: This test would need a running PC server to work properly
        # For now, just test device creation and basic functionality
        
        device = VirtualDeviceClient(device_config)
        stats = device.get_statistics()
        
        print(f"Device created successfully:")
        print(f"  Device ID: {stats['device_id']}")
        print(f"  Capabilities: {stats['capabilities']}")
        print(f"  Connected: {stats['is_connected']}")
        
        print("✓ Device communication test completed (without server)")
        return True
        
    except Exception as e:
        print(f"✗ Device communication test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("Virtual Test Environment - Quick Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Basic functionality
    try:
        await test_basic_functionality()
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        all_passed = False
    
    # Test 2: Device communication
    try:
        result = await test_device_communication()
        all_passed = all_passed and result
    except Exception as e:
        print(f"✗ Device communication test failed: {e}")
        all_passed = False
    
    # Test 3: Quick scenario (most comprehensive)
    try:
        result = await test_quick_scenario()
        all_passed = all_passed and result
    except Exception as e:
        print(f"✗ Quick scenario test failed: {e}")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests PASSED - Virtual environment is working!")
        return 0
    else:
        print("✗ Some tests FAILED - Check output above for details")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)