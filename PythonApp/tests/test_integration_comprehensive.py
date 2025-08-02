"""comprehensive integration tests for multi-sensor system"""

import pytest
import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from application import Application
from session.session_manager import SessionManager
from network.device_server import JsonSocketServer


class TestIntegrationComprehensive(unittest.TestCase):
    """comprehensive integration tests"""

    def setUp(self):
        """setup test environment"""
        self.app = None

    def tearDown(self):
        """cleanup test environment"""
        if self.app:
            self.app.cleanup()

    @patch('PyQt5.QtWidgets.QApplication')
    def test_application_initialization(self, mock_qt_app):
        """test application initializes correctly"""
        self.app = Application()
        
        # verify services created
        self.assertIsNotNone(self.app.session_manager)
        self.assertIsNotNone(self.app.json_server)
        self.assertIsNotNone(self.app.main_controller)

    @patch('PyQt5.QtWidgets.QApplication')
    def test_service_dependencies(self, mock_qt_app):
        """test service dependencies are properly injected"""
        self.app = Application()
        
        # verify json server has session manager
        self.assertEqual(
            self.app.json_server.session_manager,
            self.app.session_manager
        )

    def test_session_manager_creation(self):
        """test session manager creates properly"""
        session_manager = SessionManager()
        self.assertIsNotNone(session_manager)

    @patch('socket.socket')
    def test_network_server_creation(self, mock_socket):
        """test network server creates with session manager"""
        session_manager = SessionManager()
        server = JsonSocketServer(session_manager=session_manager)
        self.assertIsNotNone(server)
        self.assertEqual(server.session_manager, session_manager)


if __name__ == '__main__':
    unittest.main()