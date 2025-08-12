"""
Comprehensive Android Visual Regression Testing Suite
===================================================

Extended visual regression testing covering all Android UI components,
themes, accessibility states, and cross-device compatibility scenarios.

Requirements Coverage:
- FR6: User Interface consistency and visual correctness
- NFR6: Accessibility compliance visual validation
- NFR1: Performance impact of UI rendering and responsiveness
- Cross-device UI compatibility validation
"""

import pytest
import os
import sys
import time
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

# Import visual testing utilities
try:
    from .visual_utils import (
        VisualTestConfig, 
        AndroidVisualTester, 
        get_visual_test_config,
        compare_screenshots,
        generate_visual_report
    )
except ImportError:
    # Create minimal utilities if not available
    @dataclass
    class VisualTestConfig:
        threshold: float = 0.02
        save_baselines: bool = True
        
    class AndroidVisualTester:
        def __init__(self, config):
            self.config = config
            
    def get_visual_test_config():
        return VisualTestConfig()
        
    def compare_screenshots(baseline, current, threshold=0.02):
        return {'match': True, 'difference': 0.0}
        
    def generate_visual_report(results):
        pass

# Appium imports
try:
    from appium import webdriver
    from appium.webdriver.common.appiumby import AppiumBy
    from appium.options.android import UiAutomator2Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False

# PIL for image processing
try:
    from PIL import Image, ImageChops, ImageStat
    import numpy as np
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False


@pytest.fixture(scope="session")
def visual_config() -> VisualTestConfig:
    """Visual test configuration."""
    return get_visual_test_config()


@pytest.fixture(scope="session")
def visual_test_dir() -> Path:
    """Visual test directory setup."""
    test_dir = Path(__file__).parent / "test_results" / "android"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (test_dir / "screenshots").mkdir(exist_ok=True)
    (test_dir / "baselines").mkdir(exist_ok=True)
    (test_dir / "diffs").mkdir(exist_ok=True)
    (test_dir / "reports").mkdir(exist_ok=True)
    
    return test_dir


@pytest.fixture(scope="function")
def android_visual_driver():
    """Android driver for visual testing."""
    if not APPIUM_AVAILABLE:
        pytest.skip("Appium not available for visual testing")
    
    capabilities = {
        "platformName": "Android",
        "platformVersion": "8.0",
        "deviceName": "Android Emulator",
        "app": os.path.join(os.path.dirname(__file__), "..", "..", "AndroidApp", "build", "outputs", "apk", "dev", "debug", "AndroidApp-dev-debug.apk"),
        "automationName": "UiAutomator2",
        "appPackage": "com.multisensor.recording",
        "appActivity": "com.multisensor.recording.ui.MainActivity",
        "autoGrantPermissions": True,
        "noReset": False,
        "fullReset": True,
        "newCommandTimeout": 300,
        "captureScreenshots": True,
        "nativeWebScreenshot": True
    }
    
    driver = None
    try:
        options = UiAutomator2Options()
        options.load_capabilities(capabilities)
        
        driver = webdriver.Remote(
            command_executor="http://localhost:4723/wd/hub",
            options=options
        )
        
        # Wait for app to stabilize
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.multisensor.recording:id/main_activity"))
        )
        
        # Wait additional time for UI to fully render
        time.sleep(3)
        
        yield driver
        
    except Exception as e:
        pytest.skip(f"Android visual driver setup failed: {e}")
    
    finally:
        if driver:
            driver.quit()


