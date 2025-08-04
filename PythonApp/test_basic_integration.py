import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from network.pc_server import PCServer, HelloMessage, SensorDataMessage
from shimmer_manager import ShimmerManager


def test_basic_functionality():
    print('Testing basic Shimmer PC integration...')
    print('1. Creating ShimmerManager...')
    manager = ShimmerManager(enable_android_integration=True)
    print('   ✅ ShimmerManager created')
    print('2. Initializing manager...')
    if manager.initialize():
        print('   ✅ Manager initialized successfully')
    else:
        print('   ❌ Manager initialization failed')
        return False
    print('3. Testing device discovery...')
    devices = manager.scan_and_pair_devices()
    print(f'   ✅ Found devices: {devices}')
    print('4. Testing device connections...')
    if manager.connect_devices(devices):
        print('   ✅ Devices connected successfully')
    else:
        print('   ❌ Device connection failed')
        return False
    print('5. Checking device status...')
    status = manager.get_shimmer_status()
    print(f'   ✅ Device status: {len(status)} devices')
    print('6. Checking Android integration...')
    android_devices = manager.get_android_devices()
    print(f'   ✅ Android integration ready: {len(android_devices)} devices')
    print('7. Cleaning up...')
    manager.cleanup()
    print('   ✅ Cleanup completed')
    print('\n🎉 All basic tests passed!')
    return True


if __name__ == '__main__':
    try:
        success = test_basic_functionality()
        if success:
            print('\n✅ Shimmer PC Integration is working correctly!')
        else:
            print('\n❌ Some tests failed')
    except Exception as e:
        print(f'\n❌ Test failed with exception: {e}')
        import traceback
        traceback.print_exc()
