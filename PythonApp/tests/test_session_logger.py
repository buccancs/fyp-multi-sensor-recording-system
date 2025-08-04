import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from session.session_logger import SessionLogger, get_session_logger, reset_session_logger


class TestSessionLogger(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.session_logger = SessionLogger(base_sessions_dir=self.test_dir)
        print(
            f'[DEBUG_LOG] Test setup: Using temporary directory {self.test_dir}'
            )

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        reset_session_logger()
        print(
            f'[DEBUG_LOG] Test cleanup: Removed temporary directory {self.test_dir}'
            )

    def test_basic_session_lifecycle(self):
        print('[DEBUG_LOG] Testing basic session lifecycle...')
        devices = [{'id': 'Phone1', 'type': 'android_phone'}, {'id':
            'Phone2', 'type': 'android_phone'}, {'id': 'pc_webcam', 'type':
            'pc_webcam'}]
        session_info = self.session_logger.start_session('TestSession', devices
            )
        self.assertIsNotNone(session_info)
        self.assertIn('session_id', session_info)
        self.assertIn('TestSession', session_info['session_id'])
        self.assertTrue(self.session_logger.is_session_active())
        completed_session = self.session_logger.end_session()
        self.assertIsNotNone(completed_session)
        self.assertFalse(self.session_logger.is_session_active())
        self.assertIsNotNone(completed_session.get('end_time'))
        self.assertIsNotNone(completed_session.get('duration'))
        print('[DEBUG_LOG] Basic session lifecycle test passed')

    def test_event_logging(self):
        print('[DEBUG_LOG] Testing event logging...')
        devices = [{'id': 'TestDevice', 'type': 'test_device'}]
        self.session_logger.start_session('EventTest', devices)
        self.session_logger.log_device_connected('TestDevice',
            'test_device', ['test_capability'])
        self.session_logger.log_recording_start(['TestDevice'], 'EventTest')
        self.session_logger.log_device_ack('TestDevice', 'start_record')
        self.session_logger.log_stimulus_play('test_video.mp4')
        self.session_logger.log_marker('TestMarker', '00:01:30.500')
        self.session_logger.log_stimulus_stop('test_video.mp4')
        self.session_logger.log_file_received('TestDevice', 'test_file.mp4',
            1024000, 'video')
        self.session_logger.log_error('test_error', 'Test error message',
            'TestDevice')
        self.session_logger.log_recording_stop()
        completed_session = self.session_logger.end_session()
        events = completed_session.get('events', [])
        self.assertGreater(len(events), 8)
        event_types = [event.get('event') for event in events]
        expected_events = ['session_start', 'device_connected',
            'start_record', 'device_ack', 'stimulus_play', 'marker',
            'stimulus_stop', 'file_received', 'error', 'stop_record',
            'session_end']
        for expected_event in expected_events:
            self.assertIn(expected_event, event_types,
                f"Event type '{expected_event}' not found in logged events")
        print(
            f'[DEBUG_LOG] Event logging test passed - logged {len(events)} events'
            )

    def test_json_file_creation(self):
        print('[DEBUG_LOG] Testing JSON file creation...')
        self.session_logger.start_session('JSONTest')
        self.session_logger.log_event('test_event', {'test_data': 'test_value'}
            )
        completed_session = self.session_logger.end_session()
        session_id = completed_session['session']
        expected_log_file = Path(self.test_dir
            ) / session_id / f'{session_id}_log.json'
        self.assertTrue(expected_log_file.exists(),
            f'Log file not found at {expected_log_file}')
        with open(expected_log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        required_fields = ['session', 'start_time', 'end_time', 'duration',
            'devices', 'events', 'status']
        for field in required_fields:
            self.assertIn(field, log_data,
                f"Required field '{field}' not found in JSON log")
        events = log_data.get('events', [])
        self.assertGreater(len(events), 0, 'No events found in JSON log')
        for event in events:
            self.assertIn('event', event, "Event missing 'event' field")
            self.assertIn('time', event, "Event missing 'time' field")
            self.assertIn('timestamp', event, "Event missing 'timestamp' field"
                )
        print(
            f'[DEBUG_LOG] JSON file creation test passed - file size: {expected_log_file.stat().st_size} bytes'
            )

    def test_ui_signal_emission(self):
        print('[DEBUG_LOG] Testing UI signal emission...')
        log_entry_mock = Mock()
        session_started_mock = Mock()
        session_ended_mock = Mock()
        error_logged_mock = Mock()
        self.session_logger.log_entry_added.connect(log_entry_mock)
        self.session_logger.session_started.connect(session_started_mock)
        self.session_logger.session_ended.connect(session_ended_mock)
        self.session_logger.error_logged.connect(error_logged_mock)
        self.session_logger.start_session('SignalTest')
        session_started_mock.assert_called()
        self.session_logger.log_event('test_event')
        log_entry_mock.assert_called()
        self.session_logger.log_error('test_error', 'Test error')
        error_logged_mock.assert_called()
        self.session_logger.end_session()
        session_ended_mock.assert_called()
        print('[DEBUG_LOG] UI signal emission test passed')

    def test_global_instance_management(self):
        print('[DEBUG_LOG] Testing global instance management...')
        logger1 = get_session_logger()
        logger2 = get_session_logger()
        self.assertIs(logger1, logger2,
            'Global session logger should be singleton')
        reset_session_logger()
        logger3 = get_session_logger()
        self.assertIsNot(logger1, logger3, 'Reset should create new instance')
        print('[DEBUG_LOG] Global instance management test passed')

    def test_error_handling(self):
        print('[DEBUG_LOG] Testing error handling...')
        self.session_logger.log_event('test_event')
        result = self.session_logger.end_session()
        self.assertIsNone(result,
            'End session without start should return None')
        self.session_logger.start_session('Test1')
        self.assertTrue(self.session_logger.is_session_active())
        self.session_logger.start_session('Test2')
        self.assertTrue(self.session_logger.is_session_active())
        self.session_logger.end_session()
        print('[DEBUG_LOG] Error handling test passed')

    def test_performance_high_frequency_logging(self):
        print('[DEBUG_LOG] Testing high-frequency logging performance...')
        import time
        self.session_logger.start_session('PerformanceTest')
        start_time = time.time()
        event_count = 1000
        for i in range(event_count):
            self.session_logger.log_event(f'test_event_{i}', {'index': i,
                'data': f'test_data_{i}'})
        end_time = time.time()
        duration = end_time - start_time
        completed_session = self.session_logger.end_session()
        events_per_second = event_count / duration
        self.assertGreater(events_per_second, 100,
            'Should handle at least 100 events per second')
        events = completed_session.get('events', [])
        self.assertGreaterEqual(len(events), event_count,
            'All events should be logged')
        print(
            f'[DEBUG_LOG] Performance test passed - {events_per_second:.1f} events/second'
            )

    def test_large_session_simulation(self):
        print('[DEBUG_LOG] Testing large session simulation...')
        devices = [{'id': f'Device_{i}', 'type': 'test_device'} for i in
            range(10)]
        self.session_logger.start_session('LargeSessionTest', devices)
        event_types = [('device_connected', {'device': 'Device_1',
            'device_type': 'test'}), ('start_record', {'devices': [
            'Device_1', 'Device_2']}), ('device_ack', {'device': 'Device_1',
            'command': 'start_record'}), ('stimulus_play', {'media':
            'test_video.mp4'}), ('marker', {'label': 'TestMarker',
            'stim_time': '00:01:30.500'}), ('file_received', {'device':
            'Device_1', 'filename': 'test.mp4', 'size': 1024000}), (
            'stimulus_stop', {'media': 'test_video.mp4'}), ('stop_record', {})]
        cycles = 50
        for cycle in range(cycles):
            for event_type, details in event_types:
                cycle_details = details.copy()
                cycle_details['cycle'] = cycle
                self.session_logger.log_event(event_type, cycle_details)
        completed_session = self.session_logger.end_session()
        events = completed_session.get('events', [])
        expected_events = cycles * len(event_types) + 2
        self.assertGreaterEqual(len(events), expected_events,
            'All events should be logged in large session')
        print(
            f'[DEBUG_LOG] Large session test passed - {len(events)} events logged'
            )

    def test_crash_recovery_simulation(self):
        print('[DEBUG_LOG] Testing crash recovery simulation...')
        self.session_logger.start_session('CrashRecoveryTest')
        self.session_logger.log_event('test_event_1', {'data': 'before_crash'})
        self.session_logger.log_event('test_event_2', {'data': 'before_crash'})
        session_data = self.session_logger.get_current_session()
        log_file_path = self.session_logger.log_file_path
        self.assertTrue(log_file_path.exists(),
            'Log file should exist after crash')
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        events = log_data.get('events', [])
        self.assertGreaterEqual(len(events), 2,
            'Events should be preserved after crash')
        self.assertEqual(log_data.get('session'), session_data.get('session'))
        self.assertEqual(log_data.get('status'), 'active')
        print(
            '[DEBUG_LOG] Crash recovery test passed - data preserved after simulated crash'
            )

    def test_memory_usage_monitoring(self):
        print('[DEBUG_LOG] Testing memory usage monitoring...')
        import sys
        initial_size = sys.getsizeof(self.session_logger)
        self.session_logger.start_session('MemoryTest')
        event_count = 500
        for i in range(event_count):
            self.session_logger.log_event(f'memory_test_{i}', {'index': i,
                'data': f'test_data_{i}' * 10, 'timestamp':
                f'2025-07-30T12:00:{i:02d}.000Z'})
            if i % 100 == 0:
                current_size = sys.getsizeof(self.session_logger)
                growth = current_size - initial_size
                print(
                    f'[DEBUG_LOG] Memory usage after {i} events: {growth} bytes growth'
                    )
        self.session_logger.end_session()
        final_size = sys.getsizeof(self.session_logger)
        total_growth = final_size - initial_size
        max_acceptable_growth = 1024 * 1024
        self.assertLess(total_growth, max_acceptable_growth,
            f'Memory growth ({total_growth} bytes) should be reasonable')
        print(
            f'[DEBUG_LOG] Memory usage test passed - total growth: {total_growth} bytes'
            )

    def test_concurrent_logging_thread_safety(self):
        print('[DEBUG_LOG] Testing concurrent logging thread safety...')
        import threading
        import time
        self.session_logger.start_session('ConcurrencyTest')
        thread_results = []
        thread_count = 5
        events_per_thread = 50

        def logging_thread(thread_id):
            try:
                for i in range(events_per_thread):
                    self.session_logger.log_event(
                        f'thread_{thread_id}_event_{i}', {'thread_id':
                        thread_id, 'event_index': i, 'data':
                        f'thread_{thread_id}_data_{i}'})
                    time.sleep(0.001)
                thread_results.append(
                    f'Thread {thread_id} completed successfully')
            except Exception as e:
                thread_results.append(f'Thread {thread_id} failed: {str(e)}')
        threads = []
        for thread_id in range(thread_count):
            thread = threading.Thread(target=logging_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        completed_session = self.session_logger.end_session()
        self.assertEqual(len(thread_results), thread_count,
            'All threads should complete')
        events = completed_session.get('events', [])
        expected_events = thread_count * events_per_thread + 2
        self.assertEqual(len(events), expected_events,
            'All concurrent events should be logged')
        failed_threads = [result for result in thread_results if 'failed' in
            result]
        self.assertEqual(len(failed_threads), 0,
            f'No threads should fail: {failed_threads}')
        print(
            f'[DEBUG_LOG] Concurrent logging test passed - {len(events)} events from {thread_count} threads'
            )


class TestSessionLoggerIntegration(unittest.TestCase):

    def test_session_manager_integration(self):
        print('[DEBUG_LOG] Testing SessionManager integration...')
        logger = get_session_logger()
        self.assertIsNotNone(logger)
        logger.start_session('IntegrationTest')
        self.assertTrue(logger.is_session_active())
        logger.end_session()
        self.assertFalse(logger.is_session_active())
        reset_session_logger()
        print('[DEBUG_LOG] SessionManager integration test passed')


def run_session_logger_tests():
    print('[DEBUG_LOG] Starting SessionLogger test suite...')
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSessionLogger))
    test_suite.addTest(unittest.makeSuite(TestSessionLoggerIntegration))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    if result.wasSuccessful():
        print(
            f'[DEBUG_LOG] All tests passed! Ran {result.testsRun} tests successfully.'
            )
        return True
    else:
        print(
            f'[DEBUG_LOG] Tests failed! {len(result.failures)} failures, {len(result.errors)} errors.'
            )
        return False


if __name__ == '__main__':
    """Run tests when script is executed directly."""
    success = run_session_logger_tests()
    exit(0 if success else 1)
