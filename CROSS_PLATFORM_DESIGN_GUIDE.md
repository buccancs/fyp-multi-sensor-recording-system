# Cross-Platform Design Consistency Guide

## 🎯 Overview

This guide establishes design consistency between the Android app and Python GUI components of the Bucika GSR system, ensuring a unified user experience across platforms while respecting platform-specific conventions.

## 🎨 Unified Design Language

### Color Palette Standardization

```python
# shared_design_tokens.py
"""
Shared design tokens for cross-platform consistency
Used by both Android (via resource generation) and Python GUI
"""

class BucikaColors:
    # Primary Colors
    PRIMARY = "#6750A4"
    ON_PRIMARY = "#FFFFFF"
    PRIMARY_CONTAINER = "#EADDFF"
    ON_PRIMARY_CONTAINER = "#21005D"
    
    # Secondary Colors
    SECONDARY = "#625B71"
    ON_SECONDARY = "#FFFFFF"
    SECONDARY_CONTAINER = "#E8DEF8"
    ON_SECONDARY_CONTAINER = "#1D192B"
    
    # Tertiary Colors
    TERTIARY = "#7D5260"
    ON_TERTIARY = "#FFFFFF"
    TERTIARY_CONTAINER = "#FFD8E4"
    ON_TERTIARY_CONTAINER = "#31111D"
    
    # Error Colors
    ERROR = "#BA1A1A"
    ERROR_CONTAINER = "#FFDAD6"
    ON_ERROR = "#FFFFFF"
    ON_ERROR_CONTAINER = "#410002"
    
    # Surface Colors
    BACKGROUND = "#FFFBFE"
    ON_BACKGROUND = "#1C1B1F"
    SURFACE = "#FFFBFE"
    ON_SURFACE = "#1C1B1F"
    SURFACE_VARIANT = "#E7E0EC"
    ON_SURFACE_VARIANT = "#49454F"
    OUTLINE = "#79747E"
    OUTLINE_VARIANT = "#CAC4D0"
    
    # Status Colors
    STATUS_CONNECTED = "#4CAF50"
    STATUS_DISCONNECTED = "#F44336"
    STATUS_WARNING = "#FF9800"
    STATUS_INFO = "#2196F3"
    
    # Recording State Colors
    RECORDING_ACTIVE = "#F44336"
    RECORDING_INACTIVE = "#9E9E9E"
    STREAMING_ACTIVE = "#4CAF50"

class BucikaTypography:
    # Font Family
    FONT_FAMILY = "Roboto"
    FONT_FAMILY_FALLBACK = ["Arial", "Helvetica", "sans-serif"]
    
    # Display Typography
    DISPLAY_LARGE = {"size": 57, "weight": "normal", "line_height": 64}
    DISPLAY_MEDIUM = {"size": 45, "weight": "normal", "line_height": 52}
    DISPLAY_SMALL = {"size": 36, "weight": "normal", "line_height": 44}
    
    # Headline Typography
    HEADLINE_LARGE = {"size": 32, "weight": "normal", "line_height": 40}
    HEADLINE_MEDIUM = {"size": 28, "weight": "normal", "line_height": 36}
    HEADLINE_SMALL = {"size": 24, "weight": "normal", "line_height": 32}
    
    # Title Typography
    TITLE_LARGE = {"size": 22, "weight": "normal", "line_height": 28}
    TITLE_MEDIUM = {"size": 16, "weight": "500", "line_height": 24}
    TITLE_SMALL = {"size": 14, "weight": "500", "line_height": 20}
    
    # Body Typography
    BODY_LARGE = {"size": 16, "weight": "normal", "line_height": 24}
    BODY_MEDIUM = {"size": 14, "weight": "normal", "line_height": 20}
    BODY_SMALL = {"size": 12, "weight": "normal", "line_height": 16}
    
    # Label Typography
    LABEL_LARGE = {"size": 14, "weight": "500", "line_height": 20}
    LABEL_MEDIUM = {"size": 12, "weight": "500", "line_height": 16}
    LABEL_SMALL = {"size": 11, "weight": "500", "line_height": 16}

class BucikaSpacing:
    # Spacing Scale (in density-independent pixels/points)
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48
    XXXL = 64
    
    # Component-specific spacing
    CARD_PADDING = MD
    BUTTON_PADDING_HORIZONTAL = LG
    BUTTON_PADDING_VERTICAL = 12
    LIST_ITEM_PADDING = MD
    SCREEN_MARGIN = MD
```

