#!/usr/bin/env python3
"""
Cross-Platform Setup Detector and Launcher
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
    elif system in ["linux", "darwin"]:  # darwin is macOS
        return "setup.sh", "bash"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def check_prerequisites():
    """Check if basic prerequisites are available."""
    system = platform.system().lower()
    
    if system == "windows":
        # Check for PowerShell
        try:
            subprocess.run(["powershell", "-Command", "echo 'test'"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: PowerShell not found or not working")
            return False
    else:
        # Check for bash
        try:
            subprocess.run(["bash", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: Bash not found or not working")
            return False


def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("Multi-Sensor Recording System - Cross-Platform Setup")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print("=" * 60)


def main():
    """Main setup function."""
    print_banner()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    try:
        # Detect platform and get setup script
        setup_script, shell = detect_platform()
        setup_path = script_dir / setup_script
        
        if not setup_path.exists():
            print(f"ERROR: Setup script not found: {setup_path}")
            sys.exit(1)
        
        print(f"Detected platform: {platform.system()}")
        print(f"Using setup script: {setup_script}")
        print("=" * 60)
        
        # Prepare command arguments
        cmd_args = sys.argv[1:]  # Forward any command line arguments
        
        if shell == "powershell":
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(setup_path)] + cmd_args
        else:
            cmd = ["bash", str(setup_path)] + cmd_args
        
        # Run the setup script
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        
        # Exit with the same code as the setup script
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()