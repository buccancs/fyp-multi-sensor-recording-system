#!/usr/bin/env python3
"""
Demonstration script for the new file browsing and camera preview features.

This script demonstrates:
1. PyQt File Browser functionality
2. Web UI with camera preview (can be accessed via browser)
3. Simple test to verify all components work

Usage:
    python demo_features.py
"""

import sys
import os
import time
from pathlib import Path

# Add the PythonApp directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp'))

def demo_file_browser():
    """Demonstrate the PyQt file browser"""
    print("🗂️  Testing PyQt File Browser...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from gui.file_browser_dialog import show_file_browser
        
        app = QApplication(sys.argv)
        
        # Create some test files in recordings directory
        recordings_dir = Path("recordings/demo")
        recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Create demo files
        (recordings_dir / "test_session_1.txt").write_text("Demo session file 1\nTimestamp: 2025-01-01 10:00:00")
        (recordings_dir / "test_session_2.txt").write_text("Demo session file 2\nTimestamp: 2025-01-01 11:00:00")
        (recordings_dir / "demo_video.mp4").touch()
        (recordings_dir / "thermal_data.csv").write_text("timestamp,temperature\n1,25.5\n2,26.1\n")
        
        print(f"✅ Created demo files in {recordings_dir}")
        print("📂 Opening file browser dialog...")
        
        # Show file browser
        selected_file = show_file_browser(None, str(recordings_dir))
        if selected_file:
            print(f"✅ File selected: {selected_file}")
        else:
            print("ℹ️  No file selected (dialog was closed)")
            
        return True
        
    except ImportError as e:
        print(f"❌ PyQt5 not available for file browser demo: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in file browser demo: {e}")
        return False

def demo_web_dashboard():
    """Demonstrate the web dashboard with camera preview"""
    print("\n🌐 Testing Web Dashboard with Camera Preview...")
    
    try:
        from web_ui.web_dashboard import create_web_dashboard
        
        # Create and start web dashboard
        dashboard = create_web_dashboard(host='127.0.0.1', port=5001, debug=False)
        
        print("🚀 Starting web dashboard server...")
        dashboard.start_server()
        
        time.sleep(2)  # Give server time to start
        
        if dashboard.is_running():
            print("✅ Web dashboard is running!")
            print("🔗 Open your browser to: http://127.0.0.1:5001")
            print("📷 Camera preview controls are on the main dashboard")
            print("🗂️  File browser is available at: http://127.0.0.1:5001/files")
            print("\nPress Ctrl+C to stop the server")
            
            try:
                # Keep server running for demonstration
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping web dashboard...")
                dashboard.stop_server()
                print("✅ Web dashboard stopped")
                
        else:
            print("❌ Failed to start web dashboard")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Flask dependencies not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in web dashboard demo: {e}")
        return False

def demo_preview_panel():
    """Demonstrate the enhanced preview panel with IR camera"""
    print("\n📹 Testing Enhanced Preview Panel...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from gui.preview_panel import PreviewPanel
        
        app = QApplication(sys.argv)
        
        # Create main window with preview panel
        window = QMainWindow()
        window.setWindowTitle("Camera Preview Demo - Multi-Sensor Recording System")
        window.resize(800, 600)
        
        # Add preview panel
        preview_panel = PreviewPanel()
        window.setCentralWidget(preview_panel)
        
        print("✅ Preview panel created with tabs:")
        print("   - Device 1 (RGB + Thermal)")
        print("   - Device 2 (RGB + Thermal)")  
        print("   - PC RGB Camera")
        print("   - PC IR Camera (with simulated thermal preview)")
        
        window.show()
        
        print("🖥️  Preview window opened. Try the IR camera preview!")
        print("   Click on 'PC IR Camera' tab and press 'Start IR Preview'")
        
        return True
        
    except ImportError as e:
        print(f"❌ PyQt5 not available for preview panel demo: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in preview panel demo: {e}")
        return False

def main():
    """Main demonstration function"""
    print("🎯 Multi-Sensor Recording System - Feature Demonstration")
    print("=" * 60)
    
    # Test which features are available
    features_available = []
    
    print("\n🔍 Checking available components...")
    
    # Check PyQt5
    try:
        import PyQt5
        print("✅ PyQt5 is available")
        features_available.append("pyqt")
    except ImportError:
        print("❌ PyQt5 not available")
    
    # Check Flask
    try:
        import flask
        print("✅ Flask is available")
        features_available.append("web")
    except ImportError:
        print("❌ Flask not available")
    
    if not features_available:
        print("\n❌ No GUI frameworks available. Please install PyQt5 or Flask:")
        print("   pip install PyQt5 flask flask-socketio")
        return
    
    print(f"\n📋 Available demonstrations: {', '.join(features_available)}")
    
    # Ask user which demo to run
    print("\nSelect demonstration:")
    options = []
    
    if "pyqt" in features_available:
        print("1. PyQt File Browser")
        print("2. PyQt Camera Preview Panel")
        options.extend(["file_browser", "preview_panel"])
    
    if "web" in features_available:
        print("3. Web Dashboard with Camera Preview")
        options.append("web_dashboard")
    
    print("0. Exit")
    
    try:
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            return
        elif choice == "1" and "file_browser" in options:
            demo_file_browser()
        elif choice == "2" and "preview_panel" in options:
            demo_preview_panel()
        elif choice == "3" and "web_dashboard" in options:
            demo_web_dashboard()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Demonstration cancelled")
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")

if __name__ == "__main__":
    main()