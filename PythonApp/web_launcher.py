import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from utils.logging_config import get_logger
    from web_ui.integration import WebDashboardIntegration

    logger = get_logger(__name__)
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required dependencies...")
    import subprocess

    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "flask",
                "flask-socketio",
                "eventlet",
            ]
        )
        print("Dependencies installed. Please run the script again.")
        sys.exit(0)
    except Exception as install_error:
        print(f"Failed to install dependencies: {install_error}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Sensor Recording System Web Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_launcher.py
  python web_launcher.py --port 8080
  python web_launcher.py --host 0.0.0.0
  python web_launcher.py --debug
