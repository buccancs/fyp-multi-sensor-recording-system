#!/usr/bin/env python3
"""
Python-Android App Harmonization Validation Test
==================================================

Tests the harmonized communication between Python and Android apps
using shared protocols and backward compatibility with legacy protocols.
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_shared_protocols():
    """Test shared protocol message creation and parsing."""
    print("\n🔄 Testing Shared Protocols...")
    
    try:
        from shared_protocols.network_protocol import (
            HelloMessage, CommandMessage, ResponseMessage, 
            MessageType, create_message_from_json, create_success_response
        )
        from shared_protocols.data_structures import DeviceInfo, DeviceType
        
        # Test message creation
        device_info = DeviceInfo(
            device_id='android_test_001',
            device_type=DeviceType.ANDROID_PHONE,
            capabilities=['recording', 'thermal', 'rgb'],
            firmware_version='1.0'
        )
        
        hello = HelloMessage(device_info=device_info, capabilities=['test'])
        cmd = CommandMessage(command='ping', parameters={'test': True})
        resp = create_success_response('ping', {'pong': True})
        
        # Test JSON conversion
        hello_json = hello.to_json()
        cmd_json = cmd.to_json()
        resp_json = resp.to_json()
        
        # Test parsing
        parsed_hello = create_message_from_json(hello_json)
        parsed_cmd = create_message_from_json(cmd_json)
        parsed_resp = create_message_from_json(resp_json)
        
        assert isinstance(parsed_hello, HelloMessage)
        assert isinstance(parsed_cmd, CommandMessage)
        assert isinstance(parsed_resp, ResponseMessage)
        
        print("✅ Shared protocol messages work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Shared protocols test failed: {e}")
        return False


def test_python_server():
    """Test Python server with harmonized protocols."""
    print("\n🖥️ Testing Python Server...")
    
    try:
        from PythonApp.network import JsonSocketServer
        
        # Create server
        server = JsonSocketServer()
        
        # Test handler registration
        assert len(server.message_handlers) >= 20, "Not enough message handlers registered"
        
        # Test device management
        server.add_test_device('test_android_001')
        server.add_test_device('test_android_002')
        
        devices = server.get_connected_devices()
        assert len(devices) == 2, "Test devices not added correctly"
        
        # Test protocol broadcasts
        shared_targets = server.broadcast_command('ping', {'test': True}, use_shared_protocol=True)
        legacy_targets = server.broadcast_command('ping', {'test': True}, use_shared_protocol=False)
        
        assert len(shared_targets) == 2, "Shared protocol broadcast failed"
        assert len(legacy_targets) == 2, "Legacy protocol broadcast failed"
        
        # Test session control
        session_targets = server.broadcast_session_control('start', {'session_id': 'test_session'})
        assert len(session_targets) == 2, "Session control broadcast failed"
        
        print("✅ Python server harmonization works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Python server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_android_protocol_compatibility():
    """Test Android protocol message compatibility."""
    print("\n📱 Testing Android Protocol Compatibility...")
    
    try:
        # Test that Android SharedProtocolMessage format matches Python expectations
        android_message_format = {
            "message_type": "hello",
            "timestamp": 1234567890.0,
            "device_id": "android_test",
            "device_info": {
                "device_id": "android_test",
                "device_type": "android_phone",  # Use DeviceType enum value
                "capabilities": ["recording", "thermal", "rgb"],
                "firmware_version": "1.0"
            },
            "capabilities": ["recording", "thermal", "rgb"],
            "protocol_version": "1.0"
        }
        
        # Test Python can parse Android-style message
        from shared_protocols.network_protocol import create_message_from_json, HelloMessage
        import json
        
        parsed = create_message_from_json(json.dumps(android_message_format))
        
        # Should create a HelloMessage
        assert parsed is not None, "Android message format not parseable"
        assert isinstance(parsed, HelloMessage), f"Expected HelloMessage, got {type(parsed)}"
        
        print("✅ Android protocol compatibility verified")
        return True
        
    except Exception as e:
        print(f"❌ Android compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backwards_compatibility():
    """Test legacy protocol backwards compatibility."""
    print("\n🔄 Testing Backwards Compatibility...")
    
    try:
        from PythonApp.network import JsonSocketServer
        
        server = JsonSocketServer()
        server.add_test_device('legacy_test')
        
        # Test legacy message handling
        legacy_message = {
            'type': 'device_info',
            'device_id': 'legacy_test',
            'data': {
                'model': 'Legacy Device',
                'os_version': 'Android 10'
            }
        }
        
        # Should not crash when processing legacy format
        device = server.devices['legacy_test']
        server._handle_legacy_device_info(device, legacy_message)
        
        assert hasattr(device, 'legacy_info'), "Legacy info not stored"
        assert device.legacy_info == legacy_message['data'], "Legacy info not stored correctly"
        
        print("✅ Backwards compatibility works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Backwards compatibility test failed: {e}")
        return False


def test_protocol_integration():
    """Test full protocol integration scenario."""
    print("\n🔗 Testing Protocol Integration...")
    
    try:
        from PythonApp.network import JsonSocketServer
        from shared_protocols.network_protocol import CommandMessage, ResponseMessage
        
        server = JsonSocketServer()
        
        # Simulate device connection with HELLO
        server.add_test_device('integration_test')
        
        # Test command processing
        cmd = CommandMessage(command='get_status', device_id='integration_test')
        response = server._process_standard_command(
            server.devices['integration_test'], 
            'get_status', 
            {}
        )
        
        assert isinstance(response, ResponseMessage), "Command response not created"
        assert response.success == True, "Command not processed successfully"
        assert 'device_state' in response.result, "Status response incomplete"
        
        print("✅ Protocol integration works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Protocol integration test failed: {e}")
        return False


def main():
    """Run all harmonization tests."""
    print("🚀 Starting Python-Android App Harmonization Validation")
    
    tests = [
        test_shared_protocols,
        test_python_server,
        test_android_protocol_compatibility,
        test_backwards_compatibility,
        test_protocol_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All harmonization tests passed! Python-Android communication is harmonized.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)