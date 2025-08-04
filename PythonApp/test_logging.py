import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from utils.logging_config import get_logger, AppLogger


def test_logging():
    logger = get_logger('LoggingTest')
    logger.info('=== Testing Multi-Sensor Recording System Logging ===')
    logger.debug('This is a DEBUG message')
    logger.info('This is an INFO message')
    logger.warning('This is a WARNING message')
    logger.error('This is an ERROR message')
    logger.critical('This is a CRITICAL message')
    try:
        raise ValueError('Test exception for logging')
    except Exception as e:
        logger.error('Caught test exception', exc_info=True)
    logger_module2 = get_logger('TestModule2')
    logger_module2.info('Message from different module')
    logger.info('Changing log level to DEBUG')
    AppLogger.set_level('DEBUG')
    logger.debug('This DEBUG message should now be visible')
    AppLogger.set_level('WARNING')
    logger.info('This INFO message should be filtered out')
    logger.warning('This WARNING message should be visible')
    AppLogger.set_level('INFO')
    logger.info('Log level reset to INFO')
    logger.info('=== Logging test completed ===')
    log_dir = AppLogger.get_log_dir()
    if log_dir:
        logger.info(f'Log files are being written to: {log_dir}')
        if log_dir.exists():
            log_files = list(log_dir.glob('*.log'))
            logger.info(f'Log files found: {[f.name for f in log_files]}')


if __name__ == '__main__':
    test_logging()
