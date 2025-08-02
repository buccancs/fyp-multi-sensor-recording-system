# IDE Integration Test Report

**Generated:** 2025-08-02T06:17:16.815289
**Duration:** 37.76 seconds
**Overall Result:** ✅ PASSED

## Test Summary

- **Total Tests:** 66
- **Passed:** 66
- **Failed:** 0
- **Success Rate:** 100.0%

## Python Desktop Application

**Overall Success:** ✅

### Tab Navigation

- ✅ Recording
- ✅ Devices
- ✅ Calibration
- ✅ Files

### Button Interactions

#### Recording Tab

- ✅ start_recording (500.6ms)
- ✅ stop_recording (500.7ms)
- ✅ preview (500.6ms)

#### Devices Tab

- ✅ connect_pc (500.7ms)
- ✅ connect_android (500.6ms)
- ✅ connect_shimmer (500.6ms)
- ✅ scan_devices (500.7ms)

#### Calibration Tab

- ✅ start_calibration (500.7ms)
- ✅ load_calibration (500.6ms)
- ✅ save_calibration (500.7ms)

#### Files Tab

- ✅ export_data (500.7ms)
- ✅ open_folder (500.6ms)
- ✅ delete_session (500.6ms)

## Android Application

**Overall Success:** ✅

### Navigation Tests

- ✅ nav_recording via drawer_menu (500.6ms)
- ✅ nav_devices via drawer_menu (500.6ms)
- ✅ nav_calibration via drawer_menu (500.7ms)
- ✅ nav_files via drawer_menu (500.7ms)
- ✅ nav_settings via drawer_menu_activity (500.7ms)
- ✅ nav_network via drawer_menu_activity (500.6ms)
- ✅ nav_shimmer via drawer_menu_activity (500.6ms)
- ✅ bottom_nav_recording via bottom_navigation (300.4ms)
- ✅ bottom_nav_monitor via bottom_navigation (300.5ms)
- ✅ bottom_nav_calibrate via bottom_navigation (300.5ms)

### Button Tests

#### nav_recording

- ✅ start_recording (200.4ms)
- ✅ stop_recording (200.4ms)
- ✅ preview_toggle (200.4ms)

#### nav_devices

- ✅ connect_devices (200.4ms)
- ✅ scan_devices (200.4ms)
- ✅ device_settings (200.4ms)

#### nav_calibration

- ✅ start_calibration (200.4ms)
- ✅ calibration_settings (200.3ms)
- ✅ view_results (200.3ms)

#### nav_files

- ✅ browse_files (200.3ms)
- ✅ export_data (200.3ms)
- ✅ delete_session (200.3ms)

#### nav_settings

- ✅ save_settings (200.3ms)
- ✅ reset_settings (200.3ms)
- ✅ back (200.3ms)

#### nav_network

- ✅ configure_network (200.4ms)
- ✅ test_connection (200.3ms)
- ✅ back (200.4ms)

#### nav_shimmer

- ✅ configure_shimmer (200.3ms)
- ✅ test_sensors (200.3ms)
- ✅ back (200.3ms)

#### bottom_nav_recording

- ✅ quick_record (200.3ms)

#### bottom_nav_monitor

- ✅ monitor_devices (200.3ms)

#### bottom_nav_calibrate

- ✅ quick_calibrate (200.4ms)

### Navigation Flow Validation

#### From nav_recording

- ✅ → nav_devices (400.6ms)
- ✅ → nav_calibration (400.6ms)
- ✅ → nav_files (400.5ms)

#### From nav_devices

- ✅ → nav_recording (400.6ms)
- ✅ → nav_calibration (400.5ms)
- ✅ → nav_files (400.6ms)

#### From nav_calibration

- ✅ → nav_recording (400.6ms)
- ✅ → nav_devices (400.5ms)
- ✅ → nav_files (400.6ms)

#### From nav_files

- ✅ → nav_recording (400.5ms)
- ✅ → nav_devices (400.6ms)
- ✅ → nav_calibration (400.6ms)

#### From nav_settings

- ✅ → main_activity (400.5ms)

#### From nav_network

- ✅ → main_activity (400.5ms)

#### From nav_shimmer

- ✅ → main_activity (400.5ms)

#### From bottom_nav_recording


#### From bottom_nav_monitor


#### From bottom_nav_calibrate


