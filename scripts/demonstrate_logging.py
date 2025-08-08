import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from bucika_gsr.utils.logging_config import (
    get_logger, performance_timer, log_function_entry,
    log_memory_usage, log_exception_context, AppLogger
)
def demonstrate_enhanced_logging():
    print("=" * 60)
    print("Multi-Sensor Recording System - Enhanced Logging Demo")
    print("=" * 60)
    logger = get_logger(__name__)
    logger.info("🚀 Starting enhanced logging system demonstration")
    logger.info("Basic logging with structured context",
                extra={'demo_phase': 'basic', 'feature': 'context_logging'})
    @performance_timer("demonstration_operation")
    @log_function_entry
    def simulate_complex_operation():
        logger.info("Performing complex calculation...")
        time.sleep(0.1)
        timer_id = AppLogger.start_performance_timer("nested_operation", "calculation")
        time.sleep(0.05)
        AppLogger.end_performance_timer(timer_id, __name__)
        return "calculation_result"
    result = simulate_complex_operation()
    logger.info(f"Operation completed with result: {result}")
    @log_memory_usage("complex_operation_memory", __name__)
    def memory_intensive_operation():
        data = [i * i for i in range(10000)]
        logger.info(f"Created data structure with {len(data)} elements")
        return sum(data)
    memory_result = memory_intensive_operation()
    logger.info(f"Memory intensive operation result: {memory_result}")
    def demonstrate_exception_handling():
        try:
            with log_exception_context("exception_demo"):
                logger.info("About to trigger an exception for demonstration")
                raise ValueError("This is a demonstration exception")
        except ValueError as e:
            logger.warning(f"Caught and handled exception: {e}")
    demonstrate_exception_handling()
    logger.info("=== Performance Statistics ===")
    stats = AppLogger._performance_monitor.get_active_timers()
    if stats:
        for timer_id, info in stats.items():
            logger.info(f"📊 Active Timer: {timer_id} - {info}")
    else:
        logger.info("📊 No active performance timers")
    logger.info("=== Memory Usage History ===")
    if hasattr(AppLogger, 'get_memory_snapshots'):
        snapshots = []
    else:
        snapshots = []
    if snapshots:
        for snapshot in snapshots[-3:]:
            logger.info(f"💾 {snapshot.context}: {snapshot.usedMemoryMB}MB used, "
                       f"{snapshot.threadCount} threads")
    else:
        logger.info("💾 Memory snapshots feature available but no snapshots stored")
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