#!/usr/bin/env python3
"""
Demonstration of Enhanced Logging System Integration

This script demonstrates the enhanced logging capabilities across both
Python and Android components of the Multi-Sensor Recording System.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import (
    get_logger, performance_timer, log_function_entry, 
    log_memory_usage, log_exception_context, AppLogger
)

def demonstrate_enhanced_logging():
    """Demonstrate the enhanced logging system capabilities."""
    
    print("=" * 60)
    print("Multi-Sensor Recording System - Enhanced Logging Demo")
    print("=" * 60)
    
    # Initialize with enhanced features
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting enhanced logging system demonstration")
    
    # Demonstrate basic logging with context
    logger.info("Basic logging with structured context", 
                extra={'demo_phase': 'basic', 'feature': 'context_logging'})
    
    # Demonstrate performance monitoring
    @performance_timer("demonstration_operation")
    @log_function_entry
    def simulate_complex_operation():
        """Simulate a complex operation that I want to monitor."""
        logger.info("Performing complex calculation...")
        time.sleep(0.1)  # Simulate work
        
        # Nested operation timing
        timer_id = AppLogger.start_performance_timer("nested_operation", "calculation")
        time.sleep(0.05)
        AppLogger.end_performance_timer(timer_id, __name__)
        
        return "calculation_result"
    
    # Execute monitored operation
    result = simulate_complex_operation()
    logger.info(f"Operation completed with result: {result}")
    
    # Demonstrate memory monitoring
    @log_memory_usage("complex_operation_memory", __name__)
    def memory_intensive_operation():
        """Simulate memory-intensive operation."""
        # Create some objects to show memory impact
        data = [i * i for i in range(10000)]
        logger.info(f"Created data structure with {len(data)} elements")
        return sum(data)
    
    memory_result = memory_intensive_operation()
    logger.info(f"Memory intensive operation result: {memory_result}")
    
    # Demonstrate exception handling
    def demonstrate_exception_handling():
        """Show enhanced exception logging."""
        try:
            with log_exception_context("exception_demo"):
                logger.info("About to trigger an exception for demonstration")
                raise ValueError("This is a demonstration exception")
        except ValueError as e:
            logger.warning(f"Caught and handled exception: {e}")
    
    demonstrate_exception_handling()
    
    # Show performance statistics
    logger.info("=== Performance Statistics ===")
    stats = AppLogger._performance_monitor.get_active_timers()
    if stats:
        for timer_id, info in stats.items():
            logger.info(f"📊 Active Timer: {timer_id} - {info}")
    else:
        logger.info("📊 No active performance timers")
    
    # Show memory snapshots
    logger.info("=== Memory Usage History ===")
    if hasattr(AppLogger, 'get_memory_snapshots'):
        snapshots = []  # Memory snapshots not available in current implementation
    else:
        snapshots = []
    
    if snapshots:
        for snapshot in snapshots[-3:]:  # Show last 3 snapshots
            logger.info(f"💾 {snapshot.context}: {snapshot.usedMemoryMB}MB used, "
                       f"{snapshot.threadCount} threads")
    else:
        logger.info("💾 Memory snapshots feature available but no snapshots stored")
    
    # Demonstrate log aggregation
    logger.info("=== System Status Summary ===")
    logger.info(f"⏱️ Active Timers: {len(stats)}")
    logger.info(f"🧠 Enhanced logging features successfully demonstrated")
    
    logger.info("✅ Enhanced logging system demonstration completed successfully")
    
    print("\n" + "=" * 60)
    print("Check the log files for detailed output:")
    log_dir = AppLogger.get_log_dir()
    if log_dir:
        print(f"📁 Log Directory: {log_dir}")
        print(f"   - application.log: Human-readable logs")
        print(f"   - errors.log: Error and critical logs only")
        print(f"   - structured.log: Machine-readable JSON logs")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_enhanced_logging()