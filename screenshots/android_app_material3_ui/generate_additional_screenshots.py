#!/usr/bin/env python3
"""
Generate additional Material Design 3 screenshots for Multi-Sensor Recording Android app.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Material Design 3 colors from the actual app
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
    'background': '#FCFDF7',
    'on_background': '#1A1C19',
    'surface': '#FCFDF7',
    'on_surface': '#1A1C19',
    'surface_variant': '#DDE5DB',
    'on_surface_variant': '#414942',
    'outline': '#717971',
    'outline_variant': '#C1C9BF',
}

# Device dimensions
DEVICE_WIDTH = 1080
DEVICE_HEIGHT = 2340
STATUS_BAR_HEIGHT = 72
APP_BAR_HEIGHT = 144
BOTTOM_NAV_HEIGHT = 168

def get_font(size, bold=False):
    """Get Material Design font"""
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.default()

def draw_status_bar(draw, y_offset=0):
    """Draw Android status bar"""
    draw.rectangle([0, y_offset, DEVICE_WIDTH, y_offset + STATUS_BAR_HEIGHT], 
                  fill=MD3_COLORS['primary'])
    font = get_font(36)
    draw.text((48, y_offset + 18), "14:25", fill=MD3_COLORS['on_primary'], font=font)
    draw.text((DEVICE_WIDTH - 240, y_offset + 18), "5G", fill=MD3_COLORS['on_primary'], font=font)
    draw.text((DEVICE_WIDTH - 120, y_offset + 18), "100%", fill=MD3_COLORS['on_primary'], font=font)

def draw_app_bar(draw, title, y_offset=STATUS_BAR_HEIGHT):
    """Draw Material 3 app bar"""
    draw.rectangle([0, y_offset, DEVICE_WIDTH, y_offset + APP_BAR_HEIGHT], 
                  fill=MD3_COLORS['primary'])
    
    # Menu icon
    for i in range(3):
        y = y_offset + 52 + (i * 18)
        draw.rectangle([48, y, 96, y + 6], fill=MD3_COLORS['on_primary'])
    
    font = get_font(48, bold=True)
    draw.text((144, y_offset + 48), title, fill=MD3_COLORS['on_primary'], font=font)

def draw_material_card(draw, x, y, width, height, content_func, elevation=4):
    """Draw Material Design 3 card"""
    # Shadow
    shadow_offset = elevation
    draw.rectangle([x + shadow_offset, y + shadow_offset, x + width + shadow_offset, y + height + shadow_offset], 
                  fill='#00000020')
    
    # Card background
    draw.rectangle([x, y, x + width, y + height], fill=MD3_COLORS['surface'])
    draw.rectangle([x, y, x + width, y + height], outline=MD3_COLORS['outline'], width=2)
    
    # Content
    content_func(draw, x + 32, y + 32, width - 64, height - 64)

def create_calibration_screen():
    """Create sensor calibration screen"""
    img = Image.new('RGB', (DEVICE_WIDTH, DEVICE_HEIGHT), MD3_COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_status_bar(draw)
    draw_app_bar(draw, "Sensor Calibration")
    
    def draw_calibration_card(draw, x, y, width, height):
        font_title = get_font(42, bold=True)
        font_body = get_font(32)
        font_small = get_font(28)
        
        # Title
        draw.text((x, y), "Camera Calibration", fill=MD3_COLORS['on_surface'], font=font_title)
        
        # Progress indicator
        progress_y = y + 72
        progress_width = width - 64
        progress_bg_height = 24
        
        # Progress background
        draw.rectangle([x + 32, progress_y, x + 32 + progress_width, progress_y + progress_bg_height], 
                      fill=MD3_COLORS['surface_variant'])
        
        # Progress fill (65% complete)
        progress_fill = int(progress_width * 0.65)
        draw.rectangle([x + 32, progress_y, x + 32 + progress_fill, progress_y + progress_bg_height], 
                      fill=MD3_COLORS['primary'])
        
        # Progress text
        draw.text((x + 32, progress_y + 48), "Progress: 65% (13/20 images captured)", 
                 fill=MD3_COLORS['on_surface_variant'], font=font_small)
        
        # Instructions
        instructions_y = progress_y + 120
        instructions = [
            "1. Hold calibration pattern steady",
            "2. Ensure good lighting conditions", 
            "3. Cover all areas of the frame",
            "4. Avoid reflections and shadows"
        ]
        
        for i, instruction in enumerate(instructions):
            draw.text((x, instructions_y + i * 48), instruction, 
                     fill=MD3_COLORS['on_surface'], font=font_body)
        
        # Button
        button_y = instructions_y + len(instructions) * 48 + 48
        button_width = 240
        draw.rectangle([x + (width - button_width) // 2, button_y, 
                       x + (width + button_width) // 2, button_y + 96], 
                      fill=MD3_COLORS['primary'])
        
        button_text = "CAPTURE"
        button_bbox = draw.textbbox((0, 0), button_text, font=font_body)
        button_text_width = button_bbox[2] - button_bbox[0]
        draw.text((x + (width - button_text_width) // 2, button_y + 32), button_text, 
                 fill=MD3_COLORS['on_primary'], font=font_body)
    
    content_y = STATUS_BAR_HEIGHT + APP_BAR_HEIGHT + 32
    content_height = DEVICE_HEIGHT - STATUS_BAR_HEIGHT - APP_BAR_HEIGHT - 64
    
    draw_material_card(draw, 32, content_y, DEVICE_WIDTH - 64, content_height,
                      draw_calibration_card)
    
    return img

def create_files_screen():
    """Create recorded files management screen"""
    img = Image.new('RGB', (DEVICE_WIDTH, DEVICE_HEIGHT), MD3_COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_status_bar(draw)
    draw_app_bar(draw, "Recorded Sessions")
    
    def draw_files_card(draw, x, y, width, height):
        font_title = get_font(42, bold=True)
        font_body = get_font(32)
        font_small = get_font(28)
        
        # Title
        draw.text((x, y), "Recent Sessions", fill=MD3_COLORS['on_surface'], font=font_title)
        
        # File list
        files = [
            ("Session_2025-01-04_14-23", "127.3 MB", "5:23"),
            ("Session_2025-01-04_09-15", "89.7 MB", "3:41"),
            ("Session_2025-01-03_16-30", "201.2 MB", "8:12"),
            ("Calibration_2025-01-03", "15.4 MB", "0:45")
        ]
        
        file_y = y + 72
        for i, (name, size, duration) in enumerate(files):
            current_y = file_y + i * 120
            
            # File item background
            draw.rectangle([x, current_y, x + width, current_y + 96], 
                          fill=MD3_COLORS['surface_variant'])
            
            # File icon
            draw.rectangle([x + 24, current_y + 24, x + 72, current_y + 72], 
                          fill=MD3_COLORS['tertiary'])
            
            # File info
            draw.text((x + 96, current_y + 12), name, fill=MD3_COLORS['on_surface'], font=font_body)
            draw.text((x + 96, current_y + 48), f"{size} • {duration}", 
                     fill=MD3_COLORS['on_surface_variant'], font=font_small)
            
            # Actions
            draw.text((x + width - 120, current_y + 30), "⋮", 
                     fill=MD3_COLORS['on_surface_variant'], font=font_body)
    
    content_y = STATUS_BAR_HEIGHT + APP_BAR_HEIGHT + 32
    content_height = DEVICE_HEIGHT - STATUS_BAR_HEIGHT - APP_BAR_HEIGHT - 64
    
    draw_material_card(draw, 32, content_y, DEVICE_WIDTH - 64, content_height,
                      draw_files_card)
    
    return img

def create_settings_screen():
    """Create application settings screen"""
    img = Image.new('RGB', (DEVICE_WIDTH, DEVICE_HEIGHT), MD3_COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_status_bar(draw)
    draw_app_bar(draw, "Settings")
    
    def draw_settings_card(draw, x, y, width, height):
        font_title = get_font(42, bold=True)
        font_body = get_font(32)
        font_small = get_font(28)
        
        # Settings sections
        sections = [
            ("Recording", [
                "Video Quality: 1080p",
                "Frame Rate: 30 fps",
                "Audio Recording: Enabled"
            ]),
            ("Sensors", [
                "Shimmer GSR: Enabled",
                "Thermal Camera: 9 Hz",
                "Heart Rate: Enabled"
            ]),
            ("Network", [
                "PC Connection: 192.168.1.100",
                "Port: 8080",
                "Auto-sync: Enabled"
            ])
        ]
        
        current_y = y
        for section_name, settings in sections:
            # Section header
            draw.text((x, current_y), section_name, fill=MD3_COLORS['primary'], font=font_title)
            current_y += 60
            
            # Settings items
            for setting in settings:
                draw.text((x + 32, current_y), setting, fill=MD3_COLORS['on_surface'], font=font_body)
                current_y += 48
            
            current_y += 24  # Section spacing
    
    content_y = STATUS_BAR_HEIGHT + APP_BAR_HEIGHT + 32
    content_height = DEVICE_HEIGHT - STATUS_BAR_HEIGHT - APP_BAR_HEIGHT - 64
    
    draw_material_card(draw, 32, content_y, DEVICE_WIDTH - 64, content_height,
                      draw_settings_card)
    
    return img

def generate_additional_screenshots():
    """Generate additional Material 3 screenshots"""
    
    screenshots = [
        ("05_calibration_screen.png", create_calibration_screen),
        ("06_files_screen.png", create_files_screen),
        ("07_settings_screen.png", create_settings_screen),
    ]
    
    output_dir = "/home/runner/work/bucika_gsr/bucika_gsr/screenshots/android_app_material3_ui"
    
    for filename, create_func in screenshots:
        print(f"Generating {filename}...")
        img = create_func()
        img.save(os.path.join(output_dir, filename), 'PNG', quality=95)
        print(f"  ✓ Saved {filename} ({img.size[0]}x{img.size[1]})")
    
    print(f"\n✅ Generated {len(screenshots)} additional Material Design 3 screenshots")

if __name__ == "__main__":
    generate_additional_screenshots()