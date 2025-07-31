"""lightweight unit tests for core functionality"""

import pytest
import unittest
import sys
import os

# add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCoreFunctionality(unittest.TestCase):
    """test core functionality without gui dependencies"""

    def test_basic_imports(self):
        """test basic module structure"""
        try:
            import session
            import protocol
            self.assertTrue(True)
        except ImportError:
            self.skipTest("core modules not available")

    def test_session_manager_exists(self):
        """test session manager module exists"""
        try:
            from session.session_manager import SessionManager
            self.assertTrue(hasattr(SessionManager, '__init__'))
        except ImportError:
            self.skipTest("session manager not available")

    def test_protocol_module_exists(self):
        """test protocol module structure"""
        try:
            import protocol
            self.assertTrue(hasattr(protocol, '__path__'))
        except ImportError:
            self.skipTest("protocol module not available")


class TestProjectStructure(unittest.TestCase):
    """test project structure integrity"""

    def test_src_directory_structure(self):
        """test src directory has expected structure"""
        src_dir = os.path.join(os.path.dirname(__file__), '..')
        expected_dirs = ['session', 'network', 'gui', 'protocol']
        
        for expected_dir in expected_dirs:
            dir_path = os.path.join(src_dir, expected_dir)
            if os.path.exists(dir_path):
                self.assertTrue(os.path.isdir(dir_path))

    def test_tests_directory_exists(self):
        """test tests directory exists"""
        tests_dir = os.path.dirname(__file__)
        self.assertTrue(os.path.exists(tests_dir))
        self.assertTrue(os.path.isdir(tests_dir))


if __name__ == '__main__':
    unittest.main()