### Android Resource Generation

```python
# scripts/generate_android_resources.py
"""
Generate Android XML resources from shared design tokens
"""

def generate_colors_xml():
    """Generate colors.xml from BucikaColors"""
    colors_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Generated from shared design tokens -->
    <color name="md_theme_light_primary">{}</color>
    <color name="md_theme_light_onPrimary">{}</color>
    <color name="md_theme_light_primaryContainer">{}</color>
    <color name="md_theme_light_onPrimaryContainer">{}</color>
    <color name="md_theme_light_secondary">{}</color>
    <color name="md_theme_light_onSecondary">{}</color>
    <color name="md_theme_light_secondaryContainer">{}</color>
    <color name="md_theme_light_onSecondaryContainer">{}</color>
    <!-- ... additional colors ... -->
</resources>'''.format(
        BucikaColors.PRIMARY,
        BucikaColors.ON_PRIMARY,
        BucikaColors.PRIMARY_CONTAINER,
        BucikaColors.ON_PRIMARY_CONTAINER,
        BucikaColors.SECONDARY,
        BucikaColors.ON_SECONDARY,
        BucikaColors.SECONDARY_CONTAINER,
        BucikaColors.ON_SECONDARY_CONTAINER
    )
    
    with open('AndroidApp/src/main/res/values/colors_generated.xml', 'w') as f:
        f.write(colors_xml)

def generate_dimens_xml():
    """Generate dimens.xml from BucikaSpacing"""
    dimens_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Generated from shared design tokens -->
    <dimen name="spacing_xs">{}dp</dimen>
    <dimen name="spacing_sm">{}dp</dimen>
    <dimen name="spacing_md">{}dp</dimen>
    <dimen name="spacing_lg">{}dp</dimen>
    <dimen name="spacing_xl">{}dp</dimen>
    <dimen name="spacing_xxl">{}dp</dimen>
    <dimen name="spacing_xxxl">{}dp</dimen>
</resources>'''.format(
        BucikaSpacing.XS,
        BucikaSpacing.SM,
        BucikaSpacing.MD,
        BucikaSpacing.LG,
        BucikaSpacing.XL,
        BucikaSpacing.XXL,
        BucikaSpacing.XXXL
    )
    
    with open('AndroidApp/src/main/res/values/dimens_generated.xml', 'w') as f:
        f.write(dimens_xml)
```

## 🖥️ Python GUI Implementation

### Modern Python GUI with Consistency

