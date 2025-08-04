#!/usr/bin/env python3
"""
4K Resolution Screenshot Generator for Enhanced Multi-Sensor Recording System UI
Creates ultra-high-definition demonstration screenshots at 3840x2160 (4K) resolution.

This script generates 4K screenshots of the enhanced UI with:
- Realistic device data and status
- Dynamic system monitoring information
- Professional session management interfaces
- Convincing log entries and system information
- Ultra-high-definition 4K resolution (3840x2160)
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

# 4K Resolution constants
WIDTH_4K = 3840
HEIGHT_4K = 2160

def create_realistic_session_data():
    """Create realistic session data for demonstration"""
    from utils.fake_data_generator import get_fake_data_generator
    
    recordings_dir = os.path.join(os.path.dirname(__file__), 'PythonApp', 'recordings')
    
    # Create realistic session data
    generator = get_fake_data_generator()
    generator.create_realistic_session_files(recordings_dir, count=8)
    
    return recordings_dir

def setup_4k_ui_scaling(app):
    """Configure UI scaling for 4K resolution"""
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Set a larger base font size for 4K resolution
    font = QFont()
    font.setPointSize(12)  # Larger font for better readability at 4K
    app.setFont(font)

def generate_4k_enhanced_ui_screenshot():
    """Generate 4K resolution screenshot of enhanced UI with realistic data"""
    print("Generating 4K enhanced UI screenshot with realistic data...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Setup 4K UI scaling
    setup_4k_ui_scaling(app)
    
    # Create realistic session data first
    recordings_dir = create_realistic_session_data()
    print(f"Created realistic session data in: {recordings_dir}")
    
    # Import after setting up environment
    from gui.enhanced_ui_main_window import EnhancedMainWindow
    
    # Create main window with 4K resolution
    window = EnhancedMainWindow()
    window.setWindowTitle("Multi-Sensor Recording System - 4K Professional Interface")
    window.resize(WIDTH_4K, HEIGHT_4K)
    
    # Ensure all data is loaded and displayed
    window.show()
    app.processEvents()
    
    # Wait for realistic data to populate
    time.sleep(3)
    app.processEvents()
    
    # Simulate some recording activity for more interesting display
    window.start_recording()
    app.processEvents()
    
    # Let the timers run to update displays multiple times for more realistic data
    for _ in range(5):
        time.sleep(1)
        app.processEvents()
        if hasattr(window, 'update_monitoring'):
            window.update_monitoring()
        if hasattr(window, 'update_device_status_display'):
            window.update_device_status_display()
    
    # Capture 4K screenshot
    screenshot = window.grab()
    
    # Save with maximum quality
    screenshot_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_4k_professional.png')
    success = screenshot.save(screenshot_path, 'PNG', quality=100)
    
    if success:
        print(f"✓ 4K enhanced UI screenshot saved: {screenshot_path}")
        print(f"  Resolution: {screenshot.width()}x{screenshot.height()}")
        print(f"  File size: {os.path.getsize(screenshot_path):,} bytes ({os.path.getsize(screenshot_path)/1024/1024:.1f} MB)")
    else:
        print("✗ Failed to save 4K enhanced UI screenshot")
    
    return screenshot_path if success else None

def generate_4k_playback_tab_screenshot():
    """Generate 4K screenshot of the playback tab with realistic session data"""
    print("Generating 4K playback tab screenshot...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    setup_4k_ui_scaling(app)
    
    # Create realistic session data
    recordings_dir = create_realistic_session_data()
    
    # Import enhanced UI components
    from gui.enhanced_ui_main_window import EnhancedMainWindow
    
    # Create main window and switch to playback tab
    window = EnhancedMainWindow()
    window.resize(WIDTH_4K, HEIGHT_4K)
    window.show()
    app.processEvents()
    
    # Let data populate
    time.sleep(3)
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
    time.sleep(2)
    
    # Update displays for more realistic content
    for _ in range(3):
        app.processEvents()
        time.sleep(0.5)
    
    # Capture 4K screenshot
    screenshot = window.grab()
    screenshot_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_4k_playback.png')
    success = screenshot.save(screenshot_path, 'PNG', quality=100)
    
    if success:
        print(f"✓ 4K playback tab screenshot saved: {screenshot_path}")
        print(f"  Resolution: {screenshot.width()}x{screenshot.height()}")
        print(f"  File size: {os.path.getsize(screenshot_path):,} bytes ({os.path.getsize(screenshot_path)/1024/1024:.1f} MB)")
    else:
        print("✗ Failed to save 4K playback tab screenshot")
    
    return screenshot_path if success else None

def generate_4k_device_monitoring_screenshot():
    """Generate focused 4K screenshot of device monitoring section"""
    print("Generating 4K device monitoring screenshot...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    setup_4k_ui_scaling(app)
    
    from gui.enhanced_ui_main_window import EnhancedMainWindow
    
    window = EnhancedMainWindow()
    window.resize(WIDTH_4K, HEIGHT_4K)
    window.show()
    app.processEvents()
    
    # Let realistic data populate and update several times
    for _ in range(8):
        time.sleep(1)
        app.processEvents()
        if hasattr(window, 'update_monitoring'):
            window.update_monitoring()
        if hasattr(window, 'update_device_status_display'):
            window.update_device_status_display()
    
    # Capture 4K screenshot
    screenshot = window.grab()
    screenshot_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_4k_monitoring.png')
    success = screenshot.save(screenshot_path, 'PNG', quality=100)
    
    if success:
        print(f"✓ 4K device monitoring screenshot saved: {screenshot_path}")
        print(f"  Resolution: {screenshot.width()}x{screenshot.height()}")
        print(f"  File size: {os.path.getsize(screenshot_path):,} bytes ({os.path.getsize(screenshot_path)/1024/1024:.1f} MB)")
    else:
        print("✗ Failed to save 4K device monitoring screenshot")
    
    return screenshot_path if success else None

def create_4k_demo_images():
    """Create multiple 4K demo images showing different aspects"""
    print("Creating 4K professional demo images...")
    
    screenshots = []
    
    # Generate individual 4K screenshots
    main_screenshot = generate_4k_enhanced_ui_screenshot()
    if main_screenshot:
        screenshots.append(main_screenshot)
    
    playback_screenshot = generate_4k_playback_tab_screenshot()
    if playback_screenshot:
        screenshots.append(playback_screenshot)
    
    monitoring_screenshot = generate_4k_device_monitoring_screenshot()
    if monitoring_screenshot:
        screenshots.append(monitoring_screenshot)
    
    if screenshots:
        print("✓ 4K professional demo screenshots generated successfully")
        
        # Copy main screenshot as the primary 4K demo image
        if main_screenshot and os.path.exists(main_screenshot):
            import shutil
            final_path = os.path.join(os.path.dirname(__file__), 'enhanced_ui_4k_final.png')
            shutil.copy2(main_screenshot, final_path)
            
            print(f"✓ Final 4K professional demo image: {final_path}")
            screenshots.append(final_path)
        
        return screenshots
    else:
        print("✗ Failed to generate 4K demo screenshots")
        return []

def main():
    """Main function to generate all 4K professional screenshots"""
    print("Enhanced Multi-Sensor Recording System - 4K Screenshot Generator")
    print("=" * 80)
    print(f"Target resolution: {WIDTH_4K}x{HEIGHT_4K} (4K Ultra HD)")
    print("=" * 80)
    
    try:
        # Generate 4K demo images
        screenshots = create_4k_demo_images()
        
        if screenshots:
            print("\n✓ SUCCESS: 4K professional screenshots generated!")
            print("\nGenerated files:")
            
            total_size = 0
            for screenshot in screenshots:
                if os.path.exists(screenshot):
                    size = os.path.getsize(screenshot)
                    total_size += size
                    print(f"  • {os.path.basename(screenshot)}")
                    print(f"    Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
                    
                    # Try to get image dimensions
                    try:
                        from PIL import Image
                        with Image.open(screenshot) as img:
                            print(f"    Resolution: {img.width}x{img.height}")
                    except ImportError:
                        print("    Resolution: 4K (PIL not available for verification)")
                    print()
            
            print(f"Total size: {total_size/1024/1024:.1f} MB")
            
        else:
            print("\n✗ FAILED: Could not generate 4K professional screenshots")
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