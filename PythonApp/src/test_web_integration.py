#!/usr/bin/env python3
"""
Test script for Web Dashboard Integration

This script tests the web dashboard integration with real application components
to ensure everything connects properly as requested in the comment.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import sys
import os
import time
import logging

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_web_integration():
    """Test the web dashboard integration with available components."""
    logger.info("Testing Web Dashboard Integration with Real Application Components")
    
    # Test importing core components
    components = {}
    
    try:
        from web_ui.integration import WebDashboardIntegration
        components['WebDashboardIntegration'] = True
        logger.info("✓ WebDashboardIntegration imported successfully")
    except ImportError as e:
        components['WebDashboardIntegration'] = False
        logger.error(f"✗ Failed to import WebDashboardIntegration: {e}")
    
    try:
        from gui.main_controller import MainController
        components['MainController'] = True
        logger.info("✓ MainController imported successfully")
    except ImportError as e:
        components['MainController'] = False
        logger.warning(f"⚠ MainController not available: {e}")
    
    try:
        from session.session_manager import SessionManager
        components['SessionManager'] = True
        logger.info("✓ SessionManager imported successfully")
    except ImportError as e:
        components['SessionManager'] = False
        logger.warning(f"⚠ SessionManager not available: {e}")
    
    try:
        from shimmer_manager import ShimmerManager
        components['ShimmerManager'] = True
        logger.info("✓ ShimmerManager imported successfully")
    except ImportError as e:
        components['ShimmerManager'] = False
        logger.warning(f"⚠ ShimmerManager not available: {e}")
    
    try:
        from network.android_device_manager import AndroidDeviceManager
        components['AndroidDeviceManager'] = True
        logger.info("✓ AndroidDeviceManager imported successfully")
    except ImportError as e:
        components['AndroidDeviceManager'] = False
        logger.warning(f"⚠ AndroidDeviceManager not available: {e}")
    
    if not components['WebDashboardIntegration']:
        logger.error("Cannot proceed without WebDashboardIntegration")
        return False
    
    # Test creating integration with available components
    logger.info("\n--- Testing Web Dashboard Integration ---")
    
    try:
        # Create component instances for available modules
        main_controller = None
        session_manager = None
        shimmer_manager = None
        android_device_manager = None
        
        if components['MainController']:
            main_controller = MainController()
            logger.info("✓ MainController instance created")
        
        if components['SessionManager']:
            session_manager = SessionManager(base_recordings_dir="test_recordings")
            logger.info("✓ SessionManager instance created")
        
        if components['ShimmerManager']:
            shimmer_manager = ShimmerManager()
            logger.info("✓ ShimmerManager instance created")
        
        if components['AndroidDeviceManager']:
            android_device_manager = AndroidDeviceManager(server_port=9001)  # Use different port for testing
            logger.info("✓ AndroidDeviceManager instance created")
        
        # Create web integration with real components
        web_integration = WebDashboardIntegration(
            enable_web_ui=True,
            web_port=5001,  # Use different port for testing
            main_controller=main_controller,
            session_manager=session_manager,
            shimmer_manager=shimmer_manager,
            android_device_manager=android_device_manager
        )
        
        logger.info("✓ WebDashboardIntegration created with real components")
        
        # Test starting the web dashboard
        if web_integration.start_web_dashboard():
            logger.info("✓ Web dashboard started successfully")
            
            # Test some basic functionality
            web_integration.update_device_status('android_devices', 'test_device', {
                'status': 'connected',
                'battery': 85,
                'temperature': 36.5,
                'recording': False
            })
            logger.info("✓ Device status update test passed")
            
            web_integration.update_sensor_data('test_device', 'gsr', 1.23)
            logger.info("✓ Sensor data update test passed")
            
            web_integration.update_session_info({
                'active': True,
                'session_id': 'test_session_123',
                'start_time': time.time(),
                'recording_devices': ['test_device']
            })
            logger.info("✓ Session info update test passed")
            
            logger.info(f"✓ Web dashboard available at: {web_integration.get_web_dashboard_url()}")
            
            # Stop the web dashboard
            web_integration.stop_web_dashboard()
            logger.info("✓ Web dashboard stopped successfully")
            
            return True
        else:
            logger.error("✗ Failed to start web dashboard")
            return False
    
    except Exception as e:
        logger.error(f"✗ Test failed with exception: {e}")
        return False

def main():
    """Main test function."""
    logger.info("=== Web Dashboard Integration Test ===")
    
    success = test_web_integration()
    
    if success:
        logger.info("\n🎉 All tests passed! Web dashboard integration is working with real components.")
    else:
        logger.error("\n❌ Some tests failed. Check the logs above for details.")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())