```python
# src/gui/bucika_gui_framework.py
"""
Modern Python GUI framework for Bucika GSR system
Maintains consistency with Android Material Design 3
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, Any, Callable
from shared_design_tokens import BucikaColors, BucikaTypography, BucikaSpacing

class BucikaGUIFramework:
    """
    GUI framework that mirrors Android Material Design 3 components
    """
    
    def __init__(self):
        self.setup_custom_tkinter_theme()
        
    def setup_custom_tkinter_theme(self):
        """Configure CustomTkinter with Bucika design tokens"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")  # We'll override with custom colors
        
        # Custom color theme
        self.colors = {
            "primary": BucikaColors.PRIMARY,
            "primary_container": BucikaColors.PRIMARY_CONTAINER,
            "secondary": BucikaColors.SECONDARY,
            "surface": BucikaColors.SURFACE,
            "surface_variant": BucikaColors.SURFACE_VARIANT,
            "background": BucikaColors.BACKGROUND,
            "error": BucikaColors.ERROR,
            "outline": BucikaColors.OUTLINE,
        }
        
    def create_primary_button(self, parent, text: str, command: Callable, **kwargs) -> ctk.CTkButton:
        """Create Material Design 3 styled primary button"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=self.colors["primary"],
            hover_color=self._darken_color(self.colors["primary"], 0.1),
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.LABEL_LARGE["size"],
                weight=BucikaTypography.LABEL_LARGE["weight"]
            ),
            height=48,  # Consistent with Android touch targets
            corner_radius=20,  # Material Design 3 button radius
            **kwargs
        )
        
    def create_outlined_button(self, parent, text: str, command: Callable, **kwargs) -> ctk.CTkButton:
        """Create Material Design 3 styled outlined button"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            border_color=self.colors["outline"],
            border_width=1,
            text_color=self.colors["primary"],
            hover_color=self.colors["surface_variant"],
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.LABEL_LARGE["size"],
                weight=BucikaTypography.LABEL_LARGE["weight"]
            ),
            height=48,
            corner_radius=20,
            **kwargs
        )
        
    def create_card(self, parent, **kwargs) -> ctk.CTkFrame:
        """Create Material Design 3 styled card"""
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["surface"],
            corner_radius=12,  # Material Design 3 card radius
            border_width=1,
            border_color=self.colors["outline"],
            **kwargs
        )
        
    def create_status_chip(self, parent, text: str, status: str, **kwargs) -> ctk.CTkFrame:
        """Create status chip similar to Android implementation"""
        status_colors = {
            "connected": BucikaColors.STATUS_CONNECTED,
            "disconnected": BucikaColors.STATUS_DISCONNECTED,
            "warning": BucikaColors.STATUS_WARNING,
            "info": BucikaColors.STATUS_INFO
        }
        
        chip_frame = ctk.CTkFrame(
            parent,
            fg_color=status_colors.get(status, BucikaColors.STATUS_INFO),
            corner_radius=16,
            height=32,
            **kwargs
        )
        
        label = ctk.CTkLabel(
            chip_frame,
            text=text,
            text_color=BucikaColors.ON_PRIMARY,
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.LABEL_MEDIUM["size"],
                weight=BucikaTypography.LABEL_MEDIUM["weight"]
            )
        )
        label.pack(padx=12, pady=6)
        
        return chip_frame
        
    def create_section_header(self, parent, text: str, **kwargs) -> ctk.CTkLabel:
        """Create section header with consistent typography"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.TITLE_LARGE["size"],
                weight="bold"
            ),
            text_color=self.colors["primary"],
            **kwargs
        )
        
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Utility to darken a hex color for hover states"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened_rgb = tuple(int(c * (1 - factor)) for c in rgb)
        return '#%02x%02x%02x' % darkened_rgb

class BucikaMainWindow(ctk.CTk):
    """
    Main application window with Material Design 3 styling
    """
    
    def __init__(self):
        super().__init__()
        
        self.framework = BucikaGUIFramework()
        self.setup_window()
        self.create_layout()
        
    def setup_window(self):
        """Configure main window properties"""
        self.title("Bucika GSR - PC Control Center")
        self.geometry("1200x800")
        self.configure(fg_color=BucikaColors.BACKGROUND)
        
        # Set minimum size
        self.minsize(800, 600)
        
    def create_layout(self):
        """Create main application layout"""
        # Top navigation bar
        self.create_top_navigation()
        
        # Main content area with sidebar
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
    def create_top_navigation(self):
        """Create top navigation bar similar to Android top app bar"""
        nav_frame = ctk.CTkFrame(
            self,
            height=56,  # Material Design app bar height
            fg_color=BucikaColors.PRIMARY,
            corner_radius=0
        )
        nav_frame.pack(fill="x", padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # App title
        title_label = ctk.CTkLabel(
            nav_frame,
            text="Bucika GSR Control Center",
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.TITLE_LARGE["size"],
                weight="bold"
            ),
            text_color=BucikaColors.ON_PRIMARY
        )
        title_label.pack(side="left", padx=20, pady=16)
        
        # Navigation buttons
        nav_buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_buttons_frame.pack(side="right", padx=20, pady=8)
        
        nav_items = ["Dashboard", "Devices", "Sessions", "Settings"]
        for item in nav_items:
            btn = ctk.CTkButton(
                nav_buttons_frame,
                text=item,
                fg_color="transparent",
                hover_color=self.framework._darken_color(BucikaColors.PRIMARY, 0.1),
                text_color=BucikaColors.ON_PRIMARY,
                width=80,
                height=32,
                corner_radius=16
            )
            btn.pack(side="left", padx=4)
            
    def create_main_content(self):
        """Create main content area with navigation and content"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Left sidebar for navigation (similar to Android navigation drawer)
        self.create_sidebar(main_frame)
        
        # Main content area
        self.create_content_area(main_frame)
        
    def create_sidebar(self, parent):
        """Create sidebar navigation"""
        sidebar = ctk.CTkFrame(
            parent,
            width=250,
            fg_color=BucikaColors.SURFACE_VARIANT,
            corner_radius=12
        )
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)
        
        # Sidebar header
        header = self.framework.create_section_header(
            sidebar, 
            "Navigation"
        )
        header.pack(pady=(20, 10), padx=20)
        
        # Navigation items
        nav_items = [
            ("🎬", "Recording Control"),
            ("📊", "Live Monitoring"),
            ("🗂️", "Session Files"),
            ("⚙️", "Device Settings"),
            ("🔧", "Advanced Tools")
        ]
        
        for icon, label in nav_items:
            item_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=40)
            item_frame.pack(fill="x", padx=12, pady=2)
            item_frame.pack_propagate(False)
            
            icon_label = ctk.CTkLabel(
                item_frame,
                text=icon,
                width=30,
                font=ctk.CTkFont(size=16)
            )
            icon_label.pack(side="left", padx=(8, 4), pady=8)
            
            text_label = ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(
                    family=BucikaTypography.FONT_FAMILY,
                    size=BucikaTypography.BODY_MEDIUM["size"]
                ),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True, padx=(4, 8), pady=8)
            
    def create_content_area(self, parent):
        """Create main content area"""
        content_frame = ctk.CTkFrame(
            parent,
            fg_color=BucikaColors.SURFACE,
            corner_radius=12
        )
        content_frame.pack(side="right", fill="both", expand=True)
        
        # Content header
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        title = self.framework.create_section_header(
            header_frame,
            "Device Status & Control"
        )
        title.pack(side="left", pady=20)
        
        # Status indicators (similar to Android chips)
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="right", pady=16)
        
        statuses = [
            ("Shimmer GSR", "connected"),
            ("Thermal Camera", "connected"),
            ("PC Connection", "connected")
        ]
        
        for i, (device, status) in enumerate(statuses):
            chip = self.framework.create_status_chip(status_frame, device, status)
            chip.pack(side="left", padx=4)
            
        # Main content cards
        self.create_content_cards(content_frame)
        
    def create_content_cards(self, parent):
        """Create content cards similar to Android card layout"""
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Recording control card
        recording_card = self.framework.create_card(scroll_frame)
        recording_card.pack(fill="x", pady=(0, 16))
        
        card_header = self.framework.create_section_header(
            recording_card,
            "Recording Controls"
        )
        card_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        button_frame = ctk.CTkFrame(recording_card, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        start_btn = self.framework.create_primary_button(
            button_frame,
            "Start Recording",
            self.start_recording
        )
        start_btn.pack(side="left", padx=(0, 12))
        
        stop_btn = self.framework.create_outlined_button(
            button_frame,
            "Stop Recording",
            self.stop_recording
        )
        stop_btn.pack(side="left", padx=12)
        
        calibrate_btn = self.framework.create_outlined_button(
            button_frame,
            "Calibration",
            self.run_calibration
        )
        calibrate_btn.pack(side="left", padx=12)
        
        # Live data card
        data_card = self.framework.create_card(scroll_frame)
        data_card.pack(fill="x", pady=(0, 16))
        
        data_header = self.framework.create_section_header(
            data_card,
            "Live Data Monitoring"
        )
        data_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Placeholder for data visualization
        data_placeholder = ctk.CTkLabel(
            data_card,
            text="📊 Real-time GSR, Thermal, and Video Data\n🔄 Live Charts and Displays\n📈 Performance Metrics",
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.BODY_LARGE["size"]
            ),
            text_color=BucikaColors.ON_SURFACE_VARIANT,
            height=100
        )
        data_placeholder.pack(fill="x", padx=20, pady=(0, 20))
        
    def create_status_bar(self):
        """Create bottom status bar"""
        status_frame = ctk.CTkFrame(
            self,
            height=30,
            fg_color=BucikaColors.SURFACE_VARIANT,
            corner_radius=0
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Ready • All systems operational",
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.LABEL_SMALL["size"]
            ),
            text_color=BucikaColors.ON_SURFACE_VARIANT
        )
        status_label.pack(side="left", padx=16, pady=6)
        
        # Connection status
        connection_label = ctk.CTkLabel(
            status_frame,
            text="🟢 Android App Connected",
            font=ctk.CTkFont(
                family=BucikaTypography.FONT_FAMILY,
                size=BucikaTypography.LABEL_SMALL["size"]
            ),
            text_color=BucikaColors.ON_SURFACE_VARIANT
        )
        connection_label.pack(side="right", padx=16, pady=6)
        
    def start_recording(self):
        """Handle start recording action"""
        print("Starting recording session...")
        
    def stop_recording(self):
        """Handle stop recording action"""
        print("Stopping recording session...")
        
    def run_calibration(self):
        """Handle calibration action"""
        print("Running calibration sequence...")

# Example usage
if __name__ == "__main__":
    app = BucikaMainWindow()
    app.mainloop()
```

