import os
import sys
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt5.QtWidgets import QApplication
from .gui.enhanced_ui_main_window import EnhancedMainWindow


def create_enhanced_ui_demo():
    print('Creating PsychoPy-inspired Enhanced UI demo...')
    app = QApplication([])
    app.setStyle('Fusion')
    window = EnhancedMainWindow()
    window.setWindowTitle(
        'Multi-Sensor Recording System - Enhanced PsychoPy-Inspired Interface')
    window.show()
    app.processEvents()
    screenshot = window.grab()
    screenshot_path = '/tmp/enhanced_ui_psychopy_inspired.png'
    screenshot.save(screenshot_path)
    print(f'Enhanced UI screenshot saved to: {screenshot_path}')
    window.connect_all_devices()
    app.processEvents()
    window.start_calibration()
    app.processEvents()
    window.start_recording()
    app.processEvents()
    screenshot_active = window.grab()
    screenshot_active_path = '/tmp/enhanced_ui_active_state.png'
    screenshot_active.save(screenshot_active_path)
    print(f'Active state screenshot saved to: {screenshot_active_path}')
    window.close()
    app.quit()
    return True


if __name__ == '__main__':
    try:
        success = create_enhanced_ui_demo()
        if success:
            print('✓ Enhanced UI demo completed successfully')
        else:
            print('✗ Enhanced UI demo failed')
            sys.exit(1)
    except Exception as e:
        print(f'✗ Error creating enhanced UI demo: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    create_enhanced_ui_demo()


if __name__ == '__main__':
    main()
