"""
Visual Regression Testing Utilities
===================================

Provides utilities for screenshot comparison, pixel-level analysis,
and visual regression detection across different UI components.

Features:
- Screenshot capture and comparison
- Pixel difference analysis
- Baseline management
- Visual accessibility validation
- Cross-platform screenshot normalization
"""

import os
import sys
import hashlib
import json
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont, ImageChops
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None
    ImageFont = None
    ImageChops = None
    np = None

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None


class VisualTestConfig:
    """Configuration for visual regression testing."""
    
    def __init__(self):
        self.baseline_dir = Path(__file__).parent / "baselines"
        self.output_dir = Path(__file__).parent / "test_results"
        self.threshold = 0.01  # 1% pixel difference threshold
        self.ignore_regions = []  # Regions to ignore in comparison
        self.platform_specific = True  # Different baselines per platform
        
        # Ensure directories exist
        self.baseline_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)


class ScreenshotComparator:
    """Handles screenshot comparison and analysis."""
    
    def __init__(self, config: VisualTestConfig):
        self.config = config
        
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow required for visual testing. Install with: pip install Pillow")
    
    def capture_screenshot(self, target: Union[str, object], name: str) -> Path:
        """Capture screenshot from various sources."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.config.output_dir / filename
        
        if isinstance(target, str) and target.startswith("http"):
            # Web screenshot using Playwright
            return self._capture_web_screenshot(target, filepath)
        elif hasattr(target, 'grab'):  # PyQt widget
            return self._capture_pyqt_screenshot(target, filepath)
        elif isinstance(target, str) and target.endswith(".png"):
            # Copy existing screenshot
            import shutil
            shutil.copy2(target, filepath)
            return filepath
        else:
            raise ValueError(f"Unsupported screenshot target: {type(target)}")
    
    def _capture_web_screenshot(self, url: str, filepath: Path) -> Path:
        """Capture screenshot from web URL using Playwright."""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                page.screenshot(path=str(filepath))
                browser.close()
                
            return filepath
        except ImportError:
            raise ImportError("Playwright required for web screenshots. Install with: pip install playwright")
    
    def _capture_pyqt_screenshot(self, widget, filepath: Path) -> Path:
        """Capture screenshot from PyQt widget."""
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtGui import QPixmap
            
            # Ensure widget is visible
            widget.show()
            QApplication.processEvents()
            
            # Capture screenshot
            pixmap = widget.grab()
            pixmap.save(str(filepath), "PNG")
            
            return filepath
        except ImportError:
            raise ImportError("PyQt5 required for widget screenshots")
    
    def compare_screenshots(self, baseline_path: Path, current_path: Path, name: str) -> Dict:
        """Compare two screenshots and return analysis results."""
        if not baseline_path.exists():
            # First run - save as baseline
            import shutil
            shutil.copy2(current_path, baseline_path)
            return {
                "status": "baseline_created",
                "difference_percent": 0.0,
                "baseline_path": str(baseline_path),
                "current_path": str(current_path),
                "diff_path": None
            }
        
        # Load images
        baseline_img = Image.open(baseline_path)
        current_img = Image.open(current_path)
        
        # Normalize images (resize if needed)
        baseline_img, current_img = self._normalize_images(baseline_img, current_img)
        
        # Calculate difference
        diff_img = ImageChops.difference(baseline_img, current_img)
        
        # Calculate percentage difference
        diff_array = np.array(diff_img)
        total_pixels = diff_array.size
        diff_pixels = np.count_nonzero(diff_array)
        diff_percent = (diff_pixels / total_pixels) * 100
        
        # Save difference image
        diff_path = self.config.output_dir / f"{name}_diff.png"
        diff_img.save(diff_path)
        
        # Determine test result
        status = "passed" if diff_percent <= (self.config.threshold * 100) else "failed"
        
        return {
            "status": status,
            "difference_percent": diff_percent,
            "threshold_percent": self.config.threshold * 100,
            "baseline_path": str(baseline_path),
            "current_path": str(current_path),
            "diff_path": str(diff_path),
            "total_pixels": total_pixels,
            "different_pixels": diff_pixels
        }
    
    def _normalize_images(self, img1: Image.Image, img2: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """Normalize two images to same size and format."""
        # Get target size (use larger dimensions)
        target_width = max(img1.width, img2.width)
        target_height = max(img1.height, img2.height)
        
        # Resize if needed
        if img1.size != (target_width, target_height):
            img1 = img1.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        if img2.size != (target_width, target_height):
            img2 = img2.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert to same mode
        if img1.mode != img2.mode:
            target_mode = "RGB"
            img1 = img1.convert(target_mode)
            img2 = img2.convert(target_mode)
        
        return img1, img2
    
    def generate_visual_report(self, results: List[Dict], output_path: Path) -> None:
        """Generate HTML visual test report."""
        html_content = self._create_html_report(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_html_report(self, results: List[Dict]) -> str:
        """Create HTML report content."""
        passed_count = sum(1 for r in results if r['status'] == 'passed')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        baseline_count = sum(1 for r in results if r['status'] == 'baseline_created')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Visual Regression Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .test-case {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .passed {{ border-left: 5px solid #4CAF50; }}
        .failed {{ border-left: 5px solid #f44336; }}
        .baseline {{ border-left: 5px solid #2196F3; }}
        .images {{ display: flex; gap: 10px; margin-top: 10px; }}
        .image-container {{ flex: 1; text-align: center; }}
        .image-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
        .stats {{ display: inline-block; margin: 0 10px; }}
    </style>
</head>
<body>
    <h1>Visual Regression Test Report</h1>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <span class="stats">✅ Passed: {passed_count}</span>
        <span class="stats">❌ Failed: {failed_count}</span>
        <span class="stats">🆕 Baselines Created: {baseline_count}</span>
        <span class="stats">📊 Total: {len(results)}</span>
    </div>
    
    <div class="test-results">
"""
        
        for result in results:
            status_class = result['status']
            status_icon = {"passed": "✅", "failed": "❌", "baseline_created": "🆕"}[result['status']]
            
            html += f"""
        <div class="test-case {status_class}">
            <h3>{status_icon} {os.path.basename(result['current_path'])}</h3>
            <p><strong>Status:</strong> {result['status'].replace('_', ' ').title()}</p>
"""
            
            if result['status'] != 'baseline_created':
                html += f"""
            <p><strong>Difference:</strong> {result['difference_percent']:.2f}% (threshold: {result['threshold_percent']:.2f}%)</p>
            <p><strong>Different Pixels:</strong> {result['different_pixels']:,} of {result['total_pixels']:,}</p>
"""
            
            html += """
            <div class="images">
"""
            
            if result['baseline_path'] and os.path.exists(result['baseline_path']):
                html += f"""
                <div class="image-container">
                    <h4>Baseline</h4>
                    <img src="{os.path.relpath(result['baseline_path'], start=os.path.dirname(output_path))}" alt="Baseline">
                </div>
"""
            
            html += f"""
                <div class="image-container">
                    <h4>Current</h4>
                    <img src="{os.path.relpath(result['current_path'], start=os.path.dirname(output_path))}" alt="Current">
                </div>
"""
            
            if result['diff_path'] and os.path.exists(result['diff_path']):
                html += f"""
                <div class="image-container">
                    <h4>Difference</h4>
                    <img src="{os.path.relpath(result['diff_path'], start=os.path.dirname(output_path))}" alt="Difference">
                </div>
"""
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html


