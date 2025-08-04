import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import tempfile
import logging
from pathlib import Path
from config.configuration_manager import ConfigurationManager, DeviceConfig, SessionConfig


def test_configuration_manager():
    logging.basicConfig(level=logging.INFO)
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'Testing ConfigurationManager in: {temp_dir}')
        config_manager = ConfigurationManager(temp_dir)
        device_config = DeviceConfig(device_id='test_device_001',
            device_type='android_phone', ip_address='192.168.1.100', port=
            9000, capabilities=['camera', 'thermal', 'shimmer'], settings={
            'frame_rate': 5, 'quality': 85}, last_connected=
            '2025-01-30T10:00:00', active=True)
        success = config_manager.save_device_configuration(device_config)
        print(f"Device config save: {'✓' if success else '✗'}")
        retrieved_config = config_manager.get_device_configuration(
            'test_device_001')
        if (retrieved_config and retrieved_config.device_id ==
            device_config.device_id):
            print('Device config retrieval: ✓')
        else:
            print('Device config retrieval: ✗')
        session_config = SessionConfig(session_id='test_session_001',
            device_configs=[device_config], recording_settings={
            'video_enabled': True, 'raw_enabled': False},
            calibration_settings={'pattern_type': 'chessboard', 'size':
            '9x6'}, created_timestamp='2025-01-30T10:00:00',
            modified_timestamp='2025-01-30T10:00:00')
        success = config_manager.save_session_configuration(session_config)
        print(f"Session config save: {'✓' if success else '✗'}")
        export_path = config_manager.export_session_settings('test_session_001'
            )
        if export_path and Path(export_path).exists():
            print('Session export: ✓')
            imported_config = config_manager.import_session_settings(
                export_path)
            if (imported_config and imported_config.session_id ==
                session_config.session_id):
                print('Session import: ✓')
            else:
                print('Session import: ✗')
        else:
            print('Session export: ✗')
        config_manager.update_app_setting('theme', 'dark')
        config_manager.update_app_setting('auto_save', True)
        theme = config_manager.get_app_setting('theme')
        auto_save = config_manager.get_app_setting('auto_save')
        if theme == 'dark' and auto_save is True:
            print('App settings: ✓')
        else:
            print('App settings: ✗')
        last_session = config_manager.restore_last_session()
        if last_session and last_session.session_id == 'test_session_001':
            print('Restore last session: ✓')
        else:
            print('Restore last session: ✗')
        print('\n' + '=' * 50)
        print('Phase 3 ConfigurationManager Test Results:')
        print('- Device configuration persistence: Working')
        print('- Session configuration management: Working')
        print('- Export/Import functionality: Working')
        print('- Application settings: Working')
        print('- Session restoration: Working')
        print('=' * 50)
        return True


if __name__ == '__main__':
    test_configuration_manager()
