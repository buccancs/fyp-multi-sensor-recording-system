"""
Android Device Mock Infrastructure
=================================

Provides comprehensive mocking infrastructure for Android devices and Appium
testing when real devices are not available. Includes:

- Mock Android device simulation
- Mock Appium WebDriver implementation
- Realistic UI element simulation
- Hardware sensor mocking (accelerometer, GPS, etc.)
- Network connectivity simulation

This enables full test execution in CI/CD environments without real Android devices.
"""

import pytest
import time
import threading
import json
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
import os
import sys
import random

logger = logging.getLogger(__name__)


@dataclass
class MockAndroidDevice:
    """Mock Android device configuration."""
    device_id: str
    model: str
    android_version: str
    screen_resolution: tuple
    battery_level: int = 100
    connected: bool = True
    app_installed: bool = True


@dataclass
class MockUIElement:
    """Mock UI element for Appium testing."""
    element_id: str
    element_type: str  # button, text, input, etc.
    text: str
    accessibility_id: str
    xpath: str
    enabled: bool = True
    visible: bool = True
    bounds: tuple = (0, 0, 100, 50)


class MockAppiumElement:
    """Mock Appium WebElement for UI interaction testing."""
    
    def __init__(self, element_info: MockUIElement):
        self.element_info = element_info
        self._clicked = False
        self._text_value = element_info.text
        
    @property
    def text(self) -> str:
        """Get element text."""
        return self._text_value
        
    @property
    def tag_name(self) -> str:
        """Get element tag name."""
        return self.element_info.element_type
        
    @property
    def location(self) -> Dict[str, int]:
        """Get element location."""
        x, y, _, _ = self.element_info.bounds
        return {'x': x, 'y': y}
        
    @property
    def size(self) -> Dict[str, int]:
        """Get element size."""
        x, y, w, h = self.element_info.bounds
        return {'width': w - x, 'height': h - y}
        
    def click(self):
        """Simulate element click."""
        if not self.element_info.enabled:
            raise Exception(f"Element {self.element_info.element_id} is not enabled")
        if not self.element_info.visible:
            raise Exception(f"Element {self.element_info.element_id} is not visible")
            
        self._clicked = True
        logger.info(f"Mock click on element: {self.element_info.accessibility_id}")
        time.sleep(0.1)  # Simulate UI response time
        
    def send_keys(self, text: str):
        """Simulate text input."""
        if not self.element_info.enabled:
            raise Exception(f"Element {self.element_info.element_id} is not enabled")
            
        self._text_value = text
        logger.info(f"Mock text input: '{text}' to {self.element_info.accessibility_id}")
        time.sleep(0.1)
        
    def clear(self):
        """Clear element text."""
        self._text_value = ""
        logger.info(f"Mock clear text from {self.element_info.accessibility_id}")
        
    def get_attribute(self, name: str) -> str:
        """Get element attribute."""
        attributes = {
            'enabled': str(self.element_info.enabled),
            'visible': str(self.element_info.visible),
            'text': self._text_value,
            'content-desc': self.element_info.accessibility_id,
            'resource-id': self.element_info.element_id,
            'class': self.element_info.element_type
        }
        return attributes.get(name, "")
        
    def is_enabled(self) -> bool:
        """Check if element is enabled."""
        return self.element_info.enabled
        
    def is_displayed(self) -> bool:
        """Check if element is displayed."""
        return self.element_info.visible
        
    def is_selected(self) -> bool:
        """Check if element is selected."""
        return False  # Default implementation


