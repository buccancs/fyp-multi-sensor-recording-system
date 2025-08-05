# Manual Testing Guide - FileViewActivity Toast Functions

## Overview

This guide provides instructions for manually testing the newly implemented `showMessage` and `showError` functions in
FileViewActivity.kt on a Samsung device.

## Prerequisites

- Samsung Android device (API level 21+)
- Android Studio or ADB for app installation
- bucika_gsr APK built from current codebase

## Test Scenarios

### 1. Test showMessage Function

**Location**: FileViewActivity.kt line 100
**Trigger**: Menu → Export All
**Expected Result**: Short toast message "Export functionality coming soon"

**Steps**:

1. Open the bucika_gsr app on Samsung device
2. Navigate to File View screen
3. Tap the menu button (three dots)
4. Select "Export All" option
5. **Verify**: Toast message appears briefly (2-3 seconds) with text "Export functionality coming soon"

### 2. Test showError Function - File Open Error

**Location**: FileViewActivity.kt line 257
**Trigger**: Attempt to open a corrupted or inaccessible file
**Expected Result**: Long toast message with error details

**Steps**:

1. Navigate to File View screen
2. Select a session with files
3. Tap on a file to open context menu
4. Select "Open" option
5. If file opening fails, **Verify**: Toast message appears for longer duration (4-5 seconds) with error text

### 3. Test showError Function - File Share Error

**Location**: FileViewActivity.kt line 271
**Trigger**: Attempt to share a file when sharing fails
**Expected Result**: Long toast message with share error details

**Steps**:

1. Navigate to File View screen
2. Select a session with files
3. Tap on a file to open context menu
4. Select "Share" option
5. If sharing fails, **Verify**: Toast message appears for longer duration (4-5 seconds) with error text

### 4. Test showError Function - General Error Handling

**Location**: FileViewActivity.kt line 203
**Trigger**: Any error state in the UI
**Expected Result**: Long toast message with error details

**Steps**:

1. Navigate to File View screen
2. Trigger any error condition (network issues, file system errors, etc.)
3. **Verify**: Toast message appears for longer duration with appropriate error message

## Verification Checklist

- [ ] showMessage displays with Toast.LENGTH_SHORT duration (2-3 seconds)
- [ ] showError displays with Toast.LENGTH_LONG duration (4-5 seconds)
- [ ] Toast messages appear at the bottom of the screen (default Android behavior)
- [ ] Messages are readable and informative
- [ ] No app crashes when Toast functions are called
- [ ] Toast messages don't interfere with other UI elements
- [ ] Messages display correctly in both portrait and landscape orientations

## Samsung-Specific Considerations

- **One UI Interface**: Verify Toast messages display correctly with Samsung's One UI theme
- **Edge Display**: On Samsung Edge devices, ensure Toast messages are fully visible
- **Dark Mode**: Test Toast visibility in both light and dark themes
- **Accessibility**: Verify Toast messages work with Samsung's accessibility features (TalkBack, etc.)

## Troubleshooting

### If Toast Messages Don't Appear:

1. Check if "Show notifications" is enabled in app settings
2. Verify the app has proper permissions
3. Check if Samsung's "Do Not Disturb" mode is affecting notifications
4. Restart the app and try again

### If App Crashes:

1. Check logcat for error messages
2. Verify the Toast import is present: `import android.widget.Toast`
3. Ensure the functions are called from the main UI thread

## Expected Results Summary

| Function    | Duration     | Use Case             | Expected Message                        |
|-------------|--------------|----------------------|-----------------------------------------|
| showMessage | SHORT (2-3s) | Export functionality | "Export functionality coming soon"      |
| showError   | LONG (4-5s)  | File open error      | "Failed to open file: [error details]"  |
| showError   | LONG (4-5s)  | File share error     | "Failed to share file: [error details]" |
| showError   | LONG (4-5s)  | General errors       | Various error messages                  |

## Completion Criteria

✅ All Toast messages display correctly on Samsung device
✅ Appropriate durations are observed (SHORT vs LONG)
✅ No crashes or UI issues
✅ Messages are user-friendly and informative
✅ Consistent behavior across different Samsung device models and Android versions

## Notes

- This testing should be performed after each build to ensure Toast functionality remains intact
- Test on multiple Samsung device models if available (Galaxy S series, Note series, etc.)
- Document any device-specific issues or variations in behavior
- Consider testing with different Android API levels supported by the app