## 🎨 Iconography Consistency

### Shared Icon Set

```python
# shared_icons.py
"""
Shared iconography definitions for cross-platform consistency
"""

class BucikaIcons:
    """
    Icon mappings for consistent iconography across platforms
    Uses Material Design Icons where possible
    """
    
    # Navigation Icons
    RECORDING = "record_voice_over"
    MONITORING = "monitor_heart" 
    FILES = "folder"
    SETTINGS = "settings"
    ADVANCED = "build"
    
    # Device Icons
    SHIMMER_GSR = "sensors"
    THERMAL_CAMERA = "camera_alt"
    PC_CONNECTION = "computer"
    USB_DEVICE = "usb"
    
    # Action Icons
    PLAY = "play_arrow"
    STOP = "stop"
    PAUSE = "pause"
    RECORD = "fiber_manual_record"
    CALIBRATE = "tune"
    
    # Status Icons
    CONNECTED = "check_circle"
    DISCONNECTED = "cancel"
    WARNING = "warning"
    INFO = "info"
    ERROR = "error"
    
    # File Operations
    EXPORT = "file_download"
    IMPORT = "file_upload"
    SHARE = "share"
    DELETE = "delete"
    
    @classmethod
    def get_android_resource(cls, icon_name: str) -> str:
        """Get Android drawable resource name"""
        return f"@drawable/ic_{icon_name}_24"
        
    @classmethod
    def get_unicode_char(cls, icon_name: str) -> str:
        """Get Unicode character for text-based icons"""
        unicode_map = {
            "play_arrow": "▶️",
            "stop": "⏹️", 
            "pause": "⏸️",
            "record": "🔴",
            "sensors": "📡",
            "camera_alt": "📷",
            "computer": "💻",
            "folder": "📁",
            "settings": "⚙️",
            "check_circle": "✅",
            "cancel": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "error": "❌"
        }
        return unicode_map.get(icon_name, "•")
```

