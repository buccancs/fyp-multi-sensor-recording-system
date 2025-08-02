#!/usr/bin/env python3
"""
Web Dashboard Integration for Multi-Sensor Recording System

This module provides integration between the new web-based dashboard and the existing
PyQt5 desktop application. It allows the desktop application to optionally start
a web server that provides real-time monitoring and control capabilities.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import logging
import os
import sys
import threading
import time
from typing import Optional, Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from web_ui.web_dashboard import WebDashboardServer
except ImportError:
    WebDashboardServer = None

try:
    from web_ui.web_controller import WebController, create_web_controller_with_real_components
    WEB_CONTROLLER_AVAILABLE = True
except ImportError:
    WebController = None
    create_web_controller_with_real_components = None
    WEB_CONTROLLER_AVAILABLE = False

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging if utils not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class WebDashboardIntegration:
    """
    Integration layer between the web dashboard and existing desktop application.
    
    This class provides a bridge that allows the existing PyQt5 application to
    optionally enable web-based monitoring and control without requiring
    significant changes to the existing codebase.
    """
    
    def __init__(self, enable_web_ui: bool = True, web_port: int = 5000, 
                 main_controller=None, session_manager=None, shimmer_manager=None, 
                 android_device_manager=None):
        """
        Initialize the web dashboard integration.
        
        Args:
            enable_web_ui: Whether to enable the web UI (default: True)
            web_port: Port for the web server (default: 5000)
            main_controller: MainController instance from the desktop app (PyQt-based) or None
            session_manager: SessionManager instance from the desktop app
            shimmer_manager: ShimmerManager instance from the desktop app
            android_device_manager: AndroidDeviceManager instance from the desktop app
        """
        self.enable_web_ui = enable_web_ui
        self.web_port = web_port
        self.web_server: Optional[WebDashboardServer] = None
        self.is_running = False
        
        # Core application components (injected from desktop app or created for web-only mode)
        self.main_controller = main_controller
        self.session_manager = session_manager
        self.shimmer_manager = shimmer_manager
        self.android_device_manager = android_device_manager
        
        # Web controller for non-PyQt environments
        self.web_controller = None
        self.using_web_controller = False
        
        # Data bridges for synchronization
        self.device_status_cache = {}
        self.session_info_cache = {}
        self.connected_signals = False
        
        # Determine if we need to use WebController (when main_controller is None or PyQt not available)
        if self.main_controller is None and WEB_CONTROLLER_AVAILABLE:
            logger.info("Creating WebController for real component integration (PyQt not available)")
            self.web_controller = create_web_controller_with_real_components()
            self.using_web_controller = True
            # Update references from web controller
            self.session_manager = self.web_controller.session_manager
            self.shimmer_manager = self.web_controller.shimmer_manager
            self.android_device_manager = self.web_controller.android_device_manager
        
        logger.info(f"Web Dashboard Integration initialized (enabled: {enable_web_ui})")
        logger.info(f"Using WebController: {self.using_web_controller}")
        logger.info(f"Connected components: MainController={main_controller is not None}, "
                   f"SessionManager={self.session_manager is not None}, "
                   f"ShimmerManager={self.shimmer_manager is not None}, "
                   f"AndroidDeviceManager={self.android_device_manager is not None})")
    
    def start_web_dashboard(self) -> bool:
        """
        Start the web dashboard server.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.enable_web_ui:
            logger.info("Web UI is disabled, not starting dashboard")
            return False
        
        if WebDashboardServer is None:
            logger.error("Web dashboard dependencies not available")
            return False
        
        if self.is_running:
            logger.warning("Web dashboard is already running")
            return True
        
        try:
            # Create and start the web server
            self.web_server = WebDashboardServer(host='0.0.0.0', port=self.web_port, debug=False)
            self.web_server.start_server()
            self.is_running = True
            
            logger.info(f"Web dashboard started on http://localhost:{self.web_port}")
            
            # Connect to real application components if available
            controller_to_use = self.web_controller if self.using_web_controller else self.main_controller
            
            if controller_to_use is not None:
                self._connect_to_controller(controller_to_use)
                logger.info(f"Connected web dashboard to {'WebController' if self.using_web_controller else 'MainController'}")
            
            if self.session_manager is not None:
                self._connect_to_session_manager()
                logger.info("Connected web dashboard to SessionManager")
            
            if self.shimmer_manager is not None:
                self._connect_to_shimmer_manager()
                logger.info("Connected web dashboard to ShimmerManager")
            
            if self.android_device_manager is not None:
                self._connect_to_android_device_manager()
                logger.info("Connected web dashboard to AndroidDeviceManager")
            
            # Initialize with current state
            self._sync_initial_state()
            
            # Only use demo data if no real components are connected at all
            if (controller_to_use is None and self.session_manager is None and 
                self.shimmer_manager is None and self.android_device_manager is None):
                logger.warning("No real application components connected, using demo data")
                self._start_demo_data_generation()
            else:
                logger.info("Web dashboard connected to real application components")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web dashboard: {e}")
            return False
    
    def stop_web_dashboard(self):
        """Stop the web dashboard server."""
        if not self.is_running or not self.web_server:
            return
        
        try:
            # Stop web controller monitoring if we're using it
            if self.using_web_controller and self.web_controller:
                self.web_controller.stop_monitoring()
            
            self.web_server.stop_server()
            self.web_server = None
            self.is_running = False
            logger.info("Web dashboard stopped")
        except Exception as e:
            logger.error(f"Error stopping web dashboard: {e}")
    
    def update_device_status(self, device_type: str, device_id: str, status_data: Dict[str, Any]):
        """
        Update device status in both local cache and web dashboard.
        
        Args:
            device_type: Type of device ('android_devices', 'usb_webcams', 'shimmer_sensors')
            device_id: Unique identifier for the device
            status_data: Status information dictionary
        """
        # Cache the status locally
        if device_type not in self.device_status_cache:
            self.device_status_cache[device_type] = {}
        self.device_status_cache[device_type][device_id] = status_data
        
        # Update web dashboard if running
        if self.is_running and self.web_server:
            try:
                self.web_server.update_device_status(device_type, device_id, status_data)
            except Exception as e:
                logger.error(f"Failed to update web dashboard device status: {e}")
    
    def update_session_info(self, session_data: Dict[str, Any]):
        """
        Update session information in both local cache and web dashboard.
        
        Args:
            session_data: Session information dictionary
        """
        self.session_info_cache = session_data.copy()
        
        # Update web dashboard if running
        if self.is_running and self.web_server:
            try:
                self.web_server.session_info = session_data
                self.web_server._broadcast_session_update()
            except Exception as e:
                logger.error(f"Failed to update web dashboard session info: {e}")
    
    def update_sensor_data(self, device_id: str, sensor_type: str, value: float):
        """
        Update real-time sensor data in the web dashboard.
        
        Args:
            device_id: Device identifier
            sensor_type: Type of sensor data
            value: Sensor reading value
        """
        if self.is_running and self.web_server:
            try:
                self.web_server.update_sensor_data(device_id, sensor_type, value)
            except Exception as e:
                logger.error(f"Failed to update web dashboard sensor data: {e}")
    
    def _connect_to_controller(self, controller):
        """Connect to either MainController (PyQt) or WebController signals for real-time updates."""
        if controller is None or self.connected_signals:
            return
        
        try:
            # Connect to device status signals
            controller.device_connected.connect(self._on_device_connected)
            controller.device_disconnected.connect(self._on_device_disconnected)
            controller.device_status_received.connect(self._on_device_status_received)
            
            # Connect to session signals
            controller.session_status_changed.connect(self._on_session_status_changed)
            controller.recording_started.connect(self._on_recording_started)
            controller.recording_stopped.connect(self._on_recording_stopped)
            
            # Connect to data signals
            controller.sensor_data_received.connect(self._on_sensor_data_received)
            
            # Connect to error signals
            controller.error_occurred.connect(self._on_error_occurred)
            
            self.connected_signals = True
            controller_type = "WebController" if self.using_web_controller else "MainController"
            logger.info(f"Connected to {controller_type} signals")
            
        except Exception as e:
            logger.error(f"Failed to connect to controller signals: {e}")
    
    def _connect_to_main_controller(self):
        """Connect to MainController signals for real-time updates (legacy method)."""
        self._connect_to_controller(self.main_controller)
    
    def _connect_to_session_manager(self):
        """Connect to SessionManager for session information."""
        if self.session_manager is None:
            return
        
        try:
            # Get current session info
            if hasattr(self.session_manager, 'current_session') and self.session_manager.current_session:
                session_info = {
                    'active': True,
                    'session_id': self.session_manager.current_session.get('session_id'),
                    'start_time': self.session_manager.current_session.get('start_time'),
                    'session_name': self.session_manager.current_session.get('session_name'),
                    'recording_devices': self.session_manager.current_session.get('connected_devices', []),
                    'data_collected': self.session_manager.current_session.get('file_counts', {})
                }
                self.update_session_info(session_info)
            
            logger.info("Connected to SessionManager")
            
        except Exception as e:
            logger.error(f"Failed to connect to SessionManager: {e}")
    
    def _connect_to_shimmer_manager(self):
        """Connect to ShimmerManager for Shimmer device status."""
        if self.shimmer_manager is None:
            return
        
        try:
            # Get current Shimmer device status
            if hasattr(self.shimmer_manager, 'get_all_device_status'):
                shimmer_devices = self.shimmer_manager.get_all_device_status()
                for device_id, status in shimmer_devices.items():
                    self.update_device_status('shimmer_sensors', device_id, {
                        'status': 'connected' if status.get('is_connected', False) else 'disconnected',
                        'battery': status.get('battery_level', 0),
                        'signal_strength': status.get('signal_strength', 0),
                        'recording': status.get('is_recording', False),
                        'sample_rate': status.get('sampling_rate', 0),
                        'mac_address': status.get('mac_address', 'Unknown')
                    })
            
            logger.info("Connected to ShimmerManager")
            
        except Exception as e:
            logger.error(f"Failed to connect to ShimmerManager: {e}")
    
    def _connect_to_android_device_manager(self):
        """Connect to AndroidDeviceManager for Android device status."""
        if self.android_device_manager is None:
            return
        
        try:
            # Get current Android device status
            if hasattr(self.android_device_manager, 'get_connected_devices'):
                android_devices = self.android_device_manager.get_connected_devices()
                for device_id, device_info in android_devices.items():
                    self.update_device_status('android_devices', device_id, {
                        'status': 'connected',
                        'capabilities': device_info.get('capabilities', []),
                        'battery': device_info.get('status', {}).get('battery_level', 0),
                        'temperature': device_info.get('status', {}).get('temperature', 0),
                        'recording': device_info.get('is_recording', False),
                        'last_heartbeat': device_info.get('last_heartbeat', 0)
                    })
            
            logger.info("Connected to AndroidDeviceManager")
            
        except Exception as e:
            logger.error(f"Failed to connect to AndroidDeviceManager: {e}")
    
    def _sync_initial_state(self):
        """Synchronize initial state from real application components."""
        try:
            # Update PC controller status
            self.update_device_status('pc_controller', 'main', {
                'status': 'running',
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'connected_devices': len(self.device_status_cache.get('android_devices', {})) + 
                                   len(self.device_status_cache.get('shimmer_sensors', {}))
            })
            
            logger.info("Initial state synchronized")
            
        except Exception as e:
            logger.error(f"Failed to sync initial state: {e}")
    
    # Signal handlers for MainController events
    def _on_device_connected(self, device_id: str, capabilities: list):
        """Handle device connected signal."""
        device_type = self._determine_device_type(device_id, capabilities)
        self.update_device_status(device_type, device_id, {
            'status': 'connected',
            'capabilities': capabilities,
            'connection_time': time.time()
        })
    
    def _on_device_disconnected(self, device_id: str):
        """Handle device disconnected signal."""
        # Find and update the device in the appropriate category
        for device_type in ['android_devices', 'usb_webcams', 'shimmer_sensors']:
            if device_id in self.device_status_cache.get(device_type, {}):
                self.update_device_status(device_type, device_id, {
                    'status': 'disconnected',
                    'disconnection_time': time.time()
                })
                break
    
    def _on_device_status_received(self, device_id: str, status_data: dict):
        """Handle device status update signal."""
        device_type = self._determine_device_type_from_status(device_id, status_data)
        self.update_device_status(device_type, device_id, status_data)
    
    def _on_session_status_changed(self, session_id: str, is_active: bool):
        """Handle session status change signal."""
        session_info = {
            'active': is_active,
            'session_id': session_id if is_active else None,
            'start_time': time.time() if is_active else None,
            'end_time': time.time() if not is_active else None
        }
        self.update_session_info(session_info)
    
    def _on_recording_started(self, session_id: str):
        """Handle recording started signal."""
        session_info = {
            'active': True,
            'session_id': session_id,
            'start_time': time.time(),
            'recording_devices': list(self.device_status_cache.get('android_devices', {}).keys()) +
                               list(self.device_status_cache.get('shimmer_sensors', {}).keys())
        }
        self.update_session_info(session_info)
    
    def _on_recording_stopped(self, session_id: str, duration: float):
        """Handle recording stopped signal."""
        session_info = {
            'active': False,
            'session_id': None,
            'end_time': time.time(),
            'duration': duration
        }
        self.update_session_info(session_info)
    
    def _on_sensor_data_received(self, device_id: str, sensor_data: dict):
        """Handle real-time sensor data."""
        # Extract GSR data if available
        if 'gsr' in sensor_data:
            self.update_sensor_data(device_id, 'gsr', sensor_data['gsr'])
        
        # Extract thermal data if available
        if 'thermal' in sensor_data:
            self.update_sensor_data(device_id, 'thermal', sensor_data['thermal'])
        
        # Extract other sensor data
        for sensor_type, value in sensor_data.items():
            if isinstance(value, (int, float)):
                self.update_sensor_data(device_id, sensor_type, value)
    
    def _on_preview_frame_received(self, device_id: str, frame_type: str, base64_data: str):
        """Handle preview frame data (for future web streaming)."""
        # This could be used for video streaming to the web interface
        pass
    
    def _on_error_occurred(self, component: str, error_message: str):
        """Handle error signals from the application."""
        logger.error(f"Application error in {component}: {error_message}")
        # Could update web UI with error notifications
    
    def get_web_dashboard_url(self) -> Optional[str]:
        """
        Get the URL of the web dashboard.
        
        Returns:
            Dashboard URL if running, None otherwise
        """
        if self.is_running:
            return f"http://localhost:{self.web_port}"
        return None

    def _determine_device_type(self, device_id: str, capabilities: list) -> str:
        """Determine device type based on ID and capabilities."""
        if 'shimmer' in device_id.lower() or 'gsr' in capabilities:
            return 'shimmer_sensors'
        elif 'android' in device_id.lower() or 'phone' in device_id.lower():
            return 'android_devices'
        elif 'webcam' in device_id.lower() or 'camera' in device_id.lower():
            return 'usb_webcams'
        else:
            return 'android_devices'  # Default fallback
    
    def _determine_device_type_from_status(self, device_id: str, status_data: dict) -> str:
        """Determine device type from status data."""
        if 'mac_address' in status_data or 'shimmer' in device_id.lower():
            return 'shimmer_sensors'
        elif 'android' in device_id.lower() or 'phone' in device_id.lower():
            return 'android_devices'
        elif 'webcam' in device_id.lower() or 'resolution' in status_data:
            return 'usb_webcams'
        else:
            return 'android_devices'  # Default fallback
    
    def _start_demo_data_generation(self):
        """Start generating demo data for the web dashboard."""
        if not self.is_running or not self.web_server:
            return
        
        def generate_demo_data():
            """Generate realistic demo data for the dashboard."""
            import random
            import time
            
            while self.is_running:
                try:
                    # Simulate Android device status
                    self.update_device_status('android_devices', 'device_1', {
                        'status': 'connected',
                        'battery': random.randint(20, 100),
                        'temperature': round(random.uniform(35, 45), 1),
                        'recording': random.choice([True, False])
                    })
                    
                    self.update_device_status('android_devices', 'device_2', {
                        'status': 'connected',
                        'battery': random.randint(20, 100),
                        'temperature': round(random.uniform(35, 45), 1),
                        'recording': random.choice([True, False])
                    })
                    
                    # Simulate USB webcam status
                    self.update_device_status('usb_webcams', 'webcam_1', {
                        'status': 'active',
                        'resolution': '4K',
                        'fps': 30,
                        'recording': random.choice([True, False])
                    })
                    
                    self.update_device_status('usb_webcams', 'webcam_2', {
                        'status': 'active',
                        'resolution': '1080p',
                        'fps': 60,
                        'recording': random.choice([True, False])
                    })
                    
                    # Simulate Shimmer sensor status
                    self.update_device_status('shimmer_sensors', 'shimmer_1', {
                        'status': 'connected',
                        'battery': random.randint(30, 100),
                        'signal_strength': random.randint(60, 100),
                        'recording': random.choice([True, False]),
                        'sample_rate': 256,
                        'mac_address': '00:06:66:EA:12:34'
                    })
                    
                    self.update_device_status('shimmer_sensors', 'shimmer_2', {
                        'status': 'connected',
                        'battery': random.randint(30, 100),
                        'signal_strength': random.randint(60, 100),
                        'recording': random.choice([True, False]),
                        'sample_rate': 256,
                        'mac_address': '00:06:66:EA:56:78'
                    })
                    
                    # Simulate PC controller status
                    self.update_device_status('pc_controller', 'main', {
                        'status': 'monitoring',
                        'cpu_usage': random.randint(10, 80),
                        'memory_usage': random.randint(40, 90),
                        'disk_usage': random.randint(20, 70)
                    })
                    
                    # Simulate real-time sensor data
                    self.update_sensor_data('android_1', 'gsr', random.uniform(0.1, 2.0))
                    self.update_sensor_data('android_1', 'thermal', random.uniform(25, 35))
                    self.update_sensor_data('android_2', 'gsr', random.uniform(0.1, 2.0))
                    self.update_sensor_data('android_2', 'thermal', random.uniform(25, 35))
                    self.update_sensor_data('shimmer_1', '', random.uniform(0.5, 3.0))
                    self.update_sensor_data('shimmer_2', '', random.uniform(0.5, 3.0))
                    
                    time.sleep(2)  # Update every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Error generating demo data: {e}")
                    time.sleep(5)  # Wait longer on error
        
        # Start demo data generation in a separate thread
        demo_thread = threading.Thread(target=generate_demo_data, daemon=True)
        demo_thread.start()
        logger.info("Started demo data generation for web dashboard")


