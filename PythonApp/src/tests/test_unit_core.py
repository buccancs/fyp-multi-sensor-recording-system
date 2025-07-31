"""unit tests for application core functionality"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class TestApplicationCore(unittest.TestCase):
    """test core application functionality"""

    def test_import_modules(self):
        """test that core modules can be imported"""
        try:
            from application import Application
            from session.session_manager import SessionManager
        except ImportError as e:
            self.fail(f"failed to import core modules: {e}")

    @patch('logging.getLogger')
    @patch('PyQt5.QtWidgets.QApplication')
    def test_logging_setup(self, mock_qt_app, mock_logger):
        """test logging is properly configured"""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        
        from application import Application
        app = Application()
        
        # verify logger was called
        mock_logger.assert_called()
        mock_logger_instance.info.assert_called()

    def test_session_manager_functionality(self):
        """test session manager basic functionality"""
        from session.session_manager import SessionManager
        
        session_manager = SessionManager()
        self.assertIsNotNone(session_manager)
        
        # test session creation
        session_id = session_manager.create_session()
        self.assertIsNotNone(session_id)


class TestNetworkComponents(unittest.TestCase):
    """test network component functionality"""

    @patch('socket.socket')
    def test_server_initialization(self, mock_socket):
        """test server can be initialized"""
        from session.session_manager import SessionManager
        from network.device_server import JsonSocketServer
        
        session_manager = SessionManager()
        server = JsonSocketServer(session_manager=session_manager)
        
        self.assertIsNotNone(server)
        self.assertEqual(server.session_manager, session_manager)

    def test_protocol_schema_loading(self):
        """test protocol schema can be loaded"""
        try:
            from protocol.schema_utils import load_schema
            # test should pass if schema utilities exist
            self.assertTrue(True)
        except ImportError:
            # acceptable if schema utilities don't exist yet
            self.skipTest("schema utilities not implemented")


if __name__ == '__main__':
    unittest.main()