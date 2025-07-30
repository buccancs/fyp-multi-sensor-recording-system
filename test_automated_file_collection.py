#!/usr/bin/env python3
"""
Test script for automated file collection trigger - Milestone 3.6

This script tests the integration between the recording stop workflow
and the automated file collection system.
"""

import sys
import os
import time
from unittest.mock import Mock, patch

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp', 'src'))

def test_automated_file_collection():
    """Test that file collection is triggered when recording stops"""
    
    print("Testing automated file collection trigger...")
    
    try:
        # Import the main window class
        from gui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        
        # Create QApplication instance (required for Qt widgets)
        app = QApplication([])
        
        # Create main window instance
        main_window = MainWindow()
        
        # Mock the JsonSocketServer and SessionManager
        mock_json_server = Mock()
        mock_session_manager = Mock()
        
        # Set up mock return values
        mock_session_manager.end_session.return_value = {
            'session_id': 'test_session_123',
            'duration': 30.5
        }
        mock_json_server.request_all_session_files.return_value = 3  # 3 file requests sent
        
        # Replace the real objects with mocks
        main_window.json_server = mock_json_server
        main_window.session_manager = mock_session_manager
        main_window.server_running = True
        
        # Mock webcam capture
        mock_webcam = Mock()
        mock_webcam.stop_recording.return_value = "/path/to/webcam/video.mp4"
        main_window.webcam_capture = mock_webcam
        
        # Test the handle_stop method
        print("Calling handle_stop()...")
        main_window.handle_stop()
        
        # Verify that end_session was called
        mock_session_manager.end_session.assert_called_once()
        print("✓ Session ended successfully")
        
        # Wait for the QTimer to trigger (2 seconds + small buffer)
        print("Waiting for file collection timer (2.5 seconds)...")
        
        # Process Qt events to allow QTimer to execute
        start_time = time.time()
        while time.time() - start_time < 3.0:
            app.processEvents()
            time.sleep(0.1)
        
        # Verify that request_all_session_files was called
        mock_json_server.request_all_session_files.assert_called_once_with('test_session_123')
        print("✓ File collection triggered successfully")
        
        print("\n✅ Automated file collection test PASSED")
        print("The system correctly triggers file collection after recording stops")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This is expected if PyQt5 is not installed in the test environment")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_collect_session_files_method():
    """Test the collect_session_files method directly"""
    
    print("\nTesting collect_session_files method...")
    
    try:
        from gui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication instance
        app = QApplication([])
        
        # Create main window instance
        main_window = MainWindow()
        
        # Mock the JsonSocketServer
        mock_json_server = Mock()
        mock_json_server.request_all_session_files.return_value = 5
        
        main_window.json_server = mock_json_server
        main_window.server_running = True
        
        # Test the collect_session_files method
        test_session_id = "test_session_456"
        main_window.collect_session_files(test_session_id)
        
        # Verify the method was called with correct parameters
        mock_json_server.request_all_session_files.assert_called_once_with(test_session_id)
        
        print("✓ collect_session_files method works correctly")
        print("✅ Direct method test PASSED")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_error_handling():
    """Test error handling in collect_session_files"""
    
    print("\nTesting error handling...")
    
    try:
        from gui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication instance
        app = QApplication([])
        
        # Create main window instance
        main_window = MainWindow()
        
        # Test with server not running
        main_window.server_running = False
        main_window.json_server = None
        
        # This should handle the error gracefully
        main_window.collect_session_files("test_session")
        
        print("✓ Error handling works correctly when server is not running")
        
        # Test with server running but method throws exception
        main_window.server_running = True
        mock_json_server = Mock()
        mock_json_server.request_all_session_files.side_effect = Exception("Test error")
        main_window.json_server = mock_json_server
        
        # This should handle the exception gracefully
        main_window.collect_session_files("test_session")
        
        print("✓ Error handling works correctly when method throws exception")
        print("✅ Error handling test PASSED")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AUTOMATED FILE COLLECTION INTEGRATION TEST")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Run tests
    if test_automated_file_collection():
        success_count += 1
    
    if test_collect_session_files_method():
        success_count += 1
        
    if test_error_handling():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Automated file collection integration is working!")
    else:
        print("⚠️  Some tests failed - Check the implementation")
    
    print("=" * 60)
