#!/usr/bin/env python3
"""
Test script to verify face blurring has been properly removed and replaced with hand detection.
"""

import sys
import os
import re

# Add PythonApp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp'))

def test_face_blurring_disabled():
    """Test that face blurring is disabled in configuration."""
    from config.system_configuration import default_config
    
    print("Testing face blurring configuration...")
    assert default_config.security.enable_face_blurring == False, \
        "Face blurring should be disabled"
    print("✓ Face blurring is disabled in configuration")


def test_hand_detection_in_source():
    """Test that hand detection method is present in source code."""
    cv_pipeline_path = os.path.join(os.path.dirname(__file__), 'PythonApp', 'webcam', 'cv_preprocessing_pipeline.py')
    
    print("Testing hand detection in source code...")
    with open(cv_pipeline_path, 'r') as f:
        content = f.read()
    
    # Check that MEDIAPIPE_HANDS method is defined
    assert 'MEDIAPIPE_HANDS = "mediapipe_hands"' in content, \
        "MEDIAPIPE_HANDS method should be defined in ROIDetectionMethod enum"
    print("✓ MEDIAPIPE_HANDS method is defined in source code")
    
    # Check that _detect_mediapipe_hands method is implemented
    assert 'def _detect_mediapipe_hands(' in content, \
        "_detect_mediapipe_hands method should be implemented"
    print("✓ _detect_mediapipe_hands method is implemented")
    
    # Check that hands detection is handled in detect_roi method
    assert 'ROIDetectionMethod.MEDIAPIPE_HANDS:' in content, \
        "MEDIAPIPE_HANDS should be handled in detect_roi method"
    print("✓ MEDIAPIPE_HANDS is properly handled in detection logic")


def test_default_method_changed():
    """Test that default ROI detection method has been changed from face to hands."""
    cv_pipeline_path = os.path.join(os.path.dirname(__file__), 'PythonApp', 'webcam', 'cv_preprocessing_pipeline.py')
    
    print("Testing default ROI detection method in source...")
    with open(cv_pipeline_path, 'r') as f:
        content = f.read()
    
    # Check that the default parameter is now MEDIAPIPE_HANDS
    assert 'method: ROIDetectionMethod = ROIDetectionMethod.MEDIAPIPE_HANDS' in content, \
        "Default ROI detection method should be MEDIAPIPE_HANDS"
    print("✓ Default ROI detection method is now MEDIAPIPE_HANDS")
    
    # Check that create_complete_pipeline uses MEDIAPIPE_HANDS
    assert 'method=ROIDetectionMethod.MEDIAPIPE_HANDS,' in content, \
        "create_complete_pipeline should use MEDIAPIPE_HANDS"
    print("✓ Pipeline creation uses hand detection")


def test_dual_webcam_updated():
    """Test that dual webcam capture uses hand detection."""
    dual_webcam_path = os.path.join(os.path.dirname(__file__), 'PythonApp', 'webcam', 'dual_webcam_capture.py')
    
    print("Testing dual webcam configuration...")
    with open(dual_webcam_path, 'r') as f:
        content = f.read()
    
    # Check that dual webcam uses MEDIAPIPE_HANDS instead of DNN_FACE
    assert 'method=ROIDetectionMethod.MEDIAPIPE_HANDS,' in content, \
        "DualWebcamCapture should use MEDIAPIPE_HANDS"
    assert 'method=ROIDetectionMethod.DNN_FACE,' not in content, \
        "DualWebcamCapture should not use DNN_FACE anymore"
    print("✓ DualWebcamCapture uses hand detection instead of face detection")


def test_configuration_comment_updated():
    """Test that configuration comment reflects the change."""
    config_path = os.path.join(os.path.dirname(__file__), 'PythonApp', 'config', 'system_configuration.py')
    
    print("Testing configuration comment...")
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Check that the comment reflects the reason for disabling
    assert 'no faces in video, only hands' in content, \
        "Configuration comment should explain why face blurring is disabled"
    print("✓ Configuration comment explains the change")


def test_no_remaining_face_detection_defaults():
    """Test that no remaining code defaults to face detection."""
    cv_pipeline_path = os.path.join(os.path.dirname(__file__), 'PythonApp', 'webcam', 'cv_preprocessing_pipeline.py')
    
    print("Testing for remaining face detection defaults...")
    with open(cv_pipeline_path, 'r') as f:
        lines = f.readlines()
    
    # Look for any lines that might still default to face detection
    # (excluding conditional logic, enum definitions, and error fallbacks)
    face_detection_defaults = []
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if ('= ROIDetectionMethod.DNN_FACE' in line or 
            '= ROIDetectionMethod.FACE_CASCADE' in line):
            # Skip enum definitions, conditional checks, and documented fallbacks
            if (not line_stripped.startswith('if ') and 
                not line_stripped.startswith('elif ') and
                'method: ROIDetectionMethod' not in line and
                '# fallback' not in line.lower() and
                'self.method =' not in line):  # Allow fallback assignments
                face_detection_defaults.append(f"Line {i}: {line.strip()}")
    
    assert len(face_detection_defaults) == 0, \
        f"Found remaining face detection defaults: {face_detection_defaults}"
    print("✓ No inappropriate face detection defaults found")
    print("  (Face detection methods are still available for explicit use)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Face Blurring Removal Changes")
    print("=" * 60)
    
    tests = [
        test_face_blurring_disabled,
        test_hand_detection_in_source,
        test_default_method_changed,
        test_dual_webcam_updated,
        test_configuration_comment_updated,
        test_no_remaining_face_detection_defaults,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Face blurring has been successfully removed.")
        print("   The system now uses hand detection instead of face detection.")
        print()
        print("Summary of changes made:")
        print("  - Face blurring disabled in SecurityConfiguration")
        print("  - Added MEDIAPIPE_HANDS detection method")
        print("  - Implemented _detect_mediapipe_hands() function")
        print("  - Updated default ROI detection method to use hands")
        print("  - Updated DualWebcamCapture to use hand detection")
        print("  - Updated pipeline creation to use hand detection")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())