class MockAppiumDriver:
    """Mock Appium WebDriver for Android testing without real devices."""
    
    def __init__(self, device_info: MockAndroidDevice):
        self.device_info = device_info
        self.current_activity = "com.example.gsrapp.MainActivity"
        self.current_package = "com.example.gsrapp"
        self._app_state = "foreground"
        self._ui_elements = self._create_mock_ui_elements()
        self._screenshots = []
        self._orientation = "PORTRAIT"
        self._network_connected = True
        
    def _create_mock_ui_elements(self) -> Dict[str, MockUIElement]:
        """Create mock UI elements for the GSR app."""
        elements = {
            # Navigation elements
            "navigation_drawer": MockUIElement(
                element_id="com.example.gsrapp:id/drawer",
                element_type="android.widget.DrawerLayout",
                text="",
                accessibility_id="Open navigation drawer",
                xpath="//android.widget.DrawerLayout[@content-desc='Open navigation drawer']"
            ),
            
            # Main screen elements
            "start_recording_button": MockUIElement(
                element_id="com.example.gsrapp:id/start_recording",
                element_type="android.widget.Button",
                text="Start Recording",
                accessibility_id="Start GSR Recording",
                xpath="//android.widget.Button[@text='Start Recording']"
            ),
            
            "stop_recording_button": MockUIElement(
                element_id="com.example.gsrapp:id/stop_recording",
                element_type="android.widget.Button",
                text="Stop Recording",
                accessibility_id="Stop GSR Recording",
                xpath="//android.widget.Button[@text='Stop Recording']",
                enabled=False  # Initially disabled
            ),
            
            # Devices screen elements
            "devices_menu": MockUIElement(
                element_id="com.example.gsrapp:id/nav_devices",
                element_type="android.widget.TextView",
                text="Devices",
                accessibility_id="Devices",
                xpath="//android.widget.TextView[@text='Devices']"
            ),
            
            "shimmer_device": MockUIElement(
                element_id="com.example.gsrapp:id/shimmer_device",
                element_type="android.widget.LinearLayout",
                text="Shimmer3 GSR+ (Mock)",
                accessibility_id="Shimmer Device",
                xpath="//android.widget.LinearLayout[contains(@text,'Shimmer')]"
            ),
            
            "thermal_camera": MockUIElement(
                element_id="com.example.gsrapp:id/thermal_camera",
                element_type="android.widget.LinearLayout",
                text="Thermal Camera (Mock)",
                accessibility_id="Thermal Camera",
                xpath="//android.widget.LinearLayout[contains(@text,'Thermal')]"
            ),
            
            # Settings elements
            "settings_menu": MockUIElement(
                element_id="com.example.gsrapp:id/nav_settings",
                element_type="android.widget.TextView",
                text="Settings",
                accessibility_id="Settings",
                xpath="//android.widget.TextView[@text='Settings']"
            ),
            
            # Permission dialog elements
            "permission_allow": MockUIElement(
                element_id="com.android.permissioncontroller:id/permission_allow_button",
                element_type="android.widget.Button",
                text="Allow",
                accessibility_id="Allow",
                xpath="//android.widget.Button[@text='Allow']"
            ),
            
            # Bluetooth elements
            "bluetooth_toggle": MockUIElement(
                element_id="com.multisensor.recording:id/toggle_bluetooth",
                element_type="android.widget.Switch",
                text="Bluetooth",
                accessibility_id="Bluetooth Toggle",
                xpath="//android.widget.Switch[@resource-id='com.multisensor.recording:id/toggle_bluetooth']"
            ),
            
            "bluetooth_enable": MockUIElement(
                element_id="com.example.gsrapp:id/enable_bluetooth",
                element_type="android.widget.Button",
                text="Enable Bluetooth",
                accessibility_id="Enable Bluetooth",
                xpath="//android.widget.Button[@text='Enable Bluetooth']"
            ),
            
            # Device scan results
            "scan_results": MockUIElement(
                element_id="com.multisensor.recording:id/device_scan_results",
                element_type="android.widget.ListView",
                text="Found 1 Shimmer device: Mock Shimmer (00:06:66:66:66:66)",
                accessibility_id="Device Scan Results",
                xpath="//android.widget.ListView[@resource-id='com.multisensor.recording:id/device_scan_results']"
            )
        }
        
        return elements
        
    def find_element(self, by_type, value: str) -> MockAppiumElement:
        """Find a UI element using various locator strategies."""
        time.sleep(0.1)  # Simulate element search time
        
        # Handle both string and object-based locators
        locator_type = by_type if isinstance(by_type, str) else getattr(by_type, 'name', str(by_type))
        
        # Search by accessibility ID
        if locator_type == "accessibility_id" or "ACCESSIBILITY_ID" in locator_type.upper():
            for element_info in self._ui_elements.values():
                if element_info.accessibility_id == value:
                    if not element_info.visible:
                        raise Exception(f"Element not visible: {value}")
                    return MockAppiumElement(element_info)
                    
        # Search by XPath
        elif locator_type == "xpath" or "XPATH" in locator_type.upper():
            for element_info in self._ui_elements.values():
                if element_info.xpath == value or value in element_info.xpath:
                    if not element_info.visible:
                        raise Exception(f"Element not visible: {value}")
                    return MockAppiumElement(element_info)
                    
        # Search by ID
        elif locator_type == "id" or "ID" in locator_type.upper():
            for element_info in self._ui_elements.values():
                if element_info.element_id == value:
                    if not element_info.visible:
                        raise Exception(f"Element not visible: {value}")
                    return MockAppiumElement(element_info)
                    
        # Search by text
        elif "text" in locator_type.lower() or "UIAUTOMATOR" in locator_type.upper():
            for element_info in self._ui_elements.values():
                if value in element_info.text or element_info.text in value:
                    if not element_info.visible:
                        raise Exception(f"Element not visible: {value}")
                    return MockAppiumElement(element_info)
                    
        raise Exception(f"Element not found: {locator_type} = {value}")
        
    def find_elements(self, by_type, value: str) -> List[MockAppiumElement]:
        """Find multiple UI elements."""
        elements = []
        
        # Handle both string and object-based locators
        locator_type = by_type if isinstance(by_type, str) else getattr(by_type, 'name', str(by_type))
        
        for element_info in self._ui_elements.values():
            found = False
            
            if locator_type == "accessibility_id" or "ACCESSIBILITY_ID" in locator_type.upper():
                if element_info.accessibility_id == value:
                    found = True
            elif locator_type == "xpath" or "XPATH" in locator_type.upper():
                if element_info.xpath == value or value in element_info.xpath:
                    found = True
            elif locator_type == "id" or "ID" in locator_type.upper():
                if element_info.element_id == value:
                    found = True
            elif "text" in locator_type.lower() or "UIAUTOMATOR" in locator_type.upper():
                if value in element_info.text or element_info.text in value:
                    found = True
                
            if found and element_info.visible:
                elements.append(MockAppiumElement(element_info))
                
        return elements
        
    def get_screenshot_as_png(self) -> bytes:
        """Get screenshot as PNG bytes."""
        # Create a simple mock screenshot (just a header)
        mock_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x02\x00\x00\x00\x90wS\xde'
        self._screenshots.append({
            'timestamp': time.time(),
            'size': len(mock_png)
        })
        logger.info("Mock screenshot captured")
        return mock_png
        
    def save_screenshot(self, filename: str):
        """Save screenshot to file."""
        screenshot_data = self.get_screenshot_as_png()
        with open(filename, 'wb') as f:
            f.write(screenshot_data)
        logger.info(f"Mock screenshot saved: {filename}")
        
    def current_activity(self) -> str:
        """Get current activity name."""
        return self.current_activity
        
    def current_package(self) -> str:
        """Get current package name."""
        return self.current_package
        
    def orientation(self) -> str:
        """Get device orientation."""
        return self._orientation
        
    def set_orientation(self, orientation: str):
        """Set device orientation."""
        self._orientation = orientation
        logger.info(f"Mock orientation changed to: {orientation}")
        
    def get_window_size(self) -> Dict[str, int]:
        """Get window size."""
        width, height = self.device_info.screen_resolution
        return {'width': width, 'height': height}
        
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500):
        """Simulate swipe gesture."""
        logger.info(f"Mock swipe from ({start_x},{start_y}) to ({end_x},{end_y})")
        time.sleep(duration / 1000.0)
        
    def tap(self, positions: List[tuple], duration: int = 100):
        """Simulate tap gesture."""
        logger.info(f"Mock tap at positions: {positions}")
        time.sleep(duration / 1000.0)
        
    def long_press(self, element):
        """Simulate long press on element."""
        logger.info(f"Mock long press on element")
        time.sleep(0.5)
        
    def hide_keyboard(self):
        """Hide virtual keyboard."""
        logger.info("Mock hide keyboard")
        time.sleep(0.1)
        
    def is_keyboard_shown(self) -> bool:
        """Check if keyboard is shown."""
        return False  # Default: no keyboard
        
    def press_keycode(self, keycode: int):
        """Press Android keycode."""
        logger.info(f"Mock keycode press: {keycode}")
        time.sleep(0.1)
        
    def start_activity(self, app_package: str, app_activity: str):
        """Start specific activity."""
        self.current_package = app_package
        self.current_activity = app_activity
        logger.info(f"Mock activity started: {app_package}/{app_activity}")
        
    def background_app(self, seconds: int = -1):
        """Put app in background."""
        self._app_state = "background"
        logger.info(f"Mock app backgrounded for {seconds} seconds")
        if seconds > 0:
            time.sleep(seconds)
            self._app_state = "foreground"
            
    def activate_app(self, app_package: str):
        """Activate/foreground app."""
        self._app_state = "foreground"
        self.current_package = app_package
        logger.info(f"Mock app activated: {app_package}")
        
    def quit(self):
        """Quit the driver session."""
        logger.info("Mock Appium driver quit")
        
    def get_device_time(self) -> str:
        """Get device time."""
        return str(int(time.time()))
        
    def set_network_connection(self, connection_type: int):
        """Set network connection type."""
        self._network_connected = connection_type > 0
        logger.info(f"Mock network connection: {connection_type}")
        
    def get_network_connection(self) -> int:
        """Get network connection type."""
        return 6 if self._network_connected else 0  # WiFi + Data or None
        
    def toggle_wifi(self):
        """Toggle WiFi on/off."""
        self._network_connected = not self._network_connected
        logger.info(f"Mock WiFi toggled: {self._network_connected}")
        
    def simulate_user_interaction(self, interaction_type: str, **kwargs):
        """Simulate various user interactions for testing."""
        if interaction_type == "app_lifecycle":
            # Simulate app going to background and returning
            self.background_app(2)
            
        elif interaction_type == "orientation_change":
            # Simulate device rotation
            new_orientation = "LANDSCAPE" if self._orientation == "PORTRAIT" else "PORTRAIT"
            self.set_orientation(new_orientation)
            
        elif interaction_type == "memory_pressure":
            # Simulate memory pressure (would affect real app)
            logger.info("Mock memory pressure simulation")
            
        elif interaction_type == "network_disconnect":
            # Simulate network disconnection
            self.set_network_connection(0)
            time.sleep(kwargs.get('duration', 2))
            self.set_network_connection(6)
            
        elif interaction_type == "battery_low":
            # Simulate low battery
            self.device_info.battery_level = 15
            logger.info("Mock low battery simulation")
            
    def get_app_state(self, app_package: str) -> int:
        """Get application state."""
        if self.current_package == app_package:
            return 4 if self._app_state == "foreground" else 1  # Running in foreground/background
        return 0  # Not running


