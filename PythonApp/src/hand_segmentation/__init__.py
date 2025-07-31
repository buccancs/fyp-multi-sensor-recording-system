"""
Hand Segmentation Module for Multi-Sensor Recording System

This module provides hand semantic segmentation capabilities for post-session
video processing. It supports multiple segmentation algorithms and is designed
to reduce data footprint and enable neural networks to focus on areas of interest.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

from .segmentation_engine import HandSegmentationEngine, create_segmentation_engine
from .models import (
    MediaPipeHandSegmentation,
    ColorBasedHandSegmentation,
    ContourBasedHandSegmentation
)
from .post_processor import SessionPostProcessor, create_session_post_processor
from .utils import SegmentationConfig, SegmentationMethod, HandRegion, ProcessingResult

__all__ = [
    'HandSegmentationEngine',
    'create_segmentation_engine',
    'MediaPipeHandSegmentation', 
    'ColorBasedHandSegmentation',
    'ContourBasedHandSegmentation',
    'SessionPostProcessor',
    'create_session_post_processor',
    'SegmentationConfig',
    'SegmentationMethod',
    'HandRegion',
    'ProcessingResult'
]

__version__ = '1.0.0'