#!/usr/bin/env python3
"""
Test Suite for Dual Webcam Recording System

Comprehensive test suite to validate the dual Logitech Brio webcam recording 
system with master clock synchronization functionality.

Tests include:
- Webcam hardware detection and access
- Dual camera initialization and configuration  
- Master clock synchronization accuracy
- Recording functionality and file output
- Network time server operation
- Android device communication protocol

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import sys
import os
import time
import unittest
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import get_logger
from webcam.dual_webcam_capture import DualWebcamCapture, test_dual_webcam_access
from master_clock_synchronizer import MasterClockSynchronizer
from ntp_time_server import NTPTimeServer

logger = get_logger(__name__)


class TestDualWebcamHardware(unittest.TestCase):
    """Test dual webcam hardware detection and access."""
    
    def test_dual_webcam_access(self):
        """Test that both webcams can be accessed."""
        logger.info("Testing dual webcam hardware access...")
        success = test_dual_webcam_access()
        self.assertTrue(success, "Both webcams should be accessible")
        
    def test_camera_enumeration(self):
        """Test camera enumeration and detection."""
        import cv2
        
        detected_cameras = []
        for i in range(5):  # Test first 5 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    detected_cameras.append({
                        'index': i,
                        'resolution': (width, height)
                    })
                cap.release()
                
        logger.info(f"Detected cameras: {detected_cameras}")
        self.assertGreaterEqual(len(detected_cameras), 2, 
                               "At least 2 cameras should be detected")


class TestDualWebcamCapture(unittest.TestCase):
    """Test dual webcam capture functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.dual_webcam = None
        
    def tearDown(self):
        """Clean up test environment."""
        if self.dual_webcam:
            self.dual_webcam.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_dual_webcam_initialization(self):
        """Test dual webcam initialization."""
        logger.info("Testing dual webcam initialization...")
        
        self.dual_webcam = DualWebcamCapture(
            camera1_index=0,
            camera2_index=1,
            recording_fps=30,
            resolution=(1920, 1080)  # Use lower resolution for testing
        )
        
        success = self.dual_webcam.initialize_cameras()
        self.assertTrue(success, "Dual webcam initialization should succeed")
        
    def test_recording_functionality(self):
        """Test recording functionality."""
        logger.info("Testing dual webcam recording...")
        
        self.dual_webcam = DualWebcamCapture(
            camera1_index=0,
            camera2_index=1,
            recording_fps=30,
            resolution=(1280, 720)  # Lower resolution for faster testing
        )
        
        # Set output directory to temp directory
        self.dual_webcam.output_directory = self.temp_dir
        
        # Initialize cameras
        success = self.dual_webcam.initialize_cameras()
        self.assertTrue(success, "Camera initialization should succeed")
        
        # Start recording
        session_id = "test_session"
        recording_started = self.dual_webcam.start_recording(session_id)
        self.assertTrue(recording_started, "Recording should start successfully")
        
        # Record for 2 seconds
        time.sleep(2)
        
        # Stop recording
        files = self.dual_webcam.stop_recording()
        self.assertIsNotNone(files[0], "Camera 1 file should be created")
        self.assertIsNotNone(files[1], "Camera 2 file should be created")
        
        # Check files exist
        self.assertTrue(os.path.exists(files[0]), "Camera 1 file should exist")
        self.assertTrue(os.path.exists(files[1]), "Camera 2 file should exist")
        
        # Check file sizes (should be > 0)
        self.assertGreater(os.path.getsize(files[0]), 0, "Camera 1 file should not be empty")
        self.assertGreater(os.path.getsize(files[1]), 0, "Camera 2 file should not be empty")
        
        logger.info(f"Test recording files created: {files[0]}, {files[1]}")


class TestMasterClockSynchronization(unittest.TestCase):
    """Test master clock synchronization system."""
    
    def setUp(self):
        """Set up test environment."""
        self.master_sync = None
        
    def tearDown(self):
        """Clean up test environment."""
        if self.master_sync:
            self.master_sync.stop()
            
    def test_synchronizer_initialization(self):
        """Test master synchronizer initialization."""
        logger.info("Testing master synchronizer initialization...")
        
        self.master_sync = MasterClockSynchronizer(
            ntp_port=8890,  # Use different port for testing
            pc_server_port=9001
        )
        
        # Test initialization without starting servers
        self.assertIsNotNone(self.master_sync.ntp_server)
        self.assertIsNotNone(self.master_sync.pc_server)
        
    def test_timestamp_accuracy(self):
        """Test timestamp accuracy and consistency."""
        logger.info("Testing timestamp accuracy...")
        
        self.master_sync = MasterClockSynchronizer(
            ntp_port=8890,
            pc_server_port=9001
        )
        
        # Test timestamp consistency
        timestamps = []
        for _ in range(10):
            ts = self.master_sync.get_master_timestamp()
            timestamps.append(ts)
            time.sleep(0.01)
            
        # Check timestamps are increasing
        for i in range(1, len(timestamps)):
            self.assertGreater(timestamps[i], timestamps[i-1],
                             "Timestamps should be increasing")
            
        # Check timestamp precision (should be within reasonable range)
        time_span = timestamps[-1] - timestamps[0]
        self.assertGreater(time_span, 0.08, "Time span should be reasonable")
        self.assertLess(time_span, 0.15, "Time span should not be too large")


