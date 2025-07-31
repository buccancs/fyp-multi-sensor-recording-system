"""
Utility classes and functions for hand segmentation module.

This module contains configuration classes, data structures, and helper functions
used throughout the hand segmentation system.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import numpy as np


class SegmentationMethod(Enum):
    """Available hand segmentation methods."""
    MEDIAPIPE = "mediapipe"
    COLOR_BASED = "color_based"
    CONTOUR_BASED = "contour_based"


@dataclass
class HandRegion:
    """
    Represents a detected hand region in a video frame.
    
    Attributes:
        bbox: Bounding box as (x, y, width, height)
        mask: Binary mask for the hand region
        landmarks: Hand landmarks (if available)
        confidence: Detection confidence score
        hand_label: 'Left' or 'Right' hand label
    """
    bbox: Tuple[int, int, int, int]
    mask: Optional[np.ndarray] = None
    landmarks: Optional[List[Tuple[float, float]]] = None
    confidence: float = 0.0
    hand_label: str = "Unknown"


@dataclass 
class SegmentationConfig:
    """
    Configuration for hand segmentation processing.
    
    Attributes:
        method: Segmentation method to use
        min_detection_confidence: Minimum confidence for detection
        min_tracking_confidence: Minimum confidence for tracking
        max_num_hands: Maximum number of hands to detect
        output_cropped: Whether to output cropped hand regions
        output_masks: Whether to output segmentation masks
        crop_padding: Padding around detected hand regions
        target_resolution: Target resolution for processing
    """
    method: SegmentationMethod = SegmentationMethod.MEDIAPIPE
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    max_num_hands: int = 2
    output_cropped: bool = True
    output_masks: bool = True
    crop_padding: int = 20
    target_resolution: Optional[Tuple[int, int]] = None
    
    # Color-based segmentation parameters
    skin_color_lower: Tuple[int, int, int] = (0, 20, 70)
    skin_color_upper: Tuple[int, int, int] = (20, 255, 255)
    
    # Contour-based segmentation parameters  
    contour_min_area: int = 1000
    contour_max_area: int = 50000


@dataclass
class ProcessingResult:
    """
    Result of hand segmentation processing on a video.
    
    Attributes:
        input_video_path: Path to input video
        output_directory: Directory containing output files
        processed_frames: Number of frames processed
        detected_hands_count: Total number of hand detections
        processing_time: Total processing time in seconds
        output_files: Dictionary of generated output files
        success: Whether processing completed successfully
        error_message: Error message if processing failed
    """
    input_video_path: str
    output_directory: str
    processed_frames: int = 0
    detected_hands_count: int = 0
    processing_time: float = 0.0
    output_files: Dict[str, str] = None
    success: bool = False
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = {}


def create_bounding_box_from_landmarks(landmarks: List[Tuple[float, float]], 
                                     frame_width: int, 
                                     frame_height: int,
                                     padding: int = 20) -> Tuple[int, int, int, int]:
    """
    Create a bounding box from hand landmarks.
    
    Args:
        landmarks: List of (x, y) landmark coordinates (normalized 0-1)
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
        padding: Padding to add around the bounding box
        
    Returns:
        Bounding box as (x, y, width, height)
    """
    if not landmarks:
        return (0, 0, 0, 0)
    
    # Convert normalized coordinates to pixel coordinates
    x_coords = [int(point[0] * frame_width) for point in landmarks]
    y_coords = [int(point[1] * frame_height) for point in landmarks]
    
    # Find bounding box
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Add padding
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(frame_width, max_x + padding)
    max_y = min(frame_height, max_y + padding)
    
    width = max_x - min_x
    height = max_y - min_y
    
    return (min_x, min_y, width, height)


def crop_frame_to_region(frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop a frame to a specific region.
    
    Args:
        frame: Input frame
        bbox: Bounding box as (x, y, width, height)
        
    Returns:
        Cropped frame
    """
    x, y, w, h = bbox
    return frame[y:y+h, x:x+w]


def resize_frame(frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Resize a frame to target size while maintaining aspect ratio.
    
    Args:
        frame: Input frame
        target_size: Target size as (width, height)
        
    Returns:
        Resized frame
    """
    import cv2
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)


def create_hand_mask_from_landmarks(landmarks: List[Tuple[float, float]], 
                                  frame_shape: Tuple[int, int]) -> np.ndarray:
    """
    Create a binary mask from hand landmarks using convex hull.
    
    Args:
        landmarks: List of (x, y) landmark coordinates (normalized 0-1)
        frame_shape: Frame shape as (height, width)
        
    Returns:
        Binary mask
    """
    import cv2
    
    height, width = frame_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    if not landmarks:
        return mask
    
    # Convert normalized coordinates to pixel coordinates
    points = []
    for point in landmarks:
        x = int(point[0] * width)
        y = int(point[1] * height)
        points.append([x, y])
    
    # Create convex hull and fill
    points = np.array(points, dtype=np.int32)
    hull = cv2.convexHull(points)
    cv2.fillPoly(mask, [hull], 255)
    
    return mask


def save_processing_metadata(result: ProcessingResult, output_path: str):
    """
    Save processing metadata to a JSON file.
    
    Args:
        result: Processing result
        output_path: Path to save metadata file
    """
    import json
    from datetime import datetime
    
    metadata = {
        "input_video": result.input_video_path,
        "output_directory": result.output_directory,
        "processed_frames": result.processed_frames,
        "detected_hands_count": result.detected_hands_count,
        "processing_time": result.processing_time,
        "output_files": result.output_files,
        "success": result.success,
        "error_message": result.error_message,
        "processed_at": datetime.now().isoformat()
    }
    
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)