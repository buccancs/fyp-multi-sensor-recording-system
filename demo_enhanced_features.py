#!/usr/bin/env python3
"""
Demo script for Enhanced UI Features
Demonstrates the new playback tab and enhanced File/Tools menus
"""

import os
import sys

# Set up environment for headless operation if needed
if 'DISPLAY' not in os.environ:
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp', 'src'))

def create_mock_session_data():
    """Create mock session data for demonstration."""
    recordings_dir = os.path.join(os.path.dirname(__file__), 'PythonApp', 'recordings')
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Create mock session directories
    mock_sessions = [
        'session_2025_01_15_10_30_45',
        'session_2025_01_14_14_22_10',
        'session_2025_01_13_09_15_33'
    ]
    
    for session in mock_sessions:
        session_path = os.path.join(recordings_dir, session)
        os.makedirs(session_path, exist_ok=True)
        
        # Create mock session info file
        import json
        session_info = {
            "session_id": session,
            "start_time": "2025-01-15T10:30:45",
            "duration": 125.5,
            "status": "completed",
            "devices": [
                {"id": "device_1", "type": "android_phone"},
                {"id": "pc_webcam", "type": "pc_webcam"}
            ],
            "files": [
                {"filename": "device_1_camera.mp4", "file_type": "video", "file_size": 15728640},
                {"filename": "device_1_thermal.mp4", "file_type": "thermal_video", "file_size": 8388608},
                {"filename": "pc_webcam.mp4", "file_type": "webcam_video", "file_size": 25165824}
            ]
        }
        
        with open(os.path.join(session_path, 'session_info.json'), 'w') as f:
            json.dump(session_info, f, indent=2)
        
        # Create mock video files (empty files for demo)
        for file_info in session_info['files']:
            file_path = os.path.join(session_path, file_info['filename'])
            with open(file_path, 'wb') as f:
                f.write(b'0' * min(1024, file_info['file_size']))  # Small demo files
    
    print(f"Created {len(mock_sessions)} mock sessions in {recordings_dir}")
    return recordings_dir

def demonstrate_features():
    """Demonstrate the enhanced features."""
    print("Enhanced Multi-Sensor Recording System Features Demo")
    print("=" * 60)
    
    # Create mock data
    recordings_dir = create_mock_session_data()
    
    print("\n✓ NEW FEATURE: Playback Tab")
    print("  - Added comprehensive session playback functionality")
    print("  - Session browser with file listing")
    print("  - Video playback controls (play, pause, speed control)")
    print("  - Session information display")
    print("  - Progress slider and time display")
    
    print("\n✓ NEW FEATURE: Enhanced File Menu")
    print("  - Recent Sessions submenu with quick access")
    print("  - Open Session Folder and Recordings Directory")
    print("  - Export/Import session data (ZIP, TAR, folder copy)")
    print("  - Clear old recordings with age/count filters")
    print("  - Preferences dialog with tabbed settings")
    
    print("\n✓ NEW FEATURE: Enhanced Tools Menu")
    print("  - Device Tools: Diagnostics and Status Reports")
    print("  - Calibration Tools: Thermal calibration wizard and validation")
    print("  - Data Analysis: Session analysis and quality checks")
    print("  - Export Tools: Batch export and video converter")
    print("  - System Tools: Information and performance monitoring")
    
    print("\n✓ Key Functionality Highlights:")
    print("  - Real session file browsing and management")
    print("  - Video playback with multiple speed options")
    print("  - Comprehensive system diagnostics")
    print("  - Data export in multiple formats")
    print("  - Automated old recording cleanup")
    print("  - Professional preferences management")
    
    print(f"\nDemo data created in: {recordings_dir}")
    print("\nTo use these features:")
    print("1. Launch the main application")
    print("2. Click on the 'Playback' tab to browse recorded sessions")
    print("3. Use File menu for session management")
    print("4. Use Tools menu for diagnostics and analysis")
    
    return True

if __name__ == "__main__":
    try:
        success = demonstrate_features()
        if success:
            print("\n✓ Enhanced features demo completed successfully!")
        else:
            print("\n✗ Enhanced features demo failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error demonstrating enhanced features: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)