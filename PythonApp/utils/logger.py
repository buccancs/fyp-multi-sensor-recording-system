from enum import Enum
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
class LoggerManager:
    def __init__(self, log_directory="logs", max_file_size_mb=10, backup_count=5):
        self.log_directory = log_directory
        self.max_file_size_mb = max_file_size_mb
        self.backup_count = backup_count
        self.loggers = {}
        self.log_handlers = {}
        self.setup_logging_directory()
        self.setup_default_loggers()
    def setup_logging_directory(self):
        import os
        try:
            os.makedirs(self.log_directory, exist_ok=True)
            os.makedirs(os.path.join(self.log_directory, "application"), exist_ok=True)
            os.makedirs(os.path.join(self.log_directory, "network"), exist_ok=True)
            os.makedirs(os.path.join(self.log_directory, "calibration"), exist_ok=True)
            os.makedirs(os.path.join(self.log_directory, "performance"), exist_ok=True)
        except Exception as e:
            print(f"Error creating log directories: {e}")
    def setup_default_loggers(self):
        import logging
        print("[DEBUG_LOG] Setting up default loggers")
        logger_configs = {
            "application": {
                "level": logging.INFO,
                "file": "application/application.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "network": {
                "level": logging.DEBUG,
                "file": "network/network.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
            },
            "calibration": {
                "level": logging.INFO,
                "file": "calibration/calibration.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "performance": {
                "level": logging.INFO,
                "file": "performance/performance.log",
                "format": "%(asctime)s - %(message)s",
            },
        }
        for logger_name, config in logger_configs.items():
            self.create_logger(logger_name, config)
    def create_logger(self, name, config):
        import logging
        import os
        from logging.handlers import RotatingFileHandler
        try:
            if not hasattr(self, "loggers"):
                self.loggers = {}
            self.setup_logging_directory()
            logger = logging.getLogger(name)
            logger.setLevel(config["level"])
            log_file = os.path.join(self.log_directory, config["file"])
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size_mb * 1024 * 1024,
                backupCount=self.backup_count,
            )
            file_handler.setLevel(config["level"])
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            formatter = logging.Formatter(config["format"])
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            self.loggers[name] = logger
            return logger
        except Exception as e:
            print(f"Error creating logger '{name}': {e}")
            return None
    def get_logger(self, name):
        import logging
        if not hasattr(self, "loggers"):
            self.loggers = {}
        if name in self.loggers:
            return self.loggers[name]
        else:
            default_config = {
                "level": logging.INFO,
                "file": f"{name}.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            }
            return self.create_logger(name, default_config)
    def log_structured(self, logger_name, level, message, **kwargs):
        import json
        import threading
        from datetime import datetime
        logger = self.get_logger(logger_name)
        if logger:
            structured_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level.value,
                "message": message,
                "thread_id": threading.current_thread().ident,
                "module": logger_name,
                **kwargs,
            }
            json_message = json.dumps(structured_data, default=str)
            if level == LogLevel.DEBUG:
                logger.debug(json_message)
            elif level == LogLevel.INFO:
                logger.info(json_message)
            elif level == LogLevel.WARNING:
                logger.warning(json_message)
            elif level == LogLevel.ERROR:
                logger.error(json_message)
            elif level == LogLevel.CRITICAL:
                logger.critical(json_message)
        else:
            print(f"[{level.value}] {logger_name}: {message}")
    def log_performance(self, operation, duration_ms, **metadata):
        from datetime import datetime
        try:
            try:
                import psutil
                memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
                cpu_percent = psutil.Process().cpu_percent()
            except ImportError:
                memory_usage_mb = None
                cpu_percent = None
            performance_data = {
                "operation": operation,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "memory_usage_mb": memory_usage_mb,
                "cpu_percent": cpu_percent,
                **metadata,
            }
            self.log_structured(
                "performance",
                LogLevel.INFO,
                f"Operation completed: {operation}",
                **performance_data,
            )
        except Exception as e:
            print(
                f"[PERFORMANCE] {operation} took {duration_ms}ms (logging error: {e})"
            )
    def log_network_event(self, event_type, device_id, **details):
        from datetime import datetime
        try:
            network_data = {
                "event_type": event_type,
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat(),
                **details,
            }
            self.log_structured(
                "network", LogLevel.INFO, f"Network event: {event_type}", **network_data
            )
        except Exception as e:
            print(f"[NETWORK] {event_type} for device {device_id} (logging error: {e})")
    def log_calibration_event(self, event_type, **details):
        from datetime import datetime
        try:
            calibration_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                **details,
            }
            self.log_structured(
                "calibration",
                LogLevel.INFO,
                f"Calibration event: {event_type}",
                **calibration_data,
            )
        except Exception as e:
            print(f"[CALIBRATION] {event_type} (logging error: {e})")
    def export_logs(self, start_date, end_date, output_format="json"):
        import csv
        import gzip
        import json
        import os
        from datetime import datetime
        try:
            exports_dir = os.path.join(self.log_directory, "exports")
            os.makedirs(exports_dir, exist_ok=True)
            export_filename = f"logs_export_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{output_format}"
            export_path = os.path.join(exports_dir, export_filename)
            log_entries = []
            for root, dirs, files in os.walk(self.log_directory):
                for file in files:
                    if file.endswith(".log"):
                        file_path = os.path.join(root, file)
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if start_date <= file_mtime <= end_date:
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    for line in f:
                                        line = line.strip()
                                        if line:
                                            try:
                                                log_entry = json.loads(line)
                                                log_entries.append(log_entry)
                                            except json.JSONDecodeError:
                                                log_entries.append(
                                                    {
                                                        "timestamp": file_mtime.isoformat(),
                                                        "level": "INFO",
                                                        "message": line,
                                                        "source_file": file,
                                                    }
                                                )
                            except Exception as e:
                                print(f"Error reading log file {file_path}: {e}")
            if output_format.lower() == "json":
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(log_entries, f, indent=2, default=str)
            elif output_format.lower() == "csv":
                if log_entries:
                    all_keys = set()
                    for entry in log_entries:
                        all_keys.update(entry.keys())
                    with open(export_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                        writer.writeheader()
                        writer.writerows(log_entries)
            elif output_format.lower() == "txt":
                with open(export_path, "w", encoding="utf-8") as f:
                    for entry in log_entries:
                        if isinstance(entry, dict):
                            timestamp = entry.get("timestamp", "Unknown")
                            level = entry.get("level", "INFO")
                            message = entry.get("message", str(entry))
                            f.write(f"[{timestamp}] {level}: {message}\n")
                        else:
                            f.write(f"{entry}\n")
            if os.path.getsize(export_path) > 1024 * 1024:
                compressed_path = export_path + ".gz"
                with open(export_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        f_out.writelines(f_in)
                os.remove(export_path)
                export_path = compressed_path
            print(f"Logs exported to: {export_path}")
            return export_path
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return ""
    def cleanup_old_logs(self, retention_days=30):
        import gzip
        import os
        import shutil
        from datetime import datetime, timedelta
        cleanup_report = {
            "removed_files": [],
            "compressed_files": [],
            "errors": [],
            "total_space_freed": 0,
        }
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            archive_cutoff = datetime.now() - timedelta(days=7)
            for root, dirs, files in os.walk(self.log_directory):
                if "exports" in root:
                    continue
                for file in files:
                    if file.endswith(".log") or file.endswith(".log.gz"):
                        file_path = os.path.join(root, file)
                        try:
                            file_mtime = datetime.fromtimestamp(
                                os.path.getmtime(file_path)
                            )
                            file_size = os.path.getsize(file_path)
                            if file_mtime < cutoff_date:
                                os.remove(file_path)
                                cleanup_report["removed_files"].append(file_path)
                                cleanup_report["total_space_freed"] += file_size
                                print(f"Removed old log file: {file_path}")
                            elif file_mtime < archive_cutoff and file.endswith(".log"):
                                compressed_path = file_path + ".gz"
                                with open(file_path, "rb") as f_in:
                                    with gzip.open(compressed_path, "wb") as f_out:
                                        shutil.copyfileobj(f_in, f_out)
                                os.remove(file_path)
                                cleanup_report["compressed_files"].append(
                                    compressed_path
                                )
                                space_saved = file_size - os.path.getsize(
                                    compressed_path
                                )
                                cleanup_report["total_space_freed"] += space_saved
                                print(
                                    f"Compressed log file: {file_path} -> {compressed_path}"
                                )
                        except Exception as e:
                            error_msg = f"Error processing log file {file_path}: {e}"
                            cleanup_report["errors"].append(error_msg)
                            print(error_msg)
            print(
                f"Log cleanup completed. Freed {cleanup_report['total_space_freed']} bytes"
            )
            return cleanup_report
        except Exception as e:
            error_msg = f"Error during log cleanup: {e}"
            cleanup_report["errors"].append(error_msg)
            print(error_msg)
            return cleanup_report
logger_manager = None
def get_logger_manager():
    global logger_manager
    if logger_manager is None:
        try:
            import os
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "config", "logging.json"
            )
            if os.path.exists(config_path):
                import json
                with open(config_path, "r") as f:
                    config = json.load(f)
                logger_manager = LoggerManager(
                    log_directory=config.get("log_directory", "logs"),
                    max_file_size_mb=config.get("max_file_size_mb", 10),
                    backup_count=config.get("backup_count", 5),
                )
            else:
                logger_manager = LoggerManager()
        except Exception as e:
            print(f"Warning: Error loading logger configuration: {e}. Using defaults.")
            logger_manager = LoggerManager()
    return logger_manager
def log_info(logger_name, message, **kwargs):
    get_logger_manager().log_structured(logger_name, LogLevel.INFO, message, **kwargs)
def log_error(logger_name, message, **kwargs):
    get_logger_manager().log_structured(logger_name, LogLevel.ERROR, message, **kwargs)
def log_debug(logger_name, message, **kwargs):
    get_logger_manager().log_structured(logger_name, LogLevel.DEBUG, message, **kwargs)
def log_warning(logger_name, message, **kwargs):
    get_logger_manager().log_structured(
        logger_name, LogLevel.WARNING, message, **kwargs
    )
def log_critical(logger_name, message, **kwargs):
    get_logger_manager().log_structured(
        logger_name, LogLevel.CRITICAL, message, **kwargs
    )