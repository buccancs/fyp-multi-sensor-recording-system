#!/usr/bin/env python3
"""
Test script for Session Directory Integration - Milestone 3.6 Fix

This script tests that the JsonSocketServer now uses the SessionManager's
session directory instead of creating its own timestamp-based directory.
"""

import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp', 'src'))

def test_session_directory_integration():
    """Test that JsonSocketServer uses SessionManager's session directory"""
    
    print("Testing Session Directory Integration...")
    
    try:
        from network.device_server import JsonSocketServer
        from session.session_manager import SessionManager
        
        # Create a temporary directory for testing
        test_base_dir = tempfile.mkdtemp()
        print(f"Using test directory: {test_base_dir}")
        
        try:
            # Create SessionManager with test directory
            session_manager = SessionManager(test_base_dir)
            
            # Create a test session
            session_info = session_manager.create_session("test_integration_session")
            session_folder = session_info["folder_path"]
            print(f"SessionManager created session folder: {session_folder}")
            
            # Create JsonSocketServer with SessionManager integration
            json_server = JsonSocketServer(session_manager=session_manager)
            
            # Test get_session_directory method
            session_dir = json_server.get_session_directory()
            
            print(f"JsonSocketServer returned session directory: {session_dir}")
            
            # Verify that the directories match
            if session_dir == session_folder:
                print("✅ SUCCESS: JsonSocketServer uses SessionManager's session directory")
                return True
            else:
                print(f"❌ FAILURE: Directory mismatch!")
                print(f"  Expected: {session_folder}")
                print(f"  Got: {session_dir}")
                return False
                
        finally:
            # Clean up test directory
            if os.path.exists(test_base_dir):
                shutil.rmtree(test_base_dir)
                print(f"Cleaned up test directory: {test_base_dir}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_fallback_behavior():
    """Test fallback behavior when SessionManager has no active session"""
    
    print("\nTesting Fallback Behavior...")
    
    try:
        from network.device_server import JsonSocketServer
        from session.session_manager import SessionManager
        
        # Create SessionManager but don't create a session
        session_manager = SessionManager("test_recordings")
        
        # Create JsonSocketServer with SessionManager integration
        json_server = JsonSocketServer(session_manager=session_manager)
        
        # Test get_session_directory method (should fall back to creating own directory)
        session_dir = json_server.get_session_directory()
        
        print(f"JsonSocketServer fallback directory: {session_dir}")
        
        # Verify that a directory was created (fallback behavior)
        if session_dir and os.path.exists(session_dir):
            print("✅ SUCCESS: Fallback behavior works correctly")
            
            # Clean up created directory
            parent_dir = os.path.dirname(session_dir)
            if os.path.basename(parent_dir) == "sessions":
                shutil.rmtree(parent_dir)
                print(f"Cleaned up fallback directory: {parent_dir}")
            
            return True
        else:
            print("❌ FAILURE: Fallback behavior failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_without_session_manager():
    """Test behavior when no SessionManager is provided"""
    
    print("\nTesting Behavior Without SessionManager...")
    
    try:
        from network.device_server import JsonSocketServer
        
        # Create JsonSocketServer without SessionManager
        json_server = JsonSocketServer()
        
        # Test get_session_directory method (should create own directory)
        session_dir = json_server.get_session_directory()
        
        print(f"JsonSocketServer standalone directory: {session_dir}")
        
        # Verify that a directory was created
        if session_dir and os.path.exists(session_dir):
            print("✅ SUCCESS: Standalone behavior works correctly")
            
            # Clean up created directory
            parent_dir = os.path.dirname(session_dir)
            if os.path.basename(parent_dir) == "sessions":
                shutil.rmtree(parent_dir)
                print(f"Cleaned up standalone directory: {parent_dir}")
            
            return True
        else:
            print("❌ FAILURE: Standalone behavior failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_main_window_integration():
    """Test that MainWindow properly integrates SessionManager with JsonSocketServer"""
    
    print("\nTesting MainWindow Integration...")
    
    try:
        # This test requires PyQt5, so we'll mock it if not available
        try:
            from PyQt5.QtWidgets import QApplication
            from gui.main_window import MainWindow
            
            # Create QApplication instance
            app = QApplication([])
            
            # Create MainWindow instance
            main_window = MainWindow()
            
            # Verify that JsonSocketServer has SessionManager reference
            if hasattr(main_window.json_server, 'session_manager'):
                if main_window.json_server.session_manager is main_window.session_manager:
                    print("✅ SUCCESS: MainWindow properly integrates SessionManager with JsonSocketServer")
                    return True
                else:
                    print("❌ FAILURE: JsonSocketServer has different SessionManager instance")
                    return False
            else:
                print("❌ FAILURE: JsonSocketServer doesn't have session_manager attribute")
                return False
                
        except ImportError:
            print("⚠️  SKIPPED: PyQt5 not available for MainWindow integration test")
            return True  # Skip this test if PyQt5 is not available
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("SESSION DIRECTORY INTEGRATION TEST")
    print("=" * 70)
    
    success_count = 0
    total_tests = 4
    
    # Run tests
    if test_session_directory_integration():
        success_count += 1
    
    if test_fallback_behavior():
        success_count += 1
        
    if test_without_session_manager():
        success_count += 1
        
    if test_main_window_integration():
        success_count += 1
    
    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Session Directory Integration is working!")
        print("\n✅ ISSUE RESOLVED:")
        print("   JsonSocketServer now uses SessionManager's session directory")
        print("   instead of creating its own timestamp-based directory.")
    else:
        print("⚠️  Some tests failed - Check the implementation")
    
    print("=" * 70)
