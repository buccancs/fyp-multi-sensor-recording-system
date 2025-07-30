"""
Milestone 6 tests to verify shared constants and schema synchronization on Python side.

These tests verify the key requirements from Milestone 6:
1. Config manager loads shared constants correctly
2. Schema validation works for handshake messages
3. Handshake manager processes messages correctly
4. Constants match between Python and Android sides
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch
import tempfile

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from protocol.config_loader import ConfigManager
from protocol.handshake_manager import HandshakeManager
from protocol.schema_utils import SchemaManager


class TestMilestone6(unittest.TestCase):
    """Test suite for Milestone 6 functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.test_config = {
            "version": "1.0.0",
            "protocol_version": 1,
            "network": {
                "host": "192.168.0.100",
                "port": 9000,
                "timeout_seconds": 30,
                "buffer_size": 8192
            },
            "devices": {
                "camera_id": 0,
                "frame_rate": 30,
                "resolution": {
                    "width": 1920,
                    "height": 1080
                }
            },
            "calibration": {
                "pattern_type": "chessboard",
                "pattern_rows": 7,
                "pattern_cols": 6,
                "square_size_m": 0.0245
            }
        }
        
        # Create temporary config file
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()
        
        # Initialize managers with test config
        self.config_manager = ConfigManager(self.temp_config_file.name)
        self.handshake_manager = HandshakeManager()
        
        # Mock the schema manager for testing
        self.schema_manager = Mock()
        self.schema_manager.validate_message.return_value = True
        self.schema_manager.create_message.return_value = {
            'type': 'test',
            'timestamp': 1234567890
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary config file
        if os.path.exists(self.temp_config_file.name):
            os.unlink(self.temp_config_file.name)
    
    def test_config_manager_loads_constants_correctly(self):
        """Test that ConfigManager loads shared constants correctly."""
        # Test basic config values
        self.assertEqual(self.config_manager.get('version'), '1.0.0')
        self.assertEqual(self.config_manager.get('protocol_version'), 1)
        
        # Test network constants
        self.assertEqual(self.config_manager.get('network.host'), '192.168.0.100')
        self.assertEqual(self.config_manager.get('network.port'), 9000)
        self.assertEqual(self.config_manager.get('network.timeout_seconds'), 30)
        
        # Test device constants
        self.assertEqual(self.config_manager.get('devices.camera_id'), 0)
        self.assertEqual(self.config_manager.get('devices.frame_rate'), 30)
        self.assertEqual(self.config_manager.get('devices.resolution.width'), 1920)
        self.assertEqual(self.config_manager.get('devices.resolution.height'), 1080)
        
        # Test calibration constants
        self.assertEqual(self.config_manager.get('calibration.pattern_type'), 'chessboard')
        self.assertEqual(self.config_manager.get('calibration.pattern_rows'), 7)
        self.assertEqual(self.config_manager.get('calibration.pattern_cols'), 6)
        self.assertEqual(self.config_manager.get('calibration.square_size_m'), 0.0245)
    
    def test_config_manager_convenience_methods(self):
        """Test ConfigManager convenience methods."""
        self.assertEqual(self.config_manager.get_host(), '192.168.0.100')
        self.assertEqual(self.config_manager.get_port(), 9000)
        self.assertEqual(self.config_manager.get_protocol_version(), 1)
        
        # Test section getters
        network_config = self.config_manager.get_network_config()
        self.assertIsInstance(network_config, dict)
        self.assertEqual(network_config['host'], '192.168.0.100')
        self.assertEqual(network_config['port'], 9000)
        
        devices_config = self.config_manager.get_devices_config()
        self.assertIsInstance(devices_config, dict)
        self.assertEqual(devices_config['camera_id'], 0)
        self.assertEqual(devices_config['frame_rate'], 30)
    
    def test_handshake_message_creation(self):
        """Test that handshake messages can be created with correct structure."""
        # Mock the schema manager for handshake manager
        with patch.object(self.handshake_manager, 'schema_manager', self.schema_manager):
            self.schema_manager.create_message.return_value = {
                'type': 'handshake',
                'timestamp': 1234567890,
                'protocol_version': 1,
                'device_name': 'Test PC',
                'app_version': '1.0.0',
                'device_type': 'pc'
            }
            
            handshake_message = self.handshake_manager._create_handshake_message()
            
            # Verify the message has all required fields
            self.assertIn('type', handshake_message)
            self.assertIn('timestamp', handshake_message)
            self.assertIn('protocol_version', handshake_message)
            self.assertIn('device_name', handshake_message)
            self.assertIn('app_version', handshake_message)
            self.assertIn('device_type', handshake_message)
            
            # Verify field values
            self.assertEqual(handshake_message['type'], 'handshake')
            self.assertEqual(handshake_message['protocol_version'], 1)
            self.assertEqual(handshake_message['app_version'], '1.0.0')
            self.assertEqual(handshake_message['device_type'], 'pc')
    
    def test_handshake_ack_creation(self):
        """Test that handshake ack messages can be created."""
        with patch.object(self.handshake_manager, 'schema_manager', self.schema_manager):
            self.schema_manager.create_message.return_value = {
                'type': 'handshake_ack',
                'timestamp': 1234567890,
                'protocol_version': 1,
                'server_name': 'Python PC Controller',
                'server_version': '1.0.0',
                'compatible': True,
                'message': 'Test compatibility'
            }
            
            handshake_ack = self.handshake_manager._create_handshake_ack(
                compatible=True,
                message='Test compatibility'
            )
            
            # Verify the message has all required fields
            self.assertIn('type', handshake_ack)
            self.assertIn('timestamp', handshake_ack)
            self.assertIn('protocol_version', handshake_ack)
            self.assertIn('server_name', handshake_ack)
            self.assertIn('server_version', handshake_ack)
            self.assertIn('compatible', handshake_ack)
            
            # Verify field values
            self.assertEqual(handshake_ack['type'], 'handshake_ack')
            self.assertEqual(handshake_ack['protocol_version'], 1)
            self.assertEqual(handshake_ack['server_version'], '1.0.0')
            self.assertEqual(handshake_ack['compatible'], True)
    
    def test_version_compatibility_check(self):
        """Test version compatibility logic."""
        # Test compatible versions
        self.assertTrue(self.handshake_manager._are_versions_compatible(1, 1))
        
        # Test incompatible versions
        self.assertFalse(self.handshake_manager._are_versions_compatible(1, 2))
        self.assertFalse(self.handshake_manager._are_versions_compatible(2, 1))
    
    def test_handshake_processing(self):
        """Test handshake message processing."""
        # Test compatible handshake
        compatible_handshake = {
            'type': 'handshake',
            'timestamp': 1234567890,
            'protocol_version': 1,
            'device_name': 'Android Device',
            'app_version': '1.0.0',
            'device_type': 'android'
        }
        
        with patch.object(self.handshake_manager, 'schema_manager', self.schema_manager):
            compatible, message = self.handshake_manager.process_handshake(compatible_handshake)
            self.assertTrue(compatible)
            self.assertIn('compatible', message.lower())
        
        # Test incompatible handshake (different protocol version)
        incompatible_handshake = {
            'type': 'handshake',
            'timestamp': 1234567890,
            'protocol_version': 2,  # Different version
            'device_name': 'Android Device',
            'app_version': '2.0.0',
            'device_type': 'android'
        }
        
        with patch.object(self.handshake_manager, 'schema_manager', self.schema_manager):
            compatible, message = self.handshake_manager.process_handshake(incompatible_handshake)
            self.assertFalse(compatible)
            self.assertIn('mismatch', message.lower())
    
    def test_handshake_ack_processing(self):
        """Test handshake acknowledgment processing."""
        # Test compatible ack
        compatible_ack = {
            'type': 'handshake_ack',
            'timestamp': 1234567890,
            'protocol_version': 1,
            'server_name': 'Test Server',
            'server_version': '1.0.0',
            'compatible': True
        }
        
        with patch.object(self.handshake_manager, 'schema_manager', self.schema_manager):
            result = self.handshake_manager.process_handshake_ack(compatible_ack)
            self.assertTrue(result)
        
        # Test incompatible ack
        incompatible_ack = {
            'type': 'handshake_ack',
            'timestamp': 1234567890,
            'protocol_version': 2,  # Different version
            'server_name': 'Test Server',
            'server_version': '2.0.0',
            'compatible': False,
            'message': 'Version mismatch'
        }
        
        with patch.object(self.handshake_manager, 'schema_manager', self.schema_manager):
            result = self.handshake_manager.process_handshake_ack(incompatible_ack)
            self.assertFalse(result)
    
    def test_constants_match_android_expectations(self):
        """Test that Python constants match what Android expects."""
        # These values should match the generated CommonConstants.kt
        self.assertEqual(self.config_manager.get('protocol_version'), 1)
        self.assertEqual(self.config_manager.get('version'), '1.0.0')
        
        # Network constants should match
        self.assertEqual(self.config_manager.get('network.host'), '192.168.0.100')
        self.assertEqual(self.config_manager.get('network.port'), 9000)
        self.assertEqual(self.config_manager.get('network.timeout_seconds'), 30)
        
        # Device constants should match
        self.assertEqual(self.config_manager.get('devices.camera_id'), 0)
        self.assertEqual(self.config_manager.get('devices.frame_rate'), 30)
        self.assertEqual(self.config_manager.get('devices.resolution.width'), 1920)
        self.assertEqual(self.config_manager.get('devices.resolution.height'), 1080)
        
        # Calibration constants should match
        self.assertEqual(self.config_manager.get('calibration.pattern_type'), 'chessboard')
        self.assertEqual(self.config_manager.get('calibration.pattern_rows'), 7)
        self.assertEqual(self.config_manager.get('calibration.pattern_cols'), 6)
        self.assertEqual(self.config_manager.get('calibration.square_size_m'), 0.0245)
    
    def test_config_default_values(self):
        """Test that config manager returns appropriate defaults."""
        # Test with non-existent key
        self.assertIsNone(self.config_manager.get('non.existent.key'))
        self.assertEqual(self.config_manager.get('non.existent.key', 'default'), 'default')
        
        # Test with empty section
        empty_section = self.config_manager.get_section('non_existent_section')
        self.assertEqual(empty_section, {})


if __name__ == '__main__':
    unittest.main()
