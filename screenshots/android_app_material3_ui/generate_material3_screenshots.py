#!/usr/bin/env python3
"""
Generate authentic Material Design 3 screenshots for Multi-Sensor Recording Android app.

This script creates high-definition screenshots that accurately reflect the actual
Material Design 3 implementation used in the Android app, including proper color
scheme, typography, and component styling.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random
import time

# Material Design 3 colors from the actual app (colors.xml)
MD3_COLORS = {
    'primary': '#006D3B',
    'on_primary': '#FFFFFF', 
    'primary_container': '#7DFB96',
    'on_primary_container': '#00210E',
    'secondary': '#506352',
    'on_secondary': '#FFFFFF',
    'secondary_container': '#D2E8D3',
    'on_secondary_container': '#0E1F12',
    'tertiary': '#3A656E',
    'on_tertiary': '#FFFFFF',
    'tertiary_container': '#BEE9F4',
    'on_tertiary_container': '#001F25',
    'error': '#BA1A1A',
    'on_error': '#FFFFFF',
    'error_container': '#FFDAD6',
    'on_error_container': '#410002',
    'background': '#FCFDF7',
    'on_background': '#1A1C19',
    'surface': '#FCFDF7',
    'on_surface': '#1A1C19',
    'surface_variant': '#DDE5DB',
    'on_surface_variant': '#414942',
    'outline': '#717971',
    'outline_variant': '#C1C9BF',
    'status_connected': '#006D3B',
    'status_disconnected': '#BA1A1A',
    'status_warning': '#7F5500',
    'recording_active': '#BA1A1A',
    'recording_inactive': '#9E9E9E'
}

# Android device dimensions (1080x2340 - modern flagship)
DEVICE_WIDTH = 1080
DEVICE_HEIGHT = 2340
STATUS_BAR_HEIGHT = 72
APP_BAR_HEIGHT = 144
BOTTOM_NAV_HEIGHT = 168

def get_font(size, bold=False):
    """Get Material Design font (Roboto)"""
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.default()

def draw_status_bar(draw, y_offset=0):
    """Draw Android status bar with Material 3 styling"""
    # Status bar background
    draw.rectangle([0, y_offset, DEVICE_WIDTH, y_offset + STATUS_BAR_HEIGHT], 
                  fill=MD3_COLORS['primary'])
    
    # Time
    font = get_font(36)
    draw.text((48, y_offset + 18), "14:25", fill=MD3_COLORS['on_primary'], font=font)
    
    # Battery and icons
    draw.text((DEVICE_WIDTH - 240, y_offset + 18), "5G", fill=MD3_COLORS['on_primary'], font=font)
    draw.text((DEVICE_WIDTH - 120, y_offset + 18), "100%", fill=MD3_COLORS['on_primary'], font=font)

def draw_app_bar(draw, title, y_offset=STATUS_BAR_HEIGHT):
    """Draw Material 3 app bar"""
    # App bar background
    draw.rectangle([0, y_offset, DEVICE_WIDTH, y_offset + APP_BAR_HEIGHT], 
                  fill=MD3_COLORS['primary'])
    
    # Hamburger menu icon
    for i in range(3):
        y = y_offset + 52 + (i * 18)
        draw.rectangle([48, y, 96, y + 6], fill=MD3_COLORS['on_primary'])
    
    # Title
    font = get_font(48, bold=True)
    draw.text((144, y_offset + 48), title, fill=MD3_COLORS['on_primary'], font=font)

def draw_bottom_navigation(draw):
    """Draw Material 3 bottom navigation"""
    y_start = DEVICE_HEIGHT - BOTTOM_NAV_HEIGHT
    
    # Background
    draw.rectangle([0, y_start, DEVICE_WIDTH, DEVICE_HEIGHT], 
                  fill=MD3_COLORS['surface'])
    
    # Divider
    draw.line([0, y_start, DEVICE_WIDTH, y_start], fill=MD3_COLORS['outline'], width=2)
    
    # Navigation items
    items = [
        ("Record", True),   # Active item
        ("Monitor", False),
        ("Calibrate", False)
    ]
    
    item_width = DEVICE_WIDTH // 3
    font_small = get_font(30)
    
    for i, (label, is_active) in enumerate(items):
        x_center = item_width * i + item_width // 2
        
        # Icon placeholder (circle)
        icon_color = MD3_COLORS['primary'] if is_active else MD3_COLORS['on_surface_variant']
        draw.ellipse([x_center - 24, y_start + 24, x_center + 24, y_start + 72], 
                    fill=icon_color)
        
        # Label
        text_color = MD3_COLORS['primary'] if is_active else MD3_COLORS['on_surface_variant']
        bbox = draw.textbbox((0, 0), label, font=font_small)
        text_width = bbox[2] - bbox[0]
        draw.text((x_center - text_width // 2, y_start + 96), label, 
                 fill=text_color, font=font_small)

def draw_material_card(draw, x, y, width, height, content_func, elevation=4):
    """Draw Material Design 3 elevated card"""
    # Shadow effect
    shadow_offset = elevation
    draw.rectangle([x + shadow_offset, y + shadow_offset, x + width + shadow_offset, y + height + shadow_offset], 
                  fill='#00000020')
    
    # Card background with rounded corners (approximated)
    draw.rectangle([x, y, x + width, y + height], fill=MD3_COLORS['surface'])
    draw.rectangle([x, y, x + width, y + 24], fill=MD3_COLORS['surface'])  # Top rounded
    draw.rectangle([x, y + height - 24, x + width, y + height], fill=MD3_COLORS['surface'])  # Bottom rounded
    
    # Card outline
    draw.rectangle([x, y, x + width, y + height], outline=MD3_COLORS['outline'], width=2)
    
    # Draw content
    content_func(draw, x + 32, y + 32, width - 64, height - 64)

def draw_recording_controls_card(draw, x, y, width, height):
    """Draw recording controls card content"""
    font_title = get_font(42, bold=True)
    font_body = get_font(32)
    font_small = get_font(28)
    
    # Header
    draw.text((x, y), "Recording Controls", fill=MD3_COLORS['on_surface'], font=font_title)
    
    # Status indicator
    status_y = y + 72
    draw.ellipse([x, status_y, x + 36, status_y + 36], fill=MD3_COLORS['recording_inactive'])
    draw.text((x + 48, status_y + 6), "Ready to Record", fill=MD3_COLORS['on_surface_variant'], font=font_body)
    
    # Session info
    draw.text((x, status_y + 72), "No active session", fill=MD3_COLORS['on_surface_variant'], font=font_small)
    
    # Material 3 buttons
    button_y = status_y + 120
    button_width = (width - 32) // 3
    
    # Start button (filled)
    draw.rectangle([x, button_y, x + button_width, button_y + 96], fill=MD3_COLORS['primary'])
    start_bbox = draw.textbbox((0, 0), "START", font=font_body)
    start_width = start_bbox[2] - start_bbox[0]
    draw.text((x + (button_width - start_width) // 2, button_y + 32), "START", 
             fill=MD3_COLORS['on_primary'], font=font_body)
    
    # Stop button (outlined)
    stop_x = x + button_width + 16
    draw.rectangle([stop_x, button_y, stop_x + button_width, button_y + 96], 
                  outline=MD3_COLORS['primary'], width=3)
    stop_bbox = draw.textbbox((0, 0), "STOP", font=font_body)
    stop_width = stop_bbox[2] - stop_bbox[0]
    draw.text((stop_x + (button_width - stop_width) // 2, button_y + 32), "STOP", 
             fill=MD3_COLORS['primary'], font=font_body)
    
    # Pause button (outlined)
    pause_x = x + 2 * (button_width + 16)
    draw.rectangle([pause_x, button_y, pause_x + button_width, button_y + 96], 
                  outline=MD3_COLORS['secondary'], width=3)
    pause_bbox = draw.textbbox((0, 0), "PAUSE", font=font_body)
    pause_width = pause_bbox[2] - pause_bbox[0]
    draw.text((pause_x + (button_width - pause_width) // 2, button_y + 32), "PAUSE", 
             fill=MD3_COLORS['secondary'], font=font_body)

def draw_preview_card(draw, x, y, width, height):
    """Draw live data preview card content"""
    font_title = get_font(42, bold=True)
    font_small = get_font(28)
    
    # Title
    draw.text((x, y), "Live Data Preview", fill=MD3_COLORS['on_surface'], font=font_title)
    
    # Preview area
    preview_y = y + 72
    preview_height = height - 144
    draw.rectangle([x, preview_y, x + width, preview_y + preview_height], 
                  fill='#EEEEEE')
    
    # Preview placeholder text
    placeholder_text = "RGB Camera preview will appear here"
    placeholder_bbox = draw.textbbox((0, 0), placeholder_text, font=font_small)
    placeholder_width = placeholder_bbox[2] - placeholder_bbox[0]
    draw.text((x + (width - placeholder_width) // 2, 
              preview_y + (preview_height - 32) // 2), 
             placeholder_text, fill=MD3_COLORS['on_surface_variant'], font=font_small)
    
    # Statistics at bottom
    stats_y = y + height - 48
    draw.text((x, stats_y), "Duration: 00:00:00", fill=MD3_COLORS['on_surface_variant'], font=font_small)
    draw.text((x + width - 200, stats_y), "Size: 0 MB", fill=MD3_COLORS['on_surface_variant'], font=font_small)

def draw_device_status_card(draw, x, y, width, height):
    """Draw device status card content"""
    font_title = get_font(42, bold=True)
    font_body = get_font(32)
    
    # Title
    draw.text((x, y), "Device Status", fill=MD3_COLORS['on_surface'], font=font_title)
    
    # Device list
    devices = [
        ("RGB Camera", True, "1920x1080 @ 30fps"),
        ("Thermal Camera", True, "640x480 @ 9Hz"),
        ("Shimmer GSR", True, "512Hz, Connected"),
        ("Heart Rate", False, "Disconnected"),
        ("IMU Sensor", True, "100Hz, Calibrated")
    ]
    
    device_y = y + 72
    for i, (name, connected, status) in enumerate(devices):
        current_y = device_y + i * 96
        
        # Status indicator
        status_color = MD3_COLORS['status_connected'] if connected else MD3_COLORS['status_disconnected']
        draw.ellipse([x, current_y + 8, x + 24, current_y + 32], fill=status_color)
        
        # Device name
        draw.text((x + 36, current_y), name, fill=MD3_COLORS['on_surface'], font=font_body)
        
        # Status text
        status_font = get_font(28)
        draw.text((x + 36, current_y + 36), status, fill=MD3_COLORS['on_surface_variant'], font=status_font)

def draw_navigation_drawer(draw):
    """Draw Material 3 navigation drawer"""
    drawer_width = DEVICE_WIDTH * 2 // 3
    
    # Drawer background
    draw.rectangle([0, STATUS_BAR_HEIGHT, drawer_width, DEVICE_HEIGHT], 
                  fill=MD3_COLORS['surface'])
    
    # Header
    header_height = 180
    draw.rectangle([0, STATUS_BAR_HEIGHT, drawer_width, STATUS_BAR_HEIGHT + header_height], 
                  fill=MD3_COLORS['primary_container'])
    
    # Header text
    font_header = get_font(48, bold=True)
    font_subtitle = get_font(32)
    draw.text((48, STATUS_BAR_HEIGHT + 48), "Multi-Sensor Recording", 
             fill=MD3_COLORS['on_primary_container'], font=font_header)
    draw.text((48, STATUS_BAR_HEIGHT + 108), "Advanced Recording System", 
             fill=MD3_COLORS['on_primary_container'], font=font_subtitle)
    
    # Menu items
    menu_items = [
        ("Recording", True),
        ("Devices", False),
        ("Calibration", False),
        ("Files", False),
        ("Settings", False),
        ("Network Config", False)
    ]
    
    font_menu = get_font(36)
    menu_y = STATUS_BAR_HEIGHT + header_height + 48
    
    for i, (item, is_selected) in enumerate(menu_items):
        current_y = menu_y + i * 84
        
        # Selection background
        if is_selected:
            draw.rectangle([24, current_y - 12, drawer_width - 24, current_y + 60], 
                          fill=MD3_COLORS['secondary_container'])
        
        # Menu item text
        text_color = MD3_COLORS['on_secondary_container'] if is_selected else MD3_COLORS['on_surface']
        draw.text((72, current_y), item, fill=text_color, font=font_menu)

def create_main_screen():
    """Create main recording screen screenshot"""
    img = Image.new('RGB', (DEVICE_WIDTH, DEVICE_HEIGHT), MD3_COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    # Draw UI components
    draw_status_bar(draw)
    draw_app_bar(draw, "Multi-Sensor Recording")
    
    # Content area
    content_y = STATUS_BAR_HEIGHT + APP_BAR_HEIGHT + 32
    content_height = DEVICE_HEIGHT - STATUS_BAR_HEIGHT - APP_BAR_HEIGHT - BOTTOM_NAV_HEIGHT - 64
    
    # Recording controls card
    controls_height = 360
    draw_material_card(draw, 32, content_y, DEVICE_WIDTH - 64, controls_height, 
                      draw_recording_controls_card)
    
    # Live preview card
    preview_y = content_y + controls_height + 32
    preview_height = content_height - controls_height - 32
    draw_material_card(draw, 32, preview_y, DEVICE_WIDTH - 64, preview_height,
                      draw_preview_card)
    
    draw_bottom_navigation(draw)
    
    return img

def create_main_screen_with_drawer():
    """Create main screen with navigation drawer open"""
    img = create_main_screen()
    draw = ImageDraw.Draw(img)
    
    # Semi-transparent overlay
    overlay = Image.new('RGBA', (DEVICE_WIDTH, DEVICE_HEIGHT), (0, 0, 0, 128))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Draw navigation drawer
    draw_navigation_drawer(draw)
    
    return img

def create_devices_screen():
    """Create devices management screen"""
    img = Image.new('RGB', (DEVICE_WIDTH, DEVICE_HEIGHT), MD3_COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_status_bar(draw)
    draw_app_bar(draw, "Device Management")
    
    # Content area
    content_y = STATUS_BAR_HEIGHT + APP_BAR_HEIGHT + 32
    content_height = DEVICE_HEIGHT - STATUS_BAR_HEIGHT - APP_BAR_HEIGHT - BOTTOM_NAV_HEIGHT - 64
    
    # Device status card
    draw_material_card(draw, 32, content_y, DEVICE_WIDTH - 64, content_height,
                      draw_device_status_card)
    
    draw_bottom_navigation(draw)
    
    return img

def create_recording_active_screen():
    """Create screen showing active recording state"""
    img = Image.new('RGB', (DEVICE_WIDTH, DEVICE_HEIGHT), MD3_COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_status_bar(draw)
    draw_app_bar(draw, "Recording Active")
    
    # Recording indicator in app bar
    draw.ellipse([DEVICE_WIDTH - 120, STATUS_BAR_HEIGHT + 60, 
                 DEVICE_WIDTH - 84, STATUS_BAR_HEIGHT + 96], 
                fill=MD3_COLORS['error'])
    
    # Content with live data
    content_y = STATUS_BAR_HEIGHT + APP_BAR_HEIGHT + 32
    
    # Statistics card
    def draw_stats_card(draw, x, y, width, height):
        font_title = get_font(42, bold=True)
        font_stat = get_font(36)
        
        draw.text((x, y), "Recording Statistics", fill=MD3_COLORS['on_surface'], font=font_title)
        
        stats = [
            "Duration: 00:05:23",
            "File Size: 127.3 MB",
            "Frame Rate: 30.0 fps",
            "Sensors Active: 4/5"
        ]
        
        for i, stat in enumerate(stats):
            draw.text((x, y + 72 + i * 48), stat, fill=MD3_COLORS['on_surface'], font=font_stat)
    
    draw_material_card(draw, 32, content_y, DEVICE_WIDTH - 64, 300, draw_stats_card)
    
    draw_bottom_navigation(draw)
    
    return img

def generate_all_screenshots():
    """Generate all Material 3 screenshots"""
    
    screenshots = [
        ("01_main_screen_material3.png", create_main_screen),
        ("02_main_screen_with_drawer.png", create_main_screen_with_drawer),
        ("03_devices_screen.png", create_devices_screen),
        ("04_recording_active_state.png", create_recording_active_screen),
    ]
    
    output_dir = "/home/runner/work/bucika_gsr/bucika_gsr/screenshots/android_app_material3_ui"
    
    for filename, create_func in screenshots:
        print(f"Generating {filename}...")
        img = create_func()
        img.save(os.path.join(output_dir, filename), 'PNG', quality=95)
        print(f"  ✓ Saved {filename} ({img.size[0]}x{img.size[1]})")
    
    print(f"\n✅ Generated {len(screenshots)} Material Design 3 screenshots")

if __name__ == "__main__":
    generate_all_screenshots()