## 📱 Platform-Specific Adaptations

### Android Adaptations

```kotlin
// PlatformAdaptations.kt
/**
 * Platform-specific adaptations for Android
 * Maintains cross-platform consistency while respecting Android conventions
 */

class AndroidPlatformAdapter {
    companion object {
        /**
         * Adapt spacing for Android density
         */
        fun dpToPx(context: Context, dp: Int): Int {
            return (dp * context.resources.displayMetrics.density).toInt()
        }
        
        /**
         * Create consistent status chip for Android
         */
        fun createStatusChip(
            context: Context, 
            parent: ChipGroup, 
            text: String, 
            status: StatusType
        ): Chip {
            return Chip(context).apply {
                this.text = text
                chipBackgroundColor = ColorStateList.valueOf(
                    ContextCompat.getColor(context, getStatusColor(status))
                )
                setTextColor(ContextCompat.getColor(context, R.color.md_theme_light_onPrimary))
                chipIcon = ContextCompat.getDrawable(context, getStatusIcon(status))
                isCheckable = false
                chipCornerRadius = dpToPx(context, 16).toFloat()
                ensureMinTouchTargetSize = true
            }
        }
        
        private fun getStatusColor(status: StatusType): Int {
            return when (status) {
                StatusType.CONNECTED -> R.color.status_connected
                StatusType.DISCONNECTED -> R.color.status_disconnected
                StatusType.WARNING -> R.color.status_warning
                StatusType.INFO -> R.color.status_info
            }
        }
        
        private fun getStatusIcon(status: StatusType): Int {
            return when (status) {
                StatusType.CONNECTED -> R.drawable.ic_check_circle_24
                StatusType.DISCONNECTED -> R.drawable.ic_cancel_24
                StatusType.WARNING -> R.drawable.ic_warning_24
                StatusType.INFO -> R.drawable.ic_info_24
            }
        }
    }
}
```

