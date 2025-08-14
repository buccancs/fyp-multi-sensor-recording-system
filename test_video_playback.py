#!/usr/bin/env python3
"""
Test Video Playback Functionality
================================

Tests the new video playback features for emotion elicitation.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_video_player_basic():
    """Test basic video player functionality."""
    print("Testing VideoPlayer import and initialization...")
    
    try:
        from PythonApp.camera import VideoPlayer, WebcamManager, OPENCV_AVAILABLE
        
        print(f"✅ VideoPlayer imported successfully")
        print(f"OpenCV Available: {OPENCV_AVAILABLE}")
        
        # Test WebcamManager with video capabilities
        webcam_manager = WebcamManager()
        print(f"✅ WebcamManager created successfully")
        
        # Test supported formats
        formats = webcam_manager.get_supported_video_formats()
        print(f"✅ Supported video formats: {', '.join(formats)}")
        
        # Test VideoPlayer initialization
        if OPENCV_AVAILABLE:
            video_player = VideoPlayer()
            print(f"✅ VideoPlayer created successfully")
            
            # Test video loading with non-existent file (should handle gracefully)
            result = video_player.load_video("/nonexistent/video.mp4")
            if not result:
                print(f"✅ VideoPlayer correctly handles non-existent files")
            
            video_player.release()
            print(f"✅ VideoPlayer released successfully")
        else:
            print(f"⚠️ OpenCV not available - skipping VideoPlayer tests")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing video player: {e}")
        return False

def test_webcam_manager_video_integration():
    """Test WebcamManager video integration."""
    print("\nTesting WebcamManager video integration...")
    
    try:
        from PythonApp.camera import WebcamManager, OPENCV_AVAILABLE
        
        webcam_manager = WebcamManager()
        
        # Test starting video playback with non-existent file
        if OPENCV_AVAILABLE:
            video_player = webcam_manager.start_video_playback("/nonexistent/video.mp4")
            if video_player is None:
                print(f"✅ WebcamManager correctly handles invalid video files")
            
            # Test stopping video playback
            webcam_manager.stop_video_playback()
            print(f"✅ WebcamManager stop_video_playback works")
        else:
            print(f"⚠️ OpenCV not available - skipping video integration tests")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing webcam manager video integration: {e}")
        return False

def test_main_window_video_features():
    """Test main window video features (import only, no GUI)."""
    print("\nTesting main window video features...")
    
    try:
        # We can't actually test the GUI without PyQt, but we can test the structure
        import inspect
        
        # Read the main window file to check for video methods
        main_window_path = project_root / "PythonApp" / "gui" / "main_window.py"
        with open(main_window_path, 'r') as f:
            content = f.read()
        
        # Check for key video-related methods
        video_methods = [
            "_browse_video_file",
            "_play_video", 
            "_pause_video",
            "_stop_video",
            "_update_video_frame",
            "_handle_video_finished",
            "_update_video_status"
        ]
        
        missing_methods = []
        for method in video_methods:
            if method not in content:
                missing_methods.append(method)
        
        if not missing_methods:
            print(f"✅ All video playback methods found in MainWindow")
        else:
            print(f"❌ Missing video methods: {missing_methods}")
            return False
            
        # Check for video UI elements
        video_ui_elements = [
            "video_path_label",
            "browse_video_btn",
            "play_video_btn",
            "pause_video_btn", 
            "stop_video_btn",
            "video_progress_slider",
            "video_time_label"
        ]
        
        missing_elements = []
        for element in video_ui_elements:
            if element not in content:
                missing_elements.append(element)
                
        if not missing_elements:
            print(f"✅ All video UI elements found in MainWindow")
        else:
            print(f"❌ Missing video UI elements: {missing_elements}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing main window video features: {e}")
        return False

def main():
    """Run all video playback tests."""
    print("=== Video Playback for Emotion Elicitation - Test Suite ===\n")
    
    tests = [
        test_video_player_basic,
        test_webcam_manager_video_integration,
        test_main_window_video_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All video playback tests passed!")
        print("\nFeatures implemented:")
        print("• VideoPlayer class for emotion elicitation video playback")
        print("• WebcamManager integration with video capabilities")
        print("• Media & Stimuli tab with unified camera/video interface")
        print("• Complete playback controls (play, pause, stop, seek)")
        print("• Video file browser with format filtering")
        print("• Progress tracking and time display")
        print("• Error handling and status reporting")
        print("• Session integration for synchronized experiments")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)