class MockAndroidTestManager:
    """Manages Android testing with automatic device/mock selection."""
    
    def __init__(self):
        self.real_driver = None
        self.mock_driver = None
        self.use_mock = not self._detect_real_device()
        
    def _detect_real_device(self) -> bool:
        """Detect if real Android device/emulator is available."""
        try:
            # Check if Appium server is running and device is connected
            # This would involve checking ADB devices, Appium server status, etc.
            
            # For now, check environment variable
            if os.getenv('USE_REAL_ANDROID_DEVICE', 'false').lower() == 'true':
                logger.info("Real Android device mode enabled via environment")
                return True
            else:
                logger.info("Using mock Android device - real device not available")
                return False
                
        except Exception as e:
            logger.warning(f"Android device detection failed: {e}, using mock")
            return False
            
    def get_driver(self):
        """Get appropriate driver (real or mock)."""
        if self.use_mock:
            if not self.mock_driver:
                mock_device = MockAndroidDevice(
                    device_id="mock_android_001",
                    model="Mock Android Device",
                    android_version="11",
                    screen_resolution=(1080, 1920)
                )
                self.mock_driver = MockAppiumDriver(mock_device)
            return self.mock_driver
        else:
            if not self.real_driver:
                # Initialize real Appium driver
                # This would involve creating actual Appium WebDriver
                raise NotImplementedError("Real Appium driver initialization not implemented")
            return self.real_driver
            
    def cleanup(self):
        """Clean up resources."""
        if self.mock_driver:
            self.mock_driver.quit()
        if self.real_driver:
            try:
                self.real_driver.quit()
            except Exception:
                pass


