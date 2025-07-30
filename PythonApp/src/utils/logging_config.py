"""
Centralized Logging Configuration for Multi-Sensor Recording System

This module provides centralized logging configuration and utilities for the entire
Python application. It sets up consistent logging across all modules with proper
formatting, file rotation, and integration with the existing SessionLogger.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output based on log level."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log record with colors for console output."""
        # Store original level name
        original_levelname = record.levelname
        
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Restore original level name
        record.levelname = original_levelname
        
        return formatted


class AppLogger:
    """
    Centralized logger manager for the Multi-Sensor Recording System.
    
    Provides consistent logging configuration across all modules with:
    - Console output with colors
    - File output with rotation
    - Integration with SessionLogger
    - Configurable log levels
    """
    
    _initialized = False
    _root_logger = None
    _log_dir = None
    
    @classmethod
    def initialize(cls, 
                   log_level: str = "INFO",
                   log_dir: Optional[str] = None,
                   console_output: bool = True,
                   file_output: bool = True) -> None:
        """
        Initialize the application logging system.
        
        Args:
            log_level: Minimum log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            log_dir: Directory for log files (defaults to 'logs' in project root)
            console_output: Whether to output logs to console
            file_output: Whether to output logs to files
        """
        if cls._initialized:
            return
            
        # Set up log directory
        if log_dir is None:
            # Default to 'logs' directory in project root
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        
        cls._log_dir = Path(log_dir)
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get root logger
        cls._root_logger = logging.getLogger()
        cls._root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        cls._root_logger.handlers.clear()
        
        # Console handler with colors
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = ColoredFormatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            cls._root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if file_output:
            # General application log file
            app_log_file = cls._log_dir / "application.log"
            file_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)  # File gets all levels
            cls._root_logger.addHandler(file_handler)
            
            # Error-only log file for critical issues
            error_log_file = cls._log_dir / "errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            error_handler.setFormatter(file_formatter)
            error_handler.setLevel(logging.ERROR)
            cls._root_logger.addHandler(error_handler)
        
        cls._initialized = True
        
        # Log initialization message
        logger = cls.get_logger("AppLogger")
        logger.info("=== Multi-Sensor Recording System Logging Initialized ===")
        logger.info(f"Log level: {log_level}")
        logger.info(f"Log directory: {cls._log_dir}")
        logger.info(f"Console output: {console_output}")
        logger.info(f"File output: {file_output}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (typically __name__ from calling module)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()
        
        return logging.getLogger(name)
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Change the logging level at runtime.
        
        Args:
            level: New log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        if cls._root_logger:
            cls._root_logger.setLevel(getattr(logging, level.upper()))
            # Update console handler level too
            for handler in cls._root_logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                    handler.setLevel(getattr(logging, level.upper()))
    
    @classmethod
    def get_log_dir(cls) -> Optional[Path]:
        """Get the log directory path."""
        return cls._log_dir


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return AppLogger.get_logger(name)


def log_function_entry(func):
    """
    Decorator to automatically log function entry and exit.
    
    Usage:
        @log_function_entry
        def my_function(arg1, arg2):
            pass
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Entering {func.__name__}(args={len(args)}, kwargs={list(kwargs.keys())})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper


def log_method_entry(method):
    """
    Decorator to automatically log method entry and exit.
    
    Usage:
        class MyClass:
            @log_method_entry
            def my_method(self, arg1):
                pass
    """
    def wrapper(self, *args, **kwargs):
        logger = get_logger(self.__class__.__module__)
        logger.debug(f"Entering {self.__class__.__name__}.{method.__name__}(args={len(args)}, kwargs={list(kwargs.keys())})")
        try:
            result = method(self, *args, **kwargs)
            logger.debug(f"Exiting {self.__class__.__name__}.{method.__name__} successfully")
            return result
        except Exception as e:
            logger.error(f"Exception in {self.__class__.__name__}.{method.__name__}: {e}")
            raise
    return wrapper


# Auto-initialize on import with sensible defaults
AppLogger.initialize()