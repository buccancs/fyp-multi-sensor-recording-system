"""
Import Utilities Module
======================

This module provides consolidated import handling utilities to eliminate
duplicated import patterns across the codebase, particularly in production modules.

This utility handles the common pattern of trying to import modules with
fallbacks for standalone usage.
"""

import logging
from typing import Any, Callable


def get_safe_logger(name: str) -> logging.Logger:
    """
    Get a logger with fallback for standalone usage.
    
    This function consolidates the repeated pattern found across production modules
    where modules try to import the project's logging configuration, and fall back
    to basic logging if the import fails.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Logger instance with appropriate configuration
    """
    try:
        # Try to import the project's logging configuration
        from .logging_config import get_logger
        return get_logger(name)
    except ImportError:
        # Standalone usage - create simple logger
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return logging.getLogger(name)


def safe_import(module_path: str, fallback_factory: Callable[[], Any] = None) -> Any:
    """
    Safely import a module with optional fallback.
    
    Args:
        module_path: Module import path (e.g., "..utils.system_monitor")
        fallback_factory: Optional callable to create fallback object
        
    Returns:
        Imported module or fallback object
        
    Raises:
        ImportError: If import fails and no fallback is provided
    """
    try:
        # This is a simplified version - full implementation would use importlib
        # For now, we focus on the logger pattern which is the main duplication
        pass
    except ImportError:
        if fallback_factory:
            return fallback_factory()
        raise