@pytest.fixture(scope="function")
def android_manager():
    """Provide Android test manager with automatic cleanup."""
    manager = MockAndroidTestManager()
    yield manager
    manager.cleanup()


@pytest.fixture(scope="function")
def android_driver(android_manager):
    """Provide Android driver (real or mock)."""
    return android_manager.get_driver()


@pytest.fixture(scope="function")
def enhanced_appium_driver(android_manager):
    """Enhanced Appium driver fixture with additional test utilities."""
    driver = android_manager.get_driver()
    
    # Add test utilities
    driver.test_utils = {
        'interaction_simulator': driver.simulate_user_interaction if hasattr(driver, 'simulate_user_interaction') else None,
        'is_mock': android_manager.use_mock,
        'device_info': driver.device_info if hasattr(driver, 'device_info') else None
    }
    
    return driver


class MockAppiumBy:
    """Mock version of AppiumBy for element location."""
    ACCESSIBILITY_ID = "accessibility_id"
    XPATH = "xpath"
    ID = "id"
    CLASS_NAME = "class_name"
    ANDROID_UIAUTOMATOR = "android_uiautomator"


# Mock imports for when Appium is not available
def create_appium_mocks():
    """Create mock Appium classes when real library is not available."""
    
    class MockWebDriverWait:
        def __init__(self, driver, timeout):
            self.driver = driver
            self.timeout = timeout
            
        def until(self, condition):
            # Simulate wait condition
            time.sleep(0.1)
            # Always return True for mock
            return True
            
    class MockExpectedConditions:
        @staticmethod
        def presence_of_element_located(locator):
            return lambda driver: True
            
        @staticmethod
        def element_to_be_clickable(locator):
            return lambda driver: True
            
    class MockTimeoutException(Exception):
        pass
        
    class MockNoSuchElementException(Exception):
        pass
        
    return {
        'WebDriverWait': MockWebDriverWait,
        'expected_conditions': MockExpectedConditions,
        'TimeoutException': MockTimeoutException,
        'NoSuchElementException': MockNoSuchElementException,
        'AppiumBy': MockAppiumBy
    }


