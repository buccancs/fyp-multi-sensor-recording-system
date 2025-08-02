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
    
    def __init__(self, enable_web_ui: bool = True, web_port: int = 5000):
        """
        Initialize the web dashboard integration.
        
        Args:
            enable_web_ui: Whether to enable the web UI (default: True)
            web_port: Port for the web server (default: 5000)
        """
        self.enable_web_ui = enable_web_ui
        self.web_port = web_port
        self.web_server: Optional[WebDashboardServer] = None
        self.is_running = False
        
        # Data bridges for synchronization
        self.device_status_cache = {}
        self.session_info_cache = {}
        
        logger.info(f"Web Dashboard Integration initialized (enabled: {enable_web_ui})")
    
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
            
            # Start data simulation for demo purposes
            self._start_demo_data_generation()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web dashboard: {e}")
            return False
    
    def stop_web_dashboard(self):
        """Stop the web dashboard server."""
        if not self.is_running or not self.web_server:
            return
        
        try:
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
    
    def get_web_dashboard_url(self) -> Optional[str]:
        """
        Get the URL of the web dashboard.
        
        Returns:
            Dashboard URL if running, None otherwise
        """
        if self.is_running:
            return f"http://localhost:{self.web_port}"
        return None
    
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


def get_web_integration(enable_web_ui: bool = True, web_port: int = 5000) -> WebDashboardIntegration:
    """
    Get or create the web dashboard integration instance.
    
    Args:
        enable_web_ui: Whether to enable the web UI
        web_port: Port for the web server
    
    Returns:
        WebDashboardIntegration instance
    """
    global _web_integration_instance
    
    if _web_integration_instance is None:
        _web_integration_instance = WebDashboardIntegration(enable_web_ui, web_port)
    
    return _web_integration_instance


def start_web_dashboard(enable_web_ui: bool = True, web_port: int = 5000) -> bool:
    """
    Convenience function to start the web dashboard.
    
    Args:
        enable_web_ui: Whether to enable the web UI
        web_port: Port for the web server
    
    Returns:
        True if started successfully, False otherwise
    """
    integration = get_web_integration(enable_web_ui, web_port)
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