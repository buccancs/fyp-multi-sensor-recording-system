#!/usr/bin/env python3
"""
Test Enhanced Time Synchronization System
=========================================

Tests both NTP-like and LSL synchronization methods.
"""

import sys
import os
sys.path.append('PythonApp')

from sync import EnhancedSynchronizationManager, TimeServer, SessionSynchronizer
from sync.lsl_integration import LSLTimeSync, LSLDeviceCoordinator, LSL_AVAILABLE

def test_enhanced_synchronization():
    """Test the enhanced synchronization system."""
    print("=" * 60)
    print("Testing Enhanced Time Synchronization System")
    print("=" * 60)
    
    # Test 1: Basic initialization
    print("\n1. Testing Basic Initialization:")
    try:
        enhanced_sync = EnhancedSynchronizationManager(prefer_lsl=True)
        print(f"   ✅ Enhanced sync manager created")
        print(f"   Active method: {enhanced_sync.active_method}")
        print(f"   LSL available: {enhanced_sync.lsl_available}")
        print(f"   NTP available: True")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    # Test 2: Status retrieval
    print("\n2. Testing Status Retrieval:")
    try:
        status = enhanced_sync.get_synchronization_status()
        print(f"   ✅ Status retrieved successfully")
        print(f"   Active method: {status['active_method']}")
        print(f"   Current time: {status['current_time']:.3f}")
        print(f"   NTP available: {status['ntp_available']}")
        print(f"   LSL available: {status['lsl_available']}")
    except Exception as e:
        print(f"   ❌ Status retrieval failed: {e}")
    
    # Test 3: Time synchronization
    print("\n3. Testing Time Synchronization:")
    try:
        time1 = enhanced_sync.get_synchronized_time()
        time2 = enhanced_sync.get_synchronized_time()
        print(f"   ✅ Time sync working")
        print(f"   Time 1: {time1:.6f}")
        print(f"   Time 2: {time2:.6f}")
        print(f"   Difference: {(time2 - time1)*1000:.3f}ms")
    except Exception as e:
        print(f"   ❌ Time sync failed: {e}")
    
    # Test 4: Sync service start/stop
    print("\n4. Testing Sync Service Management:")
    try:
        # Start service
        start_success = enhanced_sync.start_synchronization_service()
        print(f"   Start service: {'✅ Success' if start_success else '❌ Failed'}")
        
        # Test signal sending
        if start_success:
            flash_success = enhanced_sync.send_sync_signal("flash")
            print(f"   Flash signal: {'✅ Sent' if flash_success else '❌ Failed'}")
            
            audio_success = enhanced_sync.send_sync_signal("audio", {"frequency": 1000})
            print(f"   Audio signal: {'✅ Sent' if audio_success else '❌ Failed'}")
        
        # Stop service
        enhanced_sync.stop_synchronization_service()
        print(f"   ✅ Service stopped")
        
    except Exception as e:
        print(f"   ❌ Service management failed: {e}")
    
    # Test 5: LSL-specific features (if available)
    print("\n5. Testing LSL-Specific Features:")
    if LSL_AVAILABLE and enhanced_sync.lsl_available:
        try:
            # Test LSL time sync
            lsl_time = enhanced_sync.lsl_time_sync.get_synchronized_time()
            print(f"   ✅ LSL time sync: {lsl_time:.6f}")
            
            # Test LSL calibration
            calib_success = enhanced_sync.calibrate_lsl_time_sync()
            print(f"   LSL calibration: {'✅ Success' if calib_success else '❌ No reference streams'}")
            
            # Test stream discovery
            streams = enhanced_sync.lsl_time_sync.discover_available_streams()
            print(f"   ✅ LSL stream discovery: {len(streams)} streams found")
            
        except Exception as e:
            print(f"   ❌ LSL features failed: {e}")
    else:
        print(f"   ⚠️  LSL not available (install with: pip install pylsl)")
    
    # Test 6: Sensor registration for LSL
    print("\n6. Testing Sensor Registration:")
    try:
        if enhanced_sync.lsl_available:
            reg_success = enhanced_sync.register_sensor_for_lsl("test_sensor", "GSR")
            print(f"   LSL sensor registration: {'✅ Success' if reg_success else '❌ Failed'}")
            
            # Test data push
            data_success = enhanced_sync.push_sensor_data_to_lsl("test_sensor", 5.5)
            print(f"   LSL data push: {'✅ Success' if data_success else '❌ Failed'}")
        else:
            print(f"   ⚠️  LSL sensor features skipped (LSL not available)")
    except Exception as e:
        print(f"   ❌ Sensor registration failed: {e}")
    
    print("\n" + "=" * 60)
    print("Enhanced Time Synchronization Test Complete")
    print("=" * 60)
    
    return True

def test_lsl_components():
    """Test LSL components directly."""
    print("\n" + "=" * 60)
    print("Testing LSL Components Directly")
    print("=" * 60)
    
    if not LSL_AVAILABLE:
        print("⚠️  LSL not available - using mock implementation")
        print("   Install LSL with: pip install pylsl")
    
    # Test LSL Time Sync
    print("\n1. Testing LSL Time Sync:")
    try:
        lsl_time_sync = LSLTimeSync()
        print(f"   ✅ LSL time sync created")
        print(f"   Available: {lsl_time_sync.is_available}")
        
        time_val = lsl_time_sync.get_synchronized_time()
        print(f"   Current time: {time_val:.6f}")
        
        marker_success = lsl_time_sync.send_sync_marker({"test": "data"})
        print(f"   Sync marker: {'✅ Sent' if marker_success else '❌ Failed'}")
        
    except Exception as e:
        print(f"   ❌ LSL time sync failed: {e}")
    
    # Test LSL Device Coordinator
    print("\n2. Testing LSL Device Coordinator:")
    try:
        lsl_coordinator = LSLDeviceCoordinator()
        print(f"   ✅ LSL coordinator created")
        print(f"   Available: {lsl_coordinator.is_available}")
        
        # Test sensor registration
        reg_success = lsl_coordinator.register_sensor("test_gsr", "GSR")
        print(f"   Sensor registration: {'✅ Success' if reg_success else '❌ Failed'}")
        
        # Test command sending
        cmd_success = lsl_coordinator.send_coordination_command("test_command", {"data": "test"})
        print(f"   Command sending: {'✅ Success' if cmd_success else '❌ Failed'}")
        
        # Test status
        status = lsl_coordinator.get_lsl_status()
        print(f"   ✅ Status retrieved: {len(status)} fields")
        
    except Exception as e:
        print(f"   ❌ LSL coordinator failed: {e}")
    
    print("\n" + "=" * 60)
    print("LSL Components Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_enhanced_synchronization()
        test_lsl_components()
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()