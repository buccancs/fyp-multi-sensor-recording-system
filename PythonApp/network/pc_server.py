"""
PC Server Module
================

Mock implementation for PC server functionality.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PCServer:
    """Mock PC server for testing."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.running = False
    
    def start(self) -> bool:
        """Mock server start."""
        self.running = True
        return True
    
    def stop(self):
        """Mock server stop."""
        self.running = False
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running
    
    def get_status(self) -> Dict[str, any]:
        """Get server status."""
        return {
            'running': self.running,
            'port': self.port,
            'local_ip': '127.0.0.1',
            'pid_file_exists': True,
            'process_exists': self.running
        }