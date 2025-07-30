#!/usr/bin/env python3
"""
Quick Test Video Generation Script

This script quickly creates essential test videos for immediate testing needs.
Creates smaller, faster-to-generate videos for comprehensive stimulus testing.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Purpose: Generate essential test videos quickly
"""

import os
import sys
import json
import time
from pathlib import Path

# Try to import video creation dependencies
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

def create_quick_test_video(filename, duration=3, fps=30, resolution=(640, 480)):
    """Create a quick test video with timing markers."""
    if not CV2_AVAILABLE:
        print(f"[DEBUG_LOG] Cannot create {filename} - OpenCV not available")
        return False
    
    try:
        # Determine format from filename
        ext = Path(filename).suffix.lower()
        if ext == '.mp4':
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        elif ext == '.avi':
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Default
        
        print(f"[DEBUG_LOG] Creating {filename}...")
        
        out = cv2.VideoWriter(filename, fourcc, fps, resolution)
        if not out.isOpened():
            print(f"[DEBUG_LOG] Failed to open video writer for {filename}")
            return False
        
        total_frames = int(duration * fps)
        width, height = resolution
        
        for frame_num in range(total_frames):
            # Create frame with gradient and timing info
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Simple gradient background
            for y in range(height):
                for x in range(width):
                    frame[y, x] = [
                        int(255 * (frame_num / total_frames)),  # Blue
                        int(255 * (x / width)),                 # Green
                        int(255 * (y / height))                 # Red
                    ]
            
            # Add timing information
            current_time = frame_num / fps
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Frame and time info
            cv2.putText(frame, f'Frame: {frame_num}', (10, 30), font, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f'Time: {current_time:.2f}s', (10, 60), font, 0.7, (255, 255, 255), 2)
            
            # Second markers
            if frame_num % fps == 0:
                second = int(current_time)
                cv2.putText(frame, f'{second}s', (width//2-20, height//2), font, 2, (0, 255, 255), 3)
            
            out.write(frame)
        
        out.release()
        
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"[DEBUG_LOG] Created {filename} ({size} bytes)")
            return True
        else:
            print(f"[DEBUG_LOG] Failed to create {filename}")
            return False
            
    except Exception as e:
        print(f"[DEBUG_LOG] Error creating {filename}: {e}")
        return False

def create_problematic_video(filename):
    """Create a problematic video for error testing."""
    try:
        # Create empty file
        Path(filename).touch()
        print(f"[DEBUG_LOG] Created problematic video: {filename}")
        return True
    except Exception as e:
        print(f"[DEBUG_LOG] Error creating problematic video: {e}")
        return False

def main():
    """Create essential test videos quickly."""
    print("[DEBUG_LOG] Quick Test Video Generation")
    print("=" * 40)
    
    # Create test_videos directory
    test_dir = Path("test_videos")
    test_dir.mkdir(exist_ok=True)
    
    if not CV2_AVAILABLE:
        print("[DEBUG_LOG] OpenCV not available - install with: pip install opencv-python")
        return False
    
    created_videos = []
    
    # Create essential test videos
    test_videos = [
        ("test_videos/quick_test_sd.mp4", 3, 30, (640, 480)),
        ("test_videos/quick_test_hd.mp4", 5, 30, (1280, 720)),
        ("test_videos/quick_test_sd.avi", 3, 30, (640, 480)),
        ("test_videos/timing_test.mp4", 10, 30, (800, 600)),
    ]
    
    for filename, duration, fps, resolution in test_videos:
        if create_quick_test_video(filename, duration, fps, resolution):
            created_videos.append(filename)
    
    # Create problematic videos for error testing
    problematic_videos = [
        "test_videos/empty.mp4",
        "test_videos/corrupted.avi"
    ]
    
    for filename in problematic_videos:
        if create_problematic_video(filename):
            created_videos.append(filename)
    
    # Create manifest
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_videos": len(created_videos),
        "videos": created_videos,
        "description": "Quick test videos for stimulus presentation testing"
    }
    
    with open("test_videos/quick_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n[DEBUG_LOG] Created {len(created_videos)} test videos")
    print("[DEBUG_LOG] Videos available for testing:")
    for video in created_videos:
        if Path(video).exists():
            size = Path(video).stat().st_size
            print(f"[DEBUG_LOG] - {Path(video).name} ({size} bytes)")
    
    return len(created_videos) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
