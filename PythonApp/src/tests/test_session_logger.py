"""
Test Suite for SessionLogger Module - Milestone 3.8

This module contains comprehensive tests for the SessionLogger functionality
including JSON logging, event capture, UI integration, and file management.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
Milestone: 3.8 - Session Metadata Logging and Review
"""

import unittest
import tempfile
import json
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Import the SessionLogger module
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from session.session_logger import SessionLogger, get_session_logger, reset_session_logger


class TestSessionLogger(unittest.TestCase):
    """Test cases for SessionLogger functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directory for test sessions
        self.test_dir = tempfile.mkdtemp()
        self.session_logger = SessionLogger(base_sessions_dir=self.test_dir)
        
        print(f"[DEBUG_LOG] Test setup: Using temporary directory {self.test_dir}")
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Clean up temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Reset global session logger
        reset_session_logger()
        
        print(f"[DEBUG_LOG] Test cleanup: Removed temporary directory {self.test_dir}")
    
    def test_basic_session_lifecycle(self):
        """Test basic session start and end functionality."""
        print("[DEBUG_LOG] Testing basic session lifecycle...")
        
        # Test session start
        devices = [
            {"id": "Phone1", "type": "android_phone"},
            {"id": "Phone2", "type": "android_phone"},
            {"id": "pc_webcam", "type": "pc_webcam"}
        ]
        
        session_info = self.session_logger.start_session("TestSession", devices)
        
        # Verify session info
        self.assertIsNotNone(session_info)
        self.assertIn("session_id", session_info)
        self.assertIn("TestSession", session_info["session_id"])
        self.assertTrue(self.session_logger.is_session_active())
        
        # Test session end
        completed_session = self.session_logger.end_session()
        
        # Verify session completion
        self.assertIsNotNone(completed_session)
        self.assertFalse(self.session_logger.is_session_active())
        self.assertIsNotNone(completed_session.get("end_time"))
        self.assertIsNotNone(completed_session.get("duration"))
        
        print("[DEBUG_LOG] Basic session lifecycle test passed")
    
    def test_event_logging(self):
        """Test comprehensive event logging functionality."""
        print("[DEBUG_LOG] Testing event logging...")
        
        # Start session
        devices = [{"id": "TestDevice", "type": "test_device"}]
        self.session_logger.start_session("EventTest", devices)
        
        # Test various event types
        self.session_logger.log_device_connected("TestDevice", "test_device", ["test_capability"])
        self.session_logger.log_recording_start(["TestDevice"], "EventTest")
        self.session_logger.log_device_ack("TestDevice", "start_record")
        self.session_logger.log_stimulus_play("test_video.mp4")
        self.session_logger.log_marker("TestMarker", "00:01:30.500")
        self.session_logger.log_stimulus_stop("test_video.mp4")
        self.session_logger.log_file_received("TestDevice", "test_file.mp4", 1024000, "video")
        self.session_logger.log_error("test_error", "Test error message", "TestDevice")
        self.session_logger.log_recording_stop()
        
        # End session and verify events
        completed_session = self.session_logger.end_session()
        
        # Check that all events were logged
        events = completed_session.get("events", [])
        self.assertGreater(len(events), 8)  # Should have at least 9 events plus session_start and session_end
        
        # Verify specific event types exist
        event_types = [event.get("event") for event in events]
        expected_events = [
            "session_start", "device_connected", "start_record", "device_ack",
            "stimulus_play", "marker", "stimulus_stop", "file_received", 
            "error", "stop_record", "session_end"
        ]
        
        for expected_event in expected_events:
            self.assertIn(expected_event, event_types, f"Event type '{expected_event}' not found in logged events")
        
        print(f"[DEBUG_LOG] Event logging test passed - logged {len(events)} events")
    
    def test_json_file_creation(self):
        """Test JSON log file creation and format."""
        print("[DEBUG_LOG] Testing JSON file creation...")
        
        # Start and end a session
        self.session_logger.start_session("JSONTest")
        self.session_logger.log_event("test_event", {"test_data": "test_value"})
        completed_session = self.session_logger.end_session()
        
        # Find the log file
        session_id = completed_session["session"]
        expected_log_file = Path(self.test_dir) / session_id / f"{session_id}_log.json"
        
        # Verify file exists
        self.assertTrue(expected_log_file.exists(), f"Log file not found at {expected_log_file}")
        
        # Verify JSON format
        with open(expected_log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        # Verify JSON structure
        required_fields = ["session", "start_time", "end_time", "duration", "devices", "events", "status"]
        for field in required_fields:
            self.assertIn(field, log_data, f"Required field '{field}' not found in JSON log")
        
        # Verify events structure
        events = log_data.get("events", [])
        self.assertGreater(len(events), 0, "No events found in JSON log")
        
        for event in events:
            self.assertIn("event", event, "Event missing 'event' field")
            self.assertIn("time", event, "Event missing 'time' field")
            self.assertIn("timestamp", event, "Event missing 'timestamp' field")
        
        print(f"[DEBUG_LOG] JSON file creation test passed - file size: {expected_log_file.stat().st_size} bytes")
    
    def test_ui_signal_emission(self):
        """Test Qt signal emission for UI updates."""
        print("[DEBUG_LOG] Testing UI signal emission...")
        
        # Mock signal connections
        log_entry_mock = Mock()
        session_started_mock = Mock()
        session_ended_mock = Mock()
        error_logged_mock = Mock()
        
        self.session_logger.log_entry_added.connect(log_entry_mock)
        self.session_logger.session_started.connect(session_started_mock)
        self.session_logger.session_ended.connect(session_ended_mock)
        self.session_logger.error_logged.connect(error_logged_mock)
        
        # Start session and verify signal
        self.session_logger.start_session("SignalTest")
        session_started_mock.assert_called()
        
        # Log events and verify signals
        self.session_logger.log_event("test_event")
        log_entry_mock.assert_called()
        
        # Log error and verify signal
        self.session_logger.log_error("test_error", "Test error")
        error_logged_mock.assert_called()
        
        # End session and verify signal
        self.session_logger.end_session()
        session_ended_mock.assert_called()
        
        print("[DEBUG_LOG] UI signal emission test passed")
    
    def test_global_instance_management(self):
        """Test global session logger instance management."""
        print("[DEBUG_LOG] Testing global instance management...")
        
        # Test singleton behavior
        logger1 = get_session_logger()
        logger2 = get_session_logger()
        self.assertIs(logger1, logger2, "Global session logger should be singleton")
        
        # Test reset functionality
        reset_session_logger()
        logger3 = get_session_logger()
        self.assertIsNot(logger1, logger3, "Reset should create new instance")
        
        print("[DEBUG_LOG] Global instance management test passed")
    
    def test_error_handling(self):
        """Test error handling and robustness."""
        print("[DEBUG_LOG] Testing error handling...")
        
        # Test logging without active session
        self.session_logger.log_event("test_event")  # Should not crash
        
        # Test ending session without starting
        result = self.session_logger.end_session()
        self.assertIsNone(result, "End session without start should return None")
        
        # Test multiple session starts
        self.session_logger.start_session("Test1")
        self.assertTrue(self.session_logger.is_session_active())
        
        # Starting another session should end the first
        self.session_logger.start_session("Test2")
        self.assertTrue(self.session_logger.is_session_active())
        
        # Clean up
        self.session_logger.end_session()
        
        print("[DEBUG_LOG] Error handling test passed")
    
    def test_performance_high_frequency_logging(self):
        """Test performance with high-frequency event logging."""
        print("[DEBUG_LOG] Testing high-frequency logging performance...")
        
        import time
        
        # Start session
        self.session_logger.start_session("PerformanceTest")
        
        # Log many events quickly
        start_time = time.time()
        event_count = 1000
        
        for i in range(event_count):
            self.session_logger.log_event(f"test_event_{i}", {"index": i, "data": f"test_data_{i}"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # End session
        completed_session = self.session_logger.end_session()
        
        # Verify performance
        events_per_second = event_count / duration
        self.assertGreater(events_per_second, 100, "Should handle at least 100 events per second")
        
        # Verify all events were logged
        events = completed_session.get("events", [])
        self.assertGreaterEqual(len(events), event_count, "All events should be logged")
        
        print(f"[DEBUG_LOG] Performance test passed - {events_per_second:.1f} events/second")
    
    def test_large_session_simulation(self):
        """Test handling of large sessions with many events."""
        print("[DEBUG_LOG] Testing large session simulation...")
        
        # Start session
        devices = [{"id": f"Device_{i}", "type": "test_device"} for i in range(10)]
        self.session_logger.start_session("LargeSessionTest", devices)
        
        # Simulate a large session with various event types
        event_types = [
            ("device_connected", {"device": "Device_1", "device_type": "test"}),
            ("start_record", {"devices": ["Device_1", "Device_2"]}),
            ("device_ack", {"device": "Device_1", "command": "start_record"}),
            ("stimulus_play", {"media": "test_video.mp4"}),
            ("marker", {"label": "TestMarker", "stim_time": "00:01:30.500"}),
            ("file_received", {"device": "Device_1", "filename": "test.mp4", "size": 1024000}),
            ("stimulus_stop", {"media": "test_video.mp4"}),
            ("stop_record", {}),
        ]
        
        # Log many cycles of events
        cycles = 50
        for cycle in range(cycles):
            for event_type, details in event_types:
                # Add cycle info to details
                cycle_details = details.copy()
                cycle_details["cycle"] = cycle
                self.session_logger.log_event(event_type, cycle_details)
        
        # End session
        completed_session = self.session_logger.end_session()
        
        # Verify large session handling
        events = completed_session.get("events", [])
        expected_events = cycles * len(event_types) + 2  # +2 for session_start and session_end
        self.assertGreaterEqual(len(events), expected_events, "All events should be logged in large session")
        
        print(f"[DEBUG_LOG] Large session test passed - {len(events)} events logged")
    
    def test_crash_recovery_simulation(self):
        """Test crash recovery by simulating unexpected termination."""
        print("[DEBUG_LOG] Testing crash recovery simulation...")
        
        # Start session
        self.session_logger.start_session("CrashRecoveryTest")
        
        # Log some events
        self.session_logger.log_event("test_event_1", {"data": "before_crash"})
        self.session_logger.log_event("test_event_2", {"data": "before_crash"})
        
        # Simulate crash by not calling end_session() and creating new logger
        session_data = self.session_logger.get_current_session()
        log_file_path = self.session_logger.log_file_path
        
        # Verify that events were written to disk (crash recovery)
        self.assertTrue(log_file_path.exists(), "Log file should exist after crash")
        
        # Read the log file directly to verify crash recovery
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        # Verify that events were preserved
        events = log_data.get("events", [])
        self.assertGreaterEqual(len(events), 2, "Events should be preserved after crash")
        
        # Verify session data integrity
        self.assertEqual(log_data.get("session"), session_data.get("session"))
        self.assertEqual(log_data.get("status"), "active")  # Should still be active after crash
        
        print("[DEBUG_LOG] Crash recovery test passed - data preserved after simulated crash")
    
    def test_memory_usage_monitoring(self):
        """Test memory usage during extended logging."""
        print("[DEBUG_LOG] Testing memory usage monitoring...")
        
        import sys
        
        # Get initial memory usage
        initial_size = sys.getsizeof(self.session_logger)
        
        # Start session
        self.session_logger.start_session("MemoryTest")
        
        # Log many events and monitor memory growth
        event_count = 500
        for i in range(event_count):
            self.session_logger.log_event(f"memory_test_{i}", {
                "index": i,
                "data": f"test_data_{i}" * 10,  # Make events larger
                "timestamp": f"2025-07-30T12:00:{i:02d}.000Z"
            })
            
            # Check memory usage periodically
            if i % 100 == 0:
                current_size = sys.getsizeof(self.session_logger)
                growth = current_size - initial_size
                print(f"[DEBUG_LOG] Memory usage after {i} events: {growth} bytes growth")
        
        # End session
        self.session_logger.end_session()
        
        # Final memory check
        final_size = sys.getsizeof(self.session_logger)
        total_growth = final_size - initial_size
        
        # Memory growth should be reasonable (less than 1MB for 500 events)
        max_acceptable_growth = 1024 * 1024  # 1MB
        self.assertLess(total_growth, max_acceptable_growth, 
                       f"Memory growth ({total_growth} bytes) should be reasonable")
        
        print(f"[DEBUG_LOG] Memory usage test passed - total growth: {total_growth} bytes")
    
    def test_concurrent_logging_thread_safety(self):
        """Test thread safety with concurrent logging from multiple threads."""
        print("[DEBUG_LOG] Testing concurrent logging thread safety...")
        
        import threading
        import time
        
        # Start session
        self.session_logger.start_session("ConcurrencyTest")
        
        # Shared data for threads
        thread_results = []
        thread_count = 5
        events_per_thread = 50
        
        def logging_thread(thread_id):
            """Thread function that logs events concurrently."""
            try:
                for i in range(events_per_thread):
                    self.session_logger.log_event(f"thread_{thread_id}_event_{i}", {
                        "thread_id": thread_id,
                        "event_index": i,
                        "data": f"thread_{thread_id}_data_{i}"
                    })
                    time.sleep(0.001)  # Small delay to increase chance of race conditions
                thread_results.append(f"Thread {thread_id} completed successfully")
            except Exception as e:
                thread_results.append(f"Thread {thread_id} failed: {str(e)}")
        
        # Create and start threads
        threads = []
        for thread_id in range(thread_count):
            thread = threading.Thread(target=logging_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # End session
        completed_session = self.session_logger.end_session()
        
        # Verify thread safety
        self.assertEqual(len(thread_results), thread_count, "All threads should complete")
        
        # Verify all events were logged
        events = completed_session.get("events", [])
        expected_events = thread_count * events_per_thread + 2  # +2 for session_start and session_end
        self.assertEqual(len(events), expected_events, "All concurrent events should be logged")
        
        # Verify no thread failures
        failed_threads = [result for result in thread_results if "failed" in result]
        self.assertEqual(len(failed_threads), 0, f"No threads should fail: {failed_threads}")
        
        print(f"[DEBUG_LOG] Concurrent logging test passed - {len(events)} events from {thread_count} threads")


class TestSessionLoggerIntegration(unittest.TestCase):
    """Integration tests for SessionLogger with other components."""
    
    def test_session_manager_integration(self):
        """Test integration with existing SessionManager."""
        print("[DEBUG_LOG] Testing SessionManager integration...")
        
        # This test would verify that SessionLogger works alongside SessionManager
        # For now, we'll just verify the SessionLogger can be imported and used
        logger = get_session_logger()
        self.assertIsNotNone(logger)
        
        # Test that it doesn't interfere with basic functionality
        logger.start_session("IntegrationTest")
        self.assertTrue(logger.is_session_active())
        logger.end_session()
        self.assertFalse(logger.is_session_active())
        
        reset_session_logger()
        print("[DEBUG_LOG] SessionManager integration test passed")


def run_session_logger_tests():
    """Run all SessionLogger tests."""
    print("[DEBUG_LOG] Starting SessionLogger test suite...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSessionLogger))
    test_suite.addTest(unittest.makeSuite(TestSessionLoggerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    if result.wasSuccessful():
        print(f"[DEBUG_LOG] All tests passed! Ran {result.testsRun} tests successfully.")
        return True
    else:
        print(f"[DEBUG_LOG] Tests failed! {len(result.failures)} failures, {len(result.errors)} errors.")
        return False


if __name__ == "__main__":
    """Run tests when script is executed directly."""
    success = run_session_logger_tests()
    exit(0 if success else 1)
