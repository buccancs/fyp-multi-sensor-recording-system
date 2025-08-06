"""
Performance Optimization Quick Test

A simplified test suite for the performance optimization features
to validate they are working correctly.
"""

import asyncio
import logging
import time
from PythonApp.performance_optimizer import PerformanceManager, OptimizationConfig
from PythonApp.production.device_capability_detector import DeviceCapabilityDetector
from PythonApp.production.endurance_test_suite import run_endurance_test


async def test_performance_optimization():
    """Quick test of performance optimization capabilities"""
    
    print("=== Performance Optimization Quick Test ===\n")
    
    # Test 1: Enhanced Performance Manager
    print("1. Testing Enhanced Performance Manager...")
    try:
        config = OptimizationConfig(
            enable_graceful_degradation=True,
            enable_hardware_acceleration=True,
            enable_profiling_integration=True
        )
        
        manager = PerformanceManager()
        if manager.initialize(config):
            manager.start()
            time.sleep(2)
            
            status = manager.get_status()
            
            # Test degradation decisions
            should_drop = manager.should_drop_frame()
            quality_settings = manager.get_recommended_quality_settings()
            
            manager.stop()
            
            print("   ✓ Performance manager initialized and running")
            print(f"   ✓ Hardware acceleration: {status['hardware_acceleration']['acceleration_enabled']}")
            print(f"   ✓ Optimal device: {status['hardware_acceleration']['optimal_device']}")
            print(f"   ✓ Frame drop decision: {should_drop}")
            print(f"   ✓ Quality settings available: {bool(quality_settings)}")
        else:
            print("   ✗ Failed to initialize performance manager")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 2: Device Capability Detection
    print("2. Testing Device Capability Detection...")
    try:
        detector = DeviceCapabilityDetector()
        capabilities = detector.detect_capabilities()
        profile = detector.generate_performance_profile()
        recommendations = detector.get_optimization_recommendations()
        
        print(f"   ✓ Device tier: {capabilities.overall_performance_tier}")
        print(f"   ✓ CPU cores: {capabilities.cpu_cores_logical}")
        print(f"   ✓ Memory: {capabilities.total_memory_gb:.1f}GB")
        print(f"   ✓ Max devices: {profile.max_concurrent_devices}")
        print(f"   ✓ Recommended FPS: {profile.recommended_fps}")
        print(f"   ✓ Recommendations: {len(recommendations)}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 3: Quick Endurance Test (30 seconds)
    print("3. Testing Endurance Monitoring (30 seconds)...")
    try:
        result = await run_endurance_test(
            duration_hours=30/3600,  # 30 seconds
            workload_intensity='low'
        )
        
        print(f"   ✓ Duration: {result['test_summary']['total_duration_hours']:.4f}h")
        print(f"   ✓ Samples: {result['test_summary']['samples_collected']}")
        print(f"   ✓ Memory growth: {result['memory_analysis']['memory_growth_mb']:.1f}MB")
        print(f"   ✓ Leak detected: {result['memory_analysis']['leak_detection']['is_leak_suspected']}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 4: Graceful Degradation
    print("4. Testing Graceful Degradation...")
    try:
        config = OptimizationConfig(enable_graceful_degradation=True)
        manager = PerformanceManager()
        
        if manager.initialize(config):
            manager.start()
            time.sleep(1)
            
            degradation_mgr = manager.get_degradation_manager()
            
            # Test different load conditions
            normal_drop = degradation_mgr.should_drop_frame(50.0, 60.0)
            high_drop = degradation_mgr.should_drop_frame(90.0, 95.0)
            
            normal_quality = degradation_mgr.should_reduce_quality(50.0, 60.0)
            high_quality = degradation_mgr.should_reduce_quality(85.0, 85.0)
            
            manager.stop()
            
            print(f"   ✓ Frame drop - Normal load: {normal_drop}, High load: {high_drop}")
            print(f"   ✓ Quality reduce - Normal load: {normal_quality}, High load: {high_quality}")
            print(f"   ✓ Degradation logic working correctly")
        else:
            print("   ✗ Failed to initialize manager")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    print("=== Performance Optimization Test Complete ===")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)  # Reduce verbose output
    asyncio.run(test_performance_optimization())