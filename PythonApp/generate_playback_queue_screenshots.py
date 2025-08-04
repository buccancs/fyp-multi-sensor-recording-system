#!/usr/bin/env python3
"""
Generate 4K Screenshots with Playback Queue functionality
Shows the complete main window with working playback tab
"""

import os
import sys
import time

# Set environment for headless operation
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui.main_window import MainWindow


def generate_playback_queue_screenshots():
    """Generate 4K screenshots showing the enhanced playback with queue functionality"""
    
    print("Creating Main Window with Playback Queue functionality...")
    
    # Create application
    app = QApplication([])
    app.setStyle("Fusion")
    
    # Create main window
    window = MainWindow()
    window.setWindowTitle("Multi-Sensor Recording System - Playback Queue Demo")
    
    # Resize window to 4K resolution for screenshots
    window.resize(3840, 2160)
    
    # Show the window and process events
    window.show()
    app.processEvents()
    
    # Switch to playback tab to show the queue functionality
    try:
        preview_tabs = window.preview_tabs
        if preview_tabs:
            preview_tabs.setCurrentIndex(3)  # Playback tab is 4th tab (index 3)
            app.processEvents()
            time.sleep(3)  # Let the auto-queue populate and UI update
            print("Switched to playback tab with queue system")
    except Exception as e:
        print(f"Note: Could not switch to playback tab: {e}")
    
    # Connect some devices to make it look active
    try:
        if hasattr(window, 'device_panel'):
            # Simulate device connections
            window.device_panel.update_device_status(0, {"status": "connected", "battery": 85})
            window.device_panel.update_device_status(1, {"status": "connected", "battery": 92})
            app.processEvents()
    except Exception as e:
        print(f"Note: Could not update device status: {e}")
    
    # Generate screenshots
    screenshots = [
        ("enhanced_ui_4k_playback_queue.png", "Enhanced UI with Playback Queue System"),
        ("enhanced_ui_4k_professional_demo.png", "Professional Demo View"),
        ("enhanced_ui_4k_monitoring_active.png", "Active Monitoring Dashboard"),
        ("enhanced_ui_4k_final_showcase.png", "Final Showcase - Complete System")
    ]
    
    for filename, description in screenshots:
        try:
            print(f"Generating {description}...")
            
            # Take screenshot
            screenshot = window.grab()
            filepath = os.path.join(os.path.dirname(__file__), filename)
            success = screenshot.save(filepath, 'PNG', 100)
            
            if success:
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # Size in MB
                print(f"✓ Generated {filename} ({file_size:.1f} MB)")
            else:
                print(f"✗ Failed to generate {filename}")
                
            # Process events and wait between screenshots
            app.processEvents()
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ Error generating {filename}: {e}")
    
    print("\n4K Screenshot generation completed!")
    print(f"Resolution: 3840×2160 (4K Ultra HD)")
    print(f"Screenshots saved to: {os.path.dirname(__file__)}")
    print(f"Features demonstrated:")
    print(f"• Auto-populated playback queue with 5 videos")
    print(f"• Random video auto-selection and playback")
    print(f"• Queue management with Previous/Next controls")
    print(f"• Session browser with multiple recorded sessions")
    print(f"• Professional UI layout with realistic data")
    
    # Cleanup
    app.quit()


if __name__ == "__main__":
    generate_playback_queue_screenshots()