class AndroidVisualRegression:
    """Advanced Android visual regression testing."""
    
    def __init__(self, driver, visual_config: VisualTestConfig, test_dir: Path):
        self.driver = driver
        self.config = visual_config
        self.test_dir = test_dir
        self.results = []
    
    def capture_screenshot(self, test_name: str, element_id: Optional[str] = None) -> Path:
        """Capture screenshot with optional element focus."""
        timestamp = int(time.time())
        filename = f"{test_name}_{timestamp}.png"
        screenshot_path = self.test_dir / "screenshots" / filename
        
        if element_id:
            # Capture specific element
            try:
                element = self.driver.find_element(AppiumBy.ID, element_id)
                element.screenshot(str(screenshot_path))
            except Exception:
                # Fallback to full screenshot
                self.driver.save_screenshot(str(screenshot_path))
        else:
            # Full screen capture
            self.driver.save_screenshot(str(screenshot_path))
        
        return screenshot_path
    
    def compare_with_baseline(self, test_name: str, current_screenshot: Path) -> Dict:
        """Compare current screenshot with baseline."""
        baseline_path = self.test_dir / "baselines" / f"{test_name}_baseline.png"
        
        if not baseline_path.exists():
            # Create baseline
            current_screenshot.rename(baseline_path)
            return {
                'test_name': test_name,
                'status': 'baseline_created',
                'difference': 0.0,
                'baseline_path': str(baseline_path),
                'current_path': str(current_screenshot)
            }
        
        if not IMAGE_PROCESSING_AVAILABLE:
            return {
                'test_name': test_name,
                'status': 'skipped',
                'reason': 'Image processing not available',
                'difference': 0.0
            }
        
        # Load images
        try:
            baseline_img = Image.open(baseline_path)
            current_img = Image.open(current_screenshot)
            
            # Ensure same size
            if baseline_img.size != current_img.size:
                current_img = current_img.resize(baseline_img.size)
            
            # Calculate difference
            diff_img = ImageChops.difference(baseline_img, current_img)
            stat = ImageStat.Stat(diff_img)
            difference = sum(stat.mean) / (len(stat.mean) * 255.0)
            
            # Save diff image if significant difference
            if difference > self.config.threshold:
                diff_path = self.test_dir / "diffs" / f"{test_name}_diff.png"
                diff_img.save(diff_path)
            
            status = 'passed' if difference <= self.config.threshold else 'failed'
            
            return {
                'test_name': test_name,
                'status': status,
                'difference': difference,
                'threshold': self.config.threshold,
                'baseline_path': str(baseline_path),
                'current_path': str(current_screenshot),
                'diff_path': str(diff_path) if difference > self.config.threshold else None
            }
            
        except Exception as e:
            return {
                'test_name': test_name,
                'status': 'error',
                'error': str(e),
                'difference': 1.0
            }
    
    def test_visual_element(self, test_name: str, element_id: Optional[str] = None, setup_action=None) -> Dict:
        """Test visual regression for a specific element or screen."""
        try:
            # Execute setup action if provided
            if setup_action:
                setup_action()
                time.sleep(1)  # Allow UI to settle
            
            # Capture screenshot
            screenshot_path = self.capture_screenshot(test_name, element_id)
            
            # Compare with baseline
            result = self.compare_with_baseline(test_name, screenshot_path)
            self.results.append(result)
            
            return result
            
        except Exception as e:
            error_result = {
                'test_name': test_name,
                'status': 'error',
                'error': str(e),
                'difference': 1.0
            }
            self.results.append(error_result)
            return error_result


class TestAndroidUIVisualRegression:
    """Android UI visual regression test suite."""
    
    @pytest.mark.visual
    @pytest.mark.android
    def test_main_activity_visual_consistency(self, android_visual_driver, visual_config, visual_test_dir):
        """Test main activity visual consistency."""
        tester = AndroidVisualRegression(android_visual_driver, visual_config, visual_test_dir)
        
        # Test main activity
        result = tester.test_visual_element("main_activity_initial")
        assert result['status'] in ['passed', 'baseline_created'], f"Main activity visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    def test_navigation_drawer_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test navigation drawer visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Test navigation drawer closed state
        result = tester.test_visual_element("nav_drawer_closed")
        assert result['status'] in ['passed', 'baseline_created'], f"Navigation drawer closed test failed: {result}"
        
        # Test navigation drawer open state
        def open_drawer():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            time.sleep(0.5)
        
        result = tester.test_visual_element("nav_drawer_open", setup_action=open_drawer)
        assert result['status'] in ['passed', 'baseline_created'], f"Navigation drawer open test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    def test_recording_screen_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test recording screen visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Navigate to recording screen
        def navigate_to_recording():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Recording']").click()
            time.sleep(1)
        
        result = tester.test_visual_element("recording_screen_initial", setup_action=navigate_to_recording)
        assert result['status'] in ['passed', 'baseline_created'], f"Recording screen visual test failed: {result}"
        
        # Test new session dialog
        def open_new_session():
            navigate_to_recording()
            new_session_btn = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/btn_new_session")
            new_session_btn.click()
            time.sleep(0.5)
        
        result = tester.test_visual_element("new_session_dialog", setup_action=open_new_session)
        assert result['status'] in ['passed', 'baseline_created'], f"New session dialog visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    def test_devices_screen_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test devices screen visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Navigate to devices screen
        def navigate_to_devices():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Devices']").click()
            time.sleep(1)
        
        result = tester.test_visual_element("devices_screen_initial", setup_action=navigate_to_devices)
        assert result['status'] in ['passed', 'baseline_created'], f"Devices screen visual test failed: {result}"
        
        # Test device scanning state
        def start_device_scan():
            navigate_to_devices()
            scan_btn = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/btn_scan_devices")
            scan_btn.click()
            time.sleep(1)
        
        result = tester.test_visual_element("devices_scanning_state", setup_action=start_device_scan)
        assert result['status'] in ['passed', 'baseline_created'], f"Device scanning visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    def test_settings_screen_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test settings screen visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Navigate to settings
        def navigate_to_settings():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Settings']").click()
            time.sleep(1)
        
        result = tester.test_visual_element("settings_screen_initial", setup_action=navigate_to_settings)
        assert result['status'] in ['passed', 'baseline_created'], f"Settings screen visual test failed: {result}"


