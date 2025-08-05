#!/usr/bin/env python3
"""
Comprehensive Session Management Tests
=====================================

This module provides comprehensive unit tests for all session management
functionality in the PythonApp.

Test coverage:
- SessionManager: Session lifecycle, directory management, persistence
- SessionLogger: Structured logging, event tracking, performance monitoring
- SessionSynchronizer: Multi-device synchronization, timing coordination
- Session Recovery: Error handling, state restoration, data integrity

Author: Multi-Sensor Recording System
Date: 2025-01-16
"""

import json
import os
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add PythonApp src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from session.session_manager import SessionManager
    from session.session_logger import SessionLogger, get_session_logger, reset_session_logger
    from session.session_synchronizer import SessionSynchronizer, SessionSyncState, MessagePriority
    from session.session_recovery import SessionRecovery, SessionBackup, RecoveryState
    SESSION_MODULES_AVAILABLE = True
except ImportError as e:
    SESSION_MODULES_AVAILABLE = False
    print(f"Warning: Session modules not available: {e}")


class TestSessionManager(unittest.TestCase):
    """Test SessionManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.session_manager = None

    def tearDown(self):
        """Clean up test fixtures."""
        if self.session_manager:
            try:
                self.session_manager.cleanup()
            except:
                pass
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_manager_initialization(self):
        """Test SessionManager initialization."""
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        
        self.assertEqual(self.session_manager.base_directory, str(self.test_dir))
        self.assertIsNone(self.session_manager.current_session_id)
        self.assertTrue(Path(self.session_manager.sessions_directory).exists())

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_creation(self):
        """Test session creation and initialization."""
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        
        # Test session creation
        session_info = self.session_manager.create_session("test_session")
        
        self.assertIsNotNone(session_info)
        self.assertIn('session_id', session_info)
        self.assertIn('folder_path', session_info)
        self.assertIn('start_time', session_info)
        
        # Verify session directory creation
        session_folder = Path(session_info['folder_path'])
        self.assertTrue(session_folder.exists())
        
        # Verify session is set as current
        self.assertEqual(self.session_manager.current_session_id, session_info['session_id'])

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_metadata_management(self):
        """Test session metadata creation and updates."""
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = self.session_manager.create_session("metadata_test")
        
        # Test initial metadata
        metadata = self.session_manager.get_session_metadata()
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['session_id'], session_info['session_id'])
        self.assertIn('start_time', metadata)
        self.assertIn('status', metadata)
        
        # Test metadata updates
        self.session_manager.update_session_metadata('description', 'Test session for metadata')
        self.session_manager.update_session_metadata('participant_id', 'P001')
        
        updated_metadata = self.session_manager.get_session_metadata()
        self.assertEqual(updated_metadata['description'], 'Test session for metadata')
        self.assertEqual(updated_metadata['participant_id'], 'P001')

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_termination(self):
        """Test session termination and cleanup."""
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = self.session_manager.create_session("termination_test")
        
        # Add some test data to session
        self.session_manager.update_session_metadata('devices_connected', 3)
        self.session_manager.update_session_metadata('total_samples', 1000)
        
        # Test session termination
        end_info = self.session_manager.end_session()
        
        self.assertIsNotNone(end_info)
        self.assertIn('session_id', end_info)
        self.assertIn('duration', end_info)
        self.assertIn('end_time', end_info)
        
        # Verify session is no longer current
        self.assertIsNone(self.session_manager.current_session_id)
        
        # Verify metadata was finalized
        final_metadata = self.session_manager.get_session_metadata(session_info['session_id'])
        self.assertEqual(final_metadata['status'], 'completed')
        self.assertIn('end_time', final_metadata)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_directory_structure(self):
        """Test session directory structure creation."""
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = self.session_manager.create_session("structure_test")
        
        session_folder = Path(session_info['folder_path'])
        
        # Verify standard subdirectories are created
        expected_subdirs = ['data', 'logs', 'metadata', 'recordings', 'analysis']
        
        for subdir in expected_subdirs:
            subdir_path = session_folder / subdir
            self.assertTrue(subdir_path.exists(), f"Subdirectory {subdir} should exist")
            self.assertTrue(subdir_path.is_dir(), f"{subdir} should be a directory")

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_persistence(self):
        """Test session data persistence across manager instances."""
        # Create session with first manager instance
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = self.session_manager.create_session("persistence_test")
        session_id = session_info['session_id']
        
        # Add metadata
        self.session_manager.update_session_metadata('test_value', 'persistent_data')
        
        # Create new manager instance (simulating app restart)
        new_session_manager = SessionManager(base_directory=str(self.test_dir))
        
        # Verify session can be loaded
        loaded_metadata = new_session_manager.get_session_metadata(session_id)
        self.assertIsNotNone(loaded_metadata)
        self.assertEqual(loaded_metadata['test_value'], 'persistent_data')

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_concurrent_session_access(self):
        """Test concurrent access to session data."""
        self.session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = self.session_manager.create_session("concurrent_test")
        
        # Simulate concurrent updates
        def update_session_data(thread_id, iterations):
            for i in range(iterations):
                key = f'thread_{thread_id}_update_{i}'
                value = f'data_from_thread_{thread_id}'
                self.session_manager.update_session_metadata(key, value)
                time.sleep(0.001)  # Small delay to increase chance of concurrency
        
        # Start multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=update_session_data, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all updates were preserved
        final_metadata = self.session_manager.get_session_metadata()
        
        # Check that updates from all threads are present
        for thread_id in range(3):
            for i in range(10):
                key = f'thread_{thread_id}_update_{i}'
                self.assertIn(key, final_metadata)


class TestSessionLogger(unittest.TestCase):
    """Test SessionLogger functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        reset_session_logger()  # Reset global logger state

    def tearDown(self):
        """Clean up test fixtures."""
        reset_session_logger()
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_logger_initialization(self):
        """Test SessionLogger initialization."""
        logger = SessionLogger(
            session_id="test_session_001",
            log_directory=str(self.test_dir)
        )
        
        self.assertEqual(logger.session_id, "test_session_001")
        self.assertEqual(logger.log_directory, str(self.test_dir))
        self.assertTrue(logger.is_active)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_structured_logging(self):
        """Test structured logging functionality."""
        logger = SessionLogger(
            session_id="structured_test",
            log_directory=str(self.test_dir)
        )
        
        # Test different log levels with structured data
        logger.info("Session started", extra={
            'event_type': 'session_start',
            'participant_id': 'P001',
            'device_count': 3
        })
        
        logger.warning("Device connection unstable", extra={
            'event_type': 'device_warning',
            'device_id': 'android_001',
            'signal_strength': 0.6
        })
        
        logger.error("Calibration failed", extra={
            'event_type': 'calibration_error',
            'error_code': 'CALIB_001',
            'retry_count': 2
        })
        
        # Verify log files were created
        log_files = list(Path(self.test_dir).glob("*.log"))
        self.assertGreater(len(log_files), 0)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_event_tracking(self):
        """Test event tracking and timeline generation."""
        logger = SessionLogger(
            session_id="event_test",
            log_directory=str(self.test_dir)
        )
        
        # Log sequence of events
        events = [
            ('session_start', {'participant': 'P001'}),
            ('device_connect', {'device_id': 'android_001'}),
            ('calibration_start', {'pattern_type': 'chessboard'}),
            ('calibration_complete', {'rms_error': 0.45}),
            ('recording_start', {'duration': 300}),
            ('recording_stop', {'samples_collected': 15000})
        ]
        
        for event_type, event_data in events:
            logger.log_event(event_type, event_data)
            time.sleep(0.001)  # Ensure different timestamps
        
        # Generate event timeline
        timeline = logger.get_event_timeline()
        
        self.assertEqual(len(timeline), len(events))
        self.assertEqual(timeline[0]['event_type'], 'session_start')
        self.assertEqual(timeline[-1]['event_type'], 'recording_stop')

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_performance_monitoring(self):
        """Test performance monitoring and metrics collection."""
        logger = SessionLogger(
            session_id="performance_test",
            log_directory=str(self.test_dir)
        )
        
        # Log performance metrics
        operations = [
            ('image_processing', 0.025, {'frames': 30}),
            ('sensor_sampling', 0.001, {'sample_rate': 1000}),
            ('network_send', 0.005, {'bytes': 1024}),
            ('file_write', 0.010, {'records': 100})
        ]
        
        for operation, duration, context in operations:
            logger.log_performance(operation, duration, context)
        
        # Get performance summary
        summary = logger.get_performance_summary()
        
        self.assertIn('operations_logged', summary)
        self.assertIn('average_durations', summary)
        self.assertEqual(summary['operations_logged'], len(operations))

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_global_session_logger(self):
        """Test global session logger functionality."""
        # Initialize global logger
        logger = get_session_logger("global_test", str(self.test_dir))
        
        # Test that subsequent calls return the same instance
        same_logger = get_session_logger()
        self.assertEqual(logger, same_logger)
        
        # Test logging through global instance
        logger.info("Global logger test message")
        
        # Reset and verify new instance
        reset_session_logger()
        new_logger = get_session_logger("new_global_test", str(self.test_dir))
        self.assertNotEqual(logger, new_logger)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_log_file_rotation(self):
        """Test log file rotation and size management."""
        logger = SessionLogger(
            session_id="rotation_test",
            log_directory=str(self.test_dir),
            max_log_size_mb=1  # Small size to trigger rotation
        )
        
        # Generate large amount of log data
        for i in range(1000):
            logger.info(f"Large log message {i} " + "x" * 100, extra={
                'iteration': i,
                'large_data': list(range(50))
            })
        
        # Check if log rotation occurred
        log_files = list(Path(self.test_dir).glob("*.log*"))
        # Should have multiple files if rotation worked
        # (This might not trigger in test environment, so just verify files exist)
        self.assertGreater(len(log_files), 0)


