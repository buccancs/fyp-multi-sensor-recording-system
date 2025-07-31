"""
Hand segmentation models and algorithms.

This module contains different implementations of hand segmentation algorithms,
including MediaPipe-based, color-based, and contour-based approaches.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np
import cv2

from .utils import HandRegion, SegmentationConfig, create_bounding_box_from_landmarks, create_hand_mask_from_landmarks


class BaseHandSegmentation(ABC):
    """Abstract base class for hand segmentation algorithms."""
    
    def __init__(self, config: SegmentationConfig):
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the segmentation model. Returns True if successful."""
        pass
    
    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> List[HandRegion]:
        """Process a single frame and return detected hand regions."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up resources."""
        pass


class MediaPipeHandSegmentation(BaseHandSegmentation):
    """MediaPipe-based hand segmentation implementation."""
    
    def __init__(self, config: SegmentationConfig):
        super().__init__(config)
        self.hands = None
        self.mp_hands = None
        self.mp_draw = None
    
    def initialize(self) -> bool:
        """Initialize MediaPipe hands model."""
        try:
            import mediapipe as mp
            
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
            
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=self.config.max_num_hands,
                min_detection_confidence=self.config.min_detection_confidence,
                min_tracking_confidence=self.config.min_tracking_confidence
            )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize MediaPipe hands: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> List[HandRegion]:
        """Process frame using MediaPipe hands detection."""
        if not self.is_initialized:
            return []
        
        hand_regions = []
        height, width = frame.shape[:2]
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Extract landmarks
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append((landmark.x, landmark.y))
                
                # Create bounding box
                bbox = create_bounding_box_from_landmarks(
                    landmarks, width, height, self.config.crop_padding
                )
                
                # Create hand mask
                mask = None
                if self.config.output_masks:
                    mask = create_hand_mask_from_landmarks(landmarks, frame.shape)
                
                # Get hand label (left/right)
                hand_label = "Unknown"
                if results.multi_handedness:
                    if idx < len(results.multi_handedness):
                        hand_label = results.multi_handedness[idx].classification[0].label
                
                # Create hand region
                hand_region = HandRegion(
                    bbox=bbox,
                    mask=mask,
                    landmarks=landmarks,
                    confidence=results.multi_handedness[idx].classification[0].score if results.multi_handedness and idx < len(results.multi_handedness) else 1.0,
                    hand_label=hand_label
                )
                
                hand_regions.append(hand_region)
        
        return hand_regions
    
    def cleanup(self):
        """Clean up MediaPipe resources."""
        if self.hands:
            self.hands.close()
            self.hands = None
        self.is_initialized = False


class ColorBasedHandSegmentation(BaseHandSegmentation):
    """Color-based hand segmentation using skin color detection."""
    
    def __init__(self, config: SegmentationConfig):
        super().__init__(config)
    
    def initialize(self) -> bool:
        """Initialize color-based segmentation (no special initialization needed)."""
        self.is_initialized = True
        return True
    
    def process_frame(self, frame: np.ndarray) -> List[HandRegion]:
        """Process frame using color-based skin detection."""
        if not self.is_initialized:
            return []
        
        hand_regions = []
        height, width = frame.shape[:2]
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for skin color
        lower = np.array(self.config.skin_color_lower)
        upper = np.array(self.config.skin_color_upper)
        skin_mask = cv2.inRange(hsv, lower, upper)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and create hand regions
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.config.contour_min_area <= area <= self.config.contour_max_area:
                # Create bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Add padding
                x = max(0, x - self.config.crop_padding)
                y = max(0, y - self.config.crop_padding)
                w = min(width - x, w + 2 * self.config.crop_padding)
                h = min(height - y, h + 2 * self.config.crop_padding)
                
                bbox = (x, y, w, h)
                
                # Create mask for this region
                mask = None
                if self.config.output_masks:
                    mask = np.zeros((height, width), dtype=np.uint8)
                    cv2.fillPoly(mask, [contour], 255)
                
                # Estimate confidence based on contour properties
                confidence = min(1.0, area / self.config.contour_max_area)
                
                hand_region = HandRegion(
                    bbox=bbox,
                    mask=mask,
                    landmarks=None,  # No landmarks available
                    confidence=confidence,
                    hand_label="Unknown"  # Cannot determine handedness
                )
                
                hand_regions.append(hand_region)
        
        # Sort by confidence and return top max_num_hands
        hand_regions.sort(key=lambda x: x.confidence, reverse=True)
        return hand_regions[:self.config.max_num_hands]
    
    def cleanup(self):
        """Clean up resources."""
        self.is_initialized = False


class ContourBasedHandSegmentation(BaseHandSegmentation):
    """Contour-based hand segmentation using edge detection and morphology."""
    
    def __init__(self, config: SegmentationConfig):
        super().__init__(config)
    
    def initialize(self) -> bool:
        """Initialize contour-based segmentation."""
        self.is_initialized = True
        return True
    
    def process_frame(self, frame: np.ndarray) -> List[HandRegion]:
        """Process frame using contour-based detection."""
        if not self.is_initialized:
            return []
        
        hand_regions = []
        height, width = frame.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours and create hand regions
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.config.contour_min_area <= area <= self.config.contour_max_area:
                # Calculate additional contour properties
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                # Use compactness as a hand-like shape indicator
                compactness = (4 * np.pi * area) / (perimeter * perimeter)
                
                # Filter by compactness (hands tend to have medium compactness)
                if 0.1 <= compactness <= 0.8:
                    # Create bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Add padding
                    x = max(0, x - self.config.crop_padding)
                    y = max(0, y - self.config.crop_padding)
                    w = min(width - x, w + 2 * self.config.crop_padding)
                    h = min(height - y, h + 2 * self.config.crop_padding)
                    
                    bbox = (x, y, w, h)
                    
                    # Create mask
                    mask = None
                    if self.config.output_masks:
                        mask = np.zeros((height, width), dtype=np.uint8)
                        cv2.fillPoly(mask, [contour], 255)
                    
                    # Calculate confidence based on area and compactness
                    area_score = min(1.0, area / self.config.contour_max_area)
                    shape_score = compactness
                    confidence = (area_score + shape_score) / 2.0
                    
                    hand_region = HandRegion(
                        bbox=bbox,
                        mask=mask,
                        landmarks=None,
                        confidence=confidence,
                        hand_label="Unknown"
                    )
                    
                    hand_regions.append(hand_region)
        
        # Sort by confidence and return top max_num_hands
        hand_regions.sort(key=lambda x: x.confidence, reverse=True)
        return hand_regions[:self.config.max_num_hands]
    
    def cleanup(self):
        """Clean up resources."""
        self.is_initialized = False