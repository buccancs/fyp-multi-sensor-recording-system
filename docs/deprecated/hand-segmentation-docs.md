# Hand Segmentation Feature Documentation

## Overview

The hand segmentation feature provides semantic segmentation capabilities for recorded video sessions to:
- Reduce data footprint by focusing on hand regions
- Enable neural networks to focus on areas of interest
- Support multiple segmentation algorithms 
- Run completely offline with no external dependencies

## Features

### Multiple Segmentation Methods
1. **MediaPipe Hands** (Recommended)
   - Uses Google's MediaPipe framework
   - Provides hand landmarks and segmentation
   - High accuracy and performance
   - Distinguishes left/right hands

2. **Color-based Segmentation**
   - Uses skin color detection in HSV space
   - Fast and lightweight
   - Good fallback option
   - No external ML dependencies

3. **Contour-based Segmentation** 
   - Uses edge detection and morphological operations
   - Detects hand-like shapes
   - Works in various lighting conditions
   - Purely OpenCV-based

### Output Options
- **Cropped Videos**: Extract hand regions into separate videos
- **Mask Videos**: Generate binary masks showing detected hands
- **Detection Logs**: JSON files with frame-by-frame detection data
- **Processing Metadata**: Complete processing statistics and timing

## Usage Examples

### Command Line Interface

```bash
# List available sessions
python hand_segmentation_cli.py list-sessions

# Process a session with MediaPipe
python hand_segmentation_cli.py process-session session_20250131_143022 \
    --method mediapipe \
    --confidence 0.7 \
    --max-hands 2 \
    --output-cropped \
    --output-masks

# Process a single video file
python hand_segmentation_cli.py process-video /path/to/video.mp4 \
    --method color_based \
    --output-cropped

# Check processing status
python hand_segmentation_cli.py status session_20250131_143022

# Clean up generated outputs
python hand_segmentation_cli.py cleanup session_20250131_143022
```

### Python API

```python
from hand_segmentation import (
    create_segmentation_engine,
    create_session_post_processor,
    SegmentationMethod
)

# Process a single video
engine = create_segmentation_engine(
    method="mediapipe",
    min_detection_confidence=0.5,
    max_num_hands=2,
    output_cropped=True,
    output_masks=True
)

if engine.initialize():
    result = engine.process_video("input_video.mp4", "output_directory")
    if result.success:
        print(f"Processed {result.processed_frames} frames")
        print(f"Detected {result.detected_hands_count} hands")
    engine.cleanup()

# Process entire session
processor = create_session_post_processor("recordings")
results = processor.process_session(
    "session_20250131_143022",
    method="mediapipe",
    output_cropped=True
)
```

### Integration with Session Manager

```python
from session.session_manager import SessionManager

# Create session manager
manager = SessionManager("recordings")

# Create and run a session
session = manager.create_session("test_session")
# ... record videos ...
completed_session = manager.end_session()

# Trigger post-processing with hand segmentation
results = manager.trigger_post_session_processing(
    enable_hand_segmentation=True,
    segmentation_method="mediapipe"
)

if results['hand_segmentation']['success']:
    print("Hand segmentation completed successfully!")
```

## Configuration Options

### SegmentationConfig Parameters

```python
from hand_segmentation import SegmentationConfig, SegmentationMethod

config = SegmentationConfig(
    method=SegmentationMethod.MEDIAPIPE,  # Algorithm to use
    min_detection_confidence=0.5,         # Detection threshold
    min_tracking_confidence=0.5,          # Tracking threshold  
    max_num_hands=2,                      # Maximum hands to detect
    output_cropped=True,                  # Generate cropped videos
    output_masks=True,                    # Generate mask videos
    crop_padding=20,                      # Padding around hands
    target_resolution=(640, 480),         # Optional resize target
    
    # Color-based method parameters
    skin_color_lower=(0, 20, 70),         # HSV lower bound
    skin_color_upper=(20, 255, 255),      # HSV upper bound
    
    # Contour-based method parameters
    contour_min_area=1000,                # Minimum contour area
    contour_max_area=50000                # Maximum contour area
)
```

## Output Structure

When processing a session, the following directory structure is created:

```
recordings/
└── session_20250131_143022/
    ├── session_metadata.json
    ├── webcam_recording.mp4
    ├── hand_segmentation_webcam_recording/
    │   ├── hands_cropped.mp4          # Cropped hand regions
    │   ├── hand_masks.mp4             # Binary masks
    │   ├── detection_log.json         # Frame-by-frame data
    │   └── processing_metadata.json   # Processing statistics
    └── hand_segmentation_summary_mediapipe.json
```

### Detection Log Format

```json
[
  {
    "frame": 1,
    "hands_detected": 2,
    "regions": [
      {
        "bbox": [120, 80, 150, 180],
        "confidence": 0.92,
        "hand_label": "Left"
      },
      {
        "bbox": [400, 100, 140, 170], 
        "confidence": 0.87,
        "hand_label": "Right"
      }
    ]
  }
]
```

## Performance Characteristics

| Method | Speed | Accuracy | Dependencies | Best Use Case |
|--------|-------|----------|--------------|---------------|
| MediaPipe | Medium | High | TensorFlow Lite | Production use, high accuracy needed |
| Color-based | Fast | Medium | OpenCV only | Quick processing, simple scenarios |
| Contour-based | Fast | Low-Medium | OpenCV only | Fallback, challenging lighting |

## Implementation Details

### Architecture
- Modular design with pluggable algorithms
- Clean separation between detection and I/O
- Integration with existing session management
- Comprehensive error handling and logging

### Dependencies
- **Core**: OpenCV, NumPy
- **MediaPipe**: mediapipe package (auto-installed)
- **Optional**: scikit-image for advanced processing

### Memory Usage
- Processes videos frame-by-frame to minimize memory usage
- Configurable output resolution to control file sizes
- Automatic cleanup of temporary resources

### Error Handling
- Graceful fallback when algorithms fail to initialize
- Detailed error messages and logging
- Processing continues even if some frames fail
- Comprehensive validation of inputs and outputs

## Testing

Run the comprehensive test suite:

```bash
cd PythonApp/src
python test_hand_segmentation.py -v
```

Or test individual components:

```bash
# Test with existing video
python hand_segmentation_cli.py process-video ../test_videos/quick_test_hd.mp4 \
    --method color_based --output-cropped --output-masks

# Quick functionality test
python -c "
from hand_segmentation import create_segmentation_engine
engine = create_segmentation_engine('mediapipe')
print('✅ MediaPipe available' if engine.initialize() else '❌ MediaPipe failed')
engine.cleanup()
"
```

## Troubleshooting

### Common Issues

1. **MediaPipe fails to initialize**
   ```bash
   pip install mediapipe
   ```

2. **Out of memory during processing**
   - Reduce target_resolution in config
   - Process videos in smaller segments
   - Disable mask output if not needed

3. **No hands detected**
   - Lower min_detection_confidence
   - Try different segmentation method
   - Check if video contains visible hands
   - Verify lighting conditions are adequate

4. **Poor detection quality**
   - Increase min_detection_confidence for fewer false positives
   - Adjust color thresholds for color-based method
   - Use MediaPipe for best results

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run processing with detailed output
engine = create_segmentation_engine("mediapipe")
# ... processing code ...
```

## Future Enhancements

- [ ] Real-time processing during recording
- [ ] Deep learning models for improved accuracy  
- [ ] Hand gesture recognition
- [ ] Multi-person hand tracking
- [ ] GPU acceleration support
- [ ] Integration with neural network training pipelines