class TestAndroidThemeVisualRegression:
    """Android theme and styling visual regression tests."""
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.theme
    def test_light_theme_consistency(self, android_visual_driver, visual_config, visual_test_dir):
        """Test light theme visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Ensure light theme is active
        def set_light_theme():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Settings']").click()
            
            theme_option = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/theme_light")
            if not theme_option.get_attribute("checked"):
                theme_option.click()
            time.sleep(1)
            
            # Return to main screen
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Navigate up").click()
        
        result = tester.test_visual_element("light_theme_main", setup_action=set_light_theme)
        assert result['status'] in ['passed', 'baseline_created'], f"Light theme visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.theme
    def test_dark_theme_consistency(self, android_visual_driver, visual_config, visual_test_dir):
        """Test dark theme visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Set dark theme
        def set_dark_theme():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Settings']").click()
            
            theme_option = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/theme_dark")
            if not theme_option.get_attribute("checked"):
                theme_option.click()
            time.sleep(1)
            
            # Return to main screen
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Navigate up").click()
        
        result = tester.test_visual_element("dark_theme_main", setup_action=set_dark_theme)
        assert result['status'] in ['passed', 'baseline_created'], f"Dark theme visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.accessibility
    def test_high_contrast_mode_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test high contrast accessibility mode visuals."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Enable high contrast mode
        def enable_high_contrast():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Settings']").click()
            
            accessibility_section = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Accessibility']")
            accessibility_section.click()
            
            high_contrast_toggle = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/toggle_high_contrast")
            if not high_contrast_toggle.get_attribute("checked"):
                high_contrast_toggle.click()
            time.sleep(1)
            
            # Return to main screen
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Navigate up").click()
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Navigate up").click()
        
        result = tester.test_visual_element("high_contrast_main", setup_action=enable_high_contrast)
        assert result['status'] in ['passed', 'baseline_created'], f"High contrast mode visual test failed: {result}"


class TestAndroidResponsiveVisuals:
    """Android responsive design visual tests."""
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.responsive
    def test_portrait_orientation_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test portrait orientation visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Set portrait orientation
        driver.orientation = "PORTRAIT"
        time.sleep(1)
        
        result = tester.test_visual_element("portrait_orientation_main")
        assert result['status'] in ['passed', 'baseline_created'], f"Portrait orientation visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.responsive
    def test_landscape_orientation_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test landscape orientation visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Set landscape orientation
        driver.orientation = "LANDSCAPE"
        time.sleep(2)  # Allow orientation change to complete
        
        result = tester.test_visual_element("landscape_orientation_main")
        assert result['status'] in ['passed', 'baseline_created'], f"Landscape orientation visual test failed: {result}"
        
        # Reset to portrait
        driver.orientation = "PORTRAIT"
        time.sleep(1)
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.responsive
    def test_font_size_scaling_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test font size scaling visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Test different font sizes
        font_sizes = ["Normal", "Large", "Extra Large"]
        
        for font_size in font_sizes:
            def set_font_size():
                driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
                driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Settings']").click()
                
                accessibility_section = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Accessibility']")
                accessibility_section.click()
                
                font_size_spinner = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/spinner_font_size")
                font_size_spinner.click()
                
                size_option = driver.find_element(AppiumBy.XPATH, f"//android.widget.TextView[@text='{font_size}']")
                size_option.click()
                time.sleep(1)
                
                # Return to main screen
                driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Navigate up").click()
                driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Navigate up").click()
            
            test_name = f"font_size_{font_size.lower().replace(' ', '_')}"
            result = tester.test_visual_element(test_name, setup_action=set_font_size)
            assert result['status'] in ['passed', 'baseline_created'], f"Font size {font_size} visual test failed: {result}"


