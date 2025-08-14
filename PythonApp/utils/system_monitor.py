"""
Simplified system monitoring interface - delegates to unified system monitoring.

This module provides a simplified interface to maintain backwards compatibility
while using the unified system monitoring from shared_protocols.
"""

import time

from shared_protocols.system_monitoring import (
    get_system_monitor, 
    start_system_monitoring, 
    stop_system_monitoring,
    get_current_system_metrics,
    get_system_health_report,
    UnifiedSystemMonitor,
    PerformanceMetrics,
    SystemInfo,
    ResourceLimits
)

try:
    from .logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SystemMonitor:
    """Simplified interface that delegates to UnifiedSystemMonitor."""
    
    def __init__(self):
        self._unified_monitor = get_system_monitor()
        self.monitoring = False
        self.monitor_thread = None
        self.system_info = self._get_system_info()
        self._last_update = time.time()
    
    def _get_system_info(self):
        """Get system information using unified monitor."""
        return self._unified_monitor.system_info.__dict__
    
    def start_monitoring(self, interval=1.0):
        """Start monitoring using unified system."""
        self.monitoring = start_system_monitoring(interval)
        return self.monitoring
    
    def stop_monitoring(self):
        """Stop monitoring using unified system."""
        stop_system_monitoring()
        self.monitoring = False
    
    def get_current_metrics(self):
        """Get current metrics using unified system."""
        metrics = get_current_system_metrics()
        return metrics.__dict__ if metrics else {}
    
    def get_health_report(self):
        """Get health report using unified system."""
        return get_system_health_report()
    
    def is_system_healthy(self):
        """Check if system is healthy."""
        report = self.get_health_report()
        return report.get("status") == "good"
    
    def get_memory_usage(self):
        """Get current memory usage."""
        metrics = get_current_system_metrics()
        if metrics:
            return {
                "memory_mb": metrics.memory_mb,
                "memory_percent": metrics.memory_percent
            }
        return {"memory_mb": 0, "memory_percent": 0}
    
    def get_cpu_usage(self):
        """Get current CPU usage."""
        metrics = get_current_system_metrics()
        return metrics.cpu_percent if metrics else 0.0


# Backwards compatibility
def create_system_monitor():
    """Create a system monitor instance."""
    return SystemMonitor()


# Global instance for backwards compatibility  
_global_simple_monitor = None


def get_simple_monitor():
    """Get the simplified monitor instance."""
    global _global_simple_monitor
    if _global_simple_monitor is None:
        _global_simple_monitor = SystemMonitor()
    return _global_simple_monitor


_system_monitor = None

def get_system_monitor() -> SystemMonitor:
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor
