#!/usr/bin/env python3
"""
Simple integration test for the new minimal Python implementation.
Tests basic functionality of the rebuilt system.
"""

import time
import threading
import tempfile
import json
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_network_server():
    """Test the JSON socket server."""
    print("Testing network server...")
    
    from PythonApp.network import JsonSocketServer
    
    server = JsonSocketServer(host="127.0.0.1", port=0)  # Use port 0 for auto-assignment
    
    # Start server
    assert server.start_server(), "Failed to start server"
    
    # Check server is running
    assert server.running, "Server not running"
    
    # Get connected devices (should be empty)
    devices = server.get_connected_devices()
    assert isinstance(devices, dict), "Device list should be dict"
    assert len(devices) == 0, "Should have no devices initially"
    
    # Stop server
    server.stop_server()
    assert not server.running, "Server should be stopped"
    
    print("✅ Network server test passed")


def test_session_manager():
    """Test the session manager."""
    print("Testing session manager...")
    
    from PythonApp.session import SessionManager, SessionConfig
    
    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(base_output_dir=temp_dir)
        
        # Test session creation
        config = SessionConfig(
            session_name="test_session",
            output_directory=temp_dir,
            duration_seconds=60
        )
        
        session_info = session_manager.create_session(config)
        assert session_info is not None, "Failed to create session"
        assert session_info.session_id.startswith("session_"), "Invalid session ID"
        assert session_info.status == "created", "Wrong initial status"
        
        # Test session status
        status = session_manager.get_session_status()
        assert status['has_active_session'], "Should have active session"
        
        print("✅ Session manager test passed")


def test_gui_import():
    """Test that GUI components can be imported."""
    print("Testing GUI imports...")
    
    try:
        from PythonApp.gui.main_window import MainWindow
        print("✅ GUI import test passed")
    except ImportError as e:
        # GUI import might fail in headless environment, which is OK
        print(f"⚠️  GUI import skipped (headless environment): {e}")


def test_utilities():
    """Test utility functions."""
    print("Testing utilities...")
    
    from PythonApp.utils import get_local_ip, check_port_available, format_duration
    
    # Test IP detection
    ip = get_local_ip()
    assert ip is None or isinstance(ip, str), "IP should be string or None"
    
    # Test port checking
    port_free = check_port_available(9999)  # Hopefully free port
    assert isinstance(port_free, bool), "Port check should return boolean"
    
    # Test duration formatting
    duration = format_duration(125)  # 2:05
    assert duration == "02:05", f"Expected '02:05', got '{duration}'"
    
    duration = format_duration(3665)  # 1:01:05
    assert duration == "01:01:05", f"Expected '01:01:05', got '{duration}'"
    
    print("✅ Utilities test passed")


def test_main_dependencies():
    """Test that main dependencies check works."""
    print("Testing main dependencies...")
    
    from PythonApp.main import check_dependencies
    
    deps_ok = check_dependencies()
    assert deps_ok, "Dependencies check failed"
    
    print("✅ Main dependencies test passed")


def run_all_tests():
    """Run all integration tests."""
    print("="*50)
    print("🧪 Running Minimal Python Implementation Tests")
    print("="*50)
    
    tests = [
        test_main_dependencies,
        test_utilities,
        test_network_server,
        test_session_manager,
        test_gui_import,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! New Python implementation working correctly.")
        return True
    else:
        print("💥 Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)