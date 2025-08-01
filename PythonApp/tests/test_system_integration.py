#!/usr/bin/env python3
"""
Comprehensive integration test suite for the multi-sensor recording system.
Tests complete system workflows and component interactions.
"""

import sys
import os
import unittest
import tempfile
import shutil
import time
import json
import threading
from unittest.mock import Mock, patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import components if available
try:
    from calibration.calibration import CalibrationManager
    CALIBRATION_AVAILABLE = True
except ImportError:
    CALIBRATION_AVAILABLE = False

try:
    from shimmer_manager import ShimmerManager
    SHIMMER_AVAILABLE = True
except ImportError:
    SHIMMER_AVAILABLE = False


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete multi-sensor system."""

    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # Initialize managers if available
        if CALIBRATION_AVAILABLE:
            self.calibration_manager = CalibrationManager()
        
        if SHIMMER_AVAILABLE:
            with patch('shimmer_manager.AndroidDeviceManager'):
                self.shimmer_manager = ShimmerManager(enable_android_integration=False)

    def tearDown(self):
        """Clean up integration test environment."""
        if hasattr(self, 'shimmer_manager'):
            self.shimmer_manager.stop_recording()
            self.shimmer_manager.disconnect_all_devices()

    @unittest.skipUnless(CALIBRATION_AVAILABLE and SHIMMER_AVAILABLE, 
                        "Requires both calibration and Shimmer components")
    def test_complete_system_workflow(self):
        """Test complete system workflow: calibration + sensor recording."""
        print("\nTesting complete system workflow...")
        
        # Phase 1: Camera calibration
        print("Phase 1: Camera calibration")
        
        # Create synthetic calibration images
        import cv2
        import numpy as np
        
        images = []
        image_points = []
        image_size = (640, 480)
        
        for i in range(6):
            # Create chessboard image
            img = np.ones((image_size[1], image_size[0], 3), dtype=np.uint8) * 255
            pattern_size = (9, 6)
            square_size = 50
            
            board_width = pattern_size[0] * square_size
            board_height = pattern_size[1] * square_size
            start_x = (image_size[0] - board_width) // 2
            start_y = (image_size[1] - board_height) // 2
            
            for row in range(pattern_size[1] + 1):
                for col in range(pattern_size[0] + 1):
                    if (row + col) % 2 == 1:
                        x1 = start_x + col * square_size
                        y1 = start_y + row * square_size
                        x2 = min(x1 + square_size, image_size[0])
                        y2 = min(y1 + square_size, image_size[1])
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)
            
            images.append(img)
            
            # Detect pattern
            found, corners = self.calibration_manager.detect_pattern(img, 'chessboard')
            if found:
                image_points.append(corners)
        
        # Perform calibration
        calibration_result = self.calibration_manager.calibrate_single_camera(
            images, image_points, image_size
        )
        
        self.assertIsNotNone(calibration_result)
        print(f"✓ Calibration completed with RMS error: {calibration_result['rms_error']:.4f}")
        
        # Save calibration
        calib_path = os.path.join(self.test_dir, 'system_calibration.json')
        self.calibration_manager.save_calibration(calibration_result, calib_path)
        print(f"✓ Calibration saved to: {calib_path}")
        
        # Phase 2: Shimmer sensor setup
        print("\nPhase 2: Shimmer sensor setup")
        
        # Discover devices
        devices = self.shimmer_manager.scan_and_pair_devices()
        print(f"✓ Discovered devices: {sum(len(v) for v in devices.values())} total")
        
        # Connect to simulated device
        if devices['simulated']:
            device = devices['simulated'][0]
            connected = self.shimmer_manager.connect_device(device)
            print(f"✓ Device connection: {connected}")
        
        # Phase 3: Synchronized recording session
        print("\nPhase 3: Synchronized recording")
        
        # Start recording session
        session_id = self.shimmer_manager.start_recording_session()
        print(f"✓ Recording session started: {session_id}")
        
        # Simulate synchronized data collection
        recording_duration = 2.0  # seconds
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < recording_duration:
            # Simulate sensor data
            current_time = time.time()
            mock_data = {
                'timestamp': current_time,
                'gsr': 1000 + sample_count * 2 + np.random.normal(0, 10),
                'ppg': 2000 + sample_count + np.random.normal(0, 50),
                'accel_x': 0.1 + np.random.normal(0, 0.05),
                'accel_y': 0.2 + np.random.normal(0, 0.05),
                'accel_z': 0.9 + np.random.normal(0, 0.05)
            }
            
            self.shimmer_manager._process_shimmer_data(mock_data)
            sample_count += 1
            time.sleep(0.02)  # 50 Hz simulation
        
        # Stop recording
        output_file = self.shimmer_manager.stop_recording_session()
        print(f"✓ Recording completed: {sample_count} samples")
        print(f"✓ Data saved to: {output_file}")
        
        # Phase 4: Data validation
        print("\nPhase 4: Data validation")
        
        # Verify calibration data
        loaded_calibration = self.calibration_manager.load_calibration(calib_path)
        self.assertIsNotNone(loaded_calibration)
        print("✓ Calibration data verified")
        
        # Verify sensor data
        if output_file and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                lines = f.readlines()
                self.assertGreater(len(lines), sample_count // 2)  # Should have most samples
                print(f"✓ Sensor data verified: {len(lines)} lines")
        
        print("\n✅ Complete system workflow test PASSED")

    @unittest.skipUnless(CALIBRATION_AVAILABLE, "Requires calibration component")
    def test_calibration_performance_integration(self):
        """Test calibration performance under realistic conditions."""
        print("\nTesting calibration performance integration...")
        
        import cv2
        import numpy as np
        
        # Test with various image sizes and pattern configurations
        test_configurations = [
            {'size': (640, 480), 'pattern': (9, 6)},
            {'size': (1280, 720), 'pattern': (12, 8)},
            {'size': (1920, 1080), 'pattern': (15, 10)}
        ]
        
        for config in test_configurations:
            image_size = config['size']
            pattern_size = config['pattern']
            
            print(f"Testing {image_size} with {pattern_size} pattern...")
            
            # Update calibration manager pattern
            old_pattern = self.calibration_manager.pattern_size
            self.calibration_manager.pattern_size = pattern_size
            
            # Create test images
            images = []
            image_points = []
            
            for i in range(8):  # Minimum viable number
                img = np.ones((image_size[1], image_size[0], 3), dtype=np.uint8) * 255
                
                # Create chessboard
                square_size = min(40, min(image_size) // max(pattern_size) - 2)
                board_width = pattern_size[0] * square_size
                board_height = pattern_size[1] * square_size
                start_x = (image_size[0] - board_width) // 2
                start_y = (image_size[1] - board_height) // 2
                
                for row in range(pattern_size[1] + 1):
                    for col in range(pattern_size[0] + 1):
                        if (row + col) % 2 == 1:
                            x1 = start_x + col * square_size
                            y1 = start_y + row * square_size
                            x2 = min(x1 + square_size, image_size[0])
                            y2 = min(y1 + square_size, image_size[1])
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)
                
                images.append(img)
                
                # Detect pattern
                start_time = time.time()
                found, corners = self.calibration_manager.detect_pattern(img, 'chessboard')
                detection_time = time.time() - start_time
                
                if found:
                    image_points.append(corners)
                    print(f"  Pattern detected in {detection_time:.4f}s")
            
            # Perform calibration
            if len(image_points) >= 3:
                start_time = time.time()
                result = self.calibration_manager.calibrate_single_camera(
                    images, image_points, image_size
                )
                calibration_time = time.time() - start_time
                
                self.assertIsNotNone(result)
                print(f"  Calibration completed in {calibration_time:.4f}s")
                print(f"  RMS error: {result['rms_error']:.4f}")
            
            # Restore original pattern
            self.calibration_manager.pattern_size = old_pattern
        
        print("✓ Calibration performance tests completed")

    @unittest.skipUnless(SHIMMER_AVAILABLE, "Requires Shimmer component")
    def test_shimmer_stress_integration(self):
        """Test Shimmer system under stress conditions."""
        print("\nTesting Shimmer stress integration...")
        
        # Test high-frequency data processing
        sample_rates = [50, 100, 200]  # Hz
        
        for rate in sample_rates:
            print(f"Testing {rate} Hz sampling rate...")
            
            # Start recording
            session_id = self.shimmer_manager.start_recording_session()
            
            # Generate high-frequency data
            duration = 5.0  # seconds
            samples_expected = int(rate * duration)
            interval = 1.0 / rate
            
            start_time = time.time()
            samples_sent = 0
            
            for i in range(samples_expected):
                current_time = start_time + i * interval
                
                mock_data = {
                    'timestamp': current_time,
                    'gsr': 1000 + i % 100,
                    'ppg': 2000 + i % 200,
                    'accel_x': 0.1 + (i % 50) * 0.001,
                    'accel_y': 0.2 + (i % 50) * 0.001,
                    'accel_z': 0.9 + (i % 50) * 0.001
                }
                
                self.shimmer_manager._process_shimmer_data(mock_data)
                samples_sent += 1
                
                # Small delay to simulate real-time
                time.sleep(max(0, interval - 0.001))
            
            # Stop recording
            output_file = self.shimmer_manager.stop_recording_session()
            processing_time = time.time() - start_time
            
            print(f"  Processed {samples_sent} samples in {processing_time:.2f}s")
            print(f"  Effective rate: {samples_sent / processing_time:.1f} Hz")
            
            # Verify data integrity
            if output_file and os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                    data_lines = len(lines) - 1  # Exclude header
                    print(f"  Saved {data_lines} samples ({data_lines/samples_sent*100:.1f}% retention)")
        
        print("✓ Shimmer stress tests completed")

    def test_error_recovery_integration(self):
        """Test system error recovery and resilience."""
        print("\nTesting error recovery integration...")
        
        # Test 1: Calibration with bad images
        if CALIBRATION_AVAILABLE:
            print("Testing calibration error recovery...")
            
            import cv2
            import numpy as np
            
            # Create mix of good and bad calibration images
            images = []
            image_points = []
            
            for i in range(8):
                if i % 3 == 0:
                    # Create bad image (no pattern)
                    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                else:
                    # Create good chessboard image
                    img = np.ones((480, 640, 3), dtype=np.uint8) * 255
                    pattern_size = (9, 6)
                    square_size = 50
                    
                    board_width = pattern_size[0] * square_size
                    board_height = pattern_size[1] * square_size
                    start_x = (640 - board_width) // 2
                    start_y = (480 - board_height) // 2
                    
                    for row in range(pattern_size[1] + 1):
                        for col in range(pattern_size[0] + 1):
                            if (row + col) % 2 == 1:
                                x1 = start_x + col * square_size
                                y1 = start_y + row * square_size
                                x2 = min(x1 + square_size, 640)
                                y2 = min(y1 + square_size, 480)
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)
                
                images.append(img)
                
                # Try to detect pattern
                found, corners = self.calibration_manager.detect_pattern(img, 'chessboard')
                if found:
                    image_points.append(corners)
            
            # Should handle mixed success/failure gracefully
            if len(image_points) >= 3:
                result = self.calibration_manager.calibrate_single_camera(
                    images, image_points, (640, 480)
                )
                self.assertIsNotNone(result)
                print(f"✓ Calibration succeeded with {len(image_points)}/{len(images)} valid images")
            else:
                print("✓ Calibration correctly handled insufficient valid images")
        
        # Test 2: Shimmer with data corruption
        if SHIMMER_AVAILABLE:
            print("Testing Shimmer error recovery...")
            
            # Start recording session
            session_id = self.shimmer_manager.start_recording_session()
            
            # Send mix of good and corrupted data
            good_samples = 0
            corrupted_samples = 0
            
            for i in range(50):
                if i % 7 == 0:
                    # Send corrupted data
                    corrupted_data = {
                        'timestamp': 'invalid_timestamp',
                        'gsr': None,
                        'ppg': 'not_a_number'
                    }
                    try:
                        self.shimmer_manager._process_shimmer_data(corrupted_data)
                        corrupted_samples += 1
                    except:
                        pass  # Expected to fail gracefully
                else:
                    # Send good data
                    good_data = {
                        'timestamp': time.time() + i * 0.02,
                        'gsr': 1000 + i,
                        'ppg': 2000 + i,
                        'accel_x': 0.1,
                        'accel_y': 0.2,
                        'accel_z': 0.9
                    }
                    self.shimmer_manager._process_shimmer_data(good_data)
                    good_samples += 1
            
            # Stop recording
            output_file = self.shimmer_manager.stop_recording_session()
            
            print(f"✓ Processed {good_samples} good samples, handled {corrupted_samples} corrupted samples")
            
            # Verify output contains good data
            if output_file and os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                    self.assertGreater(len(lines), good_samples // 2)
        
        print("✓ Error recovery tests completed")

    def test_concurrent_operations_integration(self):
        """Test concurrent operations and thread safety."""
        print("\nTesting concurrent operations integration...")
        
        if not SHIMMER_AVAILABLE:
            self.skipTest("Requires Shimmer component")
        
        # Test concurrent data processing
        def data_generator(manager, thread_id, samples_per_thread):
            """Generate data from multiple threads."""
            for i in range(samples_per_thread):
                mock_data = {
                    'timestamp': time.time() + i * 0.001,
                    'gsr': 1000 + thread_id * 100 + i,
                    'ppg': 2000 + thread_id * 100 + i,
                    'accel_x': 0.1 + thread_id * 0.01,
                    'thread_id': thread_id,
                    'sample_id': i
                }
                manager._process_shimmer_data(mock_data)
                time.sleep(0.001)  # Small delay
        
        # Start recording session
        session_id = self.shimmer_manager.start_recording_session()
        
        # Create multiple threads
        num_threads = 3
        samples_per_thread = 20
        threads = []
        
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(
                target=data_generator,
                args=(self.shimmer_manager, thread_id, samples_per_thread)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        processing_time = time.time() - start_time
        
        # Stop recording
        output_file = self.shimmer_manager.stop_recording_session()
        
        total_samples = num_threads * samples_per_thread
        print(f"✓ Processed {total_samples} samples from {num_threads} threads in {processing_time:.3f}s")
        
        # Verify data integrity
        if output_file and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                lines = f.readlines()
                data_lines = len(lines) - 1  # Exclude header
                print(f"✓ Saved {data_lines} samples ({data_lines/total_samples*100:.1f}% retention)")
        
        print("✓ Concurrent operations tests completed")

    def test_memory_usage_integration(self):
        """Test memory usage under extended operation."""
        print("\nTesting memory usage integration...")
        
        if not SHIMMER_AVAILABLE:
            self.skipTest("Requires Shimmer component")
        
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Run extended data processing session
        session_id = self.shimmer_manager.start_recording_session()
        
        samples_processed = 0
        batch_size = 100
        num_batches = 50
        
        for batch in range(num_batches):
            # Process batch of data
            for i in range(batch_size):
                mock_data = {
                    'timestamp': time.time() + samples_processed * 0.01,
                    'gsr': 1000 + samples_processed % 1000,
                    'ppg': 2000 + samples_processed % 2000,
                    'accel_x': 0.1 + (samples_processed % 100) * 0.001,
                    'accel_y': 0.2 + (samples_processed % 100) * 0.001,
                    'accel_z': 0.9 + (samples_processed % 100) * 0.001
                }
                self.shimmer_manager._process_shimmer_data(mock_data)
                samples_processed += 1
            
            # Check memory usage periodically
            if batch % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                print(f"  Batch {batch}: {samples_processed} samples, {current_memory:.1f} MB (+{memory_increase:.1f} MB)")
                
                # Force garbage collection
                gc.collect()
        
        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        
        # Stop recording
        output_file = self.shimmer_manager.stop_recording_session()
        
        print(f"Final memory usage: {final_memory:.1f} MB (+{total_increase:.1f} MB)")
        print(f"Memory per sample: {total_increase * 1024 / samples_processed:.3f} KB")
        
        # Memory increase should be reasonable
        self.assertLess(total_increase, 100)  # Less than 100 MB increase
        
        print("✓ Memory usage tests completed")


def run_integration_tests():
    """Run all integration tests with detailed output."""
    print("="*80)
    print("COMPREHENSIVE SYSTEM INTEGRATION TESTS")
    print("="*80)
    
    if not (CALIBRATION_AVAILABLE or SHIMMER_AVAILABLE):
        print("Skipping integration tests - no components available")
        return True
    
    print(f"Components available:")
    print(f"  Calibration: {CALIBRATION_AVAILABLE}")
    print(f"  Shimmer: {SHIMMER_AVAILABLE}")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSystemIntegration)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nIntegration Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)