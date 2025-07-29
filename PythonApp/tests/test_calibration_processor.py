"""
Unit tests for CalibrationProcessor component.

Tests OpenCV calibration algorithms and pattern detection functionality.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calibration.calibration_processor import CalibrationProcessor


class TestCalibrationProcessor:
    """Test CalibrationProcessor functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.processor = CalibrationProcessor()
    
    def test_processor_initialization(self):
        """Test basic processor initialization."""
        assert self.processor is not None
        assert hasattr(self.processor, 'pattern_size')
        assert hasattr(self.processor, 'square_size')
    
    @patch('cv2.findChessboardCorners')
    def test_find_calibration_corners_success(self, mock_find_corners):
        """Test successful corner detection."""
        mock_find_corners.return_value = (True, np.array([[100, 100], [200, 200]]))
        
        test_image = np.zeros((480, 640), dtype=np.uint8)
        result = self.processor.find_calibration_corners(test_image)
        
        assert result['success'] is True
        assert 'corners' in result
        mock_find_corners.assert_called_once()
    
    @patch('cv2.findChessboardCorners')
    def test_find_calibration_corners_failure(self, mock_find_corners):
        """Test corner detection failure."""
        mock_find_corners.return_value = (False, None)
        
        test_image = np.zeros((480, 640), dtype=np.uint8)
        result = self.processor.find_calibration_corners(test_image)
        
        assert result['success'] is False
        assert 'error' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
