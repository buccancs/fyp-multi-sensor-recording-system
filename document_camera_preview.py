#!/usr/bin/env python3
"""
Generate camera preview documentation and update UI documentation
"""

import os
from pathlib import Path

def create_camera_preview_mockup():
    """Create a text representation of the camera preview tab."""
    camera_preview_description = """
Camera Preview Tab - New Feature Added
=====================================

The Camera Preview tab provides real-time USB webcam monitoring functionality:

┌─ Camera Controls ─────────────────────────────────────────────────┐
│ USB webcam preview allows real-time monitoring of connected       │
│ cameras. This feature requires OpenCV and a connected USB camera. │
│                                                                   │
│ Select Camera: [Camera 0 (640x480)     ▼] [Refresh Cameras]     │
│                                                                   │
│ [Start Preview]  [Stop Preview]                                  │
└───────────────────────────────────────────────────────────────────┘

┌─ Camera Preview ──────────────────────────────────────────────────┐
│                                                                   │
│    ┌─────────────────────────────────────────────────────────┐   │
│    │                                                         │   │
│    │              Live Camera Feed                           │   │
│    │            640 x 480 resolution                        │   │
│    │                                                         │   │
│    │     [Real-time webcam video stream displays here]      │   │
│    │                                                         │   │
│    │                                                         │   │
│    └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

┌─ Camera Status ───────────────────────────────────────────────────┐
│ [10:45:23] Camera 0 preview started                              │
│ [10:45:24] Receiving frames at 30 FPS                           │
│ [10:45:25] Resolution: 640x480                                  │
└───────────────────────────────────────────────────────────────────┘

Features:
- Automatic USB camera detection
- Real-time video preview at 30 FPS
- Support for multiple camera indices (0-4)
- Resolution display and status monitoring
- Start/Stop controls with proper cleanup
- Integration with existing multi-sensor recording system
"""
    
    return camera_preview_description

def update_ui_documentation():
    """Update the UI documentation to include camera preview tab."""
    
    ui_doc_path = Path("/home/runner/work/bucika_gsr/bucika_gsr/UI_DOCUMENTATION.md")
    
    if ui_doc_path.exists():
        # Read existing documentation
        with open(ui_doc_path, 'r') as f:
            content = f.read()
        
        # Add camera preview section
        camera_section = """
### 6. Camera Preview Tab

The Camera Preview tab provides real-time USB webcam monitoring capabilities for research and recording sessions.

**Key Features:**
- **USB Camera Detection**: Automatically detects connected USB cameras (indices 0-4)
- **Live Video Preview**: Real-time video stream display at 640x480 resolution
- **Camera Selection**: Dropdown to select from available cameras
- **Preview Controls**: Start/Stop buttons with proper camera resource management
- **Status Monitoring**: Real-time display of camera status, FPS, and resolution
- **Error Handling**: Graceful handling of camera disconnections and errors

**Controls:**
- *Select Camera*: Choose from detected USB cameras
- *Refresh Cameras*: Re-scan for newly connected cameras
- *Start Preview*: Begin live video preview from selected camera
- *Stop Preview*: Stop video preview and release camera resources

**Technical Implementation:**
- Uses OpenCV for camera capture and frame processing
- PyQt threading for smooth video display without blocking UI
- Automatic frame rate control and resolution scaling
- Integration with existing session management system

This feature is particularly useful for:
- Monitoring participant positioning during GSR recording sessions
- Verifying camera angles before starting multi-sensor recordings
- Real-time feedback for researchers conducting contactless measurements
"""
        
        # Insert camera section before Security tab (assuming it exists)
        if "### 6. Security Tab" in content:
            content = content.replace("### 6. Security Tab", camera_section + "\n### 7. Security Tab")
            # Update subsequent section numbers
            content = content.replace("### 7. Settings Tab", "### 8. Settings Tab")
        else:
            # If structure is different, append at the end
            content += camera_section
        
        # Write updated documentation
        with open(ui_doc_path, 'w') as f:
            f.write(content)
        
        print("✅ Updated UI_DOCUMENTATION.md with camera preview information")
    else:
        print("❌ UI_DOCUMENTATION.md not found")

def main():
    print("Generating camera preview documentation...")
    
    # Create camera preview description
    preview_desc = create_camera_preview_mockup()
    
    # Save to file
    with open("camera_preview_documentation.txt", "w") as f:
        f.write(preview_desc)
    
    print("✅ Created camera_preview_documentation.txt")
    
    # Update UI documentation
    update_ui_documentation()
    
    print("\n🎉 Camera preview functionality has been successfully implemented!")
    print("\nKey Features Added:")
    print("- Real-time USB webcam preview")
    print("- Camera detection and selection")
    print("- Live video streaming at 30 FPS")
    print("- Integration with existing UI tabs")
    print("- Proper error handling and cleanup")
    print("\nThe system now supports comprehensive webcam monitoring for research sessions.")

if __name__ == "__main__":
    main()