"""
Comprehensive tests for StimulusManager functionality

Tests cover multi-monitor detection, stimulus presentation, timing controls,
audio-visual coordination, and event handling.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import unittest
import tempfile
import shutil
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stimulus_manager import (
    StimulusManager, StimulusConfig, StimulusEvent, 
    MonitorInfo, StimulusWindow
)


class TestStimulusManager(unittest.TestCase):
    """Test suite for StimulusManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        
        # Mock QApplication for testing
        self.mock_app = Mock()
        self.mock_screen1 = Mock()
        self.mock_screen1.name.return_value = "Primary Monitor"
        self.mock_screen1.geometry.return_value = Mock()
        self.mock_screen1.geometry.return_value.width.return_value = 1920
        self.mock_screen1.geometry.return_value.height.return_value = 1080
        self.mock_screen1.logicalDotsPerInch.return_value = 96.0
        
        self.mock_screen2 = Mock()
        self.mock_screen2.name.return_value = "Secondary Monitor"
        self.mock_screen2.geometry.return_value = Mock()
        self.mock_screen2.geometry.return_value.width.return_value = 1920
        self.mock_screen2.geometry.return_value.height.return_value = 1080
        self.mock_screen2.logicalDotsPerInch.return_value = 96.0
        
        self.mock_app.screens.return_value = [self.mock_screen1, self.mock_screen2]
        
        # Create StimulusManager instance
        self.stimulus_manager = StimulusManager(logger=self.mock_logger)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'stimulus_manager'):
            self.stimulus_manager.cleanup()

    def test_initialization(self):
        """Test StimulusManager initialization"""
        # Test initial state
        self.assertFalse(self.stimulus_manager.is_initialized)
        self.assertEqual(len(self.stimulus_manager.available_monitors), 0)
        
        # Verify logger calls
        self.mock_logger.info.assert_called()

    @patch('stimulus_manager.QApplication.instance')
    @patch('stimulus_manager.QDesktopWidget')
    def test_initialization_with_monitors(self, mock_desktop, mock_app_instance):
        """Test initialization with monitor detection"""
        # Setup mocks
        mock_app_instance.return_value = self.mock_app
        mock_desktop.return_value.primaryScreen.return_value = 0
        
        # Test initialization
        result = self.stimulus_manager.initialize()
        self.assertTrue(result)
        self.assertTrue(self.stimulus_manager.is_initialized)
        self.assertEqual(len(self.stimulus_manager.available_monitors), 2)
        
        # Verify monitor information
        monitor1 = self.stimulus_manager.available_monitors[0]
        self.assertEqual(monitor1.monitor_id, 0)
        self.assertEqual(monitor1.name, "Primary Monitor")
        self.assertTrue(monitor1.is_primary)
        
        monitor2 = self.stimulus_manager.available_monitors[1]
        self.assertEqual(monitor2.monitor_id, 1)
        self.assertEqual(monitor2.name, "Secondary Monitor")
        self.assertFalse(monitor2.is_primary)

    @patch('stimulus_manager.QApplication.instance')
    def test_initialization_no_app(self, mock_app_instance):
        """Test initialization failure when no QApplication"""
        mock_app_instance.return_value = None
        
        result = self.stimulus_manager.initialize()
        self.assertFalse(result)
        self.assertFalse(self.stimulus_manager.is_initialized)

    def test_monitor_utilities(self):
        """Test monitor utility methods"""
        # Setup test monitors
        self.stimulus_manager.available_monitors = [
            MonitorInfo(0, "Primary", Mock(), True, 96.0),
            MonitorInfo(1, "Secondary", Mock(), False, 96.0)
        ]
        
        # Test monitor count
        self.assertEqual(self.stimulus_manager.get_monitor_count(), 2)
        
        # Test get monitor info
        monitor_info = self.stimulus_manager.get_monitor_info(0)
        self.assertIsNotNone(monitor_info)
        self.assertEqual(monitor_info.monitor_id, 0)
        self.assertTrue(monitor_info.is_primary)
        
        # Test invalid monitor ID
        invalid_monitor = self.stimulus_manager.get_monitor_info(5)
        self.assertIsNone(invalid_monitor)
        
        # Test primary monitor ID
        primary_id = self.stimulus_manager.get_primary_monitor_id()
        self.assertEqual(primary_id, 0)
        
        # Test secondary monitor ID
        secondary_id = self.stimulus_manager.get_secondary_monitor_id()
        self.assertEqual(secondary_id, 1)

    def test_stimulus_config(self):
        """Test StimulusConfig dataclass"""
        # Test default configuration
        config = StimulusConfig()
        self.assertEqual(config.stimulus_type, "video")
        self.assertEqual(config.duration_ms, 5000)
        self.assertTrue(config.audio_enabled)
        self.assertTrue(config.fullscreen)
        self.assertEqual(config.monitor_id, 0)
        
        # Test custom configuration
        custom_config = StimulusConfig(
            stimulus_type="text",
            text_content="Test Stimulus",
            duration_ms=3000,
            monitor_id=1,
            font_size=64
        )
        self.assertEqual(custom_config.stimulus_type, "text")
        self.assertEqual(custom_config.text_content, "Test Stimulus")
        self.assertEqual(custom_config.duration_ms, 3000)
        self.assertEqual(custom_config.monitor_id, 1)
        self.assertEqual(custom_config.font_size, 64)

    @patch('stimulus_manager.StimulusWindow')
    def test_present_stimulus_not_initialized(self, mock_window):
        """Test stimulus presentation when not initialized"""
        config = StimulusConfig(stimulus_type="pattern")
        
        result = self.stimulus_manager.present_stimulus(config)
        self.assertFalse(result)
        
        # Verify error logged
        self.mock_logger.error.assert_called()

    @patch('stimulus_manager.StimulusWindow')
    def test_present_stimulus_invalid_monitor(self, mock_window):
        """Test stimulus presentation with invalid monitor ID"""
        # Setup initialized manager
        self.stimulus_manager.is_initialized = True
        self.stimulus_manager.available_monitors = [
            MonitorInfo(0, "Primary", Mock(), True, 96.0)
        ]
        
        # Test with invalid monitor ID
        config = StimulusConfig(monitor_id=5)
        result = self.stimulus_manager.present_stimulus(config)
        self.assertFalse(result)

    @patch('stimulus_manager.StimulusWindow')
    @patch('stimulus_manager.QTimer')
    def test_present_stimulus_success(self, mock_timer_class, mock_window_class):
        """Test successful stimulus presentation"""
        # Setup initialized manager
        self.stimulus_manager.is_initialized = True
        self.stimulus_manager.available_monitors = [
            MonitorInfo(0, "Primary", Mock(), True, 96.0)
        ]
        
        # Setup mocks
        mock_window = Mock()
        mock_window_class.return_value = mock_window
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        # Test stimulus presentation
        config = StimulusConfig(
            stimulus_type="text",
            text_content="Test",
            duration_ms=2000
        )
        
        result = self.stimulus_manager.present_stimulus(config)
        self.assertTrue(result)
        
        # Verify window created and shown
        mock_window_class.assert_called_once()
        mock_window.show.assert_called_once()
        mock_window.start_presentation.assert_called_once()
        
        # Verify timer setup
        mock_timer.start.assert_called_once_with(2000)
        
        # Verify event recorded
        self.assertEqual(len(self.stimulus_manager.presentation_history), 1)
        event = self.stimulus_manager.presentation_history[0]
        self.assertEqual(event.event_type, "stimulus_start")
        self.assertEqual(event.monitor_id, 0)

    def test_stop_stimulus(self):
        """Test stopping stimulus presentation"""
        # Setup active stimulus
        mock_window = Mock()
        self.stimulus_manager.stimulus_windows[0] = mock_window
        mock_timer = Mock()
        self.stimulus_manager.presentation_timers[0] = mock_timer
        
        # Test stop stimulus
        result = self.stimulus_manager.stop_stimulus(0)
        self.assertTrue(result)
        
        # Verify cleanup
        mock_window.stop_presentation.assert_called_once()
        mock_window.close.assert_called_once()
        mock_timer.stop.assert_called_once()
        
        # Verify window removed
        self.assertNotIn(0, self.stimulus_manager.stimulus_windows)
        self.assertNotIn(0, self.stimulus_manager.presentation_timers)

    def test_stop_stimulus_not_active(self):
        """Test stopping stimulus when none active"""
        result = self.stimulus_manager.stop_stimulus(0)
        self.assertFalse(result)
        
        # Verify warning logged
        self.mock_logger.warning.assert_called()

    def test_stop_all_stimuli(self):
        """Test stopping all active stimuli"""
        # Setup multiple active stimuli
        mock_window1 = Mock()
        mock_window2 = Mock()
        self.stimulus_manager.stimulus_windows[0] = mock_window1
        self.stimulus_manager.stimulus_windows[1] = mock_window2
        
        # Test stop all
        self.stimulus_manager.stop_all_stimuli()
        
        # Verify all windows cleaned up
        self.assertEqual(len(self.stimulus_manager.stimulus_windows), 0)

    @patch('stimulus_manager.StimulusWindow')
    def test_present_synchronized_stimuli(self, mock_window_class):
        """Test synchronized stimulus presentation"""
        # Setup initialized manager
        self.stimulus_manager.is_initialized = True
        self.stimulus_manager.available_monitors = [
            MonitorInfo(0, "Primary", Mock(), True, 96.0),
            MonitorInfo(1, "Secondary", Mock(), False, 96.0)
        ]
        
        # Setup mocks
        mock_window1 = Mock()
        mock_window2 = Mock()
        mock_window_class.side_effect = [mock_window1, mock_window2]
        
        # Test synchronized presentation
        configs = [
            StimulusConfig(monitor_id=0, duration_ms=3000),
            StimulusConfig(monitor_id=1, duration_ms=2000)
        ]
        
        result = self.stimulus_manager.present_synchronized_stimuli(configs)
        self.assertTrue(result)
        
        # Verify both windows created
        self.assertEqual(mock_window_class.call_count, 2)
        mock_window1.show.assert_called_once()
        mock_window2.show.assert_called_once()
        mock_window1.start_presentation.assert_called_once()
        mock_window2.start_presentation.assert_called_once()
        
        # Verify events recorded
        self.assertEqual(len(self.stimulus_manager.presentation_history), 2)

    def test_event_callbacks(self):
        """Test event callback functionality"""
        # Add callback
        callback_data = []
        def test_callback(event):
            callback_data.append(event)
        
        self.stimulus_manager.add_event_callback(test_callback)
        
        # Create and add test event
        test_event = StimulusEvent(
            event_type="test_event",
            timestamp=time.time(),
            monitor_id=0,
            stimulus_config=StimulusConfig()
        )
        self.stimulus_manager.presentation_history.append(test_event)
        
        # Simulate callback execution (would normally happen in present_stimulus)
        for callback in self.stimulus_manager.event_callbacks:
            callback(test_event)
        
        # Verify callback was called
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0], test_event)

    def test_presentation_history(self):
        """Test presentation history tracking"""
        # Test empty history
        history = self.stimulus_manager.get_presentation_history()
        self.assertEqual(len(history), 0)
        
        # Add test events
        event1 = StimulusEvent("start", time.time(), 0, StimulusConfig())
        event2 = StimulusEvent("stop", time.time(), 0, StimulusConfig())
        
        self.stimulus_manager.presentation_history.extend([event1, event2])
        
        # Test history retrieval
        history = self.stimulus_manager.get_presentation_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], event1)
        self.assertEqual(history[1], event2)
        
        # Verify it's a copy (not reference)
        history.append(StimulusEvent("extra", time.time(), 0, StimulusConfig()))
        original_history = self.stimulus_manager.get_presentation_history()
        self.assertEqual(len(original_history), 2)

    def test_cleanup(self):
        """Test cleanup functionality"""
        # Setup active stimuli and timers
        mock_window = Mock()
        mock_timer = Mock()
        self.stimulus_manager.stimulus_windows[0] = mock_window
        self.stimulus_manager.presentation_timers[0] = mock_timer
        self.stimulus_manager.event_callbacks.append(lambda x: None)
        self.stimulus_manager.is_initialized = True
        
        # Test cleanup
        self.stimulus_manager.cleanup()
        
        # Verify cleanup state
        self.assertFalse(self.stimulus_manager.is_initialized)
        self.assertEqual(len(self.stimulus_manager.stimulus_windows), 0)
        self.assertEqual(len(self.stimulus_manager.presentation_timers), 0)
        self.assertEqual(len(self.stimulus_manager.event_callbacks), 0)
        
        # Verify timer stopped
        mock_timer.stop.assert_called_once()

    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test present_stimulus with exception
        self.stimulus_manager.is_initialized = True
        self.stimulus_manager.available_monitors = [Mock()]
        
        with patch('stimulus_manager.StimulusWindow', side_effect=Exception("Test error")):
            config = StimulusConfig()
            result = self.stimulus_manager.present_stimulus(config)
            self.assertFalse(result)
            
            # Verify error logged
            self.mock_logger.error.assert_called()

    def test_stimulus_event_dataclass(self):
        """Test StimulusEvent dataclass"""
        config = StimulusConfig(stimulus_type="test")
        event = StimulusEvent(
            event_type="test_event",
            timestamp=123456.789,
            monitor_id=1,
            stimulus_config=config,
            duration_actual_ms=2500.0
        )
        
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.timestamp, 123456.789)
        self.assertEqual(event.monitor_id, 1)
        self.assertEqual(event.stimulus_config, config)
        self.assertEqual(event.duration_actual_ms, 2500.0)

    def test_monitor_info_dataclass(self):
        """Test MonitorInfo dataclass"""
        geometry = Mock()
        monitor = MonitorInfo(
            monitor_id=2,
            name="Test Monitor",
            geometry=geometry,
            is_primary=True,
            dpi=120.0
        )
        
        self.assertEqual(monitor.monitor_id, 2)
        self.assertEqual(monitor.name, "Test Monitor")
        self.assertEqual(monitor.geometry, geometry)
        self.assertTrue(monitor.is_primary)
        self.assertEqual(monitor.dpi, 120.0)


class TestStimulusManagerIntegration(unittest.TestCase):
    """Integration tests for StimulusManager"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.mock_logger = Mock()
        
    def tearDown(self):
        """Clean up integration test fixtures"""
        pass

    def test_main_application_integration(self):
        """Test integration with main application patterns"""
        # This test verifies that StimulusManager can be used
        # in the same way as would be expected in main_backup.py
        
        # Create manager
        manager = StimulusManager(logger=self.mock_logger)
        
        try:
            # Test basic functionality without Qt dependencies
            self.assertFalse(manager.is_initialized)
            self.assertEqual(manager.get_monitor_count(), 0)
            
            # Test configuration creation
            config = StimulusConfig(
                stimulus_type="text",
                text_content="Welcome to the experiment",
                duration_ms=5000,
                monitor_id=0
            )
            
            self.assertEqual(config.stimulus_type, "text")
            self.assertEqual(config.duration_ms, 5000)
            
            # Test event callback setup
            events = []
            def event_handler(event):
                events.append(event)
            
            manager.add_event_callback(event_handler)
            self.assertEqual(len(manager.event_callbacks), 1)
            
        finally:
            # Cleanup
            manager.cleanup()


if __name__ == '__main__':
    # Configure test logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)