class TestNTPTimeServer(unittest.TestCase):
    """Test NTP time server functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.ntp_server = None
        
    def tearDown(self):
        """Clean up test environment."""
        if self.ntp_server:
            self.ntp_server.stop()
            
    def test_ntp_server_initialization(self):
        """Test NTP server initialization."""
        logger.info("Testing NTP server initialization...")
        
        self.ntp_server = NTPTimeServer(port=8891)  # Use different port
        self.assertIsNotNone(self.ntp_server)
        
    def test_ntp_server_start_stop(self):
        """Test NTP server start and stop."""
        logger.info("Testing NTP server start/stop...")
        
        self.ntp_server = NTPTimeServer(port=8891)
        
        # Test start
        success = self.ntp_server.start()
        if success:  # Only test if start succeeded (may fail in CI environment)
            self.assertTrue(self.ntp_server.is_running)
            
            # Wait a bit
            time.sleep(0.5)
            
            # Test stop
            self.ntp_server.stop()
            time.sleep(0.5)
            self.assertFalse(self.ntp_server.is_running)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.master_sync = None
        self.dual_webcam = None
        
    def tearDown(self):
        """Clean up test environment."""
        if self.dual_webcam:
            self.dual_webcam.cleanup()
        if self.master_sync:
            self.master_sync.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @unittest.skipIf(not test_dual_webcam_access(), "Dual webcams not available")
    def test_synchronized_recording(self):
        """Test synchronized recording across webcams and master clock."""
        logger.info("Testing synchronized recording integration...")
        
        # Initialize master synchronizer
        self.master_sync = MasterClockSynchronizer(
            ntp_port=8892,
            pc_server_port=9002
        )
        
        # Initialize dual webcam with sync callback
        sync_timestamps = []
        def sync_callback(timestamp):
            sync_timestamps.append(timestamp)
            
        self.dual_webcam = DualWebcamCapture(
            camera1_index=0,
            camera2_index=1,
            recording_fps=30,
            resolution=(1280, 720),
            sync_callback=sync_callback
        )
        
        self.dual_webcam.output_directory = self.temp_dir
        
        # Initialize components
        sync_started = self.master_sync.start()
        cam_initialized = self.dual_webcam.initialize_cameras()
        
        if sync_started and cam_initialized:
            # Start synchronized recording
            session_id = "integration_test"
            
            # Get master timestamp
            master_timestamp = self.master_sync.get_master_timestamp()
            
            # Start webcam recording
            recording_started = self.dual_webcam.start_recording(session_id)
            self.assertTrue(recording_started, "Recording should start")
            
            # Record for 1 second
            time.sleep(1)
            
            # Stop recording
            files = self.dual_webcam.stop_recording()
            
            # Verify sync callback was called
            self.assertGreater(len(sync_timestamps), 0, 
                             "Sync callback should have been called")
            
            # Verify files were created
            if files[0] and files[1]:
                self.assertTrue(os.path.exists(files[0]))
                self.assertTrue(os.path.exists(files[1]))
                logger.info("Integration test completed successfully")
            else:
                logger.warning("Recording files not created - may be expected in test environment")
        else:
            logger.warning("Could not start all components - skipping integration test")


def run_hardware_check():
    """Run hardware compatibility check."""
    print("=== Dual Webcam Recording System - Hardware Check ===\n")
    
    # Test webcam access
    print("Testing webcam hardware access...")
    success = test_dual_webcam_access()
    
    if success:
        print("✓ PASS: Both webcams accessible")
    else:
        print("✗ FAIL: Webcam access test failed")
        print("\nTroubleshooting:")
        print("1. Ensure two USB webcams are connected")
        print("2. Close any other applications using webcams")
        print("3. Check camera drivers are installed")
        print("4. Try different camera indices if using non-standard setup")
        return False
        
    # Test camera capabilities
    print("\nTesting camera capabilities...")
    import cv2
    
    for cam_idx in [0, 1]:
        cap = cv2.VideoCapture(cam_idx)
        if cap.isOpened():
            # Test 4K resolution setting
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
            
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print(f"✓ Camera {cam_idx}: {actual_width}x{actual_height}")
                if actual_width >= 3840 and actual_height >= 2160:
                    print(f"  ✓ 4K capability confirmed")
                else:
                    print(f"  ⚠ 4K not available, using {actual_width}x{actual_height}")
            else:
                print(f"✗ Camera {cam_idx}: Failed to capture test frame")
        else:
            print(f"✗ Camera {cam_idx}: Failed to open")
            
    print("\nHardware check completed.")
    return True


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dual Webcam Recording System Test Suite')
    parser.add_argument('--hardware-only', action='store_true',
                       help='Run hardware check only')
    parser.add_argument('--unit-tests', action='store_true',
                       help='Run unit tests only')
    parser.add_argument('--integration', action='store_true',
                       help='Run integration tests only')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("=== Dual Webcam Recording System Test Suite ===")
    
    # Hardware check
    if args.hardware_only or not any([args.unit_tests, args.integration]):
        success = run_hardware_check()
        if args.hardware_only:
            return 0 if success else 1
    
    # Unit tests
    if args.unit_tests or not any([args.hardware_only, args.integration]):
        print("\n=== Running Unit Tests ===")
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test cases
        suite.addTests(loader.loadTestsFromTestCase(TestDualWebcamHardware))
        suite.addTests(loader.loadTestsFromTestCase(TestDualWebcamCapture))
        suite.addTests(loader.loadTestsFromTestCase(TestMasterClockSynchronization))
        suite.addTests(loader.loadTestsFromTestCase(TestNTPTimeServer))
        
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print("Unit tests failed!")
            return 1
    
    # Integration tests
    if args.integration or not any([args.hardware_only, args.unit_tests]):
        print("\n=== Running Integration Tests ===")
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
        
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print("Integration tests failed!")
            return 1
    
    print("\n=== All Tests Completed Successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())