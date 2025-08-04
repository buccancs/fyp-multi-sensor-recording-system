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

    def setUp(self):
        self.app = None

    def tearDown(self):
        if self.app:
            self.app.cleanup()

    @patch('PyQt5.QtWidgets.QApplication')
    def test_application_initialization(self, mock_qt_app):
        self.app = Application()
        self.assertIsNotNone(self.app.session_manager)
        self.assertIsNotNone(self.app.json_server)
        self.assertIsNotNone(self.app.main_controller)

    @patch('PyQt5.QtWidgets.QApplication')
    def test_service_dependencies(self, mock_qt_app):
        self.app = Application()
        self.assertEqual(self.app.json_server.session_manager, self.app.
            session_manager)

    def test_session_manager_creation(self):
        session_manager = SessionManager()
        self.assertIsNotNone(session_manager)

    @patch('socket.socket')
    def test_network_server_creation(self, mock_socket):
        session_manager = SessionManager()
        server = JsonSocketServer(session_manager=session_manager)
        self.assertIsNotNone(server)
        self.assertEqual(server.session_manager, session_manager)


if __name__ == '__main__':
    unittest.main()
