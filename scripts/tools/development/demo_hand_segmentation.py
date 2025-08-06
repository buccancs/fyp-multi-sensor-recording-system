#!/usr/bin/env python3

import cv2
import numpy as np
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp', 'src'))

from hand_segmentation import (
    create_segmentation_engine,
    SessionPostProcessor,
    SegmentationMethod
)


def create_demo_video_with_hands(output_path: str, frames: int = 60):
    print(f"Creating demo video: {output_path}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, 30, (640, 480))

    for frame_idx in range(frames):
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 50

        for i in range(0, 640, 40):
            cv2.line(frame, (i, 0), (i, 480), (60, 60, 60), 1)
        for i in range(0, 480, 40):
            cv2.line(frame, (0, i), (640, i), (60, 60, 60), 1)

        for hand_idx in range(2):
            t = frame_idx / frames * 2 * np.pi
            if hand_idx == 0:
                center_x = int(200 + 80 * np.cos(t))
                center_y = int(200 + 60 * np.sin(t))
                color = [15, 120, 180]
            else:
                center_x = int(450 + 60 * np.cos(t))
                center_y = int(200 + 40 * np.sin(2*t))
                color = [20, 100, 170]

            cv2.circle(frame, (center_x, center_y), 35, color, -1)

            for finger_idx in range(5):
                angle = finger_idx * 0.6 + t * 0.3
                finger_x = center_x + int(30 * np.cos(angle))
                finger_y = center_y + int(30 * np.sin(angle))
                finger_length = 20 - finger_idx * 2

                cv2.circle(frame, (finger_x, finger_y), finger_length // 2, color, -1)

                tip_x = finger_x + int(finger_length * np.cos(angle))
                tip_y = finger_y + int(finger_length * np.sin(angle))
                cv2.circle(frame, (tip_x, tip_y), 6,
                          [c + 20 for c in color], -1)

        noise = np.random.randint(-5, 6, frame.shape, dtype=np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        writer.write(frame)

    writer.release()
    print(f"Demo video created with {frames} frames")


def demonstrate_method(method_name: str, video_path: str):
    print(f"\n{'='*60}")
    print(f"DEMONSTRATING: {method_name.upper()} METHOD")
    print(f"{'='*60}")

    engine = create_segmentation_engine(
        method=method_name,
        output_cropped=True,
        output_masks=True,
        min_detection_confidence=0.3,
        max_num_hands=2
    )

    if not engine.initialize():
        print(f"[ERROR] Failed to initialize {method_name} engine")
        return

    output_dir = f"demo_output_{method_name}"
    os.makedirs(output_dir, exist_ok=True)

    result = engine.process_video(video_path, output_dir)

    if result.success:
        print(f"✅ SUCCESS: {method_name} processing completed")
        print(f"   📹 Frames processed: {result.processed_frames}")
        print(f"   🖐️  Hand detections: {result.detected_hands_count}")
        print(f"   ⏱️  Processing time: {result.processing_time:.2f}s")
        print(f"   📁 Output directory: {result.output_directory}")

        if result.output_files:
            print(f"   📄 Generated files:")
            for file_type, file_path in result.output_files.items():
                file_size = os.path.getsize(file_path) / 1024
                print(f"      - {file_type}: {Path(file_path).name} ({file_size:.1f} KB)")
    else:
        print(f"❌ FAILED: {method_name} processing failed")
        print(f"   Error: {result.error_message}")

    engine.cleanup()


def compare_methods():
    print(f"\n{'='*80}")
    print("HAND SEGMENTATION METHODS COMPARISON")
    print(f"{'='*80}")

    demo_video = "demo_hands_video.mp4"
    if not os.path.exists(demo_video):
        create_demo_video_with_hands(demo_video, frames=90)

    methods = ['color_based', 'contour_based', 'mediapipe']
    results = {}

    for method in methods:
        try:
            print(f"\n🔍 Testing {method} method...")

            engine = create_segmentation_engine(
                method=method,
                output_cropped=False,
                output_masks=False,
                min_detection_confidence=0.3
            )

            if engine.initialize():
                result = engine.process_video(demo_video, f"comparison_{method}")
                results[method] = {
                    'success': result.success,
                    'detections': result.detected_hands_count,
                    'time': result.processing_time,
                    'error': result.error_message
                }
                engine.cleanup()
            else:
                results[method] = {
                    'success': False,
                    'detections': 0,
                    'time': 0,
                    'error': 'Failed to initialize'
                }

        except Exception as e:
            results[method] = {
                'success': False,
                'detections': 0,
                'time': 0,
                'error': str(e)
            }

    print(f"\n{'='*80}")
    print("COMPARISON RESULTS")
    print(f"{'='*80}")
    print(f"{'Method':<15} {'Status':<10} {'Detections':<12} {'Time (s)':<10} {'Notes'}")
    print("-" * 80)

    for method, result in results.items():
        status = "✅ OK" if result['success'] else "❌ FAIL"
        detections = result['detections'] if result['success'] else "-"
        time_str = f"{result['time']:.2f}" if result['success'] else "-"
        notes = result['error'] if not result['success'] else "Success"

        print(f"{method:<15} {status:<10} {detections:<12} {time_str:<10} {notes}")

    successful_methods = [m for m, r in results.items() if r['success']]
    if successful_methods:
        print(f"\n📊 PERFORMANCE SUMMARY:")
        fastest = min(successful_methods, key=lambda m: results[m]['time'])
        most_detections = max(successful_methods, key=lambda m: results[m]['detections'])

        print(f"   🏃 Fastest method: {fastest} ({results[fastest]['time']:.2f}s)")
        print(f"   🎯 Most detections: {most_detections} ({results[most_detections]['detections']} hands)")


def main():
    print("🖐️  HAND SEGMENTATION DEMONSTRATION")
    print("=" * 80)
    print("This demo showcases the hand segmentation capabilities")
    print("of the Multi-Sensor Recording System.")
    print()

    test_videos = [
        "../test_videos/quick_test_hd.mp4",
        "test_videos/quick_test_hd.mp4",
        "quick_test_hd.mp4"
    ]

    demo_video = None
    for video_path in test_videos:
        if os.path.exists(video_path):
            demo_video = video_path
            break

    if demo_video:
        print(f"📹 Using existing test video: {demo_video}")

        for method in ['color_based', 'mediapipe', 'contour_based']:
            try:
                demonstrate_method(method, demo_video)
            except Exception as e:
                print(f"❌ Error demonstrating {method}: {e}")
    else:
        print("📹 Creating custom demo video...")

    try:
        compare_methods()
    except Exception as e:
        print(f"❌ Error in method comparison: {e}")

    print(f"\n{'='*80}")
    print("🎉 DEMONSTRATION COMPLETE!")
    print("Check the generated output directories for results:")
    print("   - demo_output_* directories contain processed videos")
    print("   - comparison_* directories contain performance data")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()