"""
Utilities Module
================

Common utilities and helper functions.
"""

import socket
import subprocess
import platform
from typing import Optional


def get_local_ip() -> Optional[str]:
    """Get the local IP address."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return None


def check_port_available(port: int, host: str = "localhost") -> bool:
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False


def ping_host(host: str, timeout: int = 3) -> bool:
    """Ping a host to check if it's reachable."""
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(
            ["ping", param, "1", host],
            capture_output=True,
            timeout=timeout
        )
        return result.returncode == 0
    except:
        return False


def format_duration(seconds: int) -> str:
    """Format duration in seconds as HH:MM:SS."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"