# Android Application Screenshots

This directory contains automated screenshot generation tools for the Multi-Sensor Recording Android application.

## Quick Start

### Option 1: Use the automated script (Recommended)
```bash
# Generate all screenshots automatically
./tools/generate_hd_screenshots.sh

# Generate basic screenshots quickly
./tools/generate_hd_screenshots.sh --quick
```

### Option 2: Use Gradle tasks
```bash
# Simple screenshots (most reliable)
./gradlew generateSimpleScreenshots

# Full HD screenshots (comprehensive)
./gradlew generateHDScreenshots

# Quick screenshots for CI/CD
./gradlew generateQuickScreenshots
```

### Option 3: Manual test execution
```bash
# Build the test APK
./gradlew :AndroidApp:assembleDevDebug :AndroidApp:assembleDevDebugAndroidTest

# Install on device
./gradlew :AndroidApp:installDevDebug :AndroidApp:installDevDebugAndroidTest

# Run screenshot test
adb shell am instrument -w \
  -e class com.multisensor.recording.SimpleScreenshotTest \
  com.multisensor.recording.dev.test/androidx.test.runner.AndroidJUnitRunner

# Pull screenshots from device
adb pull /sdcard/Android/data/com.multisensor.recording.dev/files/Pictures/screenshots ./screenshots
```

## Requirements

- Android device or emulator connected via ADB
- Device unlocked with screen on
- USB debugging enabled
- Sufficient storage space on device

## Output

Screenshots are saved to:
- **Device**: `/sdcard/Android/data/com.multisensor.recording.dev/files/Pictures/screenshots/`
- **Local**: `./screenshots/` (after pulling from device)

## Files Included

### Test Classes
- `ScreenshotAutomationTest.kt` - Comprehensive screenshot automation with full app navigation
- `SimpleScreenshotTest.kt` - Basic screenshot capture for reliable operation

### Automation Tools
- `generate_hd_screenshots.sh` - Complete automation script with device management
- Gradle tasks in `build.gradle.kts` for build system integration

### Documentation
- `ANDROID_SCREENSHOT_AUTOMATION.md` - Comprehensive documentation
- This README for quick reference

## Troubleshooting

### Common Issues

1. **"No devices connected"**
   ```bash
   adb devices  # Check device connectivity
   ```

2. **"App not installed"**
   ```bash
   ./gradlew :AndroidApp:installDevDebug
   ```

3. **"Test execution failed"**
   - Ensure device is unlocked
   - Check app permissions are granted
   - Try the simple screenshot test first

4. **"Build failed"**
   ```bash
   ./gradlew clean
   ./gradlew :AndroidApp:assembleDevDebug
   ```

### Getting Help

For detailed documentation, see `docs/ANDROID_SCREENSHOT_AUTOMATION.md`

For build issues, check the main project README.md

## Example Output

After running the screenshot automation, you'll get organized screenshots like:

```
screenshots/
└── simple_screenshots_20250116_143022/
    ├── 01_main_screen_initial.png
    ├── 02_main_screen_with_toolbar.png
    ├── 03_main_screen_with_drawer.png
    ├── 04_main_screen_with_bottom_nav.png
    └── 05_main_screen_final.png
```

These high-definition screenshots capture the Android application UI for documentation, marketing, and development purposes.