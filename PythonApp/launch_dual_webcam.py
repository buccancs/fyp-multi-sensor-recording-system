#!/usr/bin/env python3
"""
Dual Webcam Recording System Launcher

Quick launcher for testing the dual Logitech Brio webcam recording system
with master clock synchronization.

Usage:
    python launch_dual_webcam.py [options]

Options:
    --test-only     Test webcam access without starting full application
    --cameras N,M   Specify camera indices (default: 0,1)
    --resolution WxH Set recording resolution (default: 3840x2160)
    --fps N         Set recording FPS (default: 30)

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import argparse
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from utils.logging_config import get_logger, AppLogger
from webcam.dual_webcam_capture import test_dual_webcam_access
from gui.dual_webcam_main_window import DualWebcamMainWindow

logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Dual Webcam Recording System Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--test-only', action='store_true',
                       help='Test webcam access without starting full application')
    
    parser.add_argument('--cameras', type=str, default='0,1',
                       help='Camera indices to use (default: 0,1)')
    
    parser.add_argument('--resolution', type=str, default='3840x2160',
                       help='Recording resolution (default: 3840x2160)')
    
    parser.add_argument('--fps', type=int, default=30,
                       help='Recording FPS (default: 30)')
    
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    
    return parser.parse_args()


def test_system():
    """Test the dual webcam system."""
    logger.info("=== Dual Webcam System Test ===")
    
    # Test webcam access
    logger.info("Testing dual webcam access...")
    success = test_dual_webcam_access()
    
    if success:
        logger.info("✓ Dual webcam test PASSED")
        print("SUCCESS: Both webcams are accessible for recording!")
        return True
    else:
        logger.error("✗ Dual webcam test FAILED")
        print("ERROR: Could not access dual webcams. Please check:")
        print("  1. Two USB webcams are connected")
        print("  2. Webcams are not in use by other applications")
        print("  3. Camera drivers are properly installed")
        return False


def main():
    """Main launcher function."""
    args = parse_arguments()
    
    # Configure logging
    AppLogger.set_level(args.log_level)
    
    logger.info("=== Dual Webcam Recording System Launcher ===")
    logger.info(f"Arguments: {vars(args)}")
    
    # Parse camera indices
    try:
        camera_indices = [int(x.strip()) for x in args.cameras.split(',')]
        if len(camera_indices) != 2:
            raise ValueError("Exactly two camera indices required")
    except ValueError as e:
        logger.error(f"Invalid camera indices: {e}")
        print(f"ERROR: Invalid camera indices '{args.cameras}'. Use format: N,M (e.g., 0,1)")
        return 1
    
    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
    except ValueError:
        logger.error(f"Invalid resolution: {args.resolution}")
        print(f"ERROR: Invalid resolution '{args.resolution}'. Use format: WIDTHxHEIGHT (e.g., 3840x2160)")
        return 1
    
    logger.info(f"Camera indices: {camera_indices}")
    logger.info(f"Recording resolution: {width}x{height}")
    logger.info(f"Recording FPS: {args.fps}")
    
    # Test only mode
    if args.test_only:
        success = test_system()
        return 0 if success else 1
    
    # Test system first
    logger.info("Running system test before starting application...")
    if not test_system():
        logger.error("System test failed, aborting application start")
        return 1
    
    # Start full application
    try:
        logger.info("Starting PyQt5 application...")
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Dual Webcam Recording System")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Multi-Sensor Recording System Team")
        
        # Create main window
        logger.info("Creating main window...")
        main_window = DualWebcamMainWindow()
        
        # Apply configuration if needed
        # TODO: Pass camera indices and settings to main window
        
        # Show window
        main_window.show()
        logger.info("Application started successfully")
        
        # Run application
        exit_code = app.exec_()
        logger.info(f"Application exited with code: {exit_code}")
        
        return exit_code
        
    except Exception as e:
        logger.error(f"Fatal error during application startup: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())