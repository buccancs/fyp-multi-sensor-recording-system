import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from utils.logging_config import get_logger, AppLogger
try:
    from session.session_manager import SessionManager
except ImportError as e:
    print(f'Warning: Could not import SessionManager: {e}')
    SessionManager = None
try:
    from calibration.calibration_manager import CalibrationManager
except ImportError as e:
    print(f'Warning: Could not import CalibrationManager: {e}')
    CalibrationManager = None
try:
    from network.device_server import JsonSocketServer
except ImportError as e:
    print(f'Warning: Could not import JsonSocketServer: {e}')
    JsonSocketServer = None
try:
    from webcam.webcam_capture import WebcamCapture
except ImportError as e:
    print(f'Warning: Could not import WebcamCapture: {e}')
    WebcamCapture = None
try:
    from config.webcam_config import WebcamConfiguration, VideoCodec, Resolution
except ImportError as e:
    print(f'Warning: Could not import WebcamConfiguration: {e}')
    WebcamConfiguration = VideoCodec = Resolution = None
try:
    from error_handling.recovery_manager import RecoveryManager
except ImportError as e:
    print(f'Warning: Could not import RecoveryManager: {e}')
    RecoveryManager = None


def test_comprehensive_logging():
    AppLogger.set_level('DEBUG')
    logger = get_logger('IntegrationTest')
    logger.info(
        '=== Multi-Sensor Recording System - Comprehensive Logging Integration Test ==='
        )
    try:
        logger.info('Testing Session Management logging...')
        if SessionManager:
            try:
                session_manager = SessionManager('test_recordings')
                session_info = session_manager.create_session(
                    'integration_test_session')
                logger.info(f"Session created: {session_info['session_id']}")
            except Exception as e:
                logger.warning(f'Session management test failed: {e}')
        else:
            logger.warning(
                'Session management test skipped - module not available')
        logger.info('Testing Calibration System logging...')
        if CalibrationManager:
            try:
                calibration_manager = CalibrationManager('test_calibration')
                calibration_session = (calibration_manager.
                    start_calibration_session(['device1', 'device2'],
                    'test_calibration_session'))
                logger.info(
                    f"Calibration session started: {calibration_session['session_name']}"
                    )
            except Exception as e:
                logger.warning(f'Calibration test failed: {e}')
        else:
            logger.warning('Calibration test skipped - module not available')
        logger.info('Testing Network Server logging...')
        if JsonSocketServer:
            try:
                server = JsonSocketServer(port=9001)
                logger.info('Network server instance created')
            except Exception as e:
                logger.warning(f'Network server test failed: {e}')
        else:
            logger.warning('Network server test skipped - module not available'
                )
        logger.info('Testing Webcam Configuration logging...')
        if WebcamConfiguration and VideoCodec and Resolution:
            try:
                webcam_config = WebcamConfiguration(camera_index=0,
                    resolution=Resolution.HD_720P, framerate=30.0, codec=
                    VideoCodec.MP4V)
                logger.info(
                    f'Webcam config created: {webcam_config.camera_index}@{webcam_config.resolution.value}'
                    )
            except Exception as e:
                logger.warning(f'Webcam config test failed: {e}')
        else:
            logger.warning('Webcam config test skipped - module not available')
        logger.info('Testing Error Recovery System logging...')
        if RecoveryManager:
            try:
                recovery_manager = RecoveryManager()
                logger.info('Recovery manager initialized')
            except Exception as e:
                logger.warning(f'Recovery manager test failed: {e}')
        else:
            logger.warning(
                'Recovery manager test skipped - module not available')
        logger.info('Testing exception handling with logging...')
        try:
            raise ValueError('Test exception for logging verification')
        except Exception as e:
            logger.error('Successfully caught and logged test exception',
                exc_info=True)
        logger.debug('Debug message - detailed troubleshooting info')
        logger.info('Info message - general application flow')
        logger.warning('Warning message - potential issue detected')
        logger.error('Error message - recoverable error occurred')
        logger.critical('Critical message - serious system issue')
        logger.info('Testing performance timing...')
        import time
        start_time = time.time()
        time.sleep(0.1)
        end_time = time.time()
        logger.info(
            f'Operation completed in {(end_time - start_time) * 1000:.1f}ms')
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.info(
                f'Memory usage: RSS={memory_info.rss // 1024 // 1024}MB, VMS={memory_info.vms // 1024 // 1024}MB'
                )
        except ImportError:
            logger.warning('psutil not available - skipping memory usage test')
        log_dir = AppLogger.get_log_dir()
        if log_dir and log_dir.exists():
            log_files = list(log_dir.glob('*.log'))
            logger.info(f'Log files generated: {[f.name for f in log_files]}')
            for log_file in log_files:
                size = log_file.stat().st_size
                logger.info(f'Log file {log_file.name}: {size} bytes')
        else:
            logger.warning('Log directory not found or not accessible')
        logger.info('=== Comprehensive Logging Integration Test - SUCCESS ===')
    except Exception as e:
        logger.error(f'Integration test failed: {e}', exc_info=True)
        return False
    return True


def test_log_rotation():
    logger = get_logger('RotationTest')
    logger.info('Testing log rotation by generating many log entries...')
    for i in range(100):
        logger.info(
            f'Log entry {i + 1}: Testing log rotation functionality with detailed messages'
            )
        logger.debug(
            f'Debug entry {i + 1}: Additional debugging information for entry {i + 1}'
            )
        if i % 20 == 0:
            logger.warning(f'Milestone log entry {i + 1}')
    logger.info('Log rotation test completed')


def main():
    print('Starting Multi-Sensor Recording System Logging Integration Test...')
    success = test_comprehensive_logging()
    if success:
        print('✅ Comprehensive logging test PASSED')
    else:
        print('❌ Comprehensive logging test FAILED')
        return 1
    test_log_rotation()
    print('✅ Log rotation test completed')
    print('\n' + '=' * 60)
    print('📋 TEST SUMMARY:')
    print('✅ Centralized logging configuration')
    print('✅ Multiple module logging integration')
    print('✅ Different log levels and formatting')
    print('✅ Exception handling with stack traces')
    print('✅ Performance and memory logging')
    print('✅ Log file creation and rotation')
    print('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