class AndroidVisualTester:
    """Visual testing for Android UI components."""
    
    def __init__(self, config: VisualTestConfig):
        self.config = config
        self.comparator = ScreenshotComparator(config)
    
    def test_fragment_screenshot(self, appium_driver, fragment_name: str) -> Dict:
        """Test visual appearance of Android fragment."""
        # Navigate to fragment
        self._navigate_to_fragment(appium_driver, fragment_name)
        
        # Capture screenshot
        screenshot_path = self._capture_android_screenshot(appium_driver, fragment_name)
        
        # Compare with baseline
        baseline_path = self.config.baseline_dir / f"android_{fragment_name}.png"
        
        return self.comparator.compare_screenshots(baseline_path, screenshot_path, f"android_{fragment_name}")
    
    def _navigate_to_fragment(self, driver, fragment_name: str):
        """Navigate to specific fragment in Android app."""
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Open navigation drawer
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click()
            
            # Click on fragment
            fragment_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, f"//android.widget.TextView[@text='{fragment_name}']"))
            )
            fragment_item.click()
            
            # Wait for fragment to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, f"com.multisensor.recording:id/{fragment_name.lower()}_fragment"))
            )
            
        except Exception as e:
            print(f"Warning: Could not navigate to fragment {fragment_name}: {e}")
    
    def _capture_android_screenshot(self, driver, name: str) -> Path:
        """Capture screenshot from Android device."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"android_{name}_{timestamp}.png"
        filepath = self.config.output_dir / filename
        
        # Use Appium screenshot capability
        driver.save_screenshot(str(filepath))
        
        return filepath


class PyQtVisualTester:
    """Visual testing for PyQt5 desktop application."""
    
    def __init__(self, config: VisualTestConfig):
        self.config = config
        self.comparator = ScreenshotComparator(config)
    
    def test_window_screenshot(self, widget, window_name: str) -> Dict:
        """Test visual appearance of PyQt window."""
        # Capture screenshot
        screenshot_path = self.comparator.capture_screenshot(widget, f"pyqt_{window_name}")
        
        # Compare with baseline
        baseline_path = self.config.baseline_dir / f"pyqt_{window_name}.png"
        
        return self.comparator.compare_screenshots(baseline_path, screenshot_path, f"pyqt_{window_name}")


class WebVisualTester:
    """Visual testing for Web dashboard components."""
    
    def __init__(self, config: VisualTestConfig):
        self.config = config
        self.comparator = ScreenshotComparator(config)
    
    def test_page_screenshot(self, url: str, page_name: str) -> Dict:
        """Test visual appearance of web page."""
        # Capture screenshot
        screenshot_path = self.comparator.capture_screenshot(url, f"web_{page_name}")
        
        # Compare with baseline
        baseline_path = self.config.baseline_dir / f"web_{page_name}.png"
        
        return self.comparator.compare_screenshots(baseline_path, screenshot_path, f"web_{page_name}")


def get_visual_test_config() -> VisualTestConfig:
    """Get default visual test configuration."""
    config = VisualTestConfig()
    
    # Adjust threshold based on environment
    if os.getenv("CI") == "true":
        config.threshold = 0.02  # More lenient in CI
    
    return config


if __name__ == "__main__":
    # Test utilities
    config = get_visual_test_config()
    comparator = ScreenshotComparator(config)
    print(f"Visual testing utilities initialized. Baseline dir: {config.baseline_dir}")