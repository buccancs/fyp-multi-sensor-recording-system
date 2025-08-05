#!/usr/bin/env python3
"""
Cross-Platform Setup Entry Point
Multi-Sensor Recording System

This script automatically detects the platform and launches the appropriate setup script.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def detect_platform():
    """Detect the current platform and return appropriate setup script."""
    system = platform.system().lower()

    if system == "windows":
        return "setup_dev_env.ps1", "powershell"
    elif system in ["linux", "darwin"]:
        return "setup.sh", "bash"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def check_prerequisites():
    """Check if basic prerequisites are available."""
    system = platform.system().lower()

    if system == "windows":
        try:
            subprocess.run(["powershell", "-Command", "echo 'test'"],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: PowerShell not found or not working")
            return False
    else:
        try:
            subprocess.run(["bash", "--version"],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: Bash not found or not working")
            return False


def main():
    """Main entry point."""
    print("=== Multi-Sensor Recording System - Setup Launcher ===")
    print(f"Detected platform: {platform.system()} {platform.release()}")

    if not check_prerequisites():
        sys.exit(1)

    try:
        script_name, shell = detect_platform()
        script_path = Path(__file__).parent / script_name

        if not script_path.exists():
            print(f"ERROR: Setup script not found: {script_path}")
            sys.exit(1)

        print(f"Launching setup script: {script_name}")

        args = [shell, str(script_path)] + sys.argv[1:]

        result = subprocess.run(args)
        sys.exit(result.returncode)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()