### Python Platform Adaptations

```python
# platform_adaptations.py
"""
Platform-specific adaptations for Python GUI
"""

import platform
import tkinter as tk
from tkinter import ttk

class PythonPlatformAdapter:
    """
    Adapts GUI elements for different operating systems
    """
    
    @staticmethod
    def get_platform_font_family():
        """Get appropriate font family for the platform"""
        system = platform.system()
        if system == "Windows":
            return "Segoe UI"
        elif system == "Darwin":  # macOS
            return "SF Pro Display"
        else:  # Linux
            return "Ubuntu"
            
    @staticmethod
    def get_platform_scaling():
        """Get DPI scaling factor for the platform"""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            scaling = root.tk.call('tk', 'scaling')
            root.destroy()
            return scaling
        except:
            return 1.0
            
    @staticmethod
    def apply_platform_specific_styling(widget):
        """Apply platform-specific styling adjustments"""
        system = platform.system()
        
        if system == "Windows":
            # Windows-specific adjustments
            if isinstance(widget, ttk.Button):
                widget.configure(style="Windows.TButton")
        elif system == "Darwin":
            # macOS-specific adjustments
            if isinstance(widget, ttk.Button):
                widget.configure(style="macOS.TButton")
        else:
            # Linux-specific adjustments
            if isinstance(widget, ttk.Button):
                widget.configure(style="Linux.TButton")
```

## 🔄 Synchronization and Communication

### Design Token Synchronization

