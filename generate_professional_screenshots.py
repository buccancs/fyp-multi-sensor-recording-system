#!/usr/bin/env python3
"""
High-Quality Screenshot Generator for Enhanced Multi-Sensor Recording System UI
Creates professional demonstration screenshots showing realistic device data and system state.

This script generates high-quality screenshots of the enhanced UI with:
- Realistic device data and status
- Dynamic system monitoring information
- Professional session management interfaces
- Convincing log entries and system information
"""

import os
import sys
import time
from datetime import datetime

# Set up environment for headless operation
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PythonApp', 'src'))

from PyQt5.QtWidgets import QApplication, QTabWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QPainter, QFont

def create_realistic_session_data():
    """Create realistic session data for demonstration"""
    from utils.fake_data_generator import get_fake_data_generator
    
    recordings_dir = os.path.join(os.path.dirname(__file__), 'PythonApp', 'recordings')
    
    # Create realistic session data
    generator = get_fake_data_generator()
    generator.create_realistic_session_files(recordings_dir, count=8)
    
    return recordings_dir

def generate_enhanced_ui_screenshot():
    """Generate high-quality screenshot of enhanced UI with realistic data"""
    print("Generating enhanced UI screenshot with realistic data...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Create realistic session data first
    recordings_dir = create_realistic_session_data()
    print(f"Created realistic session data in: {recordings_dir}")
    
    # Import after setting up environment
    from gui.enhanced_ui_main_window import EnhancedMainWindow
    
    # Create main window
    window = EnhancedMainWindow()
    window.setWindowTitle("Multi-Sensor Recording System - Professional Interface")
    window.resize(1600, 1000)  # Larger size for better quality
    
    # Ensure all data is loaded and displayed
    window.show()
    app.processEvents()
    
    # Wait for realistic data to populate
    time.sleep(2)
    app.processEvents()
    
    # Simulate some recording activity for more interesting display
    window.start_recording()
    app.processEvents()
    
    # Let the timers run to update displays
    time.sleep(3)
    app.processEvents()
    
    # Capture high-quality screenshot
    screenshot = window.grab()
    
    # Save with high quality
    screenshot_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_professional_demo.png')
    success = screenshot.save(screenshot_path, 'PNG', quality=100)
    
    if success:
        print(f"✓ High-quality enhanced UI screenshot saved: {screenshot_path}")
        print(f"  Resolution: {screenshot.width()}x{screenshot.height()}")
        print(f"  File size: {os.path.getsize(screenshot_path)} bytes")
    else:
        print("✗ Failed to save enhanced UI screenshot")
    
    return screenshot_path if success else None

def generate_playback_tab_screenshot():
    """Generate screenshot of the playback tab with realistic session data"""
    print("Generating playback tab screenshot...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Create realistic session data
    recordings_dir = create_realistic_session_data()
    
    # Import enhanced UI components
    from gui.enhanced_ui_main_window import EnhancedMainWindow
    
    # Create main window and switch to playback tab
    window = EnhancedMainWindow()
    window.resize(1600, 1000)
    window.show()
    app.processEvents()
    
    # Let data populate
    time.sleep(2)
    app.processEvents()
    
    # Try to access playback tab if available
    if hasattr(window, 'tab_widget'):
        # Switch to playback tab (assuming it's the 4th tab)
        for i in range(window.tab_widget.count()):
            tab_text = window.tab_widget.tabText(i)
            if 'playback' in tab_text.lower() or 'session' in tab_text.lower():
                window.tab_widget.setCurrentIndex(i)
                break
    
    app.processEvents()
    time.sleep(1)
    
    # Capture screenshot
    screenshot = window.grab()
    screenshot_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_playback_professional.png')
    success = screenshot.save(screenshot_path, 'PNG', quality=100)
    
    if success:
        print(f"✓ Playback tab screenshot saved: {screenshot_path}")
    else:
        print("✗ Failed to save playback tab screenshot")
    
    return screenshot_path if success else None

def generate_device_monitoring_screenshot():
    """Generate focused screenshot of device monitoring section"""
    print("Generating device monitoring screenshot...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    from gui.enhanced_ui_main_window import EnhancedMainWindow
    
    window = EnhancedMainWindow()
    window.resize(1600, 1000)
    window.show()
    app.processEvents()
    
    # Let realistic data populate and update several times
    for _ in range(5):
        time.sleep(1)
        app.processEvents()
        window.update_monitoring()
        window.update_device_status_display()
    
    # Capture screenshot
    screenshot = window.grab()
    screenshot_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_monitoring_professional.png')
    success = screenshot.save(screenshot_path, 'PNG', quality=100)
    
    if success:
        print(f"✓ Device monitoring screenshot saved: {screenshot_path}")
    else:
        print("✗ Failed to save device monitoring screenshot")
    
    return screenshot_path if success else None

def create_combined_demo_image():
    """Create a combined demo image showing multiple aspects"""
    print("Creating combined professional demo image...")
    
    # Generate individual screenshots
    main_screenshot = generate_enhanced_ui_screenshot()
    
    if main_screenshot and os.path.exists(main_screenshot):
        print("✓ Professional demo screenshots generated successfully")
        
        # Copy main screenshot as the primary demo image
        import shutil
        final_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_final_professional.png')
        shutil.copy2(main_screenshot, final_path)
        
        print(f"✓ Final professional demo image: {final_path}")
        return final_path
    else:
        print("✗ Failed to generate demo screenshots")
        return None

def main():
    """Main function to generate all professional screenshots"""
    print("Enhanced Multi-Sensor Recording System - Professional Screenshot Generator")
    print("=" * 80)
    
    try:
        # Generate professional demo image
        final_image = create_combined_demo_image()
        
        if final_image:
            print("\n✓ SUCCESS: Professional screenshots generated!")
            print(f"Main demo image: {final_image}")
            
            # Show file information
            if os.path.exists(final_image):
                size = os.path.getsize(final_image)
                print(f"File size: {size:,} bytes ({size/1024/1024:.1f} MB)")
                
                # Try to get image dimensions
                try:
                    from PIL import Image
                    with Image.open(final_image) as img:
                        print(f"Resolution: {img.width}x{img.height}")
                except ImportError:
                    print("PIL not available for dimension checking")
        else:
            print("\n✗ FAILED: Could not generate professional screenshots")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)