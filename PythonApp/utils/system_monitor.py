"""
System Monitor Module
====================

Simple system monitoring utilities.
"""

import psutil
import logging

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Basic system monitoring."""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()
    
    def get_system_stats(self) -> dict:
        """Get basic system statistics."""
        return {
            'memory_mb': self.get_memory_usage_mb(),
            'cpu_percent': self.get_cpu_usage(),
            'num_threads': self.process.num_threads(),
            'pid': self.process.pid
        }


def get_system_monitor() -> SystemMonitor:
    """Get system monitor instance."""
    return SystemMonitor()