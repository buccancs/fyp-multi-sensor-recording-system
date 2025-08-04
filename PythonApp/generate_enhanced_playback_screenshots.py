#!/usr/bin/env python3
"""
Generate 4K Screenshots with Enhanced Playback Queue System
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
from gui.enhanced_ui_main_window import EnhancedMainWindow


def generate_enhanced_playback_screenshots():
    """Generate 4K screenshots showing the enhanced playback functionality"""
    
    print("Creating Enhanced UI with Playback Queue...")
    
    # Create application
    app = QApplication([])
    app.setStyle("Fusion")
    
    # Create enhanced main window
    window = EnhancedMainWindow()
    window.setWindowTitle("Multi-Sensor Recording System - Enhanced Playback Queue")
    
    # Resize window to 4K resolution for screenshots
    window.resize(3840, 2160)
    
    # Show the window and process events
    window.show()
    app.processEvents()
    
    # Connect some fake devices to make it look active
    try:
        if hasattr(window, 'connect_all_devices'):
            window.connect_all_devices()
            app.processEvents()
            time.sleep(1)
    except:
        pass
    
    # Switch to playback tab to show the queue functionality
    try:
        preview_panel = window.preview_panel
        if preview_panel:
            preview_panel.setCurrentIndex(3)  # Playback tab is 4th tab (index 3)
            app.processEvents()
            time.sleep(3)  # Let the auto-queue populate and UI update
            print("Switched to playback tab with queue system")
        else:
            print("Note: Preview panel not available")
    except Exception as e:
        print(f"Note: Could not switch to playback tab: {e}")
    
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
    
    # Cleanup
    app.quit()


if __name__ == "__main__":
    generate_enhanced_playback_screenshots()