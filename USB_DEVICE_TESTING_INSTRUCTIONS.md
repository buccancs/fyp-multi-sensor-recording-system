# USB Device Detection Testing Instructions

## Overview
The app has been updated to properly detect and respond to Topdon thermal camera connections. This document provides testing instructions to verify the USB device detection and auto-launch functionality.

## Implementation Summary

### Changes Made
1. **Fixed Device Filter**: Updated `device_filter.xml` with correct vendor ID (0x0BDA) matching IRCamera library
2. **Enhanced MainActivity**: Added comprehensive USB device handling with logging and user notifications
3. **Auto-Launch Configuration**: App will automatically launch when supported Topdon devices are connected

### Supported Devices
- **Vendor ID**: 0x0BDA (Topdon)
- **Product IDs**: 
  - 0x3901 (TC001 series)
  - 0x5840 (TC001 Plus)
  - 0x5830 (TC001 variant)
  - 0x5838 (TC001 variant)

## Testing Instructions

### Prerequisites
- Samsung SM-S901E device with app installed
- Topdon thermal camera (TC001, TC001 Plus, or compatible model)
- USB-C OTG adapter/cable
- ADB access for log monitoring (optional but recommended)

### Test Scenarios

#### Test 1: Auto-Launch on Device Connection
1. **Setup**: Ensure app is not currently running
2. **Action**: Connect Topdon thermal camera via USB-C OTG
3. **Expected Results**:
   - App should launch automatically
   - MainActivity should open
   - Toast notification: "Topdon Thermal Camera Connected!"
   - Status text: "Topdon thermal camera connected - Ready for recording"

#### Test 2: Device Recognition Logging
1. **Setup**: Enable ADB logging or use device logs
2. **Action**: Connect Topdon device
3. **Expected Log Entries**:
   ```
   [DEBUG_LOG] onNewIntent() called
   [DEBUG_LOG] Handling USB device intent: android.hardware.usb.action.USB_DEVICE_ATTACHED
   [DEBUG_LOG] USB device attached:
   [DEBUG_LOG] - Device name: [device_name]
   [DEBUG_LOG] - Vendor ID: 0x0BDA
   [DEBUG_LOG] - Product ID: 0x[product_id]
   [DEBUG_LOG] - Device class: [class]
   [DEBUG_LOG] Device support check:
   [DEBUG_LOG] - Expected VID: 0x0BDA
   [DEBUG_LOG] - Actual VID: 0x0BDA
   [DEBUG_LOG] - Expected PIDs: 0x3901, 0x5840, 0x5830, 0x5838
   [DEBUG_LOG] - Actual PID: 0x[product_id]
   [DEBUG_LOG] - Is supported: true
   [DEBUG_LOG] ✓ Supported Topdon thermal camera detected!
   ```

#### Test 3: Permission Integration
1. **Setup**: Connect Topdon device with app having all permissions
2. **Expected**: 
   - Device detected
   - Recording system initializes automatically
   - Log: "Permissions available, initializing thermal recorder"

#### Test 4: Permission Handling
1. **Setup**: Connect Topdon device with missing permissions
2. **Expected**:
   - Device detected
   - Status: "Thermal camera detected - Please grant permissions to continue"
   - Log: "Permissions not available, requesting permissions first"

#### Test 5: Unsupported Device Handling
1. **Setup**: Connect non-Topdon USB device
2. **Expected**:
   - No auto-launch (if device not in filter)
   - If launched manually, log: "USB device is not a supported Topdon thermal camera"

### Verification Checklist

- [ ] App launches automatically when Topdon device connected
- [ ] Correct device detection and vendor/product ID validation
- [ ] User notifications appear (Toast messages)
- [ ] Status text updates appropriately
- [ ] Comprehensive logging for debugging
- [ ] Permission integration works correctly
- [ ] Unsupported devices handled gracefully

### Troubleshooting

#### App Doesn't Launch Automatically
1. Check device filter configuration in `device_filter.xml`
2. Verify vendor ID (should be 0x0BDA)
3. Confirm product ID is supported (0x3901, 0x5840, 0x5830, 0x5838)
4. Check Android manifest USB intent filter configuration

#### Device Not Recognized
1. Enable ADB logging to see actual vendor/product IDs
2. Compare with supported device list
3. Check if device requires specific drivers or setup

#### Permissions Issues
1. Verify all dangerous permissions are granted
2. Check permission callback handling
3. Ensure recording system initialization occurs after permissions

## Log Monitoring Commands

```bash
# Monitor app logs
adb logcat | findstr "MainActivity"

# Monitor USB events
adb logcat | findstr "USB"

# Monitor all app logs
adb logcat | findstr "com.multisensor.recording"
```

## Next Steps

After successful testing:
1. Document any issues or unexpected behavior
2. Update device filter if additional product IDs are discovered
3. Consider adding more detailed user guidance for USB connection
4. Test with different Topdon camera models if available

## Implementation Files Modified

- `AndroidApp/src/main/res/xml/device_filter.xml` - USB device filter configuration
- `AndroidApp/src/main/java/com/multisensor/recording/MainActivity.kt` - USB device handling
- `AndroidApp/src/main/AndroidManifest.xml` - USB intent filter (already configured)

## Date
2025-07-28 21:21