# Singleton instance for easy access
_web_integration_instance: Optional[WebDashboardIntegration] = None


def get_web_integration(enable_web_ui: bool = True, web_port: int = 5000, 
                       main_controller=None, session_manager=None, shimmer_manager=None, 
                       android_device_manager=None) -> WebDashboardIntegration:
    """
    Get or create the web dashboard integration instance.
    
    Args:
        enable_web_ui: Whether to enable the web UI
        web_port: Port for the web server
        main_controller: MainController instance from the desktop app
        session_manager: SessionManager instance from the desktop app
        shimmer_manager: ShimmerManager instance from the desktop app
        android_device_manager: AndroidDeviceManager instance from the desktop app
    
    Returns:
        WebDashboardIntegration instance
    """
    global _web_integration_instance
    
    if _web_integration_instance is None:
        _web_integration_instance = WebDashboardIntegration(
            enable_web_ui, web_port, main_controller, session_manager, 
            shimmer_manager, android_device_manager
        )
    
    return _web_integration_instance


def start_web_dashboard(enable_web_ui: bool = True, web_port: int = 5000,
                       main_controller=None, session_manager=None, shimmer_manager=None, 
                       android_device_manager=None) -> bool:
    """
    Convenience function to start the web dashboard.
    
    Args:
        enable_web_ui: Whether to enable the web UI
        web_port: Port for the web server
        main_controller: MainController instance from the desktop app
        session_manager: SessionManager instance from the desktop app
        shimmer_manager: ShimmerManager instance from the desktop app
        android_device_manager: AndroidDeviceManager instance from the desktop app
    
    Returns:
        True if started successfully, False otherwise
    """
    integration = get_web_integration(
        enable_web_ui, web_port, main_controller, session_manager, 
        shimmer_manager, android_device_manager
    )
    return integration.start_web_dashboard()


def stop_web_dashboard():
    """Convenience function to stop the web dashboard."""
    global _web_integration_instance
    
    if _web_integration_instance:
        _web_integration_instance.stop_web_dashboard()


if __name__ == '__main__':
    # Demo mode - start web dashboard with demo data
    print("Starting Web Dashboard Integration Demo...")
    
    integration = WebDashboardIntegration(enable_web_ui=True, web_port=5000)
    
    if integration.start_web_dashboard():
        print(f"Web dashboard available at: {integration.get_web_dashboard_url()}")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping web dashboard...")
            integration.stop_web_dashboard()
            print("Demo completed.")
    else:
        print("Failed to start web dashboard")