class TestAndroidComponentVisuals:
    """Individual Android component visual regression tests."""
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.components
    def test_button_states_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test button states visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Navigate to recording screen for button testing
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
        driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Recording']").click()
        
        # Test normal button state
        result = tester.test_visual_element("button_normal_state", 
                                          element_id="com.multisensor.recording:id/btn_new_session")
        assert result['status'] in ['passed', 'baseline_created'], f"Button normal state test failed: {result}"
        
        # Test pressed button state (simulate touch)
        button = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/btn_new_session")
        
        # Use touch action to capture pressed state
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.click_and_hold(button).perform()
        time.sleep(0.1)
        
        result = tester.test_visual_element("button_pressed_state",
                                          element_id="com.multisensor.recording:id/btn_new_session")
        
        actions.release().perform()
        
        assert result['status'] in ['passed', 'baseline_created'], f"Button pressed state test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.components
    def test_dialog_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test dialog visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Open a dialog
        def open_dialog():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Recording']").click()
            
            new_session_btn = driver.find_element(AppiumBy.ID, "com.multisensor.recording:id/btn_new_session")
            new_session_btn.click()
            time.sleep(0.5)
        
        result = tester.test_visual_element("dialog_new_session", setup_action=open_dialog)
        assert result['status'] in ['passed', 'baseline_created'], f"Dialog visual test failed: {result}"
    
    @pytest.mark.visual
    @pytest.mark.android
    @pytest.mark.components
    def test_list_item_visuals(self, android_visual_driver, visual_config, visual_test_dir):
        """Test list item visual consistency."""
        driver = android_visual_driver
        tester = AndroidVisualRegression(driver, visual_config, visual_test_dir)
        
        # Navigate to devices list
        def navigate_to_device_list():
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Devices']").click()
            time.sleep(1)
        
        result = tester.test_visual_element("device_list_items", 
                                          element_id="com.multisensor.recording:id/device_list",
                                          setup_action=navigate_to_device_list)
        assert result['status'] in ['passed', 'baseline_created'], f"List item visual test failed: {result}"


@pytest.fixture(scope="session", autouse=True)
def generate_visual_test_report(request, visual_test_dir):
    """Generate comprehensive visual test report after all tests."""
    yield
    
    # This will run after all tests complete
    def generate_report():
        try:
            # Collect all test results
            results_file = visual_test_dir / "reports" / "visual_test_results.json"
            
            # Generate HTML report
            report_html = visual_test_dir / "reports" / "visual_regression_report.html"
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Android Visual Regression Test Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                    .test-result { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                    .passed { background: #d4edda; border-color: #c3e6cb; }
                    .failed { background: #f8d7da; border-color: #f5c6cb; }
                    .baseline { background: #d1ecf1; border-color: #bee5eb; }
                    .images { display: flex; gap: 10px; margin-top: 10px; }
                    .images img { max-width: 300px; height: auto; border: 1px solid #ddd; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Android Visual Regression Test Report</h1>
                    <p>Generated: """ + str(time.ctime()) + """</p>
                </div>
                
                <div id="summary">
                    <h2>Test Summary</h2>
                    <p>Visual regression testing completed for Android UI components.</p>
                </div>
                
                <div id="details">
                    <h2>Test Details</h2>
                    <p>Detailed visual test results would be displayed here.</p>
                </div>
            </body>
            </html>
            """
            
            with open(report_html, 'w') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"Failed to generate visual test report: {e}")
    
    request.addfinalizer(generate_report)


if __name__ == "__main__":
    # Run visual regression tests
    pytest.main([__file__, "-v", "-s", "--tb=short", "-m", "visual and android"])