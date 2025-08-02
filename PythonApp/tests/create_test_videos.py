#!/usr/bin/env python3
"""
Test Video Creation Script for Enhanced Stimulus Presentation Testing

This script creates comprehensive test videos in multiple formats with various
characteristics to thoroughly test the enhanced stimulus controller's capabilities.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Purpose: Generate sample videos for comprehensive testing
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict

# Try to import video creation dependencies
try:
    import cv2
    import numpy as np

    CV2_AVAILABLE = True
    print("[DEBUG_LOG] OpenCV available for video creation")
except ImportError:
    CV2_AVAILABLE = False
    print("[DEBUG_LOG] OpenCV not available - limited video creation capabilities")

try:
    import requests

    REQUESTS_AVAILABLE = True
    print("[DEBUG_LOG] Requests available for downloading sample videos")
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[DEBUG_LOG] Requests not available - cannot download external samples")


class TestVideoCreator:
    """Creates comprehensive test videos for stimulus presentation testing."""

    def __init__(self, output_dir: str = "PythonApp/test_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video specifications for different test scenarios
        self.video_specs = {
            "short_hd": {
                "duration": 5,  # seconds
                "fps": 30,
                "resolution": (1280, 720),
                "description": "Short HD video for basic testing",
            },
            "medium_fhd": {
                "duration": 10,
                "fps": 30,
                "resolution": (1920, 1080),
                "description": "Medium Full HD video for standard testing",
            },
            "long_sd": {
                "duration": 30,
                "fps": 24,
                "resolution": (640, 480),
                "description": "Long SD video for extended testing",
            },
            "high_fps": {
                "duration": 5,
                "fps": 60,
                "resolution": (1280, 720),
                "description": "High frame rate video for performance testing",
            },
            "timing_test": {
                "duration": 10,
                "fps": 30,
                "resolution": (1920, 1080),
                "description": "Precision timing test video with frame markers",
            },
        }

        # Supported output formats
        self.output_formats = {
            "mp4": {"fourcc": "mp4v", "ext": ".mp4"},
            "avi": {"fourcc": "XVID", "ext": ".avi"},
            "mov": {"fourcc": "mp4v", "ext": ".mov"},
            "mkv": {"fourcc": "XVID", "ext": ".mkv"},
            "wmv": {"fourcc": "WMV2", "ext": ".wmv"},
        }

        # Sample video URLs for downloading
        self.sample_urls = {
            "big_buck_bunny_480p": "https://sample-videos.com/zip/10/mp4/480/SampleVideo_1280x720_1mb_mp4.mp4",
            "test_pattern": "https://file-examples.com/storage/fe68c1b7c66b7b59c5e8e7e/2017/10/file_example_MP4_1920_18MG.mp4",
        }

        self.created_videos = []
        self.video_manifest = {}

    def create_test_video(self, name: str, spec: Dict, format_name: str) -> bool:
        """Create a test video with specified characteristics."""
        if not CV2_AVAILABLE:
            print(f"[DEBUG_LOG] Cannot create {name} - OpenCV not available")
            return False

        try:
            format_info = self.output_formats[format_name]
            filename = f"{name}_{spec['resolution'][0]}x{spec['resolution'][1]}_{spec['fps']}fps{format_info['ext']}"
            filepath = self.output_dir / filename

            print(f"[DEBUG_LOG] Creating {filename}...")

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*format_info["fourcc"])
            out = cv2.VideoWriter(
                str(filepath), fourcc, spec["fps"], spec["resolution"]
            )

            if not out.isOpened():
                print(f"[DEBUG_LOG] Failed to open video writer for {filename}")
                return False

            total_frames = int(spec["duration"] * spec["fps"])

            for frame_num in range(total_frames):
                frame = self.create_test_frame(frame_num, total_frames, spec)
                out.write(frame)

                # Progress indicator
                if frame_num % (total_frames // 10) == 0:
                    progress = (frame_num / total_frames) * 100
                    print(f"[DEBUG_LOG] Progress: {progress:.0f}%")

            out.release()

            # Verify file was created
            if filepath.exists() and filepath.stat().st_size > 0:
                self.created_videos.append(str(filepath))
                self.video_manifest[filename] = {
                    "path": str(filepath),
                    "format": format_name,
                    "spec": spec,
                    "size_bytes": filepath.stat().st_size,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                print(
                    f"[DEBUG_LOG] Successfully created {filename} ({filepath.stat().st_size} bytes)"
                )
                return True
            else:
                print(f"[DEBUG_LOG] Failed to create {filename}")
                return False

        except Exception as e:
            print(f"[DEBUG_LOG] Error creating {name}: {e}")
            return False

    def create_test_frame(
        self, frame_num: int, total_frames: int, spec: Dict
    ) -> np.ndarray:
        """Create a test frame with timing and visual markers."""
        width, height = spec["resolution"]
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Calculate time and progress
        current_time = frame_num / spec["fps"]
        progress = frame_num / total_frames

        # Create gradient background
        for y in range(height):
            for x in range(width):
                # Color gradient based on position and time
                r = int(255 * (x / width) * (1 - progress))
                g = int(255 * (y / height) * progress)
                b = int(255 * progress)
                frame[y, x] = [b, g, r]  # BGR format for OpenCV

        # Add timing information
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(width, height) / 1000.0
        thickness = max(1, int(font_scale * 2))

        # Frame number
        cv2.putText(
            frame,
            f"Frame: {frame_num}",
            (50, 50),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )

        # Time stamp
        cv2.putText(
            frame,
            f"Time: {current_time:.3f}s",
            (50, 100),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )

        # Progress bar
        bar_width = width - 100
        bar_height = 20
        bar_x, bar_y = 50, height - 100

        # Background bar
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (100, 100, 100),
            -1,
        )

        # Progress fill
        fill_width = int(bar_width * progress)
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + fill_width, bar_y + bar_height),
            (0, 255, 0),
            -1,
        )

        # Second markers (vertical lines every second)
        if frame_num % spec["fps"] == 0:
            second = int(current_time)
            cv2.line(frame, (width // 2, 0), (width // 2, height), (255, 255, 0), 5)
            cv2.putText(
                frame,
                f"{second}s",
                (width // 2 - 30, height // 2),
                font,
                font_scale * 2,
                (255, 255, 0),
                thickness * 2,
            )

        # Add test pattern for timing precision
        if spec.get("description", "").startswith("Precision timing"):
            # Add precise timing markers
            millisecond = int((current_time * 1000) % 1000)
            cv2.putText(
                frame,
                f"{millisecond:03d}ms",
                (width - 200, 50),
                font,
                font_scale,
                (0, 255, 255),
                thickness,
            )

            # Add frame-accurate timing grid
            grid_size = 50
            for x in range(0, width, grid_size):
                cv2.line(frame, (x, 0), (x, height), (50, 50, 50), 1)
            for y in range(0, height, grid_size):
                cv2.line(frame, (0, y), (width, y), (50, 50, 50), 1)

        return frame

    def download_sample_videos(self) -> bool:
        """Download sample videos from external sources."""
        if not REQUESTS_AVAILABLE:
            print(
                "[DEBUG_LOG] Cannot download samples - requests library not available"
            )
            return False

        success_count = 0

        for name, url in self.sample_urls.items():
            try:
                print(f"[DEBUG_LOG] Downloading {name}...")
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()

                # Determine file extension from URL
                ext = Path(url).suffix or ".mp4"
                filename = f"sample_{name}{ext}"
                filepath = self.output_dir / filename

                # Download with progress
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(
                                    f"\r[DEBUG_LOG] Progress: {progress:.1f}%", end=""
                                )

                print(f"\n[DEBUG_LOG] Downloaded {filename} ({downloaded} bytes)")

                self.created_videos.append(str(filepath))
                self.video_manifest[filename] = {
                    "path": str(filepath),
                    "format": "downloaded",
                    "source_url": url,
                    "size_bytes": downloaded,
                    "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                success_count += 1

            except Exception as e:
                print(f"[DEBUG_LOG] Failed to download {name}: {e}")

        return success_count > 0

    def create_problematic_videos(self) -> bool:
        """Create videos with issues for error testing."""
        if not CV2_AVAILABLE:
            return False

        try:
            # Create a very short video (1 frame)
            short_path = self.output_dir / "problematic_too_short.mp4"
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(short_path), fourcc, 30, (640, 480))

            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                frame,
                "TOO SHORT",
                (200, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (255, 255, 255),
                3,
            )
            out.write(frame)
            out.release()

            self.created_videos.append(str(short_path))

            # Create an empty file for testing
            empty_path = self.output_dir / "problematic_empty.mp4"
            empty_path.touch()

            self.created_videos.append(str(empty_path))

            print("[DEBUG_LOG] Created problematic test videos")
            return True

        except Exception as e:
            print(f"[DEBUG_LOG] Error creating problematic videos: {e}")
            return False

    def save_manifest(self):
        """Save video manifest for test reference."""
        manifest_path = self.output_dir / "video_manifest.json"

        manifest_data = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_videos": len(self.video_manifest),
            "videos": self.video_manifest,
            "supported_formats": list(self.output_formats.keys()),
            "video_specs": self.video_specs,
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=2)

        print(f"[DEBUG_LOG] Saved video manifest: {manifest_path}")

    def create_all_test_videos(self) -> bool:
        """Create all test videos in all supported formats."""
        print("[DEBUG_LOG] Starting comprehensive test video creation...")

        total_created = 0
        total_attempted = 0

        # Create test videos in multiple formats
        for spec_name, spec in self.video_specs.items():
            for format_name in self.output_formats.keys():
                total_attempted += 1
                if self.create_test_video(spec_name, spec, format_name):
                    total_created += 1

        # Download sample videos
        if self.download_sample_videos():
            print("[DEBUG_LOG] Successfully downloaded sample videos")

        # Create problematic videos for error testing
        if self.create_problematic_videos():
            print("[DEBUG_LOG] Created problematic videos for error testing")

        # Save manifest
        self.save_manifest()

        print(
            f"[DEBUG_LOG] Video creation complete: {total_created}/{total_attempted} created successfully"
        )
        print(f"[DEBUG_LOG] Total videos available: {len(self.created_videos)}")

        return total_created > 0


def main():
    """Main function to create all test videos."""
    print("[DEBUG_LOG] Test Video Creation Script")
    print("=" * 50)

    # Check dependencies
    if not CV2_AVAILABLE:
        print(
            "[DEBUG_LOG] Warning: OpenCV not available - install with: pip install opencv-python"
        )

    if not REQUESTS_AVAILABLE:
        print(
            "[DEBUG_LOG] Warning: Requests not available - install with: pip install requests"
        )

    # Create video creator
    creator = TestVideoCreator()

    # Create all test videos
    success = creator.create_all_test_videos()

    if success:
        print("\n[DEBUG_LOG] Test video creation completed successfully!")
        print(f"[DEBUG_LOG] Videos created in: {creator.output_dir}")
        print(
            "[DEBUG_LOG] Use these videos for comprehensive stimulus presentation testing"
        )

        # List created videos
        print("\n[DEBUG_LOG] Created videos:")
        for video_path in creator.created_videos:
            video_name = Path(video_path).name
            size = Path(video_path).stat().st_size if Path(video_path).exists() else 0
            print(f"[DEBUG_LOG] - {video_name} ({size} bytes)")
    else:
        print("\n[DEBUG_LOG] Test video creation failed!")
        print("[DEBUG_LOG] Check dependencies and try again")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