```python
# design_sync.py
"""
Synchronization system for design tokens across platforms
"""

import json
import yaml
from pathlib import Path

class DesignTokenSync:
    """
    Synchronizes design tokens between Android and Python implementations
    """
    
    def __init__(self, android_path: str, python_path: str):
        self.android_path = Path(android_path)
        self.python_path = Path(python_path)
        
    def export_tokens_to_json(self):
        """Export design tokens to JSON for cross-platform use"""
        tokens = {
            "colors": {
                "primary": BucikaColors.PRIMARY,
                "on_primary": BucikaColors.ON_PRIMARY,
                "primary_container": BucikaColors.PRIMARY_CONTAINER,
                "secondary": BucikaColors.SECONDARY,
                "surface": BucikaColors.SURFACE,
                "background": BucikaColors.BACKGROUND,
                "error": BucikaColors.ERROR,
                "outline": BucikaColors.OUTLINE,
            },
            "typography": {
                "font_family": BucikaTypography.FONT_FAMILY,
                "display_large": BucikaTypography.DISPLAY_LARGE,
                "headline_medium": BucikaTypography.HEADLINE_MEDIUM,
                "title_large": BucikaTypography.TITLE_LARGE,
                "body_large": BucikaTypography.BODY_LARGE,
                "label_medium": BucikaTypography.LABEL_MEDIUM,
            },
            "spacing": {
                "xs": BucikaSpacing.XS,
                "sm": BucikaSpacing.SM,
                "md": BucikaSpacing.MD,
                "lg": BucikaSpacing.LG,
                "xl": BucikaSpacing.XL,
            }
        }
        
        # Export to shared location
        with open("shared/design_tokens.json", "w") as f:
            json.dump(tokens, f, indent=2)
            
        return tokens
        
    def generate_android_resources(self, tokens: dict):
        """Generate Android XML resources from design tokens"""
        # Generate colors.xml
        colors_xml = self._generate_colors_xml(tokens["colors"])
        colors_path = self.android_path / "src/main/res/values/colors_generated.xml"
        colors_path.write_text(colors_xml)
        
        # Generate dimens.xml
        dimens_xml = self._generate_dimens_xml(tokens["spacing"])
        dimens_path = self.android_path / "src/main/res/values/dimens_generated.xml"
        dimens_path.write_text(dimens_xml)
        
    def _generate_colors_xml(self, colors: dict) -> str:
        """Generate Android colors.xml content"""
        xml_content = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        xml_content += '    <!-- Auto-generated design tokens - DO NOT EDIT MANUALLY -->\n'
        
        for name, value in colors.items():
            android_name = name.replace("_", "_theme_light_")
            xml_content += f'    <color name="md_{android_name}">{value}</color>\n'
            
        xml_content += '</resources>\n'
        return xml_content
        
    def _generate_dimens_xml(self, spacing: dict) -> str:
        """Generate Android dimens.xml content"""
        xml_content = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        xml_content += '    <!-- Auto-generated design tokens - DO NOT EDIT MANUALLY -->\n'
        
        for name, value in spacing.items():
            xml_content += f'    <dimen name="spacing_{name}">{value}dp</dimen>\n'
            
        xml_content += '</resources>\n'
        return xml_content

# Build script integration
if __name__ == "__main__":
    sync = DesignTokenSync("AndroidApp", "PythonApp/src")
    tokens = sync.export_tokens_to_json()
    sync.generate_android_resources(tokens)
    print("Design tokens synchronized successfully!")
```

## 📋 Implementation Checklist

### Cross-Platform Consistency Goals

- [ ] **Unified Color Palette**: Same colors across Android and Python
- [ ] **Consistent Typography**: Matching font families and scales
- [ ] **Shared Iconography**: Same icons with platform-appropriate formats
- [ ] **Consistent Spacing**: Uniform spacing system across platforms
- [ ] **Synchronized Components**: Similar-looking UI components
- [ ] **Platform Adaptations**: Respect platform conventions while maintaining consistency

### Implementation Tasks

1. **Design Token System** (Week 1)
   - [ ] Create shared design tokens module
   - [ ] Implement Android resource generation
   - [ ] Set up Python GUI framework
   - [ ] Create synchronization scripts

2. **Component Alignment** (Week 2)
   - [ ] Implement Material Design 3 components in Python
   - [ ] Update Android components to match
   - [ ] Create shared icon mapping system
   - [ ] Align spacing and typography

3. **Platform Testing** (Week 3)
   - [ ] Test on Windows, macOS, Linux
   - [ ] Test on different Android screen sizes
   - [ ] Validate accessibility across platforms
   - [ ] Performance testing

4. **Documentation** (Week 4)
   - [ ] Create design system documentation
   - [ ] Developer guidelines for consistency
   - [ ] Component usage examples
   - [ ] Maintenance procedures

This cross-platform design guide ensures that users have a consistent experience whether they're using the Android app or the Python PC interface, while still respecting the unique characteristics and conventions of each platform.