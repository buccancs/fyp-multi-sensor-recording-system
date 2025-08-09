# Code Complexity and Documentation Analysis

**Generated:** 2025-08-06T06:55:47.275674

## Summary

- **Total Functions Analysed:** 1499
- **Need Documentation:** 493
- **High Complexity (>15):** 67
- **Medium Complexity (10-15):** 39
- **Average Complexity:** 4.6

## Recommendations

### HIGH: Complexity Reduction
**Issue:** 67 functions have very high complexity (>15)

**Action:** Refactor these functions into smaller, focused functions

### MEDIUM: Documentation
**Issue:** 106 complex functions lack documentation

**Action:** Add complete docstrings explaining logic and parameters

## Top Complex Functions Needing Attention

### `ShimmerManager` in `PythonApp/shimmer_manager.py`
- **Complexity:** 152
- **Line:** 130
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 152 control structures

### `_setup_routes` in `PythonApp/web_ui/web_dashboard.py`
- **Complexity:** 143
- **Line:** 96
- **Type:** method
- **Needs Docs:** Yes
- **Reasons:** Very high cyclomatic complexity (143), Contains complex logic patterns (nested loops, exception handling, or async operations), Multiple return paths (143), Missing documentation

### `WebDashboardServer` in `PythonApp/web_ui/web_dashboard.py`
- **Complexity:** 73
- **Line:** 40
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 73 control structures

### `SecurityScanner` in `PythonApp/production/security_scanner.py`
- **Complexity:** 68
- **Line:** 44
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 68 control structures

### `EnhancedDeviceServer` in `PythonApp/network/enhanced_device_server.py`
- **Complexity:** 60
- **Line:** 213
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 60 control structures

### `DualWebcamCapture` in `PythonApp/webcam/dual_webcam_capture.py`
- **Complexity:** 55
- **Line:** 51
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 55 control structures

### `JsonSocketServer` in `PythonApp/network/device_server.py`
- **Complexity:** 55
- **Line:** 93
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 55 control structures

### `SessionRecoveryManager` in `PythonApp/session/session_recovery.py`
- **Complexity:** 53
- **Line:** 12
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 53 control structures

### `EnhancedStimulusController` in `PythonApp/gui/enhanced_stimulus_controller.py`
- **Complexity:** 52
- **Line:** 278
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 52 control structures

### `WebController` in `PythonApp/web_ui/web_controller.py`
- **Complexity:** 50
- **Line:** 73
- **Type:** class
- **Needs Docs:** Yes
- **Reasons:** Complex class with 50 control structures
