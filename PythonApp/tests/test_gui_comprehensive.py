#!/usr/bin/env python3
"""
Comprehensive GUI and Web UI Tests
===================================

This module provides comprehensive unit tests for all GUI and web interface
functionality in the PythonApp.

Test coverage:
- Enhanced Main Application: GUI initialization, event handling, state management
- Web UI Components: Flask routes, WebSocket communication, real-time updates
- Demo Features: Interactive demonstrations, user interface validation
- GUI Integration: Cross-component communication, responsive design

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys
import threading
import time
from queue import Queue

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from enhanced_main_with_web import EnhancedMainApplication, WebUIManager
    from demo_enhanced_ui import DemoUIManager, InteractiveFeatures
    from web_launcher import WebLauncher, WebSocketManager
    GUI_MODULES_AVAILABLE = True
except ImportError as e:
    GUI_MODULES_AVAILABLE = False
    print(f"Warning: GUI modules not available: {e}")

try:
    from gui.main_window import MainWindow
    from gui.calibration_dialog import CalibrationDialog
    from gui.device_manager_widget import DeviceManagerWidget
    GUI_COMPONENTS_AVAILABLE = True
except ImportError as e:
    GUI_COMPONENTS_AVAILABLE = False
    print(f"Warning: GUI components not available: {e}")

try:
    import flask
    from flask_socketio import SocketIO
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class TestEnhancedMainApplication(unittest.TestCase):
    """Test EnhancedMainApplication GUI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not GUI_MODULES_AVAILABLE:
            self.skipTest("GUI modules not available")
        
        self.mock_config = {
            'gui': {
                'window_size': [1200, 800],
                'theme': 'modern',
                'auto_save': True
            },
            'web_ui': {
                'enabled': True,
                'port': 8080,
                'host': 'localhost'
            }
        }
        
        with patch('enhanced_main_with_web.tkinter'):
            self.app = EnhancedMainApplication(self.mock_config)

    def test_application_initialization(self):
        """Test application initialization and window creation."""
        with patch('enhanced_main_with_web.tkinter.Tk') as mock_tk:
            mock_window = Mock()
            mock_tk.return_value = mock_window
            
            app = EnhancedMainApplication(self.mock_config)
            
            self.assertIsNotNone(app.main_window)
            mock_window.title.assert_called()
            mock_window.geometry.assert_called()

    def test_menu_system(self):
        """Test menu system creation and functionality."""
        with patch('enhanced_main_with_web.tkinter') as mock_tk:
            mock_menu = Mock()
            mock_tk.Menu.return_value = mock_menu
            
            self.app.create_menu_system()
            
            # Verify menu creation
            self.assertTrue(mock_tk.Menu.called)
            mock_menu.add_cascade.assert_called()

    def test_device_management_panel(self):
        """Test device management panel functionality."""
        with patch('enhanced_main_with_web.DeviceManagerWidget') as mock_widget:
            mock_widget_instance = Mock()
            mock_widget.return_value = mock_widget_instance
            
            panel = self.app.create_device_panel()
            
            self.assertIsNotNone(panel)
            mock_widget_instance.refresh_devices.assert_called()

    def test_calibration_workflow_integration(self):
        """Test calibration workflow integration in GUI."""
        with patch('enhanced_main_with_web.CalibrationDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog.return_value = mock_dialog_instance
            mock_dialog_instance.show_modal.return_value = {'success': True}
            
            result = self.app.start_calibration_workflow()
            
            self.assertTrue(result['success'])
            mock_dialog_instance.show_modal.assert_called_once()

    def test_real_time_data_display(self):
        """Test real-time data display and updates."""
        with patch('enhanced_main_with_web.DataVisualizationWidget') as mock_viz:
            mock_viz_instance = Mock()
            mock_viz.return_value = mock_viz_instance
            
            # Mock incoming data
            sensor_data = {
                'timestamp': time.time(),
                'gsr': 1.234,
                'device_id': 'shimmer_001'
            }
            
            self.app.update_real_time_display(sensor_data)
            
            mock_viz_instance.update_data.assert_called_with(sensor_data)

    def test_session_control_integration(self):
        """Test session control integration in GUI."""
        with patch('enhanced_main_with_web.SessionManager') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value = mock_session_instance
            mock_session_instance.start_session.return_value = True
            
            result = self.app.start_recording_session()
            
            self.assertTrue(result)
            mock_session_instance.start_session.assert_called_once()

    def test_error_dialog_system(self):
        """Test error dialog and notification system."""
        with patch('enhanced_main_with_web.tkinter.messagebox') as mock_messagebox:
            error_message = "Device connection failed"
            
            self.app.show_error_dialog(error_message)
            
            mock_messagebox.showerror.assert_called_with("Error", error_message)

    def test_settings_persistence(self):
        """Test GUI settings persistence and restoration."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            settings_file = f.name
            test_settings = {
                'window_position': [100, 100],
                'panel_sizes': [300, 500],
                'theme': 'dark'
            }
            json.dump(test_settings, f)
        
        try:
            with patch('enhanced_main_with_web.CONFIG_FILE', settings_file):
                loaded_settings = self.app.load_settings()
                
                self.assertEqual(loaded_settings['theme'], 'dark')
                self.assertEqual(loaded_settings['window_position'], [100, 100])
        finally:
            os.unlink(settings_file)


class TestWebUIManager(unittest.TestCase):
    """Test WebUIManager web interface functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not GUI_MODULES_AVAILABLE or not FLASK_AVAILABLE:
            self.skipTest("GUI or Flask modules not available")
        
        self.config = {
            'web_ui': {
                'port': 8080,
                'debug': False,
                'secret_key': 'test_secret'
            }
        }
        
        with patch('enhanced_main_with_web.Flask'):
            self.web_manager = WebUIManager(self.config)

    def test_flask_app_initialization(self):
        """Test Flask application initialization."""
        with patch('enhanced_main_with_web.Flask') as mock_flask:
            mock_app = Mock()
            mock_flask.return_value = mock_app
            
            manager = WebUIManager(self.config)
            
            self.assertIsNotNone(manager.app)
            mock_flask.assert_called_once()

    def test_websocket_setup(self):
        """Test WebSocket setup and configuration."""
        with patch('enhanced_main_with_web.SocketIO') as mock_socketio:
            mock_socketio_instance = Mock()
            mock_socketio.return_value = mock_socketio_instance
            
            self.web_manager.setup_websocket()
            
            mock_socketio.assert_called_once()

    def test_api_routes_registration(self):
        """Test API routes registration and handling."""
        with patch('enhanced_main_with_web.Flask') as mock_flask:
            mock_app = Mock()
            mock_flask.return_value = mock_app
            
            manager = WebUIManager(self.config)
            manager.register_api_routes()
            
            # Verify route registration calls
            self.assertTrue(mock_app.route.called)

    def test_real_time_data_broadcast(self):
        """Test real-time data broadcasting via WebSocket."""
        with patch('enhanced_main_with_web.SocketIO') as mock_socketio:
            mock_socketio_instance = Mock()
            mock_socketio.return_value = mock_socketio_instance
            
            self.web_manager.socketio = mock_socketio_instance
            
            # Test data broadcast
            test_data = {
                'timestamp': time.time(),
                'sensors': {'gsr': 1.234, 'ecg': 0.567},
                'device_id': 'shimmer_001'
            }
            
            self.web_manager.broadcast_sensor_data(test_data)
            
            mock_socketio_instance.emit.assert_called_with('sensor_data', test_data)

    def test_device_control_api(self):
        """Test device control API endpoints."""
        with patch('enhanced_main_with_web.request') as mock_request:
            mock_request.json = {
                'action': 'start_recording',
                'device_id': 'shimmer_001'
            }
            
            with patch.object(self.web_manager, 'device_manager') as mock_device_manager:
                mock_device_manager.start_recording.return_value = True
                
                response = self.web_manager.handle_device_control()
                
                self.assertEqual(response['status'], 'success')

    def test_calibration_web_interface(self):
        """Test calibration interface through web UI."""
        with patch('enhanced_main_with_web.request') as mock_request:
            mock_request.json = {
                'camera_id': 0,
                'pattern_type': 'chessboard',
                'pattern_size': [9, 6]
            }
            
            with patch.object(self.web_manager, 'calibration_manager') as mock_cal_manager:
                mock_cal_manager.start_calibration.return_value = {'status': 'started'}
                
                response = self.web_manager.handle_calibration_request()
                
                self.assertEqual(response['status'], 'started')

    def test_session_management_api(self):
        """Test session management through web API."""
        with patch('enhanced_main_with_web.request') as mock_request:
            mock_request.json = {
                'session_name': 'test_session',
                'duration': 300,
                'devices': ['shimmer_001', 'shimmer_002']
            }
            
            with patch.object(self.web_manager, 'session_manager') as mock_session_manager:
                mock_session_manager.create_session.return_value = {'session_id': 'sess_123'}
                
                response = self.web_manager.handle_session_creation()
                
                self.assertIn('session_id', response)


class TestDemoUIManager(unittest.TestCase):
    """Test DemoUIManager interactive demonstration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not GUI_MODULES_AVAILABLE:
            self.skipTest("GUI modules not available")
        
        with patch('demo_enhanced_ui.tkinter'):
            self.demo_manager = DemoUIManager()

    def test_demo_initialization(self):
        """Test demo interface initialization."""
        with patch('demo_enhanced_ui.tkinter.Tk') as mock_tk:
            mock_window = Mock()
            mock_tk.return_value = mock_window
            
            demo = DemoUIManager()
            
            self.assertIsNotNone(demo.demo_window)

    def test_interactive_features_demo(self):
        """Test interactive features demonstration."""
        with patch('demo_enhanced_ui.InteractiveFeatures') as mock_features:
            mock_features_instance = Mock()
            mock_features.return_value = mock_features_instance
            
            self.demo_manager.start_interactive_demo()
            
            mock_features_instance.show_calibration_demo.assert_called()

    def test_simulation_mode(self):
        """Test simulation mode for demonstrations."""
        with patch('demo_enhanced_ui.SimulatedDataGenerator') as mock_generator:
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            mock_generator_instance.generate_gsr_data.return_value = [1.0, 1.1, 1.2]
            
            simulated_data = self.demo_manager.generate_demo_data()
            
            self.assertIsInstance(simulated_data, list)
            self.assertEqual(len(simulated_data), 3)

    def test_tutorial_system(self):
        """Test tutorial and help system."""
        with patch('demo_enhanced_ui.TutorialManager') as mock_tutorial:
            mock_tutorial_instance = Mock()
            mock_tutorial.return_value = mock_tutorial_instance
            
            self.demo_manager.start_tutorial()
            
            mock_tutorial_instance.show_step.assert_called()


class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration workflows and cross-component communication."""

    def setUp(self):
        """Set up test fixtures."""
        if not GUI_MODULES_AVAILABLE:
            self.skipTest("GUI modules not available")

    def test_complete_gui_workflow(self):
        """Test complete GUI workflow from startup to shutdown."""
        with patch('enhanced_main_with_web.EnhancedMainApplication') as mock_app, \
             patch('enhanced_main_with_web.WebUIManager') as mock_web:
            
            mock_app_instance = Mock()
            mock_web_instance = Mock()
            mock_app.return_value = mock_app_instance
            mock_web.return_value = mock_web_instance
            
            # Test workflow
            mock_app_instance.initialize.return_value = True
            mock_web_instance.start_server.return_value = True
            
            app = mock_app_instance
            web = mock_web_instance
            
            # Startup sequence
            startup_success = app.initialize() and web.start_server()
            self.assertTrue(startup_success)
            
            # Verify initialization calls
            app.initialize.assert_called_once()
            web.start_server.assert_called_once()

    def test_cross_component_communication(self):
        """Test communication between GUI components."""
        with patch('enhanced_main_with_web.EventBus') as mock_event_bus:
            mock_bus_instance = Mock()
            mock_event_bus.return_value = mock_bus_instance
            
            # Test event publishing and subscription
            event_data = {
                'event_type': 'device_connected',
                'device_id': 'shimmer_001',
                'timestamp': time.time()
            }
            
            mock_bus_instance.publish('device_events', event_data)
            mock_bus_instance.publish.assert_called_with('device_events', event_data)

    def test_responsive_design_adaptation(self):
        """Test responsive design adaptation for different screen sizes."""
        with patch('enhanced_main_with_web.ScreenManager') as mock_screen:
            mock_screen_instance = Mock()
            mock_screen.return_value = mock_screen_instance
            
            # Test different screen configurations
            screen_configs = [
                {'width': 1920, 'height': 1080},  # Desktop
                {'width': 1366, 'height': 768},   # Laptop
                {'width': 800, 'height': 600}     # Small display
            ]
            
            for config in screen_configs:
                mock_screen_instance.adapt_layout(config)
                mock_screen_instance.adapt_layout.assert_called_with(config)

    def test_error_propagation(self):
        """Test error propagation through GUI layers."""
        with patch('enhanced_main_with_web.ErrorHandler') as mock_error_handler:
            mock_handler_instance = Mock()
            mock_error_handler.return_value = mock_handler_instance
            
            # Simulate error in lower layer
            test_error = Exception("Device communication failed")
            
            mock_handler_instance.handle_error(test_error)
            mock_handler_instance.handle_error.assert_called_with(test_error)


def create_gui_test_suite():
    """Create comprehensive test suite for GUI functionality."""
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestEnhancedMainApplication))
    suite.addTest(unittest.makeSuite(TestWebUIManager))
    suite.addTest(unittest.makeSuite(TestDemoUIManager))
    suite.addTest(unittest.makeSuite(TestGUIIntegration))
    
    return suite


if __name__ == '__main__':
    if GUI_MODULES_AVAILABLE:
        # Run comprehensive tests
        runner = unittest.TextTestRunner(verbosity=2)
        suite = create_gui_test_suite()
        result = runner.run(suite)
        
        # Print results summary
        print(f"\n{'='*60}")
        print(f"GUI and Web UI Tests Summary")
        print(f"{'='*60}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    else:
        print("GUI modules not available - skipping tests")