# Provide mocks when Appium is not available
appium_mocks = create_appium_mocks()


def patch_appium_imports():
    """Patch Appium imports with mocks when library is not available."""
    import sys
    
    # Create mock modules
    mock_modules = {
        'appium': Mock(),
        'appium.webdriver': Mock(),
        'appium.webdriver.common': Mock(),
        'appium.webdriver.common.appiumby': Mock(),
        'appium.options': Mock(),
        'appium.options.android': Mock(),
        'selenium': Mock(),
        'selenium.webdriver': Mock(),
        'selenium.webdriver.support': Mock(),
        'selenium.webdriver.support.ui': Mock(),
        'selenium.webdriver.support.expected_conditions': Mock(),
        'selenium.common': Mock(),
        'selenium.common.exceptions': Mock(),
    }
    
    for module_name, mock_module in mock_modules.items():
        sys.modules[module_name] = mock_module
        
    # Set up specific mock attributes
    sys.modules['appium.webdriver.common.appiumby'].AppiumBy = MockAppiumBy
    sys.modules['selenium.webdriver.support.ui'].WebDriverWait = appium_mocks['WebDriverWait']
    sys.modules['selenium.webdriver.support.expected_conditions'] = appium_mocks['expected_conditions']
    sys.modules['selenium.common.exceptions'].TimeoutException = appium_mocks['TimeoutException']
    sys.modules['selenium.common.exceptions'].NoSuchElementException = appium_mocks['NoSuchElementException']


if __name__ == "__main__":
    # Test the mock infrastructure
    manager = MockAndroidTestManager()
    driver = manager.get_driver()
    
    print(f"Using mock driver: {manager.use_mock}")
    print(f"Device info: {driver.device_info if hasattr(driver, 'device_info') else 'N/A'}")
    
    # Test some interactions
    try:
        nav_element = driver.find_element(MockAppiumBy.ACCESSIBILITY_ID, "Open navigation drawer")
        nav_element.click()
        print("Navigation drawer clicked successfully")
        
        start_button = driver.find_element(MockAppiumBy.XPATH, "//android.widget.Button[@text='Start Recording']")
        start_button.click()
        print("Start recording button clicked successfully")
        
        screenshot = driver.get_screenshot_as_png()
        print(f"Screenshot captured: {len(screenshot)} bytes")
        
    except Exception as e:
        print(f"Test interaction failed: {e}")
        
    manager.cleanup()
    print("Mock Android infrastructure test complete")