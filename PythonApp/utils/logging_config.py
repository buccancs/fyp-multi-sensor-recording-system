"""
Logging Configuration Module
============================

Simple logging setup for the application.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)