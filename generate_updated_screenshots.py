#!/usr/bin/env python3
"""
Generate updated UI screenshots with camera preview tab
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set offscreen rendering
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    # Import Qt components
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication  
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QPixmap
        PYQT_VERSION = 5
    except ImportError:
        print("PyQt not available - creating mock screenshots")
        exit(0)

def main():
    app = QApplication([])
    
    try:
        from PythonApp.gui.main_window import MainWindow
        
        # Create main window
        window = MainWindow()
        window.resize(1200, 800)
        
        # Force show to render all components
        window.show()
        app.processEvents()
        
        print("Generating updated screenshots with camera preview...")
        
        # Generate main window screenshot
        pixmap = window.grab()
        pixmap.save("ui_main_window.png")
        print("✅ Generated: ui_main_window.png")
        
        # Generate individual tab screenshots
        tab_widget = None
        for child in window.findChildren(type(window.findChild(type(None)))):
            if hasattr(child, 'count') and child.count() > 0:
                tab_widget = child
                break
        
        if tab_widget:
            tab_names = [
                "recording", "devices", "sensors", "sync", 
                "calibration", "camera_preview", "security", "settings"
            ]
            
            for i in range(tab_widget.count()):
                # Select tab
                tab_widget.setCurrentIndex(i)
                app.processEvents()
                
                # Get tab name (use index if can't determine name)
                tab_name = tab_names[i] if i < len(tab_names) else f"tab_{i}"
                
                # Screenshot the current tab content
                current_widget = tab_widget.currentWidget()
                if current_widget:
                    tab_pixmap = current_widget.grab()
                    filename = f"ui_tab_{i:02d}_{tab_name}.png"
                    tab_pixmap.save(filename)
                    print(f"✅ Generated: {filename}")
        
        print(f"\n🎉 Successfully generated screenshots with camera preview tab!")
        print("The new 'Camera Preview' tab is now available in the interface.")
        
    except Exception as e:
        print(f"Error generating screenshots: {e}")
        import traceback
        traceback.print_exc()
    
    app.quit()

if __name__ == "__main__":
    main()