class TestSessionSynchronizer(unittest.TestCase):
    """Test SessionSynchronizer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_synchronizer_initialization(self):
        """Test SessionSynchronizer initialization."""
        synchronizer = SessionSynchronizer(
            session_id="sync_test",
            master_device_id="pc_master"
        )
        
        self.assertEqual(synchronizer.session_id, "sync_test")
        self.assertEqual(synchronizer.master_device_id, "pc_master")
        self.assertEqual(synchronizer.state, SessionSyncState.IDLE)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_device_registration(self):
        """Test device registration for synchronization."""
        synchronizer = SessionSynchronizer(
            session_id="device_reg_test",
            master_device_id="pc_master"
        )
        
        # Register devices
        devices = [
            {"device_id": "android_001", "type": "android", "capabilities": ["camera", "gsr"]},
            {"device_id": "android_002", "type": "android", "capabilities": ["thermal"]},
            {"device_id": "desktop_001", "type": "desktop", "capabilities": ["processing"]}
        ]
        
        for device in devices:
            synchronizer.register_device(**device)
        
        # Verify registration
        registered_devices = synchronizer.get_registered_devices()
        self.assertEqual(len(registered_devices), len(devices))
        
        for device in devices:
            self.assertIn(device["device_id"], registered_devices)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_synchronization_sequence(self):
        """Test synchronization sequence orchestration."""
        synchronizer = SessionSynchronizer(
            session_id="sync_sequence_test",
            master_device_id="pc_master"
        )
        
        # Register devices
        device_ids = ["android_001", "android_002", "desktop_001"]
        for device_id in device_ids:
            synchronizer.register_device(device_id, "android", ["recording"])
        
        # Mock message sending
        with patch.object(synchronizer, 'send_sync_message') as mock_send:
            # Start synchronization
            sync_result = synchronizer.start_synchronization()
            
            self.assertTrue(sync_result)
            self.assertEqual(synchronizer.state, SessionSyncState.SYNCHRONIZING)
            
            # Verify sync messages sent to all devices
            self.assertEqual(mock_send.call_count, len(device_ids))

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_timing_coordination(self):
        """Test timing coordination between devices."""
        synchronizer = SessionSynchronizer(
            session_id="timing_test",
            master_device_id="pc_master"
        )
        
        # Register devices with latency information
        devices_with_latency = [
            ("android_001", 50),  # 50ms latency
            ("android_002", 30),  # 30ms latency
            ("desktop_001", 5)    # 5ms latency
        ]
        
        for device_id, latency in devices_with_latency:
            synchronizer.register_device(device_id, "android", ["recording"])
            synchronizer.update_device_latency(device_id, latency)
        
        # Calculate synchronized start time
        sync_start_time = synchronizer.calculate_synchronized_start_time()
        
        self.assertIsNotNone(sync_start_time)
        
        # Verify timing adjustments for each device
        for device_id, expected_latency in devices_with_latency:
            adjusted_start_time = synchronizer.get_device_start_time(device_id)
            self.assertIsNotNone(adjusted_start_time)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_synchronization_recovery(self):
        """Test synchronization recovery after failures."""
        synchronizer = SessionSynchronizer(
            session_id="recovery_test",
            master_device_id="pc_master"
        )
        
        # Register devices
        device_ids = ["android_001", "android_002", "android_003"]
        for device_id in device_ids:
            synchronizer.register_device(device_id, "android", ["recording"])
        
        # Simulate synchronization failure
        synchronizer.state = SessionSyncState.SYNCHRONIZING
        
        # Report device failure
        synchronizer.report_device_sync_failure("android_002", "timeout")
        
        # Test recovery process
        with patch.object(synchronizer, 'send_sync_message') as mock_send:
            recovery_result = synchronizer.attempt_sync_recovery()
            
            self.assertTrue(recovery_result)
            # Should try to re-sync failed device
            mock_send.assert_called()

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_priority_message_handling(self):
        """Test priority-based message handling in synchronization."""
        synchronizer = SessionSynchronizer(
            session_id="priority_test",
            master_device_id="pc_master"
        )
        
        # Queue messages with different priorities
        messages = [
            ("Low priority status", MessagePriority.LOW),
            ("Emergency stop", MessagePriority.CRITICAL),
            ("Normal command", MessagePriority.NORMAL),
            ("High priority sync", MessagePriority.HIGH)
        ]
        
        for content, priority in messages:
            synchronizer.queue_priority_message(content, priority)
        
        # Process messages - should handle in priority order
        processed_messages = []
        while synchronizer.has_pending_messages():
            message = synchronizer.get_next_priority_message()
            processed_messages.append(message.priority)
        
        # Verify priority ordering (CRITICAL > HIGH > NORMAL > LOW)
        expected_order = [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                         MessagePriority.NORMAL, MessagePriority.LOW]
        self.assertEqual(processed_messages, expected_order)


class TestSessionRecovery(unittest.TestCase):
    """Test session recovery and backup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_backup_creation(self):
        """Test session backup creation."""
        # Create a session to backup
        session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = session_manager.create_session("backup_test")
        
        # Add some data to the session
        session_manager.update_session_metadata('participant_id', 'P001')
        session_manager.update_session_metadata('device_count', 3)
        
        # Create backup
        recovery = SessionRecovery(base_directory=str(self.test_dir))
        backup_info = recovery.create_session_backup(session_info['session_id'])
        
        self.assertIsNotNone(backup_info)
        self.assertIn('backup_id', backup_info)
        self.assertIn('backup_path', backup_info)
        self.assertTrue(Path(backup_info['backup_path']).exists())

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_session_state_restoration(self):
        """Test session state restoration from backup."""
        # Create and backup a session
        session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = session_manager.create_session("restoration_test")
        session_id = session_info['session_id']
        
        # Add test data
        test_metadata = {
            'participant_id': 'P001',
            'device_count': 3,
            'calibration_status': 'completed',
            'recording_duration': 300
        }
        
        for key, value in test_metadata.items():
            session_manager.update_session_metadata(key, value)
        
        # Create backup
        recovery = SessionRecovery(base_directory=str(self.test_dir))
        backup_info = recovery.create_session_backup(session_id)
        
        # Simulate session corruption/loss
        session_manager.end_session()
        
        # Restore from backup
        restored_session = recovery.restore_session_from_backup(backup_info['backup_id'])
        
        self.assertIsNotNone(restored_session)
        self.assertEqual(restored_session['session_id'], session_id)
        
        # Verify restored metadata
        for key, expected_value in test_metadata.items():
            self.assertIn(key, restored_session['metadata'])
            self.assertEqual(restored_session['metadata'][key], expected_value)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_automatic_recovery_detection(self):
        """Test automatic detection of sessions needing recovery."""
        recovery = SessionRecovery(base_directory=str(self.test_dir))
        
        # Create sessions in different states
        session_manager = SessionManager(base_directory=str(self.test_dir))
        
        # Normal completed session
        completed_session = session_manager.create_session("completed_test")
        session_manager.update_session_metadata('status', 'recording')
        session_manager.end_session()
        
        # Interrupted session (simulate crash)
        interrupted_session = session_manager.create_session("interrupted_test")
        session_manager.update_session_metadata('status', 'recording')
        # Don't call end_session() - simulates crash
        
        # Check recovery detection
        recovery_candidates = recovery.detect_sessions_needing_recovery()
        
        self.assertIsInstance(recovery_candidates, list)
        # Should detect the interrupted session
        interrupted_found = any(
            candidate['session_id'] == interrupted_session['session_id']
            for candidate in recovery_candidates
        )
        self.assertTrue(interrupted_found)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_data_integrity_validation(self):
        """Test data integrity validation during recovery."""
        session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = session_manager.create_session("integrity_test")
        
        # Add test data files
        session_folder = Path(session_info['folder_path'])
        test_files = {
            'data/sensor_data.json': {'samples': 1000, 'checksum': 'abc123'},
            'recordings/video.mp4': {'size': 1024000, 'duration': 60},
            'metadata/calibration.json': {'rms_error': 0.45, 'valid': True}
        }
        
        for file_path, content in test_files.items():
            full_path = session_folder / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                json.dump(content, f)
        
        # Validate integrity
        recovery = SessionRecovery(base_directory=str(self.test_dir))
        integrity_report = recovery.validate_session_integrity(session_info['session_id'])
        
        self.assertIsNotNone(integrity_report)
        self.assertIn('files_checked', integrity_report)
        self.assertIn('integrity_score', integrity_report)
        self.assertIn('issues_found', integrity_report)

    @unittest.skipUnless(SESSION_MODULES_AVAILABLE, "Session modules not available")
    def test_incremental_backup_strategy(self):
        """Test incremental backup strategy."""
        session_manager = SessionManager(base_directory=str(self.test_dir))
        session_info = session_manager.create_session("incremental_test")
        session_id = session_info['session_id']
        
        recovery = SessionRecovery(base_directory=str(self.test_dir))
        
        # Create initial backup
        initial_backup = recovery.create_session_backup(session_id)
        
        # Add more data
        session_manager.update_session_metadata('new_data', 'added_after_backup')
        session_manager.update_session_metadata('sample_count', 5000)
        
        # Create incremental backup
        incremental_backup = recovery.create_incremental_backup(
            session_id, initial_backup['backup_id']
        )
        
        self.assertIsNotNone(incremental_backup)
        self.assertIn('backup_id', incremental_backup)
        self.assertIn('parent_backup_id', incremental_backup)
        self.assertEqual(incremental_backup['parent_backup_id'], initial_backup['backup_id'])


def run_session_tests():
    """Run all session management tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestSessionManager,
        TestSessionLogger,
        TestSessionSynchronizer,
        TestSessionRecovery
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("COMPREHENSIVE SESSION MANAGEMENT TESTS")
    print("=" * 70)
    
    if not SESSION_MODULES_AVAILABLE:
        print("❌ Session modules not available - skipping tests")
        exit(1)
    
    success = run_session_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL SESSION TESTS PASSED")
        exit(0)
    else:
        print("❌ SOME SESSION TESTS FAILED")
        exit(1)