#!/usr/bin/env python3
"""
Screenshot generator for Enhanced UI Features
Creates visual representations of the new playback tab and enhanced menus
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_enhanced_ui_screenshot():
    """Create a visual screenshot showing the enhanced UI features."""
    
    # Create a large canvas for the complete UI
    width, height = 1400, 900
    img = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fall back to default if not available
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        font_normal = ImageFont.truetype("DejaVuSans.ttf", 12)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 10)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw window frame
    draw.rectangle([10, 10, width-10, height-10], outline='#333333', width=2)
    
    # Draw title bar
    draw.rectangle([10, 10, width-10, 40], fill='#2c3e50', outline='#333333')
    draw.text((20, 18), "Multi-Sensor Recording System - Enhanced UI", fill='white', font=font_title)
    
    # Draw menu bar
    draw.rectangle([10, 40, width-10, 70], fill='#ecf0f1', outline='#bdc3c7')
    menu_items = ["File", "Tools", "View", "Help"]
    x_pos = 25
    for item in menu_items:
        draw.text((x_pos, 50), item, fill='black', font=font_normal)
        x_pos += len(item) * 8 + 20
    
    # Draw toolbar
    draw.rectangle([10, 70, width-10, 100], fill='#34495e', outline='#2c3e50')
    toolbar_buttons = ["Connect", "Disconnect", "Start Session", "Stop", "Calibration"]
    x_pos = 25
    for button in toolbar_buttons:
        button_width = len(button) * 8 + 20
        draw.rectangle([x_pos, 75, x_pos + button_width, 95], fill='#3498db', outline='#2980b9')
        draw.text((x_pos + 10, 80), button, fill='white', font=font_small)
        x_pos += button_width + 10
    
    # Draw main content area
    content_y = 110
    
    # Left panel - Device Status
    device_panel_width = 200
    draw.rectangle([20, content_y, 20 + device_panel_width, height-50], fill='white', outline='#bdc3c7')
    draw.text((30, content_y + 10), "Device Status Panel", fill='black', font=font_title)
    
    devices = ["• Device 1 (Connected)", "• Device 2 (Connected)", "• PC Webcam (Active)"]
    y_pos = content_y + 40
    for device in devices:
        draw.text((35, y_pos), device, fill='#27ae60', font=font_small)
        y_pos += 25
    
    # Right panel - Preview area with tabs
    preview_x = 30 + device_panel_width
    preview_width = width - preview_x - 30
    preview_height = 400
    
    # Draw tab bar
    tab_y = content_y
    draw.rectangle([preview_x, tab_y, preview_x + preview_width, tab_y + 30], fill='#ecf0f1', outline='#bdc3c7')
    
    tabs = ["Device 1", "Device 2", "PC Webcam", "Playback"]
    tab_width = preview_width // 4
    for i, tab in enumerate(tabs):
        x_start = preview_x + i * tab_width
        # Highlight the Playback tab
        if tab == "Playback":
            draw.rectangle([x_start, tab_y, x_start + tab_width, tab_y + 30], fill='#3498db', outline='#2980b9')
            text_color = 'white'
        else:
            draw.rectangle([x_start, tab_y, x_start + tab_width, tab_y + 30], fill='#ecf0f1', outline='#bdc3c7')
            text_color = 'black'
        
        # Center the tab text
        text_x = x_start + (tab_width - len(tab) * 6) // 2
        draw.text((text_x, tab_y + 8), tab, fill=text_color, font=font_normal)
    
    # Draw playback tab content
    playback_y = tab_y + 35
    playback_content_height = 350
    
    # Left side of playback tab - Session browser
    browser_width = preview_width // 3
    draw.rectangle([preview_x, playback_y, preview_x + browser_width, playback_y + playback_content_height], 
                  fill='white', outline='#bdc3c7')
    
    # Session browser header
    draw.text((preview_x + 10, playback_y + 10), "Recorded Sessions", fill='black', font=font_title)
    
    # Session list
    sessions = [
        "session_2025_01_15_10_30",
        "session_2025_01_14_14_22", 
        "session_2025_01_13_09_15"
    ]
    
    y_pos = playback_y + 40
    for i, session in enumerate(sessions):
        # Highlight first session as selected
        if i == 0:
            draw.rectangle([preview_x + 5, y_pos - 2, preview_x + browser_width - 5, y_pos + 18], 
                          fill='#3498db', outline='#2980b9')
            text_color = 'white'
        else:
            text_color = 'black'
        
        draw.text((preview_x + 10, y_pos), session, fill=text_color, font=font_small)
        y_pos += 25
    
    # Files section
    draw.text((preview_x + 10, y_pos + 10), "Session Files:", fill='black', font=font_normal)
    files = ["• device_1_camera.mp4", "• device_1_thermal.mp4", "• pc_webcam.mp4"]
    y_pos += 35
    for file in files:
        draw.text((preview_x + 15, y_pos), file, fill='#7f8c8d', font=font_small)
        y_pos += 20
    
    # Refresh button
    draw.rectangle([preview_x + 10, playback_y + playback_content_height - 35, 
                   preview_x + 80, playback_y + playback_content_height - 10], 
                  fill='#95a5a6', outline='#7f8c8d')
    draw.text((preview_x + 20, playback_y + playback_content_height - 30), "Refresh", fill='white', font=font_small)
    
    # Right side - Video player and info
    player_x = preview_x + browser_width + 10
    player_width = preview_width - browser_width - 20
    
    # Video display area
    video_height = 200
    draw.rectangle([player_x, playback_y, player_x + player_width, playback_y + video_height], 
                  fill='black', outline='#2c3e50')
    draw.text((player_x + player_width//2 - 50, playback_y + video_height//2 - 10), 
              "Video Player", fill='white', font=font_title)
    
    # Playback controls
    controls_y = playback_y + video_height + 10
    control_buttons = ["Play", "Stop"]
    x_pos = player_x
    for button in control_buttons:
        button_width = len(button) * 8 + 16
        draw.rectangle([x_pos, controls_y, x_pos + button_width, controls_y + 25], 
                      fill='#2ecc71', outline='#27ae60')
        draw.text((x_pos + 8, controls_y + 6), button, fill='white', font=font_small)
        x_pos += button_width + 10
    
    # Speed control
    draw.text((x_pos, controls_y + 6), "Speed: 1.0x", fill='black', font=font_small)
    
    # Progress bar
    progress_y = controls_y + 35
    draw.rectangle([player_x, progress_y, player_x + player_width - 50, progress_y + 8], 
                  fill='#ecf0f1', outline='#bdc3c7')
    draw.rectangle([player_x, progress_y, player_x + (player_width - 50) // 3, progress_y + 8], 
                  fill='#3498db')
    
    # Time labels
    draw.text((player_x, progress_y + 15), "02:35", fill='black', font=font_small)
    draw.text((player_x + player_width - 40, progress_y + 15), "05:20", fill='black', font=font_small)
    
    # Session info panel
    info_y = progress_y + 40
    info_height = playback_y + playback_content_height - info_y
    draw.rectangle([player_x, info_y, player_x + player_width, playback_y + playback_content_height], 
                  fill='#f8f9fa', outline='#bdc3c7')
    
    draw.text((player_x + 5, info_y + 5), "Session Information:", fill='black', font=font_normal)
    
    info_lines = [
        "Session: session_2025_01_15_10_30",
        "Duration: 125.5 seconds",
        "Devices: 2 (device_1, pc_webcam)",
        "Files: 3 video files (49.3 MB total)",
        "Status: Completed"
    ]
    
    y_pos = info_y + 25
    for line in info_lines:
        draw.text((player_x + 10, y_pos), line, fill='#2c3e50', font=font_small)
        y_pos += 18
    
    # Draw stimulus control panel at bottom
    stimulus_y = content_y + preview_height + 50
    draw.rectangle([20, stimulus_y, width-20, height-20], fill='#ecf0f1', outline='#bdc3c7')
    draw.text((30, stimulus_y + 10), "Stimulus Control Panel", fill='black', font=font_title)
    
    # Add status bar
    draw.rectangle([10, height-20, width-10, height-10], fill='#34495e', outline='#2c3e50')
    draw.text((20, height-18), "Ready - Enhanced UI with Playback functionality active", fill='white', font=font_small)
    
    return img

def create_menu_demonstration():
    """Create a visual demonstration of the enhanced menus."""
    
    # Create canvas for menu demonstration
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        font_normal = ImageFont.truetype("DejaVuSans.ttf", 12)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 10)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    draw.text((width//2 - 150, 20), "Enhanced File and Tools Menus", fill='black', font=font_title)
    
    # File menu demonstration
    file_menu_x = 50
    file_menu_y = 80
    menu_width = 200
    menu_height = 300
    
    draw.rectangle([file_menu_x, file_menu_y, file_menu_x + menu_width, file_menu_y + menu_height], 
                  fill='#f8f9fa', outline='#333333')
    draw.rectangle([file_menu_x, file_menu_y, file_menu_x + menu_width, file_menu_y + 25], 
                  fill='#3498db', outline='#2980b9')
    draw.text((file_menu_x + 10, file_menu_y + 5), "File Menu", fill='white', font=font_title)
    
    file_items = [
        "Recent Sessions ▶",
        "──────────────────",
        "Open Session Folder...",
        "Open Recordings Directory",
        "──────────────────",
        "Export Session Data...",
        "Import Session Data...",
        "──────────────────",
        "Clear Old Recordings...",
        "──────────────────",
        "Preferences...",
        "──────────────────",
        "Exit"
    ]
    
    y_pos = file_menu_y + 35
    for item in file_items:
        if item.startswith("──"):
            draw.line([(file_menu_x + 10, y_pos + 8), (file_menu_x + menu_width - 10, y_pos + 8)], 
                     fill='#bdc3c7', width=1)
        else:
            draw.text((file_menu_x + 10, y_pos), item, fill='black', font=font_small)
        y_pos += 20
    
    # Tools menu demonstration
    tools_menu_x = 300
    tools_menu_y = 80
    
    draw.rectangle([tools_menu_x, tools_menu_y, tools_menu_x + menu_width, tools_menu_y + menu_height], 
                  fill='#f8f9fa', outline='#333333')
    draw.rectangle([tools_menu_x, tools_menu_y, tools_menu_x + menu_width, tools_menu_y + 25], 
                  fill='#e74c3c', outline='#c0392b')
    draw.text((tools_menu_x + 10, tools_menu_y + 5), "Tools Menu", fill='white', font=font_title)
    
    tools_items = [
        "Device Tools ▶",
        "Calibration Tools ▶",
        "Data Analysis ▶",
        "Export Tools ▶",
        "──────────────────",
        "System Information",
        "Performance Monitor",
        "──────────────────",
        "Settings..."
    ]
    
    y_pos = tools_menu_y + 35
    for item in tools_items:
        if item.startswith("──"):
            draw.line([(tools_menu_x + 10, y_pos + 8), (tools_menu_x + menu_width - 10, y_pos + 8)], 
                     fill='#bdc3c7', width=1)
        else:
            draw.text((tools_menu_x + 10, y_pos), item, fill='black', font=font_small)
        y_pos += 25
    
    # Recent sessions submenu
    submenu_x = file_menu_x + menu_width + 5
    submenu_y = file_menu_y + 35
    submenu_width = 180
    submenu_height = 100
    
    draw.rectangle([submenu_x, submenu_y, submenu_x + submenu_width, submenu_y + submenu_height], 
                  fill='#ecf0f1', outline='#333333')
    
    recent_sessions = [
        "session_2025_01_15_10_30",
        "session_2025_01_14_14_22",
        "session_2025_01_13_09_15"
    ]
    
    y_pos = submenu_y + 10
    for session in recent_sessions:
        draw.text((submenu_x + 5, y_pos), session, fill='black', font=font_small)
        y_pos += 25
    
    # Feature highlights
    highlights_y = 450
    draw.text((50, highlights_y), "Key Features:", fill='black', font=font_title)
    
    features = [
        "✓ Playback tab with session browser and video player",
        "✓ File menu with session management and export/import",
        "✓ Tools menu with diagnostics and analysis utilities",
        "✓ Recent sessions quick access",
        "✓ Comprehensive system information and monitoring"
    ]
    
    y_pos = highlights_y + 30
    for feature in features:
        draw.text((60, y_pos), feature, fill='#27ae60', font=font_normal)
        y_pos += 25
    
    return img

def main():
    """Generate all screenshots for the enhanced UI features."""
    
    print("Generating enhanced UI screenshots...")
    
    # Create main UI screenshot
    main_ui = create_enhanced_ui_screenshot()
    main_ui_path = "/home/runner/work/bucika_gsr/bucika_gsr/enhanced_ui_playback_tab.png"
    main_ui.save(main_ui_path)
    print(f"✓ Main UI screenshot saved: {main_ui_path}")
    
    # Create menu demonstration
    menu_demo = create_menu_demonstration()
    menu_demo_path = "/home/runner/work/bucika_gsr/bucika_gsr/enhanced_menus_demo.png"
    menu_demo.save(menu_demo_path)
    print(f"✓ Menu demonstration saved: {menu_demo_path}")
    
    print("\nScreenshots generated successfully!")
    print("Files created:")
    print(f"  - {main_ui_path}")
    print(f"  - {menu_demo_path}")
    
    return True

if __name__ == "__main__":
    main()